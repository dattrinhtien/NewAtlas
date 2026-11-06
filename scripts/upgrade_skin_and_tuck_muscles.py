import bpy
import struct
import json
import math
import os

BASE_DIR = "/Volumes/D/Hoc Python/NewAtlas"
HL_ORIG = os.path.join(BASE_DIR, "web/models/human-learning.glb.orig")
HL_OUT = os.path.join(BASE_DIR, "web/models/human-learning.glb")


def load_hl_orig():
    with open(HL_ORIG, "rb") as f:
        buf = f.read()
    json_len = struct.unpack("<I", buf[12:16])[0]
    gltf = json.loads(buf[20 : 20 + json_len].decode("utf-8"))
    bin_off = 20 + json_len + 8
    prim = gltf["meshes"][0]["primitives"][0]
    pos_acc = gltf["accessors"][prim["attributes"]["POSITION"]]
    norm_acc = gltf["accessors"][prim["attributes"]["NORMAL"]]
    idx_acc = gltf["accessors"][prim["indices"]]
    pos_bv = gltf["bufferViews"][pos_acc["bufferView"]]
    norm_bv = gltf["bufferViews"][norm_acc["bufferView"]]
    idx_bv = gltf["bufferViews"][idx_acc["bufferView"]]

    v_count = pos_acc["count"]
    hl_pos = [
        list(
            struct.unpack(
                "<fff",
                buf[
                    bin_off
                    + pos_bv.get("byteOffset", 0)
                    + pos_acc.get("byteOffset", 0)
                    + i * pos_bv.get("byteStride", 12) : bin_off
                    + pos_bv.get("byteOffset", 0)
                    + pos_acc.get("byteOffset", 0)
                    + i * pos_bv.get("byteStride", 12)
                    + 12
                ],
            )
        )
        for i in range(v_count)
    ]
    hl_norm = [
        list(
            struct.unpack(
                "<fff",
                buf[
                    bin_off
                    + norm_bv.get("byteOffset", 0)
                    + norm_acc.get("byteOffset", 0)
                    + i * norm_bv.get("byteStride", 12) : bin_off
                    + norm_bv.get("byteOffset", 0)
                    + norm_acc.get("byteOffset", 0)
                    + i * norm_bv.get("byteStride", 12)
                    + 12
                ],
            )
        )
        for i in range(v_count)
    ]
    i_count = idx_acc["count"]
    io = bin_off + idx_bv.get("byteOffset", 0) + idx_acc.get("byteOffset", 0)
    fmt = "<I" if idx_acc["componentType"] == 5125 else "<H"
    step = 4 if idx_acc["componentType"] == 5125 else 2
    hl_indices = [
        struct.unpack(fmt, buf[io + i * step : io + (i + 1) * step])[0]
        for i in range(i_count)
    ]
    return gltf, hl_pos, hl_norm, hl_indices


