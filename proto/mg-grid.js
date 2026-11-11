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
const N=14, TS=1.8, HALF=N*TS/2, GRAV=24, JV=7.4, SPD=6.2, STAGE_T=60, MAXP=6, WAIT=10000;   /* (v595) 사용자: 「입장 인원 6명까지 · 이게 기본 룰」 */
const COL={off:0x252a5c, blue:0x2f8cff, green:0x2fd866, red:0xff2d55, hi:0xd23dff, gold:0xffd23f, warn:0xff9a3d, done:0x3a3f7a};

/* ── 같은 번호 = 같은 판 ── */
function RNG(seed){ let s=(seed>>>0)||0x9e3779b9; return ()=>{ s^=s<<13; s>>>=0; s^=s>>>17; s^=s<<5; s>>>=0; return s/4294967296; }; }
const mix=(a,b)=>{ let h=(a^0x45d9f3b)>>>0; h=Math.imul(h^(b+0x9e3779b9),0x85ebca6b)>>>0; h^=h>>>13; h=Math.imul(h,0xc2b2ae35)>>>0; return (h^(h>>>16))>>>0; };
/* (v595) 사용자: 「나중엔 점프로만 피할 수 없게 · 초록 칸도 적어져야 · 빨간 칸이 선풍기처럼 돌아가기도 · 그러려면 조금 더 넓어야」
   → 바닥 10×10 → 14×14 · 🟩 판마다 줄고(9판부터 2칸) 4판부터는 판 중간(30초)에 절반이 꺼짐 · 🟪 높은 벽(hi) = 점프해도 맞음 → 틈으로 달려야 함
     · 굵은 줄(2~3칸 = 점프로 못 넘음) · 🌀 선풍기(날개 3~4개 돌기 · 7판부터 높은 선풍기) */
const GREEN_T=["🟩 네 모서리","🟩 가운데 십자","🟩 양옆 띠","🟩 작은 섬 3개","🟩 대각선 징검다리","🟩 몇 칸만","🟩 더 적게","🟩 아주 조금","🟩 거의 없어요!"];
const HZ_T=["🟥 줄 + ⭐ 금빛 칸","💓 심장 박동 고리","♟ 박자 스텝 (색 바꿔 밟기)","🎯 네 구역 룰렛","🌊 밀물이 밀려와요","🐍 뱀이 기어 다녀요","🌪 소용돌이 + 박자 스텝","🌊 밀물 + 🎯 룰렛 + 🌀","🔥 다 섞여요!"];
/* (v597) 사용자(LED 바닥 놀이 영상): 「이런 것도 있고 조금 더 창의적으로」 → 판마다 대표 무늬(SIG)가 처음에 나옴
   💓 pulse 심장 박동(고리 3겹) · ♟ checker 박자 스텝(체크판 절반이 박자마다 바뀜 = 다른 색으로 콩콩) · 🎯 quad 네 구역 룰렛(한 구역만 안전)
   🌊 flood 밀물(한쪽에서 바닥 절반 넘게 덮었다 빠짐) · 🐍 snake 뱀(빨간 줄이 구불구불) · 🌪 spiral 소용돌이(바깥 → 안으로 도는 띠) · ⭐ 금빛 칸(잠깐 · +50) · 뒤 LED 전광판 = 지금 무늬 이름 */
const LED_T=["🟥 줄 + ⭐","💓 박동 고리","♟ 박자 스텝","🎯 룰렛","🌊 밀물","🐍 뱀","🌪 소용돌이","🌊 🎯 🌀","🔥 다 섞여요"];
const SIG=[null,"pulse","checker","quad","flood","snake","spiral","flood",null];
const SPIRAL=(()=>{ const o=new Int16Array(N*N).fill(-1); let x0=0,y0=0,x1=N-1,y1=N-1,k=0; while(x0<=x1&&y0<=y1){ for(let i=x0;i<=x1;i++) o[y0*N+i]=k++; for(let j=y0+1;j<=y1;j++) o[j*N+x1]=k++; if(y1>y0) for(let i=x1-1;i>=x0;i--) o[y1*N+i]=k++; if(x1>x0) for(let j=y1-1;j>y0;j--) o[j*N+x0]=k++; x0++; y0++; x1--; y1--; } return o; })();
const HZ_NM={pulse:"💓 심장 박동!", checker:"♟ 박자 스텝!", quad:"🎯 안전한 곳!", flood:"🌊 밀물!", snake:"🐍 뱀이 와요!", spiral:"🌪 소용돌이!", wall:"🟪 벽! 틈으로", fan:"🌀 선풍기!", band:"🟥 굵은 줄!"};
/* (v596) 사용자: 「쉬움 모드랑 어려움 모드 있어야 할 것 같아」 — 🐣 쉬움: 느리게 · 간격 넓게 · 🟪 높은 것 없음(9판 전) · 굵은 줄 늦게 · 🟩 더 많이 · ❤️5 / 🔥 어려움: 빠르게 · 촘촘하게 · 🟩 적게 · 판 중간 꺼짐 일찍 */
const DF={easy:{per:1.35, fl:.5, sp:.72, gap:1.45, hiAt:8, bandAt:5, g:4, goAt:6, goT:35, life:5, ic:"🐣", nm:"쉬움"}, normal:{per:1.05, fl:.6, sp:1, gap:1, hiAt:0, bandAt:0, g:0, goAt:3, goT:30, life:3, ic:"🙂", nm:"보통"}, hard:{per:.85, fl:.68, sp:1.22, gap:.78, hiAt:0, bandAt:0, g:-1, goAt:2, goT:24, life:3, ic:"🔥", nm:"어려움"}};
function plan(seed, s, df){ const D=DF[df]||DF.normal; const R=RNG(mix(seed, s*7919+13)), ri=n=>Math.floor(R()*n), cell=new Uint8Array(N*N), G=[];
  const put=(i,j)=>{ if(i>=0&&j>=0&&i<N&&j<N && !cell[j*N+i]){ cell[j*N+i]=2; G.push(j*N+i); } };
  const th=Math.min(s, 8), M=N-1, c0=Math.floor(N/2);
  if(th===0){ [[0,0],[N-2,0],[0,N-2],[N-2,N-2]].forEach(([a,b])=>{ put(a,b); put(a+1,b); put(a,b+1); put(a+1,b+1); }); put(c0-1,c0-1); put(c0,c0); put(c0-1,c0); put(c0,c0-1); }
  else if(th===1){ [[c0-1,c0-1],[c0,c0-1],[c0-1,c0],[c0,c0],[c0-2,c0-1],[c0+1,c0],[c0-1,c0-2],[c0,c0+1]].forEach(([a,b])=>put(a,b)); put(0,0); put(M,M); }
  else if(th===2){ for(let j=c0-2;j<=c0+1;j++){ put(0,j); put(M,j); } }
  else if(th===3){ let k=0, g=0; while(k<3 && g++<99){ const a=1+ri(N-3), b=1+ri(N-3); if([0,1].some(x=>[0,1].some(y=>cell[(b+y)*N+a+x]))) continue; put(a,b); put(a+1,b); put(a,b+1); put(a+1,b+1); k++; } }
  else if(th===4){ for(let i=1;i<N;i+=3){ put(i,i); put(M-i,i); } }
  else { const n=[0,0,0,0,0,6,5,4,3][th]-(s>8?Math.min(1,Math.floor((s-8)/2)):0); let g=0; while(G.length<Math.max(2,n) && g++<199) put(1+ri(N-2), 1+ri(N-2)); }
  if(D.g>0){ let g=0; const n0=G.length; while(G.length<n0+D.g && g++<199) put(ri(N), ri(N)); } else if(D.g<0 && G.length>3){ for(let z=0;z<-D.g;z++){ const q=G.pop(); cell[q]=0; } }
  const nb=Math.min(52, 16+s*5); let k=0, guard=0; while(k<nb && guard++<1999){ const q=ri(N*N); if(cell[q]) continue; cell[q]=1; k++; }
  /* 🟩 판 중간에 절반 꺼짐 (4판부터) */
  const GO=s>=D.goAt && G.length>2 ? {t:D.goT, L:G.filter((q,i)=>i%2===1)} : null;
  /* 빨강 시간표 (판 시작 뒤 초) */
  const PAL=[["row","col"],["ring","row","col","pulse"],["spin","row","col","checker"],["band","blink","row","quad"],["fan","ring","row","flood"],["wall","band","col","snake"],["hfan","band","row","checker","spiral"],["wall","fan","fan2","band","quad","flood"],["row","col","ring","blink","cross","spin","band","wall","fan","hfan","fan2","row2","pulse","checker","quad","flood","snake","spiral"]][th];
  const sp=Math.min(3.8, 1.7+s*.2)*D.sp, w=Math.max(.75, 1.25-s*.05), H=[]; let t=2.6;
  const C=()=>[c0-.5+(R()-.5)*3, c0-.5+(R()-.5)*3];
  let first=SIG[th]; const GD=[];
  for(let gt=7+ri(5); gt<STAGE_T-4; gt+=11+ri(8)){ let q=ri(N*N), g=0; while(cell[q] && g++<40) q=ri(N*N); GD.push({t0:gt, q, dur:5}); }   /* ⭐ 금빛 칸 */
  while(t<STAGE_T){ const kd=first||PAL[ri(PAL.length)]; first=null; let gap=0, xt=0;
    if(kd==="pulse"){ const ci=2+ri(N-4), cj=2+ri(N-4); for(let r=0;r<3;r++) H.push({t0:t+r*.9, k:"ring", ci, cj, sp:sp*.9, w:r?0:w+.3, th:1, sig:r?0:"pulse"}); xt=2; }
    else if(kd==="checker"){ H.push({t0:t, k:"checker", w:w+.6, per:D.per, n:6+Math.min(4,s), p0:ri(2), sig:"checker"}); xt=(6+Math.min(4,s))*D.per; }
    else if(kd==="quad"){ H.push({t0:t, k:"quad", w:2.3, on:2, safe:ri(4), sig:"quad"}); xt=3; }
    else if(kd==="flood"){ H.push({t0:t, k:"flood", w:1.8, side:ri(4), f:D.fl+(s>=8?.1:0), sp:sp*1.15, hold:2.2, sig:"flood"}); xt=5; }
    else if(kd==="snake"){ const P=[]; let x=ri(N), z=0, dx=0, dz=1; if(R()<.5){ z=ri(N); x=0; dx=1; dz=0; } for(let k2=0;k2<48;k2++){ P.push(z*N+x); if(R()<.28){ const tn=R()<.5?1:-1; const ndx=-dz*tn, ndz=dx*tn; dx=ndx; dz=ndz; } let nx=x+dx, nz=z+dz; if(nx<0||nz<0||nx>=N||nz>=N){ dx=-dx; dz=-dz; nx=x+dx; nz=z+dz; } x=nx; z=nz; }
      H.push({t0:t, k:"snake", w:w+.4, P, len:6+Math.min(4,s>>1), sp:sp*1.6, sig:"snake"}); xt=6; }
    else if(kd==="spiral"){ H.push({t0:t, k:"spiral", w:w+.5, rate:26*D.sp+s, dur:1.1, sig:"spiral"}); xt=5; }
    if(kd==="row"||kd==="col"){ H.push({t0:t, k:kd, dir:R()<.5?1:-1, sp, w, th:1}); }
    else if(kd==="band"){ H.push({t0:t, k:R()<.5?"row":"col", dir:R()<.5?1:-1, sp:sp*.75, w:w+.2, th:s<D.bandAt?1:s>=7?3:2}); }   /* 굵은 줄 = 점프로 못 넘음 */
    else if(kd==="wall"){ const g=1+ri(N-4); H.push({t0:t, k:R()<.5?"row":"col", dir:R()<.5?1:-1, sp:sp*.62, w:w+.35, th:1, hi:s>=D.hiAt?1:0, gap:[g,g+2]}); gap=1; }   /* 🟪 높은 벽 + 틈 3칸 */
    else if(kd==="row2"){ H.push({t0:t, k:"row", dir:1, sp, w, th:1}); H.push({t0:t, k:"row", dir:-1, sp, w, th:1}); }
    else if(kd==="cross"){ H.push({t0:t, k:"row", dir:1, sp:sp*.9, w, th:1}); H.push({t0:t, k:"col", dir:-1, sp:sp*.9, w, th:1}); }
    else if(kd==="ring"){ H.push({t0:t, k:"ring", ci:1+ri(N-2), cj:1+ri(N-2), sp:sp*.85, w, th:s>=5?2:1}); }
    else if(kd==="blink"){ const L=[]; const n=Math.min(36, 10+s*3); for(let q=0;q<n;q++){ const z=ri(N*N); if(cell[z]!==2) L.push(z); } H.push({t0:t, k:"blink", L, w:w+.25, on:1.3}); }
    else if(kd==="spin"){ const [x,z]=C(); H.push({t0:t, k:"fan", cx:x, cz:z, nb:2, a:R()*6.28, sp:(R()<.5?-1:1)*(.9+s*.05), len:N*.62, dur:6.5, w}); }
    else if(kd==="fan"||kd==="hfan"||kd==="fan2"){ const nb=s>=6?4:3, d=(R()<.5?-1:1); const one=(x,z,dd)=>H.push({t0:t, k:"fan", cx:x, cz:z, nb, a:R()*6.28, sp:dd*(.75+s*.045), len:kd==="fan2"?N*.34:N*.55, dur:8, w:w+.3, hi:kd==="hfan" && s>=D.hiAt?1:0});
      if(kd==="fan2"){ one(N*.27,N*.27,d); one(N*.73-1,N*.73-1,-d); } else { const [x,z]=C(); one(x,z,d); } }
    t+=Math.max(1.5, 4.4-s*.3)*D.gap+(kd.indexOf("fan")>=0||kd==="spin"?3.5:0)+(gap?1:0)+xt*.6+R()*.5; }
  H.forEach(h=>{ if(!h.sig && h.w>0){ h.sig=h.hi?"wall":h.k==="fan"?"fan":(h.th||1)>1?"band":0; } });
  return {cell, G, H, GO, GD, blue:k, th}; }
