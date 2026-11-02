/* (v544) 🏘 마을 시설 9곳 — 사용자: "마을에 있는 것들까지 생각해야 하는 거구나 · 그러면 다른 건 뭐가 있을까" → "일단 시설 다 넣어 보자"
   📣 마을 목표판 + 🎆 축제 (학원 모두가 이번 주 단어를 모으면 불꽃놀이 · 금요일 🎤 퀴즈 쇼)
   📮 우체국 (단어 조각으로 영어 편지 만들어 친구 집에 · 간식 선물 · 받은 편지 읽기)
   🐶 펫 가게 (펫이 나를 따라다님 · 밥 주기 · "Sit!" 듣고 재주 배우기)
   🏛 박물관 (물고기·광물·작물·요리 기증 → 마을 모두의 전시 · 기증한 아이 이름)
   🍦 간식 가게 + 🍗 배부름 (영어로 주문 · 배부르면 빨라짐 · 배고프면 느려짐)
   📸 사진관 (배경·포즈·영어 한 줄 → 사진 → 🖼 액자로 방에)
   📚 도서관 (영어 그림책 6권 · 읽어 주기 · 다 읽으면 문제 2개)
   🚉 기차역 (마을 어디든 · "Next stop is the lake!" 듣고 맞히기)
   🎃 계절 꾸밈 (봄 꽃잎 · 여름 파라솔 · 가을 단풍·호박 · 겨울 눈·트리 · ?season= 로 바꿔 보기)
   자리 = 마을 설계도(isle-map) 빈 곳 (길·땅·명소와 3칸 넘게 떨어짐) · 건물은 가까운 길을 봄 */
