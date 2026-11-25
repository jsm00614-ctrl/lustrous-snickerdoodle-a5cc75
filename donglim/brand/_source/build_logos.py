"""
동림 로고 시안 생성기 (scratchpad 도구)
- 글자는 OFL 폰트(Jost, Cormorant Garamond, Noto Sans/Serif KR)의 윤곽선을 path로 변환해 넣습니다.
- 결과물: <out>/<concept>/*.svg  (폰트 없이 어디서나 동일하게 보이는 순수 벡터)
사용: python build_logos.py <fonts node_modules/@fontsource 경로> <출력 폴더>
"""
import sys, os, math, json
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

FS, OUT = sys.argv[1], sys.argv[2]
INK, AMBER, BLACK, WHITE = '#121619', '#A8571B', '#000000', '#FFFFFF'

F = {
    'jost500': f'{FS}/jost/files/jost-latin-500-normal.woff',
    'jost600': f'{FS}/jost/files/jost-latin-600-normal.woff',
    'jost400': f'{FS}/jost/files/jost-latin-400-normal.woff',
    'corm600': f'{FS}/cormorant-garamond/files/cormorant-garamond-latin-600-normal.woff',
    'sanskr700': [f'{FS}/noto-sans-kr/files/noto-sans-kr-118-700-normal.woff', f'{FS}/noto-sans-kr/files/noto-sans-kr-116-700-normal.woff'],
    'sanskr500': [f'{FS}/noto-sans-kr/files/noto-sans-kr-118-500-normal.woff', f'{FS}/noto-sans-kr/files/noto-sans-kr-116-500-normal.woff'],
    'serifkr700': [f'{FS}/noto-serif-kr/files/noto-serif-kr-118-700-normal.woff', f'{FS}/noto-serif-kr/files/noto-serif-kr-116-700-normal.woff'],
}
_cache = {}
def tt(p):
    if p not in _cache: _cache[p] = TTFont(p)
    return _cache[p]

def fonts_for(key):
    v = F[key]
    return [tt(x) for x in (v if isinstance(v, list) else [v])]

def r(v): return f'{v:.2f}'.rstrip('0').rstrip('.')

def glyph(fonts, ch, size, x, y):
    """한 글자 path + 전진폭 + 경계."""
    for f in fonts:
        cmap = f.getBestCmap()
        if ord(ch) in cmap: break
    else:
        raise KeyError(ch)
    gs = f.getGlyphSet(); s = size / f['head'].unitsPerEm; g = gs[cmap[ord(ch)]]
    t = (s, 0, 0, -s, x, y)
    pen = SVGPathPen(gs, ntos=r); g.draw(TransformPen(pen, t))
    bp = BoundsPen(gs); g.draw(TransformPen(bp, t))
    return pen.getCommands(), g.width * s, bp.bounds

def text(key, s, size, x=0, y=0, track=0.0):
    """문자열 → (path d, (minx,miny,maxx,maxy)). y는 기준선."""
    fonts = fonts_for(key); cx = x; ds = []; bb = [1e9, 1e9, -1e9, -1e9]
    for ch in s:
        if ch == ' ':
            cx += size * 0.28 + track * size; continue
        d, adv, b = glyph(fonts, ch, size, cx, y)
        ds.append(d)
        if b:
            bb = [min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3])]
        cx += adv + track * size
    return ' '.join(ds), tuple(bb)

def text_c(key, s, size, cx, y, track=0.0):
    """가운데 정렬 텍스트."""
    _, b = text(key, s, size, 0, y, track)
    return text(key, s, size, cx - (b[0] + (b[2] - b[0]) / 2), y, track)

def text_r(key, s, size, right, y, track=0.0):
    """오른쪽 정렬 텍스트."""
    _, b = text(key, s, size, 0, y, track)
    return text(key, s, size, right - b[2], y, track)

def cap_h(key, size):
    f = fonts_for(key)[0]
    return f['OS/2'].sCapHeight * size / f['head'].unitsPerEm

