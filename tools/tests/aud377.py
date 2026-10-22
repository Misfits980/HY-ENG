"""(v377) 아이폰 실험 결과: 계단 부드럽게 끔 → 320ms 멈춤 그대로 · 소리까지 끔 → 사라짐 (큰 끊김 4, 최대 64ms)
  → 달리는 동안 들리지 않는 아주 작은 소리를 계속 틀어 소리 장치를 켠 채로 (판 끝나면 멈춤)
  · 실험 단추 추가: 영어 읽기만 끄기 · 효과음만 끄기 · 소리 붙잡기 끄기"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

START = "()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); G.set='elem'; G.diff='normal'; G.rule='normal'; G.lesson=null; G.tag=null; startGame(); }"

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"]); ctx = await br.new_context(viewport={"width": 390, "height": 844})
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)
        await pg.evaluate(START); await pg.wait_for_timeout(800)
        r = await pg.evaluate("()=>[!!SFX._ka, SFX.ctx && SFX.ctx.state, SFX._ka && SFX._ka.g.gain.value]")
        ok(r[0] and r[2] < 0.001, f"판 시작 → 들리지 않는 소리로 소리 장치 붙잡기 {r}")
        await pg.evaluate("()=>{ G.quit=true; G.skipOutro=true; gameOver(); }"); await pg.wait_for_timeout(300)
        ok(await pg.evaluate("()=>SFX._ka===null"), "판 끝 → 멈춤")
        await pg.evaluate(START); await pg.wait_for_timeout(500)
        ok(await pg.evaluate("()=>!!SFX._ka"), "다시 하기 → 다시 붙잡기")
        await pg.evaluate("()=>{ G.quit=true; G.skipOutro=true; gameOver(); SFX.on=false; }")
        await pg.evaluate(START); await pg.wait_for_timeout(300)
        ok(await pg.evaluate("()=>SFX._ka===null"), "효과음을 꺼 두면 붙잡지 않음")
        # 실험 단추
        await pg.goto(ORIGIN + "index.html?perf=1"); await pg.wait_for_timeout(1500)
        await pg.evaluate(START); await pg.wait_for_timeout(800)
        await pg.evaluate("()=>{ G.quit=true; G.skipOutro=true; gameOver(); }"); await pg.wait_for_timeout(1000)
        names = await pg.evaluate("()=>[...document.querySelectorAll('#perfBox button')].map(b=>b.textContent)")
        print(names)
        ok(all(any(k in n for n in names) for k in ["영어 읽기만 끄고", "효과음만 끄고", "소리 붙잡기(v377) 끄고"]), "실험 단추 3개 추가")
        for key, want in [("영어 읽기만 끄고", [False, True, True]), ("효과음만 끄고", [False, False, False]), ("소리 붙잡기(v377) 끄고", None)]:
            await pg.evaluate("(k)=>[...document.querySelectorAll('#perfBox button')].find(b=>b.textContent.indexOf(k)>=0).click()", key); await pg.wait_for_timeout(1800)
            await pg.evaluate(START); await pg.wait_for_timeout(600)
            r = await pg.evaluate("()=>[Voice.on, SFX.on, !!SFX._ka, JSON.parse(localStorage.getItem('hyeng_exp'))]")
            print(key, r)
            if want: ok(r[:3] == want, f"{key} → 읽기/효과음/붙잡기 {r}")
            await pg.evaluate("()=>{ G.quit=true; G.skipOutro=true; gameOver(); }"); await pg.wait_for_timeout(1000)
        rep = await pg.evaluate("()=>document.getElementById('perfBox').innerText")
        ok("영어 읽기 끔 · 효과음 끔 · 소리 붙잡기 끔" in rep, "보고서에 실험 상태")
        await pg.evaluate("()=>{ localStorage.removeItem('hyeng_perf'); localStorage.removeItem('hyeng_exp'); }")
        e = real_errs(errs); ok(not e, "오류 없음 " + str(e[:3]))
        await br.close()
    print("결과:", "통과" if not bad else "실패 " + str(bad))
asyncio.run(main())
