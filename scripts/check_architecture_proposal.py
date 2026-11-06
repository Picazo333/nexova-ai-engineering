#!/usr/bin/env python3
"""Comprueba docs/ARCHITECTURE_PROPOSAL.md contra el encargo de arquitectura.

Confirma secciones obligatorias, convenciones de FastAPI citadas, riesgos,
diagramas Mermaid cerrados y supuestos marcados. No instala FastAPI.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = ROOT / "docs" / "ARCHITECTURE_PROPOSAL.md"

REQUIRED_H2 = [
    "## Patrón arquitectónico",
    "## Estructura de carpetas y módulos",
    "## Endpoints y routers",
    "## Cómo la estructura estándar de FastAPI influye en esta propuesta",
    "## Frontend y backend como sistemas separados",
    "## Decisiones técnicas iniciales",
    "## Riesgos y puntos de atención",
    "## Mapa de decisiones",
    "## Supuestos",
    "## Fuentes",
]

REQUIRED_PHRASES = [
    "arquitectura en capas",
    "APIRouter",
    "include_router",
    "CORSMiddleware",
    "variables de entorno",
    "https://fastapi.tiangolo.com/tutorial/bigger-applications/",
    "https://fastapi.tiangolo.com/tutorial/cors/",
    "https://fastapi.tiangolo.com/advanced/settings/",
    "Nexova",
    "validation.js",
    "services/api",
    "monorepo",
    "MVC",
    "Serverless",
    "Supuesto:",
]

MERMAID_TYPES = ("flowchart", "sequenceDiagram", "stateDiagram", "classDiagram")
RISKS_HEADING = "## Riesgos y puntos de atención"
MIN_RISKS = 2
MIN_MERMAID = 2


def check_text(text: str) -> list[str]:
    errors: list[str] = []
    if not text.endswith("\n"):
        errors.append("el documento debe terminar en un salto de línea")
    if "\t" in text:
        errors.append("el documento contiene tabuladores")

    lines = text.splitlines()
    headings = [
        (index, line)
        for index, line in enumerate(lines, start=1)
        if line.startswith("#") and not line.startswith("####")
    ]
    h1 = [line for _, line in headings if line.startswith("# ") and not line.startswith("## ")]
    if len(h1) != 1:
        errors.append(f"hace falta un único h1; hay {len(h1)}")

    previous_level = 0
    for number, line in headings:
        level = len(line) - len(line.lstrip("#"))
        if previous_level and level > previous_level + 1:
            errors.append(f"línea {number}: el encabezado salta de nivel ({line})")
        previous_level = level

    for heading in REQUIRED_H2:
        if heading not in lines:
            errors.append(f"falta la sección {heading}")

    positions = []
    for heading in REQUIRED_H2:
        if heading in lines:
            positions.append(lines.index(heading))
    if positions != sorted(positions):
        errors.append("las secciones obligatorias no aparecen en el orden esperado")

    for phrase in REQUIRED_PHRASES:
        if phrase not in text:
            errors.append(f"falta la mención obligatoria: {phrase}")

    if "```" in text:
        fences = [i for i, line in enumerate(lines) if line.startswith("```")]
        if len(fences) % 2 != 0:
            errors.append("hay un bloque de código sin cerrar")

    mermaid: list[str] = []
    in_mermaid = False
    buffer: list[str] = []
    for number, line in enumerate(lines, start=1):
        if line.startswith("```"):
            if in_mermaid:
                mermaid.append("\n".join(buffer))
                in_mermaid = False
                buffer = []
            elif line.strip() == "```mermaid":
                in_mermaid = True
            continue
        if in_mermaid:
            buffer.append(line)
    if in_mermaid:
        errors.append("un bloque mermaid quedó abierto")
    if len(mermaid) < MIN_MERMAID:
        errors.append(f"hacen falta al menos {MIN_MERMAID} diagramas mermaid; hay {len(mermaid)}")
    for index, block in enumerate(mermaid, start=1):
        first = next((item.strip() for item in block.splitlines() if item.strip()), "")
        if not first.startswith(MERMAID_TYPES):
            errors.append(f"el diagrama mermaid {index} no declara un tipo conocido: {first!r}")

    if RISKS_HEADING in lines:
        start = lines.index(RISKS_HEADING) + 1
        end = len(lines)
        for offset, line in enumerate(lines[start:], start=start):
            if line.startswith("## ") and not line.startswith("### "):
                end = offset
                break
        risks = [line for line in lines[start:end] if line.startswith("### ")]
        if len(risks) < MIN_RISKS:
            errors.append(f"la sección de riesgos tiene {len(risks)} apartados; el mínimo es {MIN_RISKS}")

    if "El mismo mapa en texto:" not in text and "El mismo flujo en texto:" not in text:
        errors.append("falta la alternativa textual de los diagramas")

    return errors


def minimal_valid() -> str:
    body = ["# Propuesta de arquitectura de backend", ""]
    phrases = " ".join(REQUIRED_PHRASES)
    for heading in REQUIRED_H2:
        body.append(heading)
        body.append("")
        body.append(phrases)
        body.append("")
        if heading == RISKS_HEADING:
            body.extend(["### Riesgo uno", "", "Consecuencia.", "", "### Riesgo dos", "", "Consecuencia.", ""])
        if heading == "## Patrón arquitectónico":
            body.extend(
                [
                    "```mermaid",
                    "flowchart TB",
                    "  a[A] --> b[B]",
                    "```",
                    "",
                    "El mismo mapa en texto: A precede a B.",
                    "",
                    "```mermaid",
                    "sequenceDiagram",
                    "  participant A",
                    "  participant B",
                    "  A->>B: hola",
                    "```",
                    "",
                    "El mismo flujo en texto: A llama a B.",
                    "",
                ]
            )
    return "\n".join(body) + "\n"


def self_test() -> list[str]:
    failures: list[str] = []
    valid_errors = check_text(minimal_valid())
    if valid_errors:
        failures.append("el documento mínimo válido fue rechazado: " + "; ".join(valid_errors))

    broken = minimal_valid().replace("## Riesgos y puntos de atención\n", "", 1)
    broken_errors = check_text(broken)
    if not any("Riesgos" in item or "riesgos" in item for item in broken_errors):
        failures.append("un documento sin la sección de riesgos no fue rechazado")

    one_risk = minimal_valid().replace("### Riesgo dos\n", "#### Nota\n", 1)
    one_risk_errors = check_text(one_risk)
    if not any("riesgos" in item for item in one_risk_errors):
        failures.append("un documento con un solo riesgo no fue rechazado")

    bad_mermaid = minimal_valid().replace("flowchart TB", "pie", 1)
    mermaid_errors = check_text(bad_mermaid)
    if not any("mermaid" in item for item in mermaid_errors):
        failures.append("un diagrama mermaid de tipo desconocido no fue rechazado")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="ejecuta comprobaciones del propio checker")
    parser.add_argument("--emit-mermaid", type=Path, help="escribe cada bloque mermaid en este directorio")
    parser.add_argument("document", nargs="?", type=Path, default=DOCUMENT)
    args = parser.parse_args()

    if args.self_test:
        failures = self_test()
        if failures:
            for item in failures:
                print(f"FAIL {item}", file=sys.stderr)
            return 1
        print("PASS self-test")
        return 0

    path = args.document
    if not path.is_file():
        print(f"FAIL no existe {path}", file=sys.stderr)
        return 1
    text = path.read_text(encoding="utf-8")
    errors = check_text(text)
    if args.emit_mermaid:
        args.emit_mermaid.mkdir(parents=True, exist_ok=True)
        blocks = []
        capture = False
        buf: list[str] = []
        for line in text.splitlines():
            if line.strip() == "```mermaid":
                capture = True
                buf = []
                continue
            if capture and line.startswith("```"):
                blocks.append("\n".join(buf) + "\n")
                capture = False
                continue
            if capture:
                buf.append(line)
        for index, block in enumerate(blocks, start=1):
            (args.emit_mermaid / f"diagram-{index}.mmd").write_text(block, encoding="utf-8")
        print(f"mermaid blocks: {len(blocks)} -> {args.emit_mermaid}")

    if errors:
        for item in errors:
            print(f"FAIL {item}", file=sys.stderr)
        return 1
    print(f"PASS {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
