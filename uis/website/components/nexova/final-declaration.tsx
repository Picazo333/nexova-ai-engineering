import Image from 'next/image'
import { Reveal } from '@/components/nexova/reveal'

export function FinalDeclaration() {
  return (
    <section
      id="presencia"
      className="relative flex min-h-[90vh] w-full items-end overflow-hidden bg-obsidian md:min-h-screen"
    >
      <Image
        src="/nexova/A5_FINAL_DECLARATION.png"
        alt="Dos monolitos ante un eclipse, figura solitaria reflejada en agua oscura"
        fill
        className="object-cover"
        style={{ objectPosition: '50% 35%' }}
        sizes="100vw"
      />
      <div className="absolute inset-0 bg-obsidian/50" />
      <div className="absolute inset-0 bg-gradient-to-t from-obsidian via-obsidian/25 to-transparent" />

      <div className="relative z-10 flex w-full flex-col items-center gap-10 px-6 pb-24 pt-32 text-center md:pb-32">
        <Reveal>
          <span className="font-mono text-[11px] uppercase tracking-[0.3em] text-ash">04 — DECLARACIÓN FINAL</span>
        </Reveal>
        <Reveal delay={180}>
          <h2 className="max-w-4xl font-serif text-[clamp(2.25rem,7.5vw,5.5rem)] leading-[1.05] text-bone">
            LA ESTRUCTURA
            <br />
            NO SUSTITUYE
            <br />
            EL CRITERIO.
            <br />
            LO HACE <span className="text-oxblood">ESCALABLE.</span>
          </h2>
        </Reveal>
        <Reveal delay={360}>
          <a
            id="contacto"
            href="#top"
            className="mt-4 border border-bone/30 px-6 py-3 font-mono text-[11px] uppercase tracking-[0.2em] text-bone transition-colors hover:border-bone hover:bg-bone hover:text-obsidian"
          >
            INICIAR CONVERSACIÓN
          </a>
        </Reveal>
      </div>
    </section>
  )
}
