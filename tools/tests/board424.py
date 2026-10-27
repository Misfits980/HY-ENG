"""(v424→v429) 🎲 영어 파티 보드 규칙 (3D 없이 — 3D 화면은 board428)
  사용자: "보드게임처럼 영어를" → v428 "해 보는데 너무 재미가 없는데? 요소가 너무 재미없어" → 🎉 마리오 파티처럼 (사용자 "그래")
  ① 설정: 판 2개 · 2~4명 명단 · 라운드 3/5/7
  ② 판: 🚩 출발 · 🔵 +3 · 🔴 −3(맞히면 지킴) · ⚔️ 결투 · ❓ 깜짝 · 🏪 상점 · ⭐ 별(🪙10 + 문제)
  ③ 아이템: 🍄 주사위 2개 · 🔒 함정 · 🔄 자리 바꾸기 · 🧲 자석
  ④ 라운드 끝 = 🎮 미니게임(한 패드 · 자리마다 같은 문제 · 먼저 맞히기) → 🪙 10·5·2
  ⑤ 마지막 = 🎁 보너스 별 → 🏆 별 많은 사람 · 💎 10·7·5 (이 기기 = 바로 · 다른 아이 = 🎁 배달) · 직접 쓴 이름 = 연습 · 하루 2판"""
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
        br = await p.chromium.launch()
        ctx = await br.new_context(viewport={"width": 1024, "height": 768}, service_workers="block")
        await ctx.add_init_script("window.HY_FB_LOCAL=true; try{ if(!localStorage.getItem('hyeng_t0')){ localStorage.clear(); localStorage.setItem('hyeng_t0','1'); localStorage.setItem('hyeng_nick','루아'); } }catch(e){}")
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await boot(pg); E = pg.evaluate
        async def until(js, n=60):
            for _ in range(n):
                if await E(js): return True
                await pg.wait_for_timeout(200)
            return False
        await E("()=>FB.set('/hy/roster',{t:{a1:{n:'유치부',e:'🧸'}}, k:{k1:{n:'루아',t:'a1'}, k2:{n:'주호',t:'a1'}, k3:{n:'라언',t:'a1'}}}).then(()=>HyBoss.refresh(true))")
        ok(await E("()=>(Kid.me()||{}).id") == "k1", "이 기기 = 루아")
        ok(await E("()=>document.querySelector('#selRule [data-v=board]').offsetHeight===0"), "(v427) 시작 화면 🎲 카드는 아직 숨김")
        # (v430) 새 3D 아이콘 그림 — 카드·상점·명단에 그림으로
        r = await E("()=>Promise.all(['blue','red','duel','event','shop','star','start','trap','mush','lock','swap','mag','coins','dice','trophy','gift'].flatMap(n=>['k','e'].map(s=>fetch('assets/board/'+s+'/'+n+'.webp').then(x=>x.ok)))).then(a=>a.every(Boolean))")
        ok(r, "아이콘 16개 × 판 2개 그림 파일")
        # ① 설정
        await E("()=>Board.setup()"); await pg.wait_for_timeout(500)
        r = await E("()=>[!!document.getElementById('bdSetup'), document.querySelectorAll('.bdSkB').length, document.querySelectorAll('.bdSeat').length, document.getElementById('bdFrom').options.length>0, [...document.querySelectorAll('#bdRnd option')].map(o=>+o.value)]")
        ok(r == [True, 2, 2, True, [3, 5, 7]], f"설정: 판 2개 · 기본 2명 · Stage · 라운드 3/5/7 {r}")
        await E("()=>document.querySelector('[data-bd=add]').click()")
        await E("""()=>{ const S=[...document.querySelectorAll('.bdSeat select')]; S[0].value='k1'; S[0].dispatchEvent(new Event('change',{bubbles:true})); }""")
        await E("""()=>{ const S=[...document.querySelectorAll('.bdSeat select')]; S[1].value='k2'; S[1].dispatchEvent(new Event('change',{bubbles:true})); }""")
        sel = await E("()=>[...document.querySelectorAll('.bdSeat select')][2].innerHTML")
        ok("k1" not in sel and "k2" not in sel, "이미 고른 아이는 다른 자리 목록에서 빠짐")
        await E("()=>{ Board._seats[2]={n:'손님', id:'', ch:4}; Board.seats(); document.querySelector('[data-sk=k]').click(); document.getElementById('bdRnd').value='3'; }")
        await E("()=>document.querySelector('[data-bd=go]').click()")
        r = await E("""()=>{ const o=Board.o, c={}; o.T.forEach(k=>c[k]=(c[k]||0)+1); return [o.cfg.sk, o.R, o.N, c, o.P.map(p=>[p.n,p.coin,p.star]), o.T[o.star]]; }""")
        ok(r[0] == "k" and r[1] == 3 and r[2] == 29 and r[4] == [["루아", 10, 0], ["주호", 10, 0], ["손님", 10, 0]] and r[5] == "blue", f"🧸 판 · 3 라운드 · 29칸(새 그림) · 모두 🪙10 · ⭐ 는 파란 칸 위 {r}")
        ok(r[3] == {"start": 1, "shop": 2, "duel": 3, "event": 4, "red": 6, "blue": 13}, f"칸: 🚩1 🏪2 ⚔️3 ❓4 🔴6 🔵13 {r[3]}")
        ok(await E("()=>{ const T=Board.o.T; return T.every((k,i)=>k==='blue'||k==='start'||k==='shop'|| (T[(i+1)%T.length]!==k)); }"), "같은 특별 칸이 붙어 있지 않음")
        # ② 차례 → 🎲 → 🔵 +3
        ok(await until("()=>!!document.querySelector('[data-bd=roll]')"), "루아 차례 · 🎲 굴리기")
        await E("()=>{ const o=Board.o; o.T[1]='blue'; o.T[2]='blue'; o.T[3]='blue'; o.star=20; o.force=3; document.querySelector('[data-bd=roll]').click(); }")
        ok(await until("()=>Board.o.cur===1"), "3칸 가고 다음 친구")
        r = await E("()=>[Board.o.P[0].pos, Board.o.P[0].coin]")
        ok(r == [3, 13], f"🔵 파란 칸 = 🪙 +3 {r}")
        # 이제부터 직접 부름 (타이머 정리)
        S = "const B=Board, o=B.o, w=ms=>new Promise(r=>setTimeout(r,ms)); clearTimeout(B._to); clearInterval(B._tm); B.act('');"
        RIGHT = "q=>q.opts.findIndex((x,i)=>B.right(q,i))"
        # 🔴 −3 / 맞히면 지킴
        r = await E("""async()=>{ %s const R={}, rt=%s; o.cur=1; const p=o.P[1]; p.coin=10;
            B.tile('red'); await w(1300); R.why=o.why; B.answer(rt(o.q)+100); await w(2000); clearTimeout(B._to); R.lose=p.coin;
            B.tile('red'); await w(1300); B.answer(rt(o.q)); await w(1100); clearTimeout(B._to); R.keep=p.coin; return R; }""" % (S, RIGHT))
        ok(r["why"] == "red" and r["lose"] == 7 and r["keep"] == 7, f"🔴 틀리면 🪙 −3 · 맞히면 지킴 {r}")
        # ⭐ 별: 🪙 부족 → 그냥 지나감 · 🪙10 + 맞힘 → 별 +1 · 별이 다른 칸으로
        r = await E("""async()=>{ %s const R={}, rt=%s; o.cur=1; const p=o.P[1]; p.pos=5; p.coin=4; o.star=7; o.T[6]='blue'; o.T[7]='blue'; o.T[8]='blue';
            B.walk(3); await w(2600); R.poor=[p.pos, p.star, o.star]; clearTimeout(B._to); B.act('');
            o.cur=1; p.pos=5; p.coin=15; B.walk(3); await w(1200); R.card=!!document.querySelector('.bdStarC');
            document.querySelector('[data-bd=star]').click(); await w(300); R.hq=o.q && o.q.t; R.hctx=o.why; B.answer(rt(o.q)); await w(4800);
            R.got=[p.star, p.coin, o.star!==7, o.T[o.star]]; await w(1500); R.pos=p.pos; clearTimeout(B._to); return R; }""" % (S, RIGHT))
        ok(r["poor"][1] == 0 and r["poor"][0] == 8, f"🪙 모자라면 ⭐ 그냥 지나감 {r['poor']}")
        ok(r["card"] and r["hctx"] == "star", f"⭐ 지나가다 멈춰서 '별을 살까요?' · 별 문제 {r}")
        ok(r["got"][0] == 1 and r["got"][1] == 8 and r["got"][2] and r["got"][3] == "blue", f"⭐ 맞히면 별 +1 · 🪙 15−10 (+🔵3) · 별은 다른 파란 칸으로 {r['got']}")
        ok(r["pos"] == 8, f"별을 사고 남은 칸을 마저 감 (5 → 8) {r['pos']}")
        # 🏪 상점 · 🍄 버섯 = 주사위 2개
        r = await E("""async()=>{ %s const R={}; o.cur=0; const p=o.P[0]; p.coin=20; p.it=[]; o.star=25;
            B.shop(); await w(100); R.dis=[...document.querySelectorAll('.bdShop [data-bd=buy]')].filter(b=>b.disabled).length; B.buy('mush'); await w(200); clearTimeout(B._to); R.it=p.it.slice(); R.coin=p.coin;
            o.cur=0; B.turnMenu(); R.bag=!!document.querySelector('[data-bd=bag]'); B.bag(); B.use('mush'); R.two=document.querySelector('.bdRoll').textContent;
            p.pos=10; for(let i=11;i<=15;i++) o.T[i]='blue'; o.force=2; B.roll(); await w(2500); clearTimeout(B._to); R.pos=p.pos; R.it2=p.it.length; return R; }""" % (S,))
        ok(r["dis"] == 0 and r["it"] == ["mush"] and r["coin"] == 15, f"🏪 상점에서 🍄 사기 (🪙 −5) {r}")
        await E("()=>{ clearTimeout(Board._to); Board.o.cur=0; Board.o.rolling=0; Board.turnMenu(); return 1; }")
        r2 = await E("()=>[document.querySelectorAll('.bdRoll img.bdIc[src$=\"dice.webp\"]').length, document.querySelectorAll('#bdPl img.bdIc[src$=\"star.webp\"]').length]")
        ok(r2[0] == 1 and r2[1] == 3, f"🎲 단추 · 명단 별 = 그림 아이콘 {r2}")
        ok(r["bag"] and "두 번" in r["two"] and r["pos"] == 14 and r["it2"] == 0, f"🎒 🍄 쓰면 주사위 2개 (2+2 = 4칸) {r}")
        # 🔒 함정
        r = await E("""async()=>{ %s const R={}; o.cur=0; const a=o.P[0], b=o.P[1]; a.it=['trap']; a.pos=12; o.T[12]='blue'; a.coin=5; b.coin=9;
            B.use('trap'); R.trap=o.trap[12]; clearTimeout(B._to); o.cur=1; b.pos=12; B.land(); await w(2900); clearTimeout(B._to); R.c=[a.coin, b.coin, o.trap[12]]; return R; }""" % (S,))
        ok(r["trap"] == 0 and r["c"] == [10, 7, None], f"🔒 함정: 친구가 밟으면 🪙5 가져옴 (+🔵3 은 밟은 친구) {r}")
        # 🔄 자리 바꾸기 · 🧲 자석
        r = await E("""async()=>{ %s const R={}; o.cur=0; const a=o.P[0], b=o.P[2]; a.pos=3; b.pos=20; a.it=['swap','mag']; a.coin=0; b.coin=8;
            B.use('swap'); R.tg=[...document.querySelectorAll('[data-bd=tgt]')].map(x=>+x.dataset.i); B.tgt(2); R.sw=[a.pos, b.pos]; await w(200); clearTimeout(B._to);
            B.use('mag'); B.tgt(2); R.mg=[a.coin, b.coin, a.it.length]; clearTimeout(B._to); return R; }""" % (S,))
        ok(r["tg"] == [1, 2] and r["sw"] == [20, 3], f"🔄 친구 골라 자리 바꾸기 {r}")
        ok(r["mg"] == [3, 5, 0], f"🧲 친구 🪙3 끌어오기 {r['mg']}")
        # ❓ 깜짝
        r = await E("""async()=>{ %s const R={}; const P=o.P; P.forEach(p=>{ p.coin=10; p.star=0; }); o.cur=0;
            B.event('rain'); await w(1700); clearTimeout(B._to); R.rain=P[0].coin;
            B.event('gift'); await w(1700); clearTimeout(B._to); R.gift=P.map(p=>p.coin);
            P[2].star=2; P[2].coin=6; B.event('robin'); await w(1700); clearTimeout(B._to); R.robin=[P[0].coin, P[2].coin];
            return R; }""" % (S,))
        ok(r["rain"] == 15 and r["gift"] == [17, 12, 12] and r["robin"] == [20, 3], f"❓ 코인 비 +5 · 모두 +2 · 🏹 1등에게서 🪙3 {r}")
        # ⚔️ 결투 = 2명 미니게임 · 이긴 사람 🪙5
        await E("""()=>{ %s o.cur=0; o.P[0].coin=10; o.P[1].coin=10; o.P[0].dw=0; B.tile('duel'); }""" % (S,))
        ok(await until("()=>!!document.querySelector('#bdAct [data-bd=tgt]')"), "⚔️ 결투 칸 → 상대 고르기")
        await E("()=>document.querySelector('#bdAct [data-bd=tgt][data-i=\"1\"]').click()")
        ok(await until("()=>!!document.querySelector('#bdMG .mgZ') && !document.querySelector('.mgIntro')", 40), "결투 화면 (3·2·1)")
        r = await E("()=>[document.querySelectorAll('#bdMG .mgZ').length, document.querySelector('#bdMG .z0').classList.contains('flip'), document.querySelector('#bdMG .z1').classList.contains('flip'), [...document.querySelectorAll('#mgO0 button')].map(b=>b.textContent).sort().join()==[...document.querySelectorAll('#mgO1 button')].map(b=>b.textContent).sort().join()]")
        ok(r == [2, True, False, True], f"2명 = 위아래 반 · 위쪽은 거꾸로 · 같은 문제 {r}")
        await pg.screenshot(path=OUT + "board424_duel.png")
        # 주호가 한 번 틀림 → 잠김 → 루아가 맞힘
        r = await E("()=>{ const q=MG.o.q, a=q.ans!=null?q.ans:q.opts.findIndex((x,i)=>MG.right(q,i)), w=(a+1)%q.opts.length; MG.tap(1,w); const lk=!!MG.o.lock[1]; MG.tap(1,a); const after=MG.o.sc[1]; MG.tap(0,a); return [lk, after, MG.o.sc[0]]; }")
        ok(r == [True, 0, 1], f"틀리면 그 문제는 잠김 · 먼저 맞힌 사람 1점 {r}")
        await until("()=>MG.o && MG.o.qi===2 && MG.o.won==null", 30)
        await E("()=>{ const q=MG.o.q; MG.tap(0, q.ans!=null?q.ans:q.opts.findIndex((x,i)=>MG.right(q,i))); }")
        ok(await until("()=>!document.getElementById('bdMG')", 40), "2점 먼저 = 결투 끝")
        await pg.wait_for_timeout(300)
        r = await E("()=>[Board.o.P[0].coin, Board.o.P[1].coin, Board.o.P[0].dw]")
        ok(r == [15, 5, 1], f"⚔️ 이긴 루아가 🪙5 가져옴 {r}")
        # 🎮 라운드 끝 = 미니게임 (모두) → 🪙 10·5·2
        await until("()=>Board.o.cur===1", 30)
        await E("""()=>{ %s o.P.forEach(p=>p.coin=0); o.cur=2; B.endTurn(); }""" % (S,))
        ok(await until("()=>!!document.querySelector('#bdMG .mgZ') && !document.querySelector('.mgIntro')", 50), "라운드 끝 → 🎮 미니게임")
        r = await E("()=>[document.querySelectorAll('#bdMG .mgZ').length, [...document.querySelectorAll('#bdMG .mgZ')].map(z=>z.classList.contains('flip')), MG.o.cfg.n]")
        ok(r == [3, [True, True, False], 5], f"3명 = 위 두 자리(거꾸로) + 아래 · 5문제 {r}")
        await pg.screenshot(path=OUT + "board424_mg.png")
        # 손님 2 · 주호 1 · 루아 0 — 나머지는 아무도 못 맞힘
        for who in [2, 2, 1, -1, -1]:
            await until("()=>MG.o && MG.o.q && MG.o.won==null", 40)
            if who >= 0:
                await E("(w)=>{ const q=MG.o.q; MG.tap(w, q.ans!=null?q.ans:q.opts.findIndex((x,i)=>MG.right(q,i))); }", who)
            else:
                await E("()=>{ const q=MG.o.q, a=q.ans!=null?q.ans:q.opts.findIndex((x,i)=>MG.right(q,i)); MG.o.P.forEach(p=>MG.tap(p.i,(a+1)%q.opts.length)); }")
            await until("()=>!MG.o || MG.o.won!=null", 20)
        ok(await until("()=>!document.getElementById('bdMG')", 60), "미니게임 끝")
        await pg.wait_for_timeout(300)
        r = await E("()=>[Board.o.P.map(p=>p.coin), Board.o.rnd]")
        ok(r == [[0, 5, 10], 2], f"🎮 1등 🪙10 · 2등 🪙5 · 0점은 없음 · 라운드 2 {r}")
        # ⑤ 마지막 라운드 → 🎁 보너스 별 → 🏆
        await until("()=>Board.o.cur===0 && !!document.querySelector('[data-bd=roll]')", 40)
        await E("""()=>{ %s const P=o.P; o.rnd=3; P[0].star=2; P[1].star=2; P[2].star=1; P[0].ok=5; P[1].ok=3; P[2].ok=3; P[0].dw=0; P[1].dw=2; P[2].dw=0; P[0].coin=4; P[1].coin=9; P[2].coin=20; o.cur=2;
            o.P.forEach(p=>p.it=[]); B.endTurn(); }""" % (S,))
        await until("()=>!!document.querySelector('#bdMG .mgZ') && !document.querySelector('.mgIntro')", 50)
        await E("()=>{ MG.o.cfg.n=0; }")
        for _ in range(3):
            await until("()=>!MG.o || (MG.o.q && MG.o.won==null)", 40)
            if not await E("()=>!!MG.o"): break
            await E("()=>{ const q=MG.o.q, a=q.ans!=null?q.ans:q.opts.findIndex((x,i)=>MG.right(q,i)); MG.o.P.forEach(p=>MG.tap(p.i,(a+1)%q.opts.length)); }")
        ok(await until("()=>!!document.querySelector('.bdEnd')", 80), "마지막 미니게임 → 🎁 보너스 별 → 🏆")
        r = await E("()=>[Board.o.P.map(p=>p.star), document.querySelector('.bdEnd').innerText]")
        ok(r[0] == [3, 3, 2], f"🧠 정답왕 루아 · ⚔️ 결투왕 주호 · 🪙 부자 손님 = 별 +1씩 {r[0]}")
        txt = r[1]
        ok("주호 우승" in txt, f"별 같으면 🪙 많은 사람이 우승 (주호 ⭐3 🪙9 > 루아 ⭐3 🪙4) {txt[:60]!r}")
        ok("손님" in txt and "연습" in txt and "💎 +10" in txt and "💎 +7" in txt, f"💎 10·7 · 직접 쓴 이름 = 연습 {txt[:200]!r}")
        await pg.screenshot(path=OUT + "board424_end.png")
        await pg.wait_for_timeout(600)
        g = await E("()=>FB.get('/hy/gift/k2')")
        v = list((g or {}).values())
        ok(len(v) == 1 and v[0].get("g") == 10 and v[0].get("n") == "주호", f"주호(다른 아이) = 🎁 배달 💎10 {v}")
        await E("()=>Board.pay(Board.o.P.slice())")
        r = await E("()=>Board.pay(Board.o.P.slice())")
        ok(r[0] == 0 and r[1] == 0 and r[2] is None, f"하루 2판까지만 💎 {r}")
        # 한 판 더 · ⚔️ 초등 판 · 나가기
        await E("()=>document.querySelector('[data-bd=again]').click()"); await pg.wait_for_timeout(400)
        ok(await E("()=>Board.o && !Board.o.fin && Board.o.rnd===1 && Board.o.P.every(p=>p.pos===0 && p.coin===10 && p.star===0)"), "🔁 한 판 더 = 같은 사람 · 처음부터")
        await E("()=>Board.begin(Object.assign({}, Board.o.cfg, {sk:'e'}))"); await pg.wait_for_timeout(800)
        ok(await E("()=>Board.o.SK.bg.indexOf('board/e/')>=0 && Board.o.N===30 && !!document.getElementById('bdStage')"), "⚔️ 초등 던전 판 (30칸)")
        await E("()=>{ Board.o.fin=true; document.querySelector('[data-bd=quit]').click(); }")
        ok(await E("()=>!document.getElementById('board') && !document.body.classList.contains('arOn')"), "나가기 → 원래 화면")
        ok(not real_errs(errs), "오류 없음 " + str(real_errs(errs)[:3]))
        await br.close()
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)

asyncio.run(main())
