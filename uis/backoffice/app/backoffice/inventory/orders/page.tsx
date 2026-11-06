import type { Metadata } from "next";

import { OrdersScreen } from "@/components/inventory/OrdersScreen";

export const metadata: Metadata = {
  title: "Historial · Inventario",
  description: "Entradas y salidas de activos, de solo lectura, con el user_uuid de quien las registró.",
};

export default async function Page({ searchParams }: { searchParams: Promise<{ office?: string }> }) {
  const params = await searchParams;
  return <OrdersScreen initialOffice={params.office ?? ""} />;
}
