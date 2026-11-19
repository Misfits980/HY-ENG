"""(v712) 📖 짧은 글 — G1-2(basic) · G3-4(elem) · G5-6 리딩(rd1~3) 도 게임에서 읽기 (data/rdst.json)
  ① storyFor: 그 Stage 글 (기록 id = 책-Stage-편) · 유치원 = 없음 · 과를 시작하면 rdst.json 을 미리 받음
  ② ★3 끝 화면 「📖 짧은 글 읽기」 → 읽기 카드 (제목 고르기 있는 글은 제목 안 보임) → 문제
     G1-2 = ⭕❌ 2 · G3-4 = ⭕❌ 2 · 제목 · 🔎 세부 내용 · 리딩 = ⭕❌ 2 · 제목 · 요약 · 세부 내용
  ③ 생각: G1-2 = 둘 중 고르기(안 고르면 못 넘어감) · G3-4 = 빈칸 한 낱말(비우거나 문장이면 다시) · 리딩 = 한 줄(3낱말+)
  ④ 끝: 💎+1 · 내 생각 저장(틀 채운 문장) · 한 편뿐이라 다음 글 없음"""
import asyncio, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

CASES = [("basic", 5, ["ox", "ox"], "ch"), ("elem", 7, ["ox", "ox", "tc", "wh"], "fr"), ("rd2", 3, ["ox", "ox", "tc", "sm", "wh"], "ta")]

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await br.new_page(viewport={"width": 820, "height": 1180})
        pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)
        E = pg.evaluate
        r = await E("()=>[!!loadRd.j, Study.storyFor('basic', Study.lessons('basic')[0])]")
        ok(r == [False, None], f"① 받기 전엔 없음 {r}")
        await E("()=>{ StudyUI.open(); const L=Study.lessons('basic'); StudyUI.set='basic'; StudyUI.book=Study.bookOf('basic'); StudyUI.start(0,false); }")
        for _ in range(40):
            if await E("()=>!!loadRd.j"): break
            await pg.wait_for_timeout(200)
        ok(await E("()=>!!loadRd.j && !!loadRd.j.basic && !!loadRd.j.elem"), "① 과를 시작하면 rdst.json 받음")
        r = await E("()=>Study.storyFor('kinder', Study.lessons('kinder')[0])")
        ok(r is None, "① 유치원 = 짧은 글 없음")
        for set_, u, kinds_want, th in CASES:
            r = await E("""(a)=>{ const [set,u]=a; Study.ctx(set); const L=Study.lessons(set), i=L.findIndex(x=>String(x.wd)===String(u)), x=L[i]; const s=Study.load(); s.rdd={}; s.thk={}; s.seen={}; x.ws.forEach(w=>s.seen[w.en]=1); s.lv={}; s.lv[Study.key(set,x.n)]=2; Study.save();
                const rd=Study.storyFor(set, x); StudyUI.set=set; StudyUI.book=Study.bookOf(set); StudyUI.les=x; StudyUI.start(i,false); StudyUI.tier=2; StudyUI.first=StudyUI.total; StudyUI.finish(true);
                const b=document.querySelector('#stDoneIn [data-read]'); return [rd && rd.day, rd && rd.k, rd && rd.n, rd && rd.st.t[0], b ? b.innerText : null, i]; }""", [set_, u])
            ok(r[0] == f"{set_}-{u}" and r[1] == 0 and r[2] == 1 and r[4] and "짧은 글" in r[4], f"② {set_} Stage {u}: 글 {r[:4]} · 끝 화면 단추 {r[4]!r}")
            g0 = await E("()=>Wallet.gems()")
            await E("()=>document.querySelector('#stDoneIn [data-read]').click()"); await pg.wait_for_timeout(400)
            r = await E("()=>{ const d=document.getElementById('stQ'), st=StudyUI.rd.st; return [d.querySelectorAll('.rdS').length, st.s.length, !!d.querySelector('.rdT'), !!st.tc, d.querySelectorAll('b.rdW').length, StudyUI.rdMode]; }")
            ok(r[0] == r[1] and r[2] == (not r[3]) and r[4] >= 2 and r[5], f"② 읽기 카드: 문장 {r[0]} · 제목 보임 {r[2]} (제목 고르기 {r[3]}) · 단어 표시 {r[4]}")
            await pg.screenshot(path=OUT + f"rd712_{set_}_read.png")
            await E("()=>document.getElementById('stCheck').click()"); await pg.wait_for_timeout(300)
            kinds = []
            for _ in range(8):
                q = await E("()=>{ const q=StudyUI.qs[StudyUI.i]; return q ? [q.t, q.hd||'', q.x && q.x.k, q.opts ? q.opts.length : 0, document.querySelector('#stQ .stKind') ? document.querySelector('#stQ .stKind').innerText : ''] : null; }")
                if not q or q[0] == "intro": break
                kinds.append(q[2])
                if q[2] == "wh":
                    ok(q[3] == 4 and "찾아요" in q[4], f"② 🔎 세부 내용: 보기 {q[3]} · {q[4]!r}")
                    await pg.screenshot(path=OUT + f"rd712_{set_}_wh.png")
                await E("()=>{ const q=StudyUI.qs[StudyUI.i]; StudyUI.sel=q.opts.indexOf(q.ans); StudyUI.check(); }"); await pg.wait_for_timeout(150)
                await E("()=>{ clearTimeout(StudyUI._adv); StudyUI.next(); }"); await pg.wait_for_timeout(200)
            ok(kinds == kinds_want, f"② 문제 {kinds}")
            r = await E("()=>{ const q=StudyUI.qs[StudyUI.i]; return q && q.hd; }")
            ok(r == "think", f"③ ✍️ 생각 카드 {r}")
            st = await E("()=>StudyUI.rd.st")
            if th == "ch":
                await E("()=>document.getElementById('stCheck').click()"); await pg.wait_for_timeout(200)
                ok(await E("()=>StudyUI.qs[StudyUI.i] && StudyUI.qs[StudyUI.i].hd==='think'"), "③ G1-2: 안 고르면 못 넘어감")
                n = await E("()=>document.querySelectorAll('#stQ [data-thc]').length")
                await E("()=>document.querySelector('#stQ [data-thc=\"1\"]').click()"); await pg.wait_for_timeout(200)
                r = await E("()=>[document.querySelector('#stQ .rdFr').innerText, !!document.querySelector('#stQ [data-thc=\"1\"].sel')]")
                ok(n == 2 and st["ch"][1] in r[0] and r[1], f"③ G1-2 고르기 {n}개 → 틀에 들어감 {r}")
                await pg.screenshot(path=OUT + f"rd712_{set_}_think.png")
                want = st["fr"].replace("___", st["ch"][1]).replace(" .", ".")
            elif th == "fr":
                for v in ["", "I like red apples"]:
                    await E("(v)=>{ document.getElementById('rdThink').value=v; document.getElementById('stCheck').click(); }", v); await pg.wait_for_timeout(200)
                    ok(await E("()=>StudyUI.qs[StudyUI.i] && StudyUI.qs[StudyUI.i].hd==='think'"), f"③ G3-4: {v!r} → 다시 쓰게")
                r = await E("()=>{ const e=document.getElementById('rdThink'); return [e.tagName, document.querySelector('#stQ .rdFr').innerText]; }")
                ok(r[0] == "INPUT" and st["fr"].split("___")[0].strip() in r[1], f"③ G3-4 한 낱말 칸 {r}")
                await E("()=>{ document.getElementById('rdThink').value='bananas'; }")
                await pg.screenshot(path=OUT + f"rd712_{set_}_think.png")
                await E("()=>document.getElementById('stCheck').click()"); await pg.wait_for_timeout(500)
                want = st["fr"].replace("___", "bananas").replace(" .", ".")
            else:
                ok(await E("()=>document.getElementById('rdThink').tagName==='TEXTAREA'"), "③ 리딩: 한 줄 쓰기 그대로")
                await E("()=>{ document.getElementById('rdThink').value='I would help the dog because it is lost.'; }")
                want = "I would help the dog because it is lost."
            if th != "fr":
                await E("()=>document.getElementById('stCheck').click()"); await pg.wait_for_timeout(500)
            r = await E("()=>[document.getElementById('stDoneIn').innerText.replace(/\\n/g,' | ').slice(0,220), Wallet.gems(), Study.load().rdd||{}, Study.load().thk||{}, !!document.querySelector('#stDoneIn [data-read]')]")
            rid = f"{set_}-{u}-0"
            ok("짧은 글 끝" in r[0] and r[1] == g0 + 1 and rid in r[2] and r[3].get(rid) == want and not r[4], f"④ 끝: 💎+{r[1]-g0} · 기록 {list(r[2])} · 내 생각 {r[3].get(rid)!r} · 다음 글 없음 {not r[4]}")
            await pg.screenshot(path=OUT + f"rd712_{set_}_end.png")
            r = await E("(a)=>{ const L=Study.lessons(a[0]); return Study.storyFor(a[0], L.find(x=>String(x.wd)===String(a[1]))); }", [set_, u])
            ok(r is None, "④ 다 읽으면 버튼 없음")
        # 중등은 그대로 (DAY 번호 기록)
        for _ in range(30):
            if await E("()=>Object.keys(XT.st||{}).length>10"): break
            await pg.wait_for_timeout(250)
        r = await E("()=>{ const s=Study.load(); s.rdd={}; Study.save(); const rd=Study.storyFor('mv1', Study.lessons('mv1')[0]); return rd ? [rd.day, rd.n] : null; }")
        ok(r and r[0] == "36" and r[1] == 2, f"중등 짧은 글 그대로 {r}")
        await br.close()
    real = real_errs(errs)
    ok(not real, f"오류 없음 {real[:3]}")
    print("DONE bad=%d" % len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
