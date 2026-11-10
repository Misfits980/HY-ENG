/* ═════════ 🃏 컬러팡 — 🎡 놀이 섬 가운데 카드 카페
   (v633) 사용자: 「우노 이런 거 못 만드나?」 → 「그림 바꾸는 게 좋지 않을까? 우노인데?」 → 「영어 굳이 안 넣어도 되니까 개선판」
                → 「스타2 · 테이블탑 시뮬레이터도 참고」 → 「만들어 주고 더 개선할 게 없는지 생각해 봐」
   (v634) 사용자: 「5번까지다」 = ① 👫 친구랑 같이(최대 4명 · 빈자리 봇) ② 🎴 카드 뒷면 모으기 ③ 🎯 오늘의 카드 미션 ④ 📖 첫 판 따라 하기 ⑤ ⚙️ 규칙 고르기(+2 쌓기 · 시작 카드 7/5장)
   · 그림·데이터·CSS = mg-card-art.js (window.CPA)
   · 흐름 = 「일(action)」 하나씩: 혼자 = 바로 apply · 같이 = 방장이 정하고(act) → 방 g 에 상태+최근 일 → 모두 같은 apply 로 따라 그림
     일: p 내기 · d 받기(ids) · rf 다시 섞기 · dir · sk · one · ow(한 장 기다림) · oops · pend(쌓인 수) · turn(차례, dl 마감) · pass · end
   · 메뉴(menu:true): ▶ 혼자 · 👫 같이 · 📖 배우기 · 🎯 미션 · 🎴 뒷면 · ⚙️ 규칙
   · 상: MG 공통 하루 3판 🪙 (1등 10 · 2등 6 · 3등 5 · 4등 4) + 미션 🪙
   시험 손잡이: MG.run.G · .phase · .auto · .fast · .tapCard · .myDraw · .callOne · .menuGo(k) · .sync */
