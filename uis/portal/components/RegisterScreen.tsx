"use client";

import { useRef, useState } from "react";
import { useRouter } from "next/navigation";

import { ErrorBanner, LoadingState } from "@/components/AsyncStatus";
import { ApiError, apiFetch } from "@/lib/api";
import { emailError, passwordError, textLimit } from "@/lib/forms";
import { safeNext, viewLabel } from "@/lib/paths";
import { writeToken } from "@/lib/session";
import type { TokenResponse } from "@/lib/types";

type Fields = {
  email: string;
  password: string;
  name: string;
  phone: string;
  address: string;
};

const EMPTY: Fields = { email: "", password: "", name: "", phone: "", address: "" };

export function RegisterScreen({ nextRaw }: { nextRaw: string | null }) {
  const router = useRouter();
  const next = safeNext(nextRaw);
  const [values, setValues] = useState<Fields>(EMPTY);
  const [fields, setFields] = useState<Record<string, string>>({});
  const [formError, setFormError] = useState("");
  const [pending, setPending] = useState(false);
  const [status, setStatus] = useState("");
  const request = useRef(0);
  const alertRef = useRef<HTMLDivElement>(null);

  function set<K extends keyof Fields>(key: K, value: string) {
    setValues((current) => ({ ...current, [key]: value }));
  }

  function clientErrors(current: Fields): Record<string, string> {
    const nextErrors: Record<string, string> = {};
    const email = emailError(current.email);
    const password = passwordError(current.password);
    const name = textLimit(current.name, 200, "El nombre");
    const phone = textLimit(current.phone, 40, "El teléfono");
    const address = textLimit(current.address, 400, "La dirección");
    if (email) nextErrors.email = email;
    if (password) nextErrors.password = password;
    if (name) nextErrors.name = name;
    if (phone) nextErrors.phone = phone;
    if (address) nextErrors.address = address;
    return nextErrors;
  }

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (pending) return;
    const local = clientErrors(values);
    setFields(local);
    setFormError("");
    if (Object.keys(local).length > 0) return;
    const id = ++request.current;
    setPending(true);
    setStatus("Creando la cuenta…");
    const email = values.email.trim();
    const body = {
      email,
      password: values.password,
      name: values.name.trim() || null,
      phone: values.phone.trim() || null,
      address: values.address.trim() || null,
    };
    try {
      try {
        await apiFetch(
          "/users",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
          },
          { auth: false },
        );
      } catch (error: unknown) {
        if (id !== request.current) return;
        if (error instanceof ApiError) {
          setFields(error.fields ?? {});
          setFormError(error.message);
        } else {
          setFormError("No se pudo crear la cuenta. Los datos escritos se conservan.");
        }
        setStatus("");
        alertRef.current?.focus();
        return;
      }
      if (id !== request.current) return;
      setStatus("Entrando con la cuenta nueva…");
      try {
        const token = await apiFetch<TokenResponse>(
          "/auth/login",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password: values.password }),
          },
          { auth: false },
        );
        if (id !== request.current) return;
        if (!token?.access_token || !writeToken(token.access_token)) {
          setFormError("La cuenta se creó, pero este navegador no guardó el token.");
          setStatus("");
          alertRef.current?.focus();
          return;
        }
        router.push(next);
      } catch (error: unknown) {
        if (id !== request.current) return;
        const message = error instanceof ApiError ? error.message : "No se pudo iniciar sesión.";
        setFormError(`La cuenta se creó, pero no se pudo entrar. ${message}`);
        setStatus("");
        alertRef.current?.focus();
      }
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
          <h1>Crear una cuenta</h1>
          <p className="lead">
            El alta llama a <code>POST /users</code> y, si la API acepta la cuenta, a{" "}
            <code>POST /auth/login</code> con el mismo correo y la misma contraseña.
          </p>
          {next !== "/" ? (
            <p className="note">Después de crear la cuenta volverás a {viewLabel(next)}.</p>
          ) : null}
          {formError ? (
            <ErrorBanner
              title="No se pudo crear la cuenta"
              message={formError}
              alertRef={alertRef}
              onRetry={() => document.getElementById("register-email")?.focus()}
            />
          ) : null}
          <form className="panel stack" onSubmit={onSubmit} noValidate>
            <Field
              id="register-email"
              label="Correo"
              type="email"
              autoComplete="email"
              value={values.email}
              error={fields.email}
              onChange={(value) => set("email", value)}
            />
            <Field
              id="register-password"
              label="Contraseña"
              type="password"
              autoComplete="new-password"
              value={values.password}
              error={fields.password}
              onChange={(value) => set("password", value)}
            />
            <Field
              id="register-name"
              label="Nombre"
              value={values.name}
              error={fields.name}
              onChange={(value) => set("name", value)}
            />
            <Field
              id="register-phone"
              label="Teléfono"
              type="tel"
              autoComplete="tel"
              value={values.phone}
              error={fields.phone}
              onChange={(value) => set("phone", value)}
            />
            <Field
              id="register-address"
              label="Dirección"
              autoComplete="street-address"
              value={values.address}
              error={fields.address}
              onChange={(value) => set("address", value)}
            />
            <p className="actions">
              <button className="button" type="submit" disabled={pending} aria-busy={pending}>
                Crear cuenta
              </button>
            </p>
            {pending ? <LoadingState label={status || "Creando la cuenta…"} /> : <p role="status">{status}</p>}
            <p>
              <a href={`/login?next=${encodeURIComponent(next)}`}>Ya tengo cuenta</a>
            </p>
          </form>
        </div>
      </main>
    </>
  );
}

function Field({
  id,
  label,
  type = "text",
  autoComplete,
  value,
  error,
  onChange,
}: {
  id: string;
  label: string;
  type?: string;
  autoComplete?: string;
  value: string;
  error?: string;
  onChange: (value: string) => void;
}) {
  return (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      <input
        id={id}
        name={id}
        type={type}
        autoComplete={autoComplete}
        value={value}
        aria-invalid={error ? "true" : "false"}
        aria-describedby={error ? `${id}-error` : undefined}
        onChange={(event) => onChange(event.target.value)}
      />
      {error ? (
        <p id={`${id}-error`} className="field-error">
          {error}
        </p>
      ) : null}
    </div>
  );
}
