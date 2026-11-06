# v582 ✏️ 문장 따라쓰기 📐 문법 (표시·문제+답안지) — data/sva.json
import asyncio, sys
sys.path.insert(0, "/home/claude/hy-eng/tools/tests")
from harness import *
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); errs=[]
        pg=await br.new_page(viewport={"width":1280,"height":1800}, device_scale_factor=1.5); pg.on("pageerror", lambda e: errs.append(str(e)[:300])); await boot(pg); E=pg.evaluate
        for st,gm in (("elem","show"),("elem","quiz"),("g56","show"),("mv1","show"),("mv1","quiz")):
            await E("(a)=>{ Paper.close(); Paper.open({set:a[0], mode:'ks'}); document.getElementById('ppGm').value=a[1]; Paper.make(); }", [st,gm]); await pg.wait_for_timeout(2500)
            info=await E("()=>[document.getElementById('ppInfo').textContent, document.querySelectorAll('#ppWrap .pp').length, document.querySelectorAll('#ppWrap .sg:not(.n)').length, getComputedStyle(document.querySelector('.ppKsO')).display]")
            print(st, gm, info)
            await E("()=>{ document.getElementById('ppWrap').style.zoom=1; }")
            await pg.locator("#ppWrap .pp").first.screenshot(path=f"/tmp/claude-0/sva582_{st}_{gm}.png")
            if gm=="quiz": await pg.locator("#ppWrap .pp.key").first.screenshot(path=f"/tmp/claude-0/sva582_{st}_key.png")
        print("errs", errs)
        await br.close()
asyncio.run(main())
