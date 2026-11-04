/* ═════════ (v590) 🟦 발판 게임 — LED 바닥 놀이
   사용자: 「2번은 발판 게임 — 초록색은 세이프티 존 · 파란색은 밟아서 지워야 하는 것 · 빨간색이 다가오면 점프하거나 피해야 해」
   규칙: 🟦 파란 칸을 모두 밟으면 다음 판 (점점 빨라짐) · 🟥 빨간 줄·고리·깜빡이가 다가옴 → 점프로 넘거나 피하기 · 🟩 초록 칸 = 빨강이 안 옴
         ❤️ 3개 · 빨강을 밟으면 ❤️ 하나 (잠깐 반짝이는 동안은 안전) · 한 판 60초
   (v594) 사용자: 「애들이랑 같이 하면 스테이지마다 안전한 지역이 변해야 하고 레이저 패턴도 달라져야 · 다 같이 최대 5명」
          → 「혼자 하기 · 같이 하기 · 대기방 · 방장이 게임 시작 → 10초 뒤 시작 · 순위 말고 같이 몇 점 얻었는지만」
   · 판 설계 plan(seed, 판) = 같은 번호면 모든 기기가 똑같은 판: 🟩 안전 칸 모양이 판마다 바뀜(모서리 → 가운데 십자 → 양옆 띠 → 섬 → 대각선 → 점점 적게) · 🟥 판마다 무늬 테마(줄 → 고리 → 회전 막대 → 십자+깜빡 → 양쪽 줄+고리 → 다 섞기)
   · 빨강은 「판이 시작된 뒤 몇 초」만으로 계산(상태 없음) → 같이 할 때 서버 시각(srvNow)으로 모두 같은 순간에 같은 빨강
   · 같이 하기: /hy/day/mgg<날>/<방>/{h:방 정보, p:아이들 위치, c:밟은 칸} · 위치 0.15초마다 · 방 읽기 0.3초마다 · 판 넘기기는 방장(나가면 남은 아이 중 하나)
   조작: 왼손 = 아무 데나 끌어 움직이기 · 점프 버튼 / 키보드 WASD · 스페이스 */
