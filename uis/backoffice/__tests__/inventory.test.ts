import { readdirSync, readFileSync, statSync } from "node:fs";
import path from "node:path";

import { loginRedirect, safeNext } from "@/lib/paths";
import { parseQuantity } from "@/lib/quantity";
import { LOW_STOCK_BELOW, stockLabel, stockLevel } from "@/lib/stock";
import { clearToken, readToken, writeToken } from "@/lib/session";

const memory = new Map<string, string>();

const localStorageMock = {
  getItem: (key: string) => memory.get(key) ?? null,
  setItem: (key: string, value: string) => {
    memory.set(key, value);
  },
  removeItem: (key: string) => {
    memory.delete(key);
  },
};

Object.defineProperty(global, "localStorage", { value: localStorageMock, configurable: true });
Object.defineProperty(global, "window", {
  value: {
    localStorage: localStorageMock,
    location: { pathname: "/backoffice/inventory/orders/outbound", search: "?asset=1", assign: jest.fn() },
  },
  configurable: true,
});

describe("sesión y guard de ruta", () => {
  beforeEach(() => {
    memory.clear();
  });

  test("la clave del token es la de la sesión existente", () => {
    expect(writeToken("jwt-demo")).toBe(true);
    expect(readToken()).toBe("jwt-demo");
    expect(memory.get("nexova-access-token")).toBe("jwt-demo");
    clearToken();
    expect(readToken()).toBe("");
  });

  test("sin token, las cuatro páginas redirigen al login y conservan la ruta", () => {
    expect(loginRedirect("/backoffice/inventory/products", "", "")).toBe(
      "/login?next=" + encodeURIComponent("/backoffice/inventory/products"),
    );
    expect(loginRedirect("/backoffice/inventory/orders/inbound", "?asset=4", "")).toContain("inbound");
    expect(loginRedirect("/backoffice/inventory/orders/outbound", "", "")).toContain("outbound");
    expect(loginRedirect("/backoffice/inventory/orders", "?office=Valencia", "")).toContain("office%3DValencia");
  });

  test("con token no redirige, y el panel público tampoco", () => {
    expect(loginRedirect("/backoffice/inventory/products", "", "jwt")).toBeNull();
    expect(loginRedirect("/", "", "")).toBeNull();
    expect(loginRedirect("/login", "", "")).toBeNull();
  });

  test("safeNext solo acepta rutas de inventario", () => {
    expect(safeNext(null)).toBe("/backoffice/inventory/products");
    expect(safeNext("/backoffice/inventory/orders/outbound?asset=2")).toBe(
      "/backoffice/inventory/orders/outbound?asset=2",
    );
    expect(safeNext("https://evil.example/phish")).toBe("/backoffice/inventory/products");
    expect(safeNext("//evil.example")).toBe("/backoffice/inventory/products");
    expect(safeNext("/proveedores")).toBe("/backoffice/inventory/products");
  });
});

describe("umbrales de stock", () => {
  test("0 sin stock, por debajo de 10 bajo, desde 10 saludable", () => {
    expect(LOW_STOCK_BELOW).toBe(10);
    expect(stockLevel(0)).toBe("out");
    expect(stockLevel(6)).toBe("low");
    expect(stockLevel(12)).toBe("healthy");
    expect(stockLabel("out")).toBe("Sin stock");
    expect(stockLabel("low")).toBe("Bajo");
    expect(stockLabel("healthy")).toBe("Saludable");
  });

  test("la cantidad solo acepta enteros positivos", () => {
    expect(parseQuantity("1")).toBe(1);
    expect(parseQuantity("0")).toBeNull();
    expect(parseQuantity("1.5")).toBeNull();
    expect(parseQuantity("-3")).toBeNull();
    expect(parseQuantity("")).toBeNull();
  });
});

