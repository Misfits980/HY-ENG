"""(v437) 🏷 이름표는 가까이 가야 — 사용자: (마당 사진에 집·만들기·요리·가게·밭 동그라미) "가까이 가야 이름표가 뜨게 만들다"
  · 마당·마을·광산: 캐릭터 가까이(보통 2.4칸 · 연못·밭·가게·타워는 조금 더)만 보임 · 멀어지면 사라짐(부드럽게)
  · 처음 안내(👇)가 가리키는 이름표는 멀어도 보임(town407) · 집 안 🚪 나가기는 늘 보임"""
import asyncio, sys, os
os.environ["HY_REAL3D"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        pg = await br.new_page(viewport={"width": 1180, "height": 820}); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*", route); await pg.goto(ORIGIN + "proto/house.html"); await pg.wait_for_timeout(800)
        await pg.evaluate("()=>{ localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); localStorage.setItem('hyeng_proto_baitok','1'); }")
        await pg.reload(); await pg.wait_for_timeout(3000)
        E = pg.evaluate
        vis = "()=>[...document.querySelectorAll('#tls .tl')].filter(e=>e.style.display!=='none' && !e.classList.contains('far')).map(e=>e.dataset.k).sort().join()"
        r = await E(vis)
        ok("door" in r, f"집 안: 🚪 나가기 늘 보임 {r!r}")
        await E("()=>{ HOUSE.setWx(false); go('yard'); }"); await pg.wait_for_timeout(3000)
        async def at(x, z):
            await E(f"()=>{{ hero.g.position.set({x},0,{z}); dirty=true; }}"); await pg.wait_for_timeout(700)
            return await E(vis)
        r = await at(1.5, 3.6)
        ok("house" in r and "shop" not in r and "pond" not in r and "farm" not in r.split(","), f"문 앞: 🚪 집만 (가게·연못 안 보임) {r!r}")
        r = await at(6.5, 3.0)
        ok("shop" in r and "house" not in r, f"가게 가까이: 🏪 가게 보임 · 집 사라짐 {r!r}")
        r = await at(4.0, 3.2)
        ok("pot" in r and "bench" in r and "shop" not in r, f"냄비·제작대 사이: 🍳 요리 · 🛠 만들기 {r!r}")
        r = await at(7.5, 4.6)
        ok("pond" in r, f"연못 가까이: 🎣 낚시 {r!r}")
        await pg.screenshot(path=OUT + "label437_yard.png")
        r = await E("()=>{ const e=document.querySelector('#tls .tl[data-k=house]'); return [e.classList.contains('far'), getComputedStyle(e).pointerEvents]; }")
        ok(r[0] and r[1] == "none", f"먼 이름표는 눌리지도 않음 {r}")
        await br.close()
    real = real_errs(errs)
    ok(not real, f"오류 없음 {real[:3]}")
    print("DONE bad=%d" % len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
