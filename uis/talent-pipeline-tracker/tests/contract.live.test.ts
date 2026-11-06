import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { createApi } from "../lib/api";
import { getApiBaseUrl } from "../lib/env";

const api = createApi(getApiBaseUrl());

describe("contrato vivo del tracker", () => {
  it("lista, crea, actualiza, anota y borra una candidatura de prueba", async () => {
    const listed = await api.listRecords({ page: 1, limit: 1 });
    assert.ok(listed.total >= 1);
    assert.equal(listed.data.length, 1);
    const existing = listed.data[0];
    assert.ok(existing);
    const detail = await api.getRecord(existing.id);
    assert.equal(detail.id, existing.id);
    assert.equal(typeof detail.applied_at, "string");
    const notes = await api.listNotes(existing.id);
    assert.equal(typeof notes.meta.total, "number");

    const stamp = new Date().toISOString().replace(/[-:.TZ]/g, "");
    const created = await api.createRecord({
      full_name: "Prueba Contrato Nexova",
      email: `nexova.pipeline.${stamp}@example.com`,
      phone: "+34 600000099",
      position: "Consultor de selección",
      linkedin_url: null,
      cv_url: null,
      experience_years: 2,
    });
    try {
      assert.equal(created.status, "received");
      assert.equal(created.stage, "pending");
      const patched = await api.patchRecord(created.id, {
        status: "in_progress",
        stage: "personal_interview",
      });
      assert.equal(patched.status, "in_progress");
      assert.equal(patched.stage, "personal_interview");
      const replaced = await api.replaceRecord(created.id, {
        full_name: created.full_name,
        email: created.email,
        phone: "+34 600000098",
        position: created.position,
        linkedin_url: "https://linkedin.com/in/nexova-contrato",
        cv_url: null,
        experience_years: 3,
      });
      assert.equal(replaced.phone, "+34 600000098");
      assert.equal(replaced.status, "in_progress");
      const note = await api.addNote(created.id, "Nota de contrato automatizada.");
      const after = await api.listNotes(created.id);
      assert.ok(after.data.some((item) => item.id === note.id));
      await api.deleteNote(created.id, note.id);
      const remaining = await api.listNotes(created.id);
      assert.equal(remaining.data.some((item) => item.id === note.id), false);
    } finally {
      const response = await fetch(`${getApiBaseUrl()}/records/${created.id}`, { method: "DELETE" });
      assert.equal(response.status, 204);
    }
  });
});
