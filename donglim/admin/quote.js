/*
 * 동림 견적 관리 (quote.html)
 * - 공개 데이터: ../content/products.json · taxonomy.json · site.json (제품 사양만, 가격 없음)
 * - 비공개 데이터(원가·설정·견적 기록)는 DB 하나로 묶어 저장합니다.
 *     · 이 브라우저: localStorage 'donglim.quote.db'
 *     · 비공개 GitHub 저장소: <repo>/quote-data.json  (관리자 페이지의 GitHub 로그인 토큰 사용, 공개 저장소면 저장 거부)
 * - 단가 = 원가(제품 구간 원가 + 부자재 + 후가공) 에 마진율 적용 → 끝자리 처리
 */
(function () {
  'use strict';

  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const won = (n) => (n == null || isNaN(n) ? '—' : Math.round(n).toLocaleString('ko-KR'));
  const numOrNull = (v) => { if (v === '' || v == null) return null; const n = Number(String(v).replace(/[,\s원₩]/g, '')); return isFinite(n) ? n : null; };
  const uid = () => Math.random().toString(36).slice(2, 9);
  const today = () => { const d = new Date(); d.setMinutes(d.getMinutes() - d.getTimezoneOffset()); return d.toISOString().slice(0, 10); };
  const addDays = (iso, n) => { const d = new Date(iso + 'T00:00:00'); d.setDate(d.getDate() + n); return `${d.getFullYear()}. ${d.getMonth() + 1}. ${d.getDate()}.`; };
  const dotDate = (iso) => (iso ? iso.replace(/-/g, '. ') + '.' : '');

  const DB_KEY = 'donglim.quote.db';
  const DRAFT_KEY = 'donglim.quote.draft';
  const STORE_KEY = 'donglim.quote.store';
  const FILE = 'quote-data.json';

  /* ───────── 기본 데이터 ───────── */
  const defaultDB = () => ({
    version: 1,
    settings: {
      margin: 25, method: 'markup', round: 10, roundMode: 'ceil', vat: true, tiers: [3000, 10000, 30000],
      prefix: 'DL', validDays: 30, delivery: '발주 후 4~5주 (재고품 1주)', payment: '발주 시 50%, 출고 전 잔금 50%',
      memo: '샘플은 품목당 3개까지 무료로 보내드립니다.\n후가공·부자재 사양이 바뀌면 단가가 달라질 수 있습니다.',
      company: null,
    },
    costs: { products: {}, closures: {}, decorations: {} },
    quotes: [],
    seq: {},
    updated: null,
  });

  const S = {
    products: [], byCode: {}, tax: {}, MAP: {}, site: {},
    db: defaultDB(), draft: null,
    store: null, dirty: false,
    pick: { q: '', cat: '' }, costQ: '', histQ: '',
  };

  /* ───────── 저장소 ───────── */
  function utf8ToB64(str) {
    const bytes = new TextEncoder().encode(str); let bin = '';
    for (let i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
    return btoa(bin);
  }
  function b64ToUtf8(b64) {
    const bin = atob(b64.replace(/\s/g, '')); const bytes = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
    return new TextDecoder().decode(bytes);
  }

  const LocalStore = {
    mode: 'local',
    label: '이 브라우저에 저장',
    async load() { try { return JSON.parse(localStorage.getItem(DB_KEY) || 'null'); } catch (e) { return null; } },
    async save(db) { localStorage.setItem(DB_KEY, JSON.stringify(db)); },
  };

  function GitStore(repo) {
    let sha = null;
    const token = () => {
      try { const u = JSON.parse(localStorage.getItem('decap-cms-user') || localStorage.getItem('netlify-cms-user') || 'null'); return u && u.token; } catch (e) { return null; }
    };
    const api = async (path, opts = {}) => {
      const t = token();
      if (!t) throw new Error('NOLOGIN');
      const res = await fetch('https://api.github.com' + path, { ...opts, headers: { Accept: 'application/vnd.github+json', Authorization: 'token ' + t, ...(opts.headers || {}) } });
      return res;
    };
    return {
      mode: 'github', repo,
      label: '비공개 저장소 · ' + repo,
      async check() {
        const r = await api('/repos/' + repo);
        if (r.status === 404) throw new Error('저장소를 찾을 수 없습니다. 이름을 확인하거나, 로그인한 계정에 권한이 있는지 확인하세요.');
        if (!r.ok) throw new Error('GitHub 연결 실패 (' + r.status + ')');
        const info = await r.json();
        if (!info.private) throw new Error('공개(Public) 저장소입니다. 원가가 외부에 보이므로 저장하지 않습니다. 비공개(Private) 저장소를 쓰세요.');
        if (info.permissions && info.permissions.push === false) throw new Error('이 저장소에 쓰기 권한이 없습니다.');
        return info;
      },
      async load() {
        await this.check();
        const r = await api(`/repos/${repo}/contents/${FILE}`);
        if (r.status === 404) { sha = null; return null; }
        if (!r.ok) throw new Error('불러오기 실패 (' + r.status + ')');
        const j = await r.json(); sha = j.sha;
        return JSON.parse(b64ToUtf8(j.content));
      },
      async save(db) {
        const body = { message: `견적 데이터 저장 (${new Date().toLocaleString('ko-KR')})`, content: utf8ToB64(JSON.stringify(db, null, 1)) };
        if (sha) body.sha = sha;
        const r = await api(`/repos/${repo}/contents/${FILE}`, { method: 'PUT', body: JSON.stringify(body), headers: { 'Content-Type': 'application/json' } });
        if (r.status === 409 || r.status === 422) throw new Error('다른 곳에서 먼저 저장했습니다. 새로고침 후 다시 저장하세요.');
        if (!r.ok) throw new Error('저장 실패 (' + r.status + ')');
        const j = await r.json(); sha = j.content && j.content.sha;
      },
    };
  }

  const storeConf = () => { try { return JSON.parse(localStorage.getItem(STORE_KEY) || 'null') || { mode: 'local' }; } catch (e) { return { mode: 'local' }; } };
  const makeStore = (conf) => (conf.mode === 'github' && conf.repo ? GitStore(conf.repo) : LocalStore);

  function mergeDB(raw) {
    const d = defaultDB();
    if (!raw) return d;
    return {
      ...d, ...raw,
      settings: { ...d.settings, ...(raw.settings || {}) },
      costs: { products: {}, closures: {}, decorations: {}, ...(raw.costs || {}) },
      quotes: raw.quotes || [], seq: raw.seq || {},
    };
  }

  function changed() {
    S.db.updated = new Date().toISOString();
    // 이 브라우저 저장은 바로 씁니다(창을 바로 닫아도 남도록). 비공개 저장소는 '저장'을 눌러야 올라갑니다.
    if (S.store.mode === 'local') S.store.save(S.db);
    else { S.dirty = true; localStorage.setItem(DB_KEY + '.cache', JSON.stringify(S.db)); }
    paintStore();
  }
  async function flush() {
    try {
      await S.store.save(S.db); S.dirty = false; paintStore();
      toast(S.store.mode === 'local' ? '저장했습니다.' : '비공개 저장소에 저장했습니다.');
      return true;
    } catch (e) { toast(e.message === 'NOLOGIN' ? '관리자 페이지에서 GitHub로 먼저 로그인하세요.' : e.message, true); return false; }
  }

  /* ───────── 가격 계산 ───────── */
  const set = () => S.db.settings;
  const company = () => ({ ...(S.site.company || {}), ...(set().company || {}) });
  function tierCost(code, qty) {
    const c = S.db.costs.products[code];
    if (!c) return null;
    let v = numOrNull(c.base);
    const tiers = [...(set().tiers || [])].sort((a, b) => a - b);
    for (const t of tiers) { const tv = numOrNull((c.tiers || {})[t]); if (qty >= t && tv != null) v = tv; }
    return v;
  }
  function applyMargin(cost, m) {
    if (cost == null) return null;
    if (set().method === 'margin') { if (m >= 100) return null; return cost / (1 - m / 100); }
    return cost * (1 + m / 100);
  }
  function roundPrice(x) {
    if (x == null || !isFinite(x)) return null;
    const u = Number(set().round) || 1;
    return set().roundMode === 'round' ? Math.round(x / u) * u : Math.ceil(x / u - 1e-9) * u;
  }
  const marginOf = (line) => (line.margin != null ? line.margin : (S.draft.margin != null ? S.draft.margin : set().margin));
  const label = (group, k) => ((S.MAP[group] || {})[k] || {}).label || k;

  function compute() {
    const rows = [];
    S.draft.lines.forEach((ln) => {
      const m = marginOf(ln);
      const qty = Math.max(0, numOrNull(ln.qty) || 0);
      let cost = null; const missing = []; let name; let spec; const setups = [];
      if (ln.type === 'custom') {
        cost = numOrNull(ln.cost); name = ln.name || '기타 항목'; spec = ln.spec || '';
        if (cost == null) missing.push('원가');
      } else {
        const p = S.byCode[ln.code] || { code: ln.code, name: '(삭제된 제품)' };
        name = `${p.code} ${p.name}`;
        const parts = [`${p.capacity || '?'} mL`, p.neck ? `넥 ${p.neck}` : '', ln.color ? label('color', ln.color) : '', ln.closure ? label('closure', ln.closure) : '부자재 없음'];
        (ln.decos || []).forEach((k) => parts.push(label('deco', k)));
        spec = parts.filter(Boolean).join(' · ');
        const base = tierCost(ln.code, qty);
        if (base == null) missing.push('제품 원가');
        let add = 0;
        if (ln.closure) { const v = numOrNull((S.db.costs.closures[ln.closure] || {}).unit); if (v == null) missing.push(label('closure', ln.closure) + ' 원가'); else add += v; }
        (ln.decos || []).forEach((k) => {
          const d = S.db.costs.decorations[k] || {};
          const u = numOrNull(d.unit); if (u == null) missing.push(label('deco', k) + ' 원가'); else add += u;
          const su = numOrNull(d.setup);
          if (su) setups.push({ name: `${label('deco', k)} 판비`, spec: p.code, qty: 1, cost: su });
        });
        cost = missing.length ? null : base + add;
      }
      const auto = roundPrice(applyMargin(cost, m));
      const price = ln.price != null ? ln.price : auto;
      const amount = price == null ? null : price * qty;
      const moq = ln.type !== 'custom' && S.byCode[ln.code] ? S.byCode[ln.code].moq : null;
      rows.push({ ln, name, spec, qty, cost, m, auto, price, amount, missing, moqWarn: moq && qty > 0 && qty < moq ? moq : null });
      setups.forEach((su) => {
        const sp = roundPrice(applyMargin(su.cost, m));
        rows.push({ ln, setup: true, name: su.name, spec: su.spec, qty: 1, cost: su.cost, m, auto: sp, price: sp, amount: sp, missing: [] });
      });
    });
    const supply = rows.reduce((a, r) => a + (r.amount || 0), 0);
    const costTotal = rows.reduce((a, r) => a + (r.cost != null ? r.cost * r.qty : 0), 0);
    const vat = set().vat ? Math.floor(supply * 0.1) : 0;
    const missingCount = rows.filter((r) => r.price == null).length;
    return { rows, supply, vat, total: supply + vat, costTotal, profit: supply - costTotal, rate: supply ? (supply - costTotal) / supply : 0, missingCount };
  }

  /* 숫자 → 한글 금액 (일금 ○○원정) */
  function koreanAmount(n) {
    n = Math.floor(n); if (!n) return '영';
    const d = ['', '일', '이', '삼', '사', '오', '육', '칠', '팔', '구'], u = ['', '십', '백', '천'], big = ['', '만', '억', '조'];
    let out = ''; let i = 0;
    while (n > 0) {
      const chunk = n % 10000; n = Math.floor(n / 10000);
      if (chunk) {
        let s = ''; let c = chunk;
        for (let j = 0; j < 4 && c > 0; j++) { const dg = c % 10; c = Math.floor(c / 10); if (dg) s = d[dg] + u[j] + s; }
        out = s + big[i] + out;
      }
      i++;
    }
    return out;
  }

  /* ───────── 견적 초안 ───────── */
  function nextNo(dateIso) {
    const ymd = (dateIso || today()).replace(/-/g, '').slice(2);
    const n = (S.db.seq[ymd] || 0) + 1;
    return `${set().prefix || 'DL'}-${ymd}-${String(n).padStart(2, '0')}`;
  }
  function newDraft() {
    const d = today();
    return {
      id: uid(), no: nextNo(d), autoNo: true, date: d, customer: { company: '', person: '', tel: '', email: '' },
      margin: null, lines: [], delivery: set().delivery, payment: set().payment,
      valid: `견적일로부터 ${set().validDays}일 (${addDays(d, Number(set().validDays) || 30)}까지)`, memo: set().memo,
    };
  }
  const saveDraft = () => localStorage.setItem(DRAFT_KEY, JSON.stringify(S.draft));

  /* ───────── 화면: 공통 ───────── */
  function toast(msg, bad) {
    const t = $('#toast'); t.textContent = msg; t.className = 'toast is-on' + (bad ? ' is-bad' : '');
    clearTimeout(toast.t); toast.t = setTimeout(() => { t.className = 'toast'; }, bad ? 5200 : 2400);
  }
  function paintStore() {
    const b = $('#storeBadge');
    b.textContent = S.store.label + (S.store.mode === 'github' ? (S.dirty ? ' · 저장 안 됨' : ' · 저장됨') : '');
    b.className = 'store' + (S.store.mode === 'github' && S.dirty ? ' is-dirty' : '');
    $('#saveBtn').hidden = !(S.store.mode === 'github' && S.dirty);
  }
  function download(name, text, type) {
    const blob = new Blob([text], { type }); const a = document.createElement('a');
    a.href = URL.createObjectURL(blob); a.download = name; document.body.appendChild(a); a.click();
    setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 500);
  }
  const csvCell = (v) => { const s = v == null ? '' : String(v); return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s; };
  const toCSV = (rows) => '﻿' + rows.map((r) => r.map(csvCell).join(',')).join('\r\n');
  function parseCSV(text) {
    text = text.replace(/^﻿/, ''); const rows = []; let row = []; let cur = ''; let q = false;
    for (let i = 0; i < text.length; i++) {
      const c = text[i];
      if (q) { if (c === '"') { if (text[i + 1] === '"') { cur += '"'; i++; } else q = false; } else cur += c; continue; }
      if (c === '"') q = true; else if (c === ',') { row.push(cur); cur = ''; } else if (c === '\n') { row.push(cur); rows.push(row); row = []; cur = ''; } else if (c !== '\r') cur += c;
    }
    if (cur !== '' || row.length) { row.push(cur); rows.push(row); }
    return rows.filter((r) => r.some((x) => x.trim() !== ''));
  }

  /* ───────── 화면: 견적 작성 ───────── */
  const thumb = (p, color) => Bottle.render(p, { mode: 'card', w: 54, h: 62, color: S.MAP.color[color || (p.colors || [])[0]] });

  function renderPicker() {
    const cats = [{ key: '', label: '전체' }, ...(S.tax.categories || [])];
    $('#pickCats').innerHTML = cats.map((c) => `<button type="button" class="chip${S.pick.cat === c.key ? ' is-on' : ''}" data-cat="${esc(c.key)}">${esc(c.label)}</button>`).join('');
    const q = S.pick.q.trim().toLowerCase();
    const list = S.products.filter((p) => (!S.pick.cat || p.category === S.pick.cat) && (!q || [p.code, p.name, p.neck, p.capacity + 'ml'].join(' ').toLowerCase().includes(q)));
    $('#pickList').innerHTML = list.map((p) => {
      const c = S.db.costs.products[p.code]; const base = c ? numOrNull(c.base) : null;
      return `<li class="pi">
        <div class="pi__img">${thumb(p)}</div>
        <div class="pi__txt"><b>${esc(p.code)}</b><span>${esc(p.name)}</span><small>${p.capacity} mL · ${esc(p.neck || '')} · MOQ ${won(p.moq)}</small>
          ${base != null ? `<em class="ok">원가 ${won(base)}원</em>` : '<em class="no">원가 미등록</em>'}</div>
        <button type="button" class="btn btn--sm btn--aqua" data-add="${esc(p.code)}">+ 추가</button></li>`;
    }).join('') || '<li class="pi pi--empty">조건에 맞는 제품이 없습니다.</li>';
  }

  function lineRow(r, i) {
    const ln = r.ln; const id = ln.id;
    const miss = r.missing.length ? `<span class="warn">원가 없음: ${esc(r.missing.join(', '))}</span>` : '';
    const moq = r.moqWarn ? `<span class="warn">MOQ ${won(r.moqWarn)}개 미만</span>` : '';
    if (r.setup) {
      return `<tr class="ln ln--setup"><td class="c-no"></td><td><div class="ln__name">${esc(r.name)}</div><div class="ln__spec">${esc(r.spec)} · 1회</div></td>
        <td class="c-qty">1</td><td class="c-int">${won(r.cost)}</td><td class="c-int c-m">${r.m}%</td><td class="c-price">${won(r.price)}</td><td class="c-amt">${won(r.amount)}</td><td class="c-x"></td></tr>`;
    }
    let left;
    if (ln.type === 'custom') {
      left = `<div class="ln__custom"><input data-f="name" data-id="${id}" value="${esc(ln.name)}" placeholder="항목명 (예: 신규 금형비)">
        <input data-f="spec" data-id="${id}" value="${esc(ln.spec)}" placeholder="내용 (선택)">
        <label class="mini">원가 <input data-f="cost" data-id="${id}" value="${ln.cost == null ? '' : ln.cost}" inputmode="numeric" placeholder="0"></label></div>`;
    } else {
      const p = S.byCode[ln.code] || {};
      const colors = (p.colors || []).map((k) => `<option value="${esc(k)}"${ln.color === k ? ' selected' : ''}>${esc(label('color', k))}</option>`).join('');
      const closures = `<option value="">부자재 없음</option>` + (p.closures || []).map((k) => `<option value="${esc(k)}"${ln.closure === k ? ' selected' : ''}>${esc(label('closure', k))}</option>`).join('');
      const decos = (p.decorations || []).map((k) => `<button type="button" class="tg${(ln.decos || []).includes(k) ? ' is-on' : ''}" data-deco="${esc(k)}" data-id="${id}">${esc(label('deco', k))}</button>`).join('');
      left = `<div class="ln__p"><div class="ln__img">${thumb(p, ln.color)}</div><div class="ln__body">
        <div class="ln__name">${esc(p.code)} <span>${esc(p.name)}</span> <small>${p.capacity} mL · ${esc(p.neck || '')}</small></div>
        <div class="ln__opts"><select data-f="color" data-id="${id}">${colors}</select><select data-f="closure" data-id="${id}">${closures}</select></div>
        <div class="ln__decos">${decos}</div></div></div>`;
    }
    const priceTitle = ln.price != null ? `직접 입력한 단가 (자동 계산: ${won(r.auto)}원)` : '자동 계산된 단가 — 직접 바꿀 수 있습니다';
    return `<tr class="ln" data-row="${id}"><td class="c-no">${i}</td><td>${left}${miss}${moq}</td>
      <td class="c-qty"><input data-f="qty" data-id="${id}" value="${ln.qty}" inputmode="numeric"></td>
      <td class="c-int" data-k="cost">${won(r.cost)}</td>
      <td class="c-int c-m"><input data-f="margin" data-id="${id}" value="${ln.margin == null ? '' : ln.margin}" placeholder="${marginOf({ margin: null })}" inputmode="decimal"></td>
      <td class="c-price"><input class="${ln.price != null ? 'is-manual' : ''}" data-f="price" data-id="${id}" value="${r.price == null ? '' : r.price}" title="${esc(priceTitle)}" inputmode="numeric">
        ${ln.price != null ? `<button type="button" class="reset" data-reset="${id}" title="자동 단가로 되돌리기">↺</button>` : ''}</td>
      <td class="c-amt" data-k="amount">${won(r.amount)}</td>
      <td class="c-x"><button type="button" class="x" data-del="${id}" aria-label="삭제">×</button></td></tr>`;
  }

  function renderLines() {
    const c = compute(); let n = 0;
    $('#lines').innerHTML = c.rows.map((r) => lineRow(r, r.setup ? '' : ++n)).join('');
    $('#linesEmpty').hidden = S.draft.lines.length > 0;
    renderTotals(c);
  }
  function renderTotals(c = compute()) {
    $('#totals').innerHTML = `
      <div class="tot tot--int"><span>원가 합계 <small>내부</small></span><b>${won(c.costTotal)}원</b></div>
      <div class="tot tot--int"><span>예상 이익 <small>내부</small></span><b>${won(c.profit)}원 <small>(${(c.rate * 100).toFixed(1)}%)</small></b></div>
      <div class="tot"><span>공급가액</span><b>${won(c.supply)}원</b></div>
      ${set().vat ? `<div class="tot"><span>부가세 (10%)</span><b>${won(c.vat)}원</b></div>` : ''}
      <div class="tot tot--big"><span>합계</span><b>${won(c.total)}원</b></div>
      ${c.missingCount ? `<p class="warn">단가가 비어 있는 품목 ${c.missingCount}개 — 원가를 등록하거나 단가를 직접 입력하세요.</p>` : ''}`;
  }

  function fillQuoteForm() {
    const d = S.draft;
    $('#qNo').value = d.no; $('#qDate').value = d.date;
    $('#cCompany').value = d.customer.company; $('#cPerson').value = d.customer.person; $('#cTel').value = d.customer.tel; $('#cEmail').value = d.customer.email;
    $('#qDelivery').value = d.delivery; $('#qPayment').value = d.payment; $('#qValid').value = d.valid; $('#qMemo').value = d.memo;
    const m = d.margin != null ? d.margin : set().margin;
    $('#mNum').value = m; $('#mRange').value = Math.min(80, m);
    $('#mHow').textContent = set().method === 'margin' ? '판매가 기준' : '원가에 더하기';
    $('#qNoHint').textContent = d.savedAt ? `저장됨 · ${new Date(d.savedAt).toLocaleString('ko-KR')}` : '';
  }

  function renderOnboard() {
    const hasCost = Object.values(S.db.costs.products).some((c) => numOrNull(c.base) != null);
    const ob = $('#onboard'); ob.hidden = hasCost;
    if (!hasCost) {
      ob.innerHTML = `<b>처음 쓰시나요?</b>
        <ol><li><a href="#" data-goto="costs">원가 관리</a>에서 제품별 원견적을 등록하세요 (CSV로 한 번에 가능).</li>
        <li><a href="#" data-goto="settings">설정</a>에서 기본 마진율·끝자리·견적서 문구를 정하세요.</li>
        <li>여기서 제품을 고르고 수량만 넣으면 단가·합계가 자동으로 계산됩니다.</li></ol>`;
    }
  }

  function addProduct(code) {
    const p = S.byCode[code]; if (!p) return;
    S.draft.lines.push({ id: uid(), type: 'product', code, color: (p.colors || [])[0] || '', closure: (p.closures || [])[0] || '', decos: [], qty: p.moq || 1000, margin: null, price: null });
    saveDraft(); renderLines(); toast(`${p.code} 추가`);
  }

  /* ───────── 화면: 원가 관리 ───────── */
  function renderCosts() {
    const tiers = [...(set().tiers || [])].sort((a, b) => a - b);
    const q = S.costQ.trim().toLowerCase();
    const list = S.products.filter((p) => !q || (p.code + ' ' + p.name).toLowerCase().includes(q));
    const done = S.products.filter((p) => numOrNull((S.db.costs.products[p.code] || {}).base) != null).length;
    $('#costCount').textContent = `${done} / ${S.products.length}개 등록`;
    $('#costTable').innerHTML = `<thead><tr><th>품번</th><th>제품명</th><th class="r">용량</th><th class="r">MOQ</th><th class="r">기본 원가</th>
      ${tiers.map((t) => `<th class="r">${won(t)}개 이상</th>`).join('')}<th>메모</th></tr></thead><tbody>` +
      list.map((p) => {
        const c = S.db.costs.products[p.code] || {};
        return `<tr><td><b>${esc(p.code)}</b></td><td>${esc(p.name)}</td><td class="r">${p.capacity} mL</td><td class="r">${won(p.moq)}</td>
          <td class="r"><input data-cost="${esc(p.code)}" data-k="base" value="${c.base == null ? '' : c.base}" inputmode="decimal" placeholder="원"></td>
          ${tiers.map((t) => `<td class="r"><input data-cost="${esc(p.code)}" data-k="t${t}" value="${(c.tiers || {})[t] == null ? '' : c.tiers[t]}" inputmode="decimal"></td>`).join('')}
          <td><input class="memo" data-cost="${esc(p.code)}" data-k="note" value="${esc(c.note || '')}"></td></tr>`;
      }).join('') + '</tbody>';
    $('#closureTable').innerHTML = '<thead><tr><th>부자재</th><th class="r">개당 원가</th></tr></thead><tbody>' +
      (S.tax.closures || []).map((c) => `<tr><td>${esc(c.label)}</td><td class="r"><input data-cl="${esc(c.key)}" value="${(S.db.costs.closures[c.key] || {}).unit ?? ''}" inputmode="decimal" placeholder="원"></td></tr>`).join('') + '</tbody>';
    $('#decoTable').innerHTML = '<thead><tr><th>후가공</th><th class="r">개당 단가</th><th class="r">판비 (1회)</th></tr></thead><tbody>' +
      (S.tax.decorations || []).map((d) => { const v = S.db.costs.decorations[d.key] || {}; return `<tr><td>${esc(d.label)}</td>
        <td class="r"><input data-dc="${esc(d.key)}" data-k="unit" value="${v.unit ?? ''}" inputmode="decimal" placeholder="원"></td>
        <td class="r"><input data-dc="${esc(d.key)}" data-k="setup" value="${v.setup ?? ''}" inputmode="decimal" placeholder="원"></td></tr>`; }).join('') + '</tbody>';
  }

  function costTemplate() {
    const tiers = [...(set().tiers || [])].sort((a, b) => a - b);
    const head = ['품번', '제품명', '용량(mL)', 'MOQ', '기본원가', ...tiers.map((t) => `${t}개이상`), '메모'];
    const rows = S.products.map((p) => { const c = S.db.costs.products[p.code] || {}; return [p.code, p.name, p.capacity, p.moq, c.base ?? '', ...tiers.map((t) => (c.tiers || {})[t] ?? ''), c.note || '']; });
    download('동림_원가표.csv', toCSV([head, ...rows]), 'text/csv;charset=utf-8');
  }
  function importCosts(text) {
    const rows = parseCSV(text); if (rows.length < 2) { toast('CSV에 내용이 없습니다.', true); return; }
    const head = rows[0].map((h) => h.trim());
    const iCode = head.findIndex((h) => /품번|code/i.test(h));
    const iBase = head.findIndex((h) => /기본\s*원가|원가$|base|cost/i.test(h));
    const iNote = head.findIndex((h) => /메모|note/i.test(h));
    const tierCols = head.map((h, i) => { const m = h.replace(/,/g, '').match(/^(\d+)\s*개?\s*이상/); return m ? [i, Number(m[1])] : null; }).filter(Boolean);
    if (iCode < 0 || iBase < 0) { toast('‘품번’과 ‘기본원가’ 열이 필요합니다. CSV 양식을 내려받아 쓰세요.', true); return; }
    let ok = 0; const unknown = [];
    rows.slice(1).forEach((r) => {
      const code = (r[iCode] || '').trim(); if (!code) return;
      if (!S.byCode[code]) { unknown.push(code); return; }
      const c = S.db.costs.products[code] || { tiers: {} };
      const b = numOrNull(r[iBase]); c.base = b;
      c.tiers = c.tiers || {};
      tierCols.forEach(([i, t]) => { const v = numOrNull(r[i]); if (v == null) delete c.tiers[t]; else c.tiers[t] = v; });
      if (iNote >= 0) c.note = (r[iNote] || '').trim();
      S.db.costs.products[code] = c; ok++;
    });
    const newTiers = tierCols.map(([, t]) => t).filter((t) => !(set().tiers || []).includes(t));
    if (newTiers.length) set().tiers = [...(set().tiers || []), ...newTiers].sort((a, b) => a - b);
    changed(); renderCosts(); renderPicker(); renderLines(); renderOnboard();
    toast(`원가 ${ok}개 불러옴${unknown.length ? ` · 모르는 품번 ${unknown.length}개 건너뜀 (${unknown.slice(0, 3).join(', ')}${unknown.length > 3 ? '…' : ''})` : ''}`, unknown.length > 0);
  }

  /* ───────── 화면: 견적 기록 ───────── */
  function renderHistory() {
    const q = S.histQ.trim().toLowerCase();
    const list = [...S.db.quotes].sort((a, b) => (b.savedAt || '').localeCompare(a.savedAt || '')).filter((x) => !q || [x.no, x.customer && x.customer.company].join(' ').toLowerCase().includes(q));
    $('#histTable').innerHTML = `<thead><tr><th>견적번호</th><th>견적일</th><th>거래처</th><th class="r">품목</th><th class="r">합계</th><th class="r">이익률 <small>내부</small></th><th></th></tr></thead><tbody>` +
      (list.map((x) => `<tr><td><b>${esc(x.no)}</b></td><td>${esc(dotDate(x.date))}</td><td>${esc((x.customer || {}).company || '—')}</td>
        <td class="r">${(x.lines || []).length}</td><td class="r">${won(x.total)}원</td><td class="r">${x.rate != null ? (x.rate * 100).toFixed(1) + '%' : '—'}</td>
        <td class="r nowrap"><button type="button" class="btn btn--sm" data-open="${esc(x.id)}">불러오기</button>
        <button type="button" class="btn btn--sm" data-dup="${esc(x.id)}">복제</button>
        <button type="button" class="btn btn--sm btn--ghost" data-rm="${esc(x.id)}">삭제</button></td></tr>`).join('') ||
        '<tr><td colspan="7" class="empty">저장한 견적이 없습니다. 견적 작성 화면에서 <b>견적 저장</b>을 누르면 여기에 쌓입니다.</td></tr>') + '</tbody>';
  }

  /* ───────── 화면: 설정 ───────── */
  function fillSettings() {
    const s = set(); const co = company();
    $('#sMargin').value = s.margin;
    $$('input[name="sMethod"]').forEach((r) => { r.checked = r.value === s.method; });
    $('#sRound').value = String(s.round); $('#sRoundMode').value = s.roundMode; $('#sVat').checked = !!s.vat;
    $('#sTiers').value = (s.tiers || []).join(', ');
    $('#sPrefix').value = s.prefix; $('#sValidDays').value = s.validDays; $('#sDelivery').value = s.delivery; $('#sPayment').value = s.payment; $('#sMemo').value = s.memo;
    $('#sCoName').value = co.name || ''; $('#sCoCeo').value = co.ceo || ''; $('#sCoBiz').value = co.bizNo || ''; $('#sCoTel').value = co.tel || '';
    $('#sCoAddr').value = co.address || ''; $('#sCoMail').value = co.email || '';
    const conf = storeConf();
    $$('input[name="sStore"]').forEach((r) => { r.checked = r.value === conf.mode; });
    $('#sRepo').value = conf.repo || ''; $('#repoRow').hidden = conf.mode !== 'github';
    methodExample();
  }
  function methodExample() {
    const s = set(); const cost = 1000; const m = Number(s.margin) || 0;
    const p = roundPrice(applyMargin(cost, m));
    $('#sMethodEx').textContent = p == null ? '판매가 기준 마진율은 100% 미만이어야 합니다.' : `예) 원가 1,000원, 마진율 ${m}% → 단가 ${won(p)}원 (판매가 대비 이익 ${p ? ((p - cost) / p * 100).toFixed(1) : 0}%)`;
  }

  /* ───────── 견적서 (인쇄용) ───────── */
  function docHTML() {
    const c = compute(); const d = S.draft; const co = company();
    const bizWarn = !co.bizNo || /^0{3}-0{2}-0{5}$/.test(co.bizNo);
    let n = 0;
    const rows = c.rows.map((r) => `<tr><td class="c">${r.setup ? '' : ++n}</td><td><b>${esc(r.name)}</b><div class="spec">${esc(r.spec)}</div></td>
      <td class="r">${won(r.qty)}</td><td class="r">${r.price == null ? '별도 협의' : won(r.price)}</td><td class="r">${r.amount == null ? '—' : won(r.amount)}</td></tr>`).join('');
    const pad = Math.max(0, 8 - c.rows.length);
    return `
      <header class="doc__hd">
        <img src="../brand/logo/svg/donglim-horizontal.svg" alt="동림 Donglim" class="doc__logo">
        <h1>견 적 서</h1>
        <dl class="doc__meta"><div><dt>견적번호</dt><dd>${esc(d.no)}</dd></div><div><dt>견적일</dt><dd>${esc(dotDate(d.date))}</dd></div></dl>
      </header>
      <section class="doc__parties">
        <div class="doc__to"><p class="lbl">수신</p><p class="to">${esc(d.customer.company || '　')} <span>귀중</span></p>
          ${d.customer.person ? `<p>담당: ${esc(d.customer.person)}</p>` : ''}${d.customer.tel || d.customer.email ? `<p>${esc([d.customer.tel, d.customer.email].filter(Boolean).join(' · '))}</p>` : ''}
          <p class="intro">아래와 같이 견적합니다.</p></div>
        <table class="doc__from"><tbody>
          <tr><th>상호</th><td>${esc(co.name || '')}</td><th>대표</th><td>${esc(co.ceo || '')} <span class="seal">(인)</span></td></tr>
          <tr><th>사업자번호</th><td colspan="3">${esc(co.bizNo || '')}${bizWarn ? ' <span class="miss">← 설정에서 입력</span>' : ''}</td></tr>
          <tr><th>주소</th><td colspan="3">${esc(co.address || '')}</td></tr>
          <tr><th>전화</th><td>${esc(co.tel || '')}</td><th>이메일</th><td>${esc(co.email || '')}</td></tr>
        </tbody></table>
      </section>
      <div class="doc__sum"><span>합계금액${set().vat ? ' (부가세 포함)' : ''}</span><b>일금 ${koreanAmount(c.total)}원정</b><em>₩${won(c.total)}</em></div>
      <table class="doc__lines"><thead><tr><th class="c">No</th><th>품목 · 사양</th><th class="r">수량</th><th class="r">단가</th><th class="r">공급가액</th></tr></thead>
        <tbody>${rows}${'<tr class="pad"><td></td><td></td><td></td><td></td><td></td></tr>'.repeat(pad)}</tbody>
        <tfoot><tr><th colspan="4">공급가액</th><td class="r">${won(c.supply)}</td></tr>
          ${set().vat ? `<tr><th colspan="4">부가세 (10%)</th><td class="r">${won(c.vat)}</td></tr>` : ''}
          <tr class="grand"><th colspan="4">합계</th><td class="r">${won(c.total)}</td></tr></tfoot></table>
      <dl class="doc__terms">
        ${d.delivery ? `<div><dt>납기</dt><dd>${esc(d.delivery)}</dd></div>` : ''}${d.payment ? `<div><dt>결제 조건</dt><dd>${esc(d.payment)}</dd></div>` : ''}
        ${d.valid ? `<div><dt>유효기간</dt><dd>${esc(d.valid)}</dd></div>` : ''}${d.memo ? `<div><dt>비고</dt><dd>${esc(d.memo).replace(/\n/g, '<br>')}</dd></div>` : ''}
      </dl>
      <footer class="doc__ft">${esc(co.name || '동림')} ${esc(co.nameEn || '')} · ${esc(co.tel || '')} · ${esc(co.email || '')}</footer>`;
  }

  function quoteCSV(internal) {
    const c = compute(); const d = S.draft;
    const head = ['No', '품목', '사양', '수량', '단가', '공급가액', ...(internal ? ['원가(개당)', '마진율(%)', '원가합계', '이익'] : [])];
    let n = 0;
    const rows = c.rows.map((r) => [r.setup ? '' : ++n, r.name, r.spec, r.qty, r.price ?? '', r.amount ?? '',
      ...(internal ? [r.cost ?? '', r.m, r.cost != null ? r.cost * r.qty : '', r.amount != null && r.cost != null ? r.amount - r.cost * r.qty : ''] : [])]);
    const meta = [['견적번호', d.no], ['견적일', d.date], ['거래처', d.customer.company], ['담당자', d.customer.person], []];
    const tail = [[], ['', '', '', '', '공급가액', c.supply], ...(set().vat ? [['', '', '', '', '부가세', c.vat]] : []), ['', '', '', '', '합계', c.total],
      ...(internal ? [['', '', '', '', '원가합계', c.costTotal], ['', '', '', '', '이익', c.profit], ['', '', '', '', '이익률(%)', (c.rate * 100).toFixed(1)]] : [])];
    download(`견적서_${d.no}${internal ? '_내부용' : ''}.csv`, toCSV([...meta, head, ...rows, ...tail]), 'text/csv;charset=utf-8');
  }

  /* ───────── 이벤트 ───────── */
  function bind() {
    $$('.tab').forEach((b) => b.addEventListener('click', () => goto(b.dataset.tab)));
    document.addEventListener('click', (e) => { const a = e.target.closest('[data-goto]'); if (a) { e.preventDefault(); goto(a.dataset.goto); } });

    // 제품 선택
    $('#pickQ').addEventListener('input', (e) => { S.pick.q = e.target.value; renderPicker(); });
    $('#pickCats').addEventListener('click', (e) => { const b = e.target.closest('[data-cat]'); if (!b) return; S.pick.cat = b.dataset.cat; renderPicker(); });
    $('#pickList').addEventListener('click', (e) => { const b = e.target.closest('[data-add]'); if (b) addProduct(b.dataset.add); });

    // 견적 정보
    const bindDraft = (sel, fn) => $(sel).addEventListener('input', (e) => { fn(e.target.value); saveDraft(); });
    bindDraft('#qNo', (v) => { S.draft.no = v; S.draft.autoNo = false; });
    $('#qDate').addEventListener('change', (e) => {
      S.draft.date = e.target.value || today();
      if (S.draft.autoNo) S.draft.no = nextNo(S.draft.date);
      S.draft.valid = `견적일로부터 ${set().validDays}일 (${addDays(S.draft.date, Number(set().validDays) || 30)}까지)`;
      saveDraft(); fillQuoteForm();
    });
    [['#cCompany', 'company'], ['#cPerson', 'person'], ['#cTel', 'tel'], ['#cEmail', 'email']].forEach(([s, k]) => bindDraft(s, (v) => { S.draft.customer[k] = v; }));
    [['#qDelivery', 'delivery'], ['#qPayment', 'payment'], ['#qValid', 'valid'], ['#qMemo', 'memo']].forEach(([s, k]) => bindDraft(s, (v) => { S.draft[k] = v; }));

    const setMargin = (v) => { const n = numOrNull(v); S.draft.margin = n; $('#mNum').value = n ?? ''; $('#mRange').value = Math.min(80, n || 0); saveDraft(); renderLines(); };
    $('#mRange').addEventListener('input', (e) => setMargin(e.target.value));
    $('#mNum').addEventListener('change', (e) => setMargin(e.target.value));

    // 품목 표
    const tb = $('#lines');
    const find = (id) => S.draft.lines.find((l) => l.id === id);
    tb.addEventListener('change', (e) => {
      const el = e.target; const ln = find(el.dataset.id); if (!ln) return;
      const f = el.dataset.f;
      if (f === 'qty') ln.qty = Math.max(0, numOrNull(el.value) || 0);
      else if (f === 'margin') ln.margin = numOrNull(el.value);
      else if (f === 'price') ln.price = numOrNull(el.value);
      else if (f === 'cost') ln.cost = numOrNull(el.value);
      else ln[f] = el.value;
      saveDraft(); renderLines();
    });
    tb.addEventListener('click', (e) => {
      const t = e.target;
      const dl = t.closest('[data-del]'); if (dl) { S.draft.lines = S.draft.lines.filter((l) => l.id !== dl.dataset.del); saveDraft(); renderLines(); return; }
      const rs = t.closest('[data-reset]'); if (rs) { find(rs.dataset.reset).price = null; saveDraft(); renderLines(); return; }
      const dc = t.closest('[data-deco]');
      if (dc) { const ln = find(dc.dataset.id); const k = dc.dataset.deco; ln.decos = ln.decos.includes(k) ? ln.decos.filter((x) => x !== k) : [...ln.decos, k]; saveDraft(); renderLines(); }
    });
    $('#addCustom').addEventListener('click', () => { S.draft.lines.push({ id: uid(), type: 'custom', name: '', spec: '', qty: 1, cost: null, margin: null, price: null }); saveDraft(); renderLines(); });

    // 실행
    $('#printBtn').addEventListener('click', () => { $('#doc').innerHTML = docHTML(); $('#preview').hidden = false; document.body.classList.add('is-preview'); });
    $('#closePreview').addEventListener('click', () => { $('#preview').hidden = true; document.body.classList.remove('is-preview'); });
    $('#doPrint').addEventListener('click', () => { const t = document.title; document.title = `견적서_${S.draft.no}_${S.draft.customer.company || ''}`; window.print(); document.title = t; });
    $('#csvBtn').addEventListener('click', () => quoteCSV(false));
    $('#csvIntBtn').addEventListener('click', () => quoteCSV(true));
    $('#newBtn').addEventListener('click', () => { if (S.draft.lines.length && !confirm('지금 견적을 비우고 새로 시작할까요? (저장하지 않은 내용은 사라집니다)')) return; S.draft = newDraft(); saveDraft(); fillQuoteForm(); renderLines(); });
    $('#saveQuoteBtn').addEventListener('click', saveQuote);

    // 원가
    $('#costQ').addEventListener('input', (e) => { S.costQ = e.target.value; renderCosts(); });
    $('#costTpl').addEventListener('click', costTemplate);
    $('#costCsv').addEventListener('change', async (e) => { const f = e.target.files[0]; if (!f) return; importCosts(await readText(f)); e.target.value = ''; });
    $('#costTable').addEventListener('change', (e) => {
      const el = e.target; const code = el.dataset.cost; if (!code) return;
      const c = S.db.costs.products[code] || { tiers: {} }; c.tiers = c.tiers || {};
      const k = el.dataset.k;
      if (k === 'base') c.base = numOrNull(el.value);
      else if (k === 'note') c.note = el.value;
      else { const t = Number(k.slice(1)); const v = numOrNull(el.value); if (v == null) delete c.tiers[t]; else c.tiers[t] = v; }
      S.db.costs.products[code] = c; changed(); renderPicker(); renderLines(); renderOnboard();
      $('#costCount').textContent = `${S.products.filter((p) => numOrNull((S.db.costs.products[p.code] || {}).base) != null).length} / ${S.products.length}개 등록`;
    });
    $('#closureTable').addEventListener('change', (e) => { const k = e.target.dataset.cl; if (!k) return; S.db.costs.closures[k] = { unit: numOrNull(e.target.value) }; changed(); renderLines(); });
    $('#decoTable').addEventListener('change', (e) => {
      const k = e.target.dataset.dc; if (!k) return;
      const v = S.db.costs.decorations[k] || {}; v[e.target.dataset.k] = numOrNull(e.target.value); S.db.costs.decorations[k] = v; changed(); renderLines();
    });

    // 기록
    $('#histQ').addEventListener('input', (e) => { S.histQ = e.target.value; renderHistory(); });
    $('#histTable').addEventListener('click', (e) => {
      const o = e.target.closest('[data-open]'); const du = e.target.closest('[data-dup]'); const rm = e.target.closest('[data-rm]');
      const get = (id) => S.db.quotes.find((x) => x.id === id);
      if (o) { S.draft = JSON.parse(JSON.stringify(get(o.dataset.open).draft)); saveDraft(); fillQuoteForm(); renderLines(); goto('quote'); toast('견적을 불러왔습니다.'); }
      if (du) {
        const src = JSON.parse(JSON.stringify(get(du.dataset.dup).draft)); const nd = newDraft();
        S.draft = { ...src, id: uid(), no: nd.no, autoNo: true, date: nd.date, valid: nd.valid, savedAt: null };
        S.draft.lines.forEach((l) => { l.id = uid(); });
        saveDraft(); fillQuoteForm(); renderLines(); goto('quote'); toast('복제했습니다. 새 견적번호가 붙었습니다.');
      }
      if (rm && confirm('이 견적 기록을 삭제할까요?')) { S.db.quotes = S.db.quotes.filter((x) => x.id !== rm.dataset.rm); changed(); renderHistory(); if (S.store.mode === 'github') flush(); }
    });

    // 설정
    const sv = (fn) => (e) => { fn(e.target); changed(); methodExample(); fillQuoteForm(); renderLines(); };
    $('#sMargin').addEventListener('change', sv((el) => { set().margin = numOrNull(el.value) ?? 0; }));
    $$('input[name="sMethod"]').forEach((r) => r.addEventListener('change', sv((el) => { set().method = el.value; })));
    $('#sRound').addEventListener('change', sv((el) => { set().round = Number(el.value); }));
    $('#sRoundMode').addEventListener('change', sv((el) => { set().roundMode = el.value; }));
    $('#sVat').addEventListener('change', sv((el) => { set().vat = el.checked; }));
    $('#sTiers').addEventListener('change', (e) => {
      set().tiers = [...new Set(e.target.value.split(/[,\s]+/).map((x) => numOrNull(x)).filter((x) => x && x > 0))].sort((a, b) => a - b);
      e.target.value = set().tiers.join(', '); changed(); renderCosts(); renderLines();
    });
    [['#sPrefix', 'prefix'], ['#sValidDays', 'validDays'], ['#sDelivery', 'delivery'], ['#sPayment', 'payment'], ['#sMemo', 'memo']].forEach(([s, k]) => $(s).addEventListener('change', (e) => {
      set()[k] = k === 'validDays' ? (numOrNull(e.target.value) || 30) : e.target.value; changed();
      if (k === 'prefix' && S.draft.autoNo) { S.draft.no = nextNo(S.draft.date); saveDraft(); fillQuoteForm(); }
    }));
    [['#sCoName', 'name'], ['#sCoCeo', 'ceo'], ['#sCoBiz', 'bizNo'], ['#sCoTel', 'tel'], ['#sCoAddr', 'address'], ['#sCoMail', 'email']].forEach(([s, k]) => $(s).addEventListener('change', (e) => {
      set().company = { ...(set().company || {}), [k]: e.target.value }; changed();
    }));
    $$('input[name="sStore"]').forEach((r) => r.addEventListener('change', () => {
      if (!r.checked) return;
      $('#repoRow').hidden = r.value !== 'github';
      if (r.value === 'local' && S.store.mode !== 'local') switchStore({ mode: 'local' });
      if (r.value === 'github') $('#repoMsg').textContent = '비공개 저장소 이름을 넣고 ‘연결’을 누르세요. 관리자 페이지에서 GitHub로 로그인되어 있어야 합니다.';
    }));
    $('#repoCheck').addEventListener('click', () => { const repo = $('#sRepo').value.trim().replace(/^https?:\/\/github\.com\//, '').replace(/\.git$/, ''); if (!/^[\w.-]+\/[\w.-]+$/.test(repo)) { $('#repoMsg').textContent = '‘계정/저장소’ 형식으로 입력하세요.'; return; } switchStore({ mode: 'github', repo }); });
    $('#saveBtn').addEventListener('click', flush);
    $('#backupBtn').addEventListener('click', () => download(`동림_견적데이터_백업_${today()}.json`, JSON.stringify(S.db, null, 1), 'application/json'));
    $('#restoreFile').addEventListener('change', async (e) => {
      const f = e.target.files[0]; if (!f) return; e.target.value = '';
      try {
        const raw = JSON.parse(await readText(f)); if (!raw || !raw.costs) throw new Error();
        if (!confirm('백업 파일로 지금 데이터를 바꿀까요? (원가·설정·견적 기록 전체)')) return;
        S.db = mergeDB(raw); changed(); refreshAll(); toast('백업을 불러왔습니다.');
      } catch (err) { toast('동림 견적 백업 파일이 아닙니다.', true); }
    });

    window.addEventListener('beforeunload', (e) => { if (S.store.mode === 'github' && S.dirty) { e.preventDefault(); e.returnValue = ''; } });
  }

  const readText = (f) => new Promise((res, rej) => { const r = new FileReader(); r.onload = () => res(r.result); r.onerror = rej; r.readAsText(f, 'utf-8'); });

  function goto(tab) {
    $$('.tab').forEach((b) => b.classList.toggle('is-on', b.dataset.tab === tab));
    $$('.pane').forEach((p) => p.classList.toggle('is-on', p.id === 'pane-' + tab));
    if (tab === 'costs') renderCosts();
    if (tab === 'history') renderHistory();
    if (tab === 'settings') fillSettings();
  }

  async function saveQuote() {
    const c = compute();
    if (!S.draft.lines.length) { toast('품목이 없습니다.', true); return; }
    const ymd = S.draft.date.replace(/-/g, '').slice(2);
    const existing = S.db.quotes.find((x) => x.id === S.draft.id);
    if (!existing && S.draft.autoNo) { S.db.seq[ymd] = (S.db.seq[ymd] || 0) + 1; S.draft.no = `${set().prefix || 'DL'}-${ymd}-${String(S.db.seq[ymd]).padStart(2, '0')}`; }
    S.draft.savedAt = new Date().toISOString();
    const rec = { id: S.draft.id, no: S.draft.no, date: S.draft.date, customer: { ...S.draft.customer }, lines: S.draft.lines.map((l) => l.code || l.name), total: c.total, supply: c.supply, rate: c.rate, savedAt: S.draft.savedAt, draft: JSON.parse(JSON.stringify(S.draft)) };
    S.db.quotes = [...S.db.quotes.filter((x) => x.id !== rec.id), rec];
    saveDraft(); fillQuoteForm(); changed();
    if (S.store.mode === 'github') await flush(); else toast(`견적 ${S.draft.no} 저장 · 견적 기록에서 다시 열 수 있습니다.`);
  }

  async function switchStore(conf) {
    const st = makeStore(conf);
    if (st.mode === 'github') {
      $('#repoMsg').textContent = '연결 중…';
      try {
        const remote = await st.load();
        if (remote) { S.db = mergeDB(remote); $('#repoMsg').textContent = `연결됨 · ${conf.repo} 의 ${FILE} 를 불러왔습니다.`; }
        else {
          if (!confirm(`${conf.repo} 에 아직 데이터가 없습니다. 지금 이 브라우저의 원가·설정·견적 기록을 올릴까요?`)) { $('#repoMsg').textContent = '취소했습니다.'; return; }
          await st.save(S.db); $('#repoMsg').textContent = `연결됨 · ${conf.repo} 에 ${FILE} 를 만들었습니다.`;
        }
      } catch (e) {
        $('#repoMsg').textContent = e.message === 'NOLOGIN' ? '관리자 페이지(/donglim/admin/)에서 GitHub로 먼저 로그인한 뒤 다시 누르세요.' : e.message;
        $$('input[name="sStore"]').forEach((r) => { r.checked = r.value === storeConf().mode; });
        return;
      }
    } else {
      await LocalStore.save(S.db);
    }
    localStorage.setItem(STORE_KEY, JSON.stringify(conf));
    S.store = st; S.dirty = false; paintStore(); refreshAll();
    toast(st.mode === 'github' ? '비공개 저장소와 연결했습니다.' : '이 브라우저에 저장합니다.');
  }

  function refreshAll() { fillQuoteForm(); renderPicker(); renderLines(); renderOnboard(); renderCosts(); renderHistory(); fillSettings(); }

  /* ───────── 시작 ───────── */
  async function init() {
    const get = async (u) => (await fetch(u, { cache: 'no-cache' })).json();
    try {
      const [prod, tax, site] = await Promise.all([get('../content/products.json'), get('../content/taxonomy.json'), get('../content/site.json')]);
      S.products = (prod.items || prod).filter((p) => p.published !== false);
      S.tax = tax; S.site = site;
    } catch (e) { toast('제품 데이터를 불러오지 못했습니다. 잠시 후 새로고침하세요.', true); }
    S.byCode = Object.fromEntries(S.products.map((p) => [p.code, p]));
    const by = (l) => Object.fromEntries((l || []).map((x) => [x.key, x]));
    S.MAP = { color: by(S.tax.colors), closure: by(S.tax.closures), deco: by(S.tax.decorations), cat: by(S.tax.categories) };

    const conf = storeConf();
    S.store = makeStore(conf);
    try {
      S.db = mergeDB(await S.store.load());
    } catch (e) {
      // 비공개 저장소에 못 붙으면 마지막 사본으로 열고 알려줍니다.
      S.db = mergeDB(JSON.parse(localStorage.getItem(DB_KEY + '.cache') || localStorage.getItem(DB_KEY) || 'null'));
      setTimeout(() => toast((e.message === 'NOLOGIN' ? '관리자 페이지에서 GitHub로 로그인해야 비공개 저장소를 씁니다. ' : e.message + ' ') + '지금은 마지막 사본으로 열었습니다.', true), 300);
    }
    try { S.draft = JSON.parse(localStorage.getItem(DRAFT_KEY) || 'null'); } catch (e) { S.draft = null; }
    if (!S.draft) S.draft = newDraft();
    bind(); paintStore(); refreshAll(); goto('quote');
  }
  init();
})();
