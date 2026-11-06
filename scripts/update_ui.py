import re

with open('/Volumes/D/Hoc Python/NewAtlas/web/index.html.bak', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Custom CSS styles for UI-UX upgrades
custom_styles = """
  <!-- UI-UX Professional Upgrades -->
  <style>
    /* Ẩn các nút rườm rà ở header cũ & hướng dẫn chuột bàn phím ở chân trang */
    .header-brand-contacts {
      display: none !important;
    }
    .viewport-hints {
      display: none !important;
    }

    /* Nút Trợ giúp & Q&A mới ở Header */
    .btn-header-help {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: rgba(30, 41, 59, 0.75);
      border: 1px solid rgba(148, 163, 184, 0.3);
      border-radius: 9999px;
      padding: 6px 14px;
      color: #e2e8f0;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
      backdrop-filter: blur(8px);
      -webkit-backdrop-filter: blur(8px);
      margin-left: 8px;
    }
    .btn-header-help:hover {
      background: rgba(56, 189, 248, 0.2);
      border-color: rgba(56, 189, 248, 0.6);
      color: #38bdf8;
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(56, 189, 248, 0.25);
    }
    .btn-header-help .help-icon {
      font-size: 14px;
    }

    /* Floating 3D Tools - Tối ưu thanh công cụ đỉnh màn hình */
    .floating-3d-tools {
      display: flex !important;
      align-items: center !important;
      gap: 8px !important;
      padding: 6px 12px !important;
      border-radius: 16px !important;
      background: rgba(11, 19, 32, 0.85) !important;
      backdrop-filter: blur(16px) !important;
      -webkit-backdrop-filter: blur(16px) !important;
      border: 1px solid rgba(56, 189, 248, 0.3) !important;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5) !important;
    }

    /* Nút Master Bóc Tách & Giải Phẫu */
    .anatomy-popover-wrapper {
      position: relative;
      display: inline-block;
    }
    .master-anatomy-btn {
      display: inline-flex !important;
      align-items: center !important;
      gap: 8px !important;
      background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.9)) !important;
      border: 1px solid rgba(56, 189, 248, 0.45) !important;
      border-radius: 12px !important;
      padding: 7px 14px !important;
      font-weight: 700 !important;
      color: #f8fafc !important;
      cursor: pointer;
      transition: all 0.2s ease !important;
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.3) !important;
    }
    .master-anatomy-btn:hover, .master-anatomy-btn.open {
      border-color: #38bdf8 !important;
      box-shadow: 0 0 16px rgba(56, 189, 248, 0.35) !important;
      background: rgba(30, 41, 59, 0.95) !important;
    }
    .master-anatomy-btn .menu-badge {
      background: rgba(56, 189, 248, 0.2);
      color: #38bdf8;
      font-size: 11px;
      font-weight: 800;
      padding: 2px 7px;
      border-radius: 9999px;
      border: 1px solid rgba(56, 189, 248, 0.4);
    }
    .master-anatomy-btn .menu-caret {
      font-size: 11px;
      color: #94a3b8;
      transition: transform 0.2s ease;
    }
    .master-anatomy-btn.open .menu-caret {
      transform: rotate(180deg);
    }

    /* Bảng điều khiển phân tầng trượt xuống (Popover Panel) */
    .anatomy-popover-panel {
      position: absolute;
      top: calc(100% + 10px);
      left: 0;
      width: 360px;
      max-width: 90vw;
      background: rgba(11, 19, 32, 0.96);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border: 1px solid rgba(56, 189, 248, 0.35);
      border-radius: 16px;
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.7), 0 0 25px rgba(56, 189, 248, 0.2);
      padding: 16px;
      z-index: 1000;
      display: none;
      opacity: 0;
      transform: translateY(-8px) scale(0.98);
      transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .anatomy-popover-panel.show {
      display: block;
      opacity: 1;
      transform: translateY(0) scale(1);
    }

    .popover-panel-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-bottom: 12px;
      border-bottom: 1px solid rgba(148, 163, 184, 0.15);
      margin-bottom: 14px;
    }
    .header-left {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .panel-icon {
      font-size: 18px;
    }
    .panel-title {
      font-size: 13px;
      font-weight: 800;
      letter-spacing: 0.05em;
      color: #38bdf8;
      text-transform: uppercase;
    }
    .btn-close-anatomy-popover {
      background: rgba(255, 255, 255, 0.08);
      border: none;
      color: #94a3b8;
      font-size: 20px;
      line-height: 1;
      width: 28px;
      height: 28px;
      border-radius: 8px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.15s ease;
    }
    .btn-close-anatomy-popover:hover {
      background: rgba(239, 68, 68, 0.2);
      color: #ef4444;
    }

    /* Thanh trượt độ trong suốt X-Ray */
    .skin-opacity-slider-card {
      background: rgba(15, 23, 42, 0.7);
      border: 1px solid rgba(56, 189, 248, 0.2);
      border-radius: 12px;
      padding: 12px;
      margin-bottom: 14px;
    }
    .slider-title-row {
      display: flex;
      justify-content: space-between;
      font-size: 12px;
      font-weight: 600;
      color: #cbd5e1;
      margin-bottom: 8px;
    }
    .opacity-val {
      color: #38bdf8;
      font-weight: 700;
      font-family: monospace;
    }
    .slider-control-row {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .slider-min, .slider-max {
      font-size: 11px;
      color: #64748b;
      font-weight: 500;
      white-space: nowrap;
    }
    .custom-range-slider {
      flex: 1;
      height: 6px;
      -webkit-appearance: none;
      background: #1e293b;
      border-radius: 9999px;
      outline: none;
    }
    .custom-range-slider::-webkit-slider-thumb {
      -webkit-appearance: none;
      width: 18px;
      height: 18px;
      border-radius: 50%;
      background: #38bdf8;
      box-shadow: 0 0 10px rgba(56, 189, 248, 0.8);
      cursor: pointer;
      transition: transform 0.15s ease;
    }
    .custom-range-slider::-webkit-slider-thumb:hover {
      transform: scale(1.2);
    }

    /* Lưới các tầng cơ thể */
    .anatomy-layers-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 8px;
      max-height: 52vh;
      overflow-y: auto;
      padding-right: 4px;
    }
    .anatomy-layers-grid::-webkit-scrollbar {
      width: 4px;
    }
    .anatomy-layers-grid::-webkit-scrollbar-thumb {
      background: rgba(148, 163, 184, 0.25);
      border-radius: 4px;
    }

    .layer-pill-toggle {
      display: flex !important;
      align-items: center !important;
      gap: 10px !important;
      padding: 10px 12px !important;
      background: rgba(15, 23, 42, 0.6) !important;
      border: 1px solid rgba(148, 163, 184, 0.15) !important;
      border-radius: 10px !important;
      color: #94a3b8 !important;
      cursor: pointer;
      text-align: left !important;
      transition: all 0.2s ease !important;
      position: relative;
      width: 100% !important;
      box-sizing: border-box;
    }
    .layer-pill-toggle:hover {
      background: rgba(30, 41, 59, 0.8) !important;
      border-color: rgba(56, 189, 248, 0.4) !important;
      color: #e2e8f0 !important;
    }
    .layer-pill-toggle.active {
      background: rgba(56, 189, 248, 0.15) !important;
      border-color: #38bdf8 !important;
      color: #f8fafc !important;
      box-shadow: 0 0 12px rgba(56, 189, 248, 0.18);
    }
    .layer-icon {
      font-size: 18px;
      flex-shrink: 0;
    }
    .layer-text-wrap {
      display: flex;
      flex-direction: column;
      flex: 1;
      min-width: 0;
    }
    .layer-title {
      font-size: 12.5px;
      font-weight: 700;
      color: #f8fafc;
      line-height: 1.2;
    }
    .layer-hint {
      font-size: 10.5px;
      color: #64748b;
      margin-top: 2px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .layer-pill-toggle.active .layer-hint {
      color: #7dd3fc;
    }
    .layer-status-dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: #334155;
      flex-shrink: 0;
      transition: all 0.2s ease;
    }
    .layer-pill-toggle.active .layer-status-dot {
      background: #38bdf8;
      box-shadow: 0 0 8px #38bdf8;
    }

    /* Master Acupoint & Label Mode Button */
    .master-acu-cycle-btn {
      background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.9)) !important;
      border: 1px solid rgba(245, 158, 11, 0.45) !important;
      border-radius: 12px !important;
      font-weight: 700 !important;
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.3) !important;
      padding: 7px 14px !important;
    }
    .master-acu-cycle-btn.active {
      border-color: #f59e0b !important;
      box-shadow: 0 0 16px rgba(245, 158, 11, 0.35) !important;
    }

    /* Toast Notification for View Mode Switching */
    .acu-mode-toast {
      position: fixed;
      top: 76px;
      left: 50%;
      transform: translateX(-50%) translateY(-10px);
      background: rgba(11, 19, 32, 0.96);
      border: 1px solid rgba(245, 158, 11, 0.6);
      color: #fef08a;
      padding: 9px 20px;
      border-radius: 9999px;
      font-size: 13.5px;
      font-weight: 700;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6), 0 0 15px rgba(245, 158, 11, 0.3);
      z-index: 9999;
      opacity: 0;
      pointer-events: none;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .acu-mode-toast.show {
      opacity: 1;
      transform: translateX(-50%) translateY(0);
    }

    /* Q&A Modal Styles */
    .qa-modal-overlay {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.8);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      z-index: 10000;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }
    .qa-modal-overlay.open {
      display: flex;
    }
    .qa-modal-card {
      width: 100%;
      max-width: 820px;
      max-height: 88vh;
      background: #0b1320;
      border: 1px solid rgba(56, 189, 248, 0.3);
      border-radius: 20px;
      box-shadow: 0 25px 60px rgba(0, 0, 0, 0.8), 0 0 30px rgba(56, 189, 248, 0.15);
      display: flex;
      flex-direction: column;
      position: relative;
      overflow: hidden;
      color: #f8fafc;
    }
    .qa-modal-close {
      position: absolute;
      top: 18px;
      right: 20px;
      background: rgba(255, 255, 255, 0.08);
      border: none;
      color: #94a3b8;
      font-size: 24px;
      width: 36px;
      height: 36px;
      border-radius: 50%;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.15s ease;
      z-index: 10;
    }
    .qa-modal-close:hover {
      background: rgba(239, 68, 68, 0.25);
      color: #ef4444;
    }
    .qa-modal-header {
      padding: 24px 28px 16px;
      border-bottom: 1px solid rgba(148, 163, 184, 0.15);
      background: linear-gradient(180deg, rgba(15, 23, 42, 0.8) 0%, rgba(11, 19, 32, 0) 100%);
    }
    .qa-header-badge {
      display: inline-block;
      font-size: 11px;
      font-weight: 800;
      letter-spacing: 0.08em;
      color: #38bdf8;
      background: rgba(56, 189, 248, 0.15);
      border: 1px solid rgba(56, 189, 248, 0.3);
      padding: 4px 10px;
      border-radius: 9999px;
      margin-bottom: 8px;
    }
    .qa-modal-header h3 {
      font-size: 20px;
      font-weight: 800;
      color: #f8fafc;
      margin: 0 0 6px;
    }
    .qa-header-sub {
      font-size: 13px;
      color: #94a3b8;
      margin: 0;
      line-height: 1.5;
    }
    .qa-search-box {
      display: flex;
      align-items: center;
      gap: 10px;
      margin: 16px 28px 10px;
      padding: 10px 16px;
      background: rgba(15, 23, 42, 0.8);
      border: 1px solid rgba(148, 163, 184, 0.25);
      border-radius: 12px;
    }
    .qa-search-box:focus-within {
      border-color: #38bdf8;
      box-shadow: 0 0 12px rgba(56, 189, 248, 0.2);
    }
    .qa-search-icon {
      font-size: 16px;
      color: #64748b;
    }
    .qa-search-box input {
      flex: 1;
      background: transparent;
      border: none;
      outline: none;
      color: #f8fafc;
      font-size: 14px;
    }
    .qa-accordion-list {
      padding: 10px 28px 24px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .qa-accordion-list::-webkit-scrollbar {
      width: 6px;
    }
    .qa-accordion-list::-webkit-scrollbar-thumb {
      background: rgba(148, 163, 184, 0.2);
      border-radius: 6px;
    }
    .qa-item {
      background: rgba(15, 23, 42, 0.65);
      border: 1px solid rgba(148, 163, 184, 0.15);
      border-radius: 12px;
      overflow: hidden;
      transition: all 0.2s ease;
    }
    .qa-item:hover {
      border-color: rgba(56, 189, 248, 0.35);
    }
    .qa-item.open {
      border-color: rgba(56, 189, 248, 0.5);
      background: rgba(15, 23, 42, 0.9);
    }
    .qa-question-btn {
      width: 100%;
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 14px 18px;
      background: transparent;
      border: none;
      color: #f1f5f9;
      font-size: 14px;
      font-weight: 700;
      text-align: left;
      cursor: pointer;
      outline: none;
    }
    .q-icon {
      font-size: 18px;
      flex-shrink: 0;
    }
    .q-text {
      flex: 1;
    }
    .q-arrow {
      font-size: 14px;
      color: #64748b;
      transition: transform 0.25s ease;
    }
    .qa-item.open .q-arrow {
      transform: rotate(180deg);
      color: #38bdf8;
    }
    .qa-answer-body {
      padding: 0 18px 16px 48px;
      font-size: 13.5px;
      line-height: 1.65;
      color: #cbd5e1;
      display: none;
    }
    .qa-item.open .qa-answer-body {
      display: block;
    }
    .qa-answer-body p {
      margin: 0 0 8px;
    }
    .qa-answer-body ul, .qa-answer-body ol {
      margin: 4px 0 8px;
      padding-left: 20px;
    }
    .qa-answer-body li {
      margin-bottom: 6px;
    }
    .qa-answer-body code {
      background: rgba(56, 189, 248, 0.15);
      color: #38bdf8;
      padding: 2px 6px;
      border-radius: 4px;
      font-family: monospace;
    }
    .qa-link {
      color: #38bdf8;
      text-decoration: none;
      font-weight: 600;
    }
    .qa-link:hover {
      text-decoration: underline;
    }

    /* Thêm các nút phụ vào modal tài khoản nhanh */
    .user-profile-quick-actions .btn-quick-qa {
      background: rgba(56, 189, 248, 0.12) !important;
      border: 1px solid rgba(56, 189, 248, 0.3) !important;
      color: #38bdf8 !important;
    }
    .user-profile-quick-actions .btn-quick-qa:hover {
      background: rgba(56, 189, 248, 0.22) !important;
      border-color: #38bdf8 !important;
    }
    .user-profile-quick-actions .btn-quick-brand {
      background: rgba(16, 185, 129, 0.12) !important;
      border: 1px solid rgba(16, 185, 129, 0.3) !important;
      color: #34d399 !important;
    }
    .user-profile-quick-actions .btn-quick-brand:hover {
      background: rgba(16, 185, 129, 0.22) !important;
      border-color: #34d399 !important;
    }

    /* Mobile Responsive Optimizations */
    @media (max-width: 768px) {
      .anatomy-popover-panel {
        position: fixed;
        top: auto;
        bottom: 0;
        left: 0;
        width: 100%;
        max-width: 100vw;
        border-radius: 20px 20px 0 0;
        padding: 20px;
        box-shadow: 0 -10px 40px rgba(0, 0, 0, 0.85);
      }
      .anatomy-layers-grid {
        grid-template-columns: 1fr;
        max-height: 48vh;
      }
      .floating-3d-tools {
        top: 68px;
        max-width: 96vw;
        padding: 5px 10px !important;
      }
      .master-anatomy-btn {
        padding: 6px 12px !important;
      }
      .master-anatomy-btn .btn-text {
        font-size: 12px;
      }
      .btn-header-help .help-label {
        display: none;
      }
    }
  </style>
"""

# Insert custom styles before </head>
html = html.replace('</head>', custom_styles + '\n</head>')

# 2. Header adjustments:
# Add btnHeaderHelp and remove header-brand-contacts
header_old = """        <!-- Vi An Y Quán Brand & Terms Quick Nav -->
        <div class="header-brand-contacts">
          <button class="hdr-brand-info-btn" id="btnOpenBrandModal" title="Giới thiệu Vi An Y Quán, Hotline & Kênh hỗ trợ">
            ℹ️ Giới thiệu & Hotline
          </button>
          <button class="hdr-brand-info-btn" id="btnOpenTermsModal" title="Điều khoản dịch vụ & Miễn trừ trách nhiệm y tế">
            📜 Điều khoản
          </button>
        </div>

        <!-- Membership & Admin Quick Controls -->
        <div class="header-membership-group" id="headerMembershipGroup">
          <!-- Populated by JS: Login, Upgrade VIP, or Admin Badge -->
        </div>"""

header_new = """        <!-- Membership Controls -->
        <div class="header-membership-group" id="headerMembershipGroup">
          <!-- Populated by JS: Login, Upgrade VIP, or Admin Badge -->
        </div>

        <!-- Nút Trợ giúp & Q&A / Hotline / Điều khoản -->
        <button class="btn-header-help" id="btnHeaderHelp" title="Trung tâm Trợ giúp, Hỏi - Đáp (Q&A), Hotline & Điều khoản">
          <span class="help-icon">❓</span>
          <span class="help-label">Trợ giúp & Q&A</span>
        </button>"""

if header_old in html:
    html = html.replace(header_old, header_new)
else:
    print("WARNING: header_old not exact match, using regex replacement")
    html = re.sub(r'<!-- Vi An Y Quán Brand & Terms Quick Nav -->.*?<div class="header-membership-group" id="headerMembershipGroup">.*?</div>', header_new, html, flags=re.DOTALL)

# 3. Replace floating-3d-tools horizontal buttons with Master Anatomy Popover
floating_old_pattern = r'<div class="floating-3d-tools" id="floating3DTools">.*?<!-- Cụm 1: Giải phẫu Đa tầng.*?</div>\s*<div class="tool-divider"></div>'

floating_new = """<div class="floating-3d-tools" id="floating3DTools">
          <!-- Nút Dropdown Master: Bóc Tách & Giải Phẫu Đa Tầng -->
          <div class="anatomy-popover-wrapper" id="anatomyPopoverWrapper">
            <button class="icon-toggle master-anatomy-btn" id="btnMasterAnatomyMenu"
              title="Nhấp để mở bảng điều khiển 7 hệ giải phẫu & Bóc tách đa tầng">
              <span class="mode-icon">🧬</span>
              <span class="btn-text">Bóc Tách & Giải Phẫu</span>
              <span class="menu-badge" id="anatomyActiveBadge">3/7</span>
              <span class="menu-caret">▾</span>
            </button>

            <!-- Popover Menu xổ xuống chứa toàn bộ 7 hệ cơ quan & Bóc tách -->
            <div class="anatomy-popover-panel" id="anatomyPopoverPanel">
              <div class="popover-panel-header">
                <div class="header-left">
                  <span class="panel-icon">🧬</span>
                  <span class="panel-title">BÓC TÁCH & GIẢI PHẪU ĐA TẦNG</span>
                </div>
                <button class="btn-close-anatomy-popover" id="btnCloseAnatomyPopover">&times;</button>
              </div>

              <!-- Thanh trượt độ trong suốt X-Ray của Da -->
              <div class="skin-opacity-slider-card">
                <div class="slider-title-row">
                  <span>🧘 Độ mờ lớp Da (X-Ray xuyên thấu)</span>
                  <span class="opacity-val" id="skinOpacityVal">35%</span>
                </div>
                <div class="slider-control-row">
                  <span class="slider-min">Xuyên thấu</span>
                  <input type="range" id="skinOpacityRange" min="0" max="100" value="35" class="custom-range-slider" />
                  <span class="slider-max">Da đặc</span>
                </div>
              </div>

              <!-- Danh sách lưới các tầng cơ thể -->
              <div class="anatomy-layers-grid">
                <button class="layer-pill-toggle active" id="btnToggleSkin"
                  title="Click để chuyển đổi: Da mờ ➔ Da đặc ➔ Ẩn da">
                  <span class="layer-icon">🧘</span>
                  <div class="layer-text-wrap">
                    <span class="layer-title" id="skinToggleText">Da mờ</span>
                    <span class="layer-hint">Biểu mô & Vỏ bọc</span>
                  </div>
                  <span class="layer-status-dot"></span>
                </button>

                <button class="layer-pill-toggle" id="btnToggleMuscles"
                  title="Hệ Cơ Bắp (177 bó cơ Z-Anatomy: Cơ Nông & Cơ Sâu)">
                  <span class="layer-icon">💪</span>
                  <div class="layer-text-wrap">
                    <span class="layer-title">Cơ bắp</span>
                    <span class="layer-hint">177 bó cơ</span>
                  </div>
                  <span class="layer-status-dot"></span>
                </button>

                <button class="layer-pill-toggle" id="btnToggleSkeleton"
                  title="Khung Xương (242 cấu trúc xương Z-Anatomy)">
                  <span class="layer-icon">🦴</span>
                  <div class="layer-text-wrap">
                    <span class="layer-title">Khung xương</span>
                    <span class="layer-hint">242 mốc xương</span>
                  </div>
                  <span class="layer-status-dot"></span>
                </button>

                <button class="layer-pill-toggle" id="btnToggleNerves"
                  title="Hệ Thần Kinh (Tủy sống, rễ gai sống, đám rối, thần kinh chi)">
                  <span class="layer-icon">⚡</span>
                  <div class="layer-text-wrap">
                    <span class="layer-title">Thần kinh</span>
                    <span class="layer-hint">Tủy & Dây thần kinh</span>
                  </div>
                  <span class="layer-status-dot"></span>
                </button>

                <button class="layer-pill-toggle" id="btnToggleOrgans"
                  title="Lục Phủ Ngũ Tạng (Tim, Phổi, Gan, Tỳ, Vị, Thận, v.v.)">
                  <span class="layer-icon">🫀</span>
                  <div class="layer-text-wrap">
                    <span class="layer-title">Nội tạng</span>
                    <span class="layer-hint">Lục phủ ngũ tạng</span>
                  </div>
                  <span class="layer-status-dot"></span>
                </button>

                <button class="layer-pill-toggle" id="btnToggleLymphatic"
                  title="Hệ Bạch Huyết (220 Cụm Hạch Bạch Huyết & Mạch Bạch Huyết)">
                  <span class="layer-icon">🟢</span>
                  <div class="layer-text-wrap">
                    <span class="layer-title">Bạch huyết</span>
                    <span class="layer-hint">220 hạch & mạch</span>
                  </div>
                  <span class="layer-status-dot"></span>
                </button>

                <button class="layer-pill-toggle" id="btnToggleVessels"
                  title="Hệ Tuần Hoàn (714 Mạch Máu Động & Tĩnh Mạch)">
                  <span class="layer-icon">🩸</span>
                  <div class="layer-text-wrap">
                    <span class="layer-title">Mạch máu</span>
                    <span class="layer-hint">714 động & tĩnh mạch</span>
                  </div>
                  <span class="layer-status-dot"></span>
                </button>

                <button class="layer-pill-toggle btn-dissection-accent" id="btnToggleDissection"
                  title="Studio Bóc Tách Đa Tầng & Dao Mổ Số (Phím tắt: Shift+D)">
                  <span class="layer-icon">🔬</span>
                  <div class="layer-text-wrap">
                    <span class="layer-title">Dao mổ số</span>
                    <span class="layer-hint">Studio bóc tách</span>
                  </div>
                  <span class="layer-status-dot"></span>
                </button>
              </div>
            </div>
          </div>

          <div class="tool-divider"></div>"""

html = re.sub(floating_old_pattern, floating_new, html, flags=re.DOTALL)

# 4. Remove viewport-hints
html = re.sub(r'<!-- Viewport Floating Helpers \(Mouse & Trackpad Instructions\) -->\s*<div class="viewport-hints">.*?</div>', '<!-- Viewport Hints removed for clean UI -->', html, flags=re.DOTALL)

# 5. Add Toast container and Q&A Modal before </body>
qa_modal_html = """
  <!-- Toast thông báo chuyển chế độ hiển thị huyệt -->
  <div class="acu-mode-toast" id="acuModeToast">
    <span id="acuToastIcon">🏷️</span>
    <span id="acuToastText">Đang hiển thị: Tên Việt</span>
  </div>

  <!-- Modal: Hỏi - Đáp Thường Gặp (Q&A) & Trung Tâm Hỗ Trợ -->
  <div class="qa-modal-overlay" id="qaModalOverlay">
    <div class="qa-modal-card">
      <button class="qa-modal-close" id="btnCloseQAModal" title="Đóng">&times;</button>
      
      <div class="qa-modal-header">
        <div class="qa-header-badge">❓ TRUNG TÂM TRỢ GIÚP & HỎI ĐÁP (Q&A)</div>
        <h3>Câu Hỏi Thường Gặp Khi Sử Dụng AcuAtlas 3D Pro</h3>
        <p class="qa-header-sub">
          Hướng dẫn thao tác 3D bóc tách, tra cứu 419 huyệt đạo, kích hoạt tài khoản VIP và kết nối chuyên gia YHCT.
        </p>
      </div>

      <!-- Khung tìm kiếm câu hỏi nhanh -->
      <div class="qa-search-box">
        <span class="qa-search-icon">🔍</span>
        <input type="text" id="qaSearchInput" placeholder="Tìm kiếm câu hỏi (ví dụ: bóc tách, VIP, thiết bị, hotline...)" autocomplete="off" />
      </div>

      <!-- Danh sách câu hỏi Accordion FAQ -->
      <div class="qa-accordion-list" id="qaAccordionList">
        
        <!-- Câu 1 -->
        <div class="qa-item" data-keywords="tim huyet phong to camera zoom tra cuu">
          <button class="qa-question-btn">
            <span class="q-icon">🎯</span>
            <span class="q-text">1. Làm sao để tìm kiếm và phóng to nhanh đến một huyệt vị bất kỳ?</span>
            <span class="q-arrow">▾</span>
          </button>
          <div class="qa-answer-body">
            <p>
              Bạn chỉ cần sử dụng thanh tìm kiếm ở góc trên bên trái, gõ <strong>tên tiếng Việt</strong> (có dấu hoặc không dấu, ví dụ: <code>hop coc</code>, <code>Hợp Cốc</code>) hoặc <strong>mã WHO quốc tế</strong> (như <code>LI4</code>, <code>ST36</code>, <code>LR3</code>). Bạn cũng có thể tìm theo triệu chứng bệnh (ví dụ: <code>đau đầu</code>, <code>mất ngủ</code>, <code>dạ dày</code>).
            </p>
            <p>
              Nhấp vào kết quả tìm kiếm, camera 3D sẽ <strong>tự động bay và phóng to cận cảnh</strong> đến đúng mốc giải phẫu của huyệt đó, đồng thời mở bảng chi tiết thông tin y học ở cột bên phải.
            </p>
          </div>
        </div>

        <!-- Câu 2 -->
        <div class="qa-item" data-keywords="boc tach da tang he co quan giai phau da co xuong noi tang mach mau bach huyet">
          <button class="qa-question-btn">
            <span class="q-icon">🧬</span>
            <span class="q-text">2. Cách bóc tách các tầng cơ thể (Da, Cơ bắp, Xương, Thần kinh, Tạng, Bạch huyết, Mạch máu)?</span>
            <span class="q-arrow">▾</span>
          </button>
          <div class="qa-answer-body">
            <p>
              Nhấp vào nút <strong>"🧬 Bóc Tách & Giải Phẫu"</strong> ở thanh công cụ phía trên màn hình để mở bảng điều khiển phân tầng. Tại đây bạn có thể:
            </p>
            <ul>
              <li><strong>Lớp Da:</strong> Điều chỉnh thanh trượt độ mờ X-Ray từ 0% (xuyên thấu) đến 100% (da đặc).</li>
              <li><strong>Hệ Cơ Bắp:</strong> Bật/tắt 177 bó cơ Z-Anatomy (cơ nông và cơ sâu).</li>
              <li><strong>Khung Xương:</strong> Bật/tắt 242 cấu trúc xương làm mốc định vị huyệt.</li>
              <li><strong>Thần Kinh, Nội Tạng, Bạch Huyết & Mạch Máu:</strong> Bật/tắt theo nhu cầu khảo sát lâm sàng.</li>
              <li><strong>Dao Mổ Số (Studio Bóc Tách):</strong> Nhấp vào để bật chế độ mổ xẻ tương tác (phím tắt <code>Shift + D</code>), cho phép click trực tiếp vào từng thớ cơ hoặc tạng phủ để bóc tách ra.</li>
            </ul>
          </div>
        </div>

        <!-- Câu 3 -->
        <div class="qa-item" data-keywords="che do huyet ma so ten viet an huyet label">
          <button class="qa-question-btn">
            <span class="q-icon">🏷️</span>
            <span class="q-text">3. Cách thay đổi chế độ hiển thị Tên tiếng Việt, Mã số WHO và Ẩn/Hiện huyệt?</span>
            <span class="q-arrow">▾</span>
          </button>
          <div class="qa-answer-body">
            <p>
              Nhấp vào nút <strong>"🏷️ Chế độ Huyệt"</strong> trên thanh công cụ nổi 3D. Mỗi lần nhấp sẽ xoay vòng qua 4 chế độ thông minh:
            </p>
            <ol>
              <li><strong>Tên Việt:</strong> Hiển thị chấm huyệt + Tên tiếng Việt rõ ràng (ví dụ: <code>Hợp Cốc</code>).</li>
              <li><strong>Mã & Tên:</strong> Hiển thị Mã WHO quốc tế kết hợp Tên (ví dụ: <code>LI4 Hợp Cốc</code>).</li>
              <li><strong>Chỉ Điểm Huyệt:</strong> Chỉ hiện các chấm phát sáng 3D, ẩn chữ để ngắm nhìn cơ thể thoáng đãng.</li>
              <li><strong>Ẩn Tất Cả Huyệt:</strong> Ẩn toàn bộ huyệt để bạn tập trung 100% quan sát giải phẫu cơ thể.</li>
            </ol>
          </div>
        </div>

        <!-- Câu 4 -->
        <div class="qa-item" data-keywords="nang cap vip dang ky chuyen khoan vietqr gia tien">
          <button class="qa-question-btn">
            <span class="q-icon">⚡</span>
            <span class="q-text">4. Đăng ký và kích hoạt Gói Hội Viên VIP như thế nào?</span>
            <span class="q-arrow">▾</span>
          </button>
          <div class="qa-answer-body">
            <p>
              1. Bấm nút <strong>"⚡ Nâng Cấp VIP"</strong> ở góc phải trên cùng.<br>
              2. Chọn gói bạn muốn: <strong>Gói 1 Năm</strong> hoặc <strong>Gói Trọn Đời</strong>.<br>
              3. Hệ thống sẽ tự động tạo mã <strong>VietQR động</strong> chứa chính xác số tiền và mã nội dung chuyển khoản riêng của bạn.<br>
              4. Mở app ngân hàng quét mã và xác nhận chuyển khoản. Hệ thống sẽ tự động duyệt mở khóa VIP trong vòng <strong>1 – 5 phút</strong>.<br>
              <em>* Nếu cần kích hoạt gấp, bạn có thể gọi hotline/Zalo: <strong>0936.380.666</strong> để được duyệt tức thì.</em>
            </p>
          </div>
        </div>

        <!-- Câu 5 -->
        <div class="qa-item" data-keywords="goi 1 nam tron doi khac nhau quyen loi">
          <button class="qa-question-btn">
            <span class="q-icon">⭐</span>
            <span class="q-text">5. Gói Hội Viên 1 Năm khác gì Gói VIP Trọn Đời?</span>
            <span class="q-arrow">▾</span>
          </button>
          <div class="qa-answer-body">
            <p>
              Cả hai gói đều mở khóa <strong>100% ĐẦY ĐỦ TÍNH NĂNG NHƯ NHAU</strong>: Trọn bộ 419 huyệt vị YHCT, 50 phác đồ điều trị đa thể bệnh, toàn bộ 7 hệ giải phẫu bóc tách Z-Anatomy và tính toán chu chuyển khí huyết Tý Ngọ Lưu Chú.
            </p>
            <p>
              <strong>Điểm khác biệt duy nhất:</strong> Gói 1 Năm có thời hạn sử dụng 365 ngày; Gói Trọn Đời chỉ thanh toán 1 lần duy nhất, dùng vĩnh viễn và được <strong>cập nhật miễn phí tất cả bệnh lý, tính năng và mô hình 3D mới</strong> trong tương lai.
            </p>
          </div>
        </div>

        <!-- Câu 6 -->
        <div class="qa-item" data-keywords="thiet bi dien thoai ipad may tinh toi da 3">
          <button class="qa-question-btn">
            <span class="q-icon">📱</span>
            <span class="q-text">6. Một tài khoản VIP được dùng trên bao nhiêu thiết bị?</span>
            <span class="q-arrow">▾</span>
          </button>
          <div class="qa-answer-body">
            <p>
              Mỗi tài khoản VIP cá nhân được đăng nhập và sử dụng đồng thời trên <strong>tối đa 03 (ba) thiết bị cá nhân</strong> (ví dụ: 1 Điện thoại + 1 iPad/Máy tính bảng + 1 Máy tính bàn/Laptop) phục vụ nhu cầu học tập và công tác linh hoạt của chính chủ.
            </p>
            <p>
              Hệ thống nghiêm cấm việc chia sẻ công khai hoặc bán lại tài khoản cho bên thứ ba.
            </p>
          </div>
        </div>

        <!-- Câu 7 -->
        <div class="qa-item" data-keywords="cai dat pwa dien thoai iphone android app man hinh chinh">
          <button class="qa-question-btn">
            <span class="q-icon">📲</span>
            <span class="q-text">7. Cách cài ứng dụng ra màn hình chính điện thoại như App (PWA)?</span>
            <span class="q-arrow">▾</span>
          </button>
          <div class="qa-answer-body">
            <p>
              Ứng dụng hỗ trợ công nghệ <strong>Progressive Web App (PWA)</strong> chạy mượt mà toàn màn hình không có thanh địa chỉ trình duyệt:
            </p>
            <ul>
              <li><strong>Trên iPhone / iPad (trình duyệt Safari):</strong> Nhấp vào nút <strong>Chia sẻ (Share)</strong> ở thanh dưới ➔ Chọn <strong>"Thêm vào Màn hình chính" (Add to Home Screen)</strong> ➔ Bấm Thêm.</li>
              <li><strong>Trên Android (trình duyệt Chrome):</strong> Nhấp vào biểu tượng <strong>3 chấm</strong> ở góc trên bên phải ➔ Chọn <strong>"Cài đặt ứng dụng"</strong> hoặc <strong>"Thêm vào màn hình chính"</strong>.</li>
            </ul>
          </div>
        </div>

        <!-- Câu 8 -->
        <div class="qa-item" data-keywords="lien he hotline ho tro ky thuat chuyen mon vi an y quan">
          <button class="qa-question-btn">
            <span class="q-icon">📞</span>
            <span class="q-text">8. Tôi cần hỗ trợ kỹ thuật hoặc tư vấn chuyên môn YHCT thì liên hệ ai?</span>
            <span class="q-arrow">▾</span>
          </button>
          <div class="qa-answer-body">
            <p>
              Đội ngũ Vi An Y Quán và Tác giả luôn sẵn sàng đồng hành cùng bạn:
            </p>
            <ul>
              <li><strong>Hotline / Zalo:</strong> <a href="tel:0936380666" class="qa-link"><strong>0936.380.666</strong></a> (Thầy thuốc Trịnh Tiến Đạt)</li>
              <li><strong>Email:</strong> <a href="mailto:tiendat.trinh@gmail.com" class="qa-link">tiendat.trinh@gmail.com</a></li>
              <li><strong>Website chính thức:</strong> <a href="https://vianyquan.trinhtiendat.com" target="_blank" rel="noopener noreferrer" class="qa-link">vianyquan.trinhtiendat.com</a></li>
              <li><strong>Kênh YouTube học thuật:</strong> <a href="https://www.youtube.com/@ViAnYQuan" target="_blank" rel="noopener noreferrer" class="qa-link">@ViAnYQuan</a></li>
            </ul>
          </div>
        </div>

      </div>
    </div>
  </div>
"""

# 6. Interactive Module Script
interactive_script = """
  <!-- Module Quản Lý UI/UX Nâng Cấp: Bóc Tách Đa Tầng, Chu Kỳ Huyệt & Q&A -->
  <script type="module">
    // -------------------------------------------------------------
    // A. QUẢN LÝ BẢNG BÓC TÁCH & GIẢI PHẪU (POPOVER DROPDOWN)
    // -------------------------------------------------------------
    const btnMasterAnatomyMenu = document.getElementById('btnMasterAnatomyMenu');
    const anatomyPopoverPanel = document.getElementById('anatomyPopoverPanel');
    const btnCloseAnatomyPopover = document.getElementById('btnCloseAnatomyPopover');
    const anatomyActiveBadge = document.getElementById('anatomyActiveBadge');
    const skinOpacityRange = document.getElementById('skinOpacityRange');
    const skinOpacityVal = document.getElementById('skinOpacityVal');

    function toggleAnatomyPopover(show = null) {
      if (!anatomyPopoverPanel) return;
      const willShow = show !== null ? show : !anatomyPopoverPanel.classList.contains('show');
      anatomyPopoverPanel.classList.toggle('show', willShow);
      btnMasterAnatomyMenu?.classList.toggle('open', willShow);
    }

    btnMasterAnatomyMenu?.addEventListener('click', (e) => {
      e.stopPropagation();
      toggleAnatomyPopover();
    });

    btnCloseAnatomyPopover?.addEventListener('click', (e) => {
      e.stopPropagation();
      toggleAnatomyPopover(false);
    });

    document.addEventListener('click', (e) => {
      if (!e.target.closest('#anatomyPopoverWrapper')) {
        toggleAnatomyPopover(false);
      }
    });

    // Cập nhật số lượng hệ giải phẫu đang kích hoạt trên badge (ví dụ: 3/7)
    function updateActiveLayersCount() {
      if (!anatomyActiveBadge) return;
      const layerBtns = [
        'btnToggleSkin',
        'btnToggleMuscles',
        'btnToggleSkeleton',
        'btnToggleNerves',
        'btnToggleOrgans',
        'btnToggleLymphatic',
        'btnToggleVessels'
      ];
      let activeCount = 0;
      layerBtns.forEach(id => {
        const btn = document.getElementById(id);
        if (btn && btn.classList.contains('active')) {
          activeCount++;
        }
      });
      anatomyActiveBadge.textContent = `${activeCount}/7`;
    }

    // Lắng nghe thay đổi trạng thái các tầng
    const observer = new MutationObserver(() => {
      updateActiveLayersCount();
    });
    [
      'btnToggleSkin',
      'btnToggleMuscles',
      'btnToggleSkeleton',
      'btnToggleNerves',
      'btnToggleOrgans',
      'btnToggleLymphatic',
      'btnToggleVessels'
    ].forEach(id => {
      const el = document.getElementById(id);
      if (el) observer.observe(el, { attributes: true, attributeFilter: ['class'] });
    });
    setTimeout(updateActiveLayersCount, 500);

    // Thanh trượt độ mờ lớp Da (X-Ray Opacity Slider)
    skinOpacityRange?.addEventListener('input', (e) => {
      const val = parseInt(e.target.value, 10);
      const opacity = val / 100;
      if (skinOpacityVal) skinOpacityVal.textContent = `${val}%`;

      // Cập nhật trực tiếp lên mô hình da 3D
      if (window.humanModel) {
        window.humanModel.traverse((child) => {
          if (child.isMesh && child.material) {
            child.material.transparent = opacity < 0.99;
            child.material.opacity = opacity;
            child.material.depthWrite = opacity >= 0.99;
            child.material.needsUpdate = true;
          }
        });
      }
      if (window.dissectionStudio && typeof window.dissectionStudio.setSkinOpacity === 'function') {
        window.dissectionStudio.setSkinOpacity(opacity);
      }
      const skinBtn = document.getElementById('btnToggleSkin');
      const skinText = document.getElementById('skinToggleText');
      if (skinBtn && skinText) {
        if (val === 0) {
          skinBtn.classList.remove('active');
          skinText.textContent = 'Ẩn da';
        } else if (val >= 95) {
          skinBtn.classList.add('active');
          skinText.textContent = 'Da đặc';
        } else {
          skinBtn.classList.add('active');
          skinText.textContent = 'Da mờ';
        }
      }
    });

    // -------------------------------------------------------------
    // B. MASTER NÚT XOAY VÒNG CHẾ ĐỘ HUYỆT VỊ & NHÃN (4 CHẾ ĐỘ)
    // -------------------------------------------------------------
    const btnCycleLabel = document.getElementById('btnCycleLabelMode');
    const cycleLabelIcon = document.getElementById('cycleLabelIcon');
    const cycleLabelText = document.getElementById('cycleLabelText');
    const acuModeToast = document.getElementById('acuModeToast');
    const acuToastIcon = document.getElementById('acuToastIcon');
    const acuToastText = document.getElementById('acuToastText');

    let toastTimer = null;
    function showAcuToast(icon, text) {
      if (!acuModeToast) return;
      if (acuToastIcon) acuToastIcon.textContent = icon;
      if (acuToastText) acuToastText.textContent = text;
      acuModeToast.classList.add('show');
      clearTimeout(toastTimer);
      toastTimer = setTimeout(() => {
        acuModeToast.classList.remove('show');
      }, 2200);
    }

    // 4 Chế độ: 
    // 0: 'vi_only' (Chấm huyệt + Tên Việt)
    // 1: 'code_and_vi' (Chấm huyệt + Mã WHO & Tên Việt)
    // 2: 'dots_only' (Chỉ chấm huyệt phát sáng, ẩn nhãn chữ)
    // 3: 'all_hidden' (Ẩn toàn bộ chấm huyệt + nhãn để tập trung giải phẫu)
    let masterAcuMode = 0;
    const acuModes = [
      { id: 'vi_only', icon: '🏷️', label: 'Tên Việt', toast: 'Đang hiển thị: Tên tiếng Việt' },
      { id: 'code_and_vi', icon: '🔢', label: 'Mã & Tên', toast: 'Đang hiển thị: Mã WHO & Tên Việt' },
      { id: 'dots_only', icon: '📍', label: 'Chỉ Điểm', toast: 'Đang hiển thị: Chỉ chấm huyệt (Ẩn chữ)' },
      { id: 'all_hidden', icon: '👁️‍🗨️', label: 'Ẩn Huyệt', toast: 'Đã ẩn toàn bộ huyệt (Tập trung Giải Phẫu)' }
    ];

    function applyAcuMode(modeIndex) {
      masterAcuMode = modeIndex % acuModes.length;
      const cur = acuModes[masterAcuMode];
      if (cycleLabelIcon) cycleLabelIcon.textContent = cur.icon;
      if (cycleLabelText) cycleLabelText.textContent = cur.label;
      showAcuToast(cur.icon, cur.toast);

      // Điều khiển các đối tượng trong Three.js Scene
      if (window.threeScene) {
        window.threeScene.traverse((child) => {
          // Điểm huyệt (Mesh)
          if (child.isMesh && child.userData && child.userData.code) {
            child.visible = cur.id !== 'all_hidden';
          }
          // Nhãn chữ (Sprite)
          if (child.isSprite && child.userData && (child.userData.isLabel || child.userData.code)) {
            if (cur.id === 'all_hidden' || cur.id === 'dots_only') {
              child.visible = false;
            } else {
              child.visible = true;
            }
          }
        });
      }
    }

    // Đè event click lên btnCycleLabelMode
    btnCycleLabel?.addEventListener('click', (e) => {
      // Cho script gốc chạy 1 lượt nếu cần, sau đó chúng ta đồng bộ hóa
      setTimeout(() => {
        applyAcuMode(masterAcuMode + 1);
      }, 50);
    }, true);

    // -------------------------------------------------------------
    // C. QUẢN LÝ MODAL HỎI - ĐÁP (Q&A) & ĐIỀU HƯỚNG TÀI KHOẢN
    // -------------------------------------------------------------
    const qaModal = document.getElementById('qaModalOverlay');
    const btnCloseQAModal = document.getElementById('btnCloseQAModal');
    const btnHeaderHelp = document.getElementById('btnHeaderHelp');
    const qaSearchInput = document.getElementById('qaSearchInput');
    const qaItems = document.querySelectorAll('.qa-item');

    function openQAModal() {
      if (qaModal) qaModal.classList.add('open');
    }
    function closeQAModal() {
      if (qaModal) qaModal.classList.remove('open');
    }

    btnHeaderHelp?.addEventListener('click', openQAModal);
    btnCloseQAModal?.addEventListener('click', closeQAModal);
    qaModal?.addEventListener('click', (e) => {
      if (e.target === qaModal) closeQAModal();
    });

    // Accordion toggle
    document.querySelectorAll('.qa-question-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const item = btn.closest('.qa-item');
        if (item) item.classList.toggle('open');
      });
    });

    // Tìm kiếm trong Q&A
    qaSearchInput?.addEventListener('input', (e) => {
      const q = e.target.value.toLowerCase().trim();
      qaItems.forEach(item => {
        const text = (item.textContent + ' ' + (item.dataset.keywords || '')).toLowerCase();
        if (!q || text.includes(q)) {
          item.style.display = 'block';
        } else {
          item.style.display = 'none';
        }
      });
    });

    // -------------------------------------------------------------
    // D. TỰ ĐỘNG CHÈN NÚT "GIỚI THIỆU", "ĐIỀU KHOẢN", "Q&A" VÀO MODAL TÀI KHOẢN
    // -------------------------------------------------------------
    function enhanceQuickProfileModal() {
      const profileModal = document.getElementById('userProfileQuickModal');
      if (!profileModal) return;
      const actionsBox = profileModal.querySelector('.user-profile-quick-actions');
      if (!actionsBox || actionsBox.querySelector('#btnQuickInjectedQA')) return;

      // Tạo nút Q&A
      const btnQA = document.createElement('button');
      btnQA.className = 'btn-quick-menu-action btn-quick-qa';
      btnQA.id = 'btnQuickInjectedQA';
      btnQA.innerHTML = '<span>❓ Hỏi - Đáp Thường Gặp (Q&A)</span>';
      btnQA.onclick = () => {
        profileModal.remove();
        openQAModal();
      };

      // Tạo nút Giới thiệu & Hotline
      const btnBrand = document.createElement('button');
      btnBrand.className = 'btn-quick-menu-action btn-quick-brand';
      btnBrand.id = 'btnQuickInjectedBrand';
      btnBrand.innerHTML = '<span>ℹ️ Giới Thiệu Vi An Y Quán & Hotline</span>';
      btnBrand.onclick = () => {
        profileModal.remove();
        document.getElementById('brandModalOverlay')?.classList.add('open');
      };

      // Chèn lên trước nút Đăng xuất
      const logoutBtn = actionsBox.querySelector('#btnQuickLogout');
      if (logoutBtn) {
        actionsBox.insertBefore(btnBrand, logoutBtn);
        actionsBox.insertBefore(btnQA, logoutBtn);
      } else {
        actionsBox.appendChild(btnBrand);
        actionsBox.appendChild(btnQA);
      }
    }

    // Quan sát DOM khi modal tài khoản mở ra
    const bodyObserver = new MutationObserver((mutations) => {
      for (const m of mutations) {
        for (const node of m.addedNodes) {
          if (node.id === 'userProfileQuickModal' || (node.querySelector && node.querySelector('#userProfileQuickModal'))) {
            setTimeout(enhanceQuickProfileModal, 50);
          }
        }
      }
    });
    bodyObserver.observe(document.body, { childList: true, subtree: true });

    // Hỗ trợ phím Escape đóng Q&A
    window.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && qaModal?.classList.contains('open')) {
        closeQAModal();
      }
    });
  </script>
"""

# Insert modal and script before </body>
html = html.replace('</body>', qa_modal_html + '\n' + interactive_script + '\n</body>')

with open('/Volumes/D/Hoc Python/NewAtlas/web/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("SUCCESS: web/index.html updated successfully with all 5 UI-UX requirements!")

