import numpy as np
from PIL import Image
from polygon import Individual

class FitnessEvaluator:
    """
    Evaluates fitness between individual polygon renders and reference target image using vectorized NumPy MSE.
    """
    def __init__(self, target_image: Image.Image, width: int, height: int):
        self.width = width
        self.height = height

        # Resize reference target to working resolution for lightning-fast evaluations
        resized_target = target_image.convert('RGB').resize((width, height), Image.Resampling.LANCZOS)
        self.target_array = np.array(resized_target, dtype=np.float32)
        self.max_possible_mse = 255.0 ** 2

    def evaluate(self, individual: Individual) -> float:
        """
        Renders the individual and returns similarity percentage (0.0% to 100.0%).
        """
        rendered_img = individual.render(self.width, self.height)
        rendered_array = np.array(rendered_img, dtype=np.float32)

        # Vectorized Mean Squared Error across all pixels and color channels
        diff = self.target_array - rendered_array
        mse = float(np.mean(diff * diff))

        individual.mse_error = mse
        # Similarity score: 100% is pixel-perfect match, 0% is maximum divergence
        similarity = max(0.0, 100.0 * (1.0 - (mse / self.max_possible_mse)))
        individual.fitness = similarity
        return similarity

