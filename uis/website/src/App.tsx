import { useEffect, useRef, useState } from "react";
import { facts, sectors, services } from "./content";
import heroDesktop from "../../../packages/design-system/assets/a1-hero-golden-desktop.png";
import heroMobile from "../../../packages/design-system/assets/a1-hero-golden-mobile.png";
import fibrousDesktop from "../../../packages/design-system/assets/a2-fibrous-golden-desktop.png";
import fibrousMobile from "../../../packages/design-system/assets/a2-fibrous-golden-mobile.png";


function useHeroManifestoMotion() {
  const storyRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const story = storyRef.current;
    if (!story) return;

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
    if (reduceMotion.matches) return;

    const heroVisual = story.querySelector<HTMLElement>(".hero__visual");
    const heroCopy = story.querySelector<HTMLElement>(".hero__copy");
    const manifestoMaterial = story.querySelector<HTMLElement>(".manifesto__material");
    const manifestoCopy = story.querySelector<HTMLElement>(".manifesto__copy");

    if (!heroVisual || !heroCopy || !manifestoMaterial || !manifestoCopy) return;

    let raf = 0;

    const render = () => {
      raf = 0;
      const rect = story.getBoundingClientRect();
      const travel = Math.max(1, story.offsetHeight - window.innerHeight);
      const progress = Math.min(1, Math.max(0, -rect.top / travel));

      const separate = Math.min(1, progress / 0.42);
      const yieldProgress = Math.min(1, Math.max(0, (progress - 0.22) / 0.48));
      const reveal = Math.min(1, Math.max(0, (progress - 0.38) / 0.5));

      heroVisual.style.transform = `translate3d(${separate * 1.5}%, ${separate * -1.2}%, 0) scale(${1 + separate * 0.035})`;
      heroCopy.style.transform = `translate3d(0, ${yieldProgress * -12}px, 0)`;

      manifestoMaterial.style.transform = `translate3d(${(1 - reveal) * -2.5}%, 0, 0) scale(${1.045 - reveal * 0.045})`;
      manifestoCopy.style.transform = `translate3d(0, ${(1 - reveal) * 22}px, 0)`;
    };

    const requestRender = () => {
      if (!raf) raf = window.requestAnimationFrame(render);
    };

    render();
    window.addEventListener("scroll", requestRender, { passive: true });
    window.addEventListener("resize", requestRender);

    return () => {
      window.removeEventListener("scroll", requestRender);
      window.removeEventListener("resize", requestRender);
      if (raf) window.cancelAnimationFrame(raf);
      [heroVisual, heroCopy, manifestoMaterial, manifestoCopy].forEach((node) => {
        node.style.removeProperty("transform");
      });
    };
  }, []);

  return storyRef;
}

function Header() {
  const [open, setOpen] = useState(false);

  const close = () => setOpen(false);

  return (
    <header className="site-header">
      <div className="site-header__inner">
        <a className="wordmark" href="#top" aria-label="Nexova, inicio">
          NEXOVA
        </a>

        <nav
          id="primary-navigation"
          className={open ? "site-nav is-open" : "site-nav"}
          aria-label="Navegación principal"
        >
          <a onClick={close} href="#servicios">Servicios</a>
          <a onClick={close} href="#evidencia">Experiencia</a>
          <a onClick={close} href="#enfoque">Enfoque</a>
          <a onClick={close} href="#presencia">Presencia</a>
        </nav>

        <div className="site-header__actions">
          <a className="header-contact" href="#contacto">
            Iniciar conversación <span aria-hidden="true">→</span>
          </a>
          <button
            type="button"
            className="menu-toggle"
            aria-expanded={open}
            aria-controls="primary-navigation"
            aria-label={open ? "Cerrar navegación" : "Abrir navegación"}
            onClick={() => setOpen((value) => !value)}
          >
            <span />
            <span />
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
          conectados por una operación disciplinada y una infraestructura más
          inteligente.
        </p>
        <div className="hero__actions">
          <a className="button button--primary" href="#servicios">
            Explorar Nexova <span aria-hidden="true">→</span>
          </a>
          <a className="text-link" href="#enfoque">
            Nuestro enfoque <span aria-hidden="true">→</span>
          </a>
        </div>
      </div>

      <figure className="hero__visual" aria-hidden="true">
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
      <figure className="manifesto__material" aria-hidden="true">
        <picture>
          <source media="(max-width: 720px)" srcSet={fibrousMobile} />
          <img
            src={fibrousDesktop}
            alt=""
            width={650}
            height={620}
            loading="lazy"
            decoding="async"
          />
        </picture>
      </figure>
      <div className="manifesto__copy">
        <p className="eyebrow">01 / Convicción operativa</p>
        <h2 id="manifesto-title" className="display">
          La experiencia es humana. La infraestructura debe ayudarla a avanzar.
        </h2>
        <p>
          Nexova ha pasado más de una década trabajando donde el criterio
          importa. El siguiente paso es conectar los sistemas que rodean ese
          criterio, no reemplazarlo.
        </p>
      </div>
    </section>
  );
}

