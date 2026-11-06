"""Evaluación temporal del pronóstico. No cambia el bosque ni el split de 035."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler

from pipelines.build_features import FEATURE_COLUMNS, build_features, drop_warmup_rows
from pipelines.load_sales import TARGET_COLUMN, repo_root
from pipelines.metrics import mean_squared_error
from pipelines.plots import ACTION, INFO, INK, MUTED, SUBTLE, _apply_style, choose_font
from matplotlib.ticker import FuncFormatter
from pipelines.split import split_train_test
from pipelines.train_sales_model import (
    MAX_DEPTH,
    MIN_SAMPLES_LEAF,
    N_ESTIMATORS,
    SEED,
    make_model,
)

# Regla fija de la etiqueta. No se ajusta para forzar un diagnóstico.
WIDE_GAP_RATIO = 1.75
CLOSE_GAP_RATIO = 1.50
LOW_VERSUS_LAG12 = 0.90
HIGH_VERSUS_LAG12 = 1.00
TRAIN_HIGH_VERSUS_LAG12 = 0.85
PERSISTENCE_FLOOR = 0.70
STABLE_CV = 0.10
MODERATE_CV = 0.25
MATERIAL_BIAS_VS_MAE = 0.50
MIN_SPLITS = 5
HELD_OUT_START = pd.Timestamp("2024-01-01")
LEVEL_COLUMNS = ("revenue_usd", "active_contracts", "avg_contract_value_usd")

_MONTHS = (
    "ene",
    "feb",
    "mar",
    "abr",
    "may",
    "jun",
    "jul",
    "ago",
    "sep",
    "oct",
    "nov",
    "dic",
)


@dataclass(frozen=True)
class FoldWindow:
    fold_number: int
    train_positions: tuple[int, ...]
    val_positions: tuple[int, ...]


@dataclass(frozen=True)
class FitStats:
    train_rmse: float
    val_rmse: float
    train_mae: float
    val_mae: float
    lag12_val_rmse: float
    lag12_val_mae: float
    lag12_train_rmse: float
    mean_signed_val: float
    signed_sum: float
    august_signed_sum: float
    august_count: int
    scaler_seen: int
    n_estimators: int
    max_depth: int
    min_samples_leaf: int
    random_state: int


@dataclass(frozen=True)
class CurvePoint:
    train_rows: int
    val_rows: int
    train_start: pd.Timestamp
    train_end: pd.Timestamp
    val_start: pd.Timestamp
    val_end: pd.Timestamp
    train_rmse: float
    val_rmse: float
    train_mae: float
    val_mae: float
    lag12_val_rmse: float
    lag12_val_mae: float
    lag12_train_rmse: float
    mean_signed_val: float


@dataclass(frozen=True)
class FoldResult:
    fold_number: int
    train_positions: tuple[int, ...]
    val_positions: tuple[int, ...]
    train_rows: int
    val_rows: int
    train_start: pd.Timestamp
    train_end: pd.Timestamp
    val_start: pd.Timestamp
    val_end: pd.Timestamp
    train_rmse: float
    val_rmse: float
    train_mae: float
    val_mae: float
    lag12_val_rmse: float
    lag12_val_mae: float
    mean_signed_val: float
    signed_sum: float
    august_signed_sum: float
    august_count: int
    scaler_seen: int
    n_estimators: int
    max_depth: int
    min_samples_leaf: int
    random_state: int
    leakage_check_passed: bool


@dataclass(frozen=True)
class Diagnosis:
    label: str
    gap_ratio: float
    wide: bool
    close: bool
    persistent: bool
    train_high: bool
    val_high: bool
    val_low: bool


@dataclass(frozen=True)
class Evaluation:
    folds: tuple[FoldResult, ...]
    curve: tuple[CurvePoint, ...]
    diagnosis: Diagnosis
    held_out_start: pd.Timestamp
    held_out_end: pd.Timestamp
    train_start: pd.Timestamp
    train_end: pd.Timestamp
    horizon: int
    n_splits: int
    font_name: str


def prepared_frames(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Mismo corte que el ajuste: origen de la serie cruda, 8 años y 2 años."""
    origin_year = int(raw["month"].dt.year.min())
    usable, _dropped = drop_warmup_rows(build_features(raw))
    return split_train_test(usable, origin_year=origin_year)


def seasonal_naive(raw: pd.DataFrame, months: pd.Series) -> np.ndarray:
    """y(t−12): el ingreso del mismo mes un año antes, leído de la serie cruda."""
    lookup = {
        timestamp: float(value)
        for timestamp, value in zip(raw["month"], raw[TARGET_COLUMN], strict=True)
    }
    predictions = []
    for month in months:
        previous = month - pd.DateOffset(years=1)
        if previous not in lookup:
            raise ValueError(f"No hay y(t−12) para {pd.Timestamp(month).date()}.")
        predictions.append(lookup[previous])
    return np.asarray(predictions, dtype=float)


def time_series_folds(frame: pd.DataFrame, n_splits: int = MIN_SPLITS) -> list[FoldWindow]:
    """TimeSeriesSplit sobre el entrenamiento. No baraja."""
    if n_splits < MIN_SPLITS:
        raise ValueError(f"Hacen falta al menos {MIN_SPLITS} folds.")
    if not bool(frame["month"].is_monotonic_increasing):
        raise ValueError("El set de entrenamiento no está en orden cronológico.")
    windows: list[FoldWindow] = []
    splitter = TimeSeriesSplit(n_splits=n_splits)
    for fold_number, (train_idx, val_idx) in enumerate(splitter.split(frame), start=1):
        windows.append(
            FoldWindow(
                fold_number=fold_number,
                train_positions=tuple(int(index) for index in train_idx),
                val_positions=tuple(int(index) for index in val_idx),
            )
        )
    assert_chronological(windows)
    return windows


