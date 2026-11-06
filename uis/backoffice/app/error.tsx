"use client";

export default function Error({ reset }: { error: Error; reset: () => void }) {
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
