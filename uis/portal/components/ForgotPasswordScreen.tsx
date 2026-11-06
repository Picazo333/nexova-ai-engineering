"use client";

import { useRef, useState } from "react";

import { ErrorBanner, LoadingState } from "@/components/AsyncStatus";
import { PublicBar } from "@/components/PublicBar";
import { ApiError, apiFetch } from "@/lib/api";
import { emailError } from "@/lib/forms";

export const FORGOT_CONFIRMATION =
  "Si esa dirección está registrada, recibirás un enlace en breve.";

export function ForgotPasswordScreen() {
  const [email, setEmail] = useState("");
  const [emailMessage, setEmailMessage] = useState("");
  const [formError, setFormError] = useState("");
  const [pending, setPending] = useState(false);
  const [done, setDone] = useState(false);
  const request = useRef(0);
  const alertRef = useRef<HTMLDivElement>(null);
  const emailRef = useRef<HTMLInputElement>(null);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (pending || done) return;
    const problem = emailError(email);
    setEmailMessage(problem ?? "");
    if (problem) return;
    const id = ++request.current;
    setPending(true);
    setFormError("");
    try {
      await apiFetch<{ message: string }>(
        "/auth/forgot-password",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: email.trim() }),
        },
        { auth: false },
      );
      if (id !== request.current) return;
      setDone(true);
    } catch (error: unknown) {
      if (id !== request.current) return;
      const message = error instanceof ApiError ? error.message : "No se pudo enviar la solicitud.";
      if (error instanceof ApiError && error.status === 422) {
        setEmailMessage(message);
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
      <PublicBar />
      <main id="contenido">
        <div className="wrap">
          <h1>Recuperar la contraseña</h1>
          <p className="lead">
            Escribe el correo de la cuenta. La respuesta es la misma tanto si ese correo está registrado como si no.
          </p>
          {done ? (
            <div className="banner" role="status">
              <h2>Solicitud registrada</h2>
              <p>{FORGOT_CONFIRMATION}</p>
              <p>El formulario queda cerrado para no repetir la misma petición.</p>
            </div>
          ) : null}
          {formError ? (
            <ErrorBanner
              title="No se pudo enviar"
              message={formError}
              alertRef={alertRef}
              onRetry={() => emailRef.current?.focus()}
            />
          ) : null}
          <form className="panel stack" onSubmit={onSubmit} noValidate>
            <fieldset className="stack" disabled={done || pending}>
              <div className="field">
                <label htmlFor="forgot-email">Correo</label>
                <input
                  id="forgot-email"
                  ref={emailRef}
                  name="email"
                  type="email"
                  autoComplete="email"
                  value={email}
                  aria-invalid={emailMessage ? "true" : "false"}
                  aria-describedby={emailMessage ? "forgot-email-error" : undefined}
                  onChange={(event) => setEmail(event.target.value)}
                />
                {emailMessage ? (
                  <p id="forgot-email-error" className="field-error">
                    {emailMessage}
                  </p>
                ) : null}
              </div>
              <p className="actions">
                <button className="button" type="submit" disabled={done || pending} aria-busy={pending}>
                  Enviar enlace
                </button>
              </p>
            </fieldset>
            {pending ? <LoadingState label="Enviando la solicitud…" /> : null}
            <p>
              <a href="/login">Volver a entrar</a>
            </p>
          </form>
        </div>
      </main>
    </>
  );
}
