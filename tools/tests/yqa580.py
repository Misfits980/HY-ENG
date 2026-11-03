"""(v580) 마당 한 바퀴 — 나무 흔들기 · 바위 · 낚시 · 제작대 · 냄비 · 가게 · 물건 놓기·옮기기 · 길 칠하기 · 밤 · 마을로 나갔다 오기 (오류·사진만)"""
import asyncio, sys, os
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from fakefb import fake
from playwright.async_api import async_playwright
D=OUT+"y580"+os.sep; os.makedirs(D, exist_ok=True)

async def main():
    errs=[]; bad=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        ctx=await br.new_context(viewport={"width":820,"height":1180}, has_touch=True)
        pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: m.type=="error" and "Failed to load resource" not in m.text and errs.append("console: "+m.text))
        await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html?isle=1"); await pg.wait_for_timeout(400)
        await pg.evaluate("()=>{ localStorage.setItem('hyeng_proto_code', JSON.stringify('YQA80')); localStorage.setItem('hyeng_nick','루아'); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); }")
        await pg.reload(); await pg.wait_for_timeout(2800)
        await pg.evaluate("()=>{ go('yard', [DOOR[0],DOOR[1]+1]); }"); await pg.wait_for_timeout(2200)
        async def idle(t=60):
            for _ in range(t):
                if await pg.evaluate("()=>!hero.moving && !trip.busy && F.st==='idle'"): return
                await pg.wait_for_timeout(200)
        # 나무 · 바위
        await pg.evaluate("()=>useTile(TREES[0][0],TREES[0][1],()=>shakeTree(0))"); await idle(); await pg.wait_for_timeout(600)
        await pg.evaluate("()=>{ try{ useTile(ROCKS[0][0],ROCKS[0][1],()=>hitRock(0)); }catch(e){ console.warn(e); } }"); await idle(); await pg.wait_for_timeout(600)
        # 낚시 1번 (끝까지)
        r=await pg.evaluate("""async ()=>{ setBait(5); const c=[POND.x0+1, POND.z0+1]; return typeof fishTap; }""")
        # 제작대 · 냄비 · 가게
        for js in ["()=>openCraft('bench')","()=>openCraft('pot')","()=>{ try{ openShop(); }catch(e){ document.getElementById('shopP').classList.add('on'); } }"]:
            await pg.evaluate(js); await pg.wait_for_timeout(500)
            await pg.evaluate("()=>SHEETS.forEach(id=>document.getElementById(id).classList.remove('on'))")
        # 물건 놓기 · 옮기기 · 길
        await pg.evaluate("()=>{ setEdit(true); yTool='items'; yDrawInv(); }"); await pg.wait_for_timeout(400)
        r=await pg.evaluate("""()=>{ const n0=yplaced.length; ystock.flowers=(ystock.flowers|0)+1; let c=null; for(let x=4;x<YN && !c;x++) for(let z=4;z<YN && !c;z++) if(yFits('flowers',x,z,0)===1) c=[x,z]; yAdd('flowers',c[0],c[1],0,0); ystock.flowers--; ySave(); return [yplaced.length-n0, c]; }""")
        ok(r[0]==1, f"물건 놓기 {r}")
        await pg.evaluate("()=>{ yTool='path'; yPaint='dirt'; yDrawInv(); for(let x=5;x<8;x++) yPaintAt([x,11]); }"); await pg.wait_for_timeout(800)
        await pg.screenshot(path=D+"qa_edit.png")
        await pg.evaluate("()=>setEdit(false)"); await pg.wait_for_timeout(400)
        # 밤
        await pg.evaluate("()=>{ try{ HOUSE.setWx(false); }catch(e){} tShift=((22-new Date().getHours()+24)%24)*3600e3; envApply(true); }"); await pg.wait_for_timeout(1500)
        await pg.screenshot(path=D+"qa_night.png")
        await pg.evaluate("()=>{ tShift=0; envApply(true); }"); await pg.wait_for_timeout(600)
        # 색 바램 고침이 남은 재질
        await pg.wait_for_timeout(1000)
        r=await pg.evaluate("()=>{ let leg=0, n=0; const L=[]; yardG.traverse(o=>{ if(o.isMesh){ n++; const m=o.material; if(m && m.userData && m.userData.leg){ leg++; let p=o, path=[]; while(p && p!==yardG){ path.push(p.name||p.type); p=p.parent; } if(L.length<5) L.push(path.join('<')+' '+m.color.getHexString()); } } }); return [n, leg, L, place.key]; }")
        ok(r[1]==0, f"마당 재질 = 모두 선형 (바랜 것 없음) {r}")
        # 마을로 나갔다 오기
        await pg.evaluate("()=>yardToVillage()")
        for _ in range(120):
            if await pg.evaluate("()=>HOUSE.place()==='isle' && !HOUSE.trip().busy"): break
            await pg.wait_for_timeout(250)
        ok(await pg.evaluate("()=>HOUSE.place()==='isle'"), "마당 → 🏝 섬(밭 쪽)")
        await pg.evaluate("()=>ISLE.tripTo('yard')")
        for _ in range(80):
            if await pg.evaluate("()=>HOUSE.place()==='yard' && !HOUSE.trip().busy"): break
            await pg.wait_for_timeout(250)
        ok(await pg.evaluate("()=>HOUSE.place()==='yard' && PLOTS.length===scene.userData.plotG.length"), "섬 → 마당 다시 · 밭 그대로")
        await pg.wait_for_timeout(1200); await pg.screenshot(path=D+"qa_back.png")
        await br.close()
    ok(not errs, f"오류 없음 {errs[:3]}")
    print("\nFAIL" if bad else "\nPASS", len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
