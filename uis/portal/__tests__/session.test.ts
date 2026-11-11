import { clearToken, readToken, TOKEN_KEY, writeToken } from "../lib/session";

class MemoryStorage {
  readonly data = new Map<string, string>();
  fail: "get" | "set" | "remove" | null = null;

  getItem(key: string): string | null {
    if (this.fail === "get") throw new Error("storage blocked");
    return this.data.has(key) ? (this.data.get(key) as string) : null;
  }

  setItem(key: string, value: string): void {
    if (this.fail === "set") throw new Error("storage blocked");
    this.data.set(key, value);
  }

  removeItem(key: string): void {
    if (this.fail === "remove") throw new Error("storage blocked");
    this.data.delete(key);
  }
}

function install(storage: MemoryStorage | undefined): void {
  if (storage === undefined) {
    Reflect.deleteProperty(globalThis, "window");
    Reflect.deleteProperty(globalThis, "localStorage");
    return;
  }
  Object.defineProperty(globalThis, "window", { value: globalThis, configurable: true });
  Object.defineProperty(globalThis, "localStorage", { value: storage, configurable: true });
}

afterEach(() => {
  install(undefined);
});

test("writeToken y readToken guardan la clave de sesión", () => {
  const storage = new MemoryStorage();
  install(storage);
  expect(writeToken("token-de-prueba")).toBe(true);
  expect(readToken()).toBe("token-de-prueba");
  expect(storage.data.get(TOKEN_KEY)).toBe("token-de-prueba");
});

test("writeToken falla si el almacén no conserva el valor", () => {
  const storage = new MemoryStorage();
  install(storage);
  storage.getItem = () => "otro-valor";
  expect(writeToken("token-de-prueba")).toBe(false);
});

test("writeToken falla si el almacén lanza", () => {
  const storage = new MemoryStorage();
  storage.fail = "set";
  install(storage);
  expect(writeToken("token-de-prueba")).toBe(false);
  expect(storage.data.has(TOKEN_KEY)).toBe(false);
});

test("readToken devuelve cadena vacía sin window o si el almacén lanza", () => {
  install(undefined);
  expect(readToken()).toBe("");
  const storage = new MemoryStorage();
  storage.fail = "get";
  install(storage);
  expect(readToken()).toBe("");
});

test("clearToken borra la clave y no propaga un almacén bloqueado", () => {
  const storage = new MemoryStorage();
  install(storage);
  writeToken("token-de-prueba");
  clearToken();
  expect(readToken()).toBe("");
  writeToken("token-de-prueba");
  storage.fail = "remove";
  expect(() => clearToken()).not.toThrow();
  expect(storage.data.get(TOKEN_KEY)).toBe("token-de-prueba");
});
