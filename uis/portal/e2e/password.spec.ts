import { expect, test, type Page } from "@playwright/test";
import fs from "node:fs";

const CAPTURE = "/tmp/nexova-014-e2e/reset-link.txt";

function account() {
  const stamp = `${Date.now()}-${Math.floor(Math.random() * 1000)}`;
  return {
    email: `restore-${stamp}@nexova.test`,
    password: "clave-segura-1",
    name: "Ana Soler",
  };
}

async function createAccount(page: Page, person: ReturnType<typeof account>) {
  const response = await page.request.post("http://127.0.0.1:8000/users", {
    data: person,
  });
  expect(response.ok()).toBeTruthy();
}

test("login muestra el enlace y la recuperación no distingue correos", async ({ page }) => {
  const person = account();
  await createAccount(page, person);
  await page.goto("/login");
  const link = page.getByRole("link", { name: "¿Olvidaste tu contraseña?" });
  await expect(link).toBeVisible();
  await link.click();
  await expect(page).toHaveURL(/\/forgot-password$/);
  await page.getByLabel("Correo").fill("nadie@nexova.test");
  await page.getByRole("button", { name: "Enviar enlace" }).click();
  await expect(
    page.getByText("Si esa dirección está registrada, recibirás un enlace en breve."),
  ).toBeVisible();
  await expect(page.getByLabel("Correo")).toBeDisabled();
  await expect(page.getByRole("button", { name: "Enviar enlace" })).toBeDisabled();
});

