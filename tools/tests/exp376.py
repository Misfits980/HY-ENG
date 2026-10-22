"""(v376) 측정 결과: 320ms 멈춤은 GC 도 아님(큰 정리 18번 중 멈춤 사이 0) · 멈춘 동안 손가락 소식도 막힘 → 브라우저 그리기(그래픽) 쪽 의심
  → 측정기 보고서에 실험 단추: 🧪 계단 부드럽게(안티에일리어싱) 끄고 다시 · 🧪 소리 끄고 다시 (이 기기만 · 측정 끄기 하면 모두 원래대로)"""
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
        await ctx.add_init_script("""window.HY_FB_LOCAL=true; window._aa=[]; let T; Object.defineProperty(window,'THREE',{configurable:true, get(){ return T; }, set(v){ T=v; const R=v.WebGLRenderer; v.WebGLRenderer=function(o){ window._aa.push(o && o.antialias); return new R(o); }; }});""")
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        async def run_end():
            await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); G.set='elem'; G.diff='normal'; G.rule='normal'; G.lesson=null; G.tag=null; startGame(); }")
            await pg.wait_for_timeout(1500)
            await pg.evaluate("()=>{ G.quit=true; G.skipOutro=true; gameOver(); }"); await pg.wait_for_timeout(1000)
            return await pg.evaluate("()=>{ const d=document.getElementById('perfBox'); return d ? d.innerText : ''; }")
        await pg.route("**/*", route); await pg.goto(ORIGIN + "index.html?perf=1"); await pg.wait_for_timeout(1500)
        ok(await pg.evaluate("()=>window._aa") == [True], "보통은 계단 부드럽게 켬")
        rep = await run_end()
        ok("🧪 실험: 없음" in rep and "계단 부드럽게 끄고 다시" in rep and "소리 끄고 다시" in rep, "보고서에 실험 단추")
        await pg.evaluate("()=>[...document.querySelectorAll('#perfBox button')].find(b=>b.textContent.indexOf('계단 부드럽게 끄고')>=0).click()")
        await pg.wait_for_timeout(2000)
        ok(await pg.evaluate("()=>window._aa") == [False], "누르면 다시 열리며 계단 부드럽게 끔")
        rep = await run_end()
        ok("🧪 실험: 계단 부드럽게 끔" in rep and "계단 부드럽게 다시 켜기" in rep, "보고서에 지금 실험")
        await pg.evaluate("()=>[...document.querySelectorAll('#perfBox button')].find(b=>b.textContent.indexOf('소리 끄고')>=0).click()")
        await pg.wait_for_timeout(2000)
        ok(await pg.evaluate("()=>[window._aa, Voice.on, SFX.on]") == [[False], False, False], "소리 끄기 실험 · 계단 실험도 그대로")
        rep = await run_end()
        ok("계단 부드럽게 끔 · 소리 끔" in rep, "두 실험 함께")
        await pg.evaluate("()=>[...document.querySelectorAll('#perfBox button')].find(b=>b.textContent==='측정 끄기').click()")
        await pg.goto(ORIGIN + "index.html"); await pg.wait_for_timeout(1500)
        r = await pg.evaluate("()=>[window._aa, Perf.on, Voice.on, SFX.on, localStorage.getItem('hyeng_exp')]"); print(r)
        ok(r == [[True], False, True, True, None], f"측정 끄면 모두 원래대로 {r}")
        e = real_errs(errs); ok(not e, "오류 없음 " + str(e[:3]))
        await br.close()
    print("결과:", "통과" if not bad else "실패 " + str(bad))
asyncio.run(main())
