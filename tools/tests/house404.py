"""(v404) 🏡 생활 모드 맛보기 (proto/house.html) — 진짜 3D(swiftshader)
  ① 집: 가구 6개 · 뒤쪽 벽 2개 · 내 아바타 · 누른 칸까지 걸어감(가구 피함) · 가구 놓기/창고 넣기
  ② 마당: 연못을 누르면 연못 옆으로 걸어가 찌를 던짐 → 입질 → 톡 → 잡음(영어 이름만 · 문제 없음) → 물고기 도감 +1 · 미끼 −1
     (사용자: 영어 문제로 묶지 말고 아이템 이름을 영어로만 — 가구·도감·꾸미기 이름 영어)
  ③ 입질 전에 톡 = 미끼 돌려받고 끝 · 입질 뒤 늦으면 놓침 · 미끼 0 이면 못 던짐
  ⑥ 가방·가게: 잡으면 가방 · 신선도(2시간 그대로→48시간 0) · 시간마다 값(0.5~1.7배, 같은 시간 같은 값) · 팔면 맛보기 보석
  ⑦ 농사·모으기·만들기·요리: 심기(씨앗 필요) · 물 안 주면 멈춤 · 물 12시간 동안 자람 · 수확 · 나무 사과(시간 지나야 다시) · 바위 · 제작대 · 요리 · 먹으면 🍀
  ⑧ 가방 칸(겹치기·꽉 참·큰 가방) · 음식 값 = 재료 × 1.3
  ⑨ 마을·NPC·지도: 길로 이동 · NPC 돌아다님 · 말 걸기(영어+한국어) · 하루 부탁 → 💎·❤️ · 다음 날 새 부탁 · 지도(잠긴 구역)
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
        q=await pg.evaluate("()=>({fish:HOUSE.F.fish.en, name:document.getElementById('qAsk').innerText.trim(), ko:/[가-힣]/.test(document.getElementById('qAsk').innerText+document.getElementById('qFish').innerText), opts:document.querySelectorAll('#qOpts button[data-en]').length})")
        ok(q["name"]==q["fish"] and not q["ko"] and q["opts"]==0, f"문제 없이 영어 이름만 (한국어 없음) {q}")
        ok(await pg.evaluate("(f)=>HOUSE.dex()[f]===1", q["fish"]), "잡으면 바로 도감 +1")
        await pg.evaluate("()=>{ if(document.getElementById('quiz').classList.contains('on')) document.getElementById('qOk').click(); }"); await pg.wait_for_timeout(200)   # 2.6초 뒤 저절로 닫힐 수 있음
        await until("()=>HOUSE.F.st==='idle'", 20)
        # ③ 일찍 누름 = 미끼 돌려받음 · 늦으면 놓침 · 미끼 0
        b1=await pg.evaluate("()=>HOUSE.bait()")
        await pg.evaluate("()=>HOUSE.tryFish(7,6)"); await until("()=>HOUSE.F.st==='wait'")
        await pg.evaluate("()=>{ HOUSE.F.nib=[]; HOUSE.F.T=99; }"); await pg.wait_for_timeout(100)
        await pg.evaluate("()=>HOUSE.tapWhileFishing()")
        ok(await pg.evaluate("()=>HOUSE.F.st")=="idle" and await pg.evaluate("()=>HOUSE.bait()")==b1, "입질 전 톡 → 끝 · 미끼 돌려받음")
        await pg.evaluate("()=>HOUSE.tryFish(7,6)"); await until("()=>HOUSE.F.st==='wait'")
        await pg.evaluate("()=>HOUSE.bite()"); ok(await until("()=>HOUSE.F.st==='idle'", 60), "입질 뒤 1초 넘게 안 누르면 놓침")
        ok(await pg.evaluate("()=>HOUSE.bait()")==b1-1, "놓쳐도 미끼는 씀")
        await pg.evaluate("()=>HOUSE.setBait(0)"); await pg.evaluate("()=>HOUSE.tryFish(7,6)"); await pg.wait_for_timeout(300)
        ok(await pg.evaluate("()=>HOUSE.F.st")=="idle" and "미끼" in await pg.evaluate("()=>document.getElementById('toast').innerText"), "미끼 0 → 못 던지고 안내")
        await pg.screenshot(path=OUT+"life_yard.png")
        # ⑥ 🎒 가방 · 🏪 가게 — 잡은 건 가방으로 · 신선도 · 시간별 값 · 팔면 보석
        ok(await pg.evaluate("(f)=>HOUSE.bag().some(it=>it.en===f)", q["fish"]), "잡은 물고기는 가방에")
        await pg.evaluate("()=>{ const n=Date.now(); const b=HOUSE.bag(); b.length=0; b.push({en:'shark',at:n},{en:'shark',at:n-47*3600e3},{en:'boot',at:n-200*3600e3}); }")
        pr=await pg.evaluate("()=>HOUSE.bag().map(it=>[HOUSE.price(it), HOUSE.fresh(it)])")
        ok(pr[0][1]==1 and pr[1][1]<0.05 and pr[0][0]>pr[1][0]*3, f"오래된 상어는 값이 크게 떨어짐 {pr}")
        ok(pr[2][1]==1, "장화는 안 상함")
        m=await pg.evaluate("()=>{ const h=HOUSE.hourIx(); const L=[]; for(let i=0;i<24;i++) L.push(+HOUSE.mkt('shark',h+i).toFixed(3)); return L; }")
        ok(len(set(m))>12 and min(m)>=0.5 and max(m)<=1.7, f"시세가 시간마다 바뀜 (0.5~1.7) {min(m)}~{max(m)}")
        ok(await pg.evaluate("()=>HOUSE.mkt('crab',123456)===HOUSE.mkt('crab',123456)"), "같은 시간 = 같은 값 (모든 기기)")
        f0=await pg.evaluate("()=>HOUSE.fresh(HOUSE.bag()[0])"); await pg.evaluate("()=>HOUSE.ffwd(30)"); f1=await pg.evaluate("()=>HOUSE.fresh(HOUSE.bag()[0])")
        ok(f1<f0, f"시간이 지나면 신선도 내려감 {f0}→{f1:.2f}")
        await pg.evaluate("()=>HOUSE.goShop()"); ok(await until("()=>document.getElementById('shopP').classList.contains('on')"), "🏪 → 가게까지 걸어가 열림")
        g0=await pg.evaluate("()=>HOUSE.gems()"); v=await pg.evaluate("()=>HOUSE.price(HOUSE.bag()[0])")
        await pg.click('#shopBag [data-sell="0"]'); await pg.wait_for_timeout(200)
        ok(await pg.evaluate("()=>HOUSE.gems()")==g0+v and await pg.evaluate("()=>HOUSE.bag().length")==2, f"sell → 💎 +{v}")
        await pg.click("#sellAll"); await pg.wait_for_timeout(200)
        ok(await pg.evaluate("()=>HOUSE.bag().length")==0 and await pg.evaluate("()=>localStorage.getItem('hyeng_proto_gems')")==str(await pg.evaluate("()=>HOUSE.gems()")), "모두 팔기 · 보석 저장(게임 보석과 따로)")
        ok(await pg.evaluate("()=>!localStorage.getItem('hyeng_wallet_v1') || !JSON.parse(localStorage.getItem('hyeng_wallet_v1')).log.some(l=>/Fish|가게/.test(l[2]))"), "게임 지갑은 안 건드림")
        await pg.click("#shopDone")
        # ⑦ 🌱 농사 · 🪵 모으기 · 🛠 만들기 · 🍳 요리
        await pg.evaluate("()=>{ const m=HOUSE.mats(); Object.keys(m).forEach(k=>delete m[k]); Object.assign(m, {'carrot seeds':1,'pumpkin seeds':1, branch:4}); }")
        ok(await pg.evaluate("()=>HOUSE.plant(0,'carrot') && !HOUSE.plant(0,'pumpkin')"), "씨앗 심기 · 심은 밭엔 또 못 심음")
        ok(await pg.evaluate("()=>!HOUSE.plant(1,'tomato')"), "없는 씨앗은 못 심음")
        await pg.evaluate("()=>HOUSE.ffwd(20)"); ok(await pg.evaluate("()=>HOUSE.plotStage(0)")=="sprout", "물을 안 주면 자라지 않음 (시들지도 않음)")
        await pg.evaluate("()=>HOUSE.water(0)"); await pg.evaluate("()=>HOUSE.ffwd(6)"); st6=await pg.evaluate("()=>HOUSE.plotStage(0)")
        await pg.evaluate("()=>HOUSE.ffwd(7)"); st13=await pg.evaluate("()=>HOUSE.plotStage(0)")
        ok(st6 in ("small","big") and st13=="ripe", f"물 주면 진짜 시간으로 자람 6시간 {st6} · 13시간 {st13}")
        ok(await pg.evaluate("()=>HOUSE.harvest(0)")==2 and await pg.evaluate("()=>HOUSE.mats().carrot")==2 and await pg.evaluate("()=>HOUSE.plotStage(0)")=="empty", "수확 → carrot ×2 · 밭 비움")
        await pg.evaluate("()=>{ HOUSE.plant(1,'pumpkin'); HOUSE.water(1); HOUSE.ffwd(30); }"); ok(await pg.evaluate("()=>HOUSE.plotStage(1)")!="ripe", "물 효과는 12시간 — 호박(48시간)은 다시 물을 줘야 함")
        a0=await pg.evaluate("()=>HOUSE.mats().apple|0"); await pg.evaluate("()=>{ HOUSE.ffwd(30); HOUSE.regen(); HOUSE.shakeTree(0); }")
        a1=await pg.evaluate("()=>HOUSE.mats().apple|0"); ok(a1>a0, f"나무 흔들기 → apple {a0}→{a1}")
        a2=await pg.evaluate("()=>{ HOUSE.shakeTree(0); return HOUSE.mats().apple|0; }"); ok(a2==a1, "바로 또 흔들면 사과 없음 (시간이 지나야 열림)")
        s0=await pg.evaluate("()=>HOUSE.mats().stone|0"); await pg.evaluate("()=>HOUSE.hitRock(0)"); ok(await pg.evaluate("()=>HOUSE.mats().stone|0")==s0+1, "바위 → stone +1")
        ok(await pg.evaluate("()=>HOUSE.make('craft','chair')") and await pg.evaluate("()=>HOUSE.stock.chair")>=1, "🛠 branch 4 → chair (집 창고로)")
        ok(not await pg.evaluate("()=>HOUSE.make('craft','lamp')"), "재료가 모자라면 못 만듦")
        await pg.evaluate("()=>HOUSE.addMat('wheat',2)"); ok(await pg.evaluate("()=>HOUSE.make('cook','bread')") and await pg.evaluate("()=>HOUSE.mats().bread")==1, "🍳 wheat 2 → bread")
        await pg.evaluate("()=>HOUSE.openBag()"); await pg.wait_for_timeout(300); await pg.click('[data-slot="bread"]'); await pg.wait_for_timeout(200)
        info=await pg.evaluate("()=>document.getElementById('bagInfo').innerText")
        ok("bread" in info and "💎" in info, "가방 칸을 누르면 자세히 (이름·값)")
        await pg.click('#bagInfo [data-act="eat"]'); await pg.wait_for_timeout(200)
        ok(await pg.evaluate("()=>HOUSE.buff()>Date.now()+8*60e3") and not await pg.evaluate("()=>HOUSE.mats().bread"), "음식 먹기 → 🍀 lucky 10분")
        await pg.click("#bagDone")
        # ⑧ 가방 칸 — 같은 것은 겹침(물고기 10 · 나머지 30) · 20칸 꽉 차면 못 담음 · 👜 큰 가방 30칸 · 음식 값 = 재료 × 1.3
        fp=await pg.evaluate("()=>HOUSE.COOK.map(r=>[r.id, r.base, HOUSE.MAT[r.id].p])")
        ok(all(p_==-(-b_*13//10) and p_>b_ for _,b_,p_ in fp), f"음식 기준 값 = 재료 합 × 1.3 (조금 더 비쌈) {fp[:3]}")
        await pg.evaluate("()=>{ const m=HOUSE.mats(); Object.keys(m).forEach(k=>delete m[k]); HOUSE.bag().length=0; HOUSE.addMat('wheat',45); }")
        ok(await pg.evaluate("()=>HOUSE.slots().length")==2, "wheat 45 = 2칸 (30씩 겹침)")
        await pg.evaluate("()=>{ ['apple','branch','stone','carrot','tomato','potato','strawberry','pumpkin','bread','fries','pasta','jam','fruit salad','apple pie','pumpkin pie','fish stew','carrot seeds','tomato seeds'].forEach(n=>HOUSE.addMat(n,1)); }")
        ok(await pg.evaluate("()=>HOUSE.slots().length")==20 and not await pg.evaluate("()=>HOUSE.canAdd('wheat seeds',1)") and await pg.evaluate("()=>HOUSE.canAdd('apple',5)"), "20칸 꽉 → 새 것은 못 담고, 있는 칸엔 겹쳐 담음")
        await pg.evaluate("()=>HOUSE.addMat('branch',6)"); await pg.evaluate("()=>{ HOUSE.addMat('stone',4); HOUSE.addMat('apple',2); }")
        ok(await pg.evaluate("()=>HOUSE.make('craft','bag')") and await pg.evaluate("()=>HOUSE.bagCap()")==30 and await pg.evaluate("()=>HOUSE.canAdd('wheat seeds',1)"), "👜 big bag 만들면 30칸")
        # ⑨ 🏘 마을 · NPC · 지도
        await pg.evaluate("()=>HOUSE.walkTo(9,8)"); await arrive()
        await pg.evaluate("()=>HOUSE.go('village')"); await pg.wait_for_timeout(900)
        ok(await pg.evaluate("()=>HOUSE.place()")=="village" and await pg.evaluate("()=>HOUSE.npcs.length")==4, "마당 오른쪽 아래 길 → 🏘 마을 · NPC 4명")
        p0=await pg.evaluate("()=>HOUSE.npcs.map(c=>[c.cx,c.cz])")
        p1=p0
        for _ in range(12):
            await pg.evaluate("()=>HOUSE.npcs.forEach(c=>{ if(!c.moving) c.wait=Math.min(c.wait,0.05); })"); await pg.wait_for_timeout(1500)
            p1=await pg.evaluate("()=>HOUSE.npcs.map(c=>[c.cx,c.cz])")
            if p1!=p0: break   # 느린 그래픽(swiftshader)이라 기다림을 줄여서 확인
        ok(p0!=p1, f"NPC 가 돌아다님 {p0}→{p1}")
        ok(await pg.evaluate("()=>[HOUSE.enCount('carrot',2),HOUSE.enCount('wheat',3),HOUSE.enCount('apple',1),HOUSE.enCount('bread',1),HOUSE.enCount('potato',2)].join('|')")=="2 carrots|3 wheat|an apple|some bread|2 potatoes", "부탁 영어 개수 말 (2 carrots · 3 wheat · an apple · some bread)")
        async def to_choices():
            for _ in range(12):
                if await pg.evaluate("()=>document.getElementById('dlgCh').classList.contains('on')"): return True
                await pg.evaluate("()=>HOUSE.tapDlg()"); await pg.wait_for_timeout(250)
            return False
        r=await pg.evaluate("()=>HOUSE.todayReq(HOUSE.npcs[0].n)")
        await pg.evaluate("(r)=>{ HOUSE.addMat(r[0], r[1]); }", r)
        await pg.evaluate("()=>HOUSE.talkTo(HOUSE.npcs[0])"); await pg.wait_for_timeout(300)
        ok(await pg.evaluate("()=>document.getElementById('dlg').classList.contains('on') && document.getElementById('dlgName').textContent==='Mia'"), "말 걸면 대화창 + 이름표")
        await pg.evaluate("()=>HOUSE.tapDlg()"); await pg.wait_for_timeout(100)   # 글자 다 보이기
        tl=await pg.evaluate("()=>document.getElementById('dlgEn').textContent+' | '+document.getElementById('dlgKo').textContent")
        ok("Mia" in tl and any('가'<=ch<='힣' for ch in tl), f"처음엔 자기소개 (영어 + 한국어 작게) {tl[:50]!r}")
        ok(await to_choices(), "▼ 넘기면 내 대답 고르기")
        ch=await pg.evaluate("()=>[...document.querySelectorAll('#dlgCh .dch')].map(b=>b.dataset.ch)")
        ok(ch[:2]==["mood","help"] and "give" in ch and "seeds" in ch and ch[-1]=="bye", f"대답: 안부·도와줄까·주기·씨앗(Mia)·잘 있어 {ch}")
        g0=await pg.evaluate("()=>HOUSE.gems()"); h0=await pg.evaluate("()=>HOUSE.npcSt().mia.h")
        await pg.click('#dlgCh [data-ch="give"]'); await pg.wait_for_timeout(300)
        ok(await pg.evaluate("()=>HOUSE.gems()")>g0 and await pg.evaluate("()=>HOUSE.npcSt().mia.h")==h0+1, f"🎁 Here you are! → 💎 + ❤️ {r}")
        ok(await to_choices() and "give" not in await pg.evaluate("()=>[...document.querySelectorAll('#dlgCh .dch')].map(b=>b.dataset.ch)"), "준 뒤엔 주기 대답이 없어짐")
        await pg.click('#dlgCh [data-ch="bye"]'); await pg.wait_for_timeout(200)
        for _ in range(8):
            if not await pg.evaluate("()=>!!HOUSE.dlg()"): break
            await pg.evaluate("()=>HOUSE.tapDlg()"); await pg.wait_for_timeout(400)
        ok(not await pg.evaluate("()=>!!HOUSE.dlg()") and not await pg.evaluate("()=>document.getElementById('dlg').classList.contains('on')"), "👋 Bye → 대화 끝")
        ok(not await pg.evaluate("()=>HOUSE.giveReq(HOUSE.npcs[0].n)"), "같은 날 또는 안 됨")
        d0=await pg.evaluate("()=>HOUSE.dayKey()"); await pg.evaluate("()=>HOUSE.ffwd(24)"); d1=await pg.evaluate("()=>HOUSE.dayKey()")
        ok(d0!=d1 and await pg.evaluate("()=>HOUSE.npcSt().mia.done!==HOUSE.dayKey()"), "다음 날 = 새 부탁")
        await pg.evaluate("()=>HOUSE.closeTalk()")
        await pg.click("#bMap"); await pg.wait_for_timeout(300)
        mp=await pg.evaluate("()=>[...document.querySelectorAll('#mapBody .mapC')].map(b=>[b.dataset.go,b.disabled])")
        ok(len(mp)==6 and [m[1] for m in mp]==[False,False,False,True,True,True], f"🗺 지도: 집·마당·마을 열림 · 숲·바닷가·광산 잠김 {mp}")
        await pg.click('#mapBody [data-go="yard"]'); await pg.wait_for_timeout(900)
        ok(await pg.evaluate("()=>HOUSE.place()")=="yard", "지도에서 마당으로")
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
