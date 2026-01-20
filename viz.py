import math
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from config import MIN_SPACING, NEIGHBOR_RADIUS, PLAZA, SITE_HEIGHT, SITE_WIDTH
from geometry import edge_distance, find_violations, rect_center

Rect = Dict[str, float]

COLORS = {"A": "#1f77b4", "B": "#ff7f0e"}


def _pairwise_metrics(layout: List[Rect]) -> Tuple[List[Tuple[int, int, float, float]], List[Tuple[float, float]]]:
    centers = [rect_center(r) for r in layout]
    pairs: List[Tuple[int, int, float, float]] = []
    for i, c1 in enumerate(centers):
        for j in range(i + 1, len(layout)):
            c2 = centers[j]
            cdist = math.hypot(c1[0] - c2[0], c1[1] - c2[1])
            edist = edge_distance(layout[i], layout[j])
            pairs.append((i, j, cdist, edist))
    return pairs, centers


def _draw_line(ax, p1, p2, label: str, color: str, lw: float = 1.2, alpha: float = 0.7):
    x_mid, y_mid = (p1[0] + p2[0]) * 0.5, (p1[1] + p2[1]) * 0.5
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color, lw=lw, alpha=alpha)
    ax.text(x_mid, y_mid, label, ha="center", va="center", fontsize=7, color=color, bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=color, alpha=0.8))


def plot_layout(layout: List[Rect], stats: Dict[str, float], outfile: str) -> None:
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_xlim(0, SITE_WIDTH)
    ax.set_ylim(0, SITE_HEIGHT)
    ax.set_aspect("equal")
    ax.set_title("Generated Layout with Distances")

    site_patch = Rectangle((0, 0), SITE_WIDTH, SITE_HEIGHT, fill=False, lw=2, color="#222")
    ax.add_patch(site_patch)

    plaza_patch = Rectangle((PLAZA["x"], PLAZA["y"]), PLAZA["w"], PLAZA["h"], color="#cccccc", alpha=0.5)
    ax.add_patch(plaza_patch)
    ax.text(
        PLAZA["x"] + PLAZA["w"] * 0.5,
        PLAZA["y"] + PLAZA["h"] * 0.5,
        "Plaza",
        ha="center",
        va="center",
        fontsize=10,
        color="#333",
    )

    violations = find_violations(layout, NEIGHBOR_RADIUS)
    spacing_fail_pairs = violations["spacing_fail_pairs"]
    affected = violations["affected_indices"]

    pairs, centers = _pairwise_metrics(layout)
    nearest: Dict[int, Tuple[int, float, float]] = {}
    for i, j, cdist, edist in pairs:
        if i not in nearest or cdist < nearest[i][1]:
            nearest[i] = (j, cdist, edist)
        if j not in nearest or cdist < nearest[j][1]:
            nearest[j] = (i, cdist, edist)

    drawn_pairs = set()
    for i, j, _, _ in pairs:
        if nearest.get(i, (None,))[0] == j and i < j:
            drawn_pairs.add((i, j))
        if nearest.get(j, (None,))[0] == i and j < i:
            drawn_pairs.add((j, i))

    for idx, rect in enumerate(layout):
        color = COLORS.get(rect["type"], "#2ca02c")
        edge_color = "#d62728" if idx in affected else "#111111"
        patch = Rectangle((rect["x"], rect["y"]), rect["w"], rect["h"], color=color, alpha=0.8, ec=edge_color, lw=2)
        ax.add_patch(patch)
        ax.text(
            rect["x"] + rect["w"] * 0.5,
            rect["y"] + rect["h"] * 0.5,
            rect["type"],
            ha="center",
            va="center",
            fontsize=9,
            color="white",
        )

    for i, j, dist in spacing_fail_pairs:
        _draw_line(ax, centers[i], centers[j], f"{dist:.1f} m < {MIN_SPACING} m", "#d62728", lw=1.8, alpha=0.9)

    for i, j in drawn_pairs:
        _, _, edist = nearest[i]
        _draw_line(ax, centers[i], centers[j], f"{edist:.1f} m", "#555555", lw=1.0, alpha=0.5)

    # Draw neighbor-mix radius lines for Tower A buildings
    neighbor_fail = violations["neighbor_fail"]
    for idx, rect in enumerate(layout):
        if rect["type"] != "A":
            continue
        # Find closest Tower B
        closest_b_idx = None
        closest_b_dist = float("inf")
        for b_idx, b_rect in enumerate(layout):
            if b_rect["type"] != "B":
                continue
            dist = math.hypot(centers[idx][0] - centers[b_idx][0], centers[idx][1] - centers[b_idx][1])
            if dist < closest_b_dist:
                closest_b_dist = dist
                closest_b_idx = b_idx
        
        if closest_b_idx is not None:
            is_violation = idx in neighbor_fail
            color = "#d62728" if is_violation else "#9467bd"
            label_text = f"A→B: {closest_b_dist:.1f} m" + (f" > {NEIGHBOR_RADIUS} m!" if is_violation else "")
            _draw_line(ax, centers[idx], centers[closest_b_idx], label_text, color, lw=1.5, alpha=0.8)

    status = "valid" if stats.get("valid", False) else "invalid"
    subtitle = (
        f"A: {stats['count_A']}  |  B: {stats['count_B']}  |  "
        f"Area: {stats['area']:.0f} m²  |  Status: {status}  |  Min spacing: {MIN_SPACING} m"
    )
    ax.text(0.02, 0.98, subtitle, transform=ax.transAxes, ha="left", va="top", fontsize=10, color="#111")

    legend_elements = [
        Rectangle((0, 0), 1, 1, color=COLORS["A"], alpha=0.8, label="Tower A (30x20)"),
        Rectangle((0, 0), 1, 1, color=COLORS["B"], alpha=0.8, label="Tower B (20x20)"),
        Rectangle((0, 0), 1, 1, color="#cccccc", alpha=0.5, label="Central plaza (40x40)"),
        Rectangle((0, 0), 1, 1, color="#ffffff", ec="#d62728", lw=2, label="Rule violation"),
        plt.Line2D([0], [0], color="#9467bd", lw=1.5, label=f"A→B neighbor ({NEIGHBOR_RADIUS}m radius)"),
    ]
    ax.legend(handles=legend_elements, loc="upper right")

    ax.set_xlabel("Meters (x)")
    ax.set_ylabel("Meters (y)")
    ax.grid(True, linestyle="--", alpha=0.3)

    fig.tight_layout()
    fig.savefig(outfile, dpi=150)
    plt.close(fig)
