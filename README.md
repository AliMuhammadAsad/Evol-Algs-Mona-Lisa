# 🧬 Evolutionary Algorithm: Mona Lisa Polygon Synthesis

An evolutionary optimization framework that reconstructs target images (such as Leonardo da Vinci's *Mona Lisa*) using semi-transparent geometric polygons, inspired by Roger Alsing's genetic programming experiment.

Built as part of exploration in **Computational Intelligence (Evolutionary Algorithms & Genetic Optimization)**.

---

## 🎯 Overview

The challenge is to approximate a complex continuous raster image using a fixed chromosome of discrete semi-transparent polygons ($N \approx 50$ to $100$). Because the search space of combinations of vertices, colors, and layering order is practically infinite, an **Evolutionary Algorithm (EA)** stochastic search is applied to iteratively mutate, recombine, and select superior candidate representations.

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│ Target Image    │ <---> │ Rendered Canvas │ ====> │ Mean Squared    │
│ (Ground Truth)  │  MSE  │ (Candidate DNA) │       │ Error (Fitness) │
└─────────────────┘       └─────────────────┘       └─────────────────┘
```

---

## 🔬 Chromosome Representation & Operators

### 1. The Chromosome (Genotype)
An individual consists of an ordered sequence of $N$ polygons:
$$\text{Individual} = [P_1, P_2, \dots, P_N]$$
Where each polygon $P_i$ contains:
* **Vertices:** A set of $V$ 2D coordinates $[(x_1, y_1), \dots, (x_V, y_V)] \in [0.0, 1.0]^2$.
* **Color:** $(R, G, B, A)$ where $A \in [20, 140]$ (transparency allows subtle optical blending and color layering).

### 2. Fitness Function
Candidates are rendered onto an internal canvas and compared with the target image array using vectorized Mean Squared Error (MSE):
$$\text{MSE} = \frac{1}{3 \times W \times H} \sum_{x,y,c} \left( I_{\text{target}}(x, y, c) - I_{\text{candidate}}(x, y, c) \right)^2$$
$$\text{Similarity (\%)} = 100 \times \left(1.0 - \frac{\text{MSE}}{255^2}\right)$$

### 3. Genetic Operators & Mutations
* **Vertex Jitter:** Perturbs a random vertex $(x, y) \pm \Delta$.
* **Color Drift:** Mutates $R, G, \text{ or } B$ color channels by $\pm \Delta$.
* **Alpha Modulation:** Nudges the transparency channel $A \pm \Delta$.
* **Z-Order Layer Swap:** Swaps the rendering order of two polygons to alter occlusion depth.
* **Uniform Crossover:** Blends polygon genes from two selected parent chromosomes.

---

## 🛠️ Selection Schemes Implemented

1. **Truncation Selection:** Selects the top $K$ individuals with the lowest MSE loss.
2. **Tournament Selection:** Randomly samples $K$ candidates and selects the fittest.
3. **Linear Rank Selection:** Assigns selection probabilities proportional to rank order.
4. **Fitness Proportional (Roulette Wheel):** Selects candidates proportional to normalized fitness.
5. **(1+1) Evolution Strategy (ES):** High-speed single-parent mutation with strict elitism.

---

## 🚀 Quickstart

### 1. Requirements
```bash
pip install -r requirements.txt
```
*(Dependencies: `pillow`, `numpy`, `tkinter`)*

### 2. Launch Interactive Desktop GUI
```bash
python main.py
```
* **Features:**
  * Real-time side-by-side rendering (Reference Target vs. Evolved Polygons).
  * Interactive sliders for Polygon count, Vertices, Mutation Rate, and Population size.
  * Image selector: choose built-in presets (`mona_lisa.jpg`, etc.) or **browse and load any custom image**.
  * Real-time telemetry: Generation count, Similarity %, MSE loss, and Generations/sec.
  * One-click Snapshot exporter to save intermediate renders.

### 3. Headless CLI Mode (High-Throughput)
```bash
# Run 10,000 generations on Mona Lisa with 50 polygons
python main.py --cli --generations 10000 --polygons 50 --image assets/mona_lisa.jpg

# Run on a custom image
python main.py --cli --generations 5000 --polygons 80 --image path/to/your/image.png
```

---

## 📂 Project Architecture

```
Evol-Algs-Mona-Lisa/
├── assets/
│   └── mona_lisa.jpg          # Reference artwork
├── output/                    # Generated snapshots and milestone renders
├── config.py                  # Hyperparameters dataclass
├── polygon.py                 # Polygon & Individual chromosome classes
├── fitness.py                 # Vectorized NumPy MSE fitness evaluator
├── selecSchemes.py            # Selection schemes (Truncation, Tournament, Rank, etc.)
├── evolAlgs.py                # Core Evolutionary Algorithm loop & elitism
├── gui.py                     # Cyberpunk Tkinter desktop application
├── main.py                    # Dual CLI & GUI launcher
├── requirements.txt           # Python dependencies
└── README.md                  # Technical documentation
```

