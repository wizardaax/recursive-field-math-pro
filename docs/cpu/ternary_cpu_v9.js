// Ternary CPU v9 – wide/mini ready, now with CLD/CST (CHERI-lite) and ECC RAM
// If you already have v8, you can rename this to v8 or add alongside and import this one in the REPL.

import {
  intToWord, wordToInt, wordToTrits, tritsToInt, alu
} from './balanced_ternary_arith.js';
import { checkCapLoad, checkCapStore } from './cap_kit.js';

const OP_ADD =  1;
const OP_SUB =  2;
const OP_AND =  3;
const OP_OR  =  4;
const OP_NOT = -1;
const OP_LD  = -2;
const OP_ST  = -3;
const OP_JMP = -4;
// new wide-only capability ops:
const OP_CLD = -5;  // regA = *(addr) guarded by cap in regB
const OP_CST = -6;  // *(addr) = regA guarded by cap in regB
// optional shifts if you wired them in ALU:
const OP_SHL =  5;
const OP_SHR =  6;

export class CPU {
  constructor({ memorySize = 64, regCount = 4 } = {}){
    this.regCount = regCount;
    this.pc = intToWord(0);
    this.registers = Array.from({length: regCount}, () => intToWord(0));
    this.memory = Array.from({length: memorySize},  () => intToWord(0));
    this.halted = false;

    // ECC: store simple parity per address (sum of trits mod 3)
    this._ecc = new Map();
    for (let i=0;i<memorySize;i++) this._writeMem(i, intToWord(0));
  }
  _parity(word){
    return wordToTrits(word).reduce((a,b) => a+b, 0);
  }
  _checkECC(addr, word){
    const p = ((this._parity(word) % 3)+3)%3;
    const ref = this._ecc.get(addr) || 0;
    if (p !== ref) {
      throw new Error(`ECC fault @${addr}: saw ${p}, expected ${ref}`);
    }
  }
  _writeMem(addr, word){
    this.memory[addr] = word;
    this._ecc.set(addr, ((this._parity(word) % 3)+3)%3);
  }

  _regIndex(x){ const m = this.regCount; return ((x % m) + m) % m; }

  fetch(){
    const addr = wordToInt(this.pc);
    if (addr < 0 || addr >= this.memory.length){ this.halted = true; return intToWord(0); }
    return this.memory[addr];
  }

  decode(instrWord){
    const T = wordToTrits(instrWord);  // LSB-first
    const op   = tritsToInt(T.slice(0,3));
    const regA = tritsToInt(T.slice(3,6));
    const regB = tritsToInt(T.slice(6,9));
    const imm  = tritsToInt(T.slice(9,12));
    // Mini-tag alternative (OP==0 => treat pairs as nonary) — keep if you already use it
    const mini = (op === 0);
    if (mini){
      const nonary = (i) => 3*tritsToInt(T.slice(i, i+3)) + tritsToInt(T.slice(i+3, i+6)); // two 3-trit fields
      const mop = nonary(0);          // [-4..+4]
      const ra  = nonary(6);
      const im  = nonary(12); // NOTE: with 12 trits total, this line is illustrative; keep your v8 mini decoder if different.
      return { op: mop, regA: ra, regB: 0, imm: im, mini: true };
    }
    return { op, regA, regB, imm, mini: false };
  }

  execute(d){
    const { op, regA, regB, imm, mini } = d;
    const ra = this._regIndex(regA), rb = this._regIndex(regB);
    const A = this.registers[ra], B = this.registers[rb];
    const nextPC = wordToInt(this.pc) + 1;

    const wrap = (addr) => ((imm % this.memory.length) + this.memory.length) % this.memory.length;

    try {
      switch (op){
        case OP_ADD: this.registers[ra] = alu('ADD', A, B); this.pc = intToWord(nextPC); break;
        case OP_SUB: this.registers[ra] = alu('SUB', A, B); this.pc = intToWord(nextPC); break;
        case OP_AND: this.registers[ra] = alu('AND', A, B); this.pc = intToWord(nextPC); break;
        case OP_OR:  this.registers[ra] = alu('OR',  A, B); this.pc = intToWord(nextPC); break;
        case OP_NOT: this.registers[ra] = alu('NOT', A);    this.pc = intToWord(nextPC); break;
        case OP_SHL: this.registers[ra] = alu('SHL', A, B); this.pc = intToWord(nextPC); break;
        case OP_SHR: this.registers[ra] = alu('SHR', A, B); this.pc = intToWord(nextPC); break;

        case OP_LD: {
          const addr = wrap(imm);
          const w = this.memory[addr];
          this._checkECC(addr, w);
          this.registers[ra] = w;
          this.pc = intToWord(nextPC);
          break;
        }
        case OP_ST: {
          const addr = wrap(imm);
          this._writeMem(addr, A);
          this.pc = intToWord(nextPC);
          break;
        }

        // Capability-checked memory access (capability is in regB)
        case OP_CLD: {
          const addr = imm;
          if (!checkCapLoad(B, addr)) throw new Error(`Capability load violation @${addr}`);
          const a = ((addr % this.memory.length)+this.memory.length)%this.memory.length;
          const w = this.memory[a];
          this._checkECC(a, w);
          this.registers[ra] = w;
          this.pc = intToWord(nextPC);
          break;
        }
        case OP_CST: {
          const addr = imm;
          if (!checkCapStore(B, addr)) throw new Error(`Capability store violation @${addr}`);
          const a = ((addr % this.memory.length)+this.memory.length)%this.memory.length;
          this._writeMem(a, A);
          this.pc = intToWord(nextPC);
          break;
        }

        case OP_JMP:
          this.pc = (wordToInt(A) !== 0) ? intToWord(imm) : intToWord(nextPC);
          break;

        default: this.halted = true; break;
      }
    } catch (e){
      // Fault path—halt cleanly with message
      this.halted = true;
      console.error(String(e));
    }

    const pcInt = wordToInt(this.pc);
    if (pcInt < 0 || pcInt >= this.memory.length) this.halted = true;
  }

  step(){ if (this.halted) return; this.execute(this.decode(this.fetch())); }
  run(maxSteps = 1000){ let n=0; while(!this.halted && n<maxSteps){ this.step(); n++; } }

  loadProgram(wordsOrInts){ 
    this.pc = intToWord(0); this.halted = false;
    for (let i=0; i<wordsOrInts.length && i<this.memory.length; i++){
      const val = (typeof wordsOrInts[i] === 'number') ? intToWord(wordsOrInts[i]) : wordsOrInts[i];
      this._writeMem(i, val);
    }
  }
}

// light self-check
function _selfTest(){
  const cpu = new CPU({ memorySize: 16 });
  cpu.registers[0] = intToWord(5);
  cpu.registers[1] = intToWord(3);
  // Simple ADD test: should add R0 + R1 -> R0
  // Encode: op=1, regA=0, regB=1, imm=0 in balanced ternary
  const addInstr = intToWord(OP_ADD + (0 * 27) + (1 * 729) + (0 * 19683)); // op + regA*3^3 + regB*3^6 + imm*3^9
  cpu._writeMem(0, addInstr);
  cpu.step();
  if (wordToInt(cpu.registers[0]) !== 8) throw new Error('CPU self-test failed');
}
_selfTest();