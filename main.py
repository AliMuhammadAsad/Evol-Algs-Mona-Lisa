import sys
import os
import argparse
import time

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
from config import EAConfig
from evolAlgs import EvolutionaryAlgorithm

def run_cli(args):
    print("=" * 70)
    print("🧬 NEURAL GENETIC LAB // MONA LISA POLYGON EVOLVER (CLI MODE)")
    print("=" * 70)

    config = EAConfig()
    if args.image:
        config.target_image_path = args.image
    if args.polygons:
        config.num_polygons = args.polygons
    if args.vertices:
        config.vertices_per_polygon = args.vertices
    if args.generations:
        config.max_generations = args.generations
    if args.mutation_rate:
        config.mutation_rate = args.mutation_rate
    if args.pop_size:
        config.population_size = args.pop_size
    if args.output:
        config.output_dir = args.output

    print(f"Target Image      : {config.target_image_path}")
    print(f"Polygon Genes     : {config.num_polygons} ({config.vertices_per_polygon} vertices/poly)")
    print(f"Population Size   : {config.population_size}")
    print(f"Mutation Rate     : {config.mutation_rate * 100:.1f}%")
    print(f"Max Generations   : {config.max_generations}")
    print(f"Output Directory  : {config.output_dir}")
    print("-" * 70)

    ea = EvolutionaryAlgorithm(config)
    print(f"Initial Fitness: {ea.best_fitness:.2f}% | MSE Error: {ea.best_individual.mse_error:.2f}")
    print("Starting Evolutionary Cycle (Press Ctrl+C to stop)...")
    print("-" * 70)

    start_time = time.time()
    last_print = start_time

    try:
        while ea.generation < config.max_generations:
            best_ind = ea.step()
            now = time.time()

            if now - last_print >= 1.0 or ea.generation == config.max_generations:
                elapsed = now - start_time
                gps = ea.generation / max(0.001, elapsed)
                print(
                    f"\r[GEN {ea.generation:06d}/{config.max_generations}] "
                    f"Fit: {ea.best_fitness:6.2f}% | "
                    f"MSE: {best_ind.mse_error:7.1f} | "
                    f"Speed: {gps:5.1f} gen/s | "
                    f"Elapsed: {int(elapsed)}s",
                    end="",
                    flush=True
                )
                last_print = now

    except KeyboardInterrupt:
        print("\n[INTERRUPTED BY USER]")

    print("\n" + "=" * 70)
    print(f"EVOLUTION COMPLETED // Best Fitness: {ea.best_fitness:.2f}%")
    final_out = os.path.join(config.output_dir, 'mona_lisa_reconstruction_final.png')
    ea.save_checkpoint('mona_lisa_reconstruction_final.png')
    print(f"Saved final render to: {final_out}")
    print("=" * 70)

def main():
    parser = argparse.ArgumentParser(description="Evolutionary Algorithm Polygon Image Reconstruction")
    parser.add_argument("--cli", action="store_true", help="Run in terminal CLI mode (headless)")
    parser.add_argument("--image", type=str, help="Path to reference target image")
    parser.add_argument("--polygons", type=int, help="Number of polygons")
    parser.add_argument("--vertices", type=int, help="Number of vertices per polygon")
    parser.add_argument("--generations", type=int, default=5000, help="Number of generations to run")
    parser.add_argument("--mutation-rate", type=float, help="Mutation rate (0.0 - 1.0)")
    parser.add_argument("--pop-size", type=int, help="Population size")
    parser.add_argument("--output", type=str, help="Directory to save output renders")

    args = parser.parse_args()

    if args.cli:
        run_cli(args)
    else:
        # Launch Desktop GUI by default
        try:
            from gui import run_app
            run_app()
        except Exception as e:
            print(f"Note: Desktop GUI could not initialize ({e}). Falling back to CLI mode...")
            run_cli(args)

if __name__ == "__main__":
    main()
