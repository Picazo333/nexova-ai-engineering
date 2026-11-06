"""Texto del reporte de métricas. Los números vienen del ajuste, no de una tabla fija."""

from __future__ import annotations

MONTHS_ES = {
    1: "enero",
    2: "febrero",
    3: "marzo",
    4: "abril",
    5: "mayo",
    6: "junio",
    7: "julio",
    8: "agosto",
    9: "septiembre",
    10: "octubre",
    11: "noviembre",
    12: "diciembre",
}


def _pct(ratio: float) -> str:
    return f"{ratio * 100:.2f} %"


def _usd(value: float) -> str:
    return f"{value:,.2f}"


def _num(value: float, digits: int = 4) -> str:
    return f"{value:,.{digits}f}"


def render_markdown(payload: dict) -> str:
    metrics = payload["test_metrics"]
    split = payload["split"]
    season = payload["seasonality"]
    growth = payload["growth"]
    august = season["august"]
    january = season["january"]
    february = season["february"]
    direction = (
        "La dirección coincide con el briefing: agosto es el mes más bajo y enero y febrero quedan por encima de la media de su año."
        if season["direction_matches_briefing"]
        else "La dirección no reproduce el patrón descrito en el briefing. Los porcentajes de abajo son los medidos, no los del texto."
    )
    bands = (
        "Los tres meses caen dentro de las bandas del briefing (agosto −15 % a −25 %; enero y febrero +15 % a +20 %)."
        if season["percent_bands_match_briefing"]
        else "Algún mes queda fuera de la banda exacta del briefing. No se ajustó la serie para meterla en esa banda."
    )
    yoy_rows = "\n".join(
        f"| {year} | {_pct(rate)} |" for year, rate in growth["yoy_growth"].items()
    )
    profile_rows = "\n".join(
        f"| {MONTHS_ES[month]} | {_pct(value - 1.0)} |"
        for month, value in season["profile_by_month"].items()
    )
    importance_rows = "\n".join(
        f"| `{item['feature']}` | {item['importance']:.4f} |"
        for item in payload["feature_importance"]
    )
    level_note = ""
    if metrics["psi_revenue_level"] > 0.25:
        level_note = (
            " En esta serie el PSI de nivel queda por encima de 0.25 porque el ingreso de 2024–2025 "
            "sale del rango de los años de entrenamiento: es el crecimiento, no un fallo del pronóstico. "
            "La lectura de estabilidad estacional es el PSI de forma."
        )
    if metrics["train_rmse_usd_diagnostic"] < metrics["rmse_usd"]:
        train_gap = (
            "El RMSE de entrenamiento es menor que el de prueba: el bosque se pega más a los años "
            "que ya vio. Los hiperparámetros no se reajustaron mirando 2024–2025."
        )
    else:
        train_gap = "El RMSE de entrenamiento no queda por debajo del de prueba."
    growth_sentence = (
        "Todos los crecimientos anuales observados son positivos."
        if growth["all_yoy_positive"]
        else "Hay al menos un año con crecimiento negativo. El briefing describe crecimiento siempre positivo; esta tabla es la medición."
    )
    return f"""# Pronóstico de ingresos de Nexova

Métricas del conjunto de prueba ({split["test_start"]} a {split["test_end"]}). No son métricas de entrenamiento.

## Resultado en los 24 meses de prueba

| Métrica | Valor | Lectura |
| --- | --- | --- |
| MSE | {_usd(metrics["mse_usd2"])} USD² | Media de (real − pronóstico)² |
| RMSE | {_usd(metrics["rmse_usd"])} USD | Raíz del MSE, en dólares del mes |
| RMSE / ingreso medio | {_pct(metrics["rmse_over_mean_revenue"])} | Ese error frente al ingreso mensual medio de la prueba ({_usd(metrics["mean_test_revenue_usd"])} USD) |
| MAE | {_usd(metrics["mae_usd"])} USD | Error absoluto medio, complemento del MSE |
| PSI (nivel) | {_num(metrics["psi_revenue_level"])} | Cambio de la distribución de `revenue_usd` entre entrenamiento y prueba |
| PSI (forma) | {_num(metrics["psi_revenue_shape"])} | Igual, después de dividir cada mes por la media de su año |
| Gini | {_num(metrics["gini"])} | Capacidad de ordenar meses de más ingreso a menos. 1 sería un orden perfecto |
| K² | {_num(metrics["k2_statistic"])} (p = {_num(metrics["k2_pvalue"])}) | D'Agostino–Pearson sobre los residuos de prueba |

Referencia, no es el modelo: repetir el ingreso del mes anterior da un RMSE de {_usd(metrics["baseline_lag1_rmse_usd"])} USD en los mismos 24 meses.

## Qué mide cada métrica, y por qué un MSE bajo no basta

- **MSE** es el error cuadrático medio en USD². Castiga más un mes muy desviado que muchos meses casi acertados. Un valor bajo en entrenamiento puede ser memoria del pasado. Por eso el MSE que vale es el de 2024–2025, que el ajuste no vio.
- **PSI** (Population Stability Index) compara dos distribuciones. No dice si el pronóstico acertó el mes. Dice si el periodo de prueba se parece al de entrenamiento. El CSV oficial solo trae `business_line=consolidated`, así que no hay un PSI del mix headhunting / outsourcing / formación: inventar esas series falsearía el briefing. El PSI de nivel sube si el ingreso creció. El PSI de forma mira el perfil dentro del año, sin el nivel.{level_note}
- **Gini** normalizado mide si el pronóstico ordena bien los meses. Un MSE moderado puede convivir con un modelo que no distingue un agosto flojo de una caída anormal. El Gini es esa distinción, que es la que el briefing pide para Laura.
- **K²** es el estadístico de D'Agostino y Pearson (`scipy.stats.normaltest`) sobre los residuos de la prueba. Un p pequeño rechaza que esos residuos sean normales: el error no es una nube simétrica alrededor de cero. Con 24 meses el contraste es débil; se publica el número y el p-valor.

El MSE de entrenamiento se calcula solo como diagnóstico y no es el resultado: {_usd(metrics["train_mse_usd2_diagnostic"])} USD² (RMSE {_usd(metrics["train_rmse_usd_diagnostic"])} USD). {train_gap}

## Split

Corte en {split["cutoff_year"]}: los años anteriores a ese corte son entrenamiento y ese año más el siguiente son prueba. Origen de la serie cruda: {split["origin_year"]}.

| Conjunto | Meses | Desde | Hasta | Años |
| --- | --- | --- | --- | --- |
| Entrenamiento | {split["train_rows"]} | {split["train_start"]} | {split["train_end"]} | {", ".join(str(year) for year in split["train_years"])} |
| Prueba | {split["test_rows"]} | {split["test_start"]} | {split["test_end"]} | {", ".join(str(year) for year in split["test_years"])} |

Se descartaron {split["warmup_rows_dropped"]} meses iniciales porque el lag de 12 meses y el rolling de 12 meses no tienen pasado suficiente. Esos meses son 2016. No se movieron a la prueba. El escalador se ajustó solo con el entrenamiento.

## Modelo

{payload["model"]["justification"]}

Semilla `random_state={payload["model"]["random_state"]}`. Árboles: {payload["model"]["n_estimators"]}. Profundidad máxima: {payload["model"]["max_depth"]}. Mínimo de muestras por hoja: {payload["model"]["min_samples_leaf"]}.

Banda del gráfico: {payload["variability_band"]}

## Features usadas en el ajuste

{chr(10).join(f"- `{name}`" for name in payload["features"])}

`active_contracts` y `avg_contract_value_usd` del mismo mes no entran: son contemporáneos al objetivo. Entran sus lags.

| Feature | Importancia de impureza |
| --- | --- |
{importance_rows}

## Estacionalidad frente al briefing

Descomposición {season["model"]}, periodo {season["period"]}, con `statsmodels.tsa.seasonal.seasonal_decompose`. {direction} {bands}

| Mes | Frente a la media de su año | Factor estacional medio |
| --- | --- | --- |
| agosto | {_pct(august["gap_vs_year_mean"])} | {august["seasonal_factor"]:.4f} |
| enero | {_pct(january["gap_vs_year_mean"])} | {january["seasonal_factor"]:.4f} |
| febrero | {_pct(february["gap_vs_year_mean"])} | {february["seasonal_factor"]:.4f} |

Desviación absoluta media del resto de meses frente a la media de su año: {_pct(season["other_months_mean_abs_gap"])}. El briefing habla de un movimiento moderado, del orden de ±5 %, en esos meses.

Perfil medio de todos los meses (ingreso / media del mismo año):

| Mes | Diferencia frente a 1 |
| --- | --- |
{profile_rows}

## Crecimiento anual observado

{growth_sentence} Mínimo {_pct(growth["min_yoy"])}, máximo {_pct(growth["max_yoy"])}. El briefing describe un crecimiento base del 4 % con años alternando cerca del 1 % y del 7 %. La tabla es el dato del CSV, no ese generador.

| Año | Variación del ingreso anual |
| --- | --- |
{yoy_rows}

## Datos

- Archivo: `{payload["dataset"]["path"]}`
- SHA-256: `{payload["dataset"]["sha256"]}`
- Coincide con el hash oficial: {payload["dataset"]["official_hash_matches"]}
- Filas leídas: {payload["dataset"]["rows_read"]}. Nulos tirados antes del modelo: {payload["dataset"]["rows_dropped_null"]}. Filas `consolidated`: {payload["dataset"]["rows_consolidated"]}.
- Fuente tipográfica de las gráficas en esta máquina: {payload["font"]}.
"""


