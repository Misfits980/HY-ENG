"""(v409) 사용자: "레이스 대결이나 반 대결 몇 과까지 하는지 선택을 못 하게 되어 있더라 (관리 화면도) · 레이스 대결에 시간 제한이 있어 · 캐릭터 선택도 못 해"
  ① 관리 🏃 달리기 레이스: 🎯 책 · Stage 골라서 (Stage 눌러 고르기) → 방 설정 rng/set/from/to → 아이 달리기 단어 = 그 Stage 단어
  ② 시간: 10분 · ⏹ 선생님이 끝낼 때까지 (레이스·교실 배틀) ③ 넘어지면 🏃 다시 달리기 (점수 이어서)
  ④ 기다리는 방에서 🧑 캐릭터 고르기 (교실 배틀·레이스·레이드) → 서버 내 자리 c 도 바뀜"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "FAIL ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={"width": 1194, "height": 834}, service_workers="block"); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        T = await ctx.new_page(); T.on("pageerror", lambda e: errs.append("T " + str(e))); await boot(T)
        await T.evaluate("()=>{ sessionStorage.setItem('hyeng_admin_ok',String(Date.now())); sessionStorage.setItem('hyeng_admin_tk','testkey'); }"); await T.reload(); await T.wait_for_timeout(2000)
        await T.evaluate("()=>Admin.open()"); await T.wait_for_timeout(500)
        await T.evaluate("()=>document.querySelector('[data-ad=nowEdit][data-k=rr]').click()"); await T.wait_for_timeout(700)
        r = await T.evaluate("()=>[document.getElementById('adRrSet').value, !!document.getElementById('adRrFromPick'), getComputedStyle(document.getElementById('adRrStg')).display, [...document.getElementById('adRrDur').options].map(o=>o.value).join()]")
        ok(r[0] == "stg" and r[1] and r[2] != "none", f"레이스: 🎯 책·Stage 골라서 + Stage 고르기 판 {r[:3]}")
        ok("600" in r[3] and "3600" in r[3], f"레이스 시간: 10분 · 끝낼 때까지 {r[3]}")
        await T.screenshot(path=OUT + "bt409_admin_rr.png")
        await T.evaluate("()=>{ const s=document.getElementById('adRrBk'); s.value='g56'; s.dispatchEvent(new Event('change')); const f=document.getElementById('adRrFrom'), t=document.getElementById('adRrTo'); f.value='4'; t.value='7'; f.dispatchEvent(new Event('change')); t.dispatchEvent(new Event('change')); const d=document.getElementById('adRrDur'); d.value='3600'; d.dispatchEvent(new Event('change')); }")
        await T.evaluate("()=>{ const s=document.getElementById('adRrSet'); s.value='elem'; s.dispatchEvent(new Event('change')); }"); await T.wait_for_timeout(100)
        ok(await T.evaluate("()=>getComputedStyle(document.getElementById('adRrStg')).display")=="none", "책 전체를 고르면 Stage 칸 숨김")
        await T.evaluate("()=>{ const s=document.getElementById('adRrSet'); s.value='stg'; s.dispatchEvent(new Event('change')); }")
        bt = await T.evaluate("()=>[...document.getElementById('adBtDur').options].map(o=>o.value).join()")
        ok("3600" in bt and "600" in bt, f"교실 배틀 시간도 10분 · 끝낼 때까지 {bt}")
        # 방 만들기 (관리 화면의 설정 그대로)
        room = await T.evaluate("""()=>new Promise(res=>{ const h=Battle.host.bind(Battle); Battle.host=(o, r)=>{ window._o=o; const x=h(o, r); res(x); return x; }; document.querySelector('[data-ad=rrGo]').click(); })""")
        o = await T.evaluate("()=>window._o")
        ok(o["rng"] == "stg" and o["set"] == "g56" and o["from"] == 4 and o["to"] == 7 and o["dur"] == 3600, f"방 설정 = g56 Stage 범위 · 끝낼 때까지 {o.get('lbl')} {o.get('from')}~{o.get('to')}")
        await T.wait_for_timeout(600)
        c = await T.evaluate(f"()=>FB.get('/battle/{room}/cfg', true)")
        ok(c["rng"] == "stg" and c["from"] == 4 and c["to"] == 7 and c["rset"] == "g56", f"서버 방 설정 {c.get('rng')} {c.get('rset')} {c.get('from')}~{c.get('to')}")
        # 아이
        K = await ctx.new_page(); K.on("pageerror", lambda e: errs.append("K " + str(e))); await boot(K)
        await K.evaluate(f"()=>{{ G.char='hero'; Battle.join('{room}', {{id:'k1', n:'민준', t:'all'}}); }}"); await K.wait_for_timeout(1500)
        ok(await K.evaluate("()=>/끝낼 때까지/.test(document.getElementById('scRaid').innerText)"), "기다리는 방: '선생님이 끝낼 때까지'")
        chs = await K.evaluate("()=>[...document.querySelectorAll('#scRaid [data-chpick]')].map(b=>b.dataset.chpick)")
        ok(len(chs) >= 3 and "hero" in chs, f"🧑 캐릭터 고르기 {chs}")
        pick = [x for x in chs if x != "hero"][0]
        await K.evaluate(f"()=>document.querySelector('#scRaid [data-chpick=\"{pick}\"]').click()"); await K.wait_for_timeout(800)
        r = await K.evaluate(f"()=>FB.get('/battle/{room}/p/k1', true).then(v=>[G.char, v && v.c, !!document.querySelector('#scRaid [data-chpick=\"{pick}\"].on')])")
        ok(r == [pick, pick, True], f"고르면 내 캐릭터 · 서버 자리도 {r}")
        await K.screenshot(path=OUT + "bt409_wait.png")
        # 시작 → 달리기 단어 = 고른 Stage
        await T.evaluate("()=>Battle.hostAct('start')")
        for _ in range(60):
            if await K.evaluate("()=>!!G.race && G.running"): break
            await K.wait_for_timeout(200)
        r = await K.evaluate("()=>{ const L=Study.lessons('g56'), want=new Set([].concat(...L.slice(4,8).map(x=>x.ws.map(w=>w.en)))); return [!!G.race, (G.words||[]).length, (G.words||[]).every(en=>want.has(en)), want.size, G.set, G.char]; }")
        ok(r[0] and r[1] > 0 and r[2] and r[1] == r[3] and r[4] == "g56", f"달리기 단어 = g56 Stage 5~8 단어만 {r[:5]}")
        ok(r[5] == pick, f"고른 캐릭터로 달림 {r[5]}")
        # 넘어짐 → 다시 달리기 (점수 이어서)
        await K.evaluate("()=>{ G.score=40; RunRace.push(true); RunRace.done(); G.running=false; }"); await K.wait_for_timeout(700)
        r = await K.evaluate("()=>[Battle.sc, !!document.querySelector('#scRaid [data-btrerun]'), document.getElementById('scRaid').innerText.includes('넘어졌어요')]")
        ok(r[0] == 40 and r[1] and r[2], f"넘어지면 '다시 달리기' {r}")
        await K.evaluate("()=>{ G._overDone=false; document.querySelector('#scRaid [data-btrerun]').click(); }")
        for _ in range(40):
            if await K.evaluate("()=>!!G.race"): break
            await K.wait_for_timeout(200)
        r = await K.evaluate("()=>{ G.score=25; return [!!G.race, G.race && G.race.base, RunRace.score(), (G.words||[]).length>0]; }")
        ok(r[0] and r[1] == 40 and r[2] == 65 and r[3], f"다시 달리면 점수 이어서 40 + 25 = {r}")
        await K.evaluate("()=>{ try{ RunRace.abort(); }catch(e){} }")
        await T.evaluate("()=>Battle.hostAct('end')"); await T.wait_for_timeout(500)
        # 레이드 기다리는 방에도 캐릭터 고르기
        rd = await T.evaluate("()=>{ Raid.MIN=1000; return Raid.host('g34',['vest','cap','glove','beard','belt'], 0, null, 250); }")
        K2 = await ctx.new_page(); K2.on("pageerror", lambda e: errs.append("K2 " + str(e))); await boot(K2)
        await K2.evaluate(f"()=>{{ G.char='hero'; Raid.FAST=0; Raid.join('{rd}','서연'); }}"); await K2.wait_for_timeout(1200)
        n = await K2.evaluate("()=>document.querySelectorAll('#scRaid [data-chpick]').length")
        ok(n >= 3, f"레이드 기다리는 방: 캐릭터 고르기 {n}")
        await K2.evaluate(f"()=>document.querySelector('#scRaid [data-chpick=\"{pick}\"]').click()"); await K2.wait_for_timeout(800)
        r = await K2.evaluate(f"()=>[G.char, (RaidNet.get().p||{{}})[Raid.me] && RaidNet.get().p[Raid.me].c]")
        ok(r == [pick, pick], f"레이드: 고르면 무대 내 캐릭터 · 서버 자리 {r}")
        ok(not errs, "오류 없음 " + str(errs[:3]))
        await br.close()
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)

asyncio.run(main())
