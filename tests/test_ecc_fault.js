// ECC fault: corrupt memory after ECC is recorded and verify load halts with ECC fault.
import { CPU } from '../cpu/ternary_cpu_v9.js';
import { intToWord } from '../cpu/balanced_ternary_arith.js';

const OP_LD = -2;

const cpu = new CPU({ memorySize: 64, regCount: 4 });

// Initialize address 5 with a known value via ECC path
cpu._writeMem(5, intToWord(7));

// Corrupt memory without updating ECC
cpu.memory[5] = intToWord(8);

// Try to load from 5 -> should detect ECC mismatch and halt
cpu.execute({ op: OP_LD, regA: 0, regB: 0, imm: 5, mini: false });

console.log('halted:', cpu.halted);
if (!cpu.halted) throw new Error('CPU did not halt on ECC fault');
console.log('PASS: test_ecc_fault');