// Happy path: CLD under valid capability loads correctly and CPU keeps running.
import { CPU } from '../cpu/ternary_cpu_v9.js';
import { intToWord, wordToInt } from '../cpu/balanced_ternary_arith.js';
import { encodeCap } from '../cpu/cap_kit.js';

const OP_CLD = -5;

const cpu = new CPU({ memorySize: 64, regCount: 4 });
const addr = 12;
cpu._writeMem(addr, intToWord(123)); // seed memory and ECC
cpu.registers[1] = encodeCap({ base: 10, length: 10, read: true, write: true });

// Execute CLD r0, r1, 12
cpu.execute({ op: OP_CLD, regA: 0, regB: 1, imm: addr, mini: false });

console.log('halted:', cpu.halted);
console.log('r0:', wordToInt(cpu.registers[0]));
if (cpu.halted) throw new Error('CPU halted unexpectedly (happy path)');
if (wordToInt(cpu.registers[0]) !== 123) throw new Error('CLD failed: r0 != 123');
console.log('PASS: test_caps_happy_path');