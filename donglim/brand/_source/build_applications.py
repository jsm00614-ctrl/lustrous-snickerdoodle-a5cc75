"""
동림 로고 활용안(명함·작업복·유니폼·서식·포장·사인·사용 규칙) 보드 생성.
- 로고는 donglim/brand/logo/svg 의 확정 파일을 그대로 읽어 <symbol>로 넣습니다 (모양 변경 없음, 색만 바꿈).
- 결과: donglim/brand/logo/applications/index.html  (한 장 = 1600×1000px, 8쪽)
- PNG·PDF는 index.html을 브라우저로 열어 쪽마다 캡처한 것입니다.
사용: python build_applications.py <donglim/brand 경로>
"""
import re, sys, os

B = sys.argv[1]
SVG = f'{B}/logo/svg'
OUT = f'{B}/logo/applications/index.html'

INK, STONE, AQUA, PAPER, MUTED, LINE = '#1c1d1f', '#eeeeeb', '#1d7a8c', '#f8f8f5', '#8b8c87', '#d4d4cf'
REP = {'name': '이상만', 'title': '대표', 'title_en': 'CEO', 'tel': '010-5033-9999', 'mail': 'smlee5033@daum.net'}


# ───────── 로고 심볼 (확정 SVG에서 path만 꺼내 색을 지움) ─────────
def symbol(fname, sid):
    s = open(f'{SVG}/{fname}', encoding='utf-8').read()
    vb = re.search(r'viewBox="([^"]+)"', s).group(1)
    body = re.search(r'<svg[^>]*>(.*)</svg>', s, re.S).group(1)
    body = re.sub(r'<title>.*?</title>', '', body, flags=re.S)
    body = re.sub(r'\sfill="#[0-9a-fA-F]{3,6}"', '', body)
    w, h = [float(x) for x in vb.split()[2:]]
    return f'<symbol id="{sid}" viewBox="{vb}">{body.strip()}</symbol>', w / h

SYMS, RATIO = [], {}
for f, sid in [('donglim-horizontal.svg', 'lh'), ('donglim-stacked.svg', 'ls'), ('donglim-en.svg', 'le')]:
    sym, ratio = symbol(f, sid); SYMS.append(sym); RATIO[sid] = ratio
# 파비콘 D 타일: 바탕(currentColor)과 D(--knock)를 따로 칠할 수 있게 다시 묶음
fav = open(f'{SVG}/donglim-favicon.svg', encoding='utf-8').read()
dpath = re.search(r'<path[^>]*d="([^"]+)"', fav).group(1)
SYMS.append(f'<symbol id="ld" viewBox="0 0 24 24"><rect width="24" height="24" rx="5.5"/><path fill="var(--knock,#eeeeeb)" fill-rule="evenodd" d="{dpath}"/></symbol>')
RATIO['ld'] = 1.0


def logo(sid, w=None, h=None, color=INK, extra='', style=''):
    r = RATIO[sid]
    if w is None: w = h * r
    if h is None: h = w / r
    return (f'<svg class="lg" viewBox="0 0 {w:.2f} {h:.2f}" width="{w:.2f}" height="{h:.2f}" style="color:{color};{style}" '
            f'fill="currentColor" {extra}><use href="#{sid}" width="{w:.2f}" height="{h:.2f}"/></svg>')


def g_logo(sid, x, y, w=None, h=None, fill=INK, extra=''):
    """SVG 안에서 쓰는 로고 (좌상단 x,y)."""
    r = RATIO[sid]
    if w is None: w = h * r
    if h is None: h = w / r
    return f'<use href="#{sid}" x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{fill}" {extra}/>'


# ───────── 공통 틀 ─────────
TOTAL = 8
def frame(no, ko, en, body, notes=(), dark=False):
    n = f'{no:02d}'
    note = ''.join(f'<li>{x}</li>' for x in notes)
    return f'''
<section class="pg{' pg--dark' if dark else ''}" id="p{n}">
  <i class="crop tl"></i><i class="crop tr"></i><i class="crop bl"></i><i class="crop br"></i>
  <header class="pg__hd"><span>DONGLIM — LOGO APPLICATIONS</span><span>{n} / {TOTAL:02d}</span></header>
  <div class="pg__body">{body}</div>
  <footer class="pg__ft">
    <div class="pg__title"><b class="pg__no">{n}</b><div><h2>{ko}</h2><p>{en}</p></div></div>
    <ul class="pg__notes">{note}</ul>
  </footer>
</section>'''


def dim_h(x1, x2, y, label):
    """가로 치수선."""
    return (f'<g class="dim"><line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}"/>'
            f'<line x1="{x1}" y1="{y-5}" x2="{x1}" y2="{y+5}"/><line x1="{x2}" y1="{y-5}" x2="{x2}" y2="{y+5}"/>'
            f'<rect x="{(x1+x2)/2-34}" y="{y-8}" width="68" height="16" class="dim__bg"/>'
            f'<text x="{(x1+x2)/2}" y="{y+4}" text-anchor="middle">{label}</text></g>')


def dim_v(x, y1, y2, label):
    """세로 치수선."""
    cy = (y1 + y2) / 2
    return (f'<g class="dim"><line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}"/>'
            f'<line x1="{x-5}" y1="{y1}" x2="{x+5}" y2="{y1}"/><line x1="{x-5}" y1="{y2}" x2="{x+5}" y2="{y2}"/>'
            f'<rect x="{x-34}" y="{cy-8}" width="68" height="16" class="dim__bg"/>'
            f'<text x="{x}" y="{cy+4}" text-anchor="middle">{label}</text></g>')


# ───────── 01 표지 ─────────
def p_cover():
    rings = ''.join(f'<circle cx="1380" cy="1060" r="{r}" fill="none" stroke="{AQUA if r == 122 else LINE}" stroke-width="{0.9 if r == 122 else 0.7}"/>'
                    for r in (44, 64, 90, 122, 160, 206, 262))
    items = [('02', '명함', 'Business card'), ('03', '작업복', 'Workwear'), ('04', '유니폼 · 모자 · 사원증', 'Uniform · Cap · ID'),
             ('05', '서식류', 'Stationery'), ('06', '포장', 'Packaging'), ('07', '사인', 'Signage'), ('08', '사용 규칙', 'Usage guide')]
    idx = ''.join(f'<li><span>{a}</span><b>{b}</b><em>{c}</em></li>' for a, b, c in items)
    body = f'''
    <svg class="cover__rings" viewBox="0 0 1600 1000" aria-hidden="true">{rings}</svg>
    <div class="cover">
      <div class="cover__mark">{logo('lh', w=720)}</div>
      <p class="cover__sub">로고 활용안 <span>Logo applications</span></p>
      <ol class="cover__idx">{idx}</ol>
    </div>'''
    return frame(1, '로고 활용안', 'Annealed Quiet — 명함부터 간판까지, 같은 표식을 공정마다 다른 재료로', body,
                 [])


