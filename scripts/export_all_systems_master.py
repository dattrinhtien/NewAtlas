#!/usr/bin/env python3
"""
export_all_systems_master.py
Trích xuất toàn bộ các hệ giải phẫu Z-Anatomy từ Startup.blend gốc giữ nguyên 100% hình học,
áp dụng biến đổi thế giới (world transforms) và vật liệu PBR riêng biệt cho từng tạng phủ.
"""

import bpy
from mathutils import Matrix
import os

base_dir = "/Volumes/D/Hoc Python/NewAtlas"
models_dir = os.path.join(base_dir, "web", "models")
os.makedirs(models_dir, exist_ok=True)

def recurse_layer_coll(layer_coll):
    layer_coll.exclude = False
    layer_coll.hide_viewport = False
    for c in layer_coll.children:
        recurse_layer_coll(c)

def unexclude_all():
    for lc in bpy.context.view_layer.layer_collection.children:
        recurse_layer_coll(lc)

def prepare_objects_with_world_transform(objects):
    """
    Chuyển đổi curves sang meshes, unparent và áp dụng matrix_world vào chính dữ liệu đỉnh (mesh vertices)
    để tọa độ hình học là tuyệt đối trong không gian cơ thể người 3D (Z-up -> Y-up của Three.js).
    """
    bpy.ops.object.select_all(action='DESELECT')
    
    # 1. Tách curves và meshes
    curves = [o for o in objects if o.type == 'CURVE']
    meshes = [o for o in objects if o.type == 'MESH']
    
    # 2. Batch convert curves to meshes
    if curves:
        for c in curves:
            c.select_set(True)
        bpy.context.view_layer.objects.active = curves[0]
        bpy.ops.object.convert(target='MESH')
        bpy.ops.object.select_all(action='DESELECT')
    
    all_meshes = meshes + curves
    
    # 3. Bake world transform directly into geometry
    for o in all_meshes:
        if o.type == 'MESH' and o.data:
            mw = o.matrix_world.copy()
            o.parent = None
            # Deep copy data if shared to avoid transforming multiple times
            if o.data.users > 1:
                o.data = o.data.copy()
            o.data.transform(mw)
            o.matrix_world = Matrix.Identity(4)
            o.select_set(True)
            o.hide_viewport = False
            o.hide_render = False

    return all_meshes

