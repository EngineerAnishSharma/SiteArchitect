"""Evolutionary optimizer for layout generation."""
import copy
import math
import random
from typing import Dict, List, Optional

from config import BUILDING_TYPES, MIN_SPACING, NEIGHBOR_RADIUS, SETBACK, SITE_HEIGHT, SITE_WIDTH
from geometry import inside_site, intersects_plaza, layout_valid, spacing_ok

Rect = Dict[str, float]


def score_layout(layout: List[Rect]) -> float:
    """Score a layout based on multiple objectives (higher is better)."""
    validation = layout_valid(layout, NEIGHBOR_RADIUS)
    
    if not validation["all"]:
        return -1000.0  # Heavily penalize invalid layouts
    
    # Scoring components
    count_score = len(layout) * 100  # Reward more buildings
    area_score = sum(r["w"] * r["h"] for r in layout)  # Total built area
    
    # Distribution bonus: reward layouts that use space well
    if layout:
        xs = [r["x"] + r["w"]/2 for r in layout]
        ys = [r["y"] + r["h"]/2 for r in layout]
        x_spread = max(xs) - min(xs) if xs else 0
        y_spread = max(ys) - min(ys) if ys else 0
        distribution_score = (x_spread + y_spread) / 2
    else:
        distribution_score = 0
    
    # Balance Tower A and Tower B (relaxed - allow more A as long as neighbor rule is satisfied)
    count_a = sum(1 for r in layout if r["type"] == "A")
    count_b = sum(1 for r in layout if r["type"] == "B")
    balance_penalty = max(0, count_a - count_b - 3) * 15  # Allow up to 3 more A than B
    
    total_score = count_score + area_score * 0.1 + distribution_score * 0.5 - balance_penalty
    return total_score


def mutate_layout(layout: List[Rect], mutation_rate: float = 0.3) -> List[Rect]:
    """Apply random mutations to a layout."""
    mutated = copy.deepcopy(layout)
    
    if not mutated:
        return mutated
    
    # Mutation operations
    for rect in mutated:
        if random.random() < mutation_rate:
            # Small position shift
            dx = random.uniform(-10, 10)
            dy = random.uniform(-10, 10)
            rect["x"] = max(SETBACK, min(rect["x"] + dx, SITE_WIDTH - SETBACK - rect["w"]))
            rect["y"] = max(SETBACK, min(rect["y"] + dy, SITE_HEIGHT - SETBACK - rect["h"]))
    
    # Occasionally swap a building type
    if random.random() < mutation_rate * 0.5 and mutated:
        idx = random.randint(0, len(mutated) - 1)
        old_type = mutated[idx]["type"]
        new_type = "B" if old_type == "A" else "A"
        dims = BUILDING_TYPES[new_type]
        mutated[idx]["w"] = dims["w"]
        mutated[idx]["h"] = dims["h"]
        mutated[idx]["type"] = new_type
    
    return mutated


