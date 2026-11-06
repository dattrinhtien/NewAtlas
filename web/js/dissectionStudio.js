/**
 * ACUATLAS 3D PRO - ANATOMY DISSECTION STUDIO & VIRTUAL SCALPEL
 * Hệ thống bóc tách giải phẫu đa tầng: Da, Cơ Nông, Cơ Sâu, Mạch Máu, Thần Kinh, Xương.
 * Tích hợp công cụ "Dao mổ số" (Interactive Scalpel) bóc từng bó cơ bằng click chuột.
 */

import * as THREE from 'three';
import anatomyDict from './data/anatomyDictionary.json';
import osteologyDict from './data/osteologyDictionary.json';
import organDict from './data/organDictionary.json';

export class DissectionStudio {
  constructor({ scene, camera, renderer, controls, humanModel, musclesModel, skeletonModel, nervesModel, organsModel, neurovascularSystem }) {
    this.scene = scene;
    this.camera = camera;
    this.renderer = renderer;
    this.controls = controls;
    this.humanModel = humanModel;
    this.musclesModel = musclesModel;
    this.skeletonModel = skeletonModel;
    this.nervesModel = nervesModel;
    this.organsModel = organsModel;
    this.neuro = neurovascularSystem;

    this.isOpen = false;
    this.isScalpelActive = false;
    this.isXRayActive = false;

    this.superficialMuscles = [];
    this.deepMuscles = [];
    this.allMuscles = [];
    this.bones = [];
    this.nerves = [];
    this.organs = [];
    this.vessels = [];
    this.lymphatic = [];
    this.peeledObjects = new Set();

    this.hoveredMesh = null;
    this.originalMaterials = new Map();

    this.raycaster = new THREE.Raycaster();
    this.mouse = new THREE.Vector2();
    window.dissectionStudio = this;
    window.Xe = this;

    this.selectedMesh = null;
    this.isInspectActive = true;
    this.initClassifications();
    this.createUI();
    this.bindEvents();
  }

