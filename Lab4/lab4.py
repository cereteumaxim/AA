import tkinter as tk
from tkinter import ttk, messagebox
import time
import random
import heapq
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import numpy as np
import threading


class ShortestPathGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Shortest Path Algorithms Visualizer")
        self.root.geometry("1000x700")

        self.graph_matrix = None
        self.graph_adj_list = None
        self.source_node = 0
        self.animation_speed = 500  # ms
        self.is_animating = False

        # Create main frames
        self.left_frame = ttk.Frame(self.root, padding="10")
        self.left_frame.grid(row=0, column=0, sticky="nsew")

        self.right_frame = ttk.Frame(self.root, padding="10")
        self.right_frame.grid(row=0, column=1, sticky="nsew")

        self.bottom_frame = ttk.Frame(self.root, padding="10")
        self.bottom_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")

        # Configure grid weights
        self.root.grid_columnconfigure(0, weight=1, minsize=250)
        self.root.grid_columnconfigure(1, weight=3)
        self.root.grid_rowconfigure(0, weight=3)
        self.root.grid_rowconfigure(1, weight=1)

        # Create controls
        self.create_controls()

        # Create graph display
        self.fig = plt.Figure(figsize=(6, 5), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)
        self.ax = self.fig.add_subplot(111)

        # Create text area for algorithm steps
        self.log_text = tk.Text(self.bottom_frame, height=10, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(self.bottom_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Initialize with a small graph
        self.generate_new_graph()

    def create_controls(self):
        # Graph generation section
        ttk.Label(self.left_frame, text="Graph Generation", font=("Arial", 11, "bold")).grid(row=0, column=0,
                                                                                             columnspan=2, pady=5,
                                                                                             sticky="w")

        ttk.Label(self.left_frame, text="Nodes:").grid(row=1, column=0, sticky="w", pady=2)
        self.node_var = tk.IntVar(value=10)
        ttk.Spinbox(self.left_frame, from_=5, to=50, textvariable=self.node_var, width=5).grid(row=1, column=1,
                                                                                               sticky="w", pady=2)

        ttk.Label(self.left_frame, text="Density:").grid(row=2, column=0, sticky="w", pady=2)
        self.density_var = tk.DoubleVar(value=0.3)
        ttk.Spinbox(self.left_frame, from_=0.1, to=1.0, increment=0.1, textvariable=self.density_var, width=5).grid(
            row=2, column=1, sticky="w", pady=2)

        ttk.Label(self.left_frame, text="Directed:").grid(row=3, column=0, sticky="w", pady=2)
        self.directed_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.left_frame, variable=self.directed_var).grid(row=3, column=1, sticky="w", pady=2)

        ttk.Button(self.left_frame, text="Generate Graph", command=self.generate_new_graph).grid(row=4, column=0,
                                                                                                 columnspan=2, pady=5)

        # Algorithm section
        ttk.Separator(self.left_frame, orient="horizontal").grid(row=5, column=0, columnspan=2, sticky="ew", pady=10)
        ttk.Label(self.left_frame, text="Algorithm Controls", font=("Arial", 11, "bold")).grid(row=6, column=0,
                                                                                               columnspan=2, pady=5,
                                                                                               sticky="w")

        ttk.Label(self.left_frame, text="Source:").grid(row=7, column=0, sticky="w", pady=2)
        self.source_var = tk.IntVar(value=0)
        self.source_combo = ttk.Combobox(self.left_frame, textvariable=self.source_var, width=5)
        self.source_combo.grid(row=7, column=1, sticky="w", pady=2)

        ttk.Label(self.left_frame, text="Algorithm:").grid(row=8, column=0, sticky="w", pady=2)
        self.algorithm_var = tk.StringVar(value="dijkstra")
        ttk.Radiobutton(self.left_frame, text="Dijkstra", variable=self.algorithm_var, value="dijkstra").grid(row=8,
                                                                                                              column=1,
                                                                                                              sticky="w",
                                                                                                              pady=2)
        ttk.Radiobutton(self.left_frame, text="Floyd-Warshall", variable=self.algorithm_var, value="floyd").grid(row=9,
                                                                                                                 column=1,
                                                                                                                 sticky="w",
                                                                                                                 pady=2)

        ttk.Label(self.left_frame, text="Speed:").grid(row=10, column=0, sticky="w", pady=2)
        self.speed_var = tk.IntVar(value=500)
        ttk.Scale(self.left_frame, from_=100, to=1500, orient="horizontal", variable=self.speed_var).grid(row=10,
                                                                                                          column=1,
                                                                                                          sticky="we",
                                                                                                          pady=2)

        # Run buttons
        ttk.Button(self.left_frame, text="Run with Visualization", command=self.run_visualization).grid(row=11,
                                                                                                        column=0,
                                                                                                        columnspan=2,
                                                                                                        pady=5)
        ttk.Button(self.left_frame, text="Reset", command=self.reset_visualization).grid(row=12, column=0, columnspan=2,
                                                                                         pady=5)

        # Batch testing section
        ttk.Separator(self.left_frame, orient="horizontal").grid(row=13, column=0, columnspan=2, sticky="ew", pady=10)
        ttk.Label(self.left_frame, text="Batch Testing", font=("Arial", 11, "bold")).grid(row=14, column=0,
                                                                                          columnspan=2, pady=5,
                                                                                          sticky="w")

        ttk.Label(self.left_frame, text="Max Nodes:").grid(row=15, column=0, sticky="w", pady=2)
        self.max_nodes_var = tk.IntVar(value=300)
        ttk.Spinbox(self.left_frame, from_=50, to=500, textvariable=self.max_nodes_var, width=5).grid(row=15, column=1,
                                                                                                      sticky="w",
                                                                                                      pady=2)

        ttk.Label(self.left_frame, text="Step Size:").grid(row=16, column=0, sticky="w", pady=2)
        self.step_size_var = tk.IntVar(value=50)
        ttk.Spinbox(self.left_frame, from_=10, to=100, textvariable=self.step_size_var, width=5).grid(row=16, column=1,
                                                                                                      sticky="w",
                                                                                                      pady=2)

        ttk.Button(self.left_frame, text="Run Batch Test", command=self.run_batch_test).grid(row=17, column=0,
                                                                                             columnspan=2, pady=5)

    def generate_new_graph(self):
        """Generate a new graph based on current settings"""
        self.is_animating = False

        n = self.node_var.get()
        density = self.density_var.get()
        directed = self.directed_var.get()

        # Generate adjacency matrix
        self.graph_matrix = self.generate_graph(n, density, directed)
        self.graph_adj_list = self.matrix_to_adj_list(self.graph_matrix)

        # Update source node dropdown
        self.source_combo['values'] = list(range(n))
        if self.source_var.get() >= n:
            self.source_var.set(0)

        # Draw the graph
        self.draw_graph()

        # Log information
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END,
                             f"Generated {'directed' if directed else 'undirected'} graph with {n} nodes and density {density:.2f}\n")
        edge_count = sum(1 for i in range(n) for j in range(n)
                         if self.graph_matrix[i][j] != float('inf') and i != j)
        self.log_text.insert(tk.END, f"Total edges: {edge_count}\n")
        self.log_text.insert(tk.END, "Select an algorithm and source node, then run visualization.\n")

    def generate_graph(self, n, density, directed=False):
        """Generate adjacency matrix for a random graph"""
        matrix = [[float('inf')] * n for _ in range(n)]

        # Set diagonal to zero
        for i in range(n):
            matrix[i][i] = 0

        # Add random edges
        for i in range(n):
            for j in range(n):
                if i != j and random.random() < density:
                    weight = random.randint(1, 10)
                    matrix[i][j] = weight
                    if not directed:
                        matrix[j][i] = weight

        return matrix

    def matrix_to_adj_list(self, matrix):
        """Convert adjacency matrix to adjacency list"""
        adj_list = []
        n = len(matrix)

        for i in range(n):
            neighbors = []
            for j in range(n):
                if matrix[i][j] != float('inf') and i != j:
                    neighbors.append((j, matrix[i][j]))
            adj_list.append(neighbors)

        return adj_list

    def draw_graph(self, distances=None, visited=None, current_node=None):
        """Draw the graph with optional algorithm state visualization"""
        self.ax.clear()

        # Create NetworkX graph
        if self.directed_var.get():
            G = nx.DiGraph()
        else:
            G = nx.Graph()

        n = len(self.graph_matrix)

        # Add nodes
        for i in range(n):
            G.add_node(i)

        # Add edges
        for i in range(n):
            for j in range(n):
                if self.graph_matrix[i][j] != float('inf') and i != j:
                    G.add_edge(i, j, weight=self.graph_matrix[i][j])

        # Generate positions - circular layout is more readable for small graphs
        if n <= 20:
            pos = nx.circular_layout(G)
        else:
            pos = nx.spring_layout(G, seed=42)

        # Node colors
        node_colors = ['lightblue'] * n

        # Source node
        source = self.source_var.get()
        if source < n:
            node_colors[source] = 'green'

        # Current node being processed
        if current_node is not None and current_node < n:
            node_colors[current_node] = 'red'

        # Visited nodes
        if visited:
            for i in range(n):
                if visited[i] and i != source:
                    node_colors[i] = 'yellow'

        # Draw nodes and edges
        nx.draw(G, pos, ax=self.ax, with_labels=True,
                node_color=node_colors, node_size=500, arrows=self.directed_var.get())

        # Draw edge labels (weights)
        edge_labels = {(i, j): self.graph_matrix[i][j] for i in range(n) for j in range(n)
                       if self.graph_matrix[i][j] != float('inf') and i != j}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=self.ax)

        # Set title
        algo = "Dijkstra's Algorithm" if self.algorithm_var.get() == "dijkstra" else "Floyd-Warshall Algorithm"
        self.ax.set_title(f"Graph Visualization - {algo}")

        # Show distances if available
        if distances:
            dist_text = "\n".join([f"Distance to node {i}: {d if d != float('inf') else 'inf'}"
                                   for i, d in enumerate(distances)])
            self.ax.text(0.02, 0.02, dist_text, transform=self.ax.transAxes,
                         bbox=dict(facecolor='white', alpha=0.8))

        self.canvas.draw()

    def run_visualization(self):
        """Run selected algorithm with visualization"""
        self.reset_visualization()
        self.is_animating = True

        algorithm = self.algorithm_var.get()
        source = self.source_var.get()

        if algorithm == "dijkstra":
            self.log_text.insert(tk.END, f"Running Dijkstra's algorithm from source {source}...\n")
            self.visualize_dijkstra(source)
        else:
            self.log_text.insert(tk.END, f"Running Floyd-Warshall algorithm (showing paths from source {source})...\n")
            self.visualize_floyd_warshall(source)

    def reset_visualization(self):
        """Reset all visualizations"""
        self.is_animating = False
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, "Ready to run algorithm.\n")
        self.draw_graph()

    def visualize_dijkstra(self, source):
        """Visualize Dijkstra's algorithm execution"""
        n = len(self.graph_adj_list)
        dist = [float('inf')] * n
        dist[source] = 0
        visited = [False] * n
        prev = [None] * n

        # Priority queue
        pq = [(0, source)]

        self.log_text.insert(tk.END, f"Initialize distances: {self.format_distances(dist)}\n")
        self.draw_graph(dist, visited)

        while pq and self.is_animating:
            # Get node with minimum distance
            current_dist, u = heapq.heappop(pq)

            # Skip if already processed
            if visited[u]:
                continue

            # Mark as visited
            visited[u] = True

            self.log_text.insert(tk.END, f"\nProcessing node {u} (distance: {current_dist})\n")
            self.draw_graph(dist, visited, u)

            # Process all neighbors
            for v, weight in self.graph_adj_list[u]:
                if not visited[v]:
                    # Relaxation step
                    if dist[v] > dist[u] + weight:
                        dist[v] = dist[u] + weight
                        prev[v] = u
                        heapq.heappush(pq, (dist[v], v))
                        self.log_text.insert(tk.END, f"  Updated node {v}: new distance = {dist[v]}\n")

            self.log_text.see(tk.END)

            # Pause for animation
            self.canvas.draw()
            self.root.update()
            time.sleep(self.speed_var.get() / 1000)

        # Show final results
        if self.is_animating:
            self.log_text.insert(tk.END, "\nFinal shortest paths from source:\n")
            for i in range(n):
                if i != source:
                    # Reconstruct path
                    path = []
                    curr = i
                    while curr is not None:
                        path.append(curr)
                        curr = prev[curr]
                    path.reverse()

                    path_str = " -> ".join(map(str, path))
                    if dist[i] == float('inf'):
                        self.log_text.insert(tk.END, f"Node {i}: No path exists\n")
                    else:
                        self.log_text.insert(tk.END, f"Node {i}: Distance = {dist[i]}, Path = {path_str}\n")

            self.draw_graph(dist, visited)
            self.log_text.see(tk.END)

    def visualize_floyd_warshall(self, source):
        """Visualize Floyd-Warshall algorithm execution"""
        n = len(self.graph_matrix)
        # Create a copy of the distance matrix
        dist = [row[:] for row in self.graph_matrix]

        self.log_text.insert(tk.END, "Initializing distance matrix...\n")

        # Visualize initial state (only from source perspective)
        self.draw_graph(dist[source], [False] * n)
        time.sleep(self.speed_var.get() / 1000)

        # Floyd-Warshall main loop
        for k in range(n):
            if not self.is_animating:
                break

            self.log_text.insert(tk.END, f"\nUsing node {k} as intermediate...\n")

            # Highlight current k node being used as intermediate
            visited = [False] * n
            visited[k] = True
            self.draw_graph(dist[source], visited, k)

            # Update distances
            updates = []
            for i in range(n):
                for j in range(n):
                    if dist[i][k] != float('inf') and dist[k][j] != float('inf'):
                        if dist[i][j] > dist[i][k] + dist[k][j]:
                            old = dist[i][j]
                            dist[i][j] = dist[i][k] + dist[k][j]
                            if i == source:  # Log only updates from source
                                updates.append(
                                    f"  Improved path {i}->{j} via {k}: {old if old != float('inf') else 'inf'} -> {dist[i][j]}")

            # Log updates from source perspective
            for update in updates:
                self.log_text.insert(tk.END, update + "\n")

            self.log_text.see(tk.END)

            # Update visualization from source perspective
            self.draw_graph(dist[source], visited, k)
            self.root.update()
            time.sleep(self.speed_var.get() / 1000)

        # Show final results
        if self.is_animating:
            self.log_text.insert(tk.END, "\nFinal shortest paths from source:\n")
            for i in range(n):
                if i != source and dist[source][i] != float('inf'):
                    self.log_text.insert(tk.END, f"Node {i}: Distance = {dist[source][i]}\n")
                elif i != source:
                    self.log_text.insert(tk.END, f"Node {i}: No path exists\n")

            self.draw_graph(dist[source], [True] * n)
            self.log_text.see(tk.END)

    def format_distances(self, distances):
        """Format distance array for display"""
        return [d if d != float('inf') else "inf" for d in distances]

    def run_dijkstra(self, adj_list, source):
        """Run Dijkstra without visualization for batch testing"""
        n = len(adj_list)
        dist = [float('inf')] * n
        dist[source] = 0

        pq = [(0, source)]
        visited = [False] * n

        while pq:
            current_dist, u = heapq.heappop(pq)

            if visited[u]:
                continue

            visited[u] = True

            for v, weight in adj_list[u]:
                if dist[v] > current_dist + weight:
                    dist[v] = current_dist + weight
                    heapq.heappush(pq, (dist[v], v))

        return dist

    def run_floyd_warshall(self, matrix):
        """Run Floyd-Warshall without visualization for batch testing"""
        n = len(matrix)
        dist = [row[:] for row in matrix]

        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if dist[i][k] != float('inf') and dist[k][j] != float('inf'):
                        dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])

        return dist

    def all_pairs_dijkstra(self, adj_list):
        """Compute all-pairs shortest paths using Dijkstra's algorithm"""
        n = len(adj_list)
        return [self.run_dijkstra(adj_list, start) for start in range(n)]

    def run_batch_test(self):
        """Run batch performance test without visualization"""
        # Create a new window for results
        result_window = tk.Toplevel(self.root)
        result_window.title("Batch Performance Test")
        result_window.geometry("800x600")

        # Create progress indicator
        progress_var = tk.DoubleVar()
        progress_frame = ttk.Frame(result_window, padding=10)
        progress_frame.pack(fill=tk.X, pady=10)

        ttk.Label(progress_frame, text="Progress:").pack(side=tk.LEFT, padx=5)
        progress_bar = ttk.Progressbar(progress_frame, variable=progress_var, maximum=100, length=300)
        progress_bar.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        status_label = ttk.Label(progress_frame, text="Preparing test...")
        status_label.pack(side=tk.LEFT, padx=5)

        # Create plot area
        fig = plt.Figure(figsize=(8, 6))
        canvas = FigureCanvasTkAgg(fig, master=result_window)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        ax = fig.add_subplot(111)

        # Create a frame for test results
        results_frame = ttk.Frame(result_window, padding=10)
        results_frame.pack(fill=tk.X)

        results_text = tk.Text(results_frame, height=10)
        scrollbar = ttk.Scrollbar(results_frame, command=results_text.yview)
        results_text.configure(yscrollcommand=scrollbar.set)
        results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Function to run the test in background
        def run_test():
            max_nodes = self.max_nodes_var.get()
            step_size = self.step_size_var.get()

            # Generate node sizes to test
            node_counts = list(range(50, max_nodes + 1, step_size))

            # Results arrays
            sparse_dijkstra_times = []
            sparse_floyd_times = []
            dense_dijkstra_times = []
            dense_floyd_times = []

            total_steps = len(node_counts) * 4
            current_step = 0

            for n in node_counts:
                # Update status
                result_window.after(0, lambda: status_label.config(text=f"Testing with {n} nodes..."))
                result_window.after(0, lambda: results_text.insert(tk.END, f"Testing with {n} nodes...\n"))
                result_window.after(0, lambda: results_text.see(tk.END))

                # Test on sparse graph
                sparse_density = min(5.0 / n, 0.3)  # Ensure sparse graph
                matrix = self.generate_graph(n, sparse_density)
                adj_list = self.matrix_to_adj_list(matrix)

                # Run Dijkstra on sparse graph
                start = time.time()
                self.all_pairs_dijkstra(adj_list)
                sparse_dijkstra_times.append(time.time() - start)
                current_step += 1
                result_window.after(0, lambda: progress_var.set(100 * current_step / total_steps))

                # Run Floyd-Warshall on sparse graph
                start = time.time()
                self.run_floyd_warshall(matrix)
                sparse_floyd_times.append(time.time() - start)
                current_step += 1
                result_window.after(0, lambda: progress_var.set(100 * current_step / total_steps))

                # Test on dense graph
                matrix = self.generate_graph(n, 0.7)  # Dense graph
                adj_list = self.matrix_to_adj_list(matrix)

                # Run Dijkstra on dense graph
                start = time.time()
                self.all_pairs_dijkstra(adj_list)
                dense_dijkstra_times.append(time.time() - start)
                current_step += 1
                result_window.after(0, lambda: progress_var.set(100 * current_step / total_steps))

                # Run Floyd-Warshall on dense graph
                start = time.time()
                self.run_floyd_warshall(matrix)
                dense_floyd_times.append(time.time() - start)
                current_step += 1
                result_window.after(0, lambda: progress_var.set(100 * current_step / total_steps))

                # Update results text
                result_msg = (f"N={n}: Sparse Dijkstra={sparse_dijkstra_times[-1]:.4f}s, "
                              f"Sparse Floyd={sparse_floyd_times[-1]:.4f}s, "
                              f"Dense Dijkstra={dense_dijkstra_times[-1]:.4f}s, "
                              f"Dense Floyd={dense_floyd_times[-1]:.4f}s\n")
                result_window.after(0, lambda: results_text.insert(tk.END, result_msg))
                result_window.after(0, lambda: results_text.see(tk.END))

            # Update plot with final results
            def update_plot():
                ax.clear()
                ax.plot(node_counts, sparse_dijkstra_times, 'o-', label='Sparse Dijkstra (All-Pairs)')
                ax.plot(node_counts, sparse_floyd_times, 's-', label='Sparse Floyd-Warshall')
                ax.plot(node_counts, dense_dijkstra_times, '^-', label='Dense Dijkstra (All-Pairs)')
                ax.plot(node_counts, dense_floyd_times, 'd-', label='Dense Floyd-Warshall')
                ax.set_xlabel('Number of Nodes')
                ax.set_ylabel('Time (seconds)')
                ax.set_title('Algorithm Performance Comparison')
                ax.legend()
                ax.grid(True)
                fig.tight_layout()
                canvas.draw()
                status_label.config(text="Test complete!")

            result_window.after(0, update_plot)

        # Run test in separate thread
        threading.Thread(target=run_test, daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = ShortestPathGUI(root)
    root.mainloop()