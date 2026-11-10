"""(v637) 🔴 4줄 팡 — 사용자 「3번도 좋다」
   ① 놀이 섬 🔴 4줄 탑(남쪽) · 누르면 메뉴 (🐣 · 🐥 · 🦅 · 👫 · 섬으로)
   ② 규칙: 가로·세로·대각선 4개 · 봇은 이길 수 있으면 이기고, 질 것 같으면 막음 · 어려움도 빨리 생각
   ③ 봇이랑 끝까지 (알 수 = 놓은 수 · 결과 창 · 🪙 · 기록) · 화면 눌러 칸 고르기
   ④ 👫 친구랑 1:1: 같은 방 → 번갈아 놓기 → 두 화면 같은 판 · 같은 결과
   ⑤ 사진 폰 · 패드 · 가로"""
import asyncio, sys, os, json, random
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from draw635 import boot
from playwright.async_api import async_playwright
OUTD=OUT+"c4637/"; os.makedirs(OUTD, exist_ok=True)
STEP = """async (n)=>{ for(let i=0;i<n;i++){ MG.step(.05,false); await null; await null; } }"""

async def enter(pg):
    for _ in range(30):
        if not await pg.evaluate("()=>MG.on"): break
        await pg.wait_for_timeout(200)
    await pg.evaluate("()=>MG.lobby('c4')")
    for _ in range(80):
        if await pg.evaluate("()=>!!(MG.on && MG.run && MG.run.ready)"): break
        await pg.wait_for_timeout(200)
    await pg.wait_for_timeout(500)

