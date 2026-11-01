import os
from dataclasses import dataclass, field

@dataclass
class EAConfig:
    """
    Hyperparameters configuration for Evolutionary Algorithm Polygon Reconstruction.
    """
    # Target Image
    target_image_path: str = os.path.join(
        os.path.dirname(__file__), 'assets', 'mona_lisa.jpg'
    )
    working_width: int = 180       # Evaluation canvas width (balances speed vs. accuracy)
    working_height: int = 240      # Evaluation canvas height

    # Individual / Chromosome Structure
    num_polygons: int = 50         # Number of semi-transparent polygons per individual
    vertices_per_polygon: int = 3  # Vertices per polygon (3 = triangles, 4 = quads)
    min_alpha: int = 20            # Minimum alpha opacity (0..255)
    max_alpha: int = 140           # Maximum alpha opacity (transparency allows subtle color mixing)

    # Evolutionary Dynamics
    population_size: int = 5       # Size of population mu (5 or 1 for fast convergence)
    num_offspring: int = 4         # Number of offspring generated per generation lambda
    mutation_rate: float = 0.85    # Probability of mutating a polygon in the chromosome
    mutation_strength: float = 0.12# Coordinate / color delta step size [0.01 .. 0.5]
    reorder_prob: float = 0.08     # Probability of swapping two polygon layers (Z-order)

    # Selection Scheme
    selection_scheme: str = 'Truncation'  # 'Truncation', 'Tournament', 'Rank', 'Elitism'
    tournament_k: int = 3

    # Termination Criteria
    max_generations: int = 15000   # 0 or None for infinite run until user stops
    target_fitness: float = 98.5   # Target similarity percentage (0..100)

    # Output & Snapshots
    output_dir: str = os.path.join(os.path.dirname(__file__), 'output')
    save_interval: int = 250       # Save snapshot image every N generations