# ───────── 02 명함 ─────────
def p_card():
    s = 6.2  # px/mm
    W, H = 90 * s, 50 * s
    fx, fy, bx, by = 150, 300, 860, 300
    m = 7 * s
    front = f'''
    <div class="card card--front" style="left:{fx}px;top:{fy}px;width:{W}px;height:{H}px">
      <div style="position:absolute;left:{m}px;top:{m}px">{logo('lh', h=4.6 * s)}</div>
      <div class="card__who" style="left:{m}px;bottom:{m}px">
        <b>{REP['name']}</b><span>{REP['title']} <i>{REP['title_en']}</i></span>
      </div>
      <dl class="card__info" style="right:{m}px;bottom:{m}px">
        <div><dt>M</dt><dd>{REP['tel']}</dd></div>
        <div><dt>E</dt><dd>{REP['mail']}</dd></div>
      </dl>
    </div>'''
    back = f'''
    <div class="card card--back" style="left:{bx}px;top:{by}px;width:{W}px;height:{H}px">
      <div class="card__emboss">{logo('ls', h=19 * s, color='#f4f4f1')}</div>
    </div>'''
    dims = (f'<svg class="dims" viewBox="0 0 1600 1000">{dim_h(fx, fx + W, fy + H + 46, "90 mm")}{dim_v(fx - 44, fy, fy + H, "50 mm")}'
            f'{dim_h(bx, bx + W, by + H + 46, "90 mm")}</svg>')
    labels = (f'<p class="cap" style="left:{fx}px;top:{fy - 40}px">앞면 · 먹 1도 + 청록 엣지 컬러</p>'
              f'<p class="cap" style="left:{bx}px;top:{by - 40}px">뒷면 · 블랙 용지 + 백색 박</p>')
    body = front + back + dims + labels
    return frame(2, '명함', 'Business card — 90 × 50 mm', body,
                 ['앞: 랑데뷰 울트라화이트 240g, 먹 1도', '뒤: 블랙 매직 300g, 백색 박(로고)', '옆면: 청록 엣지 컬러 #1D7A8C', '로고 높이 4.6 mm · 여백 7 mm'])


# ───────── 옷 그리기 ─────────
DEFS = f'''
<pattern id="twill" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(-38)">
  <rect width="6" height="6" fill="transparent"/><line x1="0" y1="0" x2="0" y2="6" stroke="#ffffff" stroke-opacity=".045" stroke-width="2"/>
</pattern>
<pattern id="pique" width="4" height="4" patternUnits="userSpaceOnUse">
  <circle cx="2" cy="2" r=".7" fill="#000" fill-opacity=".05"/>
</pattern>
<pattern id="stitchW" width="3" height="3" patternUnits="userSpaceOnUse" patternTransform="rotate(52)">
  <rect width="3" height="3" fill="#f4f4f0"/><line x1="0" y1="0" x2="0" y2="3" stroke="#c9cac4" stroke-width=".9"/>
</pattern>
<linearGradient id="shadeBody" x1="0" x2="1"><stop offset="0" stop-color="#000" stop-opacity=".22"/><stop offset=".18" stop-color="#000" stop-opacity="0"/>
  <stop offset=".82" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".22"/></linearGradient>
<linearGradient id="shadeLight" x1="0" x2="1"><stop offset="0" stop-color="#000" stop-opacity=".07"/><stop offset=".2" stop-color="#000" stop-opacity="0"/>
  <stop offset=".8" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".07"/></linearGradient>
<linearGradient id="glass" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#d9ecef"/><stop offset=".5" stop-color="#bfdde2"/><stop offset="1" stop-color="#a9cfd6"/></linearGradient>
<linearGradient id="kraft" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#cdb08a"/><stop offset="1" stop-color="#c2a37b"/></linearGradient>
<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="7"/>
  <feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 .07 0"/><feComposite in2="SourceGraphic" operator="in"/></filter>
<filter id="concrete" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".035 .09" numOctaves="3" seed="3"/>
  <feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 .045 0"/><feComposite in2="SourceGraphic" operator="in"/></filter>
<filter id="emb" x="-5%" y="-5%" width="110%" height="110%"><feDropShadow dx="0" dy=".6" stdDeviation=".35" flood-color="#000" flood-opacity=".55"/></filter>
<filter id="standoff" x="-10%" y="-20%" width="130%" height="160%"><feDropShadow dx="7" dy="9" stdDeviation="5" flood-color="#000" flood-opacity=".26"/></filter>
<filter id="lift" x="-10%" y="-10%" width="120%" height="130%"><feDropShadow dx="0" dy="14" stdDeviation="14" flood-color="#2b2c28" flood-opacity=".20"/></filter>
'''

# 작업 점퍼 (앞) — 좌표 0..500 × 0..560
JK_BODY = 'M150 48 L110 70 L124 200 L128 500 L372 500 L376 200 L390 70 L350 48 Q250 74 150 48 Z'
JK_SL_L = 'M110 70 L62 250 L46 474 L98 480 L112 296 L124 200 Z'
JK_SL_R = 'M390 70 L438 250 L454 474 L402 480 L388 296 L376 200 Z'
JK_COLLAR = 'M150 48 L156 26 Q250 40 344 26 L350 48 Q250 74 150 48 Z'
JK_BACK_COLLAR = 'M150 48 L156 28 Q250 38 344 28 L350 48 Q250 74 150 48 Z'


