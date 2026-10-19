"""(v329) 편의성 1~7 + 시험 100문제
   1 쓰러뜨린 보스를 바꿔도 처치 보상 남음 · 2 학년 '🌍 모든 학년' · 3 320×568 첫 화면 스크롤 없음 · 4 유치원 판에서 틀린 단어로 '틀린 단어' 판 = 유치원 판(기회 X)
   5 navy 뜻 · 6 (우리 반 표는 시트가 있어야 해서 함수만) · 7 📌 숙제 (선생님 내기 → 아이 카드·📌·진행 → 서버 → 선생님 표)"""
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
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2)
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)
        E = pg.evaluate
        # 1. 쓰러뜨린 보스 바꾸기 → 보상 그대로
        await E("""()=>{ window.confirm=()=>true; HyBoss.live(); localStorage.setItem('hyeng_nick','한양패드'); return FB.set('/hy/roster', {t:{}, k:{k1:{n:'민준'}}}).then(()=>HyBoss.setup({on:true, team:false, split:'eq', restart:true})); }""")
        await pg.wait_for_timeout(400)
        await E("()=>{ Kid.set({id:'k1',n:'민준',t:'all'}); HyBoss.CAP=1e9; HyBoss.add(Kid.get(), HyBoss.state('all').hp, 'study', 3); }"); await pg.wait_for_timeout(300)
        r = await E("()=>{ const B0=HyBoss.B, g0=HyBoss.reward(Kid.get()); return HyBoss.pickWeek((B0.i+2)%5).then(ok=>[ok, g0, B0.id, HyBoss.B.id, HyBoss.B.n!==B0.n, !!HyBoss.state('all').dead, HyBoss.oldRewards(Kid.get()).map(x=>[x.B.id, x.g])]); }")
        print("swap", r)
        ok(r[0] and r[1] > 0 and r[2] != r[3] and r[4] and not r[5] and r[6] == [[r[2], r[1]]], f"쓰러뜨린 보스 바꿈 → 새 보스 · 옛 보상 남음 {r}")
        g = await E("()=>{ const g0=Wallet.gems(); return HyBoss.claimSafe(Kid.get(), 'o:'+HyBoss.oldRewards(Kid.get())[0].B.id).then(x=>[x, Wallet.gems()-g0]); }")
        ok(g[1] > 0, f"옛 보스 보상 받기 {g}")
        # 2. 학년 칸 이름
        t = await E("()=>document.querySelector('[data-v=\"all\"].tile b').textContent+' '+WORD_SETS.all.label")
        ok(t == "모든 학년 모든 학년", f"학년 칸 '모든 학년' ({t})")
        # 4. 유치원 판에서 틀린 단어
        r = await E("""()=>{ const ws=['cat','dog','sun','hat','pen','cup']; ws.forEach(w=>WrongBook.add(w, true)); const a=HyBoss.easy('wrong', null, ws.map(en=>({en})));
            ws.forEach(w=>WrongBook.add(w, false)); const b=HyBoss.easy('wrong', null, ws.map(en=>({en}))); return [a, b, WrongBook.ez('cat')]; }""")
        ok(r == [True, False, False], f"유치원에서 틀린 단어 판 = 유치원 판 / G1-2 에서 다시 틀리면 아님 {r}")
        # 5. navy
        ok(await E("()=>WORD_BANK.find(w=>w.en==='navy').ko") == "남색, 해군", "navy 뜻 = 남색, 해군")
        # 시험 100문제
        n = await E("()=>{ const c={set:'g56', from:0, to:20, n:100, seed:7}; return Study.examWords(c).length; }")
        ok(n == 100, f"시험 100문제 단어 {n}")
        # 7. 📌 숙제 — 선생님 내기 (관리 화면)
        await E("()=>{ sessionStorage.setItem('hyeng_admin_ok',String(Date.now())); sessionStorage.setItem('hyeng_admin_tk','testkey'); }"); await pg.reload(); await pg.wait_for_timeout(1500)
        await E("()=>{ window.confirm=()=>true; Kid.set({id:'k1',n:'민준',t:'all'}); Admin.open(); }"); await pg.wait_for_timeout(400)
        await E("()=>document.querySelector('#adTabs [data-t=\"exam\"]').click()"); await pg.wait_for_timeout(700)
        await E("()=>{ const s=document.getElementById('adHwSet'); s.value='elem'; s.dispatchEvent(new Event('change')); document.getElementById('adHwTo').value='3'; document.getElementById('adHwGoal').value='1'; }")
        await pg.screenshot(path=OUT + "hw_admin.png")
        await E("()=>document.querySelector('[data-ad=\"hwOpen\"]').click()"); await pg.wait_for_timeout(500)
        c = await E("()=>FB.get('/hy/hw/cur').then(v=>v ? Object.values(v)[0] : null)")   # (v348) 반마다 숙제 — /hy/hw/cur = {<id>: 숙제}
        ok(c and c["on"] and c["set"] == "elem" and c["from"] == 0 and c["to"] == 3 and c["goal"] == 1 and c["due"] > 0, f"숙제 냄 {c and c['title']}")
        # 아이 화면
        await E("()=>{ document.querySelectorAll('.sheet.on').forEach(s=>s.classList.remove('on')); return HyHW.check(true); }")
        await E("()=>{ StudyUI.open(); StudyUI.book='g34'; StudyUI.set='elem'; StudyUI.path(); }"); await pg.wait_for_timeout(400)
        card = await E("()=>{ const c=document.querySelector('.hwCard'); return c ? c.innerText : ''; }")
        pins = await E("()=>document.querySelectorAll('#stMap .stDot.hw').length")
        print("card", card.replace("\n", " / "), "pins", pins)
        ok("숙제" in card and "0 / 4" in card and "숙제 하기" in card, "아이 Daily 30 맨 위 📌 숙제 카드")
        ok(pins == 4, f"범위 Stage 에 📌 {pins}")
        await pg.screenshot(path=OUT + "hw_kid.png")
        # 다른 책을 보고 있어도 ▶ 숙제 하기 → 그 책 · 첫 Stage 창
        await E("()=>{ StudyUI.book='mid'; StudyUI.set='mid'; StudyUI.path(); }"); await pg.wait_for_timeout(200)
        await E("()=>document.querySelector('[data-hw=\"go\"]').click()"); await pg.wait_for_timeout(300)
        r = await E("()=>[StudyUI.set, document.getElementById('stPop').classList.contains('on'), document.getElementById('stPop').innerText.slice(0,40)]")
        ok(r[0] == "elem" and r[1] and "1-1" in r[2], f"숙제 하기 → G3-4 첫 Stage {r}")
        # 두 Stage 끝냄 → 진행 · 서버
        await E("()=>{ const L=Study.lessons('elem'); Study.setLv('elem', L[0].n, 1); Study.setLv('elem', L[1].n, 1); StudyUI.pop(null); StudyUI.path(); }"); await pg.wait_for_timeout(400)
        card = await E("()=>document.querySelector('.hwCard').innerText")
        ok("2 / 4" in card, f"진행 2/4 ({card[:60]!r})")
        res = await E("()=>FB.get('/hy/hw/res/'+HyHW.c.id)")
        ok(res and res.get("k1", {}).get("done") == 2 and res["k1"]["tot"] == 4 and res["k1"]["n"] == "민준", f"아이 진행 → 서버 {res}")
        # 다 끝냄
        await E("()=>{ const L=Study.lessons('elem'); [2,3].forEach(i=>Study.setLv('elem', L[i].n, 1)); StudyUI.path(); }"); await pg.wait_for_timeout(300)
        card = await E("()=>document.querySelector('.hwCard').innerText")
        ok("숙제 끝" in card and await E("()=>document.querySelectorAll('#stMap .stDot.hw').length") == 0, "다 하면 🎉 숙제 끝 · 📌 사라짐")
        # 선생님 표 · 끝내기
        await E("()=>{ Admin.open(); }"); await pg.wait_for_timeout(300)
        await E("()=>document.querySelector('#adTabs [data-t=\"exam\"]').click()"); await pg.wait_for_timeout(800)
        tb = await E("()=>{ const e=document.querySelector('[id^=adHwRes_]'); return e ? e.innerText : ''; }")
        ok("민준" in tb and "✅" in tb and "다 함 1" in tb, f"선생님 숙제 표 {tb[:60]!r}")
        await pg.screenshot(path=OUT + "hw_admin_res.png")
        tabs = await E("()=>{ const t=[...document.querySelectorAll('#adTabs button')].map(b=>b.getBoundingClientRect().top); return [t.length, new Set(t.map(Math.round)).size]; }")
        ok(tabs == [6, 1], f"관리 탭 한 줄 {tabs}")
        await E("()=>document.querySelector('[data-ad=\"hwEnd\"]').click()"); await pg.wait_for_timeout(400)
        ok(not await E("()=>FB.get('/hy/hw/cur')"), "숙제 끝내기")
        ok(not errs, "오류 없음 " + str(errs[:3]))
        await ctx.close()
        # 3. 320×568 첫 화면 (이어서 하기 버튼까지)
        ctx2 = await br.new_context(viewport={"width": 320, "height": 568}, device_scale_factor=2, is_mobile=True, has_touch=True)
        await ctx2.add_init_script("window.HY_FB_LOCAL=true;")
        p2 = await ctx2.new_page(); await boot(p2)
        await p2.evaluate("()=>{ const r=document.getElementById('btnResume'); r.style.display=''; r.innerHTML='<span>이어서 하기</span><small style=\"display:block\">Adventure · NORMAL</small>'; }"); await p2.wait_for_timeout(200)
        r = await p2.evaluate("()=>{ const s=document.getElementById('scStart'); return [s.scrollHeight, s.clientHeight]; }")
        ok(r[0] <= r[1] + 2, f"320×568 스크롤 없음 {r}")
        await p2.screenshot(path=OUT + "home_320.png")
        await br.close()
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)

asyncio.run(main())
