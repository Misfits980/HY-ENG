"""(v607~) 🏝 새 섬 5판 (?v5=1) — 땅·다리·길·가게 문·시설·집 문이 광장에서 다 걸어갈 수 있는지 + 위에서 본 사진
사용자(11-06): 「A+C 를 합쳐서 조율」 → 「농장 섬 밭으로 · 애들이 가깝게」 → 「시작하자」"""
import asyncio, sys, os
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from fakefb import fake
from playwright.async_api import async_playwright
D=OUT+"isle607v5"+os.sep; os.makedirs(D, exist_ok=True)
async def main():
    bad=[]; errs=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        pg=await (await br.new_context(viewport={"width":820,"height":1180}, has_touch=True)).new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html?isle=1&v5=1"); await pg.wait_for_timeout(400)
        await pg.evaluate("()=>{ localStorage.setItem('hyeng_proto_code', JSON.stringify('V5T07')); localStorage.setItem('hyeng_nick','루아'); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); }")
        await pg.reload(); await pg.wait_for_timeout(2800)
        await pg.evaluate("()=>HOUSE.exitRoom()")
        for _ in range(240):
            if await pg.evaluate("()=>HOUSE.place()==='isle' && !HOUSE.trip().busy"): break
            await pg.wait_for_timeout(250)
        r=await pg.evaluate("()=>({v5:!!ISLE_MAP.v5, N:ISLE.N, isles:(ISLE_MAP.isles||[]).length, links:(ISLE_MAP.links||[]).length, lots:ISLE_MAP.allLots().length, open:ISLE.lots.length, shops:(ISLE.SPOT.shops||[]).length})")
        ok(r['v5'] and r['N']==280, f"새 섬 5판 켜짐 {r}")
        ok(r['lots']==96 and r['open']>=48, "땅 96칸 (처음 1~3동 48칸)")
        ok(r['shops']==8, "가게 8곳")
        # 광장에서 걸어서 갈 수 있는지 — 섬마다 · 가게 문 · 시설 · 집 문 앞
        R=await pg.evaluate("""()=>{ const N=ISLE.N, OX=ISLE.OX, OZ=ISLE.OZ, pc=ISLE.plazaCell(), seen=ISLE.reachFrom(pc[0],pc[1]);
          const reach=(x,z)=>{ const bx=Math.floor(x), bz=Math.floor(z); for(let r=0;r<3;r++) for(let dx=-r;dx<=r;dx++) for(let dz=-r;dz<=r;dz++){ const k=(bx+dx)*N+(bz+dz); if(seen[k]) return true; } return false; };
          const out={isle:{}, shop:{}, spot:{}, lots:0, lotsBad:[]};
          (ISLE_MAP.isles||[]).forEach(I=>{ if(I.lock) return; let hit=false; for(let a=0;a<6.28 && !hit;a+=.3) for(let t=.1;t<.7 && !hit;t+=.1){ const x=I.cx+Math.cos(a)*I.R*t+OX, z=I.cz+Math.sin(a)*I.R*t+OZ; if(seen[Math.floor(x)*N+Math.floor(z)]) hit=true; } out.isle[I.k]=hit; });
          (ISLE.SPOT.shops||[]).forEach(S=>{ out.shop[S.k]=reach(S.door[0],S.door[1]); });
          ["school","library","museum","station","post","bank","stage","dock","mine","tower","vil","ox","pg","chest"].forEach(k=>{ const s=ISLE_MAP.spots[k]; if(!s) return; out.spot[k]=reach(s[0]+OX+0, s[1]+OZ+0) || reach(s[0]+OX+2, s[1]+OZ+2) || reach(s[0]+OX-2, s[1]+OZ+2) || reach(s[0]+OX+2, s[1]+OZ-2) || reach(s[0]+OX-2, s[1]+OZ-2) || reach(s[0]+OX, s[1]+OZ+3.5) || reach(s[0]+OX, s[1]+OZ-3.5); });
          ISLE.lots.forEach(L=>{ const d=ISLE.doorCellOf(L); if(seen[d[0]*N+d[1]]) out.lots++; else out.lotsBad.push(L.id); });
          return out; }""")
        ok(all(R['isle'].values()), f"둘레 섬 다 걸어서 감 {R['isle']}")
        ok(all(R['shop'].values()), f"가게 문 앞 다 감 {R['shop']}")
        ok(all(R['spot'].values()), f"시설 다 감 {R['spot']}")
        ok(not R['lotsBad'], f"집 문 앞 {R['lots']}칸 다 감 {R['lotsBad'][:6]}")
        # 위에서 본 사진
        await pg.evaluate("()=>{ HOUSE.setWx(false); window._f=window.focus; window._ff=window.fitFor; window.focus=()=>({c:new THREE.Vector3(ISLE.OX+2, 0, ISLE.OZ-8), C:[], b:[1,-1,1], pitch:1.18}); window.fitFor=()=>340; camera.far=1400; camera.updateProjectionMatrix(); yaw=yawTo=0; scene.fog=null; }")
        await pg.set_viewport_size({"width":1400,"height":1100}); await pg.wait_for_timeout(2500); await pg.screenshot(path=D+"over.png", timeout=120000)
        await br.close()
    ok(not errs, f"오류 없음 {errs[:2]}")
    print("\nFAIL" if bad else "\nPASS", len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
