"""(v638) 🎳 볼링 · 🎯 다트 — 사용자 「5번은 한 번씩 좋다」
   ① 놀이 섬 🎳 볼링장(서쪽) · 메뉴 (볼링 · 다트 · 범퍼 · 섬으로)
   ② 볼링 점수 셈 (5프레임: 퍼펙트 150 · 스페어 · 보통 · 끝났는지)
   ③ 볼링: 가운데로 세게 → 핀이 많이 넘어짐 · 다음 굴림은 남은 핀만 · 범퍼 끄면 도랑 0 · 위로 쓱 밀기로 굴림 · 5프레임 끝까지 → 결과 · 🪙
   ④ 다트: 불 50 · 트리플 20 = 60 · 판 밖 0 · 9개 끝 → 합계 · 결과
   ⑤ 사진 폰 · 패드 · 가로"""
import asyncio, sys, os, json, random
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from draw635 import boot
from playwright.async_api import async_playwright
OUTD=OUT+"bowl638/"; os.makedirs(OUTD, exist_ok=True)
STEP = """async (n)=>{ for(let i=0;i<n;i++){ MG.step(.05,false); await null; await null; } }"""

async def enter(pg, opt="{}"):
    for _ in range(30):
        if not await pg.evaluate("()=>MG.on"): break
        await pg.wait_for_timeout(200)
    await pg.evaluate("()=>MG.lobby('bowl')")
    for _ in range(80):
        if await pg.evaluate("()=>!!(MG.on && MG.run && MG.run.ready)"): break
        await pg.wait_for_timeout(200)
    await pg.wait_for_timeout(500)

async def wait_aim(pg, n=400):
    for _ in range(n):
        r=await pg.evaluate("()=>[MG.run.bw.ph, MG.run.mode]")
        if r[0]=="aim" or r[1]!="bowl": return r
        await pg.evaluate(STEP, 6)
    return r

