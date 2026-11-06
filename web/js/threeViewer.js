/**
 * threeViewer.js
 * Quản lý không gian 3D Three.js cho NewAtlas Pro:
 * - Render chất lượng cao (ACESFilmic, PBR Materials, Lighting).
 * - Render 14 đường kinh lạc neon uốn lượn theo giải phẫu cơ thể.
 * - Render 419 huyệt vị với hiệu ứng tương tác Hover/Click/Search.
 * - Tự động ẩn các huyệt và nhãn ở phía sau cơ thể (Backface / Surface Normal Occlusion Culling).
 * - 3D Text Label Sprites (Hiển thị Mã WHO / Tên Việt sắc nét).
 * - Focus camera vào từng phân khu giải phẫu (Đầu mặt, Ngực bụng, Lưng gáy, Tay, Chân).
 * - Điều khiển bóc tách các hệ cơ quan (Da, Xương, Cơ, Thần kinh, Nội tạng, Mạch máu, Bạch huyết).
 */

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/OrbitControls.js';
import { GLTFLoader } from 'three/addons/GLTFLoader.js';

export class ThreeViewer {
  constructor(canvasContainer) {
    this.container = canvasContainer;
    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.controls = null;
    this.loader = new GLTFLoader();

    // Quản lý các nhóm đối tượng 3D
    this.anatomyGroup = new THREE.Group();
    this.meridianGroup = new THREE.Group();
    this.acupointGroup = new THREE.Group();
    this.labelGroup = new THREE.Group();

    // Cache các đối tượng hệ giải phẫu
    this.loadedSystems = new Map(); // systemId -> THREE.Object3D

    // Dữ liệu kinh lạc & huyệt vị
    this.acupoints = [];
    this.meridians = [];
    this.pointObjects = []; // Danh sách chi tiết gồm { mesh, labelSprite, pointData, normal, worldPos, visible }
    this.acupointMeshes = new Map(); // code -> Mesh

    // Quản lý nhãn 3D (Billboard Text)
    this.showLabels = true;
    this.labelDisplayMode = 'code_name'; // 'code_name' (LI4 Hợp Cốc), 'vi_only' (Hợp Cốc), 'code_only' (LI4)

    // Tương tác Raycast
    this.raycaster = new THREE.Raycaster();
    this.mouse = new THREE.Vector2();
    this.hoveredPoint = null;
    this.selectedPoint = null;

    // Callbacks
    this.onPointHover = null;
    this.onPointClick = null;

    // Tween camera state
    this.isTransitioning = false;
    this.targetCameraPos = null;
    this.targetLookAt = null;

    // Bộ lọc phân khu hiện tại
    this.activeRegion = null;

    this.init();
  }

  init() {
    const width = this.container.clientWidth;
    const height = this.container.clientHeight;

    // 1. Khởi tạo Scene
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x0a0d14);

    // 2. Camera
    this.camera = new THREE.PerspectiveCamera(45, width / height, 0.05, 50);
    this.camera.position.set(0, 1.2, 2.5);

