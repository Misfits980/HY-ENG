import json,glob,collections
I={}; 
for f in sorted(glob.glob('/tmp/claude-0/hs/sva/in*.jsonl')):
    for l in open(f): o=json.loads(l); I[o['i']]=o['s']
out={}; bad=collections.Counter(); n=0; T={"현재","과거","미래","현재진행","과거진행","현재완료","조동사"}
need={1:set(),2:{"C"},3:{"O"},4:{"IO","DO"},5:{"O","OC"}}
allow={1:{"S","V"},2:{"S","V","C"},3:{"S","V","O"},4:{"S","V","IO","DO"},5:{"S","V","O","OC"}}
fs=collections.Counter()
for f in sorted(glob.glob('/tmp/claude-0/hs/sva/out*.jsonl')):
    for l in open(f):
        l=l.strip()
        if not l: continue
        try: o=json.loads(l)
        except Exception: bad['json']+=1; continue
        n+=1; s=I.get(o.get('i')); 
        if s is None: bad['noid']+=1; continue
        F=o.get('f',0); R=o.get('r',[]); t=o.get('t','')
        if not F: bad['f0']+=1; continue
        roles=[r for r,_ in R]; rs=set(roles)
        if "V" not in rs: bad['noV']+=1; continue
        if not need[F]<=rs or not rs<=allow[F] or len(roles)!=len(rs): bad['shape%d'%F]+=1; continue
        p=0; sp=[]; ok=True
        for r,txt in R:
            k=s.find(txt,p)
            if k<0 or not txt.strip(): ok=False; break
            sp.append([r,k,len(txt)]); p=k+len(txt)
        if not ok: bad['span']+=1; continue
        if t not in T: t=""
        out[s]=[F,t,sp]; fs[F]+=1
print("lines",n,"kept",len(out),dict(bad),dict(fs))
json.dump(out, open('/home/claude/hy-eng/data/sva.json','w'), ensure_ascii=False, separators=(',',':'))
import os; print(os.path.getsize('/home/claude/hy-eng/data/sva.json'))