def jacket(front=True, color='#262b30', chest=None, back_logo=None):
    seams = 'stroke="#000" stroke-opacity=".28" stroke-width="1.2" fill="none"'
    stitch = 'stroke="#fff" stroke-opacity=".12" stroke-width=".9" stroke-dasharray="3 3" fill="none"'
    parts = [JK_SL_L, JK_SL_R, JK_BODY]
    g = ''.join(f'<path d="{d}" fill="{color}"/><path d="{d}" fill="url(#twill)"/>' for d in parts)
    g += f'<path d="{JK_BODY}" fill="url(#shadeBody)"/>'
    g += f'<path d="{JK_COLLAR if front else JK_BACK_COLLAR}" fill="{color}"/><path d="{JK_COLLAR if front else JK_BACK_COLLAR}" fill="#000" fill-opacity=".18"/>'
    # 소매 끝·밑단 고무단
    g += f'<path d="M48 446 L100 452" {seams}/><path d="M452 446 L400 452" {seams}/><path d="M128 470 L372 470" {seams}/>' + ''.join(f'<path d="M{x} 472 L{x} 499" stroke="#000" stroke-opacity=".16" stroke-width="1"/>' for x in range(133, 370, 6)) + f'<path d="M128 470 L372 470" {seams}/>'
    g += f'<path d="M48 450 L99 456" {stitch}/><path d="M452 450 L401 456" {stitch}/><path d="M128 466 L372 466" {stitch}/>'
    # 진동·어깨 솔기
    g += f'<path d="M110 70 L124 200" {seams}/><path d="M390 70 L376 200" {seams}/>'
    if front:
        g += f'<path d="M250 62 L250 500" stroke="#000" stroke-opacity=".45" stroke-width="2.2"/>'
        g += f'<path d="M250 62 L250 500" stroke="#9aa0a4" stroke-opacity=".55" stroke-width=".8" stroke-dasharray="1.4 1.4"/>'
        g += f'<rect x="246" y="66" width="8" height="15" rx="2" fill="#8d9396"/>'
        g += f'<path d="M150 410 L190 350" {seams}/><path d="M350 410 L310 350" {seams}/>'
        g += f'<path d="M154 410 L194 350" {stitch}/><path d="M346 410 L306 350" {stitch}/>'
        g += f'<path d="M156 126 Q250 140 344 126" {stitch}/>'
    else:
        g += f'<path d="M126 128 Q250 146 374 128" {seams}/><path d="M126 132 Q250 150 374 132" {stitch}/>'
        g += f'<path d="M250 58 L250 128" {seams}/>'
    if chest: g += chest
    if back_logo: g += back_logo
    return g


def p_workwear():
    # 앞: 왼쪽 가슴(입은 사람 기준) = 화면 오른쪽. 로고 폭 100mm ≈ 46 단위
    chest = g_logo('lh', 288, 168, w=58, fill='url(#stitchW)', extra='filter="url(#emb)"')
    back = g_logo('ls', 190, 190, w=120, fill='url(#stitchW)', extra='filter="url(#emb)"')
    front = f'<svg class="obj" style="left:96px;top:190px" width="520" height="560" viewBox="-10 -10 520 560" filter="url(#lift)">{jacket(True, chest=chest)}</svg>'
    backv = f'<svg class="obj" style="left:640px;top:190px" width="520" height="560" viewBox="-10 -10 520 560" filter="url(#lift)">{jacket(False, back_logo=back)}</svg>'
    # 자수 확대
    zoom = f'''
    <div class="zoom" style="left:1218px;top:262px">
      <svg width="290" height="290" viewBox="0 0 290 290">
        <defs><clipPath id="zc"><circle cx="145" cy="145" r="144"/></clipPath></defs>
        <g clip-path="url(#zc)"><rect width="290" height="290" fill="#262b30"/><rect width="290" height="290" fill="url(#twill)"/>
        <rect width="290" height="290" fill="url(#twill)" transform="translate(3 0)"/>
        {g_logo('lh', 30, 124, w=230, fill='url(#stitchW)', extra='filter="url(#emb)"')}</g>
        <circle cx="145" cy="145" r="144" fill="none" stroke="{AQUA}" stroke-width="1"/>
      </svg>
    </div>
    <p class="cap" style="left:1218px;top:576px;width:290px;text-align:center">자수 확대 · 백색 실, 새틴 스티치</p>'''
    labels = ('<p class="cap" style="left:106px;top:150px">앞 · 왼쪽 가슴 자수 (폭 100 mm)</p>'
              '<p class="cap" style="left:650px;top:150px">뒤 · 등판 중앙 자수 (폭 260 mm)</p>')
    return frame(3, '작업복', 'Workwear — 생산·출고 현장용 점퍼', front + backv + zoom + labels,
                 ['원단: 차콜 네이비 #262B30, 트윌', '자수: 백색 실, 가로형(가슴) · 세로형(등)', '가슴 로고 아래 이름 자수 추가 가능', '어두운 원단에는 흰색 파일만 사용'])


# ───────── 04 유니폼 · 모자 · 사원증 ─────────
PO_BODY = 'M155 46 L104 66 L120 170 L124 470 L376 470 L380 170 L396 66 L345 46 Q250 70 155 46 Z'
PO_SL_L = 'M104 66 L58 184 L108 204 L120 170 Z'
PO_SL_R = 'M396 66 L442 184 L392 204 L380 170 Z'
PO_COLLAR_L = 'M155 46 L172 22 L250 64 L232 98 Z'
PO_COLLAR_R = 'M345 46 L328 22 L250 64 L268 98 Z'


def polo():
    c = '#f6f6f3'
    seams = 'stroke="#000" stroke-opacity=".12" stroke-width="1" fill="none"'
    g = ''.join(f'<path d="{d}" fill="{c}"/><path d="{d}" fill="url(#pique)"/>' for d in (PO_SL_L, PO_SL_R, PO_BODY))
    g += f'<path d="{PO_BODY}" fill="url(#shadeLight)"/>'
    g += f'<path d="M232 66 L232 176 L268 176 L268 66" fill="#eeeeea" stroke="#000" stroke-opacity=".1"/>'
    for y in (96, 132):
        g += f'<circle cx="250" cy="{y}" r="3.2" fill="#e3e3de" stroke="#000" stroke-opacity=".18"/>'
    g += f'<path d="{PO_COLLAR_L}" fill="#f0f0ec" stroke="#000" stroke-opacity=".14"/><path d="{PO_COLLAR_R}" fill="#f0f0ec" stroke="#000" stroke-opacity=".14"/>'
    g += f'<path d="M62 176 L110 196" {seams}/><path d="M438 176 L390 196" {seams}/><path d="M104 66 L120 170" {seams}/><path d="M396 66 L380 170" {seams}/>'
    g += f'<path d="M124 456 L376 456" {seams}/>'
    g += f'<path d="M154 470 L154 444" {seams}/><path d="M346 470 L346 444" {seams}/>'
    g += g_logo('lh', 290, 140, w=58, fill=INK)
    return g


def cap():
    c = INK
    g = f'<path d="M40 200 Q40 40 200 34 Q360 40 360 200 Z" fill="{c}"/>'
    g += f'<path d="M40 200 Q40 40 200 34 Q360 40 360 200 Z" fill="url(#twill)"/>'
    g += f'<path d="M200 34 L200 200" stroke="#000" stroke-opacity=".35" stroke-width="1.2"/>'
    g += f'<path d="M122 48 Q104 120 108 200 M278 48 Q296 120 292 200" stroke="#000" stroke-opacity=".3" stroke-width="1" fill="none"/>'
    g += f'<path d="M122 52 Q106 120 110 198 M278 52 Q294 120 290 198" stroke="#fff" stroke-opacity=".1" stroke-dasharray="3 3" fill="none"/>'
    g += f'<circle cx="200" cy="38" r="6" fill="#2a2b2e"/>'
    g += f'<path d="M30 200 Q200 182 370 200 Q372 236 330 250 Q200 270 70 250 Q28 236 30 200 Z" fill="#141516"/>'
    g += f'<path d="M44 206 Q200 190 356 206" stroke="#fff" stroke-opacity=".1" stroke-dasharray="3 3" fill="none"/>'
    g += g_logo('ls', 150, 92, w=100, fill='url(#stitchW)', extra='filter="url(#emb)"')
    return g