def assert_chronological(windows: list[FoldWindow]) -> None:
    """Ningún índice de un fold posterior queda antes que uno de un fold anterior."""
    if len(windows) < MIN_SPLITS:
        raise ValueError(f"Hacen falta al menos {MIN_SPLITS} folds.")
    for window in windows:
        train_positions = list(window.train_positions)
        val_positions = list(window.val_positions)
        if train_positions != sorted(train_positions) or val_positions != sorted(val_positions):
            raise ValueError(f"El fold {window.fold_number} no conserva el orden.")
        if not train_positions or not val_positions:
            raise ValueError(f"El fold {window.fold_number} está vacío.")
        if max(train_positions) >= min(val_positions):
            raise ValueError(
                f"En el fold {window.fold_number} la validación no queda después del entrenamiento."
            )
        if train_positions != list(range(train_positions[0], train_positions[-1] + 1)):
            raise ValueError(f"El entrenamiento del fold {window.fold_number} no es un bloque contiguo.")
        if val_positions != list(range(val_positions[0], val_positions[-1] + 1)):
            raise ValueError(f"La validación del fold {window.fold_number} no es un bloque contiguo.")
    for earlier, later in zip(windows, windows[1:]):
        if max(earlier.val_positions) >= min(later.val_positions):
            raise ValueError(
                "Un índice de un fold posterior aparece antes que uno de un fold anterior."
            )
        if min(later.train_positions) < min(earlier.train_positions):
            raise ValueError("Un fold posterior empieza antes que el fold anterior.")


def features_ignore_future(raw: pd.DataFrame, frame: pd.DataFrame, cutoff: pd.Timestamp) -> bool:
    """Las features anteriores al corte no cambian si se anula el ingreso futuro."""
    masked = raw.copy()
    future = masked["month"] >= cutoff
    for column in LEVEL_COLUMNS:
        masked.loc[future, column] = np.nan
    rebuilt, _dropped = drop_warmup_rows(build_features(masked))
    original = frame.loc[frame["month"] < cutoff, ["month", *FEATURE_COLUMNS]]
    comparison = original.merge(rebuilt, on="month", how="left", suffixes=("_full", "_cut"))
    if len(comparison) != len(original) or comparison[FEATURE_COLUMNS[0] + "_cut"].isna().any():
        return False
    for column in FEATURE_COLUMNS:
        left = comparison[f"{column}_full"].to_numpy(dtype=float)
        right = comparison[f"{column}_cut"].to_numpy(dtype=float)
        if not np.allclose(left, right, equal_nan=True):
            return False
    return True


def _matrix(frame: pd.DataFrame) -> pd.DataFrame:
    return frame.loc[:, list(FEATURE_COLUMNS)]


def _rmse(actual: np.ndarray, predicted: np.ndarray) -> float:
    return float(np.sqrt(mean_squared_error(actual, predicted)))


def _mae(actual: np.ndarray, predicted: np.ndarray) -> float:
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    return float(np.mean(np.abs(actual - predicted)))


def fit_window(
    frame: pd.DataFrame,
    raw: pd.DataFrame,
    train_positions: tuple[int, ...],
    val_positions: tuple[int, ...],
) -> FitStats:
    """Ajusta el mismo bosque. El escalador solo ve el entrenamiento del fold."""
    train_view = frame.iloc[list(train_positions)]
    val_view = frame.iloc[list(val_positions)]
    if train_view["month"].max() >= val_view["month"].min():
        raise ValueError("La ventana de validación no es posterior al entrenamiento.")
    scaler = StandardScaler()
    x_train = scaler.fit_transform(_matrix(train_view))
    x_val = scaler.transform(_matrix(val_view))
    model = make_model()
    y_train = train_view[TARGET_COLUMN].to_numpy(dtype=float)
    y_val = val_view[TARGET_COLUMN].to_numpy(dtype=float)
    model.fit(x_train, y_train)
    pred_train = model.predict(x_train)
    pred_val = model.predict(x_val)
    lag12_val = seasonal_naive(raw, val_view["month"])
    lag12_train = seasonal_naive(raw, train_view["month"])
    if not np.allclose(lag12_val, val_view["revenue_lag_12"].to_numpy(dtype=float)):
        raise ValueError("revenue_lag_12 no coincide con y(t−12).")
    signed = pred_val - y_val
    august = val_view["month"].dt.month.to_numpy() == 8
    august_count = int(np.sum(august))
    august_sum = float(np.sum(signed[august])) if august_count else 0.0
    return FitStats(
        train_rmse=_rmse(y_train, pred_train),
        val_rmse=_rmse(y_val, pred_val),
        train_mae=_mae(y_train, pred_train),
        val_mae=_mae(y_val, pred_val),
        lag12_val_rmse=_rmse(y_val, lag12_val),
        lag12_val_mae=_mae(y_val, lag12_val),
        lag12_train_rmse=_rmse(y_train, lag12_train),
        mean_signed_val=float(np.mean(signed)),
        signed_sum=float(np.sum(signed)),
        august_signed_sum=august_sum,
        august_count=august_count,
        scaler_seen=int(scaler.n_samples_seen_),
        n_estimators=int(model.n_estimators),
        max_depth=int(model.max_depth) if model.max_depth is not None else 0,
        min_samples_leaf=int(model.min_samples_leaf),
        random_state=int(model.random_state),
    )


def learning_curve_sizes(n_rows: int, n_splits: int = MIN_SPLITS) -> tuple[list[int], int]:
    horizon = n_rows // (n_splits + 1)
    if horizon < 1:
        raise ValueError("El horizonte de validación quedó vacío.")
    fold_sizes = [horizon * (index + 1) for index in range(n_splits)]
    if fold_sizes[-1] + horizon > n_rows:
        raise ValueError("La curva no cabe en el set de entrenamiento.")
    sizes = set(fold_sizes)
    for left, right in zip(fold_sizes, fold_sizes[1:]):
        middle = (left + right) // 2
        if left < middle < right and middle + horizon <= n_rows:
            sizes.add(middle)
    return sorted(sizes), horizon


