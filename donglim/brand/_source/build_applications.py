"""
동림 로고 활용안 보드 생성 — nby-awesome-design-md 방식.
- 디자인 기준: donglim/brand/logo/applications/DESIGN.md
  (VoltAgent/awesome-design-md 의 Nike-inspired 디자인 언어, MIT)
  · 색: ink #111111 / canvas #ffffff / soft-cloud #f5f5f5 / hairline #cacacb, 강조는 accent-teal #0a7281 한 곳
  · 글꼴: 대형 대문자 디스플레이(Anton, 줄간격 0.9) + Inter/Pretendard UI(12–32px), 중간 크기 없음
  · 모양: 카드·이미지 모서리 0, 그림자 0, 버튼·칩·배지는 알약형(30px)
  · 구성: 캠페인 타일(풀블리드) / 상품 목록(PLP) / 상품 상세(PDP: 썸네일 열 + 큰 이미지 + 사양 줄)
- 로고는 donglim/brand/logo/svg 의 확정 파일을 그대로 읽어 <symbol>로 넣습니다 (모양 변경 없음, 색만 바꿈).
- 결과: donglim/brand/logo/applications/index.html  (한 장 = 1600×1000px)
사용: python build_applications.py <donglim/brand 경로>
"""
import re, sys, os

B = sys.argv[1]
SVG = f'{B}/logo/svg'
OUT = f'{B}/logo/applications/index.html'

INK, CANVAS, CLOUD, HAIR, MUTE, TEAL = '#111111', '#ffffff', '#f5f5f5', '#cacacb', '#707072', '#0a7281'
REP = {'name': '이상만', 'title': '대표', 'title_en': 'CEO', 'tel': '010-5033-9999', 'mail': 'smlee5033@daum.net'}


# ───────── 로고 심볼 ─────────
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
fav = open(f'{SVG}/donglim-favicon.svg', encoding='utf-8').read()
dpath = re.search(r'<path[^>]*d="([^"]+)"', fav).group(1)
SYMS.append(f'<symbol id="ld" viewBox="0 0 24 24"><rect width="24" height="24" rx="5.5"/><path fill="var(--knock,#ffffff)" fill-rule="evenodd" d="{dpath}"/></symbol>')
RATIO['ld'] = 1.0


def logo(sid, w=None, h=None, color=INK, style='', cls=''):
    r = RATIO[sid]
    if w is None: w = h * r
    if h is None: h = w / r
    return (f'<svg class="lg {cls}" viewBox="0 0 {w:.2f} {h:.2f}" width="{w:.2f}" height="{h:.2f}" style="color:{color};{style}" '
            f'fill="currentColor"><use href="#{sid}" width="{w:.2f}" height="{h:.2f}"/></svg>')


def g_logo(sid, x, y, w=None, h=None, fill=INK, extra=''):
    r = RATIO[sid]
    if w is None: w = h * r
    if h is None: h = w / r
    return f'<use href="#{sid}" x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{fill}" {extra}/>'


# ───────── SVG 공통 재료 ─────────
DEFS = '''
<pattern id="twill" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(-40)">
  <line x1="0" y1="0" x2="0" y2="5" stroke="#fff" stroke-opacity=".05" stroke-width="1.6"/></pattern>
<pattern id="pique" width="3.2" height="3.2" patternUnits="userSpaceOnUse"><circle cx="1.6" cy="1.6" r=".5" fill="#000" fill-opacity=".028"/></pattern>
<pattern id="ribV" width="4" height="10" patternUnits="userSpaceOnUse"><line x1="1" y1="0" x2="1" y2="10" stroke="#000" stroke-opacity=".22" stroke-width="1"/></pattern>
<pattern id="ribL" width="4" height="10" patternUnits="userSpaceOnUse"><line x1="1" y1="0" x2="1" y2="10" stroke="#000" stroke-opacity=".08" stroke-width="1"/></pattern>
<pattern id="stitchW" width="2.6" height="2.6" patternUnits="userSpaceOnUse" patternTransform="rotate(55)">
  <rect width="2.6" height="2.6" fill="#f7f7f5"/><line x1="0" y1="0" x2="0" y2="2.6" stroke="#cfd0cb" stroke-width=".8"/></pattern>
<pattern id="stitchK" width="2.6" height="2.6" patternUnits="userSpaceOnUse" patternTransform="rotate(55)">
  <rect width="2.6" height="2.6" fill="#141414"/><line x1="0" y1="0" x2="0" y2="2.6" stroke="#3a3a3a" stroke-width=".8"/></pattern>
<linearGradient id="sideShade" x1="0" x2="1"><stop offset="0" stop-color="#000" stop-opacity=".30"/><stop offset=".22" stop-color="#000" stop-opacity="0"/>
  <stop offset=".78" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".30"/></linearGradient>
<linearGradient id="sideShadeL" x1="0" x2="1"><stop offset="0" stop-color="#000" stop-opacity=".10"/><stop offset=".25" stop-color="#000" stop-opacity="0"/>
  <stop offset=".75" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".10"/></linearGradient>
<linearGradient id="topLight" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".08"/><stop offset=".45" stop-color="#fff" stop-opacity="0"/>
  <stop offset="1" stop-color="#000" stop-opacity=".18"/></linearGradient>
<radialGradient id="crownLight" cx=".38" cy=".28" r=".75"><stop offset="0" stop-color="#fff" stop-opacity=".14"/><stop offset=".6" stop-color="#fff" stop-opacity="0"/>
  <stop offset="1" stop-color="#000" stop-opacity=".25"/></radialGradient>
<radialGradient id="helmetLight" cx=".36" cy=".26" r=".8"><stop offset="0" stop-color="#fff" stop-opacity=".9"/><stop offset=".55" stop-color="#fff" stop-opacity="0"/>
  <stop offset="1" stop-color="#000" stop-opacity=".16"/></radialGradient>
<radialGradient id="ground" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#000" stop-opacity=".22"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>
<linearGradient id="metal" x1="0" x2="1"><stop offset="0" stop-color="#8f969b"/><stop offset=".5" stop-color="#d7dbde"/><stop offset="1" stop-color="#868d92"/></linearGradient>
<linearGradient id="glassDoor" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#d8eaed"/><stop offset=".55" stop-color="#b8d6dc"/><stop offset="1" stop-color="#9cc5cd"/></linearGradient>
<linearGradient id="bottleBody" x1="0" x2="1"><stop offset="0" stop-color="#9fd3dc" stop-opacity=".55"/><stop offset=".08" stop-color="#0d2a30" stop-opacity=".2"/>
  <stop offset=".3" stop-color="#0b1c20" stop-opacity=".05"/><stop offset=".7" stop-color="#0b1c20" stop-opacity=".05"/><stop offset=".9" stop-color="#0d2a30" stop-opacity=".25"/>
  <stop offset="1" stop-color="#b9e4ea" stop-opacity=".7"/></linearGradient>
<linearGradient id="bottleSpec" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".85"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<linearGradient id="pumpMetal" x1="0" x2="1"><stop offset="0" stop-color="#3b4044"/><stop offset=".35" stop-color="#c9ced1"/><stop offset=".55" stop-color="#eef1f2"/><stop offset="1" stop-color="#2f3336"/></linearGradient>
<filter id="soft6" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="6"/></filter>
<filter id="soft3" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="3"/></filter>
<filter id="emb" x="-5%" y="-5%" width="110%" height="110%"><feDropShadow dx="0" dy=".7" stdDeviation=".4" flood-color="#000" flood-opacity=".55"/></filter>
<filter id="halo" x="-20%" y="-60%" width="140%" height="220%"><feMorphology in="SourceAlpha" operator="dilate" radius="3" result="d"/>
  <feGaussianBlur in="d" stdDeviation="14" result="b"/><feFlood flood-color="#fff6e8" flood-opacity=".95"/><feComposite in2="b" operator="in" result="g"/>
  <feMerge><feMergeNode in="g"/><feMergeNode in="g"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="noise" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".8" numOctaves="2" seed="4"/>
  <feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 .05 0"/><feComposite in2="SourceGraphic" operator="in"/></filter>
'''


# ───────── 물건 그리기 (벡터) ─────────
def ground(cx, cy, rx, ry, op=1):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#ground)" opacity="{op}"/>'


J_BODY = ('M150 96 C158 150 162 200 164 244 L168 600 L432 600 L436 244 C438 200 442 150 450 96 '
          'L364 70 Q300 100 236 70 Z')
