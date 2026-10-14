import asyncio
from playwright.async_api import async_playwright
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
FAKE="""(()=>{ const et=new EventTarget(); et.controller={}; et.register=()=>Promise.resolve({update(){}}); Object.defineProperty(navigator,'serviceWorker',{value:et,configurable:true}); window.__loads=(+sessionStorage.getItem('L')||0)+1; sessionStorage.setItem('L',window.__loads); })()"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); errs=[]
        pg=await br.new_page(viewport={"width":390,"height":844}, is_mobile=True, has_touch=True)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.add_init_script(FAKE)
        await pg.route("**/*",route); await pg.goto(ORIGIN+"index.html"); await pg.wait_for_timeout(1200)
        L=lambda: pg.evaluate("()=>window.__loads")
        fire="()=>navigator.serviceWorker.dispatchEvent(new Event('controllerchange'))"
        await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); StudyUI.open(); StudyUI.start(0,false); }"); await pg.wait_for_timeout(300)
        await pg.evaluate(fire); await pg.wait_for_timeout(2500); print('in lesson -> loads', await L())
        for k in range(3): await pg.evaluate(SOLVE, False); await pg.wait_for_timeout(50)
        await pg.wait_for_timeout(2200); print('still in lesson ->', await L())
        await pg.evaluate("()=>document.getElementById('stQuit').click()"); await pg.wait_for_timeout(2600)
        print('back to path ->', await L())
        # run game case
        await pg.wait_for_timeout(500)
        await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); G.set='basic'; G.diff='normal'; G.rule='normal'; startGame(); }"); await pg.wait_for_timeout(1500)
        await pg.evaluate(fire); await pg.wait_for_timeout(2500); print('in run ->', await L(), await pg.evaluate("()=>G.running"))
        await pg.evaluate("()=>{ gameOver(); }"); await pg.wait_for_timeout(3000); print('result screen ->', await L())
        await pg.evaluate("()=>document.getElementById('btnMain').click()"); await pg.wait_for_timeout(2600); print('main menu ->', await L())
        print(errs[:3]); await br.close()
asyncio.run(main())
