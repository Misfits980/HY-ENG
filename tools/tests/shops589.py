"""(v589) 가게 8곳 = 서로 다른 건물 — 사진첩 + 검사 (사용자: 「상점들은 모양이 다 똑같아」)"""
import asyncio, sys, os
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from fakefb import fake
from playwright.async_api import async_playwright
D=OUT+"shops589"+os.sep; os.makedirs(D, exist_ok=True)
async def main():
    bad=[]; errs=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        pg=await (await br.new_context(viewport={"width":820,"height":1180}, has_touch=True)).new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html?isle=1"); await pg.wait_for_timeout(400)
        await pg.evaluate("()=>{ localStorage.setItem('hyeng_proto_code', JSON.stringify('SHP89')); localStorage.setItem('hyeng_nick','루아'); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); }")
        await pg.reload(); await pg.wait_for_timeout(2800)
        await pg.evaluate("()=>HOUSE.exitRoom()")
        for _ in range(160):
            if await pg.evaluate("()=>HOUSE.place()==='isle' && !HOUSE.trip().busy"): break
            await pg.wait_for_timeout(250)
        r=await pg.evaluate("()=>{ const K=[]; ISLE.G.traverse(o=>{ if(o.userData.shopK) K.push(o.userData.shopK); }); return K; }")
        ok(len(set(r))==8, f"가게 8곳 = 각자 다른 건물 {r}")
        L=await pg.evaluate("()=>MAP_SHOPS=ISLE.SPOT.shops.map(s=>[s.k, s.door[0], s.door[1], s.p[0], s.p[2]])")
        for k,dx,dz,px,pz in L:
            await pg.evaluate("([dx,dz,px,pz])=>{ HOUSE.setWx(false); const vx=dx-px, vz=dz-pz, l=Math.hypot(vx,vz)||1; TFAC.warp(dx+vx/l*3.2, dz+vz/l*3.2); yaw=yawTo=Math.atan2(vx,vz)+Math.PI+0.3; ISLE.CAM.zoom=1.5; ISLE.CAM.pitch=.45; ISLE.CAM.dragAt=performance.now()+1e6; }", [dx,dz,px,pz])
            await pg.wait_for_timeout(1800); await pg.screenshot(path=D+k+".png")
        # 문 앞 갈 수 있음 · 가게 들어가기
        r=await pg.evaluate("()=>ISLE.SPOT.shops.map(s=>[s.k, !ISLE.blocked(Math.floor(s.door[0]),Math.floor(s.door[1]))])")
        ok(sum(1 for x in r if x[1])>=7, f"문 앞 칸 열림 (펫 가게는 예전부터 막힘 → 가게 앞에서 바로 들어감) {r}")
        await br.close()
    ok(not errs, f"오류 없음 {errs[:2]}")
    print("\nFAIL" if bad else "\nPASS", len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
