# API de incidencias de Nexova

Un solo proceso FastAPI, como pide `services/README.md`. El router `app/routers/incidents.py` solo traduce HTTP. Las reglas del CSV están en `packages/incident_analysis` y son las mismas que usa `scripts/analyze.py`.

Las rutas de este entregable son las del enunciado, no un prefijo distinto:

- `POST /api/incidents/analyze` — CSV en `multipart/form-data`, campo `file`.
- `GET /api/incidents/results/export` — último análisis correcto, `results.csv`.

Con `Accept: application/json` el análisis responde JSON. Con `Accept: text/html` responde la página del backoffice. El navegador pide un fragmento con la cabecera `X-Report-Fragment: 1`.

No llama a ningún servicio de IA. No guarda el CSV. Guarda el resumen agregado en `services/api/.data/` (ignorado por git) para que la descarga sobreviva a un refresco. Si ese resumen contuviera `@`, no se escribe.

Errores de entrada: fichero ausente, vacío, sin filas, codificación o columnas incorrectas → `400` con `error` y `message`. Por encima de `INCIDENTS_MAX_UPLOAD_BYTES` (32 MiB por defecto) → `413`. Export sin análisis previo → `404`. Un fallo interno no incluye la excepción en la respuesta.

## Arranque

Desde la raíz del repositorio, con Python 3.12:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r services/api/requirements.txt
PYTHONPATH=packages:services/api uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Abre `http://127.0.0.1:8000`.

## Pruebas

```bash
pip install -r services/api/requirements.txt
python -m pytest -q
```

## Variables

| Variable | Defecto | Uso |
| --- | --- | --- |
| `INCIDENTS_DATA_DIR` | `services/api/.data` | Carpeta del último resumen |
| `INCIDENTS_MAX_UPLOAD_BYTES` | `33554432` | Tope del CSV |
| `INCIDENTS_CORS_ORIGINS` | localhost en los puertos 8000 y 3000 | Orígenes permitidos, lista separada por comas. Sin credenciales y sin comodín. |