class Art:
    """요소를 모아 경계를 계산하고 SVG로 내보내기."""
    def __init__(self): self.items = []; self.bb = [1e9, 1e9, -1e9, -1e9]
    def add(self, svg, bb):
        self.items.append(svg)
        self.bb = [min(self.bb[0], bb[0]), min(self.bb[1], bb[1]), max(self.bb[2], bb[2]), max(self.bb[3], bb[3])]
    def path(self, d, bb, fill, rule=None):
        fr = f' fill-rule="{rule}"' if rule else ''
        self.add(f'<path d="{d}" fill="{fill}"{fr}/>', bb)
    def svg(self, title, pad=0.08):
        x0, y0, x1, y1 = self.bb; w, h = x1 - x0, y1 - y0; p = max(w, h) * pad
        vb = f'{r(x0 - p)} {r(y0 - p)} {r(w + 2 * p)} {r(h + 2 * p)}'
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{r((w + 2 * p) * 4)}" height="{r((h + 2 * p) * 4)}">'
                f'<title>{title}</title>' + ''.join(self.items) + '</svg>\n')

def palette(variant):
    if variant == 'color': return INK, AMBER
    if variant == 'black': return BLACK, BLACK
    return WHITE, WHITE  # white (어두운 바탕용)

def rect(x, y, w, h): return f'M{r(x)},{r(y)} h{r(w)} v{r(h)} h{r(-w)} Z'
def ring(cx, cy, ro, ri):
    d = f'M{r(cx - ro)},{r(cy)} a{r(ro)},{r(ro)} 0 1 0 {r(2 * ro)},0 a{r(ro)},{r(ro)} 0 1 0 {r(-2 * ro)},0 Z'
    if ri > 0.01:
        d += f' M{r(cx - ri)},{r(cy)} a{r(ri)},{r(ri)} 0 1 1 {r(2 * ri)},0 a{r(ri)},{r(ri)} 0 1 1 {r(-2 * ri)},0 Z'
    return d

def bottle_d(cx, top, w, h, neck_w=None, neck_h=None, corner=None):
    """병 실루엣 (닫힌 path). top = 넥 윗면 y."""
    nw = neck_w or w * 0.34; nh = neck_h or h * 0.2; rc = corner or w * 0.14
    L, R = cx - w / 2, cx + w / 2; nl, nr = cx - nw / 2, cx + nw / 2
    sh = h * 0.2; sb = top + nh + sh; bot = top + h
    return (f'M{r(nl)},{r(top)} L{r(nl)},{r(top + nh)} C{r(nl)},{r(top + nh + sh * 0.55)} {r(L)},{r(sb - sh * 0.55)} {r(L)},{r(sb)} '
            f'L{r(L)},{r(bot - rc)} Q{r(L)},{r(bot)} {r(L + rc)},{r(bot)} L{r(R - rc)},{r(bot)} Q{r(R)},{r(bot)} {r(R)},{r(bot - rc)} '
            f'L{r(R)},{r(sb)} C{r(R)},{r(sb - sh * 0.55)} {r(nr)},{r(top + nh + sh * 0.55)} {r(nr)},{r(top + nh)} L{r(nr)},{r(top)} Z')

# ───────────── A. 몰드 ─────────────
def mold_symbol(art, x, y, size, variant):
    """열린 금형 두 쪽. 두 블록 사이의 빈 공간이 유리병이 됩니다. size = 정사각 한 변."""
    ink, acc = palette(variant)
    s = size / 100.0
    def P(px, py): return f'{r(x + px * s)},{r(y + py * s)}'
    gap = 3.4
    nl, L, top_n, sb, bot, rc = 41.0, 24.0, 24.0, 44.0, 84.0, 8.0
    left = (f'M{P(7, 0)} L{P(nl, 0)} L{P(nl, top_n)} C{P(nl, 33)} {P(L, 33)} {P(L, sb)} L{P(L, bot - rc)} Q{P(L, bot)} {P(L + rc, bot)} '
            f'L{P(50 - gap, bot)} L{P(50 - gap, 100)} L{P(7, 100)} Q{P(0, 100)} {P(0, 93)} L{P(0, 7)} Q{P(0, 0)} {P(7, 0)} Z')
    right = (f'M{P(93, 0)} L{P(100 - nl, 0)} L{P(100 - nl, top_n)} C{P(100 - nl, 33)} {P(100 - L, 33)} {P(100 - L, sb)} L{P(100 - L, bot - rc)} Q{P(100 - L, bot)} {P(100 - L - rc, bot)} '
             f'L{P(50 + gap, bot)} L{P(50 + gap, 100)} L{P(93, 100)} Q{P(100, 100)} {P(100, 93)} L{P(100, 7)} Q{P(100, 0)} {P(93, 0)} Z')
    bb = (x, y, x + size, y + size)
    art.path(left, bb, ink); art.path(right, bb, ink)
    if variant == 'color':  # 유리 반사광
        art.path(f'M{P(31, 49)} L{P(35.5, 49)} L{P(35.5, 74)} L{P(31, 74)} Z', bb, acc)

