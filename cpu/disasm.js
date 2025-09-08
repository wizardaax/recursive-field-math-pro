// cpu/disasm.js — ASCII-safe disassembler for 12-trit words.
// Decodes both wide (4×3-trit fields) and mini (3×pairs) formats.
// Heuristics:
//   - wide if op3 != 0; mini if op3 == 0
//   - mini op/reg/arg come from pairs: [3,4], [5,6], [7,8] (LSB-first trit order)
//
// Tries to import opcode maps from mini_assembler; falls back to defaults.

import { wordToTrits, tritsToInt } from './balanced_ternary_arith.js';

let OP_MAP = null, MINI_MAP = null;
try {
  const tbl = await import('./mini_assembler.js');
  OP_MAP   = tbl.OP_MAP   || null;
  MINI_MAP = tbl.MINI_MAP || null;
} catch { /* fallback below */ }

const DEFAULT_OP = { ADD:1, SUB:2, AND:3, OR:4, NOT:-1, LD:-2, ST:-3, JMP:-4, JMPREL:-5 };
const DEFAULT_MINI = { ADD:1, SUB:2, AND:3, OR:4, NOT:-1, LD:-2, ST:-3, MJMP:-4, MJMPREL:-5 };

function invert(obj){
  const out = {};
  for (const k of Object.keys(obj)) out[obj[k]] = k;
  return out;
}

const REV_WIDE = invert(OP_MAP || DEFAULT_OP);
const REV_MINI = invert(MINI_MAP || DEFAULT_MINI);

const pairToNonary = (s1,s2) => s2*3 + s1;   // s1 = lower-index trit, s2 = next trit

export function disasmWord(word, { pc=0 } = {}){
  const T = wordToTrits(word);           // LSB-first: [0..11]
  const op3 = tritsToInt(T.slice(0,3));  // wide opcode field

  if (op3 !== 0){
    // WIDE: [op][ra][rb][imm]
    const ra  = tritsToInt(T.slice(3,6));
    const rb  = tritsToInt(T.slice(6,9));
    const imm = tritsToInt(T.slice(9,12));
    const name = REV_WIDE[op3] || `OP(${op3})`;

    if (name === 'JMPREL'){
      const tgt = pc + 1 + imm;
      return `JMPREL r${ra} ${imm}    ; -> ${tgt}`;
    }
    if (name === 'JMP'){
      return `JMP r${ra} ${imm}`;
    }
    if (['NOT'].includes(name)){
      return `${name} r${ra}`;
    }
    if (['LD','ST'].includes(name)){
      return `${name} r${ra} ${imm}`;
    }
    // binary ALU
    return `${name} r${ra} r${rb}`;
  }

  // MINI (OP==0): pairs at [3,4]=op, [5,6]=rA, [7,8]=arg
  const mOp  = pairToNonary(T[3], T[4]);
  const mRA  = pairToNonary(T[5], T[6]);
  const mArg = pairToNonary(T[7], T[8]);
  const mName = REV_MINI[mOp] || `MOP(${mOp})`;

  // Heuristic: ALU ops take RB, control/mem use IMM; REL jumps annotate
  if (mName === 'MJMPREL'){
    const tgt = pc + 1 + mArg;
    return `MJMPREL r${mRA} ${mArg}   ; -> ${tgt}`;
  }
  if (mName === 'MJMP'){
    return `MJMP r${mRA} ${mArg}`;
  }
  if (['LD','ST','NOT'].includes(mName)){
    return `M${mName} r${mRA} ${mArg}`;
  }
  return `M${mName} r${mRA} r${mArg}`;
}

export function disasmProgram(words){
  const out = [];
  for (let i=0;i<words.length;i++){
    out.push(`${i.toString().padStart(4,' ')}: ${disasmWord(words[i],{pc:i})}`);
  }
  return out;
}