# Evaluación técnica del pronóstico de ingresos

Ticket: ¿el modelo tiene underfitting, overfitting o está bien ajustado? ¿Qué tan estable es si cambia el tramo de entrenamiento? ¿Qué acción correctiva concreta corresponde?

Clasificación explícita: overfitting.

No es underfitting ni bien ajustado. La etiqueta sale de la curva de aprendizaje y de la validación cruzada temporal de este archivo, no de una frase suelta.

## Respuestas

1. Patrón: Hay una brecha amplia y persistente: el error de entrenamiento queda bajo y el de validación no se le acerca. Razón en el último tramo: 3.44. Brecha amplia: sí. Brecha cerrada: no. Persistente: sí. Validación por debajo del 90 % de y(t−12): no. Clasificación explícita: overfitting.
2. Estabilidad: el RMSE de validación en 5 folds es 62,329.33 ± 11,972.21 USD. La desviación es el 19.21 % de la media (desviación muestral, ddof=1). Lectura: moderada.
3. Acción: ver la sección final. No se aplica en este cambio. El bosque de 035 queda como está.

## Qué se reutiliza

El protocolo usa el mismo `RandomForestRegressor` que `pipelines/train_sales_model.py`: 400 árboles, max_depth=6, min_samples_leaf=2, max_features='sqrt', random_state=42, n_jobs=1. El escalador es `StandardScaler` ajustado solo con las filas de entrenamiento de cada ventana. Las features son las de `FEATURE_COLUMNS`: lags, rolling causal y calendario. El corte es el de `split_train_test`: 8 años de entrenamiento y 2 de prueba, con origen en el primer año de `data/raw/nexova_sales.csv`.

Esta corrida no modifica hiperparámetros, no reescribe el CSV y no mete 2024-01-01–2025-12-01 en ningún fold. El entrenamiento disponible va de 2017-01-01 a 2023-12-01. En `output/metrics.md` el mismo bosque, sin reajuste, tiene en 2024–2025 un RMSE de 67,918.02 USD y y(t−12) uno de 56,481.58 USD. Esos 24 meses no se recalculan aquí y no entran en los folds. El objetivo sigue siendo `revenue_usd` de `business_line=consolidated`. Las otras columnas del briefing son `month`, `active_contracts` y `avg_contract_value_usd`.

## Validación cruzada

`sklearn.model_selection.TimeSeriesSplit` con n_splits=5 y gap=0 sobre las filas de entrenamiento ya ordenadas por `month`. No se usa `KFold` ni `ShuffleSplit`. Cada fold es un bloque contiguo: el entrenamiento es el prefijo y la validación son los 14 meses siguientes. Un índice de validación de un fold posterior no aparece antes que uno de un fold anterior. Dentro de cada fold, el máximo índice de entrenamiento es menor que el mínimo de validación.

Las features de lag y rolling se construyen con `shift` antes del corte, igual que en el ajuste. Para cada fold se vuelve a construir la matriz después de poner a nulo `revenue_usd`, `active_contracts` y `avg_contract_value_usd` desde el primer mes de validación en adelante. Las features de las filas de entrenamiento no cambian. Eso es el control de fuga: si un lag o un rolling del entrenamiento mirara el bloque siguiente, el nulo lo movería. El control pasó en los 5 folds.

La referencia de cada fold es y(t−12): el `revenue_usd` del mismo mes un año antes, leído de la serie cruda. Coincide con la columna `revenue_lag_12`. No es un segundo modelo. Es el baseline estacional del pronóstico de 035, repetido dentro del entrenamiento.

