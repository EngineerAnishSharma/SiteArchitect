"""Test script to generate layouts covering various scenarios and edge cases."""
import os
from typing import List

from generator import collect_valid_layouts, generate_layout, summarize
from geometry import layout_valid
from config import NEIGHBOR_RADIUS
from viz import plot_layout


def test_scenario(name: str, output_dir: str, **gen_kwargs):
    """Generate and save layouts for a specific test scenario."""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"{'='*60}")
    
    layouts = collect_valid_layouts(count=2, max_tries=1000, **gen_kwargs)
    
    if not layouts:
        print(f"❌ No valid layouts found for {name}")
        return
    
    for idx, layout in enumerate(layouts, start=1):
        stats = summarize(layout)
        outfile = os.path.join(output_dir, f"{name.replace(' ', '_').lower()}_{idx}.png")
        plot_layout(layout, stats, outfile)
        
        violations = []
        if not stats['rule_boundary']:
            violations.append("boundary")
        if not stats['rule_plaza']:
            violations.append("plaza")
        if not stats['rule_spacing']:
            violations.append("spacing")
        if not stats['rule_neighbor']:
            violations.append("neighbor-mix")
        
        status = "✓ VALID" if stats['valid'] else f"✗ INVALID ({', '.join(violations)})"
        print(f"  Layout {idx}: A={stats['count_A']}, B={stats['count_B']}, Area={stats['area']:.0f} m² - {status}")
        print(f"    Saved: {outfile}")


def generate_stress_test_layouts(output_dir: str):
    """Generate very dense layouts to stress test the visualization."""
    print(f"\n{'='*60}")
    print(f"Testing: Stress test (very dense packing)")
    print(f"{'='*60}")
    
    layouts = collect_valid_layouts(
        count=2,
        max_tries=3000,
        min_buildings=12,
        max_buildings=18,
        attempts_per_building=200,
        fill_extra=8
    )
    
    if layouts:
        print(f"  Found {len(layouts)} dense layouts")
        for idx, layout in enumerate(layouts, start=1):
            stats = summarize(layout)
            outfile = os.path.join(output_dir, f"stress_dense_{idx}.png")
            plot_layout(layout, stats, outfile)
            print(f"  Layout {idx}: A={stats['count_A']}, B={stats['count_B']}, Area={stats['area']:.0f} m² - ✓ VALID")
            print(f"    Saved: {outfile}")
    else:
        print(f"  ❌ No dense layouts found (constraints too tight)")


