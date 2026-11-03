"""(v563) 💰 경제 2.0 (가짜 서버 · 아이 2명)
   ① 🪙 코인: 팔면 코인 (한도 없음) · HUD 🪙 · 📉 마을 시세 (이번 시간 다른 아이가 많이 판 것은 내려감)
   ② 🏦 은행 환전: 환율(7~14) · 🪙→💎 하루 한도 = 10 + 오늘 공부 💎 ½ · 💎→🪙 70% · 저금·적금(한 달 복리 · 일찍 찾으면 이자 없음) · 보석 적금 최대 200
   ③ 값: 🪙만 / 💎+🪙 / 💎만 · 가구점 「살까요?」 · 🌙 이달의 한정 · 모자라면 안내
   ④ 이용료: 🚉 기차표(맞히면 다음 반값) · 🗺 바로 가기 🪙5 · 🎣 대회 참가비 → 상금 주머니
   ⑤ 🛠 강화 3가지 · 🪱 미끼 최대 20 · 공부 선물(inbox) · 🏗 마을 공사 기부 · 요약(hyeng_town_sum) · Mia 말풍선이 조이스틱·점프를 안 가림"""
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
        async def kid(code,name,q="?isle=1"):
            ctx=await br.new_context(viewport={"width":390,"height":844}, is_mobile=True, has_touch=True)
            pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(name+": "+str(e)))
            await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html"+q); await pg.wait_for_timeout(500)
            await pg.evaluate("""([c,n])=>{ Object.keys(localStorage).filter(k=>k.startsWith('hyeng_')).forEach(k=>localStorage.removeItem(k)); localStorage.setItem('hyeng_proto_code', JSON.stringify(c)); localStorage.setItem('hyeng_nick', n); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99}));
                localStorage.setItem('hyeng_study_v1', JSON.stringify({days:{n:8,tot:9,hs:8,hb:8,last:Math.floor((Date.now()-new Date().getTimezoneOffset()*60000)/864e5)}}));
                localStorage.setItem('hyeng_town_inbox', JSON.stringify({bait:5})); }""", [code,name])
            await pg.reload(); await pg.wait_for_timeout(2600); return pg
        A=await kid("AAAAA","루아")
        # ⑤ 공부 선물 (inbox) · 미끼 최대 20
        r=await A.evaluate("()=>[bait, localStorage.getItem('hyeng_town_inbox')]")
        ok(r[0]==15 and r[1] is None, f"⑤ 공부 선물 🪱+5 받음 (10→15) · inbox 비움 {r}")
        await A.evaluate("()=>{ setBait(40); }")
        ok(await A.evaluate("()=>bait")==20, "⑤ 🪱 미끼는 20개까지")
        await A.evaluate("()=>{ store('hyeng_proto_baitg',''); setBait(0); baitGift(); baitGift(); }")
        ok(await A.evaluate("()=>bait")==3, "⑤ 하루 공짜 미끼 +3 (한 번)")
        # ① 팔기 → 🪙
        r=await A.evaluate("""()=>{ const c0=TECO.coins(), g0=HOUSE.gems(); bag.push({en:'whale',at:Date.now(),cm:150}); bag.push({en:'shark',at:Date.now(),cm:90}); for(let i=0;i<30;i++) bag.push({en:'fish',at:Date.now(),cm:20});
            const v=bag.map(price).reduce((a,b)=>a+b,0); let t=0; while(bag.length) t+=sell(0); return [TECO.coins()-c0, HOUSE.gems()-g0, t>0, v]; }""")
        ok(r[0]>30 and abs(r[0]-r[3])<=2 and r[1]==0 and r[2], f"① 팔면 🪙 = 값 그대로 (한도 없음 · 💎 는 안 늘어남 · 시간마다 시세가 달라 합계는 바뀜) {r}")   # (v577) 시세가 낮은 시간엔 54 → 60 넘기 조건이 흔들림
        ok(await A.evaluate("()=>document.getElementById('hCoin').querySelector('b').textContent.replace(/,/g,'')")==str(await A.evaluate("()=>TECO.coins()")), "① HUD 🪙 칸")
        r=await A.evaluate("()=>{ const a=TECO.mkF('fish'); return [a, TECO.mkF('octopus')]; }")
        ok(r[0]<1 and r[1]==1, f"① 📉 이번 시간 많이 판 fish 는 값이 내려감 {r}")
        await A.wait_for_timeout(700); h=await A.evaluate("()=>hourIx()")   # (v563 QA) 서버엔 0.4초 모아서 한 번
        ok(str(h) in DB.get("hy",{}).get("isle",{}).get("mkt",{}) and DB["hy"]["isle"]["mkt"][str(h)]["AAAAA"].get("fish")==30, "① 서버에 이번 시간 판 수 (다른 아이 시세에 반영)")
        # ② 환전
        await A.evaluate("()=>{ TECO.setCoin(1000); gems=0; saveBag(); }")
        r=await A.evaluate("()=>[TECO.rate(), TECO.sellRate(), TECO.limit(), TECO.left()]")
        ok(7<=r[0]<=14 and r[1]==min(6,int(r[0]*0.7)) and r[2]==10, f"② 환율 💎1=🪙{r[0]} · 되팔기 🪙{r[1]} · 오늘 한도 💎{r[2]} (공부 기록 없음)")
        await A.evaluate("()=>{ const K='hyeng_wallet_v1', a=JSON.parse(localStorage.getItem(K)||'{}'); a.log=(a.log||[]).concat([[Date.now(), 30, '공부 g34-1', 30]]); localStorage.setItem(K, JSON.stringify(a)); }")
        ok(await A.evaluate("()=>TECO.limit()")==25, "② 오늘 공부 💎30 → 한도 10+15 = 25")
        r=await A.evaluate("()=>{ const c0=TECO.coins(), r=TECO.rate(); const n=TECO.buyGem(100); return [n, c0-TECO.coins(), r*25, HOUSE.gems(), TECO.buyGem(1)]; }")
        ok(r[0]==25 and r[1]==r[2] and r[3]==25 and r[4]==0, f"② 🪙→💎 한도까지만 (25) · 더는 안 됨 {r}")
        r=await A.evaluate("()=>{ const c0=TECO.coins(); TECO.sellGem(5); return [TECO.coins()-c0, TECO.sellRate()*5, HOUSE.gems()]; }")
        ok(r[0]==r[1] and r[2]==20, f"② 💎→🪙 70% {r}")
        # 저금·적금
        r=await A.evaluate("""()=>{ TECO.setCoin(2000); gems=300; saveBag(); TECO.deposit('sv',1000); TECO.deposit('lk',500); const g1=TECO.deposit('gm',150), g2=TECO.deposit('gm',100);
            const B=TECO.BK(); B.st-=TECO.MON*2; B.lk[0].t-=TECO.MON*1+1000; B.gm[0].t-=TECO.MON+1000; TECO.settle(); const v=TECO.bankV(); return [B.sv, v.lk, v.gm, g1, g2, TECO.coins(), HOUSE.gems()]; }""")
        ok(r[0]==1040 and r[1]==525 and r[2]==152 and r[3] and not r[4] and r[5]==500 and r[6]==150, f"② 🐷 2% 두 달 복리 1000→1040 · 📅 5% 525 · 💎 1% 152(반올림) · 보석 적금 200 넘으면 안 됨 {r}")
        r=await A.evaluate("()=>{ TECO.deposit('lk',100); const c0=TECO.coins(); const B=TECO.BK(); const n=TECO.withdraw('lk', B.lk.length-1); return [n, TECO.coins()-c0]; }")
        ok(r==[100,100], f"② 한 달 전에 찾으면 이자 없이 원금만 {r}")
        # (v563 QA) 돈 구멍 막기
        r=await A.evaluate("()=>{ const B=TECO.BK(); B.lk[0].t-=TECO.MON*3; return TECO.bankV().lk; }")
        ok(r==525, f"② QA 📅 한 달 적금은 5% 한 번 (계속 두어도 복리로 불지 않음) {r}")
        r=await A.evaluate("()=>{ TECO.withdraw('sv'); TECO.setCoin(5000); TECO.deposit('sv',100); const B=TECO.BK(); B.st-=TECO.MON-60000; TECO.deposit('sv',3000); B.st-=120000; TECO.settle(); return B.sv; }")
        ok(r==3102, f"② QA 🐷 이자 직전에 넣은 🪙3000 은 첫 달 이자 없음 (100×2% = 2) {r}")
        r=await A.evaluate("()=>{ let best=0; for(let h=0;h<400;h++) best=Math.max(best, Math.floor(TECO.rate(h)*0.7)>6?6:Math.floor(TECO.rate(h)*0.7)); let lo=99; for(let h=0;h<400;h++) lo=Math.min(lo, TECO.rate(h)); return [best, lo, TECO.sellRate()]; }")
        ok(r[2]<=6 and r[0]<r[1], f"② QA 되팔기(최대 🪙6) < 가장 싼 사기(🪙7) — 사고 되팔아 벌기 없음 {r}")
        await A.evaluate("()=>TECO.openBank('ex')"); await A.wait_for_timeout(300)
        r=await A.evaluate("()=>[document.getElementById('teBank').classList.contains('on'), /환율/.test(document.getElementById('teBank').innerText), !!document.querySelector('#teBank svg')]")
        ok(all(r), f"② 🏦 은행 창 (환율 · 12시간 그림) {r}")
        await A.screenshot(path=OUT+"econ563_bank.png")
        await A.evaluate("()=>TECO.openBank('sv')"); await A.wait_for_timeout(300); await A.screenshot(path=OUT+"econ563_save.png")
        await A.evaluate("()=>document.getElementById('teBank').classList.remove('on')")
        # ③ 값 · 가구점
        r=await A.evaluate("()=>[JSON.stringify(furnCO('stool')), JSON.stringify(furnCO('piano')), JSON.stringify(furnCO('bed')), AV_COST.style, ROOM_UP[0][1], HOMEX.SETS.door.gem]")
        ok(r[0]=='{"g":0,"c":250}' and json.loads(r[1])["g"]>0 and json.loads(r[1])["c"]>0 and r[3]==185 and r[4]==320 and r[5]==400, f"③ 스툴 🪙만 · 피아노 💎+🪙 · 옷 💎185 · 넓히기 💎320 · 옆방 문 💎400 {r}")
        await A.evaluate("()=>{ gems=1000; saveBag(); TECO.setCoin(5000); HOUSE.exitRoom ? 0:0; openFurn('furn'); }"); await A.wait_for_timeout(300)
        await A.evaluate("()=>document.querySelector('[data-fc=lim]').click()"); await A.wait_for_timeout(200)
        r=await A.evaluate("()=>[...document.querySelectorAll('#furnBody [data-bf]')].map(b=>b.dataset.bf)")
        ok(sorted(r)==sorted(await A.evaluate("()=>TECO.limNow()")) and len(r)>=3, f"③ 🌙 이달의 한정 칸 {r}")
        await A.evaluate("()=>document.querySelector('[data-fc=all]').click()"); await A.wait_for_timeout(200)
        r=await A.evaluate("()=>{ const out=TECO.LIMITED[1+((new Date(TECO.T()+9*3600e3).getUTCMonth()+6)%12)].filter(id=>TECO.limNow().indexOf(id)<0); return [out, out.filter(id=>document.querySelector('#furnBody [data-bf='+id+']')).length]; }")
        ok(r[1]==0, f"③ 다른 달 한정은 안 보임 {r}")
        await A.evaluate("()=>document.querySelector('#furnBody [data-bf=piano]').click()"); await A.wait_for_timeout(200)
        t=await A.evaluate("()=>document.getElementById('askT').innerText")
        ok("💎" in t and "🪙" in t, f"③ 피아노 「💎 + 🪙 에 살까요?」 {t!r}")
        r0=await A.evaluate("()=>[HOUSE.gems(), TECO.coins()]")
        await A.click("#askOk"); await A.wait_for_timeout(200)
        r=await A.evaluate("()=>{ const o=furnCO('piano'); return [HOUSE.gems(), TECO.coins(), o.g, o.c, stock.piano|0]; }")
        ok(r[0]==r0[0]-r[2] and r[1]==r0[1]-r[3] and r[4]==1, f"③ 💎 와 🪙 둘 다 빠짐 {r0}→{r}")
        await A.evaluate("()=>{ document.getElementById('furnP').classList.remove('on'); TECO.setCoin(0); }")
        ok(not await A.evaluate("()=>TECO.pay2({g:0,c:50})") and "은행" in await A.evaluate("()=>document.getElementById('toast').textContent"), "③ 모자라면 「🏦 은행」 안내")
        # ⑤ 강화
        r=await A.evaluate("()=>{ TECO.setCoin(10000); const p0=TECO.rodPow(), cap0=bagCap; TECO.upgrade('rod'); TECO.upgrade('bag'); TECO.upgrade('rod'); return [TECO.lv('rod'), TECO.lv('bag'), TECO.rodPow()<p0, bagCap-cap0, 10000-TECO.coins()]; }")
        ok(r[0]==2 and r[1]==1 and r[2] and r[3]==5 and r[4]==300+750+300, f"⑤ 🛠 강화 낚싯대 2 · 가방 1 (+5칸) · 값 300→750 {r}")
        r=await A.evaluate("()=>{ bagCap=25; const R=CRAFT.find(x=>x.id==='bag'); R.give(); return bagCap; }")
        ok(r==35, f"⑤ QA 가방 강화 +5 는 big bag(30칸) 뒤에도 남음 {r}")
        # ④ 이용료 — 기차
        await A.evaluate("()=>HOUSE.exitRoom()"); ok(await until(A, "()=>HOUSE.place()==='isle' && !HOUSE.trip().busy", 160), "🏝 마을")
        await A.wait_for_timeout(1500)
        ok(await A.evaluate("()=>LBL.some(l=>l.d.k==='f_bank')"), "② 🏦 마을 은행 건물·이름표 (광장)")
        r=await A.evaluate("()=>{ TECO.setCoin(100); store('hyeng_proto_thalf',0); const f1=TECO.trainFee(); const ok1=TECO.payTrain(); TECO.trainRight(); const f2=TECO.trainFee(); TECO.payTrain(); return [f1, ok1, f2, TECO.coins(), TECO.trainFee()]; }")
        ok(r==[10,True,5,85,10], f"④ 🎫 기차표 🪙10 · 맞히면 다음 반값 {r}")
        # 바로 가기
        # (v583) 사용자: 「기차 의미가 있을까 · 집이랑 광산은 하게」 → 🚀 바로 가기 = ⛏ 광산만 🪙5 (놀이 공원 등은 🚶/🚉)
        await A.evaluate("()=>{ TECO.setCoin(20); IHUD.goZone('mine'); }"); await A.wait_for_timeout(300)
        await A.evaluate("()=>document.querySelector('#ask [data-gz=\"1\"]').click()")
        for _ in range(60):
            if await A.evaluate("()=>HOUSE.place()==='mine' && !HOUSE.trip().busy"): break
            await A.wait_for_timeout(250)
        r=await A.evaluate("()=>[TECO.coins(), HOUSE.place()]")
        ok(r==[15,'mine'], f"④ 🗺 바로 가기 🪙5 → ⛏ 광산 {r}")
        await A.evaluate("()=>mineToVillage()")
        for _ in range(120):
            if await A.evaluate("()=>HOUSE.place()==='isle' && !HOUSE.trip().busy"): break
            await A.wait_for_timeout(250)
        # 공사
        r=await A.evaluate("async ()=>{ TECO.setCoin(1000); await TECO.donate('free1', 500); await TECO.bdLoad(true); return [TECO.bdTot('free1'), TECO.coins(), LBL.some(l=>l.d.k==='b_free1')]; }")
        ok(r[0]==500 and r[1]==500 and r[2], f"⑤ 🏗 수영장 공사에 🪙500 보탬 · 🏗 이름표 b_free1 (window.TECO) {r}")
        r=await A.evaluate("async ()=>{ const P=NET.put; NET.put=()=>Promise.reject(new Error('x')); TECO.setCoin(1000); await TECO.donate('free1', 500); NET.put=P; await TECO.donate('free1', 50); await TECO.bdLoad(true); return [TECO.coins(), TECO.bdTot('free1')]; }")
        ok(r==[950,550], f"⑤ QA 서버에 못 보낸 기부는 합계에 안 들어감 (돌려받음) {r}")
        ok(DB["hy"]["isle"]["build"]["free1"]["AAAAA"]["v"]==550, "⑤ 서버에 기부 기록 (500 + 50, 실패한 500 은 빠짐) (이름이 간판에)")
        # 요약 (관리 화면·시트용)
        await A.wait_for_timeout(400)
        s=await A.evaluate("()=>JSON.parse(localStorage.getItem('hyeng_town_sum')||'null')")
        ok(s and s["coin"]==950 and "낚싯대2" in s["tup"] and s["bank"]>=1000, f"⑤ 게임이 읽는 요약 hyeng_town_sum {s}")
        # Mia 말풍선 vs 조이스틱·점프
        await A.evaluate("()=>{ tutAdv(7); drawCoach(false); }"); await A.wait_for_timeout(400)
        r=await A.evaluate("""()=>{ const c=document.getElementById('coach').getBoundingClientRect(); const ov=id=>{ const e=document.getElementById(id); if(!e) return false; const b=e.getBoundingClientRect(); if(!b.width) return false; return !(b.right<c.left||b.left>c.right||b.bottom<c.top||b.top>c.bottom); };
            return [document.getElementById('coach').classList.contains('on'), ov('ijoy'), ov('ijump'), Math.round(c.bottom)]; }""")
        ok(r[0] and not r[1] and not r[2], f"⑤ Mia 말풍선이 조이스틱·점프를 안 가림 {r}")
        await A.screenshot(path=OUT+"econ563_coach.png")
        await A.evaluate("()=>{ tutAdv(99); }")
        # ④ 낚시 대회 참가비 → 상금 주머니 (아이 2명)
        B=await kid("BBBBB","하준","?isle=1&iplay=test&ft=on")
        await B.evaluate("()=>HOUSE.exitRoom()"); await until(B, "()=>HOUSE.place()==='isle' && !HOUSE.trip().busy", 160)
        await A.evaluate("()=>{ TECO.setCoin(100); }")
        await B.evaluate("()=>{ TECO.setCoin(100); IPLAY.onCatch(HOUSE.FISH.find(f=>f.en==='shark'), 90, false, false); }"); await B.wait_for_timeout(300)
        ok(await B.evaluate("()=>/참가비/.test(document.getElementById('askT').innerText) && document.getElementById('ask').classList.contains('on')"), "④ 🎣 대회 첫 기록 → 「참가비 🪙20 참가할까요?」")
        await B.evaluate("()=>document.getElementById('askOk').click()"); await B.wait_for_timeout(600)
        ok(await B.evaluate("()=>TECO.coins()")==80, "④ 참가비 🪙20 냄")
        sid=await B.evaluate("()=>IPLAY.ftSlot().id")
        mk=await B.evaluate("()=>ISLE.myKey()")
        rec=DB["hy"]["isle"]["ft"][sid][mk]
        ok(rec["s"]==90 and rec.get("fee")==1, f"④ 대회 기록 (참가비 표시) {rec}")
        DB["hy"]["isle"]["ft"][sid]["CCCCC"]={"n":"친구","s":40,"fee":1,"at":1}
        await B.evaluate("async ()=>{ await IPLAY.ftEnd(IPLAY.ftSlot().id); }"); await B.wait_for_timeout(400)
        r=await B.evaluate("()=>[TECO.coins(), document.getElementById('info') ? document.getElementById('info').innerText : '']")
        ok(r[0]==80+20, f"④ 1등 = 상금 주머니(2명 × 🪙20)의 50% = 🪙20 {r[0]}")
        ok(await B.evaluate("()=>IPLAY.ftQ().length")==0, "④ 끝난 대회는 기억 목록에서 빠짐")
        # (v563) 대회 끝날 때 섬에 없었어도 다음에 들어오면 상금
        DB["hy"]["isle"]["ft"]["tpast"]={mk:{"n":"하준","s":50,"fee":1,"at":1}, "CCCCC":{"n":"친구","s":30,"fee":1,"at":1}}
        r=await B.evaluate("""async ()=>{ document.getElementById('info').classList.remove('on'); TECO.setCoin(100); localStorage.setItem(TECO.kk('hyeng_isle_ftq'), JSON.stringify([{id:'tpast', en:IPLAY.T()-60000}]));
            IPLAY.ftCatchUp(IPLAY.T(), true); for(let i=0;i<40 && TECO.coins()===100;i++) await new Promise(r=>setTimeout(r,150)); await new Promise(r=>setTimeout(r,300)); return [TECO.coins(), IPLAY.ftQ().length, document.getElementById('info').classList.contains('on')]; }""")
        ok(r==[120,0,True], f"④ 앱을 닫아 대회 끝을 못 봤어도 → 다음에 섬에서 결과 창 + 1등 🪙20 {r}")
        await B.evaluate("()=>toast('테스트 알림', 3000)"); await B.wait_for_timeout(500)
        r=await B.evaluate("()=>{ const t=document.getElementById('toast').getBoundingClientRect(), h=document.getElementById('ihRes').getBoundingClientRect(); return [Math.round(t.top), Math.round(h.bottom)]; }")
        ok(r[0]>=r[1], f"🟡 섬: 알림이 💎·🪱·🪙 칸 아래 {r}")
        await br.close()
    e=real_errs(errs)
    ok(not e, f"오류 없음 {e[:3]}")
    print("\nFAIL" if bad else "\nPASS", len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