/* 판 시작 뒤 el 초의 빨강·경고 (상태 없음 = 모두 같음) · hi = 🟪 높은 것(점프해도 맞음) */
function hzAt(H, el, cell, red, warn, hi){ red.fill(0); warn.fill(0); if(hi) hi.fill(0);
  const R1=(q,h)=>{ red[q]=1; if(h.hi && hi) hi[q]=1; };
  for(const h of H){ const t=el-h.t0; if(t<0) continue; const wu=t<h.w, u=t-h.w;
    if(h.k==="row"||h.k==="col"){ const T=h.th||1, pos=h.dir>0 ? -.5+u*h.sp : N-.5-u*h.sp; if(!wu && (pos<-1.5-T||pos>N+.5+T)) continue; const e=h.dir>0?0:N-1, g=h.gap;
      for(let a=0;a<N;a++){ if(g && a>=g[0] && a<=g[1]) continue; if(wu){ warn[h.k==="row"?e*N+a:a*N+e]=1; continue; }
        for(let z=0;z<T;z++){ const b=Math.round(pos)-h.dir*z; if(b<0||b>=N) continue; R1(h.k==="row"?b*N+a:a*N+b, h); } } }
    else if(h.k==="ring"){ const r=-.5+u*h.sp, T=h.th||1; if(!wu && r>N+1+T) continue; for(let j=0;j<N;j++) for(let i=0;i<N;i++){ const d=Math.max(Math.abs(i-h.ci),Math.abs(j-h.cj)); if(wu){ if(d===0) warn[j*N+i]=1; } else if(d<=r+.5 && d>r-T+.5) R1(j*N+i, h); } }
    else if(h.k==="blink"){ if(t>h.w+h.on) continue; h.L.forEach(id=>{ if(wu) warn[id]=1; else R1(id, h); }); }
    else if(h.k==="checker"){ const b=wu?-1:Math.floor(u/h.per); if(b>=h.n) continue; for(let j=0;j<N;j++) for(let i=0;i<N;i++){ const par=(i+j)%2;
        if(wu){ if(par===h.p0) warn[j*N+i]=1; continue; } const pr=(b+h.p0)%2, ph=u-b*h.per; if(par===pr) R1(j*N+i, h); else if(ph>h.per-.38 && b+1<h.n) warn[j*N+i]=1; } }
    else if(h.k==="quad"){ if(!wu && u>h.on) continue; const hf=N/2; for(let j=0;j<N;j++) for(let i=0;i<N;i++){ const qd=(i>=hf?1:0)+(j>=hf?2:0); if(qd===h.safe) continue; if(wu){ if(t>h.w*.35) warn[j*N+i]=1; } else R1(j*N+i, h); } }
    else if(h.k==="flood"){ const F=Math.round(h.f*N), fr=Math.min(F, u*h.sp), bk=Math.max(0, (u-F/h.sp-h.hold)*h.sp); if(!wu && bk>=F) continue;
      for(let j=0;j<N;j++) for(let i=0;i<N;i++){ const a=h.side===0?i:h.side===1?N-1-i:h.side===2?j:N-1-j; if(a>=F) continue; if(wu) warn[j*N+i]=1; else if(a<fr && a>=bk) R1(j*N+i, h); } }
    else if(h.k==="snake"){ const P=h.P; if(wu){ warn[P[0]]=1; warn[P[1]]=1; continue; } const ix=Math.floor(u*h.sp); if(ix-h.len>=P.length) continue; for(let k=Math.max(0,ix-h.len+1);k<=Math.min(ix,P.length-1);k++) R1(P[k], h); }
    else if(h.k==="spiral"){ if(wu){ for(let q=0;q<N*N;q++) if(SPIRAL[q]<N*4-4) warn[q]=1; continue; } if(u>N*N/h.rate+h.dur) continue; for(let q=0;q<N*N;q++){ const tt=u-SPIRAL[q]/h.rate; if(tt>=0 && tt<h.dur) R1(q, h); } }
    else if(h.k==="fan"){ if(t>h.w+h.dur) continue; const a0=h.a+(wu?0:h.sp*u);
      for(let j=0;j<N;j++) for(let i=0;i<N;i++){ const x=i-h.cx, z=j-h.cz, r=Math.hypot(x,z); if(r>h.len+.3) continue;
        for(let b=0;b<h.nb;b++){ const a=a0+b*Math.PI*2/h.nb, ca=Math.cos(a), sa=Math.sin(a), along=x*ca+z*sa, perp=Math.abs(-x*sa+z*ca); if(along>-.4 && perp<.62){ if(wu) warn[j*N+i]=1; else R1(j*N+i, h); break; } }
        if(r<.75){ if(wu) warn[j*N+i]=1; else R1(j*N+i, h); } } } }
  for(let q=0;q<N*N;q++) if(cell[q]===2){ red[q]=0; warn[q]=0; if(hi) hi[q]=0; } }

