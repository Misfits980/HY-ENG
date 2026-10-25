"""(v395) 사용자: 관리 화면 더 간소화 · 편의성 · 기능 — 📡 수업 중 리모컨(다른 기기에서 시작·끝·한 판 더·멈춤 · 들어온/안 들어온 아이 · 💎) ·
   ⭐ 즐겨찾기 수업 · 🕘 최근 · 반 고르기 = 공용 패드 반 · 👥 아이 찾기 · 💎 두 번 누르기 · ☑ 여러 명 보석 · ⚡ 다음 숙제 · 📝 숙제 범위로 시험 · 보내기 빠른 칸 — HY_FB_LOCAL"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

ROSTER = """()=>{ FB.set('/hy/roster/t/ta',{n:'사자반',e:'🦁'}); FB.set('/hy/roster/t/tb',{n:'돌고래반',e:'🐬'});
  ['민준','서연','하준','지우'].forEach((n,i)=>FB.set('/hy/roster/k/k'+i,{n,t:'ta'})); ['도윤','수아','하린'].forEach((n,i)=>FB.set('/hy/roster/k/j'+i,{n,t:'tb'})); }"""

async def admin(ctx, vp, errs):
    pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append("A " + str(e)))
    await pg.set_viewport_size(vp); await boot(pg)
    await pg.evaluate("()=>{ sessionStorage.setItem('hyeng_admin_ok', String(Date.now())); sessionStorage.setItem('hyeng_admin_tk', 'testkey'); }")
    await pg.reload(); await pg.wait_for_timeout(1500)
    await pg.evaluate("()=>{ document.querySelectorAll('.sheet.on').forEach(s=>s.classList.remove('on')); }")
    await pg.evaluate("""()=>{ Online.on=()=>true; window._posts=[]; Online.submit=o=>{ window._posts.push(o); return Promise.resolve(o.type==='report' ? {ok:true, rep:{nicks:[], weekly:[['아이','들어온 날','오늘의 30','끝까지','공부(분)','정답률(%)','달리기 판','달리기 최고','짧은 판','새 도감','자주 틀린 단어','지난주보다 (공부)','학부모 문자'],['민준','4','8','7','60','88','5','1200','1','3','apple','+10분','민준이는 잘했어요'],['서연','2','3','2','20','75','1','500','0','1','pear','-','서연이도 잘했어요']]}} : {ok:true}); };
      Notice.fetch=()=>Promise.resolve({v:3, notices:[]}); sessionStorage.setItem('hyeng_admin_ok', String(Date.now())); sessionStorage.setItem('hyeng_admin_tk', 'testkey'); window.confirm=()=>true; window.prompt=(a,b)=>b;
      window._clip=''; try{ navigator.clipboard.writeText=t=>{ window._clip=t; return Promise.resolve(); }; }catch(e){} }""")
    return pg

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(); ctx = await br.new_context(has_touch=True); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        tv = await ctx.new_page(); tv.on("pageerror", lambda e: errs.append("TV " + str(e))); await tv.set_viewport_size({"width": 1280, "height": 720}); await boot(tv)
        await tv.evaluate(ROSTER); await tv.wait_for_timeout(400)
        pg = await admin(ctx, {"width": 390, "height": 844}, errs)
        await pg.evaluate("()=>Admin.open()"); await pg.wait_for_timeout(1200)
        # ── 반 고르기 = 공용 패드 반 ──
        await pg.click('[data-ad="nowCls"][data-c="ta"]'); await pg.wait_for_timeout(700)
        ok(await pg.evaluate("()=>HyBoss.nowT()") == "ta", "반 고르기 → 공용 패드 반 (지금 수업)")
        ok("사자반" in await pg.evaluate("()=>(document.querySelector('.adClsSub')||{}).innerText||''"), "📱 공용 패드 줄")
        # ── ⭐ 즐겨찾기 저장 → 칩 ──
        await pg.click('[data-ad="nowEdit"][data-k="bt"]'); await pg.wait_for_timeout(500)
        await pg.click('#adF_bt [data-ad="favSave"]'); await pg.wait_for_timeout(800)
        F = await pg.evaluate("()=>Object.values((HyBoss.R||{}).fav||{})")
        ok(len(F) == 1 and F[0]["k"] == "bt" and F[0]["o"]["cls"] == "ta" and "사자반" in F[0]["nm"], f"⭐ 즐겨찾기 저장 {[f['nm'] for f in F]}")
        ok(await pg.evaluate("()=>document.querySelectorAll('.adFavC.fav').length") == 1, "⭐ 칩이 지금 수업 탭에")
        # ── 📡 TV 기기에서 방 (즐겨찾기 설정 그대로) → 폰 리모컨 ──
        o = F[0]["o"]
        await tv.evaluate("(o)=>Battle.host(o, '4321')", o); await tv.wait_for_timeout(800)
        kid = await ctx.new_page(); kid.on("pageerror", lambda e: errs.append("K " + str(e))); await kid.set_viewport_size({"width": 390, "height": 844}); await boot(kid)
        await kid.evaluate("()=>Battle.join('4321', {id:'k0', n:'민준', t:'ta'})"); await kid.wait_for_timeout(900)
        await pg.wait_for_timeout(1200)
        t = await pg.evaluate("()=>($('adRemote')||{}).innerText||''")
        ok("4321" in t and "민준" in t and "아직 안 들어옴 3명" in t, "📡 리모컨: 방 · 들어온 아이 · 안 들어온 아이 " + t.replace("\n", " | ")[:160])
        await pg.click('[data-ad="rmCmd"][data-c="start"]'); await tv.wait_for_timeout(2200)
        ok(await tv.evaluate("()=>Battle.st().s") in ("count", "run"), "📡 폰에서 ▶ 시작 → TV 시작")
        await pg.wait_for_timeout(800); await pg.click('[data-ad="rmCmd"][data-c="end"]'); await pg.wait_for_timeout(300)
        ok(await tv.evaluate("()=>Battle.st().s") != "end" and await pg.evaluate("()=>!!document.querySelector('.adRmB.armed')"), "⏹ 끝내기는 두 번 누르기 (한 번은 안 끝남)")
        await pg.click('[data-ad="rmCmd"][data-c="end"]'); await tv.wait_for_timeout(2200)
        ok(await tv.evaluate("()=>Battle.st().s") == "end", "📡 두 번 → TV 끝")
        await pg.wait_for_timeout(800); await pg.click('[data-ad="rmCmd"][data-c="again"]'); await tv.wait_for_timeout(2200)
        ok(await tv.evaluate("()=>[Battle.st().s, Battle.st().rnd]") == ["wait", 1], "📡 🔁 한 판 더 → TV 새 판")
        await pg.wait_for_timeout(600)
        await pg.click('[data-ad="rmGem"]'); await pg.wait_for_timeout(200); await pg.click('[data-ad="rmGem"]'); await pg.wait_for_timeout(500)
        P = await pg.evaluate("()=>window._posts.filter(o=>o.type==='actAdd')")
        ok(len(P) == 1 and P[0]["who"] == "민준" and P[0]["value"] == "+10", f"📡 아이 두 번 눌러 💎+10 {P}")
        await pg.screenshot(path=OUT + "admin395_remote.png")
        # 레이드 — 멈춤 · 계속
        await tv.evaluate("()=>Battle.leave()"); await tv.wait_for_timeout(600)
        ok(await pg.evaluate("()=>LiveRoom.list().map(x=>x.r)") == [], "TV 가 닫으면 목록에서 빠짐")
        await tv.evaluate("()=>Raid.host('g34', [], 1, '5555', 900, 'ta')"); await tv.wait_for_timeout(1500)
        await pg.click('[data-ad="rmCmd"][data-r="5555"][data-c="start"]'); await tv.wait_for_timeout(2000)
        await pg.wait_for_timeout(900); await pg.click('[data-ad="rmCmd"][data-r="5555"][data-c="pause"]'); await tv.wait_for_timeout(2000)
        ok(await tv.evaluate("()=>Raid.st().s") == "pause", "📡 레이드 ⏸ 멈춤")
        await pg.wait_for_timeout(900); await pg.click('[data-ad="rmCmd"][data-r="5555"][data-c="plus"]'); await tv.wait_for_timeout(2000)
        ok(await tv.evaluate("()=>Raid.st().ex|0") == 180000, "📡 레이드 ➕ 3분")
        await tv.evaluate("()=>Raid.leave()"); await tv.wait_for_timeout(500)
        # ── ⭐ 누르면 바로 시작 (이 기기가 TV) · 🕘 최근 ──
        await pg.evaluate("()=>{ Admin.open(); Admin._tab('now'); }"); await pg.wait_for_timeout(800)
        await pg.click('.adFavC.fav [data-ad="favGo"]'); await pg.wait_for_timeout(1500)
        ok(await pg.evaluate("()=>[Battle.role, Battle.cfg().cls]") == ["host", "ta"], "⭐ 한 번 누르면 그 설정 그대로 방")
        ok(len(await pg.evaluate("()=>JSON.parse(localStorage.getItem('hyeng_admin_recent')||'[]')")) == 1, "🕘 최근에 남음")
        await pg.evaluate("()=>Battle.leave()"); await pg.wait_for_timeout(500)
        await pg.evaluate("()=>{ Admin.open(); Admin._tab('now'); }"); await pg.wait_for_timeout(800)
        await pg.click('[data-ad="favEdit"]'); await pg.click('[data-ad="favDel"]'); await pg.wait_for_timeout(600)
        ok(await pg.evaluate("()=>Object.keys((HyBoss.R||{}).fav||{}).length") == 0, "⭐ 빼기")
        await pg.evaluate("()=>document.querySelector('#adMsg [data-ad=undo]').click()"); await pg.wait_for_timeout(600)
        ok(await pg.evaluate("()=>Object.keys((HyBoss.R||{}).fav||{}).length") == 1, "⭐ 되돌리기")
        # ── 👥 아이들 ──
        await pg.evaluate("()=>Admin._tab('class')"); await pg.wait_for_timeout(1200)
        await pg.fill("#adKQ", "서"); await pg.wait_for_timeout(300)
        ok(await pg.evaluate("()=>[...document.querySelectorAll('#adTmList .kcW b')].map(b=>b.textContent)") == ["서연"], "🔍 아이 찾기")
        await pg.fill("#adKQ", ""); await pg.wait_for_timeout(300)
        n0 = await pg.evaluate("()=>window._posts.filter(o=>o.type==='actAdd').length")
        await pg.click('[data-ad="kdGem1"][data-k="k1"]'); await pg.wait_for_timeout(200)
        ok(await pg.evaluate("()=>window._posts.filter(o=>o.type==='actAdd').length") == n0, "💎 한 번은 안 보냄")
        await pg.click('[data-ad="kdGem1"][data-k="k1"]'); await pg.wait_for_timeout(500)
        P = await pg.evaluate("()=>window._posts.filter(o=>o.type==='actAdd').slice(-1)[0]")
        ok(P["who"] == "서연" and P["value"] == "+10", f"💎 두 번 → +10 {P}")
        await pg.click('[data-ad="selMode"]'); await pg.wait_for_timeout(400)
        for k in ("k0", "k2", "j1"): await pg.click(f'[data-ad="tmPick"][data-k="{k}"]'); await pg.wait_for_timeout(120)
        await pg.click('[data-ad="selGem"][data-n="30"]'); await pg.wait_for_timeout(1200)
        P = await pg.evaluate("()=>window._posts.filter(o=>o.type==='actAdd' && o.value==='+30').map(o=>o.who)")
        ok(sorted(P) == sorted(["민준", "하준", "수아"]), f"☑ 여러 명 💎+30 {P}")
        await pg.evaluate("()=>Admin._tab('class')"); await pg.wait_for_timeout(1500)
        b = await pg.evaluate("()=>{ const b=document.querySelector('[data-ad=copyAllTxt]'); if(!b) return null; b.click(); return b.textContent; }"); await pg.wait_for_timeout(300)
        ok(b is not None and "민준이는 잘했어요" in await pg.evaluate("()=>window._clip") and "서연이도" in await pg.evaluate("()=>window._clip"), "💬 학부모 문자 모두 복사")
        # ── 📝 다음 숙제 · 숙제 범위로 시험 ──
        await pg.evaluate("()=>FB.set('/hy/hw/cur', {ha:{id:'ha', on:1, team:'ta', set:'elem', from:0, to:3, goal:3, due:Date.now()+3*864e5, title:'초등 1~4', at:1}})"); await pg.wait_for_timeout(300)
        await pg.evaluate("()=>Admin._tab('work')"); await pg.wait_for_timeout(1500)
        ok("사자반" in await pg.evaluate("()=>(document.querySelector('.hwNext')||{}).innerText||''"), "⚡ 다음 숙제 카드")
        await pg.click('[data-ad="hwNext"][data-team="ta"]'); await pg.wait_for_timeout(1500)
        H = await pg.evaluate("()=>HyHW.L.map(c=>[c.team,c.from,c.to,c.goal])")
        ok(H == [["ta", 4, 7, 3]], f"⚡ 다음 숙제 = 바로 다음 4칸 {H}")
        ok(await pg.evaluate("()=>((HyBoss.R||{}).hwl||{}).ta && HyBoss.R.hwl.ta.from") == 4, "지난 숙제 범위 기억 (hwl)")
        await pg.evaluate("()=>document.querySelector('[data-ad=hwExam]').click()"); await pg.wait_for_timeout(500)
        ok(await pg.evaluate("()=>[adExTeam.value, adExSet.value, adExFrom.value, adExTo.value]") == ["ta", "elem", "4", "7"], "📝 숙제 범위로 시험 칸 채움")
        # ── 📢 보내기 빠른 칸 ──
        await pg.evaluate("()=>Admin._tab('send')"); await pg.wait_for_timeout(800)
        await pg.evaluate("()=>{ adKind.value='선물'; adKind.dispatchEvent(new Event('change')); }")
        await pg.click('[data-ad="valQ"][data-v="+50"]'); await pg.click('[data-ad="memoQ"]')
        r = await pg.evaluate("()=>[adKind.value, adVal.value, !!adMemo.value]")
        ok(r == ["보석", "+50", True], f"💎 빠른 칸 {r}")
        ok(not [e for e in errs], f"오류 없음 {errs[:3]}")
        await br.close()
    print("ALL OK" if not bad else "BAD " + str(bad))
    sys.exit(1 if bad else 0)
asyncio.run(main())
