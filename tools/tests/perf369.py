"""(v369) 📊 프레임 측정기 — 아이폰 끊김을 실제 기기에서 재기
  ?perf=1 → 이 기기에 기억 · 달리는 동안 왼쪽 위 한 줄 · 판이 끝나면 보고서(가장 긴 끊김 10개 + 그때 같이 있던 일)
  일부러 멈추게 한 프레임이 끊김으로 잡히고 그 프레임의 일이 붙는지 · 측정 끄기 · 꺼져 있으면 아무것도 안 함"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

START = "()=>{ G.set='elem'; G.diff='normal'; G.rule='normal'; G.lesson=null; G.tag=null; startGame(); setInterval(()=>{ try{ const s=G.sets.find(s=>!s.judged); if(s&&s.q){ const g=s.gates.find(g=>g.lane===s.q.answer); if(g) P.x=g.root.position.x; } }catch(e){} }, 50); }"

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={"width": 390, "height": 844})
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        # 꺼져 있으면 아무것도 없음
        await boot(pg)
        await pg.evaluate(START); await pg.wait_for_timeout(2500)
        ok(await pg.evaluate("()=>[Perf.on, !!document.getElementById('perfBox')]") == [False, False], "기본은 꺼짐 · 화면에 없음")
        # ?perf=1 로 켜기 → 기억
        await pg.goto(ORIGIN + "index.html?perf=1"); await pg.wait_for_timeout(1500)
        await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); }")
        await pg.goto(ORIGIN + "index.html"); await pg.wait_for_timeout(1500)
        await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); }")
        ok(await pg.evaluate("()=>Perf.on"), "?perf=1 한 번이면 이 기기에 기억 (주소 없이 열어도 켜짐)")
        await pg.evaluate(START); await pg.wait_for_timeout(3000)
        # 일부러 멈춤 — 효과와 함께 120ms 막기
        await pg.evaluate("()=>new Promise(r=>requestAnimationFrame(()=>{ puff(0,0,0,0xffffff,3); const t=performance.now(); while(performance.now()-t<120){} r(); }))")
        await pg.wait_for_timeout(2500)
        live = await pg.evaluate("()=>{ const d=document.getElementById('perfBox'); return d ? d.textContent : ''; }")
        print("live", live)
        ok("fps" in live and "큰 끊김" in live, f"달리는 동안 왼쪽 위 한 줄 {live}")
        h = await pg.evaluate("()=>Perf.run && Perf.run.hit.filter(h=>h.dt>100).map(h=>Object.keys(h.tags))")
        print("hits", h)
        ok(h and any("먼지" in t for t in h), f"멈춘 순간이 큰 끊김으로 잡히고 그때 일(먼지)이 붙음 {h}")
        # 판 끝 → 보고서
        await pg.evaluate("()=>{ G.quit=true; G.skipOutro=true; gameOver(); }"); await pg.wait_for_timeout(1500)
        rep = await pg.evaluate("()=>{ const d=document.getElementById('perfBox'); return d ? d.innerText : ''; }")
        print(rep)
        ok("프레임 측정" in rep and "가장 긴 끊김" in rep and "먼지" in rep and "측정 끄기" in rep, "판이 끝나면 보고서")
        ok(await pg.evaluate("()=>!!localStorage.getItem('hyeng_perf_last')"), "보고서는 기기에 남음")
        await pg.screenshot(path=OUT + "perf369.png")
        await pg.evaluate("()=>[...document.querySelectorAll('#perfBox button')].find(b=>b.textContent==='측정 끄기').click()")
        ok(await pg.evaluate("()=>[Perf.on, localStorage.getItem('hyeng_perf'), !!document.getElementById('perfBox')]") == [False, None, False], "측정 끄기")
        e = real_errs(errs); ok(not e, "오류 없음 " + str(e[:3]))
        await br.close()
    print("결과:", "통과" if not bad else "실패 " + str(bad))
asyncio.run(main())