def concept_mold(variant, layout):
    ink, acc = palette(variant); a = Art(); sub = acc if variant == 'color' else ink
    if layout == 'symbol':
        mold_symbol(a, 0, 0, 100, variant); return a
    if layout == 'horizontal':
        mold_symbol(a, 0, 0, 100, variant)
        d, bb = text('jost500', 'DONGLIM', 50, 126, 58, track=0.16); a.path(d, bb, ink)
        d2, b2 = text('sanskr500', '동림', 20, 127, 95, track=0.12); a.path(d2, b2, ink)
        d3, b3 = text_r('jost400', 'GLASS PACKAGING', 12, bb[2], 93, track=0.3); a.path(d3, b3, sub)
        return a
    mold_symbol(a, 70, 0, 100, variant)
    d, bb = text_c('jost500', 'DONGLIM', 44, 120, 162, track=0.16); a.path(d, bb, ink)
    d2, b2 = text_c('sanskr500', '동림', 18, 120, 194, track=0.45); a.path(d2, b2, sub)
    return a

# ───────────── B. D 보틀 ─────────────
def dbottle_symbol(art, x, y, size, variant):
    ink, acc = palette(variant); s = size / 100.0
    def P(px, py): return f'{r(x + px * s)},{r(y + py * s)}'
    D = f'M{P(0, 0)} L{P(42, 0)} A{r(50 * s)},{r(50 * s)} 0 0 1 {P(42, 100)} L{P(0, 100)} Z'
    b = bottle_d(x + 41 * s, y + 17 * s, 36 * s, 66 * s, neck_w=13 * s, neck_h=11 * s, corner=6 * s)
    bb = (x, y, x + 92 * s, y + 100 * s)
    art.path(D + ' ' + b, bb, ink, rule='evenodd')
    if variant == 'color':
        art.path(f'M{P(29, 47)} L{P(33, 47)} L{P(33, 73)} L{P(29, 73)} Z', bb, acc)

def concept_dbottle(variant, layout):
    ink, acc = palette(variant); a = Art(); sub = acc if variant == 'color' else ink
    if layout == 'symbol':
        dbottle_symbol(a, 0, 0, 100, variant); return a
    if layout == 'horizontal':
        dbottle_symbol(a, 0, 0, 100, variant)
        d, bb = text('jost600', 'DONGLIM', 58, 116, 64, track=0.04); a.path(d, bb, ink)
        a.path(rect(118, 79, bb[2] - 118, 1.8), (118, 79, bb[2], 80.8), sub)
        d2, b2 = text('sanskr700', '동림', 15, 118, 100, track=0.1); a.path(d2, b2, ink)
        d3, b3 = text_r('jost500', 'COSMETIC GLASS', 11, bb[2], 99, track=0.24); a.path(d3, b3, ink)
        return a
    dbottle_symbol(a, 74, 0, 100, variant)
    d, bb = text_c('jost600', 'DONGLIM', 46, 120, 162, track=0.04); a.path(d, bb, ink)
    d2, b2 = text_c('sanskr700', '동림', 17, 120, 192, track=0.35); a.path(d2, b2, sub)
    return a

