import { safeNext, viewLabel } from "../lib/paths";

test("safeNext conserva una ruta interna permitida", () => {
  expect(safeNext("/proveedores?country=Spain")).toBe("/proveedores?country=Spain");
  expect(safeNext("/account/profile")).toBe("/account/profile");
  expect(viewLabel("/proveedores?country=Spain")).toBe("el directorio de proveedores");
  expect(viewLabel("/account/profile")).toBe("tu perfil");
});

test("safeNext cierra las redirecciones que salen del portal", () => {
  // Un next externo no puede llevar la sesión a otro sitio.
  expect(safeNext(null)).toBe("/");
  expect(safeNext("https://evil.example/login")).toBe("/");
  expect(safeNext("//evil.example")).toBe("/");
  expect(safeNext("/%2F%2Fevil.example")).toBe("/");
  expect(safeNext("/%")).toBe("/");
  expect(safeNext("/login")).toBe("/");
  expect(safeNext("/\\evil")).toBe("/");
  expect(viewLabel("/login")).toBe("el análisis de tickets");
});
