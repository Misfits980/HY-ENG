import asyncio
from playwright.async_api import async_playwright
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
SP=OUT
VIS="(i)=>{ const d=document.querySelector('.stDot[data-s=\"rd2\"][data-i=\"'+i+'\"]'), r=d.getBoundingClientRect(); return [Math.round(r.top), innerHeight, d.textContent] }"
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); errs=[]
        pg=await br.new_page(viewport={"width":390,"height":844}, device_scale_factor=2, is_mobile=True, has_touch=True)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*",route); await pg.goto(ORIGIN+"index.html"); await pg.wait_for_timeout(1000)
        # stale pre-split resume record
        await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); const s=Study.load(); s.book='g56'; s.set='rd2'; Study.save(); localStorage.setItem(StudyUI.CUR, JSON.stringify({set:'rd2', n:1, i:0, done:0, total:30, at:Date.now(), qs:[{t:'intro',w:'xx'}]})); StudyUI.open(); }"); await pg.wait_for_timeout(1200)
        print('stale resume bar:', await pg.evaluate("()=>!!document.querySelector('.stResume')"))
        b=pg.locator('.stDot[data-s="rd2"][data-i="13"]'); await b.scroll_into_view_if_needed(); await b.tap(); await pg.wait_for_timeout(700)
        print('tapped', await pg.evaluate(VIS,13), 'popTop', await pg.evaluate("()=>Math.round(document.querySelector('.stPopIn').getBoundingClientRect().top)"))
        await pg.screenshot(path=SP+"tap2.png")
        await pg.locator('#stPop .stGo').tap(); await pg.wait_for_timeout(300)
        for k in range(5): await pg.evaluate(SOLVE, False); await pg.wait_for_timeout(30)
        await pg.locator('#stQuit').tap(); await pg.wait_for_timeout(700)
        print('after quit', await pg.evaluate(VIS,13)); await pg.screenshot(path=SP+"quit2.png")
        await pg.locator('.stResume').tap(); await pg.wait_for_timeout(300)
        for k in range(400):
            r=await pg.evaluate(SOLVE, False); await pg.wait_for_timeout(420 if r=='drag' else 15)
            if await pg.evaluate("()=>document.getElementById('stDone').style.display!=='none'"): break
        await pg.locator('#stBack').tap(); await pg.wait_for_timeout(700)
        print('after done', await pg.evaluate(VIS,13)); await pg.screenshot(path=SP+"done2.png")
        await pg.evaluate("()=>{ StudyUI.close(); StudyUI.open(); }"); await pg.wait_for_timeout(700)
        print('reopen', await pg.evaluate(VIS,13))
        print(errs); await br.close()
asyncio.run(main())
