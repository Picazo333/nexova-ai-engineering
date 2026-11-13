export type StackBody = { ok?: boolean; upstream?: string; message?: string };

export function readStack(signal?: AbortSignal): Promise<StackBody> {
  return fetch("/api/stack", { cache: "no-store", signal }).then(async (response) => {
    const body = (await response.json()) as StackBody;
    if (!response.ok && !body.message) {
      return { ok: false, message: "No hay conexión con la API." };
    }
    return body;
  });
}
