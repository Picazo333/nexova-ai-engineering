import fs from "node:fs/promises";
import { createRequire } from "node:module";
import path from "node:path";
import { chromium } from "playwright-core";

const require = createRequire(import.meta.url);
const axePath = require.resolve("axe-core/axe.min.js");
const axeSource = await fs.readFile(axePath, "utf8");

const baseUrl = process.env.PREMIUM_QA_URL || "http://127.0.0.1:3000/";
const chromePath = process.env.CHROME_BIN || "/usr/bin/google-chrome";
const outDir = path.resolve("docs/evidence/website-premium");
await fs.mkdir(outDir, { recursive: true });

const browser = await chromium.launch({
  headless: true,
  executablePath: chromePath,
  args: ["--no-sandbox", "--disable-dev-shm-usage"],
});

const widths = [1440, 1024, 768, 430, 390];
const report = {
  generatedAt: new Date().toISOString(),
  baseUrl,
  widths: {},
  reducedMotion: {},
  noJavaScript: {},
  accessibility: {},
};

let failed = false;

for (const width of widths) {
  const context = await browser.newContext({
    viewport: { width, height: 1000 },
    reducedMotion: "no-preference",
  });
  const page = await context.newPage();
  const consoleErrors = [];
  const pageErrors = [];

  page.on("console", (message) => {
    if (message.type() === "error") consoleErrors.push(message.text());
  });
  page.on("pageerror", (error) => pageErrors.push(error.message));

  await page.goto(baseUrl, { waitUntil: "networkidle" });
  await page.screenshot({
    path: path.join(outDir, `runtime-${width}.png`),
    fullPage: true,
  });

  const metrics = await page.evaluate(() => {
    const root = document.documentElement;
    const hero = document.querySelector("#hero-title");
    const manifesto = document.querySelector("#manifesto-title");
    const navToggle = document.querySelector(".menu-toggle");
    const resources = performance
      .getEntriesByType("resource")
      .map((entry) => entry.name)
      .filter((name) => /\.(avif|webp|png)(\?|$)/.test(name));

    return {
      innerWidth: window.innerWidth,
      scrollWidth: root.scrollWidth,
      overflowPx: Math.max(0, root.scrollWidth - window.innerWidth),
      heroText: hero?.textContent?.trim() ?? "",
      manifestoText: manifesto?.textContent?.trim() ?? "",
      mobileToggleVisible:
        navToggle instanceof HTMLElement &&
        getComputedStyle(navToggle).display !== "none",
      imageResources: resources,
    };
  });

  const focusSamples = [];
  await page.keyboard.press("Tab");
  for (let index = 0; index < 8; index += 1) {
    const sample = await page.evaluate(() => {
      const active = document.activeElement;
      if (!(active instanceof HTMLElement)) return null;
      const style = getComputedStyle(active);
      return {
        tag: active.tagName,
        text: active.textContent?.trim().slice(0, 80) ?? "",
        outlineStyle: style.outlineStyle,
        outlineWidth: style.outlineWidth,
      };
    });
    if (sample) focusSamples.push(sample);
    await page.keyboard.press("Tab");
  }

  if (width <= 430) {
    const toggle = page.locator(".menu-toggle");
    await toggle.click();
    const expanded = await toggle.getAttribute("aria-expanded");
    const navVisible = await page.locator(".site-nav").evaluate((element) => {
      return getComputedStyle(element).display !== "none";
    });
    if (expanded !== "true" || !navVisible) failed = true;
  }

  const hasVisibleFocus = focusSamples.some(
    (item) => item.outlineStyle !== "none" && item.outlineWidth !== "0px",
  );
  const rawMasterRequested = metrics.imageResources.some((name) =>
    /a1-hero-(desktop|mobile)\.png|a2-crimson-fibrous\.png/.test(name),
  );

  if (metrics.overflowPx > 1) failed = true;
  if (!metrics.heroText || !metrics.manifestoText) failed = true;
  if (consoleErrors.length || pageErrors.length) failed = true;
  if (!hasVisibleFocus) failed = true;
  if (rawMasterRequested) failed = true;

  report.widths[width] = {
    ...metrics,
    consoleErrors,
    pageErrors,
    focusSamples,
    hasVisibleFocus,
    rawMasterRequested,
  };

  if (width === 1440 || width === 390) {
    await page.addScriptTag({ content: axeSource });
    const axe = await page.evaluate(async () => {
      const result = await window.axe.run(document, {
        runOnly: {
          type: "tag",
          values: ["wcag2a", "wcag2aa", "wcag21aa"],
        },
      });
      return result.violations.map((violation) => ({
        id: violation.id,
        impact: violation.impact,
        description: violation.description,
        nodes: violation.nodes.length,
      }));
    });

    const blocking = axe.filter(
      (violation) => violation.impact === "critical" || violation.impact === "serious",
    );
    if (blocking.length) failed = true;
    report.accessibility[width] = { violations: axe, blocking };
  }

  await context.close();
}

{
  const context = await browser.newContext({
    viewport: { width: 390, height: 900 },
    reducedMotion: "reduce",
  });
  const page = await context.newPage();
  await page.goto(baseUrl, { waitUntil: "networkidle" });
  await page.evaluate(() => window.scrollTo(0, 500));
  await page.waitForTimeout(120);
  const state = await page.evaluate(() => {
    const hero = document.querySelector(".hero-copy");
    const manifesto = document.querySelector(".manifesto-copy");
    const heroStyle = hero ? getComputedStyle(hero) : null;
    const manifestoStyle = manifesto ? getComputedStyle(manifesto) : null;
    return {
      heroOpacity: heroStyle?.opacity ?? null,
      heroTransform: heroStyle?.transform ?? null,
      manifestoOpacity: manifestoStyle?.opacity ?? null,
      manifestoTransform: manifestoStyle?.transform ?? null,
    };
  });
  if (
    state.heroOpacity !== "1" ||
    state.manifestoOpacity !== "1" ||
    (state.heroTransform && state.heroTransform !== "none") ||
    (state.manifestoTransform && state.manifestoTransform !== "none")
  ) {
    failed = true;
  }
  report.reducedMotion = state;
  await context.close();
}

{
  const context = await browser.newContext({
    viewport: { width: 390, height: 900 },
    javaScriptEnabled: false,
  });
  const page = await context.newPage();
  await page.goto(baseUrl, { waitUntil: "domcontentloaded" });
  const text = await page.locator("body").innerText();
  const hasFallback =
    text.includes("Nexova Solutions") &&
    text.includes("Executive recruitment") &&
    text.includes("Outsourced customer support");
  if (!hasFallback) failed = true;
  report.noJavaScript = { hasFallback, excerpt: text.slice(0, 600) };
  await page.screenshot({
    path: path.join(outDir, "runtime-no-js-390.png"),
    fullPage: true,
  });
  await context.close();
}

await browser.close();
await fs.writeFile(
  path.join(outDir, "qa-report.json"),
  JSON.stringify(report, null, 2),
);

console.log(JSON.stringify(report, null, 2));

if (failed) {
  console.error("Premium runtime QA failed.");
  process.exit(1);
}
