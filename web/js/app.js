/**
 * app.js
 * Controller trung gian điều phối toàn bộ WebApp NewAtlas Pro
 */

import { storageManager } from './storageManager.js';
import { ThreeViewer } from './threeViewer.js';

class NewAtlasApp {
  constructor() {
    this.viewer = null;
    this.acupoints = [];
    this.meridians = [];
    this.specialGroups = [];

    // Bảng Tý Ngọ Lưu Chú 12 Can Chi & Khai Huyệt
    this.horaryBranches = [
      { branch: 'Tý (23h-01h)', id: 'GB', name: 'Đởm (Túi Mật)', hourStart: 23, hourEnd: 1, element: 'Mộc (Dương)', bo: { code: 'GB43', name: 'Hiệp Khê', rule: 'Huyệt Huỳnh (Thủy) • Thủy sinh Mộc (Bổ Mẹ)' }, ta: { code: 'GB38', name: 'Dương Phụ', rule: 'Huyệt Kinh (Hỏa) • Mộc sinh Hỏa (Tả Con)' }, nguyen: { code: 'GB40', name: 'Khâu Khư', rule: 'Huyệt Nguyên • Điều hòa nguyên khí Đởm kinh' } },
      { branch: 'Sửu (01h-03h)', id: 'LR', name: 'Can (Gan)', hourStart: 1, hourEnd: 3, element: 'Mộc (Âm)', bo: { code: 'LR8', name: 'Khúc Tuyền', rule: 'Huyệt Hợp (Thủy) • Thủy sinh Mộc (Bổ Mẹ)' }, ta: { code: 'LR2', name: 'Hành Gian', rule: 'Huyệt Huỳnh (Hỏa) • Mộc sinh Hỏa (Tả Con)' }, nguyen: { code: 'LR3', name: 'Thái Xung', rule: 'Huyệt Du / Nguyên • Khí huyết Can tạng' } },
      { branch: 'Dần (03h-05h)', id: 'LU', name: 'Phế (Phổi)', hourStart: 3, hourEnd: 5, element: 'Kim (Âm)', bo: { code: 'LU9', name: 'Thái Uyên', rule: 'Huyệt Du (Thổ) • Thổ sinh Kim (Bổ Mẹ)' }, ta: { code: 'LU5', name: 'Xích Trạch', rule: 'Huyệt Hợp (Thủy) • Kim sinh Thủy (Tả Con)' }, nguyen: { code: 'LU9', name: 'Thái Uyên', rule: 'Huyệt Nguyên • Tụ nguyên khí Phế kinh' } },
      { branch: 'Mão (05h-07h)', id: 'LI', name: 'Đại Trường', hourStart: 5, hourEnd: 7, element: 'Kim (Dương)', bo: { code: 'LI11', name: 'Khúc Trì', rule: 'Huyệt Hợp (Thổ) • Thổ sinh Kim (Bổ Mẹ)' }, ta: { code: 'LI2', name: 'Nhị Gian', rule: 'Huyệt Huỳnh (Thủy) • Kim sinh Thủy (Tả Con)' }, nguyen: { code: 'LI4', name: 'Hợp Cốc', rule: 'Huyệt Nguyên • Trấn thống đại huyệt' } },
      { branch: 'Thìn (07h-09h)', id: 'ST', name: 'Vị (Dạ Dày)', hourStart: 7, hourEnd: 9, element: 'Thổ (Dương)', bo: { code: 'ST41', name: 'Giải Khê', rule: 'Huyệt Kinh (Hỏa) • Hỏa sinh Thổ (Bổ Mẹ)' }, ta: { code: 'ST45', name: 'Lệ Đoài', rule: 'Huyệt Tỉnh (Kim) • Thổ sinh Kim (Tả Con)' }, nguyen: { code: 'ST42', name: 'Xung Dương', rule: 'Huyệt Nguyên • Khí huyết Vị phủ' } },
      { branch: 'Tỵ (09h-11h)', id: 'SP', name: 'Tỳ (Lá Lách)', hourStart: 9, hourEnd: 11, element: 'Thổ (Âm)', bo: { code: 'SP2', name: 'Đại Đô', rule: 'Huyệt Huỳnh (Hỏa) • Hỏa sinh Thổ (Bổ Mẹ)' }, ta: { code: 'SP5', name: 'Thương Khâu', rule: 'Huyệt Kinh (Kim) • Thổ sinh Kim (Tả Con)' }, nguyen: { code: 'SP3', name: 'Thái Bạch', rule: 'Huyệt Du / Nguyên • Kiện Tỳ ích khí' } },
      { branch: 'Ngọ (11h-13h)', id: 'HT', name: 'Tâm (Tim)', hourStart: 11, hourEnd: 13, element: 'Hỏa (Âm)', bo: { code: 'HT9', name: 'Thiếu Xung', rule: 'Huyệt Tỉnh (Mộc) • Mộc sinh Hỏa (Bổ Mẹ)' }, ta: { code: 'HT7', name: 'Thần Môn', rule: 'Huyệt Du (Thổ) • Hỏa sinh Thổ (Tả Con)' }, nguyen: { code: 'HT7', name: 'Thần Môn', rule: 'Huyệt Nguyên • Dưỡng tâm an thần' } },
      { branch: 'Mùi (13h-15h)', id: 'SI', name: 'Tiểu Trường', hourStart: 13, hourEnd: 15, element: 'Hỏa (Dương)', bo: { code: 'SI3', name: 'Hậu Khê', rule: 'Huyệt Du (Mộc) • Mộc sinh Hỏa (Bổ Mẹ)' }, ta: { code: 'SI8', name: 'Tiểu Hải', rule: 'Huyệt Hợp (Thổ) • Hỏa sinh Thổ (Tả Con)' }, nguyen: { code: 'SI4', name: 'Uyển Cốt', rule: 'Huyệt Nguyên • Thanh nhiệt giải uất' } },
      { branch: 'Thân (15h-17h)', id: 'BL', name: 'Bàng Quang', hourStart: 15, hourEnd: 17, element: 'Thủy (Dương)', bo: { code: 'BL67', name: 'Chí Âm', rule: 'Huyệt Tỉnh (Kim) • Kim sinh Thủy (Bổ Mẹ)' }, ta: { code: 'BL65', name: 'Thúc Cốt', rule: 'Huyệt Du (Mộc) • Thủy sinh Mộc (Tả Con)' }, nguyen: { code: 'BL64', name: 'Kinh Cốt', rule: 'Huyệt Nguyên • Sơ phong thanh nhiệt' } },
      { branch: 'Dậu (17h-19h)', id: 'KI', name: 'Thận', hourStart: 17, hourEnd: 19, element: 'Thủy (Âm)', bo: { code: 'KI7', name: 'Phục Lưu', rule: 'Huyệt Kinh (Kim) • Kim sinh Thủy (Bổ Mẹ)' }, ta: { code: 'KI1', name: 'Dũng Tuyền', rule: 'Huyệt Tỉnh (Mộc) • Thủy sinh Mộc (Tả Con)' }, nguyen: { code: 'KI3', name: 'Thái Khê', rule: 'Huyệt Du / Nguyên • Tư âm bổ thận' } },
      { branch: 'Tuất (19h-21h)', id: 'PC', name: 'Tâm Bào', hourStart: 19, hourEnd: 21, element: 'Hỏa (Âm)', bo: { code: 'PC9', name: 'Trung Xung', rule: 'Huyệt Tỉnh (Mộc) • Mộc sinh Hỏa (Bổ Mẹ)' }, ta: { code: 'PC7', name: 'Đại Lăng', rule: 'Huyệt Du (Thổ) • Hỏa sinh Thổ (Tả Con)' }, nguyen: { code: 'PC7', name: 'Đại Lăng', rule: 'Huyệt Nguyên • Thanh tâm hỏa' } },
      { branch: 'Hợi (21h-23h)', id: 'TE', name: 'Tam Tiêu', hourStart: 21, hourEnd: 23, element: 'Hỏa (Dương)', bo: { code: 'TE3', name: 'Trung Chử', rule: 'Huyệt Du (Mộc) • Mộc sinh Hỏa (Bổ Mẹ)' }, ta: { code: 'TE10', name: 'Thiên Tỉnh', rule: 'Huyệt Hợp (Thổ) • Hỏa sinh Thổ (Tả Con)' }, nguyen: { code: 'TE4', name: 'Dương Trì', rule: 'Huyệt Nguyên • Thông kinh hoạt lạc' } }
    ];

    // Danh mục hệ giải phẫu
    this.systemsConfig = [
      { id: 'skeleton', name: 'Hệ Khung Xương', file: 'models/skeleton.glb', sizeText: '~5 MB', isCore: true, loaded: false, visible: true, opacity: 1.0 },
      { id: 'muscles', name: 'Hệ Cơ Bắp', file: 'models/muscles.glb', sizeText: '~5.4 MB', isCore: true, loaded: false, visible: false, opacity: 0.85 },
      { id: 'skin', name: 'Lớp Da Ngọc Bích', file: 'models/human-learning.glb', sizeText: '~628 KB', isCore: true, loaded: false, visible: true, opacity: 0.4 },
      { id: 'nerves', name: 'Hệ Thần Kinh', file: 'models/nerves.glb', sizeText: '~23 MB', isCore: false, loaded: false, visible: false, opacity: 1.0 },
      { id: 'organs', name: 'Hệ Nội Tạng (Tạng Phủ)', file: 'models/organs.glb', sizeText: '~18 MB', isCore: false, loaded: false, visible: false, opacity: 1.0 },
      { id: 'lymphatic', name: 'Hệ Bạch Huyết', file: 'models/lymphatic.glb', sizeText: '~12 MB', isCore: false, loaded: false, visible: false, opacity: 1.0 },
      { id: 'vessels', name: 'Hệ Tuần Hoàn (Mạch Máu)', file: 'models/vessels.glb', sizeText: '~15 MB', isCore: false, loaded: false, visible: false, opacity: 1.0 }
    ];

    this.currentFilter = 'all'; // 'all' (419), 'primary' (362), 'extra' (57)
    this.selectedChannel = null;
    this.currentBranch = null;
  }

