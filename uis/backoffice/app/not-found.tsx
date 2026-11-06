export default function NotFound() {
  return (
    <main id="contenido" className="panel">
      <div className="wrap">
        <h1>No encontramos esa ruta</h1>
        <p>El panel interno solo publica la comprobación del servicio.</p>
        <p className="actions">
          <a className="button" href="/">
            Volver al panel
          </a>
        </p>
      </div>
    </main>
  );
}
