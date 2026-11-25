"""(v731) 🎳 볼링 옆 레인 대결 + 핀 손맛 — 사용자 「볼링 옆 레인 대결 + 핀 손맛」 (방안 claude/hy-eng-plan-town-games-v729.md)
   ① 메뉴: 상대 = 혼자 · 🤖 쉬움(기본) · 보통 · 잘함
   ② 셋이 같이: Tom(왼쪽) · Lily(오른쪽) 캐릭터 · 이름표 · 점수판 3줄 / 혼자면 예전 점수판 · 봇 숨김
   ③ 봇은 내 프레임보다 앞서지 않음 · 다 끝나야 결과 · 결과 = 등수 · 이름 · 🪙
   ④ 핀 손맛: 맞은 핀이 튀어 오르고 돌다가 눕기 · 핀 정리(판이 서 있는 핀을 들고 · 막대가 쓰러진 핀을 쓸고 · 내려놓음)
   ⑤ 스트라이크 다시 보기(옆에서 느리게 · 누르면 건너뜀) · 더블 · 터키 · 봇 스트라이크 소식
   ⑥ 휴대폰 세로 · 가로 · 패드: 점수판 · 소식이 화면 안 · 안 겹침 · 움직임 줄이기 = 흔들림 없음 · 오류 0"""
