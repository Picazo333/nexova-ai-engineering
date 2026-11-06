"use client";

import { useEffect, useRef, useState } from "react";

import { EmptyState, ErrorBanner, LoadingState } from "@/components/AsyncStatus";
import { useAssetCatalog } from "@/components/inventory/useAssetCatalog";
import { ApiError, messageOf } from "@/lib/http";
import { createAssetEntry, getAsset, type InventoryOrder, type Office } from "@/lib/inventory";
import { formatTimestamp } from "@/lib/labels";
import { parseQuantity } from "@/lib/quantity";

export function EntryForm({ initialAsset }: { initialAsset: string }) {
  const [attempt, setAttempt] = useState(0);
  const catalog = useAssetCatalog(attempt);
  const assets = catalog.rows;
  const loadPhase = catalog.phase;
  const loadError = catalog.error;
  const [assetId, setAssetId] = useState(initialAsset);
  const [quantity, setQuantity] = useState("");
  const [supplier, setSupplier] = useState("");
  const [office, setOffice] = useState<Office | "">("");
  const [stockText, setStockText] = useState("");
  const [pending, setPending] = useState(false);
  const [formError, setFormError] = useState("");
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [confirmation, setConfirmation] = useState<InventoryOrder | null>(null);
  const confirmRef = useRef<HTMLDivElement>(null);
  const alertRef = useRef<HTMLDivElement>(null);
  const submitId = useRef(0);
  const officeTouched = useRef("");

  useEffect(() => {
    setAssetId(initialAsset);
  }, [initialAsset]);

  const selected = assets.find((asset) => String(asset.id) === assetId) ?? null;

  useEffect(() => {
    if (!selected) {
      setStockText("");
      return;
    }
    let cancelled = false;
    const assetIdNow = selected.id;
    setStockText("Consultando el stock actual…");
    getAsset(assetIdNow)
      .then((asset) => {
        if (cancelled || asset.id !== assetIdNow) return;
        setStockText(`Stock actual (current_stock): ${asset.current_stock}.`);
        if (officeTouched.current !== String(asset.id)) {
          officeTouched.current = String(asset.id);
          if (asset.office === "Valencia" || asset.office === "Miami") setOffice(asset.office);
        }
      })
      .catch(() => {
        if (!cancelled) setStockText("No se pudo leer el stock. Puedes registrar la entrada igualmente.");
      });
    return () => {
      cancelled = true;
    };
  }, [selected]);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (pending) return;
    const problems: Record<string, string> = {};
    const parsed = parseQuantity(quantity);
    if (!selected) problems.asset_id = "Elige un activo por su nombre.";
    if (parsed == null) problems.quantity = "La cantidad tiene que ser un entero mayor que cero.";
    if (!supplier.trim()) problems.supplier = "Escribe el proveedor de la entrega.";
    if (office !== "Valencia" && office !== "Miami") problems.office = "Elige Valencia o Miami.";
    setFieldErrors(problems);
    if (Object.keys(problems).length > 0 || !selected || parsed == null || (office !== "Valencia" && office !== "Miami")) {
      setFormError("Revisa los campos antes de registrar la entrada.");
      alertRef.current?.focus();
      return;
    }
    const id = ++submitId.current;
    setPending(true);
    setFormError("");
    setConfirmation(null);
    try {
      const order = await createAssetEntry({
        asset_id: selected.id,
        quantity: parsed,
        supplier: supplier.trim(),
        office,
      });
      if (id !== submitId.current) return;
      setConfirmation(order);
      setQuantity("");
      setSupplier("");
      setAssetId("");
      setOffice("");
      setStockText("");
      officeTouched.current = "";
      setFieldErrors({});
      confirmRef.current?.focus();
    } catch (reason: unknown) {
      if (id !== submitId.current) return;
      if (reason instanceof ApiError) {
        setFieldErrors(reason.fields);
        setFormError(reason.message);
      } else {
        setFormError(messageOf(reason));
      }
      alertRef.current?.focus();
    } finally {
      if (id === submitId.current) setPending(false);
    }
  }

  return (
    <>
      <h1>Entrada de activos</h1>
      <p className="lead">
        Registra una entrega recibida. El envío crea un <code>AssetEntry</code> con{" "}
        <code>POST /inventory/orders/inbound</code>. El <code>user_uuid</code> lo pone la API con tu sesión.
      </p>
      {loadPhase === "loading" && assets.length === 0 ? <LoadingState label="Cargando activos…" /> : null}
      {loadPhase === "error" && assets.length === 0 ? (
        <ErrorBanner title="No se pudieron cargar los activos" message={loadError} onRetry={() => setAttempt((value) => value + 1)} />
      ) : null}
      {loadPhase === "ready" && assets.length === 0 ? (
        <EmptyState
          title="No hay activos para una entrada"
          message="La API no tiene ningún Asset. Sin un activo no se puede elegir un nombre."
          href="/backoffice/inventory/products"
          action="Volver a activos"
        />
      ) : null}
      {assets.length > 0 ? (
        <form onSubmit={onSubmit} noValidate>
          {confirmation ? (
            <div className="banner ok result-panel" data-motion-node data-arrived="true" role="status" tabIndex={-1} ref={confirmRef} data-testid="confirm">
              <h2>Entrada registrada</h2>
              <p>
                {confirmation.quantity} × {confirmation.asset_name} ({confirmation.asset_sku}). Orden {confirmation.id}.
                Proveedor: {confirmation.supplier}. Oficina: {confirmation.office}. user_uuid{" "}
                <span className="mono">{confirmation.user_uuid}</span>. {formatTimestamp(confirmation.created_at)}.
              </p>
            </div>
          ) : null}
          {formError ? (
            <div className="banner" role="alert" tabIndex={-1} ref={alertRef}>
              <h2>No se registró la entrada</h2>
              <p>{formError}</p>
            </div>
          ) : null}
          <div className="field">
            <label htmlFor="asset">Activo</label>
            <select
              id="asset"
              name="asset"
              value={selected ? assetId : ""}
              aria-invalid={fieldErrors.asset_id ? true : undefined}
              onChange={(event) => {
                setAssetId(event.target.value);
                setFormError("");
              }}
            >
              <option value="">Elige un activo</option>
              {assets.map((asset) => (
                <option key={asset.id} value={asset.id}>
                  {asset.name} · {asset.sku} · {asset.office}
                </option>
              ))}
            </select>
            {fieldErrors.asset_id ? <p className="field-error">{fieldErrors.asset_id}</p> : null}
            <p id="entry-stock" className="note" aria-live="polite">
              {stockText}
            </p>
          </div>
          <div className="field">
            <label htmlFor="quantity">Cantidad</label>
            <input
              id="quantity"
              name="quantity"
              inputMode="numeric"
              autoComplete="off"
              value={quantity}
              aria-invalid={fieldErrors.quantity ? true : undefined}
              aria-describedby="entry-stock"
              onChange={(event) => setQuantity(event.target.value)}
            />
            {fieldErrors.quantity ? <p className="field-error">{fieldErrors.quantity}</p> : null}
          </div>
          <div className="field">
            <label htmlFor="supplier">Proveedor (supplier)</label>
            <input
              id="supplier"
              name="supplier"
              autoComplete="organization"
              value={supplier}
              aria-invalid={fieldErrors.supplier ? true : undefined}
              onChange={(event) => setSupplier(event.target.value)}
            />
            {fieldErrors.supplier ? <p className="field-error">{fieldErrors.supplier}</p> : null}
          </div>
          <div className="field">
            <label htmlFor="office">Oficina receptora (office)</label>
            <select
              id="office"
              name="office"
              value={office}
              aria-invalid={fieldErrors.office ? true : undefined}
              onChange={(event) => setOffice(event.target.value === "Miami" ? "Miami" : event.target.value === "Valencia" ? "Valencia" : "")}
            >
              <option value="">Elige una oficina</option>
              <option value="Valencia">Valencia</option>
              <option value="Miami">Miami</option>
            </select>
            {fieldErrors.office ? <p className="field-error">{fieldErrors.office}</p> : null}
          </div>
          <p className="actions">
            <button type="submit" disabled={pending} aria-busy={pending}>
              {pending ? "Registrando la entrada…" : "Registrar entrada de activos"}
            </button>
          </p>
        </form>
      ) : null}
    </>
  );
}
