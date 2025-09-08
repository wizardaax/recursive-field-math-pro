// cpu/balanced_ternary_arith.js — Basic balanced ternary arithmetic operations
// Provides word/trit conversion functions and basic arithmetic

// Convert integer to balanced ternary word (12 trits, LSB first)
export function intToWord(n) {
  const trits = [];
  let value = Math.floor(n);
  
  // Convert to balanced ternary (-1, 0, 1)
  for (let i = 0; i < 12; i++) {
    const remainder = value % 3;
    if (remainder === 0) {
      trits.push(0);
      value = Math.floor(value / 3);
    } else if (remainder === 1) {
      trits.push(1);
      value = Math.floor(value / 3);
    } else { // remainder === 2
      trits.push(-1);
      value = Math.floor((value + 1) / 3);
    }
  }
  
  return { trits: trits };
}

// Convert balanced ternary word to integer
export function wordToInt(word) {
  if (!word || !word.trits) return 0;
  
  let result = 0;
  let power = 1;
  
  for (let i = 0; i < word.trits.length; i++) {
    result += word.trits[i] * power;
    power *= 3;
  }
  
  return result;
}

// Convert word to trits array (LSB first)
export function wordToTrits(word) {
  if (!word || !word.trits) return new Array(12).fill(0);
  return word.trits.slice(0, 12);
}

// Convert trits array to integer value
export function tritsToInt(trits) {
  let result = 0;
  let power = 1;
  
  for (let i = 0; i < trits.length; i++) {
    result += (trits[i] || 0) * power;
    power *= 3;
  }
  
  return result;
}

// Basic arithmetic operations
export function addWords(a, b) {
  return intToWord(wordToInt(a) + wordToInt(b));
}

export function subWords(a, b) {
  return intToWord(wordToInt(a) - wordToInt(b));
}

export function andWords(a, b) {
  return intToWord(wordToInt(a) & wordToInt(b));
}

export function orWords(a, b) {
  return intToWord(wordToInt(a) | wordToInt(b));
}

export function notWord(a) {
  return intToWord(~wordToInt(a));
}