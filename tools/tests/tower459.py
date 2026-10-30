"""(v459) 🗼 하늘 타워 40층 (쉬움 10 + 어려움 30 붙임) · 🏝 10·20·30층 넓은 땅 · 😀 휴대폰 이모티콘 가운데
  사용자: "타워 저번에 있던 10층부터 해서 이번에 만든 30층까지 붙여 줄래? 10층/20/30층마다 넓은 땅 · 토네이도식 · 20층 높이쯤이면 10층에 떨어질 수도"
          "이모티콘 휴대폰으로 했을 때 문제 생기고"
  ① 고르기 창 = 🗼 하나 (40층) · 들어가면 1 / 40층
  ② 40층: 1~9 쉬움 장애물 · 10·20·30 = 🏝 넓은 땅 · 11~40 어려움 (올라갈수록 lv) · 날마다 같음
  ③ 🏝 땅 = 타워 전체를 덮음 · 위로 갈수록 넓어짐 · 위층 바깥에서 떨어지면 땅에 내려앉음 (+ 💎 2 · 오늘 처음) · 아래층에서는 투명
  ④ 🔴 레이저 (25층) → 🏝 20층 땅부터 · 🚩 도 같은 곳 · 맨 아래에서는 맨 아래
  ⑤ 🤖 자동 선수가 40층 꼭대기까지 (5일)
  ⑥ 😀 ❤️ 말풍선 = 그림이 말풍선 가운데"""
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
  T._fl=null; const NJ=new Map(); T.S.filter(s=>s.noJump).forEach(s=>{ if(!NJ.has(s.seg)) NJ.set(s.seg,[]); NJ.get(s.seg).push(s); }); const LZ=T.S.filter(s=>s.kind==="laser"), SZ=T.S.filter(s=>s.kind==="spin"); let k=0, sec=-1, dead=T.dead, fallN=T.fall, t=0, log=[], stuck=0, lastCp=0, secT=0; const dt=1/90;
  while(t<opt.max && !T.fin){ t+=dt; secT+=dt;
    if(T.onG && T.gnd && T.gnd.ground!=null && T.cp>T.gnd.ground) T.cp=T.gnd.ground;
    if(T.onG && T.gnd && T.gnd.kind==="floor" && k>0) k=0;   // (v465) 맨 아래 바닥에 떨어지면 첫 발판부터   // (v463) 🏝 땅에 떨어지면 거기서 다시 올라감
    if(T.cp!==sec || T.dead!==dead || T.fall!==fallN){ if(T.cp!==sec){ log.push([sec, +secT.toFixed(1), T.dead]); secT=0; } sec=T.cp; dead=T.dead; fallN=T.fall; k=0; }
    if(sec>=T.cps.length-1) break;
    const gi=(T.onG && T.gnd && T.gnd.seg && T.gnd.seg.i!=null) ? T.gnd.seg.i : null; if(gi!=null && gi!==T._fl){ T._fl=gi; k=0; } const fl=(T._fl!=null && T._fl<sec)?T._fl:sec;   // (v472) 아래층으로 떨어지면 그 층 길로 다시 올라감
    const W=wps(fl), p=T.p; for(let j=W.length-1;j>=0;j--){ if(T.onG && T.gnd===W[j]){ k=Math.max(k,j+1); break; } }
    if(T.onG && T.gnd===T.cps[fl] && k>1) k=0; if(T.onG){ const j=W.indexOf(T.gnd); if(j>=0 && k>j+2) k=j+1; }   // (v472) 한 바퀴 층: 떨어져서 앞쪽 발판에 내려앉으면 거기서부터
    if(W[k] && W[k].kind==="bounce" && T.v.y>8 && inXZ(W[k],p.x,p.z)) k++;
    if(k>=W.length) k=W.length-1; let tg=W[k]; while(!tg.on && k<W.length-1){ k++; tg=W[k]; }
    const m=Math.min(0.45,(tg.max.x-tg.min.x)/2-0.02), n=Math.min(0.45,(tg.max.z-tg.min.z)/2-0.02);
    const cx=Math.max(tg.min.x+m,Math.min(tg.max.x-m,p.x)), cz=Math.max(tg.min.z+n,Math.min(tg.max.z-n,p.z));
    let dx=cx-p.x, dz=cz-p.z; const L=Math.hypot(dx,dz); if(L>0.05){ dx/=L; dz/=L; } else { dx=dz=0; } if(L<=0.05 && T.onG && k<W.length-1) k++;   // (v467) 겹친 발판 위 = 이미 도착
    if(T.onG && T.gnd && T.gnd.push && (dx||dz)){ dx=dx*4.4-T.gnd.push[0]; dz=dz*4.4-T.gnd.push[1]; const q=Math.hypot(dx,dz); dx/=q; dz/=q; }
    const g=T.gnd, gp=gap(tg,p), rise=tg.max.y-(g?g.max.y:p.y);
    if(T.onG && g && g!==tg){
      const nx=p.x+dx*0.35, nz=p.z+dz*0.35, leaving=!inXZ(g,nx,nz);
      const R=tg.move?1.1:2.6; if(tg.climb){ if(leaving && gp>0.12) T.buf=0.16; } else if(leaving && (gp>R || rise>1.45) && !g.crumble){ dx=dz=0; }   // (v463) 🍂 무너지는 발판 위에서는 기다리지 않음   // 기다림 (움직이는 발판)
      else if(leaving && gp<0.12 && Math.abs(rise)<0.12){ }   // (v466) 바로 붙은 발판은 걸어서
      else if(!tg.climb && (leaving || rise>(tg.crumble?0.25:0.06)) && gp<R && rise<1.5 && (leaving || gp<1.1)) T.buf=0.16;
    }
    for(const s of T.S){ if(s.kind==="spin" && T.onG && Math.abs(p.y-s.y0)<1.2){ const qx=p.x-s.c[0], qz=p.z-s.c[1], rr=Math.hypot(qx,qz); if(rr<s.len+0.5){   // (v454) 막대가 올 때를 계산해서 점프 (빨라진 막대)
    for(const s of T.S){ if(s.kind==="sweep" && T.onG && Math.abs(p.y-s.y0)<1.0){ const qx=p.x-s.c[0], qz=p.z-s.c[1], rr=Math.hypot(qx,qz); if(rr<s.len+0.6){   // (v464) 🕐 바늘이 올 때 점프
        const a=-s.mesh.rotation.y, ph=Math.atan2(qz,qx), M=s.len2>0?Math.PI:Math.PI*2, d=s.sp>0?(((a-ph)%M)+M)%M:(((ph-a)%M)+M)%M, tt=d/Math.abs(s.sp); if(tt>0.12 && tt<0.3) T.buf=0.16; } } }
        const a=-s.mesh.rotation.y, ph=Math.atan2(qz,qx), d=(((a-ph)%Math.PI)+Math.PI)%Math.PI, tt=d/s.sp; if(((tt>0.2 && tt<0.36) || rr<0.9) && !(T.gnd && s.seg && s.seg===T.gnd.seg)) T.buf=0.16; } } }   // (v466) 가운데(막대 뿌리)는 콩콩 뛰어서
    if(T.onG && T.gnd && T.gnd.seg && (LZ.length||SZ.length) && (dx||dz)){ const LS=LZ.filter(s=>s.seg===T.gnd.seg && Math.abs(p.y-s.y0)<0.5), SP=SZ.filter(s=>s.seg===T.gnd.seg && Math.abs(p.y-(s.y0-0.3))<0.6); if(LS.length||SP.length){   // (v472) 🔴 레이저·🌀 막대: 0.3초 달리기 → 안 되면 점프 → 안 되면 기다리기 (앞날 계산)
      const F=T.gnd.seg, d=F.d, T0=T.clk||0, vf=T.v.x*dx+T.v.z*dz, dist=(q,a)=>4.4*q-(4.4-vf)*(1-Math.exp(-a*q))/a;
      const hit=(f,dur)=>{ for(let q=0;q<=dur;q+=1/60){ const [s1,h]=f(q), x=p.x+dx*s1, z=p.z+dz*s1;
          for(const s of LS){ const u=(x-H.TWC-F.c[0])*d[0]+(z-H.TWC-F.c[1])*d[1], ul=s.u+Math.sin((T0+q)*s.sp+s.ph)*s.amp; if(Math.abs(ul-u)<0.4 && h<0.45) return true; }
          for(const s of SP){ if(h>=0.62) continue; const a=-((T0+q)*s.sp+(s.ph||0)), ex=Math.cos(a), ez=Math.sin(a), rx=x-s.c[0], rz=z-s.c[1], tt=Math.max(-s.len,Math.min(s.len,rx*ex+rz*ez)); if(Math.hypot(rx-ex*tt, rz-ez*tt)<0.42) return true; } } return false; };
      const run=q=>[dist(q,16),0], jmp=q=>[dist(q,10), Math.max(0,9.3*q-13*q*q)], wait=q=>[vf*(1-Math.exp(-16*q))/16,0];
      const back=q=>[vf*(1-Math.exp(-16*q))/16-4.4*(q-(1-Math.exp(-16*q))/16),0];
      if(!hit(run,0.3)){ } else if(!hit(jmp,0.95)) T.buf=0.16; else if(!hit(wait,0.8)){ dx=dz=0; T.buf=0; } else if(!hit(back,0.4)){ dx=-dx; dz=-dz; T.buf=0; } else if(!hit(wait,0.3)){ dx=dz=0; T.buf=0; } else T.buf=0.16; } }   // (v454) 🔴 레이저 = 점프로 넘기
    if(T.secs[fl]==="wall"){ const B=T.S.slice(T.secR[fl][0],T.secR[fl][1]).find(s=>s.wallTop);   // (v454) 🧗 벽 점프: B 쪽으로 → 벽에 닿으면 반대쪽으로 JUMP
      if(T.onG && T.gnd && T.gnd.kind==="cp" && T.gnd.i===sec) T.buf=0;
      if(T.onG && T.gnd && T.gnd.wallTop) T.buf=0;   // (v466) 벽 위에 올라서면 멈춰서 다음 발판으로 걸어감   // 처음 발판 → 길은 이어져 있으니 걸어감 (점프하면 A 벽에 부딪힘)
      if(B && !(T.onG && (T.gnd===B || T.gnd.kind==="cp" || T.gnd.kind==="top"))){
        if(!T.onG && T.wallT>0 && T.wallN){ dx=T.wallN[0]; dz=T.wallN[1]; T.buf=0.16; }
        else if(T.onG){ const ex=(B.min.x+B.max.x)/2-p.x, ez=(B.min.z+B.max.z)/2-p.z, q=Math.hypot(ex,ez)||1; dx=ex/q; dz=ez/q; T.buf = gap(B,p)<0.3 ? 0.16 : 0; }
        else if(T._wd){ dx=T._wd[0]; dz=T._wd[1]; }
        T._wd=[dx,dz]; } }
    if(T.onG && T.gnd && T.gnd.ground!=null && (dx||dz)){ const C=6, ax=p.x-C, az=p.z-C, bx=cx-C, bz=cz-C; let hit=false; for(let q=0;q<=20;q++){ const x=ax+(bx-ax)*q/20, z=az+(bz-az)*q/20; if(Math.abs(x)<2.75 && Math.abs(z)<2.75) hit=true; }   // (v463) 🏝 땅 위: 가운데 기둥을 돌아서
      if(hit){ const a1=Math.atan2(az,ax), a2=Math.atan2(bz,bx); let da=((a2-a1+Math.PI*3)%(Math.PI*2))-Math.PI; const sg=da>=0?1:-1, r=Math.hypot(ax,az), tx=-az*sg/r, tz=ax*sg/r, out=(r<3.6?0.5:0); dx=tx+ax/r*out; dz=tz+az/r*out; const q=Math.hypot(dx,dz); dx/=q; dz/=q; } }
    if((T.secs[fl]==="sweep" || (T.secsB&&T.secsB[fl]==="sweep")) && T.onG && T.gnd && T.gnd.kind!=="floor"){ const S0=T.S.slice(T.secR[fl][0],T.secR[fl][1]), sw0=S0.find(s=>s.kind==="sweep" && (!s.seg || !s.seg.kind || (s.seg.kind==="sweep" && (!T.gnd.seg || s.seg===T.gnd.seg)))), S=sw0 ? S0.filter(s=>s.seg===sw0.seg && !s.conn) : [], SL=S.filter(s=>s.kind==="solid" && !s.noWalk), sw=(sw0 && (!sw0.seg || !T.gnd.seg || T.gnd.seg===sw0.seg)) ? sw0 : null;   // (v464) 🕐 입구 → (바늘이 멀 때) 가운데 → (바늘이 멀 때) 출구
      if(sw && Math.abs(p.y-sw.y0)<1.0){ const C=sw.c, rC=Math.hypot(p.x-C[0],p.z-C[1]), arr=ph=>{ const a=-sw.mesh.rotation.y, M=sw.len2>0?Math.PI:Math.PI*2, d=sw.sp>0?(((a-ph)%M)+M)%M:(((ph-a)%M)+M)%M; return d/Math.abs(sw.sp); }, ok=ph=>{ const M=(sw.len2>0?Math.PI:Math.PI*2)/Math.abs(sw.sp), t0=arr(ph); return t0>0.5 && M-t0>0.3; };
        const ex=SL[2], exC=[(ex.min.x+ex.max.x)/2,(ex.min.z+ex.max.z)/2], exAng=Math.atan2(exC[1]-C[1],exC[0]-C[0]), toEx=((p.x-C[0])*(exC[0]-C[0])+(p.z-C[1])*(exC[1]-C[1]))>0;
        let goal=null, safe=true;
        if(T.gnd===SL[0]){ goal=C; safe=ok(Math.atan2(p.z-C[1],p.x-C[0])); }
        else if(T.gnd===SL[1] && rC>0.28 && !toEx){ goal=C; }
        else if(T.gnd===SL[1] && rC<=0.28){ goal=exC; safe=ok(exAng); }
        else if(T.gnd===SL[1]){ goal=exC; }
        if(goal){ const gx=goal[0]-p.x, gz=goal[1]-p.z, q=Math.hypot(gx,gz)||1; if(safe && q>0.05){ dx=gx/q; dz=gz/q; } else { dx=dz=0; } T.buf=0; } } }
    if((T.secs[fl]==="sweep3" || (T.secsB&&T.secsB[fl]==="sweep3")) && T.onG && T.gnd && T.gnd.kind!=="floor"){ const S=T.S.slice(T.secR[fl][0],T.secR[fl][1]), SW=S.filter(s=>s.kind==="sweep" && (!s.seg || !s.seg.kind || (s.seg.kind==="sweep3" && (!T.gnd.seg || s.seg===T.gnd.seg)))), d=(SW[0]&&SW[0].seg)?SW[0].seg.d:H.TDIR[sec%4]; if(SW[0] && SW[0].seg && T.gnd.seg && T.gnd.seg!==SW[0].seg) SW.length=0;   // (v465) 🕐🕐🕐 앞 바늘 가운데 → (세 바늘 모두 멀 때) 뒤 두 바늘 사이 → 출구
      const A=SW[0], B=SW[1], Cc=SW[2]; if(A && Math.abs(p.y-A.y0)<1.0){ const arr=(sw,ph)=>{ const a=-sw.mesh.rotation.y, M=Math.PI*2, dd=sw.sp>0?(((a-ph)%M)+M)%M:(((ph-a)%M)+M)%M; return dd/Math.abs(sw.sp); }, ok=(sw,ph,tm)=>{ const M=Math.PI*2/Math.abs(sw.sp), t0=arr(sw,ph); return t0>tm && M-t0>0.3; }, ang=(c,q)=>Math.atan2(q[1]-c[1],q[0]-c[0]);
        const G=[(B.c[0]+Cc.c[0])/2,(B.c[1]+Cc.c[1])/2], al=q=>(q[0]-p.x)*d[0]+(q[1]-p.z)*d[1], rA=Math.hypot(p.x-A.c[0],p.z-A.c[1]); let goal=null, safe=true;
        if(rA<=0.28){ goal=[G[0]+d[0]*1.3, G[1]+d[1]*1.3]; safe=ok(A,ang(A.c,G),0.5) && ok(B,ang(B.c,G),0.95) && ok(Cc,ang(Cc.c,G),0.95); }
        else if(al(A.c)>0.05){ goal=A.c; safe=rA<1.45 || ok(A,ang(A.c,[p.x,p.z]),0.55); }
        else if(al(G)>-1.0){ goal=[G[0]+d[0]*1.3, G[1]+d[1]*1.3]; }
        if(goal){ const gx=goal[0]-p.x, gz=goal[1]-p.z, q=Math.hypot(gx,gz)||1; if(safe && q>0.05){ dx=gx/q; dz=gz/q; } else { dx=dz=0; } T.buf=0; } } }
    if((T.secs[fl]==="door" || (T.secsB&&T.secsB[fl]==="door")) && T.onG && T.gnd && T.gnd.kind!=="floor" && (()=>{ const dd=T.S.slice(T.secR[fl][0],T.secR[fl][1]).find(s=>s.kind==="door" && (!T.gnd.seg || s.seg===T.gnd.seg)); return !!dd && (!dd || !dd.seg || !T.gnd.seg || T.gnd.seg===dd.seg); })()){ const d0=T.S.slice(T.secR[fl][0],T.secR[fl][1]).find(s=>s.kind==="door" && (!T.gnd.seg || s.seg===T.gnd.seg)), d=(d0&&d0.seg)?d0.seg.d:H.TDIR[sec%4], D=T.S.slice(T.secR[fl][0],T.secR[fl][1]).filter(s=>s.kind==="door" && s.fake && (!T.gnd.seg || s.seg===T.gnd.seg)).map(s=>{ const cx=(s.min.x+s.max.x)/2, cz=(s.min.z+s.max.z)/2, al=(cx-p.x)*d[0]+(cz-p.z)*d[1], lx=cx-p.x-d[0]*al, lz=cz-p.z-d[1]*al; return {cx,cz,al,lat:Math.hypot(lx,lz),lx,lz}; }).filter(o=>o.al>-0.15);   // (v463) 🚪 가짜 문 쪽으로
      if(D.length){ const a0=Math.min(...D.map(o=>o.al)), o=D.filter(o=>o.al<a0+0.3).sort((x,y)=>x.lat-y.lat)[0]; if(o.lat>0.12 && o.al<0.75){ dx=o.lx/o.lat; dz=o.lz/o.lat; } else { const ex=o.cx+d[0]*0.6-p.x, ez=o.cz+d[1]*0.6-p.z, q=Math.hypot(ex,ez)||1; dx=ex/q; dz=ez/q; } T.buf=0; } }
    for(const s of T.S){ if(s.kind!=="pend" || s.bx==null || !T.onG || Math.abs(p.y-(s.py-3.4))>1.2) continue; const al=(s.G.position.x-p.x)*s.F.d[0]+(s.G.position.z-p.z)*s.F.d[1]; if(al>0.75 && al<1.45){ const wb=Math.sin(s.th)*s.L; if(!(Math.abs(wb)>0.95 && wb*s.vth>0)){ dx=dz=0; T.buf=0; } } }   // (v463) 🔨 공이 멀어질 때 지나감
    if(T.onG && T.gnd && T.gnd.seg && NJ.has(T.gnd.seg) && !tg.climb && NJ.get(T.gnd.seg).some(b=>{ const al=((b.min.x+b.max.x)/2-p.x)*dx+((b.min.z+b.max.z)/2-p.z)*dz; return al>-0.45 && al<3.4; })) T.buf=0;   // (v472) 머리 위 빨간 막대 = 점프 안 함
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
        # ①
        await E("()=>HOUSE.towerAsk()"); await until("()=>!!document.getElementById('twS')")
        r = await E("()=>[!!document.getElementById('twS'), !!document.getElementById('twE'), !!document.getElementById('twH'), document.getElementById('infoT').innerText]")
        ok(r[0] and not r[1] and not r[2] and "40층" in r[3] and "넓은 땅" in r[3], f"고르기 창 = 🗼 40층 하나 {r[:3]} {r[3][:90]!r}")
        await pg.screenshot(path=OUT + "tower459_ask.png")
        await E("()=>{ HOUSE.TW.seed='2026-10-30'; document.getElementById('twS').click(); }")
        ok(await until("()=>HOUSE.place()==='tower' && HOUSE.TW.on"), "🗼 → 타워 안")
        await pg.wait_for_timeout(600)
        r = await E("()=>[HOUSE.TW.mode, HOUSE.TW.cps.length-1, document.getElementById('twFloor').textContent, HOUSE.twNetPath().slice(-1)]")
        ok(r[0] == "sky" and r[1] == 40 and r[2].startswith("1 / 40") and r[3] == "s", f"40층 · 1 / 40층 · 친구 보기 경로 따로(s) {r}")
        # ②
        r = await E("""()=>{ const T=HOUSE.TW, E0=["steps","gaps","lava","mover","fade","bounce","beam","ice","laser","turn","crumble","brick","door","tiptoe","pend","sweep","sweep3"], out=[];
            for(let d=1; d<=6; d++){ T.seed='2026-11-'+d; HOUSE.twBuild('sky'); const s=T.secs; out.push([s.length, s[19], s.slice(0,9).every(k=>E0.includes(k)), s.filter(k=>k==='ground').length, T.ys.every((y,i)=>!i || y>T.ys[i-1]), T.secsB.slice(10).filter((b,j)=>b && s[10+j]!=='ground' && s[10+j]!=='wall').length]); }
            T.seed='2026-11-01'; HOUSE.twBuild('sky'); const a=T.secs.join()+T.hy.toFixed(2); HOUSE.twBuild('sky'); return [out, a===T.secs.join()+T.hy.toFixed(2), +T.hy.toFixed(1)]; }""")
        ok(all(x[0] == 40 and x[1] == "ground" and x[2] and x[3] == 1 and x[4] and x[5] == 28 for x in r[0]) and r[1], f"(v471) 1~9 쉬움 · 🏝 땅은 20층 하나 · 11층부터 한 층 = 장애물 2개(28층) · 높이 계속 올라감 · 같은 날 같음 (6일) 높이 {r[2]} {r[0][:2]}")
        # ③ 땅
        r = await E("""()=>{ const T=HOUSE.TW; T.seed='2026-10-30'; HOUSE.twBuild('sky'); const G=T.grounds, sz=G.map(g=>{ const L=T.S.filter(s=>s.ground===g.gi); return +(Math.max(...L.map(s=>s.max.x))-Math.min(...L.map(s=>s.min.x))).toFixed(1); });
            return [G.map(g=>g.gi), sz, G.map(g=>+(g.y-T.cps[g.gi].max.y).toFixed(2))]; }""")
        ok(r[0] == [19] and 13.5 < r[1][0] < 14.5 and r[2] == [0], f"(v471) 🏝 땅 = 20층 하나 · 작게(14) · 땅 높이 = 그 층 발판 {r}")
        # 위층(15층쯤) 바깥에서 떨어짐 → 🏝 10층 땅
        r = await E("""()=>{ const T=HOUSE.TW; T.bot=false; T.on=true; T.fin=false; T.gSeen={}; T.cp=24; HOUSE.setGems(0); const G=T.grounds[0], C=6; let res=[];
            const y0=T.ys[24]+0.5, free=[]; for(let a=0;a<64 && free.length<4;a++){ const ang=a/64*Math.PI*2+0.05, dx=Math.cos(ang)*6.9, dz=Math.sin(ang)*6.9, x=C+dx, z=C+dz; if(!T.S.some(s=>s.min && s.ground==null && s.kind!=='floor' && x+0.3>s.min.x && x-0.3<s.max.x && z+0.3>s.min.z && z-0.3<s.max.z && s.max.y>G.y+0.01 && s.min.y<y0+2)) free.push([dx,dz]); }
            for(const [dx,dz] of free){ T.p.set(C+dx, T.ys[24]+0.5, C+dz); T.v.set(0,0,0); T.lastGY=null; T.onG=false; T.gnd=null; let n=0; HOUSE.twStep(1/90); while(!(T.onG) && n<900){ HOUSE.twStep(1/90); n++; }
              res.push([T.gnd && T.gnd.ground, +(T.p.y-G.y).toFixed(2)]); } return [res, HOUSE.gems(), document.getElementById('toast').innerText]; }""")
        ok(len(r[0]) >= 3 and all(x[0] == 19 and abs(x[1]) < 0.03 for x in r[0]) and r[1] == 2 and "20층 넓은 땅" in r[2], f"25층 바깥에서 뚝 → 🏝 20층 땅에 내려앉음 · 💎 +2 처음만 {r}")
        await pg.wait_for_timeout(300); await pg.screenshot(path=OUT + "tower459_ground.png")
        # 밑에서는 투명
        r = await E("""()=>{ const T=HOUSE.TW, G=T.grounds[0], c=T.cps[15]; T.p.set((c.min.x+c.max.x)/2, c.max.y+0.01, (c.min.z+c.max.z)/2); T.v.set(0,0,0); HOUSE.twStep(1/90); const lo=G.mat.opacity;
            const g=T.cps[19]; T.p.set((g.min.x+g.max.x)/2, g.max.y+0.01, (g.min.z+g.max.z)/2); HOUSE.twStep(1/90); return [lo, G.mat.opacity, G.D.visible]; }""")
        ok(r[0] < 0.3 and r[1] == 1 and r[2], f"16층에서 = 땅이 비침 · 땅 위 = 보임 {r}")
        await pg.wait_for_timeout(300); await pg.screenshot(path=OUT + "tower459_onground.png")
        # ④ 레이저 · 🚩
        r = await E("""()=>{ const T=HOUSE.TW; T.bot=false; const c=T.cps[24]; T.p.set((c.min.x+c.max.x)/2, c.max.y+0.01, (c.min.z+c.max.z)/2); T.v.set(0,0,0); HOUSE.twStep(1/90); T.cp=24;
            T.twDie ? 0 : 0; const L={kind:'kill', on:true, min:new THREE.Vector3(T.p.x-1,T.p.y-0.2,T.p.z-1), max:new THREE.Vector3(T.p.x+1,T.p.y+0.5,T.p.z+1), mesh:new THREE.Object3D()}; T.S.push(L); HOUSE.twStep(1/90); T.S.pop();
            const g=T.cps[19], a=[+(T.p.y-g.max.y).toFixed(2), document.getElementById('toast').innerText, T.cp];
            const c2=T.cps[27]; T.p.set((c2.min.x+c2.max.x)/2, c2.max.y+0.01, (c2.min.z+c2.max.z)/2); HOUSE.twStep(1/90); document.getElementById('twRe').click(); const b=+(T.p.y-g.max.y).toFixed(2);
            const c3=T.cps[4]; T.p.set((c3.min.x+c3.max.x)/2, c3.max.y+0.01, (c3.min.z+c3.max.z)/2); HOUSE.twStep(1/90); document.getElementById('twRe').click(); return [a, b, +(T.p.y-T.cps[0].max.y).toFixed(2)]; }""")
        ok(abs(r[0][0]) < 0.05 and "20층 땅" in r[0][1] and r[0][2] == 24 and abs(r[1]) < 0.05 and abs(r[2]) < 0.05, f"25층 용암 → 🏝 20층 땅부터 · 🚩(28층) = 20층 땅 · 🚩(5층) = 맨 아래 {r}")
        # ⑤ 🤖
        res = []
        for seed in ["2026-11-%02d" % d for d in range(1, 6)]:
            r = await E(BOT, {"mode": "sky", "seed": seed, "max": 3000})
            res.append((seed, r["fin"], r["t"], r["dead"]) + (() if r["fin"] else (r["cp"], r["secs"][r["cp"]] if r["cp"] < len(r["secs"]) else "-")))
        fails = [x for x in res if not x[1]]
        ok(not fails, f"🤖 자동 선수가 40층 꼭대기까지 (5일) {fails[:3]} 평균 {sum(x[2] for x in res)/len(res):.0f}초")
        # ⑥ 이모티콘
        r = await E("""()=>{ HOUSE.TW.emoT=0; HOUSE.twEmote('❤️'); const cv=HOUSE.hero().emo.s.material.map.image, g=cv.getContext('2d'), d=g.getImageData(0,0,128,128).data; let x0=128,x1=-1,y0=128,y1=-1;
            for(let y=0;y<104;y++) for(let x=0;x<128;x++){ const i=(y*128+x)*4; if(d[i+3]>40 && !(d[i]>235 && d[i+1]>235 && d[i+2]>235)){ if(x<x0)x0=x; if(x>x1)x1=x; if(y<y0)y0=y; if(y>y1)y1=y; } }
            return [x0,x1,y0,y1, (x0+x1)/2, (y0+y1)/2]; }""")
        ok(r[1] > 0 and abs(r[4] - 64) <= 3 and abs(r[5] - 58) <= 4 and r[0] > 14 and r[1] < 114, f"😀 ❤️ 가 말풍선 가운데 · 안쪽 {r}")
        ok(not real_errs(errs), "오류 없음 " + str(real_errs(errs)[:3]))
        await br.close()
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)

asyncio.run(main())
