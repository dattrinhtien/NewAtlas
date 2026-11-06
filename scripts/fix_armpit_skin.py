import os
import struct
import json
import math
from collections import deque
import numpy as np
from scipy.spatial import cKDTree
from PIL import Image

WORKSPACE = "/Volumes/D/Hoc Python/NewAtlas"
HL_PATH = os.path.join(WORKSPACE, "web/models/human-learning.glb")
ARTIFACT_DIR = "/Users/wildwindhill/.gemini/antigravity/brain/72f325f7-6943-46bf-9108-f60a6a751dd3"


def fix_armpit_mesh():
    with open(HL_PATH, "rb") as f:
        hb = bytearray(f.read())
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

    # MakeHuman body vertices are the last 13380 vertices; Z-Anatomy head/neck are 0..hl_start-1
    hl_start = vcnt - 13380

    # Build adjacency graph for all MakeHuman body/neck vertices (i >= hl_start)
    adj = [[] for _ in range(vcnt)]
    for a, b, c in tris:
        if a >= hl_start and b >= hl_start and c >= hl_start:
            adj[a].extend((b, c))
            adj[b].extend((a, c))
            adj[c].extend((a, b))
    adj = [list(set(nb)) for nb in adj]

    def bfs_dist(seeds, y_cut=1.358):
        dist = np.full(vcnt, 9999, dtype=int)
        q = deque()
        for s in seeds:
            dist[s] = 0
            q.append(s)
        while q:
            u = q.popleft()
            if pos[u, 1] > y_cut:
                continue
            for v in adj[u]:
                if dist[v] > dist[u] + 1:
                    dist[v] = dist[u] + 1
                    q.append(v)
        return dist

    torso_seeds = np.where((np.arange(vcnt) >= hl_start) & (pos[:, 1] > 1.00) & (pos[:, 1] < 1.12) & (np.abs(pos[:, 0]) < 0.145))[0]
    arm_seeds = np.where((np.arange(vcnt) >= hl_start) & (pos[:, 1] > 1.00) & (pos[:, 1] < 1.12) & (np.abs(pos[:, 0]) > 0.165))[0]
    d_torso = bfs_dist(torso_seeds, 1.348)
    d_arm = bfs_dist(arm_seeds, 1.348)

    is_torso = d_torso < 9999
    is_arm = d_arm < 9999

    # -------------------------------------------------------------------------
    # 1. ARMPITS ("hõm 2 nách"): Retract webbed inner-arm flap & smooth dome
    # -------------------------------------------------------------------------
    for i in range(hl_start, vcnt):
        x, y, z = pos[i]
        ax = abs(x)
        if 1.16 < y < 1.360:
            if is_arm[i] and ax < 0.215:
                t = max(0.0, min(1.0, (y - 1.16) / (1.352 - 1.16)))
                min_ax = 0.180 * (1.0 - t) + 0.164 * t
                if ax < min_ax:
                    pos[i, 0] = math.copysign(min_ax, x)
                if z < -0.070 and abs(pos[i, 0]) < 0.182:
                    pos[i, 2] = -0.070 + (z + 0.070) * 0.30
            elif is_torso[i] and 0.120 < ax < 0.200:
                t = max(0.0, min(1.0, (y - 1.16) / (1.352 - 1.16)))
                max_tx = 0.130 * (1.0 - t) + 0.143 * t
                if ax > max_tx:
                    pos[i, 0] = math.copysign(max_tx, x)

    smooth_weights = np.zeros(vcnt, dtype=np.float32)
    for i in range(hl_start, vcnt):
        x, y, z = pos[i]
        ax = abs(x)
        if 1.17 < y < 1.415 and 0.118 < ax < 0.205 and len(adj[i]) >= 3:
            wy = min((y - 1.17) / 0.03, (1.415 - y) / 0.03, 1.0)
            wx = min((ax - 0.118) / 0.015, (0.205 - ax) / 0.015, 1.0)
            smooth_weights[i] = max(0.0, min(1.0, wy * wx))

    active_armpit = np.where(smooth_weights > 0.01)[0]
    for _step in range(18):
        new_pos = pos.copy()
        for i in active_armpit:
            nbs = adj[i]
            mean_p = np.mean(pos[nbs], axis=0)
            w = 0.52 * smooth_weights[i]
            new_pos[i] = pos[i] * (1.0 - w) + mean_p * w
            y_cur = new_pos[i, 1]
            ax_cur = abs(new_pos[i, 0])
            if y_cur < 1.345:
                if is_arm[i]:
                    t = max(0.0, min(1.0, (y_cur - 1.16) / (1.345 - 1.16)))
                    min_ax = 0.179 * (1.0 - t) + 0.164 * t
                    if ax_cur < min_ax:
                        new_pos[i, 0] = math.copysign(min_ax, new_pos[i, 0])
                elif is_torso[i]:
                    t = max(0.0, min(1.0, (y_cur - 1.16) / (1.345 - 1.16)))
                    max_tx = 0.130 * (1.0 - t) + 0.142 * t
                    if ax_cur > max_tx:
                        new_pos[i, 0] = math.copysign(max_tx, new_pos[i, 0])
        pos = new_pos

    # -------------------------------------------------------------------------
    # 2. NECK & NAPE ("cổ gáy"): Seamless radial & normal fusion between ZA & HL
    # -------------------------------------------------------------------------
    neck_hl_idx = np.where(
        (np.arange(vcnt) >= hl_start)
        & (pos[:, 1] > 1.445)
        & (pos[:, 1] < 1.524)
        & (np.abs(pos[:, 0]) < 0.095)
        & ~((pos[:, 1] > 1.514) & (pos[:, 2] > 0.034))
    )[0]
    for _it in range(14):
        new_pos = pos.copy()
        w = 0.50 if (_it % 2 == 0) else -0.32
        for u in neck_hl_idx:
            nbs = [v for v in adj[u] if not (pos[v, 1] > 1.516 and pos[v, 2] > 0.036)]
            if len(nbs) >= 3:
                wy = min(1.0, max(0.0, (pos[u, 1] - 1.445) / 0.025))
                new_pos[u] = pos[u] + (w * wy) * (np.mean(pos[nbs], axis=0) - pos[u])
        pos = new_pos

    # Match ZA lower neck (1.496 < Y < 1.532) and smoothed HL upper neck (1.485 < Y < 1.525) onto a single shared smooth surface
    cz_neck = -0.020
    za_neck_idx = np.where((np.arange(vcnt) < hl_start) & (pos[:, 1] > 1.495) & (pos[:, 1] < 1.535))[0]
    hl_neck_band = np.where(
        (np.arange(vcnt) >= hl_start)
        & (pos[:, 1] > 1.480)
        & (pos[:, 1] < 1.526)
        & (np.abs(pos[:, 0]) < 0.092)
        & ~((pos[:, 1] > 1.514) & (pos[:, 2] > 0.034))
    )[0]

    # Sample clean upper ZA neck (1.516 <= Y <= 1.534) and clean lower HL neck (1.480 <= Y <= 1.500)
    shared_samples = []
    for i in za_neck_idx:
        if 1.516 <= pos[i, 1] <= 1.534:
            dx, dz = pos[i, 0], pos[i, 2] - cz_neck
            shared_samples.append((math.atan2(dx, dz), pos[i, 1], math.hypot(dx, dz)))
    for i in hl_neck_band:
        if 1.480 <= pos[i, 1] <= 1.500:
            dx, dz = pos[i, 0], pos[i, 2] - cz_neck
            shared_samples.append((math.atan2(dx, dz), pos[i, 1], math.hypot(dx, dz)))

    def eval_shared_neck_r(ang, y_q):
        num, den = 0.0, 0.0
        for sang, sy, srad in shared_samples:
            da = math.atan2(math.sin(ang - sang), math.cos(ang - sang))
            dy = (y_q - sy) * 9.0
            d2 = da * da + dy * dy + 0.0035
            wt = 1.0 / (d2 * d2)
            num += srad * wt
            den += wt
        return num / den if den > 0 else 0.055

    # Conform ZA neck (1.495 < Y < 1.528) to shared surface
    for i in za_neck_idx:
        x, y, z = pos[i]
        if y < 1.528:
            dx, dz = x, z - cz_neck
            ang = math.atan2(dx, dz)
            cur_r = math.hypot(dx, dz)
            sh_r = eval_shared_neck_r(ang, y)
            w = max(0.0, min(1.0, (1.528 - y) / 0.024))
            w = w * w * (3.0 - 2.0 * w)
            # Tuck ZA bottom edge (< 1.503) 0.15mm inward so it merges invisibly into HL
            offset = -0.00015 if y < 1.503 else 0.00015
            new_r = cur_r * (1.0 - w) + (sh_r + offset) * w
            sc = new_r / (cur_r + 1e-8)
            pos[i, 0] = dx * sc
            pos[i, 2] = cz_neck + dz * sc

    # Conform HL upper neck (1.488 < Y < 1.525) to the exact same shared surface
    for i in hl_neck_band:
        x, y, z = pos[i]
        if y > 1.488:
            dx, dz = x, z - cz_neck
            ang = math.atan2(dx, dz)
            cur_r = math.hypot(dx, dz)
            sh_r = eval_shared_neck_r(ang, y)
            w = max(0.0, min(1.0, (y - 1.488) / 0.016))
            w = w * w * (3.0 - 2.0 * w)
            offset = -0.00025 if y >= 1.503 else 0.0
            new_r = cur_r * (1.0 - w) + (sh_r + offset) * w
            if y >= 1.503:
                new_r = min(new_r, sh_r - 0.0002)
            sc = new_r / (cur_r + 1e-8)
            pos[i, 0] = dx * sc
            pos[i, 2] = cz_neck + dz * sc

    # -------------------------------------------------------------------------
    # 3. ELBOWS ("khuỷu tay"), WRISTS ("cổ bàn tay"), HANDS/FINGERS ("các ngón tay"), KNEES
    # -------------------------------------------------------------------------
    # Collect joint & extremity vertices for volume-preserving Taubin unfolding
    joint_weights = np.zeros(vcnt, dtype=np.float32)
    is_finger_v = np.zeros(vcnt, dtype=bool)
    for i in range(hl_start, vcnt):
        if len(adj[i]) < 3:
            continue
        x, y, z = pos[i]
        ax = abs(x)
        # Elbows: 1.02 < y < 1.21, ax > 0.155
        if 1.02 < y < 1.21 and ax > 0.155:
            wy = min((y - 1.02) / 0.025, (1.21 - y) / 0.025, 1.0)
            joint_weights[i] = max(joint_weights[i], wy)
        # Forearms & Wrists: 0.805 < y <= 1.02, ax > 0.18
        if 0.805 < y <= 1.02 and ax > 0.18:
            # Stronger weight at wrist (0.805 < y < 0.945), gentle transition along forearm
            if y < 0.95:
                wy = min((y - 0.805) / 0.015, (0.95 - y) / 0.025, 1.0)
                joint_weights[i] = max(joint_weights[i], wy)
            else:
                joint_weights[i] = max(joint_weights[i], 0.35)
        # Hands & Fingers: 0.67 < y <= 0.825, ax > 0.21
        if 0.67 < y <= 0.825 and ax > 0.21:
            joint_weights[i] = max(joint_weights[i], 0.85)
            if y < 0.815:
                is_finger_v[i] = True
        # Knees: 0.40 < y < 0.56
        if 0.40 < y < 0.56:
            wy = min((y - 0.40) / 0.025, (0.56 - y) / 0.025, 1.0)
            joint_weights[i] = max(joint_weights[i], wy * 0.85)

    active_joints = np.where(joint_weights > 0.01)[0]
    for it in range(24):
        new_pos = pos.copy()
        for u in active_joints:
            nbs = adj[u]
            mean_p = np.mean(pos[nbs], axis=0)
            jw = joint_weights[u]
            if is_finger_v[u]:
                # Feature-preserving Taubin step for fingers & hands
                w = (0.42 if (it % 2 == 0) else -0.40) * jw
            else:
                # Crease-unfolding Taubin step for elbows, wrists, and knees
                w = (0.55 if (it % 2 == 0) else -0.42) * jw
            new_pos[u] = pos[u] + w * (mean_p - pos[u])
        pos = new_pos

    # -------------------------------------------------------------------------
    # 4. ANKLES, HEELS ("gót chân"), AND FEET ("bàn chân", y < 0.165)
    # -------------------------------------------------------------------------
    orig_norm = norm.copy()
    # Pull down ONLY the inverted midfoot/arch sole vertices (-0.038 < z < 0.075),
    # NEVER squashing the rounded posterior heel (z <= -0.038) or malleoli!
    for i in range(hl_start, vcnt):
        x, y, z = pos[i]
        ny = orig_norm[i, 1]
        if y < 0.088 and -0.038 < z < 0.075 and ny < -0.25:
            # Smooth fade near z = -0.038 so no step between arch and heel pad
            wz = min(1.0, (z - (-0.038)) / 0.018)
            if ny < -0.48 and y > 0.005:
                target_y = 0.004 + (y - 0.004) * 0.08
                pos[i, 1] = y * (1.0 - wz) + target_y * wz
            elif ny < -0.25 and y > 0.012:
                target_y = 0.011 + (y - 0.011) * 0.15
                pos[i, 1] = y * (1.0 - wz) + target_y * wz

    # Run 28 passes of Taubin smoothing across ankle, heel ("gót chân"), and midfoot (y < 0.165, z < 0.075)
    foot_candidates = np.where((np.arange(vcnt) >= hl_start) & (pos[:, 1] < 0.165) & (np.array([len(nb) for nb in adj]) >= 3))[0]
    for it in range(28):
        new_pos = pos.copy()
        for u in foot_candidates:
            # Keep toe tips crisp (z > 0.075)
            if pos[u, 2] > 0.075:
                continue
            nbs = adj[u]
            mean_p = np.mean(pos[nbs], axis=0)
            wy = min(1.0, (0.165 - pos[u, 1]) / 0.025)
            wz = min(1.0, (0.075 - pos[u, 2]) / 0.015)
            w_base = 0.55 if (it % 2 == 0) else -0.36
            w = w_base * wy * wz
            new_pos[u] = pos[u] + w * (mean_p - pos[u])
            # Keep plantar arch flat on floor
            if -0.032 < new_pos[u, 2] < 0.065 and orig_norm[u, 1] < -0.55:
                new_pos[u, 1] = min(new_pos[u, 1], 0.0055)
        pos = new_pos

    # -------------------------------------------------------------------------
    # 5. RECOMPUTE SMOOTH NORMALS & GENTLE SKIN CUSHIONING
    # -------------------------------------------------------------------------
    recalc_mask = np.zeros(vcnt, dtype=bool)
    recalc_mask[hl_start:] = True
    recalc_mask[za_neck_idx] = True

    def compute_vertex_normals(mask):
        v_n = np.zeros_like(norm)
        va_m = pos[tris[:, 0]]
        vb_m = pos[tris[:, 1]]
        vc_m = pos[tris[:, 2]]
        fn_m = np.cross(vb_m - va_m, vc_m - va_m)
        for t_i in range(len(tris)):
            a, b, c = tris[t_i]
            if mask[a] or mask[b] or mask[c]:
                f_n = fn_m[t_i]
                v_n[a] += f_n
                v_n[b] += f_n
                v_n[c] += f_n
        for idx in np.where(mask)[0]:
            nl = np.linalg.norm(v_n[idx])
            if nl > 1e-8:
                norm[idx] = v_n[idx] / nl

    compute_vertex_normals(recalc_mask)

    # Gently expand lower-leg, ankle, heel, and foot skin (y < 0.45) to cover all tendons & muscles
    for i in np.where((np.arange(vcnt) >= hl_start) & (pos[:, 1] < 0.45))[0]:
        x, y, z = pos[i]
        nx, ny, nz = norm[i]
        if z > 0.075 and abs(nx) > 0.55:
            continue
        t_fade = min(1.0, max(0.0, (0.45 - y) / 0.06))
        expand = 0.0022 * t_fade
        if y < 0.12:
            expand = 0.0032
        pos[i] += norm[i] * expand
        if 0.012 < y < 0.115 and z > -0.025 and nz > 0.10:
            wy = math.sin(max(0.0, min(1.0, (y - 0.012) / (0.115 - 0.012))) * math.pi)
            pos[i, 2] += 0.0040 * wy * max(0.2, nz)
            if ny > 0.1:
                pos[i, 1] += 0.0020 * wy * ny
        if y < 0.025 and z > -0.045 and ny < -0.35:
            pos[i, 1] -= 0.0025 * abs(ny)

    # Gently plump elbow & wrist creases (+1.2mm along smooth outward normal)
    for i in active_joints:
        if not is_finger_v[i] and 0.81 < pos[i, 1] < 1.21:
            pos[i] += norm[i] * (0.0012 * joint_weights[i])

    # Final pass of vertex normal recomputation
    compute_vertex_normals(recalc_mask)

    # Smooth normals across 1-ring neighborhood for all smoothed joints, heels, and neck
    smooth_norm_idx = np.unique(np.concatenate([active_armpit, active_joints, foot_candidates, neck_hl_idx]))
    for _nit in range(2):
        new_norm = norm.copy()
        for u in smooth_norm_idx:
            nbs = adj[u]
            if len(nbs) >= 3:
                # Only average neighbors with compatible orientation (dot > 0.3) so fingers stay crisp
                nb_n = norm[nbs]
                dots = np.dot(nb_n, norm[u])
                good = nb_n[dots > 0.30]
                if len(good) > 0:
                    mn = norm[u] * 0.45 + np.mean(good, axis=0) * 0.55
                    nl = np.linalg.norm(mn)
                    if nl > 1e-8:
                        new_norm[u] = mn / nl
        norm = new_norm

    # Blend normals across the ZA-to-HL neck seam (1.488 < Y < 1.522) using 3D proximity
    seam_idx = np.where((pos[:, 1] > 1.488) & (pos[:, 1] < 1.522) & (np.abs(pos[:, 0]) < 0.088))[0]
    if len(seam_idx) > 0:
        seam_tree = cKDTree(pos[seam_idx])
        seam_norms = norm[seam_idx].copy()
        for k_i, idx in enumerate(seam_idx):
            near = seam_tree.query_ball_point(pos[idx], r=0.0075)
            if len(near) > 1:
                avg_n = np.mean(seam_norms[near], axis=0)
                nl = np.linalg.norm(avg_n)
                if nl > 1e-8:
                    w_n = min(1.0, (1.522 - pos[idx, 1]) / 0.012, (pos[idx, 1] - 1.488) / 0.012)
                    w_n = max(0.0, min(1.0, w_n)) * 0.75
                    blended = norm[idx] * (1.0 - w_n) + (avg_n / nl) * w_n
                    bl_len = np.linalg.norm(blended)
                    if bl_len > 1e-8:
                        norm[idx] = blended / bl_len

    # Write updated pos and norm back into human-learning.glb
    for i in range(vcnt):
        struct.pack_into("<fff", hb, boff + i * 12, float(pos[i, 0]), float(pos[i, 1]), float(pos[i, 2]))
        struct.pack_into(
            "<fff", hb, boff + n_off + i * 12, float(norm[i, 0]), float(norm[i, 1]), float(norm[i, 2])
        )

    with open(HL_PATH, "wb") as f:
        f.write(hb)
    print(
        f"✓ Đã làm mịn & liền lạc cổ gáy ({len(seam_idx)}), hõm nách ({len(active_armpit)}), "
        f"khuỷu tay/cổ tay/ngón tay ({len(active_joints)}) và gót chân ({len(foot_candidates)})!"
    )

    # Render 4-panel verification montage matching the user's 4 screenshots:
    # Panel 1: Back of Neck & Right Posterior Armpit (angle = 165 deg, y = 1.18..1.66)
    # Panel 2: Front-Oblique Neck & Shoulders (angle = -12 deg, y = 1.25..1.65)
    # Panel 3: Front Elbows, Wrists & Hands/Fingers (angle = 0 deg, y = 0.65..1.25)
    # Panel 4: Back-Oblique Calves, Ankles & Heels (angle = 125 deg, y = -0.02..0.48)
    W, H = 1280, 440
    img = np.full((H, W, 3), [15, 23, 42], dtype=np.uint8)
    zbuf = np.full((H, W), -999.0, dtype=np.float32)

    panels = [
        (math.radians(165.0), 160, 1.18, 1.66, 0.25),   # Panel 1: Back neck & posterior armpit
        (math.radians(-12.0), 480, 1.24, 1.66, 0.24),   # Panel 2: Front-side neck & collar
        (math.radians(0.0),   800, 0.66, 1.24, 0.34),   # Panel 3: Elbows, wrists, hands/fingers
        (math.radians(125.0), 1120, -0.02, 0.44, 0.22), # Panel 4: Calves, ankles & heels
    ]

    for angle, cx_off, y_min, y_max, x_span in panels:
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        y_span = y_max - y_min
        for a, b, c in tris:
            p0, p1, p2 = pos[a], pos[b], pos[c]
            if max(p0[1], p1[1], p2[1]) < y_min or min(p0[1], p1[1], p2[1]) > y_max:
                continue
            n0, n1, n2 = norm[a], norm[b], norm[c]
            ra = (p0[0] * cos_a + p0[2] * sin_a, p0[1], -p0[0] * sin_a + p0[2] * cos_a)
            rb = (p1[0] * cos_a + p1[2] * sin_a, p1[1], -p1[0] * sin_a + p1[2] * cos_a)
            rc = (p2[0] * cos_a + p2[2] * sin_a, p2[1], -p2[0] * sin_a + p2[2] * cos_a)
            if (rb[0] - ra[0]) * (rc[1] - ra[1]) - (rb[1] - ra[1]) * (rc[0] - ra[0]) <= 0:
                continue
            rna = (n0[0] * cos_a + n0[2] * sin_a, n0[1], -n0[0] * sin_a + n0[2] * cos_a)
            rnb = (n1[0] * cos_a + n1[2] * sin_a, n1[1], -n1[0] * sin_a + n1[2] * cos_a)
            rnc = (n2[0] * cos_a + n2[2] * sin_a, n2[1], -n2[0] * sin_a + n2[2] * cos_a)

            x0 = int((ra[0] / x_span) * 145 + cx_off)
            y0 = int(((y_max - ra[1]) / y_span) * (H * 0.90) + H * 0.05)
            x1 = int((rb[0] / x_span) * 145 + cx_off)
            y1 = int(((y_max - rb[1]) / y_span) * (H * 0.90) + H * 0.05)
            x2 = int((rc[0] / x_span) * 145 + cx_off)
            y2 = int(((y_max - rc[1]) / y_span) * (H * 0.90) + H * 0.05)

            min_x, max_x = max(cx_off - 155, min(x0, x1, x2)), min(cx_off + 155, max(x0, x1, x2))
            min_y, max_y = max(0, min(y0, y1, y2)), min(H - 1, max(y0, y1, y2))
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
                        if zz > zbuf[py, px]:
                            zbuf[py, px] = zz
                            nx = w0 * rna[0] + w1 * rnb[0] + w2 * rnc[0]
                            ny = w0 * rna[1] + w1 * rnb[1] + w2 * rnc[1]
                            nz = w0 * rna[2] + w1 * rnb[2] + w2 * rnc[2]
                            nl = math.hypot(nx, ny, nz) or 1.0
                            nx, ny, nz = nx / nl, ny / nl, nz / nl
                            diff = max(0.0, nx * 0.22 + ny * 0.30 + nz * 0.92)
                            fill = max(0.0, -nx * 0.25 + ny * 0.1 + nz * 0.5) * 0.25
                            spec = pow(max(0.0, nz), 18.0) * 0.12
                            val = min(1.0, 0.22 + 0.68 * diff + fill + spec)
                            img[py, px, 0] = min(255, int(238 * val))
                            img[py, px, 1] = min(255, int(184 * val))
                            img[py, px, 2] = min(255, int(152 * val))

    out_img = os.path.join(ARTIFACT_DIR, "scratch_joints_verified.png")
    Image.fromarray(img).save(out_img)
    print(f"✓ Đã lưu ảnh kiểm chứng 4 vùng: {out_img}")


if __name__ == "__main__":
    fix_armpit_mesh()
