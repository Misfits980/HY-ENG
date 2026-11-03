"""(v576) 🌿 마당 잡초가 다시 자람 — 사용자: 「그래도 좋지」
   처음엔 오늘 날짜만 적음(안 자람) · 하루 지나면 2포기 · 사흘이면 6 · 최대 8 · 같은 날 또 안 자람 · 빈 칸에만 · 뽑으면 사라짐(가끔 씨앗)"""
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
        pg=await (await br.new_context(viewport={"width":390,"height":844}, is_mobile=True, has_touch=True)).new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html"); await pg.wait_for_timeout(400)
        await pg.evaluate("()=>{ localStorage.setItem('hyeng_proto_code', JSON.stringify('WEEDK')); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); }")
        await pg.reload(); await pg.wait_for_timeout(2800)
        W="()=>Object.values(yd.db).filter(t=>t==='weed2').length"
        r=await pg.evaluate("()=>{ yd.wd=''; const n=yRegrow(); return [n, yd.wd===dayKey()]; }")
        ok(r==[0,True], f"처음 = 오늘만 적고 안 자람 {r}")
        r=await pg.evaluate("()=>{ const d=new Date(dayKey()); d.setDate(d.getDate()-1); yd.wd=d.toISOString().slice(0,10); return [yRegrow(), yRegrow()]; }")
        ok(r==[2,0], f"하루 지나면 2포기 · 같은 날 또 안 자람 {r}")
        r=await pg.evaluate("()=>{ const d=new Date(dayKey()); d.setDate(d.getDate()-5); yd.wd=d.toISOString().slice(0,10); yRegrow(); return "+W[4:]+"; }")
        ok(r==8, f"며칠 비워도 최대 8 (2 + 사흘치 6 → 8) {r}")
        r=await pg.evaluate("""()=>{ const bad=Object.keys(yd.db).filter(k=>yd.db[k]==='weed2').filter(k=>{ const [x,z]=k.split(',').map(Number); const t=yd.db[k]; delete yd.db[k]; const b=yardBlocked(x,z); yd.db[k]=t; return b || yLocked(x,z) || !!yItemAt(x,z) || isRoad(x,z) || Math.abs(x-DOOR[0])+Math.abs(z-DOOR[1])<=2; }); return bad; }""")
        ok(r==[], f"빈 칸에만 (밭·가구·길·문 앞·잠긴 땅 아님) {r}")
        r=await pg.evaluate("()=>{ const k=Object.keys(yd.db).find(k=>yd.db[k]==='weed2'); yClear(k); return [!!yd.db[k], JSON.parse(localStorage.getItem('hyeng_proto_yard')).db[k]||null, JSON.parse(localStorage.getItem('hyeng_proto_yard')).wd===dayKey()]; }")
        ok(r==[False,None,True], f"뽑으면 사라짐 · 저장(날짜 포함) {r}")
        await pg.evaluate("()=>{ go('yard', [DOOR[0],DOOR[1]+1]); }"); await pg.wait_for_timeout(2500)
        await pg.screenshot(path=OUT+"weed576_yard.png")
        ok(await pg.evaluate("()=>place===PL.yard"), "마당 사진")
        await br.close()
    ok(not errs, f"오류 없음 {errs[:2]}")
    print("\nFAIL" if bad else "\nPASS", len(bad)); sys.exit(1 if bad else 0)

asyncio.run(main())
