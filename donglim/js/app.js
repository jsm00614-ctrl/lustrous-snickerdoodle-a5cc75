/*
 * app.js — 동림 홈페이지 동작
 * 모든 문구·제품 데이터는 content/*.json 에서 읽습니다. (관리자 페이지 /admin 에서 수정)
 */
(function () {
  'use strict';

  const CONTENT = 'content/';
  const LS_CART = 'donglim.cart.v1';
  const LS_VIEW = 'donglim.view.v1';
  const MAX_COMPARE = 3;
  const CAP_RANGES = [
    { key: '0-15', label: '15mL 이하', min: 0, max: 15 },
    { key: '15-50', label: '15 – 50mL', min: 15.01, max: 50 },
    { key: '50-100', label: '50 – 100mL', min: 50.01, max: 100 },
    { key: '100-9999', label: '100mL 이상', min: 100.01, max: 99999 },
  ];

  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => Array.from(el.querySelectorAll(s));
  const esc = (v) => String(v == null ? '' : v).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const num = (v) => Number(v).toLocaleString('ko-KR');
  const mm = (v) => (Number(v) % 1 ? Number(v).toFixed(1) : String(Number(v)));
  const store = {
    get(k, d) { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch (e) { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* 저장 불가 환경 무시 */ } },
  };

  let DATA = null; // { site, tax, products, services, faq }
  let MAP = {};
  const state = {
    cat: new Set(), mold: new Set(), cap: new Set(), neck: new Set(), color: new Set(), closure: new Set(), deco: new Set(),
    stock: false, lowmoq: false, q: '', sort: 'rec', view: store.get(LS_VIEW, 'grid'),
  };
  let cart = store.get(LS_CART, []);
  const compare = new Set();

  /* ---------- 데이터 로드 ---------- */
  async function getJSON(name) {
    const res = await fetch(CONTENT + name + '.json', { cache: 'no-cache' });
    if (!res.ok) throw new Error(name + ' ' + res.status);
    return res.json();
  }

  async function init() {
    try {
      const [site, tax, products, services, faq] = await Promise.all(['site', 'taxonomy', 'products', 'services', 'faq'].map(getJSON));
      DATA = { site, tax, products: (products.items || []).filter((p) => p.published !== false), services, faq };
    } catch (err) {
      console.error(err);
      $('#productList').innerHTML = '<p class="empty-state">콘텐츠를 불러오지 못했습니다. 웹 서버에서 열어주세요. (파일을 직접 더블클릭해서 열면 JSON을 읽을 수 없습니다)</p>';
      return;
    }
    const by = (arr) => Object.fromEntries((arr || []).map((x) => [x.key, x]));
    MAP = { mold: by(DATA.tax.moldTypes), cat: by(DATA.tax.categories), color: by(DATA.tax.colors), closure: by(DATA.tax.closures), deco: by(DATA.tax.decorations) };
    bindSite();
    renderHero();
    renderStrengths();
    renderFinder();
    renderCats();
    renderFilters();
    renderList();
    renderServices();
    renderDeco();
    renderNeckTable();
    renderProcess();
    renderMold();
    renderFaq();
    renderCart();
    wire();
  }

  /* ---------- 회사 정보 바인딩 ---------- */
  function pick(obj, path) { return path.split('.').reduce((o, k) => (o == null ? o : o[k]), obj); }
  function bindSite() {
    const s = DATA.site;
    $$('[data-site]').forEach((el) => {
      const v = pick(s, el.dataset.site);
      if (v == null) return;
      if (el.hasAttribute('data-multiline')) el.innerHTML = esc(v).replace(/\n/g, '<br>');
      else el.textContent = v;
    });
    $$('[data-site-href]').forEach((el) => {
      el.href = el.dataset.siteHref.replace(/\{([^}]+)\}/g, (_, k) => String(pick(s, k) || '').replace(/[^\w@.+\-]/g, ''));
    });
    const kakao = s.company && s.company.kakaoUrl;
    if (kakao) { ['#kakaoBtn', '#quickKakao'].forEach((id) => { const a = $(id); a.href = kakao; a.hidden = false; }); }
    if (s.company && s.company.catalogPdf) { const a = $('#catalogPdf'); a.href = s.company.catalogPdf; a.removeAttribute('data-inq-type'); a.target = '_blank'; }
    $('#stats').innerHTML = (s.stats || []).map((x) => `<div><dt>${esc(x.label)}</dt><dd>${esc(x.value)}</dd></div>`).join('');
    $('#year').textContent = new Date().getFullYear();
    if (s.company && s.company.name) document.title = `${s.company.name} ${s.company.nameEn || ''} — ${s.company.tagline || '화장품 유리용기'}`;
  }

  /* ---------- HERO ---------- */
  function renderHero() {
    const p = DATA.products.find((x) => x.badge === 'BEST' && x.shape === 'round') || DATA.products[0];
    if (!p) return;
    $('#heroCode').textContent = p.code;
    $('#heroDraw').innerHTML = Bottle.render(p, { mode: 'drawing', w: 380, h: 440, animate: true, color: MAP.color[p.colors[0]], closure: p.closures[0] });
    $('#heroSpec').innerHTML = `
      <span><i>CAP.</i>${mm(p.capacity)} mL</span>
      <span><i>FULL</i>${mm(p.fullCapacity)} mL</span>
      <span><i>WT.</i>${mm(p.weight)} g</span>
      <span><i>NECK</i>${esc(p.neck)}</span>`;
    $('.hero__sheet').addEventListener('click', () => openProduct(p.code));
  }

  function necks() {
    const set = new Set(DATA.products.map((p) => p.neck));
    // 나사형(20/410) → FEA 크림프 → 롤온(RO) → 광구(G) 순, 같은 종류는 지름순
    const kind = (n) => (/^\d/.test(n) ? 0 : /^FEA/i.test(n) ? 1 : /^RO/i.test(n) ? 2 : /^G/i.test(n) ? 3 : 4);
    const dia = (n) => parseFloat((String(n).match(/\d+(?:\.\d+)?/) || [0])[0]);
    return Array.from(set).filter(Boolean).sort((a, b) => kind(a) - kind(b) || dia(a) - dia(b) || a.localeCompare(b));
  }

  function renderFinder() {
    $('#fCat').insertAdjacentHTML('beforeend', DATA.tax.categories.map((c) => `<option value="${esc(c.key)}">${esc(c.label)}</option>`).join(''));
    $('#fNeck').insertAdjacentHTML('beforeend', necks().map((n) => `<option value="${esc(n)}">${esc(n)}</option>`).join(''));
    $('#finder').addEventListener('submit', (e) => {
      e.preventDefault();
      clearFilters(false);
      const c = $('#fCat').value, cap = $('#fCap').value, n = $('#fNeck').value;
      if (c) state.cat.add(c);
      if (cap) state.cap.add(cap);
      if (n) state.neck.add(n);
      refresh();
      scrollToCatalog();
    });
  }

  /* ---------- 카테고리 타일 ---------- */
  function renderCats() {
    $('#catTiles').innerHTML = DATA.tax.categories.map((c) => {
      const count = DATA.products.filter((p) => p.category === c.key).length;
      const sample = DATA.products.find((p) => p.category === c.key);
      return `<li><button type="button" class="cat" data-cat="${esc(c.key)}">
        <span class="cat__ic">${Bottle.icon(c.key, sample && { ...sample })}</span>
        <span class="cat__t">${esc(c.label)}</span>
        <span class="cat__d">${esc(c.desc || '')}</span>
        <span class="cat__n">${count}<small>품목</small></span>
      </button></li>`;
    }).join('');
    $('#catTiles').addEventListener('click', (e) => {
      const b = e.target.closest('[data-cat]');
      if (!b) return;
      clearFilters(false);
      state.cat.add(b.dataset.cat);
      refresh();
      scrollToCatalog();
    });
  }

  /* ---------- 필터 ---------- */
  function matches(p, skip) {
    if (skip !== 'cat' && state.cat.size && !state.cat.has(p.category)) return false;
    if (skip !== 'mold' && state.mold.size && !state.mold.has(p.moldType)) return false;
    if (skip !== 'cap' && state.cap.size && !CAP_RANGES.some((r) => state.cap.has(r.key) && p.capacity >= r.min && p.capacity <= r.max)) return false;
    if (skip !== 'neck' && state.neck.size && !state.neck.has(p.neck)) return false;
    if (skip !== 'color' && state.color.size && !(p.colors || []).some((c) => state.color.has(c))) return false;
    if (skip !== 'closure' && state.closure.size && !(p.closures || []).some((c) => state.closure.has(c))) return false;
    if (skip !== 'deco' && state.deco.size && !(p.decorations || []).some((c) => state.deco.has(c))) return false;
    if (skip !== 'stock' && state.stock && !p.stock) return false;
    if (skip !== 'lowmoq' && state.lowmoq && !(p.moq <= 1000)) return false;
    if (state.q) {
      const hay = [p.code, p.name, p.neck, p.summary, (MAP.cat[p.category] || {}).label, (MAP.mold[p.moldType] || {}).label].join(' ').toLowerCase();
      if (!state.q.toLowerCase().split(/\s+/).every((t) => hay.includes(t))) return false;
    }
    return true;
  }

  function facetCount(group, test) { return DATA.products.filter((p) => matches(p, group) && test(p)).length; }

  function renderFilters() {
    const g = (title, group, opts, type = 'check') => `
      <fieldset class="fg" data-group="${group}">
        <legend>${title}</legend>
        ${opts.map((o) => {
          const n = facetCount(group, o.test);
          const checked = state[group].has(o.key) ? 'checked' : '';
          const sw = type === 'swatch' ? `<i class="sw" style="--c:${esc(o.hex)};--o:${Number(o.opacity) || 0.6}"></i>` : '';
          return `<label class="fo ${n ? '' : 'is-zero'}"><input type="checkbox" value="${esc(o.key)}" ${checked}>${sw}<span>${esc(o.label)}</span><small>${n}</small></label>`;
        }).join('')}
      </fieldset>`;
    const t = DATA.tax;
    $('#filterBody').innerHTML =
      `<fieldset class="fg fg--toggle">
        <legend>출고 조건</legend>
        <label class="fo"><input type="checkbox" id="fStock" ${state.stock ? 'checked' : ''}><span>재고 즉시출고</span><small>${facetCount('stock', (p) => p.stock)}</small></label>
        <label class="fo"><input type="checkbox" id="fLowMoq" ${state.lowmoq ? 'checked' : ''}><span>소량 주문 (MOQ 1,000개 이하)</span><small>${facetCount('lowmoq', (p) => p.moq <= 1000)}</small></label>
      </fieldset>` +
      g('생산 방식', 'mold', (t.moldTypes || []).map((c) => ({ ...c, test: (p) => p.moldType === c.key }))) +
      g('용도', 'cat', t.categories.map((c) => ({ ...c, test: (p) => p.category === c.key }))) +
      g('용량', 'cap', CAP_RANGES.map((r) => ({ ...r, test: (p) => p.capacity >= r.min && p.capacity <= r.max }))) +
      g('넥 규격', 'neck', necks().map((n) => ({ key: n, label: n, test: (p) => p.neck === n }))) +
      g('유리 색상', 'color', t.colors.map((c) => ({ ...c, test: (p) => (p.colors || []).includes(c.key) })), 'swatch') +
      g('호환 부자재', 'closure', t.closures.map((c) => ({ ...c, test: (p) => (p.closures || []).includes(c.key) }))) +
      g('가능한 후가공', 'deco', t.decorations.map((c) => ({ ...c, test: (p) => (p.decorations || []).includes(c.key) })));
  }

  function clearFilters(doRefresh = true) {
    ['cat', 'mold', 'cap', 'neck', 'color', 'closure', 'deco'].forEach((k) => state[k].clear());
    state.stock = false; state.lowmoq = false; state.q = '';
    $('#catSearch').value = ''; $('#hdSearch').value = '';
    if (doRefresh) refresh();
  }

  function renderChips() {
    const chips = [];
    const lab = { mold: (k) => (MAP.mold[k] || {}).label, cat: (k) => (MAP.cat[k] || {}).label, cap: (k) => (CAP_RANGES.find((r) => r.key === k) || {}).label, neck: (k) => k, color: (k) => (MAP.color[k] || {}).label, closure: (k) => (MAP.closure[k] || {}).label, deco: (k) => (MAP.deco[k] || {}).label };
    Object.keys(lab).forEach((g) => state[g].forEach((k) => chips.push(`<button type="button" class="chip" data-g="${g}" data-k="${esc(k)}">${esc(lab[g](k) || k)} <span aria-hidden="true">×</span><span class="sr">필터 해제</span></button>`)));
    if (state.stock) chips.push('<button type="button" class="chip" data-g="stock">재고 즉시출고 ×</button>');
    if (state.lowmoq) chips.push('<button type="button" class="chip" data-g="lowmoq">소량 주문 ×</button>');
    if (state.q) chips.push(`<button type="button" class="chip" data-g="q">“${esc(state.q)}” ×</button>`);
    $('#activeChips').innerHTML = chips.join('') + (chips.length > 1 ? '<button type="button" class="link" data-g="all">전체 해제</button>' : '');
  }

  function sorted(list) {
    const rank = { BEST: 0, NEW: 1 };
    const s = state.sort;
    const order = DATA.tax.categories.map((c) => c.key);
    return list.slice().sort((a, b) => {
      if (s === 'capAsc') return a.capacity - b.capacity;
      if (s === 'capDesc') return b.capacity - a.capacity;
      if (s === 'moqAsc') return a.moq - b.moq || a.capacity - b.capacity;
      if (s === 'code') return a.code.localeCompare(b.code);
      return (order.indexOf(a.category) - order.indexOf(b.category)) || ((rank[a.badge] ?? 9) - (rank[b.badge] ?? 9)) || a.capacity - b.capacity;
    });
  }

  function dimText(p) {
    return Number(p.depth) > 0 ? `${mm(p.diameter)}×${mm(p.depth)}×H${mm(p.height)}` : `Ø${mm(p.diameter)}×H${mm(p.height)}`;
  }

  function dots(p, max = 6) {
    return `<span class="dots">${(p.colors || []).slice(0, max).map((k) => { const c = MAP.color[k] || {}; return `<i class="sw" style="--c:${esc(c.hex)};--o:${Number(c.opacity) || 0.6}" title="${esc(c.label)}"></i>`; }).join('')}</span>`;
  }

  function photos(p) {
    return [p.image].concat((p.gallery || []).map((g) => (typeof g === 'string' ? g : g && g.src))).filter(Boolean);
  }

  function figure(p, w = 220, h = 230) {
    if (p.image) return `<img src="${esc(p.image)}" alt="${esc(p.name)}" loading="lazy">`;
    return Bottle.render(p, { mode: 'card', w, h, color: MAP.color[(p.colors || [])[0]] });
  }

  function badges(p) {
    let b = '';
    if (p.badge) b += `<span class="bdg bdg--${esc(p.badge.toLowerCase())}">${esc(p.badge)}</span>`;
    if (p.stock) b += '<span class="bdg bdg--stock">재고</span>';
    if (MAP.mold[p.moldType]) b += `<span class="bdg bdg--mold bdg--${esc(p.moldType)}">${esc(MAP.mold[p.moldType].label)}</span>`;
    return b;
  }

  function badgeTop(p) {
    let b = '';
    if (p.badge) b += `<span class="bdg bdg--${esc(p.badge.toLowerCase())}">${esc(p.badge)}</span>`;
    if (p.stock) b += '<span class="bdg bdg--stock">재고</span>';
    return b;
  }

  function renderList() {
    const list = sorted(DATA.products.filter((p) => matches(p)));
    $('#resultCount').innerHTML = `<b>${list.length}</b>개 제품`;
    $$('.seg [data-view]').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.view === state.view)));
    const el = $('#productList');
    el.className = 'plist plist--' + state.view;
    if (!list.length) {
      el.innerHTML = '<div class="empty-state"><p>조건에 맞는 제품이 없습니다.</p><p>원하는 규격이 없다면 <a href="#inquiry" data-inq-type="개발">맞춤 개발</a>로 문의해 주세요.</p><button type="button" class="btn btn--line" data-g="all">필터 초기화</button></div>';
      return;
    }
    if (state.view === 'table') {
      el.innerHTML = `<div class="tbl-wrap"><table class="tbl tbl--spec">
        <thead><tr><th scope="col">품번</th><th scope="col">제품명</th><th scope="col" class="r">용량 (만수)</th><th scope="col">치수 mm</th><th scope="col">넥</th><th scope="col">생산</th><th scope="col" class="r">중량</th><th scope="col">색상</th><th scope="col" class="r">MOQ</th><th scope="col">출고</th><th scope="col"><span class="sr">담기</span></th></tr></thead>
        <tbody>${list.map((p) => `<tr data-open="${esc(p.code)}" tabindex="0">
          <td class="mono">${esc(p.code)}</td><td><b>${esc(p.name)}</b> ${badgeTop(p)}</td>
          <td class="r mono">${mm(p.capacity)} <small>(${mm(p.fullCapacity)})</small></td><td class="mono">${dimText(p)}</td>
          <td class="mono">${esc(p.neck)}</td><td>${esc((MAP.mold[p.moldType] || {}).label || '')}</td><td class="r mono">${mm(p.weight)}g</td><td>${dots(p)}</td>
          <td class="r mono">${num(p.moq)}</td><td class="${p.stock ? 'ok' : ''}">${esc(p.leadTime)}</td>
          <td><button type="button" class="add" data-add="${esc(p.code)}" aria-label="${esc(p.name)} 견적함 담기">+ 담기</button></td></tr>`).join('')}</tbody>
      </table></div>`;
      return;
    }
    el.innerHTML = list.map((p, i) => `
      <article class="card" style="--i:${i}">
        <button type="button" class="card__fig" data-open="${esc(p.code)}" aria-label="${esc(p.name)} 상세 보기">
          ${figure(p)}
          <span class="card__bdg">${badgeTop(p)}</span>
        </button>
        <div class="card__body">
          <p class="card__code mono">${esc(p.code)}</p>
          <h3 class="card__name"><button type="button" data-open="${esc(p.code)}">${esc(p.name)}</button></h3>
          <dl class="card__spec">
            <div><dt>용량</dt><dd>${mm(p.capacity)}<small>mL</small></dd></div>
            <div><dt>넥</dt><dd>${esc(p.neck)}</dd></div>
            <div><dt>치수</dt><dd>${dimText(p)}</dd></div>
            <div><dt>생산</dt><dd>${esc((MAP.mold[p.moldType] || {}).label || '-')}</dd></div>
          </dl>
          <div class="card__ft">
            ${dots(p)}
            <span class="card__moq">MOQ ${num(p.moq)}</span>
          </div>
          <div class="card__act">
            <label class="cmpbox"><input type="checkbox" data-compare="${esc(p.code)}" ${compare.has(p.code) ? 'checked' : ''}> 비교</label>
            <button type="button" class="add" data-add="${esc(p.code)}">+ 견적함</button>
          </div>
        </div>
      </article>`).join('');
  }

  function refresh() { renderFilters(); renderChips(); renderList(); }

  /* ---------- 제품 상세 ---------- */
  function product(code) { return DATA.products.find((p) => p.code === code); }

  function openProduct(code) {
    const p = product(code);
    if (!p) return;
    release3d();
    const cat = MAP.cat[p.category] || {};
    const sel = { color: (p.colors || [])[0], closure: (p.closures || [])[0] };
    const related = DATA.products.filter((x) => x.code !== p.code && x.neck === p.neck).slice(0, 4);
    const body = $('#pdBody');
    body.innerHTML = `
      <div class="pd__hd">
        <p class="pd__crumb">${esc(cat.label || '')} <span class="mono">/ ${esc(p.code)}</span></p>
        <button type="button" class="x" data-close aria-label="닫기">×</button>
      </div>
      <div class="pd__grid">
        <div class="pd__visual">
          <div class="pd__sheet">
            ${p.model3d ? '<div class="pd__tabs" role="tablist"><button type="button" role="tab" aria-selected="true" data-tab="draw">도면</button><button type="button" role="tab" aria-selected="false" data-tab="3d">3D</button></div>' : ''}
            <div class="pd__draw" id="pdDraw"></div>
            <div class="pd__3d" id="pd3d" hidden><p class="pd__3d-msg">3D 모델을 불러오는 중…</p></div>
          </div>
          ${photos(p).length ? `<ul class="pd__gallery">${photos(p).map((src, i) => `<li><a href="${esc(src)}" target="_blank" rel="noopener"><img src="${esc(src)}" alt="${esc(p.name)} 사진 ${i + 1}" loading="lazy"></a></li>`).join('')}</ul>` : ''}
          <div class="pd__opts">
            <div><b>유리 색상</b><div class="opt" id="optColor">${(p.colors || []).map((k) => { const c = MAP.color[k] || { label: k }; return `<button type="button" data-v="${esc(k)}" aria-pressed="${k === sel.color}"><i class="sw" style="--c:${esc(c.hex)};--o:${Number(c.opacity) || 0.6}"></i>${esc(c.label)}</button>`; }).join('')}</div></div>
            <div><b>호환 부자재</b><div class="opt" id="optClosure">${(p.closures || []).map((k) => `<button type="button" data-v="${esc(k)}" aria-pressed="${k === sel.closure}">${esc((MAP.closure[k] || {}).label || k)}</button>`).join('')}<button type="button" data-v="" aria-pressed="false">병만 보기</button></div></div>
          </div>
        </div>
        <div class="pd__info">
          <div class="pd__badges">${badges(p)}</div>
          <h2 id="pdTitle">${esc(p.name)}</h2>
          <p class="pd__sum">${esc(p.summary || '')}</p>
          <table class="tbl tbl--kv">
            <tbody>
              <tr><th scope="row">품번</th><td class="mono">${esc(p.code)}</td></tr>
              <tr><th scope="row">용량 / 만수</th><td class="mono">${mm(p.capacity)} mL / ${mm(p.fullCapacity)} mL</td></tr>
              <tr><th scope="row">치수</th><td class="mono">${Number(p.depth) > 0 ? `W ${mm(p.diameter)} × D ${mm(p.depth)}` : `Ø ${mm(p.diameter)}`} × H ${mm(p.height)} mm</td></tr>
              <tr><th scope="row">넥 규격</th><td class="mono">${esc(p.neck)}</td></tr>
              <tr><th scope="row">중량</th><td class="mono">${mm(p.weight)} g (±5%)</td></tr>
              <tr><th scope="row">생산 방식</th><td>${esc((MAP.mold[p.moldType] || {}).label || '-')} · 프리몰드 (보유 금형)${MAP.mold[p.moldType] ? `<small class="pd__mold">${esc(MAP.mold[p.moldType].desc || '')}</small>` : ''}</td></tr>
              <tr><th scope="row">재질</th><td>${esc(p.material || '소다석회 유리 (Soda-lime Glass)')}</td></tr>
              <tr><th scope="row">기본 MOQ</th><td class="mono">${num(p.moq)}개</td></tr>
              <tr><th scope="row">출고</th><td class="${p.stock ? 'ok' : ''}">${esc(p.leadTime)}</td></tr>
            </tbody>
          </table>
          <div class="pd__deco"><b>가능한 후가공</b><ul>${(p.decorations || []).map((k) => { const d = MAP.deco[k] || { label: k }; return `<li title="${esc(d.desc || '')}">${esc(d.label)}${d.moq ? `<small>${esc(d.moq)}</small>` : ''}</li>`; }).join('')}</ul></div>
          <div class="pd__buy">
            <label>예상 수량 <input type="number" id="pdQty" min="1" step="500" value="${Math.max(1000, p.moq)}"></label>
            <button type="button" class="btn btn--amber" id="pdAdd">견적함 담기</button>
            <button type="button" class="btn btn--line" id="pdSample">샘플 신청</button>
          </div>
          <div class="pd__sub">
            <button type="button" class="link" id="pdCompare">${compare.has(p.code) ? '비교함에서 빼기' : '+ 비교함에 추가'}</button>
            <button type="button" class="link" id="pdPrint">스펙시트 인쇄 · PDF 저장</button>
            <a class="link" href="#inquiry" data-inq-type="자료요청" data-inq-code="${esc(p.code)}">도면·3D 파일 요청</a>
          </div>
          ${related.length ? `<div class="pd__rel"><b>같은 넥(${esc(p.neck)}) 제품</b><ul>${related.map((r) => `<li><button type="button" data-open="${esc(r.code)}"><span class="pd__rel-fig">${figure(r, 70, 80)}</span><span>${esc(r.name)}<small class="mono">${mm(r.capacity)} mL</small></span></button></li>`).join('')}</ul></div>` : ''}
        </div>
      </div>`;

    const draw = () => { $('#pdDraw').innerHTML = Bottle.render(p, { mode: 'drawing', w: 380, h: 440, color: MAP.color[sel.color], closure: sel.closure || null }); };
    draw();
    if (p.model3d) {
      $('.pd__tabs').addEventListener('click', async (e) => {
        const b = e.target.closest('[data-tab]'); if (!b) return;
        const is3d = b.dataset.tab === '3d';
        $$('.pd__tabs button').forEach((x) => x.setAttribute('aria-selected', String(x === b)));
        $('#pdDraw').hidden = is3d; $('#pd3d').hidden = !is3d;
        if (is3d && !dispose3d) {
          try {
            const v = await import(new URL('js/viewer3d.js', location.href).href);
            dispose3d = await v.mount($('#pd3d'), p.model3d, { product: p, color: MAP.color[sel.color] });
          } catch (err) {
            console.error(err);
            $('#pd3d').innerHTML = '<p class="pd__3d-msg">3D 모델을 불러오지 못했습니다. 파일 형식(.glb/.gltf/.js)을 확인해 주세요.</p>';
          }
        }
      });
    }
    const optBind = (id, key) => $(id).addEventListener('click', (e) => {
      const b = e.target.closest('button'); if (!b) return;
      sel[key] = b.dataset.v;
      $$(id + ' button').forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
      draw();
    });
    optBind('#optColor', 'color');
    optBind('#optClosure', 'closure');
    $('#pdAdd').addEventListener('click', () => { addToCart(p.code, Number($('#pdQty').value) || p.moq, sel.color, sel.closure); });
    $('#pdSample').addEventListener('click', () => { addToCart(p.code, 3, sel.color, sel.closure, true); closeDialog(); goInquiry('샘플'); });
    $('#pdCompare').addEventListener('click', (e) => { toggleCompare(p.code); e.target.textContent = compare.has(p.code) ? '비교함에서 빼기' : '+ 비교함에 추가'; });
    $('#pdPrint').addEventListener('click', () => { document.body.classList.add('print-pd'); window.print(); });

    const dlg = $('#productDialog');
    if (!dlg.open) dlg.showModal();
    dlg.scrollTop = 0; body.scrollTop = 0;
  }

  let dispose3d = null;
  function release3d() { if (dispose3d) { try { dispose3d(); } catch (e) { /* 이미 해제됨 */ } dispose3d = null; } }
  function closeDialog() { $$('dialog[open]').forEach((d) => d.close()); }
  window.addEventListener('afterprint', () => document.body.classList.remove('print-pd'));

  /* ---------- 비교 ---------- */
  function toggleCompare(code, on) {
    const want = on == null ? !compare.has(code) : on;
    if (want) {
      if (compare.size >= MAX_COMPARE && !compare.has(code)) { toast(`비교는 최대 ${MAX_COMPARE}개까지 가능합니다.`); syncCompareBoxes(); return; }
      compare.add(code);
    } else compare.delete(code);
    renderTray();
    syncCompareBoxes();
  }
  function syncCompareBoxes() { $$('[data-compare]').forEach((c) => (c.checked = compare.has(c.dataset.compare))); }

  function renderTray() {
    const tray = $('#compareTray');
    tray.hidden = compare.size === 0;
    document.body.classList.toggle('has-tray', compare.size > 0);
    const slots = [...compare].map((c) => product(c)).filter(Boolean);
    $('#compareSlots').innerHTML = slots.map((p) => `<li><span class="mono">${esc(p.code)}</span> ${esc(p.name)} <button type="button" class="x" data-uncompare="${esc(p.code)}" aria-label="${esc(p.name)} 비교 해제">×</button></li>`).join('') +
      Array.from({ length: MAX_COMPARE - slots.length }, () => '<li class="empty">비어 있음</li>').join('');
  }

  function openCompare() {
    const ps = [...compare].map(product).filter(Boolean);
    if (ps.length < 2) { toast('비교할 제품을 2개 이상 골라주세요.'); return; }
    const rows = [
      ['용도', (p) => esc((MAP.cat[p.category] || {}).label)],
      ['생산 방식', (p) => esc((MAP.mold[p.moldType] || {}).label || '-')],
      ['용량 / 만수', (p) => `${mm(p.capacity)} / ${mm(p.fullCapacity)} mL`],
      ['치수', (p) => dimText(p) + ' mm'],
      ['넥 규격', (p) => esc(p.neck)],
      ['중량', (p) => mm(p.weight) + ' g'],
      ['유리 색상', (p) => (p.colors || []).map((k) => esc((MAP.color[k] || {}).label || k)).join('<br>')],
      ['호환 부자재', (p) => (p.closures || []).map((k) => esc((MAP.closure[k] || {}).label || k)).join('<br>')],
      ['후가공', (p) => (p.decorations || []).map((k) => esc((MAP.deco[k] || {}).label || k)).join('<br>')],
      ['MOQ', (p) => num(p.moq) + '개'],
      ['출고', (p) => esc(p.leadTime)],
    ];
    $('#compareBody').innerHTML = `<div class="tbl-wrap"><table class="tbl tbl--cmp">
      <thead><tr><th scope="col"><span class="sr">항목</span></th>${ps.map((p) => `<th scope="col"><div class="cmp__fig">${figure(p, 140, 150)}</div><span class="mono">${esc(p.code)}</span><b>${esc(p.name)}</b></th>`).join('')}</tr></thead>
      <tbody>${rows.map(([k, f]) => { const vals = ps.map(f); const diff = new Set(vals).size > 1; return `<tr class="${diff ? 'diff' : ''}"><th scope="row">${k}</th>${vals.map((v) => `<td>${v}</td>`).join('')}</tr>`; }).join('')}
      <tr><th scope="row"></th>${ps.map((p) => `<td><button type="button" class="add" data-add="${esc(p.code)}">+ 견적함</button></td>`).join('')}</tr></tbody>
    </table></div><p class="cmp__note">값이 다른 항목은 강조 표시됩니다.</p>`;
    $('#compareDialog').showModal();
  }

  /* ---------- 견적함 ---------- */
  function saveCart() { store.set(LS_CART, cart); renderCart(); }
  function addToCart(code, qty, color, closure, sample) {
    const p = product(code); if (!p) return;
    const ex = cart.find((c) => c.code === code && c.color === (color || p.colors[0]));
    if (ex) { ex.qty = qty || ex.qty; if (closure !== undefined) ex.closure = closure; if (sample) ex.sample = true; }
    else cart.push({ code, qty: qty || p.moq, color: color || (p.colors || [])[0], closure: closure === undefined ? (p.closures || [])[0] : closure, sample: !!sample });
    saveCart();
    toast(`${p.name}을(를) 견적함에 담았습니다.`, true);
    const btn = $('#openCart'); btn.classList.remove('bump'); void btn.offsetWidth; btn.classList.add('bump');
  }

  function renderCart() {
    cart = cart.filter((c) => product(c.code) || !DATA);
    const n = cart.length;
    $('#cartCount').textContent = n; $('#quickCount').textContent = n;
    if (!DATA) return;
    $('#cartList').innerHTML = n ? cart.map((c, i) => {
      const p = product(c.code);
      return `<li class="cart__it">
        <div class="cart__fig">${figure(p, 64, 76)}</div>
        <div class="cart__info">
          <p><span class="mono">${esc(p.code)}</span> <b>${esc(p.name)}</b></p>
          <p class="cart__meta">${mm(p.capacity)} mL · ${esc(p.neck)}</p>
          <div class="cart__ctl">
            <label><span class="sr">색상</span><select data-ci="${i}" data-f="color">${(p.colors || []).map((k) => `<option value="${esc(k)}" ${k === c.color ? 'selected' : ''}>${esc((MAP.color[k] || {}).label || k)}</option>`).join('')}</select></label>
            <label><span class="sr">부자재</span><select data-ci="${i}" data-f="closure"><option value="">병만</option>${(p.closures || []).map((k) => `<option value="${esc(k)}" ${k === c.closure ? 'selected' : ''}>${esc((MAP.closure[k] || {}).label || k)}</option>`).join('')}</select></label>
            <label class="cart__qty">수량 <input type="number" min="1" step="500" value="${Number(c.qty) || p.moq}" data-ci="${i}" data-f="qty"></label>
          </div>
        </div>
        <button type="button" class="x" data-remove="${i}" aria-label="${esc(p.name)} 삭제">×</button>
      </li>`;
    }).join('') : '<li class="cart__empty">담은 제품이 없습니다.<br>제품 카드의 <b>+ 견적함</b>을 눌러 추가하세요.</li>';
    renderFormItems();
  }

  function cartText() {
    return cart.map((c, i) => {
      const p = product(c.code);
      return `${i + 1}. [${p.code}] ${p.name} / ${mm(p.capacity)}mL / 넥 ${p.neck} / 색상 ${(MAP.color[c.color] || {}).label || c.color} / 부자재 ${(MAP.closure[c.closure] || {}).label || '없음(병만)'} / 수량 ${num(c.qty)}${c.sample ? ' / 샘플 요청' : ''}`;
    }).join('\n');
  }

  function renderFormItems() {
    $('#formItems').innerHTML = cart.length ? cart.map((c) => {
      const p = product(c.code);
      return `<li><span class="mono">${esc(p.code)}</span> ${esc(p.name)} <small>${esc((MAP.color[c.color] || {}).label || '')} · ${num(c.qty)}개${c.sample ? ' · 샘플' : ''}</small></li>`;
    }).join('') : '<li class="empty">견적함이 비어 있습니다. 제품 목록에서 <b>견적함 담기</b>를 눌러 추가하세요.</li>';
    $('#itemsField').value = cartText();
  }

  function openCart() { const d = $('#cartDrawer'); d.classList.add('is-open'); d.setAttribute('aria-hidden', 'false'); document.body.classList.add('no-scroll'); setTimeout(() => $('.drawer__panel .x').focus(), 50); }
  function closeCart() { const d = $('#cartDrawer'); d.classList.remove('is-open'); d.setAttribute('aria-hidden', 'true'); document.body.classList.remove('no-scroll'); }

  function goInquiry(type, code) {
    closeCart(); closeDialog();
    if (type) { const r = $(`#inqForm input[name="type"][value="${type}"]`); if (r) r.checked = true; }
    if (code) { const ta = $('#inqForm textarea[name="message"]'); if (!ta.value.includes(code)) ta.value = (ta.value ? ta.value + '\n' : '') + `${code} 도면·3D 파일 요청`; }
    $('#inquiry').scrollIntoView({ behavior: 'smooth' });
  }

  /* ---------- 정적 섹션 ---------- */
  const SVC_ICON = {
    sample: '<path d="M9 3h6M10 3v6l-5 9a2 2 0 0 0 2 3h10a2 2 0 0 0 2-3l-5-9V3"/><path d="M7.5 15h9"/>',
    stock: '<path d="M3 8l9-5 9 5v8l-9 5-9-5z"/><path d="M3 8l9 5 9-5M12 13v8"/>',
    match: '<rect x="8" y="2" width="8" height="5" rx="1"/><path d="M9 7v3M15 7v3"/><path d="M7 10h10l1 3v7a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2v-7z"/>',
    deco: '<path d="M4 20l4-1 11-11-3-3L5 16z"/><path d="M14 6l3 3"/>',
    mold: '<rect x="3" y="3" width="18" height="18" rx="1"/><path d="M12 6v12M8 9c0-1.5 1.8-3 4-3s4 1.5 4 3v6c0 1.5-1.8 3-4 3s-4-1.5-4-3z"/>',
    file: '<path d="M6 2h9l5 5v15H6z"/><path d="M14 2v6h6M9 13h8M9 17h6"/>',
  };
  function renderServices() {
    $('#svcList').innerHTML = (DATA.services.services || []).map((s, i) => `
      <li class="svc__it" style="--i:${i}">
        <svg class="svc__ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${SVC_ICON[s.icon] || SVC_ICON.file}</svg>
        <h3>${esc(s.title)}</h3><p>${esc(s.desc)}</p><span class="svc__meta">${esc(s.meta || '')}</span>
      </li>`).join('');
  }

  function renderDeco() {
    $('#decoList').innerHTML = DATA.tax.decorations.map((d, i) => `
      <li class="deco__it">
        <span class="deco__sw deco__sw--${esc(d.key)}" aria-hidden="true"></span>
        <div><h3>${esc(d.label)}</h3><p>${esc(d.desc || '')}</p><span class="deco__moq">MOQ ${esc(d.moq || '문의')}</span></div>
        <span class="deco__n mono">${String(i + 1).padStart(2, '0')}</span>
      </li>`).join('');
  }

  function renderNeckTable() {
    $('#neckTable tbody').innerHTML = necks().map((n) => {
      const ps = DATA.products.filter((p) => p.neck === n);
      const cl = [...new Set(ps.flatMap((p) => p.closures || []))].map((k) => esc((MAP.closure[k] || {}).label || k)).join(', ');
      return `<tr><td class="mono"><b>${esc(n)}</b></td><td class="mono">${ps.length}</td><td>${cl}</td><td><button type="button" class="link" data-neck="${esc(n)}">보기 →</button></td></tr>`;
    }).join('');
  }

  function renderStrengths() {
    $('#strList').innerHTML = (DATA.site.strengths || []).map((s, i) => `
      <li class="str__it">
        <span class="str__no mono">${esc(s.no || String(i + 1).padStart(2, '0'))}</span>
        <h3>${esc(s.title)}</h3>
        <p>${esc(s.desc)}</p>
        ${(s.points || []).length ? `<ul>${s.points.map((x) => `<li>${esc(x)}</li>`).join('')}</ul>` : ''}
      </li>`).join('');
  }

  function renderMold() {
    const mc = DATA.services.moldCompare || {};
    $('#moldTable tbody').innerHTML = (mc.rows || []).map((r) => `<tr><th scope="row">${esc(r.label)}</th><td>${esc(r.auto)}</td><td>${esc(r.manual)}</td></tr>`).join('');
    $('#moldNote').textContent = mc.note || '';
  }

  function renderProcess() {
    $('#procList').innerHTML = (DATA.services.process || []).map((s, i) => `
      <li class="step"><span class="step__n mono">${String(i + 1).padStart(2, '0')}</span><h3>${esc(s.title)}</h3><p>${esc(s.desc)}</p><span class="step__d">${esc(s.duration || '')}</span></li>`).join('');
  }

  function renderFaq() {
    $('#faqList').innerHTML = (DATA.faq.items || []).map((f) => `<details class="qa"><summary>${esc(f.q)}</summary><p>${esc(f.a)}</p></details>`).join('');
  }

  /* ---------- 공통 ---------- */
  let toastT;
  function toast(msg, withCart) {
    const t = $('#toast');
    t.innerHTML = esc(msg) + (withCart ? ' <button type="button" class="link" data-open-cart>견적함 보기</button>' : '');
    t.classList.add('is-on');
    clearTimeout(toastT); toastT = setTimeout(() => t.classList.remove('is-on'), 3200);
  }
  function scrollToCatalog() { $('#catalog').scrollIntoView({ behavior: 'smooth' }); }

  function wire() {
    // 전역 클릭 위임
    document.addEventListener('click', (e) => {
      const t = e.target;
      const open = t.closest('[data-open]'); if (open && !t.closest('[data-add]') && !t.closest('.cmpbox')) { openProduct(open.dataset.open); return; }
      const add = t.closest('[data-add]'); if (add) { const p = product(add.dataset.add); addToCart(p.code, p.moq); return; }
      const g = t.closest('[data-g]');
      if (g) {
        const k = g.dataset.g;
        if (k === 'all') clearFilters(false);
        else if (k === 'stock' || k === 'lowmoq') state[k] = false;
        else if (k === 'q') { state.q = ''; $('#catSearch').value = ''; $('#hdSearch').value = ''; }
        else state[k].delete(g.dataset.k);
        refresh(); return;
      }
      const inq = t.closest('[data-inq-type]'); if (inq) { e.preventDefault(); goInquiry(inq.dataset.inqType, inq.dataset.inqCode); return; }
      const nk = t.closest('[data-neck]'); if (nk) { clearFilters(false); state.neck.add(nk.dataset.neck); refresh(); scrollToCatalog(); return; }
      if (t.closest('[data-close]')) { closeDialog(); return; }
      if (t.closest('[data-close-cart]')) { closeCart(); return; }
      if (t.closest('[data-open-cart]')) { openCart(); return; }
      const goi = t.closest('[data-go-inq]'); if (goi) { if (goi.dataset.goInq === '샘플') cart.forEach((c) => (c.sample = true)), saveCart(); goInquiry(goi.dataset.goInq); return; }
      const rm = t.closest('[data-remove]'); if (rm) { cart.splice(Number(rm.dataset.remove), 1); saveCart(); return; }
      const unc = t.closest('[data-uncompare]'); if (unc) { toggleCompare(unc.dataset.uncompare, false); return; }
    });
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && e.target.matches('tr[data-open]')) openProduct(e.target.dataset.open);
      if (e.key === 'Escape') closeCart();
    });
    document.addEventListener('change', (e) => {
      const t = e.target;
      if (t.matches('[data-compare]')) toggleCompare(t.dataset.compare, t.checked);
      if (t.matches('[data-ci]')) { const c = cart[Number(t.dataset.ci)]; if (c) { c[t.dataset.f] = t.dataset.f === 'qty' ? Math.max(1, Number(t.value) || 1) : t.value; saveCart(); } }
    });
    // 다이얼로그 바깥 클릭 닫기
    $$('dialog').forEach((d) => d.addEventListener('click', (e) => { if (e.target === d) d.close(); }));
    $('#productDialog').addEventListener('close', release3d);

    // 필터
    $('#filterBody').addEventListener('change', (e) => {
      const t = e.target;
      if (t.id === 'fStock') state.stock = t.checked;
      else if (t.id === 'fLowMoq') state.lowmoq = t.checked;
      else { const g = t.closest('[data-group]'); if (!g) return; const set = state[g.dataset.group]; t.checked ? set.add(t.value) : set.delete(t.value); }
      refresh();
    });
    $('#resetFilters').addEventListener('click', () => clearFilters());
    $('#openFilters').addEventListener('click', () => { $('#filters').classList.add('is-open'); document.body.classList.add('no-scroll'); });
    $('#closeFilters').addEventListener('click', () => { $('#filters').classList.remove('is-open'); document.body.classList.remove('no-scroll'); });

    // 검색·정렬·보기
    let qT;
    const onSearch = (v, scroll) => { clearTimeout(qT); qT = setTimeout(() => { state.q = v.trim(); refresh(); if (scroll && state.q) scrollToCatalog(); }, 180); };
    $('#catSearch').addEventListener('input', (e) => { $('#hdSearch').value = e.target.value; onSearch(e.target.value); });
    $('#hdSearch').addEventListener('input', (e) => { $('#catSearch').value = e.target.value; onSearch(e.target.value); });
    $('#hdSearch').addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); onSearch(e.target.value, true); } });
    $('#sortSel').addEventListener('change', (e) => { state.sort = e.target.value; renderList(); });
    $$('.seg [data-view]').forEach((b) => b.addEventListener('click', () => { state.view = b.dataset.view; store.set(LS_VIEW, state.view); renderList(); }));

    // 견적함·비교
    $('#openCart').addEventListener('click', openCart);
    $('#quickCart').addEventListener('click', openCart);
    $('#formOpenCart').addEventListener('click', openCart);
    $('#openCompare').addEventListener('click', openCompare);
    $('#clearCompare').addEventListener('click', () => { compare.clear(); renderTray(); syncCompareBoxes(); });

    // 모바일 메뉴
    $('#menuBtn').addEventListener('click', () => {
      const on = $('#hd').classList.toggle('is-menu');
      $('#menuBtn').setAttribute('aria-expanded', String(on));
    });
    $$('.gnb a').forEach((a) => a.addEventListener('click', () => { $('#hd').classList.remove('is-menu'); $('#menuBtn').setAttribute('aria-expanded', 'false'); }));

    // 헤더 그림자
    const hd = $('#hd');
    const onScroll = () => hd.classList.toggle('is-scrolled', window.scrollY > 8);
    window.addEventListener('scroll', onScroll, { passive: true }); onScroll();

    // 문의 폼 (Netlify Forms)
    $('#inqForm').addEventListener('submit', async (e) => {
      e.preventDefault();
      const f = e.target; const msg = $('#formMsg'); const btn = f.querySelector('[type="submit"]');
      $('#itemsField').value = cartText();
      btn.disabled = true; msg.className = 'form__msg'; msg.textContent = '보내는 중…';
      try {
        const res = await fetch(location.pathname, { method: 'POST', body: new FormData(f) });
        if (!res.ok) throw new Error(res.status);
        msg.classList.add('is-ok');
        msg.textContent = '문의가 접수되었습니다. 영업일 기준 하루 안에 연락드리겠습니다.';
        f.reset(); cart = []; saveCart();
      } catch (err) {
        msg.classList.add('is-err');
        const tel = (DATA.site.company || {}).tel || '';
        msg.textContent = `전송에 실패했습니다. 잠시 후 다시 시도하시거나 ${tel} 로 연락해 주세요.`;
      } finally { btn.disabled = false; }
    });

    // 스크롤 등장 효과
    if ('IntersectionObserver' in window) {
      const io = new IntersectionObserver((ents) => ents.forEach((en) => { if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); } }), { rootMargin: '0px 0px -10% 0px' });
      $$('.sec-hd, .svc__it, .deco__it, .step, .cat, .str__it').forEach((el) => { el.classList.add('reveal'); io.observe(el); });
    }
  }

  document.addEventListener('DOMContentLoaded', init);
})();
