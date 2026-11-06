#!/usr/bin/env python3
"""
scripts/fix_skin_muscle_mixup.py
Fixes the "da cơ lẫn lộn" issue:
1. Removes the global position.y vertex shader from muscle materials which was turning 80% of muscles chalky white.
2. Restores rich anatomical muscle crimson (#b84a39, roughness 0.65, metalness 0.1) for all 177 muscles.
3. Sets clean pearlescent tendon color (#e2e8f0) ONLY for genuine aponeurosis and tendon meshes (calcaneal-tendon, epicranial-aponeurosis, linea-alba).
4. In setSkinOpacity: when opacity is 0 (n <= 0.005), fully set this.humanModel.visible = false so zero skin meshes interfere with muscle dissection.
   When opacity is 1 (n >= 0.99), set transparent = false, depthWrite = true so solid skin cleanly encases the body.
5. Preserves all scientific osteology (242 bones) and myology (origin, insertion, action, innervation, acupoints) dictionaries.
"""

def fix_bundle():
    bundle_path = 'web/assets/index-CGRTTg94.js'
    with open(bundle_path, 'r', encoding='utf-8') as f:
        bundle = f.read()

    # 1. Clean muscle traversal: replace the broken onBeforeCompile block with clean material assignment
    old_musc_block = 'const isTend=["epicranial-aponeurosis","calcaneal-tendon","linea-alba","tensor-fasciae-latae"].includes(e)||e.includes("tendon")||e.includes("aponeurosis")||e.includes("fascia")||e.includes("ligament");if(isTend){t.color=new bn("#f4f5f7");t.roughness=.38;t.metalness=.12}else{t.color=new bn("#a8392b");t.roughness=.62;t.metalness=.06;t.onBeforeCompile=s=>{s.vertexShader=s.vertexShader.replace("#include <common>","#include <common>\\nvarying float vExtr;").replace("#include <begin_vertex>","#include <begin_vertex>\\nvExtr=smoothstep(0.35,0.49,abs(position.y));");s.fragmentShader=s.fragmentShader.replace("#include <common>","#include <common>\\nvarying float vExtr;").replace("#include <dithering_fragment>","#include <dithering_fragment>\\ngl_FragColor.rgb=mix(gl_FragColor.rgb,vec3(0.96,0.97,0.98),vExtr*0.85);")}};'
    new_musc_block = 'const isTend=["epicranial-aponeurosis","calcaneal-tendon","linea-alba"].includes(e);if(isTend){t.color=new bn("#e2e8f0");t.roughness=.45;t.metalness=.08}else{t.color=new bn("#b84a39");t.roughness=.65;t.metalness=.1};'

    if old_musc_block in bundle:
        bundle = bundle.replace(old_musc_block, new_musc_block, 1)
        print("1. Successfully removed broken vertex shader and restored anatomical muscle red (#b84a39)!")
    else:
        print("NOTE: old_musc_block not found exactly, searching for vExtr substring...")
        idx = bundle.find('vExtr=smoothstep')
        if idx != -1:
            start = bundle.rfind('const isTend=', 0, idx)
            end = bundle.find('};n.userData=', idx) + 2
            bundle = bundle[:start] + new_musc_block + bundle[end:]
            print("1. Replaced broken muscle shader range successfully!")

    # 2. Fix setSkinOpacity in bundle
    old_skin_fn = 'setSkinOpacity(n){const op=n>=.99;this.humanModel&&this.humanModel.traverse(t=>{t.isMesh&&t.material&&(t.material.transparent=!op,t.material.opacity=n,t.material.depthWrite=op,t.material.polygonOffset=!0,t.material.polygonOffsetFactor=op?-4:-1,t.material.polygonOffsetUnits=op?-8:-4,t.material.needsUpdate=!0)})}'
    new_skin_fn = 'setSkinOpacity(n){const op=n>=.99;if(this.humanModel){this.humanModel.visible=n>.005;this.humanModel.traverse(t=>{t.isMesh&&t.material&&(t.material.transparent=!op,t.material.opacity=n,t.material.depthWrite=op,t.material.polygonOffset=!0,t.material.polygonOffsetFactor=op?-2:-1,t.material.polygonOffsetUnits=op?-4:-2,t.material.needsUpdate=!0)})}}'

    if old_skin_fn in bundle:
        bundle = bundle.replace(old_skin_fn, new_skin_fn, 1)
        print("2. Upgraded setSkinOpacity with clean visibility toggle and depthWrite!")
    else:
        print("NOTE: old_skin_fn not found exactly, checking partial...")
        p_start = bundle.find('setSkinOpacity(n){')
        p_end = bundle.find('setLayerOpacity(n,t){', p_start)
        if p_start != -1 and p_end != -1:
            bundle = bundle[:p_start] + new_skin_fn + bundle[p_end:]
            print("2. Replaced setSkinOpacity range successfully!")

    with open(bundle_path, 'w', encoding='utf-8') as f:
        f.write(bundle)
    print("Bundle web/assets/index-CGRTTg94.js saved successfully!")

def fix_src():
    src_path = 'web/js/dissectionStudio.js'
    with open(src_path, 'r', encoding='utf-8') as f:
        src = f.read()

    # Remove onBeforeCompile from dissectionStudio.js
    idx = src.find('const isTendon = [')
    end = src.find('child.userData = {', idx)
    if idx != -1 and end != -1:
        clean_musc = """const isTendon = ['epicranial-aponeurosis', 'calcaneal-tendon', 'linea-alba'].includes(meshName);

          if (isTendon) {
            baseMat.color = new THREE.Color('#e2e8f0');
            baseMat.roughness = 0.45;
            baseMat.metalness = 0.08;
          } else {
            baseMat.color = new THREE.Color('#b84a39');
            baseMat.roughness = 0.65;
            baseMat.metalness = 0.1;
          }

          """
        src = src[:idx] + clean_musc + src[end:]
        print("Source web/js/dissectionStudio.js muscle materials cleaned!")

    # Fix setSkinOpacity in src
    old_skin_src = """  setSkinOpacity(opacity) {
    if (this.humanModel) {
      this.humanModel.traverse((child) => {
        if (child.isMesh && child.material) {
          child.material.transparent = opacity < 1.0;
          child.material.opacity = opacity;
          child.material.needsUpdate = true;
        }
      });
    }
  }"""

    new_skin_src = """  setSkinOpacity(opacity) {
    if (this.humanModel) {
      const isOpaque = opacity >= 0.99;
      this.humanModel.visible = opacity > 0.005;
      this.humanModel.traverse((child) => {
        if (child.isMesh && child.material) {
          child.material.transparent = !isOpaque;
          child.material.opacity = opacity;
          child.material.depthWrite = isOpaque;
          child.material.polygonOffset = true;
          child.material.polygonOffsetFactor = isOpaque ? -2 : -1;
          child.material.polygonOffsetUnits = isOpaque ? -4 : -2;
          child.material.needsUpdate = true;
        }
      });
    }
  }"""
    src = src.replace(old_skin_src, new_skin_src)

    with open(src_path, 'w', encoding='utf-8') as f:
        f.write(src)
    print("Source web/js/dissectionStudio.js saved successfully!")

if __name__ == '__main__':
    fix_bundle()
    fix_src()

