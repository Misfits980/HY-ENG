"""(v728) 📱 관리 화면 휴대폰 — 아래 탭 5개(🏠 오늘 · ⚔️ 수업 · 👥 아이들 · 🎯 기록 · ☰ 더보기) · 연결 점 · 🏠 오늘 숫자 · 아이 한 줄 · 아이 자세히 한 장 · 예전 모양으로
   사용자: 「패드뿐만 아니라 난 휴대폰으로 확인을 많이 해」 · (이름은 지어낸 별명)"""
import asyncio, sys, os
os.environ["HY_ADM_PH"] = "1"          # 이 시험만 휴대폰 모양 (harness 기본 = 예전 탭)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

SEED = """()=>FB.ready().then(()=>{ const now=Date.now(), dk=HyDay.key(), yk=HyDay.key(now-864e5);
  return Promise.all([
    FB.set('/hy/roster', {k:{r1:{n:'토토',t:'t1'}, r2:{n:'별사탕',t:'t1'}, r3:{n:'콩콩',t:'t1'}, r4:{n:'몽글',t:'t2'}}, t:{t1:{n:'3반',e:'🐬'}, t2:{n:'4반',e:'🦊'}}}),
    FB.set('/hy/day/'+dk, {r1:{n:'토토',t:'t1',s:3,r:2,rr:18,rw:2,la:now-3600e3,lk:'s'}, r2:{n:'별사탕',t:'t1',s:1,la:now-7200e3,lk:'s'}, r3:{n:'콩콩',t:'t1',r:4,rr:30,rw:6,c:1,cb:1,la:now-600e3,lk:'c'}}),
    FB.set('/hy/day/'+yk, {r1:{n:'토토',s:1}, r4:{n:'몽글',s:2}}),
    FB.set('/hy/hw/cur', {hw1:{id:'hw1', on:true, set:Object.keys(WORD_SETS)[0], from:0, to:3, goal:3, due:now+2*864e5, title:'Stage 1~4', team:'t1', at:now}}),
    FB.set('/hy/hw/res/hw1', {r1:{n:'토토',done:4,tot:4}, r2:{n:'별사탕',done:1,tot:4}})]); })"""
LOGIN = "()=>{ sessionStorage.setItem('hyeng_admin_ok', String(Date.now())); sessionStorage.setItem('hyeng_admin_tk', 'testkey'); sessionStorage.removeItem('hyeng_admin_tab'); }"
MOCK = """()=>{ Notice.fetch=()=>Promise.resolve({v:28, notices:[]});
  Online.submit=(o)=>Promise.resolve(o && o.type==='check' ? {ok:true} : o && o.type==='tags' ? {ok:true, list:[{tag:'0031', nick:'토토', first:'토토', dev:'d1'}, {tag:'0027', nick:'별사탕', first:'별사탕', dev:'d2'}]} : {ok:false, err:'net'}); }"""
