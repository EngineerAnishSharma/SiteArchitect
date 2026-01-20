"""Create comparison visualization between approaches."""
import matplotlib.pyplot as plt
import os

from generator import collect_valid_layouts
from evolution import evolutionary_search, score_layout
from viz import plot_layout
from generator import summarize


def create_comparison():
    """Generate side-by-side comparison of random vs evolved layouts."""
    print("Generating comparison layouts...")
    
    # Generate random layout
    random_layouts = collect_valid_layouts(
        count=1,
        max_tries=1500,
        min_buildings=5,
        max_buildings=10,
        attempts_per_building=150,
        fill_extra=2,
    )
    
    if not random_layouts:
        print("Failed to generate random layout")
        return
    
    # Evolve it
    print("Evolving layout...")
    evolved = evolutionary_search(
        count=1,
        initial_pool=random_layouts,
        generations=150,
        population_size=30,
        mutation_rate=0.3,
    )
    
    if not evolved:
        print("Evolution failed")
        return
    
    random_layout = random_layouts[0]
    evolved_layout = evolved[0]
    
    # Get stats
    random_stats = summarize(random_layout)
    evolved_stats = summarize(evolved_layout)
    
    random_score = score_layout(random_layout)
    evolved_score = score_layout(evolved_layout)
    
    # Create side-by-side visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))
    
    from config import SITE_WIDTH, SITE_HEIGHT, PLAZA
    from matplotlib.patches import Rectangle
    
    for ax, layout, stats, title, score in [
        (ax1, random_layout, random_stats, "Random Search", random_score),
        (ax2, evolved_layout, evolved_stats, "After Evolution", evolved_score),
    ]:
        ax.set_xlim(0, SITE_WIDTH)
        ax.set_ylim(0, SITE_HEIGHT)
        ax.set_aspect("equal")
        ax.set_title(f"{title}\nScore: {score:.1f} | Buildings: {len(layout)} | Area: {stats['area']:.0f} m²", fontsize=12, fontweight='bold')
        
        # Site
        site_patch = Rectangle((0, 0), SITE_WIDTH, SITE_HEIGHT, fill=False, lw=2, color="#222")
        ax.add_patch(site_patch)
        
        # Plaza
        plaza_patch = Rectangle((PLAZA["x"], PLAZA["y"]), PLAZA["w"], PLAZA["h"], color="#cccccc", alpha=0.5)
        ax.add_patch(plaza_patch)
        ax.text(PLAZA["x"] + PLAZA["w"]/2, PLAZA["y"] + PLAZA["h"]/2, "Plaza", ha="center", va="center", fontsize=9, color="#333")
        
        # Buildings
        colors = {"A": "#1f77b4", "B": "#ff7f0e"}
        for rect in layout:
            color = colors.get(rect["type"], "#2ca02c")
            patch = Rectangle((rect["x"], rect["y"]), rect["w"], rect["h"], color=color, alpha=0.8, lw=1.5, ec="#111")
            ax.add_patch(patch)
            ax.text(rect["x"] + rect["w"]/2, rect["y"] + rect["h"]/2, rect["type"], ha="center", va="center", fontsize=9, color="white", fontweight='bold')
        
        ax.set_xlabel("Meters (x)")
        ax.set_ylabel("Meters (y)")
        ax.grid(True, linestyle="--", alpha=0.3)
    
    # Add comparison text
    improvement = ((evolved_score - random_score) / random_score * 100)
    building_gain = len(evolved_layout) - len(random_layout)
    
    fig.text(0.5, 0.02, f"Evolution improved score by {improvement:.1f}% and added {building_gain} buildings", 
             ha='center', fontsize=11, fontweight='bold', color='green' if building_gain > 0 else 'red')
    
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    outfile = os.path.join(output_dir, "comparison_random_vs_evolved.png")
    fig.savefig(outfile, dpi=150, bbox_inches='tight')
    plt.close(fig)
    
    print(f"\nComparison saved: {outfile}")
    print(f"\nRandom:  {len(random_layout)} buildings, score {random_score:.1f}")
    print(f"Evolved: {len(evolved_layout)} buildings, score {evolved_score:.1f}")
    print(f"Gain:    {building_gain:+d} buildings ({improvement:+.1f}% score)")


if __name__ == "__main__":
    create_comparison()