  initClassifications() {
    if (!this.skeletonModel && (window.Ui || window.skeletonModel)) this.skeletonModel = window.Ui || window.skeletonModel;
    if (!this.musclesModel && (window.Yt || window.musclesModel)) this.musclesModel = window.Yt || window.musclesModel;
    if (!this.nervesModel && (window.wt || window.nervesModel)) this.nervesModel = window.wt || window.nervesModel;
    if (!this.organsModel && (window.Dt || window.organsModel)) this.organsModel = window.Dt || window.organsModel;

    this.allMuscles = [];
    this.superficialMuscles = [];
    this.deepMuscles = [];
    this.bones = [];
    this.nerves = [];
    this.organs = [];
    if (this.musclesModel) {
      this.musclesModel.traverse((child) => {
        if (child.isMesh) {
          // Gán vật liệu độc lập cho từng cơ để hover & bóc tách riêng biệt
          const baseMat = child.material ? child.material.clone() : new THREE.MeshStandardMaterial({
            color: new THREE.Color('#b84a39'),
            roughness: 0.65,
            metalness: 0.1
          });
          baseMat.polygonOffset = true;
          baseMat.polygonOffsetFactor = 2;
          baseMat.polygonOffsetUnits = 4;
          child.material = baseMat;
          this.originalMaterials.set(child, {
            color: baseMat.color.clone(),
            emissive: baseMat.emissive.clone(),
            opacity: baseMat.opacity,
            transparent: baseMat.transparent
          });

          const meshName = child.name || '';
          const info = anatomyDict[meshName] || {
            name_vi: meshName.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
            name_lat: meshName,
            layer: 'superficial',
            region: 'body'
          };

          const isTendon = ['epicranial-aponeurosis', 'calcaneal-tendon', 'linea-alba'].includes(meshName);

          if (isTendon) {
            baseMat.color = new THREE.Color('#e2e8f0');
            baseMat.roughness = 0.45;
            baseMat.metalness = 0.08;
          } else {
            baseMat.color = new THREE.Color('#b84a39');
            baseMat.roughness = 0.65;
            baseMat.metalness = 0.1;
          }

          child.userData = {
            isMuscle: true,
            meshName,
            nameVi: info.name_vi,
            nameLat: info.name_lat,
            layer: info.layer,
            region: info.region,
            origin: info.origin,
            insertion: info.insertion,
            action: info.action,
            innervation: info.innervation,
            acupoints: info.acupoints
          };

          this.allMuscles.push(child);
          if (info.layer === 'deep') {
            this.deepMuscles.push(child);
          } else {
            this.superficialMuscles.push(child);
          }
        }
      });
    }

    if (this.skeletonModel) {
      this.skeletonModel.traverse((child) => {
        if (child.isMesh) {
          const bMat = child.material ? child.material.clone() : new THREE.MeshStandardMaterial({
            color: new THREE.Color('#e5e0d4'),
            roughness: 0.42,
            metalness: 0.05
          });
          bMat.polygonOffset = true;
          bMat.polygonOffsetFactor = 2;
          bMat.polygonOffsetUnits = 4;
          child.material = bMat;
          this.originalMaterials.set(child, {
            color: bMat.color.clone(),
            emissive: bMat.emissive.clone(),
            opacity: bMat.opacity,
            transparent: bMat.transparent
          });

          const boneName = child.name || '';
          const bInfo = osteologyDict[boneName] || {
            name_vi: 'Xương ' + boneName.replace(/-/g, ' '),
            name_lat: boneName,
            region: 'body',
            type: 'Khung xương cơ thể',
            landmarks: 'Mốc mấu giải phẫu xương',
            note: 'Cấu trúc mốc xương Z-Anatomy.',
            acupoints: 'Mốc giải phẫu định vị huyệt vị YHCT'
          };
          child.userData = {
            isBone: true,
            meshName: boneName,
            nameVi: bInfo.name_vi,
            nameLat: bInfo.name_lat,
            region: bInfo.region || 'body',
            type: bInfo.type || 'Khung xương cơ thể',
            landmarks: bInfo.landmarks || '',
            note: bInfo.note || '',
            acupoints: bInfo.acupoints || ''
          };
          this.bones.push(child);
        }
      });
    }

    // Phân loại Hệ Thần Kinh 3D Z-Anatomy (123 nhánh)
    if (this.nervesModel) {
      const nerveDictionary = {
        'medulla_spinalis': { vi: 'Tủy sống', lat: 'Medulla spinalis', note: 'Trung tâm phản xạ & dẫn truyền thần kinh trung ương, phát xuất 31 đôi rễ gai sống.' },
        'sciatic_nerve': { vi: 'Thần kinh hông to (Thần kinh tọa)', lat: 'Nervus ischiadicus', note: 'Dây thần kinh lớn nhất cơ thể, chui dưới cơ hình lê (Hoàn Khiêu GB30, Ân Môn BL37, Ủy Trung BL40).' },
        'femoral_nerve': { vi: 'Dây thần kinh đùi', lat: 'Nervus femoralis', note: 'Chui dưới dây chằng bẹn (Khí Xung ST30, Bễ Quan ST31, Phục Thỏ ST32).' },
        'radial_nerve': { vi: 'Dây thần kinh quay', lat: 'Nervus radialis', note: 'Chạy trong rãnh thần kinh quay cánh tay xuống cẳng tay (Khúc Trì LI11, Hợp Cốc LI4).' },
        'median_nerve': { vi: 'Dây thần kinh giữa', lat: 'Nervus medianus', note: 'Đi giữa cẳng tay trước, qua ống cổ tay (Khúc Trạch PC3, Nội Quan PC6, Đại Lăng PC7, Lao Cung PC8).' },
        'ulnar_nerve': { vi: 'Dây thần kinh trụ', lat: 'Nervus ulnaris', note: 'Chạy qua rãnh ròng rọc khuỷu tay (Tiểu Hải SI8), cổ tay trụ (Thần Môn HT7) ra ngón út.' },
        'tibial_nerve': { vi: 'Dây thần kinh chày', lat: 'Nervus tibialis', note: 'Đi dọc bắp chân sau (Ủy Trung BL40, Hợp Dương BL55, Thừa Sơn BL57, Thái Khê KI3).' },
        'peroneal_deep': { vi: 'Thần kinh mác sâu', lat: 'Nervus fibularis profundus', note: 'Chạy trước cẳng chân (Túc Tam Lý ST36, Giải Khê ST41, Thái Xung LR3).' },
        'peroneal_superficial': { vi: 'Thần kinh mác nông', lat: 'Nervus fibularis superficialis', note: 'Chạy mặt ngoài cẳng chân (Quang Minh GB37, Huyền Chung GB39).' },
        'peroneal_common': { vi: 'Thần kinh mác chung', lat: 'Nervus fibularis communis', note: 'Vòng quanh chỏm xương mác tại huyệt Dương Lăng Tuyền (GB34).' },
        'cranial_V1': { vi: 'Thần kinh sọ V1 (Thần kinh mắt)', lat: 'Nervus ophthalmicus (CN V1)', note: 'Ra khuyết trên ổ mắt (Toản Trúc BL2, Ngư Yêu EX-HN4, Dương Bạch GB14).' },
        'cranial_V2': { vi: 'Thần kinh sọ V2 (Thần kinh hàm trên)', lat: 'Nervus maxillaris (CN V2)', note: 'Ra lỗ dưới ổ mắt (Tứ Bạch ST2, Cự Liêu ST3).' },
        'cranial_V3': { vi: 'Thần kinh sọ V3 (Thần kinh hàm dưới)', lat: 'Nervus mandibularis (CN V3)', note: 'Ra lỗ cằm (Thừa Tương CV24, Hạ Quan ST7, Giáp Xa ST6).' },
        'cranial_VII': { vi: 'Thần kinh mặt VII', lat: 'Nervus facialis (CN VII)', note: 'Xuất phát từ lỗ trâm chũm (Ế Phong TE17), chi phối toàn bộ cơ mặt (liệt mặt Bell\'s palsy).' }
      };

      this.nervesModel.traverse((child) => {
        if (child.isMesh) {
          const baseMat = child.material ? child.material.clone() : new THREE.MeshStandardMaterial({
            color: new THREE.Color('#facc15'),
            roughness: 0.35,
            metalness: 0.15
          });
          child.material = baseMat;
          this.originalMaterials.set(child, {
            color: baseMat.color.clone(),
            emissive: baseMat.emissive.clone(),
            opacity: baseMat.opacity,
            transparent: baseMat.transparent
          });

          const mName = child.name || '';
          const nInfo = this.getNerveInfo(mName);
          child.userData = {
            isNerve: true,
            meshName: mName,
            nameVi: nInfo.vi,
            nameLat: nInfo.lat,
            roots: nInfo.roots,
            function: nInfo.func,
            acupoints: nInfo.acupoints,
            note: nInfo.note,
            layer: 'nerve'
          };
          this.nerves.push(child);
        }
      });
    }

    // Phân loại Hệ Nội Tạng / Lục Phủ Ngũ Tạng (13 cơ quan & mạch máu - niệu quản)
    if (this.organsModel) {
      const organDictionary = {
        'organ_heart': {
          vi: 'Trái tim (Tạng Tâm)',
          lat: 'Cor / Heart',
          pos: 'Trung thất giữa lồng ngực, nghiêng trái, tựa vòm hoành, trước cột sống T5-T8, màng ngoài tim bao bọc.',
          phys: 'Bơm cơ học trung tâm tuần hoàn, co bóp đẩy máu giàu oxy qua ĐM chủ nuôi toàn thân và hút máu tĩnh mạch về phổi.',
          blood: '2 động mạch vành (ĐM vành phải & trái); Đám rối tim (giao cảm T1-T4 tăng nhịp, phó giao cảm dây X giảm nhịp).',
          yhct: 'Tâm vi Quân chủ chi quan. Chủ huyết mạch, tàng Thần, khai khiếu ra lưỡi, hoa ở mặt. Ngũ hành thuộc Hỏa, biểu lý với Tiểu Trường.',
          acupoints: 'Mộ: Cự Khuyết (CV14); Mộ Tâm Bào: Đản Trung (CV17); Du: Tâm Du (BL15); Cực Tuyền (HT1), Thần Môn (HT7).'
        },
        'organ_aorta_arch': {
          vi: 'Cung động mạch chủ',
          lat: 'Arcus aortae',
          pos: 'Nối từ ĐM chủ lên (ngang góc ức T4) uốn cong sang trái và ra sau tới bờ trái thân đốt sống T4 thành ĐM chủ ngực.',
          phys: 'Thân đại động mạch chịu áp lực tống máu cao nhất từ thất trái, phân nhánh ĐM thân cánh tay đầu, ĐM cảnh chung trái và ĐM dưới đòn trái.',
          blood: 'Cấp máu cho toàn bộ đầu, cổ, não bộ và hai chi trên.',
          yhct: 'Huyết mạch then chốt của Tâm, nguồn cội phân phối vinh huyết nuôi dưỡng toàn thân.',
          acupoints: 'Thiên Đột (CV22), Khuyết Bồn (ST12), Đản Trung (CV17).'
        },
        'organ_pulmonary_trunk': {
          vi: 'Thân động mạch phổi',
          lat: 'Truncus pulmonalis',
          pos: 'Xuất phát từ lỗ động mạch phổi của tâm thất phải, chạy chếch lên trên ra sau qua trước cung ĐM chủ rồi chia 2 nhánh ĐM phổi phải và trái.',
          phys: 'Dẫn toàn bộ dòng máu nghèo oxy (tĩnh mạch) từ tim phải lên hai lá phổi để thực hiện trao đổi khí.',
          blood: 'Áp lực tuần hoàn phổi thấp (khoảng 25/10 mmHg).',
          yhct: 'Cửa ngõ liên hoàn giữa Tâm và Phế, nơi Huyết tìm Khí để phục hồi thanh khí.',
          acupoints: 'Ưng Song (ST15), Đản Trung (CV17).'
        },
        'organ_vena_cava': {
          vi: 'Tĩnh mạch chủ trên',
          lat: 'Vena cava superior',
          pos: 'Nằm ở trung thất trước trên, hợp bởi 2 tĩnh mạch cánh tay đầu phải và trái, đổ vào phần trên tâm nhĩ phải.',
          phys: 'Thu hồi toàn bộ dòng máu tĩnh mạch từ nửa trên cơ thể (đầu, cổ, chi trên và thành ngực) đưa về tim.',
          blood: 'Áp lực tĩnh mạch trung tâm (CVP) đo lường đổ đầy tim phải.',
          yhct: 'Dòng hồi lưu huyết dịch trở về Tâm quân chủ.',
          acupoints: 'Khí Xá (ST11), Khuyết Bồn (ST12).'
        },
        'organ_trachea': {
          vi: 'Khí quản',
          lat: 'Trachea',
          pos: 'Ống dẫn khí sụn sợi dài 11-13cm, nối tiếp thanh quản từ sụn nhẫn (ngang C6) chạy xuống trung thất trên chia đôi ở chẽ khí quản (Carina, T4-T5).',
          phys: 'Đường thở chính; Cấu tạo 16-20 vòng sụn chữ C giữ đường thở thông thoáng; Lớp biểu mô trụ giả tầng có lông chuyển quét bụi nhầy lên họng.',
          blood: 'Động mạch giáp dưới và nhánh phế quản; Dây thần kinh thanh quản quặt ngược (dây X).',
          yhct: 'Cửa ngõ hô hấp thông thiên khí vào Phế tạng.',
          acupoints: 'Thiên Đột (CV22 - Huyệt quan trọng trị hen suyễn, khó thở).'
        },
        'organ_bronchus_right': {
          vi: 'Phế quản gốc phải',
          lat: 'Bronchus principalis dexter',
          pos: 'Rẽ từ chẽ khí quản đi vào rốn phổi phải; Khẩu kính lớn hơn, ngắn hơn (2.5cm) và dốc đứng hơn phế quản trái.',
          phys: 'Dẫn khí vào 3 thùy phổi phải; Do dốc đứng nên dị vật đường thở thường rơi vào phế quản phải.',
          blood: 'Động mạch phế quản phải xuất phát từ ĐM gian sườn hoặc ĐM chủ ngực.',
          yhct: 'Nhánh dẫn thông khí thanh lọc của Phế bên phải.',
          acupoints: 'Trung Phủ (LU1), Toàn Cơ (CV21).'
        },
        'organ_bronchus_left': {
          vi: 'Phế quản gốc trái',
          lat: 'Bronchus principalis sinister',
          pos: 'Dài hơn (5cm), hẹp hơn và chạy chếch ngang dưới quai động mạch chủ vào rốn phổi trái.',
          phys: 'Dẫn khí phân chia vào 2 thùy phổi trái.',
          blood: '2 động mạch phế quản trái xuất phát trực tiếp từ ĐM chủ ngực.',
          yhct: 'Nhánh dẫn thông khí của Phế bên trái.',
          acupoints: 'Trung Phủ (LU1), Hoa Cái (CV20).'
        },
        'organ_lung_right': {
          vi: 'Lá phổi phải (Hữu Phế)',
          lat: 'Pulmo dexter',
          pos: 'Chiếm nửa phải lồng ngực, gồm 3 thùy (trên, giữa, dưới) ngăn cách bởi rãnh chếch và rãnh ngang; Đáy tựa lên vòm hoành phải.',
          phys: 'Dung tích phổi phải chiếm 55% tổng dung tích phổi; Trao đổi khí O2 và CO2 qua màng phế nang - mao mạch.',
          blood: 'Tuần hoàn chức phận: ĐM phổi; Tuần hoàn dinh dưỡng: ĐM phế quản; Thần kinh: Đám rối phổi (dây X co thắt, giao cảm giãn phế quản).',
          yhct: 'Phế vi Tướng phó chi quan, chủ Khí, tư hô hấp, tuyên phát túc giáng, thông điều thủy đạo, hợp bì mao. Ngũ hành thuộc Kim, biểu lý với Đại Trường.',
          acupoints: 'Mộ: Trung Phủ (LU1); Du: Phế Du (BL13); Vân Môn (LU2), Phách Hộ (BL42).'
        },
        'organ_lung_right_upper': {
          vi: 'Phổi phải (Thùy trên)',
          lat: 'Lobus superior pulmonis dextri',
          pos: 'Chiếm phần trên phổi phải, từ đỉnh phổi đến rãnh ngang (sườn 4).',
          phys: 'Gồm 3 phân thùy (đỉnh, sau, trước); Thông khí vùng cao phổi.',
          blood: 'Nhánh thùy trên của ĐM phổi phải.',
          yhct: 'Phần tuyên phát thượng tiêu của Phế khí.',
          acupoints: 'Vân Môn (LU2), Trung Phủ (LU1).'
        },
        'organ_lung_right_middle': {
          vi: 'Phổi phải (Thùy giữa)',
          lat: 'Lobus medius pulmonis dextri',
          pos: 'Hình nêm nằm giữa rãnh ngang và rãnh chếch mặt trước phổi phải.',
          phys: 'Gồm 2 phân thùy (ngoài và trong).',
          blood: 'Nhánh thùy giữa ĐM phổi phải.',
          yhct: 'Vùng trung châu của Phế hữu.',
          acupoints: 'Khố Phòng (ST14), Chu Vinh (SP20).'
        },
        'organ_lung_right_lower': {
          vi: 'Phổi phải (Thùy dưới)',
          lat: 'Lobus inferior pulmonis dextri',
          pos: 'Thùy lớn nhất nằm sau dưới rãnh chếch, đáy tựa lên cơ hoành.',
          phys: 'Gồm 5 phân thùy đáy; Vùng trao đổi khí hiệu quả nhất do tưới máu trọng lực.',
          blood: 'Nhánh thùy dưới ĐM phổi phải.',
          yhct: 'Phần túc giáng hạ tiêu của Phế khí.',
          acupoints: 'Phế Du (BL13), Phách Hộ (BL42).'
        },
        'organ_lung_left': {
          vi: 'Lá phổi trái (Tả Phế)',
          lat: 'Pulmo sinister',
          pos: 'Nửa trái lồng ngực, gồm 2 thùy (trên và dưới) phân cách bởi rãnh chếch; Bờ trước có khuyết tim ôm trọn mỏm tim.',
          phys: 'Chiếm 45% tổng dung tích phổi; Trao đổi khí O2 và CO2.',
          blood: 'Động mạch phổi trái và 2 ĐM phế quản trái; Đám rối thần kinh phổi.',
          yhct: 'Phế chủ khí toàn thân, triều bách mạch (mọi mạch máu đều quy về Phế để nhận thanh khí).',
          acupoints: 'Mộ: Trung Phủ (LU1); Du: Phế Du (BL13); Liệt Khuyết (LU7), Thái Uyên (LU9).'
        },
        'organ_lung_left_upper': {
          vi: 'Phổi trái (Thùy trên & Khuyết tim)',
          lat: 'Lobus superior pulmonis sinistri',
          pos: 'Chiếm phần trước trên phổi trái, có lưỡi phổi (lingula) tương ứng thùy giữa bên phải.',
          phys: 'Gồm các phân thùy đỉnh - sau, trước và các phân thùy lưỡi.',
          blood: 'Các nhánh thùy trên của ĐM phổi trái.',
          yhct: 'Tuyên phát phế khí vùng ngực trái.',
          acupoints: 'Trung Phủ (LU1), Đản Trung (CV17).'
        },
        'organ_lung_left_lower': {
          vi: 'Phổi trái (Thùy dưới)',
          lat: 'Lobus inferior pulmonis sinistri',
          pos: 'Nằm sau dưới rãnh chếch, áp sát vòm hoành trái che phủ lách và dạ dày.',
          phys: 'Gồm các phân thùy đáy trao đổi khí.',
          blood: 'Nhánh thùy dưới ĐM phổi trái.',
          yhct: 'Túc giáng phế khí nạp về Thận.',
          acupoints: 'Phế Du (BL13), Cách Du (BL17).'
        },
        'organ_liver': {
          vi: 'Lá gan (Tạng Can)',
          lat: 'Hepar / Liver',
          pos: 'Tầng trên mạc treo đại tràng ngang, chiếm trọn hạ sườn phải, thượng vị và lấn sang hạ sườn trái; Áp sát dưới vòm hoành phải.',
          phys: 'Tuyến tiêu hóa lớn nhất: Chuyển hóa đường, đạm, mỡ; Khử độc thuốc và hóa chất; Dự trữ glycogen, sắt, vitamin; Tiết mật (0.8 - 1L/ngày) nhũ hóa chất béo.',
          blood: 'Nhận 75% máu từ tĩnh mạch cửa (giàu dưỡng chất hấp thu từ ruột) và 25% máu từ ĐM gan riêng; Máu ra qua 3 TM gan đổ về TM chủ dưới.',
          yhct: 'Can vi Tướng quân chi quan, mưu lự xuất yên. Can tàng Huyết, chủ sơ tiết (điều đạt khí cơ, tinh thần), chủ Cân (gân cơ), khai khiếu ra Mắt, hoa ở Móng. Ngũ hành thuộc Mộc, biểu lý với Đởm.',
          acupoints: 'Mộ: Kỳ Môn (LR14); Du: Can Du (BL18); Chương Môn (LR13 - Hội của Tạng); Thái Xung (LR3 - Huyệt Nguyên).'
        },
        'organ_gallbladder': {
          vi: 'Túi mật (Phủ Đởm)',
          lat: 'Vesica biliaris / Gallbladder',
          pos: 'Nằm trong hố túi mật ở mặt dưới của gan, hình quả lê dài 7-10cm, gồm đáy, thân và cổ tiếp nối với ống túi mật.',
          phys: 'Chứa đựng và cô đặc dịch mật gấp 5-10 lần (dung tích 30-50ml); Co bóp tống mật vào tá tràng khi có mỡ trong bữa ăn.',
          blood: 'Động mạch túi mật (nhánh từ nhánh phải ĐM gan riêng); Đám rối gan (dây X kích thích co bóp, giao cảm ức chế).',
          yhct: 'Đởm vi Trung chính chi quan, quyết đoán xuất yên. Là một trong Lục Phủ và là Phủ Kỳ Hằng (chứa dịch trong sạch thanh trấp). Chủ về sự dũng cảm, quyết đoán.',
          acupoints: 'Mộ: Nhật Nguyệt (GB24); Du: Đởm Du (BL19); Dương Lăng Tuyền (GB34 - Hội của Cân, Huyệt Hợp); Khâu Khư (GB40).'
        },
        'organ_bile_duct': {
          vi: 'Ống mật chủ',
          lat: 'Ductus choledochus',
          pos: 'Hình thành do sự hợp nhất giữa ống gan chung và ống túi mật, dài khoảng 7-8cm chạy trong cuống gan sau tá tràng.',
          phys: 'Dẫn toàn bộ dịch mật từ gan và túi mật đổ vào nhú tá lớn (Bóng Vater), có cơ vòng Oddi kiểm soát dòng chảy dịch mật vào tá tràng.',
          blood: 'Nhánh từ ĐM túi mật và ĐM vị tá tràng.',
          yhct: 'Đường dẫn truyền thanh trấp từ Đởm xuống Tiểu Trường để tiêu hóa thức ăn.',
          acupoints: 'Dương Lăng Tuyền (GB34), Nhật Nguyệt (GB24).'
        },
        'organ_stomach': {
          vi: 'Dạ dày (Phủ Vị)',
          lat: 'Gaster / Stomach',
          pos: 'Đoạn phình to nhất ống tiêu hóa, hình chữ J, chiếm vùng thượng vị, hạ sườn trái và rốn; Nối tâm vị (ngang T11) đến môn vị (ngang L1).',
          phys: 'Chứa đựng thức ăn (dung tích 1.5 - 2L); Tiết acid HCl (pH 1.5 - 2) tiêu diệt vi khuẩn, hoạt hóa men pepsin phân giải protein; Co bóp nhào trộn thành dưỡng trấp.',
          blood: 'Vòng ĐM bờ cong nhỏ (ĐM vị trái & phải) và bờ cong lớn (ĐM vị mạc nối trái & phải); Dây thần kinh X (kích thích tiết acid và nhu động).',
          yhct: 'Vị vi Thương lẫm chi quan, ngũ vị xuất yên. Chủ thu nạp và ngấu nhừ thủy cốc; Khí của Vị chủ giáng. Cùng Tỳ tạo nên Hậu thiên chi bản, nguồn cội sinh hóa khí huyết.',
          acupoints: 'Mộ: Trung Quản (CV12 - Hội của Phủ); Du: Vị Du (BL21); Lương Khâu (ST34 - Huyệt Khích); Túc Tam Lý (ST36 - Huyệt Hợp kinh Vị).'
        },
        'organ_spleen': {
          vi: 'Lách (Tạng Tỳ YHCT)',
          lat: 'Lien / Splen / Spleen',
          pos: 'Nằm sâu ở hạ sườn trái trong ô dưới hoành trái, nép sau dạ dày và trước các xương sườn 9, 10, 11 (dọc theo trục xương sườn 10).',
          phys: 'Cơ quan lympho lớn nhất: Lọc máu, bắt giữ và tiêu hủy hồng cầu già cỗi; Dự trữ tiểu cầu và bạch cầu; Đáp ứng miễn dịch tạo kháng thể bảo vệ cơ thể.',
          blood: 'Động mạch lách (nhánh lớn nhất uốn lượn của thân tạng); Tĩnh mạch lách hợp cùng TM mạc treo tràng trên tạo thành tĩnh mạch cửa.',
          yhct: 'Tỳ vi Gián nghị chi quan, tri chu xuất yên. Tỳ chủ vận hóa (thủy cốc & thủy thấp), thống nhiếp Huyết, chủ Cơ nhục và Tứ chi, khai khiếu ra Miệng, hoa ở Môi. Ngũ hành thuộc Thổ, biểu lý với Vị.',
          acupoints: 'Mộ: Chương Môn (LR13 - Hội của Tạng); Du: Tỳ Du (BL20); Tam Âm Giao (SP6 - Hội 3 kinh âm chân); Thái Bạch (SP3 - Huyệt Nguyên).'
        },
        'organ_kidney_right': {
          vi: 'Quả thận phải (Hữu Thận)',
          lat: 'Ren dexter',
          pos: 'Sau phúc mạc ở hố thắt lưng phải, từ T12 đến L3; Cực trên tiếp xúc tuyến thượng thận phải; Nằm thấp hơn thận trái 1.5cm do gan đè.',
          phys: 'Lọc 180L máu/ngày, cô đặc thành 1.5L nước tiểu; Thải trừ ure, acid uric, creatinin; Điều hòa thăng bằng nước, điện giải, acid-base; Tiết Renin, Erythropoietin, Calcitriol.',
          blood: 'Động mạch thận phải xuất phát từ ĐM chủ bụng, chạy sau TM chủ dưới; Dẫn lưu về TM chủ dưới.',
          yhct: 'Thận vi Tác cường chi quan, kỹ xảo xuất yên. Thận tàng Tinh (sinh dục & phát dục), chủ Cốt tủy, chủ Thủy, chủ Nạp khí, khai khiếu ra Tai và Nhị âm, hoa ở Tóc. Gốc của Tiên Thiên. Biểu lý với Bàng Quang.',
          acupoints: 'Mộ: Kinh Môn (GB25); Du: Thận Du (BL23); Chí Thất (BL52); Thái Khê (KI3 - Huyệt Nguyên); Mệnh Môn (GV4).'
        },
        'organ_kidney_left': {
          vi: 'Quả thận trái (Tả Thận)',
          lat: 'Ren sinister',
          pos: 'Sau phúc mạc ở hố thắt lưng trái, từ T11 đến L2 (cao hơn thận phải); Cực trên tiếp xúc thượng thận trái, lách và dạ dày.',
          phys: 'Đảm nhiệm 50% chức năng thanh thải lọc máu và nội tiết của hệ tiết niệu.',
          blood: 'Động mạch thận trái từ ĐM chủ bụng (ngắn hơn ĐM thận phải); Tĩnh mạch thận trái dài hơn, bắt chéo trước ĐM chủ bụng.',
          yhct: 'Tả thận tàng tinh, hữu thận mệnh môn. Nơi lưu giữ chân âm chân dương của toàn thân.',
          acupoints: 'Mộ: Kinh Môn (GB25); Du: Thận Du (BL23); Thái Khê (KI3), Dũng Tuyền (KI1).'
        },
        'organ_ureter_right': {
          vi: 'Niệu quản phải',
          lat: 'Ureter dexter',
          pos: 'Ống cơ dài 25-28cm, nối bể thận phải chạy sau phúc mạc dọc bờ trước cơ thắt lưng lớn xuống cắm chéo vào đáy bàng quang.',
          phys: 'Dẫn nước tiểu liên tục từ bể thận xuống bàng quang bằng sóng nhu động cơ trơn (2-6 lần/phút); Có 3 chỗ hẹp sinh lý dễ nghẽn sỏi niệu quản.',
          blood: 'Nhánh từ ĐM thận, ĐM sinh dục, ĐM chậu chung và ĐM bàng quang dưới.',
          yhct: 'Con đường vận chuyển thủy đạo từ Thận tạng xuống Bàng Quang phủ.',
          acupoints: 'Đại Cự (ST27), Khí Xung (ST30), Tam Âm Giao (SP6).'
        },
        'organ_ureter_left': {
          vi: 'Niệu quản trái',
          lat: 'Ureter sinister',
          pos: 'Nối bể thận trái chạy dọc cơ thắt lưng lớn trái, bắt chéo trước ĐM chậu chung trái để vào chậu hông bé cắm vào bàng quang.',
          phys: 'Nhu động cơ trơn đẩy nước tiểu một chiều vào bàng quang, van niệu quản - bàng quang ngăn trào ngược.',
          blood: 'Nhánh từ ĐM thận trái, ĐM buồng trứng/tinh hoàn trái và ĐM chậu.',
          yhct: 'Đường dẫn thủy dịch hạ tiêu.',
          acupoints: 'Đại Cự (ST27), Thủy Đạo (ST28).'
        },
        'organ_colon': {
          vi: 'Ruột già (Phủ Đại Trường)',
          lat: 'Colon / Large intestine',
          pos: 'Khung hình chữ U ngược dài 1.5m bao quanh ruột non: Manh tràng & ruột thừa (hố chậu phải) -> ĐT lên -> ĐT ngang -> ĐT xuống -> ĐT sigma -> Trực tràng.',
          phys: 'Hấp thu 90% nước và điện giải từ dưỡng trấp; Hệ vi khuẩn tổng hợp vitamin K, biotin; Tạo khuôn phân và đào thải ra ngoài qua phản xạ đại tiện.',
          blood: 'ĐM mạc treo tràng trên (nửa phải) và ĐM mạc treo tràng dưới (nửa trái); Thần kinh tự chủ điều hòa nhu động (dây X và thần kinh tạng chậu hông S2-S4).',
          yhct: 'Đại trường vi Truyền đạo chi quan, biến hóa xuất yên. Nhận chất cặn bã từ Tiểu Trường, tái hấp thu tân dịch và tống khứ chất cặn bã ra ngoài. Ngũ hành thuộc Kim, biểu lý với Phế.',
          acupoints: 'Mộ: Thiên Khu (ST25); Du: Đại Trường Du (BL25); Hợp Cốc (LI4 - Huyệt Nguyên); Thượng Cự Hư (ST37 - Huyệt Hạ hợp).'
        },
        'organ_small_intestine': {
          vi: 'Ruột non (Phủ Tiểu Trường)',
          lat: 'Intestinum tenue / Small intestine',
          pos: 'Dài 5 - 6 mét, uốn khúc thành 14-16 quai ruột chiếm trung tâm ổ bụng và chậu hông; Gồm Tá tràng, Hỗng tràng và Hồi tràng.',
          phys: 'Cơ quan tiêu hóa và hấp thu dinh dưỡng chủ yếu nhất: Nhận dịch mật và men tụy thủy phân đường, đạm, béo thành chất đơn giản hấp thu qua vi nhung mao.',
          blood: 'ĐM mạc treo tràng trên (SMA) qua các quai động mạch hỗng hồi tràng; Tĩnh mạch dẫn lưu về tĩnh mạch cửa gan.',
          yhct: 'Tiểu trường vi Thụ thịnh chi quan, hóa vật xuất yên. Chủ phân thanh giáng trọc: đưa chất tinh hoa về Tỳ, đưa chất cặn bã xuống Đại trường, đưa nước thừa vào Bàng quang. Ngũ hành thuộc Hỏa, biểu lý với Tâm.',
          acupoints: 'Mộ: Quan Nguyên (CV4); Du: Tiểu Trường Du (BL27); Hạ Cự Hư (ST39 - Huyệt Hạ hợp); Hậu Khê (SI3).'
        },
        'organ_small_intestine_duodenum': {
          vi: 'Tá tràng (Đoạn đầu Ruột non)',
          lat: 'Duodenum',
          pos: 'Đoạn đầu cố định của ruột non dài 25cm hình chữ C ôm quanh đầu tụy, nằm sau phúc mạc.',
          phys: 'Tiếp nhận dưỡng trấp acid từ dạ dày; Đổ dịch mật và dịch tụy qua nhú tá lớn (bóng Vater) để trung hòa acid và bắt đầu tiêu hóa mạnh.',
          blood: 'ĐM vị tá tràng và ĐM mạc treo tràng trên (vòng cung động mạch tá tụy).',
          yhct: 'Cửa ngõ tiếp nhận thủy cốc từ Vị phủ để bắt đầu phân thanh giáng trọc.',
          acupoints: 'Trung Quản (CV12), Lương Môn (ST21).'
        },
        'organ_small_intestine_jejunum': {
          vi: 'Hỗng tràng (Phần trên Ruột non)',
          lat: 'Jejunum',
          pos: 'Chiếm 2/5 trên của đoạn ruột non di động, nằm chủ yếu ở vùng bụng trên bên trái, quai ruột xếp nằm ngang.',
          phys: 'Thành ruột dày, mạch máu phong phú, nếp gấp niêm mạc cao; Hấp thu phần lớn carbohydrate, acid amin và vitamin.',
          blood: 'Các nhánh hỗng tràng của ĐM mạc treo tràng trên.',
          yhct: 'Hóa vật xuất yên, vận hóa tinh chất dưỡng chất.',
          acupoints: 'Thiên Khu (ST25), Quan Nguyên (CV4).'
        },
        'organ_small_intestine_ileum': {
          vi: 'Hồi tràng (Phần cuối Ruột non)',
          lat: 'Ileum',
          pos: 'Chiếm 3/5 dưới của ruột non di động, nằm ở vùng bụng dưới và chậu hông, quai ruột xếp thẳng đứng, tận cùng ở van hồi-manh tràng.',
          phys: 'Hấp thu vitamin B12, muối mật và lượng nước còn lại; Chứa nhiều mảng Peyer (hạch bạch huyết) bảo vệ miễn dịch đường ruột.',
          blood: 'Các nhánh hồi tràng của ĐM mạc treo tràng trên.',
          yhct: 'Đoạn phân định ranh giới giữa thanh khí dinh dưỡng và trọc khí cặn bã.',
          acupoints: 'Khí Hải (CV6), Quan Nguyên (CV4).'
        },
        'organ_mesentery': {
          vi: 'Mạc treo ruột non',
          lat: 'Mesenterium',
          pos: 'Nếp phúc mạc hình quạt rộng neo giữ các quai ruột non vào thành bụng sau; Rễ mạc treo dài 15cm chạy chếch từ góc tá-hỗng tràng (L2 trái) đến khớp cùng chậu phải.',
          phys: 'Chứa bó mạch thần kinh mạc treo tràng trên, mạch bạch huyết (chứa dưỡng trấp nhũ hóa chyle) và hàng trăm hạch bạch huyết mạc treo.',
          blood: 'Toàn bộ mạch máu mạc treo tràng trên.',
          yhct: 'Màng bao nâng đỡ trung tiêu, đường lưu thông của màng mỡ và tân dịch.',
          acupoints: 'Thần Khuyết (CV8), Hoang Du (KI16).'
        },
        'organ_bladder': {
          vi: 'Bàng quang (Phủ Bàng Quang)',
          lat: 'Vesica urinaria / Urinary bladder',
          pos: 'Nằm trong chậu hông bé, sau khớp mu, trước trực tràng (ở nam) hoặc trước tử cung âm đạo (ở nữ); Khi căng phình vượt lên trên khớp mu vào ổ bụng.',
          phys: 'Chứa đựng nước tiểu (dung tích 300 - 500ml); Phản xạ đi tiểu do cơ co bàng quang (detrusor) và cơ thắt niệu đạo phối hợp dưới kiểm soát thần kinh tự chủ và vỏ não.',
          blood: 'Động mạch bàng quang trên và dưới (nhánh từ ĐM chậu trong); Thần kinh đối giao cảm S2-S4 gây co bàng quang, giao cảm T11-L2 giữ nước tiểu.',
          yhct: 'Bàng quang vi Châu đô chi quan, tân dịch tàng yên, khí hóa năng xuất. Nơi chứa đựng nước tiểu dưới tác động khí hóa của Thận dương để bài tiết ra ngoài. Ngũ hành thuộc Thủy, biểu lý với Thận.',
          acupoints: 'Mộ: Trung Cực (CV3); Du: Bàng Quang Du (BL28); Ủy Trung (BL40 - Huyệt Hợp kinh Bàng quang); Côn Lôn (BL60).'
        }
      };

      this.organsModel.traverse((child) => {
        if (child.isMesh) {
          const baseMat = child.material ? child.material.clone() : new THREE.MeshStandardMaterial({
            color: new THREE.Color('#e11d48'),
            roughness: 0.5,
            metalness: 0.1
          });
          child.material = baseMat;
          this.originalMaterials.set(child, {
            color: baseMat.color.clone(),
            emissive: baseMat.emissive.clone(),
            opacity: baseMat.opacity,
            transparent: baseMat.transparent
          });

          const mName = child.name || '';
          let info = organDict[mName] || organDict[mName.replace(/ /g, '_')] || organDict[mName.replace(/_/g, ' ')];
          if (!info) {
            const cleanName = mName.replace(/[\(\)\.\d]/g, '').trim().toLowerCase();
            const matchedKey = Object.keys(organDict).find(k => {
              const cleanK = k.replace(/[\(\)\.\d]/g, '').trim().toLowerCase();
              return cleanName === cleanK || cleanName.includes(cleanK) || cleanK.includes(cleanName);
            });
            if (matchedKey) info = organDict[matchedKey];
          }
          if (!info) {
            info = {
              vi: 'Cấu trúc tạng phủ (' + mName.replace(/_/g, ' ') + ')',
              lat: mName,
              pos: 'Cấu trúc giải phẫu chuyên sâu tạng phủ lồng ngực và ổ bụng.',
              phys: 'Tham gia điều hòa sinh lý nội môi, tuần hoàn, hô hấp hoặc tiêu hóa.',
              blood: 'Hệ thống mạch máu và thần kinh thực vật phân khu tạng phủ.',
              yhct: 'Phối hợp điều hòa khí huyết âm dương giữa lục phủ và ngũ tạng.',
              acupoints: 'Các huyệt vị thuộc 14 đường kinh phân bố theo tiết đoạn thần kinh.',
              note: 'Cấu trúc giải phẫu 3D chuẩn xác Z-Anatomy.'
            };
          }
          child.userData = {
            isOrgan: true,
            meshName: mName,
            nameVi: info.vi,
            nameLat: info.lat,
            note: info.note || '',
            layer: 'organ',
            anatomy_pos: info.pos || '',
            physiology: info.phys || '',
            blood_nerve: info.blood || '',
            yhct_role: info.yhct || '',
            acupoints: info.acupoints || ''
          };
          this.organs.push(child);
        }
      });
    }
  }

