import { expect, test, type APIRequestContext, type Page, type Route } from "@playwright/test";

// Rúbrica 016 (ai-eng-centralized-incident-manager), «Qué evaluaremos › Frontend».
// El backoffice lo sirve la API en :8000.
const API = "http://127.0.0.1:8000";
const TECHNICAL = /Traceback|psycopg|pydantic|value_error|\/srv\/|Internal Server Error|Unexpected token/;

async function session(page: Page, request: APIRequestContext): Promise<string> {
  const email = `c14-${Date.now()}-${Math.random().toString(16).slice(2)}@nexova.test`;
  const password = "clave-segura-1";
  expect((await request.post(`${API}/users`, { data: { email, password } })).status()).toBe(201);
  const token = (await (await request.post(`${API}/auth/login`, { data: { email, password } })).json())
    .access_token as string;
  await page.goto(`${API}/incidencias/nueva`);
  await page.evaluate((value) => sessionStorage.setItem("nexova-access-token", value), token);
  return token;
}

async function fillForm(page: Page, title: string) {
  await page.locator("#incident-title").fill(title);
  await page.locator("#incident-description").fill("Prueba de criterios C14 a C17.");
  await page.locator("#incident-category").selectOption("technical_failure");
  await page.locator("#incident-status").selectOption("open");
  await page.locator("#incident-origin").selectOption("internal");
  await page.locator("#incident-branch").selectOption("central");
}

function hold(): { wait: Promise<void>; release: () => void } {
  let release = () => {};
  const wait = new Promise<void>((resolve) => (release = resolve));
  return { wait, release };
}

test("C14 — Los estados de carga son visibles y el botón de envío queda deshabilitado durante la petición.", async ({ page, request }) => {
  await session(page, request);
  await page.reload();
  const gate = hold();
  await page.route("**/api/incidents", async (route: Route) => {
    if (route.request().method() !== "POST") return route.continue();
    await gate.wait;
    await route.continue();
  });
  await fillForm(page, `C14 carga ${Date.now()}`);
  const submit = page.locator("#incident-submit");
  await submit.click();
  // Mientras la petición sigue abierta:
  await expect(submit).toBeDisabled();
  await expect(submit).toHaveAttribute("aria-busy", "true");
  await expect(submit).toHaveText("Guardando…");
  await expect(page.locator("#incident-form-status")).toHaveText("Enviando la incidencia…");
  gate.release();
  // Al terminar, el botón vuelve y la confirmación aparece.
  await expect(page.getByText(/Incidencia registrada\. Identificador/)).toBeVisible();
  await expect(submit).toBeEnabled();
  await expect(submit).toHaveAttribute("aria-busy", "false");
});

test("C15 — Los errores de la API se muestran en lenguaje comprensible para el usuario, nunca como texto técnico.", async ({ page, request }) => {
  await session(page, request);
  await page.reload();
  // (a) 400 real de la API: se cambia la categoría por un valor no permitido en el cuerpo enviado.
  await page.route("**/api/incidents", async (route: Route) => {
    if (route.request().method() !== "POST") return route.continue();
    const body = JSON.parse(route.request().postData() || "{}");
    body.category = "categoria_inexistente";
    await route.continue({ postData: JSON.stringify(body) });
  });
  await fillForm(page, `C15 400 ${Date.now()}`);
  const api400 = page.waitForResponse((r) => r.url().endsWith("/api/incidents") && r.request().method() === "POST");
  await page.locator("#incident-submit").click();
  expect((await api400).status()).toBe(400);
  await expect(page.locator("#incident-form-error")).toHaveText("Revisa los campos marcados.");
  // El mensaje va junto al campo que la API señala.
  await expect(page.locator("#category-error")).toBeVisible();
  await expect(page.locator("#category-error")).toContainText(/categor/i);
  await expect(page.locator("#incident-category")).toHaveAttribute("aria-invalid", "true");
  await expect(page.locator("#category-error")).not.toContainText(TECHNICAL);
  await expect(page.locator("main")).not.toContainText(TECHNICAL);

  // (b) 500 con cuerpo técnico: el usuario ve una frase y no el detalle.
  await page.unroute("**/api/incidents");
  await page.route("**/api/incidents", async (route: Route) => {
    if (route.request().method() !== "POST") return route.continue();
    await route.fulfill({
      status: 500,
      contentType: "application/json",
      body: JSON.stringify({ detail: "Traceback (most recent call last): psycopg2.OperationalError /srv/app/db.py" }),
    });
  });
  await fillForm(page, `C15 500 ${Date.now()}`);
  await page.locator("#incident-submit").click();
  await expect(page.locator("#incident-form-error")).toHaveText("No se pudo registrar la incidencia. Inténtalo de nuevo.");
  await expect(page.locator("main")).not.toContainText(TECHNICAL);
});

