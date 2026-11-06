import type { Metadata } from "next";

import { FooterLockup } from "@/components/FooterLockup";
import { MotionPref } from "@/components/MotionPref";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "Portal interno de Nexova",
    template: "%s · Nexova",
  },
  description: "Acceso interno al análisis de tickets de soporte y al directorio de proveedores.",
  robots: { index: false, follow: false },
  icons: { icon: "/favicon.svg" },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body>
        <MotionPref />
        <a className="skip" href="#contenido">
          Saltar al contenido
        </a>
        {children}
        <FooterLockup />
      </body>
    </html>
  );
}
