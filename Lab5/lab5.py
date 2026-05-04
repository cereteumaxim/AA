import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib
import matplotlib.pyplot as plt
import networkx as nx
import random
import time
import numpy as np

# Use TkAgg backend for embedding in Tkinter
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# ---------------------
# Graph Generation Utils
# ---------------------
def generate_random_graph(num_nodes, edge_prob, weight_range=(1, 20)):
    """Generate a random undirected weighted graph."""
    G = nx.Graph()
    for i in range(num_nodes):
        G.add_node(i)
    # Add edges with given probability
    for i in range(num_nodes):
        for j in range(i + 1, num_nodes):
            if random.random() < edge_prob:
                weight = random.randint(*weight_range)
                G.add_edge(i, j, weight=weight)
    # Ensure connectivity (if graph is disconnected, add some edges)
    if not nx.is_connected(G):
        components = list(nx.connected_components(G))
        for idx in range(len(components) - 1):
            u = random.choice(list(components[idx]))
            v = random.choice(list(components[idx + 1]))
            weight = random.randint(*weight_range)
            G.add_edge(u, v, weight=weight)
    return G


# ---------------------
# Greedy Algorithms
# ---------------------
def prim_mst(G, callback=None, delay=300):
    """
    Compute MST using Prim's algorithm.
    Calls callback(G, mst_edges, current_edge, step, total_weight) after each step.
    """
    nodes = list(G.nodes)
    if not nodes:
        return []
    mst_edges = []
    visited = set([nodes[0]])
    candidate_edges = []
    step = 0
    total_weight = 0

    for u, v, data in G.edges(nodes[0], data=True):
        candidate_edges.append((data['weight'], nodes[0], v))
    candidate_edges.sort()

    while candidate_edges and len(visited) < len(G.nodes):
        weight, u, v = candidate_edges.pop(0)
        if v in visited:
            continue
        visited.add(v)
        mst_edges.append((u, v, weight))
        total_weight += weight
        step += 1
        if callback:
            callback(G, mst_edges, (u, v, weight), step, total_weight)
            time.sleep(delay / 1000)

        for x, y, data in G.edges(v, data=True):
            if y not in visited:
                candidate_edges.append((data['weight'], v, y))
        candidate_edges.sort()
    return mst_edges


def find(parent, i):
    """Utility function for union-find"""
    if parent[i] != i:
        parent[i] = find(parent, parent[i])
    return parent[i]


def union(parent, rank, x, y):
    """Utility function for union-find"""
    xroot = find(parent, x)
    yroot = find(parent, y)
    if rank[xroot] < rank[yroot]:
        parent[xroot] = yroot
    elif rank[xroot] > rank[yroot]:
        parent[yroot] = xroot
    else:
        parent[yroot] = xroot
        rank[xroot] += 1


def kruskal_mst(G, callback=None, delay=300):
    """
    Compute MST using Kruskal's algorithm.
    Calls callback(G, mst_edges, current_edge, step, total_weight) after each step.
    """
    edges = [(data['weight'], u, v) for u, v, data in G.edges(data=True)]
    edges.sort()
    parent = {node: node for node in G.nodes()}
    rank = {node: 0 for node in G.nodes()}
    mst_edges = []
    step = 0
    total_weight = 0

    for weight, u, v in edges:
        if find(parent, u) != find(parent, v):
            union(parent, rank, u, v)
            mst_edges.append((u, v, weight))
            total_weight += weight
            step += 1
            if callback:
                callback(G, mst_edges, (u, v, weight), step, total_weight)
                time.sleep(delay / 1000)  # simulate delay
    return mst_edges


