'use client'

import { useEffect, useRef } from 'react'
import Image from 'next/image'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { cn } from '@/lib/utils'

if (typeof window !== 'undefined') {
  gsap.registerPlugin(ScrollTrigger)
}

export function HeroTransition() {
  const sectionRef = useRef<HTMLDivElement>(null)
  const heroContentRef = useRef<HTMLDivElement>(null)
  const heroImageRef = useRef<HTMLDivElement>(null)
  const materialWrapRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const section = sectionRef.current
    const heroContent = heroContentRef.current
    const heroImage = heroImageRef.current
    const materialWrap = materialWrapRef.current
    if (!section || !heroContent || !heroImage || !materialWrap) return

    const mm = gsap.matchMedia()

    mm.add('(prefers-reduced-motion: no-preference) and (min-width: 900px)', () => {
      gsap.set(materialWrap, { height: '0%', opacity: 1 })
      gsap.set(heroImage, { scale: 1, x: 0, opacity: 1 })
      gsap.set(heroContent, { opacity: 1, y: 0 })

      const tl = gsap.timeline({
        scrollTrigger: {
          trigger: section,
          start: 'top top',
          end: '+=140%',
          scrub: true,
          pin: true,
          anticipatePin: 1,
        },
      })

      tl.to(heroImage, { scale: 1.06, x: 16, duration: 0.32, ease: 'power2.inOut' }, 0.15)
        .to(materialWrap, { height: '100%', duration: 0.34, ease: 'power2.inOut' }, 0.15)
        .to(heroContent, { opacity: 0, y: -56, duration: 0.22, ease: 'power2.in' }, 0.5)
        .to(heroImage, { opacity: 0.12, duration: 0.22, ease: 'power2.in' }, 0.5)
        .to(materialWrap, { opacity: 0, duration: 0.26, ease: 'power1.in' }, 0.74)

      return () => {
        tl.kill()
      }
    })

    return () => mm.revert()
  }, [])

  return (
    <section
      id="top"
      ref={sectionRef}
      className="relative w-full bg-obsidian md:h-screen md:overflow-hidden"
    >
      <div className="absolute inset-0 bg-obsidian" />

      <div
        ref={heroContentRef}
        className="relative z-20 flex flex-col gap-10 px-6 pb-10 pt-32 md:absolute md:inset-0 md:justify-start md:gap-8 md:px-16 md:pb-0 md:pt-[24vh]"
      >
        <div className="flex max-w-xl flex-col gap-7 md:max-w-2xl md:gap-8">
          <div className="flex items-center gap-3 font-mono text-[10px] uppercase tracking-[0.28em] text-ash md:text-[11px]">
            <span className="h-px w-8 bg-oxblood" aria-hidden="true" />
            NEXOVA SOLUTIONS / DESDE 2011
          </div>
          <h1 className="font-serif text-[clamp(2.5rem,11vw,7rem)] leading-[0.96] text-bone">
            CRITERIO HUMANO.
            <br />
            ESTRUCTURADO
            <br />
            PARA LO QUE <span className="text-oxblood">SIGUE.</span>
          </h1>
          <p className="max-w-sm font-sans text-sm leading-relaxed text-ash md:text-base">
            Selección ejecutiva, soporte externalizado y formación corporativa conectados por una
            operación disciplinada.
          </p>
        </div>
      </div>

      <div className="relative z-10 mx-6 mb-16 h-[46vh] overflow-hidden md:hidden">
        <Image
          src="/nexova/A1_HERO_ABYSSAL_PRESENCE.png"
          alt="Presencia abisal — figura envuelta en fibra carmesí ante un umbral de luz"
          fill
          priority
          className="object-cover"
          style={{ objectPosition: '70% 22%' }}
          sizes="100vw"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-obsidian via-transparent to-transparent" />
        <div className="absolute inset-0 bg-gradient-to-b from-obsidian/40 via-transparent to-transparent" />
      </div>

      <div ref={heroImageRef} className="pointer-events-none absolute inset-0 z-0 hidden md:block">
        <Image
          src="/nexova/A1_HERO_ABYSSAL_PRESENCE.png"
          alt="Presencia abisal — figura envuelta en fibra carmesí ante un umbral de luz"
          fill
          priority
          className="object-cover"
          style={{ objectPosition: '70% 40%' }}
          sizes="100vw"
        />
        <div className="absolute inset-0 bg-gradient-to-r from-obsidian via-obsidian/55 to-transparent" />
        <div className="absolute inset-0 bg-gradient-to-b from-obsidian/45 via-transparent to-obsidian/70" />
      </div>

      <div
        ref={materialWrapRef}
        className="pointer-events-none absolute inset-x-0 bottom-0 z-30 hidden overflow-hidden md:block"
        style={{ height: '0%' }}
        aria-hidden="true"
      >
        <div className="absolute inset-x-0 bottom-0" style={{ height: '100vh' }}>
          <Image
            src="/nexova/A2_FIBROUS_CRIMSON_MATERIAL.png"
            alt=""
            fill
            className="object-cover"
          />
          <div className="absolute inset-0 bg-obsidian/25" />
        </div>
      </div>

      <div
        className={cn(
          'pointer-events-none absolute inset-x-0 bottom-10 z-20 hidden justify-center font-mono text-[10px] uppercase tracking-[0.3em] text-ash/70 md:flex',
        )}
        aria-hidden="true"
      >
        DESPLAZAR
      </div>
    </section>
  )
}
