const barsEl = document.getElementById('bars');
const overlayEl = document.getElementById('overlay');
const algorithmEl = document.getElementById('algorithm');
const sizeEl = document.getElementById('size');
const sizeValueEl = document.getElementById('size-value');
const speedEl = document.getElementById('speed');
const speedValueEl = document.getElementById('speed-value');
const statusEl = document.getElementById('status');
const detailEl = document.getElementById('detail');
const secondaryTitleEl = document.getElementById('secondary-title');
const valuesEl = document.getElementById('array-values');
const customInputEl = document.getElementById('custom-array');
const loadBtn = document.getElementById('load-array');

const generateBtn = document.getElementById('generate');
const playBtn = document.getElementById('play');
const stepBtn = document.getElementById('step');
const resetBtn = document.getElementById('reset');

let baseArray = [];
let steps = [];
let stepIndex = 0;
let playing = false;
let playHandle = null;

const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));

function randomArray(size) {
  const arr = [];
  for (let i = 0; i < size; i++) {
    arr.push(Math.floor(Math.random() * 90) + 10);
  }
  return arr;
}

function renderBars(arr, highlights = {}, algorithm = '') {
  barsEl.innerHTML = '';
  const max = Math.max(...arr);
  const duration = algorithm === 'shell' ? 280 : 140;

  arr.forEach((val, idx) => {
    const bar = document.createElement('div');
    const pct = (val / max) * 100;
    bar.className = 'bar';
    if (highlights[idx]) {
      bar.classList.add(highlights[idx]);
    }
    bar.style.transition = `height ${duration}ms ease, transform ${duration}ms ease, background ${duration}ms ease`;
    bar.style.height = `${pct}%`;
    barsEl.appendChild(bar);
  });

  valuesEl.innerHTML = '';
  arr.forEach((val, idx) => {
    const span = document.createElement('span');
    span.className = `val ${highlights[idx] || ''}`.trim();
    span.textContent = val;
    valuesEl.appendChild(span);
  });
}

function clearOverlay() {
  overlayEl.innerHTML = '';
}

function drawHeapTree(arr, highlights) {
  clearOverlay();
  const w = 1100;
  const h = 500;
  const maxLevel = Math.floor(Math.log2(arr.length || 1));
  const levelGap = h / (maxLevel + 2);

  const nodes = arr.map((value, idx) => {
    const level = Math.floor(Math.log2(idx + 1));
    const posInLevel = idx - (Math.pow(2, level) - 1);
    const slots = Math.pow(2, level);
    const x = ((posInLevel + 1) / (slots + 1)) * w;
    const y = (level + 1) * levelGap;
    return { idx, value, x, y };
  });

  nodes.forEach((node) => {
    const parentIdx = Math.floor((node.idx - 1) / 2);
    if (parentIdx >= 0) {
      const parent = nodes[parentIdx];
      const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      line.setAttribute('x1', parent.x);
      line.setAttribute('y1', parent.y);
      line.setAttribute('x2', node.x);
      line.setAttribute('y2', node.y);
      line.setAttribute('stroke', '#263341');
      line.setAttribute('stroke-width', '2');
      overlayEl.appendChild(line);
    }
  });

  nodes.forEach((node) => {
    const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    const color = highlights[node.idx] === 'swap' ? '#f472b6'
      : highlights[node.idx] === 'pivot' ? '#facc15'
      : highlights[node.idx] === 'compare' ? '#38bdf8'
      : '#0ea5e9';
    circle.setAttribute('cx', node.x);
    circle.setAttribute('cy', node.y);
    circle.setAttribute('r', '22');
    circle.setAttribute('fill', color);
    circle.setAttribute('stroke', '#0b1119');
    circle.setAttribute('stroke-width', '2');

    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('x', node.x);
    text.setAttribute('y', node.y + 5);
    text.setAttribute('text-anchor', 'middle');
    text.setAttribute('fill', '#0b1119');
    text.setAttribute('font-size', '14');
    text.setAttribute('font-weight', '700');
    text.textContent = node.value;

    group.appendChild(circle);
    group.appendChild(text);
    overlayEl.appendChild(group);
  });
}

