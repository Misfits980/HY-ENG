"""(v636) 🍉 과일 합치기 — 사용자 「그 게임 안에 랭킹 이번 주 · 이번 달 · 전체 — 형광판 같은 느낌으로」
   ① 놀이 섬 🍉 과일 가게(북쪽) · 누르면 시작 화면 = 📟 형광판(이번 주 · 이번 달 · 전체) + 과일 11단계 + ▶ 시작
   ② 서버에 있던 랭킹이 형광판에 점수 순으로 · 탭 누르면 바뀜 · 5초마다 저절로 넘어감
   ③ 자동 선수: 떨어뜨리기 → 같은 과일 합쳐짐 · 상자 밖으로 안 나감 · 숫자 깨짐 없음 · 선 위에 쌓이면 끝
   ④ 끝 → 결과 창 🪙 · 서버 3곳(주·달·전체)에 내 기록 · 형광판에 나 (NEW) · 더 낮은 점수는 안 덮어씀
   ⑤ 사진 폰 · 패드 · 가로"""
import asyncio, sys, os, json
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
import fakefb
from fakefb import fake
from draw635 import boot
from playwright.async_api import async_playwright
OUTD=OUT+"fruit636/"; os.makedirs(OUTD, exist_ok=True)

async def enter(pg):
    for _ in range(30):
        if not await pg.evaluate("()=>MG.on"): break
        await pg.wait_for_timeout(200)
    await pg.evaluate("()=>MG.lobby('fruit')")
    for _ in range(80):
        if await pg.evaluate("()=>!!(MG.on && MG.run && MG.run.ready)"): break
        await pg.wait_for_timeout(200)
    await pg.wait_for_timeout(700)

SANE = """()=>{ const R=MG.run, F=R.FR; let bad=0; R.B.forEach(b=>{ if(!isFinite(b.x)||!isFinite(b.y)||b.x<b.r-2||b.x>600-b.r+2||b.y>820-b.r+2||b.y<-200){ bad++; window._frBad=[b.x,b.y,b.r,b.vx,b.vy]; } }); R.B.forEach(b=>{ }); return [bad, R.B.length, R.maxLv, R.merges, R.drops, R.score, R.over]; }"""

