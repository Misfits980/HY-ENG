import asyncio
from playwright.async_api import async_playwright
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch()
        pg=await br.new_page(viewport={"width":390,"height":844}, is_mobile=True, has_touch=True)
        await pg.route("**/*",route); await pg.goto(ORIGIN+"index.html"); await pg.wait_for_timeout(1000)
        await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); const s=Study.load(); s.book='g56'; s.set='rd2'; Study.save(); StudyUI.open(); }"); await pg.wait_for_timeout(1200)
        await pg.evaluate("()=>{ document.getElementById('scStudy').scrollTop=1300; StudyUI.pop(13); }")
        print(await pg.evaluate("()=>{ const c=getComputedStyle(document.getElementById('scStudy')); return [c.transform,c.filter,c.contain,c.willChange,c.backdropFilter] }"))
        print(await pg.evaluate("()=>{ const e=document.getElementById('stPop'), r=e.getBoundingClientRect(), r2=e.firstChild.getBoundingClientRect(); let a=e, ch=[]; while(a){ const cs=getComputedStyle(a); if(cs.transform!=='none'||cs.filter!=='none'||cs.contain!=='none'||cs.willChange!=='auto') ch.push(a.id||a.className); a=a.parentElement; } return {r:[r.top,r.height], in:[r2.top,r2.height], ch, sc:document.getElementById('scStudy').scrollTop} }"))
        await br.close()
asyncio.run(main())