def p_uniform():
    s = 3.4  # px/mm (사원증 54×86)
    W, H = 54 * s, 86 * s
    x0, y0 = 1250, 300
    strap = ''.join(f'<span>DONGLIM</span>' for _ in range(5))
    badge = f'''
    <div class="lanyard" style="left:{x0 + W / 2 - 13}px;top:0;height:{y0 + 18}px"><div>{strap}</div></div>
    <div class="clip" style="left:{x0 + W / 2 - 15}px;top:{y0 - 16}px"></div>
    <div class="badge" style="left:{x0}px;top:{y0}px;width:{W}px;height:{H}px">
      <div class="badge__top">{logo('lh', w=W - 44)}</div>
      <div class="badge__photo"><svg viewBox="0 0 60 70" width="78" height="91"><circle cx="30" cy="24" r="12" fill="#c9c9c3"/><path d="M6 70 Q8 42 30 42 Q52 42 54 70 Z" fill="#c9c9c3"/></svg></div>
      <b class="badge__name">{REP['name']}</b>
      <span class="badge__role">{REP['title']} · {REP['title_en']}</span>
      <i class="badge__edge"></i>
    </div>'''
    po = f'<svg class="obj" style="left:96px;top:186px" width="520" height="500" viewBox="-10 -10 520 500" filter="url(#lift)">{polo()}</svg>'
    cp = f'<svg class="obj" style="left:690px;top:300px" width="400" height="290" viewBox="0 0 400 290" filter="url(#lift)">{cap()}</svg>'
    labels = ('<p class="cap" style="left:106px;top:146px">사무·영업 폴로 · 먹색 자수</p>'
              '<p class="cap" style="left:700px;top:260px">모자 · 세로형 백색 자수</p>'
              f'<p class="cap" style="left:{x0}px;top:{y0 + H + 24}px">사원증 · 54 × 86 mm</p>')
    return frame(4, '유니폼 · 모자 · 사원증', 'Uniform · Cap · ID card', po + cp + badge + labels,
                 ['폴로: 화이트 피케, 가슴 가로형 먹색 자수 폭 90 mm', '모자: 블랙 6패널, 정면 세로형 백색 자수', '사원증 줄: 먹색 바탕 + DONGLIM 백색 반복 인쇄'])


# ───────── 05 서식류 ─────────
def p_stationery():
    s = 2.0
    LW, LH = 210 * s, 297 * s
    lx, ly = 150, 160
    bars = ''.join(f'<i style="width:{w}%"></i>' for w in (92, 96, 88, 94, 60, 0, 95, 90, 97, 72, 0, 84, 93, 40))
    letter = f'''
    <div class="sheet" style="left:{lx}px;top:{ly}px;width:{LW}px;height:{LH}px">
      <div style="position:absolute;left:{20 * s}px;top:{18 * s}px">{logo('lh', h=6 * s)}</div>
      <p class="sheet__date" style="right:{20 * s}px;top:{20 * s}px">2026. 11. 26.</p>
      <div class="sheet__to" style="left:{20 * s}px;top:{52 * s}px"><b>수신</b> 귀사 담당자님<br><b>제목</b> 유리용기 견적의 건</div>
      <div class="sheet__bars" style="left:{20 * s}px;right:{20 * s}px;top:{82 * s}px">{bars}</div>
      <div class="sheet__ft" style="left:{20 * s}px;right:{20 * s}px;bottom:{14 * s}px">
        <span>동림 DONGLIM · 화장품 유리용기</span><span>{REP['tel']} · {REP['mail']}</span>
      </div>
    </div>'''
    EW, EH = 220 * s, 105 * s
    ex, ey = 720, 250
    env = f'''
    <div class="env" style="left:{ex}px;top:{ey}px;width:{EW}px;height:{EH}px">
      <div style="position:absolute;left:{12 * s}px;top:{11 * s}px">{logo('lh', h=4.6 * s)}</div>
      <p class="env__from" style="left:{12 * s}px;bottom:{10 * s}px">{REP['tel']}<br>{REP['mail']}</p>
      <div class="env__to" style="left:{104 * s}px;top:{52 * s}px"><i></i><i></i><i style="width:60%"></i></div>
      <i class="env__edge"></i>
    </div>'''
    sx, sy = 720, 560
    seal = f'''
    <div class="seal" style="left:{sx}px;top:{sy}px">{logo('ld', w=118, style='--knock:#eeeeeb')}</div>
    <div class="seal seal--round" style="left:{sx + 170}px;top:{sy}px"><svg width="118" height="118" viewBox="0 0 118 118">
      <circle cx="59" cy="59" r="58" fill="{PAPER}"/><circle cx="59" cy="59" r="50" fill="none" stroke="{AQUA}" stroke-width=".9"/>
      {g_logo('ls', 32, 37, w=54, fill=INK)}</svg></div>
    <div class="folder" style="left:{sx + 340}px;top:{sy - 16}px"><div>{logo('le', w=110, color='#f4f4f1')}</div><span>QUOTATION</span></div>'''
    dims = f'<svg class="dims" viewBox="0 0 1600 1000">{dim_h(lx, lx + LW, ly + LH + 34, "210 mm")}{dim_h(ex, ex + EW, ey + EH + 34, "220 mm")}</svg>'
    labels = (f'<p class="cap" style="left:{ex}px;top:{ey - 40}px">규격 봉투 · 220 × 105 mm</p>'
              f'<p class="cap" style="left:{sx}px;top:{sy + 140}px">봉인 스티커 · 원형 라벨 · 견적서 폴더</p>')
    return frame(5, '서식류', 'Stationery — 레터헤드 · 봉투 · 스티커 · 폴더', letter + env + seal + dims + labels,
                 ['레터헤드 A4: 로고 높이 6 mm, 여백 20 mm', '봉투: 먹 1도, 가로형 로고 높이 4.6 mm', '스티커: D 타일 30 mm / 원형 30 mm', '견적서 폴더: 먹색 바탕, 영문 단독 백색 박'])