J_SL_L = 'M150 96 C116 106 98 150 92 214 L70 532 L130 540 L146 330 C150 296 156 268 164 244 C162 200 158 150 150 96 Z'
J_SL_R = 'M450 96 C484 106 502 150 508 214 L530 532 L470 540 L454 330 C450 296 444 268 436 244 C438 200 442 150 450 96 Z'
J_YOKE = 'M150 96 L236 70 Q300 100 364 70 L450 96 C452 120 450 140 448 156 Q300 172 152 156 C150 140 148 120 150 96 Z'
J_COLLAR = 'M228 74 L234 30 Q300 18 366 30 L372 74 Q300 104 228 74 Z'
J_COLLAR_IN = 'M244 38 Q300 50 356 38 L358 62 Q300 84 242 62 Z'
J_BCOLLAR = 'M228 74 L234 30 Q300 22 366 30 L372 74 Q300 104 228 74 Z'


def jacket(front=True, color='#25292e', yoke='#16191c', logo_svg=''):
    seam = 'stroke="#000" stroke-opacity=".35" stroke-width="1.3" fill="none"'
    st = 'stroke="#fff" stroke-opacity=".16" stroke-width=".9" stroke-dasharray="3 2.4" fill="none"'
    g = ground(300, 612, 210, 18)
    for d in (J_SL_L, J_SL_R):
        g += f'<path d="{d}" fill="{color}"/><path d="{d}" fill="url(#twill)"/><path d="{d}" fill="url(#topLight)"/>'
    g += f'<path d="{J_BODY}" fill="{color}"/><path d="{J_BODY}" fill="url(#twill)"/><path d="{J_BODY}" fill="url(#sideShade)"/>'
    # 요크 (어깨 배색)
    yk = J_YOKE if front else J_YOKE
    g += f'<path d="{yk}" fill="{yoke}"/><path d="{yk}" fill="url(#twill)"/>'
    g += f'<path d="M152 156 Q300 172 448 156" {seam}/><path d="M152 161 Q300 177 448 161" {st}/>'
    # 진동 솔기
    g += f'<path d="M150 96 C158 150 162 200 164 244" {seam}/><path d="M450 96 C442 150 438 200 436 244" {seam}/>'
    # 소매·밑단 립
    g += '<path d="M72 504 L132 512 L130 540 L70 532 Z" fill="url(#ribV)"/><path d="M528 504 L468 512 L470 540 L530 532 Z" fill="url(#ribV)"/>'
    g += f'<path d="M72 504 L132 512" {seam}/><path d="M528 504 L468 512" {seam}/>'
    g += '<rect x="168" y="568" width="264" height="32" fill="url(#ribV)"/>'
    g += f'<path d="M168 568 L432 568" {seam}/>'
    if front:
        g += f'<path d="{J_COLLAR}" fill="{yoke}"/><path d="{J_COLLAR_IN}" fill="#0b0c0e"/>'
        g += f'<path d="M234 30 Q300 18 366 30" {st}/>'
        # 지퍼
        g += '<path d="M300 34 L300 600" stroke="#0c0d0f" stroke-width="6"/>'
        g += '<path d="M300 34 L300 600" stroke="#6b7075" stroke-width="3.2" stroke-dasharray="1.2 1.3"/>'
        g += '<rect x="294" y="40" width="12" height="20" rx="2" fill="url(#metal)"/><rect x="297" y="58" width="6" height="22" rx="3" fill="url(#metal)"/>'
        # 가슴 지퍼 주머니 (보는 쪽 왼쪽)
        g += '<path d="M206 192 L206 286" stroke="#0c0d0f" stroke-width="4"/><path d="M206 192 L206 286" stroke="#5f656a" stroke-width="2" stroke-dasharray="1 1.2"/>'
        g += '<rect x="202" y="194" width="8" height="12" rx="1.5" fill="url(#metal)"/>'
        # 옆 주머니
        for sx in (1, -1):
            x1, x2 = 300 - sx * 112, 300 - sx * 84
            g += f'<path d="M{x1} 470 L{x2} 388" stroke="#000" stroke-opacity=".55" stroke-width="3"/>'
            g += f'<path d="M{x1 + 5 * sx} 470 L{x2 + 5 * sx} 388" {st}/>'
        # 몸판 앞 반사광
        g += '<ellipse cx="236" cy="300" rx="40" ry="120" fill="#fff" fill-opacity=".035" filter="url(#soft6)"/>'
    else:
        g += f'<path d="{J_BCOLLAR}" fill="{yoke}"/><path d="M234 30 Q300 22 366 30" {st}/>'
        g += '<path d="M300 172 L300 566" stroke="#000" stroke-opacity=".18" stroke-width="2"/>'
    g += logo_svg
    return g


P_BODY = 'M160 96 C168 140 172 180 174 214 L178 560 L422 560 L426 214 C428 180 432 140 440 96 L364 70 Q300 96 236 70 Z'
P_SL_L = 'M160 96 C124 106 106 150 92 236 L146 262 C156 244 166 228 174 214 C172 180 168 140 160 96 Z'
P_SL_R = 'M440 96 C476 106 494 150 508 236 L454 262 C444 244 434 228 426 214 C428 180 432 140 440 96 Z'


def polo(color='#fbfbf9', logo_svg=''):
    seam = 'stroke="#000" stroke-opacity=".13" stroke-width="1.1" fill="none"'
    g = ground(300, 570, 190, 14, .7)
    for d in (P_SL_L, P_SL_R):
        g += f'<path d="{d}" fill="{color}"/><path d="{d}" fill="url(#pique)"/><path d="{d}" fill="url(#topLight)" opacity=".35"/>'
    g += f'<path d="{P_BODY}" fill="{color}"/><path d="{P_BODY}" fill="url(#pique)"/><path d="{P_BODY}" fill="url(#sideShadeL)"/>'
    g += '<path d="M94 226 L148 252 L146 262 L92 236 Z" fill="url(#ribL)"/><path d="M506 226 L452 252 L454 262 L508 236 Z" fill="url(#ribL)"/>'
    g += f'<path d="M95 226 L149 251" {seam}/><path d="M505 226 L451 251" {seam}/>'
    g += f'<path d="M160 96 C168 140 172 180 174 214" {seam}/><path d="M440 96 C432 140 428 180 426 214" {seam}/>'
    g += f'<path d="M178 540 L422 540" {seam}/><path d="M180 560 L180 528" {seam}/><path d="M420 560 L420 528" {seam}/>'
    # 플래킷
    g += '<path d="M286 92 L286 214 L314 214 L314 92" fill="#f4f4f1" stroke="#000" stroke-opacity=".1"/>'
    for y in (122, 160, 196):
        g += f'<circle cx="300" cy="{y}" r="3.6" fill="#ecebe6" stroke="#000" stroke-opacity=".2"/><circle cx="299" cy="{y - 1}" r="1" fill="#fff"/>'
    # 칼라
    g += '<path d="M236 70 Q300 54 364 70 L356 78 Q300 64 244 78 Z" fill="#efefeb"/>'
    g += '<path d="M236 70 Q262 70 300 120 L268 158 Q238 118 214 84 Z" fill="#f7f7f4" stroke="#000" stroke-opacity=".12"/>'
    g += '<path d="M364 70 Q338 70 300 120 L332 158 Q362 118 386 84 Z" fill="#f7f7f4" stroke="#000" stroke-opacity=".12"/>'
    g += '<path d="M268 158 Q300 150 332 158" stroke="#000" stroke-opacity=".08" fill="none"/>'
    g += '<path d="M214 84 Q240 120 268 158" stroke="#000" stroke-opacity=".06" stroke-width="5" fill="none" filter="url(#soft3)"/>'
    g += logo_svg
    return g


def cap(color='#151515', logo_svg=''):
    g = ground(300, 400, 220, 18)
    crown = 'M118 318 C118 168 200 86 300 86 C400 86 482 168 482 318 Z'
    g += f'<path d="{crown}" fill="{color}"/><path d="{crown}" fill="url(#twill)"/><path d="{crown}" fill="url(#crownLight)"/>'
    for d in ('M300 88 C268 140 254 230 252 318', 'M300 88 C332 140 346 230 348 318', 'M300 88 C220 110 168 200 160 318', 'M300 88 C380 110 432 200 440 318'):
        g += f'<path d="{d}" stroke="#000" stroke-opacity=".5" stroke-width="1.4" fill="none"/>'
        g += f'<path d="{d}" stroke="#fff" stroke-opacity=".09" stroke-width="1" stroke-dasharray="3 2.5" fill="none" transform="translate(3 0)"/>'
    for x in (206, 394):
        g += f'<circle cx="{x}" cy="176" r="4.5" fill="#0a0a0a"/><circle cx="{x}" cy="176" r="2" fill="#2a2a2a"/>'
    g += '<ellipse cx="300" cy="88" rx="11" ry="6" fill="#1d1d1d"/><ellipse cx="298" cy="86" rx="5" ry="2.5" fill="#fff" fill-opacity=".12"/>'
    brim = 'M96 318 Q300 288 504 318 Q526 352 470 376 Q300 420 130 376 Q74 352 96 318 Z'
    g += f'<path d="{brim}" fill="#0d0d0d"/>'
    g += '<path d="M104 322 Q300 294 496 322" stroke="#fff" stroke-opacity=".12" stroke-width="1" stroke-dasharray="3 2.5" fill="none"/>'
    g += '<path d="M112 336 Q300 312 488 336" stroke="#fff" stroke-opacity=".08" stroke-width="1" stroke-dasharray="3 2.5" fill="none"/>'
    g += '<path d="M130 376 Q300 420 470 376" stroke="#fff" stroke-opacity=".08" stroke-width="2" fill="none"/>'
    g += logo_svg
    return g


