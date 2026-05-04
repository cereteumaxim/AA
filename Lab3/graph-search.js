// Graph Search Visualization - Lab 3

class GraphVisualizer {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.nodes = [];
        this.edges = [];
        this.graph = {};
        this.visited = new Set();
        this.visitedOrder = [];
        this.path = [];
        this.isAnimating = false;
        this.animationSpeed = 500;
        this.algorithm = 'dfs';
        this.startTime = 0;
        this.elapsedTime = 0;
    }

    generateRandomGraph(numNodes, edgeProbability) {
        this.nodes = [];
        this.edges = [];
        this.graph = {};
        this.visited = new Set();
        this.visitedOrder = [];
        this.path = [];

        // Create nodes in circle layout to prevent overlapping
        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2;
        const radius = Math.min(this.canvas.width, this.canvas.height) / 3;
        const nodeRadius = 25;

        for (let i = 0; i < numNodes; i++) {
            const angle = (i / numNodes) * Math.PI * 2;
            this.nodes.push({
                id: i,
                x: centerX + radius * Math.cos(angle),
                y: centerY + radius * Math.sin(angle),
                radius: nodeRadius
            });
            this.graph[i] = [];
        }

        // Create edges based on probability
        const probability = edgeProbability / 100;
        for (let i = 0; i < numNodes; i++) {
            for (let j = i + 1; j < numNodes; j++) {
                if (Math.random() < probability) {
                    this.edges.push({ from: i, to: j });
                    this.graph[i].push(j);
                    this.graph[j].push(i);
                }
            }
        }

        // Ensure connectivity - add a random edge if no edges exist
        if (this.edges.length === 0) {
            const from = 0;
            const to = numNodes - 1;
            this.edges.push({ from, to });
            this.graph[from].push(to);
            this.graph[to].push(from);
        }

        this.draw();
    }

    draw() {
        this.ctx.fillStyle = '#f8f9fa';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw edges
        this.ctx.strokeStyle = '#ccc';
        this.ctx.lineWidth = 2;
        for (const edge of this.edges) {
            const fromNode = this.nodes[edge.from];
            const toNode = this.nodes[edge.to];
            this.ctx.beginPath();
            this.ctx.moveTo(fromNode.x, fromNode.y);
            this.ctx.lineTo(toNode.x, toNode.y);
            this.ctx.stroke();
        }

        // Draw nodes with better styling
        for (const node of this.nodes) {
            let fillColor = '#667eea';
            let textColor = 'white';

            if (this.visitedOrder.includes(node.id)) {
                fillColor = '#4caf50';
            }
            if (this.path.includes(node.id)) {
                fillColor = '#ffc107';
                textColor = '#333';
            }

            // Node shadow
            this.ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
            this.ctx.beginPath();
            this.ctx.arc(node.x + 2, node.y + 3, node.radius, 0, Math.PI * 2);
            this.ctx.fill();

            // Node body with gradient
            const gradient = this.ctx.createRadialGradient(node.x - 8, node.y - 8, 0, node.x, node.y, node.radius);
            gradient.addColorStop(0, this.lightenColor(fillColor, 30));
            gradient.addColorStop(1, fillColor);
            this.ctx.fillStyle = gradient;
            this.ctx.beginPath();
            this.ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
            this.ctx.fill();

            // Node border
            this.ctx.strokeStyle = this.darkenColor(fillColor, 40);
            this.ctx.lineWidth = 2.5;
            this.ctx.stroke();

            // Node label
            this.ctx.fillStyle = textColor;
            this.ctx.font = 'bold 18px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            this.ctx.fillText(node.id, node.x, node.y);
        }
    }

    lightenColor(color, percent) {
        const num = parseInt(color.replace('#',''), 16);
        const amt = Math.round(2.55 * percent);
        return '#' + (0x1000000 + (Math.min(255, (num >> 16) + amt) * 0x10000) + 
                      (Math.min(255, (num >> 8 & 0x00FF) + amt) * 0x100) + 
                      Math.min(255, (num & 0x0000FF) + amt)).toString(16).slice(1);
    }

    darkenColor(color, percent) {
        const num = parseInt(color.replace('#',''), 16);
        const amt = Math.round(2.55 * percent);
        return '#' + (0x1000000 + (Math.max(0, (num >> 16) - amt) * 0x10000) + 
                      (Math.max(0, (num >> 8 & 0x00FF) - amt) * 0x100) + 
                      Math.max(0, (num & 0x0000FF) - amt)).toString(16).slice(1);
    }

    async dfs(startNode, targetNode) {
        this.startTime = performance.now();
        this.visited.clear();
        this.visitedOrder = [];
        this.path = [];

        const stack = [startNode];
        const parent = {};

        while (stack.length > 0) {
            const node = stack.pop();

            if (!this.visited.has(node)) {
                this.visited.add(node);
                this.visitedOrder.push(node);
                this.draw();
                await this.delay(this.animationSpeed);

                if (node === targetNode) {
                    this.reconstructPath(node, startNode, parent);
                    break;
                }

                for (const neighbor of this.graph[node]) {
                    if (!this.visited.has(neighbor)) {
                        parent[neighbor] = node;
                        stack.push(neighbor);
                    }
                }
            }
        }

        this.elapsedTime = performance.now() - this.startTime;
        this.draw();
    }

    async bfs(startNode, targetNode) {
        this.startTime = performance.now();
        this.visited.clear();
        this.visitedOrder = [];
        this.path = [];

        const queue = [startNode];
        const parent = {};
        this.visited.add(startNode);
        this.visitedOrder.push(startNode);

        while (queue.length > 0) {
            const node = queue.shift();

            if (node === targetNode) {
                this.reconstructPath(node, startNode, parent);
                break;
            }

            for (const neighbor of this.graph[node]) {
                if (!this.visited.has(neighbor)) {
                    this.visited.add(neighbor);
                    this.visitedOrder.push(neighbor);
                    parent[neighbor] = node;
                    queue.push(neighbor);
                    this.draw();
                    await this.delay(this.animationSpeed);
                }
            }
        }

        this.elapsedTime = performance.now() - this.startTime;
        this.draw();
    }

    reconstructPath(node, startNode, parent) {
        this.path = [];
        let current = node;
        while (current !== startNode && current in parent) {
            this.path.unshift(current);
            current = parent[current];
        }
        this.path.unshift(startNode);
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    reset() {
        this.visited.clear();
        this.visitedOrder = [];
        this.path = [];
        this.elapsedTime = 0;
        this.draw();
    }
}

