import asyncio
from playwright.async_api import async_playwright
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch()
        pg=await br.new_page(viewport={"width":390,"height":844}, is_mobile=True, has_touch=True)
        await pg.route("**/*",route); await pg.goto(ORIGIN+"index.html"); await pg.wait_for_timeout(1500)
        print(await pg.evaluate("""()=>{ const out=[]; document.querySelectorAll('.screen *').forEach(e=>{ const cs=getComputedStyle(e); if(cs.position==='fixed') out.push((e.closest('.screen').id)+' > '+(e.id||e.className)); }); return out }"""))
        await br.close()
asyncio.run(main())
