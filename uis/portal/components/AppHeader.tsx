"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { clearToken } from "@/lib/session";

const LINKS = [
  { href: "/", label: "Incidencias" },
  { href: "/proveedores", label: "Proveedores" },
  { href: "/account/profile", label: "Perfil" },
];

export function AppHeader({ email }: { email: string }) {
  const pathname = usePathname();

  function logout() {
    clearToken();
    window.location.assign("/login");
  }

  return (
    <header className="site-header">
      <div className="wrap header-inner">
        <p className="product">
          Nexova <span>Portal interno</span>
        </p>
        <nav className="nav" aria-label="Secciones">
          {LINKS.map((link) => (
            <Link key={link.href} href={link.href} aria-current={pathname === link.href ? "page" : undefined}>
              {link.label}
            </Link>
          ))}
        </nav>
        <div className="header-actions">
          <p className="who">{email}</p>
          <button className="button secondary" type="button" onClick={logout}>
            Cerrar sesión
          </button>
        </div>
      </div>
    </header>
  );
}
