"""(v322) 🏠 주간 보스 점검 고친 것 — 이 기기 안 Firebase 흉내(HY_FB_LOCAL)
   테스트 슬라임 중 보스 바꾸기 → 기회가 되살아나지 않음 · 같은 주 끄고 켜기 = 그대로 · ↺ 다시 = 기회 옮김 + 쓰러뜨린 보스 보상 남음
   주 중간 반 옮기기 → 데미지 반 = 보이는 반 = 보상 반 · 두 태블릿: 오래된 화면은 먼저 읽고 때림 · 쓰러짐 이름 안 덮음
   같은 아이 두 기기 기회(더하기 카운터) · 1단어 그만두기 = 내림 + 다음 판에 이어서 · 월요일 0시 넘으면 새 보스 · 경고 중 닫기 = (v390) 손해 없음"""
import asyncio, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright
ROSTER = "(r)=>FB.set('/hy/roster', r).then(()=>HyBoss.setup({on:true, team:Object.keys(r.t||{}).length>1, split:'eq', restart:true}))"
QUIT = """(o)=>{ Online.on=()=>false; Object.assign(G, {set:'elem', book:null, lesson:0, rule:'normal', diff:'normal', testRun:false, practice:false, cleared:false, quit:true,
  score:100, stage:1, zone:0, wrong:0, bestCombo:1, running:false, skipOutro:true, overFade:false, _overDone:false}, o||{}); gameOver(); G.skipOutro=false; }"""