def helmet(color='#f6f6f3', logo_svg=''):
    g = ground(300, 398, 230, 18)
    dome = 'M136 336 C136 170 214 92 300 92 C386 92 464 170 464 336 Z'
    g += f'<path d="{dome}" fill="{color}"/><path d="{dome}" fill="url(#helmetLight)"/>'
    for x in (252, 348):
        g += f'<path d="M{x} 96 C{x + (x - 300) * .55} 150 {x + (x - 300) * .7} 240 {x + (x - 300) * .72} 336" stroke="#000" stroke-opacity=".10" stroke-width="12" fill="none" filter="url(#soft3)"/>'
        g += f'<path d="M{x - 3} 96 C{x + (x - 300) * .55 - 3} 150 {x + (x - 300) * .7 - 3} 240 {x + (x - 300) * .72 - 3} 336" stroke="#fff" stroke-opacity=".8" stroke-width="3" fill="none"/>'
    brim = 'M80 336 Q300 304 520 336 Q536 356 496 368 Q300 400 104 368 Q64 356 80 336 Z'
    g += f'<path d="{brim}" fill="#ecece8"/><path d="M84 338 Q300 308 516 338" stroke="#fff" stroke-width="2" fill="none"/>'
    g += '<path d="M104 368 Q300 400 496 368" stroke="#000" stroke-opacity=".12" stroke-width="2" fill="none"/>'
    g += logo_svg
    return g


def bottle_big():
    """표지용 유리병 (펌프)."""
    body = ('M150 220 C150 196 170 184 196 180 L196 150 L264 150 L264 180 C290 184 310 196 310 220 '
            'L310 600 C310 624 296 636 272 636 L188 636 C164 636 150 624 150 600 Z')
    g = f'<path d="{body}" fill="url(#bottleBody)"/>'
    g += f'<path d="{body}" fill="none" stroke="#bfe6ec" stroke-opacity=".75" stroke-width="1.4"/>'
    g += '<rect x="166" y="230" width="10" height="380" rx="5" fill="url(#bottleSpec)" opacity=".9"/>'
    g += '<rect x="282" y="250" width="5" height="330" rx="2.5" fill="url(#bottleSpec)" opacity=".45"/>'
    g += '<path d="M160 600 Q230 618 300 600 L300 612 Q230 630 160 612 Z" fill="#cdeef3" fill-opacity=".35"/>'
    g += '<rect x="186" y="96" width="88" height="62" rx="4" fill="url(#pumpMetal)"/>'
    g += '<rect x="214" y="44" width="32" height="56" rx="3" fill="url(#pumpMetal)"/>'
    g += '<path d="M208 34 L300 34 Q318 34 321 46 L323 62 L313 62 L311 51 Q309 50 300 50 L208 50 Z" fill="url(#pumpMetal)"/>'
    g += '<rect x="186" y="96" width="88" height="62" rx="4" fill="#fff" fill-opacity=".05"/>'
    return g


def svg(inner, vb, w, h, extra=''):
    return f'<svg viewBox="{vb}" width="{w}" height="{h}" {extra}>{inner}</svg>'


# ───────── HTML 물건 ─────────
def card_front(scale=1.0):
    s = 6.0 * scale; m = 7 * s
    return f'''<div class="bc bc--f" style="width:{90 * s}px;height:{50 * s}px">
      <div style="position:absolute;left:{m}px;top:{m}px">{logo('lh', h=4.6 * s)}</div>
      <div class="bc__who" style="left:{m}px;bottom:{m}px;--s:{scale}"><b>{REP['name']}</b><span>{REP['title']} · {REP['title_en']}</span></div>
      <div class="bc__info" style="right:{m}px;bottom:{m}px;--s:{scale}"><span><i>M</i>{REP['tel']}</span><span><i>E</i>{REP['mail']}</span></div>
    </div>'''


def card_back(scale=1.0):
    s = 6.0 * scale
    return f'''<div class="bc bc--b" style="width:{90 * s}px;height:{50 * s}px">{logo('ls', h=18 * s, color='#f2f2f0')}</div>'''


def card_stack(face, n=7, edge=TEAL):
    layers = ''.join(f'<div class="bc-layer" style="transform:translateZ({i * 0.9:.1f}px);background:{edge}"></div>' for i in range(n))
    return f'<div class="bc-stack">{layers}<div class="bc-top" style="transform:translateZ({n * 0.9:.1f}px)">{face}</div></div>'


def letterhead(s=1.0):
    W, H = 210 * s, 297 * s
    bars = ''.join(f'<i style="width:{w}%"></i>' for w in (94, 97, 90, 96, 58, 0, 95, 91, 97, 74, 0, 86, 93, 40))
    return f'''<div class="lh" style="width:{W}px;height:{H}px;--s:{s}">
      <div style="position:absolute;left:{20 * s}px;top:{18 * s}px">{logo('lh', h=6 * s)}</div>
      <p class="lh__date" style="right:{20 * s}px;top:{20 * s}px">2026. 11. 26.</p>
      <p class="lh__to" style="left:{20 * s}px;top:{48 * s}px"><b>수신</b> 귀사 담당자님<br><b>제목</b> 유리용기 견적의 건</p>
      <div class="lh__bars" style="left:{20 * s}px;right:{20 * s}px;top:{94 * s}px">{bars}</div>
      <div class="lh__ft" style="left:{20 * s}px;right:{20 * s}px;bottom:{14 * s}px"><span>동림</span><span>{REP['tel']} · {REP['mail']}</span></div>
    </div>'''


def envelope(s=1.0):
    W, H = 220 * s, 105 * s
    return f'''<div class="env" style="width:{W}px;height:{H}px;--s:{s}">
      <div style="position:absolute;left:{12 * s}px;top:{11 * s}px">{logo('lh', h=4.6 * s)}</div>
      <p class="env__from" style="left:{12 * s}px;bottom:{10 * s}px">{REP['tel']}<br>{REP['mail']}</p>
      <div class="env__to" style="left:{110 * s}px;top:{50 * s}px;width:{80 * s}px"><i></i><i></i><i style="width:60%"></i></div>
    </div>'''


def folder(s=1.0):
    W, H = 220 * s, 310 * s
    return f'''<div class="fd" style="width:{W}px;height:{H}px">
      <div style="position:absolute;left:{18 * s}px;top:{20 * s}px">{logo('le', w=70 * s, color='#f2f2f0')}</div>
      <span class="fd__t" style="left:{18 * s}px;bottom:{18 * s}px;font-size:{10 * s}px">QUOTATION · 견적서</span>
      <i class="fd__pocket" style="height:{70 * s}px"></i>
    </div>'''


def sticker_sheet(s=1.0):
    W, H = 150 * s, 200 * s
    cells = ''
    for r in range(3):
        for c in range(2):
            if (r + c) % 2 == 0:
                cells += f'<div class="st__c">{logo("ld", w=44 * s, style="--knock:#ffffff")}</div>'
            else:
                cells += f'<div class="st__c"><div class="st__r" style="width:{44 * s}px;height:{44 * s}px">{logo("ls", w=26 * s)}</div></div>'
    return f'<div class="st" style="width:{W}px;height:{H}px;padding:{14 * s}px">{cells}</div>'


def id_badge(s=1.0, strap=220):
    W, H = 54 * 3.4 * s, 86 * 3.4 * s
    words = ''.join('<span>DONGLIM</span>' for _ in range(6))
    return f'''<div class="idb" style="width:{W}px;--s:{s}">
      <div class="idb__strap" style="height:{strap * s}px;width:{26 * s}px"><div style="gap:{22 * s}px;font-size:{9 * s}px">{words}</div></div>
      <div class="idb__clip" style="width:{30 * s}px;height:{30 * s}px;margin-top:{-12 * s}px"></div>
      <div class="idb__card" style="width:{W}px;height:{H}px;padding:{26 * s}px {22 * s}px">
        {logo('lh', w=W - 46 * s)}
        <div class="idb__photo" style="width:{94 * s}px;height:{110 * s}px;margin-top:{20 * s}px"><svg viewBox="0 0 60 70" width="{76 * s}" height="{89 * s}"><circle cx="30" cy="24" r="12" fill="#c8c8c6"/><path d="M6 70 Q8 42 30 42 Q52 42 54 70 Z" fill="#c8c8c6"/></svg></div>
        <b style="font-size:{19 * s}px;margin-top:{16 * s}px">{REP['name']}</b>
        <span style="font-size:{11 * s}px;margin-top:{6 * s}px">{REP['title']} · {REP['title_en']}</span>
        <i class="idb__edge" style="height:{7 * s}px"></i>
      </div>
    </div>'''


