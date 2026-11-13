"use client";

import { usePathname } from "next/navigation";

import { apiOrigin, portalUrl } from "@/lib/public-urls";

const LINKS = [
  { href: "/", label: "Panel", match: (path: string) => path === "/" },
  {
    href: "/backoffice/inventory/products",
    label: "Inventario",
    match: (path: string) => path.startsWith("/backoffice/inventory"),
  },
  { href: "/login", label: "Entrar", match: (path: string) => path === "/login" },
];

export function SiteHeader() {
  const pathname = usePathname() || "/";
  const portal = portalUrl();
  const api = apiOrigin();
  return (
    <header className="site-header">
      <div className="wrap header-inner">
        <p className="product">Nexova · panel interno</p>
        <nav className="nav" aria-label="Secciones">
          {LINKS.map((link) => {
            const current = link.match(pathname);
            return (
              <a key={link.href} href={link.href} aria-current={current ? "page" : undefined}>
                {link.label}
              </a>
            );
          })}
          <a href={portal}>Portal</a>
          <a href={`${api}/incidencias`}>Gestor en la API</a>
        </nav>
      </div>
    </header>
  );
}
