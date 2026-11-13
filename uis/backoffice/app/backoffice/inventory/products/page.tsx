import type { Metadata } from "next";

import { AssetsScreen } from "@/components/inventory/AssetsScreen";

export const metadata: Metadata = {
  title: "Activos · Inventario",
  description: "Activos de Nexova con el stock calculado de entradas menos salidas.",
};

export default async function Page({ searchParams }: { searchParams: Promise<{ office?: string }> }) {
  const params = await searchParams;
  return <AssetsScreen initialOffice={params.office ?? ""} />;
}
