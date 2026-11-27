"""(v738) ⚔️ 수업 탭 = 시안 v4-3 — 사용자: 「방탈출 없애고 시안처럼 해 봐」
   ① 맨 위 📚 오늘 단어 한 줄 (반 · 책 · 6단원 · 30개) → 「바꾸기」 = 아래에서 올라오는 창 (반 · 책 · 단원 번호판 · 단어 미리 보기) · 반마다 기억
   ② 놀이 그림 4개(⚔️ 레이드 · 🏃 달리기 레이스 · 🏫 교실 배틀 · 🎲 파티 보드) · ▶/톡 = 지난 설정 그대로 방 · ⚙/꾹 = 이번만 바꾸기 창(설정 칸 그대로)
   ③ 저택 탈출 코드 없음 · 휴대폰(390) · 패드(820) 옆 넘침 없음 · 창이 아래 탭 바 위로 보임"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "adm735.py"), encoding="utf-8").read().split("async def main():")[0]
ns = {"__name__": "x", "__file__": os.path.join(os.path.dirname(os.path.abspath(__file__)), "adm735.py")}; exec(src, ns)
from harness import *
from playwright.async_api import async_playwright
SHOT = os.environ.get("HY_SHOT")
async def open_admin(br, vw, vh, ph, errs):
    os.environ["HY_ADM_PH"] = "1" if ph else ""
    ctx = await br.new_context(viewport={"width": vw, "height": vh}, is_mobile=ph, has_touch=True, device_scale_factor=2 if SHOT else 1)
    await ctx.add_init_script("window.HY_FB_LOCAL=true;")
    T = await ctx.new_page(); T.on("pageerror", lambda e: errs.append(str(e))); E = T.evaluate
    await T.clock.set_fixed_time(ns["NOW"])
    await boot(T); await E(ns["SEED"], ns["K"]); await E(ns["LOGIN"]); await T.reload(); await T.wait_for_timeout(1500)
    await E("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); }"); await E(ns["MOCK"], ns["K"])
    await E("()=>{ document.querySelectorAll('.sheet.on').forEach(s=>s.classList.remove('on')); Admin.open(); Admin._tab('now'); }"); await T.wait_for_timeout(1800)
    return ctx, T, E
async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch()
        ctx, T, E = await open_admin(br, 390, 844, True, errs)
        r = await E("""()=>({esc:[typeof Esc, typeof EscTV, typeof EscPad, typeof ESC_OPEN], tiles:[...document.querySelectorAll('#adBody .a3T')].map(t=>t.dataset.k+':'+t.dataset.go),
            sum:(document.getElementById('a2ScSum')||{}).textContent||'', old:!!document.querySelector('#adBody .a2Scope, #adBody .adTiles, #adBody [data-ad=bdTry], #adBody [data-ad=escTry]'),
            forms:['adRrSet','adBtSet','adRdBook','adNowSet'].map(id=>!!document.getElementById(id)), shOn:document.getElementById('a3Sh').classList.contains('on'),
            sub:[...document.querySelectorAll('#adBody .a3T small')].map(e=>e.textContent), ox:document.documentElement.scrollWidth-innerWidth, ix:(s=>s.scrollWidth-s.clientWidth)(document.querySelector('#shAdmin .sheetIn'))})""")
        ok(r["esc"] == ["undefined"] * 4, f"③ 저택 탈출 코드 없음 {r['esc']}")
        ok(r["tiles"] == ["rd:raidGo", "rr:rrGo", "bt:btGo", "bd:bdGo"] and not r["old"], f"② 놀이 그림 4개 · 예전 범위 카드·한 줄 타일·보드 단추 없음 {r['tiles']}")
        ok(all(r["forms"]) and not r["shOn"], f"설정 칸은 숨은 채 그대로 (방 만들 때 읽음) · 창은 닫혀 있음 {r['forms']}")
        ok(all(s and s != "…" for s in r["sub"]), f"그림마다 방식 · 시간 한 줄 {r['sub']}")
        ok(r["ox"] <= 0 and r["ix"] <= 0, f"③ 휴대폰 옆 넘침 없음 {r['ox']} {r['ix']}")
        if SHOT: await T.screenshot(path=OUT + "cls738_ph_now.png")
        # ① 바꾸기 → 창 · 6단원 고르기
        await E("()=>document.querySelector('#adBody .a3ScB').click()"); await T.wait_for_timeout(900)
        r = await E("""()=>{ const sh=document.getElementById('a3Sh'), inn=sh.querySelector('.a3ShIn'), b=inn.getBoundingClientRect(), nav=document.getElementById('adNav');
            const hit=document.elementFromPoint(innerWidth/2, innerHeight-30); return {on:sh.classList.contains('on'), top:Math.round(b.top), bot:Math.round(b.bottom), h:innerHeight,
            grid:inn.querySelectorAll('.stgGB').length, cls:inn.querySelectorAll('[data-ad=nowCls]').length, hitIn:inn.contains(hit), sel:!!inn.querySelector('#adNowSet')}; }""")
        ok(r["on"] and r["grid"] >= 10 and r["cls"] >= 3 and r["sel"] and r["hitIn"] and r["bot"] <= r["h"] and r["top"] > 40, f"① 바꾸기 → 아래에서 창 (반 · 책 · 번호판 · 탭 바 위로) {r}")
        r = await E("""async ()=>{ const s=document.getElementById('adNowSet'); s.value='g56'; s.dispatchEvent(new Event('change')); await new Promise(z=>setTimeout(z,200));
            const g=[...document.querySelectorAll('#a3Sh .stgGB')].find(b=>b.textContent.trim()==='6'); g.click(); await new Promise(z=>setTimeout(z,250));
            return {sum:document.getElementById('a2ScSum').textContent, wd:document.getElementById('a3Wd').textContent, bt:[document.getElementById('adBtSet').value, document.getElementById('adBtFrom').value, document.getElementById('adBtTo').value],
              rr:[document.getElementById('adRrSet').value, document.getElementById('adRrBk').value], rd:document.getElementById('adRdBook').value}; }""")
        ok("6단원" in r["sum"] and "30개" in r["sum"] and "G5-6" in r["sum"], f"① 6단원 하나 = 「… G5-6 · 6단원 · 30개」 {r['sum']}")
        ok(r["wd"].startswith("단어 30개") and "contest" in r["wd"], f"① 고른 단어 미리 보기 {r['wd'][:60]}")
        ok(r["bt"][0] == "g56" and r["rr"] == ["stg", "g56"] and r["rd"] == "g56", f"① 고른 범위가 배틀 · 레이스 · 레이드(책)에 같이 {r['bt']} {r['rr']} {r['rd']}")
        if SHOT: await T.screenshot(path=OUT + "cls738_ph_scope.png")
        # 반마다 기억: 4반으로 → 다른 곳 → 3반으로 돌아오면 6단원
        await E("()=>[...document.querySelectorAll('#a3Sh [data-ad=nowCls]')].find(b=>b.textContent.indexOf('3반')>=0).click()"); await T.wait_for_timeout(900)
        await E("""async ()=>{ const g=[...document.querySelectorAll('#a3Sh .stgGB')].find(b=>b.textContent.trim()==='6'); g.click(); await new Promise(z=>setTimeout(z,250)); }""")
        await E("()=>[...document.querySelectorAll('#a3Sh [data-ad=nowCls]')].find(b=>b.textContent.indexOf('4반')>=0).click()"); await T.wait_for_timeout(900)
        await E("""async ()=>{ const g=[...document.querySelectorAll('#a3Sh .stgGB')].find(b=>b.textContent.trim()==='9'); g.click(); await new Promise(z=>setTimeout(z,250)); }""")
        a4 = await E("()=>[document.getElementById('a2ScSum').textContent, document.getElementById('a3Sh').classList.contains('on')]")
        await E("()=>[...document.querySelectorAll('#a3Sh [data-ad=nowCls]')].find(b=>b.textContent.indexOf('3반')>=0).click()"); await T.wait_for_timeout(900)
        a3 = await E("()=>document.getElementById('a2ScSum').textContent")
        ok("4반" in a4[0] and "9단원" in a4[0] and a4[1] and "3반" in a3 and "6단원" in a3, f"① 반마다 기억 (4반 = 9단원 · 3반으로 오면 6단원) · 반을 바꿔도 창 그대로 {a4} {a3}")
        await E("()=>document.querySelector('#a3Sh .a3ShF [data-ad=scClose]').click()"); await T.wait_for_timeout(300)
        ok(not await E("()=>document.getElementById('a3Sh').classList.contains('on')"), "✔ 이 단어로 정하기 → 창 닫힘")
        # ② ⚙ = 이번만 바꾸기 창 (교실 배틀 설정 칸)
        await E("()=>document.querySelector('#adBody .a3T_bt .a3Ed').click()"); await T.wait_for_timeout(500)
        r = await E("""()=>{ const sh=document.getElementById('a3Ed'), f=document.getElementById('adF_bt'); return {on:sh.classList.contains('on'), ttl:sh.querySelector('.a3ShH b').textContent, vis:!!(f && f.offsetParent), go:!!(f && f.querySelector('[data-ad=btGo]'))}; }""")
        ok(r["on"] and "교실 배틀" in r["ttl"] and r["vis"] and r["go"], f"② ⚙ → 「🏫 교실 배틀 · 이번엔 이렇게」 창 · 설정 칸 · 방 만들기 단추 {r}")
        if SHOT: await T.screenshot(path=OUT + "cls738_ph_edit.png")
        await E("()=>document.querySelector('#a3Ed .a3X').click()"); await T.wait_for_timeout(400)
        ok(not await E("()=>document.getElementById('a3Ed').classList.contains('on')"), "② ✕ → 닫힘")
        # 꾹 = 설정 창 (손 떼도 시작 안 함)
        r = await E("""async ()=>{ const t=document.querySelector('#adBody .a3T_rr'), r=t.getBoundingClientRect(), x=r.left+40, y=r.top+40; let started=0; const s0=Battle.host; Battle.host=()=>{ started++; return '1234'; };
            t.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,clientX:x,clientY:y})); await new Promise(z=>setTimeout(z,700)); t.dispatchEvent(new PointerEvent('pointerup',{bubbles:true,clientX:x,clientY:y})); t.click();
            await new Promise(z=>setTimeout(z,400)); const on=document.getElementById('a3Ed').classList.contains('on'), ttl=document.querySelector('#a3Ed .a3ShH b').textContent; Battle.host=s0; return [on, ttl, started]; }""")
        ok(r[0] and "달리기" in r[1] and r[2] == 0, f"② 그림을 꾹 = 이번만 바꾸기 창 (손을 떼도 방 안 만듦) {r}")
        await E("()=>document.querySelector('#a3Ed .a3X').click()"); await T.wait_for_timeout(300)
        # 톡 = 바로 시작 (레이스 = Battle.host · 보드 = BoardTV.host · 레이드 = Raid.host) — 실제 방은 안 만듦
        r = await E("""async ()=>{ const L=[]; const b0=Battle.host, r0=Raid.host, d0=BoardTV.host; Battle.host=o=>{ L.push(['bt', o.kind||'', o.set, o.from, o.to]); return '1'; }; Raid.host=(b)=>{ L.push(['rd', b]); return '1'; }; BoardTV.host=c=>{ L.push(['bd', c.set, c.from, c.to, c.rounds]); };
            const fr=window.freeRoom; for(const k of ['rr','bt','rd','bd']){ document.getElementById('shAdmin').classList.add('on'); const t=document.querySelector('#adBody .a3T_'+k); if(t) t.click(); await new Promise(z=>setTimeout(z,500)); }
            Battle.host=b0; Raid.host=r0; BoardTV.host=d0; return L; }""")
        kinds = [x[0] + (":" + x[1] if x[0] == "bt" else "") for x in r]
        ok(kinds == ["bt:run", "bt:", "rd", "bd"], f"② 그림 톡 = 바로 시작 (레이스 · 배틀 · 레이드 · 보드) {r}")
        ok(all(x[2] == "g56" for x in r if x[0] in ("bt",)) and r[-1][1] == "g56", f"② 오늘 단어(6단원) 그대로 들어감 {r}")
        await ctx.close()
        # 패드
        ctx, T, E = await open_admin(br, 820, 1180, False, errs)
        r = await E("()=>({n:document.querySelectorAll('#adBody .a3T').length, ox:document.documentElement.scrollWidth-innerWidth, w:[...document.querySelectorAll('#adBody .a3T')].map(t=>Math.round(t.getBoundingClientRect().width))})")
        ok(r["n"] == 4 and r["ox"] <= 0, f"③ 패드: 그림 4개 · 옆 넘침 없음 {r}")
        if SHOT: await T.screenshot(path=OUT + "cls738_pad_now.png")
        await E("()=>document.querySelector('#adBody .a3ScB').click()"); await T.wait_for_timeout(900)
        await T.wait_for_function("()=>!document.getAnimations().some(a=>a.animationName==='a3Up' && a.playState==='running')", timeout=8000)
        r = await E("()=>{ const b=document.querySelector('#a3Sh .a3ShIn').getBoundingClientRect(); return [Math.round(b.width), Math.round(b.left), Math.round(b.bottom), innerHeight]; }")
        ok(r[0] <= 680 and r[1] > 0 and r[2] <= r[3], f"③ 패드: 창은 가운데 680 폭 {r}")
        if SHOT: await T.screenshot(path=OUT + "cls738_pad_scope.png")
        await ctx.close(); await br.close()
    e = real_errs(errs); ok(not e, f"오류 없음 {e[:3]}")
    print("BAD: %d" % len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
