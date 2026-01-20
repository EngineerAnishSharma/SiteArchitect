# Layout Generator

Python script that generates multiple feasible layouts for two tower types on a 200 m × 140 m site while enforcing spacing, setback, plaza, and neighbor-mix rules. Plots now annotate inter-building distances and highlight violations in red.

## Features
- **Random search** with constraint checking
- **Evolutionary optimization** to maximize building count and quality
- **Ranking system** scoring layouts by density, balance, and distribution
- **Visual annotations** showing distances, violations, and neighbor relationships
- **JSON/CSV export** for external analysis and integration

## Requirements
- Python 3.10+
- matplotlib

Install deps:
```
pip install -r requirements.txt
```

## Quick Start
Generate 4 random valid layouts:
```
python main.py --layouts 4
```

## Advanced Usage

### Evolutionary Optimization
Use genetic algorithm to evolve better layouts:
```
python main.py --layouts 6 --evolve --generations 150 --population-size 30
```

### Export Data
Save layouts as JSON and summary as CSV:
```
python main.py --layouts 4 --export-json --export-csv
```

### High-density Search
Try to pack more buildings:
```
python main.py --layouts 5 --max-tries 1500 --min-buildings 8 --max-buildings 15 --fill-extra 5
```

### Reproducible Results
Set a seed for deterministic generation:
```
python main.py --layouts 3 --seed 42
```

## Key Flags
- `--layouts` (default 4): Number of layouts to generate
- `--max-tries` (default 800): Search attempts for valid layouts
- `--min-buildings` / `--max-buildings`: Building count range per layout
- `--attempts-per-building`: Placement retries per building
- `--fill-extra` (default 2): Extra greedy placements to densify layouts
- `--evolve`: Enable evolutionary optimization (slower but better quality)
- `--generations` (default 100): Evolution iterations when `--evolve` is used
- `--population-size` (default 20): Population size for evolution
- `--mutation-rate` (default 0.3): Mutation probability (0.0-1.0)
- `--export-json`: Export each layout as JSON with full metadata
- `--export-csv`: Export summary statistics table
- `--seed`: Random seed for reproducibility
- `--output-dir` (default outputs): Output folder

## Outputs
- **PNG images**: Visualizations with distance annotations, violation highlights, and neighbor links
- **JSON files** (if `--export-json`): Layout coordinates, constraints, and validation results
- **CSV summary** (if `--export-csv`): Aggregate statistics table for all layouts

## Testing
Run comprehensive test suite covering all rule violations:
```
python test.py
```
Outputs in `outputs/test_cases/` include examples of spacing, plaza, boundary, and neighbor-mix violations.

## Scoring System
Layouts are ranked by a quality score considering:
- **Building count** (higher is better)
- **Total built area** (more coverage)
- **Spatial distribution** (using full site)
- **Tower balance** (prefer similar counts of A and B)

Valid layouts always score higher than invalid ones.