# ───────────── C. 넥 링 (한글 직접 설계) ─────────────
def hangul_donglim(art, x, y, s, variant, only_dong=False):
    """모듈형 '동림'. 획 두께 15, 글자 높이 128. 동의 ㅇ = 위에서 본 병 입구(링 + 점)."""
    ink, acc = palette(variant); t = 15
    def R(px, py, w, h): return rect(x + px * s, y + py * s, w * s, h * s)
    dong = [R(6, 0, 90, t), R(6, 0, t, 40), R(6, 40 - t, 90, t),   # ㄷ
            R(43.5, 47, t, 14), R(0, 61, 102, t)]                  # ㅗ
    art.path(' '.join(dong), (x, y, x + 102 * s, y + 128 * s), ink)
    cx, cy = x + 51 * s, y + 103 * s
    ac = acc if variant == 'color' else ink
    art.path(ring(cx, cy, 25 * s, 11 * s), (cx - 25 * s, cy - 25 * s, cx + 25 * s, cy + 25 * s), ac)
    art.path(ring(cx, cy, 4.5 * s, 0), (cx - 5 * s, cy - 5 * s, cx + 5 * s, cy + 5 * s), ac)
    if only_dong:
        return x + 102 * s
    o = 126
    lieul = [R(o, 0, 62, t), R(o + 62 - t, 0, t, 37), R(o, 22 + 7, 62, t), R(o, 29, t, 37), R(o, 66 - t + 9, 62, t)]
    lieul = [R(o, 0, 62, t), R(o + 62 - t, 0, t, 44), R(o, 30, 62, t), R(o, 30, t, 45), R(o, 75 - t, 62, t)]
    yi = [R(o + 80, 0, t, 78)]
    mieum = [R(o + 4, 87, 91, t), R(o + 4, 87, t, 41), R(o + 95 - t, 87, t, 41), R(o + 4, 128 - t, 91, t)]
    art.path(' '.join(lieul + yi + mieum), (x + o * s, y, x + (o + 95) * s, y + 128 * s), ink)
    return x + (o + 95) * s

def concept_ring(variant, layout):
    ink, acc = palette(variant); a = Art(); sub = acc if variant == 'color' else ink
    if layout == 'symbol':
        # 넥 링이 들어간 '동' 한 글자 (파비콘·도장·자수용)
        hangul_donglim(a, 0, 0, 1.0, variant, only_dong=True)
        return a
    if layout == 'horizontal':
        end = hangul_donglim(a, 0, 0, 0.78, variant)
        a.path(rect(end + 16, 14, 1.6, 72), (end + 16, 14, end + 17.6, 86), ink)
        d, bb = text('jost500', 'DONGLIM', 30, end + 32, 54, track=0.3); a.path(d, bb, ink)
        d2, b2 = text('jost400', 'COSMETIC GLASS PACKAGING', 10, end + 33, 80, track=0.25); a.path(d2, b2, sub)
        return a
    end = hangul_donglim(a, 0, 0, 1.0, variant)
    d, bb = text_c('jost500', 'DONGLIM', 30, end / 2, 182, track=0.42); a.path(d, bb, ink)
    return a

# ───────────── D. 앰버 보틀 (세리프) ─────────────
def concept_amber(variant, layout):
    ink, acc = palette(variant); a = Art(); sub = acc if variant == 'color' else ink
    size = 72; base = 80; capH = cap_h('corm600', size)
    def bottle_o(cx, base, hh):
        w = hh * 0.58
        return bottle_d(cx, base - hh, w, hh, neck_w=w * 0.38, neck_h=hh * 0.16, corner=w * 0.2)
    if layout == 'symbol':
        hh = 100; w = hh * 0.58
        a.path(bottle_o(50, 100, hh), (50 - w / 2, 0, 50 + w / 2, 100), sub)
        hl = WHITE if variant != 'white' else INK
        if variant == 'color': a.path(rect(39, 46, 4.5, 40), (39, 46, 43.5, 86), '#F3E2D2')
        return a
    track = 0.1
    d1, b1 = text('corm600', 'D', size, 0, base, track=track); a.path(d1, b1, ink)
    hh = capH * 1.3; bw = hh * 0.58; ox = b1[2] + size * 0.13
    a.path(bottle_o(ox + bw / 2, base, hh), (ox, base - hh, ox + bw, base), sub)
    d2, b2 = text('corm600', 'NGLIM', size, ox + bw + size * 0.13, base, track=track); a.path(d2, b2, ink)
    if layout == 'horizontal':
        a.path(rect(0, base + 16, b2[2], 1.1), (0, base + 16, b2[2], base + 17.1), ink)
        d3, b3 = text('serifkr700', '동림', 19, 1, base + 44, track=0.55); a.path(d3, b3, ink)
        d4, b4 = text_r('jost400', 'COSMETIC GLASS PACKAGING', 11, b2[2], base + 41, track=0.3); a.path(d4, b4, sub)
        return a
    a2 = Art(); cx = b2[2] / 2; hh = 116; w = hh * 0.58
    a2.path(bottle_o(cx, 116, hh), (cx - w / 2, 0, cx + w / 2, 116), sub)
    if variant == 'color': a2.path(rect(cx - w * 0.3, 52, 4.5, 50), (0, 52, 1, 102), '#F3E2D2')
    d1, b1 = text_c('corm600', 'DONGLIM', 48, cx, 180, track=0.16); a2.path(d1, b1, ink)
    d3, b3 = text_c('serifkr700', '동림', 18, cx, 212, track=0.6); a2.path(d3, b3, ink)
    return a2

