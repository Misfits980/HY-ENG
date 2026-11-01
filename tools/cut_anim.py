"""공격 그림(12칸) 자르기 — 칸 사이로 번지는 빛·불꽃을 '가장 가까운 몸'에 붙여서 나눔
python3 cut_anim.py 그림.png 열 행 저장.webp [미리보기.png]
- 몸 찾기: 불투명(알파>200)을 깎아 큰 덩어리 = 몸 (열×행 개만큼)
- 모든 칠한 점을 가장 가까운 몸 상자에 붙임 (옆 칸으로 번진 효과는 그 칸 몸 것으로)
- 칸 자리(왼쪽 위)를 기준으로 옮겨 놓아 돌진 움직임은 그대로, 12칸 모두 같은 자르기 · 바닥 맞춤 → 3072×256 한 줄"""
import sys, numpy as np
from PIL import Image
from scipy import ndimage
def main(path, cols, rows, out, prev=None, N=12):
    a = np.array(Image.open(path).convert('RGBA')).astype(np.int32); H, W = a.shape[:2]
    al = a[:, :, 3]; solid = ndimage.binary_erosion(al > 200, iterations=4)
    lab, n = ndimage.label(solid); sz = ndimage.sum(solid, lab, range(1, n + 1)); objs = ndimage.find_objects(lab)
    big = sorted(range(n), key=lambda i: -sz[i])
    cw, ch = W / cols, H / rows
    bodies = {}
    for i in big:
        ys, xs = objs[i]; cy = (ys.start + ys.stop) / 2; cx = (xs.start + xs.stop) / 2
        k = min(rows - 1, int(cy // ch)) * cols + min(cols - 1, int(cx // cw))
        if k in bodies:
            b = bodies[k]; bodies[k] = (min(b[0], ys.start), min(b[1], xs.start), max(b[2], ys.stop), max(b[3], xs.stop)); continue
        if sz[i] < 0.08 * sz[big[0]]: continue
        bodies[k] = (ys.start, xs.start, ys.stop, xs.stop)
    assert len(bodies) == N, ('몸 개수', len(bodies))
    ks = sorted(bodies)
    yy, xx = np.mgrid[0:H, 0:W]
    D = []
    for k in ks:
        y0, x0, y1, x1 = bodies[k]
        dx = np.maximum(0, np.maximum((x0 - xx) * 0.45, (xx - x1) * 1.6)); dy = np.maximum(0, np.maximum(y0 - yy, yy - y1)); D.append(dx * dx + dy * dy)
    own = np.argmin(np.stack(D), 0)   # 공격은 왼쪽으로 → 몸 왼쪽의 빛은 그 몸 것으로 (왼쪽 거리 ×0.45)
    ML = int(cw * 0.45); CWo = int(cw) + ML * 2; CHo = int(ch)
    frames = []
    for j, k in enumerate(ks):
        r, c = divmod(k, cols); ox, oy = int(c * cw), int(r * ch)
        m = (own == j) & (al > 0)
        f = np.zeros((CHo, CWo, 4), np.uint8)
        ys, xs = np.where(m); ty = ys - oy; tx = xs - ox + ML
        ok = (ty >= 0) & (ty < CHo) & (tx >= 0) & (tx < CWo)
        f[ty[ok], tx[ok]] = a[ys[ok], xs[ok]]
        frames.append(f)
    allm = np.any(np.stack([f[:, :, 3] > 24 for f in frames]), 0); ys, xs = np.where(allm)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    S = 256; strip = Image.new('RGBA', (S * N, S), (0, 0, 0, 0))
    bw, bh = x1 - x0, y1 - y0; sc = min(S / bw, S / bh) * 0.96
    for j, f in enumerate(frames):
        im = Image.fromarray(f).crop((x0, y0, x1, y1)).resize((max(1, round(bw * sc)), max(1, round(bh * sc))), Image.LANCZOS)
        strip.alpha_composite(im, (j * S + (S - im.width) // 2, S - im.height - 2))
    strip.save(out, 'WEBP', quality=86, method=6)
    if prev:
        bg = Image.new('RGBA', strip.size, (40, 34, 70, 255)); bg.alpha_composite(strip)
        from PIL import ImageDraw
        d = ImageDraw.Draw(bg)
        for j in range(1, N): d.line([(j * S, 0), (j * S, S)], fill=(255, 255, 255, 90))
        bg.convert('RGB').save(prev)
    print(out, strip.size, 'scale', round(sc, 3))
if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5] if len(sys.argv) > 5 else None)
