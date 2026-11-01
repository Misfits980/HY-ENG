"""(v520·v521) 🏝 우리 마을 (진짜 3D · swiftshader)
   ① B 툰: 바깥 재질에 툰 표시 · 테두리 후처리 켜짐(?edge=1)
   ② 이름이 PLAYER 면 방 문을 나서도 마을에 못 들어감 (안내 창)
   ③ 이름이 있으면 🚪 → 🏝 우리 마을 · 내 집 문 앞 · 내 집 ⭐ · 걸을 수 있는 칸 1000개 넘음 · 물·집 칸은 막힘
   ④ 조이스틱으로 움직임 · 막힌 칸으로는 못 감 · 점프
   ⑤ 이름표: 내 집·시장·밭·학교·타워·광산 · 「내 집」 누르면 방으로
   ⑥ 마당(밭 섬)에서 「마을」 → 다시 🏝 · 오류 없음"""
import asyncio, sys, os
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

async def page(br, nick):
    ctx=await br.new_context(viewport={"width":390,"height":700}, is_mobile=True, has_touch=True)
    await ctx.add_init_script("(()=>{ try{ localStorage.setItem('hyeng_nick','"+nick+"'); }catch(e){} })();")
    pg=await ctx.new_page(); errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
    await pg.route("**/*", route); await pg.goto(ORIGIN+"proto/house.html?isle=1&edge=1"); await pg.wait_for_timeout(2500)
    await pg.evaluate("()=>{ Object.keys(localStorage).filter(k=>k.startsWith('hyeng_proto_')).forEach(k=>localStorage.removeItem(k)); }")
    await pg.reload(); await pg.wait_for_timeout(3000)
    await pg.evaluate("()=>{ const b=document.getElementById('coachSkip'); if(b) b.click(); }")
    return ctx, pg, errs

