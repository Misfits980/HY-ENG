"""(v375) 홈 화면 앱에서도 320ms 멈춤 · 사이에 아무 사건 없음 → 자바스크립트 쓰레기 정리(GC) 때문인지 가리는 측정
  4초 넘게 붙잡았다 놓은 물건이 사라지면 「큰 정리(GC)」 · 끊김 사이에 있으면 「| 큰 정리(GC) +0」 · 보고서에 횟수"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={"width": 390, "height": 844})
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*", route); await pg.goto(ORIGIN + "index.html?perf=1"); await pg.wait_for_timeout(1500)
        await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); G.set='elem'; G.diff='normal'; G.rule='normal'; G.lesson=null; G.tag=null; startGame(); }")
        await pg.wait_for_timeout(7000)
        n0 = await pg.evaluate("()=>[Perf._gw.length, Perf.gcN]")
        print("weak", n0)
        # 큰 정리 + 멈춤
        await pg.evaluate("()=>new Promise(r=>requestAnimationFrame(()=>{ setTimeout(()=>{ Perf._gw.push({deref:()=>undefined}); const t=performance.now(); while(performance.now()-t<150){} r(); }, 3); }))")
        await pg.wait_for_timeout(800)
        h = await pg.evaluate("()=>Perf.run.hit.filter(h=>h.dt>100).map(h=>h.ev)")
        print("hits", h, await pg.evaluate("()=>[Perf.gcN, Perf.gcS]"))
        ok(h and any(any(x.startswith("큰 정리(GC) +") for x in e) for e in h), f"멈춘 사이의 큰 정리(GC)가 적힘 {h}")
        await pg.evaluate("()=>{ G.quit=true; G.skipOutro=true; gameOver(); }"); await pg.wait_for_timeout(1200)
        rep = await pg.evaluate("()=>{ const d=document.getElementById('perfBox'); return d ? d.innerText : ''; }")
        print(rep[:700])
        ok("큰 정리(GC) " in rep and "번 · 작은 정리" in rep, "보고서에 GC 횟수")
        await pg.evaluate("()=>localStorage.removeItem('hyeng_perf')")
        e = real_errs(errs); ok(not e, "오류 없음 " + str(e[:3]))
        await br.close()
    print("결과:", "통과" if not bad else "실패 " + str(bad))
asyncio.run(main())
