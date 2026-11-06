import { Suspense } from "react";
import type { Metadata } from "next";
import { LoadingStatus } from "@/components/AsyncStatus";
import { CandidateForm } from "@/components/CandidateForm";

export const metadata: Metadata = {
  title: "Registrar candidatura",
};

export default function NewCandidatePage() {
  return (
    <Suspense fallback={<LoadingStatus label="Cargando el formulario…" />}>
      <CandidateForm mode="create" />
    </Suspense>
  );
}
