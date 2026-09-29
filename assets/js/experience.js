/* Nexova · capa inmersiva (Storyboard v3). Vanilla, sin dependencias.
   Solo actúa en secciones con data-mode="scrolly" (lo pone un script inline si no hay
   prefers-reduced-motion ni Save-Data). Sin JS o con fallback, el contenido ya es visible. */
(() => {
  'use strict';
  const scenes = document.querySelectorAll('[data-mode="scrolly"]');
  if (!scenes.length) return;

  const W = 1920, H = 1080;
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const seg = (p, a, b) => clamp((p - a) / (b - a));
  const snap = (t) => 1 - Math.pow(1 - t, 3);
  const pad = (n) => String(n).padStart(3, '0');
  const loadImg = (src) => new Promise((res) => {
    const i = new Image(); i.decoding = 'async';
    i.onload = () => (i.decode ? i.decode().catch(() => {}) : Promise.resolve()).then(() => res(i));
    i.onerror = () => res(null); i.src = src;
  });
  const loadSeq = (dir, n) => Promise.all(Array.from({ length: n }, (_, k) => loadImg(`assets/seq/${dir}/${pad(k + 1)}.webp`)));

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
      const kx = img.naturalWidth / W, ky = img.naturalHeight / H;
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

  /* ---------- HERO: media cara + volteo cerámico + gestos ---------- */
  function hero(root) {
    const box = root.querySelector('[data-media]'), canvas = root.querySelector('[data-canvas]');
    const lg = matchMedia('(min-width: 1024px)');
    const st = new Stage(canvas, box);
    const progress = scroller(root);
    const stills = [null, null, null, null];
    const FACE = [0.55, 0, 0.45, 1], FULL = [0, 0, 1, 1];
    const G = [ // gesto por persona: carpeta, nº de fotogramas, región, tramo dentro del scroll
      { dir: 'g1', n: 32, r: FACE, a: 0.015, b: 0.13 },
      { dir: 'g2', n: 39, r: FULL, a: 0.245, b: 0.395 },
      { dir: 'g3', n: 36, r: FACE, a: 0.515, b: 0.665 },
      { dir: 'g4', n: 29, r: FACE, a: 0.79, b: 0.93 },
    ];
    const P = [[0, 0.14], [0.23, 0.41], [0.5, 0.68], [0.77, 1]];      // persona fija
    const F = [[0.14, 0.23], [0.41, 0.5], [0.68, 0.77]];               // volteos
    const ACTIVE = [0.185, 0.455, 0.725];                                // cambio de texto a mitad del volteo
    let ready = false, last = -1;

    const v = () => (lg.matches ? st.view(FULL, 0.85, 0.37) : st.view(FACE, 0.8, 0.37));

    function flip(fp, a, b, ka, kb, view) {
      const ctx = st.ctx, cw = st.cw, ch = st.ch;
      const cols = lg.matches ? 12 : 6, rows = Math.max(4, Math.round(cols * ch / cw));
      const A = st.buffered(ka, a, view), B = st.buffered(kb, b, view);
      const tw = cw / cols, th = ch / rows, D = cols + rows - 2, k = 0.055, j3 = 3 * st.dpr;
      ctx.fillStyle = '#F3E9DB'; ctx.fillRect(0, 0, cw, ch);
      for (let i = 0; i < cols; i++) for (let j = 0; j < rows; j++) {
        const d = (cols - 1 - i) + j; // ola diagonal: arriba-derecha → abajo-izquierda
        const lp = clamp(fp * (1 + D * k) - d * k);
        const x = Math.round(i * tw), y = Math.round(j * th), w = Math.round((i + 1) * tw) - x, h = Math.round((j + 1) * th) - y;
        const sx = Math.abs(Math.cos(lp * Math.PI)), src = lp < 0.5 ? A : B;
        if (lp <= 0 || lp >= 1) { ctx.drawImage(src, x, y, w, h, x, y, w, h); continue; }
        const dw = Math.max(1, w * sx);
        ctx.drawImage(src, x, y, w, h, x + (w - dw) / 2, y, dw, h);
        ctx.fillStyle = `rgba(255,253,249,${0.18 * (1 - sx)})`; ctx.fillRect(x + (w - dw) / 2, y, dw, h); // brillo de esmalte
        ctx.strokeStyle = '#F3E9DB'; ctx.lineWidth = j3; ctx.strokeRect(x + (w - dw) / 2, y, dw, h);       // junta marfil
      }
    }

    function draw(force) {
      if (!ready) return;
      const p = progress();
      if (!force && p === last) return; last = p;
      root.dataset.active = p < ACTIVE[0] ? 'p1' : p < ACTIVE[1] ? 'p2' : p < ACTIVE[2] ? 'p3' : 'p4';
      const view = v();
      for (let f = 0; f < 3; f++) {
        if (p > F[f][0] && p < F[f][1]) return flip(seg(p, F[f][0], F[f][1]), stills[f], stills[f + 1], f, f + 1, view);
      }
      const idx = P.findIndex(([a, b]) => p >= a && p <= b);
      const i = idx < 0 ? 0 : idx;
      st.still(stills[i], view);
      const g = G[i];
      if (g.frames && p > g.a && p < g.b) {
        const u = seg(p, g.a, g.b);
        if (u < 0.85) st.layer(g.frames[Math.round((u / 0.85) * (g.n - 1))], g.r, view);
        else st.layer(g.frames[g.n - 1], g.r, view, 1 - (u - 0.85) / 0.15); // fundido de cierre hacia el still
      }
    }

    st.onResize = () => draw(true);
    whenArmed(async () => {
      const imgs = await Promise.all([1, 2, 3, 4].map((n) => loadImg(`assets/img/hero-p${n}-1440.webp`)));
      if (imgs.some((x) => !x)) return; // sin stills: se queda el fallback
      imgs.forEach((x, n) => { stills[n] = x; });
      ready = true; canvas.hidden = false; draw(true);
      for (const g of G) { // secuencias, una a una, por orden de aparición
        const fr = await loadSeq(g.dir, g.n);
        if (fr.every(Boolean)) { g.frames = fr; draw(true); }
      }
    });
    return () => draw(false);
  }

  /* ---------- OFICINA PANAL: estrategia B ---------- */
  function office(root) {
    const box = root.querySelector('[data-media]'), canvas = root.querySelector('[data-canvas]');
    const st = new Stage(canvas, box);
    const progress = scroller(root);
    const R = [0, 0, 1, 1];
    const S = { o1: null, o2: null, o3: null };
    const Q = { o1: { dir: 'o1', n: 24 }, o2: { dir: 'o2', n: 48 } };
    let ready = false, last = -1;
    // 19 celdas hexagonales (radio axial 2), por anillos
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

    function frame(seq, u, fallback, view) {
      if (seq.frames) st.still(seq.frames[Math.round(u * (seq.n - 1))], view);
      else st.still(fallback, view);
    }

    function draw(force) {
      if (!ready) return;
      const p = progress();
      if (!force && p === last) return; last = p;
      const step = p < 0.25 ? 1 : p < 0.5 ? 2 : p < 0.75 ? 3 : 4;
      root.dataset.step = String(step);
      const view = st.view(R, 0.5, 0.5);
      if (step === 1) { frame(Q.o1, 0, S.o1, view); hexes(0, 1, view); }
      else if (step === 2) {
        const u = seg(p, 0.25, 0.5);
        frame(Q.o1, u, u < 0.5 ? S.o1 : S.o2, view);
        hexes(clamp(u / 0.8), u < 0.8 ? 1 : 1 - (u - 0.8) / 0.2, view);
      } else if (step === 3) frame(Q.o2, seg(p, 0.5, 0.75) * 0.5, S.o2, view);
      else { const u = seg(p, 0.75, 1); frame(Q.o2, 0.5 + u * 0.5, u < 0.9 ? S.o2 : S.o3, view); }
    }

    st.onResize = () => draw(true);
    let started = false;
    const start = () => whenArmed(async () => {
      if (started) return; started = true;
      const [a, b, c] = await Promise.all(['o1', 'o2', 'o3'].map((k) => loadImg(`assets/img/office-${k}-1280.webp`)));
      if (!a || !b || !c) return;
      Object.assign(S, { o1: a, o2: b, o3: c }); ready = true; canvas.hidden = false; draw(true);
      for (const k of ['o1', 'o2']) { const fr = await loadSeq(Q[k].dir, Q[k].n); if (fr.every(Boolean)) { Q[k].frames = fr; draw(true); } }
    });
    new IntersectionObserver((es, io) => { if (es.some((e) => e.isIntersecting)) { io.disconnect(); start(); } }, { rootMargin: '100% 0px' }).observe(root);
    return () => draw(false);
  }

  const renders = [];
  scenes.forEach((el) => {
    if (el.hasAttribute('data-hero')) renders.push(hero(el));
    else if (el.hasAttribute('data-office')) renders.push(office(el));
  });
  let raf = 0;
  const tick = () => { raf = 0; renders.forEach((r) => r()); };
  addEventListener('scroll', () => { if (!raf) raf = requestAnimationFrame(tick); }, { passive: true });
})();
