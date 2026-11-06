"use client";

import type { IncidentReport } from "@/lib/types";

export function IncidentResult({
  report,
  onDownload,
}: {
  report: IncidentReport;
  onDownload: () => void;
}) {
  const rules = report.invalid_breakdown.filter((item) => item.count > 0);

  return (
    <section className="result-panel" data-motion-node="" data-arrived="true" aria-labelledby="resultado">
      <h2 id="resultado">Resultado</h2>
      <p>{report.summary_es}</p>
      <div className="table-scroll" role="region" aria-label="Desplazamiento horizontal de los totales">
        <table>
          <caption>Totales del fichero</caption>
          <thead>
            <tr>
              <th scope="col">Métrica</th>
              <th className="num" scope="col">
                Cantidad
              </th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Registros en el fichero</td>
              <td className="num">{report.total_records}</td>
            </tr>
            <tr>
              <td>Válidos</td>
              <td className="num">{report.valid_records}</td>
            </tr>
            <tr>
              <td>Inválidos o incompletos</td>
              <td className="num">{report.invalid_records}</td>
            </tr>
          </tbody>
        </table>
      </div>
      {rules.length === 0 ? (
        <p>Ninguna fila inválida en este fichero.</p>
      ) : (
        <div className="table-scroll" role="region" aria-label="Desplazamiento horizontal de las reglas">
          <table>
            <caption>Reglas con filas inválidas</caption>
            <thead>
              <tr>
                <th scope="col">Problema</th>
                <th className="num" scope="col">
                  Registros
                </th>
              </tr>
            </thead>
            <tbody>
              {rules.map((rule) => (
                <tr key={rule.code}>
                  <td>{rule.label_es}</td>
                  <td className="num">{rule.count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <p className="actions">
        <button className="button secondary" type="button" onClick={onDownload}>
          Descargar results.csv
        </button>
      </p>
    </section>
  );
}
