"""(v417) 🧸 패드 주인 · 🎁 수업 보석 배달 · 🎓 졸업 — 사용자: "유치부는 자기 패드가 없어(루아·주호·단우·경훈·라언) · 늘 자기 패드 · 보석은 우리 애들이 썼으면 · 졸업하면?"
  A (공용 패드 「한양 배려 패드」, 주인 = 루아): 주인 = 내 기기처럼 · 민준(수업 모드) = 진도·보석·도감 따로 + 서버로 · 상점·이름 바꾸기 막음 · 시트 own/dex
  B (민준 기기): 켜면 📦 수업에서 받은 것 (💎·⭐·📖)
  A → 🎓 졸업: 루아 기록을 서버에 맡기고 패드 비움 · C (루아 새 기기): 「가져올까요?」 → 💎·공부·My Town 그대로"""
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
        A = await dev("한양 배려 패드", name="A")
        E = A.evaluate
        await E("()=>FB.set('/hy/roster',{t:{a1:{n:'A1',e:'🍎'}}, k:{k1:{n:'루아',t:'a1'}, k2:{n:'민준',t:'a1'}}}).then(()=>HyBoss.refresh(true))")
        word = await E("()=>DEX_BASE.find(w=>!Dex.has(w.en)).en")
        r = await E("()=>{ Kid.setOwner({id:'k1', n:'루아', t:'a1'}); return [Kid.shared(), Kid.ownerMode(), (Kid.me()||{}).id, Kid.guest(), Kid.k('x')]; }")
        ok(r == [True, True, "k1", None, "x"], f"🧸 주인 = 루아 · 이름을 안 골라도 루아 (내 기기처럼) {r}")
        await E("()=>{ Wallet.addGems(10, 't'); Study.setLv('basic',1,3); }")
        ok(await E("()=>Object.keys(Gift.q).length===0 && Wallet.gems()===10"), "주인이 받은 💎 = 이 패드 (배달 없음)")
        # 주인 확인 창
        await E("()=>{ window._cb=0; Kid.confirm(()=>{ window._cb=1; }); }"); await A.wait_for_timeout(300)
        r = await E("()=>[!!document.getElementById('kidAsk'), (document.querySelector('#kidAsk b')||{}).textContent]")
        ok(r[0] and "루아" in r[1], f"공부·달리기 시작 때 「루아 맞아요?」 {r}")
        await E("()=>document.querySelector('#kidAsk [data-ka=y]').click()")
        ok(await E("()=>window._cb===1 && Kid.get() && Kid.get().id==='k1'"), "네 → 루아로")
        # 수업 모드 민준
        await E("()=>Kid.set({id:'k2', n:'민준', t:'a1', pk:Date.now()})")
        r = await E("(w)=>{ const a=[!!Kid.guest(), Kid.ownerMode(), Wallet.gems(), Study.lv('basic',1)]; Wallet.addGems(7,'raid'); Wallet.addPts(45); Study.setLv('basic',2,2); Dex.add(w); return a.concat([Wallet.gems(), JSON.parse(localStorage.getItem('hyeng_wallet_v1')).gems, Study.lv('basic',2)]); }", word)
        ok(r[0] and not r[1] and r[2] == 0 and r[3] == 0, f"민준 = 수업 모드 · 루아 💎·⭐ 안 보임 {r[:4]}")
        ok(r[4] == 9 and r[5] == 10 and r[6] == 2, f"민준이 받은 💎 7 + 점수 45(=💎2) 는 민준 칸 · 루아 지갑 10 그대로 {r[4:]}")
        ok(await E("()=>!!localStorage.getItem('hyeng_wallet_v1@k2') && !!localStorage.getItem('hyeng_study_v1@k2') && !!localStorage.getItem('hyeng_dex_v1@k2')"), "수업 모드 칸 = …@k2")
        await E("()=>ShopUI.open()"); await A.wait_for_timeout(200)
        ok(await E("()=>!document.getElementById('shShop').classList.contains('on')"), "🛍 상점 막음 (내 패드에서)")
        ok(await E("()=>/선생님/.test(NameCard.change('ABC')||'')"), "공용 패드 이름 바꾸기 막음")
        sent = await E("""async()=>{ const S=[]; const p0=Online.post; Online.post=b=>{ S.push(JSON.parse(JSON.stringify(b))); return Promise.resolve({ok:true}); };
            await Online.submit({nick:'한양 배려 패드', score:10, diff:'normal', rule:'normal', dex:900});
            Kid.set({id:'k1', n:'루아', t:'a1', pk:Date.now()}); await Online.submit({nick:'한양 배려 패드', score:10, diff:'normal', rule:'normal', dex:900});
            Online.post=p0; return S.map(b=>[b.nick, b.dex, b.own||0]); }""")
        ok(sent[0][1] == "" and sent[0][2] == 0 and sent[1][1] == 900 and sent[1][2] == 1 and sent[1][0] == "👤루아", f"시트: 수업 모드 = 단어 수 안 보냄 · 주인 = 👤루아·단어 수·주인 칸 {sent}")
        ok(await E("()=>Wallet.gems()===10 && Study.lv('basic',1)===3"), "다시 루아 → 루아 것 그대로")
        await E("()=>Gift.flush()"); await A.wait_for_timeout(500)
        g = await E("()=>FB.get('/hy/gift/k2')")
        v = list((g or {}).values())
        ok(len(v) == 1 and v[0].get("g") == 7 and v[0].get("p") == 45 and "basic|2" in v[0].get("st", "") and word in v[0].get("dx", ""), f"🎁 서버 /hy/gift/k2 (💎7 · 점수45 · ⭐ · 📖) {v}")
        fb = await E("()=>localStorage.getItem('hyeng_fb_local')")
        # B = 민준 자기 기기
        B = await dev("민준", fb, "B")
        await B.evaluate("()=>HyBoss.refresh(true)")
        r = await B.evaluate("(w)=>Gift.recv().then(n=>[n, Wallet.gems(), Study.lv('basic',2), Dex.has(w), document.getElementById('actNote').classList.contains('on'), document.getElementById('actNote').innerText])", word)
        ok(r[1] == 9 and r[2] == 2 and r[3] and r[4] and "수업" in r[5], f"📦 민준 기기: 수업에서 받은 것 💎9 · ⭐ · 📖 {r[:5]}")
        await B.screenshot(path=OUT + "pad417_gift.png")
        ok(await B.evaluate("()=>FB.get('/hy/gift/k2').then(v=>!v || !Object.keys(v).length)"), "받으면 서버에서 지움")
        r = await B.evaluate("()=>Gift.recv().then(()=>Wallet.gems())")
        ok(r == 9, "두 번 받지 않음")
        # A → 🎓 졸업
        await E("""()=>{ localStorage.setItem('hyeng_dm_k1', JSON.stringify({d:'x', n:3})); localStorage.setItem('hyeng_proto_@k1_gems', '55'); localStorage.setItem('hyeng_proto_@k2_gems', '99'); localStorage.setItem('hyeng_raidtut:k2','1'); }""")
        r = await E("()=>Move.grad()")
        ok(r and r.get("ok") == 1, f"🎓 루아 기록 서버에 맡김 {r}")
        r = await E("()=>[Kid.owner(), localStorage.getItem('hyeng_wallet_v1'), localStorage.getItem('hyeng_nick'), localStorage.getItem('hyeng_dev')!==null]")
        ok(r[1] is None and r[2] == "한양 배려 패드" and r[3], f"패드 비움 (이름·기기 코드는 그대로) {r}")
        mv = await E("()=>FB.get('/hy/move/k1')")
        d = json.loads(mv["d"])["data"]
        ok("hyeng_wallet_v1" in d and "hyeng_dm_k1" in d and "hyeng_proto_@k1_gems" in d and not any("@k2" in k or k.endswith("k2") for k in d) and "hyeng_nick" not in d,
           f"맡긴 것 = 루아 것만 (민준 수업 칸 · 패드 이름 빼고) {sorted(d)[:12]}")
        fb = await E("()=>localStorage.getItem('hyeng_fb_local')")
        # C = 루아 새 기기
        C = await dev("루아", fb, "C")
        await C.evaluate("()=>HyBoss.refresh(true)")
        await C.evaluate("()=>{ Move.noReload=true; return Move.check(); }"); await C.wait_for_timeout(400)
        r = await C.evaluate("()=>[!!document.getElementById('moveAsk'), (document.getElementById('moveAsk')||{}).innerText||'']")
        ok(r[0] and "가져" in r[1], f"루아 새 기기: 「학원 패드 기록 가져올까요?」 {r[1][:40]!r}")
        await C.screenshot(path=OUT + "pad417_move.png")
        await C.evaluate("()=>document.querySelector('#moveAsk [data-mv=y]').click()"); await C.wait_for_timeout(500)
        r = await C.evaluate("()=>[JSON.parse(localStorage.getItem('hyeng_wallet_v1')).gems, localStorage.getItem('hyeng_dm'), localStorage.getItem('hyeng_proto_gems'), localStorage.getItem('hyeng_nick'), localStorage.getItem('hyeng_proto_@k2_gems')]")
        ok(r[0] == 10 and json.loads(r[1]).get("n") == 3 and r[2] == "55" and r[3] == "루아" and r[4] is None, f"가져옴: 💎10 · 미션 · My Town 💎55 (내 기기 칸으로) · 이름은 그대로 {r}")
        ok(await C.evaluate("()=>FB.get('/hy/move/k1/done').then(v=>v>0)"), "가져가면 서버에 done (다시 안 물음)")
        ok(not errs, "오류 없음 " + str(errs[:3]))
        await br.close()
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)

asyncio.run(main())