# ───────── 06 포장 ─────────
def handling():
    glass = '<path d="M6 2 h12 l-1.5 9 a4.5 4.5 0 0 1 -9 0 Z M12 16 v6 M8 22 h8" fill="none" stroke="currentColor" stroke-width="1.6"/>'
    up = '<path d="M7 22 V6 M3 10 L7 4 L11 10 M17 22 V6 M13 10 L17 4 L21 10 M2 23 h20" fill="none" stroke="currentColor" stroke-width="1.6"/>'
    rain = '<path d="M2 12 a10 10 0 0 1 20 0 Z M12 12 v8 a2 2 0 0 1 -4 0 M5 2 l-1 3 M12 0 l-1 3 M19 2 l-1 3" fill="none" stroke="currentColor" stroke-width="1.6"/>'
    return ''.join(f'<svg viewBox="0 0 24 24" width="38" height="38">{x}</svg>' for x in (glass, up, rain))


def p_packaging():
    bx, by, BW, BH = 150, 230, 620, 420
    box = f'''
    <div class="box" style="left:{bx}px;top:{by}px;width:{BW}px;height:{BH}px">
      <i class="box__flap"></i><i class="box__tape"></i>
      <div class="box__logo">{logo('lh', w=300)}</div>
      <p class="box__fragile">FRAGILE · GLASS<br><span>유리 제품 · 취급 주의</span></p>
      <div class="box__icons">{handling()}</div>
      <div class="box__spec"><span>품번</span><b>DL-SR030</b><span>수량</span><b>120 EA</b><span>LOT</span><b>26-1126</b></div>
    </div>'''
    tape_units = ''.join(f'<span class="tape__u">{logo("lh", h=15, color=INK)}</span>' for _ in range(7))
    tape = f'<div class="tape" style="left:150px;top:{by + BH + 70}px;width:1300px"><div>{tape_units}</div></div>'
    s = 4.0
    LW, LH = 100 * s, 70 * s
    lx, ly = 900, 230
    label = f'''
    <div class="lbl" style="left:{lx}px;top:{ly}px;width:{LW}px;height:{LH}px">
      <div class="lbl__hd">{logo('lh', h=22)}<span>SHIPPING LABEL</span></div>
      <dl class="lbl__tb">
        <div><dt>품번</dt><dd>DL-SR030 · 세럼 라운드 30 ml</dd></div>
        <div><dt>색상</dt><dd>투명 (Flint) · 펌프 넥 20/410</dd></div>
        <div><dt>수량</dt><dd>120 EA / 1 CTN</dd></div>
        <div><dt>LOT</dt><dd>26-1126 · 검사 완료</dd></div>
      </dl>
      <svg class="lbl__bar" viewBox="0 0 180 34" width="180" height="34">{''.join(f'<rect x="{i * 3}" y="0" width="{(1, 2, 1, 1, 2, 1, 2, 2, 1)[i % 9] * .9}" height="34" fill="{INK}"/>' for i in range(60))}</svg>
      <i class="lbl__edge"></i>
    </div>'''
    labels = (f'<p class="cap" style="left:{bx}px;top:{by - 40}px">출고 박스 · 먹 1도 인쇄</p>'
              f'<p class="cap" style="left:{lx}px;top:{ly - 40}px">박스 라벨 · 100 × 70 mm</p>'
              f'<p class="cap" style="left:150px;top:{by + BH + 34}px">포장 테이프 · 투명 바탕 먹 1도 반복 (폭 48 mm)</p>')
    return frame(6, '포장', 'Packaging — 출고 박스 · 라벨 · 테이프', box + label + tape + labels,
                 ['박스: 크라프트 골판지, 먹 1도 플렉소 인쇄', '라벨: 감열지, 로고 높이 5.5 mm', '테이프: OPP 투명, 로고 간격 = 로고 폭 1/2'])


# ───────── 07 사인 ─────────
def p_signage():
    wall = f'''
    <div class="wall" style="left:96px;top:170px;width:860px;height:520px">
      <svg class="wall__tex" width="860" height="520"><rect width="860" height="520" fill="#dcdcd6"/><rect width="860" height="520" fill="#dcdcd6" filter="url(#concrete)"/>
        {''.join(f'<line x1="0" y1="{y}" x2="860" y2="{y}" stroke="#000" stroke-opacity=".06"/>' for y in (130, 260, 390))}
        {''.join(f'<line x1="{x}" y1="0" x2="{x}" y2="520" stroke="#000" stroke-opacity=".05"/>' for x in (215, 430, 645))}
      </svg>
      <div class="wall__sign">{logo('lh', w=560, extra='filter="url(#standoff)"')}</div>
      <i class="wall__light"></i>
    </div>'''
    door = f'''
    <div class="door" style="left:1040px;top:170px;width:400px;height:620px">
      <svg width="400" height="620" viewBox="0 0 400 620">
        <rect x="0" y="0" width="400" height="620" fill="#2a2b2d"/>
        <rect x="14" y="14" width="372" height="592" fill="url(#glass)"/>
        <path d="M14 14 L160 14 L14 300 Z" fill="#fff" fill-opacity=".22"/>
        <path d="M200 14 L240 14 L14 470 L14 390 Z" fill="#fff" fill-opacity=".14"/>
        <rect x="14" y="14" width="372" height="592" fill="none" stroke="{AQUA}" stroke-width="1"/>
        <rect x="336" y="250" width="10" height="160" rx="5" fill="#b7bcbe"/>
        {g_logo('ls', 140, 214, w=120, fill='#ffffff')}
        <line x1="120" y1="400" x2="280" y2="400" stroke="#fff" stroke-opacity=".7"/>
        <text x="200" y="430" text-anchor="middle" class="door__t">평일 09:00 – 18:00</text>
        <text x="200" y="452" text-anchor="middle" class="door__t">{REP['tel']}</text>
      </svg>
    </div>'''
    labels = ('<p class="cap" style="left:106px;top:130px">외벽 간판 · 먹색 스탠드오프 채널 문자</p>'
              '<p class="cap" style="left:1040px;top:130px">출입문 유리 · 백색 시트 커팅</p>')
    dims = f'<svg class="dims" viewBox="0 0 1600 1000">{dim_h(246, 806, 730, "2,400 mm")}</svg>'
    return frame(7, '사인', 'Signage — 외벽 간판 · 출입문', wall + door + labels + dims,
                 ['간판: 무광 먹색 알루미늄, 벽면에서 30 mm 띄움', '야간: 뒤쪽 간접 조명(백색)', '유리문: 백색 컷팅 시트, 세로형 폭 300 mm'])


