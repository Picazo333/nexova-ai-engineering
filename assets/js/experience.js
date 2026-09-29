/* Nexova · capa inmersiva (Storyboard v3) — C8: reproducción a tempo propio.
   El scroll decide QUÉ momento se muestra (persona 1–4, paso 1–4); el reloj decide A QUÉ VELOCIDAD se
   reproduce. Así el volteo, los gestos y la oficina se ven igual scrollee el usuario rápido o lento:
   - Una "posición de línea de tiempo" x avanza hacia el estado pedido por el scroll a ritmo fijo
     (duración nativa de cada tramo), con easing; si el usuario vuelve atrás, x invierte sin saltos.
   - Los gestos (G1–G4) se reproducen a su velocidad nativa al llegar a cada persona, con mezcla de
     fotogramas (sin tirones a 7–9 fps).
   Solo actúa con data-mode="scrolly" (sin prefers-reduced-motion ni Save-Data). Sin JS, el contenido ya es visible. */
(() => {
  'use strict';
  const scenes = document.querySelectorAll('[data-mode="scrolly"]');
  if (!scenes.length) return;

  const W = 1920, H = 1080;
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const snap = (t) => 1 - Math.pow(1 - t, 3);
  const easeIO = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
  const pad = (n) => String(n).padStart(3, '0');
  const loadImg = (src) => new Promise((res) => {
    const i = new Image(); i.decoding = 'async';
    i.onload = () => (i.decode ? i.decode().catch(() => {}) : Promise.resolve()).then(() => res(i));
    i.onerror = () => res(null); i.src = src;
  });
  const toBitmap = (i) => (i && window.createImageBitmap ? createImageBitmap(i).catch(() => i) : Promise.resolve(i));
  const loadSeq = (dir, n) => Promise.all(Array.from({ length: n }, (_, k) => loadImg(`assets/seq/${dir}/${pad(k + 1)}.webp`).then(toBitmap)));

  // Espera intención: carga después de 'load' y del primer gesto de scroll/teclado.
  let armed = false; const waiting = [];
  const arm = () => { if (armed) return; armed = true; waiting.splice(0).forEach((f) => f()); };
  const whenArmed = (f) => (armed ? f() : waiting.push(f));
  const onFirst = () => { ['scroll', 'wheel', 'touchstart', 'keydown'].forEach((e) => removeEventListener(e, onFirst)); arm(); };
  const listen = () => ['scroll', 'wheel', 'touchstart', 'keydown'].forEach((e) => addEventListener(e, onFirst, { passive: true }));
  if (document.readyState === 'complete') listen(); else addEventListener('load', listen, { once: true });
  if (scrollY > 0) addEventListener('load', arm, { once: true });

  /* ---------- Canvas base: cover-fit de una región del fotograma 1920×1080 ---------- */
  class Stage {
    constructor(canvas, box) {
      this.c = canvas; this.box = box; this.ctx = canvas.getContext('2d');
      this.buf = new Map();
      new ResizeObserver(() => { this.resize(); this.onResize && this.onResize(); }).observe(box);
      this.resize();
    }
    resize() {
      const r = this.box.getBoundingClientRect();
      const dpr = Math.min(devicePixelRatio || 1, 2);
      this.cw = Math.max(1, Math.round(r.width * dpr)); this.ch = Math.max(1, Math.round(r.height * dpr));
      this.dpr = dpr;
      if (this.c.width !== this.cw || this.c.height !== this.ch) { this.c.width = this.cw; this.c.height = this.ch; this.buf.clear(); }
    }
    view(region, fx, fy) { // región normalizada del fotograma → vista en px de fotograma
      const Rx = region[0] * W, Ry = region[1] * H, Rw = region[2] * W, Rh = region[3] * H;
      const s = Math.max(this.cw / Rw, this.ch / Rh);
      const vw = this.cw / s, vh = this.ch / s;
      const sx = clamp(fx * W - vw / 2, Rx, Rx + Rw - vw), sy = clamp(fy * H - vh / 2, Ry, Ry + Rh - vh);
      return { s, sx, sy, vw, vh };
    }
    still(img, v, ctx = this.ctx) {
      const kx = (img.naturalWidth || img.width) / W, ky = (img.naturalHeight || img.height) / H;
      ctx.drawImage(img, v.sx * kx, v.sy * ky, v.vw * kx, v.vh * ky, 0, 0, this.cw, this.ch);
    }
    layer(img, r, v, alpha = 1) { // fotograma de secuencia que cubre la región r del fotograma
      const dx = (r[0] * W - v.sx) * v.s, dy = (r[1] * H - v.sy) * v.s;
      this.ctx.globalAlpha = alpha;
      this.ctx.drawImage(img, dx, dy, r[2] * W * v.s, r[3] * H * v.s);
      this.ctx.globalAlpha = 1;
    }
    buffered(key, img, v) { // still pre-renderizado a tamaño de canvas (para el volteo)
      if (!this.buf.has(key)) {
        const b = document.createElement('canvas'); b.width = this.cw; b.height = this.ch;
        this.still(img, v, b.getContext('2d')); this.buf.set(key, b);
      }
      return this.buf.get(key);
    }
  }


  const scroller = (root) => () => {
    const total = root.offsetHeight - innerHeight;
    return total > 0 ? clamp(-root.getBoundingClientRect().top / total) : 0;
  };
  // Estado discreto pedido por el scroll, con histéresis para que no titile en el umbral.
  const stateOf = (p, cuts, prev) => {
    const h = 0.012;
    let s = 0; for (const c of cuts) if (p >= c) s++;
    if (prev != null && s !== prev) { // solo cambia si se cruzó el umbral con margen
      const c = s > prev ? cuts[s - 1] : cuts[prev - 1];
      if (Math.abs(p - c) < h) return prev;
    }
    return s;
  };
  // Seguidor a ritmo fijo: x va hacia el entero `target` a 1/dur(tramo) por ms; varios tramos pendientes → más rápido.
  function follow(sc, dt, durOf) {
    const d = sc.target - sc.x;
    if (Math.abs(d) < 1e-4) { sc.x = sc.target; return false; }
    const segIdx = d > 0 ? Math.floor(sc.x + 1e-6) : Math.ceil(sc.x - 1e-6) - 1;
    const boost = Math.abs(d) > 1.05 ? 1.9 : 1;           // saltar varios estados no debe ser lento
    const back = d < 0 ? 1.35 : 1;                         // volver atrás un poco más ágil
    const step = (dt / durOf(clamp(segIdx, 0, 99))) * boost * back;
    sc.x = d > 0 ? Math.min(sc.target, sc.x + step) : Math.max(sc.target, sc.x - step);
    return true;
  }

  /* ---------- HERO: media cara + volteo cerámico + video real por persona (C9) ----------
     El scroll elige la persona; cada una tiene su <video> (24 fps reales) que se reproduce una vez, a su
     velocidad, al llegar. Entre personas, el volteo cerámico en canvas (duración fija) parte del fotograma
     exacto en el que estaba el video y llega al primer fotograma del siguiente (= su still). */
  function hero(root) {
    const box = root.querySelector('[data-media]'), canvas = root.querySelector('[data-canvas]');
    const lg = matchMedia('(min-width: 1024px)');
    const st = new Stage(canvas, box);
    const progress = scroller(root);
    const stills = [null, null, null, null];
    const FACE = [0.55, 0, 0.45, 1], FULL = [0, 0, 1, 1];
    const CUTS = [0.1975, 0.4875, 0.7725];   // umbrales de persona
    const FLIP_MS = 1150;                    // volteo cerámico a duración fija
    const sc = { id: 'hero', x: 0, target: 0, state: 0, arrived: -1, snap: null, shown: -1 };
    let ready = false;

    const v = () => (lg.matches ? st.view(FULL, 0.85, 0.37) : st.view(FACE, 0.8, 0.37));
    const region = () => (lg.matches ? FULL : FACE);
    const probe = document.createElement('video');
    const EXT = probe.canPlayType('video/webm; codecs="vp9"') ? 'webm' : 'mp4'; // VP9 (más ligero) o H.264 (Safari)
    const srcFor = (n) => `assets/video/g${n + 1}-${lg.matches ? '720' : 'm'}.${EXT}`;

    // Cuatro <video> apilados sobre el canvas (bajo el degradado del copy); sin src hasta la intención.
    const V = [0, 1, 2, 3].map((n) => {
      const el = document.createElement('video');
      el.muted = true; el.defaultMuted = true; el.playsInline = true; el.preload = 'none';
      el.setAttribute('muted', ''); el.setAttribute('playsinline', ''); el.setAttribute('aria-hidden', 'true');
      el.disablePictureInPicture = true; el.tabIndex = -1;
      Object.assign(el.style, { position: 'absolute', left: '0', top: '0', maxWidth: 'none', opacity: '0', pointerEvents: 'none' });
      return { el, n, src: '' };
    });
    for (let k = 3; k >= 0; k--) canvas.insertAdjacentElement('afterend', V[k].el);

    function place() { // mismo encuadre que el canvas: la región del fotograma que cubre el video, en px CSS
      const view = v(), r = region(), k = view.s / st.dpr;
      for (const x of V) Object.assign(x.el.style, {
        left: `${(r[0] * W - view.sx) * k}px`, top: `${(r[1] * H - view.sy) * k}px`,
        width: `${r[2] * W * k}px`, height: `${r[3] * H * k}px`,
      });
    }
    function ensure(n) { // asigna el archivo (desktop 1280×720 o móvil 4:5) la primera vez que hace falta
      const x = V[n]; if (!x || x.src === srcFor(n)) return x;
      x.src = srcFor(n); x.el.src = x.src; x.el.preload = 'auto'; x.el.load(); return x;
    }
    function show(n) { sc.shown = n; V.forEach((x, k) => { x.el.style.opacity = k === n ? '1' : '0'; }); }
    function snapshot(n) { // fotograma actual del video → búfer del tamaño del canvas
      const el = V[n].el; if (el.readyState < 2 || !el.videoWidth) return null;
      const view = v(), r = region(), b = document.createElement('canvas');
      b.width = st.cw; b.height = st.ch;
      const kx = el.videoWidth / (r[2] * W), ky = el.videoHeight / (r[3] * H);
      b.getContext('2d').drawImage(el, (view.sx - r[0] * W) * kx, (view.sy - r[1] * H) * ky, view.vw * kx, view.vh * ky, 0, 0, st.cw, st.ch);
      return { i: n, buf: b };
    }
    const bufFor = (k, view) => (sc.snap && sc.snap.i === k ? sc.snap.buf : st.buffered(k, stills[k], view));

    function flip(fp, A, B) {
      const ctx = st.ctx, cw = st.cw, ch = st.ch;
      const cols = lg.matches ? 12 : 6, rows = Math.max(4, Math.round(cols * ch / cw));
      const tw = cw / cols, th = ch / rows, D = cols + rows - 2, k = 0.055, j3 = 3 * st.dpr;
      const base = fp < 0.5 ? A : B;
      ctx.drawImage(base, 0, 0);
      ctx.fillStyle = '#F3E9DB'; ctx.strokeStyle = '#F3E9DB'; ctx.lineWidth = j3;
      const joints = new Path2D();
      for (let i = 0; i < cols; i++) for (let j = 0; j < rows; j++) {
        const d = (cols - 1 - i) + j; // ola diagonal: arriba-derecha → abajo-izquierda
        const lp = clamp(fp * (1 + D * k) - d * k);
        const src = lp < 0.5 ? A : B;
        const settled = lp <= 0 || lp >= 1;
        if (settled && src === base) continue;
        const x = Math.round(i * tw), y = Math.round(j * th), w = Math.round((i + 1) * tw) - x, h = Math.round((j + 1) * th) - y;
        if (settled) { ctx.drawImage(src, x, y, w, h, x, y, w, h); continue; }
        const sx = Math.abs(Math.cos(lp * Math.PI)), dw = Math.max(1, w * sx), dx = x + (w - dw) / 2;
        ctx.fillRect(x, y, w, h);
        ctx.drawImage(src, x, y, w, h, dx, y, dw, h);
        ctx.globalAlpha = 0.18 * (1 - sx); ctx.fillStyle = '#FFFDF9'; ctx.fillRect(dx, y, dw, h); // brillo de esmalte
        ctx.globalAlpha = 1; ctx.fillStyle = '#F3E9DB';
        joints.rect(dx, y, dw, h);
      }
      ctx.stroke(joints);
    }

    function render() {
      if (!root.dataset.mode) { delete root.dataset.active; return; } // fallo de stills: el hero queda en modo estático
      const i = Math.floor(sc.x + 1e-6), f = sc.x - i;
      root.dataset.active = 'p' + (Math.min(3, f < 0.5 ? i : i + 1) + 1); // el texto cambia a mitad del volteo
      if (!ready) return;
      const view = v();
      if (f > 1e-4) flip(easeIO(f), bufFor(i, view), bufFor(i + 1, view));
      else st.ctx.drawImage(bufFor(i, view), 0, 0);
    }

    function leave() { // el usuario pide otra persona: congela el fotograma actual y pausa
      const n = sc.shown;
      if (n >= 0) { sc.snap = snapshot(n) || sc.snap; V[n].el.pause(); }
      show(-1); sc.arrived = -1;
    }
    function arrive(n) { // llegó: su video, desde el principio y a velocidad real
      sc.arrived = n; sc.snap = null; render();
      const x = ensure(n); ensure(n + 1);                     // precarga la siguiente persona
      const el = x.el;
      const reveal = () => { if (sc.arrived === n && Math.abs(sc.x - n) < 1e-4) show(n); };
      try { el.currentTime = 0; } catch (e) { /* aún sin metadatos */ }
      el.addEventListener('playing', reveal, { once: true });
      const pr = el.play(); if (pr && pr.catch) pr.catch(() => {});   // si el navegador lo bloquea, queda el still
    }

    function tick(now, dt) {
      sc.state = stateOf(progress(), CUTS, sc.state);
      if (sc.state !== sc.target || Math.abs(sc.x - sc.target) > 1e-4) {
        if (sc.arrived >= 0 && sc.state !== sc.arrived) leave();
        sc.target = sc.state;
      }
      const busy = follow(sc, dt, () => FLIP_MS);
      render();
      if (!busy && ready && sc.arrived !== sc.x && sc.x === sc.target) arrive(sc.x);
      return busy;
    }

    st.onResize = () => { place(); render(); };
    lg.addEventListener('change', () => { V.forEach((x) => { if (x.src) { x.src = ''; x.el.removeAttribute('src'); x.el.load(); } }); show(-1); sc.arrived = -1; sc.snap = null; place(); kick(); });
    whenArmed(async () => {
      const imgs = await Promise.all([1, 2, 3, 4].map((n) => loadImg(`assets/img/hero-p${n}-1440.webp`)));
      if (imgs.some((x) => !x)) { delete root.dataset.mode; delete root.dataset.active; return; }
      imgs.forEach((x, n) => { stills[n] = x; });
      ready = true; canvas.hidden = false; place(); render(); kick();
    });
    sc.state = stateOf(progress(), CUTS, null); sc.x = sc.target = sc.state;
    render();
    return Object.assign(sc, { tick, selector: '[data-hero]', canvas: '[data-hero] [data-canvas]', beats: 4, progress, cuts: CUTS });
  }

  /* ---------- OFICINA PANAL ---------- */
  function office(root) {
    const box = root.querySelector('[data-media]'), canvas = root.querySelector('[data-canvas]');
    const st = new Stage(canvas, box);
    const progress = scroller(root);
    const R = [0, 0, 1, 1];
    const S = { o1: null, o2: null, o3: null };
    const Q = { o1: { dir: 'o1', n: 24 }, o2: { dir: 'o2', n: 48 } };
    const CUTS = [0.2, 0.5, 0.75];
    const SEG_MS = [2400, 2800, 2800];     // paso 1→2 (armado + panal), 2→3, 3→4: duración propia
    const sc = { id: 'office', x: 0, target: 0, state: 0 };
    let ready = false;
    const cells = [];
    for (let q = -2; q <= 2; q++) for (let r = -2; r <= 2; r++) {
      const s = -q - r; if (Math.abs(s) > 2) continue;
      cells.push({ q, r, ring: Math.max(Math.abs(q), Math.abs(r), Math.abs(s)), rot: ((q * 7 + r * 13) % 9 - 4) * 0.05 });
    }

    function hexes(u, alpha, view) { // u: 0 = explotado, 1 = encajado (3 pasos secos)
      const ctx = st.ctx, s = view.s, size = 118 * s, sq = 0.6;
      const cx = (0.5 * W - view.sx) * s, cy = (0.5 * H - view.sy) * s;
      ctx.save(); ctx.globalAlpha = alpha; ctx.strokeStyle = '#FAF5EC'; ctx.lineWidth = 2 * st.dpr;
      for (const c of cells) {
        const t = snap(clamp(u * 3 - c.ring)), k = 1 + (1 - t) * (0.9 + c.ring * 0.25), lift = (1 - t) * c.ring * 26 * s;
        const x = cx + size * 1.5 * c.q * k, y = cy + size * Math.sqrt(3) * (c.r + c.q / 2) * sq * k - lift;
        const a0 = c.rot * (1 - t);
        ctx.beginPath();
        for (let m = 0; m < 6; m++) {
          const ang = a0 + (Math.PI / 3) * m;
          const px = x + size * 0.92 * Math.cos(ang), py = y + size * 0.92 * Math.sin(ang) * sq;
          m ? ctx.lineTo(px, py) : ctx.moveTo(px, py);
        }
        ctx.closePath(); ctx.stroke();
      }
      ctx.restore();
    }


    function frame(seq, u, fallback, view) { // con mezcla entre fotogramas vecinos
      if (!seq.frames) return st.still(fallback, view);
      const pos = clamp(u) * (seq.n - 1), k = Math.floor(pos), a = pos - k;
      st.still(seq.frames[k], view);
      if (a > 0.02 && k + 1 < seq.n) { st.ctx.globalAlpha = a; st.still(seq.frames[k + 1], view); st.ctx.globalAlpha = 1; }
    }

    function render() {
      const i = Math.min(2, Math.floor(sc.x + 1e-6)), f = clamp(sc.x - i), s = sc.x >= 3 ? 1 : f;
      root.dataset.step = String(Math.min(4, Math.round(sc.x) + 1));
      if (!ready) return;
      const view = st.view(R, 0.5, 0.5);
      if (sc.x <= 1e-4) { frame(Q.o1, 0, S.o1, view); hexes(0, 1, view); return; }
      const e = easeIO(s);
      if (i === 0) { frame(Q.o1, e, e < 0.5 ? S.o1 : S.o2, view); hexes(clamp(e / 0.85), e < 0.85 ? 1 : 1 - (e - 0.85) / 0.15, view); }
      else if (i === 1) frame(Q.o2, e * 0.5, S.o2, view);
      else {
        frame(Q.o2, 0.5 + e * 0.5, S.o2, view);
        if (e > 0.92 && S.o3) { st.ctx.globalAlpha = (e - 0.92) / 0.08; st.still(S.o3, view); st.ctx.globalAlpha = 1; }
      }
    }

    function tick(now, dt) {
      sc.state = stateOf(progress(), CUTS, sc.state);
      sc.target = sc.state;
      const busy = follow(sc, dt, (k) => SEG_MS[Math.min(2, k)]);
      render();
      return busy;
    }

    st.onResize = () => render();
    let started = false;
    const start = () => whenArmed(async () => {
      if (started) return; started = true;
      const [a, b, c] = await Promise.all(['o1', 'o2', 'o3'].map((k) => loadImg(`assets/img/office-${k}-1280.webp`)));
      if (!a || !b || !c) { delete root.dataset.mode; delete root.dataset.step; return; }
      Object.assign(S, { o1: a, o2: b, o3: c }); ready = true; canvas.hidden = false; render();
      for (const k of ['o1', 'o2']) { const fr = await loadSeq(Q[k].dir, Q[k].n); if (fr.every(Boolean)) { Q[k].frames = fr; render(); } }
    });
    new IntersectionObserver((es, io) => { if (es.some((e) => e.isIntersecting)) { io.disconnect(); start(); } }, { rootMargin: '100% 0px' }).observe(root);
    sc.state = stateOf(progress(), CUTS, null); sc.x = sc.target = sc.state;
    return Object.assign(sc, { tick, selector: '[data-office]', canvas: '[data-office] [data-canvas]', beats: 4, progress, cuts: CUTS });
  }

  /* ---------- Bucle: corre mientras haya algo reproduciéndose ---------- */
  const SC = [];
  scenes.forEach((el) => {
    const s = el.hasAttribute('data-hero') ? hero(el) : el.hasAttribute('data-office') ? office(el) : null;
    if (s) SC.push(s);
  });
  let raf = 0, prev = 0;
  const loop = (now) => {
    raf = 0;
    const dt = prev ? Math.min(50, now - prev) : 16.7; prev = now;
    let busy = false;
    for (const s of SC) busy = s.tick(now, dt) || busy;
    if (busy) raf = requestAnimationFrame(loop); else prev = 0;
  };
  function kick() { if (!raf) raf = requestAnimationFrame(loop); }
  addEventListener('scroll', kick, { passive: true });
  addEventListener('resize', kick, { passive: true });

  if (/[?&]debug=scroll\b/.test(location.search)) { // hook de depuración: modo "triggered" (tempo propio)
    window.__scrollFeel = {
      version: 1, mode: 'triggered',
      scenes: SC.map((s) => ({
        id: s.id, selector: s.selector, canvas: s.canvas, beats: s.beats, cuts: s.cuts,
        get target() { return s.progress(); }, get state() { return s.state; }, get timeline() { return s.x; },
      })),
    };
  }
})();
