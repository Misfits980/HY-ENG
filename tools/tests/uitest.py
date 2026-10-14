import asyncio, os, mimetypes, json
from playwright.async_api import async_playwright
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
SP=OUT
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); errs=[]
        pg=await br.new_page(viewport={"width":390,"height":844}, device_scale_factor=2, is_mobile=True, has_touch=True)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*",route); await pg.goto(ORIGIN+"index.html"); await pg.wait_for_timeout(2000); await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); }"); await pg.wait_for_timeout(500)
        await pg.screenshot(path=SP+"ui_menu.png")
        await pg.evaluate("()=>document.getElementById('btnGo').click()"); await pg.wait_for_timeout(500)
        await pg.screenshot(path=SP+"ui_mode.png")
        await pg.evaluate("()=>document.querySelector('#selRule [data-v=daily]').click()"); await pg.wait_for_timeout(400)
        await pg.evaluate("()=>document.querySelector('#selDiff [data-v=normal]').click()"); await pg.wait_for_timeout(400)
        await pg.evaluate("()=>document.querySelector('#selMode [data-v=mix]').click()"); await pg.wait_for_timeout(500)
        await pg.screenshot(path=SP+"ui_set.png")
        await pg.evaluate("()=>{ goStep(0); }"); await pg.wait_for_timeout(200); await pg.evaluate("()=>document.querySelector('#selRule [data-v=normal]').click()"); await pg.wait_for_timeout(300); await pg.evaluate("()=>goStep(2)"); await pg.wait_for_timeout(400); await pg.screenshot(path=SP+"ui_set_normal.png"); await pg.evaluate("()=>{ goStep(0); }"); await pg.wait_for_timeout(200); await pg.evaluate("()=>document.querySelector('#selRule [data-v=daily]').click()"); await pg.wait_for_timeout(300); await pg.evaluate("()=>goStep(2)"); await pg.wait_for_timeout(400)
        await pg.evaluate("()=>document.querySelector('#selCourse [data-v=basic]').click()"); await pg.wait_for_timeout(500)
        await pg.screenshot(path=SP+"ui_lesson.png")
        await pg.evaluate("()=>document.querySelector('#lessonChips [data-n=\"5\"]').click()"); await pg.wait_for_timeout(600)
        await pg.screenshot(path=SP+"ui_ready.png")
        r=await pg.evaluate("()=>({set:G.set, lesson:G.lesson, pool:pool().map(w=>w.en).join(' '), step})")
        print(json.dumps(r,ensure_ascii=False))
        await pg.evaluate("()=>document.getElementById('cNext').click()"); await pg.wait_for_timeout(400); await pg.screenshot(path=SP+"ui_ready2.png")
        for k in range(3): await pg.evaluate("()=>document.getElementById('cNext').click()")
        await pg.wait_for_timeout(400); await pg.screenshot(path=SP+"ui_ready3.png")
        print(await pg.evaluate("()=>({char:G.char, view:CharPick.view, step, start:document.getElementById('btnStart').textContent, rule:G.rule})"))
        print("errs",errs[:5]); await br.close()
asyncio.run(main())
