// cpu/balanced_ternary_arith.js — ASCII-safe balanced ternary arithmetic
// Core module providing conversion between integers and balanced ternary words
// Used by other CPU modules for encoding/decoding instructions

const MAX_TRITS = 12;  // 12-trit words
const TRIT_VALUES = [-1, 0, 1];

// Convert an integer to balanced ternary representation (array of trits)
export function intToTrits(n, numTrits = MAX_TRITS) {
  const trits = [];
  let val = Math.floor(n);
  
  for (let i = 0; i < numTrits; i++) {
    if (val === 0) {
      trits.push(0);
      continue;
    }
    
    const rem = val % 3;
    if (rem === 0) {
      trits.push(0);
      val = Math.floor(val / 3);
    } else if (rem === 1) {
      trits.push(1);
      val = Math.floor(val / 3);
    } else { // rem === 2
      trits.push(-1);
      val = Math.floor(val / 3) + 1;
    }
  }
  
  return trits;
}

// Convert balanced ternary trits to integer
export function tritsToInt(trits) {
  let result = 0;
  let power = 1;
  
  for (let i = 0; i < trits.length; i++) {
    result += trits[i] * power;
    power *= 3;
  }
  
  return result;
}

// Word object representing a 12-trit balanced ternary value
export class Word {
  constructor(trits = null) {
    if (trits === null) {
      this.trits = new Array(MAX_TRITS).fill(0);
    } else if (Array.isArray(trits)) {
      this.trits = trits.slice(0, MAX_TRITS);
      while (this.trits.length < MAX_TRITS) {
        this.trits.push(0);
      }
    } else {
      throw new Error('Word constructor expects array of trits or null');
    }
  }
  
  toInt() {
    return tritsToInt(this.trits);
  }
  
  static fromInt(n) {
    return new Word(intToTrits(n, MAX_TRITS));
  }
}

// Convert integer to Word object
export function intToWord(n) {
  return Word.fromInt(n);
}

// Convert Word object to integer
export function wordToInt(word) {
  if (word && word.trits) {
    return word.toInt();
  }
  if (word && typeof word._n === 'number') {
    return word._n; // fallback for stub format
  }
  return 0;
}

// Convert Word to array of trits (LSB first)
export function wordToTrits(word) {
  if (word && word.trits) {
    return word.trits.slice();
  }
  // Fallback for other formats
  return intToTrits(wordToInt(word), MAX_TRITS);
}

// Arithmetic operations
export function addWords(a, b) {
  return intToWord(wordToInt(a) + wordToInt(b));
}

export function subWords(a, b) {
  return intToWord(wordToInt(a) - wordToInt(b));
}

export function andWords(a, b) {
  const aTrits = wordToTrits(a);
  const bTrits = wordToTrits(b);
  const result = [];
  
  for (let i = 0; i < MAX_TRITS; i++) {
    // Balanced ternary AND: min(a, b)
    result.push(Math.min(aTrits[i], bTrits[i]));
  }
  
  return new Word(result);
}

export function orWords(a, b) {
  const aTrits = wordToTrits(a);
  const bTrits = wordToTrits(b);
  const result = [];
  
  for (let i = 0; i < MAX_TRITS; i++) {
    // Balanced ternary OR: max(a, b)
    result.push(Math.max(aTrits[i], bTrits[i]));
  }
  
  return new Word(result);
}

export function notWord(a) {
  const aTrits = wordToTrits(a);
  const result = [];
  
  for (let i = 0; i < MAX_TRITS; i++) {
    // Balanced ternary NOT: -a
    result.push(-aTrits[i]);
  }
  
  return new Word(result);
}