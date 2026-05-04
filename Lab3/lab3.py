import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import time
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
from collections import deque
import timeit
import numpy as np
import csv
from datetime import datetime
import os


class GraphSearchVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Graph Search Visualization - DFS & BFS")
        self.root.geometry("1200x800")

        # Graph variables
        self.graph = {}  # Adjacency list representation
        self.nodes = []
        self.edges = []
        self.visited = []
        self.path = []
        self.animation_speed = 0.5  # seconds
        self.animation_running = False
        self.start_node = None
        self.target_node = None

        # Performance metrics
        self.metrics = {
            "dfs": {"time": 0, "nodes_visited": 0, "path_length": 0, "space": 0},
            "bfs": {"time": 0, "nodes_visited": 0, "path_length": 0, "space": 0}
        }

        # Default parameters
        self.default_random_nodes = 10
        self.default_random_edges = 15
        self.default_grid_rows = 4
        self.default_grid_cols = 4
        self.default_tree_depth = 3
        self.default_tree_branching = 2

        # Statistics collection
        self.all_metrics = []

        self.create_widgets()
        self.create_sample_graph()

    def create_widgets(self):
        # Main frame layout with notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tab 1: Visualization
        self.viz_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.viz_tab, text="Visualization")

        # Tab 2: Batch Comparison
        self.batch_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.batch_tab, text="Batch Comparison")

        self.setup_visualization_tab()
        self.setup_batch_comparison_tab()

    def setup_visualization_tab(self):
        main_frame = ttk.Frame(self.viz_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left panel for controls
        control_frame = ttk.LabelFrame(main_frame, text="Controls")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        # Graph generation
        graph_frame = ttk.LabelFrame(control_frame, text="Graph Generation")
        graph_frame.pack(fill=tk.X, padx=5, pady=5)

        # Random graph controls
        ttk.Label(graph_frame, text="Random Graph:").pack(anchor=tk.W, padx=5, pady=2)

        random_params_frame = ttk.Frame(graph_frame)
        random_params_frame.pack(fill=tk.X, padx=5, pady=2)

        ttk.Label(random_params_frame, text="Nodes:").pack(side=tk.LEFT, padx=2)
        self.random_nodes_var = tk.StringVar(value=str(self.default_random_nodes))
        random_nodes_entry = ttk.Entry(random_params_frame, width=5, textvariable=self.random_nodes_var)
        random_nodes_entry.pack(side=tk.LEFT, padx=2)

        ttk.Label(random_params_frame, text="Edges:").pack(side=tk.LEFT, padx=2)
        self.random_edges_var = tk.StringVar(value=str(self.default_random_edges))
        random_edges_entry = ttk.Entry(random_params_frame, width=5, textvariable=self.random_edges_var)
        random_edges_entry.pack(side=tk.LEFT, padx=2)

        ttk.Button(graph_frame, text="Generate Random Graph",
                   command=lambda: self.create_random_graph(int(self.random_nodes_var.get()),
                                                            int(self.random_edges_var.get()))).pack(fill=tk.X, padx=5,
                                                                                                    pady=2)

        # Grid graph controls
        ttk.Label(graph_frame, text="Grid Graph:").pack(anchor=tk.W, padx=5, pady=2)

        grid_params_frame = ttk.Frame(graph_frame)
        grid_params_frame.pack(fill=tk.X, padx=5, pady=2)

        ttk.Label(grid_params_frame, text="Rows:").pack(side=tk.LEFT, padx=2)
        self.grid_rows_var = tk.StringVar(value=str(self.default_grid_rows))
        grid_rows_entry = ttk.Entry(grid_params_frame, width=5, textvariable=self.grid_rows_var)
        grid_rows_entry.pack(side=tk.LEFT, padx=2)

        ttk.Label(grid_params_frame, text="Cols:").pack(side=tk.LEFT, padx=2)
        self.grid_cols_var = tk.StringVar(value=str(self.default_grid_cols))
        grid_cols_entry = ttk.Entry(grid_params_frame, width=5, textvariable=self.grid_cols_var)
        grid_cols_entry.pack(side=tk.LEFT, padx=2)

        ttk.Button(graph_frame, text="Generate Grid Graph",
                   command=lambda: self.create_grid_graph(int(self.grid_rows_var.get()),
                                                          int(self.grid_cols_var.get()))).pack(fill=tk.X, padx=5,
                                                                                               pady=2)

        # Tree graph controls
        ttk.Label(graph_frame, text="Tree Graph:").pack(anchor=tk.W, padx=5, pady=2)

        tree_params_frame = ttk.Frame(graph_frame)
        tree_params_frame.pack(fill=tk.X, padx=5, pady=2)

        ttk.Label(tree_params_frame, text="Depth:").pack(side=tk.LEFT, padx=2)
        self.tree_depth_var = tk.StringVar(value=str(self.default_tree_depth))
        tree_depth_entry = ttk.Entry(tree_params_frame, width=5, textvariable=self.tree_depth_var)
        tree_depth_entry.pack(side=tk.LEFT, padx=2)

        ttk.Label(tree_params_frame, text="Branching:").pack(side=tk.LEFT, padx=2)
        self.tree_branching_var = tk.StringVar(value=str(self.default_tree_branching))
        tree_branching_entry = ttk.Entry(tree_params_frame, width=5, textvariable=self.tree_branching_var)
        tree_branching_entry.pack(side=tk.LEFT, padx=2)

        ttk.Button(graph_frame, text="Generate Tree Graph",
                   command=lambda: self.create_tree_graph(int(self.tree_depth_var.get()),
                                                          int(self.tree_branching_var.get()))).pack(fill=tk.X, padx=5,
                                                                                                    pady=2)

        # Algorithm controls
        algo_frame = ttk.LabelFrame(control_frame, text="Algorithms")
        algo_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(algo_frame, text="Run DFS", command=lambda: self.run_search("dfs")).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(algo_frame, text="Run BFS", command=lambda: self.run_search("bfs")).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(algo_frame, text="Compare Algorithms", command=self.compare_algorithms).pack(fill=tk.X, padx=5,
                                                                                                pady=2)

        # Animation control
        anim_frame = ttk.LabelFrame(control_frame, text="Animation")
        anim_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(anim_frame, text="Speed:").pack(anchor=tk.W, padx=5)
        self.speed_scale = ttk.Scale(anim_frame, from_=0.1, to=2.0, orient=tk.HORIZONTAL,
                                     command=self.update_speed)
        self.speed_scale.set(0.5)
        self.speed_scale.pack(fill=tk.X, padx=5, pady=2)

        ttk.Button(anim_frame, text="Reset Visualization", command=self.reset_visualization).pack(fill=tk.X, padx=5,
                                                                                                  pady=5)

        # Node selection
        node_frame = ttk.LabelFrame(control_frame, text="Node Selection")
        node_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(node_frame, text="Set Start Node", command=lambda: self.set_node("start")).pack(fill=tk.X, padx=5,
                                                                                                   pady=2)
        ttk.Button(node_frame, text="Set Target Node", command=lambda: self.set_node("target")).pack(fill=tk.X, padx=5,
                                                                                                     pady=2)

        # Results section
        self.results_frame = ttk.LabelFrame(control_frame, text="Results")
        self.results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.results_text = tk.Text(self.results_frame, height=10, width=30)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Export Results
        ttk.Button(control_frame, text="Export Results to CSV", command=self.export_results).pack(fill=tk.X, padx=5,
                                                                                                  pady=5)

        # Right panel for visualization
        viz_frame = ttk.LabelFrame(main_frame, text="Visualization")
        viz_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Matplotlib figure for graph visualization
        self.fig = plt.Figure(figsize=(6, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.fig, master=viz_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Chart frame for metrics comparison
        self.chart_frame = ttk.LabelFrame(main_frame, text="Performance Metrics")
        self.chart_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        self.metric_fig = plt.Figure(figsize=(10, 3), dpi=100)
        self.metric_ax = self.metric_fig.add_subplot(111)
        self.metric_canvas = FigureCanvasTkAgg(self.metric_fig, master=self.chart_frame)
        self.metric_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def setup_batch_comparison_tab(self):
        # Batch comparison tab
        batch_main_frame = ttk.Frame(self.batch_tab)
        batch_main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Control panel
        batch_control_frame = ttk.LabelFrame(batch_main_frame, text="Batch Comparison Settings")
        batch_control_frame.pack(fill=tk.X, padx=5, pady=5)

        # Graph type selection
        graph_type_frame = ttk.Frame(batch_control_frame)
        graph_type_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(graph_type_frame, text="Graph Type:").pack(side=tk.LEFT, padx=5)
        self.graph_type_var = tk.StringVar(value="random")
        ttk.Radiobutton(graph_type_frame, text="Random", variable=self.graph_type_var, value="random").pack(
            side=tk.LEFT, padx=5)
        ttk.Radiobutton(graph_type_frame, text="Grid", variable=self.graph_type_var, value="grid").pack(side=tk.LEFT,
                                                                                                        padx=5)
        ttk.Radiobutton(graph_type_frame, text="Tree", variable=self.graph_type_var, value="tree").pack(side=tk.LEFT,
                                                                                                        padx=5)

        # Graph size parameters
        size_frame = ttk.LabelFrame(batch_control_frame, text="Graph Size Range")
        size_frame.pack(fill=tk.X, padx=5, pady=5)

        # Size range controls
        size_params_frame = ttk.Frame(size_frame)
        size_params_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(size_params_frame, text="Min Size:").pack(side=tk.LEFT, padx=5)
        self.min_size_var = tk.StringVar(value="10")
        ttk.Entry(size_params_frame, width=5, textvariable=self.min_size_var).pack(side=tk.LEFT, padx=2)

        ttk.Label(size_params_frame, text="Max Size:").pack(side=tk.LEFT, padx=5)
        self.max_size_var = tk.StringVar(value="100")
        ttk.Entry(size_params_frame, width=5, textvariable=self.max_size_var).pack(side=tk.LEFT, padx=2)

        ttk.Label(size_params_frame, text="Step:").pack(side=tk.LEFT, padx=5)
        self.step_size_var = tk.StringVar(value="10")
        ttk.Entry(size_params_frame, width=5, textvariable=self.step_size_var).pack(side=tk.LEFT, padx=2)

        ttk.Label(size_params_frame, text="Iterations per size:").pack(side=tk.LEFT, padx=5)
        self.iterations_var = tk.StringVar(value="3")
        ttk.Entry(size_params_frame, width=5, textvariable=self.iterations_var).pack(side=tk.LEFT, padx=2)

        # Specific parameter frame (changes based on graph type)
        self.specific_params_frame = ttk.LabelFrame(batch_control_frame, text="Graph Type Specific Parameters")
        self.specific_params_frame.pack(fill=tk.X, padx=5, pady=5)

        # Default is random graph parameters
        self.setup_random_graph_params()

        # Add callback for graph type change
        self.graph_type_var.trace_add("write", self.update_specific_params)

        # Run batch tests button
        ttk.Button(batch_control_frame, text="Run Batch Comparison", command=self.run_batch_comparison).pack(fill=tk.X,
                                                                                                             padx=5,
                                                                                                             pady=10)

        # Results visualization
        batch_viz_frame = ttk.LabelFrame(batch_main_frame, text="Batch Comparison Results")
        batch_viz_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Add notebook for different result charts
        self.results_notebook = ttk.Notebook(batch_viz_frame)
        self.results_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tab for time comparison
        self.time_tab = ttk.Frame(self.results_notebook)
        self.results_notebook.add(self.time_tab, text="Execution Time")

        # Tab for nodes visited comparison
        self.nodes_tab = ttk.Frame(self.results_notebook)
        self.results_notebook.add(self.nodes_tab, text="Nodes Visited")

        # Tab for path length comparison
        self.path_tab = ttk.Frame(self.results_notebook)
        self.results_notebook.add(self.path_tab, text="Path Length")

        # Tab for space complexity comparison
        self.space_tab = ttk.Frame(self.results_notebook)
        self.results_notebook.add(self.space_tab, text="Space Usage")

        # Create figures for each tab
        self.setup_comparison_charts()

        # Export button for batch results
        ttk.Button(batch_main_frame, text="Export Batch Results to CSV",
                   command=self.export_batch_results).pack(fill=tk.X, padx=5, pady=5)

    def setup_random_graph_params(self):
        # Clear frame
        for widget in self.specific_params_frame.winfo_children():
            widget.destroy()

        # Edge factor control (edges = nodes * factor)
        ttk.Label(self.specific_params_frame, text="Edge Factor (edges = nodes * factor):").pack(anchor=tk.W, padx=5,
                                                                                                 pady=2)
        self.edge_factor_var = tk.StringVar(value="1.5")
        ttk.Entry(self.specific_params_frame, width=5, textvariable=self.edge_factor_var).pack(anchor=tk.W, padx=5,
                                                                                               pady=2)

        ttk.Label(self.specific_params_frame,
                  text="Note: For 'Size' in random graphs, we use the number of nodes.").pack(anchor=tk.W, padx=5,
                                                                                              pady=5)

    def setup_grid_graph_params(self):
        # Clear frame
        for widget in self.specific_params_frame.winfo_children():
            widget.destroy()

        ttk.Label(self.specific_params_frame,
                  text="Note: For 'Size' in grid graphs, we use N for an NxN grid.").pack(anchor=tk.W, padx=5, pady=5)

    def setup_tree_graph_params(self):
        # Clear frame
        for widget in self.specific_params_frame.winfo_children():
            widget.destroy()

        # Branching factor control
        ttk.Label(self.specific_params_frame, text="Branching Factor:").pack(anchor=tk.W, padx=5, pady=2)
        self.branching_factor_var = tk.StringVar(value="2")
        ttk.Entry(self.specific_params_frame, width=5, textvariable=self.branching_factor_var).pack(anchor=tk.W, padx=5,
                                                                                                    pady=2)

        ttk.Label(self.specific_params_frame,
                  text="Note: For 'Size' in tree graphs, we use the depth of the tree.").pack(anchor=tk.W, padx=5,
                                                                                              pady=5)

    def update_specific_params(self, *args):
        graph_type = self.graph_type_var.get()
        if graph_type == "random":
            self.setup_random_graph_params()
        elif graph_type == "grid":
            self.setup_grid_graph_params()
        elif graph_type == "tree":
            self.setup_tree_graph_params()

    def setup_comparison_charts(self):
        # Time comparison chart
        self.time_fig = plt.Figure(figsize=(8, 6), dpi=100)
        self.time_ax = self.time_fig.add_subplot(111)
        self.time_canvas = FigureCanvasTkAgg(self.time_fig, master=self.time_tab)
        self.time_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Nodes visited chart
        self.nodes_fig = plt.Figure(figsize=(8, 6), dpi=100)
        self.nodes_ax = self.nodes_fig.add_subplot(111)
        self.nodes_canvas = FigureCanvasTkAgg(self.nodes_fig, master=self.nodes_tab)
        self.nodes_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Path length chart
        self.path_fig = plt.Figure(figsize=(8, 6), dpi=100)
        self.path_ax = self.path_fig.add_subplot(111)
        self.path_canvas = FigureCanvasTkAgg(self.path_fig, master=self.path_tab)
        self.path_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Space usage chart
        self.space_fig = plt.Figure(figsize=(8, 6), dpi=100)
        self.space_ax = self.space_fig.add_subplot(111)
        self.space_canvas = FigureCanvasTkAgg(self.space_fig, master=self.space_tab)
        self.space_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update_speed(self, val):
        self.animation_speed = float(val)

    def create_sample_graph(self):
        # Default graph is a small random graph
        self.create_random_graph(self.default_random_nodes, self.default_random_edges)

    def create_random_graph(self, num_nodes=None, num_edges=None):
        if num_nodes is None:
            num_nodes = int(self.random_nodes_var.get())
        if num_edges is None:
            num_edges = int(self.random_edges_var.get())

        self.nodes = list(range(1, num_nodes + 1))
        self.graph = {node: [] for node in self.nodes}

        # First ensure the graph is connected
        shuffled_nodes = self.nodes.copy()
        random.shuffle(shuffled_nodes)

        for i in range(len(shuffled_nodes) - 1):
            n1, n2 = shuffled_nodes[i], shuffled_nodes[i + 1]
            self.graph[n1].append(n2)
            self.graph[n2].append(n1)

        # Add remaining random edges
        edges_to_add = num_edges - (num_nodes - 1)
        potential_edges = [(i, j) for i in self.nodes for j in self.nodes if i < j and j not in self.graph[i]]

        if potential_edges and edges_to_add > 0:
            selected_edges = random.sample(potential_edges, min(edges_to_add, len(potential_edges)))
            for n1, n2 in selected_edges:
                self.graph[n1].append(n2)
                self.graph[n2].append(n1)

        self.reset_visualization()
        self.draw_graph()
        self.update_results(
            "Created random graph with {} nodes and approximately {} edges".format(num_nodes, num_edges))

    def create_grid_graph(self, rows=None, cols=None):
        if rows is None:
            rows = int(self.grid_rows_var.get())
        if cols is None:
            cols = int(self.grid_cols_var.get())

        # Create a grid-like graph
        self.nodes = [(r, c) for r in range(rows) for c in range(cols)]
        self.graph = {node: [] for node in self.nodes}

        # Connect to adjacent nodes (up, down, left, right)
        for r, c in self.nodes:
            if r > 0:
                self.graph[(r, c)].append((r - 1, c))  # Up
            if r < rows - 1:
                self.graph[(r, c)].append((r + 1, c))  # Down
            if c > 0:
                self.graph[(r, c)].append((r, c - 1))  # Left
            if c < cols - 1:
                self.graph[(r, c)].append((r, c + 1))  # Right

        self.reset_visualization()
        self.draw_graph()
        self.update_results(f"Created grid graph with {rows}x{cols} nodes")

    def create_tree_graph(self, depth=None, branching=None):
        if depth is None:
            depth = int(self.tree_depth_var.get())
        if branching is None:
            branching = int(self.tree_branching_var.get())

        # Create a tree graph with specified depth and branching factor
        if depth <= 0 or branching <= 0:
            return

        self.nodes = []
        self.graph = {}

        # Breadth-first generation of the tree
        node_count = 1
        queue = [1]  # Start with root node
        self.nodes.append(1)
        self.graph[1] = []

        current_depth = 0
        nodes_at_current_depth = 1
        nodes_processed = 0

        while queue and current_depth < depth:
            parent = queue.pop(0)
            nodes_processed += 1

            # Add children
            for _ in range(branching):
                node_count += 1
                child = node_count
                self.nodes.append(child)
                self.graph[child] = [parent]  # Child connected to parent
                self.graph[parent].append(child)  # Parent connected to child
                queue.append(child)

            # Check if we need to increment depth
            if nodes_processed == nodes_at_current_depth:
                current_depth += 1
                nodes_at_current_depth = len(queue)
                nodes_processed = 0

        self.reset_visualization()
        self.draw_graph()
        self.update_results(f"Created tree graph with depth {depth} and branching factor {branching}")

    def draw_graph(self):
        self.ax.clear()

        # Create networkx graph
        G = nx.Graph()

        # Add nodes
        for node in self.nodes:
            G.add_node(node)

        # Add edges
        for node, neighbors in self.graph.items():
            for neighbor in neighbors:
                G.add_edge(node, neighbor)

        # Set node colors
        node_colors = []
        for node in G.nodes():
            if node == self.start_node:
                node_colors.append('green')
            elif node == self.target_node:
                node_colors.append('red')
            elif node in self.visited:
                node_colors.append('lightblue')
            else:
                node_colors.append('gray')

        # Set edge colors
        edge_colors = []
        for u, v in G.edges():
            # Check if both nodes are in the path and are consecutive
            if (self.path and u in self.path and v in self.path):
                try:
                    u_index = self.path.index(u)
                    v_index = self.path.index(v)
                    # Check if nodes are adjacent in the path
                    if abs(u_index - v_index) == 1:
                        edge_colors.append('red')
                    else:
                        edge_colors.append('black')
                except ValueError:  # If node not in path
                    edge_colors.append('black')
            else:
                edge_colors.append('black')

        # Choose appropriate layout based on graph type
        if isinstance(list(self.nodes)[0], tuple):  # Grid graph
            # Create position dictionary for grid
            pos = {(r, c): (c, -r) for r, c in self.nodes}  # Flip y-axis for visual clarity
        else:
            # For random and tree graphs
            pos = nx.spring_layout(G, seed=42)  # Consistent layout

        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=500, ax=self.ax)
        nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=1.5, ax=self.ax)
        nx.draw_networkx_labels(G, pos, font_size=10, font_family="sans-serif", ax=self.ax)

        self.ax.set_axis_off()
        self.canvas.draw()

    def update_results(self, text):
        self.results_text.insert(tk.END, text + "\n")
        self.results_text.see(tk.END)

    def set_node(self, node_type):
        try:
            if self.nodes:
                if isinstance(self.nodes[0], tuple):
                    node_names = [f"({n[0]},{n[1]})" for n in self.nodes]
                else:
                    node_names = [str(n) for n in self.nodes]

                selected = simpledialog.askstring("Select Node",
                                                  f"Available nodes: {', '.join(node_names)}\nEnter node:")

                if selected:
                    if "," in selected and "(" in selected:
                        # Handle tuple input format (r,c)
                        try:
                            r, c = map(int, selected.strip("()").split(","))
                            selected_node = (r, c)
                        except:
                            messagebox.showerror("Error", "Invalid node format")
                            return
                    else:
                        try:
                            selected_node = int(selected)
                        except:
                            messagebox.showerror("Error", "Invalid node")
                            return

                    if selected_node in self.nodes:
                        if node_type == "start":
                            self.start_node = selected_node
                            self.update_results(f"Start node set to {selected_node}")
                        else:
                            self.target_node = selected_node
                            self.update_results(f"Target node set to {selected_node}")
                        self.draw_graph()
                    else:
                        messagebox.showerror("Error", "Node not found in graph")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def reset_visualization(self):
        self.visited = []
        self.path = []
        self.draw_graph()

    def run_search(self, algorithm):
        if self.start_node is None:
            messagebox.showinfo("Info", "Please set a start node first.")
            return

        self.reset_visualization()
        self.update_results(f"Running {algorithm.upper()}...")

        if algorithm == "dfs":
            self.run_dfs()
        elif algorithm == "bfs":
            self.run_bfs()

    def run_dfs(self):
        if not self.graph or self.start_node is None:
            return

        self.animation_running = True
        self.visited = []
        self.path = []

        # Track performance metrics
        start_time = timeit.default_timer()
        max_stack_size = 0

        # Handle path finding if target is specified
        if self.target_node:
            stack = [(self.start_node, [self.start_node])]  # (node, path_so_far)
            visited_set = set()  # For O(1) lookup

            while stack and self.animation_running:
                current, path = stack.pop()

                # Track max stack size
                max_stack_size = max(max_stack_size, len(stack))

                if current not in visited_set:
                    visited_set.add(current)
                    self.visited.append(current)

                    # Update visualization
                    self.draw_graph()
                    self.root.update()
                    time.sleep(self.animation_speed)

                    # Check if target found
                    if current == self.target_node:
                        self.path = path
                        self.draw_graph()
                        break

                    # Add neighbors in reverse order (to process in original order when popping)
                    neighbors = sorted(self.graph[current], reverse=True)
                    for neighbor in neighbors:
                        if neighbor not in visited_set:
                            stack.append((neighbor, path + [neighbor]))
        else:
            # Regular DFS without path tracking
            stack = [self.start_node]
            visited_set = set()

            while stack and self.animation_running:
                current = stack.pop()

                # Track max stack size
                max_stack_size = max(max_stack_size, len(stack))

                if current not in visited_set:
                    visited_set.add(current)
                    self.visited.append(current)

                    # Update visualization
                    self.draw_graph()
                    self.root.update()
                    time.sleep(self.animation_speed)

                    # Add neighbors
                    neighbors = sorted(self.graph[current], reverse=True)
                    for neighbor in neighbors:
                        if neighbor not in visited_set:
                            stack.append(neighbor)

        # Calculate metrics
        end_time = timeit.default_timer()
        self.metrics["dfs"]["time"] = end_time - start_time
        self.metrics["dfs"]["nodes_visited"] = len(self.visited)
        self.metrics["dfs"]["path_length"] = len(self.path) - 1 if self.path else 0
        self.metrics["dfs"]["space"] = max_stack_size

        self.animation_running = False
        self.update_results(f"DFS completed. Nodes visited: {len(self.visited)}")
        self.update_results(f"Time: {self.metrics['dfs']['time']:.4f}s, Space: {max_stack_size}")

        if self.target_node:
            if self.path:
                self.update_results(f"Path found with length: {len(self.path) - 1}")
            else:
                self.update_results("No path found to target")

    def run_bfs(self):
        if not self.graph or self.start_node is None:
            return

        self.animation_running = True
        self.visited = []
        self.path = []

        # Track performance metrics
        start_time = timeit.default_timer()
        max_queue_size = 0

        # Handle path finding if target is specified
        if self.target_node:
            queue = deque([(self.start_node, [self.start_node])])  # (node, path_so_far)
            visited_set = set([self.start_node])  # For O(1) lookup

            while queue and self.animation_running:
                current, path = queue.popleft()
                self.visited.append(current)

                # Track max queue size
                max_queue_size = max(max_queue_size, len(queue))

                # Update visualization
                self.draw_graph()
                self.root.update()
                time.sleep(self.animation_speed)

                # Check if target found
                if current == self.target_node:
                    self.path = path
                    self.draw_graph()
                    break

                # Add unvisited neighbors
                for neighbor in self.graph[current]:
                    if neighbor not in visited_set:
                        visited_set.add(neighbor)
                        queue.append((neighbor, path + [neighbor]))
        else:
            # Regular BFS without path tracking
            queue = deque([self.start_node])
            visited_set = set([self.start_node])

            while queue and self.animation_running:
                current = queue.popleft()
                self.visited.append(current)

                # Track max queue size
                max_queue_size = max(max_queue_size, len(queue))

                # Update visualization
                self.draw_graph()
                self.root.update()
                time.sleep(self.animation_speed)

                # Add unvisited neighbors
                for neighbor in self.graph[current]:
                    if neighbor not in visited_set:
                        visited_set.add(neighbor)
                        queue.append(neighbor)

        # Calculate metrics
        end_time = timeit.default_timer()
        self.metrics["bfs"]["time"] = end_time - start_time
        self.metrics["bfs"]["nodes_visited"] = len(self.visited)
        self.metrics["bfs"]["path_length"] = len(self.path) - 1 if self.path else 0
        self.metrics["bfs"]["space"] = max_queue_size

        self.animation_running = False
        self.update_results(f"BFS completed. Nodes visited: {len(self.visited)}")
        self.update_results(f"Time: {self.metrics['bfs']['time']:.4f}s, Space: {max_queue_size}")

        if self.target_node:
            if self.path:
                self.update_results(f"Path found with length: {len(self.path) - 1}")
            else:
                self.update_results("No path found to target")

    def compare_algorithms(self):
        if self.start_node is None:
            messagebox.showinfo("Info", "Please set a start node first.")
            return

        # Run DFS first
        self.run_dfs()
        dfs_metrics = self.metrics["dfs"].copy()

        # Then run BFS
        self.run_bfs()
        bfs_metrics = self.metrics["bfs"].copy()

        # Add to all metrics history
        self.all_metrics.append({
            "graph_type": "custom",
            "nodes": len(self.nodes),
            "edges": sum(len(neighbors) for neighbors in self.graph.values()) // 2,
            "dfs": dfs_metrics,
            "bfs": bfs_metrics
        })

        # Show comparison
        self.show_metrics_comparison()

    def show_metrics_comparison(self):
        # Prepare data for comparison chart
        self.metric_ax.clear()

        if not self.metrics["dfs"]["time"] and not self.metrics["bfs"]["time"]:
            return

        metrics = ['time', 'nodes_visited', 'path_length', 'space']
        dfs_values = [self.metrics["dfs"][m] for m in metrics]
        bfs_values = [self.metrics["bfs"][m] for m in metrics]

        x = np.arange(len(metrics))
        width = 0.35

        self.metric_ax.bar(x - width / 2, dfs_values, width, label='DFS')
        self.metric_ax.bar(x + width / 2, bfs_values, width, label='BFS')

        self.metric_ax.set_xticks(x)
        self.metric_ax.set_xticklabels(['Time (s)', 'Nodes Visited', 'Path Length', 'Space Usage'])
        self.metric_ax.legend()
        self.metric_ax.set_title('DFS vs BFS Performance Comparison')

        self.metric_canvas.draw()

    def run_batch_comparison(self):
        # Get parameters
        graph_type = self.graph_type_var.get()
        min_size = int(self.min_size_var.get())
        max_size = int(self.max_size_var.get())
        step = int(self.step_size_var.get())
        iterations = int(self.iterations_var.get())

        # Create a progress window
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Running Batch Comparison")
        progress_window.geometry("300x100")

        ttk.Label(progress_window, text="Running batch tests...").pack(pady=10)
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress_window, variable=progress_var, maximum=100)
        progress_bar.pack(fill=tk.X, padx=20, pady=10)

        # Prepare data collection
        all_data = []
        sizes = list(range(min_size, max_size + 1, step))
        total_tests = len(sizes) * iterations
        tests_completed = 0

        # Function to create graph based on type and size
        def create_graph_for_batch(graph_type, size):
            if graph_type == "random":
                # For random graphs, size is node count
                edge_factor = float(self.edge_factor_var.get())
                edge_count = int(size * edge_factor)
                self.create_random_graph(size, edge_count)
                return size, edge_count

            elif graph_type == "grid":
                # For grid graphs, size is dimensions of an NxN grid
                self.create_grid_graph(size, size)
                # Calculate nodes and edges in an NxN grid
                nodes = size * size
                # In a grid, each internal node has 4 neighbors, but we count each edge once
                # Horizontal edges: N * (N-1)
                # Vertical edges: N * (N-1)
                edges = 2 * size * (size - 1)
                return nodes, edges

            elif graph_type == "tree":
                # For tree graphs, size is depth
                branching = int(self.branching_factor_var.get())
                self.create_tree_graph(size, branching)
                # Calculate nodes in a tree with given depth and branching factor
                # Sum of geometric series: (1-r^(n+1))/(1-r) where r is branching factor and n is depth
                if branching == 1:
                    nodes = size + 1
                else:
                    nodes = (1 - branching ** (size + 1)) // (1 - branching)
                # In a tree, edges = nodes - 1
                edges = nodes - 1
                return nodes, edges

        # Run batch tests
        for size in sizes:
            for i in range(iterations):
                # Create graph and select random start/target nodes
                nodes, edges = create_graph_for_batch(graph_type, size)

                # Pick random start and target nodes
                if self.nodes:
                    self.start_node = random.choice(self.nodes)
                    self.target_node = random.choice([n for n in self.nodes if n != self.start_node])

                    # Run DFS
                    self.animation_speed = 0  # Turn off animation for batch testing
                    self.run_dfs()
                    dfs_metrics = self.metrics["dfs"].copy()

                    # Run BFS
                    self.run_bfs()
                    bfs_metrics = self.metrics["bfs"].copy()

                    # Collect data
                    all_data.append({
                        "size": size,
                        "graph_type": graph_type,
                        "nodes": nodes,
                        "edges": edges,
                        "dfs_time": dfs_metrics["time"],
                        "bfs_time": bfs_metrics["time"],
                        "dfs_nodes": dfs_metrics["nodes_visited"],
                        "bfs_nodes": bfs_metrics["nodes_visited"],
                        "dfs_path": dfs_metrics["path_length"],
                        "bfs_path": bfs_metrics["path_length"],
                        "dfs_space": dfs_metrics["space"],
                        "bfs_space": bfs_metrics["space"]
                    })

                # Update progress
                tests_completed += 1
                progress_var.set(100 * tests_completed / total_tests)
                progress_window.update()

        # Close progress window
        progress_window.destroy()

        # Process and display results
        self.batch_data = all_data
        self.plot_batch_results()

    def plot_batch_results(self):
        if not hasattr(self, 'batch_data') or not self.batch_data:
            return

        # Process data by size
        sizes = sorted(set(d["size"] for d in self.batch_data))

        # Aggregate metrics by size
        aggregated_data = {size: {"dfs_time": [], "bfs_time": [],
                                  "dfs_nodes": [], "bfs_nodes": [],
                                  "dfs_path": [], "bfs_path": [],
                                  "dfs_space": [], "bfs_space": []} for size in sizes}

        for d in self.batch_data:
            size = d["size"]
            for metric in ["time", "nodes", "path", "space"]:
                aggregated_data[size][f"dfs_{metric}"].append(d[f"dfs_{metric}"])
                aggregated_data[size][f"bfs_{metric}"].append(d[f"bfs_{metric}"])

        # Calculate averages
        avg_data = {size: {} for size in sizes}
        for size in sizes:
            for metric in ["time", "nodes", "path", "space"]:
                avg_data[size][f"dfs_{metric}"] = np.mean(aggregated_data[size][f"dfs_{metric}"])
                avg_data[size][f"bfs_{metric}"] = np.mean(aggregated_data[size][f"bfs_{metric}"])

        # Plot time comparison
        self.time_ax.clear()
        self.time_ax.plot(sizes, [avg_data[s]["dfs_time"] for s in sizes], 'o-', label='DFS')
        self.time_ax.plot(sizes, [avg_data[s]["bfs_time"] for s in sizes], 's-', label='BFS')
        self.time_ax.set_xlabel('Graph Size')
        self.time_ax.set_ylabel('Execution Time (s)')
        self.time_ax.set_title('DFS vs BFS: Execution Time by Graph Size')
        self.time_ax.legend()
        self.time_ax.grid(True)
        self.time_canvas.draw()

        # Plot nodes visited comparison
        self.nodes_ax.clear()
        self.nodes_ax.plot(sizes, [avg_data[s]["dfs_nodes"] for s in sizes], 'o-', label='DFS')
        self.nodes_ax.plot(sizes, [avg_data[s]["bfs_nodes"] for s in sizes], 's-', label='BFS')
        self.nodes_ax.set_xlabel('Graph Size')
        self.nodes_ax.set_ylabel('Nodes Visited')
        self.nodes_ax.set_title('DFS vs BFS: Nodes Visited by Graph Size')
        self.nodes_ax.legend()
        self.nodes_ax.grid(True)
        self.nodes_canvas.draw()

        # Plot path length comparison
        self.path_ax.clear()
        self.path_ax.plot(sizes, [avg_data[s]["dfs_path"] for s in sizes], 'o-', label='DFS')
        self.path_ax.plot(sizes, [avg_data[s]["bfs_path"] for s in sizes], 's-', label='BFS')
        self.path_ax.set_xlabel('Graph Size')
        self.path_ax.set_ylabel('Path Length')
        self.path_ax.set_title('DFS vs BFS: Path Length by Graph Size')
        self.path_ax.legend()
        self.path_ax.grid(True)
        self.path_canvas.draw()

        # Plot space usage comparison
        self.space_ax.clear()
        self.space_ax.plot(sizes, [avg_data[s]["dfs_space"] for s in sizes], 'o-', label='DFS')
        self.space_ax.plot(sizes, [avg_data[s]["bfs_space"] for s in sizes], 's-', label='BFS')
        self.space_ax.set_xlabel('Graph Size')
        self.space_ax.set_ylabel('Space Usage (max queue/stack)')
        self.space_ax.set_title('DFS vs BFS: Space Usage by Graph Size')
        self.space_ax.legend()
        self.space_ax.grid(True)
        self.space_canvas.draw()

    def export_results(self):
        if not self.metrics["dfs"]["time"] and not self.metrics["bfs"]["time"]:
            messagebox.showinfo("Info", "No results to export. Run a comparison first.")
            return

        try:
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"graph_search_results_{timestamp}.csv"

            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Algorithm', 'Time (s)', 'Nodes Visited', 'Path Length', 'Space Usage'])
                writer.writerow(['DFS', self.metrics["dfs"]["time"], self.metrics["dfs"]["nodes_visited"],
                                 self.metrics["dfs"]["path_length"], self.metrics["dfs"]["space"]])
                writer.writerow(['BFS', self.metrics["bfs"]["time"], self.metrics["bfs"]["nodes_visited"],
                                 self.metrics["bfs"]["path_length"], self.metrics["bfs"]["space"]])

            messagebox.showinfo("Success", f"Results exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export results: {str(e)}")

    def export_batch_results(self):
        if not hasattr(self, 'batch_data') or not self.batch_data:
            messagebox.showinfo("Info", "No batch results to export. Run a batch comparison first.")
            return

        try:
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"batch_comparison_results_{timestamp}.csv"

            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Graph Type', 'Size', 'Nodes', 'Edges',
                                 'DFS Time (s)', 'BFS Time (s)',
                                 'DFS Nodes Visited', 'BFS Nodes Visited',
                                 'DFS Path Length', 'BFS Path Length',
                                 'DFS Space Usage', 'BFS Space Usage'])

                for data in self.batch_data:
                    writer.writerow([
                        data["graph_type"], data["size"], data["nodes"], data["edges"],
                        data["dfs_time"], data["bfs_time"],
                        data["dfs_nodes"], data["bfs_nodes"],
                        data["dfs_path"], data["bfs_path"],
                        data["dfs_space"], data["bfs_space"]
                    ])

            messagebox.showinfo("Success", f"Batch results exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export batch results: {str(e)}")

            # Main function to run the application
def main():
    root = tk.Tk()
    app = GraphSearchVisualizer(root)
    root.mainloop()


if __name__ == "__main__":
    main()