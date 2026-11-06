# Pronóstico de ingresos de Nexova

Métricas del conjunto de prueba (2024-01-01 a 2025-12-01). No son métricas de entrenamiento.

## Resultado en los 24 meses de prueba

| Métrica | Valor | Lectura |
| --- | --- | --- |
| MSE | 4,612,858,070.60 USD² | Media de (real − pronóstico)² |
| RMSE | 67,918.02 USD | Raíz del MSE, en dólares del mes |
| RMSE / ingreso medio | 7.08 % | Ese error frente al ingreso mensual medio de la prueba (959,363.25 USD) |
| MAE | 54,600.39 USD | Error absoluto medio, complemento del MSE |
| PSI (nivel) | 6.3753 | Cambio de la distribución de `revenue_usd` entre entrenamiento y prueba |
| PSI (forma) | 0.1659 | Igual, después de dividir cada mes por la media de su año |
| Gini | 0.8639 | Capacidad de ordenar meses de más ingreso a menos. 1 sería un orden perfecto |
| K² | 2.0454 (p = 0.3596) | D'Agostino–Pearson sobre los residuos de prueba |

Referencia, no es el modelo: repetir el ingreso del mes anterior da un RMSE de 94,696.72 USD en los mismos 24 meses.

## Qué mide cada métrica, y por qué un MSE bajo no basta

- **MSE** es el error cuadrático medio en USD². Castiga más un mes muy desviado que muchos meses casi acertados. Un valor bajo en entrenamiento puede ser memoria del pasado. Por eso el MSE que vale es el de 2024–2025, que el ajuste no vio.
- **PSI** (Population Stability Index) compara dos distribuciones. No dice si el pronóstico acertó el mes. Dice si el periodo de prueba se parece al de entrenamiento. El CSV oficial solo trae `business_line=consolidated`, así que no hay un PSI del mix headhunting / outsourcing / formación: inventar esas series falsearía el briefing. El PSI de nivel sube si el ingreso creció. El PSI de forma mira el perfil dentro del año, sin el nivel. En esta serie el PSI de nivel queda por encima de 0.25 porque el ingreso de 2024–2025 sale del rango de los años de entrenamiento: es el crecimiento, no un fallo del pronóstico. La lectura de estabilidad estacional es el PSI de forma.
- **Gini** normalizado mide si el pronóstico ordena bien los meses. Un MSE moderado puede convivir con un modelo que no distingue un agosto flojo de una caída anormal. El Gini es esa distinción, que es la que el briefing pide para Laura.
- **K²** es el estadístico de D'Agostino y Pearson (`scipy.stats.normaltest`) sobre los residuos de la prueba. Un p pequeño rechaza que esos residuos sean normales: el error no es una nube simétrica alrededor de cero. Con 24 meses el contraste es débil; se publica el número y el p-valor.

El MSE de entrenamiento se calcula solo como diagnóstico y no es el resultado: 639,995,086.81 USD² (RMSE 25,298.12 USD). El RMSE de entrenamiento es menor que el de prueba: el bosque se pega más a los años que ya vio. Los hiperparámetros no se reajustaron mirando 2024–2025.

## Split

Corte en 2024: los años anteriores a ese corte son entrenamiento y ese año más el siguiente son prueba. Origen de la serie cruda: 2016.

| Conjunto | Meses | Desde | Hasta | Años |
| --- | --- | --- | --- | --- |
| Entrenamiento | 84 | 2017-01-01 | 2023-12-01 | 2017, 2018, 2019, 2020, 2021, 2022, 2023 |
| Prueba | 24 | 2024-01-01 | 2025-12-01 | 2024, 2025 |

Se descartaron 12 meses iniciales porque el lag de 12 meses y el rolling de 12 meses no tienen pasado suficiente. Esos meses son 2016. No se movieron a la prueba. El escalador se ajustó solo con el entrenamiento.

## Modelo

