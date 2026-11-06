"""(v608) 🏝 새 섬 5판 QA — 3단계(시내 건물) · 4단계(텃밭 섬 「내 밭」) 뒤 전체 점검
사용자(11-06): 「3-4번 하고 qa 해 줘」 + 「그래픽 깨지는 거랑 이상한 모션들은?」
① 길·이동  ② 기록 옮기기  ③ 친구 방 나눔  ④ 화면(폰·패드)  ⑤ 속도  ⑧ 그래픽(뜸·묻힘·물 위·겹침·검은 덩어리·오류)  ⑨ 모션(발·회전·카메라 떨림)
결과 = out/isle608qa/qa.json + 사진 · GIF"""
import asyncio, sys, os, json, time, math
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
import fakefb
from fakefb import fake
from playwright.async_api import async_playwright
D=OUT+"isle608qa"+os.sep; os.makedirs(D, exist_ok=True)
RES={}; bad=[]; errs=[]
def ok(c,m,k=None,v=None):
    print(("OK  " if c else "BAD ")+m, flush=True)
    if not c: bad.append(m)
    if k: RES[k]=v
NOW=int(time.time()*1000)
SETUP="""(o)=>{ localStorage.setItem('hyeng_proto_code', JSON.stringify(o.code)); localStorage.setItem('hyeng_nick', o.n); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99}));
  localStorage.setItem('hyeng_proto_plotn', JSON.stringify(10)); localStorage.setItem('hyeng_proto_plotxy', JSON.stringify([[2,6],[3,6],[4,6],[5,6],[2,7],[3,7]]));
  localStorage.setItem('hyeng_proto_plots', JSON.stringify([{s:'carrot',g:99,wt:0},{s:'tomato',g:3,wt:Date.now()},{s:'pumpkin',g:99},{s:null},{s:'corn',g:1,wt:0},{s:'watermelon',g:99}]));
  if(o.v5!=null) localStorage.setItem('hyeng_isle_v5', o.v5?'1':'0'); }"""
async def enter(pg):
    await pg.evaluate("()=>HOUSE.exitRoom()")
    for _ in range(280):
        if await pg.evaluate("()=>HOUSE.place()==='isle' && !HOUSE.trip().busy"): return True
        await pg.wait_for_timeout(250)
    return False
async def kid(br, code, n, vw=(820,1180), v5=True):
    ctx=await br.new_context(viewport={"width":vw[0],"height":vw[1]}, has_touch=True); pg=await ctx.new_page()
    pg.on("pageerror", lambda e: errs.append(code+": "+str(e))); pg.on("console", lambda m: errs.append(code+": "+m.text) if m.type=="error" else None)
    await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html?isle=1"+("&v5=1" if v5 else "&v5=0")); await pg.wait_for_timeout(400)
    await pg.evaluate(SETUP, {"code":code, "n":n, "v5":v5}); await pg.reload(); await pg.wait_for_timeout(2600)
    await enter(pg); await pg.evaluate("()=>HOUSE.setWx(false)"); return pg
