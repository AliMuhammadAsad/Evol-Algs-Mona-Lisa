import os
import time
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from config import EAConfig
from evolAlgs import EvolutionaryAlgorithm

class MonaLisaEAGUI:
    """
    Cyberpunk-Themed Interactive Desktop GUI for Evolutionary Algorithm Polygon Image Synthesis.
    """
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("NEURAL GENETIC LAB // MONA LISA POLYGON EVOLVER")
        self.root.geometry("1100x720")
        self.root.configure(bg="#05060A")

        # Config and Engine
        self.config = EAConfig()
        self.ea: EvolutionaryAlgorithm = EvolutionaryAlgorithm(self.config)
        self.is_running = False
        self.worker_thread: threading.Thread = None

        # Image references to prevent garbage collection
        self.tk_target = None
        self.tk_evolved = None

        self._build_ui()
        self._load_current_target()
        self._update_render_display()

    def _build_ui(self):
        # Top Cyber Header Bar
        header = tk.Frame(self.root, bg="#0A0E1A", height=45, bd=1, relief="ridge")
        header.pack(fill="x", side="top", padx=8, pady=(8, 0))

        title_lbl = tk.Label(
            header,
            text="🧬 EVOLUTIONARY POLYGON SYNTHESIZER // CS-451 CI",
            fg="#00F0FF",
            bg="#0A0E1A",
            font=("Consolas", 12, "bold")
        )
        title_lbl.pack(side="left", padx=15, pady=8)

        status_lbl = tk.Label(
            header,
            text="STATUS: READY // SYSTEM IDLE",
            fg="#00FFA3",
            bg="#0A0E1A",
            font=("Consolas", 10)
        )
        status_lbl.pack(side="right", padx=15)
        self.status_lbl = status_lbl

        # Main Layout: Left controls (340px) + Right canvas view
        main_pane = tk.Frame(self.root, bg="#05060A")
        main_pane.pack(fill="both", expand=True, padx=8, pady=8)

        # Left Control Panel
        left_ctrl = tk.LabelFrame(
            main_pane,
            text=" [ HYPERPARAMETERS & CONTROLS ] ",
            fg="#00F0FF",
            bg="#0A0E1A",
            font=("Consolas", 10, "bold"),
            padx=12,
            pady=10
        )
        left_ctrl.pack(side="left", fill="y", padx=(0, 8))

        # Target Image Selection
        tk.Label(left_ctrl, text="TARGET IMAGE:", fg="#C084FC", bg="#0A0E1A", font=("Consolas", 9, "bold")).pack(anchor="w")
        btn_browse = tk.Button(
            left_ctrl,
            text="📁 BROWSE CUSTOM IMAGE...",
            command=self._browse_image,
            bg="#1E293B",
            fg="#FFFFFF",
            activebackground="#00F0FF",
            activeforeground="#000000",
            font=("Consolas", 9, "bold"),
            bd=0,
            padx=10,
            pady=5,
            cursor="hand2"
        )
        btn_browse.pack(fill="x", pady=(2, 10))

        # Preset Dropdown
        assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
        self.preset_files = [f for f in os.listdir(assets_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))] if os.path.exists(assets_dir) else []
        self.preset_var = tk.StringVar(value='mona_lisa.jpg' if 'mona_lisa.jpg' in self.preset_files else (self.preset_files[0] if self.preset_files else ''))

        if self.preset_files:
            tk.Label(left_ctrl, text="OR SELECT PRESET:", fg="#94A3B8", bg="#0A0E1A", font=("Consolas", 8)).pack(anchor="w")
            preset_menu = ttk.Combobox(left_ctrl, textvariable=self.preset_var, values=self.preset_files, state="readonly")
            preset_menu.pack(fill="x", pady=(2, 12))
            preset_menu.bind("<<ComboboxSelected>>", self._on_preset_change)

        # Sliders
        # 1. Number of Polygons
        self.slider_polys = self._create_slider(left_ctrl, "POLYGONS COUNT (Genes):", 10, 200, self.config.num_polygons, step=5)
        # 2. Vertices per Polygon
        self.slider_verts = self._create_slider(left_ctrl, "VERTICES / POLYGON:", 3, 6, self.config.vertices_per_polygon, step=1)
        # 3. Mutation Rate
        self.slider_mut_rate = self._create_slider(left_ctrl, "MUTATION RATE (%):", 10, 100, int(self.config.mutation_rate * 100), step=5)
        # 4. Mutation Strength
        self.slider_mut_str = self._create_slider(left_ctrl, "MUTATION STRENGTH (%):", 1, 50, int(self.config.mutation_strength * 100), step=1)
        # 5. Population Size
        self.slider_pop = self._create_slider(left_ctrl, "POPULATION SIZE (Mu):", 1, 20, self.config.population_size, step=1)

        # Selection Scheme
        tk.Label(left_ctrl, text="SELECTION SCHEME:", fg="#C084FC", bg="#0A0E1A", font=("Consolas", 9, "bold")).pack(anchor="w", pady=(4, 0))
        self.scheme_var = tk.StringVar(value=self.config.selection_scheme)
        scheme_menu = ttk.Combobox(left_ctrl, textvariable=self.scheme_var, values=["Truncation", "Tournament", "Rank", "FitnessProportional"], state="readonly")
        scheme_menu.pack(fill="x", pady=(2, 12))

        # Control Buttons
        btn_frame = tk.Frame(left_ctrl, bg="#0A0E1A")
        btn_frame.pack(fill="x", pady=8)

        self.btn_start = tk.Button(
            btn_frame,
            text="▶ START EVOLUTION",
            command=self._toggle_run,
            bg="#00F0FF",
            fg="#000000",
            activebackground="#FFFFFF",
            font=("Consolas", 10, "bold"),
            bd=0,
            pady=8,
            cursor="hand2"
        )
        self.btn_start.pack(fill="x", pady=3)

        self.btn_reset = tk.Button(
            btn_frame,
            text="↺ RESET CHROMOSOMES",
            command=self._reset_ea,
            bg="#334155",
            fg="#FFFFFF",
            activebackground="#E2E8F0",
            font=("Consolas", 9),
            bd=0,
            pady=5,
            cursor="hand2"
        )
        self.btn_reset.pack(fill="x", pady=3)

        btn_save = tk.Button(
            btn_frame,
            text="💾 SAVE SNAPSHOT (PNG)",
            command=self._save_snapshot,
            bg="#1E293B",
            fg="#00FFA3",
            font=("Consolas", 9),
            bd=0,
            pady=5,
            cursor="hand2"
        )
        btn_save.pack(fill="x", pady=3)

        # Right Side: Visualizer Canvas & Live Telemetry
        right_disp = tk.Frame(main_pane, bg="#0A0E1A", bd=1, relief="ridge")
        right_disp.pack(side="right", fill="both", expand=True)

        # Telemetry Stats Dashboard
        telemetry = tk.Frame(right_disp, bg="#05060A", height=60)
        telemetry.pack(fill="x", side="top", padx=10, pady=10)

        self.lbl_gen = self._create_stat_box(telemetry, "GENERATION", "00000", "#00F0FF", side="left")
        self.lbl_fit = self._create_stat_box(telemetry, "SIMILARITY", "00.00%", "#00FFA3", side="left")
        self.lbl_mse = self._create_stat_box(telemetry, "MSE LOSS", "0000.0", "#C084FC", side="left")
        self.lbl_speed = self._create_stat_box(telemetry, "SPEED", "0.0 GEN/S", "#F59E0B", side="left")
        self.lbl_time = self._create_stat_box(telemetry, "TIME", "00:00:00", "#38BDF8", side="right")

        # Side-by-Side Image Displays
        canvas_frame = tk.Frame(right_disp, bg="#0A0E1A")
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Target Image Panel
        target_box = tk.LabelFrame(canvas_frame, text=" [ REFERENCE TARGET ] ", fg="#94A3B8", bg="#05060A", font=("Consolas", 9))
        target_box.pack(side="left", fill="both", expand=True, padx=(0, 5))
        self.target_canvas = tk.Label(target_box, bg="#05060A")
        self.target_canvas.pack(fill="both", expand=True, padx=4, pady=4)

        # Evolving Polygon Canvas
        evolved_box = tk.LabelFrame(canvas_frame, text=" [ EVOLVED POLYGONS ] ", fg="#00F0FF", bg="#05060A", font=("Consolas", 9, "bold"))
        evolved_box.pack(side="right", fill="both", expand=True, padx=(5, 0))
        self.evolved_canvas = tk.Label(evolved_box, bg="#05060A")
        self.evolved_canvas.pack(fill="both", expand=True, padx=4, pady=4)

    def _create_slider(self, parent, label, min_val, max_val, init_val, step=1):
        tk.Label(parent, text=label, fg="#94A3B8", bg="#0A0E1A", font=("Consolas", 8, "bold")).pack(anchor="w", pady=(2, 0))
        var = tk.IntVar(value=init_val) if isinstance(init_val, int) else tk.DoubleVar(value=init_val)
        slider = tk.Scale(
            parent,
            from_=min_val,
            to=max_val,
            resolution=step,
            orient="horizontal",
            variable=var,
            bg="#0A0E1A",
            fg="#FFFFFF",
            highlightthickness=0,
            troughcolor="#1E293B",
            activebackground="#00F0FF",
            font=("Consolas", 7)
        )
        slider.pack(fill="x", pady=(0, 4))
        return var

    def _create_stat_box(self, parent, title, init_val, color, side="left"):
        frame = tk.Frame(parent, bg="#0A0E1A", padx=10, pady=4, bd=1, relief="ridge")
        frame.pack(side=side, padx=4)
        tk.Label(frame, text=title, fg="#64748B", bg="#0A0E1A", font=("Consolas", 7, "bold")).pack(anchor="w")
        lbl = tk.Label(frame, text=init_val, fg=color, bg="#0A0E1A", font=("Consolas", 12, "bold"))
        lbl.pack(anchor="w")
        return lbl

    def _load_current_target(self):
        try:
            img = Image.open(self.config.target_image_path).convert('RGB')
            # Thumbnail for UI preview
            thumb = img.copy()
            thumb.thumbnail((320, 440))
            self.tk_target = ImageTk.PhotoImage(thumb)
            self.target_canvas.configure(image=self.tk_target)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")

    def _update_render_display(self):
        if self.ea.best_individual:
            w, h = self.config.working_width * 2, self.config.working_height * 2
            rendered = self.ea.best_individual.render(w, h)
            rendered.thumbnail((320, 440))
            self.tk_evolved = ImageTk.PhotoImage(rendered)
            self.evolved_canvas.configure(image=self.tk_evolved)

    def _browse_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Reference Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.webp")]
        )
        if file_path:
            self.config.target_image_path = file_path
            self._reset_ea()
            self._load_current_target()

    def _on_preset_change(self, event=None):
        filename = self.preset_var.get()
        if filename:
            path = os.path.join(os.path.dirname(__file__), 'assets', filename)
            if os.path.exists(path):
                self.config.target_image_path = path
                self._reset_ea()
                self._load_current_target()

    def _apply_ui_config(self):
        self.config.num_polygons = self.slider_polys.get()
        self.config.vertices_per_polygon = self.slider_verts.get()
        self.config.mutation_rate = self.slider_mut_rate.get() / 100.0
        self.config.mutation_strength = self.slider_mut_str.get() / 100.0
        self.config.population_size = self.slider_pop.get()
        self.config.selection_scheme = self.scheme_var.get()

    def _reset_ea(self):
        was_running = self.is_running
        self.is_running = False
        self._apply_ui_config()
        self.ea = EvolutionaryAlgorithm(self.config)
        self.status_lbl.configure(text="STATUS: RESET // GENERATION 0", fg="#00F0FF")
        self.lbl_gen.configure(text="00000")
        self.lbl_fit.configure(text=f"{self.ea.best_fitness:.2f}%")
        self.lbl_mse.configure(text=f"{self.ea.best_individual.mse_error:.1f}")
        self._update_render_display()
        if was_running:
            self.btn_start.configure(text="▶ START EVOLUTION", bg="#00F0FF")

    def _toggle_run(self):
        if not self.is_running:
            self.is_running = True
            self.btn_start.configure(text="⏸ PAUSE EVOLUTION", bg="#F59E0B")
            self.status_lbl.configure(text="STATUS: EVOLVING // RECOMBINING DNA", fg="#00FFA3")
            self._apply_ui_config()
            self.ea.is_running = True
            self.ea.start_time = time.time()
            self.worker_thread = threading.Thread(target=self._run_loop, daemon=True)
            self.worker_thread.start()
        else:
            self.is_running = False
            self.ea.stop()
            self.btn_start.configure(text="▶ RESUME EVOLUTION", bg="#00F0FF")
            self.status_lbl.configure(text="STATUS: PAUSED", fg="#F59E0B")

    def _run_loop(self):
        start_t = time.time()
        start_gen = self.ea.generation
        last_ui_update = time.time()

        while self.is_running and self.ea.is_running:
            # Step generation
            self._apply_ui_config()
            self.ea.step()

            # Throttle UI redraw to ~25 FPS to keep GUI silky smooth and maximize computation throughput
            now = time.time()
            if now - last_ui_update >= 0.04:
                elapsed = now - start_t
                gen_diff = self.ea.generation - start_gen
                speed = gen_diff / max(0.001, elapsed)

                mins, secs = divmod(int(elapsed), 60)
                hrs, mins = divmod(mins, 60)
                time_str = f"{hrs:02d}:{mins:02d}:{secs:02d}"

                gen = self.ea.generation
                fit = self.ea.best_fitness
                mse = self.ea.best_individual.mse_error if self.ea.best_individual else 0.0

                self.root.after(0, self._sync_ui_telemetry, gen, fit, mse, speed, time_str)
                last_ui_update = now

    def _sync_ui_telemetry(self, gen, fit, mse, speed, time_str):
        self.lbl_gen.configure(text=f"{gen:05d}")
        self.lbl_fit.configure(text=f"{fit:.2f}%")
        self.lbl_mse.configure(text=f"{mse:.1f}")
        self.lbl_speed.configure(text=f"{speed:.1f} G/S")
        self.lbl_time.configure(text=time_str)
        self._update_render_display()

    def _save_snapshot(self):
        if self.ea.best_individual:
            self.ea.save_checkpoint()
            messagebox.showinfo("Saved", f"Snapshot saved to:\n{self.config.output_dir}")

def run_app():
    root = tk.Tk()
    app = MonaLisaEAGUI(root)
    root.mainloop()

if __name__ == '__main__':
    run_app()

