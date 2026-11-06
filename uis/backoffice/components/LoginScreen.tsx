"use client";

import { useRef, useState } from "react";
import { useRouter } from "next/navigation";

import { ApiError } from "@/lib/http";
import { login } from "@/lib/auth";
import { safeNext, viewLabel } from "@/lib/paths";
import { writeToken } from "@/lib/session";

export function LoginScreen({ nextRaw, reason }: { nextRaw: string | null; reason: string | null }) {
  const router = useRouter();
  const next = safeNext(nextRaw);
  const expired = reason === "expired";
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [formError, setFormError] = useState("");
  const [pending, setPending] = useState(false);
  const request = useRef(0);
  const alertRef = useRef<HTMLDivElement>(null);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (pending) return;
    const trimmed = email.trim();
    if (!trimmed || !trimmed.includes("@")) {
      setFormError("Escribe el correo de la cuenta.");
      alertRef.current?.focus();
      return;
    }
    if (!password) {
      setFormError("Escribe la contraseña.");
      alertRef.current?.focus();
      return;
    }
    const id = ++request.current;
    setPending(true);
    setFormError("");
    try {
      const token = await login(trimmed, password);
      if (id !== request.current) return;
      if (!token.access_token || !writeToken(token.access_token)) {
        setFormError("Este navegador no puede guardar el token en localStorage.");
        alertRef.current?.focus();
        return;
      }
      router.push(next);
    } catch (error: unknown) {
      if (id !== request.current) return;
      setFormError(error instanceof ApiError ? error.message : "No se pudo iniciar sesión.");
      alertRef.current?.focus();
    } finally {
      if (id === request.current) setPending(false);
    }
  }

  return (
    <main id="contenido" className="panel">
      <div className="wrap">
        <h1>Entrar al panel interno</h1>
        <p className="lead">
          El inventario pide el JWT de <code>POST /auth/login</code>. El token se guarda en este origen, en{" "}
          <code>localStorage</code>, con la clave <code>nexova-access-token</code>. El portal usa la misma clave en
          su propio origen.
        </p>
        {expired ? (
          <div className="banner warn" role="status">
            <h2>La sesión ha caducado</h2>
            <p>El token ya no es válido. Entra de nuevo para volver a {viewLabel(next)}.</p>
          </div>
        ) : null}
        {formError ? (
          <div className="banner" role="alert" tabIndex={-1} ref={alertRef}>
            <h2>No se pudo entrar</h2>
            <p>{formError}</p>
          </div>
        ) : null}
        <form onSubmit={onSubmit} noValidate>
          <div className="field">
            <label htmlFor="email">Correo</label>
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="username"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </div>
          <div className="field">
            <label htmlFor="password">Contraseña</label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </div>
          <p className="actions">
            <button type="submit" disabled={pending} aria-busy={pending}>
              {pending ? "Comprobando la sesión…" : "Entrar"}
            </button>
          </p>
        </form>
      </div>
    </main>
  );
}