RandomForestRegressor de scikit-learn, no XGBoost. La serie útil de entrenamiento tiene 84 meses: es corta para una búsqueda de boosting. Finanzas necesita explicar el error y ver un rango, no un solo número. El bosque promedia árboles; la desviación estándar entre árboles es la banda de variabilidad. Los hiperparámetros quedan fijos (400 árboles, profundidad 6, mínimo 2 muestras por hoja, semilla 42) y no se eligen mirando la prueba. XGBoost quedaría solo si el objetivo fuera ganar precisión y hubiera tiempo de ajuste.

Semilla `random_state=42`. Árboles: 400. Profundidad máxima: 6. Mínimo de muestras por hoja: 2.

Banda del gráfico: ±1 desviación estándar de las predicciones de los árboles en cada mes de prueba. No es un intervalo calibrado al 95 %.

## Features usadas en el ajuste

- `revenue_lag_1`
- `revenue_lag_12`
- `revenue_roll_mean_3`
- `revenue_roll_std_12`
- `contracts_lag_1`
- `avg_contract_value_lag_1`
- `month_sin`
- `month_cos`
- `quarter`
- `trend_month_index`

`active_contracts` y `avg_contract_value_usd` del mismo mes no entran: son contemporáneos al objetivo. Entran sus lags.

| Feature | Importancia de impureza |
| --- | --- |
| `revenue_lag_12` | 0.4075 |
| `trend_month_index` | 0.1413 |
| `revenue_lag_1` | 0.0790 |
| `revenue_roll_mean_3` | 0.0730 |
| `quarter` | 0.0665 |
| `month_sin` | 0.0649 |
| `contracts_lag_1` | 0.0615 |
| `month_cos` | 0.0468 |
| `revenue_roll_std_12` | 0.0374 |
| `avg_contract_value_lag_1` | 0.0220 |

## Estacionalidad frente al briefing

Descomposición multiplicative, periodo 12, con `statsmodels.tsa.seasonal.seasonal_decompose`. La dirección coincide con el briefing: agosto es el mes más bajo y enero y febrero quedan por encima de la media de su año. Los tres meses caen dentro de las bandas del briefing (agosto −15 % a −25 %; enero y febrero +15 % a +20 %).

| Mes | Frente a la media de su año | Factor estacional medio |
| --- | --- | --- |
| agosto | -21.55 % | 0.7795 |
| enero | 16.94 % | 1.1925 |
| febrero | 16.40 % | 1.1825 |

Desviación absoluta media del resto de meses frente a la media de su año: 1.45 %. El briefing habla de un movimiento moderado, del orden de ±5 %, en esos meses.

Perfil medio de todos los meses (ingreso / media del mismo año):

| Mes | Diferencia frente a 1 |
| --- | --- |
| enero | 16.94 % |
| febrero | 16.40 % |
| marzo | -1.06 % |
| abril | 0.61 % |
| mayo | -1.63 % |
| junio | -2.36 % |
| julio | -0.74 % |
| agosto | -21.55 % |
| septiembre | -2.14 % |
| octubre | -1.38 % |
| noviembre | -0.87 % |
| diciembre | -2.23 % |

## Crecimiento anual observado

Todos los crecimientos anuales observados son positivos. Mínimo 0.50 %, máximo 7.35 %. El briefing describe un crecimiento base del 4 % con años alternando cerca del 1 % y del 7 %. La tabla es el dato del CSV, no ese generador.

| Año | Variación del ingreso anual |
| --- | --- |
| 2017 | 6.91 % |
| 2018 | 0.67 % |
| 2019 | 6.79 % |
| 2020 | 1.34 % |
| 2021 | 7.35 % |
| 2022 | 0.50 % |
| 2023 | 7.23 % |
| 2024 | 2.55 % |
| 2025 | 6.10 % |

## Datos

- Archivo: `/workspace/data/raw/nexova_sales.csv`
- SHA-256: `e3af15657506fae36a81eec6a9a544a54473bf38f41f2ee1bb066799ff94440a`
- Coincide con el hash oficial: True
- Filas leídas: 120. Nulos tirados antes del modelo: 0. Filas `consolidated`: 120.
- Fuente tipográfica de las gráficas en esta máquina: Liberation Sans.
