import { expect, test } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";

const root = path.resolve(__dirname, "../../..");

test("el website público no redirige a login ni guarda el token", async ({ page, request }) => {
  for (const file of ["index.html", "application.html", "404.html"]) {
    const body = fs.readFileSync(path.join(root, file), "utf8");
    expect(body).not.toContain("nexova-access-token");
    expect(body).not.toContain("/login");
    expect(body).not.toContain("localStorage");
  }
  const home = await request.get("http://127.0.0.1:4173/index.html");
  expect(home.status()).toBe(200);
  const html = await home.text();
  expect(html).toContain("Nexova");
  expect(html).not.toContain("/login");
  const application = await request.get("http://127.0.0.1:4173/application.html");
  expect(application.status()).toBe(200);

  await page.goto("http://127.0.0.1:4173/index.html");
  await expect(page).toHaveURL("http://127.0.0.1:4173/index.html");
  await expect(page).not.toHaveURL(/\/login/);
});

test("las rutas HTML de la API siguen públicas y no saltan al portal", async ({ request }) => {
  const home = await request.get("http://127.0.0.1:8000/");
  expect(home.status()).toBe(200);
  const homeHtml = await home.text();
  expect(homeHtml).toContain("Análisis de incidencias de soporte");
  expect(homeHtml).toContain("Nexova");
  expect(homeHtml).not.toContain("127.0.0.1:3000/login");

  const privacy = await request.get("http://127.0.0.1:8000/privacidad");
  expect(privacy.status()).toBe(200);
  expect(await privacy.text()).toContain("Privacidad");

  const directory = await request.get("http://127.0.0.1:8000/proveedores");
  expect(directory.status()).toBe(200);
  const directoryHtml = await directory.text();
  expect(directoryHtml).toContain("Backoffice");
  expect(directoryHtml).not.toContain("127.0.0.1:3000/login");
});
