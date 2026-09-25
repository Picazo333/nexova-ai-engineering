import Image from 'next/image'
import { Reveal } from '@/components/nexova/reveal'

const evidences = [
  { n: '12', label: 'AÑOS DE OPERACIÓN CONTINUA', copy: 'Selección, soporte y formación bajo un mismo criterio.' },
  { n: '03', label: 'LÍNEAS INTEGRADAS', copy: 'Ejecutiva, externalizada, formativa.' },
  { n: '01', label: 'ARQUITECTURA', copy: 'Un solo marco disciplinado para cada decisión.' },
]

export function EvidenceSection() {
  return (
    <section id="servicios" className="relative bg-obsidian">
      <div className="grid md:min-h-screen md:grid-cols-[1.1fr_1fr]">
        <div className="flex flex-col justify-center gap-12 px-6 py-24 md:gap-14 md:px-16 md:py-32">
          <Reveal className="flex items-center gap-4">
            <span className="font-mono text-[11px] uppercase tracking-[0.3em] text-oxblood">
              03 — EVIDENCIA / PRECISIÓN
            </span>
          </Reveal>
          <Reveal delay={100}>
            <h2 className="font-serif text-[clamp(2.1rem,5.5vw,3.75rem)] leading-[1.05] text-bone">
              LA PRECISIÓN
              <br />
              NO ES DECORACIÓN.
              <br />
              ES <span className="text-oxblood">MÉTODO.</span>
            </h2>
          </Reveal>

          <div className="flex flex-col divide-y divide-ash/15 border-y border-ash/15">
            {evidences.map((item, i) => (
              <Reveal key={item.label} delay={150 + i * 100} className="flex items-baseline gap-6 py-6">
                <span className="font-mono text-4xl text-oxblood md:text-5xl">{item.n}</span>
                <div className="flex flex-col gap-1">
                  <span className="font-mono text-[11px] uppercase tracking-[0.2em] text-bone">{item.label}</span>
                  <span className="font-sans text-sm text-ash">{item.copy}</span>
                </div>
              </Reveal>
            ))}
          </div>
        </div>

        <div className="relative min-h-[55vh] md:min-h-full">
          <Image
            src="/nexova/A4_EVIDENCE_PRECISION.png"
            alt="Formación rocosa fracturada frente a dos monolitos, cifras de coordenadas superpuestas"
            fill
            className="object-cover"
            style={{ objectPosition: '55% 45%' }}
            sizes="(min-width: 768px) 45vw, 100vw"
          />
          <div className="absolute inset-0 bg-obsidian/20" />
          <div className="absolute inset-y-0 left-0 hidden w-24 bg-gradient-to-r from-obsidian to-transparent md:block" />
          <div className="absolute inset-0 bg-gradient-to-t from-obsidian/70 via-transparent to-transparent md:bg-none" />

          <div className="relative z-10 flex h-full flex-col justify-between p-6 font-mono text-[10px] uppercase tracking-[0.25em] text-ash/80 md:p-8">
            <div className="flex flex-col gap-1"><span>OBSERVAR</span><span>ANALIZAR</span></div>
            <div className="flex flex-col items-end gap-1 text-right"><span>CORRELACIONAR</span><span>REVELAR</span></div>
          </div>
        </div>
      </div>
    </section>
  )
}
