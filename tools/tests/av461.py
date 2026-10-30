"""(v460~461) 🧒 캐릭터 — 사용자: "캐릭터 퀄리티 조금 더" · "몸통이 조금 더 자연스러우면 좋겠지만 표정이랑 선택해서"
  ① 몸통 = 둥근 돌림체 (네모 상자 아님) · 색 = 적은 그대로(sRGB)
  ② 나 꾸미기 → 🙂 얼굴 탭에 「표정」 6개 · 고르면 내 캐릭터 표정이 바뀌고 저장됨
  ③ 감정 표현(😱 등) → 잠깐 그 표정 → 말풍선이 사라지면 고른 표정으로
  ④ 모든 옷·모자·머리 × 표정 조합이 오류 없이 만들어짐"""
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
        await pg.evaluate("()=>{ Object.keys(localStorage).filter(k=>k.startsWith('hyeng_proto_')).forEach(k=>localStorage.removeItem(k)); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); localStorage.setItem('hyeng_proto_baitok','1'); }")
        await pg.reload(); await pg.wait_for_timeout(2500)
        E = pg.evaluate
        await E("()=>{ HOUSE.setWx(false); HOUSE.go('yard'); }"); await pg.wait_for_timeout(2500)
        r = await E("""()=>{ const h=HOUSE.hero(); let lathe=0, srgb=0; h.g.traverse(m=>{ if(m.isMesh && m.geometry && m.geometry.type==='LatheGeometry') lathe++; }); const c=new THREE.Color('#6ec3ff').convertSRGBToLinear(); let found=false; h.g.traverse(m=>{ if(m.material && m.material.isMeshToonMaterial && Math.abs(m.material.color.r-c.r)<0.002 && Math.abs(m.material.color.b-c.b)<0.002) found=true; }); return [lathe, found, h.expr]; }""")
        ok(r[0] >= 2 and r[1] and r[2] == "smile", f"둥근 몸통·엉덩이 · 옷 색 sRGB · 처음 표정 방긋 {r}")
        # ②
        await E("()=>HOUSE.openAv()"); await pg.wait_for_timeout(400)
        r = await E("()=>[...document.querySelectorAll('#avBody [data-k=expr]')].map(b=>b.dataset.v)")
        ok(r == ["smile", "grin", "wink", "wow", "cat", "cool"], f"🙂 얼굴 탭 = 표정 6개 {r}")
        await pg.screenshot(path=OUT + "av461_pick.png")
        await E("()=>document.querySelector('#avBody [data-k=expr][data-v=wink]').click()"); await pg.wait_for_timeout(300)
        r = await E("()=>[HOUSE.hero().expr, HOUSE.av().expr, JSON.parse(localStorage.getItem('hyeng_proto_av')).expr, document.querySelector('#avBody [data-k=expr].on').dataset.v, HOUSE.hero().eyesG.children.length]")
        ok(r[0] == r[1] == r[2] == r[3] == "wink" and r[4] > 3, f"😉 윙크 고름 → 내 캐릭터 · 저장 · 표시 {r}")
        await pg.screenshot(path=OUT + "av461_wink.png")
        await E("()=>document.getElementById('avDone').click()"); await pg.wait_for_timeout(300)
        # ③
        r = await E("()=>{ const h=HOUSE.hero(); HOUSE.emote(h,'😱'); return h.expr; }")
        r2 = None
        for _ in range(60):
            await pg.wait_for_timeout(250); r2 = await E("()=>HOUSE.hero().expr")
            if r2 != "wow": break
        ok(r == "wow" and r2 == "wink", f"😱 → 잠깐 깜짝 → 다시 윙크 {r} {r2}")
        # ④
        r = await E("""()=>{ const O=HOUSE.AV_OPT, out=[]; let n=0; for(const st of O.style) for(const h of O.hat) for(const hr of O.hair) for(const ex of O.expr){ const A=HOUSE.buildAvatar({style:st[0], hat:h[0], hair:hr[0], expr:ex[0], acc:['none','glasses','ribbon','flower','backpack'][n%5]}); n++; if(!A.setExpr || A.expr!==ex[0]) out.push([st[0],h[0],hr[0],ex[0]]); A.setExpr('grin'); A.setExpr(ex[0]); } return [n, out.slice(0,3)]; }""")
        ok(r[0] == 4 * 5 * 5 * 6 and not r[1], f"옷 4 × 모자 5 × 머리 5 × 표정 6 = {r[0]} 모두 만들어짐 {r[1]}")
        ok(not real_errs(errs), "오류 없음 " + str(real_errs(errs)[:3]))
        await br.close()
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)
asyncio.run(main())
