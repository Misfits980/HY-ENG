"""(v389) 🏃 달리기 레이스 — 사용자: 워드 게이트 러너를 대결로 (교실 전체 · 빨강 vs 파랑) · 서로 안 보여도 머리 위에 1등·2등만 바뀌면 됨
  · 관리: 🏃 달리기 레이스 카드 (단어 · 방식 · 시간 · 난이도) → 교실 배틀 방 (cfg.kind run)
  · 시작하면 아이 패드마다 러너 출발 (같은 단어 칸·난이도) · 머리 위 배지 = 지금 순위 / 인원 · 남은 시간 · 두 팀이면 우리 팀 앞섬/따라감
  · 점수는 방에 씀 → TV 순위·팀 1인 평균 막대 · 하트를 다 잃으면 결과 화면 대신 배틀 화면에서 기다림
  · 시간 끝/선생님 끝 → 러너도 끝 · 순위 · 💎 (두 팀: 이긴 팀 4 · 진 팀 2) · 러너 결과 화면(scOver)은 안 뜸"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={"width": 1024, "height": 768})
        await ctx.add_init_script("window.HY_FB_LOCAL=true; try{ sessionStorage.setItem('hyeng_admin_ok', String(Date.now())); sessionStorage.setItem('hyeng_admin_tk','testkey'); }catch(e){}")
        T = await ctx.new_page(); T.on("pageerror", lambda e: errs.append("T " + str(e))); await boot(T)
        await T.evaluate("()=>{ Admin.open(); Admin._tab('play'); }"); await T.wait_for_timeout(800)
        r = await T.evaluate("()=>({set:[...document.querySelectorAll('#adRrSet option')].map(o=>o.value), mode:[...document.querySelectorAll('#adRrMode option')].map(o=>o.value), go:!!document.querySelector('[data-ad=rrGo]')})")
        ok("elem" in r["set"] and "mv1" in r["set"] and r["mode"] == ["score", "auto"] and r["go"], f"관리: 🏃 달리기 레이스 카드 {r}")
        await T.evaluate("()=>{ const m=document.getElementById('adRrMode'); m.value='auto'; document.getElementById('adRrDur').value='120'; document.getElementById('adRrSet').value='g56'; document.getElementById('adRrDiff').value='easy'; document.querySelector('[data-ad=rrGo]').click(); }")
        await T.wait_for_timeout(1200)
        r = await T.evaluate("()=>{ const c=Battle.cfg(); return [Battle.role, c.kind, c.rset, c.diff, c.dur, c.tmode, c.mode, document.getElementById('rdIn').innerText.indexOf('달리기')>=0]; }")
        ok(r == ["host", "run", "g56", "easy", 120, "auto", "score", True], f"레이스 방 만들기 (두 팀) {r}")
        room = await T.evaluate("()=>Battle.room")
        K = []
        for nm in ["민준", "서연", "지호", "하린"]:
            k = await ctx.new_page(); k.on("pageerror", lambda e, n=nm: errs.append(n + " " + str(e))); await k.set_viewport_size({"width": 820, "height": 1180}); await boot(k)
            await k.evaluate("()=>RaidJoin.open()"); await k.wait_for_timeout(150)
            await k.evaluate(f"()=>{{ document.getElementById('rdNameIn').value='{nm}'; }}")
            for d in room: await k.evaluate(f"()=>document.querySelector('[data-rjk=\"{d}\"]').click()")
            await k.wait_for_timeout(700); K.append(k)
        await T.wait_for_timeout(1500)
        r = await T.evaluate("()=>{ const P=Battle.T().p||{}; const t=Object.keys(P).map(k=>P[k].tm); return {n:t.length, r:t.filter(x=>x==='r').length, b:t.filter(x=>x==='b').length, cols:document.querySelectorAll('.btCol').length, btn:(document.querySelector('[data-bth=start]')||{}).innerText||''}; }")
        ok(r["n"] == 4 and r["r"] == 2 and r["b"] == 2 and r["cols"] == 2 and "레이스" in r["btn"], f"4명 · 두 팀 2:2 · 대기 화면 팀 칸 · 레이스 시작 버튼 {r}")
        await K[0].wait_for_timeout(400)
        r = await K[0].evaluate("()=>[document.getElementById('rdIn').innerText.indexOf('달리면서')>=0, !!document.querySelector('.btMyTeam')]")
        ok(r == [True, True], f"아이 대기: 달리기 안내 · 내 팀 {r}")
        await T.evaluate("()=>Battle.hostAct('start')"); await T.wait_for_timeout(4600)
        r = [await k.evaluate("()=>[!!G.race, G.running, G.set, G.diff, !!document.getElementById('rrBadge'), document.getElementById('scRaid').classList.contains('on')]") for k in K]
        ok(all(x == [True, True, "g56", "easy", True, False] for x in r), f"시작 → 아이마다 러너 출발 (같은 단어 칸·난이도) · 머리 위 배지 · 배틀 화면 숨김 {r}")
        # 점수 — 민준 400 · 서연 300 · 지호 200 · 하린 100
        tm = await T.evaluate("()=>{ const P=Battle.T().p||{}; const o={}; Object.keys(P).forEach(k=>o[P[k].n]=P[k].tm); return o; }")
        for k, s in zip(K, [400, 300, 200, 100]):
            await k.evaluate(f"()=>{{ G.score={s}; RunRace.push(true); }}")
        await T.wait_for_timeout(1500)
        r = [await k.evaluate("()=>{ RunRace.badge(); const b=document.getElementById('rrBadge'); return b.querySelector('.rrRk b').innerText; }") for k in K]
        ok(r[0].endswith("1등") and "🥇" in r[0] and r[1].endswith("2등") and r[2].endswith("3등") and r[3] == "4등", f"머리 위 순위 {r}")
        r = await K[3].evaluate("()=>[document.querySelector('#rrBadge .rrRk span').innerText, (document.querySelector('#rrBadge .rrTm')||{}).innerText||'', document.querySelector('#rrBadge .rrTi').innerText]")
        ok(r[0] == "/ 4명" and "팀" in r[1] and r[2].startswith("⏱"), f"배지: 인원 · 우리 팀 · 남은 시간 {r}")
        # 역전 → 위로 (up)
        await K[3].evaluate("()=>{ G.score=900; RunRace.push(true); RunRace.badge(); }")
        r = await K[3].evaluate("()=>[document.querySelector('#rrBadge .rrRk b').innerText, document.getElementById('rrBadge').classList.contains('up')]")
        ok(r[0].endswith("1등") and r[1], f"역전하면 1등 · 올라가는 효과 {r}")
        r = await T.evaluate("()=>{ const a=Battle.runTeams(); return {bar:document.querySelectorAll('#rdIn .rrBar .rrT').length, a}; }")
        exp = {"r": 0, "b": 0}; cnt = {"r": 0, "b": 0}
        for nm, s in zip(["민준", "서연", "지호", "하린"], [400, 300, 200, 900]): exp[tm[nm]] += s; cnt[tm[nm]] += 1
        ok(r["bar"] == 2 and r["a"]["r"]["a"] == round(exp["r"] / cnt["r"]) and r["a"]["b"]["a"] == round(exp["b"] / cnt["b"]), f"TV: 두 팀 1인 평균 막대 {r} 기대 {exp}")
        # 지호: 하트 다 잃음 → 결과 화면 대신 배틀 화면에서 기다림
        await K[2].evaluate("()=>{ G.lives=0; gameOver(); }"); await K[2].wait_for_timeout(1200)
        r = await K[2].evaluate("()=>[!!G.race, G.running, document.getElementById('scRaid').classList.contains('on'), document.getElementById('scOver').classList.contains('on'), !!document.getElementById('rrBadge'), document.getElementById('rdIn').innerText.indexOf('다 달렸어요')>=0, Battle._raced]")
        ok(r == [False, False, True, False, False, True, 1], f"먼저 끝난 아이: 배틀 화면에서 기다림 (결과 화면 X · 배지 X) {r}")
        await K[2].wait_for_timeout(500)
        r = await K[2].evaluate("()=>[!!G.race, G.running]")
        ok(r == [False, False], f"먼저 끝난 아이는 다시 출발하지 않음 {r}")
        # 선생님 끝 → 나머지 러너도 끝 · 순위 · 💎
        g0 = [await k.evaluate("()=>Wallet.gems()") for k in K]
        await T.evaluate("()=>Battle.hostAct('end')"); await T.wait_for_timeout(5200)
        r = [await k.evaluate("()=>[!!G.race, G.running, document.getElementById('scOver').classList.contains('on'), Battle.ended, Battle._gems, Battle._win]") for k in K]
        win = "r" if exp["r"] / cnt["r"] > exp["b"] / cnt["b"] else "b"
        expg = [4 if tm[nm] == win else 2 for nm in ["민준", "서연", "지호", "하린"]]
        ok(all(x[:4] == [False, False, False, True] for x in r) and [x[4] for x in r] == expg, f"끝 → 러너도 끝 · 결과 화면 X · 이긴 팀 💎4 진 팀 💎2 {r} 기대 {expg}")
        r = await K[0].evaluate("()=>[document.getElementById('rdIn').innerText, document.querySelectorAll('#rdIn .rrBar').length]")
        ok(("승리" in r[0] or "잘 달렸어요" in r[0]) and r[1] == 1, f"아이 끝 화면: 팀 결과 · 막대 {r[0][:60]!r}")
        r = await T.evaluate("()=>[document.querySelector('#rdIn .btWin') && document.querySelector('#rdIn .btWin').innerText, document.querySelectorAll('#rdIn .btPodium .btP').length]")
        ok(r[0] and ("승리" in r[0]) and r[1] >= 3, f"TV 끝: 이긴 팀 · 시상대 {r}")
        # 🔁 한 판 더 → 다시 달림 (점수 0 부터)
        await T.evaluate("()=>Battle.hostAct('again')"); await T.wait_for_timeout(1500)
        await T.evaluate("()=>Battle.hostAct('start')"); await T.wait_for_timeout(4800)
        r = [await k.evaluate("()=>[!!G.race, G.running, RunRace.score()<900]") for k in K]
        ok(all(x == [True, True, True] for x in r), f"한 판 더 → 모두 다시 출발 (지호도) {r}")
        await T.evaluate("()=>Battle.hostAct('end')"); await T.wait_for_timeout(1500)
        # 개인 레이스 (반 전체 순위)
        await T.evaluate("()=>{ Battle.leave(); }"); await T.wait_for_timeout(600)
        await T.evaluate("()=>{ Admin.open(); Admin._tab('play'); }"); await T.wait_for_timeout(600)
        await T.evaluate("()=>{ document.getElementById('adRrMode').value='score'; document.querySelector('[data-ad=rrGo]').click(); }"); await T.wait_for_timeout(1200)
        r = await T.evaluate("()=>[Battle.cfg().kind, Battle.cfg().tmode, Battle.cfg().rset, Battle.cfg().dur, Battle.auto()]")
        ok(r == ["run", "solo", "elem", 180, False], f"개인 레이스 (기본 3분 · G3-4) {r}")
        await br.close()
    e = real_errs(errs)
    ok(not e, f"스크립트 오류 없음 {e[:3]}")
    print("\nALL OK" if not bad else "\nFAIL", bad)
    sys.exit(1 if bad else 0)
asyncio.run(main())
