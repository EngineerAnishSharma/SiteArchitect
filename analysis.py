"""Batch analysis to compare random vs evolutionary approaches."""
import os
import statistics

from generator import collect_valid_layouts, summarize
from evolution import evolutionary_search, score_layout


def analyze_approach(name: str, layouts, output_dir: str):
    """Analyze and report statistics for a set of layouts."""
    print(f"\n{'='*70}")
    print(f"{name}")
    print(f"{'='*70}")
    
    if not layouts:
        print("  No layouts generated!")
        return
    
    scores = [score_layout(layout) for layout in layouts]
    building_counts = [len(layout) for layout in layouts]
    areas = [sum(r["w"] * r["h"] for r in layout) for layout in layouts]
    
    tower_a_counts = [sum(1 for r in layout if r["type"] == "A") for layout in layouts]
    tower_b_counts = [sum(1 for r in layout if r["type"] == "B") for layout in layouts]
    
    print(f"  Layouts generated: {len(layouts)}")
    print(f"\n  Quality Score:")
    print(f"    Mean:   {statistics.mean(scores):.1f}")
    print(f"    Median: {statistics.median(scores):.1f}")
    print(f"    Max:    {max(scores):.1f}")
    print(f"    Min:    {min(scores):.1f}")
    print(f"    StdDev: {statistics.stdev(scores) if len(scores) > 1 else 0:.1f}")
    
    print(f"\n  Buildings per Layout:")
    print(f"    Mean:   {statistics.mean(building_counts):.1f}")
    print(f"    Median: {statistics.median(building_counts):.1f}")
    print(f"    Max:    {max(building_counts)}")
    print(f"    Min:    {min(building_counts)}")
    
    print(f"\n  Built Area (m²):")
    print(f"    Mean:   {statistics.mean(areas):.0f}")
    print(f"    Max:    {max(areas):.0f}")
    print(f"    Min:    {min(areas):.0f}")
    
    print(f"\n  Tower Mix:")
    print(f"    Avg Tower A: {statistics.mean(tower_a_counts):.1f}")
    print(f"    Avg Tower B: {statistics.mean(tower_b_counts):.1f}")
    print(f"    A/B Ratio:   {statistics.mean(tower_a_counts) / statistics.mean(tower_b_counts):.2f}")


def main():
    print("\n" + "="*70)
    print("BATCH ANALYSIS: Random Search vs Evolutionary Optimization")
    print("="*70)
    
    output_dir = "outputs/analysis"
    os.makedirs(output_dir, exist_ok=True)
    
    # Test 1: Random search
    print("\n[1/2] Running random search (20 layouts)...")
    random_layouts = collect_valid_layouts(
        count=20,
        max_tries=2000,
        min_buildings=6,
        max_buildings=14,
        attempts_per_building=150,
        fill_extra=3,
    )
    
    analyze_approach("Random Search Results", random_layouts, output_dir)
    
    # Test 2: Evolutionary approach
    if random_layouts:
        print("\n[2/2] Running evolutionary optimization...")
        initial_pool = random_layouts[:10]  # Use 10 as starting points
        evolved_layouts = evolutionary_search(
            count=20,
            initial_pool=initial_pool * 2,  # Duplicate to have enough
            generations=120,
            population_size=25,
            mutation_rate=0.3,
        )
        
        analyze_approach("Evolutionary Optimization Results", evolved_layouts, output_dir)
        
        # Comparison
        if evolved_layouts:
            print(f"\n{'='*70}")
            print("COMPARISON")
            print(f"{'='*70}")
            
            random_avg_score = statistics.mean([score_layout(l) for l in random_layouts])
            evolved_avg_score = statistics.mean([score_layout(l) for l in evolved_layouts])
            
            random_avg_buildings = statistics.mean([len(l) for l in random_layouts])
            evolved_avg_buildings = statistics.mean([len(l) for l in evolved_layouts])
            
            improvement_score = ((evolved_avg_score - random_avg_score) / random_avg_score) * 100
            improvement_buildings = ((evolved_avg_buildings - random_avg_buildings) / random_avg_buildings) * 100
            
            print(f"  Average Score Improvement:    {improvement_score:+.1f}%")
            print(f"  Average Building Count Gain:  {improvement_buildings:+.1f}%")
            print(f"  Evolution produces {improvement_buildings:+.1f}% more buildings on average!")
    
    print(f"\n{'='*70}")
    print("Analysis complete!")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