# -------------------------------------------------------------
# 1. HỆ NỘI TẠNG & TẠNG PHỦ (ORGANS)
# -------------------------------------------------------------
def export_organs():
    print("\n" + "="*60)
    print("--> 1. ĐANG XUẤT HỆ NỘI TẠNG & TẠNG PHỦ (ORGANS.GLB)...")
    coll = bpy.data.collections.get("8: Visceral systems")
    if not coll:
        print("Không tìm thấy collection 8: Visceral systems")
        return

    objs = [o for o in coll.objects if o.type in ('MESH', 'CURVE')]
    print(f"Tổng số đối tượng nội tạng: {len(objs)}")
    
    processed = prepare_objects_with_world_transform(objs)
    
    # Bảng màu giải phẫu riêng biệt cho từng tạng phủ
    color_palette = {
        'ureter': (0.96, 0.92, 0.55, 1.0),      # Vàng ngà niệu quản
        'kidney': (0.58, 0.16, 0.08, 1.0),      # Nâu đỏ thẫm Thận
        'renal': (0.58, 0.16, 0.08, 1.0),
        'bladder': (0.92, 0.42, 0.12, 1.0),     # Cam hổ phách Bàng quang
        'urethra': (0.85, 0.65, 0.45, 1.0),
        'liver': (0.48, 0.14, 0.09, 1.0),       # Nâu đất Can (Gan)
        'gallbladder': (0.12, 0.52, 0.16, 1.0), # Xanh ô liu Đởm (Túi mật)
        'cystic': (0.12, 0.52, 0.16, 1.0),
        'stomach': (0.82, 0.48, 0.08, 1.0),     # Vàng hổ phách Vị (Dạ dày)
        'spleen': (0.48, 0.09, 0.48, 1.0),      # Tím mận Tỳ (Lách)
        'pancreas': (0.92, 0.75, 0.10, 1.0),    # Vàng kim Tụy tạng
        'pancreatic': (0.92, 0.75, 0.10, 1.0),
        'heart': (0.78, 0.12, 0.14, 1.0),       # Đỏ sẫm Tâm (Tim)
        'ventricle': (0.78, 0.12, 0.14, 1.0),
        'atrium': (0.78, 0.12, 0.14, 1.0),
        'lung': (0.92, 0.58, 0.58, 1.0),        # Hồng phớt Phế (Phổi)
        'colon': (0.68, 0.42, 0.24, 1.0),       # Nâu sáng Đại trường (Đại tràng)
        'caecum': (0.68, 0.42, 0.24, 1.0),
        'rectum': (0.68, 0.42, 0.24, 1.0),
        'appendix': (0.68, 0.42, 0.24, 1.0),
        'intestine': (0.94, 0.62, 0.58, 1.0),   # Hồng cam Tiểu trường (Ruột non)
        'duodenum': (0.94, 0.62, 0.58, 1.0),
        'jejunum': (0.94, 0.62, 0.58, 1.0),
        'ileum': (0.94, 0.62, 0.58, 1.0),
        'trachea': (0.38, 0.78, 0.88, 1.0),     # Xanh ngọc sụn khí phế quản
        'bronch': (0.38, 0.78, 0.88, 1.0),
        'larynx': (0.42, 0.72, 0.82, 1.0),
        'thyroid': (0.72, 0.32, 0.28, 1.0),     # Tuyến giáp
        'oesophagus': (0.86, 0.48, 0.48, 1.0),  # Thực quản
        'parotid': (0.82, 0.68, 0.48, 1.0),     # Tuyến mang tai
        'sublingual': (0.82, 0.68, 0.48, 1.0),
        'submandibular': (0.82, 0.68, 0.48, 1.0)
    }

    mat_cache = {}
    for o in processed:
        name_l = o.name.lower()
        matched = 'organ_general'
        color = (0.72, 0.38, 0.32, 1.0)
        for k, c in color_palette.items():
            if k in name_l:
                matched = k
                color = c
                break
        
        if matched not in mat_cache:
            m = bpy.data.materials.new(name=f"PBR_{matched}")
            bs = m.node_tree.nodes.get("Principled BSDF")
            if bs:
                bs.inputs['Base Color'].default_value = color
                bs.inputs['Roughness'].default_value = 0.35
            mat_cache[matched] = m
        
        o.data.materials.clear()
        o.data.materials.append(mat_cache[matched])

    out_path = os.path.join(models_dir, "organs.glb")
    bpy.context.view_layer.objects.active = processed[0]
    bpy.ops.export_scene.gltf(
        filepath=out_path,
        export_format='GLB',
        use_selection=True,
        export_apply=True,
        export_yup=True,
        export_materials='EXPORT'
    )
    print(f"✓ XUẤT HOÀN TẤT ORGANS.GLB: {os.path.getsize(out_path)/(1024*1024):.2f} MB ({len(processed)} đối tượng)")

# -------------------------------------------------------------
# 2. HỆ BẠCH HUYẾT (LYMPHATIC)
# -------------------------------------------------------------
def export_lymphatic():
    print("\n" + "="*60)
    print("--> 2. ĐANG XUẤT HỆ BẠCH HUYẾT (LYMPHATIC.GLB)...")
    coll = bpy.data.collections.get("6: Lymphoid organs")
    if not coll:
        print("Không tìm thấy collection 6: Lymphoid organs")
        return

    objs = [o for o in coll.objects if o.type in ('MESH', 'CURVE')]
    print(f"Tổng số đối tượng hạch & cơ quan bạch huyết: {len(objs)}")
    processed = prepare_objects_with_world_transform(objs)

    mat_lymph = bpy.data.materials.new(name="PBR_Lymphatic")
    bs = mat_lymph.node_tree.nodes.get("Principled BSDF")
    if bs:
        bs.inputs['Base Color'].default_value = (0.15, 0.85, 0.40, 1.0) # Xanh ngọc lục bảo trong mờ
        bs.inputs['Roughness'].default_value = 0.28

    for o in processed:
        o.data.materials.clear()
        o.data.materials.append(mat_lymph)

    out_path = os.path.join(models_dir, "lymphatic.glb")
    bpy.context.view_layer.objects.active = processed[0]
    bpy.ops.export_scene.gltf(
        filepath=out_path,
        export_format='GLB',
        use_selection=True,
        export_apply=True,
        export_yup=True,
        export_materials='EXPORT'
    )
    print(f"✓ XUẤT HOÀN TẤT LYMPHATIC.GLB: {os.path.getsize(out_path)/(1024*1024):.2f} MB ({len(processed)} đối tượng)")

