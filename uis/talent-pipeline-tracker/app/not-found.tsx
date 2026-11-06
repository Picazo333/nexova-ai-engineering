import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Página no encontrada",
};

export default function NotFound() {
  return (
    <>
      <h1>Página no encontrada</h1>
      <p className="lead">Esa ruta no existe en el seguimiento de candidaturas.</p>
      <Link className="button button-primary" href="/">
        Ir al listado
      </Link>
    </>
  );
}
