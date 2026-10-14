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
        await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); StudyUI.open(); }"); await pg.wait_for_timeout(1500)
        await pg.evaluate("()=>{ StudyUI.book='g12'; StudyUI.set='basic'; StudyUI.path(); StudyUI.start(Study.lessons('basic').findIndex(x=>x.fin),false); const j=StudyUI.qs.findIndex(q=>q.t==='talk'); StudyUI.i=j; StudyUI.show(); }"); await pg.wait_for_timeout(800)
        await pg.screenshot(path=SP+"talk_q.png")
        await pg.evaluate("()=>{ const q=StudyUI.qs[StudyUI.i]; const k=q.opts.findIndex(o=>o.en===q.w.en); document.querySelector('.stOpt[data-k=\"'+k+'\"]').click(); }"); await pg.wait_for_timeout(300)
        await pg.screenshot(path=SP+"talk_ok.png")
        # dex talk tab
        await pg.evaluate("()=>{ document.getElementById('stQuit').click(); StudyUI.close(); Dex.add('foot',true); DexUI.open(); DexDet.show('foot',true); }"); await pg.wait_for_timeout(800)
        await pg.evaluate("()=>document.querySelector('[data-wt=\"t\"]').click()"); await pg.wait_for_timeout(400)
        await pg.screenshot(path=SP+"dex_talk.png")
        print('tabs', await pg.evaluate("()=>[...document.querySelectorAll('[data-wt]')].map(b=>b.textContent+(b.classList.contains('on')?'*':'')).join(' ')"))
        print(errs[:3]); await br.close()
asyncio.run(main())
