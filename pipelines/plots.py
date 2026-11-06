"""Gráficas del pronóstico. Sin interfaz web: claridad de ejes, fuente y fuente de datos."""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib
import matplotlib.ticker

matplotlib.use("Agg", force=True)

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager
from matplotlib.patches import Patch

CANVAS = "#F7F8FA"
SURFACE = "#FFFFFF"
INK = "#18202B"
MUTED = "#505E70"
SUBTLE = "#E7ECF2"
ACTION = "#B53A17"
INFO = "#204EA0"
AUGUST = "#FCEDE6"


def choose_font() -> str:
    """Arial o Helvetica si existen. Si no, Liberation Sans (métrica de Arial)."""
    available = {font.name for font in font_manager.fontManager.ttflist}
    for name in ("Arial", "Helvetica", "Liberation Sans"):
        if name in available:
            return name
    return "DejaVu Sans"


def _apply_style(font_name: str) -> None:
    matplotlib.rcParams.update(
        {
            "font.family": font_name,
            "font.size": 12,
            "axes.titlesize": 16,
            "axes.titleweight": "bold",
            "axes.labelsize": 12,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "text.color": INK,
            "axes.labelcolor": INK,
            "xtick.color": INK,
            "ytick.color": INK,
            "axes.edgecolor": INK,
            "figure.facecolor": CANVAS,
            "axes.facecolor": SURFACE,
            "axes.unicode_minus": False,
            "savefig.facecolor": CANVAS,
        }
    )


def _usd(value: float, _position: float) -> str:
    return f"{value:,.0f}"


def plot_forecast(
    months: pd.Series,
    actual: np.ndarray,
    predicted: np.ndarray,
    low: np.ndarray,
    high: np.ndarray,
    path: Path,
    subtitle: str,
    font_name: str,
) -> None:
    """Pronóstico de los dos años de prueba con banda de dispersión entre árboles."""
    _apply_style(font_name)
    figure, axis = plt.subplots(figsize=(12.8, 7.2), dpi=140)
    month_index = pd.DatetimeIndex(pd.to_datetime(months))

    for month in month_index:
        if int(month.month) == 8:
            axis.axvspan(
                month,
                month + pd.DateOffset(months=1),
                color=AUGUST,
                zorder=0,
            )

    axis.plot(
        month_index,
        actual,
        color=INK,
        linewidth=2.2,
        marker="o",
        markersize=4.5,
        label="Ingreso real",
        zorder=3,
    )
    axis.plot(
        month_index,
        predicted,
        color=ACTION,
        linewidth=2.2,
        label="Pronóstico",
        zorder=3,
    )
    axis.fill_between(
        month_index,
        low,
        high,
        color=ACTION,
        alpha=0.18,
        label="Banda entre árboles (±1 desv. estándar)",
        zorder=2,
    )
    for month, value in zip(month_index, actual):
        if int(month.month) in (1, 2):
            axis.annotate(
                "ene" if int(month.month) == 1 else "feb",
                xy=(month, value),
                xytext=(0, 8),
                textcoords="offset points",
                ha="center",
                fontsize=9,
                color=INFO,
            )

    axis.set_title(
        "Nexova — ingresos de 2024 y 2025: dato real frente al pronóstico",
        loc="left",
        color=INK,
        pad=10,
    )
    axis.set_xlabel("Mes")
    axis.set_ylabel("Ingresos (USD)")
    axis.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(_usd))
    axis.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    axis.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    axis.yaxis.grid(True, color=SUBTLE, linewidth=1)
    axis.xaxis.grid(False)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    low_y = float(min(np.min(actual), np.min(low)))
    high_y = float(max(np.max(actual), np.max(high)))
    span = high_y - low_y
    axis.set_ylim(low_y - span * 0.08, high_y + span * 0.18)
    handles, labels = axis.get_legend_handles_labels()
    handles.append(Patch(facecolor=AUGUST, edgecolor="none", label="Agosto"))
    labels.append("Agosto")
    figure.tight_layout(rect=(0, 0.22, 1, 1))
    figure.legend(
        handles,
        labels,
        frameon=False,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.16),
        ncol=2,
        fontsize=10,
    )
    figure.text(0.012, 0.02, subtitle, color=MUTED, fontsize=9, ha="left", va="bottom")
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path)
    plt.close(figure)


def plot_decomposition(result, path: Path, font_name: str) -> None:
    _apply_style(font_name)
    panels = (
        ("Observado", result.observed, "USD"),
        ("Tendencia", result.trend, "USD"),
        ("Estacionalidad", result.seasonal, "Factor"),
        ("Residual", result.resid, "Factor"),
    )
    figure, axes = plt.subplots(4, 1, figsize=(12.8, 9.6), dpi=140, sharex=True)
    figure.suptitle(
        "Nexova — descomposición multiplicativa de ingresos mensuales, 2016–2025",
        color=INK,
        fontsize=16,
        fontweight="bold",
        x=0.01,
        ha="left",
    )
    def _millions(value: float, _position: float) -> str:
        return f"{value / 1_000_000:.2f}"

    for axis, (title, series, ylabel) in zip(axes, panels):
        axis.plot(series.index, series.to_numpy(), color=INK, linewidth=1.6)
        if title == "Estacionalidad":
            axis.axhline(1.0, color=ACTION, linewidth=1, linestyle="--")
        if ylabel == "USD":
            axis.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(_millions))
            axis.set_ylabel("Millones USD")
        else:
            axis.set_ylabel(ylabel)
        axis.set_title(title, loc="left", fontsize=13, color=INK)
        axis.yaxis.grid(True, color=SUBTLE, linewidth=1)
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    axes[-1].set_xlabel("Año")
    figure.text(
        0.01,
        0.005,
        "Diagnóstico con statsmodels (modelo multiplicativo, periodo 12). No es el pronóstico. Fuente: data/raw/nexova_sales.csv.",
        color=MUTED,
        fontsize=10,
        ha="left",
    )
    figure.tight_layout(rect=(0, 0.03, 1, 0.96))
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path)
    plt.close(figure)


def plot_feature_importance(
    names: list[str],
    importances: np.ndarray,
    path: Path,
    font_name: str,
) -> None:
    _apply_style(font_name)
    order = np.argsort(importances)
    ordered_names = [names[index] for index in order]
    ordered_values = np.asarray(importances, dtype=float)[order]
    figure, axis = plt.subplots(figsize=(12.8, 6.4), dpi=140)
    axis.barh(ordered_names, ordered_values, color=ACTION, height=0.7)
    axis.set_title(
        "Nexova — qué variables usa el bosque al partir",
        loc="left",
        color=INK,
        pad=12,
    )
    axis.set_xlabel("Importancia media de la impureza")
    axis.xaxis.grid(True, color=SUBTLE, linewidth=1)
    axis.yaxis.grid(False)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    figure.text(
        0.01,
        0.01,
        "Importancia de impureza del Random Forest. Favorece variables continuas. No es un efecto causal. Semilla 42.",
        color=MUTED,
        fontsize=10,
        ha="left",
    )
    figure.tight_layout(rect=(0, 0.04, 1, 1))
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path)
    plt.close(figure)
