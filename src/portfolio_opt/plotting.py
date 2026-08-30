from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def save_figure(path: str | Path, figure_name: str) -> None:
    """Create a placeholder plot file for generated benchmark visualizations."""
    out = Path(path)
    out.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot([0, 1], [0, 1], label=figure_name)
    ax.set_title(figure_name)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / f"{figure_name}.png", dpi=200)
    plt.close(fig)
