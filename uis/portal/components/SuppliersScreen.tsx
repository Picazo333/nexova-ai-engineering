"use client";

import { useEffect, useRef, useState } from "react";

import { ErrorBanner, LoadingState } from "@/components/AsyncStatus";
import { ApiError, apiFetch } from "@/lib/api";
import { categoryLabel, countryLabel, statusLabel } from "@/lib/labels";
import type { Supplier } from "@/lib/types";

export function SuppliersScreen() {
  const [country, setCountry] = useState("");
  const [rows, setRows] = useState<Supplier[] | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [attempt, setAttempt] = useState(0);
  const request = useRef(0);

  useEffect(() => {
    const id = ++request.current;
    const query = country ? `?country=${encodeURIComponent(country)}` : "";
    setLoading(true);
    setError("");
    apiFetch<Supplier[]>(`/suppliers${query}`)
      .then((list) => {
        if (id !== request.current) return;
        setRows(Array.isArray(list) ? list : []);
      })
      .catch((caught: unknown) => {
        if (id !== request.current) return;
        if (caught instanceof ApiError && caught.status === 401) return;
        setError(caught instanceof ApiError ? caught.message : "No se pudo leer el directorio.");
      })
      .finally(() => {
        if (id === request.current) setLoading(false);
      });
  }, [country, attempt]);

  const money = new Intl.NumberFormat("es-ES", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

  return (
    <>
      <h1>Contratos de proveedores</h1>
      <p className="lead">
        Listado de <code>GET /suppliers</code>. La tarifa y el contacto solo llegan si la petición lleva el
        token.
      </p>
      <div className="filters">
        <div className="field">
          <label htmlFor="country">País</label>
          <select id="country" value={country} onChange={(event) => setCountry(event.target.value)}>
            <option value="">Todos</option>
            <option value="Spain">España</option>
            <option value="USA">Estados Unidos</option>
          </select>
        </div>
        {country ? (
          <button className="button secondary" type="button" onClick={() => setCountry("")}>
            Quitar el filtro
          </button>
        ) : null}
      </div>
      {loading ? <LoadingState label="Cargando contratos…" /> : null}
      {error ? (
        <ErrorBanner
          title="No se pudo cargar el directorio"
          message={error}
          onRetry={() => setAttempt((value) => value + 1)}
        />
      ) : null}
      {!loading && rows && rows.length === 0 ? (
        <div className="banner" role="status">
          <h2>No hay contratos con este filtro</h2>
          <p>
            {country
              ? "Ningún contrato coincide con el país elegido."
              : "El directorio no tiene contratos."}
          </p>
          {country ? (
            <p className="actions">
              <button className="button" type="button" onClick={() => setCountry("")}>
                Ver todos los países
              </button>
            </p>
          ) : null}
        </div>
      ) : null}
      {rows && rows.length > 0 ? (
        <div className="table-scroll" role="region" aria-label="Desplazamiento horizontal de los contratos">
          <table>
            <caption>
              {rows.length} {rows.length === 1 ? "contrato" : "contratos"}
              {country ? ` en ${countryLabel(country)}` : ""}
            </caption>
            <thead>
              <tr>
                <th scope="col">Nombre</th>
                <th scope="col">País</th>
                <th scope="col">Categorías</th>
                <th scope="col">Estado</th>
                <th className="num" scope="col">
                  Tarifa mensual
                </th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.id ?? row.name}>
                  <th scope="row">{row.name ?? "Sin nombre"}</th>
                  <td>{countryLabel(row.country ?? "") || "Sin país"}</td>
                  <td>{(row.categories ?? []).map((code) => categoryLabel(code)).join(", ") || "Sin categoría"}</td>
                  <td>{statusLabel(row.status ?? "") || "Sin estado"}</td>
                  <td className="num">
                    {Number.isFinite(row.monthly_rate) ? money.format(row.monthly_rate) : "—"} {row.currency ?? ""}
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
