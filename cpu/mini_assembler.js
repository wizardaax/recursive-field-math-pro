// cpu/mini_assembler.js — ASCII-safe mini assembler for 12-trit words
// Basic assembler without macros/labels, used as dependency for macro_assembler.js

import { intToWord, wordToTrits, tritsToInt } from './balanced_ternary_arith.js';

// Opcode mappings for wide format (when op3 != 0)
export const OP_MAP = {
  ADD: 1,
  SUB: 2, 
  AND: 3,
  OR: 4,
  NOT: -1,
  LD: -2,
  ST: -3,
  JMP: -4,
  JMPREL: -5
};

// Opcode mappings for mini format (when op3 == 0)
export const MINI_MAP = {
  ADD: 1,
  SUB: 2,
  AND: 3, 
  OR: 4,
  NOT: -1,
  LD: -2,
  ST: -3,
  MJMP: -4,
  MJMPREL: -5
};

const strip = (s) => s.split('//')[0].trim();
const isRegister = (tok) => /^r-?\d+$/i.test(tok);
const parseRegister = (tok) => {
  const match = tok.match(/^r(-?\d+)$/i);
  return match ? parseInt(match[1], 10) : 0;
};
const parseImmediate = (tok) => parseInt(tok, 10) || 0;

// Convert value to pair of trits (using proper balanced ternary)
function valueToPair(val) {
  // For a 2-trit field, we can represent values in range [-4, 4]
  if (val < -4 || val > 4) {
    console.warn(`Warning: Value ${val} clamped to range [-4, 4] for mini format`);
  }
  const clampedVal = Math.max(-4, Math.min(4, val));
  
  // Proper balanced ternary conversion for 2 trits
  let n = clampedVal;
  const trits = [];
  
  for (let i = 0; i < 2; i++) {
    if (n === 0) {
      trits.push(0);
      continue;
    }
    
    const rem = n % 3;
    if (rem === 0) {
      trits.push(0);
      n = Math.floor(n / 3);
    } else if (rem === 1) {
      trits.push(1);
      n = Math.floor(n / 3);
    } else { // rem === 2 or rem === -1 or rem === -2
      trits.push(-1);
      n = Math.floor(n / 3) + 1;
    }
  }
  
  return trits;
}

// Encode word with wide format: [op][ra][rb][imm] (3 trits each)
function encodeWide(op, ra, rb, imm) {
  const trits = new Array(12).fill(0);
  
  // Pack fields into 3-trit segments
  const opTrits = intToTrits(op, 3);
  const raTrits = intToTrits(ra, 3);
  const rbTrits = intToTrits(rb, 3);
  const immTrits = intToTrits(imm, 3);
  
  // Layout: [op:0-2][ra:3-5][rb:6-8][imm:9-11]
  for (let i = 0; i < 3; i++) {
    trits[i] = opTrits[i];
    trits[i + 3] = raTrits[i];
    trits[i + 6] = rbTrits[i];
    trits[i + 9] = immTrits[i];
  }
  
  return new (intToWord(0).constructor)(trits);
}

// Encode word with mini format: op=0, then pairs at [3,4], [5,6], [7,8]
function encodeMini(op, ra, arg) {
  const trits = new Array(12).fill(0);
  
  // op field = 0 (trits 0-2)
  // pairs: [3,4]=op, [5,6]=rA, [7,8]=arg
  const opPair = valueToPair(op);
  const raPair = valueToPair(ra);
  const argPair = valueToPair(arg);
  
  trits[3] = opPair[0];
  trits[4] = opPair[1];
  trits[5] = raPair[0];
  trits[6] = raPair[1];
  trits[7] = argPair[0];
  trits[8] = argPair[1];
  
  return new (intToWord(0).constructor)(trits);
}

function intToTrits(n, numTrits) {
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

// Assemble a single line of assembly
export function assembleLine(line) {
  const cleanLine = strip(line);
  if (!cleanLine) return null;
  
  const tokens = cleanLine.split(/\s+/);
  const op = tokens[0].toUpperCase();
  
  // Check for wide format opcodes
  if (OP_MAP.hasOwnProperty(op)) {
    const opcode = OP_MAP[op];
    
    if (op === 'NOT') {
      // NOT ra
      const ra = isRegister(tokens[1]) ? parseRegister(tokens[1]) : 0;
      return encodeWide(opcode, ra, 0, 0);
    } else if (op === 'LD' || op === 'ST') {
      // LD/ST ra, imm
      const ra = isRegister(tokens[1]) ? parseRegister(tokens[1]) : 0;
      const imm = parseImmediate(tokens[2]);
      return encodeWide(opcode, ra, 0, imm);
    } else if (op === 'JMP' || op === 'JMPREL') {
      // JMP/JMPREL ra, imm
      const ra = isRegister(tokens[1]) ? parseRegister(tokens[1]) : 0;
      const imm = parseImmediate(tokens[2]);
      return encodeWide(opcode, ra, 0, imm);
    } else {
      // Binary ALU: ADD/SUB/AND/OR ra, rb
      const ra = isRegister(tokens[1]) ? parseRegister(tokens[1]) : 0;
      const rb = isRegister(tokens[2]) ? parseRegister(tokens[2]) : 0;
      return encodeWide(opcode, ra, rb, 0);
    }
  }
  
  // Check for mini format opcodes (prefixed with M)
  if (op.startsWith('M') && MINI_MAP.hasOwnProperty(op.substring(1))) {
    const baseOp = op.substring(1);
    const opcode = MINI_MAP[baseOp];
    
    if (baseOp === 'NOT') {
      // MNOT ra, imm
      const ra = isRegister(tokens[1]) ? parseRegister(tokens[1]) : 0;
      const imm = parseImmediate(tokens[2]);
      return encodeMini(opcode, ra, imm);
    } else if (baseOp === 'LD' || baseOp === 'ST') {
      // MLD/MST ra, imm
      const ra = isRegister(tokens[1]) ? parseRegister(tokens[1]) : 0;
      const imm = parseImmediate(tokens[2]);
      return encodeMini(opcode, ra, imm);
    } else if (baseOp === 'JMP' || baseOp === 'JMPREL') {
      // MJMP/MJMPREL ra, imm
      const ra = isRegister(tokens[1]) ? parseRegister(tokens[1]) : 0;
      const imm = parseImmediate(tokens[2]);
      return encodeMini(opcode, ra, imm);
    } else {
      // Binary ALU: MADD/MSUB/MAND/MOR ra, rb
      const ra = isRegister(tokens[1]) ? parseRegister(tokens[1]) : 0;
      const rb = isRegister(tokens[2]) ? parseRegister(tokens[2]) : 0;
      return encodeMini(opcode, ra, rb);
    }
  }
  
  // Check for mini format without M prefix (MJMP, MJMPREL)
  if (MINI_MAP.hasOwnProperty(op)) {
    const opcode = MINI_MAP[op];
    const ra = isRegister(tokens[1]) ? parseRegister(tokens[1]) : 0;
    const arg = parseImmediate(tokens[2]);
    return encodeMini(opcode, ra, arg);
  }
  
  throw new Error(`Unknown instruction: ${op}`);
}

// Assemble an array of assembly lines
export function assembleProgram(lines) {
  const words = [];
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    try {
      const word = assembleLine(line);
      if (word !== null) {
        words.push(word);
      }
    } catch (err) {
      throw new Error(`Line ${i + 1}: ${err.message}`);
    }
  }
  
  return words;
}