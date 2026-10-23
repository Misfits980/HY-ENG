"""(v392) 주간 보스 = 🏠 대기실 / ⚔️ 싸움 화면 나눔 — 싸우기 → 꽉 찬 싸움 화면 · 💥 필살 게이지(막기·피하기) 다 차면 다음 ⚔️ ×3 · 그만 → 결과(싸움 화면 위) → 닫기 = 대기실로 (무대도 대기실로)"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright
async def main():
    bad=[]; errs=[]
    def ok(c, m):
        print(("OK  " if c else "FAIL ")+m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(); ctx=await br.new_context(viewport={"width":390,"height":844}, service_workers="block"); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)
        await pg.evaluate("""()=>{ HyBoss.live(); return FB.set('/hy/roster', {t:{}, k:{k1:{n:'민준'}, k2:{n:'서연'}}}).then(()=>HyBoss.setup({on:true, team:false, split:'eq', restart:true})); }"""); await pg.wait_for_timeout(400)
        await pg.evaluate("()=>{ G.char='knight'; Kid.set({id:'k1',n:'민준',t:'all'}); HyBoss.earn(Kid.get(),'study',8); WeekBoss.open(); }"); await pg.wait_for_timeout(1000)
        await pg.screenshot(path=OUT+"wk392_lobby.png")
        r=await pg.evaluate("()=>[!!document.getElementById('wba'), !!document.querySelector('#wbView [data-wbf=fight]'), document.getElementById('wbStage').contains(RaidStage.me && RaidStage.me.el)]")
        ok(r==[False,True,True], f"대기실: 싸움 화면 없음 · 「싸우기」 · 무대 미리 보기 {r}")
        await pg.evaluate("()=>document.querySelector('[data-wbf=fight]').click()"); await pg.wait_for_timeout(700)
        await pg.evaluate("()=>{ BossLive.manual=true; }")
        r=await pg.evaluate("()=>[!!document.getElementById('wba'), document.getElementById('wbaStage').contains(RaidStage.me.el), BossLive.on(), document.getElementById('wbaMe').innerText]")
        ok(r[0] and r[1] and r[2] and "8" in r[3], f"싸우기 → 꽉 찬 싸움 화면 · 내 캐릭터 · 남은 기회 {r}")
        # 💥 필살 게이지 — 완벽 막기 3번
        for i in range(3):
            await pg.evaluate("()=>{ const S=BossLive.S; S.A=null; S.sh=-1e9; S.cd=0; const r=Math.random; Math.random=()=>0.01; BossLive.launch(performance.now()); Math.random=r; const A=S.A; A.hits.forEach(h=>{ S.cd=0; BossLive.press('shield', h.t-40); BossLive.tick(h.t+1); }); }")
            await pg.wait_for_timeout(200)
        r=await pg.evaluate("()=>[WeekBoss.F.sp, document.getElementById('wbaSp').classList.contains('full'), !!document.querySelector('#bpCtl .blB.at.spReady')]")
        ok(r[0]>=100 and r[1] and r[2], f"완벽 막기로 💥 필살 게이지 가득 · ⚔️ 반짝 {r}")
        await pg.screenshot(path=OUT+"wk392_full.png")
        d=await pg.evaluate("()=>{ const d0=HyBoss.mine('k1').d|0; BossLive.S.busy=0; BossLive.press('atk'); return [(HyBoss.mine('k1').d|0)-d0, WeekBoss.F.sp]; }")
        ok(d[0]>=3*8 and d[1]==0, f"필살 일격 = ×3 · 게이지 비움 {d}")
        await pg.wait_for_timeout(600)
        d=await pg.evaluate("()=>{ const d0=HyBoss.mine('k1').d|0; BossLive.S.busy=0; BossLive.press('atk'); return (HyBoss.mine('k1').d|0)-d0; }")
        ok(0<d<=2*12+10+5, f"그다음은 보통 공격 {d}")
        await pg.wait_for_timeout(600)
        await pg.evaluate("()=>document.querySelector('#wba [data-wbf=quit]').click()"); await pg.wait_for_timeout(700)
        r=await pg.evaluate("()=>[!!document.querySelector('#wba #wbRes'), BossLive.on()]"); ok(r==[True,False], f"◀ 그만 → 결과창 (싸움 화면 위) {r}")
        await pg.screenshot(path=OUT+"wk392_res.png")
        await pg.evaluate("()=>document.querySelector('#wbRes [data-wbf=rx]').click()"); await pg.wait_for_timeout(700)
        r=await pg.evaluate("()=>[!!document.getElementById('wba'), !!document.getElementById('wbView'), document.getElementById('wbStage').contains(RaidStage.me.el), document.body.classList.contains('arOn')]")
        ok(r==[False,True,True,False], f"닫기 → 대기실 · 무대도 대기실로 {r}")
        ok(not errs, f"스크립트 오류 없음 {errs[:3]}")
        await br.close()
    print("\nALL OK" if not bad else "\nFAIL", bad)
    if bad: sys.exit(1)
asyncio.run(main())
