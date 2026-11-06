import { Suspense } from "react";
import { LoadingStatus } from "@/components/AsyncStatus";
import { CandidateBrowser } from "@/components/CandidateBrowser";

export default function HomePage() {
  return (
    <>
      <h1>Candidaturas</h1>
      <p className="lead">
        Operaciones de Selección consulta aquí el nombre, el puesto, el estado y la etapa de cada
        candidatura, sin volver a la hoja de cálculo.
      </p>
      <Suspense fallback={<LoadingStatus label="Cargando candidaturas…" />}>
        <CandidateBrowser />
      </Suspense>
    </>
  );
}