| Fold | Entrenamiento | Validación | RMSE entreno / validación | MAE entreno / validación | RMSE y(t−12) | MAE y(t−12) | Sesgo |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2017-01-01–2018-02-01 (14) | 2018-03-01–2019-04-01 (14) | 37,408.47 / 58,947.11 | 26,113.53 / 44,044.61 | 41,248.38 | 31,066.61 | -5,930.75 |
| 2 | 2017-01-01–2019-04-01 (28) | 2019-05-01–2020-06-01 (14) | 28,201.19 / 59,767.71 | 19,468.41 / 49,377.53 | 46,738.53 | 37,489.73 | -20,450.90 |
| 3 | 2017-01-01–2020-06-01 (42) | 2020-07-01–2021-08-01 (14) | 24,839.40 / 68,218.25 | 18,998.17 / 55,125.80 | 62,300.31 | 53,629.11 | -45,133.55 |
| 4 | 2017-01-01–2021-08-01 (56) | 2021-09-01–2022-10-01 (14) | 24,832.49 / 46,222.15 | 19,203.99 / 34,987.99 | 37,852.65 | 28,547.44 | -26,007.26 |
| 5 | 2017-01-01–2022-10-01 (70) | 2022-11-01–2023-12-01 (14) | 22,821.42 / 78,491.41 | 17,666.40 / 71,148.76 | 67,783.93 | 58,498.82 | -54,242.75 |

Sesgo = media de (pronóstico − real) en la validación del fold. Positivo: el bosque sobreestima.

| Métrica | Entrenamiento | Validación del bosque | Validación de y(t−12) |
| --- | --- | --- | --- |
| RMSE | 27,620.59 ± 5,802.59 USD | 62,329.33 ± 11,972.21 USD | 51,184.76 ± 13,184.59 USD |
| MAE | 20,290.10 ± 3,328.67 USD | 50,936.94 ± 13,512.67 USD | 41,846.34 ± 13,492.42 USD |

Métrica principal: RMSE. Media ± desviación estándar en validación: 62,329.33 ± 11,972.21 USD.

El bosque pierde contra y(t−12) en la media del RMSE de validación (62,329.33 frente a 51,184.76).

## Curva de aprendizaje

Cada punto entrena con un prefijo cronológico y valida los 14 meses inmediatamente posteriores. Esos meses siguen dentro de 2017-01-01–2023-12-01. Los tamaños que coinciden con un fold reutilizan ese ajuste. No hay barajado. La figura está en `data/eval/learning_curve.png`.

| Meses de entrenamiento | Validación | RMSE entrenamiento | RMSE validación | RMSE y(t−12) | MAE entrenamiento | MAE validación | MAE y(t−12) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 14 | 2018-03-01–2019-04-01 | 37,408.47 | 58,947.11 | 41,248.38 | 26,113.53 | 44,044.61 | 31,066.61 |
| 21 | 2018-10-01–2019-11-01 | 28,588.02 | 72,054.50 | 55,251.73 | 21,915.67 | 61,167.01 | 43,621.95 |
| 28 | 2019-05-01–2020-06-01 | 28,201.19 | 59,767.71 | 46,738.53 | 19,468.41 | 49,377.53 | 37,489.73 |
| 35 | 2019-12-01–2021-01-01 | 25,512.79 | 68,810.15 | 39,584.80 | 18,681.70 | 54,910.83 | 35,123.03 |
| 42 | 2020-07-01–2021-08-01 | 24,839.40 | 68,218.25 | 62,300.31 | 18,998.17 | 55,125.80 | 53,629.11 |
| 49 | 2021-02-01–2022-03-01 | 24,085.10 | 64,602.00 | 59,354.52 | 18,586.18 | 55,260.77 | 47,533.73 |
| 56 | 2021-09-01–2022-10-01 | 24,832.49 | 46,222.15 | 37,852.65 | 19,203.99 | 34,987.99 | 28,547.44 |
| 63 | 2022-04-01–2023-05-01 | 22,756.91 | 59,321.03 | 49,308.48 | 17,841.60 | 49,777.59 | 40,016.80 |
| 70 | 2022-11-01–2023-12-01 | 22,821.42 | 78,491.41 | 67,783.93 | 17,666.40 | 71,148.76 | 58,498.82 |

En el último punto (70 meses, validación 2022-11-01 a 2023-12-01) la razón RMSE de validación / RMSE de entrenamiento es 3.44. y(t−12) en esa ventana tiene RMSE 67,783.93 USD. Umbrales de la regla: brecha amplia si la razón es mayor o igual que 1.75; brecha cerrada si es menor o igual que 1.50; la brecha se considera persistente si los tres últimos puntos siguen en razón mayor o igual que 1.50 y el hueco en dólares del último punto conserva al menos el 70 % del hueco del primero de esos tres. Error de validación alto si no baja de y(t−12); bajo si queda en 90 % o menos del RMSE de y(t−12). Error de entrenamiento alto si no baja del 85 % del RMSE de y(t−12) en esas mismas filas.

