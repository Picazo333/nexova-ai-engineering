export default function NotFound() {
  return (
    <main id="contenido" className="panel">
      <div className="wrap">
        <h1>No encontramos esa ruta</h1>
        <p>El panel interno no tiene esa ruta.</p>
        <p className="actions">
          <a className="button" href="/">
            Volver al panel
          </a>
          <a className="button secondary" href="/backoffice/inventory/products">
            Ir a activos
          </a>
        </p>
      </div>
    </main>
  );
}
