with open('web/js/dissectionStudio.js', 'r', encoding='utf-8') as f:
    code = f.read()

# Update displayInfoCard badge
old_card_badges = """    if (data.isBone) {
      badge = '🦴 KHUNG XƯƠNG (242 XƯƠNG)'; ic = '🦴'; bg = 'rgba(148,163,184,0.2)'; col = '#e2e8f0';
    } else if (data.isOrgan) {
      badge = '🫀 LỤC PHỦ NGŨ TẠNG'; ic = '🫀'; bg = 'rgba(239,68,68,0.2)'; col = '#f87171';
    } else if (data.isNerve) {
      badge = '⚡ DÂY THẦN KINH (Z-ANATOMY)'; ic = '⚡'; bg = 'rgba(234,179,8,0.2)'; col = '#facc15';
    } else if (data.layer === 'deep') {
      badge = '🥩 LỚP CƠ SÂU'; ic = '🥩'; bg = 'rgba(244,63,94,0.2)'; col = '#fb7185';
    }"""

new_card_badges = """    if (data.isBone) {
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
    }"""

if old_card_badges in code:
    code = code.replace(old_card_badges, new_card_badges, 1)
    print("Updated badges in displayInfoCard")

# Update displayInfoCard details
old_card_details = """    } else if (data.isBone) {
      if (data.type) details += `<div class="card-prop-row"><span class="prop-label">🦴 Phân loại hình thái:</span><span class="prop-val">${data.type}</span></div>`;
      if (data.landmarks) details += `<div class="card-prop-row"><span class="prop-label">📍 Mốc mấu giải phẫu then chốt:</span><span class="prop-val">${data.landmarks}</span></div>`;
      if (data.note) details += `<div class="card-prop-row highlight-action"><span class="prop-label">⚡ Vị trí & Cơ năng giải phẫu:</span><span class="prop-val">${data.note}</span></div>`;
      if (data.acupoints) details += `<div class="card-prop-row highlight-acupoint"><span class="prop-label">🏮 Mốc định vị Huyệt Đạo YHCT:</span><span class="prop-val">${data.acupoints}</span></div>`;
    } else {"""

new_card_details = """    } else if (data.isBone) {
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
    } else {"""

if old_card_details in code:
    code = code.replace(old_card_details, new_card_details, 1)
    print("Updated details in displayInfoCard")

# Update showTooltip badges
old_tt_badges = """    if (data.isBone) {
      badge = '🦴 KHUNG XƯƠNG (Z-ANATOMY)';
      icon = '🦴';
    } else if (data.isOrgan) {
      badge = '🫀 LỤC PHỦ NGŨ TẠNG (Z-ANATOMY)';
      icon = '🫀';
    } else if (data.isNerve) {
      badge = '⚡ DÂY THẦN KINH (Z-ANATOMY)';
      icon = '⚡';
    } else if (data.layer === 'deep') {
      badge = '🥩 LỚP CƠ SÂU';
      icon = '🥩';
    }"""

new_tt_badges = """    if (data.isBone) {
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
    }"""

if old_tt_badges in code:
    code = code.replace(old_tt_badges, new_tt_badges, 1)
    print("Updated badges in showTooltip")

# Update showTooltip details
old_tt_details = """    } else if (data.isBone) {
      if (data.type) details += `<div style="margin-top:4px;font-size:11px;color:#cbd5e1;line-height:1.35;">🦴 <strong>Phân loại:</strong> ${data.type}</div>`;
      if (data.landmarks) details += `<div style="margin-top:3px;font-size:11px;color:#93c5fd;line-height:1.35;">📍 <strong>Mốc mấu:</strong> ${data.landmarks}</div>`;
      if (data.note) details += `<div style="margin-top:3px;font-size:11px;color:#cbd5e1;line-height:1.35;">⚡ <strong>Cơ năng:</strong> ${data.note}</div>`;
      if (data.acupoints) details += `<div style="margin-top:4px;font-size:11px;color:#fef08a;background:rgba(234,179,8,0.18);padding:3px 7px;border-radius:4px;line-height:1.35;">🏮 <strong>Mốc định vị Huyệt:</strong> ${data.acupoints}</div>`;
    } else {"""

new_tt_details = """    } else if (data.isBone) {
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
    } else {"""

if old_tt_details in code:
    code = code.replace(old_tt_details, new_tt_details, 1)
    print("Updated details in showTooltip")

with open('web/js/dissectionStudio.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Saved dissectionStudio.js cards and tooltips!")