# ---------------------
# Visualization Utilities
# ---------------------
class GraphVisualizer:
    def __init__(self, canvas_frame):
        self.fig, self.ax = plt.subplots(figsize=(6, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=canvas_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.pos = None
        self.current_layout = 'spring'

    def get_layout(self, G):
        if self.current_layout == 'spring':
            return nx.spring_layout(G, seed=42)
        elif self.current_layout == 'circular':
            return nx.circular_layout(G)
        elif self.current_layout == 'shell':
            return nx.shell_layout(G)
        else:
            return nx.spring_layout(G, seed=42)

    def draw_graph(self, G, mst_edges=None, highlight_edge=None, title="Graph",
                   node_size=500, edge_width=2):
        self.ax.clear()
        self.pos = self.get_layout(G)
        # Draw all nodes and edges
        nx.draw_networkx_nodes(G, self.pos, ax=self.ax, node_color='skyblue', node_size=node_size)
        nx.draw_networkx_labels(G, self.pos, ax=self.ax, font_size=10, font_color='black')
        nx.draw_networkx_edges(G, self.pos, ax=self.ax, edge_color='gray', width=edge_width)
        # Draw edge weights
        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, self.pos, edge_labels=edge_labels, ax=self.ax, font_color='brown')

        # Highlight MST edges if available
        if mst_edges:
            nx.draw_networkx_edges(G, self.pos, edgelist=[(u, v) for u, v, w in mst_edges],
                                   ax=self.ax, edge_color='green', width=edge_width + 1)
        # Highlight current edge if provided
        if highlight_edge:
            u, v, w = highlight_edge
            nx.draw_networkx_edges(G, self.pos, edgelist=[(u, v)],
                                   ax=self.ax, edge_color='red', width=edge_width + 2)
        self.ax.set_title(title, fontsize=14)
        self.ax.axis("off")
        self.canvas.draw()


# ---------------------
# Main Application Class
# ---------------------
class GreedyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Greedy Algorithms Visualizer")
        self.geometry("1200x800")
        self.graph = None
        self.mst_edges = []
        self.visualizer = None

        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        self.create_widgets()

    def create_widgets(self):
        # Top frame for all controls
        controls_frame = ttk.Frame(self)
        controls_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # Graph settings frame
        graph_settings = ttk.Labelframe(controls_frame, text="Graph Settings")
        graph_settings.grid(row=0, column=0, padx=5, pady=5, sticky="nw")

        ttk.Label(graph_settings, text="Number of Nodes:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.nodes_entry = ttk.Entry(graph_settings, width=8)
        self.nodes_entry.grid(row=0, column=1, padx=5, pady=5)
        self.nodes_entry.insert(0, "10")

        ttk.Label(graph_settings, text="Edge Probability (0-1):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.prob_entry = ttk.Entry(graph_settings, width=8)
        self.prob_entry.grid(row=1, column=1, padx=5, pady=5)
        self.prob_entry.insert(0, "0.4")

        ttk.Label(graph_settings, text="Layout:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.layout_combo = ttk.Combobox(graph_settings, values=["spring", "circular", "shell"], state="readonly",
                                         width=10)
        self.layout_combo.grid(row=2, column=1, padx=5, pady=5)
        self.layout_combo.set("spring")

        # Customization settings frame
        custom_settings = ttk.Labelframe(controls_frame, text="Customization")
        custom_settings.grid(row=0, column=1, padx=5, pady=5, sticky="nw")

        ttk.Label(custom_settings, text="Node Size:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.node_size_slider = ttk.Scale(custom_settings, from_=100, to=1000, orient=tk.HORIZONTAL)
        self.node_size_slider.set(500)
        self.node_size_slider.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(custom_settings, text="Edge Width:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.edge_width_slider = ttk.Scale(custom_settings, from_=1, to=5, orient=tk.HORIZONTAL)
        self.edge_width_slider.set(2)
        self.edge_width_slider.grid(row=1, column=1, padx=5, pady=5)

        self.animate_var = tk.BooleanVar(value=True)
        self.animate_check = ttk.Checkbutton(custom_settings, text="Step-by-Step Animation", variable=self.animate_var)
        self.animate_check.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        # Buttons frame for algorithm actions
        actions_frame = ttk.Frame(controls_frame)
        actions_frame.grid(row=0, column=2, padx=5, pady=5, sticky="nw")

        self.generate_btn = ttk.Button(actions_frame, text="Generate Graph", command=self.generate_graph)
        self.generate_btn.grid(row=0, column=0, padx=5, pady=5)

        self.prim_btn = ttk.Button(actions_frame, text="Run Prim's", command=self.run_prim)
        self.prim_btn.grid(row=1, column=0, padx=5, pady=5)

        self.kruskal_btn = ttk.Button(actions_frame, text="Run Kruskal's", command=self.run_kruskal)
        self.kruskal_btn.grid(row=2, column=0, padx=5, pady=5)

        self.performance_btn = ttk.Button(actions_frame, text="Performance Analysis", command=self.run_performance)
        self.performance_btn.grid(row=3, column=0, padx=5, pady=5)

        # Info Panel for detailed algorithm output
        self.info_text = tk.Text(self, height=10, wrap=tk.WORD, font=("Arial", 10))
        self.info_text.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        # Canvas Frame for graph visualization
        canvas_frame = ttk.Frame(self)
        canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.visualizer = GraphVisualizer(canvas_frame)

    def generate_graph(self):
        try:
            num_nodes = int(self.nodes_entry.get())
            edge_prob = float(self.prob_entry.get())
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numeric values.")
            return

        self.visualizer.current_layout = self.layout_combo.get()
        self.graph = generate_random_graph(num_nodes, edge_prob)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END,
                              f"Generated graph with {num_nodes} nodes using {self.visualizer.current_layout} layout.\n")
        node_size = self.node_size_slider.get()
        edge_width = self.edge_width_slider.get()
        self.visualizer.draw_graph(self.graph, title="Generated Graph", node_size=node_size, edge_width=edge_width)

    def run_prim(self):
        if self.graph is None:
            messagebox.showerror("Graph Error", "Generate a graph first!")
            return
        self.info_text.insert(tk.END, "Running Prim's algorithm...\n")
        self.mst_edges = []

        def prim_callback(G, current_mst, current_edge, step, total_weight):
            self.mst_edges = list(current_mst)
            node_size = self.node_size_slider.get()
            edge_width = self.edge_width_slider.get()
            self.visualizer.draw_graph(G, mst_edges=self.mst_edges, highlight_edge=current_edge,
                                       title=f"Prim's Algorithm (Step {step})", node_size=node_size,
                                       edge_width=edge_width)
            self.info_text.insert(tk.END,
                                  f"Step {step}: Added edge {current_edge[0]}-{current_edge[1]} (weight {current_edge[2]}). Total MST weight: {total_weight}\n")
            self.info_text.see(tk.END)
            if self.animate_var.get():
                self.update()

        start_time = time.time()
        prim_mst(self.graph, callback=prim_callback, delay=300 if self.animate_var.get() else 0)
        elapsed = time.time() - start_time
        self.info_text.insert(tk.END, f"Prim's algorithm completed in {elapsed:.3f} seconds.\n")
        node_size = self.node_size_slider.get()
        edge_width = self.edge_width_slider.get()
        self.visualizer.draw_graph(self.graph, mst_edges=self.mst_edges, title="Prim's MST", node_size=node_size,
                                   edge_width=edge_width)

    def run_kruskal(self):
        if self.graph is None:
            messagebox.showerror("Graph Error", "Generate a graph first!")
            return
        self.info_text.insert(tk.END, "Running Kruskal's algorithm...\n")
        self.mst_edges = []

        def kruskal_callback(G, current_mst, current_edge, step, total_weight):
            self.mst_edges = list(current_mst)
            node_size = self.node_size_slider.get()
            edge_width = self.edge_width_slider.get()
            self.visualizer.draw_graph(G, mst_edges=self.mst_edges, highlight_edge=current_edge,
                                       title=f"Kruskal's Algorithm (Step {step})", node_size=node_size,
                                       edge_width=edge_width)
            self.info_text.insert(tk.END,
                                  f"Step {step}: Added edge {current_edge[0]}-{current_edge[1]} (weight {current_edge[2]}). Total MST weight: {total_weight}\n")
            self.info_text.see(tk.END)
            if self.animate_var.get():
                self.update()

        start_time = time.time()
        kruskal_mst(self.graph, callback=kruskal_callback, delay=300 if self.animate_var.get() else 0)
        elapsed = time.time() - start_time
        self.info_text.insert(tk.END, f"Kruskal's algorithm completed in {elapsed:.3f} seconds.\n")
        node_size = self.node_size_slider.get()
        edge_width = self.edge_width_slider.get()
        self.visualizer.draw_graph(self.graph, mst_edges=self.mst_edges, title="Kruskal's MST", node_size=node_size,
                                   edge_width=edge_width)

    def run_performance(self):
        self.info_text.insert(tk.END, "Running performance analysis...\n")
        node_counts = range(10, 101, 10)
        prim_times = []
        kruskal_times = []

        for n in node_counts:
            G = generate_random_graph(n, 0.4)
            # Time Prim's
            start = time.time()
            prim_mst(G, callback=None, delay=0)
            prim_times.append(time.time() - start)
            # Time Kruskal's
            start = time.time()
            kruskal_mst(G, callback=None, delay=0)
            kruskal_times.append(time.time() - start)

        fig, ax = plt.subplots(figsize=(6, 5))
        ax.plot(node_counts, prim_times, marker='o', label="Prim's", color='blue')
        ax.plot(node_counts, kruskal_times, marker='o', label="Kruskal's", color='orange')
        ax.set_title("Performance Analysis", fontsize=14)
        ax.set_xlabel("Number of Nodes", fontsize=12)
        ax.set_ylabel("Execution Time (s)", fontsize=12)
        ax.legend()
        ax.grid(True)
        plt.tight_layout()

        perf_window = tk.Toplevel(self)
        perf_window.title("Performance Analysis")
        canvas = FigureCanvasTkAgg(fig, master=perf_window)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        canvas.draw()
        self.info_text.insert(tk.END, "Performance analysis complete. See new window for graph.\n")


if __name__ == "__main__":
    app = GreedyApp()
    app.mainloop()