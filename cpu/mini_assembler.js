// cpu/mini_assembler.js — Basic assembler for 12-trit words
// Supports both wide and mini instruction formats

import { intToWord, tritsToInt } from './balanced_ternary_arith.js';

// Wide format opcodes (op3 != 0)
export const OP_MAP = {
  ADD: 1,
  SUB: 2, 
  AND: 3,
  OR: 4,
  NOT: -1,
  LD: -2,
  ST: -3,
  JMP: -4,
  JMPREL: -5,
  JNZREL: -6
};

// Mini format opcodes (op3 == 0, encoded in pairs)
export const MINI_MAP = {
  ADD: 1,
  SUB: 2,
  AND: 3, 
  OR: 4,
  NOT: -1,
  LD: -2,
  ST: -3,
  MJMP: -4,
  MJMPREL: -5,
  JNZREL: -6
};

// Parse register name (r0, r1, r-1, etc.)
function parseRegister(token) {
  const match = token.match(/^r(-?\d+)$/i);
  if (!match) throw new Error(`Invalid register: ${token}`);
  return parseInt(match[1], 10);
}

// Parse immediate value or register
function parseOperand(token) {
  if (/^r-?\d+$/i.test(token)) {
    return parseRegister(token);
  }
  if (/^-?\d+$/.test(token)) {
    return parseInt(token, 10);
  }
  throw new Error(`Invalid operand: ${token}`);
}

// Encode trits into a word
function encodeTrits(trits) {
  const paddedTrits = new Array(12).fill(0);
  for (let i = 0; i < Math.min(trits.length, 12); i++) {
    paddedTrits[i] = trits[i] || 0;
  }
  return { trits: paddedTrits };
}

// Encode wide format instruction
function encodeWideInstruction(opcode, ra = 0, rb = 0, imm = 0) {
  const trits = [];
  
  // Encode opcode (3 trits)
  let op = opcode;
  for (let i = 0; i < 3; i++) {
    const remainder = op % 3;
    if (remainder === 0) {
      trits.push(0);
      op = Math.floor(op / 3);
    } else if (remainder === 1) {
      trits.push(1);
      op = Math.floor(op / 3);
    } else {
      trits.push(-1);
      op = Math.floor((op + 1) / 3);
    }
  }
  
  // Encode ra (3 trits)
  let regA = ra;
  for (let i = 0; i < 3; i++) {
    const remainder = regA % 3;
    if (remainder === 0) {
      trits.push(0);
      regA = Math.floor(regA / 3);
    } else if (remainder === 1) {
      trits.push(1);
      regA = Math.floor(regA / 3);
    } else {
      trits.push(-1);
      regA = Math.floor((regA + 1) / 3);
    }
  }
  
  // Encode rb (3 trits)
  let regB = rb;
  for (let i = 0; i < 3; i++) {
    const remainder = regB % 3;
    if (remainder === 0) {
      trits.push(0);
      regB = Math.floor(regB / 3);
    } else if (remainder === 1) {
      trits.push(1);
      regB = Math.floor(regB / 3);
    } else {
      trits.push(-1);
      regB = Math.floor((regB + 1) / 3);
    }
  }
  
  // Encode immediate (3 trits)
  let immediate = imm;
  for (let i = 0; i < 3; i++) {
    const remainder = immediate % 3;
    if (remainder === 0) {
      trits.push(0);
      immediate = Math.floor(immediate / 3);
    } else if (remainder === 1) {
      trits.push(1);
      immediate = Math.floor(immediate / 3);
    } else {
      trits.push(-1);
      immediate = Math.floor((immediate + 1) / 3);
    }
  }
  
  return encodeTrits(trits);
}

// Encode mini format instruction (op3 = 0, use pairs)
function encodeMiniInstruction(opcode, ra = 0, arg = 0) {
  const trits = [0, 0, 0]; // op3 = 0 for mini format
  
  // Encode mini opcode as pair at positions [3,4]
  const opPair = encodePair(opcode);
  trits.push(opPair[0], opPair[1]);
  
  // Encode register as pair at positions [5,6]
  const raPair = encodePair(ra);
  trits.push(raPair[0], raPair[1]);
  
  // Encode argument as pair at positions [7,8]
  const argPair = encodePair(arg);
  trits.push(argPair[0], argPair[1]);
  
  // Pad remaining trits
  while (trits.length < 12) trits.push(0);
  
  return encodeTrits(trits);
}

// Encode value as a pair of trits (nonary encoding)
function encodePair(value) {
  let val = value;
  const s1 = val % 3;
  val = Math.floor(val / 3);
  const s2 = val % 3;
  return [s1, s2];
}

// Assemble a single line of assembly
export function assembleLine(line) {
  const trimmed = line.trim();
  if (!trimmed || trimmed.startsWith('//')) return null;
  
  const parts = trimmed.replace(/,/g, ' ').split(/\s+/).filter(Boolean);
  if (parts.length === 0) return null;
  
  const op = parts[0].toUpperCase();
  
  // Check for mini-specific instructions first (MJMP, MJMPREL)
  if (MINI_MAP[op] !== undefined && (op === 'MJMP' || op === 'MJMPREL')) {
    const opcode = MINI_MAP[op];
    const ra = parts[1] ? parseRegister(parts[1]) : 0;
    const arg = parts[2] ? parseOperand(parts[2]) : 0;
    return encodeMiniInstruction(opcode, ra, arg);
  }

  // Wide format instructions
  if (OP_MAP[op] !== undefined) {
    const opcode = OP_MAP[op];
    
    if (op === 'NOT') {
      const ra = parts[1] ? parseRegister(parts[1]) : 0;
      return encodeWideInstruction(opcode, ra, 0, 0);
    }
    
    if (op === 'LD' || op === 'ST') {
      const ra = parts[1] ? parseRegister(parts[1]) : 0;
      const imm = parts[2] ? parseOperand(parts[2]) : 0;
      return encodeWideInstruction(opcode, ra, 0, imm);
    }
    
    if (op === 'JMP' || op === 'JMPREL' || op === 'JNZREL') {
      const ra = parts[1] ? parseRegister(parts[1]) : 0;
      const imm = parts[2] ? parseOperand(parts[2]) : 0;
      return encodeWideInstruction(opcode, ra, 0, imm);
    }
    
    // Binary ALU operations
    const ra = parts[1] ? parseRegister(parts[1]) : 0;
    const rb = parts[2] ? parseRegister(parts[2]) : 0;
    return encodeWideInstruction(opcode, ra, rb, 0);
  }
  
  // Mini format instructions (with M prefix or direct mini names)
  const miniOp = op.startsWith('M') ? op.substring(1) : op;
  if (MINI_MAP[miniOp] !== undefined) {
    const opcode = MINI_MAP[miniOp];
    const ra = parts[1] ? parseRegister(parts[1]) : 0;
    const arg = parts[2] ? parseOperand(parts[2]) : 0;
    return encodeMiniInstruction(opcode, ra, arg);
  }
  
  throw new Error(`Unknown instruction: ${op}`);
}

// Assemble multiple lines
export async function assembleProgram(lines) {
  const words = [];
  for (const line of lines) {
    const word = assembleLine(line);
    if (word !== null) {
      words.push(word);
    }
  }
  return words;
}