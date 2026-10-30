"""(v467) 🟢 쉬움 30층 — 사용자: "쉬움은 조금 더 쉽게 · 초반 진짜 연습하는 것처럼 체크포인트 있게"
  ① 1~9층 발판에 🚩 깃발 = 체크포인트 (닿으면 노랑 + 「체크포인트!」) · 10층은 🏝 땅
  ② 연습 구간: 깃발보다 3 아래로 떨어지면 바로 그 깃발로 · 용암 = 깃발로 · 🚩 단추 = 깃발로
  ③ 11층부터: 용암 = 🏝 10층 땅 (깃발은 10층까지만)
  ④ 더 쉬움: 사다리 1.5 · 점프 칸 넓게 · 흔들 공·바늘·레이저 느리게 (🗼 도전과 비교)"""
import asyncio, sys, os
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
        ctx = await br.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
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
        await E("()=>{ HOUSE.setWx(false); HOUSE.TW.seed='2026-10-30'; HOUSE.twEnterGo('kid'); }"); ok(await until("()=>HOUSE.place()==='tower' && HOUSE.TW.on"), "🟢 쉬움 타워 안")
        await pg.wait_for_timeout(500)
        r = await E("()=>{ const T=HOUSE.TW; return [T.cps.map((c,i)=>c.flag?i:-1).filter(i=>i>=0), T.secs[9], document.getElementById('toast').innerText]; }")
        ok(r[0] == list(range(1, 9)) and r[1] == "ground" and "깃발" in r[2], f"🚩 깃발 = 1~8 발판 (2~9층 시작) · 10층 = 🏝 땅 · 들어갈 때 안내 {r}")
        r = await E("""()=>{ const T=HOUSE.TW; T.bot=false; T.cp=0; T.best=0; const c=T.cps[4]; T.p.set((c.min.x+c.max.x)/2, c.max.y+0.3, (c.min.z+c.max.z)/2); T.v.set(0,0,0); T.onG=false; T.lastGY=null; for(let i=0;i<40;i++) HOUSE.twStep(1/90);
            return [T.cp, c.flag.material.color.getHexString(), document.getElementById('toast').innerText]; }""")
        ok(r[0] == 4 and r[1] == "ffd23f" and "체크포인트" in r[2], f"5층 깃발에 닿음 → 체크포인트 · 깃발 노랑 {r}")
        await pg.screenshot(path=OUT + "tower467_flag.png")
        r = await E("""()=>{ const T=HOUSE.TW, c=T.cps[4]; const a=T.S.slice(T.secR[4][0],T.secR[4][1]).find(s=>s.kind==='solid'); T.p.set((a.min.x+a.max.x)/2+8, a.max.y+0.5, (a.min.z+a.max.z)/2+8); T.v.set(0,0,0); T.onG=false; let n=0; while(n<400){ HOUSE.twStep(1/90); n++; if(Math.abs(T.p.y-c.max.y)<0.01 && T.onG) break; }
            const fallBack=[+(T.p.y-c.max.y).toFixed(2), Math.hypot(T.p.x-(c.min.x+c.max.x)/2, T.p.z-(c.min.z+c.max.z)/2)<0.05, document.getElementById('toast').innerText];
            const L={kind:'kill', on:true, min:new THREE.Vector3(T.p.x-1,T.p.y-0.2,T.p.z-1), max:new THREE.Vector3(T.p.x+1,T.p.y+0.5,T.p.z+1), mesh:new THREE.Object3D()}; T.p.y+=0.01; T.S.push(L); HOUSE.twStep(1/90); T.S.pop(); const lava=[+(T.p.y-c.max.y).toFixed(2)];
            T.p.set(T.p.x+1, T.p.y, T.p.z); document.getElementById('twRe').click(); return [fallBack, lava, +(T.p.y-c.max.y).toFixed(2)]; }""")
        ok(abs(r[0][0]) < 0.02 and r[0][1] and "깃발" in r[0][2] and abs(r[1][0]) < 0.02 and abs(r[2]) < 0.02, f"떨어짐 → 5층 깃발 · 용암 → 깃발 · 🚩 단추 → 깃발 {r}")
        r = await E("""()=>{ const T=HOUSE.TW; T.cp=15; const c=T.cps[15]; T.p.set((c.min.x+c.max.x)/2, c.max.y+0.01, (c.min.z+c.max.z)/2); T.v.set(0,0,0); HOUSE.twStep(1/90); const L={kind:'kill', on:true, min:new THREE.Vector3(T.p.x-1,T.p.y-0.2,T.p.z-1), max:new THREE.Vector3(T.p.x+1,T.p.y+0.5,T.p.z+1), mesh:new THREE.Object3D()}; T.S.push(L); HOUSE.twStep(1/90); T.S.pop();
            return [+(T.p.y-T.cps[9].max.y).toFixed(2), document.getElementById('toast').innerText]; }""")
        ok(abs(r[0]) < 0.05 and "10층 땅" in r[1], f"16층 용암 → 🏝 10층 땅 {r}")
        r = await E("""()=>{ const T=HOUSE.TW, rise=m=>{ HOUSE.twBuild(m); const a=[]; for(let i=1;i<T.ys.length;i++) if(T.secs[i-1]!=='ground' && (m!=='sky' || i<10)) a.push(T.ys[i]-T.ys[i-1]); return a; };
            T.seed='2026-10-30'; const kid=rise('kid'); HOUSE.twBuild('kid'); const kS=T.S.filter(s=>s.kind==='sweep').map(s=>Math.abs(s.sp)), kP=T.S.filter(s=>s.kind==='pend').map(s=>s.sp);
            const gk=T.S.slice(T.secR[T.secs.indexOf('gaps')]?.[0]||0, T.secR[T.secs.indexOf('gaps')]?.[1]||0).filter(s=>s.kind==='solid').map(s=>+Math.max(s.max.x-s.min.x,s.max.z-s.min.z).toFixed(2));
            HOUSE.twBuild('easy'); const gE=T.secs.indexOf('gaps')>=0 ? T.S.slice(T.secR[T.secs.indexOf('gaps')][0],T.secR[T.secs.indexOf('gaps')][1]).filter(s=>s.kind==='solid').map(s=>+Math.max(s.max.x-s.min.x,s.max.z-s.min.z).toFixed(2)) : [];
            return [+Math.min(...kid).toFixed(2), +(kid.reduce((a,b)=>a+b,0)/kid.length).toFixed(2), kS.length?Math.max(...kS):0, kP.length?Math.max(...kP):0, gk.slice(0,3), gE.slice(0,3)]; }""")
        ok(r[0] <= 1.5 and r[1] < 2.7 and (r[2] == 0 or r[2] <= 0.95) and (r[3] == 0 or r[3] <= 1.15) and r[4][0] > r[5][0], f"쉬움: 사다리 1.5 · 층 높이 평균 {r[1]} · 바늘 ≤0.95 · 흔들 공 ≤1.15 · 점프 칸 {r[4]} (예전 쉬움 {r[5]}) {r}")
        ok(not real_errs(errs), "오류 없음 " + str(real_errs(errs)[:3]))
        await br.close()
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)
asyncio.run(main())
