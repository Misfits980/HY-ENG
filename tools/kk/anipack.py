#!/usr/bin/env python3
"""(v694) 🐾 단어 손님 — Quaternius 움직이는 동물(.glb, CC0)을 마을용 작은 묶음으로.
   python3 tools/kk/anipack.py            → assets/town/ani/<key>.json · <key>.bin  (전부)
   python3 tools/kk/anipack.py Fox Cow    → 고른 것만

   - 뼈: 장면의 모든 마디(메시 마디 빼고)를 그대로 — 이름 대신 번호(b<i>) (three 의 PropertyBinding 은 「Ear3.L」 같은 점 이름을 못 읽음)
   - 메시: 재료 5개를 한 덩어리로 (꼭짓점마다 재료 번호 1바이트 → 게임에서 색) · 위치 int16 · 법선 int8 · 뼈 uint8×4 · 무게 uint8×4(합 255)
   - 애니: Idle · Walk · Eating · Gallop · Jump_ToIdle 만 · 30fps 원본을 몇 장 건너 · 안 바뀌는 줄은 뺌(쉬는 자세 그대로) · 회전 int16
   - 읽는 곳: proto/isle-ani.js (ANI.load / ANI.make)
"""
import json, struct, sys, os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "tools/kk/src/animals")
OUT = os.path.join(ROOT, "assets/town/ani")
CLIPS = [("Idle", 3), ("Walk", 2), ("Eating", 3), ("Gallop", 2), ("Jump_ToIdle", 2)]
NAMES = {"Cow": "cow", "Horse": "horse", "Horse_White": "pony", "Deer": "deer", "Donkey": "donkey", "Fox": "fox", "Wolf": "wolf",
         "ShibaInu": "shiba", "Husky": "husky", "Bull": "bull", "Alpaca": "alpaca", "Stag": "stag"}
CT = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
NC = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}


def glb(fn):
    f = open(fn, "rb").read()
    L = struct.unpack("<I", f[12:16])[0]
    j = json.loads(f[20:20 + L])
    o = 20 + L
    bl = struct.unpack("<I", f[o:o + 4])[0]
    return j, f[o + 8:o + 8 + bl]


def read(j, B, i):
    a = j["accessors"][i]
    v = j["bufferViews"][a["bufferView"]]
    dt = CT[a["componentType"]]
    n = NC[a["type"]]
    off = v.get("byteOffset", 0) + a.get("byteOffset", 0)
    st = v.get("byteStride", 0)
    isz = np.dtype(dt).itemsize * n
    if st and st != isz:
        rows = [np.frombuffer(B, dt, n, off + k * st) for k in range(a["count"])]
        x = np.array(rows)
    else:
        x = np.frombuffer(B, dt, a["count"] * n, off).reshape(a["count"], n)
    if a.get("normalized") and dt != np.float32:
        x = x.astype(np.float32) / np.iinfo(dt).max
    return x


