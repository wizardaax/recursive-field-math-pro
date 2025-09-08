// CHERI-lite capability helpers for ternary CPU (ASCII-safe)
// Layout in 12 trits (LSB-first view):
//  [0..5]  base (6 trits, signed)   ~ range about +/- 364
//  [6..9]  length (4 trits, unsigned) -> 0..(3^4-1)/? ≈ 0..40 (we'll keep as raw int via tritsToInt)
//  [10]    R perm (trit > 0 => allowed)
//  [11]    W perm (trit > 0 => allowed)

import { intToTrits, tritsToInt, tritsToWord, wordToTrits } from './balanced_ternary_arith.js';

export function encodeCap({ base, length, read = true, write = true }){
  const t = Array(12).fill(0);
  const tb = intToTrits(base, 6);          for (let i=0;i<6;i++) t[i] = tb[i] || 0;
  const tl = intToTrits(length, 4);        for (let i=0;i<4;i++) t[6+i] = tl[i] || 0;
  t[10] = read ? 1 : 0;
  t[11] = write ? 1 : 0;
  return tritsToWord(t);
}

export function decodeCap(capWord){
  const t = wordToTrits(capWord);
  const base   = tritsToInt(t.slice(0,6));
  const length = Math.max(0, tritsToInt(t.slice(6,10)));
  const read   = (t[10] || 0) > 0;
  const write  = (t[11] || 0) > 0;
  return { base, length, read, write };
}

export function checkCapLoad(capWord, addr){
  const { base, length, read } = decodeCap(capWord);
  const ok = read && addr >= base && addr < base + length;
  return !!ok;
}
export function checkCapStore(capWord, addr){
  const { base, length, write } = decodeCap(capWord);
  const ok = write && addr >= base && addr < base + length;
  return !!ok;
}