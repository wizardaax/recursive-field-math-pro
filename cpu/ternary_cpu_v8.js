// cpu/ternary_cpu_v8.js — ASCII-safe ternary CPU implementation
// 12-trit balanced ternary CPU with registers and instruction execution

import { 
  intToWord, 
  wordToInt, 
  wordToTrits, 
  tritsToInt,
  addWords,
  subWords,
  andWords,
  orWords,
  notWord
} from './balanced_ternary_arith.js';

// CPU with 4 registers (r0-r3) and program counter
export class CPU {
  constructor() {
    this.registers = [
      intToWord(0), // r0
      intToWord(0), // r1  
      intToWord(0), // r2
      intToWord(0)  // r3
    ];
    this.pc = intToWord(0);
    this.memory = new Map(); // address -> word
    this.program = [];
    this.halted = false;
  }
  
  // Load program into memory starting at address 0
  loadProgram(words) {
    this.program = words.slice();
    this.memory.clear();
    
    // Load program into memory
    for (let i = 0; i < words.length; i++) {
      this.memory.set(i, words[i]);
    }
    
    this.pc = intToWord(0);
    this.halted = false;
  }
  
  // Get register value
  getReg(index) {
    if (index >= 0 && index < this.registers.length) {
      return this.registers[index];
    }
    return intToWord(0);
  }
  
  // Set register value
  setReg(index, value) {
    if (index >= 0 && index < this.registers.length) {
      this.registers[index] = value;
    }
  }
  
  // Memory load
  load(address) {
    const addr = wordToInt(address);
    return this.memory.get(addr) || intToWord(0);
  }
  
  // Memory store
  store(address, value) {
    const addr = wordToInt(address);
    this.memory.set(addr, value);
  }
  
  // Execute one instruction
  step() {
    if (this.halted) return;
    
    const pcVal = wordToInt(this.pc);
    const instruction = this.memory.get(pcVal);
    
    if (!instruction) {
      this.halted = true;
      return;
    }
    
    // Decode instruction
    const trits = wordToTrits(instruction);
    const op3 = tritsToInt(trits.slice(0, 3));
    
    // Advance PC
    this.pc = intToWord(pcVal + 1);
    
    if (op3 !== 0) {
      // Wide format: [op][ra][rb][imm]
      const ra = tritsToInt(trits.slice(3, 6));
      const rb = tritsToInt(trits.slice(6, 9));
      const imm = tritsToInt(trits.slice(9, 12));
      
      this.executeWide(op3, ra, rb, imm);
    } else {
      // Mini format: pairs at [3,4], [5,6], [7,8]
      const mOp = this.pairToValue(trits[3], trits[4]);
      const mRA = this.pairToValue(trits[5], trits[6]);
      const mArg = this.pairToValue(trits[7], trits[8]);
      
      this.executeMini(mOp, mRA, mArg);
    }
  }
  
  pairToValue(s1, s2) {
    return s1 + s2 * 3;
  }
  
  executeWide(op, ra, rb, imm) {
    switch (op) {
      case 1: // ADD
        this.setReg(ra, addWords(this.getReg(ra), this.getReg(rb)));
        break;
      case 2: // SUB
        this.setReg(ra, subWords(this.getReg(ra), this.getReg(rb)));
        break;
      case 3: // AND
        this.setReg(ra, andWords(this.getReg(ra), this.getReg(rb)));
        break;
      case 4: // OR
        this.setReg(ra, orWords(this.getReg(ra), this.getReg(rb)));
        break;
      case -1: // NOT
        this.setReg(ra, notWord(this.getReg(ra)));
        break;
      case -2: // LD
        this.setReg(ra, this.load(intToWord(imm)));
        break;
      case -3: // ST
        this.store(intToWord(imm), this.getReg(ra));
        break;
      case -4: // JMP
        this.pc = intToWord(imm);
        break;
      case -5: // JMPREL
        const newPC = wordToInt(this.pc) + imm;
        this.pc = intToWord(newPC);
        break;
      default:
        this.halted = true;
    }
  }
  
  executeMini(op, ra, arg) {
    switch (op) {
      case 1: // ADD
        this.setReg(ra, addWords(this.getReg(ra), this.getReg(arg)));
        break;
      case 2: // SUB
        this.setReg(ra, subWords(this.getReg(ra), this.getReg(arg)));
        break;
      case 3: // AND
        this.setReg(ra, andWords(this.getReg(ra), this.getReg(arg)));
        break;
      case 4: // OR
        this.setReg(ra, orWords(this.getReg(ra), this.getReg(arg)));
        break;
      case -1: // NOT
        this.setReg(ra, notWord(this.getReg(ra)));
        break;
      case -2: // LD
        this.setReg(ra, this.load(intToWord(arg)));
        break;
      case -3: // ST
        this.store(intToWord(arg), this.getReg(ra));
        break;
      case -4: // MJMP
        this.pc = intToWord(arg);
        break;
      case -5: // MJMPREL
        const newPC = wordToInt(this.pc) + arg;
        this.pc = intToWord(newPC);
        break;
      default:
        this.halted = true;
    }
  }
  
  // Get CPU state for debugging
  getState() {
    return {
      pc: wordToInt(this.pc),
      halted: this.halted,
      registers: this.registers.map(wordToInt),
      memorySize: this.memory.size
    };
  }
}