import { Suspense } from "react";
import type { Metadata } from "next";
import { LoadingStatus } from "@/components/AsyncStatus";
import { CandidateDetail } from "@/components/CandidateDetail";

export const metadata: Metadata = {
  title: "Candidatura",
};

export default async function CandidatePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return (
    <Suspense fallback={<LoadingStatus label="Cargando la candidatura…" />}>
      <CandidateDetail id={id} />
    </Suspense>
  );
}
