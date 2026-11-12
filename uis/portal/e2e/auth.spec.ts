import { expect, test, type Page } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";

const TOKEN_KEY = "nexova-access-token";

function account() {
  const stamp = `${Date.now()}-${Math.floor(Math.random() * 1000)}`;
  return {
    email: `portal-${stamp}@nexova.test`,
    password: "clave-segura-1",
    name: "Ana Soler",
    phone: "600111222",
    address: "Calle de Colón 1, Valencia",
  };
}

async function register(page: Page, person = account()) {
  await page.goto("/register");
  await page.getByLabel("Correo").fill(person.email);
  await page.getByLabel("Contraseña").fill(person.password);
  await page.getByLabel("Nombre").fill(person.name);
  await page.getByLabel("Teléfono").fill(person.phone);
  await page.getByLabel("Dirección").fill(person.address);
  await page.getByRole("button", { name: "Crear cuenta" }).click();
  await expect(page).toHaveURL("http://127.0.0.1:3000/");
  await expect(page.getByRole("heading", { name: "Análisis de tickets de soporte" })).toBeVisible();
  const token = await page.evaluate((key) => localStorage.getItem(key), TOKEN_KEY);
  expect(token).toBeTruthy();
  return person;
}

test("no hay middleware de Next para leer localStorage", () => {
  expect(fs.existsSync(path.join(__dirname, "../middleware.ts"))).toBe(false);
  expect(fs.existsSync(path.join(__dirname, "../src/middleware.ts"))).toBe(false);
});

test("el registro guarda el token y el perfil muestra los datos de la API", async ({ page }) => {
  const person = await register(page);
  const me = page.waitForRequest((request) => request.url().endsWith("/auth/me") && request.method() === "GET");
  await page.goto("/account/profile");
  const request = await me;
  expect(request.headers().authorization).toMatch(/^Bearer\s+\S+/);
  await expect(page.locator(".meta dd", { hasText: person.email })).toBeVisible();
  await expect(page.getByLabel("Nombre")).toHaveValue(person.name);
  await expect(page.getByLabel("Teléfono")).toHaveValue(person.phone);
  await expect(page.getByLabel("Dirección")).toHaveValue(person.address);

  const saved = page.waitForRequest(
    (request) => request.url().endsWith("/profiles/me") && request.method() === "PUT",
  );
  await page.getByLabel("Teléfono").fill("600999888");
  await page.getByRole("button", { name: "Guardar perfil" }).click();
  const put = await saved;
  expect(put.headers().authorization).toMatch(/^Bearer\s+\S+/);
  await expect(page.getByText("Perfil actualizado.")).toBeVisible();
  await page.reload();
  await expect(page.getByLabel("Teléfono")).toHaveValue("600999888");
});

test("el login fallido conserva la contraseña y el registro muestra errores de campo", async ({ page }) => {
  await page.goto("/login");
  await page.getByLabel("Correo").fill("nadie@nexova.test");
  await page.getByLabel("Contraseña").fill("clave-erronea");
  await page.getByRole("button", { name: "Entrar" }).click();
  await expect(page.locator(".alert")).toContainText("no son válidos");
  await expect(page.getByLabel("Contraseña")).toHaveValue("clave-erronea");
  await expect(page.getByLabel("Correo")).toHaveValue("nadie@nexova.test");

  await page.goto("/register");
  await page.getByLabel("Correo").fill("mal");
  await page.getByLabel("Contraseña").fill("corta");
  await page.getByRole("button", { name: "Crear cuenta" }).click();
  await expect(page.locator("#register-email-error")).toContainText("formato válido");
  await expect(page.locator("#register-password-error")).toContainText("8 caracteres");
  await expect(page.getByLabel("Contraseña")).toHaveValue("corta");
});

test("un correo repetido marca el campo", async ({ page }) => {
  const person = account();
  await register(page, person);
  await page.getByRole("button", { name: "Cerrar sesión" }).click();
  await page.goto("/register");
  await page.getByLabel("Correo").fill(person.email);
  await page.getByLabel("Contraseña").fill(person.password);
  await page.getByRole("button", { name: "Crear cuenta" }).click();
  await expect(page.locator("#register-email-error")).toContainText("Ya existe una cuenta");
});

test("sin token la vista protegida va a login y no muestra contratos", async ({ page }) => {
  await page.goto("/proveedores");
  await expect(page).toHaveURL(/\/login\?next=/);
  await expect(page.getByRole("heading", { name: "La sesión ha vencido" })).toHaveCount(0);
  await expect(page.getByText("LinkedIn Talent Solutions")).toHaveCount(0);
});

test("un 401 limpia la sesión y al entrar se vuelve a la vista protegida", async ({ page }) => {
  const person = await register(page);
  await page.evaluate((key) => localStorage.setItem(key, "token-caducado"), TOKEN_KEY);
  await page.goto("/account/profile");
  await expect(page).toHaveURL(/reason=expired/);
  await expect(page).toHaveURL(/account%2Fprofile|account\/profile/);
  await expect(page.getByRole("heading", { name: "La sesión ha vencido" })).toBeVisible();
  await expect(page.getByText("tu perfil")).toBeVisible();
  expect(await page.evaluate((key) => localStorage.getItem(key), TOKEN_KEY)).toBeNull();

  await page.getByLabel("Correo").fill(person.email);
  await page.getByLabel("Contraseña").fill(person.password);
  await page.getByRole("button", { name: "Entrar" }).click();
  await expect(page).toHaveURL(/\/account\/profile$/);
  await expect(page.locator(".meta dd", { hasText: person.email })).toBeVisible();
});

test("el logout borra el token y la vista protegida vuelve a pedir login", async ({ page }) => {
  await register(page);
  await page.getByRole("link", { name: "Proveedores" }).click();
  await expect(page.getByRole("heading", { name: "Contratos de proveedores" })).toBeVisible();
  await expect(page.getByRole("rowheader", { name: "LinkedIn Talent Solutions" })).toBeVisible();
  await page.getByRole("button", { name: "Cerrar sesión" }).click();
  await expect(page).toHaveURL(/\/login$/);
  expect(await page.evaluate((key) => localStorage.getItem(key), TOKEN_KEY)).toBeNull();
  await page.goto("/");
  await expect(page).toHaveURL(/\/login\?next=/);
  await expect(page.getByRole("heading", { name: "Análisis de tickets de soporte" })).toHaveCount(0);
});