  async init() {
    console.log('[NewAtlas] Khởi chạy ứng dụng...');

    const hideSplash = () => {
      const splash = document.getElementById('app-loading');
      if (splash && splash.style.opacity !== '0') {
        splash.style.opacity = '0';
        setTimeout(() => splash.remove(), 400);
      }
    };

    try {
      // 1. Khởi tạo 3D Viewer
      const canvasContainer = document.getElementById('canvas-container');
      this.viewer = new ThreeViewer(canvasContainer);

      // Gắn callbacks tương tác
      this.viewer.onPointHover = (pt, evt) => this.handlePointHover(pt, evt);
      this.viewer.onPointClick = (pt) => this.showPointDetail(pt);

      // 2. Nạp dữ liệu Kinh Lạc & 419 Huyệt Vị
      await this.loadAcupunctureData();

      // 3. Khởi tạo UI Điều khiển, Đồng hồ Tý Ngọ Lưu Chú
      this.initUI();
      this.initHoraryClock();

      // 4. Cập nhật trạng thái Cache trên giao diện
      await this.updateCacheStatsUI();

      // Ẩn splash screen NGAY LẬP TỨC để người dùng thấy kinh lạc huyệt vị tức thì!
      hideSplash();

      // 5. Tải ngầm các hệ Baseline cốt lõi (Da, Xương)
      this.loadCoreSystems().then(() => {
        console.log('[NewAtlas] Đã tải xong các hệ giải phẫu cốt lõi.');
      }).catch(err => {
        console.warn('[NewAtlas] Lỗi tải hệ cốt lõi ngầm:', err);
      });

    } catch (err) {
      console.error('[NewAtlas] Lỗi khởi tạo ứng dụng:', err);
      hideSplash();
    }
  }

