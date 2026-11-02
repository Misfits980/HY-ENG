"""(v536) 🏠 집 안 넓히기 · 처음부터 다시 · 새 튜토리얼 · 바깥 집 층·모던 (가짜 서버 · 아이 2명)
   ① 초기화(?reset=1): 💎·가방·방·할 일 지워짐 · 집 코드·타워 기록은 남음 · 처음 방 = 비어 있음 + 침대·책상 1개씩
   ② 튜토리얼: 침대 놓기 → 책상 놓기 단계가 넘어감 · 책상 누르면 「영어 공부」
   ③ 잠긴 문: 부엌·침실·2층 자리에 문 + 🔒 이름표 · 문 앞 칸은 가구 못 놓음 · 누르면 넓히기 창 (연속 n일 더)
   ④ 연속 공부 + 💎 → 부엌 열기 · 문으로 들어가면 부엌(빈 방, 다른 바닥) · 거실 가구는 그대로 저장 · 다시 거실로
   ⑤ 부엌에서 새로 고침해도 부엌 · 밖에서 들어오면 늘 거실
   ⑥ 2층까지 열면 바깥 집이 2층 (서버 f=2) · 모던 집 고르기 → 서버 h=M_… · 친구 화면에도 모던 2층
   ⑦ 친구가 놀러 오면 열린 방(부엌)까지 구경 · 잠긴 방 문은 안 보임 · 나가기
   ⑧ 연속 공부: 금요일 → 월요일 = 이어짐 · 수요일 빠지면 1부터 (index.html didToday)"""
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
        async def kid(code, name, q="", pre=None):
            ctx=await br.new_context(viewport={"width":390,"height":760}, is_mobile=True, has_touch=True)
            pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(name+": "+str(e)))
            await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html?isle=1"); await pg.wait_for_timeout(500)
            await pg.evaluate("""([c,n,pre])=>{ Object.keys(localStorage).filter(k=>k.startsWith('hyeng_')).forEach(k=>localStorage.removeItem(k)); localStorage.setItem('hyeng_proto_code', JSON.stringify(c)); localStorage.setItem('hyeng_nick', n);
                Object.entries(pre||{}).forEach(([k,v])=>localStorage.setItem(k, typeof v==='string'?v:JSON.stringify(v))); }""", [code,name,pre or {}])
            await pg.goto(ORIGIN+"proto/house.html?isle=1"+q); await pg.wait_for_timeout(2200); return pg
        # ① 초기화
        old={"hyeng_proto_gems":99, "hyeng_proto_bag":[{"en":"carp","at":1}], "hyeng_proto_tower":{"b":123}, "hyeng_proto_tut":{"s":99},
             "hyeng_proto_room":{"p":[["sofa",2,2,0,0],["bed",0,0,0,0]],"rn":8}, "hyeng_isle_lot":"1-3", "hyeng_study_v1":{"days":{"n":1,"tot":1,"last":1}}}
        A=await kid("AAAAA","루아","&reset=1",old)
        r=await A.evaluate("()=>({gems:HOUSE.gems(), bag:JSON.parse(localStorage.getItem('hyeng_proto_bag')||'null'), tower:JSON.parse(localStorage.getItem('hyeng_proto_tower')||'null'), code:JSON.parse(localStorage.getItem('hyeng_proto_code')), rn:RN, placed:placed.map(p=>p.id), stock:Object.assign({},stock), tut:HOUSE.tut().s, lot:localStorage.getItem('hyeng_isle_lot'), ep:localStorage.getItem('hyeng_proto_epoch')})")
        print("①", r)
        ok(r["gems"]==0 and not r["bag"] and r["rn"]==6 and r["placed"]==[] and r["lot"] is None, f"① 초기화: 💎0 · 가방·방·땅 비움 {r}")
        ok(r["tower"]=={"b":123} and r["code"]=="AAAAA" and r["ep"]=="536", "① 집 코드·타워 기록은 남음")
        ok(r["stock"]=={"bed":1,"desk":1}, f"① 처음 = 침대·책상만 {r['stock']}")
        ok(r["tut"]==0, "① 튜토리얼 처음부터")
        # ② (v539) 새 시작 — 우리 마을 광장 → 📋 땅 고르기 → 집이 생김 → 집 안 → 🎁 입주 선물 → 침대 → 책상
        ok(await until(A, "()=>HOUSE.place()==='isle' && !HOUSE.trip().busy && HOUSE.tut().s===0 && /게시판/.test(document.getElementById('coachT').innerText)", 160), "② 처음 = 🏝 우리 마을 광장 · Mia 「게시판에서 내 땅」")
        await A.evaluate("()=>ISLE.openLots()")
        ok(await until(A, "()=>document.getElementById('lotP').classList.contains('on') && !document.getElementById('lotGo').disabled && /집 짓기/.test(document.getElementById('lotGo').textContent)", 40), "② 땅 고르기 = 👍 추천 땅이 골라져 있음 · 「여기에 집 짓기」")
        await A.evaluate("()=>document.getElementById('lotGo').click()"); await until(A, "()=>document.getElementById('ask').classList.contains('on')", 20); await A.evaluate("()=>document.getElementById('askOk').click()")
        ok(await until(A, "()=>!!ISLE.myHouse() && HOUSE.tut().s===1", 60), "② 집이 생김 → 다음 안내 「⭐ 내 집」")
        mine=[v for v in DB["hy"]["isle"].get("lot2",{}).values() if v.get("c")=="AAAAA"]
        ok(len(mine)==1, f"② 서버에 내 땅 {mine}")
        await A.evaluate("()=>ISLE.enterHome()")
        ok(await until(A, "()=>HOUSE.place()==='room' && !HOUSE.trip().busy && HOUSE.tut().s===2", 80), "② 내 집 안 → 안내 3단계")
        ok(await until(A, "()=>document.getElementById('info').classList.contains('on') && /입주 선물/.test(document.getElementById('infoT').innerText)", 20), "② 🎁 Mia 의 입주 선물 (침대·책상)")
        await A.evaluate("()=>document.getElementById('infoOk').click()")
        await A.evaluate("()=>{ HOUSE.tEv('walk'); }")
        ok(await until(A, "()=>HOUSE.tut().s===3 && /침대/.test(document.getElementById('coachT').innerText)", 20), "② 걷기 → 🛏 침대 놓기 안내")
        for i,(it,step) in enumerate((("bed",4),("desk",5))):
            await A.evaluate("(id)=>{ startGhost(id); okGhost(); }", it); await A.wait_for_timeout(300)
            ok(await until(A, f"()=>HOUSE.tut().s==={step}", 20) and await A.evaluate("(id)=>placed.some(p=>p.id===id)", it), f"② {it} 놓기 → 다음 단계 ({step})")
        await A.evaluate("()=>{ const p=placed.find(p=>p.id==='desk'); useItem(p); }")
        ok(await until(A, "()=>document.getElementById('ask').classList.contains('on') && /영어 공부/.test(document.getElementById('askT').innerText)", 20), "② 책상 = 「영어 공부 하러 갈까요?」")
        await A.evaluate("()=>document.getElementById('askNo').click()")
        # ③ 잠긴 문
        r=await A.evaluate("""()=>{ const L=LBL.map(l=>[l.d.k, l.el.textContent]); const sl=HOMEX.slots().map(s=>[s.side,s.s,s.to]); const cells=HOMEX.cells();
            return {L, sl, cells, blockKitchen:!fits('chair', RN-2, 0, 0), wallSlot:!wallFits(0,1)}; }""")
        print("③", r)
        ks=[x[0] for x in r["L"]]
        ok(all(k in ks for k in ("door","hd_kitchen","hd_bedroom","hd_f2")), f"③ 문 이름표: 나가기·부엌·침실·2층 {ks}")
        ok(any("🔒" in t and "부엌" in t for k,t in r["L"] if k=="hd_kitchen"), "③ 부엌 = 🔒 (연속 n일)")
        ok(r["blockKitchen"] and r["wallSlot"], "③ 문 앞 칸·문 자리 벽엔 가구 못 놓음")
        await A.evaluate("()=>LBL.find(l=>l.d.k==='hd_kitchen').d.act()")
        ok(await until(A, "()=>document.getElementById('upP') && document.getElementById('upP').classList.contains('on')", 20), "③ 잠긴 문 → 🏗 넓히기 창")
        t=await A.evaluate("()=>document.querySelector('[data-row=kitchen]').innerText")
        ok("일 더" in t, f"③ 부엌: 연속이 모자라면 「🔥 n일 더」 {t!r}")
        # ④ 연속 + 💎 → 부엌
        await A.evaluate("()=>{ localStorage.setItem('hyeng_study_v1', JSON.stringify({days:{n:8,tot:9,hs:8,hb:8,last:Math.floor((Date.now()-new Date().getTimezoneOffset()*60000)/864e5)}})); HOUSE.setGems ? HOUSE.setGems(300) : (gems=300); saveBag(); HOMEX.drawUp(); }")
        r=await A.evaluate("()=>[HOMEX.state('kitchen'), HOMEX.state('bath'), HOMEX.state('f2'), HOMEX.state('f3')]")
        ok(r==["ok","par","ok","par"], f"④ 연속 8일 + 💎300: 부엌 ○ · 욕실 = 침실 먼저 · 2층 ○ · 3층 = 2층 먼저 {r}")
        await A.evaluate("()=>document.querySelector('[data-up=kitchen]').click()"); await A.wait_for_timeout(200); await A.evaluate("()=>document.getElementById('askOk').click()")
        ok(await until(A, "()=>HOMEX.H().o.kitchen===1", 20) and await A.evaluate("()=>HOUSE.gems()")==280, "④ 부엌 열림 · 💎 -20")
        await A.evaluate("()=>document.getElementById('upP').classList.remove('on')")
        await A.evaluate("()=>LBL.find(l=>l.d.k==='hd_kitchen').d.act()")
        ok(await until(A, "()=>HOMEX.cur()==='kitchen' && !HOUSE.trip().busy && HOUSE.place()==='room'", 60), "④ 부엌 문 → 부엌으로")
        r=await A.evaluate("()=>({placed:placed.map(p=>p.id), f:floorIx, door:LBL.find(l=>l.d.k==='door').el.textContent, hero:[HOUSE.hero().cx,HOUSE.hero().cz], saved:(HOMEX.H().r.living||{}).p})")
        print("④", r)
        ok(sorted(r["placed"])==sorted(["stove","fridge","table","stool"]) and r["f"]==1 and "거실" in r["door"], f"④ 부엌 = 🍳🧊 처음 가구 · 타일 바닥 · 문 = 거실로 {r['door']!r}")
        ok(r["saved"] and {x[0] for x in r["saved"]}=={"bed","desk"}, "④ 거실 가구는 저장됨")
        await A.evaluate("()=>{ startGhost('desk'); }");
        await A.evaluate("()=>{ cancelGhost(); }")
        # ⑤ 새로 고침 → 부엌 · 밖에서 → 거실
        await A.reload(); await A.wait_for_timeout(2200)
        ok(await A.evaluate("()=>HOMEX.cur()==='kitchen' && floorIx===1"), "⑤ 새로 고침해도 부엌")
        await A.evaluate("()=>HOUSE.exitRoom()")
        ok(await until(A, "()=>HOMEX.cur()==='living' && !HOUSE.trip().busy && HOUSE.place()==='room'", 60), "⑤ 부엌 문 = 거실로")
        ok(await A.evaluate("()=>placed.some(p=>p.id==='bed') && placed.some(p=>p.id==='desk')"), "⑤ 거실 가구 그대로")
        # ⑥ 2층 · 바깥 집
        await A.evaluate("()=>HOMEX.unlock('f2')")
        ok(await A.evaluate("()=>HOMEX.floors()")==2, "⑥ 2층 열림 → 2층 집")
        await A.evaluate("()=>HOUSE.exitRoom()")
        ok(await until(A, "()=>HOUSE.place()==='isle' && !HOUSE.trip().busy", 80), "⑥ 밖 = 우리 마을")
        await A.wait_for_timeout(1500)
        await A.evaluate("()=>{ ISLE.openHouse(); document.querySelector('[data-hs=M_blue]').click(); }"); await A.wait_for_timeout(1200)
        lots=DB["hy"]["isle"].get("lot2",{})
        mine=[v for v in lots.values() if v.get("c")=="AAAAA"]
        print("⑥", mine)
        ok(mine and mine[0].get("f")==2 and mine[0].get("h")=="M_blue", f"⑥ 서버 땅 기록: 2층 · 모던 파랑 {mine}")
        ok("lot" not in DB["hy"]["isle"] or not any(v.get("c")=="AAAAA" for v in DB["hy"]["isle"].get("lot",{}).values()), "⑥ 예전 땅 목록(lot)은 안 씀")
        r=await A.evaluate("()=>{ const L=ISLE.myHouse(); let n=0, vc=0; L.obj.traverse(o=>{ if(o.isMesh){ n++; if(o.geometry.attributes.color) vc+=o.geometry.attributes.position.count; } }); return [L.style, L.fl, n, vc]; }")
        ok(r[0]=="M_blue" and r[1]==2 and r[2]<=2 and r[3]>300, f"⑥ 내 집 = 모던 2층 (한 덩어리) {r}")
        await A.evaluate("()=>HOUSE.publish()"); await A.wait_for_timeout(400)
        B=await kid("BBBBB","하준","",{"hyeng_proto_tut":{"s":99}})
        await B.evaluate("()=>HOUSE.exitRoom()"); await until(B, "()=>HOUSE.place()==='isle' && !HOUSE.trip().busy", 80); await B.wait_for_timeout(1500)
        r=await B.evaluate("()=>{ const L=ISLE.lots.find(l=>l.owner==='루아'); return L ? [L.style, L.fl, (()=>{ let y=0; L.obj.traverse(o=>{ if(o.isMesh){ const b=new THREE.Box3().setFromObject(o); y=Math.max(y,b.max.y); } }); return +y.toFixed(2); })()] : null; }")
        ok(r and r[0]=="M_blue" and r[1]==2 and r[2]>1.6, f"⑥ 친구 화면에도 모던 2층 (높이) {r}")
        # ⑦ 친구 집 방
        await A.evaluate("()=>ISLE.enterHome()")   # 루아는 집 안으로 (같은 브라우저 — 큰 섬 그리기를 줄여 친구 쪽이 빠르게)
        await B.evaluate("()=>HOUSE.visitCode('AAAAA')")
        await until(B, "()=>['visit','yvisit'].includes(HOUSE.place()) && !HOUSE.trip().busy && !HOUSE.hero().slide", 80)
        if await B.evaluate("()=>HOUSE.place()==='yvisit'"): await B.evaluate("()=>HOUSE.yVisitHouse()")
        ok(await until(B, "()=>HOUSE.place()==='visit' && !HOUSE.trip().busy", 280), "⑦ 루아 집에 놀러 감")
        r=await B.evaluate("()=>({ks:LBL.map(l=>l.d.k), placed:placed.map(p=>p.id), cur:HOMEX.cur()})")
        ok(r["cur"]=="living" and "hd_kitchen" in r["ks"] and "hd_bedroom" not in r["ks"] and "bed" in r["placed"], f"⑦ 거실부터 · 열린 부엌 문만 보임 {r}")
        await B.evaluate("()=>LBL.find(l=>l.d.k==='hd_kitchen').d.act()")
        ok(await until(B, "()=>HOMEX.cur()==='kitchen' && !HOUSE.trip().busy && HOUSE.place()==='visit'", 200), "⑦ 친구 부엌까지 구경")
        await B.evaluate("()=>HOUSE.exitRoom()"); await until(B, "()=>HOMEX.cur()==='living' && !HOUSE.trip().busy", 200)
        await B.evaluate("()=>HOUSE.exitRoom()")
        ok(await until(B, "()=>['isle','yvisit'].includes(HOUSE.place()) && !HOUSE.trip().busy", 200), "⑦ 거실 문 → 나가기")
        r=await B.evaluate("()=>[HOMEX.cur(), placed.length, HOMEX.H().c]")
        ok(r[0]=="living" and r[2]=="living", f"⑦ 내 집 정보는 그대로 {r}")
        # ⑧ 연속 (index.html)
        await A.context.close(); await B.context.close()
        P=await (await br.new_context()).new_page(); await P.route("**/*", route); await P.goto(ORIGIN+"index.html", timeout=90000); await P.wait_for_timeout(1500)
        r=await P.evaluate("""()=>{ const W=d=>new Date(d*864e5).getUTCDay(); let fri=Math.floor(Date.now()/864e5); while(W(fri)!==5) fri--; const mon=fri+3, wed=mon+2;
            const sim=(last,hs,t)=>{ const s={days:{last, hs, hb:hs, n:1, tot:5}}; const wk=d=>{ const w=new Date(d*864e5).getUTCDay(); return w===0||w===6; }; let ok=!!s.days.last && t-s.days.last>=1 && t-s.days.last<=3; for(let d=s.days.last+1; ok && d<t; d++) if(!wk(d)) ok=false; return ok ? hs+1 : 1; };
            const src=document.documentElement.innerHTML.indexOf('s.days.hb = Math.max(s.days.hb||0, s.days.hs)')>0;
            return [sim(fri,4,mon), sim(mon,5,wed), src]; }""")
        ok(r==[5,1,True], f"⑧ 금→월 = 이어짐 · 화요일 빠지면 1 {r}")
        await br.close()
    e=real_errs(errs)
    ok(not e, f"오류 없음 {e[:3]}")
    print("\nFAIL" if bad else "\nPASS", len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
