# Este archivo genera una imagen resumen del análisis del vídeo usando Matplotlib

import os
from typing import Dict
import matplotlib.pyplot as plt

# Directorio para guardar gráficos en caché
GRAPH_DIR = "data/graphs"

# Esta función obtiene la ruta del archivo del gráfico en caché
def get_graph_path(analysis_id: str) -> str:
    return f"{GRAPH_DIR}/{analysis_id}_analysis.png"

# Esta función verifica si el gráfico ya está en caché
def is_graph_cached(analysis_id: str) -> str | None:
    path = get_graph_path(analysis_id)
    return path if os.path.exists(path) else None

# Esta función guarda la figura del gráfico en disco
def save_graph(fig, analysis_id: str) -> str:
    path = get_graph_path(analysis_id)
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path

# Esta función determina el color según la confianza
def confidence_color(confidence: float) -> str:
    if confidence < 40:
        return "red"
    elif confidence < 70:
        return "orange"
    return "green"

# Esta función genera (o recupera de caché) la imagen resumen del análisis
def generate_graph(analysis_id: str, classification: Dict) -> str:

    # 1. Caché
    cached = is_graph_cached(analysis_id)
    if cached:
        print("📦 Gráfico encontrado en caché.")
        return cached

    # 2. Extraer datos
    is_travel = classification.get("is_travel", False)
    confidence = classification.get("travel_confidence", 0.0) * 100

    distribution = classification.get("distribution", {})
    labels = ["Gastronomía", "Cultura", "Entretenimiento", "Otros"]
    values = [
        distribution.get("gastronomy", 0.0) * 100,
        distribution.get("culture", 0.0) * 100,
        distribution.get("entertainment", 0.0) * 100,
        distribution.get("others", 0.0) * 100,
    ]
    colors = ["green", "blue", "red", "gray"]

    # 3. Crear figuras
    fig, (ax_conf, ax_dist) = plt.subplots(
        2,
        1,
        figsize=(8, 6),
        gridspec_kw={"height_ratios": [1, 3]}
    )

    # 3.1 Barra de confianza
    ax_conf.barh(
        ["Confianza de viaje"],
        [confidence],
        color=confidence_color(confidence),
    )
    ax_conf.set_xlim(0, 100)
    ax_conf.set_xlabel("Porcentaje (%)")

    status_text = "SÍ" if is_travel else "NO"
    ax_conf.set_title(f"¿Es un vídeo de viajes? {status_text}")

    ax_conf.text(
        confidence + 1,
        0,
        f"{confidence:.1f}%",
        va="center",
        fontsize=10
    )

    # 3.2 Gráfico de distribución
    bars = ax_dist.bar(labels, values, color=colors)
    ax_dist.set_ylim(0, 100)
    ax_dist.set_ylabel("Porcentaje (%)")
    ax_dist.set_title("Distribución del contenido")

    # 3.3 Etiquetas encima de las barras
    for bar in bars:
        height = bar.get_height()
        ax_dist.text(
            bar.get_x() + bar.get_width() / 2,
            height + 1,
            f"{height:.1f}%",
            ha="center",
            va="bottom",
            fontsize=9
        )

    plt.tight_layout()

    # 4. Guardar gráfico
    path = save_graph(fig, analysis_id)

    print("📊 Gráfico generado y guardado.")
    return path

