import type { Metadata } from "next";

import { FooterLockup } from "@/components/FooterLockup";
import { apiOrigin, portalUrl } from "@/lib/public-urls";
import "./globals.css";

export const metadata: Metadata = {
  title: "Panel interno · Nexova",
  description: "Proceso Next.js del backoffice. Comprueba la API por el nombre del servicio Docker.",
  robots: { index: false, follow: false },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const portal = portalUrl();
  const api = apiOrigin();
  return (
    <html lang="es">
      <body>
        <a className="skip" href="#contenido">
          Saltar al contenido
        </a>
        <header className="site-header">
          <div className="wrap header-inner">
            <p className="product">Nexova · panel interno</p>
            <nav className="nav" aria-label="Secciones">
              <a href="/" aria-current="page">
                Panel
              </a>
              <a href={portal}>Portal</a>
              <a href={`${api}/incidencias`}>Gestor en la API</a>
            </nav>
          </div>
        </header>
        {children}
        <FooterLockup />
      </body>
    </html>
  );
}
