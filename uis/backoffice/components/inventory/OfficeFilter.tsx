"use client";

export function OfficeFilter({
  id,
  value,
  onChange,
}: {
  id: string;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <div className="field">
      <label htmlFor={id}>Oficina</label>
      <select id={id} value={value} onChange={(event) => onChange(event.target.value)}>
        <option value="">Valencia y Miami</option>
        <option value="Valencia">Valencia</option>
        <option value="Miami">Miami</option>
      </select>
    </div>
  );
}

export function cleanOffice(value: string | undefined): string {
  return value === "Valencia" || value === "Miami" ? value : "";
}