async def main():
    bad=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        ctx,pg,errs=await boot(br,"루아","C4637A", vp={"width":900,"height":700})
        r=await pg.evaluate("()=>{ const L=[]; MG.labels(L); return [!!MG.SPOT.c4, L.map(x=>x.k).sort().join(',')]; }")
        ok(r[0] and "mg_c4" in r[1], f"① 4줄 탑 자리 · 이름표 {r}")
        await pg.evaluate("()=>{ const g=MG.SPOT.c4; HOUSE.setWx(false); TFAC.warp(g[0]-2, g[2]-9); yaw=yawTo=Math.PI; ISLE.CAM.zoom=2.4; ISLE.CAM.pitch=.45; ISLE.CAM.dragAt=performance.now()+1e6; }")
        await pg.wait_for_timeout(2500); await pg.screenshot(path=OUTD+"building.png")
        await ctx.close()
        ctx,pg,errs=await boot(br,"루아","C4637A", isle=False)
        await enter(pg)
        r=await pg.evaluate("()=>{ const M=document.querySelector('#mgUI .c4Menu'); return [MG.run.mode, getComputedStyle(M).display, [...M.querySelectorAll('[data-m]')].map(b=>b.dataset.m).join(','), !!M.querySelector('.out')]; }")
        ok(r==["menu","flex","easy,normal,hard,co",True], f"① 메뉴 (쉬움·보통·어려움·친구랑·섬으로) {r}")
        await pg.screenshot(path=OUTD+"menu.png")
        # ② 규칙 · 봇
        r=await pg.evaluate("""()=>{ const R=MG.run, F=()=>Array.from({length:7},()=>[]);
            const t=(cols,c,r)=>{ const b=F(); cols.forEach(([x,arr])=>b[x]=arr.slice()); return !!R.line4(b,c,r); };
            const h=t([[0,[0]],[1,[0]],[2,[0]],[3,[0]]],3,0), v=t([[2,[1,1,1,1]]],2,3), d1=t([[0,[0]],[1,[1,0]],[2,[1,1,0]],[3,[1,1,1,0]]],3,3), d2=t([[3,[0]],[2,[1,0]],[1,[1,1,0]],[0,[1,1,1,0]]],0,3), no=t([[0,[0]],[1,[0]],[2,[0]],[4,[0]]],4,0);
            const b1=F(); b1[1]=[1,1,1]; const win=R.aiMove(b1.map(x=>x.slice()),1,'easy');
            const b2=F(); b2[4]=[0,0,0]; b2[0]=[1]; const blk=R.aiMove(b2.map(x=>x.slice()),1,'normal');
            const b3=F(); b3[3]=[0,1,0]; b3[2]=[1,0]; b3[4]=[1]; const t0=performance.now(); R.aiMove(b3.map(x=>x.slice()),1,'hard'); const ms=Math.round(performance.now()-t0);
            return [h,v,d1,d2,no,win,blk,ms]; }""")
        ok(r[:5]==[True,True,True,True,False] and r[5]==1 and r[6]==4 and r[7]<1500, f"② 가로·세로·대각선 둘 · 3개는 아님 · 봇이 이김 수 · 막기 · 어려움 생각 {r[7]}ms {r}")
        # ③ 봇이랑 (보통) — 나는 아무 데나
        c0=await pg.evaluate("()=>TECO.coins()")
        await pg.evaluate("()=>{ MG.run.fast=true; MG.run.menuGo('normal'); }"); await pg.evaluate(STEP, 30)
        # 화면 눌러 칸 고르기 (가운데 칸)
        for _ in range(20):
            if await pg.evaluate("()=>MG.run.turn===MG.run.me && !MG.run.over"): break
            await pg.evaluate(STEP, 10)
        x=await pg.evaluate("()=>{ const R=MG.run, v=new THREE.Vector3(0, 3.9, 0).project(MG.run.scene && MG.run.cam ? MG.run.cam : null); return (v.x+1)/2*innerWidth; }")
        n0=await pg.evaluate("()=>MG.run.mv.length")
        await pg.mouse.click(x, 500); await pg.evaluate(STEP, 6)
        r=await pg.evaluate("(n0)=>[MG.run.mv.length>n0, MG.run.mv[n0], MG.run.colAt(%f)]" % x, n0)
        ok(r[0] and r[1]==3 and r[2]==3, f"③ 화면 가운데를 누르면 가운데 칸(4번째)에 놓임 {r}")
        await pg.evaluate(STEP, 20); await pg.screenshot(path=OUTD+"play.png")
        for _ in range(80):
            st=await pg.evaluate("()=>[MG.run.over, MG.run.turn===MG.run.me]")
            if st[0]: break
            if st[1]: await pg.evaluate("()=>{ const R=MG.run, ok=[0,1,2,3,4,5,6].filter(c=>R.bd[c].length<6); R.play(ok[Math.floor(Math.random()*ok.length)]); }")
            await pg.evaluate(STEP, 8)
        await pg.evaluate(STEP, 40)
        r=await pg.evaluate("()=>{ const R=MG.run, n=R.bd.reduce((s,c)=>s+c.length,0), el=document.getElementById('mgRes'); return [R.over, n, R.mv.length, R.win&&R.win.p, el&&el.classList.contains('on'), el?el.querySelector('h3').textContent:'', TECO.coins(), MG.payLeft('c4')]; }")
        ok(r[0] and r[1]==r[2] and r[4] and r[6]>c0 and r[7]==2, f"③ 보통 봇이랑 끝까지 · 알 수 = 놓은 수 · 결과 창 · 🪙 {r}")
        await pg.screenshot(path=OUTD+"result.png")
        # 어려움 vs 아무 데나 → 봇이 이김
        wins=0
        for gi in range(2):
            await pg.evaluate("()=>{ document.getElementById('mgRes').classList.remove('on'); MG.run.menuGo('hard'); }")
            for _ in range(80):
                st=await pg.evaluate("()=>[MG.run.over, MG.run.turn===MG.run.me]")
                if st[0]: break
                if st[1]: await pg.evaluate("()=>{ const R=MG.run, ok=[0,1,2,3,4,5,6].filter(c=>R.bd[c].length<6); R.play(ok[Math.floor(Math.random()*ok.length)]); }")
                await pg.evaluate(STEP, 8)
            if await pg.evaluate("()=>MG.run.win && MG.run.win.p===1-MG.run.me"): wins+=1
            if gi==0:
                await pg.evaluate("()=>{ MG.run.fast=false; }"); await pg.evaluate(STEP, 12); await pg.wait_for_timeout(300); await pg.screenshot(path=OUTD+"win4.png"); await pg.evaluate("()=>{ MG.run.fast=true; }")
            await pg.evaluate(STEP, 40)
        ok(wins==2, f"③ 🦅 어려움 봇은 아무 데나 두는 사람을 이김 {wins}/2")
        r=await pg.evaluate("()=>[(store('hyeng_proto_c4r')||{}).n, (store('hyeng_proto_c4r')||{}).w]")
        ok(r[0]==3, f"③ 기록 3판 {r}")
        ok(not errs, f"오류 0 {errs[:5]}")
        await ctx.close()
        # ④ 같이 1:1
        cA,A_,eA=await boot(br,"루아","CO637A", isle=False); cB,B_,eB=await boot(br,"민수","CO637B", isle=False)
        P2=[A_,B_]
        for x in P2: await enter(x)
        async def steps(n=6, dt=.1):
            for _ in range(n):
                for x in P2: await x.evaluate("async (dt)=>{ MG.step(dt,false); await null; await null; }", dt)
                await A_.wait_for_timeout(60)
        await A_.evaluate("()=>MG.run.menuGo('co')"); await steps(3)
        await A_.evaluate("()=>MG.run.RM.make()"); await steps(4)
        await B_.evaluate("()=>MG.run.menuGo('co')")
        for _ in range(15):
            await B_.evaluate("()=>MG.run.RM.list()"); await steps(2)
            if await B_.evaluate("()=>document.querySelectorAll('#mgUI [data-j]').length"): break
        await B_.evaluate("()=>document.querySelector('#mgUI [data-j]').click()"); await steps(4)
        for x in P2: await x.evaluate("()=>{ MG.run.fast=true; }")
        await A_.evaluate("()=>document.querySelector('#mgUI [data-st]').click()"); await steps(4)
        for x in P2: await x.evaluate("()=>{ TWN8.test=(TWN8.test||0)+5000; }")
        for it in range(90):
            await steps(2)
            r=[await x.evaluate("()=>[MG.run.mode, MG.run.me, MG.run.turn]") for x in P2]
            if all(q[0]=="co-play" for q in r): break
            if it%15==14:
                for x in P2: await x.evaluate("()=>{ TWN8.test=(TWN8.test||0)+3000; }")
        ok(all(q[0]=="co-play" for q in r) and sorted([r[0][1], r[1][1]])==[0,1] and r[0][2]==r[1][2], f"④ 둘이 같은 판 · 나는 빨강/노랑 하나씩 · 같은 차례 {r}")
        await steps(3); await A_.screenshot(path=OUTD+"co_A.png")
        for it in range(60):
            o=[await x.evaluate("()=>[MG.run.over, MG.run.turn===MG.run.me, MG.run.mv.length]") for x in P2]
            if o[0][0] and o[1][0]: break
            for i,x in enumerate(P2):
                if o[i][1] and not o[i][0] and o[0][2]==o[1][2]:
                    await x.evaluate("()=>{ const R=MG.run, ok=[3,2,4,1,5,0,6].filter(c=>R.bd[c].length<6); R.play(Math.random()<.5?ok[0]:ok[Math.floor(Math.random()*ok.length)]); }")
                    break
            await steps(4)
        await steps(30)
        r=[await x.evaluate("()=>{ const el=document.getElementById('mgRes'); return [MG.run.over, JSON.stringify(MG.run.bd), MG.run.win&&MG.run.win.p, MG.run.me, el&&el.classList.contains('on'), el?el.querySelector('h3').textContent:'']; }") for x in P2]
        ok(r[0][0] and r[1][0] and r[0][1]==r[1][1] and r[0][2]==r[1][2] and r[0][4] and r[1][4] and (r[0][2]==-1 or r[0][5]!=r[1][5]), f"④ 끝까지 · 두 화면 같은 판 · 같은 승자 · 한쪽 이김/한쪽 짐 {[(q[2],q[3],q[5]) for q in r]}")
        await B_.screenshot(path=OUTD+"co_end.png")
        ok(not (eA+eB), f"오류 0 (같이) {(eA+eB)[:5]}")
        for c_ in (cA,cB): await c_.close()
        for nm,vp in [("pad",{"width":820,"height":1180}),("land",{"width":844,"height":390})]:
            ctx,pg,errs=await boot(br,"루아","C4637"+nm, vp=vp, isle=False); await enter(pg); await pg.screenshot(path=OUTD+nm+"_menu.png")
            await pg.evaluate("()=>{ MG.run.fast=true; MG.run.menuGo('easy'); }")
            for _ in range(10):
                if await pg.evaluate("()=>MG.run.turn===MG.run.me"): await pg.evaluate("()=>MG.run.play([3,2,4,3,2][MG.run.mv.length%5])")
                await pg.evaluate(STEP, 10)
            await pg.wait_for_timeout(400); await pg.screenshot(path=OUTD+nm+"_play.png")
            r=await pg.evaluate("()=>{ const R=MG.run, p=c=>{ const v=new THREE.Vector3(c-3, .9+c*0, 0).project(R.cam||MG.run.cam); return [(v.x+1)/2*innerWidth, (1-v.y)/2*innerHeight]; }; const a=R.board.localToWorld(new THREE.Vector3(-3.6,7.2,0)).project(R.cam), b=R.board.localToWorld(new THREE.Vector3(3.6,.2,0)).project(R.cam); const t=document.querySelector('#mgUI .c4Top').getBoundingClientRect(); return [Math.round((a.x+1)/2*innerWidth), Math.round((1-a.y)/2*innerHeight), Math.round((b.x+1)/2*innerWidth), Math.round((1-b.y)/2*innerHeight), Math.round(t.bottom), innerWidth, innerHeight]; }")
            ok(r[0]>=0 and r[2]<=r[5] and r[3]<=r[6] and r[1]>=0, f"⑤ {nm}: 판이 화면 안 {r}")
            await ctx.close()
            ok(not errs, f"오류 0 ({nm}) {errs[:3]}")
        await br.close()
    print("BAD:", len(bad)); sys.exit(1 if bad else 0)
if __name__=="__main__": asyncio.run(main())
