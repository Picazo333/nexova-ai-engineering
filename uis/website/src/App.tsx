import { useEffect, useRef, useState } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { facts, sectors, services } from "./content";
import heroDesktop from "../../../packages/design-system/assets/a1-hero-desktop.png";
import heroMobile from "../../../packages/design-system/assets/a1-hero-mobile.png";
import fibrousDesktop from "../../../packages/design-system/assets/a2-crimson-fibrous.png";
import fibrousMobile from "../../../packages/design-system/assets/a2-crimson-fibrous.png";

function useHeroManifestoMotion() {
  const storyRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const story = storyRef.current;
    if (!story) return;

    const hero = story.querySelector<HTMLElement>(".hero");
    const heroArt = story.querySelector<HTMLElement>(".hero__art");
    const heroFibers = story.querySelector<HTMLElement>(".hero__fibers");
    const heroCopy = story.querySelector<HTMLElement>(".hero__copy");
    const manifesto = story.querySelector<HTMLElement>(".manifesto");
    const manifestoCopy = story.querySelector<HTMLElement>(".manifesto__copy");
    if (!hero || !heroArt || !heroFibers || !heroCopy || !manifesto || !manifestoCopy) return;

    gsap.registerPlugin(ScrollTrigger);
    document.documentElement.dataset.gsap = "active";
    const ctx = gsap.context(() => {
      const mm = gsap.matchMedia();

      mm.add("(min-width: 769px) and (prefers-reduced-motion: no-preference)", () => {
        gsap.set(manifestoCopy, { opacity: 1, y: 24 });

        const tl = gsap.timeline({
          scrollTrigger: {
            trigger: hero,
            start: "top top",
            end: () => "+=" + Math.max(300, Math.round(manifesto.offsetHeight * 1.35)),
            pin: hero,
            pinSpacing: true,
            scrub: 0.72,
            anticipatePin: 1,
            invalidateOnRefresh: true,
          },
        });

        tl
          .to(heroArt, { scale: 1.09, xPercent: 3.2, yPercent: -1.3, duration: 1 }, 0)
          .to(heroFibers, { xPercent: 11, yPercent: -8, scale: 1.16, opacity: 0.68, duration: 1 }, 0)
          .to(heroCopy, { yPercent: -8, opacity: 0.76, duration: 0.82 }, 0.34)
          .to(manifesto, { y: () => -Math.min(250, manifesto.offsetHeight * 0.86), duration: 1 }, 0.42)
          .to(manifestoCopy, { y: 0, duration: 0.74 }, 0.56);

        return () => {
          tl.scrollTrigger?.kill();
          tl.kill();
        };
      });

      mm.add("(max-width: 768px), (prefers-reduced-motion: reduce)", () => {
        gsap.set([hero, heroArt, heroFibers, heroCopy, manifesto, manifestoCopy], { clearProps: "transform,opacity" });
      });

      Promise.all([
        document.fonts?.ready ?? Promise.resolve(),
        ...Array.from(story.querySelectorAll("img")).map((img) => img.decode?.().catch(() => undefined)),
      ]).then(() => ScrollTrigger.refresh());

      return () => mm.revert();
    }, story);

    return () => ctx.revert();
  }, []);

  return storyRef;
}

function Header() {
  const [open, setOpen] = useState(false);
  const close = () => setOpen(false);

  return (
    <header className="site-header">
      <div className="site-header__inner">
        <a className="wordmark" href="#top" aria-label="Nexova, inicio">NEXOVA</a>
        <nav id="primary-navigation" className={open ? "site-nav is-open" : "site-nav"} aria-label="Navegación principal">
          <a onClick={close} href="#servicios">Servicios</a>
          <a onClick={close} href="#evidencia">Experiencia</a>
          <a onClick={close} href="#enfoque">Enfoque</a>
          <a onClick={close} href="#presencia">Presencia</a>
        </nav>
        <div className="site-header__actions">
          <a className="header-contact" href="#contacto">Iniciar conversación <span aria-hidden="true">→</span></a>
          <button type="button" className="menu-toggle" aria-expanded={open} aria-controls="primary-navigation" aria-label={open ? "Cerrar navegación" : "Abrir navegación"} onClick={() => setOpen((value) => !value)}>
            <span /><span />
          </button>
        </div>
      </div>
    </header>
  );
}

function Hero() {
  return (
    <section className="hero" aria-labelledby="hero-title">
      <div className="hero__copy">
        <p className="eyebrow">Nexova Solutions / Desde 2011</p>
        <h1 id="hero-title" className="display display--hero">
          Criterio humano.<br />
          Estructurado para<br />
          lo que sigue.
        </h1>
        <p className="hero__lede">
          Selección ejecutiva, soporte externalizado y formación corporativa,
          conectados por una operación disciplinada y una infraestructura más inteligente.
        </p>
        <div className="hero__actions">
          <a className="button button--primary" href="#servicios">Explorar Nexova <span aria-hidden="true">→</span></a>
          <a className="text-link" href="#enfoque">Nuestro enfoque <span aria-hidden="true">→</span></a>
        </div>
      </div>

      <figure className="hero__visual" aria-hidden="true">
        <picture className="hero__art">
          <source media="(max-width: 720px)" srcSet={heroMobile} />
          <img src={heroDesktop} alt="" width={1024} height={1024} fetchPriority="high" decoding="async" />
        </picture>

        <picture className="hero__fibers">
          <source media="(max-width: 720px)" srcSet={fibrousMobile} />
          <img src={fibrousDesktop} alt="" width={1024} height={1024} decoding="async" />
        </picture>

        <figcaption>
          <span>Tecnología</span>
          <span>al servicio de</span>
          <span>la intención humana.</span>
        </figcaption>
      </figure>
    </section>
  );
}