def diagnose(points: tuple[CurvePoint, ...] | list[CurvePoint]) -> Diagnosis:
    """Etiqueta el patrón relativo de las dos curvas. No mira 2024–2025."""
    if len(points) < 3:
        raise ValueError("La curva necesita al menos 3 tamaños de entrenamiento.")
    last = points[-1]
    if last.train_rmse <= 0 or last.lag12_val_rmse <= 0 or last.lag12_train_rmse <= 0:
        raise ValueError("Un RMSE de la curva es cero y la razón no está definida.")
    tail = list(points)[-3:]
    gap_ratio = last.val_rmse / last.train_rmse
    tail_ratios = [point.val_rmse / point.train_rmse for point in tail]
    gaps = [point.val_rmse - point.train_rmse for point in tail]
    wide = gap_ratio >= WIDE_GAP_RATIO
    close = gap_ratio <= CLOSE_GAP_RATIO
    persistent = all(ratio >= CLOSE_GAP_RATIO for ratio in tail_ratios) and (
        gaps[-1] >= PERSISTENCE_FLOOR * gaps[0]
    )
    train_high = last.train_rmse >= TRAIN_HIGH_VERSUS_LAG12 * last.lag12_train_rmse
    val_high = last.val_rmse >= HIGH_VERSUS_LAG12 * last.lag12_val_rmse
    val_low = last.val_rmse <= LOW_VERSUS_LAG12 * last.lag12_val_rmse
    open_gap = wide or persistent
    if open_gap and not train_high:
        label = "overfitting"
    elif train_high and val_high and not wide:
        label = "underfitting"
    elif close and val_low:
        label = "well fitted"
    elif open_gap:
        label = "overfitting"
    elif val_high:
        label = "underfitting"
    elif close:
        label = "well fitted"
    else:
        label = "overfitting"
    return Diagnosis(
        label=label,
        gap_ratio=float(gap_ratio),
        wide=wide,
        close=close,
        persistent=persistent,
        train_high=train_high,
        val_high=val_high,
        val_low=val_low,
    )


def mean_and_std(values: list[float]) -> tuple[float, float]:
    array = np.asarray(values, dtype=float)
    if array.size < 2:
        raise ValueError("La desviación estándar pide al menos dos folds.")
    return float(array.mean()), float(array.std(ddof=1))


def stability_word(mean: float, std: float) -> str:
    ratio = std / mean if mean else float("inf")
    if ratio <= STABLE_CV:
        return "estable"
    if ratio <= MODERATE_CV:
        return "moderada"
    return "inestable"


def run_evaluation(raw: pd.DataFrame, n_splits: int = MIN_SPLITS) -> Evaluation:
    train, test = prepared_frames(raw)
    if test["month"].min() < HELD_OUT_START:
        raise ValueError("La prueba reservada entra en el bloque de evaluación.")
    windows = time_series_folds(train, n_splits=n_splits)
    horizon = len(windows[0].val_positions)
    fold_stats: dict[int, FitStats] = {}
    folds: list[FoldResult] = []
    for window in windows:
        stats = fit_window(train, raw, window.train_positions, window.val_positions)
        cutoff = pd.Timestamp(train["month"].iloc[window.val_positions[0]])
        leakage_ok = features_ignore_future(raw, train, cutoff)
        if not leakage_ok:
            raise ValueError(f"Fuga de features en el fold {window.fold_number}.")
        if stats.scaler_seen != len(window.train_positions):
            raise ValueError("El escalador vio filas que no son el entrenamiento del fold.")
        if train["month"].iloc[window.val_positions[-1]] >= HELD_OUT_START:
            raise ValueError("Un fold de validación entra en 2024–2025.")
        fold_stats[len(window.train_positions)] = stats
        folds.append(_fold_result(train, window, stats, leakage_ok))

    sizes, curve_horizon = learning_curve_sizes(len(train), n_splits)
    if curve_horizon != horizon:
        raise ValueError("El horizonte de la curva no coincide con el de TimeSeriesSplit.")
    curve: list[CurvePoint] = []
    for size in sizes:
        train_positions = tuple(range(size))
        val_positions = tuple(range(size, size + horizon))
        stats = fold_stats.get(size)
        if stats is None:
            stats = fit_window(train, raw, train_positions, val_positions)
            cutoff = pd.Timestamp(train["month"].iloc[val_positions[0]])
            if not features_ignore_future(raw, train, cutoff):
                raise ValueError(f"Fuga de features en el tramo de {size} meses.")
        curve.append(_curve_point(train, train_positions, val_positions, stats))

    return Evaluation(
        folds=tuple(folds),
        curve=tuple(curve),
        diagnosis=diagnose(curve),
        held_out_start=pd.Timestamp(test["month"].min()),
        held_out_end=pd.Timestamp(test["month"].max()),
        train_start=pd.Timestamp(train["month"].min()),
        train_end=pd.Timestamp(train["month"].max()),
        horizon=horizon,
        n_splits=n_splits,
        font_name=choose_font(),
    )


