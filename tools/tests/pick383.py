"""(v383) 사용자: 공용 패드라 이름 고르기를 많이 씀 → 수업 입장 창 안에서 반을 누르면 그 반 아이 이름이 나오고, 이름을 누르면 고름
  · 공용 패드(한양…/…패드)는 지난 아이 이름을 미리 고르지 않음 · 개인 기기는 내 반이 먼저 열리고 내 이름이 골라져 있음
  · 이름 고른 뒤 방 번호 4자리 → 바로 들어감 (번호 먼저 넣고 이름을 눌러도 바로)"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright
ROSTER = "{t:{a:{n:'사자반',e:'🦁'},b:{n:'돌고래반',e:'🐬'}},k:{k1:{n:'민준',t:'a'},k2:{n:'서연',t:'a'},k4:{n:'지우',t:'a'},k3:{n:'하준',t:'b'},k5:{n:'유나',t:'b'}}}"

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={"width": 1024, "height": 768})
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        T = await ctx.new_page(); T.on("pageerror", lambda e: errs.append("T " + str(e))); await boot(T)
        await T.evaluate("()=>FB.set('/hy/roster'," + ROSTER + ")"); await T.wait_for_timeout(300)
        room = await T.evaluate("()=>Battle.host({set:'g56', from:0, to:2, dur:180, mode:'score', lvl:'easy', qt:['mean'], lbl:'t'}, '5678')")
        # 공용 패드
        k = await ctx.new_page(); k.on("pageerror", lambda e: errs.append("K " + str(e))); await k.set_viewport_size({"width": 390, "height": 844}); await boot(k)
        await k.evaluate("()=>{ localStorage.setItem('hyeng_nick','한양패드'); Kid.set({id:'k1', n:'민준', t:'a', pk:Date.now()}); return HyBoss.refresh(true); }"); await k.wait_for_timeout(300)
        await k.evaluate("()=>RaidJoin.open()"); await k.wait_for_timeout(600)
        r = await k.evaluate("()=>({cls:[...document.querySelectorAll('.rjC')].map(b=>b.innerText), on:(document.querySelector('.rjC.on')||{}).innerText, kids:[...document.querySelectorAll('.rjN')].map(b=>b.innerText), sel:document.querySelectorAll('.rjN.on').length, name:!!document.getElementById('rdNameIn')})")
        print(r)
        ok(len(r["cls"]) == 2 and r["kids"] == ["민준", "서연", "지우"] and r["sel"] == 0 and not r["name"], f"공용 패드: 반 칩 · 첫 반 이름 · 미리 고른 이름 없음 {r}")
        await k.evaluate("()=>document.querySelectorAll('.rjC')[1].click()"); await k.wait_for_timeout(150)
        r = await k.evaluate("()=>[...document.querySelectorAll('.rjN')].map(b=>b.innerText)")
        ok(r == ["유나", "하준"], f"반 누르면 그 반 이름 {r}")
        await k.screenshot(path=OUT + "pick383.png")
        r = await k.evaluate("()=>{ for(const d of '5678') document.querySelector('[data-rjk=\"'+d+'\"]').click(); return [Battle.role, document.getElementById('rdJoinMsg').innerText]; }")
        ok(r[0] != "kid", f"이름 없이 번호만이면 안 들어감 {r}")
        await k.evaluate("()=>[...document.querySelectorAll('.rjN')].find(b=>b.innerText==='하준').click()"); await k.wait_for_timeout(1200)
        r = await k.evaluate("()=>[Battle.role, Battle.me, (Battle.pick||{}).n, Kid.get().n]")
        ok(r == ["kid", "k3", "하준", "하준"], f"번호 먼저 → 이름 누르면 바로 들어감 {r}")
        # 개인 기기
        k2 = await ctx.new_page(); k2.on("pageerror", lambda e: errs.append("K2 " + str(e))); await k2.set_viewport_size({"width": 390, "height": 844}); await boot(k2)
        await k2.evaluate("()=>{ localStorage.setItem('hyeng_nick','yuna'); Kid.set({id:'k5', n:'유나', t:'b', pk:Date.now()}); return HyBoss.refresh(true); }"); await k2.wait_for_timeout(300)
        await k2.evaluate("()=>RaidJoin.open()"); await k2.wait_for_timeout(500)
        r = await k2.evaluate("()=>[document.querySelectorAll('.rjN').length, document.getElementById('rdJoin') ? document.getElementById('rdJoin').innerText : '']")
        ok(r[0] == 0 and "내 기기" in r[1], f"(v478) 개인 기기: 이름 고르기 없이 「내 기기」 {r[0]} {r[1][:60]!r}")
        await k2.evaluate("()=>{ for(const d of '5678') document.querySelector('[data-rjk=\"'+d+'\"]').click(); }"); await k2.wait_for_timeout(1200)
        r = await k2.evaluate("()=>[Battle.role, Battle.me]")
        ok(r == ["kid", "k5"], f"번호 4자리면 바로 들어감 {r}")
        e = real_errs(errs); ok(not e, "오류 없음 " + str(e[:3]))
        await br.close()
    print("결과:", "통과" if not bad else "실패 " + str(bad))
asyncio.run(main())
