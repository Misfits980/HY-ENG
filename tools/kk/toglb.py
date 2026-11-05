"""gltf(데이터 URI) → glb · OBJ+MTL → glb (재료 색) — 원본 보관용
사용: toglb.py gltf <src.gltf> <dst.glb> [뺄 애니 정규식]
      toglb.py obj  <src.obj>  <dst.glb>"""
import sys, json, base64, struct, re, os
def pad4(b, c=b'\0'): return b + c*((4-len(b)%4)%4)
def write_glb(j, binb, dst):
    js=pad4(json.dumps(j,separators=(',',':')).encode(), b' '); binb=pad4(binb)
    out=struct.pack('<III',0x46546C67,2,12+8+len(js)+8+len(binb))+struct.pack('<II',len(js),0x4E4F534A)+js+struct.pack('<II',len(binb),0x004E4942)+binb
    open(dst,'wb').write(out)
def from_gltf(src, dst, drop=None):
    j=json.load(open(src)); assert len(j['buffers'])==1
    raw=base64.b64decode(j['buffers'][0]['uri'].split(',',1)[1])
    if drop:
        R=re.compile(drop); keep=[a for a in j.get('animations',[]) if not R.search(a.get('name',''))]
        j['animations']=keep
    # 움직임 없는 줄(값이 처음부터 끝까지 같음) = 키 하나로
    CS={5120:1,5121:1,5122:2,5123:2,5125:4,5126:4}; NC={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}
    def vals(i):
        a=j['accessors'][i]; bv=j['bufferViews'][a['bufferView']]; o=bv.get('byteOffset',0)+a.get('byteOffset',0); n=NC[a['type']]
        assert a['componentType']==5126 and 'byteStride' not in bv
        return struct.unpack_from('<%df'%(a['count']*n), raw, o), n
    for an in j.get('animations',[]):
        for s in an['samplers']:
            v,n=vals(s['output'])
            if all(abs(v[k]-v[k%n])<1e-5 for k in range(len(v))):
                ai=dict(j['accessors'][s['input']]); ao=dict(j['accessors'][s['output']])
                t0=vals(s['input'])[0][0]; ai['count']=1; ai['min']=[t0]; ai['max']=[t0]; ao['count']=1; ao.pop('min',None); ao.pop('max',None)
                j['accessors'].append(ai); s['input']=len(j['accessors'])-1; j['accessors'].append(ao); s['output']=len(j['accessors'])-1
    # 쓰는 accessor/bufferView 만 다시 모음
    used=set()
    def acc(i): used.add(i)
    for m in j['meshes']:
        for p in m['primitives']:
            for v in p['attributes'].values(): acc(v)
            if 'indices' in p: acc(p['indices'])
            for t in p.get('targets',[]):
                for v in t.values(): acc(v)
    for s in j.get('skins',[]):
        if 'inverseBindMatrices' in s: acc(s['inverseBindMatrices'])
    for a in j.get('animations',[]):
        for s in a['samplers']: acc(s['input']); acc(s['output'])
    amap={}; newA=[]; newBV=[]; blob=bytearray()
    for i in sorted(used):
        a=dict(j['accessors'][i]); bv=j['bufferViews'][a['bufferView']]
        es=CS[a['componentType']]*NC[a['type']]; st=bv.get('byteStride',es)
        o=bv.get('byteOffset',0)+a.get('byteOffset',0); data=raw[o:o+st*(a['count']-1)+es]; a['byteOffset']=0
        while len(blob)%4: blob.append(0)
        nb={'buffer':0,'byteOffset':len(blob),'byteLength':len(data)}
        if 'byteStride' in bv: nb['byteStride']=bv['byteStride']
        if 'target' in bv: nb['target']=bv['target']
        blob+=data; newBV.append(nb); a['bufferView']=len(newBV)-1; amap[i]=len(newA); newA.append(a)
    for m in j['meshes']:
        for p in m['primitives']:
            p['attributes']={k:amap[v] for k,v in p['attributes'].items()}
            if 'indices' in p: p['indices']=amap[p['indices']]
            if 'targets' in p: p['targets']=[{k:amap[v] for k,v in t.items()} for t in p['targets']]
    for s in j.get('skins',[]):
        if 'inverseBindMatrices' in s: s['inverseBindMatrices']=amap[s['inverseBindMatrices']]
    for a in j.get('animations',[]):
        for s in a['samplers']: s['input']=amap[s['input']]; s['output']=amap[s['output']]
    j['accessors']=newA; j['bufferViews']=newBV; j['buffers']=[{'byteLength':len(blob)}]
    write_glb(j, bytes(blob), dst)
