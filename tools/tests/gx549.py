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
        await pg.evaluate("()=>Paper.open({set:'mid',from:0,to:3})"); await pg.wait_for_timeout(4000); await pg.evaluate("()=>Paper.close()")
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
        ok(not errs, f"오류 없음 {errs}")
        await br.close()
    print(f"{sum(R)}/{len(R)}")
asyncio.run(main())
