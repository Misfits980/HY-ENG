import asyncio, json
from playwright.async_api import async_playwright
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
SP=OUT
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); errs=[]
        pg=await br.new_page(viewport={"width":390,"height":844}, device_scale_factor=2, is_mobile=True, has_touch=True)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        # old player: 300 opened words, layout v1
        await pg.add_init_script("""try{ if(!localStorage.getItem('seeded')){ localStorage.setItem('seeded','1'); localStorage.setItem('hyeng_study_v1', JSON.stringify({book:'g34', set:'elem', phv:2, spv:1})); } }catch(e){}""")
        await pg.route("**/*",route); await pg.goto(ORIGIN+"index.html"); await pg.wait_for_timeout(1200)
        await pg.evaluate("()=>{ const m=JSON.parse(localStorage.getItem('hyeng_dex_v1'))||{got:{},open:{}}; m.got=m.got||{}; m.open=m.open||{}; DEX_BASE.slice(0,400).forEach(w=>{ m.got[w.en]=1; m.open[w.en]=1; }); m.ov=1; m.seeded=1; delete m.lay; localStorage.setItem('hyeng_dex_v1', JSON.stringify(m)); }")
        await pg.reload(); await pg.wait_for_timeout(1500)
        g0=await pg.evaluate("()=>Wallet.gems()")
        info=await pg.evaluate("""()=>{ const A=Dex.albums(); const by={}; A.forEach(a=>{ (by[a.g]=by[a.g]||[]).push(a.name+'('+a.words.length+')'); });
           const n=A.reduce((s,a)=>s+a.words.length,0), uniq=new Set(); A.forEach(a=>a.words.forEach(w=>uniq.add(w.en)));
           return {by, n, uniq:uniq.size, base:new Set(DEX_BASE.map(w=>w.en)).size, gifts:Dex.gifts().length, lay:JSON.parse(localStorage.getItem('hyeng_dex_v1')).lay} }""")
        for g,v in info['by'].items(): print(g, len(v), ' '.join(v))
        print('total', info['n'], 'uniq', info['uniq'], 'base', info['base'], 'pending gifts after migration', info['gifts'], 'lay', info['lay'])
        await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); document.getElementById('btnDex').click(); }"); await pg.wait_for_timeout(700)
        print('gems before/after open', g0, await pg.evaluate("()=>Wallet.gems()"), 'grade', await pg.evaluate("()=>DexUI.g"))
        await pg.screenshot(path=SP+"shelf_g34.png")
        await pg.locator('#dexGr [data-g="k"]').tap(); await pg.wait_for_timeout(500); await pg.screenshot(path=SP+"shelf_k.png")
        await pg.locator('#dexShelf [data-a]').first.tap(); await pg.wait_for_timeout(500); await pg.screenshot(path=SP+"album_k.png")
        print('head', await pg.evaluate("()=>document.getElementById('dexHead').innerText.replace(/\\n/g,' | ')"), 'gr hidden', await pg.evaluate("()=>document.getElementById('dexGr').style.display"))
        await pg.evaluate("()=>document.querySelector('#dexHead [data-back]').click()"); await pg.wait_for_timeout(300)
        print('back grade', await pg.evaluate("()=>DexUI.g+' '+document.querySelector('#dexGr .on').innerText.replace(/\\n/g,' ')"))
        # detail tag + found
        await pg.evaluate("()=>{ DexDet.show('went', true); }"); await pg.wait_for_timeout(300)
        print('det', await pg.evaluate("()=>{ const t=document.querySelector('#dexDet .wTags'), f=document.querySelector('#dexDet .wFind'); return (t?t.innerText:'')+' || '+(f?f.innerText.replace(/\\n/g,' '):'') }"))
        # dexgo from study
        print('where went', await pg.evaluate("()=>{ const w=Dex.where('went'); return w.a.id }"))
        print(errs[:3]); await br.close()
asyncio.run(main())