Hay una brecha amplia y persistente: el error de entrenamiento queda bajo y el de validación no se le acerca. Razón en el último tramo: 3.44. Brecha amplia: sí. Brecha cerrada: no. Persistente: sí. Validación por debajo del 90 % de y(t−12): no.

## Métrica principal y costo para Nexova

El briefing de ventas (`data/raw/nexova-BRIEFING.es.md`, sección 1) dice que Laura necesita el ingreso de los próximos meses antes de comprometer presupuesto. No asigna un dólar distinto al signo del error. La decisión que el pronóstico desbloquea es ese compromiso. Sobreestimar el ingreso compromete capacidad que el mes no va a cubrir. Subestimar retrasa el compromiso y se puede corregir cuando cierra el mes. Entre los dos signos, sobreestimar es el más caro. La sección 4 hace ese error concreto en agosto: el ingreso cae 15–25 % respecto al promedio. Tratar agosto como un mes normal sobreestima justo el mes en que Javier ve parada la contratación.

Entre MAE y RMSE, la principal es RMSE. La sección 3 pide el MSE en USD² y como porcentaje del ingreso mensual promedio: el error cuadrático ya es la lectura que el briefing da a Marcos y a Laura. El MAE trata igual cada dólar, así que un agosto desviado un 15–25 % pesa, dólar a dólar, como un mes ordinario de ±5 %. El RMSE eleva al cuadrado el error en dólares y deja que esos meses dominen. Ni el MAE ni el RMSE miran el signo. El sesgo medio va al lado para no esconderlo.

En el conjunto de las validaciones el sesgo medio (pronóstico − real) es -30,353.04 USD: el bosque subestima. Es material frente al MAE de validación. En los 6 agostos de la validación el sesgo medio es 63,216.10 USD: el bosque sobreestima agosto.

## Diagnóstico

Clasificación explícita: overfitting.

Respaldo: la tabla de la curva, la figura `data/eval/learning_curve.png` y la media ± desviación de los 5 folds. Hay una brecha amplia y persistente: el error de entrenamiento queda bajo y el de validación no se le acerca. Razón en el último tramo: 3.44. Brecha amplia: sí. Brecha cerrada: no. Persistente: sí. Validación por debajo del 90 % de y(t−12): no. La estabilidad de esa validación es moderada (62,329.33 ± 11,972.21 USD).

## Acción correctiva

En el último tramo el RMSE de entrenamiento es 22,821.42 USD y el de validación es 78,491.41 USD (razón 3.44). En los 5 folds el RMSE de validación del bosque es 62,329.33 ± 11,972.21 USD y el de y(t−12) es 51,184.76 ± 13,184.59 USD. La brecha es de overfitting: el bosque se ajusta a los meses que ya vio y no sostiene ese error en el bloque siguiente. A la vez pierde contra y(t−12). Un árbol predice la media de una hoja de entrenamiento y no puede seguir el nivel cuando el año siguiente crece, que es lo que ya muestra el pronóstico de 035 en 2024–2025. Subir max_depth o n_estimators no está en esta acción: apretaría el entrenamiento y no crea extrapolación. La acción es cambiar el objetivo del mismo RandomForestRegressor (n_estimators=400, max_depth=6, max_features='sqrt', random_state=42) al residuo revenue_usd − y(t−12), publicar el pronóstico como y(t−12) más ese residuo, quitar revenue_lag_12 de las features de ese residuo, y subir min_samples_leaf de 2 a 8 para que una hoja no memorice un solo mes del residuo. Se acepta solo si, en estos mismos 5 folds, la media del RMSE de validación queda por debajo de la media de y(t−12) y la razón validación/entrenamiento del último tramo baja de 1.5. No se usa 2024–2025 para elegir ese cambio.

Esta entrega no aplica el cambio. El modelo, las features y el split de 035 siguen iguales.

## Cómo reproducir

```bash
uv run python scripts/evaluate_regression_model.py
uv run pytest tests/pipelines/test_temporal_cv.py
```

Salidas: `data/eval/evaluation_report.md`, `data/eval/learning_curve.png` y `data/eval/cv_stability.png`. No se guarda una matriz de features. El script la recalcula.
