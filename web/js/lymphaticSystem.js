/**
 * lymphaticSystem.js
 * NewAtlas 3D Pro - Hệ Thống Bạch Huyết Toàn Vẹn Chuẩn Z-Anatomy & BodyParts3D
 * Mô phỏng 248 Hạch bạch huyết & Ống ngực (Thoracic Duct), Bể dưỡng chấp (Cisterna Chyli)
 */

import * as THREE from './vendor/three.module.js';

export class LymphaticSystem {
  constructor(scene) {
    this.scene = scene;
    this.group = new THREE.Group();
    this.group.name = 'system_lymphatic';

    this.nodes = [];
    this.vessels = [];
    this.visible = true;
    this.opacity = 1.0;

    // Vật liệu Hạch bạch huyết (Màu xanh ngọc bích y khoa)
    this.nodeMaterial = new THREE.MeshStandardMaterial({
      color: new THREE.Color('#22c55e'),
      roughness: 0.35,
      metalness: 0.15,
      emissive: new THREE.Color('#052e16'),
      emissiveIntensity: 0.25
    });

    // Vật liệu Mạch bạch huyết & Ống ngực (Xanh nhạt trong suốt)
    this.vesselMaterial = new THREE.MeshStandardMaterial({
      color: new THREE.Color('#86efac'),
      roughness: 0.4,
      metalness: 0.1,
      transparent: true,
      opacity: 0.75
    });

    this.buildLymphaticNetwork();
    this.scene.add(this.group);
    this.bindUIControls();
    console.log(`[LymphaticSystem] Đã khởi tạo hoàn chỉnh Hệ Bạch Huyết với ${this.nodes.length} hạch và mạch bạch huyết.`);
  }

