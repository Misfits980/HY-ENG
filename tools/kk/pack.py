"""(v434) KayKit(CC0) glTF → My Town 모델 묶음 (assets/town/kk/<묶음>.json + .bin + 텍스처 .webp)
   · 모델마다 위치 int16(상자 기준) · 법선 int8 · UV uint16 · 삼각형 uint16 — 한 묶음 = 파일 3개
   쓰기: python3 tools/kk/pack.py <묶음이름> <텍스처.png> <gltf 파일들...>"""
import json, struct, sys, os, math
import numpy as np
from PIL import Image
CT={5120:np.int8,5121:np.uint8,5122:np.int16,5123:np.uint16,5125:np.uint32,5126:np.float32}
NC={"SCALAR":1,"VEC2":2,"VEC3":3,"VEC4":4}
def acc(j, bins, i):
    a=j["accessors"][i]; bv=j["bufferViews"][a["bufferView"]]; b=bins[bv["buffer"]]
    off=bv.get("byteOffset",0)+a.get("byteOffset",0); n=NC[a["type"]]; dt=np.dtype(CT[a["componentType"]])
    st=bv.get("byteStride", n*dt.itemsize)
    if st==n*dt.itemsize: return np.frombuffer(b, dt, a["count"]*n, off).reshape(a["count"], n).astype(np.float64 if dt.kind=="f" else np.int64)
    out=np.zeros((a["count"],n)); 
    for k in range(a["count"]): out[k]=np.frombuffer(b, dt, n, off+k*st)
    return out
def qmat(q):
    x,y,z,w=q; return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
def nodeM(n):
    M=np.eye(4)
    if "matrix" in n: return np.array(n["matrix"]).reshape(4,4).T
    S=np.diag(n.get("scale",[1,1,1])+[1]); R=np.eye(4); R[:3,:3]=qmat(n.get("rotation",[0,0,0,1])); T=np.eye(4); T[:3,3]=n.get("translation",[0,0,0])
    return T@R@S
def load(f):
    j=json.load(open(f)); d=os.path.dirname(f); bins=[open(os.path.join(d,b["uri"]),"rb").read() for b in j["buffers"]]
    P=[];N=[];U=[];I=[]; base=0
    def walk(ni, M):
        nonlocal base
        n=j["nodes"][ni]; M=M@nodeM(n)
        if "mesh" in n:
            for p in j["meshes"][n["mesh"]]["primitives"]:
                pos=acc(j,bins,p["attributes"]["POSITION"]); nor=acc(j,bins,p["attributes"]["NORMAL"]); uv=acc(j,bins,p["attributes"]["TEXCOORD_0"])
                idx=acc(j,bins,p["indices"]).reshape(-1) if "indices" in p else np.arange(len(pos))
                pos=(np.c_[pos,np.ones(len(pos))]@M.T)[:,:3]; R=M[:3,:3]; nor=nor@np.linalg.inv(R).T if abs(np.linalg.det(R))>1e-9 else nor
                nor=nor/np.maximum(1e-9,np.linalg.norm(nor,axis=1))[:,None]
                P.append(pos);N.append(nor);U.append(uv);I.append(idx+base); base+=len(pos)
        for c in n.get("children",[]): walk(c, M)
    sc=j["scenes"][j.get("scene",0)]
    for r in sc["nodes"]: walk(r, np.eye(4))
    return np.vstack(P), np.vstack(N), np.vstack(U), np.concatenate(I)
def main():
    name, tex = sys.argv[1], sys.argv[2]; files=sys.argv[3:]; out=os.path.join(os.path.dirname(__file__), "..", "..", "assets", "town", "kk"); os.makedirs(out, exist_ok=True)
    B=bytearray(); idx={}
    for f in files:
        P,N,U,I=load(f); k=os.path.basename(f)[:-5]
        assert len(P)<65536, (k,len(P))
        mn=P.min(0); mx=P.max(0); sp=np.maximum(mx-mn,1e-6)
        q=np.round((P-mn)/sp*65535-32768).astype(np.int16); n8=np.round(N*127).astype(np.int8)
        assert U.min()>=-0.001 and U.max()<=1.001, (k, U.min(), U.max())
        u16=np.round(np.clip(U,0,1)*65535).astype(np.uint16); i16=I.astype(np.uint16)
        def put(a):
            while len(B)%4: B.append(0)
            o=len(B); B.extend(a.tobytes()); return o
        idx[k]={"v":len(P),"i":len(I),"mn":[round(x,5) for x in mn],"mx":[round(x,5) for x in mx],"p":put(q),"n":put(n8),"u":put(u16),"x":put(i16)}
    open(os.path.join(out,name+".bin"),"wb").write(B)
    json.dump({"tex":name+".webp","m":idx}, open(os.path.join(out,name+".json"),"w"), separators=(",",":"))
    im=Image.open(tex).convert("RGB"); im=im.resize((512,512), Image.NEAREST) if im.size[0]>512 else im; im.save(os.path.join(out,name+".webp"),"WEBP",quality=92,method=6)
    print(name, len(files), "models", len(B)//1024, "KB")
main()
# (v434) nature 묶음은 만든 뒤 풀 색(연두 → My Town 잔디 초록)을 바꿈 — tools/kk/README 참고
