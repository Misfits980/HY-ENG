"""(v390) ⚔️ 보스 공격 패턴 — 사용자: 보스전이 그냥 두들겨 패는 느낌 · 체력 깎는 패턴도 타이밍 방어도 없음 → 주간 보스 · 수업 레이드 둘 다
  · 공격 3가지 = 내려찍기(🛡 타이밍) · 휩쓸기(◀ ▶ 피하기) · 연속 발사(🛡 3번 리듬) · 보스 20% 아래 필살기(완벽만 버팀)
  · 판정: 완벽 / 막기 / 너무 빨라요 / 못 막음 · 학년별 판정 시간 · 화면 아래 큰 버튼 · 원·빨간 쪽·공
  · 주간 보스: 내 하트 ❤️5 · 맞으면 하트 -1 · 0 이면 😵 기절 → 공격 기회 -1 · 막기 콤보만큼 공격 +
  · 수업 레이드: 문제 대신 패턴 · 하트 ❤️3 (0 이면 10초 쉬기) · 막으면 반격"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

RUN = """async ([j, fin, book, plan])=>{ let box=document.getElementById('tbox'); if(!box){ box=document.createElement('div'); box.id='tbox'; box.style.cssText='position:fixed;left:0;top:0;width:390px;height:300px'; document.body.appendChild(box); }
  RaidStage.ensure('wk', {box, boss:BOSS_LINE[0], me:'', key:'x'}); window._r=null;
  const A=BossPat.run({j, fin, k:'hb1-a', nm:'시험', book, done:r=>{ window._r=r; }});
  const ui={ctl:!!document.getElementById('bpCtl'), btn:document.querySelectorAll('#bpCtl [data-bp]').length, ring:!!document.querySelector('.rsHero.me .bpRing'), sw:!!document.querySelector('.rsHero.me .bpSw'), kind:A.kind, n:A.hits.length, W:A.W};
  plan.forEach(([k, off])=>{ if(k==='L'||k==='R'){ const side = off==='safe' ? (A.side==='L'?'R':'L') : A.side; BossPat.press(side, A.rv+150); BossPat.tick(A.hits[0]+A.W.g+1); } else { const i=A.done.findIndex(x=>!x); if(i>=0) BossPat.press('shield', A.hits[i]+off); } });
  if(BossPat.A===A) BossPat.tick(A.hits[A.hits.length-1]+A.W.g+1);
  for(let t=0;t<30 && !window._r;t++) await new Promise(r=>setTimeout(r,100));
  return Object.assign(ui, {res:window._r, done:A.done, left:!!document.getElementById('bpCtl') || !!document.querySelector('.bpRing')}); }"""

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={"width": 390, "height": 844})
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)
        r = await pg.evaluate("()=>[BossPat.win('kinder').g, BossPat.win('basic').p, BossPat.win('g34').g, BossPat.win('g56').p, BossPat.win('mid').g, BossPat.win('mv1').p]")
        ok(r == [420, 190, 340, 150, 280, 120], f"학년별 판정 시간 (어릴수록 넉넉) {r}")
        # 내려찍기
        r = await pg.evaluate(RUN, [0, False, "g34", [["s", 20]]])
        ok(r["kind"] == "slam" and r["ctl"] and r["btn"] == 1 and r["ring"] and r["res"] == {"kind": "slam", "perf": 1, "good": 0, "ok": 1, "hurt": 0} and not r["left"], f"내려찍기: 큰 🛡 버튼 · 원 · 맞는 순간 = 완벽 · 끝나면 사라짐 {r}")
        r = await pg.evaluate(RUN, [0, False, "g34", [["s", 260]]])
        ok(r["res"]["good"] == 1 and r["res"]["hurt"] == 0, f"조금 늦게 = 막기 {r['res']}")
        r = await pg.evaluate(RUN, [0, False, "g34", [["s", -600]]])
        ok(r["done"] == ["early"] and r["res"]["hurt"] == 1, f"너무 빨리 = 맞음 {r['done']} {r['res']}")
        r = await pg.evaluate(RUN, [0, False, "g34", []])
        ok(r["done"] == ["miss"] and r["res"]["hurt"] == 1, f"안 누름 = 맞음 {r['done']}")
        r = await pg.evaluate(RUN, [0, False, "kinder", [["s", 400]]])
        ok(r["res"]["good"] == 1, f"유치원은 0.4초 늦어도 막기 {r['res']}")
        r = await pg.evaluate(RUN, [0, False, "mid", [["s", 300]]])
        ok(r["res"]["hurt"] == 1, f"중등은 0.3초 늦으면 맞음 {r['res']}")
        # 휩쓸기
        r = await pg.evaluate(RUN, [1, False, "g34", [["L", "safe"]]])
        ok(r["kind"] == "sweep" and r["btn"] == 2 and r["sw"] and r["res"]["perf"] == 1 and r["res"]["hurt"] == 0, f"휩쓸기: ◀ ▶ 두 버튼 · 빨간 쪽 · 반대로 피함(직전) = 완벽 {r}")
        r = await pg.evaluate(RUN, [1, False, "g34", [["L", "same"]]])
        ok(r["res"]["hurt"] == 1, f"같은 쪽으로 = 맞음 {r['res']}")
        r = await pg.evaluate("""async ()=>{ const A=BossPat.run({j:1, k:'hb1-a', nm:'x', book:'g34', done:r=>{ window._r=r; }}); window._r=null; await new Promise(r=>setTimeout(r,300));
          const z=document.querySelector('.rsHero.me .bpSw'), early=[!!z, z && z.classList.contains('on'), A.rv-A.t0];
          BossPat.tick(A.rv+50); const flash=z.classList.contains('on'); BossPat.tick(A.rv+500); const after=z.classList.contains('on');
          BossPat.press(A.side==='L'?'R':'L', A.rv-100); for(let t=0;t<20 && !window._r;t++) await new Promise(r=>setTimeout(r,100));
          return {early, flash, after, done:A.done, res:window._r}; }""")
        ok(r["early"][0] and not r["early"][1] and r["early"][2] == 1300 and r["flash"] and not r["after"], f"빨간 쪽은 처음엔 안 보이고 맞기 0.7초 전에 한 번만 짧게 번쩍 {r['early']} {r['flash']} {r['after']}")
        ok(r["done"] == ["early"] and r["res"]["hurt"] == 1, f"번쩍이기 전에 피하면 = 너무 빨라요(맞음) {r['done']}")
        # 연속 발사
        r = await pg.evaluate(RUN, [2, False, "g34", [["s", 0], ["s", 30], ["s", 300]]])
        ok(r["kind"] == "burst" and r["n"] == 3 and r["res"]["perf"] == 2 and r["res"]["good"] == 1 and r["res"]["hurt"] == 0, f"연속 발사: 공 3개 · 박자마다 막기 {r['res']}")
        r = await pg.evaluate(RUN, [2, False, "g34", [["s", 0]]])
        ok(r["res"]["ok"] == 1 and r["res"]["hurt"] == 2, f"하나만 막으면 ❤️-2 {r['res']}")
        # 필살기
        r = await pg.evaluate(RUN, [0, True, "g34", [["s", 0]]])
        ok(r["kind"] == "fin" and r["res"]["hurt"] == 0 and r["res"]["perf"] == 1, f"필살기: 완벽 = 버팀 {r['res']}")
        r = await pg.evaluate(RUN, [0, True, "g34", [["s", 250]]])
        ok(r["res"]["hurt"] == 1, f"필살기: 그냥 막기 = ❤️-1 {r['res']}")
        r = await pg.evaluate(RUN, [0, True, "g34", []])
        ok(r["res"]["hurt"] == 2, f"필살기: 못 막음 = ❤️-2 {r['res']}")
        # 키보드
        r = await pg.evaluate("""async ()=>{ const A=BossPat.run({j:0, k:'hb1-a', nm:'x', book:'g34', done:r=>{ window._r=r; }}); window._r=null; await new Promise(r=>setTimeout(r, Math.max(0, A.hits[0]-performance.now()-30)));
          document.dispatchEvent(new KeyboardEvent('keydown', {key:' ', bubbles:true})); for(let t=0;t<20 && !window._r;t++) await new Promise(r=>setTimeout(r,100)); return window._r; }""")
        ok(r and r["ok"] == 1, f"키보드 Space = 막기 {r}")
        # ── 주간 보스: 하트 · 기절 → 기회 -1
        await pg.evaluate("""()=>{ HyBoss.live(); return FB.set('/hy/roster', {t:{}, k:{k1:{n:'민준'}}}).then(()=>HyBoss.setup({on:true, team:false, split:'eq', restart:true})); }"""); await pg.wait_for_timeout(400)
        await pg.evaluate("()=>{ Kid.set({id:'k1',n:'민준',t:'all'}); HyBoss.earn(Kid.get(),'study',8); WeekBoss.open(); }"); await pg.wait_for_timeout(900)
        await pg.evaluate("()=>{ WeekBoss.swing(); }"); await pg.wait_for_timeout(300)
        await pg.evaluate("()=>{ WeekBoss.F.next=1; WeekBoss.F.lock=0; WeekBoss.swing(); }"); await pg.wait_for_function("()=>BossPat.A", timeout=4000)
        await pg.evaluate("()=>patSolve(true)"); await pg.wait_for_function("()=>!BossPat.A && WeekBoss.F && WeekBoss.F.phase==='idle'", timeout=4000)
        c = await pg.evaluate("()=>WeekBoss.F.combo")
        h0 = await pg.evaluate("()=>HyBoss.mine('k1').d|0")
        await pg.evaluate("()=>{ WeekBoss.F.lock=0; WeekBoss.F.next=9; Math._r=Math.random; Math.random=()=>0.5; WeekBoss.swing(); Math.random=Math._r; }"); await pg.wait_for_timeout(200)
        h1 = await pg.evaluate("()=>HyBoss.mine('k1').d|0")
        ok(c >= 1 and h1 - h0 == 10 + min(10, c), f"막기 콤보만큼 공격 + (콤보 {c}: {h1-h0})")
        # 주간 보스 = 연습용: 여러 번 맞아도 기회 그대로 · 기절 없음 · 콤보만 끊김
        s0 = await pg.evaluate("()=>{ const k=HyBoss.stock('k1'); return k.r+k.s; }")
        for i in range(3):
            await pg.evaluate("()=>{ WeekBoss.F.next=1; WeekBoss.F.lock=0; WeekBoss.F.next=0; WeekBoss.bossTurn(); }"); await pg.wait_for_function("()=>BossPat.A", timeout=4000)
            await pg.evaluate("()=>patSolve(false)"); await pg.wait_for_function("()=>!BossPat.A && WeekBoss.F && WeekBoss.F.phase==='idle'", timeout=5000)
        r = await pg.evaluate("()=>{ const k=HyBoss.stock('k1'); return [k.r+k.s, WeekBoss.F.combo, WeekBoss.F.hit>=3, !document.getElementById('wbRes'), document.getElementById('wbFHint').innerText]; }")
        ok(r[0] == s0 and r[1] == 0 and r[2] and r[3], f"주간 보스 연습: 맞아도 기회 그대로 · 기절 없음 · 콤보 0 {s0} {r[:4]}")
        await pg.evaluate("()=>{ WeekBoss.F.next=0; WeekBoss.bossTurn(); }"); await pg.wait_for_function("()=>BossPat.A", timeout=4000)
        await pg.evaluate("()=>WeekBoss.endFight()")
        r = await pg.evaluate("()=>{ const k=HyBoss.stock('k1'); return [k.r+k.s, !!BossPat.A, !!document.getElementById('bpCtl')]; }")
        ok(r == [s0, False, False], f"공격 중에 닫아도 손해 없음 · 버튼 사라짐 {s0} {r}")
        # ── 수업 레이드: 패턴 · 하트 3 · 반격
        ctx2 = await br.new_context(viewport={"width": 1024, "height": 768}); await ctx2.add_init_script("window.HY_FB_LOCAL=true;")
        T = await ctx2.new_page(); T.on("pageerror", lambda e: errs.append("T " + str(e))); await boot(T)
        room = await T.evaluate("()=>{ Raid.host('g34', [], 0, null, 900, 'all'); return Raid.room; }"); await T.wait_for_timeout(800)
        K = await ctx2.new_page(); K.on("pageerror", lambda e: errs.append("K " + str(e))); await K.set_viewport_size({"width": 390, "height": 844}); await boot(K)
        await K.evaluate(f"()=>Raid.join('{room}', '민준')"); await K.wait_for_timeout(800)
        await T.evaluate("()=>Raid.hostAct('start')"); await T.wait_for_timeout(800)
        await K.wait_for_timeout(500)
        await K.evaluate("()=>{ Raid.atk=null; Raid.nextAtk=1; Raid.restTo=0; }"); await K.wait_for_function("()=>BossPat.A && Raid.atk && Raid.atk.pat", timeout=5000)
        r = await K.evaluate("()=>[BossPat.A.W.g, document.getElementById('rdIn').innerText.indexOf('막거나 피해요')>=0, !!document.getElementById('bpCtl')]")
        ok(r == [340, True, True], f"레이드: 보스 공격 = 패턴 (G3-4 판정) · 안내 · 큰 버튼 {r}")
        d0 = await K.evaluate("()=>[Raid.dmg, Raid.blk, Raid.hearts]")
        k = await K.evaluate("()=>patSolve(true)"); await K.wait_for_function("()=>!BossPat.A && !Raid.atk", timeout=4000)
        d1 = await K.evaluate("()=>[Raid.dmg, Raid.blk, Raid.hearts]")
        n = 3 if k == "burst" else 1
        ok(d1[0] - d0[0] == 25 * n and d1[1] - d0[1] == n and d1[2] == d0[2], f"레이드: 완벽 막기 = 반격 25 · 🛡 {k} {d0} {d1}")
        await K.evaluate("()=>{ Raid.nextAtk=1; Raid.restTo=0; }"); await K.wait_for_function("()=>BossPat.A && Raid.atk && Raid.atk.pat", timeout=5000)
        k = await K.evaluate("()=>patSolve(false)"); await K.wait_for_function("()=>!BossPat.A && !Raid.atk", timeout=4000)
        d2 = await K.evaluate("()=>[Raid.hearts, Raid.restTo > Raid.now()]")
        ok((k == "burst" and d2 == [3, True]) or (k != "burst" and d2 == [2, False]), f"레이드: 못 막으면 하트 -1 (연속 발사 3개 다 = 쉬기) {k} {d2}")
        await br.close()
    e = real_errs(errs)
    ok(not e, f"스크립트 오류 없음 {e[:3]}")
    print("\nALL OK" if not bad else "\nFAIL", bad)
    sys.exit(1 if bad else 0)
asyncio.run(main())
