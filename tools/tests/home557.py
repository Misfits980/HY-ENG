"""(v557) 🛋 가구점 새 가구 · 🚪 옆방 문 (가짜 서버 · 아이 2명)
   ① 가구점: 새 가구 36가지 + 칸(✨ 새 가구·놀이·식물·취미·부엌·욕실·계절) · 💎로 사면 창고 · NEW 표시
   ② 🏗 「🚪 옆방 문」 💎50 → 창고 · 벽에 달 때 문 앞 칸이 막혀 있으면 못 담 · 달면 옆방 번호 1
   ③ 문을 누르면 옆방(새 방) · 가구 놓고 나오면 1층 문 앞 · 새로 고침해도 옆방 가구 그대로
   ④ 옆방 문을 창고에 넣었다 다시 달면 예전 옆방 그대로 (가구 안 잃음) · 두 번째 문 = 옆방 2
   ⑤ 옆방에서 🪜 계단 = 2층 (층은 1층 기준) · 친구가 놀러 와서 옆방까지 구경 · 오류 없음"""
import asyncio, sys, os, json
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from fakefb import fake, DB
from playwright.async_api import async_playwright

async def main():
    bad=[]; errs=[]
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
        async def kid(code,name):
            ctx=await br.new_context(viewport={"width":390,"height":760}, is_mobile=True, has_touch=True)
            pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(name+": "+str(e)))
            await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html"); await pg.wait_for_timeout(500)
            await pg.evaluate("""([c,n])=>{ Object.keys(localStorage).filter(k=>k.startsWith('hyeng_')).forEach(k=>localStorage.removeItem(k)); localStorage.setItem('hyeng_proto_code', JSON.stringify(c)); localStorage.setItem('hyeng_nick', n); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99}));
                localStorage.setItem('hyeng_study_v1', JSON.stringify({days:{n:8,tot:9,hs:8,hb:8,last:Math.floor((Date.now()-new Date().getTimezoneOffset()*60000)/864e5)}})); }""", [code,name])
            await pg.reload(); await pg.wait_for_timeout(2200); return pg
        A=await kid("AAAAA","루아")
        await A.evaluate("()=>{ gems=1000; saveBag(); TECO.setCoin(20000); }")
        # ① 가구점
        await A.evaluate("()=>openFurn('furn')"); await A.wait_for_timeout(300)
        r=await A.evaluate("()=>[Object.keys(NEWF).length, [...document.querySelectorAll('#furnBody [data-fc]')].map(b=>b.dataset.fc)]")
        ok(r[0]>=36 and all(k in r[1] for k in ("new","play","plant","hobby","kb","season")), f"① 새 가구 {r[0]}가지 · 칸 {r[1]}")
        await A.evaluate("()=>document.querySelector('[data-fc=play]').click()"); await A.wait_for_timeout(200)
        r=await A.evaluate("()=>[...document.querySelectorAll('#furnBody [data-bf]')].map(b=>b.dataset.bf)")
        ok("arcade" in r and "teepee" in r and "bed" not in r, f"① 🧸 놀이 칸 {r}")
        ok(await A.evaluate("()=>/NEW/.test(document.getElementById('furnBody').innerText)"), "① NEW 표시")
        await A.evaluate("()=>document.querySelector('#furnBody [data-bf=teepee]').click()"); await A.wait_for_timeout(200)
        ok(await A.evaluate("()=>(stock.teepee|0)===0 && /살까요/.test(document.getElementById('askT').innerText)"), "① (v561) 사기 전에 「살까요?」")
        await A.click('#askOk'); await A.wait_for_timeout(200)
        ok(await A.evaluate("()=>(stock.teepee|0)===1 && HOUSE.gems()===1000-furnCO('teepee').g"), "① ⛺ 사면 창고 · 💎+🪙")
        await A.evaluate("()=>document.getElementById('furnP').classList.remove('on')")
        # 새 가구는 모두 지어짐 (빌드 오류 없음)
        r=await A.evaluate("()=>Object.keys(NEWF).filter(id=>{ try{ const o=ITEMS[id].build(0); return !o || !o.children.length; }catch(e){ return true; } })")
        ok(r==[], f"① 새 가구 모양 다 만들어짐 {r}")
        # ② 옆방 문
        await A.evaluate("()=>{ HOMEX.openUp(); }"); await A.wait_for_timeout(200)
        ok(await A.evaluate("()=>!!document.querySelector('[data-up=door]')"), "② 🏗 「🚪 옆방 문」 사기")
        await A.evaluate("()=>{ document.querySelector('[data-up=door]').click(); }"); await A.wait_for_timeout(200); await A.evaluate("()=>document.getElementById('askOk').click()"); await A.wait_for_timeout(300)
        g1=await A.evaluate("()=>HOUSE.gems()")
        ok(await A.evaluate("()=>(stock.sidedoor|0)===1"), "② 💎50 → 🚪 창고")
        await A.evaluate("()=>document.getElementById('upP').classList.remove('on')")
        r=await A.evaluate("()=>{ addPlaced('stool',3,0,0); const a=wallOk('sidedoor',0,3); const b=wallOk('sidedoor',0,1); return [a,b]; }")
        ok(r==[False,True], f"② 문 앞 칸에 가구가 있으면 못 담 · 빈 칸은 됨 {r}")
        await A.evaluate("()=>{ edit=true; startGhost('sidedoor'); ghost.side=0; ghost.s=1; okGhost(); edit=false; }"); await A.wait_for_timeout(400)
        r=await A.evaluate("()=>{ const w=wplaced.find(w=>w.id==='sidedoor'); return [w && w.c, JSON.stringify(HOMEX.H().ax), stock.sidedoor|0, !!LBL.find(l=>l.d.k==='sd_1'), !fits('stool',1,0,0)]; }")
        ok(r[0]==1 and "living" in r[1] and r[2]==0 and r[3] and r[4], f"② 벽에 달면 옆방 1 · 이름표 · 문 앞 칸 비움 {r}")
        # ③ 옆방
        await A.evaluate("()=>useItem(wplaced.find(w=>w.id==='sidedoor'))")
        ok(await until(A, "()=>HOMEX.cur()==='a1' && !HOUSE.trip().busy && HOUSE.place()==='room'", 80), "③ 문 → 옆방 1")
        r=await A.evaluate("()=>[RN, placed.length, PL.room.name, LBL.find(l=>l.d.k==='door').d.t]")
        ok(r[0]==6 and r[1]==0 and "옆방" in r[2] and "거실로" in r[3], f"③ 새 방 6×6 · 비어 있음 · 문 = 거실로 돌아가기 {r}")
        await A.evaluate("()=>{ addPlaced('teepee',1,1,0,0); stock.teepee--; HOMEX.grow('r'); saveRoom(); }")
        ok(await A.evaluate("()=>RN===8 && placed.some(p=>p.id==='teepee')"), "③ 옆방도 넓히기 · 꾸미기")
        await A.evaluate("()=>HOUSE.exitRoom()")
        ok(await until(A, "()=>HOMEX.cur()==='living' && !HOUSE.trip().busy", 80), "③ 나오면 1층")
        r=await A.evaluate("()=>{ const w=wplaced.find(w=>w.id==='sidedoor'); return [HOUSE.hero().cx, HOUSE.hero().cz, w.s]; }")
        ok(r[0]==r[2] and r[1]==0, f"③ 1층 옆방 문 앞에 섬 {r}")
        await A.reload(); await A.wait_for_timeout(2200)
        await A.evaluate("()=>useItem(wplaced.find(w=>w.id==='sidedoor'))")
        ok(await until(A, "()=>HOMEX.cur()==='a1' && !HOUSE.trip().busy", 80) and await A.evaluate("()=>RN===8 && placed.some(p=>p.id==='teepee')"), "③ 새로 고침해도 옆방 가구 그대로")
        await A.evaluate("()=>HOUSE.exitRoom()"); await until(A, "()=>HOMEX.cur()==='living' && !HOUSE.trip().busy", 80)
        # ④ 창고에 넣었다 다시 → 예전 옆방 · 두 번째 문 = 옆방 2
        await A.evaluate("()=>{ const w=wplaced.find(w=>w.id==='sidedoor'); removePlaced(w); stock.sidedoor=(stock.sidedoor|0)+1; saveRoom(); addWall('sidedoor',3,2,0); stock.sidedoor--; saveRoom(); drawLabels(); }")
        ok(await A.evaluate("()=>wplaced.find(w=>w.id==='sidedoor').c")==1, "④ 다시 달면 예전 옆방 1 (가구 그대로)")
        await A.evaluate("()=>{ gems=1000; saveBag(); HOMEX.unlock('door'); addWall('sidedoor',0,4,0); stock.sidedoor--; saveRoom(); drawLabels(); }")
        r=await A.evaluate("()=>[wplaced.filter(w=>w.id==='sidedoor').map(w=>w.c).sort(), Object.keys(HOMEX.H().ax)]")
        ok(r==[[1,2],["1","2"]], f"④ 두 번째 문 = 옆방 2 {r}")
        # ⑤ 옆방에서 계단 = 2층 · 친구 방문
        await A.evaluate("()=>{ HOMEX.unlock('f2'); }")
        await A.evaluate("()=>useItem(wplaced.find(w=>w.id==='sidedoor' && w.c===1))"); await until(A, "()=>HOMEX.cur()==='a1' && !HOUSE.trip().busy", 80)
        await A.evaluate("()=>{ addPlaced('stairs',6,6,0,0); stock.stairs--; saveRoom(); useItem(placed.find(p=>p.id==='stairs')); }")
        ok(await until(A, "()=>HOMEX.cur()==='f2' && !HOUSE.trip().busy", 80), "⑤ 옆방 🪜 계단 → 2층")
        await A.evaluate("()=>HOUSE.exitRoom()"); await until(A, "()=>HOMEX.cur()==='living' && !HOUSE.trip().busy", 80)
        await A.evaluate("()=>HOUSE.publish()"); await A.wait_for_timeout(500)
        h=DB["hy"]["life"]["h"]["AAAAA"]["home"]
        ok(set(h.get("ax",{}).keys())=={"1","2"} and "a1" in h["r"], f"⑤ 서버 집 기록에 옆방 {list(h.get('ax',{}).keys())}")
        B=await kid("BBBBB","하준")
        await B.evaluate("()=>HOUSE.visitCode('AAAAA')")
        await until(B, "()=>['visit','yvisit'].includes(HOUSE.place()) && !HOUSE.trip().busy", 120)
        if await B.evaluate("()=>HOUSE.place()==='yvisit'"): await B.evaluate("()=>HOUSE.yVisitHouse()")
        ok(await until(B, "()=>HOUSE.place()==='visit' && !HOUSE.trip().busy", 200), "⑤ 루아 집에 놀러 감")
        await B.evaluate("()=>useItem(wplaced.find(w=>w.id==='sidedoor' && w.c===1))")
        ok(await until(B, "()=>HOMEX.cur()==='a1' && !HOUSE.trip().busy && placed.some(p=>p.id==='teepee')", 120), "⑤ 친구 옆방까지 구경 (⛺ 보임)")
        r=await B.evaluate("()=>[HOMEX.H().c, Object.keys(HOMEX.H().ax||{}).length]")
        ok(r==["living",0], f"⑤ 내 집 정보는 그대로 {r}")
        await br.close()
    e=real_errs(errs)
    ok(not e, f"오류 없음 {e[:3]}")
    print("\nFAIL" if bad else "\nPASS", len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
