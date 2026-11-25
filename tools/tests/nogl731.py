"""(v731) 🖥 3D(WebGL)가 안 되는 브라우저 — 사용자: ChatGPT 에이전트 QA 화면
   「Uncaught Error: Error creating WebGL context.」 → 다시 시작도 같은 오류 · 계속하기 = 「모험 준비 중」에서 멈춤
   ① WebGL 을 끈 크롬으로 켜도 오류 창 없이 첫 화면 · 안내 카드 한 번 · Daily 30 열림
   ② ▶ START = 「3D 라서 못 해요」 카드 (달리기 안 켬)
   ③ My Town 카드 = 같은 카드 · house.html 을 바로 열어도 오류 없이 첫 화면으로 돌아와 안내
   ④ 보통 크롬(WebGL 있음)은 그대로 — 카드 없음 · NoGL.on false"""
import asyncio, sys, os, json
os.environ["HY_REAL3D"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright


async def main():
    bad = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(args=["--disable-webgl", "--disable-3d-apis"])
        ctx = await br.new_context(viewport={"width": 1363, "height": 936})
        pg = await ctx.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*", route)
        await pg.goto(ORIGIN + "index.html"); await pg.wait_for_timeout(5000)
        E = pg.evaluate
        r = await E("""()=>{ const vis=el=>!!el && getComputedStyle(el).display!=='none' && el.getBoundingClientRect().height>0;
            const card=document.getElementById('townMt');
            return {nogl:NoGL.on, why:NoGL.why, err:vis(document.getElementById('err')), errTxt:(document.body.innerText.match(/잠깐 문제가 생겼어요/)||[''])[0],
              card:card ? card.innerText.replace(/\\s+/g,' ') : '', start:vis(document.getElementById('btnStart')), noGLcls:document.body.classList.contains('noGL')}; }""")
        ok(r["nogl"] and "WebGL" in r["why"] and r["noGLcls"], f"① WebGL 없음을 알아챔 {r['why'][:60]!r}")
        ok(not r["errTxt"] and not r["err"], f"① 「앗, 잠깐 문제가 생겼어요」 오류 창 없음 {r['errTxt']!r}")
        ok("3D 그림을 그릴 수 없어요" in r["card"] and "Daily 30" in r["card"], f"① 안내 카드 한 번 {r['card'][:80]!r}")
        ok(not [e for e in errs if "WebGL" in e], f"① 페이지 오류 없음 {errs[:2]}")
        await pg.screenshot(path=OUT + "/nogl731_home.png")
        await E("()=>document.querySelector('#townMt [data-d]').click()"); await pg.wait_for_timeout(800)
        r = await E("()=>{ const s=document.getElementById('scStudy'); return !!s && s.classList.contains('on'); }")
        ok(r, "① 「📚 Daily 30 하러 가기」 → Daily 30 열림")
        await pg.screenshot(path=OUT + "/nogl731_study.png")
        await E("()=>{ try{ StudyUI.close(); }catch(e){} const m=document.getElementById('townMt'); if(m) m.remove(); }"); await pg.wait_for_timeout(400)
        # ② START
        await E("()=>{ G.running=false; startGame(); }"); await pg.wait_for_timeout(300)
        r = await E("()=>[!!document.getElementById('townMt') && /달리기는 3D/.test(document.getElementById('townMt').innerText), !!G.running]")
        ok(r == [True, False], f"② START = 「달리기는 3D 라서」 카드 · 달리기 안 켬 {r}")
        await E("()=>document.querySelector('#townMt [data-x]').click()")
        r = await E("()=>{ G.race={room:'x'}; let t=''; try{ startGame(); }catch(e){ t=e.message; } G.race=null; return t; }")
        ok(r == "NoGL", f"② 교실 배틀 경주는 오류로 넘겨 대신 화면(B.screen) {r!r}")
        await E("()=>{ const m=document.getElementById('townMt'); if(m) m.remove(); }")
        # ③ My Town
        await E("()=>{ const t=document.querySelector('#selRule [data-v=\"town\"]'); if(t) t.click(); }"); await pg.wait_for_timeout(400)
        r = await E("()=>{ const m=document.getElementById('townMt'); return [m ? m.innerText.replace(/\\s+/g,' ') : '', location.pathname]; }")
        ok("My Town 은 3D" in r[0] and r[1].endswith("index.html"), f"③ My Town 카드 = 안내 (마을로 안 넘어감) {r[0][:50]!r}")
        await E("()=>{ const m=document.getElementById('townMt'); if(m) m.remove(); localStorage.setItem('hyeng_town_ok', String(Study.today())); }")
        errs.clear()
        await pg.goto(ORIGIN + "proto/house.html"); await pg.wait_for_timeout(5000)
        r = await E("()=>{ const m=document.getElementById('townMt'); return [location.pathname, location.hash, m ? m.innerText.replace(/\\s+/g,' ') : '', /잠깐 문제가 생겼어요|마을이 멈췄어요/.test(document.body.innerText)]; }")
        ok(r[0].endswith("index.html") and r[1] == "" and "🏡 My Town 은 3D" in r[2] and not r[3], f"③ house.html 바로 열기 → 첫 화면 + 안내 · 오류 창 없음 {r[:2]} {r[2][:40]!r}")
        await pg.screenshot(path=OUT + "/nogl731_town.png")
        await br.close()

        # ④ 보통 크롬 (WebGL 있음 · swiftshader)
        br = await p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        pg = await (await br.new_context(viewport={"width": 820, "height": 1180})).new_page(); errs2 = []; pg.on("pageerror", lambda e: errs2.append(str(e)))
        await pg.route("**/*", route)
        await pg.goto(ORIGIN + "index.html"); await pg.wait_for_timeout(5000)
        r = await pg.evaluate("()=>[NoGL.on, !!document.getElementById('townMt') && /3D 그림/.test(document.getElementById('townMt').innerText), document.body.classList.contains('noGL'), !!(renderer && renderer.getContext && renderer.getContext().getParameter)]")
        ok(r[:3] == [False, False, False], f"④ WebGL 있는 기기 = 그대로 (안내 없음) {r}")
        ok(not real_errs(errs2), f"④ 오류 없음 {real_errs(errs2)[:2]}")
        await br.close()
    print("FAIL" if bad else "PASS", len(bad))
    sys.exit(1 if bad else 0)

asyncio.run(main())
