import asyncio, json
from playwright.async_api import async_playwright
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
SP=OUT

async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch()
        for name,vp,mob in (('m',{"width":360,"height":740},True),('pc',{"width":1280,"height":800},False)):
            errs=[]; pg=await br.new_page(viewport=vp, is_mobile=mob, has_touch=mob)
            pg.on("pageerror", lambda e: errs.append(str(e)))
            await pg.route("**/*",route); await pg.goto(ORIGIN+"index.html"); await pg.wait_for_timeout(1500)
            await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); }")
            run=None
            for b in ['btnDex','btnShop','btnVersus','btnStats','btnRankHome','btnNews','btnWords','btnHelp','btnGear']:
                try:
                    await pg.evaluate(f"()=>document.getElementById('{b}').click()"); await pg.wait_for_timeout(700)
                    ov=await pg.evaluate("()=>({w:document.documentElement.scrollWidth, iw:innerWidth})")
                    await pg.screenshot(path=SP+f"{name}_{b}.png")
                    if ov['w']>ov['iw']+2: print(name,b,'H-OVERFLOW',ov)
                    for c in ['btnDexClose','btnShopClose','btnStatsClose','btnHelpClose','btnSetClose','btnSetDone','btnRankBack','btnBack','btnAdminClose','btnSheetClose']:
                        await pg.evaluate(f"()=>{{ const e=document.getElementById('{c}'); if(e && e.offsetParent) e.click(); }}")
                    await pg.wait_for_timeout(200)
                except Exception as e: print(name,b,'FAIL',str(e)[:100])
            print(name,'errs',errs[:3]); await pg.close()
        await br.close()
asyncio.run(main())
