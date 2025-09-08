// docs/repl_harness.js
// REPL history + registers + memory inspector + save/load sessions
// Adjust import paths below to match your repo structure.

const TRY_IMPORTS = [
  {cpu: '../ternary_cpu_v7.js', alu: '../balanced_ternary_arith.js'},
  {cpu: '../ternary_cpu_v6.js', alu: '../balanced_ternary_arith.js'},
  {cpu: '../ternary_cpu_v5.js', alu: '../balanced_ternary_arith.js'},
  {cpu: '../ternary_cpu_v4.js', alu: '../balanced_ternary_arith.js'},
  {cpu: '../ternary_cpu_v3.js', alu: '../balanced_ternary_arith.js'},
  {cpu: '../ternary_cpu_v2.js', alu: '../balanced_ternary_arith.js'},
];

async function loadCPU() {
  let lastErr = null;
  for (const p of TRY_IMPORTS) {
    try {
      const cpu = await import(p.cpu);
      const alu = await import(p.alu);
      return {cpu, alu, used: p};
    } catch (e) { lastErr = e; }
  }
  throw new Error("Could not import CPU/ALU modules. Edit TRY_IMPORTS paths in docs/repl_harness.js.\nLast error: " + (lastErr?.message||lastErr));
}

const ui = sel => document.querySelector(sel);

function tritsToString(trits) { // LSB→MSB as ascii -/0/+
  return trits.map(t => t === -1 ? '-' : (t === 0 ? '0' : '+')).join('');
}

function timestamp() {
  const d = new Date();
  return d.toISOString().split('T')[1].replace('Z','');
}

function saveBlob(name, text, mime='application/json') {
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([text], {type: mime}));
  a.download = name;
  a.click();
  setTimeout(()=>URL.revokeObjectURL(a.href), 1000);
}

