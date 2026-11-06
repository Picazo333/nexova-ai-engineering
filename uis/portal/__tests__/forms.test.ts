import { emailError, passwordConfirmError, passwordError, textLimit } from "../lib/forms";

test("emailError acepta un correo con espacios y mayúsculas", () => {
  expect(emailError("  ANA@Nexova.test ")).toBeNull();
});

test("emailError rechaza un texto sin dominio", () => {
  expect(emailError("mal")).toMatch(/formato válido/);
  expect(emailError("ana@nexova")).toMatch(/formato válido/);
  expect(emailError("ana nexova@nexova.test")).toMatch(/formato válido/);
  expect(emailError("@nexova.test")).toMatch(/formato válido/);
});

test("passwordError acepta ocho caracteres y rechaza el borde", () => {
  expect(passwordError("12345678")).toBeNull();
  expect(passwordError("1234567")).toMatch(/8 caracteres/);
  expect(passwordError(" 12345678")).toMatch(/sin espacios al borde/);
  expect(passwordError("12345678 ")).toMatch(/sin espacios al borde/);
});

test("passwordError cuenta bytes y no caracteres", () => {
  // "á" ocupa dos bytes. 36 caben; 37 se pasan de 72.
  expect(passwordError("á".repeat(36))).toBeNull();
  expect(passwordError("á".repeat(37))).toMatch(/72 bytes/);
  expect(passwordError("a".repeat(73))).toMatch(/72 bytes/);
});

test("passwordConfirmError exige la misma contraseña válida", () => {
  expect(passwordConfirmError("nueva-clave-9", "nueva-clave-9")).toBeNull();
  expect(passwordConfirmError("corta", "corta")).toMatch(/8 caracteres/);
  expect(passwordConfirmError("nueva-clave-9", "otra-clave-99")).toMatch(/no coincide/);
});

test("textLimit acepta un texto dentro del límite", () => {
  expect(textLimit("  hola  ", 10, "El nombre")).toBeNull();
});

test("textLimit rechaza un texto que se pasa", () => {
  expect(textLimit("a".repeat(11), 10, "El nombre")).toBe("El nombre supera los 10 caracteres.");
});
