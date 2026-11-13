import { spawnSync } from "node:child_process";
import { mkdirSync, renameSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import AxeBuilder from "@axe-core/playwright";
import { chromium } from "@playwright/test";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const outDir = process.env.EVIDENCE_DIR || path.resolve(root, "../../docs/inventory-management-backoffice/evidence");
mkdirSync(outDir, { recursive: true });

const email = process.env.INVENTORY_E2E_EMAIL || "";
const password = process.env.INVENTORY_E2E_PASSWORD || "";
const base = process.env.BACKOFFICE_URL || "http://127.0.0.1:3001";
if (!email || !password) {
  console.error("Faltan INVENTORY_E2E_EMAIL y INVENTORY_E2E_PASSWORD");
  process.exit(1);
}

const widths = [
  { name: "390", width: 390, height: 844 },
  { name: "768", width: 768, height: 1024 },
  { name: "1280", width: 1280, height: 800 },
];

const browser = await chromium.launch({ headless: true });
const failures = [];

function note(message) {
  console.log(message);
}

async function shot(page, name) {
  const file = path.join(outDir, `${name}.png`);
  await page.screenshot({ path: file, fullPage: true });
  const overflow = await page.evaluate(() => {
    const doc = document.documentElement;
    return doc.scrollWidth - doc.clientWidth;
  });
  note(`shot ${name} overflow=${overflow}`);
  if (overflow > 1) failures.push(`${name} overflow ${overflow}`);
  return file;
}

async function login(page) {
  await page.goto(`${base}/login?next=${encodeURIComponent("/backoffice/inventory/products")}`, {
    waitUntil: "networkidle",
  });
  await page.locator("#email").fill(email);
  await page.locator("#password").fill(password);
  await page.getByRole("button", { name: "Entrar" }).click();
  await page.getByRole("heading", { name: "Activos", exact: true }).waitFor({ timeout: 30000 });
  await page.getByRole("cell", { name: "NXV-IT-001" }).waitFor();
}

async function axe(page, name) {
  const result = await new AxeBuilder({ page }).analyze();
  const serious = result.violations.filter((item) => item.impact === "serious" || item.impact === "critical");
  const summary = {
    name,
    url: page.url(),
    violations: result.violations.map((item) => ({
      id: item.id,
      impact: item.impact,
      nodes: item.nodes.length,
      help: item.help,
    })),
  };
  note(`axe ${name} serious=${serious.length} total=${result.violations.length}`);
  if (serious.length) failures.push(`${name} axe ${serious.map((item) => item.id).join(",")}`);
  return summary;
}

const axeReports = [];

const setup = await browser.newContext();
const setupPage = await setup.newPage();
await login(setupPage);
await setup.storageState({ path: "/tmp/inventory-storage-state.json" });
await setup.close();

for (const size of widths) {
  const context = await browser.newContext({
    viewport: { width: size.width, height: size.height },
    storageState: "/tmp/inventory-storage-state.json",
  });
  const page = await context.newPage();
  await page.goto(`${base}/backoffice/inventory/products`, { waitUntil: "networkidle" });
  await page.getByRole("cell", { name: "NXV-IT-001" }).waitFor();
  const stockText = await page.locator("tr", { hasText: "NXV-IT-001" }).innerText();
  if (!stockText.includes("12") || !stockText.includes("Saludable")) {
    failures.push(`${size.name} products missing seed stock: ${stockText}`);
  }
  if (!(await page.locator("tr", { hasText: "NXV-IT-002" }).innerText()).includes("Bajo")) {
    failures.push(`${size.name} NXV-IT-002 should be Bajo`);
  }
  if (!(await page.locator("tr", { hasText: "NXV-PER-002" }).innerText()).includes("Sin stock")) {
    failures.push(`${size.name} NXV-PER-002 should be Sin stock`);
  }
  await shot(page, `products-${size.name}`);
  if (size.name === "1280") axeReports.push(await axe(page, "products-1280"));

  await page.locator("tr", { hasText: "NXV-IT-001" }).getByRole("link", { name: "Registrar salida" }).click();
  await page.getByTestId("stock-now").getByText("12").waitFor();
  await page.locator("#quantity").fill("99");
  await page.locator("#assigned_to").fill("NXV-EMP-1042");
  await page.getByTestId("stock-warning").waitFor();
  await shot(page, `outbound-warning-${size.name}`);
  await page.getByRole("button", { name: "Registrar salida de activos" }).click();
  await page.getByTestId("api-error").waitFor();
  const apiError = await page.getByTestId("api-error").innerText();
  if (!apiError.includes("Insufficient stock") || !apiError.includes("Available: 12")) {
    failures.push(`${size.name} 400 message: ${apiError}`);
  }
  await shot(page, `outbound-400-${size.name}`);
  if (size.name === "1280") axeReports.push(await axe(page, "outbound-400-1280"));
  await context.close();
}

{
  const context = await browser.newContext({
    viewport: { width: 1280, height: 800 },
    storageState: "/tmp/inventory-storage-state.json",
    recordVideo: { dir: outDir, size: { width: 1280, height: 800 } },
  });
  const page = await context.newPage();
  await page.goto(`${base}/backoffice/inventory/products`, { waitUntil: "networkidle" });
  await page.waitForTimeout(1500);
  await page.locator("tr", { hasText: "NXV-IT-001" }).getByRole("link", { name: "Registrar salida" }).click();
  await page.getByTestId("stock-now").getByText("12").waitFor();
  await page.waitForTimeout(1200);
  await page.locator("#quantity").fill("99");
  await page.locator("#assigned_to").fill("NXV-EMP-1042");
  await page.getByTestId("stock-warning").waitFor();
  await page.waitForTimeout(1500);
  await page.getByRole("button", { name: "Registrar salida de activos" }).click();
  await page.getByTestId("api-error").waitFor();
  await page.waitForTimeout(1800);
  const video = page.video();
  await context.close();
  const saved = await video?.path();
  if (saved) {
    const target = path.join(outDir, "recorrido-salida-400.webm");
    renameSync(saved, target);
    note(`video ${target}`);
  }
}

{
  const context = await browser.newContext({
    viewport: { width: 1280, height: 800 },
    storageState: "/tmp/inventory-storage-state.json",
    reducedMotion: "reduce",
    recordVideo: { dir: outDir, size: { width: 1280, height: 800 } },
  });
  const page = await context.newPage();
  await page.goto(`${base}/backoffice/inventory/products`, { waitUntil: "networkidle" });
  await page.waitForTimeout(1500);
  await page.locator("tr", { hasText: "NXV-IT-001" }).getByRole("link", { name: "Registrar salida" }).click();
  await page.getByTestId("stock-now").getByText("12").waitFor();
  await page.waitForTimeout(2000);
  const video = page.video();
  await context.close();
  const saved = await video?.path();
  if (saved) {
    renameSync(saved, path.join(outDir, "recorrido-reduced.webm"));
  }
}

{
  const context = await browser.newContext({
    viewport: { width: 1280, height: 800 },
    storageState: "/tmp/inventory-storage-state.json",
  });
  const page = await context.newPage();
  await page.goto(`${base}/backoffice/inventory/orders/inbound`, { waitUntil: "networkidle" });
  await page.locator("#asset").selectOption({ label: 'Laptop 14" Business · NXV-IT-001 · Valencia' });
  await page.getByText(/Stock actual \(current_stock\):/).waitFor();
  await page.locator("#supplier").fill("TechDistrib Valencia S.L.");
  await page.locator("#quantity").fill("1");
  await page.getByRole("button", { name: "Registrar entrada de activos" }).click();
  await page.getByTestId("confirm").waitFor();
  const confirm = await page.getByTestId("confirm").innerText();
  if (!confirm.includes("Entrada registrada") || !confirm.includes("NXV-IT-001")) {
    failures.push(`confirm: ${confirm}`);
  }
  for (const size of widths) {
    await page.setViewportSize({ width: size.width, height: size.height });
    await shot(page, `inbound-confirm-${size.name}`);
  }
  axeReports.push(await axe(page, "inbound-confirm"));
  await page.goto(`${base}/backoffice/inventory/orders`, { waitUntil: "networkidle" });
  await page.getByRole("heading", { name: "Historial de entradas y salidas" }).waitFor();
  await page.getByText("00000000-0000-4000-8000-000000000201").first().waitFor();
  for (const size of widths) {
    await page.setViewportSize({ width: size.width, height: size.height });
    await shot(page, `orders-${size.name}`);
  }
  axeReports.push(await axe(page, "orders"));
  await context.close();
}

{
  const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const page = await context.newPage();
  await page.goto(`${base}/backoffice/inventory/products`, { waitUntil: "networkidle" });
  await page.waitForURL(/\/login/);
  await shot(page, "login-redirect-390");
  await page.setViewportSize({ width: 768, height: 1024 });
  await shot(page, "login-redirect-768");
  await page.setViewportSize({ width: 1280, height: 800 });
  await shot(page, "login-redirect-1280");
  axeReports.push(await axe(page, "login"));
  await context.close();
}

for (const size of widths) {
  const context = await browser.newContext({
    viewport: { width: size.width, height: size.height },
    storageState: "/tmp/inventory-storage-state.json",
  });
  const page = await context.newPage();
  await page.route(/127\.0\.0\.1:8000\/inventory\/products(?:\?|$)/, async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 1200));
    await route.continue();
  });
  const pending = page.goto(`${base}/backoffice/inventory/products`);
  await page.getByText("Cargando activos…").waitFor();
  await shot(page, `products-loading-${size.name}`);
  await page.unroute(/127\.0\.0\.1:8000\/inventory\/products(?:\?|$)/);
  await pending;
  await context.close();
}