const TFAC=(()=>{
  const day=()=>{ try{ return dayKey(); }catch(e){ return new Date().toISOString().slice(0,10); } };
  const T=()=>{ try{ return now(); }catch(e){ return Date.now(); } };
  const kst=()=>new Date(T()+9*3600e3);
  const wkKey=()=>{ const d=kst(), w=(d.getUTCDay()+6)%7; return new Date(d.getTime()-w*864e5).toISOString().slice(0,10); };   /* 이번 주 월요일 */
  const nick=()=>{ try{ return String(kidInfo().n||"친구").slice(0,8); }catch(e){ return "친구"; } };
  const study=()=>{ try{ return JSON.parse(localStorage.getItem("hyeng_study_v1")||"{}"); }catch(e){ return {}; } };
  const isIsle=()=>{ try{ return window.ISLE && place===ISLE.PLC; }catch(e){ return false; } };
  const Q=new URLSearchParams(location.search);
  const daily=k=>{ let o=store("hyeng_proto_tfd")||{}; if(o.d!==day()) o={d:day()}; return {n:o[k]|0, add(){ o[k]=(o[k]|0)+1; store("hyeng_proto_tfd", o); }}; };
  const pay=(n,why)=>{ if(!n) return; gems+=n; saveBag(); try{ SND.big(); }catch(e){} toast("💎 +"+n+(why?" · "+why:""), 1600); };   /* 💎 = 영어 문제 (퀴즈 쇼·펫 재주·도서관) */
  const C5=5, payC=(n,why)=>{ if(!n) return; const c=n*C5; try{ TECO.addCoin(c); SND.big(); }catch(e){} toast("🪙 +"+c+(why?" · "+why:""), 1600); };   /* (v563) 사용자: 「💎 는 공부로」 → 축제·편지·박물관은 🪙 (예전 💎 × 5) */

  /* ── 간식 · 펫 밥 (가방 재료로) ── */
  const SNACK=[["cookie","🍪",1,1],["lemonade","🍋",1,1],["ice cream","🍦",2,1],["donut","🍩",2,1],["sandwich","🥪",3,2],["hot dog","🌭",3,2]];   /* [이름, 그림, 💎, 배부름 하트] */   /* (v561) 간식 juice(💎1) 가 요리 juice(수박, 팔면 💎14~23)와 같은 이름이라 사서 바로 팔면 이득 → lemonade */
  SNACK.forEach(([n,e])=>{ if(!MAT[n]) MAT[n]={e, food:1}; }); if(!MAT["pet food"]) MAT["pet food"]={e:"🦴"};

  /* ── 창 (HLIFE 와 같은 모양) ── */
  const st=document.createElement("style"); st.textContent=`
.tfTabs{display:flex;gap:6px;margin:0 0 8px;overflow-x:auto}.tfTabs button{flex:0 0 auto;height:36px;padding:0 12px;border-radius:999px;border:2.5px solid #3b2433;background:#fffdf7;font:14px var(--kr);color:#3b2433}.tfTabs button.on{background:#ffd23f}
.tfGrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(92px,1fr));gap:6px}
.tfGrid button{min-height:96px;border-radius:16px;border:2.5px solid #3b2433;background:#fffdf7;box-shadow:0 3px 0 #3b2433;font:12px var(--kr);color:#3b2433;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;padding:4px}
.tfGrid button i{font-style:normal;font-size:30px}.tfGrid button b{font:800 13px var(--en)}.tfGrid button.no{opacity:.45;background:#efe6d6}.tfGrid button.can{background:#fff3c4;outline:3px dashed #e0a41a}
.tfCard{border:3px solid #3b2433;border-radius:20px;background:#fffdf7;box-shadow:0 3px 0 #3b2433;padding:12px;margin:6px 0;text-align:center}
.tfCard .big{font-size:56px;line-height:1.1}.tfCard .en{font:800 21px var(--en);margin:6px 0 2px}.tfCard .ko{font-size:14px;color:#8a6a4a}
.tfBar{height:20px;border-radius:999px;border:2.5px solid #3b2433;background:#efe6d6;overflow:hidden;margin:6px 0}.tfBar i{display:block;height:100%;background:linear-gradient(90deg,#ffd23f,#ff7aa8)}
.tfRow{display:flex;gap:8px;flex-wrap:wrap;justify-content:center;margin:8px 0}
.tfRow button{min-width:64px;height:48px;padding:0 12px;border-radius:14px;border:3px solid #3b2433;background:#fffdf7;box-shadow:0 3px 0 #3b2433;font:800 17px var(--en);color:#3b2433}
.tfRow button.r{background:#bff0a8}.tfRow button.w{background:#ffc4c4;animation:tfShake .3s}.tfRow button.sel{background:#ffd23f}
.tfAns{min-height:52px;border:3px dashed #c9b28e;border-radius:16px;padding:6px;display:flex;gap:6px;flex-wrap:wrap;justify-content:center;align-items:center;font:800 18px var(--en)}
.tfAns span{background:#bff0a8;border:2.5px solid #3b2433;border-radius:10px;padding:4px 8px}
@keyframes tfShake{25%{transform:translateX(-5px)}75%{transform:translateX(5px)}}
#tfRide{position:fixed;inset:0;z-index:30;display:none;flex-direction:column;align-items:center;justify-content:center;background:linear-gradient(#8fd3f0,#cfeffc 60%,#7fc463 60%);font-family:var(--kr);color:#3b2433}
#tfRide.on{display:flex}#tfRide .tr{font-size:60px;white-space:nowrap;animation:tfTrain 2.6s linear infinite}#tfRide .an{margin-top:18px;background:#fffdf7;border:3px solid #3b2433;border-radius:18px;padding:10px 16px;font:800 22px var(--en);box-shadow:0 4px 0 #3b2433}
#tfRide .qq{margin-top:12px;font-size:16px}
@keyframes tfTrain{from{transform:translateX(70vw)}to{transform:translateX(-70vw)}}
.pill.full b{letter-spacing:-1px}`; document.head.appendChild(st);
  function sheet(id){ let d=$(id); if(d) return d; d=document.createElement("div"); d.id=id; d.className="hlP"; d.innerHTML='<div class="lb"></div>'; document.body.appendChild(d);
    d.addEventListener("click", e=>{ if(e.target===d || e.target.closest(".x")) d.classList.remove("on"); }); ["pointerdown","pointerup"].forEach(ev=>d.addEventListener(ev, e=>e.stopPropagation())); try{ SHEETS.push(id); }catch(e){} return d; }
  function show(id, html){ const d=sheet(id); d.querySelector(".lb").innerHTML=html; d.classList.add("on"); return d; }
  const close=id=>{ const d=$(id); if(d) d.classList.remove("on"); };
  const hd=(t,s)=>'<h3>'+t+'<small>'+(s||"")+'</small><button class="x" aria-label="닫기">✕</button></h3>';
  /* 그림 → 영어 3~4개 중 고르기 (한 문제) */
  function pick1(title, e, ans, pool, then, opt){ opt=opt||{}; let q=$("hqP"); if(!q){ HLIFE.quiz("", [], ()=>{}); q=$("hqP"); } const box=q.querySelector(".b");
    const opts=[ans]; let g=0; while(opts.length<(opt.n||4) && g++<80){ const x=pool[Math.floor(Math.random()*pool.length)]; if(x && opts.indexOf(x)<0) opts.push(x); } opts.sort(()=>Math.random()-.5);
    box.innerHTML='<div class="t">'+title+'</div><div class="e">'+e+'</div><div class="k">'+(opt.ask||"영어로?")+'</div><div class="o">'+opts.map(o=>'<button data-w="'+esc(o)+'">'+esc(o)+'</button>').join("")+'</div>';
    box.onclick=ev=>{ const b=ev.target.closest("[data-w]"); if(!b || box.dataset.lock) return; const r=b.dataset.w===ans; if(!r && opt.retry){ b.classList.add("w"); try{ SND.snap(); say(ans); }catch(_){} setTimeout(()=>b.classList.remove("w"),500); return; }
      box.dataset.lock=1; b.classList.add(r?"r":"w"); box.querySelectorAll("[data-w]").forEach(x=>{ if(x.dataset.w===ans) x.classList.add("r"); }); try{ say(ans); (r?SND.win:SND.snap)(); }catch(_){}
      setTimeout(()=>{ delete box.dataset.lock; q.classList.remove("on"); then(r); }, 900); };
    q.classList.add("on"); }

  /* ═════════ 🏗 건물 (isle.js build 가 부름) ═════════ */
  /* (v550) 자리는 마을 설계도(ISLE_MAP.spots) — 🍦 간식 · 🐶 펫 · 📸 사진관은 🏪 상점가 가게로 옮김 */
  const FAC=[
    {k:"goal", ic:"📣", t:"마을 목표판"},
    {k:"post", ic:"📮", t:"우체국", w:4, d:3.4, h:2.2, wall:0xfff3e0, roof:0xe24b4b, bg:"#ffd0d0", face:"plaza"},
    {k:"museum", ic:"🏛", t:"박물관", w:5, d:3.8, h:2.7, wall:0xf3eee2, roof:0xd6cbb2, bg:"#f3eee2", face:"campus"},
    {k:"library", ic:"📚", t:"도서관", w:4.6, d:3.6, h:3.2, wall:0xffeccc, roof:0x5aa7ff, bg:"#d6ebff", face:"campus"},
    {k:"station", ic:"🚉", t:"기차역", w:4.4, d:2.6, h:2.4, wall:0xfff3e0, roof:0x4caf50, bg:"#d8f5cc", face:"plaza"},
    {k:"bank", ic:"🏦", t:"마을 은행", w:4.4, d:3.4, h:2.8, wall:0xf6f0e2, roof:0xd9a62e, bg:"#fff1c9", face:"plaza"},   /* (v563) 💰 환전 · 저금 · 적금 · 🛠 강화 */
  ];
  let C=null; const SP={}; let goalTex=null, goalCv=null, bunt=null, parts=null, fw=null;
  function faceDir(x,z){ const M_=C.MAP; let best=1e9, bp=null; const segs=Object.values(M_.roads).map(r=>r.p).concat(M_.hoods.map(h=>h.p));
    segs.forEach(P=>{ const Qp=M_.cr(P,8); for(let i=1;i<Qp.length;i++){ const a=Qp[i-1], b=Qp[i], dx=b[0]-a[0], dz=b[1]-a[1], L2=dx*dx+dz*dz||1, t=Math.max(0,Math.min(1,((x-a[0])*dx+(z-a[1])*dz)/L2)), px=a[0]+dx*t, pz=a[1]+dz*t, d=Math.hypot(x-px,z-pz); if(d<best){ best=d; bp=[px,pz]; } } });
    let fx=bp?bp[0]-x:-x, fz=bp?bp[1]-z:-z; const L=Math.hypot(fx,fz)||1; return [fx/L, fz/L]; }
  const mergeIn=W=>{ if(!C.vcMerge) return; const L=[]; W.children.slice().forEach(m=>{ if(m.isMesh && m.material && m.material.isMeshStandardMaterial && !m.material.vertexColors){ m.updateMatrix(); L.push({g:m.geometry, col:m.material.color.clone().convertLinearToSRGB().getHex(), m:m.matrix.clone()}); W.remove(m); } }); if(L.length){ W.add(C.vcMerge(L)); L.forEach(e=>e.g.dispose()); } };
  function building(f){ const [x,z]=f.at, D=f.face==='plaza' ? (()=>{ const L=Math.hypot(x,z)||1; return [-x/L,-z/L]; })() : f.face==='campus' && C.MAP.spots.campus ? (()=>{ const c=C.MAP.spots.campus, L=Math.hypot(c[0]-x,c[1]-z)||1; return [(c[0]-x)/L,(c[1]-z)/L]; })() : faceDir(x,z), ry=Math.atan2(D[0],D[1]), OX=C.OX, OZ=C.OZ;
    const W=new THREE.Group(); W.position.set(x+OX,0,z+OZ); W.rotation.y=ry; W.userData.solo=1; W.userData.fac=f.k;
    const B=(w,h,d,col,bx,by,bz)=>C.box(W,w,h,d,col,bx,by+h/2,bz);
    const X=(geo,col,px,py,pz,rx,ry2,rz,o)=>{ const m=new THREE.Mesh(geo, o&&o.basic?new THREE.MeshBasicMaterial({color:C.LIN(col)}):C.MC(col)); m.position.set(px,py,pz); m.rotation.set(rx||0,ry2||0,rz||0); m.castShadow=true; m.receiveShadow=true; W.add(m); return m; };
    const gable=(w,d,hh,col,y)=>{ const s=new THREE.Shape(); s.moveTo(-w/2-.25,0); s.lineTo(w/2+.25,0); s.lineTo(0,hh); s.lineTo(-w/2-.25,0); const g=new THREE.ExtrudeGeometry(s,{depth:d+.4, bevelEnabled:false}); g.translate(0,0,-(d+.4)/2); return X(g,col,0,y,0); };
    const L2W=(lx,lz)=>[x+lx*Math.cos(ry)+lz*Math.sin(ry), z-lx*Math.sin(ry)+lz*Math.cos(ry)];
    const w=f.w, d=f.d, h=f.h, fr=d/2;
    // 공통 — 바닥 판 · 벽 · 문 · 창 · 띠
    B(w+.4,.18,d+.4,0xd9c9a8,0,0,0); B(w,h,d,f.wall,0,.18,0); B(.95,1.5,.12,0x8a5a3a,0,.18,fr+.02); B(.18,.18,.1,0xffd23f,.3,.9,fr+.1);
    [-1,1].forEach(s=>{ if(w>3.2){ B(.82,.72,.1,0x9fd8ff,s*(w/2-.85),1.05,fr+.02); B(.95,.1,.14,0xffffff,s*(w/2-.85),.98,fr+.06); } });
    B(w+.04,.22,d+.04,f.roof,0,h-.05,0);
    let top=h+.18;
    if(f.k==="post"){ gable(w,d,1.1,f.roof,top); B(.5,.8,.42,0xe24b4b,w/2+.6,.0,fr+.6); X(new THREE.CylinderGeometry(.21,.21,.42,14,1,false,0,Math.PI),0xe24b4b,w/2+.6,.8,fr+.6,Math.PI/2,0,Math.PI/2); B(.12,.5,.12,0x7a4f2c,w/2+.6,0,fr+.6); B(.3,.06,.02,0x3b2433,w/2+.6,.55,fr+.82);
      B(1.1,.7,.08,0xffffff,0,top+.15,fr+.24); X(new THREE.BoxGeometry(.7,.42,.05),0xffd0d0,0,top+.5,fr+.3); }
    else if(f.k==="snack"){ B(w+.2,.25,d+.2,f.roof,0,top-.1,0); for(let i=0;i<6;i++){ const aw=X(new THREE.BoxGeometry((w+.2)/6,.06,.9),i%2?0xffffff:0xff7aa8,-w/2-.1+(i+.5)*(w+.2)/6,1.95,fr+.38,.42); aw.castShadow=false; }
      X(new THREE.ConeGeometry(.42,1.0,14),0xe8b46a,0,top+.62,0,Math.PI); X(new THREE.SphereGeometry(.46,14,10),0xffb6d1,0,top+1.2,0); X(new THREE.SphereGeometry(.36,14,10),0x9ff0d0,0,top+1.62,0); X(new THREE.SphereGeometry(.1,8,6),0xff4b4b,0,top+1.98,0);
      [-1,1].forEach(s=>{ X(new THREE.CylinderGeometry(.32,.32,.06,16),0xffffff,s*1.1+1.6*s,.62,fr+1.3); X(new THREE.CylinderGeometry(.04,.04,.6,6),0x7a4f2c,s*2.7,.3,fr+1.3); }); }
    else if(f.k==="pet"){ gable(w,d,1.0,f.roof,top); X(new THREE.CylinderGeometry(.12,.12,1.0,10),0xffffff,0,top+.35,fr+.25,0,0,Math.PI/2); [-.5,.5].forEach(s=>[-.1,.1].forEach(t=>X(new THREE.SphereGeometry(.15,10,8),0xffffff,s,top+.35+t,fr+.25)));
      const yx=w/2+1.5; for(let i=0;i<7;i++){ const a=i/6; B(.08,.6,.08,0xffffff,yx-1+a*2,0,fr+.3); B(.08,.6,.08,0xffffff,yx-1+a*2,0,-fr); } [[-1],[1]].forEach(([s])=>{ B(2.1,.08,.06,0xffffff,yx,.4,s>0?fr+.3:-fr); }); B(.06,.08,d+.3,0xffffff,yx+1,.4,.15);
      B(.9,.7,.8,0xd9a066,yx,0,-.3); { const s=new THREE.Shape(); s.moveTo(-.55,0); s.lineTo(.55,0); s.lineTo(0,.45); s.lineTo(-.55,0); const g=new THREE.ExtrudeGeometry(s,{depth:1.0,bevelEnabled:false}); g.translate(0,0,-.5); X(g,0xc94545,yx,.7,-.3); } B(.4,.42,.05,0x3b2433,yx,0,.11); }
    else if(f.k==="museum"){ B(w+1.2,.16,d+1.6,0xe9e2d0,0,0,.3); B(w+.8,.16,d+1.2,0xf3eee2,0,.16,.2); [-1.8,-.6,.6,1.8].forEach(cx=>{ X(new THREE.CylinderGeometry(.2,.24,h,12),0xffffff,cx,h/2+.3,fr+.55); X(new THREE.BoxGeometry(.5,.14,.5),0xe9e2d0,cx,.38,fr+.55); X(new THREE.BoxGeometry(.5,.14,.5),0xe9e2d0,cx,h+.24,fr+.55); });
      B(w+.5,.32,d+1.1,0xe9e2d0,0,h+.25,.28); gable(w+.2,d+.7,.9,f.roof,h+.57); X(new THREE.CircleGeometry(.32,20),0xffd23f,0,h+.9,fr+.67,0,0,0,{basic:1}); }
    else if(f.k==="photo"){ gable(w,d,.8,f.roof,top); B(1.0,.62,.56,0x3b2433,0,top+.72,.1); X(new THREE.CylinderGeometry(.22,.24,.32,16),0x9fd8ff,0,top+1.03,.5,Math.PI/2); X(new THREE.CylinderGeometry(.26,.26,.06,16),0x3b2433,0,top+1.03,.66,Math.PI/2); B(.28,.16,.2,0xffd23f,-.3,top+1.34,0);
      [-1,1].forEach(s=>X(new THREE.OctahedronGeometry(.16),0xffd23f,s*1.3,top+.5,fr+.2,0,0,0,{basic:1})); }
    else if(f.k==="library"){ for(let r=0;r<2;r++) [-1,0,1].forEach(c=>{ if(r===0 && c===0) return; B(.7,.75,.1,0x9fd8ff,c*1.45,.8+r*1.35,fr+.02); }); B(w+.1,.14,d+.1,0xc9925c,0,1.72,0); gable(w,d,1.2,f.roof,top);
      [[0xff6b6b,0],[0x5aa7ff,.32],[0xffd23f,.64]].forEach(([c,y],i)=>B(1.1-i*.12,.3,.75,c,-w/2-.85,y,fr-.1)); X(new THREE.CylinderGeometry(.3,.3,.06,20),0xffffff,0,top+.55,fr+.25,Math.PI/2); X(new THREE.BoxGeometry(.04,.22,.02),0x3b2433,0,top+.6,fr+.29); }
    else if(f.k==="station"){ X(new THREE.BoxGeometry(w+3.6,.14,d+1.6),0x4caf50,0,h+.28,.1); [-1,1].forEach(s=>[-1,1].forEach(t=>B(.14,h,.14,0xffffff,s*(w/2+1.6),.18,t>0?fr+.55:-fr-.4)));
      gable(w,d,.9,0xc94545,h+.35); X(new THREE.CylinderGeometry(.32,.32,.06,20),0xffffff,0,h+.75,fr+.24,Math.PI/2); X(new THREE.BoxGeometry(.04,.22,.02),0x3b2433,0,h+.8,fr+.28);
      const rz=-fr-1.25; B(w+5,.12,2.0,0xcfc8b8,0,0,-fr-1.25+.0); for(let i=-5;i<=5;i++) B(.18,.06,1.2,0x7a4f2c,i*.62,.12,rz); [-.42,.42].forEach(o=>B(w+5,.08,.08,0x8f8f9a,0,.18,rz+o));
      const car=(cx,col,eng)=>{ B(1.35,.75,.92,col,cx,.36,rz); B(1.45,.1,1.0,0x3b2433,cx,1.11,rz); [-.42,.42].forEach(wx=>[-.48,.48].forEach(wz=>X(new THREE.CylinderGeometry(.18,.18,.08,12),0x3b2433,cx+wx,.34,rz+wz,Math.PI/2)));
        if(eng){ X(new THREE.CylinderGeometry(.3,.3,.9,14),col,cx+.45,.95,rz,0,0,Math.PI/2); X(new THREE.CylinderGeometry(.09,.13,.4,10),0x3b2433,cx+.75,1.45,rz); B(.6,.5,.92,0xffd23f,cx-.35,1.11,rz); } else [-.32,.32].forEach(wx=>B(.36,.3,.04,0x9fd8ff,cx+wx,.66,rz+.47)); };
      car(-2.3,0xff6b6b,1); car(-.8,0x5aa7ff); car(.7,0xffd23f);
      [-2.3,-.8,.7].forEach(cx=>{ const p=L2W(cx,rz); C.cols.push([p[0]+OX,p[1]+OZ,.75]); }); [-4,-2,0,2,4].forEach(cx=>{ const p=L2W(cx,rz); C.busy.push([p[0],p[1],1.3]); }); }
    C.flush(W); mergeIn(W); C.G.add(W);
    const rad=Math.max(w,d)/2*.92+(f.k==="museum"?.3:0); C.cols.push([x+OX,z+OZ,rad]); C.busy.push([x,z,rad+1.4]); if(f.k==="pet"){ const p=L2W(w/2+1.5,0); C.cols.push([p[0]+OX,p[1]+OZ,1.1]); C.busy.push([p[0],p[1],1.6]); }
    const sp=new THREE.Sprite(new THREE.SpriteMaterial({map:C.signTex(f.ic+" "+f.t, f.bg, 448), depthWrite:false})); sp.scale.set(2.5,.72,1); const sg=L2W(0,fr+.5); sp.position.set(sg[0]+OX, f.k==="museum"?h+1.95:(f.k==="library"?h+2.0:h+1.65), sg[1]+OZ); sp.renderOrder=2; C.G.add(sp); C.SIGNS.push(sp);
    const dp=L2W(0,fr+(f.k==="museum"?1.9:1.25)), lp=L2W(0,fr+.4); SP[f.k]={k:f.k, ic:f.ic, t:f.t, p:[lp[0]+OX,1.6,lp[1]+OZ], door:[dp[0]+OX, dp[1]+OZ], at:[x+OX,z+OZ]}; }
  /* 📣 목표판 — 광장 쪽을 보는 큰 판 (글씨 = 그림판, 서버 값이 오면 다시 그림) */
  function goalBoard(f){ const [x,z]=f.at, OX=C.OX, OZ=C.OZ, ry=Math.atan2(-x,-z), W=new THREE.Group(); W.position.set(x+OX,0,z+OZ); W.rotation.y=ry;
    [-1,1].forEach(s=>{ const p=new THREE.Mesh(new THREE.CylinderGeometry(.07,.07,2.3,8), C.MC(0x9a6a40)); p.position.set(s*1.05,1.15,0); p.castShadow=true; W.add(p); });
    const bd=new THREE.Mesh(new THREE.BoxGeometry(2.3,1.45,.1), C.MC(0xc9925c)); bd.position.y=1.55; bd.castShadow=true; W.add(bd);
    goalCv=document.createElement("canvas"); goalCv.width=512; goalCv.height=320; goalTex=new THREE.CanvasTexture(goalCv); goalTex.encoding=THREE.sRGBEncoding;
    const pl=new THREE.Mesh(new THREE.PlaneGeometry(2.1,1.3), new THREE.MeshBasicMaterial({map:goalTex})); pl.position.set(0,1.55,.06); W.add(pl);
    mergeIn(W); C.G.add(W); C.cols.push([x+OX,z+OZ,.9]); C.busy.push([x,z,1.6]); const fx=-Math.sin(ry+Math.PI), fz=-Math.cos(ry+Math.PI);
    SP.goal={k:"goal", ic:"📣", t:"마을 목표판", p:[x+OX,2.6,z+OZ], door:[x+OX+Math.sin(ry)*1.4, z+OZ+Math.cos(ry)*1.4], at:[x+OX,z+OZ]}; drawGoal(); }
  function drawGoal(){ if(!goalCv) return; const g=goalCv.getContext("2d"), G_=GOAL, pct=Math.min(1, G_.tot/Math.max(1,G_.target));
    g.fillStyle="#fffdf7"; g.fillRect(0,0,512,320); g.strokeStyle="#3b2433"; g.lineWidth=10; g.strokeRect(5,5,502,310);
    g.fillStyle="#3b2433"; g.font="bold 40px sans-serif"; g.textAlign="center"; g.fillText("📣 이번 주 마을 목표", 256, 62);
    g.font="bold 30px sans-serif"; g.fillText("📚 다 같이 단어 "+G_.target+"점", 256, 112);
    g.fillStyle="#efe6d6"; g.fillRect(40,140,432,52); g.fillStyle=pct>=1?"#ff7aa8":"#ffd23f"; g.fillRect(40,140,432*pct,52); g.strokeStyle="#3b2433"; g.lineWidth=6; g.strokeRect(40,140,432,52);
    g.fillStyle="#3b2433"; g.font="bold 30px sans-serif"; g.fillText(G_.tot+" / "+G_.target, 256, 177);
    g.font="bold 32px sans-serif"; g.fillStyle=pct>=1?"#e0457b":"#3b2433"; g.fillText(pct>=1?"🎉 축제 중! 불꽃놀이 🎆":"🎆 축제까지 "+Math.max(0,G_.target-G_.tot)+"점", 256, 250);
    g.font="24px sans-serif"; g.fillStyle="#8a6a4a"; g.fillText("Daily 30 단어 1개 = 1점 · 공부한 날 = 5점", 256, 292); goalTex.needsUpdate=true; try{ dirty=true; }catch(e){} }
  /* 🎏 광장 깃발 줄 · 🎃 계절 꾸밈 · 날리는 것(꽃잎·낙엽·눈) */
  function season(){ const s=Q.get("season"); if(s) return s; const m=kst().getUTCMonth()+1; return m>=3&&m<=5?"spring":m>=6&&m<=8?"summer":m>=9&&m<=11?"autumn":"winter"; }
  const SEA={spring:{flag:[0xff9ac8,0xffffff,0x9ff0d0,0xffd23f], p:0xffb6d1, n:"🌸 봄"}, summer:{flag:[0x5aa7ff,0xffd23f,0xffffff,0xff6b6b], p:0, n:"🏖 여름"}, autumn:{flag:[0xff8a3d,0xffd23f,0xc94545,0x8a5a34], p:0xe8742a, n:"🍁 가을"}, winter:{flag:[0xffffff,0x9fd8ff,0xc94545,0x4caf50], p:0xffffff, n:"⛄ 겨울"}};
  function decorate(){ const OX=C.OX, OZ=C.OZ, S=season(), sea=SEA[S]||SEA.spring, fest=GOAL.tot>=GOAL.target;
    // 깃발 줄: 분수 위 → 광장 둘레 8곳
    const pos=[], col=[], c3=new THREE.Color(); const flags=fest?[0xff6b6b,0xffd23f,0x5aa7ff,0x7fd36a,0xff9ac8]:sea.flag;
    const PR=C.MAP.plaza.r; for(let k=0;k<8;k++){ const a=k/8*6.283+.2, ex=Math.cos(a)*PR*.78, ez=Math.sin(a)*PR*.78, n=9;
      for(let i=1;i<n;i++){ const t=i/n, x=ex*t, z=ez*t, y=2.75-(2.75-2.35)*t-Math.sin(t*Math.PI)*.45, tx=-Math.sin(a)*.17, tz=Math.cos(a)*.17; c3.set(flags[(i+k)%flags.length]).convertSRGBToLinear();
        [[x-tx,y,z-tz],[x+tx,y,z+tz],[x,y-.36,z]].forEach(v=>{ pos.push(v[0]+OX,v[1],v[2]+OZ); col.push(c3.r,c3.g,c3.b); }); } }
    const bg=new THREE.BufferGeometry(); bg.setAttribute("position",new THREE.Float32BufferAttribute(pos,3)); bg.setAttribute("color",new THREE.Float32BufferAttribute(col,3));
    bunt=new THREE.Mesh(bg, new THREE.MeshBasicMaterial({vertexColors:true, side:THREE.DoubleSide})); C.G.add(bunt);
    const DG=new THREE.Group(); DG.position.set(OX,0,OZ); C.G.add(DG); const pole=new THREE.Mesh(new THREE.CylinderGeometry(.05,.05,1.0,6), C.MC(0xffffff)); pole.position.set(0,2.3,0); DG.add(pole);
    // 계절 소품 — 광장 둘레 (길 위는 피함)
    const ring=(r, n, fn)=>{ for(let k=0;k<n;k++){ const a=k/n*6.283+.35, x=Math.cos(a)*r, z=Math.sin(a)*r; try{ if(ISLE.onPave(x+OX,z+OZ) && Math.hypot(x,z)>C.MAP.plaza.r-.2) continue; }catch(e){} fn(x,z,a,k); } };
    const P_=(geo,c,x,y,z,o)=>{ const m=new THREE.Mesh(geo, C.MC(c)); m.position.set(x,y,z); if(o) m.scale.set(o[0],o[1],o[2]); m.castShadow=true; DG.add(m); return m; };
    if(S==="autumn") ring(PR*.57, 12, (x,z,a,k)=>{ if(k%2) return; P_(new THREE.SphereGeometry(.3,12,8),0xff8a3d,x,.24,z,[1,.75,1]); P_(new THREE.CylinderGeometry(.04,.05,.16,6),0x5a8a3a,x,.5,z); });
    if(S==="winter"){ ring(PR*.57, 12, (x,z,a,k)=>{ if(k%3) return; P_(new THREE.SphereGeometry(.34,12,10),0xffffff,x,.32,z); P_(new THREE.SphereGeometry(.24,12,10),0xffffff,x,.82,z); P_(new THREE.ConeGeometry(.05,.22,6),0xff8a3d,x+Math.cos(a+3.14)*.24,.84,z+Math.sin(a+3.14)*.24).rotation.set(0,0,Math.PI/2); });
      const tx=9.2, tz=-3.8; C.busy.push([tx,tz,2]); [[1.25,1.3,.7],[1.0,1.1,1.5],[.7,.9,2.2]].forEach(([r,h,y])=>P_(new THREE.ConeGeometry(r,h,14),0x2f8f3f,tx,y,tz)); P_(new THREE.CylinderGeometry(.18,.2,.5,8),0x7a4f2c,tx,.25,tz);
      P_(new THREE.OctahedronGeometry(.28),0xffd23f,tx,2.85,tz); C.cols.push([tx+OX,tz+OZ,1.2]);
      for(let i=0;i<14;i++){ const a=i*2.4, r=.5+(i%4)*.18, y=.9+(i%5)*.3, b=new THREE.Mesh(new THREE.SphereGeometry(.08,8,6), new THREE.MeshBasicMaterial({color:C.LIN([0xff6b6b,0xffd23f,0x5aa7ff,0xffffff][i%4])})); b.position.set(tx+Math.cos(a)*r*(1.6-y/2.4), y, tz+Math.sin(a)*r*(1.6-y/2.4)); b.material=C.MC([0xff6b6b,0xffd23f,0x5aa7ff,0xffffff][i%4]); DG.add(b); } }
    if(S==="summer") ring(PR*.59, 12, (x,z,a,k)=>{ if(k%3) return; P_(new THREE.CylinderGeometry(.04,.04,1.8,6),0xffffff,x,.9,z); P_(new THREE.ConeGeometry(.9,.4,12),[0xff6b6b,0x5aa7ff,0xffd23f][k%3],x,1.9,z); });
    if(S==="spring") ring(PR*.58, 12, (x,z,a,k)=>{ if(k%2) return; P_(new THREE.CylinderGeometry(.24,.18,.32,10),0xc9925c,x,.16,z); [0,1,2].forEach(j=>P_(new THREE.SphereGeometry(.1,8,6),[0xff9ac8,0xffffff,0xffd23f][j],x+Math.cos(j*2.1)*.1,.42,z+Math.sin(j*2.1)*.1)); });
    mergeIn(DG);
    // 날리는 것 (여름 = 없음)
    parts=null; if(sea.p){ const n=(typeof LOW!=="undefined" && LOW)?120:240, g=new THREE.BufferGeometry(), a=new Float32Array(n*3); for(let i=0;i<n;i++){ a[i*3]=(Math.random()-.5)*40; a[i*3+1]=Math.random()*14; a[i*3+2]=(Math.random()-.5)*40; } g.setAttribute("position",new THREE.BufferAttribute(a,3));
      const cv=document.createElement("canvas"); cv.width=cv.height=32; const x2=cv.getContext("2d"); x2.fillStyle="#"+new THREE.Color(sea.p).getHexString(); x2.beginPath(); if(S==="winter") x2.arc(16,16,13,0,7); else x2.ellipse(16,16,14,8,.6,0,7); x2.fill();
      const tx=new THREE.CanvasTexture(cv); const m=new THREE.PointsMaterial({size:S==="winter"?.22:.28, map:tx, transparent:true, depthWrite:false, alphaTest:.3}); parts=new THREE.Points(g,m); parts.frustumCulled=false; parts.userData.kind=S; C.G.add(parts); }
    fw=new THREE.Group(); C.G.add(fw); }
  function build(ctx){ C=ctx; Object.keys(SP).forEach(k=>delete SP[k]); FAC.forEach(f=>{ try{ const a=(C.MAP.spots||{})[f.k]; if(!a) return; f.at=a; if(f.k==="goal") goalBoard(f); else building(f); }catch(e){ console.warn("TFAC", f.k, e); } }); try{ decorate(); }catch(e){ console.warn(e); } loadGoal(); try{ if(window.TECO) TECO.build(C); }catch(e){ console.warn(e); } }
  /* 이름표 — 누르면 문 앞까지 걸어가서 열기 */
  function go(S, fn){ const run=()=>{ try{ fn(); tEv("fac_"+S.k); }catch(e){ console.warn(e); } }; const c=[Math.floor(S.door[0]), Math.floor(S.door[1])];
    if(Math.hypot(hero.g.position.x-S.door[0], hero.g.position.z-S.door[1])<2.4 || ISLE.blocked(c[0],c[1])) run(); else walkTo(c[0],c[1],run); }
  const OPEN={bank:()=>TECO.openBank(), goal:()=>openGoal(), post:()=>openPost(), snack:()=>openSnack(), pet:()=>openPet(), museum:()=>openMuseum(), photo:()=>openPhoto(), library:()=>openLib(), station:()=>openStation()};
  function labels(L){ Object.values(SP).forEach(S=>{ let t=S.t; if(S.k==="post" && MAIL.unread) t+=" ✉️"+MAIL.unread; if(S.k==="goal" && GOAL.tot>=GOAL.target) t="🎉 축제 중!";
      L.push({k:"f_"+S.k, ic:S.ic, t, p:S.p, r:3, act:()=>go(S, OPEN[S.k])}); }); try{ if(window.TECO) TECO.labels(L); }catch(e){}
    if(C){ const st=C.MAP.spots.stage, fri=kst().getUTCDay()===5; L.push({k:"f_stage", ic:fri?"🎤":"🎪", t:fri?"금요 퀴즈 쇼!":"무대", p:[st[0]+C.OX,2.6,st[1]+C.OZ], r:3, act:()=>stage()}); } }

  /* ═════════ 📣 마을 목표 · 🎆 축제 · 🎤 금요 퀴즈 쇼 ═════════ */
  const GOAL={tot:0, target:150, by:{}, at:0};
  function myPts(){ const S=study(), n=Object.keys(S.srs||{}).length, tot=(S.days||{}).tot|0, w=wkKey(); let b=store("hyeng_proto_goalb"); if(!b || b.w!==w){ b={w, s:n, d:tot}; store("hyeng_proto_goalb", b); }
    return Math.max(0, n-b.s)+5*Math.max(0, tot-b.d); }
  async function loadGoal(){ const w=wkKey(), mine=myPts(); let kids=1; try{ kids=Math.max(1, Object.keys(ISLE.SRV()||{}).length); }catch(e){}
    GOAL.target=Math.max(150, kids*40); let v=null; try{ v=await NET.get("/hy/isle/goal/"+w); }catch(e){}
    const by=(v&&v.by)||{}; if(mine>0 && (!by[myCode] || (by[myCode].v|0)<mine)){ by[myCode]={n:nick(), v:mine}; try{ await NET.patch("/hy/isle/goal/"+w+"/by/"+myCode, {n:nick(), v:mine}); }catch(e){} }
    GOAL.by=by; GOAL.tot=Object.values(by).reduce((a,o)=>a+(o&&o.v|0),0); if(!v && mine) GOAL.tot=Math.max(GOAL.tot, mine); GOAL.at=Date.now(); drawGoal(); try{ drawLabels(); }catch(e){} }
  function openGoal(){ const fest=GOAL.tot>=GOAL.target, got=store("hyeng_proto_goalc")===wkKey(), L=Object.entries(GOAL.by).filter(([c,o])=>o&&o.v).sort((a,b)=>b[1].v-a[1].v).slice(0,10);
    const d=show("tfGo", hd("📣 이번 주 마을 목표", "월요일마다 새 목표 · 학원 친구 모두 같이")+'<div class="tfCard"><div class="big">'+(fest?"🎆":"📚")+'</div><div class="en">'+GOAL.tot+' / '+GOAL.target+'</div><div class="tfBar"><i style="width:'+Math.min(100,GOAL.tot/GOAL.target*100)+'%"></i></div><div class="ko">'+(fest?'🎉 <b>축제 중!</b> 이번 주 내내 광장에 불꽃놀이':'🎆 '+(GOAL.target-GOAL.tot)+'점 더 모으면 <b>축제</b> — 광장에 불꽃놀이 · 모두 🪙100')+'</div></div>'
      +'<p style="margin:6px 4px;font-size:14px">내 점수 <b>'+myPts()+'</b>점 · 🏫 Daily 30 에서 새 단어 1개 = 1점 · 공부한 날 = 5점</p>'
      +(fest?'<button class="hlBig" data-claim'+(got?' disabled':'')+'>'+(got?'✅ 축제 선물 받았어요':'🎁 축제 선물 🪙100 받기')+'</button>':'')
      +'<div class="hlList">'+(L.length?L.map(([c,o],i)=>'<button><span style="font-size:20px">'+(["🥇","🥈","🥉"][i]||"⭐")+'</span><span>'+esc(o.n||"친구")+(c===myCode?' (나)':'')+'</span><em>'+o.v+'점</em></button>').join(""):'<p style="text-align:center;color:#8a6a4a">아직 아무도 없어요 — 첫 번째가 되어 봐요!</p>')+'</div>');
    d.querySelector(".lb").onclick=e=>{ if(e.target.closest("[data-claim]") && !got){ store("hyeng_proto_goalc", wkKey()); payC(20, "🎉 축제 선물"); try{ emote(hero,"🎉"); }catch(_){} openGoal(); } }; loadGoal().then(()=>{ if($("tfGo").classList.contains("on") && Date.now()-GOAL.at<500){} }); }
  function stage(){ const fri=kst().getUTCDay()===5, done=store("hyeng_proto_fri")===day();
    if(!fri){ toast("🎪 금요일엔 여기서 <b>🎤 퀴즈 쇼</b>가 열려요!<br><small>단어 10문제 · 맞힌 만큼 💎</small>", 2600); return; }
    if(done){ toast("🎤 오늘 퀴즈 쇼는 끝났어요 — 다음 금요일에 또!", 2200); return; }
    ask("🎤 <b>금요 퀴즈 쇼!</b><br>단어 10문제 · 맞힌 만큼 💎<br><small>오늘 한 번</small>", ()=>{ HLIFE.quiz("🎤 금요 퀴즈 쇼", HLIFE.pickWords(10), ok=>{ store("hyeng_proto_fri", day()); try{ hero.act="dance"; hero.actT=0; emote(hero, ok>=8?"🌟":"👏"); }catch(_){} pay(ok, "🎤 "+ok+" / 10"); }); }); }

  /* ═════════ 📮 우체국 ═════════ */
  const SENT=[["You are my best friend!","너는 내 가장 친한 친구야!"],["Let's play together!","같이 놀자!"],["I like your house!","너네 집 멋져!"],["Thank you!","고마워!"],["Good job!","잘했어!"],["See you tomorrow!","내일 봐!"],["Let's go fishing!","낚시하러 가자!"],["Happy birthday!","생일 축하해!"],["You are so cool!","너 정말 멋져!"],["Have a nice day!","좋은 하루 보내!"],["I miss you!","보고 싶어!"],["Come to my house!","우리 집에 놀러 와!"]];
  const STK=["🌟","💖","🌈","🐶","🍦","🎉","🌸","⚽"];
  const NPCM=[["Mia","Welcome to our town!","우리 마을에 온 걸 환영해!","🌸"],["Leo","Let's go fishing!","낚시하러 가자!","🎣"],["Rosa","I made a cake for you!","너를 위해 케이크를 만들었어!","🍰"],["Max","Your house is so cool!","너네 집 정말 멋져!","🔨"]];
  const MAIL={list:[], unread:0, at:0};
  const readSet=()=>store("hyeng_proto_mailr")||[];
  function localMail(){ let L=store("hyeng_proto_mailL"); if(!L){ L=[{id:"npc0", n:"Mia", en:NPCM[0][1], ko:NPCM[0][2], st:"🌸", t:T(), npc:1}]; store("hyeng_proto_mailL", L); } return L; }
  async function loadMail(){ let v=null; try{ v=await NET.get("/hy/isle/mail/"+myCode); }catch(e){}
    const L=Object.entries(v||{}).filter(([id,o])=>o && SENT[o.s]).map(([id,o])=>({id, f:o.f, n:String(o.n||"친구").slice(0,8), en:SENT[o.s][0], ko:SENT[o.s][1], st:STK[o.st]||"💌", g:SNACK.some(s=>s[0]===o.g)?o.g:null, t:+o.t||0}));
    MAIL.list=L.concat(localMail()).sort((a,b)=>b.t-a.t); const R=readSet(); MAIL.unread=MAIL.list.filter(m=>R.indexOf(m.id)<0).length; MAIL.at=Date.now();
    if(L.length>30){ L.slice(30).forEach(m=>{ if(R.indexOf(m.id)>=0) NET.del("/hy/isle/mail/"+myCode+"/"+m.id).catch(()=>{}); }); } try{ drawLabels(); }catch(e){} return MAIL; }
  function openPost(tab){ tab=tab||"in"; const d=show("tfPo", hd("📮 우체국", "영어 편지 · 하루 3통 보내기")+'<div class="tfTabs"><button data-tab="in" class="'+(tab==="in"?"on":"")+'">📬 받은 편지'+(MAIL.unread?" ("+MAIL.unread+")":"")+'</button><button data-tab="out" class="'+(tab==="out"?"on":"")+'">✏️ 편지 쓰기</button></div><div id="tfPoB"><p>불러오는 중…</p></div>');
    d.querySelector(".tfTabs").onclick=e=>{ const b=e.target.closest("[data-tab]"); if(b) openPost(b.dataset.tab); };
    if(tab==="in") loadMail().then(()=>drawInbox()); else writeTo(); }
  function drawInbox(){ const B=$("tfPoB"); if(!B) return; const R=readSet();
    B.innerHTML=MAIL.list.length ? '<div class="hlList">'+MAIL.list.slice(0,30).map(m=>'<button data-m="'+esc(m.id)+'"><span style="font-size:26px">'+(R.indexOf(m.id)<0?"💌":m.st)+'</span><span><b style="font-weight:400">'+esc(m.n)+'</b><br><small style="color:#8a6a4a">'+(R.indexOf(m.id)<0?"새 편지! 눌러서 읽어요":esc(m.en))+'</small></span>'+(m.g?'<em>🎁</em>':'')+'</button>').join("")+'</div>' : '<p style="text-align:center;color:#8a6a4a">아직 편지가 없어요</p>';
    B.onclick=e=>{ const b=e.target.closest("[data-m]"); if(!b) return; const m=MAIL.list.find(x=>x.id===b.dataset.m); if(m) readMail(m); }; }
  function readMail(m){ const R=readSet(), fresh=R.indexOf(m.id)<0; if(fresh){ R.push(m.id); store("hyeng_proto_mailr", R.slice(-80)); MAIL.unread=Math.max(0,MAIL.unread-1); }
    const B=$("tfPoB"); B.innerHTML='<div class="tfCard"><div class="ko">From. <b>'+esc(m.n)+'</b></div><div class="big">'+m.st+'</div><div class="en">'+esc(m.en)+'</div><div class="ko">'+esc(m.ko)+'</div>'+(m.g?'<div style="margin-top:8px;font-size:15px">🎁 선물: '+MAT[m.g].e+' <b>'+esc(m.g)+'</b></div>':'')+'</div><div class="tfRow"><button data-say>🔊 듣기</button><button data-back>📬 목록</button>'+(m.npc?'':'<button data-reply>✏️ 답장</button>')+'</div>';
    try{ say(m.en); }catch(e){}
    if(fresh){ if(m.g){ addMat(m.g,1); saveBag(); toast("🎁 "+MAT[m.g].e+" "+m.g+" → 🎒", 1500); } const D=daily("read"); if(D.n<3){ D.add(); payC(1, "📬 편지 읽기"); } }
    B.onclick=e=>{ if(e.target.closest("[data-say]")) try{ say(m.en); }catch(_){} if(e.target.closest("[data-back]")) drawInbox(); if(e.target.closest("[data-reply]")) writeTo({c:m.f, n:m.n}); }; try{ drawLabels(); }catch(e){} }
  async function friends(){ let S={}; try{ await ISLE.loadLots(); S=ISLE.SRV()||{}; }catch(e){} const me=(()=>{ try{ return ISLE.myKey(); }catch(e){ return ""; } })(), seen={};
    const L=[]; Object.values(S).forEach(v=>{ if(v && v.c && v.k!==me && v.c!==myCode && !seen[v.c]){ seen[v.c]=1; L.push({c:v.c, n:String(v.n||"친구").slice(0,8)}); } }); return L; }
  async function writeTo(to){ const B=$("tfPoB"); if(!B) return; const D=daily("mail"), sentTo=(store("hyeng_proto_mails")||{}); const today=sentTo.d===day()?sentTo.to||[]:[];
    if(D.n>=3){ B.innerHTML='<p style="text-align:center">✉️ 오늘은 3통 다 보냈어요 — 내일 또 써요!</p>'; return; }
    if(!to){ B.innerHTML='<p>누구에게 보낼까요? <small>(오늘 '+(3-D.n)+'통 더)</small></p><div class="hlList" id="tfTo"><p>찾는 중…</p></div>'; const F=await friends();
      const NP=NPCM.map(x=>({c:"npc:"+x[0], n:x[0], npc:1})); const all=F.concat(NP);
      $("tfTo").innerHTML=all.map(f=>'<button data-c="'+esc(f.c)+'" data-n="'+esc(f.n)+'"'+(today.indexOf(f.c)>=0?' disabled style="opacity:.5"':'')+'><span style="font-size:24px">'+(f.npc?"🧑‍🌾":"🏠")+'</span><span>'+esc(f.n)+(f.npc?' <small style="color:#8a6a4a">마을 사람</small>':'')+'</span><em>'+(today.indexOf(f.c)>=0?"오늘 보냄":"✏️")+'</em></button>').join("");
      $("tfTo").onclick=e=>{ const b=e.target.closest("[data-c]"); if(b && !b.disabled) writeTo({c:b.dataset.c, n:b.dataset.n}); }; return; }
    B.innerHTML='<p>✉️ <b>'+esc(to.n)+'</b> 에게 — 무슨 말을 할까요?</p><div class="hlList">'+SENT.map((s,i)=>'<button data-s="'+i+'"><span><b style="font:800 16px var(--en)">'+esc(s[0])+'</b><br><small style="color:#8a6a4a">'+esc(s[1])+'</small></span></button>').join("")+'</div>';
    B.onclick=e=>{ const b=e.target.closest("[data-s]"); if(b) buildSent(to, +b.dataset.s); }; }
  /* 낱말 조각을 순서대로 눌러 문장 만들기 */
  function buildSent(to, si){ const B=$("tfPoB"), words=SENT[si][0].split(" "), tiles=words.map((w,i)=>({w,i})).sort(()=>Math.random()-.5); let k=0;
    const draw=()=>{ B.innerHTML='<p>🧩 낱말을 순서대로 눌러 문장을 만들어요 <small>('+esc(SENT[si][1])+')</small></p><div class="tfAns">'+words.slice(0,k).map(w=>'<span>'+esc(w)+'</span>').join("")+'</div><div class="tfRow">'+tiles.map((t,j)=>t.used?'':'<button data-t="'+j+'">'+esc(t.w)+'</button>').join("")+'</div><div class="tfRow"><button data-say style="font-size:15px">🔊 문장 듣기</button></div>'; };
    draw(); try{ say(SENT[si][0]); }catch(e){}
    B.onclick=e=>{ if(e.target.closest("[data-say]")){ try{ say(SENT[si][0]); }catch(_){} return; } const b=e.target.closest("[data-t]"); if(!b) return; const t=tiles[+b.dataset.t];
      if(t.w===words[k]){ t.used=1; k++; try{ SND.pop(); }catch(_){} if(k>=words.length){ try{ say(SENT[si][0]); SND.win(); }catch(_){} setTimeout(()=>pickStk(to, si), 700); } draw(); }
      else { b.classList.add("w"); try{ SND.snap(); }catch(_){} setTimeout(()=>b.classList.remove("w"),400); } }; }
  function pickStk(to, si){ const B=$("tfPoB"); let stk=0, gift=null; const have=SNACK.filter(s=>(mats[s[0]]|0)>0);
    const draw=()=>{ B.innerHTML='<div class="tfCard"><div class="big">'+STK[stk]+'</div><div class="en">'+esc(SENT[si][0])+'</div><div class="ko">To. '+esc(to.n)+'</div></div><p style="margin:4px">스티커</p><div class="tfRow">'+STK.map((s,i)=>'<button data-st="'+i+'" class="'+(i===stk?"sel":"")+'" style="font-size:24px">'+s+'</button>').join("")+'</div>'
      +(have.length?'<p style="margin:4px">🎁 간식 같이 보내기 (골라도 되고 안 골라도 돼요)</p><div class="tfRow">'+have.map(s=>'<button data-g="'+esc(s[0])+'" class="'+(gift===s[0]?"sel":"")+'" style="font-size:22px">'+s[1]+'</button>').join("")+'</div>':'')+'<button class="hlBig" data-send>📮 보내기</button>'; };
    draw(); B.onclick=e=>{ const s=e.target.closest("[data-st]"); if(s){ stk=+s.dataset.st; draw(); return; } const g=e.target.closest("[data-g]"); if(g){ gift=gift===g.dataset.g?null:g.dataset.g; draw(); return; } if(e.target.closest("[data-send]")) send(to, si, stk, gift); }; }
  async function send(to, si, stk, gift){ const B=$("tfPoB"); B.innerHTML='<p style="text-align:center">📮 보내는 중…</p>'; const t=T();
    if(gift && (mats[gift]|0)<1) gift=null; let ok=true;
    if(to.c.startsWith("npc:")){ const N=NPCM.find(x=>"npc:"+x[0]===to.c)||NPCM[0]; const L=localMail(); L.push({id:"npc"+t, n:N[0], en:N[1]==="Welcome to our town!"?"Thank you for your letter!":N[1], ko:N[1]==="Welcome to our town!"?"편지 고마워!":N[2], st:N[3], t:t+60e3, npc:1}); store("hyeng_proto_mailL", L.slice(-20)); }
    else { try{ await NET.put("/hy/isle/mail/"+to.c+"/m"+t+"_"+myCode, {f:myCode, n:nick(), s:si, st:stk, g:gift||null, t}); }catch(e){ ok=false; } }
    if(!ok){ B.innerHTML='<p style="text-align:center">📡 인터넷이 잠깐 안 돼요 — 다시 해 봐요</p>'; return; }
    if(gift) addMat(gift,-1); const D=daily("mail"); D.add(); let S=store("hyeng_proto_mails")||{}; if(S.d!==day()) S={d:day(), to:[]}; S.to.push(to.c); store("hyeng_proto_mails", S);
    try{ tEv("mail"); }catch(e){} B.innerHTML='<div class="tfCard"><div class="big">📮✨</div><div class="en">Sent!</div><div class="ko"><b>'+esc(to.n)+'</b> 에게 편지를 보냈어요'+(to.c.startsWith("npc:")?' — 곧 답장이 와요':'')+'</div></div>'; payC(1, "✉️ 편지"); if(to.c.startsWith("npc:")) loadMail(); }

  /* ═════════ 🍦 간식 가게 + 🍗 배부름 ═════════ */
  let FULL=store("hyeng_proto_full")||{h:5, t:T()};
  const full=()=>Math.max(0, Math.min(5, FULL.h-(T()-FULL.t)/(2*3600e3)));   /* 2시간에 하트 1개 */
  function spd(){ const h=full(); return h>=4.5?1.15 : h<=.01?.8 : 1; }
  const foodV=n=>{ const s=SNACK.find(x=>x[0]===n); if(s) return s[3]; return MAT[n] && MAT[n].food ? (/pizza|cake|stew|pie/.test(n)?3:2) : 0; };
  function eat(n){ const v=foodV(n); if(!v || (mats[n]|0)<1) return false; addMat(n,-1); saveBag(); FULL={h:Math.min(5, full()+v), t:T()}; store("hyeng_proto_full", FULL);
    try{ say(n); emote(hero,"😋"); SND.pop(); tEv("eat"); }catch(e){} toast("😋 냠냠! "+MAT[n].e+" "+n+" · 🍗 +"+v+(full()>=4.5?"<br><small>⚡ 배불러서 빨리 달려요!</small>":""), 1800); updPill(); return true; }
  function openSnack(){ const d=show("tfSn", hd("🍦 간식 가게", "영어로 주문해요 · 🪙 <b>"+TECO.coins()+"</b>")+'<div class="tfCard" style="text-align:left;display:flex;gap:10px;align-items:center"><span style="font-size:40px">🧑‍🍳</span><span><b style="font:800 18px var(--en)">"What would you like?"</b><br><small>먹고 싶은 걸 눌러요 — 영어 이름을 맞히면 주문 끝!</small></span></div>'
      +'<div class="hlList">'+SNACK.map(([n,e,p,h])=>'<button data-sn="'+esc(n)+'"><span style="font-size:30px">'+e+'</span><span><b style="font:800 16px var(--en)">'+esc(n)+'</b><br><small style="color:#8a6a4a">🍗 +'+h+' · 가방에 '+(mats[n]|0)+'</small></span><em>🪙 '+(p*5)+'</em></button>').join("")+'</div>'
      +'<p style="font-size:13px;color:#8a6a4a;margin:6px 4px">🍗 배부름 '+heartTxt()+' · 배부르면 ⚡ 빨리 달리고, 배고프면 느려져요 · 🍳 요리한 음식도 먹을 수 있어요</p>');
    try{ say("What would you like"); }catch(e){}
    d.querySelector(".lb").onclick=e=>{ const b=e.target.closest("[data-sn]"); if(!b) return; const S=SNACK.find(x=>x[0]===b.dataset.sn); if(TECO.coins()<S[2]*5){ TECO.pay2({g:0,c:S[2]*5}); return; } close("tfSn");   /* (v563) 간식 = 🪙 */
      pick1("🍦 주문하기", S[1], S[0], SNACK.map(x=>x[0]), r=>{ if(!TECO.pay2({g:0,c:S[2]*5})) return; addMat(S[0],1); saveBag(); try{ say("Here you are"); }catch(_){} toast("🧑‍🍳 \"Here you are!\" "+S[1]+" → 🎒", 1700); openSnack(); }, {ask:'🧑‍🍳 "What would you like?"<br><small>이 간식은 영어로?</small>', n:3, retry:1}); }; }
  const heartTxt=()=>{ const h=Math.round(full()); return "❤️".repeat(h)+"🤍".repeat(5-h); };
  function openMe(){ const P=PET(), foods=Object.keys(mats).filter(n=>(mats[n]|0)>0 && foodV(n));
    const d=show("tfMe", hd("🍗 배부름 · 🐾 내 펫", "")+'<div class="tfCard"><div style="font-size:28px">'+heartTxt()+'</div><div class="ko">'+(full()>=4.5?"⚡ 배불러요! 마을에서 더 빨리 달려요":full()<=.01?"😵 배고파요… 느려졌어요 — 뭐라도 먹어요":"🙂 괜찮아요 · 2시간마다 하트 1개씩 줄어요")+'</div></div>'
      +(foods.length?'<p style="margin:4px">🍽 먹기</p><div class="tfRow">'+foods.map(n=>'<button data-eat="'+esc(n)+'" style="font-size:15px">'+MAT[n].e+' '+esc(n)+' ×'+mats[n]+'</button>').join("")+'</div>':'<p style="text-align:center;color:#8a6a4a">가방에 먹을 게 없어요 — 🍦 간식 가게 · 🍳 요리</p>')
      +(P?petCard(P):'<p style="text-align:center;color:#8a6a4a;margin-top:10px">🐶 마을 <b>펫 가게</b>에서 같이 다닐 친구를 만나요</p>'));
    d.querySelector(".lb").onclick=e=>{ const b=e.target.closest("[data-eat]"); if(b){ eat(b.dataset.eat); openMe(); return; } petClick(e, openMe); }; }
  function updPill(){ const h=Math.round(full()), P=PET(), txt=(P?PETS_BY[P.t].ic:"🍗")+" "+h; ["hFull","ihFull"].forEach(id=>{ const el=$(id); if(el && el.dataset.v!==txt){ el.dataset.v=txt; el.querySelector("b").textContent=h; el.querySelector("i").textContent=P?PETS_BY[P.t].ic:"🍗"; el.classList.toggle("low", h<=1); } }); }

  /* ═════════ 🐶 펫 ═════════ */
  /* (v559) 💰 펫 값 = 가구점 물가(ECON): 20·30·30·40·60·80 → 145·205·205·265·385·505 */
  const PETS=[{k:"chick",ic:"🐥",nm:"병아리",p:230,c:[0xffd23f,0xff9a3d]},{k:"dog",ic:"🐶",nm:"강아지",p:330,c:[0xd9a066,0x8a5a34]},{k:"cat",ic:"🐱",nm:"고양이",p:330,c:[0xf2a65a,0xffffff]},{k:"bunny",ic:"🐰",nm:"토끼",p:425,c:[0xffffff,0xffb6c8]},{k:"fox",ic:"🦊",nm:"여우",p:615,c:[0xff8a3d,0xffffff]},{k:"panda",ic:"🐼",nm:"판다",p:810,c:[0xffffff,0x2b2b2b]}];
  const PETS_BY={}; PETS.forEach(p=>PETS_BY[p.k]=p);
  const PNAME=["Coco","Lucky","Mimi","Bori","Choco","Momo","Toby","Lulu"];
  const TRICK=[["sit","🧘","앉아"],["jump","⬆️","점프"],["spin","🌀","빙글빙글"],["shake","🤝","악수"],["roll","🔄","데굴데굴"],["dance","💃","춤"]];
  const PET=()=>{ const p=store("hyeng_proto_pet"); return p && PETS_BY[p.t] ? p : null; };
  const happy=P=>Math.max(0, Math.min(5, (P.h==null?3:P.h)-Math.floor((T()-(P.fed||T()))/864e5)));
  function petMesh(t){ const P=PETS_BY[t]||PETS[1], g=new THREE.Group(), [a,b]=P.c, mA=M(a), mB=M(b), dk=M(0x2b1d1d), pk=M(0xffb6c8), B=new THREE.Group(); g.add(B);
    const S=(r,m,x,y,z,s)=>{ const o=new THREE.Mesh(new THREE.SphereGeometry(r,14,10),m); o.position.set(x,y,z); if(s) o.scale.set(s[0],s[1],s[2]); o.castShadow=true; B.add(o); return o; };
    const Cy=(r1,r2,h,m,x,y,z,rx,rz)=>{ const o=new THREE.Mesh(new THREE.CylinderGeometry(r1,r2,h,8),m); o.position.set(x,y,z); o.rotation.set(rx||0,0,rz||0); o.castShadow=true; B.add(o); return o; };
    const Co=(r,h,m,x,y,z,rx,rz)=>{ const o=new THREE.Mesh(new THREE.ConeGeometry(r,h,8),m); o.position.set(x,y,z); o.rotation.set(rx||0,0,rz||0); B.add(o); return o; };
    if(t==="chick"){ S(.24,mA,0,.26,0,[1,.95,1]); S(.17,mA,0,.52,.08); Co(.05,.12,mB,0,.5,.26,Math.PI/2); [-1,1].forEach(s=>{ S(.03,dk,s*.07,.56,.22); S(.09,mA,s*.22,.28,0,[.5,1,1.2]); Cy(.02,.02,.12,mB,s*.08,.06,0); }); }
    else { S(.22,mA,0,.32,0,[1,.9,1.35]); S(.2,t==="panda"?mA:mA,0,.58,.22);
      [-1,1].forEach(s=>{ S(.032,dk,s*.075,.62,.39); if(t==="panda") S(.06,mB,s*.075,.62,.37,[1,1.2,.5]); [-1,1].forEach(f=>Cy(.055,.05,.2,t==="panda"?mB:mA,s*.12,.1,f*.16));
        if(t==="dog") S(.08,mB,s*.17,.62,.18,[.6,1.4,.8]); else if(t==="bunny"){ const e=Cy(.05,.06,.34,mA,s*.08,.88,.18); e.rotation.z=s*.12; S(.03,pk,s*.08,.9,.22,[1,3,.5]); } else if(t==="panda") S(.07,mB,s*.13,.76,.2); else { Co(.08,.16,mA,s*.11,.8,.2,0,s*-.25); } });
      S(.035,dk,0,.56,.42); if(t==="cat"||t==="fox") [-1,1].forEach(s=>S(.02,mB,s*.05,.53,.4)); if(t==="fox"||t==="cat") S(.09,mB,0,.52,.32,[1.2,.8,1]);
      if(t==="dog") Cy(.035,.025,.26,mA,0,.45,-.32,-.7); else if(t==="cat") Cy(.03,.025,.42,mA,0,.52,-.36,-.4); else if(t==="fox"){ S(.12,mA,0,.38,-.4,[.8,.8,1.6]); S(.06,mB,0,.38,-.6); } else if(t==="bunny"||t==="panda") S(.07,t==="panda"?mB:mA,0,.36,-.3); }
    g.userData.body=B; return g; }
  let petObj=null, petT0="", petAnim=null, visPet=null, visKey="";
  function petSync(){ const P=PET(), key=P?P.t:""; if(key===petT0) return; petT0=key; if(petObj){ scene.remove(petObj); petObj=null; } if(P){ petObj=petMesh(P.t); petObj.position.copy(hero.g.position); scene.add(petObj); try{ TOON.scan(petObj); }catch(e){} } }
  function trick(k){ if(!petObj) return; petAnim={k, t:0}; try{ say(k); }catch(e){} }
  function petTick(dt){ if(!petObj || !hero) return false; const hide=(typeof TW!=="undefined" && TW.on) || place===PL.visit || place===PL.yvisit; petObj.visible=!hide; if(hide) return false;
    const hp=hero.g.position, f=hero.face||0, tx=hp.x-Math.sin(f)*.85+Math.cos(f)*.45, tz=hp.z-Math.cos(f)*.85-Math.sin(f)*.45, p=petObj.position, dx=tx-p.x, dz=tz-p.z, d=Math.hypot(dx,dz);
    if(d>6){ p.set(tx,0,tz); } let mv=false; if(d>.12){ const k=Math.min(1, dt*(d>1.5?6:3.5)); p.x+=dx*k; p.z+=dz*k; petObj.rotation.y=Math.atan2(dx,dz); mv=true; } else if(Math.abs(petObj.rotation.y-f)>.01){ petObj.rotation.y+=(f-petObj.rotation.y)*Math.min(1,dt*4); }
    const B=petObj.userData.body, tm=performance.now()/1000; B.position.y=0; B.rotation.set(0,0,0); B.scale.set(1,1,1);
    if(petAnim){ petAnim.t+=dt; const t=petAnim.t, k=petAnim.k; if(k==="jump") B.position.y=Math.max(0,Math.sin(t*Math.PI/0.6))*.6*(t<1.2?1:0); else if(k==="spin") B.rotation.y=t*9; else if(k==="sit"){ B.scale.set(1,.8,1); B.rotation.x=-.35; } else if(k==="shake") B.rotation.z=Math.sin(t*14)*.25; else if(k==="roll") B.rotation.z=t*8; else if(k==="dance"){ B.rotation.y=Math.sin(t*8)*.6; B.position.y=Math.abs(Math.sin(t*8))*.15; } else if(k==="happy") B.position.y=Math.abs(Math.sin(t*10))*.2;
      if(t>1.4) petAnim=null; return true; }
    if(mv) B.position.y=Math.abs(Math.sin(tm*12))*.08; else B.scale.y=1+Math.sin(tm*3)*.02; return true; }
  function visTick(dt){ const v=(place===PL.visit && visiting && visiting.data && visiting.data.pet && PETS_BY[visiting.data.pet.t]) ? visiting.data.pet : null, key=v?visiting.code+v.t:"";
    if(key!==visKey){ visKey=key; if(visPet){ scene.remove(visPet); visPet=null; } if(v){ visPet=petMesh(v.t); visPet.position.set(RN/2-.5,0,RN/2+.5); scene.add(visPet); } }
    if(visPet){ const tm=performance.now()/1000; visPet.rotation.y=Math.sin(tm*.6)*1.2; visPet.userData.body.position.y=Math.abs(Math.sin(tm*2.5))*.05; return true; } return false; }
  function petCard(P){ const H=happy(P), next=TRICK.find(t=>(P.tr||[]).indexOf(t[0])<0), today=P.ld===day();
    return '<div class="tfCard"><div class="big">'+PETS_BY[P.t].ic+'</div><div class="en">'+esc(P.n)+'</div><div class="ko">기분 '+"💛".repeat(H)+"🤍".repeat(5-H)+' · 하루 밥을 안 주면 하나씩 줄어요</div></div>'
      +'<div class="tfRow"><button data-feed style="font-size:15px">🦴 밥 주기 ('+(mats["pet food"]|0)+')</button><button data-learn style="font-size:15px"'+(!next||today?' disabled':'')+'>🎓 '+(next?(today?"재주는 내일 또":"재주 배우기"):"재주 다 배웠어요")+'</button></div>'
      +((P.tr||[]).length?'<p style="margin:4px">🎾 같이 놀기 — 영어로 말해요</p><div class="tfRow">'+(P.tr||[]).map(k=>'<button data-tr="'+k+'">'+k[0].toUpperCase()+k.slice(1)+'!</button>').join("")+'</div>':''); }
  function petClick(e, re){ const P=PET(); if(!P) return; if(e.target.closest("[data-feed]")){ if((mats["pet food"]|0)<1){ toast("🦴 펫 밥이 없어요 — 🐶 펫 가게에서 사요", 1800); return; } addMat("pet food",-1); saveBag(); P.h=Math.min(5, happy(P)+2); P.fed=T(); store("hyeng_proto_pet", P); trick("happy"); try{ emote(hero,"💖"); SND.pop(); }catch(_){} toast("🦴 냠냠! "+esc(P.n)+" 기분 최고", 1500); re(); return; }
    const tr=e.target.closest("[data-tr]"); if(tr){ const k=tr.dataset.tr; close("tfMe"); close("tfPt"); trick(k); toast("🗣 \""+k[0].toUpperCase()+k.slice(1)+"!\"", 1200); return; }
    if(e.target.closest("[data-learn]")){ const next=TRICK.find(t=>(P.tr||[]).indexOf(t[0])<0); if(!next || P.ld===day()) return; if(happy(P)<2){ toast("😢 "+esc(P.n)+" 기분이 안 좋아요 — 🦴 밥부터 줘요", 1800); return; }
      close("tfMe"); close("tfPt"); let q=$("hqP"); if(!q){ HLIFE.quiz("", [], ()=>{}); q=$("hqP"); } const box=q.querySelector(".b"), opts=TRICK.slice().sort(()=>Math.random()-.5).slice(0,4); if(opts.indexOf(next)<0) opts[0]=next; opts.sort(()=>Math.random()-.5);
      box.innerHTML='<div class="t">🎓 재주 배우기</div><div class="e">'+PETS_BY[P.t].ic+'</div><div class="k"><b style="font:800 22px var(--en)">"'+next[0][0].toUpperCase()+next[0].slice(1)+'!"</b><br><small>잘 듣고 맞는 그림을 눌러요</small></div><div class="o em">'+opts.map(o=>'<button data-w="'+o[0]+'">'+o[1]+'</button>').join("")+'</div><button class="sb" data-again>🔊 다시 듣기</button>';
      try{ say(next[0]); }catch(_){} q.classList.add("on");
      box.onclick=ev=>{ if(ev.target.closest("[data-again]")){ try{ say(next[0]); }catch(_){} return; } const b=ev.target.closest("[data-w]"); if(!b || box.dataset.lock) return;
        if(b.dataset.w===next[0]){ box.dataset.lock=1; b.classList.add("r"); P.tr=(P.tr||[]).concat(next[0]); P.ld=day(); store("hyeng_proto_pet", P); setTimeout(()=>{ delete box.dataset.lock; q.classList.remove("on"); trick(next[0]); pay(2, "🎓 "+esc(P.n)+" 이(가) "+next[2]+"를 배웠어요"); }, 700); try{ SND.win(); }catch(_){} }
        else { b.classList.add("w"); try{ SND.snap(); say(next[0]); }catch(_){} setTimeout(()=>b.classList.remove("w"),500); } }; } }
  function openPet(){ const P=PET();
    let h=hd("🐶 펫 가게", "나를 따라다니는 친구 · 💎 <b>"+gems+"</b> · 🪙 <b>"+TECO.coins()+"</b>")+'<div class="hlList"><button data-food><span style="font-size:28px">🦴</span><span><b style="font:800 16px var(--en)">pet food</b><br><small style="color:#8a6a4a">펫 밥 · 가방에 '+(mats["pet food"]|0)+'</small></span><em>🪙 10</em></button></div>';
    if(P) h+=petCard(P);
    h+='<p style="margin:8px 4px 4px">'+(P?'🔁 다른 친구로 바꾸기 (재주는 그대로)':'🐾 같이 다닐 친구를 골라요')+'</p><div class="tfGrid">'+PETS.map(p=>'<button data-buy="'+p.k+'"'+(P&&P.t===p.k?' class="no"':'')+'><i>'+p.ic+'</i><span>'+p.nm+'</span><b>💎 '+p.p+'</b></button>').join("")+'</div>';
    const d=show("tfPt", h);
    d.querySelector(".lb").onclick=e=>{ if(e.target.closest("[data-food]")){ if(!TECO.pay2({g:0,c:10})) return; addMat("pet food",1); saveBag(); try{ say("pet food"); SND.pop(); }catch(_){} openPet(); return; }
      const b=e.target.closest("[data-buy]"); if(b){ const p=PETS_BY[b.dataset.buy]; if(P && P.t===p.k) return; ask(p.ic+" <b>"+p.nm+"</b> 를 데려갈까요? (💎 "+p.p+")", ()=>{ if(!spend(p.p)) return; const old=PET(); if(old){ old.t=p.k; store("hyeng_proto_pet", old); petSync(); trick("happy"); openPet(); return; } pickName(p); }); return; }
      petClick(e, openPet); }; }
  function pickName(p){ const d=show("tfPt", hd("🐾 이름 지어 주기", p.ic+" "+p.nm)+'<div class="tfRow">'+PNAME.map(n=>'<button data-nm="'+n+'">'+n+'</button>').join("")+'</div>');
    d.querySelector(".lb").onclick=e=>{ const b=e.target.closest("[data-nm]"); if(!b) return; store("hyeng_proto_pet", {t:p.k, n:b.dataset.nm, h:4, fed:T(), tr:[]}); addMat("pet food",2); saveBag(); petSync(); trick("happy"); try{ say(b.dataset.nm); SND.big(); tEv("pet"); emote(hero,"💖"); }catch(_){} close("tfPt");
      toast(p.ic+" <b>"+b.dataset.nm+"</b> 이(가) 나를 따라와요!<br><small>🦴 밥 2개 선물 · 오른쪽 위 "+p.ic+" 단추로 돌봐요</small>", 3000); updPill(); }; }

  /* ═════════ 🏛 박물관 ═════════ */
  const MUSC=()=>[["fish","🐟 물고기", FISH.filter(f=>!(SPEC[f.en]||{}).junk).map(f=>[f.en,f.e])], ["ore","⛏ 광물", ["coal","iron","silver","gold","diamond"].map(n=>[n,MAT[n].e])], ["crop","🌾 작물", ["wheat","carrot","potato","tomato","corn","strawberry","pumpkin","watermelon"].map(n=>[n,MAT[n].e])], ["food","🍳 요리", Object.keys(MAT).filter(n=>MAT[n].food && !SNACK.some(s=>s[0]===n)).map(n=>[n,MAT[n].e])]];
  const mkey=n=>n.replace(/[^a-z0-9]+/gi,"_");
  let MUS={}, musTab="fish";
  const hasIt=(cat,n)=>cat==="fish" ? bag.some(it=>it.en===n) : (mats[n]|0)>0;
  async function loadMus(){ let v=null; try{ v=await NET.get("/hy/isle/museum"); }catch(e){} MUS=Object.assign({}, store("hyeng_proto_mus")||{}, v||{}); return MUS; }
  function openMuseum(){ show("tfMu", hd("🏛 마을 박물관", "기증하면 마을 모두가 봐요 · 내 이름이 남아요")+'<p>불러오는 중…</p>'); loadMus().then(drawMus); }
  function drawMus(){ const d=$("tfMu"); if(!d || !d.classList.contains("on")) return; const CAT=MUSC(), all=CAT.reduce((a,c)=>a+c[2].length,0), got=CAT.reduce((a,c)=>a+c[2].filter(x=>MUS[mkey(x[0])]).length,0), cur=CAT.find(c=>c[0]===musTab)||CAT[0];
    d.querySelector(".lb").innerHTML=hd("🏛 마을 박물관", "기증하면 마을 모두가 봐요 · 내 이름이 남아요")+'<div class="tfBar"><i style="width:'+(got/all*100)+'%"></i></div><p style="margin:0 4px 6px;font-size:14px">마을 전시 <b>'+got+' / '+all+'</b> · 기증하면 🪙25</p>'
      +'<div class="tfTabs">'+CAT.map(c=>'<button data-mt="'+c[0]+'" class="'+(c[0]===cur[0]?"on":"")+'">'+c[1]+' '+c[2].filter(x=>MUS[mkey(x[0])]).length+'/'+c[2].length+'</button>').join("")+'</div>'
      +'<div class="tfGrid">'+cur[2].map(([n,e])=>{ const m=MUS[mkey(n)]; if(m) return '<button data-sy="'+esc(n)+'"><i>'+e+'</i><b>'+esc(n)+'</b><span>🏷 '+esc(String(m.n||"친구").slice(0,8))+'</span></button>'; const can=hasIt(cur[0],n); return '<button data-dn="'+esc(n)+'" class="'+(can?"can":"no")+'"><i>'+(can?e:"❔")+'</i><span>'+(can?"🎁 기증하기":"아직 없어요")+'</span></button>'; }).join("")+'</div>';
    d.querySelector(".lb").onclick=e=>{ const t=e.target.closest("[data-mt]"); if(t){ musTab=t.dataset.mt; drawMus(); return; } const s=e.target.closest("[data-sy]"); if(s){ try{ say(s.dataset.sy); }catch(_){} return; }
      const b=e.target.closest("[data-dn]"); if(b && b.classList.contains("can")) donate(cur, b.dataset.dn); }; }
  function donate(cat, n){ const e=cat[2].find(x=>x[0]===n)[1]; close("tfMu");
    pick1("🏛 기증하기 — 이름표 붙이기", e, n, cat[2].map(x=>x[0]), async r=>{ if(!r){ toast("🏷 이름표가 틀렸어요 — 다시 해 봐요<br><b>"+e+" = "+esc(n)+"</b>", 2200); openMuseum(); return; }
      let ex=null; try{ ex=await NET.get("/hy/isle/museum/"+mkey(n)); }catch(_){} if(ex){ MUS[mkey(n)]=ex; toast("😮 방금 "+esc(ex.n||"친구")+" 이(가) 먼저 기증했어요!", 2000); openMuseum(); return; }
      if(!hasIt(cat[0],n)){ openMuseum(); return; }
      if(cat[0]==="fish"){ const i=bag.findIndex(it=>it.en===n); bag.splice(i,1); } else addMat(n,-1); saveBag();
      const rec={c:myCode, n:nick(), t:T()}; MUS[mkey(n)]=rec; const L=store("hyeng_proto_mus")||{}; L[mkey(n)]=rec; store("hyeng_proto_mus", L); try{ await NET.put("/hy/isle/museum/"+mkey(n), rec); }catch(_){}
      try{ tEv("museum"); emote(hero,"🏛"); }catch(_){} { const Dm=daily("mus"); if(Dm.n<2){ Dm.add(); payC(5, "🏛 "+e+" "+n+" 기증"); } else toast("🏛 "+e+" "+n+" 기증! 🏷 내 이름이 붙었어요<br><small>기증 💎 는 하루 두 번까지</small>", 2200); } openMuseum(); }   /* (v561) QA: 마트에서 사서 기증하면 하루 💎110 — 하루 💎10 까지 */, {ask:"🏷 이 전시물의 영어 이름은?"}); }

  /* ═════════ 📸 사진관 ═════════ */
  const BGS=[["rainbow","🌈",["#ffd6e8","#d6ebff","#d8f5cc"],"🌈⭐"],["beach","🏖",["#8fd3f0","#cfeffc","#ffe8a8"],"🐚🌊"],["space","🚀",["#1d1b4a","#3b2f7a","#6a4bb0"],"⭐🪐"],["flower","🌸",["#ffe0ef","#fff3c4","#d8f5cc"],"🌸🌼"],["castle","🏰",["#e6dcff","#fff3e0","#ffd0d0"],"👑✨"]];
  const CAPS=["Best day ever!","Hello, friends!","I love my town!","Me and my pet!","Happy Halloween!","Merry Christmas!","Cheese!"];
  const POSES=[["yay","🙌"],["wave","👋"],["dance","💃"],["idle","🙂"]];
  const album=()=>store("hyeng_proto_album")||[];
  let ph={bg:0, cap:0, pose:0};
  function openPhoto(){ const A=album(); const d=show("tfPh", hd("📸 사진관", "배경·포즈·영어 한 줄 → 찰칵! · 🖼 액자로 방에 걸어요")
      +'<p style="margin:2px 4px">배경</p><div class="tfRow">'+BGS.map((b,i)=>'<button data-bg="'+i+'" class="'+(ph.bg===i?"sel":"")+'" style="font-size:24px">'+b[1]+'</button>').join("")+'</div>'
      +'<p style="margin:2px 4px">포즈</p><div class="tfRow">'+POSES.map((p,i)=>'<button data-po="'+i+'" class="'+(ph.pose===i?"sel":"")+'" style="font-size:24px">'+p[1]+'</button>').join("")+'</div>'
      +'<p style="margin:2px 4px">영어 한 줄</p><div class="tfRow">'+CAPS.map((c,i)=>'<button data-cp="'+i+'" class="'+(ph.cap===i?"sel":"")+'" style="font-size:14px">'+c+'</button>').join("")+'</div>'
      +'<button class="hlBig" data-shoot>📸 찰칵! (🪙 10)</button>'+(A.length?'<p style="margin:6px 4px">📒 내 앨범 '+A.length+' / 6</p><div class="tfRow">'+A.map((a,i)=>'<img src="'+a.d+'" alt="" style="width:76px;border-radius:8px;border:2.5px solid #3b2433">').join("")+'</div>':''));
    d.querySelector(".lb").onclick=e=>{ const g=(k,a)=>{ const b=e.target.closest("["+a+"]"); if(b){ ph[k]=+b.getAttribute(a); if(k==="cap") try{ say(CAPS[ph.cap]); }catch(_){} openPhoto(); return true; } }; if(g("bg","data-bg")||g("pose","data-po")||g("cap","data-cp")) return;
      if(e.target.closest("[data-shoot]")){ if(!TECO.pay2({g:0,c:10})) return; let url=""; try{ url=shoot(); }catch(err){ console.warn(err); } if(!url){ toast("📸 사진을 못 찍었어요", 1500); return; }
        const A2=album(); A2.unshift({d:url, t:T()}); store("hyeng_proto_album", A2.slice(0,6)); addStock("photo"); try{ SND.big(); tEv("photo"); say(CAPS[ph.cap]); }catch(_){}
        show("tfPh", hd("📸 찰칵!", "🖼 액자 1개 → 🏠 창고 · 집 🛋️ 가구에서 벽에 걸어요")+'<div style="text-align:center"><img src="'+url+'" alt="" style="width:min(240px,70vw);border-radius:12px;border:3px solid #3b2433;box-shadow:0 4px 0 #3b2433"></div><button class="hlBig" data-again>📸 또 찍기</button>');
        $("tfPh").querySelector(".lb").onclick=ev=>{ if(ev.target.closest("[data-again]")) openPhoto(); }; } }; }
  /* 따로 작은 장면에 내 캐릭터(+펫)를 세워 찍음 → 배경·액자·글자 */
  function shoot(){ const Wd=256, Ht=320, S=new THREE.Scene(); S.add(new THREE.HemisphereLight(0xffffff,0xb8a890,1.05)); const dl=new THREE.DirectionalLight(0xffffff,.75); dl.position.set(2,4,5); S.add(dl);
    const A=buildAvatar(av), pose=POSES[ph.pose][0]; S.add(A.g); try{ const r=(o,x,z)=>{ if(o){ o.rotation.x=x; if(z!=null) o.rotation.z=z; } }; if(pose==="yay"){ r(A.armL,-2.8); r(A.armR,-2.8); A.setExpr && A.setExpr("grin"); } else if(pose==="wave"){ r(A.armR,-2.6,-.2); A.setExpr && A.setExpr("smile"); } else if(pose==="dance"){ r(A.armL,-1.3); r(A.armR,-2.5); if(A.body) A.body.rotation.z=.14; r(A.legL,.35); A.setExpr && A.setExpr("wink"); } }catch(e){}
    const P=PET(); if(P){ const pm=petMesh(P.t); pm.position.set(.55,0,.25); pm.rotation.y=-.5; S.add(pm); }
    const bb=new THREE.Box3().setFromObject(S), hgt=bb.max.y-bb.min.y||1.4, cy=bb.min.y+hgt*.5, cam=new THREE.PerspectiveCamera(30, Wd/Ht, .1, 50); cam.position.set(P?.25:0, cy+.1, hgt*2.25+.8); cam.lookAt(P?.25:0, cy, 0);
    const RT=new THREE.WebGLRenderTarget(Wd,Ht), old=renderer.getClearColor(new THREE.Color()), oa=renderer.getClearAlpha(); renderer.setRenderTarget(RT); renderer.setClearColor(0x000000,0); renderer.clear(); renderer.render(S,cam);
    const px=new Uint8Array(Wd*Ht*4); renderer.readRenderTargetPixels(RT,0,0,Wd,Ht,px); renderer.setRenderTarget(null); renderer.setClearColor(old,oa); RT.dispose(); try{ dirty=true; }catch(e){}
    const cv=document.createElement("canvas"); cv.width=Wd; cv.height=Ht; const g=cv.getContext("2d"), bg=BGS[ph.bg], gr=g.createLinearGradient(0,0,0,Ht); bg[2].forEach((c,i)=>gr.addColorStop(i/(bg[2].length-1),c)); g.fillStyle=gr; g.fillRect(0,0,Wd,Ht);
    g.font="26px sans-serif"; g.globalAlpha=.55; for(let i=0;i<9;i++) g.fillText([...bg[3]][i%2], 14+(i*67)%230, 30+(i*97)%200); g.globalAlpha=1;
    const im=g.createImageData(Wd,Ht), gm=v=>Math.round(255*Math.pow(v/255,1/2.2)); for(let y=0;y<Ht;y++) for(let x=0;x<Wd;x++){ const s=((Ht-1-y)*Wd+x)*4, t=(y*Wd+x)*4; im.data[t]=gm(px[s]); im.data[t+1]=gm(px[s+1]); im.data[t+2]=gm(px[s+2]); im.data[t+3]=px[s+3]; }
    const tc=document.createElement("canvas"); tc.width=Wd; tc.height=Ht; tc.getContext("2d").putImageData(im,0,0); g.drawImage(tc,0,-10);
    g.fillStyle="#fffdf7"; g.fillRect(0,Ht-56,Wd,56); g.fillStyle="#3b2433"; g.font="bold 24px sans-serif"; g.textAlign="center"; g.fillText(CAPS[ph.cap], Wd/2, Ht-20);
    g.lineWidth=12; g.strokeStyle="#3b2433"; g.strokeRect(0,0,Wd,Ht); return cv.toDataURL("image/jpeg", .8); }
  /* 🖼 액자 (벽) — 색 단추 = 앨범의 다른 사진 */
  const phTex={};
  ITEMS.photo={nm:"photo frame", ic:"🖼", sz:[1,1], wall:true, use:"photo", special:1, cols:[0xc9925c,0xffffff,0xff9ac8,0x5aa7ff,0xffd23f,0x3b2433], build(c){ const g=new THREE.Group(), A=album(), a=A.length?A[(c|0)%A.length]:null;
      const fr=part(g, new THREE.BoxGeometry(.7,.86,.05), M(this.cols[(c|0)%this.cols.length]), 0,1.5,.03);
      let mat; if(a){ if(!phTex[a.t]){ const tx=new THREE.TextureLoader().load(a.d, ()=>{ try{ dirty=true; }catch(e){} }); tx.encoding=THREE.sRGBEncoding; phTex[a.t]=tx; } mat=new THREE.MeshBasicMaterial({map:phTex[a.t]}); } else mat=M(0xfff3e0);
      const p=new THREE.Mesh(new THREE.PlaneGeometry(.56,.7), mat); p.position.set(0,1.5,.06); g.add(p); return g; }};
  try{ VISIT_OK.photo=1; const _use=HLIFE.use; HLIFE.use=u=>{ if(u==="photo"){ const A=album(); if(visiting){ toast("🖼 친구 사진이에요", 1400); return true; } if(!A.length){ toast("🖼 아직 사진이 없어요 — 마을 📸 사진관에서 찍어요", 2000); return true; }
      show("tfAl", hd("📒 내 앨범", "액자 색 단추를 누르면 다른 사진")+'<div class="tfRow">'+A.map(a=>'<img src="'+a.d+'" alt="" style="width:120px;border-radius:10px;border:2.5px solid #3b2433">').join("")+'</div>'); return true; } return _use(u); }; }catch(e){}

  /* ═════════ 📚 도서관 — 영어 그림책 ═════════ */
  const BOOKS=[
    {id:"cat", t:"My Cat", e:"🐱", c:"#ff9ac8", p:[["🐱","This is my cat.","이건 내 고양이야."],["🐾","My cat is small.","내 고양이는 작아."],["🐟","My cat likes fish.","내 고양이는 물고기를 좋아해."],["⬆️","My cat can jump.","내 고양이는 점프할 수 있어."],["🛏","My cat sleeps on my bed.","내 고양이는 내 침대에서 자."],["❤️","I love my cat!","나는 내 고양이가 좋아!"]]},
    {id:"park", t:"At the Park", e:"🌳", c:"#7fd36a", p:[["🌳","I go to the park.","나는 공원에 가."],["🌲","I see a big tree.","큰 나무가 보여."],["⚽","I see a red ball.","빨간 공이 보여."],["🧒","I play with my friend.","나는 친구랑 놀아."],["🏃","We run and jump.","우리는 달리고 점프해."],["☀️","It is a happy day!","행복한 날이야!"]]},
    {id:"dog", t:"The Hungry Dog", e:"🐶", c:"#ffc93d", p:[["🐶","The dog is hungry.","강아지가 배고파."],["🍎","He finds an apple.","강아지가 사과를 찾았어."],["🙅","He does not like apples.","강아지는 사과를 안 좋아해."],["🦴","He finds a bone.","강아지가 뼈다귀를 찾았어."],["😋","Yum! He likes bones.","냠! 강아지는 뼈다귀를 좋아해."],["😊","Now he is happy.","이제 강아지는 행복해."]]},
    {id:"rain", t:"Rainy Day", e:"☔", c:"#5aa7ff", p:[["🌧","It is raining.","비가 와."],["☂️","I have a yellow umbrella.","나는 노란 우산이 있어."],["💦","I jump in the water.","나는 물웅덩이에서 점프해."],["👢","My boots are wet.","내 장화가 젖었어."],["🌈","I see a rainbow!","무지개가 보여!"],["☀️","Hello, sun!","안녕, 해님!"]]},
    {id:"fish", t:"Fishing Trip", e:"🎣", c:"#4cc3c9", p:[["🏞","We go to the lake.","우리는 호수에 가."],["🎣","I have a fishing rod.","나는 낚싯대가 있어."],["⏳","I wait and wait.","나는 기다리고 또 기다려."],["🐟","I catch a big fish!","큰 물고기를 잡았어!"],["🐢","Look! A turtle!","봐! 거북이야!"],["🎉","What a fun day!","정말 재미있는 날이야!"]]},
    {id:"night", t:"Good Night", e:"🌙", c:"#9b72f0", p:[["🌙","The moon is up.","달이 떴어."],["⭐","The stars are shining.","별이 반짝여."],["🪥","I brush my teeth.","나는 이를 닦아."],["📖","I read a book.","나는 책을 읽어."],["🧸","I hug my teddy bear.","나는 곰 인형을 안아."],["😴","Good night!","잘 자!"]]},
  ];
  const libDone=()=>store("hyeng_proto_lib")||{};
  function openLib(){ const D=libDone(), tot=(study().days||{}).tot|0;
    const d=show("tfLb", hd("📚 도서관", "영어 그림책 · 공부한 날 2일마다 한 권씩 열려요")+'<div class="hlBooks" style="grid-template-columns:repeat(3,1fr)">'+BOOKS.map((b,i)=>{ const open=tot>=i*2; return '<button data-bk="'+i+'" style="height:110px;background:'+(open?b.c:"#c9bfae")+'"'+(open?'':' disabled')+'><span style="font-size:34px">'+(open?b.e:"🔒")+'</span>'+esc(b.t)+(D[b.id]?'<br>⭐':(open?'':'<br><small>공부 '+i*2+'일</small>'))+'</button>'; }).join("")+'</div>');
    d.querySelector(".lb").onclick=e=>{ const b=e.target.closest("[data-bk]"); if(b && !b.disabled) readBook(BOOKS[+b.dataset.bk], 0); }; }
  function readBook(bk, i){ const pg=bk.p[i], last=i===bk.p.length-1;
    const d=show("tfLb", hd("📖 "+esc(bk.t), (i+1)+" / "+bk.p.length)+'<div class="tfCard" style="background:'+bk.c+'22"><div class="big" style="font-size:84px">'+pg[0]+'</div><div class="en" data-say style="cursor:pointer">'+esc(pg[1])+'</div><div class="ko" id="tfKo" style="visibility:hidden">'+esc(pg[2])+'</div></div>'
      +'<div class="tfRow"><button data-prev'+(i?'':' disabled')+'>◀</button><button data-say style="font-size:15px">🔊 읽어 주기</button><button data-ko style="font-size:15px">👀 뜻</button><button data-next>'+(last?'✅':'▶')+'</button></div>');
    try{ say(pg[1]); }catch(e){}
    d.querySelector(".lb").onclick=e=>{ if(e.target.closest("[data-say]")){ try{ say(pg[1]); }catch(_){} return; } if(e.target.closest("[data-ko]")){ $("tfKo").style.visibility="visible"; return; }
      if(e.target.closest("[data-prev]") && i) readBook(bk, i-1); if(e.target.closest("[data-next]")){ if(!last) readBook(bk, i+1); else bookQuiz(bk); } }; }
  function bookQuiz(bk){ close("tfLb"); const ix=[0,1,2,3,4,5].sort(()=>Math.random()-.5).slice(0,2); let k=0, ok=0;
    const one=()=>{ if(k>=2){ if(!ok){ toast("📚 한 문제는 맞혀야 ⭐ 를 받아요 — 다시 읽어 봐요!", 2200); openLib(); return; }   /* (v561) QA: 다 틀려도 ⭐·💎3 받던 것 */
      const D=libDone(), first=!D[bk.id]; D[bk.id]=1; store("hyeng_proto_lib", D); try{ tEv("book"); emote(hero,"📖"); }catch(_){} if(first) pay(3, "📚 "+bk.t+" 다 읽었어요 ⭐"); else toast("📚 또 읽었어요! "+ok+" / 2", 1600); openLib(); return; }
      const pg=bk.p[ix[k]]; pick1("📖 "+bk.t+" — 무슨 문장일까요? "+(k+1)+" / 2", pg[0], pg[1], bk.p.map(x=>x[1]), r=>{ if(r) ok++; k++; one(); }, {ask:"그림에 맞는 문장은?", n:3}); };
    one(); }

  /* ═════════ 🚉 기차역 ═════════ */
  const DEST=[["plaza","⛲","광장","the plaza"],["market","🏪","상점가","the market"],["lake","🎣","호수","the lake"],["school","🎓","배움 언덕","the school"],["tower","🗼","하늘 타워","the tower"],["mine","⛏","광산","the mine"],["park","🎡","놀이 공원","the park"],["farm","🌾","농장","the farm"],["home","⭐","내 집","my house"]];
  function destAt(k){ const S=ISLE.SPOT; if(k==="home"){ const d=ISLE.doorCell(); return d?[d[0]+.5,d[1]+.5]:null; } if(k==="plaza") return [ISLE.OX+2.6, ISLE.OZ+2.6]; if(k==="park") return S.oxC?[S.oxC[0]+3.6,S.oxC[1]-3.6]:null; if(k==="market") return S.shops&&S.shops[0]?S.shops[0].door:null;
    const p=S[k]; return p?[p[0], p[2]]:null; }
  function warp(x,z){ const B=ISLE.blocked; let bx=Math.floor(x), bz=Math.floor(z), f=null; for(let r=0;r<8 && !f;r++) for(let dx=-r;dx<=r && !f;dx++) for(let dz=-r;dz<=r && !f;dz++){ if(Math.max(Math.abs(dx),Math.abs(dz))!==r) continue; if(!B(bx+dx,bz+dz)) f=[bx+dx,bz+dz]; }
    if(!f) return false; hero.path=[]; hero.moving=false; hero.slide=null; hero.cx=f[0]; hero.cz=f[1]; hero.g.position.set(f[0]+.5,0,f[1]+.5); if(petObj) petObj.position.copy(hero.g.position); camSnap=true; placeCamera(); return true; }
  function openStation(){ const d=show("tfSt", hd("🚉 기차역", "🎫 표 🪙"+TECO.trainFee()+" · 안내 방송을 맞히면 다음 표 반값 · 걸어가면 무료")+'<div class="tfGrid">'+DEST.map(x=>'<button data-ds="'+x[0]+'"><i>'+x[1]+'</i><span>'+x[2]+'</span><b>'+x[3]+'</b></button>').join("")+'</div>');
    d.querySelector(".lb").onclick=e=>{ const b=e.target.closest("[data-ds]"); if(b) ride(DEST.find(x=>x[0]===b.dataset.ds)); }; }
  function ride(D){ if(!TECO.payTrain()) return; close("tfSt");   /* (v563) 🎫 기차표 = 이용료 (코인을 털어 냄) */ let R=$("tfRide"); if(!R){ R=document.createElement("div"); R.id="tfRide"; document.body.appendChild(R); ["pointerdown","pointerup","click"].forEach(ev=>R.addEventListener(ev, e=>e.stopPropagation())); }
    const an="Next stop is "+D[3]+"!"; R.innerHTML='<div class="tr">🚂🚃🚃</div><div class="an">🔊 "'+esc(an)+'"</div><div class="qq">칙칙폭폭…</div>'; R.classList.add("on"); try{ say(an); SND.pop(); }catch(e){}
    setTimeout(()=>{ const opts=[D]; while(opts.length<3){ const x=DEST[Math.floor(Math.random()*DEST.length)]; if(opts.indexOf(x)<0) opts.push(x); } opts.sort(()=>Math.random()-.5);
      R.querySelector(".qq").innerHTML='🤔 어디에 도착할까요?<div class="tfRow">'+opts.map(o=>'<button data-a="'+o[0]+'" style="font-size:16px;height:58px">'+o[1]+' '+o[2]+'</button>').join("")+'</div>';
      R.onclick=e=>{ const b=e.target.closest("[data-a]"); if(!b || R.dataset.lock) return; R.dataset.lock=1; const r=b.dataset.a===D[0]; b.classList.add(r?"r":"w"); try{ (r?SND.win:SND.snap)(); }catch(_){}
        setTimeout(()=>{ delete R.dataset.lock; R.classList.remove("on"); R.onclick=null; const p=destAt(D[0]); if(p) warp(p[0],p[1]); try{ tEv("train"); }catch(_){}
          if(r){ TECO.trainRight(); toast("🚉 "+D[2]+" 도착! · 🎫 다음 기차표 반값", 1800); } else toast("🚉 "+D[2]+" ("+D[3]+") 에 왔어요!", 1800); }, 800); }; }, 2600); }

  /* ═════════ 틱 — 펫 · 날리는 것 · 불꽃놀이 · 편지 알림 ═════════ */
  let lastPl=null, fwT=0, pillT=0, mailSeen=-1;
  function tick(dt){ let anim=false; try{ if(window.TECO && TECO.tick(dt)) anim=true; }catch(e){} try{ if(petT0===""&&!tick.s){ tick.s=1; petSync(); } if(petTick(dt)) anim=true; if(visTick(dt)) anim=true; }catch(e){}
    pillT+=dt; if(pillT>1){ pillT=0; ensurePill(); updPill(); try{ petSync(); }catch(e){} }
    const isle=isIsle(); if(isle!==lastPl){ lastPl=isle; if(isle){ loadMail().then(M=>{ let tOn=false; try{ tOn=tut.s<TUT.length-1; }catch(e){} if(M.unread && !tOn && M.unread!==mailSeen){ mailSeen=M.unread; toast("📮 편지 <b>"+M.unread+"통</b>이 왔어요! 우체국에 가 봐요", 2400); } });   /* (v561) QA: 튜토리얼 중엔 안 띄움(Mia 안내와 겹침) · 같은 수면 다시 안 띄움 */ if(Date.now()-GOAL.at>60e3) loadGoal(); } }
    if(!isle) return anim;
    if(parts){ const a=parts.geometry.attributes.position, hp=hero.g.position, k=parts.userData.kind, tm=performance.now()/1000;
      for(let i=0;i<a.count;i++){ let x=a.getX(i), y=a.getY(i), z=a.getZ(i); y-=dt*(k==="winter"?.9:.7); x+=Math.sin(tm+i)*dt*(k==="winter"?.2:.5); if(y<0){ y=14; } a.setXYZ(i,x,y,z); }
      a.needsUpdate=true; parts.position.set(hp.x, 0, hp.z); anim=true; }
    if(fw && GOAL.tot>=GOAL.target){ const tn=performance.now(); if(tn-fwT>2200){ fwT=tn; burst(); } fw.children.slice().forEach(P=>{ P.userData.t+=dt; const t=P.userData.t, A=P.geometry.attributes.position, V=P.userData.v; for(let i=0;i<A.count;i++) A.setXYZ(i, V[i*3]*t, V[i*3+1]*t-1.6*t*t, V[i*3+2]*t); A.needsUpdate=true; P.material.opacity=Math.max(0,1-t/1.7); if(t>1.7){ fw.remove(P); P.geometry.dispose(); P.material.dispose(); } }); anim=true; }
    return anim; }
  function burst(){ const n=50, g=new THREE.BufferGeometry(), a=new Float32Array(n*3), v=[]; for(let i=0;i<n;i++){ const u=Math.random()*2-1, th=Math.random()*6.283, s=Math.sqrt(1-u*u), sp=3+Math.random()*1.4; v.push(s*Math.cos(th)*sp, u*sp, s*Math.sin(th)*sp); }
    g.setAttribute("position", new THREE.BufferAttribute(a,3)); const P=new THREE.Points(g, new THREE.PointsMaterial({color:[0xff6b6b,0xffd23f,0x5aa7ff,0x7fd36a,0xff9ac8][Math.floor(Math.random()*5)], size:.35, transparent:true, depthWrite:false})); P.frustumCulled=false;
    P.position.set(C.OX+(Math.random()-.5)*10, 13+Math.random()*3, C.OZ+(Math.random()-.5)*10); P.userData={t:0, v}; fw.add(P); }
  /* 🍗 단추 — 방 HUD(#hud) · 섬 HUD(#ihRes) */
  function ensurePill(){ const mk=(par, id, cls)=>{ const p=$(par); if(!p || $(id)) return; const b=document.createElement(par==="hud"?"button":"span"); b.id=id; b.className=cls; b.innerHTML='<i>🍗</i><b>5</b>'; b.setAttribute("aria-label","배부름 · 펫"); b.style.cursor="pointer";
      ["pointerdown","pointerup"].forEach(ev=>b.addEventListener(ev, e=>e.stopPropagation())); b.addEventListener("click", e=>{ e.stopPropagation(); openMe(); }); p.appendChild(b); };
    mk("hud","hFull","pill tap full"); mk("ihRes","ihFull",""); }
  function petPub(){ const P=PET(); return P?{t:P.t, n:P.n}:null; }
  return {build, labels, tick, spd, full, eat, openGoal, openPost, openSnack, openPet, openMuseum, openPhoto, openLib, openStation, openMe, loadGoal, loadMail, loadMus, myPts, petPub, shoot, warp, ride, stage, season, SP, GOAL, MAIL, FAC, BOOKS, SENT, SNACK, PETS, TRICK, DEST, petObj:()=>petObj, PET};
})();
window.TFAC=TFAC;
