"""(v676) 사용자: Stage 한 판 끝내자마자 주간 시험이 열려 방금 본 단어로 80점 💎5 → 하루 지난 단어만
   오늘 배운 단어만 있으면 안 열림 · 어제(지난 일요일 포함) 배운 단어가 8개 넘으면 열림 · 약한 단어로 채워서 열지 않음 · 오늘 처음 본 단어는 시험에 안 나옴"""
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
        br = await p.chromium.launch(); pg = await br.new_page(viewport={"width": 820, "height": 1180})
        pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg); E = pg.evaluate
        # 지금 책 첫 두 판의 단어를 '배운 날'로 넣는 도우미
        await E("()=>{ StudyUI.open(); }"); await pg.wait_for_timeout(400)
        await E("""()=>{ const set=StudyUI.set; window._wk=(d0,d1,weak)=>{ const S=Study.load(); const L=Study.lessons(set), t=Study.today();
            S.sd={}; S.d1={}; S.srs={}; S.seen={};
            L[0].ws.forEach(w=>{ S.seen[w.en]=1; if(d0!=null) S.sd[w.en]=t+d0; });
            L[1].ws.forEach(w=>{ S.seen[w.en]=1; if(d1!=null) S.sd[w.en]=t+d1; if(weak) S.srs[w.en]=[0,t]; });
            Study.save(); const W=Study.weekWords(set), Q=Study.buildWeek(set); return [W.fresh, W.ws.length, !!Q, Q?Q.filter(q=>q.w && L[1].ws.some(x=>x.en===q.w.en)).length:-1, L[0].ws.length]; }; }""")
        r = await E("()=>_wk(0,0,false)")
        ok(r[0] == 0 and not r[2], f"오늘 배운 단어만 → 주간 시험 안 열림 {r}")
        r = await E("()=>_wk(-1,0,true)")
        ok(r[0] == r[4] and r[2] and r[3] == 0, f"어제 배운 판 → 열림 · 오늘 처음 본 단어(약한 단어여도)는 안 나옴 {r}")
        r = await E("()=>{ const t=Study.today(), ws=Study.weekStart(); return _wk(ws-1-t, null, false); }")
        ok(r[0] == r[4] and r[2], f"지난 일요일에 배운 단어도 이번 주 시험에 {r}")
        r = await E("()=>{ const t=Study.today(), ws=Study.weekStart(); return _wk(ws-2-t, null, false); }")
        ok(r[0] == 0 and not r[2], f"그 전 주 단어는 안 셈 {r}")
        r = await E("()=>{ const t=Study.today(); const S=Study.load(); return _wk(null, 0, true); }")
        ok(not r[2], f"약한 단어만으로는 안 열림 {r}")
        ok(not real_errs(errs), f"JS 오류 없음 {real_errs(errs)[:2]}")
        await br.close()
    print("DONE bad=%d" % len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
