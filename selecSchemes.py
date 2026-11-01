import random
from typing import List
from polygon import Individual

class SelectionSchemes:
    """
    Selection schemes for choosing parent chromosomes and survivor populations.
    """

    @staticmethod
    def Truncation(population: List[Individual], fitness_vals: List[float], num_selected: int) -> List[Individual]:
        """
        Selects the top K individuals with the highest fitness scores.
        """
        sorted_pairs = sorted(zip(population, fitness_vals), key=lambda x: x[1], reverse=True)
        return [pair[0].copy() for pair in sorted_pairs[:num_selected]]

    @staticmethod
    def Tournament(population: List[Individual], fitness_vals: List[float], num_selected: int, k: int = 3) -> List[Individual]:
        """
        Tournament selection: picks k individuals at random, selects the best, repeats.
        """
        selected = []
        n = len(population)
        for _ in range(num_selected):
            aspirants_idx = random.sample(range(n), min(k, n))
            best_idx = max(aspirants_idx, key=lambda idx: fitness_vals[idx])
            selected.append(population[best_idx].copy())
        return selected

    @staticmethod
    def Rank(population: List[Individual], fitness_vals: List[float], num_selected: int) -> List[Individual]:
        """
        Linear rank-based selection.
        """
        n = len(population)
        sorted_indices = sorted(range(n), key=lambda i: fitness_vals[i])
        # Rank from 1 (worst) to n (best)
        ranks = [i + 1 for i in range(n)]
        total_rank = sum(ranks)
        probs = [r / total_rank for r in ranks]

        selected_indices = random.choices(sorted_indices, weights=probs, k=num_selected)
        return [population[i].copy() for i in selected_indices]

    @staticmethod
    def FitnessProportional(population: List[Individual], fitness_vals: List[float], num_selected: int) -> List[Individual]:
        """
        Roulette-wheel fitness proportional selection.
        """
        min_fit = min(fitness_vals)
        # Shift fitness so minimum is strictly positive
        offset_fitness = [max(0.001, f - min_fit + 1.0) for f in fitness_vals]
        total = sum(offset_fitness)
        probs = [f / total for f in offset_fitness]

        selected = random.choices(population, weights=probs, k=num_selected)
        return [ind.copy() for ind in selected]

