import asyncio
from playwright.async_api import async_playwright
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); errs=[]; pg=await br.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*",route); await pg.goto(ORIGIN+"index.html"); await pg.wait_for_timeout(1000)
        await pg.evaluate("()=>{ StudyUI.open(); Voice.canListen=()=>true; }"); await pg.wait_for_timeout(2500)
        print(await pg.evaluate("""()=>{ Study.ctx('vowel2'); const L=Study.lessons('vowel2'), x=L.find(y=>Study.stageNo('vowel2',y.n)==='1-5'); const see=x.ws.find(w=>w.en==='see'); let bad=0;
          for(let i=0;i<300;i++){ const q=Study.stepQ(see,1,x.ws,'ee',x.ws,true); if(q.opts && q.opts.some(o=>o.en==='sea')) bad++; }
          Study.ctx('kinder'); const K=Study.lessons('kinder')[0]; let dragSame=0, dp=0; for(let i=0;i<300;i++){ const q=Study.stepQ(K.ws.find(w=>w.en==='mouth'),1,K.ws,null,K.ws,true); if(q.t==='drag'){ if(q.pic){ dp++; if(new Set(q.ws.map(w=>w.emoji)).size<q.ws.length) dragSame++; } } }
          Study.ctx('short'); let pic=0; const rat=Study.word('rat'); for(let i=0;i<200;i++){ if(Study.stepQ(rat,0,Study.lessons('short')[0].ws,'a',[],true).t==='pic') pic++; }
          return {seaWithSee:bad, dragPic:dp, dragSamePic:dragSame, ratPicQs:pic, homo:[Study.hasHomo('see'),Study.hasHomo('cat')]}; }"""))
        print('errs',errs); await br.close()
asyncio.run(main())
