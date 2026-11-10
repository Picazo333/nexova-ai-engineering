import { chromium } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";

const outDir = path.resolve("../../docs/auth-frontend/evidence");
fs.mkdirSync(outDir, { recursive: true });

const email = `foto-${Date.now()}@nexova.test`;
const password = "clave-segura-1";

async function json(url, options) {
  const response = await fetch(url, options);
  const text = await response.text();
  if (!response.ok) throw new Error(`${response.status} ${url} ${text}`);
  return JSON.parse(text);
}

await json("http://127.0.0.1:8000/users", {
  method: "POST",
  headers: { "content-type": "application/json", accept: "application/json" },
  body: JSON.stringify({
    email,
    password,
    name: "Ana Soler",
    phone: "600111222",
    address: "Calle de Colón 1, Valencia",
  }),
});
const token = (
  await json("http://127.0.0.1:8000/auth/login", {
    method: "POST",
    headers: { "content-type": "application/json", accept: "application/json" },
    body: JSON.stringify({ email, password }),
  })
).access_token;

const browser = await chromium.launch({ channel: "chrome", headless: true });
const widths = [
  { name: "390", width: 390, height: 844 },
  { name: "768", width: 768, height: 1024 },
  { name: "1280", width: 1280, height: 800 },
];

async function shot(page, name) {
  const file = path.join(outDir, `${name}.png`);
  await page.screenshot({ path: file, fullPage: true });
  const box = await page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
  }));
  if (box.scrollWidth > box.clientWidth + 1) {
    throw new Error(`overflow ${name} ${box.scrollWidth}>${box.clientWidth}`);
  }
  console.log("shot", name);
}

for (const size of widths) {
  const context = await browser.newContext({ viewport: { width: size.width, height: size.height } });
  const page = await context.newPage();
  await page.goto("http://127.0.0.1:3000/login", { waitUntil: "networkidle" });
  await page.getByRole("heading", { name: "Entrar al portal interno" }).waitFor();
  await shot(page, `login-${size.name}`);
  await page.goto("http://127.0.0.1:3000/register", { waitUntil: "networkidle" });
  await page.getByRole("heading", { name: "Crear una cuenta" }).waitFor();
  await shot(page, `register-${size.name}`);
  await context.close();
}

{
  const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const page = await context.newPage();
  await page.goto("http://127.0.0.1:3000/register");
  await page.getByLabel("Correo").fill("mal");
  await page.getByLabel("Contraseña").fill("corta");
  await page.getByRole("button", { name: "Crear cuenta" }).click();
  await page.locator("#register-password-error").waitFor();
  await shot(page, "register-error-390");
  await context.close();
}

{
  const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const page = await context.newPage();
  await page.goto("http://127.0.0.1:3000/register");
  await page.getByLabel("Correo").fill("mal");
  await page.getByLabel("Contraseña").fill("corta");
  await page.getByRole("button", { name: "Crear cuenta" }).click();
  await page.locator("#register-email-error").waitFor();
  await shot(page, "register-error-1280");
  await context.close();
}

{
  const context = await browser.newContext({ viewport: { width: 768, height: 1024 } });
  const page = await context.newPage();
  await page.goto("http://127.0.0.1:3000/login");
  await page.getByLabel("Correo").fill("nadie@nexova.test");
  await page.getByLabel("Contraseña").fill("clave-erronea");
  await page.getByRole("button", { name: "Entrar" }).click();
  await page.locator(".alert").waitFor();
  await shot(page, "login-error-768");
  await context.close();
}

for (const size of widths) {
  const context = await browser.newContext({ viewport: { width: size.width, height: size.height } });
  await context.addInitScript((value) => localStorage.setItem("nexova-access-token", value), token);
  const page = await context.newPage();
  await page.goto("http://127.0.0.1:3000/", { waitUntil: "networkidle" });
  await page.getByRole("heading", { name: "Análisis de tickets de soporte" }).waitFor();
  await page.getByText("Aún no hay un análisis").waitFor();
  await shot(page, `incidencias-vacio-${size.name}`);
  await context.close();
}

