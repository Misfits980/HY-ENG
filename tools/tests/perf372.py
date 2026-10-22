"""(v372) 사파리 앱 측정: 계산 0ms 인데 320ms 멈춤이 자주(48번) → 그 사이에 브라우저 쪽에서 일어난 일을 시각과 함께
  터치·손 뗌·주소창/화면 바뀜·스크롤·화면 가림·음성 말하기/소리 시작/끝/끊기·효과음·네트워크 → 끊김마다 「| 터치 +40」
  새 셰이더는 종류 이름까지 · 보고서에 음성 켬/끔"""
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
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={"width": 390, "height": 844}, has_touch=True)
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*", route); await pg.goto(ORIGIN + "index.html?perf=1"); await pg.wait_for_timeout(1500)
        await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); G.set='elem'; G.diff='normal'; G.rule='normal'; G.lesson=null; G.tag=null; startGame(); }")
        await pg.wait_for_timeout(2500)
        # 멈춘 사이에 터치·음성
        await pg.evaluate("""()=>new Promise(r=>requestAnimationFrame(()=>{ setTimeout(()=>{ Perf.ev('터치'); try{ speechSynthesis.speak(new SpeechSynthesisUtterance(' ')); }catch(e){}
            const t=performance.now(); while(performance.now()-t<150){} r(); }, 5); }))""")
        await pg.wait_for_timeout(1500)
        h = await pg.evaluate("()=>Perf.run.hit.filter(h=>h.dt>100).map(h=>h.ev)")
        print("hits", h)
        ok(h and any(any(x.startswith("터치 +") for x in e) and any(x.startswith("음성 말하기 +") for x in e) for e in h), f"멈춘 사이의 터치·음성이 시각과 함께 {h}")
        await pg.touchscreen.tap(30, 400); await pg.wait_for_timeout(200)
        ok(await pg.evaluate("()=>Perf.evs.some(e=>e.n==='터치') && Perf.evs.some(e=>e.n==='손 뗌')"), "진짜 터치도 적힘")
        await pg.evaluate("()=>{ G.quit=true; G.skipOutro=true; gameOver(); }"); await pg.wait_for_timeout(1200)
        rep = await pg.evaluate("()=>{ const d=document.getElementById('perfBox'); return d ? d.innerText : ''; }")
        print(rep)
        ok("큰 끊김 사이에 브라우저에서 일어난 일: " in rep and "터치 1" in rep and "| 터치 +" in rep and "음성 켬" in rep, "보고서에 사이에 일어난 일 · 음성 켬/끔")
        await pg.screenshot(path=OUT + "perf372.png")
        await pg.evaluate("()=>localStorage.removeItem('hyeng_perf')")
        e = real_errs(errs); ok(not e, "오류 없음 " + str(e[:3]))
        await br.close()
    print("결과:", "통과" if not bad else "실패 " + str(bad))
asyncio.run(main())
