import { chromium } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import fs from "node:fs";
import path from "node:path";

const outDir = path.resolve("../../evidence");
const artifactDir = "/opt/cursor/artifacts";
fs.mkdirSync(outDir, { recursive: true });
fs.mkdirSync(artifactDir, { recursive: true });

const stamp = Date.now();
const email = `foto-${stamp}@nexova.test`;
const password = "clave-segura-1";
const nextPassword = "nueva-clave-9";

async function json(url, options) {
  const response = await fetch(url, options);
  const text = await response.text();
  if (!response.ok) throw new Error(`${response.status} ${url} ${text}`);
  return JSON.parse(text);
}

await json("http://127.0.0.1:8000/users", {
  method: "POST",
  headers: { "content-type": "application/json", accept: "application/json" },
  body: JSON.stringify({ email, password, name: "Ana Soler" }),
});
const access = (
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

async function prepare(page) {
  await page.addInitScript(() => {
    document.documentElement.style.scrollBehavior = "auto";
  });
}

const axeReport = [];

async function axe(page, name) {
  const results = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag22aa"])
    .analyze();
  const serious = results.violations.filter((item) => item.impact === "serious" || item.impact === "critical");
  axeReport.push({
    name,
    violations: serious.map((item) => ({
      id: item.id,
      impact: item.impact,
      help: item.help,
      nodes: item.nodes.length,
    })),
  });
  if (serious.length) {
    console.error("axe", name, JSON.stringify(serious, null, 2));
    throw new Error(`axe ${name} ${serious.map((item) => item.id).join(",")}`);
  }
  console.log("axe", name, "ok");
}

for (const size of widths) {
  const context = await browser.newContext({ viewport: { width: size.width, height: size.height } });
  const page = await context.newPage();
  await prepare(page);

  await page.goto("http://127.0.0.1:3000/login", { waitUntil: "networkidle" });
  await page.getByRole("link", { name: "¿Olvidaste tu contraseña?" }).waitFor();
  await shot(page, `restore-login-${size.name}`);
  if (size.name === "1280") await axe(page, "login");

  await page.goto("http://127.0.0.1:3000/login?notice=password-updated", { waitUntil: "networkidle" });
  await page.getByRole("heading", { name: "Contraseña actualizada" }).waitFor();
  await shot(page, `restore-login-ok-${size.name}`);

  await page.goto("http://127.0.0.1:3000/forgot-password", { waitUntil: "networkidle" });
  await page.getByRole("heading", { name: "Recuperar la contraseña" }).waitFor();
  await shot(page, `restore-forgot-idle-${size.name}`);
  if (size.name === "1280") await axe(page, "forgot-idle");

  let releaseLoading = () => {};
  const loadingDone = new Promise((resolve) => {
    releaseLoading = resolve;
  });
  await page.route("**/auth/forgot-password", async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 1500));
    try {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          message: "Si esa dirección está registrada, recibirás un enlace en breve.",
        }),
      });
    } catch {
      /* The screenshot already ran; a late duplicate must not abort the pass. */
    } finally {
      releaseLoading();
    }
  });
  await page.getByLabel("Correo").fill("ana@nexova.test");
  await page.getByRole("button", { name: "Enviar enlace" }).click();
  await page.getByText("Enviando la solicitud…").waitFor();
  await shot(page, `restore-forgot-loading-${size.name}`);
  await loadingDone;
  await page.unroute("**/auth/forgot-password");

  await page.goto("http://127.0.0.1:3000/forgot-password", { waitUntil: "networkidle" });
  await page.route("**/auth/forgot-password", (route) => route.abort());
  await page.getByLabel("Correo").fill(email);
  await page.getByRole("button", { name: "Enviar enlace" }).click();
  await page.getByRole("heading", { name: "No se pudo enviar" }).waitFor();
  await shot(page, `restore-forgot-error-${size.name}`);
  await page.unroute("**/auth/forgot-password");

  await page.goto("http://127.0.0.1:3000/forgot-password", { waitUntil: "networkidle" });
  await page.getByLabel("Correo").fill("nadie@nexova.test");
  await page.getByRole("button", { name: "Enviar enlace" }).click();
  await page.getByRole("heading", { name: "Solicitud registrada" }).waitFor();
  await shot(page, `restore-forgot-success-${size.name}`);
  if (size.name === "1280") await axe(page, "forgot-success");

  await page.goto("http://127.0.0.1:3000/reset-password", { waitUntil: "networkidle" });
  await page.getByRole("heading", { name: "Falta el enlace de recuperación" }).waitFor();
  await shot(page, `restore-reset-empty-${size.name}`);
  if (size.name === "1280") await axe(page, "reset-empty");

  async function dead(code, heading, message, file) {
    await page.goto(`http://127.0.0.1:3000/reset-password?token=${code}`, { waitUntil: "networkidle" });
    await page.route("**/auth/reset-password", async (route) => {
      await route.fulfill({
        status: 400,
        contentType: "application/json",
        body: JSON.stringify({
          error: "http_error",
          message,
          detail: message,
          code,
        }),
      });
    });
    await page.getByLabel("Nueva contraseña").fill(nextPassword);
    await page.getByLabel("Confirmación").fill(nextPassword);
    await page.getByRole("button", { name: "Guardar contraseña" }).click();
    await page.getByRole("heading", { name: heading }).waitFor();
    await shot(page, file);
    await page.unroute("**/auth/reset-password");
  }

  await dead(
    "expired",
    "El enlace ha caducado",
    "El enlace ha caducado. Pide otro.",
    `restore-reset-expired-${size.name}`,
  );
  await dead(
    "used",
    "Este enlace ya se usó",
    "Este enlace ya se usó. Pide otro.",
    `restore-reset-used-${size.name}`,
  );
  if (size.name === "1280") await axe(page, "reset-used");

  await page.goto("http://127.0.0.1:3000/login");
  await page.evaluate((token) => localStorage.setItem("nexova-access-token", token), access);
  await page.goto("http://127.0.0.1:3000/account/change-password", { waitUntil: "networkidle" });
  await page.getByRole("heading", { name: "Cambiar la contraseña" }).waitFor();
  await shot(page, `restore-change-idle-${size.name}`);
  if (size.name === "1280") await axe(page, "change-idle");
  await page.getByLabel("Contraseña actual").fill("clave-erronea");
  await page.getByLabel("Nueva contraseña").fill(nextPassword);
  await page.getByLabel("Confirmación").fill(nextPassword);
  await page.getByRole("button", { name: "Cambiar contraseña" }).click();
  await page.locator("#change-current-error").waitFor();
  await shot(page, `restore-change-error-${size.name}`);

  await context.close();
}

