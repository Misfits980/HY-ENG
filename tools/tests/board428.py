"""(v428) 🎲 보드게임 3D 화면 — 사용자: "다시 만들어야겠다 · 너무 센세이션하지 않아" → 🎬 3D 보드
  · 판(그림 바닥 + 두께) · 길 위의 원판 30칸 · 말 = 8방향 걷기 그림 · 카메라가 차례인 친구를 따라감 · 🎲 3D 주사위가 굴러서 그 숫자가 위로
  · 칸마다 콩 점프 · 🪜 날아감 · 🗺 전체 보기 · 닫으면 3D 를 다 지움 (뒤 달리기 화면 다시 그림)"""
import asyncio, sys, os, json, math
os.environ["HY_REAL3D"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        pg = await br.new_page(viewport={"width": 430, "height": 932}); pg.on("pageerror", lambda e: errs.append(str(e)))
        await boot(pg); E = pg.evaluate
        async def until(js, n=120):
            for _ in range(n):
                if await E(js): return True
                await pg.wait_for_timeout(250)
            return False
        await E("()=>Board.begin({sk:'k', set:'elem', from:0, to:2, qt:['mean'], sec:0, P:[{n:'루아',id:'',ch:0},{n:'주호',id:'',ch:3}]})")
        r = await E("()=>[!!B3.R, !!document.querySelector('#bdStage canvas'), B3.TP.length, B3.pc.length, B3.mode]")
        ok(r[0] and r[1] and r[2] == 30 and r[3] == 2 and r[4] == "intro", f"3D 판 · 칸 30 · 말 2 · 처음엔 판 전체를 보여 줌 {r}")
        # 칸 = 그림 길 위 (판 좌표 = 그림 좌표)
        r = await E("()=>B3.TP.every((v,i)=>{ const P=Board.SK.k.P[i]; return Math.abs(v.x-(P[0]-0.5)*B3.BW)<1e-6 && Math.abs(v.z-(P[1]-0.5)*B3.BH)<1e-6; })")
        ok(r, "칸 자리 = 그림의 길 좌표 그대로 (기기마다 똑같음)")
        ok(await until("()=>B3.mode==='follow' && !!Board.o.q"), "인트로 → 차례인 친구를 따라감 · 문제")
        await pg.screenshot(path=OUT + "board428_q.png")
        # 정답 → 🎲 3
        await E("()=>{ const q=Board.o.q; const k=q.opts.findIndex((x,i)=>Board.right(q,i)); document.querySelectorAll('#bdAct .bdO')[k].click(); }")
        ok(await until("()=>!!document.querySelector('[data-bd=roll]')"), "맞히면 🎲 굴리기")
        await E("()=>{ window._rows=new Set(); window._ri=setInterval(()=>{ try{ window._rows.add(B3.pc[0].row); }catch(e){} }, 30); Board.o.force=3; document.querySelector('[data-bd=roll]').click(); }")
        ok(await until("()=>B3.mode==='dice' && B3.die.visible"), "3D 주사위가 굴러감")
        await pg.screenshot(path=OUT + "board428_dice.png")
        ok(await until("()=>B3.die.userData.done===1"), "주사위가 멈춤")
        top = await E("""()=>{ const d=B3.die, ax=[[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]].map(a=>new THREE.Vector3(...a).applyQuaternion(d.quaternion).y); return B3.DF[ax.indexOf(Math.max(...ax))]; }""")
        ok(top == 3, f"주사위 윗면 = 3 {top}")
        ok(await until("()=>Board.o.cur===1"), "3칸 가고 다음 친구")
        r = await E("()=>{ const g=B3.pc[0].g.position, T=B3.TP[3]; return [Board.o.P[0].pos, +Math.hypot(g.x-T.x, g.z-T.z).toFixed(2), [...window._rows]]; }")
        ok(r[0] == 3 and r[1] < 0.8 and len(r[2]) >= 2, f"말이 3번 칸 위 · 가는 쪽으로 몸을 돌림(방향 그림 여러 개) {r}")
        # 🪜 날기 — 루아 차례로 바꿔 4칸 → 사다리
        await E("()=>{ clearInterval(window._ri); }")
        ok(await until("()=>Board.o.cur===1 && Board.o.q && !Board.o.q.done && document.querySelectorAll('#bdAct .bdO').length>0"), "주호 문제")
        await E("()=>{ const q=Board.o.q; const k=q.opts.findIndex((x,i)=>Board.right(q,i)); document.querySelectorAll('#bdAct .bdO')[k].click(); }")
        ok(await until("()=>!!document.querySelector('[data-bd=roll]')"), "주호 🎲")
        await E("()=>{ Board.o.force=4; document.querySelector('[data-bd=roll]').click(); }")
        ok(await until("()=>B3.pc[1].anim && B3.pc[1].anim.k==='fly'"), "🪜 사다리 칸 → 날아감")
        await pg.screenshot(path=OUT + "board428_fly.png")
        ok(await until("()=>Board.o.cur===0"), "다음 차례")
        r = await E("()=>{ const g=B3.pc[1].g.position, T=B3.TP[10]; return [Board.o.P[1].pos, +Math.hypot(g.x-T.x, g.z-T.z).toFixed(2)]; }")
        ok(r[0] == 10 and r[1] < 0.8, f"🪜 4 → 10 칸 위 {r}")
        # 🗺 전체 보기
        await E("()=>document.querySelector('[data-bd=ov]').click()")
        ok(await E("()=>B3.mode==='over'"), "🗺 전체 보기")
        # 문제 카드가 떠 있으면 카메라를 위로
        ok(await until("()=>document.querySelectorAll('#bdAct .bdO').length>0 && B3.padB>0.1"), f"문제 카드 높이만큼 판을 위로 {await E('()=>B3.padB')}")
        # 🏆
        await E("()=>{ const o=Board.o; clearTimeout(Board._to); o.P[0].pos=29; Board.win(o.P[0]); }")
        ok(await until("()=>B3.mode==='win' && B3.fx.length>0", 40), "🏆 색종이 · 카메라가 우승자 둘레를 돎")
        await pg.wait_for_timeout(800); await pg.screenshot(path=OUT + "board428_win.png")
        # 닫기
        await E("()=>{ Board.o.fin=true; document.querySelector('[data-bd=quit]').click(); }")
        ok(await E("()=>!B3.R && !document.querySelector('#bdStage') && !Board.o"), "닫으면 3D 를 다 지움")
        ok(not real_errs(errs), "오류 없음 " + str(real_errs(errs)[:3]))
        await br.close()
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)

asyncio.run(main())
