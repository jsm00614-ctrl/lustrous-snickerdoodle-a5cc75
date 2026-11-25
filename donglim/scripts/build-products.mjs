#!/usr/bin/env node
/**
 * build-products.mjs
 * ─────────────────────────────────────────────────────────────
 * 사이트가 읽는 content/products.json 을 만듭니다. (그 파일은 직접 수정하지 마세요)
 *
 *   1) content/products/*.json   — 관리자(CMS) “제품” 메뉴에서 1개씩 등록한 제품
 *   2) content/bulk.json 에 등록된 CSV — 관리자 “엑셀 일괄 등록” 메뉴에서 올린 파일
 *
 * 같은 품번이 양쪽에 있으면 1)의 개별 제품이 우선합니다.
 * Netlify 배포 때 자동으로 실행됩니다 (netlify.toml). 로컬에서는:
 *   node donglim/scripts/build-products.mjs
 */
import { readFileSync, writeFileSync, readdirSync, existsSync } from 'node:fs';
import { join, dirname, resolve, basename } from 'node:path';
import { fileURLToPath } from 'node:url';

const SITE = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const ROOT = resolve(SITE, '..');
const CONTENT = join(SITE, 'content');
const warn = [];

const readJSON = (f, d) => { try { return JSON.parse(readFileSync(f, 'utf8')); } catch (e) { if (d !== undefined) return d; throw new Error(`${f}: ${e.message}`); } };
const tax = readJSON(join(CONTENT, 'taxonomy.json'));

/* ---------- 라벨 ↔ 키 변환 (CSV에는 한글 이름으로 적어도 됩니다) ---------- */
const norm = (s) => String(s || '').toLowerCase().replace(/\s+/g, '').replace(/[()（）]/g, '');
function keyOf(list, value) {
  const v = norm(value);
  if (!v) return '';
  for (const it of list || []) {
    if (norm(it.key) === v || norm(it.label) === v) return it.key;
    const short = norm(String(it.label).split(/[ (]/)[0]);
    if (short && (short === v || norm(it.label).startsWith(v))) return it.key;
  }
  return null;
}
const SHAPES = [
  { key: 'round', label: '라운드' }, { key: 'square', label: '스퀘어' }, { key: 'boston', label: '보스턴' },
  { key: 'jar', label: '자' }, { key: 'perfume', label: '향수' }, { key: 'vial', label: '바이알' },
];
const splitList = (s) => String(s || '').split(/[,/·|;\n]+/).map((x) => x.trim()).filter(Boolean);
const yes = (s, d = false) => { const v = norm(s); if (!v) return d; return ['y', 'yes', 'true', '1', 'o', '예', '네', '공개', '재고', '있음'].includes(v); };
const numOf = (s) => { const n = parseFloat(String(s ?? '').replace(/[^0-9.\-]/g, '')); return Number.isFinite(n) ? n : 0; };

/* ---------- CSV 파서 (따옴표·줄바꿈 지원, 엑셀 “CSV UTF-8” 저장 형식) ---------- */
function parseCSV(text) {
  text = text.replace(/^﻿/, '');
  const first = text.split('\n')[0];
  const delim = (first.match(/\t/g) || []).length > (first.match(/,/g) || []).length ? '\t' : ',';
  const rows = []; let row = [], cell = '', q = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (q) {
      if (c === '"' && text[i + 1] === '"') { cell += '"'; i++; }
      else if (c === '"') q = false;
      else cell += c;
    } else if (c === '"') q = true;
    else if (c === delim) { row.push(cell); cell = ''; }
    else if (c === '\n' || c === '\r') {
      if (c === '\r' && text[i + 1] === '\n') i++;
      row.push(cell); rows.push(row); row = []; cell = '';
    } else cell += c;
  }
  if (cell || row.length) { row.push(cell); rows.push(row); }
  return rows.filter((r) => r.some((x) => String(x).trim()));
}

/* CSV 머리글 → 필드 (한글/영문 모두 허용, 괄호 안 설명·* 표시는 무시) */
const HEAD = {
  code: ['품번', 'code'], name: ['제품명', 'name'], category: ['용도', '카테고리', 'category'], shape: ['형태', 'shape'],
  capacity: ['용량', 'capacity'], fullCapacity: ['만수', '만수용량', 'fullcapacity'], height: ['높이', 'height'],
  diameter: ['지름', '가로', '지름가로', '지름/가로', 'diameter', 'width'], depth: ['세로', 'depth'], neck: ['넥', '넥규격', 'neck'],
  weight: ['중량', 'weight'], colors: ['색상', '유리색상', 'colors'], closures: ['부자재', '호환부자재', 'closures'],
  decorations: ['후가공', 'decorations'], moq: ['moq', '최소주문', '최소주문수량'], stock: ['재고', '재고여부', 'stock'],
  leadTime: ['납기', '출고', 'leadtime'], moldType: ['생산방식', '자동수동', 'moldtype'], badge: ['배지', 'badge'],
  summary: ['설명', 'summary'], material: ['재질', 'material'], image: ['이미지', '사진', 'image'], published: ['공개', 'published'],
};