  async loadAcupunctureData() {
    try {
      const [ptsRes, merRes] = await Promise.all([
        fetch('data/acupoints.json'),
        fetch('data/meridians.json')
      ]);

      this.acupoints = await ptsRes.json();
      this.meridians = await merRes.json();

      console.log(`[NewAtlas] Đã nạp ${this.acupoints.length} huyệt vị và ${this.meridians.length} đường kinh.`);

      this.viewer.setAcupoints(this.acupoints);
      this.viewer.setMeridians(this.meridians);

      const countEl = document.getElementById('stat-total-points');
      if (countEl) countEl.innerText = this.acupoints.length;
    } catch (err) {
      console.error('[NewAtlas] Lỗi nạp dữ liệu kinh huyệt:', err);
    }
  }

  async loadCoreSystems() {
    for (const sys of this.systemsConfig) {
      if (sys.isCore) {
        await this.loadOrActivateSystem(sys.id, false);
      }
    }
  }

  async loadOrActivateSystem(systemId, showProgressModal = true) {
    const sys = this.systemsConfig.find(s => s.id === systemId);
    if (!sys) return;

    if (sys.loaded) {
      sys.visible = !sys.visible;
      this.viewer.setSystemVisibility(systemId, sys.visible);
      this.updateSystemToggleUI(systemId);
      return;
    }

    const progressModal = document.getElementById('download-progress-modal');
    const progressBar = document.getElementById('download-progress-bar');
    const progressPercent = document.getElementById('download-progress-percent');
    const progressTitle = document.getElementById('download-progress-title');

    if (showProgressModal && progressModal) {
      progressTitle.innerText = `Đang tải ${sys.name} (${sys.sizeText})...`;
      progressBar.style.width = '0%';
      progressPercent.innerText = '0%';
      progressModal.classList.remove('hidden');
    }

    try {
      const { data, isCached } = await storageManager.loadSystemData(
        sys.id,
        sys.file,
        (percent, loaded, total, fromCache) => {
          if (showProgressModal && progressBar && progressPercent) {
            progressBar.style.width = `${percent}%`;
            progressPercent.innerText = fromCache ? 'Đọc từ Cache máy...' : `${percent}%`;
          }
        }
      );

      await this.viewer.loadSystemModel(sys.id, data);
      sys.loaded = true;
      sys.visible = true;

      this.updateSystemToggleUI(systemId);
      await this.updateCacheStatsUI();

      if (showProgressModal && progressModal) {
        setTimeout(() => progressModal.classList.add('hidden'), 300);
      }
    } catch (err) {
      console.error(`[NewAtlas] Lỗi tải hệ ${sys.name}:`, err);
      if (showProgressModal && progressModal) {
        progressTitle.innerText = `Chưa có tệp ${sys.file}. Hãy chạy export từ Blender!`;
        setTimeout(() => progressModal.classList.add('hidden'), 2000);
      }
    }
  }

