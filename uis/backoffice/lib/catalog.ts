export type CatalogPhase = "loading" | "ready" | "error";

export type CatalogView<T> = {
  phase: CatalogPhase;
  rows: T[];
  error: string;
};

export function beginCatalog<T>(rows: T[]): CatalogView<T> {
  return { phase: "loading", rows, error: "" };
}

export function settleCatalog<T>(rows: T[]): CatalogView<T> {
  return { phase: "ready", rows, error: "" };
}

export function failCatalog<T>(rows: T[], error: string): CatalogView<T> {
  return { phase: "error", rows, error };
}
