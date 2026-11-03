"""(v571) 마을 건물 사진첩 — 시설·상점마다 앞에 서서 찍기 (out/bld571/) · 검사 아님"""
import asyncio, sys, os
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from fakefb import fake
from playwright.async_api import async_playwright
D=OUT+"bld571"+os.sep; os.makedirs(D, exist_ok=True)

async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        ctx=await br.new_context(viewport={"width":820,"height":1180}, has_touch=True)
        pg=await ctx.new_page(); errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html?isle=1"); await pg.wait_for_timeout(400)
        await pg.evaluate("()=>{ localStorage.setItem('hyeng_proto_code', JSON.stringify('PHOTO')); localStorage.setItem('hyeng_nick','루아'); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); }")
        await pg.reload(); await pg.wait_for_timeout(2600)
        await pg.evaluate("()=>HOUSE.exitRoom()")
        for _ in range(160):
            if await pg.evaluate("()=>HOUSE.place()==='isle' && !HOUSE.trip().busy"): break
            await pg.wait_for_timeout(250)
        await pg.wait_for_timeout(1000)
        await pg.evaluate("()=>{ ISLE.CAM.zoom=1.25; ISLE.CAM.pitch=.62; }")
        L=await pg.evaluate("()=>{ const out=[]; ISLE.G.traverse(o=>{ if(o.userData && o.userData.fac) out.push([o.userData.fac, o.position.x, o.position.z, o.rotation.y]); }); return out; }")
        shops=await pg.evaluate("()=>(ISLE.SPOT.shops||[]).map(s=>{ const dx=s.door[0]-s.p[0], dz=s.door[2]===undefined ? s.door[1]-s.p[2] : 0, L=Math.hypot(dx,dz)||1; return [s.k, 0, 0, s.door[0]+dx/L*5, s.door[1]+dz/L*5]; })")
        print("fac", [x[0] for x in L]); print("shops", [s[0] for s in shops])
        async def stand(name, x, z):
            await pg.evaluate("([x,z])=>{ const h=HOUSE.hero(); h.g.position.set(x,0,z); h.cx=Math.floor(x); h.cz=Math.floor(z); h.path=[]; try{ placeCamera(); }catch(e){} dirty=true; }", [x, z])
            await pg.wait_for_timeout(900); await pg.screenshot(path=D+name+".png")
        import math
        for k,x,z,ry in L:
            await stand("f_"+k, x+math.sin(ry)*4, z+math.cos(ry)*4)
        for i,(k,x,z,rx,rz) in enumerate(shops[:8]):
            await stand("s%d_%s"%(i,k), rx, rz)
        await br.close(); print("errs", errs[:2])
asyncio.run(main())
