"""(v544) 🏘 마을 시설 9곳 (가짜 서버 · 아이 2명)
   ① 건물 8곳 + 🎪 무대 이름표 · 건물 자리는 막힘 · 문 앞은 걸을 수 있음 · 🍗 단추
   ② 📣 마을 목표: 새 단어·공부한 날 = 내 점수 → 서버 · 목표를 넘으면 🎉 축제 (불꽃 · 💎20 한 번)
   ③ 📮 우체국: 낱말 조각으로 문장 → 친구에게 (간식 선물) · 하루 3통 · 친구가 읽으면 💎1 + 선물 · 마을 사람에게 보내면 답장
   ④ 🍦 간식 가게: 영어 이름 맞혀 주문 · 먹으면 🍗 · 배부르면 빨라짐 · 배고프면 느려짐
   ⑤ 🐶 펫: 사기 → 이름 → 따라다님 · 밥 · "Sit!" 듣고 재주 · 집 기록에 펫
   ⑥ 🏛 박물관: 영어 이름표 맞히면 기증 · 가방에서 빠짐 · 💎5 · 다른 아이도 기증자 이름을 봄 · 이미 있으면 못 함
   ⑦ 📸 사진관: 찰칵 → 앨범 · 🖼 액자 창고
   ⑧ 📚 도서관: 그림책 끝까지 → 문제 2개 → ⭐ · 💎3 (처음 한 번) · 잠긴 책
   ⑨ 🚉 기차역: "Next stop is the lake!" → 맞히면 💎1 → 호수 앞
   ⑩ 🎃 계절: ?season=winter → 눈 · 오류 없음"""
