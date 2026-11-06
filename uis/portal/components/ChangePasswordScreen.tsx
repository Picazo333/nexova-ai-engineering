"use client";

import { useRef, useState } from "react";

import { ErrorBanner, LoadingState } from "@/components/AsyncStatus";
import { useSession } from "@/components/SessionGate";
import { ApiError, apiFetch } from "@/lib/api";
import { passwordConfirmError } from "@/lib/forms";

export function ChangePasswordScreen() {
  const { phase } = useSession();
  if (phase.kind !== "in") return null;
  return <ChangeForm email={phase.me.email} />;
}

function ChangeForm({ email }: { email: string }) {
  const [current, setCurrent] = useState("");
  const [password, setPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [fields, setFields] = useState<Record<string, string>>({});
  const [formError, setFormError] = useState("");
  const [saved, setSaved] = useState("");
  const [pending, setPending] = useState(false);
  const request = useRef(0);
  const alertRef = useRef<HTMLDivElement>(null);
  const currentRef = useRef<HTMLInputElement>(null);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (pending) return;
    const problem = passwordConfirmError(password, confirmation);
    const local: Record<string, string> = {};
    if (!current) local.current = "La contraseña actual es obligatoria.";
    if (problem) local.password = problem;
    setFields(local);
    setSaved("");
    if (Object.keys(local).length > 0) return;
    const id = ++request.current;
    setPending(true);
    setFormError("");
    try {
      const body = await apiFetch<{ message: string }>("/auth/change-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ current_password: current, new_password: password }),
      });
      if (id !== request.current) return;
      setSaved(body.message || "La contraseña se ha actualizado.");
      setCurrent("");
      setPassword("");
      setConfirmation("");
    } catch (error: unknown) {
      if (id !== request.current) return;
      if (error instanceof ApiError && error.status === 401) return;
      const message = error instanceof ApiError ? error.message : "No se pudo cambiar la contraseña.";
      const code = error instanceof ApiError ? error.code : "";
      if (code === "current_password") {
        setFields({ current: message });
        currentRef.current?.focus();
      } else if (code === "same_password") {
        setFields({ password: message });
      } else {
        setFormError(message);
        alertRef.current?.focus();
      }
    } finally {
      if (id === request.current) setPending(false);
    }
  }

  return (
    <>
      <h1>Cambiar la contraseña</h1>
      <p className="lead">
        La contraseña de <strong>{email}</strong> cambia en esta sesión. Hace falta la actual.
      </p>
      {saved ? (
        <p className="status-line" role="status">
          {saved}
        </p>
      ) : null}
      {formError ? (
        <ErrorBanner
          title="No se pudo cambiar"
          message={formError}
          alertRef={alertRef}
          onRetry={() => currentRef.current?.focus()}
        />
      ) : null}
      <form className="panel stack" onSubmit={onSubmit} noValidate>
        <fieldset className="stack" disabled={pending}>
          <div className="field">
            <label htmlFor="change-current">Contraseña actual</label>
            <input
              id="change-current"
              ref={currentRef}
              name="current_password"
              type="password"
              autoComplete="current-password"
              value={current}
              aria-invalid={fields.current ? "true" : "false"}
              aria-describedby={fields.current ? "change-current-error" : undefined}
              onChange={(event) => setCurrent(event.target.value)}
            />
            {fields.current ? (
              <p id="change-current-error" className="field-error">
                {fields.current}
              </p>
            ) : null}
          </div>
          <div className="field">
            <label htmlFor="change-password">Nueva contraseña</label>
            <input
              id="change-password"
              name="new_password"
              type="password"
              autoComplete="new-password"
              value={password}
              aria-invalid={fields.password ? "true" : "false"}
              aria-describedby={fields.password ? "change-password-error" : undefined}
              onChange={(event) => setPassword(event.target.value)}
            />
            {fields.password ? (
              <p id="change-password-error" className="field-error">
                {fields.password}
              </p>
            ) : null}
          </div>
          <div className="field">
            <label htmlFor="change-confirmation">Confirmación</label>
            <input
              id="change-confirmation"
              name="confirmation"
              type="password"
              autoComplete="new-password"
              value={confirmation}
              onChange={(event) => setConfirmation(event.target.value)}
            />
          </div>
          <p className="actions">
            <button className="button" type="submit" disabled={pending} aria-busy={pending}>
              Cambiar contraseña
            </button>
          </p>
        </fieldset>
        {pending ? <LoadingState label="Cambiando la contraseña…" /> : null}
        <p>
          <a href="/account/profile">Volver al perfil</a>
        </p>
      </form>
    </>
  );
}