async def main():
    bad=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        ctx,pg,errs=await boot(br,"루아","FR636A", vp={"width":900,"height":700})
        r=await pg.evaluate("()=>{ const L=[]; MG.labels(L); return [!!MG.SPOT.fruit, L.map(x=>x.k).sort().join(',')]; }")
        ok(r[0] and "mg_fruit" in r[1], f"① 과일 가게 자리 · 이름표 {r}")
        await pg.evaluate("()=>{ const g=MG.SPOT.fruit; HOUSE.setWx(false); TFAC.warp(g[0]+1.5, g[2]+9); yaw=yawTo=0; ISLE.CAM.zoom=2.3; ISLE.CAM.pitch=.42; ISLE.CAM.dragAt=performance.now()+1e6; }")
        await pg.wait_for_timeout(2500); await pg.screenshot(path=OUTD+"building.png")
        await ctx.close()
        ctx,pg,errs=await boot(br,"루아","FR636A", isle=False)
        # 서버 랭킹 미리 (주 · 달 · 전체)
        await pg.evaluate("""async ()=>{ const now=srvNow(), d=new Date(now+9*3600e3); const y=d.getUTCFullYear(), m=d.getUTCMonth()+1;
            const t=new Date(Date.UTC(y,d.getUTCMonth(),d.getUTCDate())), dn=(t.getUTCDay()+6)%7; t.setUTCDate(t.getUTCDate()-dn+3); const y1=new Date(Date.UTC(t.getUTCFullYear(),0,4)); const wk=1+Math.round(((t-y1)/864e5-3+((y1.getUTCDay()+6)%7))/7);
            const K={W:"frW"+t.getUTCFullYear()+String(wk).padStart(2,"0"), M:"frM"+y+String(m).padStart(2,"0"), A:"frA"};
            await NET.put("/hy/day/"+K.W, {X1:{n:"민수",s:420,at:1}, X2:{n:"지우",s:910,at:2}});
            await NET.put("/hy/day/"+K.M, {X1:{n:"민수",s:420,at:1}, X2:{n:"지우",s:910,at:2}, X3:{n:"하늘",s:1500,at:3}});
            await NET.put("/hy/day/"+K.A, {X1:{n:"민수",s:420,at:1}, X2:{n:"지우",s:910,at:2}, X3:{n:"하늘",s:1500,at:3}, X4:{n:"별님",s:99999,at:4}}); }""")
        await enter(pg)
        K=await pg.evaluate("()=>MG.run.keys()")
        r=await pg.evaluate("()=>{ const S=document.querySelector('#mgUI .frSt'); return [MG.run.phase, getComputedStyle(S).display, S.querySelectorAll('.frLed .tb button').length, [...S.querySelectorAll('.frLed .rw .n')].map(e=>e.textContent).join(','), S.querySelectorAll('.ch span').length, !!S.querySelector('.go'), S.querySelector('.mq span').textContent.slice(0,40)]; }")
        ok(r[0]=="title" and r[1]=="flex" and r[2]==3 and r[3]=="지우,민수" and r[4]==11 and r[5] and "1등" in r[6], f"① 시작 화면: 📟 형광판(탭 3 · 이번 주 지우>민수) · 과일 11 · ▶ 시작 · 흐르는 글 {r}")
        await pg.screenshot(path=OUTD+"title.png")
        await pg.evaluate("()=>document.querySelector('#mgUI .frSt .frLed .tb [data-t=A]').click()"); await pg.wait_for_timeout(150)
        r=await pg.evaluate("()=>[MG.run.tabK, [...document.querySelectorAll('#mgUI .frSt .frLed .rw .n')].map(e=>e.textContent).join(',')]")
        ok(r==["A","별님,하늘,지우,민수"], f"② 탭 「전체」 → 전체 순위 {r}")
        await pg.evaluate("()=>{ for(let i=0;i<18*20;i++) MG.step(.05,false); }")
        r=await pg.evaluate("()=>MG.run.tabK")
        ok(r!="A", f"② 가만히 두면 탭이 저절로 넘어감 {r}")
        # ③ 게임
        c0=await pg.evaluate("()=>TECO.coins()")
        await pg.evaluate("()=>document.querySelector('#mgUI .frSt .go').click()"); await pg.wait_for_timeout(300)
        r=await pg.evaluate("()=>[MG.run.phase, getComputedStyle(document.querySelector('#mgUI .frSt')).display, document.querySelectorAll('#mgUI .frR > .frLed .rw').length>0]")
        ok(r==["play","none",True], f"③ 시작 → 상자 · 게임 중에도 형광판 {r}")
        # 손으로 몇 개
        for x in (150, 300, 450, 300):
            await pg.evaluate("(x)=>{ MG.run.aim(x); MG.run.drop(); for(let i=0;i<40;i++) MG.step(1/60,false); }", x)
        r=await pg.evaluate(SANE)
        ok(r[0]==0 and r[4]==4 and r[1]>=1, f"③ 떨어뜨리기 4번 · 상자 안 {r}")
        await pg.wait_for_timeout(300); await pg.screenshot(path=OUTD+"play_start.png")
        await pg.evaluate("()=>{ MG.run.bot=true; MG.run.fast=true; for(let i=0;i<60*6;i++) MG.step(1/60,false); MG.run.bot=false; for(let i=0;i<60*4;i++) MG.step(1/60,false); }")
        r=await pg.evaluate("()=>{ const B=MG.run.B, p0=B.map(b=>[b.id,b.x,b.y]); for(let i=0;i<60;i++) MG.step(1/60,false); const B2=MG.run.B; let d=0,n=0; p0.forEach(([id,x,y])=>{ const b=B2.find(q=>q.id===id); if(b){ d+=Math.hypot(b.x-x,b.y-y); n++; } }); return [B2.length, Math.round(d/Math.max(1,n)*10)/10, MG.run.over]; }")
        ok(r[0]>=6 and r[1]<3, f"③ 쌓인 과일이 가만히 멈춤 (1초 동안 평균 움직임 {r[1]} / 600 · 과일 {r[0]})")
        await pg.evaluate("()=>{ MG.run.bot=true; MG.run.fast=true; }")
        worst=0; shot=False
        for it in range(400):
            r=await pg.evaluate("()=>{ for(let i=0;i<30;i++) MG.step(1/60,false); }")
            r=await pg.evaluate(SANE); worst=max(worst, r[0])
            if not shot and r[1]>=18: await pg.screenshot(path=OUTD+"play_mid.png"); shot=True
            if r[6]: break
        ok(worst==0 and r[3]>=10 and r[2]>=4 and r[6], f"③ 자동: 합쳐짐 · 큰 과일까지 · 상자 밖 0 · 숫자 깨짐 0 · 선 넘으면 끝 [밖 {worst}, 과일 {r[1]}, 최대 {r[2]}, 합침 {r[3]}, 떨굼 {r[4]}, 점수 {r[5]}]")
        sc=r[5]; print("bad sample", await pg.evaluate("()=>window._frBad||null"))
        await pg.screenshot(path=OUTD+"play_over.png")
        await pg.wait_for_timeout(1200)
        r=await pg.evaluate("()=>{ const el=document.getElementById('mgRes'); return [el&&el.classList.contains('on'), el?el.querySelector('h3').textContent:'', TECO.coins(), MG.payLeft('fruit'), (store('hyeng_proto_frr')||{}).best]; }")
        ok(r[0] and str(f"{sc:,}") in r[1] and r[2]>c0 and r[3]==2 and r[4]==sc, f"④ 결과 창 · 🪙 · 하루 판 수 · 내 최고 {r}")
        await pg.screenshot(path=OUTD+"result.png")
        db=fakefb.DB["hy"]["day"]
        r=[(db.get(K[k],{}).get("FR636A") or {}).get("s") for k in "WMA"]
        ok(r==[sc,sc,sc], f"④ 서버 주·달·전체에 내 기록 {r}")
        # 형광판에 나 (NEW)
        await pg.evaluate("()=>document.querySelector('#mgRes').classList.remove('on')")
        await pg.evaluate("()=>MG.run.tab('W')"); await pg.wait_for_timeout(100)
        r=await pg.evaluate("()=>[...document.querySelectorAll('#mgUI .frR > .frLed .rw')].map(e=>(e.classList.contains('me')?'*':'')+e.querySelector('.n').textContent).join(',')")
        ok("*루아 NEW!" in r, f"④ 형광판에 내 이름 반짝 + NEW {r}")
        # 더 낮은 점수는 안 덮어씀
        await pg.evaluate("()=>{ MG.run.begin(); MG.run.gameOver(); }"); await pg.wait_for_timeout(600)
        r=[(db.get(K[k],{}).get("FR636A") or {}).get("s") for k in "WMA"]
        ok(r==[sc,sc,sc], f"④ 0점 판은 기록 안 덮음 {r}")
        ok(not errs, f"오류 0 {errs[:5]}")
        await ctx.close()
        for nm,vp in [("pad",{"width":820,"height":1180}),("land",{"width":844,"height":390})]:
            ctx,pg,errs=await boot(br,"루아","FR636"+nm, vp=vp, isle=False); await enter(pg); await pg.screenshot(path=OUTD+nm+"_title.png")
            await pg.evaluate("()=>document.querySelector('#mgUI .frSt .go').click()"); await pg.evaluate("()=>{ MG.run.bot=true; MG.run.fast=true; for(let i=0;i<60*12;i++) MG.step(1/60,false); MG.run.bot=false; }")
            await pg.wait_for_timeout(500); await pg.screenshot(path=OUTD+nm+"_play.png")
            r=await pg.evaluate("()=>{ const b=document.querySelector('#mgUI .frBox canvas').getBoundingClientRect(), l=document.querySelector('#mgUI .frR > .frLed').getBoundingClientRect(); return [Math.round(b.width), Math.round(b.height), Math.round(b.bottom), innerHeight, Math.round(l.bottom), Math.round(b.top), document.documentElement.scrollWidth<=innerWidth, Math.round(b.width/b.height*100)]; }")
            ok(r[0]>200 and r[2]<=r[3] and r[6] and abs(r[7]-73)<=2, f"⑤ {nm}: 상자 화면 안 · 비율 600:820 {r}")
            await ctx.close()
            ok(not errs, f"오류 0 ({nm}) {errs[:3]}")
        await br.close()
    print("BAD:", len(bad)); sys.exit(1 if bad else 0)
if __name__=="__main__": asyncio.run(main())
