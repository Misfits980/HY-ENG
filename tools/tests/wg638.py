# v638 🎯 이번 주 내 목표 — 고르기 · 잠금 · DM.add 로 진행 · 보상 한 번 · 다음 주 초기화 · 5 화면 넘침 없음
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *

OUT = os.environ.get("HY_OUT", "/tmp/wg638_")
bad = []
def ok(c, m):
    print(("OK  " if c else "BAD ") + m)
    if not c: bad.append(m)

FIT = """()=>{ const d=document.querySelector('#dmView .rdJoinIn'); if(!d) return null; const r=d.getBoundingClientRect();
  return {sh:d.scrollHeight-d.clientHeight, top:r.top, bot:r.bottom, ih:innerHeight, w:document.documentElement.scrollWidth-innerWidth, box:!!d.querySelector('.wgBox')}; }"""

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True); errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await boot(pg)
        await pg.evaluate("()=>{ localStorage.removeItem(WeekGoal.key()); DM.view(); }"); await pg.wait_for_timeout(300)
        r = await pg.evaluate("()=>{ const b=document.querySelector('#dmView .wgBox'); return b && {pick:b.classList.contains('pick'), ok:b.querySelector('.wgOk').disabled, k:b.querySelectorAll('.wgK button').length}; }")
        ok(r and r["pick"] and r["ok"] and r["k"] == 3, f"처음엔 고르기 · 정하기 단추 잠김 {r}")
        await pg.click("#dmView [data-wg=k][data-k=les]"); await pg.click("#dmView [data-wg=lv][data-lv='0']")
        await pg.screenshot(path=OUT + "pick_ph.png")
        await pg.click("#dmView .wgOk"); await pg.wait_for_timeout(200)
        r = await pg.evaluate("()=>({s:WeekGoal.load(), t:document.querySelector('#dmView .wgBox').textContent, pick:!!document.querySelector('#dmView .wgBox.pick')})")
        ok(r["s"]["k"] == "les" and r["s"]["lv"] == 0 and not r["pick"] and "3" in r["t"], f"정하면 잠김 · Stage 3개 {r['s']} {r['t']}")
        # 잠긴 뒤 바꾸기 시도 → 안 바뀜
        await pg.evaluate("()=>{ WeekGoal.act({dataset:{wg:'k', k:'run'}}); WeekGoal.act({dataset:{wg:'ok'}}); }")
        ok(await pg.evaluate("()=>WeekGoal.load().k") == "les", "이번 주엔 못 바꿈")
        # 진행: 다른 종류는 안 셈 · les 3번이면 💎3 한 번
        g0 = await pg.evaluate("()=>Wallet.gems()")
        await pg.evaluate("()=>{ DM.add('q', 5); DM.add('run', 2); DM.add('les', 1); DM.add('les', 1); }")
        ok(await pg.evaluate("()=>WeekGoal.load().n") == 2, "다른 종류는 안 셈 · les 2")
        await pg.evaluate("()=>{ DM.add('les', 1); DM.add('les', 1); DM.add('les', 1); }"); await pg.wait_for_timeout(300)
        r = await pg.evaluate("()=>({s:WeekGoal.load(), g:Wallet.gems()})")
        ok(r["s"]["got"] == 1 and r["g"] - g0 == 3, f"달성 💎3 한 번만 {r['g']-g0} {r['s']}")
        # 저장 지워져도 같은 주엔 두 번 안 줌
        await pg.evaluate("()=>{ const s=WeekGoal.load(); s.got=0; s.n=2; WeekGoal.save(); DM.add('les', 1); }")
        ok(await pg.evaluate("()=>Wallet.gems()") - g0 == 3, "같은 주 두 번 보상 없음")
        await pg.evaluate("()=>{ DM.draw(); }"); await pg.wait_for_timeout(200)
        t = await pg.evaluate("()=>document.querySelector('#dmView .wgBox.ok') && document.querySelector('#dmView .wgBox').textContent")
        ok(t and "달성" in t, f"달성 표시 {t}")
        await pg.screenshot(path=OUT + "done_ph.png")
        # 다음 주 = 새로 고르기
        r = await pg.evaluate("()=>{ const k=WeekGoal.key(); const s=JSON.parse(localStorage.getItem(k)); s.wk='2020-01-06'; localStorage.setItem(k, JSON.stringify(s)); return WeekGoal.load(); }")
        ok(r["k"] is None and r["got"] == 0, f"다음 주 = 새로 {r}")
        # 월요일 계산
        wk = await pg.evaluate("()=>{ const w=WeekGoal.wk(); return [w, new Date(w+'T00:00:00Z').getUTCDay()]; }")
        ok(wk[1] == 1, f"주 시작 = 월요일 {wk}")
        e = real_errs(errs); ok(not e, f"오류 없음 {e[:3]}")
        await pg.close()
        for nm, vp in (("ph", (390, 844)), ("pad", (820, 1180)), ("tv", (1920, 1080)), ("phL", (915, 412)), ("padL", (1180, 820))):
            for st in ("pick", "run"):
                pg = await b.new_page(viewport={"width": vp[0], "height": vp[1]}, is_mobile=nm != "tv", has_touch=nm != "tv"); await boot(pg)
                await pg.evaluate("(st)=>{ localStorage.removeItem(WeekGoal.key()); if(st==='run'){ WeekGoal.act({dataset:{wg:'k',k:'q'}}); WeekGoal.act({dataset:{wg:'ok'}}); DM.add('q', 40); } DM.view(); }", st); await pg.wait_for_timeout(400)
                r = await pg.evaluate(FIT)
                ok(r and r["box"] and r["sh"] <= 2 and r["top"] >= 0 and r["bot"] <= r["ih"] + 1 and r["w"] <= 0, f"{nm} {st} 미션 창 안에 다 보임 {r}")
                await pg.screenshot(path=f"{OUT}{st}_{nm}.png")
                await pg.close()
        await b.close()
    print("PASS" if not bad else "FAIL", len(bad))
    if bad: sys.exit(1)

asyncio.run(main())