function drawQuickOverlay(step) {
  clearOverlay();
  const { arr, meta, highlights } = step;
  const w = 1100;
  const h = 160;
  const y = 120;
  const barW = w / arr.length;

  const band = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
  band.setAttribute('x', meta.low * barW);
  band.setAttribute('y', 40);
  band.setAttribute('width', (meta.high - meta.low + 1) * barW);
  band.setAttribute('height', 220);
  band.setAttribute('fill', 'rgba(56,189,248,0.08)');
  band.setAttribute('stroke', '#263341');
  overlayEl.appendChild(band);

  arr.forEach((val, idx) => {
    const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    const cls = highlights[idx];
    const fill = cls === 'pivot' ? '#facc15' : cls === 'swap' ? '#f472b6' : cls === 'compare' ? '#38bdf8' : '#0ea5e9';
    rect.setAttribute('x', idx * barW + 6);
    rect.setAttribute('y', y - val * 2);
    rect.setAttribute('width', barW - 8);
    rect.setAttribute('height', val * 2);
    rect.setAttribute('rx', '6');
    rect.setAttribute('fill', fill);
    overlayEl.appendChild(rect);
  });

  if (meta.pivotIndex !== undefined) {
    const tri = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
    const px = meta.pivotIndex * barW + barW / 2;
    tri.setAttribute('points', `${px - 10},30 ${px + 10},30 ${px},10`);
    tri.setAttribute('fill', '#facc15');
    overlayEl.appendChild(tri);
  }
}

function drawMergeOverlay(step) {
  clearOverlay();
  const { arr, meta, highlights } = step;
  const w = 1100;
  const laneHeight = 60;
  const barW = w / arr.length;

  const lanes = [120, 220, 320];
  const segments = [
    { start: meta.left, end: meta.mid, y: lanes[0], color: 'rgba(56,189,248,0.16)' },
    { start: meta.mid + 1, end: meta.right, y: lanes[1], color: 'rgba(244,162,97,0.16)' },
    { start: meta.left, end: meta.right, y: lanes[2], color: 'rgba(45,212,191,0.12)' },
  ];

  segments.forEach((seg) => {
    const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    rect.setAttribute('x', seg.start * barW);
    rect.setAttribute('y', seg.y - laneHeight / 2);
    rect.setAttribute('width', (seg.end - seg.start + 1) * barW);
    rect.setAttribute('height', laneHeight);
    rect.setAttribute('rx', '10');
    rect.setAttribute('fill', seg.color);
    rect.setAttribute('stroke', '#263341');
    overlayEl.appendChild(rect);
  });

  arr.forEach((val, idx) => {
    const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    const cls = highlights[idx];
    const fill = cls === 'swap' ? '#f472b6' : cls === 'compare' ? '#38bdf8' : '#0ea5e9';
    const lane = idx >= meta.left && idx <= meta.right ? lanes[2] : lanes[0];
    rect.setAttribute('x', idx * barW + 6);
    rect.setAttribute('y', lane - val * 1.2);
    rect.setAttribute('width', barW - 8);
    rect.setAttribute('height', val * 1.2);
    rect.setAttribute('rx', '6');
    rect.setAttribute('fill', fill);
    overlayEl.appendChild(rect);
  });
}

function drawShellOverlay(step) {
  clearOverlay();
  const { arr, meta, highlights } = step;
  const w = 1100;
  const barW = w / arr.length;

  // Show current gap size visually via horizontal bands and a small label.
  if (meta.gap) {
    const gapBand = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    gapBand.setAttribute('x', 0);
    gapBand.setAttribute('y', 14);
    gapBand.setAttribute('width', w);
    gapBand.setAttribute('height', 34);
    gapBand.setAttribute('rx', '10');
    gapBand.setAttribute('fill', 'rgba(34,197,94,0.12)');
    gapBand.setAttribute('stroke', '#263341');
    overlayEl.appendChild(gapBand);

    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('x', 20);
    text.setAttribute('y', 38);
    text.setAttribute('fill', '#0b1119');
    text.setAttribute('font-size', '14');
    text.setAttribute('font-weight', '700');
    text.textContent = `gap = ${meta.gap}`;
    overlayEl.appendChild(text);
  }

  arr.forEach((val, idx) => {
    const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    const cls = highlights[idx];
    const fill = cls === 'run' ? '#22c55e' : cls === 'swap' ? '#f472b6' : cls === 'compare' ? '#38bdf8' : '#0ea5e9';
    rect.setAttribute('x', idx * barW + 6);
    rect.setAttribute('y', 220 - val * 1.5);
    rect.setAttribute('width', barW - 8);
    rect.setAttribute('height', val * 1.5);
    rect.setAttribute('rx', '6');
    rect.setAttribute('fill', fill);
    overlayEl.appendChild(rect);
  });
}

function renderStep(step) {
  if (!step) return;
  renderBars(step.arr, step.highlights, step.algorithm);
  detailEl.textContent = step.note || '';
  secondaryTitleEl.textContent = step.meta?.title || 'Algorithm View';
  switch (step.algorithm) {
    case 'heap':
      drawHeapTree(step.arr, step.highlights);
      break;
    case 'quick':
      drawQuickOverlay(step);
      break;
    case 'merge':
      drawMergeOverlay(step);
      break;
    case 'shell':
      drawShellOverlay(step);
      break;
    default:
      clearOverlay();
  }
}

