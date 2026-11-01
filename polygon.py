import random
from typing import List, Tuple
from PIL import Image, ImageDraw

class Polygon:
    """
    Represents a single semi-transparent colored polygon in normalized coordinates [0.0, 1.0].
    """
    def __init__(self, num_vertices: int = 3, min_alpha: int = 20, max_alpha: int = 140):
        self.num_vertices = num_vertices
        self.min_alpha = min_alpha
        self.max_alpha = max_alpha

        # Random normalized vertices [0.0, 1.0]
        self.vertices: List[Tuple[float, float]] = [
            (random.random(), random.random()) for _ in range(num_vertices)
        ]

        # Random RGBA color
        self.color: Tuple[int, int, int, int] = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(min_alpha, max_alpha),
        )

    def copy(self) -> 'Polygon':
        p = Polygon(self.num_vertices, self.min_alpha, self.max_alpha)
        p.vertices = list(self.vertices)
        p.color = tuple(self.color)
        return p

    def mutate(self, strength: float = 0.12):
        """
        Mutates either vertices or color attributes based on random roll.
        """
        mutation_choice = random.random()

        if mutation_choice < 0.60:
            # Mutate a random vertex
            v_idx = random.randint(0, self.num_vertices - 1)
            x, y = self.vertices[v_idx]
            dx = (random.random() * 2.0 - 1.0) * strength
            dy = (random.random() * 2.0 - 1.0) * strength
            new_x = max(0.0, min(1.0, x + dx))
            new_y = max(0.0, min(1.0, y + dy))
            self.vertices[v_idx] = (new_x, new_y)

        elif mutation_choice < 0.90:
            # Mutate color channels (RGB)
            r, g, b, a = self.color
            c_idx = random.randint(0, 2)
            delta = int((random.random() * 2.0 - 1.0) * (255 * strength))
            channels = [r, g, b]
            channels[c_idx] = max(0, min(255, channels[c_idx] + delta))
            self.color = (channels[0], channels[1], channels[2], a)

        else:
            # Mutate Alpha opacity
            r, g, b, a = self.color
            delta_a = int((random.random() * 2.0 - 1.0) * (self.max_alpha - self.min_alpha) * strength)
            new_a = max(self.min_alpha, min(self.max_alpha, a + delta_a))
            self.color = (r, g, b, new_a)


class Individual:
    """
    Represents an individual solution (chromosome) composed of ordered polygons.
    """
    def __init__(self, num_polygons: int = 50, vertices_per_polygon: int = 3, min_alpha: int = 20, max_alpha: int = 140):
        self.num_polygons = num_polygons
        self.vertices_per_polygon = vertices_per_polygon
        self.min_alpha = min_alpha
        self.max_alpha = max_alpha
        self.polygons: List[Polygon] = [
            Polygon(vertices_per_polygon, min_alpha, max_alpha)
            for _ in range(num_polygons)
        ]
        self.fitness: float = -float('inf')  # Higher is better (0..100% similarity)
        self.mse_error: float = float('inf') # Lower is better

    def copy(self) -> 'Individual':
        ind = Individual(self.num_polygons, self.vertices_per_polygon, self.min_alpha, self.max_alpha)
        ind.polygons = [p.copy() for p in self.polygons]
        ind.fitness = self.fitness
        ind.mse_error = self.mse_error
        return ind

    def render(self, width: int, height: int, background: Tuple[int, int, int] = (0, 0, 0)) -> Image.Image:
        """
        Renders all polygons onto an RGBA canvas with alpha blending.
        """
        img = Image.new('RGB', (width, height), background)
        draw = ImageDraw.Draw(img, 'RGBA')

        for poly in self.polygons:
            pts = [(int(x * width), int(y * height)) for x, y in poly.vertices]
            draw.polygon(pts, fill=poly.color)

        return img

    def mutate(self, mutation_rate: float = 0.85, mutation_strength: float = 0.12, reorder_prob: float = 0.08):
        """
        Applies mutation across polygons with potential layer reordering (Z-index shift).
        """
        # Mutate polygons
        for poly in self.polygons:
            if random.random() < mutation_rate / self.num_polygons:
                poly.mutate(mutation_strength)

        # Layer reordering mutation
        if random.random() < reorder_prob and len(self.polygons) >= 2:
            i, j = random.sample(range(len(self.polygons)), 2)
            self.polygons[i], self.polygons[j] = self.polygons[j], self.polygons[i]

    def crossover(self, other: 'Individual') -> 'Individual':
        """
        Uniform crossover between two parent individuals.
        """
        child = self.copy()
        for i in range(self.num_polygons):
            if random.random() < 0.5:
                child.polygons[i] = other.polygons[i].copy()
        return child

