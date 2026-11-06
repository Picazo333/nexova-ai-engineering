import { expect, test } from "@playwright/test";

const API = "http://127.0.0.1:8000";

test("el formulario valida, resalta la sede y el panel sobrevive a un resumen fallido", async ({ page, request }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(`${API}/incidencias/nueva`);
  await page.getByRole("button", { name: "Registrar incidencia" }).click();
  await expect(page.getByText("El título es obligatorio.")).toBeVisible();
  await expect(page.getByText("La sede es obligatoria.")).toBeVisible();
  await expect(page.getByRole("button", { name: "Registrar incidencia" })).toBeEnabled();

  await page.locator("#incident-origin").selectOption("branch");
  await expect(page.locator("#branch-field")).toHaveAttribute("data-highlight", "1");
  await expect(page.getByText("Estás reportando desde una sede concreta.")).toBeVisible();
  await expect(page.locator("#incident-branch")).toContainText("Central — Sede Valencia");
  await expect(page.locator("#incident-branch")).toContainText("Remoto (empleado sin sede fija)");

  const email = `gestor-${Date.now()}@nexova.test`;
  const password = "clave-segura-1";
  const created = await request.post(`${API}/users`, {
    data: { email, password, name: "Operador Gestor" },
  });
  expect(created.status()).toBe(201);
  const logged = await request.post(`${API}/auth/login`, { data: { email, password } });
  expect(logged.status()).toBe(200);
  const token = (await logged.json()).access_token as string;

  await page.evaluate((value) => sessionStorage.setItem("nexova-access-token", value), token);
  await page.reload();
  const title = `Fallo del ATS ${Date.now()}`;
  await page.locator("#incident-title").fill(title);
  await page.locator("#incident-description").fill("El ATS no abre la ficha del candidato.");
  await page.locator("#incident-category").selectOption("technical_failure");
  await page.locator("#incident-status").selectOption("open");
  await page.locator("#incident-origin").selectOption("branch");
  await page.locator("#incident-branch").selectOption("miami_office");
  await page.getByRole("button", { name: "Registrar incidencia" }).click();
  await expect(page.getByText(/Incidencia registrada\. Identificador/)).toBeVisible();
  await expect(page.locator("#incident-title")).toHaveValue("");

  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.route("**/api/incidents/summary", (route) => route.abort());
  await page.goto(`${API}/incidencias`);
  await expect(page.locator("html")).toHaveAttribute("data-motion", "reduced");
  await expect(page.getByRole("heading", { name: "Panel de incidencias" })).toBeVisible();
  await expect(page.getByText(title).first()).toBeVisible();
  await expect(page.getByText("No se pudo cargar el resumen. El listado de abajo sigue disponible.")).toBeVisible();
  await expect(page.getByRole("button", { name: "Reintentar el resumen" })).toBeVisible();
});
