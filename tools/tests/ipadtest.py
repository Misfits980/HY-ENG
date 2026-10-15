"""(v271) 아이패드 — 철자 칸 글자를 누르면 그 글자부터 뒤까지 지움 · 세로/가로에서 Daily 30 탭이 다 보이고 위가 안 잘림 · 돌려도 캔버스가 화면을 채움"""
import asyncio, os, sys
from playwright.async_api import async_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *

async def main():
    bad = []
    async with async_playwright() as p:
        br = await p.chromium.launch(); errs = []
        pg = await br.new_page(viewport={"width": 768, "height": 954}, is_mobile=True, has_touch=True)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await boot(pg); await pg.wait_for_timeout(300)
        # 철자: 4글자 넣고 두 번째 글자를 누르면 1글자만 남는다
        await pg.evaluate("()=>{ StudyUI.open(); StudyUI.book='g56'; StudyUI.path(); StudyUI.start(0,false); }"); await pg.wait_for_timeout(300)
        for _ in range(200):
            t = await pg.evaluate("()=>{ const q=StudyUI.qs[StudyUI.i]; return q&&!StudyUI.locked&&!StudyUI._brk ? q.t : null }")
            if t == "spell": break
            await pg.evaluate(SOLVE, False); await pg.wait_for_timeout(450 if t == "drag" else 20)
        r = await pg.evaluate("""()=>{ const q=StudyUI.qs[StudyUI.i]; for(const c of q.w.en.slice(0,4)){ const b=[...document.querySelectorAll('.stTile')].find(x=>!x.disabled&&x.textContent===c); b.click(); }
            document.querySelector('#stSlots [data-sk="1"]').click();
            return {got:q.got, used:q.used.length, off:document.querySelectorAll('.stTile:disabled').length, want:q.w.en[0]} }""")
        print("spell tap", r)
        if not (r["got"] == r["want"] and r["used"] == 1 and r["off"] == 1): bad.append("철자 칸 누르기")
        await pg.evaluate("()=>document.getElementById('stQuit').click()"); await pg.wait_for_timeout(300)
        for (w, h) in [(768, 954), (1024, 698), (1180, 750)]:
            await pg.set_viewport_size({"width": w, "height": h}); await pg.wait_for_timeout(500)
            await pg.evaluate("()=>{ StudyUI.open(); StudyUI.book='g12'; StudyUI.path(); }"); await pg.wait_for_timeout(500)
            v = await pg.evaluate("""()=>{ const T=[...document.querySelectorAll('#stTabs .stCat')].map(b=>b.getBoundingClientRect()), top=document.getElementById('stClose').getBoundingClientRect();
                const c=document.getElementById('c').getBoundingClientRect();
                return {tabsIn: T.every(r=>r.left>=0 && r.right<=innerWidth+1), n:T.length, topVis: top.top>=0, canvas:[Math.round(c.width),Math.round(c.height)]} }""")
            print(w, h, v)
            if not (v["tabsIn"] and v["topVis"]): bad.append("Daily 30 %dx%d" % (w, h))
            if v["canvas"] != [w, h]: bad.append("캔버스 %dx%d" % (w, h))
        await pg.screenshot(path=OUT + "ipad_path_land.png")
        e = real_errs(errs); print("errs", e)
        if e: bad.append("errors")
        if bad: print("BAD", bad)
        await br.close()
asyncio.run(main())
