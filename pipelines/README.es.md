# Pronóstico de ingreso mensual de Nexova

Pronóstico del ingreso consolidado mensual de Nexova Solutions. La serie es el archivo oficial `data/raw/nexova_sales.csv` (2016-01 a 2025-12, 120 filas). No se genera en este repositorio. Procedencia y SHA-256: [`data/raw/SALES_DATASET.md`](../data/raw/SALES_DATASET.md). Columnas y estacionalidad: [`data/raw/nexova-BRIEFING.es.md`](../data/raw/nexova-BRIEFING.es.md).

_English version: [README.md](./README.md)._

## Cómo ejecutarlo

En la raíz del repositorio, con [uv](https://docs.astral.sh/uv/):

```bash
uv sync --all-groups
uv run python scripts/train_sales_forecast.py
uv run pytest
```

El script escribe:

| Archivo | Contenido |
| --- | --- |
| `output/metrics.md` | Métricas de prueba, split, contraste de estacionalidad y crecimiento anual observado |
| `output/metrics.json` | Los mismos números |
| `output/forecast_vs_actual.png` | Ingreso real de 2024–2025, pronóstico y banda de dispersión entre árboles |
| `output/decomposition.png` | Tendencia, estacionalidad y residual multiplicativos |
| `output/feature_importance.png` | Importancia de impureza de las features con las que parte el bosque |
| `output/train.log` | El resumen de terminal |

No hay una segunda copia de la serie en `data/process/`. El script recalcula las features.

## Qué tiene que predecir

El objetivo es `revenue_usd` de `business_line=consolidated`. El entrenamiento usa los primeros 8 años calendario de la serie cruda (2016–2023). La comprobación usa los 2 años más recientes (2024–2025). El corte es cronológico. No hay barajado.

Los primeros 12 meses se descartan después de construir las features: un lag de 12 meses y un rolling de 12 meses no tienen pasado. Esos meses son todo 2016. No pasan a la prueba. El entrenamiento útil es 2017-01 a 2023-12 (84 meses). La prueba es 2024-01 a 2025-12 (24 meses). El año de corte es `año_origen + 8` (2024). El año de origen sale del archivo crudo, no de la primera fila que sobrevive al calentamiento.

## Features

Todas entran a `RandomForestRegressor`. La columna objetivo no entra.

| Familia | Columnas | Regla |
| --- | --- | --- |
| Lag | `revenue_lag_1`, `revenue_lag_12`, `contracts_lag_1`, `avg_contract_value_lag_1` | `shift`. La fila `t` ve el valor en `t-k`, nunca en `t` ni después. |
| Rolling | `revenue_roll_mean_3`, `revenue_roll_std_12` | Primero `shift(1)`, luego `rolling`. El mes en curso queda fuera de la ventana. |
| Calendario | `month_sin`, `month_cos`, `quarter`, `trend_month_index` | Salen de la fecha, que se conoce antes de cerrar el ingreso. |

`active_contracts` y `avg_contract_value_usd` del mismo mes no son features. Describen el mes que se quiere pronosticar.

Los nulos y las celdas vacías de las columnas crudas se tiran antes de entrenar. El archivo oficial no trae ninguno (`rows_dropped_null = 0`). Los nulos del calentamiento de los lags se tiran y se cuentan.

`StandardScaler` se ajusta solo con las filas de entrenamiento y después transforma la prueba. Un bosque aleatorio es invariante a un reescalado afín por columna, así que el escalador no cambia en sustancia los cortes del bosque. Aun así se ajusta solo con entrenamiento: el enunciado pide escalar magnitudes distintas, y un modelo lineal posterior no debe ver la prueba.

## Por qué Random Forest

`RandomForestRegressor` de scikit-learn, no XGBoost.

- **Tamaño.** 84 meses de entrenamiento son una serie corta. Un bosque con profundidad limitada no necesita una búsqueda de boosting.
- **Explicabilidad.** Finanzas pidió un error que se pueda explicar y un rango, no un solo número optimista. El bosque promedia árboles. La banda del gráfico es la desviación estándar entre esos árboles.
- **Tiempo de ajuste.** Los hiperparámetros quedan fijos: 400 árboles, `max_depth=6`, `min_samples_leaf=2`, `random_state=42`, `n_jobs=1`. No se eligen mirando 2024–2025.

XGBoost tendría sentido si el objetivo fuera ganar precisión y hubiera tiempo para ajustarlo. No es este pedido.

La misma justificación está en `pipelines/train_sales_model.py` (`MODEL_JUSTIFICATION`).

## Métricas (solo el conjunto de prueba)

Están en `output/metrics.md`. Definiciones:

- **MSE.** Media de `(real − pronóstico)²` en los 24 meses de prueba, en USD². También se publica la raíz (RMSE) en USD y esa raíz dividida por el ingreso mensual medio de la prueba, para leer el error como porcentaje de un mes típico. Un MSE bajo en los años de entrenamiento solo diría que el modelo se acuerda de ellos. El número que cuenta es el de la prueba. El MSE de entrenamiento se imprime debajo como diagnóstico y no es el resultado.
- **PSI.** Population Stability Index entre la distribución del entrenamiento (esperada) y la de la prueba (observada), con cortes por cuantiles del entrenamiento. No dice si un mes concreto se acertó. Dice si los años de prueba se alejaron de la distribución de entrenamiento. El CSV oficial solo trae filas `consolidated`, así que no hay mix de líneas que comparar. Inventar series de headhunting, outsourcing y formación contradiría el briefing. Se publican dos PSI: uno del nivel de ingreso (ahí aparece el crecimiento) y otro del ingreso dividido por la media de su año (la forma dentro del año). Guía habitual: por debajo de 0.10 estable, de 0.10 a 0.25 moderado, por encima de 0.25 un cambio claro.
- **Gini.** Gini normalizado del ranking. Los meses se ordenan por el pronóstico, de mayor a menor, y el ingreso real acumulado se compara con un ranking perfecto del ingreso real. 1 significa que el pronóstico ordena los meses de más ingreso por encima de los de menos. Es la métrica que habla de distinguir un agosto normal de una caída rara. No es el error en dólares.
- **K² Score.** K² de D'Agostino–Pearson, `scipy.stats.normaltest`, sobre los residuos de prueba (`real − pronóstico`), más el p-valor. Un K² alto y un p pequeño indican que los residuos no se ven normales: un solo MSE esconde sesgo o colas. Con 24 meses el contraste tiene poca potencia; se publican los dos números sin estirar la lectura.

Como referencia, no como segundo modelo, se incluye el RMSE de pronosticar cada mes de prueba con el ingreso del mes anterior.

## Resultados y limitaciones

El PSI de nivel es 6.3753. Eso indica que el ingreso de 2024–2025 está por encima del rango de entrenamiento, y un Random Forest no extrapola la tendencia. En el test, el máximo predicho es 987,295.59 USD y el máximo real es 1,145,988.88 USD.

Sobre los mismos 24 meses, el bosque se compara con un baseline estacional ingenuo: la predicción de cada mes es el ingreso de hace doce meses, y(t−12). El modelo y sus hiperparámetros no cambian.

| Modelo | MSE (USD²) | RMSE (USD) |
| --- | --- | --- |
| Random Forest | 4,612,858,070.60 | 67,918.02 |
| Baseline estacional y(t−12) | 3,190,168,976.25 | 56,481.58 |

El Random Forest pierde contra ese baseline en MSE y en RMSE.

## Descomposición

`statsmodels.tsa.seasonal.seasonal_decompose` con `model="multiplicative"` y `period=12`. El briefing describe agosto y enero–febrero como porcentajes sobre el promedio, en una serie que crece. Una oscilación aditiva en dólares mezclaría la tendencia con la amplitud estacional. `extrapolate_trend="period"` solo rellena los extremos de la tendencia diagnóstica. La descomposición no es el pronosticador.

`output/metrics.md` dice si agosto es el mes bajo y si enero y febrero quedan por encima de la media de su año, con los números medidos en este archivo. Las bandas del briefing se comprueban; no se dan por ciertas.

## Gráficas

`output/forecast_vs_actual.png` muestra el ingreso real de 2024–2025, la media del bosque y una banda de ±1 desviación estándar entre árboles. Esa banda es la dispersión del bosque, no un intervalo calibrado al 95 %. Agosto va sombreado. Enero y febrero van rotulados. El RMSE en dólares y como porcentaje del ingreso medio de la prueba sale de la misma ejecución y queda escrito en la figura.

`output/feature_importance.png` es la importancia de impureza. Favorece columnas continuas y no es un efecto causal.

La fuente es Arial o Helvetica si están instaladas; si no, Liberation Sans. El log de la ejecución dice cuál se usó. Este proyecto no tiene interfaz web.

## Pruebas

```bash
uv run pytest
```

| Archivo | Qué fija |
| --- | --- |
| `tests/pipelines/test_split.py` | Corte de 8 años / 2 años, meses y años disjuntos, sin barajar, año de origen de la serie cruda |
| `tests/pipelines/test_features.py` | El lag es el valor crudo pasado; el rolling excluye la fila actual; se tiran nulos y celdas vacías; el bosque se ajusta con esas features |
| `tests/pipelines/test_metrics.py` | El Gini de un ranking perfecto es 1; el PSI reacciona a un desplazamiento; K² devuelve un estadístico finito |
| `tests/pipelines/test_reproducibility.py` | Dos ajustes con semilla 42 coinciden; la media del escalador es la del entrenamiento, no la de train+test |
| `tests/pipelines/test_seasonal_baseline.py` | En 2024–2025 el baseline estacional es y(t−12) y su MSE/RMSE salen de ese vector |

## Dónde está el código

El monorepo documenta el ETL en `data/pipelines/`. Este enunciado pide las pruebas en `tests/pipelines/` y, en el briefing de Nexova, el script de entrenamiento en `scripts/`. El código importable está en `pipelines/` para que las pruebas lo importen, y `scripts/train_sales_forecast.py` es el punto de entrada. `data/pipelines/README.es.md` apunta aquí.