describe("lib/inventory y errores HTTP", () => {
  beforeEach(() => {
    memory.clear();
    writeToken("jwt-demo");
    jest.restoreAllMocks();
  });

  function mockResponse(status: number, body: unknown): void {
    const text = body == null ? "" : JSON.stringify(body);
    jest.spyOn(global, "fetch").mockResolvedValue({
      ok: status >= 200 && status < 300,
      status,
      text: async () => text,
    } as Response);
  }

  test("manda Authorization Bearer y no envía user_uuid ni current_stock", async () => {
    mockResponse(201, {
      id: 9,
      order_type: "outbound",
      asset_id: 1,
      asset_name: 'Laptop 14" Business',
      asset_sku: "NXV-IT-001",
      asset_category: "hardware",
      quantity: 1,
      office: "Valencia",
      created_at: "2026-03-02T09:00:00Z",
      user_uuid: "user-1",
      supplier: null,
      exit_type: "allocation",
      assigned_to: "NXV-EMP-1042",
    });
    const { createAssetExit } = await import("@/lib/inventory");
    await createAssetExit({
      asset_id: 1,
      quantity: 1,
      exit_type: "allocation",
      assigned_to: "NXV-EMP-1042",
      office: "Valencia",
    });
    const [url, init] = (fetch as jest.Mock).mock.calls[0];
    expect(url).toBe("http://127.0.0.1:8000/inventory/orders/outbound");
    const headers = init.headers as Headers;
    expect(headers.get("Authorization")).toBe("Bearer jwt-demo");
    const payload = JSON.parse(String(init.body));
    expect(payload.user_uuid).toBeUndefined();
    expect(payload.current_stock).toBeUndefined();
    expect(payload.assigned_to).toBe("NXV-EMP-1042");
  });

  test("un consumo envía assigned_to nulo", async () => {
    mockResponse(201, {
      id: 10,
      order_type: "outbound",
      asset_id: 5,
      asset_name: "A4 paper ream",
      asset_sku: "NXV-OFF-001",
      asset_category: "office_supplies",
      quantity: 1,
      office: "Valencia",
      created_at: "2026-03-02T09:00:00Z",
      user_uuid: "user-1",
      supplier: null,
      exit_type: "consumption",
      assigned_to: null,
    });
    const { createAssetExit } = await import("@/lib/inventory");
    await createAssetExit({
      asset_id: 5,
      quantity: 1,
      exit_type: "consumption",
      assigned_to: "no-debe-enviarse",
      office: "Valencia",
    });
    const payload = JSON.parse(String((fetch as jest.Mock).mock.calls[0][1].body));
    expect(payload.assigned_to).toBeNull();
  });

  test("el 400 de stock insuficiente conserva el mensaje de la API", async () => {
    const detail = "Insufficient stock for asset 'Laptop 14\" Business'. Available: 12, requested: 99.";
    mockResponse(400, { detail });
    const { createAssetExit } = await import("@/lib/inventory");
    const { ApiError } = await import("@/lib/http");
    await expect(
      createAssetExit({
        asset_id: 1,
        quantity: 99,
        exit_type: "allocation",
        assigned_to: "NXV-EMP-1042",
        office: "Valencia",
      }),
    ).rejects.toMatchObject({ status: 400, message: detail });
    await expect(
      createAssetExit({
        asset_id: 1,
        quantity: 99,
        exit_type: "allocation",
        assigned_to: "NXV-EMP-1042",
        office: "Valencia",
      }),
    ).rejects.toBeInstanceOf(ApiError);
    expect(readToken()).toBe("jwt-demo");
  });

  test("un 422 rellena el campo y un 500 no se traga", async () => {
    mockResponse(422, {
      detail: [{ loc: ["body", "assigned_to"], msg: "Value error, assigned_to es obligatorio cuando exit_type es allocation.", type: "value_error" }],
    });
    const { createAssetExit } = await import("@/lib/inventory");
    await expect(
      createAssetExit({
        asset_id: 1,
        quantity: 1,
        exit_type: "allocation",
        assigned_to: "NXV-EMP-1",
        office: "Valencia",
      }),
    ).rejects.toMatchObject({
      status: 422,
      fields: { assigned_to: "assigned_to es obligatorio cuando exit_type es allocation." },
    });

    mockResponse(500, { detail: "No se pudo completar la operación." });
    await expect(
      createAssetExit({
        asset_id: 1,
        quantity: 1,
        exit_type: "allocation",
        assigned_to: "NXV-EMP-1",
        office: "Valencia",
      }),
    ).rejects.toMatchObject({ status: 500, message: "No se pudo completar la operación." });
  });

  test("un 500 sin cuerpo y un fallo de red siguen siendo error", async () => {
    mockResponse(500, null);
    const { listAssets } = await import("@/lib/inventory");
    await expect(listAssets()).rejects.toMatchObject({
      status: 500,
      message: "La API respondió 500 sin un mensaje legible.",
    });
    jest.spyOn(global, "fetch").mockRejectedValue(new Error("offline"));
    await expect(listAssets()).rejects.toMatchObject({ status: 0 });
  });

  test("un 401 borra el token", async () => {
    mockResponse(401, { detail: "Falta un token válido." });
    const { listOrders } = await import("@/lib/inventory");
    await expect(listOrders()).rejects.toMatchObject({ status: 401 });
    expect(readToken()).toBe("");
  });

  test("la base usa NEXT_PUBLIC_INVENTORY_API_URL sin barra final", async () => {
    process.env.NEXT_PUBLIC_INVENTORY_API_URL = "http://localhost:8000/";
    jest.resetModules();
    mockResponse(200, []);
    writeToken("jwt-demo");
    const { listAssets } = await import("@/lib/inventory");
    await listAssets("Valencia");
    expect((fetch as jest.Mock).mock.calls[0][0]).toBe("http://localhost:8000/inventory/products?office=Valencia");
    delete process.env.NEXT_PUBLIC_INVENTORY_API_URL;
    jest.resetModules();
  });
});

describe("los componentes no llaman a fetch", () => {
  test("fetch vive en lib, no en components ni en las páginas", () => {
    const root = path.resolve(__dirname, "..");
    const files: string[] = [];
    const walk = (dir: string) => {
      for (const entry of readdirSync(dir)) {
        const full = path.join(dir, entry);
        if (statSync(full).isDirectory()) {
          if (entry === "node_modules" || entry === ".next") continue;
          walk(full);
          continue;
        }
        if (/\.(tsx|jsx)$/.test(entry)) files.push(full);
      }
    };
    walk(path.join(root, "components"));
    walk(path.join(root, "app"));
    const offenders = files.filter((file) => /\bfetch\s*\(/.test(readFileSync(file, "utf8")));
    expect(offenders).toEqual([]);
  });
});
