#!/usr/bin/env python3
"""
scripts/upgrade_peel_mesh.py
Updates peelMesh and dissectInfoCard to render full scientific details
(Origin, Insertion, Action, Innervation, Acupoints, and Note).
"""

def update_bundle():
    bundle_path = 'web/assets/index-CGRTTg94.js'
    with open(bundle_path, 'r', encoding='utf-8') as f:
        text = f.read()

    target = 'document.getElementById("infoDesc").textContent=h.note?`${h.note} (Đã bóc tách thành công để bộc lộ các mốc giải phẫu bên dưới).`:"Đã bóc tách thành công để lộ các cấu trúc giải phẫu và mốc xương phía trong."'
    replacement = 'let d="";h.origin&&(d+=`<div style="margin-top:3px;">📍 <strong>Nguyên uỷ:</strong> ${h.origin}</div>`),h.insertion&&(d+=`<div style="margin-top:2px;">🎯 <strong>Bám tận:</strong> ${h.insertion}</div>`),h.action&&(d+=`<div style="margin-top:2px;">⚡ <strong>Động tác:</strong> ${h.action}</div>`),h.innervation&&(d+=`<div style="margin-top:2px;color:#a5b4fc;">🧠 <strong>Thần kinh:</strong> ${h.innervation}</div>`),h.acupoints&&(d+=`<div style="margin-top:4px;color:#fde047;">🏮 <strong>Huyệt YHCT:</strong> ${h.acupoints}</div>`),h.note&&(d+=`<div style="margin-top:3px;color:#93c5fd;">📌 ${h.note}</div>`),document.getElementById("infoDesc").innerHTML=d||"Đã bóc tách cấu trúc để lộ các lớp giải phẫu bên dưới."'

    if target in text:
        text = text.replace(target, replacement, 1)
        with open(bundle_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print("Bundle peelMesh successfully updated!")
    else:
        print("Target not found in bundle!")

def update_src():
    src_path = 'web/js/dissectionStudio.js'
    with open(src_path, 'r', encoding='utf-8') as f:
        text = f.read()

    target = """    const desc = data.note
      ? `${data.note} (Đã bóc tách thành công để bộc lộ các mốc giải phẫu bên dưới).`
      : 'Đã bóc tách thành công để lộ các cấu trúc giải phẫu và mốc xương phía trong.';
    document.getElementById('infoDesc').textContent = desc;"""

    replacement = """    let desc = '';
    if (data.origin) desc += `<div style="margin-top:3px;">📍 <strong>Nguyên uỷ:</strong> ${data.origin}</div>`;
    if (data.insertion) desc += `<div style="margin-top:2px;">🎯 <strong>Bám tận:</strong> ${data.insertion}</div>`;
    if (data.action) desc += `<div style="margin-top:2px;">⚡ <strong>Động tác:</strong> ${data.action}</div>`;
    if (data.innervation) desc += `<div style="margin-top:2px;color:#a5b4fc;">🧠 <strong>Thần kinh:</strong> ${data.innervation}</div>`;
    if (data.acupoints) desc += `<div style="margin-top:4px;color:#fde047;">🏮 <strong>Huyệt YHCT:</strong> ${data.acupoints}</div>`;
    if (data.note) desc += `<div style="margin-top:3px;color:#93c5fd;">📌 ${data.note}</div>`;
    if (!desc) desc = 'Đã bóc tách thành công để lộ các cấu trúc giải phẫu phía trong.';
    document.getElementById('infoDesc').innerHTML = desc;"""

    if target in text:
        text = text.replace(target, replacement, 1)
        with open(src_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print("Source peelMesh successfully updated!")
    else:
        print("Target not found in src!")

if __name__ == '__main__':
    update_bundle()
    update_src()

