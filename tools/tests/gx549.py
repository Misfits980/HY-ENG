# v549 🧩 문법 섞기 — 학년마다 문법 종류가 만들어지는지 · 보기 3개(답 포함·서로 다름) · 해석 있음 · 아이에게 안 맞는 말 없음 · ★3·★4 에 섞임 · 시험지
import asyncio, sys, re
sys.path.insert(0, "/home/claude/hy-eng/tools/tests")
from harness import *
from playwright.async_api import async_playwright
R=[]
def ok(c,m): R.append(bool(c)); print(("✅ " if c else "❌ ")+m)
BAN=re.compile(r"\b(divorc\w*|missiles?|cigarettes?|smok\w*|crimes?|funerals?|died|kill\w*|wars?|guns?|romanc\w*|criminal)\b", re.I)
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); errs=[]; pg=await br.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)[:200])); await boot(pg)
        await pg.evaluate("()=>{ Study.hsqLoad(); GNote.load(); Paper.open({set:'mid',from:0,to:3}); }"); await pg.wait_for_timeout(4000); await pg.evaluate("()=>Paper.close()")
        need={"elem":["prog","modal","conj","place","comp"], "g56":["prog","modal","conj","place","dur","comp","sup","inf"], "mv1":["conj","dur","inf","ger","perf","pass","rel"]}
        for st,K in need.items():
            r=await pg.evaluate("""([st,K])=>{ const o={}; K.forEach(k=>{ const L=Study._gxAll(st,k); o[k]=L.map(q=>({s:q.st.pre+'['+q.ans+']'+q.st.post, ko:q.st.ko, o:q.opts, a:q.ans, why:q.x.why, lbl:q.x.lbl})); }); return o; }""", [st,K])
            for k,L in r.items():
                bad=[q for q in L if len(set(x.lower() for x in q["o"]))!=3 or q["a"] not in q["o"] or not q["ko"] or not q["why"] or not q["lbl"] or BAN.search(q["s"])]
                ok(len(L)>=5 and not bad, f"{st} {k}: {len(L)}문제 · 이상 {len(bad)} {bad[:1]}")
        # 학년에 안 맞는 종류는 안 나옴
        lo=await pg.evaluate("()=>{ const L=Study._gxAll('elem'); return [...new Set(L.map(q=>q.x.gk))]; }")
        ok(not set(lo)&{"perf","pass","rel","ger","dur","sup","inf"}, f"초3-4 에는 쉬운 문법만 {lo}")
        # ★3·★4 에 섞임
        c=await pg.evaluate("""()=>{ let n=0, t=0; for(let i=0;i<10;i++) for(const tr of [2,3]) Study._bt('g56', i*4, tr).forEach(q=>{ if(q.t==='intro') return; t++; if(q.x && q.x.kind==='gx') n++; }); return [n,t]; }""")
        ok(c[0]>=15, f"초5-6 ★3·★4 에 문법 섞기 {c[0]}/{c[1]}")
        # 시험지
        await pg.evaluate("()=>{ localStorage.removeItem('hyeng_paper'); Paper.open({set:'mv1', from:0, to:9}); }"); await pg.wait_for_timeout(2500)
        r=await pg.evaluate("()=>{ document.querySelectorAll('#ppTy input').forEach(i=>i.checked=i.value==='gx'); Paper.make(); return [document.querySelectorAll('#paper .ppQ').length, document.getElementById('ppInfo').textContent]; }")
        ok(r[0]>=20, f"시험지 「문법 섞어서」 {r}")
        key=await pg.evaluate("()=>document.querySelector('#paper .pp.key') ? document.querySelector('#paper .pp.key').innerText : ''")
        ok("과거분사" in key or "해석" in key or "be동사" in key, "답안지에 이유 (앞 글자 잘림 없이)")
        # (v551) 중등 Stage 마다 「이번 Stage 문법」 — 11가지가 고르게 · ★3 카드+3문제 · ★4 카드+4문제
        d=await pg.evaluate("()=>{ const L=Study.lessons('mv1'); const o={}; L.forEach(x=>{ const G=Study.stgGx('mv1', x.n); if(G) o[G.k]=(o[G.k]||0)+1; }); return o; }")
        ok(len(d)==23 and min(d.values())>=3, f"중등 Stage 문법 23가지 고르게 (v555) {d}")
        t=await pg.evaluate("()=>[2,3].map(tr=>{ const Q=Study._bt('mv1', 9, tr); return [Q.filter(q=>q.t==='intro'&&q.hd==='rule'&&q.x.kd).length, Q.filter(q=>q.tg==='🧩 이번 Stage 문법').length]; })")
        ok(t[0][0]==1 and t[0][1]>=3 and t[1][0]==1 and t[1][1]>=4, f"★3 {t[0]} · ★4 {t[1]} (규칙 카드 · 문제)")
        g=await pg.evaluate("()=>[Study.stgGx('g56', Study.lessons('g56')[3].n), Study.stgGx('elem', Study.lessons('elem')[3].n)]")
        ok(g==[None, None], "초등 Stage 에는 없음 (문법 돌 따로)")
        ok(not errs, f"오류 없음 {errs}")
        await br.close()
    print(f"{sum(R)}/{len(R)}")
asyncio.run(main())
