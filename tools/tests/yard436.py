"""(v436) 🌳 내 땅(마당) 더 예쁘게 — 사용자: "마이타운 자기땅을 더 이쁘게 꾸며야할꺼같은데 너가 일단 해 주고 있어"
  ① 잔디 질감 512 (얼룩·풀잎·클로버) · 빈 칸마다 풀포기 (물건·길·밭·안 연 땅에서는 숨김)
  ② 안 연 땅: 뾰족 원뿔 → 동그란 덤불 + 긴 풀 + 들꽃 · 땅 색 진하게 · 열면 없어짐
  ③ 집 앞: 창 화분 · 덧문(문 색 따라감) · 돌계단 · 벽등(밤에 켜짐) · 덤불 / 뒤 울타리 밖 덤불 줄
  ④ 안 산 밭 = 흰 줄 틀 대신 흙 자리 · 디딤돌 = 넓적 돌"""
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
        await pg.route("**/*", route); await pg.goto(ORIGIN + "proto/house.html"); await pg.wait_for_timeout(800)
        await pg.evaluate("()=>{ localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); localStorage.setItem('hyeng_proto_baitok','1'); }")
        await pg.reload(); await pg.wait_for_timeout(3000)
        E = pg.evaluate
        await E("()=>{ HOUSE.setWx(false); go('yard'); }"); await pg.wait_for_timeout(3500)
        r = await E("""()=>{ const g=yardG.children.find(m=>m.geometry && m.geometry.type==='BoxGeometry' && m.material.map); const G=yardG.getObjectByName('yGrass');
            const vis=()=>{ let n=0; const m=new THREE.Matrix4(), s=new THREE.Vector3(), q=new THREE.Quaternion(), v=new THREE.Vector3(); for(let i=0;i<G.count;i++){ G.getMatrixAt(i,m); m.decompose(v,q,s); if(s.x>0.01) n++; } return n; };
            return [g && g.material.map.image.width, !!G, G && G.count, G && vis()]; }""")
        ok(r[0] == 512 and r[1] and r[2] == 14 * 14 * 2 and 60 < r[3] < r[2], f"① 잔디 512 · 풀포기 {r[2]}개 중 빈 칸만 보임 {r[3]}")
        r = await E("""()=>{ const G=yardG.getObjectByName('yGrass'); const cnt=(x,z)=>{ const m=new THREE.Matrix4(), s=new THREE.Vector3(), q=new THREE.Quaternion(), v=new THREE.Vector3(); let n=0; G.userData.L.forEach((L,i)=>{ if(L[0]===x&&L[1]===z){ G.getMatrixAt(i,m); m.decompose(v,q,s); if(s.x>0.01) n++; } }); return n; };
            const a=cnt(5,3); const p=yAdd('lamp',5,3,0,0); yFlowersUpd(); const b=cnt(5,3); yRemove(p); yFlowersUpd(); const c=cnt(5,3); yd.g['5,3']='dirt'; yDrawGround(); const d=cnt(5,3); delete yd.g['5,3']; yDrawGround();
            return [a,b,c,d, cnt(1,5), cnt(12,3)]; }""")
        ok(r[0] == 2 and r[1] == 0 and r[2] == 2 and r[3] == 0 and r[4] == 0 and r[5] == 0, f"풀포기: 물건 놓으면 숨음 · 치우면 다시 · 길 칠하면 숨음 · 밭·안 연 땅엔 없음 {r}")
        r = await E("""()=>{ const I=ywG.children.filter(m=>m.isInstancedMesh); return [I.length, I.some(m=>m.geometry===yGeo.tuft), I[0] && I[0].geometry.type, ywG.children.filter(m=>m.isMesh && !m.isInstancedMesh && m.material.transparent && m.material.opacity<0.3).length, ywG.userData.noFade]; }""")
        ok(r[0] == 3 and not r[1] and r[2] == "IcosahedronGeometry" and r[3] == 3 and r[4], f"② 안 연 땅 = 덤불·긴 풀·들꽃 (원뿔 없음) · 진한 땅 3곳 {r}")
        r = await E("()=>{ HOUSE.yd().pc=[1,0,0]; yDrawWild(); return [ywG.children.filter(m=>m.isMesh && !m.isInstancedMesh && m.material.transparent).length, ywG.children.filter(m=>m.isInstancedMesh).reduce((a,m)=>a+m.count,0)]; }")
        ok(r[0] == 2 and r[1] > 0, f"땅을 열면 그 땅의 덤불·진한 색 없어짐 {r}")
        await E("()=>{ HOUSE.yd().pc=[0,0,0]; yDrawWild(); }")
        r = await E("""()=>{ const H=scene.userData.houseObj, sh=[]; H.traverse(m=>{ if(m.userData.shutter) sh.push(m); }); const a=sh[0].material.color.getHex(); HOUSE.yd().hx.d=2; yHouseColors(); const b=sh[0].material.color.getHex(); HOUSE.yd().hx.d=0; yHouseColors();
            const L=scene.userData.wallLamp; yNight(true); const n=L.material.emissiveIntensity; yNight(false); const d=L.material.emissiveIntensity; const hd=yardG.getObjectByName('yHedge');
            return [sh.length, a!==b, b===new THREE.Color(HXC.d[2]).getHex(), n>1, d<0.5, hd && hd.children[0].count, hd && hd.userData.noFade]; }""")
        ok(r[0] == 4 and r[1] and r[2] and r[3] and r[4] and r[5] > 50 and r[6], f"③ 덧문 4 = 문 색 따라감 · 벽등 밤에 켜짐 · 울타리 밖 덤불 {r}")
        r = await E("""()=>{ const P=scene.userData.plotG[plotN]; const thin=[]; P.traverse(m=>{ if(m.isMesh){ m.geometry.computeBoundingBox(); const s=new THREE.Vector3(); m.geometry.boundingBox.getSize(s); if(Math.min(s.x,s.z)<0.1 && Math.max(s.x,s.z)>0.8) thin.push(m); } });
            const st=yardG.children.filter(m=>m.name==='step'); return [P.userData.st, thin.length, st.length, st.every(m=>m.geometry.parameters.radialSegments===7)]; }""")
        ok(r[0].startswith("lot") and r[1] == 0 and r[2] == 5 and r[3], f"④ 안 산 밭 = 흙 자리(줄 틀 없음) · 디딤돌 5 = 넓적 돌 {r}")
        await pg.screenshot(path=OUT + "yard436_day.png")
        await br.close()
    real = real_errs(errs)
    ok(not real, f"오류 없음 {real[:3]}")
    print("DONE bad=%d" % len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