WARP="([x,z,ya,zoom,pitch])=>{ TFAC.warp(x+ISLE.OX, z+ISLE.OZ); yaw=yawTo=ya; ISLE.CAM.zoom=zoom||1.5; ISLE.CAM.pitch=pitch||.62; ISLE.CAM.dragAt=performance.now()+1e6; }"
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        A=await kid(br, "QAAA1", "루아")
        # ── ① 길·이동 ──
        r=await A.evaluate("""()=>{ const N=ISLE.N, OX=ISLE.OX, OZ=ISLE.OZ, W=ISLE.W, pc=ISLE.plazaCell(), seen=ISLE.reachFrom(pc[0],pc[1]);
          const near=(x,z,r)=>{ const bx=Math.floor(x), bz=Math.floor(z); for(let d=0;d<=(r||2);d++) for(let a=-d;a<=d;a++) for(let b=-d;b<=d;b++) if(seen[(bx+a)*N+(bz+b)]) return true; return false; };
          const out={isle:{}, shop:{}, fac:{}, lotsBad:[], fieldBad:[], train:{}, mg:[], trapped:[]};
          ISLE_MAP.isles.forEach(I=>{ if(I.lock) return; let hit=false; for(let a=0;a<6.28&&!hit;a+=.3) for(let t=.1;t<.7&&!hit;t+=.1){ const x=I.cx+Math.cos(a)*I.R*t+OX, z=I.cz+Math.sin(a)*I.R*t+OZ; if(seen[Math.floor(x)*N+Math.floor(z)]) hit=true; } out.isle[I.k]=hit; });
          (ISLE.SPOT.shops||[]).forEach(S=>out.shop[S.k]=near(S.door[0],S.door[1],1));
          Object.values(TFAC.SP||{}).forEach(S=>{ if(S && S.door) out.fac[S.k]=near(S.door[0],S.door[1],1); });
          ISLE_MAP.allLots().forEach(L=>{ const d=ISLE.doorCellOf(L); if(!near(d[0]+.5,d[1]+.5,1)) out.lotsBad.push(L.id); });
          ISLE.SLOTS().forEach(f=>{ if(!near(f.door[0]+.5,f.door[1]+.5,1)) out.fieldBad.push(f.id); });
          TFAC.DEST.forEach(d=>{ out.train[d[0]]=null; });
          (MG.GATES||[]).forEach(g=>out.mg.push([g.k, near(g.at[0]+OX, g.at[1]+OZ+3, 3) || near(g.at[0]+OX, g.at[1]+OZ-3, 3)]));
          /* 갇힌 곳: 걸을 수 있는데 광장과 안 이어진 덩어리 (6칸 이상) */
          const lab=new Uint8Array(N*N); for(let i=0;i<N*N;i++){ if(!W[i] || seen[i] || lab[i]) continue; const Q=[i]; lab[i]=1; for(let h=0;h<Q.length;h++){ const v=Q[h], x=Math.floor(v/N), z=v%N; [[1,0],[-1,0],[0,1],[0,-1]].forEach(([a,b])=>{ const k=(x+a)*N+(z+b); if(x+a<0||z+b<0||x+a>=N||z+b>=N||lab[k]||!W[k]) return; lab[k]=1; Q.push(k); }); } if(Q.length>=6){ const v=Q[0], x=Math.floor(v/N)-OX, z=v%N-OZ; const lockI=ISLE_MAP.isles.some(I=>I.lock && Math.hypot(x-I.cx,z-I.cz)<I.R+2), freeZ=ISLE_MAP.zones.some(Z=>Z.free && ISLE_MAP.inPoly(x,z,Z.poly)); if(!lockI && !freeZ) out.trapped.push([x, z, Q.length]); } }
          return out; }""")
        ok(all(r['isle'].values()), f"① 둘레 섬 다 걸어서 감 {r['isle']}")
        ok(all(r['shop'].values()), f"① 가게 문 {r['shop']}")
        ok(all(r['fac'].values()), f"① 시설 문 {r['fac']}")
        ok(not r['lotsBad'], f"① 집터 96칸 문 앞 {r['lotsBad'][:6]}")
        ok(not r['fieldBad'], f"① 텃밭 23자리 입구 {r['fieldBad'][:6]}")
        ok(all(x[1] for x in r['mg']), f"① 놀이 섬 게임 문 {r['mg']}")
        ok(len(r['trapped'])==0, f"① 갇힌 땅(잠긴 섬·공사장 빼고 광장과 안 이어짐 6칸+) {len(r['trapped'])}곳 {r['trapped'][:8]}", "trapped", r['trapped'])
        # 기차 — 행선지마다 내리는 자리가 걸을 수 있는 곳
        r=await A.evaluate("""()=>{ const o={}; TFAC.DEST.forEach(d=>{ const S=ISLE.SPOT; let p=null; try{ const k=d[0]; if(k==='home'){ const c=ISLE.doorCell(); p=c?[c[0]+.5,c[1]+.5]:null; } else if(k==='plaza') p=[ISLE.OX+2.6, ISLE.OZ+2.6]; else if(k==='park') p=S.oxC?[S.oxC[0]+3.6,S.oxC[1]-3.6]:null; else if(k==='market') p=S.shops&&S.shops[0]?S.shops[0].door:null; else if(k==='vil'){ const v=ISLE_MAP.spots.vil; p=[v[0]+ISLE.OX, v[1]+ISLE.OZ+7]; } else { const q=S[k]; p=q?[q[0],q[2]]:null; } }catch(e){}
            o[d[0]]=p ? TFAC.warp(p[0],p[1]) : false; }); return o; }""")
        ok(all(r.values()), f"① 🚉 기차 행선지 10곳 내리는 자리 {r}")
        # 걸리는 시간 (내 집 문 → 곳곳) = 길 칸 수 ÷ 걸음 3.4
        r=await A.evaluate("""()=>{ const d=ISLE.doorCell(), S=ISLE.SPOT, t={}; const go=(k,x,z)=>{ const P=findPath(d[0],d[1],Math.floor(x),Math.floor(z)); t[k]=P?Math.round(P.length/3.4):null; };
          const fs=ISLE.SLOTS(); go('텃밭(가까운 빈 밭)', fs[0].door[0], fs[0].door[1]); go('텃밭(먼 밭)', fs[fs.length-1].door[0], fs[fs.length-1].door[1]); go('광장', ISLE.OX, ISLE.OZ+3);
          go('마트', S.shops[0].door[0], S.shops[0].door[1]); go('학교', S.school[0], S.school[2]+4); go('호수 부두', S.lake[0]-3, S.lake[2]); go('놀이 섬', S.oxC[0]+3.6, S.oxC[1]-3.6); go('광산', S.mine[0], S.mine[2]+4); return {t, door:d, lot:ISLE.myHouse()&&ISLE.myHouse().id}; }""")
        ok(r['t']['텃밭(가까운 빈 밭)'] is not None and r['t']['텃밭(가까운 빈 밭)']<=35, f"① 내 집({r['lot']}) → 걸어서 (초) {r['t']}", "walkSec", r)
        # ── ② 기록 옮기기 (마당 밭 → 텃밭 섬) ──
        r=await A.evaluate("()=>({plots:plots.length, plotN, p0:plots[0], p2:plots[2], PL0:PLOTS[0], xy:localStorage.getItem('hyeng_proto_plotxy'), code:ISLE.fieldCode(), fd:ISLE.myFd(), path:vlNetPath()})")
        ok(r['plotN']==10 and r['plots']==10 and r['p0']['s']=='carrot' and r['p2']['s']=='pumpkin', f"② 작물·칸 수 그대로 (10칸 · 당근·호박) {r['code']}")
        ok(r['PL0'][0]<-100 and json.loads(r['xy'])[0]==[2,6], "② 마당 밭 자리 저장은 그대로(새 섬에선 화면 밖)")
        ok('/i5' in r['path'], f"③ 친구 방 = 새 섬 전용 {r['path']}")
        slot=await A.evaluate("()=>ISLE.SLOTS()[0].id")
        await A.evaluate("(i)=>ISLE.claimField(ISLE_MAP.fields.slots[i])", slot); await A.wait_for_timeout(400); await A.evaluate("()=>document.getElementById('askOk').click()"); await A.wait_for_timeout(1500)
        r=await A.evaluate("()=>({fd:ISLE.myFd(), rec:ISLE.myHouse() && ISLE.myHouse().rec})")
        ok(r['fd']==slot and r['rec'] and r['rec'].get('fd')==slot, f"② 빈 밭 → 내 밭 (서버 기록 fd) {r['rec']}")
        await A.evaluate("()=>ISLE.syncMine()"); await A.wait_for_timeout(800)
        srv=fakefb.DB.get('hy',{}).get('isle',{}).get('lot2',{})
        mine=[v for v in srv.values() if isinstance(v,dict) and v.get('c')=='QAAA1']
        ok(mine and mine[0].get('fc','').startswith('C'), f"② 친구에게 보일 밭 모습(fc) 서버에 {mine[0].get('fc') if mine else None}")
        # 친구 B — 같은 자리 못 고름 · A 밭이 보임
        B=await kid(br, "QABB2", "하준")
        r=await B.evaluate("(i)=>{ const f=ISLE.SLOTS().find(s=>s.id===i); return {n:f&&f.n, empty:f&&f.empty}; }", slot)
        ok(r['n']=='루아' and not r['empty'], f"② 친구 화면에 「루아의 밭」 {r}")
        await B.evaluate("(i)=>ISLE.claimField(ISLE_MAP.fields.slots[i])", slot); await B.wait_for_timeout(600)
        r=await B.evaluate("()=>({fd:ISLE.myFd(), ask:document.getElementById('ask').classList.contains('on')})")
        ok(r['fd'] is None, f"② 친구 밭은 못 고름 {r}")
        await B.context.close()   # 두 화면이 같이 돌면 느려져서 걷기 시간이 틀어짐
        # 수확 → 가방 · 밭 그림 바뀜 (밭 입구에서 — 먼 길 걷기는 아래 ⑨ 에서 따로)
        await A.evaluate("()=>{ const f=ISLE.SLOTS().find(s=>s.me); TFAC.warp(f.door[0]+.5,f.door[1]+.5); }"); await A.wait_for_timeout(500)
        r=await A.evaluate("""async ()=>{ const F=ISLE_MAP.fields.slots[ISLE.myFd()], c=Math.cos(F.face), si=Math.sin(F.face), u=-2, v=1.5, x=F.x+u*c+v*si+ISLE.OX, z=F.z-u*si+v*c+ISLE.OZ; const m0=mats.carrot||0;
            const t0=performance.now(); ISLE.fieldTap(x,z); for(let i=0;i<120;i++){ await new Promise(r=>setTimeout(r,250)); if(!plots[0].s) break; } return {m0, m1:mats.carrot||0, sec:Math.round((performance.now()-t0)/100)/10, code:ISLE.fieldCode()}; }""")
        ok(r['m1']>r['m0'], f"② 내 밭 칸 누르면 걸어가서 수확 {r}")
        # ── ⑨ 모션: 집 → 밭 걷기 (발 높이 · 휙 도는 것 · 카메라 떨림 · 멈춤) + GIF ──
        await A.evaluate("()=>{ const d=ISLE.doorCell(); TFAC.warp(d[0]+.5,d[1]+.5); }"); await A.wait_for_timeout(600)
        await A.evaluate("""()=>{ window._mo=[]; const f=ISLE.SLOTS()[0]; const t0=performance.now(); walkTo(f.door[0], f.door[1]); const h=HOUSE.hero();
            (function s(){ const p=h.g.position, c=camera.position; window._mo.push([performance.now()-t0, p.x, p.y, p.z, h.g.rotation.y, h.moving?1:0, c.x, c.y, c.z, (h.path||[]).length]); if(performance.now()-t0<60000 && (h.moving || (h.path||[]).length)) requestAnimationFrame(s); else window._moDone=1; })(); }""")
        frames=[]
        for i in range(80):
            await A.wait_for_timeout(700)
            if i%2==0:
                fp=D+f"walk_{i:02d}.png"; await A.screenshot(path=fp, timeout=60000); frames.append(fp)
            if await A.evaluate("()=>!!window._moDone"): break
        mo=await A.evaluate("()=>window._mo")
        ys=[m[2] for m in mo]; stuck=0; last=None; st_t=0; turns=0; camj=0
        for k in range(1,len(mo)):
            dt=(mo[k][0]-mo[k-1][0])/1000 or 1e-3; d=math.hypot(mo[k][1]-mo[k-1][1], mo[k][3]-mo[k-1][3])
            if mo[k][5] and d<1e-4: st_t+=dt
            else: st_t=0
            stuck=max(stuck,st_t)
            dr=abs(((mo[k][4]-mo[k-1][4]+math.pi)%(2*math.pi))-math.pi)
            if dr>1.2 and dt<0.12: turns+=1
            if k>1:
                a=[mo[k][j]-2*mo[k-1][j]+mo[k-2][j] for j in (6,7,8)]
                if math.sqrt(sum(x*x for x in a))>0.6: camj+=1
        walk_s=mo[-1][0]/1000 if mo else 0; fps=len(mo)/max(.1,walk_s)
        ok(max(abs(y) for y in ys)<0.05 if ys else False, f"⑨ 걷는 동안 발이 땅에 (높이 최대 {max(abs(y) for y in ys):.3f})" if ys else "⑨ 기록 없음")
        ok(stuck<1.5, f"⑨ 걷다가 멈춤 최대 {stuck:.2f}초")
        ok(turns<=2, f"⑨ 한 번에 휙 도는 것 {turns}번")
        ok(camj<=3, f"⑨ 카메라 튐 {camj}번 ({len(mo)}프레임)")
        RES["walkHomeField"]={"fps":round(fps,1), "sec":round(walk_s,1), "frames":len(mo), "stuck":round(stuck,2), "turns":turns, "camJ":camj}
        print("   집 → 밭 실제로 걸은 시간", round(walk_s,1), "초")
        try:
            from PIL import Image
            ims=[Image.open(f).convert("RGB").resize((410,590)) for f in frames]
            if ims: ims[0].save(D+"walk.gif", save_all=True, append_images=ims[1:], duration=350, loop=0)
        except Exception as e: print("gif", e)
        # ── ⑤ 속도 · ⑧ 그래픽 (구역마다) ──
        SP=[("plaza",0,5,3.14),("downtown",12,-26.6,1.57),("downtown2",24,-12,3.14),("farm",-104,4,1.57),("fun",96,4,-1.57),("bridgeE",76,4,-1.57),("home",-40,14,1.57),("lake",74,-66,-2.2),("vil",-70,58,2.2),("mine",0,-70,3.14)]
        perf={}
        for k,x,z,ya in SP:
            await A.evaluate(WARP, [x,z,ya,1.5,.62]); await A.wait_for_timeout(1300)
            r=await A.evaluate("()=>{ renderer.info.autoReset=true; const t0=performance.now(); for(let i=0;i<3;i++) TOON.draw(); const ms=(performance.now()-t0)/3; return {calls:renderer.info.render.calls, tris:renderer.info.render.triangles, ms:Math.round(ms)}; }")
            perf[k]=r; fp=D+f"pad_{k}.png"; await A.screenshot(path=fp, timeout=60000)
            try:
                from PIL import Image
                im=Image.open(fp).convert("RGB"); w,h=im.size; px=im.crop((0,int(h*.2),w,int(h*.75))).resize((200,110)).load(); blk=mag=0
                for a in range(200):
                    for b in range(110):
                        c=px[a,b]
                        if max(c)<14: blk+=1
                        if c[0]>200 and c[1]<70 and c[2]>200: mag+=1
                perf[k]["black%"]=round(blk/220,2); perf[k]["magenta%"]=round(mag/220,2)
            except Exception as e: print(e)
        RES["perf"]=perf; print("   ", json.dumps(perf, ensure_ascii=False))
        ok(all(v["calls"]<260 for k,v in perf.items() if k!="vil"), f"⑤ 그리기 횟수 260 아래 {[(k,v['calls']) for k,v in perf.items()]}")
        ok(perf["vil"]["calls"]<330, f"⑤ 🍄 버섯 마을 {perf['vil']['calls']} (마을 사람 4명 몸 조각 — 330 아래)")
        ok(all(v.get("black%",0)<2 and v.get("magenta%",0)<.5 for v in perf.values()), "⑧ 새까만·분홍 덩어리 없음 (그림 파일 빠짐)")
        # 물건 뜸·묻힘·물 위·길 위·겹침
        r=await A.evaluate("""()=>{ const OX=ISLE.OX, OZ=ISLE.OZ, out={float:[], sunk:[], water:[], onRoad:[], overlap:[], treeRoad:0, treeWater:0}; const B=[];
          ISLE.G.children.forEach(o=>{ if(!o.userData.solo) return; const b=new THREE.Box3().setFromObject(o); if(!isFinite(b.min.y)) return; const cx=(b.min.x+b.max.x)/2, cz=(b.min.z+b.max.z)/2, nm=o.userData.city||o.userData.shopK||o.userData.fac||(o.userData.lot&&o.userData.lot.id)||'obj';
            if(b.min.y>.35) out.float.push([nm, +b.min.y.toFixed(2), Math.round(cx-OX), Math.round(cz-OZ)]); if(b.max.y<.3) out.sunk.push([nm, Math.round(cx-OX), Math.round(cz-OZ)]);
            if(!ISLE.inIsle(cx,cz)) out.water.push([nm, Math.round(cx-OX), Math.round(cz-OZ)]);
            if(o.userData.city==null && ISLE.onPave(cx,cz) && !o.userData.lot) out.onRoad.push([nm, Math.round(cx-OX), Math.round(cz-OZ)]); B.push([nm,b,o]); });
          for(let i=0;i<B.length;i++) for(let j=i+1;j<B.length;j++){ const a=B[i][1], b=B[j][1]; const ox=Math.min(a.max.x,b.max.x)-Math.max(a.min.x,b.min.x), oz=Math.min(a.max.z,b.max.z)-Math.max(a.min.z,b.min.z); if(ox>.6 && oz>.6 && !(B[i][0]===B[j][0] && typeof B[i][0]==='string' && B[i][0].length===1)) out.overlap.push([B[i][0],B[j][0],+ox.toFixed(1),+oz.toFixed(1)]); }
          ISLE.trees().forEach(([x,z])=>{ if(ISLE.onPave(x+OX,z+OZ)) out.treeRoad++; if(ISLE.waterCell(Math.floor(x+OX),Math.floor(z+OZ))) out.treeWater++; });
          out.n=B.length; return out; }""")
        RES["objects"]=r
        ok(not r['float'], f"⑧ 공중에 뜬 건물 {r['float'][:6]}")
        ok(not r['sunk'], f"⑧ 땅에 묻힌 건물 {r['sunk'][:6]}")
        ok(not r['water'], f"⑧ 물 위 건물 {r['water'][:6]}")
        ok(not r['onRoad'], f"⑧ 길 위에 놓인 건물 {r['onRoad'][:6]}")
        ok(len(r['overlap'])==0, f"⑧ 건물끼리 겹침 {len(r['overlap'])} {r['overlap'][:6]}")
        ok(r['treeRoad']==0 and r['treeWater']==0, f"⑧ 길·물 위 나무 {r['treeRoad']} / {r['treeWater']}")
        # ── ④ 화면 (폰) — 이름표 겹침 · 지도 · 땅 고르기 ──
        P=await kid(br, "QAPH3", "서아", (390,844))
        lab={}
        for k,x,z,ya in [("plaza",0,5,3.14),("downtown",3,-18,3.14),("farm",-100,4,1.57),("fun",100,4,-1.57)]:
            await P.evaluate(WARP, [x,z,ya,1.5,.62]); await P.wait_for_timeout(1500)
            r=await P.evaluate("""()=>{ const L=[...document.querySelectorAll('#tls .tl')].filter(e=>getComputedStyle(e).display!=='none' && e.offsetParent).map(e=>e.getBoundingClientRect()); let n=0; for(let i=0;i<L.length;i++) for(let j=i+1;j<L.length;j++){ const a=L[i], b=L[j], ox=Math.min(a.right,b.right)-Math.max(a.left,b.left), oy=Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top); if(ox>6 && oy>6) n++; } return {shown:L.length, overlap:n}; }""")
            lab[k]=r; await P.screenshot(path=D+f"phone_{k}.png", timeout=60000)
        RES["labels"]=lab; ok(all(v['overlap']<=1 for v in lab.values()), f"④ 폰 이름표 겹침 {lab}")
        await P.evaluate("()=>IHUD.openMap()"); await P.wait_for_timeout(800); await P.screenshot(path=D+"phone_map.png", timeout=60000)
        r=await P.evaluate("()=>({zones:document.querySelectorAll('#ihMap [data-z]').length, isles:document.querySelectorAll('#ihMap polygon,#ihMap path').length})"); ok(r['zones']>=10, f"④ 지도 구역 {r}")
        await P.evaluate("()=>{ document.getElementById('ihMap').classList.remove('on'); }")
        await P.evaluate("()=>ISLE.openLots()"); await P.wait_for_timeout(900); await P.screenshot(path=D+"phone_lots.png", timeout=60000)
        r=await P.evaluate("()=>({hoods:document.querySelectorAll('#lotP [data-hood], #lotP .lhTab, #lotP button').length})"); RES["lotP"]=r
        await A.evaluate("()=>IHUD.openMap()"); await A.wait_for_timeout(800); await A.screenshot(path=D+"pad_map.png", timeout=60000)
        # ── ⑨ 모션: 마을 사람·물고기 그림자 (물 위·벽 안) ──
        r=await A.evaluate("()=>{ const out=[]; try{ (VIL.NPC||[]).forEach(n=>{ const g=n.g||n.obj; if(!g) return; const p=g.position; out.push([n.k||n.id||n.nm, Math.round(p.x-ISLE.OX), Math.round(p.z-ISLE.OZ), ISLE.blocked(Math.floor(p.x),Math.floor(p.z))?1:0]); }); }catch(e){} return out; }")
        RES["npc"]=r; ok(all(x[3]==0 for x in r) if r else True, f"⑨ 마을 사람 서 있는 자리 {r}")
        await br.close()
    real=[e for e in real_errs(errs) if "404" not in e]
    ok(not real, f"⑧ 오류 없음 {real[:3]}")
    RES["bad"]=bad; json.dump(RES, open(D+"qa.json","w"), ensure_ascii=False, indent=1)
    print("\nFAIL" if bad else "\nPASS", len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
