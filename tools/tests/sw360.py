"""(v360) 서비스워커가 학원 서버(Firebase) 읽기·실시간 연결을 저장해 두고 옛 값을 돌려주던 큰 버그
  sw.js 를 node 에서 가짜 self·caches 로 돌려 fetch 처리를 확인:
  Firebase GET · 실시간(text/event-stream) · 다른 사이트 = 손대지 않음 / 게임 그림·스크립트·CDN = 저장해 둔 것 먼저 (예전 그대로)"""
import subprocess, os, json, sys
HERE = os.path.dirname(os.path.abspath(__file__)); SW = os.path.join(HERE, "..", "..", "sw.js")
JS = r"""
const fs=require('fs'); const src=fs.readFileSync(process.argv[1],'utf8'); const H={};
const self={ location:new URL('https://misfits980.github.io/HY-ENG/sw.js'), addEventListener:(t,f)=>{ H[t]=f; }, skipWaiting(){}, clients:{claim(){}} };
const caches={ match:async()=>undefined, open:async()=>({put(){}, addAll:async()=>{}, add:async()=>{}}), keys:async()=>[], delete:async()=>true };
const fetch=async()=>({ok:true, clone(){ return this; }});
new Function('self','caches','fetch', src)(self, caches, fetch);
const out={};
const T=[['fb','https://hy-eng-raid-default-rtdb.asia-southeast1.firebasedatabase.app/hy/hw/cur.json',{}],
         ['fbus','https://hy-eng-raid-default-rtdb.firebaseio.com/hy/roster.json',{}],
         ['es','https://hy-eng-raid-default-rtdb.asia-southeast1.firebasedatabase.app/battle/7114.json',{accept:'text/event-stream'}],
         ['sheet','https://script.google.com/macros/s/x/exec',{}],
         ['other','https://example.com/a.json',{}],
         ['art','https://misfits980.github.io/HY-ENG/assets/chars/run-hero.webp',{}],
         ['js','https://misfits980.github.io/HY-ENG/three.min.js',{}],
         ['cdn','https://cdnjs.cloudflare.com/ajax/libs/x/1.0/x.min.js',{}]];
for(const [k,u,h] of T){ let used=false; const req={url:u, method:'GET', mode:'cors', headers:{get:n=>h[n.toLowerCase()]||null}};
  try{ H.fetch({request:req, respondWith(){ used=true; }, waitUntil(){}}); }catch(e){ out[k]='ERR '+e.message; continue; } out[k]=used; }
console.log(JSON.stringify(out));
"""
r = subprocess.run(["node", "-e", JS, SW], capture_output=True, text=True)
print(r.stdout.strip(), r.stderr.strip()[:300])
bad = []
try:
    o = json.loads(r.stdout.strip().splitlines()[-1])
except Exception:
    o = {}; bad.append("node 실행 실패")
def ok(c, m):
    print(("OK  " if c else "BAD ") + m)
    if not c: bad.append(m)
ok(o.get("fb") is False and o.get("fbus") is False, f"Firebase 읽기는 서비스워커가 손대지 않음 {o.get('fb')} {o.get('fbus')}")
ok(o.get("es") is False, f"실시간 연결(event-stream)도 손대지 않음 {o.get('es')}")
ok(o.get("sheet") is False and o.get("other") is False, "구글 시트·다른 사이트도 손대지 않음")
ok(o.get("art") is True and o.get("js") is True and o.get("cdn") is True, f"게임 그림·스크립트·CDN 은 예전처럼 저장 {o.get('art')} {o.get('js')} {o.get('cdn')}")
print("결과:", "통과" if not bad else "실패 " + str(bad))
