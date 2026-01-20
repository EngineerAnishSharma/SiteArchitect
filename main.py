import argparse
import os
from typing import List

from generator import collect_valid_layouts, summarize
from viz import plot_layout
from evolution import evolutionary_search, score_layout
from export import export_to_json, export_to_csv


def run(args: argparse.Namespace) -> None:
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Generate initial layouts
    print(f"Generating {args.layouts} initial layouts...")
    initial_layouts = collect_valid_layouts(
        count=args.layouts if not args.evolve else args.layouts * 2,
        max_tries=args.max_tries,
        min_buildings=args.min_buildings,
        max_buildings=args.max_buildings,
        attempts_per_building=args.attempts_per_building,
        fill_extra=args.fill_extra,
        seed=args.seed,
    )

    if not initial_layouts:
        print("No valid layouts found. Try increasing max_tries or relaxing constraints.")
        return
    
    # Evolve if requested
    if args.evolve:
        print(f"Evolving layouts for {args.generations} generations...")
        layouts = evolutionary_search(
            count=args.layouts,
            initial_pool=initial_layouts,
            generations=args.generations,
            population_size=args.population_size,
            mutation_rate=args.mutation_rate,
        )
        if not layouts:
            print("Evolution produced no valid layouts, using initial ones.")
            layouts = initial_layouts[:args.layouts]
    else:
        layouts = initial_layouts
    
    # Rank layouts by score
    scored_layouts = [(score_layout(layout), layout) for layout in layouts]
    scored_layouts.sort(key=lambda x: x[0], reverse=True)
    
    print(f"\n{'='*70}")
    print(f"Generated {len(layouts)} layouts (ranked by quality score)")
    print(f"{'='*70}\n")
    
    # Store for CSV export
    all_exports = []
    
    for idx, (score, layout) in enumerate(scored_layouts, start=1):
        stats = summarize(layout)
        base_name = f"layout_{idx}"
        
        # Save PNG
        png_file = os.path.join(args.output_dir, f"{base_name}.png")
        plot_layout(layout, stats, png_file)
        
        # Save JSON if requested
        if args.export_json:
            json_file = os.path.join(args.output_dir, f"{base_name}.json")
            export_to_json(layout, stats, json_file)
        
        all_exports.append((layout, stats))
        
        print(
            f"Layout {idx}: Score={score:.1f} | A={stats['count_A']} B={stats['count_B']} | "
            f"Area={stats['area']:.0f} m² | Buildings={len(layout)} | Valid={stats['valid']}"
        )
        print(f"  → PNG: {png_file}")
        if args.export_json:
            print(f"  → JSON: {json_file}")
    
    # Export CSV summary
    if args.export_csv:
        csv_file = os.path.join(args.output_dir, "summary.csv")
        export_to_csv(all_exports, csv_file)
        print(f"\n→ CSV summary: {csv_file}")
    
    # Show aggregate statistics
    print(f"\n{'='*70}")
    print("Aggregate Statistics:")
    print(f"{'='*70}")
    avg_buildings = sum(len(layout) for _, layout in scored_layouts) / len(scored_layouts)
    avg_area = sum(stats['area'] for _, stats in all_exports) / len(all_exports)
    avg_score = sum(score for score, _ in scored_layouts) / len(scored_layouts)
    print(f"  Average buildings per layout: {avg_buildings:.1f}")
    print(f"  Average built area: {avg_area:.0f} m²")
    print(f"  Average quality score: {avg_score:.1f}")
    print(f"  Best score: {scored_layouts[0][0]:.1f}")
    print(f"  Worst score: {scored_layouts[-1][0]:.1f}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate building layouts")
    parser.add_argument("--layouts", type=int, default=4, help="Number of layouts to save")
    parser.add_argument("--max-tries", type=int, default=800, help="Attempts to search for valid layouts")
    parser.add_argument("--min-buildings", type=int, default=5, help="Minimum buildings per layout")
    parser.add_argument("--max-buildings", type=int, default=12, help="Maximum buildings per layout")
    parser.add_argument("--attempts-per-building", type=int, default=120, help="Placement retries per building")
    parser.add_argument("--fill-extra", type=int, default=2, help="Greedy extra buildings to try adding after a valid draft")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    parser.add_argument("--output-dir", default="outputs", help="Directory to save plots")
    
    # Evolutionary optimization
    parser.add_argument("--evolve", action="store_true", help="Use evolutionary algorithm to improve layouts")
    parser.add_argument("--generations", type=int, default=100, help="Number of evolution generations")
    parser.add_argument("--population-size", type=int, default=20, help="Population size for evolution")
    parser.add_argument("--mutation-rate", type=float, default=0.3, help="Mutation rate (0.0-1.0)")
    
    # Export options
    parser.add_argument("--export-json", action="store_true", help="Export each layout as JSON")
    parser.add_argument("--export-csv", action="store_true", help="Export summary statistics as CSV")
    
    run(parser.parse_args())