def from_obj(src, dst):
    mtl={}; cur=None; d=os.path.dirname(src)
    V=[];N=[];prims={}; order=[]; mat='default'
    for line in open(src, errors='ignore'):
        t=line.split()
        if not t: continue
        if t[0]=='mtllib':
            mp=os.path.join(d,' '.join(t[1:]))
            if os.path.exists(mp):
                for l2 in open(mp, errors='ignore'):
                    u=l2.split()
                    if not u: continue
                    if u[0]=='newmtl': cur=' '.join(u[1:]); mtl[cur]=[.8,.8,.8,1]
                    elif u[0]=='Kd' and cur: mtl[cur][:3]=[float(x) for x in u[1:4]]
                    elif u[0]=='d' and cur: mtl[cur][3]=float(u[1])
        elif t[0]=='v': V.append([float(x) for x in t[1:4]])
        elif t[0]=='vn': N.append([float(x) for x in t[1:4]])
        elif t[0]=='usemtl': mat=' '.join(t[1:])
        elif t[0]=='f':
            fs=[]
            for s in t[1:]:
                p=s.split('/'); vi=int(p[0]); ni=int(p[2]) if len(p)>2 and p[2] else 0
                fs.append((vi-1 if vi>0 else len(V)+vi, (ni-1 if ni>0 else len(N)+ni) if ni else -1))
            if mat not in prims: prims[mat]=[]; order.append(mat)
            for k in range(1,len(fs)-1): prims[mat].append((fs[0],fs[k],fs[k+1]))
    blob=bytearray(); acc=[]; bvs=[]; meshp=[]; mats=[]
    def add(arr, fmt, comp, typ, target, mm=False):
        while len(blob)%4: blob.append(0)
        b=b''.join(struct.pack(fmt,*x) if isinstance(x,(list,tuple)) else struct.pack(fmt,x) for x in arr)
        bvs.append({'buffer':0,'byteOffset':len(blob),'byteLength':len(b),'target':target}); blob.extend(b)
        a={'bufferView':len(bvs)-1,'componentType':comp,'count':len(arr),'type':typ}
        if mm: a['min']=[min(x[i] for x in arr) for i in range(3)]; a['max']=[max(x[i] for x in arr) for i in range(3)]
        acc.append(a); return len(acc)-1
    import math
    for m in order:
        P=[];NN=[];I=[]; key={}
        for tri in prims[m]:
            if any(ni<0 for _,ni in tri):
                a,b,c=[V[vi] for vi,_ in tri]; u=[b[i]-a[i] for i in range(3)]; w=[c[i]-a[i] for i in range(3)]
                n=[u[1]*w[2]-u[2]*w[1],u[2]*w[0]-u[0]*w[2],u[0]*w[1]-u[1]*w[0]]; L=math.sqrt(sum(x*x for x in n)) or 1; fn=[x/L for x in n]
            for vi,ni in tri:
                k=(vi,ni) if ni>=0 else (vi,'f',tuple(round(x,4) for x in fn))
                if k not in key: key[k]=len(P); P.append(V[vi]); NN.append(N[ni] if ni>=0 else fn)
                I.append(key[k])
        pa=add(P,'<3f',5126,'VEC3',34962,True); na=add(NN,'<3f',5126,'VEC3',34962)
        ia=add(I,'<I' if len(P)>65535 else '<H',5125 if len(P)>65535 else 5123,'SCALAR',34963)
        c=mtl.get(m,[.8,.8,.8,1]); mats.append({'name':m,'pbrMetallicRoughness':{'baseColorFactor':c,'metallicFactor':0,'roughnessFactor':.9}})
        meshp.append({'attributes':{'POSITION':pa,'NORMAL':na},'indices':ia,'material':len(mats)-1})
    j={'asset':{'version':'2.0','generator':'hyeng toglb'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[{'mesh':0,'name':os.path.basename(src)[:-4]}],
       'meshes':[{'primitives':meshp}],'materials':mats,'accessors':acc,'bufferViews':bvs,'buffers':[{'byteLength':len(blob)}]}
    write_glb(j, bytes(blob), dst)
if __name__=='__main__':
    k=sys.argv[1]
    if k=='gltf': from_gltf(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv)>4 else None)
    else: from_obj(sys.argv[2], sys.argv[3])
