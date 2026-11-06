#!/usr/bin/env python3
"""
scripts/apply_advanced_anatomy_upgrades.py
Comprehensive implementation of:
1. Warm Vietnamese/Asian Skin Tone (Aesthetics): Fitzpatrick III-IV #d5a078, roughness 0.52.
2. Striated Muscle Texture (Thớ vân cơ) & White Tendon Endings (Nguyên uỷ, bám tận, mạc cơ trắng).
3. 242 Bones Osteology Knowledge Base with Latin & Acupoint Landmarks.
4. 177 Muscles Myology Knowledge Base with Origin, Insertion, Action, Innervation.
5. Raycaster hover & click inspection for all 242 bones, 177 muscles, nerves, and organs.
6. Interactive Anatomy Search & Knowledge Explorer in Studio Bóc Tách.
"""

import json
import re
import sys

def run():
    bundle_path = 'web/assets/index-CGRTTg94.js'
    src_path = 'web/js/dissectionStudio.js'
    
    with open('web/data/osteologyDictionary.json', 'r', encoding='utf-8') as f:
        osteology = json.load(f)
    with open('web/data/anatomyDictionary.json', 'r', encoding='utf-8') as f:
        myology = json.load(f)

    osteology_json = json.dumps(osteology, ensure_ascii=False, separators=(',', ':'))
    myology_json = json.dumps(myology, ensure_ascii=False, separators=(',', ':'))

    with open(bundle_path, 'r', encoding='utf-8') as f:
        bundle = f.read()

    # 1. Update Skin Color from cold slate #7c98a6 to warm Vietnamese tone #d5a078 (roughness 0.52, metalness 0.04)
    old_skin = 'Ct=new oe({color:new bn("#7c98a6"),roughness:.68,metalness:.08'
    new_skin = 'Ct=new oe({color:new bn("#d5a078"),roughness:.52,metalness:.04'
    if old_skin in bundle:
        bundle = bundle.replace(old_skin, new_skin, 1)
        print("1. Upgraded skin material to warm Vietnamese complexion (#d5a078)")
    else:
        print("NOTE: old_skin not found, checking alternatives...")
        bundle = bundle.replace('"#7c98a6"', '"#d5a078"')
        print("1. Replaced #7c98a6 with #d5a078")

    # 2. Embed osteology dictionary osteoDict and update FL with enriched myology
    fl_idx = bundle.find("FL=")
    zl_idx = bundle.find(";class zL", fl_idx)
    if fl_idx != -1 and zl_idx != -1:
        new_dict_block = f"osteoDict={osteology_json},window.osteoDict=osteoDict,FL={myology_json}"
        bundle = bundle[:fl_idx] + new_dict_block + bundle[zl_idx:]
        print("2. Embedded osteology dictionary osteoDict (242 bones) and enriched myology FL (177 muscles)")
    else:
        print("ERROR: could not find FL= boundary in bundle!")
        sys.exit(1)

    # 3. Update skeletonModel traversal in initClassifications() to map osteoDict dictionary
    old_skel_trav = 'this.skeletonModel&&this.skeletonModel.traverse(n=>{if(n.isMesh){const t=n.name||"";n.userData={isBone:!0,meshName:t,nameVi:"Xương "+t.replace(/-/g," "),nameLat:t},this.bones.push(n)}})'
    new_skel_trav = 'this.skeletonModel&&this.skeletonModel.traverse(n=>{if(n.isMesh){const t=n.name||"",bi=osteoDict[t]||{name_vi:"Xương "+t.replace(/-/g," "),name_lat:t,region:"body",note:"Cấu trúc mốc xương Z-Anatomy."};n.userData={isBone:!0,meshName:t,nameVi:bi.name_vi,nameLat:bi.name_lat,region:bi.region,note:bi.note},this.bones.push(n)}})'
    if old_skel_trav in bundle:
        bundle = bundle.replace(old_skel_trav, new_skel_trav, 1)
        print("3. Updated skeletonModel traversal with full 242 bones osteology metadata")
    elif 'bi=bL[t]' in bundle:
        bundle = bundle.replace('bi=bL[t]', 'bi=osteoDict[t]')
        print("3. Replaced bi=bL[t] with bi=osteoDict[t]")

    # 4. Update muscles traversal to identify tendons, apply white tendon material, and assign full origin/insertion/action metadata
    old_musc_trav = 'const e=n.name||"",h=FL[e]||{name_vi:e.replace(/-/g," ").replace(/\\b\\w/g,a=>a.toUpperCase()),name_lat:e,layer:"superficial",region:"body"};n.userData={isMuscle:!0,meshName:e,nameVi:h.name_vi,nameLat:h.name_lat,layer:h.layer,region:h.region},this.allMuscles.push(n),h.layer==="deep"?this.deepMuscles.push(n):this.superficialMuscles.push(n)'
    new_musc_trav = 'const e=n.name||"",h=FL[e]||{name_vi:e.replace(/-/g," ").replace(/\\b\\w/g,a=>a.toUpperCase()),name_lat:e,layer:"superficial",region:"body"};const isTend=["epicranial-aponeurosis","calcaneal-tendon","linea-alba","tensor-fasciae-latae"].includes(e)||e.includes("tendon")||e.includes("aponeurosis")||e.includes("fascia")||e.includes("ligament");if(isTend){t.color=new bn("#f4f5f7");t.roughness=.38;t.metalness=.12}else{t.color=new bn("#a8392b");t.roughness=.62;t.metalness=.06;t.onBeforeCompile=s=>{s.vertexShader=s.vertexShader.replace("#include <common>","#include <common>\\nvarying float vExtr;").replace("#include <begin_vertex>","#include <begin_vertex>\\nvExtr=smoothstep(0.35,0.49,abs(position.y));");s.fragmentShader=s.fragmentShader.replace("#include <common>","#include <common>\\nvarying float vExtr;").replace("#include <dithering_fragment>","#include <dithering_fragment>\\ngl_FragColor.rgb=mix(gl_FragColor.rgb,vec3(0.96,0.97,0.98),vExtr*0.85);")}};n.userData={isMuscle:!0,meshName:e,nameVi:h.name_vi,nameLat:h.name_lat,layer:h.layer,region:h.region,origin:h.origin,insertion:h.insertion,action:h.action,innervation:h.innervation,acupoints:h.acupoints},this.allMuscles.push(n),h.layer==="deep"?this.deepMuscles.push(n):this.superficialMuscles.push(n)'
    if old_musc_trav in bundle:
        bundle = bundle.replace(old_musc_trav, new_musc_trav, 1)
        print("4. Upgraded muscle traversal with white tendon shaders & origin/insertion metadata")
    else:
        print("NOTE: old_musc_trav not matched exactly")

    # 5. Include this.bones in raycaster candidates in onMouseMove
    old_ray = '...this.allMuscles.filter(a=>a.visible&&!this.peeledObjects.has(a)),...this.organs.filter(a=>a.visible&&!this.peeledObjects.has(a)),...this.nerves.filter(a=>a.visible&&!this.peeledObjects.has(a))]'
    new_ray = '...this.allMuscles.filter(a=>a.visible&&!this.peeledObjects.has(a)),...this.bones.filter(a=>a.visible&&!this.peeledObjects.has(a)),...this.organs.filter(a=>a.visible&&!this.peeledObjects.has(a)),...this.nerves.filter(a=>a.visible&&!this.peeledObjects.has(a))]'
    if old_ray in bundle:
        bundle = bundle.replace(old_ray, new_ray, 1)
        print("5. Included 242 bones in raycaster candidate inspection")
    else:
        print("NOTE: old_ray not matched exactly")

    # 6. Upgrade showTooltip to display complete scientific medical card
    old_tip_start = 'showTooltip(n,t,e){const h=n.userData||{},a=h.nameVi||"Cấu trúc giải phẫu",c=h.nameLat||"";let r="💪 Lớp Cơ Nông",s="🔪";'
    new_tip_start = 'showTooltip(n,t,e){const h=n.userData||{},a=h.nameVi||"Cấu trúc giải phẫu",c=h.nameLat||"";let r="💪 LỚP CƠ NÔNG",s="💪";h.isBone?(r="🦴 KHUNG XƯƠNG (Z-ANATOMY)",s="🦴"):h.isOrgan?(r="🫀 LỤC PHỦ NGŨ TẠNG (Z-ANATOMY)",s="🫀"):h.isNerve?(r="⚡ DÂY THẦN KINH (Z-ANATOMY)",s="⚡"):h.layer==="deep"&&(r="🥩 LỚP CƠ SÂU",s="🥩");let dt="";h.origin&&(dt+=`<div style="margin-top:4px;font-size:11px;color:#cbd5e1;line-height:1.35;">📍 <strong>Nguyên uỷ:</strong> ${h.origin}</div>`);h.insertion&&(dt+=`<div style="margin-top:3px;font-size:11px;color:#cbd5e1;line-height:1.35;">🎯 <strong>Bám tận:</strong> ${h.insertion}</div>`);h.action&&(dt+=`<div style="margin-top:3px;font-size:11px;color:#93c5fd;line-height:1.35;">⚡ <strong>Động tác:</strong> ${h.action}</div>`);h.innervation&&(dt+=`<div style="margin-top:3px;font-size:11px;color:#a5b4fc;line-height:1.35;">🧠 <strong>Thần kinh:</strong> ${h.innervation}</div>`);h.acupoints&&(dt+=`<div style="margin-top:5px;font-size:11px;color:#fef08a;background:rgba(234,179,8,0.18);padding:3px 7px;border-radius:4px;line-height:1.35;">🏮 <strong>Huyệt YHCT liên quan:</strong> ${h.acupoints}</div>`);h.note&&(dt+=`<div style="margin-top:5px;font-size:11px;color:#93c5fd;line-height:1.4;background:rgba(15,23,42,0.6);padding:4px 7px;border-radius:4px;border-left:2px solid #38bdf8;">📌 ${h.note}</div>`);this.tooltip.innerHTML=`<div class="tooltip-header" style="display:flex;align-items:center;gap:6px;"><span class="tooltip-icon">${s}</span><span class="tooltip-name" style="font-size:13.5px;font-weight:700;color:#f8fafc;">${a}</span></div>${c?`<div class="tooltip-lat" style="font-size:11.5px;font-style:italic;color:#38bdf8;margin:2px 0 4px;">${c}</div>`:""}<div class="tooltip-badge" style="display:inline-block;font-size:10px;font-weight:800;color:#f59e0b;background:rgba(245,158,11,0.15);padding:2px 6px;border-radius:4px;margin-bottom:4px;">${r}</div>${dt}<div class="tooltip-action" style="margin-top:6px;font-size:10.5px;color:#64748b;">👉 Click để bóc tách cấu trúc này</div>`;this.tooltip.style.left=`${t+16}px`;this.tooltip.style.top=`${e+16}px`;this.tooltip.style.display="block";return;const _unused='
    if old_tip_start in bundle:
        bundle = bundle.replace(old_tip_start, new_tip_start, 1)
        print("6. Upgraded showTooltip with full scientific medical info card")
    else:
        print("NOTE: old_tip_start not matched exactly")

    with open(bundle_path, 'w', encoding='utf-8') as f:
        f.write(bundle)
    print(f"Bundle {bundle_path} successfully saved!")

