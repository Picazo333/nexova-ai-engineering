"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";

import { EmptyState, ErrorBanner, LoadingState } from "@/components/AsyncStatus";
import { OfficeFilter, cleanOffice } from "@/components/inventory/OfficeFilter";
import { StockBadge } from "@/components/inventory/StockBadge";
import { categoryLabel } from "@/lib/labels";
import { listAssets, type Asset } from "@/lib/inventory";
import { messageOf } from "@/lib/http";
import { LOW_STOCK_BELOW } from "@/lib/stock";

export function AssetsScreen({ initialOffice }: { initialOffice: string }) {
  const router = useRouter();
  const pathname = usePathname();
  const [office, setOffice] = useState(cleanOffice(initialOffice));
  const [assets, setAssets] = useState<Asset[]>([]);
  const [phase, setPhase] = useState<"loading" | "ready" | "error">("loading");
  const [error, setError] = useState("");
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    setOffice(cleanOffice(initialOffice));
  }, [initialOffice]);

  useEffect(() => {
    let cancelled = false;
    setPhase("loading");
    listAssets(office || undefined)
      .then((rows) => {
        if (cancelled) return;
        setAssets(rows);
        setError("");
        setPhase("ready");
      })
      .catch((reason: unknown) => {
        if (cancelled) return;
        setError(messageOf(reason));
        setPhase("error");
      });
    return () => {
      cancelled = true;
    };
  }, [office, attempt]);

  function onOffice(next: string) {
    const cleaned = cleanOffice(next);
    setOffice(cleaned);
    const params = new URLSearchParams();
    if (cleaned) params.set("office", cleaned);
    const query = params.toString();
    router.replace(query ? `${pathname}?${query}` : pathname, { scroll: false });
  }

  const showTable = assets.length > 0;
  return (
    <>
      <h1>Activos</h1>
      <p className="lead">
        Cada fila es un Asset. El stock actual (<code>current_stock</code>) se calcula con las entradas (
        <code>AssetEntry</code>) y las salidas (<code>AssetExit</code>). No es un campo editable.
      </p>
      <p className="note">
        Indicador: sin stock en 0. Bajo por debajo de {LOW_STOCK_BELOW}. Saludable desde {LOW_STOCK_BELOW}. El color
        va acompañado del texto.
      </p>
      <OfficeFilter id="office-assets" value={office} onChange={onOffice} />
      {phase === "loading" && assets.length === 0 ? <LoadingState label="Cargando activos…" /> : null}
      {phase === "loading" && assets.length > 0 ? <LoadingState label="Actualizando activos…" /> : null}
      {phase === "error" && assets.length === 0 ? (
        <ErrorBanner title="No se pudieron cargar los activos" message={error} onRetry={() => setAttempt((value) => value + 1)} />
      ) : null}
      {phase === "error" && assets.length > 0 ? (
        <ErrorBanner
          title="No se pudo actualizar el listado"
          message={`${error} Se conserva la lista anterior.`}
          onRetry={() => setAttempt((value) => value + 1)}
        />
      ) : null}
      {phase === "ready" && assets.length === 0 ? (
        <EmptyState
          title="No hay activos"
          message="La API no devolvió ningún Asset para esta oficina. Cuando llegue material, registra una entrada de activos."
          href="/backoffice/inventory/orders/inbound"
          action="Registrar una entrada"
        />
      ) : null}
      {showTable ? (
        <div className="table-scroll" tabIndex={0} role="region" aria-label="Tabla de activos. Desplaza en horizontal si no cabe.">
          <table>
            <caption>{assets.length === 1 ? "1 activo" : `${assets.length} activos`} con stock calculado</caption>
            <thead>
              <tr>
                <th scope="col">Activo</th>
                <th scope="col">SKU</th>
                <th scope="col">Categoría</th>
                <th scope="col">Oficina</th>
                <th scope="col">Stock actual</th>
                <th scope="col">Registrar</th>
              </tr>
            </thead>
            <tbody>
              {assets.map((asset) => (
                <tr key={asset.id}>
                  <th scope="row">{asset.name}</th>
                  <td className="mono">{asset.sku}</td>
                  <td>
                    {categoryLabel(asset.category)} <span className="mono note">({asset.category})</span>
                  </td>
                  <td>{asset.office}</td>
                  <td>
                    <StockBadge stock={asset.current_stock} />
                  </td>
                  <td>
                    <p className="actions tight">
                      <a className="button" href={`/backoffice/inventory/orders/inbound?asset=${asset.id}`}>
                        Registrar entrada
                      </a>
                      <a className="button secondary" href={`/backoffice/inventory/orders/outbound?asset=${asset.id}`}>
                        Registrar salida
                      </a>
                    </p>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
    </>
  );
}
