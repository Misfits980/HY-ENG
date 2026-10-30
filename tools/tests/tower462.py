"""(v462) 🟢 쉬움 30층 — 사용자: "쉬움 버전도 30층까지 잘 만들어 줘 · 유치부 애들이 어려움 도전하기 전에 할 수 있게"
  ① 고르기 창 = 🟢 쉬움 30층 + 🗼 도전 40층 · 쉬움 → 1 / 30층
  ② 1~9 = 아주 쉬운 것만(🔥 용암·🔴 레이저·🟥 킬브릭·🧊 얼음·🍂 무너짐 없음) · 10·20 = 🏝 땅 · 11~30 = 쉬움 · 어려움 장애물 없음 · 사다리 낮음
  ③ 용암 → 아래 🏝 땅 · 친구 보기 경로 따로(k) · 꼭대기 💎 12 · 친구 기록 🟢
  ④ 🤖 자동 선수가 30층 꼭대기까지 (6일)"""
import asyncio, sys, os, json
os.environ["HY_REAL3D"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright
BOT = r"""(opt)=>{ const H=HOUSE, T=H.TW, X=H.THX; T.bot=true; T.seed=opt.seed; T.clk=0; H.twBuild(opt.mode); T.on=true; T.fin=false; T.cp=0; T.dead=0; T.t0=performance.now(); H.twRespawn(true); T.yaw=0;
  const walk=s=>(s.on || s.kind==="fade") && ["solid","cp","top","bounce","conv","fade","glass","ice","wall"].includes(s.kind) && !s.noWalk && !(s.kind==="glass" && !s.ok);
  const wps=i=>T.S.slice(T.secR[i][0], T.secR[i][1]).filter(walk).concat([T.cps[i+1]]);
  const gap=(s,p)=>{ const dx=Math.max(s.min.x-(p.x+X), (p.x-X)-s.max.x, 0), dz=Math.max(s.min.z-(p.z+X), (p.z-X)-s.max.z, 0); return Math.hypot(dx,dz); };
  const inXZ=(s,x,z)=>x>s.min.x && x<s.max.x && z>s.min.z && z<s.max.z;
  let k=0, sec=-1, dead=T.dead, fallN=T.fall, t=0, log=[], stuck=0, lastCp=0, secT=0; const dt=1/90;
  while(t<opt.max && !T.fin){ t+=dt; secT+=dt;
    if(T.onG && T.gnd && T.gnd.ground!=null && T.cp>T.gnd.ground) T.cp=T.gnd.ground;
    if(T.onG && T.gnd && T.gnd.kind==="floor" && k>0) k=0;   // (v465) 맨 아래 바닥에 떨어지면 첫 발판부터   // (v463) 🏝 땅에 떨어지면 거기서 다시 올라감
    if(T.cp!==sec || T.dead!==dead || T.fall!==fallN){ if(T.cp!==sec){ log.push([sec, +secT.toFixed(1), T.dead]); secT=0; } sec=T.cp; dead=T.dead; fallN=T.fall; k=0; }
    if(sec>=T.cps.length-1) break;
    const W=wps(sec), p=T.p; for(let j=W.length-1;j>=0;j--){ if(T.onG && T.gnd===W[j]){ k=Math.max(k,j+1); break; } }
    if(W[k] && W[k].kind==="bounce" && T.v.y>8 && inXZ(W[k],p.x,p.z)) k++;
    if(k>=W.length) k=W.length-1; let tg=W[k]; while(!tg.on && k<W.length-1){ k++; tg=W[k]; }
    const m=Math.min(0.45,(tg.max.x-tg.min.x)/2-0.02), n=Math.min(0.45,(tg.max.z-tg.min.z)/2-0.02);
    const cx=Math.max(tg.min.x+m,Math.min(tg.max.x-m,p.x)), cz=Math.max(tg.min.z+n,Math.min(tg.max.z-n,p.z));
    let dx=cx-p.x, dz=cz-p.z; const L=Math.hypot(dx,dz); if(L>0.05){ dx/=L; dz/=L; } else { dx=dz=0; } if(L<=0.05 && T.onG && k<W.length-1) k++;   // (v467) 겹친 발판 위 = 이미 도착
    if(T.onG && T.gnd && T.gnd.push && (dx||dz)){ dx=dx*4.4-T.gnd.push[0]; dz=dz*4.4-T.gnd.push[1]; const q=Math.hypot(dx,dz); dx/=q; dz/=q; }
    const g=T.gnd, gp=gap(tg,p), rise=tg.max.y-(g?g.max.y:p.y);
    if(T.onG && g && g!==tg){
      const nx=p.x+dx*0.35, nz=p.z+dz*0.35, leaving=!inXZ(g,nx,nz);
      const R=tg.move?1.1:2.0; if(tg.climb){ if(leaving && gp>0.12) T.buf=0.16; } else if(leaving && (gp>R || rise>1.45) && !g.crumble){ dx=dz=0; }   // (v463) 🍂 무너지는 발판 위에서는 기다리지 않음   // 기다림 (움직이는 발판)
      else if(leaving && gp<0.12 && Math.abs(rise)<0.12){ }   // (v466) 바로 붙은 발판은 걸어서
      else if(!tg.climb && (leaving || rise>(tg.crumble?0.25:0.06)) && gp<R && rise<1.5 && (leaving || gp<1.1)) T.buf=0.16;
    }
    for(const s of T.S){ if(s.kind==="spin" && T.onG && Math.abs(p.y-s.y0)<1.2){ const qx=p.x-s.c[0], qz=p.z-s.c[1], rr=Math.hypot(qx,qz); if(rr<s.len+0.5){   // (v454) 막대가 올 때를 계산해서 점프 (빨라진 막대)
    for(const s of T.S){ if(s.kind==="sweep" && T.onG && Math.abs(p.y-s.y0)<1.0){ const qx=p.x-s.c[0], qz=p.z-s.c[1], rr=Math.hypot(qx,qz); if(rr<s.len+0.6){   // (v464) 🕐 바늘이 올 때 점프
        const a=-s.mesh.rotation.y, ph=Math.atan2(qz,qx), M=s.len2>0?Math.PI:Math.PI*2, d=s.sp>0?(((a-ph)%M)+M)%M:(((ph-a)%M)+M)%M, tt=d/Math.abs(s.sp); if(tt>0.12 && tt<0.3) T.buf=0.16; } } }
        const a=-s.mesh.rotation.y, ph=Math.atan2(qz,qx), d=(((a-ph)%Math.PI)+Math.PI)%Math.PI, tt=d/s.sp; if((tt>0.2 && tt<0.36) || rr<0.9) T.buf=0.16; } } }   // (v466) 가운데(막대 뿌리)는 콩콩 뛰어서
    for(const s of T.S){ if(s.kind==="laser" && T.onG && Math.abs(p.y-s.y0)<0.5 && gap(s,p)<0.55) T.buf=0.16; }   // (v454) 🔴 레이저 = 점프로 넘기
    if(T.secs[sec]==="wall"){ const B=T.S.slice(T.secR[sec][0],T.secR[sec][1]).find(s=>s.wallTop);   // (v454) 🧗 벽 점프: B 쪽으로 → 벽에 닿으면 반대쪽으로 JUMP
      if(T.onG && T.gnd && T.gnd.kind==="cp" && T.gnd.i===sec) T.buf=0;
      if(T.onG && T.gnd && T.gnd.wallTop) T.buf=0;   // (v466) 벽 위에 올라서면 멈춰서 다음 발판으로 걸어감   // 처음 발판 → 길은 이어져 있으니 걸어감 (점프하면 A 벽에 부딪힘)
      if(B && !(T.onG && (T.gnd===B || T.gnd.kind==="cp" || T.gnd.kind==="top"))){
        if(!T.onG && T.wallT>0 && T.wallN){ dx=T.wallN[0]; dz=T.wallN[1]; T.buf=0.16; }
        else if(T.onG){ const ex=(B.min.x+B.max.x)/2-p.x, ez=(B.min.z+B.max.z)/2-p.z, q=Math.hypot(ex,ez)||1; dx=ex/q; dz=ez/q; T.buf = gap(B,p)<0.3 ? 0.16 : 0; }
        else if(T._wd){ dx=T._wd[0]; dz=T._wd[1]; }
        T._wd=[dx,dz]; } }
    if(T.onG && T.gnd && T.gnd.ground!=null && (dx||dz)){ const C=6, ax=p.x-C, az=p.z-C, bx=cx-C, bz=cz-C; let hit=false; for(let q=0;q<=20;q++){ const x=ax+(bx-ax)*q/20, z=az+(bz-az)*q/20; if(Math.abs(x)<2.75 && Math.abs(z)<2.75) hit=true; }   // (v463) 🏝 땅 위: 가운데 기둥을 돌아서
      if(hit){ const a1=Math.atan2(az,ax), a2=Math.atan2(bz,bx); let da=((a2-a1+Math.PI*3)%(Math.PI*2))-Math.PI; const sg=da>=0?1:-1, r=Math.hypot(ax,az), tx=-az*sg/r, tz=ax*sg/r, out=(r<3.6?0.5:0); dx=tx+ax/r*out; dz=tz+az/r*out; const q=Math.hypot(dx,dz); dx/=q; dz/=q; } }
    if((T.secs[sec]==="sweep" || (T.secsB&&T.secsB[sec]==="sweep")) && T.onG && T.gnd && T.gnd.kind!=="floor"){ const S0=T.S.slice(T.secR[sec][0],T.secR[sec][1]), sw0=S0.find(s=>s.kind==="sweep" && (!s.seg || !s.seg.kind || s.seg.kind==="sweep")), S=sw0 ? S0.filter(s=>s.seg===sw0.seg && !s.conn) : [], SL=S.filter(s=>s.kind==="solid" && !s.noWalk), sw=(sw0 && (!sw0.seg || !T.gnd.seg || T.gnd.seg===sw0.seg)) ? sw0 : null;   // (v464) 🕐 입구 → (바늘이 멀 때) 가운데 → (바늘이 멀 때) 출구
      if(sw && Math.abs(p.y-sw.y0)<1.0){ const C=sw.c, rC=Math.hypot(p.x-C[0],p.z-C[1]), arr=ph=>{ const a=-sw.mesh.rotation.y, M=sw.len2>0?Math.PI:Math.PI*2, d=sw.sp>0?(((a-ph)%M)+M)%M:(((ph-a)%M)+M)%M; return d/Math.abs(sw.sp); }, ok=ph=>{ const M=(sw.len2>0?Math.PI:Math.PI*2)/Math.abs(sw.sp), t0=arr(ph); return t0>0.5 && M-t0>0.3; };
        const ex=SL[2], exC=[(ex.min.x+ex.max.x)/2,(ex.min.z+ex.max.z)/2], exAng=Math.atan2(exC[1]-C[1],exC[0]-C[0]), toEx=((p.x-C[0])*(exC[0]-C[0])+(p.z-C[1])*(exC[1]-C[1]))>0;
        let goal=null, safe=true;
        if(T.gnd===SL[0]){ goal=C; safe=ok(Math.atan2(p.z-C[1],p.x-C[0])); }
        else if(T.gnd===SL[1] && rC>0.28 && !toEx){ goal=C; }
        else if(T.gnd===SL[1] && rC<=0.28){ goal=exC; safe=ok(exAng); }
        else if(T.gnd===SL[1]){ goal=exC; }
        if(goal){ const gx=goal[0]-p.x, gz=goal[1]-p.z, q=Math.hypot(gx,gz)||1; if(safe && q>0.05){ dx=gx/q; dz=gz/q; } else { dx=dz=0; } T.buf=0; } } }
    if((T.secs[sec]==="sweep3" || (T.secsB&&T.secsB[sec]==="sweep3")) && T.onG && T.gnd && T.gnd.kind!=="floor"){ const S=T.S.slice(T.secR[sec][0],T.secR[sec][1]), SW=S.filter(s=>s.kind==="sweep" && (!s.seg || !s.seg.kind || s.seg.kind==="sweep3")), d=(SW[0]&&SW[0].seg)?SW[0].seg.d:H.TDIR[sec%4]; if(SW[0] && SW[0].seg && T.gnd.seg && T.gnd.seg!==SW[0].seg) SW.length=0;   // (v465) 🕐🕐🕐 앞 바늘 가운데 → (세 바늘 모두 멀 때) 뒤 두 바늘 사이 → 출구
      const A=SW[0], B=SW[1], Cc=SW[2]; if(A && Math.abs(p.y-A.y0)<1.0){ const arr=(sw,ph)=>{ const a=-sw.mesh.rotation.y, M=Math.PI*2, dd=sw.sp>0?(((a-ph)%M)+M)%M:(((ph-a)%M)+M)%M; return dd/Math.abs(sw.sp); }, ok=(sw,ph,tm)=>{ const M=Math.PI*2/Math.abs(sw.sp), t0=arr(sw,ph); return t0>tm && M-t0>0.3; }, ang=(c,q)=>Math.atan2(q[1]-c[1],q[0]-c[0]);
        const G=[(B.c[0]+Cc.c[0])/2,(B.c[1]+Cc.c[1])/2], al=q=>(q[0]-p.x)*d[0]+(q[1]-p.z)*d[1], rA=Math.hypot(p.x-A.c[0],p.z-A.c[1]); let goal=null, safe=true;
        if(rA<=0.28){ goal=[G[0]+d[0]*1.3, G[1]+d[1]*1.3]; safe=ok(A,ang(A.c,G),0.5) && ok(B,ang(B.c,G),0.95) && ok(Cc,ang(Cc.c,G),0.95); }
        else if(al(A.c)>0.05){ goal=A.c; safe=rA<1.45 || ok(A,ang(A.c,[p.x,p.z]),0.55); }
        else if(al(G)>-1.0){ goal=[G[0]+d[0]*1.3, G[1]+d[1]*1.3]; }
        if(goal){ const gx=goal[0]-p.x, gz=goal[1]-p.z, q=Math.hypot(gx,gz)||1; if(safe && q>0.05){ dx=gx/q; dz=gz/q; } else { dx=dz=0; } T.buf=0; } } }
    if((T.secs[sec]==="door" || (T.secsB&&T.secsB[sec]==="door")) && T.onG && T.gnd && T.gnd.kind!=="floor" && (()=>{ const dd=T.S.slice(T.secR[sec][0],T.secR[sec][1]).find(s=>s.kind==="door"); return !dd || !dd.seg || !T.gnd.seg || T.gnd.seg===dd.seg; })()){ const d0=T.S.slice(T.secR[sec][0],T.secR[sec][1]).find(s=>s.kind==="door"), d=(d0&&d0.seg)?d0.seg.d:H.TDIR[sec%4], D=T.S.slice(T.secR[sec][0],T.secR[sec][1]).filter(s=>s.kind==="door" && s.fake).map(s=>{ const cx=(s.min.x+s.max.x)/2, cz=(s.min.z+s.max.z)/2, al=(cx-p.x)*d[0]+(cz-p.z)*d[1], lx=cx-p.x-d[0]*al, lz=cz-p.z-d[1]*al; return {cx,cz,al,lat:Math.hypot(lx,lz),lx,lz}; }).filter(o=>o.al>-0.15);   // (v463) 🚪 가짜 문 쪽으로
      if(D.length){ const a0=Math.min(...D.map(o=>o.al)), o=D.filter(o=>o.al<a0+0.3).sort((x,y)=>x.lat-y.lat)[0]; if(o.lat>0.12 && o.al<0.75){ dx=o.lx/o.lat; dz=o.lz/o.lat; } else { const ex=o.cx+d[0]*0.6-p.x, ez=o.cz+d[1]*0.6-p.z, q=Math.hypot(ex,ez)||1; dx=ex/q; dz=ez/q; } T.buf=0; } }
    for(const s of T.S){ if(s.kind!=="pend" || s.bx==null || !T.onG || Math.abs(p.y-(s.py-3.4))>1.2) continue; const al=(s.G.position.x-p.x)*s.F.d[0]+(s.G.position.z-p.z)*s.F.d[1]; if(al>0.75 && al<1.45){ const wb=Math.sin(s.th)*s.L; if(!(Math.abs(wb)>0.95 && wb*s.vth>0)){ dx=dz=0; T.buf=0; } } }   // (v463) 🔨 공이 멀어질 때 지나감
    T.inp.x=dx; T.inp.y=-dz; H.twStep(dt);
  }
  log.push([sec, +secT.toFixed(1), T.dead]);
  const r={fin:T.fin, t:+t.toFixed(1), dead:T.dead, cp:T.cp, n:T.cps.length-1, secs:T.secs, log}; T.bot=false; T.inp.x=T.inp.y=0; return r; }
"""

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
        await pg.evaluate("()=>{ Object.keys(localStorage).filter(k=>k.startsWith('hyeng_proto_')).forEach(k=>localStorage.removeItem(k)); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); localStorage.setItem('hyeng_proto_baitok','1'); }")
        await pg.reload(); await pg.wait_for_timeout(2500)
        E = pg.evaluate
        async def until(js, n=60):
            for _ in range(n):
                try:
                    if await E(js): return True
                except Exception: pass
                await pg.wait_for_timeout(200)
            return False
        await E("()=>{ HOUSE.setWx(false); HOUSE.go('village'); }"); await until("()=>HOUSE.place()==='village'")
        await E("()=>HOUSE.towerAsk()"); await until("()=>!!document.getElementById('twK')")
        r = await E("()=>[!!document.getElementById('twK'), !!document.getElementById('twS'), document.getElementById('infoT').innerText]")
        ok(r[0] and r[1] and "30층" in r[2] and "40층" in r[2] and "연습" in r[2], f"🟢 쉬움 30층 + 🗼 도전 40층 {r[2][:120]!r}")
        await pg.screenshot(path=OUT + "tower462_ask.png")
        await E("()=>{ HOUSE.TW.seed='2026-10-30'; document.getElementById('twK').click(); }")
        ok(await until("()=>HOUSE.place()==='tower' && HOUSE.TW.on"), "🟢 → 타워 안")
        await pg.wait_for_timeout(600)
        r = await E("()=>[HOUSE.TW.mode, HOUSE.TW.cps.length-1, document.getElementById('twFloor').textContent, HOUSE.twNetPath().slice(-1)]")
        ok(r[0] == "kid" and r[1] == 30 and r[2].startswith("1 / 30") and r[3] == "k", f"30층 · 1 / 30층 · 경로 k {r}")
        await pg.screenshot(path=OUT + "tower462_in.png")
        r = await E("""()=>{ const T=HOUSE.TW, G=["steps","gaps","mover","bounce","beam","fade","turn","door"], EZ=["steps","gaps","lava","mover","fade","bounce","beam","ice","laser","turn","crumble","brick","door","tiptoe","pend","sweep","sweep3"], out=[];
            for(let d=1; d<=8; d++){ T.seed='2026-12-'+d; HOUSE.twBuild('kid'); const s=T.secs, rise=[]; for(let i=1;i<T.ys.length;i++) if(s[i-1]!=='ground' && s[i]!=='ground') rise.push(T.ys[i]-T.ys[i-1]);
              out.push([s.length, s[9], s[19], s.filter(k=>k==='ground').length, s.slice(0,9).every(k=>G.includes(k)), s.every(k=>k==='ground' || EZ.includes(k)), T.S.filter(x=>x.kind==='spin').length]); }
            HOUSE.twBuild('sky'); const skyH=T.hy; HOUSE.twBuild('kid'); return [out, +T.hy.toFixed(1), +skyH.toFixed(1)]; }""")
        ok(all(x[0] == 30 and x[1] == x[2] == "ground" and x[3] == 2 and x[4] and x[5] and x[6] == 0 for x in r[0]), f"1~9 아주 쉬움 · 🏝 10·20 · 어려움 장애물 없음(빙글 막대 0) (8일) {r[0][:2]} 높이 쉬움 {r[1]} / 도전 {r[2]}")
        # 용암 → 아래 땅
        r = await E("""()=>{ const T=HOUSE.TW; T.seed='2026-10-30'; HOUSE.twBuild('kid'); T.mode='kid'; T.bot=false; T.on=true; T.fin=false; const c=T.cps[15]; T.p.set((c.min.x+c.max.x)/2, c.max.y+0.01, (c.min.z+c.max.z)/2); T.v.set(0,0,0); HOUSE.twStep(1/90); T.cp=15;
            const L={kind:'kill', on:true, min:new THREE.Vector3(T.p.x-1,T.p.y-0.2,T.p.z-1), max:new THREE.Vector3(T.p.x+1,T.p.y+0.5,T.p.z+1), mesh:new THREE.Object3D()}; T.S.push(L); HOUSE.twStep(1/90); T.S.pop();
            return [+(T.p.y-T.cps[9].max.y).toFixed(2), document.getElementById('toast').innerText]; }""")
        ok(abs(r[0]) < 0.05 and "10층 땅" in r[1], f"16층 용암 → 🏝 10층 땅부터 {r}")
        res = []
        for seed in ["2026-11-%02d" % d for d in range(1, 7)]:
            r = await E(BOT, {"mode": "kid", "seed": seed, "max": 1100})
            res.append((seed, r["fin"], r["t"], r["dead"]) + (() if r["fin"] else (r["cp"], r["secs"][r["cp"]] if r["cp"] < len(r["secs"]) else "-")))
        fails = [x for x in res if not x[1]]
        ok(not fails, f"🤖 자동 선수가 쉬움 30층 꼭대기까지 (6일) {fails[:3]} 평균 {sum(x[2] for x in res)/len(res):.0f}초")
        # 꼭대기 💎 12
        await E("()=>{ HOUSE.TW.rec={}; Object.keys(localStorage).filter(k=>k.indexOf('hyeng_proto_tower')>=0).forEach(k=>localStorage.removeItem(k)); }")
        await E("()=>{ const T=HOUSE.TW; T.bot=false; T.seed=null; HOUSE.twBuild('kid'); T.on=true; T.fin=false; T.mode='kid'; T.t0=performance.now()-300000; T.cp=0; HOUSE.twRespawn(true); HOUSE.setGems(0); }")
        r = await E("""()=>{ const T=HOUSE.TW, top=T.top; T.bot=true; T.p.set((top.min.x+top.max.x)/2, top.max.y+0.3, (top.min.z+top.max.z)/2); T.v.set(0,0,0); for(let i=0;i<40;i++) HOUSE.twStep(1/90); T.bot=false; return [T.fin, HOUSE.gems()]; }""")
        await pg.wait_for_timeout(1300)
        t = await E("()=>document.getElementById('infoT').innerText")
        ok(r[0] and r[1] == 12 and "쉬움 30층" in t and "40층 도전" in t, f"🏆 쉬움 꼭대기 → 💎 12 · 「40층 도전도」 {r} {t[:80]!r}")
        r = await E("""()=>{ const d=HOUSE.dayKey(); const s=HOUSE.SOC(); s.cls={AAAAA:{n:'루아', tw:{d, k:301.2}}}; s.who={}; HOUSE.towerAsk(); return document.getElementById('twBd').innerText; }""")
        ok("루아" in r and "🟢" in r, f"친구 기록 🟢 쉬움 줄 {r!r}")
        ok(not real_errs(errs), "오류 없음 " + str(real_errs(errs)[:3]))
        await br.close()
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)

asyncio.run(main())