async def main():
    bad=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        ctx,pg,errs=await boot(br,"루아","BW638A", vp={"width":900,"height":700})
        r=await pg.evaluate("()=>{ const L=[]; MG.labels(L); return [!!MG.SPOT.bowl, L.map(x=>x.k).sort().join(',')]; }")
        ok(r[0] and "mg_bowl" in r[1], f"① 볼링장 자리 · 이름표 {r}")
        await pg.evaluate("()=>{ const g=MG.SPOT.bowl; HOUSE.setWx(false); TFAC.warp(g[0]+9, g[2]+1.5); yaw=yawTo=-Math.PI/2; ISLE.CAM.zoom=2.4; ISLE.CAM.pitch=.45; ISLE.CAM.dragAt=performance.now()+1e6; }")
        await pg.wait_for_timeout(2500); await pg.screenshot(path=OUTD+"building.png")
        await ctx.close()
        ctx,pg,errs=await boot(br,"루아","BW638A", isle=False)
        await enter(pg)
        r=await pg.evaluate("()=>{ const M=document.querySelector('#mgUI .puM'); return [MG.run.mode, getComputedStyle(M).display, [...M.querySelectorAll('[data-m]')].map(b=>b.dataset.m).join(','), !!M.querySelector('[data-sg]'), !!M.querySelector('.out')]; }")
        ok(r==["menu","flex","bowl,dart",True,True], f"① 메뉴 (볼링 · 다트 · 범퍼 · 섬으로) {r}")
        await pg.screenshot(path=OUTD+"menu.png")
        r=await pg.evaluate("""()=>{ const R=MG.run, S=x=>R.bowlScore(x).total;
            return [S([10,10,10,10,10,10,10]), S([5,5,5,5,5,5,5,5,5,5,5]), S([3,4,3,4,3,4,3,4,3,4]), S([10,3,4]), R.bowlDone([10,10,10,10,10,10,10]), R.bowlDone([3,4,3,4,3,4,3,4,3,4]), R.bowlDone([3,4,3,4,3,4,3,4,5,5]), R.bowlDone([3,4,3,4,3,4,3,4,5,5,2]),
              R.bowlScore([10]).marks[0].join(''), R.bowlScore([7,3]).marks[0].join(''), R.bowlScore([0,5]).marks[0].join('')]; }""")
        ok(r==[150,75,35,24,True,True,False,True,"X","7/","-5"], f"② 볼링 점수 셈 (퍼펙트 150 · 스페어 75 · 보통 35 · 끝났는지 · X / -) {r}")
        # ③ 볼링
        c0=await pg.evaluate("()=>TECO.coins()")
        await pg.evaluate("()=>{ MG.run.fast=true; MG.run.menuGo('bowl'); }"); await pg.evaluate(STEP, 4)
        await pg.screenshot(path=OUTD+"bowl_aim.png")
        await pg.evaluate("()=>MG.run.throwBall(0, 0, 13)")
        for _ in range(12):
            await pg.evaluate(STEP, 3)
            z=await pg.evaluate("()=>MG.run.bw.ph")
        await pg.evaluate("()=>{ MG.run.fast=false; }"); await pg.evaluate(STEP, 2); await pg.wait_for_timeout(250); await pg.screenshot(path=OUTD+"bowl_hit.png"); await pg.evaluate("()=>{ MG.run.fast=true; }")
        await wait_aim(pg)
        r=await pg.evaluate("()=>{ const R=MG.run; return [R.bw.rolls.slice(), R.pins.filter(p=>p.up && p.g.visible).length]; }")
        ok(len(r[0])>=1 and r[0][0]>=6 and (r[0][0]==10 or r[1]==10-r[0][0]), f"③ 가운데로 세게 → 핀 {r[0][0]}개 · 다음 굴림은 남은 핀 {r[1]}개만 {r}")
        # 위로 쓱 밀기
        if await pg.evaluate("()=>MG.run.bw.ph==='aim'"):
            n0=await pg.evaluate("()=>MG.run.bw.rolls.length")
            await pg.mouse.move(195, 720); await pg.mouse.down(); await pg.mouse.move(197, 600, steps=3); await pg.mouse.move(200, 420, steps=3); await pg.mouse.up()
            r=await pg.evaluate("()=>[MG.run.bw.ph, MG.run.bw.vz]")
            ok(r[0] in ("roll","count") and r[1]<-5, f"③ 위로 쓱 밀면 굴러감 {r}")
            await wait_aim(pg)
        # 범퍼 끄고 도랑
        await pg.evaluate("()=>{ document.querySelector('#mgUI .spBtn').click(); }")
        r0=await pg.evaluate("()=>[MG.run.SET.bump, MG.run.bw.rolls.length]")
        await pg.evaluate("()=>MG.run.throwBall(-.85, -1.4, 9)")
        await wait_aim(pg)
        r=await pg.evaluate("(n)=>[MG.run.bw.gutter, MG.run.bw.rolls[n]]", r0[1])
        ok(r0[0]==0 and r[1]==0, f"③ 범퍼 끄면 도랑 → 0점 {r0} {r}")
        await pg.evaluate("()=>{ document.querySelector('#mgUI .spBtn').click(); }")
        for _ in range(16):
            r=await wait_aim(pg)
            if r[1]!="bowl" or await pg.evaluate("()=>!!document.querySelector('#mgUI .puR')"): break
            await pg.evaluate("()=>MG.run.throwBall((Math.random()-.5)*.6, (Math.random()-.5)*.3, 8+Math.random()*6)")
        await pg.evaluate(STEP, 40)
        r=await pg.evaluate("()=>{ const R=MG.run, el=document.querySelector('#mgUI .puR'); return [R.bowlDone(R.bw.rolls), R.bw.rolls, R.bowlScore(R.bw.rolls).total, !!el, el?el.textContent:'', TECO.coins(), MG.payLeft('bowl')]; }")
        ok(r[0] and r[3] and str(r[2]) in r[4] and r[5]>c0 and r[6]==2, f"③ 5프레임 끝 · 결과 창 점수 · 🪙 {r}")
        await pg.screenshot(path=OUTD+"bowl_end.png")
        # ④ 다트
        await pg.evaluate("()=>{ (document.querySelector('#mgUI .puR')||{remove(){}}).remove(); MG.run.menuGo('dart'); }"); await pg.evaluate(STEP, 4)
        await pg.screenshot(path=OUTD+"dart_aim.png")
        r=await pg.evaluate("()=>{ const R=MG.run; return [R.scoreAt(0,0).s, R.scoreAt(0,.07).s, R.scoreAt(0,.6).s, R.scoreAt(0,.98).s, R.scoreAt(.3,0).s, R.scoreAt(0,1.2).s, R.scoreAt(0,.6).w]; }")
        ok(r==[50,25,60,40,6,0,"triple twenty"], f"④ 다트 점수: 불 50 · 25 · 트리플 20 = 60 · 더블 20 = 40 · 6 · 밖 0 · 영어 {r}")
        tot=0
        for i,(x,y) in enumerate([(0,0),(0,.6),(0,1.3),(.3,0),(0,.3),(0,.98),(-.4,.2),(.1,-.5),(0,0)]):
            for _ in range(40):
                if await pg.evaluate("()=>!MG.run.dt.fly"): break
                await pg.evaluate(STEP, 2)
            sc=await pg.evaluate("([x,y])=>{ const s=MG.run.dart(x,y); return s?s.s:-1; }", [x,y]); tot+=sc
            if i==1:
                await pg.evaluate("()=>{ MG.run.fast=false; }"); await pg.evaluate(STEP, 12); await pg.wait_for_timeout(200); await pg.screenshot(path=OUTD+"dart_hit.png"); await pg.evaluate("()=>{ MG.run.fast=true; }")
        await pg.evaluate(STEP, 60)
        r=await pg.evaluate("()=>{ const el=document.querySelector('#mgUI .puR'); return [MG.run.dt.n, MG.run.dt.sum, !!el, el?el.textContent:'', MG.payLeft('bowl')]; }")
        ok(r[0]==9 and r[1]==tot and r[2] and str(tot) in r[3] and r[4]==1, f"④ 다트 9개 · 합계 {tot} · 결과 창 {r}")
        await pg.screenshot(path=OUTD+"dart_end.png")
        ok(not errs, f"오류 0 {errs[:5]}")
        await ctx.close()
        for nm,vp in [("pad",{"width":820,"height":1180}),("land",{"width":844,"height":390})]:
            ctx,pg,errs=await boot(br,"루아","BW638"+nm, vp=vp, isle=False); await enter(pg); await pg.screenshot(path=OUTD+nm+"_menu.png")
            await pg.evaluate("()=>{ MG.run.menuGo('bowl'); }"); await pg.evaluate(STEP, 6); await pg.wait_for_timeout(300); await pg.screenshot(path=OUTD+nm+"_bowl.png")
            r=await pg.evaluate("()=>{ const R=MG.run, c=MG.run.cam, w=innerWidth, h=innerHeight; const p=(x,y,z)=>{ const v=new THREE.Vector3(x,y,z).project(c); return [Math.round((v.x+1)/2*w), Math.round((1-v.y)/2*h)]; }; return [p(0,.2,0), p(0,.4,-10.3), p(-1.2,0,0), p(1.2,0,0), w, h]; }")
            ok(0<=r[0][1]<=r[5] and 0<=r[1][1]<=r[5] and r[1][1]<r[0][1], f"⑤ {nm}: 공 · 핀이 화면 안 {r}")
            await pg.evaluate("()=>{ MG.run.menuShow(); MG.run.menuGo('dart'); }"); await pg.evaluate(STEP, 6); await pg.wait_for_timeout(300); await pg.screenshot(path=OUTD+nm+"_dart.png")
            await ctx.close()
            ok(not errs, f"오류 0 ({nm}) {errs[:3]}")
        await br.close()
    print("BAD:", len(bad)); sys.exit(1 if bad else 0)
if __name__=="__main__": asyncio.run(main())
