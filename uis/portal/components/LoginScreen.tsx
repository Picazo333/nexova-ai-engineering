"use client";

import { useRef, useState } from "react";
import { useRouter } from "next/navigation";

import { ApiError, apiFetch } from "@/lib/api";
import { emailError } from "@/lib/forms";
import { safeNext, viewLabel } from "@/lib/paths";
import { writeToken } from "@/lib/session";
import type { TokenResponse } from "@/lib/types";

export function LoginScreen({ nextRaw, reason }: { nextRaw: string | null; reason: string | null }) {
  const router = useRouter();
  const next = safeNext(nextRaw);
  const expired = reason === "expired";
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [emailMessage, setEmailMessage] = useState("");
  const [formError, setFormError] = useState("");
  const [pending, setPending] = useState(false);
  const [status, setStatus] = useState("");
  const request = useRef(0);
  const alertRef = useRef<HTMLDivElement>(null);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (pending) return;
    const emailProblem = emailError(email);
    setEmailMessage(emailProblem ?? "");
    if (!password) {
      setFormError("Escribe la contraseña.");
      alertRef.current?.focus();
      return;
    }
    if (emailProblem) return;
    const id = ++request.current;
    setPending(true);
    setFormError("");
    setStatus("Comprobando la sesión…");
    try {
      const token = await apiFetch<TokenResponse>(
        "/auth/login",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: email.trim(), password }),
        },
        { auth: false },
      );
      if (id !== request.current) return;
      if (!token.access_token || !writeToken(token.access_token)) {
        setFormError("Este navegador no puede guardar el token en localStorage.");
        setStatus("");
        alertRef.current?.focus();
        return;
      }
      router.push(next);
    } catch (error: unknown) {
      if (id !== request.current) return;
      const message = error instanceof ApiError ? error.message : "No se pudo iniciar sesión.";
      setFormError(message);
      setStatus("");
      alertRef.current?.focus();
    } finally {
      if (id === request.current) setPending(false);
    }
  }

  return (
    <>
      <header className="topbar">
        <div className="wrap topbar-inner">
          <p className="product">
            Nexova <span>Portal interno</span>
          </p>
        </div>
      </header>
      <main id="contenido">
        <div className="wrap">
          <h1>Entrar al portal interno</h1>
          <p className="lead">
            El análisis de tickets y el directorio de proveedores piden el JWT que devuelve{" "}
            <code>POST /auth/login</code>.
          </p>
          {expired ? (
            <div className="banner" role="status">
              <h2>La sesión ha vencido</h2>
              <p>
                El token ya no es válido. Entra de nuevo para volver a {viewLabel(next)}.
              </p>
            </div>
          ) : null}
          {formError ? (
            <div className="alert" role="alert" tabIndex={-1} ref={alertRef}>
              <h2>No se pudo entrar</h2>
              <p>{formError}</p>
            </div>
          ) : null}
          <form className="panel stack" onSubmit={onSubmit} noValidate>
            <div className="field">
              <label htmlFor="login-email">Correo</label>
              <input
                id="login-email"
                name="email"
                type="email"
                autoComplete="email"
                value={email}
                aria-invalid={emailMessage ? "true" : "false"}
                aria-describedby={emailMessage ? "login-email-error" : undefined}
                onChange={(event) => setEmail(event.target.value)}
              />
              {emailMessage ? (
                <p id="login-email-error" className="field-error">
                  {emailMessage}
                </p>
              ) : null}
            </div>
            <div className="field">
              <label htmlFor="login-password">Contraseña</label>
              <input
                id="login-password"
                name="password"
                type="password"
                autoComplete="current-password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
              />
            </div>
            <p className="actions">
              <button className="button" type="submit" disabled={pending} aria-busy={pending}>
                Entrar
              </button>
            </p>
            <p role="status">{status}</p>
            <p>
              <a href={`/register?next=${encodeURIComponent(next)}`}>Crear una cuenta</a>
            </p>
          </form>
        </div>
      </main>
    </>
  );
}
