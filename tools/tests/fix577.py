"""(v577) 사용자 아이폰 사진:
   ① 「지도 누르고 마을 가면 예전에 만든 마을로 가지더라」 → 섬 모드 지도 = 🏝 우리 마을(섬) · 없는 숲·바닷가 뺌 · 2×2
   ② 「저 창 때문에 나가기나 다른 게 안 보여」 → 왼쪽 위 💎🪙🪱·할 일·🍗 칸을 옆으로 두 줄 · 문 「나가기」 이름표와 안 겹침
   ③ 「밑에 파란색으로 남더라」 → 홈 화면 앱(iOS 26)에서 화면 고정 칸이 짧을 때 캔버스·아래 단추 줄·시트를 기기 화면 끝까지"""
import asyncio, sys, os
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from fakefb import fake
from playwright.async_api import async_playwright

SA="""Object.defineProperty(navigator,'standalone',{get:()=>true}); Object.defineProperty(screen,'height',{get:()=>932}); Object.defineProperty(screen,'width',{get:()=>430});"""

async def main():
    bad=[]; errs=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        # 홈 화면 앱 흉내: 기기 화면 932 · 화면 고정 칸 886 (46 짧음)
        ctx=await br.new_context(viewport={"width":430,"height":886}, is_mobile=True, has_touch=True, device_scale_factor=2)
        await ctx.add_init_script(SA)
        pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html?isle=1"); await pg.wait_for_timeout(400)
        await pg.evaluate("()=>{ localStorage.setItem('hyeng_proto_code', JSON.stringify('FIX77')); localStorage.setItem('hyeng_nick','루아'); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); }")
        await pg.reload(); await pg.wait_for_timeout(3000)
        # ③ 아래 빈 띠
        r=await pg.evaluate("()=>{ const c=document.getElementById('cv').getBoundingClientRect(), b=document.querySelector('.bar.bot').getBoundingClientRect(); return [APPH, Math.round(c.height), Math.round(b.bottom), renderer.domElement.height/devicePixelRatio|0]; }")
        ok(r[0]==932 and r[1]==932 and r[2]>=930 and abs(r[3]-932)<=2, f"③ 홈 화면 앱: 캔버스·아래 단추 줄이 기기 화면 끝(932)까지 {r}")
        # ② 왼쪽 위 칸 = 두 줄 · 나가기 이름표와 안 겹침
        r=await pg.evaluate("""()=>{ const h=document.getElementById('hud').getBoundingClientRect(); const pills=[...document.querySelectorAll('#hud > *')].filter(e=>e.offsetParent).map(e=>e.getBoundingClientRect());
            const L=LBL.filter(L=>L.el.style.display!=='none' && /나가기/.test(L.el.textContent)).map(L=>L.el.getBoundingClientRect());
            const hit=L.some(a=>pills.some(b=>a.left<b.right && b.left<a.right && a.top<b.bottom && b.top<a.bottom));
            return [Math.round(h.height), pills.length, L.length, hit]; }""")
        ok(r[0]<=100 and r[1]>=4 and not r[3], f"② 왼쪽 위 칸 높이 ≤ 100 (두 줄) · 나가기 이름표와 안 겹침 {r}")
        await pg.screenshot(path=OUT+"fix577_room.png")
        # ① 지도
        await pg.evaluate("()=>document.getElementById('bMap').click()"); await pg.wait_for_timeout(500)
        r=await pg.evaluate("()=>[[...document.querySelectorAll('#mapBody [data-go]')].map(b=>b.dataset.go), document.getElementById('mapBody').innerText.replace(/\\s+/g,' '), Math.round(document.getElementById('mapP').getBoundingClientRect().bottom)]")
        ok(r[0]==["room","yard","isle","mine"] and "우리 마을" in r[1] and r[2]>=930, f"① 지도 = 내 집·마당·🏝 우리 마을·광산 (예전 마을·숲·바닷가 없음) · ③ 시트도 화면 끝까지 {r}")
        await pg.screenshot(path=OUT+"fix577_map.png")
        await pg.evaluate("()=>document.querySelector('#mapBody [data-go=isle]').click()")
        for _ in range(120):
            if await pg.evaluate("()=>HOUSE.place()==='isle' && !HOUSE.trip().busy"): break
            await pg.wait_for_timeout(250)
        ok(await pg.evaluate("()=>HOUSE.place()==='isle'"), "① 🏝 우리 마을을 누르면 섬으로 (예전 마을 아님)")
        await pg.wait_for_timeout(1500)
        # 섬에서 땅을 누르면 그 자리로 (VH 로 바꾼 눌림 위치가 맞는지)
        r=await pg.evaluate("""()=>{ const h=HOUSE.hero().g.position; const v=h.clone(); v.project(camera); return [Math.round((v.x+1)/2*innerWidth), Math.round((1-v.y)/2*VH())]; }""")
        await pg.screenshot(path=OUT+"fix577_isle.png")
        ok(0<r[0]<430 and 200<r[1]<932, f"섬: 캐릭터가 화면 안 {r}")
        await br.close()
        # 보통 브라우저(홈 화면 앱 아님) = 그대로
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        pg=await (await br.new_context(viewport={"width":390,"height":844}, is_mobile=True, has_touch=True)).new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html"); await pg.wait_for_timeout(2600)
        r=await pg.evaluate("()=>[APPH, Math.round(document.getElementById('cv').getBoundingClientRect().height), [...document.querySelectorAll('#mapBody [data-go]')].length || (drawMap(), [...document.querySelectorAll('#mapBody [data-go]')].map(b=>b.dataset.go))]")
        ok(r[0]==0 and r[1]==844 and r[2]==["room","yard","village","forest","beach","mine"], f"보통 브라우저 · 섬 아닌 맛보기 = 예전 그대로 {r}")
        await br.close()
    ok(not errs, f"오류 없음 {errs[:2]}")
    print("\nFAIL" if bad else "\nPASS", len(bad)); sys.exit(1 if bad else 0)

asyncio.run(main())
