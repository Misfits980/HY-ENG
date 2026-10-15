"""(v272) Daily 30 — 틀리면 정답을 본 뒤 같은 문제를 바로 한 번 더(보기 다시 섞음) · 뒤에 또 나옴 · 진도/정답률은 그대로"""
import asyncio, os, sys
from playwright.async_api import async_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *

async def main():
    bad = []
    async with async_playwright() as p:
        br = await p.chromium.launch(); errs = []
        pg = await br.new_page(viewport={"width": 390, "height": 844})
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await boot(pg); await pg.wait_for_timeout(300)
        await pg.evaluate("()=>{ StudyUI.open(); StudyUI.book='g34'; StudyUI.path(); StudyUI.start(0,false); }"); await pg.wait_for_timeout(300)
        # 보기를 고르는 첫 문제까지
        for _ in range(60):
            t = await pg.evaluate("()=>{ const q=StudyUI.qs[StudyUI.i]; return q&&!StudyUI.locked&&!StudyUI._brk ? q.t : null }")
            if t in ("e2k", "k2e", "listen", "sent", "spell"): break
            await pg.evaluate(SOLVE, False); await pg.wait_for_timeout(450 if t == "drag" else 20)
        a = await pg.evaluate("()=>({i:StudyUI.i, n:StudyUI.qs.length, en:StudyUI.qs[StudyUI.i].w.en, t:StudyUI.qs[StudyUI.i].t, done:StudyUI.done})")
        await pg.evaluate(SOLVE, True); await pg.wait_for_timeout(100)
        msg = await pg.evaluate("()=>document.getElementById('stFoot').innerText")
        nx = await pg.evaluate("()=>{ const q=StudyUI.qs[StudyUI.i+1]; return {retry:!!q.retry, en:q.w.en, t:q.t} }")
        later = await pg.evaluate("(en)=>StudyUI.qs.slice(StudyUI.i+2).filter(q=>q.w&&q.w.en===en&&q.again&&!q.retry).length", a["en"])
        print("first", a, "| foot", msg.replace("\n", " / "), "| next", nx, "| later copies", later)
        if not (nx["retry"] and nx["en"] == a["en"]) or later < 1: bad.append("바로 다시 / 뒤에 또")
        await pg.evaluate("()=>document.getElementById('stCheck').click()"); await pg.wait_for_timeout(150)
        tag = await pg.evaluate("()=>document.querySelector('#stQ .stStep') ? document.querySelector('#stQ .stStep').innerText : ''")
        await pg.screenshot(path=OUT + "retry_q.png")
        d0 = await pg.evaluate("()=>[StudyUI.done, StudyUI.wrong, StudyUI.first]")
        await pg.evaluate(SOLVE, True); await pg.wait_for_timeout(100)   # SOLVE 는 again 문제를 맞게 푼다
        d1 = await pg.evaluate("()=>[StudyUI.done, StudyUI.wrong, StudyUI.first]")
        print("retry tag", tag, "| done/wrong/first", d0, "->", d1)
        await pg.screenshot(path=OUT + "retry_ok.png")
        if "한 번 더" not in tag or d0 != d1: bad.append("다시 푸는 문제가 진도에 들어감")
        # 끝까지 — 마지막에 정답률이 처음 틀린 1개만 반영
        for _ in range(400):
            if await pg.evaluate("()=>document.getElementById('stDone').style.display!=='none'"): break
            t = await pg.evaluate("()=>{ const q=StudyUI.qs[StudyUI.i]; return q&&q.t }")
            await pg.evaluate(SOLVE, False); await pg.wait_for_timeout(450 if t == "drag" else 20)
        f = await pg.evaluate("()=>({done:StudyUI.done, total:StudyUI.total, fw:StudyUI._fw, acc:StudyUI.acc1()})")
        print("end", f)
        if f["done"] != f["total"] or f["fw"] != 1: bad.append("끝 집계")
        e = real_errs(errs); print("errs", e)
        if e: bad.append("errors")
        if bad: print("BAD", bad)
        await br.close()
asyncio.run(main())
