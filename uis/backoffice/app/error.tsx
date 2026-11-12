"use client";

import { useEffect } from "react";

import { recordException } from "@/lib/telemetry";

export default function Error({ error, reset }: { error: Error; reset: () => void }) {
  useEffect(() => {
    void recordException(error);
  }, [error]);
  return (
    <main id="contenido" className="panel">
      <div className="wrap">
        <h1>No se pudo abrir el panel</h1>
        <p className="alert" role="alert">
          La comprobación falló. El filtro, si lo habías escrito, sigue en esta pestaña.
        </p>
        <button type="button" onClick={() => reset()}>
          Reintentar
        </button>
      </div>
    </main>
  );
}
