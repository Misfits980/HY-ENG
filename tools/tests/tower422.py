"""(v422) 🗼 하늘 타워 (로블록스 오비) · 😀 감정 표현 · 🏆 오늘 친구 기록 — 사용자: "마이타운에 로블록스 타워 같은 것도 · 마이타운을 더 다듬어 줘 · 애들이 재미없어지면 안 되니까"
  ① 마을 🗼 건물·이름표 → 쉬움/어려움 고르기 → 타워 안 (조이스틱·점프 단추·층·시간)
  ② 몸: 앞으로 걷기 · 점프 · 착지 · 용암/떨어지면 🚩 체크포인트 · 🔤 단어 다리(맞는 유리만) · 점프대 · 사라지는 발판
  ③ 날마다 같은 타워(모든 기기) · 다른 날은 다르게 · 🤖 자동 선수가 쉬움·어려움 모든 날 끝까지 (못 깨는 타워 없음)
  ④ 꼭대기: 오늘 처음 💎 (쉬움 5 · 어려움 12) · 기록 · 다시 하면 💎 없음 · 친구 기록 · 마을로
  ⑤ 😀 감정 표현 (👋 마을 사람이 대답 · 💃 춤)"""
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
    if(T.secs[sec]==="sweep" && T.onG && T.gnd && T.gnd.kind!=="floor"){ const S=T.S.slice(T.secR[sec][0],T.secR[sec][1]), sw=S.find(s=>s.kind==="sweep"), SL=S.filter(s=>s.kind==="solid" && !s.noWalk);   // (v464) 🕐 입구 → (바늘이 멀 때) 가운데 → (바늘이 멀 때) 출구
      if(sw && Math.abs(p.y-sw.y0)<1.0){ const C=sw.c, rC=Math.hypot(p.x-C[0],p.z-C[1]), arr=ph=>{ const a=-sw.mesh.rotation.y, M=sw.len2>0?Math.PI:Math.PI*2, d=sw.sp>0?(((a-ph)%M)+M)%M:(((ph-a)%M)+M)%M; return d/Math.abs(sw.sp); }, ok=ph=>{ const M=(sw.len2>0?Math.PI:Math.PI*2)/Math.abs(sw.sp), t0=arr(ph); return t0>0.5 && M-t0>0.3; };
        const ex=SL[2], exC=[(ex.min.x+ex.max.x)/2,(ex.min.z+ex.max.z)/2], exAng=Math.atan2(exC[1]-C[1],exC[0]-C[0]), toEx=((p.x-C[0])*(exC[0]-C[0])+(p.z-C[1])*(exC[1]-C[1]))>0;
        let goal=null, safe=true;
        if(T.gnd===SL[0]){ goal=C; safe=ok(Math.atan2(p.z-C[1],p.x-C[0])); }
        else if(T.gnd===SL[1] && rC>0.28 && !toEx){ goal=C; }
        else if(T.gnd===SL[1] && rC<=0.28){ goal=exC; safe=ok(exAng); }
        else if(T.gnd===SL[1]){ goal=exC; }
        if(goal){ const gx=goal[0]-p.x, gz=goal[1]-p.z, q=Math.hypot(gx,gz)||1; if(safe && q>0.05){ dx=gx/q; dz=gz/q; } else { dx=dz=0; } T.buf=0; } } }
    if(T.secs[sec]==="sweep3" && T.onG && T.gnd && T.gnd.kind!=="floor"){ const S=T.S.slice(T.secR[sec][0],T.secR[sec][1]), SW=S.filter(s=>s.kind==="sweep"), d=H.TDIR[sec%4];   // (v465) 🕐🕐🕐 앞 바늘 가운데 → (세 바늘 모두 멀 때) 뒤 두 바늘 사이 → 출구
      const A=SW[0], B=SW[1], Cc=SW[2]; if(A && Math.abs(p.y-A.y0)<1.0){ const arr=(sw,ph)=>{ const a=-sw.mesh.rotation.y, M=Math.PI*2, dd=sw.sp>0?(((a-ph)%M)+M)%M:(((ph-a)%M)+M)%M; return dd/Math.abs(sw.sp); }, ok=(sw,ph,tm)=>{ const M=Math.PI*2/Math.abs(sw.sp), t0=arr(sw,ph); return t0>tm && M-t0>0.3; }, ang=(c,q)=>Math.atan2(q[1]-c[1],q[0]-c[0]);
        const G=[(B.c[0]+Cc.c[0])/2,(B.c[1]+Cc.c[1])/2], al=q=>(q[0]-p.x)*d[0]+(q[1]-p.z)*d[1], rA=Math.hypot(p.x-A.c[0],p.z-A.c[1]); let goal=null, safe=true;
        if(rA<=0.28){ goal=[G[0]+d[0]*1.3, G[1]+d[1]*1.3]; safe=ok(A,ang(A.c,G),0.5) && ok(B,ang(B.c,G),0.95) && ok(Cc,ang(Cc.c,G),0.95); }
        else if(al(A.c)>0.05){ goal=A.c; safe=rA<1.45 || ok(A,ang(A.c,[p.x,p.z]),0.55); }
        else if(al(G)>-1.0){ goal=[G[0]+d[0]*1.3, G[1]+d[1]*1.3]; }
        if(goal){ const gx=goal[0]-p.x, gz=goal[1]-p.z, q=Math.hypot(gx,gz)||1; if(safe && q>0.05){ dx=gx/q; dz=gz/q; } else { dx=dz=0; } T.buf=0; } } }
    if(T.secs[sec]==="door" && T.onG && T.gnd && T.gnd.kind!=="floor"){ const d=H.TDIR[sec%4], D=T.S.slice(T.secR[sec][0],T.secR[sec][1]).filter(s=>s.kind==="door" && s.fake).map(s=>{ const cx=(s.min.x+s.max.x)/2, cz=(s.min.z+s.max.z)/2, al=(cx-p.x)*d[0]+(cz-p.z)*d[1], lx=cx-p.x-d[0]*al, lz=cz-p.z-d[1]*al; return {cx,cz,al,lat:Math.hypot(lx,lz),lx,lz}; }).filter(o=>o.al>-0.15);   // (v463) 🚪 가짜 문 쪽으로
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
        # ① 마을
        r = await E("()=>[HOUSE.LBL().some(L=>L.d.k==='tower'), !!HOUSE.towerObj(), HOUSE.TW_AT]")
        ok(r[0] and r[1] and r[2] == [9, 3, 2, 2], f"마을에 🗼 타워 건물 · 이름표 {r}")
        r = await E("()=>{ const L=HOUSE.LBL().find(L=>L.d.k==='tower'); L.d.act(); return 1; }")
        ok(await until("()=>document.getElementById('info').classList.contains('on') && !!document.getElementById('twS')", 80), "이름표 → 걸어가서 「오늘의 하늘 타워」 (v459) 🗼 40층")
        r = await E("()=>document.getElementById('infoT').innerText")
        ok("40층" in r and ("친구 기록" in r or "첫 번째" in r), f"고르기 창 + 🏆 오늘 친구 기록 {r[:80]!r}")
        await pg.screenshot(path=OUT + "tower422_ask.png")
        await E("()=>{ HOUSE.TW.seed='2026-10-07'; document.getElementById('twS').click(); }")
        ok(await until("()=>HOUSE.place()==='tower' && HOUSE.TW.on"), "🗼 → 타워 안")
        r = await E("()=>[HOUSE.TW.cps.length-1, HOUSE.TW.secs.includes('word'), document.getElementById('twUI').classList.contains('on'), getComputedStyle(document.querySelector('.bar.bot')).display, document.getElementById('twFloor').textContent, HOUSE.TW.cp]")
        ok(r[0] == 40 and not r[1] and r[2] and r[3] == "none" and r[4].startswith("1 / 40") and r[5] == 0, f"(v459) 40층 · (v453) 🔤 단어 다리 없음 · 조이스틱·점프 화면 (아래 독 숨김) {r}")
        await pg.wait_for_timeout(800); await pg.screenshot(path=OUT + "tower422_in.png")
        # ② 몸 — 시간이 멈춘 채로 직접 계산 (TW.bot)
        r = await E("""()=>{ const T=HOUSE.TW; T.bot=true; HOUSE.twRespawn(true); const y0=T.p.y, a=[T.onG, T.p.x, T.p.z]; T.yaw=0; T.inp.x=0; T.inp.y=0;
            for(let i=0;i<30;i++) HOUSE.twStep(1/90); const still=[T.p.x, T.p.y];
            T.buf=0.16; let top=0; for(let i=0;i<120;i++){ HOUSE.twStep(1/90); top=Math.max(top, T.p.y-y0); }
            return [a[0], Math.abs(still[1]-y0)<0.01, +top.toFixed(2), T.onG, Math.abs(T.p.y-y0)<0.02]; }""")
        ok(r[0] and r[1] and 1.3 < r[2] < 2.0 and r[3] and r[4], f"서 있기 · 점프 높이 ≈1.6 · 다시 착지 {r}")
        r = await E("""()=>{ const T=HOUSE.TW, x0=T.p.x; T.key.r=1; for(let i=0;i<20;i++) HOUSE.twStep(1/90); T.key.r=0; const dx=T.p.x-x0; for(let i=0;i<30;i++) HOUSE.twStep(1/90); return [+dx.toFixed(2), Math.round(HOUSE.TW.p.y*100)/100]; }""")
        ok(r[0] > 0.3, f"⌨️ 오른쪽 화살표 → 움직임 {r}")
        r = await E("""()=>{ const T=HOUSE.TW; for(let d=1; d<60; d++){ T.seed='2026-12-'+d; HOUSE.twBuild('easy'); if(T.secs.includes('lava')) break; } T.cp=0; HOUSE.twRespawn(true); const d0=T.dead; const lava=T.S.find(s=>s.kind==='kill'); if(!lava) return 'nolava';
            T.cp=1; HOUSE.twRespawn(true); const c=T.p.clone(); T.p.set((lava.min.x+lava.max.x)/2, lava.max.y+0.05, (lava.min.z+lava.max.z)/2); T.v.set(0,-1,0); for(let i=0;i<10;i++) HOUSE.twStep(1/90);
            const back=T.p.distanceTo(c)<0.05; const d1=T.dead; T.p.y-=20; HOUSE.twStep(1/90); return [T.dead-d0, back, T.dead-d1, T.p.distanceTo(c)<0.05]; }""")
        ok(r != "nolava" and r[0] >= 1 and r[1] and r[2] == 1 and r[3], f"🔥 용암 → 🚩 체크포인트로 · 떨어져도 체크포인트로 {r}")
        # (v453) 🔤 유리 단어 다리는 뺌 (tower453 이 확인)
        # (v423) 🪜 사다리 기둥 · 카메라 면
        r = await E("""()=>{ const T=HOUSE.TW; for(let d=1; d<60; d++){ T.seed='2026-12-'+d; HOUSE.twBuild('easy'); if(!['door','tiptoe','pend'].includes(T.secs[0])) break; } T.cp=0; HOUSE.twRespawn(true); const pad=T.cps[1], a=T.secR[0], last=T.S.slice(a[0],a[1]).filter(s=>s.kind!=='kill' && !s.move && s.kind!=='glass' && s.kind!=='door' && !s.fake && !s.noWalk && s.net==null && s.min).pop();
            const s0=T.side.slice(); T.p.set((last.min.x+last.max.x)/2, last.max.y+0.001, (last.min.z+last.max.z)/2); T.v.set(0,0,0);
            const cx=(pad.min.x+pad.max.x)/2-T.p.x, cz=(pad.min.z+pad.max.z)/2-T.p.z, L=Math.hypot(cx,cz); T.yaw=0; T.inp.x=cx/L; T.inp.y=-cz/L; let climbed=0;
            for(let i=0;i<360 && T.cp<1;i++){ HOUSE.twStep(1/90); if(T.climb) climbed=1; } T.inp.x=T.inp.y=0;
            return [pad.climb, +(pad.max.y-last.max.y).toFixed(2), climbed, T.cp, s0.join(), T.side.join()]; }""")
        ok(r[0] and r[1] > 1.6 and r[2] == 1 and r[3] == 1 and r[4] != r[5], f"🪜 사다리 기둥: 밀면 올라가서 🚩 2층 · 카메라가 다음 면으로 {r}")
        # ③ 날마다
        r = await E("""()=>{ const T=HOUSE.TW, sig=()=>T.secs.join()+'|'+T.S.length+'|'+T.hy.toFixed(2); T.seed='2026-10-07'; HOUSE.twBuild('hard'); const a=sig(); HOUSE.twBuild('hard'); const b=sig(); T.seed='2026-10-08'; HOUSE.twBuild('hard'); const c=sig(); return [a===b, a!==c, T.cps.length-1]; }""")
        ok(r[0] and r[1] and r[2] == 30, f"같은 날 = 같은 타워 · 다른 날 = 다른 타워 · (v454) 🔴 30층 {r}")
        r = await E("""()=>{ const T=HOUSE.TW, bad=[]; const solid=s=>s.min && s.kind!=='spin' && s.kind!=='floor';
            for(const mode of ['easy','hard']) for(let d=1; d<=12; d++){ T.seed='2026-09-'+d; HOUSE.twBuild(mode); const own=new Map(); T.secR.forEach(([a,b],i)=>{ for(let j=a;j<b;j++) own.set(T.S[j], i); }); T.cps.forEach((c,i)=>own.set(c, 'cp'+i));
              const L=T.S.filter(solid).filter(s=>own.has(s)); for(let i=0;i<L.length;i++) for(let j=i+1;j<L.length;j++){ const A=L[i], B=L[j]; if(own.get(A)===own.get(B)) continue;
                const o=k=>Math.min(A.max[k],B.max[k])-Math.max(A.min[k],B.min[k]); if(o('x')>0.02 && o('y')>0.02 && o('z')>0.02) bad.push([mode,d,own.get(A),own.get(B),A.kind,B.kind]); } }
            return bad; }""")
        ok(not r, f"층과 층의 발판·사다리 기둥이 겹치지 않음 (24개 타워) {r[:3]}")
        res = []
        for mode in ["easy", "hard"]:
            for seed in ["2026-11-%02d" % d for d in range(1, 9)]:
                r = await E(BOT, {"mode": mode, "seed": seed, "max": 900 if mode == "hard" else 400})
                res.append((mode, seed, r["fin"], r["t"], r["dead"]) + (() if r["fin"] else (r["cp"], r["secs"][r["cp"]] if r["cp"] < len(r["secs"]) else "-")))
        fails = [x for x in res if not x[2]]
        ok(not fails, f"🤖 자동 선수가 쉬움 8일·어려움 8일 모두 꼭대기 (못 깨는 타워 없음) {fails[:3]} 평균 {sum(x[3] for x in res)/len(res):.0f}초")
        # ④ 꼭대기 (🤖 가 남긴 기록은 지움)
        await E("()=>{ HOUSE.TW.rec={}; Object.keys(localStorage).filter(k=>k.indexOf('hyeng_proto_tower')>=0).forEach(k=>localStorage.removeItem(k)); }")
        await E("()=>{ const T=HOUSE.TW; T.bot=false; T.seed=null; HOUSE.twBuild('easy'); T.on=true; T.fin=false; T.mode='easy'; T.t0=performance.now()-65000; T.cp=0; HOUSE.twRespawn(true); HOUSE.setGems(10); }")
        r = await E("""()=>{ const T=HOUSE.TW, top=T.top; T.bot=true; T.p.set((top.min.x+top.max.x)/2, top.max.y+0.3, (top.min.z+top.max.z)/2); T.v.set(0,0,0); for(let i=0;i<40;i++) HOUSE.twStep(1/90); T.bot=false; return [T.fin, HOUSE.gems()]; }""")
        await pg.wait_for_timeout(1200)
        t = await E("()=>document.getElementById('infoT').innerText")
        ok(r[0] and r[1] == 16 and "꼭대기" in t and "💎 +6" in t and "1:0" in t, f"🏆 꼭대기 → 💎 +6 (오늘 처음) · 시간 {r} {t[:60]!r}")
        await pg.screenshot(path=OUT + "tower422_win.png")
        r = await E("""()=>{ const rec=JSON.parse(localStorage.getItem(Object.keys(localStorage).find(k=>k.indexOf('hyeng_proto_tower')>=0))); const d=Object.keys(rec)[0]; return [rec[d].easy.best>60, rec[d].easy.n]; }""")
        ok(r[0] and r[1] == 1, f"기록 저장 {r}")
        await E("()=>{ document.getElementById('info').classList.remove('on'); const T=HOUSE.TW; T.on=true; T.fin=false; T.t0=performance.now()-40000; T.cp=0; HOUSE.twRespawn(true); }")
        r = await E("""()=>{ const T=HOUSE.TW, top=T.top; T.bot=true; T.p.set((top.min.x+top.max.x)/2, top.max.y+0.3, (top.min.z+top.max.z)/2); T.v.set(0,0,0); for(let i=0;i<40;i++) HOUSE.twStep(1/90); T.bot=false; return [T.fin, HOUSE.gems()]; }""")
        await pg.wait_for_timeout(1200)
        t = await E("()=>document.getElementById('infoT').innerText")
        ok(r[1] == 16 and "새 기록" in t, f"두 번째 = 💎 없음 · 🎉 새 기록 {r} {t[:50]!r}")
        r = await E("()=>{ HOUSE.TW.rec; return document.querySelector('#infoT') && 1; }")
        await E("()=>document.getElementById('infoOk').click()")
        ok(await until("()=>HOUSE.place()==='village' && !HOUSE.TW.on"), "🏘 마을로 → 타워 끝")
        r = await E("()=>[document.getElementById('twUI').classList.contains('on'), document.body.classList.contains('twOn'), HOUSE.camera.fov, getComputedStyle(document.querySelector('.bar.bot')).display]")
        ok(r == [False, False, 30, "flex"], f"화면·카메라 원래대로 {r}")
        # 친구 기록 (publish 에 tw)
        r = await E("""()=>{ const d=HOUSE.dayKey(); const s=HOUSE.SOC(); s.cls={AAAAA:{n:'루아', tw:{d, e:41.2}}, BBBBB:{n:'주호', tw:{d:'2000-01-01', e:10}}}; s.who={CCCCC:{n:'라언', tw:{d, e:80, h:120.5}}};
            HOUSE.towerAsk(); return document.getElementById('twBd').innerText; }""")
        ok("루아" in r and "라언" in r and "주호" not in r and "🥇" in r and "0:41.2" in r, f"🏆 오늘 친구 기록 (오늘 것만 · 빠른 순) {r!r}")
        await pg.screenshot(path=OUT + "tower422_board.png")
        await E("()=>document.getElementById('infoOk').click()")
        # ⑤ 감정 표현
        await pg.wait_for_timeout(600)
        ok(await E("()=>document.getElementById('bEmo').classList.contains('on')"), "😀 감정 표현 단추 (마을)")
        await E("()=>{ const h=HOUSE.hero(), n=HOUSE.npcs[0]; n.path=[]; n.moving=false; n.talking=false; n.cx=h.cx+1; n.cz=h.cz; n.g.position.set(n.cx+0.5,0,n.cz+0.5); document.getElementById('bEmo').click(); }")
        ok(await E("()=>document.getElementById('emoBar').classList.contains('on') && document.querySelectorAll('#emoBar button').length===4"), "👋 💃 🎉 ❤️")
        await pg.screenshot(path=OUT + "tower422_emo.png")
        await E("()=>document.querySelector('#emoBar [data-emo=\"1\"]').click()"); await pg.wait_for_timeout(900)
        r = await E("()=>[HOUSE.hero().act, HOUSE.npcs[0].act, document.getElementById('toast').innerText]")
        ok(r[0] == "dance" and r[1] == "yay" and "dance" in r[2], f"💃 춤 → 옆 마을 사람도 같이 {r}")
        await pg.screenshot(path=OUT + "tower422_dance.png")
        ok(not real_errs(errs), "오류 없음 " + str(real_errs(errs)[:3]))
        await br.close()
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)

asyncio.run(main())
