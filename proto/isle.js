/* ═════════ (v521) 🏝 우리 마을 — 학원 전체가 같이 사는 섬 마을 (1단계: 땅·건물·조이스틱·이름 확인)
   사용자: "마을뿐만 아니라 타운을 다같이 쓰는 집처럼 · 집에서 나오면 다같이 보이면서 바로 이야기 · 밭은 다른 곳 · 마인크래프트처럼"
           → "학원전체로 · 이름을 플레이어로 한 사람은 못 들어가게 · 맵이 더 넓게 · 집이 늘어나기도 · 집짓기는 포기 (대신 고민해서)"
   · 모델 = KayKit Medieval Hexagon(CC0) 섬 묶음 assets/town/kk/isle.* (풀 색은 My Town 초록으로 바꿈)
   · 가운데 섬(광장·분수·시장 천막·같이 낚시터·가게 거리·학교·공원·하늘 타워·광산) + 동네 섬 3(집 터 18 · 내 집 ⭐) + 새 동네 자리 + 밭 섬 — 다리로 이음
   · 칸 = 1 (다른 장소와 같음) · 땅 그림은 육각 · 걸을 수 있는 칸은 육각 → 네모 칸으로 다시 계산 (BFS·이름표·친구 위치가 그대로 동작)
   · 정적 모델은 섬마다 하나로 합쳐 그림 (그리기 수 줄이기) · 조이스틱 + 점프 · 그림자는 나를 따라감
   · 테스트(자동 브라우저)에서는 기본 꺼짐 — ?isle=1 로 켬 (기존 마당 테스트가 그대로 돌게) */
