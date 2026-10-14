import asyncio
from playwright.async_api import async_playwright
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); errs=[]
        pg=await br.new_page(viewport={"width":390,"height":844}, is_mobile=True, has_touch=True)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*",route); await pg.goto(ORIGIN+"index.html"); await pg.wait_for_timeout(1200)
        await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); StudyUI.open(); StudyUI.book='mid'; StudyUI.set='mv1'; StudyUI.path(); Study.setLv && 0; }")
        for st,i in (('mv1',0),('g56',0),('basic',0),('elem',3)):
            await pg.evaluate(f"()=>{{ StudyUI.set='{st}'; const s=Study.load(); s.lv[Study.key('{st}',Study.lessons('{st}')[{i}].n)]=1; StudyUI.run({i}); }}"); await pg.wait_for_timeout(2500)
            print(st, await pg.evaluate("()=>({run:G.running, set:G.set, lesson:G.lesson, words:(G.words||[]).length, q:(typeof activeSet==='function' && activeSet() && activeSet().q) ? activeSet().q.word.en : null})"))
            await pg.evaluate("()=>{ gameOver(); }"); await pg.wait_for_timeout(800)
            await pg.evaluate("()=>{ const b=document.getElementById('btnMain'); if(b) b.click(); }"); await pg.wait_for_timeout(300)
        # news shows k item
        print('news', await pg.evaluate("()=>NEWS[0].id"))
        print('errs', errs[:5]); await br.close()
asyncio.run(main())
