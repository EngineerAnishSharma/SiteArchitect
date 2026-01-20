"""Export layouts to various formats."""
import json
from typing import Any, Dict, List

from config import (
    BUILDING_TYPES,
    MIN_SPACING,
    NEIGHBOR_RADIUS,
    PLAZA,
    SETBACK,
    SITE_HEIGHT,
    SITE_WIDTH,
)

Rect = Dict[str, float]


def export_to_json(layout: List[Rect], stats: Dict[str, Any], filepath: str) -> None:
    """Export a layout to JSON format."""
    data = {
        "site": {
            "width": SITE_WIDTH,
            "height": SITE_HEIGHT,
            "setback": SETBACK,
        },
        "plaza": PLAZA,
        "constraints": {
            "min_spacing": MIN_SPACING,
            "neighbor_radius": NEIGHBOR_RADIUS,
        },
        "buildings": [
            {
                "id": idx,
                "type": rect["type"],
                "x": rect["x"],
                "y": rect["y"],
                "width": rect["w"],
                "height": rect["h"],
                "center_x": rect["x"] + rect["w"] / 2,
                "center_y": rect["y"] + rect["h"] / 2,
                "area": rect["w"] * rect["h"],
            }
            for idx, rect in enumerate(layout)
        ],
        "statistics": {
            "total_buildings": len(layout),
            "tower_a_count": stats.get("count_A", 0),
            "tower_b_count": stats.get("count_B", 0),
            "total_built_area": stats.get("area", 0),
            "valid": stats.get("valid", False),
        },
        "rule_validation": {
            "boundary": stats.get("rule_boundary", False),
            "plaza": stats.get("rule_plaza", False),
            "spacing": stats.get("rule_spacing", False),
            "neighbor_mix": stats.get("rule_neighbor", False),
        },
    }
    
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)


def export_to_csv(layouts: List[tuple[List[Rect], Dict[str, Any]]], filepath: str) -> None:
    """Export multiple layouts to CSV summary format."""
    import csv
    
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "layout_id",
            "total_buildings",
            "tower_a_count",
            "tower_b_count",
            "total_area_m2",
            "valid",
            "rule_boundary",
            "rule_plaza",
            "rule_spacing",
            "rule_neighbor_mix",
        ])
        
        for idx, (layout, stats) in enumerate(layouts, start=1):
            writer.writerow([
                idx,
                len(layout),
                stats.get("count_A", 0),
                stats.get("count_B", 0),
                stats.get("area", 0),
                stats.get("valid", False),
                stats.get("rule_boundary", False),
                stats.get("rule_plaza", False),
                stats.get("rule_spacing", False),
                stats.get("rule_neighbor", False),
            ])
