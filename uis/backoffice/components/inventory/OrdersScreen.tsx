"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";

import { EmptyState, ErrorBanner, LoadingState } from "@/components/AsyncStatus";
import { OfficeFilter, cleanOffice } from "@/components/inventory/OfficeFilter";
import { listOrders, type InventoryOrder } from "@/lib/inventory";
import { messageOf } from "@/lib/http";
import { exitTypeLabel, formatTimestamp, orderTypeLabel } from "@/lib/labels";

export function OrdersScreen({ initialOffice }: { initialOffice: string }) {
  const router = useRouter();
  const pathname = usePathname();
  const [office, setOffice] = useState(cleanOffice(initialOffice));
  const [orders, setOrders] = useState<InventoryOrder[]>([]);
  const [phase, setPhase] = useState<"loading" | "ready" | "error">("loading");
  const [error, setError] = useState("");
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    setOffice(cleanOffice(initialOffice));
  }, [initialOffice]);

  useEffect(() => {
    let cancelled = false;
    setPhase("loading");
    listOrders(office || undefined)
      .then((rows) => {
        if (cancelled) return;
        setOrders(rows);
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

  return (
    <>
      <h1>Historial de entradas y salidas</h1>
      <p className="lead">
        Cada fila es una <code>AssetEntry</code> o una <code>AssetExit</code>. Esta página es de solo lectura: no se
        edita ni se borra ninguna orden.
      </p>
      <OfficeFilter id="office-orders" value={office} onChange={onOffice} />
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
              {orders.map((order) => (
                <tr key={`${order.order_type}-${order.id}`}>
                  <td>
                    <span className={order.order_type === "inbound" ? "tag tag-in" : "tag tag-out"}>
                      {orderTypeLabel(order.order_type)}
                    </span>
                  </td>
                  <th scope="row">
                    {order.asset_name} <span className="mono note">{order.asset_sku}</span>
                  </th>
                  <td>{order.quantity}</td>
                  <td>{formatTimestamp(order.created_at)}</td>
                  <td className="mono">{order.user_uuid}</td>
                  <td>
                    {order.order_type === "inbound" ? `Proveedor: ${order.supplier ?? "—"}. ` : null}
                    {order.order_type === "outbound"
                      ? `${exitTypeLabel(order.exit_type ?? "")} (${order.exit_type ?? "—"}). ${
                          order.assigned_to ? `assigned_to ${order.assigned_to}.` : "Sin assigned_to."
                        } `
                      : null}
                    Oficina: {order.office}.
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
