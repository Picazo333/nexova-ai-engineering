export function SiteHeader() {
  return (
    <header className="fixed inset-x-0 top-0 z-50 flex items-center justify-between px-6 py-6 md:px-12 md:py-8">
      <a href="#top" className="font-serif text-xl tracking-[0.06em] text-bone md:text-2xl" aria-label="NEXOVA — inicio">
        NEXOVA
      </a>

      <nav
        aria-label="Navegación principal"
        className="hidden items-center gap-10 font-mono text-[11px] uppercase tracking-[0.22em] text-ash md:flex"
      >
        <a href="#servicios" className="transition-colors hover:text-bone">SERVICIOS</a>
        <a href="#experiencia" className="transition-colors hover:text-bone">EXPERIENCIA</a>
        <a href="#enfoque" className="transition-colors hover:text-bone">ENFOQUE</a>
        <a href="#presencia" className="transition-colors hover:text-bone">PRESENCIA</a>
      </nav>

      <a
        href="#contacto"
        className="shrink-0 border border-bone/30 px-3 py-2 font-mono text-[9px] uppercase tracking-[0.16em] text-bone transition-colors hover:border-bone hover:bg-bone hover:text-obsidian md:px-4 md:text-[11px] md:tracking-[0.18em]"
      >
        INICIAR CONVERSACIÓN
      </a>
    </header>
  )
}