def _fold_result(
    frame: pd.DataFrame,
    window: FoldWindow,
    stats: FitStats,
    leakage_ok: bool,
) -> FoldResult:
    return FoldResult(
        fold_number=window.fold_number,
        train_positions=window.train_positions,
        val_positions=window.val_positions,
        train_rows=len(window.train_positions),
        val_rows=len(window.val_positions),
        train_start=pd.Timestamp(frame["month"].iloc[window.train_positions[0]]),
        train_end=pd.Timestamp(frame["month"].iloc[window.train_positions[-1]]),
        val_start=pd.Timestamp(frame["month"].iloc[window.val_positions[0]]),
        val_end=pd.Timestamp(frame["month"].iloc[window.val_positions[-1]]),
        train_rmse=stats.train_rmse,
        val_rmse=stats.val_rmse,
        train_mae=stats.train_mae,
        val_mae=stats.val_mae,
        lag12_val_rmse=stats.lag12_val_rmse,
        lag12_val_mae=stats.lag12_val_mae,
        mean_signed_val=stats.mean_signed_val,
        signed_sum=stats.signed_sum,
        august_signed_sum=stats.august_signed_sum,
        august_count=stats.august_count,
        scaler_seen=stats.scaler_seen,
        n_estimators=stats.n_estimators,
        max_depth=stats.max_depth,
        min_samples_leaf=stats.min_samples_leaf,
        random_state=stats.random_state,
        leakage_check_passed=leakage_ok,
    )


def _curve_point(
    frame: pd.DataFrame,
    train_positions: tuple[int, ...],
    val_positions: tuple[int, ...],
    stats: FitStats,
) -> CurvePoint:
    return CurvePoint(
        train_rows=len(train_positions),
        val_rows=len(val_positions),
        train_start=pd.Timestamp(frame["month"].iloc[train_positions[0]]),
        train_end=pd.Timestamp(frame["month"].iloc[train_positions[-1]]),
        val_start=pd.Timestamp(frame["month"].iloc[val_positions[0]]),
        val_end=pd.Timestamp(frame["month"].iloc[val_positions[-1]]),
        train_rmse=stats.train_rmse,
        val_rmse=stats.val_rmse,
        train_mae=stats.train_mae,
        val_mae=stats.val_mae,
        lag12_val_rmse=stats.lag12_val_rmse,
        lag12_val_mae=stats.lag12_val_mae,
        lag12_train_rmse=stats.lag12_train_rmse,
        mean_signed_val=stats.mean_signed_val,
    )


def corrective_action(
    diagnosis: str,
    *,
    last_train_rmse: float,
    last_val_rmse: float,
    rmse_mean: float,
    rmse_std: float,
    lag12_mean: float,
    lag12_std: float,
    loses_to_lag12: bool,
) -> str:
    """Una acción, atada al diagnóstico y a los números de esta corrida."""
    gap_ratio = last_val_rmse / last_train_rmse
    measured = (
        f"En el último tramo el RMSE de entrenamiento es {_usd(last_train_rmse)} USD "
        f"y el de validación es {_usd(last_val_rmse)} USD (razón {gap_ratio:.2f}). "
        f"En los {MIN_SPLITS} folds el RMSE de validación del bosque es "
        f"{_usd(rmse_mean)} ± {_usd(rmse_std)} USD y el de y(t−12) es "
        f"{_usd(lag12_mean)} ± {_usd(lag12_std)} USD."
    )
    if diagnosis == "overfitting" and loses_to_lag12:
        return (
            f"{measured} La brecha es de overfitting: el bosque se ajusta a los meses que ya vio "
            "y no sostiene ese error en el bloque siguiente. A la vez pierde contra y(t−12). "
            "Un árbol predice la media de una hoja de entrenamiento y no puede seguir el nivel "
            "cuando el año siguiente crece, que es lo que ya muestra el pronóstico de 035 "
            "en 2024–2025. Subir max_depth o n_estimators no está en esta acción: apretaría "
            "el entrenamiento y no crea extrapolación. "
            f"La acción es cambiar el objetivo del mismo RandomForestRegressor "
            f"(n_estimators={N_ESTIMATORS}, max_depth={MAX_DEPTH}, max_features='sqrt', "
            f"random_state={SEED}) al residuo revenue_usd − y(t−12), publicar el pronóstico "
            "como y(t−12) más ese residuo, quitar revenue_lag_12 de las features de ese residuo, "
            f"y subir min_samples_leaf de {MIN_SAMPLES_LEAF} a 8 para que una hoja no memorice "
            "un solo mes del residuo. Se acepta solo si, en estos mismos 5 folds, la media del "
            "RMSE de validación queda por debajo de la media de y(t−12) y la razón "
            "validación/entrenamiento del último tramo baja de 1.5. No se usa 2024–2025 para "
            "elegir ese cambio."
        )
    if diagnosis == "overfitting":
        return (
            f"{measured} El bosque ya queda por debajo de y(t−12) en validación, pero la brecha "
            "con el entrenamiento sigue abierta. No se añaden años ni se sube la profundidad. "
            f"La acción es bajar max_depth de {MAX_DEPTH} a 4 y subir min_samples_leaf de "
            f"{MIN_SAMPLES_LEAF} a 8, dejando n_estimators={N_ESTIMATORS}, max_features='sqrt' "
            f"y random_state={SEED}. Se acepta solo si la razón del último tramo baja de 1.5 "
            "y la media del RMSE de validación no supera la media actual. No se usa 2024–2025."
        )
    if diagnosis == "underfitting":
        return (
            f"{measured} Entrenamiento y validación se quedan altos frente a y(t−12): el bosque "
            "no está capturando el nivel estacional que el briefing describe. La primera acción "
            "no es añadir filas. Es dar a cada partición las columnas que hoy "
            f"max_features='sqrt' puede dejar fuera: con {len(FEATURE_COLUMNS)} features, sqrt "
            "mira unas tres columnas por corte y revenue_lag_12 no entra siempre junto a "
            "month_sin y month_cos. "
            f"La acción es pasar max_features de 'sqrt' a 1.0 y dejar max_depth={MAX_DEPTH}, "
            f"min_samples_leaf={MIN_SAMPLES_LEAF}, n_estimators={N_ESTIMATORS} y "
            f"random_state={SEED}. No se sube la profundidad en el mismo cambio. Se acepta "
            "solo si la media del RMSE de validación de estos 5 folds baja de la media de "
            "y(t−12). No se usa 2024–2025."
        )
    return (
        f"{measured} Las curvas se juntan en un error bajo que mejora a y(t−12) dentro del "
        "entrenamiento. No se toca min_samples_leaf ni max_depth. El bloque 2024–2025 sigue "
        "fuera de este protocolo y no se reajusta. La acción previa a staging, si el reporte "
        "de 035 sigue mostrando que el bosque pierde contra y(t−12) por no extrapolar, es "
        "repetir exactamente estos 5 folds con el objetivo revenue_usd − y(t−12) y el "
        "pronóstico reconstruido como y(t−12) más el residuo, sin subir max_depth."
    )


