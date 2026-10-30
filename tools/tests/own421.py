"""(v421) 🧸 공용 패드 주인 저절로 — 배려=루아 · 행복=주호 · 정직=라언 · 나눔=경훈 · 책임=단우 (기기 코드로)
  명단에 있으면 그 아이 · 없으면 새로 넣음 · 서버 /hy/pads 에 있으면 그것을 따름 · 공용 패드가 아니면 아무것도 안 함"""
import asyncio, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch()
        async def dev(nick, devc, name):
            ctx = await br.new_context(viewport={"width": 390, "height": 844}, service_workers="block")
            await ctx.add_init_script("window.HY_FB_LOCAL=true; try{ if(!localStorage.getItem('t0')){ localStorage.clear(); localStorage.setItem('t0','1'); localStorage.setItem('hyeng_nick', %s); localStorage.setItem('hyeng_dev', %s); } }catch(e){}" % (json.dumps(nick), json.dumps(devc)))
            pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(name + ": " + str(e))); await boot(pg); return pg
        A = await dev("한양 배려", "axqr06lvmv8tpb58", "A")
        await A.evaluate("()=>FB.set('/hy/roster',{t:{y:{n:'유치부'}}, k:{r1:{n:'루아',t:'y'}, k2:{n:'민준',t:'y'}}}).then(()=>HyBoss.refresh(true))")
        await A.wait_for_timeout(1500)   # (v476) 켤 때 저절로 도는 padAutoOwner(명단 넣기 전)가 만든 주인·임시 루아를 지우고 다시 — 테스트 순서 문제
        await A.evaluate("()=>{ Kid.setOwner(null); return Promise.all([FB.set('/hy/pads/axqr06lvmv8tpb58', null), FB.set('/hy/roster',{t:{y:{n:'유치부'}}, k:{r1:{n:'루아',t:'y'}, k2:{n:'민준',t:'y'}}})]).then(()=>HyBoss.refresh(true)); }")
        r = await A.evaluate("()=>padAutoOwner().then(o=>[o, (Kid.me()||{}).n, Kid.ownerMode()])")
        ok(r[0] and r[0]["k"] == "r1" and r[0]["n"] == "루아" and r[1] == "루아" and r[2], f"배려 패드 = 루아 (명단의 루아) {r}")
        ok(await A.evaluate("()=>FB.get('/hy/pads/axqr06lvmv8tpb58').then(v=>v && v.k==='r1')"), "서버 /hy/pads 에도")
        # 명단에 없으면 새로
        B = await dev("한양 책임", "zg8xy1himv8tvpts", "B")
        r = await B.evaluate("()=>padAutoOwner().then(o=>[o && o.n, HyBoss.kids()[o.k] ? HyBoss.kids()[o.k].n : (FB.get('/hy/roster/k/'+o.k))])")
        nm = r[1] if isinstance(r[1], str) else None
        ok(r[0] == "단우", f"책임 패드 = 단우 {r}")
        # 서버에서 바꾸면 따라감
        await A.evaluate("()=>FB.set('/hy/pads/axqr06lvmv8tpb58', {k:'k2', n:'민준', t:'y', at:Date.now()})")
        r = await A.evaluate("()=>padAutoOwner().then(o=>o && o.n)")
        ok(r == "민준", f"선생님이 서버에서 바꾸면 따라감 {r}")
        # 공용 패드가 아님
        C = await dev("김지후", "axqr06lvmv8tpb58", "C")
        ok(await C.evaluate("()=>padAutoOwner().then(o=>o===null && !Kid.owner())"), "자기 기기는 아무것도 안 함")
        ok(not errs, "오류 없음 " + str(errs[:3]))
        await br.close()
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)

asyncio.run(main())
