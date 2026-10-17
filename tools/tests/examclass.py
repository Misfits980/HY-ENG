"""(v330) 📝 시험 반마다 따로 · 🧒 각자 배운 단어 · 📅 오늘 한 아이
   반 A 시험(G3-4 범위) · 반 B 시험(각자 배운 단어)을 동시에 → A 아이는 A 시험만, B 아이는 B 시험만 · B 아이 단어 = 자기 Daily 30 책에서 배운 단어
   달리기·공부 판이 끝나면 /hy/day/<날짜>/<아이> → 선생님 📋 우리 반 맨 위 '📅 오늘 한 아이' (시트 없어도)"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

ROSTER = "()=>FB.set('/hy/roster', {t:{a:{n:'초등반'}, b:{n:'중등반'}}, k:{k1:{n:'민준',t:'a'}, k2:{n:'서연',t:'b'}}})"

async def kid(ctx, errs, k, n, t):
    pg = await ctx.new_page(); await pg.set_viewport_size({"width": 390, "height": 844})
    pg.on("pageerror", lambda e: errs.append(n + " " + str(e))); await boot(pg)
    await pg.evaluate(f"()=>{{ localStorage.setItem('hyeng_nick','한양패드'); window.confirm=()=>true; Kid.set({{id:'{k}',n:'{n}',t:'{t}'}}); show('scStart'); return HyBoss.refresh(true); }}")
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
        await T.evaluate(ROSTER); await T.evaluate("()=>{ window.confirm=()=>true; return HyBoss.refresh(true); }")
        A = await kid(ctx, errs, "k1", "민준", "a"); B = await kid(ctx, errs, "k2", "서연", "b")
        # 서연: 중등 단어 몇 Stage 배움 (각자 배운 단어용)
        await B.evaluate("()=>{ const s=Study.load(); s.set='mid'; s.book='mid'; const L=Study.lessons('mid'); const ws=[].concat(...L.slice(0,4).map(x=>x.ws)); ws.forEach((w,i)=>{ s.seen[w.en]=1; s.sd=s.sd||{}; s.sd[w.en]=Study.today()-(i<10?0:3); }); Study.save(); }")
        # 선생님 — 반 A: G3-4 시험 · 반 B: 각자 배운 단어
        await T.evaluate("()=>{ Admin.open(); }"); await T.wait_for_timeout(400)
        await T.evaluate("()=>document.querySelector('#adTabs [data-t=\"exam\"]').click()"); await T.wait_for_timeout(700)
        opts = await T.evaluate("()=>[...document.querySelectorAll('#adExTeam option')].map(o=>o.textContent)")
        ok(any("초등반" in o for o in opts) and any("중등반" in o for o in opts), f"반 고르기 {opts}")
        await T.evaluate("()=>{ const t=document.getElementById('adExTeam'); t.value='a'; t.dispatchEvent(new Event('change')); const s=document.getElementById('adExSet'); s.value='elem'; s.dispatchEvent(new Event('change')); document.getElementById('adExN').value='20'; document.getElementById('adExMode').value='open'; document.getElementById('adExMode').dispatchEvent(new Event('change')); }")
        await T.evaluate("()=>document.querySelector('[data-ad=\"exOpen\"]').click()"); await T.wait_for_timeout(600)
        await T.evaluate("()=>{ const t=document.getElementById('adExTeam'); t.value='b'; const r=document.getElementById('adExRng'); r.value='mine'; r.dispatchEvent(new Event('change')); document.getElementById('adExN').value='20'; document.getElementById('adExMode').value='open'; document.getElementById('adExMode').dispatchEvent(new Event('change')); }")
        info = await T.evaluate("()=>document.getElementById('adExInfo').textContent")
        ok("각자" in info or "아이마다" in info, f"각자 배운 단어 안내 {info[:50]!r}")
        await T.evaluate("()=>document.querySelector('[data-ad=\"exOpen\"]').click()"); await T.wait_for_timeout(600)
        O = await T.evaluate("()=>FB.get('/hy/exam/open').then(O=>Object.values(O||{}).map(c=>[c.team, c.rng, c.title, c.st]))")
        print("open", O)
        ok(len(O) == 2 and {o[0] for o in O} == {"a", "b"}, "시험 두 개 동시에 (반마다)")
        await T.screenshot(path=OUT + "examclass_admin.png")
        cards = await T.evaluate("()=>document.querySelectorAll('.exCur').length")
        ok(cards == 2, f"관리 화면에 열린 시험 카드 {cards}개")
        # 아이 — 자기 반 시험만
        ra = await A.evaluate("()=>HyExam.check(true).then(()=>HyExam.c && HyExam.c.team)")
        rb = await B.evaluate("()=>HyExam.check(true).then(()=>HyExam.c && [HyExam.c.team, HyExam.c.rng])")
        ok(ra == "a" and rb == ["b", "mine"], f"민준 = 초등반 시험 {ra} · 서연 = 중등반 각자 시험 {rb}")
        # 서연 시작 → 자기 배운 단어 (중등 단어)
        await B.evaluate("()=>{ const a=document.getElementById('exAsk'); if(a) a.remove(); HyExam.go(); }"); await B.wait_for_timeout(3500)
        q = await B.evaluate("()=>{ const U=StudyUI, Q=U.qs.filter(q=>q.t!=='intro'), s=Study.load(), mid={}; Study.lessons('mid').slice(0,4).forEach(x=>x.ws.forEach(w=>mid[w.en]=1)); return {ex:!!U.ex, set:U.set, n:Q.length, inMid:Q.every(q=>mid[q.w.en]), P:U.qs[0].P}; }")
        print("seoyeon", q)
        ok(q["ex"] and q["set"] == "mid" and q["n"] == 20 and q["inMid"], "서연 시험 = 자기가 배운 중등 단어 20개")
        r = await T.evaluate("()=>FB.get('/hy/exam/open').then(O=>{ const id=Object.values(O).find(c=>c.team==='b').id; return FB.get('/hy/exam/res/'+id+'/k2'); })")
        ok(r and r.get("bk") and r.get("tot") == 20, f"결과 칸에 아이 책 {r and r.get('bk')}")
        # 배운 단어가 적은 아이는 못 봄
        await B.evaluate("()=>{ StudyUI.path(); const s=Study.load(); s.seen={}; Study.save(); localStorage.clear; }")
        await B.evaluate("()=>FB.set('/hy/exam/res/'+HyExam.c.id+'/k2', null)")
        await B.evaluate("()=>{ window._t=''; const o=hyToast; window.hyToast=(m)=>{ window._t=m; }; HyExam.go(); }"); await B.wait_for_timeout(800)
        ok("적어요" in await B.evaluate("()=>window._t"), "배운 단어가 적으면 '먼저 Daily 30'")
        # 📅 오늘 한 아이 — 달리기 · 공부
        await A.evaluate("()=>{ G.score=1234; G.stage=7; G.right=12; G.wrong=3; G.runStart=Date.now()-90000; G.pauseMs=0; G.testRun=false; HyDay.add({r:1, rr:12, rw:3, rs:90}, {b:1234, bs:7}); HyDay.add({r:1, rr:5, rw:5, rs:40}, {b:800, bs:3}); HyDay.add({s:1, so:10, sw:1}); }")
        await A.wait_for_timeout(300)
        d = await T.evaluate("()=>FB.get('/hy/day/'+HyDay.key()+'/k1')")
        ok(d and d["r"] == 2 and d["rr"] == 17 and d["b"] == 1234 and d["s"] == 1 and d["n"] == "민준", f"하루 칸 {d}")
        await T.evaluate("()=>document.querySelector('#adTabs [data-t=\"class\"]').click()"); await T.wait_for_timeout(1200)
        card = await T.evaluate("()=>{ const c=[...document.querySelectorAll('.adCard')].find(x=>/한 아이/.test(x.innerText)); return c ? c.innerText : ''; }")
        print("day", card.replace("\n", " / ")[:200])
        ok("민준" in card and "2판" in card and "1,234" in card and "달리기 1명" in card, "📋 우리 반 맨 위 '📅 오늘 한 아이'")
        await T.screenshot(path=OUT + "day_card.png")
        await T.evaluate("()=>document.querySelector('[data-ad=\"dayPick\"]:nth-child(2)').click()"); await T.wait_for_timeout(500)
        ok("어제" in await T.evaluate("()=>[...document.querySelectorAll('.adCard h3')].map(h=>h.innerText).join(' ')"), "어제 보기")
        ok(not errs, "오류 없음 " + str(errs[:3]))
        await br.close()
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)

asyncio.run(main())