def render_report(result: Evaluation) -> str:
    diagnosis = result.diagnosis
    label = _label_es(diagnosis.label)
    rmse_mean, rmse_std = mean_and_std([fold.val_rmse for fold in result.folds])
    mae_mean, mae_std = mean_and_std([fold.val_mae for fold in result.folds])
    train_rmse_mean, train_rmse_std = mean_and_std([fold.train_rmse for fold in result.folds])
    train_mae_mean, train_mae_std = mean_and_std([fold.train_mae for fold in result.folds])
    lag_rmse_mean, lag_rmse_std = mean_and_std([fold.lag12_val_rmse for fold in result.folds])
    lag_mae_mean, lag_mae_std = mean_and_std([fold.lag12_val_mae for fold in result.folds])
    loses = rmse_mean > lag_rmse_mean
    total_rows = sum(fold.val_rows for fold in result.folds)
    pooled_signed = sum(fold.signed_sum for fold in result.folds) / total_rows
    august_n = sum(fold.august_count for fold in result.folds)
    august_signed = (
        sum(fold.august_signed_sum for fold in result.folds) / august_n if august_n else 0.0
    )
    last = result.curve[-1]
    action = corrective_action(
        diagnosis.label,
        last_train_rmse=last.train_rmse,
        last_val_rmse=last.val_rmse,
        rmse_mean=rmse_mean,
        rmse_std=rmse_std,
        lag12_mean=lag_rmse_mean,
        lag12_std=lag_rmse_std,
        loses_to_lag12=loses,
    )
    stability = stability_word(rmse_mean, rmse_std)
    cv_ratio = rmse_std / rmse_mean
    other = _rejected_labels(diagnosis.label)
    bias_sentence = _bias_sentence(pooled_signed, mae_mean, august_n, august_signed)
    fold_table = _fold_table(result)
    curve_table = _curve_table(result)
    gap_sentence = _gap_sentence(diagnosis)
    return f"""# Evaluación técnica del pronóstico de ingresos

Ticket: ¿el modelo tiene underfitting, overfitting o está bien ajustado? ¿Qué tan estable es si cambia el tramo de entrenamiento? ¿Qué acción correctiva concreta corresponde?

Clasificación explícita: {label}.

No es {other}. La etiqueta sale de la curva de aprendizaje y de la validación cruzada temporal de este archivo, no de una frase suelta.

## Respuestas

1. Patrón: {gap_sentence} Clasificación explícita: {label}.
2. Estabilidad: el RMSE de validación en {result.n_splits} folds es {_usd(rmse_mean)} ± {_usd(rmse_std)} USD. La desviación es el {cv_ratio * 100:.2f} % de la media (desviación muestral, ddof=1). Lectura: {stability}.
3. Acción: ver la sección final. No se aplica en este cambio. El bosque de 035 queda como está.

## Qué se reutiliza

El protocolo usa el mismo `RandomForestRegressor` que `pipelines/train_sales_model.py`: {N_ESTIMATORS} árboles, max_depth={MAX_DEPTH}, min_samples_leaf={MIN_SAMPLES_LEAF}, max_features='sqrt', random_state={SEED}, n_jobs=1. El escalador es `StandardScaler` ajustado solo con las filas de entrenamiento de cada ventana. Las features son las de `FEATURE_COLUMNS`: lags, rolling causal y calendario. El corte es el de `split_train_test`: 8 años de entrenamiento y 2 de prueba, con origen en el primer año de `data/raw/nexova_sales.csv`.

Esta corrida no modifica hiperparámetros, no reescribe el CSV y no mete {_iso(result.held_out_start)}–{_iso(result.held_out_end)} en ningún fold. El entrenamiento disponible va de {_iso(result.train_start)} a {_iso(result.train_end)}. En `output/metrics.md` el mismo bosque, sin reajuste, tiene en 2024–2025 un RMSE de 67,918.02 USD y y(t−12) uno de 56,481.58 USD. Esos 24 meses no se recalculan aquí y no entran en los folds. El objetivo sigue siendo `revenue_usd` de `business_line=consolidated`. Las otras columnas del briefing son `month`, `active_contracts` y `avg_contract_value_usd`.

## Validación cruzada

`sklearn.model_selection.TimeSeriesSplit` con n_splits={result.n_splits} y gap=0 sobre las filas de entrenamiento ya ordenadas por `month`. No se usa `KFold` ni `ShuffleSplit`. Cada fold es un bloque contiguo: el entrenamiento es el prefijo y la validación son los {result.horizon} meses siguientes. Un índice de validación de un fold posterior no aparece antes que uno de un fold anterior. Dentro de cada fold, el máximo índice de entrenamiento es menor que el mínimo de validación.

Las features de lag y rolling se construyen con `shift` antes del corte, igual que en el ajuste. Para cada fold se vuelve a construir la matriz después de poner a nulo `revenue_usd`, `active_contracts` y `avg_contract_value_usd` desde el primer mes de validación en adelante. Las features de las filas de entrenamiento no cambian. Eso es el control de fuga: si un lag o un rolling del entrenamiento mirara el bloque siguiente, el nulo lo movería. El control pasó en los {result.n_splits} folds.

La referencia de cada fold es y(t−12): el `revenue_usd` del mismo mes un año antes, leído de la serie cruda. Coincide con la columna `revenue_lag_12`. No es un segundo modelo. Es el baseline estacional del pronóstico de 035, repetido dentro del entrenamiento.

| Fold | Entrenamiento | Validación | RMSE entreno / validación | MAE entreno / validación | RMSE y(t−12) | MAE y(t−12) | Sesgo |
| --- | --- | --- | --- | --- | --- | --- | --- |
{fold_table}

Sesgo = media de (pronóstico − real) en la validación del fold. Positivo: el bosque sobreestima.

| Métrica | Entrenamiento | Validación del bosque | Validación de y(t−12) |
| --- | --- | --- | --- |
| RMSE | {_usd(train_rmse_mean)} ± {_usd(train_rmse_std)} USD | {_usd(rmse_mean)} ± {_usd(rmse_std)} USD | {_usd(lag_rmse_mean)} ± {_usd(lag_rmse_std)} USD |
| MAE | {_usd(train_mae_mean)} ± {_usd(train_mae_std)} USD | {_usd(mae_mean)} ± {_usd(mae_std)} USD | {_usd(lag_mae_mean)} ± {_usd(lag_mae_std)} USD |

Métrica principal: RMSE. Media ± desviación estándar en validación: {_usd(rmse_mean)} ± {_usd(rmse_std)} USD.

El bosque {"pierde contra" if loses else "supera a"} y(t−12) en la media del RMSE de validación ({_usd(rmse_mean)} frente a {_usd(lag_rmse_mean)}).

## Curva de aprendizaje

Cada punto entrena con un prefijo cronológico y valida los {result.horizon} meses inmediatamente posteriores. Esos meses siguen dentro de {_iso(result.train_start)}–{_iso(result.train_end)}. Los tamaños que coinciden con un fold reutilizan ese ajuste. No hay barajado. La figura está en `data/eval/learning_curve.png`.

| Meses de entrenamiento | Validación | RMSE entrenamiento | RMSE validación | RMSE y(t−12) | MAE entrenamiento | MAE validación | MAE y(t−12) |
| --- | --- | --- | --- | --- | --- | --- | --- |
{curve_table}

En el último punto ({last.train_rows} meses, validación {_iso(last.val_start)} a {_iso(last.val_end)}) la razón RMSE de validación / RMSE de entrenamiento es {diagnosis.gap_ratio:.2f}. y(t−12) en esa ventana tiene RMSE {_usd(last.lag12_val_rmse)} USD. Umbrales de la regla: brecha amplia si la razón es mayor o igual que {WIDE_GAP_RATIO:.2f}; brecha cerrada si es menor o igual que {CLOSE_GAP_RATIO:.2f}; la brecha se considera persistente si los tres últimos puntos siguen en razón mayor o igual que {CLOSE_GAP_RATIO:.2f} y el hueco en dólares del último punto conserva al menos el {PERSISTENCE_FLOOR * 100:.0f} % del hueco del primero de esos tres. Error de validación alto si no baja de y(t−12); bajo si queda en {LOW_VERSUS_LAG12 * 100:.0f} % o menos del RMSE de y(t−12). Error de entrenamiento alto si no baja del {TRAIN_HIGH_VERSUS_LAG12 * 100:.0f} % del RMSE de y(t−12) en esas mismas filas.

{gap_sentence}

## Métrica principal y costo para Nexova

El briefing de ventas (`data/raw/nexova-BRIEFING.es.md`, sección 1) dice que Laura necesita el ingreso de los próximos meses antes de comprometer presupuesto. No asigna un dólar distinto al signo del error. La decisión que el pronóstico desbloquea es ese compromiso. Sobreestimar el ingreso compromete capacidad que el mes no va a cubrir. Subestimar retrasa el compromiso y se puede corregir cuando cierra el mes. Entre los dos signos, sobreestimar es el más caro. La sección 4 hace ese error concreto en agosto: el ingreso cae 15–25 % respecto al promedio. Tratar agosto como un mes normal sobreestima justo el mes en que Javier ve parada la contratación.

Entre MAE y RMSE, la principal es RMSE. La sección 3 pide el MSE en USD² y como porcentaje del ingreso mensual promedio: el error cuadrático ya es la lectura que el briefing da a Marcos y a Laura. El MAE trata igual cada dólar, así que un agosto desviado un 15–25 % pesa, dólar a dólar, como un mes ordinario de ±5 %. El RMSE eleva al cuadrado el error en dólares y deja que esos meses dominen. Ni el MAE ni el RMSE miran el signo. El sesgo medio va al lado para no esconderlo.

{bias_sentence}

## Diagnóstico

Clasificación explícita: {label}.

Respaldo: la tabla de la curva, la figura `data/eval/learning_curve.png` y la media ± desviación de los {result.n_splits} folds. {gap_sentence} La estabilidad de esa validación es {stability} ({_usd(rmse_mean)} ± {_usd(rmse_std)} USD).

## Acción correctiva

{action}

Esta entrega no aplica el cambio. El modelo, las features y el split de 035 siguen iguales.

## Cómo reproducir

```bash
uv run python scripts/evaluate_regression_model.py
uv run pytest tests/pipelines/test_temporal_cv.py
```

Salidas: `data/eval/evaluation_report.md`, `data/eval/learning_curve.png` y `data/eval/cv_stability.png`. No se guarda una matriz de features. El script la recalcula.
"""


