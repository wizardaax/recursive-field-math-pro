// cpu/macro_assembler.js — ASCII-safe, no deps besides mini_assembler
// Two-pass macro assembler with labels + LOOP/ENDLOOP + MACRO/USE.
// Exports both async and truly-sync entry points.
//
// Async usage:
//   import { macroAssemble } from './cpu/macro_assembler.js';
//   const words = await macroAssemble(sourceText);
//
// Sync usage:
//   import { macroAssembleSync } from './cpu/macro_assembler.js';
//   const words = macroAssembleSync(sourceText);

import { assembleProgram, assembleLine } from './mini_assembler.js';

const MAX_MACRO_EXPANSION = 10000;

const strip = (s) => s.split('//')[0].trim();
const isLabel = (s) => /:\s*$/.test(s);
const labelName = (s) => s.replace(/:\s*$/,'').trim();
const isRegister = (tok) => /^r-?\d+$/i.test(tok);
const toRel = (fromIdx, targetIdx) => targetIdx - (fromIdx + 1);

function expandAndCollect(source, { defaultLoopReg='r0' } = {}){
  const src = (Array.isArray(source) ? source : String(source).split(/\r?\n/))
    .map(strip).filter(Boolean);

  const macros = new Map();
  const out = [];
  const labels = new Map();
  const loopStack = [];

  let inMacro = null, macroBuf = [], expanded = 0;

  // Pass A1: build macros, expand USE inline
  for (const raw0 of src){
    const raw = raw0;

    if (/^MACRO\s+/i.test(raw)){
      inMacro = raw.replace(/^MACRO\s+/i,'').trim().toUpperCase();
      if (!inMacro) throw new Error('MACRO requires a name');
      macroBuf = [];
      continue;
    }
    if (/^ENDMACRO$/i.test(raw)){
      if (!inMacro) throw new Error('ENDMACRO without MACRO');
      macros.set(inMacro, macroBuf.slice());
      inMacro = null; macroBuf = [];
      continue;
    }
    if (inMacro){
      macroBuf.push(raw);
      continue;
    }

    if (/^USE\s+/i.test(raw)){
      const name = raw.replace(/^USE\s+/i,'').trim().toUpperCase();
      const body = macros.get(name);
      if (!body) throw new Error('Unknown macro: ' + name);
      for (const ln of body){
        expanded++; if (expanded > MAX_MACRO_EXPANSION) throw new Error('Macro expansion limit exceeded');
        out.push(ln);
      }
      continue;
    }

    out.push(raw);
  }

  // Pass A2: labels + LOOP placeholders
  const normalized = [];
  for (const raw of out){
    if (isLabel(raw)){
      labels.set(labelName(raw), normalized.filter(l => !isLabel(l)).length);
      continue;
    }
    if (/^LOOP(\s+r-?\d+)?$/i.test(raw)){
      const m = raw.match(/^LOOP(?:\s+(r-?\d+))?$/i);
      loopStack.push({ idx: normalized.length, reg: (m && m[1]) || defaultLoopReg });
      normalized.push('__LOOP__');
      continue;
    }
    if (/^ENDLOOP$/i.test(raw)){
      const fr = loopStack.pop();
      if (!fr) throw new Error('ENDLOOP without LOOP');
      const dist = normalized.length - fr.idx;
      normalized[fr.idx] = `MJMPREL ${fr.reg} -${dist}`;
      continue;
    }
    normalized.push(raw);
  }
  if (loopStack.length) throw new Error('Unclosed LOOP');

  return { lines: normalized, labels };
}

function resolveLabels(lines, labels){
  // map file-line index → instruction index (labels don't count)
  const instrRows = lines.map((ln,i)=>({ln,i})).filter(x=>!isLabel(x.ln));
  const idxByLine = new Map(instrRows.map((x,k)=>[x.i,k]));

  const out = [];
  for (let i=0;i<lines.length;i++){
    const ln = lines[i];
    if (isLabel(ln)) continue; // skip labels in output

    // Replace label references
    let resolved = ln;
    for (const [lbl, targetInstrIdx] of labels.entries()){
      const pattern = new RegExp('\\b' + lbl + '\\b', 'g');
      resolved = resolved.replace(pattern, (match) => {
        const currInstrIdx = idxByLine.get(i);
        if (currInstrIdx === undefined) throw new Error(`Cannot resolve label ${lbl}: instruction index not found`);
        
        // Check if this looks like a relative jump
        if (/(JMPREL|MJMPREL)/i.test(resolved)) {
          return toRel(currInstrIdx, targetInstrIdx).toString();
        }
        // Otherwise absolute
        return targetInstrIdx.toString();
      });
    }
    out.push(resolved);
  }
  return out;
}

// Synchronous macro assembler
export function macroAssembleSync(source, options = {}) {
  try {
    const { lines, labels } = expandAndCollect(source, options);
    const resolved = resolveLabels(lines, labels);
    return assembleProgram(resolved);
  } catch (err) {
    throw new Error(`Macro assembly failed: ${err.message}`);
  }
}

// Async macro assembler (same logic, wrapped in Promise for API compatibility)
export async function macroAssemble(source, options = {}) {
  return macroAssembleSync(source, options);
}