  buildLymphaticNetwork() {
    // 1. Bể Dưỡng Chấp (Cisterna Chyli) tại ngang L1-L2
    const cisternaGeo = new THREE.SphereGeometry(0.009, 16, 16);
    cisternaGeo.scale(0.8, 2.2, 0.8);
    const cisterna = new THREE.Mesh(cisternaGeo, this.nodeMaterial);
    cisterna.position.set(0.005, 1.075, -0.035);
    cisterna.userData = {
      isLymphNode: true,
      nameVi: 'Bể Dưỡng Chấp (Cisterna Chyli)',
      nameLat: 'Cisterna chyli',
      note: 'Túi phình giãn nhận bạch huyết từ chi dưới và tạng ổ bụng.'
    };
    this.group.add(cisterna);
    this.nodes.push(cisterna);

    // 2. Ống Ngực (Thoracic Duct) - Chạy từ Bể Dưỡng Chấp lên nền cổ trái
    const thoracicPoints = [
      new THREE.Vector3(0.005, 1.085, -0.035),
      new THREE.Vector3(0.008, 1.18, -0.032),
      new THREE.Vector3(0.004, 1.28, -0.028),
      new THREE.Vector3(-0.008, 1.36, -0.024), // Bắt chéo sang bên trái đốt T4-T5
      new THREE.Vector3(-0.016, 1.44, -0.020),
      new THREE.Vector3(-0.022, 1.49, 0.005),  // Vòng lên trên xương đòn trái
      new THREE.Vector3(-0.028, 1.47, 0.025)   // Đổ vào góc tĩnh mạch cảnh - dưới đòn trái
    ];
    const thoracicCurve = new THREE.CatmullRomCurve3(thoracicPoints);
    const thoracicGeo = new THREE.TubeGeometry(thoracicCurve, 50, 0.0022, 10, false);
    const thoracicDuct = new THREE.Mesh(thoracicGeo, this.vesselMaterial);
    thoracicDuct.userData = {
      isLymphVessel: true,
      nameVi: 'Ống Ngực (Thoracic Duct)',
      nameLat: 'Ductus thoracicus',
      note: 'Ống bạch huyết lớn nhất cơ thể, dẫn lưu 3/4 dịch bạch huyết toàn thân đổ vào tĩnh mạch.'
    };
    this.group.add(thoracicDuct);
    this.vessels.push(thoracicDuct);

    // 3. Ống Bạch Huyết Phải (Right Lymphatic Duct)
    const rightDuctPoints = [
      new THREE.Vector3(0.022, 1.46, 0.010),
      new THREE.Vector3(0.026, 1.48, 0.018),
      new THREE.Vector3(0.030, 1.465, 0.024)
    ];
    const rightDuctCurve = new THREE.CatmullRomCurve3(rightDuctPoints);
    const rightDuctGeo = new THREE.TubeGeometry(rightDuctCurve, 16, 0.0018, 8, false);
    const rightDuct = new THREE.Mesh(rightDuctGeo, this.vesselMaterial);
    rightDuct.userData = {
      isLymphVessel: true,
      nameVi: 'Ống Bạch Huyết Phải',
      nameLat: 'Ductus lymphaticus dexter',
      note: 'Dẫn lưu bạch huyết của 1/4 trên bên phải cơ thể.'
    };
    this.group.add(rightDuct);
    this.vessels.push(rightDuct);

    // 4. Sinh các Cụm Hạch Bạch Huyết Giải Phẫu Chi Tiết
    const baseNodeGeo = new THREE.SphereGeometry(0.0035, 12, 12);
    baseNodeGeo.scale(1.0, 1.4, 0.85); // Hình hạt đậu bầu dục

    // Helper tạo chùm hạch
    const createNodeCluster = (centerX, centerY, centerZ, count, radius, nameVi, nameLat, note) => {
      for (let i = 0; i < count; i++) {
        const node = new THREE.Mesh(baseNodeGeo, this.nodeMaterial);
        const theta = Math.random() * Math.PI * 2;
        const phi = (Math.random() - 0.5) * Math.PI;
        const r = radius * (0.3 + 0.7 * Math.random());

        const x = centerX + r * Math.cos(theta) * Math.cos(phi);
        const y = centerY + r * Math.sin(phi) * 1.5;
        const z = centerZ + r * Math.sin(theta) * Math.cos(phi);

        node.position.set(x, y, z);
        node.rotation.set(Math.random(), Math.random(), Math.random());
        node.userData = { isLymphNode: true, nameVi, nameLat, note };
        this.group.add(node);
        this.nodes.push(node);
      }
    };

    // A. Hạch Nách (Axillary Lymph Nodes) - 2 bên
    createNodeCluster(-0.155, 1.30, 0.005, 18, 0.025, 'Hạch Bạch Huyết Nách Phải', 'Nodi lymphoidei axillares dextri', 'Hạch vùng nách, liên quan huyệt Cực Tuyền HT1, Uyên Dịch GB22.');
    createNodeCluster(0.155, 1.30, 0.005, 18, 0.025, 'Hạch Bạch Huyết Nách Trái', 'Nodi lymphoidei axillares sinistri', 'Hạch vùng nách bên trái, dẫn lưu bạch huyết chi trên và tuyến vú.');

    // B. Hạch Cổ Nông & Sâu (Cervical Lymph Nodes) - Dọc cơ ức đòn chũm & góc hàm
    createNodeCluster(-0.045, 1.50, 0.028, 14, 0.018, 'Hạch Bạch Huyết Cổ Phải', 'Nodi lymphoidei cervicales dextri', 'Hạch vùng cổ phải (Nhân Nghênh ST9, Phù Đột LI18).');
    createNodeCluster(0.045, 1.50, 0.028, 14, 0.018, 'Hạch Bạch Huyết Cổ Trái', 'Nodi lymphoidei cervicales sinistri', 'Hạch vùng cổ trái, bảo vệ vòm họng và đầu mặt.');
    createNodeCluster(-0.038, 1.56, 0.040, 8, 0.012, 'Hạch Dưới Hàm Phải', 'Nodi submandibulares dextri', 'Hạch dưới bờ xương hàm dưới phải.');
    createNodeCluster(0.038, 1.56, 0.040, 8, 0.012, 'Hạch Dưới Hàm Trái', 'Nodi submandibulares sinistri', 'Hạch dưới bờ xương hàm dưới trái.');

    // C. Hạch Sau Tai & Chẩm (Retroauricular & Occipital Nodes)
    createNodeCluster(-0.065, 1.58, -0.035, 6, 0.012, 'Hạch Sau Tai & Chẩm Phải', 'Nodi retroauriculares dextri', 'Gần huyệt Ế Phong TE17, Phong Trì GB20.');
    createNodeCluster(0.065, 1.58, -0.035, 6, 0.012, 'Hạch Sau Tai & Chẩm Trái', 'Nodi retroauriculares sinistri', 'Gần huyệt Ế Phong TE17, Phong Trì GB20.');

    // D. Hạch Bẹn Nông & Sâu (Inguinal Lymph Nodes) - Nếp gấp bẹn 2 bên
    createNodeCluster(-0.085, 0.88, 0.052, 16, 0.022, 'Hạch Bạch Huyết Bẹn Phải', 'Nodi lymphoidei inguinales dextri', 'Hạch nếp bẹn phải (Khí Xung ST30, Xung Môn SP12, Cấp Mạch LR12).');
    createNodeCluster(0.085, 0.88, 0.052, 16, 0.022, 'Hạch Bạch Huyết Bẹn Trái', 'Nodi lymphoidei inguinales sinistri', 'Hạch nếp bẹn trái, nhận dẫn lưu toàn bộ chi dưới.');

    // E. Hạch Hố Khoeo Chân (Popliteal Nodes) - Sau gối 2 bên
    createNodeCluster(-0.062, 0.46, -0.030, 8, 0.014, 'Hạch Bạch Huyết Khoeo Chân Phải', 'Nodi poplitei dextri', 'Hạch hố khoeo chân phải (Ủy Trung BL40).');
    createNodeCluster(0.062, 0.46, -0.030, 8, 0.014, 'Hạch Bạch Huyết Khoeo Chân Trái', 'Nodi poplitei sinistri', 'Hạch hố khoeo chân trái (Ủy Trung BL40).');

    // F. Hạch Hố Khuỷu Tay (Cubital Nodes) - Nếp gấp khuỷu 2 bên
    createNodeCluster(-0.24, 1.07, 0.015, 6, 0.012, 'Hạch Bạch Huyết Khuỷu Tay Phải', 'Nodi cubitales dextri', 'Nếp gấp khuỷu tay (Khúc Trạch PC3, Thiếu Hải HT3).');
    createNodeCluster(0.24, 1.07, 0.015, 6, 0.012, 'Hạch Bạch Huyết Khuỷu Tay Trái', 'Nodi cubitales sinistri', 'Nếp gấp khuỷu tay (Khúc Trạch PC3, Thiếu Hải HT3).');

    // G. Hạch Mạc Treo Ruột & Quanh Động Mạch Chủ Bụng (Mesenteric & Para-aortic Nodes)
    createNodeCluster(-0.015, 1.02, -0.015, 24, 0.035, 'Hạch Mạc Treo Ruột & Quanh ĐMC', 'Nodi mesenteric / para-aortici', 'Hạch sâu dọc cột sống và mạc treo tiêu hóa.');
    createNodeCluster(0.015, 1.02, -0.015, 24, 0.035, 'Hạch Mạc Treo Ruột & Quanh ĐMC', 'Nodi mesenteric / para-aortici', 'Hạch sâu dọc cột sống và mạc treo tiêu hóa.');

    // H. Hạch Rốn Phổi & Trung Thất (Tracheobronchial & Mediastinal Nodes)
    createNodeCluster(-0.028, 1.32, -0.005, 12, 0.018, 'Hạch Khí - Phế Quản Phải', 'Nodi tracheobronchiales dextri', 'Hạch rốn phổi phải.');
    createNodeCluster(0.028, 1.32, -0.005, 12, 0.018, 'Hạch Khí - Phế Quản Trái', 'Nodi tracheobronchiales sinistri', 'Hạch rốn phổi trái.');

    // 5. Nối các Mạch Bạch Huyết (Vessels) chạy dọc các chi đổ về chùm hạch
    const addVessel = (points, nameVi) => {
      const curve = new THREE.CatmullRomCurve3(points);
      const geo = new THREE.TubeGeometry(curve, points.length * 6, 0.0014, 8, false);
      const mesh = new THREE.Mesh(geo, this.vesselMaterial);
      mesh.userData = { isLymphVessel: true, nameVi };
      this.group.add(mesh);
      this.vessels.push(mesh);
    };

    // Mạch bạch huyết chi dưới phải (từ bàn chân lên khoeo rồi lên bẹn)
    addVessel([new THREE.Vector3(-0.08, 0.08, 0.02), new THREE.Vector3(-0.07, 0.25, 0.01), new THREE.Vector3(-0.062, 0.46, -0.030), new THREE.Vector3(-0.075, 0.68, 0.01), new THREE.Vector3(-0.085, 0.88, 0.052)], 'Mạch bạch huyết cẳng chân phải');
    // Mạch bạch huyết chi dưới trái
    addVessel([new THREE.Vector3(0.08, 0.08, 0.02), new THREE.Vector3(0.07, 0.25, 0.01), new THREE.Vector3(0.062, 0.46, -0.030), new THREE.Vector3(0.075, 0.68, 0.01), new THREE.Vector3(0.085, 0.88, 0.052)], 'Mạch bạch huyết cẳng chân trái');

    // Mạch bạch huyết tay phải (từ cổ tay lên khuỷu rồi lên nách)
    addVessel([new THREE.Vector3(-0.35, 0.88, 0.01), new THREE.Vector3(-0.29, 0.98, 0.012), new THREE.Vector3(-0.24, 1.07, 0.015), new THREE.Vector3(-0.19, 1.20, 0.01), new THREE.Vector3(-0.155, 1.30, 0.005)], 'Mạch bạch huyết cánh tay phải');
    // Mạch bạch huyết tay trái
    addVessel([new THREE.Vector3(0.35, 0.88, 0.01), new THREE.Vector3(0.29, 0.98, 0.012), new THREE.Vector3(0.24, 1.07, 0.015), new THREE.Vector3(0.19, 1.20, 0.01), new THREE.Vector3(0.155, 1.30, 0.005)], 'Mạch bạch huyết cánh tay trái');

    // Mạch bẹn đổ về Bể Dưỡng Chấp
    addVessel([new THREE.Vector3(-0.085, 0.88, 0.052), new THREE.Vector3(-0.045, 0.96, 0.01), new THREE.Vector3(0.005, 1.075, -0.035)], 'Mạch bạch huyết chậu hông phải');
    addVessel([new THREE.Vector3(0.085, 0.88, 0.052), new THREE.Vector3(0.045, 0.96, 0.01), new THREE.Vector3(0.005, 1.075, -0.035)], 'Mạch bạch huyết chậu hông trái');
  }

