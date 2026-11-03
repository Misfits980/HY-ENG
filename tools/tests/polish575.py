"""(v575) 섬 점검(미술 감독) 고침 사진첩 + 검사
   둥근 바닥 polygonOffset · 첫 화면 카메라 · 깃발 줄 · 목표판 자리 · 구역 겹 · 차양 · 연꽃 · 빈 땅 글씨 · 밤 가로등 · 학교 십자가 없앰 · 무대"""
import asyncio, sys, os
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from fakefb import fake
from playwright.async_api import async_playwright
D=OUT+"pol575"+os.sep; os.makedirs(D, exist_ok=True)

async def main():
    bad=[]; errs=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        ctx=await br.new_context(viewport={"width":1180,"height":820}, has_touch=True)
        pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html?isle=1"); await pg.wait_for_timeout(400)
        await pg.evaluate("()=>{ localStorage.setItem('hyeng_proto_code', JSON.stringify('POLSH')); localStorage.setItem('hyeng_nick','루아'); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); }")
        await pg.reload(); await pg.wait_for_timeout(2600)
        await pg.evaluate("()=>HOUSE.exitRoom()")
        for _ in range(160):
            if await pg.evaluate("()=>HOUSE.place()==='isle' && !HOUSE.trip().busy"): break
            await pg.wait_for_timeout(250)
        await pg.wait_for_timeout(1500); await pg.screenshot(path=D+"01_arrive.png")
        r=await pg.evaluate("""()=>{ let disc=0, po=0; ISLE.G.children.forEach(m=>{ if(m.isMesh && m.geometry && m.geometry.type==='CircleGeometry'){ disc++; if(m.material.polygonOffset) po++; } });
            let glow=0; ISLE.G.traverse(o=>{ if(o.isSprite && o.material.blending===THREE.AdditiveBlending) glow++; });
            let lines=0; ISLE.G.traverse(o=>{ if(o.isLineSegments) lines++; });
            return [disc, po, glow, lines, !!(KK.R.isle && KK.R.isle.G.school_nc), ISLE_MAP.spots.goal]; }""")
        ok(r[1]>=r[0]-2 and r[0]>3, f"둥근 바닥 polygonOffset {r[:2]}")
        ok(r[2]>=5, f"밤 가로등 빛 {r[2]}")
        ok(r[3]>=1, f"깃발 줄 {r[3]}")
        ok(r[4], "학교 = 십자가 잘라 낸 모델")
        async def at(name, x, z, zoom=1.5, pitch=.9):
            await pg.evaluate("([x,z,zm,pt])=>{ ISLE.CAM.zoom=zm; ISLE.CAM.pitch=pt; TFAC.warp(x+98,z+98); }", [x, z, zoom, pitch])
            await pg.wait_for_timeout(1100); await pg.screenshot(path=D+name+".png")
        S=await pg.evaluate("()=>ISLE_MAP.spots")
        await at("10_plaza", 0, 9.5, 2.2, 1.0)
        await at("11_post_goal", 6, 1, 1.4, .8)
        await at("20_school", S["school"][0]+6, S["school"][1]+6, 1.6, .7)
        await at("21_stage", S["stage"][0]+3, S["stage"][1]+4, 1.3, .7)
        await at("30_ox_park", S["ox"][0], S["ox"][1]+5, 2.2, 1.0)
        await at("40_market", 15, -13, 1.6, .85)
        await at("50_lake", 41, -9, 2.0, .95)
        await at("60_lots", -30, 30, 2.0, .95)
        await pg.evaluate("()=>{ ISLE.night(true); }"); await at("70_night_plaza", 0, 9.5, 2.0, .8)
        await br.close()
    ok(not errs, f"오류 없음 {errs[:2]}")
    print("\nFAIL" if bad else "\nPASS", len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
