/* ═════════ (v590) 🟦 발판 게임 — LED 바닥 놀이
   사용자: 「2번은 발판 게임 — 초록색은 세이프티 존 · 파란색은 밟아서 지워야 하는 것 · 빨간색이 다가오면 점프하거나 피해야 해」
   규칙: 🟦 파란 칸을 모두 밟으면 다음 판 (점점 빨라짐) · 🟥 빨간 줄·고리·깜빡이가 다가옴 → 점프로 넘거나 피하기 · 🟩 초록 칸 = 빨강이 안 옴
         ❤️ 3개 · 빨강을 밟으면 ❤️ 하나 (잠깐 반짝이는 동안은 안전) · 한 판 60초 · 남은 시간 = 보너스
   조작: 왼손 = 아무 데나 끌어 움직이기 · 점프 버튼 / 키보드 WASD · 스페이스 */
(()=>{ if(typeof MG==="undefined" || typeof THREE==="undefined") return;
const V3=THREE.Vector3;
const N=10, TS=1.8, HALF=N*TS/2, GRAV=24, JV=7.4, SPD=6.2, STAGE_T=60;
const COL={off:0x252a5c, blue:0x2f8cff, green:0x2fd866, red:0xff2d55, warn:0xff9a3d, done:0x3a3f7a};

function start(api){
  const scene=new THREE.Scene(); scene.background=new THREE.Color(0x10123a); scene.fog=new THREE.Fog(0x10123a, 40, 80);
  const cam=new THREE.PerspectiveCamera(50, 1, .3, 200);
  scene.add(new THREE.HemisphereLight(0xdfe6ff, 0x2a2550, .7)); const sun=new THREE.DirectionalLight(0xffffff, .9); sun.position.set(-6,20,10); scene.add(sun); scene.add(sun.target);
  if(!api.low){ sun.castShadow=true; sun.shadow.mapSize.set(1024,1024); const c=sun.shadow.camera; c.left=c.bottom=-14; c.right=c.top=14; c.near=1; c.far=50; sun.shadow.bias=-0.001; }
  const toon=m=>{ try{ TOON.mat(m); }catch(e){} return m; };
  const disp=[];

  /* ── 방: 어두운 벽 · 빛 띠 · 바닥 칸(한 번에 그림) ── */
  { const g=new THREE.BoxGeometry(N*TS+3, .5, N*TS+3); disp.push(g); const m=new THREE.Mesh(g, toon(new THREE.MeshStandardMaterial({color:0x1a1d48, roughness:.9}))); m.position.y=-.26; m.receiveShadow=true; scene.add(m);
    const W=N*TS+3, wm=toon(new THREE.MeshStandardMaterial({color:0x22265e, roughness:.9})), nm=new THREE.MeshBasicMaterial({color:0x7fe0ff}), nm2=new THREE.MeshBasicMaterial({color:0xff6bd6});
    [[0,-W/2,W,.6],[0,W/2,W,.6],[-W/2,0,.6,W],[W/2,0,.6,W]].forEach(([x,z,w,d],i)=>{ const b=new THREE.Mesh(new THREE.BoxGeometry(w,1.2,d), wm); b.position.set(x,.35,z); scene.add(b); disp.push(b.geometry);
      const s=new THREE.Mesh(new THREE.BoxGeometry(w+.02,.08,d+.02), i%2?nm2:nm); s.position.set(x,.98,z); scene.add(s); disp.push(s.geometry); });
    /* 뒤 큰 화면 테두리 · 점 조명 */
    for(let i=0;i<26;i++){ const s=new THREE.Mesh(new THREE.SphereGeometry(.12,8,6), i%3?nm:nm2); const a=i/26*Math.PI*2; s.position.set(Math.cos(a)*22, 6+Math.sin(i*1.7)*2.5, Math.sin(a)*22-4); scene.add(s); disp.push(s.geometry); } }
  const TG=new THREE.BoxGeometry(TS*.9, .18, TS*.9); disp.push(TG);
  const TM=new THREE.MeshBasicMaterial({color:0xffffff}); const T=new THREE.InstancedMesh(TG, TM, N*N); T.instanceMatrix.setUsage(THREE.DynamicDrawUsage); scene.add(T);
  const _m=new THREE.Matrix4(), _c=new THREE.Color();
  const cx=i=>-HALF+TS*(i+.5);
  for(let j=0;j<N;j++) for(let i=0;i<N;i++){ _m.makeTranslation(cx(i), .02, cx(j)); T.setMatrixAt(j*N+i, _m); T.setColorAt(j*N+i, _c.setHex(COL.off)); }
  T.instanceColor.setUsage(THREE.DynamicDrawUsage);

  /* ── 나 (내 아바타) ── */
  let me=null; try{ me=buildAvatar(api.av); me.g.scale.setScalar(1.5); me.g.traverse(m=>{ if(m.isMesh) m.castShadow=!api.low; }); scene.add(me.g); }catch(e){ me=null; }
  const P={p:new V3(), vy:0, onG:true, inv:0, face:0};
  /* 내가 선 칸 = 흰 테두리 (어느 칸인지 바로 보임) */
  const HL=new THREE.Group(); { const hm=new THREE.MeshBasicMaterial({color:0xffffff}), a=TS*.92, t=.12; [[0,-a/2,a,t],[0,a/2,a,t],[-a/2,0,t,a],[a/2,0,t,a]].forEach(([x,z,w,d])=>{ const g=new THREE.BoxGeometry(w,.05,d); disp.push(g); const m=new THREE.Mesh(g,hm); m.position.set(x,.14,z); HL.add(m); }); } scene.add(HL);
  const shadowD=new THREE.Mesh(new THREE.CircleGeometry(.45,20), new THREE.MeshBasicMaterial({color:0x000000, transparent:true, opacity:.35, depthWrite:false})); shadowD.rotation.x=-Math.PI/2; scene.add(shadowD); disp.push(shadowD.geometry);

  /* ── 판 상태 ── */
  const st={stage:0, t:0, left:STAGE_T, lives:3, score:0, combo:0, comboT:0, blue:0, over:false, clearT:0, intro:2.4, hz:[], hzT:2.5, flash:0, best:0, steps:0};
  const cell=new Uint8Array(N*N);   /* 0 꺼짐 · 1 파랑 · 2 초록 · 3 지운 칸 */
  const red=new Float32Array(N*N), warn=new Float32Array(N*N);
  const rnd=(a,b)=>a+Math.random()*(b-a), ri=n=>Math.floor(Math.random()*n);
  function layout(){ cell.fill(0); const s=st.stage;
    /* 🟩 안전 칸: 처음엔 네 모서리 + 가운데 · 판이 오를수록 줄어듦 */
    const G=[[0,0],[N-1,0],[0,N-1],[N-1,N-1]]; if(s<3){ G.push([4,4],[5,5],[4,5],[5,4]); } else if(s<6){ G.push([4+ri(2),4+ri(2)]); } if(s<2){ G.push([0,1],[1,0],[N-1,N-2],[N-2,N-1],[0,N-2],[1,N-1],[N-1,1],[N-2,0]); }
    G.forEach(([i,j])=>cell[j*N+i]=2);
    const nb=Math.min(34, 12+s*4); let k=0, guard=0; while(k<nb && guard++<999){ const i=ri(N), j=ri(N); if(cell[j*N+i]) continue; cell[j*N+i]=1; k++; } st.blue=k; }
  function newStage(first){ if(!first) st.stage++; layout(); st.left=STAGE_T; st.hz=[]; st.hzT=first?3:2.2; st.clearT=0; red.fill(0); warn.fill(0);
    if(first){ P.p.set(cx(0),0,cx(N-1)); } api.msg('🟦 '+(st.stage+1)+' 판<small>파란 칸 '+st.blue+'개를 밟아 지워요!</small>', 1600); try{ api.sfx.up(); }catch(e){} drawHud(); }

  /* ── 빨강 무늬 ── w = 경고 시간, sp = 칸/초 */
  function spawnHz(){ const s=st.stage, sp=Math.min(3.6, 1.7+s*.22), kinds=["row","col","blink"]; if(s>=1) kinds.push("ring"); if(s>=2) kinds.push("cross"); if(s>=3) kinds.push("spin"); if(s>=4) kinds.push("row2");
    const k=kinds[ri(kinds.length)], w=Math.max(.75, 1.25-s*.06);
    if(k==="row"||k==="col"){ const dir=Math.random()<.5?1:-1; st.hz.push({k, dir, pos:dir>0?-.5:N-.5, sp, w, t:0}); }
    else if(k==="row2"){ st.hz.push({k:"row", dir:1, pos:-.5, sp, w, t:0}); st.hz.push({k:"row", dir:-1, pos:N-.5, sp, w, t:0}); }
    else if(k==="cross"){ st.hz.push({k:"row", dir:1, pos:-.5, sp:sp*.9, w, t:0}); st.hz.push({k:"col", dir:-1, pos:N-.5, sp:sp*.9, w, t:0}); }
    else if(k==="ring"){ const [ci,cj]=[1+ri(N-2),1+ri(N-2)]; st.hz.push({k, ci, cj, r:-.5, sp:sp*.85, w, t:0}); }
    else if(k==="blink"){ const L=[]; const n=Math.min(22, 6+s*2); for(let q=0;q<n;q++){ const i=ri(N), j=ri(N); if(cell[j*N+i]!==2) L.push(j*N+i); } st.hz.push({k, L, w:w+.25, on:1.3, t:0}); }
    else if(k==="spin"){ st.hz.push({k, a:Math.random()*6.28, sp:(Math.random()<.5?-1:1)*(.9+s*.06), dur:6.5, w, t:0}); }
    st.hzT=Math.max(1.3, 3.4-s*.25)+(k==="spin"?3:0); }
  function hzTick(dt){ red.fill(0); warn.fill(0);
    for(let n=st.hz.length-1;n>=0;n--){ const h=st.hz[n]; h.t+=dt; const warmup=h.t<h.w;
      if(h.k==="row"||h.k==="col"){ if(!warmup) h.pos+=h.dir*h.sp*dt; if(h.pos<-1.5 || h.pos>N+.5){ st.hz.splice(n,1); continue; }
        for(let a=0;a<N;a++){ const b=Math.round(h.pos); if(warmup){ const e=h.dir>0?0:N-1; const id=h.k==="row"?e*N+a:a*N+e; warn[id]=1; continue; } if(b<0||b>=N) continue; const id=h.k==="row"?b*N+a:a*N+b; red[id]=1; } }
      else if(h.k==="ring"){ if(!warmup) h.r+=h.sp*dt; if(h.r>N+1){ st.hz.splice(n,1); continue; } for(let j=0;j<N;j++) for(let i=0;i<N;i++){ const d=Math.max(Math.abs(i-h.ci),Math.abs(j-h.cj)); if(warmup){ if(d===0) warn[j*N+i]=1; } else if(Math.abs(d-h.r)<.5) red[j*N+i]=1; } }
      else if(h.k==="blink"){ if(h.t>h.w+h.on){ st.hz.splice(n,1); continue; } h.L.forEach(id=>{ if(warmup) warn[id]=1; else red[id]=1; }); }
      else if(h.k==="spin"){ if(h.t>h.w+h.dur){ st.hz.splice(n,1); continue; } if(!warmup) h.a+=h.sp*dt; const ca=Math.cos(h.a), sa=Math.sin(h.a), c0=(N-1)/2;
        for(let j=0;j<N;j++) for(let i=0;i<N;i++){ const x=i-c0, z=j-c0, along=x*ca+z*sa, perp=Math.abs(-x*sa+z*ca); if(perp<.62 && Math.abs(along)<N/2+.2){ if(warmup) warn[j*N+i]=1; else red[j*N+i]=1; } } } }
    for(let q=0;q<N*N;q++) if(cell[q]===2){ red[q]=0; warn[q]=0; } }

  /* ── 화면 글자 ── */
  const hud=api.hud;
  hud.innerHTML=`<style>
#mgUI .gTop{position:absolute;left:50%;top:calc(8px + env(safe-area-inset-top));transform:translateX(-50%);display:flex;gap:6px;align-items:center;pointer-events:none;flex-wrap:wrap;justify-content:center;max-width:calc(100vw - 150px)}
#mgUI .gTop span{background:rgba(10,14,50,.6);border-radius:12px;padding:4px 10px;font-size:16px;white-space:nowrap}
#mgUI .gTop .tm{font-family:var(--en);font-weight:900}
@media (max-width:480px){ #mgUI .gTop span{font-size:13.5px;padding:3px 7px} #mgUI .gTop{gap:4px} }
#mgUI .gTop .tm.low{background:#ff2d55}
#mgUI .gIntro{position:absolute;left:50%;top:62%;transform:translate(-50%,-50%);background:rgba(10,14,50,.82);border-radius:20px;padding:16px 18px;font-size:17px;line-height:1.7;pointer-events:none;text-align:left;border:2px solid rgba(127,224,255,.6);transition:opacity .3s;width:max-content;max-width:calc(100vw - 30px)}
#mgUI .gIntro b{display:inline-block;width:22px;height:22px;border-radius:6px;vertical-align:-4px;margin-right:6px}
#mgUI .gHurt{position:absolute;inset:0;pointer-events:none;background:radial-gradient(ellipse at center, rgba(255,45,85,0) 40%, rgba(255,45,85,.6) 100%);opacity:0;transition:opacity .15s}
#mgUI .gCombo{position:absolute;left:50%;top:22%;transform:translateX(-50%);font-size:24px;font-family:var(--en);font-weight:900;color:#7fe0ff;text-shadow:0 3px 0 rgba(0,0,0,.4);pointer-events:none;opacity:0;transition:opacity .2s}
#mgUI .mgB[data-b=jump]{right:max(22px,calc(env(safe-area-inset-right) + 14px));bottom:calc(36px + env(safe-area-inset-bottom));width:104px;height:104px;font-size:34px;background:rgba(47,140,255,.45)}
</style>
<div class="gHurt"></div><div class="gTop"><span class="sg"></span><span class="tm"></span><span class="lv"></span><span class="bl"></span><span class="sc"></span></div><div class="gCombo"></div>
<div class="gIntro"><div><b style="background:#2f8cff"></b>파란 칸 = 밟아서 지우기</div><div><b style="background:#ff2d55"></b>빨간 칸이 오면 = <b style="width:auto;height:auto;background:none;margin:0">⤒</b>점프로 넘거나 피하기</div><div><b style="background:#ff9a3d"></b>주황 깜빡 = 곧 빨강이 와요</div><div><b style="background:#2fd866"></b>초록 칸 = 안전 (빨강이 안 와요)</div></div>`;
  const Q=s=>hud.querySelector(s), eSg=Q(".sg"), eTm=Q(".tm"), eLv=Q(".lv"), eBl=Q(".bl"), eSc=Q(".sc"), eIn=Q(".gIntro"), eHurt=Q(".gHurt"), eCb=Q(".gCombo");
  function drawHud(){ eSg.textContent=(st.stage+1)+" 판"; eLv.textContent="❤️".repeat(Math.max(0,st.lives))+"🤍".repeat(Math.max(0,3-st.lives)); eBl.textContent="🟦 "+st.blue; eSc.textContent="⭐ "+st.score; }
  let tmS=-1; function drawTime(){ const s=Math.ceil(st.left); if(s===tmS) return; tmS=s; eTm.textContent="⏱ "+s; eTm.classList.toggle("low", s<=10); if(s<=5 && s>0 && !st.over) api.sfx.tick(); }

  /* ── 움직임 · 칸 밟기 ── */
  const camT=new V3(); let camInit=false, paused=false;
  function idxAt(x,z){ const i=Math.floor((x+HALF)/TS), j=Math.floor((z+HALF)/TS); if(i<0||j<0||i>=N||j>=N) return -1; return j*N+i; }
  function hit(){ if(P.inv>0 || st.over) return; st.lives--; P.inv=1.6; st.combo=0; st.flash=.5; api.sfx.bad(); drawHud();
    if(me){ try{ emote(me, "💦"); }catch(e){} }
    if(st.lives<=0){ end(false); return; } api.msg('앗! ❤️ '+st.lives+'개 남았어요<small>잠깐 반짝이는 동안은 안전해요</small>', 1200); }
  function step(dt){ const I=api.I;
    let mx=I.mx, mz=-I.my; const m=Math.hypot(mx,mz); if(m>1){ mx/=m; mz/=m; }
    P.p.x+=mx*SPD*dt; P.p.z+=mz*SPD*dt; const lim=HALF-.3; P.p.x=Math.max(-lim,Math.min(lim,P.p.x)); P.p.z=Math.max(-lim,Math.min(lim,P.p.z));
    if(m>.1) P.face=Math.atan2(mx,mz);
    if((I.jumpP || I.jump) && P.onG){ P.vy=JV; P.onG=false; api.sfx.jump(); }
    if(!P.onG){ P.vy-=GRAV*dt; P.p.y+=P.vy*dt; if(P.p.y<=0){ P.p.y=0; P.vy=0; P.onG=true; } }
    P.inv=Math.max(0,P.inv-dt);
    const id=idxAt(P.p.x,P.p.z);
    if(id>=0 && P.onG){
      if(cell[id]===1){ cell[id]=3; st.blue--; st.steps++; st.combo=st.comboT>0?st.combo+1:1; st.comboT=1.1; const pts=10+Math.min(10,(st.combo-1)*2); st.score+=pts; api.sfx.tile(st.combo); drawHud();
        if(st.combo>=3){ eCb.textContent="COMBO ×"+st.combo+" +"+pts; eCb.style.opacity=1; clearTimeout(eCb._t); eCb._t=setTimeout(()=>eCb.style.opacity=0, 700); }
        if(st.blue<=0){ const b=Math.ceil(st.left)*2+20; st.score+=b; st.clearT=2.2; st.hz=[]; api.sfx.clear(); api.msg('🎉 '+(st.stage+1)+' 판 깼다!<small>남은 시간 보너스 ⭐ +'+b+'</small>', 1900); drawHud(); } }
      if(red[id] && cell[id]!==2) hit(); }
    st.comboT=Math.max(0, st.comboT-dt); }
  function end(won){ if(st.over) return; st.over=true; const reached=st.stage+1;
    setTimeout(()=>{ api.end({title:st.lives>0?'⏰ 시간 끝!':'💦 ❤️ 다 썼어요', sub:reached+' 판까지 · ⭐ '+st.score+' · 지운 칸 '+st.steps, rows:null,
      extra:'<div class="sub" style="margin-top:10px;font-size:17px;color:#4b3527">'+(reached>=5?'🔥 대단해요!':reached>=3?'👍 잘했어요!':'다음엔 3판까지 가 봐요!')+'</div>',
      coins:reached>=5?15:reached>=3?10:5, upd:(b,t)=>{ if(st.score>(b.sc|0)) b.sc=st.score; if(reached>(b.st|0)) b.st=reached; t.tiles=(t.tiles|0)+st.steps; }}); }, 1100); }

  /* ── 한 장면 ── */
  function tick(dt){ if(paused) return; st.t+=dt;
    if(st.intro>0){ st.intro-=dt; eIn.style.opacity=st.intro>.3?1:0; } if(st.intro<=0 && eIn.style.display!=="none") eIn.style.display="none";
    if(!st.over){
      if(st.clearT>0){ st.clearT-=dt; if(st.clearT<=0) newStage(false); }
      else { st.left-=dt; if(st.left<=0){ st.left=0; end(false); } st.hzT-=dt; if(st.hzT<=0 && st.intro<=.5) spawnHz(); }
      hzTick(st.clearT>0?0:dt); step(dt); }
    drawTime();
    /* 칸 색 (빨강 > 경고 깜빡 > 파랑 > 초록 > 꺼짐) */
    const blink=(Math.sin(st.t*18)>0), pulse=.85+.15*Math.sin(st.t*5);
    for(let q=0;q<N*N;q++){ let c=COL.off, k=1; if(red[q]) c=COL.red; else if(warn[q]) c=blink?COL.warn:COL.off; else if(cell[q]===1){ c=COL.blue; k=pulse; } else if(cell[q]===2) c=COL.green; else if(cell[q]===3) c=COL.done; _c.setHex(c).convertSRGBToLinear(); if(k!==1) _c.multiplyScalar(k); T.setColorAt(q, _c); }
    T.instanceColor.needsUpdate=true;
    /* 나 */
    if(me){ me.g.position.copy(P.p); me.face=P.face; me.moving=P.onG && Math.hypot(api.I.mx,api.I.my)>.1; try{ animChar(me, dt); }catch(e){} me.g.visible=!(P.inv>0 && Math.sin(st.t*30)>0); }
    { const id=idxAt(P.p.x,P.p.z); HL.visible=id>=0; if(id>=0) HL.position.set(cx(id%N), 0, cx(Math.floor(id/N))); }
    shadowD.position.set(P.p.x,.13,P.p.z); shadowD.scale.setScalar(1-Math.min(.5,P.p.y*.3));
    st.flash=Math.max(0,st.flash-dt); eHurt.style.opacity=st.flash>0?1:0;
    /* 카메라 — 판 전체가 보이게 · 나를 살짝 따라감 */
    const asp=cam.aspect||1, port=asp<1, W=asp<.6?7.6:10.6, tv=Math.tan(cam.fov*Math.PI/360), d=Math.max(15, Math.min(38, W/(tv*Math.min(asp,1.45)))), pit=port?.92:.86;
    const fx=Math.max(0, HALF+1.2-W), tx=Math.max(-fx, Math.min(fx, P.p.x*.8)), tz=P.p.z*(asp<.6?.45:.25)+(asp<.6?1.6:asp<1?-.4:1.4); if(!camInit){ camT.set(tx,0,tz); camInit=true; } camT.x+=(tx-camT.x)*Math.min(1,dt*3); camT.z+=(tz-camT.z)*Math.min(1,dt*3);
    cam.position.set(camT.x, Math.sin(pit)*d, camT.z+Math.cos(pit)*d); cam.lookAt(camT.x, 0, camT.z); }
  newStage(true);
  function dispose(){ disp.forEach(x=>{ try{ x.dispose(); }catch(e){} }); }
  return {scene, cam, tick, dispose, pause:(v)=>{ paused=!!v; }, st, P, cell, red, warn, spawnHz, hzTick, newStage, idxAt, N, TS, HALF, cx}; }

MG.reg("grid", {ic:"🟦", nm:"발판 게임", tag:"LED 바닥 · 밟고 · 피하고 · 점프", bg:"linear-gradient(135deg,#252a5c,#10123a)", big:"🟦🟥🟩",
  how:[["🟦","<b>파란 칸</b>을 모두 밟으면 다음 판 (점점 빨라져요)"],["🟥","<b>빨간 줄·고리</b>가 오면 점프로 넘거나 피하기"],["🟧","주황 깜빡 = 곧 빨강이 와요"],["🟩","<b>초록 칸</b> = 안전 (빨강이 안 와요)"],["❤️","3번 맞으면 끝 · 한 판 60초 · 남은 시간은 보너스"]],
  payTxt:"5판 🪙15 · 3판 🪙10 · 참가 🪙5",
  bestTxt:(b,t)=>'🏆 최고 '+(b.st|0)+'판 · ⭐ '+(b.sc|0)+' · 지운 칸 모두 '+(t.tiles|0)+'개',
  ui:{look:false, btns:[{b:"jump", ic:"⤒", t:"점프"}]},
  start});
})();
