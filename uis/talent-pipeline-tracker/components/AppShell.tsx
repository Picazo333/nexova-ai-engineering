import Link from "next/link";
import { SignalLockup } from "@/components/SignalLockup";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <>
      <a className="skip" href="#contenido">
        Saltar al contenido
      </a>
      <header className="site-header">
        <div className="shell header-bar">
          <Link className="brand" href="/">
            <span className="brand-org">Nexova Solutions</span>
            <span className="brand-product">Seguimiento de candidaturas</span>
          </Link>
          <nav aria-label="Secciones">
            <ul className="nav-list">
              <li>
                <Link href="/">Candidaturas</Link>
              </li>
              <li>
                <Link href="/candidates/new">Registrar candidatura</Link>
              </li>
            </ul>
          </nav>
        </div>
      </header>
      <main id="contenido" tabIndex={-1} className="shell site-main">
        {children}
      </main>
      <footer className="site-footer">
        <div className="shell footer-grid">
          <div>
            <p>Nexova Solutions · Operaciones de Selección · Valencia y Miami.</p>
            <p>
              Herramienta interna para consultar el tracker del curso. Los registros salen de la API
              pública y no son la base de producción de Nexova.
            </p>
          </div>
          <SignalLockup />
        </div>
      </footer>
      <noscript>
        <p className="noscript">Esta herramienta necesita JavaScript para consultar el tracker.</p>
      </noscript>
    </>
  );
}
