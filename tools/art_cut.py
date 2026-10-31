"""시트 자르기 — 칸 경계로 자르지 않고, 덩어리(연결된 그림)의 '중심'이 어느 칸에 있는지로 나눔 → 칸을 넘어간 칼빛·발판 끝이 잘리지 않음
cut(시트, 이름들, 열, 행, 저장폴더, 최대크기)"""
import numpy as np
from PIL import Image
from scipy import ndimage
def cut(path, names, cols, rows, outdir, maxw=300, thr=60, dil=6, minfrac=0.004):
    im = Image.open(path).convert('RGBA'); a = np.array(im); a[a[:, :, 3] < thr, 3] = 0; im = Image.fromarray(a)
    H, W = a.shape[:2]; m = a[:, :, 3] > 0; lab, n = ndimage.label(ndimage.binary_dilation(m, iterations=dil))
    sz = ndimage.sum(m, lab, range(1, n + 1)); cm = ndimage.center_of_mass(m, lab, range(1, n + 1))
    cells = {}
    for i, (s, (cy, cx)) in enumerate(zip(sz, cm), 1):
        if s < minfrac * W * H / (cols * rows): continue
        k = min(rows - 1, int(cy / (H / rows))) * cols + min(cols - 1, int(cx / (W / cols)))
        cells.setdefault(k, []).append(i)
    res = []
    for k, nm in enumerate(names):
        if not nm or k not in cells: continue
        mk = np.isin(lab, cells[k]) & m; ys, xs = np.where(mk)
        b = a.copy(); b[~mk, 3] = 0; sub = Image.fromarray(b).crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
        if max(sub.size) > maxw: sub.thumbnail((maxw, maxw), Image.LANCZOS)
        sub.save(f'{outdir}/{nm}.webp', 'WEBP', quality=86, method=6); res.append((nm, sub.size))
    return res
