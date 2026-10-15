import asyncio, json
from playwright.async_api import async_playwright
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
SP=OUT
# SOLVE 는 harness 것을 쓴다 (새 문제 유형이 생겨도 한 곳만 고치면 됨)
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); errs=[]
        pg=await br.new_page(viewport={"width":390,"height":844}, device_scale_factor=2, is_mobile=True, has_touch=True)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*",route); await pg.goto(ORIGIN+"index.html"); await pg.wait_for_timeout(1500)
        await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); StudyUI.open(); }"); await pg.wait_for_timeout(1200)
        await pg.screenshot(path=SP+"s2_path.png")
        tabs=await pg.evaluate("()=>[...document.querySelectorAll('#stTabs button')].map(b=>b.textContent)")
        # book 2 lesson 1 at level 1 (to get sent/dict types) — set lv 2 for variety
        await pg.evaluate("()=>{ StudyUI.book='mid'; StudyUI.path(); Study.setLv('mid',Study.lessons('mid')[0].n,2); StudyUI.set='mid'; StudyUI.start(0,false); }"); await pg.wait_for_timeout(300)
        types=[]; shots=set()
        for step in range(200):
            t=await pg.evaluate("()=>{ const q=StudyUI.qs[StudyUI.i]; return q? q.t : null }")
            if not t: break
            if t not in shots and t in ("sent","dict","pic","spell"): shots.add(t); await pg.screenshot(path=SP+f"s2_{t}.png")
            r=await pg.evaluate(SOLVE, step in (2,3)); types.append(r)
            await pg.wait_for_timeout(450 if r=='drag' else 20)
            if await pg.evaluate("()=>document.getElementById('stDone').style.display!=='none'"): break
        await pg.wait_for_timeout(300); await pg.screenshot(path=SP+"s2_done.png")
        d=await pg.evaluate("()=>({lv:Study.lv('mid',Study.lessons('mid')[0].n), gems:Wallet.gems(), pts:Wallet.pts(), dex2:Dex.count(2), streak:Study.streak(), srs:Object.keys(Study.load().srs||{}).length, done:document.getElementById('stDoneIn').innerText.slice(0,200)})")
        print("tabs", tabs); print("types", sorted(set(types)), len(types)); print(json.dumps(d, ensure_ascii=False))
        # book1 kinder: pic type
        await pg.evaluate("()=>{ document.getElementById('stBack').click(); StudyUI.book='b1'; StudyUI.path(); StudyUI.set='kinder'; StudyUI.start(0,false); }"); await pg.wait_for_timeout(300)
        t2=[]
        for step in range(150):
            t=await pg.evaluate("()=>{ const q=StudyUI.qs[StudyUI.i]; return q? q.t : null }")
            if not t: break
            if t=="pic" and "pic" not in shots: shots.add("pic"); await pg.screenshot(path=SP+"s2_pic.png")
            r=await pg.evaluate(SOLVE, False); t2.append(r)
            if r=='drag': await pg.wait_for_timeout(450)
            if await pg.evaluate("()=>document.getElementById('stDone').style.display!=='none'"): break
        print("kinder types", sorted(set(t2)))
        # review: make srs due
        await pg.evaluate("()=>{ document.getElementById('stBack').click(); const s=Study.load(); Object.keys(s.srs).forEach(en=>{ s.srs[en][1]=0; }); Study.save(); StudyUI.path(); }"); await pg.wait_for_timeout(300)
        await pg.screenshot(path=SP+"s2_review_card.png")
        await pg.evaluate("()=>document.querySelector('[data-review]').click()"); await pg.wait_for_timeout(300)
        n=0
        for step in range(120):
            if await pg.evaluate("()=>document.getElementById('stDone').style.display!=='none'"): break
            r=await pg.evaluate(SOLVE, False); n+=1
            if r=='drag': await pg.wait_for_timeout(450)
        await pg.wait_for_timeout(300); await pg.screenshot(path=SP+"s2_review_done.png")
        print("review", n, await pg.evaluate("()=>({gems:Wallet.gems(), txt:document.getElementById('stDoneIn').innerText.slice(0,120)})"))
        print("errs", errs[:5]); await br.close()
asyncio.run(main())
