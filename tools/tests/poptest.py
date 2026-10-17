import asyncio
from playwright.async_api import async_playwright
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch()
        pg=await br.new_page(viewport={"width":390,"height":844}, is_mobile=True, has_touch=True)
        await pg.route("**/*",route); await pg.goto(ORIGIN+"index.html"); await pg.wait_for_timeout(1000)
        await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); const s=Study.load(); s.book='g56'; s.set='rd2'; Study.save(); StudyUI.open(); }"); await pg.wait_for_timeout(1200)
        await pg.evaluate("()=>{ document.getElementById('scStudy').scrollTop=1300; StudyUI.pop(13); }")
        print(await pg.evaluate("()=>{ const c=getComputedStyle(document.getElementById('scStudy')); return [c.transform,c.filter,c.contain,c.willChange,c.backdropFilter] }"))
        print(await pg.evaluate("()=>{ const e=document.getElementById('stPop'), r=e.getBoundingClientRect(), r2=e.firstChild.getBoundingClientRect(); let a=e, ch=[]; while(a){ const cs=getComputedStyle(a); if(cs.transform!=='none'||cs.filter!=='none'||cs.contain!=='none'||cs.willChange!=='auto') ch.push(a.id||a.className); a=a.parentElement; } return {r:[r.top,r.height], in:[r2.top,r2.height], ch, sc:document.getElementById('scStudy').scrollTop} }"))
        # (v322) 미션 완료 알림(기다려도 되는 알림)은 결과 화면이 떠 있는 동안 줄 서 있다가 닫히면 나온다 · 버튼 알림은 바로
        cnt="()=>document.querySelectorAll('#hyToast .hyT').length"
        await pg.evaluate("()=>{ StudyUI.close&&StudyUI.close(); show('scOver'); hyToast('🎯 미션 완료! test', 0, true); hyToast('이미 받았어요'); }"); await pg.wait_for_timeout(900)
        n1=await pg.evaluate(cnt); print('toasts on result screen', n1)
        if n1!=1: print("BAD 결과 화면 위에 미션 알림이 바로 나옴(또는 버튼 알림이 안 나옴)", n1)
        await pg.evaluate("()=>show('scStart')"); await pg.wait_for_timeout(900)
        n2=await pg.evaluate("()=>[...document.querySelectorAll('#hyToast .hyT')].some(e=>e.textContent.indexOf('미션 완료')>=0)"); print('queued toast after closing', n2)
        if not n2: print("BAD 결과 화면을 닫아도 줄 선 미션 알림이 안 나옴")
        await br.close()
asyncio.run(main())
