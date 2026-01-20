# Layout Generator - Usage Examples

## Basic Usage

### Generate simple layouts
```bash
# Generate 4 random layouts
python main.py

# Generate more layouts
python main.py --layouts 10
```

### Adjust density
```bash
# Try to pack more buildings
python main.py --min-buildings 8 --max-buildings 14 --fill-extra 5 --max-tries 1500

# Sparse layouts
python main.py --min-buildings 3 --max-buildings 6 --fill-extra 0
```

## Evolutionary Optimization

### Enable evolution for better results
```bash
# Basic evolution (default: 100 generations)
python main.py --layouts 5 --evolve

# Intensive evolution for maximum density
python main.py --layouts 5 --evolve --generations 200 --population-size 40

# Quick evolution
python main.py --layouts 8 --evolve --generations 50 --population-size 15
```

### Tune evolution parameters
```bash
# Higher mutation rate for more diversity
python main.py --evolve --mutation-rate 0.5 --generations 150

# Lower mutation rate for refinement
python main.py --evolve --mutation-rate 0.15 --generations 100
```

## Data Export

### Export layouts as JSON
```bash
# Individual JSON files per layout
python main.py --layouts 5 --export-json

# With evolution
python main.py --layouts 5 --evolve --export-json
```

### Export summary statistics
```bash
# CSV summary table
python main.py --layouts 10 --export-csv

# Both JSON and CSV
python main.py --layouts 5 --export-json --export-csv
```

## Reproducibility

### Use seeds for deterministic results
```bash
# Same layouts every time
python main.py --layouts 3 --seed 42

# Different but reproducible
python main.py --layouts 3 --seed 12345 --evolve --generations 100
```

## Advanced Examples

### High-quality dense layouts
```bash
python main.py \
  --layouts 6 \
  --evolve \
  --generations 150 \
  --population-size 30 \
  --min-buildings 10 \
  --max-buildings 16 \
  --fill-extra 5 \
  --max-tries 2000 \
  --export-json \
  --export-csv
```

### Batch comparison study
```bash
# Generate many layouts for analysis
python main.py --layouts 20 --export-csv --output-dir outputs/batch_random
python main.py --layouts 20 --evolve --export-csv --output-dir outputs/batch_evolved

# Run statistical comparison
python analysis.py
```

### Quick validation test
```bash
# Test all violation types
python test.py

# Generate visual comparison
python comparison.py
```

## Output Organization

### Use different output directories
```bash
# Organize by experiment
python main.py --output-dir outputs/exp1_random
python main.py --evolve --output-dir outputs/exp2_evolved

# Date-based folders
python main.py --output-dir "outputs/2026-01-20_run1"
```

## Performance Tips

1. **For speed**: Use fewer layouts, lower max-tries, skip evolution
   ```bash
   python main.py --layouts 3 --max-tries 400
   ```

2. **For quality**: Enable evolution with high generations
   ```bash
   python main.py --layouts 5 --evolve --generations 200
   ```

3. **For diversity**: Generate many layouts, sort by score
   ```bash
   python main.py --layouts 20 --export-csv
   ```

4. **For dense packing**: Increase ranges and fill-extra
   ```bash
   python main.py --max-buildings 18 --fill-extra 8 --max-tries 3000
   ```

## Common Workflows

### Research workflow
```bash
# 1. Generate baseline
python main.py --layouts 10 --export-csv --output-dir outputs/baseline

# 2. Run evolution
python main.py --layouts 10 --evolve --generations 150 --export-csv --output-dir outputs/evolved

# 3. Analyze results
python analysis.py
```

### Quick demo
```bash
# Generate visual comparison in 30 seconds
python comparison.py
```

### Production run
```bash
# Generate 50 high-quality layouts with full data export
python main.py \
  --layouts 50 \
  --evolve \
  --generations 120 \
  --population-size 25 \
  --export-json \
  --export-csv \
  --output-dir outputs/production_run
```