function addStep(collection, algorithm, arr, highlights, note, meta = {}) {
  collection.push({ arr: [...arr], highlights: { ...highlights }, note, meta, algorithm });
}

function heapSteps(data) {
  const arr = [...data];
  const steps = [];
  const n = arr.length;

  function heapify(n, i) {
    let largest = i;
    const l = 2 * i + 1;
    const r = 2 * i + 2;

    if (l < n && arr[l] > arr[largest]) largest = l;
    if (r < n && arr[r] > arr[largest]) largest = r;

    addStep(steps, 'heap', arr, { [i]: 'compare', [l]: 'compare', [r]: 'compare' }, `heapify at index ${i}`, {});

    if (largest !== i) {
      [arr[i], arr[largest]] = [arr[largest], arr[i]];
      addStep(steps, 'heap', arr, { [i]: 'swap', [largest]: 'swap' }, `swap ${arr[largest]} ↔ ${arr[i]}`, {});
      heapify(n, largest);
    }
  }

  for (let i = Math.floor(n / 2) - 1; i >= 0; i--) {
    heapify(n, i);
  }

  for (let i = n - 1; i > 0; i--) {
    [arr[0], arr[i]] = [arr[i], arr[0]];
    addStep(steps, 'heap', arr, { 0: 'swap', [i]: 'swap' }, `move max to position ${i}`, {});
    heapify(i, 0);
  }
  return steps;
}

function quickSteps(data) {
  const arr = [...data];
  const steps = [];

  function partition(low, high) {
    const pivot = arr[high];
    let i = low - 1;
    addStep(steps, 'quick', arr, { [high]: 'pivot' }, `pivot = ${pivot}`, { low, high, pivotIndex: high, title: 'Partition' });
    for (let j = low; j < high; j++) {
      addStep(steps, 'quick', arr, { [j]: 'compare', [high]: 'pivot' }, `compare ${arr[j]} with pivot ${pivot}`, { low, high, pivotIndex: high });
      if (arr[j] <= pivot) {
        i++;
        [arr[i], arr[j]] = [arr[j], arr[i]];
        addStep(steps, 'quick', arr, { [i]: 'swap', [j]: 'swap', [high]: 'pivot' }, `swap ${arr[i]} ↔ ${arr[j]}`, { low, high, pivotIndex: high });
      }
    }
    [arr[i + 1], arr[high]] = [arr[high], arr[i + 1]];
    addStep(steps, 'quick', arr, { [i + 1]: 'pivot', [high]: 'swap' }, 'place pivot', { low, high, pivotIndex: i + 1, title: 'Partition' });
    return i + 1;
  }

  function sort(low, high) {
    if (low < high) {
      const pi = partition(low, high);
      sort(low, pi - 1);
      sort(pi + 1, high);
    }
  }

  sort(0, arr.length - 1);
  return steps;
}

function mergeSteps(data) {
  const arr = [...data];
  const steps = [];

  function merge(l, m, r) {
    const left = arr.slice(l, m + 1);
    const right = arr.slice(m + 1, r + 1);
    let i = 0;
    let j = 0;
    let k = l;
    while (i < left.length && j < right.length) {
      const highlights = { [k]: 'compare' };
      addStep(steps, 'merge', arr, highlights, `compare ${left[i]} vs ${right[j]}`, { left: l, mid: m, right: r, title: 'Merging' });
      if (left[i] <= right[j]) {
        arr[k] = left[i];
        i++;
      } else {
        arr[k] = right[j];
        j++;
      }
      addStep(steps, 'merge', arr, { [k]: 'swap' }, `write index ${k}`, { left: l, mid: m, right: r, title: 'Merging' });
      k++;
    }
    while (i < left.length) {
      arr[k] = left[i];
      addStep(steps, 'merge', arr, { [k]: 'swap' }, `flush left ${left[i]}`, { left: l, mid: m, right: r, title: 'Merging' });
      i++; k++;
    }
    while (j < right.length) {
      arr[k] = right[j];
      addStep(steps, 'merge', arr, { [k]: 'swap' }, `flush right ${right[j]}`, { left: l, mid: m, right: r, title: 'Merging' });
      j++; k++;
    }
  }

  function sort(l, r) {
    if (l >= r) return;
    const m = Math.floor((l + r) / 2);
    sort(l, m);
    sort(m + 1, r);
    merge(l, m, r);
  }

  sort(0, arr.length - 1);
  return steps;
}