(()=>{ if(typeof MG==="undefined" || typeof THREE==="undefined") return;
const V3=THREE.Vector3;
const N=10, TS=1.8, HALF=N*TS/2, GRAV=24, JV=7.4, SPD=6.2, STAGE_T=60, MAXP=5, WAIT=10000;
const COL={off:0x252a5c, blue:0x2f8cff, green:0x2fd866, red:0xff2d55, warn:0xff9a3d, done:0x3a3f7a};

/* ── 같은 번호 = 같은 판 ── */
function RNG(seed){ let s=(seed>>>0)||0x9e3779b9; return ()=>{ s^=s<<13; s>>>=0; s^=s>>>17; s^=s<<5; s>>>=0; return s/4294967296; }; }
const mix=(a,b)=>{ let h=(a^0x45d9f3b)>>>0; h=Math.imul(h^(b+0x9e3779b9),0x85ebca6b)>>>0; h^=h>>>13; h=Math.imul(h,0xc2b2ae35)>>>0; return (h^(h>>>16))>>>0; };
const GREEN_T=["🟩 네 모서리","🟩 가운데 십자","🟩 양옆 띠","🟩 작은 섬 4개","🟩 대각선 징검다리","🟩 몇 칸만"];
const HZ_T=["🟥 줄이 지나가요","🟥 고리가 퍼져요","🟥 막대가 돌아요","🟥 십자 + 깜빡","🟥 양쪽에서 줄 + 고리","🟥 다 섞여요!"];
function plan(seed, s){ const R=RNG(mix(seed, s*7919+13)), ri=n=>Math.floor(R()*n), cell=new Uint8Array(N*N), G=[];
  const put=(i,j)=>{ if(i>=0&&j>=0&&i<N&&j<N && !cell[j*N+i]){ cell[j*N+i]=2; G.push(j*N+i); } };
  const th=s<5 ? s : 5;
  if(th===0){ [[0,0],[N-2,0],[0,N-2],[N-2,N-2]].forEach(([a,b])=>{ put(a,b); put(a+1,b); put(a,b+1); put(a+1,b+1); }); }
  else if(th===1){ [[4,4],[5,4],[4,5],[5,5],[3,4],[6,5],[4,3],[5,6]].forEach(([a,b])=>put(a,b)); [[0,0],[N-1,N-1]].forEach(([a,b])=>put(a,b)); }
  else if(th===2){ for(let j=3;j<=6;j++){ put(0,j); put(N-1,j); } }
  else if(th===3){ let k=0, g=0; while(k<4 && g++<99){ const a=1+ri(N-3), b=1+ri(N-3); if([0,1].some(x=>[0,1].some(y=>cell[(b+y)*N+a+x]))) continue; put(a,b); put(a+1,b); put(a,b+1); put(a+1,b+1); k++; } }
  else if(th===4){ for(let i=1;i<N;i+=2){ put(i,i); put(N-1-i,i); } }
  else { const n=Math.max(3, 7-Math.floor((s-5)/2)); let g=0; while(G.length<n && g++<99) put(ri(N), ri(N)); }
  const nb=Math.min(34, 12+s*4); let k=0, guard=0; while(k<nb && guard++<999){ const q=ri(N*N); if(cell[q]) continue; cell[q]=1; k++; }
  /* 빨강 시간표 (판 시작 뒤 초) */
  const PAL=[["row","col"],["ring","row","col"],["spin","row","col"],["cross","blink"],["row2","ring"],["row","col","ring","blink","cross","spin","row2"]][th];
  const sp=Math.min(3.6, 1.7+s*.22), w=Math.max(.75, 1.25-s*.06), H=[]; let t=2.6;
  while(t<STAGE_T){ const kd=PAL[ri(PAL.length)];
    if(kd==="row"||kd==="col"){ H.push({t0:t, k:kd, dir:R()<.5?1:-1, sp, w}); }
    else if(kd==="row2"){ H.push({t0:t, k:"row", dir:1, sp, w}); H.push({t0:t, k:"row", dir:-1, sp, w}); }
    else if(kd==="cross"){ H.push({t0:t, k:"row", dir:1, sp:sp*.9, w}); H.push({t0:t, k:"col", dir:-1, sp:sp*.9, w}); }
    else if(kd==="ring"){ H.push({t0:t, k:"ring", ci:1+ri(N-2), cj:1+ri(N-2), sp:sp*.85, w}); }
    else if(kd==="blink"){ const L=[]; const n=Math.min(22, 6+s*2); for(let q=0;q<n;q++){ const z=ri(N*N); if(cell[z]!==2) L.push(z); } H.push({t0:t, k:"blink", L, w:w+.25, on:1.3}); }
    else if(kd==="spin"){ H.push({t0:t, k:"spin", a:R()*6.28, sp:(R()<.5?-1:1)*(.9+s*.06), dur:6.5, w}); }
    t+=Math.max(1.3, 3.4-s*.25)+(kd==="spin"?3:0)+R()*.5; }
  return {cell, G, H, blue:k, th}; }
/* 판 시작 뒤 el 초의 빨강·경고 (상태 없음 = 모두 같음) */
function hzAt(H, el, cell, red, warn){ red.fill(0); warn.fill(0);
  for(const h of H){ const t=el-h.t0; if(t<0) continue; const wu=t<h.w, u=t-h.w;
    if(h.k==="row"||h.k==="col"){ const pos=h.dir>0 ? -.5+u*h.sp : N-.5-u*h.sp; if(!wu && (pos<-1.5||pos>N+.5)) continue; const b=Math.round(pos), e=h.dir>0?0:N-1;
      for(let a=0;a<N;a++){ if(wu){ warn[h.k==="row"?e*N+a:a*N+e]=1; continue; } if(b<0||b>=N) continue; red[h.k==="row"?b*N+a:a*N+b]=1; } }
    else if(h.k==="ring"){ const r=-.5+u*h.sp; if(!wu && r>N+1) continue; for(let j=0;j<N;j++) for(let i=0;i<N;i++){ const d=Math.max(Math.abs(i-h.ci),Math.abs(j-h.cj)); if(wu){ if(d===0) warn[j*N+i]=1; } else if(Math.abs(d-r)<.5) red[j*N+i]=1; } }
    else if(h.k==="blink"){ if(t>h.w+h.on) continue; h.L.forEach(id=>{ if(wu) warn[id]=1; else red[id]=1; }); }
    else if(h.k==="spin"){ if(t>h.w+h.dur) continue; const a=h.a+(wu?0:h.sp*u), ca=Math.cos(a), sa=Math.sin(a), c0=(N-1)/2;
      for(let j=0;j<N;j++) for(let i=0;i<N;i++){ const x=i-c0, z=j-c0, along=x*ca+z*sa, perp=Math.abs(-x*sa+z*ca); if(perp<.62 && Math.abs(along)<N/2+.2){ if(wu) warn[j*N+i]=1; else red[j*N+i]=1; } } } }
  for(let q=0;q<N*N;q++) if(cell[q]===2){ red[q]=0; warn[q]=0; } }

function start(api){
  const CO=api.opt.mode==="co";
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
    for(let i=0;i<26;i++){ const s=new THREE.Mesh(new THREE.SphereGeometry(.12,8,6), i%3?nm:nm2); const a=i/26*Math.PI*2; s.position.set(Math.cos(a)*22, 6+Math.sin(i*1.7)*2.5, Math.sin(a)*22-4); scene.add(s); disp.push(s.geometry); } }
  const TG=new THREE.BoxGeometry(TS*.9, .18, TS*.9); disp.push(TG);
  const TM=new THREE.MeshBasicMaterial({color:0xffffff}); const T=new THREE.InstancedMesh(TG, TM, N*N); T.instanceMatrix.setUsage(THREE.DynamicDrawUsage); scene.add(T);
  const _m=new THREE.Matrix4(), _c=new THREE.Color();
  const cx=i=>-HALF+TS*(i+.5);
  for(let j=0;j<N;j++) for(let i=0;i<N;i++){ _m.makeTranslation(cx(i), .02, cx(j)); T.setMatrixAt(j*N+i, _m); T.setColorAt(j*N+i, _c.setHex(COL.off)); }
  T.instanceColor.setUsage(THREE.DynamicDrawUsage);

  /* ── 캐릭터 (나 · 같이 하는 친구) ── */
  function avatar(o, k){ let c=null; try{ c=buildAvatar(o||{}); c.t=0; c.blinkT=2; c.face=0; c.act="idle"; c.g.scale.setScalar(k||1.8); c.g.traverse(m=>{ if(m.isMesh) m.castShadow=!api.low; }); scene.add(c.g); }catch(e){ c=null; } return c; }   /* (v593) t 가 없으면 걸을 때 NaN → 캐릭터가 사라짐 */
  function tag(nm){ const cv=document.createElement("canvas"); cv.width=256; cv.height=64; const g=cv.getContext("2d"); g.font="800 30px Jua, Nunito, sans-serif"; g.textAlign="center"; g.lineWidth=7; g.strokeStyle="rgba(10,14,50,.85)"; g.strokeText(nm,128,42); g.fillStyle="#fff"; g.fillText(nm,128,42);
    const tx=new THREE.CanvasTexture(cv); tx.encoding=THREE.sRGBEncoding; disp.push(tx); const sp=new THREE.Sprite(new THREE.SpriteMaterial({map:tx, depthWrite:false, transparent:true})); sp.scale.set(2.4,.6,1); scene.add(sp); return sp; }
  const me=avatar(api.av);
  const P={p:new V3(), vy:0, onG:true, inv:0, face:0};
  const HL=new THREE.Group(); { const hm=new THREE.MeshBasicMaterial({color:0xffffff}), a=TS*.92, t=.12; [[0,-a/2,a,t],[0,a/2,a,t],[-a/2,0,t,a],[a/2,0,t,a]].forEach(([x,z,w,d])=>{ const g=new THREE.BoxGeometry(w,.05,d); disp.push(g); const m=new THREE.Mesh(g,hm); m.position.set(x,.14,z); HL.add(m); }); } scene.add(HL);
  const shadowD=new THREE.Mesh(new THREE.CircleGeometry(.45,20), new THREE.MeshBasicMaterial({color:0x000000, transparent:true, opacity:.35, depthWrite:false})); shadowD.rotation.x=-Math.PI/2; scene.add(shadowD); disp.push(shadowD.geometry);

  /* ── 판 상태 ── */
  const st={stage:0, t:0, el:0, left:STAGE_T, lives:3, score:0, combo:0, comboT:0, blue:0, over:false, clearT:0, intro:CO?0:2.4, flash:0, steps:0, seed:(Math.random()*4294967296)>>>0, pl:null, phase:CO?"room":"play", out:false, cleared:0};
  const cell=new Uint8Array(N*N);   /* 0 꺼짐 · 1 파랑 · 2 초록 · 3 지운 칸 */
  const red=new Float32Array(N*N), warn=new Float32Array(N*N);
  function nearGreen(){ const G=st.pl?st.pl.G:[]; if(!G.length) return [cx(0),cx(N-1)]; let best=G[0], bd=1e9; G.forEach(q=>{ const d=Math.hypot(cx(q%N)-P.p.x, cx(Math.floor(q/N))-P.p.z); if(d<bd){ bd=d; best=q; } }); return [cx(best%N), cx(Math.floor(best/N))]; }
  function newStage(s, first){ st.stage=s; st.pl=plan(st.seed, s); cell.set(st.pl.cell); st.blue=st.pl.blue; st.el=0; st.left=STAGE_T; st.clearT=0; red.fill(0); warn.fill(0);
    if(st.out){ st.out=false; st.lives=3; P.inv=1.5; }   /* 같이 하기: 구경하던 아이 = 다음 판에 ❤️3 으로 다시 */
    if(first || CO){ const g=nearGreen(); P.p.set(g[0],0,g[1]); }
    api.msg('🟦 '+(s+1)+' 판<small>'+GREEN_T[st.pl.th]+' · '+HZ_T[st.pl.th]+'</small>', 1900); try{ api.sfx.up(); }catch(e){} drawHud(); }

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
#mgUI .mgB[data-b=jump]{right:max(22px,calc(env(safe-area-inset-right) + 14px));bottom:calc(36px + env(safe-area-inset-bottom));width:104px;height:104px;font-size:20px;background:rgba(47,140,255,.45)}
#mgUI .gRoom{position:absolute;left:50%;top:calc(58px + env(safe-area-inset-top));transform:translateX(-50%);width:min(380px,calc(100vw - 24px));background:rgba(10,14,50,.86);border:2px solid rgba(127,224,255,.55);border-radius:20px;padding:12px 14px;pointer-events:auto;text-align:center;font-size:16px}
#mgUI .gRoom h4{margin:0 0 6px;font-size:20px;font-weight:400}
#mgUI .gRoom .sub{font-size:13.5px;opacity:.85;margin:4px 0}
#mgUI .gRoom button{font:inherit;border:0;border-radius:14px;padding:10px 14px;margin:5px 3px 0;min-height:46px;background:#2f8cff;color:#fff;font-size:16px}
#mgUI .gRoom button.go{background:#2fd866;color:#10123a}
#mgUI .gRoom button.gr{background:rgba(255,255,255,.18)}
#mgUI .gRoom .rl{display:flex;flex-direction:column;gap:6px;margin:8px 0;max-height:34vh;overflow:auto}
#mgUI .gRoom .rl button{margin:0;width:100%;text-align:left;background:rgba(255,255,255,.12)}
#mgUI .gRoom .pl{display:flex;flex-wrap:wrap;gap:6px;justify-content:center;margin:8px 0}
#mgUI .gRoom .pl span{background:rgba(255,255,255,.14);border-radius:12px;padding:5px 10px}
#mgUI .gRoom .pl span.me{background:#ff8466}
#mgUI .gCnt{position:absolute;left:50%;top:40%;transform:translate(-50%,-50%);font-size:84px;font-family:var(--en);font-weight:900;text-shadow:0 5px 0 rgba(0,0,0,.35);pointer-events:none}
#mgUI .gOut{position:absolute;left:50%;bottom:calc(150px + env(safe-area-inset-bottom));transform:translateX(-50%);background:rgba(10,14,50,.8);border-radius:14px;padding:8px 14px;font-size:15px;pointer-events:none;display:none;white-space:nowrap}
</style>
<div class="gHurt"></div><div class="gTop"><span class="sg"></span><span class="tm"></span><span class="lv"></span><span class="bl"></span><span class="sc"></span></div><div class="gCombo"></div><div class="gCnt"></div><div class="gOut">👀 구경 중 — 다음 판에 ❤️3 으로 다시 들어가요</div><div class="gRoom" style="display:none"></div>
<div class="gIntro"><div><b style="background:#2f8cff"></b>파란 칸 = 밟아서 지우기</div><div><b style="background:#ff2d55"></b>빨간 칸이 오면 = <b style="width:auto;height:auto;background:none;margin:0">⤒</b>점프로 넘거나 피하기</div><div><b style="background:#ff9a3d"></b>주황 깜빡 = 곧 빨강이 와요</div><div><b style="background:#2fd866"></b>초록 칸 = 안전 (판마다 자리가 바뀌어요)</div></div>`;
  const Q=s=>hud.querySelector(s), eSg=Q(".sg"), eTm=Q(".tm"), eLv=Q(".lv"), eBl=Q(".bl"), eSc=Q(".sc"), eIn=Q(".gIntro"), eHurt=Q(".gHurt"), eCb=Q(".gCombo"), eRoom=Q(".gRoom"), eCnt=Q(".gCnt"), eOut=Q(".gOut");
  if(CO) eIn.style.display="none";
  function drawHud(){ eSg.textContent=st.phase==="play"?(st.stage+1)+" 판":CO?"👫 같이 하기":"🟦"; eLv.textContent="❤️".repeat(Math.max(0,st.lives))+"🤍".repeat(Math.max(0,3-st.lives)); eBl.textContent="🟦 "+st.blue; eSc.textContent=(CO?"🤝 ":"⭐ ")+st.score; }
  let tmS=-1; function drawTime(){ const s=Math.ceil(st.left); if(s===tmS) return; tmS=s; eTm.textContent="⏱ "+s; eTm.classList.toggle("low", s<=10); if(s<=5 && s>0 && !st.over && st.phase==="play") api.sfx.tick(); }

  /* ══════════ 👫 같이 하기 (방 · 대기 · 동기화) ══════════ */
  const NETOK=typeof NET!=="undefined", code=(()=>{ try{ return myCode; }catch(e){ return "ME"+Math.floor(Math.random()*999); } })(), nm=api.nick;
  const now=()=>{ try{ return srvNow(); }catch(e){ return Date.now(); } };
  const day=()=>{ try{ return dayKey().replace(/\D/g,""); }catch(e){ return "0"; } };
  const BASE=()=>"/hy/day/mgg"+day();
  const R={id:null, path:null, d:null, peers:{}, sendT:0, pollT:0, listT:0, rooms:[], busy:false, host:false, lastSent:null, gone:false, endSent:false};
  function roomUI(){ if(!CO) return; if(st.phase!=="room" && st.phase!=="wait"){ eRoom.style.display="none"; return; } eRoom.style.display="";
    if(st.phase==="room"){ const L=R.rooms;
      eRoom.innerHTML='<h4>👫 같이 하기 <small style="font-size:13px;opacity:.8">(최대 '+MAXP+'명)</small></h4><div class="sub">친구 방에 들어가거나, 내 방을 만들어요</div><div class="rl">'+(L.length?L.map(r=>'<button data-j="'+r.id+'">🟦 '+esc(r.n)+'의 방 · '+r.c+'/'+MAXP+'명</button>').join(""):'<div class="sub">아직 열린 방이 없어요</div>')+'</div><button class="go" data-mk="1">＋ 내 방 만들기</button>'; }
    else { const d=R.d||{}, h=d.h||{}, ps=livePeers(true), cnt=ps.length, st0=h.st||0;
      eRoom.innerHTML='<h4>🟦 '+esc(h.n||"")+'의 방</h4><div class="pl">'+ps.map(p=>'<span class="'+(p.k===code?"me":"")+'">'+(p.k===h.c?"👑 ":"")+esc(p.n)+'</span>').join("")+'</div><div class="sub">'+cnt+' / '+MAXP+'명 · 기다리는 동안 바닥에서 걸어 봐요</div>'+
        (st0?'<div class="sub">곧 시작해요!</div>':R.host?'<button class="go" data-st="1">▶ 게임 시작 (10초 뒤)</button>':'<div class="sub">방장(👑)이 「게임 시작」을 누르면 10초 뒤 시작해요</div>')+'<button class="gr" data-lv="1">방 나가기</button>'; } }
  const esc=s=>String(s==null?"":s).replace(/[<>&"]/g,c=>({"<":"&lt;",">":"&gt;","&":"&amp;",'"':"&quot;"}[c]));
  eRoom.addEventListener("click", e=>{ const b=e.target.closest("button"); if(!b || R.busy) return; if(b.dataset.mk) mkRoom(); else if(b.dataset.j) joinRoom(b.dataset.j); else if(b.dataset.st) startRoom(); else if(b.dataset.lv) leaveRoom(true); });
  eRoom.addEventListener("pointerdown", e=>e.stopPropagation());
  function meNode(){ return {n:nm, av:api.av||{}, x:+P.p.x.toFixed(2), z:+P.p.z.toFixed(2), y:+P.p.y.toFixed(2), f:+P.face.toFixed(2), l:st.lives, o:st.out?1:0, t:now()}; }
  async function listRooms(){ if(!NETOK) return; let d=null; try{ d=await NET.get(BASE()); }catch(e){ return; } const t=now(), L=[];
    Object.keys(d||{}).forEach(id=>{ const r=d[id]; if(!r || !r.h || r.h.st) return; if(t-(r.h.hb||0)>15000) return; const c=Object.values(r.p||{}).filter(p=>p && t-(p.t||0)<10000).length; if(c<MAXP) L.push({id, n:r.h.n||"친구", c}); });
    R.rooms=L.sort((a,b)=>b.c-a.c).slice(0,6); if(st.phase==="room") roomUI(); }
  async function mkRoom(){ if(!NETOK){ api.msg("서버에 연결이 안 돼요<small>혼자 하기로 해 봐요</small>", 1800); return; } R.busy=true; const id=code+"_"+(Date.now()%100000);
    R.id=id; R.path=BASE()+"/"+id; R.host=true; const h={c:code, n:nm, st:0, hb:now(), at:now()};
    try{ await NET.put(R.path, {h, p:{[code]:meNode()}}); }catch(e){} R.d={h, p:{[code]:meNode()}}; st.phase="wait"; R.busy=false; roomUI(); }
  async function joinRoom(id){ R.busy=true; const path=BASE()+"/"+id; let d=null; try{ d=await NET.get(path); }catch(e){}
    const t=now(), c=d && d.p ? Object.values(d.p).filter(p=>p && t-(p.t||0)<10000).length : 0;
    if(!d || !d.h || d.h.st || c>=MAXP){ R.busy=false; api.msg(d && d.h && d.h.st?"이미 시작한 방이에요":"방이 꽉 찼어요 (최대 "+MAXP+"명)", 1500); listRooms(); return; }
    R.id=id; R.path=path; R.host=false; R.d=d; try{ await NET.put(path+"/p/"+code, meNode()); }catch(e){} st.phase="wait"; R.busy=false; roomUI(); }
  async function startRoom(){ if(!R.host || !R.path) return; const at=now()+WAIT, seed=(Math.random()*4294967296)>>>0;
    try{ await NET.patch(R.path+"/h", {st:at, seed, sg:{s:0, at}}); }catch(e){} R.d.h=Object.assign({}, R.d.h, {st:at, seed, sg:{s:0, at}}); roomUI(); }
  function leaveRoom(toList){ if(R.path && NETOK){ try{ NET.del(R.path+"/p/"+code).catch(()=>{}); }catch(e){} if(R.host && st.phase==="wait"){ try{ NET.del(R.path).catch(()=>{}); }catch(e){} } }
    Object.values(R.peers).forEach(pp=>dropPeer(pp)); R.peers={}; R.id=R.path=null; R.d=null; R.host=false; if(toList){ st.phase="room"; listRooms(); roomUI(); drawHud(); } }
  function livePeers(withMe){ const d=R.d||{}, t=now(), L=[]; Object.keys(d.p||{}).forEach(k=>{ const p=d.p[k]; if(!p) return; if(k!==code && t-(p.t||0)>10000) return; if(!withMe && k===code) return; L.push(Object.assign({k}, p)); }); if(withMe && !L.some(p=>p.k===code)) L.push(Object.assign({k:code}, meNode())); return L.sort((a,b)=>a.k<b.k?-1:1); }
  function dropPeer(pp){ if(pp.c) scene.remove(pp.c.g); if(pp.tag) scene.remove(pp.tag); }
  function authority(){ const d=R.d||{}, h=d.h||{}, L=livePeers(true).map(p=>p.k); if(L.indexOf(h.c)>=0) return h.c===code; return L[0]===code; }   /* 방장이 나가면 남은 아이 중 첫 번째가 판을 넘김 */
  async function poll(){ if(!R.path || R.busy) return; let d=null; try{ d=await NET.get(R.path); }catch(e){ return; } if(!R.path) return;
    if(!d || !d.h){ if(st.phase==="wait"){ api.msg("방이 닫혔어요", 1400); leaveRoom(true); } return; } R.d=d; applyRoom(); }
  function applyRoom(){ const d=R.d, h=d.h, t=now();
    /* 친구 모습 */
    const seen={}; Object.keys(d.p||{}).forEach(k=>{ if(k===code) return; const p=d.p[k]; if(!p || t-(p.t||0)>10000) return; seen[k]=1; let pp=R.peers[k];
      if(!pp){ pp=R.peers[k]={c:avatar(p.av, 1.6), tag:tag(p.n||"친구"), x:p.x||0, z:p.z||0, y:0}; } pp.tx=p.x||0; pp.tz=p.z||0; pp.ty=p.y||0; pp.f=p.f||0; pp.o=!!p.o; pp.n=p.n; });
    Object.keys(R.peers).forEach(k=>{ if(!seen[k]){ dropPeer(R.peers[k]); delete R.peers[k]; } });
    if(st.phase==="wait"){ if(h.st){ st.seed=h.seed>>>0; st.phase="count"; } roomUI(); drawHud(); }
    if(st.phase==="play" && h.sg && h.sg.s>st.stage && t>=h.sg.at) newStage(h.sg.s);
    /* 밟은 칸 (모두의 것) */
    if(st.phase==="play"){ const pre=st.stage+"_"; let n=0; Object.keys(d.c||{}).forEach(key=>{ if(key.indexOf(pre)!==0) return; const q=+key.slice(pre.length); if(cell[q]===1){ cell[q]=3; st.blue--; } });
      teamScore(); drawHud(); }
    if(h.end && !st.over) end(); }
  function teamScore(){ const d=R.d||{}; let n=0; Object.keys(d.c||{}).forEach(()=>n++); const h=d.h||{}; st.score=n*10+((h.sg && h.sg.s)|0)*50; }
  function netTick(dt){ if(!CO || !NETOK) return;
    if(st.phase==="room"){ R.listT-=dt; if(R.listT<=0){ R.listT=1.5; listRooms(); } return; }
    if(!R.path) return;
    R.sendT-=dt; if(R.sendT<=0){ R.sendT=.15; const m=meNode(), s=R.lastSent; if(!s || Math.abs(s.x-m.x)+Math.abs(s.z-m.z)+Math.abs(s.y-m.y)>.05 || s.l!==m.l || s.o!==m.o || m.t-s.t>1500){ R.lastSent=m; NET.put(R.path+"/p/"+code, m).catch(()=>{}); } }
    R.pollT-=dt; if(R.pollT<=0){ R.pollT=.3; poll(); }
    if(R.host && st.phase==="wait"){ R.hbT=(R.hbT||0)-dt; if(R.hbT<=0){ R.hbT=3; NET.put(R.path+"/h/hb", now()).catch(()=>{}); } }
    /* 판 넘기기 · 끝 (방장) */
    if(st.phase==="play" && authority() && R.d && R.d.h){ const h=R.d.h;
      if(st.blue<=0 && !(h.sg && h.sg.s>st.stage)){ const sg={s:st.stage+1, at:now()+2600}; h.sg=sg; NET.put(R.path+"/h/sg", sg).catch(()=>{}); }
      const ps=livePeers(true); if(!R.endSent && ps.length && ps.every(p=>p.k===code ? st.out : !!p.o)){ R.endSent=true; NET.put(R.path+"/h/end", 1).catch(()=>{}); end(); } } }
  function peersTick(dt){ Object.values(R.peers).forEach(pp=>{ pp.x+=(pp.tx-pp.x)*Math.min(1,dt*10); pp.z+=(pp.tz-pp.z)*Math.min(1,dt*10); pp.y+=(pp.ty-pp.y)*Math.min(1,dt*14);
    if(pp.c){ const mv=Math.hypot(pp.tx-pp.x,pp.tz-pp.z)>.05; pp.c.g.position.set(pp.x,pp.y,pp.z); pp.c.face=pp.f; pp.c.moving=mv && pp.y<.05; try{ animChar(pp.c, dt); }catch(e){} pp.c.g.visible=!pp.o; }
    if(pp.tag){ pp.tag.position.set(pp.x, pp.y+(pp.o?.6:2.55), pp.z); pp.tag.material.opacity=pp.o?.5:1; } }); }

  /* ── 움직임 · 칸 밟기 ── */
  const camT=new V3(); let camInit=false, paused=false;
  function idxAt(x,z){ const i=Math.floor((x+HALF)/TS), j=Math.floor((z+HALF)/TS); if(i<0||j<0||i>=N||j>=N) return -1; return j*N+i; }
  function hit(){ if(P.inv>0 || st.over || st.out) return; st.lives--; P.inv=1.6; st.combo=0; st.flash=.5; api.sfx.bad(); drawHud();
    if(me){ try{ emote(me, "💦"); }catch(e){} }
    if(st.lives<=0){ if(CO){ st.out=true; api.msg('👀 ❤️ 다 썼어요<small>친구들을 응원하다가 다음 판에 다시 들어가요</small>', 2000); return; } end(); return; }
    api.msg('앗! ❤️ '+st.lives+'개 남았어요<small>잠깐 반짝이는 동안은 안전해요</small>', 1200); }
  function clearTile(id){ cell[id]=3; st.blue--; st.steps++; st.combo=st.comboT>0?st.combo+1:1; st.comboT=1.1; api.sfx.tile(st.combo);
    if(CO){ if(R.path){ R.d.c=R.d.c||{}; R.d.c[st.stage+"_"+id]=code; NET.put(R.path+"/c/"+st.stage+"_"+id, code).catch(()=>{}); } teamScore(); }
    else { const pts=10+Math.min(10,(st.combo-1)*2); st.score+=pts; if(st.combo>=3){ eCb.textContent="COMBO ×"+st.combo+" +"+pts; eCb.style.opacity=1; clearTimeout(eCb._t); eCb._t=setTimeout(()=>eCb.style.opacity=0, 700); } }
    drawHud(); }
  function step(dt, live){ const I=api.I;
    let mx=I.mx, mz=-I.my; const m=Math.hypot(mx,mz); if(m>1){ mx/=m; mz/=m; }
    P.p.x+=mx*SPD*dt; P.p.z+=mz*SPD*dt; const lim=HALF-.3; P.p.x=Math.max(-lim,Math.min(lim,P.p.x)); P.p.z=Math.max(-lim,Math.min(lim,P.p.z));
    if(m>.1) P.face=Math.atan2(mx,mz);
    if((I.jumpP || I.jump) && P.onG){ P.vy=JV; P.onG=false; api.sfx.jump(); }
    if(!P.onG){ P.vy-=GRAV*dt; P.p.y+=P.vy*dt; if(P.p.y<=0){ P.p.y=0; P.vy=0; P.onG=true; } }
    P.inv=Math.max(0,P.inv-dt);
    if(!live || st.out) return;
    const id=idxAt(P.p.x,P.p.z);
    if(id>=0 && P.onG){ if(cell[id]===1) clearTile(id); if(red[id] && cell[id]!==2) hit(); }
    st.comboT=Math.max(0, st.comboT-dt); }
  function stageClear(){ if(st.clrS===st.stage) return; st.clrS=st.stage; st.cleared++; st.clearT=2.4; api.sfx.clear();
    if(CO){ teamScore(); api.msg('🎉 다 같이 '+(st.stage+1)+' 판 깼다!<small>🤝 +50</small>', 1900); }
    else { const b=Math.ceil(st.left)*2+20; st.score+=b; api.msg('🎉 '+(st.stage+1)+' 판 깼다!<small>남은 시간 보너스 ⭐ +'+b+'</small>', 1900); } drawHud(); }
  function end(){ if(st.over) return; st.over=true; const reached=st.stage+1;
    if(CO && R.path && NETOK){ NET.del(R.path+"/p/"+code).catch(()=>{}); }
    const who=CO ? livePeers(true).map(p=>p.n||"친구") : [];
    setTimeout(()=>{ api.end(CO ? {title:'🤝 함께 ⭐ '+st.score+'점!', sub:(who.length)+'명이 함께 · '+reached+' 판까지 · 내가 지운 칸 '+st.steps, rows:null,
        extra:'<div class="sub" style="margin-top:10px;font-size:16px;color:#4b3527">👫 '+who.map(esc).join(' · ')+'</div>',
        coins:reached>=5?15:reached>=3?10:5, upd:(b,t)=>{ if(st.score>(b.co|0)) b.co=st.score; if(reached>(b.st|0)) b.st=reached; t.tiles=(t.tiles|0)+st.steps; t.co=(t.co|0)+1; }}
      : {title:st.lives>0?'⏰ 시간 끝!':'💦 ❤️ 다 썼어요', sub:reached+' 판까지 · ⭐ '+st.score+' · 지운 칸 '+st.steps, rows:null,
        extra:'<div class="sub" style="margin-top:10px;font-size:17px;color:#4b3527">'+(reached>=5?'🔥 대단해요!':reached>=3?'👍 잘했어요!':'다음엔 3판까지 가 봐요!')+'</div>',
        coins:reached>=5?15:reached>=3?10:5, upd:(b,t)=>{ if(st.score>(b.sc|0)) b.sc=st.score; if(reached>(b.st|0)) b.st=reached; t.tiles=(t.tiles|0)+st.steps; }}); }, 1100); }

  /* ── 한 장면 ── */
  function tick(dt){ if(paused) return; st.t+=dt;
    if(st.intro>0){ st.intro-=dt; eIn.style.opacity=st.intro>.3?1:0; } if(st.intro<=0 && eIn.style.display!=="none") eIn.style.display="none";
    netTick(dt); peersTick(dt);
    if(st.phase==="count"){ const h=(R.d&&R.d.h)||{}, left=(h.st-now())/1000; eCnt.textContent=left>0?Math.ceil(left):""; if(left<=3 && left>0 && Math.ceil(left)!==st.lc){ st.lc=Math.ceil(left); api.sfx.tick(); }
      if(left<=0){ eCnt.textContent=""; st.phase="play"; newStage(0, true); } }
    if(st.phase==="play" && !st.over){
      if(CO){ const h=(R.d&&R.d.h)||{}, sg=h.sg||{s:0, at:h.st||now()}; st.el=sg.s===st.stage ? (now()-sg.at)/1000 : st.el; }
      else if(st.clearT<=0) st.el+=dt;
      st.left=Math.max(0, STAGE_T-st.el);
      if(st.clearT>0 || st.clrS===st.stage){ st.clearT=Math.max(0,st.clearT-dt); red.fill(0); warn.fill(0); if(st.clearT<=0 && !CO) newStage(st.stage+1); }
      else { if(st.el>=STAGE_T){ if(CO && authority() && R.path && !R.endSent){ R.endSent=true; NET.put(R.path+"/h/end", 1).catch(()=>{}); } end(); }
        hzAt(st.pl.H, st.el, cell, red, warn); if(st.blue<=0) stageClear(); }
      step(dt, st.clrS!==st.stage); }
    else if(st.phase!=="play") step(dt, false);
    eOut.style.display=st.out && !st.over?"block":"none";
    drawTime();
    const blink=(Math.sin(st.t*18)>0), pulse=.85+.15*Math.sin(st.t*5);
    for(let q=0;q<N*N;q++){ let c=COL.off, k=1; if(red[q]) c=COL.red; else if(warn[q]) c=blink?COL.warn:COL.off; else if(cell[q]===1){ c=COL.blue; k=pulse; } else if(cell[q]===2) c=COL.green; else if(cell[q]===3) c=COL.done; _c.setHex(c).convertSRGBToLinear(); if(k!==1) _c.multiplyScalar(k); T.setColorAt(q, _c); }
    T.instanceColor.needsUpdate=true;
    if(me){ me.g.position.copy(P.p); me.face=P.face; me.moving=P.onG && Math.hypot(api.I.mx,api.I.my)>.1; try{ animChar(me, dt); }catch(e){} me.g.visible=!st.out && !(P.inv>0 && Math.sin(st.t*30)>0); }
    { const id=idxAt(P.p.x,P.p.z); HL.visible=id>=0 && !st.out; if(id>=0) HL.position.set(cx(id%N), 0, cx(Math.floor(id/N))); }
    shadowD.position.set(P.p.x,.13,P.p.z); shadowD.scale.setScalar(1-Math.min(.5,P.p.y*.3)); shadowD.visible=!st.out;
    st.flash=Math.max(0,st.flash-dt); eHurt.style.opacity=st.flash>0?1:0;
    const asp=cam.aspect||1, port=asp<1, W=asp<.6?7.6:10.6, tv=Math.tan(cam.fov*Math.PI/360), d=Math.max(15, Math.min(38, W/(tv*Math.min(asp,1.45)))), pit=port?.92:.86;
    const fx=Math.max(0, HALF+1.2-W), tx=Math.max(-fx, Math.min(fx, P.p.x*.8)), tz=P.p.z*(asp<.6?.45:.25)+(asp<.6?1.6:asp<1?-.4:1.4); if(!camInit){ camT.set(tx,0,tz); camInit=true; } camT.x+=(tx-camT.x)*Math.min(1,dt*3); camT.z+=(tz-camT.z)*Math.min(1,dt*3);
    cam.position.set(camT.x, Math.sin(pit)*d, camT.z+Math.cos(pit)*d); cam.lookAt(camT.x, 0, camT.z); }
  if(CO){ /* 대기 바닥: 안전 칸만 켜 둠 · 걸어 다닐 수 있음 */ st.pl=plan(st.seed, 0); cell.set(st.pl.cell); for(let q=0;q<N*N;q++) if(cell[q]===1) cell[q]=0; st.blue=0; P.p.set(cx(1),0,cx(N-2)); listRooms(); roomUI(); drawHud(); }
  else newStage(0, true);
  function dispose(){ R.gone=true; if(CO) leaveRoom(false); disp.forEach(x=>{ try{ x.dispose(); }catch(e){} }); }
  return {scene, cam, tick, dispose, pause:(v)=>{ paused=!!v; }, st, P, cell, red, warn, newStage, idxAt, N, TS, HALF, cx, R, plan, hzAt, mkRoom, joinRoom, startRoom, listRooms, poll, code}; }

MG.reg("grid", {ic:"🟦", nm:"발판 게임", tag:"LED 바닥 · 밟고 · 피하고 · 점프 · 친구랑 같이 (최대 5명)", bg:"linear-gradient(135deg,#252a5c,#10123a)", big:"🟦🟥🟩",
  how:[["🟦","<b>파란 칸</b>을 모두 밟으면 다음 판 (점점 빨라져요)"],["🟥","<b>빨간 줄·고리·막대</b>가 오면 점프로 넘거나 피하기 · 판마다 무늬가 달라요"],["🟩","<b>초록 칸</b> = 안전 · 판마다 자리가 바뀌어요"],["❤️","3번 맞으면 끝 (같이 하기는 구경하다 다음 판에 다시)"],["👫","같이 하기 = 친구 방에 들어가거나 방 만들기 · 방장이 시작 → 10초 뒤 · 다 같이 얻은 점수"]],
  opts:[{k:"mode", t:"어떻게 할까요?", d:"solo", v:[["solo","🙋 혼자 하기"],["co","👫 같이 하기 (최대 5명)"]]}],
  payTxt:"5판 🪙15 · 3판 🪙10 · 참가 🪙5",
  bestTxt:(b,t)=>'🏆 최고 '+(b.st|0)+'판 · ⭐ '+(b.sc|0)+(b.co?' · 🤝 같이 최고 '+b.co+'점':'')+' · 지운 칸 모두 '+(t.tiles|0)+'개',
  ui:{look:false, btns:[{b:"jump", ic:"JUMP", cls:"tx"}]},
  start});
})();
