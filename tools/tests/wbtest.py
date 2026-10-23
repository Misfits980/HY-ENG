"""(v310) 🏠 주간 보스 화면 + 🎯 오늘의 미션
   첫 화면 알림 → 보스 화면(언제·어떻게·보상 안내 · 내가 깎은 만큼 때리는 장면) · TV(선생님) 실시간 · 달리기 결과에서 미션 칸이 오름 · 상자 한 번만 · 다음 날 새 미션 + 연속"""
import asyncio, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright
END = """()=>{ Online.on=()=>false; G.set='basic'; G.lesson=0; G.rule='normal'; G.diff='normal'; G.testRun=false; G.practice=false; G.cleared=false; G.quit=true;
  G.score=900; G.stage=10; G.zone=1; G.right=20; G.wrong=1; G.bestCombo=12; G.running=false; G.skipOutro=true; G.overFade=false; G._overDone=false; gameOver(); G.skipOutro=false; }"""
async def main():
    bad=[]; errs=[]
    async with async_playwright() as p:
        br=await p.chromium.launch(); ctx=await br.new_context(viewport={"width":390,"height":844})
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)
        ban0=await pg.evaluate("()=>document.getElementById('hbBan').hidden"); print("banner before", ban0)
        if not ban0: bad.append("보스가 없는데 알림이 보임")
        await pg.evaluate("""()=>{ HyBoss.live(); return FB.set('/hy/roster', {t:{}, k:{k1:{n:'민준'},k2:{n:'서연'}}}).then(()=>HyBoss.setup({on:true, team:false, split:'eq', restart:true})); }"""); await pg.wait_for_timeout(400)
        await pg.evaluate("()=>{ localStorage.setItem('hyeng_nick','한양패드'); Kid.set({id:'k2',n:'서연',t:'all'}); G.char='mage'; HyBoss.add(Kid.get(), 60, 'study'); Kid.set({id:'k1',n:'민준',t:'all'}); G.char='knight'; show('scStart'); }"); await pg.wait_for_timeout(300)
        b=await pg.evaluate("()=>{ const e=document.getElementById('hbBan'); return [e.hidden, e.getAttribute('aria-label')]; }"); print("banner", b)
        if b[0] or "초원 수호자" not in b[1] or "시간" not in b[1] and "일" not in b[1]: bad.append(f"첫 화면 알림 {b}")
        # (v312) 달리기 한 판 → ⚔️ 공격 기회 +5 (20단어 ÷ 4) + 미션 · 쌓였을 때 작은 장면
        await pg.evaluate(END); await pg.wait_for_timeout(600)
        ov=await pg.evaluate("()=>{ const o=document.querySelector('.ovBoss'); return o?o.innerText:''; }"); print("over", ov)
        if "+5" not in ov or "공격하러" not in ov: bad.append(f"달리기 결과 공격 기회 {ov}")
        dm=await pg.evaluate("()=>DM.list().map(m=>[m.k, m.n, m.goal, m.done])"); print("missions", dm)
        runm=[m for m in dm if m[0] in ("run","rw","combo")]
        if not runm or not runm[0][3]: bad.append(f"달리기 미션 {dm}")
        # (v322) 결과 화면에서는 큰 창(#wbPop) 대신 보스 타일만 반짝 + 👤 누구 이름으로 쌓였는지
        await pg.wait_for_timeout(1500); await pg.screenshot(path=OUT+"wb_gain.png")
        fl=await pg.evaluate("()=>[!!document.getElementById('wbPop'), !!document.querySelector('#oBoss .rwT.rwFlash'), (document.querySelector('#oBoss .rwWho')||{}).textContent||'', Math.round(document.querySelector('#oBoss .rwGo').getBoundingClientRect().height)]"); print("flash", fl)
        if fl[0] or not fl[1] or "민준" not in fl[2]: bad.append(f"결과 타일 반짝·이름 (큰 창 없이) {fl}")
        if fl[3]<40: bad.append(f"공격하러 버튼 40px {fl[3]}")
        await pg.evaluate("()=>document.querySelector('#oBoss .rwGo').click()"); await pg.wait_for_timeout(600)
        v=await pg.evaluate("()=>{ const d=document.getElementById('wbView'); return d ? d.innerText : ''; }")
        for need in ["월요일 0시", "일요일 밤 12시", "3문제 맞히면 ⚔️1", "4단어 맞히면 ⚔️1", "막기", "도망", "이번 주 순위", "서연", "5/10"]:
            if need not in v: bad.append(f"보스 화면에 '{need}' 없음")
        await pg.evaluate("()=>HyBoss.earn(Kid.get(),'study',3)")
        # 휘두르기 — 기회 1개 = 8~12 (치명타 ×2)
        h0=await pg.evaluate("()=>HyBoss.mine('k1').d|0")
        await pg.evaluate("()=>{ WeekBoss.swing(); }"); await pg.wait_for_timeout(500)
        sw=await pg.evaluate("()=>[HyBoss.mine('k1').d|0, JSON.stringify(HyBoss.stock('k1')), WeekBoss.F.sw]"); print("swing", h0, sw)
        if not (8<=sw[0]-h0<=24) or sw[1]!='{"r":4,"s":3}' or sw[2]!=1: bad.append(f"한 번 휘두르기 {h0} {sw}")
        # (v392) 실시간 보스전 — 버튼 4개(◀ ⚔️ 🛡 ▶)는 늘 그대로 · 보스 공격 → 맞는 순간 🛡 = 완벽 (반격 30 · 기회 그대로)
        g=await pg.evaluate("()=>[BossLive.on(), [...document.querySelectorAll('#bpCtl [data-bp]')].map(b=>b.dataset.bp).join(',')]")
        if g!=[True, "end,L,R,shield,atk"]: bad.append(f"싸움 중 버튼 4개 + 그만 {g}")
        await pg.evaluate("()=>liveAtk()")
        g2=await pg.evaluate("()=>[...document.querySelectorAll('#bpCtl [data-bp]')].map(b=>b.dataset.bp).join(',')")
        if g2!=g[1]: bad.append(f"공격이 와도 버튼은 그대로 {g2}")
        st1=await pg.evaluate("()=>[HyBoss.mine('k1').d|0, JSON.stringify(HyBoss.stock('k1'))]")
        k=await pg.evaluate("()=>patSolve(true)"); await pg.wait_for_timeout(300)
        st2=await pg.evaluate("()=>[HyBoss.mine('k1').d|0, JSON.stringify(HyBoss.stock('k1')), WeekBoss.F.blk, WeekBoss.F.combo]"); print("block", k, st1, st2)
        n=3 if k=="burst" else 1
        if st2[0]-st1[0]!=30*n or st2[1]!=st1[1] or st2[2]!=n or st2[3]!=n: bad.append(f"완벽 막기 반격 {k} {st1} {st2}")
        # 주간 보스 = 연습 — 못 막아도 기회 그대로 · 콤보 0
        await pg.evaluate("()=>liveAtk()"); st3=await pg.evaluate("()=>{ const k=HyBoss.stock('k1'); return k.r+k.s; }")
        k=await pg.evaluate("()=>patSolve(false)"); await pg.wait_for_timeout(300)
        st4=await pg.evaluate("()=>{ const k=HyBoss.stock('k1'); return [k.r+k.s, WeekBoss.F.combo, WeekBoss.F.hit>0]; }"); print("miss", k, st3, st4)
        if st4!=[st3, 0, True]: bad.append(f"(연습) 못 막아도 기회 그대로 · 콤보 0 {k} {st3} {st4}")
        # 다 쓰면 결과창
        for i in range(12):
            if await pg.evaluate("()=>!!document.getElementById('wbRes')"): break
            await pg.evaluate("()=>{ if(WeekBoss.F){ WeekBoss.F.next=99; WeekBoss.F.lock=0; } WeekBoss.swing(); }"); await pg.wait_for_timeout(250)
        await pg.wait_for_selector("#wbRes", timeout=4000); await pg.wait_for_timeout(1200); await pg.screenshot(path=OUT+"wb_result.png")
        rs=await pg.evaluate("()=>document.getElementById('wbRes').innerText"); print("result", rs.replace("\n"," / "))
        if "공격 끝" not in rs or "막음" not in rs or "→" not in rs: bad.append(f"결과창 {rs}")
        if await pg.evaluate("()=>{ const k=HyBoss.stock('k1'); return k.r+k.s; }")!=0: bad.append("결과창인데 기회 남음")
        await pg.evaluate("()=>WeekBoss.close()")
        # (v311) 선생님이 이번 주 보스 고르기 — 데미지는 이어지고 체력은 새 보스로, 다음 주는 그다음
        pk=await pg.evaluate("()=>{ const s0=HyBoss.state('all').sum; return HyBoss.pickWeek(2).then(ok=>[ok, HyBoss.B.i, HyBoss.B.n, HyBoss.state('all').sum===s0, HyBoss.B.max.all, HyBoss.C.wp[HyBoss.B.wk]]); }"); print("pick", pk)
        if pk[:5]!=[True,2,"빙관 설원수",True,7000]: bad.append(f"이번 주 보스 고르기 {pk}")
        nw=await pg.evaluate("()=>{ const n0=Date.now; Date.now=()=>n0()+7*864e5; HyBoss.calc(); const r=[HyBoss.B.i, HyBoss.B.n, HyBoss.P.n]; Date.now=n0; HyBoss.calc(); return r; }"); print("next week", nw)
        if nw!=[3,"잿불 화룡","빙관 설원수"]: bad.append(f"다음 주 {nw}")
        # 미션 다 하고 상자 — 한 번만
        await pg.evaluate("()=>{ DM.add('les',3); DM.add('q',40); DM.add('swing',20); DM.add('run',1); DM.add('rw',20); DM.add('combo',12); }")
        r=await pg.evaluate("()=>{ const g0=Wallet.gems(), a=DM.ready(), g=DM.open(), g2=DM.open(); return [a, g, g2, Wallet.gems()-g0, DM.s.st]; }"); print("chest", r)
        if not r[0] or r[1] not in (5,10) or r[2]!=0 or r[3]!=r[1] or r[4]!=1: bad.append(f"상자 {r}")
        # 다음 날 → 새 미션 · 연속 1 → 보너스 +1
        r2=await pg.evaluate("()=>{ const n0=Date.now; Date.now=()=>n0()+864e5; Kid.set({id:'k1',n:'민준',t:'all'}); DM.s=null; const L=DM.list(); const out=[DM.s.day, DM.s.got, DM.s.st, DM.reward(), L.filter(m=>m.done).length, new Set(L.map(m=>m.k)).size]; Date.now=n0; DM.s=null; return out; }"); print("next day", r2)
        if r2[1]!=0 or r2[2]!=1 or r2[3]!=6 or r2[4]!=0 or r2[5]!=3: bad.append(f"다음 날 {r2}")
        # TV
        await pg.set_viewport_size({"width":1280,"height":800}); await pg.evaluate("()=>WeekBoss.open(true)"); await pg.wait_for_timeout(500)
        await pg.evaluate("()=>{ Kid.set({id:'k2',n:'서연',t:'all'}); HyBoss.add(Kid.get(), 30, 'study'); }"); await pg.wait_for_timeout(500)
        tk=await pg.evaluate("()=>(document.getElementById('wbTick')||{}).innerText||''"); print("tv tick", tk)
        if "서연" not in tk or "+30" not in tk: bad.append(f"TV 실시간 {tk}")
        await pg.screenshot(path=OUT+"wb_tv2.png")
        print("errs", errs[:5]); await br.close()
    print("결과:", "통과 ✅" if not bad and not errs else "실패 ❌"); [print(" BAD", b) for b in bad]
    if bad or errs: sys.exit(1)
asyncio.run(main())