test("C16 — El listado gestiona correctamente los tres estados posibles: cargando, vacío, con datos.", async ({ page, request }) => {
  const token = await session(page, request);
  await request.post(`${API}/api/incidents`, {
    headers: { Authorization: `Bearer ${token}` },
    data: { title: `C16 datos ${Date.now()}`, description: "Fila para el estado con datos.", category: "process_error", status: "open", origin: "internal", branch: "central" },
  });
  const list = page.locator("#incident-list");
  const isList = (route: Route) => route.request().method() === "GET" && /\/api\/incidents(\?.*)?$/.test(route.request().url());

  // Cargando: la respuesta se retiene.
  const gate = hold();
  await page.route(/\/api\/incidents(\?.*)?$/, async (route) => {
    if (!isList(route)) return route.continue();
    await gate.wait;
    await route.continue();
  });
  await page.goto(`${API}/incidencias`);
  await expect(list).toHaveAttribute("data-state", "loading");
  await expect(list).toHaveAttribute("aria-busy", "true");
  await expect(page.locator("#incident-list-status")).toHaveText("Cargando incidencias…");
  // Con datos: la misma petición se libera contra la API real.
  gate.release();
  await expect(list).toHaveAttribute("data-state", "ready");
  await expect(list.locator("tbody tr").first()).toBeVisible();

  // Vacío: la API devuelve una lista vacía.
  await page.unroute(/\/api\/incidents(\?.*)?$/);
  await page.route(/\/api\/incidents(\?.*)?$/, async (route) => {
    if (!isList(route)) return route.continue();
    await route.fulfill({ status: 200, contentType: "application/json", body: "[]" });
  });
  await page.reload();
  await expect(list).toHaveAttribute("data-state", "empty");
  await expect(list).toContainText("Sin incidencias para mostrar");
  await expect(list.locator("table")).toHaveCount(0);
});

test("C17 — La actualización de estado en el listado revierte visualmente si la petición falla.", async ({ page, request }) => {
  const token = await session(page, request);
  const created = await request.post(`${API}/api/incidents`, {
    headers: { Authorization: `Bearer ${token}` },
    data: { title: `C17 revertir ${Date.now()}`, description: "Fila para la reversión.", category: "technical_failure", status: "open", origin: "internal", branch: "central" },
  });
  expect(created.status()).toBe(201);
  const id = (await created.json()).id as string;
  for (const failure of ["500", "abort"] as const) {
    await page.route(`**/api/incidents/${id}/status`, (route) =>
      failure === "500"
        ? route.fulfill({ status: 500, contentType: "application/json", body: JSON.stringify({ detail: "Traceback boom" }) })
        : route.abort(),
    );
    await page.goto(`${API}/incidencias`);
    const select = page.locator(`#status-${id}`);
    await expect(select).toHaveValue("open");
    await select.selectOption("in_progress");
    await expect(select).toHaveValue("open");
    await expect(page.locator("#incident-list-error")).toBeVisible();
    await expect(page.locator("#incident-list-error")).toContainText("Se ha recuperado el valor anterior.");
    await expect(select).toBeEnabled();
    await page.unroute(`**/api/incidents/${id}/status`);
  }
  // Sin fallo, el cambio se mantiene (control de que la prueba no pasa siempre).
  await page.goto(`${API}/incidencias`);
  const select = page.locator(`#status-${id}`);
  await select.selectOption("in_progress");
  await expect(page.locator(`#status-${id}`)).toHaveValue("in_progress");
});
