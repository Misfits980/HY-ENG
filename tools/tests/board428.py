"""(v428→v429) 🎲 파티 보드 3D 화면 — 🎬 3D 보드 (사용자 고름) + 🎉 파티 규칙 (사용자 "그래")
  · 판(그림 바닥 + 두께) · 길 위의 원판 30칸 — 색 = 칸 종류(🔵+3 🔴−3 VS ? SHOP GO) · ⭐ 금별이 칸 위에서 돎
  · 말 = 8방향 걷기 그림 · 카메라가 차례인 친구를 따라감 · 🎲 3D 주사위 · 칸마다 콩 점프 · 🪙 숫자가 머리 위로
  · ⭐ 사면 별이 다른 칸으로 날아감 · 🔒 함정 표 · 🗺 전체 보기 · 닫으면 3D 를 다 지움"""
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
        await E("()=>Board.begin({sk:'k', set:'elem', from:0, to:2, qt:['mean'], sec:0, rounds:3, star:12, P:[{n:'루아',id:'',ch:0},{n:'주호',id:'',ch:3}]})")
        r = await E("()=>[!!B3.R, !!document.querySelector('#bdStage canvas'), B3.TP.length, B3.pc.length, B3.mode, B3.tg.length]")
        ok(r[0] and r[1] and r[2] == 30 and r[3] == 2 and r[4] == "intro" and r[5] == 30, f"3D 판 · 칸 30 · 말 2 · 처음엔 판 전체 {r}")
        r = await E("()=>B3.TP.every((v,i)=>{ const P=Board.SK.k.P[i]; return Math.abs(v.x-(P[0]-0.5)*B3.BW)<1e-6 && Math.abs(v.z-(P[1]-0.5)*B3.BH)<1e-6; })")
        ok(r, "칸 자리 = 그림의 길 좌표 그대로")
        r = await E("()=>Board.o.T.every((k,i)=>{ const side=B3.tg[i].children[0].material.color, want=new THREE.Color(B3.TOP[k][1]).multiplyScalar(0.72); return Math.abs(side.r-want.r)+Math.abs(side.g-want.g)+Math.abs(side.b-want.b)<0.01; })")
        ok(r, "칸 색 = 칸 종류 (파랑 · 빨강 · 주황 · 보라 · 초록 · 흰 출발)")
        await until("()=>{ const s=B3.starM.position, T=B3.TP[12]; return Math.hypot(s.x-T.x, s.z-T.z)<0.1 && s.y>1.2; }", 40)
        r = await E("()=>{ const s=B3.starM.position, T=B3.TP[12]; return [+Math.hypot(s.x-T.x, s.z-T.z).toFixed(2), s.y>1.2]; }")
        ok(r[0] < 0.1 and r[1], f"⭐ 금별 = 12번 칸 위에 떠 있음 {r}")
        ok(await until("()=>B3.mode==='follow' && !!document.querySelector('[data-bd=roll]')"), "인트로 → 차례인 친구를 따라감 · 🎲 굴리기")
        await pg.screenshot(path=OUT + "board428_menu.png")
        # 🎲 3 → 콩콩 3칸
        await E("()=>{ const o=Board.o; [1,2,3].forEach(i=>o.T[i]='blue'); B3.tiles(); window._rows=new Set(); window._ri=setInterval(()=>{ try{ window._rows.add(B3.pc[0].row); }catch(e){} }, 30); o.force=3; document.querySelector('[data-bd=roll]').click(); }")
        ok(await until("()=>B3.mode==='dice' && B3.die.visible"), "3D 주사위가 굴러감")
        await pg.screenshot(path=OUT + "board428_dice.png")
        ok(await until("()=>B3.die.userData.done===1"), "주사위가 멈춤")
        top = await E("""()=>{ const d=B3.die, ax=[[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]].map(a=>new THREE.Vector3(...a).applyQuaternion(d.quaternion).y); return B3.DF[ax.indexOf(Math.max(...ax))]; }""")
        ok(top == 3, f"주사위 윗면 = 3 {top}")
        ok(await until("()=>B3.fl.length>0", 60), "🔵 +3 🪙 글자가 머리 위로 떠오름")
        ok(await until("()=>Board.o.cur===1"), "다음 친구")
        r = await E("()=>{ const g=B3.pc[0].g.position, T=B3.TP[3]; return [Board.o.P[0].pos, Board.o.P[0].coin, +Math.hypot(g.x-T.x, g.z-T.z).toFixed(2), [...window._rows]]; }")
        ok(r[0] == 3 and r[1] == 13 and r[2] < 0.8 and len(r[3]) >= 2, f"말이 3번 칸 위 · 🪙13 · 가는 쪽으로 몸을 돌림 {r}")
        await E("()=>clearInterval(window._ri)")
        # ⭐ 주호: 🪙15 로 12번 별 지나감 → 사기 → 별이 날아감
        ok(await until("()=>Board.o.cur===1 && !!document.querySelector('[data-bd=roll]')"), "주호 🎲")
        await E("()=>{ const o=Board.o; o.P[1].pos=10; o.P[1].coin=15; for(let i=11;i<=14;i++) o.T[i]='blue'; B3.tiles(); Board.place(true); o.force=3; document.querySelector('[data-bd=roll]').click(); }")
        ok(await until("()=>!!document.querySelector('.bdStarC')"), "⭐ 별 칸에서 멈춤 → 별을 살까요?")
        await E("()=>document.querySelector('[data-bd=star]').click()")
        ok(await until("()=>!!document.querySelector('#bdAct .bdO')"), "⭐ 문제")
        await E("()=>{ const q=Board.o.q; document.querySelectorAll('#bdAct .bdO')[q.opts.findIndex((x,i)=>Board.right(q,i))].click(); }")
        ok(await until("()=>B3.mode==='star' && !!B3.starFly", 60), "⭐ 별이 다른 칸으로 날아감 (카메라가 별을 따라감)")
        await pg.wait_for_timeout(500); await pg.screenshot(path=OUT + "board428_star.png")
        ok(await until("()=>!B3.starFly && Board.o.cur===0", 120), "별 도착 → 남은 칸 마저 · 다음 차례")
        r = await E("()=>{ const o=Board.o, s=B3.starM.position, T=B3.TP[o.star]; return [o.P[1].star, o.P[1].pos, o.star!==12, +Math.hypot(s.x-T.x, s.z-T.z).toFixed(2)]; }")
        ok(r[0] == 1 and r[1] == 13 and r[2] and r[3] < 0.2, f"주호 ⭐1 · 13번 칸 · 별은 새 칸 위 {r}")
        # 🔒 함정 표
        await E("()=>{ const o=Board.o; o.trap[5]=1; B3.tiles(); }")
        ok(await E("()=>B3.tg[5].children.some(m=>m.isSprite)"), "🔒 함정 칸에 표")
        # 🗺 전체 보기 · 문제 카드가 떠 있으면 판을 위로
        await E("()=>document.querySelector('[data-bd=ov]').click()")
        ok(await E("()=>B3.mode==='over'"), "🗺 전체 보기")
        await E("()=>{ clearTimeout(Board._to); Board.o.cur=0; Board.ask('red', ()=>{}); }")
        ok(await until("()=>document.querySelectorAll('#bdAct .bdO').length>0 && B3.padB>0.1"), f"문제 카드 높이만큼 판을 위로 {await E('()=>B3.padB')}")
        # 🏆
        await E("()=>{ const o=Board.o; clearTimeout(Board._to); o.q.done=1; Board.win(); }")
        ok(await until("()=>B3.mode==='win' && B3.fx.length>0", 40), "🏆 색종이 · 카메라가 우승자 둘레를 돎")
        await pg.wait_for_timeout(800); await pg.screenshot(path=OUT + "board428_win.png")
        await E("()=>document.querySelector('.bdEnd [data-bd=quit]').click()")
        ok(await E("()=>!B3.R && !document.querySelector('#bdStage') && !Board.o"), "닫으면 3D 를 다 지움")
        ok(not real_errs(errs), "오류 없음 " + str(real_errs(errs)[:3]))
        await br.close()
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)

asyncio.run(main())
