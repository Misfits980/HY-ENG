"""(v443) 📗 중등 voca 1 (노션 Junior DAY 1~35, 새 반 mv0) · 📕 중등 voca 2 (DAY 36~70, 예전 mv1 — 기록 그대로)
  사용자: "나눠서 해 줘 voca1 voca2 로 나눠 줘"
  ① 반 이름 · 순서 (중등 = voca 1 → voca 2 → 리스닝 → 중등 단어) ② mv0 Stage = DAY 1~35 · 단어 30개씩 · 뜻
  ③ mv0 에도 [표 3] 문제 · 📖 짧은 글 ④ 예전 mv1 기록 키(mv1-3601) 그대로 ⑤ 달리기 책 · 칭호 · 화면"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await br.new_page(viewport={"width": 390, "height": 844})
        pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)
        E = pg.evaluate
        await E("()=>{ StudyUI.open(); }")
        for _ in range(40):
            if await E("()=>Object.keys(XT.st).length>60"): break
            await pg.wait_for_timeout(250)
        r = await E("()=>[Study.label('mv0'), Study.label('mv1'), Study.BOOKS.mid.sets, Study.bookOf('mv0'), Study.gradeOf ? Study.gradeOf('mv0') : null]")
        ok(r[0].endswith("중등 voca 1") and r[1].endswith("중등 voca 2") and r[2][:2] == ["mv0", "mv1"] and r[3] == "mid", f"① 반 이름·순서 {r}")
        r = await E("""()=>{ const L=Study.lessons('mv0'), days={}; L.forEach(x=>{ if(!x.fin) days[x.pn]=(days[x.pn]||0)+x.ws.length; }); const nk=L.filter(x=>!x.fin).reduce((a,x)=>a+x.ws.filter(w=>!w.ko).length,0);
            return [Object.keys(days).length, Math.min(...Object.values(days)), Math.max(...Object.values(days)), L[0].pn, L[0].ws.slice(0,3).map(w=>w.en+'='+w.ko), nk, L.length]; }""")
        ok(r[0] == 35 and r[1] >= 29 and r[2] <= 30 and r[3] == 1 and r[5] == 0, f"② mv0 = DAY {r[0]}개 · DAY 단어 {r[1]}~{r[2]} · 첫 Stage DAY {r[3]} {r[4]} · 뜻 없는 단어 {r[5]} · Stage {r[6]}")
        r = await E("""()=>{ const L=Study.lessons('mv1'); return [L[0].pn, L[0].n, L.filter(x=>!x.fin).map(x=>x.pn).reduce((a,b)=>Math.max(a,b),0)]; }""")
        ok(r[0] == 36 and r[1] == 3601 and r[2] == 70, f"④ voca 2 = DAY 36~70 · Stage 키 그대로 {r}")
        r = await E("""()=>{ Study.ctx('mv0'); const L=Study.lessons('mv0').filter(x=>!x.fin), n={xfam:0,xidm:0,xfrm:0};
            L.forEach(les=>les.ws.forEach(w=>['xfam','xidm','xfrm'].forEach(t=>{ if(Study.xQ(t,w,'mv0',les.ws)) n[t]++; }))); 
            const s=Study.load(); s.rdd={}; Study.save(); const rd=Study.storyFor('mv0', L[0]); return [n, rd && rd.day, rd && rd.st.t[0]]; }""")
        ok(r[0]["xfam"] > 400 and r[0]["xfrm"] > 400 and r[0]["xidm"] > 60 and r[1] == "1", f"③ voca 1 [표 3] 문제 {r[0]} · 짧은 글 DAY {r[1]} 「{r[2]}」")
        # 판 만들기 — 모든 Stage ★1 · ★3 · 💜1 · 확인
        r = await E("""()=>{ const L=Study.lessons('mv0'), out={n:0, err:[]}; L.forEach(les=>[0,1,2].forEach(lv=>{ const s=Study.load(); s.seen={}; if(lv) les.ws.forEach(w=>s.seen[w.en]=1); s.lv={}; s.lv[Study.key('mv0',les.n)]=lv; s.ck={}; s.dp={}; Study.save();
              try{ const qs=Study.build('mv0', les.n)||[]; if(qs.filter(q=>q.t!=='intro').length<5) out.err.push([les.n,lv,'짧음']); out.n++; }catch(e){ out.err.push([les.n,lv,String(e)]); } })); return out; }""")
        ok(not r["err"], f"② voca 1 판 {r['n']}개 만들기 · 문제 {r['err'][:3]}")
        r = await E("()=>[RunBook && JSON.stringify(Object.values(RunBook.DEF||{}).flat ? 0 : 0), (typeof titleOf==='function' && titleOf('t-c-mv0')||{}).name, (typeof titleOf==='function' && titleOf('t-c-mv1')||{}).name]")
        ok(r[1] == "중등 voca 1을 정복한" and r[2] == "중등 voca 2를 정복한", f"⑤ 칭호 {r[1:]}")
        r = await E("""()=>{ const s=Study.load(); s.lv={'mv1-3601':2}; s.sub={}; Study.save(); StudyUI.set=null; StudyUI.book='mid'; StudyUI.path(); const a=StudyUI.set;
            const s2=Study.load(); s2.lv={}; s2.sub={}; Study.save(); StudyUI.set=null; StudyUI.path(); return [a, StudyUI.set]; }""")
        ok(r == ["mv1", "mv0"], f"④ 예전 voca 하던 아이 → voca 2 그대로 · 새 아이 → voca 1 {r}")
        # 화면: Daily 30 중등 책 줄
        await E("()=>{ const b=document.querySelector('#stTabs [data-b=mid]'); if(b) b.click(); }"); await pg.wait_for_timeout(400)
        txt = await E("()=>document.getElementById('scStudy') ? document.getElementById('scStudy').innerText : ''")
        print("화면:", txt[:200].replace("\n", " | "))
        await pg.screenshot(path=OUT + "mid443_books.png")
        await br.close()
    real = real_errs(errs)
    ok(not real, f"오류 없음 {real[:3]}")
    print("DONE bad=%d" % len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
