import { Suspense } from "react";
import type { Metadata } from "next";
import { LoadingStatus } from "@/components/AsyncStatus";
import { CandidateForm } from "@/components/CandidateForm";

export const metadata: Metadata = {
  title: "Editar candidatura",
};

export default async function EditCandidatePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return (
    <Suspense fallback={<LoadingStatus label="Cargando los datos de la candidatura…" />}>
      <CandidateForm mode="edit" id={id} />
    </Suspense>
  );
}
