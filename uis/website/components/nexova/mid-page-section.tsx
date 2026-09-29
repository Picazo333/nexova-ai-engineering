import Image from 'next/image'
import { Reveal } from '@/components/nexova/reveal'

export function MidPageSection() {
  return (
    <section
      id="experiencia"
      className="relative min-h-[85vh] w-full overflow-hidden bg-obsidian md:min-h-screen"
    >
      <Image
        src="/nexova/A3_EDITORIAL_MID_PAGE.png"
        alt="Umbral entre dos columnas de piedra, figura de pie ante una luz lunar"
        fill
        className="object-cover"
        style={{ objectPosition: '58% 45%' }}
        sizes="100vw"
      />
      <div className="absolute inset-0 bg-gradient-to-t from-obsidian via-obsidian/25 to-obsidian/10" />
      <div className="absolute inset-0 bg-gradient-to-r from-obsidian/85 via-transparent to-transparent" />

      <div className="relative z-10 flex min-h-[85vh] flex-col justify-end px-6 py-16 md:min-h-screen md:px-16 md:py-28">
        <Reveal className="mb-8 flex items-center gap-4">
          <span className="h-px w-8 bg-oxblood" aria-hidden="true" />
          <span className="font-mono text-[11px] uppercase tracking-[0.3em] text-ash">
            02 — UMBRAL
          </span>
        </Reveal>
        <Reveal delay={100}>
          <h2 className="max-w-2xl font-serif text-[clamp(2rem,6vw,4.25rem)] leading-[1.05] text-bone">
            ENTRE LA RAZÓN
            <br />
            Y LA MATERIA,
            <br />
            UN SOLO <span className="text-oxblood">UMBRAL.</span>
          </h2>
        </Reveal>
        <Reveal delay={220}>
          <p className="mt-8 max-w-md font-sans text-sm leading-relaxed text-ash md:text-base">
            Cada decisión corporativa cruza un umbral entre lo estructural y lo humano. Nexova
            diseña ese paso para que sea intencional, no accidental.
          </p>
        </Reveal>
      </div>
    </section>
  )
}
