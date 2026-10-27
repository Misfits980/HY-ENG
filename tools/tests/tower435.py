"""(v435) 🗼 타워 조작감 — 사용자: "타워 진짜 더 불편해졌는데? · 카메라가 저절로 돈다 · 화면 돌리다가 조이스틱이 눌려짐" → 뒤에서 따라가기
  ① 조이스틱 = 동그라미 근처에서 누를 때만 (왼쪽 화면 다른 곳 = 카메라 돌리기)
  ② 카메라는 저절로 안 돎 (걸어도·옆면으로 가도) · 손으로 끌면 좌우 = 돌리기 · 위아래 = 높이
  ③ 🚩 다시 시작할 때만 가는 쪽 뒤로 맞춤 · 카메라 = 캐릭터 뒤 (가운데 기둥 안으로 안 들어감)"""
import asyncio, sys, os, math
os.environ["HY_REAL3D"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "FAIL ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        for (W, H, tag) in [(390, 844, "phone"), (1180, 820, "pad")]:
            ctx = await br.new_context(viewport={"width": W, "height": H}, is_mobile=True, has_touch=True)
            pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
            await pg.route("**/*", route); await pg.goto(ORIGIN + "proto/house.html"); await pg.wait_for_timeout(800)
            await pg.evaluate("()=>{ localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); localStorage.setItem('hyeng_proto_baitok','1'); }")
            await pg.reload(); await pg.wait_for_timeout(2500)
            E = pg.evaluate
            async def until(js, n=60):
                for _ in range(n):
                    try:
                        if await E(js): return True
                    except Exception: pass
                    await pg.wait_for_timeout(200)
                return False
            await E("()=>{ HOUSE.setWx(false); HOUSE.TW.seed='2026-10-07'; HOUSE.twEnterGo('easy'); }")
            ok(await until("()=>HOUSE.place()==='tower' && HOUSE.TW.on"), f"[{tag}] 타워 안")
            await pg.wait_for_timeout(1200)
            # ③ 처음 = 가는 쪽 뒤
            r = await E("""()=>{ const T=HOUSE.TW, H=HOUSE; const d=H.TDIR[0], c=H.camera.position, p=T.p; const bx=c.x-p.x, bz=c.z-p.z, L=Math.hypot(bx,bz);
                return [+((bx*d[0]+bz*d[1])/L).toFixed(2), +L.toFixed(1)]; }""")
            ok(r[0] < -0.9 and 3 < r[1] < 10, f"[{tag}] 시작: 카메라 = 캐릭터 뒤 (가는 쪽 반대) {r}")
            await pg.screenshot(path=OUT + f"tower435_{tag}_start.png")
            # ① 왼쪽 화면 가운데(조이스틱 밖) 끌기 = 카메라 · 조이스틱 안 눌림
            h = await E("()=>{ HOUSE.twJoyHome(); return HOUSE.TW.home; }")
            async def drag(x0, y0, x1, y1, pid):
                await E(f"""()=>{{ const el=document.elementFromPoint({x0},{y0}); const ev=(t,x,y)=>new PointerEvent(t,{{pointerId:{pid},pointerType:'touch',clientX:x,clientY:y,bubbles:true,cancelable:true,isPrimary:true}});
                    el.dispatchEvent(ev('pointerdown',{x0},{y0})); window.__el=el; window.__s=[!!HOUSE.TW.joy, !!HOUSE.TW.cam, HOUSE.TW.yaw]; }}""")
                await pg.wait_for_timeout(60)
                await E(f"()=>{{ window.__el.dispatchEvent(new PointerEvent('pointermove',{{pointerId:{pid},pointerType:'touch',clientX:{x1},clientY:{y1},bubbles:true}})); window.__s.push(HOUSE.TW.yaw, HOUSE.TW.pit, HOUSE.TW.inp.x, HOUSE.TW.inp.y); }}")
                s = await E("()=>window.__s")
                await E(f"()=>window.__el.dispatchEvent(new PointerEvent('pointerup',{{pointerId:{pid},pointerType:'touch',clientX:{x1},clientY:{y1},bubbles:true}}))")
                return s
            s = await drag(W * 0.3, H * 0.45, W * 0.3 + 120, H * 0.45 + 60, 7)
            ok(not s[0] and s[1] and abs(s[3] - s[2]) > 0.5 and s[4] > 0.45 and s[5] == 0 and s[6] == 0, f"[{tag}] 왼쪽 화면 가운데 끌기 = 카메라 (좌우·위아래) · 조이스틱 안 눌림 {[round(x,2) if isinstance(x,float) else x for x in s]}")
            s = await drag(h[0] + 20, h[1] - 10, h[0] + 20, h[1] - 60, 8)
            ok(s[0] and not s[1] and abs(s[3] - s[2]) < 1e-6 and s[6] > 0.5, f"[{tag}] 동그라미 누르기 = 조이스틱 (카메라 그대로) {[round(x,2) if isinstance(x,float) else x for x in s]}")
            # ② 저절로 안 돎: 걸어서 옆면으로 가도 yaw 그대로
            r = await E("""async()=>{ const T=HOUSE.TW, C=HOUSE.TWC; const y0=T.yaw, d0=T.dead; T.inp.x=0.5; T.inp.y=0.2; await new Promise(r=>setTimeout(r,500)); T.inp.x=T.inp.y=0; const a=+(T.yaw-y0).toFixed(4), da=T.dead-d0;
                T.bot=true; const out=[]; for(const [x,z] of [[C+7,C],[C,C+7],[C-7,C],[C,C-7]]){ T.p.set(x, 3, z); await new Promise(r=>setTimeout(r,500)); out.push(+(T.yaw-y0).toFixed(4)); } T.bot=false;
                return [a, da, out]; }""")
            ok((r[0] == 0 or r[1] > 0) and r[2] == [0, 0, 0, 0], f"[{tag}] 걸어도·네 면 어디로 가도 카메라가 저절로 안 돎 {r}")
            # ③ 🚩 다시 시작 → 뒤로 맞춤 · 기둥 안으로 안 들어감
            r = await E("""async()=>{ const T=HOUSE.TW, H=HOUSE; T.yaw+=2.0; H.twRespawn(false); await new Promise(r=>setTimeout(r,900)); const d=H.TDIR[T.cp%4], c=H.camera.position, p=T.p;
                const bx=c.x-p.x, bz=c.z-p.z, L=Math.hypot(bx,bz), C=H.TWC, K=H.TCORE; const inCore=Math.abs(c.x-C)<K && Math.abs(c.z-C)<K && c.y<T.hy+3;
                return [+((bx*d[0]+bz*d[1])/L).toFixed(2), inCore]; }""")
            ok(r[0] < -0.9 and not r[1], f"[{tag}] 떨어져서 다시 시작 → 가는 쪽 뒤로 · 기둥 안 아님 {r}")
            # 카메라를 기둥 쪽으로 돌려도 기둥 안으로 안 들어감
            r = await E("""async()=>{ const T=HOUSE.TW, H=HOUSE, C=H.TWC, K=H.TCORE; const p=T.p; T.yaw=Math.atan2(C-p.x, C-p.z); T.pit=0.25; await new Promise(r=>setTimeout(r,700)); const c=H.camera.position;
                return [Math.abs(c.x-C)<K && Math.abs(c.z-C)<K && c.y<T.hy+3, +T.camD.toFixed(2)]; }""")
            ok(not r[0] and r[1] < 7, f"[{tag}] 기둥 쪽으로 돌리면 카메라가 앞으로 당겨 옴 (기둥 안 X) {r}")
            await pg.screenshot(path=OUT + f"tower435_{tag}_core.png")
            await E("()=>{ const T=HOUSE.TW; T.pit=0.42; T.yaw=T.yawTo+0.6; }"); await pg.wait_for_timeout(600)
            await pg.screenshot(path=OUT + f"tower435_{tag}_turn.png")
            r = await E("()=>document.querySelector('#twUI .twHelp').textContent")
            ok("화면 끌기" in r, f"[{tag}] 도움말 {r!r}")
            await ctx.close()
        await br.close()
    real = real_errs(errs)
    ok(not real, f"오류 없음 {real[:3]}")
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)

asyncio.run(main())
