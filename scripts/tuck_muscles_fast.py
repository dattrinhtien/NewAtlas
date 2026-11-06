import os
import struct
import json
import math
import numpy as np
from scipy.spatial import cKDTree
from PIL import Image

WORKSPACE = "/Volumes/D/Hoc Python/NewAtlas"
HL_OUT = os.path.join(WORKSPACE, "web/models/human-learning.glb")
MUSC_ORIG = os.path.join(WORKSPACE, "web/models/muscles.glb.orig")
MUSC_OUT = os.path.join(WORKSPACE, "web/models/muscles.glb")
ARTIFACT_DIR = "/Users/wildwindhill/.gemini/antigravity/brain/72f325f7-6943-46bf-9108-f60a6a751dd3"


def load_skin():
    with open(HL_OUT, "rb") as f:
        hb = f.read()
    jlen = struct.unpack("<I", hb[12:16])[0]
    hg = json.loads(hb[20 : 20 + jlen].decode("utf-8"))
    boff = 20 + jlen + 8
    vcnt = hg["accessors"][0]["count"]
    icnt = hg["accessors"][2]["count"]
    n_off = hg["bufferViews"][1]["byteOffset"]
    i_off = hg["bufferViews"][2]["byteOffset"]

    pos = np.frombuffer(hb, dtype=np.float32, count=vcnt * 3, offset=boff).reshape(-1, 3).copy()
    norm = np.frombuffer(hb, dtype=np.float32, count=vcnt * 3, offset=boff + n_off).reshape(-1, 3).copy()
    tris = np.frombuffer(hb, dtype=np.uint32, count=icnt, offset=boff + i_off).reshape(-1, 3).copy()
    return pos, norm, tris


