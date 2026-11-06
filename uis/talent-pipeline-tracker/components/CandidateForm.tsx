"use client";

import Link from "next/link";
import { useEffect, useId, useState } from "react";
import { useSearchParams } from "next/navigation";
import { ErrorStatus, LoadingStatus } from "@/components/AsyncStatus";
import { useTracker } from "@/hooks/useTracker";
import { toErrorMessage } from "@/lib/errors";
import { labelStage, labelStatus } from "@/lib/labels";
import {
  emptyCandidateForm,
  toCandidateWrite,
  validateCandidateForm,
  type CandidateField,
  type CandidateFormValues,
  type FieldErrors,
} from "@/lib/validation";
import type { Candidate } from "@/types/candidate";

const FIELDS: { name: CandidateField; label: string; type: string; required: boolean }[] = [
  { name: "full_name", label: "Nombre completo", type: "text", required: true },
  { name: "email", label: "Correo", type: "email", required: true },
  { name: "phone", label: "Teléfono", type: "tel", required: true },
  { name: "position", label: "Puesto", type: "text", required: true },
  { name: "experience_years", label: "Años de experiencia", type: "number", required: true },
  { name: "linkedin_url", label: "LinkedIn", type: "url", required: false },
  { name: "cv_url", label: "Enlace al CV", type: "url", required: false },
];

export function CandidateForm({ mode, id }: { mode: "create" | "edit"; id?: string }) {
  const api = useTracker();
  const searchParams = useSearchParams();
  const from = searchParams.get("from") ?? "";
  const formId = useId();
  const [values, setValues] = useState<CandidateFormValues>(emptyCandidateForm);
  const [errors, setErrors] = useState<FieldErrors>({});
  const [attempt, setAttempt] = useState(0);
  const [loading, setLoading] = useState(mode === "edit");
  const [loadError, setLoadError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [saved, setSaved] = useState<Candidate | null>(null);

  useEffect(() => {
    if (mode !== "edit" || !id) return;
    const controller = new AbortController();
    let active = true;
    void (async () => {
      try {
        const record = await api.getRecord(id, controller.signal);
        if (!active) return;
        setValues({
          full_name: record.full_name,
          email: record.email,
          phone: record.phone,
          position: record.position,
          linkedin_url: record.linkedin_url ?? "",
          cv_url: record.cv_url ?? "",
          experience_years: String(record.experience_years),
        });
        setLoading(false);
      } catch (cause) {
        if (!active || controller.signal.aborted) return;
        setLoadError(toErrorMessage(cause));
        setLoading(false);
      }
    })();
    return () => {
      active = false;
      controller.abort();
    };
  }, [api, attempt, id, mode]);

  function update(name: CandidateField, value: string) {
    setValues((current) => ({ ...current, [name]: value }));
    setSaved(null);
  }

  async function submit() {
    const nextErrors = validateCandidateForm(values);
    setErrors(nextErrors);
    setSubmitError(null);
    const firstInvalid = FIELDS.find((field) => nextErrors[field.name]);
    if (firstInvalid) {
      document.getElementById(`${formId}-${firstInvalid.name}`)?.focus();
      return;
    }
    setSubmitting(true);
    try {
      const body = toCandidateWrite(values);
      const record =
        mode === "create" ? await api.createRecord(body) : await api.replaceRecord(id ?? "", body);
      setSaved(record);
      if (mode === "create") setValues(emptyCandidateForm());
    } catch (cause) {
      setSubmitError(toErrorMessage(cause));
    } finally {
      setSubmitting(false);
    }
  }

  const backHref = from ? `/?${from}` : "/";
  const detailHref =
    saved && mode === "create"
      ? `/candidates/${saved.id}`
      : id
        ? from
          ? `/candidates/${id}?from=${encodeURIComponent(from)}`
          : `/candidates/${id}`
        : backHref;

  return (
    <>
      <p className="back">
        <Link href={mode === "edit" && id ? detailHref : backHref}>
          {mode === "edit" ? "Volver a la candidatura" : "Volver al listado"}
        </Link>
      </p>
      <h1>{mode === "create" ? "Registrar candidatura" : "Editar candidatura"}</h1>
      <p className="lead">
        {mode === "create"
          ? "El alta pide nombre, correo, teléfono, puesto y años de experiencia. LinkedIn y CV son opcionales."
          : "Corrige los datos de contacto y el puesto. El estado y la etapa se cambian en el detalle."}
      </p>
      {loading ? <LoadingStatus label="Cargando los datos de la candidatura…" /> : null}
      {loadError ? (
        <ErrorStatus
          message={loadError}
          onRetry={() => {
            setLoading(true);
            setLoadError(null);
            setAttempt((value) => value + 1);
          }}
        />
      ) : null}
      {!loading && !loadError ? (
        <form
          className="candidate-form"
          noValidate
          onSubmit={(event) => {
            event.preventDefault();
            if (!submitting) void submit();
          }}
        >
          {Object.keys(errors).length > 0 ? (
            <div className="feedback feedback-error" role="alert">
              <p>Revisa los campos obligatorios antes de enviar.</p>
              <ul>
                {FIELDS.filter((field) => errors[field.name]).map((field) => (
                  <li key={field.name}>
                    <a href={`#${formId}-${field.name}`}>{errors[field.name]}</a>
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
          {FIELDS.map((field) => {
            const error = errors[field.name];
            const describedBy = error ? `${formId}-${field.name}-error` : undefined;
            return (
              <label className="field" key={field.name} htmlFor={`${formId}-${field.name}`}>
                <span>
                  {field.label}
                  {field.required ? <span className="required"> Obligatorio</span> : null}
                </span>
                <input
                  id={`${formId}-${field.name}`}
                  name={field.name}
                  type={field.type}
                  inputMode={field.name === "experience_years" ? "decimal" : undefined}
                  min={field.name === "experience_years" ? 0 : undefined}
                  step={field.name === "experience_years" ? "any" : undefined}
                  value={values[field.name]}
                  required={field.required}
                  aria-invalid={error ? true : undefined}
                  aria-describedby={describedBy}
                  onChange={(event) => update(field.name, event.target.value)}
                />
                {error ? (
                  <span id={describedBy} className="field-error">
                    {error}
                  </span>
                ) : null}
              </label>
            );
          })}
          {submitError ? (
            <p className="feedback feedback-error" role="alert">
              {submitError}
            </p>
          ) : null}
          {saved ? (
            <div className="feedback feedback-success" role="status">
              <p>
                {mode === "create" ? "Candidatura registrada." : "Datos actualizados."} Quedó en{" "}
                {labelStatus(saved.status)}, etapa {labelStage(saved.stage)}.
              </p>
              <Link
                href={
                  from
                    ? `/candidates/${saved.id}?from=${encodeURIComponent(from)}`
                    : `/candidates/${saved.id}`
                }
              >
                Ver {saved.full_name}
              </Link>
            </div>
          ) : null}
          <button className="button button-primary" type="submit" disabled={submitting}>
            {submitting
              ? "Guardando…"
              : mode === "create"
                ? "Registrar candidatura"
                : "Guardar cambios"}
          </button>
        </form>
      ) : null}
    </>
  );
}