(function(){
"use strict";
const A=window.CPA; if(!A) return;
const {INK, CREAM, COL, KO, CS, esc, shp, cardSVG, icSVG, mkDeck, isW, shuffle, josa, kname, ORDV, ACTC, league, BOTS, EMOS, EMO_X, BACKS, BACK, backVal, backOpen, MISS, missToday}=A;
const DECK=mkDeck(), CARD=id=>DECK[id];
const TURN_T=30, ONE_T=2.4;
const st=(k,v)=>{ try{ return typeof store==="function" ? store(k,v) : (v===undefined?JSON.parse(localStorage.getItem(k)||"null"):localStorage.setItem(k,JSON.stringify(v))); }catch(e){ return null; } };
const dayK=()=>{ try{ return dayKey().replace(/\D/g,""); }catch(e){ const d=new Date(Date.now()+9*3600e3); return d.toISOString().slice(0,10).replace(/-/g,""); } };

function start(api){
  const SFX=api.sfx, LOW=!!api.low || (window.GUARD && GUARD.lv>=2), O=api.opt||{};
  api.menu=true; api.ui.classList.add("cpOn"); A.css();
  let gone=false, paused=false, fast=0, auto=false;
  const disp=[];
  const SET=Object.assign({df:"normal", hs:7, stk:0, bk:"base"}, st("hyeng_proto_cpset")||{});
  const saveSet=()=>st("hyeng_proto_cpset", SET);
  /* ── 시간 (멈춤 지킴) ── */
  const TM=[]; const later=(s,fn)=>TM.push({t:s,fn}); const wait=s=>new Promise(r=>later(fast?Math.min(s,.02):s, r));
  const now=()=>{ try{ return srvNow(); }catch(e){ return Date.now(); } };

  /* ══ 3D 카페 ══ */
  const scene=new THREE.Scene(); scene.background=new THREE.Color(0x3a2630); scene.fog=new THREE.Fog(0x3a2630, 8, 17);
  const cam=new THREE.PerspectiveCamera(50, 1, .05, 40);
  scene.add(new THREE.HemisphereLight(0xfff0e0, 0x6a4450, .62));
  { const rim=new THREE.DirectionalLight(0xc8dcff,.45); rim.position.set(0,3.5,-6); scene.add(rim); }
  const sun=new THREE.DirectionalLight(0xffe2c0,.78); sun.position.set(2.5,6,3); scene.add(sun); scene.add(sun.target);
  if(!LOW){ sun.castShadow=true; sun.shadow.mapSize.set(1024,1024); Object.assign(sun.shadow.camera,{left:-3.2,right:3.2,top:3.2,bottom:-3.2,near:1,far:14}); sun.shadow.bias=-.0008; }
  { const lp=new THREE.PointLight(0xffc98a,1.1,6,1.6); lp.position.set(0,2.8,0); scene.add(lp); }
  const toon=m=>{ try{ TOON.mat(m); }catch(e){} return m; };
  const MS=(c,o)=>{ const m=toon(new THREE.MeshStandardMaterial(Object.assign({color:c,roughness:.85},o||{}))); disp.push(m); return m; };
  const G3=g=>{ disp.push(g); return g; };
  function tex(w,h,draw){ const c=document.createElement("canvas"); c.width=w; c.height=h; draw(c.getContext("2d"),w,h); const t=new THREE.CanvasTexture(c); t.encoding=THREE.sRGBEncoding; t.anisotropy=4; disp.push(t); return t; }
  { const ft=tex(256,256,(g,w)=>{ for(let i=0;i<4;i++){ g.fillStyle=["#a8714a","#9c6842","#b07a50","#a06c45"][i]; g.fillRect(0,i*64,w,64); g.fillStyle="rgba(60,30,20,.35)"; g.fillRect(0,i*64,w,3); for(let k=0;k<2;k++) g.fillRect((i*97+k*131)%w,i*64,3,64); } }); ft.wrapS=ft.wrapT=THREE.RepeatWrapping; ft.repeat.set(12,12);
    const fl=new THREE.Mesh(G3(new THREE.PlaneGeometry(30,30)), MS(0xffffff,{map:ft})); fl.rotation.x=-Math.PI/2; fl.receiveShadow=true; scene.add(fl);
    const rug=new THREE.Mesh(G3(new THREE.CircleGeometry(2.9,40)), MS(0x5b3a7a,{roughness:.95})); rug.rotation.x=-Math.PI/2; rug.position.y=.005; rug.receiveShadow=true; scene.add(rug);
    const r2=new THREE.Mesh(G3(new THREE.RingGeometry(2.55,2.7,40)), MS(0xe0a84a)); r2.rotation.x=-Math.PI/2; r2.position.y=.007; scene.add(r2);
    const wm=MS(0x8d5a6b), wg=G3(new THREE.PlaneGeometry(14,5)), win=new THREE.MeshBasicMaterial({color:0xffd99a}); disp.push(win); const wing=G3(new THREE.PlaneGeometry(1.3,1.5));
    [[0,-6.5,0],[-6.5,0,Math.PI/2],[6.5,0,-Math.PI/2]].forEach(([x,z,r])=>{ const w=new THREE.Mesh(wg,wm); w.position.set(x,2.5,z); w.rotation.y=r; scene.add(w);
      for(let i=-1;i<=1;i++){ const q=new THREE.Mesh(wing,win); q.position.set(x+(r?(x<0?.01:-.01):i*3.6),2.4,z+(r?i*3.6:.01)); q.rotation.y=r; scene.add(q); } });
    const sg=tex(512,160,(g,w,h)=>{ g.fillStyle=INK; g.fillRect(0,0,w,h); g.strokeStyle="#ffd36b"; g.lineWidth=8; g.strokeRect(4,4,w-8,h-8); g.font="900 76px Jua,sans-serif"; g.textAlign="center"; g.textBaseline="middle"; ["컬","러","팡","!"].forEach((t,i)=>{ g.shadowColor=COL[CS[i]]; g.shadowBlur=16; g.fillStyle=COL[CS[i]]; g.fillText(t,w/2+(i-1.5)*76,h/2-8); }); g.shadowBlur=0; g.font="800 24px Jua,sans-serif"; g.fillStyle=CREAM; g.fillText("🃏 카드 카페",w/2,h-22); });
    const sgm=new THREE.MeshBasicMaterial({map:sg}); disp.push(sgm); const sign=new THREE.Mesh(G3(new THREE.PlaneGeometry(3.2,1)), sgm); sign.position.set(0,2.05,-6.45); scene.add(sign); scene.userData.sign=sign;
    const fg=G3(new THREE.BufferGeometry()); fg.setAttribute("position", new THREE.Float32BufferAttribute([-.14,0,0,.14,0,0,0,-.3,0],3)); const fm=CS.map(c=>{ const m=new THREE.MeshBasicMaterial({color:COL[c],side:THREE.DoubleSide}); disp.push(m); return m; });
    for(let i=0;i<=26;i++){ const t=i/26, m=new THREE.Mesh(fg,fm[i%4]); m.position.set(-6+t*12,3.35-Math.sin(t*Math.PI)*.5,-6.4); scene.add(m); }
    const bg=G3(new THREE.SphereGeometry(.05,6,4)), bm=new THREE.MeshBasicMaterial({color:0xfff0b0}); disp.push(bm); for(let i=0;i<30;i++){ const t=i/29, b=new THREE.Mesh(bg,bm); b.position.set(-6+t*12,4.2-Math.sin(t*Math.PI)*.35,-6.38); scene.add(b); }
    const sh=new THREE.Mesh(G3(new THREE.ConeGeometry(.42,.32,20,1,true)), MS(0xffd36b,{side:THREE.DoubleSide,emissive:0x5a3a00})); sh.position.set(0,3.9,0); scene.add(sh); }
  const TY=.66, TR=1.32, table=new THREE.Group(); scene.add(table);
  { const rim=new THREE.Mesh(G3(new THREE.CylinderGeometry(TR,TR-.04,.1,48)), MS(0x8a5a3c,{roughness:.55})); rim.position.y=TY-.05; rim.castShadow=rim.receiveShadow=true; table.add(rim);
    const ftx=tex(512,512,(g,w,h)=>{ const gr=g.createRadialGradient(w/2,h/2,10,w/2,h/2,w/2); gr.addColorStop(0,"#6fd0a0"); gr.addColorStop(1,"#3a9c70"); g.fillStyle=gr; g.fillRect(0,0,w,h); for(let i=0;i<5000;i++){ g.fillStyle="rgba(255,255,255,"+(Math.random()*.05)+")"; g.fillRect(Math.random()*w,Math.random()*h,1.5,1.5); }
      g.strokeStyle="rgba(255,255,255,.28)"; g.lineWidth=6; g.setLineDash([22,16]); g.beginPath(); g.arc(w/2,h/2,w*.36,0,7); g.stroke(); g.setLineDash([]); g.globalAlpha=.1; g.fillStyle="#fff"; g.font="900 64px Jua,sans-serif"; g.textAlign="center"; g.fillText("컬러팡!",w/2,h/2+22); });
    const felt=new THREE.Mesh(G3(new THREE.CircleGeometry(TR-.1,48)), MS(0xffffff,{map:ftx,roughness:.95})); felt.rotation.x=-Math.PI/2; felt.position.y=TY+.002; felt.receiveShadow=true; table.add(felt);
    const leg=new THREE.Mesh(G3(new THREE.CylinderGeometry(.16,.22,TY-.1,16)), MS(0x6e4430)); leg.position.y=(TY-.1)/2; table.add(leg);
    const base=new THREE.Mesh(G3(new THREE.CylinderGeometry(.6,.7,.08,24)), MS(0x6e4430)); base.position.y=.04; table.add(base); }
  const glowM=new THREE.MeshBasicMaterial({color:0x3ea2ff}); disp.push(glowM);
  { const gl=new THREE.Mesh(G3(new THREE.TorusGeometry(TR-.06,.022,6,72)), glowM); gl.rotation.x=Math.PI/2; gl.position.y=TY+.012; table.add(gl); }
  const haloM=new THREE.MeshBasicMaterial({map:tex(128,128,(g,w,h)=>{ const gr=g.createRadialGradient(w/2,h/2,w*.36,w/2,h/2,w*.5); gr.addColorStop(0,"rgba(255,255,255,0)"); gr.addColorStop(.25,"rgba(255,255,255,.9)"); gr.addColorStop(1,"rgba(255,255,255,0)"); g.fillStyle=gr; g.fillRect(0,0,w,h); }),color:0x3ea2ff,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,opacity:.3}); disp.push(haloM);
  { const h=new THREE.Mesh(G3(new THREE.PlaneGeometry(TR*2.5,TR*2.5)), haloM); h.rotation.x=-Math.PI/2; h.position.y=TY+.008; table.add(h); }
  const glowCol=new THREE.Color(0x3ea2ff), glowTo=new THREE.Color(0x3ea2ff);
  const myArc=new THREE.Group(); table.add(myArc); myArc.visible=false;
  { const a=new THREE.Mesh(G3(new THREE.TorusGeometry(TR-.02,.045,6,40,Math.PI*.42)), new THREE.MeshBasicMaterial({color:0xffe14d})); disp.push(a.material); a.rotation.x=Math.PI/2; a.rotation.z=Math.PI/2-Math.PI*.21; a.position.y=TY+.03; myArc.add(a);
    const hm=new THREE.MeshBasicMaterial({map:tex(64,32,(g,w,hh)=>{ const gr=g.createLinearGradient(0,0,0,hh); gr.addColorStop(0,"rgba(255,225,77,0)"); gr.addColorStop(1,"rgba(255,225,77,.45)"); g.fillStyle=gr; g.fillRect(0,0,w,hh); }),transparent:true,depthWrite:false,blending:THREE.AdditiveBlending}); disp.push(hm);
    const h=new THREE.Mesh(G3(new THREE.PlaneGeometry(TR*1.2,.7)), hm); h.rotation.x=-Math.PI/2; h.position.set(0,TY+.01,TR-.42); myArc.add(h); }
  /* ── 카드 물건 ── */
  const CW=.36, CH=.52, CT=.007;
  const cardGeo=(()=>{ const s=new THREE.Shape(), w=CW/2, h=CH/2, r=.035; s.moveTo(-w+r,-h); s.lineTo(w-r,-h); s.quadraticCurveTo(w,-h,w,-h+r); s.lineTo(w,h-r); s.quadraticCurveTo(w,h,w-r,h); s.lineTo(-w+r,h); s.quadraticCurveTo(-w,h,-w,h-r); s.lineTo(-w,-h+r); s.quadraticCurveTo(-w,-h,-w+r,-h);
    let g=new THREE.ExtrudeGeometry(s,{depth:CT,bevelEnabled:false,curveSegments:3}); g.rotateX(-Math.PI/2); if(g.index) g=g.toNonIndexed();
    const p=g.attributes.position, uv=g.attributes.uv, n=g.attributes.normal, cnt=p.count, tri=[];
    for(let i=0;i<cnt;i+=3){ const ny=n.getY(i); tri.push(ny>.9?1:ny<-.9?2:0); if(Math.abs(ny)>.9) for(let j=0;j<3;j++) uv.setXY(i+j,(p.getX(i+j)+w)/CW,(-p.getZ(i+j)+h)/CH); }
    const ord=tri.map((m,i)=>[m,i]).sort((a,b)=>a[0]-b[0]), idx=new Uint16Array(cnt); ord.forEach(([m,t],k)=>{ for(let j=0;j<3;j++) idx[k*3+j]=t*3+j; }); g.setIndex(new THREE.BufferAttribute(idx,1));
    let s0=0; [0,1,2].forEach(m=>{ const c=tri.filter(x=>x===m).length*3; g.addGroup(s0,c,m); s0+=c; }); return G3(g); })();
  const sideM=MS(0xfff8ea,{roughness:.6});
  /* 그림 → 이미지(미리) → 텍스처(쓸 때 · 28장까지). 뒷면은 "x|back|<뒷면>" */
  const IMG={}, TEX=new Map(), FLY=[], pileM=[];
  const key=(k,bk)=>k?(k.c||"x")+"|"+k.v:"x|back|"+(bk||SET.bk);
  function img(kk, svg){ if(IMG[kk]) return Promise.resolve(); return new Promise(res=>{ const im=new Image(); im.onload=()=>res(); im.onerror=()=>res(); im.src="data:image/svg+xml;charset=utf-8,"+encodeURIComponent(svg); IMG[kk]=im; }); }
  function loadImgs(){ const L=[]; L.push(img("x|wild",cardSVG(null,"wild")), img("x|wild4",cardSVG(null,"wild4"))); CS.forEach(c=>{ for(let n=0;n<=9;n++) L.push(img(c+"|"+n,cardSVG(c,n))); ["skip","rev","d2"].forEach(v=>L.push(img(c+"|"+v,cardSVG(c,v)))); });
    BACKS.forEach(b=>L.push(img("x|back|"+b.k, cardSVG(null,"back",150,b.k)))); return Promise.all(L); }
  const inUse=kk=>pileM.some(m=>m.userData.kk===kk) || FLY.some(f=>f.m.userData.kk===kk);
  function faceMat(k, bk){ const kk=key(k,bk); let e=TEX.get(kk); if(e){ e.used=performance.now(); return e.m; }
    const t=tex(192,276,(g)=>{ const im=IMG[kk]; try{ if(im && im.complete) g.drawImage(im,0,0,192,276); }catch(_){} }); t.anisotropy=8; const m=new THREE.MeshStandardMaterial({map:t,roughness:.55}); disp.push(m);
    e={m,t,used:performance.now()}; TEX.set(kk,e);
    if(TEX.size>28){ let old=null; for(const [q,v] of TEX) if(!/\|back\|/.test(q) && (!old || v.used<old[1].used)) old=[q,v]; if(old && !inUse(old[0])){ old[1].t.dispose(); old[1].m.dispose(); TEX.delete(old[0]); } }
    return m; }
  function cardMesh(k, faceUp, bk){ const f=faceMat(k), b=faceMat(null,bk); const m=new THREE.Mesh(cardGeo, faceUp===false?[sideM,b,f]:[sideM,f,b]); m.castShadow=!LOW; m.receiveShadow=!LOW; m.userData.kk=key(k); return m; }
  const drawPile=new THREE.Group(); drawPile.position.set(-.48,TY,.28); drawPile.rotation.y=.12; table.add(drawPile);
  const edgeM=MS(0xffffff,{map:tex(32,32,(g,w,h)=>{ g.fillStyle=CREAM; g.fillRect(0,0,w,h); g.fillStyle="#d8c7a8"; for(let i=0;i<h;i+=4) g.fillRect(0,i,w,1.5); })});
  const stack=new THREE.Mesh(G3(new THREE.BoxGeometry(CW-.01,.1,CH-.01)), [edgeM,edgeM,sideM,edgeM,edgeM,edgeM]); stack.position.y=.05; stack.castShadow=!LOW; stack.receiveShadow=true; drawPile.add(stack);
  let topBack=null;
  function setDeckBack(){ stack.material[2]=faceMat(null); if(topBack) drawPile.remove(topBack); topBack=cardMesh(null,false); topBack.position.set(.015,.102,.012); topBack.rotation.y=-.08; drawPile.add(topBack); }
  function pileH(){ const n=G.draw.length; stack.scale.y=Math.max(.08, Math.min(1, n/60)); stack.position.y=.05*stack.scale.y; if(topBack) topBack.position.y=.1*stack.scale.y+.002; drawPile.visible=n>0; }
  const disc=new THREE.Group(); disc.position.set(.36,TY,.3); table.add(disc);
  function pileAdd(k){ const m=cardMesh(k); const n=pileM.length; m.position.set((Math.random()-.5)*.08, .001+n*(CT+.0015), (Math.random()-.5)*.08); m.rotation.y=(Math.random()-.5)*(n?1.4:.2); disc.add(m); pileM.push(m);
    if(pileM.length>7){ const o=pileM.shift(); disc.remove(o); pileM.forEach((q,i)=>q.position.y=.001+i*(CT+.0015)); } }
  function pileReset(){ while(pileM.length) disc.remove(pileM.pop()); }
  /* ── 자리 (로컬 1 왼쪽 · 2 앞 · 3 오른쪽) ── */
  const chairM=MS(0xa66a42), chairD=MS(0x7a4a2c);
  function chair(G){ const c=new THREE.Group(); const B=(w,h,d,x,y,z,m)=>{ const q=new THREE.Mesh(G3(new THREE.BoxGeometry(w,h,d)), m); q.position.set(x,y,z); q.castShadow=!LOW; c.add(q); };
    B(.56,.07,.52,0,.42,0,chairM); B(.56,.5,.07,0,.7,-.24,chairM); B(.48,.08,.05,0,.82,-.25,chairD); [[-.23,-.21],[.23,-.21],[-.23,.21],[.23,.21]].forEach(([x,z])=>B(.06,.42,.06,x,.21,z,chairD)); G.add(c); }
  function arms(P, k){ if(!P) return; if(k==="yay"){ P.armL.rotation.set(-2.7,0,.4); P.armR.rotation.set(-2.7,0,-.4); } else if(k==="clap"){ P.armL.rotation.set(-1.3,0,-.35); P.armR.rotation.set(-1.3,0,.35); } else { P.armL.rotation.set(-1.05,0,.25); P.armR.rotation.set(-1.05,0,-.25); } }
  const SEATS=[];
  [-.6,0,.6].forEach((ang,j)=>{ const L=j+1, d=TR+.5, x=Math.sin(ang)*d, z=-Math.cos(ang)*d, G=new THREE.Group(); G.position.set(x,0,z); G.rotation.y=Math.atan2(-x,-z); scene.add(G); chair(G);
    const hand=new THREE.Group(); hand.position.set(0,.8,.42); hand.rotation.x=-.5; G.add(hand); SEATS[L]={L, G, P:null, hand, n:-1, bk:"", t:Math.random()*6, actT:0, avK:""}; });
  function seatAv(L, av){ const s=SEATS[L], k=JSON.stringify(av||{}); if(s.avK===k && s.P) return; s.avK=k; if(s.P){ s.G.remove(s.P.g); s.P=null; }
    try{ const P=buildAvatar(av||{}); P.g.scale.setScalar(1.08); P.g.position.set(0,.25,-.02); s.G.add(P.g); P.legL.rotation.x=P.legR.rotation.x=-1.45; arms(P,"hold"); P.expr0=(av&&av.expr)||"smile"; s.P=P; }catch(e){ console.warn("CP av", e); } }
  const backPG=G3(new THREE.PlaneGeometry(CW*.62,CH*.62)), backBM=MS(0xfff8ea,{side:THREE.BackSide}), FANM={};
  function fanMat(bk){ if(FANM[bk]) return FANM[bk]; const m=new THREE.MeshStandardMaterial({map:faceMat(null,bk).map,roughness:.6}); disp.push(m); return FANM[bk]=m; }
  function fan(s, n, bk){ n=Math.min(n,8); bk=bk||SET.bk; if(s.n===n && s.bk===bk) return; s.n=n; s.bk=bk; while(s.hand.children.length) s.hand.remove(s.hand.children[0]); const fm=fanMat(bk);
    for(let i=0;i<n;i++){ const a=(i-(n-1)/2)*.17; const m=new THREE.Mesh(backPG,fm), m2=new THREE.Mesh(backPG,backBM); m.position.set(Math.sin(a)*.12, Math.cos(a)*.12-.12, i*.004); m.rotation.z=-a; m2.position.copy(m.position); m2.rotation.copy(m.rotation); s.hand.add(m); s.hand.add(m2); } }
  /* 내 얼굴 */
  const PSc=new THREE.Scene(); PSc.background=new THREE.Color(0x2b3a5a); PSc.add(new THREE.HemisphereLight(0xffffff,0x445566,.85)); { const l=new THREE.DirectionalLight(0xffffff,.55); l.position.set(.6,1.4,1.4); PSc.add(l); }
  const PC=new THREE.PerspectiveCamera(26,1,.1,10); PC.position.set(.05,1.0,1.75); PC.lookAt(0,.88,0);
  let ME_AV=null; try{ ME_AV=buildAvatar(api.av||{}); PSc.add(ME_AV.g); ME_AV.setExpr("grin"); }catch(e){}
  /* 날기 · 팡! · 색종이 */
  function fly(k, faceUp, from, to, dur, o){ o=o||{}; const m=cardMesh(k, faceUp, o.bk); m.position.copy(from); scene.add(m); return new Promise(res=>FLY.push({m, from:from.clone(), to:to.clone(), t:0, dur:fast?.01:dur, arc:o.arc==null?.45:o.arc, r0:o.r0||new THREE.Euler(-.5,0,.2), r1:o.r1||new THREE.Euler(0,(Math.random()-.5)*.6,0), res})); }
  const popTex=tex(256,256,(g,w,h)=>{ g.translate(w/2,h/2); g.beginPath(); for(let i=0;i<24;i++){ const a=i/24*Math.PI*2, r=i%2?w*.27:w*.46; g.lineTo(Math.cos(a)*r,Math.sin(a)*r); } g.closePath(); g.fillStyle="#ffe14d"; g.fill(); g.lineWidth=8; g.strokeStyle=INK; g.lineJoin="round"; g.stroke();
    g.rotate(-.18); g.font="900 62px Jua,sans-serif"; g.textAlign="center"; g.textBaseline="middle"; g.lineWidth=14; g.strokeStyle=INK; g.strokeText("팡!",0,4); g.fillStyle="#ff5a5f"; g.fillText("팡!",0,4); });
  const popM=new THREE.SpriteMaterial({map:popTex,depthTest:false,transparent:true}); disp.push(popM); const popS=new THREE.Sprite(popM); popS.renderOrder=9; popS.visible=false; scene.add(popS); let popT=9;
  function pop(){ const w=new THREE.Vector3(); disc.getWorldPosition(w); popS.position.set(w.x+.3,w.y+.34,w.z-.1); popT=0; popS.visible=true; }
  const CONF=[]; function confetti(n){ const g=G3(new THREE.PlaneGeometry(.08,.13)); for(let i=0;i<n;i++){ const m=new THREE.Mesh(g,new THREE.MeshBasicMaterial({color:[0xff5a5f,0xffc83d,0x3fc46a,0x3ea2ff,0xffffff][i%5],side:THREE.DoubleSide})); disp.push(m.material);
      m.position.set((Math.random()-.5)*4, 2.6+Math.random()*2, (Math.random()-.5)*3.4); m.rotation.set(Math.random()*6,Math.random()*6,0); m.userData.v=.5+Math.random()*.7; m.userData.s=(Math.random()-.5)*4; scene.add(m); CONF.push(m); } }

  /* ══ 화면 ══ */
  const U=api.ui, HUD=document.createElement("div"); HUD.id="cpHud"; U.appendChild(HUD);
  HUD.innerHTML='<div class="cpVig"></div><div class="cpPlates"></div><div class="cpFeed"></div><div class="cpBan"><div><span class="t"></span><small></small></div></div><div class="cpPend"></div><div class="cpMT"></div>'
    +'<div class="cpHand"><div class="in"></div></div>'
    +'<div class="cpCon"><div class="cpPor"><canvas></canvas><div class="who"></div><div class="emo"></div></div><div class="cpMid"><div class="cpHint"></div><div class="cpBar"><i></i></div></div>'
    +'<div class="cpCmd"><button data-c="draw"><span>🃏</span><b>뽑기</b></button><button data-c="one" class="one"><span>☝️</span><b>한 장!</b></button><button data-c="emo"><span>😊</span><b>표정</b></button><button data-c="sort"><span>🔀</span><b>색 순서</b></button></div></div>'
    +'<div class="cpEmo"></div><div class="cpPick"></div><div class="cpEnd"></div><div class="cpMenu"></div><div class="cpCoachW"></div><div class="cpLoad">🃏 카드 섞는 중…</div>';
  const $=s=>HUD.querySelector(s);
  api.topR.innerHTML='<div class="cpTop"><div class="cpOrd"></div><div class="cpCoin"></div></div>';
  const ORD=api.topR.querySelector(".cpOrd"); const porCv=$(".cpPor canvas"), porG=porCv.getContext("2d");
  const REC=()=>MG.rec(); const T0=()=>(REC().t.card)||{}, B0=()=>(REC().b.card)||{};

  /* ══ 상태 ══ */
  let phase="menu";          /* menu · room · count · play · end */
  let ME=0, HOST=true, CO=false, RM=null, TUT=false, RULE={hs:SET.hs, stk:SET.stk}, BOTDF=SET.df;
  const G={P:[], dir:1, turn:-1, cur:"b", top:null, pile:[], draw:[], over:false, pend:0, drew:false, dl:0, hist:[], sq:0, A:[], wait:true, oneWin:null, lock:false};
  const ST={play:0, atk:0, rev:0, wild:0, w4:0, skip:0, d2:0, swap:0, one:0};
  const loc=g=>(g-ME+4)%4, glo=L=>(L+ME)%4, SE=g=>SEATS[loc(g)];
  const meP=()=>G.P[ME];
  const STK_MAX=8;   /* 쌓기는 8장까지 — 넘으면 받아야 함 (아이 판이 끝없이 길어지지 않게) */
  const okC=(k)=>{ const top=G.top; if(!top) return false; if(G.pend>0) return G.pend<STK_MAX && (k.v==="wild4" || (k.v==="d2" && top.v==="d2")); return isW(k) || k.c===G.cur || (!isW(top) && k.v===top.v); };
  const canAny=g=>G.P[g].h.some(id=>okC(CARD(id)));
  const isMyTurn=()=>phase==="play" && !G.over && G.turn===ME && !G.wait && !Q.length && !G.lock;

  /* ── 소식 · 띠 · 힌트 ── */
  function feed(h, c){ const F=$(".cpFeed"); F.insertAdjacentHTML("afterbegin",'<div style="--c:'+(c?COL[c]:"#fff")+'">'+(c?icSVG(c,13):"")+'<span>'+h+'</span></div>'); while(F.children.length>3) F.lastChild.remove(); }
  let banT=0; function banner(t, sub){ const b=$(".cpBan"); b.querySelector(".t").textContent=t; b.querySelector("small").textContent=sub||""; b.classList.add("on"); banT=1.3; }
  const vs=()=>G.top?(typeof G.top.v==="number"?G.top.v:ACTC[G.top.v]):"";
  function hint(){ const h=$(".cpHint"); h.classList.remove("my"); if(phase!=="play"){ h.innerHTML=phase==="end"?"🏁 끝!":"🃏 컬러팡"; return; } if(G.over){ h.innerHTML="🏁 끝!"; return; }
    if(G.turn!==ME){ const p=G.P[G.turn]; h.innerHTML=p?'⏳ <b>'+esc(p.nm)+'</b> 차례':'⏳'; return; }
    h.classList.add("my"); const pl=canAny(ME);
    if(G.pend>0) h.innerHTML=pl?'+'+(G.top.v==="d2"?2:4)+' 내서 넘기기 · 아니면 <b>'+G.pend+'장</b>':'<b>🃏 '+G.pend+'장 받기</b>';
    else h.innerHTML=pl ? icSVG(G.cur,16)+' <b>'+KO[G.cur]+'</b>'+(isW(G.top)?'':' 또는 <b>'+vs()+'</b>')+'!' : (G.drew?'낼 카드가 없어요 → 넘겨요':'<b>🃏 뽑기</b>를 눌러요'); }
  let toastT=0; function toast(h){ const t=$(".cpHint"); t.innerHTML=h; t.classList.add("warn"); toastT=1.6; }
  function setCur(c){ G.cur=c; glowTo.set(COL[c]); }
  function pendUI(){ const e=$(".cpPend"); e.textContent=G.pend>0?"+"+G.pend+"!":""; e.classList.toggle("on", G.pend>0 && phase==="play" && !G.over); }

  /* ── 차례 줄 · 이름표 ── */
  function drawTop(){ if(!G.P.length){ ORD.innerHTML=""; } else ORD.innerHTML=[0,1,2,3].map((j,n)=>{ const g=(ME+j)%4, p=G.P[g]; return (n?'<b>'+(G.dir>0?'›':'‹')+'</b>':'')+'<i class="'+(G.turn===g&&!G.over?"on":"")+'" style="background:'+p.col+'">'+esc((g===ME?"나":p.nm).slice(0,1))+'</i>'; }).join("")+'<b class="d">'+(G.dir>0?'↻':'↺')+'</b>';
    const left=MG.payLeft("card"); api.topR.querySelector(".cpCoin").textContent=left>0?'🪙 '+left+'판':'🪙 끝'; }
  const PL=$(".cpPlates");
  PL.innerHTML=[1,2,3].map(L=>'<div class="cpPlate" data-l="'+L+'"><div class="emo"></div><div class="one1">☝️ 한 장!</div><div class="nm"><span class="dot"></span><span class="n"></span><u></u></div><div class="think"><i></i><i></i><i></i></div></div>').join("");
  function plates(){ [1,2,3].forEach(L=>{ const el=PL.querySelector('[data-l="'+L+'"]'), p=G.P[glo(L)]; if(!p){ el.style.display="none"; return; } el.style.display=""; el.querySelector(".n").textContent=p.nm+(p.bot?" 🤖":""); el.querySelector(".dot").style.background=p.col;
      const u=el.querySelector("u"); u.textContent="🂠 "+p.h.length; u.classList.toggle("one", p.h.length===1); el.classList.toggle("turn", G.turn===glo(L) && !G.over && phase==="play"); el.classList.toggle("o1", p.h.length===1 && !G.over); }); }
  const v3=new THREE.Vector3();
  function platePos(){ const W=innerWidth, H=innerHeight; [1,2,3].forEach(L=>{ const s=SEATS[L]; if(!s || !s.P) return; s.P.head.getWorldPosition(v3); v3.y+=.42; v3.project(cam); const el=PL.querySelector('[data-l="'+L+'"]'); el.style.left=((v3.x+1)/2*W)+"px"; el.style.top=((1-v3.y)/2*H)+"px"; }); }
  const EMT={}; function emote(g, e){ const L=loc(g), el=L===0?$(".cpPor .emo"):PL.querySelector('[data-l="'+L+'"] .emo'); if(!el) return; el.textContent=e; el.classList.add("on"); clearTimeout(EMT[L]); EMT[L]=setTimeout(()=>el.classList.remove("on"), 1800);
    const P=L===0?ME_AV:(SEATS[L]&&SEATS[L].P); if(P && EMO_X[e]){ P.setExpr(EMO_X[e]); if(L) SEATS[L].actT=1.8; } }
  function react(g, ex, t){ const L=loc(g); if(!L) return; const s=SEATS[L]; if(!s || !s.P) return; s.P.setExpr(ex); s.actT=t||1.6; }

  /* ── 내 패 ── */
  const HAND=$(".cpHand .in"); let sortK="c", handSig="", newIds={};
  function sorted(){ const h=(meP()?meP().h:[]).map(CARD); const co=c=>c?CS.indexOf(c):9; return sortK==="c" ? h.sort((a,b)=>co(a.c)-co(b.c) || ORDV(a.v)-ORDV(b.v)) : h.sort((a,b)=>ORDV(a.v)-ORDV(b.v) || co(a.c)-co(b.c)); }
  function layoutHand(){ handSig=""; drawHand(); }
  function drawHand(){ if(!meP()){ HAND.innerHTML=""; return; } const h=sorted(), W=innerWidth, H=innerHeight, land=W>H, n=Math.max(1,h.length), my=isMyTurn();
    const cw=Math.round(Math.max(44, Math.min(land?H*.19:118, H*(land?.19:.14), (W*(land?.5:.86))/(1+(n-1)*.64)))), ov=Math.round(cw*.36), rot=Math.min(4.2, 30/n);
    const sig=h.map(k=>k.id).join(",")+"|"+cw+"|"+my+"|"+G.cur+"|"+(G.top&&G.top.id)+"|"+G.pend+"|"+G.over;
    if(sig===handSig) return; handSig=sig; const mid=(n-1)/2;
    HAND.innerHTML=h.map((k,i)=>{ const can=my && okC(k); const d=i-mid;
      return '<div class="cpC '+(my?(can?"ok":"no"):"")+(newIds[k.id]?" new":"")+'" data-id="'+k.id+'" style="margin-left:'+(i?-ov:0)+'px;--r:'+(d*rot).toFixed(1)+'deg;--y:'+(d*d*1.3).toFixed(1)+'px">'+cardSVG(k.c,k.v,cw)+'</div>'; }).join("");
    newIds={}; coachCheck(); }
  HAND.addEventListener("pointerdown", e=>{ const c=e.target.closest(".cpC"); if(!c) return; e.preventDefault(); tapCard(+c.dataset.id, c); });
  function shake(el){ if(!el) return; el.classList.remove("shk"); void el.offsetWidth; el.classList.add("shk"); }
  function tapCard(id, el){ try{ SFX.ctx(); }catch(e){} if(phase!=="play" || G.over || !meP()) return; if(meP().h.indexOf(id)<0) return; const k=CARD(id);
    if(!isMyTurn()){ shake(el); return; }
    if(!okC(k)){ shake(el); try{ SFX.tone(220,.12,"square",.03); }catch(e){} toast(G.pend>0?'+'+(G.top.v==="d2"?2:4)+' 카드만 낼 수 있어요 · 아니면 🃏 받기':icSVG(G.cur,15)+' '+KO[G.cur]+(isW(G.top)?'':' 또는 '+vs())+' 만 낼 수 있어요'); return; }
    coachDone("card"); if(isW(k)){ pickColor(k); return; }
    input("play", {id}); }
  /* 🌈 색 고르기 */
  function pickColor(k){ coachDone("wild"); const cnt={}; meP().h.forEach(q=>{ const c=CARD(q).c; if(c && q!==k.id) cnt[c]=(cnt[c]|0)+1; }); let best=null; CS.forEach(c=>{ if((cnt[c]|0)>0 && (!best || cnt[c]>cnt[best])) best=c; });
    const C=["y","g","b","r"]; let svg='<svg viewBox="0 0 300 300">'; C.forEach((c,i)=>{ const a0=(i*90-135)*Math.PI/180, a1=a0+Math.PI/2, r=140, ri=58, P=(a,rr)=>(150+Math.cos(a)*rr).toFixed(1)+" "+(150+Math.sin(a)*rr).toFixed(1);
      svg+='<path data-c="'+c+'" d="M'+P(a0,ri)+'L'+P(a0,r)+'A'+r+' '+r+' 0 0 1 '+P(a1,r)+'L'+P(a1,ri)+'A'+ri+' '+ri+' 0 0 0 '+P(a0,ri)+'Z" fill="'+COL[c]+'" stroke="'+INK+'" stroke-width="6" stroke-linejoin="round"/>'; });
    svg+='</svg>'; const lab=C.map((c,i)=>{ const a=(i*90-90)*Math.PI/180; return '<div class="lb'+(c===best?" rec":"")+'" data-c="'+c+'" style="left:'+(50+Math.cos(a)*33.3)+'%;top:'+(50+Math.sin(a)*33.3)+'%">'+icSVG(c,40)+KO[c]+(c===best?'<small>내 카드에 '+cnt[c]+'장</small>':'')+'</div>'; }).join("");
    const P=$(".cpPick"); P.innerHTML='<h3>🌈 무슨 색으로 할까?</h3><div class="wh">'+svg+lab+'<div class="mid">'+cardSVG(null,k.v,62)+'</div></div><p>👆 누르면 탁자 색이 바뀌어요</p><button class="no">↩ 다른 카드</button>'; P.classList.add("on");
    P.querySelectorAll("[data-c]").forEach(el=>el.onclick=()=>{ P.classList.remove("on"); if(isMyTurn()) input("play", {id:k.id, c:el.dataset.c}); });
    P.querySelector(".no").onclick=()=>P.classList.remove("on"); }
  /* 버튼 */
  HUD.querySelector(".cpCmd").addEventListener("click", e=>{ const b=e.target.closest("button"); if(!b) return; try{ SFX.ctx(); }catch(_){} const c=b.dataset.c;
    if(c==="draw"){ coachDone("draw"); if(G.drew && G.pend<=0) input("pass"); else input("draw"); }
    else if(c==="one"){ coachDone("one"); input("one"); }
    else if(c==="sort"){ sortK=sortK==="c"?"n":"c"; b.querySelector("b").textContent=sortK==="c"?"색 순서":"숫자 순서"; layoutHand(); try{ SFX.tone(660,.06,"triangle",.03); }catch(_){} }
    else if(c==="emo"){ const E=$(".cpEmo"); E.innerHTML=EMOS.map(x=>'<button>'+x+'</button>').join(""); E.classList.toggle("on"); E.querySelectorAll("button").forEach(bb=>bb.onclick=()=>{ E.classList.remove("on"); emote(ME, bb.textContent); if(CO && RM) RM.feed({t:"emo", s:ME, e:bb.textContent}); else botReply(); }); } });
  let replyT=0; function botReply(){ if(replyT>0) return; replyT=4; if(Math.random()<.6){ const g=[0,1,2,3].filter(x=>x!==ME && G.P[x] && G.P[x].bot); if(g.length) later(.7+Math.random()*.6, ()=>emote(g[Math.floor(Math.random()*g.length)], EMOS[Math.floor(Math.random()*EMOS.length)])); } }
  function cmd(){ const C=$(".cpCmd"), dr=C.querySelector('[data-c="draw"]'), on=C.querySelector('[data-c="one"]'), me=meP();
    if(!me || phase!=="play"){ dr.classList.add("off"); on.classList.add("off"); on.classList.remove("glow"); dr.classList.remove("glow"); return; }
    const can=isMyTurn(), pl=canAny(ME);
    dr.classList.toggle("off", !can); dr.classList.toggle("glow", can && (G.pend>0 ? !pl : (!pl && !G.drew)));
    const pass=G.drew && G.pend<=0; dr.querySelector("span").textContent=pass?"⏭":"🃏"; dr.querySelector("b").textContent=G.pend>0?G.pend+"장 받기":pass?"넘기기":"뽑기";
    const ow=G.oneWin && G.oneWin.s===ME; const oneOn=!G.over && ((can && me.h.length===2 && pl && !me.called) || ow);
    on.classList.toggle("off", !oneOn && !me.called); on.classList.toggle("glow", oneOn); on.querySelector("b").textContent=me.called?"외쳤어요!":"한 장!"; }

  /* ══ 일(action) 적용 — 혼자·방장·친구 모두 같은 길 ══ */
  const Q=[]; let qRun=false;
  function seatPos(g){ const v=new THREE.Vector3(); if(g===ME) return new THREE.Vector3(0,-.82,.5).unproject(cam); SE(g).hand.getWorldPosition(v); return v; }
  function myCardPos(id){ const el=HAND.querySelector('[data-id="'+id+'"]'); let x=innerWidth/2, y=innerHeight*.85; if(el){ const r=el.getBoundingClientRect(); x=r.left+r.width/2; y=r.top+r.height/2; }
    const v=new THREE.Vector3(x/innerWidth*2-1, -(y/innerHeight)*2+1, .5).unproject(cam), d=v.sub(cam.position).normalize(); return cam.position.clone().add(d.multiplyScalar(1.6)); }
  const pileTop=()=>{ const w=new THREE.Vector3(); disc.getWorldPosition(w); w.y+=.02+pileM.length*(CT+.0015); return w; };
  const nm=g=>g===ME?"내가":esc(josa(G.P[g].nm,"이가","가"));
  const nm2=g=>g===ME?"나":esc(G.P[g].nm);
  function stat(k, g, prevCur, prevTop){ if(g!==ME) return; ST.play++; if(k.v==="d2"){ ST.d2++; ST.atk++; } if(k.v==="wild4"){ ST.w4++; ST.wild++; ST.atk++; } if(k.v==="wild") ST.wild++; if(k.v==="skip") ST.skip++; if(k.v==="rev") ST.rev++;
    if(typeof k.v==="number" && prevTop && typeof prevTop.v==="number" && k.v===prevTop.v && k.c!==prevCur) ST.swap++; missTick(); }
  let EP=0;   /* hardSync 하면 +1 → 그 전에 돌던 apply 는 기다린 뒤 멈춤 */
  async function apply(a){ const P=G.P, ep=EP;
    switch(a.t){
    case "deal": { G.P.forEach((p,i)=>p.h=a.h[i].slice()); G.draw=a.dw.slice(); G.pile=[a.top]; G.top=CARD(a.top); G.dir=1; G.pend=0; G.over=false; pileReset(); pileAdd(G.top); setCur(G.top.c); glowCol.copy(glowTo); G.hist=[G.P.map(p=>p.h.length)];
      [1,2,3].forEach(L=>fan(SEATS[L], G.P[glo(L)].h.length, G.P[glo(L)].bk)); pileH(); feed('🃏 첫 카드: <b>'+kname(G.top)+'</b>', G.top.c); try{ SFX.noise(.4,.04,2200,.5,800); }catch(e){} handSig=""; drawHand(); plates(); drawTop(); break; }
    case "turn": { G.turn=a.s; G.drew=false; G.dl=a.dl||0; G.wait=false; G.hist.push(P.map(p=>p.h.length)); drawTop(); plates();
      if(a.s===ME){ myArc.visible=true; banner(G.pend>0?"😮 +"+G.pend+"!":"⭐ 내 차례! ⭐", G.pend>0?(canAny(ME)?"+"+(G.top.v==="d2"?2:4)+" 카드로 넘기거나 "+G.pend+"장 받아요":G.pend+"장 받아요"):(canAny(ME)?KO[G.cur]+(isW(G.top)?'':'이나 '+vs())+' 를 내요':'낼 카드가 없어요 → 🃏 뽑기')); try{ SFX.tone(660,.1,"triangle",.04); SFX.tone(990,.14,"triangle",.04,0,.09); }catch(e){} if(auto) later(.3, autoMove); }
      else { myArc.visible=false; if(coachEl){ Object.keys(COACH).forEach(k=>{ if(COACH[k]===1) COACH[k]=2; }); coachClear(); } } handSig=""; drawHand(); break; }
    case "p": { const k=CARD(a.id), p=P[a.s]; const i=p.h.indexOf(a.id); if(i>=0) p.h.splice(i,1); G.wait=true; if(a.s===ME) myArc.visible=false;
      const from=a.s===ME?myCardPos(a.id):seatPos(a.s); if(a.s===ME) drawHand(); else fan(SE(a.s), p.h.length, p.bk); plates(); try{ SFX.noise(.12,.05,2600,.6,900); }catch(e){}
      const pc=G.cur, pt=G.top;
      await fly(k, true, from, pileTop(), a.s===ME?.34:.42, {arc:a.s===ME?.35:.5, r0:new THREE.Euler(a.s===ME?-1.1:-.6,0,.3), r1:new THREE.Euler(0,(Math.random()-.5)*.7,0)});
      if(gone || ep!==EP) return; G.pile.push(a.id); G.top=k; pileAdd(k); setCur(isW(k)?a.c:k.c); pop(); if(p.h.length>1) p.called=false;
      try{ SFX.tone(isW(k)?520:440,.1,"triangle",.05,isW(k)?1040:880); if(isW(k)) [523,659,784,988].forEach((f,j)=>SFX.tone(f,.12,"triangle",.035,0,j*.05)); }catch(e){}
      feed((a.s===ME?"🙋 ":"")+nm(a.s)+' <b>'+kname(k)+'</b>'+(isW(k)?' → '+KO[a.c]:''), isW(k)?a.c:k.c); stat(k, a.s, pc, pt); if(a.s!==ME) react(a.s,"grin",1.2);
      handSig=""; drawHand(); plates(); break; }
    case "d": { const p=P[a.s]; for(const id of a.ids){ if(gone) return; const j=G.draw.indexOf(id); if(j>=0) G.draw.splice(j,1); pileH(); const from=new THREE.Vector3(); drawPile.getWorldPosition(from); from.y+=.12;
        try{ SFX.noise(.08,.03,1800); }catch(e){}
        await fly(CARD(id), false, from, seatPos(a.s), .24, {arc:.3, r0:new THREE.Euler(0,.12,0), r1:new THREE.Euler(a.s===ME?-1.1:-.3,0,0), bk:p.bk||SET.bk});
        if(ep!==EP) return; p.h.push(id); if(a.s===ME){ newIds[id]=1; handSig=""; drawHand(); } else fan(SE(a.s), p.h.length, p.bk); plates(); }
      if(p.h.length>1) p.called=false; if(a.own && a.s===G.turn){ G.drew=true; G.wait=false; if(a.s===ME && auto) later(.3, autoMove); } handSig=""; drawHand(); break; }
    case "rf": { G.draw=a.dw.slice(); G.pile=[G.pile[G.pile.length-1]]; pileH(); feed("🔄 카드를 다시 섞었어요"); break; }
    case "dir": G.dir=a.d; feed('⇄ 방향이 바뀌었어요', G.top&&G.top.c); drawTop(); break;
    case "sk": react(a.s,"wow"); feed('⊘ '+esc(nm2(a.s))+' 건너뛰어요', G.top&&G.top.c); if(a.s===ME) banner("⊘ 건너뛰기!", "이번엔 쉬어요"); break;
    case "pend": G.pend=a.m; pendUI(); if(a.m>0) feed('📚 +'+a.m+' 쌓였어요!', G.top&&G.top.c); break;
    case "hit": react(a.s,"wow",2.2); if(a.s!==ME && Math.random()<.6) later(.3,()=>emote(a.s,"😱")); if(a.s===ME) banner("😮 +"+a.m+"!", a.m+"장 받고 한 번 쉬어요"); feed('😱 '+esc(nm2(a.s))+' +'+a.m+'장', G.cur); break;
    case "ow": G.oneWin={s:a.s, t:ONE_T}; break;
    case "one": P[a.s].called=true; G.oneWin=null; if(a.s===ME){ ST.one++; missTick(); emote(ME,"☝️"); } else { emote(a.s,"😝"); } feed('☝️ '+esc(nm2(a.s))+' 「한 장!」'); try{ SFX.tone(880,.12,"square",.04); SFX.tone(1320,.12,"square",.03,0,.08); }catch(e){} break;
    case "oops": G.oneWin=null; feed('😅 '+esc(nm2(a.s))+' 「한 장!」 깜빡 → 2장'); if(a.s===ME) banner("😅 깜빡!", "「☝️ 한 장!」을 안 눌러서 2장 받아요"); else react(a.s,"wow",1.8); break;
    case "pass": G.wait=true; feed('⏭ '+(a.s===ME?"내가":esc(josa(P[a.s].nm,"이","")))+' 넘겼어요'+(a.why?' ('+a.why+')':'')); break;
    case "end": if(!HOST && RM && RM.d && RM.d.g && RM.d.g.s && RM.d.g.s.over) hardSync(RM.d.g, true); await endShow(a.w, a.ord); break;
    }
    if(a.t!=="end"){ hint(); cmd(); } }
  async function runQ(){ if(qRun) return; qRun=true; while(Q.length && !gone){ const a=Q[0]; if(Q.length>4) fast=Math.max(fast,1); try{ await apply(a); }catch(e){ console.warn("CP apply", e); } Q.shift(); G.sq=Math.max(G.sq,a.n|0); if(Q.length<=1 && fast===1 && !FASTX) fast=0; } qRun=false; hint(); cmd(); drawHand(); }
  let FASTX=false;
  /* 방장/혼자: 일을 정해서 기록 → 같이면 방에 → 적용 */
  let SEQ=0;
  async function act(a){ a.n=++SEQ; G.A.push(a); if(G.A.length>120) G.A.shift(); if(CO) pub(); await apply(a); G.sq=a.n; if(CO) pubT=Math.max(pubT,1.2); }
  function snap(){ return {sq:SEQ, A:G.A, s:{P:G.P.map(p=>({h:p.h, c:p.called?1:0, k:p.k||"", nm:p.nm, b:p.bot?1:0, av:p.av||null, bk:p.bk||"base", col:p.col})), dw:G.draw, pl:G.pile, top:G.top?G.top.id:-1, cur:G.cur, dir:G.dir, turn:G.turn, pend:G.pend, over:G.over?1:0, dl:G.dl, hist:G.hist.slice(-80), drew:G.drew?1:0, sq:G.sq}}; }   /* s.sq = 상태가 반영한 일 번호 (A 는 그보다 앞설 수 있음) */
  let pubT=0; function pub(){ if(!RM) return; pubT=0; RM.put("g", snap()); }

  /* ══ 방장 일 ══ */
  const nextI=(i,s)=>(i+G.dir*(s||1)+40)%4;
  async function take(n, g){ const out=[]; for(let j=0;j<n;j++){ if(!G.draw.length){ const top=G.pile[G.pile.length-1], rest=shuffle(G.pile.slice(0,-1)); if(!rest.length) break; await act({t:"rf", dw:rest}); } const id=G.draw[G.draw.length-1-out.length]; if(id==null) break; out.push(id); }
    return out; }
  async function giveCards(g, n, own){ let left=n; while(left>0){ if(!G.draw.length){ const rest=shuffle(G.pile.slice(0,-1)); if(!rest.length) break; await act({t:"rf", dw:rest}); } const k=Math.min(left, G.draw.length); const ids=G.draw.slice(G.draw.length-k).reverse(); await act({t:"d", s:g, ids, own:own?1:0}); left-=k; if(!k) break; } }
  function beginTurn(g){ if(G.over || gone) return; const p=G.P[g]; act({t:"turn", s:g, dl:now()+TURN_T*1000}).then(()=>{ if(p.bot && !G.over) later(fast?.01:(TUT?1.4:.75)+Math.random()*.6, ()=>botMove(g)); }); }
  function advance(skip){ if(G.over || gone) return; beginTurn(nextI(G.turn, skip?2:1)); }
  async function doPlay(g, id, col){ const k=CARD(id), p=G.P[g]; if(p.h.indexOf(id)<0 || !okC(k)) return false; G.lock=true;
    if(isW(k) && !col) col=bestCol(g,k);
    await act({t:"p", s:g, id, c:isW(k)?col:null});
    if(gone) return true; if(!p.h.length){ await finishGame(g); return true; }
    if(p.h.length===1 && !p.called) await oneRule(g); else if(p.h.length===1 && p.called) {}
    if(gone || G.over) return true;
    let skip=false; const t=nextI(g);
    if(k.v==="skip"){ skip=true; await act({t:"sk", s:t}); }
    else if(k.v==="rev"){ await act({t:"dir", d:-G.dir}); }
    else if(k.v==="d2"||k.v==="wild4"){ const n=k.v==="d2"?2:4;
      if(RULE.stk){ await act({t:"pend", m:G.pend+n}); }
      else { skip=true; await act({t:"hit", s:t, m:n}); await wait(.2); await giveCards(t, n); } }
    G.lock=false; await wait(.25); advance(skip); return true; }
  async function oneRule(g){ const p=G.P[g];
    if(p.bot){ if(Math.random()<(BOTDF==="easy"?.72:.88)){ await act({t:"one", s:g}); } else { await wait(.6); await act({t:"oops", s:g}); await giveCards(g,2); } return; }
    await act({t:"ow", s:g}); const t0=performance.now(); while(!p.called && !gone){ await wait(.05); if((G.oneWin && G.oneWin.t<=0) || (fast && performance.now()-t0>30)) break; if(!G.oneWin) break; }
    G.oneWin=null; if(!p.called){ await act({t:"oops", s:g}); await giveCards(g,2); } }
  async function takePend(g){ const n=G.pend; G.lock=true; await act({t:"pend", m:0}); await act({t:"hit", s:g, m:n}); await giveCards(g, n); G.lock=false; await wait(.2); advance(false); }
  async function doDraw(g){ if(G.pend>0) return takePend(g); if(G.drew) return; G.lock=true; await giveCards(g,1,true); G.lock=false;
    const p=G.P[g]; if(!canAny(g) && !p.bot){ await wait(.7); if(G.turn===g && !G.over) await doPass(g, "낼 카드 없음"); } }
  async function doPass(g, why){ if(G.turn!==g || G.over || G.lock) return; G.lock=true; await act({t:"pass", s:g, why:why||""}); G.lock=false; advance(false); }
  async function finishGame(w){ G.over=true; const ord=[0,1,2,3].sort((a,b)=>(a===w?-1:b===w?1:G.P[a].h.length-G.P[b].h.length)); await act({t:"end", w, ord}); }
  /* 🤖 봇 */
  function choose(g, pl){ if(BOTDF==="easy") return pl[Math.floor(Math.random()*pl.length)];
    const p=G.P[g], nx=G.P[nextI(g)], cnt={}; p.h.forEach(id=>{ const c=CARD(id).c; if(c) cnt[c]=(cnt[c]|0)+1; }); const danger=nx.h.length<=2 ? 1 : 0;
    let best=null, bs=-1e9; pl.forEach(k=>{ let s=Math.random()*1.2; if(k.c) s+=(cnt[k.c]|0)*.6; if(typeof k.v==="number") s+=1.5+k.v*.05;
      if(k.v==="skip"||k.v==="d2") s+=danger?5:.5; if(k.v==="rev") s+=danger?2:.3; if(k.v==="wild") s+=danger?1:-4; if(k.v==="wild4") s+=danger?6:-7; if(p.h.length<=2 && isW(k)) s+=3; if(G.pend>0) s+=5;
      if(s>bs){ bs=s; best=k; } }); return best; }
  function bestCol(g, k){ const cnt={}; G.P[g].h.forEach(q=>{ const c=CARD(q).c; if(c && q!==k.id) cnt[c]=(cnt[c]|0)+1; }); let b=null; CS.forEach(c=>{ if(!b || (cnt[c]|0)>(cnt[b]|0)) b=c; }); return (cnt[b]|0)>0?b:CS[Math.floor(Math.random()*4)]; }
  async function botMove(g){ if(G.over || gone || G.turn!==g || !HOST) return; const p=G.P[g]; if(!p.bot) return;
    let pl=p.h.map(CARD).filter(okC);
    if(G.pend>0){ if(pl.length && (BOTDF!=="easy" || Math.random()<.7)) return doPlay(g, choose(g,pl).id); return takePend(g); }
    if(!pl.length){ G.lock=true; await giveCards(g,1,true); G.lock=false; pl=p.h.map(CARD).filter(okC); if(!pl.length){ await wait(.3); return doPass(g); } await wait(.45); }
    const k=choose(g,pl); await doPlay(g, k.id, isW(k)?bestCol(g,k):null); }
  /* 사람(나 · 친구) 입력 */
  function input(t, o){ o=o||{}; if(phase!=="play" || G.over) return;
    if(t==="one"){ const me=meP(); if(!me) return; if(!(G.oneWin && G.oneWin.s===ME) && !(isMyTurn() && me.h.length===2)) return; if(me.called) return; }
    else if(!isMyTurn()) return;
    if(t!=="one"){ G.wait=true; cmd(); drawHand(); }
    if(HOST) hostIn(ME, t, o); else RM.ev(hostC||hostCode(), Object.assign({t:"in", a:t, s:ME}, o)); }
  function hostIn(g, t, o){ const p=G.P[g]; if(!p || G.over) return;
    if(t==="one"){ if(p.called) return; if((G.oneWin && G.oneWin.s===g) || (G.turn===g && p.h.length===2)){ p.called=true; act({t:"one", s:g}); } return; }
    if(G.turn!==g || G.lock){ return; }
    if(t==="play") doPlay(g, o.id, o.c).then(ok=>{ if(!ok){ G.wait=false; if(CO) act({t:"turn", s:g, dl:G.dl}); } });
    else if(t==="draw") doDraw(g);
    else if(t==="pass") doPass(g); }
  async function autoMove(){ if(!isMyTurn()) return; const me=meP(); let pl=me.h.map(CARD).filter(okC);
    if(me.h.length===2 && pl.length) input("one");
    if(G.pend>0){ if(pl.length){ const k=pl[0]; input("play",{id:k.id, c:isW(k)?bestCol(ME,k):null}); } else input("draw"); return; }
    if(!pl.length){ input("draw"); return; }
    const k=choose(ME,pl); input("play",{id:k.id, c:isW(k)?bestCol(ME,k):null}); }
  /* 같은 판에서 내가 뽑은 뒤 낼 수 있을 때 자동 */

  /* ══ 끝 ══ */
  async function endShow(w, ord){ G.over=true; G.wait=true; myArc.visible=false; G.hist.push(G.P.map(p=>p.h.length)); drawTop(); plates(); cmd(); hint(); handSig=""; drawHand(); pendUI();
    [1,2,3].forEach(L=>{ const s=SEATS[L], g=glo(L); if(!s || !s.P) return; if(g===w){ arms(s.P,"yay"); s.P.setExpr("grin"); s.hand.visible=false; } else { arms(s.P,w===ME?"clap":"hold"); s.P.setExpr(w===ME?"wow":"smile"); } s.actT=99; });
    if(w===ME){ confetti(LOW?70:150); banner("🎉 다 냈다!", ""); try{ SFX.win(); }catch(e){} } else { banner("🏁 "+esc(G.P[w].nm)+" 다 냈어요!", ""); try{ SFX.tone(392,.25,"triangle",.05); SFX.tone(330,.35,"triangle",.05,0,.2); }catch(e){} }
    await wait(1.6); if(gone) return; phase="end";
    const rank=ord.indexOf(ME)+1, COINS=[10,6,5,4][rank-1], streak=w===ME?((B0().cs|0)+1):0, S2=Object.assign({}, ST);
    if(!TUT){ MISSP.games=(MISSP.games|0)+1; if(rank===1) MISSP.win=(MISSP.win|0)+1; if(rank<=2) MISSP.top2=(MISSP.top2|0)+1; missTick(true); }
    if(TUT){ /* 배우기 판 = 🪙·하루 판 수 안 셈 */ const r=REC(); r.t.card=r.t.card||{}; r.t.card.tut=1; st("hyeng_proto_mg", r); endUI(ord, w, rank, 0, 0, S2); return; }
    const got=api.end({title:rank===1?"🏆 1등!":rank+"등", sub:"컬러팡", rows:ord.map(i=>[G.P[i].nm, i===w?"다 냈어요":G.P[i].h.length+"장", i===ME]), coins:COINS,
      upd:(b,t)=>{ t.win=(t.win|0)+(w===ME?1:0); t.cards=(t.cards|0)+S2.play; t.atk=(t.atk|0)+S2.atk; if(CO) t.co=(t.co|0)+1; b.cs=streak; b.bs=Math.max(b.bs|0, streak); b.top=Math.min(b.top||9, rank); }});
    try{ const r=document.getElementById("mgRes"); if(r) r.classList.remove("on"); }catch(e){}
    endUI(ord, w, rank, got, streak, S2); }
  function graph(){ const H=G.hist.length?G.hist:[[7,7,7,7]], n=H.length, w=300, h=86, mx=Math.max(7,...H.map(r=>Math.max(...r))), X=i=>8+i*(w-16)/Math.max(1,n-1), Y=v=>8+(mx-v)/mx*(h-16);
    let s='<svg viewBox="0 0 '+w+' '+h+'" width="100%" height="'+h+'" preserveAspectRatio="none" style="display:block;background:#f6ecd6;border-radius:10px">';
    for(let k=1;k<4;k++) s+='<line x1="8" x2="'+(w-8)+'" y1="'+(8+k*(h-16)/4)+'" y2="'+(8+k*(h-16)/4)+'" stroke="#e2d2b4" stroke-width="1"/>';
    [0,1,2,3].filter(j=>j!==ME).concat([ME]).forEach(j=>{ const pts=H.map((r,i)=>X(i).toFixed(1)+','+Y(r[j]).toFixed(1)).join(" "); s+='<polyline fill="none" stroke="'+INK+'" stroke-width="'+(j===ME?6.5:4.5)+'" stroke-linejoin="round" points="'+pts+'"/><polyline fill="none" stroke="'+G.P[j].col+'" stroke-width="'+(j===ME?3.8:2.4)+'" stroke-linejoin="round" points="'+pts+'"/>'; });
    return s+'</svg>'; }
  function endUI(ord, w, rank, got, streak, S2){ const E=$(".cpEnd"), lg=league(T0().win);
    const emb=rank===1?"승리!":rank===2?"2등!":rank===3?"3등!":"4등"; const sub=TUT?"📖 배우기 끝! 이제 혼자 해 봐요":rank===1?"카드를 제일 먼저 다 냈어요":"아깝다! 카드가 "+meP().h.length+"장 남았어요";
    const nb=newBacks(); const md=missList().map(m=>'<div class="'+(m.ok?"ok":"")+'"><span>'+(m.ok?"✅ ":"🎯 ")+m.t+'</span><span>'+Math.min(m.v,m.n)+'/'+m.n+'</span></div>').join("");
    E.innerHTML='<div class="ed"></div>'+(rank===1?'<div class="rays"></div>':'')+'<div class="eb"><div class="emb r'+rank+'">'+emb+'</div>'+(streak>=2?'<div class="rib">🔥 '+streak+'연승!</div>':'')+'<div class="sub">'+sub+'</div>'
      +'<div class="ec"><div class="rk">'+ord.map((i,j)=>'<i>'+(["🥇","🥈","🥉","4"][j])+'</i><span class="'+(i===ME?"t-me me":"")+'"><b class="dt" style="background:'+G.P[i].col+'"></b>'+esc(G.P[i].nm)+(G.P[i].bot?' 🤖':'')+'</span><em>'+(i===w?"다 냈어요!":G.P[i].h.length+"장")+'</em>').join("")+'</div>'
      +'<div class="gr"><div class="t">📈 남은 카드<em>판이 어떻게 흘렀나</em></div>'+graph()+'</div>'
      +'<div class="rew">'+(TUT?'<span>📖 배우기</span>':got>0?'<span>🪙 +'+got+'</span>':'<span class="off">🪙 오늘 상 끝</span>')+(S2.atk?'<span>⚔️ 공격 '+S2.atk+'번</span>':'')+'<span>🃏 낸 카드 '+S2.play+'</span></div>'
      +(nb.length?'<div class="nb">🎴 새 카드 뒷면! '+nb.map(b=>'<b>'+b.nm+'</b>').join(" · ")+' — 메뉴에서 골라요</div>':'')
      +'<div class="ms">'+md+'</div>'
      +'<div class="lv">'+lg.ic+' '+lg.nm+'<div class="lvb"><i style="width:'+Math.round(lg.p*100)+'%"></i></div>'+(lg.next?lg.next+' <small>'+lg.left+'번 더 이기면</small>':'최고!')+'</div>'
      +'<div class="bt"><button class="out">☰ 메뉴</button><button class="go">🔄 한 판 더</button></div></div></div>';
    E.classList.add("on"); E.querySelector(".out").onclick=()=>api.restart({});
    E.querySelector(".go").onclick=()=>{ if(CO){ api.restart({}); return; } api.restart({quick:1, tut:0}); }; }

  /* ══ 🎯 미션 · 🎴 뒷면 ══ */
  const MDAY=dayK(); let MSTORE=st("hyeng_proto_cpm"); if(!MSTORE || MSTORE.d!==MDAY) MSTORE={d:MDAY, p:{}, got:{}, all:0};
  const MISSP=MSTORE.p;
  const GK={games:1,win:1,top2:1}, MK={cards:"play"};
  const mv=k=>GK[k] ? (MISSP[k]|0) : (MISSP[MK[k]||k]|0)+(ST[MK[k]||k]|0);   /* ST = 이번 판(끝나면 MISSP 에 더하고 0) */
  function missList(){ return missToday(MDAY).map(m=>Object.assign({}, m, {v:mv(m.k), ok:!!MSTORE.got[m.k]})); }
  function missTick(save){ if(TUT) return; const L=missToday(MDAY); let any=false;
    L.forEach(m=>{ const cur=mv(m.k);
      if(!MSTORE.got[m.k] && cur>=m.n){ MSTORE.got[m.k]=1; any=true; let got=0; try{ got=TECO.addCoin(m.c)|0; }catch(e){} mtoast('🎯 미션 완료! '+m.t+' · 🪙+'+(got||m.c)); try{ SFX.tone(784,.1,"triangle",.05); SFX.tone(1046,.16,"triangle",.05,0,.1); }catch(e){}
        try{ const r=REC(); r.t.card=r.t.card||{}; r.t.card.ms=(r.t.card.ms|0)+1; st("hyeng_proto_mg", r); }catch(e){} } });
    if(!MSTORE.all && L.every(m=>MSTORE.got[m.k])){ MSTORE.all=1; any=true; try{ TECO.addCoin(20); }catch(e){} later(2.2, ()=>mtoast('🎁 오늘 미션 다 깼어요! 🪙+20')); }
    if(save || any){ if(save){ Object.keys(ST).forEach(k=>{ MISSP[k]=(MISSP[k]|0)+(ST[k]|0); ST[k]=0; }); }
      st("hyeng_proto_cpm", {d:MSTORE.d, p:MISSP, got:MSTORE.got, all:MSTORE.all}); } }
  let mtT=0; function mtoast(h){ const e=$(".cpMT"); e.innerHTML=h; e.classList.add("on"); mtT=2.4; }
  const BK0=BACKS.filter(b=>backOpen(b, REC())).map(b=>b.k);
  function newBacks(){ const R=REC(); return BACKS.filter(b=>backOpen(b,R) && BK0.indexOf(b.k)<0); }

  /* ══ 📖 따라 하기 (처음 두 판 + 배우기) ══ */
  const COACH={}; let coachOn=false, coachEl=null, fingEl=null;
  function coachClear(){ try{ coachEl && coachEl.remove(); fingEl && fingEl.remove(); }catch(e){} coachEl=fingEl=null; }
  function coachDone(k){ if(COACH[k]===1){ COACH[k]=2; coachClear(); } }
  function coach(k, html, target, up){ if(!coachOn || COACH[k]) return; COACH[k]=1; coachClear(); const W=$(".cpCoachW");
    coachEl=document.createElement("div"); coachEl.className="cpCoach"; coachEl.innerHTML=html+'<small>👆 눌러서 닫기</small>'; W.appendChild(coachEl); coachEl.onclick=()=>{ COACH[k]=2; coachClear(); };
    const r=target?target.getBoundingClientRect():null, cw=Math.min(300, innerWidth*.8); coachEl.style.width=cw+"px";
    if(r){ fingEl=document.createElement("div"); fingEl.className="cpFinger"; fingEl.textContent="👇"; W.appendChild(fingEl); fingEl.style.left=(r.left+r.width/2)+"px"; fingEl.style.top=(r.top-46)+"px";
      coachEl.style.left=Math.max(8, Math.min(innerWidth-cw-8, r.left+r.width/2-cw/2))+"px"; coachEl.style.top=Math.max(60, r.top-46-coachEl.offsetHeight-8)+"px"; }
    else { coachEl.style.left=(innerWidth-cw)/2+"px"; coachEl.style.top="42%"; } }
  function coachCheck(){ if(!coachOn || phase!=="play" || G.over || coachEl) return; const me=meP(); if(!me) return;
    if(isMyTurn()){
      if(G.pend>0) return coach("pend", '📚 <b>+'+G.pend+'</b> 이 쌓였어요! 같은 +카드를 내면 다음 친구에게 넘어가고, 없으면 <b>받기</b>', $(".cpCmd [data-c=draw]"));
      if(me.h.length===2 && canAny(ME) && !me.called) return coach("one", '카드가 <b>2장</b>! 내기 전에 <b>☝️ 한 장!</b> 을 눌러요<br>안 누르면 2장 더 받아요', $(".cpCmd [data-c=one]"));
      const ok=HAND.querySelector(".cpC.ok"); const w=[...HAND.querySelectorAll(".cpC.ok")].find(el=>isW(CARD(+el.dataset.id)));
      if(ok && !COACH.card) return coach("card", '가운데 카드와 <b>같은 색</b>이나 <b>같은 숫자</b>를 낼 수 있어요<br>노랗게 <b>빛나는 카드</b>를 눌러요!', ok);
      if(w && !COACH.wild) return coach("wild", '🌈 <b>무지개 카드</b>는 아무 때나 낼 수 있어요<br>내고 나서 <b>색을 골라요</b>', w);
      if(!ok && !G.drew) return coach("draw", '낼 카드가 없어요 → <b>🃏 뽑기</b>를 눌러요', $(".cpCmd [data-c=draw]"));
    } }

  /* ══ 메뉴 ══ */
  const MENU=$(".cpMenu");
  function menuShow(v){ phase="menu"; MENU.style.display="flex"; HUD.classList.add("inMenu"); const R=REC(), t=T0(), b=B0(), lg=league(t.win), left=MG.payLeft("card");
    const ml=missList(), md=ml.filter(m=>m.ok).length, bo=BACKS.filter(B=>backOpen(B,R)).length;
    if(!v){ MENU.innerHTML='<div class="pn"><div class="lg"><span>컬</span><span>러</span><span>팡</span><span>!</span></div>'
      +'<div class="me"><span>'+lg.ic+' '+lg.nm+'</span><span>🏆 '+(t.win|0)+'승</span><span>🔥 최고 '+(b.bs|0)+'연승</span><span>🪙 '+(left>0?'오늘 '+left+'판':'오늘 상 끝')+'</span></div>'
      +'<div class="bb"><button class="big" data-m="solo">▶ 혼자 하기<small>봇 3명과</small></button>'
      +'<div style="grid-column:1/-1" class="df">'+[["easy","🐣 쉬운 봇"],["normal","🙂 보통 봇"]].map(q=>'<button data-df="'+q[0]+'" class="'+(SET.df===q[0]?"on":"")+'">'+q[1]+'</button>').join("")+'</div>'
      +'<button class="co" data-m="co">👫 같이 하기<small>친구 최대 4명 · 빈자리 봇</small></button>'
      +'<button data-m="tut" class="'+(!(t.play|0) && !t.tut?"new":"")+'">📖 배우기<small>따라 하며 한 판</small></button>'
      +'<button data-m="mis">🎯 오늘의 미션<small>'+md+' / 3 깼어요</small></button>'
      +'<button data-m="bk">🎴 카드 뒷면<small>'+bo+' / '+BACKS.length+' 모음</small></button>'
      +'<button data-m="rule" style="grid-column:1/-1">⚙️ 규칙<small>시작 '+SET.hs+'장 · +2 쌓기 '+(SET.stk?"켬":"끔")+'</small></button></div>'
      +'<div class="bt2"><button data-m="out">🏝 섬으로</button></div></div>'; return; }
    const back='<div class="bt2"><button data-m="home">← 메뉴</button></div>';
    if(v==="mis") MENU.innerHTML='<div class="pn"><h4>🎯 오늘의 미션</h4><div class="ml">'+ml.map(m=>'<div class="mi '+(m.ok?"ok":"")+'"><div class="t">'+(m.ok?"✅ ":"")+m.t+'<div class="b"><i style="width:'+Math.min(100,Math.round(m.v/m.n*100))+'%"></i></div></div><div class="c">'+Math.min(m.v,m.n)+'/'+m.n+' · 🪙'+m.c+'</div></div>').join("")+'</div><div class="me" style="margin-top:10px"><span>🎁 셋 다 깨면 🪙+20</span><span>내일 새 미션</span></div>'+back+'</div>';
    else if(v==="bk") MENU.innerHTML='<div class="pn"><h4>🎴 카드 뒷면</h4><div class="me"><span>고른 뒷면 = 내 뽑기 더미 · 같이 하면 친구 화면에서 내 카드</span></div><div class="bg2">'+BACKS.map(B=>{ const o=backOpen(B,R); return '<button class="bk '+(o?"":"lock")+(SET.bk===B.k?" on":"")+'" data-bk="'+B.k+'">'+cardSVG(null,"back",72,B.k)+B.nm+'<small>'+(o?(SET.bk===B.k?"✔ 쓰는 중":"고르기"):B.need[2]+' ('+Math.min(backVal(B.need[0],R),B.need[1])+'/'+B.need[1]+')')+'</small></button>'; }).join("")+'</div>'+back+'</div>';
    else if(v==="rule") MENU.innerHTML='<div class="pn"><h4>⚙️ 규칙</h4><div class="rr"><div class="r"><b>🃏 시작 카드</b><div class="op">'+[7,5].map(n=>'<button data-hs="'+n+'" class="'+(SET.hs===n?"on":"")+'">'+n+'장'+(n===5?' (빨리 끝나요)':'')+'</button>').join("")+'</div></div>'
      +'<div class="r"><b>📚 +2 쌓기</b><div class="op">'+[[0,"끔"],[1,"켬"]].map(q=>'<button data-stk="'+q[0]+'" class="'+(SET.stk===q[0]?"on":"")+'">'+q[1]+'</button>').join("")+'</div><small>켜면 +2 위에 +2(또는 🌈+4)를 내서 다음 친구에게 넘길 수 있어요. 못 내면 쌓인 만큼 다 받아요!</small></div>'
      +'<div class="r"><b>👫 같이 하기</b><small>방장이 고른 규칙으로 해요</small></div></div>'+back+'</div>';
  }
  MENU.addEventListener("click", e=>{ const b=e.target.closest("button"); if(!b) return; try{ SFX.ctx(); SFX.tone(660,.05,"triangle",.03); }catch(_){}
    const m=b.dataset.m; if(b.dataset.df){ SET.df=b.dataset.df; saveSet(); menuShow(); return; }
    if(b.dataset.bk){ const B=BACK[b.dataset.bk]; if(!backOpen(B,REC())){ shake(b); return; } SET.bk=B.k; saveSet(); setDeckBack(); menuShow("bk"); return; }
    if(b.dataset.hs){ SET.hs=+b.dataset.hs; saveSet(); menuShow("rule"); return; } if(b.dataset.stk){ SET.stk=+b.dataset.stk; saveSet(); menuShow("rule"); return; }
    menuGo(m); });
  function menuGo(m){ if(m==="home") return menuShow(); if(m==="solo"||m==="tut"||m==="co") HUD.classList.remove("inMenu"); if(m==="mis"||m==="bk"||m==="rule") return menuShow(m); if(m==="out") return MG.exit();
    if(m==="solo"||m==="tut"){ MENU.style.display="none"; startSolo(m==="tut"); }
    else if(m==="co"){ MENU.style.display="none"; startCo(); } }

  /* ══ 혼자 ══ */
  const PCOL=["#ffc83d","#ff5a5f","#3ea2ff","#3fc46a"];
  function botP(i, b, bk){ return {nm:b.nm, bot:true, h:[], col:PCOL[i], av:b.av, bk:bk||BACKS[Math.floor(Math.random()*BACKS.length)].k, called:false}; }
  async function startSolo(tut){ TUT=!!tut; coachOn=TUT || ((T0().play|0)<2 && !T0().tut); CO=false; HOST=true; ME=0; RULE={hs:TUT?7:SET.hs, stk:TUT?0:SET.stk}; BOTDF=TUT?"easy":SET.df;
    const names=shuffle(BOTS.slice()).slice(0,3);
    G.P=[{nm:api.nick||"나", me:true, h:[], col:PCOL[0], av:api.av, bk:SET.bk}].concat(names.map((b,i)=>botP(i+1,b)));
    [1,2,3].forEach(L=>seatAv(L, G.P[L].av)); phase="play"; plates(); drawTop();
    await wait(.3); dealHost(); }
  function dealHost(){ const dw=shuffle(DECK.map(k=>k.id)); const hs=RULE.hs, H=[[],[],[],[]];
    if(TUT){ /* 배우기: 내 손에 무지개 · 같은 숫자 · +2 를 넣어 줌 */ const pickId=f=>{ const i=dw.findIndex(id=>f(CARD(id))); return i>=0?dw.splice(i,1)[0]:dw.pop(); };
      const top=pickId(k=>k.c==="b" && k.v===5); H[0].push(pickId(k=>k.c==="b" && typeof k.v==="number" && k.v!==5), pickId(k=>k.c==="r" && k.v===5), pickId(k=>k.v==="wild"), pickId(k=>k.c==="y" && k.v==="d2"), pickId(k=>k.c==="g" && typeof k.v==="number"));
      while(H[0].length<hs) H[0].push(dw.pop()); for(let i=1;i<4;i++) while(H[i].length<hs) H[i].push(dw.pop()); dw.push(top); }
    else for(let r=0;r<hs;r++) for(let i=0;i<4;i++) H[i].push(dw.pop());
    let top; do{ top=dw.pop(); if(typeof CARD(top).v!=="number"){ dw.unshift(top); top=null; } }while(top==null);
    const first=TUT?0:Math.floor(Math.random()*4);
    act({t:"deal", h:H, dw, top}).then(()=>wait(.6)).then(()=>beginTurn(first)); }

  /* ══ 👫 같이 하기 (MG.room · 최대 4명 · 빈자리 봇 · 방장이 판을 돌림) ══ */
  let hostC="", hostMiss=0;
  const hostCode=()=>{ if(!RM || !RM.d) return hostC; const live=RM.live(true).map(p=>p.k), h=RM.d.h||{}; return live.indexOf(h.c)>=0?h.c:(live[0]||h.c); };
  function startCo(){ CO=true; TUT=false; coachOn=false; phase="room";
    RM=MG.room(api, {pre:"mgc", title:"컬러팡 같이 하기", ic:"🃏", max:4, fill:true, wait:8000, send:.5, poll:.35,
      h:()=>({hs:SET.hs, stk:SET.stk, df:SET.df}), tag:h=>'🃏 '+(h.hs||7)+'장'+(h.stk?' · 📚 쌓기':''),
      back:()=>{ try{ RM.dispose(); }catch(e){} RM=null; CO=false; phase="menu"; menuShow(); }});
    RM.node=()=>({av:api.av||null, bk:SET.bk});
    { const st0=RM.start; RM.start=async()=>{ const ro=RM.live(true).map(p=>p.k).slice(0,4); try{ await NET.patch(RM.path+"/h", {ro}); }catch(e){} if(RM.d && RM.d.h) RM.d.h.ro=ro; return st0(); }; }   /* 자리표는 방장이 시작할 때 정함 (모두 같은 자리) */
    RM.onEv=(e)=>{ if(e && e.t==="in" && HOST && phase==="play") hostIn(e.s, e.a, e); };
    RM.onFeed=(f)=>{ if(f && f.t==="emo" && phase==="play") emote(f.s, f.e); };
    RM.onStart=(h, live)=>{ const codes=(h.ro && h.ro.length ? h.ro : live.map(p=>p.k)).slice(0,4); hostC=h.c; const PD=(RM.d&&RM.d.p)||{}; RULE={hs:h.hs||7, stk:h.stk?1:0}; BOTDF=h.df||"normal";
      const names=BOTS.slice(); let s=(h.seed||1)>>>0; const rnd=()=>{ s=(s*1103515245+12345)>>>0; return s/4294967296; };
      for(let i=names.length-1;i>0;i--){ const j=Math.floor(rnd()*(i+1)); [names[i],names[j]]=[names[j],names[i]]; }
      G.P=[]; for(let i=0;i<4;i++){ const c=codes[i]; if(c){ const p=Object.assign({}, PD[c]||{}, live.find(q=>q.k===c)||{}); G.P.push({nm:p.n||"친구", k:c, bot:false, h:[], col:PCOL[i], av:p.av||{}, bk:p.bk||"base", called:false}); } else G.P.push(botP(i, names[i], BACKS[Math.floor(rnd()*BACKS.length)].k)); }
      ME=Math.max(0, codes.indexOf(RM.code)); HOST=(h.c===RM.code); phase="play";
      [1,2,3].forEach(L=>seatAv(L, G.P[glo(L)].av)); plates(); drawTop(); handSig=""; drawHand();
      if(HOST) later(.4, dealHost); };
  }
  /* 친구 화면: 방의 g 를 보고 따라 함 */
  let lastSync=0;
  function coTick(dt){ if(!RM || !CO || phase==="menu") return; try{ RM.tick(dt); }catch(e){}
    if(phase!=="play" && phase!=="end") return;
    const g=RM.d && RM.d.g; const hc=hostCode(); hostMiss=(hc!==hostC)?hostMiss+dt:0; if(hc!==hostC && hostMiss>7) hostC=hc;   /* 방장이 7초 넘게 안 보일 때만 바뀜 */
    const amHost=hostC===RM.code;
    if(amHost && !HOST){ HOST=true; /* 방장이 나감 → 내가 이어서 */ if(g && g.sq>G.sq) hardSync(g); if(!G.over){ feed('👑 내가 방장이 되었어요'); later(.3, ()=>{ if(!G.lock && !Q.length) beginTurn(G.turn<0?0:G.turn); }); } }
    if(HOST){ pubT+=dt; if(pubT>1.5 && RM.path) pub();
      /* 나간 친구 → 봇 */ const live=RM.live(true).map(p=>p.k); G.P.forEach((p,i)=>{ if(!p.bot && p.k && p.k!==RM.code && live.indexOf(p.k)<0){ p.gone=(p.gone||0)+dt; if(p.gone>8){ p.bot=true; feed('🚪 '+esc(p.nm)+' 나감 → 🤖'); if(G.turn===i && !G.lock && !G.over) later(.5,()=>botMove(i)); } } else p.gone=0; });
      return; }
    if(!g || !g.A) return;
    if(g.sq<=G.sq) return;
    const A=g.A, first=A.length?A[0].n:g.sq+1;
    if(!synced || G.sq<first-1 || !G.P.length){ hardSync(g); if(G.sq>=g.sq) return; }
    A.forEach(a=>{ if(a.n>G.sq && !Q.some(q=>q.n===a.n)) Q.push(a); }); runQ(); }
  let synced=false;
  function hardSync(g, keepQ){ const s=g.s; if(!s) return; EP++; synced=true; if(!keepQ) Q.length=0; const mi=s.P.findIndex(q=>q.k===(RM&&RM.code)); if(mi>=0) ME=mi; s.P.forEach((q,i)=>{ const p=G.P[i]||(G.P[i]={}); Object.assign(p,{h:q.h.slice(), called:!!q.c, k:q.k, nm:q.nm, bot:!!q.b, av:q.av, bk:q.bk, col:q.col}); });
    G.draw=s.dw.slice(); G.pile=s.pl.slice(); G.top=s.top>=0?CARD(s.top):null; G.dir=s.dir; G.turn=s.turn; G.pend=s.pend|0; G.over=!!s.over; G.dl=s.dl; G.hist=s.hist||[]; G.drew=!!s.drew; G.sq=(s.sq!=null?s.sq:g.sq); SEQ=Math.max(SEQ,g.sq); G.A=(g.A||[]).slice(); G.wait=false;
    if(G.top){ pileReset(); G.pile.slice(-5).forEach(id=>pileAdd(CARD(id))); setCur(s.cur); }
    [1,2,3].forEach(L=>{ seatAv(L, G.P[glo(L)].av); fan(SEATS[L], G.P[glo(L)].h.length, G.P[glo(L)].bk); }); pileH(); pendUI(); myArc.visible=G.turn===ME; handSig=""; drawHand(); plates(); drawTop(); hint(); cmd(); }

  /* ══ 시작 ══ */
  const LG0=league(T0().win); $(".cpPor .who").textContent=(api.nick||"나")+" · "+LG0.ic+" "+LG0.nm;
  let ready=false;
  [1,2,3].forEach(L=>seatAv(L, BOTS[L-1].av));
  loadImgs().then(()=>{ if(gone) return; TEX.forEach(e=>{ try{ e.t.dispose(); e.m.dispose(); }catch(_){} }); TEX.clear(); Object.keys(FANM).forEach(k=>delete FANM[k]);
    setDeckBack(); [1,2,3].forEach(L=>{ SEATS[L].n=-1; fan(SEATS[L], 5, BACKS[L].k); }); $(".cpLoad").remove(); ready=true;
    if(O.quick){ MENU.style.display="none"; HUD.classList.remove("inMenu"); startSolo(!!O.tut); } else menuShow(); });
  plates(); drawTop(); hint(); cmd();

  /* ══ 매 프레임 ══ */
  let fr=0, lastA=0; const q0=new THREE.Quaternion(), q1=new THREE.Quaternion();
  function fitCam(){ const a=cam.aspect||1; if(Math.abs(a-lastA)<.01) return; lastA=a; let fov, p, l;
    if(a<1){ const t=Math.max(0,Math.min(1,(a-.46)/(.72-.46))); fov=52-8*t; p=[0,4.15-.25*t,5.35-.75*t]; l=[0,.6,-.15-.1*t]; }
    else { const t=Math.max(0,Math.min(1,(a-1.3)/(2.16-1.3))); fov=46-4*t; p=[0,3.0-.1*t,3.55-.15*t]; l=[0,.8,-.62]; }
    cam.fov=fov; cam.position.set(...p); cam.lookAt(...l); cam.updateProjectionMatrix(); HUD.classList.toggle("land", a>=1); HUD.classList.toggle("pad", a>=.6 && a<1); try{ scene.userData.sign.visible=a>=.6; }catch(e){} layoutHand(); }
  function tick(dt){ if(paused || gone) return; const steps=fast?20:1;
    for(let s=0;s<steps;s++){ const d=fast?.05:dt;
      for(let i=TM.length-1;i>=0;i--){ TM[i].t-=d; if(TM[i].t<=0){ const f=TM[i].fn; TM.splice(i,1); try{ f(); }catch(e){ console.warn("CP", e); } } }
      for(let i=FLY.length-1;i>=0;i--){ const f=FLY[i]; f.t+=d/f.dur; const t=Math.min(1,f.t), e=t<.5?2*t*t:1-Math.pow(-2*t+2,2)/2;
        f.m.position.lerpVectors(f.from,f.to,e); f.m.position.y+=Math.sin(t*Math.PI)*f.arc; q0.setFromEuler(f.r0); q1.setFromEuler(f.r1); f.m.quaternion.copy(q0).slerp(q1,e);
        if(t>=1){ FLY.splice(i,1); scene.remove(f.m); f.res(); } }
      if(G.oneWin) G.oneWin.t-=d;
      /* 시간 다 됨 (방장이 사람 차례만) */
      if(HOST && phase==="play" && !G.over && G.turn>=0 && !G.lock && !Q.length && G.P[G.turn] && !G.P[G.turn].bot && G.dl && now()>G.dl+(fast?-29000:0)){ const g=G.turn; G.dl=now()+60000;
        if(G.pend>0) takePend(g); else if(!G.drew){ G.lock=true; giveCards(g,1,true).then(()=>{ G.lock=false; return doPass(g,"⏰ 시간"); }); } else doPass(g,"⏰ 시간"); } }
    if(CO) coTick(dt);
    if(banT>0){ banT-=dt; if(banT<=0) $(".cpBan").classList.remove("on"); }
    if(toastT>0){ toastT-=dt; if(toastT<=0){ $(".cpHint").classList.remove("warn"); hint(); } }
    if(mtT>0){ mtT-=dt; if(mtT<=0) $(".cpMT").classList.remove("on"); }
    if(replyT>0) replyT-=dt;
    glowCol.lerp(glowTo, Math.min(1,dt*6)); glowM.color.copy(glowCol); haloM.color.copy(glowCol);
    if(popS.visible){ popT+=dt; const k=popT<.15?popT/.15:1; popS.scale.setScalar(.65*(.6+.4*k)*(1+.08*Math.sin(popT*20))); popM.opacity=popT>.55?Math.max(0,1-(popT-.55)/.25):1; if(popT>.8) popS.visible=false; }
    [1,2,3].forEach(L=>{ const s=SEATS[L]; if(!s || !s.P) return; s.t+=dt; const th=G.turn===glo(L) && !G.over && phase==="play"; s.P.g.position.y=.25+(th?Math.abs(Math.sin(s.t*5))*.025:Math.sin(s.t*1.6)*.006); s.P.head.rotation.y=th?Math.sin(s.t*2)*.15:Math.sin(s.t*.7)*.08;
      if(s.actT>0 && s.actT<90){ s.actT-=dt; if(s.actT<=0) s.P.setExpr(s.P.expr0||"smile"); } });
    for(const m of CONF){ m.position.y-=m.userData.v*dt; m.rotation.x+=m.userData.s*dt; m.rotation.y+=dt*2; if(m.position.y<TY+.02) m.position.y=TY+.02; }
    const bar=$(".cpBar i"); if(bar) bar.style.width=(phase==="play" && G.turn===ME && !G.over && G.dl?Math.max(0,Math.min(100,(G.dl-now())/(TURN_T*10))):0)+"%";
    if(G.oneWin && G.oneWin.s===ME && fr%6===0) cmd();
    fitCam(); platePos(); if(fr%20===0 && phase==="play") coachCheck(); }
  function render(rn){ fr++; const box=$(".cpPor"); if(ME_AV && box && (fr%8===1 || porCv.width<4)){ const r=box.getBoundingClientRect(), pr=rn.getPixelRatio(), sz=Math.max(8,Math.round(r.width-8));
      if(porCv.width!==Math.round(sz*pr)){ porCv.width=porCv.height=Math.round(sz*pr); }
      try{ rn.setScissorTest(true); rn.setScissor(0,0,sz,sz); rn.setViewport(0,0,sz,sz); rn.render(PSc,PC); porG.clearRect(0,0,porCv.width,porCv.height); porG.drawImage(rn.domElement,0,rn.domElement.height-porCv.height,porCv.width,porCv.height,0,0,porCv.width,porCv.height); }catch(e){}
      rn.setScissorTest(false); const c=rn.domElement; rn.setViewport(0,0,c.width/rn.getPixelRatio(),c.height/rn.getPixelRatio()); }
    MG.draw(scene, cam); }
  function dispose(){ gone=true; TM.length=0; FLY.length=0; Q.length=0; coachClear(); try{ if(RM) RM.dispose(); }catch(e){} try{ U.classList.remove("cpOn"); HUD.remove(); }catch(e){} disp.forEach(x=>{ try{ x.dispose(); }catch(e){} }); TEX.forEach(e=>{ try{ e.t.dispose(); e.m.dispose(); }catch(_){} }); TEX.clear(); }
  return {scene, cam, tick, render, dispose, pause:(v)=>{ paused=!!v; }, G, SEATS, ST, CARD, okC, get phase(){ return phase; }, get ME(){ return ME; }, get HOST(){ return HOST; }, get RM(){ return RM; }, get TUT(){ return TUT; }, get coach(){ return Object.assign({}, COACH); },
    get auto(){ return auto; }, set auto(v){ auto=!!v; if(auto && isMyTurn()) later(.1, autoMove); }, set fast(v){ fast=v?1:0; FASTX=!!v; }, get fast(){ return !!fast; }, get ready(){ return ready; },
    tapCard, myDraw:()=>input(G.drew && G.pend<=0?"pass":"draw"), callOne:()=>input("one"), menuGo, menuShow, cmd, drawHand, isMyTurn, missList, SET, input}; }

MG.reg("card", {ic:"🃏", nm:"컬러팡", tag:"색깔 카드 게임 · 혼자(봇 3명) · 친구랑 같이(최대 4명)", bg:"linear-gradient(135deg,#ff5a5f,#ffc83d 35%,#3fc46a 65%,#3ea2ff)", big:"🃏🌈", menu:true,
  how:[["🎨","<b>같은 색</b>이나 <b>같은 숫자</b> 카드를 내요"],["🏆","카드를 <b>먼저 다 내면</b> 이겨요"]],
  payTxt:"1등 🪙10 · 2등 🪙6 · 3등 🪙5 · 4등 🪙4",
  bestTxt:(b,t)=>{ const L=league(t.win); return '🏆 이긴 판 '+(t.win|0)+' · 🔥 최고 '+(b.bs|0)+'연승 · '+L.ic+' '+L.nm; },
  ui:{look:false, btns:[]},
  start});
window.CPF={cardSVG, mkDeck, league, isW};
})();
