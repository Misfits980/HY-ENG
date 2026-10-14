import asyncio
from playwright.async_api import async_playwright
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch()
        for vp in ({"width":360,"height":600},{"width":740,"height":360}):
            pg=await br.new_page(viewport=vp, is_mobile=True, has_touch=True)
            await pg.route("**/*",route); await pg.goto(ORIGIN+"index.html"); await pg.wait_for_timeout(1200)
            await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); }")
            st=await pg.evaluate("()=>{ const s=document.getElementById('scStart'); s.scrollTop=9999; const r=document.getElementById('btnFsHome').getBoundingClientRect(), v=document.getElementById('verTag').getBoundingClientRect(); return {sh:s.scrollHeight, ch:s.clientHeight, st:s.scrollTop, fs:[Math.round(r.top),Math.round(r.bottom)], ver:[Math.round(v.top),Math.round(v.bottom)]} }")
            await pg.evaluate("()=>{ const s=Study.load(); s.book='g56'; s.set='rd2'; Study.save(); StudyUI.open(); }"); await pg.wait_for_timeout(900)
            await pg.evaluate("()=>{ document.getElementById('scStudy').scrollTop=1500; StudyUI.start(13,false); }"); await pg.wait_for_timeout(300)
            res=[]
            for k in range(40):
                r=await pg.evaluate("()=>{ const s=document.getElementById('scStudy'), f=document.getElementById('stFoot').getBoundingClientRect(); return [s.scrollTop, s.scrollHeight-s.clientHeight, Math.round(f.bottom), innerHeight, StudyUI.qs[StudyUI.i].t] }")
                res.append(r)
                await pg.evaluate("()=>{ const s=document.getElementById('scStudy'); s.scrollTop=9999; }")
                r2=await pg.evaluate("()=>{ const s=document.getElementById('scStudy'), f=document.getElementById('stFoot').getBoundingClientRect(); return [s.scrollTop, Math.round(f.bottom)] }")
                if r2[0]>0: res[-1].append(('scrolled',r2))
                await pg.evaluate("()=>{ document.getElementById('scStudy').scrollTop=0; }")
                await pg.evaluate(SOLVE, False); await pg.wait_for_timeout(450)
            print(vp, 'start', st); 
            for r in res:
                if r[0]>0 or len(r)>5: print('  ', r)
            await pg.close()
        await br.close()
asyncio.run(main())
