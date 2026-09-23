import { useEffect, useState } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import heroDesktop from "../../../packages/design-system/assets/a1-hero-desktop.png";
import heroMobile from "../../../packages/design-system/assets/a1-hero-mobile.png";
import crimsonFibrous from "../../../packages/design-system/assets/a2-crimson-fibrous.png";

gsap.registerPlugin(ScrollTrigger);

function useSignatureMotion() {
  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    const context = gsap.context(() => {
      const timeline = gsap.timeline({
        defaults: { ease: "none" },
        scrollTrigger: {
          trigger: ".hero",
          start: "top top",
          end: "bottom+=220 top",
          scrub: 0.6,
          invalidateOnRefresh: true,
        },
      });

      timeline
        .to(".hero-art img", { scale: 1.045, xPercent: -2, duration: 0.55 }, 0)
        .to(".hero-copy", { yPercent: -8, opacity: 0.58, duration: 0.5 }, 0.08)
        .fromTo(
          ".manifesto-material img",
          { scale: 1.08, yPercent: -5 },
          { scale: 1, yPercent: 0, duration: 0.55 },
          0.34,
        )
        .fromTo(
          ".manifesto-copy",
          { y: 54, opacity: 0.28 },
          { y: 0, opacity: 1, duration: 0.5 },
          0.4,
        );
    });

    return () => context.revert();
  }, []);
}

const capabilities = [
  {
    index: "01",
    title: "Executive recruitment",
    body: "Headhunting for mid-management and executive roles.",
  },
  {
    index: "02",
    title: "Outsourced customer support",
    body: "Dedicated support teams built around client operations.",
  },
  {
    index: "03",
    title: "Leadership & soft-skills training",
    body: "Corporate development focused on leadership and human capability.",
  },
];

const evidence = [
  ["2011", "Founded"],
  ["120", "Employees"],
  ["Valencia", "Headquarters"],
  ["Miami", "Expansion office"],
];

function Header() {
  const [open, setOpen] = useState(false);

  return (
    <header className="site-header">
      <div className="header-shell">
        <a className="wordmark" href="#top" aria-label="Nexova home">
          NEXOVA
        </a>

        <nav
          id="site-navigation"
          className={open ? "site-nav is-open" : "site-nav"}
          aria-label="Primary navigation"
        >
          <a href="#about" onClick={() => setOpen(false)}>About</a>
          <a href="#services" onClick={() => setOpen(false)}>Services</a>
          <a href="#presence" onClick={() => setOpen(false)}>Presence</a>
        </nav>

        <div className="header-actions">
          <a className="header-cta" href="#contact">
            Start a conversation <span aria-hidden="true">→</span>
          </a>
          <button
            className="menu-toggle"
            type="button"
            aria-controls="site-navigation"
            aria-expanded={open}
            aria-label={open ? "Close navigation" : "Open navigation"}
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
      <div className="hero-copy">
        <p className="eyebrow">Nexova Solutions / Since 2011</p>
        <h1 id="hero-title" className="display hero-title">
          Human judgment.
          <br />
          Structured for
          <br />
          what&apos;s next.
        </h1>
        <p className="hero-lede">
          Recruitment, outsourced customer support and corporate training —
          connected by disciplined operations and a more intelligent foundation.
        </p>
        <div className="hero-actions">
          <a className="button-outline" href="#services">
            Explore Nexova <span aria-hidden="true">→</span>
          </a>
          <a className="text-action" href="#about">
            Our approach <span aria-hidden="true">→</span>
          </a>
        </div>
      </div>

      <figure className="hero-art" aria-label="Abstract abyssal Nexova artwork">
        <picture>
          <source media="(max-width: 767px)" srcSet={heroMobile} />
          <img
            src={heroDesktop}
            alt=""
            width={1536}
            height={1536}
            fetchPriority="high"
            decoding="async"
          />
        </picture>
        <figcaption className="hero-art-note" aria-hidden="true">
          Technology in service of human intent.
        </figcaption>
      </figure>
    </section>
  );
}

function Manifesto() {
  return (
    <section className="manifesto" id="about" aria-labelledby="manifesto-title">
      <figure className="manifesto-material" aria-hidden="true">
        <img
          src={crimsonFibrous}
          alt=""
          width={1536}
          height={1024}
          loading="lazy"
          decoding="async"
        />
      </figure>

      <div className="manifesto-copy">
        <p className="eyebrow">01 / Operating belief</p>
        <h2 id="manifesto-title" className="display manifesto-title">
          Experience is human. Infrastructure should help it move.
        </h2>
        <p>
          Nexova has spent more than a decade working where judgment matters.
          The next step is connecting the systems around that judgment — not
          replacing it.
        </p>
      </div>
    </section>
  );
}

