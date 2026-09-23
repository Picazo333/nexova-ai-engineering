import { useEffect, useRef, useState } from "react";
import { facts, sectors, services } from "./content";
import heroDesktop from "../../../packages/design-system/assets/a1-hero-desktop.png";
import heroMobile from "../../../packages/design-system/assets/a1-hero-mobile.png";
import crimsonFibrous from "../../../packages/design-system/assets/a2-crimson-fibrous.png";

/**
 * Progressive-enhancement scroll reveal for the Hero → Manifesto choreography.
 * - Native scroll only; no pin, scrub, wheel or touch interception.
 * - Hidden pre-states apply only when `html.js` is present AND motion is allowed,
 *   so content is fully legible with JS disabled or reduced-motion on.
 */
function useScrollReveal() {
  const rootRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const root = rootRef.current;
    if (!root) return;
    const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const targets = Array.from(root.querySelectorAll<HTMLElement>("[data-reveal]"));
    if (prefersReduced || !("IntersectionObserver" in window)) {
      targets.forEach((el) => el.classList.add("is-revealed"));
      return;
    }
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-revealed");
            io.unobserve(entry.target);
          }
        });
      },
      { rootMargin: "0px 0px -12% 0px", threshold: 0.15 },
    );
    targets.forEach((el) => io.observe(el));
    return () => io.disconnect();
  }, []);
  return rootRef;
}

function ServiceCard({ index, title, text, meta }: { index: string; title: string; text: string; meta: string }) {
  return <article className="service-card nx-panel">
    <div className="service-card__top"><span className="nx-overline">{index}</span><span aria-hidden="true" className="service-card__mark">知</span></div>
    <h3 className="nx-display">{title}</h3><p>{text}</p><div className="service-card__meta">{meta}</div>
  </article>;
}

function Header() {
  const [open, setOpen] = useState(false);
  return <header className="site-header"><div className="nx-container header-inner">
    <a className="wordmark" href="#top" aria-label="Nexova, inicio">NEXOVA</a>
    <nav id="mobile-navigation" className={open ? "is-open" : ""} aria-label="Navegación principal"><a onClick={() => setOpen(false)} href="#servicios">Servicios</a><a onClick={() => setOpen(false)} href="#enfoque">Enfoque</a><a onClick={() => setOpen(false)} href="#presencia">Presencia</a><a onClick={() => setOpen(false)} href="#contacto">Contacto</a></nav>
    <div className="header-actions"><a className="nx-button nx-button--quiet header-cta" href="#contacto">Hablar con Nexova <span aria-hidden="true">→</span></a><button className="menu-toggle" type="button" aria-expanded={open} aria-controls="mobile-navigation" aria-label={open ? "Cerrar navegación" : "Abrir navegación"} onClick={() => setOpen(v => !v)}><span /><span /></button></div>
  </div></header>;
}

function Hero() {
  return <section className="hero" aria-labelledby="hero-title">
    <div className="hero__art" aria-hidden="true">
      <picture>
        <source media="(max-width: 720px)" srcSet={heroMobile} />
        <img
          src={heroDesktop}
          alt=""
          width={1024}
          height={1024}
          fetchPriority="high"
          decoding="async"
        />
      </picture>
    </div>
    <div className="hero__scrim" aria-hidden="true" />
    <div className="nx-container hero__inner">
      <p className="hero__kicker nx-overline">Personas × criterio × una forma más alta de operar</p>
      <h1 id="hero-title" className="nx-display">La disciplina crea <em>posibilidades.</em></h1>
      <p className="hero__lede">Nexova ayuda a empresas a encontrar, desarrollar y acompañar talento con la experiencia de una firma construida durante más de una década.</p>
      <div className="hero__actions">
        <a className="nx-button nx-button--primary" href="#servicios">Explorar Nexova <span aria-hidden="true">→</span></a>
        <a className="text-link" href="#enfoque">Nuestro enfoque <span aria-hidden="true">↘</span></a>
      </div>
    </div>
    <div className="hero__index nx-container" aria-hidden="true"><span>01</span><span className="hero__index-line" /><span>UN ORDEN MÁS ALTO</span></div>
  </section>;
}

function App() {
  const revealRef = useScrollReveal();
  return <div id="top" className="site-shell" ref={revealRef}>
    <Header />
    <main>
      <Hero />

      <section className="fact-band" aria-label="Nexova en cifras"><div className="nx-container fact-grid">{facts.map(f => <div className="fact" key={f.label}><strong className="nx-display">{f.value}</strong><span>{f.label}</span></div>)}</div></section>

      <section className="section section--services" id="servicios"><div className="nx-container">
        <div className="section-heading"><div><span className="nx-overline">03 líneas de negocio</span><h2 className="nx-display">La experiencia humana sigue siendo el núcleo.</h2></div><p>Selección, formación y soporte diseñados para equipos profesionales con necesidades concretas y expectativas altas.</p></div>
        <div className="services-grid">{services.map(s => <ServiceCard key={s.index} {...s} />)}</div>
      </div></section>

      <section className="philosophy" id="enfoque" aria-labelledby="philosophy-title">
        <figure className="philosophy__material" data-reveal>
          <img src={crimsonFibrous} alt="" width={1024} height={1024} loading="lazy" decoding="async" />
        </figure>
        <div className="philosophy__copy">
          <span className="nx-overline" data-reveal>Una firma construida para evolucionar</span>
          <h2 id="philosophy-title" className="nx-display" data-reveal>Lo que importa no es automatizar más. Es operar <em>mejor.</em></h2>
          <p data-reveal>Nexova nació como una consultora de dos personas y hoy reúne a 120 profesionales en dos países. La siguiente etapa consiste en mantener el criterio humano mientras la infraestructura gana claridad, velocidad y escala.</p>
          <blockquote data-reveal>“La tecnología debe ampliar la intención humana, no reemplazarla.”</blockquote>
          <a className="text-link" href="#contacto" data-reveal>Construir el siguiente capítulo <span aria-hidden="true">→</span></a>
        </div>
      </section>

      <section className="section presence" id="presencia"><div className="nx-container presence-grid">
        <div><span className="nx-overline">Presencia y sectores</span><h2 className="nx-display">Valencia. Miami. Un mismo estándar.</h2><p>Trabajamos con medianas empresas que han decidido externalizar parte o la totalidad de su gestión de talento.</p></div>
        <div className="presence-list"><div><span>01</span><strong>Valencia, España</strong></div><div><span>02</span><strong>Miami, Florida</strong></div>{sectors.map((s, i) => <div key={s}><span>0{i + 3}</span><strong>{s}</strong></div>)}</div>
      </div></section>

      <section className="section final-cta" id="contacto"><div className="nx-container final-cta__inner"><div><span className="nx-overline">La siguiente conversación</span><h2 className="nx-display">Un futuro más significativo empieza con una decisión bien tomada.</h2></div><a className="nx-button nx-button--primary" href="#servicios">Explorar servicios <span aria-hidden="true">→</span></a></div></section>
    </main>
    <footer><div className="nx-container footer-inner"><div><span className="wordmark">NEXOVA</span><p>Talento, formación y soporte para organizaciones que quieren operar a un estándar más alto.</p></div><div className="footer-meta"><span>Documento de escenario · 4Geeks Academy</span><span>Oni Nocturne Oxblood · Visual system v1</span></div></div></footer>
  </div>;
}
export { App };
