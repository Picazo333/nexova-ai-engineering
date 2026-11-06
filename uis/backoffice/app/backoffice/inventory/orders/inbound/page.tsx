import type { Metadata } from "next";

import { LazyEntryForm } from "@/components/inventory/LazyEntryForm";

export const metadata: Metadata = {
  title: "Entrada de activos · Inventario",
  description: "Formulario para registrar una entrega de activos (AssetEntry).",
};

export default async function Page({ searchParams }: { searchParams: Promise<{ asset?: string }> }) {
  const params = await searchParams;
  return <LazyEntryForm initialAsset={params.asset ?? ""} />;
}