  createUI() {
    // 1. Nút kích hoạt trên Top HUD
    let btnDissect = document.getElementById('btnToggleDissection');
    if (!btnDissect) {
      const topHud = document.querySelector('.floating-3d-tools') || document.body;
      btnDissect = document.createElement('button');
      btnDissect.id = 'btnToggleDissection';
      btnDissect.className = 'tool-btn hud-tool-btn';
      btnDissect.title = 'Bóc Tách & Soi Giải Phẫu (Shift + D)';
      btnDissect.innerHTML = `<span class="icon">🔬</span><span class="label">Bóc Tách</span>`;
      btnDissect.style.background = 'linear-gradient(135deg, rgba(239, 68, 68, 0.25), rgba(185, 28, 28, 0.4))';
      btnDissect.style.border = '1px solid rgba(239, 68, 68, 0.5)';
      topHud.appendChild(btnDissect);
    }
    btnDissect.addEventListener('click', () => this.togglePanel());

    // 2. Bảng điều khiển Bóc Tách (Dissection Panel)
    const panel = document.createElement('div');
    panel.id = 'anatomyDissectionPanel';
    panel.className = 'dissection-panel glass-panel';
    panel.innerHTML = `
      <div class="dissect-header">
        <div class="dissect-title">
          <span class="pulse-icon">🔬</span>
          <div>
            <h3>BÓC TÁCH & SOI GIẢI PHẪU 3D</h3>
            <span class="dissect-subtitle">Z-Anatomy Multi-Layer Scientific Engine</span>
          </div>
        </div>
        <button id="btnCloseDissect" class="btn-icon-close" title="Đóng panel">✕</button>
      </div>

      <div class="dissect-body">
        <!-- Chuyển đổi chế độ: Soi Chi Tiết vs Dao Mổ -->
        <div class="dissect-mode-tabs">
          <button id="btnModeInspect" class="mode-tab-btn active" title="Rê chuột để soi tên; Click để xem toàn bộ thông tin khoa học">
            🔍 Soi Thông Tin
          </button>
          <button id="btnModeScalpel" class="mode-tab-btn btn-scalpel-tab" title="Click vào cơ/xương để bóc tách ngay">
            🔪 Dao Mổ Bóc
          </button>
          <button id="btnResetPeeled" class="btn-dissect-reset" title="Khôi phục toàn bộ">
            🔄
          </button>
        </div>

        <div id="modeHintText" class="mode-hint-text">
          💡 <strong>Soi & Tra Cứu:</strong> Rê chuột để soi tên cơ/xương. Bấm trực tiếp vào bất kỳ cấu trúc nào trên mô hình 3D để xem đầy đủ hồ sơ khoa học & huyệt vị!
        </div>

        <!-- Tìm kiếm nhanh 242 xương, 177 cơ, tạng -->
        <div class="dissect-search-container">
          <input type="text" id="dissectSearchInput" class="dissect-search-input" placeholder="🔍 Tra cứu 242 xương, 177 cơ, tạng (ví dụ: delta, đòn, ngực...)" autocomplete="off">
          <div id="dissectSearchResults" class="dissect-search-results" style="display: none;"></div>
        </div>

        <!-- Thẻ thông tin cấu trúc đang chọn (Hiển thị ngay trên đầu khi chọn) -->
        <div id="dissectInfoCard" class="dissect-info-card" style="display: none;">
          <!-- Dynamically populated -->
        </div>

        <!-- Các thanh trượt phân tầng -->
        <div class="dissect-section">
          <div class="section-title">PHÂN TẦNG ĐỘ MỜ (OPACITY)</div>
          
          <div class="layer-control">
            <div class="layer-header">
              <span>🧖 Lớp Da Ngoài</span>
              <div style="display:flex; align-items:center; gap:8px;">
                <span id="valSkinOpacity" class="val-badge">100%</span>
                <label class="switch-toggle">
                  <input type="checkbox" id="chkSkin" checked>
                  <span class="slider round"></span>
                </label>
              </div>
            </div>
            <input type="range" id="sliderSkinOpacity" min="0" max="100" value="100" class="dissect-slider">
          </div>

          <div class="layer-control">
            <div class="layer-header">
              <span>💪 Lớp Cơ Nông (Superficial)</span>
              <div style="display:flex; align-items:center; gap:8px;">
                <span id="valSuperficialOpacity" class="val-badge">100%</span>
                <label class="switch-toggle">
                  <input type="checkbox" id="chkSuperficial" checked>
                  <span class="slider round"></span>
                </label>
              </div>
            </div>
            <input type="range" id="sliderSuperficialOpacity" min="0" max="100" value="100" class="dissect-slider">
          </div>

          <div class="layer-control">
            <div class="layer-header">
              <span>🥩 Lớp Cơ Sâu (Deep Muscles)</span>
              <div style="display:flex; align-items:center; gap:8px;">
                <span id="valDeepOpacity" class="val-badge">100%</span>
                <label class="switch-toggle">
                  <input type="checkbox" id="chkDeep" checked>
                  <span class="slider round"></span>
                </label>
              </div>
            </div>
            <input type="range" id="sliderDeepOpacity" min="0" max="100" value="100" class="dissect-slider">
          </div>

          <div class="layer-control">
            <div class="layer-header">
              <span>🩸 Hệ Mạch Máu (Động & Tĩnh mạch)</span>
              <div style="display:flex; align-items:center; gap:8px;">
                <span id="valVesselsOpacity" class="val-badge">100%</span>
                <label class="switch-toggle">
                  <input type="checkbox" id="chkArteries" checked>
                  <span class="slider round"></span>
                </label>
              </div>
            </div>
            <input type="range" id="sliderVesselsOpacity" min="0" max="100" value="100" class="dissect-slider">
          </div>

          <div class="layer-control">
            <div class="layer-header">
              <span>⚡ Hệ Dây Thần Kinh (123 nhánh Z-Anatomy)</span>
              <div style="display:flex; align-items:center; gap:8px;">
                <span id="valNervesOpacity" class="val-badge">100%</span>
                <label class="switch-toggle">
                  <input type="checkbox" id="chkNerves" checked>
                  <span class="slider round"></span>
                </label>
              </div>
            </div>
            <input type="range" id="sliderNervesOpacity" min="0" max="100" value="100" class="dissect-slider">
          </div>

          <div class="layer-control">
            <div class="layer-header">
              <span>🫀 Lục Phủ Ngũ Tạng (13 Tạng Phủ YHCT)</span>
              <div style="display:flex; align-items:center; gap:8px;">
                <span id="valOrgansOpacity" class="val-badge">100%</span>
                <label class="switch-toggle">
                  <input type="checkbox" id="chkOrgans" checked>
                  <span class="slider round"></span>
                </label>
              </div>
            </div>
            <input type="range" id="sliderOrgansOpacity" min="0" max="100" value="100" class="dissect-slider">
          </div>

          <div class="layer-control">
            <div class="layer-header">
              <span>🦴 Khung Xương (242 Xương)</span>
              <div style="display:flex; align-items:center; gap:8px;">
                <span id="valSkeletonOpacity" class="val-badge">100%</span>
                <label class="switch-toggle">
                  <input type="checkbox" id="chkSkeleton" checked>
                  <span class="slider round"></span>
                </label>
              </div>
            </div>
            <input type="range" id="sliderSkeletonOpacity" min="0" max="100" value="100" class="dissect-slider">
          </div>

          <div class="layer-control">
            <div class="layer-header">
              <span>🟢 Hệ Bạch Huyết (220 Hạch Z-Anatomy)</span>
              <div style="display:flex; align-items:center; gap:8px;">
                <span id="valLymphaticOpacity" class="val-badge">95%</span>
                <label class="switch-toggle">
                  <input type="checkbox" id="chkLymphatic" checked>
                  <span class="slider round"></span>
                </label>
              </div>
            </div>
            <input type="range" id="sliderLymphaticOpacity" min="0" max="100" value="95" class="dissect-slider">
          </div>
        </div>

        <!-- Thao tác nhanh -->
        <div class="quick-dissect-actions">
          <button id="btnPeelAllSuperficial" class="btn-pill">⚡ Bóc Toàn Bộ Cơ Nông</button>
          <button id="btnToggleXRay" class="btn-pill">🔮 Chế Độ X-Ray Xuyên Thấu</button>
        </div>

        <!-- Danh sách cấu trúc đã bóc tách -->
        <div class="dissect-section">
          <div class="section-title" style="display:flex; justify-content:space-between; align-items:center;">
            <span>CẤU TRÚC ĐÃ BÓC TÁCH (<span id="peeledCount">0</span>)</span>
            <button id="btnRestoreAllPeeled" style="background:rgba(239,68,68,0.2); border:1px solid rgba(239,68,68,0.4); color:#fca5a5; font-size:10px; font-weight:700; padding:2px 8px; border-radius:4px; cursor:pointer;">Khôi phục tất cả</button>
          </div>
          <div id="peeledList" class="peeled-list">
            <div class="empty-peeled">Chưa bóc cấu trúc nào. Bạn có thể nháy đúp chuột (hoặc 2 chạm) vào bất kỳ cơ, xương, tạng phủ, mạch máu hay thần kinh để bóc tách ngay!</div>
          </div>
        </div>
      </div>
    `;
    document.body.appendChild(panel);
    this.panel = panel;

    // 3. Floating Tooltip theo con trỏ chuột
    const tooltip = document.createElement('div');
    tooltip.id = 'scalpelHoverTooltip';
    tooltip.className = 'scalpel-tooltip';
    tooltip.style.display = 'none';
    document.body.appendChild(tooltip);
    this.tooltip = tooltip;
  }