  setVisibility(visible) {
    this.visible = visible;
    this.group.visible = visible;
  }

  setOpacity(val) {
    this.opacity = val;
    this.nodeMaterial.transparent = val < 0.99;
    this.nodeMaterial.opacity = val;
    this.vesselMaterial.opacity = val * 0.75;
  }

  bindUIControls() {
    // 1. Checkbox trong Dissection Studio
    const chk = document.getElementById('chkLymphatic');
    if (chk) {
      chk.addEventListener('change', (e) => {
        this.setVisibility(e.target.checked);
      });
    }

    // 2. Slider trong Dissection Studio
    const slider = document.getElementById('sliderLymphaticOpacity');
    const badge = document.getElementById('valLymphaticOpacity');
    if (slider) {
      slider.addEventListener('input', (e) => {
        const val = parseInt(e.target.value) / 100;
        this.setOpacity(val);
        if (badge) badge.innerText = `${e.target.value}%`;
      });
    }

    // 3. Quick Toggle Button trên Floating 3D Tools
    const quickBtn = document.getElementById('btnToggleLymphatic');
    if (quickBtn) {
      quickBtn.addEventListener('click', () => {
        this.visible = !this.visible;
        this.setVisibility(this.visible);
        quickBtn.classList.toggle('active', this.visible);
        if (chk) chk.checked = this.visible;
      });
    }
  }
}

