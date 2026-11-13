"use client";

import { useEffect, useMemo, useState } from "react";
import { usePathname, useRouter } from "next/navigation";

import { EmptyState, ErrorBanner, LoadingState } from "@/components/AsyncStatus";
import { OfficeFilter, cleanOffice } from "@/components/inventory/OfficeFilter";
import { listOrdersView, type InventoryOrder } from "@/lib/inventory";
import { messageOf, type CacheMark } from "@/lib/http";
import { prepareHistory } from "@/lib/orders-rollup";

export function OrdersScreen({ initialOffice }: { initialOffice: string }) {
  const router = useRouter();
  const pathname = usePathname();
  const [office, setOffice] = useState(cleanOffice(initialOffice));
  const [orders, setOrders] = useState<InventoryOrder[]>([]);
  const [cache, setCache] = useState<CacheMark>("");
  const [phase, setPhase] = useState<"loading" | "ready" | "error">("loading");
  const [error, setError] = useState("");
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    setOffice(cleanOffice(initialOffice));
  }, [initialOffice]);

  useEffect(() => {
    let cancelled = false;
    setPhase("loading");
    listOrdersView(office || undefined)
      .then((view) => {
        if (cancelled) return;
        setOrders(view.rows);
        setCache(view.cache);
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

  const history = useMemo(() => prepareHistory(orders), [orders]);
  const summary = history.summary;

  function onOffice(next: string) {
    const cleaned = cleanOffice(next);
    setOffice(cleaned);
    const params = new URLSearchParams();
    if (cleaned) params.set("office", cleaned);
    const query = params.toString();
    router.replace(query ? `${pathname}?${query}` : pathname, { scroll: false });
  }

  return (
    <>
      <h1>Historial de entradas y salidas</h1>
      <p className="lead">
        Cada fila es una <code>AssetEntry</code> o una <code>AssetExit</code>. Esta página es de solo lectura: no se
        edita ni se borra ninguna orden.
      </p>
      <OfficeFilter id="office-orders" value={office} onChange={onOffice} />
      {orders.length > 0 ? (
        <p>
          {summary.inbound === 1 ? "1 entrada" : `${summary.inbound} entradas`} ({summary.unitsIn}{" "}
          {summary.unitsIn === 1 ? "unidad" : "unidades"}) y{" "}
          {summary.outbound === 1 ? "1 salida" : `${summary.outbound} salidas`} ({summary.unitsOut}{" "}
          {summary.unitsOut === 1 ? "unidad" : "unidades"})
          {summary.offices.length > 0
            ? `. ${summary.offices
                .map((item) => `${item.office}: ${item.orders === 1 ? "1 orden" : `${item.orders} órdenes`}`)
                .join(". ")}.`
            : "."}
        </p>
      ) : null}
      {cache === "HIT" && orders.length > 0 ? (
        <p className="note" role="status">
          Lista leída de la caché en memoria de la API. Caduca a los 30 segundos, o antes si alguien registra una
          entrada o una salida.
        </p>
      ) : null}
      {phase === "loading" && orders.length === 0 ? <LoadingState label="Cargando el historial…" /> : null}
      {phase === "loading" && orders.length > 0 ? <LoadingState label="Actualizando el historial…" /> : null}
      {phase === "error" && orders.length === 0 ? (
        <ErrorBanner title="No se pudo cargar el historial" message={error} onRetry={() => setAttempt((value) => value + 1)} />
      ) : null}
      {phase === "error" && orders.length > 0 ? (
        <ErrorBanner
          title="No se pudo actualizar el historial"
          message={`${error} Se conserva la lista anterior.`}
          onRetry={() => setAttempt((value) => value + 1)}
        />
      ) : null}
      {phase === "ready" && orders.length === 0 ? (
        <EmptyState
          title="Aún no hay entradas ni salidas"
          message="Cuando operaciones registre una entrega o un consumo, aparecerá aquí con el activo y el user_uuid."
          href="/backoffice/inventory/orders/inbound"
          action="Registrar una entrada"
        />
      ) : null}
      {orders.length > 0 ? (
        <div className="table-scroll" tabIndex={0} role="region" aria-label="Historial de órdenes. Desplaza en horizontal si no cabe.">
          <table>
            <caption>{orders.length === 1 ? "1 orden" : `${orders.length} órdenes`} de solo lectura</caption>
            <thead>
              <tr>
                <th scope="col">Tipo</th>
                <th scope="col">Activo</th>
                <th scope="col">Cantidad</th>
                <th scope="col">Fecha</th>
                <th scope="col">user_uuid</th>
                <th scope="col">Detalle</th>
              </tr>
            </thead>
            <tbody>
              {history.rows.map((order) => (
                <tr key={`${order.order_type}-${order.id}`}>
                  <td>
                    <span className={order.order_type === "inbound" ? "tag tag-in" : "tag tag-out"}>
                      {order.typeLabel}
                    </span>
                  </td>
                  <th scope="row">
                    {order.asset_name} <span className="mono note">{order.asset_sku}</span>
                  </th>
                  <td>{order.quantity}</td>
                  <td>{order.when}</td>
                  <td className="mono">{order.user_uuid}</td>
                  <td>{order.detail}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
    </>
  );
}
