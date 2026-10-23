"""(v365) 사용자 사진: 이름 고르기에 같은 아이가 두 번 (👤단우 · 단우 …) · 「반 없음」을 못 지움
  ① 이름 고르기: 👤 떼고 · 반 있는 아이와 이름 같은 「반 없음」 아이는 안 보임
  ② 선생님 👥 우리 반: 「⚠️ 같은 아이가 두 번」 → 🧹 정리하기 (두 번 누르기) · 되돌리기 · 「반 없음 모두 빼기」
  ③ 반·아이 넣기에서 👤 붙은 이름은 떼고 · 같은 아이로 봄"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

ROSTER = """()=>FB.set('/hy/roster', {t:{a:{n:'6세', e:'🦁'}, b:{n:'3시 영어'}}, k:{
  k1:{n:'👤단우', t:'a'}, k2:{n:'👤라언', t:'a'}, k3:{n:'경훈', t:'a'}, k4:{n:'👤SEOWON', t:'b'}, k5:{n:'김지환', t:'b'},
  x1:{n:'단우'}, x2:{n:'라언', t:'gone'}, x3:{n:'SEOWON'}, x4:{n:'한양 정직'}, x5:{n:'김지후'}, k6:{n:'👤패트와 매트(패', t:'b'}, x6:{n:'패트와 매트(패트)'}}})"""

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={"width": 820, "height": 1180}); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        K = await ctx.new_page(); K.on("pageerror", lambda e: errs.append("K " + str(e))); await boot(K)
        await K.evaluate(ROSTER); await K.evaluate("()=>{ localStorage.setItem('hyeng_nick','한양 행복'); return HyBoss.refresh(true); }")
        await K.evaluate("()=>KidPick.open()"); await K.wait_for_timeout(300)
        r = await K.evaluate("()=>[...document.querySelectorAll('#kidPick .kpK')].map(b=>b.textContent)")
        ok(sorted(r) == sorted(["단우", "라언", "경훈", "SEOWON", "김지환", "한양 정직", "김지후", "패트와 매트(패"]) and not any("👤" in x for x in r), f"이름 고르기: 겹침·👤 없음 {r}")
        await K.evaluate("()=>document.querySelector('#kidPick [data-kp=\"k1\"]').click()"); await K.wait_for_timeout(200)
        ok(await K.evaluate("()=>Kid.get().n") == "단우", "고른 이름은 👤 없이")
        T = await ctx.new_page(); T.on("pageerror", lambda e: errs.append("T " + str(e))); await boot(T)
        await T.evaluate("()=>{ sessionStorage.setItem('hyeng_admin_ok',String(Date.now())); sessionStorage.setItem('hyeng_admin_tk','testkey'); }"); await T.reload(); await T.wait_for_timeout(1500)
        await T.evaluate("()=>{ window.confirm=()=>true; Admin.open(); }"); await T.wait_for_timeout(400)
        await T.evaluate("()=>document.querySelector('#adTabs [data-t=\"class\"]').click()"); await T.wait_for_timeout(900)
        r = await T.evaluate("()=>{ const b=[...document.querySelectorAll('#adTmList .dyWarn')].find(x=>/두 번/.test(x.innerText)); return b ? b.innerText : ''; }")   # (v387) 위에 📱 패드 이름 안내가 먼저 나올 수 있음
        ok("두 번" in r and "8명" in r, f"맨 위 안내 {r[:40]}")
        await T.screenshot(path=OUT + "dup365_admin.png")
        CL = "()=>document.querySelector('[data-ad=\"rsClean\"]').click()"
        await T.evaluate(CL); await T.wait_for_timeout(300)
        n1 = await T.evaluate("()=>FB.get('/hy/roster/k').then(K=>Object.keys(K).length)")
        ok(n1 == 12, "한 번 누름: 그대로")
        await T.evaluate(CL); await T.wait_for_timeout(600)
        k = await T.evaluate("()=>FB.get('/hy/roster/k')")
        names = sorted((v["n"], v.get("t")) for v in k.values())
        print(names)
        ok(sorted(k.keys()) == ["k1", "k2", "k3", "k4", "k5", "k6", "x4", "x5"] and k["k6"]["n"] == "패트와 매트(패트)" and all(not v["n"].startswith("👤") for v in k.values()), f"정리: 반 없는 겹침 빼고 · 👤 뗌 {names}")
        ok(k["k1"]["n"] == "단우" and k["k1"]["t"] == "a", "반 있는 쪽이 남음 (6세 단우)")
        await T.evaluate("()=>document.querySelector('#adMsg [data-ad=\"undo\"]').click()"); await T.wait_for_timeout(500)
        ok(await T.evaluate("()=>FB.get('/hy/roster/k').then(K=>Object.keys(K).length)") == 12, "되돌리기")
        await T.wait_for_timeout(600)
        NA = "()=>document.querySelector('[data-ad=\"nocAll\"]').click()"
        await T.evaluate(NA); await T.wait_for_timeout(200); await T.evaluate(NA); await T.wait_for_timeout(600)
        k = await T.evaluate("()=>FB.get('/hy/roster/k')")
        ok(sorted(k.keys()) == ["k1", "k2", "k3", "k4", "k5", "k6"], f"반 없음 모두 빼기 {sorted(k.keys())}")
        # 반·아이 넣기: 👤 붙은 이름은 같은 아이로
        await T.evaluate("()=>{ const d=document.getElementById('adTmAdd'); if(d) d.open=true; const s=document.getElementById('adTmTo'); if(s){ s.value='b'; s.dispatchEvent(new Event('change')); } }")
        await T.evaluate("()=>{ const ta=document.getElementById('adTmMany'); ta.value='👤경훈, 새친구'; document.querySelector('[data-ad=\"tmMany\"]').click(); }"); await T.wait_for_timeout(500)
        k = await T.evaluate("()=>FB.get('/hy/roster/k')")
        ns = sorted(v["n"] for v in k.values())
        ok(ns.count("경훈") == 1 and "새친구" in ns and "👤경훈" not in ns and "👤새친구" not in ns and k["k3"]["t"] == "b", f"👤경훈 = 경훈 (옮김) · 새친구 넣음 {ns}")
        e = real_errs(errs); ok(not e, "오류 없음 " + str(e[:3]))
        await br.close()
    print("결과:", "통과" if not bad else "실패 " + str(bad))
asyncio.run(main())
