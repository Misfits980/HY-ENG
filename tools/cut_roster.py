"""몬스터 시트 자르기 (위 줄 = 전신, 아래 줄 = 동그란 얼굴)
python3 cut_roster.py 시트.png 이름1,이름2,... 몸저장폴더 얼굴저장폴더
- 얼굴: 아래쪽 큰 원을 찾아 깨끗한 원으로 다시 자름 (원 밖 번개·부스러기 제거)
- 몸: 얼굴 원과 그 둘레를 지운 뒤, 열마다 가장 큰 덩어리 + 가까운 조각만 (떨어진 점·티끌 제거), 옅은 무지개 테두리 제거"""
import sys, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
def main(path, names, bodydir, ptdir):
    im = Image.open(path).convert('RGBA'); a = np.array(im).astype(np.int32); H, W = a.shape[:2]; n = len(names)
    al = a[:, :, 3]; solid = al > 200
    # 1) 얼굴 원: 아래 절반에서 크게 깎아도 남는 덩어리 = 원
    er = ndimage.binary_erosion(solid, iterations=18); lab, k = ndimage.label(er)
    circles = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        ys, xs = sl; cy = (ys.start + ys.stop) / 2; cx = (xs.start + xs.stop) / 2
        w = xs.stop - xs.start + 36; h = ys.stop - ys.start + 36
        if cy > H * 0.5 and min(w, h) > W / n * 0.55 and abs(w - h) < 0.12 * max(w, h): circles.append((cx, cy, min(w, h) / 2))
    circles.sort(); assert len(circles) == n, ('원 개수', len(circles), circles)
    out = []
    for (cx, cy, r), nm in zip(circles, names):
        r2 = r * 0.975; S = 4; D = int(2 * r2)
        x0, y0 = int(round(cx - r2)), int(round(cy - r2))
        sub = Image.fromarray(a.astype(np.uint8)).crop((x0, y0, x0 + D, y0 + D))
        mk = Image.new('L', (D * S, D * S), 0); ImageDraw.Draw(mk).ellipse((0, 0, D * S - 1, D * S - 1), fill=255); mk = mk.resize((D, D), Image.LANCZOS)
        sub.putalpha(Image.fromarray(np.minimum(np.array(sub.getchannel('A')), np.array(mk))))
        sub.resize((220, 220), Image.LANCZOS).save(f'{ptdir}/pt_{nm}.webp', 'WEBP', quality=86, method=6)
    # 2) 몸: 원(+여유) 지우기
    yy, xx = np.mgrid[0:H, 0:W]; b = a.copy()
    for (cx, cy, r) in circles: b[((yy - cy) ** 2 + (xx - cx) ** 2) < (r + 10) ** 2, 3] = 0
    ytop = min(cy - r for cx, cy, r in circles)
    m = b[:, :, 3] > 40; lab, k = ndimage.label(ndimage.binary_dilation(m, iterations=3))
    sz = ndimage.sum(m, lab, range(1, k + 1)); cm = ndimage.center_of_mass(m, lab, range(1, k + 1))
    for j, ((cx, cy, r), nm) in enumerate(zip(circles, names)):
        cand = [(s, i + 1) for i, (s, (yc, xc)) in enumerate(zip(sz, cm)) if yc < ytop + 20 and abs(xc - cx) < W / n * 0.6]
        if not cand: print('몸 없음', nm); continue
        big = max(cand)[0]; keep = [i for s, i in cand if s > big * 0.01]
        mk = np.isin(lab, keep) & m; c = b.copy(); c[~mk, 3] = 0
        # 옅은 테두리: 반투명 + 채도 높은 무지개 띠 줄이기
        A = c[:, :, 3]; rgb = c[:, :, :3]; mx = rgb.max(2); mn = rgb.min(2)
        fr = (A < 140) & (A > 0) & ((mx - mn) > 120); c[fr, 3] = (A[fr] * 0.35).astype(np.int32)
        ys, xs = np.where(c[:, :, 3] > 24); pad = 4
        crop = Image.fromarray(c.astype(np.uint8)).crop((max(0, xs.min() - pad), max(0, ys.min() - pad), min(W, xs.max() + pad + 1), min(H, ys.max() + pad + 1)))
        crop.thumbnail((300, 300), Image.LANCZOS); crop.save(f'{bodydir}/m_{nm}.webp', 'WEBP', quality=86, method=6)
        out.append((nm, crop.size, len(keep)))
    print(out)
if __name__ == '__main__': main(sys.argv[1], sys.argv[2].split(','), sys.argv[3], sys.argv[4])
