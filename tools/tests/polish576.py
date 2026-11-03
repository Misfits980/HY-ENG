"""(v576) 섬 「나사 빠진」 곳 2차 고침 (미술 감독 점검) 사진첩 + 검사
   놀이터(미끄럼틀·그네·시소·뺑뺑이·울타리 난간) · 보물 상자 · 밭 사이 나무 · 텐트 · 광산 길 끝 · 공사장 3곳(다른 모양 · 게이지 · 울타리 막힘)
   시계 바늘 2개 · 숲속 나 실루엣 · 1단계 집 크기 · 덤불 · 간판 두 겹 · 기차역 지붕 · 모닥불
   PRE=1 → 고치기 전 사진만 (b_ 앞붙임 · 검사 안 함)"""
import asyncio, sys, os
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
import fakefb
from fakefb import fake
from playwright.async_api import async_playwright
D=OUT+"pol576"+os.sep; os.makedirs(D, exist_ok=True)
PRE=os.environ.get("PRE")=="1"; PF="b_" if PRE else ""

async def main():
    bad=[]; errs=[]
    # 친구 집 (1~4단계 · 모양 A·B·M) — 집 크기 보기
    fakefb.DB.setdefault("hy",{}).setdefault("isle",{})["lot2"]={"1-3":{"k":"a","c":"AAAAA","n":"민지","t":1,"h":"A_red"},"1-5":{"k":"b","c":"BBBBB","n":"준","t":1,"h":"B_blue"},"1-7":{"k":"c","c":"CCCCC","n":"하나","t":1,"h":"M_green"},"1-4":{"k":"d","c":"DDDDD","n":"솔","t":4,"h":"A_yellow"},"1-6":{"k":"e","c":"EEEEE","n":"윤","t":3,"h":"B_green"},"1-8":{"k":"f","c":"FFFFF","n":"별","t":2,"h":"A_blue"}}
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        ctx=await br.new_context(viewport={"width":1180,"height":820}, has_touch=True)
        pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html?isle=1"); await pg.wait_for_timeout(400)
        await pg.evaluate("()=>{ localStorage.setItem('hyeng_proto_code', JSON.stringify('POLSH')); localStorage.setItem('hyeng_nick','루아'); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); }")
        await pg.reload(); await pg.wait_for_timeout(2600)
        await pg.evaluate("()=>HOUSE.exitRoom()")
        for _ in range(160):
            if await pg.evaluate("()=>HOUSE.place()==='isle' && !HOUSE.trip().busy"): break
            await pg.wait_for_timeout(250)
        await pg.wait_for_timeout(1500)
        S=await pg.evaluate("()=>ISLE_MAP.spots")
        async def at(name, x, z, zoom=1.5, pitch=.9, yw=None):
            await pg.evaluate("([x,z,zm,pt,yw])=>{ ISLE.CAM.zoom=zm; ISLE.CAM.pitch=pt; TFAC.warp(x+98,z+98); if(yw!==null){ yaw=yawTo=yw; ISLE.CAM.dragAt=performance.now()+1e6; } }", [x, z, zoom, pitch, yw])
            await pg.wait_for_timeout(1300); await pg.screenshot(path=D+PF+name+".png")
        await pg.evaluate("()=>HOUSE.setWx(false)")
        # 사진 — 자리마다
        pgx,pgz=S["pg"]; cx,cz=S["chest"]
        await at("01_playground", pgx-1.5, pgz+1.0, 2.0, .75, 2.2)
        await at("02_park_top", pgx, pgz, 2.4, 1.1, 0.3)
        await at("03_chest", cx+.71*2.0+.71*1.1, cz+.71*2.0-.71*1.1, .6, .4, 0.6)
        await at("04_farm", S["farm"][0]+2, S["farm"][1]+9, 2.4, 1.1, 0.0)
        await at("05_tents", -46.5, -8.5, 1.3, .55, 0.785)
        await at("06_mine_road", 16, -52, 2.4, 1.15, 0.0)
        await at("06b_mine_door", 17.5, -56.5, 1.2, .55, 1.4)
        await at("07_site1", -53.5+6.2, 30, 1.6, .62, 1.5708)
        await at("08_site2", 48.5, 56.5-6.5, 1.6, .62, 3.1416)
        await at("09_site3", -31, -59+6.5, 1.8, .62, 0.0)
        await at("10_library_clock", S["library"][0]-.62*5.5+.78*1.6, S["library"][1]+.78*5.5+.62*1.6, 2.4, .5, -0.67)
        await at("11_station", S["station"][0]-.18*5+1.2, S["station"][1]+.98*5, 1.5, .8, -0.18)
        await at("11b_station_clock", S["station"][0]-.18*8+1.0, S["station"][1]+.98*8, 1.3, .28, -0.18)
        await at("12_lots", -10.5, 19.2, 1.3, .55, 1.5708)
        await at("13_bushes", -40, 4, 2.4, 1.0, 0.0)
        await at("15_camp", S["camp"][0]+2.4, S["camp"][1]+.6, .8, .6, 1.5708)
        fd=await pg.evaluate("()=>{ const s=ISLE.SPOT.shops[0]; return [s.door[0]-98, s.door[1]-98]; }")
        await at("14_shop_sign", fd[0], fd[1], 1.1, .55, None)
        sg=await pg.evaluate("()=>{ let o=null; ISLE.G.traverse(m=>{ if(m.isSprite && m.userData.lbl==='fish') o=m; }); const L=LBL.find(l=>l.d.k==='fish'); return [o?o.visible:null, L?!!L.near:null]; }")
        if not PRE: ok(sg[1] is True and sg[0] is False, f"가게 앞 = 이름표만 (3D 간판 숨김) {sg}")
        await at("14b_shop_far", fd[0]-6, fd[1]+6, 1.6, .7, None)
        # (v577) 멀리 = 이름표가 접힘 → 3D 간판은 이름표 때문에 숨지 않음 (카메라와 나 사이에 있으면 원래 규칙대로 흐려짐)
        sg=await pg.evaluate("()=>{ let o=null; ISLE.G.traverse(m=>{ if(m.isSprite && m.userData.lbl==='fish') o=m; }); const L=LBL.find(l=>l.d.k==='fish'), h=HOUSE.hero().g.position; const front=o && o.position.distanceTo(camera.position) < camera.position.distanceTo(h)-3.5; return [L?!!L.near:null, o?o.visible:null, !!front]; }")
        if not PRE: ok(sg[0] is False and (sg[1] is True or sg[2] is True), f"멀리서는 3D 간판 (이름표 접힘 · 앞을 가리면만 흐림) {sg}")
        # 숲 속 (나무에 가려도 실루엣)
        FOREST=await pg.evaluate("""()=>{ const T=ISLE.trees(), O=98; let best=null, bs=0; for(let i=0;i<T.length;i+=3){ const [tx,tz]=T[i]; for(let k=0;k<8;k++){ const a=k/8*6.283, hx=tx-Math.sin(a)*2.2, hz=tz-Math.cos(a)*2.2;
              if(ISLE.blocked(Math.floor(hx+O),Math.floor(hz+O))) continue; let n=0; T.forEach(([x,z])=>{ const u=(x-hx)*Math.sin(a)+(z-hz)*Math.cos(a), v=Math.abs((x-hx)*Math.cos(a)-(z-hz)*Math.sin(a)); if(u>.8 && u<4.5 && v<.9) n++; }); if(n>bs){ bs=n; best=[hx,hz,a]; } } } return best||[60,-22,0]; }""")
        print("forest", FOREST)
        await at("16_forest", FOREST[0], FOREST[1], 1.0, .3, FOREST[2])
        gh=await pg.evaluate("()=>window.HGHOST ? HGHOST.on() : null")
        if not PRE: ok(gh is True, f"숲에 가려지면 실루엣 켜짐 {gh}")
        await at("17_open", 0, 9.5, 1.6, .8, 0.0)
        gh=await pg.evaluate("()=>window.HGHOST ? HGHOST.on() : null")
        if not PRE: ok(gh is False, f"트인 곳 = 실루엣 꺼짐 {gh}")
        if not PRE:
            r=await pg.evaluate("""()=>{ const G=ISLE.G, U=G.userData; return {pg:U.pgParts||0, chest:!!(U.chest && U.chest.userData.v576), tents:U.tents||0, calls:renderer.info.render.calls}; }""")
            ok(r["pg"]>=4, f"놀이터 기구 {r['pg']}")
            ok(r["chest"], "보물 상자 = 둥근 뚜껑 상자")
            ok(r["tents"]==2, f"텐트 2 {r['tents']}")
            print("draw calls", r["calls"])
            n=await pg.evaluate("()=>{ const f=ISLE_MAP.spots.farm; return ISLE.treeIn(f[0]-6.8,f[1]-4,f[0]+6.8,f[1]+4); }")
            ok(n==0, f"밭 안 나무 {n}")
            d=await pg.evaluate("()=>{ const r=ISLE_MAP.roads.mine.p, e=r[r.length-1], m=ISLE_MAP.spots.mine; return Math.hypot(e[0]-m[0],e[1]-m[1]); }")
            ok(d<3.6, f"광산 길 끝 ↔ 입구 {d:.2f}")
            fb=await pg.evaluate("""()=>{ const O=98, out=[]; ['free1','free2','free3'].forEach(k=>{ const Z=ISLE_MAP.zones.find(z=>z.k===k); let x=0,z=0; Z.poly.forEach(q=>{x+=q[0];z+=q[1];}); x/=Z.poly.length; z/=Z.poly.length; let n=0, t=0;
                for(let s=-3.25;s<=3.25;s+=.25){ [[s,-3.25],[s,3.25],[-3.25,s],[3.25,s]].forEach(([u,v])=>{ t++; if(ISLE.blocked(Math.floor(x+O+u),Math.floor(z+O+v))) n++; }); } out.push(+(n/t).toFixed(2)); }); return out; }""")
            ok(all(v>.97 for v in fb), f"공사장 울타리 막힘 {fb}")
            sites=await pg.evaluate("""()=>{ const out=[]; ISLE.G.children.forEach(o=>{ if(o.userData.board) out.push(o.children.length); }); return out; }""")
            ok(len(sites)==3, f"공사장 게이지판 3 {sites}")
            sp=await pg.evaluate("""()=>{ let n=0; ISLE.G.traverse(o=>{ if(o.isSprite && o.material.map && o.material.map.image && o.material.map.image.width===512 && Math.abs(o.scale.x-2.8)<.01) n++; }); return n; }""")
            ok(sp==0, f"「새 구역 준비 중」 팻말 없앰 {sp}")
            hs=await pg.evaluate("()=>ISLE.lots.filter(l=>l.obj && l.tier===1).map(L=>{ const b=new THREE.Box3().setFromObject(L.obj); return +(b.max.y-b.min.y).toFixed(2); })")
            ok(len(hs)>0 and min(hs)>1.85, f"1단계 집 높이 (나 1.7) {hs}")
            ov=await pg.evaluate("()=>ISLE.lots.filter(l=>l.obj).map(L=>{ const b=new THREE.Box3().setFromObject(L.obj), c=Math.cos(L.face), s=Math.sin(L.face); let m=0; [[b.min.x,b.min.z],[b.max.x,b.max.z],[b.min.x,b.max.z],[b.max.x,b.min.z]].forEach(([x,z])=>{}); return +Math.max(b.max.x-b.min.x, b.max.z-b.min.z).toFixed(2); })")
            ok(max(ov)<2.35, f"집 넓이 ≤ 땅 칸 {ov}")
            st=await pg.evaluate("()=>ISLE.stuckDoors().length")
            ok(st==0, f"문 막힘 없음 {st}")
        await br.close()
    ok(not errs, f"오류 없음 {errs[:2]}")
    print("\nFAIL" if bad else "\nPASS", len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
