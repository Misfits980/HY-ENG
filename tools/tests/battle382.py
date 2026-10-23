"""(v382) 사용자: 교실 배틀이 많이 불편함 (입장 · 선생님 설정 · TV 가 심심함 · 문제가 쉬움 · 반을 고를 칸도 방법도 없음) — 방 번호(비밀번호)는 그대로
  ① 수업 입장: 이름 먼저 · 큰 숫자판 · 4자리 다 누르면 바로 들어감 · 쓴 이름 기억
  ② 🔴🔵 두 팀 대결: 반 명단 없이 들어온 아이를 자동으로 두 팀(적은 쪽으로) · 🔀 섞기 · 팀 깃발 두 줄 · 아이 화면에 내 팀
  ③ 점수: ⚡ 번개 문제(6문제마다) 3배 · 🔥 마지막 30초 2배 · 빨리 맞히면 +3
  ④ 새 문제: 👀 순간 기억 · 🔊 듣고 철자 · 「시험처럼」에도 재미 문제 섞기
  ⑤ TV: 1·2·3등 크게 · 실시간 소식 · 끝나면 캐릭터 시상대 · 관리: ⚡ 지난번처럼 바로 만들기 · 반 명단이 없으면 안내"""
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
        T = await ctx.new_page(); T.on("pageerror", lambda e: errs.append("T " + str(e))); await boot(T); await T.evaluate('()=>{ Battle.FR=false; }')
        # ⑤ 관리: 반 명단 없음 안내 · 방식 3가지
        await T.evaluate("()=>{ Admin.open(); Admin._tab('play'); }"); await T.wait_for_timeout(800)
        r = await T.evaluate("()=>{ const m=[...document.querySelectorAll('#adBtMode option')].map(o=>o.value); const tx=document.getElementById('shAdmin').innerText; return {m, hint:tx.indexOf('반 명단이 아직 없어요')>=0, last:!!document.querySelector('[data-ad=btLast]'), fun:!!document.getElementById('adBtFun'), cls:!!document.getElementById('adBtCls')}; }")
        ok(r["m"] == ["score", "auto", "flag"] and r["hint"] and not r["last"] and r["fun"] and r["cls"], f"배틀 설정: 개인·두 팀·반 대항 · 반 명단 없음 안내 {r}")
        await T.evaluate("()=>{ const m=document.getElementById('adBtMode'); m.value='auto'; m.dispatchEvent(new Event('change')); const d=document.getElementById('adBtDur'); d.value='180'; document.querySelector('[data-ad=btGo]').click(); }")
        await T.wait_for_timeout(1200)
        r = await T.evaluate("()=>[Battle.role, Battle.cfg().tmode, Battle.cfg().mode, Battle.cfg().fun, JSON.parse(localStorage.getItem('hyeng_bt_last')||'{}').mode]")
        ok(r == ["host", "auto", "flag", 1, "auto"], f"두 팀 방 만들기 · 지난 설정 기억 {r}")
        room = await T.evaluate("()=>Battle.room")
        # ① 아이 입장 — 이름 먼저 · 숫자판 4자리면 바로
        K = []
        for i, nm in enumerate(["민준", "서연", "지호", "하린", "도윤"]):
            k = await ctx.new_page(); k.on("pageerror", lambda e, n=nm: errs.append(n + " " + str(e))); await k.set_viewport_size({"width": 390, "height": 844}); await boot(k); await k.evaluate('()=>{ Battle.FR=false; }')
            await k.evaluate("()=>RaidJoin.open()"); await k.wait_for_timeout(150)
            await k.evaluate(f"()=>{{ document.getElementById('rdNameIn').value='{nm}'; }}")
            for d in room: await k.evaluate(f"()=>document.querySelector('[data-rjk=\"{d}\"]').click()")
            await k.wait_for_timeout(900); K.append(k)
        r = await K[0].evaluate("()=>[Battle.role, Battle.room, !!document.getElementById('rdJoin'), localStorage.getItem('hyeng_raid_name')]")
        ok(r == ["kid", room, False, "도윤"], f"숫자판 4자리 → 바로 들어감 · 쓴 이름 기억 (같은 브라우저라 마지막 이름) {r}")
        r = await K[1].evaluate("()=>{ RaidJoin.open(); const v=document.getElementById('rdNameIn').value; RaidJoin.close(); return v; }")
        ok(r == "도윤", f"다음에 열면 이름이 들어 있음 {r}")
        # ② 두 팀 자동
        await T.wait_for_timeout(1200)
        r = await T.evaluate("()=>{ const P=Battle.T().p||{}; const t=Object.keys(P).map(k=>P[k].tm); return {r:t.filter(x=>x==='r').length, b:t.filter(x=>x==='b').length, lanes:Battle.teamsOf().map(a=>a.t).sort(), cols:document.querySelectorAll('.btCol').length}; }")
        ok(r["r"] + r["b"] == 5 and abs(r["r"] - r["b"]) <= 1 and r["lanes"] == ["b", "r"] and r["cols"] == 2, f"들어온 아이를 두 팀으로 고르게 · 두 줄 · 대기 화면 팀 칸 {r}")
        t0 = await T.evaluate("()=>{ const P=Battle.T().p||{}; return Object.keys(P).sort().map(k=>P[k].tm).join(''); }")
        await T.evaluate("()=>{ for(let i=0;i<6;i++) Battle.hostAct('shuffle'); }"); await T.wait_for_timeout(800)
        r = await T.evaluate("()=>{ const P=Battle.T().p||{}; const t=Object.keys(P).map(k=>P[k].tm); return [t.filter(x=>x==='r').length, t.filter(x=>x==='b').length]; }")
        ok(abs(r[0] - r[1]) <= 1, f"🔀 섞어도 고르게 {r}")
        await K[0].wait_for_timeout(600)
        r = await K[0].evaluate("()=>{ const tm=(Battle.T().p||{})[Battle.me].tm; return [tm, (document.querySelector('.btMyTeam')||{}).className||'', document.getElementById('rdIn').innerText.indexOf('팀')>=0]; }")
        ok(r[0] in ("r", "b") and r[0] in r[1] and r[2], f"아이 대기 화면에 내 팀 {r}")
        # ③ 점수 — 번개 · 2배 · 빠름
        await T.evaluate("()=>Battle.hostAct('start')"); await T.wait_for_timeout(4200)
        r = await K[0].evaluate("""()=>{ Battle.FAST=0; const out={}; const c=Battle.cfg(); c.lvl='easy'; c.qt=['mean']; const go=(zap, dbl, fast)=>{ Battle.streak=0; const q=Battle.mkQ(); q.zap=zap; Battle.q=q; Battle.qAt=Battle.now()-(fast?100:5000); const d0=Battle.dbl; if(dbl) Battle.dbl=()=>true; else Battle.dbl=()=>false;
              const s0=Battle.sc; Battle.answer(q.ans!=null?q.ans:q.opts.findIndex(o=>o.en===q.w.en)); Battle.dbl=d0; return Battle.sc-s0; };
            out.base=go(false,false,false); out.fast=go(false,false,true); out.dbl=go(false,true,false); out.zap=go(true,false,false); return out; }""")
        b = r["base"]
        ok(r["fast"] == b + 3 and r["dbl"] == b * 2 and r["zap"] == b * 3, f"빠름 +3 · 2배 · 번개 3배 {r}")
        # (v384) 번개 문제 간격 = 순위 (위 7 · 가운데 6 · 아래 5 · 맨 끝이고 많이 뒤지면 4) · 처음 4문제는 없음
        r = await K[0].evaluate("""()=>{ const P=Battle.T().p||{}, ks=Object.keys(P), me=Battle.me, sv=Battle.sc, out={};
            const cnt=(mySc, others)=>{ Battle._poll=null; const fake={}; ks.forEach((k,i)=>{ fake[k]=Object.assign({}, P[k], {sc: k===me ? mySc : others[i%others.length]}); }); const t0=Battle.T; Battle.T=()=>Object.assign({}, t0.call(Battle), {p:fake}); Battle.sc=mySc;
              let n=0, first=99; Battle._qn=0; Battle._zg=0; for(let i=0;i<60;i++){ const q=Battle.nextQ(); if(q.zap){ n++; first=Math.min(first, i+1); } } Battle.T=t0; return [n, first, Battle.zapGap ? (Battle.T=()=>Object.assign({}, t0.call(Battle), {p:fake}), (()=>{ const g=Battle.zapGap(); Battle.T=t0; return g; })()) : 0]; };
            out.top=cnt(500,[100,90,80,70]); out.mid=cnt(85,[100,90,80,70]); out.low=cnt(60,[100,90,80,70]); out.far=cnt(10,[300,200,150,120]); Battle.sc=sv; return out; }""")
        print("zap", r)
        ok(r["top"][2] == 7 and r["low"][2] == 5 and r["far"][2] == 4 and r["top"][0] < r["low"][0] < r["far"][0] and r["far"][0] <= 15 and min(v[1] for v in r.values()) >= 5, f"번개 문제: 순위 낮을수록 조금 더 자주 (60문제에 위 {r['top'][0]} · 아래 {r['low'][0]} · 맨 끝 {r['far'][0]}) · 처음 4문제는 없음 {r}")
        r = await K[0].evaluate("""()=>{ const c=Battle.cfg(); const t0=Battle.st().t0, d=c.dur; Battle._dl=Battle.left; Battle.left=()=>20000; const a=Battle.dbl(); Battle.left=()=>60000; const b=Battle.dbl(); Battle.left=Battle._dl; return [a,b]; }""")
        ok(r == [True, False], f"마지막 30초만 2배 {r}")
        # ④ 새 문제
        r = await K[1].evaluate("""()=>{ const c=Battle.cfg(), q0=c.qt, l0=c.lvl; const T={}; c.lvl='easy'; c.qt=['flash','lsp']; for(let i=0;i<40;i++){ const q=Battle.mkQ(); T[q.t]=(T[q.t]||0)+1; }
            c.lvl='exam'; c.fun=1; const E={}; for(let i=0;i<200;i++){ const q=Battle.mkQ(); const k=q.exq?'exam':q.t; E[k]=(E[k]||0)+1; } c.qt=q0; c.lvl=l0; return {T, E}; }""")
        print(r)
        ok(r["T"].get("flash", 0) > 5 and r["T"].get("lsp", 0) > 5, f"👀 순간 기억 · 🔊 듣고 철자 {r['T']}")
        fun = sum(v for k, v in r["E"].items() if k != "exam")
        ok(r["E"].get("exam", 0) > 100 and 20 <= fun <= 90, f"시험처럼에도 재미 문제 섞임 {r['E']}")
        r = await K[1].evaluate("""()=>{ const c=Battle.cfg(); c.lvl='easy'; c.qt=['flash']; const q=Battle.mkQ(); q.zap=1; Battle.q=q; Battle.qAt=Battle.now(); Battle.draw(); const d=document.getElementById('rdIn'); return [!!d.querySelector('.btFlash'), !!d.querySelector('.rdQ.zap'), d.innerText.indexOf('번개')>=0, q.lab.indexOf(q.w.ko)===q.ans]; }""")
        ok(r == [True, True, True, True], f"순간 기억 화면 · 번개 표시 {r}")
        # ⑤ TV
        for step in range(25):
            for k in K: await k.evaluate("()=>{ const q=Battle.q; if(!q||q.done) return; Battle.FAST=0; Battle.answer(q.ans!=null?q.ans:q.opts.findIndex(o=>o.en===q.w.en)); }")
            await T.wait_for_timeout(120)
        r = await T.evaluate("()=>{ const d=document.getElementById('rdIn'); return [d.querySelectorAll('.btT3').length, d.querySelectorAll('.btFd:not(.idle)').length, d.querySelectorAll('.btLane').length]; }")
        ok(r[0] == 3 and r[1] >= 1 and r[2] == 2, f"TV: 1·2·3등 · 실시간 소식 · 두 팀 줄 {r}")
        await T.evaluate("()=>Battle.hostAct('end')"); await T.wait_for_timeout(3600)
        r = await T.evaluate("()=>{ const d=document.getElementById('rdIn'); return [d.querySelectorAll('.btPodium .btP').length, !!d.querySelector('.btWin')]; }")
        ok(r == [3, True], f"끝: 팀 우승 · 시상대 {r}")
        r = await K[0].evaluate("()=>[Battle.ended, Battle._gems>0]")
        ok(r == [True, True], f"아이 끝 · 보석 {r}")
        # ⚡ 지난번처럼
        await T.evaluate("()=>{ Battle.leave(); }"); await T.wait_for_timeout(300)
        await T.evaluate("()=>{ Admin.open(); Admin._tab('play'); }"); await T.wait_for_timeout(700)
        r = await T.evaluate("()=>{ const b=document.querySelector('[data-ad=btLast]'); if(!b) return null; const t=b.innerText; b.click(); return t; }")
        await T.wait_for_timeout(1200)
        r2 = await T.evaluate("()=>[Battle.role, Battle.cfg().tmode, Battle.cfg().dur]")
        ok(r and "두 팀" in r and r2 == ["host", "auto", 180], f"⚡ 지난번처럼 바로 만들기 {r} {r2}")
        e = real_errs(errs); ok(not e, "오류 없음 " + str(e[:3]))
        await br.close()
    print("결과:", "통과" if not bad else "실패 " + str(bad))
asyncio.run(main())
