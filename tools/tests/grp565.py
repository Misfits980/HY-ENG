"""(v565) 사용자 캡처: Daily 30 「③ 묶어서 기억해요」 카드에 China — 🔤 같은 첫소리 — chess <img class="emj" …> 코드가 글로 보임
   학원 PC·옛 패드는 EmojiFix 가 그림 글자(♟️)를 <img> 로 바꿔 두는데, 카드가 단어+그림을 한 글자로 묶어 esc 해서 생긴 것.
   → 그림은 따로(emoHtml) · 글로 보이는 '<img' 가 없어야 함"""
import asyncio, os, sys
from playwright.async_api import async_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *

async def main():
    bad = []
    def ok(c, m): print(("OK  " if c else "BAD ") + m); (None if c else bad.append(m))
    async with async_playwright() as p:
        br = await p.chromium.launch(); errs = []
        pg = await br.new_page(viewport={"width": 390, "height": 844})
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await boot(pg)
        await pg.evaluate("""()=>{ StudyUI.open(); StudyUI.book='g12'; StudyUI.set='basic'; StudyUI.path(); StudyUI.start(0,false); }""")
        await pg.wait_for_timeout(300)
        r = await pg.evaluate("""()=>{ const U=StudyUI, w=WORD_BANK.find(x=>x.en==='chess')||WORD_BANK[0];
            const img='<img class="emj" src="assets/emoji/265f.svg" alt="" draggable="false">';
            U.qs.splice(U.i, 0, {t:"intro", hd:"grp", w, ws:[w], x:{rows:[["China","🔤 같은 첫소리","chess",img],["either","↔ 반대말","neither (둘 다 아닌)"]]}});
            U.show(); const c=document.querySelector('.grpR span'); return [c ? c.innerText : '', !!(c && c.querySelector('img.emj')), document.querySelector('#scStudy').innerText.indexOf('<img')]; }""")
        ok(r[0].strip() == "chess" and r[1] and r[2] < 0, f"③ 같은 첫소리 = 'chess' + 그림 (코드 글자 없음) {r}")
        await pg.screenshot(path=OUT + "grp565.png")
        await br.close()
    ok(not errs, f"오류 없음 {errs[:2]}")
    print("\nFAIL" if bad else "\nPASS", len(bad)); sys.exit(1 if bad else 0)

asyncio.run(main())
