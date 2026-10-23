"""(v387) ① 끌기 문제 그림자 조각이 다음 카드 위에 남던 버그 (두 손가락 · 손가락 신호 끊김 · 문제가 넘어감)
   ② 🗒 오늘 할 일 (관리 🏠 홈 맨 위) ③ 📱 공용 패드 이름 빼기 ④ 🎁 보스 보상 현황표 — HY_FB_LOCAL (이 기기 안 Firebase 흉내)"""
import asyncio, sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

PD = """(o)=>{ const ch=document.querySelector('.dgChip[data-en="'+o.en+'"]'), r=ch.getBoundingClientRect();
  ch.dispatchEvent(new PointerEvent(o.t, {pointerId:o.id, bubbles:true, cancelable:true, clientX:r.left+5+(o.dx||0), clientY:r.top+5+(o.dy||0), pointerType:'touch', isPrimary:o.id===1})); }"""

async def find_drag(pg):
    for book, st in (("g12", "basic"), ("g34", "elem"), ("g12", "basic2")):
        for n in range(4):
            await pg.evaluate("(a)=>{ StudyUI.book=a[0]; StudyUI.set=a[1]; StudyUI.path(); StudyUI.start(a[2], false); }", [book, st, n]); await pg.wait_for_timeout(150)
            for i in range(160):
                t = await pg.evaluate("()=>{ const U=StudyUI, q=U.qs[U.i]; return q && !U.locked && !U._brk ? q.t : null; }")
                if t == "drag": return True
                if await pg.evaluate("()=>document.getElementById('stDone').style.display!=='none'"): break
                await pg.evaluate(SOLVE, False); await pg.wait_for_timeout(10)
    return False

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch()
        # ── ① 끌기 그림자 ──
        pg = await br.new_page(viewport={"width": 820, "height": 1180}, is_mobile=True, has_touch=True)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await boot(pg)
        await pg.evaluate("()=>StudyUI.open()"); await pg.wait_for_timeout(1200)
        found = await find_drag(pg)
        ok(found, "끌기 문제를 찾음")
        if found:
            ens = await pg.evaluate("()=>StudyUI.qs[StudyUI.i].ws.map(w=>w.en)")
            # 두 손가락: 조각 두 개를 동시에 누름 → 그림자는 하나만
            await pg.evaluate(PD, {"en": ens[0], "t": "pointerdown", "id": 1})
            await pg.evaluate(PD, {"en": ens[1], "t": "pointerdown", "id": 2})
            n2 = await pg.evaluate("()=>document.querySelectorAll('.dgChip.ghost').length")
            ok(n2 == 1, f"두 손가락으로 눌러도 그림자 하나 ({n2})")
            await pg.evaluate(PD, {"en": ens[1], "t": "pointerup", "id": 2})
            await pg.evaluate(PD, {"en": ens[0], "t": "pointermove", "id": 1, "dx": 40, "dy": 40})
            await pg.evaluate(PD, {"en": ens[0], "t": "pointerup", "id": 1, "dx": 40, "dy": 40})
            n3 = await pg.evaluate("()=>document.querySelectorAll('.dgChip.ghost').length")
            ok(n3 == 0, f"손 떼면 그림자 없음 ({n3})")
            # 끄는 중에 손가락 신호가 끊김(pointerup 없음) → 잃어버린 손가락 신호로 정리
            await pg.evaluate(PD, {"en": ens[0], "t": "pointerdown", "id": 3})
            await pg.evaluate("(en)=>document.querySelector('.dgChip[data-en=\"'+en+'\"]').dispatchEvent(new PointerEvent('lostpointercapture', {pointerId:3, bubbles:true}))", ens[0]); await pg.wait_for_timeout(50)
            n4 = await pg.evaluate("()=>document.querySelectorAll('.dgChip.ghost').length")
            ok(n4 == 0, f"손가락 신호가 끊겨도 그림자 없음 ({n4})")
            # 끄는 중에 문제가 넘어감 → 다음 카드 위에 그림자 없음 (사진: mice 카드 위에 bite)
            await pg.evaluate(PD, {"en": ens[0], "t": "pointerdown", "id": 4})
            await pg.evaluate(SOLVE, False); await pg.wait_for_timeout(500)
            for i in range(6):
                if await pg.evaluate("()=>{ const q=StudyUI.qs[StudyUI.i]; return !q || q.t!=='drag'; }"): break
                await pg.evaluate(SOLVE, False); await pg.wait_for_timeout(450)
            n5 = await pg.evaluate("()=>document.querySelectorAll('.dgChip.ghost').length")
            ok(n5 == 0, f"다음 문제로 넘어가면 그림자 없음 ({n5})")
            await pg.screenshot(path=OUT + "a387_after_drag.png")
            # 길로 나가도
            await pg.evaluate("()=>{ const g=document.createElement('div'); g.className='dgChip ghost'; g.textContent='bite'; document.body.appendChild(g); StudyUI.view('stPath'); }")
            ok(await pg.evaluate("()=>document.querySelectorAll('.dgChip.ghost').length") == 0, "길로 나가면 남은 그림자 지움")
        await pg.close()

        # ── ②③④ 관리 화면 ──
        ctx = await br.new_context(viewport={"width": 820, "height": 1180}, is_mobile=True, has_touch=True)
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        T = await ctx.new_page(); T.on("pageerror", lambda e: errs.append("T " + str(e)))
        await boot(T); E = T.evaluate
        await E("()=>{ sessionStorage.setItem('hyeng_admin_ok', String(Date.now())); sessionStorage.setItem('hyeng_admin_tk', 'testkey'); }")
        await T.reload(); await T.wait_for_timeout(1500); await E("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); }")
        await E("()=>{ sessionStorage.setItem('hyeng_admin_ok', String(Date.now())); sessionStorage.setItem('hyeng_admin_tk', 'testkey'); window.confirm=()=>true;"
                " Online.on=()=>true; Online.submit=o=>Promise.resolve(o.type==='report' ? {ok:true, rep:{nicks:[]}} : {ok:true}); Notice.fetch=()=>Promise.resolve({v:3, notices:[]}); }")
        await E("()=>HyBoss.live()")
        roster = {"t": {"a": {"n": "사자반", "e": "🦁"}}, "k": {
            "k1": {"n": "민준", "t": "a"}, "k2": {"n": "서연", "t": "a"}, "k3": {"n": "지호", "t": "a"}, "k4": {"n": "하윤", "t": "a"},
            "p1": {"n": "한양 나눔", "t": "a"}, "p2": {"n": "한양 정직"}}}
        await E("(r)=>FB.set('/hy/roster', r).then(()=>HyBoss.setup({on:true, team:false, split:'eq', restart:true}))", roster); await T.wait_for_timeout(500)
        # 민준·서연 3번 이상 · 지호 1번 · 하윤 안 싸움 → 쓰러뜨림 → 민준만 받음
        await E("()=>{ HyBoss.CAP=1e9; HyBoss.add({id:'k1',n:'민준',t:'a'}, 300, 'study', 4); HyBoss.add({id:'k3',n:'지호',t:'a'}, 10, 'study', 1);"
                " HyBoss.add({id:'k2',n:'서연',t:'a'}, HyBoss.state('all').hp, 'study', 5); HyBoss.CAP=400; }"); await T.wait_for_timeout(3600)
        dead = await E("()=>!!HyBoss.state('all').dead")
        ok(dead, "보스 쓰러뜨림")
        g1 = await E("()=>{ Kid.set({id:'k1',n:'민준',t:'a'}); return HyBoss.claimSafe(Kid.get()); }")
        ok(g1 and g1 > 0, f"민준 보상 받음 💎{g1}")
        await T.wait_for_timeout(300)
        rows = await E("()=>HyBoss.rwRows(HyBoss.B, HyBoss.D).map(r=>r.n+':'+r.st+':'+r.g)")
        st = {r.split(":")[0]: r.split(":")[1] for r in rows}
        ok(st.get("민준") == "got" and st.get("서연") == "wait" and st.get("지호") == "sw" and st.get("하윤") == "none" and "한양 나눔" not in st, f"현황 계산 {rows}")
        # 숙제 오늘 마감
        await E("()=>FB.set('/hy/hw/cur', {h1:{id:'h1', on:true, set:'elem', from:0, to:2, goal:1, title:'1~3 Stage', due:Date.now()+3600e3, at:Date.now()}})")
        # 관리 열기 → 🏠 홈
        await E("()=>{ document.querySelectorAll('.sheet.on').forEach(s=>s.classList.remove('on')); Admin.open(); Admin._tab('class'); }"); await T.wait_for_timeout(1500)
        td = await E("()=>{ const t=document.getElementById('adTodo'); return t ? t.innerText : ''; }")
        print("   todo:", td.replace("\n", " / ")[:300])
        ok("오늘 할 일" in td, "👥 아이들 맨 위 「오늘 할 일」")
        ok("보스 보상을 안 받은 아이 1명" in td and "서연" in td, "할 일: 보스 보상 안 받은 아이 (서연)")
        ok("공용 패드 이름이 2개" in td, "할 일: 공용 패드 이름 2개")
        ok("숙제" in td and "오늘 마감" in td, "할 일: 숙제 오늘 마감")
        top = await E("()=>{ const t=document.getElementById('adTodo'), q=document.getElementById('adTmList'); return !!(t && q && (t.compareDocumentPosition(q) & Node.DOCUMENT_POSITION_FOLLOWING)); }")
        ok(top, "(v392) 👥 아이들 맨 위 = 오늘 할 일 (반 명단보다 위)")
        n = await E("()=>(document.querySelector('#adTabs [data-t=class] .adTabN')||{}).textContent||''")
        ok(n.isdigit() and int(n) >= 3, f"(v392) 👥 아이들 탭에 할 일 수 {n!r}")
        await T.screenshot(path=OUT + "a387_todo.png")
        # 📱 빼기 — 두 번 눌러야
        await E("()=>document.querySelector('#adTodo [data-ad=padClean]').click()"); await T.wait_for_timeout(200)
        still = await E("()=>HyBoss.padKids().length")
        ok(still == 2, f"한 번 누르면 아직 안 지움 ({still})")
        await E("()=>document.querySelector('#adTodo [data-ad=padClean]').click()"); await T.wait_for_timeout(600)
        left = await E("()=>[HyBoss.padKids().length, Object.keys(HyBoss.kids()).length]")
        ok(left == [0, 4], f"두 번 누르면 패드 이름만 빠짐 {left}")
        td2 = await E("()=>document.getElementById('adTodo').innerText")
        ok("공용 패드" not in td2, "빼고 나면 할 일에서 사라짐")
        ok(await E("()=>/되돌리기/.test(document.getElementById('adMsg').innerHTML)"), "↩️ 되돌리기 있음")
        # 현황표로 가기
        await E("()=>[...document.querySelectorAll('#adTodo [data-ad=go]')].find(b=>b.dataset.t==='boss').click()"); await T.wait_for_timeout(900)
        rw = await E("()=>{ const e=document.getElementById('adBossRw'); return e ? e.innerText : ''; }")
        print("   rw:", rw.replace("\n", " / ")[:400])
        ok("받음 1" in rw and "안 받음 1" in rw and "3번 못 채움 1" in rw, "현황표 요약 (받음 1 · 안 받음 1 · 3번 못 채움 1)")
        trs = await E("()=>[...document.querySelectorAll('#adBossRw tr')].slice(1).map(r=>[...r.cells].map(c=>c.innerText.trim()))")
        ok(len(trs) == 4 and trs[0][0] == "서연" and "안 받음" in trs[0][5] and any(r[0] == "민준" and "받음" in r[5] and r[4].startswith("💎") for r in trs) and any(r[0] == "하윤" and r[2] == "-" for r in trs), f"표: 안 받은 아이 먼저 · 받은 💎 {trs}")
        ok("서연" in await E("()=>(document.querySelector('#adBossRw .rwTell')||{}).innerText||''"), "안 받은 아이에게 알려 줄 말")
        await T.screenshot(path=OUT + "a387_boss_rw.png", full_page=False)
        await E("()=>document.getElementById('adBossRw').scrollIntoView()"); await T.wait_for_timeout(200)
        await T.screenshot(path=OUT + "a387_boss_rw2.png")
        # 서연이 받으면 표가 바로 바뀜
        await E("()=>{ Kid.set({id:'k2',n:'서연',t:'a'}); return HyBoss.claimSafe(Kid.get()); }"); await T.wait_for_timeout(900)
        rw2 = await E("()=>document.getElementById('adBossRw').innerText")
        ok("받음 2" in rw2 and "안 받음 0" in rw2, "받으면 표가 바로 바뀜")
        await E("()=>Admin._tab('class')"); await T.wait_for_timeout(700)
        td3 = await E("()=>document.getElementById('adTodo').innerText")
        ok("보스 보상" not in td3, "다 받으면 할 일에서 사라짐")
        # 휴대폰 화면 — 가로로 넘치지 않음
        await T.set_viewport_size({"width": 375, "height": 800}); await T.wait_for_timeout(300)
        ov = await E("()=>{ const t=document.getElementById('adTodo'); return t.scrollWidth<=t.clientWidth+1; }")
        ok(ov, "휴대폰 폭에서 할 일 카드가 넘치지 않음")
        await T.screenshot(path=OUT + "a387_todo_phone.png")
        # 할 일이 없으면 ✅
        await E("()=>FB.set('/hy/hw/cur', null).then(()=>HyHW.check(true))"); await E("()=>Admin._tab('class')"); await T.wait_for_timeout(900)
        td4 = await E("()=>document.getElementById('adTodo').innerText")
        ok("손볼 것이 없어요" in td4, f"할 일 없으면 ✅ ({td4[:60]!r})")
        # 👥 우리 반 — 패드 이름 경고 막대
        await E("()=>FB.update('/hy/roster/k/p9', {n:'한양 배려'})"); await E("()=>Admin._tab('class')"); await T.wait_for_timeout(900)
        ok(await E("()=>/공용 패드 이름이 아이처럼/.test(document.getElementById('adTmList').innerText)"), "👥 우리 반에도 패드 이름 빼기")
        await br.close()
    errs = real_errs(errs)
    ok(not errs, f"에러 없음 {errs[:3]}")
    print("\nFAILED:", bad) if bad else print("\nALL OK")
    sys.exit(1 if bad else 0)

asyncio.run(main())
