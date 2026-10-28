"""(v438) 📚 Daily 30 — 보기 품질 + ⏱ 판 시간 (사용자: "데일리30 개선하고 게임 시간이 얼마나 될지도 고려")
  ① G3-4·G5-6·중등: 두 번째 만남부터 보기에 헷갈리는 짝·비슷한 철자(다른 Stage) 섞기 — 같은 Stage 단어만이면 '아는 단어 지우기'로 찍힘
  ② G1-2·유치원은 그대로 (같은 Stage 보기)
  ③ Stage 창에 ⏱ 약 n분 (시트 기록으로 잰 문제당 초)"""
import asyncio, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await br.new_page(viewport={"width": 1180, "height": 820})
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*", route); await pg.goto(ORIGIN + "index.html"); await pg.wait_for_timeout(2500)
        r = await pg.evaluate("""()=>{ const out={}; for(const set of ['basic','g56','mid']){ let tot=0, outside=0, conf=0;
            for(const les of Study.lessons(set).filter(x=>!x.fin).slice(0,5)) for(let k=0;k<2;k++){ const s=Study.load(); s.seen={}; s.lv={}; Study.save(); const qs=Study.build(set, les.n)||[], own={}; les.ws.forEach(w=>own[w.en]=1);
              qs.forEach(q=>{ if(!q || !q.opts || typeof (q.opts[0]||'')!=='object') return; if(q.opts.indexOf(q.w)<0) throw new Error('정답 없음 '+q.w.en); q.opts.forEach(o=>{ if(o===q.w) return; tot++; if(!own[o.en]) outside++; }); }); }
            out[set]=Math.round(outside/Math.max(1,tot)*100); } return out; }""")
        ok(r["g56"] >= 28 and r["mid"] >= 28, f"① G5-6·중등 보기 중 다른 Stage(헷갈리는 짝·비슷한 철자) {r['g56']}% · {r['mid']}% (전 18~19%)")
        ok(r["basic"] <= 25, f"② G1-2 는 그대로 {r['basic']}%")
        r = await pg.evaluate("()=>[Study.estMin('mid',1,40,false), Study.estMin('g56',4,12,false), Study.estMin('elem',0,25,true), Study.estMin('basic',3,20,false)]")
        ok(r == [7, 1, 2, 3], f"③ 시간 짐작: 중등 새 단어 40문제 7분 · ★2 확인 12문제 1분 · 🚩 25문제 2분 · 💜 20문제 3분 {r}")
        await pg.evaluate("()=>{ localStorage.setItem('hyeng_study_v1', JSON.stringify({set:'g56'})); }")
        await pg.reload(); await pg.wait_for_timeout(2500)
        t = await pg.evaluate("""async ()=>{ StudyUI.open && StudyUI.open(); await new Promise(r=>setTimeout(r,600)); StudyUI.book='g56'; StudyUI.set='g56'; StudyUI.path(); await new Promise(r=>setTimeout(r,400));
            const d=document.querySelector('[data-act=pop], .stDot[data-i], [data-i].stDot'); if(d) d.click(); await new Promise(r=>setTimeout(r,500)); const b=document.querySelector('.stPopIn'); return b ? b.innerText : ''; }""")
        ok("⏱ 약" in t and "분" in t, f"③ Stage 창에 ⏱ 약 n분 {t[:90]!r}")
        await pg.screenshot(path=OUT + "d30_438_pop.png")
        await br.close()
    real = real_errs(errs)
    ok(not real, f"오류 없음 {real[:3]}")
    print("DONE bad=%d" % len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
