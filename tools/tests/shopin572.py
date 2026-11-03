"""(v572) 사용자: 「파는 곳인데 괴리감 · 가게를 들어가서 하는 게 아니더라 · 가게도 안을 꾸며서 만들어 줘」
   ① 상점가 8곳 이름표 → 걸어가서 문 → 🏪 가게 안 (장소 shop · 가게마다 장식·주인)
   ② 들어가면 주인 인사(영어 말풍선) → 카운터까지 걸어가서 원래 가게 창이 열림
   ③ 창 닫고 주인(카운터)을 누르면 다시 그 창 · 물건을 누르면 영어 이름
   ④ 🚪 나가기 → 섬의 그 가게 문 앞 · 장식은 버림
   ⑤ 휴대폰·패드 가로 스크린샷 · 오류 없음
   SHOT=0 이면 스크린샷 생략 · ONLY=fish,pet 이면 그 가게만"""
import asyncio, sys, os
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from fakefb import fake
from playwright.async_api import async_playwright

SHEET={"fish":"()=>document.getElementById('shopP').classList.contains('on')",
       "clothes":"()=>document.getElementById('avP').classList.contains('on') && /옷 가게/.test(document.getElementById('avTtl').textContent)",
       "hair":"()=>document.getElementById('avP').classList.contains('on') && /미용실/.test(document.getElementById('avTtl').textContent)",
       "mart":"()=>!!document.getElementById('hlMt') && document.getElementById('hlMt').classList.contains('on')",
       "furn":"()=>document.getElementById('furnP').classList.contains('on')",
       "snack":"()=>!!document.getElementById('tfSn') && document.getElementById('tfSn').classList.contains('on')",
       "pet":"()=>!!document.getElementById('tfPt') && document.getElementById('tfPt').classList.contains('on')",
       "photo":"()=>!!document.getElementById('tfPh') && document.getElementById('tfPh').classList.contains('on')"}
DECO={"fish":["fish tank","net","life ring","barrel"],"clothes":["shirt","dress","mirror","shoes"],"mart":["apple","fridge","cart","watermelon"],
      "hair":["chair","mirror","barber pole","hair dryer"],"snack":["ice cream","menu","donut","table"],"furn":["sofa","lamp","bookshelf","table"],
      "pet":["puppy","cat","goldfish","bowl"],"photo":["camera","background","light","photo"]}
CLOSE="()=>{ try{ closeAv(); }catch(e){} SHEETS.forEach(id=>{ const el=document.getElementById(id); if(el) el.classList.remove('on'); }); }"

