"""(v571) 사용자: 「다시 집어넣는 기능 — 아이들이 언제든지 꾸미고 뺄 수 있게」 · 「상점·은행 … 이쁘게 · 차이점이 없어」
   ① 가구 메뉴 = 글자 붙은 단추(↻ 돌리기 · ✋ 옮기기 · 🎨 색 · 📦 넣기) · 📦 넣기 → 창고 +1
   ② 창고 줄 = 「👆 놓인 가구를 누르면 📦 넣기」 안내 + 🧹 이 방 다 넣기(확인 → 계단·옆방 문은 그대로)
   ③ 섬: 가게 8곳마다 장식(차양·지붕 상징물·문 옆 소품) · 🏦 은행 건물"""
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
        ctx=await br.new_context(viewport={"width":390,"height":844}, is_mobile=True, has_touch=True)
        pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html?isle=1"); await pg.wait_for_timeout(400)
        await pg.evaluate("()=>{ localStorage.setItem('hyeng_proto_code', JSON.stringify('DECOK')); localStorage.setItem('hyeng_nick','루아'); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); }")
        await pg.reload(); await pg.wait_for_timeout(2800)
        await pg.evaluate("()=>{ ['lamp','plant','chair'].forEach(id=>addStock(id)); setEdit(true); ['lamp','plant','chair'].forEach(id=>{ const f=firstFree(id,0); if(f){ addPlaced(id,f[0],f[1],0,0); stock[id]--; } }); addStock('stairs'); { const f=firstFree('stairs',0); if(f){ addPlaced('stairs',f[0],f[1],0,0); stock.stairs--; } } drawInv(); }")
        await pg.wait_for_timeout(300)
        r=await pg.evaluate("()=>{ selectP(placed.find(p=>p.id==='lamp')); const m=document.getElementById('menu'); return [m.classList.contains('on'), m.innerText.replace(/\\s+/g,' ')]; }")
        ok(r[0] and "넣기" in r[1] and "돌리기" in r[1] and "옮기기" in r[1], f"① 가구 메뉴에 글자 (돌리기·옮기기·색·넣기) {r}")
        await pg.screenshot(path=OUT+"deco571_menu.png")
        r=await pg.evaluate("()=>{ const s0=stock.lamp|0; document.getElementById('mBox').click(); return [(stock.lamp|0)-s0, placed.some(p=>p.id==='lamp')]; }")
        ok(r==[1,False], f"① 📦 넣기 → 창고 +1 · 방에서 빠짐 {r}")
        t=await pg.evaluate("()=>document.getElementById('inv').innerText")
        ok("놓인 가구를 누르면" in t and "다 넣기" in t, f"② 창고 줄 = 넣기 안내 + 🧹 이 방 다 넣기 {t[-60:]!r}")
        await pg.evaluate("()=>document.querySelector('#inv [data-allin]').click()"); await pg.wait_for_timeout(200)
        ok(await pg.evaluate("()=>document.getElementById('ask').classList.contains('on')"), "② 다 넣기 = 먼저 「넣을까요?」")
        await pg.evaluate("()=>document.getElementById('askOk').click()"); await pg.wait_for_timeout(300)
        r=await pg.evaluate("()=>[placed.map(p=>p.id), stock.plant|0, stock.chair|0, stock.bed|0]")
        ok(r[0]==["stairs"] and r[1]>=1 and r[2]>=1 and r[3]>=1, f"② 다 넣기 → 계단만 남고 나머지 창고로 {r}")
        await pg.screenshot(path=OUT+"deco571_inv.png")
        # ③ 섬 장식
        await pg.evaluate("()=>{ setEdit(false); HOUSE.exitRoom(); }")
        for _ in range(160):
            if await pg.evaluate("()=>HOUSE.place()==='isle' && !HOUSE.trip().busy"): break
            await pg.wait_for_timeout(250)
        r=await pg.evaluate("()=>{ let deco=0, bank=0; ISLE.G.traverse(o=>{ if(o.isGroup && o.children.length>=6 && o.children.some(c=>c.geometry && c.geometry.type==='BoxGeometry' && Math.abs(c.position.y-2.15)<.05)) deco++; if(o.userData && o.userData.fac==='bank') bank++; }); return [deco, bank, (ISLE.SPOT.shops||[]).length]; }")
        ok(r[0]>=8 and r[1]==1, f"③ 가게 장식 8곳 이상 · 🏦 은행 건물 {r}")
        await br.close()
    ok(not errs, f"오류 없음 {errs[:2]}")
    print("\nFAIL" if bad else "\nPASS", len(bad)); sys.exit(1 if bad else 0)

asyncio.run(main())
