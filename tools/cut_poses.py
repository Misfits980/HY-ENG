"""포즈 시트(열×행) 자르기 — 효과(빛·바람)는 '가장 가까운 몸'에 붙임 (공격은 오른쪽으로 → 몸 오른쪽 거리 ×0.45)
python3 cut_poses.py 시트.png 열 행 저장폴더 이름 [이름들(쉼표)]
→ 저장폴더/<이름>_<포즈>.png  (몸 가운데·발을 기준으로 같은 캔버스에 놓아 포즈를 바꿔도 안 흔들림) + 정보 출력"""
import sys, os, json, numpy as np
from PIL import Image
from scipy import ndimage
def bodies_of(al, cols, rows, H, W, er=6):
    solid = ndimage.binary_erosion(al > 200, iterations=er); lab, n = ndimage.label(solid)
    sz = ndimage.sum(solid, lab, range(1, n+1)); objs = ndimage.find_objects(lab); big = sorted(range(n), key=lambda i: -sz[i])
    cw, ch = W/cols, H/rows; B = {}
    for i in big:
        ys, xs = objs[i]; cy=(ys.start+ys.stop)/2; cx=(xs.start+xs.stop)/2; k=min(rows-1,int(cy//ch))*cols+min(cols-1,int(cx//cw))
        if sz[i] < 0.06*sz[big[0]]: continue
        if k in B: continue   # 칸마다 가장 큰 덩어리 = 몸 (효과 덩어리를 몸에 합치면 칸 경계가 틀어짐)
        B[k]=(ys.start, xs.start, ys.stop, xs.stop)
    return B
def main(path, cols, rows, out, name, poses):
    a = np.array(Image.open(path).convert('RGBA')); H, W = a.shape[:2]; al = a[:,:,3].astype(int)
    B = bodies_of(al, cols, rows, H, W); N = cols*rows; assert len(B)==N, ('몸 개수', len(B), sorted(B))
    ks = sorted(B); yy, xx = np.mgrid[0:H, 0:W]
    # 줄 경계 = 위 줄 몸 아래 ~ 아래 줄 몸 위 가운데 · 칸 경계 = 오른쪽 몸의 왼쪽 끝 (공격 효과는 오른쪽으로 뻗어 옆 칸까지 감 → 왼쪽 몸 것)
    ysp=[0]+[ (max(B[k][2] for k in ks if k//cols==r) + min(B[k][0] for k in ks if k//cols==r+1))//2 for r in range(rows-1)]+[H]
    own=np.zeros((H,W),int)
    for r in range(rows):
        rk=[k for k in ks if k//cols==r]; xsp=[0]+[B[k][1]-4 for k in rk[1:]]+[W]
        for c,k in enumerate(rk): own[ysp[r]:ysp[r+1], xsp[c]:xsp[c+1]] = ks.index(k)
    P=[]
    for j,k in enumerate(ks):
        m=(own==j)&(al>12); y0,x0,y1,x1=B[k]
        lb,nn=ndimage.label(m); 
        if nn>1:   # 옆 칸에서 넘어온 작은 부스러기 지우기 (몸 상자에서 40px 넘게 떨어진 작은 조각)
            szs=ndimage.sum(m, lb, range(1,nn+1)); ob=ndimage.find_objects(lb); tot=szs.sum()
            for q in range(nn):
                sy,sx=ob[q]; far = sx.stop < x0-40 or sx.start > x1+40 or sy.stop < y0-40 or sy.start > y1+40
                if szs[q] < 0.004*tot and far: m[lb==q+1]=False
        ys,xs=np.where(m)
        feet=int(np.percentile(ys[(xs>=x0)&(xs<x1)], 99.5)); cx=(x0+x1)//2
        P.append(dict(k=k, m=m, top=ys.min(), left=xs.min(), right=xs.max(), feet=feet, cx=cx, bh=feet-y0))
    L=max(p['cx']-p['left'] for p in P)+6; R=max(p['right']-p['cx'] for p in P)+6; T=max(p['feet']-p['top'] for p in P)+6; Bt=max(0,max(ys_.max() for ys_ in [np.where(p['m'])[0] for p in P]) - 0)
    BOT=max(np.where(p['m'])[0].max()-p['feet'] for p in P)+4
    CW, CH = L+R, T+BOT; os.makedirs(out, exist_ok=True); info=[]
    for p,nm in zip(P, poses):
        c=np.zeros((CH,CW,4),np.uint8); ys,xs=np.where(p['m']); ty=ys-p['feet']+T; tx=xs-p['cx']+L; c[ty,tx]=a[ys,xs]
        Image.fromarray(c).save(f"{out}/{name}_{nm}.png"); info.append((nm, int(p['bh'])))
    print(json.dumps({"name":name,"canvas":[int(CW),int(CH)],"anchor":[int(L),int(T)],"bodyH":dict(info)}, ensure_ascii=False))
if __name__=='__main__':
    main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5], (sys.argv[6] if len(sys.argv)>6 else "idle,charge,atk,hurt").split(","))