ST = """()=>{ const S=document.getElementById('shAdmin'), sc=S.querySelector('.sheetIn'), nv=[...document.querySelectorAll('#adNav button')];
  return {ph:S.classList.contains('adPh'), nav:nv.map(b=>b.dataset.t), on:nv.filter(b=>b.classList.contains('on')).map(b=>b.dataset.t).join(','), tabsVis:getComputedStyle(document.getElementById('adTabs')).display!=='none',
    pane:((document.querySelector('#adBody .adPane')||{}).className||''), over:sc.scrollWidth-sc.clientWidth, sh:!document.getElementById('adKidSh').hidden}; }"""

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch()
        ctx = await br.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        T = await ctx.new_page(); T.on("pageerror", lambda e: errs.append(str(e)[:300])); await boot(T); E = T.evaluate
        await E(SEED); await E(LOGIN); await T.reload(); await T.wait_for_timeout(1500)
        await E("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); }"); await E(MOCK)
        await E("()=>{ document.querySelectorAll('.sheet.on').forEach(s=>s.classList.remove('on')); Admin.open(); }"); await T.wait_for_timeout(1600)
        s = await E(ST)
        ok(s["ph"] and s["nav"] == ["today", "now", "class", "rec", "more"] and not s["tabsVis"], "휴대폰 = 아래 탭 5개 · 위 탭 6개 숨김 " + str(s["nav"]))
        ok(s["on"] == "today" and "adP_today" in s["pane"], "처음 = 🏠 오늘")
        # 🏠 오늘 숫자
        t = await E("()=>[...document.querySelectorAll('#adBody .tdyS')].map(b=>b.innerText.replace(/\\s+/g,' ').trim())")
        print(t)
        ok(len(t) == 4 and t[0].startswith("🔥 오늘 한 아이 3") and "어제 2명" in t[0], "오늘 한 아이 3 · 어제 2명")
        ok("4" in t[1] and "🏃 6판" in t[1], "오늘 공부 4판 · 달리기 6판")
        ok("1/3" in t[2].replace(" ", ""), "숙제 끝 1/3 (3반 3명 중 토토)")
        kr = await E("()=>[...document.querySelectorAll('#adBody .tdyR b')].map(b=>b.textContent)")
        ok(kr == ["콩콩", "토토", "별사탕"], "오늘 한 아이 = 마지막에 한 순서 " + str(kr))
        ok(await E("()=>!!document.querySelector('#adBody #adTodo')"), "오늘 할 일 카드가 🏠 오늘에")
        bd = await E("()=>(document.querySelector('#adNav [data-t=today] .adTabN')||{}).textContent||''")
        td = await E("()=>(document.querySelector('#adBody .tdyS.hot b')||{}).textContent||'0'")
        ok(bd == td or (not bd and td == "0"), "아래 🏠 숫자 = 확인할 것 " + bd + " / " + td)
        # 연결 점
        c = await E("()=>{ const b=document.getElementById('adConn'); return [b.hidden, b.className, b.textContent]; }")
        ok(not c[0] and c[1].split()[-1] in ("g", "y", "r"), "위 연결 점 " + str(c))
        await E("()=>document.getElementById('adConn').click()"); await T.wait_for_timeout(700)
        s = await E(ST); cc = await E("()=>{ const c=document.getElementById('adConnCard'); return c ? c.innerText : ''; }")
        ok(s["on"] == "more" and "시트 서버" in cc and "v28" in cc and "게임 서버" in cc and "선생님 열쇠" in cc and "있음" in cc, "연결 점 → ☰ 더보기 연결 카드 (시트 v28 · 게임 서버 · 열쇠 있음)")
        # 더보기 → 숙제·시험 → ← 더보기
        await E("()=>document.querySelector('#adBody .moR[data-t=work]').click()"); await T.wait_for_timeout(800)
        s = await E(ST); bh = await E("()=>(document.querySelector('#adBody .adBackH')||{}).innerText||''")
        ok("adP_work" in s["pane"] and s["on"] == "more" and "더보기" in bh and "숙제" in bh, "더보기 → 📝 숙제 · 시험 (아래 ☰ 켜진 채 · 위 「← 더보기」)")
        ok(await E("()=>{ const b=document.getElementById('adAccBar'), h=document.querySelector('#adBody .adBackH'); return !b || !!(h.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING); }"), "모두 펼치기 줄은 「← 더보기」 아래")
        await E("()=>document.querySelector('#adBody .adBackH .mini').click()"); await T.wait_for_timeout(500)
        ok("adP_more" in (await E(ST))["pane"], "← 더보기 = 다시 더보기")
        await E("()=>document.querySelector('#adBody .moR[data-t=set]').click()"); await T.wait_for_timeout(700)
        ok(await E("()=>{ const b=document.querySelector('#adBody .adSetH .mini'); return !!b && b.dataset.t==='more'; }"), "⚙️ 설정 위 「← 더보기」")
        # 수업 시작 단추
        await E("()=>document.querySelector('#adNav [data-t=today]').click()"); await T.wait_for_timeout(700)
        await E("()=>document.querySelector('#adBody .tdyGo').click()"); await T.wait_for_timeout(800)
        s = await E(ST); ok(s["on"] == "now" and "adP_now" in s["pane"], "「⚔️ 지금 수업 시작」 → ⚔️ 수업")
        # 아이들: 반 칩 · 한 줄 · 자세히 한 장
        await E("()=>document.querySelector('#adNav [data-t=class]').click()"); await T.wait_for_timeout(1200)
        rows = await E("()=>[...document.querySelectorAll('#adTmList .kRow b')].map(b=>b.textContent)")
        ok(sorted(rows) == sorted(["토토", "별사탕", "콩콩", "몽글"]), "아이 한 줄씩 " + str(rows))
        ok(not await E("()=>!!document.querySelector('#adBody #adTodo')"), "아이들 탭엔 오늘 할 일 없음 (🏠 오늘로)")
        tg = await E("()=>{ const r=[...document.querySelectorAll('#adTmList .kRow')].find(x=>x.querySelector('b').textContent==='토토'); return r ? r.querySelector('small').textContent : ''; }")
        ok("#0031" in tg, "줄에 #태그 " + tg)
        ch = await E("()=>[...document.querySelectorAll('#adTmList .kCls .mini')].map(b=>b.textContent)")
        ok(len(ch) == 3 and ch[0].startswith("전체"), "반 칩 3개 " + str(ch))
        await E("()=>document.querySelector('#adTmList .kCls [data-t=t2]').click()"); await T.wait_for_timeout(400)
        rows = await E("()=>[...document.querySelectorAll('#adTmList .kRow b')].map(b=>b.textContent)")
        ok(rows == ["몽글"], "🦊 4반 칩 → 몽글만")
        await E("()=>document.querySelector('#adTmList .kCls [data-t=all]').click()"); await T.wait_for_timeout(400)
        await E("()=>{ const s=document.querySelector('#shAdmin .sheetIn'); s.scrollTop=120; }"); y0 = await E("()=>document.querySelector('#shAdmin .sheetIn').scrollTop")
        await E("()=>[...document.querySelectorAll('#adTmList .kRowB')].find(b=>b.dataset.k==='r2').click()"); await T.wait_for_timeout(600)
        k = await E("()=>{ const s=document.getElementById('adKidSh'), r=s.getBoundingClientRect(); return {on:!s.hidden, nm:(s.querySelector('.kshTop b')||{}).textContent, full:r.width>=388 && r.height>=840, gem:!!s.querySelector('[data-ad=kdGem]'), mv:!!s.querySelector('#adTmMv'), j:s.querySelectorAll('[data-ad=kdJump]').length}; }")
        ok(k["on"] and k["nm"] == "별사탕" and k["full"], "아이 누르면 화면 덮는 한 장 (별사탕)")
        ok(k["gem"] and k["mv"] and k["j"] == 2, "한 장 안: 💎 · 반 옮기기 · 🏆 랭킹 단계 · 🏷 태그")
        await T.screenshot(path=OUT + "adm728_kid.png")
        await E("()=>document.querySelector('#adKidSh .kshTop .mini').click()"); await T.wait_for_timeout(400)
        y1 = await E("()=>document.querySelector('#shAdmin .sheetIn').scrollTop")
        ok(not (await E(ST))["sh"] and abs(y1 - y0) < 4, "← 뒤로 = 보던 자리 그대로 (" + str(y0) + " → " + str(y1) + ")")
        await E("()=>[...document.querySelectorAll('#adTmList .kRowB')].find(b=>b.dataset.k==='r1').click()"); await T.wait_for_timeout(400)
        await E("()=>document.querySelector('#adKidSh [data-ad=kdJump][data-j=tag]').click()"); await T.wait_for_timeout(900)
        q = await E("()=>(document.getElementById('adTagQ')||{}).value")
        ok(not (await E(ST))["sh"] and q == "토토", "🏷 기기 · 태그 → 한 장 닫고 태그 칸에 「토토」")
        await E("()=>[...document.querySelectorAll('#adTmList .kRowB')].find(b=>b.dataset.k==='r3').click()"); await T.wait_for_timeout(400)
        await E("()=>document.querySelector('#adNav [data-t=rec]').click()"); await T.wait_for_timeout(700)
        ok(not (await E(ST))["sh"], "다른 탭으로 가면 한 장 닫힘")
        ok(await E("()=>!!document.querySelector('#adBody .adFab')") is False, "기록 탭엔 둥근 ＋ 없음")
        await E("()=>document.querySelector('#adNav [data-t=class]').click()"); await T.wait_for_timeout(700)
        ok(await E("()=>!!document.querySelector('#adBody .adFab')"), "아이들 탭 둥근 ＋")
        # 넘침 없음
        ov = {}
        for tb in ("today", "now", "class", "rec", "more", "work", "prize", "send", "set"):
            await E("(t)=>Admin._tab(t)", tb); await T.wait_for_timeout(500); ov[tb] = (await E(ST))["over"]
        ok(all(v <= 0 for v in ov.values()), "가로 넘침 없음 " + str(ov))
        tb = await E("()=>{ const b=document.getElementById('adToast'); return b ? parseFloat(getComputedStyle(b).bottom) : -1; }")
        ok(tb < 0 or tb >= 80, "알림 글이 아래 탭 위로 (" + str(tb) + "px)")
        # 예전 모양 ↔ 휴대폰 모양
        await E("()=>Admin._tab('more')"); await T.wait_for_timeout(500)
        await E("()=>document.querySelector('#adBody [data-ad=phMode][data-v=\"0\"]').click()"); await T.wait_for_timeout(700)
        s = await E(ST)
        ok(not s["ph"] and not s["nav"] and s["tabsVis"] and "adP_now" in s["pane"], "🖥 예전 모양 → 위 탭 6개 · ⚔️ 수업")
        ok(await E("()=>localStorage.getItem('hyeng_admin_ph')==='0'"), "이 기기에 기억")
        await E("()=>document.querySelector('#adBody .adPhBack [data-ad=phMode]').click()"); await T.wait_for_timeout(700)
        s = await E(ST); ok(s["ph"] and s["on"] == "today", "📱 휴대폰 모양으로 → 다시 🏠 오늘")
        await T.screenshot(path=OUT + "adm728_today.png")
        await ctx.close()
        # 패드: 그대로
        ctx = await br.new_context(viewport={"width": 820, "height": 1180}, has_touch=True)
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        P = await ctx.new_page(); P.on("pageerror", lambda e: errs.append("pad " + str(e)[:300])); await boot(P)
        await P.evaluate(LOGIN); await P.evaluate("()=>sessionStorage.setItem('hyeng_admin_tab','today')"); await P.reload(); await P.wait_for_timeout(1500)
        await P.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); }"); await P.evaluate(MOCK)
        await P.evaluate("()=>{ document.querySelectorAll('.sheet.on').forEach(s=>s.classList.remove('on')); Admin.open(); }"); await P.wait_for_timeout(1200)
        s = await P.evaluate(ST)
        ok(not s["ph"] and not s["nav"] and s["tabsVis"] and "adP_now" in s["pane"], "패드 = 위 탭 그대로 (🏠 오늘 → ⚔️ 수업)")
        ok(await P.evaluate("()=>!document.getElementById('adConn').hidden && !document.querySelector('#adBody .adPhBack')"), "패드도 연결 점 · 휴대폰 단추 없음")
        await P.evaluate("()=>document.getElementById('adConn').click()"); await P.wait_for_timeout(600)
        ok("adP_set" in (await P.evaluate(ST))["pane"], "패드 연결 점 → ⚙️ 설정 열쇠")
        await ctx.close()
        Er = real_errs(errs); ok(not Er, "페이지 오류 없음 " + str(Er[:3]))
        await br.close()
    print("FAIL " + str(len(bad)) if bad else "ALL OK"); sys.exit(1 if bad else 0)

if __name__ == "__main__": asyncio.run(main())
