"""(v356) 사용자: 공용 패드를 반으로 지정 — 「🏫 지금 수업 반」 (선생님이 누르면 모든 공용 패드가 그 반, 3시간 뒤 저절로 풀림)
  ① 선생님 👥 우리 반 맨 위 버튼 → /hy/roster/now {t, until}
  ② 공용 패드: 이름 고르기에 그 반 먼저(v359: 다른 반도 펼친 채로) · 이름 안 골라도 그 반 숙제·시험 · 오늘 한 아이 줄에 그 반
  ③ 개인 기기는 그대로 · 수업 끝 / 시간 지나면 원래대로"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

ROSTER = "()=>FB.set('/hy/roster', {t:{a:{n:'초등반'}, b:{n:'중등반'}}, k:{k1:{n:'민준',t:'a'}, k2:{n:'서연',t:'b'}, k3:{n:'하준',t:'a'}}})"

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={"width": 1180, "height": 820})
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        T = await ctx.new_page(); T.on("pageerror", lambda e: errs.append("T " + str(e))); await boot(T)
        await T.evaluate(ROSTER)
        await T.evaluate("()=>{ sessionStorage.setItem('hyeng_admin_ok',String(Date.now())); sessionStorage.setItem('hyeng_admin_tk','testkey'); }"); await T.reload(); await T.wait_for_timeout(1500)
        await T.evaluate("()=>{ window.confirm=()=>true; Admin.open(); }"); await T.wait_for_timeout(500)
        # (v395) 지금 수업 반 = 🏫 지금 수업 탭 「어느 반 수업?」 (반 고르기가 공용 패드 반까지)
        await T.evaluate("()=>document.querySelector('#adTabs [data-t=\"now\"]').click()"); await T.wait_for_timeout(900)
        r = await T.evaluate("()=>[...document.querySelectorAll('[data-ad=\"nowCls\"]')].map(b=>b.textContent.trim())")
        ok([x.split(" ")[-1] for x in r] == ["전체", "초등반", "중등반"], f"지금 수업 반 버튼 {r}")
        await T.evaluate("()=>document.querySelector('[data-ad=\"nowCls\"][data-c=\"b\"]').click()"); await T.wait_for_timeout(900)
        n = await T.evaluate("()=>FB.get('/hy/roster/now')")
        ok(n and n.get("t") == "b" and n["until"] - n["at"] == 3 * 3600 * 1000, f"서버에 지금 수업 반 {n}")
        r = await T.evaluate("()=>{ const e=document.querySelector('.adClsSub'); return e ? e.innerText : ''; }")
        ok("중등반" in r and "공용 패드" in r, f"선생님 화면 표시 {r}")
        await T.screenshot(path=OUT + "pad356_admin.png")
        # 숙제·시험 — 초등반·중등반 따로
        await T.evaluate("""()=>Promise.all([FB.set('/hy/hw/cur', {ha:{id:'ha', on:1, team:'a', set:'elem', from:0, to:1, goal:3, due:Date.now()+864e5, title:'초등 숙제', at:1}, hb:{id:'hb', on:1, team:'b', set:'mid', from:0, to:1, goal:3, due:Date.now()+864e5, title:'중등 숙제', at:2}}),
            FB.set('/hy/exam/open/ea', {id:'ea', on:1, st:'run', mode:'open', until:Date.now()+36e5, team:'a', set:'elem', from:0, to:2, n:10, title:'초등 시험', at:1}),
            FB.set('/hy/exam/open/eb', {id:'eb', on:1, st:'run', mode:'open', until:Date.now()+36e5, team:'b', set:'mid', from:0, to:2, n:10, title:'중등 시험', at:2})])""")
        # 공용 패드 (이름 안 고름)
        K = await ctx.new_page(); await K.set_viewport_size({"width": 390, "height": 844}); K.on("pageerror", lambda e: errs.append("K " + str(e))); await boot(K)
        await K.evaluate("()=>{ localStorage.setItem('hyeng_nick','한양 행복'); Kid.clear(); return HyBoss.refresh(true); }"); await K.wait_for_timeout(300)
        r = await K.evaluate("()=>[Kid.padT(), Kid.get()]")
        ok(r == ["b", None], f"공용 패드 = 중등반 (이름 안 고름) {r}")
        r = await K.evaluate("()=>HyHW.check(true).then(()=>HyHW.mine() && HyHW.mine().title)")
        ok(r == "중등 숙제", f"이름 안 골라도 중등 숙제 {r}")
        r = await K.evaluate("()=>{ show('scStart'); return HyExam.check(true).then(()=>HyExam.c && HyExam.c.title); }")
        ok(r == "중등 시험", f"이름 안 골라도 중등 시험 {r}")
        r = await K.evaluate("()=>HyDay.who()")
        ok(r and r.get("t") == "b" and "이름 안 고름" in r.get("n", ""), f"오늘 한 아이 줄에 중등반 {r}")
        await K.evaluate("()=>KidPick.open()"); await K.wait_for_timeout(200)
        r = await K.evaluate("()=>{ const d=document.getElementById('kidPick'); const G=[...d.querySelectorAll('.kpL > .kpG')]; return [G.map(g=>g.querySelector('b').innerText.trim()), [...d.querySelectorAll('.kpK')].filter(b=>b.getBoundingClientRect().height>10).map(b=>b.textContent), !!d.querySelector('.kpMore')]; }")
        ok(r[0][0].startswith("🏫 지금 수업") and "중등반" in r[0][0] and sorted(r[1]) == ["민준", "서연", "하준"] and r[1][0] == "서연" and not r[2], f"이름 고르기: 중등반 먼저 · 다른 반도 다 보임 (v359) {r}")
        # (v359) 이름 고르기를 열어 둔 사이 선생님이 아이를 새로 넣으면 바로 보임
        await K.evaluate("()=>KidPick.close()")
        await T.evaluate("()=>FB.update('/hy/roster/k/k9', {n:'임시아이', t:'a'})"); await K.wait_for_timeout(200)
        await K.evaluate("()=>{ delete HyBoss.R.k.k9; HyBoss._p=null; KidPick.open(); window._first=[...document.querySelectorAll('#kidPick .kpK')].map(b=>b.textContent); }"); await K.wait_for_timeout(700)
        ok("임시아이" not in await K.evaluate("()=>window._first"), "(이 패드 명단이 옛것이었음)")
        r = await K.evaluate("()=>[...document.querySelectorAll('#kidPick .kpK')].map(b=>b.textContent)")
        ok("임시아이" in r, f"새로 넣은 아이가 이름 고르기에 바로 {r}")
        await K.screenshot(path=OUT + "pad356_pick.png")
        await K.evaluate("()=>KidPick.close()")
        # 개인 기기는 그대로
        P = await ctx.new_page(); P.on("pageerror", lambda e: errs.append("P " + str(e))); await boot(P)
        await P.evaluate("()=>{ localStorage.setItem('hyeng_nick','민준이'); return HyBoss.refresh(true); }")
        r = await P.evaluate("()=>[Kid.padT(), HyBoss.nowT()]")
        ok(r == [None, "b"], f"개인 기기는 반 지정 안 받음 {r}")
        # 수업 끝
        await T.evaluate("()=>document.querySelector('[data-ad=\"nowCls\"][data-c=\"all\"]').click()"); await T.wait_for_timeout(500)
        r = await K.evaluate("()=>HyBoss.refresh(true).then(()=>[Kid.padT(), HyHW.mine() && HyHW.mine().title])")
        ok(r[0] is None and r[1] is None, f"수업 끝 → 공용 패드 원래대로 (반 숙제 안 보임) {r}")
        # 시간 지나면 저절로
        await T.evaluate("()=>FB.set('/hy/roster/now', {t:'a', at:Date.now()-4*36e5, until:Date.now()-36e5})")
        r = await K.evaluate("()=>HyBoss.refresh(true).then(()=>Kid.padT())")
        ok(r is None, f"3시간 지나면 저절로 풀림 {r}")
        # 명단 다른 기능은 그대로 (반·아이 수)
        r = await T.evaluate("()=>HyBoss.refresh(true).then(()=>{ const K=HyBoss.kids(); return [Object.keys(HyBoss.teams()).length, Object.keys(K).filter(k=>!K[k].nw).length, Object.values(K).filter(x=>x.nw).map(x=>x.n)]; })")
        ok(r[0] == 2 and r[1] == 4 and r[2] in ([], ["민준이"]), f"명단 그대로 (v478: 개인 기기 「민준이」는 🆕 로 스스로 들어갈 수 있음) {r}")
        e = real_errs(errs); ok(not e, "오류 없음 " + str(e[:3]))
        await br.close()
    print("결과:", "통과" if not bad else "실패 " + str(bad))
asyncio.run(main())
