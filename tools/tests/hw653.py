# v653 📒 문법 숙제 (반 · 한 아이) + 선생님 📒 문법별 정답률
import asyncio, sys, os, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
OUT = os.environ.get("HY_OUT", "/tmp/hw653_")
bad = []
def ok(c, m):
    print(("OK  " if c else "BAD ") + m)
    if not c: bad.append(m)
ROSTER = {"t": {"a": {"n": "사자반", "e": "🦁"}, "b": {"n": "토끼반", "e": "🐰"}}, "k": {"k1": {"n": "민준", "t": "a"}, "k2": {"n": "서연", "t": "a"}, "k3": {"n": "지호", "t": "b"}}}
REP = {"at": 0, "d": {"nicks": [], "learn": {"days": 14, "kids": [{"n": "민준", "ok": 9, "tot": 20, "sp": 3, "w": [["quite", 3]], "g": ["중등 문법 · 현재완료", 45]}], "words": [],
       "gram": [["중등 문법 · 현재완료", 2, 3, 45], ["중등 문법 · 수동태", 1, 1, 100]]}}}

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={"width": 820, "height": 1180}, is_mobile=True, has_touch=True); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        T = await ctx.new_page(); errs = []; T.on("pageerror", lambda e: errs.append(str(e))); await boot(T); E = T.evaluate
        await E("(r)=>{ r.at=Date.now(); localStorage.setItem('hyeng_admin_rep', JSON.stringify(r)); sessionStorage.setItem('hyeng_admin_ok', String(Date.now())); sessionStorage.setItem('hyeng_admin_tk', 'testkey'); }", REP)
        await T.reload(); await T.wait_for_timeout(1500)
        await E("(R)=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); window.confirm=()=>true; Online.on=()=>true; Online.submit=o=>Promise.resolve(o.type==='report' ? {ok:true, rep:R.d} : {ok:true}); Notice.fetch=()=>Promise.resolve({v:3, notices:[]}); }", REP)
        await E("(r)=>FB.set('/hy/roster', r).then(()=>Promise.all([HyBoss.refresh(true), Gram.load()]))", ROSTER); await T.wait_for_timeout(400)
        async def work():
            await E("()=>{ document.querySelectorAll('.sheet.on').forEach(s=>s.classList.remove('on')); Admin.open(); }"); await T.wait_for_timeout(400)
            await E("()=>document.querySelector('#adTabs [data-t=\"work\"]').click()"); await T.wait_for_timeout(900)
        await work()
        r = await E("()=>[document.querySelectorAll('#adGwUnits input').length, [...document.querySelectorAll('#adGwUnits .gwSec')].map(x=>x.textContent), document.getElementById('adGwKid').options.length, document.getElementById('adGwGoal').value]")
        ok(r[0] >= 23 and r[1][0] == "중등 문법" and r[2] == 4 and r[3] == "3", f"📒 문법 숙제 내기 칸: 단원 {r[0]}개 · 묶음 · 아이 고르기 {r[1]}")
        await E("()=>document.querySelector('[data-ad=hwGOpen]').click()"); await T.wait_for_timeout(300)
        ok("골라" in await E("()=>document.getElementById('adToast').textContent"), "단원을 안 고르면 안내")
        # 사자반에 현재완료 · 수동태 ★2 까지
        await E("()=>{ document.getElementById('adGwTeam').value='a'; ['mid-15','mid-16'].forEach(id=>{ document.querySelector('#adGwUnits input[value=\"'+id+'\"]').checked=true; }); document.getElementById('adGwGoal').value='2'; document.querySelector('[data-ad=hwGOpen]').click(); }"); await T.wait_for_timeout(900)
        cur = await E("()=>FB.get('/hy/hw/cur')"); g = [c for c in (cur or {}).values() if c.get("kind") == "gram"]
        ok(len(g) == 1 and g[0]["gids"] == ["mid-15", "mid-16"] and g[0]["team"] == "a" and g[0]["goal"] == 2 and g[0]["set"] == "@gram" and "현재완료" in g[0]["title"], f"서버에 문법 숙제 {g and {k: g[0][k] for k in ('team','gids','goal','title')}}")
        # 단어 숙제를 같은 반에 내도 문법 숙제는 그대로 · 반대도
        await E("()=>{ document.getElementById('adHwTeam').value='a'; document.querySelector('[data-ad=hwOpen]').click(); }"); await T.wait_for_timeout(900)
        cur = await E("()=>FB.get('/hy/hw/cur')"); kinds = sorted(c.get("kind", "word") for c in cur.values())
        ok(kinds == ["gram", "word"], f"같은 반에 단어 숙제를 내도 문법 숙제가 안 지워짐 {kinds}")
        # 지호(토끼반) 한 아이에게 to부정사 ★1
        await E("()=>{ document.getElementById('adGwKid').value='k3'; document.querySelector('#adGwUnits input[value=\"mid-11\"]').checked=true; document.getElementById('adGwGoal').value='1'; document.querySelector('[data-ad=hwGOpen]').click(); }"); await T.wait_for_timeout(900)
        cur = await E("()=>FB.get('/hy/hw/cur')"); gk = [c for c in cur.values() if c.get("kid") == "k3"]
        ok(len(cur) == 3 and len(gk) == 1 and gk[0]["gids"] == ["mid-11"], f"한 아이에게만 (다른 숙제는 그대로) {len(cur)}")
        r = await E("()=>[...document.querySelectorAll('#adBody .hwCur h3')].map(x=>x.textContent)")
        ok(any("📒" in x and "사자반" in x and "★2" in x for x in r) and any("📒" in x and "지호" in x for x in r), f"선생님 카드: 반 · 아이 이름 {r}")
        await T.screenshot(path=OUT + "teacher_pad.png", full_page=False)
        await E("()=>{ const el=document.getElementById('adGwUnits'); if(el) el.scrollIntoView({block:'center'}); }"); await T.wait_for_timeout(200); await T.screenshot(path=OUT + "teacher_form_pad.png")
        # 옛 게임이 보는 눈: 단어 숙제 고르기에 문법 숙제가 안 섞임
        ids = {c["id"]: c for c in cur.values()}
        # 아이: 민준(사자반)
        await E("()=>{ Admin.close(); localStorage.setItem('hyeng_me', JSON.stringify({id:'k1', at:Date.now()})); sessionStorage.removeItem('hyeng_admin_ok'); localStorage.removeItem('hyeng_gram_v1'); }")
        await E("()=>HyHW.check(true)"); await T.wait_for_timeout(300)
        await E("()=>{ StudyUI.book='mid'; StudyUI.set=Study.BOOKS.mid.sets[0]; StudyUI.open(); }"); await T.wait_for_timeout(700)
        r = await E("()=>[[...document.querySelectorAll('#stPath .hwCard')].map(x=>x.querySelector('.hwT b').textContent), (document.querySelector('#stPath .hwCard.gw .hwBar span')||{}).textContent, HyHW.c && !HyHW.isG(HyHW.c)]")
        ok(len(r[0]) == 2 and "문법 숙제" in r[0][0] and "to부정사" not in " ".join(r[0]) and r[1] == "0 / 2 단원" and r[2], f"민준: 📒 문법 숙제 카드(우리 반 것만) + 단어 숙제 카드 {r}")
        r = await E("()=>[...document.querySelectorAll('#sbChips .sbChip')].map(x=>[x.dataset.sbk, x.textContent, x.getBoundingClientRect().height>20])")
        ok(any(x[0] == "gw" and "0/2" in x[1] and x[2] for x in r) and any(x[0] == "hw" and x[2] for x in r), f"위쪽 단추에 📒 문법 숙제 0/2 · 📌 숙제 (눈에 보임) {[x[1] for x in r]}")
        await T.set_viewport_size({"width": 390, "height": 844}); await T.wait_for_timeout(300); await T.screenshot(path=OUT + "kid_ph.png"); await T.set_viewport_size({"width": 820, "height": 1180})
        await E("()=>document.querySelector('#sbChips [data-sbk=gw]').click()"); await T.wait_for_timeout(500)
        r = await E("()=>[GramUI.g && GramUI.g.id, GramUI.mode]"); ok(r[0] == "mid-15" and r[1] == "cards", f"▶ 문법 숙제 하기 → 첫 단원(현재완료) {r}")
        # 현재완료 ★2 · 수동태 ★1 → 1/2 → 서버 보고
        await E("()=>{ Gram.put('mid-15', {s:2}); Gram.put('mid-16', {s:1}); HyHW.reportG(); GramUI.home(); }"); await T.wait_for_timeout(500)
        gid = g[0]["id"]; res = await E("(id)=>FB.get('/hy/hw/res/'+id)", gid)
        ok(res and res.get("k1", {}).get("done") == 1 and res["k1"]["tot"] == 2 and res["k1"]["n"] == "민준", f"진행 보고 1/2 {res}")
        await E("()=>document.querySelector('#stPath [data-hwg]').click()"); await T.wait_for_timeout(400)
        ok(await E("()=>GramUI.g.id") == "mid-16", "다음에는 아직 안 된 단원(수동태)으로")
        await E("()=>{ Gram.put('mid-16', {s:2}); HyHW.reportG(); GramUI.home(); }"); await T.wait_for_timeout(500)
        r = await E("()=>(document.querySelector('#stPath .hwCard.gw .hwDone')||{}).textContent||''"); ok("끝" in r, f"다 하면 🎉 {r}")
        # 지호(토끼반): 자기에게 온 것만
        await E("()=>{ localStorage.setItem('hyeng_me', JSON.stringify({id:'k3', at:Date.now()})); localStorage.removeItem('hyeng_gram_v1'); }"); await E("()=>HyHW.check(true)"); await E("()=>StudyUI.path()"); await T.wait_for_timeout(400)
        r = await E("()=>[...document.querySelectorAll('#stPath .hwCard')].map(x=>x.querySelector('.hwT b').textContent)"); ok(len(r) == 1 and "to부정사" in r[0], f"지호: 자기에게 온 문법 숙제만 {r}")
        # 서연(사자반, 아직 안 함) → 선생님 표
        await E("()=>{ localStorage.removeItem('hyeng_me'); sessionStorage.setItem('hyeng_admin_ok', String(Date.now())); sessionStorage.setItem('hyeng_admin_tk', 'testkey'); }"); await T.reload(); await T.wait_for_timeout(1500)
        await E("(R)=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); window.confirm=()=>true; Online.on=()=>true; Online.submit=o=>Promise.resolve(o.type==='report' ? {ok:true, rep:R.d} : {ok:true}); Notice.fetch=()=>Promise.resolve({v:3, notices:[]}); return Promise.all([HyBoss.refresh(true), Gram.load()]); }", REP)
        await work(); await T.wait_for_timeout(600)
        r = await E("(id)=>{ const el=document.getElementById('adHwRes_'+id); return el ? [...el.querySelectorAll('.hwK')].map(x=>x.querySelector('b').textContent+':'+x.querySelector('small').textContent) : null; }", gid)
        ok(r and "서연:0/2" in r and "민준:✅" in r and not any("지호" in x for x in r), f"선생님 표: 반 아이만 · 안 한 아이도 {r}")
        r = await E("(id)=>{ const el=document.getElementById('adHwRes_'+id); return el ? [...el.querySelectorAll('.hwK')].map(x=>x.querySelector('b').textContent) : null; }", gk[0]["id"])
        ok(r == ["지호"], f"한 아이 숙제 표 = 그 아이만 {r}")
        # 끝내기 → 문법 숙제만 사라지고 나머지는 그대로
        await E("(id)=>document.querySelector('[data-ad=hwEnd][data-id=\"'+id+'\"]').click()", gid); await T.wait_for_timeout(900)
        cur = await E("()=>FB.get('/hy/hw/cur')"); ok(len(cur) == 2 and gid not in cur, f"■ 끝내기 = 그 숙제만 {len(cur)}")
        # 📒 문법별 정답률 (기록 탭)
        await T.click('#adTabs [data-t="rec"]'); await T.wait_for_timeout(900)
        await E("()=>{ document.querySelectorAll('#adBody details').forEach(d=>{ if(/문법별|며칠 뒤/.test(d.textContent)) d.open=true; }); const el=[...document.querySelectorAll('#adBody h3, #adBody summary')].find(x=>/문법별 정답률/.test(x.textContent)); if(el) el.scrollIntoView({block:'start'}); }")
        t = await E("()=>document.getElementById('adBody').innerText")
        ok("문법별 정답률" in t and "45%" in t and "현재완료" in t and "약한 문법" in t, "기록 탭: 📒 문법별 정답률 · 아이별 약한 문법"); await T.screenshot(path=OUT + "rec_pad.png")
        e = real_errs(errs); ok(not e, f"오류 없음 {e[:3]}")
        await b.close()
    g = subprocess.run(["node", os.path.join(os.path.dirname(os.path.abspath(__file__)), "gs_learn650.js")], capture_output=True, text=True); ok(g.returncode == 0, "Code.gs v20 (gs_learn650.js)")
    print("PASS" if not bad else "FAIL", len(bad))
    if bad: sys.exit(1)
asyncio.run(main())
