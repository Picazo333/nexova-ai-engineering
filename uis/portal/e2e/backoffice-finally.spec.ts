import { expect, test } from "@playwright/test";

// Rubric 017: the backoffice clears its loading state in `finally`,
// whatever the outcome of the request (here: network aborted).
const API = "http://127.0.0.1:8000";

test("el backoffice limpia aria-busy aunque la red falle", async ({ page, request }) => {
  const email = `finally-${Date.now()}@nexova.test`;
  const password = "clave-segura-1";
  expect((await request.post(`${API}/users`, { data: { email, password } })).status()).toBe(201);
  const token = (await (await request.post(`${API}/auth/login`, { data: { email, password } })).json())
    .access_token as string;

  await page.goto(`${API}/incidencias`);
  await page.evaluate((value) => sessionStorage.setItem("nexova-access-token", value), token);
  await page.route("**/api/incidents/summary", (route) => route.abort());
  await page.route(/\/api\/incidents(\?.*)?$/, (route) => route.abort());
  await page.reload();
  await expect(page.locator("#incident-summary")).toHaveAttribute("aria-busy", "false");
  await expect(page.locator("#incident-list")).toHaveAttribute("aria-busy", "false");

  await page.goto(`${API}/incidencias/nueva`);
  await page.locator("#incident-title").fill("Fallo de red simulado");
  await page.locator("#incident-description").fill("La petición se aborta a propósito.");
  await page.locator("#incident-category").selectOption("technical_failure");
  await page.locator("#incident-status").selectOption("open");
  await page.locator("#incident-origin").selectOption("internal");
  await page.locator("#incident-branch").selectOption("central");
  await page.getByRole("button", { name: "Registrar incidencia" }).click();
  await expect(page.getByText("No hay conexión con la API. Los datos del formulario se conservan.")).toBeVisible();
  const submit = page.locator("#incident-submit");
  await expect(submit).toBeEnabled();
  await expect(submit).toHaveAttribute("aria-busy", "false");
  await expect(page.locator("#incident-title")).toHaveValue("Fallo de red simulado");
});
