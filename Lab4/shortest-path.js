// Shortest Path Visualization - Lab 4

class ShortestPathVisualizer {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.nodes = [];
        this.edges = [];
        this.graph = {};
        this.distances = {};
        this.visited = new Set();
        this.path = [];
        this.isAnimating = false;
        this.animationSpeed = 300;
        this.algorithm = 'dijkstra';
        this.startTime = 0;
        this.elapsedTime = 0;
    }

    generateRandomGraph(numNodes, density) {
        this.nodes = [];
        this.edges = [];
        this.graph = {};
        this.distances = {};
        this.visited = new Set();
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
            this.graph[i] = {};
        }

        const edgeProbability = density / 100;
        for (let i = 0; i < numNodes; i++) {
            for (let j = i + 1; j < numNodes; j++) {
                if (Math.random() < edgeProbability) {
                    const weight = Math.floor(Math.random() * 20) + 1;
                    this.edges.push({ from: i, to: j, weight });
                    this.graph[i][j] = weight;
                    this.graph[j][i] = weight;
                }
            }
        }

        // Ensure connectivity
        if (this.edges.length === 0) {
            const from = 0;
            const to = numNodes - 1;
            const weight = Math.floor(Math.random() * 20) + 1;
            this.edges.push({ from, to, weight });
            this.graph[from][to] = weight;
            this.graph[to][from] = weight;
        }

        this.draw();
    }

    draw(highlightNode = null) {
        this.ctx.fillStyle = '#f8f9fa';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw edges with weights
        this.ctx.strokeStyle = '#ddd';
        this.ctx.lineWidth = 2.5;
        for (const edge of this.edges) {
            const fromNode = this.nodes[edge.from];
            const toNode = this.nodes[edge.to];
            this.ctx.beginPath();
            this.ctx.moveTo(fromNode.x, fromNode.y);
            this.ctx.lineTo(toNode.x, toNode.y);
            this.ctx.stroke();

            // Draw weight label with background
            const midX = (fromNode.x + toNode.x) / 2;
            const midY = (fromNode.y + toNode.y) / 2;
            this.ctx.fillStyle = 'white';
            this.ctx.fillRect(midX - 12, midY - 10, 24, 20);
            this.ctx.strokeStyle = '#999';
            this.ctx.lineWidth = 1;
            this.ctx.strokeRect(midX - 12, midY - 10, 24, 20);
            
            this.ctx.fillStyle = '#333';
            this.ctx.font = 'bold 12px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            this.ctx.fillText(edge.weight, midX, midY);
        }

        // Draw nodes
        for (const node of this.nodes) {
            let fillColor = '#667eea';

            if (this.visited.has(node.id)) {
                fillColor = '#4caf50';
            }
            if (this.path.includes(node.id)) {
                fillColor = '#ffc107';
            }
            if (highlightNode === node.id) {
                fillColor = '#f5576c';
            }

            // Node shadow
            this.ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
            this.ctx.beginPath();
            this.ctx.arc(node.x + 2, node.y + 3, node.radius, 0, Math.PI * 2);
            this.ctx.fill();

            // Node body with gradient
            const gradient = this.ctx.createRadialGradient(node.x - 8, node.y - 8, 0, node.x, node.y, node.radius);
            gradient.addColorStop(0, this.lightenColor(fillColor, 25));
            gradient.addColorStop(1, fillColor);
            this.ctx.fillStyle = gradient;
            this.ctx.beginPath();
            this.ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
            this.ctx.fill();

            this.ctx.strokeStyle = this.darkenColor(fillColor, 35);
            this.ctx.lineWidth = 2.5;
            this.ctx.stroke();

            this.ctx.fillStyle = 'white';
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

    async dijkstra(sourceNode, targetNode) {
        this.startTime = performance.now();
        this.visited.clear();
        this.path = [];

        const distances = {};
        const previous = {};

        for (let i = 0; i < this.nodes.length; i++) {
            distances[i] = Infinity;
            previous[i] = null;
        }
        distances[sourceNode] = 0;

        for (let i = 0; i < this.nodes.length; i++) {
            let minNode = null;
            let minDist = Infinity;

            for (let j = 0; j < this.nodes.length; j++) {
                if (!this.visited.has(j) && distances[j] < minDist) {
                    minNode = j;
                    minDist = distances[j];
                }
            }

            if (minNode === null || minDist === Infinity) break;

            this.visited.add(minNode);
            this.draw(minNode);
            this.log(`Visiting node ${minNode}, distance: ${minDist}`);
            await this.delay(this.animationSpeed);

            for (const neighbor in this.graph[minNode]) {
                const neighborId = parseInt(neighbor);
                const weight = this.graph[minNode][neighbor];
                const newDist = distances[minNode] + weight;

                if (newDist < distances[neighborId]) {
                    distances[neighborId] = newDist;
                    previous[neighborId] = minNode;
                }
            }
        }

        // Reconstruct path
        let current = targetNode;
        while (current !== null) {
            this.path.unshift(current);
            current = previous[current];
        }

        this.elapsedTime = performance.now() - this.startTime;
        this.draw();
        this.log(`Path found: ${this.path.join(' → ')}, Distance: ${distances[targetNode]}`);

        return distances[targetNode];
    }

    async floydWarshall(sourceNode, targetNode) {
        this.startTime = performance.now();
        this.visited.clear();
        this.path = [];

        const n = this.nodes.length;
        const dist = Array(n).fill(null).map(() => Array(n).fill(Infinity));
        const next = Array(n).fill(null).map(() => Array(n).fill(null));

        // Initialize
        for (let i = 0; i < n; i++) {
            dist[i][i] = 0;
            next[i][i] = i;
        }

        for (const edge of this.edges) {
            dist[edge.from][edge.to] = edge.weight;
            dist[edge.to][edge.from] = edge.weight;
            next[edge.from][edge.to] = edge.to;
            next[edge.to][edge.from] = edge.from;
        }

        // Floyd-Warshall algorithm
        for (let k = 0; k < n; k++) {
            this.visited.add(k);
            this.draw(k);
            this.log(`Processing node ${k}`);
            await this.delay(this.animationSpeed);

            for (let i = 0; i < n; i++) {
                for (let j = 0; j < n; j++) {
                    if (dist[i][k] + dist[k][j] < dist[i][j]) {
                        dist[i][j] = dist[i][k] + dist[k][j];
                        next[i][j] = next[i][k];
                    }
                }
            }
        }

        // Reconstruct path
        let current = sourceNode;
        while (current !== targetNode && current !== null) {
            this.path.push(current);
            current = next[current][targetNode];
        }
        this.path.push(targetNode);

        this.elapsedTime = performance.now() - this.startTime;
        this.draw();
        this.log(`Path found: ${this.path.join(' → ')}, Distance: ${dist[sourceNode][targetNode]}`);

        return dist[sourceNode][targetNode];
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    reset() {
        this.visited.clear();
        this.path = [];
        this.elapsedTime = 0;
        document.getElementById('logArea').innerHTML = '';
        this.draw();
    }

    log(message) {
        const logArea = document.getElementById('logArea');
        const entry = document.createElement('div');
        entry.className = 'log-entry';
        entry.textContent = message;
        logArea.appendChild(entry);
        logArea.scrollTop = logArea.scrollHeight;
    }
}

let visualizer;

function initVisualization() {
    visualizer = new ShortestPathVisualizer('graphCanvas');
    generateGraph();
}

function generateGraph() {
    const numNodes = parseInt(document.getElementById('numNodes').value);
    const density = parseInt(document.getElementById('density').value);
    visualizer.generateRandomGraph(numNodes, density);
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
    updateMetrics(0, 0, 0, '∞');
}

async function startAlgorithm() {
    if (visualizer.isAnimating) return;

    visualizer.isAnimating = true;
    const sourceNode = parseInt(document.getElementById('sourceNode').value);
    const targetNode = parseInt(document.getElementById('targetNode').value);
    visualizer.animationSpeed = parseInt(document.getElementById('animationSpeed').value);

    visualizer.reset();

    let distance = Infinity;
    if (visualizer.algorithm === 'dijkstra') {
        distance = await visualizer.dijkstra(sourceNode, targetNode);
    } else {
        distance = await visualizer.floydWarshall(sourceNode, targetNode);
    }

    updateMetrics(
        visualizer.elapsedTime.toFixed(2),
        visualizer.path.length - 1,
        visualizer.path.length,
        distance === Infinity ? '∞' : distance
    );

    visualizer.isAnimating = false;
}

function updateMetrics(time, steps, pathLength, distance) {
    document.getElementById('metricTime').textContent = time;
    document.getElementById('metricPath').textContent = pathLength;
    document.getElementById('metricDistance').textContent = distance;
    document.getElementById('metricStatus').textContent = distance !== '∞' ? 'Found!' : 'No Path';
}

window.addEventListener('DOMContentLoaded', initVisualization);
