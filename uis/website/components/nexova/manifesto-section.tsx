import { Reveal } from '@/components/nexova/reveal'

export function ManifestoSection() {
  return (
    <section id="enfoque" className="relative bg-obsidian px-6 py-28 md:px-16 md:py-40">
      <div className="mx-auto flex max-w-6xl flex-col gap-16">
        <Reveal className="flex items-center gap-4">
          <span className="font-mono text-[11px] uppercase tracking-[0.3em] text-oxblood">
            01 — MANIFIESTO
          </span>
          <span className="h-px flex-1 bg-ash/20" aria-hidden="true" />
        </Reveal>

        <div className="grid gap-12 md:grid-cols-[0.85fr_1.4fr] md:gap-20">
          <Reveal
            y={16}
            className="hidden flex-col gap-6 font-mono text-[11px] uppercase tracking-[0.25em] text-ash md:flex"
          >
            <span>MATERIA</span>
            <span>CONTEXTO</span>
            <span>SISTEMA</span>
            <span>HUMANO</span>
          </Reveal>

          <div className="flex flex-col gap-14">
            <Reveal>
              <h2 className="font-serif text-[clamp(2.25rem,6.5vw,4.75rem)] leading-[1.02] text-bone">
                EL CRITERIO
                <br />
                NO SE AUTOMATIZA.
                <br />
                <span className="text-oxblood">SE ESTRUCTURA.</span>
              </h2>
            </Reveal>

            <Reveal delay={150}>
              <div className="grid gap-8 border-t border-ash/15 pt-10 font-sans text-sm leading-relaxed text-ash md:grid-cols-2 md:text-base">
                <p>
                  Nexova opera en la intersección entre selección humana y sistemas disciplinados.
                  Cada decisión ejecutiva atraviesa un marco que preserva el juicio — nunca lo
                  sustituye.
                </p>
                <p>
                  Formación, soporte y talento externalizado convergen en una misma arquitectura
                  operativa: visible, auditable, deliberada.
                </p>
              </div>
            </Reveal>
          </div>
        </div>
      </div>
    </section>
  )
}
