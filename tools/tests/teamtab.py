"""(v340) 👥 반 탭 — 반 만들기 · 게임 이름 눌러 넣기 · 찾기 · 붙여 넣기 · 옮기기 · 이름 고치기 · 화면이 안 튐 · 게임 이름 = 명단 이름이면 그 기기 자동"""
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
        br = await p.chromium.launch()
        ctx = await br.new_context(viewport={"width": 820, "height": 1180}, is_mobile=True, has_touch=True)
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("dialog", lambda d: asyncio.ensure_future(d.accept("하준이")))
        await boot(pg)
        nicks = ["SEOWON", "MINJUN", "HAJUN", "JIWOO", "DOYUN", "SUA"]
        await pg.evaluate("()=>{ sessionStorage.setItem('hyeng_admin_ok', String(Date.now())); sessionStorage.setItem('hyeng_admin_tk', 'testkey'); }")
        await pg.reload(); await pg.wait_for_timeout(1500)
        await pg.evaluate("()=>{ document.querySelectorAll('.sheet.on').forEach(s=>s.classList.remove('on')); }")
        await pg.evaluate("""(nicks)=>{ Online.on=()=>true; Online.submit=o=>Promise.resolve(o.type==='report' ? {ok:true, rep:{nicks}} : {ok:true}); Notice.fetch=()=>Promise.resolve({v:3, notices:[]});
            sessionStorage.setItem('hyeng_admin_ok', String(Date.now())); sessionStorage.setItem('hyeng_admin_tk', 'testkey'); window.confirm=()=>true; }""", nicks)
        await pg.evaluate("()=>{ Admin.open(); }"); await pg.wait_for_timeout(800)
        await pg.evaluate("()=>document.querySelector('#adTabs [data-t=\"class\"]').click()"); await pg.wait_for_timeout(1200)
        ok(await pg.evaluate("()=>!!document.getElementById('adTeN')"), "👥 반 탭이 있음")
        # 반 두 개 만들기
        for nm, e in (("사자반", "🦁"), ("돌고래반", "🐬")):
            await pg.fill("#adTeN", nm); await pg.select_option("#adTeE", e); await pg.click('[data-ad="teAdd"]'); await pg.wait_for_timeout(500)
        T = await pg.evaluate("()=>Object.values(HyBoss.teams()).map(t=>t.n)")
        ok(sorted(T) == ["돌고래반", "사자반"], f"반 만들기 {T}")
        # 넣을 반 = 마지막에 만든 반 (돌고래반) → 사자반으로 바꿔서 게임 이름 2개 누르기
        await pg.evaluate("()=>{ const s=document.getElementById('adTmTo'); const o=[...s.options].find(o=>o.textContent.indexOf('사자반')>=0); s.value=o.value; s.dispatchEvent(new Event('change')); }")
        n = await pg.evaluate("()=>document.querySelectorAll('#adTmNicks [data-ad=tmAdd]').length")
        ok(n == len(nicks), f"시트 게임 이름이 버튼으로 ({n})")
        await pg.evaluate("()=>{ const sc=document.querySelector('#shAdmin .sheetIn'); sc.scrollTop=400; }")
        top0 = await pg.evaluate("()=>document.querySelector('#shAdmin .sheetIn').scrollTop")
        for nm in ("SEOWON", "MINJUN"):
            await pg.evaluate("(n)=>document.querySelector('#adTmNicks [data-n=\"'+n+'\"]').click()", nm); await pg.wait_for_timeout(400)
        top1 = await pg.evaluate("()=>document.querySelector('#shAdmin .sheetIn').scrollTop")
        K = await pg.evaluate("()=>{ const T=HyBoss.teams(), K=HyBoss.kids(); return Object.values(K).map(k=>k.n+'@'+(T[k.t]||{}).n).sort(); }")
        ok(K == ["MINJUN@사자반", "SEOWON@사자반"], f"누르면 바로 들어감 {K}")
        ok(abs(top1 - top0) < 30, f"넣어도 화면이 안 튐 ({top0}→{top1})")
        dim = await pg.evaluate("()=>document.querySelector('#adTmNicks [data-n=\"SEOWON\"]').classList.contains('in')")
        ok(dim, "이미 넣은 이름은 흐리게")
        # 찾기
        await pg.fill("#adTmQ", "ju"); await pg.wait_for_timeout(200)
        f = await pg.evaluate("()=>[...document.querySelectorAll('#adTmNicks [data-ad=tmAdd]')].map(b=>b.dataset.n)")
        ok(f == ["MINJUN", "HAJUN"] or sorted(f) == ["HAJUN", "MINJUN"], f"찾기 ju → {f}")
        await pg.fill("#adTmQ", ""); await pg.wait_for_timeout(100)
        # 붙여 넣기 → 돌고래반
        await pg.evaluate("()=>{ const s=document.getElementById('adTmTo'); const o=[...s.options].find(o=>o.textContent.indexOf('돌고래반')>=0); s.value=o.value; s.dispatchEvent(new Event('change')); document.getElementById('adTmAdd').open=true; document.querySelector('#adTmMany').closest('details').open=true; }")
        await pg.evaluate("()=>{ document.getElementById('adTmMany').value='JIWOO, DOYUN\\nSUA'; document.querySelector('[data-ad=\"tmMany\"]').click(); }"); await pg.wait_for_timeout(500)
        cnt = await pg.evaluate("()=>{ const T=HyBoss.teams(), K=HyBoss.kids(); return Object.values(K).filter(k=>(T[k.t]||{}).n==='돌고래반').length; }")
        ok(cnt == 3, f"붙여 넣기 3명 ({cnt})")
        # 아이 이름 누르기 → 옮기기 · 이름 고치기
        await pg.evaluate("()=>{ const b=[...document.querySelectorAll('#adTmList [data-ad=tmPick]')].find(b=>b.textContent==='SUA'); b.click(); }"); await pg.wait_for_timeout(300)
        ok(await pg.evaluate("()=>!!document.getElementById('adTmMv')"), "아이 이름 누르면 옮기기·이름·빼기")
        await pg.screenshot(path=OUT + "team_pick.png")
        await pg.evaluate("()=>{ const s=document.getElementById('adTmMv'); const o=[...s.options].find(o=>o.textContent.indexOf('사자반')>=0); s.value=o.value; document.querySelector('[data-ad=tmMv]').click(); }"); await pg.wait_for_timeout(400)
        mv = await pg.evaluate("()=>{ const T=HyBoss.teams(), K=HyBoss.kids(), k=Object.values(K).find(k=>k.n==='SUA'); return (T[k.t]||{}).n; }")
        ok(mv == "사자반", f"반 옮기기 ({mv})")
        await pg.evaluate("()=>{ const b=[...document.querySelectorAll('#adTmList [data-ad=tmPick]')].find(b=>b.textContent==='DOYUN'); b.click(); }"); await pg.wait_for_timeout(200)
        await pg.evaluate("()=>document.querySelector('[data-ad=tmRn]').click()"); await pg.wait_for_timeout(400)
        rn = await pg.evaluate("()=>Object.values(HyBoss.kids()).map(k=>k.n).indexOf('하준이')>=0")
        ok(rn, "이름 고치기")
        # 같은 이름을 다른 반에서 누르면 옮김 (두 번 안 생김)
        await pg.evaluate("()=>{ const s=document.getElementById('adTmTo'); const o=[...s.options].find(o=>o.textContent.indexOf('돌고래반')>=0); s.value=o.value; s.dispatchEvent(new Event('change')); document.querySelector('#adTmNicks [data-n=\"SEOWON\"]').click(); }"); await pg.wait_for_timeout(400)
        r = await pg.evaluate("()=>{ const T=HyBoss.teams(), K=Object.values(HyBoss.kids()).filter(k=>k.n==='SEOWON'); return [K.length, (T[K[0].t]||{}).n]; }")
        ok(r == [1, "돌고래반"], f"이미 있는 이름 → 옮김 {r}")
        await pg.screenshot(path=OUT + "team_tab.png", full_page=False)
        # (v341) 아이 카드 → 기록 · 💎 보내기 · 🎁 다른 것(보내기 칸에 이름) · 접는 칸이 보임
        await pg.evaluate("()=>{ window._posts=[]; Online.submit=o=>{ window._posts.push(o); return Promise.resolve(o.type==='report' ? {ok:true, rep:{nicks:['SEOWON','MINJUN','HAJUN','JIWOO','DOYUN','SUA'], weekly:[['아이','들어온 날','오늘의 30','끝까지','공부(분)','정답률(%)','달리기 판','달리기 최고','짧은 판','새 도감','자주 틀린 단어','지난주보다 (공부)','학부모 문자'],['MINJUN','4','8','7','60','88','5','1200','1','3','apple','+10분','민준이는 잘했어요']]}} : {ok:true}); }; Admin._tab('key'); }")
        await pg.wait_for_timeout(600); await pg.evaluate("()=>Admin._tab('class')"); await pg.wait_for_timeout(800)
        await pg.evaluate("()=>{ const b=document.querySelector('[data-ad=repLoad]'); b && b.click(); }"); await pg.wait_for_timeout(1000)
        await pg.evaluate("()=>{ const b=[...document.querySelectorAll('#adTmList [data-ad=tmPick]')].find(b=>/MINJUN/.test(b.textContent)); b.click(); }"); await pg.wait_for_timeout(400)
        info = await pg.evaluate("()=>{ const i=document.querySelector('.adKidInfo'); return i ? i.innerText : ''; }")
        ok("88%" in info and "학생은 이번 주 4일" in info and "apple" in info, "아이 카드 → 이번 주 기록 · 학부모 문자 " + info[:60].replace("\n"," / "))
        await pg.evaluate("()=>{ window.confirm=()=>true; document.querySelector('.adKidInfo [data-ad=kdGem][data-n=\"30\"]').click(); }"); await pg.wait_for_timeout(500)
        ps = await pg.evaluate("()=>window._posts.filter(p=>p.type==='actAdd')")
        ok(ps and ps[-1]["who"] == "MINJUN" and ps[-1]["value"] == "+30" and ps[-1]["kind"] == "보석", f"💎 +30 보내기 {ps[-1:] }")
        await pg.evaluate("()=>document.querySelector('.adKidInfo [data-ad=kdSend]').click()"); await pg.wait_for_timeout(600)
        w = await pg.evaluate("()=>[(document.getElementById('adWho')||{}).value, document.querySelector('#adTabs .on').dataset.t, (document.querySelector('.adSub .on')||{}).dataset && document.querySelector('.adSub .on').dataset.s]")
        ok(w[:2] == ["MINJUN", "send"], f"🎁 다른 것 → 📢 보내기 탭에 이름 {w}")
        # (v392) 🏫 지금 수업 — 타일 3개 · ⚙ 바꾸기 → 그 설정 칸만 펼침
        await pg.evaluate("()=>Admin._tab('now')"); await pg.wait_for_timeout(500)
        q = await pg.evaluate("()=>document.querySelectorAll('#adBody .adTile').length")
        await pg.evaluate("()=>document.querySelector('#adBody [data-ad=nowEdit][data-k=bt]').click()"); await pg.wait_for_timeout(700)
        t = await pg.evaluate("()=>[document.querySelector('#adTabs .on').dataset.t, !!document.getElementById('adBtSet'), getComputedStyle(document.getElementById('adF_bt')).display!=='none', getComputedStyle(document.getElementById('adF_rd')).display]")
        ok(q == 3 and t == ["now", True, True, "none"], f"지금 수업 타일 {q}개 → ⚙ 바꾸기 = 배틀 칸만 {t}")
        # 접는 칸(더 고르기 · ⓘ)이 보임 · 마지막 고른 값 기억
        vis = await pg.evaluate("()=>[...document.querySelectorAll('#adF_bt details')].map(d=>d.getBoundingClientRect().height>0)")
        ok(vis and all(vis), f"접는 칸 보임 {vis}")
        await pg.evaluate("()=>{ const s=document.getElementById('adBtSet'); s.value='mid'; s.dispatchEvent(new Event('change')); const d=document.getElementById('adBtDur'); d.value='420'; d.dispatchEvent(new Event('change')); Admin._tab('class'); Admin._tab('play'); }"); await pg.wait_for_timeout(500)
        pv = await pg.evaluate("()=>[document.getElementById('adBtSet').value, document.getElementById('adBtDur').value]")
        ok(pv == ["mid", "420"], f"마지막 고른 값 기억 {pv}")
        # 게임 이름 = 명단 이름 → 그 기기는 자동으로 (공용 패드는 아님)
        r = await pg.evaluate("()=>{ Kid.clear(); localStorage.setItem('hyeng_nick','minjun'); const a=Kid.me(); Kid.clear(); localStorage.setItem('hyeng_nick','한양패드'); const b=Kid.me(); localStorage.setItem('hyeng_nick','PLAYER'); Kid.clear(); return [a && (a.rn||a.n), b]; }")   # (v478) 보이는 이름 = 설정 이름 · 명단 이름은 rn
        ok(r == ["MINJUN", None], f"게임 이름이 명단과 같으면 자동 · 공용 패드는 고르기 {r}")
        e = real_errs(errs); print("errs", e[:3]); ok(not e, "오류 없음")
        await br.close()
    print("결과:", "통과" if not bad else "실패 " + str(bad))
asyncio.run(main())