def box3d(W=420, H=300, D=300):
    icons = handling(30)
    return f'''<div class="bx" style="--w:{W}px;--h:{H}px;--d:{D}px">
      <div class="bx__f bx__front">
        <i class="bx__tape-f"></i>
        <div class="bx__logo">{logo('lh', w=W * 0.56)}</div>
        <p class="bx__fr">FRAGILE · GLASS<br><span>유리 제품 · 취급 주의</span></p>
        <div class="bx__icons">{icons}</div>
      </div>
      <div class="bx__f bx__side">
        <div class="bx__label">{logo('lh', h=13)}<dl><div><dt>품번</dt><dd>DL-SR030</dd></div><div><dt>수량</dt><dd>120 EA</dd></div><div><dt>LOT</dt><dd>26-1126</dd></div></dl></div>
        <div class="bx__sidelogo">{logo('ls', w=D * 0.3)}</div>
      </div>
      <div class="bx__f bx__top"><i class="bx__seam"></i><i class="bx__tape-t"></i></div>
    </div>'''


def handling(sz=34):
    glass = '<path d="M6 2 h12 l-1.5 9 a4.5 4.5 0 0 1 -9 0 Z M12 16 v6 M8 22 h8" fill="none" stroke="currentColor" stroke-width="1.7"/>'
    up = '<path d="M7 22 V6 M3 10 L7 4 L11 10 M17 22 V6 M13 10 L17 4 L21 10 M2 23 h20" fill="none" stroke="currentColor" stroke-width="1.7"/>'
    rain = '<path d="M2 12 a10 10 0 0 1 20 0 Z M12 12 v8 a2 2 0 0 1 -4 0 M5 2 l-1 3 M12 0 l-1 3 M19 2 l-1 3" fill="none" stroke="currentColor" stroke-width="1.7"/>'
    return ''.join(f'<svg viewBox="0 0 24 24" width="{sz}" height="{sz}">{x}</svg>' for x in (glass, up, rain))


def ship_label(s=1.0):
    bars = ''.join(f'<rect x="{i * 3}" y="0" width="{(1, 2, 1, 1, 2, 1, 2, 2, 1)[i % 9] * .9}" height="30" fill="{INK}"/>' for i in range(54))
    return f'''<div class="sl" style="width:{100 * 3.6 * s}px;height:{70 * 3.6 * s}px;--s:{s}">
      <div class="sl__hd">{logo('lh', h=20 * s)}<span>SHIPPING LABEL</span></div>
      <dl class="sl__tb"><div><dt>품번</dt><dd>DL-SR030 · 세럼 라운드 30 ml</dd></div><div><dt>색상</dt><dd>투명 (Flint) · 넥 20/410</dd></div>
      <div><dt>수량</dt><dd>120 EA / 1 CTN</dd></div><div><dt>LOT</dt><dd>26-1126 · 검사 완료</dd></div></dl>
      <svg class="sl__bar" viewBox="0 0 162 30" width="{162 * s}" height="{30 * s}">{bars}</svg>
    </div>'''


def tape(len_px=640, h=58):
    units = ''.join(f'<span>{logo("lh", h=h * 0.24)}</span>' for _ in range(max(2, int(len_px / 170) + 1)))
    return f'<div class="tp" style="width:{len_px}px;height:{h}px"><div>{units}</div></div>'


def wall_night(W, H):
    lw = W * 0.6
    return f'''<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" class="wn">
      <rect width="{W}" height="{H}" fill="#18191b"/><rect width="{W}" height="{H}" filter="url(#noise)"/>
      {''.join(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}" stroke="#000" stroke-opacity=".35"/>' for x in range(0, W, W // 5))}
      <rect y="{H * .78}" width="{W}" height="{H * .22}" fill="#0f1011"/>
      <rect y="{H * .78}" width="{W}" height="1.2" fill="#2a2b2e"/>
      {g_logo('lh', (W - lw) / 2, H * 0.34, w=lw, fill='#0e0f10', extra='filter="url(#halo)"')}
    </svg>'''


def glass_door(W, H):
    return f'''<svg viewBox="0 0 400 620" width="{W}" height="{H}" preserveAspectRatio="xMidYMid slice">
      <rect width="400" height="620" fill="#e9eaea"/>
      <rect x="40" y="40" width="320" height="580" fill="#2a2b2d"/>
      <rect x="52" y="52" width="296" height="568" fill="url(#glassDoor)"/>
      <path d="M52 52 L170 52 L52 290 Z" fill="#fff" fill-opacity=".25"/><path d="M200 52 L236 52 L52 450 L52 380 Z" fill="#fff" fill-opacity=".14"/>
      <rect x="318" y="260" width="9" height="150" rx="4.5" fill="url(#metal)"/>
      {g_logo('ls', 140, 230, w=120, fill='#ffffff')}
      <line x1="140" y1="404" x2="260" y2="404" stroke="#fff" stroke-opacity=".8"/>
      <text x="200" y="430" text-anchor="middle" class="gd__t">평일 09:00 – 18:00</text>
      <text x="200" y="450" text-anchor="middle" class="gd__t">{REP['tel']}</text>
    </svg>'''


# ───────── 쪽 틀 ─────────
NAV = [('03', '명함'), ('04', '작업복'), ('05', '유니폼'), ('06', '서식류'), ('07', '포장'), ('08', '사인'), ('09', '사용 규칙')]
TOTAL = 9


def page(no, body, dark_nav=False):
    n = f'{no:02d}'
    links = ''.join(f'<a class="{"is-on" if p == n else ""}">{t}</a>' for p, t in NAV)
    return f'''
<section class="pg" id="p{n}">
  <div class="ub"><span>DONGLIM IDENTITY KIT</span><span>로고 파일 &nbsp;|&nbsp; 사용 규칙 &nbsp;|&nbsp; 문의 {REP['tel']} &nbsp;|&nbsp; {n} / {TOTAL:02d}</span></div>
  <nav class="nv">{logo('lh', h=22)}<div class="nv__links">{links}</div><span class="nv__pill">로고 활용안</span></nav>
  <div class="ct">{body}</div>
</section>'''


def pill(text, kind='primary'):
    return f'<span class="pl pl--{kind}">{text}</span>'


def dots(colors, active=0):
    return '<div class="dots">' + ''.join(
        f'<i class="{"on" if i == active else ""}" style="background:{c}"></i>' for i, c in enumerate(colors)) + '</div>'


def rows(items):
    return '<dl class="rw">' + ''.join(f'<div><dt>{a}</dt><dd>{b}</dd></div>' for a, b in items) + '</dl>'


def pdp(thumbs, main, info):
    th = ''.join(f'<div class="th{" is-on" if i == 0 else ""}">{t}</div>' for i, t in enumerate(thumbs))
    return f'<div class="pdp"><div class="pdp__rail">{th}</div><div class="pdp__main">{main}</div><div class="pdp__info">{info}</div></div>'


def info(badge, title, sub, line, colors, chips, file, spec):
    ch = ''.join(f'<span class="chip{" is-on" if i == 0 else ""}">{c}</span>' for i, c in enumerate(chips))
    return f'''<span class="bd">{badge}</span><h2 class="h-xl">{title}</h2><p class="cap-md">{sub}</p>
      <p class="b-strong">{line}</p>
      <div class="sw"><span class="cap-sm">색상 {len(colors)}</span>{dots(colors)}</div>
      <div class="chips">{ch}</div>
      <div class="ctas">{pill('업체 전달 파일 · ' + file)}</div>
      {rows(spec)}'''


def plp(title, count, crumb, cards):
    cs = ''.join(f'''<article class="pc"><div class="pc__img">{img}</div>{dots(cl)}<span class="bd bd--sm"{'' if bd else ' style="visibility:hidden"'}>{bd or '·'}</span>
      <p class="b-strong">{nm}</p><p class="cap-md">{sub}</p><p class="b-strong pc__price">{spec}</p></article>'''
                 for img, cl, bd, nm, sub, spec in cards)
    return f'''<div class="plp"><div class="sub"><p class="cap-md">로고 활용안 / {crumb}</p><h2 class="h-xl">{title} <span>({count})</span></h2></div>
      <div class="plp__grid">{cs}</div></div>'''