for (const size of [widths[0], widths[2]]) {
  const context = await browser.newContext({ viewport: { width: size.width, height: size.height } });
  await context.addInitScript((value) => localStorage.setItem("nexova-access-token", value), token);
  const page = await context.newPage();
  await page.goto("http://127.0.0.1:3000/account/profile", { waitUntil: "networkidle" });
  await page.getByLabel("Nombre").waitFor();
  await shot(page, `perfil-${size.name}`);
  await page.goto("http://127.0.0.1:3000/proveedores", { waitUntil: "networkidle" });
  await page.getByRole("rowheader", { name: "LinkedIn Talent Solutions" }).waitFor();
  await shot(page, `proveedores-${size.name}`);
  await context.close();
}

{
  const context = await browser.newContext({ viewport: { width: 768, height: 1024 } });
  await context.addInitScript((value) => localStorage.setItem("nexova-access-token", value), token);
  const page = await context.newPage();
  await page.route("**/suppliers**", async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 2500));
    await route.continue();
  });
  const going = page.goto("http://127.0.0.1:3000/proveedores");
  await page.getByText("Cargando contratos…").waitFor();
  await shot(page, "proveedores-carga-768");
  await going;
  await context.close();
}

{
  const context = await browser.newContext({ viewport: { width: 768, height: 1024 } });
  await context.addInitScript((value) => localStorage.setItem("nexova-access-token", value), token);
  const page = await context.newPage();
  await page.route("**/suppliers**", (route) => route.abort());
  await page.goto("http://127.0.0.1:3000/proveedores");
  await page.getByRole("heading", { name: "No se pudo cargar el directorio" }).waitFor();
  await shot(page, "proveedores-error-768");
  await context.close();
}

for (const size of [widths[0], widths[2]]) {
  const context = await browser.newContext({ viewport: { width: size.width, height: size.height } });
  await context.addInitScript(() => localStorage.setItem("nexova-access-token", "token-caducado"));
  const page = await context.newPage();
  await page.goto("http://127.0.0.1:3000/account/profile");
  await page.getByRole("heading", { name: "La sesión ha vencido" }).waitFor();
  await shot(page, `sesion-vencida-${size.name}`);
  await context.close();
}

{
  const context = await browser.newContext({
    viewport: { width: 1280, height: 800 },
    reducedMotion: "reduce",
  });
  await context.addInitScript((value) => localStorage.setItem("nexova-access-token", value), token);
  const page = await context.newPage();
  await page.goto("http://127.0.0.1:3000/", { waitUntil: "networkidle" });
  await page.getByRole("heading", { name: "Análisis de tickets de soporte" }).waitFor();
  const motion = await page.evaluate(() => document.documentElement.dataset.motion);
  if (motion !== "reduced") throw new Error(`motion ${motion}`);
  await shot(page, "incidencias-reduced-1280");
  await context.close();
}

{
  const videoDir = "/tmp/nexova-video";
  fs.mkdirSync(videoDir, { recursive: true });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 },
    recordVideo: { dir: videoDir, size: { width: 1280, height: 720 } },
  });
  const page = await context.newPage();
  await page.goto("http://127.0.0.1:3000/login");
  await page.getByRole("heading", { name: "Entrar al portal interno" }).waitFor();
  await page.waitForTimeout(1600);
  await page.getByLabel("Correo").fill(email);
  await page.getByLabel("Contraseña").fill(password);
  await page.waitForTimeout(900);
  await page.getByRole("button", { name: "Entrar" }).click();
  await page.getByRole("heading", { name: "Análisis de tickets de soporte" }).waitFor();
  await page.waitForTimeout(1800);
  await page.getByRole("link", { name: "Perfil" }).click();
  await page.getByLabel("Nombre").waitFor();
  await page.waitForTimeout(1800);
  const video = page.video();
  await context.close();
  const saved = await video.path();
  const target = path.join(outDir, "recorrido.webm");
  fs.copyFileSync(saved, target);
  console.log("video", target);
}

await browser.close();
console.log("done");
