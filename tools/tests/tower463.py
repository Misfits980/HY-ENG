"""(v463) 🎪 폴가이즈 같은 장애물 — 사용자: "폴가이즈에 있는 장애물도 넣어 보는 거 어때?"
  🚪 문 부수기: 가짜 문은 몸으로 밀면 와장창 · 진짜 문은 막힘 · 너무 높아 못 넘음 (쉬움 줄 2·가짜 2 / 어려움 줄 3·가짜 1)
  🦶 진짜 발판 찾기: 가짜 칸에 올라가면 사라짐 → 🕸 그물 → 이 층 처음 발판 (사라진 칸은 그대로 = 길이 보임)
  🔨 흔들 공: 공이 길을 가로질러 흔들림 · 맞으면 옆으로 퉁 · 공이 멀 때는 그냥 지나감
  · 쉬움 30층 1~9층에도 🚪 · 🤖 가 세 가지 모두 통과 (tower459·462 의 🤖 가 확인)"""
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
        r = await E("""()=>{ const T=HOUSE.TW, c={sky:{}, kid:{}}; for(const m of ['sky','kid']) for(let d=1; d<=12; d++){ T.seed='2027-03-'+d; HOUSE.twBuild(m); T.secs.forEach((k,i)=>{ if(['door','tiptoe','pend','sweep','sweep3'].includes(k)) c[m][k+(m==='kid'&&i<9?'<10':'')]=(c[m][k+(m==='kid'&&i<9?'<10':'')]||0)+1; }); } return c; }""")
        ok(all(r["sky"].get(k, 0) > 0 for k in ["door", "tiptoe", "pend", "sweep", "sweep3"]) and r["kid"].get("door<10", 0) > 0 and not r["kid"].get("tiptoe<10") and not r["kid"].get("pend<10") and not r["kid"].get("sweep<10") and not r["kid"].get("sweep3<10"), f"🗼 도전·🟢 쉬움에 새 장애물 · 쉬움 1~9층엔 🚪 만 {r}")
        # 🚪
        r = await E("""()=>{ const T=HOUSE.TW; for(let d=1; d<80; d++){ T.seed='2027-04-'+d; HOUSE.twBuild('sky'); if(T.secs.indexOf('door')>=10) break; } const i=T.secs.indexOf('door'); T.mode='sky'; T.bot=true; T.on=true; T.fin=false;
            const D=T.S.slice(T.secR[i][0],T.secR[i][1]).filter(s=>s.kind==='door'), rows=new Set(D.map(s=>s.row)).size, fk=D.filter(s=>s.fake).length, h=+(D[0].max.y-D[0].min.y).toFixed(2), F=T.S.slice(T.secR[i][0],T.secR[i][1])[0];
            const go=(s)=>{ const cx=(s.min.x+s.max.x)/2, cz=(s.min.z+s.max.z)/2, d=HOUSE.TDIR[i%4]; T.p.set(cx-d[0]*0.9, s.min.y+0.001, cz-d[1]*0.9); T.v.set(0,0,0); T.onG=true; T.yaw=Math.atan2(-d[0],-d[1]); T.inp.x=0; T.inp.y=1; for(let n=0;n<90;n++) HOUSE.twStep(1/90); T.inp.y=0; const al=(T.p.x-cx)*d[0]+(T.p.z-cz)*d[1]; return [s.on, +al.toFixed(2)]; };
            const real=D.find(s=>!s.fake && s.row===0), fake=D.find(s=>s.fake && s.row===0); const a=go(real), b=go(fake); T.bot=false; return [rows, fk, h, a, b]; }""")
        ok(r[0] == 3 and r[1] == 3 and r[2] >= 2.0 and r[3][0] and r[3][1] < -0.2 and not r[4][0] and r[4][1] > 0.3, f"🚪 어려움: 줄 3 · 가짜 3(줄마다 1) · 높이 2.2 · 진짜 문 = 막힘 · 가짜 문 = 와장창 지나감 {r}")
        # 🦶
        r = await E("""()=>{ const T=HOUSE.TW; for(let d=1; d<80; d++){ T.seed='2027-05-'+d; HOUSE.twBuild('sky'); if(T.secs.includes('tiptoe')) break; } const i=T.secs.indexOf('tiptoe'); T.bot=false; T.on=true; T.fin=false; T.cp=i;
            const S=T.S.slice(T.secR[i][0],T.secR[i][1]), f=S.find(s=>s.fake), net=S.find(s=>s.net!=null); T.p.set((f.min.x+f.max.x)/2, f.max.y+0.3, (f.min.z+f.max.z)/2); T.v.set(0,0,0); T.onG=false; T.lastGY=null; const f0=T.fall;
            let n=0; while(n<400){ HOUSE.twStep(1/90); n++; if(T.fall>f0) break; } const c=T.cps[i]; return [f.on, T.fall-f0, +(T.p.y-c.max.y).toFixed(2), document.getElementById('toast').innerText, net.net===i]; }""")
        ok(r[0] is False and r[1] == 1 and abs(r[2]) < 0.05 and "그물" in r[3] and r[4], f"🦶 가짜 칸 → 사라짐 → 🕸 그물 → 이 층 처음 발판 {r}")
        # 🔨
        r = await E("""()=>{ const T=HOUSE.TW; for(let d=1; d<80; d++){ T.seed='2027-06-'+d; HOUSE.twBuild('sky'); if(T.secs.indexOf('pend')>=10) break; } const i=T.secs.indexOf('pend'); T.bot=true; T.on=true; T.fin=false; T.clk=0;
            const P=T.S.find(s=>s.kind==='pend' && s.F.i===i); HOUSE.twStep(1/90); let hit=null, far=null;
            for(let n=0;n<900 && !hit;n++){ const tt=T.clk; const th=P.amp*Math.sin((tt+1/90)*P.sp+P.ph); if(Math.abs(th)<0.05){ const c=P.G.position; T.p.set(c.x, P.py-3.4+0.001, c.z); T.v.set(0,0,0); T.onG=true; const v0=T.v.clone(); HOUSE.twStep(1/90); hit=[+Math.hypot(T.v.x,T.v.z).toFixed(1), +T.v.y.toFixed(1), T.kick>0]; } else HOUSE.twStep(1/90); }
            for(let n=0;n<900 && !far;n++){ const tt=T.clk; const th=P.amp*Math.sin((tt+1/90)*P.sp+P.ph); if(Math.abs(Math.sin(th))*P.L>1.6){ const c=P.G.position; T.p.set(c.x, P.py-3.4+0.001, c.z); T.v.set(0,0,0); T.onG=true; T.kick=0; HOUSE.twStep(1/90); far=[+Math.hypot(T.v.x,T.v.z).toFixed(1), T.kick>0]; } else HOUSE.twStep(1/90); }
            T.bot=false; return [hit, far]; }""")
        ok(r[0] and r[0][0] > 3 and r[0][1] > 3 and r[0][2] and r[1] and r[1][0] < 1 and not r[1][1], f"🔨 공이 가운데 = 퉁! (옆으로·위로) · 공이 멀리 = 안 맞음 {r}")
        # (v464) 🕐 시계 막대
        r = await E("""()=>{ const T=HOUSE.TW; for(let d=1; d<80; d++){ T.seed='2027-07-'+d; HOUSE.twBuild('kid'); if(T.secs.indexOf('sweep')>=10) break; } const i=T.secs.indexOf('sweep'); T.bot=true; T.on=true; T.fin=false; T.clk=0; HOUSE.twStep(1/90);
            const S=T.S.find(s=>s.kind==='sweep' && Math.abs(s.y0-(T.ys[i]+0.2))<0.01), y=T.ys[i]; const at=(r,ang)=>{ T.p.set(S.c[0]+Math.cos(ang)*r, y+0.001, S.c[1]+Math.sin(ang)*r); T.v.set(0,0,0); T.onG=true; T.kick=0; };
            let a=-S.mesh.rotation.y; at(1.0, a+0.02*Math.sign(S.sp)*-1); S.hitT=0; HOUSE.twStep(1/90); const hit=[+Math.hypot(T.v.x,T.v.z).toFixed(1), +T.v.y.toFixed(1)];
            a=-S.mesh.rotation.y; at(0.05, a); S.hitT=0; HOUSE.twStep(1/90); const hub=+Math.hypot(T.v.x,T.v.z).toFixed(1);
            a=-S.mesh.rotation.y; at(1.0, a+Math.PI*0.9); S.hitT=0; HOUSE.twStep(1/90); const far=+Math.hypot(T.v.x,T.v.z).toFixed(1); T.bot=false; return [T.secs[i], hit, hub, far, S.len2]; }""")
        ok(r[0] == "sweep" and r[1][0] > 3 and r[1][1] > 3 and r[2] < 0.5 and r[3] < 0.5 and r[4] == 0, f"🕐 바늘에 닿으면 퉁 (죽지 않음) · 가운데 기둥 위 = 안전 · 바늘 반대쪽 = 안 맞음 · 쉬움 = 바늘 1개 {r}")
        # (v465) 🕐🕐🕐 세 바늘
        r = await E("""()=>{ const T=HOUSE.TW; for(let d=1; d<80; d++){ T.seed='2027-08-'+d; HOUSE.twBuild('sky'); if(T.secs.includes('sweep3')) break; } const i=T.secs.indexOf('sweep3'); T.bot=true; T.clk=0; HOUSE.twStep(1/90);
            const y=T.ys[i], SW=T.S.filter(s=>s.kind==='sweep' && Math.abs(s.y0-(y+0.2))<0.01), d=HOUSE.TDIR[i%4], aD=Math.atan2(d[1],d[0]), out=[];
            for(let n=0;n<5;n++){ for(let k=0;k<37;k++) HOUSE.twStep(1/90); const aB=-SW[1].mesh.rotation.y, aC=-SW[2].mesh.rotation.y, m=((aB+aC-2*aD)%(Math.PI*2)+Math.PI*3)%(Math.PI*2)-Math.PI; out.push(+Math.abs(m).toFixed(3)); }
            const c=SW.map(s=>s.c), tri=[Math.hypot(c[0][0]-c[1][0],c[0][1]-c[1][1]), Math.hypot(c[1][0]-c[2][0],c[1][1]-c[2][1]), Math.hypot(c[0][0]-c[2][0],c[0][1]-c[2][1])].map(v=>+v.toFixed(2));
            T.bot=false; return [SW.length, out, tri, Math.sign(SW[0].sp)!==Math.sign(SW[1].sp)]; }""")
        ok(r[0] == 3 and max(r[1]) < 0.01 and abs(r[2][0] - r[2][2]) < 0.01 and r[3], f"🕐🕐🕐 바늘 3개 · 삼각형(앞 1·뒤 2) · 뒤 두 바늘은 거울처럼 · 앞과 뒤는 반대로 {r}")
        # (v466) 둥근 시계판만 · 🗼 도전 층 길이 들쭉날쭉
        r = await E("""()=>{ const T=HOUSE.TW; for(let d=1; d<80; d++){ T.seed='2027-08-'+d; HOUSE.twBuild('sky'); if(T.secs.includes('sweep3')||T.secsB.includes('sweep3')) break; } const i=T.secs.indexOf('sweep3')>=0?T.secs.indexOf('sweep3'):T.secsB.indexOf('sweep3'); T.bot=true;
            const R=T.S.slice(T.secR[i][0],T.secR[i][1]).filter(s=>s.rnd && s.seg && s.seg.kind==='sweep3'), A=R[0], c=[A.rnd[0],A.rnd[1]], r=A.rnd[2], d=A.seg.d, n=[-d[1],d[0]]; const y=A.max.y;
            const drop=(k)=>{ T.S.forEach(s=>{ if(s.kind==='sweep') s.hitT=99; }); T.p.set(c[0]+n[0]*r*k*0.7071-d[0]*r*k*0.7071, y+0.3, c[1]+n[1]*r*k*0.7071-d[1]*r*k*0.7071); T.v.set(0,0,0); T.onG=false; for(let q=0;q<40;q++) HOUSE.twStep(1/90); return +(T.p.y-y).toFixed(2); };
            const inn=drop(0.8), out=drop(1.25); const sq=T.S.slice(T.secR[i][0],T.secR[i][1]).filter(s=>s.kind==='solid' && !s.rnd && !s.noWalk && !s.conn && s.seg===A.seg).map(s=>+((s.max.x-s.min.x)*(s.max.z-s.min.z)).toFixed(1));
            const fl=[], rise=[]; for(let dd=1; dd<=8; dd++){ T.seed='2027-10-'+dd; HOUSE.twBuild('sky'); fl.push(T.secsB.filter(Boolean).length); for(let j=11;j<T.ys.length;j++) rise.push(+(T.ys[j]-T.ys[j-1]).toFixed(1)); }
            T.bot=false; return [R.length, inn, out, sq, fl, Math.min(...rise), Math.max(...rise)]; }""")
        ok(r[0] == 3 and abs(r[1]) < 0.05 and r[2] < -0.5 and max(r[3]) < 4.5, f"🕐🕐🕐 둥근 판 3개만 (네모 판 없음) · 판 안 = 서 있음 · 둥근 판 밖(네모였으면 서 있던 곳) = 떨어짐 {r[:4]}")
        ok(all(x == 28 for x in r[4]) and r[6] > 4.0, f"(v471) 🗼 도전 11층부터 한 층 = 장애물 2개 (타워마다 {r[4]}층) · 층 높이 {r[5]}~{r[6]}")
        # (v468) 🎨 장애물마다 다른 무늬 · 층 시작 표지판 · 진짜/가짜 칸은 똑같이
        r = await E("""()=>{ const T=HOUSE.TW; T.seed='2027-11-1'; HOUSE.twBuild('sky'); const pat={}; T.secs.forEach((k,i)=>{ const L=T.S.slice(T.secR[i][0],T.secR[i][1]); const ds=L.filter(s=>s.decal).map(s=>s.decal.material.map.image); pat[k]=pat[k]||new Set(); ds.forEach(im=>pat[k].add(im)); });
            const kinds=['steps','gaps','lava','beam','ice','crumble','fade','mover','laser','tiptoe','pend'].filter(k=>pat[k]), first={}; kinds.forEach(k=>first[k]=[...pat[k]][0]);
            const uniq=new Set(kinds.map(k=>first[k])).size; const i=T.secs.indexOf('tiptoe'), L=T.S.slice(T.secR[i][0],T.secR[i][1]); const real=L.filter(s=>s.decal && !s.fake), fake=L.filter(s=>s.decal && s.fake);
            return [kinds.length, uniq, real.length>0 && fake.length>0 && real[0].decal.material.map.image===fake[0].decal.material.map.image]; }""")
        ok(r[0] >= 8 and r[1] >= r[0] - 1 and r[2], f"🎨 장애물마다 다른 윗면 무늬 ({r[0]}종 · 무늬 {r[1]}개) · 🦶 진짜·가짜 칸 무늬 같음 {r}")
        # (v469) 🧗 벽 점프 = 🗼 도전 38층에만 · 쉽게 (가까이 가면 붙음 · 한 번 차면 올라감 · JUMP 반짝)
        r = await E("""()=>{ const T=HOUSE.TW, w=[]; for(let d=1; d<=12; d++){ T.seed='2027-12-'+d; HOUSE.twBuild('sky'); w.push(T.secs.map((k,i)=>k==='wall'?i:-1).filter(i=>i>=0).join()); }
            const i=37, S=T.S.slice(T.secR[i][0],T.secR[i][1]), B=S.find(s=>s.wallTop), y=T.ys[i], d=B.seg.d; T.bot=false; T.mode='sky'; T.on=true; T.fin=false; T.cp=i; T.kick=0;
            const bc=[(B.min.x+B.max.x)/2,(B.min.z+B.max.z)/2], al=(bc[0]-0)*0, toB=[d[0],d[1]];
            const st=S.find(s=>s.kind==='solid'); const sx=(st.min.x+st.max.x)/2, sz=(st.min.z+st.max.z)/2; const face=(B.min.x+B.max.x)/2-d[0]*((B.max.x-B.min.x)/2) , facez=(B.min.z+B.max.z)/2-d[1]*((B.max.z-B.min.z)/2);
            T.p.set(face-d[0]*0.45 + (d[0]?0:sx-face), y+0.001, facez-d[1]*0.45 + (d[1]?0:sz-facez)); T.v.set(0,0,0); T.onG=true; T.yaw=Math.atan2(-d[0],-d[1]);
            const sv=(ix,iy)=>{ T.inp.x=ix; T.inp.y=iy; }; sv(0,1); T.buf=0.16; let stuck=false, glow=false, top=false, jumps=0;
            for(let n=0;n<500 && !top;n++){ HOUSE.twStep(1/90); HOUSE.twTick(0); if(T.wallT>0 && !T.onG && !stuck){ stuck=true; glow=document.getElementById('twJump').classList.contains('glow'); sv(0,0); }
              if(stuck && jumps===0 && T.wallT>0){ T.buf=0.16; jumps=1; } if(jumps===1 && T.kick<=0 && T.v.y<3) sv(0,1); if(T.onG && T.gnd===B) top=true; }
            sv(0,0); return [w, stuck, glow, jumps, top, +(B.max.y-y).toFixed(2)]; }""")
        ok(all(x == "37" for x in r[0]) and r[1] and r[2] and r[3] == 1 and r[4] and r[5] < 2.5, f"🧗 벽 점프 = 38층에만 (12일) · 큰 벽 쪽으로 밀며 점프 → 붙음 · JUMP 반짝 · 한 번 차고 다시 벽 쪽 → 꼭대기 {r[1:]} {r[0][:4]}")
        ok(not real_errs(errs), "오류 없음 " + str(real_errs(errs)[:3]))
        await br.close()
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)
asyncio.run(main())
