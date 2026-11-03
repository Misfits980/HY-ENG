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
  const S=1.05, N=196, OX=98, OZ=98;   /* (v536) 하나로 이어진 큰 섬 (ISLE_MAP) · (v550) 3.5배 섬 → 196칸 */
  const MAP=window.ISLE_MAP;
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
    /* (v536) 큰 섬 — 덩어리를 14칸 구역마다 나눔 (화면 밖 구역은 안 그림) */
    const key=pack+"|"+(o.chunk==="far" ? "far" : "g"+Math.floor((x+104)/26)+"_"+Math.floor((z+104)/26)); (bag[key]=bag[key]||[]).push({g, m:M4, cast:o.cast!==false}); return true; }
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
  /* ── (v535) 작은 물건(울타리·꽃·바위·땅 판) = 색마다 한 덩어리로 합침 (그리는 횟수 ↓ — 집 96채여도 가볍게) ── */
  const pbag={};   // "색|f" → [{g,m}] (f = 그림자 안 드리움)
  function prim(geo,col,x,y,z,o){ o=o||{}; const q=new THREE.Quaternion().setFromEuler(new THREE.Euler(o.rx||0,o.ry||0,o.rz||0,"YXZ"));
    const M=new THREE.Matrix4().compose(new THREE.Vector3(x+OX,y,z+OZ), q, new THREE.Vector3(o.sx||1,o.sy||1,o.sz||1)); const k=col+(o.flat?"|f":""); (pbag[k]=pbag[k]||[]).push({g:geo,m:M}); }
  function mergeP(){ Object.keys(pbag).forEach(key=>{ const L=pbag[key], col=+key.split("|")[0], flat=key.indexOf("|f")>0; let nv=0, ni=0;
      L.forEach(e=>{ nv+=e.g.attributes.position.count; ni+=e.g.index ? e.g.index.count : e.g.attributes.position.count; });
      const P=new Float32Array(nv*3), Nn=new Float32Array(nv*3), I=new Uint32Array(ni); let ov=0, oi=0; const v=new THREE.Vector3(), nm=new THREE.Matrix3();
      L.forEach(e=>{ const g=e.g, pa=g.attributes.position, na=g.attributes.normal, ix=g.index; nm.getNormalMatrix(e.m);
        for(let i=0;i<pa.count;i++){ v.fromBufferAttribute(pa,i).applyMatrix4(e.m); P[(ov+i)*3]=v.x; P[(ov+i)*3+1]=v.y; P[(ov+i)*3+2]=v.z; v.fromBufferAttribute(na,i).applyMatrix3(nm).normalize(); Nn[(ov+i)*3]=v.x; Nn[(ov+i)*3+1]=v.y; Nn[(ov+i)*3+2]=v.z; }
        const n=ix ? ix.count : pa.count; for(let i=0;i<n;i++) I[oi+i]=(ix ? ix.getX(i) : i)+ov; ov+=pa.count; oi+=n; });
      const geo=new THREE.BufferGeometry(); geo.setAttribute("position", new THREE.BufferAttribute(P,3)); geo.setAttribute("normal", new THREE.BufferAttribute(Nn,3)); geo.setIndex(new THREE.BufferAttribute(I,1)); geo.computeBoundingSphere();
      let mat=MC(col); if(flat){ mat=mat.clone(); mat.polygonOffset=true; mat.polygonOffsetFactor=-1; mat.polygonOffsetUnits=-4; }   /* (v572) 사용자 사진: 땅에 초록 줄무늬(깊이 겹침) — 바닥에 붙은 판(길·패드)은 땅보다 앞으로 */
      const m=new THREE.Mesh(geo, mat); m.castShadow=!flat; m.receiveShadow=true; G.add(m); delete pbag[key]; }); }
  const GEO={};   // 같은 모양은 한 번만 만듦
  const geo_=(k,f)=>GEO[k]||(GEO[k]=f());
  /* ── (v528) 섬 = 매끈한 땅 한 판 (사용자: "꼭 6각형 타일로 한 이유는?" → 판처럼 보여서 매끈한 땅 + 네모 땅 칸) ── */
  const ISL=[];   // {cx,cz,R,s,holes:[[x,z,rx,rz]]}
  const rr=(I,a)=>I.main ? MAP.edge(a) : I.R*(1+.035*Math.sin(3*a+I.s)+.025*Math.sin(5*a+I.s*2));
  function inIsle(I,x,z,m){ const dx=x-I.cx, dz=z-I.cz; return Math.hypot(dx,dz) < rr(I,Math.atan2(dz,dx))-(m||0); }
  const GRASS=0x86c96a, DIRT=0xa3714a, PATH=0xdcbf86, STONE=0xd2c7b0, PAD=0x9fd884, PADE=0xe0c896;
  function land(cx,cz,R,s,holes,main){ const I={cx,cz,R,s:s||0,holes:holes||[],main:!!main}; ISL.push(I); const sh=new THREE.Shape(), n=72;
    for(let i=0;i<=(main?160:n);i++){ const a=i/(main?160:n)*6.2832, r=rr(I,a); const x=Math.cos(a)*r, y=Math.sin(a)*r; i?sh.lineTo(x,y):sh.moveTo(x,y); }
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
  /* (v535) 사용자: "안 한 것도 다 해 보자" — 🏡 집 모양(A·B)·색 4가지 = 아이가 고름 · 공부한 날만큼 집이 자람 (서버 땅 기록 h·t) */
  const HSH=["A","B","M"], HCOL=["red","blue","yellow","green"], HCOLK={red:"빨강",blue:"파랑",yellow:"노랑",green:"초록"};
  const TIER=[{d:0,s:1.62,t:"작은 집",ic:"🌱"},{d:3,s:1.78,t:"우체통·꽃",ic:"🌷"},{d:10,s:1.92,t:"울타리·덤불",ic:"🏡"},{d:25,s:2.04,t:"깃발·큰 집",ic:"🏰"}];
  const tierOf=d=>{ let t=1; TIER.forEach((T,i)=>{ if(d>=T.d) t=i+1; }); return t; };
  function myStyle(){ return store("hyeng_proto_ihouse")||""; }   /* (v536) 아이마다 (같이 쓰는 패드) · 초기화에 같이 지워짐 */
  function styleOf(L){ const h=(L.me && myStyle()) || (L.rec && L.rec.h) || ""; if(/^[ABM]_(red|blue|yellow|green)$/.test(h)) return h; const k=HC[(L.n*3+L.hood.charCodeAt(0))%HC.length]; return k.replace("building_home_",""); }
  /* (v536) 층 = 집 안에서 연 2·3·4층 (HOMEX) · 친구 = 서버 기록 f · 사용자: "3층 4층 가능성도 · 모던한 하우스도 느낌 있게 정할 수 있게" */
  function floorsLot(L){ if(L.me){ try{ return HOMEX.floors(); }catch(e){ return 1; } } return Math.max(1, Math.min(4, +(L.rec && L.rec.f)||1)); }
  const HCV={red:[0xff6b6b,0xc94545],blue:[0x5aa7ff,0x2f6fc4],yellow:[0xffc93d,0xc9901a],green:[0x5cc46a,0x2f8f3f]};
  /* (v536) 집 조각 = 색을 꼭짓점에 넣어 한 덩어리 (집 하나 = 한 번 그리기) */
  function box(W,w,h,d,col,x,y,z,ry){ (W.userData.parts=W.userData.parts||[]).push([w,h,d,col,x,y,z,ry||0]); }
  const VCM=new THREE.MeshStandardMaterial({vertexColors:true, roughness:.85});
  function flush(W){ const P=W.userData.parts; if(!P || !P.length) return; delete W.userData.parts; let nv=0, ni=0; const B=new THREE.BoxGeometry(1,1,1); nv=B.attributes.position.count*P.length; ni=B.index.count*P.length;
    const pos=new Float32Array(nv*3), nor=new Float32Array(nv*3), colA=new Float32Array(nv*3), idx=new Uint32Array(ni), M4=new THREE.Matrix4(), nm=new THREE.Matrix3(), v=new THREE.Vector3(), c=new THREE.Color(); let ov=0, oi=0;
    P.forEach(([w,h,d,col,x,y,z,ry])=>{ M4.compose(new THREE.Vector3(x,y,z), new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,1,0),ry), new THREE.Vector3(w,h,d)); nm.getNormalMatrix(M4); c.set(col).convertSRGBToLinear();
      const pa=B.attributes.position, na=B.attributes.normal; for(let i=0;i<pa.count;i++){ v.fromBufferAttribute(pa,i).applyMatrix4(M4); pos.set([v.x,v.y,v.z],(ov+i)*3); v.fromBufferAttribute(na,i).applyMatrix3(nm).normalize(); nor.set([v.x,v.y,v.z],(ov+i)*3); colA.set([c.r,c.g,c.b],(ov+i)*3); }
      for(let i=0;i<B.index.count;i++) idx[oi+i]=B.index.getX(i)+ov; ov+=pa.count; oi+=B.index.count; });
    const g=new THREE.BufferGeometry(); g.setAttribute("position",new THREE.BufferAttribute(pos,3)); g.setAttribute("normal",new THREE.BufferAttribute(nor,3)); g.setAttribute("color",new THREE.BufferAttribute(colA,3)); g.setIndex(new THREE.BufferAttribute(idx,1)); g.computeBoundingSphere();
    const m=new THREE.Mesh(g, VCM); m.castShadow=true; m.receiveShadow=true; W.add(m); }
  /* (v550) 여러 조각 → 꼭짓점 색 한 덩어리 (그리기 1번) — [{g, col, m}] · m = Matrix4(없으면 그대로) */
  const VCM2=new THREE.MeshStandardMaterial({vertexColors:true, roughness:.9});
  function vcMerge(L, mat){ const parts=L.map(e=>{ let g=e.g.index ? e.g.toNonIndexed() : e.g.clone(); if(e.m) g.applyMatrix4(e.m); if(!g.attributes.normal) g.computeVertexNormals(); return [g, new THREE.Color(e.col).convertSRGBToLinear()]; });
    let n=0; parts.forEach(([g])=>n+=g.attributes.position.count); const P=new Float32Array(n*3), Nn=new Float32Array(n*3), Cc=new Float32Array(n*3); let o=0;
    parts.forEach(([g,c])=>{ const k=g.attributes.position.count; P.set(g.attributes.position.array.subarray(0,k*3), o*3); Nn.set(g.attributes.normal.array.subarray(0,k*3), o*3); for(let i=0;i<k;i++){ Cc[(o+i)*3]=c.r; Cc[(o+i)*3+1]=c.g; Cc[(o+i)*3+2]=c.b; } o+=k; g.dispose(); });
    const G2=new THREE.BufferGeometry(); G2.setAttribute("position",new THREE.BufferAttribute(P,3)); G2.setAttribute("normal",new THREE.BufferAttribute(Nn,3)); G2.setAttribute("color",new THREE.BufferAttribute(Cc,3)); G2.computeBoundingSphere();
    const m=new THREE.Mesh(G2, mat||VCM2); m.castShadow=true; m.receiveShadow=true; return m; }
  function houseObj(L){ const fl=L.fl||1, sty=L.style, col=sty.slice(2), S2=TIER[(L.tier||1)-1].s;
    if(sty[0]==="M"){ /* 🏢 모던 — 흰 상자 층마다 · 큰 유리창 · 나무 판 · 평평한 지붕 · 맨 위 유리 난간 */
      const W=new THREE.Group(); W.userData.solo=1; W.position.set(L.x+OX,0,L.z+OZ); W.rotation.y=L.face; G.add(W); const k=S2/1.9, bw=1.62*k, bd=1.5*k, FH=.86*k, ac=HCV[col]||HCV.blue;
      for(let i=0;i<fl;i++){ const y=i*FH, off=(i%2?.12:-.08)*k;
        box(W,bw,FH,bd, i%2?0xf1ebe0:0xfbf8f2, off,y+FH/2,0); box(W,bw*.62,FH*.55,.03, 0x7ab8dc, off-bw*.12,y+FH*.55,bd/2+.016); box(W,.04,FH*.55,.035, 0xffffff, off-bw*.12,y+FH*.55,bd/2+.03);   // 큰 창 (하늘빛)
        box(W,bw*.62+.08,.06,.07, ac[0], off-bw*.12,y+FH*.26,bd/2+.035); box(W,bw*.26,FH*.86,.04, 0xc98c55, off+bw*.33,y+FH*.48,bd/2+.02);   // 창 아래 색 띠 · 나무 판
        [-1,1].forEach(a=>box(W,.03,FH*.4,bd*.5, 0x7ab8dc, a*(bw/2+.016)+off,y+FH*.55,0));   // 옆 창
        box(W,bw+.16,.1,bd+.16, 0x8a8094, off,y+FH+.05,0); }
      box(W,.34,FH*.62,.05, ac[0], -bw*.12,FH*.31,bd/2+.035); box(W,bw*.5,.05,.32, ac[1], -bw*.12,FH*.72,bd/2+.16);   // 문 · 차양 (고른 색)
      const top=fl*FH+.08; for(let a=-1;a<=1;a+=2){ box(W,bw+.1,.28,.03, 0xbfe6ff, 0,top+.15,a*(bd/2+.05)); box(W,.03,.28,bd+.1, 0xbfe6ff, a*(bw/2+.05),top+.15,0); }   // 옥상 유리 난간
      box(W,.22,.36,.22, ac[0], bw*.3,top+.18,-bd*.2);   // 옥상 화분 상자
      flush(W); W.userData.lot=L; return W; }
    const W=kk("isle","building_home_"+sty,L.x,L.z,{s:S2,ry:L.face,solo:1}); if(!W) return null; if(fl<=1) return W;
    /* 🏡 오두막 + 층 — 지붕 집을 위로 올리고 아래에 층을 쌓음 */
    const g=KK.R.isle.G["building_home_"+sty], bb=g.boundingBox, sc=S*S2, bw=(bb.max.x-bb.min.x)*sc*.78, bd=(bb.max.z-bb.min.z)*sc*.78, FH=(bb.max.y-bb.min.y)*sc*.36;
    W.position.y=(fl-1)*FH; const ac=HCV[col]||HCV.red;
    for(let i=0;i<fl-1;i++){ const y=i*FH-W.position.y, Bx=new THREE.Group(); Bx.position.set(L.x+OX,y,L.z+OZ); Bx.rotation.y=L.face; W.add(Bx);
      box(Bx,bw,FH,bd, 0xfff1d8, 0,FH/2,0); box(Bx,bw+.08,.07,bd+.08, ac[1], 0,FH,0);
      [-1,1].forEach(a=>{ box(Bx,bw*.24,FH*.42,.03, 0x9fd6f5, a*bw*.24,FH*.55,bd/2+.016); box(Bx,bw*.28,FH*.5,.02, 0xffffff, a*bw*.24,FH*.55,bd/2+.008); });
      if(i===0) box(Bx,.3,FH*.66,.04, 0xa0683c, 0,FH*.33,bd/2+.03); flush(Bx); }
    return W; }
  function tierLot(L){ if(L.me) return tierOf(studyDays()); const t=+(L.rec && L.rec.t)||1; return Math.max(1,Math.min(4,t)); }
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
  /* (v536) 동네 = ISLE_MAP 의 이름 있는 길 6개 · D = 길 가운데 (화면 이름·지도용) */
  const HOODS=MAP.hoods.map((h,i)=>[h.id,"d"+(i+1)]);
  const D={plaza:[0,0], farm:MAP.spots.farm.slice()}; MAP.hoods.forEach((h,i)=>{ const C=MAP.curve(h.p), A=MAP.at(C.Q,C.L,h.s0+3.5*MAP.GAP); D["d"+(i+1)]=[A.x,A.z]; });
  const hoodInfo=id=>MAP.hoods.find(h=>h.id===id)||MAP.hoods[0];
  const SPOT={};   // 이름표·문 자리
  const onB=[];    // 다 지은 뒤 (놀이 IPLAY 가 물건을 붙임)
  let myHouse=null;
  function studyDays(){ try{ const s=JSON.parse(localStorage.getItem("hyeng_study_v1")||"{}"), d=s.days||{}; return d.tot||d.n||0; }catch(e){ return 0; } }
  const PREM_DAYS=5;
  function myLotId(){ return store("hyeng_proto_ilot")||""; }
  /* ── (v528) 땅 = 서버 /hy/isle/lot/<땅> = {k:아이, c:집 코드, n:이름, at} · 먼저 고른 아이만 (쓰고 → 다시 읽어 내 것인지 확인) ── */
  const LOTP="/hy/isle/lot2";   /* (v536) 사용자: "싹 초기화 … 마을 땅도" → 새 땅 목록 (예전 lot 은 안 씀) */
  let SRV={}, srvAt=0, srvOk=false;
  function myKey(){ let k=""; try{ const K=kidInfo(); k=K.rid||""; }catch(e){} return String(k||("c:"+myCode)).replace(/[.#$\[\]\/]/g,"_").slice(0,48); }
  async function loadLots(){ try{ const v=await NET.get(LOTP); SRV=v||{}; srvOk=true; srvAt=Date.now(); }catch(e){ srvOk=false; } return SRV; }
  function owners(){ const me=myKey(); let mine=null;
    lots.forEach(L=>{ const s=SRV[L.id]; L.rec=s||null; L.me=!!(s && s.k===me); L.owner=s ? (L.me?"나":String(s.n||"친구").slice(0,8)) : ""; if(L.me) mine=L; });
    if(!mine && !srvOk){ let id=myLotId(); if(!id){ const F=lots.filter(L=>!L.owner && !L.prem); let h=0; for(const ch of myKey()) h=(h*31+ch.charCodeAt(0))>>>0; if(F.length) id=F[h%F.length].id; } const L=lots.find(L=>L.id===id && !L.owner); if(L){ L.me=true; L.owner="나"; } }   /* 서버가 안 될 때 = 기기에 적어 둔 내 땅 */ }
  async function claim(id){ const L=lots.find(L=>L.id===id); if(!L) return "none"; const me=myKey(), K=kidInfo(), rec={k:me, c:myCode, n:String(K.n||"친구").slice(0,10), at:Date.now()};
    if(!NET.on()){ await NET.ready(); } if(!NET.on()){ store("hyeng_proto_ilot", id); return "local"; }
    try{ const cur=await NET.get(LOTP+"/"+id); if(cur && cur.k!==me) return "taken";
      await NET.put(LOTP+"/"+id, rec); await new Promise(r=>setTimeout(r, 450)); const chk=await NET.get(LOTP+"/"+id); if(!chk || chk.k!==me) return "taken";
      const old=Object.keys(SRV).filter(k=>k!==id && SRV[k] && SRV[k].k===me); for(const k of old){ try{ await NET.del(LOTP+"/"+k); }catch(e){} }   /* 전에 살던 땅은 비움 */
      store("hyeng_proto_ilot", id); await loadLots(); return "ok"; }catch(e){ return "err"; } }
  /* 처음 나오면 — 서버에 내 땅이 없으면 빈 땅 하나를 저절로 (나중에 게시판에서 옮길 수 있음) */
  /* (v539) 처음 온 아이 = 튜토리얼에서 직접 고름 (자동 X) · 추천 땅 = 아이 코드로 정한 빈 땅 */
  function recLot(){ const F=lots.filter(L=>!L.owner && !L.prem); if(!F.length) return null; let h=0; for(const ch of myKey()) h=(h*31+ch.charCodeAt(0))>>>0; return F[h%F.length]; }
  async function autoClaim(){ if(lots.some(L=>L.me) || !srvOk) return false; try{ if(tut.s<1) return false; }catch(e){} const F=lots.filter(L=>!L.owner && !L.prem); if(!F.length) return false;
    let h=0; for(const ch of myKey()) h=(h*31+ch.charCodeAt(0))>>>0; for(let i=0;i<4;i++){ const L=F[(h+i*7)%F.length]; const r=await claim(L.id); if(r==="ok"){ toast("🏡 <b>"+L.hood+" "+L.n+"번 땅</b>이 내 집이 됐어요!<br><small>📋 광장 게시판에서 다른 땅으로 옮길 수 있어요</small>", 3600); return true; } } return false; }
  /* 동네 늘리기 — 빈 땅이 4칸 아래면 다음 동네 섬이 열림 (최대 6동 = 96칸) */
  function hoodCount(){ const n=Object.keys(SRV).length; let h=3; while(h<6 && h*16-n<4) h++; return h; }
  function drawLots(){ owners();
    const gPad=geo_("pad",()=>{ const g=new THREE.PlaneGeometry(LOT,LOT); g.rotateX(-Math.PI/2); return g; }), gEd=geo_("ped",()=>{ const g=new THREE.RingGeometry(LOT*.66,LOT*.72,4,1); g.rotateZ(Math.PI/4); g.rotateX(-Math.PI/2); return g; });
    lots.forEach(L=>{ prim(gPad, L.owner?PAD:(L.prem?0xf3dc9a:PADE), L.x,.008,L.z,{flat:1}); prim(gEd, L.owner?0x6fae58:(L.prem?0xe0b040:0xc9a46a), L.x,.012,L.z,{flat:1});
      if(L.owner){ L.style=styleOf(L); L.tier=tierLot(L); L.fl=floorsLot(L); L.obj=houseObj(L); cols.push([L.x+OX,L.z+OZ,.9]); lotDeco(L);
        if(L.me){ const st=mesh(new THREE.OctahedronGeometry(.32), 0xffd23f, L.x,3.0,L.z,{basic:1,nocast:1}); G.userData.star=st; } }
      else { const p=mesh(new THREE.CylinderGeometry(.05,.05,.8,6), 0x8a5a34, L.x,.4,L.z); const b=mesh(new THREE.BoxGeometry(.62,.36,.06), L.prem?0xffd23f:0xfff3d6, L.x,.82,L.z); b.rotation.y=L.face; cols.push([L.x+OX,L.z+OZ,.2]); } });
    myHouse=lots.find(L=>L.me)||null;
    lots.forEach(L=>{ if(L.obj) L.obj.userData.lot=L; }); }
  /* (v535) 집 둘레 꾸밈 — 단계마다 하나씩 늘어남 (모두 땅 칸 안 · 걷는 길은 그대로) */
  function lotDeco(L){ const fx=Math.sin(L.face), fz=Math.cos(L.face), sx=fz, sz=-fx, P=(f,sd)=>[L.x+fx*f+sx*sd, L.z+fz*f+sz*sd], t=L.tier||1;
    { const [x,z]=P(.98,0); prim(geo_("mat",()=>{ const g=new THREE.BoxGeometry(.5,.03,.26); return g; }), 0xc9925c, x,.02,z,{ry:L.face,flat:1}); }   // 문 앞 발판
    if(t>=2){ const [x,z]=P(.82,.78); prim(geo_("mbP",()=>new THREE.CylinderGeometry(.035,.035,.5,6)), 0x7a4f2c, x,.25,z); prim(geo_("mbB",()=>new THREE.BoxGeometry(.2,.16,.28)), [0xff6b6b,0x5aa7ff,0xffc93d,0x5cc46a][HCOL.indexOf(L.style.slice(2))]||0xff6b6b, x,.56,z,{ry:L.face});
      const [a,b]=P(.8,-.78); [[0,0,0xff7aa8],[.12,.08,0xffd23f],[-.1,.1,0xffffff],[.05,-.12,0xb28dff]].forEach(([u,w,c])=>{ prim(geo_("lf",()=>new THREE.ConeGeometry(.06,.2,5)), 0x4fa34a, a+u,.1,b+w); prim(geo_("bl",()=>new THREE.IcosahedronGeometry(.07,0)), c, a+u,.22,b+w); }); }
    if(t>=3){ const R=1.0; [[[.55,-R],[-R,-R]],[[-R,-R],[-R,R]],[[-R,R],[.55,R]]].forEach(([p1,p2])=>{ // 뒤·옆 울타리 (문 쪽은 열림)
        const A=P(p1[0],p1[1]), B=P(p2[0],p2[1]), dx=B[0]-A[0], dz=B[1]-A[1], len=Math.hypot(dx,dz), ry=Math.atan2(dx,dz);
        for(let i=0;i<=4;i++){ const u=i/4; prim(geo_("fp",()=>new THREE.BoxGeometry(.07,.36,.07)), 0xfff6e6, A[0]+dx*u,.18,A[1]+dz*u); }
        [.13,.27].forEach(y=>prim(geo_("fr"+len.toFixed(2),()=>new THREE.BoxGeometry(.04,.05,len)), 0xfff6e6, (A[0]+B[0])/2,y,(A[1]+B[1])/2,{ry})); });
      [[-.75,.75],[-.75,-.75]].forEach(([f,sd])=>{ const [x,z]=P(f,sd); kk("city","bush",x,z,{s:.55,chunk:L.chunk}); }); }
    if(t>=4){ const [x,z]=P(-.7,.75); kk("isle", L.style.slice(2)==="blue"||L.style.slice(2)==="green"?"flag_yellow":"flag_blue", x,z,{s:1.3,chunk:L.chunk}); } }
  /* (v535) 사용자: "땅도 조금 더 이쁘게" — 얕은 물 테 · 모래 해변 · 가장자리 바위 · 꽃밭 · 덤불 · 가로등 · 구름 */
  function shore(I){ // 얕은 물 (섬 둘레 밝은 청록) + 모래 띠(바다 쪽 일부만)
    const sh=new THREE.Shape(), n=72; for(let i=0;i<=n;i++){ const a=i/n*6.2832, r=rr(I,a)+1.7+.5*Math.sin(4*a+I.s); const x=Math.cos(a)*r, y=Math.sin(a)*r; i?sh.lineTo(x,y):sh.moveTo(x,y); }
    const g=new THREE.ShapeGeometry(sh,2); g.rotateX(Math.PI/2); const m=new THREE.Mesh(g, new THREE.MeshStandardMaterial({color:LIN(0x8fe0e6), roughness:.3})); m.position.set(I.cx+OX,-.735,I.cz+OZ); m.receiveShadow=true; G.add(m);
    const pos=[], idx=[]; const nn=96; for(let i=0;i<=nn;i++){ const a=i/nn*6.2832, ro=rr(I,a)-.06, w=Math.max(0, .15+.95*Math.sin(2*a+I.s*1.7)); pos.push(Math.cos(a)*ro,0,Math.sin(a)*ro, Math.cos(a)*(ro-w),0,Math.sin(a)*(ro-w)); if(i<nn){ const k=i*2; idx.push(k,k+1,k+2, k+1,k+3,k+2); } }
    const bg=new THREE.BufferGeometry(); bg.setAttribute("position", new THREE.Float32BufferAttribute(pos,3)); bg.setIndex(idx); bg.computeVertexNormals(); const nr=bg.attributes.normal; for(let i=0;i<nr.count;i++) nr.setXYZ(i,0,1,0);
    const b=new THREE.Mesh(bg, MC(0xf0dca8)); b.position.set(I.cx+OX,.006,I.cz+OZ); b.receiveShadow=true; G.add(b); }
  function rocks(I,n,chunk){ const RK=["rock_single_A","rock_single_B","rock_single_C","rock_single_D","rock_single_E"];
    for(let k=0;k<n;k++){ const a=rnd()*6.2832, out=rnd()<.45, r=rr(I,a)+(out?.9+rnd()*.8:-.35), x=I.cx+Math.cos(a)*r, z=I.cz+Math.sin(a)*r;
      if(!out && (onPave(x,z,.6) || busy.some(([bx,bz,br])=>Math.hypot(x-bx,z-bz)<br))) continue;
      kk("nature",RK[Math.floor(rnd()*RK.length)],x,z,{s:.7+rnd()*.7,ry:rnd()*6,y:out?-.75:-.05,chunk,col:out?0:.45}); } }
  function bed(x,z,r,chunk){ // 동그란 꽃밭
    prim(geo_("bedS",()=>new THREE.CylinderGeometry(1,1.04,.1,22)), 0xd8cdb4, x,.05,z,{sx:r,sz:r});   // 돌 테두리
    prim(geo_("bedT",()=>new THREE.CylinderGeometry(1,1,.02,22)), 0x5aa845, x,.1,z,{sx:r*.88,sz:r*.88,flat:1});   // 풀 바닥
    const C=[0xff7aa8,0xffd23f,0xffffff,0xb28dff,0xff9a3d,0xff5d6c]; const n=Math.round(r*r*34);
    for(let i=0;i<n;i++){ const a=rnd()*6.283, d=Math.sqrt(rnd())*r*.8, px=x+Math.cos(a)*d, pz=z+Math.sin(a)*d, h=.18+rnd()*.12; prim(geo_("lf",()=>new THREE.ConeGeometry(.06,.2,5)), 0x4fa34a, px,.1+h/2,pz,{sy:h/.2}); prim(geo_("bl2",()=>new THREE.IcosahedronGeometry(.1,0)), C[i%6], px,.12+h,pz,{sy:.7}); }
    cols.push([x+OX,z+OZ,r+.1]); busy.push([x,z,r+.5]); }
  function bushes(I,n,chunk){ for(let k=0;k<n;k++){ const a=rnd()*6.2832, r=rr(I,a)*(.45+rnd()*.45), x=I.cx+Math.cos(a)*r, z=I.cz+Math.sin(a)*r;
      if(!inIsle(I,x,z,.8) || water(x,z) || onPave(x,z,.7) || busy.some(([bx,bz,br])=>Math.hypot(x-bx,z-bz)<br)) continue; kk("city","bush",x,z,{s:.7+rnd()*.4,ry:rnd()*6,chunk,col:.45}); busy.push([x,z,.8]); } }
  function clouds(){ for(let i=0;i<9;i++){ const a=i/9*6.283+.5, d=104+rnd()*30; kk("nature",i%2?"cloud_big":"cloud_small",Math.cos(a)*d,Math.sin(a)*d-18,{s:2.2+rnd()*1.6,y:9+rnd()*5,ry:rnd()*6,chunk:"far",cast:false}); } }
  /* (v536) 길 = 곡선을 짧은 판으로 (색마다 한 덩어리) · 테두리 한 줄 */
  const ROAD=0xe6d6b0, ROADE=0xc4ab7e, LANE=0xdcbf86, LANEE=0xbf9f6a;
  function roadP(P,w,col,edge){ const UPL=geo_("upl",()=>{ const g=new THREE.PlaneGeometry(1,1); g.rotateX(-Math.PI/2); return g; }), UCI=geo_("uci",()=>{ const g=new THREE.CircleGeometry(.5,18); g.rotateX(-Math.PI/2); return g; });
    const Q=MAP.cr(P,8); for(let i=1;i<Q.length;i++){ const a=Q[i-1], b=Q[i], L=Math.hypot(b[0]-a[0],b[1]-a[1]); if(L<1e-3) continue; const ry=Math.atan2(b[0]-a[0],b[1]-a[1]), mx=(a[0]+b[0])/2, mz=(a[1]+b[1])/2;
      prim(UPL, edge, mx,.009,mz,{ry, sx:w+.34, sz:L+.02, flat:1}); prim(UPL, col, mx,.013,mz,{ry, sx:w, sz:L+.02, flat:1}); paved.push([a[0],a[1],b[0],b[1],w/2]); }
    Q.forEach((p,i)=>{ if(i%2 && i!==Q.length-1) return; prim(UCI, edge, p[0],.008,p[1],{sx:w+.34,sz:w+.34,flat:1}); prim(UCI, col, p[0],.012,p[1],{sx:w,sz:w,flat:1}); }); return Q; }
  /* 이름 있는 길 입구 — 나무 아치 + 이름판 (잠긴 길 = 🚧 공사 중 울타리) */
  function signTex(txt, bg, w){ const c=document.createElement("canvas"); c.width=w||512; c.height=128; const g=c.getContext("2d"); g.fillStyle=bg||"#fffdf7"; g.strokeStyle="#3b2433"; g.lineWidth=10;
    g.beginPath(); g.roundRect ? g.roundRect(8,10,c.width-16,108,54) : g.rect(8,10,c.width-16,108); g.fill(); g.stroke(); g.fillStyle="#3b2433"; g.font="bold 58px sans-serif"; g.textAlign="center"; g.textBaseline="middle"; g.fillText(txt,c.width/2,68);
    const t=new THREE.CanvasTexture(c); t.encoding=THREE.sRGBEncoding; return t; }
  function arch(h, i, open){ const C=MAP.curve(h.p), A=MAP.at(C.Q,C.L,Math.max(1.2,h.s0-2.3)), nx=-A.tz, nz=A.tx, ry=Math.atan2(A.tx,A.tz);
    if(open){ [-1,1].forEach(sd=>{ prim(geo_("arP",()=>new THREE.CylinderGeometry(.09,.11,2.5,8)), 0x8a5a34, A.x+nx*sd*1.25,1.25,A.z+nz*sd*1.25); cols.push([A.x+nx*sd*1.25+OX, A.z+nz*sd*1.25+OZ, .2]); });
      prim(geo_("arB",()=>new THREE.BoxGeometry(2.9,.16,.16)), 0x8a5a34, A.x,2.45,A.z,{ry:ry+Math.PI/2});
      const T={blossom:0xffb7d0, sun:0xffd23f, palm:0x5cc46a, clover:0x7be39a, maple:0xff8a4a, star:0xc7a6ff}[h.tree]||0xffd23f;
      for(let k=-3;k<=3;k++){ prim(geo_("arF",()=>new THREE.IcosahedronGeometry(.17,0)), k%2?T:0xffffff, A.x+nx*k*.4,2.6,A.z+nz*k*.4); } }
    else { for(let k=-2;k<=2;k++){ prim(geo_("fcP",()=>new THREE.BoxGeometry(.12,.8,.12)), 0xfff1c4, A.x+nx*k*.6,.4,A.z+nz*k*.6); cols.push([A.x+nx*k*.6+OX, A.z+nz*k*.6+OZ, .45]); }
      [.25,.6].forEach(y=>prim(geo_("fcR",()=>new THREE.BoxGeometry(2.6,.12,.06)), 0xff9a3d, A.x,y,A.z,{ry:ry+Math.PI/2})); kk("isle","resource_lumber",A.x+A.tx*1.6,A.z+A.tz*1.6,{s:1.2,chunk:"m"}); }
    const sp=new THREE.Sprite(new THREE.SpriteMaterial({map:signTex((open?"":"🚧 ")+h.ic+" "+h.id+" "+h.nm, open?"#fffdf7":"#ffd23f"), depthWrite:false})); sp.scale.set(3.0,.75,1); sp.position.set(A.x+OX, open?2.95:1.7, A.z+OZ); sp.renderOrder=2; G.add(sp); SIGNS.push(sp);
    return A; }
  /* 동네 나무 — 길마다 색 (🌸 벚꽃 · 🌻 해바라기 · 🌊 야자 · 🍀 클로버 · 🍁 단풍 · ⭐ 별빛) · 땅 뒤 마당 쪽 */
  function laneTrees(h){ const C=MAP.curve(h.p), end=C.L[C.L.length-1];
    const ok=(x,z,r)=>MAP.inside(x,z,1.2) && !onPave(x,z,.7) && !water(x,z) && !busy.some(([bx,bz,br])=>Math.hypot(x-bx,z-bz)<br+(r||0)-.9) && !lots.some(L=>Math.abs(L.x-x)<1.5 && Math.abs(L.z-z)<1.5);
    if(h.tree==="sun"){ for(let s=h.s0-1; s<end; s+=1.35){ const A=MAP.at(C.Q,C.L,s); [-1,1].forEach(sd=>{ const x=A.x-A.tz*sd*4.15, z=A.z+A.tx*sd*4.15; if(!ok(x,z)) return;
        prim(geo_("snS",()=>new THREE.CylinderGeometry(.04,.05,1.1,5)), 0x4fa34a, x,.55,z); prim(geo_("snF",()=>new THREE.CylinderGeometry(.24,.24,.06,10)), 0xffc21a, x,1.12,z,{rx:1.2, ry:Math.atan2(A.tx,A.tz)}); prim(geo_("snC",()=>new THREE.CylinderGeometry(.11,.11,.08,8)), 0x8a5a34, x,1.13,z,{rx:1.2, ry:Math.atan2(A.tx,A.tz)}); }); } return; }
    /* (v536) 가로수 — 땅 사이 틈 길가 (집 뒤에 두면 집에서 나올 때 카메라를 가림) · 등과 번갈아 */
    const SP=[]; for(let k=-1;k<MAP.PER;k++){ if(k>=0 && k%2===0 && k<MAP.PER-1) continue; SP.push([h.s0+(k+.5)*MAP.GAP, (k+1)%4<2?1:-1]); SP.push([h.s0+(k+.5)*MAP.GAP, (k+1)%4<2?-1:1]); }
    SP.forEach(([s,sd])=>{ if(s<.8 || s>end) return; const A=MAP.at(C.Q,C.L,s); { const x=A.x-A.tz*sd*1.6, z=A.z+A.tx*sd*1.6; if(!MAP.inside(x,z,1) || water(x,z)) return; cols.push([x+OX,z+OZ,.3]);
        if(h.tree==="palm"){ const lean=.25; prim(geo_("pmT",()=>new THREE.CylinderGeometry(.1,.16,2.6,7)), 0xb08050, x,1.3,z,{rz:lean}); const tx=x-Math.sin(lean)*1.3, ty=2.55;
          for(let k=0;k<6;k++) prim(geo_("pmL",()=>{ const g=new THREE.ConeGeometry(.22,1.5,4); g.translate(0,.75,0); return g; }), k%2?0x3fae4a:0x5cc46a, tx,ty,z,{ry:k*1.05, rz:1.9}); return; }
        if(h.tree==="clover"){ [[0,0],[.5,.3],[-.4,.35]].forEach(([a,b],k)=>prim(geo_("clv",()=>new THREE.IcosahedronGeometry(.42,1)), k?0x7be39a:0x5cc46a, x+a,.32,z+b,{sy:.55})); return; }
        const col={blossom:[0xffb7d0,0xff8fb8,0xfff0f5], maple:[0xff8a4a,0xe8572a,0xffc061], star:[0xc7a6ff,0x8f63ef,0xfff3a8]}[h.tree]||[0x5cc46a,0x3f9a4a,0x7be39a];
        prim(geo_("ttr",()=>new THREE.CylinderGeometry(.12,.17,1.2,7)), 0x8a5a34, x,.6,z);
        [[0,1.55,0,.85],[.45,1.35,.2,.6],[-.4,1.4,-.25,.62],[.05,2.0,-.1,.55]].forEach(([a,y,b,r],k)=>prim(geo_("tb"+k,()=>new THREE.IcosahedronGeometry(r,1)), col[k%col.length===2&&k===3?2:k%2], x+a,y,z+b));
        if(h.tree==="star") prim(geo_("tst",()=>new THREE.OctahedronGeometry(.22)), 0xffe27a, x,2.75,z); } }); }
  let SIGNS=[];   /* (v539) 길 팻말·가게 간판 — 카메라 바로 앞이면 흐려짐 (화면을 가리지 않게) */
  function build(){
    if(G.userData.built) return; G.userData.built=1; SIGNS=[];
    const sea=new THREE.Mesh(new THREE.CircleGeometry(400,48), new THREE.MeshStandardMaterial({color:LIN(0x6cc0dc), roughness:.35})); sea.rotation.x=-Math.PI/2; sea.position.set(OX,-0.76,OZ); sea.receiveShadow=true; G.add(sea); G.userData.sea=sea;
    /* (v536) 사용자: "마을은 이쁘게 다시 만들어 줘야 해" → 하나로 이어진 큰 섬 (ISLE_MAP 설계도) — 광장 · 굽은 돌길 · 시장 거리 · 숲속 호수 · 언덕 학교 · 곶 타워 · 산 아래 광산 · 풍차 밭 · 공원 · 이름 있는 동네 길 */
    const LK=LKD, Sx=MAP.spots; const C=land(MAP.island.cx,MAP.island.cz,Math.max(MAP.island.ax,MAP.island.az),MAP.island.s,[LK],true);
    const HN=hoodCount();
    /* (v550) 🗺 구역 — 바닥 색(부드러운 모양) · 입구 문 + 이름판 · 🚧 빈 자리 팻말 */
    { const ZL=[]; (MAP.zones||[]).forEach(Z=>{ const P=Z.poly, Q=MAP.cr(P.concat([P[0],P[1]]),6).slice(6*1, 6*(P.length+1)), cx=P.reduce((a,p)=>a+p[0],0)/P.length, cz=P.reduce((a,p)=>a+p[1],0)/P.length;
      if(Z.free){ prim(geo_("fpost",()=>new THREE.CylinderGeometry(.08,.08,1.7,8)), 0x9a6a40, cx,.85,cz); cols.push([cx+OX,cz+OZ,.35]); busy.push([cx,cz,7]);
        const sp=new THREE.Sprite(new THREE.SpriteMaterial({map:signTex("🚧 새 구역 준비 중", "#ffe9a8", 512), depthWrite:false})); sp.scale.set(2.8,.7,1); sp.position.set(cx+OX,2.0,cz+OZ); sp.renderOrder=2; G.add(sp); SIGNS.push(sp); SPOT["free_"+Z.k]=[cx+OX,1.6,cz+OZ]; return; }
      const sh=new THREE.Shape(); Q.forEach((q,i)=>i?sh.lineTo(q[0],-q[1]):sh.moveTo(q[0],-q[1])); if(MAP.inPoly(LK[0],LK[1],P)){ const hp=new THREE.Path(); for(let k=0;k<=40;k++){ const a=k/40*6.2832; const x=LK[0]+Math.cos(a)*(LK[2]+1.6), z=LK[1]+Math.sin(a)*(LK[3]+1.6); k?hp.lineTo(x,-z):hp.moveTo(x,-z); } sh.holes.push(hp); }
      const g=new THREE.ShapeGeometry(sh,2); g.rotateX(-Math.PI/2); ZL.push({g, col:new THREE.Color(GRASS).lerp(new THREE.Color(Z.c),.42).getHex()}); g.dispose;
      if(Z.gate){ const [gx,gz]=Z.gate, L=Math.hypot(gx,gz)||1, fx=gx/L, fz=gz/L, px=-fz, pz=fx, W2=2.5;
        [-1,1].forEach(sd=>{ const x=gx+px*W2*sd, z=gz+pz*W2*sd; prim(geo_("gpost",()=>new THREE.CylinderGeometry(.13,.15,2.8,10)), 0xfffdf7, x,1.4,z); prim(geo_("gball",()=>new THREE.SphereGeometry(.2,10,8)), 0xffd23f, x,2.9,z); cols.push([x+OX,z+OZ,.3]); busy.push([x,z,.9]); });
        prim(geo_("gbeam",()=>new THREE.BoxGeometry(5.5,.26,.26)), 0xc94545, gx,2.62,gz,{ry:Math.atan2(-pz,px)});
        const sp=new THREE.Sprite(new THREE.SpriteMaterial({map:signTex(Z.nm, "#"+new THREE.Color(Z.c).lerp(new THREE.Color(0xffffff),.35).getHexString(), 512), depthWrite:false})); sp.scale.set(3.4,.85,1); sp.position.set(gx+OX,3.25,gz+OZ); sp.renderOrder=2; G.add(sp); SIGNS.push(sp); } });
      if(ZL.length){ const zm=vcMerge(ZL, new THREE.MeshStandardMaterial({vertexColors:true, roughness:.95, polygonOffset:true, polygonOffsetFactor:-1, polygonOffsetUnits:-2}));   /* (v572) 구역 바닥색이 땅과 겹쳐 줄무늬 */ zm.castShadow=false; zm.position.set(OX,.005,OZ); G.add(zm); } }
    /* 🎓 캠퍼스 마당 (학교·도서관·박물관이 봄) */
    if(Sx.campus){ disc(Sx.campus[0],Sx.campus[1],5.6,STONE); roadP([MAP.roads.school.p[MAP.roads.school.p.length-1], Sx.campus], 2.2, ROAD, ROADE); }
    // 길
    disc(0,0,MAP.plaza.r,STONE);
    Object.entries(MAP.roads).forEach(([k,r])=>roadP(r.p, r.w, ROAD, ROADE));
    MAP.hoods.forEach((h,i)=>{ if(i<HN) roadP(h.p, 1.5, LANE, LANEE); else { const Q=MAP.cr(h.p,8); const UPL=geo_("upl",()=>null); for(let j=1;j<Q.length;j++){ const a=Q[j-1], b=Q[j], L=Math.hypot(b[0]-a[0],b[1]-a[1]); if(j%2) prim(UPL, 0xd4bd8a, (a[0]+b[0])/2,.006,(a[1]+b[1])/2,{ry:Math.atan2(b[0]-a[0],b[1]-a[1]), sx:1.2, sz:L*.9, flat:1}); paved.push([a[0],a[1],b[0],b[1],.75]); }
        MAP.hoodLots(h,i).forEach(L=>busy.push([L.x,L.z,1.4])); } });   /* 잠긴 길도 자리는 비워 둠 (나무 X) */
    // ⛲ 광장 — 큰 분수 · 벤치 · 가로등
    { const st=0xcfc8b8, k=1.3; mesh(new THREE.CylinderGeometry(1.45*k,1.55*k,.45,18), st, 0,.22,0); mesh(new THREE.CylinderGeometry(1.3*k,1.3*k,.1,28), 0x5cc4e8, 0,.43,0,{nocast:1}); mesh(new THREE.CylinderGeometry(.2,.27,1.3,10), st, 0,.95,0);
      mesh(new THREE.CylinderGeometry(.62,.44,.2,14), st, 0,1.6,0); mesh(new THREE.CylinderGeometry(.54,.54,.06,16), 0x7fd3ea, 0,1.7,0,{nocast:1}); mesh(new THREE.SphereGeometry(.22,10,8), 0xbfeaff, 0,1.92,0,{nocast:1}); cols.push([OX,OZ,1.95*k]); SPOT.fountain=[OX,1.2,OZ]; }
    [-112,-67,22,67,112,157,-157].forEach(d=>{ const a=d*Math.PI/180, x=Math.cos(a)*5.35, z=Math.sin(a)*5.35; if(!onPave(x,z,.3)) kk("city","streetlight",x,z,{s:1,chunk:"m",col:.2}); });
    [[-150,3.6],[135,3.6],[-30,3.6]].forEach(([d,r])=>{ const a=d*Math.PI/180; kk("city","bench",Math.cos(a)*r,Math.sin(a)*r,{s:.9,ry:-a-Math.PI/2,chunk:"m",col:.45}); });
    // 📋 게시판 (땅 고르기)
    { const [bx,bz]=Sx.board; const b=new THREE.Group(); b.position.set(bx+OX,0,bz+OZ); b.rotation.y=Math.PI*.25; const W_=MC(0x9a6a40); [-.55,.55].forEach(x=>{ const p=new THREE.Mesh(new THREE.BoxGeometry(.1,1.3,.1),W_); p.position.set(x,.65,0); b.add(p); });
      const bd=new THREE.Mesh(new THREE.BoxGeometry(1.4,.85,.08),MC(0xc9925c)); bd.position.y=1.05; b.add(bd); [[-.3,1.15,0xfff3d6],[.25,1.0,0xdff3d6],[-.2,.88,0xffd9e6]].forEach(([x,y,c])=>{ const pp=new THREE.Mesh(new THREE.BoxGeometry(.38,.3,.02),MC(c)); pp.position.set(x,y,.05); b.add(pp); });
      b.traverse(m=>{ if(m.isMesh){ m.castShadow=true; } }); G.add(b); cols.push([bx+OX,bz+OZ,.5]); SPOT.board=[bx+OX,1.9,bz+OZ]; busy.push([bx,bz,1.2]); }
    /* (v571) 사용자: 「상점들 … 조금 더 이쁘게 · 차이점이 없어」 — 가게마다 지붕 위 큰 상징물 + 문 옆 소품 + 가게 색 차양
       로컬 좌표: +z = 길(앞) · x = 옆 · 지붕 ≈ 3.3 */
    function shopDeco(SH, x, z, nx, nz){ const k=SH[0], col=SH[3], g=new THREE.Group(); g.position.set(x+OX,0,z+OZ); g.rotation.y=Math.atan2(-nx,-nz);
      const P=(geo,c,px,py,pz,rx,ry,rz,o)=>{ const m=new THREE.Mesh(geo, o&&o.basic?new THREE.MeshBasicMaterial({color:LIN(c)}):MC(c)); m.position.set(px,py,pz); m.rotation.set(rx||0,ry||0,rz||0); m.castShadow=true; g.add(m); return m; };
      const Bx=(w,h,d,c,px,py,pz)=>P(new THREE.BoxGeometry(w,h,d),c,px,py+h/2,pz), Sp=(r,c,px,py,pz,sx,sy,sz)=>{ const m=P(new THREE.SphereGeometry(r,12,10),c,px,py,pz); if(sx) m.scale.set(sx,sy,sz); return m; }, Cy=(rt,rb,h,c,px,py,pz,rx,rz)=>P(new THREE.CylinderGeometry(rt,rb,h,14),c,px,py,pz,rx,0,rz);
      /* 차양 (가게 색 줄무늬) */ for(let j=0;j<5;j++){ const a=P(new THREE.BoxGeometry(.5,.05,.85),j%2?0xffffff:col,-1+j*.5,2.15,2.05,.38); a.castShadow=false; }
      const R=2.0, sx=-1.95, sz=1.9;   // 지붕 위(가게 지붕 ≈ 1.7) · 문 옆
      if(k==="fish"){ const f=Sp(.55,0x5aa7ff,0,R+.4,0,1.6,.8,.6); Sp(.09,0xffffff,.62,R+.55,.28); Sp(.05,0x3b2433,.65,R+.55,.32); P(new THREE.ConeGeometry(.42,.6,4),0x3d8be0,-1.05,R+.4,0,0,0,Math.PI/2); Cy(.04,.04,.5,0x8a8a96,0,R-.05,0);
        Bx(.9,.45,.6,0xffffff,sx,0,sz); Bx(.8,.06,.5,0xbfeaff,sx,.45,sz); [[-.2,0xff9a3d],[.05,0x5aa7ff],[.25,0xc7a6ff]].forEach(([o,c])=>Sp(.08,c,sx+o,.55,sz,2,.7,.9)); }
      else if(k==="clothes"){ Cy(.05,.05,.5,0x8a8a96,0,R-.05,0); const t=Bx(1.1,.85,.12,col,0,R+.15,0); Bx(.3,.4,.12,col,-.7,R+.55,0).rotation.z=.6; Bx(.3,.4,.12,col,.7,R+.55,0).rotation.z=-.6; Bx(.5,.18,.13,0xffffff,0,R+.85,0);
        Cy(.14,.18,.75,0xff9ac8,sx,.42,sz); Sp(.14,0xf3d6c0,sx,1.0,sz); Cy(.03,.03,.3,0x8a8a96,sx,.12,sz); Cy(.12,.12,.04,0x8a8a96,sx,.02,sz); }
      else if(k==="mart"){ Cy(.05,.05,.5,0x8a8a96,0,R-.05,0); Bx(1.0,.55,.7,0xc48a58,0,R+.15,0); [[-.25,.1,0xff4b4b],[.05,-.12,0xffd23f],[.28,.12,0x7fd36a],[-.05,.15,0xff9a3d]].forEach(([a,b,c])=>Sp(.17,c,a,R+.78,b));
        [[0,0xff4b4b],[.55,0xffd23f]].forEach(([o,c])=>{ Bx(.5,.3,.42,0xc48a58,sx+o,0,sz); for(let q=0;q<3;q++) Sp(.08,c,sx+o-.13+q*.13,.36,sz); }); }
      else if(k==="hair"){ Cy(.05,.05,.5,0x8a8a96,0,R-.05,0); [0,1].forEach(s2=>{ const r=new THREE.Mesh(new THREE.TorusGeometry(.2,.06,8,18), MC(0xc0c0cc)); r.position.set(-.18+s2*.36,R+.35,0); g.add(r); }); Bx(.08,.9,.06,0xc0c0cc,-.12,R+.5,0).rotation.z=-.35; Bx(.08,.9,.06,0xc0c0cc,.12,R+.5,0).rotation.z=.35;
        for(let q=0;q<6;q++) Cy(.13,.13,.18,[0xff4b4b,0xffffff,0x5aa7ff][q%3],sx,.3+q*.18,sz); Sp(.15,0xffffff,sx,1.45,sz); }
      else if(k==="snack"){ P(new THREE.ConeGeometry(.38,.9,14),0xe8b46a,0,R+.4,0,Math.PI); Sp(.42,0xffb6d1,0,R+.95,0); Sp(.32,0x9ff0d0,0,R+1.32,0); Sp(.09,0xff4b4b,0,R+1.66,0);
        Cy(.3,.3,.05,0xffffff,sx,.62,sz); Cy(.04,.04,.6,0x7a4f2c,sx,.3,sz); Cy(.06,.06,1.5,0xffffff,sx,1.0,sz); P(new THREE.ConeGeometry(.75,.35,10),col,sx,1.85,sz); }
      else if(k==="furn"){ Bx(1.2,.3,.6,col,0,R,0); Bx(1.2,.45,.16,col,0,R+.3,-.22); Bx(.16,.35,.6,col,-.6,R+.25,0); Bx(.16,.35,.6,col,.6,R+.25,0);
        Bx(.8,.3,.5,0x7d8ff0,sx,.15,sz); Bx(.8,.35,.14,0x7d8ff0,sx,.4,sz-.2); Cy(.03,.03,1.2,0x3b2433,sx+.65,.6,sz); P(new THREE.CylinderGeometry(.12,.22,.26,14),0xffe9a8,sx+.65,1.3,sz,0,0,0,{basic:1}); }
      else if(k==="pet"){ Cy(.05,.05,.5,0x8a8a96,0,R-.05,0); Cy(.11,.11,.9,0xffffff,0,R+.35,0,0,Math.PI/2); [-.45,.45].forEach(o=>[-.1,.1].forEach(t2=>Sp(.14,0xffffff,o,R+.35+t2,0)));
        Bx(.7,.55,.65,0xd9a066,sx,0,sz); P(new THREE.ConeGeometry(.56,.38,4),0xc94545,sx,.74,sz,0,Math.PI/4); Bx(.26,.3,.02,0x3b2433,sx,.04,sz+.33); }
      else if(k==="photo"){ Bx(.95,.6,.5,0x3b2433,0,R+.05,0); Cy(.2,.22,.3,0x9fd8ff,0,R+.35,.32,Math.PI/2); Cy(.24,.24,.06,0x3b2433,0,R+.35,.48,Math.PI/2); Bx(.24,.14,.2,0x3b2433,-.28,R+.65,0); Sp(.07,0xffd23f,.3,R+.68,.1);
        [[-.18],[.18]].forEach(([o])=>Cy(.025,.025,.9,0x8a5a34,sx+o,.45,sz,.18*(o>0?1:-1))); Bx(.35,.25,.25,0x3b2433,sx,.92,sz); }
      g.traverse(m=>{ if(m.isMesh) m.receiveShadow=true; }); G.add(g); }
    // 🏪 시장 거리 — 가게 6채가 길을 보고 마주 섬 · 사이사이 가로등 · 상자
    { const MK=["building_market_red","building_market_blue","building_market_yellow","building_market_green"], Cm=MAP.curve(MAP.roads.market.p); SPOT.shops=[];
      /* (v539) 가게 · (v550) 상점가 큰길 양옆 8채 (🍦 간식 · 🐶 펫 · 📸 사진관도 여기로) */
      MAP.shopLots().forEach((L,i)=>{ const SH=L.sh, nx=L.nx, nz=L.nz, x=L.x, z=L.z; kk("isle",MK[i%4],x,z,{s:1.9,ry:Math.atan2(-nx,-nz),chunk:"m",col:1.35,solo:1}); busy.push([x,z,2.4]);
        { const sp=new THREE.Sprite(new THREE.SpriteMaterial({map:signTex(SH[1]+" "+SH[2], "#"+new THREE.Color(SH[3]).lerp(new THREE.Color(0xffffff),.55).getHexString(), 448), depthWrite:false})); sp.scale.set(2.5,.72,1); sp.position.set(x-nx*1.5+OX,3.1,z-nz*1.5+OZ); sp.renderOrder=2; G.add(sp); SIGNS.push(sp); }
        SPOT.shops.push({k:SH[0], ic:SH[1], t:SH[2], p:[x-nx*2.3+OX,1.4,z-nz*2.3+OZ], door:[L.rx+nx*1.9+OX, L.rz+nz*1.9+OZ]});
        const tx=-nz, tz=nx; kk("isle",(i%2)?"barrel":"crate_A_big",x-nx*.6+tx*1.9,z-nz*.6+tz*1.9,{s:.45,chunk:"m",col:.3});
        try{ shopDeco(SH, x, z, nx, nz); }catch(e){ console.warn("shopDeco", e); } });
      for(let s2=6, k=0; s2<35; s2+=7.5, k++){ const A=MAP.at(Cm.Q,Cm.L,s2), sd=k%2?1:-1; kk("city","streetlight",A.x-A.tz*sd*2.0,A.z+A.tx*sd*2.0,{s:.95,chunk:"m",col:.2}); }
      SPOT.market=[Sx.market[0]+OX,1.7,Sx.market[1]+OZ];
      /* 🏘 마을 사람들 (예전 마을) 가는 길 팻말 — 광장 서쪽 */
      { const tx=-9.5, tz=3.4; const po=mesh(new THREE.CylinderGeometry(.07,.07,1.6,8), 0x9a6a40, tx,.8,tz); cols.push([tx+OX,tz+OZ,.35]); busy.push([tx,tz,1.2]);
        const sp=new THREE.Sprite(new THREE.SpriteMaterial({map:signTex("🏘 마을 사람들", "#ece0ff", 448), depthWrite:false})); sp.scale.set(2.3,.66,1); sp.position.set(tx+OX,1.9,tz+OZ); sp.renderOrder=2; G.add(sp); SIGNS.push(sp);
        SPOT.shops.push({k:"town", ic:"🏘", t:"마을 사람들", p:[tx+OX,1.4,tz+OZ], door:[tx+OX+1.2, tz+OZ-1.2]}); } }
    // ⛏ 광산 (산 아래)
    { const mt=Sx.mountain||[Sx.mine[0]+3,Sx.mine[1]-4], re=MAP.roads.mine.p[MAP.roads.mine.p.length-1]; kk("nature","mountain_B_grass_trees",mt[0],mt[1],{s:5.5,chunk:"m",col:6.5}); busy.push([mt[0],mt[1],9]);
      kk("isle","building_mine_blue",Sx.mine[0],Sx.mine[1],{s:2.3,ry:Math.atan2(re[0]-Sx.mine[0],re[1]-Sx.mine[1]),chunk:"m",col:1.4,solo:1}); }
    SPOT.mine=[Sx.mine[0]+OX,2,Sx.mine[1]+OZ]; busy.push([Sx.mine[0]+1,Sx.mine[1]-1.5,5]);
    // 🗼 하늘 타워 (동쪽 곶)
    kk("isle","building_tower_B_blue",Sx.tower[0],Sx.tower[1],{s:3.3,chunk:"m",col:1.6,solo:1}); kk("isle","flag_blue",Sx.tower[0]-1.5,Sx.tower[1]+1.2,{s:1.6,chunk:"m"}); SPOT.tower=[Sx.tower[0]+OX,3.6,Sx.tower[1]+OZ]; busy.push([Sx.tower[0],Sx.tower[1],3.2]);
    // 🏫 학교 (언덕)
    { const [sx,sz]=Sx.school; prim(geo_("hill",()=>new THREE.CylinderGeometry(1,1.18,.34,28)), 0x7fc463, sx,.17,sz,{sx:4.2,sz:3.6}); kk("isle","building_church_blue",sx,sz,{s:2.5,y:.34,ry:Math.atan2((MAP.spots.campus||[-31,-29])[0]-sx,(MAP.spots.campus||[-31,-29])[1]-sz),chunk:"m",col:2.6,solo:1});
      SPOT.school=[sx+OX,3.2,sz+OZ]; busy.push([sx,sz,4.4]); [[-1,1],[1,1]].forEach(([a])=>kk("city","bush",sx+a*3.2,sz+2.2,{s:.8,chunk:"m"})); }
    // 🎪 무대 · 🔥 모닥불
    kk("isle","building_stage_A",Sx.stage[0],Sx.stage[1],{s:2.2,ry:Math.atan2(-Sx.stage[0],-Sx.stage[1]),chunk:"m",col:1.2}); busy.push([Sx.stage[0],Sx.stage[1],2.2]);
    { const [fx,fz]=Sx.camp; for(let i=0;i<4;i++){ const a=i/4*6.283+.4; const lg=mesh(new THREE.CylinderGeometry(.16,.16,.85,8), 0xa06a3c, fx+Math.cos(a)*1.1,.16,fz+Math.sin(a)*1.1); lg.rotation.z=Math.PI/2; lg.rotation.y=-a; }
      const f1=mesh(new THREE.ConeGeometry(.24,.6,8), 0xffa53a, fx,.32,fz,{basic:1,nocast:1}), f2=mesh(new THREE.ConeGeometry(.13,.42,8), 0xffe27a, fx,.3,fz,{basic:1,nocast:1}); G.userData.fire=[f1,f2]; cols.push([fx+OX,fz+OZ,.45]); SPOT.camp=[fx+OX,.9,fz+OZ]; busy.push([fx,fz,1.8]); }
    // 🎣 숲속 호수 — 부두 (서쪽 물가에서 물로)
    /* (v572) 사용자: 「나무판자 쪽에 캐릭터가 가라앉는 경우 · 낚시터 나무 안 예뻐」 — 판 윗면 = 땅 높이(0) · 넓게(1.8) · 아래 받침 · 기둥+밧줄 난간 · 끝에 등불 · 양동이 · 구명 튜브 */
    { const [dx,dz]=Sx.dock, B=new THREE.Group(); B.position.set(dx+OX,0,dz+OZ); const P_=(geo,c,x,y,z,o)=>{ const m=new THREE.Mesh(geo, o&&o.basic?new THREE.MeshBasicMaterial({color:LIN(c)}):MC(c)); m.position.set(x,y,z); m.castShadow=!(o&&o.flat); m.receiveShadow=true; B.add(m); return m; };
      const PL=[0xc48a58,0xb07a4a,0xd09a66,0xb98252]; for(let i=0;i<9;i++){ P_(new THREE.BoxGeometry(.44,.1,1.8),PL[i%4],i*.47,-.05,0,{flat:1}); P_(new THREE.BoxGeometry(.03,.012,1.8),0x8a5a34,i*.47+.235,.002,0,{flat:1}); }
      [-.78,.78].forEach(z=>P_(new THREE.BoxGeometry(4.3,.14,.14),0x7a4f2c,1.88,-.17,z));
      [0,1.88,3.76].forEach(x=>[-.86,.86].forEach(z=>{ P_(new THREE.CylinderGeometry(.09,.1,1.15,8),0x8a5a34,x,-.15,z); P_(new THREE.SphereGeometry(.1,8,6),0x9a6a40,x,.45,z); }));
      [-.86,.86].forEach(z=>[[0,1.88],[1.88,3.76]].forEach(([a,b])=>{ const r=P_(new THREE.CylinderGeometry(.025,.025,b-a,6),0xe8d2a6,(a+b)/2,.32,z); r.rotation.z=Math.PI/2; }));
      { const r=P_(new THREE.CylinderGeometry(.025,.025,1.72,6),0xe8d2a6,3.76,.32,0); r.rotation.x=Math.PI/2; }
      P_(new THREE.CylinderGeometry(.04,.04,1.3,6),0x3b2433,3.6,.65,.62); P_(new THREE.BoxGeometry(.2,.26,.2),0x3b2433,3.6,1.38,.62); P_(new THREE.BoxGeometry(.14,.18,.14),0xffd56a,3.6,1.38,.62,{basic:1});
      P_(new THREE.CylinderGeometry(.16,.13,.26,10),0x5aa7ff,.9,.13,-.55); P_(new THREE.TorusGeometry(.16,.015,6,12),0x3b2433,.9,.27,-.55).rotation.x=Math.PI/2;
      { const t=P_(new THREE.TorusGeometry(.24,.08,8,16),0xff6b6b,1.88,.22,-.93); t.rotation.y=Math.PI/2; }
      G.add(B); G.userData.dock=B;
      bridges.push([dx-.4+OX,dz+OZ,dx+3.8+OX,dz+OZ,.8]); SPOT.lake=[dx+2.4+OX,.6,dz+OZ]; busy.push([dx+1.4,dz,1.6]); }
    for(let i=0;i<12;i++){ const a=rnd()*6.28, r=Math.sqrt(rnd())*.82; kk("isle",rnd()<.5?"waterlily_A":"waterlily_B",LK[0]+Math.cos(a)*LK[2]*r,LK[1]+Math.sin(a)*LK[3]*r,{s:.8,y:-.36,chunk:"m",cast:false}); }
    // 🌾 풍차 밭 (→ 내 마당)
    { const [fx,fz]=Sx.farm; disc(fx+3.2,fz+4.6,1.6,PATH);
      for(let gx=0;gx<5;gx++) for(let gz=0;gz<3;gz++){ const x=fx-5.6+gx*2.8, z=fz-2.8+gz*2.8, col=[0xffd23f,0xff9a3d,0x7fd36a,0xff6b6b][(gx+gz*2)%4];
        prim(geo_("fld",()=>new THREE.BoxGeometry(2.0,.12,2.0)), 0x8a5a34, x,.06,z); busy.push([x,z,1.4]); cols.push([x+OX,z+OZ,.95]);
        for(let a=-1;a<=1;a++) for(let b=-1;b<=1;b++){ prim(geo_("crL",()=>new THREE.ConeGeometry(.08,.28,5)), 0x5db95a, x+a*.56,.25,z+b*.56); prim(geo_("crF",()=>new THREE.SphereGeometry(.12,8,6)), col, x+a*.56,.42,z+b*.56); } }
      const wm=Sx.windmill||[fx-1.2,fz-5.2]; kk("isle","building_windmill_yellow",wm[0],wm[1],{s:2.6,chunk:"m",col:1.2,solo:1}); busy.push([wm[0],wm[1],3]); SPOT.farm=[fx+3.2+OX,1.6,fz+1.6+OZ];
      /* ⛺ 캠핑장 — 텐트 2 · 모닥불 자리 */ [[fx+8,fz+6],[fx+11,fz+3]].forEach(([tx,tz],k)=>{ kk("isle","tent",tx,tz,{s:1.4,ry:k?.6:-.3,chunk:"m",col:.9}); busy.push([tx,tz,1.8]); }); }
    /* 🎡 공원 — ⭕❌ OX 마당 · 🧊 놀이터 · 🎁 보물 상자 (v528 놀이 자리) */
    { const pk=Sx.park; disc(pk.x,pk.z,pk.r,0xa8dc8a); }
    { const ox=Sx.ox; SPOT.oxC=[ox[0]+OX,ox[1]+OZ]; busy.push([ox[0],ox[1],4.2]); disc(ox[0],ox[1],3.9,0xe7dcc2);
      [[-2,0x7fd3ff,"O"],[2,0xff9a9a,"X"]].forEach(([dx,col,ch])=>{ const c=document.createElement("canvas"); c.width=c.height=128; const g=c.getContext("2d"); g.fillStyle="#"+new THREE.Color(col).getHexString(); g.fillRect(0,0,128,128); g.fillStyle="#fff"; g.font="900 96px sans-serif"; g.textAlign="center"; g.textBaseline="middle"; g.fillText(ch,64,70); g.strokeStyle="#3b2433"; g.lineWidth=8; g.strokeRect(4,4,120,120);
        const tx=new THREE.CanvasTexture(c); tx.encoding=THREE.sRGBEncoding; const m=new THREE.Mesh(new THREE.PlaneGeometry(3.1,3.1), new THREE.MeshStandardMaterial({map:tx, roughness:.9})); m.rotation.x=-Math.PI/2; m.position.set(ox[0]+dx+OX,.022,ox[1]+OZ); m.receiveShadow=true; G.add(m); G.userData["ox"+ch]=m; });
      SPOT.ox=[ox[0]+OX,1.4,ox[1]-2.6+OZ]; }
    { const pg=Sx.pg; SPOT.pgC=[pg[0]+OX,pg[1]+OZ]; busy.push([pg[0],pg[1],4]); disc(pg[0],pg[1],3.4,0xf1dca0);
      for(let i=0;i<16;i++){ const a=i/16*6.283; if(i===3||i===4) continue; prim(geo_("pgp",()=>new THREE.CylinderGeometry(.08,.08,.6,6)), [0xff7aa8,0xffd23f,0x7fd3ff,0x86dc7c][i%4], pg[0]+Math.cos(a)*3.5,.3,pg[1]+Math.sin(a)*3.5); }
      SPOT.pg=[pg[0]+OX,1.4,pg[1]+OZ];
      const sl=(a)=>{ const x=pg[0]+Math.cos(a)*4.6, z=pg[1]+Math.sin(a)*4.6, ry=-a+Math.PI/2;
        prim(geo_("slS",()=>new THREE.BoxGeometry(.7,1.1,.7)), 0xff7aa8, x,.55,z,{ry}); prim(geo_("slR",()=>new THREE.BoxGeometry(.8,.12,.8)), 0xffd23f, x,1.16,z,{ry});
        const fx=Math.sin(ry), fz=Math.cos(ry); prim(geo_("slD",()=>new THREE.BoxGeometry(.55,.07,1.7)), 0x5aa7ff, x+fx*.95,.6,z+fz*.95,{ry, rx:.62}); cols.push([x+OX+fx*.4,z+OZ+fz*.4,.9]); busy.push([x,z,1.6]); };
      const sw=(a)=>{ const x=pg[0]+Math.cos(a)*4.7, z=pg[1]+Math.sin(a)*4.7, ry=-a; const ux=Math.sin(ry), uz=Math.cos(ry);
        [-1,1].forEach(k=>prim(geo_("swL",()=>new THREE.CylinderGeometry(.05,.05,1.6,6)), 0xff9a3d, x+ux*k*.8,.78,z+uz*k*.8));
        prim(geo_("swT",()=>new THREE.CylinderGeometry(.05,.05,1.7,6)), 0xff9a3d, x,1.58,z,{ry, rz:Math.PI/2});
        [-.35,.35].forEach(k=>{ const sx=x+ux*k, sz=z+uz*k; prim(geo_("swR",()=>new THREE.CylinderGeometry(.012,.012,1.0,4)), 0x3b2433, sx,1.05,sz); prim(geo_("swS",()=>new THREE.BoxGeometry(.32,.05,.2)), 0x7fd36a, sx,.52,sz,{ry}); });
        cols.push([x+OX,z+OZ,.9]); busy.push([x,z,1.6]); };
      sl(Math.PI*.82); sw(Math.PI*1.22); }
    { const [cx,cz]=Sx.chest; const ch=new THREE.Group(); ch.position.set(cx+OX,0,cz+OZ); ch.rotation.y=Math.PI*.25; const bx=new THREE.Mesh(new THREE.BoxGeometry(1.1,.62,.75), MC(0xb07a4a)); bx.position.y=.31; ch.add(bx);
      const lid=new THREE.Group(); lid.position.set(0,.62,-.37); const lm=new THREE.Mesh(new THREE.BoxGeometry(1.14,.28,.79), MC(0xc98c55)); lm.position.set(0,.14,.37); lid.add(lm); ch.add(lid);
      [-.45,.45].forEach(x=>{ const b=new THREE.Mesh(new THREE.BoxGeometry(.1,.95,.8), MC(0xffd23f)); b.position.set(x,.45,0); ch.add(b); });
      ch.traverse(m=>{ if(m.isMesh) m.castShadow=true; }); G.add(ch); G.userData.chest=ch; G.userData.chestLid=lid; cols.push([cx+OX,cz+OZ,.7]); busy.push([cx,cz,1.3]); SPOT.chest=[cx+OX,1.4,cz+OZ]; }
    // 동네 땅 (열린 동네만) · 길 입구 아치 · 다음 동네 = 🚧
    MAP.hoods.slice(0,HN).forEach((h,i)=>MAP.hoodLots(h,i).forEach(L=>{ L.chunk="h"+i; lots.push(L); busy.push([L.x,L.z,1.6]); }));
    MAP.hoods.forEach((h,i)=>{ if(i<HN) arch(h,i,true); else if(i===HN){ const A=arch(h,i,false); SPOT.nu=[A.x+OX,1.4,A.z+OZ]; SPOT.nuName=h.ic+" "+h.id+" "+h.nm; } else arch(h,i,false); });
    /* (v544) 🏘 마을 시설 9곳 (proto/town-fac.js) — 나무보다 먼저 자리 잡음 */
    try{ if(window.TFAC) TFAC.build({G, OX, OZ, MAP, box, flush, prim, mesh, disc, kk, signTex, SIGNS, busy, cols, SPOT, MC, LIN, geo_, vcMerge}); }catch(e){ console.warn(e); }
    /* 얕은 물·해변 · 꽃밭 (나무보다 먼저 자리 잡음) */
    ISL.forEach(shore);
    const tryBed=(x,z,r)=>{ if(onPave(x,z,r+.25) || water(x,z) || !MAP.inside(x,z,1.5) || busy.some(([bx,bz,br])=>Math.hypot(x-bx,z-bz)<br+r*.6)) return; bed(x,z,r,"m"); };
    { for(let k=0;k<16;k++){ const a=k/16*6.283+.2; tryBed(Math.cos(a)*10.2, Math.sin(a)*10.2, .85); } [[14,-8],[-14,-6],[20,8],[-20,8],[8,-26],[-8,-30],[28,-12],[-34,-12],[40,10],[-44,8],[12,64],[-12,64],[46,-34],[-56,-2],[60,-4]].forEach(([x,z])=>tryBed(x,z,.9)); }   /* (v550) 광장 둘레 · 구역마다 꽃밭 */
    // 큰길 가로등
    Object.values(MAP.roads).forEach(r=>{ const Cc=MAP.curve(r.p), end=Cc.L[Cc.L.length-1]; for(let s=6, k=0; s<end-1; s+=6.5, k++){ const A=MAP.at(Cc.Q,Cc.L,s), sd=k%2?1:-1, x=A.x-A.tz*sd*(r.w/2+.45), z=A.z+A.tx*sd*(r.w/2+.45); if(!busy.some(([bx,bz,br])=>Math.hypot(x-bx,z-bz)<br) && !water(x,z)) kk("city","streetlight",x,z,{s:.9,chunk:"m",col:.2}); } });
    MAP.hoods.slice(0,HN).forEach((h)=>laneTrees(h)); MAP.hoods.slice(HN).forEach(h=>laneTrees(h));
    // 동네 길 가로등 (땅 사이 틈)
    MAP.hoods.slice(0,HN).forEach(h=>{ const Cc=MAP.curve(h.p); for(let k=0;k<MAP.PER-1;k+=2){ const s=h.s0+(k+.5)*MAP.GAP, A=MAP.at(Cc.Q,Cc.L,s), sd=(k/2)%2?1:-1; kk("city","streetlight",A.x-A.tz*sd*1.45,A.z+A.tx*sd*1.45,{s:.85,chunk:"m",col:.15}); } });
    const LOWD=typeof LOW!=="undefined" && LOW; trees(C,LOWD?520:950,"m");   /* 느린 기기 = 나무 줄임 */
    drawLots();
    if(myHouse){ const dx=Math.sin(myHouse.face), dz=Math.cos(myHouse.face); SPOT.home=[myHouse.x+OX+dx*1.25,1.3,myHouse.z+OZ+dz*1.25]; SPOT.homeIn=[myHouse.x+OX+dx*1.0,myHouse.z+OZ+dz*1.0]; }
    rocks(C, 200, "m"); bushes(C, 160, "m"); clouds();
    // 풀포기 · 들꽃 — (v536) 12칸 구역마다 (화면 밖은 안 그림)
    { const cells={}, CS=24; ISL.forEach(I=>{ for(let k=0;k<I.R*I.R*((typeof LOW!=="undefined" && LOW)?.4:.75);k++){ const a=rnd()*6.28, r=Math.sqrt(rnd())*rr(I,a)*.95, x=I.cx+Math.cos(a)*r, z=I.cz+Math.sin(a)*r; if(water(x,z) || onPave(x,z,.1)) continue; const key=Math.floor(x/CS)+"_"+Math.floor(z/CS); (cells[key]=cells[key]||[]).push([x,z,rnd()]); } });
      const g0=new THREE.ConeGeometry(.05,.24,3); g0.translate(0,.11,0); const f0=new THREE.IcosahedronGeometry(.075,0), d=new THREE.Object3D(), col=new THREE.Color();
      Object.keys(cells).forEach(key=>{ const gs=cells[key], [ci,cj]=key.split("_").map(Number), cx=(ci+.5)*CS, cz=(cj+.5)*CS, sph=new THREE.Sphere(new THREE.Vector3(0,.2,0), CS*.75);
        const geo=g0.clone(); geo.boundingSphere=sph; const im=new THREE.InstancedMesh(geo, MC(0x5aa845), gs.length*3); im.position.set(cx+OX,0,cz+OZ); let k=0;
        gs.forEach(([x,z,r])=>{ for(let j=0;j<3;j++){ d.position.set(x-cx+(j-1)*.06,0,z-cz+(j%2)*.04); d.rotation.set((j-1)*.35,r*6,0); d.scale.setScalar(.8+r*.6); d.updateMatrix(); im.setMatrixAt(k++, d.matrix); } }); G.add(im);
        const fl=gs.filter(g=>g[2]<.4); if(!fl.length) return; const fg=f0.clone(); fg.boundingSphere=sph.clone(); const fm=new THREE.InstancedMesh(fg, MC(0xffffff), fl.length); fm.position.set(cx+OX,0,cz+OZ);
        fl.forEach(([x,z,r],i)=>{ d.position.set(x-cx+.15,.08,z-cz-.1); d.rotation.set(0,r*6,0); d.scale.setScalar(1); d.updateMatrix(); fm.setMatrixAt(i,d.matrix); fm.setColorAt(i,col.set([0xff7aa8,0xffd23f,0xffffff,0xb28dff][Math.floor(r*97)%4])); }); G.add(fm); }); }
    for(let i=0;i<10;i++){ const a=i/10*6.283+0.3, d=95+rnd()*30; kk("nature",["mountain_A_grass_trees","mountain_B_grass_trees","hills_A_trees","hills_C_trees"][i%4],Math.cos(a)*d,Math.sin(a)*d,{s:1.6+rnd(),y:-0.76,chunk:"far",cast:false}); }
    merge(); mergeP(); walkmap();
    G.children.forEach(o=>{ if(!o.userData.solo) o.userData.noFade=1; });
    setTimeout(syncMine, 600);
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
  const PLC={key:"isle", N, g:G, h:3, name:"🏝 우리 마을", blocked, start:[OX-3,OZ-2], pitch:.55, follow:true, sky:0xa6dcf5};
  function doorCell(){ return SPOT.door || [OX-3,OZ-2]; }   /* 집이 없으면 = 광장 게시판 옆 (튜토리얼 시작) */
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
    if(m>.12 && !busy){ hero.path=[]; hero.then=null; if(hero.slide && !hero.slide.then) hero.slide=null; const fx=-Math.sin(yaw), fz=-Math.cos(yaw), rx=Math.cos(yaw), rz=-Math.sin(yaw), mx=rx*jx+fx*(-jy), mz=rz*jx+fz*(-jy), L=Math.hypot(mx,mz)||1, sp=SPD*(window.TFAC?TFAC.spd():1)*Math.min(1,m)*dt;
      const nx=p.x+mx/L*sp, nz=p.z+mz/L*sp, okc=(x,z)=>!blocked(Math.floor(x),Math.floor(z));
      if(okc(nx,nz)){ p.x=nx; p.z=nz; } else if(okc(nx,p.z)){ p.x=nx; } else if(okc(p.x,nz)){ p.z=nz; }
      hero.face=Math.atan2(mx,mz); hero.cx=Math.floor(p.x); hero.cz=Math.floor(p.z); hero.moving=true; hero.joy=true; anim=true;
      /* (v528) 타워처럼 — 앞으로 밀면 카메라가 천천히 등 뒤로 (손으로 돌린 뒤 1.5초는 그대로) */
      if(performance.now()-(CAM.dragAt||0)>1500){ const want=hero.face+Math.PI, d=((want-yaw)%(2*Math.PI)+3*Math.PI)%(2*Math.PI)-Math.PI, k=Math.min(1, dt*1.8*Math.max(0, -jy-.3)); if(k>0){ yaw+=d*k; yawTo=yaw; } } }
    else if(hero.joy){ hero.joy=false; if(!hero.path.length) hero.moving=false; anim=true; }
    if(J.air){ J.vy-=16*dt; p.y=Math.max(0, p.y+J.vy*dt); if(p.y<=0 && J.vy<0){ p.y=0; J.air=false; } hero.act=J.air?"air":(hero.act==="air"?"idle":hero.act); anim=true; }
    // 그림자 상자는 나를 따라감
    const dh=camera.position.distanceTo(p); for(const sp of SIGNS){ const o=Math.max(0,Math.min(1,(sp.position.distanceTo(camera.position)-(dh-3.5))/3)); if(Math.abs(sp.material.opacity-o)>.02){ sp.material.opacity=o; sp.visible=o>.03; anim=true; } }
    const s=sun.shadow.camera; sun.position.set(p.x-14, 26, p.z-7); sun.target.position.set(p.x,0,p.z); if(s.right!==16){ s.left=-16; s.right=16; s.top=16; s.bottom=-16; s.near=1; s.far=80; s.updateProjectionMatrix(); }
    if(!hero.joy && hero.moving && hero.path && hero.path.length && performance.now()-(CAM.dragAt||0)>1500){ const want=hero.face+Math.PI, d=((want-yaw)%(2*Math.PI)+3*Math.PI)%(2*Math.PI)-Math.PI; yaw+=d*Math.min(1,dt*.9); yawTo=yaw; }
    const st=G.userData.star; if(st){ st.rotation.y+=dt*1.5; st.position.y=3.1+Math.sin(performance.now()*.003)*.12; anim=true; }
    const fi=G.userData.fire; if(fi){ const t=performance.now()*.012; fi[0].scale.set(1,1+Math.sin(t)*.12,1); fi[1].scale.set(1,1+Math.cos(t*1.3)*.15,1); }
    try{ if(window.IPLAY && IPLAY.tick(dt)) anim=true; }catch(e){ console.warn(e); }
    try{ if(window.IHUD && IHUD.tick(dt)) anim=true; }catch(e){ console.warn(e); }
    return anim; }
  function show(on){ ui(); camUI(); document.body.classList.toggle("isleOn", !!on); if(on) camHint(); }
  /* ── 이름표 (가까이 가면) ── */
  function labels(){ const L=[];
    if(SPOT.home) L.push({k:"home", ic:"⭐", t:"내 집", p:SPOT.home, r:3, act:()=>walkTo(SPOT.door[0],SPOT.door[1],()=>enterHome())});
    if(SPOT.board) L.push({k:"board", ic:"📋", t:"땅 고르기", p:SPOT.board, r:3.4, act:()=>openLots()});
    (SPOT.shops||[]).forEach(S=>L.push({k:S.k, ic:S.ic, t:S.t, p:S.p, r:3, act:()=>shopGo(S)}));
    if(SPOT.lake) L.push({k:"lake", ic:"🎣", t:"같이 낚시", p:SPOT.lake, r:3.2, act:()=>{ const L=lake(); fishTap(Math.floor(L.x-1.5), Math.floor(L.z), L.x-1.4, L.z); }});
    if(SPOT.farm) L.push({k:"farm", ic:"🌱", t:"내 밭 가기 (마당)", p:SPOT.farm, r:4.5, act:()=>tripTo("yard")});
    if(SPOT.school) L.push({k:"school", ic:"🏫", t:"학교 · 공부하기", p:SPOT.school, r:3.4, act:()=>ask("🏫 공부하러 갈까요?<br><small>Daily 30 을 하면 🪱 미끼를 받아요</small>", ()=>{ location.href="../index.html"; })});
    if(SPOT.tower) L.push({k:"tower", ic:"🗼", t:"하늘 타워", p:SPOT.tower, r:3.6, act:()=>towerAsk()});
    if(SPOT.mine) L.push({k:"mine", ic:"⛏", t:"광산", p:SPOT.mine, r:3.4, act:()=>tripTo("mine")});
    if(SPOT.nu) L.push({k:"nu", ic:"🚧", t:(SPOT.nuName||"새 동네")+" (친구가 오면)", p:SPOT.nu, r:4, act:()=>toast("🚧 학원 친구가 늘면 <b>새 동네</b>가 여기에 생겨요!", 2600)});
    if(SPOT.camp) L.push({k:"camp", ic:"🔥", t:"모닥불", p:SPOT.camp, r:2.6, act:()=>{ hero.act="sit"; hero.actT=0; toast("🔥 따뜻해요 — 친구들이 모이는 곳이에요", 2200); }});
    try{ if(window.TFAC) TFAC.labels(L); }catch(e){ console.warn(e); }
    return L; }
  /* (v539) 가게 — 문 앞까지 걸어가서 그 가게 창 */
  function shopGo(S){ const run=()=>{ const k=S.k; if(k==="fish") openShop(); else if(k==="furn") openFurn("furn"); else if(k==="clothes") openAv("clothes"); else if(k==="hair") openAv("hair"); else if(k==="mart"){ try{ HLIFE.openMart(); }catch(e){} } else if(k==="town") tripTo("village"); else if(window.TFAC && k==="snack") TFAC.openSnack(); else if(window.TFAC && k==="pet") TFAC.openPet(); else if(window.TFAC && k==="photo") TFAC.openPhoto(); try{ tEv("shop_"+k); }catch(e){} };
    const go_=(window.SHOPIN && SHOPIN.has(S.k)) ? ()=>{ if(!SHOPIN.enter(S, run)) run(); } : run;   /* (v572) 🏪 가게 안으로 들어가서 → 카운터에서 창 */
    const c=[Math.floor(S.door[0]), Math.floor(S.door[1])]; if(Math.hypot(hero.g.position.x-S.door[0], hero.g.position.z-S.door[1])<2.2 || blocked(c[0],c[1])) go_(); else walkTo(c[0],c[1],go_); }
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
#lotP .lb,#hsP .lb{width:min(560px,100%);max-height:92vh;overflow:auto;background:#fff8ea;border:3px solid #3b2433;border-bottom:0;border-radius:26px 26px 0 0;padding:12px 14px calc(14px + env(safe-area-inset-bottom));font-family:var(--kr);color:#3b2433}
#lotP h3,#hsP h3{margin:2px 4px 8px;font-weight:400;font-size:20px;display:flex;align-items:center;gap:8px} #lotP h3 small,#hsP h3 small{font-size:12.5px;color:#9a7e63;flex:1}
#lotP .x,#hsP .x{width:38px;height:38px;border-radius:50%;border:3px solid #3b2433;background:#fffdf7;box-shadow:0 3px 0 #3b2433;font-size:16px;color:#3b2433}
.lotT{display:flex;gap:6px;margin-bottom:8px}.lotT button{flex:1;height:42px;border-radius:14px;border:3px solid #3b2433;background:#fffdf7;font:16px var(--kr);color:#3b2433;box-shadow:0 3px 0 #3b2433}.lotT button.on{background:#ffd23f}
.lotT button em{font-style:normal;font-size:11.5px;color:#7a5b3a;margin-left:3px}
#lotMap{display:block;width:100%;height:auto;touch-action:manipulation}
.lotK{display:flex;flex-wrap:wrap;gap:6px 12px;font-size:12.5px;margin:6px 4px 8px;color:#6a5040}.lotK i{display:inline-block;width:14px;height:14px;border-radius:4px;border:2px solid #3b2433;vertical-align:-2px;margin-right:4px}
.lotSel{display:flex;align-items:center;gap:10px;background:#fffdf7;border:3px solid #3b2433;border-radius:18px;padding:8px 10px;box-shadow:0 3px 0 #3b2433;min-height:62px}
.lotSel b{font-weight:400;font-size:17px;display:block} .lotSel small{font-size:12.5px;color:#9a7e63}
.lotSel .go{margin-left:auto;height:46px;border-radius:14px;border:3px solid #3b2433;padding:0 16px;font:17px var(--kr);color:#fff;background:linear-gradient(180deg,#86dc7c,#4caf50);box-shadow:0 3px 0 #3b2433;text-shadow:0 1px 0 rgba(30,80,30,.45);white-space:nowrap}
.lotSel .go[disabled]{filter:grayscale(.8);opacity:.6}`; document.head.appendChild(st);
    const d=document.createElement("div"); d.id="lotP"; d.innerHTML='<div class="lb"><h3>🏡 땅 고르기<small>빈 땅을 누르면 내 집이 그리로 옮겨가요</small><button class="x" id="lotX" aria-label="닫기">✕</button></h3><div class="lotT" id="lotT"></div><svg id="lotMap" viewBox="-114 -82 228 164"></svg>'
      +'<div class="lotK"><span><i style="background:#ffd23f"></i>내 집</span><span><i style="background:#9fd884"></i>친구 집</span><span><i style="background:#fff;border-style:dashed"></i>빈 땅</span><span><i style="background:#fff3bf"></i>⭐ 바다 앞 좋은 자리</span></div><div class="lotSel" id="lotSel"></div></div>';
    document.body.appendChild(d);
    d.addEventListener("click", e=>{ if(e.target===d || e.target.id==="lotX"){ d.classList.remove("on"); return; }
      const tb=e.target.closest("[data-hood]"); if(tb){ lotHood=tb.dataset.hood; lotSel=null; drawLotP(); return; }
      const g=e.target.closest("[data-lot]"); if(g){ lotSel=g.dataset.lot; drawLotP(); try{ SND.pop && SND.pop(); }catch(_){} return; }
      if(e.target.id==="lotGo") pickLot(lotSel); });
    ["pointerdown","pointerup"].forEach(ev=>d.addEventListener(ev, e=>e.stopPropagation())); }
  function lotState(L){ const sd=studyDays(); return L.me ? "me" : L.owner ? "friend" : (L.prem && sd<PREM_DAYS) ? "lock" : "free"; }
  function drawLotP(){ const H=HOODS.slice(0,hoodCount()).map(h=>h[0]), cnt=h=>lots.filter(L=>L.hood===h && !L.owner).length;
    $("lotT").innerHTML=H.map(h=>{ const hi=hoodInfo(h); return '<button data-hood="'+h+'" class="'+(h===lotHood?"on":"")+'">'+hi.ic+' '+h+(myHouse&&myHouse.hood===h?" ⭐":"")+'<em>빈 '+cnt(h)+'</em></button>'; }).join("");
    /* (v536) 이름 있는 길 — 아이가 보기 쉽게 곧게 펼친 길 (위·아래 8칸씩) · 왼쪽 = 광장 쪽 · 오른쪽 끝 = ⭐ 좋은 자리 */
    const hi=hoodInfo(lotHood), HL=lots.filter(L=>L.hood===lotHood); const CW=24.6, X0=-98, Y0=-14;
    let s='<rect x="-112" y="-80" width="224" height="160" rx="20" fill="#86c96a" stroke="#3b2433" stroke-width="3"/>';
    s+='<rect x="-110" y="-9" width="220" height="18" fill="#dcbf86"/><rect x="-110" y="-10" width="220" height="2" fill="#bf9f6a"/><rect x="-110" y="8" width="220" height="2" fill="#bf9f6a"/>';
    s+='<text x="-104" y="4" font-size="8" fill="#6a5040">'+(hi.from?"🛣":"⛲")+'</text><text x="0" y="-66" font-size="11" text-anchor="middle" fill="#3b2433">'+hi.ic+' '+hi.id+' '+hi.nm+'</text>';
    s+='<text x="0" y="74" font-size="8" text-anchor="middle" fill="#3b2433">'+(hi.from?"← 큰길 쪽":"← 광장 쪽")+' · 끝 ⭐ = 좋은 자리 →</text>';
    const RC=!myHouse && recLot();
    HL.forEach(L=>{ const k=Math.floor((L.n-1)/2), up=L.n%2===1, w=22, x=X0+k*CW+w/2-4, y=up?-36:36, st=lotState(L), sel=lotSel===L.id;
      const fill=st==="me"?"#ffd23f":st==="friend"?"#9fd884":L.prem?"#fff3bf":"#fff", dash=(st==="free"||st==="lock")?' stroke-dasharray="4 3"':'';
      s+='<g data-lot="'+L.id+'" style="cursor:pointer"><rect x="'+(x-w/2)+'" y="'+(y-w/2)+'" width="'+w+'" height="'+w+'" rx="5" fill="'+fill+'" stroke="'+(sel?"#ff5d6c":"#3b2433")+'" stroke-width="'+(sel?3.5:2)+'"'+dash+'/>';
      s+='<rect x="'+(x-3)+'" y="'+(up?y+w/2:y-w/2-6)+'" width="6" height="6" fill="#c9a46a"/>';
      const ic=st==="me"?"⭐":st==="friend"?"🏠":st==="lock"?"🔒":L.prem?"⭐":"＋";
      s+='<text x="'+x+'" y="'+(y+(st==="friend"||st==="me"?0:4))+'" font-size="'+(st==="free"&&!L.prem?13:11)+'" text-anchor="middle" fill="#3b2433">'+ic+'</text>';
      if(st==="friend"||st==="me") s+='<text x="'+x+'" y="'+(y+(up?-14:19))+'" font-size="6.5" text-anchor="middle" fill="#3b2433">'+(st==="me"?"내 집":esc(L.owner))+'</text>';
      else if(RC && RC.id===L.id) s+='<text x="'+x+'" y="'+(y+(up?-14:19))+'" font-size="7" text-anchor="middle" fill="#e8572a">👍 추천</text>';
      s+='</g>'; });
    $("lotMap").innerHTML=s;
    const L=lots.find(L=>L.id===lotSel), sd=studyDays();
    $("lotSel").innerHTML = !L ? '<div><b>빈 땅을 눌러 보세요</b><small>'+(myHouse?'지금 내 집: '+myHouse.hood+' '+myHouse.n+'번 땅':'')+'</small></div>'
      : '<div><b>'+L.hood+' '+L.n+'번 땅'+(L.prem?' · ⭐ 바다 앞':'')+'</b><small>'+(lotState(L)==="friend"?esc(L.owner)+' 의 집이에요':lotState(L)==="me"?'지금 내 집이에요':lotState(L)==="lock"?'공부한 날 '+PREM_DAYS+'일부터 (지금 '+sd+'일) — Daily 30 을 해요':'여기로 이사할 수 있어요')+'</small></div>'
        +'<button class="go" id="lotGo"'+(lotState(L)==="free"?'':' disabled')+'>'+(myHouse?'여기로 할래요':'🔨 여기에 집 짓기')+'</button>'; }
  async function openLots(){ lotCSS(); await loadLots(); owners(); lotSel=null; if(myHouse) lotHood=myHouse.hood; else { const R=recLot(); if(R){ lotHood=R.hood; lotSel=R.id; } } drawLotP(); $("lotP").classList.add("on"); }
  function pickLot(id){ const L=lots.find(L=>L.id===id); if(!L || lotState(L)!=="free") return; const first=!myHouse;
    ask(first ? "🏡 <b>"+hoodInfo(L.hood).ic+" "+L.hood+" "+L.n+"번 땅</b>에 내 집을 지을까요?" : "🏡 <b>"+L.hood+" "+L.n+"번 땅</b>으로 이사할까요?"+(L.prem?"<br><small>⭐ 바다 앞 좋은 자리예요</small>":""), async ()=>{
      $("lotP").classList.remove("on"); toast(first?"🔨 집을 짓는 중…":"🚚 이사하는 중…", 1500); const r=await claim(id);
      if(first && (r==="ok"||r==="local")){ setTimeout(()=>{ rebuild(); try{ const d=doorCell(); hero.path=[]; hero.moving=false; hero.slide=null; hero.cx=d[0]; hero.cz=d[1]; hero.g.position.set(d[0]+.5,0,d[1]+.5); hero.face=myHouse.face+Math.PI; yaw=yawTo=myHouse.face; camSnap=true; placeCamera(); }catch(e){ console.warn(e); } drawLabels(); riseHouse();   /* 내 땅 앞으로 와서 집이 솟는 걸 봄 */ try{ if(!store("hyeng_proto_gift")) store("hyeng_proto_gift","due"); tEv("lot"); }catch(e){} try{ SND.big(); }catch(e){} toast("🎉 <b>내 집이 생겼어요!</b><br><small>"+hoodInfo(L.hood).ic+" "+L.hood+" "+hoodInfo(L.hood).nm+" "+L.n+"번 땅 · ⭐ 내 집을 눌러 들어가요</small>", 3400); }, 400); return; }
      if(r==="taken"){ toast("😮 방금 친구가 그 땅을 골랐어요 — 다른 땅을 골라 봐요", 2600); await loadLots(); rebuild(); drawLabels(); return; }
      if(r==="err"){ toast("📡 인터넷이 잠깐 안 돼요 — 다시 해 봐요", 2400); return; }
      setTimeout(()=>{ rebuild(); const d=doorCell(); hero.path=[]; hero.moving=false; hero.slide=null; hero.cx=d[0]; hero.cz=d[1]; hero.g.position.set(d[0]+.5,0,d[1]+.5); faceOut(); drawLabels(); placeCamera();
        try{ confetti && confetti(); }catch(e){} toast("🎉 새 집이에요! <b>"+L.hood+" "+L.n+"번 땅</b>", 2600); }, 400); }); }
  /* (v539) 집이 생기는 순간 — 땅에서 쑥 올라오며 통통 + 먼지 */
  function riseHouse(){ const L=myHouse; if(!L || !L.obj) return; const W_=L.obj, y0=W_.position.y, t0=performance.now();
    const dust=[]; for(let i=0;i<10;i++){ const m=new THREE.Mesh(geo_("dust",()=>new THREE.IcosahedronGeometry(.25,0)), new THREE.MeshBasicMaterial({color:0xf3e2c0, transparent:true, opacity:.9})); const a=i/10*6.283; m.position.set(L.x+OX+Math.cos(a)*1.1,.2,L.z+OZ+Math.sin(a)*1.1); m.userData.v=[Math.cos(a)*1.4,1.2,Math.sin(a)*1.4]; G.add(m); dust.push(m); }
    const step=()=>{ const t=Math.min(1,(performance.now()-t0)/900), e=t<.7 ? t/.7 : 1+Math.sin((t-.7)/.3*Math.PI)*.08; W_.position.y=y0-2.6*(1-Math.min(1,e))+(t>=.7?(e-1)*1.2:0);
      dust.forEach(m=>{ const v=m.userData.v; m.position.x+=v[0]*.016; m.position.y+=v[1]*.016; m.position.z+=v[2]*.016; m.material.opacity=Math.max(0,.9-t); m.scale.setScalar(1+t); }); dirty=true;
      if(t<1) requestAnimationFrame(step); else { W_.position.y=y0; dust.forEach(m=>{ G.remove(m); m.material.dispose(); }); } }; step(); }
  /* (v535) 🏡 내 집 꾸미기 — 모양 A·B · 색 4 · 공부한 날만큼 자라는 단계 */
  function houseSVG(h, big){ const sh=h[0], c={red:["#ff6b6b","#c94545"],blue:["#5aa7ff","#2f6fc4"],yellow:["#ffc93d","#c9901a"],green:["#5cc46a","#2f8f3f"]}[h.slice(2)]||["#ff6b6b","#c94545"], W=big?120:64;
    if(sh==="M"){ const fl=big ? (()=>{ try{ return HOMEX.floors(); }catch(e){ return 1; } })() : 2, fh=Math.min(16, 40/fl); let g='';
      for(let i=0;i<fl;i++){ const y=56-(i+1)*fh, x=i%2?16:12; g+='<rect x="'+x+'" y="'+y+'" width="34" height="'+fh+'" fill="'+(i%2?"#ece6da":"#f7f4ee")+'" stroke="#3b2433" stroke-width="2"/><rect x="'+(x+3)+'" y="'+(y+fh*.22)+'" width="18" height="'+(fh*.5)+'" fill="#2c4a66"/><rect x="'+(x+25)+'" y="'+(y+2)+'" width="6" height="'+(fh-4)+'" fill="#b07a4a"/><rect x="'+(x-2)+'" y="'+(y-2.5)+'" width="38" height="3" fill="#4a4450"/>'; }
      g+='<rect x="18" y="'+(56-fh*.62)+'" width="6" height="'+(fh*.62)+'" fill="'+c[0]+'" stroke="#3b2433" stroke-width="1.4"/><rect x="'+(13)+'" y="'+(56-fh*fl-9)+'" width="38" height="6" fill="#bfe6ff" stroke="#3b2433" stroke-width="1.2" opacity=".85"/>';
      return '<svg viewBox="0 0 64 62" width="'+(big?120:64)+'" height="'+Math.round((big?120:64)*62/64)+'"><ellipse cx="32" cy="57" rx="27" ry="4" fill="#86c96a"/>'+g+'</svg>'; }
    const body=sh==="A" ? '<rect x="18" y="34" width="28" height="22" rx="2" fill="#fff6e6" stroke="#3b2433" stroke-width="2.5"/><path d="M12 36 L32 14 L52 36 Z" fill="'+c[0]+'" stroke="#3b2433" stroke-width="2.5" stroke-linejoin="round"/><rect x="28" y="44" width="8" height="12" rx="1.5" fill="#a0683c" stroke="#3b2433" stroke-width="2"/><rect x="38" y="40" width="6" height="6" fill="#bfeaff" stroke="#3b2433" stroke-width="1.6"/>'
      : '<rect x="12" y="34" width="40" height="22" rx="2" fill="#fff6e6" stroke="#3b2433" stroke-width="2.5"/><rect x="40" y="16" width="6" height="12" fill="'+c[1]+'" stroke="#3b2433" stroke-width="2"/><path d="M7 36 L20 20 L44 20 L57 36 Z" fill="'+c[0]+'" stroke="#3b2433" stroke-width="2.5" stroke-linejoin="round"/><rect x="28" y="44" width="8" height="12" rx="1.5" fill="#a0683c" stroke="#3b2433" stroke-width="2"/><rect x="16" y="40" width="7" height="7" fill="#bfeaff" stroke="#3b2433" stroke-width="1.6"/><rect x="41" y="40" width="7" height="7" fill="#bfeaff" stroke="#3b2433" stroke-width="1.6"/>';
    return '<svg viewBox="0 0 64 62" width="'+W+'" height="'+Math.round(W*62/64)+'"><ellipse cx="32" cy="57" rx="27" ry="4" fill="#86c96a"/>'+body+'</svg>'; }
  function hsCSS(){ if($("hsP")) return; lotCSS(); const st=document.createElement("style"); st.textContent=`
#hsP{position:fixed;inset:0;z-index:20;display:none;background:rgba(30,18,40,.42);align-items:flex-end;justify-content:center} #hsP.on{display:flex}
.hsTop{display:flex;align-items:center;gap:12px;background:#fffdf7;border:3px solid #3b2433;border-radius:20px;padding:8px 12px;box-shadow:0 3px 0 #3b2433;margin-bottom:10px}
.hsTop b{font-weight:400;font-size:18px;display:block}.hsTop small{font-size:12.5px;color:#9a7e63}
.hsL{font-size:14px;margin:10px 4px 6px;color:#6a5040}
.hsG{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}
.hsG button{border:3px solid #3b2433;border-radius:16px;background:#fffdf7;box-shadow:0 3px 0 #3b2433;padding:4px 0 2px;font:13px var(--kr);color:#3b2433;display:flex;flex-direction:column;align-items:center}
.hsG button.on{background:#fff3bf;outline:3px solid #ffd23f}
.hsT{display:flex;gap:6px;margin-top:4px}.hsT div{flex:1;border:2.5px solid #3b2433;border-radius:14px;padding:6px 2px;text-align:center;font-size:12px;background:#fffdf7;opacity:.55}
.hsT div.on{opacity:1;background:#eaffdf}.hsT div.now{outline:3px solid #4caf50}.hsT i{display:block;font-size:22px;font-style:normal}
.hsN{margin:10px 2px 0;font-size:13px;text-align:center;color:#6a5040}`; document.head.appendChild(st);
    const d=document.createElement("div"); d.id="hsP"; d.innerHTML='<div class="lb"><h3>🏡 내 집 꾸미기<small>누르면 바로 바뀌어요 · 친구들 화면에도</small><button class="x" id="hsX" aria-label="닫기">✕</button></h3><div id="hsB"></div></div>'; document.body.appendChild(d);
    d.addEventListener("click", e=>{ if(e.target===d || e.target.id==="hsX"){ d.classList.remove("on"); return; } const b=e.target.closest("[data-hs]"); if(b) setStyle(b.dataset.hs); });
    ["pointerdown","pointerup"].forEach(ev=>d.addEventListener(ev, e=>e.stopPropagation())); try{ SHEETS.push("hsP"); }catch(e){} }
  function drawHs(){ const L=myHouse, h=L ? styleOf(L) : (myStyle()||"A_red"), sd=studyDays(), t=tierOf(sd), nx=TIER[t];
    let s='<div class="hsTop">'+houseSVG(h,1)+'<div><b>'+(L?L.hood+' '+L.n+'번 땅':'내 집')+'</b><small>'+TIER[t-1].ic+' '+t+'단계 · '+TIER[t-1].t+'<br>🏢 '+(()=>{ try{ return HOMEX.floors(); }catch(e){ return 1; } })()+'층 (집 안 🏗 넓히기) · 공부한 날 '+sd+'일'+(nx?' · '+nx.ic+' '+(t+1)+'단계까지 '+(nx.d-sd)+'일':' · 가장 큰 집!')+'</small></div></div>';
    s+='<div class="hsL">🏠 모양 · 색</div><div class="hsG">'+HSH.map(a=>HCOL.map(c=>{ const k=a+"_"+c; return '<button data-hs="'+k+'" class="'+(k===h?"on":"")+'">'+houseSVG(k)+({A:"뾰족 ",B:"넓은 ",M:"모던 "})[a]+HCOLK[c]+'</button>'; }).join("")).join("")+'</div>';
    s+='<div class="hsL">🌱 공부하면 집이 자라요 <small>(Daily 30 한 날)</small></div><div class="hsT">'+TIER.map((T,i)=>'<div class="'+(i<t?"on":"")+(i===t-1?" now":"")+'"><i>'+T.ic+'</i>'+(i+1)+'단계<br><small>'+T.d+'일~</small><br>'+T.t+'</div>').join("")+'</div>';
    s+='<p class="hsN">집 모양은 언제든 바꿀 수 있어요 · 다른 땅으로 옮기려면 광장 📋 게시판</p>';
    $("hsB").innerHTML=s; }
  function openHouse(){ hsCSS(); drawHs(); $("hsP").classList.add("on"); }
  function setStyle(h){ if(!/^[ABM]_(red|blue|yellow|green)$/.test(h)) return; store("hyeng_proto_ihouse", h); const L=myHouse; try{ SND.pop && SND.pop(); }catch(_){}
    if(L && L.obj){ const W_=L.obj; if(W_.parent) W_.parent.remove(W_); try{ faded.delete && faded.delete(W_); }catch(e){} L.style=h; L.fl=floorsLot(L); L.obj=houseObj(L); if(L.obj) L.obj.userData.lot=L; try{ TOON.scan(L.obj); }catch(e){} dirty=true; }
    if(L && L.rec && srvOk){ NET.patch(LOTP+"/"+L.id, {h}).then(()=>{ L.rec.h=h; }).catch(()=>{}); }
    drawHs(); }
  function syncMine(){ const L=myHouse; if(!L || !L.rec || !srvOk) return; const up={}, t=tierOf(studyDays()), h=styleOf(L), f=floorsLot(L); if(+L.rec.t!==t) up.t=t; if(L.rec.h!==h) up.h=h; if((+L.rec.f||1)!==f) up.f=f;
    if(Object.keys(up).length) NET.patch(LOTP+"/"+L.id, up).then(()=>Object.assign(L.rec, up)).catch(()=>{}); }
  /* 🎣 호수 (같이 낚시) — house.html pondCtx 가 씀 */
  const LKD=[MAP.spots.lake.x, MAP.spots.lake.z, MAP.spots.lake.rx, MAP.spots.lake.rz];
  function lake(){ return {x:LKD[0]+OX, z:LKD[1]+OZ, hw:LKD[2]*.72, hd:LKD[3]*.72, wl:-.18, g:G}; }
  function waterCell(x,z){ return water(x+.5-OX, z+.5-OZ); }
  function enterHome(){ go("room", null, ()=>{ try{ HOMEX.toLiving(); }catch(e){} PL.room.start=!roomBlocked(1,RN-1)?[1,RN-1]:[0,RN-1]; }, {from:()=>[0.05,RN-0.5], door:roomDoor}); }
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
  return {riseHouse, recLot, openHouse, setStyle, styleOf, tierOf, TIER, syncMine, stuckDoors, ensureDoors, reachFrom, plazaCell, doorCellOf, onBuild:f=>onB.push(f), MC, W, ON, CAM, lake, waterCell, claim, loadLots, autoClaim, myKey, hoodCount, houseAt, visitLot, doorOf, SRV:()=>SRV, D, HOODS, LOT, HOODR, inIsle:(x,z)=>ISL.some(I=>inIsle(I,x-OX,z-OZ,.4)), onPave:(x,z)=>onPave(x-OX,z-OZ), busyAt:(x,z,r)=>busy.some(([bx,bz,br])=>Math.hypot(x-OX-bx,z-OZ-bz)<br+(r||0)), faceOut, back, ready, G, PLC, N, OX, OZ, S, build, enter, tick, show, labels, tap, blocked, nameOk, gate, SPOT, lots, rebuild, openLots, pickLot, lotState, studyDays, myHouse:()=>myHouse, W, J, doorCell, enterHome};
})();
window.ISLE=ISLE; PL.isle=ISLE.PLC; LBL_DEF.isle=ISLE.labels; LBL_NEAR.isle=1;
