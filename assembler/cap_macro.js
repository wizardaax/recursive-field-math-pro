// Capability builder macro helper (ESM)
// Usage examples:
//   import { capWord } from './assembler/cap_macro.js';
//   const cap = capWord(10, 10, 'rw');  // base=10, len=10, read+write
//
// In a macro assembler that supports constants/data words, you can emit this value at a label
// and then LD it into a register, or directly seed a register before running.

import { encodeCap } from '../cpu/cap_kit.js';

function parseRW(rw){
  const s = String(rw || 'rw').toLowerCase();
  return {
    read:  s.includes('r'),
    write: s.includes('w'),
  };
}

export function capWord(base, length, rw = 'rw'){
  const { read, write } = parseRW(rw);
  return encodeCap({ base: Number(base), length: Number(length), read, write });
}