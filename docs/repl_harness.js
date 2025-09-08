// Minimal harness that tries to import your CPU/ALU; falls back to no-op stubs if missing.
// Note: On GitHub Pages, the site root is "docs/". We import from "./cpu/*.js" which are copied during deploy.
export async function boot(statusEl){
  const log = (msg)=> statusEl.textContent = String(msg);
  let cpuMod = null, aluMod = null;
  try { cpuMod = await import('./cpu/ternary_cpu_v8.js'); } catch { /* optional until real module exists */ }
  try { aluMod = await import('./cpu/balanced_ternary_arith.js'); } catch { /* optional until real module exists */ }

  // Fallback stubs so the page still loads if files aren’t there yet
  const stub = {
    intToWord: n => ({_n:n}),
    wordToInt: w => (w && typeof w._n === 'number') ? (w._n|0) : 0,
    CPU: class {
      constructor(){ this.pc={_n:0}; this.halted=false; this.registers=[{_n:7},{_n:-4},{_n:0},{_n:0}]; }
      step(){ this.registers[0]._n += this.registers[1]._n; this.halted = true; }
      loadProgram(){ this.pc._n=0; this.halted=false; }
    }
  };

  const env = {
    intToWord: (aluMod && aluMod.intToWord) || stub.intToWord,
    wordToInt: (aluMod && aluMod.wordToInt) || stub.wordToInt,
    CPU:       (cpuMod && cpuMod.CPU)       || stub.CPU,
    cpu: null,
    load(text){
      this.cpu = new this.CPU();
      // If real CPU present and assembler exported, assemble; else just reset
      try{
        if (cpuMod && cpuMod.assembleProgram) {
          const program = cpuMod.assembleProgram(text.split(/\r?\n/));
          this.cpu.loadProgram(program);
        } else {
          this.cpu.loadProgram([]);
        }
      }catch(e){ console.error(e); }
    }
  };

  log('CPU ready');
  return env;
}