# ───────── 08 사용 규칙 ─────────
def p_guide():
    # 여백: '동' 높이 x 만큼
    W = 520; H = W / RATIO['lh']; x = H * 0.86  # '동' 높이 ≈ 로고 높이의 86%
    cs = f'''
    <div class="g-clear" style="left:120px;top:190px;width:{W + 2 * x}px;height:{H + 2 * x}px">
      <i class="g-clear__box" style="inset:{x}px"></i>
      <div style="position:absolute;left:{x}px;top:{x}px">{logo('lh', w=W)}</div>
      <span class="g-x" style="left:0;top:{x + H / 2 - 9}px;width:{x}px">x</span>
      <span class="g-x" style="right:0;top:{x + H / 2 - 9}px;width:{x}px">x</span>
      <span class="g-x" style="left:{x + W / 2 - 9}px;top:{x / 2 - 9}px">x</span>
      <span class="g-x" style="left:{x + W / 2 - 9}px;bottom:{x / 2 - 9}px">x</span>
    </div>
    <p class="cap" style="left:120px;top:150px">여백 · 로고 둘레에 ‘동’ 한 글자 높이(x)만큼</p>'''
    mins = f'''
    <div class="g-min" style="left:120px;top:{190 + H + 2 * x + 70}px">
      <div>{logo('lh', h=17)}<span>가로형 · 인쇄 25 mm / 화면 100 px</span></div>
      <div>{logo('ls', h=40)}<span>세로형 · 인쇄 15 mm / 화면 60 px</span></div>
      <div>{logo('ld', h=24)}<span>D 타일 · 인쇄 5 mm / 화면 16 px</span></div>
    </div>
    <p class="cap" style="left:120px;top:{190 + H + 2 * x + 30}px">최소 크기</p>'''
    sw = [('#1C1D1F', 'INK', '로고 기본색'), ('#EEEEEB', 'STONE', '바탕 · 종이'), ('#1D7A8C', 'AQUA', '엣지 · 선 강조'), ('#FFFFFF', 'WHITE', '어두운 바탕 위 로고')]
    sws = ''.join(f'<div><i style="background:{c}"></i><b>{n}</b><span>{c}</span><em>{d}</em></div>' for c, n, d in sw)
    colors = f'<div class="g-sw" style="left:1000px;top:190px">{sws}</div><p class="cap" style="left:1000px;top:150px">색</p>'
    def dont(inner, txt):
        return f'<div class="g-dont"><div class="g-dont__box">{inner}</div><span>{txt}</span></div>'
    donts = ''.join([
        dont(logo('lh', w=112, style='transform:scaleX(1.6)'), '늘이거나 줄이지 않기'),
        dont(f'<svg width="150" height="{150 / RATIO["lh"]:.1f}" viewBox="0 0 150 {150 / RATIO["lh"]:.1f}"><defs><clipPath id="half"><rect width="56" height="40"/></clipPath></defs>'
             f'{g_logo("lh", 0, 0, w=150, fill=INK)}<g clip-path="url(#half)">{g_logo("lh", 0, 0, w=150, fill="#c2501b")}</g></svg>', '한글·영문 색 나누지 않기'),
        dont(f'<div style="background:#c9c9c3;padding:12px 10px">{logo("lh", w=130, color="#a9a9a3")}</div>', '대비 낮은 바탕 피하기'),
        dont(logo('lh', w=150, style='filter:drop-shadow(3px 4px 2px rgba(0,0,0,.45))'), '그림자·효과 넣지 않기'),
    ])
    dz = f'<div class="g-donts" style="left:1000px;top:520px">{donts}</div><p class="cap" style="left:1000px;top:480px">하지 말 것</p>'
    return frame(8, '사용 규칙', 'Usage guide — 여백 · 최소 크기 · 색 · 하지 말 것', cs + mins + colors + dz,
                 ['파일: donglim/brand/logo/svg', '인쇄소·자수 업체에는 SVG(또는 PDF) 전달', '별색은 실물 교정 후 확정'])


PAGES = [p_cover(), p_card(), p_workwear(), p_uniform(), p_stationery(), p_packaging(), p_signage(), p_guide()]

