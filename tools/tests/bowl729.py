"""(v729) 🎳 볼링 손보기 — 사용자 「버그도 찾아보고 … 볼링 물총아레나 특히」
   ① 느린 공이 핀에 부딪혀 거의 멈추거나 거꾸로 굴러오던 것 (전: 5초 · 19초 기다림) → 공은 늘 앞으로 · 6.5초 안에 셈
   ② 겨냥 점선 = 분홍 · 크게 (노란 레인 위 노란 점은 안 보였음)
   ③ BOWLING 간판이 점수 화면 뒤에 가려 잘려 보이던 것 → 점수 화면 아래
   ④ 내 캐릭터가 세로 휴대폰에서 공 길을 가리던 것 → 조금 옆 · 작게
   ⑤ 패드: 점수판 · 단추 · 안내 크게"""
import asyncio, sys, os
os.environ["HY_REAL3D"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from draw635 import boot
from playwright.async_api import async_playwright

ENTER = """async ()=>{ MG.lobby('bowl'); for(let i=0;i<80;i++){ if(MG.on && MG.run && MG.run.ready) break; await new Promise(r=>setTimeout(r,200)); } MG.run.menuGo('bowl'); return !!MG.run; }"""
ROLL = """async ([x,vx,vz])=>{ const R=MG.run, B=R.bw; R.menuGo('bowl'); for(let i=0;i<200 && B.ph!=='aim';i++) MG.step(.05,false);
  R.throwBall(x,vx,vz); const r0=B.rolls.length; let n=0, back=false, tMax=0;
  while(B.rolls.length===r0 && n<4000){ MG.step(.02,false); n++; if(B.vz>0.01) back=true; if(B.ph==='roll') tMax=B.t; }
  return [B.rolls[B.rolls.length-1], back, +tMax.toFixed(2)]; }"""

async def main():
    bad = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        ctx, pg, errs = await boot(br, "루아", "BW729A", vp={"width": 390, "height": 844}, isle=False)
        await pg.evaluate(ENTER); await pg.wait_for_timeout(600); await pg.evaluate("()=>{ MG.run.SET.bump=1; }")
        # ① 예전에 거꾸로 굴러오던 공들 (느리게 · 가운데 근처)
        R = []
        for t in ([-.05, -.04, 5.9], [-.4, 0, 6], [.25, 0, 6], [-.3, 0, 10], [.45, 0, 10], [0, 0, 5]):
            R.append(await pg.evaluate(ROLL, t))
        ok(not any(r[1] for r in R), f"① 공이 거꾸로 안 굴러옴 {[r[1] for r in R]}")
        ok(max(r[2] for r in R) <= 6.5, f"① 느린 공도 6.5초 안에 끝 (굴림 시간 {[r[2] for r in R]})")
        ok(all(0 <= r[0] <= 10 for r in R), f"① 핀 수 0~10 {[r[0] for r in R]}")
        r = await pg.evaluate(ROLL, [.12, 0, 12]); ok(r[0] == 10, f"① 포켓(가운데 살짝 오른쪽)은 여전히 스트라이크 {r}")
        # ② ③ ④ 화면 물건
        r = await pg.evaluate("""()=>{ const R=MG.run; let guide=null, sign=null, mon=null, av=null;
            R.scene.traverse(o=>{ if(o.isGroup && o.children.length===14 && o.children.every(c=>c.geometry && c.geometry.type==='CircleGeometry')) guide=o;
              if(o.isMesh && o.geometry && o.geometry.type==='PlaneGeometry' && o.geometry.parameters.width===4 && o.geometry.parameters.height===1.1) sign=o;
              if(o.isMesh && o.geometry && o.geometry.type==='PlaneGeometry' && o.geometry.parameters.width===3.2 && o.geometry.parameters.height===1.0) mon=o; });
            const g=guide.children[0]; return {col:g.material.color.getHexString(), r:g.geometry.parameters.radius, signTop:+(sign.position.y+.55*sign.scale.y).toFixed(2), monBot:+(mon.position.y-.5).toFixed(2), bx:R.bw.bx}; }""")
        ok(r["col"] != "ffe14d" and r["r"] >= .08, f"② 겨냥 점선 색 #{r['col']} · 크기 {r['r']}")
        ok(r["signTop"] < r["monBot"], f"③ BOWLING 간판 위 {r['signTop']} < 점수 화면 아래 {r['monBot']} (안 가림)")
        r = await pg.evaluate("""()=>{ const R=MG.run; R.menuGo('bowl'); for(let i=0;i<40;i++) MG.step(.05,false); let av=null; R.scene.traverse(o=>{ if(!av && o.isGroup && o.userData && o.parent && o.parent.children.length>40 && o.scale.x<.75 && o.scale.x>.6) av=o; }); return av ? [+(av.position.x-R.bw.bx).toFixed(2), +av.scale.x.toFixed(2)] : null; }""")
        ok(r and r[0] >= .65 and r[1] <= .72, f"④ 캐릭터 = 공에서 {r and r[0]} 옆 · 크기 {r and r[1]}")
        # 진짜 손가락 쓱 → 굴러감
        await pg.evaluate("()=>{ MG.run.menuGo('bowl'); }"); await pg.wait_for_timeout(500)
        await pg.mouse.move(200, 740); await pg.mouse.down()
        for k in range(1, 8): await pg.mouse.move(202 + k, 740 - k * 45); await pg.wait_for_timeout(18)
        await pg.mouse.up(); await pg.wait_for_timeout(80)
        r = await pg.evaluate("()=>[MG.run.bw.ph, MG.run.bw.vz<0]"); ok(r == ["roll", True], f"쓱 밀기 → 굴러감 {r}")
        await pg.wait_for_timeout(600); await pg.screenshot(path=OUT + "bowl729_phone.png")
        E1 = real_errs(errs); await ctx.close()
        # ⑤ 패드
        ctx, pg, errs2 = await boot(br, "루아", "BW729B", vp={"width": 820, "height": 1180}, isle=False)
        await pg.evaluate(ENTER); await pg.wait_for_timeout(900)
        r = await pg.evaluate("()=>{ const z=s=>parseFloat(getComputedStyle(document.querySelector('#mgUI '+s)).zoom||1); const b=document.querySelector('#mgUI .spSc').getBoundingClientRect(); return [z('.spSc'), z('.spBtn'), z('.spSay'), Math.round(b.left), Math.round(b.right), innerWidth]; }")
        ok(r[0] >= 1.25 and r[1] >= 1.2 and r[2] >= 1.2 and r[3] >= 0 and r[4] <= r[5], f"⑤ 패드: 점수판 · 단추 · 안내 크게 · 화면 안 {r}")
        await pg.screenshot(path=OUT + "bowl729_pad.png")
        E2 = real_errs(errs2); await ctx.close()
        ok(not E1 and not E2, f"오류 없음 {(E1+E2)[:3]}")
        await br.close()
    print("\nFAIL" if bad else "\nPASS", len(bad)); sys.exit(1 if bad else 0)

if __name__ == "__main__": asyncio.run(main())
