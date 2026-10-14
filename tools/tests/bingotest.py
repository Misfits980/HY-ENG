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
        await pg.route("**/*",route)
        # old save: some got words (should become opened)
        await pg.add_init_script("""try{ if(!localStorage.getItem('hyeng_dex_v1')) localStorage.setItem('hyeng_dex_v1', JSON.stringify({got:{cat:1,dog:1,bird:1}, seeded:1})); }catch(e){}""")
        await pg.goto(ORIGIN+"index.html"); await pg.wait_for_timeout(1500)
        r0=await pg.evaluate("()=>({cat:Dex.opened('cat'), sealed:Dex.sealedCount()})")
        # collect first board of animal: all except one, via add (sealed)
        r=await pg.evaluate("""()=>{ const A=Dex.album('g12-animal'); const R=Dex.board(A,0); const pos=R.map(L=>L.map(w=>w.level).join('')).join(' ');
           R.forEach((L,r)=>L.forEach((w,c)=>{ Dex.add(w.en); })); return {pos, sealed:Dex.sealedCount(), gifts:Dex.gifts(A).length}; }""")
        await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); refreshResume(); }")
        badge=await pg.evaluate("()=>document.getElementById('dexBadge').textContent")
        await pg.evaluate("()=>{ DexUI.open(); DexUI.goAlbum('g12-animal'); }"); await pg.wait_for_timeout(500)
        await pg.screenshot(path=SP+"bingo_sealed.png")
        # open all cards answering correctly
        await pg.evaluate("()=>document.querySelector('[data-openall]').click()"); await pg.wait_for_timeout(1000)
        await pg.screenshot(path=SP+"card_open.png")
        n=0
        for i in range(30):
            ok=await pg.evaluate("()=>{ if(!document.getElementById('cOpen').classList.contains('on')) return false; const k=CardOpen.opts.findIndex(o=>o.en===CardOpen.cur.en); document.querySelector('.coOpts [data-k=\"'+k+'\"]').click(); return true; }")
            if not ok: break
            n+=1
            if n==1: await pg.wait_for_timeout(200); await pg.screenshot(path=SP+"card_answer.png")
            await pg.evaluate("()=>document.querySelector('[data-next]').click()"); await pg.wait_for_timeout(950)
        r2=await pg.evaluate("()=>{ const A=Dex.album('g12-animal'); return {opened:n=Dex.board(A,0).flat().filter(w=>Dex.opened(w.en)).length, gifts:Dex.gifts(A).map(g=>g.key+'='+g.gems), gems:Wallet.gems(), pts:Wallet.pts()}; }")
        await pg.wait_for_timeout(300); await pg.screenshot(path=SP+"bingo_gifts.png")
        await pg.evaluate("()=>DexUI.claimAll()"); await pg.wait_for_timeout(300)
        r3=await pg.evaluate("()=>({gems:Wallet.gems(), left:Dex.gifts(Dex.album('g12-animal')).length})")
        await pg.screenshot(path=SP+"bingo_done.png")
        print(r0, r, badge, "opened", n, r2, r3, errs[:3]); await br.close()
asyncio.run(main())
