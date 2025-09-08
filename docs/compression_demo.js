// Compression Demo – live Huffman panel (ASCII-safe, browser ESM)
// Auto-mounts a small demo panel; no external CSS required.

import { buildHuffmanTree, ternaryHuffmanEncode, ternaryHuffmanDecode, DEMO_FREQS } from './compression_backend.js';

function bitsForTrits(tritCount) {
  // Information-theoretic bit weight per trit
  const BITS_PER_TRIT = Math.log2(3); // ~1.5849625
  return tritCount * BITS_PER_TRIT;
}

function formatRatio(bitsTernary, bitsOriginal) {
  if (bitsOriginal <= 0) return '—';
  const ratio = bitsTernary / bitsOriginal;
  const pct = (ratio * 100).toFixed(1);
  const savings = ((1 - ratio) * 100).toFixed(1);
  return `${pct}% of original (${savings}% saved)`;
}

function makePanel() {
  const wrap = document.createElement('section');
  wrap.id = 'huffman-demo';
  wrap.style.border = '1px solid #ccc';
  wrap.style.borderRadius = '6px';
  wrap.style.padding = '12px';
  wrap.style.margin = '12px 0';
  wrap.style.fontFamily = 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace';
  wrap.style.background = '#fafafa';

  const h = document.createElement('h3');
  h.textContent = 'Ternary Huffman – Live Demo';
  h.style.margin = '0 0 8px 0';

  const input = document.createElement('textarea');
  input.id = 'hf-input';
  input.placeholder = 'Type here to encode...';
  input.rows = 3;
  input.style.width = '100%';
  input.style.padding = '8px';
  input.style.boxSizing = 'border-box';
  input.style.margin = '8px 0';

  const stats = document.createElement('div');
  stats.style.display = 'flex';
  stats.style.flexWrap = 'wrap';
  stats.style.gap = '12px';
  stats.style.margin = '8px 0';

  const origBits = document.createElement('span');
  const ternBits = document.createElement('span');
  const ratioEl = document.createElement('span');
  stats.appendChild(origBits);
  stats.appendChild(ternBits);
  stats.appendChild(ratioEl);

  const tritsLabel = document.createElement('div');
  tritsLabel.textContent = 'Encoded trits (-1,0,1):';
  tritsLabel.style.marginTop = '8px';

  const tritsOut = document.createElement('pre');
  tritsOut.id = 'hf-trits';
  tritsOut.style.whiteSpace = 'pre-wrap';
  tritsOut.style.wordBreak = 'break-word';
  tritsOut.style.background = '#f0f0f0';
  tritsOut.style.padding = '8px';
  tritsOut.style.borderRadius = '4px';
  tritsOut.style.margin = '4px 0';

  const decLabel = document.createElement('div');
  decLabel.textContent = 'Decoded preview:';
  decLabel.style.marginTop = '8px';

  const decOut = document.createElement('pre');
  decOut.id = 'hf-decoded';
  decOut.style.whiteSpace = 'pre-wrap';
  decOut.style.wordBreak = 'break-word';
  decOut.style.background = '#f0f0f0';
  decOut.style.padding = '8px';
  decOut.style.borderRadius = '4px';
  decOut.style.margin = '4px 0';

  wrap.appendChild(h);
  wrap.appendChild(input);
  wrap.appendChild(stats);
  wrap.appendChild(tritsLabel);
  wrap.appendChild(tritsOut);
  wrap.appendChild(decLabel);
  wrap.appendChild(decOut);

  return { wrap, input, origBits, ternBits, ratioEl, tritsOut, decOut };
}

function mount(container) {
  const { wrap, input, origBits, ternBits, ratioEl, tritsOut, decOut } = makePanel();
  container.appendChild(wrap);

  const tree = buildHuffmanTree(DEMO_FREQS);

  function render() {
    const text = input.value || '';
    const trits = ternaryHuffmanEncode(text, DEMO_FREQS);
    const decoded = ternaryHuffmanDecode(trits, tree);

    const bitsOrig = text.length * 8;
    const bitsTern = bitsForTrits(trits.length);

    origBits.textContent = `Original: ${bitsOrig} bits (${text.length} chars @ 8 bits/char)`;
    ternBits.textContent = `Ternary: ${trits.length} trits ≈ ${bitsTern.toFixed(1)} bits`;
    ratioEl.textContent = `Ratio: ${formatRatio(bitsTern, bitsOrig)}`;

    // Render trits in compact groups
    const grouped = [];
    for (let i = 0; i < trits.length; i += 48) {
      grouped.push(trits.slice(i, i + 48).join(' '));
    }
    tritsOut.textContent = grouped.join('\n');
    decOut.textContent = decoded;
  }

  input.addEventListener('input', render);
  input.value = 'hello ternary world';
  render();
}

(function bootstrap() {
  const target = document.getElementById('demo-panel') || document.body;
  // Insert at top if using a known demo container, else append to body
  if (target.id === 'demo-panel') {
    mount(target);
  } else {
    const holder = document.createElement('div');
    holder.style.maxWidth = '900px';
    holder.style.margin = '0 auto';
    holder.style.padding = '0 12px';
    document.body.appendChild(holder);
    mount(holder);
  }
})();