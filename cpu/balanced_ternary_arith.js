// Balanced ternary arithmetic + logic for Tri / Word / IOBus (ASCII-safe)
// Storage note: Words store MSB-first internally; adapters expose LSB-first trit arrays.
// This patch adds: fitsInWord, SHL/SHR, and NOP in the ALU.

export const STATES = new Set([-1, 0, 1]);
export const WORD_SIZE = 12;  // total trits per Word

// ---------- helpers ----------
export function fitsInWord(n, width = WORD_SIZE){
  // Signed range for balanced ternary width W is about [- (3^W-1)/2, + (3^W-1)/2 ]
  // We do a strict encode/decode check to be exact for negative corners:
  const t = intToTrits(n, width);
  return tritsToInt(t) === n;
}

class Tri {
  constructor(){ this.state = 0; }
  setState(val){ if (!STATES.has(val)) throw new Error("Invalid trit: " + val); this.state = val; }
  getState(){ return this.state; }
}

class Word {
  constructor(){ this.data = Array.from({ length: WORD_SIZE }, () => new Tri()); }
  readWord(){ return this.data.slice(); }
  writeWord(tris){
    if (tris.length !== WORD_SIZE) throw new Error("Word size mismatch");
    for (let i = 0; i < WORD_SIZE; i++) this.data[i] = tris[i];
  }
}

export class IOBus {
  read(addr){ console.log("IOBus read from " + addr); return new Word(); }
  write(addr, word){ console.log("IOBus write to " + addr); }
}

// normalize sum s to digit/carry
export function normalizeSum(s){
  const carry = Math.round(s / 3);
  const digit = s - 3 * carry;
  if (digit < -1 || digit > 1) throw new Error("normalizeSum overflow: digit not in {-1,0,1}");
  return { digit, carry };
}

// logic (Kleene-style)
export function tnot(a){ return -a; }
export function tand(a, b){ return Math.min(a, b); }
export function tor(a, b){ return Math.max(a, b); }

// int <-> trits (LSB-first array of -1/0/1)
export function intToTrits(n, width = WORD_SIZE){
  if (n === 0) return Array(width).fill(0);
  const out = [];
  let x = n;
  while (x !== 0 && out.length < width){
    let r = ((x % 3) + 3) % 3;
    if (r === 2){ out.push(-1); x = Math.floor((x + 1) / 3); }
    else { out.push(r); x = Math.floor((x - r) / 3); }
  }
  while (out.length < width) out.push(0);
  return out;
}
export function tritsToInt(trits){
  let acc = 0, p = 1;
  for (let i = 0; i < trits.length; i++){ acc += trits[i] * p; p *= 3; }
  return acc;
}

// Word adapters
export function wordToTrits(word){
  // expose LSB-first
  return word.readWord().map(t => t.getState()).reverse();
}
export function tritsToWord(trits){
  const w = new Word();
  const data = w.readWord();
  const msbFirst = trits.slice().reverse();
  for (let i = 0; i < WORD_SIZE; i++) data[i].setState(msbFirst[i] || 0);
  w.writeWord(data);
  return w;
}
export function intToWord(n){
  if (!fitsInWord(n)) throw new Error("Integer out of range for Word: " + n);
  return tritsToWord(intToTrits(n, WORD_SIZE));
}
export function wordToInt(word){ return tritsToInt(wordToTrits(word)); }

// trit arith
export function addTrits(a, b, cin = 0){ return normalizeSum(a + b + cin); }
export function subTrits(a, b, cin = 0){ return addTrits(a, -b, cin); }

// word arith
export function addWords(wordA, wordB){
  const A = wordToTrits(wordA), B = wordToTrits(wordB);
  const out = []; let carry = 0;
  for (let i = 0; i < WORD_SIZE; i++){
    const { digit, carry: c } = addTrits(A[i] || 0, B[i] || 0, carry);
    out.push(digit); carry = c;
  }
  return { word: tritsToWord(out), carry };
}
export function subWords(wordA, wordB){
  const A = wordToTrits(wordA), B = wordToTrits(wordB);
  const out = []; let carry = 0;
  for (let i = 0; i < WORD_SIZE; i++){
    const { digit, carry: c } = subTrits(A[i] || 0, B[i] || 0, carry);
    out.push(digit); carry = c;
  }
  return { word: tritsToWord(out), carry };
}

// word logic
export function andWords(wordA, wordB){
  const A = wordToTrits(wordA), B = wordToTrits(wordB);
  return tritsToWord(A.map((a,i) => tand(a, B[i] || 0)));
}
export function orWords(wordA, wordB){
  const A = wordToTrits(wordA), B = wordToTrits(wordB);
  return tritsToWord(A.map((a,i) => tor(a, B[i] || 0)));
}
export function notWord(word){
  const A = wordToTrits(word);
  return tritsToWord(A.map(t => tnot(t)));
}
export function negWord(word){
  const A = wordToTrits(word);
  return tritsToWord(A.map(t => -t));
}

// shifts (0-fill). Amount read from B (signed int). Positive = left for SHL/right for SHR.
export function shlWord(word, amount){
  let trits = wordToTrits(word);
  if (amount > 0) trits = trits.slice(amount).concat(Array(amount).fill(0));
  else if (amount < 0){ amount = -amount; trits = Array(amount).fill(0).concat(trits.slice(0, -amount)); }
  return tritsToWord(trits.slice(0, WORD_SIZE));
}
export function shrWord(word, amount){
  let trits = wordToTrits(word);
  if (amount > 0) trits = Array(amount).fill(0).concat(trits.slice(0, -amount));
  else if (amount < 0){ amount = -amount; trits = trits.slice(amount).concat(Array(amount).fill(0)); }
  return tritsToWord(trits.slice(0, WORD_SIZE));
}

// ALU facade
export function alu(op, wordA, wordB = null){
  switch (op){
    case 'NOP': return wordA;
    case 'ADD': return addWords(wordA, wordB).word;
    case 'SUB': return subWords(wordA, wordB).word;
    case 'AND': return andWords(wordA, wordB);
    case 'OR':  return orWords(wordA, wordB);
    case 'NOT': return notWord(wordA);
    case 'NEG': return negWord(wordA);
    case 'SHL': return shlWord(wordA, wordToInt(wordB));
    case 'SHR': return shrWord(wordA, wordToInt(wordB));
    default: throw new Error('Unknown ALU op: ' + op);
  }
}

// self-test (kept tiny)
function _selfTest(){
  const a = intToWord(7), b = intToWord(-4);
  const { word: sum } = addWords(a, b);
  if (wordToInt(sum) !== 3) throw new Error('ADD failed');
}
_selfTest();