CSS = f'''
:root {{ --ink:{INK}; --stone:{STONE}; --aqua:{AQUA}; --paper:{PAPER}; --muted:{MUTED}; --line:{LINE}; }}
* {{ box-sizing:border-box; margin:0; padding:0; }}
html {{ background:#d9d9d4; }}
body {{ font-family:'Gothic A1','Pretendard',sans-serif; color:var(--ink); word-break:keep-all; -webkit-font-smoothing:antialiased; }}
.pg {{ position:relative; width:1600px; height:1000px; margin:0 auto 40px; background:var(--stone); overflow:hidden; page-break-after:always; break-after:page; }}
.pg:last-child {{ margin-bottom:0; }}
.crop {{ position:absolute; width:18px; height:18px; border-color:#b9b9b3; border-style:solid; border-width:0; }}
.crop.tl {{ left:34px; top:34px; border-left-width:1px; border-top-width:1px; }}
.crop.tr {{ right:34px; top:34px; border-right-width:1px; border-top-width:1px; }}
.crop.bl {{ left:34px; bottom:34px; border-left-width:1px; border-bottom-width:1px; }}
.crop.br {{ right:34px; bottom:34px; border-right-width:1px; border-bottom-width:1px; }}
.pg__hd {{ position:absolute; left:64px; right:64px; top:56px; display:flex; justify-content:space-between; font:400 11px/1 'DM Mono','Gothic A1',monospace; letter-spacing:.16em; color:var(--muted); }}
.pg__ft {{ position:absolute; left:64px; right:64px; bottom:56px; display:flex; justify-content:space-between; align-items:flex-end; gap:40px; }}
.pg__title {{ display:flex; align-items:flex-end; gap:22px; }}
.pg__no {{ font:400 64px/0.8 'Bricolage Grotesque',sans-serif; letter-spacing:-.04em; position:relative; padding-bottom:2px; }}
.pg__no::after {{ content:''; position:absolute; left:2px; bottom:-14px; width:36px; height:1px; background:var(--aqua); }}
.pg__title h2 {{ font:600 21px/1.2 'Gothic A1',sans-serif; letter-spacing:-.03em; }}
.pg__title p {{ font:400 11.5px/1.5 'DM Mono','Gothic A1',monospace; color:var(--muted); margin-top:6px; letter-spacing:.02em; }}
.pg__notes {{ list-style:none; text-align:right; font:400 11px/1.75 'DM Mono','Gothic A1',monospace; color:#6c6d68; }}
.pg__body {{ position:absolute; inset:0; }}
.cap {{ position:absolute; font:400 11.5px/1 'DM Mono','Gothic A1',monospace; letter-spacing:.04em; color:#6c6d68; white-space:nowrap; }}
.dims {{ position:absolute; inset:0; width:1600px; height:1000px; pointer-events:none; overflow:visible; }}
.dim line {{ stroke:#9d9e98; stroke-width:.8; }}
.dim__bg {{ fill:var(--stone); }}
.dim text {{ font:400 10.5px 'DM Mono','Gothic A1',monospace; fill:#7d7e79; letter-spacing:.06em; }}
.obj {{ position:absolute; overflow:visible; }}
.lg {{ display:block; overflow:visible; }}

/* 표지 */
.cover__rings {{ position:absolute; inset:0; width:1600px; height:1000px; }}
.cover {{ position:absolute; left:140px; top:300px; right:140px; }}
.cover__sub {{ margin-top:46px; font:600 17px 'Gothic A1',sans-serif; letter-spacing:-.02em; }}
.cover__sub span {{ font:400 12px 'DM Mono','Gothic A1',monospace; color:var(--muted); margin-left:12px; letter-spacing:.08em; }}
.cover__idx {{ list-style:none; position:absolute; left:930px; top:-74px; width:420px; border-top:1px solid var(--line); }}
.cover__idx li {{ display:grid; grid-template-columns:44px 1fr auto; align-items:baseline; padding:11px 0; border-bottom:1px solid var(--line); }}
.cover__idx span {{ font:400 11px 'DM Mono','Gothic A1',monospace; color:var(--aqua); }}
.cover__idx b {{ font:500 14px 'Gothic A1',sans-serif; letter-spacing:-.02em; }}
.cover__idx em {{ font:400 10.5px 'DM Mono','Gothic A1',monospace; color:var(--muted); font-style:normal; letter-spacing:.04em; }}

/* 명함 */
.card {{ position:absolute; border-radius:2px; }}
.card--front {{ background:#fbfbf8; box-shadow:0 0 0 1.4px var(--aqua), 0 1px 1px rgba(0,0,0,.05), 0 22px 36px -16px rgba(43,44,40,.30); }}
.card--front::before {{ content:''; position:absolute; inset:0; background:linear-gradient(160deg,rgba(255,255,255,.8),rgba(255,255,255,0) 40%); pointer-events:none; }}
.card--back {{ background:#18191b; box-shadow:0 0 0 1.4px var(--aqua), 0 22px 36px -16px rgba(20,20,18,.42); display:grid; place-items:center; }}
.card__emboss {{ filter:drop-shadow(0 .6px 0 rgba(255,255,255,.35)) drop-shadow(0 -.5px 0 rgba(0,0,0,.6)); }}
.card__who {{ position:absolute; display:grid; gap:6px; }}
.card__who b {{ font:600 21px/1 'Gothic A1',sans-serif; letter-spacing:.02em; }}
.card__who span {{ font:500 11.5px/1 'Gothic A1',sans-serif; color:#55564f; }}
.card__who i {{ font:400 10px 'DM Mono','Gothic A1',monospace; font-style:normal; letter-spacing:.12em; margin-left:4px; color:var(--muted); }}
.card__info {{ position:absolute; display:grid; gap:7px; text-align:right; }}
.card__info div {{ display:flex; justify-content:flex-end; gap:10px; font:400 11.5px/1 'DM Mono','Gothic A1',monospace; letter-spacing:.02em; }}
.card__info dt {{ color:var(--aqua); }}

/* 작업복 */
.zoom {{ position:absolute; filter:drop-shadow(0 16px 22px rgba(43,44,40,.22)); }}

/* 사원증 */
.lanyard {{ position:absolute; width:26px; background:#1a1b1d; overflow:hidden; }}
.lanyard div {{ display:flex; flex-direction:column; align-items:center; gap:22px; padding-top:14px; }}
.lanyard span {{ writing-mode:vertical-rl; font:500 9px 'Bricolage Grotesque',sans-serif; letter-spacing:.32em; color:#e9e9e5; }}
.clip {{ position:absolute; width:30px; height:30px; border-radius:6px; background:linear-gradient(#c4c8ca,#9aa0a3); box-shadow:0 2px 3px rgba(0,0,0,.2); }}
.badge {{ position:absolute; background:#fbfbf8; border-radius:9px; padding:26px 22px; display:flex; flex-direction:column; align-items:center;
  box-shadow:0 1px 1px rgba(0,0,0,.05), 0 22px 36px -16px rgba(43,44,40,.30); overflow:hidden; }}
.badge::before {{ content:''; position:absolute; top:10px; left:50%; width:34px; height:6px; margin-left:-17px; border-radius:3px; background:var(--stone); box-shadow:inset 0 1px 2px rgba(0,0,0,.18); }}
.badge__top {{ margin-top:10px; }}
.badge__photo {{ margin-top:22px; width:96px; height:112px; display:grid; place-items:end center; background:#e6e6e1; overflow:hidden; border-radius:3px; }}
.badge__name {{ margin-top:18px; font:600 19px 'Gothic A1',sans-serif; letter-spacing:.04em; }}
.badge__role {{ margin-top:6px; font:400 10.5px 'DM Mono','Gothic A1',monospace; color:var(--muted); letter-spacing:.06em; }}
.badge__edge {{ position:absolute; left:0; right:0; bottom:0; height:7px; background:var(--ink); border-top:1.2px solid var(--aqua); }}

/* 서식류 */
.sheet {{ position:absolute; background:#fbfbf8; box-shadow:0 1px 1px rgba(0,0,0,.05), 0 26px 40px -18px rgba(43,44,40,.30); }}
.sheet__date {{ position:absolute; font:400 9.5px 'DM Mono','Gothic A1',monospace; color:var(--muted); letter-spacing:.06em; }}
.sheet__to {{ position:absolute; font:400 10px/1.9 'Gothic A1',sans-serif; color:#3e3f3a; }}
.sheet__to b {{ font-weight:600; margin-right:8px; }}
.sheet__bars {{ position:absolute; display:grid; gap:9px; }}
.sheet__bars i {{ display:block; height:3px; background:#dcdcd6; }}
.sheet__ft {{ position:absolute; display:flex; justify-content:space-between; padding-top:9px; border-top:1px solid var(--aqua); font:400 8.5px 'DM Mono','Gothic A1',monospace; color:#6c6d68; letter-spacing:.03em; }}
.env {{ position:absolute; background:#fbfbf8; box-shadow:0 1px 1px rgba(0,0,0,.05), 0 22px 34px -16px rgba(43,44,40,.28); }}
.env__from {{ position:absolute; font:400 9px/1.6 'DM Mono','Gothic A1',monospace; color:#6c6d68; }}
.env__to {{ position:absolute; display:grid; gap:12px; width:180px; }}
.env__to i {{ display:block; height:3px; background:#dcdcd6; width:100%; }}
.env__edge {{ position:absolute; left:0; right:0; bottom:0; height:1.2px; background:var(--aqua); }}
.seal {{ position:absolute; filter:drop-shadow(0 10px 14px rgba(43,44,40,.22)); }}
.folder {{ position:absolute; width:240px; height:150px; background:#18191b; border-radius:2px; padding:20px; box-shadow:0 0 0 1.2px var(--aqua), 0 20px 30px -14px rgba(20,20,18,.4); }}
.folder span {{ position:absolute; left:20px; bottom:18px; font:400 9.5px 'DM Mono','Gothic A1',monospace; letter-spacing:.3em; color:#8f908b; }}

/* 포장 */
.box {{ position:absolute; background:linear-gradient(#cdb08a,#c1a27a); box-shadow:inset 0 0 0 1px rgba(0,0,0,.08), 0 26px 40px -18px rgba(43,44,40,.34); }}
.box::before {{ content:''; position:absolute; inset:0; background:repeating-linear-gradient(90deg,rgba(0,0,0,.025) 0 2px,transparent 2px 7px); }}
.box__flap {{ position:absolute; left:0; right:0; top:0; height:92px; border-bottom:1.4px solid rgba(60,40,20,.25); }}
.box__tape {{ position:absolute; left:50%; top:0; width:72px; height:118px; margin-left:-36px; background:rgba(235,232,222,.55); border-left:1px solid rgba(255,255,255,.4); border-right:1px solid rgba(0,0,0,.06); }}
.box__logo {{ position:absolute; left:54px; top:168px; mix-blend-mode:multiply; opacity:.92; }}
.box__fragile {{ position:absolute; left:54px; bottom:54px; font:500 14px/1.5 'Bricolage Grotesque',sans-serif; letter-spacing:.26em; mix-blend-mode:multiply; }}
.box__fragile span {{ font:500 11px 'Gothic A1',sans-serif; letter-spacing:.08em; }}
.box__icons {{ position:absolute; right:54px; bottom:54px; display:flex; gap:14px; color:var(--ink); mix-blend-mode:multiply; }}
.box__spec {{ position:absolute; right:54px; top:168px; display:grid; grid-template-columns:auto auto; gap:8px 18px; font:400 11px 'DM Mono','Gothic A1',monospace; mix-blend-mode:multiply; }}
.box__spec span {{ color:rgba(28,29,31,.62); }}
.lbl {{ position:absolute; background:#fbfbf8; padding:20px 22px; box-shadow:0 1px 1px rgba(0,0,0,.05), 0 22px 34px -16px rgba(43,44,40,.28); }}
.lbl__hd {{ display:flex; justify-content:space-between; align-items:center; padding-bottom:12px; border-bottom:1px solid var(--ink); }}
.lbl__hd span {{ font:400 9.5px 'DM Mono','Gothic A1',monospace; letter-spacing:.24em; color:var(--muted); }}
.lbl__tb {{ margin-top:10px; display:grid; gap:7px; }}
.lbl__tb div {{ display:grid; grid-template-columns:48px 1fr; font:400 11px 'Gothic A1',sans-serif; }}
.lbl__tb dt {{ font:400 10px 'DM Mono','Gothic A1',monospace; color:var(--muted); }}
.lbl__bar {{ position:absolute; right:22px; bottom:20px; }}
.lbl__edge {{ position:absolute; left:0; top:0; bottom:0; width:5px; background:var(--aqua); }}
.tape {{ position:absolute; height:64px; background:rgba(242,240,232,.82); box-shadow:0 1px 0 rgba(0,0,0,.06), 0 10px 18px -10px rgba(43,44,40,.25); overflow:hidden; }}
.tape::before {{ content:''; position:absolute; inset:0; background:linear-gradient(180deg,rgba(255,255,255,.6),rgba(255,255,255,0) 45%,rgba(0,0,0,.03)); }}
.tape div {{ display:flex; align-items:center; height:100%; gap:78px; padding-left:40px; }}
.tape__u {{ flex:none; }}

/* 사인 */
.wall {{ position:absolute; overflow:hidden; box-shadow:0 26px 40px -22px rgba(43,44,40,.35); }}
.wall__tex {{ position:absolute; inset:0; }}
.wall__sign {{ position:absolute; left:150px; top:210px; }}
.wall__light {{ position:absolute; inset:0; background:radial-gradient(70% 60% at 50% 0%,rgba(255,255,255,.35),transparent 70%); pointer-events:none; }}
.door {{ position:absolute; box-shadow:0 26px 40px -22px rgba(43,44,40,.4); }}
.door__t {{ font:400 11px 'DM Mono','Gothic A1',monospace; fill:#fff; letter-spacing:.08em; }}

/* 사용 규칙 */
.g-clear {{ position:absolute; background:#fbfbf8; outline:1px dashed #b9b9b3; }}
.g-clear__box {{ position:absolute; border:1px solid var(--aqua); }}
.g-x {{ position:absolute; display:grid; place-items:center; height:18px; min-width:18px; font:400 11px 'DM Mono','Gothic A1',monospace; color:var(--aqua); }}
.g-min {{ position:absolute; display:flex; gap:56px; align-items:flex-end; }}
.g-min div {{ display:grid; gap:14px; justify-items:start; }}
.g-min span {{ font:400 10.5px 'DM Mono','Gothic A1',monospace; color:#6c6d68; }}
.g-sw {{ position:absolute; display:grid; grid-template-columns:repeat(4,110px); gap:16px; }}
.g-sw div {{ display:grid; gap:5px; align-content:start; }}
.g-sw i {{ display:block; height:110px; box-shadow:inset 0 0 0 1px rgba(0,0,0,.08); }}
.g-sw b {{ margin-top:6px; font:500 11px 'DM Mono','Gothic A1',monospace; letter-spacing:.14em; }}
.g-sw span {{ font:400 10.5px 'DM Mono','Gothic A1',monospace; color:#6c6d68; }}
.g-sw em {{ font:400 10.5px/1.5 'Gothic A1',sans-serif; color:#6c6d68; font-style:normal; }}
.g-donts {{ position:absolute; display:grid; grid-template-columns:repeat(2,230px); gap:20px 22px; }}
.g-dont {{ display:grid; gap:8px; }}
.g-dont__box {{ height:84px; display:grid; place-items:center; background:#fbfbf8; position:relative; overflow:hidden; }}
.g-dont__box::after {{ content:''; position:absolute; inset:0; background:linear-gradient(to top right,transparent calc(50% - .6px),#c2501b calc(50% - .6px),#c2501b calc(50% + .6px),transparent calc(50% + .6px)); opacity:.55; }}
.g-dont span {{ font:400 11px 'Gothic A1',sans-serif; color:#55564f; }}

@media print {{ html {{ background:none; }} .pg {{ margin:0; }} @page {{ size:1600px 1000px; margin:0; }} }}
'''

HTML = f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=1600">
<title>동림 로고 활용안</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,500&family=DM+Mono&family=Gothic+A1:wght@400;500;600&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>{''.join(SYMS)}{DEFS}</defs></svg>
{''.join(PAGES)}
</body>
</html>
'''
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, 'w', encoding='utf-8').write(HTML)
print('ok', OUT, len(PAGES), 'pages')