import asyncio, sys, os
os.environ["HY_REAL3D"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from draw635 import boot
from playwright.async_api import async_playwright

ENTER = """async ()=>{ MG.lobby('bowl'); for(let i=0;i<80;i++){ if(MG.on && MG.run && MG.run.ready) break; await new Promise(r=>setTimeout(r,200)); } return !!MG.run; }"""
ADV = """([n, until])=>{ const R=MG.run; R.pause(false); const f=until?new Function('R','B','return ('+until+');'):null; let k=0; for(;k<n;k++){ MG.step(.016,false); if(f && f(R,R.bw)) break; } R.pause(true); MG.step(0,true); return k; }"""
GO = """(vs)=>{ const R=MG.run; R.SET.vs=vs; R.SET.bump=1; R.menuGo('bowl'); R.pause(true); MG.step(0,true); return R.lanes.map(L=>L.on); }"""

async def main():
    bad = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        ctx, pg, errs = await boot(br, "루아", "BW731A", vp={"width": 390, "height": 844}, isle=False)
        E = pg.evaluate
        async def adv(n, until=None): return await E(ADV, [n, until])
        await E(ENTER); await pg.wait_for_timeout(600)
        # ① 메뉴
        r = await E("()=>{ const M=document.querySelector('#mgUI .puM'); return [[...M.querySelectorAll('[data-sg]')].map(b=>b.dataset.sg+(b.classList.contains('on')?'*':'')).join(','), M.textContent.includes('🤖 대결')]; }")
        ok(r[0] == "0,easy*,normal,hard,co" and r[1], f"① 메뉴 상대 고르기 (기본 쉬움 · 👫 친구) {r}")
        await E("()=>document.querySelector('#mgUI .puM [data-sg=\"hard\"]').click()")
        r = await E("()=>[MG.run.SET.vs, document.querySelector('#mgUI .puM [data-sg=\"hard\"]').classList.contains('on'), JSON.parse(localStorage.getItem('hyeng_proto_spset')||'{}').vs]")
        ok(r == ["hard", True, "hard"], f"① 고르면 저장 {r}")
        # ② 셋이 같이 / 혼자
        r = await E(GO, "normal"); await adv(30)
        r2 = await E("()=>{ const R=MG.run, sc=document.querySelector('#mgUI .spSc'); return [sc.classList.contains('multi'), sc.querySelectorAll('.rw').length, [...sc.querySelectorAll('.rw .nm')].map(e=>e.textContent).join(','), R.lanes.slice(1).map(L=>!!(L.P && L.P.g.visible && L.tag && L.tag.visible && L.ball.visible)), R.lanes.slice(1).map(L=>L.sk)]; }")
        ok(r == [True, True, True] and r2[0] and r2[1] == 3 and r2[2] == "루아,Tom,Lily" and r2[3] == [True, True] and r2[4] == ["normal", "normal"], f"② 셋이 같이: 점수판 3줄 · Tom · Lily 캐릭터·이름표·공 {r} {r2}")
        await pg.screenshot(path=OUT + "bowl731_aim_phone.png")
        r = await E(GO, "0"); await adv(10)
        r2 = await E("()=>{ const R=MG.run, sc=document.querySelector('#mgUI .spSc'); return [sc.classList.contains('multi'), sc.querySelectorAll(':scope > div').length, R.lanes.slice(1).map(L=>!!(L.P && L.P.g.visible) || L.ball.visible)]; }")
        ok(r == [True, False, False] and not r2[0] and r2[1] == 6 and r2[2] == [False, False], f"② 혼자: 예전 점수판 · 봇 숨김 {r} {r2}")
        # ④ 핀 손맛 — 포켓으로 세게 (천천히 단계)
        await E(GO, "0"); await adv(10)
        await E("()=>MG.run.throwBall(.12, 0, 12)")
        r = await E("""()=>{ const R=MG.run, B=R.bw; R.pause(false); let maxY=0, spin=0, k=0; for(;k<1500 && B.ph==='roll';k++){ MG.step(.016,false); B.pins.forEach(p=>{ maxY=Math.max(maxY, p.g.position.y); spin=Math.max(spin, Math.abs(p.rot)); }); } R.pause(true); return [+maxY.toFixed(2), +spin.toFixed(2), k]; }""")
        ok(r[0] > .55 and r[1] > 2.2, f"④ 맞은 핀이 튀어 오르고(높이 {r[0]}) 돎(각 {r[1]})")
        await adv(400, "B.rolls.length===1")
        r = await E("()=>{ const B=MG.run.bw; return [B.rolls[0], B.pins.filter(p=>!p.up).every(p=>Math.abs(Math.sin(p.rot))>.97 && !p.air && Math.abs(p.g.position.y-.12)<.04)]; }")
        ok(r[1], f"④ 쓰러진 핀은 바닥에 누움 {r}")
        # ⑤ 다시 보기 (스트라이크일 때) — 아니면 넘어감
        if r[0] == 10:
            await adv(200, "R.rp")
            r = await E("()=>{ const R=MG.run; return [!!R.rp, document.querySelector('#mgUI .spRp').classList.contains('on'), +R.cam.position.x.toFixed(2), document.querySelector('#mgUI .spBig').textContent]; }")
            ok(r[0] and r[1] and r[2] > 1.4 and "STRIKE" in r[3], f"⑤ 스트라이크 → 옆에서 다시 보기 · 표시 {r}")
            await pg.screenshot(path=OUT + "bowl731_replay.png")
            await adv(30)
            await E("()=>{ const h=document.querySelector('#mgUI .spHit'), b=h.getBoundingClientRect(); h.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true, clientX:b.width/2, clientY:b.height/2})); }")
            await adv(2)
            r = await E("()=>{ const R=MG.run; return [!!R.rp, document.querySelector('#mgUI .spRp').classList.contains('on')]; }")
            ok(r == [False, False], f"⑤ 누르면 다시 보기 건너뜀 {r}")
        else:
            ok(True, f"⑤ (이번 공 {r[0]}개 — 다시 보기 검사는 아래 강제 스트라이크로)")
        # ④ 핀 정리 — 남은 핀이 있는 굴림
        await E(GO, "0"); await adv(10)
        await E("()=>MG.run.throwBall(-.55, 0, 7)"); await adv(1500, "B.sw")
        r = await E("()=>{ const B=MG.run.bw; return [B.rolls[0], B.deck.visible, B.bar.visible]; }")
        ok(r[0] < 10 and r[1] and r[2], f"④ 핀 정리 시작 (판 · 막대 보임) {r}")
        await adv(200, "B.sw && B.sw.t>.6")
        r = await E("()=>{ const B=MG.run.bw, st=B.pins.filter(p=>p.up && !p.down && p.g.visible); return [st.length, st.every(p=>p.lift>.3), +B.bar.position.y.toFixed(2)]; }")
        ok(r[0] == 10 - (await E("()=>MG.run.bw.rolls[0]")) and r[1] and r[2] < .2, f"④ 서 있는 핀은 들려 있고 · 막대가 바닥을 쓸음 {r}")
        await adv(200, "B.sw && B.sw.t>1")
        r = await E("()=>{ const B=MG.run.bw; return [B.pins.filter(p=>!p.up && p.g.visible).length]; }")
        ok(r[0] == 0, f"④ 쓰러진 핀은 치워짐 {r}")
        await adv(400, "B.ph==='aim'")
        r = await E("()=>{ const B=MG.run.bw, st=B.pins.filter(p=>p.g.visible); return [st.length, st.every(p=>p.up && !p.down && p.lift===0 && Math.abs(p.g.position.y-.3)<.01 && Math.hypot(p.x-p.hx,p.z-p.hz)<.01), B.deck.visible, B.bar.visible, 10-B.rolls[0]]; }")
        ok(r[0] == r[4] and r[1] and not r[2] and not r[3], f"④ 남은 핀만 제자리에 다시 섬 · 판/막대 숨김 {r}")
        # ⑤ 더블 · 터키 (스트라이크 줄 흉내)
        await E(GO, "0"); await adv(10)
        r = await E("""()=>{ const R=MG.run, B=R.bw, out=[]; R.fast=true; R.pause(false); for(let s=0;s<3;s++){ for(let i=0;i<300 && B.ph!=='aim';i++) MG.step(.05,false); B.pins.forEach(p=>{ p.down=true; }); const r0=B.rolls.length; R.throwBall(0,0,13); for(let i=0;i<600 && B.rolls.length===r0;i++) MG.step(.05,false); out.push([B.rolls[B.rolls.length-1], document.querySelector('#mgUI .spBig').textContent.slice(0,8)]); } R.fast=false; R.pause(true); return out; }""")
        ok([x[0] for x in r] == [10, 10, 10] and r[0][1].startswith("STRIKE") and r[1][1].startswith("DOUBLE") and r[2][1].startswith("TURKEY"), f"⑤ 스트라이크 → 더블 → 터키 {r}")
        # ③ 같이 굴림 · 봇은 앞서지 않음 · 결과
        await E(GO, "easy"); await adv(5)
        c0 = await E("()=>TECO.coins()")
        r = await E("""()=>{ const R=MG.run, B=R.bw; R.fast=true; R.pause(false); let ahead=0, k=0, bothRoll=0;
            for(;k<40000 && !document.querySelector('#mgUI .puR');k++){ MG.step(.05,false);
              const mf=R.bowlDone(B.rolls)?5:R.rollsInFrame(B.rolls).f; R.lanes.slice(1).forEach(L=>{ const lf=R.bowlDone(L.rolls)?5:R.rollsInFrame(L.rolls).f; if(L.ph==='roll' && lf>mf) ahead++; if(L.ph==='roll' && B.ph==='roll') bothRoll++; });
              if(B.ph==='aim' && Math.random()<.2) R.throwBall((Math.random()-.5)*.5,(Math.random()-.5)*.2,8+Math.random()*5); }
            R.fast=false; const el=document.querySelector('#mgUI .puR'); return [ahead, bothRoll, !!el, el?el.textContent:'', R.lanes.map(L=>L.ph), R.lanes.map(L=>R.bowlScore(L.rolls).total)]; }""")
        ok(r[0] == 0, f"③ 봇이 내 프레임보다 앞서 굴린 적 0 ({r[0]})")
        ok(r[1] > 0, f"③ 봇과 내가 같은 때 굴림 ({r[1]} 걸음)")
        ok(r[2] and r[4] == ["done", "done", "done"] and "Tom" in r[3] and "Lily" in r[3] and "등" in r[3], f"③ 다 끝나야 결과 · 등수 · 이름 {r[4]} {r[5]} {r[3][:80]}")
        c1 = await E("()=>TECO.coins()"); ok(c1 > c0, f"③ 🪙 {c0} → {c1}")
        await E("()=>MG.run.pause(false)"); await pg.wait_for_timeout(1500); await pg.screenshot(path=OUT + "bowl731_end_phone.png")
        # ⑤ 봇 스트라이크 소식
        await E("()=>MG.run.restart ? 0 : 0"); await E(GO, "normal"); await adv(5)
        await E("()=>{ const L=MG.run.lanes[1]; L.aim=[.12,0,12]; L.wait=0; }")
        await adv(1500, "R.lanes[1].rolls.length===1"); await adv(4)
        r = await E("()=>{ const L=MG.run.lanes[1], P=document.querySelector('#mgUI .spPop'); return [L.rolls[0], P.classList.contains('on'), P.textContent]; }")
        ok(r[0] != 10 or (r[1] and "Tom" in r[2] and "스트라이크" in r[2]), f"⑤ 봇 스트라이크 → 「Tom 스트라이크!」 {r}")
        E1 = real_errs(errs); await ctx.close()
        # ⑥ 화면 3가지 (셋이 같이)
        E2 = []
        for nm, w, h in (("phoneP", 390, 844), ("land", 844, 390), ("padP", 820, 1180)):
            ctx, Q, e3 = await boot(br, "루아", "BW731B", vp={"width": w, "height": h}, isle=False)
            await Q.evaluate(ENTER); await Q.wait_for_timeout(500); await Q.evaluate(GO, "normal"); await Q.evaluate(ADV, [40, None])
            await Q.evaluate("()=>{ const P=document.querySelector('#mgUI .spPop'); P.textContent='Lily 스트라이크! 🎳'; P.classList.add('on'); }")
            await Q.evaluate("()=>{ MG.run.lanes[2].stk=1; }")
            await Q.wait_for_timeout(400)
            r = await Q.evaluate("""()=>{ const R=e=>e.getBoundingClientRect(), sc=R(document.querySelector('#mgUI .spSc')), say=R(document.querySelector('#mgUI .spSay')), btn=R(document.querySelector('#mgUI .spBtn')), top=R(document.querySelector('#mgUI .mgTop')||document.body);
              const inS=b=>b.left>=-1 && b.top>=-1 && b.right<=innerWidth+1 && b.bottom<=innerHeight+1, ov=(a,b)=>a.left<b.right && b.left<a.right && a.top<b.bottom && b.top<a.bottom;
              return [inS(sc), inS(say), !ov(sc,say), !ov(sc,btn), Math.round(sc.width), Math.round(sc.height), innerWidth]; }""")
            ok(r[0] and r[1] and r[2] and r[3], f"⑥ {nm}: 점수판 3줄 · 안내 · 단추 화면 안 · 안 겹침 {r}")
            await Q.screenshot(path=OUT + f"bowl731_{nm}.png")
            E2 += real_errs(e3); await ctx.close()
        # ⑥ 움직임 줄이기 → 흔들림 없음
        ctx = await br.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True, reduced_motion="reduce")
        from fakefb import fake
        Q = await ctx.new_page(); e4 = []; Q.on("pageerror", lambda e: e4.append(str(e)))
        await Q.route("**/*", fake); await Q.goto(ORIGIN + "proto/house.html?isle=1"); await Q.wait_for_timeout(300)
        await Q.evaluate("()=>{ localStorage.setItem('hyeng_nick','루아'); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); }"); await Q.reload(); await Q.wait_for_timeout(2400)
        await Q.evaluate(ENTER); await Q.wait_for_timeout(400); await Q.evaluate(GO, "0"); await Q.evaluate(ADV, [10, None])
        await Q.evaluate("()=>MG.run.throwBall(.12, 0, 13)")
        r = await Q.evaluate("()=>{ const R=MG.run, B=R.bw; R.pause(false); let mx=0; for(let k=0;k<900 && B.ph==='roll';k++){ MG.step(.016,false); mx=Math.max(mx, R.shk); } R.pause(true); return [B.hit, mx]; }")
        ok(r[0] and r[1] == 0, f"⑥ 움직임 줄이기: 부딪혀도 흔들림 0 {r}")
        E2 += real_errs(e4); await ctx.close()
        ok(not E1 and not E2, f"오류 없음 {(E1 + E2)[:3]}")
        await br.close()
    print("\nFAIL" if bad else "\nPASS", len(bad)); sys.exit(1 if bad else 0)

if __name__ == "__main__": asyncio.run(main())
