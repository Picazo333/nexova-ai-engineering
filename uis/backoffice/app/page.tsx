import { StackStatus } from "@/components/StackStatus";

export default function Page() {
  return (
    <main id="contenido" className="panel">
      <div className="wrap">
        <h1>Panel interno</h1>
        <p className="lead">
          Este proceso es el backoffice Next.js del monorepo. Escucha en el puerto 3001. La API
          corre en otro proceso y el navegador la llama con NEXT_PUBLIC_INVENTORY_API_URL.
        </p>
        <p className="actions">
          <a className="button" href="/backoffice/inventory/products">
            Abrir el inventario de activos
          </a>
        </p>
        <StackStatus />
      </div>
    </main>
  );
}