function Manifesto() {
  return (
    <section className="manifesto" id="enfoque" aria-labelledby="manifesto-title">
      <div className="manifesto__void" aria-hidden="true"><span /></div>
      <div className="manifesto__copy">
        <p className="eyebrow">01 / Convicción operativa</p>
        <h2 id="manifesto-title" className="display">La experiencia es humana. La infraestructura debe ayudarla a avanzar.</h2>
        <p>Nexova ha pasado más de una década trabajando donde el criterio importa. El siguiente paso es conectar los sistemas que rodean ese criterio, no reemplazarlo.</p>
      </div>
    </section>
  );
}

function Capabilities() {
  return (
    <section className="capabilities" id="servicios" aria-labelledby="capabilities-title">
      <div className="capabilities__intro">
        <p className="eyebrow">02 / Lo que hace Nexova</p>
        <h2 id="capabilities-title" className="display">Tres disciplinas.<br />Un mismo estándar operativo.</h2>
        <p>El negocio actual de Nexova se sostiene en talento, operación de servicio y desarrollo de liderazgo.</p>
      </div>
      <div className="capabilities__list">
        {services.map((service) => (
          <article className="capability" key={service.index}>
            <p className="capability__index">{service.index}</p>
            <div><h3 className="display">{service.title}</h3><p>{service.text}</p></div>
          </article>
        ))}
      </div>
    </section>
  );
}

function Evidence() {
  return (
    <section className="evidence" id="evidencia" aria-labelledby="evidence-title">
      <div className="evidence__intro">
        <p className="eyebrow">03 / Operación establecida</p>
        <h2 id="evidence-title" className="display">Experiencia,<br />hecha visible.</h2>
      </div>
      <div className="evidence__facts" aria-label="Nexova en cifras">
        {facts.map((fact) => (
          <div className="evidence-fact" key={fact.label}><strong className="display">{fact.value}</strong><span>{fact.label}</span></div>
        ))}
      </div>
    </section>
  );
}

function Philosophy() {
  return (
    <section className="philosophy" aria-labelledby="philosophy-title">
      <figure className="philosophy__material" aria-hidden="true">
        <span className="philosophy__orb philosophy__orb--bone" />
        <span className="philosophy__orb philosophy__orb--crimson" />
        <span className="philosophy__orb philosophy__orb--ochre" />
      </figure>
      <div className="philosophy__copy">
        <p className="eyebrow">04 / Filosofía operativa</p>
        <h2 id="philosophy-title" className="display">La experiencia humana no debe desaparecer dentro de los sistemas.</h2>
        <p>La transformación de Nexova consiste en conectar la infraestructura alrededor del criterio: hacer que la experiencia sea más fácil de consultar, coordinar y convertir en acción.</p>
      </div>
    </section>
  );
}

function Presence() {
  return (
    <section className="presence" id="presencia" aria-labelledby="presence-title">
      <div className="presence__title">
        <p className="eyebrow">05 / Presencia</p>
        <h2 id="presence-title" className="display">Criterio local.<br />Alcance transfronterizo.</h2>
      </div>
      <div className="presence__locations">
        <div><strong className="display">Valencia</strong><span>Sede / España</span></div>
        <div><strong className="display">Miami</strong><span>Oficina de expansión / Florida</span></div>
      </div>
      <div className="presence__sectors">
        <p className="eyebrow eyebrow--gold">Sectores frecuentes</p>
        <ul>{sectors.map((sector) => <li className="display" key={sector}>{sector}</li>)}</ul>
      </div>
    </section>
  );
}

function Closing() {
  return (
    <section className="closing" id="contacto" aria-labelledby="closing-title">
      <div className="closing__copy">
        <p className="eyebrow">06 / Nexova</p>
        <h2 id="closing-title" className="display">Experiencia,<br />conectada.</h2>
        <p>Una base operativa más disciplinada para talento, servicio y desarrollo.</p>
        <a className="button button--primary" href="#servicios">Explorar servicios <span aria-hidden="true">→</span></a>
      </div>
      <div className="closing__field" aria-hidden="true">
        <span className="closing__field-orb closing__field-orb--one" />
        <span className="closing__field-orb closing__field-orb--two" />
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="site-footer">
      <div><span className="wordmark">NEXOVA</span><p>Selección · Soporte · Formación corporativa</p></div>
      <nav aria-label="Navegación de pie"><a href="#servicios">Servicios</a><a href="#presencia">Presencia</a><a href="#contacto">Contacto</a></nav>
      <p>Valencia / Miami · Desde 2011</p>
    </footer>
  );
}

function App() {
  const storyRef = useHeroManifestoMotion();
  return (
    <div id="top" className="site-shell">
      <Header />
      <main>
        <div className="hero-manifesto-story" ref={storyRef}><Hero /><Manifesto /></div>
        <Capabilities /><Evidence /><Philosophy /><Presence /><Closing />
      </main>
      <Footer />
    </div>
  );
}

export { App };
