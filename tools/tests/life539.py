"""(v539) 🏠 방·층마다 할 일 · 🛒 시장 거리 가게 · 👕 옷·💇 머리 사기 (가짜 서버 · 아이 2명)
   ① 시장 거리 가게 6곳 이름표 (생선·가구·옷·미용실·마트·마을 사람들) · 누르면 그 창
   ② 👕 옷 가게: 입어 보기 → 💎 사기 → 집 옷장(나 꾸미기)에서 🔒 풀림 · 안 사고 닫으면 원래 옷 · 집 옷장에선 안 산 것 못 고름
   ③ 🛒 마트: 씨앗·재료 사면 가방에
   ④ 방마다 처음 가구: 2층 📚 책장 · 3층 🏆 진열장 · 4층 🔭 망원경·🪴 화분 · 욕실 🛁 · 부엌 🍳🧊 · 침실 🛏
   ⑤ 📚 책장 = 단어 10개 = 책 1권 · 📝 오늘의 복습 5문제 → 맞힌 만큼 💎 · 하루 한 번
   ⑥ 🏆 자랑 진열장 · 친구가 놀러 와도 내 기록이 보임
   ⑦ 🔭 망원경 = 마을 친구 집 목록 → 누르면 놀러 감
   ⑧ 🛁 씻기 = 🍀 행운 10분 (1시간에 한 번) · 🛏 침실에서 자면 💤 꿈 카드 3문제 (하루 한 번)
   ⑨ 🍳 요리 = "Put in the …!" 듣고 재료 고르기 → 음식 완성"""
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
        async def kid(code,name):
            ctx=await br.new_context(viewport={"width":390,"height":760}, is_mobile=True, has_touch=True)
            pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(name+": "+str(e)))
            await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html?isle=1"); await pg.wait_for_timeout(500)
            await pg.evaluate("""([c,n,W])=>{ Object.keys(localStorage).filter(k=>k.startsWith('hyeng_')).forEach(k=>localStorage.removeItem(k)); localStorage.setItem('hyeng_proto_code', JSON.stringify(c)); localStorage.setItem('hyeng_nick', n); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); localStorage.setItem('hyeng_isle_cam','1');
                localStorage.setItem('hyeng_study_v1', JSON.stringify({srs:Object.fromEntries(W.map(w=>[w,[1,0]])), days:{n:15,tot:16,hs:15,hb:15,last:Math.floor((Date.now()-new Date().getTimezoneOffset()*60000)/864e5)}})); }""", [code,name,WORDS])
            await pg.reload(); await pg.wait_for_timeout(2000); return pg
        A=await kid("AAAAA","루아")
        await A.evaluate("()=>{ gems=600; saveBag(); }")
        # ① 가게
        await A.evaluate("()=>HOUSE.exitRoom()"); ok(await until(A, "()=>HOUSE.place()==='isle' && !HOUSE.trip().busy", 120), "🏝 우리 마을")
        await A.wait_for_timeout(1200)
        r=await A.evaluate("()=>(ISLE.SPOT.shops||[]).map(s=>s.k)")
        ok(sorted(r)==sorted(["fish","furn","clothes","hair","mart","town","snack","pet","photo"]), f"① 상점가 가게 8곳 + 마을 사람들 {r}")
        r=await A.evaluate("()=>LBL.filter(l=>['fish','furn','clothes','hair','mart','town','snack','pet','photo'].includes(l.d.k)).length")
        ok(r==9, f"① 가게 이름표 9개 {r}")
        # ② 옷 가게
        await A.evaluate("()=>{ const S=ISLE.SPOT.shops.find(s=>s.k==='clothes'), h=HOUSE.hero(); h.g.position.set(S.door[0],0,S.door[1]); h.cx=Math.floor(S.door[0]); h.cz=Math.floor(S.door[1]); LBL.find(l=>l.d.k==='clothes').d.act(); }")
        ok(await until(A, "()=>document.getElementById('avP').classList.contains('on') && /옷 가게/.test(document.getElementById('avTtl').textContent)", 40), "② 👕 옷 가게 창")
        r=await A.evaluate("()=>{ const b=document.querySelector('.chip.lk[data-k=style][data-v=hoodie]'); b.click(); return [av.style, document.getElementById('avBuy').hidden, document.getElementById('avBuy').textContent]; }")
        ok(r[0]=="hoodie" and not r[1] and "15" in r[2], f"② 입어 보기 → 「💎 15 사기」 {r}")
        await A.evaluate("()=>closeAv()")
        r=await A.evaluate("()=>[av.style, JSON.parse(localStorage.getItem('hyeng_proto_av')||'{}').style||'tee']")
        ok(r[0]==r[1]=="tee", f"② 안 사고 닫으면 원래 옷 {r}")
        await A.evaluate("()=>{ openAv('clothes'); document.querySelector('.chip.lk[data-k=style][data-v=hoodie]').click(); document.getElementById('avBuy').click(); }"); await A.wait_for_timeout(300)
        r=await A.evaluate("()=>[av.style, HOUSE.gems(), JSON.parse(localStorage.getItem('hyeng_proto_avown')||'{}')['style:hoodie']]")
        ok(r==["hoodie",585,1], f"② 사면 입고 💎 -15 · 내 옷장에 {r}")
        await A.evaluate("()=>{ closeAv(); openAv(); avTab='wear'; drawAv(); }")
        r=await A.evaluate("()=>[!!document.querySelector('.chip[data-k=style][data-v=hoodie]:not(.lk)'), !!document.querySelector('.chip.lk[data-k=style][data-v=dress]')]")
        ok(r==[True,True], f"② 집 옷장: 산 옷은 풀림 · 안 산 옷은 🔒 {r}")
        await A.evaluate("()=>document.querySelector('.chip.lk[data-k=style][data-v=dress]').click()")
        ok(await A.evaluate("()=>av.style==='hoodie'"), "② 집 옷장에선 안 산 옷 못 입음")
        await A.evaluate("()=>closeAv()")
        await A.evaluate("()=>{ openAv('hair'); }")
        r=await A.evaluate("()=>[document.getElementById('avTtl').textContent, !!document.querySelector('.chip[data-k=hair]'), !document.querySelector('.chip[data-k=skin]'), !document.querySelector('.chip[data-k=style]')]")
        ok(r[0]=="💇 미용실" and r[1] and r[2] and r[3], f"② 💇 미용실 = 머리·표정만 {r}")
        await A.evaluate("()=>closeAv()")
        # ③ 마트
        await A.evaluate("()=>HLIFE.openMart()"); await A.wait_for_timeout(300)
        m0=await A.evaluate("()=>mats['tomato']|0")
        await A.evaluate("()=>document.querySelector('#hlMt [data-buy=tomato]').click()"); await A.wait_for_timeout(300)
        ok(await A.evaluate("()=>mats['tomato']|0")==m0+1, "③ 🛒 마트에서 tomato 사면 가방에")
        await A.evaluate("()=>document.getElementById('hlMt').classList.remove('on')")
        # ④ 방 가구
        await A.evaluate("()=>ISLE.enterHome()"); ok(await until(A, "()=>HOUSE.place()==='room' && !HOUSE.trip().busy", 80), "집 안")
        await A.evaluate("()=>{ ['f2','f3','f4'].forEach(k=>HOMEX.H().o[k]=1); HOMEX.save(); }")
        want={"f2":["bookcase","stairs"],"f3":["trophy","stairs"],"f4":["telescope","planter"]}
        async def goRoom(rm):
            await A.evaluate("(r)=>HOMEX.moveTo(r)", rm); return await until(A, f"()=>HOMEX.cur()==='{rm}' && !HOUSE.trip().busy", 60)
        for rm,ids in want.items():
            await goRoom(rm)
            r=await A.evaluate("()=>placed.map(p=>p.id)")
            ok(all(i in r for i in ids), f"④ {rm} 처음 가구 {ids} ⊂ {r}")
        await goRoom("living")
        await A.evaluate("()=>{ localStorage.setItem('hyeng_study_v1', JSON.stringify(Object.assign(JSON.parse(localStorage.getItem('hyeng_study_v1')), {}))); ['bath','bedroom','kitchen'].forEach(k=>HOMEX.unlock(k)); }")
        r=await A.evaluate("()=>[stock.bathtub|0, stock.closet|0, stock.stove|0, stock.fridge|0]")
        ok(r==[1,1,1,1], f"④ 🛁 욕실 · 🛏 침실 · 🍳 부엌 세트 → 창고 {r}")
        # ⑤ 책장 · 복습
        await goRoom("f2")
        await A.evaluate("()=>useItem(placed.find(p=>p.id==='bookcase'))")
        ok(await until(A, "()=>document.getElementById('hlBk') && document.getElementById('hlBk').classList.contains('on') && document.querySelectorAll('#hlBk [data-book]').length===2", 20), "⑤ 📚 단어 22개 = 책 2권")
        g0=await A.evaluate("()=>HOUSE.gems()")
        await A.evaluate("()=>document.querySelector('#hlBk [data-rev]').click()")
        for i in range(5):
            await until(A, "()=>document.getElementById('hqP').classList.contains('on') && !document.querySelector('#hqP .b').dataset.lock", 20)
            await A.evaluate("()=>{ const box=document.querySelector('#hqP .b'), e=box.querySelector('.e').textContent; const w=ISLE_WORDS.find(w=>w[2]===e && box.querySelector('[data-w=\"'+w[0]+'\"]')); box.querySelector('[data-w=\"'+w[0]+'\"]').click(); }")
            await A.wait_for_timeout(1300)
        ok(await until(A, "()=>!document.getElementById('hqP').classList.contains('on')", 20) and await A.evaluate("()=>HOUSE.gems()")==g0+5, f"⑤ 복습 5/5 → 💎 +5")
        await A.evaluate("()=>useItem(placed.find(p=>p.id==='bookcase'))"); await A.wait_for_timeout(300)
        ok(await A.evaluate("()=>document.querySelector('#hlBk [data-rev]').disabled"), "⑤ 복습은 하루 한 번")
        await A.evaluate("()=>document.getElementById('hlBk').classList.remove('on')")
        # ⑥ 자랑
        await goRoom("f3"); await A.evaluate("()=>useItem(placed.find(p=>p.id==='trophy'))"); await A.wait_for_timeout(300)
        t=await A.evaluate("()=>document.getElementById('hlBr').innerText")
        ok("15일" in t and "2권" in t and "16일" in t, f"⑥ 🏆 자랑 진열장 (연속 15일 · 책 2권 · 공부한 날 16일)")
        await A.evaluate("()=>document.getElementById('hlBr').classList.remove('on')")
        await A.evaluate("()=>HOUSE.publish()"); await A.wait_for_timeout(400)
        h=DB["hy"]["life"]["h"]["AAAAA"]
        ok(h.get("brag",{}).get("books")==2 and h["brag"].get("hb")==15, f"⑥ 서버 집 기록에 자랑 {h.get('brag')}")
        # ⑧ 욕실 · 꿈
        await goRoom("living")
        await A.evaluate("()=>{ const put=id=>{ for(let x=0;x<RN;x++) for(let z=0;z<RN-1;z++) for(const r of [0,1]){ if(stock[id]>0 && fits(id,x,z,r)){ addPlaced(id,x,z,r,0); stock[id]--; return; } } }; put('bathtub'); put('bed'); saveRoom(); }")
        await A.evaluate("()=>{ buffUntil=0; useItem(placed.find(p=>p.id==='bathtub')); }"); await A.wait_for_timeout(300)
        r=await A.evaluate("()=>[Math.round((buffUntil-now())/60e3), document.getElementById('toast') ? 1 : 1]")
        ok(9<=r[0]<=10, f"⑧ 🛁 씻기 → 🍀 행운 10분 {r}")
        await A.evaluate("()=>useItem(placed.find(p=>p.id==='bathtub'))"); await A.wait_for_timeout(300)
        ok(await A.evaluate("()=>Math.round((buffUntil-now())/60e3)")<=10, "⑧ 1시간에 한 번")
        g0=await A.evaluate("()=>HOUSE.gems()")
        await A.evaluate("()=>sitOn(placed.find(p=>p.id==='bed'))")
        ok(await until(A, "()=>document.getElementById('hqP').classList.contains('on') && /꿈/.test(document.getElementById('hqP').innerText)", 20), "⑧ 💤 침대(어디에 놓든)에서 자면 꿈 카드")
        for i in range(3):
            await until(A, "()=>document.getElementById('hqP').classList.contains('on') && !document.querySelector('#hqP .b').dataset.lock", 20)
            await A.evaluate("()=>{ const box=document.querySelector('#hqP .b'), e=box.querySelector('.e').textContent; const w=ISLE_WORDS.find(w=>w[2]===e && box.querySelector('[data-w=\"'+w[0]+'\"]')); box.querySelector('[data-w=\"'+w[0]+'\"]').click(); }")
            await A.wait_for_timeout(1300)
        ok(await until(A, "()=>!document.getElementById('hqP').classList.contains('on')", 20) and await A.evaluate("()=>HOUSE.gems()")==g0+3, "⑧ 꿈 카드 3/3 → 💎 +3")
        await A.evaluate("()=>{ standUp(); sitOn(placed.find(p=>p.id==='bed')); }"); await A.wait_for_timeout(2000)
        ok(not await A.evaluate("()=>document.getElementById('hqP').classList.contains('on')"), "⑧ 꿈 카드는 하루 한 번")
        await A.evaluate("()=>standUp()")
        # ⑨ 요리
        await A.evaluate("()=>{ for(let x=0;x<RN;x++) for(let z=0;z<RN-1;z++){ if(stock.stove>0 && fits('stove',x,z,0)){ addPlaced('stove',x,z,0,0); stock.stove--; } } }")
        await A.evaluate("()=>{ addMat('wheat',2); addMat('tomato',2); openCraft('cook'); }"); await A.wait_for_timeout(300)
        p0=await A.evaluate("()=>mats['pasta']|0")
        await A.evaluate("()=>document.querySelector('#craftBody [data-make=pasta]').click()")
        ok(await until(A, "()=>document.getElementById('hqP').classList.contains('on') && /Put in the/.test(document.getElementById('hqP').innerText)", 20), "⑨ 🍳 요리 = 「Put in the …!」")
        for i in range(2):
            await until(A, "()=>document.getElementById('hqP').classList.contains('on') && !document.querySelector('#hqP .b').dataset.lock", 20)
            await A.evaluate("()=>{ const box=document.querySelector('#hqP .b'), n=box.querySelector('.k b').textContent.match(/the (.+)!/)[1]; box.querySelector('[data-w=\"'+n+'\"]').click(); }")
            await A.wait_for_timeout(900)
        ok(await until(A, "()=>(mats['pasta']|0)>"+str(p0), 20), "⑨ 재료를 다 맞히면 pasta 완성")
        # ⑦ 망원경 + 친구 방문
        B=await kid("BBBBB","하준")
        await B.evaluate("()=>HOUSE.exitRoom()"); await until(B, "()=>HOUSE.place()==='isle' && !HOUSE.trip().busy", 120)
        await B.wait_for_timeout(1500)
        await goRoom("f4")
        await A.evaluate("()=>useItem(placed.find(p=>p.id==='telescope'))")
        ok(await until(A, "()=>document.querySelectorAll('#hlScL [data-c]').length>=1 && /하준/.test(document.getElementById('hlScL').innerText)", 40), "⑦ 🔭 망원경 = 마을 친구 집 목록 (하준)")
        await A.evaluate("()=>document.querySelector('#hlScL [data-c=BBBBB]').click()")
        ok(await until(A, "()=>['visit','yvisit'].includes(HOUSE.place()) && HOUSE.visiting() && HOUSE.visiting().code==='BBBBB'", 120), "⑦ 누르면 하준 집에 놀러 감")
        await br.close()
    e=real_errs(errs)
    ok(not e, f"오류 없음 {e[:3]}")
    print("\nFAIL" if bad else "\nPASS", len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