def try_add_building(layout: List[Rect], attempts: int = 50) -> Optional[List[Rect]]:
    """Try to add one more building with boundary-first strategy for Tower A."""
    new_layout = copy.deepcopy(layout)
    
    # Count existing buildings
    count_a = sum(1 for r in layout if r["type"] == "A")
    count_b = sum(1 for r in layout if r["type"] == "B")
    
    # Find all Tower A locations that need Tower B coverage
    tower_a_centers = [(r["x"] + r["w"]/2, r["y"] + r["h"]/2) for r in layout if r["type"] == "A"]
    tower_b_centers = [(r["x"] + r["w"]/2, r["y"] + r["h"]/2) for r in layout if r["type"] == "B"]
    
    # Check if any Tower A needs a closer Tower B
    needs_tower_b = False
    for ax, ay in tower_a_centers:
        has_close_b = any(math.hypot(ax - bx, ay - by) <= NEIGHBOR_RADIUS for bx, by in tower_b_centers)
        if not has_close_b:
            needs_tower_b = True
            break
    
    # If we need Tower B for existing Tower A, prioritize that
    if needs_tower_b and count_b < count_a:
        building_type = "B"
        dims = BUILDING_TYPES[building_type]
        
        # Place Tower B near uncovered Tower A
        for _ in range(attempts):
            ax, ay = random.choice(tower_a_centers)
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(25, 55)  # Within 60m radius
            
            x = ax + distance * math.cos(angle) - dims["w"] / 2
            y = ay + distance * math.sin(angle) - dims["h"] / 2
            
            x = max(SETBACK, min(x, SITE_WIDTH - SETBACK - dims["w"]))
            y = max(SETBACK, min(y, SITE_HEIGHT - SETBACK - dims["h"]))
            
            rect = {"x": x, "y": y, "w": dims["w"], "h": dims["h"], "type": building_type}
            
            if inside_site(rect) and not intersects_plaza(rect) and spacing_ok(rect, new_layout, MIN_SPACING):
                new_layout.append(rect)
                return new_layout
    
    # Otherwise, try adding Tower A near boundaries
    if count_a <= count_b + 4:  # Allow up to 4 more A than B
        building_type = "A"
        dims = BUILDING_TYPES[building_type]
        
        # Define boundary zones (near edges but respecting setback)
        boundary_zones = [
            # Left edge
            (SETBACK, random.uniform(SETBACK, SITE_HEIGHT - SETBACK - dims["h"])),
            # Right edge
            (SITE_WIDTH - SETBACK - dims["w"], random.uniform(SETBACK, SITE_HEIGHT - SETBACK - dims["h"])),
            # Top edge
            (random.uniform(SETBACK, SITE_WIDTH - SETBACK - dims["w"]), SETBACK),
            # Bottom edge
            (random.uniform(SETBACK, SITE_WIDTH - SETBACK - dims["w"]), SITE_HEIGHT - SETBACK - dims["h"]),
            # Near corners
            (SETBACK + 5, SETBACK + 5),
            (SITE_WIDTH - SETBACK - dims["w"] - 5, SETBACK + 5),
            (SETBACK + 5, SITE_HEIGHT - SETBACK - dims["h"] - 5),
            (SITE_WIDTH - SETBACK - dims["w"] - 5, SITE_HEIGHT - SETBACK - dims["h"] - 5),
        ]
        
        # Try boundary positions first
        for _ in range(attempts // 2):
            x, y = random.choice(boundary_zones)
            # Add small random offset
            x += random.uniform(-10, 10)
            y += random.uniform(-10, 10)
            
            x = max(SETBACK, min(x, SITE_WIDTH - SETBACK - dims["w"]))
            y = max(SETBACK, min(y, SITE_HEIGHT - SETBACK - dims["h"]))
            
            rect = {"x": x, "y": y, "w": dims["w"], "h": dims["h"], "type": building_type}
            
            if inside_site(rect) and not intersects_plaza(rect) and spacing_ok(rect, new_layout, MIN_SPACING):
                new_layout.append(rect)
                return new_layout
    
    # Fallback: try random placement
    building_type = random.choice(["A", "B"])
    dims = BUILDING_TYPES[building_type]
    
    for _ in range(attempts):
        x = random.uniform(SETBACK, SITE_WIDTH - SETBACK - dims["w"])
        y = random.uniform(SETBACK, SITE_HEIGHT - SETBACK - dims["h"])
        rect = {"x": x, "y": y, "w": dims["w"], "h": dims["h"], "type": building_type}
        
        if inside_site(rect) and not intersects_plaza(rect) and spacing_ok(rect, new_layout, MIN_SPACING):
            new_layout.append(rect)
            return new_layout
    
    return None


def evolve_layout(
    initial_layout: List[Rect],
    generations: int = 100,
    population_size: int = 20,
    mutation_rate: float = 0.3,
) -> List[Rect]:
    """Evolve a layout using evolutionary algorithm."""
    population = [copy.deepcopy(initial_layout) for _ in range(population_size)]
    best_layout = initial_layout
    best_score = score_layout(initial_layout)
    
    for gen in range(generations):
        # Score all individuals
        scored = [(score_layout(layout), layout) for layout in population]
        scored.sort(key=lambda x: x[0], reverse=True)
        
        # Update best
        if scored[0][0] > best_score:
            best_score = scored[0][0]
            best_layout = copy.deepcopy(scored[0][1])
        
        # Keep top 50%
        survivors = [layout for _, layout in scored[:population_size // 2]]
        
        # Generate new population
        new_population = copy.deepcopy(survivors)
        
        while len(new_population) < population_size:
            parent = random.choice(survivors)
            child = mutate_layout(parent, mutation_rate)
            
            # Occasionally try to add a building
            if random.random() < 0.3:
                improved = try_add_building(child)
                if improved is not None:
                    child = improved
            
            new_population.append(child)
        
        population = new_population
    
    return best_layout


def evolutionary_search(
    count: int,
    initial_pool: List[List[Rect]],
    generations: int = 100,
    **evolve_kwargs,
) -> List[List[Rect]]:
    """Evolve multiple initial layouts to produce diverse high-quality results."""
    evolved = []
    
    for initial in initial_pool[:count]:
        improved = evolve_layout(initial, generations, **evolve_kwargs)
        validation = layout_valid(improved, NEIGHBOR_RADIUS)
        if validation["all"]:
            evolved.append(improved)
    
    # Sort by score and return best
    evolved_scored = [(score_layout(layout), layout) for layout in evolved]
    evolved_scored.sort(key=lambda x: x[0], reverse=True)
    
    return [layout for _, layout in evolved_scored[:count]]
