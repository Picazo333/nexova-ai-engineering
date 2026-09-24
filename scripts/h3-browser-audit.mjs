import { spawn } from "node:child_process";
import { mkdir, readFile, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";

const chromeBin = process.env.CHROME_BIN;
const baseUrl = process.env.BASE_URL ?? "http://127.0.0.1:3000/";
const evidenceDir = path.resolve("docs/evidence/website-premium");
const debugPort = 9222;

if (!chromeBin) throw new Error("CHROME_BIN is required.");

await mkdir(evidenceDir, { recursive: true });
const profileDir = path.join(os.tmpdir(), "nexova-h3-chrome");
await rm(profileDir, { recursive: true, force: true });

const chrome = spawn(chromeBin, [
  "--headless=new",
  "--no-sandbox",
  "--disable-gpu",
  "--hide-scrollbars",
  "--remote-debugging-address=127.0.0.1",
  "--remote-debugging-port=" + debugPort,
  "--user-data-dir=" + profileDir,
  "--window-size=1440,900",
  "about:blank",
], { stdio: "ignore" });

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function discoverTarget() {
  for (let attempt = 0; attempt < 40; attempt += 1) {
    try {
      const response = await fetch("http://127.0.0.1:" + debugPort + "/json/list");
      const targets = await response.json();
      const page = targets.find((target) => target.type === "page");
      if (page?.webSocketDebuggerUrl) return page.webSocketDebuggerUrl;
    } catch {}
    await sleep(250);
  }
  throw new Error("Chrome DevTools target did not become available.");
}

class CdpClient {
  constructor(url) {
    this.ws = new WebSocket(url);
    this.nextId = 1;
    this.pending = new Map();
    this.listeners = new Map();
    this.ready = new Promise((resolve, reject) => {
      this.ws.addEventListener("open", resolve, { once: true });
      this.ws.addEventListener("error", reject, { once: true });
    });
    this.ws.addEventListener("message", (event) => {
      const message = JSON.parse(String(event.data));
      if (message.id) {
        const pending = this.pending.get(message.id);
        if (!pending) return;
        this.pending.delete(message.id);
        if (message.error) pending.reject(new Error(message.error.message));
        else pending.resolve(message.result ?? {});
        return;
      }
      const handlers = this.listeners.get(message.method) ?? [];
      for (const handler of handlers) handler(message.params ?? {});
    });
  }

  async send(method, params = {}) {
    await this.ready;
    const id = this.nextId++;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }

  on(method, handler) {
    const handlers = this.listeners.get(method) ?? [];
    handlers.push(handler);
    this.listeners.set(method, handlers);
  }

  close() {
    this.ws.close();
  }
}

const failures = [];
const runtimeErrors = [];
const report = {
  candidate: process.env.GITHUB_SHA ?? "local",
  baseUrl,
  viewports: {},
  consoleErrors: runtimeErrors,
  keyboard: null,
  mobileNavigation: null,
  noJs: null,
  reducedMotion: null,
  axe: null,
  visualContracts: null,
};

let cdp;
const fail = (message) => failures.push(message);

async function evaluate(expression) {
  const result = await cdp.send("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
  if (result.exceptionDetails) throw new Error(result.exceptionDetails.text || "Runtime evaluation failed");
  return result.result?.value;
}

async function setViewport(width, height = 900) {
  await cdp.send("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: 1, mobile: false });
}

async function navigate(url = baseUrl) {
  await cdp.send("Page.navigate", { url });
  for (let attempt = 0; attempt < 40; attempt += 1) {
    try {
      const state = await evaluate("document.readyState");
      if (state === "complete" || state === "interactive") break;
    } catch {}
    await sleep(100);
  }
  await sleep(350);
}

async function dispatchTab() {
  const common = { key: "Tab", code: "Tab", windowsVirtualKeyCode: 9, nativeVirtualKeyCode: 9 };
  await cdp.send("Input.dispatchKeyEvent", { type: "keyDown", ...common });
  await cdp.send("Input.dispatchKeyEvent", { type: "keyUp", ...common });
  await sleep(100);
}

try {
  const wsUrl = await discoverTarget();
  cdp = new CdpClient(wsUrl);
  await cdp.ready;

  cdp.on("Runtime.exceptionThrown", (params) => {
    runtimeErrors.push({ source: "Runtime.exceptionThrown", text: params.exceptionDetails?.text ?? "Uncaught runtime exception" });
  });
  cdp.on("Log.entryAdded", (params) => {
    if (params.entry?.level === "error") runtimeErrors.push({ source: "Log.entryAdded", text: params.entry.text, url: params.entry.url ?? null });
  });

  await cdp.send("Page.enable");
  await cdp.send("Runtime.enable");
  await cdp.send("Log.enable");
  await cdp.send("Accessibility.enable");

  for (const width of [1440, 1024, 768, 430, 390]) {
    await setViewport(width);
    await navigate();
    const overflow = await evaluate("(() => { const root=document.documentElement; const body=document.body; return {clientWidth:root.clientWidth,rootScrollWidth:root.scrollWidth,bodyScrollWidth:body.scrollWidth,ok:root.scrollWidth<=root.clientWidth+1&&body.scrollWidth<=root.clientWidth+1}; })()");
    report.viewports[String(width)] = overflow;
    if (!overflow?.ok) fail("Horizontal overflow at " + width + "px: " + JSON.stringify(overflow));
  }

  await setViewport(1440, 900);
  await navigate();
  const axeSource = await readFile(path.resolve("node_modules/axe-core/axe.min.js"), "utf8");
  await evaluate(axeSource);
  const axeResult = await evaluate("(async () => { const result = await axe.run(document, { resultTypes: ['violations'] }); return { testEngine: result.testEngine, testEnvironment: result.testEnvironment, violations: result.violations }; })()");
  const blockingAxe = (axeResult?.violations ?? []).filter((violation) => violation.impact === "critical" || violation.impact === "serious");
  report.axe = {
    ok: blockingAxe.length === 0,
    critical: blockingAxe.filter((violation) => violation.impact === "critical").length,
    serious: blockingAxe.filter((violation) => violation.impact === "serious").length,
    totalViolations: (axeResult?.violations ?? []).length,
  };
  await writeFile(path.join(evidenceDir, "axe.json"), JSON.stringify(axeResult, null, 2) + "\n");
  if (blockingAxe.length > 0) fail("Axe serious/critical violations: " + JSON.stringify(blockingAxe.map((violation) => ({ id: violation.id, impact: violation.impact, nodes: violation.nodes?.length ?? 0 }))));

  report.visualContracts = await evaluate("(() => { const fonts = { instrumentSerif: document.fonts.check('42px \\\"Instrument Serif\\\"'), inter: document.fonts.check('16px Inter'), ibmPlexMono: document.fonts.check('11px \\\"IBM Plex Mono\\\"') }; const motion = { gsap: Boolean(window.gsap), scrollTrigger: Boolean(window.ScrollTrigger) }; const staticA2Blocks = document.querySelectorAll('.manifesto__material img, .closing__material img').length; return { ok: Object.values(fonts).every(Boolean) && motion.gsap && motion.scrollTrigger && staticA2Blocks === 0, fonts, motion, staticA2Blocks }; })()");
  if (!report.visualContracts?.ok) fail("Visual contract audit failed: " + JSON.stringify(report.visualContracts));

  await setViewport(390, 844);
  await navigate();
  const controlsPresent = await evaluate("(() => { const button=document.querySelector('.menu-toggle'); const nav=document.querySelector('#primary-navigation'); return button instanceof HTMLButtonElement && nav instanceof HTMLElement; })()");
  if (!controlsPresent) {
    report.mobileNavigation = { ok: false, reason: "controls missing" };
    fail("Mobile navigation failed: controls missing");
  } else {
    await evaluate("document.querySelector('.menu-toggle').click()");
    await sleep(120);
    const opened = await evaluate("(() => { const button=document.querySelector('.menu-toggle'); const nav=document.querySelector('#primary-navigation'); return button.getAttribute('aria-expanded')==='true' && nav.classList.contains('is-open') && getComputedStyle(nav).display!=='none'; })()");
    await evaluate("document.querySelector('.menu-toggle').click()");
    await sleep(120);
    const closed = await evaluate("(() => { const button=document.querySelector('.menu-toggle'); const nav=document.querySelector('#primary-navigation'); return button.getAttribute('aria-expanded')==='false' && !nav.classList.contains('is-open'); })()");
    report.mobileNavigation = { ok: Boolean(opened && closed), opened: Boolean(opened), closed: Boolean(closed) };
    if (!report.mobileNavigation.ok) fail("Mobile navigation failed: " + JSON.stringify(report.mobileNavigation));
  }

  await navigate();
  await evaluate("document.activeElement instanceof HTMLElement && document.activeElement.blur()");
  await dispatchTab();
  report.keyboard = await evaluate("(() => { const el=document.activeElement; if(!(el instanceof HTMLElement)||el===document.body) return {ok:false,reason:'no interactive focus target'}; const style=getComputedStyle(el); const focusVisible=el.matches(':focus-visible'); const outlineVisible=style.outlineStyle!=='none'&&parseFloat(style.outlineWidth||'0')>=1; return {ok:focusVisible&&outlineVisible,tag:el.tagName,text:(el.textContent||'').trim().slice(0,80),focusVisible,outlineStyle:style.outlineStyle,outlineWidth:style.outlineWidth,outlineColor:style.outlineColor}; })()");
  if (!report.keyboard?.ok) fail("Keyboard/focus audit failed: " + JSON.stringify(report.keyboard));

  await cdp.send("Emulation.setScriptExecutionDisabled", { value: true });
  await setViewport(390, 844);
  await cdp.send("Page.navigate", { url: baseUrl });
  await sleep(700);
  const axTree = await cdp.send("Accessibility.getFullAXTree");
  const axNames = (axTree.nodes ?? []).map((node) => node.name?.value).filter(Boolean).join(" ");
  const noJsReadable = axNames.includes("Criterio humano") && axNames.includes("Nexova Solutions");
  const noJsShot = await cdp.send("Page.captureScreenshot", { format: "png", fromSurface: true });
  await writeFile(path.join(evidenceDir, "no-js-390.png"), Buffer.from(noJsShot.data, "base64"));
  report.noJs = { ok: noJsReadable, evidenceTextPresent: noJsReadable };
  if (!noJsReadable) fail("No-JS fallback was not readable in the accessibility tree.");
  await cdp.send("Emulation.setScriptExecutionDisabled", { value: false });

  await cdp.send("Emulation.setEmulatedMedia", { media: "screen", features: [{ name: "prefers-reduced-motion", value: "reduce" }] });
  await setViewport(390, 844);
  await navigate();
  const reduced = await evaluate("window.matchMedia('(prefers-reduced-motion: reduce)').matches");
  const reducedShot = await cdp.send("Page.captureScreenshot", { format: "png", fromSurface: true, captureBeyondViewport: true });
  await writeFile(path.join(evidenceDir, "reduced-motion-390.png"), Buffer.from(reducedShot.data, "base64"));
  report.reducedMotion = { ok: Boolean(reduced), mediaQueryMatches: Boolean(reduced) };
  if (!reduced) fail("Reduced-motion media emulation did not activate.");
  await cdp.send("Emulation.setEmulatedMedia", { media: "screen", features: [] });

  if (runtimeErrors.length > 0) fail("Console/runtime errors: " + JSON.stringify(runtimeErrors));

  report.pass = failures.length === 0;
  report.failures = failures;
  await writeFile(path.join(evidenceDir, "browser-audit.json"), JSON.stringify(report, null, 2) + "\n");
  if (failures.length > 0) throw new Error(failures.join("\n"));
} finally {
  cdp?.close();
  chrome.kill("SIGTERM");
  await sleep(150);
  await rm(profileDir, { recursive: true, force: true });
}