{
  const context = await browser.newContext({
    viewport: { width: 1280, height: 800 },
    reducedMotion: "reduce",
  });
  const page = await context.newPage();
  await page.goto("http://127.0.0.1:3000/forgot-password", { waitUntil: "networkidle" });
  let releaseReduced = () => {};
  const reducedDone = new Promise((resolve) => {
    releaseReduced = resolve;
  });
  await page.route("**/auth/forgot-password", async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 1500));
    try {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          message: "Si esa dirección está registrada, recibirás un enlace en breve.",
        }),
      });
    } catch {
      /* Same late-handler guard as the loading shots. */
    } finally {
      releaseReduced();
    }
  });
  await page.getByLabel("Correo").fill("ana@nexova.test");
  await page.getByRole("button", { name: "Enviar enlace" }).click();
  await page.getByText("Enviando la solicitud…").waitFor();
  const motion = await page.locator(".loading-mark").evaluate((element) => ({
    animationName: getComputedStyle(element).animationName,
    dataset: document.documentElement.dataset.motion || "",
  }));
  fs.writeFileSync(path.join(outDir, "restore-reduced-motion.txt"), JSON.stringify(motion, null, 2));
  if (motion.animationName !== "none") throw new Error(`reduced motion animates ${motion.animationName}`);
  await shot(page, "restore-reduced-1280");
  await reducedDone;
  await context.close();
}

{
  const context = await browser.newContext({
    viewport: { width: 1280, height: 800 },
    recordVideo: { dir: outDir, size: { width: 1280, height: 800 } },
  });
  const page = await context.newPage();
  await page.goto("http://127.0.0.1:3000/login", { waitUntil: "networkidle" });
  await page.waitForTimeout(700);
  await page.getByRole("link", { name: "¿Olvidaste tu contraseña?" }).click();
  await page.getByLabel("Correo").fill(email);
  await page.waitForTimeout(600);
  await page.getByRole("button", { name: "Enviar enlace" }).click();
  await page.getByRole("heading", { name: "Solicitud registrada" }).waitFor();
  await page.waitForTimeout(900);
  const link = fs.readFileSync("/tmp/nexova-014-evidence/reset-link.txt", "utf8").trim();
  await page.goto("http://127.0.0.1:3000/reset-password");
  await page.getByRole("heading", { name: "Falta el enlace de recuperación" }).waitFor();
  await page.waitForTimeout(800);
  await page.goto(link);
  await page.getByLabel("Nueva contraseña").fill(nextPassword);
  await page.getByLabel("Confirmación").fill(nextPassword);
  await page.waitForTimeout(500);
  await page.getByRole("button", { name: "Guardar contraseña" }).click();
  await page.getByRole("heading", { name: "Contraseña actualizada" }).waitFor();
  await page.waitForTimeout(1100);
  await context.close();
  const video = page.video();
  const saved = video ? await video.path() : "";
  const target = path.join(outDir, "restore-recorrido.webm");
  if (saved) fs.copyFileSync(saved, target);
  fs.copyFileSync(target, path.join(artifactDir, "restore-recorrido.webm"));
  console.log("video", target);
}

const axePath = path.join(outDir, "axe.json");
fs.writeFileSync(axePath, JSON.stringify({ project: "ai-eng-user-authentication-restore", pages: axeReport }, null, 2));
fs.copyFileSync(axePath, path.join(artifactDir, "axe.json"));
await browser.close();
console.log("capture done");
