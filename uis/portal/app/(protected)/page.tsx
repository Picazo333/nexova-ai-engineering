import type { Metadata } from "next";

import { IncidentsScreen } from "@/components/IncidentsScreen";

export const metadata: Metadata = { title: "Análisis de tickets" };

export default function HomePage() {
  return <IncidentsScreen />;
}