function rowToProduct(h, r, src, line) {
  const get = (f) => { const i = h[f]; return i == null ? '' : String(r[i] ?? '').trim(); };
  const code = get('code');
  if (!code) { warn.push(`${src}:${line} 품번이 비어 있어 건너뜀`); return null; }
  const mapList = (field, list) => splitList(get(field)).map((v) => {
    const k = keyOf(list, v);
    if (!k) warn.push(`${src}:${line} [${code}] ${field} '${v}' 를 찾을 수 없음 (분류 설정 확인)`);
    return k;
  }).filter(Boolean);
  const cat = keyOf(tax.categories, get('category'));
  if (!cat) warn.push(`${src}:${line} [${code}] 용도 '${get('category')}' 를 찾을 수 없음`);
  const stock = yes(get('stock'));
  const p = {
    code, name: get('name') || code, category: cat || '', shape: keyOf(SHAPES, get('shape')) || 'round',
    capacity: numOf(get('capacity')), fullCapacity: numOf(get('fullCapacity')) || numOf(get('capacity')),
    height: numOf(get('height')), diameter: numOf(get('diameter')), depth: numOf(get('depth')),
    neck: get('neck'), weight: numOf(get('weight')),
    colors: mapList('colors', tax.colors), closures: mapList('closures', tax.closures), decorations: mapList('decorations', tax.decorations),
    moq: numOf(get('moq')), stock, leadTime: get('leadTime') || (stock ? '재고 즉시출고 (D+2)' : '생산 4~6주'),
    moldType: keyOf(tax.moldTypes, get('moldType')) || 'auto', badge: get('badge').toUpperCase(), summary: get('summary'),
    material: get('material'), image: get('image'), gallery: [], model3d: '', published: yes(get('published'), true),
  };
  if (!p.colors.length) p.colors = ['flint'];
  if (!p.height || !p.diameter) warn.push(`${src}:${line} [${code}] 높이·지름이 없어 도면이 기본값으로 그려짐`);
  return p;
}

function loadCSV(file) {
  const rows = parseCSV(readFileSync(file, 'utf8'));
  if (rows.length < 2) return [];
  const h = {};
  rows[0].forEach((name, i) => {
    const n = norm(String(name).replace(/\*/g, '').replace(/[(（].*$/, ''));
    for (const [f, alias] of Object.entries(HEAD)) if (alias.some((a) => norm(a) === n)) h[f] = i;
  });
  if (h.code == null) { warn.push(`${basename(file)}: 첫 줄에 '품번' 머리글이 없음`); return []; }
  return rows.slice(1).map((r, i) => rowToProduct(h, r, basename(file), i + 2)).filter(Boolean);
}

function resolveUpload(p) {
  const clean = String(p || '').replace(/^\/+/, '');
  for (const c of [join(ROOT, clean), join(SITE, clean.replace(/^donglim\//, '')), join(CONTENT, 'bulk', basename(clean))]) if (existsSync(c)) return c;
  return null;
}

/* ---------- 합치기 ---------- */
const byCode = new Map();
const bulk = readJSON(join(CONTENT, 'bulk.json'), { files: [] });
let fromCSV = 0;
for (const f of bulk.files || []) {
  if (f.enabled === false || !f.file) continue;
  const path = resolveUpload(f.file);
  if (!path) { warn.push(`CSV 파일을 찾을 수 없음: ${f.file}`); continue; }
  for (const p of loadCSV(path)) { byCode.set(p.code, p); fromCSV++; }
}
const dir = join(CONTENT, 'products');
let fromCMS = 0;
for (const f of existsSync(dir) ? readdirSync(dir).filter((x) => x.endsWith('.json')) : []) {
  const p = readJSON(join(dir, f), null);
  if (!p || !p.code) { warn.push(`${f}: 읽을 수 없거나 품번이 없음`); continue; }
  byCode.set(p.code, p); fromCMS++;
}

const order = tax.categories.map((c) => c.key);
const items = [...byCode.values()].sort((a, b) => (order.indexOf(a.category) - order.indexOf(b.category)) || (a.capacity - b.capacity) || String(a.code).localeCompare(String(b.code)));
writeFileSync(join(CONTENT, 'products.json'), JSON.stringify({ generated: 'build-products.mjs 가 자동 생성 — 직접 수정하지 마세요', count: items.length, items }, null, 2) + '\n');

console.log(`[build-products] 개별 ${fromCMS}개 + CSV ${fromCSV}행 → ${items.length}개 제품 (content/products.json)`);
warn.forEach((w) => console.warn('  ⚠', w));
