# v657 🏃 교실 배틀 = 달리기 경주 (TV 트랙 · 패드 띠) — 점수 배틀만 · 깃발 레이스는 예전 그대로
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
bad = []
def ok(c, m):
    print(("OK  " if c else "BAD ") + m)
    if not c: bad.append(m)
ANS = "(g)=>{ const q=Battle.q; if(!q||q.done) return -1; let i=q.ans!=null ? q.ans : q.opts.findIndex(o=>o.en===q.w.en); if(!g) i=(i+1)%q.opts.length; Battle.answer(i); return i; }"
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={"width": 1920, "height": 1080}); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        errs = []; H = await ctx.new_page(); H.on("pageerror", lambda e: errs.append("H " + str(e))); await boot(H)
        room = await H.evaluate("()=>Battle.host({set:'g56', from:0, to:2, dur:30, team:false, lbl:'G5-6'})"); K = []
        for i, (nm, vp) in enumerate([("민준", (390, 844)), ("서연", (375, 667)), ("지호", (820, 1180))]):
            k = await ctx.new_page(); k.on("pageerror", lambda e, n=nm: errs.append(n + " " + str(e))); await k.set_viewport_size({"width": vp[0], "height": vp[1]}); await boot(k)
            await k.evaluate(f"()=>{{ const k0=Kid.k.bind(Kid); Kid.k=b=>k0(b)+'@t{i}'; RaidJoin.open(); }}"); await k.wait_for_timeout(100)
            await k.evaluate(f"()=>{{ document.getElementById('rdRoomIn').value='{room}'; document.getElementById('rdNameIn').value='{nm}'; document.querySelector('[data-rj=go]').click(); }}"); await k.wait_for_timeout(400); await k.evaluate("()=>{ Battle.FAST=0; }"); K.append(k)
        await H.wait_for_timeout(400)
        ok(not await H.evaluate("()=>!!document.getElementById('btRace')") and not await K[0].evaluate("()=>!!document.getElementById('btStrip')"), "기다리는 중엔 예전 대기 화면 (트랙 없음)")
        await H.evaluate("()=>Battle.hostAct('start')"); await H.wait_for_function("()=>Battle.st().s==='run' && Battle.left()>0", timeout=9000); await H.wait_for_timeout(700)
        r = await H.evaluate("()=>[!!document.getElementById('btRace'), document.querySelectorAll('#brTrk .brR').length, document.getElementById('scRaid').classList.contains('brOn'), !!document.querySelector('#rdB .btBoard'), [...document.querySelectorAll('#brTrk .brR')].every(e=>e.querySelector('.btChr'))]")
        ok(r == [True, 3, True, False, True], f"TV: 트랙 · 아이마다 한 줄(캐릭터) · 예전 순위 막대는 숨김 {r}")
        x0 = await H.evaluate("()=>[...document.querySelectorAll('#brTrk .brR')].map(e=>parseFloat(e.style.left))")
        for _ in range(3):
            await K[0].wait_for_function("()=>Battle.q && !Battle.q.done && Date.now()>=Battle.lockTo", timeout=5000); await K[0].evaluate(ANS, True); await K[0].wait_for_timeout(450)
        st = await K[0].evaluate("()=>[!!document.getElementById('btStrip'), document.getElementById('bsRk').textContent, document.getElementById('bsPop').textContent, document.getElementById('bsGap').textContent]")
        ok(st[0] and st[1] == "1등" and st[2].startswith("+") and "1등으로" in st[3], f"패드: 달리기 띠 · 맞히면 +점수 · 1등 표시 {st}")
        await K[1].wait_for_function("()=>Battle.q && !Battle.q.done", timeout=5000); await K[1].evaluate(ANS, False); await K[1].wait_for_timeout(200)
        ok(await K[1].evaluate("()=>document.getElementById('bsM').classList.contains('oops')"), "패드: 틀리면 비틀 💦")
        await H.wait_for_timeout(900)
        r = await H.evaluate("()=>{ const L=[...document.querySelectorAll('#brTrk .brR')]; return [L.map(e=>parseFloat(e.style.left)), L.map(e=>e.querySelector('.brTag').textContent), L.map(e=>e.querySelector('.brPop').textContent), document.getElementById('brFeed').textContent]; }")
        i = next(j for j, t in enumerate(r[1]) if "민준" in t)
        ok(r[0][i] > x0[i] + 5 and r[1][i].startswith("1") and r[2][i].startswith("+") and all(x <= 87.01 for x in r[0]), f"TV: 맞힌 아이가 앞으로 · 이름표에 등수·점수 · +점수 {r[1]} {r[0]}")
        r = await K[1].evaluate("()=>{ const s=document.getElementById('scRaid'); return [s.scrollHeight-s.clientHeight, getComputedStyle(document.querySelector('.btLive')||document.body).display, document.getElementById('bsGap').textContent, document.getElementById('bsA').children.length>0]; }")
        ok(r[0] <= 2 and r[1] == "none" and "지호" in r[2] and "같은 점수" in r[2] and r[3], f"작은 휴대폰(375×667): 스크롤 없음 · 앞 친구가 보임 {r}")
        r = await K[2].evaluate("()=>{ const s=document.getElementById('scRaid'); return [s.scrollHeight-s.clientHeight, document.getElementById('btStrip').offsetHeight]; }"); ok(r[0] <= 2 and r[1] >= 150, f"패드: 스크롤 없음 · 띠 높이 {r}")
        await H.screenshot(path=OUT + "bt657_tv.png"); await K[0].screenshot(path=OUT + "bt657_kid.png")
        await H.evaluate("()=>Battle.hostAct('end')"); await H.wait_for_timeout(3600)
        r = await H.evaluate("()=>[!!document.getElementById('btRace'), document.getElementById('scRaid').classList.contains('brOn'), !!document.querySelector('.btPodium')]"); k = await K[0].evaluate("()=>[!!document.getElementById('btStrip'), Battle.ended]")
        ok(r == [False, False, True] and k == [False, True], f"끝나면 트랙을 걷고 예전 시상대 {r} {k}")
        await H.evaluate("()=>Battle.hostAct('again')"); await H.wait_for_timeout(800); await H.evaluate("()=>Battle.hostAct('start')"); await H.wait_for_function("()=>Battle.st().s==='run' && Battle.left()>0", timeout=9000); await H.wait_for_timeout(700)
        r = await H.evaluate("()=>[document.querySelectorAll('#brTrk .brR').length, [...document.querySelectorAll('#brTrk .brR')].map(e=>parseFloat(e.style.left))]"); ok(r[0] == 3 and all(abs(x - 15) < 0.1 for x in r[1]), f"한 판 더: 출발선에서 다시 {r}")
        await H.evaluate("()=>Battle.leave()"); await H.wait_for_timeout(300); ok(not await H.evaluate("()=>!!document.getElementById('btRace') || document.getElementById('scRaid').classList.contains('brOn')"), "닫으면 트랙도 사라짐")
        # 깃발 레이스는 그대로
        await H.evaluate("()=>Battle.host({set:'g56', from:0, to:2, dur:30, mode:'flag', team:true, lbl:'깃발'})"); await H.wait_for_timeout(500); await H.evaluate("()=>Battle.hostAct('start')"); await H.wait_for_timeout(5200)
        ok(not await H.evaluate("()=>!!document.getElementById('btRace')"), "🚩 깃발 레이스는 예전 화면 그대로")
        e = real_errs(errs); ok(not e, "오류 없음 " + str(e[:3])); await br.close()
    print("결과:", "통과" if not bad else "실패 " + str(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
