"""사고팔기 화면 사진첩 (검사 아님) — 물고기 가게(팔기) · 마트 · 간식 · 가구 가게 · 가방 · PF 앞붙임"""
import asyncio, sys, os
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from fakefb import fake
from playwright.async_api import async_playwright
D=OUT+"shop"+os.sep; os.makedirs(D, exist_ok=True)
PF=os.environ.get("PF","")

async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        for nm,vp in [("phone",{"width":390,"height":844}),("pad",{"width":820,"height":1180})]:
            ctx=await br.new_context(viewport=vp, is_mobile=nm=="phone", has_touch=True)
            pg=await ctx.new_page(); errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
            await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html?isle=1"); await pg.wait_for_timeout(400)
            await pg.evaluate("()=>{ localStorage.setItem('hyeng_proto_code', JSON.stringify('SHOPS')); localStorage.setItem('hyeng_nick','루아'); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); }")
            await pg.reload(); await pg.wait_for_timeout(2800)
            await pg.evaluate("""()=>{ TECO.setCoin(820); const t=Date.now(); ['fish','fish','crab','frog','shark','whale','squid','sock','turtle','shrimp'].forEach((en,i)=>bag.push({en, at:t-i*3600e3*5, cm:(SPEC[en].cm?SPEC[en].cm[0]+5:0)})); addMat('carrot',4); addMat('apple',3); addMat('wheat',6); saveBag(); }""")
            await pg.evaluate("()=>HOUSE.exitRoom()")
            for _ in range(160):
                if await pg.evaluate("()=>HOUSE.place()==='isle' && !HOUSE.trip().busy"): break
                await pg.wait_for_timeout(250)
            await pg.wait_for_timeout(800)
            for k in ["fish","mart","snack","furn"]:
                await pg.evaluate("(k)=>{ const S=ISLE.SPOT.shops.find(s=>s.k===k); if(S){ TFAC.warp(S.door[0], S.door[1]); } }", k); await pg.wait_for_timeout(600)
                await pg.evaluate("(k)=>{ const S=ISLE.SPOT.shops.find(s=>s.k===k); const L=LBL.find(l=>l.d.k===k); if(L) L.d.act(); }", k)
                for _ in range(60):
                    if await pg.evaluate("()=>[...document.querySelectorAll('.sheet.on, .tfP.on, #tfSnack.on, .on.tfW')].length>0 || !!document.querySelector('[id^=tf].on')"): break
                    await pg.wait_for_timeout(250)
                await pg.wait_for_timeout(900)
                await pg.screenshot(path=D+PF+nm+"_"+k+".png")
                await pg.evaluate("()=>{ document.querySelectorAll('.on').forEach(e=>{ if(e.matches('.sheet,[id^=tf]')) e.classList.remove('on'); }); }")
                await pg.evaluate("()=>{ try{ SHOPIN.exit && SHOPIN.exit(); }catch(e){} }")
                for _ in range(60):
                    if await pg.evaluate("()=>HOUSE.place()==='isle' && !HOUSE.trip().busy"): break
                    await pg.wait_for_timeout(250)
            await pg.evaluate("()=>openBag()"); await pg.wait_for_timeout(700); await pg.screenshot(path=D+PF+nm+"_bag.png")
            print(nm, errs[:2])
            await ctx.close()
        await br.close()
asyncio.run(main())