def tuck_muscles_and_verify(skin_pos, skin_norm, skin_tris):
    print("--> Đang thu gọn 177 bó cơ bằng SciPy cKDTree & Z-Buffer...")
    samples_p = []
    samples_n = []

    va = skin_pos[skin_tris[:, 0]]
    vb = skin_pos[skin_tris[:, 1]]
    vc = skin_pos[skin_tris[:, 2]]
    na = skin_norm[skin_tris[:, 0]]
    nb = skin_norm[skin_tris[:, 1]]
    nc = skin_norm[skin_tris[:, 2]]

    bary_weights = [
        (1.0, 0.0, 0.0),
        (0.0, 1.0, 0.0),
        (0.0, 0.0, 1.0),
        (1 / 3, 1 / 3, 1 / 3),
        (0.5, 0.5, 0.0),
        (0.0, 0.5, 0.5),
        (0.5, 0.0, 0.5),
        (0.6, 0.2, 0.2),
        (0.2, 0.6, 0.2),
        (0.2, 0.2, 0.6),
    ]
    for w0, w1, w2 in bary_weights:
        pts = va * w0 + vb * w1 + vc * w2
        nms = na * w0 + nb * w1 + nc * w2
        n_len = np.linalg.norm(nms, axis=1, keepdims=True)
        n_len[n_len < 1e-6] = 1.0
        nms = nms / n_len

        head_mask = pts[:, 1] > 1.495
        rx = pts[:, 0]
        ry = np.maximum(0.0, pts[:, 1] - 1.58) * 0.7
        rz = pts[:, 2] - (-0.022)
        rl = np.sqrt(rx * rx + ry * ry + rz * rz)
        rl[rl < 1e-6] = 1.0
        rad_dot = (rx * nms[:, 0] + ry * nms[:, 1] + rz * nms[:, 2]) / rl
        valid = (~head_mask) | (rad_dot > 0.30)

        samples_p.append(pts[valid])
        samples_n.append(nms[valid])

    sp_all = np.vstack(samples_p).astype(np.float32)
    sn_all = np.vstack(samples_n).astype(np.float32)
    kdtree = cKDTree(sp_all)

    with open(MUSC_ORIG, "rb") as f:
        m_buf = bytearray(f.read())
    json_len = struct.unpack("<I", m_buf[12:16])[0]
    m_gltf = json.loads(m_buf[20 : 20 + json_len].decode("utf-8"))
    bin_off = 20 + json_len + 8

    SCALE = 0.2641
    OFFSET_Y = 0.878

    mesh_slices = []
    all_m_verts = []
    for m_idx, mesh in enumerate(m_gltf["meshes"]):
        prim = mesh["primitives"][0]
        pa = m_gltf["accessors"][prim["attributes"]["POSITION"]]
        bv_p = m_gltf["bufferViews"][pa["bufferView"]]
        p_stride = bv_p.get("byteStride", 12)
        p_off = bin_off + bv_p.get("byteOffset", 0) + pa.get("byteOffset", 0)
        v_cnt = pa["count"]

        ia = m_gltf["accessors"][prim["indices"]]
        bv_i = m_gltf["bufferViews"][ia["bufferView"]]
        i_off = bin_off + bv_i.get("byteOffset", 0) + ia.get("byteOffset", 0)
        i_cnt = ia["count"]

        verts = np.zeros((v_cnt, 3), dtype=np.float32)
        for i in range(v_cnt):
            lx, ly, lz = struct.unpack("<fff", m_buf[p_off + i * p_stride : p_off + i * p_stride + 12])
            verts[i, 0] = lx * SCALE
            verts[i, 1] = ly * SCALE + OFFSET_Y
            verts[i, 2] = lz * SCALE

        if ia["componentType"] == 5123:
            tris = np.frombuffer(m_buf, dtype=np.uint16, count=i_cnt, offset=i_off).astype(np.uint32).reshape(-1, 3)
        else:
            tris = np.frombuffer(m_buf, dtype=np.uint32, count=i_cnt, offset=i_off).reshape(-1, 3)

        start_v = sum(len(x) for x in all_m_verts)
        all_m_verts.append(verts)
        mesh_slices.append((m_idx, pa, p_off, p_stride, v_cnt, start_v, tris))

    V = np.vstack(all_m_verts)

    # Pre-Stage: Align foot & ankle muscle pose (y < 0.145) with skin foot envelope
    foot_m = V[:, 1] < 0.145
    t_foot = np.clip((0.145 - V[foot_m, 1]) / 0.105, 0.0, 1.0)
    V[foot_m, 2] -= 0.0165 * t_foot
    # Keep intrinsic plantar muscles safely above the sole skin arch
    sole_m = (V[:, 1] < 0.035) & (V[:, 2] < 0.065)
    V[sole_m, 1] = np.maximum(V[sole_m, 1], 0.0115)
    fore_m = (V[:, 1] < 0.025) & (V[:, 2] >= 0.065)
    V[fore_m, 1] = np.maximum(V[fore_m, 1], 0.0045)

    # Precompute interior cross-section centers for lower legs (0.075 <= y < 0.50) and feet (y < 0.085)
    def pull_leg_foot_toward_interior(verts):
        for side in (-1.0, 1.0):
            # 1. Lower leg & ankle slices along Y (0.065 <= y < 0.48)
            for y0 in np.linspace(0.065, 0.46, 24):
                y1 = y0 + 0.018
                s_sl = sp_all[(sp_all[:, 0] * side > 0) & (sp_all[:, 1] >= y0) & (sp_all[:, 1] < y1)]
                if len(s_sl) < 10:
                    continue
                cx = 0.5 * (np.percentile(s_sl[:, 0], 8) + np.percentile(s_sl[:, 0], 92))
                cz = 0.5 * (np.percentile(s_sl[:, 2], 8) + np.percentile(s_sl[:, 2], 92))
                rx = max(0.012, 0.5 * (np.percentile(s_sl[:, 0], 92) - np.percentile(s_sl[:, 0], 8)) - 0.0055)
                rz = max(0.012, 0.5 * (np.percentile(s_sl[:, 2], 92) - np.percentile(s_sl[:, 2], 8)) - 0.0055)
                m_idx = np.where((verts[:, 0] * side > 0) & (verts[:, 1] >= y0) & (verts[:, 1] < y1))[0]
                if len(m_idx) == 0:
                    continue
                dx = (verts[m_idx, 0] - cx) / rx
                dz = (verts[m_idx, 2] - cz) / rz
                rad = np.sqrt(dx * dx + dz * dz)
                out = rad > 0.92
                if np.any(out):
                    scale = np.minimum(0.90, 0.88 / rad[out])
                    verts[m_idx[out], 0] = cx + (verts[m_idx[out], 0] - cx) * scale
                    verts[m_idx[out], 2] = cz + (verts[m_idx[out], 2] - cz) * scale

            # 2. Foot slices along Z (-0.09 <= z <= 0.135, y < 0.085)
            for z0 in np.linspace(-0.090, 0.120, 28):
                z1 = z0 + 0.009
                s_sl = sp_all[(sp_all[:, 0] * side > 0) & (sp_all[:, 1] < 0.090) & (sp_all[:, 2] >= z0) & (sp_all[:, 2] < z1)]
                if len(s_sl) < 10:
                    continue
                xmin, xmax = np.percentile(s_sl[:, 0], 6), np.percentile(s_sl[:, 0], 94)
                ymin, ymax = np.percentile(s_sl[:, 1], 6), np.percentile(s_sl[:, 1], 94)
                if xmin > xmax:
                    xmin, xmax = xmax, xmin
                cx = 0.5 * (xmin + xmax)
                cy = 0.5 * (ymin + ymax)
                rx = max(0.006, 0.5 * (xmax - xmin) - 0.0045)
                ry = max(0.004, 0.5 * (ymax - ymin) - 0.0045)
                m_idx = np.where((verts[:, 0] * side > 0) & (verts[:, 1] < 0.085) & (verts[:, 2] >= z0) & (verts[:, 2] < z1))[0]
                if len(m_idx) == 0:
                    continue
                verts[m_idx, 0] = np.clip(verts[m_idx, 0], cx - rx, cx + rx)
                verts[m_idx, 1] = np.clip(verts[m_idx, 1], cy - ry, cy + ry)

    pull_leg_foot_toward_interior(V)

    # Pre-tuck any muscle vertices bridging across the cleaned armpit cleft (1.18 < y < 1.365, 0.132 < |x| < 0.186)
    ap_cleft = (V[:, 1] > 1.18) & (V[:, 1] < 1.365) & (np.abs(V[:, 0]) > 0.132) & (np.abs(V[:, 0]) < 0.186)
    if np.any(ap_cleft):
        V[ap_cleft, 1] = np.maximum(V[ap_cleft, 1], 1.364)

    # Stage 1: Iterative 3D cKDTree surface tucking (6 passes)
    for _pass in range(6):
        dists, idxs = kdtree.query(V, k=1, distance_upper_bound=0.065)
        valid = idxs < len(sp_all)
        s_pts = sp_all[idxs[valid]]
        s_nms = sn_all[idxs[valid]]
        v_sub = V[valid]

        diff = v_sub - s_pts
        dots = np.sum(diff * s_nms, axis=1)

        margins = np.full(len(v_sub), -0.0055, dtype=np.float32)
        margins[v_sub[:, 1] > 1.48] = -0.0095
        margins[(v_sub[:, 1] > 1.18) & (v_sub[:, 1] < 1.40) & (np.abs(v_sub[:, 0]) > 0.11) & (np.abs(v_sub[:, 0]) < 0.22)] = -0.0115
        margins[(v_sub[:, 1] > 0.68) & (v_sub[:, 1] < 1.22) & (np.abs(v_sub[:, 0]) > 0.155)] = -0.0075
        margins[(v_sub[:, 1] > 0.78) & (v_sub[:, 1] < 0.91) & (np.abs(v_sub[:, 0]) < 0.11)] = -0.0085
        margins[v_sub[:, 1] < 0.45] = -0.0065
        margins[v_sub[:, 1] < 0.14] = -0.0050

        need_tuck = dots > margins
        push = (dots[need_tuck] - margins[need_tuck])[:, None] * s_nms[need_tuck]
        v_sub[need_tuck] -= push
        V[valid] = v_sub
        pull_leg_foot_toward_interior(V)

    # Stage 2: Exact Screen-Space Z-Buffer Tucking & Verification Render (WB=700, HB=800)
    WB, HB = 700, 800
    img_skin = np.full((HB, WB, 3), [15, 23, 42], dtype=np.uint8)
    zbuf_skin = np.full((HB, WB), -999.0, dtype=np.float32)

    for angle, cx_off in [(0.0, 175), (math.pi, 525)]:
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        for a, b, c in skin_tris:
            va_s, vb_s, vc_s = skin_pos[a], skin_pos[b], skin_pos[c]
            ra = (va_s[0] * cos_a + va_s[2] * sin_a, va_s[1], -va_s[0] * sin_a + va_s[2] * cos_a)
            rb = (vb_s[0] * cos_a + vb_s[2] * sin_a, vb_s[1], -vb_s[0] * sin_a + vb_s[2] * cos_a)
            rc = (vc_s[0] * cos_a + vc_s[2] * sin_a, vc_s[1], -vc_s[0] * sin_a + vc_s[2] * cos_a)
            if (rb[0] - ra[0]) * (rc[1] - ra[1]) - (rb[1] - ra[1]) * (rc[0] - ra[0]) <= 0:
                continue

            na_s, nb_s, nc_s = skin_norm[a], skin_norm[b], skin_norm[c]
            rna = (na_s[0] * cos_a + na_s[2] * sin_a, na_s[1], -na_s[0] * sin_a + na_s[2] * cos_a)
            rnb = (nb_s[0] * cos_a + nb_s[2] * sin_a, nb_s[1], -nb_s[0] * sin_a + nb_s[2] * cos_a)
            rnc = (nc_s[0] * cos_a + nc_s[2] * sin_a, nc_s[1], -nc_s[0] * sin_a + nc_s[2] * cos_a)

            x0 = int((ra[0] / 0.34) * 155 + cx_off)
            y0 = int(((1.76 - ra[1]) / 1.80) * (HB * 0.92) + HB * 0.04)
            x1 = int((rb[0] / 0.34) * 155 + cx_off)
            y1 = int(((1.76 - rb[1]) / 1.80) * (HB * 0.92) + HB * 0.04)
            x2 = int((rc[0] / 0.34) * 155 + cx_off)
            y2 = int(((1.76 - rc[1]) / 1.80) * (HB * 0.92) + HB * 0.04)

            min_x, max_x = max(cx_off - 165, min(x0, x1, x2)), min(cx_off + 165, max(x0, x1, x2))
            min_y, max_y = max(0, min(y0, y1, y2)), min(HB - 1, max(y0, y1, y2))
            if min_x > max_x or min_y > max_y:
                continue
            denom = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
            if denom == 0:
                continue
            inv_d = 1.0 / denom
            for py in range(min_y, max_y + 1):
                for px in range(min_x, max_x + 1):
                    w0 = ((y1 - y2) * (px - x2) + (x2 - x1) * (py - y2)) * inv_d
                    w1 = ((y2 - y0) * (px - x2) + (x0 - x2) * (py - y2)) * inv_d
                    w2 = 1.0 - w0 - w1
                    if w0 >= 0 and w1 >= 0 and w2 >= 0:
                        zz = w0 * ra[2] + w1 * rb[2] + w2 * rc[2]
                        if zz > zbuf_skin[py, px]:
                            zbuf_skin[py, px] = zz
                            nx = w0 * rna[0] + w1 * rnb[0] + w2 * rnc[0]
                            ny = w0 * rna[1] + w1 * rnb[1] + w2 * rnc[1]
                            nz = w0 * rna[2] + w1 * rnb[2] + w2 * rnc[2]
                            nl = math.hypot(nx, ny, nz) or 1.0
                            diff = max(0.0, (nx * 0.2 + ny * 0.25 + nz * 0.94) / nl)
                            val = min(1.0, 0.24 + 0.72 * diff)
                            img_skin[py, px, 0] = int(238 * val)
                            img_skin[py, px, 1] = int(184 * val)
                            img_skin[py, px, 2] = int(152 * val)

    # Run 3 fast passes of exact Z-buffer tucking against zbuf_skin
    for _iter in range(3):
        for angle, cx_off in [(0.0, 175), (math.pi, 525)]:
            cos_a, sin_a = math.cos(angle), math.sin(angle)
            v_push_z = np.zeros(len(V), dtype=np.float32)
            v_armpit_sil = np.zeros(len(V), dtype=bool)

            for _, _, _, _, v_cnt, start_v, tris in mesh_slices:
                for a_l, b_l, c_l in tris:
                    ia, ib, ic = start_v + a_l, start_v + b_l, start_v + c_l
                    va_m, vb_m, vc_m = V[ia], V[ib], V[ic]
                    ra = (va_m[0] * cos_a + va_m[2] * sin_a, va_m[1], -va_m[0] * sin_a + va_m[2] * cos_a)
                    rb = (vb_m[0] * cos_a + vb_m[2] * sin_a, vb_m[1], -vb_m[0] * sin_a + vb_m[2] * cos_a)
                    rc = (vc_m[0] * cos_a + vc_m[2] * sin_a, vc_m[1], -vc_m[0] * sin_a + vc_m[2] * cos_a)

                    x0 = int((ra[0] / 0.34) * 155 + cx_off)
                    y0 = int(((1.76 - ra[1]) / 1.80) * (HB * 0.92) + HB * 0.04)
                    x1 = int((rb[0] / 0.34) * 155 + cx_off)
                    y1 = int(((1.76 - rb[1]) / 1.80) * (HB * 0.92) + HB * 0.04)
                    x2 = int((rc[0] / 0.34) * 155 + cx_off)
                    y2 = int(((1.76 - rc[1]) / 1.80) * (HB * 0.92) + HB * 0.04)

                    min_x, max_x = max(cx_off - 165, min(x0, x1, x2)), min(cx_off + 165, max(x0, x1, x2))
                    min_y, max_y = max(0, min(y0, y1, y2)), min(HB - 1, max(y0, y1, y2))
                    if min_x > max_x or min_y > max_y:
                        continue
                    denom = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
                    if denom == 0:
                        continue
                    inv_d = 1.0 / denom
                    max_ex = 0.0
                    out_sil = False
                    for py in range(min_y, max_y + 1):
                        for px in range(min_x, max_x + 1):
                            w0 = ((y1 - y2) * (px - x2) + (x2 - x1) * (py - y2)) * inv_d
                            w1 = ((y2 - y0) * (px - x2) + (x0 - x2) * (py - y2)) * inv_d
                            w2 = 1.0 - w0 - w1
                            if w0 >= 0 and w1 >= 0 and w2 >= 0:
                                sf = zbuf_skin[py, px]
                                if sf <= -900.0:
                                    out_sil = True
                                else:
                                    zz = w0 * ra[2] + w1 * rb[2] + w2 * rc[2]
                                    ex = zz - (sf - 0.003)
                                    if ex > max_ex:
                                        max_ex = ex
                    if max_ex > 0.0 and max_ex < 0.055:
                        for idx_v in (ia, ib, ic):
                            if max_ex + 0.0035 > v_push_z[idx_v]:
                                v_push_z[idx_v] = max_ex + 0.0035
                    if out_sil:
                        for idx_v in (ia, ib, ic):
                            v_armpit_sil[idx_v] = True

            push_m = (v_push_z > 0) & (V[:, 1] >= 0.125)
            V[push_m, 2] -= v_push_z[push_m] * cos_a

            if np.any(v_armpit_sil):
                v_s = V[v_armpit_sil]
                # For armpit bridge (1.16 < y < 1.368, 0.105 < |x| < 0.205), lift Y up into axillary dome
                ap = (v_s[:, 1] > 1.16) & (v_s[:, 1] < 1.368) & (np.abs(v_s[:, 0]) > 0.105) & (np.abs(v_s[:, 0]) < 0.205)
                if np.any(ap):
                    v_ap = v_s[ap]
                    v_ap[:, 1] = np.maximum(v_ap[:, 1], 1.362)
                    v_s[ap] = v_ap
                _, idxs_s = kdtree.query(v_s, k=1)
                v_s = sp_all[idxs_s] - 0.0075 * sn_all[idxs_s]
                V[v_armpit_sil] = v_s

            pull_leg_foot_toward_interior(V)
            leg_sub_idx = np.where(V[:, 1] < 0.45)[0]
            _, idxs_l = kdtree.query(V[leg_sub_idx], k=1)
            s_pts_l = sp_all[idxs_l]
            s_nms_l = sn_all[idxs_l]
            dots_l = np.sum((V[leg_sub_idx] - s_pts_l) * s_nms_l, axis=1)
            over_l = dots_l > -0.0050
            if np.any(over_l):
                V[leg_sub_idx[over_l]] -= (dots_l[over_l] - (-0.0055))[:, None] * s_nms_l[over_l]
            pull_leg_foot_toward_interior(V)

    # Save muscles.glb
    for m_idx, pa, p_off, p_stride, v_cnt, start_v, tris in mesh_slices:
        verts_w = V[start_v : start_v + v_cnt]
        verts_l = np.empty_like(verts_w)
        verts_l[:, 0] = verts_w[:, 0] / SCALE
        verts_l[:, 1] = (verts_w[:, 1] - OFFSET_Y) / SCALE
        verts_l[:, 2] = verts_w[:, 2] / SCALE
        for i in range(v_cnt):
            struct.pack_into(
                "<fff",
                m_buf,
                p_off + i * p_stride,
                float(verts_l[i, 0]),
                float(verts_l[i, 1]),
                float(verts_l[i, 2]),
            )

    with open(MUSC_OUT, "wb") as f:
        f.write(m_buf)
    print(f"✓ Đã xuất {MUSC_OUT} ({os.path.getsize(MUSC_OUT)/1024/1024:.2f} MB)")

    # Final verification render
    img_b = img_skin.copy()
    zbuf_b = zbuf_skin.copy()
    red_pixels = 0
    for angle, cx_off in [(0.0, 175), (math.pi, 525)]:
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        for _, _, _, _, v_cnt, start_v, tris in mesh_slices:
            for a_l, b_l, c_l in tris:
                va, vb, vc = V[start_v + a_l], V[start_v + b_l], V[start_v + c_l]
                ra = (va[0] * cos_a + va[2] * sin_a, va[1], -va[0] * sin_a + va[2] * cos_a)
                rb = (vb[0] * cos_a + vb[2] * sin_a, vb[1], -vb[0] * sin_a + vb[2] * cos_a)
                rc = (vc[0] * cos_a + vc[2] * sin_a, vc_s[1] if False else vc[1], -vc[0] * sin_a + vc[2] * cos_a)

                x0 = int((ra[0] / 0.34) * 155 + cx_off)
                y0 = int(((1.76 - ra[1]) / 1.80) * (HB * 0.92) + HB * 0.04)
                x1 = int((rb[0] / 0.34) * 155 + cx_off)
                y1 = int(((1.76 - rb[1]) / 1.80) * (HB * 0.92) + HB * 0.04)
                x2 = int((rc[0] / 0.34) * 155 + cx_off)
                y2 = int(((1.76 - rc[1]) / 1.80) * (HB * 0.92) + HB * 0.04)

                min_x, max_x = max(cx_off - 165, min(x0, x1, x2)), min(cx_off + 165, max(x0, x1, x2))
                min_y, max_y = max(0, min(y0, y1, y2)), min(HB - 1, max(y0, y1, y2))
                if min_x > max_x or min_y > max_y:
                    continue
                denom = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
                if denom == 0:
                    continue
                inv_d = 1.0 / denom
                for py in range(min_y, max_y + 1):
                    for px in range(min_x, max_x + 1):
                        w0 = ((y1 - y2) * (px - x2) + (x2 - x1) * (py - y2)) * inv_d
                        w1 = ((y2 - y0) * (px - x2) + (x0 - x2) * (py - y2)) * inv_d
                        w2 = 1.0 - w0 - w1
                        if w0 >= 0 and w1 >= 0 and w2 >= 0:
                            zz = w0 * ra[2] + w1 * rb[2] + w2 * rc[2]
                            if zz > zbuf_b[py, px]:
                                zbuf_b[py, px] = zz
                                red_pixels += 1
                                img_b[py, px] = [225, 45, 45]

    Image.fromarray(img_b).save(os.path.join(ARTIFACT_DIR, "final_body_with_muscles.png"))
    print(f"✓ Số điểm ảnh cơ lộ ra ngoài da trên toàn thân (Mặt trước + Mặt sau): {red_pixels} px")


if __name__ == "__main__":
    s_pos, s_norm, s_tris = load_skin()
    tuck_muscles_and_verify(s_pos, s_norm, s_tris)