# ───────── 01 표지 (캠페인 타일) ─────────
def p_cover():
    tile = f'''<div class="cmp">
      <svg class="cmp__art" viewBox="0 0 1520 860" width="1520" height="860" preserveAspectRatio="xMidYMid slice">
        <rect width="1520" height="860" fill="#0c0d0e"/>
        <radialGradient id="spot" cx=".72" cy=".42" r=".55"><stop offset="0" stop-color="#20393d"/><stop offset="1" stop-color="#0c0d0e" stop-opacity="0"/></radialGradient>
        <rect width="1520" height="860" fill="url(#spot)"/>
        <rect y="700" width="1520" height="160" fill="#080909"/>
        <ellipse cx="1090" cy="712" rx="230" ry="16" fill="#000" opacity=".8" filter="url(#soft6)"/>
        <g transform="translate(860 40) scale(1.02)">{bottle_big()}</g>
        <g transform="translate(1120 210) scale(.78)" opacity=".85">{bottle_big()}</g>
        <ellipse cx="1090" cy="716" rx="200" ry="6" fill="#9fd3dc" opacity=".12" filter="url(#soft6)"/>
      </svg>
      <div class="cmp__copy">
        {logo('lh', h=30, color='#ffffff')}
        <h1 class="disp">DONGLIM<br>IDENTITY KIT</h1>
        <p class="cmp__sub">명함부터 작업복, 출고 박스, 간판까지 — 동림 로고를 실제로 쓰는 방법</p>
        {pill('활용안 7종 보기', 'onimg')}
      </div>
    </div>'''
    return page(1, tile)


# ───────── 02 둘러보기 (레일) ─────────
def p_index():
    jk = svg(jacket(True, logo_svg=g_logo('lh', 330, 196, w=56, fill='url(#stitchW)', extra='filter="url(#emb)"')), '40 0 520 640', 220, 272)
    po = svg(polo(logo_svg=g_logo('lh', 330, 168, w=52, fill='url(#stitchK)')), '60 30 480 560', 214, 250)
    minis = [
        ('03', '명함', 'Business card', f'<div class="mini mini--card">{card_front(0.36)}</div>'),
        ('04', '작업복', 'Workwear', jk),
        ('05', '유니폼', 'Polo · Cap · Helmet · ID', po),
        ('06', '서식류', 'Stationery', f'<div class="mini">{letterhead(0.8)}</div>'),
        ('07', '포장', 'Packaging', f'<div class="mini mini--box">{box3d(150, 108, 108)}</div>'),
        ('08', '사인', 'Signage', wall_night(214, 330)),
        ('09', '사용 규칙', 'Usage guide', f'<div class="mini mini--guide"><div>{logo("lh", w=140)}</div></div>'),
    ]
    cards = ''.join(f'''<article class="rc"><div class="rc__img{' rc__img--dark' if n == '08' else ''}">{m}</div>
      <p class="b-strong">{t}</p><p class="cap-md">{e}</p><p class="cap-sm rc__p">p.{n}</p></article>''' for n, t, e, m in minis)
    body = f'''<div class="ix">
      <div class="ix__hd"><div><p class="cap-md">로고 활용안</p><h2 class="h-xl">활용안 둘러보기</h2></div>
        <div class="ix__nav"><span class="ib">‹</span><span class="ib">›</span></div></div>
      <div class="rail">{cards}</div>
      <div class="ix__band">
        <div class="ix__big"><p class="disp disp--ink">ONE MARK.<br>EVERY SURFACE.</p></div>
        <div class="ix__txt"><p class="b-md">종이, 실, 골판지, 금속, 유리. 재료가 바뀌어도 로고는 같은 모양, 같은 색으로 씁니다.
          어두운 바탕에는 흰색 로고, 밝은 바탕에는 먹색 로고 — 이 두 가지가 전부입니다.</p>
          <div class="ctas">{pill('파일: donglim/brand/logo/svg')}{pill('사용 규칙 p.09', 'secondary')}</div></div>
      </div>
    </div>'''
    return page(2, body)


# ───────── 03 명함 (PDP) ─────────
def p_card():
    main = f'''<div class="desk"><div class="plane">
        <div class="pos" style="left:10px;top:10px;transform:rotateZ(-8deg)">{card_stack(card_front(1.0))}</div>
        <div class="pos" style="left:140px;top:330px;transform:rotateZ(16deg)">{card_stack(card_back(1.0), n=5, edge=TEAL)}</div>
      </div></div>'''
    thumbs = [f'<div class="tz">{card_front(0.13)}</div>', f'<div class="tz">{card_back(0.13)}</div>',
              '<svg viewBox="0 0 72 72" width="72" height="72">' + ''.join(f'<rect x="12" y="{20 + i * 7}" width="48" height="5" fill="#fff"/><rect x="12" y="{25 + i * 7}" width="48" height="1.6" fill="#0a7281"/>' for i in range(5)) + '</svg>']
    inf = info('추천', '명함', 'Business card · 90 × 50 mm', '앞 먹 1도 · 뒤 백색 박 · 청록 엣지',
               ['#ffffff', '#111111'], ['앞면', '뒷면', '옆면'], 'donglim-horizontal.svg',
               [('앞면 용지', '랑데뷰 울트라화이트 240g'), ('뒷면 용지', '블랙 매직 300g'), ('후가공', '백색 박 · 엣지 컬러 #0A7281'),
                ('로고', '앞 높이 4.6 mm · 뒤 세로형 18 mm'), ('기본 수량', '200매 / 1인')])
    return page(3, pdp(thumbs, main, inf))


# ───────── 04 작업복 (PDP) ─────────
def p_work():
    chest = g_logo('lh', 328, 198, w=58, fill='url(#stitchW)', extra='filter="url(#emb)"')
    back = g_logo('ls', 222, 228, w=156, fill='url(#stitchW)', extra='filter="url(#emb)"')
    main = f'''<div class="duo">
      {svg(jacket(True, logo_svg=chest), '40 0 520 640', 430, 530)}
      {svg(jacket(False, logo_svg=back), '40 0 520 640', 430, 530)}
    </div>'''
    zoom = svg(f'<rect width="120" height="120" fill="#25292e"/><rect width="120" height="120" fill="url(#twill)"/>{g_logo("lh", 8, 50, w=104, fill="url(#stitchW)", extra="filter=&quot;url(#emb)&quot;")}', '0 0 120 120', 72, 72)
    thumbs = [svg(jacket(True, logo_svg=chest), '40 0 520 640', 60, 72), svg(jacket(False, logo_svg=back), '40 0 520 640', 60, 72), zoom]
    inf = info('현장용', '작업복 점퍼', 'Workwear · 생산 · 출고 현장', '가슴 가로형 · 등판 세로형 백색 자수',
               ['#25292e', '#111111', '#5d6166'], ['가슴 110 mm', '등판 300 mm', '이름 자수'], 'donglim-stacked-white.svg',
               [('원단', '폴리 트윌 · 차콜 #25292E, 어깨 블랙 배색'), ('자수', '백색 실 · 새틴 스티치'), ('가슴', '가로형 폭 110 mm (보는 쪽 오른쪽)'),
                ('등판', '세로형 폭 300 mm · 목선 아래 120 mm'), ('주의', '어두운 원단에는 흰색 파일만')])
    return page(4, pdp(thumbs, main, inf))


# ───────── 05 유니폼 (PLP) ─────────
def p_uniform():
    po = svg(polo(logo_svg=g_logo('lh', 330, 168, w=52, fill='url(#stitchK)')), '60 30 480 560', 330, 385)
    cp = svg(cap(logo_svg=g_logo('ls', 236, 150, w=128, fill='url(#stitchW)', extra='filter="url(#emb)"')), '60 60 480 380', 330, 261)
    hm = svg(helmet(logo_svg=g_logo('lh', 214, 236, w=172, fill=INK)), '60 70 480 360', 330, 248)
    cards = [
        (po, ['#fbfbf9', '#111111', '#25292e'], '사무 · 영업', '폴로셔츠', 'Polo · 화이트 피케', '가슴 가로형 먹색 자수 90 mm'),
        (cp, ['#151515', '#25292e', '#f5f5f5'], '', '모자', 'Cap · 블랙 6패널', '정면 세로형 백색 자수'),
        (hm, ['#f6f6f3', '#e9d34a'], '현장 안전', '안전모', 'Safety helmet · 화이트', '정면 가로형 먹색 실크 인쇄'),
        (f'<div class="pc__id">{id_badge(0.82, strap=120)}</div>', ['#111111'], '', '사원증', 'ID card · 54 × 86 mm', '목걸이 줄 DONGLIM 반복 인쇄'),
    ]
    return page(5, plp('유니폼 · 소품', 4, '유니폼', cards))


# ───────── 06 서식류 (PLP) ─────────
def p_stationery():
    cards = [
        (f'<div class="pc__obj">{letterhead(1.12)}</div>', ['#ffffff'], '기본', '레터헤드', 'Letterhead · A4', '로고 높이 6 mm · 여백 20 mm'),
        (f'<div class="pc__obj">{envelope(1.36)}</div>', ['#ffffff', '#111111'], '', '규격 봉투', 'Envelope · 220 × 105 mm', '먹 1도 · 로고 4.6 mm'),
        (f'<div class="pc__obj">{folder(1.08)}</div>', ['#111111'], '영업', '견적서 폴더', 'Folder · 220 × 310 mm', '영문 단독 백색 박'),
        (f'<div class="pc__obj">{sticker_sheet(1.55)}</div>', ['#111111', '#ffffff'], '', '스티커', 'Sticker · 30 mm', 'D 타일 · 원형 세로형'),
    ]
    return page(6, plp('서식류', 4, '서식류', cards))


