import { beginCatalog, failCatalog, settleCatalog } from "@/lib/catalog";

describe("catálogo de activos", () => {
  test("una carga conserva las filas anteriores y limpia el error", () => {
    expect(beginCatalog([{ id: 1 }])).toEqual({ phase: "loading", rows: [{ id: 1 }], error: "" });
  });

  test("una respuesta lista sustituye las filas", () => {
    expect(settleCatalog([{ id: 4 }, { id: 9 }])).toEqual({
      phase: "ready",
      rows: [{ id: 4 }, { id: 9 }],
      error: "",
    });
  });

  test("un fallo conserva las filas y guarda el mensaje", () => {
    expect(failCatalog([{ id: 4 }], "No hay conexión con la API.")).toEqual({
      phase: "error",
      rows: [{ id: 4 }],
      error: "No hay conexión con la API.",
    });
  });
});