{
  const context = await browser.newContext({
    viewport: { width: 1280, height: 800 },
    storageState: "/tmp/inventory-storage-state.json",
    reducedMotion: "reduce",
  });
  const page = await context.newPage();
  await page.goto(`${base}/backoffice/inventory/products`, { waitUntil: "networkidle" });
  const motion = await page.evaluate(() => document.documentElement.dataset.motion);
  note(`motion=${motion}`);
  if (motion !== "reduced") failures.push(`motion dataset ${motion}`);
  await shot(page, "products-reduced-1280");
  await page.setViewportSize({ width: 390, height: 844 });
  await shot(page, "products-reduced-390");
  await context.close();
}

async function rewriteInventory(page, port) {
  await page.route(/127\.0\.0\.1:8000\/inventory\//, async (route) => {
    const url = route.request().url().replace("127.0.0.1:8000", `127.0.0.1:${port}`);
    const response = await route.fetch({ url });
    await route.fulfill({ response });
  });
}

for (const size of widths) {
  const context = await browser.newContext({
    viewport: { width: size.width, height: size.height },
    storageState: "/tmp/inventory-storage-state.json",
  });
  const page = await context.newPage();
  await rewriteInventory(page, 8012);
  await page.goto(`${base}/backoffice/inventory/products`, { waitUntil: "networkidle" });
  await page.getByRole("heading", { name: "No hay activos" }).waitFor({ timeout: 20000 });
  await shot(page, `products-empty-${size.name}`);
  await page.goto(`${base}/backoffice/inventory/orders`, { waitUntil: "networkidle" });
  await page.getByRole("heading", { name: "Aún no hay entradas ni salidas" }).waitFor();
  await shot(page, `orders-empty-${size.name}`);
  if (size.name === "1280") axeReports.push(await axe(page, "orders-empty"));
  await context.close();
}

