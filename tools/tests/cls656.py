# v656 🖨 시험지 날짜·오답 노트 · 숙제 안내 쪽지 · 🏫 수업 게임 공통(틀린 단어 → 복습 · TV 한 줄 · 기록) · 🏫 한밤의 학교
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
bad = []
def ok(c, m):
    print(("OK  " if c else "BAD ") + m)
    if not c: bad.append(m)
ROSTER = {"t": {"a": {"n": "사자반", "e": "🦁"}}, "k": {"k1": {"n": "민준", "t": "a"}, "k2": {"n": "서연", "t": "a"}, "k3": {"n": "하윤", "t": "a"}}}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={"width": 1280, "height": 900}); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        T = await ctx.new_page(); errs = []; T.on("pageerror", lambda e: errs.append(str(e))); await boot(T); E = T.evaluate
        # ── 시험지
        await E("()=>{ localStorage.removeItem('hyeng_paper'); Paper.open({set:'elem', from:0, to:2, mode:'test'}); }"); await T.wait_for_timeout(1800)
        r = await E("""()=>{ const W=document.getElementById('ppWrap'); const pg=[...W.querySelectorAll('.pp:not(.key):not(.rd)')], N=[...W.querySelectorAll('.ppNote')];
          return [W.querySelectorAll('.ppHdF i.d').length, N.length, N.map(n=>n.querySelectorAll('.ppNR:not(.hd)').length), [...W.querySelectorAll('.ppCol')].filter(c=>c.scrollHeight>c.clientHeight+1).length, pg.length, document.getElementById('ppNote').checked]; }""")
        ok(r[0] >= 2 and r[1] == 2 and min(r[2]) >= 5 and r[3] == 0 and r[5], f"시험지: 날짜 칸 · A/B형 마지막 쪽에 오답 노트(5줄 이상) · 넘침 없음 {r}")
        n0 = r[4]
        await E("()=>{ const c=document.getElementById('ppNote'); c.checked=false; c.dispatchEvent(new Event('change', {bubbles:true})); }"); await T.wait_for_timeout(1500)
        r = await E("()=>[document.querySelectorAll('#ppWrap .ppNote').length, document.querySelectorAll('#ppWrap .pp:not(.key):not(.rd)').length, (JSON.parse(localStorage.getItem('hyeng_paper'))||{}).note]")
        ok(r[0] == 0 and r[1] == n0 and r[2] is False, f"오답 노트 끄면 사라짐 · 쪽 수 그대로 · 기억 {r}")
        await E("()=>{ Paper.close(); Paper.open({set:'kinder', from:0, to:1, mode:'kw'}); }"); await T.wait_for_timeout(1500)
        r = await E("()=>[...document.querySelectorAll('#ppWrap .kjW b')].filter(b=>b.textContent.length>=10).map(b=>[b.textContent, b.className, b.getClientRects().length, Math.round(b.offsetHeight/parseFloat(getComputedStyle(b).lineHeight))])")
        ok(len(r) > 0 and all(x[1] in ("lg", "xl") and x[3] == 1 for x in r), f"따라쓰기 긴 단어는 작게 한 줄 {r[:3]}")
        await E("()=>Paper.close()")
        # ── 🏫 Cls
        r = await E("""()=>{ const s0=Study.load(); s0.srs=s0.srs||{}; s0.srs.beard=[4, Study.today()+9]; Study.save && Study.save(); Cls.cur=null; Cls.ans('beard', false); Cls.ans('Cheek', false); Cls.ans('vest', true); Cls.ans('beard', false);
          const s=Study.load(), t=Study.today(); return [s.srs.beard, s.srs.cheek, t, Cls.mw(), Cls.cur.ok, Cls.cur.ng, Study.clsN()]; }""")
        ok(r[0][1] == r[2] + 1 and r[0][0] in (2, 3) and r[1] and r[1][1] == r[2] + 1 and r[3] == "beard,Cheek" and r[4] == 1 and r[5] == 3, f"틀린 단어 → 내일 복습(칸은 한 칸씩만 내림) · mw {r}")
        r = await E("()=>{ const c=Cls.take(); return [c.miss, c.n, c.ok, c.ng, Cls.cur]; }"); ok(r[0] == "beard, Cheek" and r[1] == 2 and r[4] is None, f"take → 점수 줄 「틀린 단어」 {r}")
        await E("(R)=>FB.set('/hy/roster', R).then(()=>HyBoss.refresh(true))", ROSTER)
        await E("()=>{ localStorage.removeItem('hyeng_cls_log'); Kid.teacher=()=>true; Cls.bar('battle', '1234', {P:{k1:{n:'민준', ok:6, ng:4, mw:'beard,cheek'}, k2:{n:'서연', ok:8, ng:2, mw:'beard'}, x:{ok:1}}, t0:1}, '사자반'); }"); await T.wait_for_timeout(400)
        r = await E("()=>[document.getElementById('clsBar').innerText.replace(/\\n/g,' | '), Cls.logs().length, Cls.logs()[0]]")
        ok("beard" in r[0] and "×2" in r[0] and "70%" in r[0] and "첫 기록" in r[0] and r[1] == 1 and r[2]["n"] == 2 and r[2]["acc"] == 70 and r[2]["w"][0] == ["beard", 2], f"TV 한 줄: 많이 틀린 단어 · 반 정답률 · 기록 {r[0][:90]}")
        await E("()=>Cls.bar('battle', '1234', {P:{}, t0:1})"); r1 = await E("()=>Cls.logs().length"); ok(r1 == 1, "같은 판은 한 번만 적음")
        await T.wait_for_timeout(30)
        await E("()=>Cls.bar('battle', '1235', {P:{k1:{n:'민준', ok:9, ng:1, mw:'vest'}}, t0:2})"); await T.wait_for_timeout(300)
        r = await E("()=>[document.getElementById('clsBar').innerText, (HyBoss.R||{}).clog ? 1 : 0, Cls.last('battle'), Cls.adminCard()]")
        fb = await E("()=>FB.get('/hy/roster/clog')")
        ok("지난번 70%" in r[0] and "▲20" in r[0] and "지난번" in r[2] and "90%" in r[2] and "배틀" in r[3] and fb and len(fb) == 2, f"지난번 대비 ▲ · 대기 화면 한 줄 · 선생님 기록 · 서버 {len(fb or {})}")
        await T.screenshot(path=os.environ.get("HY_OUT", "/tmp/cls656_") + "bar.png")
        await E("()=>document.querySelector('#clsBar button').click()"); ok(not await E("()=>!!document.getElementById('clsBar')"), "✕ 닫기")
        # ── 배틀 아이: 틀리면 내 줄에 mw
        await E("""()=>{ const w=Study.word('beard'), o=[Study.word('cheek'), Study.word('vest')];
            Battle.role='kid'; Battle.room='9999'; Battle.me='k1'; Battle.pick={id:'k1', n:'민준'}; Battle.h=null; Battle._last={cfg:{set:'elem', from:0, to:2, dur:300, qt:['e2k']}, st:{s:'run', t0:Date.now()-5000}, p:{}};
            Battle.screen(); Battle.q={t:'e2k', w, opts:[w].concat(o)}; Battle.qAt=Date.now()-5000; Battle.lockTo=0; Battle.draw(); Battle.answer(1); }"""); await T.wait_for_timeout(500)
        r = await E("()=>FB.get('/battle/9999/p/k1')"); ok(r and r.get("ng") == 1 and r.get("mw") == "beard", f"배틀: 틀리면 내 줄에 틀린 단어 {r}")
        await E("()=>{ Battle.role=null; Battle.q=null; clearInterval(Battle.t); try{ document.getElementById('scRaid').classList.remove('on'); }catch(e){} Cls.cur=null; }")
        # ── 🏫 한밤의 학교
        ok(await E("()=>Esc.HS.length>=2 && Esc.HS.every(h=>h.Z.length===3 && h.Z.every(z=>z[1].length===3 && z[1].every(r=>r[2].length===5)) && h.R.length===3 && h.FLV.length===3)"), "집 두 채 — 층 3 · 방 3 · 물건 5 씩 같은 틀")
        await E("()=>EscTV.host({set:'elem', from:0, to:5, dur:20, lv:1, mo:0, hv:1})"); await T.wait_for_function("()=>EscTV.room", timeout=8000); room = await E("()=>EscTV.room")
        K = await ctx.new_page(); await K.set_viewport_size({"width": 400, "height": 860}); await boot(K)
        await K.evaluate("(r)=>{ EscPad.join(r, {id:'k1', n:'민준'}); window.confirm=()=>true; }", room); await T.wait_for_timeout(1300)
        lob = await E("()=>document.getElementById('escTV').innerText.slice(0,40)")
        await E("()=>document.querySelector('[data-et=go]').click()"); await T.wait_for_function("()=>EscTV.st && EscTV.st.s==='run'", timeout=10000); await K.wait_for_timeout(1500)
        r = await E("()=>[EscTV.st.hv, EscTV.st.Z[0].H.map(z=>z.R.map(x=>x.nm).join('/')).join(' | ')]"); k = await K.evaluate("()=>[Esc.hv, Esc.HOUSE.nm]")
        ok("한밤의 학교" in lob and r[0] == 1 and "교실" in r[1] and "천문대" in r[1] and k == [1, "한밤의 학교"], f"한밤의 학교: 대기 화면 · 방 이름 · 패드도 같은 집 {lob[:16]} · {r[1][:40]} · {k}")
        await E("()=>EscTV.finish()"); await T.wait_for_timeout(400)
        r = await E("()=>[(document.getElementById('clsBar')||{}).innerText||'', Cls.logs()[0].m, Cls.logs()[0].x]"); ok(r[1] == "esc" and "한밤의 학교" in r[2], f"저택 탈출도 기록 {r[2]}")
        await E("()=>EscTV.stop()"); ok(not await E("()=>!!document.getElementById('clsBar')"), "닫으면 한 줄도 사라짐")
        e = real_errs(errs); ok(not e, "오류 없음 " + str(e[:3])); await b.close()
    print("결과:", "통과" if not bad else "실패 " + str(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
