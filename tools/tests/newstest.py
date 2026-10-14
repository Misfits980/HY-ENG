import asyncio, os, mimetypes
from playwright.async_api import async_playwright
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); ctx=await br.new_context(viewport={"width":390,"height":844}, device_scale_factor=2); pg=await ctx.new_page()
        errs=[]; pg.on("pageerror",lambda e: errs.append(str(e)))
        await pg.route("**/*",route); await pg.goto(ORIGIN+"index.html"); await pg.wait_for_timeout(3000)
        on=lambda: pg.evaluate("()=>document.getElementById('shNews').classList.contains('on')")
        print("first load popup:", await on())
        await pg.screenshot(path=OUT+"n1.png")
        await pg.click("#btnNewsOk"); await pg.wait_for_timeout(200)
        print("closed:", not await on(), "dot:", await pg.evaluate("()=>getComputedStyle(document.getElementById('newsDot')).display"))
        await pg.reload(); await pg.wait_for_timeout(3000); print("second load popup:", await on())
        await pg.click("#btnNews"); await pg.wait_for_timeout(200); print("menu opens:", await on())
        await pg.click("#btnNewsOk")
        await pg.evaluate("()=>localStorage.removeItem('hyeng_news_seen')")
        await pg.goto(ORIGIN+"index.html?stage=50"); await pg.wait_for_timeout(3000); print("test mode popup:", await on())
        await pg.goto(ORIGIN+"index.html"); await pg.wait_for_timeout(3000)
        await pg.screenshot(path=OUT+"n_menu.png")
        print(errs or "no errors"); await br.close()
asyncio.run(main())
