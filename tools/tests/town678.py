"""(v678) 사용자: 「애들이 마이타운만 한다 · 데일리30 Stage 해야 들어가게」 → 오늘 서로 다른 Stage 3개 (5개 → 「우리 애들 평균적으로 5개는 안 해」 3개)
   ① 아이 기기: 처음엔 카드 🔒 0 / 3 · 누르면 잠금 창(동그라미 3개 · 오늘의 30 하러 가기) · My Town 으로 안 감
   ② 진짜 Stage 한 판 끝 → 1개 · 끝 화면 「My Town 까지 Stage 2개 더」
   ③ 같은 Stage 같은 단계 다시 = 안 셈 · 복습 한 판 = 1개 · 3개째 끝 화면 「My Town 이 열렸어요!」 · 카드 원래대로 · 누르면 My Town (hyeng_town_ok = 오늘)
   ④ 다음 날 = 0부터 다시 잠김
   ⑤ 선생님 기기 = 그냥 들어감 · 공용 패드 손님 = 끝 화면 줄 없음
   ⑥ house.html 을 바로 열면: 안 열렸으면 첫 화면 + 잠금 창 · 오늘 열었으면 그대로"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright
HOUSE = "<!doctype html><html><body><h1 id=house>HOUSE</h1><script>%s</script></body></html>"

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m, flush=True)
        if not c: bad.append(m)
    gate = open(os.path.join(SITE, "proto", "house.html"), encoding="utf-8").read()
    gate = gate[gate.index("/* (v678)"):]; gate = gate[:gate.index("})();") + 5]
    async with async_playwright() as p:
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={"width": 820, "height": 1180})
        await ctx.add_init_script("window.HY_TOWN_GATE=true; localStorage.setItem('hyeng_nick','민준');")
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await boot(pg); E = pg.evaluate
        await pg.route("**/proto/house.html*", lambda r: r.fulfill(status=200, content_type="text/html", body=HOUSE % gate))
        CARD = "()=>{ const t=document.querySelector('#selRule .c-town'); return [t.classList.contains('twLock'), t.querySelector('.townTag').textContent, t.querySelector('small').textContent]; }"
        await E("()=>{ const a=document.getElementById('rkAnn'); if(a) a.remove(); localStorage.removeItem('hyeng_town_ok'); Kid.confirm=(cb)=>cb(); document.getElementById('btnGo').click(); }"); await pg.wait_for_timeout(500)
        r = await E(CARD)
        ok(r[0] and r[1] == "🔒 0 / 3" and "3개" in r[2], f"① 카드 잠김 0/3 {r}")
        await E("()=>document.querySelector('#selRule .c-town').click()"); await pg.wait_for_timeout(500)
        r = await E("()=>{ const d=document.getElementById('townMt'); return d ? [d.querySelectorAll('.twPips i').length, d.querySelectorAll('.twPips i.on').length, d.innerText.replace(/\\s+/g,' ').slice(0,80), location.pathname] : null; }")
        ok(r and r[0] == 3 and r[1] == 0 and "Stage 3개" in r[2] and r[3].endswith("index.html"), f"① 누르면 잠금 창 · My Town 안 감 {r}")
        await pg.screenshot(path=OUT + "town678_lock.png")
        await E("()=>document.querySelector('#townMt [data-d]').click()"); await pg.wait_for_timeout(500)
        ok(await E("()=>document.getElementById('scStudy').classList.contains('on')"), "① 「오늘의 30 하러 가기」 → Daily 30")
        # ② 진짜 한 판
        G34 = await E("()=>Study.BOOKS.g34.sets[0]")
        await E("""(set)=>{ const S=Study.load(); S.srs={}; S.seen={}; S.lv={}; S.cp={}; S.tw=null; S.wuSkip=Study.today(); Study.save(); StudyUI.set=set; StudyUI.book='g34'; StudyUI.open(); StudyUI.start(0,false); }""", G34)
        await pg.wait_for_timeout(500)
        for _ in range(200):
            v = await E("()=>document.getElementById('stDone').style.display")
            if v not in ("none", ""): break
            await E(SOLVE, False); await pg.wait_for_timeout(50)
        await pg.wait_for_timeout(700)
        r = await E("()=>[Study.townN(), (document.querySelector('#stDoneIn .twLine')||{}).textContent||'']")
        ok(r[0] == 1 and "2개 더" in r[1], f"② 한 판 끝 → 1개 · 끝 화면 「2개 더」 {r}")
        await pg.screenshot(path=OUT + "town678_done.png")
        # ③
        k1 = await E("()=>Object.keys(Study.load().tw.k)[0]")
        r = await E("(k)=>{ Study.townTick(k); const a=Study.townN(); Study.townTick('rv'); return [a, Study.townN()]; }", k1)
        ok(r == [1, 2], f"③ 같은 판 다시 = 안 셈 · 복습 = 1개 {r} ({k1})")
        r = await E("""()=>{ const b=TownGate.n(); Study.townTick('xx-2'); return [Study.townN(), TownGate.line(b), TownGate.ok()]; }""")
        ok(r[0] == 3 and "열렸어요" in r[1] and r[2], f"③ 3개째 끝 화면 「열렸어요」 {r[:1]} {r[1][:60]}")
        await E("()=>{ StudyUI.close&&StudyUI.close(); show('scStart'); document.getElementById('btnGo').click(); }"); await pg.wait_for_timeout(500)
        r = await E(CARD)
        ok(not r[0] and "My Town" in await E("()=>document.querySelector('#selRule .c-town').textContent") and "🔒" not in r[1], f"③ 카드 원래대로 {r}")
        await E("()=>document.querySelector('#selRule .c-town').click()")
        await pg.wait_for_url("**/proto/house.html*", timeout=5000); await pg.wait_for_timeout(600)
        r = await E("()=>[location.pathname, !!document.getElementById('house'), localStorage.getItem('hyeng_town_ok')]")
        ok(r[0].endswith("proto/house.html") and r[1] and r[2], f"③ 누르면 My Town (오늘 표시 남김) {r}")
        # ⑥ house.html 바로: 오늘 열었으면 그대로 · 표시·공부 칸 지우면 첫 화면 잠금 창
        await pg.goto(ORIGIN + "proto/house.html"); await pg.wait_for_timeout(800)
        ok((await E("()=>location.pathname")).endswith("proto/house.html"), "⑥ 오늘 연 기기는 house.html 바로 열어도 그대로")
        await E("()=>{ localStorage.removeItem('hyeng_town_ok'); const s=JSON.parse(localStorage.getItem('hyeng_study_v1')||'{}'); s.tw=null; localStorage.setItem('hyeng_study_v1', JSON.stringify(s)); }")
        await pg.goto(ORIGIN + "proto/house.html"); await pg.wait_for_timeout(2600)
        r = await E("()=>[location.pathname, location.hash, !!document.getElementById('townMt')]")
        ok(r[0].endswith("index.html") and r[2], f"⑥ 안 열린 날 house.html 바로 → 첫 화면 + 잠금 창 {r}")
        # ④ 다음 날
        await E("""()=>{ const s=Study.load(); s.tw={d:Study.today(), k:{a:1,b:1,c:1}}; Study.save(); }"""); ok(await E("()=>TownGate.ok()"), "④ (오늘 3개)")
        await E("()=>Study._day(1)")
        r = await E("()=>[Study.townN(), TownGate.ok()]")
        ok(r == [0, False], f"④ 다음 날 = 0부터 다시 잠김 {r}")
        await E("()=>Study._day(0)")
        # ⑤ 선생님 · 공용 패드 손님
        r = await E("""()=>{ const s=Study.load(); s.tw=null; Study.save(); localStorage.setItem('hyeng_teacher_dev','1'); const a=[TownGate.ok(), TownGate.line(0)]; localStorage.removeItem('hyeng_teacher_dev'); return a; }""")
        ok(r == [True, ""], f"⑤ 선생님 기기 = 그냥 · 끝 화면 줄 없음 {r}")
        r = await E("""()=>{ const g=Kid.guest; Kid.guest=()=>({id:'x'}); const a=TownGate.line(0); Kid.guest=g; return a; }""")
        ok(r == "", f"⑤ 공용 패드 손님 = 끝 화면 줄 없음 {r!r}")
        ok(not real_errs(errs), f"JS 오류 없음 {real_errs(errs)[:2]}")
        await br.close()
    print("DONE bad=%d" % len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
