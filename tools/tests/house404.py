"""(v404) 🏡 생활 모드 맛보기 (proto/house.html) — 진짜 3D(swiftshader)
  ① 집: 가구 6개 · 뒤쪽 벽 2개 · 내 아바타 · 누른 칸까지 걸어감(가구 피함) · 가구 놓기/창고 넣기
  ② 마당: 연못을 누르면 연못 옆으로 걸어가 찌를 던짐 → 입질 → 톡 → 잡음(영어 이름만 · 문제 없음) → 물고기 도감 +1 · 미끼 −1
     (사용자: 영어 문제로 묶지 말고 아이템 이름을 영어로만 — 가구·도감·꾸미기 이름 영어)
  ③ 입질 전에 톡 = 미끼 돌려받고 끝 · 입질 뒤 늦으면 놓침 · 미끼 0 이면 못 던짐
  ④ 나 꾸미기: 모자 바꾸면 저장되고 새로 열어도 그대로
  ⑤ 가로 화면에서도 방이 화면 안 · 오류 없음"""
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
        await pg.evaluate("()=>{ localStorage.removeItem('hyeng_proto_av'); localStorage.removeItem('hyeng_proto_fish'); localStorage.removeItem('hyeng_proto_bait'); }")
        await pg.reload(); await pg.wait_for_timeout(2500)
        async def arrive():
            for _ in range(80):
                if not await pg.evaluate("()=>HOUSE.hero().moving"): return
                await pg.wait_for_timeout(250)
        async def until(js, n=80):
            for _ in range(n):
                if await pg.evaluate(js): return True
                await pg.wait_for_timeout(250)
            return False
        # ① 집
        st=await pg.evaluate("()=>({n:HOUSE.placed.length, place:HOUSE.place(), av:!!HOUSE.hero().head, legs:!!HOUSE.hero().legL})")
        ok(st["n"]==6 and st["place"]=="room" and st["av"] and st["legs"], f"집 · 가구 6 · 아바타 {st}")
        wv=await pg.evaluate("()=>HOUSE.scene.children.filter(c=>c.type==='Group')[0].children.filter(c=>c.userData.normal).map(w=>w.visible)")
        ok(wv.count(True)==2, f"벽 2개만 보임 {wv}")
        await pg.evaluate("()=>HOUSE.walkTo(5,5)"); await arrive()
        ok(await pg.evaluate("()=>[HOUSE.hero().cx,HOUSE.hero().cz]")==[5,5], "누른 칸까지 걸어감")
        path=await pg.evaluate("()=>HOUSE.findPath(5,5,1,1)")
        clash=await pg.evaluate("(P)=>P.some(([x,z])=>HOUSE.placed.some(p=>{ if(HOUSE.ITEMS[p.id].rug) return false; const s=HOUSE.ITEMS[p.id].sz, w=p.r%2?s[1]:s[0], d=p.r%2?s[0]:s[1]; return p.x<=x && x<p.x+w && p.z<=z && z<p.z+d; }))", path or [])
        ok(path and not clash, f"길은 가구 칸을 피함 {path}")
        await pg.click("#bEdit"); await pg.wait_for_timeout(300)
        await pg.click('.card[data-id="sofa"]'); await pg.wait_for_timeout(300); await pg.click("#pOk"); await pg.wait_for_timeout(300)
        ok(await pg.evaluate("()=>HOUSE.stock.sofa===0 && HOUSE.placed.length===7"), "소파 놓기")
        ok(not await pg.evaluate("()=>HOUSE.fits('sofa',0,0,0)") and await pg.evaluate("()=>HOUSE.fits('chair',2,2,0)"), "침대 자리엔 못 놓음 · 러그 위엔 놓음")
        names=await pg.evaluate("()=>[...document.querySelectorAll('#inv .card span')].map(e=>e.innerText)")
        ok(names and all(not any('가'<=ch<='힣' for ch in n) for n in names), f"창고 가구 이름 = 영어 {names}")
        await pg.click("#bDone"); await pg.wait_for_timeout(300)
        # ② 마당 · 낚시
        await pg.click("#bOut"); await pg.wait_for_timeout(800)
        ok(await pg.evaluate("()=>HOUSE.place()")=="yard", "🚪 → 마당")
        ok(await pg.evaluate("()=>HOUSE.findPath(HOUSE.hero().cx,HOUSE.hero().cz,7,6)")==None, "연못 칸으로는 못 걸어감")
        b0=await pg.evaluate("()=>HOUSE.bait()")
        await pg.evaluate("()=>HOUSE.tryFish(7,6)")
        ok(await until("()=>HOUSE.F.st==='wait'"), "연못 옆까지 걸어가 찌를 던짐")
        nx=await pg.evaluate("()=>{ const h=HOUSE.hero(); return [[1,0],[-1,0],[0,1],[0,-1],[1,1],[1,-1],[-1,1],[-1,-1]].some(([a,b])=>{ const x=h.cx+a, z=h.cz+b; return x>=6&&x<=8&&z>=5&&z<=7; }); }")
        ok(nx and await pg.evaluate("()=>HOUSE.bait()")==b0-1, f"연못 바로 옆 · 미끼 {b0}→{b0-1}")
        await pg.evaluate("()=>HOUSE.bite()"); await pg.wait_for_timeout(100)
        ok(await pg.evaluate("()=>document.getElementById('bang').classList.contains('on')"), "입질 → ! 표시")
        await pg.evaluate("()=>HOUSE.tapWhileFishing()")
        ok(await until("()=>document.getElementById('quiz').classList.contains('on')", 20), "톡 → 잡음 카드")
        q=await pg.evaluate("()=>({fish:HOUSE.F.fish.en, name:document.getElementById('qAsk').innerText.trim(), ko:/[가-힣]/.test(document.getElementById('quiz').innerText.replace('🆕','')), opts:document.querySelectorAll('#qOpts button[data-en]').length})")
        ok(q["name"]==q["fish"] and not q["ko"] and q["opts"]==0, f"문제 없이 영어 이름만 (한국어 없음) {q}")
        ok(await pg.evaluate("(f)=>HOUSE.dex()[f]===1", q["fish"]), "잡으면 바로 도감 +1")
        await pg.click("#qOk"); await pg.wait_for_timeout(200)
        await until("()=>HOUSE.F.st==='idle'", 20)
        # ③ 일찍 누름 = 미끼 돌려받음 · 늦으면 놓침 · 미끼 0
        b1=await pg.evaluate("()=>HOUSE.bait()")
        await pg.evaluate("()=>HOUSE.tryFish(7,6)"); await until("()=>HOUSE.F.st==='wait'")
        await pg.evaluate("()=>{ HOUSE.F.nib=[]; HOUSE.F.T=99; }"); await pg.wait_for_timeout(100)
        await pg.evaluate("()=>HOUSE.tapWhileFishing()")
        ok(await pg.evaluate("()=>HOUSE.F.st")=="idle" and await pg.evaluate("()=>HOUSE.bait()")==b1, "입질 전 톡 → 끝 · 미끼 돌려받음")
        await pg.evaluate("()=>HOUSE.tryFish(7,6)"); await until("()=>HOUSE.F.st==='wait'")
        await pg.evaluate("()=>HOUSE.bite()"); ok(await until("()=>HOUSE.F.st==='idle'", 12), "입질 뒤 1초 넘게 안 누르면 놓침")
        ok(await pg.evaluate("()=>HOUSE.bait()")==b1-1, "놓쳐도 미끼는 씀")
        await pg.evaluate("()=>HOUSE.setBait(0)"); await pg.evaluate("()=>HOUSE.tryFish(7,6)"); await pg.wait_for_timeout(300)
        ok(await pg.evaluate("()=>HOUSE.F.st")=="idle" and "미끼" in await pg.evaluate("()=>document.getElementById('toast').innerText"), "미끼 0 → 못 던지고 안내")
        await pg.screenshot(path=OUT+"life_yard.png")
        # ④ 나 꾸미기
        await pg.click("#bAv2"); await pg.wait_for_timeout(500)
        await pg.click('.chip[data-k="hat"][data-v="cap"]'); await pg.wait_for_timeout(300)
        ok(await pg.evaluate("()=>HOUSE.av().hat")=="cap", "모자 바꾸기")
        await pg.screenshot(path=OUT+"life_av.png")
        await pg.click("#avDone"); await pg.reload(); await pg.wait_for_timeout(2500)
        ok(await pg.evaluate("()=>HOUSE.av().hat")=="cap" and await pg.evaluate("(f)=>HOUSE.dex()[f]===1", q["fish"]), "새로 열어도 모자·도감 그대로")
        # ⑤ 가로
        await pg.set_viewport_size({"width":844,"height":390}); await pg.wait_for_timeout(1000)
        inb=await pg.evaluate("()=>{ let ok=true; for(const x of [0,6]) for(const z of [0,6]){ const v=new THREE.Vector3(x,0,z).project(HOUSE.camera); if(Math.abs(v.x)>1||Math.abs(v.y)>1) ok=false; } return ok; }")
        ok(inb, "가로 화면에서도 방 네 귀퉁이가 화면 안")
        e=real_errs(errs); ok(not e, "오류 없음 "+str(e[:2]))
        await br.close()
    print("DONE bad=%d"%len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
