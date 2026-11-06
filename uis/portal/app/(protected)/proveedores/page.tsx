import type { Metadata } from "next";

import { SuppliersScreen } from "@/components/SuppliersScreen";

export const metadata: Metadata = { title: "Contratos de proveedores" };

export default function SuppliersPage() {
  return <SuppliersScreen />;
}
