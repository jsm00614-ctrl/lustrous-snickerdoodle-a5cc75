# 로고 원본 생성 스크립트

로고 SVG와 시안 보드(`../index.html`)는 아래 두 스크립트로 만듭니다. 모양을 고칠 때는 SVG를 직접 수정하지 말고, 스크립트의 숫자를 바꾼 뒤 다시 생성하세요.

필요한 것: Python 3, Node.js

```bash
pip install fonttools brotli
```

```bash
mkdir -p /tmp/fonts && cd /tmp/fonts && npm install @fontsource/jost @fontsource/cormorant-garamond @fontsource/noto-serif-kr @fontsource/noto-sans-kr
```

```bash
python donglim/brand/_source/build_logos.py /tmp/fonts/node_modules/@fontsource donglim/brand/logos
```

```bash
python donglim/brand/_source/gen_board.py donglim/brand
```

글꼴은 모두 SIL Open Font License(로고·상업적 사용 가능)이며, 결과 SVG에는 글자가 윤곽선(path)으로 들어가 폰트 없이 열립니다.
