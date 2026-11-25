"""(v731) 🎳 볼링 👫 친구랑 — 방 만들기 · 들어가기 · 같이 시작 · 옆 레인에 친구(이름 · 캐릭터) · 친구가 던진 공이 내 화면 옆 레인에서도 굴러감 · 점수가 두 화면에서 같음 · 결과에 친구 이름"""
import asyncio, sys, os, json
os.environ["HY_REAL3D"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from draw635 import boot
from playwright.async_api import async_playwright
ENTER = """async ()=>{ MG.lobby('bowl'); for(let i=0;i<80;i++){ if(MG.on && MG.run && MG.run.ready) break; await new Promise(r=>setTimeout(r,200)); } return !!MG.run; }"""

async def main():
    bad = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        cA, A, eA = await boot(br, "루아", "BC731A", isle=False); cB, B, eB = await boot(br, "별사탕", "BC731B", isle=False)
        P2 = [A, B]
        for x in P2: await x.evaluate(ENTER)
        await A.wait_for_timeout(500)
        async def steps(n=4, dt=.1):
            for _ in range(n):
                for x in P2: await x.evaluate("async (dt)=>{ MG.step(dt,false); await null; }", dt)
                await A.wait_for_timeout(40)
        r = await A.evaluate("()=>[...document.querySelectorAll('#mgUI .puM [data-sg]')].map(b=>b.dataset.sg).join(',')")
        ok(r.endswith(",co"), f"① 메뉴에 👫 친구 {r}")
        for x in P2: await x.evaluate("()=>{ document.querySelector('#mgUI .puM [data-sg=\"co\"]').click(); document.querySelector('#mgUI .puM [data-m=\"bowl\"]').click(); }")
        await steps(3)
        r = [await x.evaluate("()=>[!!MG.run.RM, MG.run.RM && MG.run.RM.phase, getComputedStyle(document.querySelector('#mgUI .mgRoomP')).display, getComputedStyle(document.querySelector('#mgUI .spSc')).display]") for x in P2]
        ok(all(q[0] and q[1] == "room" and q[2] != "none" and q[3] == "none" for q in r), f"① 볼링 → 방 고르기 화면 (점수판 숨김) {r}")
        await A.evaluate("()=>MG.run.RM.make()"); await steps(4)
        for _ in range(15):
            await B.evaluate("()=>MG.run.RM.list()"); await steps(2)
            if await B.evaluate("()=>document.querySelectorAll('#mgUI [data-j]').length"): break
        await B.evaluate("()=>document.querySelector('#mgUI [data-j]').click()")
        for _ in range(16):
            await steps(1)
            if await B.evaluate("()=>MG.run.RM.phase==='wait'"): break
        await steps(4)
        r = [await x.evaluate("()=>[MG.run.RM.phase, document.querySelectorAll('#mgUI .mgRoomP .pl span').length]") for x in P2]
        ok(all(q == ["wait", 2] for q in r), f"② 둘이 같은 방 {r}")
        await A.screenshot(path=OUT + "bowlco731_room.png")
        await A.evaluate("()=>document.querySelector('#mgUI [data-st]').click()"); await steps(4)
        for x in P2: await x.evaluate("()=>{ TWN8.test=(TWN8.test||0)+9000; }")
        for _ in range(40):
            await steps(2)
            r = [await x.evaluate("()=>{ const R=MG.run; return [R.CO, R.lanes.map(L=>L.on), R.lanes[1].nm, R.bw.ph]; }") for x in P2]
            if all(q[0] for q in r): break
        ok(all(q[0] and q[1] == [True, True, False] and q[3] == "aim" for q in r) and r[0][2] == "별사탕" and r[1][2] == "루아", f"③ 같이 시작: 왼쪽 레인 = 친구 이름 · 오른쪽 빈 레인 {r}")
        r = [await x.evaluate("()=>{ const sc=document.querySelector('#mgUI .spSc'); return [[...sc.querySelectorAll('.rw .nm')].map(e=>e.textContent).join(','), !!(MG.run.lanes[1].P && MG.run.lanes[1].P.g.visible)]; }") for x in P2]
        ok(r[0] == ["루아,별사탕", True] and r[1] == ["별사탕,루아", True], f"③ 점수판 두 줄 · 친구 캐릭터 {r}")
        # A 가 한 번 굴림 → B 화면 옆 레인에서도 굴러감
        await A.evaluate("()=>MG.run.throwBall(.1, 0, 11)")
        seen = False
        for _ in range(40):
            await steps(1)
            if await B.evaluate("()=>MG.run.lanes[1].ph==='roll'"): seen = True; break
        ok(seen, "④ A 가 던진 공이 B 화면 옆 레인에서 굴러감")
        await B.screenshot(path=OUT + "bowlco731_B_roll.png")
        # 끝까지 (둘 다 빠르게 · 아무렇게나)
        for x in P2: await x.evaluate("()=>{ MG.run.fast=true; }")
        AUTO = "()=>{ const R=MG.run; if(R.bw.ph==='aim' && Math.random()<.5) R.throwBall((Math.random()-.5)*.5,(Math.random()-.5)*.2,8+Math.random()*5); return !!document.querySelector('#mgUI .puR'); }"
        done = [False, False]
        for it in range(700):
            await steps(1)
            done = [await x.evaluate(AUTO) for x in P2]
            if all(done): break
        ok(all(done), f"⑤ 둘 다 끝 · 결과 ({it}걸음) {done}")
        r = [await x.evaluate("()=>{ const R=MG.run; return [R.bw.rolls.slice(), R.lanes[1].rolls.slice(), (document.querySelector('#mgUI .puR')||{}).textContent||'']; }") for x in P2]
        ok(r[0][0] == r[1][1] and r[1][0] == r[0][1], f"⑤ 점수가 두 화면에서 같음 A:{r[0][0]} = B가 본 A:{r[1][1]} · B:{r[1][0]} = A가 본 B:{r[0][1]}")
        ok("별사탕" in r[0][2] and "루아" in r[1][2] and "친구랑" in r[0][2], f"⑤ 결과에 친구 이름 · 👫 {r[0][2][:70]} | {r[1][2][:70]}")
        await A.evaluate("()=>MG.run.fast=false"); await A.wait_for_timeout(1200); await A.screenshot(path=OUT + "bowlco731_end.png")
        # ⑥ 「한 판 더」 = 다시 방 고르기 → 둘이 다시 시작 → 친구가 나가면 그 레인은 「나갔어요」 · 나는 끝까지
        for x in P2: await x.evaluate("()=>{ MG.run.fast=false; const b=[...document.querySelectorAll('#mgUI .puR button')].find(b=>b.textContent.includes('한 판')); b && b.click(); }")
        await A.wait_for_timeout(2500); await steps(3)
        r = [await x.evaluate("()=>!!(MG.run && MG.run.RM && MG.run.RM.phase==='room')") for x in P2]
        ok(all(r), f"⑥ 한 판 더 → 다시 방 고르기 {r}")
        await A.evaluate("()=>MG.run.RM.make()"); await steps(4)
        for _ in range(15):
            await B.evaluate("()=>MG.run.RM.list()"); await steps(2)
            if await B.evaluate("()=>document.querySelectorAll('#mgUI [data-j]').length"): break
        await B.evaluate("()=>document.querySelector('#mgUI [data-j]').click()")
        for _ in range(16):
            await steps(1)
            if await B.evaluate("()=>MG.run.RM.phase==='wait'"): break
        await steps(3); await A.evaluate("()=>document.querySelector('#mgUI [data-st]').click()"); await steps(4)
        for x in P2: await x.evaluate("()=>{ TWN8.test=(TWN8.test||0)+9000; }")
        for _ in range(40):
            await steps(2)
            if all([await x.evaluate("()=>MG.run.CO") for x in P2]): break
        eB2 = real_errs(eB); await cB.close(); P2[:] = [A]
        await A.evaluate("()=>{ TWN8.test=(TWN8.test||0)+11000; }")
        await steps(140, .1)
        r = await A.evaluate("()=>{ const L=MG.run.lanes[1], P=document.querySelector('#mgUI .spPop'); return [L.ph, L.left, P.textContent]; }")
        ok(r[0] == "done" and r[1] == 1 and "나갔어요" in r[2], f"⑥ 친구가 나가면 그 레인 끝 · 「나갔어요」 {r}")
        await A.evaluate("()=>{ MG.run.fast=true; }")
        for it in range(400):
            await steps(1)
            if await A.evaluate(AUTO): break
        r = await A.evaluate("()=>!!document.querySelector('#mgUI .puR')")
        ok(r, f"⑥ 나는 끝까지 · 결과 {r}")
        E1 = real_errs(eA) + eB2; ok(not E1, f"오류 없음 {E1[:3]}")
        await br.close()
    print("\nFAIL" if bad else "\nPASS", len(bad)); sys.exit(1 if bad else 0)

if __name__ == "__main__": asyncio.run(main())
