"""(v364) 사용자: 상점 한정 이벤트 「빼빼로」 — 보석 500 · 한 사람 1번 · 산 아이가 관리자 화면에 (달란트 시장처럼)
  ① 상점 맨 위 🎁 진짜 상품 · 공용 패드는 먼저 이름 고르기 · 사면 💎-500 · 서버 /hy/roster/pz/pepero/<아이>
  ② 같은 아이는 다른 기기에서도 다시 못 삼 · 다른 아이는 삼 · 보석 모자라면 안 됨
  ③ 선생님 🏠 홈: 산 아이 목록 · 「줬어요」 체크 · 판매 멈추기 → 아이 상점에서 사라짐"""
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
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={"width": 390, "height": 844}); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        K = await ctx.new_page(); K.on("pageerror", lambda e: errs.append("K " + str(e))); await boot(K)
        await K.evaluate("()=>FB.set('/hy/roster', {t:{a:{n:'고학년', e:'🐸'}}, k:{k1:{n:'라언', t:'a'}, k2:{n:'단우', t:'a'}}}).then(()=>{ localStorage.setItem('hyeng_nick','한양 행복'); Kid.clear(); Kid.setOwner({id:'k1', n:'라언', t:'a'}); Wallet.adjust(1200, 'test'); return HyBoss.refresh(true); })")
        await K.evaluate("()=>ShopUI.open()"); await K.wait_for_timeout(500)
        r = await K.evaluate("()=>{ const b=document.getElementById('shopPrize'); return [b.style.display, b.innerText.indexOf('빼빼로')>=0, !!b.querySelector('[data-act=\"pzarm\"]')]; }")
        ok(r == ["block", True, True], f"상점 맨 위 진짜 상품 빼빼로 {r}")
        await K.screenshot(path=OUT + "prize364_shop.png")
        # (v417) 🧸 주인 패드(라언)는 이름을 안 골라도 라언 · 수업 모드(다른 아이)는 진짜 상품 못 삼
        await K.evaluate("()=>{ Kid.set({id:'k2', n:'단우', t:'a', pk:Date.now()}); ShopUI.draw(); document.querySelector('[data-act=\"pzarm\"]').click(); }"); await K.wait_for_timeout(200)
        ok(await K.evaluate("()=>/내 패드/.test(document.getElementById('shopMsg').textContent)"), "공용 패드 수업 모드(단우)는 진짜 상품 못 삼 (내 패드에서)")
        await K.evaluate("()=>{ Kid.clear(); ShopUI.draw(); }"); await K.wait_for_timeout(200)
        g0 = await K.evaluate("()=>Wallet.gems()")
        await K.evaluate("()=>document.querySelector('[data-act=\"pzarm\"]').click()"); await K.wait_for_timeout(200)
        await K.evaluate("()=>document.querySelector('[data-act=\"pzbuy\"]').click()"); await K.wait_for_timeout(600)
        r = await K.evaluate("()=>[Wallet.gems(), document.getElementById('shopMsg').textContent, document.getElementById('shopPrize').innerText.indexOf('샀어요')>=0]")
        ok(r[0] == g0 - 500 and "빼빼로" in r[1] and r[2], f"라언이 삼: 💎-500 · 「샀어요」 {r}")
        d = await K.evaluate("()=>FB.get('/hy/roster/pz/pepero')")
        ok(d and d.get("k1", {}).get("n") == "라언", f"서버에 산 기록 {d}")
        # 같은 아이 · 다른 기기 → 못 삼
        P = await ctx.new_page(); P.on("pageerror", lambda e: errs.append("P " + str(e))); await boot(P)
        await P.evaluate("()=>{ localStorage.setItem('hyeng_nick','한양 배려'); Wallet.adjust(1000,'t'); Kid.set({id:'k1', n:'라언', t:'a'}); return HyBoss.refresh(true); }")
        await P.evaluate("()=>{ ShopUI.open(); }"); await P.wait_for_timeout(500)
        r = await P.evaluate("()=>[!!document.querySelector('[data-act=\"pzarm\"]'), document.getElementById('shopPrize').innerText.indexOf('샀어요')>=0]")
        ok(r == [False, True], f"같은 아이는 다른 기기에서도 「샀어요」 {r}")
        # 다른 기기 메모리에 옛 명단이 있어도 서버 한 번 쓰기로 막힘
        r = await P.evaluate("()=>{ delete HyBoss.R.pz; Prize.arm='pepero'; const g=Wallet.gems(); Prize.act('pzbuy','pepero'); return new Promise(res=>setTimeout(()=>res([g, Wallet.gems(), document.getElementById('shopMsg').textContent]), 500)); }")
        ok(r[0] == r[1] and "이미" in r[2], f"서버가 두 번째 사기를 막음 (보석 안 빠짐) {r}")
        # 다른 아이(단우)는 삼 · 보석 모자라면 안 됨
        r = await P.evaluate("()=>{ Kid.setOwner({id:'k2', n:'단우', t:'a'}); Kid.set({id:'k2', n:'단우', t:'a'}); Wallet.adjust(-Wallet.gems()+100,'t'); ShopUI.draw(); Prize.act('pzarm','pepero'); return [Wallet.gems(), document.getElementById('shopMsg').textContent]; }")
        ok(r[0] == 100 and "더 필요" in r[1], f"보석 모자라면 안 됨 {r}")
        # 선생님 홈
        T = await ctx.new_page(); T.on("pageerror", lambda e: errs.append("T " + str(e))); await boot(T)
        await T.evaluate("()=>{ sessionStorage.setItem('hyeng_admin_ok',String(Date.now())); sessionStorage.setItem('hyeng_admin_tk','testkey'); }"); await T.reload(); await T.wait_for_timeout(1500)
        await T.evaluate("()=>{ window.confirm=()=>true; Admin.open(); Admin._tab('class'); }"); await T.wait_for_timeout(1200)   # (v392) 진짜 상품 = 👥 아이들
        r = await T.evaluate("()=>{ const c=document.getElementById('adPrize'); return c ? c.innerText.replace(/\\s+/g,' ') : ''; }")
        ok("빼빼로 산 아이 1명" in r and "라언" in r and "줘야 할 아이 1명" in r, f"선생님 홈: 산 아이 {r[:80]}")
        await T.screenshot(path=OUT + "prize364_admin.png", full_page=False)
        await T.evaluate("()=>document.querySelector('[data-ad=\"pzGive\"]').click()"); await T.wait_for_timeout(500)
        r = await T.evaluate("()=>FB.get('/hy/roster/pz/pepero/k1').then(x=>x && x.g)")
        ok(r == 1, f"줬어요 체크 {r}")
        await T.evaluate("()=>document.querySelector('[data-ad=\"pzOff\"]').click()"); await T.wait_for_timeout(500)
        r = await K.evaluate("()=>HyBoss.refresh(true).then(()=>{ ShopUI.draw(); return document.getElementById('shopPrize').style.display; })")
        ok(r == "none", f"판매 멈추면 아이 상점에서 사라짐 {r}")
        e = real_errs(errs); ok(not e, "오류 없음 " + str(e[:3]))
        await br.close()
    print("결과:", "통과" if not bad else "실패 " + str(bad))
asyncio.run(main())