SRV = "(k)=>FB.get('/hy/dmg/'+HyBoss.B.id+'/'+k).then(v=>HyBoss.clampStk(HyBoss.rawStk(v)))"
async def main():
    bad=[]; errs=[]
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(); ctx=await br.new_context(viewport={"width":390,"height":844})
        await ctx.add_init_script("window.HY_FB_LOCAL=true; localStorage.setItem('hyeng_nick','한양패드');")
        T=await ctx.new_page(); T.on("pageerror", lambda e: errs.append("T "+str(e))); await boot(T)
        await T.evaluate("()=>HyBoss.live()")
        await T.evaluate(ROSTER, {"t":{}, "k":{"k1":{"n":"민준"},"k2":{"n":"서연"}}}); await T.wait_for_timeout(400)
        E=T.evaluate
        await E("()=>{ window.confirm=()=>true; Kid.set({id:'k1',n:'민준',t:'all'}); HyBoss.earn(Kid.get(),'study',10); HyBoss.earn(Kid.get(),'run',10); }"); await T.wait_for_timeout(200)
        # 1. 🧪 테스트 슬라임에서 기회를 쓰고 다른 보스를 고르면 — 쓴 기회가 되살아나지 않음
        await E("()=>HyBoss.testWeek(true)"); await T.wait_for_timeout(300)
        await E("()=>{ for(let i=0;i<15;i++) HyBoss.use(Kid.get()); }"); await T.wait_for_timeout(200)
        s1=await E("()=>HyBoss.stock('k1')")
        await E("()=>HyBoss.pickWeek(3)"); await T.wait_for_timeout(400)
        s2=await E("()=>[HyBoss.B.n, HyBoss.B.test, HyBoss.stock('k1')]")
        ok(s1=={"r":2,"s":3} and s2[2]==s1 and not s2[1], f"테스트 중 보스 바꾸기 → 기회 그대로 {s1} → {s2}")
        # 2. 같은 주에 끄고 켜기 → 보스·기회 그대로 (다시 시작 안 함)
        id0=await E("()=>HyBoss.B.id")
        await E("()=>HyBoss.setup({on:false, team:false, split:'eq'})"); await T.wait_for_timeout(200)
        same=await E("()=>HyBoss.sameWeekOn()")
        await E("()=>HyBoss.setup({on:true, team:false, split:'eq', restart:!HyBoss.sameWeekOn()})"); await T.wait_for_timeout(300)
        s3=await E("()=>[HyBoss.B.id, HyBoss.stock('k1')]")
        ok(same and s3==[id0, s1], f"같은 주 끄고 켜기 = 그대로 {same} {s3}")
        # 3. 쓰러뜨리고 보상 안 받은 채 ↺ 다시 → 기회는 새 보스로, 옛 보상은 남음
        await E("()=>{ HyBoss.CAP=1e9; HyBoss.add(Kid.get(), HyBoss.state('all').hp, 'study', 3); HyBoss.CAP=400; }"); await T.wait_for_timeout(300)
        g0=await E("()=>HyBoss.reward(Kid.get())")
        await E("()=>HyBoss.setup({on:true, team:false, split:'eq', restart:true})"); await T.wait_for_timeout(400)
        r3=await E("()=>[HyBoss.B.id, HyBoss.stock('k1'), HyBoss.oldRewards(Kid.get()).map(x=>[x.B.id, x.g])]")
        ok(r3[0]!=id0 and r3[1]==s1 and r3[2]==[[id0, g0]] and g0>0, f"↺ 다시 → 기회 옮김 · 옛 보상 남음 {g0} {r3}")
        gm=await E("()=>{ const w0=Wallet.gems(); return HyBoss.claimSafe(Kid.get(), 'o:"+id0+"').then(g=>[g, Wallet.gems()-w0, HyBoss.oldRewards(Kid.get()).length]); }")
        ok(gm[0]==g0 and gm[1]==g0 and gm[2]==0, f"옛 보스 보상 받기 한 번 {gm}")
        # 4. 반 대항전 — 주 중간에 반을 옮겨도 데미지·보이는 체력·보상이 같은 반
        await E(ROSTER, {"t":{"a":{"n":"사자반","e":"🦁"},"b":{"n":"호랑이반","e":"🐯"}}, "k":{"k1":{"n":"민준","t":"a"},"k2":{"n":"서연","t":"b"},"k3":{"n":"지호","t":"b"}}}); await T.wait_for_timeout(400)
        await E("()=>{ Kid.set({id:'k1',n:'민준',t:'a'}); HyBoss.add(Kid.get(), 100, 'study'); }"); await T.wait_for_timeout(200)
        await E("()=>FB.update('/hy/roster/k/k1', {t:'b'})"); await T.wait_for_timeout(300)
        await E("()=>{ Kid.set({id:'k1',n:'민준',t:'b'}); HyBoss.add(Kid.get(), 50, 'study'); }"); await T.wait_for_timeout(200)
        await E("()=>{ HyBoss.CAP=1e9; HyBoss.add({id:'k2',n:'서연',t:'b'}, HyBoss.state('b').hp, 'study'); HyBoss.CAP=400; }"); await T.wait_for_timeout(300)
        r4=await E("()=>{ const me=Kid.get(); return [HyBoss.mine('k1').t, HyBoss.state('a').sum, WeekBoss.view(HyBoss.B, me).t, !!HyBoss.state('b').dead, HyBoss.reward(me)]; }")
        ok(r4==["a",150,"a",True,0], f"반 옮겨도 데미지·화면·보상 = 처음 반 {r4}")
        # 5. 두 태블릿 — 오래된 화면(8초 넘게 안 읽음)은 먼저 읽고 때림 · 쓰러짐 이름은 먼저 쓴 아이
        await E(ROSTER, {"t":{}, "k":{"k1":{"n":"민준"},"k2":{"n":"서연"}}}); await T.wait_for_timeout(400)
        A=await ctx.new_page(); A.on("pageerror", lambda e: errs.append("A "+str(e))); await boot(A)
        B=await ctx.new_page(); B.on("pageerror", lambda e: errs.append("B "+str(e))); await boot(B)
        for pg,k,n in ((A,'k1','민준'),(B,'k2','서연')):
            await pg.evaluate(f"()=>{{ Kid.set({{id:'{k}',n:'{n}',t:'all'}}); HyBoss.start(); return HyBoss.refresh(true).then(()=>{{ HyBoss.earn(Kid.get(),'study',10); HyBoss.earn(Kid.get(),'run',10); }}); }}")
        await A.wait_for_timeout(300)
        await E("()=>{ HyBoss.CAP=1e9; HyBoss.add({id:'k2',n:'서연'}, HyBoss.state('all').hp-30, 'study'); HyBoss.CAP=400; }"); await T.wait_for_timeout(300)
        for pg in (A,B): await pg.evaluate("()=>{ HyBoss.CAP=1e9; WeekBoss.open(); }")
        await A.wait_for_timeout(800)
        for i in range(6):
            await A.evaluate("()=>{ if(WeekBoss.F){ WeekBoss.F.next=99; WeekBoss.F.lock=0; } WeekBoss.swing(); }"); await A.wait_for_timeout(150)
        await A.wait_for_timeout(300)
        b0=await B.evaluate("()=>HyBoss.stock('k2')")
        await B.evaluate("()=>{ HyBoss._t=Date.now()-9000; }")   # B 화면은 9초 전에 읽음
        for i in range(4):
            await B.evaluate("()=>{ if(WeekBoss.F){ WeekBoss.F.next=99; WeekBoss.F.lock=0; } WeekBoss.swing(); }"); await B.wait_for_timeout(250)
        b1=await B.evaluate("()=>[HyBoss.stock('k2'), !!WeekBoss.view(HyBoss.B, Kid.me()).dead]")
        ok(b1[0]==b0 and b1[1], f"오래된 화면은 먼저 읽음 — 쓰러진 보스에 기회 안 날림 {b0} → {b1}")
        await B.evaluate("()=>{ HyBoss.C.dead={}; HyBoss.B.dead={}; HyBoss.markDead(HyBoss.B, 'all', '서연'); }"); await T.wait_for_timeout(300)   # B 가 아직 모르는 채 쓰러짐을 쓰려 해도
        by=await T.evaluate("()=>FB.get('/hy/boss/dead/'+HyBoss.B.id+'/all').then(v=>v && v.by)")
        ok(by=="민준", f"쓰러짐 이름은 한 번만 (덮지 않음) {by}")
        # 6. 같은 아이 두 기기 — 기회는 더하기 카운터라 서로 덮지 않음
        for pg in (A,B): await pg.evaluate("()=>WeekBoss.close()")
        await E("()=>HyBoss.setup({on:true, team:false, split:'eq', restart:true})"); await T.wait_for_timeout(300)
        for pg in (A,B): await pg.evaluate("()=>{ Kid.set({id:'k3',n:'지호',t:'all'}); return HyBoss.refresh(true); }")
        await A.evaluate("()=>HyBoss.earn(Kid.get(),'study',5)"); await A.wait_for_timeout(200)
        await B.evaluate("()=>{ HyBoss._t=0; return HyBoss.refresh(true); }"); await B.evaluate("()=>{ WeekBoss.open(); }"); await B.wait_for_timeout(500)
        await A.evaluate("()=>HyBoss.earn(Kid.get(),'run',4)"); await A.wait_for_timeout(200)
        await B.evaluate("()=>{ if(WeekBoss.F){ WeekBoss.F.next=99; WeekBoss.F.lock=0; } WeekBoss.swing(); }"); await B.wait_for_timeout(300)
        sv=await E(SRV, "k3")
        ok(sv=={"r":4,"s":4}, f"같은 아이 두 기기 — 기회 안 덮임 {sv}")
        await B.evaluate("()=>WeekBoss.close()")
        # 7. 1단어 맞히고 그만두기 → 내림, 남은 맞힘은 다음 판에 (4번째 판에 +1) · 짧은 판은 '달리기 한 판' 미션에 안 셈
        await A.evaluate("()=>{ Kid.set({id:'k2',n:'서연',t:'all'}); localStorage.removeItem('hyeng_rrem_k2'); for(let i=0;i<20;i++) HyBoss.use(Kid.get()); window._dmRun=0; const a=DM.add.bind(DM); DM.add=(k,n)=>{ if(k==='run') window._dmRun++; return a(k,n); }; }")
        st0=await A.evaluate("()=>HyBoss.stock('k2').r")
        got=[]
        for i in range(4):
            await A.evaluate(QUIT, {"right":1}); await A.wait_for_timeout(700)
            got.append(await A.evaluate("()=>HyBoss.stock('k2').r")-st0)
            await A.evaluate("()=>show('scStart')")
        dm=await A.evaluate("()=>window._dmRun")
        ok(got==[0,0,0,1] and dm==0, f"1단어 그만두기 = 내림 + 다음 판에 이어서 {got} · 달리기 미션 {dm}")
        # 8. 일요일 밤 12시가 지나면 열린 화면도 새 주 보스 (지난주 보스에 데미지 안 들어감)
        await B.evaluate("""()=>{ const n0=Date.now, mon=HyBoss.kd(HyBoss.monday())-12*3600e3, end=mon+7*864e5, t0=n0(); Date.now=()=>end-2000+(n0()-t0); Kid.set({id:'k3',n:'지호',t:'all'}); HyBoss.calc(); WeekBoss.open(); }""")
        await B.wait_for_timeout(2600)
        w8=await B.evaluate("()=>{ const old=HyBoss.B.id; HyBoss.CAP=1e9; const a=HyBoss.add(Kid.get(), 10, 'study'); return [old, HyBoss.B.id, HyBoss.B.wk===HyBoss.monday(), a, HyBoss.P && HyBoss.P.id]; }")
        ok(w8[1]!=w8[0] and w8[2] and w8[4]==w8[0], f"월요일 0시 → 새 주 보스로 {w8}")
        await B.evaluate("()=>WeekBoss.close()")
        # 9. ⚠️ 경고 중에 ◀ 닫기 → (v390) 주간 보스는 패턴 연습용이라 손해 없음 (예전엔 기회 -1) · 패턴 버튼도 사라짐
        await A.evaluate("()=>{ Kid.set({id:'k1',n:'민준',t:'all'}); HyBoss.earn(Kid.get(),'study',5); WeekBoss.open(); }"); await A.wait_for_timeout(600)
        await A.evaluate("()=>{ WeekBoss.swing(); }"); await A.wait_for_timeout(500)
        await A.evaluate("()=>liveAtk()"); await A.wait_for_timeout(300)
        w9=await A.evaluate("()=>{ const at=!!(BossLive.S && BossLive.S.A), k=HyBoss.stock('k1'); WeekBoss.close(); const k2=HyBoss.stock('k1'); return [at, k.r+k.s, k2.r+k2.s, BossLive.on(), !!document.getElementById('bpCtl')]; }")
        ok(w9[0] and w9[2]==w9[1] and not w9[3] and not w9[4], f"(v392) 보스 공격 중 닫기 = 연습이라 손해 없음 · 싸움 정리 {w9}")
        ok(await A.evaluate("()=>[BossLive.lead(BossPat.win('kinder')), BossLive.lead(BossPat.win('g34')), BossLive.lead(BossPat.win('mid'))]")==[1350,1100,900], "(v392) 보스 공격 준비 시간 (유치원 1.35초 · 보통 1.1초 · 중등 0.9초)")
        # 10. 'D-2' 대신 남은 시간 · 토요일 = 1일
        dl=await A.evaluate("()=>{ const n0=Date.now, mon=HyBoss.kd(HyBoss.monday())-12*3600e3; Date.now=()=>mon+5*864e5+12*3600e3; const r=[HyBoss.daysLeft(), HyBoss.leftTxt(HyBoss.B||HyBoss.B0)]; Date.now=n0; return r; }")
        ok(dl[0]==1 and dl[1].startswith("1일 12"), f"토요일 낮 = 1일 남음 {dl}")
        # 11. 공용 패드 — 이름 고른 지 3분 넘었으면 달리기 시작 때 「민준 맞아요?」 한 번
        await A.evaluate("()=>{ show('scStart'); Kid.set({id:'k1',n:'민준',t:'all',pk:Date.now()-4*60000}); document.getElementById('btnGo').click(); }"); await A.wait_for_timeout(300)
        ka=await A.evaluate("()=>[!!document.getElementById('kidAsk'), (document.getElementById('kidAsk')||{}).innerText||'', document.getElementById('scSetup').classList.contains('on')]")
        await A.evaluate("()=>{ const b=document.querySelector('#kidAsk [data-ka=y]'); b && b.click(); }"); await A.wait_for_timeout(300)
        ka2=await A.evaluate("()=>{ const a=document.getElementById('scSetup').classList.contains('on'); show('scStart'); document.getElementById('btnGo').click(); return [a, !!document.getElementById('kidAsk')]; }")
        ok(ka[0] and "민준 맞아요" in ka[1] and not ka[2] and ka2==[True, False], f"공용 패드 이름 확인 한 번 {ka} {ka2}")
        # 12. 이름을 안 고른 아이 — 달리기 결과 보스 칸에 [이름 고르기]
        await A.evaluate("()=>{ Kid.clear(); show('scStart'); }")
        await A.evaluate(QUIT, {"right":8}); await A.wait_for_timeout(700)
        nm=await A.evaluate("()=>{ const o=document.querySelector('#oBoss .rwT'); return o ? [o.innerText.replace(/\\n/g,' '), !!o.querySelector('[data-kidpick]')] : null; }")
        ok(nm and "이름을 고르면" in nm[0] and nm[1], f"이름 안 고른 아이 타일 {nm}")
        print("errs", real_errs(errs)[:5]); await br.close()
    if real_errs(errs): bad.append("errs")
    print("결과:", "통과 ✅" if not bad else "실패 ❌"); [print(" BAD", b) for b in bad]
    if bad: sys.exit(1)
asyncio.run(main())
