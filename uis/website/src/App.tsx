import { useState } from "react";
import { facts, sectors, services } from "./content";

function ServiceCard({index,title,text,meta}:{index:string;title:string;text:string;meta:string}) {
  return <article className="service-card nx-panel">
    <div className="service-card__top"><span className="nx-overline">{index}</span><span aria-hidden="true" className="service-card__mark">知</span></div>
    <h3 className="nx-display">{title}</h3><p>{text}</p><div className="service-card__meta">{meta}</div>
  </article>;
}
function Header(){
  const [open,setOpen]=useState(false);
  return <header className="site-header"><div className="nx-container header-inner">
    <a className="wordmark" href="#top" aria-label="Nexova, inicio">NEXOVA</a>
    <nav id="mobile-navigation" className={open ? "is-open" : ""} aria-label="Navegación principal"><a onClick={()=>setOpen(false)} href="#servicios">Servicios</a><a onClick={()=>setOpen(false)} href="#enfoque">Enfoque</a><a onClick={()=>setOpen(false)} href="#presencia">Presencia</a><a onClick={()=>setOpen(false)} href="#contacto">Contacto</a></nav>
    <div className="header-actions"><a className="nx-button nx-button--quiet header-cta" href="#contacto">Hablar con Nexova <span aria-hidden="true">→</span></a><button className="menu-toggle" type="button" aria-expanded={open} aria-controls="mobile-navigation" aria-label={open?"Cerrar navegación":"Abrir navegación"} onClick={()=>setOpen(v=>!v)}><span/><span/></button></div>
  </div></header>
}
function App(){return <div id="top" className="site-shell">
  <Header/>
  <main>
    <section className="hero" aria-labelledby="hero-title"><div className="hero-art" aria-hidden="true"/><div className="hero-vignette" aria-hidden="true"/>
      <div className="nx-container hero-grid"><div className="hero-copy">
        <div className="hero-kicker"><span className="nx-overline">Personas × inteligencia × una forma más alta de operar</span><span className="nx-seal" aria-hidden="true">無</span></div>
        <h1 id="hero-title" className="nx-display">La disciplina crea <em>posibilidades.</em></h1>
        <p>Nexova ayuda a empresas a encontrar, desarrollar y acompañar talento con la experiencia de una firma construida durante más de una década.</p>
        <div className="hero-actions"><a className="nx-button nx-button--primary" href="#servicios">Explorar Nexova <span aria-hidden="true">→</span></a><a className="text-link" href="#enfoque">Nuestro enfoque <span aria-hidden="true">↘</span></a></div>
      </div><div className="hero-side"><span className="hero-side__jp" aria-hidden="true">闇 が 意 志 を 鍛 え る</span><p>Tradición, criterio y sistemas para un futuro más claro.</p></div></div>
      <div className="hero-index nx-container" aria-hidden="true"><span>01</span><span className="hero-index__line"/><span>UN ORDEN MÁS ALTO</span></div>
    </section>

    <section className="fact-band" aria-label="Nexova en cifras"><div className="nx-container fact-grid">{facts.map(f=><div className="fact" key={f.label}><strong className="nx-display">{f.value}</strong><span>{f.label}</span></div>)}</div></section>

    <section className="section section--services" id="servicios"><div className="nx-container">
      <div className="section-heading"><div><span className="nx-overline">03 líneas de negocio</span><h2 className="nx-display">La experiencia humana sigue siendo el núcleo.</h2></div><p>Selección, formación y soporte diseñados para equipos profesionales con necesidades concretas y expectativas altas.</p></div>
      <div className="services-grid">{services.map(s=><ServiceCard key={s.index} {...s}/>)}</div>
    </div></section>

    <section className="section section--belief" id="enfoque"><div className="nx-container belief-grid">
      <div className="belief-art" role="img" aria-label="Paisaje japonés oscuro con torii bajo una luna roja"/>
      <div className="belief-copy"><span className="nx-overline">Una firma construida para evolucionar</span><h2 className="nx-display">Lo que importa no es automatizar más. Es operar <em>mejor.</em></h2>
      <p>Nexova nació como una consultora de dos personas y hoy reúne a 120 profesionales en dos países. La siguiente etapa consiste en mantener el criterio humano mientras la infraestructura gana claridad, velocidad y escala.</p>
      <blockquote>“La tecnología debe ampliar la intención humana, no reemplazarla.”</blockquote>
      <a className="text-link" href="#contacto">Construir el siguiente capítulo <span aria-hidden="true">→</span></a></div>
    </div></section>

    <section className="section presence" id="presencia"><div className="nx-container presence-grid">
      <div><span className="nx-overline">Presencia y sectores</span><h2 className="nx-display">Valencia. Miami. Un mismo estándar.</h2><p>Trabajamos con medianas empresas que han decidido externalizar parte o la totalidad de su gestión de talento.</p></div>
      <div className="presence-list"><div><span>01</span><strong>Valencia, España</strong></div><div><span>02</span><strong>Miami, Florida</strong></div>{sectors.map((s,i)=><div key={s}><span>0{i+3}</span><strong>{s}</strong></div>)}</div>
    </div></section>

    <section className="section final-cta" id="contacto"><div className="nx-container final-cta__inner"><div><span className="nx-overline">La siguiente conversación</span><h2 className="nx-display">Un futuro más significativo empieza con una decisión bien tomada.</h2></div><a className="nx-button nx-button--primary" href="#servicios">Explorar servicios <span aria-hidden="true">→</span></a></div></section>
  </main>
  <footer><div className="nx-container footer-inner"><div><span className="wordmark">NEXOVA</span><p>Talento, formación y soporte para organizaciones que quieren operar a un estándar más alto.</p></div><div className="footer-meta"><span>Documento de escenario · 4Geeks Academy</span><span>Oni Nocturne Oxblood · Visual system v1</span></div></div></footer>
</div>}
export { App };
