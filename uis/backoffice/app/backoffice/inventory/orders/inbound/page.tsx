import type { Metadata } from "next";

import { EntryForm } from "@/components/inventory/EntryForm";

export const metadata: Metadata = {
  title: "Entrada de activos · Inventario",
  description: "Formulario para registrar una entrega de activos (AssetEntry).",
};

export default async function Page({ searchParams }: { searchParams: Promise<{ asset?: string }> }) {
  const params = await searchParams;
  return <EntryForm initialAsset={params.asset ?? ""} />;
}