def terminal_summary(result: Evaluation) -> str:
    rmse_mean, rmse_std = mean_and_std([fold.val_rmse for fold in result.folds])
    lag_mean, lag_std = mean_and_std([fold.lag12_val_rmse for fold in result.folds])
    return "\n".join(
        [
            "Evaluación temporal del pronóstico de Nexova",
            f"Clasificación explícita: {_label_es(result.diagnosis.label)}",
            f"RMSE de validación: {_usd(rmse_mean)} ± {_usd(rmse_std)} USD",
            f"RMSE de y(t−12): {_usd(lag_mean)} ± {_usd(lag_std)} USD",
            f"Folds: {result.n_splits}. Horizonte: {result.horizon} meses.",
            f"Fuera de los folds: {_iso(result.held_out_start)} a {_iso(result.held_out_end)}.",
            "Figura: data/eval/learning_curve.png",
            "Reporte: data/eval/evaluation_report.md",
        ]
    )


def write_outputs(result: Evaluation, root=None) -> dict[str, str]:
    from pathlib import Path

    base = Path(root) if root is not None else repo_root()
    directory = base / "data" / "eval"
    directory.mkdir(parents=True, exist_ok=True)
    curve_path = directory / "learning_curve.png"
    cv_path = directory / "cv_stability.png"
    report_path = directory / "evaluation_report.md"
    plot_learning_curve(result, curve_path)
    plot_cv_stability(result, cv_path)
    report_path.write_text(render_report(result), encoding="utf-8")
    return {
        "learning_curve": str(curve_path),
        "cv_stability": str(cv_path),
        "report": str(report_path),
    }