def render_terminal(payload: dict) -> str:
    metrics = payload["test_metrics"]
    split = payload["split"]
    season = payload["seasonality"]
    return "\n".join(
        [
            "Nexova — pronóstico de ingresos mensuales",
            f"Dataset: data/raw/nexova_sales.csv",
            f"SHA-256: {payload['dataset']['sha256']}",
            f"Hash oficial: {payload['dataset']['official_hash_matches']}",
            f"Nulos eliminados: {payload['dataset']['rows_dropped_null']}",
            (
                f"Split: entrenamiento {split['train_start']} → {split['train_end']} "
                f"({split['train_rows']} meses); prueba {split['test_start']} → {split['test_end']} "
                f"({split['test_rows']} meses). Calentamiento causal descartado: {split['warmup_rows_dropped']} meses."
            ),
            "Modelo: RandomForestRegressor (scikit-learn), random_state=42",
            "Métricas en prueba (no en entrenamiento):",
            f"  MSE: {_usd(metrics['mse_usd2'])} USD²",
            (
                f"  RMSE: {_usd(metrics['rmse_usd'])} USD "
                f"({_pct(metrics['rmse_over_mean_revenue'])} del ingreso mensual medio de la prueba)"
            ),
            f"  PSI nivel: {_num(metrics['psi_revenue_level'])}",
            f"  PSI forma: {_num(metrics['psi_revenue_shape'])}",
            f"  Gini: {_num(metrics['gini'])}",
            f"  K²: {_num(metrics['k2_statistic'])} (p={_num(metrics['k2_pvalue'])})",
            f"  RMSE de referencia (lag 1): {_usd(metrics['baseline_lag1_rmse_usd'])} USD",
            (
                "Estacionalidad: agosto "
                f"{_pct(season['august']['gap_vs_year_mean'])} frente a la media del año; "
                f"dirección alineada con el briefing: {season['direction_matches_briefing']}; "
                f"bandas exactas: {season['percent_bands_match_briefing']}."
            ),
            "Gráficas: output/forecast_vs_actual.png, output/decomposition.png, output/feature_importance.png",
            "Detalle: output/metrics.md",
        ]
    )