# -------------------------------------------------------------
# 3. HỆ TUẦN HOÀN MẠCH MÁU (VESSELS)
# -------------------------------------------------------------
def export_vessels():
    print("\n" + "="*60)
    print("--> 3. ĐANG XUẤT HỆ MẠCH MÁU (VESSELS.GLB)...")
    coll = bpy.data.collections.get("5: Cardiovascular system")
    if not coll:
        print("Không tìm thấy collection 5: Cardiovascular system")
        return

    objs = [o for o in coll.objects if o.type in ('MESH', 'CURVE')]
    print(f"Tổng số mạch máu: {len(objs)}")
    processed = prepare_objects_with_world_transform(objs)

    mat_art = bpy.data.materials.new(name="PBR_Artery")
    bs_a = mat_art.node_tree.nodes.get("Principled BSDF")
    if bs_a:
        bs_a.inputs['Base Color'].default_value = (0.88, 0.12, 0.12, 1.0) # Đỏ động mạch
        bs_a.inputs['Roughness'].default_value = 0.35

    mat_vn = bpy.data.materials.new(name="PBR_Vein")
    bs_v = mat_vn.node_tree.nodes.get("Principled BSDF")
    if bs_v:
        bs_v.inputs['Base Color'].default_value = (0.12, 0.40, 0.88, 1.0) # Xanh tĩnh mạch
        bs_v.inputs['Roughness'].default_value = 0.35

    for o in processed:
        name_l = o.name.lower()
        is_vein = 'vein' in name_l or 'cava' in name_l or 'sinus' in name_l or 'venous' in name_l
        mat = mat_vn if is_vein else mat_art
        o.data.materials.clear()
        o.data.materials.append(mat)

    out_path = os.path.join(models_dir, "vessels.glb")
    bpy.context.view_layer.objects.active = processed[0]
    bpy.ops.export_scene.gltf(
        filepath=out_path,
        export_format='GLB',
        use_selection=True,
        export_apply=True,
        export_yup=True,
        export_materials='EXPORT'
    )
    print(f"✓ XUẤT HOÀN TẤT VESSELS.GLB: {os.path.getsize(out_path)/(1024*1024):.2f} MB ({len(processed)} đối tượng)")

# -------------------------------------------------------------
# 4. HỆ THẦN KINH (NERVES)
# -------------------------------------------------------------
def export_nerves():
    print("\n" + "="*60)
    print("--> 4. ĐANG XUẤT HỆ THẦN KINH (NERVES.GLB)...")
    coll = bpy.data.collections.get("7: Nervous system & Sense organs")
    if not coll:
        print("Không tìm thấy collection 7: Nervous system & Sense organs")
        return

    objs = [o for o in coll.objects if o.type in ('MESH', 'CURVE')]
    print(f"Tổng số cấu trúc thần kinh & giác quan: {len(objs)}")
    processed = prepare_objects_with_world_transform(objs)

    mat_nerve = bpy.data.materials.new(name="PBR_Nerve")
    bs = mat_nerve.node_tree.nodes.get("Principled BSDF")
    if bs:
        bs.inputs['Base Color'].default_value = (0.95, 0.82, 0.18, 1.0) # Vàng ánh điện Thần kinh
        bs.inputs['Roughness'].default_value = 0.35

    for o in processed:
        o.data.materials.clear()
        o.data.materials.append(mat_nerve)

    out_path = os.path.join(models_dir, "nerves.glb")
    bpy.context.view_layer.objects.active = processed[0]
    bpy.ops.export_scene.gltf(
        filepath=out_path,
        export_format='GLB',
        use_selection=True,
        export_apply=True,
        export_yup=True,
        export_materials='EXPORT'
    )
    print(f"✓ XUẤT HOÀN TẤT NERVES.GLB: {os.path.getsize(out_path)/(1024*1024):.2f} MB ({len(processed)} đối tượng)")

def main():
    unexclude_all()
    export_organs()
    export_lymphatic()
    export_vessels()
    export_nerves()
    print("\n" + "="*60)
    print("ĐÃ HOÀN THÀNH TOÀN BỘ QUÁ TRÌNH TRÍCH XUẤT Z-ANATOMY GỐC CHUẨN XÁC!")
    print("="*60)

if __name__ == "__main__":
    main()

