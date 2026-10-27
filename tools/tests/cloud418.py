"""(v418) ☁️ 아이 기록 서버 백업 — 자기 기기는 바뀌면 /hy/acct/<아이> 에 저장 · 새 기기(빈 기기)에서 그 아이가 되면 「예전 기록 가져올까요?」
  · 같은 기록이면 다시 안 올림 · 수업 모드(공용 패드 다른 아이)는 안 올림 · 🧸 주인 패드는 주인 것만"""
import asyncio, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch()
        async def dev(nick, fb=None, name="?"):
            ctx = await br.new_context(viewport={"width": 390, "height": 844}, service_workers="block")
            init = "window.HY_FB_LOCAL=true; try{ if(!localStorage.getItem('hyeng_t0')){ localStorage.clear(); localStorage.setItem('hyeng_t0','1'); localStorage.setItem('hyeng_nick', %s); %s } }catch(e){}" % (json.dumps(nick), ("localStorage.setItem('hyeng_fb_local', %s);" % json.dumps(fb)) if fb else "")
            await ctx.add_init_script(init)
            pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(name + ": " + str(e))); await boot(pg); return pg
        A = await dev("민준", name="A")
        E = A.evaluate
        await E("()=>FB.set('/hy/roster',{t:{a1:{n:'A1',e:'🍎'}}, k:{k1:{n:'루아',t:'a1'}, k2:{n:'민준',t:'a1'}}}).then(()=>HyBoss.refresh(true))")
        r = await E("()=>[(Kid.me()||{}).id, Cloud.empty()]")
        ok(r == ["k2", True], f"민준 기기 · 처음엔 빈 기기 {r}")
        await E("()=>{ Wallet.addGems(33,'t'); Study.setLv('basic',1,3); Study.setLv('basic',2,1); localStorage.setItem('hyeng_proto_gems','12'); }")
        r = await E("()=>Cloud.save().then(ok=>[ok, FB.get('/hy/acct/k2')]).then(async ([ok,p])=>[ok, await p])")
        ok(r[0] and r[1]["sm"]["g"] == 33 and r[1]["sm"]["st"] == 2 and r[1]["n"] == "민준", f"☁️ 서버에 저장 (💎33 · Stage 2) {r[1] and r[1].get('sm')}")
        ok(await E("()=>Cloud.save()") is False, "바뀐 게 없으면 다시 안 올림")
        await E("()=>Wallet.addGems(1,'t')")
        ok(await E("()=>Cloud.save()") is True, "바뀌면 올림")
        fb = await E("()=>localStorage.getItem('hyeng_fb_local')")
        # 새 기기 (빈 기기) — 같은 이름
        B = await dev("민준", fb, "B")
        await B.evaluate("()=>HyBoss.refresh(true)")
        await B.evaluate("()=>{ Move.noReload=true; return Cloud.check(); }"); await B.wait_for_timeout(400)
        r = await B.evaluate("()=>[!!document.getElementById('moveAsk'), (document.getElementById('moveAsk')||{}).innerText||'']")
        ok(r[0] and "예전 기록" in r[1] and "34" in r[1], f"새 기기: 「☁️ 민준 예전 기록 · 💎34」 {r[1][:60]!r}")
        await B.screenshot(path=OUT + "cloud418_ask.png")
        await B.evaluate("()=>document.querySelector('#moveAsk [data-mv=y]').click()"); await B.wait_for_timeout(400)
        r = await B.evaluate("()=>[JSON.parse(localStorage.getItem('hyeng_wallet_v1')).gems, JSON.parse(localStorage.getItem('hyeng_study_v1')).lv, localStorage.getItem('hyeng_proto_gems'), localStorage.getItem('hyeng_nick')]")
        ok(r[0] == 34 and len([k for k, v in r[1].items() if v > 0]) == 2 and r[2] == "12" and r[3] == "민준", f"가져옴: 💎34 · 별 · My Town · 이름 그대로 {r[0]}, {r[2]}, {r[3]}")
        # 아니요 → 다시 안 물음
        C = await dev("민준", fb, "C")
        await C.evaluate("()=>HyBoss.refresh(true)")
        await C.evaluate("()=>Cloud.check()"); await C.wait_for_timeout(300)
        await C.evaluate("()=>document.querySelector('#moveAsk [data-mv=n]').click()")
        await C.evaluate("()=>Cloud.check()"); await C.wait_for_timeout(300)
        ok(await C.evaluate("()=>!document.getElementById('moveAsk')"), "「아니요」면 다시 안 물음")
        # 공용 패드: 수업 모드는 안 올림 · 주인은 주인 것만
        D = await dev("한양 행복 패드", fb, "D")
        await D.evaluate("()=>HyBoss.refresh(true)")
        r = await D.evaluate("()=>{ Kid.setOwner({id:'k1', n:'루아'}); Kid.set({id:'k2', n:'민준', t:'a1', pk:Date.now()}); return [Cloud.who(), Kid.guest() && Kid.guest().id]; }")
        ok(r[0] is None and r[1] == "k2", f"수업 모드(민준) = 안 올림 {r}")
        r = await D.evaluate("""()=>{ Kid.set({id:'k1', n:'루아', t:'a1', pk:Date.now()}); Wallet.addGems(5,'t'); localStorage.setItem('hyeng_dm_k1','{"n":1}'); localStorage.setItem('hyeng_wallet_v1@k2','{"gems":9}');
            return Cloud.save(true).then(()=>FB.get('/hy/acct/k1')).then(v=>{ const d=JSON.parse(v.d).data; return [v.sm.g, Object.keys(d).some(k=>k.indexOf('@k2')>=0), 'hyeng_dm_k1' in d]; }); }""")
        ok(r == [5, False, True], f"🧸 주인 패드 = 루아 것만 올림 (민준 수업 칸 빼고) {r}")
        ok(not errs, "오류 없음 " + str(errs[:3]))
        await br.close()
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)

asyncio.run(main())
