import os
import time
import random
from typing import List, Callable, Optional
from PIL import Image
from config import EAConfig
from polygon import Individual
from fitness import FitnessEvaluator
from selecSchemes import SelectionSchemes

class EvolutionaryAlgorithm:
    """
    Core Evolutionary Algorithm Engine for polygon-based image approximation.
    """
    def __init__(self, config: EAConfig, target_image: Optional[Image.Image] = None):
        self.config = config
        os.makedirs(self.config.output_dir, exist_ok=True)

        # Load reference target image
        if target_image is not None:
            self.target_image = target_image
        else:
            self.target_image = Image.open(self.config.target_image_path)

        self.evaluator = FitnessEvaluator(
            self.target_image,
            self.config.working_width,
            self.config.working_height
        )

        self.population: List[Individual] = []
        self.fitness_vals: List[float] = []
        self.generation: int = 0
        self.best_individual: Optional[Individual] = None
        self.best_fitness: float = -float('inf')
        self.is_running: bool = False
        self.start_time: float = 0.0

        self.initialize_population()

    def initialize_population(self):
        """
        Creates random individuals and evaluates their baseline fitness.
        """
        self.population = [
            Individual(
                self.config.num_polygons,
                self.config.vertices_per_polygon,
                self.config.min_alpha,
                self.config.max_alpha
            )
            for _ in range(self.config.population_size)
        ]
        self.fitness_vals = [self.evaluator.evaluate(ind) for ind in self.population]

        best_idx = max(range(len(self.fitness_vals)), key=lambda i: self.fitness_vals[i])
        self.best_individual = self.population[best_idx].copy()
        self.best_fitness = self.fitness_vals[best_idx]
        self.generation = 0

    def step(self) -> Individual:
        """
        Executes a single generational step:
        Parent Selection -> Mutation/Crossover -> Offspring Evaluation -> Survivor Selection (Elitist).
        """
        self.generation += 1

        # High-Speed (1 + Lambda) or (Mu + Lambda) Elitist Strategy
        if self.config.population_size == 1:
            # High-speed (1+1) Evolution Strategy (classic Roger Alsing approach)
            parent = self.population[0]
            candidate = parent.copy()
            candidate.mutate(
                self.config.mutation_rate,
                self.config.mutation_strength,
                self.config.reorder_prob
            )
            cand_fitness = self.evaluator.evaluate(candidate)

            # Accept if fitness improves or strictly equals
            if cand_fitness >= self.fitness_vals[0]:
                self.population[0] = candidate
                self.fitness_vals[0] = cand_fitness
                self.best_individual = candidate.copy()
                self.best_fitness = cand_fitness
        else:
            # (Mu + Lambda) Population EA
            selection_func = getattr(SelectionSchemes, self.config.selection_scheme, SelectionSchemes.Truncation)
            parents = selection_func(self.population, self.fitness_vals, self.config.num_offspring)

            offspring: List[Individual] = []
            for i in range(len(parents)):
                p1 = parents[i]
                p2 = parents[(i + 1) % len(parents)]
                child = p1.crossover(p2)
                child.mutate(
                    self.config.mutation_rate,
                    self.config.mutation_strength,
                    self.config.reorder_prob
                )
                offspring.append(child)

            offspring_fitness = [self.evaluator.evaluate(child) for child in offspring]

            # Survivor selection: Combine parents + offspring with strict Elitism
            combined_pop = self.population + offspring
            combined_fitness = self.fitness_vals + offspring_fitness

            # Elitist Truncation for survivors to prevent regression
            survivors = SelectionSchemes.Truncation(combined_pop, combined_fitness, self.config.population_size)
            self.population = survivors
            self.fitness_vals = [self.evaluator.evaluate(ind) for ind in self.population]

            best_idx = max(range(len(self.fitness_vals)), key=lambda i: self.fitness_vals[i])
            if self.fitness_vals[best_idx] > self.best_fitness:
                self.best_fitness = self.fitness_vals[best_idx]
                self.best_individual = self.population[best_idx].copy()

        # Periodic snapshot saving
        if self.config.save_interval > 0 and self.generation % self.config.save_interval == 0:
            self.save_checkpoint()

        return self.best_individual

    def save_checkpoint(self, filename: Optional[str] = None):
        """
        Saves current best individual render to output directory.
        """
        if self.best_individual is None:
            return

        if filename is None:
            filename = f'gen_{self.generation:06d}_fit_{self.best_fitness:.2f}.png'

        out_path = os.path.join(self.config.output_dir, filename)
        # Render in higher resolution for export
        w, h = self.target_image.size
        img = self.best_individual.render(w, h)
        img.save(out_path)

    def run(self, callback: Optional[Callable[[int, float, Individual], None]] = None):
        """
        Continuous loop running until max generations reached or target fitness achieved.
        """
        self.is_running = True
        self.start_time = time.time()

        while self.is_running:
            best_ind = self.step()

            if callback:
                callback(self.generation, self.best_fitness, best_ind)

            if self.config.max_generations > 0 and self.generation >= self.config.max_generations:
                break

            if self.best_fitness >= self.config.target_fitness:
                break

        self.is_running = False
        self.save_checkpoint('final_mona_lisa_reconstruction.png')

    def stop(self):
        self.is_running = False