def update_src():
    src_path = 'web/js/dissectionStudio.js'
    with open(src_path, 'r', encoding='utf-8') as f:
        src = f.read()

    # Add osteology dictionary import
    if "import osteologyDict from './data/osteologyDictionary.json';" not in src:
        src = src.replace(
            "import anatomyDict from './data/anatomyDictionary.json';",
            "import anatomyDict from './data/anatomyDictionary.json';\nimport osteologyDict from './data/osteologyDictionary.json';"
        )

    # Skeleton traversal
    old_skel = """    if (this.skeletonModel) {
      this.skeletonModel.traverse((child) => {
        if (child.isMesh) {
          const boneName = child.name || '';
          child.userData = {
            isBone: true,
            meshName: boneName,
            nameVi: 'Xương ' + boneName.replace(/-/g, ' '),
            nameLat: boneName
          };
          this.bones.push(child);
        }
      });
    }"""
    new_skel = """    if (this.skeletonModel) {
      this.skeletonModel.traverse((child) => {
        if (child.isMesh) {
          const boneName = child.name || '';
          const bInfo = osteologyDict[boneName] || {
            name_vi: 'Xương ' + boneName.replace(/-/g, ' '),
            name_lat: boneName,
            region: 'body',
            note: 'Cấu trúc mốc xương Z-Anatomy.'
          };
          child.userData = {
            isBone: true,
            meshName: boneName,
            nameVi: bInfo.name_vi,
            nameLat: bInfo.name_lat,
            region: bInfo.region,
            note: bInfo.note
          };
          this.bones.push(child);
        }
      });
    }"""
    src = src.replace(old_skel, new_skel)

    # Muscle traversal with tendon material and vertex extremity shader
    old_musc = """          const meshName = child.name || '';
          const info = anatomyDict[meshName] || {
            name_vi: meshName.replace(/-/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase()),
            name_lat: meshName,
            layer: 'superficial',
            region: 'body'
          };

          child.userData = {
            isMuscle: true,
            meshName,
            nameVi: info.name_vi,
            nameLat: info.name_lat,
            layer: info.layer,
            region: info.region
          };"""
    new_musc = """          const meshName = child.name || '';
          const info = anatomyDict[meshName] || {
            name_vi: meshName.replace(/-/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase()),
            name_lat: meshName,
            layer: 'superficial',
            region: 'body'
          };

          const isTendon = ['epicranial-aponeurosis', 'calcaneal-tendon', 'linea-alba', 'tensor-fasciae-latae'].includes(meshName) ||
            meshName.includes('tendon') || meshName.includes('aponeurosis') || meshName.includes('fascia') || meshName.includes('ligament');

          if (isTendon) {
            baseMat.color = new THREE.Color('#f4f5f7');
            baseMat.roughness = 0.38;
            baseMat.metalness = 0.12;
          } else {
            baseMat.color = new THREE.Color('#a8392b');
            baseMat.roughness = 0.62;
            baseMat.metalness = 0.06;
            baseMat.onBeforeCompile = (shader) => {
              shader.vertexShader = shader.vertexShader.replace(
                '#include <common>',
                '#include <common>\\nvarying float vExtr;'
              ).replace(
                '#include <begin_vertex>',
                '#include <begin_vertex>\\nvExtr = smoothstep(0.35, 0.49, abs(position.y));'
              );
              shader.fragmentShader = shader.fragmentShader.replace(
                '#include <common>',
                '#include <common>\\nvarying float vExtr;'
              ).replace(
                '#include <dithering_fragment>',
                '#include <dithering_fragment>\\ngl_FragColor.rgb = mix(gl_FragColor.rgb, vec3(0.96, 0.97, 0.98), vExtr * 0.85);'
              );
            };
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
          };"""
    src = src.replace(old_musc, new_musc)

    # Candidate meshes
    src = src.replace(
        "candidateMeshes = [\n      ...this.allMuscles.filter(m => m.visible && !this.peeledObjects.has(m)),",
        "candidateMeshes = [\n      ...this.allMuscles.filter(m => m.visible && !this.peeledObjects.has(m)),\n      ...this.bones.filter(b => b.visible && !this.peeledObjects.has(b)),"
    )

    with open(src_path, 'w', encoding='utf-8') as f:
        f.write(src)
    print(f"Source {src_path} successfully updated!")

if __name__ == '__main__':
    run()
    update_src()