# ───────── 07 포장 (PDP) ─────────
def p_pack():
    main = f'''<div class="pk"><div class="pk__box">{box3d()}</div>{svg(ground(260, 30, 260, 26), '0 0 520 60', 520, 60, 'class="pk__gr"')}</div>'''
    thumbs = [f'<div class="tz">{box3d(36, 26, 26)}</div>', f'<div class="tz">{ship_label(0.17)}</div>', f'<div class="tz tz--tape">{tape(120, 16)}</div>']
    inf = info('출고', '출고 박스', 'Packaging · 크라프트 골판지', '먹 1도 플렉소 · 박스 라벨 · 로고 테이프',
               ['#c8a87f', '#f5f5f5'], ['정면', '측면 라벨', '테이프'], 'donglim-horizontal.svg',
               [('박스', '이중 골판지 · 크라프트'), ('인쇄', '먹 1도 · 정면 가로형 폭 = 박스 폭 56%'), ('라벨', '감열지 100 × 70 mm'),
                ('테이프', 'OPP 투명 48 mm · 로고 반복'), ('표시', 'FRAGILE · 위로 · 습기 주의')])
    return page(7, pdp(thumbs, main, inf))


# ───────── 08 사인 (캠페인 2칸) ─────────
def p_sign():
    body = f'''<div class="cmp2">
      <div class="cmp2__a">{wall_night(1000, 836)}
        <div class="cmp__copy cmp__copy--sm"><h2 class="disp disp--md">MADE<br>HERE.</h2>
          <p class="cmp__sub">외벽 간판 · 후광 조명 채널 문자 · 폭 2,400 mm</p>{pill('먹색 알루미늄 · 벽에서 40 mm 띄움', 'onimg')}</div></div>
      <div class="cmp2__b">{glass_door(512, 836)}
        <div class="cmp__copy cmp__copy--sm cmp__copy--ink"><p class="cmp__sub">출입문 유리 · 백색 시트 커팅</p>{pill('세로형 폭 300 mm', 'primary')}</div></div>
    </div>'''
    return page(8, body)


# ───────── 09 사용 규칙 (FAQ 줄) ─────────
def p_guide():
    W = 470; H = W / RATIO['lh']; x = H * 0.86
    clear = f'''<div class="gd-clear" style="width:{W + 2 * x}px;height:{H + 2 * x}px"><i style="inset:{x}px"></i>
      <div style="position:absolute;left:{x}px;top:{x}px">{logo('lh', w=W)}</div>
      <b style="left:{x / 2 - 5}px;top:{x + H / 2 - 9}px">x</b><b style="right:{x / 2 - 5}px;top:{x + H / 2 - 9}px">x</b>
      <b style="left:{x + W / 2 - 5}px;top:{x / 2 - 9}px">x</b><b style="left:{x + W / 2 - 5}px;bottom:{x / 2 - 9}px">x</b></div>'''
    mins = f'''<div class="gd-min"><div>{logo('lh', h=17)}<span>가로형 · 25 mm / 100 px</span></div>
      <div>{logo('ls', h=40)}<span>세로형 · 15 mm / 60 px</span></div><div>{logo('ld', h=24)}<span>D 타일 · 5 mm / 16 px</span></div></div>'''
    sw = ''.join(f'<div><i style="background:{c}"></i><b>{n}</b><span>{c.upper()} · {d}</span></div>' for c, n, d in
                 [('#111111', 'INK', '로고 기본'), ('#ffffff', 'WHITE', '어두운 바탕'), ('#f5f5f5', 'SOFT CLOUD', '바탕'), ('#0a7281', 'TEAL', '엣지 · 한 곳만')])
    donts = ''.join(f'<div><div class="gd-x">{v}</div><span>{t}</span></div>' for v, t in [
        (logo('lh', w=96, style='transform:scaleX(1.5)'), '늘이기'),
        (f'<svg width="120" height="{120 / RATIO["lh"]:.1f}" viewBox="0 0 120 {120 / RATIO["lh"]:.1f}"><defs><clipPath id="hf"><rect width="45" height="30"/></clipPath></defs>{g_logo("lh", 0, 0, w=120, fill=INK)}<g clip-path="url(#hf)">{g_logo("lh", 0, 0, w=120, fill="#d30005")}</g></svg>', '색 나누기'),
        (f'<div style="background:#cacacb;padding:8px 10px">{logo("lh", w=100, color="#9e9ea0")}</div>', '낮은 대비'),
        (logo('lh', w=120, style='filter:drop-shadow(3px 4px 2px rgba(0,0,0,.5))'), '그림자 효과')])
    body = f'''<div class="gd">
      <div class="gd__l"><p class="cap-md">로고 활용안 / 사용 규칙</p><h2 class="disp disp--ink disp--md">RULES</h2>
        <p class="b-md">로고를 쓸 때 지킬 네 가지입니다. 인쇄소·자수 업체에는 SVG 파일을 그대로 전달하세요.</p>
        <div class="ctas">{pill('donglim/brand/logo/svg')}</div></div>
      <div class="gd__r">
        <div class="gd-row"><h3>여백</h3><div>{clear}<p class="cap-md">로고 둘레에 ‘동’ 한 글자 높이(x)만큼 비웁니다.</p></div></div>
        <div class="gd-row"><h3>최소 크기</h3>{mins}</div>
        <div class="gd-row"><h3>색</h3><div class="gd-sw">{sw}</div></div>
        <div class="gd-row"><h3>하지 말 것</h3><div class="gd-dont">{donts}</div></div>
      </div></div>'''
    return page(9, body)


PAGES = [p_cover(), p_index(), p_card(), p_work(), p_uniform(), p_stationery(), p_pack(), p_sign(), p_guide()]

