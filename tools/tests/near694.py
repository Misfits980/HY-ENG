"""(v694) 섬 「카메라 앞 비침(uNear)」 깊이 부호 — v689~v693 에서는 -vViewPosition.z 라 섬의 모든 툰 물건이 높이 .35 위로 잘렸음
   (나무 = 컵 모양 · 마을 목표판·간판·호박 장식 사라짐). 같은 장면을 uNear 켬/끔으로 찍어 먼 곳(화면 위 55%)이 같은지 본다.
   ① uNear 가 섬에서 켜져 있음(>0)  ② 먼 곳 그림이 거의 같음(바뀐 점 < 2.5%)  ③ 오류 없음"""
import asyncio, sys, os, io
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from fakefb import fake
from playwright.async_api import async_playwright
from PIL import Image, ImageChops

async def main():
    bad=[]; errs=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        ctx=await br.new_context(viewport={"width":820,"height":1180}, has_touch=True); pg=await ctx.new_page(); pg.set_default_timeout(150000)
        pg.on("pageerror", lambda e: errs.append(str(e)[:200]))
        await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html?isle=1"); await pg.wait_for_timeout(400)
        await pg.evaluate("""()=>{ Object.keys(localStorage).filter(k=>k.startsWith('hyeng_')).forEach(k=>localStorage.removeItem(k));
            localStorage.setItem('hyeng_proto_code', JSON.stringify('QN694')); localStorage.setItem('hyeng_nick','루아'); localStorage.setItem('hyeng_dev','dQN694'); localStorage.setItem('hyeng_me', JSON.stringify({id:'kQN694', t:'A568'})); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); }""")
        await pg.reload(); await pg.wait_for_timeout(2000)
        await pg.evaluate("()=>ISLE.enter()")
        for _ in range(200):
            if await pg.evaluate("()=>HOUSE.place()==='isle' && !HOUSE.trip().busy"): break
            await pg.wait_for_timeout(250)
        await pg.evaluate("()=>TFAC.warp(ISLE.OX+4.5, ISLE.OZ+4.5)"); await pg.wait_for_timeout(3000)
        nv=await pg.evaluate("()=>TOON.nearV()")
        ok(nv>0, f"① 섬에서 uNear 켜짐 {nv}")
        await pg.evaluate("()=>{ window.__nr=TOON.near; TOON.near=()=>{}; }"); await pg.wait_for_timeout(300)
        a=Image.open(io.BytesIO(await pg.screenshot())).convert("RGB")
        await pg.evaluate("()=>{ window.__nr(0); }"); await pg.wait_for_timeout(600)
        b=Image.open(io.BytesIO(await pg.screenshot())).convert("RGB")
        await pg.evaluate("()=>{ TOON.near=window.__nr; }")
        W,H=a.size; box=(0, int(H*.18), W, int(H*.55))   # 위 HUD 아래 ~ 화면 가운데 (먼 곳)
        d=ImageChops.difference(a.crop(box), b.crop(box)).convert("L").point(lambda v: 255 if v>40 else 0)
        frac=sum(1 for v in d.getdata() if v)/(d.size[0]*d.size[1])
        a.save(OUT+"near694_on.png"); b.save(OUT+"near694_off.png")
        ok(frac<0.025, f"② 먼 곳은 uNear 켬/끔이 같음 — 바뀐 점 {frac*100:.2f}% (예전 부호 오류면 나무·간판이 잘려 크게 다름)")
        ok(not real_errs(errs), f"③ JS 오류 없음 {real_errs(errs)[:3]}")
        await br.close()
    print("DONE bad=%d"%len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
