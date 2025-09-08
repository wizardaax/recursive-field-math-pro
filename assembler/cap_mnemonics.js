// Assembler / Disassembler helpers for CLD/CST (CHERI-lite), ESM-friendly
// Encodes 12-trit instruction: [op(3), regA(3), regB(3), imm(3)] in LSB-first field order.
// Notes:
// - 3-trit signed range is [-13..+13]; imm outside this range cannot be encoded in this narrow format.
// - These helpers are additive. You can integrate them with your assembler or use directly.

import { intToTrits, tritsToWord, wordToTrits, tritsToInt } from '../cpu/balanced_ternary_arith.js';

// Keep in sync with ternary_cpu_v9.js
export const OP_CLD = -5; // regA = *(imm) guarded by cap in regB
export const OP_CST = -6; // *(imm) = regA  guarded by cap in regB

function fits3(n){
  const t = intToTrits(n, 3);
  return tritsToInt(t) === n;
}
function encodeField3(n, name){
  if (!fits3(n)) throw new Error(`${name} does not fit 3 trits: ${n}`);
  return intToTrits(n, 3);
}
export function encodeInstrWord(op, regA, regB, imm){
  const t = [
    ...encodeField3(op, 'op'),
    ...encodeField3(regA, 'regA'),
    ...encodeField3(regB, 'regB'),
    ...encodeField3(imm, 'imm'),
  ];
  return tritsToWord(t);
}

function parseReg(token){
  // accepts r0, r1, r2, ...
  const m = /^r(-?\d+)$/.exec(String(token).trim());
  if (!m) throw new Error(`Bad register: ${token}`);
  return Number(m[1]);
}

// Mnemonics: "CLD rA rB IMM" and "CST rA rB IMM"
export function assembleCLD(rA, rB, imm){
  return encodeInstrWord(OP_CLD, parseReg(rA), parseReg(rB), Number(imm));
}
export function assembleCST(rA, rB, imm){
  return encodeInstrWord(OP_CST, parseReg(rA), parseReg(rB), Number(imm));
}

// Minimal disassembler for the two ops. Returns { opName, ra, rb, imm } or null if not CLD/CST.
export function disassembleCap(word){
  const T = wordToTrits(word); // LSB-first
  const op   = tritsToInt(T.slice(0,3));
  const ra   = tritsToInt(T.slice(3,6));
  const rb   = tritsToInt(T.slice(6,9));
  const imm  = tritsToInt(T.slice(9,12));
  if (op === OP_CLD) return { opName: 'CLD', ra, rb, imm };
  if (op === OP_CST) return { opName: 'CST', ra, rb, imm };
  return null;
}

// Optional convenience: parse a single CLD/CST line like "CLD r0 r1 12"
export function assembleLine(line){
  const parts = String(line).trim().split(/\s+/);
  const op = parts[0]?.toUpperCase();
  if (op === 'CLD') return assembleCLD(parts[1], parts[2], parts[3]);
  if (op === 'CST') return assembleCST(parts[1], parts[2], parts[3]);
  throw new Error('assembleLine only supports CLD/CST');
}