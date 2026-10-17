"""(v324) 중등 단어(mid)도 나눔 — 25개 과 → 12개 안팎 Stage 몇 개 + 🚩 모아서 복습 · 예전 과의 별·확인·심화·최고 점수·달린 표시·마지막 과를 나눈 Stage 로 옮김"""
import asyncio, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

OLD = {"set": "mid", "spv": 1, "gv": 1, "tv": 1, "lv": {"mid-1": 2, "mid-2": 1, "mid-31": 1, "mv1-101": 1},
       "ck": {"mid-2": 1}, "dp": {"mid-1": 1}, "b2": {"mid-1": 85}, "d1": {}, "ran": {"mid-1": 123}, "seen": {}, "last": {"mid": 2}}

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2)
        await ctx.add_init_script("if(!sessionStorage.getItem('mt')){ sessionStorage.setItem('mt','1'); localStorage.setItem('hyeng_study_v1', " + json.dumps(json.dumps(OLD)) + "); }")
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)
        r = await pg.evaluate("""()=>{ const L=Study.lessons('mid'); const g={}; L.forEach(x=>{ (g[x.pn]=g[x.pn]||[]).push(x); });
            const sz=L.filter(x=>!x.fin).map(x=>x.ws.length), fin=L.filter(x=>x.fin);
            return {n:L.length, parts:Object.keys(g).length, max:Math.max(...sz), min:Math.min(...sz), finAll:fin.every(x=>{ const P=L.filter(y=>y.pn===x.pn && !y.fin); return P.length===0 || x.ws.length===P.reduce((a,y)=>a+y.ws.length,0); }),
              first:g[1].map(x=>[x.n, x.ws.length, !!x.fin]) }; }""")
        print(r)
        ok(r["max"] <= 12 and r["min"] >= 5, f"Stage 크기 {r['min']}~{r['max']}")
        ok(r["first"][-1][2] and r["first"][0][0] == 101 and len(r["first"]) >= 3, f"1과 → {r['first']}")
        ok(r["finAll"], "🚩 = 과 전체")
        m = await pg.evaluate("""()=>{ const s=Study.load(); return {lv:[Study.lv('mid',101), Study.lv('mid',102), Study.lv('mid',201), Study.lv('mid',203)],
            fin1:Study.lv('mid', Study.lessons('mid').find(x=>x.pn===1 && x.fin).n), star:Study.starN('mid', Study.lessons('mid').find(x=>x.n===201)), T:[Study.tierOf('mid',101), Study.tierOf('mid',201)],
            one:(()=>{ const L=Study.lessons('mid'), x=L[L.length-1]; return [x.n, x.fin, L.filter(y=>y.pn===x.pn).length, Study.lv('mid', x.n)]; })(),
            dp:!!s.dp['mid-102'], b2:s.b2['mid-103'], ran:s.ran['mid-101'], last:s.last.mid, mv1:s.lv['mv1-101'], mdv:s.mdv, cur:Study.lessons('mid')[Study.cur('mid')].n}; }""")
        print(m)
        ok(m["lv"] == [2, 2, 1, 1] and m["fin1"] == 0, f"별 옮김 {m['lv']} · 🚩 새로 {m['fin1']}")
        ok(m["star"] == 2 and m["T"][1] == 2, f"확인(★2) 옮김 {m['star']} {m['T']}")
        ok(m["one"][2] > 1 or m["one"][3] == 1, f"안 나뉜 마지막 과도 별 옮김 {m['one']}")
        ok(m["dp"] and m["b2"] == 85 and m["ran"] == 123, "심화·최고 점수·달린 표시")
        ok(m["last"] == 201 and m["mv1"] == 1 and m["mdv"] == 1, f"마지막 과 {m['last']} · 다른 책 그대로")
        # 다시 불러도 그대로 (한 번만)
        await pg.reload(); await pg.wait_for_timeout(1200)
        m2 = await pg.evaluate("()=>[Study.lv('mid',101), Study.load().last.mid]")
        ok(m2 == [2, 201], f"다시 열어도 그대로 {m2}")
        # 화면 — 중등 단어 Stage 지도
        await pg.evaluate("()=>{ StudyUI.open(); StudyUI.book='mid'; StudyUI.set='mid'; StudyUI.path(); }"); await pg.wait_for_timeout(500)
        txt = await pg.evaluate("()=>document.getElementById('scStudy').innerText")
        await pg.screenshot(path=OUT + "mid_split.png")
        ok("1-1" in txt or "1-2" in txt, "화면에 나눈 Stage 번호 (1-1 …)")
        # 처음 하는 Stage 한 판 = 다른 책(mv1 43 · jl 35)과 비슷
        q, qw = await pg.evaluate("()=>{ const b=Study.build('mid', 301), qs=(b&&(b.qs||b))||[], W={}; qs.forEach(x=>{ if(x.w) W[x.w.en]=1; }); return [qs.length, Object.keys(W)]; }"); print('301', q, qw)
        ok(0 < q <= 55, f"한 판 문제 수 {q} (예전 25개 과 = 96 · mv1 Stage 53)")
        ok(not errs, "오류 없음 " + str(errs[:3]))
        await br.close()
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)

asyncio.run(main())
