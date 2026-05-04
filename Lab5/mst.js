// Minimum Spanning Tree Visualization - Lab 5

class MSTVisualizer {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.nodes = [];
        this.edges = [];
        this.graph = {};
        this.mstEdges = [];
        this.visitedEdges = [];
        this.isAnimating = false;
        this.animationSpeed = 400;
        this.algorithm = 'prim';
        this.startTime = 0;
        this.elapsedTime = 0;
        this.totalWeight = 0;
    }

    generateRandomGraph(numNodes, edgeProbability, maxWeight) {
        this.nodes = [];
        this.edges = [];
        this.graph = {};
        this.mstEdges = [];
        this.visitedEdges = [];
        this.totalWeight = 0;

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

        const probability = edgeProbability / 100;
        for (let i = 0; i < numNodes; i++) {
            for (let j = i + 1; j < numNodes; j++) {
                if (Math.random() < probability) {
                    const weight = Math.floor(Math.random() * maxWeight) + 1;
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
            const weight = Math.floor(Math.random() * maxWeight) + 1;
            this.edges.push({ from, to, weight });
            this.graph[from][to] = weight;
            this.graph[to][from] = weight;
        }

        // Sort edges by weight for Kruskal's
        this.edges.sort((a, b) => a.weight - b.weight);

        this.draw();
    }

    draw() {
        this.ctx.fillStyle = '#f8f9fa';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw edges
        for (const edge of this.edges) {
            const fromNode = this.nodes[edge.from];
            const toNode = this.nodes[edge.to];

            let strokeColor = '#ddd';
            let lineWidth = 2;

            if (this.mstEdges.some(e => (e.from === edge.from && e.to === edge.to) || (e.from === edge.to && e.to === edge.from))) {
                strokeColor = '#ffc107';
                lineWidth = 4;
            } else if (this.visitedEdges.some(e => (e.from === edge.from && e.to === edge.to) || (e.from === edge.to && e.to === edge.from))) {
                strokeColor = '#a5d6a7';
                lineWidth = 2.5;
            }

            this.ctx.strokeStyle = strokeColor;
            this.ctx.lineWidth = lineWidth;
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
            // Node shadow
            this.ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
            this.ctx.beginPath();
            this.ctx.arc(node.x + 2, node.y + 3, node.radius, 0, Math.PI * 2);
            this.ctx.fill();

            // Node body with gradient
            const gradient = this.ctx.createRadialGradient(node.x - 8, node.y - 8, 0, node.x, node.y, node.radius);
            gradient.addColorStop(0, '#7e8fef');
            gradient.addColorStop(1, '#667eea');
            this.ctx.fillStyle = gradient;
            this.ctx.beginPath();
            this.ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
            this.ctx.fill();

            this.ctx.strokeStyle = '#4c47d4';
            this.ctx.lineWidth = 2.5;
            this.ctx.stroke();

            this.ctx.fillStyle = 'white';
            this.ctx.font = 'bold 18px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            this.ctx.fillText(node.id, node.x, node.y);
        }
    }

    find(parent, i) {
        if (parent[i] !== i) {
            parent[i] = this.find(parent, parent[i]);
        }
        return parent[i];
    }

    union(parent, rank, x, y) {
        const xroot = this.find(parent, x);
        const yroot = this.find(parent, y);

        if (rank[xroot] < rank[yroot]) {
            parent[xroot] = yroot;
        } else if (rank[xroot] > rank[yroot]) {
            parent[yroot] = xroot;
        } else {
            parent[yroot] = xroot;
            rank[xroot]++;
        }
    }

    async prim(startNode = 0) {
        this.startTime = performance.now();
        this.mstEdges = [];
        this.visitedEdges = [];
        this.totalWeight = 0;

        const visited = new Set([startNode]);
        const candidateEdges = [];

        // Add all edges from start node
        for (const neighbor in this.graph[startNode]) {
            const neighborId = parseInt(neighbor);
            const weight = this.graph[startNode][neighbor];
            candidateEdges.push({ from: startNode, to: neighborId, weight });
        }
        candidateEdges.sort((a, b) => a.weight - b.weight);

        while (candidateEdges.length > 0 && visited.size < this.nodes.length) {
            candidateEdges.sort((a, b) => a.weight - b.weight);
            const edge = candidateEdges.shift();

            if (visited.has(edge.to)) {
                this.visitedEdges.push(edge);
                continue;
            }

            visited.add(edge.to);
            this.mstEdges.push(edge);
            this.totalWeight += edge.weight;
            this.visitedEdges.push(edge);

            this.draw();
            this.log(`Added edge: ${edge.from}-${edge.to} (weight: ${edge.weight})`);
            await this.delay(this.animationSpeed);

            // Add new candidate edges
            for (const neighbor in this.graph[edge.to]) {
                const neighborId = parseInt(neighbor);
                if (!visited.has(neighborId)) {
                    const weight = this.graph[edge.to][neighbor];
                    candidateEdges.push({ from: edge.to, to: neighborId, weight });
                }
            }
        }

        this.elapsedTime = performance.now() - this.startTime;
        this.draw();
    }

    async kruskal() {
        this.startTime = performance.now();
        this.mstEdges = [];
        this.visitedEdges = [];
        this.totalWeight = 0;

        const parent = {};
        const rank = {};

        for (let i = 0; i < this.nodes.length; i++) {
            parent[i] = i;
            rank[i] = 0;
        }

        for (const edge of this.edges) {
            const x = this.find(parent, edge.from);
            const y = this.find(parent, edge.to);

            if (x !== y) {
                this.mstEdges.push(edge);
                this.totalWeight += edge.weight;
                this.union(parent, rank, x, y);
                this.log(`Added edge: ${edge.from}-${edge.to} (weight: ${edge.weight})`);
            } else {
                this.visitedEdges.push(edge);
                this.log(`Skipped edge: ${edge.from}-${edge.to} (would create cycle)`);
            }

            this.draw();
            await this.delay(this.animationSpeed);
        }

        this.elapsedTime = performance.now() - this.startTime;
        this.draw();
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    reset() {
        this.mstEdges = [];
        this.visitedEdges = [];
        this.totalWeight = 0;
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
    visualizer = new MSTVisualizer('graphCanvas');
    generateGraph();
}

function generateGraph() {
    const numNodes = parseInt(document.getElementById('numNodes').value);
    const edgeProbability = parseInt(document.getElementById('edgeProbability').value);
    const maxWeight = parseInt(document.getElementById('maxWeight').value);

    visualizer.generateRandomGraph(numNodes, edgeProbability, maxWeight);
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

async function startAlgorithm() {
    if (visualizer.isAnimating) return;

    visualizer.isAnimating = true;
    visualizer.animationSpeed = parseInt(document.getElementById('animationSpeed').value);

    visualizer.reset();

    if (visualizer.algorithm === 'prim') {
        await visualizer.prim(0);
    } else {
        await visualizer.kruskal();
    }

    updateMetrics(
        visualizer.elapsedTime.toFixed(2),
        visualizer.mstEdges.length,
        visualizer.totalWeight
    );

    visualizer.isAnimating = false;
}

function updateMetrics(time, edgesUsed, totalWeight) {
    document.getElementById('metricTime').textContent = time;
    document.getElementById('metricEdges').textContent = edgesUsed;
    document.getElementById('metricWeight').textContent = totalWeight;
    document.getElementById('metricStatus').textContent = edgesUsed > 0 ? 'Complete' : 'Ready';
}

window.addEventListener('DOMContentLoaded', initVisualization);
