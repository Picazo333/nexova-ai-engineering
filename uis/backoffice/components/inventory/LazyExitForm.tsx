"use client";

import dynamic from "next/dynamic";

import { LoadingState } from "@/components/AsyncStatus";

const ExitForm = dynamic(() => import("@/components/inventory/ExitForm").then((mod) => mod.ExitForm), {
  loading: () => <LoadingState label="Cargando el formulario de salida…" />,
});

export function LazyExitForm({ initialAsset }: { initialAsset: string }) {
  return <ExitForm initialAsset={initialAsset} />;
}
