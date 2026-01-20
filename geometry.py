import math
from typing import Dict, Iterable, List, Tuple

from config import MIN_SPACING, PLAZA, SETBACK, SITE_HEIGHT, SITE_WIDTH

Rect = Dict[str, float]
ViolationReport = Dict[str, object]


def rect_center(rect: Rect) -> tuple[float, float]:
    return rect["x"] + rect["w"] * 0.5, rect["y"] + rect["h"] * 0.5


def inside_site(rect: Rect) -> bool:
    return (
        rect["x"] >= SETBACK
        and rect["y"] >= SETBACK
        and rect["x"] + rect["w"] <= SITE_WIDTH - SETBACK
        and rect["y"] + rect["h"] <= SITE_HEIGHT - SETBACK
    )


def intersects_plaza(rect: Rect) -> bool:
    px, py, pw, ph = PLAZA["x"], PLAZA["y"], PLAZA["w"], PLAZA["h"]
    return not (
        rect["x"] + rect["w"] <= px
        or px + pw <= rect["x"]
        or rect["y"] + rect["h"] <= py
        or py + ph <= rect["y"]
    )


def edge_distance(r1: Rect, r2: Rect) -> float:
    dx = max(0.0, r2["x"] - (r1["x"] + r1["w"]), r1["x"] - (r2["x"] + r2["w"]))
    dy = max(0.0, r2["y"] - (r1["y"] + r1["h"]), r1["y"] - (r2["y"] + r2["h"]))
    return math.hypot(dx, dy)


def spacing_ok(rect: Rect, others: Iterable[Rect], min_spacing: float = MIN_SPACING) -> bool:
    return all(edge_distance(rect, other) >= min_spacing for other in others)


def neighbor_mix_ok(layout: List[Rect], neighbor_radius: float) -> bool:
    centers = {id(r): rect_center(r) for r in layout}
    bs = [r for r in layout if r["type"] == "B"]
    if not bs:
        return False
    for rect in layout:
        if rect["type"] != "A":
            continue
        cx, cy = centers[id(rect)]
        close_b = False
        for b in bs:
            bx, by = centers[id(b)]
            if math.hypot(cx - bx, cy - by) <= neighbor_radius:
                close_b = True
                break
        if not close_b:
            return False
    return True


def layout_valid(layout: List[Rect], neighbor_radius: float) -> Dict[str, bool]:
    rule_boundary = all(inside_site(r) for r in layout)
    rule_plaza = all(not intersects_plaza(r) for r in layout)
    rule_spacing = all(
        edge_distance(r1, r2) >= MIN_SPACING
        for i, r1 in enumerate(layout)
        for r2 in layout[i + 1 :]
    )
    rule_neighbor = neighbor_mix_ok(layout, neighbor_radius)
    return {
        "boundary": rule_boundary,
        "plaza": rule_plaza,
        "spacing": rule_spacing,
        "neighbor_mix": rule_neighbor,
        "all": rule_boundary and rule_plaza and rule_spacing and rule_neighbor,
    }


def find_violations(layout: List[Rect], neighbor_radius: float) -> ViolationReport:
    boundary_fail = {idx for idx, r in enumerate(layout) if not inside_site(r)}
    plaza_fail = {idx for idx, r in enumerate(layout) if intersects_plaza(r)}

    spacing_fail_pairs: List[Tuple[int, int, float]] = []
    for i, r1 in enumerate(layout):
        for j in range(i + 1, len(layout)):
            r2 = layout[j]
            dist = edge_distance(r1, r2)
            if dist < MIN_SPACING:
                spacing_fail_pairs.append((i, j, dist))

    centers = [rect_center(r) for r in layout]
    bs = [idx for idx, r in enumerate(layout) if r["type"] == "B"]
    neighbor_fail = set()
    for idx, rect in enumerate(layout):
        if rect["type"] != "A":
            continue
        cx, cy = centers[idx]
        if not any(math.hypot(cx - centers[b][0], cy - centers[b][1]) <= neighbor_radius for b in bs):
            neighbor_fail.add(idx)

    affected = boundary_fail | plaza_fail | neighbor_fail | {i for pair in spacing_fail_pairs for i in pair[:2]}

    return {
        "boundary_fail": boundary_fail,
        "plaza_fail": plaza_fail,
        "spacing_fail_pairs": spacing_fail_pairs,
        "neighbor_fail": neighbor_fail,
        "affected_indices": affected,
    }