def plot_learning_curve(result: Evaluation, path) -> None:
    import matplotlib.pyplot as plt

    _apply_style(result.font_name)
    sizes = [point.train_rows for point in result.curve]
    figure, axes = plt.subplots(1, 2, figsize=(12.8, 6.8), dpi=140)
    panels = (
        (
            "RMSE, métrica principal",
            [point.train_rmse for point in result.curve],
            [point.val_rmse for point in result.curve],
            [point.lag12_val_rmse for point in result.curve],
        ),
        (
            "MAE",
            [point.train_mae for point in result.curve],
            [point.val_mae for point in result.curve],
            [point.lag12_val_mae for point in result.curve],
        ),
    )
    for axis, (title, train_error, val_error, baseline) in zip(axes, panels, strict=True):
        axis.plot(sizes, train_error, color=INFO, linewidth=1.8, marker="o", label="Entrenamiento del bosque")
        axis.plot(sizes, val_error, color=ACTION, linewidth=1.8, marker="o", label="Validación del bosque")
        axis.plot(
            sizes,
            baseline,
            color=MUTED,
            linewidth=1.6,
            linestyle="--",
            marker="o",
            label="Referencia y(t−12)",
        )
        axis.set_title(title, loc="left", color=INK, fontsize=14)
        axis.set_xlabel("Meses de entrenamiento")
        axis.set_ylabel("USD")
        axis.yaxis.set_major_formatter(_usd_formatter())
        axis.set_ylim(bottom=0)
        axis.yaxis.grid(True, color=SUBTLE, linewidth=1)
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
        axis.legend(frameon=False, fontsize=11)
    figure.suptitle(
        f"Nexova — {_label_es(result.diagnosis.label)}",
        x=0.01,
        ha="left",
        color=INK,
        fontsize=16,
        fontweight="bold",
    )
    figure.text(
        0.01,
        0.012,
        "Curva dentro del entrenamiento 2017–2023. 2024–2025 no entra. "
        "y(t−12) es referencia, no un segundo modelo. "
        f"Fuente: data/raw/nexova_sales.csv. Tipografía: {result.font_name}.",
        color=MUTED,
        fontsize=12,
        ha="left",
    )
    figure.tight_layout(rect=(0, 0.06, 1, 0.90))
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path)
    plt.close(figure)


def plot_cv_stability(result: Evaluation, path) -> None:
    import matplotlib.pyplot as plt

    _apply_style(result.font_name)
    labels = [
        f"{fold.fold_number}\n{_short_month(fold.val_start)}–{_short_month(fold.val_end)}"
        for fold in result.folds
    ]
    positions = np.arange(len(result.folds), dtype=float)
    figure, axes = plt.subplots(2, 1, figsize=(12.8, 9.2), dpi=140, sharex=True)
    panels = (
        (
            "RMSE de validación",
            [fold.val_rmse for fold in result.folds],
            [fold.lag12_val_rmse for fold in result.folds],
        ),
        (
            "MAE de validación",
            [fold.val_mae for fold in result.folds],
            [fold.lag12_val_mae for fold in result.folds],
        ),
    )
    for axis, (title, model_error, baseline) in zip(axes, panels, strict=True):
        mean, std = mean_and_std(model_error)
        axis.fill_between(
            [-0.5, len(positions) - 0.5],
            [mean - std, mean - std],
            [mean + std, mean + std],
            color="#FCEDE6",
            linewidth=0,
            label="Media ± desviación del bosque",
        )
        axis.plot(positions, model_error, color=ACTION, linewidth=1.8, marker="o", label="Bosque")
        axis.plot(
            positions,
            baseline,
            color=MUTED,
            linewidth=1.6,
            linestyle="--",
            marker="o",
            label="y(t−12)",
        )
        axis.axhline(mean, color=ACTION, linewidth=1)
        axis.set_xticks(positions, labels, fontsize=12)
        axis.set_xlim(-0.5, len(positions) - 0.5)
        axis.set_title(
            f"{title}: {_usd(mean)} ± {_usd(std)} USD",
            loc="left",
            color=INK,
            fontsize=14,
        )
        axis.set_ylabel("USD")
        axis.yaxis.set_major_formatter(_usd_formatter())
        axis.set_ylim(bottom=0)
        axis.yaxis.grid(True, color=SUBTLE, linewidth=1)
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
    handles, legend_labels = axes[0].get_legend_handles_labels()
    figure.legend(
        handles,
        legend_labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.90),
        ncol=3,
        frameon=False,
        fontsize=12,
    )
    figure.suptitle(
        "Nexova — cinco folds temporales, sin barajar",
        x=0.01,
        ha="left",
        color=INK,
        fontsize=16,
        fontweight="bold",
    )
    figure.text(
        0.01,
        0.012,
        "Cada fold valida el bloque siguiente. La banda es la media ± la desviación muestral del bosque. "
        f"Fuente: data/raw/nexova_sales.csv. Tipografía: {result.font_name}.",
        color=MUTED,
        fontsize=12,
        ha="left",
    )
    figure.tight_layout(rect=(0, 0.05, 1, 0.84))
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path)
    plt.close(figure)


