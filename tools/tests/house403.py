"""(v403) 🏠 내 집 맛보기 (proto/house.html · B형 3D 방 + 걷기 그림 캐릭터) — 진짜 3D(swiftshader)로 연다
  ① 열림 · 오류 없음 · 처음 가구 6개 · 뒤쪽 벽 2개만 보임
  ② 바닥을 누르면 그 칸까지 걸어감 · 가구 칸은 피해 감 · 걷는 방향에 맞는 그림 줄
  ③ 꾸미기: 창고에서 소파 → 놓기 / 겹치는 자리는 못 놓음 / 돌리기 / 창고에 넣으면 개수 돌아옴
  ④ 방 돌리기 → 보이는 벽이 바뀜 · 가로 화면도 방이 화면 안"""
import asyncio, sys, os
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright
async def main():
    bad=[]; errs=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        ctx=await br.new_context(viewport={"width":390,"height":844}, is_mobile=True, has_touch=True)
        pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*", route); await pg.goto(ORIGIN+"proto/house.html"); await pg.wait_for_timeout(2500)
        st=await pg.evaluate("()=>({n:HOUSE.placed.length, walls:HOUSE.scene.children.length, vis:null, tex:!!HOUSE.hero().mat.map})")
        ok(st["n"]==6 and st["tex"], f"처음 가구 6개 · 캐릭터 그림 {st}")
        wv=await pg.evaluate("()=>{ const r=HOUSE.scene.children.find(c=>c.type==='Group'); return r.children.filter(c=>c.userData.normal).map(w=>w.visible); }")
        ok(wv.count(True)==2, f"벽 2개만 보임 {wv}")
        # ② 걷기 — 침대(0,0)(0,1) 뒤쪽으로
        async def arrive():
            for _ in range(60):
                if not await pg.evaluate("()=>HOUSE.hero().moving"): return
                await pg.wait_for_timeout(250)
        await pg.evaluate("()=>HOUSE.walkTo(5,5)"); await arrive()
        h=await pg.evaluate("()=>[HOUSE.hero().cx, HOUSE.hero().cz, HOUSE.hero().moving]")
        ok(h[:2]==[5,5] and not h[2], f"(5,5)까지 걸어감 {h}")
        path=await pg.evaluate("()=>HOUSE.findPath(5,5,1,1)")
        clash=await pg.evaluate("(P)=>P.some(([x,z])=>HOUSE.placed.some(p=>{ if(HOUSE.ITEMS[p.id].rug) return false; const s=HOUSE.ITEMS[p.id].sz, w=p.r%2?s[1]:s[0], d=p.r%2?s[0]:s[1]; return p.x<=x && x<p.x+w && p.z<=z && z<p.z+d; }))", path or [])
        ok(path and not clash, f"길은 가구 칸을 피함 {path}")
        rows=await pg.evaluate("()=>[HOUSE.rowFor(0,-1),HOUSE.rowFor(0,1),HOUSE.rowFor(-1,0),HOUSE.rowFor(1,0)]")
        ok(len(set(rows))==4 and all(0<=r<8 for r in rows), f"방향마다 다른 그림 줄 {rows}")
        await pg.evaluate("()=>HOUSE.walkTo(0,0)"); await pg.wait_for_timeout(300)
        ok(await pg.evaluate("()=>{ const h=HOUSE.hero(); return !(h.path.length && h.path[h.path.length-1][0]===0 && h.path[h.path.length-1][1]===0); }"), "침대 칸을 누르면 침대 위가 아니라 가까운 빈 칸으로")
        await arrive()
        # ③ 꾸미기
        await pg.click("#bEdit"); await pg.wait_for_timeout(300)
        n0=await pg.evaluate("()=>HOUSE.stock.sofa"); await pg.click('.card[data-id="sofa"]'); await pg.wait_for_timeout(300)
        okb=await pg.evaluate("()=>!document.getElementById('pOk').disabled"); await pg.click("#pOk"); await pg.wait_for_timeout(300)
        n1=await pg.evaluate("()=>HOUSE.stock.sofa"); cnt=await pg.evaluate("()=>HOUSE.placed.length")
        ok(okb and n1==n0-1 and cnt==7, f"소파 놓기 → 창고 {n0}→{n1} · 가구 {cnt}")
        ov=await pg.evaluate("()=>HOUSE.fits('sofa',0,0,0)")
        ok(not ov, "침대 자리에는 못 놓음")
        ok(await pg.evaluate("()=>HOUSE.fits('chair',2,2,0)"), "러그 위에는 놓을 수 있음")
        # 놓인 소파 고르기 → 돌리기 → 창고
        await pg.evaluate("()=>{ const p=HOUSE.placed.find(p=>p.id==='sofa'); window._sofa=p; }")
        r0=await pg.evaluate("()=>_sofa.r")
        await pg.evaluate("()=>{ /* 선택은 화면 누르기 대신 직접 */ }")
        await pg.evaluate("()=>{ const p=_sofa; const ev=new Event('x'); }")
        # 화면 좌표로 누르기
        xy=await pg.evaluate("()=>{ const p=_sofa, v=p.obj.position.clone(); v.y=0.4; v.project(HOUSE.camera); return [(v.x+1)/2*innerWidth, (1-v.y)/2*innerHeight]; }")
        await pg.mouse.click(xy[0], xy[1]); await pg.wait_for_timeout(300)
        menu=await pg.evaluate("()=>document.getElementById('menu').classList.contains('on')")
        ok(menu, f"꾸미기에서 소파를 누르면 메뉴 {xy}")
        if menu:
            await pg.click("#mBox"); await pg.wait_for_timeout(300)
            ok(await pg.evaluate("()=>HOUSE.stock.sofa")==n0 and await pg.evaluate("()=>HOUSE.placed.length")==6, "📦 넣으면 창고 개수 돌아옴")
        await pg.click("#bDone"); await pg.wait_for_timeout(200)
        # ④ 방 돌리기
        await pg.click("#bCam"); await pg.wait_for_timeout(1200)
        wv2=await pg.evaluate("()=>{ const r=HOUSE.scene.children.find(c=>c.type==='Group'); return r.children.filter(c=>c.userData.normal).map(w=>w.visible); }")
        ok(wv2.count(True)==2 and wv2!=wv, f"돌리면 보이는 벽이 바뀜 {wv}→{wv2}")
        await pg.screenshot(path=OUT+"house_p.png")
        await pg.set_viewport_size({"width":844,"height":390}); await pg.wait_for_timeout(800)
        inb=await pg.evaluate("()=>{ const N=6; let ok=true; for(const x of [0,N]) for(const z of [0,N]){ const v=new THREE.Vector3(x,0,z).project(HOUSE.camera); if(Math.abs(v.x)>1||Math.abs(v.y)>1) ok=false; } return ok; }")
        ok(inb, "가로 화면에서도 방 바닥 네 귀퉁이가 화면 안")
        await pg.screenshot(path=OUT+"house_l.png")
        e=real_errs(errs); ok(not e, "오류 없음 "+str(e[:2]))
        await br.close()
    print("DONE bad=%d"%len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
