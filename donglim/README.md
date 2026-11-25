# 동림 DONGLIM 홈페이지

화장품 유리용기 B2B 홈페이지입니다. 별도의 빌드 도구 없이 동작하는 정적 사이트(HTML·CSS·JS)이며,
모든 문구와 제품 데이터는 `content/` 폴더의 JSON 파일에 들어 있고 **관리자 페이지(Decap CMS)** 에서 수정합니다.

- 사이트 주소: `https://<사이트주소>/donglim/`
- 관리자 주소: `https://<사이트주소>/donglim/admin/`

---

## 1. 처음 한 번만 하는 설정

1. **이 브랜치를 `main`에 합치기**: 관리자 페이지는 `main` 브랜치에 저장합니다 (`admin/config.yml`의 `branch`).
2. **Netlify에서 GitHub 로그인 연결**: 관리자 페이지에 GitHub 계정으로 로그인하려면 OAuth를 한 번 연결해야 합니다.
   - GitHub → Settings → Developer settings → OAuth Apps → New OAuth App
     - Homepage URL: 사이트 주소
     - Authorization callback URL: `https://api.netlify.com/auth/done`
   - Netlify → 사이트 설정 → Access & security → OAuth → Install provider → GitHub → 위에서 만든 Client ID / Secret 입력
3. **관리자 계정**: 이 저장소에 쓰기 권한이 있는 GitHub 계정이면 로그인할 수 있습니다. 직원이 수정해야 하면 저장소 Collaborator로 초대하세요.
4. **회사 정보 입력**: 관리자 → 설정 → 회사 정보 · 메인 문구 에서 대표자, 사업자등록번호, 주소, 전화, 이메일, 카카오톡 채널 주소를 실제 값으로 바꿔주세요. (지금은 자리표시 값입니다)
5. **샘플 제품 교체**: 지금 들어 있는 24개 제품은 화면 구성을 보여주기 위한 **예시 데이터**입니다. 실제 품번·치수·MOQ로 바꾸거나 삭제하세요.

> 저장하면 GitHub에 커밋되고 Netlify가 자동으로 다시 배포합니다. 반영까지 1~2분 걸립니다.

---

## 2. 제품 올리기

### 한 개씩 (가장 쉬움)
관리자 → **제품 (프리몰드)** → **새 제품**
- 품번, 제품명, 용도, 용량, 높이, 지름, 넥 규격, 색상을 입력하면 오른쪽 미리보기에 **실제 비율의 도면**이 바로 그려집니다.
- 대표 사진을 올리면 목록에는 사진이, 상세에는 도면과 사진이 함께 나옵니다. 사진이 없어도 도면으로 충분히 보입니다.
- **비슷한 제품은 복제가 빠릅니다**: 기존 제품을 열고 → 오른쪽 위 게시 메뉴 → **복제** → 품번·용량·치수만 바꿔 저장.
- 잠시 숨기려면 **공개** 스위치를 끄세요.

### 여러 개를 한 번에 (엑셀)
1. 양식 내려받기: `/donglim/admin/products-template.csv` (엑셀에서 열림)
2. 한 줄에 제품 하나씩 채웁니다. 첫 줄(머리글)은 그대로 두세요.
   - 용도·색상·부자재·후가공·생산방식은 **화면에 보이는 한글 이름**으로 적으면 됩니다. 여러 개는 쉼표로 구분 (예: `투명, 앰버`)
   - 재고·공개는 `Y` / `N`
3. 엑셀에서 **다른 이름으로 저장 → CSV UTF-8 (쉼표로 분리)** 로 저장
4. 관리자 → 설정 → **엑셀 일괄 등록** → 항목 추가 → CSV 파일 올리기 → 저장
5. 배포 로그(Netlify → Deploys)에 `개별 N개 + CSV M행 → 총 K개 제품`이 찍히고, 이름을 못 찾은 값이 있으면 ⚠ 경고로 알려줍니다.

같은 품번이 ‘제품’ 메뉴와 CSV에 모두 있으면 **‘제품’ 메뉴 쪽이 우선**합니다.
CSV로 올린 뒤 사진만 추가하고 싶다면 ‘제품’ 메뉴에서 같은 품번으로 새 제품을 만들면 됩니다.

### 분류·옵션 추가
관리자 → 설정 → **분류 · 옵션** 에서 용도, 유리 색상, 부자재, 후가공, 생산 방식(자동병/수동병)을 추가합니다.
‘키’(영문)는 제품과 연결되는 값이라 한 번 정하면 바꾸지 마세요. 이름은 언제든 바꿔도 됩니다.

---

## 3. 3D 모델 (img2threejs 등)

제품의 **3D 모델** 필드에 파일을 올리면 상세 화면에 `도면 | 3D` 탭이 생깁니다. Three.js는 3D 탭을 누를 때만 불러옵니다.

- `.glb` / `.gltf` 파일, 또는
- Three.js 모듈(`.js`) — 아래 형식으로 내보내면 됩니다:

```js
export default function createModel(THREE, options) {
  // options.product : 제품 데이터 (height, diameter, neck … 단위 mm)
  // options.color   : { hex, opacity } 상세 화면에서 고른 유리 색상
  const mesh = /* ... */;
  return mesh; // THREE.Object3D (Promise도 가능)
}
```

모델 크기·위치는 화면에 맞게 자동으로 맞춥니다. 예제: `models/example-round-bottle.js` (DL-SR030에 연결되어 있음).
Three.js 버전은 `index.html`의 import map에서 바꿀 수 있습니다 (현재 0.160.0).

---

## 4. 문의 접수

문의 폼은 **Netlify Forms** 로 접수됩니다 (Netlify → Forms → `inquiry`).
- 견적함에 담은 제품 목록이 `items` 필드에 자동으로 들어갑니다.
- 첨부파일(로고·스케치)도 함께 받습니다.
- 알림 메일: Netlify → Forms → Form notifications 에서 받을 이메일을 추가하세요.

---

## 5. 파일 구조

```
donglim/
├─ index.html              사이트 (섹션 구조)
├─ css/style.css           디자인
├─ js/app.js               목록·필터·상세·비교·견적함·문의
├─ js/bottle.js            치수 → SVG 도면 그리기
├─ js/viewer3d.js          3D 탭 (필요할 때만 로딩)
├─ content/                ← 관리자 페이지가 수정하는 데이터
│  ├─ products/*.json      제품 1개 = 파일 1개
│  ├─ products.json        자동 생성 (직접 수정 금지)
│  ├─ bulk.json, bulk/     엑셀 일괄 등록 파일
│  ├─ site.json            회사 정보·메인 문구·강점
│  ├─ taxonomy.json        분류·색상·부자재·후가공·생산방식
│  ├─ services.json        서비스·자동/수동병 비교·개발 단계
│  └─ faq.json
├─ admin/                  관리자 페이지 (Decap CMS 설정·미리보기·엑셀 양식)
├─ models/                 3D 모델
├─ images/uploads/         관리자에서 올린 사진
└─ scripts/build-products.mjs   배포 때 products.json 생성
```

## 6. 내 컴퓨터에서 미리보기

```bash
node donglim/scripts/build-products.mjs
```

```bash
python3 -m http.server 8000
```

브라우저에서 `http://localhost:8000/donglim/` 접속 (파일을 더블클릭해서 열면 데이터를 읽지 못합니다).

로그인 없이 관리자 페이지를 써 보려면 저장소 루트에서 `npx decap-server` 를 함께 실행하고 `http://localhost:8000/donglim/admin/` 에 접속합니다.