function start(api){
  /* (v658) 사용자: 「물총 아레나랑 발판 게임 게임 자체 퀄리티도 올려 줬으면」 → 규칙은 그대로 · 무대(네온 놀이방 · LED 칸 · 조명) · 손맛(밟으면 물결 · 통통 · 터지는 조각 · 무지개) · 화면(메뉴·결과 = 공통 키트 B · 게임 중 = A) */
  const MENU=!api.opt.mode, CO=api.opt.mode==="co", DFKEY="hyeng_proto_griddf";
  let DFK=DF[api.opt.df]?api.opt.df:(()=>{ try{ const v=localStorage.getItem(DFKEY); return DF[v]?v:"normal"; }catch(e){ return "normal"; } })();
  if(MENU) api.menu=true; try{ PUI.css(); }catch(e){}
  const scene=new THREE.Scene(); scene.fog=new THREE.Fog(0x140f44, 46, 96);
  { const cv=document.createElement("canvas"); cv.width=4; cv.height=256; const g=cv.getContext("2d"), gr=g.createLinearGradient(0,0,0,256); gr.addColorStop(0,"#05061c"); gr.addColorStop(.45,"#1a1258"); gr.addColorStop(.8,"#3b1a72"); gr.addColorStop(1,"#5a2485"); g.fillStyle=gr; g.fillRect(0,0,4,256);
    const tx=new THREE.CanvasTexture(cv); tx.encoding=THREE.sRGBEncoding; scene.background=tx; }
  const cam=new THREE.PerspectiveCamera(50, 1, .3, 200);
  scene.add(new THREE.HemisphereLight(0xdfe6ff, 0x2a2550, .7)); const sun=new THREE.DirectionalLight(0xffffff, .9); sun.position.set(-6,20,10); scene.add(sun); scene.add(sun.target);
  if(!api.low){ sun.castShadow=true; sun.shadow.mapSize.set(1024,1024); const c=sun.shadow.camera; c.left=c.bottom=-14; c.right=c.top=14; c.near=1; c.far=50; sun.shadow.bias=-0.001; }
  const toon=m=>{ try{ TOON.mat(m); }catch(e){} return m; };
  const disp=[]; disp.push(scene.background);

  const LED={cv:null, tx:null, txt:"", col:""};
  function ledDraw(t, col){ if(!LED.cv || (LED.txt===t && LED.col===col)) return; LED.txt=t; LED.col=col; const g=LED.cv.getContext("2d"); g.fillStyle="#05061a"; g.fillRect(0,0,128,32);
    g.font="bold 16px Jua, Nunito, sans-serif"; const tw=g.measureText(t).width; if(tw>120) g.font="bold "+Math.max(9, Math.floor(16*120/tw))+"px Jua, Nunito, sans-serif"; g.textAlign="center"; g.textBaseline="middle"; g.fillStyle=col; g.fillText(t,64,17);
    const d=g.getImageData(0,0,128,32); for(let y=0;y<32;y++) for(let x=0;x<128;x++){ if(x%2===1||y%2===1){ const o=(y*128+x)*4; d.data[o]*=.35; d.data[o+1]*=.35; d.data[o+2]*=.35; } } g.putImageData(d,0,0); LED.tx.needsUpdate=true; }   /* 점 LED 느낌 */
  /* ── 방: 네온 놀이방 · LED 칸(빛 번짐) · 조명 ── */
  const W=N*TS+3, FXL={beams:[], bars:[], orbs:[], neon:[]};
  { const g=new THREE.BoxGeometry(W, .5, W); disp.push(g); const m=new THREE.Mesh(g, toon(new THREE.MeshStandardMaterial({color:0x14163c, roughness:.9}))); m.position.y=-.26; m.receiveShadow=true; scene.add(m);
    const gg=new THREE.PlaneGeometry(140,140); disp.push(gg); const fcv=document.createElement("canvas"); fcv.width=fcv.height=32; { const g=fcv.getContext("2d"); g.fillStyle="#12103a"; g.fillRect(0,0,32,32); g.fillStyle="#2a2470"; g.beginPath(); g.arc(16,16,2.2,0,6.3); g.fill(); g.fillStyle="#1b1850"; g.fillRect(0,0,32,1); g.fillRect(0,0,1,32); }
    const ftx=new THREE.CanvasTexture(fcv); ftx.wrapS=ftx.wrapT=THREE.RepeatWrapping; ftx.repeat.set(70,70); ftx.encoding=THREE.sRGBEncoding; disp.push(ftx); const gm=new THREE.Mesh(gg, new THREE.MeshBasicMaterial({map:ftx, fog:false})); gm.rotation.x=-Math.PI/2; gm.position.y=-.5; scene.add(gm);
    const wm=toon(new THREE.MeshStandardMaterial({color:0x22265e, roughness:.9})), dk=toon(new THREE.MeshStandardMaterial({color:0x15173f, roughness:.9}));
    const nm=new THREE.MeshBasicMaterial({color:0x7fe0ff}), nm2=new THREE.MeshBasicMaterial({color:0xff6bd6}); FXL.neon=[nm,nm2];
    const box=(w,h,d,mat,x,y,z)=>{ const b=new THREE.Mesh(new THREE.BoxGeometry(w,h,d), mat); b.position.set(x,y,z); scene.add(b); disp.push(b.geometry); return b; };
    [[0,-W/2,W,.6],[0,W/2,W,.6],[-W/2,0,.6,W],[W/2,0,.6,W]].forEach(([x,z,w,d],i)=>{ box(w,1.2,d,wm,x,.35,z); box(w+.02,.1,d+.02,i%2?nm2:nm,x,.99,z); box(w+.06,.06,d+.06,i%2?nm:nm2,x,.3,z); });
    /* 뒤 LED 전광판 (네온 테두리) */
    { const cv=document.createElement("canvas"); cv.width=128; cv.height=32; const tx=new THREE.CanvasTexture(cv); tx.magFilter=THREE.NearestFilter; tx.minFilter=THREE.LinearFilter; tx.encoding=THREE.sRGBEncoding; disp.push(tx);
      const bw=W*.8, bh=W*.2, by=5.4, bz=-W/2-.5;
      const m=new THREE.Mesh(new THREE.PlaneGeometry(bw, bh), new THREE.MeshBasicMaterial({map:tx})); m.position.set(0, by, bz+.12); scene.add(m); disp.push(m.geometry);
      box(bw+.6, bh+.6, .3, dk, 0, by, bz-.1); box(bw+.9, .14, .14, nm2, 0, by+bh/2+.36, bz+.1); box(bw+.9, .14, .14, nm2, 0, by-bh/2-.36, bz+.1); box(.14, bh+.86, .14, nm, -bw/2-.38, by, bz+.1); box(.14, bh+.86, .14, nm, bw/2+.38, by, bz+.1);
      box(.5, by-bh/2, .5, dk, -bw/2+1.5, (by-bh/2)/2, bz-.1); box(.5, by-bh/2, .5, dk, bw/2-1.5, (by-bh/2)/2, bz-.1); LED.cv=cv; LED.tx=tx; }
    /* 모서리 기둥 + 빛 구슬 · 스피커 */
    [[-1,-1],[1,-1],[-1,1],[1,1]].forEach(([a,b],i)=>{ const cg=new THREE.CylinderGeometry(.42,.5,3,10); disp.push(cg); const c=new THREE.Mesh(cg, dk); c.position.set(a*W/2, 1.2, b*W/2); scene.add(c);
      const og=new THREE.SphereGeometry(.62,14,10); disp.push(og); const om=new THREE.MeshBasicMaterial({color:i%2?0xff6bd6:0x7fe0ff}); const o=new THREE.Mesh(og, om); o.position.set(a*W/2, 3.1, b*W/2); scene.add(o); FXL.orbs.push({m:om, k:i}); });
    [-1,1].forEach(a=>{ const x=a*(W/2+2.6), z=-W/2+1.5; box(2.4,4.4,2, dk, x,2,z); [3.1,1.3].forEach((y,k)=>{ const g=new THREE.CircleGeometry(k?.86:.56,20); disp.push(g); const m=new THREE.Mesh(g, new THREE.MeshBasicMaterial({color:0x2a2f6e})); m.position.set(x,y,z+1.01); scene.add(m);
        const g2=new THREE.RingGeometry((k?.86:.56)*.86,(k?.86:.56),20); disp.push(g2); const m2=new THREE.Mesh(g2, a>0?nm2:nm); m2.position.set(x,y,z+1.02); scene.add(m2); }); });
    /* 양옆 빛 기둥 (박자에 맞춰 오르내림) */
    if(!api.low){ const bg=new THREE.BoxGeometry(.7,1,.7); bg.translate(0,.5,0); disp.push(bg); const bm=new THREE.MeshBasicMaterial({color:0xffffff}); const B=new THREE.InstancedMesh(bg, bm, 28); B.instanceMatrix.setUsage(THREE.DynamicDrawUsage); scene.add(B); FXL.barM=B;
      for(let i=0;i<28;i++){ const side=i<14?-1:1, k=i%14; FXL.bars.push({x:side*(W/2+1.3), z:-W/2+1+k*(W-2)/13, k, side}); } }
    /* 천장 조명 줄 + 내려오는 빛 */
    { const ty=11.5, tz=-W/2+1; box(W+4,.3,.3, dk, 0,ty,tz); box(.3,ty,.3, dk, -W/2-2,ty/2,tz); box(.3,ty,.3, dk, W/2+2,ty/2,tz);
      const cols=[0x7fe0ff,0xff6bd6,0xffd23f,0x7fe0ff,0xff6bd6];
      for(let i=0;i<5;i++){ const x=(i-2)*W/5; const hg=new THREE.CylinderGeometry(.3,.5,.7,10); disp.push(hg); const h=new THREE.Mesh(hg, dk); h.position.set(x,ty-.4,tz); scene.add(h);
        if(api.low) continue; const L=17, cg=new THREE.ConeGeometry(3.4, L, 18, 1, true); cg.translate(0,-L/2,0); disp.push(cg);
        const cm=new THREE.MeshBasicMaterial({color:cols[i], transparent:true, opacity:.075, blending:THREE.AdditiveBlending, depthWrite:false, side:THREE.DoubleSide, fog:false}); const c=new THREE.Mesh(cg, cm); const piv=new THREE.Group(); piv.position.set(x,ty-.6,tz); piv.add(c); scene.add(piv); FXL.beams.push({p:piv, k:i}); } }
    for(let i=0;i<40;i++){ const s=new THREE.Mesh(new THREE.SphereGeometry(.09+((i*7)%5)*.02,6,5), i%3?nm:nm2); const a=i/40*Math.PI*2; s.position.set(Math.cos(a)*(26+(i%5)*3), 7+Math.sin(i*1.7)*4.5+(i%4), Math.sin(a)*(26+(i%5)*3)-6); scene.add(s); disp.push(s.geometry); } }
  /* LED 칸: 점 무늬 + 가운데가 밝은 판 (칸 색 × 무늬) · 위에 빛 번짐 한 겹 */
  const tileTx=(()=>{ const cv=document.createElement("canvas"); cv.width=cv.height=64; const g=cv.getContext("2d"); g.fillStyle="#3a3a3a"; g.fillRect(0,0,64,64);
    const gr=g.createRadialGradient(32,32,4,32,32,44); gr.addColorStop(0,"#ffffff"); gr.addColorStop(.7,"#d2d2d2"); gr.addColorStop(1,"#9a9a9a"); g.fillStyle=gr; g.beginPath(); if(g.roundRect) g.roundRect(3,3,58,58,9); else g.rect(3,3,58,58); g.fill();
    g.fillStyle="rgba(0,0,0,.13)"; for(let y=0;y<8;y++) for(let x=0;x<8;x++){ g.fillRect(4+x*7+5,4+y*7,2,7); g.fillRect(4+x*7,4+y*7+5,7,2); }
    g.strokeStyle="rgba(255,255,255,.55)"; g.lineWidth=2; g.beginPath(); if(g.roundRect) g.roundRect(5,5,54,54,8); else g.rect(5,5,54,54); g.stroke();
    const tx=new THREE.CanvasTexture(cv); tx.encoding=THREE.sRGBEncoding; disp.push(tx); return tx; })();
  const TG=new THREE.BoxGeometry(TS*.94, .22, TS*.94); disp.push(TG);
  const TM=new THREE.MeshBasicMaterial({color:0xffffff, map:tileTx}); const T=new THREE.InstancedMesh(TG, TM, N*N); T.instanceMatrix.setUsage(THREE.DynamicDrawUsage); scene.add(T);
  const _m=new THREE.Matrix4(), _c=new THREE.Color(), _w=new THREE.Color(), _q=new THREE.Quaternion(), _s=new V3(), _p=new V3();
  const cx=i=>-HALF+TS*(i+.5);
  for(let j=0;j<N;j++) for(let i=0;i<N;i++){ _m.makeTranslation(cx(i), .02, cx(j)); T.setMatrixAt(j*N+i, _m); T.setColorAt(j*N+i, _c.setHex(COL.off)); }
  T.instanceColor.setUsage(THREE.DynamicDrawUsage); const HT=new Uint8Array(N*N);
  let GLW=null; if(!api.low){ const cv=document.createElement("canvas"); cv.width=cv.height=64; const g=cv.getContext("2d"), gr=g.createRadialGradient(32,32,2,32,32,32); gr.addColorStop(0,"rgba(255,255,255,.9)"); gr.addColorStop(.45,"rgba(255,255,255,.34)"); gr.addColorStop(1,"rgba(255,255,255,0)"); g.fillStyle=gr; g.fillRect(0,0,64,64);
    const tx=new THREE.CanvasTexture(cv); disp.push(tx); const gg=new THREE.PlaneGeometry(TS*1.9, TS*1.9); gg.rotateX(-Math.PI/2); disp.push(gg);
    GLW=new THREE.InstancedMesh(gg, new THREE.MeshBasicMaterial({map:tx, transparent:true, blending:THREE.AdditiveBlending, depthWrite:false, fog:false}), N*N); GLW.renderOrder=2;
    for(let j=0;j<N;j++) for(let i=0;i<N;i++){ _m.makeTranslation(cx(i), .16, cx(j)); GLW.setMatrixAt(j*N+i, _m); GLW.setColorAt(j*N+i, _c.setHex(0)); } GLW.instanceColor.setUsage(THREE.DynamicDrawUsage); scene.add(GLW); }
  /* 손맛: 물결(밟은 곳에서 퍼지는 빛) · 조각(지운 칸이 터짐) · 착지 고리 · 떠오르는 점수 */
  const FXR=[], PN=72, PT=[]; let PM=null;
  function ripple(q, hex, pow, life){ if(q<0) return; FXR.push({i:q%N, j:Math.floor(q/N), t:0, c:hex==null?null:new THREE.Color(hex).convertSRGBToLinear(), p:pow||1, L:life||.7}); if(FXR.length>8) FXR.shift(); }
  { const g=new THREE.BoxGeometry(.3,.3,.3); disp.push(g); PM=new THREE.InstancedMesh(g, new THREE.MeshBasicMaterial({color:0xffffff}), PN); PM.instanceMatrix.setUsage(THREE.DynamicDrawUsage); PM.frustumCulled=false;
    for(let i=0;i<PN;i++){ PT.push({l:0, x:0,y:0,z:0, vx:0,vy:0,vz:0, r:0}); _m.makeScale(0,0,0); PM.setMatrixAt(i,_m); PM.setColorAt(i,_c.setHex(0xffffff)); } scene.add(PM); }
  let pI=0; function burst(x, z, hex, n, up){ for(let k=0;k<n;k++){ const p=PT[pI], a=Math.random()*6.283, v=1.5+Math.random()*3.2; p.l=.55+Math.random()*.3; p.x=x+(Math.random()-.5)*.8; p.y=.3; p.z=z+(Math.random()-.5)*.8; p.vx=Math.cos(a)*v; p.vz=Math.sin(a)*v; p.vy=(up||5)+Math.random()*3.5; p.r=Math.random()*6; PM.setColorAt(pI, _c.setHex(hex).convertSRGBToLinear()); pI=(pI+1)%PN; } PM.instanceColor.needsUpdate=true; }
  function partTick(dt){ for(let i=0;i<PN;i++){ const p=PT[i]; if(p.l<=0){ if(p.l>-1){ p.l=-1; _m.makeScale(0,0,0); PM.setMatrixAt(i,_m); } continue; } p.l-=dt; p.vy-=16*dt; p.x+=p.vx*dt; p.y+=p.vy*dt; p.z+=p.vz*dt; p.r+=dt*9; const k=Math.max(.01, Math.min(1, p.l*3)); _q.setFromAxisAngle(_p.set(.6,.5,.62).normalize(), p.r); _m.compose(_p.set(p.x,Math.max(.15,p.y),p.z), _q, _s.set(k,k,k)); PM.setMatrixAt(i,_m); } PM.instanceMatrix.needsUpdate=true; }
  const LAND=(()=>{ const g=new THREE.RingGeometry(.55,.75,28); disp.push(g); const m=new THREE.Mesh(g, new THREE.MeshBasicMaterial({color:0xffffff, transparent:true, opacity:0, depthWrite:false})); m.rotation.x=-Math.PI/2; m.position.y=.17; m.renderOrder=3; scene.add(m); return {m, t:9}; })();
  function floatTxt(x, y, z, txt, cls){ try{ const U=api.ui, v=_p.set(x,y,z).project(cam), el=document.createElement("div"); el.className="gFl "+(cls||""); el.textContent=txt; el.style.left=((v.x+1)/2*U.clientWidth)+"px"; el.style.top=((1-v.y)/2*U.clientHeight)+"px"; hud.appendChild(el); setTimeout(()=>el.remove(), 800); }catch(e){} }

  /* ── 캐릭터 (나 · 같이 하는 친구) ── */
  function avatar(o, k){ k=AVS; let c=null; try{ c=buildAvatar(o||{}); c.t=0; c.blinkT=2; c.face=0; c.act="idle"; c.g.scale.setScalar(k||AVS); c.g.traverse(m=>{ if(m.isMesh) m.castShadow=!api.low; }); scene.add(c.g); }catch(e){ c=null; } return c; }   /* (v593) t 가 없으면 걸을 때 NaN → 캐릭터가 사라짐 */
  /* (v596) 사용자: 「자기 캐릭터가 누군지 몰라 · 스킨이 다 기본이라 · 이름이 잘 안 보여」 → 아이마다 색(발밑 고리 · 이름 알약) · 나 = 머리 위 「▼ 나」 + 큰 노란 고리 */
  const PCOL=["#ff4d6d","#2f8cff","#ffc93d","#2fd866","#b06cff","#ff9a3d"];
  function tag(nm, col, mine){ const cv=document.createElement("canvas"); cv.width=512; cv.height=128; const g=cv.getContext("2d"); g.font="900 54px Jua, Nunito, sans-serif"; const t=(mine?"⭐ ":"")+nm, w=Math.min(500, g.measureText(t).width+56), x0=(512-w)/2;
    g.fillStyle="rgba(10,14,50,.55)"; g.beginPath(); g.roundRect ? g.roundRect(x0+4,20,w,92,46) : g.rect(x0+4,20,w,92); g.fill();
    g.fillStyle=col||"#2f8cff"; g.beginPath(); g.roundRect ? g.roundRect(x0,14,w,92,46) : g.rect(x0,14,w,92); g.fill(); g.lineWidth=6; g.strokeStyle="#fff"; g.stroke();
    g.textAlign="center"; g.textBaseline="middle"; g.lineWidth=8; g.strokeStyle="rgba(10,14,50,.7)"; g.strokeText(t,256,62); g.fillStyle="#fff"; g.fillText(t,256,62);
    const tx=new THREE.CanvasTexture(cv); tx.encoding=THREE.sRGBEncoding; disp.push(tx); const sp=new THREE.Sprite(new THREE.SpriteMaterial({map:tx, depthWrite:false, depthTest:false, transparent:true, sizeAttenuation:false})); sp.renderOrder=5; sp.center.set(.5,0); sp.scale.set(mine?.21:.19,mine?.0525:.0475,1); scene.add(sp); return sp; }   /* 화면에서 늘 같은 크기 = 멀어도 잘 보임 */
  function ring(col, big){ const g=new THREE.RingGeometry(big?.62:.5, big?.92:.74, 32); disp.push(g); const m=new THREE.Mesh(g, new THREE.MeshBasicMaterial({color:col, transparent:true, opacity:.95, depthWrite:false})); m.rotation.x=-Math.PI/2; m.renderOrder=3; scene.add(m); return m; }
  const slotOf=k=>{ if(!CO || !R || !R.d) return 0; const L=livePeers(true).map(p=>p.k); const i=L.indexOf(k); return i<0?0:i%PCOL.length; };
  const AVS=2.45; const me=avatar(api.av);
  const MY={tag:null, col:null, ring:ring(0xffd23f, true), arrow:null};
  { const cv=document.createElement("canvas"); cv.width=256; cv.height=160; const g=cv.getContext("2d"); g.font="900 64px Jua, Nunito, sans-serif"; g.textAlign="center"; g.lineWidth=10; g.strokeStyle="#10123a"; g.strokeText("나",128,62); g.fillStyle="#ffd23f"; g.fillText("나",128,62);
    g.beginPath(); g.moveTo(88,92); g.lineTo(168,92); g.lineTo(128,150); g.closePath(); g.fillStyle="#ffd23f"; g.fill(); g.lineWidth=8; g.stroke(); g.fill();
    const tx=new THREE.CanvasTexture(cv); tx.encoding=THREE.sRGBEncoding; disp.push(tx); MY.arrow=new THREE.Sprite(new THREE.SpriteMaterial({map:tx, depthWrite:false, depthTest:false, transparent:true, sizeAttenuation:false})); MY.arrow.renderOrder=6; MY.arrow.center.set(.5,-1.02); MY.arrow.scale.set(.085,.053,1);   /* 이름 알약 바로 위 (화면 기준) */ scene.add(MY.arrow); }
  function myTag(){ const col=PCOL[slotOf(code)]; if(MY.col===col) return; MY.col=col; if(MY.tag){ scene.remove(MY.tag); } MY.tag=tag(api.nick, col, true); }
  const P={p:new V3(), vy:0, onG:true, inv:0, face:0};
  const HL=new THREE.Group(); { const hm=new THREE.MeshBasicMaterial({color:0xffffff}), a=TS*.92, t=.12; [[0,-a/2,a,t],[0,a/2,a,t],[-a/2,0,t,a],[a/2,0,t,a]].forEach(([x,z,w,d])=>{ const g=new THREE.BoxGeometry(w,.05,d); disp.push(g); const m=new THREE.Mesh(g,hm); m.position.set(x,.14,z); HL.add(m); }); } scene.add(HL);
  const shadowD=new THREE.Mesh(new THREE.CircleGeometry(.45,20), new THREE.MeshBasicMaterial({color:0x000000, transparent:true, opacity:.35, depthWrite:false})); shadowD.rotation.x=-Math.PI/2; scene.add(shadowD); disp.push(shadowD.geometry);

  /* ── 판 상태 ── */
  const st={stage:0, t:0, el:0, left:STAGE_T, lives:DF[DFK].life, score:0, combo:0, comboT:0, blue:0, over:false, clearT:0, intro:(CO||MENU)?0:2.4, flash:0, steps:0, seed:(Math.random()*4294967296)>>>0, pl:null, phase:MENU?"menu":CO?"room":"play", out:false, cleared:0, wipe:9, shake:0, best:0, gold:0};
  const cell=new Uint8Array(N*N);   /* 0 꺼짐 · 1 파랑 · 2 초록 · 3 지운 칸 */
  const red=new Float32Array(N*N), warn=new Float32Array(N*N), hi=new Float32Array(N*N), GT=new Set();   /* GT = 이번 판에 먹은 ⭐ 금빛 칸 */
  let GI=-1;
  const goldAt=q=>{ const L=st.pl && st.pl.GD; if(!L || st.phase!=="play") return -1; for(let i=0;i<L.length;i++){ const g=L[i]; if(g.q===q && st.el>=g.t0 && st.el<g.t0+g.dur && !GT.has(i) && cell[q]!==2) return i; } return -1; };
  function nearGreen(){ const G=st.pl?st.pl.G:[]; if(!G.length) return [cx(0),cx(N-1)]; let best=G[0], bd=1e9; G.forEach(q=>{ const d=Math.hypot(cx(q%N)-P.p.x, cx(Math.floor(q/N))-P.p.z); if(d<bd){ bd=d; best=q; } }); return [cx(best%N), cx(Math.floor(best/N))]; }
  function newStage(s, first){ GT.clear(); st.nohit=true; st.clrS=-1; st.goS=-1; st.stage=s; st.pl=plan(st.seed, s, DFK); cell.set(st.pl.cell); st.blue=st.pl.blue; st.blue0=st.pl.blue; st.el=0; st.left=STAGE_T; st.clearT=0; st.wipe=0; red.fill(0); warn.fill(0);
    if(st.out){ st.out=false; st.lives=DF[DFK].life; P.inv=1.5; }   /* 같이 하기: 구경하던 아이 = 다음 판에 ❤️3 으로 다시 */
    if(first || CO){ const g=nearGreen(); P.p.set(g[0],0,g[1]); } if(me) me.act="idle";
    api.msg('<b class="gStg">'+(s+1)+' 판</b><small>'+GREEN_T[st.pl.th]+' · '+HZ_T[st.pl.th]+'</small>', 1900); try{ api.sfx.up(); }catch(e){} drawHud(); }

  /* ── 화면 글자 ── */
  const hud=api.hud;
  hud.innerHTML=`<style>
#mgUI .gTop{position:absolute;left:0;right:0;top:calc(8px + env(safe-area-inset-top));padding:0 max(10px,env(safe-area-inset-right)) 0 max(108px,calc(env(safe-area-inset-left) + 108px));display:flex;gap:8px 9px;align-items:center;pointer-events:none;flex-wrap:wrap;justify-content:center}
@media (min-width:760px){ #mgUI .gTop{padding-right:max(108px,calc(env(safe-area-inset-right) + 108px))} }
#mgUI .gTop .paPill{box-shadow:0 0 0 2px #fff,0 4px 0 2px rgba(74,46,31,.35);padding:2px 11px;font-size:17px;white-space:nowrap;min-height:32px;gap:5px}
#mgUI .gTop .tm b{font-family:var(--en);font-weight:900;font-size:19px;min-width:24px;text-align:center}
#mgUI .gTop .tm.low{background:#FF5A4E;color:#fff;animation:gLow .5s infinite alternate} @keyframes gLow{to{transform:scale(1.12)}}
#mgUI .gTop .lv{padding:2px 8px;gap:1px} #mgUI .gTop .lv .puI.pop{animation:gHeart .5s}
@keyframes gHeart{30%{transform:scale(1.7) rotate(-14deg)}}
#mgUI .gTop .bl{gap:7px;padding-right:12px} #mgUI .gTop .bl>i{width:18px;height:18px;border-radius:5px;background:#2f8cff;border:2px solid #4A2E1F;flex:none}
#mgUI .gTop .bl .b{width:74px;height:11px;border-radius:7px;background:#e6d6b8;border:2px solid #4A2E1F;overflow:hidden} #mgUI .gTop .bl .b i{display:block;height:100%;background:linear-gradient(#5fb0ff,#2f8cff);transition:width .2s}
#mgUI .gTop .bl b{font-family:var(--en);font-weight:900;min-width:18px}
#mgUI .gTop .sc b{font-family:var(--en);font-weight:900} #mgUI .gTop .sc.bump{animation:gBump .25s} @keyframes gBump{50%{transform:scale(1.18)}}
@media (max-width:480px){ #mgUI .gTop .paPill{font-size:15px;padding:1px 9px;min-height:29px} #mgUI .gTop{gap:7px 7px} #mgUI .gTop .bl .b{width:58px} }
#mgUI .gBan{top:calc(96px + env(safe-area-inset-top));font-size:21px;display:none} #mgUI .gBan.on{display:block}
@media (min-width:760px){ #mgUI .gBan{top:calc(58px + env(safe-area-inset-top))} }
@media (orientation:landscape) and (max-height:520px){ #mgUI .gBan{top:calc(50px + env(safe-area-inset-top));font-size:18px} }
#mgUI .gIntro{position:absolute;left:50%;top:60%;transform:translate(-50%,-50%) rotate(-1.5deg);background:#FFF6E3;color:#4A2E1F;border:3px solid #4A2E1F;border-radius:22px;box-shadow:0 0 0 4px #fff,0 8px 0 4px rgba(74,46,31,.35);padding:14px 18px;font-size:17px;line-height:1.75;pointer-events:none;text-align:left;transition:opacity .3s;width:max-content;max-width:calc(100vw - 30px)}
#mgUI .gIntro b{display:inline-block;width:24px;height:24px;border-radius:7px;vertical-align:-5px;margin-right:8px;border:2px solid #4A2E1F}
#mgUI .gHurt{position:absolute;inset:0;pointer-events:none;background:radial-gradient(ellipse at center, rgba(255,45,85,0) 40%, rgba(255,45,85,.6) 100%);opacity:0;transition:opacity .15s}
#mgUI .gCombo{position:absolute;left:50%;top:24%;transform:translateX(-50%) rotate(-4deg);font-size:34px;font-family:var(--kr);color:#ffe14d;-webkit-text-stroke:7px #0D0F33;paint-order:stroke fill;pointer-events:none;opacity:0;transition:opacity .2s;white-space:nowrap}
#mgUI .gCombo.pop{animation:gPop .25s} @keyframes gPop{from{transform:translateX(-50%) rotate(-4deg) scale(1.5)}}
#mgUI .gFl{position:absolute;transform:translate(-50%,-50%);font-family:var(--en);font-weight:900;font-size:22px;color:#fff;-webkit-text-stroke:5px #0D0F33;paint-order:stroke fill;pointer-events:none;animation:gFl .8s ease-out forwards;white-space:nowrap;z-index:3}
#mgUI .gFl.g{color:#ffe14d;font-size:30px} #mgUI .gFl.r{color:#ff8a9c;font-size:26px}
@keyframes gFl{0%{transform:translate(-50%,-50%) scale(.5)}20%{transform:translate(-50%,-90%) scale(1.2)}100%{transform:translate(-50%,-240%) scale(1);opacity:0}}
#mgUI .mgMsg .gStg{display:inline-block;font-weight:400;font-size:54px;color:#ffd860;-webkit-text-stroke:9px #0D0F33;paint-order:stroke fill;transform:rotate(-4deg);filter:drop-shadow(0 5px 0 #0D0F33);text-shadow:none;white-space:nowrap}
#mgUI .mgB[data-b=jump]{right:max(22px,calc(env(safe-area-inset-right) + 14px));bottom:calc(36px + env(safe-area-inset-bottom));width:108px;height:108px;font-size:25px;font-family:var(--kr);background:#FFF6E3;color:#4A2E1F;border:4px solid #4A2E1F;box-shadow:0 0 0 4px #fff,inset 0 -9px 0 rgba(74,46,31,.14),0 7px 0 4px rgba(74,46,31,.4);opacity:.94}
#mgUI .mgB[data-b=jump].dn{transform:translateY(5px) scale(.96);background:#ffe9b8;box-shadow:0 0 0 4px #fff,0 2px 0 4px rgba(74,46,31,.4)}
#mgUI .mgB[data-b=jump] small{font-size:22px;margin:0 0 -4px;order:-1;opacity:1}
#mgUI.gMenuOn .mgB,#mgUI.gMenuOn .mgJoy,#mgUI.gMenuOn .mgJoyH,#mgUI.gMenuOn .gTop,#mgUI.gMenuOn .gIntro{display:none!important}
#mgUI .gRoom{--nv:#1E2160;--nv2:#262a78;--deep:#0D0F33;--gold:#FFC94A;--pink:#FF4FA8;--mint:#2FD49A;--sky:#3FD8FF;position:absolute;left:50%;top:calc(104px + env(safe-area-inset-top));transform:translateX(-50%);width:min(400px,calc(100vw - 24px));background:linear-gradient(#262a78,#171a52);border:3px solid var(--gold);border-radius:22px;box-shadow:0 0 0 3px var(--deep),inset 0 0 0 2px rgba(255,201,74,.22),0 0 30px rgba(63,216,255,.25);padding:12px 14px;pointer-events:auto;text-align:center;font-size:16px}
@media (min-width:760px),(orientation:landscape){ #mgUI .gRoom{top:calc(58px + env(safe-area-inset-top))} }
#mgUI .gRoom h4{margin:0 0 6px;font-size:23px;font-weight:400;color:#ffd860}
#mgUI .gRoom .sub{font-size:14px;opacity:.88;margin:4px 0}
#mgUI .gRoom .puBtn{font-size:18px;min-height:46px;padding:7px 14px;margin:5px 3px 0;display:inline-flex}
#mgUI .gRoom .rl{display:flex;flex-direction:column;gap:7px;margin:8px 0;max-height:34vh;overflow:auto;padding:2px 2px 6px}
#mgUI .gRoom .rl .puBtn{margin:0;width:100%;justify-content:flex-start;font-size:16px}
#mgUI .gRoom .pl{display:flex;flex-wrap:wrap;gap:6px;justify-content:center;margin:8px 0}
#mgUI .gRoom .pl span{background:var(--nv);border:2px solid rgba(255,201,74,.55);border-radius:999px;padding:4px 12px}
#mgUI .gRoom .pl span.me{background:var(--pink);border-color:#fff}
#mgUI .gCnt{position:absolute;left:50%;top:44%;transform:translate(-50%,-50%) rotate(-4deg);font-size:120px;font-family:var(--en);font-weight:900;color:#ffd860;-webkit-text-stroke:12px #0D0F33;paint-order:stroke fill;pointer-events:none}
#mgUI .gOut{position:absolute;left:50%;bottom:calc(158px + env(safe-area-inset-bottom));transform:translateX(-50%);padding:6px 16px;font-size:15px;pointer-events:none;display:none;white-space:nowrap}
#mgUI .gHow{position:absolute;inset:0;z-index:30;display:flex;align-items:center;justify-content:center;background:rgba(13,15,51,.72);pointer-events:auto;padding:16px}
#mgUI .gHow>div{background:#FFF6E3;color:#4A2E1F;border:3px solid #4A2E1F;border-radius:22px;box-shadow:0 0 0 4px #fff,0 8px 0 4px rgba(74,46,31,.35);padding:14px 16px;width:min(100%,430px);font-size:16px;line-height:1.5;max-height:100%;overflow:auto}
#mgUI .gHow h4{margin:0 0 8px;font-size:24px;font-weight:400;text-align:center} #mgUI .gHow p{margin:0 0 9px;display:flex;gap:10px;align-items:center} #mgUI .gHow p>i{flex:none;width:34px;height:34px;border-radius:9px;border:2.5px solid #4A2E1F;display:flex;align-items:center;justify-content:center;font-style:normal;font-size:19px}
#mgUI .gHow .paBtn{margin:6px auto 0;font-size:19px;padding:7px 26px;min-height:46px}
@media (orientation:landscape) and (max-height:520px){ #mgUI .gHow>div{width:min(100%,700px);display:grid;grid-template-columns:1fr 1fr;column-gap:16px;padding:10px 14px} #mgUI .gHow h4,#mgUI .gHow .paBtn{grid-column:1/-1} #mgUI .gHow h4{font-size:20px;margin-bottom:5px} #mgUI .gHow p{font-size:14px;margin-bottom:6px;line-height:1.35} #mgUI .gHow p>i{width:28px;height:28px} }
@media (min-width:700px) and (min-height:900px), (min-width:1000px) and (min-height:700px){ #mgUI .gTop{zoom:1.4;padding-left:84px;padding-right:84px} #mgUI .gBan{zoom:1.3} #mgUI .mgB[data-b=jump]{width:140px;height:140px;font-size:32px} #mgUI .gRoom,#mgUI .gHow>div,#mgUI .gIntro{zoom:1.3} #mgUI .gCombo{font-size:46px} #mgUI .gFl{font-size:30px} }
</style>
<div class="gHurt"></div><div class="gTop"><span class="paPill sg"></span><span class="paPill tm"></span><span class="paPill sc"></span><span class="paPill lv"></span><span class="paPill bl"><i></i><div class="b"><i></i></div><b></b></span></div><div class="paBan gBan"></div><div class="gCombo"></div><div class="gCnt"></div><div class="paPill gOut">👀 구경 중 — 다음 판에 ❤️ 를 다시 채워서 들어가요</div><div class="gRoom" style="display:none"></div>
<div class="gIntro"><div><b style="background:#2f8cff"></b>파란 칸 = 밟아서 지우기</div><div><b style="background:#ff2d55"></b>빨간 칸이 오면 = 점프로 넘거나 피하기</div><div><b style="background:#ff9a3d"></b>주황 깜빡 = 곧 빨강이 와요</div><div><b style="background:#2fd866"></b>초록 칸 = 안전 (판마다 바뀌고 줄어요)</div><div><b style="background:#d23dff"></b>높은 보라 벽 = 점프로 못 넘어요 · 틈으로!</div></div>`;
  const Q=s=>hud.querySelector(s), eSg=Q(".sg"), eTm=Q(".tm"), eLv=Q(".lv"), eBl=Q(".bl"), eSc=Q(".sc"), eIn=Q(".gIntro"), eHurt=Q(".gHurt"), eCb=Q(".gCombo"), eRoom=Q(".gRoom"), eCnt=Q(".gCnt"), eOut=Q(".gOut"), eBan=Q(".gBan"), eBlB=eBl.querySelector(".b i"), eBlN=eBl.querySelector("b");
  const IC=(n,px)=>{ try{ return PUI.ic(n,px); }catch(e){ return ""; } };
  if(CO || MENU) eIn.style.display="none"; if(MENU) api.ui.classList.add("gMenuOn"); else api.ui.classList.remove("gMenuOn"); api.ui.classList.remove("gEnd");
  let hudK="", scS=-1;
  function drawHud(){ const play=st.phase==="play"; eSg.textContent=play?(st.stage+1)+" 판":CO?"👫 같이 하기":"🟦"; const L=Math.max(0,st.lives), M=DF[DFK].life, k=L+"/"+M;
    if(k!==hudK){ const lost=hudK && L<(+hudK.split("/")[0]); hudK=k; eLv.innerHTML=(IC("heart",24)||"❤️").repeat(L)+(IC("heart0",24)||"🤍").repeat(Math.max(0,M-L)); if(lost){ const h=eLv.children[L]; if(h) h.classList.add("pop"); } }
    eBl.style.display=play?"":"none"; eBlN.textContent=st.blue; eBlB.style.width=(st.blue0?Math.round((1-st.blue/st.blue0)*100):0)+"%";
    if(st.score!==scS){ if(scS>=0 && st.score>scS){ eSc.classList.remove("bump"); void eSc.offsetWidth; eSc.classList.add("bump"); } scS=st.score; eSc.innerHTML=(CO?"🤝":(IC("star",22)||"⭐"))+"<b>"+st.score.toLocaleString()+"</b>"; } }
  let tmS=-1; function drawTime(){ const s=Math.ceil(st.left); if(s===tmS) return; tmS=s; eTm.innerHTML=(IC("clock",22)||"⏱")+"<b>"+s+"</b>"; eTm.classList.toggle("low", s<=10 && st.phase==="play"); if(s<=5 && s>0 && !st.over && st.phase==="play") api.sfx.tick(); }

  /* ══════════ 👫 같이 하기 (방 · 대기 · 동기화) ══════════ */
  const NETOK=typeof NET!=="undefined", code=(()=>{ try{ return myCode; }catch(e){ return "ME"+Math.floor(Math.random()*999); } })(), nm=api.nick;
  const now=()=>{ try{ return srvNow(); }catch(e){ return Date.now(); } };
  const day=()=>{ try{ return dayKey().replace(/\D/g,""); }catch(e){ return "0"; } };
  const BASE=()=>"/hy/day/mgg"+day();
  const R={id:null, path:null, d:null, peers:{}, sendT:0, pollT:0, listT:0, rooms:[], busy:false, host:false, lastSent:null, gone:false, endSent:false};
  function roomUI(){ if(!CO) return; if(st.phase!=="room" && st.phase!=="wait"){ eRoom.style.display="none"; return; } eRoom.style.display="";
    if(st.phase==="room"){ const L=R.rooms;
      eRoom.innerHTML='<h4>👫 같이 하기 <small style="font-size:13px;opacity:.8">(최대 '+MAXP+'명)</small></h4><div class="sub">친구 방에 들어가거나, 내 방을 만들어요</div><div class="rl">'+(L.length?L.map(r=>'<button class="puBtn" data-j="'+r.id+'">🟦 '+esc(r.n)+'의 방 · '+(DF[r.df]||DF.normal).ic+' '+(DF[r.df]||DF.normal).nm+' · '+r.c+'/'+MAXP+'명</button>').join(""):'<div class="sub">아직 열린 방이 없어요</div>')+'</div><button class="puBtn mt go" data-mk="1">＋ 내 방 만들기</button><button class="puBtn gr" data-bk="1">☰ 메뉴</button>'; }
    else { const d=R.d||{}, h=d.h||{}, ps=livePeers(true), cnt=ps.length, st0=h.st||0;
      eRoom.innerHTML='<h4>🟦 '+esc(h.n||"")+'의 방 <small style="font-size:14px">'+(DF[h.df]||DF.normal).ic+' '+(DF[h.df]||DF.normal).nm+'</small></h4><div class="pl">'+ps.map(p=>'<span class="'+(p.k===code?"me":"")+'">'+(p.k===h.c?"👑 ":"")+esc(p.n)+'</span>').join("")+'</div><div class="sub">'+cnt+' / '+MAXP+'명 · 기다리는 동안 바닥에서 걸어 봐요</div>'+
        (st0?'<div class="sub">곧 시작해요!</div>':R.host?'<button class="puBtn pk go" data-st="1">▶ 게임 시작 (10초 뒤)</button>':'<div class="sub">방장(👑)이 「게임 시작」을 누르면 10초 뒤 시작해요</div>')+'<button class="puBtn gr" data-lv="1">방 나가기</button>'; } }
  const esc=s=>String(s==null?"":s).replace(/[<>&"]/g,c=>({"<":"&lt;",">":"&gt;","&":"&amp;",'"':"&quot;"}[c]));
  eRoom.addEventListener("click", e=>{ const b=e.target.closest("button"); if(!b || R.busy) return; try{ api.sfx.tick(); }catch(_){} if(b.dataset.bk){ api.restart({}); return; } if(b.dataset.mk) mkRoom(); else if(b.dataset.j) joinRoom(b.dataset.j); else if(b.dataset.st) startRoom(); else if(b.dataset.lv) leaveRoom(true); });
  eRoom.addEventListener("pointerdown", e=>e.stopPropagation());
  function meNode(){ return {n:nm, av:api.av||{}, x:+P.p.x.toFixed(2), z:+P.p.z.toFixed(2), y:+P.p.y.toFixed(2), f:+P.face.toFixed(2), l:st.lives, o:st.out?1:0, t:now()}; }
  async function listRooms(){ if(!NETOK) return; let d=null; try{ d=await NET.get(BASE()); }catch(e){ return; } const t=now(), L=[];
    Object.keys(d||{}).forEach(id=>{ const r=d[id]; if(!r || !r.h || r.h.st) return; if(t-(r.h.hb||0)>15000) return; const c=Object.values(r.p||{}).filter(p=>p && t-(p.t||0)<10000).length; if(c<MAXP) L.push({id, n:r.h.n||"친구", c, df:r.h.df||"normal"}); });
    R.rooms=L.sort((a,b)=>b.c-a.c).slice(0,6); if(st.phase==="room") roomUI(); }
  async function mkRoom(){ if(!NETOK){ api.msg("서버에 연결이 안 돼요<small>혼자 하기로 해 봐요</small>", 1800); return; } R.busy=true; const id=code+"_"+(Date.now()%100000);
    R.id=id; R.path=BASE()+"/"+id; R.host=true; const h={c:code, n:nm, st:0, hb:now(), at:now(), df:DFK};
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
  function dropPeer(pp){ if(pp.c) scene.remove(pp.c.g); if(pp.tag) scene.remove(pp.tag); if(pp.ring) scene.remove(pp.ring); }
  function authority(){ const d=R.d||{}, h=d.h||{}, L=livePeers(true).map(p=>p.k); if(L.indexOf(h.c)>=0) return h.c===code; return L[0]===code; }   /* 방장이 나가면 남은 아이 중 첫 번째가 판을 넘김 */
  async function poll(){ if(!R.path || R.busy) return; let d=null; try{ d=await NET.get(R.path); }catch(e){ return; } if(!R.path) return;
    if(!d || !d.h){ if(st.phase==="wait"){ api.msg("방이 닫혔어요", 1400); leaveRoom(true); } return; } R.d=d; applyRoom(); }
  function applyRoom(){ const d=R.d, h=d.h, t=now();
    /* 친구 모습 */
    const seen={}; Object.keys(d.p||{}).forEach(k=>{ if(k===code) return; const p=d.p[k]; if(!p || t-(p.t||0)>10000) return; seen[k]=1; let pp=R.peers[k];
      const col=PCOL[slotOf(k)]; if(pp && pp.col!==col){ dropPeer(pp); delete R.peers[k]; pp=null; }
      if(!pp){ st.tk=0; pp=R.peers[k]={c:avatar(p.av, 1.8), tag:tag(p.n||"친구", col), ring:ring(new THREE.Color(col).getHex()), col, x:p.x||0, z:p.z||0, y:0}; } pp.tx=p.x||0; pp.tz=p.z||0; pp.ty=p.y||0; pp.f=p.f||0; pp.o=!!p.o; pp.n=p.n; });
    Object.keys(R.peers).forEach(k=>{ if(!seen[k]){ dropPeer(R.peers[k]); delete R.peers[k]; } });
    if(st.phase==="wait"){ if(h.df && DF[h.df] && h.df!==DFK){ DFK=h.df; st.lives=DF[DFK].life; } if(h.st){ st.seed=h.seed>>>0; st.lives=DF[DFK].life; st.phase="count"; } roomUI(); drawHud(); }
    if(st.phase==="play" && h.sg && h.sg.s>st.stage && t>=h.sg.at) newStage(h.sg.s);
    /* 밟은 칸 (모두의 것) */
    if(st.phase==="play"){ const gp="g"+st.stage+"_"; Object.keys(d.c||{}).forEach(key=>{ if(key.indexOf(gp)===0) GT.add(+key.slice(gp.length)); }); }
    if(st.phase==="play"){ const pre=st.stage+"_"; let n=0; Object.keys(d.c||{}).forEach(key=>{ if(key.indexOf(pre)!==0) return; const q=+key.slice(pre.length); if(cell[q]===1){ cell[q]=3; st.blue--; } });
      teamScore(); drawHud(); }
    if(h.end && !st.over) end(); }
  function teamScore(){ const d=R.d||{}; let n=0; Object.keys(d.c||{}).forEach(k=>{ n+=k.charAt(0)==='g'?5:1; }); const h=d.h||{}; st.score=n*10+((h.sg && h.sg.s)|0)*50; }
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
    if(pp.tag){ pp.tag.position.set(pp.x, pp.y+(pp.o?.4:3.5), pp.z); pp.tag.material.opacity=pp.o?.45:1; } if(pp.ring){ pp.ring.position.set(pp.x,.15,pp.z); pp.ring.visible=!pp.o; } }); }

  /* ── 움직임 · 칸 밟기 ── */
  const camT=new V3(); let camInit=false, paused=false;
  function idxAt(x,z){ const i=Math.floor((x+HALF)/TS), j=Math.floor((z+HALF)/TS); if(i<0||j<0||i>=N||j>=N) return -1; return j*N+i; }
  function hit(){ if(P.inv>0 || st.over || st.out) return; st.lives--; st.nohit=false; P.inv=1.6; st.combo=0; st.flash=.5; st.shake=.45; api.sfx.bad(); drawHud();
    ripple(idxAt(P.p.x,P.p.z), COL.red, 1.3, .8); burst(P.p.x, P.p.z, 0xff5a7a, 12, 6); floatTxt(P.p.x, 2.4, P.p.z, "−❤", "r"); P.sq=-.35;
    if(me){ try{ emote(me, "💦"); }catch(e){} }
    if(st.lives<=0){ if(CO){ st.out=true; api.msg('👀 ❤️ 다 썼어요<small>친구들을 응원하다가 다음 판에 다시 들어가요</small>', 2000); return; } end(); return; }
    api.msg('앗! ❤️ '+st.lives+'개 남았어요<small>잠깐 반짝이는 동안은 안전해요</small>', 1200); }
  function clearTile(id){ cell[id]=3; st.blue--; st.steps++; st.combo=st.comboT>0?st.combo+1:1; st.comboT=1.1; api.sfx.tile(st.combo); if(st.combo>st.best) st.best=st.combo;
    { const x=cx(id%N), z=cx(Math.floor(id/N)); ripple(id, 0x9fd4ff, .55+Math.min(.5,st.combo*.06), .5); burst(x, z, st.combo>=5?0xffe14d:0x6fc0ff, st.combo>=5?8:5, 4); if(!CO) floatTxt(x, 1.2, z, "+"+(10+Math.min(10,(st.combo-1)*2)), st.combo>=5?"g":""); }
    if(CO){ if(R.path){ R.d.c=R.d.c||{}; R.d.c[st.stage+"_"+id]=code; NET.put(R.path+"/c/"+st.stage+"_"+id, code).catch(()=>{}); } teamScore(); }
    else { const pts=10+Math.min(10,(st.combo-1)*2); st.score+=pts; if(st.combo>=3){ eCb.textContent="콤보 ×"+st.combo; eCb.style.opacity=1; eCb.classList.remove("pop"); void eCb.offsetWidth; eCb.classList.add("pop"); clearTimeout(eCb._t); eCb._t=setTimeout(()=>eCb.style.opacity=0, 700); } }
    drawHud(); }
  function step(dt, live){ const I=api.I;
    let mx=I.mx, mz=-I.my; const m=Math.hypot(mx,mz); if(m>1){ mx/=m; mz/=m; }
    P.p.x+=mx*SPD*dt; P.p.z+=mz*SPD*dt; const lim=HALF-.3; P.p.x=Math.max(-lim,Math.min(lim,P.p.x)); P.p.z=Math.max(-lim,Math.min(lim,P.p.z));
    if(m>.1) P.face=Math.atan2(mx,mz);
    if((I.jumpP || I.jump) && P.onG){ P.vy=JV; P.onG=false; P.sq=.3; api.sfx.jump(); }
    if(!P.onG){ P.vy-=GRAV*dt; P.p.y+=P.vy*dt; if(P.p.y<=0){ P.p.y=0; P.vy=0; P.onG=true; P.sq=-.32; LAND.t=0; LAND.m.position.set(P.p.x,.17,P.p.z); try{ api.sfx.land(); }catch(e){} ripple(idxAt(P.p.x,P.p.z), null, .45, .45); } }
    P.sq=(P.sq||0)*Math.max(0, 1-dt*9);
    P.inv=Math.max(0,P.inv-dt);
    if(!live || st.out) return;
    const id=idxAt(P.p.x,P.p.z);
    if(id>=0){ if(P.onG && cell[id]===1) clearTile(id); if(P.onG){ const gi=goldAt(id); if(gi>=0) takeGold(gi); } if(red[id] && cell[id]!==2 && (P.onG || (hi[id] && P.p.y<1.6))) hit(); }   /* 🟪 높은 것은 점프해도 맞음 */
    st.comboT=Math.max(0, st.comboT-dt); }
  function greenOff(){ const GO=st.pl && st.pl.GO; if(!GO || st.goS===st.stage || st.el<GO.t) return; st.goS=st.stage; GO.L.forEach(q=>{ if(cell[q]===2) cell[q]=0; }); api.msg('🟩 초록 칸이 줄었어요!<small>남은 초록으로 가요</small>', 1500); try{ api.sfx.bad(); }catch(e){} }
  const isHeart=i=>i===1 && st.stage>=1 && st.lives<DF[DFK].life && !st.out;
  const PK=[]; ["⭐","❤️"].forEach(t=>{ const cv=document.createElement("canvas"); cv.width=cv.height=128; const g=cv.getContext("2d"); g.font="96px sans-serif"; g.textAlign="center"; g.textBaseline="middle"; g.shadowColor="rgba(10,14,50,.6)"; g.shadowBlur=10; g.fillText(t,64,70);
    const tx=new THREE.CanvasTexture(cv); tx.encoding=THREE.sRGBEncoding; disp.push(tx); const sp=new THREE.Sprite(new THREE.SpriteMaterial({map:tx, depthWrite:false, transparent:true})); sp.scale.set(1.5,1.5,1); sp.visible=false; sp.renderOrder=4; scene.add(sp); PK.push(sp); });
  function pickTick(){ PK[0].visible=PK[1].visible=false; const L=st.pl && st.pl.GD; if(!L || st.phase!=="play" || st.over) return; for(let i=0;i<L.length;i++){ const g=L[i]; if(goldAt(g.q)!==i) continue; const sp=PK[isHeart(i)?1:0], left=g.t0+g.dur-st.el; sp.visible=left>1.2 || Math.sin(st.t*22)>0; sp.position.set(cx(g.q%N), 1.5+Math.sin(st.t*5)*.22, cx(Math.floor(g.q/N))); const k=1.5+Math.sin(st.t*7)*.12; sp.scale.set(k,k,1); break; } }
  function takeGold(i){ const hrt=isHeart(i); GT.add(i); st.gold++; try{ api.sfx.clear(); }catch(e){} { const q=st.pl.GD[i].q, x=cx(q%N), z=cx(Math.floor(q/N)); ripple(q, hrt?0xff7aa8:COL.gold, 1.2, .9); burst(x, z, hrt?0xff7aa8:0xffe14d, 16, 7); floatTxt(x, 1.6, z, hrt?"❤ +1":"⭐ +50", hrt?"r":"g"); }
    if(hrt){ st.lives++; if(me){ try{ emote(me, "❤️"); }catch(e){} } api.msg('❤️ 하나 더!<small>하트 칸을 밟았어요</small>', 1100); if(!CO){ drawHud(); return; } }
    if(CO){ if(R.path){ R.d.c=R.d.c||{}; R.d.c["g"+st.stage+"_"+i]=code; NET.put(R.path+"/c/g"+st.stage+"_"+i, code).catch(()=>{}); } teamScore(); } else st.score+=50; drawHud(); }
  function stageClear(){ if(st.clrS===st.stage) return; st.clrS=st.stage; st.cleared++; st.clearT=2.4; api.sfx.clear(); if(me) me.act="yay";
    for(let k=0;k<5;k++) burst((Math.random()-.5)*HALF*1.6, (Math.random()-.5)*HALF*1.6, [0xff5a7a,0xffe14d,0x5fe08a,0x6fc0ff,0xc58bff][k], 9, 9);
    if(CO){ teamScore(); api.msg('<b class="gStg">🎉 다 같이 깼다!</b><small>🤝 +50</small>', 1900); }
    else { const pf=st.nohit?100:0, b=Math.ceil(st.left)*2+20; st.score+=b+pf; if(pf){ st.perf=(st.perf||0)+1; floatTxt(P.p.x, 2.6, P.p.z, "퍼펙트 +100", "g"); } api.msg('<b class="gStg">'+(pf?'🌟 퍼펙트! ':'🎉 ')+(st.stage+1)+' 판 깼다!</b><small>남은 시간 보너스 ⭐ +'+b+(pf?' · 안 맞고 깨기 ⭐ +100':'')+'</small>', 1900); } drawHud(); }
  function end(){ if(st.over) return; st.over=true; const reached=st.stage+1;
    if(CO && R.path && NETOK){ NET.del(R.path+"/p/"+code).catch(()=>{}); }
    const who=CO ? livePeers(true).map(p=>p.n||"친구") : [];
    const b0=(()=>{ try{ return Object.assign({}, MG.rec().b.grid||{}); }catch(e){ return {}; } })();
    eBan.classList.remove("on"); if(me) me.act=reached>=3?"yay":"idle";
    setTimeout(()=>{ if(R.gone) return; const coins=reached>=5?15:reached>=3?10:5;
      const got=PUI.award(api, CO ? {title:'🤝 함께 ⭐ '+st.score+'점!', sub:reached+' 판까지', rows:null, coins, upd:(b,t)=>{ if(st.score>(b.co|0)) b.co=st.score; if(reached>(b.st|0)) b.st=reached; t.tiles=(t.tiles|0)+st.steps; t.co=(t.co|0)+1; }}
        : {title:reached+' 판까지', sub:'⭐ '+st.score, rows:null, coins, upd:(b,t)=>{ if(st.score>(b.sc|0)) b.sc=st.score; if(reached>(b.st|0)) b.st=reached; t.tiles=(t.tiles|0)+st.steps; }});
      let left=3; try{ left=MG.payLeft("grid"); }catch(e){}
      const stars=reached>=5?3:reached>=3?2:reached>=2?1:0, newSt=reached>(b0.st|0), newSc=CO ? st.score>(b0.co|0) : st.score>(b0.sc|0);
      api.ui.classList.add("gMenuOn");
      PUI.result(hud, {res:(stars>0||CO)?"win":"lose", stars, title:CO?"함께 "+reached+" 판까지!":reached+" 판까지!", av:api.av,
        sub:DF[DFK].ic+" "+DF[DFK].nm+" · "+(CO ? "👫 "+who.map(esc).join(" · ") : (st.lives>0?"⏰ 시간이 다 됐어요":"❤️ 를 다 썼어요")+" · 지운 칸 "+st.steps),
        rewards:[["🪙", got>0?"+"+got:"0", got>0?"코인":"오늘 상 끝"], [CO?"🤝":"star", st.score.toLocaleString(), CO?"다 같이":"점수", newSc], CO?["🟦", st.steps, "내가 지운 칸"]:["🔥", "×"+st.best, "최고 콤보"]],
        extra:newSt?'🏆 <b style="color:#ffd860">최고 기록! '+reached+' 판</b>':reached<3?'다음엔 <b style="color:#ffd860">3판</b>까지 가 봐요 (🪙 10)':reached<5?'<b style="color:#ffd860">5판</b>까지 가면 🪙 15':'',
        prog:{t:"오늘 🪙 상 "+(3-left)+" / 3판", v:(3-left)/3},
        onAgain:()=>api.restart({mode:CO?"co":"solo", df:DFK}), onMenu:()=>api.restart({})}); }, 1100); }

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
        greenOff(); hzAt(st.pl.H, st.el, cell, red, warn, hi); if(st.blue<=0) stageClear(); }
      step(dt, st.clrS!==st.stage); if(st.blue<=0 && st.clrS!==st.stage && !st.over) stageClear(); }
    else if(st.phase!=="play") step(dt, false);
    eOut.style.display=st.out && !st.over?"block":"none";
    drawTime();
    { let t="🟦 발판 게임", col="#7fe0ff"; if(st.phase==="play" && st.pl){ t=(st.stage+1)+"판 "+LED_T[st.pl.th]; for(const h of st.pl.H){ const u=st.el-h.t0; if(h.sig && u>=0 && u<h.w+1.2){ t=HZ_NM[h.sig]||t; col=u<h.w?"#ff9a3d":"#ff2d55"; } } if(st.clrS===st.stage){ t="🎉 판 깼다!"; col="#2fd866"; } }
      else if(st.phase==="count"){ t="곧 시작!"; col="#ffd23f"; } else if(CO){ t="👫 같이 하기"; } ledDraw(t, col);
      const hz=col==="#ff9a3d"||col==="#ff2d55"; if(hz && !st.over){ if(eBan.textContent!==t){ eBan.textContent=t; eBan.classList.remove("pop"); void eBan.offsetWidth; eBan.classList.add("pop"); } eBan.classList.toggle("y", col==="#ff9a3d"); eBan.classList.add("on"); } else eBan.classList.remove("on"); }
    const blink=(Math.sin(st.t*18)>0), pulse=.85+.15*Math.sin(st.t*5), party=st.phase==="play" && st.clrS===st.stage && st.clearT>0, demo=st.phase!=="play";
    st.wipe+=dt; for(let k=FXR.length-1;k>=0;k--){ FXR[k].t+=dt; if(FXR[k].t>FXR[k].L) FXR.splice(k,1); }
    for(let q=0;q<N*N;q++){ const i=q%N, j=(q-i)/N; let c=COL.off, k=1, glow=0; const isRed=!!red[q], tall=isRed && !!hi[q], hk=tall?2:isRed?1:0;
      if(hk!==HT[q]){ HT[q]=hk; _m.makeTranslation(cx(i), tall?.8:isRed?.07:.02, cx(j)); if(tall) _m.scale(_s.set(1,7.6,1)); else if(isRed) _m.scale(_s.set(1,1.5,1)); T.setMatrixAt(q,_m); T.instanceMatrix.needsUpdate=true; }
      if(isRed){ c=hi[q]?COL.hi:COL.red; glow=.75; k=.92+.08*Math.sin(st.t*14+i+j); } else if(warn[q]){ c=blink?COL.warn:COL.off; glow=blink?.5:0; } else if((GI=goldAt(q))>=0){ c=isHeart(GI)?0xff7aa8:COL.gold; k=.8+.4*Math.abs(Math.sin(st.t*9)); glow=.9; } else if(cell[q]===1){ c=COL.blue; k=pulse; glow=.42; } else if(cell[q]===2){ c=COL.green; glow=.5; k=.94+.06*Math.sin(st.t*3+i*.7+j*.5); } else if(cell[q]===3) c=COL.done;
      _c.setHex(c).convertSRGBToLinear(); if(k!==1) _c.multiplyScalar(k);
      if(party || demo){ const h=((i+j)*.045+st.t*(party?.9:.18))%1; _w.setHSL(h, 1, party?.56:.5).convertSRGBToLinear(); if(party){ _c.copy(_w); glow=.7; } else if(cell[q]!==2){ const f=.5+.5*Math.sin(st.t*1.6-(Math.hypot(i-6.5,j-6.5))*.8); _c.lerp(_w, .55*f); glow=.35*f; } }
      if(st.wipe<1.1){ const f=st.wipe*22-(i+j)*.6; if(f<0){ _c.multiplyScalar(.25); glow*=.2; } else if(f<1.6){ _c.lerp(_w.setRGB(1,1,1), .7*(1-f/1.6)); glow=Math.max(glow,.6); } }
      for(let z=0;z<FXR.length;z++){ const r=FXR[z], d=Math.hypot(i-r.i,j-r.j), w=1-Math.abs(d-r.t*11)/1.25; if(w>0){ const f=Math.min(.85, w*(1-r.t/r.L)*r.p); if(r.c) _c.lerp(r.c, f); else _c.lerp(_w.setRGB(1,1,1), f*.75); glow=Math.max(glow, f*.7); } }
      T.setColorAt(q, _c); if(GLW){ GLW.setColorAt(q, _w.copy(_c).multiplyScalar(glow)); } }
    T.instanceColor.needsUpdate=true; if(GLW) GLW.instanceColor.needsUpdate=true;
    partTick(dt);
    /* 조명 · 빛 기둥 · 구슬 */
    { const low=st.phase==="play" && st.left<=10 && !st.over, beat=.5+.5*Math.sin(st.t*5.2);
      FXL.beams.forEach(o=>{ o.p.rotation.x=.42+Math.sin(st.t*.7+o.k*1.3)*.3; o.p.rotation.z=Math.sin(st.t*.5+o.k*2.1)*.5; });
      if(FXL.barM){ for(let n=0;n<FXL.bars.length;n++){ const o=FXL.bars[n], h=1+2.6*Math.abs(Math.sin(st.t*2.6+o.k*.55))*(.55+.45*Math.sin(st.t*1.3+o.k)); _m.compose(_p.set(o.x,0,o.z), _q.identity(), _s.set(1,h,1)); FXL.barM.setMatrixAt(n,_m);
          if(low) _c.setHex(Math.sin(st.t*10)>0?0xff2d55:0x5a1030); else _c.setHSL((o.k*.035+st.t*.05+(o.side>0?.5:0))%1, .9, .58); FXL.barM.setColorAt(n, _c.convertSRGBToLinear()); } FXL.barM.instanceMatrix.needsUpdate=true; FXL.barM.instanceColor.needsUpdate=true; }
      FXL.orbs.forEach(o=>{ if(low) o.m.color.setHex(Math.sin(st.t*10)>0?0xff2d55:0x5a1030); else o.m.color.setHSL((o.k*.25+st.t*.08)%1, .9, .62+.1*beat); });
      FXL.neon[0].color.setHex(low && Math.sin(st.t*10)>0?0xff2d55:0x7fe0ff); FXL.neon[1].color.setHex(low && Math.sin(st.t*10)>0?0xff2d55:0xff6bd6);
      LAND.t+=dt; { const f=LAND.t/.38; LAND.m.visible=f<1; if(f<1){ LAND.m.scale.setScalar(1+f*2.2); LAND.m.material.opacity=.8*(1-f); } } }
    if(me){ me.g.position.copy(P.p); me.face=P.face; me.moving=P.onG && Math.hypot(api.I.mx,api.I.my)>.1; try{ animChar(me, dt); }catch(e){} me.g.visible=!st.out && !(P.inv>0 && Math.sin(st.t*30)>0); const q=P.sq||0; me.g.scale.set(AVS*(1-q*.45), AVS*(1+q), AVS*(1-q*.45)); }
    { const id=idxAt(P.p.x,P.p.z); HL.visible=id>=0 && !st.out; if(id>=0) HL.position.set(cx(id%N), 0, cx(Math.floor(id/N))); }
    myTag(); const bob=Math.sin(st.t*4)*.12, tk=(cam.aspect||1)>1.3?1.75:1; MY.tag.scale.set(.21*tk,.0525*tk,1); MY.arrow.scale.set(.085*tk,.053*tk,1); if(tk!==st.tk){ st.tk=tk; Object.values(R.peers).forEach(pp=>{ if(pp.tag) pp.tag.scale.set(.19*tk,.0475*tk,1); }); } MY.tag.position.set(P.p.x, P.p.y+3.5, P.p.z); MY.arrow.position.set(P.p.x, P.p.y+3.5+bob*.3, P.p.z); MY.arrow.center.y=(CO?-1.02:-.1)-Math.abs(bob)*.8; MY.ring.position.set(P.p.x,.16,P.p.z); MY.ring.scale.setScalar(1+Math.sin(st.t*5)*.06); MY.arrow.visible=MY.ring.visible=!st.out; MY.tag.visible=!st.out && !!CO;   /* (v659) 혼자 할 땐 이름 알약이 캐릭터를 가려서 뺌 */ pickTick();
    shadowD.position.set(P.p.x,.13,P.p.z); shadowD.scale.setScalar(1-Math.min(.5,P.p.y*.3)); shadowD.visible=!st.out;
    st.flash=Math.max(0,st.flash-dt); eHurt.style.opacity=st.flash>0?1:0;
    const asp=cam.aspect||1, port=asp<1, W=asp<.6?8.6:HALF+1.4, tv=Math.tan(cam.fov*Math.PI/360), d=Math.max(15, Math.min(48, W/(tv*Math.min(asp,1.45)))), pit=port?.84:.8;
    const fx=Math.max(0, HALF+1.2-W), tx=Math.max(-fx, Math.min(fx, P.p.x*.8)), tz=P.p.z*(asp<.6?.45:.25)+(asp<.6?1.6:asp<1?-.4:1.4); if(!camInit){ camT.set(tx,0,tz); camInit=true; } camT.x+=(tx-camT.x)*Math.min(1,dt*3); camT.z+=(tz-camT.z)*Math.min(1,dt*3);
    st.shake=Math.max(0, st.shake-dt); const sk=st.shake*st.shake*2.2, sx=sk*Math.sin(st.t*71), sy=sk*Math.cos(st.t*83);
    cam.position.set(camT.x+sx, Math.sin(pit)*d+sy, camT.z+Math.cos(pit)*d); cam.lookAt(camT.x+sx*.6, 0, camT.z); }
  function howShow(){ const el=document.createElement("div"); el.className="gHow"; const sq=(c,t)=>'<i style="background:'+c+'">'+(t||"")+'</i>';
    el.innerHTML='<div><h4>🟦 놀이 방법</h4><p>'+sq("#2f8cff")+'<span><b>파란 칸</b>을 모두 밟으면 다음 판! 판이 넘어갈수록 빨라져요</span></p><p>'+sq("#ff2d55")+'<span><b>빨간 칸</b>이 오면 점프로 넘거나 피해요. 밟으면 ❤️ 하나</span></p><p>'+sq("#ff9a3d")+'<span><b>주황 깜빡</b> = 곧 빨강이 와요</span></p><p>'+sq("#d23dff")+'<span><b>높은 보라 벽</b>은 점프로 못 넘어요. 틈으로 달려요</span></p><p>'+sq("#2fd866")+'<span><b>초록 칸</b>은 안전해요. 판마다 바뀌고 줄어요</span></p><p>'+sq("#ffd23f","⭐")+'<span><b>금빛 칸</b>은 잠깐만 나와요. 밟으면 +50</span></p><p>'+sq("#fff","👫")+'<span><b>같이 하기</b>는 다 같이 점수를 모아요. ❤️ 를 다 쓰면 다음 판에 다시 들어가요</span></p><button class="paBtn">알겠어요!</button></div>';
    el.addEventListener("pointerdown", e=>e.stopPropagation()); el.querySelector("button").onclick=()=>el.remove(); hud.appendChild(el); }
  function menuShow(){ let b={}, t={}; try{ const r=MG.rec(); b=r.b.grid||{}; t=r.t.grid||{}; }catch(e){}
    PUI.menu(hud, {title:"발판 게임", sub:"파란 칸은 밟고, 빨간 칸은 피해요!", av:api.av, nick:api.nick,
      stats:[["trophy",(b.st|0)+"판","내 최고"],["star",(b.sc|0).toLocaleString(),"최고 점수"]].concat(b.co?[["🤝",(b.co|0).toLocaleString(),"같이 최고"]]:[]),
      deco:[["🟦","left:8%;top:26%;font-size:34px;transform:rotate(-12deg)"],["🟥","right:9%;top:18%;font-size:30px;transform:rotate(10deg)"],["🟩","right:16%;bottom:16%;font-size:26px;transform:rotate(-8deg)"],["⭐","left:15%;bottom:20%;font-size:26px"]],
      seg:{items:Object.keys(DF).map(k=>[k, DF[k].ic+" "+DF[k].nm+(k==="easy"?" ❤️5":"")]), on:DFK, pick:k=>{ if(!DF[k]) return; DFK=k; try{ localStorage.setItem(DFKEY,k); }catch(e){} menuShow(); }},
      primary:{k:"solo", label:"혼자 하기", ic:"play"}, primaryTop:true, n:2,
      tiles:[{k:"co", emoji:"👫", bg:"#ff8fc4", nm:"친구랑 같이", sub:"최대 "+MAXP+"명 · 다 같이 점수"},{k:"how", emoji:"❓", bg:"#ffd36b", nm:"놀이 방법", sub:"칸 색깔 알아보기"}],
      pay:(()=>{ try{ return MG.payLeft("grid"); }catch(e){ return 0; } })(),
      onPick:k=>{ if(k==="how"){ howShow(); return; } try{ api.sfx.up(); }catch(e){} api.restart({mode:k, df:DFK}); }}); }
  if(MENU){ st.pl=plan(st.seed, 0, DFK); cell.set(st.pl.cell); for(let q=0;q<N*N;q++) if(cell[q]===1) cell[q]=0; st.blue=0; P.p.set(0,0,cx(N-3)); drawHud(); menuShow(); }
  else if(CO){ /* 대기 바닥: 안전 칸만 켜 둠 · 걸어 다닐 수 있음 */ st.pl=plan(st.seed, 0, DFK); cell.set(st.pl.cell); for(let q=0;q<N*N;q++) if(cell[q]===1) cell[q]=0; st.blue=0; P.p.set(cx(1),0,cx(N-2)); listRooms(); roomUI(); drawHud(); }
  else newStage(0, true);
  function dispose(){ R.gone=true; try{ api.ui.classList.remove("gMenuOn"); }catch(e){} if(CO) leaveRoom(false); disp.forEach(x=>{ try{ x.dispose(); }catch(e){} }); }
  return {scene, cam, tick, dispose, pause:(v)=>{ paused=!!v; }, menuShow, howShow, get DFK(){ return DFK; }, st, P, cell, red, warn, newStage, idxAt, N, TS, HALF, cx, R, plan, hzAt, mkRoom, joinRoom, startRoom, listRooms, poll, code}; }

