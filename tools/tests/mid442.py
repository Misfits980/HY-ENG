"""(v442) 📗 중등 노션 보카 v2.1 — [표 3] 문제 + 📖 짧은 글 (사용자: "중등 거 만들어 줘")
  ① data/xtra.json (tools/basic/xtra.py ← 노션 Junior DAY 36~70 [표 3]·[짧은 글 1·2]) 읽힘
  ② 문제: 🔗 짝 단어(가족 · 뜻 보고 고르기) · 📌 숙어 빈칸 · ✏️ 모양 바꿔 고르기 · 📖 영어 풀이 = [표 3] 영어 힌트
     ★2 확인(짝 단어·숙어 1개씩) · ★3(모양) · 💜1(셋 다) — 더하지 않고 바꿔 넣음 (판 문제 수 그대로)
  ③ ★3·💜 끝 화면 「📖 짧은 글 읽기」 → 읽기 카드(문장 누르면 뜻 · 🔊) → ⭕❌ 2 · 제목 · 요약 → ✍️ 한 줄 생각 → 끝(처음 💎1 · 다음 글)
     별·단어 기록과 상관없음"""
import asyncio, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await br.new_page(viewport={"width": 820, "height": 1180})
        pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)
        E = pg.evaluate
        await E("()=>{ StudyUI.open(); }")
        for _ in range(40):
            if await E("()=>Object.keys(XT.w).length>500 && !!MIDX && Object.keys(XT.st).length>10"): break
            await pg.wait_for_timeout(250)
        r = await E("()=>[Object.keys(XT.w).length, Object.keys(XT.st).length, XT.st['36'].length, Study.lessons('mv1')[0].pn, Study.lessons('mv1')[0].n]")
        ok(r[0] > 1000 and r[1] == 35 and r[2] == 2, f"① xtra.json: 단어 {r[0]} · DAY {r[1]} · DAY36 짧은 글 {r[2]}편 · mv1 첫 Stage pn/n {r[3:]}")
        # ② 문제 만들기
        r = await E("""()=>{ Study.ctx('mv1'); const L=Study.lessons('mv1').filter(x=>!x.fin), out={xfam:0, xidm:0, xfrm:0, bad:[]};
            L.forEach(les=>les.ws.forEach(w=>['xfam','xidm','xfrm'].forEach(t=>{ const q=Study.xQ(t, w, 'mv1', les.ws); if(!q) return; out[t]++;
              if(t==='xfam'){ if(q.opts.indexOf(q.ans)<0 || new Set(q.opts.map(o=>o.toLowerCase())).size!==q.opts.length || q.opts.length<3) out.bad.push(['fam', w.en, q.opts]); }
              if(t==='xidm'){ if(q.opts.indexOf(w)<0 || (q.st.pre+w.en+q.st.post).toLowerCase().indexOf(w.en.toLowerCase())<0) out.bad.push(['idm', w.en]); }
              if(t==='xfrm'){ if(q.opts.indexOf(q.form)<0 || new Set(q.opts).size!==q.opts.length || !(q.st.pre+q.form+q.st.post).trim()) out.bad.push(['frm', w.en, q.opts]); } }))); return out; }""")
        ok(r["xfam"] > 600 and r["xidm"] > 150 and r["xfrm"] > 600 and not r["bad"], f"② 만들 수 있는 문제 — 짝 {r['xfam']} · 숙어 {r['xidm']} · 모양 {r['xfrm']} · 이상 {r['bad'][:3]}")
        r = await E("""()=>{ const w=Study.word('sculpture'); const d=Study._mk('def','sculpture','mv1',3); return [d && d.d, XT.w.sculpture.hint]; }""")
        ok(r[0] and r[0] == r[1], f"📖 영어 풀이 = [표 3] 영어 힌트 {r}")
        # 판에 들어갔는지 (★2 확인 · ★3 · 💜1) + 문제 수 그대로
        r = await E("""()=>{ const L=Study.lessons('mv1').filter(x=>!x.fin), cnt={chk:{}, t2:{}, d1:{}}, n={chk:[], t2:[]};
            const go=(lv,tag)=>{ L.slice(0,6).forEach(les=>{ const s=Study.load(); s.seen={}; les.ws.forEach(w=>s.seen[w.en]=1); s.lv={}; s.lv[Study.key('mv1',les.n)]=lv===3?2:lv; s.ck={}; s.d1={}; s.dp={}; if(lv===3) s.dp[Study.key('mv1',les.n)]=1; Study.save();
                  let qs=[]; try{ qs=Study.build('mv1', les.n)||[]; }catch(e){ cnt.err=String(e); } qs.forEach(q=>{ const k=q.idm?'xidm':q.xf?'xfrm':(q.x&&q.x.kd==='f')?'xfam':null; if(k) cnt[tag][k]=(cnt[tag][k]||0)+1; }); if(n[tag]) n[tag].push(qs.filter(q=>q.t!=='intro').length); }); };
            go(1,'chk'); go(2,'t2'); go(3,'d1'); return [cnt, n, Study.tierOf('mv1', L[0].n)]; }""")
        ok(r[0]["d1"].get("xfam", 0) + r[0]["d1"].get("xfrm", 0) + r[0]["d1"].get("xidm", 0) >= 6, f"💜1 판에 짝·숙어·모양 문제 {r[0]['d1']}")
        ok(r[0]["t2"].get("xfrm", 0) >= 3, f"★3 판에 ✏️ 모양 문제 {r[0]['t2']}")
        print("chk", r[0]["chk"], "판 문제 수", r[1])
        # 화면: 세 문제 그리기
        for t in ["xfam", "xidm", "xfrm"]:
            r = await E(f"""()=>{{ const L=Study.lessons('mv1'), les=L.find(x=>x.ws.some(w=>Study.xHas('{t}', w))); const w=les.ws.find(w=>Study.xHas('{t}', w)); Study.ctx('mv1');
                const q=Study.xQ('{t}', w, 'mv1', les.ws); StudyUI.set='mv1'; StudyUI.book='mid'; StudyUI.les=les; StudyUI.qs=[q]; StudyUI.retryMode=true; StudyUI.begin(); const d=document.getElementById('stQ');
                const k=q.so ? q.opts.indexOf(q.ans) : q.t==='sentp' ? q.opts.indexOf(q.form) : q.opts.indexOf(w); StudyUI.sel=k; StudyUI.check(); return [d.querySelector('.stKind').innerText, d.querySelectorAll('.stOpt').length, d.innerText.slice(0,160).replace(/\\n/g,' | '), !!document.querySelector('#stQ .stOpt.ok')]; }}""")
            ok(r[1] >= 2 and r[3] and ("짝 단어" in r[0] or "숙어" in r[0] or "알맞은 모양" in r[0]), f"화면 {t}: {r[0]!r} · 보기 {r[1]} · 맞힘 표시 {r[3]} · {r[2][:110]!r}")
            await pg.screenshot(path=OUT + f"mid442_{t}.png")
        # ③ 짧은 글
        r = await E("""()=>{ const L=Study.lessons('mv1'), x=L[0]; const s=Study.load(); s.rdd={}; Study.save(); const rd=Study.storyFor('mv1', x); return rd ? [rd.day, rd.k, rd.n, rd.st.t[0], rd.st.s.length, rd.st.ox.length, !!rd.st.tc, !!rd.st.sm, !!rd.st.q] : null; }""")
        ok(r and r[2] == 2 and r[4] == 6 and r[5] == 2 and r[6] and r[7] and r[8], f"③ Stage 1 → DAY {r and r[0]} 짧은 글 {r and r[2]}편 · 문장 6 · OX 2 · 제목·요약·생각 {r}")
        # 끝 화면 버튼 (★3 통과로 가정)
        r = await E("""()=>{ const L=Study.lessons('mv1'), k=0, x=L[k]; StudyUI.set='mv1'; StudyUI.book='mid'; StudyUI.les=x; const s=Study.load(); s.seen={}; x.ws.forEach(w=>s.seen[w.en]=1); s.lv={}; s.lv[Study.key('mv1',x.n)]=2; Study.save();
            StudyUI.start(k,false); StudyUI.tier=2; StudyUI.first=StudyUI.total; StudyUI.finish(true); const b=document.querySelector('#stDoneIn [data-read]'); return b ? b.innerText : null; }""")
        ok(r and "짧은 글" in r, f"③ ★3 끝 화면에 「📖 짧은 글 읽기」 {r!r}")
        await pg.screenshot(path=OUT + "mid442_done.png")
        g0 = await E("()=>Wallet.gems()")
        await E("()=>document.querySelector('#stDoneIn [data-read]').click()"); await pg.wait_for_timeout(400)
        r = await E("()=>{ const d=document.getElementById('stQ'); return [d.querySelector('.rdT') && d.querySelector('.rdT').innerText, d.querySelectorAll('.rdS').length, d.querySelectorAll('b.rdW').length, StudyUI.rdMode]; }")
        ok(r[1] == 6 and r[2] >= 3 and r[3], f"③ 읽기 카드: 문장 6 · 단어 초록 {r[2]} · 제목 {r[0]!r}")
        await E("()=>document.querySelector('#stQ .rdS span').click()")
        ok(await E("()=>document.querySelector('#stQ .rdS').classList.contains('ko')"), "③ 문장 누르면 뜻")
        await pg.screenshot(path=OUT + "mid442_read.png")
        await E("()=>document.getElementById('stCheck').click()"); await pg.wait_for_timeout(300)
        kinds = []
        for _ in range(6):
            q = await E("()=>{ const q=StudyUI.qs[StudyUI.i]; return q ? [q.t, q.hd||'', q.x && q.x.k] : null; }")
            if not q or q[0] == "intro": break
            kinds.append(q[2])
            await E("()=>{ const q=StudyUI.qs[StudyUI.i]; StudyUI.sel=q.opts.indexOf(q.ans); StudyUI.check(); }"); await pg.wait_for_timeout(200)
            if q[2] == "sm": await pg.screenshot(path=OUT + "mid442_sm.png")
            await E("()=>{ clearTimeout(StudyUI._adv); StudyUI.next(); }"); await pg.wait_for_timeout(250)
        ok(kinds == ["ox", "ox", "tc", "sm"], f"③ 문제: ⭕❌ 2 · 제목 · 요약 {kinds}")
        r = await E("()=>{ const q=StudyUI.qs[StudyUI.i]; return q && q.hd; }")
        ok(r == "think", f"③ ✍️ 한 줄 생각 카드 {r}")
        await E("()=>{ document.getElementById('rdThink').value='Hi'; document.getElementById('stCheck').click(); }"); await pg.wait_for_timeout(300)
        ok(await E("()=>StudyUI.qs[StudyUI.i] && StudyUI.qs[StudyUI.i].hd==='think'"), "③ 너무 짧으면 다시 쓰게")
        await pg.screenshot(path=OUT + "mid442_think.png")
        await E("()=>{ document.getElementById('rdThink').value='I would make a volcano with my friends.'; document.getElementById('stCheck').click(); }"); await pg.wait_for_timeout(600)
        r = await E("()=>[document.getElementById('stDoneIn').innerText.replace(/\\n/g,' | ').slice(0,200), Wallet.gems(), JSON.stringify(Study.load().rdd||{}), (Study.load().thk||{})]")
        ok("짧은 글 끝" in r[0] and r[1] == g0 + 1 and "다음 짧은 글" in r[0] and r[3], f"③ 끝: 💎+1 · 내 생각 저장 · 다음 짧은 글 {r[0][:120]!r} {r[1]-g0}")
        await pg.screenshot(path=OUT + "mid442_end.png")
        await E("()=>document.querySelector('#stDoneIn [data-read]').click()"); await pg.wait_for_timeout(300)
        r = await E("()=>[StudyUI.rd.k, StudyUI.rdMode]")
        ok(r == [1, True], f"③ 다음 짧은 글 = 2편 {r}")
        r = await E("()=>{ const L=Study.lessons('mv1'); Study.readDone(StudyUI.rd.day+'-1'); return Study.storyFor('mv1', L[0]); }")
        ok(r is None, "③ 두 편 다 읽으면 버튼 없음")
        await br.close()
    real = real_errs(errs)
    ok(not real, f"오류 없음 {real[:3]}")
    print("DONE bad=%d" % len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