async def main():
    bad=[]; allerr=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        async def until(pg, js, n=160):
            for _ in range(n):
                if await pg.evaluate(js): return True
                await pg.wait_for_timeout(250)
            return False
        # ② PLAYER
        ctx, pg, errs = await page(br, "PLAYER")
        await pg.evaluate("()=>HOUSE.exitRoom()"); await until(pg, "()=>document.getElementById('info').classList.contains('on') || HOUSE.place()!=='room'", 120)
        r=await pg.evaluate("()=>[HOUSE.place(), document.getElementById('info').classList.contains('on'), document.getElementById('infoT').textContent]")
        print("PLAYER", r)
        ok(r[0]=="room" and r[1] and "이름" in r[2], "이름이 PLAYER 면 마을에 못 들어감 + 안내")
        allerr+=errs; await ctx.close()
        # ①③
        ctx, pg, errs = await page(br, "용현")
        r=await pg.evaluate("()=>[TOON.on, TOON.edge]")
        ok(r==[True, True], f"툰 · 테두리 켜짐 {r}")
        await pg.evaluate("()=>HOUSE.exitRoom()")
        ok(await until(pg, "()=>HOUSE.place()==='isle' && !HOUSE.trip().busy"), "🚪 → 🏝 우리 마을")
        await pg.wait_for_timeout(800)
        r=await pg.evaluate("""()=>{ let w=0; for(const v of ISLE.W) w+=v; const h=HOUSE.hero(), d=ISLE.doorCell(), m=ISLE.myHouse();
            let toon=0, mats=0; ISLE.G.traverse(o=>{ if(o.isMesh && o.material && o.material.isMeshStandardMaterial){ mats++; if(o.material.userData.toon) toon++; } });
            const sea=ISLE.blocked(Math.floor(ISLE.OX+9.5*ISLE.S), Math.floor(ISLE.OZ-0.8*ISLE.S));
            return {w, at:[h.cx,h.cz], d, hood:m&&m.hood, toon, mats, sea, edge:ISLE.blocked(2,2), star:!!ISLE.G.userData.star}; }""")
        print("마을", r)
        ok(r["w"]>1000, f"걸을 수 있는 칸 {r['w']}")
        ok(abs(r["at"][0]-r["d"][0])<=1 and abs(r["at"][1]-r["d"][1])<=1, f"내 집 문 앞에서 시작 {r['at']} {r['d']}")
        ok(r["hood"] in ("1동","2동","3동") and r["star"], f"내 집 = {r['hood']} ⭐")
        ok(r["sea"] and r["edge"], "호수·바다 칸은 막힘")
        ok(r["mats"]>0 and r["toon"]==r["mats"], f"마을 재질 모두 툰 {r['toon']}/{r['mats']}")
        # ④ 조이스틱
        await until(pg, "()=>!HOUSE.hero().slide")
        await pg.evaluate("()=>{ HOUSE.hero().g.position.set(ISLE.OX+0.5, 0, ISLE.OZ+4.6); }")   # 광장 남쪽 큰길
        a=await pg.evaluate("()=>{ const p=HOUSE.hero().g.position; return [p.x,p.z]; }")
        await pg.evaluate("()=>{ ISLE.J.x=0; ISLE.J.y=1; for(let i=0;i<20;i++) ISLE.tick(0.05); ISLE.J.y=0; ISLE.tick(0.05); }")
        b=await pg.evaluate("()=>{ const p=HOUSE.hero().g.position; return [p.x,p.z]; }")
        ok(abs(b[0]-a[0])+abs(b[1]-a[1])>1.0, f"조이스틱으로 움직임 {a} → {b}")
        r=await pg.evaluate("""()=>{ const h=HOUSE.hero(), p=h.g.position; p.set(ISLE.OX+4.5, 0, ISLE.OZ+0.5); const st=!ISLE.blocked(Math.floor(p.x), Math.floor(p.z)); let wet=false;
            for(const [jx,jy] of [[1,0],[1,-1],[1,1]]){ ISLE.J.x=jx; ISLE.J.y=jy; for(let i=0;i<160;i++){ ISLE.tick(0.05); if(ISLE.blocked(Math.floor(p.x), Math.floor(p.z))) wet=true; } }
            ISLE.J.x=0; ISLE.J.y=0; ISLE.tick(0.05); return st && !wet; }""")
        ok(r, "물로는 못 들어감 (늘 걸을 수 있는 칸)")
        r=await pg.evaluate("()=>{ const d=ISLE.doorCell(); HOUSE.hero().g.position.set(d[0]+.5,0,d[1]+.5); ISLE.J.air=false; document.getElementById('ijump').dispatchEvent(new PointerEvent('pointerdown',{bubbles:true})); for(let i=0;i<4;i++) ISLE.tick(0.05); const y=HOUSE.hero().g.position.y; for(let i=0;i<40;i++) ISLE.tick(0.05); return [y, HOUSE.hero().g.position.y]; }")
        ok(r[0]>0.3 and r[1]==0, f"점프 {r}")
        # ⑤ 이름표
        ks=await pg.evaluate("()=>LBL.map(L=>L.d.k)")
        ok(all(k in ks for k in ["home","mk","farm","school","tower","mine","lake"]), f"이름표 {ks}")
        vis=await pg.evaluate("()=>[getComputedStyle(document.getElementById('iUI')).display, getComputedStyle(document.getElementById('ijump')).display, document.getElementById('gIsle').classList.contains('on')]")
        ok(vis[0]!="none" and vis[1]!="none" and vis[2], f"조이스틱·점프·아래 단추 보임 {vis}")
        await pg.evaluate("()=>{ const d=ISLE.doorCell(); const h=HOUSE.hero(); h.g.position.set(d[0]+.5,0,d[1]+.5); h.cx=d[0]; h.cz=d[1]; const L=LBL.find(L=>L.d.k==='home'); L.d.act(); }")
        ok(await until(pg, "()=>HOUSE.place()==='room' && !HOUSE.trip().busy"), "⭐ 내 집 → 방")
        vis=await pg.evaluate("()=>getComputedStyle(document.getElementById('iUI')).display")
        ok(vis=="none", "방에서는 조이스틱 숨김")
        # ⑥ 밭 섬 → 마당 → 다시 섬
        await pg.evaluate("()=>HOUSE.exitRoom()"); await until(pg, "()=>HOUSE.place()==='isle' && !HOUSE.trip().busy")
        await pg.evaluate("()=>{ const L=LBL.find(L=>L.d.k==='farm'); L.d.act(); }")
        ok(await until(pg, "()=>HOUSE.place()==='yard' && !HOUSE.trip().busy"), "🌱 밭 섬 → 내 마당")
        await pg.evaluate("()=>HOUSE.yardToVillage()")
        ok(await until(pg, "()=>HOUSE.place()==='isle' && !HOUSE.trip().busy"), "마당 「마을」 → 🏝")
        r=await pg.evaluate("()=>{ const h=HOUSE.hero(); return !ISLE.blocked(h.cx,h.cz) && Math.hypot(h.cx-ISLE.SPOT.farm[0], h.cz-ISLE.SPOT.farm[2])<9; }")
        ok(r, "밭 섬 근처로 돌아옴")
        allerr+=errs; await ctx.close()
        await br.close()
    e=real_errs(allerr)
    ok(not e, f"오류 없음 {e[:3]}")
    print("\nFAIL" if bad else "\nPASS", len(bad)); sys.exit(1 if bad else 0)

asyncio.run(main())
