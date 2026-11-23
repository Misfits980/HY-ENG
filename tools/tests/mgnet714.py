"""(v714) 🔌 오락실 친구끼리 끊김 — 사용자: 「마이타운 물총아레나 애들끼리 할 때 서로 툭툭 끊기는 현상」 → 「고쳐 보자 오락실 안에 게임들」
   ① MG.track: 늦게 온 옛 자리 버림 · 들쭉날쭉 와도 한 프레임에 건너뛰는 양이 작음 · 서 있다 움직이기 · 튄 자리는 서서히 메움
   ② MG.liveSync / MG.room 받기: Firebase 계속 받기(put/patch/null) 그대로 맞춤 · 받기가 살아 있으면 방 전체 GET 안 함
   ③ 계속 받기가 안 되는 곳(503) → 예전 받기로 · 하나 끝나야 다음(겹친 GET 0) · 내 칸 PUT 동시에 3개까지
   ④ 물총 아레나 둘이 같이 (가짜 계속 받기): 방 만들기 → 들어가기 → 시작 → 친구 모습이 따라옴 · 오류 없음
   ⑤ 얼굴 사진(4줄 팡 · 컬러팡 · 그림 맞히기)은 표정이 바뀔 때만 다시 그림"""
import asyncio, sys, os, json
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
import fakefb
from fakefb import fake
from playwright.async_api import async_playwright

CNT={"get":0, "conc":0, "maxc":0, "put":0, "pconc":0, "pmax":0}
async def counting(r):
    u=r.request.url
    if ("firebasedatabase.app" in u) and "/hy/day/mga" in u and "fes=1" not in u and "text/event-stream" not in (r.request.headers.get("accept") or ""):
        m=r.request.method
        if m=="GET" and "/p/" not in u:
            CNT["get"]+=1; CNT["conc"]+=1; CNT["maxc"]=max(CNT["maxc"], CNT["conc"])
            try:
                await asyncio.sleep(.12); return await fake(r)
            finally: CNT["conc"]-=1
        if m=="PUT" and "/p/" in u:
            CNT["put"]+=1; CNT["pconc"]+=1; CNT["pmax"]=max(CNT["pmax"], CNT["pconc"])
            try:
                await asyncio.sleep(.25); return await fake(r)
            finally: CNT["pconc"]-=1
    return await fake(r)

FAKE_ES="""(()=>{ class FES{ constructor(url){ this.url=url; this.readyState=0; this.L={}; this.first=true; this.closed=false; this.onerror=null; window.__fesN=(window.__fesN||0)+1; setTimeout(()=>this.run(), 30); }
    addEventListener(k,f){ (this.L[k]=this.L[k]||[]).push(f); } close(){ this.closed=true; this.readyState=2; }
    emit(k,m){ (this.L[k]||[]).forEach(f=>{ try{ f({data:JSON.stringify(m)}); }catch(e){} }); }
    async run(){ this.readyState=1; while(!this.closed){ let d=null; try{ const r=await fetch(this.url+(this.url.indexOf('?')>=0?'&':'?')+'fes=1', {cache:'no-store'}); d=await r.json(); }catch(e){} if(this.closed) break; this.diff(d); await new Promise(r=>setTimeout(r,40)); } }
    diff(d){ const J=x=>JSON.stringify(x===undefined?null:x); if(this.first){ this.first=false; this.prev=JSON.parse(J(d)); this.emit('put',{path:'/',data:d}); return; }
      const P=this.prev||{}, N=d||{}; if(!d && this.prev){ this.emit('put',{path:'/',data:null}); this.prev=null; return; }
      new Set([...Object.keys(P),...Object.keys(N)]).forEach(k=>{ const a=P[k], b=N[k]; if(J(a)===J(b)) return;
        if(a && b && typeof a==='object' && typeof b==='object' && !Array.isArray(a) && !Array.isArray(b) && k!=='h'){ new Set([...Object.keys(a),...Object.keys(b)]).forEach(kk=>{ if(J(a[kk])!==J(b[kk])) this.emit('put',{path:'/'+k+'/'+kk, data:b[kk]===undefined?null:b[kk]}); }); }
        else this.emit('put',{path:'/'+k, data:b===undefined?null:b}); });
      this.prev=JSON.parse(J(d)); } }
  window.EventSource=FES; })();"""

