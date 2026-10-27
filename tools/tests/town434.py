"""(v434) 🎨 My Town 그래픽 — 사용자: "마이타운 그래픽 개선 · 1~3 해 줘"
  ① 하늘(시간마다 색) · 섬 둘레 들판·숲·산·구름 · 안개   ② 그림 바닥·벽지 3개씩 + 질감 그림 자리(assets/town/tex)
  ③ KayKit(CC0) 모델: 마을 집 4채 · 마당 바위 · 새 가구 14 · 마당 꾸미기 8 — 고르기(누르기) 그대로"""
import asyncio, sys, os
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
        pg = await br.new_page(viewport={"width": 1180, "height": 820}); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.add_init_script("(()=>{ const d=new Date(); const kst=new Date(d.getTime()+9*3600e3); const want=Date.UTC(kst.getUTCFullYear(),kst.getUTCMonth(),kst.getUTCDate(),13,10)-9*3600e3; const off=want-d.getTime(); const N=Date.now; Date.now=()=>N()+off; })()")
        await pg.route("**/*", route); await pg.goto(ORIGIN + "proto/house.html"); await pg.wait_for_timeout(4000)
        E = pg.evaluate
        async def until(js, n=60):
            for _ in range(n):
                if await E(js): return True
                await pg.wait_for_timeout(250)
            return False
        ok(await until("()=>!!(KK.R.nature && KK.R.furniture)"), "KayKit 묶음 2개 읽음")
        r = await E("()=>[Object.keys(KK.R.nature.G).length, Object.keys(KK.R.furniture.G).length, KK.R.nature.tex.image && KK.R.nature.tex.image.width]")
        ok(r[0] >= 30 and r[1] >= 30 and r[2] == 512, f"자연 모델 · 가구 모델 · 텍스처 512 {r}")
        # 방 = 하늘·안개 없음
        ok(await E("()=>!skyDome.visible && !scene.fog"), "집 안 = 하늘 공·안개 없음")
        # ③ 새 가구
        r = await E("""()=>{ const ids=Object.keys(ITEMS).filter(k=>k.startsWith('kk_')); const p=addPlaced('kk_couch',3,3,0,1); const m=p.obj.getObjectByProperty('isMesh',true); const bb=new THREE.Box3().setFromObject(p.obj), s=new THREE.Vector3(); bb.getSize(s);
            return [ids.length, ids.every(k=>PRICE[k]>0), !!m, !!(m && m.userData.p===p), +s.x.toFixed(2), +s.z.toFixed(2), m && m.name]; }""")
        ok(r[0] == 14 and r[1], f"새 가구 14개 · 가게 값 {r[:2]}")
        ok(r[2] and r[3] and r[4] <= 1.96 and r[5] <= 0.98 and r[6] == "kk:couch_pillows", f"🛋 couch(노랑) = 모델 · 칸(2×1) 안 · 눌러서 고르기 {r[2:]}")
        r = await E("()=>{ const out=Object.keys(ITEMS).filter(k=>k.startsWith('kk_')).map(k=>{ const g=ITEMS[k].build(0); const bb=new THREE.Box3().setFromObject(g), s=new THREE.Vector3(); bb.getSize(s); const it=ITEMS[k]; return [k, s.x<=it.sz[0]+0.01 && s.z<=it.sz[1]+0.01 && s.y>0.005 && s.y<2.2]; }); return out.filter(x=>!x[1]).map(x=>x[0]); }")
        ok(r == [], f"새 가구 모두 칸 안 · 높이 알맞음 {r}")
        r = await E("()=>[FLOORS.length, WALLS.length, FLOORS.slice(-3).map(f=>f.file), WALLS.slice(-3).map(f=>f.file)]")
        ok(r[2] == ["floor_oak", "floor_herring", "floor_tile"] and r[3] == ["wall_flower", "wall_wood", "wall_star"], f"② 그림 바닥·벽지 3개씩 (그림 자리) {r}")
        await E("()=>{ setFloor(FLOORS.length-3); setWall(WALLS.length-1); dirty=true; }"); await pg.wait_for_timeout(800)
        ok(await E("()=>floorMat.map.image.width===512 && wallMat.map.image.width===512"), "그림 바닥·벽지 = 512 (그림이 오면 또렷하게)")
        await pg.screenshot(path=OUT + "town434_room.png")
        # 마당 = 하늘·안개·둘레
        await E("()=>go('yard')"); await pg.wait_for_timeout(3500)
        r = await E("()=>{ const F=yardG.getObjectByName('farLand'); return [skyDome.visible, !!scene.fog, F && F.children.length, scene.userData.rocks.every(R=>R.children.some(c=>c.children && c.children[0] && /^kk:rock/.test(c.children[0].name)))]; }")
        ok(r[0] and r[1] and r[2] > 40 and r[3], f"① 마당: 하늘 공 · 안개 · 들판·숲·산·구름 {r[2]}개 · 바위 = 모델 {r}")
        r = await E("()=>{ const c=skyDome.geometry.attributes.color; let top=0, bot=0; for(let i=0;i<c.count;i++){ const y=skyDome.geometry.attributes.position.getY(i); if(y>150) top=c.getZ(i); if(y<-150) bot=c.getZ(i); } return [+top.toFixed(3), +bot.toFixed(3)]; }")
        ok(r[0] != r[1], f"하늘 = 위아래 색이 다름 {r}")
        r = await E("()=>{ const p=yAdd('kk_mill', 11, 11, 0, 0); const m=p.obj.getObjectByProperty('isMesh',true); return [!!m, !!(m && m.userData.yp===p), Object.keys(OUT).filter(k=>k.startsWith('kk_')).length]; }")
        ok(r[0] and r[1] and r[2] == 8, f"마당 꾸미기 KayKit 8개 · 풍차 놓기 · 고르기 {r}")
        await pg.wait_for_timeout(600); await pg.screenshot(path=OUT + "town434_yard.png")
        tri = await E("()=>{ renderer.render(scene,camera); return renderer.info.render.triangles; }")
        ok(tri < 250000, f"마당 삼각형 수 (아이패드 부담) {tri}")
        # 마을 = 집 4채 모델 · 밤 색
        await E("()=>go('village')"); await pg.wait_for_timeout(3500)
        r = await E("()=>scene.userData.vHouses.map(H=>H.children.some(c=>c.children && c.children[0] && /^kk:building_home_A/.test(c.children[0].name)))")
        ok(r == [True]*4, f"③ 마을 집 4채 = KayKit 집 {r}")
        await pg.screenshot(path=OUT + "town434_village.png")
        r = await E("()=>{ townEnv(true,'n',false); const n=skyKey; townEnv(true,'d',false); return [n, skyKey]; }")
        ok(r[0] != r[1], f"밤·낮 하늘 색이 다름 {r}")
        await E("()=>go('room')"); await pg.wait_for_timeout(2500)
        ok(await E("()=>!skyDome.visible && !scene.fog"), "다시 집 안 = 하늘·안개 끔")
        ok(not real_errs(errs), "오류 없음 " + str(real_errs(errs)[:3]))
        await br.close()
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)

asyncio.run(main())
