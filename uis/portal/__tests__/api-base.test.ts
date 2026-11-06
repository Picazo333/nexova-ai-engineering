import { apiBase } from "../lib/api";

const KEY = "NEXT_PUBLIC_API_URL";

afterEach(() => {
  delete process.env[KEY];
});

test("apiBase usa la URL configurada sin la barra final", () => {
  process.env[KEY] = "http://127.0.0.1:9000/";
  expect(apiBase()).toBe("http://127.0.0.1:9000");
});

test("apiBase no inventa una ruta relativa si la variable está vacía", () => {
  delete process.env[KEY];
  expect(apiBase()).toBe("http://127.0.0.1:8000");
  process.env[KEY] = "   ";
  expect(apiBase()).toBe("http://127.0.0.1:8000");
});
