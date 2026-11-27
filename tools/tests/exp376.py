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
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={"width": 390, "height": 844}, service_workers="block")   # (v738) 서비스 워커가 새로 고침을 받아 진짜 주소로 가져오다 끊김(ERR_ABORTED · 실험이 안 바뀜)
        await ctx.add_init_script("""window.HY_FB_LOCAL=true; window._aa=[]; let T; Object.defineProperty(window,'THREE',{configurable:true, get(){ return T; }, set(v){ T=v; const R=v.WebGLRenderer; v.WebGLRenderer=function(o){ window._aa.push(o && o.antialias); return new R(o); }; }});""")
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        async def run_end():
            await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); G.set='elem'; G.diff='normal'; G.rule='normal'; G.lesson=null; G.tag=null; startGame(); }")
            await pg.wait_for_timeout(1500)
            await pg.evaluate("()=>{ G.quit=true; G.skipOutro=true; gameOver(); }")
            try: await pg.wait_for_function("()=>{ const d=document.getElementById('perfBox'); return d && d.querySelectorAll('button').length>2; }", timeout=15000)
            except Exception: pass
            return await pg.evaluate("()=>{ const d=document.getElementById('perfBox'); return d ? d.innerText : ''; }")
        async def tap_reload(txt):
            """(v738) 진짜 손가락처럼 눌러 새로 고침 — evaluate 안에서 .click() 하면 그 자리에서 페이지가 바뀌어 기다림이 꼬였음 (가끔 실험이 안 바뀜)"""
            b = pg.locator("#perfBox button", has_text=txt).first
            await b.wait_for(state="visible", timeout=30000)
            await pg.evaluate("()=>{ window.__hyOld=1; }"); await b.click(no_wait_after=True)
            for _ in range(240):   # 옛 페이지 표시가 없어지고 새 페이지가 다 뜰 때까지 (expect_navigation 은 가끔 ERR_ABORTED 로 끊김)
                try:
                    if await pg.evaluate("()=>!window.__hyOld && document.readyState==='complete' && typeof startGame==='function'"): break
                except Exception: pass
                await pg.wait_for_timeout(250)
            await settle(pg, 900)
        await pg.route("**/*", route); await pg.goto(ORIGIN + "index.html?perf=1"); await settle(pg, 900)
        ok(await pg.evaluate("()=>window._aa") == [True], "보통은 계단 부드럽게 켬")
        rep = await run_end()
        ok("🧪 실험: 없음" in rep and "계단 부드럽게 끄고 다시" in rep and "소리 끄고 다시" in rep, "보고서에 실험 단추")
        await tap_reload("계단 부드럽게 끄고")
        ok(await pg.evaluate("()=>window._aa") == [False], "누르면 다시 열리며 계단 부드럽게 끔")
        rep = await run_end()
        ok("🧪 실험: 계단 부드럽게 끔" in rep and "계단 부드럽게 다시 켜기" in rep, "보고서에 지금 실험")
        await tap_reload("소리 끄고")
        r = await pg.evaluate("()=>[window._aa, Voice.on, SFX.on]"); ok(r == [[False], False, False], f"소리 끄기 실험 · 계단 실험도 그대로 {r}")
        rep = await run_end()
        ok("계단 부드럽게 끔 · 소리 끔" in rep, "두 실험 함께")
        await pg.evaluate("()=>[...document.querySelectorAll('#perfBox button')].find(b=>b.textContent==='측정 끄기').click()")
        await pg.goto(ORIGIN + "index.html"); await settle(pg, 900)
        r = await pg.evaluate("()=>[window._aa, Perf.on, Voice.on, SFX.on, localStorage.getItem('hyeng_exp')]"); print(r)
        ok(r == [[True], False, True, True, None], f"측정 끄면 모두 원래대로 {r}")
        e = real_errs(errs); ok(not e, "오류 없음 " + str(e[:3]))
        await br.close()
    print("결과:", "통과" if not bad else "실패 " + str(bad))
asyncio.run(main())