function shellSteps(data) {
  const arr = [...data];
  const steps = [];

  function record(highlights, note, meta = {}) {
    addStep(steps, 'shell', arr, highlights, note, { ...meta, title: 'Shell Sort' });
  }

  // Knuth gap sequence: 1, 4, 13, 40, ...
  const gaps = [];
  let gap = 1;
  while (gap < arr.length / 3) gap = gap * 3 + 1;
  while (gap >= 1) {
    gaps.push(gap);
    gap = Math.floor(gap / 3);
  }

  for (const gap of gaps) {
    record({}, `start gap ${gap}`, { gap });
    for (let i = gap; i < arr.length; i++) {
      const temp = arr[i];
      let j = i;
      record({ [i]: 'run' }, `consider element ${temp} at index ${i}`, { gap, i });
      while (j >= gap) {
        record({ [j]: 'compare', [j - gap]: 'compare' }, `compare ${arr[j - gap]} and ${temp}`, { gap, i, j });
        if (arr[j - gap] <= temp) break;
        arr[j] = arr[j - gap];
        record({ [j]: 'swap', [j - gap]: 'swap' }, `shift ${arr[j]} to index ${j}`, { gap, i, j });
        j -= gap;
      }
      arr[j] = temp;
      record({ [j]: 'swap' }, `insert ${temp} at index ${j}`, { gap, i, j });
    }
  }

  return steps;
}

function buildSteps(algorithm, data) {
  switch (algorithm) {
    case 'heap': return heapSteps(data);
    case 'quick': return quickSteps(data);
    case 'merge': return mergeSteps(data);
    case 'shell': return shellSteps(data);
    default: return [];
  }
}

function resetPlayback() {
  playing = false;
  stepIndex = 0;
  clearInterval(playHandle);
  playHandle = null;
  statusEl.textContent = 'ready';
}

function showStep(index) {
  const step = steps[index];
  renderStep(step);
  statusEl.textContent = `step ${index + 1} / ${steps.length}`;
}

function play() {
  if (!steps.length) {
    steps = buildSteps(algorithmEl.value, baseArray);
    stepIndex = 0;
  }
  if (!steps.length) return;
  playing = true;
  statusEl.textContent = 'playing';
  const baseSpeed = parseInt(speedEl.value, 10);
  const algorithm = algorithmEl.value;
  const speed = algorithm === 'shell' ? Math.round(baseSpeed * 1.6) : baseSpeed;
  clearInterval(playHandle);
  playHandle = setInterval(() => {
    if (stepIndex >= steps.length) {
      clearInterval(playHandle);
      statusEl.textContent = 'done';
      playing = false;
      return;
    }
    showStep(stepIndex);
    stepIndex++;
  }, speed);
}

function stepOnce() {
  if (!steps.length) {
    steps = buildSteps(algorithmEl.value, baseArray);
    stepIndex = 0;
  }
  if (stepIndex < steps.length) {
    showStep(stepIndex);
    stepIndex++;
  } else {
    statusEl.textContent = 'done';
  }
}

function generateNew() {
  baseArray = randomArray(parseInt(sizeEl.value, 10));
  steps = [];
  stepIndex = 0;
  playing = false;
  clearInterval(playHandle);
  playHandle = null;
  statusEl.textContent = 'ready';
  detailEl.textContent = 'No step yet';
  secondaryTitleEl.textContent = 'Algorithm View';
  renderBars(baseArray, {});
  clearOverlay();
}

function parseCustomArray(text) {
  if (!text.trim()) return null;
  const parts = text.split(/[,\s]+/).filter(Boolean);
  if (!parts.length) return null;
  const nums = parts.map((p) => Number(p));
  if (nums.some((n) => Number.isNaN(n))) return null;
  return nums;
}

function loadCustomArray() {
  const parsed = parseCustomArray(customInputEl.value || '');
  if (!parsed) {
    statusEl.textContent = 'invalid array';
    return;
  }
  baseArray = parsed.map((n) => clamp(Math.round(n), -999, 999));
  steps = [];
  stepIndex = 0;
  playing = false;
  clearInterval(playHandle);
  playHandle = null;
  statusEl.textContent = 'ready (custom)';
  detailEl.textContent = 'No step yet';
  secondaryTitleEl.textContent = 'Algorithm View';
  renderBars(baseArray, {});
  clearOverlay();
}

sizeEl.addEventListener('input', () => {
  sizeValueEl.textContent = sizeEl.value;
});

speedEl.addEventListener('input', () => {
  speedValueEl.textContent = speedEl.value;
  if (playing) {
    play();
  }
});

algorithmEl.addEventListener('change', () => {
  steps = [];
  stepIndex = 0;
  secondaryTitleEl.textContent = 'Algorithm View';
  detailEl.textContent = 'No step yet';
  clearOverlay();
});

loadBtn.addEventListener('click', loadCustomArray);

generateBtn.addEventListener('click', generateNew);
playBtn.addEventListener('click', play);
stepBtn.addEventListener('click', stepOnce);
resetBtn.addEventListener('click', () => {
  resetPlayback();
  renderBars(baseArray, {});
  clearOverlay();
  detailEl.textContent = 'No step yet';
});

generateNew();
