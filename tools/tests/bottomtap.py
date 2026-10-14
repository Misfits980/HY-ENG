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
        await pg.mouse.click(195,100); await pg.wait_for_timeout(300)
        print('closed', await pg.evaluate("()=>!document.getElementById('stPop').classList.contains('on')"))
        await pg.evaluate("()=>StudyUI.close()"); await pg.wait_for_timeout(500)
        print('hidden on start screen', await pg.evaluate("()=>{ StudyUI.pop(3); return getComputedStyle(document.getElementById('stPop')).display }"))
        print(errs); await br.close()
asyncio.run(main())
