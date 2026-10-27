"""(v424) 🎲 영어 보드게임 — 🪑 둘러앉기 (한 패드 2~4명) · 🏁 주사위 레이스 · 🧸 유아 판 / ⚔️ 초등 던전 판
  사용자: "보드게임처럼 영어를 해 보는 건? 애들 문제 푸는 거" · "유아용 보드 초등 보드 따로"
  ① 시작 화면 🎲 카드 → 설정(판 · 범위 · 문제 종류 · 시간 · 2~4명 명단에서)
  ② 차례: 문제 → 맞히면 🎲 → 이동 · 틀리면 다음 친구 · 시간 끝 = 틀림
  ③ 칸: 🪜 위로 · 🛝 아래로(🛡 방패 / 문제 맞히면 안 내려감) · ⭐ 찬스(➕2 · 🎲 한 번 더 · 🛡 · 👈 친구 뒤로 · 💎) · 🔥 도전(+3)
  ④ 🏆 → 💎 10·7·5 (이 기기 주인 = 바로 · 다른 아이 = 🎁 배달) · 직접 쓴 이름 = 연습 · 하루 2판"""
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
        await E("()=>FB.set('/hy/roster',{t:{a1:{n:'유치부',e:'🧸'}}, k:{k1:{n:'루아',t:'a1'}, k2:{n:'주호',t:'a1'}, k3:{n:'라언',t:'a1'}}}).then(()=>HyBoss.refresh(true))")
        ok(await E("()=>(Kid.me()||{}).id") == "k1", "이 기기 = 루아")
        # ① 시작 화면 카드
        ok(await E("()=>document.querySelector('#selRule [data-v=board]').offsetHeight===0"), "(v427) 시작 화면 🎲 카드는 숨김 (다시 만드는 중)")
        await E("()=>Board.setup()"); await pg.wait_for_timeout(500)
        r = await E("()=>[!!document.getElementById('bdSetup'), document.querySelectorAll('.bdSkB').length, document.querySelectorAll('.bdSeat').length, document.getElementById('bdFrom').options.length>0]")
        ok(r == [True, 2, 2, True], f"설정: 판 2개(유아·초등) · 기본 2명 · Stage 고르기 {r}")
        await E("()=>{ document.querySelector('[data-bd=add]').click(); }")
        sel = await E("()=>[...document.querySelectorAll('.bdSeat select')].map(s=>[...s.options].map(o=>o.value))")
        ok(len(sel) == 3 and "k1" in sel[0] and "__" in sel[0], f"➕ 한 명 더 · 명단에서 고르기 · ✏️ 직접 쓰기 {sel[0]}")
        await E("""()=>{ const S=[...document.querySelectorAll('.bdSeat select')]; S[0].value='k1'; S[0].dispatchEvent(new Event('change',{bubbles:true})); }""")
        await E("""()=>{ const S=[...document.querySelectorAll('.bdSeat select')]; S[1].value='k2'; S[1].dispatchEvent(new Event('change',{bubbles:true})); }""")
        sel = await E("()=>[...document.querySelectorAll('.bdSeat select')][2].innerHTML")
        ok("k1" not in sel and "k2" not in sel, "이미 고른 아이는 다른 자리 목록에서 빠짐")
        await E("()=>{ Board._seats[2]={n:'손님', id:'', ch:4}; Board.seats(); document.querySelector('[data-sk=k]').click(); }")
        await E("()=>document.querySelector('[data-bd=go]').click()"); await pg.wait_for_timeout(1500)
        r = await E("()=>[!!Board.o, Board.o.cfg.sk, Board.o.P.map(p=>p.n), document.querySelectorAll('.bdT').length, document.querySelectorAll('.bdT img').length, !!document.querySelector('.bdQ'), Board.o.cur]")
        ok(r[0] and r[1] == "k" and r[2] == ["루아", "주호", "손님"] and r[3] == 30 and r[4] == 14 and r[5] and r[6] == 0, f"🧸 유아 판 30칸 (특별 칸 그림 14) · 루아 차례 문제 {r}")
        await pg.screenshot(path=OUT + "board424_q.png")
        # ② 맞히면 🎲
        right = "()=>{ const q=Board.o.q; return q.opts.findIndex((x,i)=>Board.right(q,i)); }"
        await E("(k)=>document.querySelectorAll('#bdAct .bdO')[k].click()", await E(right)); await pg.wait_for_timeout(900)
        ok(await E("()=>!!document.querySelector('[data-bd=roll]')"), "맞히면 🎲 굴리기 단추")
        await E("()=>{ Board.o.force=4; document.querySelector('[data-bd=roll]').click(); }"); await pg.wait_for_timeout(3800)
        r = await E("()=>[Board.o.P[0].pos, Board.o.cur]")
        ok(r == [10, 1], f"🎲 4 → 4칸 = 🪜 사다리 → 10칸 · 다음 = 주호 {r}")
        # 틀리면 다음
        await pg.wait_for_timeout(900)
        k = await E(right)
        await E("(k)=>document.querySelectorAll('#bdAct .bdO')[(k+1)%document.querySelectorAll('#bdAct .bdO').length].click()", k); await pg.wait_for_timeout(3200)
        r = await E("()=>[Board.o.P[1].pos, Board.o.cur, Board.o.P[1].ng, Object.keys(Board.o.miss||{}).length]")
        ok(r[0] == 0 and r[1] == 2 and r[2] == 1 and r[3] == 1, f"틀리면 그 자리 · 다음 친구 · 헷갈린 단어에 {r}")
        # 시간 끝 = 틀림
        await pg.wait_for_timeout(900)
        await E("()=>{ Board.o.q.t0=Date.now()-16000; }")
        for _ in range(40):
            await pg.wait_for_timeout(200)
            if await E("()=>Board.o.cur===0"): break
        r = await E("()=>[Board.o.P[2].ng, Board.o.cur]")
        ok(r == [1, 0], f"⏱ 15초 지나면 틀림 → 다음 {r}")
        # ③ 칸들 — 직접 부름
        await pg.wait_for_timeout(600)
        r = await E("""async()=>{ const B=Board, o=B.o, w=ms=>new Promise(r=>setTimeout(r,ms)); clearTimeout(B._to); clearInterval(B._tm); o.q && (o.q.done=1); B.act('');
            const R={}; o.cur=0; const p=o.P[0];
            p.pos=14; p.sh=1; B.land(); await w(1500); R.shield=[p.pos, p.sh];
            clearTimeout(B._to); o.cur=0; p.pos=14; B.land(); await w(1100); R.slideAsk=o.why; const q=o.q; const bad=q.opts.findIndex((x,i)=>!B.right(q,i)); B.answer(bad); await w(3000); R.slid=p.pos;
            clearTimeout(B._to); o.cur=0; p.pos=22; B.land(); await w(1100); const q2=o.q; B.answer(q2.opts.findIndex((x,i)=>B.right(q2,i))); await w(1500); R.saved=p.pos;
            clearTimeout(B._to); o.cur=0; p.pos=8; B.land(); await w(1100); R.hardQ=[o.why, o.q.t]; const q3=o.q; B.answer(q3.opts.findIndex((x,i)=>B.right(q3,i))); await w(2000); R.hard=p.pos;
            return R; }""")
        ok(r["shield"] == [14, 0], f"🛝 미끄럼 + 🛡 방패 = 안 내려감 (방패 씀) {r['shield']}")
        ok(r["slideAsk"] == "slide" and r["slid"] == 7, f"🛝 방패 없으면 문제 → 틀리면 14 → 7 {r['slideAsk']} {r['slid']}")
        ok(r["saved"] == 22, f"🛝 문제 맞히면 안 내려감 {r['saved']}")
        ok(r["hardQ"][0] == "hard" and r["hardQ"][1] in ("spell", "gap", "k2e", "e2k", "pic", "sent", "def") and r["hard"] == 11, f"🔥 도전 칸: 어려운 문제(철자·빈칸) → 맞히면 8 → 11 {r['hardQ']} {r['hard']}")
        r = await E("""async()=>{ const B=Board, o=B.o, w=ms=>new Promise(r=>setTimeout(r,ms)); clearTimeout(B._to); const R={};
            const go=async(k)=>{ clearTimeout(B._to); o.cur=0; B.act(''); B.card(k); await w(200); };
            o.P[0].pos=6; await go('fwd'); await w(2200); R.fwd=o.P[0].pos;
            await go('shield'); await w(1500); R.sh=o.P[0].sh;
            await go('gem'); await w(1500); R.gem=o.P[0].gem;
            await go('again'); await w(1500); R.again=!!document.querySelector('[data-bd=roll]');
            o.P[1].pos=12; o.P[1].sh=0; o.P[2].pos=0; await go('back'); R.tg=[...document.querySelectorAll('[data-bd=tgt]')].map(b=>+b.dataset.i); B.backTo(1); await w(1500); R.back=o.P[1].pos;
            o.P[1].sh=1; await go('back'); B.backTo(1); await w(1500); R.blk=[o.P[1].pos, o.P[1].sh];
            return R; }""")
        ok(r["fwd"] == 8, f"⭐ ➕2칸 (6 → 8) {r['fwd']}")
        ok(r["sh"] >= 1 and r["gem"] == 1 and r["again"], f"⭐ 🛡 방패 · 💎 +1 · 🎲 한 번 더 {r}")
        ok(r["tg"] == [1] and r["back"] == 10, f"⭐ 👈 친구 고르기(출발 칸 친구는 빼고) → 2칸 뒤로 {r['tg']} {r['back']}")
        ok(r["blk"] == [10, 0], f"⭐ 👈 방패 있는 친구는 막힘 {r['blk']}")
        await pg.screenshot(path=OUT + "board424_card.png")
        # ④ 🏆
        r = await E("""async()=>{ const B=Board, o=B.o, w=ms=>new Promise(r=>setTimeout(r,ms)); clearTimeout(B._to); const g0=Wallet.gems(); o.cur=0; o.P[0].pos=26; o.P[1].pos=20; o.P[2].pos=25; o.P[0].gem=1; B.act('');
            o.force=5; B.rollBtn(); B.roll(); await w(2600); await Gift.flush && 0; return [o.fin, o.P[0].pos, Wallet.gems()-g0, document.querySelector('.bdEnd') && document.querySelector('.bdEnd').innerText]; }""")
        ok(r[0] and r[1] == 29 and r[2] == 11 and "우승" in r[3], f"🏆 넘쳐도 도착 → 루아(이 기기) 💎 10+1 바로 {r[:3]}")
        txt = r[3]
        ok("손님" in txt and "연습" in txt, f"직접 쓴 이름 = 연습 (💎 없음) {txt[:120]!r}")
        await pg.wait_for_timeout(600)
        g = await E("()=>FB.get('/hy/gift/k2')")
        v = list((g or {}).values())
        ok(len(v) == 1 and v[0].get("g") == 5 and v[0].get("n") == "주호", f"주호(3등 · 다른 아이) = 🎁 배달 💎5 {v}")
        await pg.screenshot(path=OUT + "board424_end.png")
        # 하루 2판
        await E("()=>{ const o=Board.o; Board.pay(o.P.slice()); }")
        r = await E("()=>Board.pay(Board.o.P.slice())")
        ok(r[0] == 0 and r[1] == 0 and r[2] is None, f"하루 2판까지만 💎 (3판째 = 0) {r}")
        # 한 판 더 · 🧭 ⚔️ 초등 판
        await E("()=>document.querySelector('[data-bd=again]').click()"); await pg.wait_for_timeout(600)
        ok(await E("()=>Board.o && !Board.o.fin && Board.o.P.every(p=>p.pos===0)"), "🔁 한 판 더 = 같은 사람 · 처음부터")
        await E("()=>Board.begin(Object.assign({}, Board.o.cfg, {sk:'e'}))"); await pg.wait_for_timeout(1200)
        ok(await E("()=>document.getElementById('bdBoard').style.backgroundImage.indexOf('board/e/')>=0 && document.querySelector('.bdT.up img').src.indexOf('board/e/')>=0"), "⚔️ 초등 던전 판 · 던전 그림 칸")
        await pg.screenshot(path=OUT + "board424_e.png")
        await E("()=>{ Board.o.fin=true; document.querySelector('[data-bd=quit]').click(); }")
        ok(await E("()=>!document.getElementById('board') && !document.body.classList.contains('arOn')"), "나가기 → 원래 화면")
        ok(not real_errs(errs), "오류 없음 " + str(real_errs(errs)[:3]))
        await br.close()
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)

asyncio.run(main())
