"""Genera docs/arquitectura_lambda.png — diagrama de la arquitectura Lambda del proyecto."""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.font_manager as fm

fig, ax = plt.subplots(figsize=(13, 9))
ax.set_xlim(0, 13)
ax.set_ylim(0, 9)
ax.axis("off")

COLOR_SOURCE = "#37474F"
COLOR_INGEST = "#455A64"
COLOR_SPEED = "#C62828"
COLOR_BATCH = "#1565C0"
COLOR_SERVE = "#2E7D32"
COLOR_VIEW = "#6A1B9A"
TXT = "white"


def box(x, y, w, h, text, color, fontsize=10, ax=ax):
    b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.12",
                        linewidth=1.2, edgecolor="white", facecolor=color, zorder=3)
    ax.add_patch(b)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", color=TXT,
             fontsize=fontsize, fontweight="bold", zorder=4, linespacing=1.4)


def arrow(x1, y1, x2, y2, color="#607D8B"):
    a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=16,
                         linewidth=1.6, color=color, zorder=2)
    ax.add_patch(a)


ax.text(6.5, 8.6, "Arquitectura Lambda — Detección de Fraude Bancario en Tiempo Real",
        ha="center", fontsize=14, fontweight="bold", color="#212121")
ax.text(6.5, 8.25, "Grupo 1 · DD283 Big Data · Kafka + PySpark + MongoDB Atlas + ML Ensemble",
        ha="center", fontsize=9.5, color="#616161")

# Fuentes de datos
box(0.4, 6.9, 2.6, 0.9, "Transacciones\nen tiempo real\n(mock / Kafka producer)", COLOR_SOURCE, 8.5)
box(3.3, 6.9, 2.6, 0.9, "Historial de cuentas\n(CSV / Parquet)", COLOR_SOURCE, 8.5)
box(6.2, 6.9, 2.6, 0.9, "Datos geoespaciales\nLima (JSON)", COLOR_SOURCE, 8.5)
ax.text(0.4, 7.95, "FUENTES DE DATOS", fontsize=8.5, color="#455A64", fontweight="bold")

# Ingesta
box(2.0, 5.5, 6.5, 0.85, "CAPA DE INGESTA\nApache Kafka / Python Simulator  —  tópico: transacciones-raw",
    COLOR_INGEST, 9)

arrow(1.7, 6.9, 3.5, 6.35)
arrow(4.6, 6.9, 5.2, 6.35)
arrow(7.5, 6.9, 7.0, 6.35)

# Speed layer
box(0.4, 3.9, 3.6, 1.15, "SPEED LAYER\nPySpark Structured Streaming\ntrigger < 500ms · scoring online", COLOR_SPEED, 9)
# Batch layer
box(4.6, 3.9, 3.6, 1.15, "BATCH LAYER\nPySpark batch\nhistórico + reentrenamiento (24h)", COLOR_BATCH, 9)
# Model layer
box(8.6, 3.9, 3.6, 1.15, "ML ENSEMBLE\nRandom Forest + XGBoost\nMLflow (versión + scoring)", "#EF6C00", 9)

arrow(3.5, 5.5, 2.2, 5.05)
arrow(5.5, 5.5, 6.4, 5.05)
arrow(9.3, 5.05, 9.3, 5.05)
arrow(8.2, 4.45, 8.6, 4.45)

# Serving layer
box(1.5, 2.3, 9.0, 1.0,
    "SERVING LAYER  —  MongoDB Atlas (alertas + resultados)\nEsquema Medallion: Bronze → Silver → Gold",
    COLOR_SERVE, 9.5)

arrow(2.2, 3.9, 3.5, 3.3)
arrow(6.4, 3.9, 6.0, 3.3)
arrow(10.4, 3.9, 8.5, 3.3)

# Dashboard / API
box(2.5, 0.9, 6.5, 0.95, "DASHBOARD / API REST\nStreamlit  ·  métricas de negocio y alertas activas", COLOR_VIEW, 9.5)
arrow(6.0, 2.3, 6.0, 1.85)

# Leyenda de gobierno de datos
ax.text(0.4, 0.25, "Gobierno de datos: trazabilidad de scoring, enmascaramiento de PII (Ley 29733), auditoría por transacción",
        fontsize=8, color="#757575", style="italic")

plt.tight_layout()
plt.savefig("/home/claude/grupo1-fraude-bancario-bd/docs/arquitectura_lambda.png",
            dpi=200, bbox_inches="tight", facecolor="white")
print("Diagrama guardado.")
