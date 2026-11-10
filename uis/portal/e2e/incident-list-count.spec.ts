import { expect, test } from "@playwright/test";

// 016: el contador "Mostrando N incidencias con los filtros actuales." debe
// aparecer una sola vez (antes salía en el listado y en la región de estado).
const API = "http://127.0.0.1:8000";

test("el contador del listado aparece una sola vez", async ({ page, request }) => {
  const email = `contador-${Date.now()}@nexova.test`;
  const password = "clave-segura-1";
  expect((await request.post(`${API}/users`, { data: { email, password } })).status()).toBe(201);
  const token = (await (await request.post(`${API}/auth/login`, { data: { email, password } })).json())
    .access_token as string;
  const headers = { Authorization: `Bearer ${token}` };
  for (const title of ["Contador uno", "Contador dos"]) {
    const created = await request.post(`${API}/api/incidents`, {
      headers,
      data: { title, description: "Fila para contar el listado.", category: "technical_failure", status: "open", origin: "internal", branch: "central" },
    });
    expect(created.status()).toBe(201);
  }
  const total = ((await (await request.get(`${API}/api/incidents`, { headers })).json()) as unknown[]).length;

  await page.goto(`${API}/incidencias`);
  await page.evaluate((value) => sessionStorage.setItem("nexova-access-token", value), token);
  await page.reload();
  await expect(page.locator("#incident-list")).toHaveAttribute("data-state", "ready");
  const sentence = `Mostrando ${total} incidencias con los filtros actuales.`;
  await expect(page.getByText(sentence, { exact: true })).toHaveCount(1);
  // La región role=status sigue anunciándolo para lectores de pantalla.
  await expect(page.locator("#incident-list-status")).toHaveText(sentence);
});
