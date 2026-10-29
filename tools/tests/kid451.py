"""(v451) 사용자(컴퓨터로 해 보고): ① 🪙 은화 코인이 깨져서 나온다 ② 캐릭터가 무협지처럼 날아다녀 ③ 게임 들어가기 전에 짧은 설명
  ① 🪙 이모지 → 금 코인 그림 (Board.fx) · 머리 위 +3 도 그림 코인 ② 콩콩 높이 0.3 · 한 칸 0.3초 ③ 미니게임 13개 모두 3줄 설명 → 누르면/4.2초 뒤 3·2·1"""
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
        # ① 코인
        r = await E("""()=>{ const s=Board.fx('+3 🪙 · 🪙10'); return [s.indexOf('🪙'), (s.match(/<img/g)||[]).length, /coins\\.webp/.test(s)]; }""")
        ok(r[0] == -1 and r[1] == 2 and r[2], f"① Board.fx: 🪙 → 코인 그림 {r}")
        r = await E("""()=>{ const src=document.documentElement.innerHTML; return [Board.HOW.map(h=>h[2]).join('').indexOf('🪙')>=0, typeof B3.label]; }""")
        ok(r[1] == "function", "① B3.label 있음")
        await E("()=>Board.begin({sk:'k', set:'elem', from:0, to:2, qt:['mean'], sec:0, rounds:3, star:12, P:[{n:'루아',id:'',ch:0},{n:'주호',id:'',ch:3}]})")
        await pg.wait_for_timeout(800)
        await E("()=>Board.ban('코인 비! 🪙 +5','good',3000)")
        r = await E("()=>{ const b=document.getElementById('bdBan'); return [b.innerHTML.indexOf('🪙'), !!b.querySelector('img.bdIc')]; }")
        ok(r[0] == -1 and r[1], f"① 알림 글자의 🪙 → 그림 {r}")
        r = await E("()=>{ Board.act('<b>🪙 부자</b>'); const a=document.getElementById('bdAct'); return [a.innerHTML.indexOf('🪙'), !!a.querySelector('img.bdIc.cn')]; }")
        ok(r[0] == -1 and r[1], f"① 단추 영역의 🪙 → 그림 {r}")
        r = await E("""()=>{ let e=0; try{ B3.label('+3 🪙', null, '#ffd23f', 58); B3.float(0,'+3 🪙','#ffd23f'); B3.float(0,'-3 🪙','#ff5d6c'); }catch(x){ e=String(x); } return e; }""")
        ok(r == 0, f"① 머리 위 +3 🪙 글자 그림 만들기 오류 없음 {r}")
        r = await E("""()=>{ const h=Board.podHtml('t',[{p:{i:0,n:'a',ch:0,col:'#f00'},sc:3,c:10,r:1}]); return Board.fx(h).indexOf('🪙'); }""")
        ok(r == -1, f"① 시상대 +🪙 → 그림 {r}")
        await E("()=>Board.close && Board.close()")
        # ③ 설명
        r = await E("()=>[MiniG.ACT.concat(MiniG.ENG).every(k=>MiniG.HOW[k] && MiniG.HOW[k].length===3), MiniG.howHtml('fruit','k').split('<li>').length-1, MiniG.howHtml('mole','e').indexOf('고블린')>=0, MiniG.howHtml('mole','k').indexOf('두더지')>=0]")
        ok(r == [True, 3, True, True], f"③ 13개 게임 모두 3줄 설명 · 초등 = 고블린/랜턴 {r}")
        r = await E("()=>[MiniG.cnt(8000), MiniG.cnt(3200), MiniG.cnt(3000), MiniG.cnt(1200), MiniG.cnt(10)]")
        ok(r == ["", "", "3", "2", "1"], f"③ 패드 카운트다운: 설명 동안 비움 → 마지막 3초만 {r}")
        OPEN = """([k,np,sec])=>{ const c={set:'elem',from:0,to:3,words:[],qt:['mean']}, x=Object.create(Battle); x._ws=null; x.cfg=()=>c;
            const P=[{n:'루아',ch:0},{n:'주호',ch:3}].slice(0,np).map((p,i)=>Object.assign(p,{i,col:Board.COL[i]}));
            window._r=null; MG.open({title:MiniG.L[k][0], sub:MiniG.L[k][1], P, ctx:x, kind:k, sec}, sc=>window._r=sc); }"""
        await E(OPEN, ["fruit", 2, 6])
        r = await E("()=>{ const I=document.querySelector('.mgIntro'); return [!!I, I && I.classList.contains('how'), document.querySelectorAll('.mgIntro .mgHow li').length, document.getElementById('mgCnt').textContent]; }")
        ok(r == [True, True, 3, ""], f"③ 시작 전 설명 3줄 · 숫자는 아직 비어 있음 {r}")
        await pg.wait_for_timeout(1000)
        ok(bool(await E("()=>!!document.querySelector('.mgIntro.how')")), "③ 설명은 잠깐 지나도 계속 보임")
        await E("()=>document.querySelector('.mgIntro').click()")
        r = await E("()=>[document.querySelector('.mgIntro').classList.contains('how'), document.getElementById('mgCnt').textContent]")
        ok(r == [False, "3"], f"③ 화면을 누르면 바로 3·2·1 {r}")
        ok(await until("()=>!document.querySelector('.mgIntro') && MG.o && MG.o.inst && MG.o.inst.length===2", 60), "③ → 게임 시작")
        await E("()=>MG.close()")
        # 자동 (4.2초)
        await E(OPEN, ["stack", 2, 6])
        ok(await until("()=>document.getElementById('mgCnt') && document.getElementById('mgCnt').textContent==='3'", 40, 200), "③ 안 눌러도 4.2초 뒤 3·2·1")
        await E("()=>MG.close()")
        # HY_NOHOW
        await E("()=>{ window.HY_NOHOW=true; }")
        await E(OPEN, ["jump", 2, 6])
        r = await E("()=>[document.querySelector('.mgIntro').classList.contains('how'), document.getElementById('mgCnt').textContent]")
        ok(r == [False, "3"], f"③ HY_NOHOW = 설명 건너뜀 {r}")
        await E("()=>MG.close()")
        # ② 콩콩
        r = await E("()=>[(Board.o||{}).left]")
        await br.close()
    r = real_errs(errs)
    print("errs", r)
    if bad or r: print("FAILED", bad); sys.exit(1)
    print("ALL OK")
asyncio.run(main())
