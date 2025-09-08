// Read violation: CLD outside bounds (or without read permission) should halt with a fault.
import { CPU } from '../cpu/ternary_cpu_v9.js';
import { intToWord } from '../cpu/balanced_ternary_arith.js';
import { encodeCap } from '../cpu/cap_kit.js';

const OP_CLD = -5;

const cpu = new CPU({ memorySize: 64, regCount: 4 });
// Place some data but we'll try to access out-of-bounds for the cap
cpu._writeMem(30, intToWord(777));

// Capability only covers [10,15), so addr=30 is a violation
cpu.registers[1] = encodeCap({ base: 10, length: 5, read: true, write: true });

// Execute CLD r0, r1, 30
cpu.execute({ op: OP_CLD, regA: 0, regB: 1, imm: 30, mini: false });

console.log('halted:', cpu.halted);
if (!cpu.halted) throw new Error('CPU did not halt on capability read violation');
console.log('PASS: test_caps_read_violation');