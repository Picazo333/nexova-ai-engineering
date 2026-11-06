import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { createApi, parseCandidate, parseNote, parseNoteList, parseRecordList } from "../lib/api";
import { ApiError } from "../lib/errors";
import { filterCandidates, foldText } from "../lib/filters";
import { formatExperience } from "../lib/format";
import { createRequestGuard } from "../lib/guard";
import { labelStage, labelStatus } from "../lib/labels";
import { emptyCandidateForm, toCandidateWrite, validateCandidateForm, validateNoteContent } from "../lib/validation";
import type { Candidate } from "../types/candidate";

const candidate = {
  id: "53f2bbdc-4ea0-4b34-b076-4f8e7c2736ac",
  full_name: "Víctor Alonso",
  email: "victor.alonso@gmail.com",
  phone: "+34 600000000",
  position: "Consultor de selección",
  linkedin_url: "https://linkedin.com/in/victor-alonso",
  cv_url: null,
  status: "in_progress",
  stage: "review",
  experience_years: 6,
  notes_count: 1,
  applied_at: "2026-03-06T20:04:32.114Z",
  updated_at: "2026-03-27T20:04:32.114Z",
} satisfies Candidate;

describe("filtros", () => {
  const records = [
    candidate,
    { ...candidate, id: "b", full_name: "Ana Ruiz", email: "ana.ruiz@gmail.com", status: "received", stage: "pending" },
  ];

  it("filtra por estado, etapa y texto sin distinguir acentos", () => {
    assert.equal(filterCandidates(records, { status: "in_progress", stage: "", q: "" }).length, 1);
    assert.equal(filterCandidates(records, { status: "", stage: "pending", q: "" })[0]?.full_name, "Ana Ruiz");
    assert.equal(filterCandidates(records, { status: "", stage: "", q: "VICTOR" })[0]?.id, candidate.id);
    assert.equal(filterCandidates(records, { status: "received", stage: "review", q: "" }).length, 0);
  });

  it("normaliza diacríticos", () => {
    assert.equal(foldText("Víctor"), "victor");
  });
});

describe("validación", () => {
  it("bloquea el alta si faltan campos obligatorios", () => {
    const errors = validateCandidateForm(emptyCandidateForm());
    assert.ok(errors.full_name);
    assert.ok(errors.email);
    assert.ok(errors.phone);
    assert.ok(errors.position);
    assert.ok(errors.experience_years);
    assert.equal(validateNoteContent("   "), "Escribe la nota antes de guardarla.");
  });

  it("acepta una candidatura completa y deja los enlaces vacíos en null", () => {
    const errors = validateCandidateForm({
      ...emptyCandidateForm(),
      full_name: "Laura Méndez",
      email: "laura.mendez@example.com",
      phone: "+34 611111111",
      position: "Consultora de selección",
      experience_years: "4",
    });
    assert.deepEqual(errors, {});
    const body = toCandidateWrite({
      ...emptyCandidateForm(),
      full_name: " Laura Méndez ",
      email: "laura.mendez@example.com",
      phone: "+34 611111111",
      position: "Consultora de selección",
      experience_years: "4",
    });
    assert.equal(body.linkedin_url, null);
    assert.equal(body.cv_url, null);
    assert.equal(body.experience_years, 4);
  });
});

describe("contrato de parseo", () => {
  it("lee el listado, la ficha y las notas con la forma publicada", () => {
    const list = parseRecordList({ total: 1, page: 1, limit: 100, data: [candidate] });
    assert.equal(list.data[0]?.full_name, "Víctor Alonso");
    assert.equal(parseCandidate(candidate).cv_url, null);
    const note = parseNote({
      id: "n1",
      record_id: candidate.id,
      content: "Nota interna",
      created_at: "2026-03-25T20:04:32.114Z",
    });
    const notes = parseNoteList({ data: [note], meta: { total: 1 } });
    assert.equal(notes.meta.total, 1);
  });

  it("rechaza una ficha incompleta", () => {
    assert.throws(() => parseCandidate({ id: "x" }), /full_name/);
  });
});

describe("cliente HTTP", () => {
  it("usa async/await, pagina el listado y no aplica una respuesta obsoleta", async () => {
    const calls: string[] = [];
    const api = createApi("https://tracker.test/api/v1", async (input, init) => {
      calls.push(`${init?.method ?? "GET"} ${input}`);
      const url = String(input);
      if (url.includes("/records?")) {
        const page = new URL(url).searchParams.get("page");
        const body =
          page === "1"
            ? { total: 2, page: 1, limit: 100, data: [candidate] }
            : { total: 2, page: 2, limit: 100, data: [{ ...candidate, id: "second", full_name: "Segunda" }] };
        return jsonResponse(body);
      }
      if (init?.method === "POST" && url.endsWith("/notes")) return jsonResponse(parseNote({
        id: "n1",
        record_id: candidate.id,
        content: "Nota",
        created_at: "2026-11-06T00:00:00.000Z",
      }), 201);
      if (init?.method === "DELETE") return new Response(null, { status: 204 });
      if (init?.method === "PATCH") return jsonResponse({ ...candidate, status: "selected" });
      return jsonResponse({ error: "Record not found" }, 404);
    });

    const all = await api.listAllRecords();
    assert.equal(all.data.length, 2);
    assert.equal(calls[0]?.startsWith("GET "), true);
    const patched = await api.patchRecord(candidate.id, { status: "selected" });
    assert.equal(patched.status, "selected");
    await api.deleteNote(candidate.id, "n1");
    await assert.rejects(() => api.getRecord("missing"), (error: unknown) => {
      assert.ok(error instanceof ApiError);
      assert.equal(error.status, 404);
      return true;
    });
  });
});

describe("guardia de carrera", () => {
  it("ignora la petición anterior cuando llega otra", () => {
    const guard = createRequestGuard();
    const first = guard.next();
    const second = guard.next();
    assert.equal(guard.isCurrent(first), false);
    assert.equal(guard.isCurrent(second), true);
  });
});

describe("etiquetas", () => {
  it("traduce los valores del tracker y conserva uno desconocido", () => {
    assert.equal(labelStatus("received"), "Recibida");
    assert.equal(labelStage("technical_interview"), "Entrevista técnica");
    assert.equal(labelStatus("custom"), "custom");
    assert.equal(formatExperience(1), "1 año");
  });
});

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });
}
