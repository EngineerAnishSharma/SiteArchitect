import random
from typing import Dict, List, Optional

from config import BUILDING_TYPES, MIN_SPACING, NEIGHBOR_RADIUS, SETBACK, SITE_HEIGHT, SITE_WIDTH
from geometry import (
    edge_distance,
    inside_site,
    intersects_plaza,
    layout_valid,
    neighbor_mix_ok,
    spacing_ok,
)

Rect = Dict[str, float]


def _random_position(w: float, h: float) -> tuple[float, float]:
    x = random.uniform(SETBACK, SITE_WIDTH - SETBACK - w)
    y = random.uniform(SETBACK, SITE_HEIGHT - SETBACK - h)
    return x, y


def _try_place(type_name: str, current: List[Rect], attempts: int) -> Optional[Rect]:
    dims = BUILDING_TYPES[type_name]
    for _ in range(attempts):
        x, y = _random_position(dims["w"], dims["h"])
        rect = {"x": x, "y": y, "w": dims["w"], "h": dims["h"], "type": type_name}
        if not inside_site(rect):
            continue
        if intersects_plaza(rect):
            continue
        if not spacing_ok(rect, current, MIN_SPACING):
            continue
        return rect
    return None


def generate_layout(
    min_buildings: int = 5,
    max_buildings: int = 12,
    attempts_per_building: int = 120,
    fill_extra: int = 0,
    seed: Optional[int] = None,
) -> Optional[List[Rect]]:
    if seed is not None:
        random.seed(seed)
    target = random.randint(min_buildings, max_buildings)
    current: List[Rect] = []

    type_choices = ["A", "B"]
    for _ in range(target):
        t = random.choice(type_choices)
        rect = _try_place(t, current, attempts_per_building)
        if rect is None:
            return None
        current.append(rect)

    added = 0
    while added < fill_extra:
        t = random.choice(type_choices)
        rect = _try_place(t, current, attempts_per_building)
        if rect is None:
            break
        current.append(rect)
        added += 1

    if not neighbor_mix_ok(current, NEIGHBOR_RADIUS):
        return None
    return current


def collect_valid_layouts(
    count: int,
    max_tries: int = 800,
    **kwargs,
) -> List[List[Rect]]:
    layouts: List[List[Rect]] = []
    for _ in range(max_tries):
        layout = generate_layout(**kwargs)
        if layout is None:
            continue
        if layout_valid(layout, NEIGHBOR_RADIUS)["all"]:
            layouts.append(layout)
        if len(layouts) >= count:
            break
    return layouts


def summarize(layout: List[Rect]) -> Dict[str, float]:
    counts = {"A": 0, "B": 0}
    for r in layout:
        counts[r["type"]] += 1
    area = sum(r["w"] * r["h"] for r in layout)
    rules = layout_valid(layout, NEIGHBOR_RADIUS)
    return {
        "count_A": counts["A"],
        "count_B": counts["B"],
        "area": area,
        "rule_boundary": rules["boundary"],
        "rule_plaza": rules["plaza"],
        "rule_spacing": rules["spacing"],
        "rule_neighbor": rules["neighbor_mix"],
        "valid": rules["all"],
    }
