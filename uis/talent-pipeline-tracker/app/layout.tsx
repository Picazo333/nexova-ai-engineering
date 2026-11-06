import type { Metadata } from "next";
import { AppShell } from "@/components/AppShell";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "Seguimiento de candidaturas · Nexova Solutions",
    template: "%s · Nexova Solutions",
  },
  description:
    "Herramienta interna de Operaciones de Selección para ver, filtrar y actualizar candidaturas en el tracker.",
  robots: { index: false, follow: false },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="es">
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html:
              "try{var m=window.matchMedia('(prefers-reduced-motion: reduce)');var a=function(){document.documentElement.dataset.motion=m.matches?'reduced':'full'};a();m.addEventListener('change',a);}catch(e){}",
          }}
        />
      </head>
      <body>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
