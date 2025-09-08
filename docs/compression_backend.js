// Compression Backend – Ternary Huffman Encoder (ASCII-safe)
// Balanced trit Huffman tree for ternary codes, prefix-free, encode/decode strings to trit array {-1,0,1}*
// Browser-friendly ESM for the demo panel

// Build a ternary (3-ary) Huffman tree. Pads with zero-frequency dummies so (n-1) % 2 == 0.
export function buildHuffmanTree(freqs) {
  const nodes = Object.entries(freqs).map(([char, freq]) => ({
    char,
    freq: Number(freq) || 0,
    left: null,
    mid: null,
    right: null
  }));

  // If no symbols, return a trivial empty node
  if (nodes.length === 0) {
    return { char: null, freq: 0, left: null, mid: null, right: null };
  }

  // For ternary Huffman, ensure (N - 1) % 2 == 0 by padding with dummies
  while ((nodes.length - 1) % 2 !== 0) {
    nodes.push({ char: null, freq: 0, left: null, mid: null, right: null });
  }

  // Deterministic tie-break: sort by freq asc, then by char asc (null last)
  const sortNodes = (arr) => {
    arr.sort((a, b) => {
      if (a.freq !== b.freq) return a.freq - b.freq;
      const ak = a.char === null ? '\x7f' : String(a.char);
      const bk = b.char === null ? '\x7f' : String(b.char);
      return ak < bk ? -1 : ak > bk ? 1 : 0;
    });
  };

  while (nodes.length > 1) {
    sortNodes(nodes);
    const group = nodes.splice(0, 3);
    // If fewer than 3 remain due to edge cases, pad locally
    while (group.length < 3) {
      group.push({ char: null, freq: 0, left: null, mid: null, right: null });
    }
    const [left, mid, right] = group;
    const parent = {
      char: null,
      freq: (left.freq || 0) + (mid.freq || 0) + (right.freq || 0),
      left, mid, right
    };
    nodes.push(parent);
  }
  return nodes[0];
}

function generateCodes(tree, prefix = []) {
  // Leaf detected by non-null char
  if (tree && tree.char !== null) return [{ char: tree.char, code: prefix }];
  const codes = [];
  if (tree && tree.left) codes.push(...generateCodes(tree.left, [...prefix, -1]));
  if (tree && tree.mid)  codes.push(...generateCodes(tree.mid,  [...prefix,  0]));
  if (tree && tree.right)codes.push(...generateCodes(tree.right,[...prefix,  1]));
  return codes;
}

export function ternaryHuffmanEncode(str, freqs) {
  const tree = buildHuffmanTree(freqs);
  const codeMap = generateCodes(tree).reduce((map, { char, code }) => {
    map[char] = code;
    return map;
  }, {});
  const encoded = [];
  for (const ch of str) {
    const code = codeMap[ch];
    if (!code) continue; // skip unknown chars (not in freqs)
    for (let i = 0; i < code.length; i++) encoded.push(code[i]);
  }
  return encoded; // array of -1/0/1
}

export function ternaryHuffmanDecode(trits, tree) {
  let decoded = '';
  let node = tree;
  for (let i = 0; i < trits.length; i++) {
    const t = trits[i];
    if (t === -1) node = node.left;
    else if (t === 0) node = node.mid;
    else node = node.right;
    if (!node) break; // malformed stream
    if (node.char !== null) {
      decoded += node.char;
      node = tree;
    }
  }
  return decoded;
}

// Example freqs for demo (English-ish)
export const DEMO_FREQS = {
  ' ': 0.182, 'e': 0.102, 't': 0.075, 'a': 0.064, 'o': 0.062, 'i': 0.057, 'n': 0.057, 's': 0.051, 'r': 0.05, 'h': 0.05,
  'd': 0.036, 'l': 0.033, 'u': 0.023, 'c': 0.022, 'm': 0.02,  'f': 0.019, 'w': 0.017, 'g': 0.016, 'y': 0.016, 'p': 0.015,
  'b': 0.012, 'v': 0.008, 'k': 0.006, 'x': 0.001, 'q': 0.001, 'j': 0.001, 'z': 0.001
};