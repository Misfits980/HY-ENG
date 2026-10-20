"""(v361) 사용자: 「➕ 반·아이 넣기」 게임 이름 목록에 구글 시트 아이들이 많이 없음
  → 시트 여러 탭(주간 체크·주간 리포트·오늘의 30·진도표·기기별 이름) 이름을 모두 모음 · 👤 뗌 · 공용 패드·PLAYER·플레이어 N 뺌 · 겹치지 않게"""
import asyncio, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

REP = {"at": 0, "d": {
    "week": [["아이", "월", "화"], ["단우", "❌", "✅ 2"], ["라언", "❌", "✅ 2"], ["빈", "✅ 1", "❌"], ["플레이어 1", "❌", "❌"], ["🏫 한양 행복", "✅", "✅"], ["한양 정직", "✅ 1", "❌"], ["루아", "❌", "❌"]],
    "weekly": [["아이", "들어온 날"], ["주호", "1"], ["경훈", "2"], ["김지후", "3"]],
    "today": [], "prog": [["아이", "책"], ["서연", "G3-4"]],
    "nicks": ["👤김지후", "👤SEOWON", "김지후", "PLAYER", "영어선생님패드", "👤한양 나눔", "스트로베리"]}}

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={"width": 820, "height": 1180}); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        T = await ctx.new_page(); T.on("pageerror", lambda e: errs.append(str(e))); await boot(T)
        await T.evaluate("(r)=>{ r.at=Date.now(); localStorage.setItem('hyeng_admin_rep', JSON.stringify(r)); sessionStorage.setItem('hyeng_admin_ok',String(Date.now())); sessionStorage.setItem('hyeng_admin_tk','testkey'); }", REP)
        await T.reload(); await T.wait_for_timeout(1500)
        await T.evaluate("()=>FB.set('/hy/roster', {t:{a:{n:'고학년'}}, k:{k1:{n:'단우', t:'a'}}}).then(()=>HyBoss.refresh(true))")
        await T.evaluate("()=>{ window.confirm=()=>true; Admin.open(); }"); await T.wait_for_timeout(400)
        await T.evaluate("()=>document.querySelector('#adTabs [data-t=\"class\"]').click()"); await T.wait_for_timeout(800)
        await T.evaluate("()=>{ const d=document.getElementById('adTmAdd'); if(d) d.open=true; }"); await T.wait_for_timeout(300)
        r = await T.evaluate("()=>[...document.querySelectorAll('#adTmNicks .adKid')].map(b=>b.dataset.n)")
        print(r)
        need = ["단우", "라언", "빈", "루아", "주호", "경훈", "김지후", "서연", "SEOWON", "스트로베리"]
        ok(all(n in r for n in need), f"시트 여러 탭의 아이가 모두 {[n for n in need if n not in r]}")
        ok(not any(x for x in r if x.startswith("👤") or x.startswith("🏫") or x.startswith("플레이어") or x == "PLAYER" or x.startswith("한양") or x.endswith("패드")), f"👤·공용 패드·PLAYER 없음 {r}")
        ok(len(r) == len(set(x.lower() for x in r)), "겹치는 이름 없음")
        r2 = await T.evaluate("()=>{ const b=[...document.querySelectorAll('#adTmNicks .adKid')].find(b=>b.dataset.n==='단우'); return b && b.classList.contains('in'); }")
        ok(r2, "이미 명단에 있는 아이(단우)는 흐리게")
        e = real_errs(errs); ok(not e, "오류 없음 " + str(e[:3]))
        await br.close()
    print("결과:", "통과" if not bad else "실패 " + str(bad))
asyncio.run(main())
