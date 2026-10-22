"""(v378) 사용자: 조이스틱 움직일 때 멈추는 것 같다 → 실험 단추 「조이스틱 가볍게」: 터치를 막지 않는(passive) 조이스틱 · 보통은 그대로"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

TOUCH = """(k)=>{ const c=document.getElementById('c'); const t=new Touch({identifier:7, target:c, clientX:200, clientY:700+(k==='touchmove'?10:0)});
  const ev=new TouchEvent(k, {touches:k==='touchend'?[]:[t], targetTouches:k==='touchend'?[]:[t], changedTouches:[t], bubbles:true, cancelable:true}); c.dispatchEvent(ev); return [ev.defaultPrevented, stick.id, Math.round(input.y*100)]; }"""
START = "()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); G.set='elem'; G.diff='normal'; G.rule='normal'; G.lesson=null; G.tag=null; startGame(); }"

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={"width": 390, "height": 844}, has_touch=True)
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)
        await pg.evaluate(START); await pg.wait_for_timeout(600)
        a = await pg.evaluate(TOUCH, "touchstart"); b = await pg.evaluate(TOUCH, "touchmove"); await pg.evaluate(TOUCH, "touchend")
        ok(a[0] and b[0] and a[1] == 7 and b[2] < 0, f"보통: 조이스틱이 터치를 막음 · 움직임 {a} {b}")
        await pg.goto(ORIGIN + "index.html?perf=1"); await pg.wait_for_timeout(1200)
        await pg.evaluate("()=>{ localStorage.setItem('hyeng_exp', JSON.stringify({pass:1})); }")
        await pg.goto(ORIGIN + "index.html"); await pg.wait_for_timeout(1500)
        await pg.evaluate(START); await pg.wait_for_timeout(600)
        a = await pg.evaluate(TOUCH, "touchstart"); b = await pg.evaluate(TOUCH, "touchmove"); await pg.evaluate(TOUCH, "touchend")
        ok(not a[0] and not b[0] and a[1] == 7 and b[2] < 0, f"실험: 막지 않아도 조이스틱은 그대로 움직임 {a} {b}")
        await pg.evaluate("()=>{ G.quit=true; G.skipOutro=true; gameOver(); }"); await pg.wait_for_timeout(1000)
        rep = await pg.evaluate("()=>document.getElementById('perfBox').innerText")
        ok("조이스틱 가볍게" in rep, "보고서에 실험 상태 · 단추")
        await pg.evaluate("()=>{ localStorage.removeItem('hyeng_perf'); localStorage.removeItem('hyeng_exp'); }")
        e = real_errs(errs); ok(not e, "오류 없음 " + str(e[:3]))
        await br.close()
    print("결과:", "통과" if not bad else "실패 " + str(bad))
asyncio.run(main())