def generate_manual_test_cases(output_dir: str):
    """Create hand-crafted scenarios to test specific visualization features."""
    from geometry import find_violations
    
    print(f"\n{'='*60}")
    print(f"Testing: Manual test cases")
    print(f"{'='*60}")
    
    # Case 1: Minimal valid layout
    manual_layout_1 = [
        {"x": 20.0, "y": 20.0, "w": 30.0, "h": 20.0, "type": "A"},
        {"x": 70.0, "y": 20.0, "w": 20.0, "h": 20.0, "type": "B"},
        {"x": 140.0, "y": 20.0, "w": 30.0, "h": 20.0, "type": "A"},
        {"x": 140.0, "y": 60.0, "w": 20.0, "h": 20.0, "type": "B"},
    ]
    
    stats_1 = summarize(manual_layout_1)
    outfile_1 = os.path.join(output_dir, "manual_basic_valid.png")
    plot_layout(manual_layout_1, stats_1, outfile_1)
    print(f"  Manual basic: A={stats_1['count_A']}, B={stats_1['count_B']}, Valid={stats_1['valid']}")
    print(f"    Saved: {outfile_1}")
    
    # Case 2: Spacing violation (buildings too close)
    manual_layout_2 = [
        {"x": 20.0, "y": 20.0, "w": 30.0, "h": 20.0, "type": "A"},
        {"x": 55.0, "y": 20.0, "w": 20.0, "h": 20.0, "type": "B"},  # Too close to A
        {"x": 140.0, "y": 20.0, "w": 30.0, "h": 20.0, "type": "A"},
        {"x": 140.0, "y": 60.0, "w": 20.0, "h": 20.0, "type": "B"},
    ]
    
    stats_2 = summarize(manual_layout_2)
    outfile_2 = os.path.join(output_dir, "manual_spacing_violation.png")
    plot_layout(manual_layout_2, stats_2, outfile_2)
    print(f"  Spacing violation: A={stats_2['count_A']}, B={stats_2['count_B']}, Valid={stats_2['valid']}")
    print(f"    Saved: {outfile_2}")
    
    # Case 3: Plaza violation (building overlaps plaza)
    manual_layout_3 = [
        {"x": 20.0, "y": 20.0, "w": 30.0, "h": 20.0, "type": "A"},
        {"x": 70.0, "y": 20.0, "w": 20.0, "h": 20.0, "type": "B"},
        {"x": 90.0, "y": 55.0, "w": 30.0, "h": 20.0, "type": "A"},  # Overlaps plaza at (80-120, 50-90)
        {"x": 140.0, "y": 20.0, "w": 20.0, "h": 20.0, "type": "B"},
    ]
    
    stats_3 = summarize(manual_layout_3)
    outfile_3 = os.path.join(output_dir, "manual_plaza_violation.png")
    plot_layout(manual_layout_3, stats_3, outfile_3)
    print(f"  Plaza violation: A={stats_3['count_A']}, B={stats_3['count_B']}, Valid={stats_3['valid']}")
    print(f"    Saved: {outfile_3}")
    
    # Case 4: Neighbor-mix violation (Tower A far from all Bs)
    manual_layout_4 = [
        {"x": 20.0, "y": 20.0, "w": 30.0, "h": 20.0, "type": "A"},
        {"x": 20.0, "y": 100.0, "w": 20.0, "h": 20.0, "type": "B"},  # Far from first A
        {"x": 150.0, "y": 20.0, "w": 30.0, "h": 20.0, "type": "A"},
        {"x": 150.0, "y": 100.0, "w": 20.0, "h": 20.0, "type": "B"},
    ]
    
    stats_4 = summarize(manual_layout_4)
    outfile_4 = os.path.join(output_dir, "manual_neighbor_violation.png")
    plot_layout(manual_layout_4, stats_4, outfile_4)
    print(f"  Neighbor violation: A={stats_4['count_A']}, B={stats_4['count_B']}, Valid={stats_4['valid']}")
    print(f"    Saved: {outfile_4}")
    
    # Case 5: Boundary violation (building outside setback)
    manual_layout_5 = [
        {"x": 5.0, "y": 20.0, "w": 30.0, "h": 20.0, "type": "A"},  # Too close to left edge
        {"x": 50.0, "y": 20.0, "w": 20.0, "h": 20.0, "type": "B"},
        {"x": 140.0, "y": 20.0, "w": 30.0, "h": 20.0, "type": "A"},
        {"x": 140.0, "y": 60.0, "w": 20.0, "h": 20.0, "type": "B"},
    ]
    
    stats_5 = summarize(manual_layout_5)
    outfile_5 = os.path.join(output_dir, "manual_boundary_violation.png")
    plot_layout(manual_layout_5, stats_5, outfile_5)
    print(f"  Boundary violation: A={stats_5['count_A']}, B={stats_5['count_B']}, Valid={stats_5['valid']}")
    print(f"    Saved: {outfile_5}")
    
    # Case 6: Multiple violations
    manual_layout_6 = [
        {"x": 5.0, "y": 20.0, "w": 30.0, "h": 20.0, "type": "A"},  # Boundary violation
        {"x": 40.0, "y": 20.0, "w": 20.0, "h": 20.0, "type": "B"},  # Spacing violation with A
        {"x": 95.0, "y": 60.0, "w": 30.0, "h": 20.0, "type": "A"},  # Plaza violation
        {"x": 170.0, "y": 100.0, "w": 20.0, "h": 20.0, "type": "B"},  # Too close to edge
    ]
    
    stats_6 = summarize(manual_layout_6)
    outfile_6 = os.path.join(output_dir, "manual_multiple_violations.png")
    plot_layout(manual_layout_6, stats_6, outfile_6)
    print(f"  Multiple violations: A={stats_6['count_A']}, B={stats_6['count_B']}, Valid={stats_6['valid']}")
    print(f"    Saved: {outfile_6}")
    
    # Case 7: Dense valid layout
    manual_layout_7 = [
        {"x": 15.0, "y": 15.0, "w": 30.0, "h": 20.0, "type": "A"},
        {"x": 60.0, "y": 15.0, "w": 20.0, "h": 20.0, "type": "B"},
        {"x": 15.0, "y": 100.0, "w": 30.0, "h": 20.0, "type": "A"},
        {"x": 60.0, "y": 100.0, "w": 20.0, "h": 20.0, "type": "B"},
        {"x": 130.0, "y": 15.0, "w": 30.0, "h": 20.0, "type": "A"},
        {"x": 130.0, "y": 50.0, "w": 20.0, "h": 20.0, "type": "B"},
        {"x": 165.0, "y": 15.0, "w": 20.0, "h": 20.0, "type": "B"},
        {"x": 130.0, "y": 100.0, "w": 30.0, "h": 20.0, "type": "A"},
    ]
    
    stats_7 = summarize(manual_layout_7)
    outfile_7 = os.path.join(output_dir, "manual_dense_valid.png")
    plot_layout(manual_layout_7, stats_7, outfile_7)
    print(f"  Dense valid: A={stats_7['count_A']}, B={stats_7['count_B']}, Valid={stats_7['valid']}")
    print(f"    Saved: {outfile_7}")


