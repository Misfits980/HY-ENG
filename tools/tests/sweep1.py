import asyncio, json, sys
from playwright.async_api import async_playwright
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
BOOK={'kinder':'k','abc':'k','short':'k','long':'k','digr':'k','vowel2':'k','sight':'k','basic':'g12','elem':'g34','g56':'g56','rd1':'g56','rd2':'g56','rd3':'g56','mv1':'mid','mid':'mid','phrase':'ph'}
CHK="""()=>{ const U=StudyUI,q=U.qs[U.i]; if(!q) return null; const txt=document.getElementById('stQ').innerText; const bad=[];
 if(/undefined|NaN|\\bnull\\b|\\[object/.test(txt)) bad.push('txt:'+txt.slice(0,80).replace(/\\n/g,'|'));
 if(q.opts && Array.isArray(q.opts) && q.t!=='ox'){ const keys=q.opts.map(o=>typeof o==='string'?o:(o&&(o.en||o.ko||o.txt))); if(new Set(keys).size!==keys.length) bad.push('dupopt:'+keys.join(','));
   if(keys.some(k=>!k)) bad.push('emptyopt'); }
 if(q.t==='intro' && !document.getElementById('stQ').innerText.trim()) bad.push('emptyintro');
 return bad.length? {t:q.t,en:q.w&&q.w.en,bad}: 0 }"""
async def main():
    only=sys.argv[1:] 
    async with async_playwright() as p:
        br=await p.chromium.launch()
        for st,bk in BOOK.items():
            if only and st not in only: continue
            errs=[]; pg=await br.new_page(viewport={"width":390,"height":844}, is_mobile=True, has_touch=True)
            pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append('C:'+m.text) if m.type=='error' else None)
            await pg.route("**/*",route); await pg.goto(ORIGIN+"index.html"); await pg.wait_for_timeout(1000)
            await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); StudyUI.open(); Voice.canListen=()=>true; }"); await pg.wait_for_timeout(1200)
            n=await pg.evaluate(f"()=>Study.lessons('{st}').length"); bads=[]; steps=0; incomplete=[]
            for i in range(n):
                try:
                    await pg.evaluate(f"()=>{{ const b=document.getElementById('stBack'); if(b&&document.getElementById('stDone').style.display==='none'&&StudyUI.qs&&StudyUI.qs.length) b.click(); StudyUI.book='{bk}'; StudyUI.set='{st}'; StudyUI.path(); StudyUI.start({i},false); }}")
                except Exception as e: bads.append((i,'start',str(e)[:100])); continue
                await pg.wait_for_timeout(60)
                done=False
                for s in range(500):
                    c=await pg.evaluate(CHK)
                    if c: bads.append((i,c))
                    if c is None: break
                    r=await pg.evaluate(SOLVE, s%7==3); steps+=1
                    if r=='drag': await pg.wait_for_timeout(420)
                    if await pg.evaluate("()=>document.getElementById('stDone').style.display!=='none'"): done=True; break
                if not done: incomplete.append(i)
            print(st, 'stages',n,'steps',steps,'bad',len(bads),'incomplete',incomplete,'errs',[e for e in errs if 'Failed to load' not in e and 'unknown error' not in e][:3]); 
            for b in bads[:6]: print('  ',b)
            await pg.close()
        await br.close()
asyncio.run(main())
