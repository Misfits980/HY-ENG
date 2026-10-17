import asyncio
from playwright.async_api import async_playwright
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
SP=OUT
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); errs=[]
        pg=await br.new_page(viewport={"width":390,"height":844}, device_scale_factor=2, is_mobile=True, has_touch=True)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*",route); await pg.goto(ORIGIN+"index.html"); await pg.wait_for_timeout(1000)
        await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); const s=Study.load(); s.book='g56'; s.set='rd2'; Study.save(); StudyUI.open(); }"); await pg.wait_for_timeout(1200)
        # put node 9 near the bottom edge
        await pg.evaluate("()=>{ const d=document.querySelector('.stDot[data-i=\"9\"]'), s=document.getElementById('scStudy'); s.scrollTop += d.getBoundingClientRect().bottom - innerHeight + 20; }"); await pg.wait_for_timeout(200)
        await pg.locator('.stDot[data-i="9"]').tap(); await pg.wait_for_timeout(800)
        print(await pg.evaluate("()=>{ const d=document.querySelector('.stDot[data-i=\"9\"]').getBoundingClientRect(), p=document.querySelector('.stPopIn').getBoundingClientRect(); return [Math.round(d.bottom), Math.round(p.top)] }"))
        await pg.screenshot(path=SP+"bottomtap.png")
        isOn="()=>document.getElementById('stPop').classList.contains('on')"
        # (v322) 길 화면 빈 곳(위쪽 지도)을 누르면 닫혀야 한다 — 예전엔 닫히지 않았다
        what=await pg.evaluate("()=>{ const e=document.elementFromPoint(30,450); return e?(e.id||e.className):'' }")
        await pg.touchscreen.tap(30,450); await pg.wait_for_timeout(300)
        c1=not await pg.evaluate(isOn); print('closed (empty map tap)', what, c1)
        if not c1: print("BAD Stage 창이 빈 곳을 눌러도 안 닫힘")
        # (v322) ✕ 버튼
        await pg.locator('.stDot[data-i="9"]').tap(); await pg.wait_for_timeout(500)
        xb=await pg.evaluate("()=>{ const b=document.querySelector('.stPopX'); if(!b) return null; const r=b.getBoundingClientRect(); return [Math.round(r.width),Math.round(r.height)] }")
        print('x button', xb)
        if not xb or min(xb)<40: print("BAD Stage 창 ✕ 버튼이 없거나 40px 보다 작음", xb)
        else:
            await pg.locator('.stPopX').tap(); await pg.wait_for_timeout(300)
            c2=not await pg.evaluate(isOn); print('closed (x)', c2)
            if not c2: print("BAD ✕ 를 눌러도 Stage 창이 안 닫힘")
        # 다른 Stage 동그라미를 누르면 창이 바뀌어 열려 있어야 한다
        await pg.locator('.stDot[data-i="9"]').tap(); await pg.wait_for_timeout(400)
        await pg.locator('.stDot[data-i="8"]').tap(); await pg.wait_for_timeout(400)
        c3=await pg.evaluate(isOn); print('dot -> dot still open', c3)
        if not c3: print("BAD 다른 Stage 를 누르니 창이 닫힘")
        await pg.mouse.click(195,100); await pg.wait_for_timeout(300)
        c4=await pg.evaluate("()=>!document.getElementById('stPop').classList.contains('on')"); print('closed', c4)
        if not c4: print("BAD Stage 창이 위쪽을 눌러도 안 닫힘")
        await pg.evaluate("()=>StudyUI.close()"); await pg.wait_for_timeout(500)
        print('hidden on start screen', await pg.evaluate("()=>{ StudyUI.pop(3); return getComputedStyle(document.getElementById('stPop')).display }"))
        print(errs); await br.close()
asyncio.run(main())