for (const size of widths) {
  const context = await browser.newContext({
    viewport: { width: size.width, height: size.height },
    storageState: "/tmp/inventory-storage-state.json",
  });
  const page = await context.newPage();
  await rewriteInventory(page, 8013);
  await page.goto(`${base}/backoffice/inventory/products`, { waitUntil: "networkidle" });
  await page.getByRole("heading", { name: "No se pudieron cargar los activos" }).waitFor({ timeout: 20000 });
  const errorText = await page.locator(".banner").innerText();
  if (!errorText.includes("No se pudo completar la operación")) {
    failures.push(`${size.name} 503 text: ${errorText}`);
  }
  await shot(page, `products-error-${size.name}`);
  if (size.name === "390") axeReports.push(await axe(page, "products-error"));
  await context.close();
}

const hash = spawnSync(
  "sha256sum",
  [
    path.join(root, "brand/lockups/signal-horizontal.svg"),
    path.join(root, "brand/lockups/signal-stacked.svg"),
  ],
  { encoding: "utf8" },
);
note(hash.stdout);

writeFileSync(path.join(outDir, "axe-summary.json"), JSON.stringify({ failures, axeReports }, null, 2));
await browser.close();
if (failures.length) {
  console.error(failures.join("\n"));
  process.exit(1);
}
note("capture ok");
