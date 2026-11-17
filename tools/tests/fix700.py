"""(v700) QA 뒤 개선 1-5 + 종이(시험지·따라쓰기·문법) — claude/hy-eng-qa-v700.md
   ① 오늘의 30 지도: 「▶ 다음 할 것」 큰 줄(.sbNext) — 누르면 그 일로 · 폰에서 칩은 작게
   ② 🧪 점검 모드(?qa=1): Firebase·구글 시트 쓰기·sendBeacon = 안 보냄(가짜 성공) · 읽기는 진짜 · 배지 · 끝내기(?qa=0) = 이 기기 저장 되돌림
      · 탭을 그냥 닫아도 다음에 열 때 되돌림(hyeng_qa_bak)
   ③ 🧭 이야기: 예문 여럿 중 이야기에 맞는 것(14단어 이하 · 단어 한 번) · 맞히면 「⭐ Great!」/「👍 You got it!」 (「Thank you!」 없음)
   ④ My Town 밤: 섬에 들어오면 「Good night!」 한 번만 (같은 밤 두 번 X)
   ⑥ 🏫 학원 프린터용: 25문제 시험 마지막 글이 쪽 아래에서 25mm 넘게 위 · 넘친 단 없음 · 쪽 번호 21mm 위
      · 인쇄 직전 점검(Paper.prep): 늦게 들어온 글꼴·그림으로 단이 넘치면 그 자리에서 다시 나눔
   ⑦ 📒 문법 종이: 「⚠️ 이렇게 틀리기 쉬워요」·「✍️ 따라 써 보기」 · 틀리기 쉬운 문장은 그 쪽 문제와 안 겹침
   ⑧ 게임 안 문법 「🤔 기억나요?」: 「⚠️ 이렇게 틀리기 쉬워요」 두 줄 · 그 문장으로 만든 문제는 이번 판에서 뺌"""
import asyncio, sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("HY_REAL3D", "1")
from harness import *
from fakefb import fake
from playwright.async_api import async_playwright

FBU = "https://hyeng-qa-test-default-rtdb.asia-southeast1.firebasedatabase.app"
GASU = "https://script.google.com/macros/s/QA700/exec"
LEAF_GAP = r"""()=>{ const W=document.getElementById('ppWrap'); const z=W.style.zoom; W.style.zoom=''; const mm=96/25.4, out=[];
  [...W.querySelectorAll('.pp')].forEach(p=>{ const pr=p.getBoundingClientRect(); let lo=pr.top, over=0;
    p.querySelectorAll('.ppCol,.kjBody').forEach(c=>{ over=Math.max(over, c.scrollHeight-c.clientHeight); });
    p.querySelectorAll('*').forEach(e=>{ if(e.children.length || e.closest('.ppFt')) return; const r=e.getBoundingClientRect(); if(!r.width || !r.height) return; if(r.bottom>lo) lo=r.bottom; });
    const ft=p.querySelector('.ppFt'), fr=ft && ft.getBoundingClientRect(), fb=fr ? (pr.bottom-fr.bottom)/mm : 99;
    out.push([+((pr.bottom-lo)/mm).toFixed(1), over, +fb.toFixed(1)]); });
  W.style.zoom=z; return out; }"""