function Capabilities() {
  return (
    <section className="capabilities section-dark" id="services" aria-labelledby="capabilities-title">
      <div className="capability-intro">
        <p className="eyebrow">02 / What Nexova does</p>
        <h2 id="capabilities-title" className="display section-title">
          Three disciplines.
          <br />
          One operating
          <br />
          standard.
        </h2>
      </div>

      <div className="capability-list">
        {capabilities.map((item) => (
          <article className="capability-item" key={item.index}>
            <p className="capability-index">{item.index}</p>
            <div>
              <h3 className="display">{item.title}</h3>
              <p>{item.body}</p>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

function Evidence() {
  return (
    <section className="evidence section-dark" aria-labelledby="evidence-title">
      <div className="evidence-heading">
        <p className="eyebrow">03 / Established operations</p>
        <h2 id="evidence-title" className="display section-title">
          Experience,
          <br />
          made visible.
        </h2>
      </div>

      <div className="evidence-grid" aria-label="Nexova company facts">
        {evidence.map(([value, label]) => (
          <div className="evidence-item" key={label}>
            <strong className="display">{value}</strong>
            <span>{label}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

function Philosophy() {
  return (
    <section className="philosophy" aria-labelledby="philosophy-title">
      <figure className="philosophy-material" aria-hidden="true">
        <img
          src={crimsonFibrous}
          alt=""
          width={1536}
          height={1024}
          loading="lazy"
          decoding="async"
        />
      </figure>

      <div className="philosophy-copy">
        <p className="eyebrow">04 / Operating philosophy</p>
        <h2 id="philosophy-title" className="display section-title">
          Human expertise
          <br />
          should not disappear
          <br />
          inside systems.
        </h2>
        <p>
          Nexova&apos;s transformation is about connecting the infrastructure
          around judgment — making experience easier to access, coordinate and
          act on.
        </p>
      </div>
    </section>
  );
}

function Presence() {
  return (
    <section className="presence section-dark" id="presence" aria-labelledby="presence-title">
      <div className="presence-heading">
        <p className="eyebrow">05 / Presence</p>
        <h2 id="presence-title" className="display section-title">
          Local judgment.
          <br />
          Cross-border reach.
        </h2>
      </div>

      <div className="presence-locations">
        <div>
          <strong className="display">Valencia</strong>
          <span>Headquarters / Spain</span>
        </div>
        <div>
          <strong className="display">Miami</strong>
          <span>Expansion office / Florida</span>
        </div>
      </div>

      <div className="presence-sectors">
        <p className="eyebrow">Frequent client sectors</p>
        <p className="display">Technology</p>
        <p className="display">Retail</p>
        <p className="display">Financial services</p>
      </div>
    </section>
  );
}

function Closing() {
  return (
    <section className="closing" id="contact" aria-labelledby="closing-title">
      <div className="closing-copy">
        <p className="eyebrow">06 / Nexova</p>
        <h2 id="closing-title" className="display closing-title">
          Experience,
          <br />
          connected.
        </h2>
        <p>
          A more disciplined operating foundation for talent, service and
          development.
        </p>
        <a className="button-outline" href="mailto:hello@nexova.example">
          Start a conversation <span aria-hidden="true">→</span>
        </a>
      </div>

      <figure className="closing-material" aria-hidden="true">
        <img
          src={crimsonFibrous}
          alt=""
          width={1536}
          height={1024}
          loading="lazy"
          decoding="async"
        />
      </figure>
    </section>
  );
}

function Footer() {
  return (
    <footer className="site-footer">
      <div>
        <span className="wordmark">NEXOVA</span>
        <p>Recruitment / Customer Support / Corporate Training</p>
      </div>
      <nav aria-label="Footer navigation">
        <a href="#about">About</a>
        <a href="#services">Services</a>
        <a href="#presence">Presence</a>
        <a href="#contact">Contact</a>
      </nav>
      <p className="footer-meta">Valencia / Miami · Since 2011</p>
    </footer>
  );
}

function App() {
  useSignatureMotion();

  return (
    <div id="top" className="site-shell">
      <Header />
      <main>
        <Hero />
        <Manifesto />
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