async def main():
    bad=[]; errs=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        async def boot(nick, code, es, route=counting):
            ctx=await br.new_context(viewport={"width":480,"height":320}, device_scale_factor=1)
            if es: await ctx.add_init_script(FAKE_ES)
            pg=await ctx.new_page(); pg.set_default_timeout(150000); pg.on("pageerror", lambda e: errs.append(nick+": "+str(e)[:200]))
            await pg.route("**/*", route); await pg.goto(ORIGIN+"proto/house.html?isle=1&perf=off"); await pg.wait_for_timeout(300)
            await pg.evaluate("([n,c])=>{ localStorage.setItem('hyeng_proto_code', JSON.stringify(c)); localStorage.setItem('hyeng_nick', n); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); }", [nick, code])
            await pg.reload(); await pg.wait_for_timeout(2400); return ctx, pg
        # ── ① 따라가기 (한 페이지에서 계산만)
        cT,T=await boot("시험","TT714",False)
        r=await T.evaluate("""()=>{ const out={}; let s=7; const rnd=()=>{ s=(s*9301+49297)%233280; return s/233280; };
            /* 친구가 5m/s 로 달림 · 0.1초마다 보냄 · 도착은 60~250ms + 가끔 0.7초 · 순서 바뀜도 */
            const T=MG.track(), arr=[]; for(let i=0;i<80;i++){ const st=1e6+i*100, lat=rnd()<.06?700:60+rnd()*190; arr.push([st+lat+5e5, st, [i*.5, 0, 0, 0]]); } arr.sort((a,b)=>a[0]-b[0]);
            let ai=0, last=null, maxStep=0, back=0, n=0; for(let now=arr[0][0]; now<arr[arr.length-1][0]+400; now+=16.7){ while(ai<arr.length && arr[ai][0]<=now){ T.push(arr[ai][1], arr[ai][2], arr[ai][0]); ai++; }
              const v=T.smooth(now, [0,0,0,1]); if(v && last){ const d=v[0]-last; if(ai>6){ maxStep=Math.max(maxStep, Math.abs(d)); if(d<-.02) back++; n++; } } if(v) last=v[0]; }
            out.maxStep=+maxStep.toFixed(3); out.back=back; out.n=n;
            /* 옛것 버림 */ const T2=MG.track(); T2.push(2000,[1,0,0,0],1000); T2.push(1900,[9,0,0,0],1010); out.old=T2.b.length;
            /* 서 있다 움직이기: 2초 쉬고 다시 → 사이에 「그 자리」 점 */ const T3=MG.track(); T3.push(1000,[0,0,0,0],0); T3.push(1100,[0,0,0,0],100); T3.push(3100,[1,0,0,0],2100); out.hold=T3.b.length;
            /* 달리다 늦게 온 것은 그대로 잇기 */ const T4=MG.track(); T4.push(1000,[0,0,0,0],0); T4.push(1100,[.5,0,0,0],100); T4.push(1700,[3.5,0,0,0],700); out.run=T4.b.length;
            return out; }""")
        ok(r["maxStep"]<0.3 and r["back"]<=2 and r["n"]>300, f"① 들쭉날쭉·순서 바뀜·0.7초 늦음에도 한 프레임 건너뜀 {r['maxStep']}m 아래 (5m/s = 0.083m/프레임) · 뒤로 감 {r['back']} {r}")
        ok(r["old"]==1 and r["hold"]==4 and r["run"]==3, f"① 옛것 버림 · 쉬었다 움직이면 그 자리 점 · 달리다 늦은 건 그대로 {r}")
        r=await T.evaluate("""()=>{ const R={path:'/x', d:null}, S=MG.liveSync(R,'ME'); S.setAt('/', {h:{n:'a'}, p:{A:{x:1}}}); S.setAt('/p/B', {x:2}); S.setAt('/h', {st:5}, true); S.setAt('/p/A', null); S.setAt('/b', [[1,2],[3,4]]); S.setAt('/b/1', [5,6]); S.setAt('/e/ME/q1', {k:'hit'});
            return JSON.stringify(R.d); }""")
        ok(r=='{"h":{"n":"a","st":5},"p":{"B":{"x":2}},"b":[[1,2],[5,6]],"e":{"ME":{"q1":{"k":"hit"}}}}', f"② 계속 받기 맞춤 (put · patch · 지움 · 배열) {r}")
        await cT.close()
        # ── ③ 계속 받기 없음(503) → 예전 받기 · 겹침 없음
        cA,A=await boot("루아","AAAA2",False); cB,B=await boot("민수","BBBB3",False)
        async def coop(A,B):
            await A.evaluate("()=>MG.enter('arena',{mode:'co', diff:'easy', quick:1})"); await B.evaluate("()=>MG.enter('arena',{mode:'co', diff:'easy', quick:1})"); await A.wait_for_timeout(1800)
            await A.evaluate("()=>document.querySelector('#mgUI .mgRoomP [data-mk]').click()"); await A.wait_for_timeout(1500)
            for _ in range(40):
                if await B.evaluate("()=>document.querySelectorAll('#mgUI .mgRoomP [data-j]').length"): break
                await B.wait_for_timeout(300)
            await B.evaluate("()=>document.querySelector('#mgUI .mgRoomP [data-j]').click()"); await B.wait_for_timeout(2500)
            await A.evaluate("()=>document.querySelector('#mgUI .mgRoomP [data-st]').click()")
            for _ in range(140):
                ph=[await x.evaluate("()=>MG.run.NETR && MG.run.NETR.phase") for x in (A,B)]
                if ph==["play","play"]: return True
                await A.wait_for_timeout(250)
            return False
        for k in CNT: CNT[k]=0
        st=await coop(A,B)
        await A.wait_for_timeout(3000)
        net=[await x.evaluate("()=>MG.run.NETR.net()") for x in (A,B)]
        ok(st and all(n["dead"] and not n["stream"] for n in net) and CNT["get"]>10 and CNT["maxc"]<=2, f"③ 계속 받기가 막힌 곳 = 예전 받기 · 겹친 GET 최대 {CNT['maxc']} (두 기기 합) · GET {CNT['get']} {net}")
        ok(CNT["pmax"]<=6 and CNT["put"]>5, f"③ 내 칸 PUT 동시에 기기마다 3개까지 (두 기기 합 최대 {CNT['pmax']}) · PUT {CNT['put']}")
        for x in (A,B): await x.evaluate("()=>MG.exit()")
        await cA.close(); await cB.close()
        # ── ④ 가짜 계속 받기 → GET 없이 같이 놀기 · 친구가 따라옴
        cA,A=await boot("루아","AAAA5",True); cB,B=await boot("민수","BBBB6",True)
        for k in CNT: CNT[k]=0
        st=await coop(A,B)
        g0=CNT["get"]
        for x in (A,B): await x.evaluate("()=>{ renderer.render=()=>{}; }")   # 그리기 끔 (느린 swiftshader) — 계산·받기는 그대로
        await A.wait_for_timeout(8500)   # 소개 끝
        await A.evaluate("()=>{ const me=MG.run.me, x0=me.p.x, t0=performance.now(); window.__drv=setInterval(()=>{ me.p.x=x0+3*Math.sin((performance.now()-t0)/1000*Math.PI/2); me.v.set(0,0,0); }, 16); }")
        r=await B.evaluate("""(ms)=>new Promise(res=>{ const R=MG.run, L=[]; const t0=performance.now(); const f=()=>{ const a=Object.values(R.PEER)[0]; if(a) L.push(a.p.x); if(performance.now()-t0<ms) requestAnimationFrame(f); else { let mx=0, mv=0; for(let i=1;i<L.length;i++){ mx=Math.max(mx, Math.abs(L[i]-L[i-1])); } res({n:L.length, maxStep:+mx.toFixed(3), span:+(Math.max(...L)-Math.min(...L)).toFixed(2), legs:!!(a=>a&&a.c)(Object.values(R.PEER)[0])}); } }; requestAnimationFrame(f); })""", 5000)
        net=[await x.evaluate("()=>MG.run.NETR.net()") for x in (A,B)]
        ok(st and all(n["stream"] for n in net), f"④ 계속 받기로 방 만들기·들어가기·시작 {net}")
        ok(CNT["get"]-g0<=2, f"④ 노는 동안 방 전체 GET 안 함 (계속 받기) {CNT['get']-g0}")
        ok(r["n"]>100 and r["span"]>4 and r["maxStep"]<0.35, f"④ B 화면의 A 가 왔다 갔다 따라옴 · 한 프레임 최대 {r['maxStep']}m {r}")
        await A.evaluate("()=>clearInterval(__drv)")
        for x in (A,B): await x.evaluate("()=>MG.exit()")
        await A.wait_for_timeout(800)
        r=await A.evaluate("()=>window.__fesN")
        await cA.close(); await cB.close()
        # ── ⑤ 얼굴 사진
        cC,C=await boot("루아","CCCC7",False)
        await C.evaluate("()=>MG.enter('c4',{go:'normal'})"); await C.wait_for_timeout(2500)
        r=await C.evaluate("""()=>new Promise(res=>{ const rn=renderer, o=rn.render; let n=0; rn.render=function(sc){ if(sc && sc!==MG.run.scene && sc.children && sc.children.some(c=>c.isGroup)) n++; return o.apply(this, arguments); }; setTimeout(()=>{ rn.render=o; res(n); }, 1500); })""")
        ok(r<=1, f"⑤ 4줄 팡 얼굴 사진: 표정이 그대로면 다시 안 그림 (1.5초에 {r}번 · 예전 8프레임마다)")
        await C.evaluate("()=>MG.exit()"); await C.wait_for_timeout(800)
        await C.evaluate("()=>MG.enter('card',{quick:1, mode:'solo'})"); await C.wait_for_timeout(3500)
        r=await C.evaluate("""()=>new Promise(res=>{ const rn=renderer, o=rn.render; let n=0; rn.render=function(sc){ if(sc && sc!==MG.run.scene && sc.children && sc.children.some(c=>c.isGroup)) n++; return o.apply(this, arguments); }; setTimeout(()=>{ rn.render=o; res(n); }, 1500); })""")
        px=await C.evaluate("()=>{ const c=document.querySelector('#mgUI .cpPor canvas'); if(!c) return -1; const g=c.getContext('2d'), d=g.getImageData(0,0,c.width,c.height).data; let n=0; for(let i=3;i<d.length;i+=4) if(d[i]>0) n++; return n; }")
        ok(r<=1 and px>200, f"⑤ 컬러팡 얼굴 사진: 그려져 있고({px}점) 표정 그대로면 다시 안 그림 ({r}번)")
        await cC.close()
        await br.close()
    ok(not real_errs(errs), f"페이지 오류 없음 {real_errs(errs)[:3]}")
    print("\n결과:", "모두 통과" if not bad else f"{len(bad)}개 실패"); sys.exit(1 if bad else 0)
asyncio.run(main())
