import type { Metadata } from "next";

import { LazyExitForm } from "@/components/inventory/LazyExitForm";

export const metadata: Metadata = {
  title: "Salida de activos · Inventario",
  description: "Formulario para registrar una asignación o un consumo (AssetExit), con el stock actual antes de enviar.",
};

export default async function Page({ searchParams }: { searchParams: Promise<{ asset?: string }> }) {
  const params = await searchParams;
  return <LazyExitForm initialAsset={params.asset ?? ""} />;
}
