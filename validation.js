// validation.js — formulario de solicitud de Nexova Solutions (vanilla, sin dependencias).
// Contrato: id = name, error en #{name}-error, JS solo cambia atributos (hidden, aria-invalid,
// data-state, disabled) y textos. Sin envío real: el éxito es simulado y no hay peticiones de red.
(() => {
  'use strict';
  const form = document.querySelector('form[data-validate]');
  if (!form) return;

  // 1. CONFIGURACIÓN ------------------------------------------------------------
  const M = {
    nombre: 'Escribe tu nombre y al menos un apellido.',
    email: 'Escribe un email válido, por ejemplo nombre@empresa.com.',
    telefono: 'Escribe un teléfono válido con prefijo, por ejemplo +34 600 000 000.',
    pais: 'Selecciona tu país.',
    empresa: 'Escribe el nombre de tu empresa.',
    cargo: 'Escribe tu cargo en la empresa.',
    sector: 'Selecciona el sector de tu empresa.',
    servicios: 'Marca al menos un servicio.',
    nivelPuesto: 'Indica el nivel de los puestos que quieres cubrir.',
    numPosiciones: 'Indica cuántas posiciones, entre 1 y 99.',
    canales: 'Marca al menos un canal de atención.',
    temas: 'Marca al menos un tema de formación.',
    formato: 'Elige un formato o marca que aún no lo sabes.',
    participantes: 'Indica un número de personas entre 1 y 500.',
    necesidadMin: 'Describe tu necesidad en al menos 20 caracteres.',
    necesidadMax: 'Máximo 1000 caracteres.',
    privacidad: 'Necesitamos tu consentimiento para tramitar la solicitud.',
    summary: (n) => (n === 1 ? 'Revisa 1 campo antes de enviar.' : `Revisa ${n} campos antes de enviar.`),
    success: (nombre, servicios) => `Gracias, ${nombre}. Hemos registrado tu interés en ${servicios}. Esto es una demostración: no se ha enviado ningún dato.`,
  };
  const SERVICE_NAMES = { seleccion: 'selección de mandos medios y directivos', soporte: 'soporte al cliente externalizado', formacion: 'formación corporativa' };
  const NAME_RE = /^[\p{L}][\p{L}'’\- ]*$/u;
  const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  const TEL_RE = /^\+?[0-9 ]{9,17}$/;
  const intIn = (v, a, b) => /^\d+$/.test(v) && +v >= a && +v <= b;
  const len = (v, a, b) => v.length >= a && v.length <= b;

  const RULES = {
    nombre: (v) => (len(v, 2, 80) && NAME_RE.test(v) && v.split(/\s+/).filter(Boolean).length >= 2 ? '' : M.nombre),
    email: (v) => (EMAIL_RE.test(v) ? '' : M.email),
    telefono: (v) => (!v || (TEL_RE.test(v) && len(v.replace(/\D/g, ''), 9, 15)) ? '' : M.telefono),
    pais: (v) => (v ? '' : M.pais),
    empresa: (v) => (len(v, 2, 100) ? '' : M.empresa),
    cargo: (v) => (len(v, 2, 80) ? '' : M.cargo),
    sector: (v) => (v ? '' : M.sector),
    servicios: (v) => (v.length ? '' : M.servicios),
    nivelPuesto: (v) => (v ? '' : M.nivelPuesto),
    numPosiciones: (v) => (intIn(v, 1, 99) ? '' : M.numPosiciones),
    canales: (v) => (v.length ? '' : M.canales),
    temas: (v) => (v.length ? '' : M.temas),
    formato: (v) => (v ? '' : M.formato),
    participantes: (v) => (intIn(v, 1, 500) ? '' : M.participantes),
    necesidad: (v) => (v.length < 20 ? M.necesidadMin : v.length > 1000 ? M.necesidadMax : ''),
    privacidad: (v) => (v ? '' : M.privacidad),
  };
  const GROUPS = ['servicios', 'canales', 'temas'];

  // 2. AYUDAS PURAS ----------------------------------------------------------------
  const boxes = (name) => [...form.querySelectorAll(`input[type="checkbox"][name="${name}"]`)];
  const control = (name) => (GROUPS.includes(name) ? document.getElementById(name) : form.elements[name]);
  const valueOf = (name) => {
    if (GROUPS.includes(name)) return boxes(name).filter((b) => b.checked).map((b) => b.value);
    const el = form.elements[name];
    if (el.type === 'checkbox') return el.checked;
    return el.value.trim();
  };
  const isActive = (name) => { const c = control(name); return c && !c.disabled && !c.closest('fieldset[disabled]'); };
  const firstError = (name) => (isActive(name) ? RULES[name](valueOf(name)) : '');
  const focusTarget = (name) => (GROUPS.includes(name) ? boxes(name)[0] : form.elements[name]);

  // 3. ESTADO DEL DOM ----------------------------------------------------------------
  const errorEl = (name) => document.getElementById(`${name}-error`);
  function setFieldState(name, message) {
    const c = control(name), e = errorEl(name);
    if (!c || !e) return;
    const targets = GROUPS.includes(name) ? boxes(name) : [c];
    if (message) {
      targets.forEach((t) => t.setAttribute('aria-invalid', 'true'));
      e.querySelector('[data-msg]').textContent = `Error: ${message}`;
      e.hidden = false;
    } else {
      targets.forEach((t) => t.removeAttribute('aria-invalid'));
      e.hidden = true;
      e.querySelector('[data-msg]').textContent = '';
    }
  }
  const validateField = (name) => { const m = firstError(name); setFieldState(name, m); return !m; };
  const validateForm = () => Object.keys(RULES).filter((n) => !validateField(n));

  // Sub-bloques condicionales por servicio
  function syncSubs() {
    const chosen = valueOf('servicios');
    form.querySelectorAll('fieldset[data-sub]').forEach((fs) => {
      const on = chosen.includes(fs.dataset.sub);
      fs.disabled = !on; fs.hidden = !on;
      if (!on) Object.keys(RULES).forEach((n) => { const c = control(n); if (c && fs.contains(c)) setFieldState(n, ''); });
    });
  }

  // Contador de caracteres
  const counter = document.getElementById('necesidad-counter');
  const updateCounter = () => { counter.textContent = `${form.elements.necesidad.value.trim().length} / 1000 caracteres`; };

  // 4. ESTADO Y ÉXITO -----------------------------------------------------------------
  const status = document.getElementById('form-status');
  const success = document.getElementById('form-success');
  function setStatus(state, invalid = []) {
    status.dataset.state = state; form.dataset.state = state;
    status.textContent = '';
    if (state !== 'error') return;
    const title = document.createElement('p');
    title.className = 'font-semibold text-error';
    title.textContent = M.summary(invalid.length);
    const list = document.createElement('ul');
    list.className = 'mt-3 flex flex-col gap-1 list-disc pl-5';
    invalid.forEach((n) => {
      const li = document.createElement('li'); const a = document.createElement('a');
      a.href = `#${focusTarget(n).id}`; a.className = 'text-error underline underline-offset-4';
      a.textContent = errorEl(n).querySelector('[data-msg]').textContent.replace(/^Error: /, '');
      a.addEventListener('click', (ev) => { ev.preventDefault(); focusTarget(n).focus(); });
      li.append(a); list.append(li);
    });
    status.append(title, list);
  }
  function clearAll() {
    Object.keys(RULES).forEach((n) => setFieldState(n, ''));
    form.querySelectorAll('[data-touched]').forEach((el) => el.removeAttribute('data-touched'));
    setStatus('idle');
  }

  // 5. EVENTOS --------------------------------------------------------------------------
  const nameOf = (el) => (el && el.name && RULES[el.name] ? el.name : null);
  form.addEventListener('blur', (ev) => {
    const n = nameOf(ev.target); if (!n) return;
    const c = control(n); c.setAttribute('data-touched', '');
    if (GROUPS.includes(n) && c.contains(document.activeElement)) return;
    validateField(n);
  }, true);
  form.addEventListener('input', (ev) => {
    const n = nameOf(ev.target); if (!n) return;
    if (n === 'necesidad') updateCounter();
    const c = control(n);
    if (c.hasAttribute('data-touched') || focusTarget(n).getAttribute('aria-invalid') === 'true') validateField(n);
  });
  form.addEventListener('change', (ev) => {
    const n = nameOf(ev.target); if (!n) return;
    if (n === 'servicios') syncSubs();
    control(n).setAttribute('data-touched', '');
    validateField(n);
  });
  form.addEventListener('submit', (ev) => {
    ev.preventDefault();
    const invalid = validateForm();
    if (invalid.length) { setStatus('error', invalid); focusTarget(invalid[0]).focus(); return; }
    const chosen = valueOf('servicios').map((v) => SERVICE_NAMES[v]);
    const list = chosen.length > 1 ? `${chosen.slice(0, -1).join(', ')} y ${chosen[chosen.length - 1]}` : chosen[0];
    const nombre = valueOf('nombre').split(/\s+/)[0];
    document.getElementById('form-success-body').textContent = M.success(nombre, list);
    setStatus('success');
    form.hidden = true; success.hidden = false; success.focus();
  });
  form.addEventListener('reset', () => {
    requestAnimationFrame(() => { clearAll(); syncSubs(); updateCounter(); focusTarget('nombre').focus(); });
  });
  document.getElementById('form-new').addEventListener('click', () => {
    success.hidden = true; form.hidden = false; form.reset();
  });

  // Deep link ?tipo=seleccion|soporte|formacion
  const tipo = new URLSearchParams(location.search).get('tipo');
  const box = tipo && document.getElementById(`servicios-${tipo}`);
  if (box) box.checked = true;
  syncSubs(); updateCounter();
})();