// Global visualizer instance
let visualizer;

function initVisualization() {
    visualizer = new GraphVisualizer('graphCanvas');
    generateGraph();
}

function generateGraph() {
    const numNodes = parseInt(document.getElementById('numNodes').value);
    const edgeProbability = parseInt(document.getElementById('edgeProbability').value);

    visualizer.generateRandomGraph(numNodes, edgeProbability);
}

function setAlgorithm(algo) {
    document.querySelectorAll('.algorithm-tabs button').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    visualizer.algorithm = algo;
}

function resetVisualization() {
    visualizer.reset();
    updateMetrics(0, 0, 0);
}

async function startSearch() {
    if (visualizer.isAnimating) return;

    visualizer.isAnimating = true;
    const startNode = parseInt(document.getElementById('startNode').value);
    const targetNode = parseInt(document.getElementById('targetNode').value);
    visualizer.animationSpeed = parseInt(document.getElementById('animationSpeed').value);

    visualizer.reset();

    if (visualizer.algorithm === 'dfs') {
        await visualizer.dfs(startNode, targetNode);
    } else {
        await visualizer.bfs(startNode, targetNode);
    }

    updateMetrics(
        visualizer.elapsedTime.toFixed(2),
        visualizer.visitedOrder.length,
        visualizer.path.length
    );

    visualizer.isAnimating = false;
}

function updateMetrics(time, visited, pathLength) {
    document.getElementById('metricTime').textContent = time;
    document.getElementById('metricVisited').textContent = visited;
    document.getElementById('metricPath').textContent = pathLength;
    document.getElementById('metricStatus').textContent = pathLength > 0 ? 'Found!' : 'Ready';
}

// Initialize on page load
window.addEventListener('DOMContentLoaded', initVisualization);
