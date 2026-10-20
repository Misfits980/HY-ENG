"""(v357) 사용자 사진: G1-2 「👂 첫소리가 같은 단어는?」 인데 head 의 ea 에 밑줄 (G1-2 소리 강조) → 첫소리(h)에만 밑줄
  · 겹자음 첫소리(bl·st…)는 두 글자 · 다른 문제(뜻 고르기)는 예전처럼 소리 강조 그대로"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await br.new_page(viewport={"width": 820, "height": 1180})
        pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)
        await pg.evaluate("()=>{ StudyUI.open(); StudyUI.start(0,false); }"); await pg.wait_for_timeout(300)
        R = """(en)=>{ const U=StudyUI, q=Study._mk('sfs', en, 'basic'); if(!q) return null; U.les=Object.assign({}, U.les||{}, {hl:'g12'}); U.qs=[q]; U.i=0; U.locked=false; U.show();
            const e=document.querySelector('#stQ .stEn'); return [q.x.on, [...e.querySelectorAll('u')].map(u=>u.textContent), e.textContent.replace(/[🔊\\s]/g,'')]; }"""
        r = await pg.evaluate(R, "head")
        print("head", r)
        ok(r and r[1] == ["h"] and r[2] == "head", f"head: 첫소리 h 에만 밑줄 (ea 아님) {r}")
        await pg.screenshot(path=OUT + "sfs357.png")
        for en in ["black", "stop", "ship", "frog", "tree"]:
            r = await pg.evaluate(R, en)
            if r: ok(r[1] == [r[0]] and r[2] == en and en.startswith(r[0]), f"{en}: 밑줄 = 첫소리 {r}")
        # 뜻 문제는 소리 강조 그대로
        r = await pg.evaluate("""()=>{ const U=StudyUI, w=Study.word('head'); U.les=Object.assign({}, U.les||{}, {hl:'g12'}); return U.wd('head'); }""")
        ok("<u>ea</u>" in r, f"다른 문제의 소리 강조는 그대로 {r}")
        e = real_errs(errs); ok(not e, "오류 없음 " + str(e[:3]))
        await br.close()
    print("결과:", "통과" if not bad else "실패 " + str(bad))
asyncio.run(main())
