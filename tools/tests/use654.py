# v654 🎮 모드별 사용 시간 — 기기에서 세기 · 보내기 · 선생님 화면 카드 (+ 서버 gs_use654.js)
import asyncio, sys, os, subprocess, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
OUT = os.environ.get("HY_OUT", "/tmp/use654_")
bad = []
def ok(c, m):
    print(("OK  " if c else "BAD ") + m)
    if not c: bad.append(m)
REP = {"at": 0, "d": {"nicks": [], "use": {"days": 14, "kids": 9, "modes": [["study", "오늘의 30", 1840.5, 9], ["gram", "문법", 62, 3], ["run", "달리기", 410, 8], ["battle", "교실 배틀", 95, 6], ["raid", "레이드", 0, 0],
       ["board", "보드게임", 48, 5], ["esc", "저택 탈출", 30, 4], ["vs", "대결", 0, 0], ["town", "마이타운", 0, 0], ["menu", "첫 화면", 120, 9]]}}}

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        pg = await ctx.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg); E = pg.evaluate
        posts = []
        async def grab(route):
            try: posts.append(json.loads(route.request.post_data or "{}"))
            except Exception: pass
            await route.fulfill(status=200, content_type="application/json", body='{"ok":true}')
        await pg.route("**/script.google.com/**", grab)
        ok(await E("()=>{ Use.tick(false); return localStorage.getItem('hyeng_use_v1'); }") is None, "자동 시험(webdriver)에서는 안 셈")
        # 시간을 손으로 흘려 보내며 세기 (tick 사이를 15초로)
        STEP = """(sec)=>{ Use.force=true; Use.act=Date.now(); if(Use.at) Use.at-=sec*1000; Use.tick(false); return [Use.cur, Use.load().s, Use.load().n]; }"""
        r = await E("()=>{ Use.force=true; localStorage.removeItem('hyeng_use_v1'); Use.cur=''; Use.at=0; Use.act=Date.now(); Use.tick(false); return Use.cur; }"); ok(r == "menu", f"첫 화면 = menu {r}")
        r = await E(STEP, 15); ok(abs(r[1].get("menu", 0) - 15) < 1.5, f"15초 뒤 menu 15초 {r[1]}")
        await E("()=>{ StudyUI.open(); }"); await pg.wait_for_timeout(500)
        r = await E(STEP, 15); r = await E(STEP, 15); ok(r[0] == "study" and abs(r[1].get("study", 0) - 15) < 1.5 and r[2].get("study") == 1, f"Daily 30 = study · 들어간 번 1 {r}")
        await E("()=>GramUI.start('mid-11')"); await pg.wait_for_timeout(500)
        r = await E(STEP, 15); r = await E(STEP, 15); ok(r[0] == "gram" and abs(r[1].get("gram", 0) - 15) < 1.5, f"문법 판 = gram {r[:2]}")
        await E("()=>{ GramUI.home(); }"); await pg.wait_for_timeout(300)
        # 2분 동안 안 만지면 안 셈 (혼자 하는 모드) · 수업 게임은 셈
        r = await E("()=>{ Use.tick(false); const a=Use.load().s.study; Use.act=Date.now()-130000; Use.tick(false); const c1=Use.cur; Use.at-=15000; Use.tick(false); return [a, Use.load().s.study, c1]; }")
        ok(r[2] == "" and abs(r[0] - r[1]) < 1, f"2분 넘게 안 만지면 멈춤 {r}")
        r = await E("()=>{ BoardPad.room='9999'; Use.act=Date.now()-130000; Use.tick(false); const c=Use.cur; Use.at-=15000; Use.tick(false); const s=Use.load().s.board; BoardPad.room=null; return [c, s]; }")
        ok(r[0] == "board" and abs(r[1] - 15) < 1.5, f"보드게임(수업)은 안 만져도 셈 {r}")
        r = await E("()=>{ EscPad.room='1'; Use.tick(false); const a=Use.cur; EscPad.room=null; Battle.role='kid'; Use.tick(false); const b=Use.cur; Battle.role='host'; Use.tick(false); const c=Use.cur; Battle.role=null; Raid.role='kid'; Use.tick(false); const d=Use.cur; Raid.role=null; return [a,b,c,d]; }")
        ok(r == ["esc", "battle", "", "raid"], f"저택 탈출 · 교실 배틀 · (방장 TV 는 안 셈) · 레이드 {r}")
        # 보내기: 5분마다 · 숨길 때 — 그날 합계(분)
        ok(len([x for x in posts if x.get("type") == "use"]) >= 1, "쌓이면 알아서 보냄 (5분마다)"); posts.clear()
        await E("()=>{ const o=Use.load(); o.s={study:600, board:120, menu:2}; localStorage.setItem('hyeng_use_v1', JSON.stringify(o)); localStorage.setItem('hyeng_nick','TESTER'); Use.cur=''; Use.at=0; Use.sentAt=0; Use.act=Date.now(); Use.tick(true); }"); await pg.wait_for_timeout(400)
        u = [x for x in posts if x.get("type") == "use"]
        ok(len(u) == 1 and u[0]["m"].get("study") == 10 and u[0]["m"].get("board") == 2 and "menu" not in u[0]["m"] and u[0]["day"] and u[0]["dev"] and u[0]["key"] == "HYENG" and u[0]["ver"].startswith("v"), f"서버로: 모드마다 분 (6초 안 된 모드는 뺌) {u and u[-1]}")
        await E("()=>{ Use.send(Use.load(), true); Use.send(Use.load(), false); }"); await pg.wait_for_timeout(300)
        ok(len([x for x in posts if x.get("type") == "use"]) == 1, "바뀐 게 없으면 다시 안 보냄")
        r = await E("()=>{ localStorage.setItem('hyeng_teacher_dev','1'); const a=JSON.stringify(Use.load()); Use.at-=15000; Use.tick(false); const same=a===JSON.stringify(Use.load()); localStorage.removeItem('hyeng_teacher_dev'); return same; }"); ok(r, "선생님 기기는 안 셈")
        e = real_errs(errs); ok(not e, f"오류 없음 {e[:3]}"); await ctx.close()
        # 선생님 화면 카드
        for nm, vp in (("pad", (820, 1180)), ("ph", (390, 844))):
            ctx = await b.new_context(viewport={"width": vp[0], "height": vp[1]}, is_mobile=True, has_touch=True); T = await ctx.new_page(); await boot(T)
            await T.evaluate("(r)=>{ r.at=Date.now(); localStorage.setItem('hyeng_admin_rep', JSON.stringify(r)); sessionStorage.setItem('hyeng_admin_ok',String(Date.now())); sessionStorage.setItem('hyeng_admin_tk','testkey'); }", REP)
            await T.reload(); await T.wait_for_timeout(1500)
            await T.evaluate("(R)=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); Online.on=()=>true; Notice.fetch=()=>Promise.resolve({v:3, notices:[]}); Online.submit=o=>Promise.resolve(o.type==='report' ? {ok:true, rep:R.d} : {ok:true}); document.querySelectorAll('.sheet.on').forEach(s=>s.classList.remove('on')); Admin.open(); }", REP)
            await T.wait_for_timeout(500); await T.click('#adTabs [data-t="rec"]'); await T.wait_for_timeout(800)
            await T.evaluate("()=>{ document.querySelectorAll('#adBody details').forEach(d=>{ if(/모드별/.test(d.textContent)) d.open=true; }); const el=document.querySelector('#adBody .adUse'); if(el) el.scrollIntoView({block:'center'}); }")
            r = await T.evaluate("()=>{ const R=[...document.querySelectorAll('#adBody .adUseR')]; return [R.length, R.filter(x=>x.classList.contains('zero')).map(x=>x.querySelector('b').textContent), R[0] && R[0].textContent, document.getElementById('adBody').scrollWidth-document.getElementById('adBody').clientWidth]; }")
            ok(r[0] == 10 and r[1] == ["레이드", "대결", "마이타운"] and "30시간" in r[2] and r[3] <= 1, f"{nm}: 🎮 모드별 사용 시간 — 10줄 · 안 쓰는 모드 흐리게 · 가로 넘침 없음 {r[1:]}")
            await T.screenshot(path=f"{OUT}admin_{nm}.png"); await ctx.close()
        await b.close()
    g = subprocess.run(["node", os.path.join(os.path.dirname(os.path.abspath(__file__)), "gs_use654.js")], capture_output=True, text=True); ok(g.returncode == 0, "Code.gs v21 (gs_use654.js)")
    print("PASS" if not bad else "FAIL", len(bad))
    if bad: sys.exit(1)
asyncio.run(main())