def build_upgraded_human_glb():
    gltf, hl_pos, hl_norm, hl_indices = load_hl_orig()

    cz_neck = -0.020
    hl_neck_samples = []
    for i, v in enumerate(hl_pos):
        if 1.482 <= v[1] <= 1.504:
            dx, dz = v[0], v[2] - cz_neck
            ang = math.atan2(dx, dz)
            rad = math.hypot(dx, dz)
            hl_neck_samples.append((ang, v[1], rad, hl_norm[i]))

    def get_hl_neck_radius_and_norm(ang, y_target):
        num, den = 0.0, 0.0
        nx, ny, nz = 0.0, 0.0, 0.0
        for sang, sy, srad, sn in hl_neck_samples:
            da = math.atan2(math.sin(ang - sang), math.cos(ang - sang))
            dy = (y_target - sy) * 6.0
            d2 = da * da + dy * dy + 0.008
            w = 1.0 / (d2 * d2)
            num += srad * w
            nx += sn[0] * w
            ny += sn[1] * w
            nz += sn[2] * w
            den += w
        nl = math.hypot(nx, ny, nz) or 1.0
        return (num / den if den > 0 else 0.056), (nx / nl, ny / nl, nz / nl)

    coll_head = bpy.data.collections.get("Regions of head")
    coll_neck = bpy.data.collections.get("Regions of neck")
    za_meshes = []
    for c in (coll_head, coll_neck):
        if c:
            for o in c.all_objects:
                nl = o.name.lower()
                if (
                    o.type == "MESH"
                    and not nl.endswith(".j")
                    and not nl.endswith(".g")
                    and not nl.endswith("-line")
                    and "hairs" not in nl
                    and "eyelash" not in nl
                    and "supraclavicular" not in nl
                    and o not in za_meshes
                ):
                    za_meshes.append(o)

    eye_meshes = []
    for en in ["Sclera.r", "Sclera.l", "Cornea.r", "Cornea.l"]:
        o = bpy.data.objects.get(en)
        if o and o.type == "MESH":
            eye_meshes.append(o)

    def map_za_vert_and_norm(tx, ty, tz, nx, ny, nz, is_eye=False):
        hy = ty * 1.013 + 0.0205
        hx = tx * 0.94
        hz = tz * 0.96 - 0.005
        if is_eye or hy >= 1.528:
            return [hx, hy, hz], [nx, ny, nz]
        w = max(0.0, min(1.0, (1.528 - hy) / 0.032))
        w = w * w * (3.0 - 2.0 * w)
        dx, dz = hx, hz - cz_neck
        ang = math.atan2(dx, dz)
        cur_r = math.hypot(dx, dz)
        target_r, target_n = get_hl_neck_radius_and_norm(
            ang, max(1.490, min(1.502, hy))
        )
        new_r = cur_r * (1.0 - w) + target_r * w
        scale = new_r / (cur_r + 1e-8)
        bnx = nx * (1.0 - w) + target_n[0] * w
        bny = ny * (1.0 - w) + target_n[1] * w
        bnz = nz * (1.0 - w) + target_n[2] * w
        bnl = math.hypot(bnx, bny, bnz) or 1.0
        return [dx * scale, hy, cz_neck + dz * scale], [
            bnx / bnl,
            bny / bnl,
            bnz / bnl,
        ]

    out_pos = []
    out_norm = []
    out_tris = []

    # 1. Add ZA head & neck meshes
    for o in za_meshes:
        mw = o.matrix_world
        mn = mw.to_3x3().inverted().transposed()
        flip = mw.determinant() < 0
        me = o.data
        me.calc_loop_triangles()
        base_idx = len(out_pos)
        for v in me.vertices:
            wv = mw @ v.co
            wn = (mn @ v.normal).normalized()
            mp, mn_out = map_za_vert_and_norm(
                wv.x, wv.z, -wv.y, wn.x, wn.z, -wn.y, is_eye=False
            )
            out_pos.append(mp)
            out_norm.append(mn_out)
        for tri in me.loop_triangles:
            a, b, c = (
                base_idx + tri.vertices[0],
                base_idx + tri.vertices[1],
                base_idx + tri.vertices[2],
            )
            va, vb, vc = out_pos[a], out_pos[b], out_pos[c]
            if min(va[1], vb[1], vc[1]) < 1.498:
                continue
            if flip:
                out_tris.append((a, c, b))
            else:
                out_tris.append((a, b, c))

    # Smooth normals across ZA head region seams ONLY (before adding eyes!)
    buckets = {}
    for idx in range(len(out_pos)):
        p = out_pos[idx]
        key = (round(p[0] * 2500), round(p[1] * 2500), round(p[2] * 2500))
        buckets.setdefault(key, []).append(idx)

    for group in buckets.values():
        if len(group) > 1:
            for i in group:
                ni = out_norm[i]
                sx, sy, sz = ni[0], ni[1], ni[2]
                for j in group:
                    if i == j:
                        continue
                    nj = out_norm[j]
                    if ni[0] * nj[0] + ni[1] * nj[1] + ni[2] * nj[2] > 0.78:
                        sx += nj[0]
                        sy += nj[1]
                        sz += nj[2]
                sl = math.hypot(sx, sy, sz) or 1.0
                out_norm[i] = [sx / sl, sy / sl, sz / sl]

    # 2. Add Sclera & Cornea meshes with pure spherical normals
    for o in eye_meshes:
        mw = o.matrix_world
        mn = mw.to_3x3().inverted().transposed()
        flip = mw.determinant() < 0
        me = o.data
        me.calc_loop_triangles()
        base_idx = len(out_pos)
        for v in me.vertices:
            wv = mw @ v.co
            wn = (mn @ v.normal).normalized()
            mp, mn_out = map_za_vert_and_norm(
                wv.x, wv.z, -wv.y, wn.x, wn.z, -wn.y, is_eye=True
            )
            out_pos.append(mp)
            out_norm.append(mn_out)
        for tri in me.loop_triangles:
            a, b, c = (
                base_idx + tri.vertices[0],
                base_idx + tri.vertices[1],
                base_idx + tri.vertices[2],
            )
            if flip:
                out_tris.append((a, c, b))
            else:
                out_tris.append((a, b, c))

    # Ensure all ZA head & eye triangles have winding matching their outward normal
    for idx_t in range(len(out_tris)):
        a, b, c = out_tris[idx_t]
        va, vb, vc = out_pos[a], out_pos[b], out_pos[c]
        ux, uy, uz = vb[0] - va[0], vb[1] - va[1], vb[2] - va[2]
        vx, vy, vz = vc[0] - va[0], vc[1] - va[1], vc[2] - va[2]
        cx, cy, cz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
        na, nb, nc = out_norm[a], out_norm[b], out_norm[c]
        if (
            cx * (na[0] + nb[0] + nc[0])
            + cy * (na[1] + nb[1] + nc[1])
            + cz * (na[2] + nb[2] + nc[2])
            < 0
        ):
            out_tris[idx_t] = (a, c, b)

    # 3. Add HL body + neck up to Y = 1.518 (gentle 1.5% tuck at top rim so no step!)
    base_hl = len(out_pos)
    for i, v in enumerate(hl_pos):
        vp = list(v)
        if 1.502 < vp[1] < 1.528:
            t = max(0.0, min(1.0, (vp[1] - 1.502) / 0.016))
            vp[0] *= 1.0 - 0.015 * t
            vp[2] = cz_neck + (vp[2] - cz_neck) * (1.0 - 0.015 * t)
        out_pos.append(vp)
        out_norm.append(hl_norm[i])

    for t in range(0, len(hl_indices), 3):
        a, b, c = hl_indices[t], hl_indices[t + 1], hl_indices[t + 2]
        va, vb, vc = out_pos[base_hl + a], out_pos[base_hl + b], out_pos[base_hl + c]
        if min(va[1], vb[1], vc[1]) > 1.516 and max(va[2], vb[2], vc[2]) > 0.032:
            continue
        if min(va[1], vb[1], vc[1]) > 1.519:
            continue
        out_tris.append((base_hl + a, base_hl + b, base_hl + c))

    v_total = len(out_pos)
    i_total = len(out_tris) * 3

    pos_bytes = bytearray()
    norm_bytes = bytearray()
    min_pos = [999.0, 999.0, 999.0]
    max_pos = [-999.0, -999.0, -999.0]
    for i in range(v_total):
        px, py, pz = out_pos[i]
        nx, ny, nz = out_norm[i]
        if px < min_pos[0]: min_pos[0] = px
        if py < min_pos[1]: min_pos[1] = py
        if pz < min_pos[2]: min_pos[2] = pz
        if px > max_pos[0]: max_pos[0] = px
        if py > max_pos[1]: max_pos[1] = py
        if pz > max_pos[2]: max_pos[2] = pz
        pos_bytes.extend(struct.pack("<fff", px, py, pz))
        norm_bytes.extend(struct.pack("<fff", nx, ny, nz))

    idx_bytes = bytearray()
    for a, b, c in out_tris:
        idx_bytes.extend(struct.pack("<III", a, b, c))

    bin_chunk = pos_bytes + norm_bytes + idx_bytes
    while len(bin_chunk) % 4 != 0:
        bin_chunk.extend(b"\x00")

    new_gltf = {
        "asset": {"generator": "NewAtlas Z-Anatomy & MakeHuman Fusion", "version": "2.0"},
        "scene": 0,
        "scenes": [{"name": "Scene", "nodes": [0]}],
        "nodes": [{"mesh": 0, "name": "MakeHuman body - palms-forward study pose"}],
        "materials": gltf.get("materials", [{"name": "Neutral study surface"}]),
        "meshes": [
            {
                "name": "MakeHuman body - palms-forward study pose",
                "primitives": [
                    {
                        "attributes": {"POSITION": 0, "NORMAL": 1},
                        "indices": 2,
                        "material": 0,
                        "mode": 4,
                    }
                ],
            }
        ],
        "accessors": [
            {
                "bufferView": 0,
                "byteOffset": 0,
                "componentType": 5126,
                "count": v_total,
                "max": max_pos,
                "min": min_pos,
                "type": "VEC3",
            },
            {
                "bufferView": 1,
                "byteOffset": 0,
                "componentType": 5126,
                "count": v_total,
                "type": "VEC3",
            },
            {
                "bufferView": 2,
                "byteOffset": 0,
                "componentType": 5125,
                "count": i_total,
                "type": "SCALAR",
            },
        ],
        "bufferViews": [
            {"buffer": 0, "byteLength": len(pos_bytes), "byteOffset": 0, "target": 34962},
            {
                "buffer": 0,
                "byteLength": len(norm_bytes),
                "byteOffset": len(pos_bytes),
                "target": 34962,
            },
            {
                "buffer": 0,
                "byteLength": len(idx_bytes),
                "byteOffset": len(pos_bytes) + len(norm_bytes),
                "target": 34963,
            },
        ],
        "buffers": [{"byteLength": len(bin_chunk)}],
    }

    json_bytes = json.dumps(new_gltf, separators=(",", ":")).encode("utf-8")
    while len(json_bytes) % 4 != 0:
        json_bytes += b" "

    total_len = 12 + 8 + len(json_bytes) + 8 + len(bin_chunk)
    with open(HL_OUT, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, total_len))
        f.write(struct.pack("<II", len(json_bytes), 0x4E4F534A))
        f.write(json_bytes)
        f.write(struct.pack("<II", len(bin_chunk), 0x004E4942))
        f.write(bin_chunk)

    print(f"DONE HL_OUT: {v_total} verts, {len(out_tris)} tris")


if __name__ == "__main__":
    build_upgraded_human_glb()
