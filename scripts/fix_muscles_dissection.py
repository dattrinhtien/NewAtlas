#!/usr/bin/env python3
"""
scripts/fix_muscles_dissection.py
Fixes muscle layer controls (Lớp cơ nông & Lớp cơ sâu) in:
1. web/assets/index-CGRTTg94.js (production bundle)
2. web/js/dissectionStudio.js (source file)

Key fixes:
1. Update dictionary FL with all 177 muscles from anatomyDictionary.json (was missing 56 muscles).
2. Reset this.allMuscles, this.superficialMuscles, this.deepMuscles on initClassifications to avoid duplication.
3. Automatically load muscles.glb via window.toggleMuscles(true) when opening Studio Bóc Tách or moving sliders.
4. When moving muscle sliders, ensure musclesModel.visible = true so changes are visible.
5. In setLayerOpacity, set depthWrite = opacity >= 0.99 and visible = opacity > 0.005 to prevent 0%-opacity muscles from creating invisible occlusions over deep muscles and bones.
"""

import json
import re
import sys

def fix_bundle():
    bundle_path = "web/assets/index-CGRTTg94.js"
    dict_path = "web/data/anatomyDictionary.json"

    with open(bundle_path, "r", encoding="utf-8") as f:
        bundle = f.read()

    with open(dict_path, "r", encoding="utf-8") as f:
        dict_data = json.load(f)

    # 1. Replace dictionary FL with complete 177 muscles
    fl_start = bundle.find("FL={")
    fl_end = bundle.find(";class zL", fl_start)
    if fl_start == -1 or fl_end == -1:
        print("ERROR: could not find FL in bundle!")
        sys.exit(1)

    new_fl = "FL=" + json.dumps(dict_data, ensure_ascii=False, separators=(',', ':'))
    bundle = bundle[:fl_start] + new_fl + bundle[fl_end:]
    print("1. Replaced FL with full 177 muscles dictionary")

    # 2. Expose window.dissectionStudio and window.Xe in zL constructor
    ctor_target = "this.mouse=new rn,this.initClassifications()"
    ctor_replacement = "this.mouse=new rn,window.dissectionStudio=this,window.Xe=this,this.initClassifications()"
    if ctor_target in bundle:
        bundle = bundle.replace(ctor_target, ctor_replacement, 1)
        print("2. Added window.dissectionStudio and window.Xe exposure")

    # 3. Reset arrays in initClassifications
    init_target = "initClassifications(){if(this.musclesModel&&this.musclesModel.traverse("
    init_replacement = "initClassifications(){this.allMuscles=[],this.superficialMuscles=[],this.deepMuscles=[],this.musclesModel&&this.musclesModel.traverse("
    if init_target in bundle:
        bundle = bundle.replace(init_target, init_replacement, 1)
        print("3. Added array resets to initClassifications")

    # 4. Auto-load muscles in togglePanel
    panel_target = "this.isOpen&&window.syncAllAnatomyControls&&window.syncAllAnatomyControls(),!this.isOpen"
    panel_replacement = "this.isOpen&&window.syncAllAnatomyControls&&window.syncAllAnatomyControls(),this.isOpen&&!this.musclesModel&&window.toggleMuscles&&window.toggleMuscles(!0),!this.isOpen"
    if panel_target in bundle:
        bundle = bundle.replace(panel_target, panel_replacement, 1)
        print("4. Added auto-load muscles to togglePanel")

    # 5. Fix slider events for superficial and deep muscles
    slider_target = 'document.getElementById("sliderSuperficialOpacity").addEventListener("input",u=>{const g=parseInt(u.target.value);document.getElementById("valSuperficialOpacity").textContent=g+"%",this.setLayerOpacity(this.superficialMuscles,g/100)}),document.getElementById("sliderDeepOpacity").addEventListener("input",u=>{const g=parseInt(u.target.value);document.getElementById("valDeepOpacity").textContent=g+"%",this.setLayerOpacity(this.deepMuscles,g/100)})'
    slider_replacement = 'document.getElementById("sliderSuperficialOpacity").addEventListener("input",async u=>{const g=parseInt(u.target.value);document.getElementById("valSuperficialOpacity").textContent=g+"%",!this.musclesModel&&window.toggleMuscles&&await window.toggleMuscles(!0),this.musclesModel&&g>0&&(this.musclesModel.visible=!0),this.setLayerOpacity(this.superficialMuscles,g/100)}),document.getElementById("sliderDeepOpacity").addEventListener("input",async u=>{const g=parseInt(u.target.value);document.getElementById("valDeepOpacity").textContent=g+"%",!this.musclesModel&&window.toggleMuscles&&await window.toggleMuscles(!0),this.musclesModel&&g>0&&(this.musclesModel.visible=!0),this.setLayerOpacity(this.deepMuscles,g/100)})'
    if slider_target in bundle:
        bundle = bundle.replace(slider_target, slider_replacement, 1)
        print("5. Upgraded sliderSuperficialOpacity and sliderDeepOpacity events")

    # 6. Fix btnPeelAllSuperficial to auto-load muscles if needed
    peel_target = 'document.getElementById("btnPeelAllSuperficial").addEventListener("click",()=>{this.superficialMuscles.forEach(u=>this.peelMesh(u,!1)),this.updatePeeledListUI()})'
    peel_replacement = 'document.getElementById("btnPeelAllSuperficial").addEventListener("click",async()=>{!this.musclesModel&&window.toggleMuscles&&await window.toggleMuscles(!0),this.superficialMuscles.forEach(u=>this.peelMesh(u,!1)),this.updatePeeledListUI()})'
    if peel_target in bundle:
        bundle = bundle.replace(peel_target, peel_replacement, 1)
        print("6. Upgraded btnPeelAllSuperficial event")

    # 7. Fix setLayerOpacity to handle depthWrite and visibility properly
    layer_target = 'setLayerOpacity(n,t){n.forEach(e=>{e.material&&(e.material.transparent=t<1,e.material.opacity=t,e.material.needsUpdate=!0)})}'
    layer_replacement = 'setLayerOpacity(n,t){n.forEach(e=>{e.material&&(e.material.transparent=t<.99,e.material.opacity=t,e.material.depthWrite=t>=.99,e.visible=t>.005&&!this.peeledObjects.has(e),e.material.needsUpdate=!0)})}'
    if layer_target in bundle:
        bundle = bundle.replace(layer_target, layer_replacement, 1)
        print("7. Upgraded setLayerOpacity with depthWrite & visibility control")

    with open(bundle_path, "w", encoding="utf-8") as f:
        f.write(bundle)
    print(f"Bundle {bundle_path} successfully saved!")

