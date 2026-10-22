"""(v305) 🏠 주간 보스 — 이 기기 안 Firebase 흉내(HY_FB_LOCAL), 선생님 1 · 아이 2
   켜기 → 이번 주 1번 보스(체력 = 인원 × 400, 최소 500) · 🏃 달리기 하루 100 · 📚 공부 합쳐 300 · 쓰러뜨림 → 보상 똑같이 · 한 번만
   다음 주 → 2번 보스 + 지난주 보상 · 못 잡으면 도망(깎은 % × 40%) · 반 대항전에 반 없는 아이는 공격 안 됨 · 레이드 입장 창 폭 · 없는 방 번호"""
import asyncio, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright
END = """()=>{ Online.on=()=>false; G.set='basic'; G.lesson=0; G.rule='normal'; G.diff='normal'; G.testRun=false; G.practice=false; G.cleared=false; G.quit=true;
  G.score=900; G.stage=10; G.zone=1; G.right=80; G.wrong=1; G.running=false; G.skipOutro=true; G.overFade=false; G._overDone=false; gameOver(); G.skipOutro=false; }"""
OVB = "()=>{ const o=document.querySelector('.ovBoss'); return o?o.innerText:''; }"
WEEK = "(d)=>{ const kk=Kid.get(); if(!window._n0) window._n0=Date.now; Date.now=()=>window._n0()+d*864e5; if(kk) Kid.set(kk); HyBoss.calc(); return HyBoss.refresh(true).then(()=>[HyBoss.B&&HyBoss.B.i, HyBoss.B&&HyBoss.B.n, HyBoss.P&&HyBoss.P.n]); }"
async def main():
    bad=[]; errs=[]
    async with async_playwright() as p:
        br=await p.chromium.launch(); ctx=await br.new_context(viewport={"width":1024,"height":760})
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        host=await ctx.new_page(); host.on("pageerror", lambda e: errs.append("H "+str(e))); await boot(host)
        await host.evaluate("""()=>{ HyBoss.live(); return FB.set('/hy/roster', {t:{ta:{n:'사자반',e:'🦁'}, tb:{n:'돌고래반',e:'🐬'}}, k:{k1:{n:'민준',t:'ta'}, k2:{n:'서연',t:'tb'}}}); }"""); await host.wait_for_timeout(300)
        await host.evaluate("()=>HyBoss.setup({on:true, team:false, split:'eq', restart:true})"); await host.wait_for_timeout(400)
        b=await host.evaluate("()=>[HyBoss.B.i, HyBoss.B.img, HyBoss.B.max.all, HyBoss.B.gems, HyBoss.B.team]"); print("week0", b)
        if b!=[0,"hb1",5000,500,False]: bad.append(f"1번 보스 {b}")
        kids=[]
        for kid,nm,t in [("k1","민준","ta"),("k2","서연","tb")]:
            k=await ctx.new_page(); k.on("pageerror", lambda e,n=nm: errs.append(n+" "+str(e))); await k.set_viewport_size({"width":390,"height":844}); await boot(k)
            await k.evaluate(f"()=>{{ localStorage.setItem('hyeng_nick','한양패드'); Kid.set({{id:'{kid}',n:'{nm}',t:'{t}'}}); HyBoss.start(); return HyBoss.refresh(true); }}"); kids.append(k)
        k1,k2=kids
        # (v312) 달리기 = ⚔️ 공격 기회 (맞힌 4단어 = 1번 · 🏃 10까지) — 데미지는 보스 화면에서 휘둘러야
        await k1.evaluate(END); await k1.wait_for_timeout(500); t1=await k1.evaluate(OVB); r1=await k1.evaluate("()=>[HyBoss.mine('k1').d|0, JSON.stringify(HyBoss.stock('k1'))]"); print("run1", t1, r1)
        if r1!=[0,'{"r":10,"s":0}'] or "+10" not in t1: bad.append(f"달리기 = 공격 기회 10 {r1} {t1}")
        await k1.screenshot(path=OUT+"week_over.png")
        await k1.evaluate(END); await k1.wait_for_timeout(500); t2=await k1.evaluate(OVB); print("run2", t2)
        if "가득" not in t2: bad.append("달리기 기회 10 넘음")
        e3=await k1.evaluate("()=>[HyBoss.earn(Kid.get(),'study',99), HyBoss.earn(Kid.get(),'study',1), JSON.stringify(HyBoss.stock('k1'))]"); print("study earn", e3)
        if e3!=[10,0,'{"r":10,"s":10}']: bad.append(f"데일리 기회 10 {e3}")
        u=await k1.evaluate("()=>[HyBoss.use(Kid.get()), JSON.stringify(HyBoss.stock('k1')), HyBoss.use(Kid.get()), JSON.stringify(HyBoss.stock('k1'))]"); print("use", u)
        if u!=[True,'{"r":9,"s":10}',True,'{"r":9,"s":9}']: bad.append(f"기회 쓰기 {u}")
        a3=await k1.evaluate("()=>HyBoss.add(Kid.get(), 999, 'study', 3)"); print("study", a3)
        if a3!=400: bad.append(f"하루 400 {a3}")
        # 서연 — 다른 기기에서 읽으면 민준 300 이 보임 (서버 더하기)
        s2=await k2.evaluate("()=>HyBoss.refresh(true).then(()=>[HyBoss.state('all').sum, HyBoss.mine('k1').d, JSON.stringify(HyBoss.D)])"); print("k2 sees", s2)
        if s2[:2]!=[400,400]: bad.append(f"다른 기기에서 데미지 {s2}")
        sk=await k2.evaluate("()=>JSON.stringify(HyBoss.stock('k1'))"); print("k2 sees stock", sk)
        if sk!='{"r":9,"s":9}': bad.append(f"다른 기기에서 공격 기회 {sk}")
        await k2.evaluate("()=>{ HyBoss.CAP=9999; }")
        a4=await k2.evaluate("()=>HyBoss.add(Kid.get(), 9999, 'study', 3)"); print("kill", a4)
        if a4!=4600: bad.append(f"남은 체력만큼만 {a4}")
        d=await k1.evaluate("()=>HyBoss.refresh(true).then(()=>[!!HyBoss.state('all').dead, HyBoss.state('all').dead.by, HyBoss.reward(Kid.get())])"); print("dead", d)
        if d!=[True,"서연",250]: bad.append(f"쓰러뜨림·보상 500÷2 {d}")
        await k1.evaluate("()=>{ show('scStudy'); StudyUI.path(); }"); await k1.wait_for_timeout(400)
        card=await k1.evaluate("()=>document.getElementById('stBossCard').innerText"); print("card", card.replace("\n"," / "))
        if "보상 받기" not in card: bad.append("카드 보상")
        await k1.screenshot(path=OUT+"week_card_dead.png")
        g0=await k1.evaluate("()=>Wallet.gems()"); await k1.click("[data-bossclaim='1']"); await k1.wait_for_timeout(300)
        g1=await k1.evaluate("()=>[Wallet.gems(), HyBoss.claim(Kid.get())]"); print("claim", g0, g1)
        if g1[0]-g0!=250 or g1[1]!=0: bad.append(f"보상 한 번 {g0} {g1}")
        # 다음 주 — 2번 보스 · 지난주 보상(서연은 아직)
        w1=await k2.evaluate(WEEK, 7); print("week1", w1)
        if w1[0]!=1 or w1[2]!="초원 수호자": bad.append(f"다음 주 2번 보스 {w1}")
        pr=await k2.evaluate("()=>[HyBoss.prevReward(Kid.get()), HyBoss.claim(Kid.get(), true), HyBoss.prevReward(Kid.get())]"); print("prev", pr)
        if pr!=[250,250,0]: bad.append(f"지난주 보상 {pr}")
        await k2.evaluate("()=>{ show('scStudy'); StudyUI.path(); }"); await k2.wait_for_timeout(300); await k2.screenshot(path=OUT+"week_card_new.png")
        # 2번 보스 조금만 깎고 → 그다음 주: 도망 보상
        await k2.evaluate("()=>HyBoss.add(Kid.get(), 100, 'study', 3)")
        w2=await k2.evaluate(WEEK, 14); pe=await k2.evaluate("()=>{ const P=HyBoss.P, s=HyBoss.stateOf(P, HyBoss.PD, 'all'); return [!!s.dead, s.max, HyBoss.prevReward(Kid.get())]; }"); print("escape", w2, pe)
        if pe[0] or pe[2]<1 or pe[2]>10: bad.append(f"도망 보상 {pe}")
        await k2.evaluate("()=>StudyUI.bossCard()"); await k2.wait_for_timeout(100)
        card2=await k2.evaluate("()=>document.getElementById('stBossCard').innerText"); print("card2", card2.replace("\n"," / "))
        if "보상 받기" not in card2 or not await k2.evaluate("()=>!!document.querySelector('#stBossCard [data-bossclaim=\"prev\"]')"): bad.append("도망 보상 버튼 (지난주)")
        await k2.screenshot(path=OUT+"week_card_escape.png")
        # 반 대항전 — 반 없는 아이는 공격 안 됨
        await host.evaluate("()=>{ window._n0=null; HyBoss.setup({on:true, team:true, split:'eq', restart:true}); }"); await host.wait_for_timeout(400)
        tm=await host.evaluate("()=>[HyBoss.B.team, Object.keys(HyBoss.B.max).sort(), HyBoss.B.max.ta]"); print("team", tm)
        if tm!=[True,["ta","tb"],5000]: bad.append(f"반 대항 보스 {tm}")
        k3=await ctx.new_page(); k3.on("pageerror", lambda e: errs.append("K3 "+str(e))); await boot(k3)
        nt=await k3.evaluate("()=>{ localStorage.setItem('hyeng_nick','한양패드'); Kid.set({id:'zz',n:'손님',t:'all'}); HyBoss.start(); return HyBoss.refresh(true).then(()=>[HyBoss.team('zz', Kid.get()), HyBoss.add(Kid.get(), 50, 'study')]); }"); print("no team", nt)
        if nt!=[None,0]: bad.append(f"반 없는 아이 {nt}")
        # 레이드 입장 창 — 휴대폰 폭 · 없는 방
        for w in (320,375):
            await k3.set_viewport_size({"width":w,"height":700}); await k3.evaluate("()=>{ RaidJoin.close(); RaidJoin.open(1); }"); await k3.wait_for_timeout(150)
            r=await k3.evaluate("()=>{ const b=document.querySelector('.rdJoinIn').getBoundingClientRect(); return [Math.round(b.left), Math.round(b.right)]; }"); print("join", w, r)
            if r[0]<0 or r[1]>w: bad.append(f"입장 창이 화면 밖 {w} {r}")
        await k3.evaluate("()=>{ RaidJoin.pick=Kid.get(); document.getElementById('rdRoomIn').value='4321'; document.querySelector('[data-rj=go]').click(); }"); await k3.wait_for_timeout(500)   # (v383) 공용 패드는 이름을 먼저 골라야 함
        jm=await k3.evaluate("()=>[!!document.getElementById('rdJoin'), (document.getElementById('rdJoinMsg')||{}).textContent]"); print("no room", jm)
        if not jm[0] or "확인" not in (jm[1] or ""): bad.append(f"없는 방 {jm}")
        await k3.screenshot(path=OUT+"join_320.png")
        print("errs", errs[:5]); await br.close()
    print("결과:", "통과 ✅" if not bad and not errs else "실패 ❌"); [print(" BAD", b) for b in bad]
    if bad or errs: sys.exit(1)
asyncio.run(main())