CSS = r'''
:root { --ink:#111111; --canvas:#ffffff; --cloud:#f5f5f5; --hair:#cacacb; --hair-soft:#e5e5e5; --mute:#707072; --stone:#9e9ea0; --teal:#0a7281; --charcoal:#39393b; }
* { box-sizing:border-box; margin:0; padding:0; }
html { background:#dcdcdc; }
body { font-family:'Inter','Pretendard Variable','Pretendard',sans-serif; color:var(--ink); word-break:keep-all; -webkit-font-smoothing:antialiased; }
.pg { position:relative; width:1600px; height:1000px; margin:0 auto 40px; background:var(--canvas); overflow:hidden; break-after:page; }
.pg:last-child { margin-bottom:0; }
.lg { display:block; overflow:visible; flex:none; }

/* 상단 바 (utility-bar · primary-nav) */
.ub { height:36px; background:var(--cloud); display:flex; justify-content:space-between; align-items:center; padding:0 40px; font:500 12px/1.5 'Inter','Pretendard Variable',sans-serif; }
.ub span:first-child { letter-spacing:.08em; }
.nv { height:64px; display:flex; align-items:center; padding:0 40px; box-shadow:inset 0 -1px 0 var(--hair-soft); }
.nv__links { flex:1; display:flex; justify-content:center; gap:28px; font:500 16px/1.5 'Inter','Pretendard Variable',sans-serif; }
.nv__links a { padding:20px 0 18px; border-bottom:2px solid transparent; }
.nv__links a.is-on { border-color:var(--ink); }
.nv__pill { height:40px; padding:0 18px; border-radius:24px; background:var(--cloud); display:flex; align-items:center; font:400 15px 'Inter','Pretendard Variable',sans-serif; color:var(--mute); }
.ct { position:absolute; left:0; right:0; top:100px; bottom:0; }

/* 타이포 토큰 */
.disp { font:400 148px/.9 'Anton','Pretendard Variable',sans-serif; text-transform:uppercase; letter-spacing:-.005em; color:#fff; }
.disp--ink { color:var(--ink); }
.disp--md { font-size:120px; }
.h-xl { font:500 32px/1.2 'Inter','Pretendard Variable',sans-serif; letter-spacing:-.01em; }
.h-xl span { color:var(--mute); }
.b-md { font:400 16px/1.5 'Inter','Pretendard Variable',sans-serif; color:var(--charcoal); }
.b-strong { font:500 16px/1.5 'Inter','Pretendard Variable',sans-serif; }
.cap-md { font:500 14px/1.5 'Inter','Pretendard Variable',sans-serif; color:var(--mute); }
.cap-sm { font:500 12px/1.5 'Inter','Pretendard Variable',sans-serif; color:var(--mute); }

/* 알약형 요소 */
.pl { display:inline-flex; align-items:center; height:48px; padding:0 28px; border-radius:30px; font:500 16px/1.5 'Inter','Pretendard Variable',sans-serif; white-space:nowrap; }
.pl--primary { background:var(--ink); color:#fff; }
.pl--secondary { background:var(--cloud); color:var(--ink); }
.pl--onimg { background:#fff; color:var(--ink); height:44px; padding:0 24px; }
.ctas { display:flex; gap:10px; flex-wrap:wrap; }
.bd { align-self:flex-start; display:inline-block; padding:4px 12px; border:1px solid var(--hair); border-radius:30px; font:500 12px/1.5 'Inter','Pretendard Variable',sans-serif; background:#fff; }
.bd--sm { margin-top:2px; }
.chips { display:flex; gap:8px; flex-wrap:wrap; }
.chip { padding:8px 16px; border:1px solid var(--hair); border-radius:30px; font:500 15px/1.5 'Inter','Pretendard Variable',sans-serif; }
.chip.is-on { background:var(--ink); border-color:var(--ink); color:#fff; }
.dots { display:flex; gap:8px; }
.dots i { width:12px; height:12px; border-radius:50%; box-shadow:0 0 0 1px var(--hair); }
.dots i.on { box-shadow:0 0 0 2px #fff, 0 0 0 4px var(--ink); }
.sw { display:flex; align-items:center; gap:14px; }
.ib { width:40px; height:40px; border-radius:50%; background:var(--cloud); display:grid; place-items:center; font:500 22px/1 'Inter',sans-serif; }

/* 캠페인 타일 */
.cmp { position:absolute; left:40px; right:40px; top:24px; bottom:40px; overflow:hidden; background:#0c0d0e; }
.cmp__art { position:absolute; inset:0; width:100%; height:100%; }
.cmp__copy { position:absolute; left:56px; bottom:56px; display:flex; flex-direction:column; align-items:flex-start; gap:24px; }
.cmp__copy .disp { margin-top:28px; }
.cmp__sub { font:500 16px/1.5 'Inter','Pretendard Variable',sans-serif; color:#fff; }
.cmp__copy--sm { left:40px; bottom:40px; gap:18px; }
.cmp__copy--ink { left:84px; }
.cmp__copy--ink .cmp__sub { color:var(--ink); }
.cmp2 { position:absolute; left:40px; right:40px; top:24px; bottom:40px; display:grid; grid-template-columns:1000px 1fr; gap:8px; }
.cmp2__a, .cmp2__b { position:relative; overflow:hidden; }
.cmp2__b svg { display:block; width:100%; height:100%; }
.gd__t { font:500 11px 'Inter','Pretendard Variable',sans-serif; fill:#fff; letter-spacing:.06em; }

/* 둘러보기 */
.ix { position:absolute; inset:24px 40px 40px; display:flex; flex-direction:column; }
.ix__hd { display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:18px; }
.ix__nav { display:flex; gap:10px; }
.rail { display:grid; grid-template-columns:repeat(7,1fr); gap:8px; }
.rc__img { height:330px; background:var(--cloud); display:grid; place-items:center; overflow:hidden; margin-bottom:10px; }
.rc__img--dark { background:#18191b; }
.rc__img > svg { display:block; }
.rc__p { margin-top:2px; }
.mini { display:grid; place-items:center; }
.mini--card .bc { box-shadow:0 0 0 1px rgba(0,0,0,.04); }
.mini--box .bx { transform:rotateX(-22deg) rotateY(-36deg) translateX(10px); }
.mini--guide > div { padding:18px; background:#fff; outline:1px solid var(--teal); outline-offset:-1px; }
.ix__band { margin-top:40px; flex:1; display:grid; grid-template-columns:1fr 560px; gap:48px; align-items:end; border-top:1px solid var(--hair); padding-top:36px; }
.ix__big .disp { font-size:112px; }
.ix__txt { display:grid; gap:24px; padding-bottom:8px; }

/* PDP */
.pdp { position:absolute; inset:24px 40px 40px; display:grid; grid-template-columns:72px 900px 1fr; gap:0 24px; }
.pdp__rail { display:flex; flex-direction:column; gap:8px; }
.th { width:72px; height:72px; background:var(--cloud); display:grid; place-items:center; overflow:hidden; position:relative; }
.th.is-on::after { content:''; position:absolute; inset:0; box-shadow:inset 0 0 0 1.5px var(--ink); }
.pdp__main { background:var(--cloud); position:relative; overflow:hidden; display:grid; place-items:center; }
.pdp__info { display:flex; flex-direction:column; gap:14px; padding:4px 0 0 32px; }
.pdp__info .h-xl { margin-top:4px; }
.pdp__info .cap-md { margin-top:-10px; }
.pdp__info .ctas { margin-top:8px; }
.rw { margin-top:14px; border-top:1px solid var(--hair); }
.rw div { display:flex; justify-content:space-between; gap:20px; padding:16px 0; border-bottom:1px solid var(--hair); }
.rw dt { font:500 16px/1.5 'Inter','Pretendard Variable',sans-serif; flex:none; }
.rw dd { font:500 14px/1.6 'Inter','Pretendard Variable',sans-serif; color:var(--mute); text-align:right; }
.duo { display:flex; gap:10px; align-items:center; }
.tz { display:grid; place-items:center; width:100%; height:100%; }
.tz--edge { display:flex; flex-direction:column; justify-content:center; gap:2px; padding:0 14px; }
.tz--edge i { display:block; height:5px; background:#fff; border-bottom:2px solid var(--teal); }
.tz--tape { transform:rotate(-14deg); }

/* 명함 3D */
.desk { position:absolute; inset:0; perspective:2400px; perspective-origin:50% 20%; }
.plane { position:absolute; left:70px; top:120px; width:760px; height:620px; transform-style:preserve-3d; transform:rotateX(50deg) rotateZ(-14deg); }
.pos { position:absolute; transform-style:preserve-3d; }
.bc-stack { position:relative; width:540px; height:300px; transform-style:preserve-3d; }
.bc-stack::before { content:''; position:absolute; inset:-10px; background:rgba(0,0,0,.28); filter:blur(16px); transform:translate(14px,22px); }
.bc-layer, .bc-top { position:absolute; inset:0; border-radius:2px; }
.bc-top > .bc { width:100% !important; height:100% !important; }
.bc { position:relative; border-radius:2px; overflow:hidden; }
.bc--f { background:#fdfdfc; }
.bc--f::after { content:''; position:absolute; inset:0; background:linear-gradient(140deg,rgba(255,255,255,.9),rgba(255,255,255,0) 45%,rgba(0,0,0,.03)); pointer-events:none; }
.bc--b { background:#141414; display:grid; place-items:center; }
.bc__who { position:absolute; display:grid; gap:calc(6px * var(--s)); }
.bc__who b { font:600 calc(21px * var(--s))/1 'Pretendard Variable',sans-serif; letter-spacing:.02em; }
.bc__who span { font:500 calc(11.5px * var(--s))/1 'Inter','Pretendard Variable',sans-serif; color:var(--mute); }
.bc__info { position:absolute; display:grid; gap:calc(7px * var(--s)); text-align:right; font:500 calc(11.5px * var(--s))/1 'Inter',sans-serif; }
.bc__info i { font-style:normal; color:var(--teal); margin-right:calc(10px * var(--s)); }

/* 서식류 */
.lh { position:relative; background:#fff; box-shadow:0 1px 2px rgba(0,0,0,.06), 0 14px 26px -16px rgba(0,0,0,.35); }
.lh__date { position:absolute; font:500 calc(9.5px * var(--s)) 'Inter',sans-serif; color:var(--mute); }
.lh__to { position:absolute; font:400 calc(10px * var(--s))/1.9 'Pretendard Variable',sans-serif; color:var(--charcoal); }
.lh__to b { font-weight:600; margin-right:calc(8px * var(--s)); }
.lh__bars { position:absolute; display:grid; gap:calc(9px * var(--s)); }
.lh__bars i { display:block; height:calc(3px * var(--s)); background:#e2e2e2; }
.lh__ft { position:absolute; display:flex; white-space:nowrap; gap:8px; justify-content:space-between; padding-top:calc(8px * var(--s)); border-top:1px solid var(--ink); font:500 calc(7.5px * var(--s)) 'Inter','Pretendard Variable',sans-serif; color:var(--mute); }
.env { position:relative; background:#fff; box-shadow:0 1px 2px rgba(0,0,0,.06), 0 14px 26px -16px rgba(0,0,0,.35); }
.env__from { position:absolute; font:500 calc(8.5px * var(--s))/1.6 'Inter',sans-serif; color:var(--mute); }
.env__to { position:absolute; display:grid; gap:calc(11px * var(--s)); }
.env__to i { display:block; height:calc(3px * var(--s)); background:#e2e2e2; width:100%; }
.fd { position:relative; background:#141414; box-shadow:0 14px 26px -14px rgba(0,0,0,.45); }
.fd__t { position:absolute; z-index:2; font-family:'Inter','Pretendard Variable',sans-serif; font-weight:500; letter-spacing:.24em; color:#9e9ea0; }
.fd__pocket { position:absolute; left:0; right:0; bottom:0; background:linear-gradient(#1c1c1c,#161616); border-top:1px solid #2a2a2a; clip-path:polygon(0 18%,100% 0,100% 100%,0 100%); }
.st { background:#fff; display:grid; grid-template-columns:1fr 1fr; align-items:center; justify-items:center; box-shadow:0 14px 26px -16px rgba(0,0,0,.35); }
.st__r { border-radius:50%; background:#fff; box-shadow:inset 0 0 0 1.2px var(--teal); display:grid; place-items:center; }

/* 사원증 */
.idb { display:flex; flex-direction:column; align-items:center; }
.idb__strap { background:#141414; overflow:hidden; }
.idb__strap div { display:flex; flex-direction:column; align-items:center; padding-top:10px; }
.idb__strap span { writing-mode:vertical-rl; font-family:'Inter',sans-serif; font-weight:600; letter-spacing:.3em; color:#eaeaea; }
.idb__clip { border-radius:6px; background:linear-gradient(#cfd3d5,#9aa1a5); position:relative; z-index:2; }
.idb__card { position:relative; margin-top:-14px; background:#fff; border-radius:9px; display:flex; flex-direction:column; align-items:center; overflow:hidden; box-shadow:0 1px 2px rgba(0,0,0,.06), 0 16px 26px -16px rgba(0,0,0,.4); }
.idb__photo { background:#ececec; display:grid; place-items:end center; overflow:hidden; }
.idb__card b { font-family:'Pretendard Variable',sans-serif; font-weight:600; letter-spacing:.04em; }
.idb__card span { font-family:'Inter','Pretendard Variable',sans-serif; font-weight:500; color:var(--mute); }
.idb__edge { position:absolute; left:0; right:0; bottom:0; background:var(--ink); }

/* PLP */
.plp { position:absolute; inset:24px 40px 40px; }
.sub { display:grid; gap:2px; margin-bottom:24px; }
.plp__grid { display:grid; grid-template-columns:repeat(4,1fr); gap:8px; }
.pc { display:flex; flex-direction:column; gap:8px; }
.pc__img { height:560px; background:var(--cloud); display:grid; place-items:center; overflow:hidden; margin-bottom:6px; }
.pc .b-strong + .cap-md { margin-top:-8px; }
.pc__price { margin-top:-2px; }
.pc__obj { display:grid; place-items:center; }
.pc__id { display:flex; justify-content:center; align-self:start; }

/* 포장 */
.pk { position:relative; width:100%; height:100%; display:grid; place-items:center; }
.pk__box { perspective:2000px; transform:translateY(-10px); }
.pk__gr { position:absolute; left:50%; bottom:150px; transform:translateX(-50%); }
.bx { position:relative; width:var(--w); height:var(--h); transform-style:preserve-3d; transform:rotateX(-20deg) rotateY(-34deg); }
.bx__f { position:absolute; left:0; top:0; backface-visibility:hidden; overflow:hidden; }
.bx__f::before { content:''; position:absolute; inset:0; background:repeating-linear-gradient(90deg,rgba(0,0,0,.022) 0 2px,transparent 2px 7px); }
.bx__front { width:var(--w); height:var(--h); background:linear-gradient(#cfae84,#c4a277); transform:translateZ(calc(var(--d) / 2)); }
.bx__side { width:var(--d); height:var(--h); background:linear-gradient(#b8986f,#ad8c63); transform:rotateY(90deg) translateZ(calc(var(--w) - var(--d) / 2)); }
.bx__top { width:var(--w); height:var(--d); background:linear-gradient(#dcc099,#d3b58b); transform:rotateX(90deg) translateZ(calc(var(--d) / 2)); }
.bx__seam { position:absolute; left:0; right:0; top:50%; height:1.5px; background:rgba(80,55,25,.35); }
.bx__tape-t { position:absolute; left:0; right:0; top:calc(50% - 12%); height:24%; background:rgba(246,242,232,.62); }
.bx__tape-f { position:absolute; left:0; right:0; top:0; height:12%; background:rgba(246,242,232,.62); }
.bx__logo { position:absolute; left:8%; top:30%; mix-blend-mode:multiply; }
.bx__fr { position:absolute; left:8%; bottom:9%; font:600 calc(var(--h) * .045)/1.5 'Inter',sans-serif; letter-spacing:.24em; mix-blend-mode:multiply; }
.bx__fr span { font-family:'Pretendard Variable',sans-serif; letter-spacing:.06em; font-weight:500; }
.bx__icons { position:absolute; right:7%; bottom:9%; display:flex; gap:10px; color:var(--ink); mix-blend-mode:multiply; }
.bx__label { position:absolute; left:12%; top:16%; width:76%; background:#fff; padding:10px 12px; display:grid; gap:8px; box-shadow:0 1px 2px rgba(0,0,0,.15); }
.bx__label dl { display:grid; gap:3px; font:500 10px 'Inter','Pretendard Variable',sans-serif; }
.bx__label dl div { display:flex; justify-content:space-between; border-top:1px solid #eee; padding-top:3px; }
.bx__label dt { color:var(--mute); }
.bx__sidelogo { position:absolute; left:50%; bottom:12%; transform:translateX(-50%); mix-blend-mode:multiply; }
.sl { position:relative; background:#fff; padding:calc(18px * var(--s)) calc(20px * var(--s)); box-shadow:0 1px 2px rgba(0,0,0,.08); }
.sl__hd { display:flex; justify-content:space-between; align-items:center; padding-bottom:calc(10px * var(--s)); border-bottom:1px solid var(--ink); }
.sl__hd span { font:500 calc(9px * var(--s)) 'Inter',sans-serif; letter-spacing:.22em; color:var(--mute); }
.sl__tb { margin-top:calc(8px * var(--s)); display:grid; gap:calc(6px * var(--s)); }
.sl__tb div { display:grid; grid-template-columns:calc(44px * var(--s)) 1fr; font:500 calc(11px * var(--s)) 'Pretendard Variable',sans-serif; }
.sl__tb dt { color:var(--mute); }
.sl__bar { position:absolute; right:calc(20px * var(--s)); bottom:calc(16px * var(--s)); }
.tp { background:rgba(246,244,238,.9); overflow:hidden; box-shadow:0 4px 10px -6px rgba(0,0,0,.3); }
.tp div { display:flex; align-items:center; height:100%; gap:40px; padding-left:16px; }

/* 사용 규칙 */
.gd { position:absolute; inset:24px 40px 40px; display:grid; grid-template-columns:420px 1fr; gap:64px; }
.gd__l { display:flex; flex-direction:column; gap:20px; }
.gd__l .disp { margin-top:8px; }
.gd__r { border-top:1px solid var(--hair); }
.gd-row { display:grid; grid-template-columns:160px 1fr; gap:24px; padding:34px 0; border-bottom:1px solid var(--hair); }
.gd-row h3 { font:500 16px/1.5 'Inter','Pretendard Variable',sans-serif; }
.gd-row > div { display:flex; gap:24px; align-items:center; }
.gd-clear { position:relative; background:var(--cloud); flex:none; }
.gd-clear i { position:absolute; border:1px solid var(--teal); }
.gd-clear b { position:absolute; font:500 12px 'Inter',sans-serif; color:var(--teal); }
.gd-min { display:flex; gap:48px; align-items:flex-end; }
.gd-min div { display:grid; gap:10px; justify-items:start; }
.gd-min span, .gd-sw span, .gd-dont span { font:500 12px/1.5 'Inter','Pretendard Variable',sans-serif; color:var(--mute); }
.gd-sw { display:flex; gap:28px; }
.gd-sw div { display:grid; grid-template-columns:auto 1fr; column-gap:10px; align-items:center; }
.gd-sw i { grid-row:span 2; width:36px; height:36px; border-radius:50%; box-shadow:0 0 0 1px var(--hair); }
.gd-sw b { font:500 13px 'Inter',sans-serif; letter-spacing:.06em; }
.gd-dont { display:flex !important; gap:10px !important; }
.gd-dont > div { display:grid; gap:6px; }
.gd-x { width:176px; height:84px; background:var(--cloud); display:grid; place-items:center; position:relative; overflow:hidden; }
.gd-x::after { content:''; position:absolute; inset:0; background:linear-gradient(to top right,transparent calc(50% - .7px),#d30005 calc(50% - .7px),#d30005 calc(50% + .7px),transparent calc(50% + .7px)); }

@media print { html { background:none; } .pg { margin:0; } @page { size:1600px 1000px; margin:0; } }
'''

HTML = f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=1600">
<title>동림 로고 활용안</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
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