function Capabilities() {
  return (
    <section className="capabilities" id="servicios" aria-labelledby="capabilities-title">
      <div className="capabilities__intro">
        <p className="eyebrow">02 / Lo que hace Nexova</p>
        <h2 id="capabilities-title" className="display">
          Tres disciplinas.<br />Un mismo estándar operativo.
        </h2>
        <p>
          El negocio actual de Nexova se sostiene en talento, operación de
          servicio y desarrollo de liderazgo.
        </p>
      </div>

      <div className="capabilities__list">
        {services.map((service) => (
          <article className="capability" key={service.index}>
            <p className="capability__index">{service.index}</p>
            <div>
              <h3 className="display">{service.title}</h3>
              <p>{service.text}</p>
            </div>
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
        <h2 id="evidence-title" className="display">
          Experiencia,<br />hecha visible.
        </h2>
      </div>

      <div className="evidence__facts" aria-label="Nexova en cifras">
        {facts.map((fact) => (
          <div className="evidence-fact" key={fact.label}>
            <strong className="display">{fact.value}</strong>
            <span>{fact.label}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

function Philosophy() {
  return (
    <section className="philosophy" aria-labelledby="philosophy-title">
      <figure className="philosophy__material" aria-hidden="true">
        <picture>
          <source media="(max-width: 720px)" srcSet={fibrousMobile} />
          <img
            src={fibrousDesktop}
            alt=""
            width={650}
            height={620}
            loading="lazy"
            decoding="async"
          />
        </picture>
      </figure>

      <div className="philosophy__copy">
        <p className="eyebrow">04 / Filosofía operativa</p>
        <h2 id="philosophy-title" className="display">
          La experiencia humana no debe desaparecer dentro de los sistemas.
        </h2>
        <p>
          La transformación de Nexova consiste en conectar la infraestructura
          alrededor del criterio: hacer que la experiencia sea más fácil de
          consultar, coordinar y convertir en acción.
        </p>
      </div>
    </section>
  );
}

function Presence() {
  return (
    <section className="presence" id="presencia" aria-labelledby="presence-title">
      <div className="presence__title">
        <p className="eyebrow">05 / Presencia</p>
        <h2 id="presence-title" className="display">
          Criterio local.<br />Alcance transfronterizo.
        </h2>
      </div>

      <div className="presence__locations">
        <div>
          <strong className="display">Valencia</strong>
          <span>Sede / España</span>
        </div>
        <div>
          <strong className="display">Miami</strong>
          <span>Oficina de expansión / Florida</span>
        </div>
      </div>

      <div className="presence__sectors">
        <p className="eyebrow eyebrow--gold">Sectores frecuentes</p>
        <ul>
          {sectors.map((sector) => <li className="display" key={sector}>{sector}</li>)}
        </ul>
      </div>
    </section>
  );
}

function Closing() {
  return (
    <section className="closing" id="contacto" aria-labelledby="closing-title">
      <div className="closing__copy">
        <p className="eyebrow">06 / Nexova</p>
        <h2 id="closing-title" className="display">
          Experiencia,<br />conectada.
        </h2>
        <p>
          Una base operativa más disciplinada para talento, servicio y
          desarrollo.
        </p>
        <a className="button button--primary" href="#servicios">
          Explorar servicios <span aria-hidden="true">→</span>
        </a>
      </div>

      <figure className="closing__material" aria-hidden="true">
        <picture>
          <source media="(max-width: 720px)" srcSet={fibrousMobile} />
          <img
            src={fibrousDesktop}
            alt=""
            width={650}
            height={620}
            loading="lazy"
            decoding="async"
          />
        </picture>
      </figure>
    </section>
  );
}

function Footer() {
  return (
    <footer className="site-footer">
      <div>
        <span className="wordmark">NEXOVA</span>
        <p>Selección · Soporte · Formación corporativa</p>
      </div>
      <nav aria-label="Navegación de pie">
        <a href="#servicios">Servicios</a>
        <a href="#presencia">Presencia</a>
        <a href="#contacto">Contacto</a>
      </nav>
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
        <div className="hero-manifesto-story" ref={storyRef}>
          <Hero />
          <Manifesto />
        </div>
        <Capabilities />
        <Evidence />
        <Philosophy />
        <Presence />
        <Closing />
      </main>
      <Footer />
    </div>
  );
}

export { App };