  /**
   * ĐỒNG HỒ TÝ NGỌ LƯU CHÚ THỜI GIAN THỰC (HORARY MERIDIAN CLOCK)
   */
  initHoraryClock() {
    const clockBadge = document.getElementById('horary-clock-badge');
    const clockTime = document.getElementById('horary-current-time');
    const clockBranch = document.getElementById('horary-active-branch');
    const popover = document.getElementById('horary-popover');
    const btnClosePopover = document.getElementById('btn-close-horary-popover');
    const btnFocusMeridian = document.getElementById('btn-horary-focus-meridian');

    const updateClock = () => {
      const now = new Date();
      const hours = now.getHours();
      const minutes = String(now.getMinutes()).padStart(2, '0');
      const seconds = String(now.getSeconds()).padStart(2, '0');

      if (clockTime) clockTime.innerText = `${String(hours).padStart(2, '0')}:${minutes}:${seconds}`;

      // Tìm Can Chi tương ứng theo giờ hiện tại
      let matchedBranch = null;
      for (const b of this.horaryBranches) {
        if (b.hourStart > b.hourEnd) {
          // Khung giờ Tý (23h - 01h sáng)
          if (hours >= b.hourStart || hours < b.hourEnd) {
            matchedBranch = b;
            break;
          }
        } else {
          if (hours >= b.hourStart && hours < b.hourEnd) {
            matchedBranch = b;
            break;
          }
        }
      }

      if (matchedBranch && this.currentBranch !== matchedBranch) {
        this.currentBranch = matchedBranch;
        if (clockBranch) {
          clockBranch.innerText = `${matchedBranch.branch} • Kinh ${matchedBranch.name}`;
        }
        this.renderHoraryPopover(matchedBranch);
      }
    };

    updateClock();
    setInterval(updateClock, 1000);

    // Bật/tắt Popover
    if (clockBadge) {
      clockBadge.addEventListener('click', (e) => {
        e.stopPropagation();
        popover.classList.toggle('hidden');
      });
    }

    if (btnClosePopover) {
      btnClosePopover.addEventListener('click', () => {
        popover.classList.add('hidden');
      });
    }

    // Đóng popover khi click ngoài
    document.addEventListener('click', (e) => {
      if (popover && !popover.contains(e.target) && !clockBadge.contains(e.target)) {
        popover.classList.add('hidden');
      }
    });

    // Nút Focus vào Kinh Mạch Đang Vượng Khí
    if (btnFocusMeridian) {
      btnFocusMeridian.addEventListener('click', () => {
        if (this.currentBranch) {
          this.viewer.highlightMeridian(this.currentBranch.id);
          popover.classList.add('hidden');
        }
      });
    }
  }

