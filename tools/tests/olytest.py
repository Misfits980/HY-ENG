import asyncio, json
from playwright.async_api import async_playwright
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
SP=OUT
BK={'basic':'g12','elem':'g34','g56':'g56','mv1':'mid','rd1':'g56'}
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); errs=[]
        pg=await br.new_page(viewport={"width":390,"height":844}, device_scale_factor=2, is_mobile=True, has_touch=True)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*",route); await pg.goto(ORIGIN+"index.html"); await pg.wait_for_timeout(1200)
        await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); StudyUI.FAST=0; StudyUI.open(); }"); await pg.wait_for_timeout(1500)
        for st in ['basic','elem','g56','mv1','rd1']:
            i=await pg.evaluate(f"()=>Study.lessons('{st}').findIndex(x=>x.fin)")
            await pg.evaluate(f"()=>{{ StudyUI.book='{BK[st]}'; StudyUI.set='{st}'; StudyUI.path(); StudyUI.pop({i}); }}"); await pg.wait_for_timeout(200)
            pop=await pg.evaluate("()=>document.getElementById('stPop').innerText.replace(/\\n/g,' | ')")
            if st=='basic': await pg.screenshot(path=SP+"oly_pop.png")
            await pg.evaluate(f"()=>{{ StudyUI.pop(null); StudyUI.start({i},false); }}"); await pg.wait_for_timeout(300)
            info=await pg.evaluate("()=>({oly:StudyUI.oly, n:StudyUI.qs.length, types:StudyUI.qs.map(q=>q.t+(q.opic?'*':'')+(q.noKo?'-':'')).join(' '), secs:[...new Set(StudyUI.qs.map(q=>q.sec))].join(',')})")
            print(st, pop[:120]); print('  ', info)
            if st in ('basic','mv1'): await pg.screenshot(path=SP+f"oly_intro_{st}.png")
            seen=set(); steps=0; wrongs=0
            for k in range(80):
                t=await pg.evaluate("()=>{ const q=StudyUI.qs[StudyUI.i]; return q? q.t+(q.opic?'*':'') : null }")
                if t is None: break
                if t not in seen and t!='intro':
                    seen.add(t); await pg.wait_for_timeout(1200); await pg.screenshot(path=SP+f"oly_{st}_{t.replace('*','P')}.png")
                if st=='g56' and k==3:   # let one time out
                    await pg.wait_for_timeout(9500); print('  timeout ->', await pg.evaluate("()=>document.getElementById('stFoot').innerText.replace(/\\n/g,' ')"))
                    await pg.screenshot(path=SP+"oly_timeout.png")
                    await pg.evaluate("()=>document.getElementById('stCheck').click()"); await pg.wait_for_timeout(100); continue
                wf = (st=='mv1' and k%2==1)
                await pg.evaluate(SOLVE, wf); steps+=1; await pg.wait_for_timeout(30)
                if wf: await pg.evaluate("()=>{ const b=document.getElementById('stCheck'); if(b && StudyUI.locked) b.click(); }")
                if await pg.evaluate("()=>document.getElementById('stDone').style.display!=='none'"): break
                if await pg.evaluate("()=>StudyUI.locked"): await pg.evaluate("()=>document.getElementById('stCheck').click()")
            await pg.wait_for_timeout(300)
            print('   done:', await pg.evaluate("()=>document.getElementById('stDoneIn').innerText.replace(/\\n+/g,' | ').slice(0,160)"), 'lv', await pg.evaluate(f"()=>Study.lv('{st}', Study.lessons('{st}')[{i}].n)"))
            if st in ('basic','mv1'): await pg.screenshot(path=SP+f"oly_done_{st}.png")
            await pg.evaluate("()=>document.getElementById('stBack').click()"); await pg.wait_for_timeout(300)
        print('errs', errs[:4]); await br.close()
asyncio.run(main())
