"""(v735) 📋 관리 화면 v2 — 🏠 오늘(지금 하는 중 · 숫자 셋 · 🚨 챙길 아이 + 까닭 + 바로 문자 · 오늘은 괜찮아요 · 반별 오늘)
   · 👥 아이들 표(칩 · 정렬 · 평균) · 아이 한 명(휴대폰 한 장 / PC·패드 오른쪽 서랍) · 서버 안내 · 같은 id 두 번
   사용자: 「일단 관리자 모드 다시 만들고」 · 시각은 2026-11-26(목) 15:00 으로 고정 · 이름은 지어낸 별명"""
import asyncio, sys, os
os.environ["HY_ADM_PH"] = "1"          # 휴대폰 모양 (패드는 아래에서 따로)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

NOW = "2026-11-26T15:00:00+09:00"     # 목요일
# k, 이름, 반, 오늘 몇 분 전(None = 안 함), 월~금 온 날(오늘 앞까지만 씀), 정답률, 판
K = [("r1","토토","t1",45,[1,1,1,1,1],92,12),("r2","별사탕","t1",80,[1,0,1,1,1],84,7),("r3","콩콩","t1",3,[1,1,0,1,1],88,9),("r4","몽글","t1",None,[1,0,0,0,0],81,3),("r5","뭉치","t1",None,[0,0,0,0,0],None,0),
     ("r6","젤리","t2",120,[1,1,1,0,1],68,6),("r7","쿠키","t2",None,[1,0,1,1,1],90,8),("r8","마루","t2",6,[0,1,1,1,1],95,10),("r9","포포","t2",None,[0,1,1,1,1],86,5),("r10","방울","t2",None,[1,0,0,0,0],77,2)]
SEED = """(N)=>FB.ready().then(()=>{ const now=Date.now(), dk=HyDay.key(); const R={k:{}, t:{t1:{n:'3반',e:'🐬'}, t2:{n:'4반',e:'🦊'}}}; N.forEach(x=>R.k[x[0]]={n:x[1],t:x[2]});
  const D={}; N.forEach((x,i)=>{ if(x[3]==null) return; D[x[0]]={n:x[1],t:x[2],s:1+i%3,r:i%2?2:0,rr:10,rw:2,la:now-x[3]*60e3,lk:'s'}; });
  return Promise.all([FB.set('/hy/roster', R), FB.set('/hy/day/'+dk, D),
    FB.set('/hy/hw/cur', {hw1:{id:'hw1', on:true, set:Object.keys(WORD_SETS)[0], from:0, to:3, goal:3, due:now+20*3600e3, title:'Stage 1~4', team:'t1', at:now}}),
    FB.set('/hy/hw/res/hw1', {r1:{n:'토토',done:4,tot:4}, r2:{n:'별사탕',done:1,tot:4}, r3:{n:'콩콩',done:3,tot:4}})]); })"""
MOCK = """(N)=>{ const wd=(new Date(Date.now()+HyBoss.KST).getUTCDay()+6)%7;
  const W=[['아이','들어온 날','오늘의 30','끝까지','공부(분)','정답률(%)','달리기 판','달리기 최고','짧은 판','새 도감','자주 틀린 단어','지난주보다 (공부)','학부모 문자']];
  const WK=[['아이','월','화','수','목','금','토','일','평일 들어온 날','빠진 날','끝낸 Stage','공부(분)','정답률(%)','★2','주간 시험','자주 틀린 단어','상태','구분']];
  N.forEach((x,i)=>{ const marks=[0,1,2,3,4,5,6].map(d=>d<wd && d<5 ? (x[4][d] ? (x[6]>6?'✅ 6':'🔸 2') : '❌') : '');
    const days=marks.filter(m=>/✅|🔸/.test(m)).length+(x[3]!=null?1:0);
    W.push([x[1], String(days), String(x[6]), String(x[6]), String(x[6]*5), x[5]==null?'-':String(x[5]), String(i%4), '1200', '0', String(i%3), ['apple, banana','library','because, enough','tomorrow'][i%4], i%2?'+10':'-5', x[1]+' 학생 이번 주 기록']);
    WK.push([x[1]].concat(marks, [days+' / 5', '', '', '', x[5]==null?'-':String(x[5]), '', '', '', '', x[2]==='t1'?'3반':'4반'])); });
  Online.on=()=>true; Online.submit=(o)=>Promise.resolve(o && o.type==='report' ? {ok:true, rep:{nicks:[], weekly:W, week:WK}} : o && o.type==='check' ? {ok:true} : o && o.type==='tags' ? {ok:true, list:N.map((x,i)=>({tag:'00'+(31+i), nick:x[1], first:x[1], dev:'d'+i}))} : {ok:true});
  Notice.fetch=()=>Promise.resolve({v:28, notices:[]}); }"""
