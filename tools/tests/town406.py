"""(v406) 🏡 My Town — 사용자: "Adventure · Daily 30 밑에 카테고리 만들어서 · 공지 없이 아이들이 스스로"
  ① 게임 시작 → 첫 화면 카드 3장 (Adventure · Daily 30 · 🏡 My Town 맛보기) · 폰·패드·작은 폰·가로에서 세 장 모두 화면 안
  ② My Town 누르면 proto/house.html 로 · 소식(NEWS)·공지에는 안 나옴"""
import asyncio, sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright
async def main():
    bad=[]; errs=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch()
        for vw in [{"width":390,"height":844},{"width":320,"height":568},{"width":820,"height":1180},{"width":844,"height":390}]:
            pg=await br.new_page(viewport=vw); pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)
            await pg.evaluate("()=>{ document.querySelectorAll('.sheet.on').forEach(s=>s.classList.remove('on')); }")
            await pg.evaluate("()=>{ show('scSetup'); goStep(0); }"); await pg.wait_for_timeout(500)
            r=await pg.evaluate("""()=>{ const L=[...document.querySelectorAll('#selRule .tile.card')]; return L.map(t=>{ const b=t.getBoundingClientRect(); return [t.dataset.v, Math.round(b.top), Math.round(b.bottom), Math.round(b.left), Math.round(b.right), getComputedStyle(t).backgroundImage.indexOf('world-town')>=0]; }); }""")
            vs=[x[0] for x in r]; inside=all(x[1]>=0 and x[2]<=vw["height"]+1 and x[3]>=0 and x[4]<=vw["width"]+1 for x in r)
            ok(vs==["normal","daily","town"] and inside and r[2][5], f"{vw['width']}×{vw['height']} 카드 3장 모두 화면 안 · 마을 그림 {r}")
            if vw["width"]==390:
                await pg.screenshot(path=OUT+"town_card.png")
                await pg.route("**/proto/house.html", lambda r: r.fulfill(status=200, content_type="text/html", body="<p>town</p>"))
                await pg.click('#selRule [data-v="town"]'); await pg.wait_for_timeout(1500)
                ok(pg.url.endswith("proto/house.html"), f"🏡 My Town → 생활 맛보기 {pg.url}")
            await pg.close()
        html=open(os.path.join(SITE,"index.html"),encoding="utf-8").read()
        news=re.findall(r"NEWS[^\n]{0,4000}", html)
        ok(not any("My Town" in n or "마을 생활" in n for n in news), "소식(NEWS)에는 안 알림 (아이들이 스스로)")
        e=real_errs(errs); ok(not e, "오류 없음 "+str(e[:2]))
        await br.close()
    print("DONE bad=%d"%len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
