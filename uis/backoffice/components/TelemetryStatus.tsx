"use client";

import { useSyncExternalStore } from "react";

import { flushTelemetry, getTelemetrySnapshot, subscribeTelemetry } from "@/lib/telemetry";

export function TelemetryStatus() {
  const snap = useSyncExternalStore(subscribeTelemetry, getTelemetrySnapshot, getTelemetrySnapshot);
  if (process.env.NODE_ENV !== "development") return null;
  const counts = `${snap.queued} en cola · ${snap.sent} enviados`;
  return (
    <p className="telemetry-status" role="status" aria-live="polite" data-testid="telemetry-status">
      {snap.phase === "loading" ? <span>Enviando el lote de telemetría… </span> : null}
      {snap.phase === "empty" ? <span>Telemetría de desarrollo: sin eventos en esta sesión.</span> : null}
      {snap.phase === "error" ? (
        <span>
          Telemetría de desarrollo: {snap.error} {counts}.
        </span>
      ) : null}
      {snap.phase === "ready" ? <span>Telemetría de desarrollo: {counts}.</span> : null}
      {snap.phase === "error" && snap.queued > 0 ? (
        <button type="button" onClick={() => void flushTelemetry()}>
          Reintentar el envío
        </button>
      ) : null}
    </p>
  );
}
