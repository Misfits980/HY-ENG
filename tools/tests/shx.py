import asyncio
from playwright.async_api import async_playwright
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
SP=OUT
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); errs=[]
        for nm,vp,mob in (('m',{"width":390,"height":844},True),('pc',{"width":1280,"height":800},False)):
            pg=await br.new_page(viewport=vp, device_scale_factor=2 if mob else 1, is_mobile=mob, has_touch=mob)
            pg.on("pageerror", lambda e: errs.append(str(e)))
            await pg.route("**/*",route); await pg.goto(ORIGIN+"index.html"); await pg.wait_for_timeout(1300)
            await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); }")
            for b,sh in (('btnDex','shDex'),('btnShop','shShop'),('btnStats','shStats'),('btnHelp','shHelp')):
                await pg.evaluate(f"()=>document.getElementById('{b}').click()"); await pg.wait_for_timeout(600)
                if b=='btnDex':   # open an album (bingo board, long)
                    await pg.evaluate("()=>{ const a=document.querySelector('#dexShelf [data-a], #dexShelf button'); if(a) a.click(); }"); await pg.wait_for_timeout(500)
                await pg.evaluate(f"()=>{{ const s=document.querySelector('#{sh} .sheetIn'); s.scrollTop=99999; const l=s.querySelector('.dexL'); if(l) l.scrollTop=99999; }}"); await pg.wait_for_timeout(300)
                vis=await pg.evaluate(f"()=>{{ const x=document.querySelector('#{sh} .shX'); const r=x.getBoundingClientRect(); const e=document.elementFromPoint(r.left+r.width/2, r.top+r.height/2); return [Math.round(r.top),Math.round(r.right), e===x] }}")
                await pg.screenshot(path=SP+f"shx_{nm}_{b}.png")
                await pg.evaluate(f"()=>document.querySelector('#{sh} .shX').click()"); await pg.wait_for_timeout(400)
                print(nm,b,'x at',vis,'closed', await pg.evaluate(f"()=>!document.getElementById('{sh}').classList.contains('on')"))
            await pg.close()
        print(errs[:3]); await br.close()
asyncio.run(main())
