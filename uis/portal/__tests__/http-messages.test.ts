import { HTTP_CATALOG, fieldMessage, humanMessage, isReadableMessage } from "../lib/http-messages";

test("un 409 sigue siendo la frase del correo repetido", () => {
  expect(humanMessage(409, "Traceback")).toBe("Ya existe una cuenta con ese correo.");
  expect(humanMessage(409)).toBe(HTTP_CATALOG[409]);
});

test("una frase propia de la API se conserva", () => {
  expect(isReadableMessage(undefined)).toBe(false);
  expect(isReadableMessage("500")).toBe(false);
  expect(fieldMessage("500")).toBe("Revisa este campo.");
  const sentence = "La contraseña es obligatoria.";
  expect(isReadableMessage(sentence)).toBe(true);
  expect(humanMessage(422, sentence)).toBe(sentence);
  expect(humanMessage(401, "El correo o la contraseña no son válidos.")).toBe(
    "El correo o la contraseña no son válidos.",
  );
});

test("traza, secreto, código y JSON en crudo no se enseñan", () => {
  const leaked = [
    'Traceback (most recent call last): File "/workspace/services/api/.env"',
    "JWT_SECRET no está definido",
    "Unexpected token < in JSON",
    "Error 500",
    "500",
    "secret-sentinel",
  ];
  for (const sample of leaked) {
    const sentence = humanMessage(500, sample);
    expect(sentence).toBe(HTTP_CATALOG[500]);
    expect(sentence).not.toMatch(/traceback|jwt_secret|unexpected token|secret-sentinel|\.env/i);
  }
  expect(humanMessage(404, "Not Found")).toBe("Not Found");
  expect(humanMessage(404, "")).toBe(HTTP_CATALOG[404]);
  expect(humanMessage(401, "")).toBe("El correo o la contraseña no coinciden con una cuenta activa.");
  expect(humanMessage(0, "socket hang up")).toBe(HTTP_CATALOG[0]);
  expect(humanMessage(418, "I am a teapot".repeat(40))).toBe("No se pudo completar la solicitud.");
});

test("un mensaje de campo quita el prefijo de validación y no repite una traza", () => {
  expect(fieldMessage("Value error, El nombre supera los 200 caracteres.")).toBe(
    "El nombre supera los 200 caracteres.",
  );
  expect(fieldMessage("Traceback")).toBe("Revisa este campo.");
  expect(fieldMessage("")).toBe("Revisa este campo.");
});
