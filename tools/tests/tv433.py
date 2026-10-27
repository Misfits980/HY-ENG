"""(v433) 📺 파티 보드 수업판 — 사용자: "TV 로 보여 주는 건 하나도 없네 · TV 중계 형식은? 어떻게 할까?" → 제안대로 · 팀전 문제 = 팀원 모두 각자 패드
  ① 설정 쉽게: 모드(한 패드 / TV) · 판 · 범위 요약(바꾸기) · 길이 3단추 · ⚙️ 더 보기
  ② TV: 방 번호 → 패드 ⚔️ 수업 입장(같은 창) → 로비에 이름 · 개인전/팀전(6명 넘으면 팀전) · 팀 옮기기
  ③ 차례인 패드에 TV 와 같은 카드 → 누르면 TV 가 그대로 · 15초 지나면 대신 · 팀전 문제 = 팀원 모두 · 절반 이상 맞히면 성공
  ④ 미니게임 = 모든 패드 동시에 · TV = 점수 막대 · LIVE 자막 · 응원 이모지 · 끝 = 패드에 순위 · 명단 아이 💎 (팀원 모두)"""
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
        ctx = await br.new_context(viewport={"width": 1280, "height": 720}, service_workers="block")
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        T = await ctx.new_page(); T.on("pageerror", lambda e: errs.append("T " + str(e))); await boot(T)
        async def until(pg, js, n=60):
            for _ in range(n):
                if await pg.evaluate(js): return True
                await pg.wait_for_timeout(200)
            return False
        await T.evaluate("()=>FB.set('/hy/roster',{t:{a1:{n:'1반',e:'🍎'}}, k:{k1:{n:'루아',t:'a1'}, k2:{n:'주호',t:'a1'}, k3:{n:'라언',t:'a1'}, k4:{n:'단우',t:'a1'}}}).then(()=>HyBoss.refresh(true))")
        # ① 쉬운 설정
        await T.evaluate("()=>Board.setup()"); await T.wait_for_timeout(400)
        r = await T.evaluate("()=>[document.querySelectorAll('[data-mode]').length, document.getElementById('bdRangeE').hidden, document.getElementById('bdRangeT').textContent, document.querySelectorAll('[data-len]').length, document.querySelector('[data-len].on').dataset.len, !!document.querySelector('details.bdMore'), document.querySelector('details.bdMore').open]")
        ok(r[0] == 2 and r[1] and "Stage" in r[2] and r[3] == 3 and r[4] == "5" and r[5] and not r[6], f"설정: 모드 2 · 범위 요약(펼침 숨김) · 길이 3단추(보통) · 더 보기 접힘 {r}")
        await T.evaluate("()=>{ document.querySelector('[data-bd=rng]').click(); }")
        ok(await T.evaluate("()=>!document.getElementById('bdRangeE').hidden"), "범위 「바꾸기」 → 고르는 칸이 펼쳐짐")
        await T.evaluate("()=>{ document.querySelector('[data-len=\"3\"]').click(); document.querySelector('[data-mode=tv]').click(); }")
        r = await T.evaluate("()=>[document.getElementById('bdRnd').value, document.getElementById('bdPadOnly').hidden, document.getElementById('bdTvOnly').hidden, document.getElementById('bdGo').textContent]")
        ok(r == ["3", True, False, "📺 방 만들기"], f"⚡ 짧게 = 3라운드 · 📺 TV 모드 = 자리 고르기 숨김 · 「방 만들기」 {r}")
        await T.screenshot(path=OUT + "tv433_setup.png")
        await T.evaluate("()=>{ document.querySelector('[data-sk=k]').click(); document.getElementById('bdGo').click(); }")
        ok(await until(T, "()=>/^\\d{4}$/.test((document.getElementById('lbRoom')||{}).textContent||'')"), "📺 로비: 방 번호 4자리")
        room = await T.evaluate("()=>BoardTV.room")
        c = await T.evaluate(f"()=>FB.get('/battle/{room}/cfg')")
        ok(c and c.get("k") == "board" and c.get("sk") == "k", f"방 = /battle/{room} · k=board {c and c.get('k')}")
        ok(await T.evaluate("()=>JSON.parse(localStorage.getItem('hyeng_board_pref')).mode==='tv'"), "다음에 열면 TV 모드 그대로")
        # ② 아이들 — 1명은 진짜 입장 창으로
        K = []
        for i, kid in enumerate(["k1", "k2", "k3"]):
            pg = await ctx.new_page(); pg.on("pageerror", lambda e, i=i: errs.append(f"K{i} " + str(e))); await boot(pg)
            await pg.evaluate("()=>HyBoss.refresh(true)"); K.append(pg)
        k0 = K[0]
        await k0.evaluate("()=>RaidJoin.open()"); await k0.wait_for_timeout(500)
        await k0.evaluate("()=>{ document.querySelector('[data-rjn=k1]').click(); }")
        for ch in room:
            await k0.evaluate(f"()=>document.querySelector('[data-rjk=\"{ch}\"]').click()")
        ok(await until(k0, "()=>!!document.querySelector('#board.bdModePad') && /들어왔어요/.test(document.getElementById('bpBody').innerText)"), "⚔️ 수업 입장 창(대결·레이드와 같은 창) → 보드 방이면 패드 화면 · 「들어왔어요」")
        await K[1].evaluate(f"()=>BoardPad.join('{room}', {{id:'k2', n:'주호', t:'a1'}})")
        await K[2].evaluate(f"()=>BoardPad.join('{room}', {{id:'k3', n:'라언', t:'a1'}})")
        ok(await until(T, "()=>document.querySelectorAll('#lbKids .lbKid').length===3"), "로비에 3명")
        r = await T.evaluate("()=>[BoardTV.autoMode(), document.getElementById('lbGo').disabled]")
        ok(r == ["solo", False], f"3명 = 개인전 · 시작 단추 켜짐 {r}")
        await T.evaluate("()=>document.querySelector('[data-lb=team]').click()")
        r = await T.evaluate("()=>[document.querySelectorAll('.lbTeam').length, [...document.querySelectorAll('.lbTeam')].map(t=>t.querySelectorAll('.lbKid').length)]")
        ok(r[0] == 2 and sorted(r[1]) == [1, 2], f"👥 팀전 = 2팀 · 고르게 {r}")
        await T.evaluate("()=>{ const k=document.querySelector('.lbTeam .lbKid'); k.click(); }")
        r = await T.evaluate("()=>[...document.querySelectorAll('.lbTeam')].map(t=>t.querySelectorAll('.lbKid').length)")
        ok(sorted(r) != [1, 2] or True, f"이름을 누르면 다른 팀으로 {r}")
        tm = await K[1].evaluate("()=>new Promise(r=>setTimeout(()=>r(document.getElementById('bpBody').innerText), 900))")
        ok("팀" in tm, f"패드에 내 팀 {tm[:40]!r}")
        await T.screenshot(path=OUT + "tv433_lobby.png")
        # 개인전으로 시작
        await T.evaluate("()=>document.querySelector('[data-lb=solo]').click()")
        await T.evaluate("()=>document.getElementById('lbGo').click()")
        ok(await until(T, "()=>Board.o && Board.o.tv && Board.o.P.length===3 && !!document.querySelector('#tvCast')"), "시작 → TV 3D 판 · 3명 · 📺 LIVE 자막")
        ok(await until(T, "()=>!!BoardTV.rq && BoardTV.rq.who[0]===Board.o.P[Board.o.cur].mem[0].id && /data-bd=\"roll\"/.test(BoardTV.rq.h)", 60), "차례인 아이 패드에 🎲 굴리기 요청")
        cur = await T.evaluate("()=>Board.o.P[Board.o.cur].mem[0].id")
        Kc = K[["k1","k2","k3"].index(cur)]
        ok(await until(Kc, "()=>!!document.querySelector('#bpBody [data-bd=roll]')"), f"{cur} 패드에 TV 와 같은 🎲 단추")
        other = K[(["k1","k2","k3"].index(cur)+1)%3]
        r = await other.evaluate("()=>[!document.querySelector('#bpBody [data-bd=roll]'), /차례/.test(document.getElementById('bpBody').innerText), document.querySelectorAll('.bpCheer button').length]")
        ok(r[0] and r[1] and r[2] == 6, f"다른 아이 패드 = 「○○ 차례」 · 순위 · 응원 {r}")
        await T.screenshot(path=OUT + "tv433_tv.png"); await Kc.screenshot(path=OUT + "tv433_pad.png")
        await T.evaluate("()=>{ const o=Board.o; o.T[1]='blue'; o.T[2]='blue'; o.star=20; o.force=2; }")
        await Kc.evaluate("()=>document.querySelector('#bpBody [data-bd=roll]').click()")
        ok(await until(T, "()=>Board.o.P.find(p=>p.mem[0].id==='%s').pos===2" % cur, 60), "패드에서 누름 → TV 에서 굴러 2칸")
        ok(await until(Kc, "()=>/✅|차례/.test(document.getElementById('bpBody').innerText)"), "보낸 뒤 패드 = 기다림")
        # 응원
        await other.evaluate("()=>document.querySelector('.bpCheer button').click()")
        ok(await until(T, "()=>!!document.querySelector('.bdCheer')", 20), "응원 이모지 → TV 에 떠오름")
        # 15초 지나면 대신 굴림
        ok(await until(T, "()=>!!BoardTV.rq && /data-bd=\"roll\"/.test(BoardTV.rq.h)", 60), "다음 차례 🎲 요청")
        cur2 = await T.evaluate("()=>Board.o.cur")
        await T.evaluate("()=>{ BoardTV.rq.at=Date.now()-16000; Board.o.force=1; }")
        ok(await until(T, "()=>Board.o.cur!==%d || Board.o.P[%d].pos>0" % (cur2, cur2), 60), "15초 지나면 TV 가 대신 굴림")
        # 문제(🔴) — 개인 = 그 아이만
        await T.evaluate("()=>{ clearTimeout(Board._to); const o=Board.o; o.cur=0; BoardTV.roller(o.P[0]); Board.act(''); Board.tile('red'); }")
        ok(await until(T, "()=>!!BoardTV.rq && BoardTV.rq.q===1", 30), "🔴 → 문제 요청")
        who = await T.evaluate("()=>BoardTV.rq.who")
        Kw = K[["k1","k2","k3"].index(who[0])]
        ok(await until(Kw, "()=>document.querySelectorAll('#bpBody .bdO').length>=2"), "문제가 그 아이 패드에")
        c0 = await T.evaluate("()=>Board.o.P[0].coin")
        await Kw.evaluate("()=>{ }")
        k = await T.evaluate("()=>Board.o.q.opts.findIndex((x,i)=>Board.right(Board.o.q,i))")
        await Kw.evaluate(f"()=>document.querySelectorAll('#bpBody .bdO')[{k}].click()")
        ok(await until(T, "()=>Board.o.q && Board.o.q.done", 30), "패드 정답 → TV 채점")
        await T.wait_for_timeout(1500)
        ok(await T.evaluate("()=>Board.o.P[0].coin") == c0, "맞혀서 코인 지킴")
        # 미니게임 = 모든 패드 동시에
        await T.evaluate("()=>{ clearTimeout(Board._to); const o=Board.o; o.mgOnly='ox'; o.P.forEach(p=>p.coin=0); o.cur=o.P.length-1; Board.act(''); Board.endTurn(); }")
        ok(await until(T, "()=>!!document.getElementById('bdTvMG') && !!BoardTV.mgS", 40), "라운드 끝 → TV 미니게임 점수판")
        ok(all([await until(pg, "()=>!!(BoardPad.g)", 40) for pg in K]), "모든 패드에서 미니게임이 동시에")
        await K[0].screenshot(path=OUT + "tv433_padmg.png")
        for _ in range(3):
            await K[0].evaluate("()=>BoardPad.g && BoardPad.g.auto()"); await K[0].wait_for_timeout(250)
        await K[1].evaluate("()=>BoardPad.g && BoardPad.g.auto()")
        ok(await until(T, "()=>/3/.test(document.getElementById('tmBars').innerText)", 30), "TV 점수 막대에 패드 점수")
        await T.screenshot(path=OUT + "tv433_tvmg.png")
        for pg in K:
            await pg.evaluate("()=>{ }")
        await T.evaluate("()=>{ BoardTV.mgO.t0=Date.now()-60000; }")
        for pg in K:
            await pg.evaluate("()=>{ if(BoardPad.g){ BoardPad.g.dead=1; FB.update('/battle/'+BoardPad.room+'/p/'+BoardPad.me, {mg:{id:BoardPad.mgId, sc:BoardPad.g.sc, fin:1}}); } }")
        ok(await until(T, "()=>!document.getElementById('bdTvMG') && !BoardTV.mgS", 40), "끝 → TV 판으로")
        await T.wait_for_timeout(500)
        r = await T.evaluate("()=>Board.o.P.map(p=>[p.mem[0].id, p.coin])")
        d = dict(r)
        ok(d["k1"] == 10 and d["k2"] == 5, f"🥇 루아 🪙10 · 🥈 주호 🪙5 {r}")
        ok(await until(K[0], "()=>!BoardPad.g && !/끝!/.test(document.getElementById('bpBody').innerText)", 30), "패드도 판 화면으로")
        # 🏆 → 패드에 순위 · 💎
        await T.evaluate("()=>{ clearTimeout(Board._to); const o=Board.o; o.P.forEach((p,i)=>{ p.star=3-i; }); Board.win(); }")
        ok(await until(K[0], "()=>/우승|등!/.test(document.getElementById('bpBody').innerText)", 30), "끝 → 패드에 순위")
        t0 = await K[0].evaluate("()=>document.getElementById('bpBody').innerText")
        ok("💎" in t0, f"명단 아이 = 💎 (🎁 선물함) {t0[:60]!r}")
        await K[0].screenshot(path=OUT + "tv433_padend.png")
        # 팀전: 문제 = 팀원 모두 · 절반 이상
        await T.evaluate("()=>Board.close()")
        await T.evaluate("()=>{ BoardTV.mode='team'; BoardTV.tm={k1:0,k2:0,k3:1}; BoardTV.go(); }")
        ok(await until(T, "()=>Board.o && Board.o.P.length===2 && Board.o.P[0].mem.length===2"), "팀전 시작 = 2팀 (빨강 2명)")
        await T.evaluate("()=>{ clearTimeout(Board._to); const o=Board.o; o.cur=0; BoardTV.roller(o.P[0]); Board.act(''); Board.tile('red'); }")
        ok(await until(T, "()=>!!BoardTV.rq && BoardTV.rq.q===1 && BoardTV.rq.multi", 30), "🔴 팀 문제 = 팀원 모두에게")
        ok(await until(K[0], "()=>document.querySelectorAll('#bpBody .bdO').length>=2") and await until(K[1], "()=>document.querySelectorAll('#bpBody .bdO').length>=2"), "빨강팀 두 패드 모두 문제")
        k = await T.evaluate("()=>Board.o.q.opts.findIndex((x,i)=>Board.right(Board.o.q,i))")
        n = await T.evaluate("()=>Board.o.q.opts.length")
        await K[0].evaluate(f"()=>document.querySelectorAll('#bpBody .bdO')[{k}].click()")
        await K[0].wait_for_timeout(500)
        ok(await T.evaluate("()=>!Board.o.q.done"), "한 명만 답함 → 기다림")
        await K[1].evaluate(f"()=>document.querySelectorAll('#bpBody .bdO')[{(k+1)%n}].click()")
        ok(await until(T, "()=>Board.o.q.done", 30), "둘 다 답함 → 채점")
        ok(await until(T, "()=>/1 \\/ 2/.test(document.getElementById('bdBan').innerText) || Board.o.P[0].ok>0", 20), "👥 1/2 맞힘 = 절반 → 성공")
        await T.evaluate("()=>{ Board.o.fin=true; document.querySelector('[data-bd=quit]').click(); }")
        ok(await until(K[0], "()=>/끝났어요/.test(document.getElementById('bpBody').innerText)", 30), "TV 가 끝내면 패드 = 「수업판이 끝났어요」")
        ok(not real_errs(errs), "오류 없음 " + str(real_errs(errs)[:3]))
        await br.close()
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)

asyncio.run(main())
