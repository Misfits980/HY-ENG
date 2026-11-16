"""(v690) 사용자: 「바꾸고」 — 🏡 My Town 잠금(오늘의 30 Stage 3개)을 학원 패드·집 기기 합쳐 셈 (서버 v24)
   ① 끝까지 푼 Stage 를 보낼 때 「마을 칸」 tw = 이 기기에서 센 이름과 같은 것 · 못 끝낸 판 · 📝 시험 · 그만둔 복습 = tw 없음 · 끝낸 복습 = rv
   ② 서버 랭킹 답 me.twk(다른 기기에서 센 이름) + 이 기기 이름 = 서로 다른 것만 셈 → 3개면 카드가 바로 열림 (답이 올 때 카드 다시 그림)
   ③ 서버 답이 어제 것(twd) · 다른 아이 것(공용 패드에서 아이가 바뀜) · 옛 서버(me.tw 없음) = 이 기기 것만
   ④ 서버로 열린 카드를 누르면 My Town (hyeng_town_ok = 오늘) · 잠금 창 글 「학원 패드」"""
import asyncio, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright
HOUSE = "<!doctype html><html><body><h1 id=house>HOUSE</h1></body></html>"

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m, flush=True)
        if not c: bad.append(m)
    ME = {}
    async def sheet(r):
        u = r.request.url
        if "board=1" in u:
            return await r.fulfill(status=200, content_type="application/json", body=json.dumps({"ok": True, "v": 24, "boards": {"study": [], "words": [], "run": []}, "me": ME}))
        return await r.fulfill(status=200, content_type="application/json", body='{"ok":true,"list":[]}')
    async with async_playwright() as p:
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={"width": 820, "height": 1180})
        await ctx.add_init_script("window.HY_TOWN_GATE=true; localStorage.setItem('hyeng_nick','민준'); localStorage.setItem('hyeng_tag','0006');")
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*", route); await pg.route("https://script.google.com/**", sheet)
        await pg.route("**/proto/house.html*", lambda r: r.fulfill(status=200, content_type="text/html", body=HOUSE))
        await pg.goto(ORIGIN + "index.html"); await pg.wait_for_timeout(1300)
        await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); try{ StudyUI.FAST=0; }catch(e){} }")
        E = pg.evaluate
        await E("()=>{ window._sub=[]; Online.submit=o=>{ window._sub.push(JSON.parse(JSON.stringify(o))); return Promise.resolve({ok:true}); }; ['helloMt','rkAnn'].forEach(i=>{ const d=document.getElementById(i); if(d) d.remove(); }); localStorage.removeItem('hyeng_town_ok'); }")
        # ① 진짜 한 판
        G34 = await E("()=>Study.BOOKS.g34.sets[0]")
        await E("""(set)=>{ const S=Study.load(); S.srs={}; S.seen={}; S.lv={}; S.cp={}; S.tw=null; S.wuSkip=Study.today(); Study.save(); StudyUI.set=set; StudyUI.book='g34'; StudyUI.open(); StudyUI.start(0,false); }""", G34)
        await pg.wait_for_timeout(500)
        for _ in range(200):
            v = await E("()=>document.getElementById('stDone').style.display")
            if v not in ("none", ""): break
            await E(SOLVE, False); await pg.wait_for_timeout(50)
        await pg.wait_for_timeout(700)
        r = await E("()=>{ const s=window._sub.filter(o=>o.diff==='study'); const o=s[s.length-1]||{}; return [Study.townK(), o.tw, o.clear, o.rule]; }")
        ok(len(r[0]) == 1 and r[1] == r[0][0] and r[2] == 1, f"① 끝까지 푼 Stage → 보낸 판 tw = 이 기기에서 센 이름 {r}")
        LAST = "()=>{ const o=window._sub[window._sub.length-1]||{}; return [o.rule, o.tw===undefined ? null : o.tw]; }"
        await E("()=>{ StudyUI._lg=0; StudyUI.log(false, 30); }")   # 한 판에 한 줄만 보내는 막음(_lg)을 시험마다 풂
        r = await E(LAST); ok(r[1] is None, f"① 못 끝낸 판 = tw 없음 {r}")
        await E("()=>{ StudyUI._lg=0; StudyUI.ex={title:'시험'}; StudyUI.log(true, 90); StudyUI.ex=null; }")
        r = await E(LAST); ok(r[0] == "study-exam" and r[1] is None, f"① 📝 시험 = tw 없음 (이 기기에서도 안 셈) {r}")
        await E("()=>{ StudyUI._lg=0; StudyUI.rv=true; StudyUI.log(true, 90); }")
        r = await E(LAST); ok(r[0] == "study-review" and r[1] == "rv", f"① 끝낸 복습 = rv {r}")
        await E("()=>{ StudyUI._lg=0; localStorage.removeItem('hyeng_study_lastquit'); StudyUI.log(false, 20, 'quit'); StudyUI.rv=false; }")
        r = await E(LAST); ok(r[1] is None, f"① 그만둔 복습 = tw 없음 {r}")
        # ② 서버(다른 기기) 이름 + 이 기기 이름
        loc = (await E("()=>Study.townK()"))[0]
        await E("()=>{ StudyUI.close&&StudyUI.close(); show('scStart'); Kid.confirm=(cb)=>cb(); document.getElementById('btnGo').click(); }"); await pg.wait_for_timeout(500)
        CARD = "()=>{ const t=document.querySelector('#selRule .c-town'); return [t.classList.contains('twLock'), (t.querySelector('.townTag')||{}).textContent||'', TownGate.n()]; }"
        r = await E(CARD); ok(r[0] and r[1] == "🔒 1 / 3", f"② 처음엔 이 기기 1개 = 잠김 {r}")
        today = await E("()=>TodayRank.dkey()")
        FETCH = "()=>{ LiveRank._f=0; LiveRank._busy=0; LiveRank._fresh=0; LiveRank.fetch(); }"
        ME.clear(); ME.update({"tw": 2, "twk": [loc, "g34_x-0"], "twd": today})
        await E(FETCH); await pg.wait_for_timeout(800)
        r = await E(CARD); ok(r[0] and r[1] == "🔒 2 / 3" and r[2] == 2, f"② 서버에 같은 판 1 + 다른 판 1 → 2 (같은 것은 1개 · 답이 오면 카드 바로 다시 그림) {r}")
        ME.update({"tw": 3, "twk": [loc, "g34_x-0", "g34_y-1"]})
        await E(FETCH); await pg.wait_for_timeout(800)
        r = await E(CARD); ok((not r[0]) and r[2] == 3 and await E("()=>TownGate.ok()"), f"② 학원 패드에서 2개 더 → 3 → 카드 열림 {r}")
        ME.clear(); ME.update({"tw": 2, "twk": ["g34_a-0", "g34_b-0"], "twd": today})
        await E(FETCH); await pg.wait_for_timeout(800)
        r = await E(CARD); ok((not r[0]) and r[2] == 3, f"② 이 기기 1 + 서버 다른 2 = 3 (수만 큰 것을 쓰면 2) {r}")
        # ③ 쓰지 않는 답
        ME.update({"twd": "2026-01-01", "tw": 3, "twk": ["a", "b", "c"]})
        await E(FETCH); await pg.wait_for_timeout(800)
        r = await E(CARD); ok(r[0] and r[2] == 1, f"③ 서버 답이 다른 날 것 = 이 기기 것만 · 카드 다시 잠김 {r}")
        ME.update({"twd": today})
        await E(FETCH); await pg.wait_for_timeout(800)
        r = await E("()=>{ LiveRank.B.who='#9999'; return TownGate.n(); }"); ok(r == 1, f"③ 받아 둔 답이 다른 아이 것(공용 패드에서 아이가 바뀜) = 이 기기 것만 {r}")
        ME.clear()
        await E(FETCH); await pg.wait_for_timeout(800)
        r = await E("()=>TownGate.n()"); ok(r == 1, f"③ 옛 서버(me.tw 없음) = 이 기기 것만 {r}")
        r = await E("()=>{ TownGate.show(); const t=document.getElementById('townMt').innerText.replace(/\\s+/g,' '); document.getElementById('townMt').remove(); return t; }")
        ok("학원 패드" in r and "이 기기에서 한 Stage 만" not in r, f"④ 잠금 창 글 {r[:120]!r}")
        # ④ 서버로 열린 카드 → My Town
        ME.update({"tw": 3, "twk": ["p", "q", "r"], "twd": today})
        await E(FETCH); await pg.wait_for_timeout(800)
        await E("()=>{ StudyUI.close&&StudyUI.close(); show('scStart'); document.getElementById('btnGo').click(); }"); await pg.wait_for_timeout(500)
        r = await E(CARD); ok(not r[0], f"④ 카드 열림 {r}")
        await pg.screenshot(path=OUT + "fix689_card.png")
        await E("()=>document.querySelector('#selRule .c-town').click()")
        try:
            await pg.wait_for_url("**/proto/house.html*", timeout=5000); await pg.wait_for_timeout(400)
            r = await E("()=>[location.pathname, localStorage.getItem('hyeng_town_ok')]")
        except Exception as e:
            r = ["(안 감)", str(e)[:80]]
        ok(r[0].endswith("house.html") and r[1], f"④ 누르면 My Town · hyeng_town_ok = 오늘 {r}")
        await ctx.close()
        # ── ⑤ 시험지·따라쓰기 📏 넉넉하게 (사용자: 「깜지 쓰는 거랑 프린트가 버티질 못해 · 널널하게」)
        pg = await br.new_page(viewport={"width": 1280, "height": 900}); pg.on("pageerror", lambda e: errs.append(str(e))); E = pg.evaluate
        await boot(pg)
        await E("()=>{ localStorage.removeItem('hyeng_paper'); try{ DexData.load(1); DexData.load(2); DexData.load(3); loadEasy(); }catch(e){} Paper.open({mode:'test'}); }"); await pg.wait_for_timeout(5000)
        S = await E("()=>({g12:Study.BOOKS.g12.sets[0], g34:Study.BOOKS.g34.sets[0], g56:Study.BOOKS.g56.sets[0]})")
        MM = "(px)=>Math.round(px/(96/25.4)*10)/10"
        r = await E("()=>[document.getElementById('paper').classList.contains('ppRoom'), (document.querySelector('#paper .ppRm')||{}).textContent]")
        ok(r[0] and "켜짐" in (r[1] or ""), f"⑤ 처음엔 📏 넉넉하게 켜짐 (기본) {r}")
        async def kj(mode, set_, f, t, rep):
            await E("(a)=>{ const [m,s,f,t,rep]=a; Paper.close(); Paper.open({mode:m, set:s, from:f, to:t}); const R=document.getElementById('ppRep'); R.value=String(rep); Paper._kjMix=false; Paper.make(); }", [mode, set_, f, t, rep]); await pg.wait_for_timeout(900)
        await kj("kw", S["g12"], 0, 2, 3)
        r = await E("""()=>{ const p=document.querySelector('#ppWrap .pp.kj'), sp=parseFloat(getComputedStyle(p).getPropertyValue('--sp'))||0, st=p.querySelector('.kjStrip'), c=p.querySelector('.kjC');
          return [p.classList.contains('big'), Math.round(st.getBoundingClientRect().height/(96/25.4)*10)/10, Math.round(c.getBoundingClientRect().width/(96/25.4))]; }""")
        ok((not r[0]) and 12.5 <= r[1] <= 14 and r[2] >= 30, f"⑤ 단어 따라쓰기 G1-2: 4선 줄 높이 ≈13mm (예전 9mm) · 칸 너비 30mm 이상 [big?, 줄 mm, 칸 mm] {r}")
        await kj("kw", S["g34"], 0, 2, 3)
        r = await E("""()=>{ const B=[...document.querySelectorAll('#ppWrap .pp.kj .kjB')], L=B.find(b=>/necklace|sweater|costume/.test(b.querySelector('.kjW b').textContent));
          const cs=L ? [...L.querySelectorAll('.kjS > .kjStrip .kjC')].map(c=>Math.round(c.getBoundingClientRect().width/(96/25.4))) : [];
          const over=[...document.querySelectorAll('#ppWrap .kjBody')].filter(b=>b.scrollHeight>b.clientHeight+1).length;
          return [cs, L ? L.querySelectorAll('.kjS > .kjStrip').length : 0, document.querySelectorAll('#ppWrap .pp').length, over]; }""")
        ok(len(r[0]) == 3 and min(r[0]) >= 55 and r[1] == 2 and r[3] == 0, f"⑤ G3-4 긴 단어(8글자) 3번 = 두 줄에 나눠 칸마다 55mm 이상 · 넘친 쪽 없음 [칸 mm, 줄 수, 쪽, 넘침] {r}")
        n_room = r[2]
        await E("()=>document.querySelector('#paper [data-pp=room]').click()"); await pg.wait_for_timeout(900)
        r = await E("()=>[document.getElementById('paper').classList.contains('ppRoom'), document.querySelectorAll('#ppWrap .pp').length, (JSON.parse(localStorage.getItem('hyeng_paper'))||{}).room, (document.querySelector('#paper .ppRm')||{}).textContent, Math.round(document.querySelector('#ppWrap .kjStrip').getBoundingClientRect().height/(96/25.4))]")
        ok((not r[0]) and r[1] < n_room and r[2] is False and "꺼짐" in r[3] and r[4] == 9, f"⑤ 끄면 예전 촘촘한 모양(줄 9mm) · 쪽 수 줄어듦({n_room} → {r[1]}) · 기억 {r}")
        await E("()=>document.querySelector('#paper [data-pp=room]').click()"); await pg.wait_for_timeout(600)
        await kj("ks", S["g34"], 0, 2, 1)
        r = await E("""()=>{ const B=[...document.querySelectorAll('#ppWrap .kjB.s')].map(b=>[(b.querySelector('.kjT')||{textContent:''}).textContent.length, b.querySelectorAll('.kjS > .kjStrip').length]);
          return [B.filter(x=>x[0]>30).every(x=>x[1]===3), B.filter(x=>x[0]>0 && x[0]<=30).every(x=>x[1]===2), B.slice(0,6), B.every(x=>x[0]>0)]; }""")
        ok(r[0] and r[1] and r[3], f"⑤ 문장 따라쓰기 G3-4: 30자 넘는 문장 = 흐린 줄 + 쓰는 줄 2 · 짧은 문장 = 흐린 줄 + 1 {r[2]}")
        await E("()=>{ Paper.close(); Paper.open({mode:'test'}); }"); await pg.wait_for_timeout(1200)
        await E("(s)=>{ const $=id=>document.getElementById(id), S=$('ppSet'); S.value=s; S.dispatchEvent(new Event('change',{bubbles:true})); $('ppFrom').value=0; $('ppTo').value=2; $('ppN').value='30'; document.querySelectorAll('#ppTy input').forEach(i=>{ i.checked=['mean','sent','vform','vtab','wen'].indexOf(i.value)>=0; }); Paper.seed=3; Paper.make(); }", S["g56"]); await pg.wait_for_timeout(1500)
        r = await E("""()=>{ const mm=x=>Math.round(x/(96/25.4)), W=document.getElementById('ppWrap'); W.style.zoom='';
          const u=[...W.querySelectorAll('.pp:not(.key) .ppS u')].filter(x=>!x.classList.contains('mk') && !x.classList.contains('ul')).map(x=>mm(x.getBoundingClientRect().width));
          const ln=[...W.querySelectorAll('.pp:not(.key) .ppQ.row .ppLine')].map(x=>[mm(x.getBoundingClientRect().width), mm(x.getBoundingClientRect().height)]);
          const vt=[...W.querySelectorAll('.ppVt')].map(v=>{ const e=v.querySelectorAll('em'), l=v.querySelectorAll('.ppLine'); return e.length && l.length ? Math.abs(e[0].getBoundingClientRect().bottom-l[0].getBoundingClientRect().bottom)<12 : true; });
          const over=[...W.querySelectorAll('.ppCol')].filter(c=>c.scrollHeight>c.clientHeight+1).length; Paper.fit();
          return [u.length ? Math.min(...u) : 0, ln.length ? Math.min(...ln.map(x=>x[0])) : 0, ln.length ? Math.min(...ln.map(x=>x[1])) : 0, vt.every(Boolean) && vt.length>0, over, Paper.B.total]; }""")
        ok(r[0] >= 23 and r[1] >= 33 and r[2] >= 8 and r[3] and r[4] == 0 and r[5] == 30, f"⑤ 시험지: 문장 빈칸 24mm · 쓰는 줄 34mm×9mm 이상 · 동사 변화 「과거 ___」 이름과 칸이 한 줄 · 넘침 없음 · 30문제 {r}")
        await br.close()
    re = real_errs(errs); ok(not re, f"JS 오류 없음 {re[:3]}")
    print("BAD:", len(bad)); sys.exit(1 if bad else 0)

asyncio.run(main())
