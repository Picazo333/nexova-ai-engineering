"use client";

import dynamic from "next/dynamic";

import { LoadingState } from "@/components/AsyncStatus";

const EntryForm = dynamic(() => import("@/components/inventory/EntryForm").then((mod) => mod.EntryForm), {
  loading: () => <LoadingState label="Cargando el formulario de entrada…" />,
});

export function LazyEntryForm({ initialAsset }: { initialAsset: string }) {
  return <EntryForm initialAsset={initialAsset} />;
}