import asyncio, sys, os, json
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from fakefb import fake, DB
from playwright.async_api import async_playwright
WORDS=['cat','dog','apple','book','sun','moon','star','tree','fish','bird','cake','ball','hat','shoe','bus','duck','frog','milk','egg','pen','cup','bed']

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
        async def kid(code,name,qs=""):
            ctx=await br.new_context(viewport={"width":390,"height":760}, is_mobile=True, has_touch=True)
            pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(name+": "+str(e)))
            await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html?isle=1"); await pg.wait_for_timeout(500)
            await pg.evaluate("""([c,n,W])=>{ Object.keys(localStorage).filter(k=>k.startsWith('hyeng_')).forEach(k=>localStorage.removeItem(k)); localStorage.setItem('hyeng_proto_code', JSON.stringify(c)); localStorage.setItem('hyeng_nick', n); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); localStorage.setItem('hyeng_isle_cam','1');
                localStorage.setItem('hyeng_study_v1', JSON.stringify({srs:Object.fromEntries(W.map(w=>[w,[1,0]])), days:{n:5,tot:5,hs:5,hb:5,last:Math.floor((Date.now()-new Date().getTimezoneOffset()*60000)/864e5)}})); }""", [code,name,WORDS])
            await pg.goto(ORIGIN+"proto/house.html?isle=1"+qs); await pg.wait_for_timeout(2000)
            await pg.evaluate("()=>{ gems=300; saveBag(); HOUSE.exitRoom(); }")
            await until(pg, "()=>HOUSE.place()==='isle' && !HOUSE.trip().busy", 160); await pg.wait_for_timeout(1200)
            return pg
        A=await kid("AAAAA","루아")
        # ①
        r=await A.evaluate("()=>LBL.filter(l=>/^f_/.test(l.d.k)).map(l=>l.d.k)")
        ok(sorted(r)==sorted(["f_goal","f_post","f_museum","f_library","f_station","f_bank","f_stage"]), f"① 시설 이름표 7개 (v563 🏦 은행) (간식·펫·사진관 = 상점가 가게) {r}")
        r=await A.evaluate("()=>['snack','pet','photo'].map(k=>!!LBL.find(l=>l.d.k===k))")
        ok(r==[True,True,True], f"① 🏪 상점가: 🍦 🐶 📸 이름표 {r}")
        r=await A.evaluate("()=>Object.values(TFAC.SP).filter(S=>S.k!=='goal').map(S=>[S.k, ISLE.blocked(Math.floor(S.at[0]),Math.floor(S.at[1])), ISLE.blocked(Math.floor(S.door[0]),Math.floor(S.door[1]))])")
        ok(all(x[1] for x in r), f"① 건물 자리는 막힘 {r}")
        ok(all(not x[2] for x in r), f"① 문 앞은 걸을 수 있음 {[x for x in r if x[2]]}")
        r=await A.evaluate("()=>{ const h=HOUSE.hero(); return Object.values(TFAC.SP).filter(S=>S.k!=='goal').map(S=>[S.k, ISLE.reachFrom ? 1 : 1]); }")
        ok(await until(A, "()=>!!document.getElementById('ihFull')", 20), "① 🍗 단추 (섬 HUD)")
        # 걸어서 가게 앞 → 창
        await A.evaluate("()=>{ const S=ISLE.SPOT.shops.find(s=>s.k==='snack'); TFAC.warp(S.door[0]+3, S.door[1]+3); LBL.find(l=>l.d.k==='snack').d.act(); }")
        ok(await until(A, "()=>document.getElementById('tfSn') && document.getElementById('tfSn').classList.contains('on')", 200), "① 🍦 상점가 이름표 → 걸어가서 간식 가게 창")
        await A.evaluate("()=>document.getElementById('tfSn').classList.remove('on')")
        if await A.evaluate("()=>!!window.SHOPIN && SHOPIN.is()"):   # (v572) 가게 안 → 🚪 나가기 로 섬에 돌아옴
            await A.evaluate("()=>SHOPIN.exit()"); ok(await until(A, "()=>HOUSE.place()==='isle' && !HOUSE.trip().busy && !HOUSE.hero().slide", 80), "① (v572) 🍦 가게 안 → 나가기 → 🏝")
        # ② 목표
        await A.evaluate("()=>{ const S=JSON.parse(localStorage.getItem('hyeng_study_v1')); ['red','blue','green','pink','sky'].forEach(w=>S.srs[w]=[1,0]); S.days.tot+=1; localStorage.setItem('hyeng_study_v1', JSON.stringify(S)); }")
        await A.evaluate("()=>TFAC.loadGoal()")
        r=await A.evaluate("()=>[TFAC.myPts(), TFAC.GOAL.tot, TFAC.GOAL.target]")
        wk=list(DB["hy"]["isle"]["goal"].keys())[0]
        ok(r[0]==10 and DB["hy"]["isle"]["goal"][wk]["by"]["AAAAA"]["v"]==10 and r[2]>=150, f"② 새 단어 5 + 공부한 날 1 = 10점 → 서버 {r}")
        DB["hy"]["isle"]["goal"][wk]["by"]["ZZZZZ"]={"n":"하준","v":500}
        await A.evaluate("()=>TFAC.loadGoal()")
        r=await A.evaluate("()=>[TFAC.GOAL.tot>=TFAC.GOAL.target, LBL.find(l=>l.d.k==='f_goal').d.t]")
        ok(r[0] and "축제" in r[1], f"② 목표 넘으면 🎉 축제 {r}")
        await A.wait_for_timeout(2600)
        ok(await A.evaluate("()=>ISLE.G.children.some(o=>o.isGroup && o.children.some(c=>c.isPoints))"), "② 🎆 불꽃놀이")
        g0=await A.evaluate("()=>TECO.coins()")
        await A.evaluate("()=>{ TFAC.openGoal(); document.querySelector('#tfGo [data-claim]').click(); }"); await A.wait_for_timeout(300)
        await A.evaluate("()=>{ TFAC.openGoal(); const b=document.querySelector('#tfGo [data-claim]'); if(b) b.click(); }"); await A.wait_for_timeout(300)
        ok(await A.evaluate("()=>TECO.coins()")==g0+100, "② 축제 선물 🪙100 (v563 · 한 번만)")
        await A.evaluate("()=>document.getElementById('tfGo').classList.remove('on')")
        # B 들어옴 (땅 있음)
        B=await kid("BBBBB","하준")
        # ③ 우체국
        await A.evaluate("()=>{ addMat('cookie',1); saveBag(); TFAC.openPost('out'); }")
        ok(await until(A, "()=>!!document.querySelector('#tfTo [data-c=BBBBB]')", 40), "③ 받는 사람 목록에 하준")
        await A.evaluate("()=>document.querySelector('#tfTo [data-c=BBBBB]').click()"); await A.wait_for_timeout(200)
        await A.evaluate("()=>document.querySelector('#tfPoB [data-s=\"2\"]').click()"); await A.wait_for_timeout(200)
        r=await A.evaluate("""()=>{ const words="I like your house!".split(" "); let wrong=0; const B=document.getElementById('tfPoB');
            const first=[...B.querySelectorAll('[data-t]')].find(b=>b.textContent!==words[0]); if(first){ first.click(); wrong=B.querySelector('.tfAns span') ? 0 : 1; }
            words.forEach(w=>{ const b=[...document.querySelectorAll('#tfPoB [data-t]')].find(b=>b.textContent===w); if(b) b.click(); }); return wrong; }""")
        ok(r==1, "③ 틀린 낱말은 안 들어감")
        ok(await until(A, "()=>!!document.querySelector('#tfPoB [data-send]')", 20), "③ 문장 완성 → 스티커·선물 고르기")
        await A.evaluate("()=>{ document.querySelector('#tfPoB [data-st=\"1\"]').click(); document.querySelector('#tfPoB [data-g=cookie]').click(); document.querySelector('#tfPoB [data-send]').click(); }")
        ok(await until(A, "()=>/Sent/.test(document.getElementById('tfPoB').innerText)", 20), "③ 보냄")
        box=DB["hy"]["isle"]["mail"]["BBBBB"]; m=list(box.values())[0]
        ok(m["s"]==2 and m["st"]==1 and m["g"]=="cookie" and m["f"]=="AAAAA", f"③ 서버 편지 {m}")
        ok(await A.evaluate("()=>(mats.cookie|0)===0"), "③ 보낸 간식은 내 가방에서 빠짐")
        await A.evaluate("()=>{ localStorage.setItem('hyeng_proto_tfd', JSON.stringify({d:dayKey(), mail:3})); TFAC.openPost('out'); }"); await A.wait_for_timeout(400)
        ok("3통" in await A.evaluate("()=>document.getElementById('tfPoB').innerText"), "③ 하루 3통까지")
        await A.evaluate("()=>document.getElementById('tfPo').classList.remove('on')")
        await B.evaluate("()=>TFAC.loadMail()")
        r=await B.evaluate("()=>[TFAC.MAIL.unread, LBL.find(l=>l.d.k==='f_post').d.t]")
        ok(r[0]==2 and "✉️2" in r[1], f"③ 하준: 새 편지 2 (루아 + Mia 환영) {r}")
        g0=await B.evaluate("()=>TECO.coins()")
        await B.evaluate("()=>TFAC.openPost('in')")
        await until(B, "()=>document.querySelectorAll('#tfPoB [data-m]').length>=2", 20)
        await B.evaluate("()=>{ const m=TFAC.MAIL.list.find(x=>x.f==='AAAAA'); document.querySelector('#tfPoB [data-m=\"'+m.id+'\"]').click(); }"); await B.wait_for_timeout(300)
        r=await B.evaluate("()=>[document.getElementById('tfPoB').innerText, mats.cookie|0, TECO.coins(), TFAC.MAIL.unread]")
        ok("I like your house!" in r[0] and "루아" in r[0] and r[1]==1 and r[2]==g0+5 and r[3]==1, f"③ 읽기: 문장·보낸 사람 · 🍪 선물 · 🪙5 (v563) {r[1:]}")
        await B.evaluate("()=>{ document.querySelector('#tfPoB [data-reply]').click(); }"); await B.wait_for_timeout(300)
        ok("루아" in await B.evaluate("()=>document.getElementById('tfPoB').innerText"), "③ 답장 = 루아에게")
        await B.evaluate("()=>document.getElementById('tfPo').classList.remove('on')")
        await A.evaluate("()=>{ localStorage.setItem('hyeng_proto_tfd', JSON.stringify({d:dayKey(), mail:0})); }")
        # ④ 간식
        await A.evaluate("()=>{ localStorage.setItem('hyeng_proto_full', JSON.stringify({h:1, t:Date.now()})); }")
        await A.reload(); await A.wait_for_timeout(2000); await A.evaluate("()=>{ HOUSE.exitRoom(); }"); await until(A, "()=>HOUSE.place()==='isle' && !HOUSE.trip().busy", 160); await A.wait_for_timeout(800)
        await A.evaluate("()=>TECO.setCoin(500)"); g0=await A.evaluate("()=>TECO.coins()")
        await A.evaluate("()=>{ TFAC.openSnack(); document.querySelector('#tfSn [data-sn=\"ice cream\"]').click(); }")
        ok(await until(A, "()=>document.getElementById('hqP').classList.contains('on') && /What would you like/.test(document.getElementById('hqP').innerText)", 20), "④ 🧑‍🍳 \"What would you like?\"")
        await A.evaluate("()=>{ const box=document.querySelector('#hqP .b'); const w=[...box.querySelectorAll('[data-w]')].find(b=>b.dataset.w!=='ice cream'); w.click(); }"); await A.wait_for_timeout(300)
        ok(await A.evaluate("()=>(mats['ice cream']|0)===0"), "④ 틀리면 아직 안 삼")
        await A.evaluate("()=>document.querySelector('#hqP [data-w=\"ice cream\"]').click()")
        ok(await until(A, "()=>(mats['ice cream']|0)===1", 20) and await A.evaluate("()=>TECO.coins()")==g0-10, "④ 맞히면 🍦 ice cream 🪙10 (v563)")
        await A.evaluate("()=>document.getElementById('tfSn').classList.remove('on')")
        r=await A.evaluate("()=>[Math.round(TFAC.full()), TFAC.spd()]")
        ok(r==[1,1], f"④ 배부름 1 · 보통 빠르기 {r}")
        await A.evaluate("()=>TFAC.eat('ice cream')")
        ok(await A.evaluate("()=>Math.round(TFAC.full())")==2, "④ 먹으면 🍗 +1")
        await A.evaluate("()=>{ addMat('pizza',1); TFAC.eat('pizza'); }")
        r=await A.evaluate("()=>[Math.round(TFAC.full()), TFAC.spd()]")
        ok(r==[5,1.15], f"④ 🍕 요리 +3 → 배불러서 빨라짐 {r}")
        await A.evaluate("()=>{ localStorage.setItem('hyeng_proto_full', JSON.stringify({h:1, t:Date.now()-3*3600e3})); }")
        await A.reload(); await A.wait_for_timeout(2000)
        ok(await A.evaluate("()=>TFAC.spd()")==0.8, "④ 2시간마다 하트 1개 줄어 → 배고프면 느려짐")
        await A.evaluate("()=>{ gems=500; saveBag(); HOUSE.exitRoom(); }"); await until(A, "()=>HOUSE.place()==='isle' && !HOUSE.trip().busy", 160); await A.wait_for_timeout(800)
        # ⑤ 펫
        await A.evaluate("()=>{ TFAC.openPet(); document.querySelector('#tfPt [data-buy=dog]').click(); }"); await A.wait_for_timeout(200)
        await A.evaluate("()=>document.getElementById('askOk').click()"); await A.wait_for_timeout(300)
        await A.evaluate("()=>document.querySelector('#tfPt [data-nm=Coco]').click()"); await A.wait_for_timeout(1500)
        r=await A.evaluate("()=>[TFAC.PET(), HOUSE.gems(), !!TFAC.petObj(), mats['pet food']|0]")
        ok(r[0] and r[0]["t"]=="dog" and r[0]["n"]=="Coco" and r[1]==170 and r[2] and r[3]==2, f"⑤ 🐶 Coco 데려옴 · 💎330 (v563 ×1.6) · 밥 2 {r[1:]}")
        await A.evaluate("()=>{ const h=HOUSE.hero(); TFAC.warp(h.g.position.x+6, h.g.position.z+2); }"); await A.wait_for_timeout(2500)
        r=await A.evaluate("()=>{ const a=TFAC.petObj().position, b=HOUSE.hero().g.position; return Math.hypot(a.x-b.x,a.z-b.z); }")
        ok(r<1.6, f"⑤ 펫이 나를 따라옴 {r:.2f}")
        await A.evaluate("()=>{ TFAC.openMe(); document.querySelector('#tfMe [data-learn]').click(); }")
        ok(await until(A, "()=>document.getElementById('hqP').classList.contains('on') && /Sit!/.test(document.getElementById('hqP').innerText)", 20), "⑤ 🎓 \"Sit!\" 듣고 고르기")
        await A.evaluate("()=>document.querySelector('#hqP [data-w=sit]').click()"); await until(A, "()=>HOUSE.gems()===172", 30)
        r=await A.evaluate("()=>[TFAC.PET().tr, HOUSE.gems()]")
        ok(r==[["sit"],172], f"⑤ 재주 sit 배움 · 💎2 {r}")
        await A.evaluate("()=>{ TFAC.openMe(); }"); await A.wait_for_timeout(200)
        ok(await A.evaluate("()=>document.querySelector('#tfMe [data-learn]').disabled"), "⑤ 재주는 하루 하나")
        await A.evaluate("()=>{ document.querySelector('#tfMe [data-feed]').click(); }"); await A.wait_for_timeout(300)
        ok(await A.evaluate("()=>(mats['pet food']|0)===1"), "⑤ 🦴 밥 주기")
        await A.evaluate("()=>document.getElementById('tfMe').classList.remove('on')")
        await A.evaluate("()=>HOUSE.publish()"); await A.wait_for_timeout(400)
        ok(DB["hy"]["life"]["h"]["AAAAA"].get("pet")=={"t":"dog","n":"Coco"}, "⑤ 집 기록에 펫 (친구가 놀러 오면 보임)")
        # ⑥ 박물관
        await A.evaluate("()=>{ bag.push({en:'crab', at:Date.now()}); saveBag(); TFAC.openMuseum(); }")
        await until(A, "()=>!!document.querySelector('#tfMu [data-dn=crab].can')", 30)
        await A.evaluate("()=>document.querySelector('#tfMu [data-dn=crab]').click()")
        ok(await until(A, "()=>document.getElementById('hqP').classList.contains('on')", 20), "⑥ 기증 = 이름표 문제")
        g0=await A.evaluate("()=>TECO.coins()")
        await A.evaluate("()=>document.querySelector('#hqP [data-w=crab]').click()")
        ok(await until(A, "()=>!!document.querySelector('#tfMu [data-sy=crab]')", 30), "⑥ 🦀 전시됨")
        r=await A.evaluate("()=>[bag.some(it=>it.en==='crab'), TECO.coins()]")
        ok(r==[False, g0+25] and DB["hy"]["isle"]["museum"]["crab"]["n"]=="루아", f"⑥ 가방에서 빠짐 · 🪙25 (v563) · 서버 {r}")
        await A.evaluate("()=>document.getElementById('tfMu').classList.remove('on')")
        await B.evaluate("()=>{ bag.push({en:'crab', at:Date.now()}); saveBag(); TFAC.openMuseum(); }")
        ok(await until(B, "()=>/루아/.test((document.querySelector('#tfMu [data-sy=crab]')||{}).innerText||'')", 30), "⑥ 하준도 🏷 루아 이름을 봄 (기증 버튼 없음)")
        await B.evaluate("()=>document.getElementById('tfMu').classList.remove('on')")
        # ⑦ 사진관
        await A.evaluate("()=>{ TFAC.openPhoto(); document.querySelector('#tfPh [data-shoot]').click(); }"); await A.wait_for_timeout(1200)
        r=await A.evaluate("()=>{ const A=JSON.parse(localStorage.getItem('hyeng_proto_album')||'[]'); return [A.length, (A[0]||{}).d ? A[0].d.slice(0,15) : '', (A[0]||{}).d ? A[0].d.length : 0, (JSON.parse(localStorage.getItem('hyeng_proto_room')||'{}').s||{}).photo|0]; }")
        ok(r[0]==1 and r[1]=="data:image/jpeg" and 3000<r[2]<120000, f"⑦ 📸 사진 → 앨범 {r}")
        ok(await A.evaluate("()=>stock.photo|0")==1, "⑦ 🖼 액자 → 창고")
        await A.evaluate("()=>document.getElementById('tfPh').classList.remove('on')")
        # ⑧ 도서관
        await A.evaluate("()=>TFAC.openLib()")
        r=await A.evaluate("()=>[...document.querySelectorAll('#tfLb [data-bk]')].map(b=>b.disabled)")
        ok(r==[False,False,False,False,True,True], f"⑧ 공부 6일 = 책 4권 열림 {r}")
        await A.evaluate("()=>document.querySelector('#tfLb [data-bk=\"0\"]').click()")
        for i in range(6): await A.evaluate("()=>document.querySelector('#tfLb [data-next]').click()"); await A.wait_for_timeout(120)
        g0=await A.evaluate("()=>HOUSE.gems()")
        for i in range(2):
            await until(A, "()=>document.getElementById('hqP').classList.contains('on') && !document.querySelector('#hqP .b').dataset.lock", 20)
            await A.evaluate("()=>{ const box=document.querySelector('#hqP .b'), e=box.querySelector('.e').textContent, B=TFAC.BOOKS[0], s=B.p.find(x=>x[0]===e)[1]; box.querySelector('[data-w=\"'+s+'\"]').click(); }")
            await A.wait_for_timeout(1100)
        ok(await until(A, "()=>JSON.parse(localStorage.getItem('hyeng_proto_lib')||'{}').cat===1", 20) and await A.evaluate("()=>HOUSE.gems()")==g0+3, "⑧ 📖 My Cat 다 읽음 ⭐ 💎3")
        await A.evaluate("()=>document.getElementById('tfLb').classList.remove('on')")
        # ⑨ 기차역
        await A.evaluate("()=>{ TECO.setCoin(100); store('hyeng_proto_thalf',0); }"); g0=await A.evaluate("()=>TECO.coins()")
        await A.evaluate("()=>TFAC.ride(TFAC.DEST.find(d=>d[0]==='lake'))")
        ok(await until(A, "()=>/Next stop is the lake/.test(document.getElementById('tfRide').innerText)", 20), "⑨ 🚂 \"Next stop is the lake!\"")
        ok(await until(A, "()=>!!document.querySelector('#tfRide [data-a=lake]')", 30), "⑨ 어디에 도착할까요?")
        await A.evaluate("()=>document.querySelector('#tfRide [data-a=lake]').click()")
        ok(await until(A, "()=>!document.getElementById('tfRide').classList.contains('on')", 20), "⑨ 도착")
        r=await A.evaluate("()=>{ const h=HOUSE.hero().g.position, L=ISLE.SPOT.lake; return [Math.hypot(h.x-L[0],h.z-L[2]), TECO.coins(), TECO.trainFee()]; }")
        ok(r[0]<4 and r[1]==g0-10 and r[2]==5, f"⑨ 호수 앞 · 🎫 표 🪙10 · 맞혀서 다음 표 반값 (v563) {r}")
        await br.close()
        # ⑩ 계절
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        W_=await kid("WWWWW","겨울","&season=winter")
        r=await W_.evaluate("()=>[TFAC.season(), ISLE.G.children.some(o=>o.isPoints)]")
        ok(r==["winter",True], f"⑩ ?season=winter → ❄ 눈 {r}")
        await br.close()
    e=real_errs(errs)
    ok(not e, f"오류 없음 {e[:3]}")
    print("\nFAIL" if bad else "\nPASS", len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
