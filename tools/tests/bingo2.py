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
        await pg.route("**/*",route); await pg.goto(ORIGIN+"index.html"); await pg.wait_for_timeout(1500)
        await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); }")
        # open: row 0 fully + diagonal except center, then open center via card → row? diag completes
        r=await pg.evaluate("""()=>{ const A=Dex.album('g12-food'), R=Dex.board(A,0);
           R[0].forEach(w=>Dex.add(w.en,true));                       // 가로 1줄
           [1,3,4].forEach(i=>Dex.add(R[i][i].en,true));              // 대각선 (가운데 빼고)
           Dex.add(R[2][2].en);                                       // 가운데는 뒤집힌 카드
           Dex.toggleTarget(R[4][0].en); return {center:R[2][2].en, tg:Dex.targets()}; }""")
        await pg.evaluate("()=>{ DexUI.open(); DexUI.goAlbum('g12-food'); }"); await pg.wait_for_timeout(400)
        m1=await pg.evaluate("()=>({msg:document.getElementById('dexMsg').textContent, gems:Wallet.gems(), lit:document.querySelectorAll('.dCard.lit').length})")
        await pg.screenshot(path=SP+"b2_before.png")
        await pg.evaluate("(en)=>CardOpen.start([en])", r['center']); await pg.wait_for_timeout(1000)
        await pg.evaluate("()=>{ const k=CardOpen.opts.findIndex(o=>o.en===CardOpen.cur.en); document.querySelector('.coOpts [data-k=\"'+k+'\"]').click(); }"); await pg.wait_for_timeout(300)
        await pg.screenshot(path=SP+"b2_card_bingo.png")
        cm=await pg.evaluate("()=>document.getElementById('coMsg').innerText")
        await pg.evaluate("()=>document.querySelector('[data-next]').click()"); await pg.wait_for_timeout(400)
        m2=await pg.evaluate("()=>({msg:document.getElementById('dexMsg').textContent, gems:Wallet.gems(), lit:document.querySelectorAll('.dCard.lit').length, flash:document.querySelectorAll('.dCard.flash').length, bn:document.querySelector('.dBn').textContent})")
        await pg.screenshot(path=SP+"b2_after.png")
        # target detail
        await pg.evaluate("()=>{ DexUI.a=null; DexUI.draw(); }"); await pg.wait_for_timeout(200); await pg.screenshot(path=SP+"b2_shelf.png")
        # ranking dex tab
        await pg.evaluate("()=>{ document.getElementById('shDex').classList.remove('on'); showRank('dex'); }"); await pg.wait_for_timeout(1500)
        rk=await pg.evaluate("()=>document.getElementById('rankList').innerText.slice(0,200)")
        await pg.screenshot(path=SP+"b2_rank.png")
        print(r, m1, cm.replace("\n"," "), m2, "rank:", rk.replace("\n"," | "), errs[:3]); await br.close()
asyncio.run(main())
