"""그림 조각 검사 — 잘림(가장자리 직선) · 떨어진 부스러기 · 반투명 색 번짐 · 너무 작음
사용: python3 tools/art_check.py assets/d30 assets/words  → 문제 목록 + /tmp/art_check_*.png (밝은·어두운 배경 모음)"""
import sys, os, glob
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
FLAT = ('btn_', 'track', 'fill', 'vine', 'panel', 'ribbon', 'zone_', 'bridge', 'rectangle', 'bg', 'map', 'cutin')
def check(f):
    n = os.path.basename(f)[:-5]; im = Image.open(f).convert('RGBA'); a = np.array(im); A = a[:, :, 3]; H, W = A.shape; out = []
    if A.min() > 200: return n, im, out            # 배경(불투명) 그림
    op = A > 160
    for side, line, L in (('위', op[0], W), ('아래', op[-1], W), ('왼쪽', op[:, 0], H), ('오른쪽', op[:, -1], H)):
        run = best = 0
        for v in line: run = run + 1 if v else 0; best = max(best, run)
        if best > 0.30 * L and not n.startswith(FLAT): out.append(f'{side} 직선 잘림 의심({best}/{L}px)')
    m = A > 40; lab, k = ndimage.label(ndimage.binary_dilation(m, iterations=2))
    if k > 1:
        sz = ndimage.sum(m, lab, range(1, k + 1)); big = sz.max()
        bits = [s for s in sz if s < 0.02 * big and s > 6]
        if len(bits) >= 3: out.append(f'떨어진 부스러기 {len(bits)}개')
    main = ndimage.binary_dilation(A > 140, iterations=4)
    rgb = a[:, :, :3].astype(int); sat = rgb.max(2) - rgb.min(2)
    halo = ((A > 15) & (A < 140) & ~main & (sat > 90)).sum()
    if halo > 0.01 * (A > 40).sum() and halo > 80: out.append(f'색 번짐 {halo}px')
    if max(W, H) < 60: out.append(f'너무 작음 {W}x{H}')
    return n, im, out
def sheet(items, bg, path):
    cols = 10; c = Image.new('RGBA', (cols * 130, ((len(items) + cols - 1) // cols) * 150), bg); d = ImageDraw.Draw(c)
    for i, (n, im, bad) in enumerate(items):
        t = im.copy(); t.thumbnail((120, 120)); x, y = (i % cols) * 130, (i // cols) * 150
        c.alpha_composite(t, (x + (125 - t.width) // 2, y + 2)); d.text((x + 3, y + 128), n[:18], fill=(255, 60, 60) if bad else (90, 90, 90) if bg[0] > 128 else (220, 220, 220))
    c.save(path)
if __name__ == '__main__':
    fs = [f for d in sys.argv[1:] for f in sorted(glob.glob(os.path.join(d, '**', '*.webp'), recursive=True))]
    items = [check(f) for f in fs]; bad = [(n, b) for n, _, b in items if b]
    for n, b in bad: print('⚠️', n, '·', ' / '.join(b))
    print(f'검사 {len(items)}개 · 문제 {len(bad)}개')
    sheet(items, (245, 240, 230, 255), '/tmp/art_check_light.png'); sheet(items, (30, 34, 50, 255), '/tmp/art_check_dark.png')
