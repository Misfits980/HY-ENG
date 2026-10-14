import asyncio, json
from playwright.async_api import async_playwright
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
SP=OUT
OLD={"lv":{"kinder-1":3,"kinder-2":1,"basic-101":2,"basic-1503":1,"elem-1601":3,"elem-3004":2,"g56-101":2,"mid-1":1,"short-11":2},
     "seen":{"head":1},"set":"basic","book":"g12","last":{"basic":302,"elem":1601,"kinder":2},"ran":{"basic-101":1,"elem-1601":1},"phv":2,"spv":1}
WAL={"gems":5,"owned":[],"paid":{"st-basic-101-1":1,"st-basic-101-2":1,"wc-elem-1604":1,"stt-elem-1601":1,"st-g56-101-1":1,"rv-1":1}}
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); errs=[]
        # fresh
        pg=await br.new_page(viewport={"width":390,"height":844}, device_scale_factor=2, is_mobile=True, has_touch=True)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*",route); await pg.goto(ORIGIN+"index.html"); await pg.wait_for_timeout(1200)
        r=await pg.evaluate("""()=>{ const o={}; ['kinder','basic','elem','g56','mv1','mid'].forEach(st=>{ const L=Study.lessons(st); o[st]=L.length+' | '+L.slice(0,2).map(x=>Study.stageNo(st,x.n)+':'+x.ws.slice(0,4).map(w=>w.en).join(',')+(x.title?'['+x.title+']':'')).join(' ; '); });
          const g=Study.lessons('g56'); o.g56b=g.filter(x=>x.n>=10000).length+' basic parts, generated '+g.filter(x=>x.n<10000).length+' first gen '+(g.find(x=>x.n<10000)||{}).n;
          o.fresh={set:Study.load().set, book:Study.load().book, gv:Study.load().gv};
          o.face=Study.lessons('mv1').map(x=>x.ws.find(w=>w.en==='face')).filter(Boolean).map(w=>w.ko+'/'+w.alt)[0];
          o.newWord=Study.word('sculpture'); o.dexG=Dex.where('sculpture').a.id+' '+Dex.where('head').a.id+' '+Dex.where('beard').a.id+' '+Dex.where('stranger').a.id+' '+Dex.where('cat').a.id+' '+Dex.where('ship').a.id;
          return o; }""")
        for k,v in r.items(): print(k, v)
        await pg.close()
        # old user migration
        pg=await br.new_page(viewport={"width":390,"height":844}, device_scale_factor=2, is_mobile=True, has_touch=True)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.add_init_script("try{ if(!sessionStorage.getItem('x')){ sessionStorage.setItem('x',1); localStorage.setItem('hyeng_study_v1', JSON.stringify(%s)); localStorage.setItem('hyeng_wallet_v1', JSON.stringify(%s)); localStorage.setItem('hyeng_study_cur_v1', JSON.stringify({set:'basic',n:101,i:2,qs:[{t:'intro',w:'beard'}],at:Date.now(),done:1,total:20})); } }catch(e){}" % (json.dumps(OLD), json.dumps(WAL)))
        await pg.route("**/*",route); await pg.goto(ORIGIN+"index.html"); await pg.wait_for_timeout(1200)
        await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); StudyUI.open(); }"); await pg.wait_for_timeout(800)
        r=await pg.evaluate("()=>{ const s=Study.load(); return {lv:s.lv, last:s.last, ran:s.ran, set:s.set, book:s.book, gv:s.gv, gvw:s.gvw, cur:localStorage.getItem('hyeng_study_cur_v1'), paid:Object.keys(JSON.parse(localStorage.getItem('hyeng_wallet_v1')).paid)} }")
        for k,v in r.items(): print('old', k, v)
        await pg.screenshot(path=SP+"mig_path.png")
        await pg.evaluate("()=>{ StudyUI.book='mid'; StudyUI.set='mv1'; StudyUI.path(); document.getElementById('scStudy').scrollTop=0; }"); await pg.wait_for_timeout(400)
        await pg.screenshot(path=SP+"mv1_path.png")
        print('errs', errs[:4]); await br.close()
asyncio.run(main())
