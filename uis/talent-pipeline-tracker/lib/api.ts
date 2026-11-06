import { ApiError } from "@/lib/errors";
import type { Candidate, CandidatePatch, CandidateWrite, RecordList } from "@/types/candidate";
import type { Note, NoteList } from "@/types/note";

type FetchLike = (input: string, init?: RequestInit) => Promise<Response>;

export interface TrackerApi {
  listRecords(params?: { page?: number; limit?: number }, signal?: AbortSignal): Promise<RecordList>;
  listAllRecords(signal?: AbortSignal): Promise<RecordList>;
  getRecord(id: string, signal?: AbortSignal): Promise<Candidate>;
  createRecord(body: CandidateWrite, signal?: AbortSignal): Promise<Candidate>;
  replaceRecord(id: string, body: CandidateWrite, signal?: AbortSignal): Promise<Candidate>;
  patchRecord(id: string, body: CandidatePatch, signal?: AbortSignal): Promise<Candidate>;
  listNotes(id: string, signal?: AbortSignal): Promise<NoteList>;
  addNote(id: string, content: string, signal?: AbortSignal): Promise<Note>;
  deleteNote(id: string, noteId: string, signal?: AbortSignal): Promise<void>;
}

export function createApi(baseUrl: string, fetchImpl: FetchLike = fetch): TrackerApi {
  const root = baseUrl.replace(/\/$/, "");

  async function request(path: string, init: RequestInit | undefined, expected: number[]): Promise<Response> {
    const response = await fetchImpl(`${root}${path}`, {
      ...init,
      headers: {
        accept: "application/json",
        ...(init?.body ? { "content-type": "application/json" } : {}),
        ...init?.headers,
      },
    });
    if (!expected.includes(response.status)) {
      throw new ApiError(response.status, await readError(response));
    }
    return response;
  }

  return {
    async listRecords(params = {}, signal) {
      const query = new URLSearchParams({
        page: String(params.page ?? 1),
        limit: String(params.limit ?? 100),
      });
      const response = await request(`/records?${query.toString()}`, { method: "GET", signal }, [200]);
      return parseRecordList(await response.json());
    },
    async listAllRecords(signal) {
      const first = await this.listRecords({ page: 1, limit: 100 }, signal);
      const data = [...first.data];
      let page = 1;
      while (data.length < first.total && page < 20) {
        page += 1;
        const next = await this.listRecords({ page, limit: 100 }, signal);
        if (next.data.length === 0) break;
        data.push(...next.data);
      }
      return { total: first.total, page: 1, limit: data.length, data };
    },
    async getRecord(id, signal) {
      const response = await request(`/records/${encodeURIComponent(id)}`, { method: "GET", signal }, [200]);
      return parseCandidate(await response.json());
    },
    async createRecord(body, signal) {
      const response = await request(
        "/records",
        { method: "POST", body: JSON.stringify(body), signal },
        [201],
      );
      return parseCandidate(await response.json());
    },
    async replaceRecord(id, body, signal) {
      const response = await request(
        `/records/${encodeURIComponent(id)}`,
        { method: "PUT", body: JSON.stringify(body), signal },
        [200],
      );
      return parseCandidate(await response.json());
    },
    async patchRecord(id, body, signal) {
      const response = await request(
        `/records/${encodeURIComponent(id)}`,
        { method: "PATCH", body: JSON.stringify(body), signal },
        [200],
      );
      return parseCandidate(await response.json());
    },
    async listNotes(id, signal) {
      const response = await request(`/records/${encodeURIComponent(id)}/notes`, { method: "GET", signal }, [200]);
      return parseNoteList(await response.json());
    },
    async addNote(id, content, signal) {
      const response = await request(
        `/records/${encodeURIComponent(id)}/notes`,
        { method: "POST", body: JSON.stringify({ content }), signal },
        [201],
      );
      return parseNote(await response.json());
    },
    async deleteNote(id, noteId, signal) {
      await request(
        `/records/${encodeURIComponent(id)}/notes/${encodeURIComponent(noteId)}`,
        { method: "DELETE", signal },
        [204],
      );
    },
  };
}

export function parseRecordList(value: unknown): RecordList {
  const record = asRecord(value, "listado");
  const data = record.data;
  if (!Array.isArray(data)) throw new Error("El listado no incluye data.");
  return {
    total: asNumber(record.total, "total"),
    page: asNumber(record.page, "page"),
    limit: asNumber(record.limit, "limit"),
    data: data.map((item) => parseCandidate(item)),
  };
}

export function parseCandidate(value: unknown): Candidate {
  const record = asRecord(value, "candidatura");
  return {
    id: asString(record.id, "id"),
    full_name: asString(record.full_name, "full_name"),
    email: asString(record.email, "email"),
    phone: asString(record.phone, "phone"),
    position: asString(record.position, "position"),
    linkedin_url: asNullableString(record.linkedin_url, "linkedin_url"),
    cv_url: asNullableString(record.cv_url, "cv_url"),
    status: asString(record.status, "status"),
    stage: asString(record.stage, "stage"),
    experience_years: asNumber(record.experience_years, "experience_years"),
    notes_count: asNumber(record.notes_count, "notes_count"),
    applied_at: asString(record.applied_at, "applied_at"),
    updated_at: asString(record.updated_at, "updated_at"),
  };
}

export function parseNoteList(value: unknown): NoteList {
  const record = asRecord(value, "notas");
  if (!Array.isArray(record.data)) throw new Error("El listado de notas no incluye data.");
  const meta = asRecord(record.meta, "meta");
  return {
    data: record.data.map((item) => parseNote(item)),
    meta: { total: asNumber(meta.total, "meta.total") },
  };
}

export function parseNote(value: unknown): Note {
  const record = asRecord(value, "nota");
  return {
    id: asString(record.id, "id"),
    record_id: asString(record.record_id, "record_id"),
    content: asString(record.content, "content"),
    created_at: asString(record.created_at, "created_at"),
  };
}

async function readError(response: Response): Promise<string> {
  const text = await response.text();
  if (!text) return response.statusText || "Error sin detalle";
  try {
    const body = JSON.parse(text) as { error?: unknown; detail?: unknown };
    if (typeof body.error === "string" && body.error.trim()) return body.error;
    if (Array.isArray(body.detail)) {
      const messages = body.detail
        .map((item) => {
          if (!item || typeof item !== "object") return "";
          const detail = item as { loc?: unknown; msg?: unknown };
          const loc = Array.isArray(detail.loc) ? detail.loc.filter((part) => part !== "body").join(".") : "";
          const msg = typeof detail.msg === "string" ? detail.msg : "";
          return [loc, msg].filter(Boolean).join(": ");
        })
        .filter(Boolean);
      if (messages.length > 0) return messages.join(" ");
    }
  } catch {
    return text;
  }
  return text;
}

function asRecord(value: unknown, label: string): Record<string, unknown> {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error(`La respuesta de ${label} no es un objeto.`);
  }
  return value as Record<string, unknown>;
}

function asString(value: unknown, label: string): string {
  if (typeof value !== "string" || value.length === 0) {
    throw new Error(`Campo ausente o inválido: ${label}`);
  }
  return value;
}

function asNullableString(value: unknown, label: string): string | null {
  if (value === null) return null;
  if (typeof value === "string") return value;
  throw new Error(`Campo ausente o inválido: ${label}`);
}

function asNumber(value: unknown, label: string): number {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    throw new Error(`Campo ausente o inválido: ${label}`);
  }
  return value;
}