  bindEvents() {
    // Phím tắt bàn phím Shift + D
    window.addEventListener('keydown', (e) => {
      if (e.shiftKey && (e.key === 'D' || e.key === 'd')) {
        if (!['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) {
          e.preventDefault();
          this.togglePanel();
        }
      }
    });

    // Nút đóng
    document.getElementById('btnCloseDissect').addEventListener('click', () => this.togglePanel(false));

    // Chuyển đổi Mode: Soi vs Dao mổ
    const bInspect = document.getElementById('btnModeInspect');
    const bScalpel = document.getElementById('btnModeScalpel');
    const hintEl = document.getElementById('modeHintText');

    if (bInspect) {
      bInspect.addEventListener('click', () => {
        this.isInspectActive = true;
        this.isScalpelActive = false;
        bInspect.classList.add('active');
        bScalpel?.classList.remove('active');
        document.body.style.cursor = 'default';
        if (hintEl) {
          hintEl.innerHTML = '💡 <strong>Soi & Tra Cứu:</strong> Rê chuột để soi tên cơ/xương. Bấm trực tiếp vào bất kỳ cấu trúc nào trên mô hình 3D để xem đầy đủ hồ sơ khoa học & huyệt vị!';
        }
      });
    }

    if (bScalpel) {
      bScalpel.addEventListener('click', () => {
        this.isInspectActive = false;
        this.isScalpelActive = true;
        bScalpel.classList.add('active');
        bInspect?.classList.remove('active');
        document.body.style.cursor = 'crosshair';
        if (hintEl) {
          hintEl.innerHTML = '🔪 <strong>Dao Mổ Bóc Tách:</strong> Click vào bất kỳ cơ, tạng hoặc xương nào trên mô hình 3D để bóc tách ngay!';
        }
      });
    }

    // Khôi phục toàn bộ
    document.getElementById('btnResetPeeled').addEventListener('click', () => this.resetAllPeeled());

    // Thiết lập ô tìm kiếm 242 xương & 177 cơ
    this.setupSearch();

    // Sliders
    // Checkboxes cho Da, Cơ nông, Cơ sâu
    document.getElementById('chkSkin')?.addEventListener('change', (e) => {
      const chk = e.target.checked;
      const slider = document.getElementById('sliderSkinOpacity');
      slider.value = chk ? 100 : 0;
      document.getElementById('valSkinOpacity').textContent = slider.value + '%';
      this.setSkinOpacity(chk ? 1.0 : 0);
    });

    document.getElementById('chkSuperficial')?.addEventListener('change', async (e) => {
      const chk = e.target.checked;
      const slider = document.getElementById('sliderSuperficialOpacity');
      if (slider) slider.value = chk ? 100 : 0;
      const valBadge = document.getElementById('valSuperficialOpacity');
      if (valBadge) valBadge.textContent = (chk ? 100 : 0) + '%';
      if (!this.musclesModel && window.toggleMuscles && chk) await window.toggleMuscles(true);
      this.updateMusclesVisibility();
    });

    document.getElementById('chkDeep')?.addEventListener('change', async (e) => {
      const chk = e.target.checked;
      const slider = document.getElementById('sliderDeepOpacity');
      if (slider) slider.value = chk ? 100 : 0;
      const valBadge = document.getElementById('valDeepOpacity');
      if (valBadge) valBadge.textContent = (chk ? 100 : 0) + '%';
      if (!this.musclesModel && window.toggleMuscles && chk) await window.toggleMuscles(true);
      this.updateMusclesVisibility();
    });

    document.getElementById('sliderSkinOpacity').addEventListener('input', (e) => {
      const val = parseInt(e.target.value);
      document.getElementById('valSkinOpacity').textContent = val + '%';
      const chk = document.getElementById('chkSkin');
      if (chk) chk.checked = val > 0;
      this.setSkinOpacity(val / 100);
    });

    document.getElementById('sliderSuperficialOpacity').addEventListener('input', async (e) => {
      const val = parseInt(e.target.value);
      document.getElementById('valSuperficialOpacity').textContent = val + '%';
      const chk = document.getElementById('chkSuperficial');
      if (chk) chk.checked = val > 0;
      if (!this.musclesModel && window.toggleMuscles && val > 0) {
        await window.toggleMuscles(true);
      }
      this.updateMusclesVisibility();
    });

    document.getElementById('sliderDeepOpacity').addEventListener('input', async (e) => {
      const val = parseInt(e.target.value);
      document.getElementById('valDeepOpacity').textContent = val + '%';
      const chk = document.getElementById('chkDeep');
      if (chk) chk.checked = val > 0;
      if (!this.musclesModel && window.toggleMuscles && val > 0) {
        await window.toggleMuscles(true);
      }
      this.updateMusclesVisibility();
    });

    document.getElementById('sliderSkeletonOpacity').addEventListener('input', (e) => {
      const val = parseInt(e.target.value);
      document.getElementById('valSkeletonOpacity').textContent = val + '%';
      const chk = document.getElementById('chkSkeleton');
      if (chk) chk.checked = val > 0;
      this.setLayerOpacity(this.bones, val / 100);
      if (val > 0 && window.toggleSkeleton) window.toggleSkeleton(true);
      if (this.skeletonModel) this.skeletonModel.visible = val > 0;
    });

    document.getElementById('sliderNervesOpacity')?.addEventListener('input', (e) => {
      const val = parseInt(e.target.value);
      document.getElementById('valNervesOpacity').textContent = val + '%';
      this.setLayerOpacity(this.nerves, val / 100);
      if (val > 0 && window.toggleNerves) window.toggleNerves(true);
    });

    document.getElementById('sliderOrgansOpacity')?.addEventListener('input', (e) => {
      const val = parseInt(e.target.value);
      document.getElementById('valOrgansOpacity').textContent = val + '%';
      this.setLayerOpacity(this.organs, val / 100);
      if (val > 0 && window.toggleOrgans) window.toggleOrgans(true);
    });

    document.getElementById('sliderVesselsOpacity')?.addEventListener('input', (e) => {
      const val = parseInt(e.target.value);
      const vb = document.getElementById('valVesselsOpacity');
      if (vb) vb.textContent = val + '%';
      if (window.vesselsModel) {
        window.vesselsModel.traverse(k => {
          if (k.isMesh && k.material) {
            k.material.transparent = val < 100;
            k.material.opacity = val / 100;
            k.material.needsUpdate = true;
          }
        });
      }
      if (val > 0 && window.toggleVessels) window.toggleVessels(true);
    });

    document.getElementById('sliderLymphaticOpacity')?.addEventListener('input', (e) => {
      const val = parseInt(e.target.value);
      const vb = document.getElementById('valLymphaticOpacity');
      if (vb) vb.textContent = val + '%';
      if (window.lymphaticModel) {
        window.lymphaticModel.traverse(k => {
          if (k.isMesh && k.material) {
            k.material.transparent = val < 100;
            k.material.opacity = val / 100;
            k.material.needsUpdate = true;
          }
        });
      }
      if (val > 0 && window.toggleLymphatic) window.toggleLymphatic(true);
    });

    document.getElementById('chkArteries')?.addEventListener('change', (e) => {
      if (window.toggleVessels) window.toggleVessels(e.target.checked);
    });

    document.getElementById('chkNerves')?.addEventListener('change', (e) => {
      if (window.toggleNerves) window.toggleNerves(e.target.checked);
    });

    document.getElementById('chkOrgans')?.addEventListener('change', (e) => {
      if (window.toggleOrgans) window.toggleOrgans(e.target.checked);
    });

    document.getElementById('chkSkeleton')?.addEventListener('change', (e) => {
      if (window.toggleSkeleton) window.toggleSkeleton(e.target.checked);
    });

    document.getElementById('chkLymphatic')?.addEventListener('change', (e) => {
      if (window.toggleLymphatic) window.toggleLymphatic(e.target.checked);
    });

    document.getElementById('btnToggleOrgansQuick')?.addEventListener('click', () => {
      if (window.toggleOrgans) window.toggleOrgans();
    });

    document.getElementById('btnToggleNervesQuick')?.addEventListener('click', () => {
      if (window.toggleNerves) window.toggleNerves();
    });

    document.getElementById('btnPeelAllSuperficial').addEventListener('click', async () => {
      if (!this.musclesModel && window.toggleMuscles) await window.toggleMuscles(true);
      this.superficialMuscles.forEach(m => this.peelMesh(m, false));
      this.updatePeeledListUI();
    });

    document.getElementById('btnToggleXRay').addEventListener('click', () => {
      this.isXRayActive = !this.isXRayActive;
      this.toggleXRay(this.isXRayActive);
      document.getElementById('btnToggleXRay').classList.toggle('active', this.isXRayActive);
    });

    // Mousemove & Click & Double-click & Double-tap cho Raycasting giải phẫu
    const canvas = this.renderer.domElement;
    canvas.addEventListener('mousemove', (e) => this.onMouseMove(e));
    canvas.addEventListener('click', (e) => this.onClick(e));

    // Nháy đúp chuột (Double click) để bóc tách tức thì
    canvas.addEventListener('dblclick', (e) => {
      const hit = this.checkRaycastHit(e);
      if (hit) {
        if (this.hoveredMesh) {
          this.unhighlightMesh(this.hoveredMesh);
          this.hoveredMesh = null;
        }
        this.tooltip.style.display = 'none';
        this.peelMesh(hit, true);
        this.displayInfoCard(hit);
      }
    });

    // Chạm 2 lần (Double-tap) trên màn hình cảm ứng để bóc tách tức thì
    let lastTapTime = 0;
    let lastTapX = 0;
    let lastTapY = 0;
    canvas.addEventListener('touchend', (e) => {
      const currentTime = new Date().getTime();
      const tapLength = currentTime - lastTapTime;
      const touch = e.changedTouches ? e.changedTouches[0] : null;
      if (touch) {
        const dx = Math.abs(touch.clientX - lastTapX);
        const dy = Math.abs(touch.clientY - lastTapY);
        if (tapLength < 350 && tapLength > 40 && dx < 25 && dy < 25) {
          const hit = this.checkRaycastHit({ clientX: touch.clientX, clientY: touch.clientY });
          if (hit) {
            e.preventDefault();
            this.peelMesh(hit, true);
            this.displayInfoCard(hit);
          }
        }
        lastTapTime = currentTime;
        lastTapX = touch.clientX;
        lastTapY = touch.clientY;
      }
    }, { passive: false });

    // Nút khôi phục tất cả
    document.getElementById('btnRestoreAllPeeled')?.addEventListener('click', () => this.resetAllPeeled());
  }

  setupSearch() {
    const sInput = document.getElementById('dissectSearchInput');
    const sResults = document.getElementById('dissectSearchResults');
    if (!sInput || !sResults) return;

    sInput.addEventListener('input', (e) => {
      const q = e.target.value.trim().toLowerCase();
      if (q.length < 2) {
        sResults.style.display = 'none';
        sResults.innerHTML = '';
        return;
      }

      const candidates = [...this.allMuscles, ...this.bones, ...this.organs, ...this.nerves];
      const matches = [];
      for (const m of candidates) {
        const d = m.userData || {};
        const vi = (d.nameVi || '').toLowerCase();
        const lat = (d.nameLat || '').toLowerCase();
        const ac = (d.acupoints || '').toLowerCase();
        const act = (d.action || '').toLowerCase();
        if (vi.includes(q) || lat.includes(q) || ac.includes(q) || act.includes(q)) {
          matches.push(m);
          if (matches.length >= 8) break;
        }
      }

      if (matches.length === 0) {
        sResults.innerHTML = '<div style="padding:10px;font-size:11.5px;color:#94a3b8;text-align:center;">Không tìm thấy cấu trúc giải phẫu phù hợp.</div>';
        sResults.style.display = 'block';
        return;
      }

      sResults.innerHTML = '';
      matches.forEach(m => {
        const d = m.userData || {};
        const row = document.createElement('div');
        row.className = 'search-result-item';
        const ic = d.isBone ? '🦴' : (d.isOrgan ? '🫀' : (d.isNerve ? '⚡' : (d.layer === 'deep' ? '🥩' : '💪')));
        const typeBadge = d.isBone ? 'Xương' : (d.isOrgan ? 'Tạng' : (d.isNerve ? 'Thần kinh' : (d.layer === 'deep' ? 'Cơ sâu' : 'Cơ nông')));

        row.innerHTML = `
          <div style="display:flex;align-items:center;justify-content:space-between;">
            <span style="font-size:12.5px;font-weight:700;color:#f8fafc;">${ic} ${d.nameVi}</span>
            <span style="font-size:10px;color:#38bdf8;background:rgba(56,189,248,0.15);padding:1px 5px;border-radius:3px;">${typeBadge}</span>
          </div>
          ${d.nameLat ? `<div style="font-size:11px;font-style:italic;color:#94a3b8;">${d.nameLat}</div>` : ''}
          ${d.acupoints ? `<div style="font-size:10.5px;color:#fef08a;">🏮 ${d.acupoints}</div>` : ''}
        `;

        row.addEventListener('click', () => {
          sResults.style.display = 'none';
          sInput.value = d.nameVi;
          m.visible = true;
          if (m.parent) m.parent.visible = true;
          this.peeledObjects.delete(m);
          this.selectMesh(m);
          if (this.controls && m.geometry) {
            m.geometry.computeBoundingBox();
            const cnt = new THREE.Vector3();
            m.geometry.boundingBox.getCenter(cnt);
            m.localToWorld(cnt);
            this.controls.target.copy(cnt);
            this.controls.update();
          }
        });
        sResults.appendChild(row);
      });
      sResults.style.display = 'block';
    });

    document.addEventListener('click', (e) => {
      if (!sInput.contains(e.target) && !sResults.contains(e.target)) {
        sResults.style.display = 'none';
      }
    });
  }

  togglePanel(forceState) {
    this.isOpen = (forceState !== undefined) ? forceState : !this.isOpen;
    this.panel.classList.toggle('active', this.isOpen);
    const btnDissect = document.getElementById('btnToggleDissection');
    if (btnDissect) btnDissect.classList.toggle('active', this.isOpen);
    if (this.isOpen && window.syncAllAnatomyControls) {
      window.syncAllAnatomyControls();
    }
    if (this.isOpen) {
      if (!this.musclesModel && window.toggleMuscles) {
        window.toggleMuscles(true);
      }
      if (!this.skeletonModel && (window.Ui || window.skeletonModel)) {
        this.skeletonModel = window.Ui || window.skeletonModel;
      }
      if (window.syncAllAnatomyControls) {
        window.syncAllAnatomyControls();
      }
      if (window.vesselsModel && (!this.vessels || !this.vessels.length)) {
        this.initVesselsModel(window.vesselsModel);
      }
      if (window.lymphaticModel && (!this.lymphatic || !this.lymphatic.length)) {
        this.initLymphaticModel(window.lymphaticModel);
      }
    }
    if (!this.isOpen) {
      if (this.hoveredMesh && this.hoveredMesh !== this.selectedMesh) {
        this.unhighlightMesh(this.hoveredMesh);
        this.hoveredMesh = null;
      }
      this.tooltip.style.display = 'none';
    }
  }

  getLymphaticInfo(raw) {
    const s = (raw || '').trim();
    const norm = s.replace(/[\(\)]/g, '').replace(/\.l$|\.r$/i, '').trim().toLowerCase();
    const side = s.endsWith('.l') ? ' (trái)' : (s.endsWith('.r') ? ' (phải)' : '');

    let vi = 'Hạch bạch huyết ' + s;
    let lat = s;
    let drainage = 'Thu nhận và thanh lọc dịch bạch huyết từ các mô lân cận.';
    let acupoints = 'Hệ thống hạch phòng ngự miễn dịch phân bố dọc đường kinh lạc.';
    let clinical = 'Cơ quan lympho ngoại vi: Lọc kháng nguyên, vi khuẩn và đại thực bào; sản sinh tế bào lympho bảo vệ cơ thể.';

    if (norm.includes('spleen')) {
      vi = 'Tạng Lách (Tỳ Tạng)';
      lat = 'Splen (Lien)';
      drainage = 'Cơ quan lympho lớn nhất cơ thể: Lọc và tiêu hủy hồng cầu già cỗi, dự trữ máu và tiểu cầu.';
      acupoints = 'Chương Môn (LR13 - Mộ của Tạng Tỳ, Hội huyệt của Tạng); Tỳ Du (BL20), Tam Âm Giao (SP6).';
      clinical = 'Bảo vệ miễn dịch thể dịch và tế bào; lách to trong sốt rét, tan máu hoặc tăng áp lực tĩnh mạch cửa.';
    } else if (norm.includes('thymus')) {
      const lobe = norm.includes('left') ? 'thùy trái' : (norm.includes('right') ? 'thùy phải' : '');
      vi = lobe ? `Tuyến ức (${lobe})` : 'Tuyến ức';
      lat = 'Thymus';
      drainage = 'Cơ quan lympho trung ương: Nơi biệt hóa và trưởng thành của tế bào lympho T (miễn dịch qua trung gian tế bào).';
      acupoints = 'Nằm sau xương ức: Đản Trung (CV17 - Hội của Khí), Hoa Cái (CV20), Toàn Cơ (CV21).';
      clinical = 'Phát triển mạnh ở trẻ nhỏ và teo dần sau dậy thì; liên quan chặt chẽ đến bệnh Nhược cơ (Myasthenia Gravis).';
    } else if (norm.includes('tonsil')) {
      vi = `Amidan khẩu cái (Hạch Hạnh)${side}`;
      lat = 'Tonsilla palatina';
      drainage = 'Tuyến phòng ngự đầu tiên tại ngã tư hầu họng, bảo vệ đường hô hấp và tiêu hóa trên.';
      acupoints = 'Liêm Tuyền (CV23), Giáp Xa (ST6), Hợp Cốc (LI4).';
      clinical = 'Viêm amidan cấp/mạn tính, phì đại gây ngủ ngáy hoặc hội chứng ngưng thở khi ngủ.';
    } else if (norm.includes('supraclavicular')) {
      vi = `Nhóm hạch trên đòn (Hạch Virchow / Troisier)${side}`;
      lat = 'Nodi lymphoidei supraclaviculares';
      drainage = 'Nhận bạch huyết từ vùng cổ sâu, trung thất, thành ngực và đặc biệt là tạng ổ bụng qua ống ngực.';
      acupoints = 'Hố trên đòn: Khuyết Bồn (ST12), Thiên Đột (CV22).';
      clinical = 'Dấu hiệu Troisier/Virchow: Hạch thượng đòn trái sưng cứng không đau là chỉ điểm di căn điển hình của ung thư dạ dày hoặc phổi.';
    } else if (norm.includes('infraclavicular')) {
      vi = `Nhóm hạch dưới đòn${side}`;
      lat = 'Nodi lymphoidei infraclaviculares';
      drainage = 'Dẫn lưu bạch huyết vùng ngực trên, cơ ngực lớn và bờ ngoài chi trên.';
      acupoints = 'Rãnh đenta ngực: Vân Môn (LU2), Trung Phủ (LU1 - Mộ huyệt của Phế).';
      clinical = 'Chặng trung chuyển quan trọng của dòng dẫn lưu bạch huyết từ tuyến vú trước khi đổ về ống ngực.';
    } else if (norm.includes('axillary') || norm.includes('brachial') || norm.includes('interpectoral')) {
      let sub = '';
      if (norm.includes('anterior')) sub = ' (Nhóm trước / Nhóm ngực)';
      else if (norm.includes('posterior')) sub = ' (Nhóm sau / Dưới vai)';
      else if (norm.includes('lateral') || norm.includes('brachial')) sub = ' (Nhóm ngoài / Cánh tay)';
      else if (norm.includes('central')) sub = ' (Nhóm trung tâm)';
      else if (norm.includes('apical')) sub = ' (Nhóm đỉnh)';
      else if (norm.includes('interpectoral')) sub = ' (Nhóm gian ngực / Rotter)';
      vi = `Hạch bạch huyết vùng nách${sub}${side}`;
      lat = 'Nodi lymphoidei axillares';
      drainage = 'Dẫn lưu 75% lượng dịch bạch huyết của tuyến vú, thành ngực bên, thành bụng trên rốn và toàn bộ chi trên.';
      acupoints = 'Hố nách: Cực Tuyền (HT1), Uyên Dịch (GB22), Triếp Cân (GB23), Kiên Trinh (SI9).';
      clinical = 'Trạm hạch trọng yếu nhất trong nạo vét hạch và đánh giá giai đoạn di căn của Ung thư vú (TNM Stage).';
    } else if (norm.includes('cubital') || norm.includes('supratrochlear')) {
      vi = `Hạch bạch huyết khuỷu tay / Trên ròng rọc${side}`;
      lat = 'Nodi lymphoidei cubitales / supratrochleares';
      drainage = 'Dẫn lưu dịch bạch huyết nửa trong bàn tay và cẳng tay.';
      acupoints = 'Nếp gấp khuỷu trong: Khúc Trạch (PC3), Thiếu Hải (HT3), Xích Trạch (LU5).';
      clinical = 'Sưng to khi có nhiễm trùng bàn tay, ngón tay hoặc bệnh u hạt (Cat-scratch disease).';
    } else if (norm.includes('tibial') || norm.includes('fibular')) {
      const typ = norm.includes('anterior tibial') ? 'chày trước' : (norm.includes('posterior tibial') ? 'chày sau' : 'xương mác');
      vi = `Hạch bạch huyết ${typ}${side}`;
      lat = 'Nodi lymphoidei tibiales / fibulares';
      drainage = 'Dẫn lưu bạch huyết dọc bó mạch sâu của bàn chân và cẳng chân.';
      acupoints = 'Tam Âm Giao (SP6), Túc Tam Lý (ST36), Giải Khê (ST41), Thái Khê (KI3).';
      clinical = 'Trạm lọc đầu tiên của chi dưới trước khi dịch bạch huyết đổ lên hố khoeo.';
    } else if (norm.includes('popliteal')) {
      const sub = norm.includes('deep') ? 'sâu' : 'nông';
      vi = `Hạch bạch huyết hố khoeo (${sub})${side}`;
      lat = 'Nodi lymphoidei poplitei';
      drainage = 'Dẫn lưu bạch huyết vùng gót chân, bờ ngoài mu chân và các cơ sâu vùng bắp chân.';
      acupoints = 'Chính giữa nếp gấp khoeo: Ủy Trung (BL40 - Hợp huyệt kinh Bàng Quang, Tổng huyệt vùng thắt lưng - gối), Âm Cốc (KI10).';
      clinical = 'Sưng hạch khoeo trong nhiễm trùng bàn chân hoặc u nang bao hoạt dịch Baker vùng khoeo.';
    } else if (norm.includes('inguinal') || norm.includes('lacunar')) {
      const sub = (norm.includes('deep') || norm.includes('lacunar')) ? 'sâu' : 'nông';
      let pos_sub = '';
      if (norm.includes('inferior')) pos_sub = ' dưới';
      else if (norm.includes('superolateral')) pos_sub = ' trên ngoài';
      else if (norm.includes('superomedial')) pos_sub = ' trên trong';
      vi = `Hạch bạch huyết bẹn ${sub}${pos_sub}${side}`;
      lat = 'Nodi lymphoidei inguinales';
      drainage = 'Dẫn lưu dịch bạch huyết toàn bộ chi dưới, vùng mông, đáy chậu, cơ quan sinh dục ngoài và thành bụng dưới rốn.';
      acupoints = 'Nếp gấp bẹn: Khí Xung (ST30), Xung Môn (SP12), Phủ Xá (SP13), Cấp Mạch (LR12).';
      clinical = 'Sưng to và đau khi viêm nhiễm đường tiết niệu - sinh dục hoặc bệnh lây truyền qua đường tình dục (STD).';
    } else if (norm.includes('cervical') || norm.includes('jugular')) {
      const sub = norm.includes('deep') ? 'sâu' : 'nông';
      const sub2 = norm.includes('lateral') ? 'bên' : 'trước';
      vi = `Hạch bạch huyết cổ ${sub} (${sub2})${side}`;
      lat = 'Nodi lymphoidei cervicales';
      drainage = 'Dẫn lưu bạch huyết toàn bộ vùng đầu, mặt, khoang miệng, lưỡi, thanh quản và tuyến giáp.';
      acupoints = 'Dọc cơ ức đòn chũm: Nhân Nghênh (ST9), Phù Đột (LI18), Thiên Đột (CV22), Thiên Dung (SI17).';
      clinical = 'Thường sưng viêm phản ứng trong viêm họng, viêm amidan, lao hạch (tràng nhạc) hoặc di căn K vòm họng.';
    } else if (norm.includes('submandibular') || norm.includes('mandibular')) {
      vi = `Hạch bạch huyết dưới hàm${side}`;
      lat = 'Nodi lymphoidei submandibulares';
      drainage = 'Dẫn lưu từ má, mũi ngoài, môi trên, nướu răng và 2/3 trước của lưỡi.';
      acupoints = 'Góc hàm dưới: Giáp Xa (ST6), Đại Nghinh (ST5), Hạ Quan (ST7).';
      clinical = 'Sưng to trong các bệnh lý nhiễm trùng răng miệng, viêm nướu hoặc ung thư sàn miệng.';
    } else if (norm.includes('submental')) {
      vi = `Hạch bạch huyết dưới cằm${side}`;
      lat = 'Nodi lymphoidei submentales';
      drainage = 'Dẫn lưu bạch huyết vùng cằm, môi dưới và đỉnh lưỡi.';
      acupoints = 'Dưới cằm: Thừa Tương (CV24), Liêm Tuyền (CV23).';
      clinical = 'Phản ứng sưng trong viêm loét môi dưới hoặc mụn nhọt vùng cằm.';
    } else if (norm.includes('bucinator') || norm.includes('nasolabial')) {
      const typ = norm.includes('bucinator') ? 'cơ mút (má)' : 'rãnh mũi má';
      vi = `Hạch bạch huyết ${typ}${side}`;
      lat = 'Nodi lymphoidei faciales';
      drainage = 'Dẫn lưu bạch huyết vùng mi dưới, mũi ngoài, má và môi trên.';
      acupoints = 'Địa Thương (ST4), Giáp Xa (ST6), Nghinh Hương (LI20), Tứ Bạch (ST2).';
      clinical = 'Hạch mặt nông, sưng khi có mụn nhọt hoặc áp-xe vùng má và răng hàm trên.';
    } else if (norm.includes('retropharyngeal')) {
      vi = `Hạch bạch huyết sau hầu${side}`;
      lat = 'Nodi lymphoidei retropharyngeales';
      drainage = 'Dẫn lưu bạch huyết từ vòm mũi họng, vòi nhĩ và các xoang cạnh mũi.';
      acupoints = 'Hạ Quan (ST7), Thiên Dung (SI17), Liêm Tuyền (CV23).';
      clinical = 'Áp-xe khoang sau hầu (Retropharyngeal abscess) là cấp cứu tai mũi họng nguy hiểm ở trẻ nhỏ.';
    } else if (norm.includes('parotid') || norm.includes('pre-auricular') || norm.includes('infra-auricular')) {
      vi = `Hạch bạch huyết tuyến mang tai / Trước tai${side}`;
      lat = 'Nodi lymphoidei parotidei';
      drainage = 'Dẫn lưu từ da vùng thái dương, trán, mí mắt, tai ngoài và tuyến mang tai.';
      acupoints = 'Trước tai: Thính Hội (GB2), Thính Cung (SI19), Nhĩ Môn (TE21), Thái Dương (EX-HN5).';
      clinical = 'Sưng viêm trong viêm tai ngoài, viêm tuyến mang tai do virus quai bị.';
    } else if (norm.includes('mastoid') || norm.includes('retroauricular') || norm.includes('occipital')) {
      const typ = norm.includes('occipital') ? 'chẩm' : 'sau tai (chũm)';
      vi = `Hạch bạch huyết ${typ}${side}`;
      lat = 'Nodi lymphoidei mastoidei / occipitales';
      drainage = 'Dẫn lưu vùng da đầu phía sau, gáy và vành tai.';
      acupoints = 'Vùng sau tai và chẩm: Ế Phong (TE17), Phong Trì (GB20), Thiên Trụ (BL10), Não Không (GB19).';
      clinical = 'Sưng nổi hạch sau gáy trong bệnh sốt phát ban Rubella hoặc viêm da đầu vùng chẩm.';
    } else if (norm.includes('paratracheal') || norm.includes('pretracheal') || norm.includes('thyroid')) {
      vi = `Hạch quanh khí quản & tuyến giáp${side}`;
      lat = 'Nodi lymphoidei paratracheales / thyroidei';
      drainage = 'Dẫn lưu bạch huyết vùng thanh quản, khí quản và tuyến giáp trạng.';
      acupoints = 'Thiên Đột (CV22), Thủy Đột (ST10), Khí Xá (ST11).';
      clinical = 'Vùng hạch quan trọng nhất cần nạo vét trong phẫu thuật điều trị ung thư tuyến giáp thể nhú.';
    } else if (norm.includes('tracheobronchial') || norm.includes('intrapulmonary') || norm.includes('azygos') || norm.includes('broncho') || norm.includes('brachiocephalic') || norm.includes('ligamentum arteriosum')) {
      vi = `Hạch khí phế quản & trung thất${side}`;
      lat = 'Nodi lymphoidei mediastinales / tracheobronchiales';
      drainage = 'Dẫn lưu toàn bộ dịch bạch huyết từ nhu mô phổi, phế quản, tim và mạch máu lớn trung thất.';
      acupoints = 'Khoang liên sườn trước ngực: Định Suyễn (EX-B1), Phế Du (BL13), Đản Trung (CV17).';
      clinical = 'Hạch trung thất sưng to gây hội chứng chèn ép tĩnh mạch chủ trên hoặc chèn ép thần kinh thanh quản quặt ngược gây khàn tiếng.';
    } else if (norm.includes('parasternal') || norm.includes('intercostal') || norm.includes('pericardial') || norm.includes('diaphragmatic')) {
      const typ = norm.includes('parasternal') ? 'cạnh ức' : (norm.includes('pericardial') ? 'màng ngoài tim' : (norm.includes('diaphragmatic') ? 'cơ hoành' : 'gian sườn'));
      vi = `Hạch bạch huyết ${typ}${side}`;
      lat = `Nodi lymphoidei ${typ}`;
      drainage = 'Dẫn lưu thành ngực trước, cơ hoành, màng tim và mặt trên gan.';
      acupoints = 'Đản Trung (CV17), Cự Khuyết (CV14), Kỳ Môn (LR14), Nhật Nguyệt (GB24).';
      clinical = 'Chặng dẫn lưu sâu liên kết giữa lồng ngực và ổ bụng.';
    } else if (norm.includes('cystic node')) {
      vi = 'Hạch túi mật (Hạch Calot / Mascagni)';
      lat = 'Nodus cysticus';
      drainage = 'Dẫn lưu dịch bạch huyết từ túi mật và đường dẫn mật.';
      acupoints = 'Hạ sườn phải: Kỳ Môn (LR14), Nhật Nguyệt (GB24), Dương Lăng Tuyền (GB34).';
      clinical = 'Nằm trong tam giác Calot; mốc giải phẫu quan trọng trong phẫu thuật cắt túi mật nội soi.';
    } else if (norm.includes('gastric') || norm.includes('gastro') || norm.includes('pyloric') || norm.includes('coeliac') || norm.includes('oesophageal')) {
      const sub = norm.includes('oesophageal') ? 'cạnh thực quản' : 'dạ dày - thân tạng';
      vi = `Hạch bạch huyết ${sub}${side}`;
      lat = 'Nodi lymphoidei gastrici / coeliaci / oesophageales';
      drainage = 'Dẫn lưu dịch bạch huyết đoạn dưới thực quản, dạ dày và mạc nối.';
      acupoints = 'Thượng vị: Trung Quản (CV12 - Mộ huyệt của Vị), Vị Du (BL21), Cự Khuyết (CV14).';
      clinical = 'Nạo vét hạch trong phẫu thuật ung thư dạ dày và thực quản.';
    } else if (norm.includes('pancreatic') || norm.includes('splenic nodes')) {
      vi = `Hạch bạch huyết vùng tụy - lách${side}`;
      lat = 'Nodi lymphoidei pancreatici / splenici';
      drainage = 'Dẫn lưu bạch huyết vùng đầu/thân/đuôi tụy, tá tràng và lách.';
      acupoints = 'Kỳ Môn (LR14), Nhật Nguyệt (GB24), Tỳ Du (BL20), Vị Du (BL21).';
      clinical = 'Đánh giá di căn trong ung thư tụy và khối u vùng đuôi tụy - rốn lách.';
    } else if (norm.includes('mesenteric') || norm.includes('colic') || norm.includes('ileocolic') || norm.includes('appendicular') || norm.includes('sigmoid') || norm.includes('caecal')) {
      const sub = norm.includes('appendicular') ? 'ruột thừa' : (norm.includes('caecal') ? 'manh tràng' : (norm.includes('mesenteric') ? 'mạc treo ruột non' : 'đại tràng'));
      vi = `Hạch bạch huyết ${sub}${side}`;
      lat = 'Nodi lymphoidei mesenterici / colici / caecales';
      drainage = 'Thu nhận dưỡng chấp (chyle) hấp thu từ ruột non và dịch bạch huyết từ khung đại tràng.';
      acupoints = 'Quanh rốn: Thiên Xu (ST25), Đại Trường Du (BL25), Hạ Quản (CV10), Khí Hải (CV6).';
      clinical = 'Viêm hạch mạc treo cấp gây hội chứng đau bụng cấp tính; nạo vét hạch trong phẫu thuật K đại tràng.';
    } else if (norm.includes('aortic') || norm.includes('caval') || norm.includes('lumbar') || norm.includes('prevertebral')) {
      const sub = norm.includes('aortic') ? 'quanh ĐM chủ' : (norm.includes('caval') ? 'quanh TM chủ' : (norm.includes('prevertebral') ? 'trước cột sống' : 'thắt lưng'));
      vi = `Nhóm hạch sau phúc mạc (${sub})${side}`;
      lat = 'Nodi lymphoidei para-aortici / lumbales';
      drainage = 'Hội tụ dòng bạch huyết từ toàn bộ chi dưới, tạng chậu hông và các hạch mạc treo tiêu hóa.';
      acupoints = 'Cột sống thắt lưng: Mệnh Môn (GV4), Thận Du (BL23), Chí Thất (BL52), Quan Nguyên Du (BL26).';
      clinical = 'Trạm hội lưu bạch huyết trước khi đổ vào Bể Dưỡng Chấp (Cisterna Chyli) và Ống Ngực (Thoracic Duct).';
    } else if (norm.includes('iliac') || norm.includes('obturator') || norm.includes('sacral') || norm.includes('gluteal')) {
      const sub = norm.includes('iliac') ? 'chậu hông' : (norm.includes('obturator') ? 'vùng bịt' : 'vùng cùng cụt');
      vi = `Hạch bạch huyết ${sub}${side}`;
      lat = 'Nodi lymphoidei iliaci / sacrales';
      drainage = 'Dẫn lưu các cơ quan vùng chậu hông: Bàng quang, trực tràng, tử cung/buồng trứng, tiền liệt tuyến.';
      acupoints = 'Quan Nguyên (CV4), Khí Hải (CV6), Trung Cực (CV3), Bát Liêu (BL31-BL34).';
      clinical = 'Nơi di căn của các khối u vùng tiểu khung (ung thư bàng quang, ung thư cổ tử cung, ung thư tuyến tiền liệt).';
    } else if (norm.includes('vesical') || norm.includes('pararectal')) {
      const sub = norm.includes('vesical') ? 'bàng quang' : 'cạnh trực tràng';
      vi = `Hạch bạch huyết ${sub}${side}`;
      lat = 'Nodi lymphoidei vesicales / pararectales';
      drainage = 'Dẫn lưu thành bàng quang, đoạn dưới trực tràng và ống hậu môn.';
      acupoints = 'Trung Cực (CV3 - Mộ của Bàng Quang), Trường Cường (GV1), Hội Âm (CV1).';
      clinical = 'Đánh giá giai đoạn di căn hạch tại chỗ của ung thư trực tràng và ung thư bàng quang.';
    }

    return { vi, lat, drainage, acupoints, note: clinical };
  }

  initLymphaticModel(model) {
    if (!model) return;
    this.lymphatic = [];
    model.traverse((child) => {
      if (child.isMesh) {
        const baseMat = child.material ? child.material.clone() : new THREE.MeshStandardMaterial({
          color: new THREE.Color('#22c55e'),
          roughness: 0.35,
          metalness: 0.15
        });
        child.material = baseMat;
        this.originalMaterials.set(child, {
          color: baseMat.color.clone(),
          emissive: baseMat.emissive.clone(),
          opacity: baseMat.opacity,
          transparent: baseMat.transparent
        });
        const lInfo = this.getLymphaticInfo(child.name);
        child.userData = {
          isLymphatic: true,
          meshName: child.name,
          nameVi: lInfo.vi,
          nameLat: lInfo.lat,
          drainage: lInfo.drainage,
          acupoints: lInfo.acupoints,
          note: lInfo.note,
          layer: 'lymphatic'
        };
        this.lymphatic.push(child);
      }
    });
  }

  initVesselsModel(model) {
    if (!model) return;
    this.vessels = [];
    model.traverse((child) => {
      if (child.isMesh) {
        const isArtery = !child.name.toLowerCase().includes('vein') && !child.name.toLowerCase().includes('vena');
        const baseColor = isArtery ? '#ef4444' : '#3b82f6';
        const baseMat = child.material ? child.material.clone() : new THREE.MeshStandardMaterial({
          color: new THREE.Color(baseColor),
          roughness: 0.4,
          metalness: 0.15
        });
        child.material = baseMat;
        this.originalMaterials.set(child, {
          color: baseMat.color.clone(),
          emissive: baseMat.emissive.clone(),
          opacity: baseMat.opacity,
          transparent: baseMat.transparent
        });
        const vInfo = this.getVesselInfo(child.name);
        child.userData = {
          isVessel: true,
          isArtery: isArtery,
          meshName: child.name,
          nameVi: vInfo.vi,
          nameLat: vInfo.lat,
          origin: vInfo.origin,
          area: vInfo.area,
          acupoints: vInfo.acupoints,
          note: vInfo.note,
          layer: 'vessels'
        };
        this.vessels.push(child);
      }
    });
  }

  updateMusclesVisibility() {
    const chkS = document.getElementById('chkSuperficial')?.checked;
    const chkD = document.getElementById('chkDeep')?.checked;
    const slS = parseInt(document.getElementById('sliderSuperficialOpacity')?.value || 0);
    const slD = parseInt(document.getElementById('sliderDeepOpacity')?.value || 0);

    const opacS = chkS ? slS / 100 : 0;
    const opacD = chkD ? slD / 100 : 0;
    const anyVisible = opacS > 0 || opacD > 0;

    if (this.musclesModel) {
      this.musclesModel.visible = anyVisible;
    }
    if (window.Yt) {
      window.Yt.visible = anyVisible;
    }
    this.setLayerOpacity(this.superficialMuscles, opacS);
    this.setLayerOpacity(this.deepMuscles, opacD);
  }

  isMeshActuallyVisible(m) {
    if (!m || !m.visible) return false;
    const ud = m.userData || {};
    if (ud.isBone) {
      const c = document.getElementById('chkSkeleton'), s = document.getElementById('sliderSkeletonOpacity');
      if ((c && !c.checked) || (s && parseInt(s.value) <= 0)) return false;
    } else if (ud.isMuscle) {
      if (ud.layer === 'deep') {
        const c = document.getElementById('chkDeep'), s = document.getElementById('sliderDeepOpacity');
        if ((c && !c.checked) || (s && parseInt(s.value) <= 0)) return false;
      } else {
        const c = document.getElementById('chkSuperficial'), s = document.getElementById('sliderSuperficialOpacity');
        if ((c && !c.checked) || (s && parseInt(s.value) <= 0)) return false;
      }
    } else if (ud.isOrgan) {
      const c = document.getElementById('chkOrgans'), s = document.getElementById('sliderOrgansOpacity');
      if ((c && !c.checked) || (s && parseInt(s.value) <= 0)) return false;
    } else if (ud.isNerve) {
      const c = document.getElementById('chkNerves'), s = document.getElementById('sliderNervesOpacity');
      if ((c && !c.checked) || (s && parseInt(s.value) <= 0)) return false;
    } else if (ud.isVessel) {
      const c = document.getElementById('chkArteries'), s = document.getElementById('sliderVesselsOpacity');
      if ((c && !c.checked) || (s && parseInt(s.value) <= 0)) return false;
    } else if (ud.isLymphatic) {
      const c = document.getElementById('chkLymphatic'), s = document.getElementById('sliderLymphaticOpacity');
      if ((c && !c.checked) || (s && parseInt(s.value) <= 0)) return false;
    }
    if (m.material) {
      const mats = Array.isArray(m.material) ? m.material : [m.material];
      for (let i = 0; i < mats.length; i++) {
        if (mats[i].opacity !== undefined && mats[i].opacity <= 0.005) return false;
      }
    }
    let curr = m.parent;
    while (curr) {
      if (!curr.visible) return false;
      curr = curr.parent;
    }
    return true;
  }

  getActiveCandidateMeshes() {
    if (!this.musclesModel && (window.Yt || window.musclesModel)) {
      this.updateModelLayer('muscles', window.Yt || window.musclesModel);
    }
    if (window.vesselsModel && (!this.vessels || !this.vessels.length)) {
      this.initVesselsModel(window.vesselsModel);
    }
    if (window.lymphaticModel && (!this.lymphatic || !this.lymphatic.length)) {
      this.initLymphaticModel(window.lymphaticModel);
    }
    const all = [
      ...this.allMuscles,
      ...this.bones,
      ...this.organs,
      ...this.nerves,
      ...this.vessels,
      ...this.lymphatic
    ];
    return all.filter(m => this.isMeshActuallyVisible(m) && !this.peeledObjects.has(m));
  }

  onMouseMove(e) {
    if (!this.isOpen && !this.isScalpelActive) return;

    const rect = this.renderer.domElement.getBoundingClientRect();
    this.mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    this.mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

    this.raycaster.setFromCamera(this.mouse, this.camera);
    const candidateMeshes = this.getActiveCandidateMeshes();
    const intersects = this.raycaster.intersectObjects(candidateMeshes, false);

    if (intersects.length > 0) {
      const hit = intersects[0].object;
      if (this.hoveredMesh !== hit) {
        if (this.hoveredMesh && this.hoveredMesh !== this.selectedMesh) {
          this.unhighlightMesh(this.hoveredMesh);
        }
        this.hoveredMesh = hit;
        if (this.hoveredMesh !== this.selectedMesh) {
          this.highlightMesh(hit, '#06b6d4', 0.55);
        }
      }
      this.showTooltip(hit, e.clientX, e.clientY);
    } else {
      if (this.hoveredMesh) {
        if (this.hoveredMesh !== this.selectedMesh) {
          this.unhighlightMesh(this.hoveredMesh);
        }
        this.hoveredMesh = null;
      }
      this.tooltip.style.display = 'none';
    }
  }

  onClick(e) {
    if (!this.isOpen && !this.isScalpelActive) return;

    const rect = this.renderer.domElement.getBoundingClientRect();
    this.mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    this.mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

    this.raycaster.setFromCamera(this.mouse, this.camera);
    const candidateMeshes = this.getActiveCandidateMeshes();
    const intersects = this.raycaster.intersectObjects(candidateMeshes, false);

    if (intersects.length > 0) {
      const hit = intersects[0].object;
      if (this.isScalpelActive) {
        if (this.hoveredMesh) {
          this.unhighlightMesh(this.hoveredMesh);
          this.hoveredMesh = null;
        }
        this.tooltip.style.display = 'none';
        this.peelMesh(hit, true);
      } else {
        this.selectMesh(hit);
      }
    } else {
      if (this.isOpen && !this.isScalpelActive) {
        this.togglePanel(false);
      }
      this.unselectMesh();
    }
  }

  checkRaycastHit(e) {
    const rect = this.renderer.domElement.getBoundingClientRect();
    this.mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    this.mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

    this.raycaster.setFromCamera(this.mouse, this.camera);
    const candidateMeshes = this.getActiveCandidateMeshes();
    const intersects = this.raycaster.intersectObjects(candidateMeshes, false);
    return (intersects.length > 0) ? intersects[0].object : null;
  }

  selectMesh(mesh) {
    if (!mesh) return;
    if (this.selectedMesh && this.selectedMesh !== mesh) {
      this.unhighlightMesh(this.selectedMesh);
    }
    this.selectedMesh = mesh;
    this.highlightMesh(mesh, '#00f0ff', 0.85);

    if (!this.isOpen) {
      this.togglePanel(true);
    }
    this.displayInfoCard(mesh);
  }

  unselectMesh() {
    if (this.selectedMesh) {
      this.unhighlightMesh(this.selectedMesh);
      this.selectedMesh = null;
    }
    const card = document.getElementById('dissectInfoCard');
    if (card) card.style.display = 'none';
  }

  displayInfoCard(mesh) {
    const card = document.getElementById('dissectInfoCard');
    if (!card) return;

    const data = mesh.userData || {};
    const nameVi = data.nameVi || 'Cấu trúc giải phẫu';
    const nameLat = data.nameLat || '';

    let badge = '💪 LỚP CƠ NÔNG', ic = '💪', bg = 'rgba(245,158,11,0.15)', col = '#f59e0b';
    if (data.isBone) {
      badge = '🦴 KHUNG XƯƠNG (242 XƯƠNG)'; ic = '🦴'; bg = 'rgba(148,163,184,0.2)'; col = '#e2e8f0';
    } else if (data.isOrgan) {
      badge = '🫀 LỤC PHỦ NGŨ TẠNG'; ic = '🫀'; bg = 'rgba(239,68,68,0.2)'; col = '#f87171';
    } else if (data.isVessel) {
      badge = data.isArtery ? '🩸 HỆ ĐỘNG MẠCH (Z-ANATOMY)' : '🔵 HỆ TĨNH MẠCH (Z-ANATOMY)';
      ic = data.isArtery ? '🩸' : '🔵';
      bg = data.isArtery ? 'rgba(239,68,68,0.2)' : 'rgba(59,130,246,0.2)';
      col = data.isArtery ? '#f87171' : '#60a5fa';
    } else if (data.isLymphatic) {
      badge = '🟢 HỆ BẠCH HUYẾT (Z-ANATOMY)'; ic = '🟢'; bg = 'rgba(34,197,94,0.2)'; col = '#4ade80';
    } else if (data.isNerve) {
      badge = '⚡ DÂY THẦN KINH (Z-ANATOMY)'; ic = '⚡'; bg = 'rgba(234,179,8,0.2)'; col = '#facc15';
    } else if (data.layer === 'deep') {
      badge = '🥩 LỚP CƠ SÂU'; ic = '🥩'; bg = 'rgba(244,63,94,0.2)'; col = '#fb7185';
    }

    const regMap = {
      head_neck: 'Đầu - Mặt - Cổ', shoulder_arm: 'Vai - Cánh tay', forearm_hand: 'Cẳng tay - Bàn tay',
      chest: 'Vùng Ngực', abdomen: 'Vùng Bụng', back: 'Vùng Lưng', pelvis_hip: 'Chậu hông - Mông',
      thigh_knee: 'Đùi - Gối', leg_foot: 'Cẳng - Bàn chân', body: 'Toàn thân'
    };
    const regText = regMap[data.region] || data.region || 'Cơ thể';

    let details = '';
    if (data.isOrgan) {
      if (data.anatomy_pos) details += `<div class="card-prop-row"><span class="prop-label">📍 Vị trí & Cấu trúc:</span><span class="prop-val">${data.anatomy_pos}</span></div>`;
      if (data.physiology) details += `<div class="card-prop-row highlight-action"><span class="prop-label">⚡ Sinh lý học Hiện đại:</span><span class="prop-val">${data.physiology}</span></div>`;
      if (data.blood_nerve) details += `<div class="card-prop-row highlight-nerve"><span class="prop-label">🧠 Mạch máu & Thần kinh:</span><span class="prop-val">${data.blood_nerve}</span></div>`;
      if (data.yhct_role) details += `<div class="card-prop-row highlight-acupoint"><span class="prop-label">🏮 Lý luận Tạng Tượng YHCT:</span><span class="prop-val">${data.yhct_role}</span></div>`;
      if (data.acupoints) details += `<div class="card-prop-row highlight-acupoint"><span class="prop-label">🎯 Du - Mộ Huyệt & Kinh lạc:</span><span class="prop-val">${data.acupoints}</span></div>`;
      if (data.note) details += `<div class="card-prop-row highlight-note"><span class="prop-label">📌 Ghi chú lâm sàng:</span><span class="prop-val">${data.note}</span></div>`;
    } else if (data.isBone) {
      if (data.type) details += `<div class="card-prop-row"><span class="prop-label">🦴 Phân loại hình thái:</span><span class="prop-val">${data.type}</span></div>`;
      if (data.landmarks) details += `<div class="card-prop-row"><span class="prop-label">📍 Mốc mấu giải phẫu then chốt:</span><span class="prop-val">${data.landmarks}</span></div>`;
      if (data.note) details += `<div class="card-prop-row highlight-action"><span class="prop-label">⚡ Vị trí & Cơ năng giải phẫu:</span><span class="prop-val">${data.note}</span></div>`;
      if (data.acupoints) details += `<div class="card-prop-row highlight-acupoint"><span class="prop-label">🏮 Mốc định vị Huyệt Đạo YHCT:</span><span class="prop-val">${data.acupoints}</span></div>`;
    } else if (data.isVessel) {
      if (data.origin) details += `<div class="card-prop-row"><span class="prop-label">📍 Nguyên uỷ xuất phát:</span><span class="prop-val">${data.origin}</span></div>`;
      if (data.area) details += `<div class="card-prop-row highlight-action"><span class="prop-label">⚡ Vùng cấp máu / Dẫn lưu:</span><span class="prop-val">${data.area}</span></div>`;
      if (data.acupoints) details += `<div class="card-prop-row highlight-acupoint"><span class="prop-label">🏮 Mối liên hệ Huyệt Đạo YHCT:</span><span class="prop-val">${data.acupoints}</span></div>`;
      if (data.note) details += `<div class="card-prop-row highlight-note"><span class="prop-label">📌 Ghi chú tuần hoàn:</span><span class="prop-val">${data.note}</span></div>`;
    } else if (data.isLymphatic) {
      if (data.drainage) details += `<div class="card-prop-row"><span class="prop-label">📍 Vùng dẫn lưu bạch huyết:</span><span class="prop-val">${data.drainage}</span></div>`;
      if (data.acupoints) details += `<div class="card-prop-row highlight-acupoint"><span class="prop-label">🏮 Huyệt Đạo lân cận:</span><span class="prop-val">${data.acupoints}</span></div>`;
      if (data.note) details += `<div class="card-prop-row highlight-note"><span class="prop-label">📌 Vai trò miễn dịch:</span><span class="prop-val">${data.note}</span></div>`;
    } else {
      if (data.origin) details += `<div class="card-prop-row"><span class="prop-label">📍 Nguyên uỷ:</span><span class="prop-val">${data.origin}</span></div>`;
      if (data.insertion) details += `<div class="card-prop-row"><span class="prop-label">🎯 Bám tận:</span><span class="prop-val">${data.insertion}</span></div>`;
      if (data.action) details += `<div class="card-prop-row highlight-action"><span class="prop-label">⚡ Động tác & Cơ năng sinh lý:</span><span class="prop-val">${data.action}</span></div>`;
      if (data.innervation) details += `<div class="card-prop-row highlight-nerve"><span class="prop-label">🧠 Thần kinh chi phối:</span><span class="prop-val">${data.innervation}</span></div>`;
      if (data.acupoints) details += `<div class="card-prop-row highlight-acupoint"><span class="prop-label">🏮 Huyệt Đạo YHCT liên quan:</span><span class="prop-val">${data.acupoints}</span></div>`;
      if (data.note) details += `<div class="card-prop-row highlight-note"><span class="prop-label">📌 Ghi chú lâm sàng:</span><span class="prop-val">${data.note}</span></div>`;
    }

    card.innerHTML = `
      <div class="card-header-row">
        <div style="display:flex;align-items:center;gap:6px;">
          <span style="font-size:16px;">${ic}</span>
          <span class="card-badge" style="background:${bg};color:${col};padding:2px 8px;border-radius:4px;font-size:10px;font-weight:800;">${badge}</span>
          <span style="font-size:10px;color:#94a3b8;margin-left:auto;">${regText}</span>
        </div>
        <button id="btnCloseInfoCard" class="btn-card-close" title="Bỏ chọn">✕</button>
      </div>
      <div style="margin:8px 0 4px;">
        <h4 style="margin:0;font-size:15px;font-weight:800;color:#fff;">${nameVi}</h4>
        ${nameLat ? `<div style="font-size:12px;font-style:italic;color:#38bdf8;margin-top:2px;">${nameLat}</div>` : ''}
      </div>
      <div style="display:flex;flex-direction:column;gap:6px;margin-top:8px;font-size:11.5px;line-height:1.4;">
        ${details || '<div style="color:#94a3b8;font-style:italic;">Cấu trúc chuẩn giải phẫu Z-Anatomy.</div>'}
      </div>
      <div style="display:flex;gap:8px;margin-top:12px;border-top:1px solid rgba(255,255,255,0.08);padding-top:8px;">
        <button id="btnPeelThisMesh" class="btn-card-action" style="flex:1;padding:6px 10px;font-size:11.5px;font-weight:700;background:rgba(239,68,68,0.2);border:1px solid rgba(239,68,68,0.5);color:#fca5a5;border-radius:6px;cursor:pointer;">🔪 Bóc tách cấu trúc này</button>
        <button id="btnDismissCard" class="btn-card-action" style="padding:6px 12px;font-size:11.5px;font-weight:600;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.15);color:#cbd5e1;border-radius:6px;cursor:pointer;">Đóng</button>
      </div>
    `;
    card.style.display = 'block';

    card.querySelector('#btnCloseInfoCard')?.addEventListener('click', () => this.unselectMesh());
    card.querySelector('#btnDismissCard')?.addEventListener('click', () => this.unselectMesh());
    card.querySelector('#btnPeelThisMesh')?.addEventListener('click', () => {
      const target = this.selectedMesh;
      this.unselectMesh();
      this.peelMesh(target, true);
    });

    card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  highlightMesh(mesh, color = '#06b6d4', intensity = 0.55) {
    if (!mesh.material) return;
    mesh.material.emissive.set(color);
    mesh.material.emissiveIntensity = intensity;
    mesh.material.needsUpdate = true;
  }

  unhighlightMesh(mesh) {
    if (!mesh.material || !this.originalMaterials.has(mesh)) return;
    const orig = this.originalMaterials.get(mesh);
    mesh.material.emissive.copy(orig.emissive);
    mesh.material.emissiveIntensity = 0.0;
    mesh.material.needsUpdate = true;
  }

  showTooltip(mesh, clientX, clientY) {
    const data = mesh.userData || {};
    const nameVi = data.nameVi || 'Cấu trúc giải phẫu';
    const nameLat = data.nameLat || '';
    let badge = '💪 LỚP CƠ NÔNG';
    let icon = '💪';

    if (data.isBone) {
      badge = '🦴 KHUNG XƯƠNG (Z-ANATOMY)';
      icon = '🦴';
    } else if (data.isOrgan) {
      badge = '🫀 LỤC PHỦ NGŨ TẠNG (Z-ANATOMY)';
      icon = '🫀';
    } else if (data.isVessel) {
      badge = data.isArtery ? '🩸 HỆ ĐỘNG MẠCH (Z-ANATOMY)' : '🔵 HỆ TĨNH MẠCH (Z-ANATOMY)';
      icon = data.isArtery ? '🩸' : '🔵';
    } else if (data.isLymphatic) {
      badge = '🟢 HỆ BẠCH HUYẾT (Z-ANATOMY)';
      icon = '🟢';
    } else if (data.isNerve) {
      badge = '⚡ DÂY THẦN KINH (Z-ANATOMY)';
      icon = '⚡';
    } else if (data.layer === 'deep') {
      badge = '🥩 LỚP CƠ SÂU';
      icon = '🥩';
    }

    let details = '';
    if (data.isOrgan) {
      if (data.anatomy_pos) details += `<div style="margin-top:4px;font-size:11px;color:#cbd5e1;line-height:1.35;">📍 <strong>Vị trí:</strong> ${data.anatomy_pos}</div>`;
      if (data.physiology) details += `<div style="margin-top:3px;font-size:11px;color:#93c5fd;line-height:1.35;">⚡ <strong>Sinh lý học:</strong> ${data.physiology}</div>`;
      if (data.yhct_role) details += `<div style="margin-top:4px;font-size:11px;color:#fef08a;background:rgba(234,179,8,0.18);padding:3px 7px;border-radius:4px;line-height:1.35;">🏮 <strong>Tạng Tượng YHCT:</strong> ${data.yhct_role}</div>`;
      if (data.acupoints) details += `<div style="margin-top:3px;font-size:11px;color:#fca5a5;line-height:1.35;">🎯 <strong>Du - Mộ Huyệt:</strong> ${data.acupoints}</div>`;
      if (data.note) details += `<div style="margin-top:4px;font-size:11px;color:#93c5fd;line-height:1.4;background:rgba(15,23,42,0.6);padding:4px 7px;border-radius:4px;border-left:2px solid #38bdf8;">📌 ${data.note}</div>`;
    } else if (data.isBone) {
      if (data.type) details += `<div style="margin-top:4px;font-size:11px;color:#cbd5e1;line-height:1.35;">🦴 <strong>Phân loại:</strong> ${data.type}</div>`;
      if (data.landmarks) details += `<div style="margin-top:3px;font-size:11px;color:#93c5fd;line-height:1.35;">📍 <strong>Mốc mấu:</strong> ${data.landmarks}</div>`;
      if (data.note) details += `<div style="margin-top:3px;font-size:11px;color:#cbd5e1;line-height:1.35;">⚡ <strong>Cơ năng:</strong> ${data.note}</div>`;
      if (data.acupoints) details += `<div style="margin-top:4px;font-size:11px;color:#fef08a;background:rgba(234,179,8,0.18);padding:3px 7px;border-radius:4px;line-height:1.35;">🏮 <strong>Mốc định vị Huyệt:</strong> ${data.acupoints}</div>`;
    } else if (data.isVessel) {
      if (data.origin) details += `<div style="margin-top:4px;font-size:11px;color:#cbd5e1;line-height:1.35;">📍 <strong>Nguyên uỷ:</strong> ${data.origin}</div>`;
      if (data.area) details += `<div style="margin-top:3px;font-size:11px;color:#93c5fd;line-height:1.35;">⚡ <strong>Vùng phân bố:</strong> ${data.area}</div>`;
      if (data.acupoints) details += `<div style="margin-top:4px;font-size:11px;color:#fef08a;background:rgba(234,179,8,0.18);padding:3px 7px;border-radius:4px;line-height:1.35;">🏮 <strong>Mốc Huyệt YHCT:</strong> ${data.acupoints}</div>`;
      if (data.note) details += `<div style="margin-top:4px;font-size:11px;color:#93c5fd;line-height:1.4;background:rgba(15,23,42,0.6);padding:4px 7px;border-radius:4px;border-left:2px solid #38bdf8;">📌 ${data.note}</div>`;
    } else if (data.isLymphatic) {
      if (data.drainage) details += `<div style="margin-top:4px;font-size:11px;color:#cbd5e1;line-height:1.35;">📍 <strong>Dẫn lưu:</strong> ${data.drainage}</div>`;
      if (data.acupoints) details += `<div style="margin-top:4px;font-size:11px;color:#fef08a;background:rgba(234,179,8,0.18);padding:3px 7px;border-radius:4px;line-height:1.35;">🏮 <strong>Huyệt lân cận:</strong> ${data.acupoints}</div>`;
      if (data.note) details += `<div style="margin-top:4px;font-size:11px;color:#93c5fd;line-height:1.4;background:rgba(15,23,42,0.6);padding:4px 7px;border-radius:4px;border-left:2px solid #38bdf8;">📌 ${data.note}</div>`;
    } else {
      if (data.origin) details += `<div style="margin-top:4px;font-size:11px;color:#cbd5e1;line-height:1.35;">📍 <strong>Nguyên uỷ:</strong> ${data.origin}</div>`;
      if (data.insertion) details += `<div style="margin-top:3px;font-size:11px;color:#cbd5e1;line-height:1.35;">🎯 <strong>Bám tận:</strong> ${data.insertion}</div>`;
      if (data.action) details += `<div style="margin-top:3px;font-size:11px;color:#93c5fd;line-height:1.35;">⚡ <strong>Động tác:</strong> ${data.action}</div>`;
      if (data.innervation) details += `<div style="margin-top:3px;font-size:11px;color:#a5b4fc;line-height:1.35;">🧠 <strong>Thần kinh:</strong> ${data.innervation}</div>`;
      if (data.acupoints) details += `<div style="margin-top:5px;font-size:11px;color:#fef08a;background:rgba(234,179,8,0.18);padding:3px 7px;border-radius:4px;line-height:1.35;">🏮 <strong>Huyệt YHCT liên quan:</strong> ${data.acupoints}</div>`;
      if (data.note) details += `<div style="margin-top:5px;font-size:11px;color:#93c5fd;line-height:1.4;background:rgba(15,23,42,0.6);padding:4px 7px;border-radius:4px;border-left:2px solid #38bdf8;">📌 ${data.note}</div>`;
    }

    const actText = this.isScalpelActive ? '🔪 Click để bóc tách ngay cấu trúc này' : '👉 Click để xem hồ sơ giải phẫu chi tiết';
    const actColor = this.isScalpelActive ? '#f87171' : '#38bdf8';

    this.tooltip.innerHTML = `
      <div class="tooltip-header" style="display:flex;align-items:center;gap:6px;">
        <span class="tooltip-icon">${icon}</span>
        <span class="tooltip-name" style="font-size:13.5px;font-weight:700;color:#f8fafc;">${nameVi}</span>
      </div>
      ${nameLat ? `<div class="tooltip-lat" style="font-size:11.5px;font-style:italic;color:#38bdf8;margin:2px 0 4px;">${nameLat}</div>` : ''}
      <div class="tooltip-badge" style="display:inline-block;font-size:10px;font-weight:800;color:#f59e0b;background:rgba(245,158,11,0.15);padding:2px 6px;border-radius:4px;margin-bottom:4px;">${badge}</div>
      ${details}
      <div class="tooltip-action" style="margin-top:6px;font-size:10.5px;color:${actColor};font-weight:600;">${actText}</div>
    `;
    this.tooltip.style.left = `${clientX + 16}px`;
    this.tooltip.style.top = `${clientY + 16}px`;
    this.tooltip.style.display = 'block';
  }

  peelMesh(mesh, updateUI = true) {
    mesh.visible = false;
    this.peeledObjects.add(mesh);

    // Hiển thị thông tin cấu trúc vừa bóc
    this.displayInfoCard(mesh);
    if (updateUI) this.updatePeeledListUI();
  }

  restoreMesh(mesh) {
    mesh.visible = true;
    this.peeledObjects.delete(mesh);
    this.updatePeeledListUI();
  }

  resetAllPeeled() {
    this.peeledObjects.forEach(m => {
      m.visible = true;
    });
    this.peeledObjects.clear();
    this.updatePeeledListUI();
    const infoCard = document.getElementById('dissectInfoCard');
    if (infoCard) infoCard.style.display = 'none';
  }

  updatePeeledListUI() {
    const listEl = document.getElementById('peeledList');
    const countEl = document.getElementById('peeledCount');
    if (!listEl || !countEl) return;

    countEl.textContent = this.peeledObjects.size;
    if (this.peeledObjects.size === 0) {
      listEl.innerHTML = `<div class="empty-peeled">Chưa bóc cấu trúc nào. Bạn có thể nháy đúp chuột (hoặc 2 chạm) vào bất kỳ cơ, xương, tạng phủ, mạch máu hay thần kinh để bóc tách ngay!</div>`;
      return;
    }

    listEl.innerHTML = '';
    this.peeledObjects.forEach(mesh => {
      const h = mesh.userData || {};
      const name = h.nameVi || mesh.name || 'Cấu trúc giải phẫu';
      const lat = h.nameLat || '';
      let icon = '🥩';
      if (h.isBone) icon = '🦴';
      else if (h.isOrgan) icon = '🫀';
      else if (h.isNerve) icon = '⚡';
      else if (h.isVessel) icon = '🩸';
      else if (h.isLymphatic) icon = '🟢';

      const item = document.createElement('div');
      item.className = 'peeled-item';
      item.style.cssText = 'display:flex; align-items:center; justify-content:space-between; padding:6px 8px; margin-bottom:4px; background:rgba(30,41,59,0.5); border:1px solid rgba(148,163,184,0.15); border-radius:6px;';
      item.innerHTML = `
        <div class="peeled-item-info" style="display:flex; align-items:center; gap:6px; flex:1; overflow:hidden;">
          <span style="font-size:14px;">${icon}</span>
          <div style="overflow:hidden;">
            <div class="peeled-item-name" style="font-size:12px; font-weight:700; color:#f8fafc; text-overflow:ellipsis; overflow:hidden; white-space:nowrap;">${name}</div>
            ${lat ? `<div class="peeled-item-sub" style="font-size:10px; font-style:italic; color:#94a3b8; text-overflow:ellipsis; overflow:hidden; white-space:nowrap;">${lat}</div>` : ''}
          </div>
        </div>
        <button class="btn-restore-single" style="background:rgba(56,189,248,0.15); border:1px solid rgba(56,189,248,0.4); color:#38bdf8; font-size:10px; font-weight:700; padding:3px 8px; border-radius:4px; cursor:pointer;">Khôi phục</button>
      `;
      item.querySelector('.btn-restore-single').addEventListener('click', (e) => {
        e.stopPropagation();
        this.restoreMesh(mesh);
      });
      listEl.appendChild(item);
    });
  }

  setSkinOpacity(opacity) {
    if (this.humanModel) {
      const isOpaque = opacity >= 0.75;
      this.humanModel.visible = opacity > 0.005;
      this.humanModel.traverse((child) => {
        if (child.isMesh && child.material) {
          child.material.transparent = opacity < 0.99;
          child.material.opacity = opacity;
          child.material.depthWrite = isOpaque;
          child.material.polygonOffset = true;
          child.material.polygonOffsetFactor = isOpaque ? -4 : -2;
          child.material.polygonOffsetUnits = isOpaque ? -8 : -4;
          child.material.needsUpdate = true;
        }
      });
    }
  }

  setLayerOpacity(meshList, opacity) {
    meshList.forEach(m => {
      if (m.material) {
        m.material.transparent = opacity < 0.99;
        m.material.opacity = opacity;
        m.material.depthWrite = opacity >= 0.99;
        m.visible = opacity > 0.005 && !this.peeledObjects.has(m);
        m.material.needsUpdate = true;
      }
    });
  }

  toggleXRay(enable) {
    this.allMuscles.forEach(m => {
      if (m.material) {
        m.material.wireframe = enable;
        m.material.transparent = true;
        m.material.opacity = enable ? 0.25 : 1.0;
        m.material.needsUpdate = true;
      }
    });
    if (this.humanModel) {
      this.humanModel.traverse((child) => {
        if (child.isMesh && child.material) {
          child.material.wireframe = enable;
          child.material.opacity = enable ? 0.15 : 0.35;
          child.material.needsUpdate = true;
        }
      });
    }
  }

  /**
   * Cập nhật mô hình được nạp On-Demand (Lazy Loaded)
   */
  updateModelLayer(layerType, model) {
    if (!model) return;
    if (layerType === 'muscles') {
      this.musclesModel = model;
    } else if (layerType === 'nerves') {
      this.nervesModel = model;
    } else if (layerType === 'organs') {
      this.organsModel = model;
    } else if (layerType === 'skeleton') {
      this.skeletonModel = model;
    }
    this.initClassifications();
  }
}
