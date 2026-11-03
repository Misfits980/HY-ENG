"""(v580) 마당 사진첩 — 휴대폰·패드 · 여러 각도 (검사 아님) · PF=b_ 고치기 전"""
import asyncio, sys, os
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from fakefb import fake
from playwright.async_api import async_playwright
D=OUT+"y580"+os.sep; os.makedirs(D, exist_ok=True)
PF=os.environ.get("PF","")

async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        for nm,vp in [("phone",{"width":390,"height":844}),("pad",{"width":820,"height":1180})]:
            ctx=await br.new_context(viewport=vp, is_mobile=nm=="phone", has_touch=True)
            pg=await ctx.new_page(); errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
            await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html?isle=1"); await pg.wait_for_timeout(400)
            await pg.evaluate("()=>{ localStorage.setItem('hyeng_proto_code', JSON.stringify('YSHOT')); localStorage.setItem('hyeng_nick','루아'); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); }")
            await pg.reload(); await pg.wait_for_timeout(2800)
            await pg.evaluate("()=>{ go('yard', [DOOR[0],DOOR[1]+1]); }"); await pg.wait_for_timeout(2600)
            await pg.screenshot(path=D+PF+nm+"_1.png")
            await pg.evaluate("()=>{ try{ yaw=yawTo=yaw+Math.PI/2; }catch(e){} dirty=true; }"); await pg.wait_for_timeout(1200)
            await pg.screenshot(path=D+PF+nm+"_2.png")
            await pg.evaluate("()=>{ setEdit(true); }"); await pg.wait_for_timeout(1200)
            await pg.screenshot(path=D+PF+nm+"_edit.png")
            await pg.evaluate("()=>{ setEdit(false); }")
            print(nm, errs[:2])
            await ctx.close()
        await br.close()
asyncio.run(main())
