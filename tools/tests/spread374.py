"""(v374) 아이폰 측정: 정답 순간 한 프레임에 판정·효과·다음 문·문제 글자·읽기가 몰려 40~60ms, 「문제 표시」 41ms(강제 배치 계산)
  → 정답 프레임: 판정·효과 / 다음 프레임: 다음 문 / 그다음: 문제 글자·읽기 · 강제 배치 계산 없앰 · 판이 끝나면 미룬 일 버림
  · 두 지대 전 그림은 GPU 에서 내려놓기 · 📊 서버 실시간 소식 시각·처리 시간"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(); ctx = await br.new_context(viewport={"width": 390, "height": 844})
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)
        await pg.evaluate("()=>{ G.set='elem'; G.diff='normal'; G.rule='normal'; G.lesson=null; G.tag=null; startGame(); }")
        await pg.wait_for_timeout(1500)
        # 정답 → 프레임마다 한 가지씩
        r = await pg.evaluate("""()=>new Promise(res=>{ const log=[]; let f=0; const sp=window.spawnSet, sq=window.showQuestion;
            window.spawnSet=function(){ log.push(['spawn', f]); return sp.apply(this, arguments); }; window.showQuestion=function(){ log.push(['show', f]); return sq.apply(this, arguments); };
            const s=G.sets.find(s=>!s.judged); G.lane=s.q.answer; P.x=laneX(s.q.answer, G.lanes); const st=G.stage; judge(s);
            const now=[G.sets.filter(x=>!x.judged).length, G.stage-st]; log.push(['judge', 0]);
            const tick=()=>{ f++; if(f<6) requestAnimationFrame(tick); else { window.spawnSet=sp; window.showQuestion=sq; res({now, log, live:G.sets.filter(x=>!x.judged).length, q:document.getElementById('ptext').textContent}); } }; requestAnimationFrame(tick); })""")
        print("spread", r)
        L = {k: v for k, v in r["log"]}
        ok(r["now"] == [0, 1] and [k for k, v in r["log"]] == ["judge", "spawn", "show"] and L["show"] > L["spawn"] and r["live"] == 1, f"판정 → 다음 프레임 다음 문 → 그다음 문제 글자 {r}")
        # 강제 배치 계산 없음 · 깜빡임은 다시 붙음
        r = await pg.evaluate("""()=>new Promise(res=>{ const card=document.getElementById('prompt'); const s=G.sets.find(s=>!s.judged); showQuestion(s.q, s); const a=card.classList.contains('fresh');
            requestAnimationFrame(()=>requestAnimationFrame(()=>res([a, card.classList.contains('fresh')]))); })""")
        ok(r == [False, True], f"문제 카드 깜빡임: 바로 빼고 다음 프레임에 다시 {r}")
        src = open(os.path.join(SITE, "index.html"), encoding="utf8").read()
        i = src.index("function showQuestion("); body = src[i:i+1600]
        ok("void card.offsetWidth" not in body, "문제 표시에 강제 배치 계산(offsetWidth) 없음")
        # 판이 끝나면 미룬 일 버림
        r = await pg.evaluate("""()=>{ let n=0; Later.add(()=>{ n++; }); G.quit=true; G.skipOutro=true; gameOver(); Later.flush(); return [n, Later.q.length]; }""")
        ok(r == [0, 0], f"판이 끝나면 미룬 일을 하지 않음 {r}")
        # 두 지대 전 그림 내려놓기
        r = await pg.evaluate("""()=>{ const D=[]; const keys=['floor-meadow','props-meadow','floor-desert','floor-volcano','gate-night']; keys.forEach(k=>{ TrapArt.tex[k]=TrapArt.tex[k]||{}; const t=TrapArt.tex[k]; t.dispose=()=>D.push(k); });
            const vi=ZONES.findIndex(z=>zoneArt(z)==='volcano'); GLWarm.release(vi); return [vi, D.sort()]; }""")
        ok(r[1] == ["floor-desert", "floor-meadow", "props-meadow"], f"화산에 들어가면 초원·사막 그림만 내려놓음 (화산·밤하늘은 그대로) {r}")
        # 📊 서버 소식
        await pg.goto(ORIGIN + "index.html?perf=1"); await pg.wait_for_timeout(1500)
        r = await pg.evaluate("""()=>{ const es=new EventSource('https://example.invalid/x.json'); let got=0; es.addEventListener('put', ()=>{ got++; const t=performance.now(); while(performance.now()-t<5){} });
            Perf.cur={}; es.dispatchEvent(new MessageEvent('put', {data:'null'})); es.close(); return [got, Perf.evs.some(e=>e.n==='서버 소식(put)'), Math.round(Perf.cur['⏱서버 소식 처리']||0)]; }""")
        ok(r[0] == 1 and r[1] and r[2] >= 4, f"서버 실시간 소식 시각·처리 시간 {r}")
        await pg.evaluate("()=>localStorage.removeItem('hyeng_perf')")
        e = real_errs(errs); ok(not e, "오류 없음 " + str(e[:3]))
        await br.close()
    print("결과:", "통과" if not bad else "실패 " + str(bad))
asyncio.run(main())
