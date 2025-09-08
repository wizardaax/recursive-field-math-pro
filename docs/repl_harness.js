// docs/repl_harness.js — loads CPU/ALU; can assemble with macros or raw mnemonics.
export async function boot(statusEl){
  const set = (m)=> statusEl.textContent = String(m);

  // Optional modules (graceful if not present on first deploy)
  let cpuMod=null, aluMod=null, miniAsm=null, macroAsm=null;
  try { cpuMod   = await import('../cpu/ternary_cpu_v8.js'); } catch {}
  try { aluMod   = await import('../cpu/balanced_ternary_arith.js'); } catch {}
  try { miniAsm  = await import('../cpu/mini_assembler.js'); } catch {}
  try { macroAsm = await import('../cpu/macro_assembler.js'); } catch {}

  // Stubs (so page loads even before modules exist)
  const stub = {
    intToWord: n => ({_n:n}),
    wordToInt: w => (w && typeof w._n==='number') ? (w._n|0) : 0,
    CPU: class {
      constructor(){ this.pc={_n:0}; this.halted=false; this.registers=[{_n:7},{_n:-4},{_n:0},{_n:0}]; }
      step(){ this.registers[0]._n += this.registers[1]._n; this.halted=true; }
      loadProgram(){ this.pc._n=0; this.halted=false; }
    }
  };

  const env = {
    intToWord: (aluMod?.intToWord) || stub.intToWord,
    wordToInt: (aluMod?.wordToInt) || stub.wordToInt,
    CPU:       (cpuMod?.CPU)       || stub.CPU,
    cpu: null,

    async load(text, { useMacros=true } = {}){
      this.cpu = new this.CPU();
      const src = String(text||'');
      // Choose assembler path
      if (useMacros && macroAsm?.macroAssemble){
        const words = await macroAsm.macroAssemble(src);
        this.cpu.loadProgram(words);
      } else if (miniAsm?.assembleProgram){
        const words = await miniAsm.assembleProgram(src.split(/\r?\n/));
        this.cpu.loadProgram(words);
      } else {
        // No assembler yet → just reset
        this.cpu.loadProgram([]);
      }
    }
  };

  set('CPU ready');
  return env;
}