/*
 * bottle.js — 제품 스펙(mm)으로 유리용기 SVG를 그립니다.
 * 사진이 없는 제품도 실제 비율대로 보이도록, CMS에 입력한 높이·지름·넥 규격을 그대로 사용합니다.
 * CMS에서 제품 사진(image)을 올리면 카드에는 사진이 먼저 표시됩니다.
 */
window.Bottle = (function () {
  let uid = 0;
  const INK = '#2d4350';          // 차가운 회청색 윤곽선
  const CAP = '#e3e9ec';          // 마개(부자재) 색
  const DIM = '#2a8197';          // 치수선 색

  function neckDia(neck) {
    const m = String(neck || '').match(/(\d+(?:\.\d+)?)/);
    return m ? parseFloat(m[1]) : 20;
  }

  function geometry(p) {
    const H = Number(p.height) || 80;
    const D = Number(p.diameter) || 30;
    const R = D / 2;
    const n = Math.min(neckDia(p.neck) / 2, R * 0.9);
    let nh, sh, rc;
    switch (p.shape) {
      case 'jar': nh = Math.min(9, H * 0.2); sh = Math.min(4, H * 0.08); rc = Math.min(6, R * 0.18); break;
      case 'perfume': nh = 9; sh = 0; rc = 2; break;
      case 'vial': nh = Math.min(10, H * 0.17); sh = Math.min(R * 0.9, H * 0.12); rc = R * 0.35; break;
      case 'square': nh = 12; sh = Math.min(R * 0.5, H * 0.12); rc = 2.5; break;
      case 'boston': nh = 12; sh = Math.min(R * 0.95, H * 0.26); rc = R * 0.25; break;
      default: nh = 12; sh = Math.min(R * 0.8, H * 0.18); rc = R * 0.2;
    }
    const weight = Number(p.weight) || 0;
    const cap = Math.max(Number(p.capacity) || 1, 1);
    const baseT = Math.min(H * 0.22, 2 + (weight / cap) * 2.2);
    return { H, D, R, n, nh, sh, rc, baseT, top: -H, nb: -H + nh, sb: -H + nh + sh };
  }

  function bodyPath(p, g) {
    const { R, n, rc, top, nb, sb, sh } = g;
    if (p.shape === 'perfume') {
      const c = 3;
      return `M${-n},${top} L${-n},${nb} L${-R + c},${nb} L${-R},${nb + c} L${-R},${-c} L${-R + c},0 L${R - c},0 L${R},${-c} L${R},${nb + c} L${R - c},${nb} L${n},${nb} L${n},${top} Z`;
    }
    let c1x, c1y, c2x, c2y;
    if (p.shape === 'boston') { c1x = -n - (R - n) * 0.6; c1y = nb; c2x = -R; c2y = nb + sh * 0.35; }
    else if (p.shape === 'square') { c1x = -R * 0.8; c1y = nb; c2x = -R; c2y = nb + sh * 0.35; }
    else if (p.shape === 'jar') { c1x = -R; c1y = nb; c2x = -R; c2y = nb; }
    else { c1x = -n; c1y = nb + sh * 0.55; c2x = -R; c2y = sb - sh * 0.55; }
    return `M${-n},${top} L${-n},${nb} C${c1x},${c1y} ${c2x},${c2y} ${-R},${sb} L${-R},${-rc} Q${-R},0 ${-R + rc},0 L${R - rc},0 Q${R},0 ${R},${-rc} L${R},${sb} C${-c2x},${c2y} ${-c1x},${c1y} ${n},${nb} L${n},${top} Z`;
  }

  /* 부자재(마개) — 병 위쪽에 그림. 반환값의 top은 가장 높은 y(음수), half는 좌우 최대 폭의 절반 */
  function closure(type, p, g, sw, solid) {
    const { n, nh, nb, top, R, H } = g;
    const fill = solid ? CAP : 'rgba(250,252,253,.6)';
    const st = `fill="${fill}" stroke="${INK}" stroke-width="${sw}" ${solid ? '' : `stroke-dasharray="${sw * 2.4} ${sw * 2}" stroke-opacity=".65"`}`;
    let out = '', t = top, half = n + 1.5;
    const rect = (x, y, w, h, r = 0.8) => `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${r}" ${st}/>`;
    switch (type) {
      case 'cap': {
        const w = 2 * n + 3, h = nh + Math.max(6, n * 0.7);
        t = nb - 1 - h; out = rect(-w / 2, t, w, h, 1.2);
        for (let i = 1; i < 6; i++) out += `<line x1="${-w / 2 + (w / 6) * i}" y1="${t + 2}" x2="${-w / 2 + (w / 6) * i}" y2="${t + h - 2}" stroke="${INK}" stroke-width="${sw * 0.6}" stroke-opacity=".25"/>`;
        half = w / 2; break;
      }
      case 'lid': {
        const w = Math.min(2 * R, 2 * n + 9), h = nh + 7;
        t = nb - 0.5 - h; out = rect(-w / 2, t, w, h, 2.2);
        out += `<line x1="${-w / 2}" y1="${t + h * 0.72}" x2="${w / 2}" y2="${t + h * 0.72}" stroke="${INK}" stroke-width="${sw * 0.7}" stroke-opacity=".35"/>`;
        half = w / 2; break;
      }
      case 'pump': {
        const cw = 2 * n + 3, chh = nh + 2; const ct = nb - 1 - chh;
        const aw = Math.max(12, 2 * n * 0.95), ah = 11; const at = ct - 7 - ah;
        out = rect(-cw / 2, ct, cw, chh, 1) + rect(-1.8, ct - 7, 3.6, 7.5, 0.4) + rect(-aw / 2, at, aw, ah, 2) + rect(-aw / 2 - 11, at + 2.5, 11.5, 3.6, 0.8);
        out += `<line x1="0" y1="${nb}" x2="0" y2="${-g.baseT - 2}" stroke="${INK}" stroke-width="${sw * 0.7}" stroke-opacity=".3" stroke-dasharray="${sw * 2} ${sw * 2}"/>`;
        t = at; half = Math.max(cw / 2, aw / 2 + 11); break;
      }
      case 'dropper': {
        const cw = 2 * n + 3, chh = nh + 3; const ct = nb - 1 - chh;
        const bw = Math.max(8, 2 * n * 0.78), bh = Math.max(16, n * 2.3);
        const r = bw / 2;
        out = rect(-cw / 2, ct, cw, chh, 1);
        out += `<path d="M${-r},${ct} L${-r},${ct - bh + r} A${r},${r} 0 0 1 ${r},${ct - bh + r} L${r},${ct} Z" ${st}/>`;
        out += `<path d="M-1.6,${nb} L-1.6,${-g.baseT - 4} Q0,${-g.baseT - 1} 1.6,${-g.baseT - 4} L1.6,${nb}" fill="none" stroke="${INK}" stroke-width="${sw * 0.7}" stroke-opacity=".35"/>`;
        t = ct - bh; half = cw / 2; break;
      }
      case 'spray': {
        const fw = 2 * n + 3, fh = nh + 1; const ft = nb - fh;
        const aw = 2 * n - 1, ah = 10;
        out = rect(-fw / 2, ft, fw, fh, 0.8) + rect(-aw / 2, ft - ah - 1, aw, ah + 1.5, 1.6);
        out += `<circle cx="${-aw / 2 + 2.4}" cy="${ft - ah / 2}" r="1" fill="${INK}" fill-opacity=".5"/>`;
        out += `<line x1="0" y1="${nb}" x2="0" y2="${-g.baseT - 2}" stroke="${INK}" stroke-width="${sw * 0.6}" stroke-opacity=".28"/>`;
        t = ft - ah - 1; half = fw / 2; break;
      }
      case 'rollon': {
        const w = 2 * n + 3, h = nh + Math.max(16, H * 0.3);
        t = nb - 1 - h; out = rect(-w / 2, t, w, h, w * 0.3);
        half = w / 2; break;
      }
      case 'reed': {
        const w = 2 * n + 1, h = 6; const pt = top - 1;
        out = rect(-w / 2, pt, w, h + 1, 1);
        const L = Math.max(60, H * 1.1);
        const angles = [-14, -6, 3, 11, 18];
        angles.forEach((a, i) => {
          const rad = (a * Math.PI) / 180; const len = L * (0.86 + (i % 2) * 0.14);
          out += `<line x1="${(i - 2) * 1.6}" y1="${pt}" x2="${(i - 2) * 1.6 + Math.sin(rad) * len}" y2="${pt - Math.cos(rad) * len}" stroke="#8a7350" stroke-width="${sw * 1.3}" stroke-linecap="round" ${solid ? '' : 'stroke-opacity=".55"'}/>`;
        });
        t = pt - L; half = Math.max(w / 2, Math.sin((18 * Math.PI) / 180) * L + 4); break;
      }
      default: return { svg: '', top: top, half: n };
    }
    return { svg: out, top: t, half };
  }

  /**
   * render(product, { mode: 'card'|'drawing', color: {hex, opacity}, closure: 'pump'|..|null, w, h, animate })
   */
  function render(p, opts = {}) {
    const id = 'b' + (++uid);
    const mode = opts.mode || 'card';
    const drawing = mode === 'drawing';
    const W = opts.w || (drawing ? 380 : 220);
    const Hpx = opts.h || (drawing ? 440 : 230);
    const g = geometry(p);
    const color = opts.color || { hex: '#d9e6e8', opacity: 0.55 };
    const closureType = opts.closure === undefined ? (p.closures && p.closures[0]) : opts.closure;

    // 1:1로 부자재 범위를 계산한 뒤 화면 크기에 맞춰 축척
    const probe = closure(closureType, p, g, 1, drawing);
    const extTop = Math.min(probe.top, g.top);
    const half = Math.max(g.R, probe.half);
    const pad = drawing ? { l: 70, r: 70, t: 28, b: 64 } : { l: 18, r: 18, t: 16, b: 22 };
    const s = Math.min((W - pad.l - pad.r) / (half * 2), (Hpx - pad.t - pad.b) / -extTop);
    const ox = pad.l + (W - pad.l - pad.r) / 2;
    const oy = Hpx - pad.b;
    const sw = (drawing ? 1.2 : 0.95) / s;
    const cl = closure(closureType, p, g, sw, drawing);
    const body = bodyPath(p, g);
    const { R, n, nh, sb, top, baseT } = g;
    const op = Math.max(0.1, Math.min(1, Number(color.opacity) || 0.6));
    const isDark = op > 0.8 && !/^#f/i.test(color.hex);

    let detail = '';
    // 바닥 유리 두께 (무게/용량 비율로 계산)
    detail += `<rect x="${-R}" y="${-baseT}" width="${R * 2}" height="${baseT}" fill="${color.hex}" fill-opacity="${Math.min(1, op * 0.6)}"/>`;
    detail += `<line x1="${-R + g.rc}" y1="${-baseT}" x2="${R - g.rc}" y2="${-baseT}" stroke="${INK}" stroke-width="${sw * 0.7}" stroke-opacity=".3"/>`;
    // 하이라이트
    const hlTop = (p.shape === 'perfume' ? g.nb : sb) + 2;
    detail += `<rect x="${-R * 0.66}" y="${hlTop}" width="${Math.max(1.2, R * 0.13)}" height="${Math.max(2, -baseT - 2 - hlTop)}" rx="${R * 0.06}" fill="#fff" fill-opacity="${isDark ? 0.28 : 0.6}"/>`;
    detail += `<rect x="${R * 0.52}" y="${hlTop + 2}" width="${Math.max(0.6, R * 0.05)}" height="${Math.max(2, -baseT - 6 - hlTop)}" fill="#fff" fill-opacity="${isDark ? 0.16 : 0.35}"/>`;
    if (p.shape === 'square') {
      [-1, 1].forEach((k) => (detail += `<line x1="${k * R * 0.64}" y1="${sb + 1}" x2="${k * R * 0.64}" y2="-1" stroke="${INK}" stroke-width="${sw * 0.6}" stroke-opacity=".22"/>`));
    }
    if (p.shape === 'perfume') {
      detail += `<rect x="${-R + 4}" y="${g.nb + 4}" width="${R * 2 - 8}" height="${-g.nb - 4 - baseT}" fill="none" stroke="${INK}" stroke-width="${sw * 0.6}" stroke-opacity=".2"/>`;
    }
    // 넥 나사산
    const thread = `<line x1="${-n}" y1="${top + nh * 0.38}" x2="${n}" y2="${top + nh * 0.52}" stroke="${INK}" stroke-width="${sw * 0.7}" stroke-opacity=".45"/>
      <line x1="${-n}" y1="${top + nh * 0.68}" x2="${n}" y2="${top + nh * 0.82}" stroke="${INK}" stroke-width="${sw * 0.7}" stroke-opacity=".45"/>
      <rect x="${-n - 0.7}" y="${top}" width="${2 * n + 1.4}" height="${Math.min(2.2, nh * 0.25)}" rx="0.6" fill="${color.hex}" fill-opacity="${op}" stroke="${INK}" stroke-width="${sw * 0.8}"/>`;

    let svg = `<svg class="bottle-svg ${drawing ? 'is-drawing' : ''} ${opts.animate ? 'is-anim' : ''}" viewBox="0 0 ${W} ${Hpx}" width="100%" height="100%" preserveAspectRatio="xMidYMid meet" role="img" aria-label="${escapeAttr(p.name || '')} 형태 도면">
      <defs>
        <clipPath id="${id}c"><path d="${body}"/></clipPath>
        <linearGradient id="${id}g" x1="0" x2="1" y1="0" y2="0">
          <stop offset="0" stop-color="#0f3b48" stop-opacity=".26"/>
          <stop offset=".07" stop-color="#0f3b48" stop-opacity=".06"/>
          <stop offset=".24" stop-color="#fff" stop-opacity=".55"/>
          <stop offset=".46" stop-color="#fff" stop-opacity="0"/>
          <stop offset=".82" stop-color="#0f3b48" stop-opacity=".04"/>
          <stop offset=".94" stop-color="#0f3b48" stop-opacity=".14"/>
          <stop offset="1" stop-color="#0f3b48" stop-opacity=".28"/>
        </linearGradient>
      </defs>`;
    if (!drawing) {
      // 바닥 그림자 + 유리를 통과한 빛(커스틱)
      svg += `<ellipse cx="${ox}" cy="${oy + 2}" rx="${R * s * 1.2}" ry="${Math.max(2.5, R * s * 0.13)}" fill="#0f3b48" fill-opacity=".1"/>`;
      svg += `<ellipse cx="${ox + R * s * 0.25}" cy="${oy + 3}" rx="${R * s * 0.75}" ry="${Math.max(1.6, R * s * 0.07)}" fill="#5fc3d6" fill-opacity=".22"/>`;
    }
    svg += `<g transform="translate(${ox} ${oy}) scale(${s})">
      <g class="glass" clip-path="url(#${id}c)">
        <path d="${body}" fill="${color.hex}" fill-opacity="${op}"/>
        <rect x="${-R}" y="${top}" width="${R * 2}" height="${-top}" fill="url(#${id}g)"/>
        ${detail}
      </g>
      ${thread}
      <path class="draw" pathLength="1" d="${body}" fill="none" stroke="${INK}" stroke-width="${sw}" stroke-linejoin="round"/>
      <g class="closure">${cl.svg}</g>
    </g>`;

    if (drawing) svg += dims(p, g, s, ox, oy, cl);
    svg += '</svg>';
    return svg;
  }

  function dims(p, g, s, ox, oy, cl) {
    const c = DIM;
    const fmt = (v) => (Math.round(Number(v) * 10) / 10).toFixed(1);
    const R = g.R * s, H = g.H * s, n = g.n * s;
    const xr = ox + Math.max(R, Math.min(cl.half * s, R + 30)) + 26;
    const yb = oy + 30;
    const tick = (x, y) => `<line x1="${x - 4}" y1="${y + 4}" x2="${x + 4}" y2="${y - 4}" stroke="${c}" stroke-width="1.3"/>`;
    let o = `<g class="dims" font-family="'IBM Plex Mono', monospace" font-size="11" fill="${c}">`;
    o += `<line x1="${ox + R + 4}" y1="${oy}" x2="${xr + 6}" y2="${oy}" stroke="${c}" stroke-width=".7" stroke-dasharray="3 3"/>`;
    o += `<line x1="${ox + n + 4}" y1="${oy - H}" x2="${xr + 6}" y2="${oy - H}" stroke="${c}" stroke-width=".7" stroke-dasharray="3 3"/>`;
    o += `<line x1="${xr}" y1="${oy}" x2="${xr}" y2="${oy - H}" stroke="${c}" stroke-width="1"/>` + tick(xr, oy) + tick(xr, oy - H);
    o += `<text x="${xr + 14}" y="${oy - H / 2}" transform="rotate(-90 ${xr + 14} ${oy - H / 2})" text-anchor="middle">H ${fmt(g.H)}</text>`;
    o += `<line x1="${ox - R}" y1="${oy + 4}" x2="${ox - R}" y2="${yb + 6}" stroke="${c}" stroke-width=".7" stroke-dasharray="3 3"/>`;
    o += `<line x1="${ox + R}" y1="${oy + 4}" x2="${ox + R}" y2="${yb + 6}" stroke="${c}" stroke-width=".7" stroke-dasharray="3 3"/>`;
    o += `<line x1="${ox - R}" y1="${yb}" x2="${ox + R}" y2="${yb}" stroke="${c}" stroke-width="1"/>` + tick(ox - R, yb) + tick(ox + R, yb);
    const wl = Number(p.depth) > 0 ? `W ${fmt(p.diameter)} × D ${fmt(p.depth)}` : `Ø ${fmt(g.D)}`;
    o += `<text x="${ox}" y="${yb + 18}" text-anchor="middle">${wl}</text>`;
    const ny = oy - H + g.nh * s * 0.5;
    const lx = Math.max(8, ox - R - 58);
    o += `<line x1="${ox - n}" y1="${ny}" x2="${lx + 46}" y2="${ny}" stroke="${c}" stroke-width=".8"/><circle cx="${ox - n}" cy="${ny}" r="2" fill="${c}"/>`;
    o += `<text x="${lx}" y="${ny - 6}">NECK</text><text x="${lx}" y="${ny + 14}" font-weight="600">${escapeAttr(p.neck || '')}</text>`;
    o += '</g>';
    return o;
  }

  function escapeAttr(s) {
    return String(s).replace(/[&<>"']/g, (ch) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]));
  }

  /* 카테고리 타일용 작은 실루엣 */
  const ICONS = {
    serum: { shape: 'round', height: 96, diameter: 34, neck: '20/410', weight: 60, capacity: 30, closures: ['pump'] },
    toner: { shape: 'round', height: 140, diameter: 50, neck: '24/410', weight: 180, capacity: 120, closures: ['cap'] },
    dropper: { shape: 'boston', height: 86, diameter: 34, neck: '18/410', weight: 58, capacity: 30, closures: ['dropper'] },
    jar: { shape: 'jar', height: 50, diameter: 66, neck: 'G58', weight: 165, capacity: 50, closures: ['lid'] },
    perfume: { shape: 'perfume', height: 96, diameter: 52, neck: 'FEA15', weight: 160, capacity: 50, closures: ['spray'] },
    rollon: { shape: 'vial', height: 84, diameter: 20, neck: 'RO16', weight: 20, capacity: 10, closures: ['rollon'] },
    vial: { shape: 'vial', height: 48, diameter: 18, neck: '13/425', weight: 10, capacity: 5, closures: ['cap'] },
    diffuser: { shape: 'square', height: 92, diameter: 60, neck: '24/410', weight: 260, capacity: 100, closures: ['reed'] },
  };
  function icon(key, sample) {
    const p = sample || ICONS[key] || ICONS.serum;
    return render(p, { mode: 'card', w: 90, h: 110, color: { hex: '#d9e6e8', opacity: 0.5 } });
  }

  return { render, icon, geometry };
})();
