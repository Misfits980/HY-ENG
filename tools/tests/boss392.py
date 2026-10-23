"""(v392) ⚔️ 실시간 보스전 — 사용자: 막기·이동 버튼이 늘 한 화면에 있어야 · 공격이 올 때 막기가 켜지는 건 넌센스 · 주간 보스가 시뮬레이션 같음
  · 버튼 4개(◀ ⚔️ 🛡 ▶)는 처음부터 끝까지 그대로 · 보스는 아무 때나 공격 · 내 자리 3칸
  · 내려찍기 = 내 칸 그림자 → 옆으로 피하거나 맞는 순간 🛡 · 휩쓸기 = 가운데·앞 (직전에만 번쩍) → 뒤로 · 연속 발사 = 쏘는 순간 내 칸 → 움직이면 피함
  · 🛡 = 누르는 순간 (맞는 순간과 차이로 완벽/막기) · 연타 막기(잠깐 다시 못 누름) · ⚔️ 휘두르는 동안은 못 움직임
  · 주간 보스 = 연습 (맞아도 손해 없음) · 수업 레이드 = 문제로 공격 + 아래 ◀ 🛡 ▶ · 하트 3"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

LAUNCH = """(x)=>{ const S=BossLive.S; S.A=null; S.sh=-1e9; S.cd=0; document.querySelectorAll('.blMark,.blBand,.bpBall').forEach(e=>e.remove()); const r=Math.random; Math.random=()=>x; BossLive.launch(performance.now()); Math.random=r; const A=S.A; return A ? {kind:A.kind, n:A.hits.length, t0:A.t0, t:A.hits.map(h=>h.t), z:A.hits.map(h=>h.z), rv:A.hits[0].rv||0, mark:!!document.querySelector('.blMark')} : null; }"""

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={"width": 390, "height": 844}, service_workers="block")
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)
        r = await pg.evaluate("()=>[BossPat.win('kinder').g, BossPat.win('g34').p, BossPat.win('mid').g, BossLive.lead(BossPat.win('kinder')), BossLive.lead(BossPat.win('g56')), BossLive.lead(BossPat.win('mv1'))]")
        ok(r == [420, 150, 280, 1350, 1100, 900], f"학년별 판정·준비 시간 {r}")
        await pg.evaluate("""()=>{ HyBoss.live(); return FB.set('/hy/roster', {t:{}, k:{k1:{n:'민준'}}}).then(()=>HyBoss.setup({on:true, team:false, split:'eq', restart:true})); }"""); await pg.wait_for_timeout(400)
        await pg.evaluate("()=>{ Kid.set({id:'k1',n:'민준',t:'all'}); HyBoss.earn(Kid.get(),'study',8); WeekBoss.open(); }"); await pg.wait_for_timeout(900)
        r = await pg.evaluate("()=>[!!document.querySelector('[data-wbf=fight]'), !!document.querySelector('[data-wbf=block]'), BossLive.on()]")
        ok(r == [True, False, False], f"주간 보스: 「⚔️ 싸우기!」 하나 (막기 버튼은 싸움 안에서만) {r}")
        await pg.evaluate("()=>document.querySelector('[data-wbf=fight]').click()"); await pg.wait_for_timeout(400)
        r = await pg.evaluate("()=>[BossLive.on(), [...document.querySelectorAll('#bpCtl [data-bp]')].map(b=>b.dataset.bp).join(','), getComputedStyle(document.getElementById('wbFight')).display, BossLive.S.pos, !!BossLive.S.A]")
        ok(r == [True, "end,L,R,shield,atk", "none", 1, False], f"싸우기 → 아래 버튼 4개 + 그만 · 가운데 칸에서 시작 · 바로 공격하지 않음 {r}")
        # 이동
        r = await pg.evaluate("()=>{ BossLive.press('L'); BossLive.press('L'); const a=[BossLive.S.pos, RaidStage.me.el.style.marginLeft]; BossLive.press('R'); BossLive.press('R'); BossLive.press('R'); return a.concat([BossLive.S.pos, RaidStage.me.el.style.marginLeft, BossLive.STEP]); }")
        ok(r[:4] == [0, f"-{r[4]}px", 2, f"{r[4]}px"] and r[4] >= 70, f"◀ ▶ 로 3칸 이동 (끝에서 멈춤 · 싸움 화면 칸 넓이 {r[4]}) {r}")
        r = await pg.evaluate("()=>[!!document.getElementById('wba'), document.getElementById('wba') && document.getElementById('wbaStage').contains(RaidStage.me.el)]")
        ok(r == [True, True], f"(v392) 싸우기 = 꽉 찬 싸움 화면 (대기실과 따로) {r}")
        # 공격 — 맨 뒤면 한 칸 앞으로 · 휘두르는 동안 못 움직임
        r = await pg.evaluate("()=>{ BossLive.press('L'); BossLive.press('L'); const s0=HyBoss.stock('k1'), d0=HyBoss.mine('k1').d|0; BossLive.S.busy=0; BossLive.press('atk'); const p1=BossLive.S.pos; BossLive.press('R'); const s1=HyBoss.stock('k1'); return [p1, BossLive.S.pos, (s0.r+s0.s)-(s1.r+s1.s), (HyBoss.mine('k1').d|0)-d0>=8]; }")
        ok(r == [1, 1, 1, True], f"⚔️ 공격 = 기회 1 · 맨 뒤면 한 칸 앞으로 · 휘두르는 동안 못 움직임 {r}")
        await pg.wait_for_timeout(500)
        # 내려찍기 — 내 칸 그림자 · 옆으로 피함
        a = await pg.evaluate(LAUNCH, 0.01)
        ok(a and a["kind"] == "slam" and a["z"] == [[1]] and a["mark"] and round(a["t"][0] - a["t0"]) == 1100, f"내려찍기: 지금 내 칸에 그림자 · 1.1초 뒤 {a}")
        r = await pg.evaluate("([t])=>{ BossLive.press('R'); BossLive.tick(t+1); return [document.getElementById('bpRes').innerText, WeekBoss.F.combo, WeekBoss.F.hit]; }", [a["t"][0]])
        ok("피했다" in r[0] and r[1] == 1 and r[2] == 0, f"옆 칸으로 피함 = 💨 · 콤보 {r}")
        # 내려찍기 — 그 자리에서 맞는 순간 🛡 = 완벽 (반격 30)
        a = await pg.evaluate(LAUNCH, 0.01)
        r = await pg.evaluate("([t])=>{ const d0=HyBoss.mine('k1').d|0; BossLive.S.cd=0; BossLive.press('shield', t-60); BossLive.tick(t+1); return [document.getElementById('bpRes').innerText, (HyBoss.mine('k1').d|0)-d0]; }", [a["t"][0]])
        ok("완벽" in r[0] and r[1] == 30, f"맞는 순간 🛡 = ✨ 완벽 반격 30 {r}")
        # 너무 일찍 🛡 → 맞음 (연습: 손해 없음) · 연타 막기
        a = await pg.evaluate(LAUNCH, 0.01)
        r = await pg.evaluate("([t])=>{ const s0=HyBoss.stock('k1'); BossLive.S.cd=0; BossLive.press('shield', t-700); const sh1=BossLive.S.sh; BossLive.press('shield', t-650); const sh2=BossLive.S.sh; BossLive.tick(t+1); const s1=HyBoss.stock('k1'); return [sh1===sh2, document.getElementById('bpRes').innerText, WeekBoss.F.combo, (s0.r+s0.s)-(s1.r+s1.s)]; }", [a["t"][0]])
        ok(r[0] and "앗" in r[1] and "❤" not in r[1] and r[2] == 0 and r[3] == 0, f"너무 일찍 🛡 = 맞음 · 바로 또 눌러도 안 됨(연타 막기) · 연습이라 손해 없음 {r}")
        # 휩쓸기 — 가운데·앞 · 직전에만 번쩍 · 뒤로 피함
        await pg.evaluate("()=>{ BossLive.S.pos=1; BossLive.place(BossLive.S); }")
        a = await pg.evaluate(LAUNCH, 0.34)
        ok(a and a["kind"] == "sweep" and a["z"] == [[1, 2]] and not a["mark"], f"휩쓸기: 가운데·앞 칸 · 그림자 없음 {a}")
        r = await pg.evaluate("([rv, t])=>{ BossLive.tick(rv-50); const b0=!!document.querySelector('.blBand'); BossLive.tick(rv+20); const b1=!!document.querySelector('.blBand'); BossLive.press('L'); BossLive.tick(t+1); return [b0, b1, document.getElementById('bpRes').innerText, BossLive.S.pos]; }", [a["rv"], a["t"][0]])
        ok(r[0] is False and r[1] is True and "피했다" in r[2] and r[3] == 0, f"빨간 띠는 맞기 직전에만 · 뒤 칸으로 피함 {r}")
        # 연속 발사 — 쏘는 순간 내 칸 · 움직이면 피함 · 공 3개
        a = await pg.evaluate(LAUNCH, 0.67)
        r = await pg.evaluate("([t])=>{ const S=BossLive.S; BossLive.tick(t[0]-700); const aim=S.A.hits[0].aim, ball=!!document.querySelector('.bpBall'); BossLive.press('R'); BossLive.tick(t[0]+1); const r1=document.getElementById('bpRes').innerText; S.cd=0; BossLive.tick(t[1]-700); BossLive.press('shield', t[1]-30); BossLive.tick(t[1]+1); const r2=document.getElementById('bpRes').innerText; BossLive.tick(t[2]+1); const r3=document.getElementById('bpRes').innerText; return [aim, ball, r1, r2, r3, S.A===null]; }", [a["t"]])
        ok(a["kind"] == "burst" and a["n"] == 3 and r[1] and "피했다" in r[2] and "완벽" in r[3] and "앗" in r[4] and r[5], f"연속 발사: 공 3개 · 쏜 뒤 움직이면 피함 · 공마다 🛡 · 끝나면 다음 공격 기다림 {r}")
        # 그만 → 결과창 · 싸움 정리
        await pg.evaluate("()=>document.querySelector('#bpCtl [data-bp=end]').dispatchEvent(new PointerEvent('pointerdown', {bubbles:true}))"); await pg.wait_for_timeout(500)
        r = await pg.evaluate("()=>[BossLive.on(), !!document.getElementById('bpCtl'), !!document.getElementById('wbRes')]")
        ok(r == [False, False, True], f"「그만」 → 결과창 · 버튼 사라짐 {r}")
        # 키보드
        await pg.evaluate("()=>{ const r=document.getElementById('wbRes'); if(r) r.remove(); WeekBoss.fight(1); }"); await pg.wait_for_timeout(300)
        r = await pg.evaluate("()=>{ const S=BossLive.S; S.cd=0; const k=(key)=>document.dispatchEvent(new KeyboardEvent('keydown', {key, bubbles:true})); k('ArrowLeft'); const p=S.pos; k(' '); return [p, S.sh>0]; }")
        ok(r == [0, True], f"키보드 ← · Space {r}")
        await pg.evaluate("()=>WeekBoss.close()")
        # ── 수업 레이드
        ctx2 = await br.new_context(viewport={"width": 1024, "height": 768}, service_workers="block"); await ctx2.add_init_script("window.HY_FB_LOCAL=true;")
        T = await ctx2.new_page(); T.on("pageerror", lambda e: errs.append("T " + str(e))); await boot(T)
        room = await T.evaluate("()=>{ Raid.host('g34', [], 0, null, 900, 'all'); return Raid.room; }"); await T.wait_for_timeout(600)
        K = await ctx2.new_page(); K.on("pageerror", lambda e: errs.append("K " + str(e))); await K.set_viewport_size({"width": 390, "height": 844}); await boot(K)
        await K.evaluate(f"()=>Raid.join('{room}', '민준')"); await K.wait_for_timeout(600)
        r = await K.evaluate("()=>BossLive.on()")
        ok(r is False, f"레이드: 시작 전엔 싸움 버튼 없음 {r}")
        await T.evaluate("()=>Raid.hostAct('start')"); await K.wait_for_timeout(1200)
        r = await K.evaluate("()=>[BossLive.on(), [...document.querySelectorAll('#bpCtl [data-bp]')].map(b=>b.dataset.bp).join(','), !!(Raid.q && !Raid.q.done)]")
        ok(r == [True, "L,R,shield,atk", True], f"레이드: 시작하면 아레나 ◀ 🛡 ▶ ⚔️ (⚡ 에너지) · 문제(주문)도 그대로 {r}")
        d0 = await K.evaluate("()=>[Raid.dmg, Raid.blk, Raid.hearts]")
        a = await K.evaluate(LAUNCH, 0.01)
        await K.evaluate("([t])=>{ BossLive.S.cd=0; BossLive.press('shield', t-40); BossLive.tick(t+1); }", [a["t"][0]])
        d1 = await K.evaluate("()=>[Raid.dmg, Raid.blk, Raid.hearts, !!(Raid.q && !Raid.q.done)]")
        ok(d1[0] - d0[0] == 25 and d1[1] - d0[1] == 1 and d1[2] == d0[2] and d1[3], f"레이드: 완벽 막기 = 반격 25 · 문제는 그대로 {d0} {d1}")
        a = await K.evaluate(LAUNCH, 0.01)
        await K.evaluate("([t])=>{ BossLive.tick(t+1); }", [a["t"][0]])
        d2 = await K.evaluate("()=>[Raid.hearts, document.getElementById('bpRes').innerText]")
        ok(d2[0] == d1[2] - 1 and "❤" in d2[1], f"레이드: 맞으면 하트 -1 {d2}")
        await K.evaluate("()=>{ Raid.hearts=1; }")
        a = await K.evaluate(LAUNCH, 0.01)
        await K.evaluate("([t])=>{ BossLive.tick(t+1); }", [a["t"][0]]); await K.wait_for_timeout(300)
        r = await K.evaluate("()=>[Raid.hearts, Raid.restTo>Raid.now(), BossLive.S && BossLive.S.hold, BossLive.on()]")
        ok(r == [3, True, True, True], f"하트 0 → 10초 쉬기 (그동안 보스 공격 멈춤 · 버튼은 그대로) {r}")
        await br.close()
    e = real_errs(errs)
    ok(not e, f"스크립트 오류 없음 {e[:3]}")
    print("\nALL OK" if not bad else "\nFAIL", bad)
    sys.exit(1 if bad else 0)
asyncio.run(main())