  renderHoraryPopover(branch) {
    if (!branch) return;
    document.getElementById('hr-branch-name').innerText = branch.branch;
    document.getElementById('hr-meridian-name').innerText = `Kinh ${branch.name} (${branch.element})`;
    document.getElementById('hr-bo-code').innerText = `${branch.bo.code} - ${branch.bo.name}`;
    document.getElementById('hr-bo-desc').innerText = branch.bo.rule;
    document.getElementById('hr-ta-code').innerText = `${branch.ta.code} - ${branch.ta.name}`;
    document.getElementById('hr-ta-desc').innerText = branch.ta.rule;
    document.getElementById('hr-nguyen-code').innerText = `${branch.nguyen.code} - ${branch.nguyen.name}`;
    document.getElementById('hr-nguyen-desc').innerText = branch.nguyen.rule;
  }

  initUI() {
    // 1. Tạo danh sách các công tắc hệ giải phẫu
    const systemsListContainer = document.getElementById('systems-list');
    if (systemsListContainer) {
      systemsListContainer.innerHTML = '';
      this.systemsConfig.forEach((sys) => {
        const item = document.createElement('div');
        item.className = 'system-card';
        item.id = `system-card-${sys.id}`;

        item.innerHTML = `
          <div class="system-card-header">
            <div class="system-info">
              <span class="system-name">${sys.name}</span>
              <span class="system-status-badge" id="badge-${sys.id}">Đang kiểm tra...</span>
            </div>
            <label class="switch">
              <input type="checkbox" id="toggle-${sys.id}" ${sys.visible ? 'checked' : ''}>
              <span class="slider round"></span>
            </label>
          </div>
          <div class="system-opacity-row">
            <span class="opacity-label">Độ mờ:</span>
            <input type="range" class="opacity-slider" id="opacity-${sys.id}" min="0.05" max="1.0" step="0.05" value="${sys.opacity}">
          </div>
        `;

        systemsListContainer.appendChild(item);

        const toggle = item.querySelector(`#toggle-${sys.id}`);
        toggle.addEventListener('change', () => {
          this.loadOrActivateSystem(sys.id, true);
        });

        const opacitySlider = item.querySelector(`#opacity-${sys.id}`);
        opacitySlider.addEventListener('input', (e) => {
          const val = parseFloat(e.target.value);
          sys.opacity = val;
          this.viewer.setSystemOpacity(sys.id, val);
        });
      });
    }

    // 2. Bộ lọc số lượng huyệt (Tất cả 419, 14 Kinh chính 362, Kỳ huyệt 57)
    const filterTabs = document.querySelectorAll('.filter-tab');
    filterTabs.forEach((tab) => {
      tab.addEventListener('click', () => {
        filterTabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        this.currentFilter = tab.dataset.filter;
        this.applyFilters();
      });
    });

    // 3. Thanh Focus Phân Khu Cơ Thể (Body Regions Focus Chips)
    const regionButtons = document.querySelectorAll('.region-chip');
    regionButtons.forEach((btn) => {
      btn.addEventListener('click', () => {
        regionButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const reg = btn.dataset.region;
        this.viewer.focusRegion(reg);
      });
    });

    // 4. Nút Toggle Bật/Tắt Nhãn Tên Huyệt (3D Text Labels)
    const btnToggleLabels = document.getElementById('btn-toggle-labels');
    if (btnToggleLabels) {
      btnToggleLabels.addEventListener('click', () => {
        this.viewer.showLabels = !this.viewer.showLabels;
        this.viewer.toggleLabels(this.viewer.showLabels);
        btnToggleLabels.classList.toggle('active', this.viewer.showLabels);
      });
    }

    // 5. Nút Đổi Kiểu Nhãn (Mã + Tên / Chỉ Tên / Chỉ Mã)
    const btnCycleLabels = document.getElementById('btn-cycle-label-mode');
    if (btnCycleLabels) {
      btnCycleLabels.addEventListener('click', () => {
        const mode = this.viewer.cycleLabelMode();
        const modeNames = {
          code_name: 'Nhãn: Mã + Tên',
          vi_only: 'Nhãn: Tên Việt',
          code_only: 'Nhãn: Mã WHO'
        };
        btnCycleLabels.innerText = modeNames[mode] || 'Nhãn Tên';
      });
    }

    // 6. Tìm kiếm huyệt vị
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        const query = e.target.value.trim().toLowerCase();
        this.searchAcupoints(query);
      });
    }

    // 7. Nút Reset góc nhìn Camera
    const resetCamBtn = document.getElementById('btn-reset-cam');
    if (resetCamBtn) {
      resetCamBtn.addEventListener('click', () => {
        this.viewer.resetCamera();
        this.viewer.resetMeridianHighlight();
        regionButtons.forEach(b => b.classList.remove('active'));
        const allBtn = document.querySelector('.region-chip[data-region="all"]');
        if (allBtn) allBtn.classList.add('active');
      });
    }

    // 8. Nút Đóng Drawer chi tiết
    const closeDrawerBtn = document.getElementById('btn-close-drawer');
    if (closeDrawerBtn) {
      closeDrawerBtn.addEventListener('click', () => {
        document.getElementById('acupoint-drawer').classList.add('closed');
      });
    }

    // 9. Nút Dọn dẹp Cache
    const clearCacheBtn = document.getElementById('btn-clear-cache');
    if (clearCacheBtn) {
      clearCacheBtn.addEventListener('click', async () => {
        if (confirm('Bạn có chắc muốn xóa toàn bộ bản lưu các hệ giải phẫu trong máy để giải phóng bộ nhớ?')) {
          await storageManager.clearAllCache();
          alert('Đã dọn dẹp bộ nhớ cache thành công!');
          await this.updateCacheStatsUI();
        }
      });
    }
  }

  async updateCacheStatsUI() {
    const stats = await storageManager.getStorageStats();
    const statsEl = document.getElementById('cache-stats-text');
    if (statsEl) {
      statsEl.innerText = `Đã lưu trên máy: ${stats.totalMB} MB (${stats.count} hệ)`;
    }

    for (const sys of this.systemsConfig) {
      const isCached = await storageManager.isCached(sys.id);
      const badge = document.getElementById(`badge-${sys.id}`);
      if (badge) {
        if (isCached) {
          badge.className = 'system-status-badge cached';
          badge.innerText = 'Đã lưu máy';
        } else {
          badge.className = 'system-status-badge not-cached';
          badge.innerText = `Chưa tải (${sys.sizeText})`;
        }
      }
    }
  }

  updateSystemToggleUI(systemId) {
    const sys = this.systemsConfig.find(s => s.id === systemId);
    if (!sys) return;
    const toggle = document.getElementById(`toggle-${systemId}`);
    if (toggle) toggle.checked = sys.visible;
  }

  applyFilters() {
    this.viewer.filterAcupoints((pt) => {
      const isExtra = pt.channel_id === 'EXTRA' || pt.code.startsWith('EX-') || pt.code.startsWith('EXTRA-') || pt.code.startsWith('M-') || pt.code.startsWith('N-');
      
      if (this.currentFilter === 'primary' && isExtra) return false;
      if (this.currentFilter === 'extra' && !isExtra) return false;
      if (this.selectedChannel && pt.channel_id !== this.selectedChannel) return false;

      return true;
    });
  }

  searchAcupoints(query) {
    if (!query) {
      this.applyFilters();
      return;
    }

    let firstMatch = null;
    this.viewer.filterAcupoints((pt) => {
      const match =
        pt.code.toLowerCase().includes(query) ||
        (pt.name_vi && pt.name_vi.toLowerCase().includes(query)) ||
        (pt.name_cn && pt.name_cn.includes(query)) ||
        (pt.pinyin && pt.pinyin.toLowerCase().includes(query)) ||
        (pt.indications && JSON.stringify(pt.indications).toLowerCase().includes(query)) ||
        (pt.location_detail && pt.location_detail.toLowerCase().includes(query));

      if (match && !firstMatch) firstMatch = pt;
      return match;
    });

    if (firstMatch && query.length >= 2) {
      this.viewer.selectAcupoint(firstMatch.code, false);
      this.showPointDetail(firstMatch);
    }
  }

  handlePointHover(point, event) {
    const tooltip = document.getElementById('hover-tooltip');
    if (!tooltip) return;

    if (!point) {
      tooltip.style.display = 'none';
      return;
    }

    tooltip.style.display = 'block';
    tooltip.style.left = `${event.clientX + 14}px`;
    tooltip.style.top = `${event.clientY - 14}px`;
    tooltip.innerHTML = `
      <div class="tooltip-title">${point.code} - ${point.name_vi} (${point.name_cn || ''})</div>
      <div class="tooltip-sub">${point.region || 'Huyệt vị'} | ${point.channel_id}</div>
    `;
  }

  showPointDetail(point) {
    const drawer = document.getElementById('acupoint-drawer');
    if (!drawer) return;

    drawer.classList.remove('closed');

    document.getElementById('dt-code').innerText = point.code || '';
    document.getElementById('dt-name-vi').innerText = point.name_vi || '';
    document.getElementById('dt-name-cn').innerText = `${point.name_cn || ''} (${point.pinyin || ''})`;
    document.getElementById('dt-channel').innerText = point.channel_id || '';
    document.getElementById('dt-region').innerText = point.region || 'Cơ thể';

    document.getElementById('dt-meaning').innerText = point.name_meaning || 'Đang cập nhật...';
    document.getElementById('dt-origin').innerText = point.origin || 'Kinh điển Y học cổ truyền';

    document.getElementById('dt-location').innerText = point.location_detail || 'Đang cập nhật...';
    document.getElementById('dt-anatomy').innerText = point.anatomy || 'Gồm các lớp da, cân mạc, bó mạch và dây thần kinh đi qua.';

    const indContainer = document.getElementById('dt-indications');
    indContainer.innerHTML = '';
    if (point.indications && Array.isArray(point.indications)) {
      point.indications.forEach((ind) => {
        const li = document.createElement('li');
        li.innerText = ind;
        indContainer.appendChild(li);
      });
    } else {
      indContainer.innerHTML = '<li>Trị bệnh theo đường kinh và tại chỗ.</li>';
    }

    document.getElementById('dt-puncture').innerText = point.puncture_guide || 'Châm thẳng hoặc xiên, sâu 0.3 - 0.8 thốn.';
    document.getElementById('dt-contraindications').innerText = point.contraindications || 'Cần nắm vững giải phẫu để đảm bảo an toàn tuyệt đối.';
    document.getElementById('dt-combinations').innerText = point.point_combinations || 'Phối hợp theo nguyên tắc Du - Mộ hoặc Ngũ Du Huyệt.';
  }
}

window.addEventListener('DOMContentLoaded', () => {
  const app = new NewAtlasApp();
  app.init();
  window.newAtlasApp = app;
});
