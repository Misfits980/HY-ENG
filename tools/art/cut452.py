"""v452 보드게임 새 그림 자르기 — 시트 7장 × (k,e)"""
import numpy as np, os, sys
from PIL import Image
from scipy import ndimage
SRC = "/home/claude/art452/src/"
OUT = "/home/claude/hy-eng/assets/mg/"
SHEETS = [  # (번호k, 번호e, 열, 행, 이름들, 크기, 같은 상자 묶음)
    (1, 8, 3, 3, ["em_tug","em_light","em_paint","em_fish","em_stop","em_num","em_fruit","em_stack","em_jump"], 256, [list(range(9))]),
    (2, 9, 4, 3, ["fr_basket","fr_apple","fr_banana","fr_grape","fr_berry","fr_orange","fr_melon","fr_peach","fr_gold","fr_bomb","fr_splat","fr_spark"], 256, []),
    (3, 10, 4, 3, ["jp_run","jp_jump","jp_cactus","jp_rock","jp_box","jp_ground","st_base","st_block","st_gold","st_chip","fx_dust","fx_spark"], 256, [[0,1]]),
    (4, 11, 4, 3, ["lt_off","lt_r","lt_y","lt_g","tg_rocket","tg_rope","tg_flagr","tg_flagb","sp_watch","nu_tile","nu_ok","nu_no"], 256, [[0,1,2,3],[9,10,11],[6,7]]),
    (5, 12, 4, 2, ["fi_o","fi_b","fi_g","fi_hook","pt_roller","pt_bucket","pt_splat","pt_brush"], 256, [[0,1,2]]),
    (7, 14, 4, 2, ["pod","md_1","md_2","md_3","dice_gold","rb_red","rb_gold","confetti"], 256, [[1,2,3],[5,6]]),
]
BG = (6, 13, 3, 2, ["bg_tug","bg_light","bg_paint","bg_fish","bg_fruit","bg_jump"], 506)

def cut_sheet(path, cols, rows, names, size, groups, outdir):
    im = Image.open(path).convert("RGBA"); A = np.array(im); a = A[:, :, 3].astype(int)
    H, W = a.shape; cw, ch = W / cols, H / rows
    m = a > 70
    lab, n = ndimage.label(m, structure=np.ones((3, 3)))
    objs = ndimage.find_objects(lab); areas = ndimage.sum(m, lab, range(1, n + 1)); cms = ndimage.center_of_mass(m, lab, range(1, n + 1))
    cell = {}
    for k in range(n):
        if areas[k] < 30: continue
        cy, cx = cms[k]; c = min(cols - 1, int(cx // cw)) + cols * min(rows - 1, int(cy // ch))
        cell.setdefault(c, []).append(k)
    boxes = {}; keep = {}
    for c, ks in cell.items():
        big = max(areas[k] for k in ks)
        ks2 = [k for k in ks if areas[k] >= big * 0.012]
        keep[c] = ks2
        ys = [objs[k][0] for k in ks2]; xs = [objs[k][1] for k in ks2]
        boxes[c] = [min(s.start for s in xs), min(s.start for s in ys), max(s.stop for s in xs), max(s.stop for s in ys)]
    # 같은 상자 묶음 — 칸 안 상대 위치로 합침
    for g in groups:
        rel = []
        for c in g:
            ox, oy = (c % cols) * cw, (c // cols) * ch; b = boxes[c]
            rel.append([b[0] - ox, b[1] - oy, b[2] - ox, b[3] - oy])
        u = [min(r[0] for r in rel), min(r[1] for r in rel), max(r[2] for r in rel), max(r[3] for r in rel)]
        for c in g:
            ox, oy = (c % cols) * cw, (c // cols) * ch
            boxes[c] = [int(u[0] + ox), int(u[1] + oy), int(u[2] + ox), int(u[3] + oy)]
    os.makedirs(outdir, exist_ok=True); info = {}
    for c, nm in enumerate(names):
        if c not in boxes: print("  !! 빈 칸", nm); continue
        keepm = np.isin(lab, [k + 1 for k in keep[c]])
        # 남길 덩어리 주변(반투명 빛)만 살림: 덩어리를 12px 넓힌 영역 밖 알파 = 0
        grow = ndimage.binary_dilation(keepm, iterations=12)
        x0, y0, x1, y1 = boxes[c]; pad = 10
        x0 = max(0, x0 - pad); y0 = max(0, y0 - pad); x1 = min(W, x1 + pad); y1 = min(H, y1 + pad)
        B = A[y0:y1, x0:x1].copy(); g = grow[y0:y1, x0:x1]
        B[:, :, 3] = np.where(g, B[:, :, 3], 0)
        # 같은 칸 밖의 다른 칸 덩어리 지우기
        other = (lab[y0:y1, x0:x1] > 0) & ~np.isin(lab[y0:y1, x0:x1], [k + 1 for k in keep[c]])
        other = ndimage.binary_dilation(other, iterations=6) & ~ndimage.binary_dilation(keepm[y0:y1, x0:x1], iterations=3)
        B[:, :, 3] = np.where(other, 0, B[:, :, 3])
        B[:, :, 3] = np.where(B[:, :, 3] < 24, 0, B[:, :, 3])   # 거의 투명한 안개 = 0 (빛 번짐 필터가 네모로 보이는 것 막기)
        t = Image.fromarray(B)
        w, h = t.size; s = size / max(w, h)
        t = t.resize((max(1, round(w * s)), max(1, round(h * s))), Image.LANCZOS)
        t.save(outdir + nm + ".webp", "WEBP", quality=88, method=6)
        info[nm] = t.size
    return info

def cut_bg(path, cols, rows, names, size, outdir):
    im = Image.open(path).convert("RGB"); W, H = im.size; cw, ch = W // cols, H // rows
    for c, nm in enumerate(names):
        x, y = (c % cols) * cw, (c // cols) * ch; i = 3
        t = im.crop((x + i, y + i, x + cw - i, y + ch - i)).resize((size, size), Image.LANCZOS)
        t.save(outdir + nm + ".webp", "WEBP", quality=84, method=6)

if __name__ == "__main__":
    for nk, ne, cols, rows, names, size, groups in SHEETS:
        for sk, nn in (("k", nk), ("e", ne)):
            info = cut_sheet(SRC + f"{nn}.png", cols, rows, names, size, groups, OUT + sk + "/")
            print(sk, nn, info)
    nk, ne, cols, rows, names, size = BG
    for sk, nn in (("k", nk), ("e", ne)):
        cut_bg(SRC + f"{nn}.png", cols, rows, names, size, OUT + sk + "/")
    print("done")