def fix_src():
    src_path = "web/js/dissectionStudio.js"
    with open(src_path, "r", encoding="utf-8") as f:
        src = f.read()

    # 1. Reset arrays in initClassifications
    src = src.replace(
        "  initClassifications() {\n    if (this.musclesModel) {",
        "  initClassifications() {\n    this.allMuscles = [];\n    this.superficialMuscles = [];\n    this.deepMuscles = [];\n    if (this.musclesModel) {"
    )

    # 2. Expose window.dissectionStudio in constructor
    src = src.replace(
        "    this.mouse = new THREE.Vector2();\n\n    this.initClassifications();",
        "    this.mouse = new THREE.Vector2();\n    window.dissectionStudio = this;\n    window.Xe = this;\n\n    this.initClassifications();"
    )

    # 3. Auto-load muscles in togglePanel
    src = src.replace(
        "    const btnDissect = document.getElementById('btnToggleDissection');\n    if (btnDissect) btnDissect.classList.toggle('active', this.isOpen);\n    if (!this.isOpen && this.isScalpelActive) {",
        "    const btnDissect = document.getElementById('btnToggleDissection');\n    if (btnDissect) btnDissect.classList.toggle('active', this.isOpen);\n    if (this.isOpen && !this.musclesModel && window.toggleMuscles) {\n      window.toggleMuscles(true);\n    }\n    if (!this.isOpen && this.isScalpelActive) {"
    )

    # 4. Sliders in bindEvents
    old_superficial_slider = """    document.getElementById('sliderSuperficialOpacity').addEventListener('input', (e) => {
      const val = parseInt(e.target.value);
      document.getElementById('valSuperficialOpacity').textContent = val + '%';
      this.setLayerOpacity(this.superficialMuscles, val / 100);
    });

    document.getElementById('sliderDeepOpacity').addEventListener('input', (e) => {
      const val = parseInt(e.target.value);
      document.getElementById('valDeepOpacity').textContent = val + '%';
      this.setLayerOpacity(this.deepMuscles, val / 100);
    });"""

    new_superficial_slider = """    document.getElementById('sliderSuperficialOpacity').addEventListener('input', async (e) => {
      const val = parseInt(e.target.value);
      document.getElementById('valSuperficialOpacity').textContent = val + '%';
      if (!this.musclesModel && window.toggleMuscles) {
        await window.toggleMuscles(true);
      }
      if (this.musclesModel && val > 0) {
        this.musclesModel.visible = true;
      }
      this.setLayerOpacity(this.superficialMuscles, val / 100);
    });

    document.getElementById('sliderDeepOpacity').addEventListener('input', async (e) => {
      const val = parseInt(e.target.value);
      document.getElementById('valDeepOpacity').textContent = val + '%';
      if (!this.musclesModel && window.toggleMuscles) {
        await window.toggleMuscles(true);
      }
      if (this.musclesModel && val > 0) {
        this.musclesModel.visible = true;
      }
      this.setLayerOpacity(this.deepMuscles, val / 100);
    });"""

    src = src.replace(old_superficial_slider, new_superficial_slider)

    # 5. btnPeelAllSuperficial
    old_peel = "    document.getElementById('btnPeelAllSuperficial').addEventListener('click', () => {\n      this.superficialMuscles.forEach(m => this.peelMesh(m, false));"
    new_peel = "    document.getElementById('btnPeelAllSuperficial').addEventListener('click', async () => {\n      if (!this.musclesModel && window.toggleMuscles) await window.toggleMuscles(true);\n      this.superficialMuscles.forEach(m => this.peelMesh(m, false));"
    src = src.replace(old_peel, new_peel)

    # 6. setLayerOpacity
    old_set_layer = """  setLayerOpacity(meshList, opacity) {
    meshList.forEach(m => {
      if (m.material) {
        m.material.transparent = opacity < 1.0;
        m.material.opacity = opacity;
        m.material.needsUpdate = true;
      }
    });
  }"""

    new_set_layer = """  setLayerOpacity(meshList, opacity) {
    meshList.forEach(m => {
      if (m.material) {
        m.material.transparent = opacity < 0.99;
        m.material.opacity = opacity;
        m.material.depthWrite = opacity >= 0.99;
        m.visible = opacity > 0.005 && !this.peeledObjects.has(m);
        m.material.needsUpdate = true;
      }
    });
  }"""

    src = src.replace(old_set_layer, new_set_layer)

    with open(src_path, "w", encoding="utf-8") as f:
        f.write(src)
    print(f"Source {src_path} successfully updated!")

if __name__ == "__main__":
    fix_bundle()
    fix_src()

