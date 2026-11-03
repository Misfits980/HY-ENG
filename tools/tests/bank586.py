"""(v586) 사용자: 「은행에 바꾸려고 하는데 왜 안 돼?」 → 화면: 「📡 서버 시계를 기다리는 중」
   까닭: 켤 때 서버 연결이 한 번 늦으면 그 판 내내 「안 됨」(NET mode off) · 서버 시계도 10분마다만 다시 → 은행이 계속 막힘
   ① 처음 몇 초 서버가 안 돼도 → 다시 찾아서 시계가 맞춰지고 💎 로 바뀜  ② 은행 단추를 누르면 그 자리에서 다시 맞춰 보고 되면 이어서
   ③ 서버가 권한으로 막으면(401) 「🔐 … 선생님께」 안내 (까닭이 보이게)"""
import asyncio, sys, os, json, time
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from fakefb import fake
from playwright.async_api import async_playwright

MODE={"down_until":0, "deny":False}
async def route(r):
    url=r.request.url
    if "firebasedatabase.app" in url or "firebaseio.com" in url:
        if time.time()<MODE["down_until"]: return await r.abort()
        if "/hy/day/ck" in url and r.request.method=="PUT":
            if MODE["deny"]: return await r.fulfill(status=401, body='{"error":"Permission denied"}', content_type="application/json")
            return await r.fulfill(status=200, body=str(int(time.time()*1000)), content_type="application/json")
    return await fake(r)

async def main():
    bad=[]; errs=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        ctx=await br.new_context(viewport={"width":390,"height":844}, is_mobile=True, has_touch=True)
        await ctx.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>false});")
        pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*", route); await pg.goto(ORIGIN+"proto/house.html?isle=1"); await pg.wait_for_timeout(300)
        await pg.evaluate("()=>{ localStorage.setItem('hyeng_proto_code', JSON.stringify('BANK6')); localStorage.setItem('hyeng_nick','루아'); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); localStorage.removeItem('hyeng_fb_url'); }")
        MODE["down_until"]=time.time()+9
        await pg.reload(); await pg.wait_for_timeout(6000)
        r=await pg.evaluate("()=>[TWN8.ok, NET.on()]")
        ok(r==[False,False], f"켤 때 서버가 안 됨 → 시계 아직 {r}")
        await pg.evaluate("()=>{ TECO.setCoin(200); TECO.openBank('ex'); }"); await pg.wait_for_timeout(400)
        await pg.evaluate("()=>TECO.buyGem(1)"); await pg.wait_for_timeout(3500)
        t=await pg.evaluate("()=>document.getElementById('toast').innerText")
        ok("서버" in t, f"② 아직이면 안내 (까닭) {t!r}")
        # 서버가 돌아옴 → 저절로 다시 맞춤
        for i in range(60):
            if await pg.evaluate("()=>TWN8.ok"): break
            await pg.wait_for_timeout(1000)
        ok(await pg.evaluate("()=>TWN8.ok"), f"① 서버가 돌아오면 저절로 시계 맞춤 ({i}초)")
        r=await pg.evaluate("()=>{ const g0=HOUSE.gems(), c0=TECO.coins(); const n=TECO.buyGem(1); return [n, HOUSE.gems()-g0, c0-TECO.coins()>0]; }")
        ok(r[0]==1 and r[1]==1 and r[2], f"① 💎 1 바꾸기 됨 {r}")
        # ② 은행 단추에서 바로 다시 맞춤
        await pg.evaluate("()=>{ TWN8.ok=false; }")
        r=await pg.evaluate("()=>new Promise(res=>{ const g0=HOUSE.gems(); TECO.buyGem(1); setTimeout(()=>res([TWN8.ok, HOUSE.gems()-g0]), 2500); })")
        ok(r==[True,1], f"② 시계가 풀려 있어도 누르면 다시 맞추고 이어서 바꿈 {r}")
        # ③ 권한으로 막힘
        MODE["deny"]=True
        await pg.evaluate("()=>{ TWN8.ok=false; }")
        await pg.evaluate("()=>TECO.buyGem(1)"); await pg.wait_for_timeout(2500)
        t=await pg.evaluate("()=>[document.getElementById('toast').innerText, TWN8.err]")
        ok("선생님" in t[0] and t[1]=="401", f"③ 서버 권한(401) = 「🔐 … 선생님께」 {t}")
        await br.close()
    ok(not errs, f"오류 없음 {errs[:2]}")
    print("\nFAIL" if bad else "\nPASS", len(bad)); sys.exit(1 if bad else 0)

asyncio.run(main())
