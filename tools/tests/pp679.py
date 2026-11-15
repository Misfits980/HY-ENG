"""(v679) 사용자: 「어드민모드 시험지 오류 없는지 전체적으로 확인」 → ppall.py 로 1,700개 넘게 만들어 보고 찾은 것 고침
   ① 「그림 보고 고르기」는 그림이 있는 책(유치원·G1-2)에만 (G3-4 부터는 고르면 0문제 빈 시험지였음)
   ② 고른 형식으로 낼 문제가 0개면 빈 시험지·빈 답안지 대신 안내 한 줄
   ③ 「선 잇기」만 20문제로 고르면 5문제 → 20문제 (5개 묶음 넷)
   ④ 보기 뜻이 겹쳐 답이 둘인 문제 없음 (problem 「문제」 ~ trouble 「곤란, 문제」 · 사이트 워드 look·see 「보다」 둘)
   ⑤ 단어 따라쓰기 답안지가 한 쪽을 넘으면 다음 쪽도 「📗 답안지 (이어서)」 (예전: 학습지 머리 · 이름 칸)
   ⑥ 문제는 많은데 형식이 모자라 적게 나오면 「범위 단어가 모자라」 대신 「고른 형식으로 낼 수 있는 단어가 모자라」"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ppall.py"), encoding="utf-8").read(); ns = {}; exec(src[src.index('HELP = r"""'):src.index('def ranges')], ns)

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await br.new_page(viewport={"width": 1280, "height": 900}); pg.on("pageerror", lambda e: errs.append(str(e)))
        await boot(pg); E = pg.evaluate
        await E("()=>{ try{ DexData.load(1); DexData.load(2); DexData.load(3); loadEasy(); }catch(e){} Paper.open({mode:'test'}); }"); await pg.wait_for_timeout(5000); await E(ns["HELP"])
        S = await E("()=>({g12:Study.BOOKS.g12.sets[0], g34:Study.BOOKS.g34.sets[0], k:Paper.psets().find(s=>/사이트/.test(Study.label(s))), r1:Paper.psets().find(s=>/리딩 1/.test(Study.label(s)))})")
        r = await E("(S)=>[Paper.vis('pic', S.g34), Paper.vis('pic', S.g12), Paper.vis('pic', S.k)]", S)
        ok(r == [False, True, True], f"① 그림 보고 고르기: G3-4 없음 · G1-2·유치원 있음 {r}")
        await E(ns["TEST_CFG"], [S["g34"], 0, 2, ["opp"], 20, True, True, True, 7])
        r = await E("()=>[Paper.B.total, document.querySelectorAll('#ppWrap .pp').length, !!document.querySelector('#ppWrap .ppNone'), document.getElementById('ppInfo').textContent]")
        ok(r[0] == 0 and r[1] == 0 and r[2] and "낼 문제가 없어요" in r[3], f"② 0문제 → 빈 시험지 대신 안내 {r}")
        await E(ns["TEST_CFG"], [S["g34"], 0, 2, ["match"], 20, True, True, True, 7])
        r = await E("()=>__chk()")
        ok(r["total"] == 20 and not r["iss"], f"③ 선 잇기만 20문제 = 20 · 답안지 맞음 {r['total']} {r['iss'][:2]}")
        found = []
        for s, ty in ((S["k"], ["mean"]), (S["r1"], ["mean", "k2e"])):
            for seed in range(1, 25):
                await E(ns["TEST_CFG"], [s, 0, 2, ty, 20, True, True, False, seed])
                r = await E("()=>__chk()"); found += [x for x in r["iss"] if x[0] in ("DUPOPT", "MEAN_OVERLAP", "K2E_OVERLAP", "NOANS", "FEWOPT")]
        ok(not found, f"④ 보기 뜻 겹침·같은 보기 없음 (사이트 워드 · 리딩 1 · 씨앗 24개씩) {found[:3]}")
        await E("()=>Paper.open({mode:'kw'})"); await pg.wait_for_timeout(1200); await E(ns["HELP"])
        await E(ns["KJ_CFG"], [S["g34"], 0, 59, 50, 5, True, "quiz"]); await pg.wait_for_timeout(300)
        r = await E("()=>{ const K=[...document.querySelectorAll('#ppWrap .pp.key')]; return [K.length, K.map(p=>p.querySelector('header').textContent.slice(0,40)), [...document.querySelectorAll('#ppWrap .pp:not(.key)')].every(p=>p.querySelector('.kjB'))]; }")
        ok(r[0] >= 2 and all("답안지" in h for h in r[1]) and "(이어서)" in r[1][-1] and r[2], f"⑤ 따라쓰기 답안지 둘째 쪽 = 답안지 (이어서) · 학습지 쪽엔 다 문제 {r}")
        await E("()=>Paper.open({mode:'test'})"); await pg.wait_for_timeout(1000); await E(ns["HELP"])
        await E(ns["TEST_CFG"], [S["g34"], 0, 2, ["prep"], 20, True, True, True, 7])
        r = await E("()=>document.getElementById('ppInfo').textContent")
        ok("고른 형식으로 낼 수 있는 단어가 모자라" in r and "범위 단어가 모자라" not in r, f"⑥ 안내 말 {r[-70:]}")
        ok(not real_errs(errs), f"JS 오류 없음 {real_errs(errs)[:2]}")
        await br.close()
    print("DONE bad=%d" % len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
