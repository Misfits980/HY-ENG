"""(v598) 사용자: 「물총아레나 애들끼리 같이 못하고 버그도 너무 많네」
   ① 같이 하기: A 방 만들기 → B·C 방 목록에서 들어감 · 「게임 시작」은 방장만 · 10초 세기
   ② 시작: 사람 3 + 봇 3 = 6 · 친구 모습·이름이 보이고 움직임이 따라감 · 봇은 방장이 움직이고 모두 같은 자리
   ③ A 가 B 를 맞힘 → B 화면에서 젖음 · 흠뻑 → A 가 다음 무기 · 소식이 C 에도 · B 가 봇을 맞힘 → 방장 화면 봇이 젖음
   ④ 뿅망치(마지막)로 잡으면 → 세 화면 모두 같은 우승자 결과"""
import asyncio, sys, os
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from fakefb import fake
from playwright.async_api import async_playwright

async def boot(br, nick, code):
    ctx=await br.new_context(viewport={"width":844,"height":390}, is_mobile=True, has_touch=True)
    pg=await ctx.new_page(); errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
    await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html?isle=1"); await pg.wait_for_timeout(300)
    await pg.evaluate("([n,c])=>{ localStorage.setItem('hyeng_proto_code', JSON.stringify(c)); localStorage.setItem('hyeng_nick', n); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); }", [nick, code])
    await pg.reload(); await pg.wait_for_timeout(2400)
    await pg.evaluate("()=>MG.enter('arena',{mode:'co', diff:'normal'})"); await pg.wait_for_timeout(1500)
    return ctx, pg, errs

async def steps(pgs, n=8, dt=.1):
    for _ in range(n):
        for pg in pgs: await pg.evaluate("(dt)=>{ MG.step(dt,false); }", dt)
        await pgs[0].wait_for_timeout(70)

