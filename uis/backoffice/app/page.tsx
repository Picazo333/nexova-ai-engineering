import { StackStatus } from "@/components/StackStatus";

export default function Page() {
  return (
    <main id="contenido" className="panel">
      <div className="wrap">
        <h1>Panel interno</h1>
        <p className="lead">
          Este proceso es el backoffice Next.js del monorepo. Escucha en el puerto 3001. La API
          corre en otro contenedor y este proceso la llama por el nombre del servicio.
        </p>
        <StackStatus />
      </div>
    </main>
  );
}
