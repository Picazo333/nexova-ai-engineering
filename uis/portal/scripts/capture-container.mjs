import { chromium } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import fs from "node:fs";
import path from "node:path";

const outDir = path.resolve("../../evidence");
const artifactDir = "/opt/cursor/artifacts";
fs.mkdirSync(outDir, { recursive: true });
fs.mkdirSync(artifactDir, { recursive: true });

const base = process.env.BACKOFFICE_URL || "http://127.0.0.1:3001";
const widths = [
  { name: "390", width: 390, height: 844 },
  { name: "768", width: 768, height: 1024 },
  { name: "1280", width: 1280, height: 800 },
];

async function shot(page, name) {
  const file = path.join(outDir, `${name}.png`);
  await page.screenshot({ path: file, fullPage: true });
  fs.copyFileSync(file, path.join(artifactDir, `${name}.png`));
  const box = await page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
  }));
  if (box.scrollWidth > box.clientWidth + 1) {
    throw new Error(`overflow ${name} ${box.scrollWidth}>${box.clientWidth}`);
  }
  console.log("shot", name, box.clientWidth);
}

const browser = await chromium.launch({ headless: true });
const axeReport = [];

async function axe(page, name) {
  const results = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag22aa"])
    .analyze();
  const serious = results.violations.filter((item) => item.impact === "serious" || item.impact === "critical");
  axeReport.push({
    name,
    violations: serious.map((item) => ({ id: item.id, impact: item.impact, help: item.help, nodes: item.nodes.length })),
  });
  if (serious.length) {
    console.error("axe", name, JSON.stringify(serious, null, 2));
    throw new Error(`axe ${name}`);
  }
  console.log("axe", name, "ok");
}

for (const size of widths) {
  const context = await browser.newContext({ viewport: { width: size.width, height: size.height } });
  const page = await context.newPage();
  let release;
  const gate = new Promise((resolve) => {
    release = resolve;
  });
  await page.route("**/api/stack", async (route) => {
    await gate;
    await route.continue();
  });
  await page.goto(base + "/", { waitUntil: "domcontentloaded" });
  await page.getByText("Comprobando la API.").waitFor();
  await shot(page, `container-loading-${size.name}`);
  release();
  await page.getByText("En marcha").waitFor();
  await shot(page, `container-success-${size.name}`);
  await page.locator("#filtro").fill("sede");
  await page.getByText("Ninguna incidencia coincide con ese texto.").waitFor();
  await shot(page, `container-empty-${size.name}`);
  if (size.name === "1280") await axe(page, "success-filter");
  await page.unroute("**/api/stack");
  await page.route("**/api/stack", (route) => route.abort());
  await page.reload({ waitUntil: "domcontentloaded" });
  await page.getByText("No hay conexión con la API.").waitFor();
  const kept = await page.locator("#filtro").inputValue();
  if (kept !== "sede") throw new Error(`filter lost on error: ${kept}`);
  await shot(page, `container-error-${size.name}`);
  if (size.name === "1280") await axe(page, "error");
  await context.close();
}

const missing = await browser.newContext({ viewport: { width: 1280, height: 800 } });
const missingPage = await missing.newPage();
const response = await missingPage.goto(base + "/no-existe", { waitUntil: "domcontentloaded" });
if (response.status() !== 404) throw new Error(`expected 404, got ${response.status()}`);
await missingPage.getByRole("heading", { name: "No encontramos esa ruta" }).waitFor();
await shot(missingPage, "container-404-1280");
await axe(missingPage, "404");
await missing.close();

const reduced = await browser.newContext({
  viewport: { width: 1280, height: 800 },
  reducedMotion: "reduce",
});
const reducedPage = await reduced.newPage();
await reducedPage.goto(base + "/", { waitUntil: "networkidle" });
await reducedPage.getByText("En marcha").waitFor();
const motion = await reducedPage.locator(".result-panel").evaluate((node) => getComputedStyle(node).transitionDuration);
fs.writeFileSync(path.join(outDir, "container-reduced-motion.txt"), `transition-duration ${motion}\n`);
if (motion !== "0s") throw new Error(`reduced motion still animates: ${motion}`);
await shot(reducedPage, "container-reduced-1280");
await reduced.close();

const videoContext = await browser.newContext({
  viewport: { width: 1280, height: 800 },
  recordVideo: { dir: outDir, size: { width: 1280, height: 800 } },
});
const videoPage = await videoContext.newPage();
const started = Date.now();
await videoPage.goto(base + "/", { waitUntil: "domcontentloaded" });
await videoPage.getByText("En marcha").waitFor();
await videoPage.locator("#filtro").fill("valencia");
await videoPage.locator("footer").scrollIntoViewIfNeeded();
const elapsed = Date.now() - started;
if (elapsed < 6500) await videoPage.waitForTimeout(6500 - elapsed);
await videoContext.close();
const videoPath = await videoPage.video().path();
const target = path.join(outDir, "container-recorrido.webm");
fs.copyFileSync(videoPath, target);
fs.copyFileSync(target, path.join(artifactDir, "container-recorrido.webm"));
if (videoPath !== target) fs.rmSync(videoPath, { force: true });
console.log("video", target);

fs.writeFileSync(path.join(outDir, "container-axe.json"), JSON.stringify(axeReport, null, 2));
await browser.close();
console.log("capture done");
