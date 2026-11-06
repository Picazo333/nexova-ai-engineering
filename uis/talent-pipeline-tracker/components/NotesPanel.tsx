"use client";

import { useEffect, useRef, useState } from "react";
import { ErrorStatus, LoadingStatus } from "@/components/AsyncStatus";
import { useTracker } from "@/hooks/useTracker";
import { toErrorMessage } from "@/lib/errors";
import { formatDate } from "@/lib/format";
import { createRequestGuard } from "@/lib/guard";
import { validateNoteContent } from "@/lib/validation";
import type { Note } from "@/types/note";

export function NotesPanel({ recordId }: { recordId: string }) {
  const api = useTracker();
  const [notes, setNotes] = useState<Note[]>([]);
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [error, setError] = useState<string | null>(null);
  const [content, setContent] = useState("");
  const [formError, setFormError] = useState<string | null>(null);
  const [formMessage, setFormMessage] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [confirmId, setConfirmId] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);
  const loadGuard = useRef(createRequestGuard());
  const cancelRef = useRef<HTMLButtonElement | null>(null);

  useEffect(() => {
    const guard = loadGuard.current;
    const controller = new AbortController();
    const requestId = guard.next();
    let active = true;
    void (async () => {
      try {
        const list = await api.listNotes(recordId, controller.signal);
        if (!active || !guard.isCurrent(requestId)) return;
        setNotes(list.data);
        setStatus("success");
      } catch (cause) {
        if (!active || !guard.isCurrent(requestId) || controller.signal.aborted) return;
        setError(toErrorMessage(cause));
        setStatus("error");
      }
    })();
    return () => {
      active = false;
      controller.abort();
    };
  }, [api, attempt, recordId]);

  useEffect(() => {
    if (confirmId) cancelRef.current?.focus();
  }, [confirmId]);

  function reload() {
    setStatus("loading");
    setError(null);
    setAttempt((value) => value + 1);
  }

  async function addNote() {
    const validation = validateNoteContent(content);
    if (validation) {
      setFormError(validation);
      setFormMessage(null);
      return;
    }
    setSaving(true);
    setFormError(null);
    setFormMessage(null);
    try {
      const note = await api.addNote(recordId, content.trim());
      setNotes((current) => [note, ...current]);
      setContent("");
      setFormMessage("Nota añadida.");
      setStatus("success");
    } catch (cause) {
      setFormError(toErrorMessage(cause));
    } finally {
      setSaving(false);
    }
  }

  async function removeNote(noteId: string) {
    setDeletingId(noteId);
    setFormError(null);
    try {
      await api.deleteNote(recordId, noteId);
      setNotes((current) => current.filter((note) => note.id !== noteId));
      setConfirmId(null);
      setFormMessage("Nota eliminada.");
    } catch (cause) {
      setFormError(toErrorMessage(cause));
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <section className="notes" aria-labelledby="notes-title">
      <h2 id="notes-title">Notas internas</h2>
      {status === "loading" && notes.length === 0 ? <LoadingStatus label="Cargando notas…" /> : null}
      {status === "error" ? (
        <ErrorStatus message={error ?? "No se pudieron cargar las notas."} onRetry={reload} />
      ) : null}
      {status === "success" && notes.length === 0 ? (
        <p className="empty-inline">Todavía no hay notas internas. La primera se añade aquí.</p>
      ) : null}
      {notes.length > 0 ? (
        <ul className="note-list">
          {notes.map((note) => (
            <li key={note.id} className="note">
              <p>{note.content}</p>
              <p className="note-meta">
                <time dateTime={note.created_at}>{formatDate(note.created_at)}</time>
              </p>
              {confirmId === note.id ? (
                <div
                  className="confirm"
                  role="group"
                  aria-label="Confirmar eliminación"
                  onKeyDown={(event) => {
                    if (event.key === "Escape") setConfirmId(null);
                  }}
                >
                  <button
                    className="button button-danger"
                    type="button"
                    disabled={deletingId === note.id}
                    onClick={() => void removeNote(note.id)}
                  >
                    {deletingId === note.id ? "Eliminando…" : "Eliminar"}
                  </button>
                  <button
                    ref={cancelRef}
                    className="button button-secondary"
                    type="button"
                    onClick={() => setConfirmId(null)}
                  >
                    Cancelar
                  </button>
                </div>
              ) : (
                <button className="button button-secondary" type="button" onClick={() => setConfirmId(note.id)}>
                  Eliminar nota
                </button>
              )}
            </li>
          ))}
        </ul>
      ) : null}
      <form
        className="note-form"
        onSubmit={(event) => {
          event.preventDefault();
          if (!saving) void addNote();
        }}
      >
        <label className="field" htmlFor="note-content">
          <span>Nueva nota</span>
          <textarea
            id="note-content"
            value={content}
            rows={4}
            disabled={saving || status === "loading"}
            aria-invalid={formError ? true : undefined}
            aria-describedby={formError ? "note-error" : undefined}
            onChange={(event) => setContent(event.target.value)}
          />
        </label>
        {formError ? (
          <p id="note-error" className="feedback feedback-error" role="alert">
            {formError}
          </p>
        ) : null}
        {formMessage ? (
          <p className="feedback feedback-success" role="status">
            {formMessage}
          </p>
        ) : null}
        <button className="button button-primary" type="submit" disabled={saving || status !== "success"}>
          {saving ? "Guardando nota…" : "Añadir nota"}
        </button>
      </form>
    </section>
  );
}
