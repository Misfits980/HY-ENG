"""(v328) 📝 선생님 시험 — 평소에는 안 보이고 선생님이 열 때만 · 보카 올림피아드 틀(A·B·C · 문제당 시간) · 책 + Stage 범위
   🏫 수업 중 다 같이(곧 시험 → ▶ 시작) · ⏰ 열어 두기 · 한 번만 · 그만두면 푼 것까지 · 선생님 결과표 · 📺 크게 보기 · ↺ 다시 보게 · 지난 시험"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

async def kid(ctx, errs, k, n):
    pg = await ctx.new_page(); await pg.set_viewport_size({"width": 390, "height": 844})
    pg.on("pageerror", lambda e: errs.append(n + " " + str(e))); await boot(pg)
    await pg.evaluate(f"()=>{{ localStorage.setItem('hyeng_nick','한양패드'); window.confirm=()=>true; Kid.set({{id:'{k}',n:'{n}',t:'all'}}); show('scStart'); }}")
    return pg

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={"width": 1180, "height": 820})
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        T = await ctx.new_page(); T.on("pageerror", lambda e: errs.append("T " + str(e))); await boot(T)
        await T.evaluate("()=>{ sessionStorage.setItem('hyeng_admin_ok',String(Date.now())); sessionStorage.setItem('hyeng_admin_tk','testkey'); }"); await T.reload(); await T.wait_for_timeout(1500)
        await T.evaluate("()=>{ window.confirm=()=>true; return FB.set('/hy/roster', {t:{}, k:{k1:{n:'민준'},k2:{n:'서연'}}}); }")
        K1 = await kid(ctx, errs, "k1", "민준"); K2 = await kid(ctx, errs, "k2", "서연")
        # 평소에는 안 보임
        await K1.evaluate("()=>HyExam.check(true)"); await K1.wait_for_timeout(200)
        ok(await K1.evaluate("()=>!document.getElementById('exChip') || document.getElementById('exChip').hidden"), "평소에는 시험 버튼 없음")
        # 선생님 — 관리 화면 📝 시험 탭
        await T.evaluate("()=>{ document.querySelectorAll('.sheet.on').forEach(s=>s.classList.remove('on')); Admin.open(); }"); await T.wait_for_timeout(500)
        await T.evaluate("()=>document.querySelector('#adTabs [data-t=\"exam\"]').click()"); await T.wait_for_timeout(600)
        await T.evaluate("()=>{ const s=document.getElementById('adExSet'); s.value='elem'; s.dispatchEvent(new Event('change')); document.getElementById('adExTo').value='5'; document.getElementById('adExTo').dispatchEvent(new Event('change')); document.getElementById('adExN').value='20'; document.getElementById('adExN').dispatchEvent(new Event('change')); }"); await T.wait_for_timeout(200)
        info = await T.evaluate("()=>document.getElementById('adExInfo').textContent")
        print("info", info)
        ok("20문제" in info and "Starter" in info and "Pre-Starter" not in info and "A 7초 · B 8초 · C 11초" in info, "범위 · 단계 자동(G3-4 = Starter, v333) · 시간표")
        await T.screenshot(path=OUT + "exam_admin_form.png")
        await T.evaluate("()=>document.querySelector('[data-ad=\"exOpen\"]').click()"); await T.wait_for_timeout(600)
        cur = await T.evaluate("()=>FB.get('/hy/exam/open').then(O=>Object.values(O||{}).sort((a,b)=>b.at-a.at)[0])")
        ok(cur and cur["st"] == "wait" and cur["mode"] == "live" and cur["n"] == 20 and cur["set"] == "elem", f"시험 열림 (기다림) {cur and cur['title']}")
        # 아이 — 곧 시험
        await K1.evaluate("()=>HyExam.check(true)"); await K1.wait_for_timeout(200)
        r = await K1.evaluate("()=>{ const b=document.getElementById('exChip'); return b && !b.hidden ? [b.className, b.innerText] : null; }")
        ok(r and "wait" in r[0] and "곧 시험" in r[1], f"아이: 곧 시험 {r}")
        ok(not await K1.evaluate("()=>!!document.getElementById('exAsk')"), "시작 전엔 큰 알림 없음")
        await K1.screenshot(path=OUT + "exam_wait.png")
        # ▶ 시작
        await T.evaluate("()=>document.querySelector('[data-ad=\"exStart\"]').click()"); await T.wait_for_timeout(500)
        for K in (K1, K2): await K.evaluate("()=>HyExam.check(true)")
        await K1.wait_for_timeout(300)
        ok(await K1.evaluate("()=>!!document.getElementById('exAsk')"), "시작 → 아이 화면에 시험 알림")
        await K1.screenshot(path=OUT + "exam_ask.png")
        await K1.evaluate("()=>document.querySelector('#exAsk [data-ex=\"go\"]').click()"); await K1.wait_for_timeout(3000)
        q = await K1.evaluate("()=>{ const U=StudyUI, Q=U.qs.filter(q=>q.t!=='intro'); return {ex:!!U.ex, oly:U.oly, n:Q.length, intro:U.qs[0].hd, secs:[...new Set(Q.map(q=>q.sec))].sort((a,b)=>a-b), ab:[...new Set(Q.map(q=>q.ab))]}; }")
        print("kid1", q)
        ok(q["ex"] and q["oly"] and q["n"] == 20 and q["intro"] == "oly" and set(q["secs"]) <= {7, 8, 11} and "A" in q["ab"], f"시험 20문제 · 시간 {q['secs']} · 유형 {q['ab']}")
        await K1.screenshot(path=OUT + "exam_intro.png")
        st = await T.evaluate("()=>FB.get('/hy/exam/res/'+HyExam.L[HyExam.L.length-1].id+'/k1')")
        ok(st and st.get("st") == 1 and st.get("sc") is None, "시작하면 서버에 '보는 중'")
        # 같은 단어 (seed)
        await K2.evaluate("()=>document.querySelector('#exAsk [data-ex=\"go\"]').click()"); await K2.wait_for_timeout(3000)
        same = await K1.evaluate("()=>StudyUI.qs.filter(q=>q.t!=='intro').map(q=>q.w.en).sort().join(',')") == await K2.evaluate("()=>StudyUI.qs.filter(q=>q.t!=='intro').map(q=>q.w.en).sort().join(',')")
        ok(same, "모든 아이가 같은 단어")
        # 민준: 끝까지 (2개 틀림)
        wn = 0
        for i in range(80):
            if await K1.evaluate("()=>document.getElementById('stDone').style.display!=='none'"): break
            st2 = await K1.evaluate("()=>{ const U=StudyUI, q=U.qs[U.i]; return q ? [q.t, !!U.locked] : null; }")
            if st2 and st2[0] != "intro" and not st2[1] and wn < 2:
                await K1.evaluate("()=>{ StudyUI.sel=-1; StudyUI.result(false); }"); wn += 1
            else:
                await K1.evaluate("()=>{ StudyUI._qAt=0; }"); await K1.evaluate(SOLVE, False)
            await K1.wait_for_timeout(760)
        done = await K1.evaluate("()=>document.getElementById('stDoneIn').innerText")
        print("done", done[:120].replace("\n", " / "))
        ok("90" in done and "점" in done and "다시 볼 단어" in done, "민준 결과 화면 (18/20 = 90점)")
        await K1.screenshot(path=OUT + "exam_done.png")
        await T.wait_for_timeout(500)
        r1 = await T.evaluate("()=>FB.get('/hy/exam/res/'+HyExam.L[HyExam.L.length-1].id+'/k1')")
        ok(r1 and r1.get("sc") == 90 and r1.get("ok") == 18 and r1.get("tot") == 20 and r1.get("fin") == 1 and r1.get("miss"), f"서버 점수 {r1 and r1.get('sc')} · 틀린 단어 {r1 and r1.get('miss')}")
        # 서연: 5문제 풀고 그만두기 → 푼 것까지
        for i in range(30):
            pr = await K2.evaluate("()=>StudyUI.qs.filter(q=>q.t!=='intro' && q._r!=null).length")
            if pr >= 5: break
            await K2.evaluate("()=>{ StudyUI._qAt=0; }"); await K2.evaluate(SOLVE, False); await K2.wait_for_timeout(760)
        await K2.evaluate("()=>{ if(StudyUI.locked) document.getElementById('stCheck').click(); }"); await K2.wait_for_timeout(300)
        await K2.evaluate("()=>document.getElementById('stQuit').click()"); await K2.wait_for_timeout(500)
        r2 = await T.evaluate("()=>FB.get('/hy/exam/res/'+HyExam.L[HyExam.L.length-1].id+'/k2')")
        print("k2", r2)
        ok(r2 and r2.get("fin") == 1 and r2.get("sc") is not None and r2["sc"] <= 30, f"그만두면 푼 것까지 점수 {r2 and r2.get('sc')}")
        # 다시 못 봄
        await K1.evaluate("()=>{ document.getElementById('stBack').click(); show('scStart'); return HyExam.check(true); }"); await K1.wait_for_timeout(300)
        ok(await K1.evaluate("()=>!document.getElementById('exChip') || document.getElementById('exChip').hidden"), "본 아이는 시험 버튼 없음")
        await K1.evaluate("()=>HyExam.go()"); await K1.wait_for_timeout(500)
        ok(await K1.evaluate("()=>!StudyUI.ex && document.getElementById('stLesson').style.display==='none'"), "다시 시작 안 됨")
        # 선생님 결과표 · TV
        await T.wait_for_timeout(600)
        tb = await T.evaluate("()=>document.querySelector('[id^=adExRes_]').innerText")
        print("table", tb.replace("\n", " / ")[:200])
        ok("민준" in tb and "서연" in tb and "90" in tb and "평균" in tb, "선생님 결과표 (실시간)")
        await T.screenshot(path=OUT + "exam_admin_live.png")
        await T.evaluate("()=>document.querySelector('[data-ad=\"exTv\"]').click()"); await T.wait_for_timeout(300)
        tv = await T.evaluate("()=>document.getElementById('exTv').innerText")
        ok("🥇" in tv and "민준" in tv, "📺 크게 보기")
        await T.screenshot(path=OUT + "exam_tv.png")
        await T.evaluate("()=>document.querySelector('#exTv [data-extvx]').click()")
        # ↺ 서연 다시 보게
        await T.evaluate("()=>document.querySelector('[data-ad=\"exReset\"][data-k=\"k2\"]').click()"); await T.wait_for_timeout(300)
        ok(await T.evaluate("()=>FB.get('/hy/exam/res/'+HyExam.L[HyExam.L.length-1].id+'/k2').then(r=>r==null)"), "↺ 다시 보게 → 기록 지움")
        # 끝내기 → 아이 화면에서 사라짐 · 지난 시험
        await T.evaluate("()=>document.querySelector('[data-ad=\"exEnd\"]').click()"); await T.wait_for_timeout(700)
        await K2.evaluate("()=>{ show('scStart'); return HyExam.check(true); }"); await K2.wait_for_timeout(200)
        ok(await K2.evaluate("()=>!document.getElementById('exChip') || document.getElementById('exChip').hidden"), "끝내면 아이 화면에서 사라짐")
        hist = await T.evaluate("()=>document.getElementById('adExHist').innerText")
        ok("G3-4" in hist or "시험" in hist, f"지난 시험 목록 {hist[:60]!r}")
        # ⏰ 열어 두기 — 바로 열림
        await T.evaluate("()=>{ const s=document.getElementById('adExSet'); s.value='mid'; s.dispatchEvent(new Event('change')); document.getElementById('adExMode').value='open'; document.getElementById('adExMode').dispatchEvent(new Event('change')); document.getElementById('adExP').value='hj'; }")
        await T.evaluate("()=>document.querySelector('[data-ad=\"exOpen\"]').click()"); await T.wait_for_timeout(500)
        cur = await T.evaluate("()=>FB.get('/hy/exam/open').then(O=>Object.values(O||{}).sort((a,b)=>b.at-a.at)[0])")
        ok(cur["mode"] == "open" and cur["st"] == "run" and cur["until"] > 0 and cur["P"] == "hj", "열어 두기 = 바로 열림 · 마감 · High Junior")
        await K2.evaluate("()=>HyExam.check(true)"); await K2.wait_for_timeout(300)
        ask = await K2.evaluate("()=>{ const a=document.getElementById('exAsk'); return a ? a.innerText : ''; }")
        ok("남음" in ask, f"열어 두기 알림 (남은 시간) {ask[:80]!r}")
        secs = await K2.evaluate("()=>{ const q=Study.buildExam(HyExam.c); return [...new Set(q.filter(x=>x.t!=='intro').map(x=>x.sec))].sort((a,b)=>a-b); }")
        ok(set(secs) <= {7, 12, 15} and 7 in secs, f"High Junior 시간 {secs}")
        ok(not errs, "오류 없음 " + str(errs[:3]))
        await br.close()
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)

asyncio.run(main())
