"use client";

import { useEffect, useRef, useState } from "react";

import { EmptyState, ErrorBanner, LoadingState } from "@/components/AsyncStatus";
import { StockBadge } from "@/components/inventory/StockBadge";
import { ApiError, messageOf } from "@/lib/http";
import {
  createAssetExit,
  getAsset,
  listAssets,
  type Asset,
  type ExitType,
  type InventoryOrder,
  type Office,
} from "@/lib/inventory";
import { formatTimestamp } from "@/lib/labels";
import { parseQuantity } from "@/lib/quantity";

type StockState =
  | { kind: "idle" }
  | { kind: "loading" }
  | { kind: "ready"; asset: Asset }
  | { kind: "error"; message: string };

export function ExitForm({ initialAsset }: { initialAsset: string }) {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loadPhase, setLoadPhase] = useState<"loading" | "ready" | "error">("loading");
  const [loadError, setLoadError] = useState("");
  const [attempt, setAttempt] = useState(0);
  const [assetId, setAssetId] = useState(initialAsset);
  const [stock, setStock] = useState<StockState>({ kind: "idle" });
  const [quantity, setQuantity] = useState("");
  const [exitType, setExitType] = useState<ExitType>("allocation");
  const [assignedTo, setAssignedTo] = useState("");
  const [office, setOffice] = useState<Office | "">("");
  const [pending, setPending] = useState(false);
  const [formError, setFormError] = useState("");
  const [quantityError, setQuantityError] = useState("");
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [confirmation, setConfirmation] = useState<InventoryOrder | null>(null);
  const confirmRef = useRef<HTMLDivElement>(null);
  const alertRef = useRef<HTMLDivElement>(null);
  const quantityErrorRef = useRef<HTMLParagraphElement>(null);
  const submitId = useRef(0);
  const stockRequest = useRef(0);
  const officeTouched = useRef("");
  const [stockAttempt, setStockAttempt] = useState(0);

  useEffect(() => {
    setAssetId(initialAsset);
  }, [initialAsset]);

  useEffect(() => {
    let cancelled = false;
    setLoadPhase("loading");
    listAssets()
      .then((rows) => {
        if (cancelled) return;
        setAssets(rows);
        setLoadError("");
        setLoadPhase("ready");
      })
      .catch((reason: unknown) => {
        if (cancelled) return;
        setLoadError(messageOf(reason));
        setLoadPhase("error");
      });
    return () => {
      cancelled = true;
    };
  }, [attempt]);

  const selected = assets.find((asset) => String(asset.id) === assetId) ?? null;

  useEffect(() => {
    if (!selected) {
      setStock({ kind: "idle" });
      return;
    }
    const request = ++stockRequest.current;
    setStock({ kind: "loading" });
    getAsset(selected.id)
      .then((asset) => {
        if (request !== stockRequest.current) return;
        setStock({ kind: "ready", asset });
        if (officeTouched.current !== String(asset.id)) {
          officeTouched.current = String(asset.id);
          if (asset.office === "Valencia" || asset.office === "Miami") setOffice(asset.office);
        }
      })
      .catch((reason: unknown) => {
        if (request !== stockRequest.current) return;
        setStock({ kind: "error", message: messageOf(reason) });
      });
  }, [selected, stockAttempt]);

  useEffect(() => {
    if (quantityError) quantityErrorRef.current?.focus();
  }, [quantityError]);

  const parsed = parseQuantity(quantity);
  const available = stock.kind === "ready" ? stock.asset.current_stock : null;
  const overStock = parsed != null && available != null && parsed > available;

  function onExitType(next: ExitType) {
    setExitType(next);
    if (next === "consumption") setAssignedTo("");
    setFieldErrors((current) => ({ ...current, assigned_to: "", exit_type: "" }));
  }

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (pending) return;
    const problems: Record<string, string> = {};
    if (!selected) problems.asset_id = "Elige un activo por su nombre.";
    else if (stock.kind !== "ready") problems.asset_id = "Espera a que cargue el stock actual antes de enviar.";
    if (parsed == null) problems.quantity = "La cantidad tiene que ser un entero mayor que cero.";
    if (exitType === "allocation" && !assignedTo.trim()) {
      problems.assigned_to = "La asignación necesita el identificador de la persona (assigned_to).";
    }
    if (office !== "Valencia" && office !== "Miami") problems.office = "Elige Valencia o Miami.";
    setFieldErrors(problems);
    if (problems.quantity) setQuantityError("");
    if (Object.keys(problems).length > 0 || !selected || parsed == null || stock.kind !== "ready" || (office !== "Valencia" && office !== "Miami")) {
      setFormError("Revisa los campos antes de registrar la salida.");
      alertRef.current?.focus();
      return;
    }
    const id = ++submitId.current;
    setPending(true);
    setFormError("");
    setQuantityError("");
    setConfirmation(null);
    try {
      const order = await createAssetExit({
        asset_id: selected.id,
        quantity: parsed,
        exit_type: exitType,
        assigned_to: exitType === "allocation" ? assignedTo.trim() : null,
        office,
      });
      if (id !== submitId.current) return;
      setConfirmation(order);
      setQuantity("");
      setAssignedTo("");
      setAssetId("");
      setOffice("");
      setStock({ kind: "idle" });
      officeTouched.current = "";
      setFieldErrors({});
      confirmRef.current?.focus();
    } catch (reason: unknown) {
      if (id !== submitId.current) return;
      if (reason instanceof ApiError) {
        setFieldErrors(reason.fields);
        if (reason.status === 400) {
          setQuantityError(reason.message);
          setFormError("");
        } else {
          setFormError(reason.message);
        }
      } else {
        setFormError(messageOf(reason));
      }
      if (!(reason instanceof ApiError && reason.status === 400)) alertRef.current?.focus();
    } finally {
      if (id === submitId.current) setPending(false);
    }
  }

  return (
    <>
      <h1>Salida de activos</h1>
      <p className="lead">
        Registra una asignación o un consumo. El envío crea un <code>AssetExit</code> con{" "}
        <code>POST /inventory/orders/outbound</code>. Si la cantidad supera el stock, la API responde 400 y no escribe
        la fila.
      </p>
      {loadPhase === "loading" && assets.length === 0 ? <LoadingState label="Cargando activos…" /> : null}
      {loadPhase === "error" && assets.length === 0 ? (
        <ErrorBanner title="No se pudieron cargar los activos" message={loadError} onRetry={() => setAttempt((value) => value + 1)} />
      ) : null}
      {loadPhase === "ready" && assets.length === 0 ? (
        <EmptyState
          title="No hay activos para una salida"
          message="La API no tiene ningún Asset. Sin un activo no se puede consultar el stock."
          href="/backoffice/inventory/products"
          action="Volver a activos"
        />
      ) : null}
      {assets.length > 0 ? (
        <form onSubmit={onSubmit} noValidate>
          {confirmation ? (
            <div className="banner ok result-panel" data-motion-node data-arrived="true" role="status" tabIndex={-1} ref={confirmRef} data-testid="confirm">
              <h2>Salida registrada</h2>
              <p>
                {confirmation.quantity} × {confirmation.asset_name} ({confirmation.asset_sku}). Orden {confirmation.id}.
                Tipo: {confirmation.exit_type}.{" "}
                {confirmation.assigned_to ? `assigned_to ${confirmation.assigned_to}. ` : "Sin assigned_to. "}
                user_uuid <span className="mono">{confirmation.user_uuid}</span>. {formatTimestamp(confirmation.created_at)}.
              </p>
            </div>
          ) : null}
          {formError ? (
            <div className="banner" role="alert" tabIndex={-1} ref={alertRef}>
              <h2>No se registró la salida</h2>
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
                setQuantityError("");
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
          </div>
          <div className="stock-panel" aria-live="polite" data-testid="stock-now">
            {stock.kind === "idle" ? <p className="note">Elige un activo para ver su stock actual antes de enviar.</p> : null}
            {stock.kind === "loading" ? <LoadingState label="Consultando el stock actual…" /> : null}
            {stock.kind === "ready" ? (
              <p>
                Stock actual (<code>current_stock</code>) de {stock.asset.name}: <StockBadge stock={stock.asset.current_stock} />
              </p>
            ) : null}
            {stock.kind === "error" ? (
              <ErrorBanner title="No se pudo leer el stock" message={stock.message} onRetry={() => setStockAttempt((value) => value + 1)} />
            ) : null}
          </div>
          <div className="field">
            <label htmlFor="quantity">Cantidad</label>
            <input
              id="quantity"
              name="quantity"
              inputMode="numeric"
              autoComplete="off"
              value={quantity}
              aria-invalid={quantityError || fieldErrors.quantity || overStock ? true : undefined}
              aria-describedby="quantity-warning quantity-api-error"
              onChange={(event) => {
                setQuantity(event.target.value);
                setQuantityError("");
              }}
            />
            {fieldErrors.quantity ? <p className="field-error">{fieldErrors.quantity}</p> : null}
            {overStock ? (
              <div className="banner warn" id="quantity-warning" role="status" data-testid="stock-warning">
                <h2>Aviso</h2>
                <p>
                  La cantidad ({parsed}) supera el stock actual ({available}). Puedes enviarla: la API aplica la regla y,
                  si no hay unidades, responderá 400.
                </p>
              </div>
            ) : (
              <p id="quantity-warning" className="note">
                El aviso aparece si la cantidad supera el stock mostrado.
              </p>
            )}
            {quantityError ? (
              <p className="field-error" id="quantity-api-error" tabIndex={-1} role="alert" data-testid="api-error" ref={quantityErrorRef}>
                {quantityError}
              </p>
            ) : (
              <p id="quantity-api-error" className="note" hidden>
                Sin error de la API.
              </p>
            )}
          </div>
          <fieldset className="choices">
            <legend>Tipo de salida (exit_type)</legend>
            <label className="choice">
              <input
                type="radio"
                name="exit_type"
                value="allocation"
                checked={exitType === "allocation"}
                onChange={() => onExitType("allocation")}
              />
              Asignación a una persona
            </label>
            <label className="choice">
              <input
                type="radio"
                name="exit_type"
                value="consumption"
                checked={exitType === "consumption"}
                onChange={() => onExitType("consumption")}
              />
              Consumo
            </label>
          </fieldset>
          <div className="field">
            <label htmlFor="assigned_to">assigned_to</label>
            <input
              id="assigned_to"
              name="assigned_to"
              autoComplete="off"
              value={exitType === "consumption" ? "" : assignedTo}
              disabled={exitType === "consumption"}
              aria-invalid={fieldErrors.assigned_to ? true : undefined}
              onChange={(event) => setAssignedTo(event.target.value)}
            />
            <p className="note">
              {exitType === "allocation"
                ? "Obligatorio en una asignación. Usa el identificador interno, por ejemplo NXV-EMP-1042."
                : "En un consumo assigned_to va vacío. La API lo exige así."}
            </p>
            {fieldErrors.assigned_to ? <p className="field-error">{fieldErrors.assigned_to}</p> : null}
          </div>
          <div className="field">
            <label htmlFor="office">Oficina (office)</label>
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
            <button type="submit" disabled={pending || stock.kind === "loading"} aria-busy={pending}>
              {pending ? "Registrando la salida…" : "Registrar salida de activos"}
            </button>
          </p>
        </form>
      ) : null}
    </>
  );
}
