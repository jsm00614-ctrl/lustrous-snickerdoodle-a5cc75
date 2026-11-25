/*
 * viewer3d.js — 제품 상세의 ‘3D’ 탭 (필요할 때만 불러옵니다)
 *
 * CMS의 ‘3D 모델’ 필드에 올릴 수 있는 형식
 *   1) .glb / .gltf  — 일반 3D 파일
 *   2) .js 모듈      — img2threejs 등으로 만든 Three.js 코드
 *        export default function createModel(THREE, options) {
 *          // options.product : 제품 데이터 (높이·지름 mm 등)
 *          // options.color   : { hex, opacity } 선택된 유리 색상
 *          return mesh;       // THREE.Object3D (또는 Promise)
 *        }
 *      모델 단위는 자유롭습니다. 화면 크기에 맞게 자동으로 맞춥니다.
 */
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

export async function mount(container, url, options = {}) {
  const w = container.clientWidth || 380;
  const h = container.clientHeight || 440;
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(w, h);
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  container.innerHTML = '';
  container.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  const camera = new THREE.PerspectiveCamera(32, w / h, 0.01, 1000);
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.autoRotate = true;
  controls.autoRotateSpeed = 1.2;

  let object;
  if (/\.(glb|gltf)(\?|$)/i.test(url)) {
    const { GLTFLoader } = await import('three/addons/loaders/GLTFLoader.js');
    const gltf = await new GLTFLoader().loadAsync(url);
    object = gltf.scene;
  } else {
    const mod = await import(new URL(url, location.href).href);
    // default → createModel → 처음 나오는 함수 순서로 찾습니다 (img2threejs의 이름 붙은 팩토리도 그대로 동작)
    const create = [mod.default, mod.createModel, ...Object.values(mod)].find((f) => typeof f === 'function');
    if (!create) throw new Error('3D 모듈에서 모델을 만드는 함수를 찾지 못했습니다.');
    object = await create(THREE, options);
  }
  scene.add(object);

  // 화면에 맞추기
  const box = new THREE.Box3().setFromObject(object);
  const size = box.getSize(new THREE.Vector3());
  const center = box.getCenter(new THREE.Vector3());
  object.position.sub(center);
  const r = Math.max(size.x, size.y, size.z) || 1;
  camera.position.set(r * 0.9, r * 0.45, r * 2.4);
  camera.near = r / 100; camera.far = r * 100; camera.updateProjectionMatrix();
  controls.target.set(0, 0, 0);

  let raf = 0;
  const tick = () => { controls.update(); renderer.render(scene, camera); raf = requestAnimationFrame(tick); };
  tick();
  const ro = new ResizeObserver(() => {
    const W = container.clientWidth, H = container.clientHeight;
    if (!W || !H) return;
    renderer.setSize(W, H); camera.aspect = W / H; camera.updateProjectionMatrix();
  });
  ro.observe(container);

  return function dispose() {
    cancelAnimationFrame(raf); ro.disconnect(); controls.dispose();
    scene.traverse((o) => { if (o.geometry) o.geometry.dispose(); if (o.material) [].concat(o.material).forEach((m) => m.dispose()); });
    pmrem.dispose(); renderer.dispose(); container.innerHTML = '';
  };
}
