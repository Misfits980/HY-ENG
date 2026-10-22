"""(v373) 사파리 앱 320ms 멈춤 — 사이에 사건 없음 → 손가락을 누른 채였는지 · 손가락 움직임 소식이 언제 끊겼다 다시 왔는지
  보고서 맨 위에 🌐 브라우저 / 🏠 홈 화면 앱 · 버전 글씨 5번 빨리 누르면 측정기 켜기/끄기 (홈 화면 앱용)"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

TOUCH = """(k)=>{ const c=document.getElementById('c'); const t=new Touch({identifier:7, target:c, clientX:200, clientY:700});
  const ev=new TouchEvent(k, {touches:k==='touchend'?[]:[t], targetTouches:k==='touchend'?[]:[t], changedTouches:[t], bubbles:true, cancelable:true}); c.dispatchEvent(ev); }"""

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={"width": 390, "height": 844}, has_touch=True)
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await boot(pg)
        # 버전 글씨 5번 → 켜짐
        await pg.evaluate("()=>{ show('scStart'); }"); await pg.wait_for_timeout(300)
        await pg.evaluate("()=>{ const v=document.querySelector('#scStart .verTag'); for(let i=0;i<5;i++) v.click(); }")
        await pg.wait_for_timeout(2000)
        await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); }")
        ok(await pg.evaluate("()=>Perf.on"), "버전 글씨 5번 빨리 누르면 측정기 켜짐")
        await pg.evaluate("()=>{ G.set='elem'; G.diff='normal'; G.rule='normal'; G.lesson=null; G.tag=null; startGame(); }")
        await pg.wait_for_timeout(2000)
        await pg.evaluate(TOUCH, "touchstart")
        for i in range(5): await pg.evaluate(TOUCH, "touchmove"); await pg.wait_for_timeout(30)
        await pg.evaluate("()=>new Promise(r=>requestAnimationFrame(()=>{ const t=performance.now(); while(performance.now()-t<150){} r(); }))")
        for i in range(3): await pg.evaluate(TOUCH, "touchmove"); await pg.wait_for_timeout(30)
        await pg.evaluate(TOUCH, "touchend"); await pg.wait_for_timeout(800)
        h = await pg.evaluate("()=>Perf.run.hit.filter(h=>h.dt>100).map(h=>h.ev)")
        print("hits", h)
        ok(h and any("손가락 누른 채" in e and any(x.startswith("움직임 끝 ") for x in e) and any(x.startswith("움직임 다시 +") for x in e) for e in h), f"누른 채 · 움직임 끝/다시 {h}")
        await pg.evaluate("()=>{ G.quit=true; G.skipOutro=true; gameOver(); }"); await pg.wait_for_timeout(1200)
        rep = await pg.evaluate("()=>{ const d=document.getElementById('perfBox'); return d ? d.innerText : ''; }")
        print(rep[:900])
        ok(rep.startswith("📊") and "🌐 브라우저" in rep and "손가락 누른 채 1" in rep, "보고서: 브라우저/홈 화면 앱 · 누른 채 집계")
        # 다시 5번 → 꺼짐
        await pg.evaluate("()=>{ document.getElementById('perfBox').remove(); Perf.el=null; show('scStart'); }"); await pg.wait_for_timeout(300)
        await pg.evaluate("()=>{ const v=document.querySelector('#scStart .verTag'); for(let i=0;i<5;i++) v.click(); }")
        await pg.wait_for_timeout(2000)
        ok(await pg.evaluate("()=>!Perf.on && !localStorage.getItem('hyeng_perf')"), "다시 5번 → 꺼짐")
        e = real_errs(errs); ok(not e, "오류 없음 " + str(e[:3]))
        await br.close()
    print("결과:", "통과" if not bad else "실패 " + str(bad))
asyncio.run(main())