test("el enlace mock restablece la contraseña y el cambio exige la actual", async ({ page }) => {
  const person = account();
  await createAccount(page, person);

  await page.goto("/forgot-password");
  await page.getByLabel("Correo").fill(person.email);
  await page.getByRole("button", { name: "Enviar enlace" }).click();
  await expect(page.getByRole("heading", { name: "Solicitud registrada" })).toBeVisible();
  const link = fs.readFileSync(CAPTURE, "utf8").trim();
  expect(link).toContain("/reset-password?token=");
  expect(link).not.toContain(person.password);

  await page.goto("/reset-password");
  await expect(page.getByRole("heading", { name: "Falta el enlace de recuperación" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Pedir un enlace" })).toHaveAttribute("href", "/forgot-password");

  await page.goto("/reset-password?token=no-es-un-token");
  await page.getByLabel("Nueva contraseña").fill("nueva-clave-9");
  await page.getByLabel("Confirmación").fill("otra-distinta");
  let called = false;
  await page.route("**/auth/reset-password", async (route) => {
    called = true;
    await route.continue();
  });
  await page.getByRole("button", { name: "Guardar contraseña" }).click();
  expect(called).toBe(false);
  await expect(page.getByText("no coincide")).toBeVisible();
  await expect(page.getByLabel("Nueva contraseña")).toHaveValue("nueva-clave-9");

  await page.getByLabel("Confirmación").fill("nueva-clave-9");
  await page.getByRole("button", { name: "Guardar contraseña" }).click();
  await expect(page.getByRole("heading", { name: "El enlace no es válido" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Pedir otro enlace" })).toHaveAttribute("href", "/forgot-password");

  await page.unroute("**/auth/reset-password");
  await page.goto(link);
  await page.getByLabel("Nueva contraseña").fill("nueva-clave-9");
  await page.getByLabel("Confirmación").fill("nueva-clave-9");
  await page.getByRole("button", { name: "Guardar contraseña" }).click();
  await expect(page).toHaveURL(/\/login\?notice=password-updated/);
  await expect(page.getByRole("heading", { name: "Contraseña actualizada" })).toBeVisible();

  await page.getByLabel("Correo").fill(person.email);
  await page.getByLabel("Contraseña").fill(person.password);
  await page.getByRole("button", { name: "Entrar" }).click();
  await expect(page.locator(".alert")).toContainText("no son válidos");

  await page.getByLabel("Contraseña").fill("nueva-clave-9");
  await page.getByRole("button", { name: "Entrar" }).click();
  await expect(page).toHaveURL("http://127.0.0.1:3000/");

  await page.goto("/account/change-password");
  await expect(page.getByRole("heading", { name: "Cambiar la contraseña" })).toBeVisible();
  await page.getByLabel("Contraseña actual").fill("clave-erronea");
  await page.getByLabel("Nueva contraseña").fill("otra-clave-99");
  await page.getByLabel("Confirmación").fill("otra-clave-99");
  await page.getByRole("button", { name: "Cambiar contraseña" }).click();
  await expect(page.locator("#change-current-error")).toContainText("no es correcta");
  await expect(page.getByLabel("Contraseña actual")).toHaveValue("clave-erronea");

  await page.getByLabel("Nueva contraseña").fill("otra-clave-99");
  await page.getByLabel("Confirmación").fill("distinta-1");
  await page.getByRole("button", { name: "Cambiar contraseña" }).click();
  await expect(page.locator("#change-password-error")).toContainText("no coincide");

  await page.getByLabel("Contraseña actual").fill("nueva-clave-9");
  await page.getByLabel("Confirmación").fill("otra-clave-99");
  await page.getByRole("button", { name: "Cambiar contraseña" }).click();
  await expect(page.getByText("La contraseña se ha actualizado.")).toBeVisible();

  await page.getByRole("button", { name: "Cerrar sesión" }).click();
  await page.getByLabel("Correo").fill(person.email);
  await page.getByLabel("Contraseña").fill("otra-clave-99");
  await page.getByRole("button", { name: "Entrar" }).click();
  await expect(page).toHaveURL("http://127.0.0.1:3000/");
});

test("un enlace caducado o ya usado ofrece otro", async ({ page }) => {
  await page.goto("/reset-password?token=caducado");
  await page.route("**/auth/reset-password", async (route) => {
    await route.fulfill({
      status: 400,
      contentType: "application/json",
      body: JSON.stringify({
        error: "http_error",
        message: "El enlace ha caducado. Pide otro.",
        detail: "El enlace ha caducado. Pide otro.",
        code: "expired",
      }),
    });
  });
  await page.getByLabel("Nueva contraseña").fill("nueva-clave-9");
  await page.getByLabel("Confirmación").fill("nueva-clave-9");
  await page.getByRole("button", { name: "Guardar contraseña" }).click();
  await expect(page.getByRole("heading", { name: "El enlace ha caducado" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Pedir otro enlace" })).toBeVisible();

  await page.goto("/reset-password?token=usado");
  await page.unroute("**/auth/reset-password");
  await page.route("**/auth/reset-password", async (route) => {
    await route.fulfill({
      status: 400,
      contentType: "application/json",
      body: JSON.stringify({
        error: "http_error",
        message: "Este enlace ya se usó. Pide otro.",
        detail: "Este enlace ya se usó. Pide otro.",
        code: "used",
      }),
    });
  });
  await page.getByLabel("Nueva contraseña").fill("nueva-clave-9");
  await page.getByLabel("Confirmación").fill("nueva-clave-9");
  await page.getByRole("button", { name: "Guardar contraseña" }).click();
  await expect(page.getByRole("heading", { name: "Este enlace ya se usó" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Pedir otro enlace" })).toHaveAttribute("href", "/forgot-password");
});

test("reduced motion deja el indicador de carga quieto", async ({ browser }) => {
  const context = await browser.newContext({ reducedMotion: "reduce" });
  const page = await context.newPage();
  await page.goto("/forgot-password");
  await page.route("**/auth/forgot-password", async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 600));
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        message: "Si esa dirección está registrada, recibirás un enlace en breve.",
      }),
    });
  });
  await page.getByLabel("Correo").fill("ana@nexova.test");
  const pending = page.getByRole("button", { name: "Enviar enlace" }).click();
  await page.locator(".loading-mark").waitFor();
  const animation = await page.locator(".loading-mark").evaluate((element) => getComputedStyle(element).animationName);
  expect(animation).toBe("none");
  await pending;
  await context.close();
});
