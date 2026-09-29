const baselines = [
  { label: "Resolución de soporte", value: "48 h", target: "SLA 24 h", tone: "danger" },
  { label: "Adopción regular de CRM", value: "40%", target: "equipo comercial", tone: "warning" },
  { label: "CVs revisados por proceso", value: "30–80", target: "manual", tone: "info" },
  { label: "Preparación de reporte", value: "4–8 h", target: "por manager / semana", tone: "warning" },
];
const areas = [
  ["Selección", "40 consultores", "Cribado y seguimiento manual"],
  ["Soporte", "30 agentes", "Visibilidad y conocimiento fragmentados"],
  ["Ventas", "18 personas", "Seguimiento y CRM inconsistentes"],
  ["Formación", "12 personas", "Catálogo e inscripción manuales"],
];
function Sidebar(){return <aside className="sidebar"><div className="sidebar__brand"><span className="nx-seal">鬼</span><strong>NEXOVA</strong></div><nav aria-label="Secciones del backoffice">{["Resumen","Operaciones","Selección","Soporte","Ventas","Formación","Reportes"].map((x,i)=><a key={x} href="#overview" className={i===0?"is-active":""}>{x}</a>)}</nav><div className="sidebar__foot"><span>OPERATIONS</span><small>Context baseline</small></div></aside>}
function App(){return <div className="ops-shell"><Sidebar/><main className="workspace" id="overview">
  <header className="workspace-header"><div><span className="nx-overline">Nexova Operations</span><h1 className="nx-display">Contexto operativo</h1></div><div className="header-meta"><span className="status-dot"/>Baseline de empresa · no live data</div></header>
  <section className="notice" aria-label="Nota de procedencia"><strong>Fuente:</strong> briefing de empresa 4Geeks. Esta pantalla convierte hechos del escenario en una superficie operativa demostrativa; no representa telemetría en tiempo real.</section>
  <section className="kpi-grid" aria-label="Indicadores de contexto">{baselines.map((b)=><article className="kpi nx-panel" key={b.label}><div className={`kpi__signal kpi__signal--${b.tone}`}/><span>{b.label}</span><strong className="nx-display">{b.value}</strong><small>{b.target}</small><div className="spark" aria-hidden="true"><i/><i/><i/><i/><i/></div></article>)}</section>
  <section className="ops-grid"><article className="nx-panel ops-panel"><div className="panel-heading"><div><span className="nx-overline">Áreas</span><h2 className="nx-display">Fricción visible</h2></div><span className="nx-tag">4 dominios</span></div><div className="domain-list">{areas.map(([name,team,issue])=><div className="domain-row" key={name}><div><strong>{name}</strong><span>{team}</span></div><p>{issue}</p><span aria-hidden="true">→</span></div>)}</div></article>
  <article className="nx-panel ops-panel ops-panel--visual"><div className="oni-watermark" aria-hidden="true"/><div className="panel-heading"><div><span className="nx-overline">Principio</span><h2 className="nx-display">Misma sombra. Más claridad.</h2></div></div><p>El backoffice hereda la identidad Oni Nocturne Oxblood, pero reduce ornamento y prioriza estructura, legibilidad y decisiones.</p><ul><li>Jerarquía antes que decoración.</li><li>Rojo para señalar, no para rellenar.</li><li>Datos con procedencia explícita.</li></ul></article></section>
  <section className="nx-panel operations-table"><div className="panel-heading"><div><span className="nx-overline">Mapa operativo</span><h2 className="nx-display">Necesidades por área</h2></div><span className="nx-tag">Vista contextual</span></div><div className="table-wrap"><table><thead><tr><th>Área</th><th>Situación</th><th>Necesidad descrita</th><th>Estado</th></tr></thead><tbody>
  <tr><td>Selección</td><td>Cribado y comunicación manual</td><td>Pipeline asistido + visibilidad de candidato</td><td><span className="state state--review">Contexto</span></td></tr>
  <tr><td>Soporte</td><td>48 h de resolución vs SLA de 24 h</td><td>Base de conocimiento + dashboard</td><td><span className="state state--risk">Brecha</span></td></tr>
  <tr><td>Ventas</td><td>CRM actualizado regularmente por 40%</td><td>Pipeline + seguimiento automatizado</td><td><span className="state state--review">Contexto</span></td></tr>
  <tr><td>Dirección</td><td>Datos semanales con retraso</td><td>Vista ejecutiva unificada</td><td><span className="state state--planned">Necesidad</span></td></tr>
  </tbody></table></div></section>
</main></div>}
export { App };
