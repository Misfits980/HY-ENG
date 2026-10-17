"""(v325) 💜 보라 별 3개 · 돌 Stage — 노란 ★1~★3 다음에 보라 별 1(심화)·2(철자+빈칸 ⏱)·3(문장 만들기+뜻 보고 쓰기, ❤️ 3번 틀리면 끝).
   lv 3 = 💜1 · 4 = 💜2 · 5 = 💜3 · 보라 별마다 처음 💎10 · 별 칸 3개가 보라로 바뀜 · Stage 버튼 = 돌"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

PLAY = "()=>{ const d=document.getElementById('stDone'); return d && d.style.display!=='none'; }"

async def play(pg, solve_wrong=0):
    wn = 0
    for step in range(200):
        if await pg.evaluate(PLAY): return True
        st = await pg.evaluate("()=>{ const U=StudyUI, q=U.qs[U.i]; return q ? [q.t, !!U.locked, !!U._brk] : null; }")
        if not st: return await pg.evaluate(PLAY)
        if wn < solve_wrong and st[0] != "intro" and not st[1] and not st[2]:
            await pg.evaluate("()=>{ StudyUI.sel=-1; StudyUI.result(false); }"); wn += 1
        else:
            await pg.evaluate(SOLVE, False)
        await pg.wait_for_timeout(30)
    return await pg.evaluate(PLAY)

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch()
        pg = await br.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await boot(pg)
        await pg.evaluate("()=>{ StudyUI.open(); }"); await pg.wait_for_timeout(1500)
        for set_ in ("elem", "mid", "basic"):
            await pg.evaluate(f"()=>{{ StudyUI.book=Study.bookOf('{set_}'); StudyUI.set='{set_}'; StudyUI.path(); }}")
            n = await pg.evaluate(f"()=>Study.lessons('{set_}')[0].n")
            K = f"{set_}-{n}"
            # 노란 별 3개 + 💜1 받은 상태 (lv 3)
            await pg.evaluate(f"""()=>{{ const s=Study.load(); Study.lessons('{set_}')[0].ws.forEach(w=>s.seen[w.en]=1); s.lv['{K}']=3; s.ck=s.ck||{{}}; s.ck['{K}']=1; s.dp=s.dp||{{}}; s.dp['{K}']=1; Study.save ? Study.save() : 0; s.dg={{d:Study.today(), n:0}}; }}""")
            st = await pg.evaluate(f"()=>[Study.tierOf('{set_}',{n}), Study.deepLv('{set_}',{n}), Study.starN('{set_}', Study.lessons('{set_}')[0])]")
            ok(st == [3, 2, 4], f"{set_} lv3 → 심화 · 다음 💜2 · 별 4 {st}")
            await pg.evaluate("()=>StudyUI.path()"); await pg.wait_for_timeout(150)
            r = await pg.evaluate("()=>{ const d=document.querySelector('#stMap .stDot[data-i=\"0\"]'), w=d.closest('.stWN,.stNode'); return [d.className, (w.querySelector('.stSP')||{}).textContent||'', (w.querySelector('.stSP0')||{}).textContent||'']; }")
            ok("deep" in r[0] and r[1] == "★" and r[2] == "★★", f"{set_} 지도: 자수정 돌 · 보라 별 1/3 {r}")
            await pg.evaluate("()=>StudyUI.pop(0)"); await pg.wait_for_timeout(150)
            pop = await pg.evaluate("()=>document.getElementById('stPop').innerText")
            ok("보라 별 2 도전" in pop and "💜 1 / 3" in pop and "시간 제한" in pop, f"{set_} 창: " + pop.replace("\n", " / ")[:120])
            if set_ == "elem": await pg.screenshot(path=OUT + "purple_pop2.png")
            await pg.evaluate("()=>StudyUI.pop(null)")
            # 💜2 — 철자 + 빈칸 · 타이머
            await pg.evaluate("()=>StudyUI.start(0,false)"); await pg.wait_for_timeout(200)
            q = await pg.evaluate("()=>({tier:StudyUI.tier, dl:StudyUI.dl, intro:StudyUI.qs[0].dl, tg:[...new Set(StudyUI.qs.slice(1).map(q=>q.tg))], tm:StudyUI.qs.slice(1).every(q=>q.tm && q.sec>=10), ts:[...new Set(StudyUI.qs.slice(1).map(q=>q.t))]})")
            print(set_, "💜2", q)
            ok(q["tier"] == 3 and q["dl"] == 2 and q["intro"] == 2 and q["tg"] == ["💜2"] and q["tm"] and ("spell" in q["ts"]), f"{set_} 💜2 판 {q['ts']}")
            await pg.evaluate("()=>document.getElementById('stCheck').click()"); await pg.wait_for_timeout(200)
            tmr = await pg.evaluate("()=>!!document.querySelector('#stQ .stTimer')")
            ok(tmr, f"{set_} 💜2 ⏱ 시간 막대")
            if set_ == "elem": await pg.screenshot(path=OUT + "purple_d2.png")
            g0 = await pg.evaluate("()=>Wallet.gems()")
            done = await play(pg)
            r = await pg.evaluate(f"()=>[Study.lv('{set_}',{n}), Wallet.gems(), document.getElementById('stDoneIn').innerText]")
            ok(done and r[0] == 4 and r[1] - g0 >= 10 and "보라 별 2" in r[2], f"{set_} 💜2 통과 → lv {r[0]} · 💎 +{r[1]-g0} · {r[2][:60]!r}")
            # 💜3 — 3번 틀리면 끝
            await pg.evaluate("()=>{ document.getElementById('stBack').click(); StudyUI.start(0,false); }"); await pg.wait_for_timeout(200)
            q = await pg.evaluate("()=>({dl:StudyUI.dl, tg:[...new Set(StudyUI.qs.slice(1).map(q=>q.tg))], ts:[...new Set(StudyUI.qs.slice(1).map(q=>q.t))], hint:StudyUI.qs.some(q=>q.hint), tm:StudyUI.qs.some(q=>q.tm)})")
            print(set_, "💜3", q)
            ok(q["dl"] == 3 and q["tg"] == ["💜3"] and not q["hint"] and not q["tm"] and ("order" in q["ts"] or set_ == "basic") and ("kdict" in q["ts"] or "spell" in q["ts"] or "def" in q["ts"]), f"{set_} 💜3 판 {q['ts']}")
            await pg.evaluate("()=>document.getElementById('stCheck').click()"); await pg.wait_for_timeout(150)
            lbl = await pg.evaluate("()=>document.getElementById('stRnd').textContent")
            ok("❤️❤️❤️" in lbl, f"{set_} 하트 {lbl}")
            if set_ == "elem":
                kk = await pg.evaluate("()=>{ const k=StudyUI.qs.findIndex(q=>q.kk); return k; }")
                await pg.screenshot(path=OUT + "purple_d3.png")
            done = await play(pg, solve_wrong=3)
            await pg.wait_for_timeout(2000)
            r = await pg.evaluate(f"()=>[Study.lv('{set_}',{n}), document.getElementById('stDone').style.display!=='none', document.getElementById('stDoneIn').innerText]")
            ok(r[1] and r[0] == 4 and "3번 틀려서" in r[2], f"{set_} 💜3 3번 틀림 → 끝 · lv 그대로 {r[0]} · {r[2][:50]!r}")
            await pg.evaluate("()=>{ document.getElementById('stBack').click(); StudyUI.start(0,false); }"); await pg.wait_for_timeout(200)
            done = await play(pg, solve_wrong=2)
            r = await pg.evaluate(f"()=>[Study.lv('{set_}',{n}), Study.starN('{set_}', Study.lessons('{set_}')[0]), document.getElementById('stDoneIn').innerText]")
            ok(r[0] == 4 or "보라 별 3" in r[2], f"{set_} 💜3 2번 틀려도 끝까지 · {r[0]} {r[2][:50]!r}")
            if r[0] == 4:   # 2번 틀려서 80% 안 됐으면 한 번 더 (다 맞힘)
                await pg.evaluate("()=>{ document.getElementById('stBack').click(); StudyUI.start(0,false); }"); await pg.wait_for_timeout(200); await play(pg)
            r = await pg.evaluate(f"()=>[Study.lv('{set_}',{n}), Study.starN('{set_}', Study.lessons('{set_}')[0]), document.getElementById('stDoneIn').innerText]")
            ok(r[0] == 5 and r[1] == 6 and "다 모았어요" in r[2], f"{set_} 💜3 통과 → lv 5 · 별 6 {r}")
            await pg.evaluate("()=>{ document.getElementById('stBack').click(); }"); await pg.wait_for_timeout(300)
            r = await pg.evaluate("()=>{ const d=document.querySelector('#stMap .stDot[data-i=\"0\"]'), w=d.closest('.stWN,.stNode'); return [d.className, (w.querySelector('.stSP')||{}).className||'', (w.querySelector('.stSP')||{}).textContent||'']; }")
            ok("d3" in r[0] and "full" in r[1] and r[2] == "★★★", f"{set_} 지도: 반짝 자수정 · 보라 별 3 {r}")
            await pg.evaluate("()=>StudyUI.pop(0)"); await pg.wait_for_timeout(100)
            pop = await pg.evaluate("()=>document.getElementById('stPop').innerText")
            ok("다 모음" in pop and "보라 별 3 다시" in pop, f"{set_} 창 (다 모음)")
            await pg.evaluate("()=>StudyUI.pop(null)")
        # 돌 지도 사진 — 여러 상태 섞기
        await pg.evaluate("""()=>{ const set='elem', L=Study.lessons(set), s=Study.load(); [[1,1],[2,2],[3,3],[4,4],[5,0],[6,2]].forEach(([i,v])=>{ if(L[i]){ s.lv[set+'-'+L[i].n]=v; if(v>=1){ s.ck=s.ck||{}; s.ck[set+'-'+L[i].n]=1; } } });
            StudyUI.book=Study.bookOf(set); StudyUI.set=set; StudyUI.path(); }"""); await pg.wait_for_timeout(300)
        await pg.evaluate("()=>{ const m=document.querySelector('#stMap .stWBox'); if(m) m.scrollIntoView(); }"); await pg.wait_for_timeout(200)
        await pg.screenshot(path=OUT + "purple_map.png")
        # 다른 책(유치원) 별은 그대로 3칸 노란 별
        r = await pg.evaluate("()=>StudyUI.stars(2, 'kinder', Study.lessons('kinder')[0])")
        ok("stSP" not in r and r.count("★") == 3, f"유치원 별 그대로 {r}")
        ok(not errs, "오류 없음 " + str(errs[:3]))
        await br.close()
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)

asyncio.run(main())