async def main():
    bad=[]; errs=[]
    only=[x for x in os.environ.get("ONLY","").split(",") if x]; shots=os.environ.get("SHOT","1")!="0"
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        async def until(pg, js, n=120):
            for _ in range(n):
                try:
                    if await pg.evaluate(js): return True
                except Exception: pass
                await pg.wait_for_timeout(250)
            return False
        async def open_pg(w,h):
            ctx=await br.new_context(viewport={"width":w,"height":h}, is_mobile=w<700, has_touch=True)
            pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
            await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html?isle=1"); await pg.wait_for_timeout(400)
            await pg.evaluate("()=>{ localStorage.setItem('hyeng_proto_code', JSON.stringify('SHOPI')); localStorage.setItem('hyeng_nick','루아'); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); }")
            await pg.reload(); await pg.wait_for_timeout(2500)
            await pg.evaluate("()=>{ gems=3000; saveBag(); try{ TECO.setCoin(3000); }catch(e){} }")
            await pg.evaluate("()=>HOUSE.exitRoom()")
            ok(await until(pg, "()=>HOUSE.place()==='isle' && !HOUSE.trip().busy && !HOUSE.hero().slide", 160), f"🏝 마을 ({w}×{h})")
            await pg.wait_for_timeout(800); return pg
        async def go_in(pg, k):
            await pg.evaluate("(k)=>{ const S=ISLE.SPOT.shops.find(s=>s.k===k), h=HOUSE.hero(); h.path=[]; h.g.position.set(S.door[0],0,S.door[1]); h.cx=Math.floor(S.door[0]); h.cz=Math.floor(S.door[1]); drawLabels(); LBL.find(l=>l.d.k===k).d.act(); }", k)
            return await until(pg, f"()=>HOUSE.place()==='shop' && SHOPIN.cur()==='{k}' && !HOUSE.trip().busy", 80)

        # ── 휴대폰: 8곳 모두 ──
        pg=await open_pg(390,844)
        for k in [x for x in DECO if not only or x in only]:
            ok(await go_in(pg, k), f"① {k}: 이름표 → 🏪 가게 안")
            r=await pg.evaluate("()=>{ const W=SHOPIN.words().map(w=>w.en); let draws=0; SHOPIN.deco().traverse(o=>{ if(o.isMesh) draws++; }); return [W, draws, !!SHOPIN.keeper(), SHOPIN.G.visible, ISLE.G.visible, document.getElementById('gShop').classList.contains('on'), LBL.map(l=>l.d.k)]; }")
            ok(all(w in r[0] for w in DECO[k]), f"① {k}: 가게 장식 {DECO[k]} ⊂ {r[0]}")
            ok(r[2] and r[3] and not r[4] and r[5], f"① {k}: 주인 · 가게 보임 · 섬 숨김 · 아래 단추 {r[2:6]}")
            ok(r[1]<=70, f"① {k}: 그리는 조각 적게 (합침) {r[1]}")
            ok("door" in r[6] and k in r[6], f"① {k}: 이름표 🚪 나가기 · 카운터 {r[6]}")
            # ② 인사 → 카운터 → 창
            ok(await until(pg, SHEET[k], 60), f"② {k}: 카운터까지 걸어가서 원래 가게 창")
            r=await pg.evaluate("()=>[HOUSE.hero().cx, HOUSE.hero().cz, document.getElementById('toast').innerText]")
            ok(r[0]==3 and r[1]==2 and "/" not in r[2] and len(r[2])>5, f"② {k}: 손님 자리 · 주인 인사 {r}")
            if shots and k in ("fish","pet"):
                await pg.screenshot(path=OUT+f"shopin572_phone_{k}_sheet.png")
            await pg.evaluate(CLOSE); await pg.wait_for_timeout(200)
            if shots:
                await pg.wait_for_timeout(300); await pg.screenshot(path=OUT+f"shopin572_phone_{k}.png")
            # ③ 주인 이름표 → 다시 창 · 물건 → 영어
            await pg.evaluate("(k)=>LBL.find(l=>l.d.k===k).d.act()", k)
            ok(await until(pg, SHEET[k], 30), f"③ {k}: 주인 이름표 → 다시 창")
            await pg.evaluate(CLOSE); await pg.wait_for_timeout(150)
            r=await pg.evaluate("""(en)=>{ const w=SHOPIN.words().find(w=>w.en===en); const c=w.box.getCenter(new THREE.Vector3()).project(HOUSE.camera); const x=(c.x+1)/2*innerWidth, y=(1-c.y)/2*innerHeight;
                const o={clientX:x, clientY:y}; SHOPIN.tap(o); return [Math.round(x), Math.round(y), document.getElementById('toast').innerText]; }""", DECO[k][0])
            ok(DECO[k][0] in r[2], f"③ {k}: 물건 누르면 영어 이름 {r}")
            # 바닥 누르면 걸어감
            await pg.evaluate("()=>{ const v=new THREE.Vector3(5.5,0,5.5).project(HOUSE.camera); SHOPIN.tap({clientX:(v.x+1)/2*innerWidth, clientY:(1-v.y)/2*innerHeight}); }")
            await pg.wait_for_timeout(200)
            # ④ 나가기
            await pg.evaluate("()=>document.getElementById('bSOut').click()")
            ok(await until(pg, "()=>HOUSE.place()==='isle' && !HOUSE.trip().busy && !HOUSE.hero().slide", 80), f"④ {k}: 🚪 나가기 → 🏝 마을")
            r=await pg.evaluate("(k)=>{ const S=ISLE.SPOT.shops.find(s=>s.k===k), h=HOUSE.hero().g.position; return [Math.hypot(h.x-S.door[0], h.z-S.door[1]), SHOPIN.deco()===null, SHOPIN.G.visible, ISLE.G.visible, document.getElementById('gShop').classList.contains('on'), document.body.classList.contains('isleOn')]; }", k)
            ok(r[0]<2.2 and r[1] and not r[2] and r[3] and not r[4] and r[5], f"④ {k}: 그 가게 문 앞 · 장식 버림 · 섬 화면 {r}")
        # 문 눌러서 나가기 · 지도로 다른 곳 가도 정리
        if not only:
            ok(await go_in(pg, "fish"), "④ 다시 🐟")
            await until(pg, SHEET["fish"], 40); await pg.evaluate(CLOSE)
            await pg.evaluate("()=>LBL.find(l=>l.d.k==='door').d.act()")
            ok(await until(pg, "()=>HOUSE.place()==='isle' && !HOUSE.trip().busy", 80), "④ 🚪 문 이름표로도 나감")
            ok(await go_in(pg, "mart"), "④ 다시 🛒")
            await until(pg, SHEET["mart"], 40); await pg.evaluate(CLOSE)
            await pg.evaluate("()=>{ visitFrom={key:'shop', at:[1,6]}; ISLE.enterHome(); }")   # 친구 집에 간 셈 (돌아올 곳 = 가게)
            ok(await until(pg, "()=>HOUSE.place()==='room' && !HOUSE.trip().busy", 80), "④ 가게에서 바로 집으로 (지도 등)")
            await pg.wait_for_timeout(300)
            r=await pg.evaluate("()=>{ const r=[SHOPIN.G.visible, SHOPIN.deco()===null, document.getElementById('gShop').classList.contains('on'), visitFrom && visitFrom.key]; visitFrom=null; return r; }")
            ok(r==[False,True,False,"isle"], f"④ 다른 곳으로 가면 가게 정리 · 친구 집에서 돌아올 곳 = 섬 {r}")
        await pg.context.close()
        # ── 패드 가로 · 세로 스크린샷 ──
        if shots:
            for (w,h,tag) in [(1180,820,"ipad"),(820,1180,"ipadp")]:
                pg=await open_pg(w,h)
                for k in ([x for x in DECO if not only or x in only] if tag=="ipad" else ["clothes"]):
                    ok(await go_in(pg, k), f"⑤ {tag} {k}: 가게 안")
                    await until(pg, SHEET[k], 60); await pg.evaluate(CLOSE); await pg.wait_for_timeout(500)
                    await pg.screenshot(path=OUT+f"shopin572_{tag}_{k}.png")
                    await pg.evaluate("()=>document.getElementById('bSOut').click()")
                    await until(pg, "()=>HOUSE.place()==='isle' && !HOUSE.trip().busy && !HOUSE.hero().slide", 80)
                await pg.context.close()
        await br.close()
    ok(not errs, f"오류 없음 {errs[:3]}")
    print("\nFAIL" if bad else "\nPASS", len(bad)); sys.exit(1 if bad else 0)

asyncio.run(main())
