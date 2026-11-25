/*
 * 3D 모델 예제 — img2threejs 결과물도 이 형식으로 내보내면 됩니다.
 *
 *   export default function createModel(THREE, options) → THREE.Object3D
 *     options.product : 제품 데이터 (height, diameter, neck … 단위 mm)
 *     options.color   : { hex, opacity } 상세 화면에서 고른 유리 색상
 *
 * 이 예제는 제품 치수로 회전체(Lathe) 유리병과 펌프를 만듭니다.
 */
export default function createModel(THREE, { product = {}, color = {} } = {}) {
  const H = Number(product.height) || 96;
  const R = (Number(product.diameter) || 34) / 2;
  const n = (parseFloat(String(product.neck || '20').match(/\d+(?:\.\d+)?/)) || 20) / 2;
  const nh = 12, sh = Math.min(R * 0.8, H * 0.18), rc = R * 0.2;

  // 바깥 윤곽 (아래 → 위)
  const pts = [new THREE.Vector2(0, 0), new THREE.Vector2(R - rc, 0)];
  for (let i = 1; i <= 6; i++) { const a = (i / 6) * Math.PI / 2; pts.push(new THREE.Vector2(R - rc + Math.sin(a) * rc, rc - Math.cos(a) * rc)); }
  const sb = H - nh - sh;
  pts.push(new THREE.Vector2(R, sb));
  for (let i = 1; i <= 10; i++) { const t = i / 10; pts.push(new THREE.Vector2(R + (n - R) * (t * t * (3 - 2 * t)), sb + sh * t)); }
  pts.push(new THREE.Vector2(n, H), new THREE.Vector2(n - 1.6, H), new THREE.Vector2(n - 1.6, H - nh));
  // 안쪽 (두께 1.6mm, 바닥 두께 반영)
  const base = Math.max(3, H * 0.06);
  pts.push(new THREE.Vector2(R - 1.6, sb), new THREE.Vector2(R - 1.6, base + 2), new THREE.Vector2(0, base));

  const glass = new THREE.MeshPhysicalMaterial({
    color: new THREE.Color(color.hex || '#d9e6e8'),
    transmission: Math.max(0, 1 - (Number(color.opacity) || 0.55) * 0.6),
    roughness: 0.06, thickness: 2.5, ior: 1.5, metalness: 0, clearcoat: 1, side: THREE.DoubleSide, transparent: true,
  });
  const group = new THREE.Group();
  group.add(new THREE.Mesh(new THREE.LatheGeometry(pts, 96), glass));

  // 펌프 (칼라 + 스템 + 버튼 + 노즐)
  const plastic = new THREE.MeshStandardMaterial({ color: '#e6e3dc', roughness: 0.45 });
  const collar = new THREE.Mesh(new THREE.CylinderGeometry(n + 1.5, n + 1.5, nh + 2, 64), plastic);
  collar.position.y = H - nh / 2 + 1;
  const stem = new THREE.Mesh(new THREE.CylinderGeometry(1.8, 1.8, 7, 24), plastic);
  stem.position.y = H + 5.5;
  const w = Math.max(12, n * 1.9);
  const head = new THREE.Mesh(new THREE.BoxGeometry(w, 11, w), plastic);
  head.position.y = H + 14.5;
  const nozzle = new THREE.Mesh(new THREE.CylinderGeometry(1.8, 1.8, 11, 16), plastic);
  nozzle.rotation.z = Math.PI / 2;
  nozzle.position.set(-w / 2 - 5, H + 15, 0);
  group.add(collar, stem, head, nozzle);
  return group;
}