async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m, flush=True)
        if not c: bad.append(m)
    NET = []
    async def server(r):
        m = r.request.method; u = r.request.url
        NET.append([m, u.split("?")[0][-30:], ("act=1" in u)])
        if "script.google" in u:
            return await r.fulfill(status=200, content_type="application/json", body='{"ok":true,"list":[]}')
        return await r.fulfill(status=200, content_type="application/json", body="null")
    async with async_playwright() as p:
        br = await p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        ctx = await br.new_context(viewport={"width": 390, "height": 844}, has_touch=True)
        await ctx.add_init_script("window.HY_STY=1; localStorage.setItem('hyeng_nick','민준'); localStorage.setItem('hyeng_tag','0006');")
        pg = await ctx.new_page(); pg.set_default_timeout(120000); pg.on("pageerror", lambda e: errs.append(str(e)[:200]))
        await pg.route("**/*", route)
        await pg.route("**/*firebasedatabase.app/**", server); await pg.route("https://script.google.com/**", server)
        E = pg.evaluate

        # ── ② 🧪 점검 모드
        await pg.goto(ORIGIN + "index.html"); await pg.wait_for_timeout(800)
        await E("()=>{ localStorage.setItem('hyeng_keep','A'); localStorage.removeItem('hyeng_new'); localStorage.setItem('hyeng_alive_qa','1'); }")
        ok(await E("()=>window.HY_QA===false && !document.getElementById('hyQa')"), "② 보통 주소 = 점검 모드 아님 · 배지 없음")
        await pg.goto(ORIGIN + "index.html?qa=1"); await pg.wait_for_timeout(1500)
        r = await E("()=>[window.HY_QA, !!document.getElementById('hyQa'), sessionStorage.getItem('hyeng_qa'), !!localStorage.getItem('hyeng_qa_bak')]")
        ok(r == [True, True, "1", True], f"② ?qa=1 = 점검 모드 · 🧪 배지 · 되돌림 사본 {r}")
        NET.clear()
        r = await E("""async (a)=>{ const [FB, GAS]=a, o={};
            o.put=await (await fetch(FB+'/rooms/x.json', {method:'PUT', body:JSON.stringify({a:1})})).json();
            o.post=await (await fetch(FB+'/log.json', {method:'POST', body:'{"b":2}'})).json();
            o.sv=await (await fetch(FB+'/t.json', {method:'PUT', body:JSON.stringify({'.sv':'timestamp'})})).json();
            o.gas=await (await fetch(GAS, {method:'POST', body:'x'})).json();
            o.act=await (await fetch(GAS+'?act=1&del=1')).json();
            o.beacon=navigator.sendBeacon(GAS, 'x');
            await fetch(FB+'/board.json'); await fetch(GAS+'?board=1');
            return [o, window.HY_QA_LOG.length, window.HY_QA_LOG.filter(x=>x[1].indexOf('rooms/x')>=0).length]; }""", [FBU, GASU])
        await pg.wait_for_timeout(400)
        w = [x for x in NET if x[0] != "GET" or x[2]]
        ok(not w and len([x for x in NET if x[0] == "GET"]) == 2, f"② 쓰기·조치(act=1)·beacon = 서버로 0번 · 읽기(GET) 2번은 진짜 {NET}")
        o = r[0]
        ok(o["put"] == {"a": 1} and "name" in (o["post"] or {}) and isinstance(o["sv"], (int, float)) and o["gas"].get("qa") == 1 and o["act"].get("ok") and o["beacon"] is True and r[1] >= 6 and r[2] == 1,
           f"② 가짜 성공 답 (PUT=그대로 · POST={{name}} · .sv=시각 · 시트={{qa:1}}) · 기록 {r[1]}(게임이 쓴 것 포함) · 한 번 부르면 한 줄 {r[2]}")
        await E("()=>{ localStorage.setItem('hyeng_keep','B'); localStorage.setItem('hyeng_new','1'); }")
        await pg.goto(ORIGIN + "index.html"); await pg.wait_for_timeout(1200)
        ok(await E("()=>window.HY_QA===true && !!document.getElementById('hyQa')"), "② 주소에 qa 가 없어도 이 탭은 계속 점검 모드 (게임 안에서 넘어가도)")
        await E("()=>{ setTimeout(()=>document.querySelector('#hyQa button').click(), 30); }"); await pg.wait_for_url("**qa=0**", wait_until="commit"); await pg.wait_for_timeout(1500)   # (v702) 누르는 사이에 페이지가 바뀌어 evaluate 가 깨지던 것
        r = await E("()=>[location.search, window.HY_QA, window.HY_QA_RESTORED, localStorage.getItem('hyeng_keep'), localStorage.getItem('hyeng_new'), localStorage.getItem('hyeng_alive_qa'), localStorage.getItem('hyeng_qa_bak'), sessionStorage.getItem('hyeng_qa'), !!document.getElementById('hyQa')]")
        ok(r == ["?qa=0", False, True, "A", None, None, None, None, False], f"② 끝내기 = ?qa=0 · 이 기기 저장 되돌림(A · 새 키 지움 · 접속 표시 지움) · 배지 없음 {r}")
        r = await E("()=>[typeof GAME_VER, !!document.getElementById('hyQaHome'), (document.getElementById('hyQaHome')||{}).getAttribute ? document.getElementById('hyQaHome').getAttribute('href') : null, window.HY_QA_END===true]")
        ok(r[0] == "undefined" and r[1] and str(r[2]).endswith("index.html") and r[3], f"② (v702) 끝내기 뒤엔 게임이 켜지지 않고 「점검 모드를 끝냈어요 · 게임 열기」만 (끝나자마자 보통 모드로 서버에 쓰던 것) {r}")
        # 끝내기 없이 탭을 닫으면 → 다음에 여는 탭에서 되돌림
        await pg.goto(ORIGIN + "index.html?qa=1"); await pg.wait_for_timeout(1200)
        await E("()=>{ localStorage.setItem('hyeng_keep','C'); }")
        await pg.close()
        pg = await ctx.new_page(); pg.set_default_timeout(120000); pg.on("pageerror", lambda e: errs.append(str(e)[:200])); E = pg.evaluate
        await pg.route("**/*", route); await pg.route("https://script.google.com/**", server)
        await pg.goto(ORIGIN + "index.html"); await pg.wait_for_timeout(1300)
        r = await E("()=>[window.HY_QA, window.HY_QA_RESTORED, localStorage.getItem('hyeng_keep'), localStorage.getItem('hyeng_qa_bak')]")
        ok(r == [False, True, "A", None], f"② 점검 탭을 그냥 닫아도 → 다음에 열 때 되돌림 {r}")
        # 예전 guard.js(서비스 워커 저장본)가 실리면 → 멈추고 저장본 지우고 한 번 다시 열기
        pq = await ctx.new_page(); pq.set_default_timeout(120000); n_idx = [0]; n_g = [0]
        async def old_guard(r):
            n_g[0] += 1
            if n_g[0] == 1: return await r.fulfill(status=200, content_type="text/javascript", body="window.GUARD={report(){},frame(){},frameErr(){}};")
            return await route(r)
        async def idx(r):
            n_idx[0] += 1; return await route(r)
        await pq.route("**/*", route); await pq.route("**/HY-ENG/index.html*", idx); await pq.route("**/HY-ENG/guard.js*", old_guard)
        await pq.goto(ORIGIN + "index.html?qa=1"); await pq.wait_for_timeout(2500)
        r = await pq.evaluate("()=>[window.HY_QA, !!document.getElementById('hyQa'), sessionStorage.getItem('hyeng_qa_rl')]")
        ok(r[0] is True and r[1] and n_idx[0] == 2 and n_g[0] == 2 and r[2] is None, f"② 예전 guard.js 가 실리면 멈추고 한 번 다시 열어 점검 모드로 (index {n_idx[0]}번 · guard {n_g[0]}번) {r}")
        await pq.evaluate("()=>{ setTimeout(()=>document.querySelector('#hyQa button').click(), 30); }"); await pq.wait_for_url("**qa=0**", wait_until="commit"); await pq.wait_for_timeout(1200); await pq.close()
        await E("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); try{ StudyUI.FAST=0; }catch(e){} ['helloMt','rkAnn','moveAsk'].forEach(i=>{ const d=document.getElementById(i); if(d) d.remove(); }); }")

        # ── ① ▶ 다음 할 것
        await E("""()=>{ const set=Study.BOOKS.g34.sets[0]; const S=Study.load(); S.book='g34'; S.lv=S.lv||{}; S.sty={}; Study.lessons(set).filter(x=>!x.fin).slice(0,3).forEach(x=>{ S.lv[Study.key(set,x.n)]=1; }); Study.save();
            StudyUI.set=set; StudyUI.book='g34'; StudyUI.open(); }""")
        for _ in range(30):
            if await E("()=>!!document.querySelector('.sbMain .sbNext')"): break
            await pg.wait_for_timeout(300)
        r = await E("""()=>{ const n=document.querySelector('.sbMain .sbNext'); if(!n) return null; const b=n.getBoundingClientRect(), c=document.querySelector('#sbChips .sbChip');
            return {k:n.dataset.sbnext, t:n.innerText.replace(/\\s+/g,' ').trim(), h:Math.round(b.height), in:b.left>=0 && b.right<=innerWidth, chipH:c ? Math.round(c.getBoundingClientRect().height) : 0, n:document.querySelectorAll('.sbMain .sbNext').length}; }""")
        ok(r and r["n"] == 1 and r["k"] in ("hw", "gw", "rv", "week", "chk", "stage", "sty", "pq", "") and r["h"] >= 44 and r["in"], f"① ▶ 다음 할 것 = 한 줄 · 크게 · 화면 안 {r}")
        ok(r and 0 < r["chipH"] <= 30, f"① 폰에서 칩은 작게 (≤30px) {r and r['chipH']}")
        await pg.screenshot(path=OUT + "fix700_next.png")
        r = await E("""async ()=>{ const n=document.querySelector('.sbMain .sbNext'), k=n.dataset.sbnext; let hit=null;
            const t = k==='stage' ? document.querySelector('#stMap .stDot.now, #stMap .stDot.nowL') : k ? document.querySelector('#sbChips [data-sbk="'+k+'"]') : null;
            if(t) t.addEventListener('click', e=>{ hit=k||'top'; e.stopImmediatePropagation(); e.preventDefault(); }, {capture:true, once:true});
            n.click(); await new Promise(r=>setTimeout(r, 700)); return [k, hit, !!t]; }""")
        ok(r[1] == (r[0] or None) or (r[0] == "" and not r[2]), f"① 누르면 그 일로 (Stage = 지도 점 · 칩 = 그 칩) {r}")

        # ── ③ 🧭 이야기 문장
        await pg.set_viewport_size({"width": 820, "height": 1180})
        for _ in range(40):
            if await E("()=>DexData.st[1]==='ok' && DexData.st[2]==='ok'"): break
            await pg.wait_for_timeout(200)
        await E("""()=>{ const S=Study.load(); S.book='g12'; S.lv=S.lv||{}; S.sty={}; Study.lessons('basic').filter(x=>!x.fin).slice(0,3).forEach(x=>{ S.lv[Study.key('basic',x.n)]=1; }); Study.save(); StoryQ.open('basic'); }""")
        await pg.wait_for_timeout(300)
        await E("()=>{ const g=document.querySelector('#styMt .styGo'); if(g) g.click(); }"); await pg.wait_for_timeout(200)
        r = await E("""()=>StoryQ.S.sc.map(q=>{ const t=(q.s.pre+q.w.en+q.s.post).replace(/\\s+/g,' ').trim(); const n=(t.match(new RegExp('\\\\b'+q.w.en+'\\\\b','gi'))||[]).length; return [t, t.split(' ').length, n]; })""")
        ok(r and all(x[1] <= 14 and x[2] == 1 for x in r), f"③ 이야기 문장 = 14단어 이하 · 단어 한 번 {[x[0] for x in r]}")
        rx = []
        for i in range(len(r)):
            if i == 1:
                await E("""()=>{ const S=StoryQ.S, q=S.sc[S.i], k=q.opts.findIndex(w=>w.en!==q.w.en); document.querySelector('#styMt .styIt[data-k="'+k+'"]').click(); }"""); await pg.wait_for_timeout(120)
            await E("""()=>{ const S=StoryQ.S, q=S.sc[S.i], k=q.opts.findIndex(w=>w.en===q.w.en); document.querySelector('#styMt .styIt[data-k="'+k+'"]').click(); }"""); await pg.wait_for_timeout(150)
            rx.append(await E("()=>{ const d=document.querySelector('#styMt .stySay'); return [(d.querySelector('p.styRx')||{}).textContent||'', /Thank you/i.test(d.innerText)]; }"))
            await E("()=>document.querySelector('#styMt .styGo').click()"); await pg.wait_for_timeout(120)
        ok(rx and rx[0][0] == "⭐ Great!" and (len(rx) < 2 or rx[1][0] == "👍 You got it!") and not any(x[1] for x in rx), f"③ 맞히면 「⭐ Great!」(한 번에) · 「👍 You got it!」(다시) · 「Thank you!」 없음 {rx}")
        await E("()=>{ try{ StoryQ.close(); }catch(e){} const d=document.getElementById('styMt'); if(d) d.remove(); }")

        # ── ⑧ 게임 안 문법 「기억나요?」
        await E("()=>Gram.load()"); await pg.wait_for_timeout(300)
        r = await E("""()=>{ const L=Gram.list('g34').concat(Gram.list('g56')), g=L.find(g=>Paper.gmMis(g, null).length>=3); if(!g) return null;
            const U=GramUI; U.g=g; U.tier=2; U.full=false; U.mode='recap'; U._misM=null; U.peek=false; StudyUI.view('stGram'); U.draw();
            const d=document.getElementById('stGram'), M=[...d.querySelectorAll('.grMis p')].map(p=>p.innerText.replace(/\\s+/g,' ')); U.draw();
            const M2=[...d.querySelectorAll('.grMis p')].map(p=>p.innerText.replace(/\\s+/g,' '));
            const shown=U._misM.map(m=>m.q), sid=new Set(shown.map(q=>q.sid).filter(x=>x!=null)); let clash=0, n=0;
            for(let t=0;t<12;t++){ U.build(); n=U.qs.length; U.qs.forEach(q=>{ if((q.sid!=null && sid.has(q.sid)) || shown.some(s=>s.s===q.s && s.k===q.k)) clash++; }); }
            return {id:g.id, M, same:JSON.stringify(M)===JSON.stringify(M2), clash, n, T:U.T().n}; }""")
        ok(r and len(r["M"]) == 2 and r["same"], f"⑧ 「🤔 기억나요?」에 「⚠️ 이렇게 틀리기 쉬워요」 두 줄 · 다시 그려도 같은 줄 {r and r['M']}")
        ok(r and r["clash"] == 0 and r["n"] >= 1, f"⑧ 보여 준 문장으로 만든 문제는 이번 판에 안 나옴 (12판) · 문제 수 {r and r['n']}")
        await pg.screenshot(path=OUT + "fix700_recap.png")
        await E("()=>{ GramUI.g=null; try{ StudyUI.open(); }catch(e){} }")

        # ── ⑥ 🏫 학원 프린터용 시험지 · 인쇄 직전 점검
        await pg.set_viewport_size({"width": 1200, "height": 1500})
        await E("()=>{ localStorage.setItem('hyeng_pp_ver','school'); try{ DexData.load(3); loadEasy(); }catch(e){} Paper.open({mode:'test'}); }"); await pg.wait_for_timeout(3000)
        r = await E("""()=>{ const s=Paper.psets().find(s=>Paper.gr(s)==='g34'), $=id=>document.getElementById(id), S=$('ppSet'); S.value=s; S.dispatchEvent(new Event('change',{bubbles:true}));
            $('ppFrom').value=0; $('ppTo').value=5; $('ppN').value='25'; $('ppAB').checked=true; $('ppKey').checked=true; Paper.seed=7; Paper.make();
            return [document.getElementById('paper').classList.contains('ppSafe'), Paper.ver()]; }""")
        ok(r == [True, "school"], f"⑥ 학원 프린터용 = ppSafe {r}")
        await pg.wait_for_timeout(4500)
        g = await E(LEAF_GAP)
        ok(g and all(x[0] >= 25 and x[1] <= 1 for x in g) and all(x[2] >= 21 for x in g), f"⑥ 25문제 A·B·답안지 {len(g)}쪽 — 마지막 글 ≥25mm 위 · 넘친 단 없음 · 쪽 번호 ≥21mm 위 {g}")
        nq0 = await E("()=>document.querySelectorAll('#ppWrap .ppQ').length")
        r = await E("""async ()=>{ const c=document.querySelector('#ppWrap .ppCol'); const x=document.createElement('div'); x.style.height='160mm'; x.className='qaFat'; c.appendChild(x);
            const a=Paper.bad(); const ok=await Paper.prep(); return [a, ok, Paper.bad(), !!document.querySelector('#ppWrap .qaFat')]; }""")
        nq1 = await E("()=>document.querySelectorAll('#ppWrap .ppQ').length")
        ok(r == [True, True, False, False] and nq0 == nq1, f"⑥ 인쇄 직전 점검: 넘친 단 → 그 자리에서 다시 나눔 (문제 {nq0}→{nq1}) {r}")
        # 보통 = 예전 모양 그대로
        await E("()=>{ Paper.setVer('normal'); }"); await pg.wait_for_timeout(2500)
        r = await E("()=>[document.getElementById('paper').classList.contains('ppSafe'), getComputedStyle(document.querySelector('#ppWrap .pp')).paddingBottom, localStorage.getItem('hyeng_pp_ver')]")
        ok(r[0] is False and r[1] == "52.9134px" and r[2] == "normal", f"⑥ 🖨 보통 = 예전 여백(14mm) 그대로 {r}")

        # ── ⑦ 📒 문법 종이
        await E("()=>{ localStorage.setItem('hyeng_pp_ver','school'); Paper.open({mode:'gm'}); }"); await pg.wait_for_timeout(2500)
        await E("()=>{ const n=document.getElementById('ppN'); if(n) n.value='25'; Paper.make(); }"); await pg.wait_for_timeout(3500)
        r = await E("""()=>{ const W=document.getElementById('ppWrap'), mis=[...W.querySelectorAll('.ppMis s')].map(s=>s.textContent.trim()), Q=[...W.querySelectorAll('.ppQ')].map(q=>q.innerText.replace(/\\s+/g,' '));
            return {mis, tryN:W.querySelectorAll('.ppTry').length, line:W.querySelectorAll('.ppTry .ppLine').length, clash:mis.filter(m=>Q.some(q=>q.indexOf(m)>=0)), nq:Q.length}; }""")
        ok(r["mis"] and r["tryN"] >= 1 and r["line"] >= 1, f"⑦ 문법 종이 = 「⚠️ 이렇게 틀리기 쉬워요」 {len(r['mis'])}줄 · 「✍️ 따라 써 보기」 {r['tryN']}")
        ok(not r["clash"] and r["nq"] >= 10, f"⑦ 틀리기 쉬운 문장은 같은 종이 문제와 안 겹침 {r['clash']} · 문제 {r['nq']}")
        g = await E(LEAF_GAP)
        ok(g and all(x[0] >= 25 and x[1] <= 1 for x in g), f"⑦ 문법 종이 {len(g)}쪽 — 아래 25mm · 넘침 없음 {g}")
        await E("()=>{ const W=document.getElementById('ppWrap'); W.style.zoom='1'; }"); await pg.wait_for_timeout(300)
        el = await pg.query_selector("#ppWrap .pp")
        if el: await el.screenshot(path=OUT + "fix700_gm.png")
        # ✏️ 따라쓰기 (학원용): 흐린 글씨가 약한 프린터에서도 찍히게 #a9a9a9 · 아래 25mm
        await E("()=>Paper.open({mode:'kw'})"); await pg.wait_for_timeout(1500)
        await E("()=>{ const s=Paper.psets().find(s=>Paper.gr(s)==='g34'), $=id=>document.getElementById(id), S=$('ppSet'); S.value=s; S.dispatchEvent(new Event('change',{bubbles:true})); $('ppFrom').value=0; $('ppTo').value=2; $('ppN').value='30'; Paper.make(); }")
        await pg.wait_for_timeout(3500)
        r = await E("()=>[getComputedStyle(document.querySelector('#ppWrap .kjT')).color, getComputedStyle(document.querySelector('#ppWrap .kjStrip .g2')).borderTopColor]")
        ok(r == ["rgb(169, 169, 169)", "rgb(184, 184, 184)"], f"⑥ 따라쓰기 흐린 글씨·가운데 줄 한 단계 진하게 {r}")
        g = await E(LEAF_GAP)
        ok(g and all(x[0] >= 25 and x[1] <= 1 for x in g), f"⑥ 단어 따라쓰기 {len(g)}쪽 — 아래 25mm · 넘침 없음 {g}")
        # (v700 이어서) 사용자: 「단어 따라쓰기 여백이 너무 남는데?」
        r = await E("""()=>{ const W=document.getElementById('ppWrap'); W.style.zoom=''; const mm=96/25.4, P=[...W.querySelectorAll('.pp.kj:not(.key)')];
            const rows=[...W.querySelectorAll('.kjX')].map(x=>{ const c=x.closest('.kjB').getBoundingClientRect(); return (c.right-Math.max(...[...x.children].map(e=>e.getBoundingClientRect().right)))/mm; });
            const lone=[...W.querySelectorAll('.kjX')].filter(x=>!x.querySelector('.kjXf')).length;
            const two=[...W.querySelectorAll('.kjS')].filter(s=>s.children.length>1).map(s=>[...s.children].map(r=>r.getBoundingClientRect().right)).map(a=>Math.abs(a[0]-a[a.length-1])/mm);
            const fill=P.map(p=>p.querySelector('.kjBody').classList.contains('fill')), free=P.map(p=>{ const b=p.querySelector('.kjBody'), L=b.lastElementChild; return (b.getBoundingClientRect().bottom-L.getBoundingClientRect().bottom)/mm; });
            return {rows:rows.length, wide:rows.filter(v=>v>20).length, kjE:W.querySelectorAll('.kjE').length, lone, posIn:W.querySelectorAll('.kjPos.in').length, two:Math.max(0, ...two), fill, free:free.map(v=>+v.toFixed(1))}; }""")
        ok(r["rows"] and r["wide"] == 0 and r["kjE"] >= r["rows"] and r["lone"] == 0, f"⑥ 「여러 개」 줄 오른쪽이 비지 않음 (혼자 써 보기 칸 {r['kjE']} · 20mm 넘게 빈 줄 {r['wide']} · 칩만 있는 줄 {r['lone']} · 칩을 뜻 밑으로 {r['posIn']})")
        ok(r["two"] < 2, f"⑥ 긴 단어 둘째 줄도 첫 줄 끝까지 (차이 {r['two']:.1f}mm)")
        ok(all(r["fill"][:-1]) and not r["fill"][-1] and all(v < 6 for v in r["free"][:-1]), f"⑥ 꽉 찬 쪽 = 남는 아래 자리를 카드 사이로 · 마지막 쪽은 그대로 {r['fill']} {r['free']}")
        # (v701) 사용자: 「문장틀도 확인해봐 옵션들 선택 해보면서 단어랑 시험지도」
        ttl = await E("()=>{ const s=Paper.psets().find(s=>Paper.gr(s)==='g56'), $=id=>document.getElementById(id), S=$('ppSet'); S.value=s; S.dispatchEvent(new Event('change',{bubbles:true})); $('ppFrom').value=0; $('ppTo').value=2; $('ppN').value='30'; $('ppGm').value='quiz'; Paper.make(); return document.querySelector('#ppWrap .kjHd b').textContent; }")
        await pg.wait_for_timeout(3000)
        r = await E("""()=>{ const W=document.getElementById('ppWrap'), q=[...W.querySelectorAll('.kjPos.q')];
            return {bd:q.map(e=>getComputedStyle(e).borderTopStyle).filter(b=>b!=='none').length, n:q.length, inW:W.querySelectorAll('.kjW .kjPos.q.in').length, cells:W.querySelectorAll('.kjXf.fx .kjC.kjA').length, title:document.querySelector('#ppWrap .kjHd b').textContent}; }""")
        ok(r["n"] and r["bd"] == 0 and r["cells"] > 0 and "단어 단어" not in r["title"], f"⑥ 단어 따라쓰기 「문제로 내기」: 품사 문제에 테두리 없음(학원용이 글자를 덮었음) · 답 칸이 줄 끝까지 {r['cells']} · 「품사 ___」만 있으면 뜻 밑으로 {r['inW']} · 제목 「{r['title']}」")
        await E("()=>{ Paper.open({mode:'ks'}); }"); await pg.wait_for_timeout(1500); await E("()=>Paper.svaLoad()"); await pg.wait_for_timeout(1500)
        await E("()=>{ const s=Paper.psets().find(s=>Paper.gr(s)==='g34'), $=id=>document.getElementById(id), S=$('ppSet'); S.value=s; S.dispatchEvent(new Event('change',{bubbles:true})); $('ppFrom').value=0; $('ppTo').value=2; $('ppN').value='30'; $('ppRep').value='5'; $('ppGm').value='off'; $('ppTr').checked=true; Paper.seed=3; Paper.make(); }")
        await pg.wait_for_timeout(4500)
        r = await E("""()=>{ const W=document.getElementById('ppWrap'); W.style.zoom=''; const mm=96/25.4, P=[...W.querySelectorAll('.pp.kj:not(.key)')];
            const free=P.map(p=>{ const b=p.querySelector('.kjBody'), L=b.lastElementChild; return +((b.getBoundingClientRect().bottom-L.getBoundingClientRect().bottom)/mm).toFixed(0); });
            const C=[...W.querySelectorAll('.kjB.cont')].map(c=>{ const prev=c.closest('.pp').previousElementSibling, pb=prev && prev.querySelector('.kjBody'), last=pb && pb.lastElementChild;
                return [c.querySelector('.kjNo').textContent===(last && last.querySelector('.kjNo').textContent), (c.querySelector('.kjCt').textContent||'').replace(/^이어서/,'')===((last && (last.querySelector('.kjSt p')||{}).textContent)||'-'), c.querySelectorAll('.kjStrip').length>0, !c.querySelector('[data-g="0"]')]; });
            const over=P.some(p=>{ const b=p.querySelector('.kjBody'); return b.scrollHeight>b.clientHeight+1; });
            return {pages:P.length, free, C, over, items:W.querySelectorAll('.kjB.s:not(.cont)').length}; }""")
        ok(r["C"] and all(all(x) for x in r["C"]) and not r["over"] and r["items"] == 30, f"⑥ 문장 따라쓰기 5번씩: 쪽 끝 카드를 「이어서」로 나눔 {len(r['C'])}번 (번호·문장이 앞 쪽 카드와 같음 · 흐린 글씨 줄은 안 넘어감) · 30문장 · 넘침 없음")
        ok(r["pages"] <= 24 and max(r["free"][:-1]) < 45, f"⑥ 문장 따라쓰기 5번씩 넉넉하게 {r['pages']}쪽 (전 28쪽) · 중간 쪽 아래 남는 자리 {r['free'][:-1]}mm")

        # ── ④ My Town 밤 「Good night!」 한 번
        await pg.unroute("**/*"); await pg.route("**/*", fake)
        await pg.set_viewport_size({"width": 390, "height": 844})
        await pg.goto(ORIGIN + "proto/house.html?isle=1"); await pg.wait_for_timeout(500)
        await E("()=>{ localStorage.setItem('hyeng_proto_code', JSON.stringify('QG700')); localStorage.setItem('hyeng_dev','dQG700'); localStorage.setItem('hyeng_me', JSON.stringify({id:'kQG700', t:'A700'})); }")
        await pg.reload(); await pg.wait_for_timeout(2500)
        await E("()=>{ window.HY_HOUR=23; window._gn=[]; const t0=window.toast; window.toast=function(h, ms){ if(/Good night/.test(h)) window._gn.push(Date.now()); return t0.apply(this, arguments); }; ISLE.enter(); }")
        for _ in range(200):
            if await E("()=>HOUSE.place()==='isle' && !HOUSE.trip().busy"): break
            await pg.wait_for_timeout(250)
        # (시험 기계는 그림이 느려 5초 시계(tick, dt 0.05 상한)가 한참 걸림 → 같은 확인을 바로 부름)
        r = await E("()=>{ DAYR.gn(); const a=window._gn.length; DAYR.gn(); DAYR.gn(); const b=window._gn.length; window.HY_HOUR=12; DAYR.gn(); const c=window._gn.length; window.HY_HOUR=23; return [a, b, c, !!localStorage.getItem(Object.keys(localStorage).find(k=>/^hyeng_proto_.*gn$/.test(k))||'x')]; }")
        ok(r == [1, 1, 1, True], f"④ 밤에 섬 = 「🌙 Good night!」 한 번 · 같은 밤에 다시 불러도 안 뜸 · 낮엔 안 뜸 {r}")
        await pg.screenshot(path=OUT + "fix700_night.png")
        r = await E("()=>{ window.HY_HOUR=12; return getComputedStyle(document.getElementById('tint')).backgroundImage.slice(0,40); }")
        ok(not real_errs(errs), f"JS 오류 없음 {real_errs(errs)[:3]}")
        await br.close()
    print("DONE bad=%d" % len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
