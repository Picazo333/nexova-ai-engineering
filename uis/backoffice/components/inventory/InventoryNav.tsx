"use client";

import { usePathname } from "next/navigation";

const LINKS = [
  { href: "/backoffice/inventory/products", label: "Activos" },
  { href: "/backoffice/inventory/orders/inbound", label: "Entrada de activos" },
  { href: "/backoffice/inventory/orders/outbound", label: "Salida de activos" },
  { href: "/backoffice/inventory/orders", label: "Historial" },
];

export function InventoryNav() {
  const pathname = usePathname();
  return (
    <nav aria-label="Sección de inventario">
      <ul className="subnav">
        {LINKS.map((link) => (
          <li key={link.href}>
            <a href={link.href} aria-current={pathname === link.href ? "page" : undefined}>
              {link.label}
            </a>
          </li>
        ))}
      </ul>
    </nav>
  );
}
