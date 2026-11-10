// Capturas que pide la rúbrica 016 para el PR: formulario con error de
// validación, listado con datos y panel de resumen con métricas.
// Uso: API en API_BASE (por defecto http://127.0.0.1:8000) con el seed cargado.
//   node scripts/capture-incident-manager.mjs
import { chromium } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";

const API = process.env.API_BASE || "http://127.0.0.1:8000";
const outDir = path.resolve("../../docs/centralized-incident-manager/evidence");
fs.mkdirSync(outDir, { recursive: true });

async function json(url, options) {
  const response = await fetch(url, options);
  const text = await response.text();
  if (!response.ok) throw new Error(`${response.status} ${url}`);
  return JSON.parse(text);
}

const email = `capturas-${Date.now()}@nexova.test`;
const password = "clave-segura-1";
const headers = { "content-type": "application/json", accept: "application/json" };
await json(`${API}/users`, { method: "POST", headers, body: JSON.stringify({ email, password, name: "Operador Capturas" }) });
const token = (await json(`${API}/auth/login`, { method: "POST", headers, body: JSON.stringify({ email, password }) }))
  .access_token;

const browser = await chromium.launch({ channel: "chrome" });
const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
await context.addInitScript((value) => sessionStorage.setItem("nexova-access-token", value), token);
const page = await context.newPage();
// La cabecera es sticky: en una captura de página completa se repetiría a
// mitad de imagen. Solo para la foto se deja en flujo normal.
const unstick = () => page.addStyleTag({ content: "header, .site-header { position: static !important; }" });

await page.goto(`${API}/incidencias/nueva`);
await page.getByRole("button", { name: "Registrar incidencia" }).click();
await page.getByText("El título es obligatorio.").waitFor();
await unstick();
await page.screenshot({ path: path.join(outDir, "form-error-1280.png"), fullPage: true });

await page.goto(`${API}/incidencias`);
await page.locator('#incident-list[aria-busy="false"]').waitFor();
await page.locator("#incident-list table").waitFor();
await unstick();
// Las primeras filas bastan para mostrar datos cargados (96 filas pesan ~3 MB).
const box = await page.locator("#incident-list").boundingBox();
await page.screenshot({ path: path.join(outDir, "list-1280.png"), fullPage: true, clip: { x: 0, y: Math.max(0, box.y - 120), width: 1280, height: 1100 } });

await page.locator('#incident-summary[aria-busy="false"]').waitFor();
await page.locator("#incident-summary").screenshot({ path: path.join(outDir, "summary-1280.png") });

await browser.close();
console.log("capturas en", outDir);
