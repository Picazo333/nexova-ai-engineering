import type { Metadata } from "next";

import { ExitForm } from "@/components/inventory/ExitForm";

export const metadata: Metadata = {
  title: "Salida de activos · Inventario",
  description: "Formulario para registrar una asignación o un consumo (AssetExit), con el stock actual antes de enviar.",
};

export default async function Page({ searchParams }: { searchParams: Promise<{ asset?: string }> }) {
  const params = await searchParams;
  return <ExitForm initialAsset={params.asset ?? ""} />;
}