(async function main(){
  try {
    const {cpu: CPUm, alu: ALUm, used} = await loadCPU();

    // Expected exports (with fallbacks)
    const CPU = CPUm.CPU || CPUm.default || CPUm.Cpu || CPUm.TernaryCPU;
    const assembleProgram = CPUm.assembleProgram || CPUm.assemble || CPUm.assembleLines;
    const disassembleWord = CPUm.disassembleWord || CPUm.disasm || (w => '(no disasm)');
    const wordToInt = ALUm.wordToInt;
    const wordToTrits = ALUm.wordToTrits;
    const intToWord = ALUm.intToWord;

    if (!CPU || !assembleProgram || !wordToInt || !wordToTrits || !intToWord) {
      ui('#msg-assemble').innerHTML = `<span class="bad">CPU/ALU API mismatch.</span> Check exports & paths.`;
      return;
    }
    
    setupREPL(CPU, assembleProgram, disassembleWord, wordToInt, wordToTrits, intToWord, used);
  } catch (e) {
    // Fallback mode when CPU/ALU modules don't exist
    ui('#msg-assemble').innerHTML = `
      <div class="warn">
        <strong>Demo Mode:</strong> Ternary CPU/ALU modules not found.<br>
        This REPL is ready for a ternary computer implementation.<br>
        <small>To enable full functionality, add CPU/ALU modules and update TRY_IMPORTS paths in repl_harness.js</small>
      </div>`;
    
    // Enable basic UI interaction in demo mode
    setupDemoMode();
  }
  
function setupDemoMode() {
  // History (in-memory + localStorage)
  const HISTORY_KEY = 'mathpro.repl.history';
  let history = [];
  try { history = JSON.parse(localStorage.getItem(HISTORY_KEY)||'[]'); } catch {}
  function pushHist(msg){
    const line = `[${timestamp()}] ${msg}`;
    history.push(line);
    const li = document.createElement('li'); li.textContent = line;
    ui('#hist-list').appendChild(li);
    localStorage.setItem(HISTORY_KEY, JSON.stringify(history.slice(-1000)));
  }
  function redrawHistory(){
    ui('#hist-list').innerHTML = '';
    history.forEach(h => { const li = document.createElement('li'); li.textContent = h; ui('#hist-list').appendChild(li); });
  }
  redrawHistory();

  // Tabs
  document.querySelectorAll('.tabs .btn').forEach(b=>{
    b.addEventListener('click', ()=>{
      const tab = b.dataset.tab;
      b.parentElement.querySelectorAll('.btn').forEach(x=>x.removeAttribute('aria-current'));
      b.setAttribute('aria-current','page');
      document.querySelectorAll('[id^="tab-"]').forEach(p=>p.classList.add('hidden'));
      ui(`#tab-${tab}`).classList.remove('hidden');
    });
  });

  // Basic button handlers for demo
  ui('#btn-assemble').addEventListener('click', ()=>{
    ui('#msg-assemble').innerHTML = `<span class="warn">Demo mode: CPU/ALU modules needed for assembly.</span>`;
    pushHist('Demo: Assemble attempted');
  });

  ui('#btn-reset').addEventListener('click', ()=>{
    ui('#run-status').textContent = 'Demo mode: Reset simulated.';
    pushHist('Demo: Reset simulated');
  });

  ui('#btn-step').addEventListener('click', ()=>{
    ui('#run-status').textContent = 'Demo mode: Step simulated.';
    pushHist('Demo: Step simulated');
  });

  ui('#btn-run').addEventListener('click', ()=>{
    ui('#run-status').textContent = 'Demo mode: Run simulated.';
    pushHist('Demo: Run simulated');
  });

  ui('#btn-halt').addEventListener('click', ()=>{
    ui('#run-status').textContent = 'Demo mode: Halt simulated.';
    pushHist('Demo: Halt simulated');
  });

  // File operations
  ui('#open-asm').addEventListener('change', async e=>{
    const f = e.target.files?.[0]; if(!f) return;
    ui('#prog-src').value = await f.text();
    pushHist(`Demo: Opened ASM: ${f.name}`);
  });
  
  ui('#save-asm').addEventListener('click', ()=>{
    const txt = ui('#prog-src').value || '';
    saveBlob('program.asm', txt, 'text/plain');
    pushHist('Demo: Saved ASM file');
  });

  // History buttons
  ui('#hist-clear').addEventListener('click', ()=>{
    history = [];
    localStorage.removeItem(HISTORY_KEY);
    redrawHistory();
  });
  ui('#hist-save').addEventListener('click', ()=>{
    saveBlob('repl-history.json', JSON.stringify(history, null, 2));
  });
  ui('#hist-open').addEventListener('change', async e=>{
    const f = e.target.files?.[0]; if(!f) return;
    history = JSON.parse(await f.text());
    localStorage.setItem(HISTORY_KEY, JSON.stringify(history.slice(-1000)));
    redrawHistory();
  });

  // Right panel tabs
  document.querySelectorAll('section.panel .tabs .btn').forEach(b=>{
    b.addEventListener('click', ()=>{
      const parent = b.closest('section.panel');
      parent.querySelectorAll('.tabs .btn').forEach(x=>x.removeAttribute('aria-current'));
      b.setAttribute('aria-current','page');
      const which = b.dataset.tab;
      parent.querySelectorAll('[id^="tab-"]').forEach(p=>p.classList.add('hidden'));
      ui(`#tab-${which}`).classList.remove('hidden');
    });
  });

  // Demo content
  if (!ui('#prog-src').value.trim()){
    ui('#prog-src').value =
`// Demo Program - Ternary Assembly
// This REPL is ready for ternary CPU implementation
// Example instructions:
LOADI r0 9      // Load immediate 9 into register 0
loop:
MADD r0 -1      // Multiply-add: r0 = r0 * 1 + (-1)
MJMPREL r0 -1   // Jump back if r0 != 0
// end

// To enable full functionality:
// 1. Add ternary CPU/ALU JavaScript modules
// 2. Update TRY_IMPORTS paths in repl_harness.js`;
  }

  // Initial status
  ui('#pc-line').textContent = 'Demo mode';
  ui('#dis-line').textContent = 'CPU/ALU modules needed';
  ui('#run-status').textContent = 'Demo mode - ready to load ternary CPU modules.';
  ui('#watch-line').textContent = 'Demo mode';
  
  pushHist('Demo mode initialized');
}

})();