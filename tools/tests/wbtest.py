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
        b=await pg.evaluate("()=>{ const e=document.getElementById('hbBan'); return [e.hidden, e.innerText]; }"); print("banner", b)
        if b[0] or "초원 수호자" not in b[1] or "남음" not in b[1]: bad.append(f"첫 화면 알림 {b}")
        # 달리기 한 판 → 보스 ⚔️40 + 미션
        await pg.evaluate(END); await pg.wait_for_timeout(600)
        ov=await pg.evaluate("()=>{ const o=document.querySelector('.ovBoss'); return o?o.innerText:''; }"); print("over", ov)
        if "보스 보기" not in ov: bad.append("달리기 결과 보스 보기 단추")
        dm=await pg.evaluate("()=>DM.list().map(m=>[m.k, m.n, m.goal, m.done])"); print("missions", dm)
        runm=[m for m in dm if m[0] in ("run","rw","combo")]
        if not runm or not runm[0][3]: bad.append(f"달리기 미션 {dm}")
        await pg.evaluate("()=>{ document.querySelector('.ovBossSee').click(); }"); await pg.wait_for_timeout(500)
        v=await pg.evaluate("()=>{ const d=document.getElementById('wbView'); return d ? d.innerText : ''; }")
        for need in ["월요일 0시", "일요일 밤 12시", "Daily 30", "⚔️3", "⚔️5", "⚔️2", "도망", "많이 깎은 친구", "보스 순서", "서연"]:
            if need not in v: bad.append(f"보스 화면에 '{need}' 없음")
        hold=await pg.evaluate("()=>WeekBoss._rp"); print("replay", hold)
        if hold!=40: bad.append(f"깎은 만큼 다시 보여 주기 {hold}")
        await pg.wait_for_timeout(1700); await pg.screenshot(path=OUT+"wb_replay.png"); await pg.wait_for_function("()=>WeekBoss._hold===0", timeout=15000)
        seen=await pg.evaluate("()=>[WeekBoss._hold, localStorage.getItem('hyeng_wbs_'+HyBoss.B.id+'_k1')]"); print("after", seen)
        if seen!=[0,"40"]: bad.append(f"다시 보기 끝 {seen}")
        await pg.evaluate("()=>{ WeekBoss.close(); WeekBoss._rp=0; WeekBoss.open(); }"); await pg.wait_for_timeout(300)
        if await pg.evaluate("()=>WeekBoss._rp|0")!=0: bad.append("본 데미지를 또 보여 줌")
        await pg.evaluate("()=>WeekBoss.close()")
        # 미션 다 하고 상자 — 한 번만
        await pg.evaluate("()=>{ DM.add('les',3); DM.add('q',40); DM.add('boss',50); DM.add('run',1); DM.add('rw',20); DM.add('combo',12); }")
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