def _usd_formatter():
    return FuncFormatter(lambda value, _position: f"{value:,.0f}")


def _fold_table(result: Evaluation) -> str:
    lines = []
    for fold in result.folds:
        lines.append(
            "| {number} | {train_start}–{train_end} ({train_rows}) | "
            "{val_start}–{val_end} ({val_rows}) | {train_rmse} / {val_rmse} | "
            "{train_mae} / {val_mae} | {lag_rmse} | {lag_mae} | {signed} |".format(
                number=fold.fold_number,
                train_start=_iso(fold.train_start),
                train_end=_iso(fold.train_end),
                train_rows=fold.train_rows,
                val_start=_iso(fold.val_start),
                val_end=_iso(fold.val_end),
                val_rows=fold.val_rows,
                train_rmse=_usd(fold.train_rmse),
                val_rmse=_usd(fold.val_rmse),
                train_mae=_usd(fold.train_mae),
                val_mae=_usd(fold.val_mae),
                lag_rmse=_usd(fold.lag12_val_rmse),
                lag_mae=_usd(fold.lag12_val_mae),
                signed=_usd(fold.mean_signed_val),
            )
        )
    return "\n".join(lines)


def _curve_table(result: Evaluation) -> str:
    lines = []
    for point in result.curve:
        lines.append(
            f"| {point.train_rows} | {_iso(point.val_start)}–{_iso(point.val_end)} | "
            f"{_usd(point.train_rmse)} | {_usd(point.val_rmse)} | {_usd(point.lag12_val_rmse)} | "
            f"{_usd(point.train_mae)} | {_usd(point.val_mae)} | {_usd(point.lag12_val_mae)} |"
        )
    return "\n".join(lines)


def _gap_sentence(diagnosis: Diagnosis) -> str:
    if diagnosis.wide and diagnosis.persistent and not diagnosis.train_high:
        pattern = (
            "Hay una brecha amplia y persistente: el error de entrenamiento queda bajo "
            "y el de validación no se le acerca."
        )
    elif diagnosis.close and diagnosis.val_high:
        pattern = (
            "Las dos curvas se acercan, pero el error de validación sigue alto "
            "frente a y(t−12)."
        )
    elif diagnosis.close and diagnosis.val_low:
        pattern = (
            "Las dos curvas se acercan en un error bajo, por debajo de y(t−12)."
        )
    elif diagnosis.wide or diagnosis.persistent:
        pattern = "La brecha entre entrenamiento y validación no se cierra al crecer el prefijo."
    else:
        pattern = "El patrón no es una brecha amplia ni una convergencia clara en un error bajo."
    return (
        f"{pattern} Razón en el último tramo: {diagnosis.gap_ratio:.2f}. "
        f"Brecha amplia: {'sí' if diagnosis.wide else 'no'}. "
        f"Brecha cerrada: {'sí' if diagnosis.close else 'no'}. "
        f"Persistente: {'sí' if diagnosis.persistent else 'no'}. "
        f"Validación por debajo del 90 % de y(t−12): {'sí' if diagnosis.val_low else 'no'}."
    )


def _bias_sentence(pooled_signed: float, mae_mean: float, august_n: int, august_signed: float) -> str:
    material = abs(pooled_signed) >= MATERIAL_BIAS_VS_MAE * mae_mean
    if pooled_signed > 0:
        direction = "sobreestima"
    elif pooled_signed < 0:
        direction = "subestima"
    else:
        direction = "no se desvía en media"
    weight = "Es material frente al MAE de validación." if material else "No llega a la mitad del MAE de validación."
    august = ""
    if august_n:
        august_direction = "sobreestima" if august_signed > 0 else "subestima"
        august = (
            f" En los {august_n} agostos de la validación el sesgo medio es "
            f"{_usd(august_signed)} USD: el bosque {august_direction} agosto."
        )
    return (
        f"En el conjunto de las validaciones el sesgo medio (pronóstico − real) es "
        f"{_usd(pooled_signed)} USD: el bosque {direction}. {weight}{august}"
    )


def _label_es(label: str) -> str:
    if label == "well fitted":
        return "bien ajustado (well fitted)"
    if label in {"overfitting", "underfitting"}:
        return label
    raise ValueError(f"Etiqueta desconocida: {label}")


def _rejected_labels(label: str) -> str:
    names = {
        "overfitting": "overfitting",
        "underfitting": "underfitting",
        "well fitted": "bien ajustado",
    }
    rejected = [text for key, text in names.items() if key != label]
    return f"{rejected[0]} ni {rejected[1]}"


def _iso(value: pd.Timestamp) -> str:
    return pd.Timestamp(value).strftime("%Y-%m-%d")


def _short_month(value: pd.Timestamp) -> str:
    stamp = pd.Timestamp(value)
    return f"{_MONTHS[stamp.month - 1]} {stamp.year}"


def _usd(value: float) -> str:
    return f"{value:,.2f}"