MG.reg("grid", {menu:true, ic:"🟦", nm:"발판 게임", tag:"LED 바닥 · 밟고 · 피하고 · 점프 · 친구랑 같이 (최대 6명)", bg:"linear-gradient(135deg,#252a5c,#10123a)", big:"🟦🟥🟩",
  how:[["🟦","<b>파란 칸</b>을 모두 밟으면 다음 판 (점점 빨라져요)"],["🟥","<b>빨간 줄·고리·🌀 선풍기</b>가 오면 점프로 넘거나 피하기 · 판마다 무늬가 달라요"],["🟪","<b>높은 보라 벽·굵은 줄</b>은 점프로 못 넘어요 → 틈으로 달려요"],["🟩","<b>초록 칸</b> = 안전 · 판마다 바뀌고 점점 줄어요"],["❤️","3번 맞으면 끝 (같이 하기는 구경하다 다음 판에 다시)"],["👫","같이 하기 = 친구 방에 들어가거나 방 만들기 · 방장이 시작 → 10초 뒤 · 다 같이 얻은 점수"]],
  opts:[{k:"mode", t:"어떻게 할까요?", d:"solo", v:[["solo","🙋 혼자 하기"],["co","👫 같이 하기 (최대 6명)"]]},{k:"df", t:"난이도 (같이 하기는 방장 것)", d:"normal", v:[["easy","🐣 쉬움 ❤️5"],["normal","🙂 보통"],["hard","🔥 어려움"]]}],
  payTxt:"5판 🪙15 · 3판 🪙10 · 참가 🪙5",
  bestTxt:(b,t)=>'🏆 최고 '+(b.st|0)+'판 · ⭐ '+(b.sc|0)+(b.co?' · 🤝 같이 최고 '+b.co+'점':'')+' · 지운 칸 모두 '+(t.tiles|0)+'개',
  ui:{look:false, btns:[{b:"jump", ic:"점프", t:"⤒"}]},
  start});
})();
