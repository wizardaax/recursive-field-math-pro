// cpu/ternary_cpu_v8.js — Basic ternary CPU implementation
// Provides CPU class and program loading capabilities

import { intToWord, wordToInt, addWords, subWords, andWords, orWords, notWord } from './balanced_ternary_arith.js';
import { assembleLine } from './mini_assembler.js';

export class CPU {
  constructor() {
    this.pc = intToWord(0);
    this.halted = false;
    this.registers = [
      intToWord(0), // r0
      intToWord(0), // r1
      intToWord(0), // r2
      intToWord(0)  // r3
    ];
    this.memory = [];
  }

  loadProgram(program) {
    this.memory = program ? [...program] : [];
    this.pc = intToWord(0);
    this.halted = false;
    
    // Reset registers
    for (let i = 0; i < this.registers.length; i++) {
      this.registers[i] = intToWord(0);
    }
  }

  getRegister(index) {
    if (index >= 0 && index < this.registers.length) {
      return this.registers[index];
    }
    return intToWord(0);
  }

  setRegister(index, value) {
    if (index >= 0 && index < this.registers.length) {
      this.registers[index] = value;
    }
  }

  step() {
    if (this.halted) return;
    
    const pcVal = wordToInt(this.pc);
    if (pcVal >= this.memory.length) {
      this.halted = true;
      return;
    }
    
    const instruction = this.memory[pcVal];
    this.executeInstruction(instruction);
    
    // Increment PC (unless instruction modified it)
    if (!this.halted) {
      this.pc = intToWord(wordToInt(this.pc) + 1);
    }
  }

  executeInstruction(instruction) {
    if (!instruction || !instruction.trits) {
      this.halted = true;
      return;
    }
    
    const trits = instruction.trits;
    
    // Check if this is wide format (op3 != 0) or mini format (op3 == 0)
    const op3 = this.tritsToInt(trits.slice(0, 3));
    
    if (op3 !== 0) {
      this.executeWideInstruction(trits);
    } else {
      this.executeMiniInstruction(trits);
    }
  }

  executeWideInstruction(trits) {
    const opcode = this.tritsToInt(trits.slice(0, 3));
    const ra = this.tritsToInt(trits.slice(3, 6));
    const rb = this.tritsToInt(trits.slice(6, 9)); 
    const imm = this.tritsToInt(trits.slice(9, 12));
    
    switch (opcode) {
      case 1: // ADD
        this.setRegister(ra, addWords(this.getRegister(ra), this.getRegister(rb)));
        break;
      case 2: // SUB
        this.setRegister(ra, subWords(this.getRegister(ra), this.getRegister(rb)));
        break;
      case 3: // AND
        this.setRegister(ra, andWords(this.getRegister(ra), this.getRegister(rb)));
        break;
      case 4: // OR
        this.setRegister(ra, orWords(this.getRegister(ra), this.getRegister(rb)));
        break;
      case -1: // NOT
        this.setRegister(ra, notWord(this.getRegister(ra)));
        break;
      case -2: // LD
        // Load from memory[imm] to register ra
        if (imm >= 0 && imm < this.memory.length) {
          this.setRegister(ra, this.memory[imm]);
        }
        break;
      case -3: // ST
        // Store register ra to memory[imm]
        while (this.memory.length <= imm) {
          this.memory.push(intToWord(0));
        }
        this.memory[imm] = this.getRegister(ra);
        break;
      case -4: // JMP
        this.pc = intToWord(imm);
        return;
      case -5: // JMPREL
        this.pc = intToWord(wordToInt(this.pc) + 1 + imm);
        return;
      case -6: // JNZREL
        if (wordToInt(this.getRegister(ra)) !== 0) {
          this.pc = intToWord(wordToInt(this.pc) + 1 + imm);
          return;
        }
        break;
      default:
        this.halted = true;
        break;
    }
  }

  executeMiniInstruction(trits) {
    // Decode mini format: pairs at [3,4], [5,6], [7,8]
    const opcode = this.pairToNonary(trits[3], trits[4]);
    const ra = this.pairToNonary(trits[5], trits[6]);
    const arg = this.pairToNonary(trits[7], trits[8]);
    
    // Convert opcode to signed value
    let op = opcode;
    if (op > 4) op = op - 9; // Convert to negative range
    
    switch (op) {
      case 1: // ADD
        this.setRegister(ra, addWords(this.getRegister(ra), this.getRegister(arg)));
        break;
      case 2: // SUB
        this.setRegister(ra, subWords(this.getRegister(ra), this.getRegister(arg)));
        break;
      case 3: // AND
        this.setRegister(ra, andWords(this.getRegister(ra), this.getRegister(arg)));
        break;
      case 4: // OR
        this.setRegister(ra, orWords(this.getRegister(ra), this.getRegister(arg)));
        break;
      case -1: // NOT
        this.setRegister(ra, notWord(this.getRegister(ra)));
        break;
      case -2: // LD
        if (arg >= 0 && arg < this.memory.length) {
          this.setRegister(ra, this.memory[arg]);
        }
        break;
      case -3: // ST
        while (this.memory.length <= arg) {
          this.memory.push(intToWord(0));
        }
        this.memory[arg] = this.getRegister(ra);
        break;
      case -4: // MJMP
        this.pc = intToWord(arg);
        return;
      case -5: // MJMPREL
        this.pc = intToWord(wordToInt(this.pc) + 1 + arg);
        return;
      default:
        this.halted = true;
        break;
    }
  }

  tritsToInt(trits) {
    let result = 0;
    let power = 1;
    
    for (let i = 0; i < trits.length; i++) {
      result += (trits[i] || 0) * power;
      power *= 3;
    }
    
    return result;
  }

  pairToNonary(s1, s2) {
    return s2 * 3 + s1;
  }
}

// Export assembler function for compatibility
export function assembleProgram(lines) {
  const words = [];
  for (const line of lines) {
    if (typeof line === 'string') {
      const word = assembleLine(line);
      if (word !== null) {
        words.push(word);
      }
    }
  }
  return words;
}