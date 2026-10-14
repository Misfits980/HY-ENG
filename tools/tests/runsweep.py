import asyncio, json
from playwright.async_api import async_playwright
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
KEEP="""()=>{ if(window.__k) return; window.__k=setInterval(()=>{ try{ if(!G.running) return; if(G.lives<G.maxLives) G.lives=G.maxLives; G.inv=5; const s=activeSet(); if(s&&s.gates&&s.q){ P.x=s.gates[s.q.answer].root.position.x; P.vx=0; } }catch(e){} },40); }"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); errs=[]
        pg=await br.new_page(viewport={"width":390,"height":844}, is_mobile=True, has_touch=True)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*",route); await pg.goto(ORIGIN+"index.html"); await pg.wait_for_timeout(1500)
        await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); }")
        info=await pg.evaluate("()=>({sets:Object.keys(WORD_SETS), diffs:Object.keys(DIFF), rules:Object.keys(RULES), chars:(typeof CHARS!=='undefined'?Object.keys(CHARS):[])})")
        print(info)
        await pg.evaluate(KEEP)
        n=0
        for st in info['sets']:
            for d in info['diffs']:
                for r in info['rules']:
                    if r=='daily' and d!='normal': continue
                    before=len(errs)
                    try:
                        await pg.evaluate(f"()=>{{ G.set='{st}'; G.diff='{d}'; G.rule='{r}'; G.lesson=null; G.tag=null; startGame(); }}")
                        await pg.wait_for_timeout(1800)
                        run=await pg.evaluate("()=>G.running")
                        await pg.evaluate("()=>{ try{ gameOver(); }catch(e){ throw e } }")
                        await pg.wait_for_timeout(200)
                        await pg.evaluate("()=>{ const b=document.getElementById('btnMain'); if(b) b.click(); }")
                    except Exception as e: errs.append(f'{st}/{d}/{r}: {str(e)[:150]}')
                    n+=1
                    if len(errs)>before: print('ERR',st,d,r,errs[before:before+2])
        print('runs',n,'errs',len(errs)); print(errs[:5]); await br.close()
asyncio.run(main())
