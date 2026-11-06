"use client";

export default function RouteError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <>
      <h1>No se pudo mostrar esta vista</h1>
      <div className="feedback feedback-error" role="alert">
        <p>{error.message || "Error inesperado."}</p>
        <button className="button button-secondary" type="button" onClick={reset}>
          Reintentar
        </button>
      </div>
    </>
  );
}
