import asyncio, os, mimetypes, json
from playwright.async_api import async_playwright
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); pg=await br.new_page(); errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*",route); await pg.goto(ORIGIN+"index.html"); await pg.wait_for_timeout(1200)
        r=await pg.evaluate("""()=>{ const A=Dex.album('g12-food'); Wallet.pay('da-g12-food-20'); A.words.forEach(w=>Dex.add(w.en));
          const g=Dex.gifts(A).filter(x=>x.album); DexUI.open(); const badge=document.querySelector('[data-a="food"] .nb'); 
          // ★1 전부 → 황금 단어왕
          Dex.list(1).forEach(w=>Dex.add(w.en)); const gift=DexUI.gift().map(o=>o.id);
          return {albumGift:g.map(x=>x.key+'='+x.gems), badge:badge&&badge.textContent, gift, owns:Wallet.owns('scholar-gold'), animalGems:Dex.albumGems(Dex.album('g12-animal')), act3:Dex.albumGems(Dex.album('mid-act'))}; }""")
        print(json.dumps(r,ensure_ascii=False), errs[:3]); await br.close()
asyncio.run(main())
