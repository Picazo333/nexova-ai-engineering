"use client";

import { useRef, useState } from "react";

import { useSession } from "@/components/SessionGate";
import { ErrorBanner, LoadingState } from "@/components/AsyncStatus";
import { ApiError, apiFetch } from "@/lib/api";
import { textLimit } from "@/lib/forms";
import type { Profile } from "@/lib/types";

export function ProfileScreen() {
  const { phase, refresh } = useSession();
  if (phase.kind !== "in") return null;
  const profile = phase.me.profile ?? {
    id: "",
    user_id: phase.me.id ?? "",
    name: null,
    phone: null,
    address: null,
  };
  return (
    <ProfileForm
      key={phase.me.id ?? "session"}
      email={phase.me.email ?? ""}
      role={phase.me.role ?? ""}
      profile={profile}
      refresh={refresh}
    />
  );
}

function ProfileForm({
  email,
  role,
  profile,
  refresh,
}: {
  email: string;
  role: string;
  profile: Profile;
  refresh: () => Promise<void>;
}) {
  const [name, setName] = useState(profile.name ?? "");
  const [phone, setPhone] = useState(profile.phone ?? "");
  const [address, setAddress] = useState(profile.address ?? "");
  const [fields, setFields] = useState<Record<string, string>>({});
  const [error, setError] = useState("");
  const [saved, setSaved] = useState("");
  const [pending, setPending] = useState(false);
  const request = useRef(0);
  const alertRef = useRef<HTMLDivElement>(null);
  const empty = !profile.name && !profile.phone && !profile.address;

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (pending) return;
    const local: Record<string, string> = {};
    const nameError = textLimit(name, 200, "El nombre");
    const phoneError = textLimit(phone, 40, "El teléfono");
    const addressError = textLimit(address, 400, "La dirección");
    if (nameError) local.name = nameError;
    if (phoneError) local.phone = phoneError;
    if (addressError) local.address = addressError;
    setFields(local);
    setSaved("");
    if (Object.keys(local).length > 0) return;
    const id = ++request.current;
    setPending(true);
    setError("");
    try {
      await apiFetch<Profile>("/profiles/me", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: name.trim() || null,
          phone: phone.trim() || null,
          address: address.trim() || null,
        }),
      });
      if (id !== request.current) return;
      await refresh();
      if (id !== request.current) return;
      setSaved("Perfil actualizado.");
    } catch (caught: unknown) {
      if (id !== request.current) return;
      if (caught instanceof ApiError && caught.status === 401) return;
      setError(caught instanceof ApiError ? caught.message : "No se pudo guardar el perfil.");
      alertRef.current?.focus();
    } finally {
      if (id === request.current) setPending(false);
    }
  }

  return (
    <>
      <h1>Perfil de la cuenta</h1>
      <p className="lead">
        El correo sale de <code>User</code>. El nombre y el contacto salen del <code>Profile</code> vinculado,
        los dos en <code>GET /auth/me</code>.
      </p>
      <dl className="meta">
        <dt>Correo</dt>
        <dd>{email}</dd>
        <dt>Rol</dt>
        <dd>{role}</dd>
      </dl>
      <p>
        <a href="/account/change-password">Cambiar contraseña</a>
      </p>
      {empty && !saved ? (
        <div className="banner" role="status">
          <h2>El perfil no tiene datos de contacto</h2>
          <p>Puedes añadir nombre, teléfono y dirección. El correo no se edita en esta vista.</p>
        </div>
      ) : null}
      {saved ? (
        <p className="status-line" role="status">
          {saved}
        </p>
      ) : null}
      {error ? (
        <ErrorBanner
          title="No se pudo guardar"
          message={error}
          alertRef={alertRef}
          onRetry={() => document.getElementById("profile-name")?.focus()}
        />
      ) : null}
      <form className="panel stack" onSubmit={onSubmit} noValidate>
        <div className="field">
          <label htmlFor="profile-name">Nombre</label>
          <input
            id="profile-name"
            value={name}
            aria-invalid={fields.name ? "true" : "false"}
            aria-describedby={fields.name ? "profile-name-error" : undefined}
            onChange={(event) => setName(event.target.value)}
          />
          {fields.name ? (
            <p id="profile-name-error" className="field-error">
              {fields.name}
            </p>
          ) : null}
        </div>
        <div className="field">
          <label htmlFor="profile-phone">Teléfono</label>
          <input
            id="profile-phone"
            type="tel"
            autoComplete="tel"
            value={phone}
            aria-invalid={fields.phone ? "true" : "false"}
            aria-describedby={fields.phone ? "profile-phone-error" : undefined}
            onChange={(event) => setPhone(event.target.value)}
          />
          {fields.phone ? (
            <p id="profile-phone-error" className="field-error">
              {fields.phone}
            </p>
          ) : null}
        </div>
        <div className="field">
          <label htmlFor="profile-address">Dirección</label>
          <input
            id="profile-address"
            autoComplete="street-address"
            value={address}
            aria-invalid={fields.address ? "true" : "false"}
            aria-describedby={fields.address ? "profile-address-error" : undefined}
            onChange={(event) => setAddress(event.target.value)}
          />
          {fields.address ? (
            <p id="profile-address-error" className="field-error">
              {fields.address}
            </p>
          ) : null}
        </div>
        <p className="actions">
          <button className="button" type="submit" disabled={pending} aria-busy={pending}>
            Guardar perfil
          </button>
        </p>
        {pending ? <LoadingState label="Guardando el perfil…" /> : null}
      </form>
    </>
  );
}