def pack(src):
    j, B = glb(os.path.join(SRC, src + ".glb"))
    N = j["nodes"]
    scene = j["scenes"][j.get("scene", 0)]["nodes"]
    mesh_nodes = [i for i, n in enumerate(N) if "mesh" in n]
    assert len(mesh_nodes) == 1, src
    mn = mesh_nodes[0]
    par = {}
    for i, n in enumerate(N):
        for c in n.get("children", []):
            par[c] = i
    order = []  # 부모 먼저
    def walk(i):
        if i != mn:
            order.append(i)
        for c in N[i].get("children", []):
            walk(c)
    for r in scene:
        walk(r)
    idx = {n: k for k, n in enumerate(order)}
    bones = []
    for n in order:
        d = N[n]
        bones.append([idx.get(par.get(n), -1), [round(x, 6) for x in d.get("translation", [0, 0, 0])],
                      [round(x, 7) for x in d.get("rotation", [0, 0, 0, 1])], [round(x, 6) for x in d.get("scale", [1, 1, 1])]])
    mpar = idx.get(par.get(mn), -1)
    skin = j["skins"][N[mn]["skin"]]
    joints = [idx[n] for n in skin["joints"]]
    ibm = read(j, B, skin["inverseBindMatrices"]).astype(np.float32).reshape(-1)

    P, Nn, J, W, Mi, X = [], [], [], [], [], []
    base = 0
    for p in j["meshes"][N[mn]["mesh"]]["primitives"]:
        A = p["attributes"]
        pos = read(j, B, A["POSITION"]).astype(np.float32)
        P.append(pos)
        Nn.append(read(j, B, A["NORMAL"]).astype(np.float32))
        J.append(read(j, B, A["JOINTS_0"]).astype(np.int32))
        W.append(read(j, B, A["WEIGHTS_0"]).astype(np.float32))
        Mi.append(np.full(len(pos), p.get("material", 0), np.uint8))
        X.append(read(j, B, p["indices"]).reshape(-1).astype(np.int64) + base)
        base += len(pos)
    P = np.concatenate(P); Nn = np.concatenate(Nn); J = np.concatenate(J); W = np.concatenate(W); Mi = np.concatenate(Mi); X = np.concatenate(X)
    assert J.max() < 256 and base < 65536
    mnv, mxv = P.min(0), P.max(0)
    q = np.round((P - mnv) / np.maximum(mxv - mnv, 1e-6) * 65535 - 32768).astype(np.int16)
    nq = np.round(Nn / np.maximum(np.linalg.norm(Nn, axis=1, keepdims=True), 1e-6) * 127).astype(np.int8)
    W = W / np.maximum(W.sum(1, keepdims=True), 1e-6)
    wq = np.floor(W * 255 + .5).astype(np.int32)
    for r in range(len(wq)):  # 합 255 로 맞춤
        dlt = 255 - wq[r].sum()
        wq[r][int(np.argmax(wq[r]))] += dlt
    wq = wq.astype(np.uint8)
    pal = [[round(c, 4) for c in m.get("pbrMetallicRoughness", {}).get("baseColorFactor", [1, 1, 1, 1])[:3]] for m in j["materials"]]
    mats = [m.get("name", "") for m in j["materials"]]

    blob = bytearray()
    def put(arr):
        nonlocal blob
        while len(blob) % 4:
            blob += b"\0"
        o = len(blob)
        blob += arr.tobytes()
        return o
    off = {"p": put(q.reshape(-1)), "n": put(nq.reshape(-1)), "m": put(Mi), "j": put(J.astype(np.uint8).reshape(-1)),
           "w": put(wq.reshape(-1)), "x": put(X.astype(np.uint16)), "ib": put(ibm)}

    anims = {}
    byname = {a["name"]: a for a in j["animations"]}
    for cname, step in CLIPS:
        a = byname.get(cname)
        if not a:
            continue
        tr = []
        dur = 0
        nf = None
        for ch in a["channels"]:
            s = a["samplers"][ch["sampler"]]
            nd = ch["target"]["node"]
            path = ch["target"]["path"]
            if nd == mn or nd not in idx or path not in ("translation", "rotation", "scale"):
                continue
            t = read(j, B, s["input"]).reshape(-1)
            v = read(j, B, s["output"]).astype(np.float32)
            dur = max(dur, float(t[-1]))
            rest = {"translation": bones[idx[nd]][1], "rotation": bones[idx[nd]][2], "scale": bones[idx[nd]][3]}[path]
            if len(t) <= 1 or np.abs(v - v[0]).max() < 1e-4:
                if np.abs(v[0] - np.array(rest)).max() < 1e-4:
                    continue  # 쉬는 자세 그대로
                tr.append([idx[nd], path[0], -1, [round(float(x), 6) for x in v[0]]])
                continue
            # 고르게 다시 뽑기 (원본 30fps, 끝 장 꼭 넣음)
            n0 = len(t)
            ks = list(range(0, n0, step))
            if ks[-1] != n0 - 1:
                ks.append(n0 - 1)
            if nf is None:
                nf = [float(t[k]) for k in ks]
            elif len(nf) != len(ks):
                raise SystemExit("frames differ " + src + cname)
            vv = v[ks]
            if path == "rotation":
                for k in range(1, len(vv)):  # 사원수 부호 이어지게
                    if np.dot(vv[k], vv[k - 1]) < 0:
                        vv[k] = -vv[k]
                o = put(np.round(np.clip(vv, -1, 1) * 32767).astype(np.int16).reshape(-1))
            else:
                o = put(vv.astype(np.float32).reshape(-1))
            tr.append([idx[nd], path[0], o, None])
        if nf is None:
            nf = [0.0, dur]
        anims[cname] = {"d": round(dur, 4), "t": [round(x, 4) for x in nf], "tr": tr}
    hdr = {"v": 1, "src": src, "nv": int(base), "ni": int(len(X)), "mn": [float(x) for x in mnv], "mx": [float(x) for x in mxv],
           "pal": pal, "mats": mats, "bones": bones, "mesh": mpar, "joints": joints, "off": off, "anims": anims, "size": len(blob)}
    key = NAMES.get(src, src.lower())
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, key + ".bin"), "wb").write(bytes(blob))
    json.dump(hdr, open(os.path.join(OUT, key + ".json"), "w"), separators=(",", ":"))
    print(key, "verts", base, "bin KB", len(blob) // 1024, "json KB", os.path.getsize(os.path.join(OUT, key + ".json")) // 1024,
          {k: (len(v["t"]), len([t for t in v["tr"] if t[2] >= 0])) for k, v in anims.items()})


if __name__ == "__main__":
    L = sys.argv[1:] or ["Cow", "Horse", "Horse_White", "Deer", "Donkey", "Fox", "Wolf", "ShibaInu", "Bull"]
    for s in L:
        pack(s)