LOGIN = "()=>{ sessionStorage.setItem('hyeng_admin_ok', String(Date.now())); sessionStorage.setItem('hyeng_admin_tk', 'testkey'); sessionStorage.setItem('hyeng_admin_tab', 'today'); localStorage.removeItem('hyeng_admin_v2'); localStorage.removeItem('hyeng_admin_v2s'); }"
CARE = "()=>[...document.querySelectorAll('#a2Care .a2Who')].map(w=>[w.querySelector('.a2Nm b').textContent, [...w.querySelectorAll('.a2P')].map(p=>p.textContent).join(' | '), w.classList.contains('dn')])"
NM = "()=>[...document.querySelectorAll('#a2KList .a2KR[data-k] .nm b')].map(b=>b.firstChild.textContent)"
SH = "()=>{ const s=document.getElementById('adKidSh'); return {on:!s.hidden, wd:s.classList.contains('wd'), nm:(s.querySelector('.kshTop b')||{}).textContent||'', txt:s.hidden ? '' : s.innerText, r:s.getBoundingClientRect().toJSON()}; }"
OVER = """()=>{ const out=[], sc=document.querySelector('#shAdmin .sheetIn'); if(sc.scrollWidth>sc.clientWidth+1) out.push('sheet x '+(sc.scrollWidth-sc.clientWidth));
  document.querySelectorAll('#adBody .a2Stats, #adBody .a2Care, #adBody .a2Cls, #adBody .a2KCard, #adBody .a2Live, #adKidSh:not([hidden])').forEach(R=>R.querySelectorAll('*').forEach(e=>{ const r=e.getBoundingClientRect(); if(!r.width || !e.offsetParent) return;
    const p=e.parentElement; const pr=p.getBoundingClientRect(); if(r.right>pr.right+2 && getComputedStyle(p).overflowX==='visible' && !p.matches('.a2Chips')) out.push((e.className||e.tagName)+' > '+(p.className||p.tagName)+' '+Math.round(r.right-pr.right)); }));
  return [...new Set(out)].slice(0,8); }"""

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch()
        ctx = await br.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        await ctx.grant_permissions(["clipboard-read", "clipboard-write"], origin=ORIGIN.rstrip("/").rsplit("/", 1)[0])
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        T = await ctx.new_page(); T.on("pageerror", lambda e: errs.append(str(e)[:300])); E = T.evaluate
        await T.clock.set_fixed_time(NOW)
        await boot(T); await E(SEED, K); await E(LOGIN); await T.reload(); await T.wait_for_timeout(1500)
        await E("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); }"); await E(MOCK, K)
        await E("()=>{ document.querySelectorAll('.sheet.on').forEach(s=>s.classList.remove('on')); Admin.open(); Admin._tab('today'); }"); await T.wait_for_timeout(2500)
        ok(await E("()=>(new Date(Date.now()+HyBoss.KST).getUTCDay())") == 4, "시각 고정 = 목요일")
        # ── 🏠 오늘 ──
        st = await E("()=>[...document.querySelectorAll('#adBody .a2S')].map(b=>b.innerText.replace(/\\s+/g,''))")
        ok(st == ["오늘한아이5/10", "숙제끝·🐬3반1/5", "챙길아이6명남음"], "숫자 셋 " + str(st))
        lv = await E("()=>(document.querySelector('#adBody .a2Live')||{}).innerText||''")
        ok("지금 하는 중 2명" in lv and "콩콩" in lv and "마루" in lv, "지금 하는 중 (10분 안) 콩콩 · 마루 " + lv)
        c = await E(CARE); print("   ", c)
        ok([x[0] for x in c] == ["몽글", "뭉치", "방울", "별사탕", "콩콩", "젤리"], "챙길 아이 6명 · 빠짐 → 숙제 → 정답률 순 " + str([x[0] for x in c]))
        d = {x[0]: x[1] for x in c}
        ok("2일 안 들어옴 · 마지막 월" in d.get("몽글", "") and "숙제 0/4 · 내일 마감" in d.get("몽글", ""), "몽글: 2일 안 들어옴 · 숙제 0/4 내일 마감")
        ok("이번 주 아직 안 들어옴" in d.get("뭉치", ""), "뭉치: 이번 주 아직")
        ok(d.get("별사탕") == "숙제 1/4 · 내일 마감" and d.get("콩콩") == "숙제 3/4 · 내일 마감", "숙제 남은 아이 (마감 내일)")
        ok("정답률 68%" in d.get("젤리", "") and "자주 틀림 library" in d.get("젤리", ""), "젤리: 정답률 68% · 자주 틀림")
        ok("쿠키" not in d and "포포" not in d and "토토" not in d, "어제까지 온 아이 · 다 한 아이는 없음")
        cls = await E("()=>[...document.querySelectorAll('#adBody .a2ClR')].map(r=>r.innerText.replace(/\\s+/g,' '))")
        ok(len(cls) == 2 and "들어옴 3/5 · 숙제 끝 1/5" in cls[0] and "들어옴 2/5 · 숙제 없음" in cls[1], "반별 오늘 " + str(cls))
        bd0 = await E("()=>+((document.querySelector('#adNav [data-t=today] .adTabN')||{}).textContent||0)")
        ok(bd0 >= 6, f"아래 🏠 숫자 = 할 일 + 챙길 아이 ({bd0})")
        ov = await E(OVER); ok(not ov, "🏠 오늘 넘침 · 삐져나옴 없음 " + str(ov))
        await T.screenshot(path=OUT + "adm735_today.png")
        # 💬 학부모 문자 → 복사 · 흐리게 밑으로 · 숫자 하나 줄어듦
        await E("()=>document.querySelector('#a2Care .a2Who[data-k=r4] [data-ad=v2Pm]').click()"); await T.wait_for_timeout(700)
        clip = await E("()=>navigator.clipboard.readText()")
        ok("몽글 학생" in clip and "들어오지 않았어요" in clip, "학부모 문자 = 들어와 주세요 글 " + clip[:40])
        c = await E(CARE)
        ok(c[-1][0] == "몽글" and c[-1][2] and await E("()=>/학부모 문자/.test(document.querySelector('#a2Care .a2Who[data-k=r4] .a2Stamp').textContent)"), "보낸 아이는 흐리게 맨 밑 · ✓ 학부모 문자 시각")
        ok((await E("()=>document.querySelectorAll('#adBody .a2S')[2].innerText.replace(/\\s+/g,'')")).startswith("챙길아이5"), "챙길 아이 5명 남음")
        bd1 = await E("()=>+((document.querySelector('#adNav [data-t=today] .adTabN')||{}).textContent||0)")
        ok(bd1 == bd0 - 1, f"🏠 숫자 하나 줄어듦 {bd0} → {bd1}")
        await E("()=>document.querySelector('#a2Care .a2Who[data-k=r2] [data-ad=v2Hw]').click()"); await T.wait_for_timeout(700)
        clip = await E("()=>navigator.clipboard.readText()")
        ok("별사탕 학생" in clip and "Stage 1~4" in clip and "1/4" in clip and "11월 27일(금)" in clip, "숙제 알림 문자 " + clip[:60])
        # 오늘은 괜찮아요 → 숨김 · 다시 보기
        await E("()=>document.querySelector('#a2Care .a2Who[data-k=r6] [data-ad=v2Ok]').click()"); await T.wait_for_timeout(500)
        c = await E(CARE)
        ok("젤리" not in [x[0] for x in c] and await E("()=>/숨긴 아이 1명/.test(document.querySelector('#a2Care .a2More').textContent)"), "오늘은 괜찮아요 → 숨김 · 「숨긴 아이 1명 · 다시 보기」")
        v = await E("()=>JSON.parse(localStorage.getItem('hyeng_admin_v2'))")
        ok(v and v.get("d") == "2026-11-26" and v["ok"].get("r6") == 1 and "r4" in v["dn"] and "r2" in v["dn"], "이 기기 · 오늘 날짜로 기억 " + str(v)[:80])
        await E("()=>document.querySelector('#a2Care [data-ad=v2Unhide]').click()"); await T.wait_for_timeout(400)
        ok("젤리" in [x[0] for x in await E(CARE)], "다시 보기 → 젤리 다시")
        # 아이 얼굴 → 한 장 (🏠 오늘 그대로)
        await E("()=>document.querySelector('#a2Care .a2Who[data-k=r5] .a2Av').click()"); await T.wait_for_timeout(500)
        s = await E(SH)
        ok(s["on"] and s["nm"] == "뭉치" and not s["wd"] and "이번 주 아직 안 들어옴" in s["txt"] and "들어와 주세요" in s["txt"], "얼굴 → 뭉치 한 장 (까닭 · 들어와 주세요 글)")
        days = await E("()=>[...document.querySelectorAll('#adKidSh .a2Days span')].map(x=>x.className+':'+x.querySelector('b').textContent)")
        ok(days[:4] == ["x:✕", "x:✕", "x:✕", "t:◌"], "요일: 월화수 ✕ · 오늘 ◌ " + str(days))
        await T.screenshot(path=OUT + "adm735_kid_today.png")
        await E("()=>document.querySelector('#adKidSh .kshTop .mini').click()"); await T.wait_for_timeout(400)
        ok(not (await E(SH))["on"] and await E("()=>!!document.querySelector('#adBody .adP_today')"), "← 뒤로 = 🏠 오늘 그대로")
        # 숫자 「오늘 한 아이」 → 👥 아이들 · 오늘 함
        await E("()=>document.querySelector('#adBody .a2S[data-f=today]').click()"); await T.wait_for_timeout(1200)
        n = await E(NM)
        ok(sorted(n) == sorted(["토토", "별사탕", "콩콩", "젤리", "마루"]) and await E("()=>document.querySelector('#a2KList .a2Chips .mini.on').dataset.f==='today'"), "「오늘 한 아이」 → 👥 아이들 · 오늘 함 칩 " + str(n))
        # ── 👥 아이들 표 ──
        await E("()=>document.querySelector('#a2KList [data-f=all]').click()"); await T.wait_for_timeout(300)
        n = await E(NM)
        ok(len(n) == 10 and n[:6] == ["몽글", "뭉치", "방울", "별사탕", "콩콩", "젤리"] or len(n) == 10 and set(n[:6]) == {"몽글", "뭉치", "방울", "별사탕", "콩콩", "젤리"}, "처음 = 🚨 챙길 아이 먼저 " + str(n))
        ch = await E("()=>[...document.querySelectorAll('#a2KList .a2Chips .mini')].map(b=>b.textContent)")
        ok(ch[:5] == ["전체 10", "🚨 챙길 6", "오늘 함 5", "오늘 안 함 5", "숙제 남음 4"] and "🐬 3반 5" in ch and "🦊 4반 5" in ch, "칩 숫자 " + str(ch))
        av = await E("()=>(document.querySelector('#a2KList .a2KR.avg')||{}).innerText||''")
        ok("전체 평균" in av and "85%" in av.replace("\n", " ") and "끝 1/5" in av, "평균 줄 (정답률 85% · 숙제 끝 1/5) " + av.replace("\n", " "))
        await E("()=>document.querySelector('#a2KList [data-ad=v2Sort][data-s=acc]').click()"); await T.wait_for_timeout(300)
        n = await E(NM)
        ok(n[:3] == ["젤리", "방울", "몽글"] and n[-1] == "뭉치", "정답률 낮은 순 (기록 없는 아이는 끝) " + str(n))
        await E("()=>document.querySelector('#a2KList [data-ad=v2Sort][data-s=acc]').click()"); await T.wait_for_timeout(300)
        ok(set((await E(NM))[:6]) == {"몽글", "뭉치", "방울", "별사탕", "콩콩", "젤리"}, "한 번 더 = 처음 순서")
        await E("()=>{ const q=document.getElementById('a2Q'); q.value='콩'; q.dispatchEvent(new Event('input')); }"); await T.wait_for_timeout(300)
        ok(await E(NM) == ["콩콩"] and await E("()=>document.activeElement && document.activeElement.id")!=None, "이름 찾기 「콩」 → 콩콩")
        await E("()=>{ const q=document.getElementById('a2Q'); q.value=''; q.dispatchEvent(new Event('input')); }"); await T.wait_for_timeout(300)
        hw = await E("()=>[...document.querySelectorAll('#a2KList .a2KR[data-k]')].map(r=>r.querySelector('.nm b').firstChild.textContent+':'+r.querySelector('.hw').innerText.trim())")
        hwd = dict(x.split(":", 1) for x in hw)
        ok(hwd.get("토토") == "4/4" and hwd.get("별사탕") == "1/4" and hwd.get("뭉치") == "0/4" and hwd.get("젤리") == "—", "숙제 칸 (3반만 · 4반 —) " + str(hwd))
        ov = await E(OVER); ok(not ov, "👥 아이들 표 넘침 없음 " + str(ov))
        await T.screenshot(path=OUT + "adm735_class.png")
        await E("()=>document.querySelector('#a2KList .a2KR[data-k=r6]').click()"); await T.wait_for_timeout(500)
        s = await E(SH)
        ok(s["on"] and s["nm"] == "젤리" and "68%" in s["txt"] and "library" in s["txt"] and "학생은 이번 주" in s["txt"], "표 줄 → 젤리 한 장 (정답률 · 틀린 단어 · 학부모 문자)")
        ok(await E("()=>!!document.getElementById('adTmMv') && document.querySelectorAll('#adKidSh [data-ad=kdJump]').length===2 && !document.querySelector('#adKidSh .a2KMore').open"), "⋯ 더(반 옮기기 · 랭킹 · 태그)는 접힘")
        await E("()=>document.querySelector('#adKidSh [data-ad=v2Wk]').click()"); await T.wait_for_timeout(600)
        clip = await E("()=>navigator.clipboard.readText()")
        ok("젤리 학생은 이번 주" in clip, "한 장 학부모 문자 = 시트 한 주 글 " + clip[:30])
        ov = await E(OVER); ok(not ov, "한 장 넘침 없음 " + str(ov))
        await E("()=>document.querySelector('#adNav [data-t=rec]').click()"); await T.wait_for_timeout(1200)
        tx = await E("()=>document.getElementById('adBody').innerText")
        ok("v23 으로 바꾸면" not in tx and "v19 로 올리면" not in tx and "v21 로 올리면" not in tx, "(v735) 서버 v28 인데 「서버를 vNN 으로」 안내 안 나옴")
        await E("()=>document.querySelector('#adNav [data-t=now]').click()"); await T.wait_for_timeout(900)
        ok(await E("()=>[document.querySelectorAll('#adFbSt').length, document.querySelectorAll('#adMsg').length]") == [1, 1], "⚔️ 수업 #adFbSt · #adMsg 한 번씩")
        await ctx.close()
        # ── 패드: 🏠 오늘 두 칸 · 아이 한 명 = 오른쪽 서랍 ──
        os.environ.pop("HY_ADM_PH", None)
        ctx = await br.new_context(viewport={"width": 1024, "height": 1180}, has_touch=True)
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        P = await ctx.new_page(); P.on("pageerror", lambda e: errs.append("pad " + str(e)[:300])); E = P.evaluate
        await P.clock.set_fixed_time(NOW)
        await boot(P); await E("()=>localStorage.removeItem('hyeng_admin_ph')"); await E(SEED, K); await E(LOGIN); await P.reload(); await P.wait_for_timeout(1500)
        await E("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); }"); await E(MOCK, K)
        await E("()=>{ document.querySelectorAll('.sheet.on').forEach(s=>s.classList.remove('on')); Admin.open(); }"); await P.wait_for_timeout(2500)
        tb = await E("()=>[...document.querySelectorAll('#adTabs button')].map(b=>b.dataset.t)")
        ok(tb[0] == "today" and len(tb) == 7 and await E("()=>{ const b=document.querySelectorAll('#adTabs button'); return b[0].getBoundingClientRect().top===b[6].getBoundingClientRect().top; }"), "패드 위 탭 7개 한 줄 (🏠 오늘 먼저) " + str(tb))
        lay = await E("()=>{ const a=document.getElementById('a2Care').getBoundingClientRect(), b=document.getElementById('adTodo').getBoundingClientRect(); return [Math.round(a.left), Math.round(b.left), Math.round(a.top-b.top)]; }")
        ok(lay[1] > lay[0] + 200 and abs(lay[2]) < 10, "🏠 오늘 두 칸 (왼쪽 챙길 아이 · 오른쪽 할 일) " + str(lay))
        ok(await E("()=>getComputedStyle(document.querySelector('#adBody .tdyGoW')).position") == "static", "패드 「수업 시작」은 따라붙지 않음")
        await E("()=>Admin._tab('class')"); await P.wait_for_timeout(1500)
        ok(await E("()=>document.getElementById('a2Mgr').open"), "패드 🏫 반 관리 펼침")
        await E("()=>document.querySelector('#a2KList .a2KR[data-k=r1]').click()"); await P.wait_for_timeout(500)
        s = await E(SH)
        ok(s["on"] and s["wd"] and s["nm"] == "토토" and s["r"]["width"] <= 461 and s["r"]["right"] >= 1023, "줄 → 오른쪽 서랍 (토토) " + str(round(s["r"]["width"])))
        ok(await E("()=>document.querySelector('#a2KList .a2KR[data-k=r1]').classList.contains('on')"), "고른 줄 표시")
        await E("()=>document.querySelector('#a2KList .a2KR[data-k=r3]').click()"); await P.wait_for_timeout(500)
        ok((await E(SH))["nm"] == "콩콩", "다른 줄 → 서랍이 그 아이로")
        await P.screenshot(path=OUT + "adm735_pad_drawer.png")
        await E("()=>document.querySelector('#adKidSh .kshTop .mini').click()"); await P.wait_for_timeout(400)
        ok(not (await E(SH))["on"], "✕ 닫기")
        await E("()=>document.querySelector('#adTmList [data-ad=tmPick][data-k=r2]').click()"); await P.wait_for_timeout(500)
        ok((await E(SH))["nm"] == "별사탕" and not await E("()=>!!document.querySelector('#adTmList .adKidInfo')"), "반 관리 이름도 서랍으로 (명단 안 펼침 없음)")
        await E("()=>Admin.close()"); await P.wait_for_timeout(300)
        ok(not (await E(SH))["on"], "관리 닫으면 서랍도 닫힘")
        await ctx.close()
        Er = real_errs(errs); ok(not Er, "페이지 오류 없음 " + str(Er[:3]))
        await br.close()
    print("FAIL " + str(len(bad)) if bad else "ALL OK"); sys.exit(1 if bad else 0)

if __name__ == "__main__": asyncio.run(main())