async def main():
    bad=[]; allerr=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        cA,A,eA=await boot(br,"루아","AAAA2"); cB,B,eB=await boot(br,"민수","BBBB3"); cC,C,eC=await boot(br,"지우","CCCC4")
        P3=[A,B,C]
        r=await A.evaluate("()=>[MG.run.ACT.length, !!document.querySelector('#mgUI .mgRoomP [data-mk]')]")
        ok(r==[1,True], f"① 같이 하기 = 처음엔 방 목록(봇 없음) {r}")
        await A.evaluate("()=>document.querySelector('#mgUI .mgRoomP [data-mk]').click()"); await A.wait_for_timeout(500)
        for x in (B,C):
            for _ in range(12):
                await steps([x], 2, .8)
                r=await x.evaluate("()=>[...document.querySelectorAll('#mgUI .mgRoomP [data-j]')].map(b=>b.textContent)")
                if r: break
            ok(len(r)==1 and "루아" in r[0], f"① 방 목록에 「루아의 방」 {r}")
            await x.evaluate("()=>document.querySelector('#mgUI .mgRoomP [data-j]').click()"); await x.wait_for_timeout(600)
        await steps(P3, 8)
        r=[await x.evaluate("()=>[MG.run.NETR.phase, document.querySelectorAll('#mgUI .mgRoomP .pl span').length, !!document.querySelector('#mgUI .mgRoomP [data-st]')]") for x in P3]
        ok(all(q[0]=="wait" and q[1]==3 for q in r) and r[0][2] and not r[1][2] and not r[2][2], f"① 셋 다 대기방 · 3명 · 「게임 시작」은 방장만 {r}")
        await B.screenshot(path=OUT+"arena598_wait.png")
        await A.evaluate("()=>document.querySelector('#mgUI .mgRoomP [data-st]').click()"); await A.wait_for_timeout(400)
        await steps(P3, 5)
        r=[await x.evaluate("()=>[MG.run.NETR.phase, document.querySelector('#mgUI .mgRoomCnt').textContent]") for x in P3]
        ok(all(q[0]=="count" and q[1] in ("10","9","8","7") for q in r), f"① 방장이 시작 → 모두 10초 세기 {r}")
        for sh in (5200, 5300):
            for x in P3: await x.evaluate("(s)=>{ TWN8.test=(TWN8.test||0)+s; }", sh)
            await steps(P3, 6)
        # ② 6명
        r=[await x.evaluate("()=>{ const R=MG.run; return [R.NETR.phase, R.ACT.length, R.ACT.filter(a=>a.net).length, R.ACT.filter(a=>a.bot).length, R.ACT.filter(a=>a.bot && a.rb).length, Math.round(R.time.left)]; }") for x in P3]
        ok(all(q[0]=="play" and q[1]==6 and q[2]==2 and q[3]==3 for q in r) and r[0][4]==0 and r[1][4]==3, f"② 사람 3 + 봇 3 = 6 · 봇은 방장이 움직임 {r}")
        await B.evaluate("()=>{ const m=MG.run.me; m.p.set(3.5,0,21); m.yaw=1.2; }")
        await steps(P3, 12)
        r=await A.evaluate("()=>{ const a=MG.run.PEER['BBBB3']; return [a.nm, +a.p.x.toFixed(1), +a.p.z.toFixed(1), a.G.visible]; }")
        ok(r[0]=="민수" and abs(r[1]-3.5)<.4 and abs(r[2]-21)<.4 and r[3], f"② A 화면에 민수가 보이고 따라옴 {r}")
        r=await A.evaluate("()=>MG.run.ACT.filter(a=>a.bot).map(a=>[a.i,+a.p.x.toFixed(1),+a.p.z.toFixed(1)])")
        await steps(P3, 6, .0001)
        rb=await B.evaluate("()=>MG.run.ACT.filter(a=>a.bot).map(a=>[a.i,+a.p.x.toFixed(1),+a.p.z.toFixed(1)])")
        ok(len(rb)==3 and all(abs(x[1]-y[1])<2.5 and abs(x[2]-y[2])<2.5 for x,y in zip(r,rb)), f"② 봇 자리가 A·B 같음 {r} / {rb}")
        # ③ 맞히기
        await A.evaluate("()=>{ MG.run.D.dm=0; }")   # 시험: 봇이 사람을 적시지 않게 (방장 봇)
        await A.evaluate("()=>{ const R=MG.run; R.me.wi=0; R.hurt(R.PEER['BBBB3'], 55, R.me, 0, false, R.me.p.clone()); }")
        await steps(P3, 6, .02)
        r=await B.evaluate("()=>[Math.round(MG.run.me.soak), MG.run.me.alive]")
        ok(r[0]>=45 and r[1], f"③ A 가 쏨 → B 화면에서 젖음 {r}")
        await A.evaluate("()=>{ const R=MG.run; R.hurt(R.PEER['BBBB3'], 60, R.me, 0, false, R.me.p.clone()); }")
        await steps(P3, 6, .1); await steps(P3, 6, .1)
        r=[await B.evaluate("()=>[MG.run.me.alive, MG.run.me.deaths|0]"), await A.evaluate("()=>[MG.run.me.kills, MG.run.me.wi]"), await C.evaluate("()=>document.querySelector('#mgUI').innerText.includes('민수')")]
        ok(r[0][1]==1 and r[1]==[1,1] and r[2], f"③ B 흠뻑 → A 다음 무기(2단계) · C 에도 소식 {r}")
        r=await B.evaluate("()=>{ const R=MG.run, b=R.ACT.find(a=>a.bot && a.alive); b.prot=0; R.hurt(b, 40, R.me, 0, false, R.me.p.clone()); return b.i; }")
        await steps(P3, 6, .02)
        s=await A.evaluate("(i)=>Math.round(MG.run.ACT.find(a=>a.bot && a.i===i).soak)", r)
        ok(s>=30, f"③ B 가 봇을 맞힘 → 방장 화면 봇이 젖음 {s}")
        await steps(P3, 30, .1)
        await A.evaluate("()=>{ const R=MG.run, b=R.PEER['CCCC4']; R.me.p.set(0,0,10); R.me.yaw=Math.PI; }")
        await C.evaluate("()=>{ const R=MG.run; R.me.p.set(0,0,4); R.me.prot=0; }")
        await steps(P3, 12)
        await A.wait_for_timeout(600); await A.screenshot(path=OUT+"arena598_play.png")
        # ④ 우승
        await A.evaluate("()=>{ const R=MG.run; R.me.wi=R.WP.length-1; R.vmSet(R.me.wi); }")
        await steps(P3, 4)
        await A.evaluate("()=>{ const R=MG.run, c=R.PEER['CCCC4']; c.alive=true; R.hurt(c, 120, R.me, R.WP.length-1, false, R.me.p.clone()); }")
        await steps(P3, 12, .05)
        await A.wait_for_timeout(1800); await steps(P3, 4, .05); await A.wait_for_timeout(600)
        r=[await x.evaluate("()=>{ const el=document.getElementById('mgRes'); return [!!el && el.classList.contains('on'), el ? el.innerText.slice(0,80) : '']; }") for x in P3]
        ok(all(z[0] for z in r) and all("루아" in z[1] for z in r), f"④ 뿅망치로 잡음 → 세 화면 모두 결과 · 우승 루아 {r}")
        await C.screenshot(path=OUT+"arena598_result.png")
        allerr=eA+eB+eC
        await br.close()
    ok(not allerr, f"오류 없음 {allerr[:3]}")
    print("\nFAIL" if bad else "\nPASS", len(bad)); sys.exit(1 if bad else 0)

if __name__=="__main__": asyncio.run(main())
