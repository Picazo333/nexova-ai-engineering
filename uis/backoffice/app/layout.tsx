import type { Metadata } from "next";

import { FooterLockup } from "@/components/FooterLockup";
import { MotionPref } from "@/components/MotionPref";
import { SiteHeader } from "@/components/SiteHeader";
import "./globals.css";

export const metadata: Metadata = {
  title: "Panel interno · Nexova",
  description: "Panel interno de Nexova. Inventario de activos, entradas y salidas, y comprobación de la API.",
  robots: { index: false, follow: false },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body>
        <MotionPref />
        <a className="skip" href="#contenido">
          Saltar al contenido
        </a>
        <SiteHeader />
        <noscript>
          <p className="note wrap">
            El inventario lee el token y llama a la API desde el navegador. Sin JavaScript no puede mostrar el stock
            ni registrar entradas o salidas.
          </p>
        </noscript>
        {children}
        <FooterLockup />
      </body>
    </html>
  );
}