const ISLE=(()=>{
  const q=new URLSearchParams(location.search);
  const ON = q.get("isle")==="1" || (q.get("isle")!=="0" && !navigator.webdriver);
  const S=1.05, N=96, OX=48, OZ=60;
  const G=new THREE.Group(); G.name="isle"; G.visible=false; scene.add(G);
  const W=new Uint8Array(N*N);              // 1 = 걸을 수 있음
  const cols=[];                            // 막는 동그라미 [x,z,r]
  const bridges=[];                         // [ax,az,bx,bz,반폭]
  let seed=7; const rnd=()=>{ seed=(seed*9301+49297)%233280; return seed/233280; };
  const MT={}; const LIN=c=>new THREE.Color(c).convertSRGBToLinear(); const MC=(c)=>MT[c]||(MT[c]=new THREE.MeshStandardMaterial({color:LIN(c), roughness:.85}));   /* (v528) 색은 sRGB → 선형 (안 바꾸면 허옇게 바램) */
  /* ── 합치기 — KayKit 모델 놓을 자리만 모아 두었다가 묶음마다 한 덩어리 ── */
  const bag={};   // key = 묶음|덩어리 → [{g, m}]
  function kk(pack,k,x,z,o){ o=o||{}; const R=KK.R[pack]; if(!R || !R.G[k]) return null; const g=R.G[k], bb=g.boundingBox; let s=(o.s||1)*S;
    const M4=new THREE.Matrix4().compose(new THREE.Vector3(x+OX, o.y||0, z+OZ), new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,1,0), o.ry||0), new THREE.Vector3(s,s,s))
      .multiply(new THREE.Matrix4().makeTranslation(-(bb.min.x+bb.max.x)/2, -bb.min.y, -(bb.min.z+bb.max.z)/2));
    if(o.col) cols.push([x+OX, z+OZ, o.col]);
    if(o.solo){ const m=new THREE.Mesh(g, R.mat); m.matrixAutoUpdate=false; m.matrix.copy(M4); m.castShadow=true; m.receiveShadow=true; const W=new THREE.Group(); W.add(m); W.userData.solo=1; G.add(W); return W; }   /* (v525) 집·큰 건물 = 따로 (가리면 그것만 흐려짐) */
    const key=pack+"|"+(o.chunk||"c"); (bag[key]=bag[key]||[]).push({g, m:M4, cast:o.cast!==false}); return true; }
  function merge(){ Object.keys(bag).forEach(key=>{ const pack=key.split("|")[0], L=bag[key], R=KK.R[pack];
      let nv=0, ni=0; L.forEach(e=>{ nv+=e.g.attributes.position.count; ni+=e.g.index.count; });
      const P=new Float32Array(nv*3), Nn=new Float32Array(nv*3), U=new Float32Array(nv*2), I=new Uint32Array(ni); let ov=0, oi=0; const v=new THREE.Vector3(), nm=new THREE.Matrix3();
      L.forEach(e=>{ const g=e.g, pa=g.attributes.position, na=g.attributes.normal, ua=g.attributes.uv, ix=g.index; nm.getNormalMatrix(e.m); const uk=(ua.normalized && ua.array instanceof Uint16Array) ? 1/65535 : 1;   /* r128 getX 는 정규화 안 함 */
        for(let i=0;i<pa.count;i++){ v.fromBufferAttribute(pa,i).applyMatrix4(e.m); P.set([v.x,v.y,v.z],(ov+i)*3); v.fromBufferAttribute(na,i).applyMatrix3(nm).normalize(); Nn.set([v.x,v.y,v.z],(ov+i)*3); U[(ov+i)*2]=ua.getX(i)*uk; U[(ov+i)*2+1]=ua.getY(i)*uk; }
        for(let i=0;i<ix.count;i++) I[oi+i]=ix.getX(i)+ov; ov+=pa.count; oi+=ix.count; });
      const geo=new THREE.BufferGeometry(); geo.setAttribute("position", new THREE.BufferAttribute(P,3)); geo.setAttribute("normal", new THREE.BufferAttribute(Nn,3)); geo.setAttribute("uv", new THREE.BufferAttribute(U,2)); geo.setIndex(new THREE.BufferAttribute(I,1)); geo.computeBoundingSphere();
      const m=new THREE.Mesh(geo, R.mat); m.castShadow=true; m.receiveShadow=true; G.add(m); });
    Object.keys(bag).forEach(k=>delete bag[k]); }
  function mesh(geo, col, x, y, z, o){ const m=new THREE.Mesh(geo, o&&o.basic ? new THREE.MeshBasicMaterial({color:LIN(col)}) : MC(col)); m.position.set(x+OX,y,z+OZ); m.castShadow=!(o&&o.nocast); m.receiveShadow=true; G.add(m); return m; }
  /* ── (v528) 섬 = 매끈한 땅 한 판 (사용자: "꼭 6각형 타일로 한 이유는?" → 판처럼 보여서 매끈한 땅 + 네모 땅 칸) ── */
  const ISL=[];   // {cx,cz,R,s,holes:[[x,z,rx,rz]]}
  const rr=(I,a)=>I.R*(1+.035*Math.sin(3*a+I.s)+.025*Math.sin(5*a+I.s*2));
  function inIsle(I,x,z,m){ const dx=x-I.cx, dz=z-I.cz; return Math.hypot(dx,dz) < rr(I,Math.atan2(dz,dx))-(m||0); }
  const GRASS=0x86c96a, DIRT=0xa3714a, PATH=0xdcbf86, STONE=0xd2c7b0, PAD=0x9fd884, PADE=0xe0c896;
  function land(cx,cz,R,s,holes){ const I={cx,cz,R,s:s||0,holes:holes||[]}; ISL.push(I); const sh=new THREE.Shape(), n=72;
    for(let i=0;i<=n;i++){ const a=i/n*6.2832, r=rr(I,a); const x=Math.cos(a)*r, y=Math.sin(a)*r; i?sh.lineTo(x,y):sh.moveTo(x,y); }
    I.holes.forEach(([hx,hz,ax,az])=>{ const p=new THREE.Path(); for(let i=0;i<=48;i++){ const a=-i/48*6.2832; const x=hx-cx+Math.cos(a)*ax, y=hz-cz+Math.sin(a)*az; i?p.lineTo(x,y):p.moveTo(x,y); } sh.holes.push(p); });
    const geo=new THREE.ExtrudeGeometry(sh,{depth:1.25, bevelEnabled:true, bevelThickness:.12, bevelSize:.22, bevelSegments:2, curveSegments:6}); geo.rotateX(Math.PI/2);
    const m=new THREE.Mesh(geo,[MC(GRASS), MC(DIRT)]); m.position.set(cx+OX,-.12,cz+OZ); m.receiveShadow=true; G.add(m);
    I.holes.forEach(([hx,hz,ax,az])=>{ const w=new THREE.Mesh(new THREE.CircleGeometry(1,48), new THREE.MeshStandardMaterial({color:LIN(0x58c2e6), roughness:.25})); w.rotation.x=-Math.PI/2; w.scale.set(ax,az,1); w.position.set(hx+OX,-.2,hz+OZ); G.add(w);
      const sd=new THREE.Mesh(new THREE.RingGeometry(.93,1.06,48), MC(0xe6d29a)); sd.rotation.x=-Math.PI/2; sd.scale.set(ax,az,1); sd.position.set(hx+OX,.012,hz+OZ); sd.receiveShadow=true; G.add(sd); });
    return I; }
  const water=(x,z)=>ISL.some(I=>I.holes.some(([hx,hz,ax,az])=>((x-hx)/ax)**2+((z-hz)/az)**2<=1.06));
  /* 길 · 광장 (평평한 판) */
  const paved=[];   // [ax,az,bx,bz,반폭] · [x,z,r]
  function strip(x1,z1,x2,z2,w,col){ const L=Math.hypot(x2-x1,z2-z1), a=Math.atan2(x2-x1,z2-z1); const p=new THREE.Mesh(new THREE.PlaneGeometry(w,L), MC(col||PATH)); p.rotation.set(-Math.PI/2,0,a); p.position.set((x1+x2)/2+OX,.01,(z1+z2)/2+OZ); p.receiveShadow=true; G.add(p);
    [[x1,z1],[x2,z2]].forEach(([x,z])=>{ const c=new THREE.Mesh(new THREE.CircleGeometry(w/2,20), MC(col||PATH)); c.rotation.x=-Math.PI/2; c.position.set(x+OX,.011,z+OZ); c.receiveShadow=true; G.add(c); }); paved.push([x1,z1,x2,z2,w/2]); }
  function disc(x,z,r,col){ const c=new THREE.Mesh(new THREE.CircleGeometry(r,40), MC(col||STONE)); c.rotation.x=-Math.PI/2; c.position.set(x+OX,.013,z+OZ); c.receiveShadow=true; G.add(c);
    const e=new THREE.Mesh(new THREE.RingGeometry(r-.12,r,40), MC(0xb9ac94)); e.rotation.x=-Math.PI/2; e.position.set(x+OX,.016,z+OZ); G.add(e); paved.push([x,z,r]); }
  const onPave=(x,z,m)=>paved.some(p=>{ if(p.length===3) return Math.hypot(x-p[0],z-p[1])<p[2]+(m||0); const [ax,az,bx,bz,w]=p, dx=bx-ax, dz=bz-az, L2=dx*dx+dz*dz||1, t=Math.max(0,Math.min(1,((x-ax)*dx+(z-az)*dz)/L2)); return Math.hypot(x-ax-dx*t,z-az-dz*t)<w+(m||0); });
  const TR=["trees_A_large","trees_A_medium","trees_B_large","trees_B_medium","tree_single_A","tree_single_B","trees_A_small"];
  const busy=[];  // 나무를 심지 않을 자리 [x,z,r]
  function trees(I,n,chunk){ for(let k=0;k<n;k++){ const a=rnd()*6.2832, t=Math.sqrt(.25+rnd()*.75), r=rr(I,a)*t*.93, x=I.cx+Math.cos(a)*r, z=I.cz+Math.sin(a)*r;
      if(!inIsle(I,x,z,.7) || water(x,z) || onPave(x,z,.9) || busy.some(([bx,bz,br])=>Math.hypot(x-bx,z-bz)<br)) continue;
      const edge=t>.82, key=edge ? (rnd()<.7?"tree_single_A":"trees_A_small") : TR[Math.floor(rnd()*TR.length)]; kk("isle",key,x,z,{s:1.1,ry:rnd()*6,chunk,col:.5}); busy.push([x,z,.9]); } }
  function bridge(x1,z1,x2,z2){ const dx=x2-x1, dz=z2-z1, L=Math.hypot(dx,dz), a=Math.atan2(dx,dz); const B=new THREE.Group(); B.position.set(x1+OX,0,z1+OZ); B.rotation.y=a; G.add(B);
    const n=Math.max(2,Math.round(L/0.46)); for(let i=0;i<n;i++){ const pl=new THREE.Mesh(new THREE.BoxGeometry(1.5,.11,.42), MC(i%2?0xb07a4a:0x9a6a40)); pl.position.set(0,.025,i*(L/n)+.2); pl.receiveShadow=true; B.add(pl); }
    for(let i=0;i<=n;i+=3){ [-.76,.76].forEach(s=>{ const po=new THREE.Mesh(new THREE.CylinderGeometry(.065,.065,.8,6), MC(0x7a4f2c)); po.position.set(s,.1,i*(L/n)); B.add(po); }); }
    [-.76,.76].forEach(s=>{ const rl=new THREE.Mesh(new THREE.BoxGeometry(.06,.06,L), MC(0x7a4f2c)); rl.position.set(s,.42,L/2); B.add(rl); });
    bridges.push([x1+OX,z1+OZ,x2+OX,z2+OZ,1.0]); }   /* 걷기 폭 넉넉히 (비스듬한 다리가 계단처럼 끊기지 않게) */
  /* 다리는 섬 가장자리(구불구불)를 지나 땅 안쪽 1칸까지 — 끊기지 않게 (v528 QA: 2·3동이 광장과 안 이어짐) */
  function edgeR(c,r,ang){ const I=ISL.find(I=>Math.abs(I.cx-c[0])<.01 && Math.abs(I.cz-c[1])<.01); return I ? rr(I,ang) : r; }
  function link(A,ra,B,rb){ const dx=B[0]-A[0], dz=B[1]-A[1], L=Math.hypot(dx,dz), ux=dx/L, uz=dz/L, ea=edgeR(A,ra,Math.atan2(uz,ux)), eb=edgeR(B,rb,Math.atan2(-uz,-ux));
    bridge(A[0]+ux*(ea-1.1),A[1]+uz*(ea-1.1),B[0]-ux*(eb-1.1),B[1]-uz*(eb-1.1));
    for(let s=0;s<=3;s+=.8){ busy.push([A[0]+ux*(ea-1.1-s),A[1]+uz*(ea-1.1-s),1.3]); busy.push([B[0]-ux*(eb-1.1-s),B[1]-uz*(eb-1.1-s),1.3]); } }   /* 다리 끝에는 나무를 심지 않음 */
  /* ── 동네 = 네모 땅 칸 16개 (십자 길 양옆) · 아이가 고름 · 바다 앞 2칸 = 좋은 자리(공부한 날) ── */
  const HC=["building_home_A_red","building_home_B_blue","building_home_A_yellow","building_home_B_green","building_home_A_blue","building_home_B_red","building_home_A_green","building_home_B_yellow"];
  const LOT=2.2, HOODR=9.4;
  const lots=[];   // {id,hood,n,x,z,face,prem,owner,me,obj}
  function hood(cx,cz,name,chunk){ const I=land(cx,cz,HOODR,cx*.3+cz*.1);
    disc(cx,cz,1.5,STONE); [[1,0],[-1,0],[0,1],[0,-1]].forEach(([ux,uz])=>strip(cx+ux*1.3,cz+uz*1.3,cx+ux*8.4,cz+uz*8.4,1.45,PATH));
    kk("city","streetlight",cx+.9,cz+.9,{s:1,chunk,col:.2}); kk("city","bench",cx-1.15,cz-1.15,{s:.9,ry:Math.PI/4,chunk,col:.35});
    const toP=[-cx,-cz], Lp=Math.hypot(toP[0],toP[1])||1; let far=null, fd=9;
    [[1,0],[-1,0],[0,1],[0,-1]].forEach(([ux,uz])=>{ const d=(ux*toP[0]+uz*toP[1])/Lp; if(d<fd){ fd=d; far=[ux,uz]; } });
    let n=0; [[1,0],[-1,0],[0,1],[0,-1]].forEach(([ux,uz])=>{ [4.2,6.6].forEach(along=>{ [-1,1].forEach(side=>{ n++;
      const ox=ux*along+(uz!==0?side*1.95:0), oz=uz*along+(ux!==0?side*1.95:0), face=Math.atan2(-(ux!==0?0:side*1), -(uz!==0?0:side*1))*0+Math.atan2(ux!==0?0:-side, uz!==0?0:-side);
      const L={id:name.replace("동","")+"-"+n, hood:name, n, x:cx+ox, z:cz+oz, face, prem:!!(far && far[0]===ux && far[1]===uz && along===6.6), chunk};
      lots.push(L); busy.push([L.x,L.z,1.6]); }); }); });
    return I; }
  const D={plaza:[0,0], d1:[0,-31], d2:[-27,-17.5], d3:[27,-17.5], d4:[0,-50.5], d5:[-27,-38], d6:[27,-38], farm:[-30,11]};
  const HOODS=[["1동","d1"],["2동","d2"],["3동","d3"],["4동","d4"],["5동","d5"],["6동","d6"]];
  const SPOT={};   // 이름표·문 자리
  const onB=[];    // 다 지은 뒤 (놀이 IPLAY 가 물건을 붙임)
  let myHouse=null;
  function studyDays(){ try{ const s=JSON.parse(localStorage.getItem("hyeng_study_v1")||"{}"), d=s.days||{}; return d.tot||d.n||0; }catch(e){ return 0; } }
  const PREM_DAYS=5;
  function myLotId(){ try{ return localStorage.getItem("hyeng_isle_lot")||""; }catch(e){ return ""; } }
  /* ── (v528) 땅 = 서버 /hy/isle/lot/<땅> = {k:아이, c:집 코드, n:이름, at} · 먼저 고른 아이만 (쓰고 → 다시 읽어 내 것인지 확인) ── */
  const LOTP="/hy/isle/lot";
  let SRV={}, srvAt=0, srvOk=false;
  function myKey(){ let k=""; try{ const K=kidInfo(); k=K.rid||""; }catch(e){} return String(k||("c:"+myCode)).replace(/[.#$\[\]\/]/g,"_").slice(0,48); }
  async function loadLots(){ try{ const v=await NET.get(LOTP); SRV=v||{}; srvOk=true; srvAt=Date.now(); }catch(e){ srvOk=false; } return SRV; }
  function owners(){ const me=myKey(); let mine=null;
    lots.forEach(L=>{ const s=SRV[L.id]; L.rec=s||null; L.me=!!(s && s.k===me); L.owner=s ? (L.me?"나":String(s.n||"친구").slice(0,8)) : ""; if(L.me) mine=L; });
    if(!mine && !srvOk){ let id=myLotId(); if(!id){ const F=lots.filter(L=>!L.owner && !L.prem); let h=0; for(const ch of myKey()) h=(h*31+ch.charCodeAt(0))>>>0; if(F.length) id=F[h%F.length].id; } const L=lots.find(L=>L.id===id && !L.owner); if(L){ L.me=true; L.owner="나"; } }   /* 서버가 안 될 때 = 기기에 적어 둔 내 땅 */ }
  async function claim(id){ const L=lots.find(L=>L.id===id); if(!L) return "none"; const me=myKey(), K=kidInfo(), rec={k:me, c:myCode, n:String(K.n||"친구").slice(0,10), at:Date.now()};
    if(!NET.on()){ await NET.ready(); } if(!NET.on()){ try{ localStorage.setItem("hyeng_isle_lot", id); }catch(e){} return "local"; }
    try{ const cur=await NET.get(LOTP+"/"+id); if(cur && cur.k!==me) return "taken";
      await NET.put(LOTP+"/"+id, rec); await new Promise(r=>setTimeout(r, 450)); const chk=await NET.get(LOTP+"/"+id); if(!chk || chk.k!==me) return "taken";
      const old=Object.keys(SRV).filter(k=>k!==id && SRV[k] && SRV[k].k===me); for(const k of old){ try{ await NET.del(LOTP+"/"+k); }catch(e){} }   /* 전에 살던 땅은 비움 */
      try{ localStorage.setItem("hyeng_isle_lot", id); }catch(e){} await loadLots(); return "ok"; }catch(e){ return "err"; } }
  /* 처음 나오면 — 서버에 내 땅이 없으면 빈 땅 하나를 저절로 (나중에 게시판에서 옮길 수 있음) */
  async function autoClaim(){ if(lots.some(L=>L.me) || !srvOk) return false; const F=lots.filter(L=>!L.owner && !L.prem); if(!F.length) return false;
    let h=0; for(const ch of myKey()) h=(h*31+ch.charCodeAt(0))>>>0; for(let i=0;i<4;i++){ const L=F[(h+i*7)%F.length]; const r=await claim(L.id); if(r==="ok"){ toast("🏡 <b>"+L.hood+" "+L.n+"번 땅</b>이 내 집이 됐어요!<br><small>📋 광장 게시판에서 다른 땅으로 옮길 수 있어요</small>", 3600); return true; } } return false; }
  /* 동네 늘리기 — 빈 땅이 4칸 아래면 다음 동네 섬이 열림 (최대 6동 = 96칸) */
  function hoodCount(){ const n=Object.keys(SRV).length; let h=3; while(h<6 && h*16-n<4) h++; return h; }
  function drawLots(){ owners();
    lots.forEach(L=>{ const pad=new THREE.Mesh(new THREE.PlaneGeometry(LOT,LOT), MC(L.owner?PAD:PADE)); pad.rotation.x=-Math.PI/2; pad.position.set(L.x+OX,.008,L.z+OZ); pad.receiveShadow=true; G.add(pad);
      const ed=new THREE.Mesh(new THREE.RingGeometry(LOT*.69,LOT*.71,4,1), MC(L.owner?0x6fae58:0xc9a46a)); ed.rotation.set(-Math.PI/2,0,Math.PI/4); ed.position.set(L.x+OX,.012,L.z+OZ); G.add(ed);
      if(L.owner){ const k=HC[(L.n*3+L.hood.charCodeAt(0))%HC.length]; L.obj=kk("isle",k,L.x,L.z,{s:2.0,ry:L.face,chunk:L.chunk,col:.9,solo:1});
        if(L.me){ const st=mesh(new THREE.OctahedronGeometry(.32), 0xffd23f, L.x,3.0,L.z,{basic:1,nocast:1}); G.userData.star=st; } }
      else { const p=mesh(new THREE.CylinderGeometry(.05,.05,.8,6), 0x8a5a34, L.x,.4,L.z); const b=mesh(new THREE.BoxGeometry(.62,.36,.06), L.prem?0xffd23f:0xfff3d6, L.x,.82,L.z); b.rotation.y=L.face; cols.push([L.x+OX,L.z+OZ,.2]); } });
    myHouse=lots.find(L=>L.me)||null;
    lots.forEach(L=>{ if(L.obj) L.obj.userData.lot=L; }); }
  function build(){
    if(G.userData.built) return; G.userData.built=1;
    const sea=new THREE.Mesh(new THREE.CircleGeometry(400,48), new THREE.MeshStandardMaterial({color:LIN(0x6cc0dc), roughness:.35})); sea.rotation.x=-Math.PI/2; sea.position.set(OX,-0.76,OZ); sea.receiveShadow=true; G.add(sea); G.userData.sea=sea;
    // 가운데 섬 (호수 = 구멍)
    const LK=LKD; const C=land(0,0,17.6,.7,[LK]);
    disc(0,0,2.75,STONE); strip(0,2.6,0,15.4,1.5); strip(0,-2.6,0,-15.6,1.5); strip(-2.6,0,-15.6,0,1.5); strip(2.6,0,4.1,0,1.5); strip(-8,5.4,8,5.4,1.4); strip(-1,5.4,-3.6,10.2,1.3);
    // 분수
    { const st=0xcfc8b8; mesh(new THREE.CylinderGeometry(1.45,1.55,.45,14), st, 0,.22,0); mesh(new THREE.CylinderGeometry(1.3,1.3,.1,24), 0x5cc4e8, 0,.43,0,{nocast:1}); mesh(new THREE.CylinderGeometry(.2,.27,1.1,10), st, 0,.85,0);
      mesh(new THREE.CylinderGeometry(.55,.4,.18,12), st, 0,1.4,0); mesh(new THREE.CylinderGeometry(.48,.48,.06,16), 0x7fd3ea, 0,1.5,0,{nocast:1}); mesh(new THREE.SphereGeometry(.2,10,8), 0xbfeaff, 0,1.7,0,{nocast:1}); cols.push([OX,OZ,1.75]); SPOT.fountain=[OX,1.2,OZ]; }
    [[2.3,2.3],[-2.3,2.3],[2.3,-2.3],[-2.3,-2.3]].forEach(([x,z])=>kk("city","streetlight",x,z,{s:1,chunk:"m",col:.2}));
    [[3.3,1.3,Math.PI/2],[-3.3,1.3,-Math.PI/2]].forEach(([x,z,r])=>kk("city","bench",x,z,{s:.9,ry:r,chunk:"m",col:.45}));
    kk("isle","tent",-3.4,-3.2,{s:1.5,ry:.9,chunk:"m",col:1.0,solo:1}); kk("isle","crate_A_big",-4.4,-2.2,{s:.5,chunk:"m",col:.3}); kk("isle","barrel",-2.5,-4.2,{s:.5,chunk:"m",col:.3}); SPOT.market=[-3.4+OX,1.6,-3.2+OZ]; busy.push([-3.4,-3.2,2.2]);
    // 📋 게시판 (땅 고르기)
    { const b=new THREE.Group(); b.position.set(2.9+OX,0,-2.9+OZ); b.rotation.y=-Math.PI*.75; const W_=MC(0x9a6a40); [-.55,.55].forEach(x=>{ const p=new THREE.Mesh(new THREE.BoxGeometry(.1,1.3,.1),W_); p.position.set(x,.65,0); b.add(p); });
      const bd=new THREE.Mesh(new THREE.BoxGeometry(1.4,.85,.08),MC(0xc9925c)); bd.position.y=1.05; b.add(bd); [[-.3,1.15,0xfff3d6],[.25,1.0,0xdff3d6],[-.2,.88,0xffd9e6]].forEach(([x,y,c])=>{ const pp=new THREE.Mesh(new THREE.BoxGeometry(.38,.3,.02),MC(c)); pp.position.set(x,y,.05); b.add(pp); });
      b.traverse(m=>{ if(m.isMesh){ m.castShadow=true; } }); G.add(b); cols.push([2.9+OX,-2.9+OZ,.5]); SPOT.board=[2.9+OX,1.9,-2.9+OZ]; busy.push([2.9,-2.9,1.2]); }
    // 가게 거리
    const MK=["building_market_blue","building_market_red","building_market_green","building_market_yellow"]; [-6.6,-3.6,3.6,6.6].forEach((x,i)=>{ kk("isle",MK[i],x,7.6,{s:1.9,ry:Math.PI,chunk:"m",col:1.2,solo:1}); busy.push([x,7.6,2]); });
    kk("isle","building_church_blue",-5.2,11.2,{s:2.3,ry:Math.PI*0.9,chunk:"m",col:1.4,solo:1}); SPOT.school=[-5.2+OX,2.6,11.2+OZ]; busy.push([-5.2,11.2,2.6]);
    kk("isle","building_stage_A",5.6,11.2,{s:2.4,ry:-2,chunk:"m",col:1.2}); busy.push([5.6,11.2,2]);
    { const fx=2.4, fz=11; for(let i=0;i<4;i++){ const a=i/4*6.283+.4; const lg=mesh(new THREE.CylinderGeometry(.16,.16,.85,8), 0xa06a3c, fx+Math.cos(a)*1.1,.16,fz+Math.sin(a)*1.1); lg.rotation.z=Math.PI/2; lg.rotation.y=-a; }
      const f1=mesh(new THREE.ConeGeometry(.24,.6,8), 0xffa53a, fx,.32,fz,{basic:1,nocast:1}), f2=mesh(new THREE.ConeGeometry(.13,.42,8), 0xffe27a, fx,.3,fz,{basic:1,nocast:1}); G.userData.fire=[f1,f2]; cols.push([fx+OX,fz+OZ,.45]); SPOT.camp=[fx+OX,.9,fz+OZ]; busy.push([fx,fz,1.8]); }
    // 같이 낚시터 — 호숫가 나무 부두
    { const B=new THREE.Group(); B.position.set(4.3+OX,0,-.6+OZ); for(let i=0;i<8;i++){ const pl=new THREE.Mesh(new THREE.BoxGeometry(.45,.11,1.55), MC(i%2?0xb07a4a:0x9a6a40)); pl.position.set(i*.47,-.02,0); pl.receiveShadow=true; B.add(pl); }
      [[0,-.8],[0,.8],[3.3,-.8],[3.3,.8]].forEach(([x,z])=>{ const po=new THREE.Mesh(new THREE.CylinderGeometry(.08,.08,.9,6), MC(0x7a4f2c)); po.position.set(x,-.15,z); B.add(po); }); G.add(B); G.userData.dock=B;
      bridges.push([4.0+OX,-.6+OZ,7.6+OX,-.6+OZ,.7]); SPOT.lake=[6.5+OX,.6,-.6+OZ]; busy.push([5.5,-.6,1.5]); }
    for(let i=0;i<9;i++){ const a=rnd()*6.28, r=Math.sqrt(rnd())*.8; kk("isle",rnd()<.5?"waterlily_A":"waterlily_B",LK[0]+Math.cos(a)*LK[2]*r,LK[1]+Math.sin(a)*LK[3]*r,{s:.8,y:-.36,chunk:"m",cast:false}); }
    kk("isle","building_tower_B_blue",-10,-10,{s:3.2,chunk:"m",col:1.6,solo:1}); kk("isle","flag_blue",-8.6,-9.2,{s:1.6,chunk:"m"}); SPOT.tower=[-10+OX,3.4,-10+OZ]; busy.push([-10,-10,3]); strip(-2,-2,-8.6,-8.6,1.3);
    kk("isle","building_mine_blue",9.6,-12,{s:2.2,ry:Math.PI*0.8,chunk:"m",col:1.4,solo:1}); kk("isle","mountain_B_grass_trees",12,-13.4,{s:1.4,chunk:"m",col:2.2}); SPOT.mine=[9.6+OX,2,-12+OZ]; busy.push([10.5,-12.6,4]); strip(1.2,-6,8.2,-10.8,1.3);
    /* (v528) 놀이 자리 — ⭕❌ OX 단어 마당 · 🧊 놀이터(얼음땡) · 🎁 보물 상자 */
    { const ox=[-8.6,3.6]; SPOT.oxC=[ox[0]+OX,ox[1]+OZ]; busy.push([ox[0],ox[1],4.2]); disc(ox[0],ox[1],3.9,0xe7dcc2);
      [[-2,0x7fd3ff,"O"],[2,0xff9a9a,"X"]].forEach(([dx,col,ch])=>{ const c=document.createElement("canvas"); c.width=c.height=128; const g=c.getContext("2d"); g.fillStyle="#"+new THREE.Color(col).getHexString(); g.fillRect(0,0,128,128); g.fillStyle="#fff"; g.font="900 96px sans-serif"; g.textAlign="center"; g.textBaseline="middle"; g.fillText(ch==="O"?"O":"X",64,70); g.strokeStyle="#3b2433"; g.lineWidth=8; g.strokeRect(4,4,120,120);
        const tx=new THREE.CanvasTexture(c); tx.encoding=THREE.sRGBEncoding; const m=new THREE.Mesh(new THREE.PlaneGeometry(3.1,3.1), new THREE.MeshStandardMaterial({map:tx, roughness:.9})); m.rotation.x=-Math.PI/2; m.position.set(ox[0]+dx+OX,.02,ox[1]+OZ); m.receiveShadow=true; G.add(m); G.userData["ox"+ch]=m; });
      SPOT.ox=[ox[0]+OX,1.4,ox[1]-2.6+OZ]; }
    { const pg=[11.6,8.2]; SPOT.pgC=[pg[0]+OX,pg[1]+OZ]; busy.push([pg[0],pg[1],4]); disc(pg[0],pg[1],3.4,0xf1dca0);
      for(let i=0;i<16;i++){ const a=i/16*6.283; if(i===12||i===13) continue; mesh(new THREE.CylinderGeometry(.08,.08,.6,6), [0xff7aa8,0xffd23f,0x7fd3ff,0x86dc7c][i%4], pg[0]+Math.cos(a)*3.5,.3,pg[1]+Math.sin(a)*3.5); }
      SPOT.pg=[pg[0]+OX,1.4,pg[1]+OZ]; }
    { const cx=-2.9, cz=2.9; const ch=new THREE.Group(); ch.position.set(cx+OX,0,cz+OZ); ch.rotation.y=Math.PI*.75; const bx=new THREE.Mesh(new THREE.BoxGeometry(1.1,.62,.75), MC(0xb07a4a)); bx.position.y=.31; ch.add(bx);
      const lid=new THREE.Group(); lid.position.set(0,.62,-.37); const lm=new THREE.Mesh(new THREE.BoxGeometry(1.14,.28,.79), MC(0xc98c55)); lm.position.set(0,.14,.37); lid.add(lm); ch.add(lid);
      [-.45,.45].forEach(x=>{ const b=new THREE.Mesh(new THREE.BoxGeometry(.1,.95,.8), MC(0xffd23f)); b.position.set(x,.45,0); ch.add(b); });
      ch.traverse(m=>{ if(m.isMesh) m.castShadow=true; }); G.add(ch); G.userData.chest=ch; G.userData.chestLid=lid; cols.push([cx+OX,cz+OZ,.7]); busy.push([cx,cz,1.3]); SPOT.chest=[cx+OX,1.4,cz+OZ]; }
    // 동네 섬 · 새 동네 · 밭 섬
    const HN=hoodCount();
    HOODS.slice(0,HN).forEach(([nm,k],i)=>{ hood(D[k][0],D[k][1],nm,k); link(i<3?D.plaza:(i===3?D.d1:i===4?D.d2:D.d3), i<3?17.6:HOODR, D[k], HOODR); });
    if(HN<6){ const [nm,k]=HOODS[HN], c=D[k], I=land(c[0],c[1],6,2.2), from=HN===3?D.d1:HN===4?D.d2:D.d3;   /* 🚧 다음 동네 자리 */
      kk("isle","resource_lumber",c[0]+1.4,c[1],{s:1.6,chunk:"nu",col:.8}); kk("isle","flag_yellow",c[0]-1.6,c[1]+.6,{s:1.6,chunk:"nu"}); busy.push([c[0],c[1],3]);
      for(let i=0;i<6;i++){ const p=new THREE.Mesh(new THREE.PlaneGeometry(LOT,LOT), MC(PADE)); p.rotation.x=-Math.PI/2; p.position.set(c[0]+OX+(i%3-1)*2.6, .008, c[1]+OZ+(i<3?-2.3:2.3)); G.add(p); }
      link(from,HOODR,c,6); SPOT.nu=[c[0]+OX,1.4,c[1]+OZ]; SPOT.nuName=nm; trees(I,10,"nu"); }
    { const F=land(D.farm[0],D.farm[1],9.4,1.3); disc(D.farm[0],D.farm[1],1.8,PATH);
      for(let gx=-2;gx<=2;gx++) for(let gz=-2;gz<=2;gz++){ if(Math.abs(gx)+Math.abs(gz)<=1 || Math.hypot(gx,gz)>2.9) continue; const x=D.farm[0]+gx*2.3, z=D.farm[1]+gz*2.3, col=[0xffd23f,0xff9a3d,0x7fd36a,0xff6b6b][(gx+gz+8)%4];
        const s=new THREE.Mesh(new THREE.BoxGeometry(1.9,.12,1.9), MC(0x8a5a34)); s.position.set(x+OX,.06,z+OZ); s.receiveShadow=true; G.add(s); busy.push([x,z,1.4]);
        for(let a=-1;a<=1;a++) for(let b=-1;b<=1;b++){ const px=x+a*.55, pz=z+b*.55; mesh(new THREE.ConeGeometry(.08,.28,5), 0x5db95a, px,.25,pz,{nocast:1}); mesh(new THREE.SphereGeometry(.12,8,6), col, px,.42,pz,{nocast:1}); } }
      kk("isle","building_windmill_yellow",D.farm[0],D.farm[1]-6.6,{s:2.2,chunk:"f",col:1.0,solo:1}); busy.push([D.farm[0],D.farm[1]-6.6,2.4]); link(D.plaza,17.6,D.farm,9.4); trees(F,30,"f"); SPOT.farm=[D.farm[0]+OX,1.6,D.farm[1]+OZ]; }
    trees(C,140,"m");   /* 다리를 다 놓은 뒤 (다리 끝은 비움) */
    // 동네 땅 · 집 (내 집 ⭐)
    drawLots(); ISL.filter(I=>I.R===HOODR).forEach((I,i)=>trees(I,26,HOODS[i][1]));
    if(myHouse){ const dx=Math.sin(myHouse.face), dz=Math.cos(myHouse.face); SPOT.home=[myHouse.x+OX+dx*1.25,1.3,myHouse.z+OZ+dz*1.25]; SPOT.homeIn=[myHouse.x+OX+dx*1.0,myHouse.z+OZ+dz*1.0]; }
    // 풀포기 · 들꽃
    { const gs=[]; ISL.forEach(I=>{ for(let k=0;k<I.R*I.R*1.2;k++){ const a=rnd()*6.28, r=Math.sqrt(rnd())*rr(I,a)*.95, x=I.cx+Math.cos(a)*r, z=I.cz+Math.sin(a)*r; if(water(x,z) || onPave(x,z,.1)) continue; gs.push([x+OX,z+OZ,rnd()]); } });
      const geo=new THREE.ConeGeometry(.05,.24,3); geo.translate(0,.11,0); const im=new THREE.InstancedMesh(geo, MC(0x5aa845), gs.length*3), d=new THREE.Object3D(); let k=0;
      gs.forEach(([x,z,r])=>{ for(let j=0;j<3;j++){ d.position.set(x+(j-1)*.06,0,z+(j%2)*.04); d.rotation.set((j-1)*.35,r*6,0); d.scale.setScalar(.8+r*.6); d.updateMatrix(); im.setMatrixAt(k++, d.matrix); } }); G.add(im);
      const fl=gs.filter(g=>g[2]<.45), fm=new THREE.InstancedMesh(new THREE.IcosahedronGeometry(.075,0), MC(0xffffff), fl.length), col=new THREE.Color(); fl.forEach(([x,z,r],i)=>{ d.position.set(x+.15,.08,z-.1); d.rotation.set(0,r*6,0); d.scale.setScalar(1); d.updateMatrix(); fm.setMatrixAt(i,d.matrix); fm.setColorAt(i,col.set([0xff7aa8,0xffd23f,0xffffff,0xb28dff][Math.floor(r*97)%4])); }); G.add(fm); }
    for(let i=0;i<10;i++){ const a=i/10*6.283+0.3, d=80+rnd()*30; kk("nature",["mountain_A_grass_trees","mountain_B_grass_trees","hills_A_trees","hills_C_trees"][i%4],Math.cos(a)*d,Math.sin(a)*d-20,{s:1.4+rnd(),y:-0.76,chunk:"far",cast:false}); }
    merge(); walkmap();
    G.children.forEach(o=>{ if(!o.userData.solo) o.userData.noFade=1; });
    G.userData.at=Date.now(); onB.forEach(f=>{ try{ f(); }catch(e){ console.warn(e); } }); try{ TOON.scan(G); }catch(e){} dirty=true; }
  /* 다시 짓기 (땅을 옮겼을 때) */
  function rebuild(){ while(G.children.length){ const o=G.children.pop(); o.traverse(m=>{ if(m.isMesh && m.geometry && !Object.values(KK.R).some(R=>Object.values(R.G).indexOf(m.geometry)>=0)) m.geometry.dispose(); }); }
    [cols,bridges,ISL,paved,busy,lots].forEach(a=>a.length=0); Object.keys(SPOT).forEach(k=>delete SPOT[k]); seed=7; G.userData={}; build(); }
  /* ── 걸을 수 있는 칸 ── */
  function onBridge(x,z){ return bridges.some(([ax,az,bx,bz,w])=>{ const dx=bx-ax, dz=bz-az, L2=dx*dx+dz*dz, t=Math.max(0,Math.min(1,((x-ax)*dx+(z-az)*dz)/L2)), px=ax+dx*t, pz=az+dz*t; return Math.hypot(x-px,z-pz)<=w; }); }
  function walkmap(){ W.fill(0); for(let gx=0;gx<N;gx++) for(let gz=0;gz<N;gz++){ const x=gx+.5, z=gz+.5, lx=x-OX, lz=z-OZ; let ok=ISL.some(I=>inIsle(I,lx,lz,.45)) && !water(lx,lz);
      if(onBridge(x,z)) ok=true;
      if(ok && lots.some(L=>L.owner && Math.abs(lx-L.x)<.95 && Math.abs(lz-L.z)<.95)) ok=false;   // 집 자리
      if(ok && cols.some(([cx,cz,r])=>Math.hypot(x-cx,z-cz)<r)) ok=false;
      W[gx*N+gz]=ok?1:0; }
    if(SPOT.homeIn){ const a=[Math.floor(SPOT.homeIn[0]),Math.floor(SPOT.homeIn[1])]; W[a[0]*N+a[1]]=1; SPOT.door=a; }
    ensureDoors(); }
  /* (v528) 사용자: "나가는 길에 집이 있는 형태는 절대 안 돼 — 이러지도 저러지도 못해"
     → 모든 집 문 앞 칸에서 광장까지 걸어갈 수 있는지 길찾기로 확인 · 막혔으면 문에서 길 쪽으로 곧게 길을 틈 (집은 늘 길을 봄) */
  function reachFrom(sx,sz){ const seen=new Uint8Array(N*N), Q=[sx*N+sz]; if(!W[sx*N+sz]) return seen; seen[sx*N+sz]=1;
    for(let h=0;h<Q.length;h++){ const v=Q[h], x=Math.floor(v/N), z=v%N; for(const [a,b] of [[1,0],[-1,0],[0,1],[0,-1]]){ const nx=x+a, nz=z+b; if(nx<0||nz<0||nx>=N||nz>=N) continue; const k=nx*N+nz; if(seen[k]||!W[k]) continue; seen[k]=1; Q.push(k); } } return seen; }
  function doorCellOf(L){ const dx=Math.sin(L.face), dz=Math.cos(L.face); for(let s=1.15;s<=3.2;s+=.25){ const x=Math.floor(L.x+OX+dx*s), z=Math.floor(L.z+OZ+dz*s); if(Math.abs(x+.5-L.x-OX)<.95 && Math.abs(z+.5-L.z-OZ)<.95) continue; return [x,z]; } return [Math.floor(L.x+OX+dx*1.5), Math.floor(L.z+OZ+dz*1.5)]; }
  function plazaCell(){ for(let r=3;r<8;r++){ const x=OX, z=OZ+r; if(W[x*N+z]) return [x,z]; } return [OX,OZ+4]; }
  function ensureDoors(){ const P=plazaCell(); let R=reachFrom(P[0],P[1]); const fixed=[];
    lots.filter(L=>L.owner).forEach(L=>{ const d=doorCellOf(L); L.door=d; if(R[d[0]*N+d[1]]) return;
      const dx=Math.sin(L.face), dz=Math.cos(L.face); for(let s=1.0;s<=6;s+=.3){ const x=Math.floor(L.x+OX+dx*s), z=Math.floor(L.z+OZ+dz*s); if(x<0||z<0||x>=N||z>=N) break; if(Math.abs(x+.5-L.x-OX)<.95 && Math.abs(z+.5-L.z-OZ)<.95) continue; if(!W[x*N+z]) (G.userData.carved=G.userData.carved||[]).push([x,z]); W[x*N+z]=1; if(R[x*N+z]) break; }
      fixed.push(L.id); R=reachFrom(P[0],P[1]); });
    G.userData.doorFix=fixed; if(myHouse && myHouse.door){ SPOT.door=myHouse.door; } return fixed; }
  function stuckDoors(){ const P=plazaCell(), R=reachFrom(P[0],P[1]); return lots.filter(L=>L.owner && L.door && !R[L.door[0]*N+L.door[1]]).map(L=>L.id); }
  const blocked=(x,z)=>x<0||z<0||x>=N||z>=N||!W[x*N+z];
  /* ── 장소 ── */
  const PLC={key:"isle", N, g:G, h:3, name:"🏝 우리 마을", blocked, start:[OX,OZ+3], pitch:.55, follow:true, sky:0xa6dcf5};
  function doorCell(){ return SPOT.door || [OX,OZ+3]; }
  /* 이름 확인 — 학원 전체가 같이 쓰므로 PLAYER·빈 이름은 들어갈 수 없음 */
  function nameOk(){ let n=""; try{ const k=kidInfo(); n=(k && k.n)||""; }catch(e){} if(!n){ try{ n=(localStorage.getItem("hyeng_nick")||"").trim(); }catch(e){} }
    n=String(n).replace(/^👤\s*/,"").trim(); return !!n && !/^player\d*$/i.test(n) && n!=="친구"; }
  function gate(){ info('<div class="iBig">🏝</div><b>우리 마을에 들어가려면<br>내 이름이 필요해요</b><br><small>학원 친구들이 다 같이 사는 마을이에요.<br>게임 설정에서 <b>내 이름</b>을 정하거나, 공용 패드는 「나는 누구?」에서 이름을 골라 주세요.</small>', "알겠어요", null); }
  /* 섬 그림은 처음 나갈 때 받음 (처음 열기를 가볍게) */
  function ready(){ return Promise.all([KK.load("isle"), KK.load("city"), KK.load("nature")]); }
  function enter(o){ if(!ON) return false; if(!nameOk()){ gate(); return "gate"; }
    const run=async ()=>{ await loadLots(); if(G.userData.built && Date.now()-(G.userData.at||0)>20000) rebuild(); build(); if(await autoClaim()) rebuild();
      const d=doorCell(); go("isle", d, null, Object.assign({from:SPOT.homeIn||null}, o||{})); setTimeout(()=>faceOut(), 260); };
    if(!(KK.R.isle && KK.R.city && KK.R.nature)) toast("🏝 우리 마을로 가는 중…", 1500); ready().then(run); return true; }
  /* 마당·시장·광산·타워에서 돌아오기 — 그곳으로 가는 다리·건물 앞에 */
  function back(from){ if(!nameOk()){ gate(); return; } const near={farm:"farm", market:"market", mine:"mine", tower:"tower"}[from]||"market";
    const run=async ()=>{ if(!G.userData.built){ await loadLots(); } build(); const s=SPOT[near]; let at=s ? [Math.floor(s[0]), Math.floor(s[2])] : [OX,OZ+3]; if(blocked(at[0],at[1])){ const L=[]; for(let r=1;r<8 && !L.length;r++) for(let dx=-r;dx<=r;dx++) for(let dz=-r;dz<=r;dz++) if(!blocked(at[0]+dx,at[1]+dz)) L.push([at[0]+dx,at[1]+dz]); L.sort((a,b)=>Math.hypot(a[0]-OX,a[1]-OZ)-Math.hypot(b[0]-OX,b[1]-OZ)); if(L.length) at=L[0]; }
      go("isle", at); };
    if(KK.R.isle && KK.R.city && KK.R.nature) run(); else ready().then(run); }
  /* ── 조이스틱 · 점프 ── */
  const J={on:false, x:0, y:0, id:null, home:null, key:{}, vy:0, y0:0, air:false};
  function ui(){ if($("ijoy")) return; const d=document.createElement("div"); d.id="iUI"; d.innerHTML='<div id="ijoy"><i id="iknob"></i></div><button id="ijump" aria-label="점프"><b>⬆</b><span>점프</span></button>'; document.body.appendChild(d);
    const joy=$("ijoy"), kn=$("iknob");
    const set=(e)=>{ const r=joy.getBoundingClientRect(), cx=r.left+r.width/2, cy=r.top+r.height/2, R=r.width*.36; let dx=e.clientX-cx, dy=e.clientY-cy; const L=Math.hypot(dx,dy); if(L>R){ dx=dx/L*R; dy=dy/L*R; } J.x=dx/R; J.y=dy/R; kn.style.transform="translate(calc(-50% + "+dx+"px), calc(-50% + "+dy+"px))"; };
    joy.addEventListener("pointerdown", e=>{ e.preventDefault(); e.stopPropagation(); J.on=true; J.id=e.pointerId; try{ joy.setPointerCapture(e.pointerId); }catch(_){} set(e); hero.path=[]; hero.then=null; });
    joy.addEventListener("pointermove", e=>{ if(J.on && e.pointerId===J.id){ e.preventDefault(); set(e); } });
    const up=e=>{ if(e.pointerId!==J.id) return; J.on=false; J.x=J.y=0; kn.style.transform="translate(-50%,-50%)"; };
    joy.addEventListener("pointerup", up); joy.addEventListener("pointercancel", up);
    $("ijump").addEventListener("pointerdown", e=>{ e.preventDefault(); e.stopPropagation(); jump(); });
    addEventListener("keydown", e=>{ if(place!==PLC) return; J.key[e.key.toLowerCase()]=1; if(e.key===" "){ jump(); e.preventDefault(); } });
    addEventListener("keyup", e=>{ J.key[e.key.toLowerCase()]=0; }); }
  function jump(){ if(place!==PLC || J.air || F.st!=="idle") return; J.air=true; J.vy=5.2; try{ SND.pop && SND.pop(); }catch(e){} }
  const SPD=3.4;
  function tick(dt){ if(place!==PLC) return false; let anim=false; const p=hero.g.position;
    let jx=J.x, jy=J.y; const k=J.key; if(k.arrowleft||k.a) jx=-1; if(k.arrowright||k.d) jx=1; if(k.arrowup||k.w) jy=-1; if(k.arrowdown||k.s) jy=1;
    const busy=F.st!=="idle" || trip.busy || sheetOpen() || !!dlg || (window.IPLAY && IPLAY.frozen());
    const m=Math.hypot(jx,jy);
    if(m>.12 && !busy){ hero.path=[]; hero.then=null; if(hero.slide && !hero.slide.then) hero.slide=null; const fx=-Math.sin(yaw), fz=-Math.cos(yaw), rx=Math.cos(yaw), rz=-Math.sin(yaw), mx=rx*jx+fx*(-jy), mz=rz*jx+fz*(-jy), L=Math.hypot(mx,mz)||1, sp=SPD*Math.min(1,m)*dt;
      const nx=p.x+mx/L*sp, nz=p.z+mz/L*sp, okc=(x,z)=>!blocked(Math.floor(x),Math.floor(z));
      if(okc(nx,nz)){ p.x=nx; p.z=nz; } else if(okc(nx,p.z)){ p.x=nx; } else if(okc(p.x,nz)){ p.z=nz; }
      hero.face=Math.atan2(mx,mz); hero.cx=Math.floor(p.x); hero.cz=Math.floor(p.z); hero.moving=true; hero.joy=true; anim=true;
      /* (v528) 타워처럼 — 앞으로 밀면 카메라가 천천히 등 뒤로 (손으로 돌린 뒤 1.5초는 그대로) */
      if(performance.now()-(CAM.dragAt||0)>1500){ const want=hero.face+Math.PI, d=((want-yaw)%(2*Math.PI)+3*Math.PI)%(2*Math.PI)-Math.PI, k=Math.min(1, dt*1.8*Math.max(0, -jy-.3)); if(k>0){ yaw+=d*k; yawTo=yaw; } } }
    else if(hero.joy){ hero.joy=false; if(!hero.path.length) hero.moving=false; anim=true; }
    if(J.air){ J.vy-=16*dt; p.y=Math.max(0, p.y+J.vy*dt); if(p.y<=0 && J.vy<0){ p.y=0; J.air=false; } hero.act=J.air?"air":(hero.act==="air"?"idle":hero.act); anim=true; }
    // 그림자 상자는 나를 따라감
    const s=sun.shadow.camera; sun.position.set(p.x-14, 26, p.z-7); sun.target.position.set(p.x,0,p.z); if(s.right!==16){ s.left=-16; s.right=16; s.top=16; s.bottom=-16; s.near=1; s.far=80; s.updateProjectionMatrix(); }
    if(!hero.joy && hero.moving && hero.path && hero.path.length && performance.now()-(CAM.dragAt||0)>1500){ const want=hero.face+Math.PI, d=((want-yaw)%(2*Math.PI)+3*Math.PI)%(2*Math.PI)-Math.PI; yaw+=d*Math.min(1,dt*.9); yawTo=yaw; }
    const st=G.userData.star; if(st){ st.rotation.y+=dt*1.5; st.position.y=3.1+Math.sin(performance.now()*.003)*.12; anim=true; }
    const fi=G.userData.fire; if(fi){ const t=performance.now()*.012; fi[0].scale.set(1,1+Math.sin(t)*.12,1); fi[1].scale.set(1,1+Math.cos(t*1.3)*.15,1); }
    try{ if(window.IPLAY && IPLAY.tick(dt)) anim=true; }catch(e){ console.warn(e); }
    return anim; }
  function show(on){ ui(); camUI(); document.body.classList.toggle("isleOn", !!on); if(on) camHint(); }
  /* ── 이름표 (가까이 가면) ── */
  function labels(){ const L=[];
    if(SPOT.home) L.push({k:"home", ic:"⭐", t:"내 집", p:SPOT.home, r:3, act:()=>walkTo(SPOT.door[0],SPOT.door[1],()=>enterHome())});
    if(SPOT.board) L.push({k:"board", ic:"📋", t:"땅 고르기", p:SPOT.board, r:3.4, act:()=>openLots()});
    if(SPOT.market) L.push({k:"mk", ic:"🏘", t:"시장 · 마을 사람", p:SPOT.market, r:3.2, act:()=>tripTo("village")});
    if(SPOT.lake) L.push({k:"lake", ic:"🎣", t:"같이 낚시", p:SPOT.lake, r:3.2, act:()=>{ const L=lake(); fishTap(Math.floor(L.x-1.5), Math.floor(L.z), L.x-1.4, L.z); }});
    if(SPOT.farm) L.push({k:"farm", ic:"🌱", t:"내 밭 (밭 섬)", p:SPOT.farm, r:4.5, act:()=>tripTo("yard")});
    if(SPOT.school) L.push({k:"school", ic:"🏫", t:"학교 · 공부하기", p:SPOT.school, r:3.4, act:()=>ask("🏫 공부하러 갈까요?<br><small>Daily 30 을 하면 🪱 미끼를 받아요</small>", ()=>{ location.href="../index.html"; })});
    if(SPOT.tower) L.push({k:"tower", ic:"🗼", t:"하늘 타워", p:SPOT.tower, r:3.6, act:()=>towerAsk()});
    if(SPOT.mine) L.push({k:"mine", ic:"⛏", t:"광산", p:SPOT.mine, r:3.4, act:()=>tripTo("mine")});
    if(SPOT.nu) L.push({k:"nu", ic:"🚧", t:(SPOT.nuName||"새 동네")+" (친구가 오면)", p:SPOT.nu, r:4, act:()=>toast("🚧 학원 친구가 늘면 <b>새 동네</b>가 여기에 생겨요!", 2600)});
    if(SPOT.camp) L.push({k:"camp", ic:"🔥", t:"모닥불", p:SPOT.camp, r:2.6, act:()=>{ hero.act="sit"; hero.actT=0; toast("🔥 따뜻해요 — 친구들이 모이는 곳이에요", 2200); }});
    return L; }
  function tripTo(key){ const at=key==="yard" ? [DOOR[0],DOOR[1]] : key==="village" ? [V_GATE[0]+1,V_GATE[1]] : key==="mine" ? [M_GATE[0]-1,M_GATE[1]] : null; go(key, at); }
  /* (v525) 사용자: "화면을 돌릴 수도 없고 · 집이 동그랗게 있어서 보이지도 않아 · 화면의 자유가 없는데"
     → 빈 곳을 끌면 돌리기(좌우)·기울이기(위아래) · 두 손가락 벌리기 = 가까이/멀리 · 집에서 나오면 카메라가 내 뒤에서 마을 쪽을 봄 */
  const CAM={pitch:.6, zoom:1, drag:null, pts:new Map(), pinch:0, told:false};
  function faceOut(){ if(!myHouse) return; const a=myHouse.face+Math.PI; yaw=yawTo=a; try{ camSnap=true; }catch(e){} dirty=true; }
  function camUI(){ const cv=$("cv"); if(cv.dataset.isleCam) return; cv.dataset.isleCam=1;
    cv.addEventListener("pointerdown", e=>{ if(place!==PLC) return; CAM.pts.set(e.pointerId,[e.clientX,e.clientY]); if(CAM.pts.size===1) CAM.drag={x:e.clientX,y:e.clientY,moved:0}; else { CAM.drag=null; const P=[...CAM.pts.values()]; CAM.pinch=Math.hypot(P[0][0]-P[1][0],P[0][1]-P[1][1]); } });
    cv.addEventListener("pointermove", e=>{ if(place!==PLC || !CAM.pts.has(e.pointerId)) return; CAM.pts.set(e.pointerId,[e.clientX,e.clientY]);
      if(CAM.pts.size>=2){ const P=[...CAM.pts.values()], d=Math.hypot(P[0][0]-P[1][0],P[0][1]-P[1][1]); if(CAM.pinch>0){ CAM.zoom=Math.max(.55, Math.min(2.4, CAM.zoom*CAM.pinch/d)); } CAM.pinch=d; dirty=true; return; }
      const D=CAM.drag; if(!D) return; const dx=e.clientX-D.x, dy=e.clientY-D.y; D.x=e.clientX; D.y=e.clientY; D.moved+=Math.abs(dx)+Math.abs(dy); if(D.moved<10) return;
      yaw-=dx*.009; yawTo=yaw; CAM.dragAt=performance.now(); CAM.pitch=Math.max(.28, Math.min(1.15, CAM.pitch+dy*.005)); dirty=true;
      if(!CAM.told){ CAM.told=true; try{ localStorage.setItem("hyeng_isle_cam","1"); }catch(_){} } });
    const end=e=>{ CAM.pts.delete(e.pointerId); if(CAM.pts.size<2) CAM.pinch=0; if(!CAM.pts.size) CAM.drag=null; };
    ["pointerup","pointercancel","pointerleave"].forEach(ev=>cv.addEventListener(ev,end));
    cv.addEventListener("wheel", e=>{ if(place!==PLC) return; e.preventDefault(); CAM.zoom=Math.max(.55, Math.min(2.4, CAM.zoom*(e.deltaY>0?1.1:.9))); dirty=true; }, {passive:false});
    addEventListener("keydown", e=>{ if(place!==PLC) return; if(e.key==="q"||e.key==="Q"){ yawTo=yaw+Math.PI/4; } if(e.key==="e"||e.key==="E"){ yawTo=yaw-Math.PI/4; } }); }
  function camHint(){ let t=false; try{ t=localStorage.getItem("hyeng_isle_cam")==="1"; }catch(e){} if(!t) setTimeout(()=>{ if(place===PLC) toast("👆 화면을 <b>끌면</b> 돌아가요 · 두 손가락으로 <b>벌리면</b> 가까이", 3200); }, 900); }
/* ── (v528) 🏡 땅 고르기 — 사용자: "아이들이 땅을 정할 수 있고 집의 위치를 정할 수 있는 혜택" ──
     게시판 → 동네 지도(1동·2동·3동) → 빈 땅 누르기 → 「여기로 할래요」 → 내 집이 그 땅으로 옮겨감
     · 바다 앞 ⭐ 좋은 자리 = 공부한 날 5일부터 · 친구 땅은 이름이 보임 · (2단계) 서버에서 먼저 고른 사람만 (트랜잭션) */
  let lotHood="1동", lotSel=null;
  function lotCSS(){ if($("lotP")) return; const st=document.createElement("style"); st.textContent=`
#lotP{position:fixed;inset:0;z-index:20;display:none;background:rgba(30,18,40,.42);align-items:flex-end;justify-content:center}
#lotP.on{display:flex}
#lotP .lb{width:min(560px,100%);max-height:92vh;overflow:auto;background:#fff8ea;border:3px solid #3b2433;border-bottom:0;border-radius:26px 26px 0 0;padding:12px 14px calc(14px + env(safe-area-inset-bottom));font-family:var(--kr);color:#3b2433}
#lotP h3{margin:2px 4px 8px;font-weight:400;font-size:20px;display:flex;align-items:center;gap:8px} #lotP h3 small{font-size:12.5px;color:#9a7e63;flex:1}
#lotP .x{width:38px;height:38px;border-radius:50%;border:3px solid #3b2433;background:#fffdf7;box-shadow:0 3px 0 #3b2433;font-size:16px;color:#3b2433}
.lotT{display:flex;gap:6px;margin-bottom:8px}.lotT button{flex:1;height:42px;border-radius:14px;border:3px solid #3b2433;background:#fffdf7;font:16px var(--kr);color:#3b2433;box-shadow:0 3px 0 #3b2433}.lotT button.on{background:#ffd23f}
.lotT button em{font-style:normal;font-size:11.5px;color:#7a5b3a;margin-left:3px}
#lotMap{display:block;width:100%;height:auto;touch-action:manipulation}
.lotK{display:flex;flex-wrap:wrap;gap:6px 12px;font-size:12.5px;margin:6px 4px 8px;color:#6a5040}.lotK i{display:inline-block;width:14px;height:14px;border-radius:4px;border:2px solid #3b2433;vertical-align:-2px;margin-right:4px}
.lotSel{display:flex;align-items:center;gap:10px;background:#fffdf7;border:3px solid #3b2433;border-radius:18px;padding:8px 10px;box-shadow:0 3px 0 #3b2433;min-height:62px}
.lotSel b{font-weight:400;font-size:17px;display:block} .lotSel small{font-size:12.5px;color:#9a7e63}
.lotSel .go{margin-left:auto;height:46px;border-radius:14px;border:3px solid #3b2433;padding:0 16px;font:17px var(--kr);color:#fff;background:linear-gradient(180deg,#86dc7c,#4caf50);box-shadow:0 3px 0 #3b2433;text-shadow:0 1px 0 rgba(30,80,30,.45);white-space:nowrap}
.lotSel .go[disabled]{filter:grayscale(.8);opacity:.6}`; document.head.appendChild(st);
    const d=document.createElement("div"); d.id="lotP"; d.innerHTML='<div class="lb"><h3>🏡 땅 고르기<small>빈 땅을 누르면 내 집이 그리로 옮겨가요</small><button class="x" id="lotX" aria-label="닫기">✕</button></h3><div class="lotT" id="lotT"></div><svg id="lotMap" viewBox="-114 -114 228 228"></svg>'
      +'<div class="lotK"><span><i style="background:#ffd23f"></i>내 집</span><span><i style="background:#9fd884"></i>친구 집</span><span><i style="background:#fff;border-style:dashed"></i>빈 땅</span><span><i style="background:#fff3bf"></i>⭐ 바다 앞 좋은 자리</span></div><div class="lotSel" id="lotSel"></div></div>';
    document.body.appendChild(d);
    d.addEventListener("click", e=>{ if(e.target===d || e.target.id==="lotX"){ d.classList.remove("on"); return; }
      const tb=e.target.closest("[data-hood]"); if(tb){ lotHood=tb.dataset.hood; lotSel=null; drawLotP(); return; }
      const g=e.target.closest("[data-lot]"); if(g){ lotSel=g.dataset.lot; drawLotP(); try{ SND.pop && SND.pop(); }catch(_){} return; }
      if(e.target.id==="lotGo") pickLot(lotSel); });
    ["pointerdown","pointerup"].forEach(ev=>d.addEventListener(ev, e=>e.stopPropagation())); }
  function lotState(L){ const sd=studyDays(); return L.me ? "me" : L.owner ? "friend" : (L.prem && sd<PREM_DAYS) ? "lock" : "free"; }
  function drawLotP(){ const H=HOODS.slice(0,hoodCount()).map(h=>h[0]), cnt=h=>lots.filter(L=>L.hood===h && !L.owner).length;
    $("lotT").innerHTML=H.map(h=>'<button data-hood="'+h+'" class="'+(h===lotHood?"on":"")+'">'+h+(myHouse&&myHouse.hood===h?" ⭐":"")+'<em>빈 '+cnt(h)+'</em></button>').join("");
    const hc=D[(HOODS.find(h=>h[0]===lotHood)||HOODS[0])[1]], k=100/(HOODR+.6); let s='<circle r="'+(HOODR*k)+'" fill="#86c96a" stroke="#3b2433" stroke-width="3"/>';
    [[1,0],[-1,0],[0,1],[0,-1]].forEach(([ux,uz])=>{ s+='<line x1="0" y1="0" x2="'+(ux*8.4*k)+'" y2="'+(uz*8.4*k)+'" stroke="#dcbf86" stroke-width="'+(1.45*k)+'" stroke-linecap="round"/>'; });
    s+='<circle r="'+(1.5*k)+'" fill="#d2c7b0"/>';
    const toP=[-hc[0],-hc[1]], Lp=Math.hypot(toP[0],toP[1]); s+='<text x="'+(toP[0]/Lp*106)+'" y="'+(toP[1]/Lp*106+3)+'" font-size="9" text-anchor="middle" fill="#3b2433">⛲ 광장 쪽</text>';
    lots.filter(L=>L.hood===lotHood).forEach(L=>{ const x=(L.x-hc[0])*k, y=(L.z-hc[1])*k, w=LOT*k*.94, st=lotState(L), sel=lotSel===L.id;
      const fill=st==="me"?"#ffd23f":st==="friend"?"#9fd884":L.prem?"#fff3bf":"#fff", dash=(st==="free"||st==="lock")?' stroke-dasharray="4 3"':'';
      s+='<g data-lot="'+L.id+'" style="cursor:pointer"><rect x="'+(x-w/2)+'" y="'+(y-w/2)+'" width="'+w+'" height="'+w+'" rx="4" fill="'+fill+'" stroke="'+(sel?"#ff5d6c":"#3b2433")+'" stroke-width="'+(sel?4:2)+'"'+dash+'/>';
      const ic=st==="me"?"⭐":st==="friend"?"🏠":st==="lock"?"🔒":L.prem?"⭐":"＋";
      s+='<text x="'+x+'" y="'+(y+(st==="friend"?-1:4))+'" font-size="'+(st==="free"&&!L.prem?13:10)+'" text-anchor="middle" fill="#3b2433">'+ic+'</text>';
      if(st==="friend"||st==="me") s+='<text x="'+x+'" y="'+(y+10)+'" font-size="6.5" text-anchor="middle" fill="#3b2433">'+(st==="me"?"내 집":esc(L.owner))+'</text>';
      s+='</g>'; });
    $("lotMap").innerHTML=s;
    const L=lots.find(L=>L.id===lotSel), sd=studyDays();
    $("lotSel").innerHTML = !L ? '<div><b>빈 땅을 눌러 보세요</b><small>'+(myHouse?'지금 내 집: '+myHouse.hood+' '+myHouse.n+'번 땅':'')+'</small></div>'
      : '<div><b>'+L.hood+' '+L.n+'번 땅'+(L.prem?' · ⭐ 바다 앞':'')+'</b><small>'+(lotState(L)==="friend"?esc(L.owner)+' 의 집이에요':lotState(L)==="me"?'지금 내 집이에요':lotState(L)==="lock"?'공부한 날 '+PREM_DAYS+'일부터 (지금 '+sd+'일) — Daily 30 을 해요':'여기로 이사할 수 있어요')+'</small></div>'
        +'<button class="go" id="lotGo"'+(lotState(L)==="free"?'':' disabled')+'>여기로 할래요</button>'; }
  async function openLots(){ lotCSS(); await loadLots(); owners(); if(myHouse) lotHood=myHouse.hood; lotSel=null; drawLotP(); $("lotP").classList.add("on"); }
  function pickLot(id){ const L=lots.find(L=>L.id===id); if(!L || lotState(L)!=="free") return;
    ask("🏡 <b>"+L.hood+" "+L.n+"번 땅</b>으로 이사할까요?"+(L.prem?"<br><small>⭐ 바다 앞 좋은 자리예요</small>":""), async ()=>{
      $("lotP").classList.remove("on"); toast("🚚 이사하는 중…", 1500); const r=await claim(id);
      if(r==="taken"){ toast("😮 방금 친구가 그 땅을 골랐어요 — 다른 땅을 골라 봐요", 2600); await loadLots(); rebuild(); drawLabels(); return; }
      if(r==="err"){ toast("📡 인터넷이 잠깐 안 돼요 — 다시 해 봐요", 2400); return; }
      setTimeout(()=>{ rebuild(); const d=doorCell(); hero.path=[]; hero.moving=false; hero.slide=null; hero.cx=d[0]; hero.cz=d[1]; hero.g.position.set(d[0]+.5,0,d[1]+.5); faceOut(); drawLabels(); placeCamera();
        try{ confetti && confetti(); }catch(e){} toast("🎉 새 집이에요! <b>"+L.hood+" "+L.n+"번 땅</b>", 2600); }, 400); }); }
  /* 🎣 호수 (같이 낚시) — house.html pondCtx 가 씀 */
  const LKD=[10,-.8,5.6,4.5];
  function lake(){ return {x:LKD[0]+OX, z:LKD[1]+OZ, hw:LKD[2]*.72, hd:LKD[3]*.72, wl:-.18, g:G}; }
  function waterCell(x,z){ return water(x+.5-OX, z+.5-OZ); }
  function enterHome(){ const a=!roomBlocked(1,RN-1)?[1,RN-1]:[0,RN-1]; go("room", a, null, {from:()=>[0.05,RN-0.5], door:roomDoor}); }
  const tRay=new THREE.Raycaster(), tN=new THREE.Vector2();
  function houseAt(e){ tN.set(e.clientX/innerWidth*2-1, -(e.clientY/innerHeight)*2+1); tRay.setFromCamera(tN, camera); const objs=lots.filter(L=>L.obj).map(L=>L.obj); const h=tRay.intersectObjects(objs, true)[0]; if(!h) return null; let o=h.object; while(o && !o.userData.lot) o=o.parent; return o ? o.userData.lot : null; }
  function doorOf(L){ return L.door || doorCellOf(L); }
  function visitLot(L){ if(!L || !L.rec) return; if(L.me){ const d=doorCell(); walkTo(d[0],d[1],()=>enterHome()); return; }
    /* (v528) 먼저 묻고 → 바로 놀러 감 (멀리 걸어가다 길이 막혀 아무 일도 안 일어나는 일 없음) */
    ask("🏠 <b>"+esc(L.owner)+"</b> 의 집에 놀러 갈까요?<br><small>좋아요 · 방명록에 스티커를 남길 수 있어요</small>", ()=>{ const d=L.door||doorOf(L); if(d && !blocked(d[0],d[1])){ hero.path=[]; hero.slide=null; hero.g.position.set(d[0]+.5,0,d[1]+.5); hero.cx=d[0]; hero.cz=d[1]; } visitCode(L.rec.c); }); }   /* 나올 때 = 친구 집 문 앞 */
  function tap(e){ if(F.st!=="idle"){ return; } if(window.IPLAY && IPLAY.frozen()){ toast("🧊 얼음! 친구가 와서 풀어 줘야 해요", 1500); return; } const L=houseAt(e); if(L){ visitLot(L); return; }
    const c=cellAt(e); if(!c) return; if(waterCell(c[0],c[1])){ const hp=floorPt(e); fishTap(c[0], c[1], hp&&hp.x, hp&&hp.z); return; } walkTo(c[0], c[1]); }
  /* 단추 모양 (시안 hud3: 굵은 테두리 #3b2433) */
  { const st=document.createElement("style"); st.textContent=`#iUI{display:none} body.isleOn #iUI{display:block}
#ijoy{position:fixed;left:calc(20px + env(safe-area-inset-left));bottom:calc(104px + env(safe-area-inset-bottom));width:128px;height:128px;border-radius:50%;background:rgba(59,36,51,.18);border:3px solid rgba(255,255,255,.92);z-index:3;touch-action:none}
#ijoy::before{content:"";position:absolute;inset:16px;border-radius:50%;border:2px dashed rgba(255,255,255,.55)}
#iknob{position:absolute;left:50%;top:50%;width:56px;height:56px;border-radius:50%;transform:translate(-50%,-50%);background:radial-gradient(circle at 40% 35%,#fff,#efe6d6);border:3px solid #3b2433;box-shadow:0 4px 0 #3b2433;pointer-events:none}
#ijump{position:fixed;right:calc(18px + env(safe-area-inset-right));bottom:calc(108px + env(safe-area-inset-bottom));width:96px;height:96px;border-radius:50%;z-index:3;touch-action:none;
  background:linear-gradient(180deg,#ffe58f 0%,#ffbf33 55%,#ffa51f 100%);border:3.5px solid #3b2433;box-shadow:inset 0 -7px 0 rgba(200,110,10,.45),inset 0 5px 0 rgba(255,255,255,.55),0 5px 0 #3b2433;color:#5a3000;font-family:var(--kr);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:0}
#ijump b{font-size:30px;line-height:1} #ijump span{font-size:15px}
#ijump:active{transform:translateY(3px);box-shadow:inset 0 -5px 0 rgba(200,110,10,.45),0 2px 0 #3b2433}
body.isleOn #bEmo{bottom:calc(220px + env(safe-area-inset-bottom))}`; document.head.appendChild(st); }
  return {stuckDoors, ensureDoors, reachFrom, plazaCell, doorCellOf, onBuild:f=>onB.push(f), MC, W, ON, CAM, lake, waterCell, claim, loadLots, autoClaim, myKey, hoodCount, houseAt, visitLot, doorOf, SRV:()=>SRV, D, HOODS, LOT, HOODR, inIsle:(x,z)=>ISL.some(I=>inIsle(I,x-OX,z-OZ,.4)), onPave:(x,z)=>onPave(x-OX,z-OZ), busyAt:(x,z,r)=>busy.some(([bx,bz,br])=>Math.hypot(x-OX-bx,z-OZ-bz)<br+(r||0)), faceOut, back, ready, G, PLC, N, OX, OZ, S, build, enter, tick, show, labels, tap, blocked, nameOk, gate, SPOT, lots, rebuild, openLots, pickLot, lotState, studyDays, myHouse:()=>myHouse, W, J, doorCell, enterHome};
})();
window.ISLE=ISLE; PL.isle=ISLE.PLC; LBL_DEF.isle=ISLE.labels; LBL_NEAR.isle=1;
