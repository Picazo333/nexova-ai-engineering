"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";

import { ErrorBanner, LoadingState } from "@/components/AsyncStatus";
import { PublicBar } from "@/components/PublicBar";
import { ApiError, apiFetch } from "@/lib/api";
import { passwordConfirmError } from "@/lib/forms";

const DEAD: Record<string, string> = {
  expired: "El enlace ha caducado",
  used: "Este enlace ya se usó",
  invalid: "El enlace no es válido",
};

export function ResetPasswordScreen({ token }: { token: string }) {
  const router = useRouter();
  const trimmed = token.trim();
  const [password, setPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [passwordMessage, setPasswordMessage] = useState("");
  const [formError, setFormError] = useState("");
  const [code, setCode] = useState("");
  const [pending, setPending] = useState(false);
  const request = useRef(0);
  const alertRef = useRef<HTMLDivElement>(null);
  const passwordRef = useRef<HTMLInputElement>(null);
  const deadTitle = DEAD[code] ?? "";

  useEffect(() => {
    if (formError) alertRef.current?.focus();
  }, [formError, code]);

  if (!trimmed) {
    return (
      <>
        <PublicBar />
        <main id="contenido">
          <div className="wrap">
            <h1>Restablecer la contraseña</h1>
            <div className="banner" role="status">
              <h2>Falta el enlace de recuperación</h2>
              <p>Esta página necesita el token que viene en el enlace. Pide uno nuevo.</p>
              <p className="actions">
                <a className="button" href="/forgot-password">
                  Pedir un enlace
                </a>
              </p>
            </div>
          </div>
        </main>
      </>
    );
  }

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (pending || deadTitle) return;
    const problem = passwordConfirmError(password, confirmation);
    setPasswordMessage(problem ?? "");
    if (problem) return;
    const id = ++request.current;
    setPending(true);
    setFormError("");
    setCode("");
    try {
      await apiFetch<{ message: string }>(
        "/auth/reset-password",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ token: trimmed, new_password: password }),
        },
        { auth: false },
      );
      if (id !== request.current) return;
      router.push("/login?notice=password-updated");
    } catch (error: unknown) {
      if (id !== request.current) return;
      const apiError = error instanceof ApiError ? error : null;
      const nextCode = apiError?.code ?? "";
      setCode(nextCode);
      setFormError(apiError?.message ?? "No se pudo restablecer la contraseña.");
    } finally {
      if (id === request.current) setPending(false);
    }
  }

  return (
    <>
      <PublicBar />
      <main id="contenido">
        <div className="wrap">
          <h1>Restablecer la contraseña</h1>
          <p className="lead">Elige una contraseña nueva. El enlace solo puede usarse una vez.</p>
          {deadTitle ? (
            <div className="alert" role="alert" tabIndex={-1} ref={alertRef}>
              <h2>{deadTitle}</h2>
              <p>{formError}</p>
              <p className="actions">
                <a className="button" href="/forgot-password">
                  Pedir otro enlace
                </a>
              </p>
            </div>
          ) : null}
          {formError && !deadTitle ? (
            <ErrorBanner
              title="No se pudo guardar"
              message={formError}
              alertRef={alertRef}
              onRetry={() => passwordRef.current?.focus()}
            />
          ) : null}
          {deadTitle ? null : (
            <form className="panel stack" onSubmit={onSubmit} noValidate>
              <fieldset className="stack" disabled={pending}>
                <div className="field">
                  <label htmlFor="reset-password">Nueva contraseña</label>
                  <input
                    id="reset-password"
                    ref={passwordRef}
                    name="new_password"
                    type="password"
                    autoComplete="new-password"
                    value={password}
                    aria-invalid={passwordMessage ? "true" : "false"}
                    aria-describedby={passwordMessage ? "reset-password-error" : undefined}
                    onChange={(event) => setPassword(event.target.value)}
                  />
                  {passwordMessage ? (
                    <p id="reset-password-error" className="field-error">
                      {passwordMessage}
                    </p>
                  ) : null}
                </div>
                <div className="field">
                  <label htmlFor="reset-confirmation">Confirmación</label>
                  <input
                    id="reset-confirmation"
                    name="confirmation"
                    type="password"
                    autoComplete="new-password"
                    value={confirmation}
                    onChange={(event) => setConfirmation(event.target.value)}
                  />
                </div>
                <p className="actions">
                  <button className="button" type="submit" disabled={pending} aria-busy={pending}>
                    Guardar contraseña
                  </button>
                </p>
              </fieldset>
              {pending ? <LoadingState label="Guardando la contraseña…" /> : null}
            </form>
          )}
        </div>
      </main>
    </>
  );
}
