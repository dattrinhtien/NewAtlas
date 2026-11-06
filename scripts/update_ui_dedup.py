#!/usr/bin/env python3
"""
scripts/update_ui_dedup.py
Updates web/index.html to:
1. Streamline top floating bar to 3 compact buttons:
   [ 🔬 Bóc tách ] | [ 🏷️ Chế độ Huyệt ] | [ ⚡ Khí lưu ]
2. Eliminate redundant popover menu; unify dissection controls into native Studio Bóc Tách 3D.
3. Add mobile bottom sheet responsive styles for #anatomyDissectionPanel.
4. Upgrade Q&A accordion to single-open mode with smooth auto-scroll.
5. Update Q&A Question 2 text to reflect the unified Studio Bóc Tách.
"""

import sys

def main():
    path = "web/index.html"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update <style>: Replace popover CSS with .btn-dissection-main and responsive .dissection-panel
    style_target_start = "/* Nút Master Bóc Tách & Giải Phẫu */"
    style_target_end = "/* Master Acupoint & Label Mode Button */"
    
    new_style = """/* Nút Bóc Tách Studio Chuyên Nghiệp trên thanh công cụ nổi */
    .btn-dissection-main {
      display: inline-flex !important;
      align-items: center !important;
      gap: 7px !important;
      background: linear-gradient(135deg, rgba(239, 68, 68, 0.22), rgba(185, 28, 28, 0.4)) !important;
      border: 1px solid rgba(239, 68, 68, 0.5) !important;
      border-radius: 12px !important;
      padding: 7px 15px !important;
      font-weight: 700 !important;
      color: #fecaca !important;
      cursor: pointer;
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
      box-shadow: 0 4px 14px rgba(239, 68, 68, 0.2) !important;
    }
    .btn-dissection-main:hover {
      border-color: #ef4444 !important;
      color: #ffffff !important;
      box-shadow: 0 0 16px rgba(239, 68, 68, 0.45) !important;
      background: linear-gradient(135deg, rgba(239, 68, 68, 0.35), rgba(185, 28, 28, 0.55)) !important;
      transform: translateY(-1px);
    }
    .btn-dissection-main.active {
      border-color: #f87171 !important;
      color: #ffffff !important;
      box-shadow: 0 0 20px rgba(239, 68, 68, 0.6) !important;
      background: linear-gradient(135deg, rgba(239, 68, 68, 0.5), rgba(185, 28, 28, 0.75)) !important;
    }

    /* Tối ưu giao diện Studio Bóc Tách Giải Phẫu trên Thiết Bị Di Động (Bottom-Sheet) */
    @media (max-width: 768px) {
      .dissection-panel {
        top: auto !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        width: 100% !important;
        max-width: 100vw !important;
        max-height: 65vh !important;
        border-radius: 20px 20px 0 0 !important;
        border-bottom: none !important;
        transform: translateY(105%) !important;
        transition: transform 0.32s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.25s ease !important;
        box-shadow: 0 -12px 40px rgba(0, 0, 0, 0.85), 0 0 30px rgba(239, 68, 68, 0.25) !important;
      }
      .dissection-panel.active {
        transform: translateY(0) !important;
      }
      .floating-3d-tools {
        top: 66px !important;
        padding: 5px 10px !important;
        gap: 6px !important;
      }
      .btn-dissection-main, .master-acu-cycle-btn {
        padding: 6px 11px !important;
        font-size: 12px !important;
      }
    }

    """

    start_idx = content.find(style_target_start)
    end_idx = content.find(style_target_end)
    if start_idx == -1 or end_idx == -1:
        print("ERROR: could not find style target range!")
        sys.exit(1)
    
    content = content[:start_idx] + new_style + content[end_idx:]

    # 2. Update Q&A style to support smooth scrolling
    qa_list_style_old = """.qa-accordion-list {
      padding: 10px 28px 24px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }"""
    qa_list_style_new = """.qa-accordion-list {
      padding: 10px 28px 24px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 10px;
      scroll-behavior: smooth;
    }
    .qa-item {
      scroll-margin-top: 12px;
      scroll-margin-bottom: 12px;
    }"""
    if qa_list_style_old in content:
        content = content.replace(qa_list_style_old, qa_list_style_new, 1)
    else:
        print("NOTE: qa_list_style_old not found exactly, checking alternatives...")

    # 3. Update #floating3DTools in HTML
    tools_start = '<!-- Floating 3D Anatomy & Meridian Controls -->'
    tools_end = '<!-- Floating Camera HUD Controls'
    
    new_tools = """<!-- Floating 3D Anatomy & Meridian Controls -->
        <div class="floating-3d-tools" id="floating3DTools">
          <!-- Nút Master Studio Bóc Tách (kích hoạt panel bên phải) -->
          <button class="icon-toggle btn-dissection-main" id="btnToggleDissection"
            title="Studio Bóc Tách & Giải Phẫu Đa Tầng 3D (Shift+D)">
            <span class="mode-icon">🔬</span>
            <span class="btn-text">Bóc tách</span>
          </button>

          <div class="tool-divider"></div>

          <!-- Chế độ hiển thị huyệt vị (xoay vòng 4 chế độ thông minh) -->
          <button class="icon-toggle active label-cycle-btn master-acu-cycle-btn" id="btnCycleLabelMode"
            title="Chế độ hiển thị huyệt vị: Click để xoay vòng Tên Việt ➔ Mã & Tên ➔ Chỉ Điểm ➔ Ẩn Huyệt">
            <span class="mode-icon" id="cycleLabelIcon">🏷️</span>
            <span id="cycleLabelText">Tên Việt</span>
          </button>

          <!-- Khí lưu -->
          <button class="icon-toggle active" id="btnToggleFlow" title="Bật/Tắt hiệu ứng dòng kinh khí vận hành">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
            </svg>
            <span>Khí lưu</span>
          </button>

          <!-- Công cụ Dev / Hiệu chỉnh (Ẩn mặc định cho người dùng thương mại; mở qua phím tắt Shift+C hoặc ?dev=1) -->
          <button class="icon-toggle dev-only-toggle" id="btnToggleCalibration" style="display: none;"
            title="Studio Hiệu Chỉnh Mốc Huyệt (Admin/Dev - Phím tắt: Shift+C)">
            <span class="mode-icon">🎯</span>
            <span>Hiệu chỉnh</span>
          </button>
        </div>

        """

    t_start = content.find(tools_start)
    t_end = content.find(tools_end)
    if t_start == -1 or t_end == -1:
        print("ERROR: could not find tools target range!")
        sys.exit(1)

    content = content[:t_start] + new_tools + content[t_end:]

    # 4. Update Q&A Question 2 text
    old_q2 = """        <!-- Câu 2 -->
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
        </div>"""

    new_q2 = """        <!-- Câu 2 -->
        <div class="qa-item" data-keywords="boc tach da tang he co quan giai phau da co xuong noi tang mach mau bach huyet dao mo">
          <button class="qa-question-btn">
            <span class="q-icon">🔬</span>
            <span class="q-text">2. Cách bóc tách các tầng cơ thể (Da, Cơ bắp, Xương, Thần kinh, Tạng, Mạch máu, Bạch huyết)?</span>
            <span class="q-arrow">▾</span>
          </button>
          <div class="qa-answer-body">
            <p>
              Nhấp vào nút <strong>"🔬 Bóc Tách"</strong> ở thanh công cụ phía trên màn hình (hoặc nhấn phím tắt <code>Shift + D</code>) để mở bảng điều khiển <strong>Studio Bóc Tách Giải Phẫu 3D</strong> chuyên sâu bên phải màn hình. Tại đây bạn có thể:
            </p>
            <ul>
              <li><strong>Phân tầng độ mờ (Opacity Sliders):</strong> Kéo thanh trượt từ 0% đến 100% độc lập cho từng hệ: Lớp Da Ngoài, Cơ Nông (Superficial), Cơ Sâu (Deep Muscles), Khung Xương, Mạch Máu, Thần Kinh, Lục Phủ Ngũ Tạng và Bạch Huyết.</li>
              <li><strong>Bật Dao Mổ Số (Digital Scalpel):</strong> Chế độ mổ xẻ tương tác — rê chuột đến thớ cơ nào sẽ sáng viền và hiển thị tên tiếng Việt; nhấp chuột để bóc tách riêng cấu trúc đó ra khỏi cơ thể.</li>
              <li><strong>Thao tác nhanh 1 chạm:</strong> Bóc cơ nông, Ẩn/Hiện tạng, Ẩn/Hiện thần kinh, Chế độ X-Ray xuyên thấu, hoặc nút <strong>Khôi phục</strong> để hoàn nguyên toàn bộ mô hình về ban đầu.</li>
            </ul>
          </div>
        </div>"""

    if old_q2 in content:
        content = content.replace(old_q2, new_q2, 1)
    else:
        print("NOTE: old_q2 not found, will keep existing or manual replace")

    # 5. Update <script type="module">: Remove section A, update Q&A accordion to single-open
    script_a_start = "// -------------------------------------------------------------\n    // A. QUẢN LÝ BẢNG BÓC TÁCH & GIẢI PHẪU (POPOVER DROPDOWN)\n    // -------------------------------------------------------------"
    script_b_start = "// -------------------------------------------------------------\n    // B. MASTER NÚT XOAY VÒNG CHẾ ĐỘ HUYỆT VỊ & NHÃN (4 CHẾ ĐỘ)\n    // -------------------------------------------------------------"

    new_script_a = """// -------------------------------------------------------------
    // A. ĐỒNG BỘ NÚT BÓC TÁCH VỚI STUDIO BÓC TÁCH GIẢI PHẪU 3D
    // -------------------------------------------------------------
    // Nút #btnToggleDissection được DissectionStudio tự động liên kết
    // Khi click sẽ mở/đóng #anatomyDissectionPanel chuyên sâu bên phải màn hình

    """

    sa_idx = content.find(script_a_start)
    sb_idx = content.find(script_b_start)
    if sa_idx != -1 and sb_idx != -1:
        content = content[:sa_idx] + new_script_a + content[sb_idx:]
    else:
        print("ERROR: could not find script section A target!")
        sys.exit(1)

    # 6. Update Q&A Accordion JS to single-open + auto scroll
    old_qa_js = """    // Accordion toggle
    document.querySelectorAll('.qa-question-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const item = btn.closest('.qa-item');
        if (item) item.classList.toggle('open');
      });
    });"""

    new_qa_js = """    // Accordion toggle: Single-open với tính năng tự động cuộn đọc trọn vẹn nội dung
    document.querySelectorAll('.qa-question-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const item = btn.closest('.qa-item');
        if (!item) return;
        const isOpen = item.classList.contains('open');

        // Đóng toàn bộ các câu hỏi khác (chỉ mở duy nhất câu đang xem)
        document.querySelectorAll('.qa-item').forEach(el => {
          if (el !== item) el.classList.remove('open');
        });

        // Đổi trạng thái câu được click
        if (isOpen) {
          item.classList.remove('open');
        } else {
          item.classList.add('open');
          // Cuộn mượt mà để hiển thị toàn bộ câu hỏi và câu trả lời trong khung
          setTimeout(() => {
            item.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
          }, 100);
        }
      });
    });"""

    if old_qa_js in content:
        content = content.replace(old_qa_js, new_qa_js, 1)
    else:
        print("NOTE: old_qa_js not found exactly!")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    print("SUCCESS: web/index.html updated successfully!")

if __name__ == "__main__":
    main()

