"""(v431) 🎮 미니게임 5종 — 사용자: "미니게임들을 업데이트해 줘야 하고" (예전 3개는 다 '먼저 맞히기')
  🎈 풍선 터뜨리기 · 🔨 두더지 잡기 · 🔤 철자 조립 · 🃏 짝 맞추기 · ⭕ OX 스피드
  · 자리마다 따로 도는 게임 · 같은 단어 순서 · 위쪽 자리는 거꾸로 · 시간 끝 = 점수 순위
  · 보드 라운드 끝 = 섞인 순서로 하나씩 · 설정 화면 「🎮 미니게임만 해 보기」"""
import asyncio, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

KS = ["balloon", "mole", "spell", "memory", "ox"]

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch()
        pg = await br.new_page(viewport={"width": 1024, "height": 768}); pg.on("pageerror", lambda e: errs.append(str(e)))
        await boot(pg); E = pg.evaluate
        async def until(js, n=60):
            for _ in range(n):
                if await E(js): return True
                await pg.wait_for_timeout(200)
            return False
        OPEN = """([k,np,sec])=>{ const c={set:'elem',from:0,to:3,words:[],qt:['mean']}, x=Object.create(Battle); x._ws=null; x.cfg=()=>c;
            const P=[{n:'루아',ch:0},{n:'주호',ch:3},{n:'라언',ch:4},{n:'단우',ch:7}].slice(0,np).map((p,i)=>Object.assign(p,{i,col:Board.COL[i]}));
            window._r=null; MG.open({title:MiniG.L[k][0], sub:MiniG.L[k][1], P, ctx:x, kind:k, sec}, sc=>window._r=sc); }"""
        for k in KS:
            await E(OPEN, [k, 3, 6])
            r = await E("()=>[document.querySelector('#bdMG').classList.contains('game'), !!document.querySelector('.mgIntro'), document.querySelector('.mgIntro b').textContent]")
            ok(r[0] and r[1], f"{k}: 게임 화면 · 3·2·1 안내 {r[2]!r}")
            ok(await until("()=>!document.querySelector('.mgIntro') && MG.o && MG.o.inst && MG.o.inst.length===3"), f"{k}: 자리 3개에 게임이 하나씩")
            r = await E("()=>[MG.o.inst.every(g=>g.S===MG.o.inst[0].S), MG.o.inst.map(g=>g.cur().en), [...document.querySelectorAll('#bdMG .mgZ')].map(z=>z.classList.contains('flip'))]")
            ok(r[0] and len(set(r[1])) == 1 and r[2] == [True, True, False], f"{k}: 모두 같은 단어 순서 · 위 두 자리는 거꾸로 {r[1]} {r[2]}")
            # 루아: 맞히기 · 주호: 틀리기
            for _ in range(45):
                if await E("()=>MG.o.inst[0].sc>=2"): break
                await E("()=>MG.o.inst[0].auto()"); await pg.wait_for_timeout(120)
            r = await E("()=>{ const g=MG.o.inst[1], s0=g.sc, w=g.wrong(); return [w, g.sc, g.lock>0 || g.kind==='memory', MG.o.inst[0].sc]; }")
            ok(r[3] >= 2, f"{k}: 맞히면 점수 올라감 {r[3]}")
            ok(r[0] and r[1] == 0 and r[2], f"{k}: 틀리면 점수 없음(두더지는 −1, 0 아래로 안 감) · 잠깐 멈춤 {r}")
            await pg.wait_for_timeout(500)
            sc_el = await E("()=>document.getElementById('mgS0').textContent")
            ok(int(sc_el) == await E("()=>MG.o.inst[0].sc"), f"{k}: 자리 위 점수 = 게임 점수 {sc_el}")
            ok(await E("()=>/⏱ \\d/.test(document.getElementById('mgMid').textContent)"), f"{k}: 가운데 남은 시간")
            await pg.screenshot(path=OUT + f"mini431_{k}.png")
            ok(await until("()=>!!document.querySelector('.mgEnd')", 60), f"{k}: 시간 끝 → 순위")
            ok(await until("()=>!!window._r", 30), f"{k}: 끝나면 점수를 돌려줌")
            r = await E("()=>[window._r, !document.getElementById('bdMG')]")
            ok(r[0]["0"] >= 2 and r[0]["1"] == 0 and r[1], f"{k}: 점수 {r[0]} · 화면 닫힘")
        # 두더지: 틀리면 −1
        await E(OPEN, ["mole", 2, 20]); await until("()=>MG.o && MG.o.inst")
        r = await E("()=>{ const g=MG.o.inst[0]; g.auto(); g.lock=0; g.auto(); g.lock=0; const a=g.sc; g.wrong(); return [a, g.sc]; }")
        ok(r[0] == 2 and r[1] == 1, f"🔨 맞는 두더지 +1 · 틀린 두더지 −1 {r}")
        # 짝 맞추기: 6쌍 다 찾으면 +2 · 새 카드
        await E("()=>MG.close()")
        await E(OPEN, ["memory", 2, 30]); await until("()=>MG.o && MG.o.inst")
        for _ in range(6):
            await E("()=>MG.o.inst[0].auto()"); await pg.wait_for_timeout(60)
        await pg.wait_for_timeout(1000)
        r = await E("()=>[MG.o.inst[0].sc, MG.o.inst[0].M.querySelectorAll('.mgC').length, MG.o.inst[0].M.querySelectorAll('.got').length]")
        ok(r == [8, 12, 0], f"🃏 6쌍 = 6 + 다 찾으면 2 · 새 카드 12장 {r}")
        # 철자: 글자 순서 · 다 맞추면 1점
        await E("()=>MG.close()")
        await E(OPEN, ["spell", 2, 30]); await until("()=>MG.o && MG.o.inst")
        r = await E("()=>{ const g=MG.o.inst[0]; const w=g.w, n=g.TL.children.length; let k=0; while(g.k<w.length && k++<20){ g.auto(); } return [w, n, g.sc, [...g.SL.children].map(i=>i.textContent).join('')]; }")
        ok(r[2] == 1 and r[3] == r[0] and r[1] > len(r[0]), f"🔤 글자 + 헷갈리는 글자 · 순서대로 → 단어 완성 1점 {r}")
        await E("()=>MG.close()")
        # 폰 4명 = 2×2
        await pg.set_viewport_size({"width": 430, "height": 932})
        await E(OPEN, ["balloon", 4, 30]); await until("()=>MG.o && MG.o.inst")
        await pg.wait_for_timeout(1500)
        r = await E("()=>{ const z=[...document.querySelectorAll('#bdMG .mgZ')].map(e=>e.getBoundingClientRect()); return [z.length, z.every(b=>b.width>180 && b.height>380), [...document.querySelectorAll('.mgB span')].every(s=>s.scrollWidth<=s.clientWidth+1)]; }")
        ok(r[0] == 4 and r[1] and r[2], f"📱 폰 4명 = 2×2 자리 · 풍선 글자가 안 잘림 {r}")
        await pg.screenshot(path=OUT + "mini431_phone.png")
        await E("()=>MG.close()")
        await pg.set_viewport_size({"width": 1024, "height": 768})
        # 보드 라운드 끝 → 새 미니게임 (섞인 순서) → 🪙
        await E("()=>Board.begin({sk:'k', set:'elem', from:0, to:2, qt:['mean'], sec:0, rounds:3, P:[{n:'루아',id:'',ch:0},{n:'주호',id:'',ch:3}]})")
        await until("()=>!!document.querySelector('[data-bd=roll]')")
        await E("()=>{ const B=Board, o=B.o; clearTimeout(B._to); B.act(''); o.P.forEach(p=>p.coin=0); o.cur=1; B.endTurn(); }")
        ok(await until("()=>MG.o && MG.o.game && !document.querySelector('.mgIntro') && MG.o.inst", 50), "라운드 끝 → 새 미니게임")
        r = await E("()=>[Board.o.mgL.slice().sort().join(), MG.o.cfg.kind===Board.o.mgL[0]]")
        ok(r[0] == ",".join(sorted(KS)) and r[1], f"5종을 섞어서 하나씩 {r}")
        await E("()=>{ MG.o.t=30; }")
        for _ in range(10):
            await E("()=>MG.o && MG.o.inst[0].auto()"); await pg.wait_for_timeout(150)
        await E("()=>{ MG.o.t=0.01; }")
        ok(await until("()=>!document.getElementById('bdMG')", 40), "미니게임 끝")
        await pg.wait_for_timeout(400)
        r = await E("()=>[Board.o.P.map(p=>p.coin), Board.o.rnd]")
        ok(r[0][0] == 10 and r[0][1] == 0 and r[1] == 2, f"🥇 루아 🪙10 · 0점은 없음 · 라운드 2 {r}")
        await E("()=>{ Board.o.fin=true; Board.close(); }")
        # 설정 화면 「미니게임만 해 보기」
        await E("()=>Board.setup()"); await pg.wait_for_timeout(300)
        r = await E("()=>[...document.querySelectorAll('[data-bd=mgtry]')].map(b=>b.dataset.k)")
        ok(r == KS, f"설정 화면 🎮 미니게임만 해 보기 5개 {r}")
        await E("()=>document.querySelector('[data-bd=mgtry][data-k=ox]').click()")
        ok(await until("()=>MG.o && MG.o.cfg.kind==='ox' && document.querySelectorAll('#bdMG .mgZ').length===2 && !!MG.o.inst"), "⭕ 연습 = 설정의 친구 2명")
        await E("()=>{ MG.o.t=0.01; }")
        ok(await until("()=>!document.getElementById('bdMG') && !!document.getElementById('bdSetup')", 40), "연습 끝 → 설정 화면 그대로")
        await E("()=>Board.close()")
        ok(not real_errs(errs), "오류 없음 " + str(real_errs(errs)[:3]))
        await br.close()
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)

asyncio.run(main())
