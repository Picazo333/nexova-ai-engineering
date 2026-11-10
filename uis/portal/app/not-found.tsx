export default function NotFound() {
  return (
    <main id="contenido">
      <div className="wrap">
        <h1>Esta ruta no existe</h1>
        <p className="lead">El portal interno no tiene esa página.</p>
        <p>
          <a className="button" href="/login">
            Ir a entrar
          </a>
        </p>
      </div>
    </main>
  );
}
