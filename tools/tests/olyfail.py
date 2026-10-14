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
        await pg.route("**/*",route); await pg.goto(ORIGIN+"index.html"); await pg.wait_for_timeout(1200)
        await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); StudyUI.open(); StudyUI.book='g34'; StudyUI.set='elem'; StudyUI.path(); StudyUI.start(Study.lessons('elem').findIndex(x=>x.fin), false); }"); await pg.wait_for_timeout(300)
        for k in range(80):
            if await pg.evaluate("()=>document.getElementById('stDone').style.display!=='none'"): break
            await pg.evaluate("""()=>{ const U=StudyUI, q=U.qs[U.i]; if(U.locked||q.t==='intro'){ document.getElementById('stCheck').click(); return; }
               const k=q.opts.findIndex(o=>o.en!==q.w.en); document.querySelector('.stOpt[data-k="'+k+'"]').click(); }"""); await pg.wait_for_timeout(20)
        print(await pg.evaluate("()=>document.getElementById('stDoneIn').innerText.replace(/\\n+/g,' | ').slice(0,300)"), await pg.evaluate("()=>Study.lv('elem', Study.lessons('elem').find(x=>x.fin).n)"))
        await pg.screenshot(path=SP+"oly_fail.png"); print(errs[:3]); await br.close()
asyncio.run(main())