# ───────────── E. 엠블럼 ─────────────
def arc_text(art, key, s, size, cx, cy, radius, track, fill, bottom=False):
    fonts = fonts_for(key); items = []
    for ch in s:
        if ch == ' ': items.append((ch, size * 0.3)); continue
        _, adv, _ = glyph(fonts, ch, size, 0, 0); items.append((ch, adv))
    total = sum(w for _, w in items) + track * size * (len(items) - 1)
    span = total / radius; ang = -span / 2
    for ch, w in items:
        mid = ang + (w / 2) / radius
        if ch != ' ':
            d, _, _ = glyph(fonts, ch, size, -w / 2, 0)
            deg = math.degrees(mid if not bottom else -mid)
            if not bottom:
                tf = f'translate({r(cx)} {r(cy)}) rotate({r(deg)}) translate(0 {r(-radius)})'
            else:
                tf = f'translate({r(cx)} {r(cy)}) rotate({r(deg)}) translate(0 {r(radius)})'
            art.items.append(f'<path transform="{tf}" d="{d}" fill="{fill}"/>')
        ang += (w + track * size) / radius

def concept_emblem(variant, layout):
    ink, acc = palette(variant); a = Art(); C = 100; sub = acc if variant == 'color' else ink
    a.path(ring(C, C, 100, 95.5), (0, 0, 200, 200), ink)
    a.path(ring(C, C, 67, 64.5), (33, 33, 167, 167), ink)
    arc_text(a, 'jost600', 'DONGLIM', 24, C, C, 73, 0.5, ink)
    arc_text(a, 'jost500', 'GLASS PACKAGING', 11.5, C, C, 88.5, 0.34, ink, bottom=True)
    for px in (C - 81.5, C + 81.5):
        a.path(ring(px, C, 3.2, 0), (px - 3.2, C - 3.2, px + 3.2, C + 3.2), sub)
    mold_symbol(a, C - 29, C - 36, 58, variant)
    d, b = text_c('sanskr700', '동림', 13, C, C + 45, track=0.55); a.path(d, b, sub)
    a.bb = [0, 0, 200, 200]
    return a

CONCEPTS = {
    'A-mold': ('A. 몰드', concept_mold, ['horizontal', 'stacked', 'symbol']),
    'B-d-bottle': ('B. D 보틀', concept_dbottle, ['horizontal', 'stacked', 'symbol']),
    'C-neck-ring': ('C. 넥 링', concept_ring, ['horizontal', 'stacked', 'symbol']),
    'D-amber': ('D. 앰버 보틀', concept_amber, ['horizontal', 'stacked', 'symbol']),
    'E-emblem': ('E. 엠블럼', concept_emblem, ['badge']),
}

manifest = {}
for cid, (name, fn, layouts) in CONCEPTS.items():
    os.makedirs(f'{OUT}/{cid}', exist_ok=True)
    manifest[cid] = []
    for layout in layouts:
        for variant in ('color', 'black', 'white'):
            art = fn(variant, layout)
            fname = f'{cid.lower()}-{layout}-{variant}.svg'
            open(f'{OUT}/{cid}/{fname}', 'w', encoding='utf-8').write(
                art.svg(f'DONGLIM 동림 로고 {name} {layout} {variant}', pad=0.03 if layout == 'badge' else 0.06))
            manifest[cid].append(fname)
json.dump(manifest, open(f'{OUT}/manifest.json', 'w'), ensure_ascii=False, indent=1)
print('ok', sum(len(v) for v in manifest.values()), 'files')
