"""(v412~v413) My Town 단추·시트 다듬기 — 위 도구(친구·지도·도감 글자) · 돌리기는 방에서만 · 독 아이콘(이모지 없음) · 숨은 시트 그림자 없음 · 시트 머리 아이콘 · 창고 머리 한 줄 · ⏩ 시험용 숨김"""
import asyncio, sys, os
os.environ["HY_REAL3D"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "FAIL ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        ctx = await br.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*", route); await pg.goto(ORIGIN + "proto/house.html"); await pg.wait_for_timeout(800)
        await pg.evaluate("()=>{ Object.keys(localStorage).filter(k=>k.startsWith('hyeng_proto_')).forEach(k=>localStorage.removeItem(k)); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); }")
        await pg.reload(); await pg.wait_for_timeout(2500)
        E = pg.evaluate
        r = await E("()=>[...document.querySelectorAll('.tools .tool span')].map(e=>e.innerText).join(',')")
        ok(r == "친구,지도,도감", f"위 도구 글자 {r}")
        ok(await E("()=>document.querySelectorAll('[data-ic] svg.ic').length") >= 20, "아이콘 그림으로 바뀜")
        emo = await E("()=>[...document.querySelectorAll('.bar.bot .dk > i')].filter(i=>!i.querySelector('svg')).map(i=>i.textContent)")
        ok(emo == [], f"아래 독에 이모지 없음 {emo}")
        ok(await E("()=>document.getElementById('bCam').classList.contains('on')"), "방: 돌리기 보임")
        await E("()=>HOUSE.go('yard')"); await pg.wait_for_timeout(1500)
        ok(not await E("()=>document.getElementById('bCam').classList.contains('on')"), "마당: 돌리기 숨김")
        ok(await E("()=>document.querySelectorAll('#gYard .sep').length") == 1, "이동 | 할 일 구분선")
        ok(await E("()=>[...document.querySelectorAll('.sheet')].every(e=>getComputedStyle(e).visibility==='hidden')"), "숨은 시트 = 안 보임 (아래 그림자 얼룩 없음)")
        ok(await E("()=>getComputedStyle(document.getElementById('ffwd')).display")=="none", "⏩ +3시간 = 시험용(아이 화면엔 없음)")
        await E("()=>HOUSE.openBag()"); await pg.wait_for_timeout(500)
        ok(await E("()=>getComputedStyle(document.getElementById('bagP')).visibility==='visible' && !!document.querySelector('#bagP .hdI svg')"), "가방 시트 열림 · 머리 아이콘")
        await E("()=>document.getElementById('bagDone').click()"); await E("()=>HOUSE.go('room')"); await pg.wait_for_timeout(1500)
        await E("()=>document.getElementById('bEdit').click()"); await pg.wait_for_timeout(500)
        h = await E("()=>{ const s=document.querySelector('#drawer .hd b span'); return s.getBoundingClientRect().height; }")
        ok(h < 44, f"창고 머리 두 줄 안 넘음 (창·고 세로로 안 깨짐) {h}")
        await pg.screenshot(path=OUT + "ui413_edit.png")
        ok(not errs, "오류 없음 " + str(errs[:3]))
        await br.close()
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)

asyncio.run(main())
