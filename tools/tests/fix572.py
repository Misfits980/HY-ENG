"""(v572) 사용자 아이패드 사진:
   ① 가로로 돌리면 오른쪽에 파란 줄 → maximum-scale=1 · 돌린 뒤 다시 맞춤(reFit)
   ③ 친구 집 스티커 칸이 창 밖으로 → 칸이 줄어들 수 있게 (minmax(0,1fr))
   ④ 땅에 초록 줄무늬 → 바닥 판 polygonOffset · 카메라 near 0.3
   ⑤ 낚시터 판자에 가라앉음 → 판 윗면 = 0 · 다리 폭 · 새 부두 (난간·등불)"""
import asyncio, sys, os
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from fakefb import fake
from playwright.async_api import async_playwright

async def main():
    bad=[]; errs=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        ctx=await br.new_context(viewport={"width":1080,"height":810}, is_mobile=True, has_touch=True)
        pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html?isle=1"); await pg.wait_for_timeout(400)
        await pg.evaluate("()=>{ localStorage.setItem('hyeng_proto_code', JSON.stringify('FIX72')); localStorage.setItem('hyeng_nick','루아'); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); }")
        await pg.reload(); await pg.wait_for_timeout(2600)
        r=await pg.evaluate("()=>[document.querySelector('meta[name=viewport]').content, camera.near]")
        ok("maximum-scale=1" in r[0] and r[1]>=0.3, f"① 확대 막기 · ④ 카메라 near {r}")
        # ③ 스티커 칸 (iPad 가로)
        r=await pg.evaluate("""()=>{ ask('🌟 스티커를 남겨요<div class="stkG">'+STK.map(s=>'<button class="stkB">'+s+'</button>').join('')+'</div>', null); const b=document.querySelector('#ask .box').getBoundingClientRect(); const L=[...document.querySelectorAll('#ask .stkB')].map(e=>e.getBoundingClientRect()); return [L.length, L.every(x=>x.right<=b.right+1 && x.left>=b.left-1 && x.bottom<=b.bottom+1)]; }""")
        ok(r==[8,True], f"③ 스티커 8칸이 창 안에 {r}")
        await pg.evaluate("()=>document.getElementById('ask').classList.remove('on')")
        # 섬
        await pg.evaluate("()=>HOUSE.exitRoom()")
        for _ in range(160):
            if await pg.evaluate("()=>HOUSE.place()==='isle' && !HOUSE.trip().busy"): break
            await pg.wait_for_timeout(250)
        await pg.wait_for_timeout(2500)
        r=await pg.evaluate("""()=>{ let flatPO=0, flat=0; ISLE.G.children.forEach(m=>{ if(m.isMesh && m.material && m.material.polygonOffset) flatPO++; });
            const B=ISLE.G.userData.dock, bb=new THREE.Box3().setFromObject(B); let top=-9; B.children.forEach(c=>{ if(c.geometry && c.geometry.type==='BoxGeometry' && c.geometry.parameters.depth>=1.7){ const b=new THREE.Box3().setFromObject(c); top=Math.max(top,b.max.y); } });
            return [flatPO, +top.toFixed(3), B.children.length]; }""")
        ok(r[0]>=2 and abs(r[1])<0.02 and r[2]>=30, f"④ 바닥 판 polygonOffset · ⑤ 부두 판 윗면 = 땅(0) · 난간·등불 {r}")
        # 부두 위에 서기 → 사진
        await pg.evaluate("()=>{ ISLE.CAM.zoom=.8; const s=ISLE.SPOT.lake; TFAC.warp(s[0]-1.2, s[2]); }")
        await pg.wait_for_timeout(1500); print("hero", await pg.evaluate("()=>{ const p=HOUSE.hero().g.position; return [p.x,p.z, ISLE.SPOT.lake]; }"))
        await pg.screenshot(path=OUT+"fix572_dock.png")
        ok(await pg.evaluate("()=>{ const p=HOUSE.hero().g.position, s=ISLE.SPOT.lake; return Math.hypot(p.x-s[0],p.z-s[2])<3; }"), "⑤ 부두 위에 설 수 있음")
        await br.close()
    ok(not errs, f"오류 없음 {errs[:2]}")
    print("\nFAIL" if bad else "\nPASS", len(bad)); sys.exit(1 if bad else 0)

asyncio.run(main())
