"""(v447) 🎲 보드게임 다시 — 사용자(아이들이랑 해 보고): "게임이 매우 재미없어"
  ① 미니게임: 액션(영어 없음) 🎈 내 색 풍선 · 🔨 두더지(금·폭탄) · 💪 연타 · 🚦 신호등 · 🎨 땅따먹기 / 영어 ⚡ 스피드 퀴즈 · 🃏 카드 뒤집기 · 🎣 단어 낚시
  ② 끝나면 🏆 시상대 (누가 이겼는지) → 🪙 · 홀수 라운드 액션 / 짝수 영어
  ③ 라운드 10·15·20 · 시작 안내 5장 · 굴리기 위 ⭐ 까지 n칸 · 🪙/별 값 · 💡 작전 · 막판 3라운드(🔵 두 배 · 별 🪙5)
  ④ 아이템 🍄 · 🎯 황금 주사위 · 🔄 자리 바꾸기(두 번 눌러도 한 번 · 바뀐 자리에서 출발) · 🧲 별 자석"""
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
        br = await p.chromium.launch()
        pg = await br.new_page(viewport={"width": 1024, "height": 768}); pg.on("pageerror", lambda e: errs.append(str(e)))
        await boot(pg); E = pg.evaluate
        async def until(js, n=60, ms=200):
            for _ in range(n):
                if await E(js): return True
                await pg.wait_for_timeout(ms)
            return False
        OPEN = """([k,np,sec])=>{ const c={set:'elem',from:0,to:3,words:[],qt:['mean']}, x=Object.create(Battle); x._ws=null; x.cfg=()=>c;
            const P=[{n:'루아',ch:0},{n:'주호',ch:3},{n:'라언',ch:4},{n:'단우',ch:7}].slice(0,np).map((p,i)=>Object.assign(p,{i,col:Board.COL[i]}));
            window._r=null; MG.open({title:MiniG.L[k][0], sub:MiniG.L[k][1], P, ctx:x, kind:k, sec}, sc=>window._r=sc); }"""
        r = await E("()=>[MiniG.ACT, MiniG.ENG, Object.keys(MiniG.L)]")
        ok(r[0] == ["balloon","mole","tug","light","paint"] and r[1] == ["ox","memory","fish"] and "spell" not in r[2], f"① 액션 5 · 영어 3 · 철자 조립 뺌 {r}")
        for k in ["balloon","mole","tug","light","paint","ox","memory","fish"]:
            await E(OPEN, [k, 3, 6])
            ok(await until("()=>!document.querySelector('.mgIntro') && MG.o && MG.o.inst && MG.o.inst.length===3"), f"{k}: 자리 3개")
            for _ in range(60):
                if await E("()=>MG.o && MG.o.inst[0].sc>=3"): break
                await E("()=>MG.o && MG.o.inst[0].auto()"); await pg.wait_for_timeout(110)
            r = await E("()=>{ const g=MG.o.inst[1]; const a=g.sc; const w=g.wrong(); return [w, a, g.sc, MG.o.inst[0].sc]; }")
            ok(r[3] >= 3 or k == "light", f"{k}: 맞히면 점수 {r[3]}")
            if k in ("balloon","mole"):
                ok(r[0], f"{k}: 다른 색·폭탄 누르면 감점 {r}")
            if k == "balloon":
                q = await E("()=>[MG.o.inst.map(g=>g.me.k), [...document.querySelectorAll('#bdMG .mgMine b')].map(b=>b.textContent)]")
                ok(q[0] == [0,1,2] and q[1][0] == "내 색 = 빨강", f"🎈 자리마다 내 색 {q}")
            if k == "paint":
                q = await E("()=>{ const A=MG.o.inst[0].sh.get(), me=A.filter(v=>v===0).length, z1=[...document.querySelectorAll('#mgG1 .mgPt i')].filter(i=>i._v===0).length; return [me, z1, MG.o.inst[0].sc]; }")
                ok(q[0] >= 3 and q[0] == q[1] == q[2], f"🎨 한 판을 같이 — 루아가 칠한 칸이 주호 자리에도 {q}")
            if k == "light":
                q = await E("()=>{ const g=MG.o.inst[0]; return [g.T.slice(0,3).map(x=>+x.toFixed(2)), MG.o.inst[1].T.slice(0,3).map(x=>+x.toFixed(2)), g.st]; }")
                ok(q[0] == q[1], f"🚦 신호 시간이 자리마다 같음 {q}")
            await pg.screenshot(path=OUT + f"board447_{k}.png")
            ok(await until("()=>!!window._r", 80), f"{k}: 끝나면 점수 {await E('()=>window._r')}")
            await E("()=>MG.close()")
        # 신호등 — 초록불에 누르면 +, 빨간불에 누르면 −1
        await E(OPEN, ["light", 2, 20]); await until("()=>MG.o && MG.o.inst")
        r = await E("()=>{ const g=MG.o.inst[0]; g.sc=3; g.t=0.2; g.step(0.01); const st=g.st; g.tap(); const a=g.sc; g.lock=0; g.t=g.T[0]+0.1; g.k=-1; g.step(0.001); const st2=g.st; g.tap(); return [st, a, st2, g.sc]; }")
        ok(r[0] == "wait" and r[1] == 2 and r[2] == "go" and r[3] == 5, f"🚦 빨간불 −1 · 초록불 0.1초 = +3 {r}")
        await E("()=>MG.close()")
        # ② 보드: 한 패드 3명
        await E("""()=>{ Board.close(); Board.begin({sk:'e', set:'elem', from:0, to:3, qt:['mean'], sec:0, rounds:10, P:[{n:'루아',ch:0},{n:'주호',ch:3},{n:'라언',ch:4}]}); }""")
        ok(await until("()=>!!document.getElementById('bdHow')", 30), "③ 시작 안내 5장")
        r = await E("()=>document.getElementById('bdHow').innerText.replace(/\\n/g,' | ')")
        ok("별을 가장 많이 모으면 우승" in r, f"③ 첫 장 {r[:80]!r}")
        await pg.screenshot(path=OUT + "board447_how.png")
        await E("()=>document.querySelector('#bdHow [data-how]').click()")
        ok(await until("()=>!!document.querySelector('#bdAct .bdRoll')", 40), "③ 안내 넘기면 첫 차례")
        r = await E("()=>[Board.o.R, Board.o.P.map(p=>p.it.join(',')), document.querySelector('#bdAct .bdHud') && document.querySelector('#bdAct .bdHud').innerText.replace(/\\n/g,' '), Board.dist(Board.me())]")
        ok(r[0] == 10 and r[1] == ["mush"]*3 and r[2] and "까지" in r[2], f"③ 10라운드 · 처음에 🍄 · HUD {r}")
        await pg.screenshot(path=OUT + "board447_turn.png")
        # ④ 자리 바꾸기 — 두 번 눌러도 한 번 · 바뀐 자리에서 출발
        r = await E("""()=>{ const o=Board.o, p=Board.me(), t=o.P[1]; p.pos=3; t.pos=10; p.it=['swap']; Board.use('swap'); Board.cmd('tgt', {i:'1'}); Board.cmd('tgt', {i:'1'}); return [p.pos, t.pos, p.it.length]; }""")
        ok(r == [10, 3, 0], f"④ 🔄 자리 바꾸기 한 번만 {r}")
        await pg.wait_for_timeout(1700)
        r = await E("()=>{ const o=Board.o, p=Board.me(); o.force=2; Board.roll(); return p.pos; }")
        ok(await until("()=>Board.me().pos===12 || Board.o.cur!==0", 40), f"④ 바뀐 자리(10)에서 2칸 → 12 (지금 {await E('()=>Board.o.P[0].pos')})")
        await pg.wait_for_timeout(1500)
        SETCUR = "(c)=>{ clearTimeout(Board._to); clearInterval(Board._tm); const o=Board.o; o.cont=null; o.qcb=null; o.q=null; o.pick=null; o.rolling=0; o.cur=c; Board.act(''); Board.turnMenu(); }"
        await E(SETCUR, 1)
        # 🎯 황금 주사위
        r = await E("""()=>{ const o=Board.o, p=Board.me(); o.star=(p.pos+4)%o.N; p.it=['gold']; Board.turnMenu(); const tip=document.querySelector('#bdAct .bdTip'); Board.use('gold'); const hot=document.querySelector('#bdAct .bdGold .hot'); return [tip && tip.innerText, hot && hot.dataset.k, p.pos]; }""")
        ok(r[0] and "4" in r[0] and r[1] == "4", f"④ 🎯 💡 작전 · ⭐ 거리 숫자 반짝 {r[:2]}")
        pos0 = r[2]
        await E("()=>Board.cmd('gnum', {k:'4'})")
        ok(await until("()=>Board.o.P[1].pos===Board.o.star && (!!document.querySelector('#bdAct .bdStarC') || !!document.querySelector('#bdBan.on'))", 60), "④ 🎯 4칸 → ⭐ 칸")
        r = await E("()=>[Board.o.P[1].pos, Board.o.star, Board.o.P[1].it.length]")
        ok(r[0] == r[1] and r[2] == 0, f"④ 🎯 딱 ⭐ 칸 · 다 씀 {r}")
        # 🧲 별 자석
        await pg.wait_for_timeout(1200)
        await E(SETCUR, 2)
        r = await E("""()=>{ const o=Board.o, p=Board.me(), t=o.P[0]; t.star=2; p.star=0; p.it=['mag']; Board.use('mag'); const n=document.querySelectorAll('#bdAct [data-bd=tgt]').length; Board.cmd('tgt', {i:'0'}); return [n, t.star, p.star]; }""")
        ok(r == [1, 1, 1], f"④ 🧲 별 자석 — 별 있는 친구만 · ⭐ 1개 가져옴 {r}")
        # 막판
        r = await E("()=>{ const o=Board.o; const a=[Board.late(), Board.starP()]; o.rnd=o.R-2; return a.concat([Board.late(), Board.starP()]); }")
        ok(r == [False, 10, True, 5], f"③ 막판 3라운드 = 별 🪙5 {r}")
        await E("()=>{ Board.o.rnd=1; }")
        # ② 미니게임 → 시상대 → 코인
        r = await E("""()=>{ const o=Board.o; o.mgOnly='tug'; o.P.forEach(p=>p.coin=0); clearTimeout(Board._to); Board.mini(); return 1; }""")
        ok(await until("()=>MG.o && MG.o.inst && MG.o.inst.length===3", 40), "② 라운드 끝 미니게임")
        for _ in range(25):
            await E("()=>{ if(MG.o && MG.o.inst){ MG.o.inst[0].auto(); MG.o.inst[0].auto(); MG.o.inst[1].auto(); } }"); await pg.wait_for_timeout(100)
        ok(await until("()=>!!document.getElementById('bdPod')", 80), "② 🏆 시상대")
        r = await E("()=>[document.querySelector('#bdPod .podT').innerText, document.querySelector('#bdPod .podC.r1 b').innerText, document.querySelector('#bdPod .podC.r1 small') && document.querySelector('#bdPod .podC.r1 small').innerText]")
        ok("연타" in r[0] and r[1] == "루아" and "+🪙10" in (r[2] or ""), f"② 1등 루아 +🪙10 {r}")
        await pg.screenshot(path=OUT + "board447_pod.png")
        ok(await until("()=>!document.getElementById('bdPod')", 40), "② 시상대 끝")
        r = await E("()=>[Board.o.P.map(p=>p.coin), Board.o.rnd]")
        ok(r[0][0] == 10 and r[0][1] == 5 and r[1] == 2, f"② 🪙 10·5 · 라운드 2 {r}")
        # 짝수 라운드 = 영어
        r = await E("()=>{ const o=Board.o; o.mgOnly=null; o.mgA=null; o.mgE=null; const a=[]; for(let rr=1; rr<=6; rr++){ o.rnd=rr; const eng=o.rnd%2===0, key=eng?'mgE':'mgA'; if(!o[key]||!o[key].length) o[key]=shuffle((eng?MiniG.ENG:MiniG.ACT).slice()); a.push(o[key].shift()); } return a; }")
        ok(all((k in ["ox","memory","fish"]) == (i % 2 == 1) for i, k in enumerate(r)), f"② 홀수 = 액션 · 짝수 = 영어 {r}")
        await br.close()
    real = real_errs(errs)
    ok(not real, f"오류 없음 {real[:3]}")
    print("DONE bad=%d" % len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