def generate_invalid_for_testing(output_dir: str):
    """Try to generate layouts that might violate rules for visualization testing."""
    print(f"\n{'='*60}")
    print(f"Testing: Intentional violations (relaxed validation)")
    print(f"{'='*60}")
    
    # Try many layouts and keep some invalid ones for testing
    attempts = 0
    found_invalid = []
    
    while len(found_invalid) < 2 and attempts < 2000:
        layout = generate_layout(min_buildings=8, max_buildings=15, attempts_per_building=80, fill_extra=5)
        attempts += 1
        
        if layout is not None:
            validation = layout_valid(layout, NEIGHBOR_RADIUS)
            if not validation["all"]:  # Found an invalid layout
                found_invalid.append(layout)
    
    if found_invalid:
        print(f"  Found {len(found_invalid)} invalid layouts after {attempts} attempts")
        for idx, layout in enumerate(found_invalid, start=1):
            stats = summarize(layout)
            outfile = os.path.join(output_dir, f"invalid_test_{idx}.png")
            plot_layout(layout, stats, outfile)
            
            violations = []
            if not stats['rule_boundary']:
                violations.append("boundary")
            if not stats['rule_plaza']:
                violations.append("plaza")
            if not stats['rule_spacing']:
                violations.append("spacing")
            if not stats['rule_neighbor']:
                violations.append("neighbor-mix")
            
            print(f"  Layout {idx}: A={stats['count_A']}, B={stats['count_B']}, Area={stats['area']:.0f} m² - INVALID ({', '.join(violations)})")
            print(f"    Saved: {outfile}")
    else:
        print(f"  ❌ No invalid layouts found in {attempts} attempts (all passed validation)")


def main():
    output_dir = "outputs/test_cases"
    os.makedirs(output_dir, exist_ok=True)
    
    print("Starting comprehensive layout testing...")
    print(f"Output directory: {output_dir}")
    
    # Test 1: Minimal layouts (low density)
    test_scenario(
        "Minimal Sparse Layout",
        output_dir,
        min_buildings=3,
        max_buildings=5,
        attempts_per_building=150,
        fill_extra=0,
        seed=42
    )
    
    # Test 2: Medium density
    test_scenario(
        "Medium Density Layout",
        output_dir,
        min_buildings=6,
        max_buildings=10,
        attempts_per_building=120,
        fill_extra=2,
        seed=123
    )
    
    # Test 3: Moderate density (more realistic)
    test_scenario(
        "Moderate Density Layout",
        output_dir,
        min_buildings=7,
        max_buildings=11,
        attempts_per_building=150,
        fill_extra=3,
        seed=456
    )
    
    # Test 4: Tower A heavy (tests neighbor-mix rule)
    test_scenario(
        "Tower A Heavy Mix",
        output_dir,
        min_buildings=6,
        max_buildings=10,
        attempts_per_building=120,
        fill_extra=0,
        seed=789
    )
    
    # Test 5: Balanced moderate
    test_scenario(
        "Balanced Layout",
        output_dir,
        min_buildings=5,
        max_buildings=9,
        attempts_per_building=140,
        fill_extra=2,
        seed=999
    )
    
    # Test 6: Dense stress test
    generate_stress_test_layouts(output_dir)
    
    # Test 7: Manual test cases
    generate_manual_test_cases(output_dir)
    
    # Test 8: Try to find layouts with violations
    generate_invalid_for_testing(output_dir)
    
    print(f"\n{'='*60}")
    print("✓ Testing complete!")
    print(f"Check {output_dir} for all generated test layouts")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
