# `incident_analysis`

Métricas del CSV de tickets de soporte de Nexova. Las reglas de cada fila viven en `packages/shared/nexova_incidents` y las usan este paquete, `scripts/analyze.py`, `scripts/seed_incidents.py` y la API. No hay una segunda copia de la lógica.

La fuente de campos, categorías, estados y reglas es el briefing de la empresa en `scripts/nexova-BRIEFING.en.md` y `scripts/nexova-BRIEFING.es.md` (syllabus `content/contexts/incidents-file-analysis`, empresa Nexova). El fichero de prueba es `scripts/incidents-nexova.csv`.

Un registro es inválido si le falta un campo obligatorio, si categoría o estado no están en la lista, si el formato de `ticket_id` (`NXV-XXXXXX`), `date` (`YYYY-MM-DD`) o `agent_id` (`AGT-XX`) no cuadra, si la descripción tiene menos de 5 caracteres, si el correo no contiene `@`, si un `CLOSED` no trae puntuación, o si la puntuación no es un entero de 1 a 5. Cada regla se cuenta por separado. El total de inválidos cuenta la fila una vez.

La media de satisfacción usa solo tickets válidos con estado `CLOSED` y puntuación, redondeo half-up a dos decimales. Los porcentajes son half-up a un decimal sobre los válidos.

La salida no incluye correos ni descripciones. `analyze_bytes` lanza `AnalysisError` si el fichero está vacío o no es el CSV esperado; el mensaje no copia celdas.

## Uso

```python
from incident_analysis.engine import analyze_bytes

report = analyze_bytes(path.read_bytes(), path.name)
print(report.console())
path_out.write_text(report.csv_text(), encoding="utf-8")
```

`PYTHONPATH` debe incluir el directorio `packages/`.
