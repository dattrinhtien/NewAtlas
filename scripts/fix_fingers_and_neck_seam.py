"""
Fix anatomical model human-learning.glb:
1. Plump and round fingertips of fingers 3 and 4 (Middle and Ring fingers) on both hands.
2. Eliminate the visible neck crease ring by dense triangle projection and submerged rim blending.
"""
import os
import struct
import json
import math
import numpy as np
from scipy.spatial import cKDTree

WORKSPACE = "/Volumes/D/Hoc Python/NewAtlas"
HL_PATH = os.path.join(WORKSPACE, "web/models/human-learning.glb")

def run_fix():
    with open(HL_PATH, "rb") as f:
        hb = bytearray(f.read())
    jlen = struct.unpack("<I", hb[12:16])[0]
    hg = json.loads(hb[20:20 + jlen].decode("utf-8"))
    boff = 20 + jlen + 8

    vcnt = hg["accessors"][0]["count"]
    icnt = hg["accessors"][2]["count"]
    n_off = hg["bufferViews"][1]["byteOffset"]
    i_off = hg["bufferViews"][2]["byteOffset"]

    pos = np.frombuffer(hb, dtype=np.float32, count=vcnt * 3, offset=boff).reshape(-1, 3).copy()
    norm = np.frombuffer(hb, dtype=np.float32, count=vcnt * 3, offset=boff + n_off).reshape(-1, 3).copy()
    tris = np.frombuffer(hb, dtype=np.uint32, count=icnt, offset=boff + i_off).reshape(-1, 3).copy()
    hl_start = vcnt - 13380 # 8598

    adj = [[] for _ in range(vcnt)]
    for a, b, c in tris:
        adj[a].extend((b, c))
        adj[b].extend((a, c))
        adj[c].extend((a, b))
    adj = [list(set(nb)) for nb in adj]

    # 1. Round out fingertips of fingers 3 and 4 on both hands
    d_defs = [
        ("Ngón 3 (Giữa)", 0.282, 0.312, 0.016, 0.0045, 0.0075),
        ("Ngón 4 (Áp út)", 0.256, 0.288, 0.015, 0.0040, 0.0068),
    ]

    for sign in [-1.0, 1.0]:
        for dname, xmin, xmax, pad_len, tip_min_r, shaft_r in d_defs:
            m = (sign * pos[:, 0] >= xmin) & (sign * pos[:, 0] <= xmax) & (pos[:, 1] <= 0.745)
            d_idx = np.where(m)[0]
            if len(d_idx) == 0:
                continue
            ymin = pos[d_idx, 1].min()

            shaft_m = d_idx[(pos[d_idx, 1] >= ymin + 0.010) & (pos[d_idx, 1] <= ymin + 0.022)]
            if len(shaft_m) > 0:
                scx = np.mean(pos[shaft_m, 0])
                scz = np.mean(pos[shaft_m, 2])
            else:
                scx = np.mean(pos[d_idx, 0])
                scz = np.mean(pos[d_idx, 2])

            tip_verts = d_idx[pos[d_idx, 1] <= ymin + pad_len]
            for v in tip_verts:
                y = pos[v, 1]
                t = max(0.0, min(1.0, (y - ymin) / pad_len))
                target_r = tip_min_r + (shaft_r - tip_min_r) * math.sqrt(t)

                cz_pulp = scz + (0.0022 * (1.0 - t))
                dx = pos[v, 0] - scx
                dz = pos[v, 2] - cz_pulp
                r = math.hypot(dx, dz)

                if r < target_r:
                    sc = (r * 0.15 + target_r * 0.85) / (r + 1e-6)
                    pos[v, 0] = scx + dx * sc
                    pos[v, 2] = cz_pulp + dz * sc

                if y < ymin + 0.0025:
                    lift = 0.0012 * (1.0 - (y - ymin) / 0.0025) ** 2
                    pos[v, 1] += lift

    for sign in [-1.0, 1.0]:
        for dname, xmin, xmax, pad_len, _, _ in d_defs:
            m = (sign * pos[:, 0] >= xmin - 0.002) & (sign * pos[:, 0] <= xmax + 0.002) & (pos[:, 1] <= 0.742)
            d_idx = np.where(m)[0]
            for it in range(6):
                new_pos = pos.copy()
                w = 0.38 if (it % 2 == 0) else -0.34
                for u in d_idx:
                    nbs = [nb for nb in adj[u] if nb in d_idx]
                    if len(nbs) >= 3:
                        new_pos[u] = pos[u] + w * (np.mean(pos[nbs], axis=0) - pos[u])
                pos = new_pos

    # 2. Dense triangle sampling for seamless neck fusion
    hl_tris_neck = []
    for a, b, c in tris:
        if a >= hl_start and b >= hl_start and c >= hl_start:
            y_max = max(pos[a, 1], pos[b, 1], pos[c, 1])
            y_min = min(pos[a, 1], pos[b, 1], pos[c, 1])
            if y_max >= 1.478 and y_min <= 1.530 and max(abs(pos[a, 0]), abs(pos[b, 0]), abs(pos[c, 0])) < 0.10:
                hl_tris_neck.append((a, b, c))

    sample_pts = []
    sample_norms = []
    np.random.seed(42)
    for a, b, c in hl_tris_neck:
        va, vb, vc = pos[a], pos[b], pos[c]
        na, nb, nc = norm[a], norm[b], norm[c]
        tri_fn = np.cross(vb - va, vc - va)
        area = np.linalg.norm(tri_fn) * 0.5
        n_samples = max(4, int(area * 400000))
        r1 = np.random.uniform(0, 1, n_samples)
        r2 = np.random.uniform(0, 1, n_samples)
        sqrt_r1 = np.sqrt(r1)
        w0 = 1.0 - sqrt_r1
        w1 = sqrt_r1 * (1.0 - r2)
        w2 = sqrt_r1 * r2
        pts = w0[:, None] * va + w1[:, None] * vb + w2[:, None] * vc
        norms = w0[:, None] * na + w1[:, None] * nb + w2[:, None] * nc
        norms /= np.linalg.norm(norms, axis=1, keepdims=True) + 1e-8
        sample_pts.append(pts)
        sample_norms.append(norms)

    sample_pts = np.vstack(sample_pts)
    sample_norms = np.vstack(sample_norms)
    hl_surf_tree = cKDTree(sample_pts)

    za_neck_idx = np.where((np.arange(vcnt) < hl_start) & (pos[:, 1] >= 1.492) & (pos[:, 1] <= 1.525) & (np.abs(pos[:, 0]) < 0.095))[0]
    dists, nearest = hl_surf_tree.query(pos[za_neck_idx])
    
    for k, idx in enumerate(za_neck_idx):
        y = pos[idx, 1]
        t_near_pos = sample_pts[nearest[k]]
        t_near_norm = sample_norms[nearest[k]]
        w = max(0.0, min(1.0, (1.520 - y) / 0.016))
        w = w * w * (3.0 - 2.0 * w)
        tuck = 0.00035 * max(0.0, min(1.0, (1.506 - y) / 0.008))
        target_pos = t_near_pos - t_near_norm * tuck
        pos[idx] = pos[idx] * (1.0 - w) + target_pos * w

    za_tris_neck = []
    for a, b, c in tris:
        if a < hl_start and b < hl_start and c < hl_start:
            y_max = max(pos[a, 1], pos[b, 1], pos[c, 1])
            y_min = min(pos[a, 1], pos[b, 1], pos[c, 1])
            if y_max >= 1.502 and y_min <= 1.540 and max(abs(pos[a, 0]), abs(pos[b, 0]), abs(pos[c, 0])) < 0.095:
                za_tris_neck.append((a, b, c))

    sample_za_pts = []
    sample_za_norms = []
    for a, b, c in za_tris_neck:
        va, vb, vc = pos[a], pos[b], pos[c]
        na, nb, nc = norm[a], norm[b], norm[c]
        tri_fn = np.cross(vb - va, vc - va)
        area = np.linalg.norm(tri_fn) * 0.5
        n_samples = max(4, int(area * 400000))
        r1 = np.random.uniform(0, 1, n_samples)
        r2 = np.random.uniform(0, 1, n_samples)
        sqrt_r1 = np.sqrt(r1)
        w0 = 1.0 - sqrt_r1
        w1 = sqrt_r1 * (1.0 - r2)
        w2 = sqrt_r1 * r2
        pts = w0[:, None] * va + w1[:, None] * vb + w2[:, None] * vc
        norms = w0[:, None] * na + w1[:, None] * nb + w2[:, None] * nc
        norms /= np.linalg.norm(norms, axis=1, keepdims=True) + 1e-8
        sample_za_pts.append(pts)
        sample_za_norms.append(norms)

    sample_za_pts = np.vstack(sample_za_pts)
    sample_za_norms = np.vstack(sample_za_norms)
    za_surf_tree = cKDTree(sample_za_pts)

    hl_neck_idx = np.where((np.arange(vcnt) >= hl_start) & (pos[:, 1] >= 1.508) & (pos[:, 1] <= 1.535) & (np.abs(pos[:, 0]) < 0.095))[0]
    dists_hl, nearest_za = za_surf_tree.query(pos[hl_neck_idx])
    for k, idx in enumerate(hl_neck_idx):
        y = pos[idx, 1]
        t_near_pos = sample_za_pts[nearest_za[k]]
        t_near_norm = sample_za_norms[nearest_za[k]]
        w = max(0.0, min(1.0, (y - 1.508) / 0.015))
        w = w * w * (3.0 - 2.0 * w)
        tuck = 0.00035 * max(0.0, min(1.0, (y - 1.512) / 0.010))
        target_pos = t_near_pos - t_near_norm * tuck
        pos[idx] = pos[idx] * (1.0 - w) + target_pos * w

    # 3. Unified normal recomputation
    va_m = pos[tris[:, 0]]
    vb_m = pos[tris[:, 1]]
    vc_m = pos[tris[:, 2]]
    fn_m = np.cross(vb_m - va_m, vc_m - va_m)

    v_n = np.zeros_like(norm)
    for t_i in range(len(tris)):
        a, b, c = tris[t_i]
        f_n = fn_m[t_i]
        v_n[a] += f_n
        v_n[b] += f_n
        v_n[c] += f_n

    for i in range(vcnt):
        nl = np.linalg.norm(v_n[i])
        if nl > 1e-8:
            norm[i] = v_n[i] / nl

    neck_all_mask = (pos[:, 1] >= 1.485) & (pos[:, 1] <= 1.532) & (np.abs(pos[:, 0]) < 0.092)
    neck_all_idx = np.where(neck_all_mask)[0]
    neck_tree = cKDTree(pos[neck_all_idx])
    for _it in range(3):
        new_norm = norm.copy()
        for idx in neck_all_idx:
            near = neck_tree.query_ball_point(pos[idx], r=0.010)
            if len(near) >= 2:
                avg_n = np.mean(norm[neck_all_idx[near]], axis=0)
                nl = np.linalg.norm(avg_n)
                if nl > 1e-8:
                    new_norm[idx] = norm[idx] * 0.35 + (avg_n / nl) * 0.65
                    nl_fin = np.linalg.norm(new_norm[idx])
                    if nl_fin > 1e-8:
                        new_norm[idx] /= nl_fin
        norm = new_norm

    for i in range(vcnt):
        struct.pack_into("<fff", hb, boff + i * 12, float(pos[i, 0]), float(pos[i, 1]), float(pos[i, 2]))
        struct.pack_into("<fff", hb, boff + n_off + i * 12, float(norm[i, 0]), float(norm[i, 1]), float(norm[i, 2]))

    with open(HL_PATH, "wb") as f:
        f.write(hb)
    print("✓ Model saved successfully!")

if __name__ == "__main__":
    run_fix()