    // 3. Renderer
    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false, powerPreference: 'high-performance' });
    this.renderer.setSize(width, height);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.15;
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.container.appendChild(this.renderer.domElement);

    // 4. Controls
    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.06;
    this.controls.minDistance = 0.2;
    this.controls.maxDistance = 6.0;
    this.controls.target.set(0, 0.95, 0); // Ngang tầm ngực/bụng người
    this.controls.update();

    // 5. Hệ thống Chiếu sáng Y khoa
    this.setupLighting();

    // 6. Gắn các nhóm đối tượng vào Scene
    this.scene.add(this.anatomyGroup);
    this.scene.add(this.meridianGroup);
    this.scene.add(this.acupointGroup);
    this.scene.add(this.labelGroup);

    // 7. Lắng nghe sự kiện cửa sổ & chuột
    window.addEventListener('resize', () => this.onWindowResize());
    this.renderer.domElement.addEventListener('pointermove', (e) => this.onPointerMove(e));
    this.renderer.domElement.addEventListener('click', (e) => this.onPointerClick(e));

    // 8. Bắt đầu Vòng lặp Render (Render Loop)
    this.animate();
  }

  setupLighting() {
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
    this.scene.add(ambientLight);

    const keyLight = new THREE.DirectionalLight(0xf5f8ff, 1.3);
    keyLight.position.set(1.5, 3.0, 2.5);
    this.scene.add(keyLight);

    const fillLight = new THREE.DirectionalLight(0xdde8ff, 0.9);
    fillLight.position.set(-2.0, 1.5, 1.0);
    this.scene.add(fillLight);

    const backLight = new THREE.DirectionalLight(0x7090ff, 1.0);
    backLight.position.set(0, 2.0, -2.5);
    this.scene.add(backLight);
  }

  onWindowResize() {
    const width = this.container.clientWidth;
    const height = this.container.clientHeight;
    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(width, height);
  }

  onPointerMove(event) {
    const rect = this.renderer.domElement.getBoundingClientRect();
    this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

    // Raycast chỉ kiểm tra các huyệt ĐANG HIỂN THỊ (không bị ẩn phía sau)
    this.raycaster.setFromCamera(this.mouse, this.camera);
    const visibleMeshes = this.pointObjects
      .filter(po => po.mesh.visible)
      .map(po => po.mesh);

    const intersects = this.raycaster.intersectObjects(visibleMeshes, false);

    if (intersects.length > 0) {
      const hitMesh = intersects[0].object;
      const pointData = hitMesh.userData.point;
      this.renderer.domElement.style.cursor = 'pointer';

      if (this.hoveredPoint !== pointData) {
        if (this.hoveredPoint && this.acupointMeshes.has(this.hoveredPoint.code)) {
          this.resetPointScale(this.acupointMeshes.get(this.hoveredPoint.code));
        }
        this.hoveredPoint = pointData;
        hitMesh.scale.set(1.8, 1.8, 1.8);
        if (this.onPointHover) this.onPointHover(pointData, event);
      }
    } else {
      this.renderer.domElement.style.cursor = 'default';
      if (this.hoveredPoint) {
        if (this.acupointMeshes.has(this.hoveredPoint.code)) {
          this.resetPointScale(this.acupointMeshes.get(this.hoveredPoint.code));
        }
        this.hoveredPoint = null;
        if (this.onPointHover) this.onPointHover(null, event);
      }
    }
  }

  onPointerClick(event) {
    if (this.hoveredPoint) {
      this.selectAcupoint(this.hoveredPoint.code, true);
    }
  }

  resetPointScale(mesh) {
    if (this.selectedPoint && mesh.userData.point.code === this.selectedPoint.code) {
      mesh.scale.set(2.0, 2.0, 2.0);
    } else {
      mesh.scale.set(1.0, 1.0, 1.0);
    }
  }

  /**
   * Chọn và focus Camera mượt mà vào một Huyệt vị
   */
  selectAcupoint(code, triggerCallback = true) {
    const mesh = this.acupointMeshes.get(code);
    if (!mesh) return;

    const point = mesh.userData.point;
    this.selectedPoint = point;

    // Highlight huyệt được chọn
    for (const [mCode, mObj] of this.acupointMeshes.entries()) {
      if (mCode === code) {
        mObj.scale.set(2.0, 2.0, 2.0);
        mObj.material.color.setHex(0xffffff);
      } else {
        mObj.scale.set(1.0, 1.0, 1.0);
        mObj.material.color.setHex(mObj.userData.defaultColor);
      }
    }

    const targetWorldPos = new THREE.Vector3();
    mesh.getWorldPosition(targetWorldPos);

    // Tính vị trí camera hướng vào huyệt theo hướng vector pháp tuyến bề mặt của huyệt
    const po = this.pointObjects.find(p => p.code === code);
    let viewDir;
    if (po && po.normal) {
      viewDir = po.normal.clone().normalize();
    } else {
      viewDir = new THREE.Vector3().subVectors(this.camera.position, targetWorldPos).normalize();
    }

    const newCamPos = targetWorldPos.clone().add(viewDir.multiplyScalar(0.28));
    this.smoothMoveCamera(newCamPos, targetWorldPos);

    if (triggerCallback && this.onPointClick) {
      this.onPointClick(point);
    }
  }

  smoothMoveCamera(targetPos, targetLookAt) {
    this.targetCameraPos = targetPos;
    this.targetLookAt = targetLookAt;
    this.isTransitioning = true;
  }

  /**
   * Focus Camera vào từng Phân Khu Giải Phẫu cụ thể
   */
  focusRegion(regionKey) {
    this.activeRegion = regionKey;

    const regionPresets = {
      all: {
        cam: new THREE.Vector3(0, 1.2, 2.5),
        target: new THREE.Vector3(0, 0.95, 0)
      },
      head: {
        cam: new THREE.Vector3(0, 1.68, 0.65),
        target: new THREE.Vector3(0, 1.62, 0)
      },
      chest: {
        cam: new THREE.Vector3(0, 1.28, 0.8),
        target: new THREE.Vector3(0, 1.22, 0)
      },
      back: {
        cam: new THREE.Vector3(0, 1.28, -0.85),
        target: new THREE.Vector3(0, 1.22, 0)
      },
      arms: {
        cam: new THREE.Vector3(0.55, 1.08, 0.65),
        target: new THREE.Vector3(0.38, 0.96, 0)
      },
      legs: {
        cam: new THREE.Vector3(0, 0.48, 0.95),
        target: new THREE.Vector3(0, 0.42, 0)
      }
    };

    const preset = regionPresets[regionKey] || regionPresets.all;
    this.smoothMoveCamera(preset.cam, preset.target);
  }

  /**
   * Tạo 3D Billboard Sprite Canvas Label cho Huyệt
   */
  createPointLabelSprite(pt, pos) {
    const canvas = document.createElement('canvas');
    canvas.width = 256;
    canvas.height = 64;
    const ctx = canvas.getContext('2d');

    this.renderLabelCanvas(ctx, canvas, pt);

    const texture = new THREE.CanvasTexture(canvas);
    texture.minFilter = THREE.LinearFilter;

    const spriteMat = new THREE.SpriteMaterial({
      map: texture,
      transparent: true,
      opacity: 0.95,
      depthTest: false
    });

    const sprite = new THREE.Sprite(spriteMat);
    sprite.renderOrder = 999;
    const offsetX = pos.x < 0 ? -0.016 : 0.016;
    sprite.position.set(pos.x + offsetX, pos.y + 0.006, pos.z + 0.005);
    sprite.scale.set(0.05, 0.0125, 1);
    sprite.userData = { code: pt.code, point: pt };
    sprite.visible = this.showLabels;

    return { sprite, canvas, ctx, texture };
  }

  renderLabelCanvas(ctx, canvas, pt) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    let text = `${pt.code} ${pt.name_vi}`;
    if (this.labelDisplayMode === 'vi_only') {
      text = pt.name_vi;
    } else if (this.labelDisplayMode === 'code_only') {
      text = pt.code;
    }

    ctx.font = '700 24px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    // Viền đen tương phản cao ôm sát chữ
    ctx.strokeStyle = 'rgba(10, 15, 25, 0.92)';
    ctx.lineWidth = 5;
    ctx.lineJoin = 'round';
    ctx.miterLimit = 2;
    ctx.strokeText(text, canvas.width / 2, canvas.height / 2);

    // Chữ trắng sáng
    ctx.fillStyle = '#ffffff';
    ctx.fillText(text, canvas.width / 2, canvas.height / 2);
  }

  toggleLabels(visible) {
    this.showLabels = visible;
    this.labelGroup.visible = visible;
  }

  cycleLabelMode() {
    if (this.labelDisplayMode === 'code_name') {
      this.labelDisplayMode = 'vi_only';
    } else if (this.labelDisplayMode === 'vi_only') {
      this.labelDisplayMode = 'code_only';
    } else {
      this.labelDisplayMode = 'code_name';
    }

    // Vẽ lại toàn bộ texture nhãn
    this.pointObjects.forEach(po => {
      if (po.labelInfo) {
        this.renderLabelCanvas(po.labelInfo.ctx, po.labelInfo.canvas, po.pointData);
        po.labelInfo.texture.needsUpdate = true;
      }
    });

    return this.labelDisplayMode;
  }

  /**
   * Khởi tạo 419 Huyệt Vị lên mô hình 3D kèm Pháp Tuyến Bề Mặt (Surface Normal)
   */
  setAcupoints(points) {
    this.acupoints = points;

    // Dọn dẹp cũ
    while (this.acupointGroup.children.length > 0) {
      const obj = this.acupointGroup.children[0];
      this.acupointGroup.remove(obj);
      if (obj.geometry) obj.geometry.dispose();
      if (obj.material) obj.material.dispose();
    }
    while (this.labelGroup.children.length > 0) {
      const obj = this.labelGroup.children[0];
      this.labelGroup.remove(obj);
      if (obj.material) obj.material.dispose();
    }

    this.acupointMeshes.clear();
    this.pointObjects = [];

    const sphereGeo = new THREE.SphereGeometry(0.0042, 16, 16);

    const channelColors = {
      LU: 0xe6e6fa, LI: 0xffffff, ST: 0xffcc00, SP: 0xffd700,
      HT: 0xff3333, SI: 0xff4500, BL: 0x1e90ff, KI: 0x00bfff,
      PC: 0xff1493, TE: 0xff6347, GB: 0x32cd32, LR: 0x00ff7f,
      CV: 0x00ffff, GV: 0xffa500, EXTRA: 0xdc73ff
    };

    points.forEach((pt) => {
      let chId = pt.channel_id || 'EXTRA';
      if (!channelColors[chId]) chId = 'EXTRA';
      const colorHex = channelColors[chId];

      const mat = new THREE.MeshBasicMaterial({
        color: colorHex,
        depthTest: true,
        depthWrite: true
      });

      const pos = new THREE.Vector3(pt.position.x, pt.position.y, pt.position.z);
      const mesh = new THREE.Mesh(sphereGeo, mat);
      mesh.position.copy(pos);
      mesh.userData = {
        point: pt,
        defaultColor: colorHex
      };

      this.acupointGroup.add(mesh);
      this.acupointMeshes.set(pt.code, mesh);

      // Tính vector pháp tuyến bề mặt (Normal):
      // Vector chỉ từ trục thân mình (0, y, 0) ra phía ngoài điểm huyệt
      let normal = new THREE.Vector3(pos.x, 0.02, pos.z).normalize();
      // Nếu là Nhâm Mạch (CV) hoặc ngực bụng: hướng thẳng +Z
      if (chId === 'CV' || (Math.abs(pos.x) < 0.05 && pos.z > 0.02)) {
        normal.set(0, 0, 1);
      }
      // Nếu là Đốc Mạch (GV) hoặc lưng gáy: hướng thẳng -Z
      else if (chId === 'GV' || (Math.abs(pos.x) < 0.05 && pos.z < -0.02)) {
        normal.set(0, 0, -1);
      }

      // Tạo nhãn 3D Billboard Sprite
      const labelInfo = this.createPointLabelSprite(pt, pos);
      this.labelGroup.add(labelInfo.sprite);

      this.pointObjects.push({
        code: pt.code,
        mesh,
        labelSprite: labelInfo.sprite,
        labelInfo,
        pointData: pt,
        worldPos: pos,
        normal,
        filterVisible: true
      });
    });

    console.log(`[ThreeViewer] Đã hiển thị hoàn chỉnh ${this.pointObjects.length} huyệt vị kèm nhãn và pháp tuyến bề mặt.`);
  }

  /**
   * CƠ CHẾ TỰ ĐỘNG ẨN CÁC HUYỆT Ở PHÍA SAU (Backface / Occlusion Culling)
   * Chạy liên tục trong vòng lặp render
   */
  updateOcclusion() {
    if (!this.camera || this.pointObjects.length === 0) return;

    const camPos = this.camera.position;
    const viewVector = new THREE.Vector3();

    for (let i = 0; i < this.pointObjects.length; i++) {
      const po = this.pointObjects[i];

      // Nếu huyệt bị ẩn bởi bộ lọc tìm kiếm/kênh -> giữ ẩn
      if (!po.filterVisible) {
        po.mesh.visible = false;
        if (po.labelSprite) po.labelSprite.visible = false;
        continue;
      }

      // Tính vector từ huyệt tới camera
      viewVector.subVectors(camPos, po.worldPos).normalize();

      // Tính tích vô hướng giữa Normal bề mặt và hướng nhìn Camera
      const dot = po.normal.dot(viewVector);

      // Nếu dot < 0.04: Bề mặt huyệt đang quay lưng lại với mắt nhìn của Camera -> ẨN!
      const isFacingCamera = dot >= 0.04;

      po.mesh.visible = isFacingCamera;
      if (po.labelSprite) {
        po.labelSprite.visible = isFacingCamera && this.showLabels;
      }
    }
  }

  /**
   * Khởi tạo 14 Đường Kinh Lạc dạng Tube Neon uốn lượn
   */
  setMeridians(meridiansData) {
    this.meridians = meridiansData;

    while (this.meridianGroup.children.length > 0) {
      const obj = this.meridianGroup.children[0];
      this.meridianGroup.remove(obj);
      if (obj.geometry) obj.geometry.dispose();
      if (obj.material) obj.material.dispose();
    }

    const channelColorMap = {
      LU: 0xe6e6fa, LI: 0xffffff, ST: 0xffcc00, SP: 0xffd700,
      HT: 0xff3333, SI: 0xff4500, BL: 0x1e90ff, KI: 0x00bfff,
      PC: 0xff1493, TE: 0xff6347, GB: 0x32cd32, LR: 0x00ff7f,
      CV: 0x00ffff, GV: 0xffa500
    };

    meridiansData.forEach((meridian) => {
      const chCode = meridian.code;
      const ptsForChannel = this.acupoints.filter(p => p.channel_id === chCode);

      if (ptsForChannel.length < 2) return;

      const vectors = ptsForChannel.map(p => new THREE.Vector3(p.position.x, p.position.y, p.position.z));
      const curve = new THREE.CatmullRomCurve3(vectors, false, 'catmullrom', 0.2);

      const tubeGeo = new THREE.TubeGeometry(curve, vectors.length * 8, 0.0016, 8, false);
      const tubeMat = new THREE.MeshBasicMaterial({
        color: channelColorMap[chCode] || 0x00ffcc,
        transparent: true,
        opacity: 0.85
      });

      const tubeMesh = new THREE.Mesh(tubeGeo, tubeMat);
      tubeMesh.userData = { channelCode: chCode };
      this.meridianGroup.add(tubeMesh);
    });
  }

  /**
   * Làm nổi bật (Highlight) một đường kinh cụ thể (dùng cho Tý Ngọ Lưu Chú)
   */
  highlightMeridian(channelCode) {
    this.meridianGroup.children.forEach(tube => {
      if (tube.userData.channelCode === channelCode) {
        tube.material.opacity = 1.0;
        tube.scale.set(1.4, 1.4, 1.4);
      } else {
        tube.material.opacity = 0.2;
        tube.scale.set(1.0, 1.0, 1.0);
      }
    });

    // Lọc làm nổi bật các huyệt thuộc kinh đó
    const channelPts = this.acupoints.filter(p => p.channel_id === channelCode);
    if (channelPts.length > 0) {
      const midPt = channelPts[Math.floor(channelPts.length / 2)];
      this.selectAcupoint(midPt.code, false);
    }
  }

  resetMeridianHighlight() {
    this.meridianGroup.children.forEach(tube => {
      tube.material.opacity = 0.85;
      tube.scale.set(1.0, 1.0, 1.0);
    });
  }

  /**
   * Nạp một hệ giải phẫu (GLB) vào Scene
   */
  async loadSystemModel(systemId, arrayBuffer) {
    return new Promise((resolve, reject) => {
      this.loader.parse(
        arrayBuffer,
        '',
        (gltf) => {
          const model = gltf.scene;
          model.name = `system_${systemId}`;

          model.traverse((child) => {
            if (child.isMesh) {
              child.castShadow = false;
              child.receiveShadow = false;

              if (systemId === 'skeleton') {
                child.material = new THREE.MeshStandardMaterial({
                  color: 0xe5dfcf,
                  roughness: 0.55,
                  metalness: 0.05
                });
              } else if (systemId === 'muscles') {
                child.material = new THREE.MeshStandardMaterial({
                  color: 0x9b3838,
                  roughness: 0.65,
                  metalness: 0.02
                });
              } else if (systemId === 'skin' || systemId === 'human-learning') {
                child.material = new THREE.MeshPhysicalMaterial({
                  color: 0xc8d8e8,
                  transmission: 0.6,
                  opacity: 0.45,
                  transparent: true,
                  roughness: 0.2,
                  metalness: 0.1
                });
              } else if (systemId === 'nerves') {
                child.material = new THREE.MeshStandardMaterial({
                  color: 0xffea00,
                  roughness: 0.4,
                  emissive: 0x332b00
                });
              } else if (systemId === 'organs') {
                child.material = this.getOrganMaterial(child.name);
              } else if (systemId === 'vessels') {
                child.material = new THREE.MeshStandardMaterial({
                  color: 0xcc2222,
                  roughness: 0.3
                });
              } else if (systemId === 'lymphatic') {
                child.material = new THREE.MeshStandardMaterial({
                  color: 0x55cc55,
                  roughness: 0.4
                });
              }
            }
          });

          // Bổ sung Niệu Quản & Tuyến Tụy nếu chưa có trong mô hình
          if (systemId === 'organs') {
            this.addUretersAndPancreas(model);
          }

          if (systemId === 'skeleton') {
            model.scale.setScalar(0.4262312);
            model.position.y = 0.87504;
          } else if (systemId === 'muscles') {
            model.scale.setScalar(0.2657077);
            model.position.y = 0.87503;
          }

          if (this.loadedSystems.has(systemId)) {
            this.anatomyGroup.remove(this.loadedSystems.get(systemId));
          }

          this.anatomyGroup.add(model);
          this.loadedSystems.set(systemId, model);
          console.log(`[ThreeViewer] Nạp thành công hệ giải phẫu: ${systemId}`);
          resolve(model);
        },
        (error) => {
          console.error(`[ThreeViewer] Lỗi parse GLTF hệ ${systemId}:`, error);
          reject(error);
        }
      );
    });
  }

  setSystemVisibility(systemId, visible) {
    if (this.loadedSystems.has(systemId)) {
      this.loadedSystems.get(systemId).visible = visible;
    }
  }

  setSystemOpacity(systemId, opacity) {
    if (this.loadedSystems.has(systemId)) {
      const obj = this.loadedSystems.get(systemId);
      obj.traverse((child) => {
        if (child.isMesh && child.material) {
          child.material.transparent = opacity < 0.99;
          child.material.opacity = opacity;
        }
      });
    }
  }

  getOrganMaterial(nodeName) {
    const n = (nodeName || '').toLowerCase();

    // 1. Tim (Heart)
    if (n.includes('heart') || n.includes('card')) {
      return new THREE.MeshStandardMaterial({
        color: 0xc82333,
        roughness: 0.35,
        metalness: 0.05
      });
    }
    // 2. Phổi (Lungs)
    if (n.includes('lung') || n.includes('pulmo')) {
      return new THREE.MeshStandardMaterial({
        color: 0xf4978e,
        roughness: 0.65,
        metalness: 0.02
      });
    }
    // 3. Gan (Liver)
    if (n.includes('liver') || n.includes('hepa')) {
      return new THREE.MeshStandardMaterial({
        color: 0x78281f,
        roughness: 0.45,
        metalness: 0.05
      });
    }
    // 4. Túi Mật (Gallbladder)
    if (n.includes('gallbladder') || n.includes('cholecyst')) {
      return new THREE.MeshStandardMaterial({
        color: 0x4d7c0f,
        roughness: 0.25,
        metalness: 0.1
      });
    }
    // 5. Dạ Dày (Stomach)
    if (n.includes('stomach') || n.includes('gastr')) {
      return new THREE.MeshStandardMaterial({
        color: 0xd97706,
        roughness: 0.5,
        metalness: 0.03
      });
    }
    // 6. Lách (Spleen)
    if (n.includes('spleen') || n.includes('lien')) {
      return new THREE.MeshStandardMaterial({
        color: 0x701a75,
        roughness: 0.4,
        metalness: 0.08
      });
    }
    // 7. Thận (Kidneys)
    if (n.includes('kidney') || n.includes('ren')) {
      return new THREE.MeshStandardMaterial({
        color: 0x9a3412,
        roughness: 0.35,
        metalness: 0.05
      });
    }
    // 8. Bàng Quang (Urinary Bladder)
    if (n.includes('bladder') || n.includes('vesic')) {
      return new THREE.MeshStandardMaterial({
        color: 0xf97316,
        roughness: 0.4,
        metalness: 0.04
      });
    }
    // 9. Ruột Non (Small Intestine: Duodenum, Jejunum, Ileum)
    if (n.includes('small_intestine') || n.includes('duoden') || n.includes('jejun') || n.includes('ileum')) {
      return new THREE.MeshStandardMaterial({
        color: 0xfca5a5,
        roughness: 0.55,
        metalness: 0.02
      });
    }
    // 10. Đại Tràng / Ruột Già (Colon / Large Intestine)
    if (n.includes('colon') || n.includes('large_intestine') || n.includes('caecum') || n.includes('rectum')) {
      return new THREE.MeshStandardMaterial({
        color: 0xa8715a,
        roughness: 0.6,
        metalness: 0.02
      });
    }
    // 11. Tụy (Pancreas)
    if (n.includes('pancrea')) {
      return new THREE.MeshStandardMaterial({
        color: 0xfacc15,
        roughness: 0.5,
        metalness: 0.05
      });
    }
    // 12. Niệu Quản (Ureter)
    if (n.includes('ureter')) {
      return new THREE.MeshStandardMaterial({
        color: 0xfef08a,
        roughness: 0.3,
        metalness: 0.05
      });
    }

    return new THREE.MeshStandardMaterial({
      color: 0xb55353,
      roughness: 0.5
    });
  }

  /**
   * Bổ sung 2 Ống Niệu Quản 3D nối từ Thận xuống Bàng Quang và Tuyến Tụy
   */
  addUretersAndPancreas(organGroup) {
    // 1. Niệu Quản Phải (Right Ureter)
    const rightPoints = [
      new THREE.Vector3(-0.062, 1.11, -0.040),
      new THREE.Vector3(-0.054, 1.05, -0.028),
      new THREE.Vector3(-0.044, 0.98, -0.018),
      new THREE.Vector3(-0.032, 0.92, -0.012),
      new THREE.Vector3(-0.018, 0.875, -0.008)
    ];
    const curveR = new THREE.CatmullRomCurve3(rightPoints);
    const geomR = new THREE.TubeGeometry(curveR, 40, 0.0032, 12, false);
    const matUreter = new THREE.MeshStandardMaterial({
      color: 0xfef08a, // Màu vàng ngà niệu quản
      roughness: 0.35,
      metalness: 0.05
    });
    const ureterR = new THREE.Mesh(geomR, matUreter);
    ureterR.name = 'organ_ureter_right';
    organGroup.add(ureterR);

    // 2. Niệu Quản Trái (Left Ureter)
    const leftPoints = [
      new THREE.Vector3(0.055, 1.12, -0.040),
      new THREE.Vector3(0.048, 1.06, -0.028),
      new THREE.Vector3(0.040, 0.99, -0.018),
      new THREE.Vector3(0.030, 0.93, -0.012),
      new THREE.Vector3(0.018, 0.875, -0.008)
    ];
    const curveL = new THREE.CatmullRomCurve3(leftPoints);
    const geomL = new THREE.TubeGeometry(curveL, 40, 0.0032, 12, false);
    const ureterL = new THREE.Mesh(geomL, matUreter.clone());
    ureterL.name = 'organ_ureter_left';
    organGroup.add(ureterL);

    // 3. Tuyến Tụy (Pancreas) - nằm ngang dưới dạ dày, đầu tụy ôm trong khung tá tràng
    const pancreasPoints = [
      new THREE.Vector3(-0.028, 1.155, 0.020), // Đầu tụy (Head)
      new THREE.Vector3(0.000, 1.165, 0.010),  // Cổ & Thân tụy (Body)
      new THREE.Vector3(0.035, 1.175, 0.000),
      new THREE.Vector3(0.065, 1.190, -0.012)  // Đuôi tụy chạm rốn lách (Tail)
    ];
    const curvePancreas = new THREE.CatmullRomCurve3(pancreasPoints);
    const geomPancreas = new THREE.TubeGeometry(curvePancreas, 32, 0.0095, 16, false);
    const matPancreas = new THREE.MeshStandardMaterial({
      color: 0xfacc15, // Màu vàng tươi tạng Tụy
      roughness: 0.5,
      metalness: 0.05
    });
    const pancreasMesh = new THREE.Mesh(geomPancreas, matPancreas);
    pancreasMesh.name = 'organ_pancreas';
    organGroup.add(pancreasMesh);

    console.log('[ThreeViewer] Đã bổ sung thành công 2 ống Niệu Quản (Ureters) & Tuyến Tụy (Pancreas).');
  }

  filterAcupoints(filterFn) {
    this.pointObjects.forEach(po => {
      const isVisible = filterFn(po.pointData);
      po.filterVisible = isVisible;
    });
  }

  resetCamera() {
    this.focusRegion('all');
  }

  animate() {
    requestAnimationFrame(() => this.animate());

    // Cập nhật ẩn các huyệt và nhãn ở mặt sau cơ thể
    this.updateOcclusion();

    // Di chuyển mượt mà tới mục tiêu
    if (this.isTransitioning && this.targetCameraPos && this.targetLookAt) {
      this.camera.position.lerp(this.targetCameraPos, 0.08);
      this.controls.target.lerp(this.targetLookAt, 0.08);

      if (
        this.camera.position.distanceTo(this.targetCameraPos) < 0.005 &&
        this.controls.target.distanceTo(this.targetLookAt) < 0.005
      ) {
        this.camera.position.copy(this.targetCameraPos);
        this.controls.target.copy(this.targetLookAt);
        this.isTransitioning = false;
      }
    }

    this.controls.update();
    this.renderer.render(this.scene, this.camera);
  }
}
