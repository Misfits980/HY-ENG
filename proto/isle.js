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
  const S=1.05, HX=2, HZ=1.7320508, HR=S*1.1547, N=96, OX=48, OZ=60;
  const G=new THREE.Group(); G.name="isle"; G.visible=false; scene.add(G);
  const W=new Uint8Array(N*N);              // 1 = 걸을 수 있음
  const cols=[];                            // 막는 동그라미 [x,z,r]
  const bridges=[];                         // [ax,az,bx,bz,반폭]
  const islands=[];                         // {cx,cz,R,cells}
  let seed=7; const rnd=()=>{ seed=(seed*9301+49297)%233280; return seed/233280; };
  const MT={}; const MC=(c)=>MT[c]||(MT[c]=new THREE.MeshStandardMaterial({color:c, roughness:.85}));
  const dist=(a,b)=>(Math.abs(a)+Math.abs(b)+Math.abs(a+b))/2;
  const hp=(q,r)=>[S*HX*(q+r/2), S*HZ*r];
  /* ── 합치기 — KayKit 모델 놓을 자리만 모아 두었다가 묶음마다 한 덩어리 ── */
  const bag={};   // key = 묶음|덩어리 → [{g, m}]
  function kk(pack,k,x,z,o){ o=o||{}; const R=KK.R[pack]; if(!R || !R.G[k]) return null; const g=R.G[k], bb=g.boundingBox; let s=(o.s||1)*S;
    const M4=new THREE.Matrix4().compose(new THREE.Vector3(x+OX, o.y||0, z+OZ), new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,1,0), o.ry||0), new THREE.Vector3(s,s,s))
      .multiply(new THREE.Matrix4().makeTranslation(-(bb.min.x+bb.max.x)/2, -bb.min.y, -(bb.min.z+bb.max.z)/2));
    const key=pack+"|"+(o.chunk||"c"); (bag[key]=bag[key]||[]).push({g, m:M4, cast:o.cast!==false}); if(o.col) cols.push([x+OX, z+OZ, o.col]); return true; }
  function merge(){ Object.keys(bag).forEach(key=>{ const pack=key.split("|")[0], L=bag[key], R=KK.R[pack];
      let nv=0, ni=0; L.forEach(e=>{ nv+=e.g.attributes.position.count; ni+=e.g.index.count; });
      const P=new Float32Array(nv*3), Nn=new Float32Array(nv*3), U=new Float32Array(nv*2), I=new Uint32Array(ni); let ov=0, oi=0; const v=new THREE.Vector3(), nm=new THREE.Matrix3();
      L.forEach(e=>{ const g=e.g, pa=g.attributes.position, na=g.attributes.normal, ua=g.attributes.uv, ix=g.index; nm.getNormalMatrix(e.m); const uk=(ua.normalized && ua.array instanceof Uint16Array) ? 1/65535 : 1;   /* r128 getX 는 정규화 안 함 */
        for(let i=0;i<pa.count;i++){ v.fromBufferAttribute(pa,i).applyMatrix4(e.m); P.set([v.x,v.y,v.z],(ov+i)*3); v.fromBufferAttribute(na,i).applyMatrix3(nm).normalize(); Nn.set([v.x,v.y,v.z],(ov+i)*3); U[(ov+i)*2]=ua.getX(i)*uk; U[(ov+i)*2+1]=ua.getY(i)*uk; }
        for(let i=0;i<ix.count;i++) I[oi+i]=ix.getX(i)+ov; ov+=pa.count; oi+=ix.count; });
      const geo=new THREE.BufferGeometry(); geo.setAttribute("position", new THREE.BufferAttribute(P,3)); geo.setAttribute("normal", new THREE.BufferAttribute(Nn,3)); geo.setAttribute("uv", new THREE.BufferAttribute(U,2)); geo.setIndex(new THREE.BufferAttribute(I,1)); geo.computeBoundingSphere();
      const m=new THREE.Mesh(geo, R.mat); m.castShadow=true; m.receiveShadow=true; G.add(m); });
    Object.keys(bag).forEach(k=>delete bag[k]); }
  /* 길·광장·밭 덮개 = 육각 판 (색마다 InstancedMesh 하나) */
  const caps={};
  function cap(x,z,col,h){ (caps[col+"|"+(h||.06)]=caps[col+"|"+(h||.06)]||[]).push([x+OX,z+OZ]); }
  function drawCaps(){ Object.keys(caps).forEach(k=>{ const [col,h]=k.split("|"), L=caps[k], hh=+h; const geo=new THREE.CylinderGeometry(HR*.99,HR*.99,hh,6); geo.translate(0,hh/2+.005,0);
      const im=new THREE.InstancedMesh(geo, MC(+col), L.length), d=new THREE.Object3D(); L.forEach(([x,z],i)=>{ d.position.set(x,0,z); d.updateMatrix(); im.setMatrixAt(i,d.matrix); }); im.receiveShadow=true; G.add(im); }); }
  function mesh(geo, col, x, y, z, o){ const m=new THREE.Mesh(geo, o&&o.basic ? new THREE.MeshBasicMaterial({color:col}) : MC(col)); m.position.set(x+OX,y,z+OZ); m.castShadow=!(o&&o.nocast); m.receiveShadow=true; G.add(m); return m; }
  /* ── 섬 ── */
  function island(cx,cz,R,fn,chunk){ const cells=[]; for(let a=-R;a<=R;a++) for(let b=-R;b<=R;b++){ if(dist(a,b)>R) continue; const [x,z]=hp(a,b); const c={q:a,r:b,x:x+cx,z:z+cz,lx:x/S,lz:z/S,t:"grass",d:dist(a,b),R}; if(fn) fn(c); cells.push(c); }
    cells.forEach(c=>kk("isle", c.t==="water"?"hex_water":"hex_grass", c.x, c.z, {y:-S, chunk})); islands.push({cx,cz,R,cells}); return cells; }
  const TR=["trees_A_large","trees_A_medium","trees_B_large","trees_B_medium","tree_single_A","tree_single_B","trees_A_small"];
  function trees(cells,p,chunk){ cells.forEach(c=>{ if(c.t!=="grass") return; const e=c.d>=c.R?p[0]:c.d>=c.R-1?p[1]:p[2]; if(rnd()<e){ const x=c.x+(rnd()-.5)*S*.4, z=c.z+(rnd()-.5)*S*.4; const k=c.d>=c.R ? (rnd()<.75?"tree_single_A":"trees_A_small") : TR[Math.floor(rnd()*TR.length)]; kk("isle",k,x,z,{s:1.1,ry:rnd()*6,chunk,col:.55*S}); }   /* 가장자리는 가벼운 나무 */ }); }
  function bridge(x1,z1,x2,z2){ const dx=x2-x1, dz=z2-z1, L=Math.hypot(dx,dz), a=Math.atan2(dx,dz); const B=new THREE.Group(); B.position.set(x1+OX,0,z1+OZ); B.rotation.y=a; G.add(B);
    const n=Math.max(2,Math.round(L/0.46)); for(let i=0;i<n;i++){ const pl=new THREE.Mesh(new THREE.BoxGeometry(1.5,.11,.42), MC(i%2?0xb07a4a:0x9a6a40)); pl.position.set(0,.025,i*(L/n)+.2); pl.receiveShadow=true; B.add(pl); }
    for(let i=0;i<=n;i+=3){ [-.76,.76].forEach(s=>{ const po=new THREE.Mesh(new THREE.CylinderGeometry(.065,.065,.8,6), MC(0x7a4f2c)); po.position.set(s,.1,i*(L/n)); B.add(po); }); }
    [-.76,.76].forEach(s=>{ const rl=new THREE.Mesh(new THREE.BoxGeometry(.06,.06,L), MC(0x7a4f2c)); rl.position.set(s,.42,L/2); B.add(rl); });
    bridges.push([x1+OX,z1+OZ,x2+OX,z2+OZ,.62]); }
  function link(A,ra,B,rb){ const dx=B[0]-A[0], dz=B[1]-A[1], L=Math.hypot(dx,dz), ux=dx/L, uz=dz/L; bridge(A[0]+ux*ra,A[1]+uz*ra,B[0]-ux*rb,B[1]-uz*rb); }
  /* 동네 = 집 터 고리 (d=3, 18칸) · 빈 터(5번째마다) = 새 친구 자리 */
  const HC=["building_home_A_red","building_home_B_blue","building_home_A_yellow","building_home_B_green","building_home_A_blue","building_home_B_red","building_home_A_green","building_home_B_yellow"];
  const slots=[];   // {x,z,face,hood,i,empty}
  function hood(cx,cz,name,chunk){ const cells=island(cx,cz,4,c=>{ if(c.d<=1) c.t="sq"; },chunk);
    cells.filter(c=>c.t==="sq").forEach(c=>cap(c.x,c.z,0xa8834a));
    kk("city","streetlight",cx,cz,{s:1,chunk,col:.2}); kk("city","bench",cx+S*1.4,cz,{s:.9,ry:Math.PI/2,chunk,col:.4});
    let k=0; cells.filter(c=>c.d===3).forEach(c=>{ k++; const face=Math.atan2(cx-c.x, cz-c.z); const sl={x:c.x,z:c.z,face,hood:name,i:k,empty:k%5===0}; slots.push(sl); c.t="house"; });
    trees(cells,[0.7,0.15,0.05],chunk); return cells; }
  const D={plaza:[0,0], d1:[0,-26*S], d2:[-23*S,-15*S], d3:[23*S,-15*S], nu:[0,-46*S], farm:[-26*S,9*S]};
  const SPOT={};   // 이름표·문 자리
  let myHouse=null;
  function mySlot(){ let id=""; try{ const k=kidInfo(); id=(k && (k.id||k.n))||""; }catch(e){} if(!id){ try{ id=localStorage.getItem("hyeng_nick")||""; }catch(e){} }
    let h=0; for(const ch of String(id)) h=(h*31+ch.charCodeAt(0))>>>0; const L=slots.filter(s=>!s.empty); return L[h%L.length]; }
  function build(){
    if(G.userData.built) return; G.userData.built=1;
    const sea=new THREE.Mesh(new THREE.CircleGeometry(400,48), new THREE.MeshStandardMaterial({color:0x5cc4e8, roughness:.35})); sea.rotation.x=-Math.PI/2; sea.position.set(OX,-0.72*S,OZ); sea.receiveShadow=true; G.add(sea); G.userData.sea=sea;
    // 가운데 섬
    const C=island(0,0,8,c=>{ const x=c.lx, z=c.lz; if(((x-9.5)**2)/(5.4**2)+((z+0.8)**2)/(4.4**2)<=1) c.t="water"; else if(Math.hypot(x,z)<2.6) c.t="plaza"; else if((Math.abs(x)<1.1&&Math.abs(z)<13.5)||(Math.abs(z)<0.9&&Math.abs(x)<14)) c.t="path"; else if(Math.abs(z-5.2)<0.9&&Math.abs(x)<8) c.t="path"; else if(Math.abs(x+1.0)<1.1&&z>5&&z<12) c.t="path"; },"m");
    C.forEach(c=>{ if(c.t==="plaza") cap(c.x,c.z,0x9c8f78); if(c.t==="path") cap(c.x,c.z,0xa8834a); });
    // 분수
    { const st=0xcfc8b8; mesh(new THREE.CylinderGeometry(1.45,1.55,.45,14), st, 0,.22,0); mesh(new THREE.CylinderGeometry(1.3,1.3,.1,24), 0x5cc4e8, 0,.43,0,{nocast:1}); mesh(new THREE.CylinderGeometry(.2,.27,1.1,10), st, 0,.85,0);
      mesh(new THREE.CylinderGeometry(.55,.4,.18,12), st, 0,1.4,0); mesh(new THREE.CylinderGeometry(.48,.48,.06,16), 0x7fd3ea, 0,1.5,0,{nocast:1}); mesh(new THREE.SphereGeometry(.2,10,8), 0xbfeaff, 0,1.7,0,{nocast:1}); cols.push([OX,OZ,1.75]); SPOT.fountain=[OX,1.2,OZ]; }
    [[2.2,2.2],[-2.2,2.2],[2.2,-2.2],[-2.2,-2.2]].forEach(([x,z])=>kk("city","streetlight",x*S,z*S,{s:1,chunk:"m",col:.2}));
    [[3.1,0,Math.PI/2],[-3.1,0,-Math.PI/2],[0,3.1,0]].forEach(([x,z,r])=>kk("city","bench",x*S,z*S,{s:.9,ry:r,chunk:"m",col:.45}));
    kk("isle","tent",-2.7*S,-2.3*S,{s:1.5,ry:.9,chunk:"m",col:1.0}); kk("isle","crate_A_big",-3.5*S,-1.4*S,{s:.5,chunk:"m",col:.3}); kk("isle","barrel",-1.9*S,-3.2*S,{s:.5,chunk:"m",col:.3}); SPOT.market=[-2.7*S+OX,1.6,-2.3*S+OZ];
    // 가게 거리
    const MK=["building_market_blue","building_market_red","building_market_green","building_market_yellow"]; let mi=0;
    C.filter(c=>c.t==="grass"&&Math.abs(c.lz-6.9)<0.9&&Math.abs(c.lx)<8&&Math.abs(c.lx)>1.2).forEach(c=>{ kk("isle",MK[mi++%4],c.x,c.z,{s:1.9,ry:Math.PI,chunk:"m",col:1.1*S}); c.t="shop"; });
    kk("isle","building_church_blue",-4.8*S,10.2*S,{s:2.3,ry:Math.PI*0.9,chunk:"m",col:1.3*S}); SPOT.school=[-4.8*S+OX,2.6,10.2*S+OZ];
    kk("isle","building_stage_A",4.4*S,9.2*S,{s:2.4,ry:-2,chunk:"m",col:1.2});
    { // 모닥불
      const fx=2.4*S, fz=9.8*S; for(let i=0;i<4;i++){ const a=i/4*6.283+.4; const lg=mesh(new THREE.CylinderGeometry(.16,.16,.85,8), 0xa06a3c, fx+Math.cos(a)*1.1,.16,fz+Math.sin(a)*1.1); lg.rotation.z=Math.PI/2; lg.rotation.y=-a; }
      const f1=mesh(new THREE.ConeGeometry(.24,.6,8), 0xffa53a, fx,.32,fz,{basic:1,nocast:1}), f2=mesh(new THREE.ConeGeometry(.13,.42,8), 0xffe27a, fx,.3,fz,{basic:1,nocast:1}); G.userData.fire=[f1,f2]; cols.push([fx+OX,fz+OZ,.45]); SPOT.camp=[fx+OX,.9,fz+OZ]; }
    // 같이 낚시터 — 나무 부두
    { const B=new THREE.Group(); B.position.set(5.2*S+OX,0,-0.6*S+OZ); B.rotation.y=.15; for(let i=0;i<9;i++){ const pl=new THREE.Mesh(new THREE.BoxGeometry(.45,.11,1.55), MC(i%2?0xb07a4a:0x9a6a40)); pl.position.set(i*.47,-.02,0); pl.receiveShadow=true; B.add(pl); } G.add(B); G.userData.dock=B;
      const a=B.position, e=new THREE.Vector3(4.2,0,0).applyAxisAngle(new THREE.Vector3(0,1,0),.15); bridges.push([a.x-.2,a.z,a.x+e.x,a.z+e.z,.7]); SPOT.lake=[a.x+e.x*.6,.6,a.z+e.z*.6]; }
    C.filter(c=>c.t==="water").forEach(c=>{ if(rnd()<.35) kk("isle",rnd()<.5?"waterlily_A":"waterlily_B",c.x+(rnd()-.5)*S,c.z+(rnd()-.5)*S,{s:.8,y:-.2*S,chunk:"m",cast:false}); });
    kk("isle","building_tower_B_blue",-9*S,-9*S,{s:3.2,chunk:"m",col:1.5*S}); kk("isle","flag_blue",-7.8*S,-8.2*S,{s:1.6,chunk:"m"}); SPOT.tower=[-9*S+OX,3.4,-9*S+OZ];
    kk("isle","building_mine_blue",9*S,-11*S,{s:2.2,ry:Math.PI*0.8,chunk:"m",col:1.3*S}); kk("isle","mountain_B_grass_trees",11*S,-13*S,{s:1.4,chunk:"m",col:2.4*S}); SPOT.mine=[9*S+OX,2,-11*S+OZ];
    trees(C,[0.55,0.2,0.04],"m");
    // 동네 섬 · 새 동네 · 밭 섬
    hood(D.d1[0],D.d1[1],"1동","d1"); hood(D.d2[0],D.d2[1],"2동","d2"); hood(D.d3[0],D.d3[1],"3동","d3");
    link(D.plaza,13.6*S,D.d1,7.2*S); link(D.plaza,14.5*S,D.d2,7.2*S); link(D.plaza,14.5*S,D.d3,7.2*S);
    { const cells=island(D.nu[0],D.nu[1],3,null,"nu"); cells.forEach(c=>{ if(rnd()<.3) cap(c.x,c.z,0xc9a46a,.05); }); kk("isle","resource_lumber",D.nu[0],D.nu[1],{s:1.6,chunk:"nu",col:.8}); kk("isle","flag_yellow",D.nu[0]+S*2,D.nu[1],{s:1.6,chunk:"nu"}); bridge(0,D.d1[1]-7.2*S,0,D.nu[1]+5.4*S); SPOT.nu=[D.nu[0]+OX,1.4,D.nu[1]+OZ]; }
    { const FC=island(D.farm[0],D.farm[1],4,c=>{ if(c.d<=3 && c.d>=1) c.t="farm"; },"f");
      FC.filter(c=>c.t==="farm").forEach((c,i)=>{ cap(c.x,c.z,0x8a5a34,.08); const col=[0xffd23f,0xff9a3d,0x7fd36a,0xff6b6b][i%4]; for(let a=-1;a<=1;a++) for(let b=-1;b<=1;b++){ const x=c.x+a*S*.42, z=c.z+b*S*.5; const s=mesh(new THREE.ConeGeometry(.08,.28,5), 0x5db95a, x,.22,z,{nocast:1}); const f=mesh(new THREE.SphereGeometry(.12,8,6), col, x,.4,z,{nocast:1}); } });
      kk("isle","building_windmill_yellow",D.farm[0],D.farm[1],{s:2.2,chunk:"f",col:1.0}); trees(FC,[0.6,0.1,0],"f"); link(D.plaza,15*S,D.farm,7.2*S); SPOT.farm=[D.farm[0]+OX,1.6,D.farm[1]+OZ]; }
    // 동네 집 (내 집은 ⭐)
    myHouse=mySlot();
    slots.forEach(sl=>{ const ch=sl.hood==="1동"?"d1":sl.hood==="2동"?"d2":"d3";
      if(sl.empty){ cap(sl.x,sl.z,0xc9a46a,.05); kk("city","box_A",sl.x,sl.z,{s:.8,chunk:ch,col:.4}); return; }
      kk("isle",HC[(sl.i*3+ch.charCodeAt(1))%HC.length],sl.x,sl.z,{s:2.2,ry:sl.face,chunk:ch,col:.95});
      if(sl===myHouse){ const st=mesh(new THREE.OctahedronGeometry(.32), 0xffd23f, sl.x,3.1,sl.z,{basic:1,nocast:1}); G.userData.star=st; } });
    if(myHouse){ const dx=Math.sin(myHouse.face), dz=Math.cos(myHouse.face); SPOT.home=[myHouse.x+OX+dx*1.25,1.3,myHouse.z+OZ+dz*1.25]; SPOT.homeIn=[myHouse.x+OX+dx*.55,myHouse.z+OZ+dz*.55]; }
    // 풀포기 · 들꽃
    { const gs=[]; islands.forEach(I=>I.cells.forEach(c=>{ if(c.t!=="grass") return; for(let i=0;i<2;i++) gs.push([c.x+OX+(rnd()-.5)*S*1.6, c.z+OZ+(rnd()-.5)*S*1.6, rnd()]); }));
      const geo=new THREE.ConeGeometry(.05,.24,3); geo.translate(0,.11,0); const im=new THREE.InstancedMesh(geo, MC(0x4e9e3a), gs.length*3), d=new THREE.Object3D(); let k=0;
      gs.forEach(([x,z,r])=>{ for(let j=0;j<3;j++){ d.position.set(x+(j-1)*.06,0,z+(j%2)*.04); d.rotation.set((j-1)*.35,r*6,0); d.scale.setScalar(.8+r*.6); d.updateMatrix(); im.setMatrixAt(k++, d.matrix); } }); G.add(im);
      const fl=gs.filter(g=>g[2]<.5), fm=new THREE.InstancedMesh(new THREE.IcosahedronGeometry(.075,0), MC(0xffffff), fl.length), col=new THREE.Color(); fl.forEach(([x,z,r],i)=>{ d.position.set(x+.15,.08,z-.1); d.rotation.set(0,r*6,0); d.scale.setScalar(1); d.updateMatrix(); fm.setMatrixAt(i,d.matrix); fm.setColorAt(i,col.set([0xff7aa8,0xffd23f,0xffffff,0xb28dff][Math.floor(r*97)%4])); }); G.add(fm); }
    // 먼 섬 · 구름 (테두리 계산에서 멀리 빼려고 그림자 없음)
    for(let i=0;i<10;i++){ const a=i/10*6.283+0.3, d=75+rnd()*30; kk("nature",["mountain_A_grass_trees","mountain_B_grass_trees","hills_A_trees","hills_C_trees"][i%4],Math.cos(a)*d,Math.sin(a)*d-20,{s:1.4+rnd(),y:-0.72*S,chunk:"far",cast:false}); }
    merge(); drawCaps(); walkmap();
    G.children.forEach(o=>{ o.userData.noFade=1; });   /* 합친 섬은 통째로 흐려지지 않게 (가림 흐리기 제외) */
    try{ TOON.scan(G); }catch(e){} dirty=true; }
  /* ── 걸을 수 있는 칸 ── */
  function hexOf(x,z){ for(const I of islands){ const lx=x-(I.cx+OX), lz=z-(I.cz+OZ); const fq=(Math.sqrt(3)/3*lx-1/3*lz)/HR, fr=(2/3*lz)/HR; let rq=Math.round(fq), rr=Math.round(fr), rs=Math.round(-fq-fr); const dq=Math.abs(rq-fq), dr=Math.abs(rr-fr), ds=Math.abs(rs+fq+fr);
      if(dq>dr && dq>ds) rq=-rr-rs; else if(dr>ds) rr=-rq-rs; if(dist(rq,rr)>I.R) continue; return I.cells.find(c=>c.q===rq&&c.r===rr)||null; } return null; }
  function onBridge(x,z){ return bridges.some(([ax,az,bx,bz,w])=>{ const dx=bx-ax, dz=bz-az, L2=dx*dx+dz*dz, t=Math.max(0,Math.min(1,((x-ax)*dx+(z-az)*dz)/L2)), px=ax+dx*t, pz=az+dz*t; return Math.hypot(x-px,z-pz)<=w; }); }
  function walkmap(){ W.fill(0); for(let gx=0;gx<N;gx++) for(let gz=0;gz<N;gz++){ const x=gx+.5, z=gz+.5; let ok=false; const c=hexOf(x,z);
      if(c && c.t!=="water" && c.t!=="house" && c.t!=="shop") ok=true; if(onBridge(x,z)) ok=true;
      if(ok && c && c.d>=c.R && !onBridge(x,z)){ const I=islands.find(I=>I.cells.indexOf(c)>=0); const lx=x-(I.cx+OX), lz=z-(I.cz+OZ); if(Math.hypot(lx,lz)>I.R*2*S-.35) ok=false; }   // 섬 가장자리 반 칸 여유
      if(ok && cols.some(([cx,cz,r])=>Math.hypot(x-cx,z-cz)<r)) ok=false;
      W[gx*N+gz]=ok?1:0; }
    if(SPOT.homeIn){ const a=[Math.floor(SPOT.homeIn[0]),Math.floor(SPOT.homeIn[1])]; W[a[0]*N+a[1]]=1; SPOT.door=a; } }
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
    const run=()=>{ build(); const d=doorCell(); go("isle", d, null, Object.assign({from:SPOT.homeIn||null}, o||{})); };
    if(KK.R.isle && KK.R.city && KK.R.nature){ run(); return true; }
    toast("🏝 우리 마을로 가는 중…", 1500); ready().then(run); return true; }
  /* 마당·시장·광산·타워에서 돌아오기 — 그곳으로 가는 다리·건물 앞에 */
  function back(from){ if(!nameOk()){ gate(); return; } const near={farm:"farm", market:"market", mine:"mine", tower:"tower"}[from]||"market";
    const run=()=>{ build(); const s=SPOT[near]; let at=s ? [Math.floor(s[0]), Math.floor(s[2])] : [OX,OZ+3]; if(blocked(at[0],at[1])){ const L=[]; for(let r=1;r<8 && !L.length;r++) for(let dx=-r;dx<=r;dx++) for(let dz=-r;dz<=r;dz++) if(!blocked(at[0]+dx,at[1]+dz)) L.push([at[0]+dx,at[1]+dz]); L.sort((a,b)=>Math.hypot(a[0]-OX,a[1]-OZ)-Math.hypot(b[0]-OX,b[1]-OZ)); if(L.length) at=L[0]; }
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
    const busy=F.st!=="idle" || trip.busy || sheetOpen() || !!dlg;
    const m=Math.hypot(jx,jy);
    if(m>.12 && !busy){ hero.path=[]; hero.then=null; if(hero.slide && !hero.slide.then) hero.slide=null; const fx=-Math.sin(yaw), fz=-Math.cos(yaw), rx=Math.cos(yaw), rz=-Math.sin(yaw), mx=rx*jx+fx*(-jy), mz=rz*jx+fz*(-jy), L=Math.hypot(mx,mz)||1, sp=SPD*Math.min(1,m)*dt;
      const nx=p.x+mx/L*sp, nz=p.z+mz/L*sp, okc=(x,z)=>!blocked(Math.floor(x),Math.floor(z));
      if(okc(nx,nz)){ p.x=nx; p.z=nz; } else if(okc(nx,p.z)){ p.x=nx; } else if(okc(p.x,nz)){ p.z=nz; }
      hero.face=Math.atan2(mx,mz); hero.cx=Math.floor(p.x); hero.cz=Math.floor(p.z); hero.moving=true; hero.joy=true; anim=true; }
    else if(hero.joy){ hero.joy=false; if(!hero.path.length) hero.moving=false; anim=true; }
    if(J.air){ J.vy-=16*dt; p.y=Math.max(0, p.y+J.vy*dt); if(p.y<=0 && J.vy<0){ p.y=0; J.air=false; } hero.act=J.air?"air":(hero.act==="air"?"idle":hero.act); anim=true; }
    // 그림자 상자는 나를 따라감
    const s=sun.shadow.camera; sun.position.set(p.x-14, 26, p.z-7); sun.target.position.set(p.x,0,p.z); if(s.right!==16){ s.left=-16; s.right=16; s.top=16; s.bottom=-16; s.near=1; s.far=80; s.updateProjectionMatrix(); }
    const st=G.userData.star; if(st){ st.rotation.y+=dt*1.5; st.position.y=3.1+Math.sin(performance.now()*.003)*.12; anim=true; }
    const fi=G.userData.fire; if(fi){ const t=performance.now()*.012; fi[0].scale.set(1,1+Math.sin(t)*.12,1); fi[1].scale.set(1,1+Math.cos(t*1.3)*.15,1); }
    return anim; }
  function show(on){ ui(); document.body.classList.toggle("isleOn", !!on); }
  /* ── 이름표 (가까이 가면) ── */
  function labels(){ const L=[];
    if(SPOT.home) L.push({k:"home", ic:"⭐", t:"내 집", p:SPOT.home, r:3, act:()=>walkTo(SPOT.door[0],SPOT.door[1],()=>enterHome())});
    if(SPOT.market) L.push({k:"mk", ic:"🏘", t:"시장 · 마을 사람", p:SPOT.market, r:3.2, act:()=>tripTo("village")});
    if(SPOT.lake) L.push({k:"lake", ic:"🎣", t:"낚시터", p:SPOT.lake, r:3.2, act:()=>toast("🎣 <b>같이 낚시</b>는 곧 열려요!<br><small>지금은 「🌱 밭 섬」 다리 건너 내 마당 연못에서 낚시해요</small>", 3000)});
    if(SPOT.farm) L.push({k:"farm", ic:"🌱", t:"밭 섬 · 내 마당", p:SPOT.farm, r:4.5, act:()=>tripTo("yard")});
    if(SPOT.school) L.push({k:"school", ic:"🏫", t:"학교 · 공부하기", p:SPOT.school, r:3.4, act:()=>ask("🏫 공부하러 갈까요?<br><small>Daily 30 을 하면 🪱 미끼를 받아요</small>", ()=>{ location.href="../index.html"; })});
    if(SPOT.tower) L.push({k:"tower", ic:"🗼", t:"하늘 타워", p:SPOT.tower, r:3.6, act:()=>towerAsk()});
    if(SPOT.mine) L.push({k:"mine", ic:"⛏", t:"광산", p:SPOT.mine, r:3.4, act:()=>tripTo("mine")});
    if(SPOT.nu) L.push({k:"nu", ic:"🚧", t:"새 동네 (친구가 오면)", p:SPOT.nu, r:4, act:()=>toast("🚧 학원 친구가 늘면 <b>새 동네</b>가 여기에 생겨요!", 2600)});
    if(SPOT.camp) L.push({k:"camp", ic:"🔥", t:"모닥불", p:SPOT.camp, r:2.6, act:()=>{ hero.act="sit"; hero.actT=0; toast("🔥 따뜻해요 — 친구들이 모이는 곳이에요", 2200); }});
    return L; }
  function tripTo(key){ const at=key==="yard" ? [DOOR[0],DOOR[1]] : key==="village" ? [V_GATE[0]+1,V_GATE[1]] : key==="mine" ? [M_GATE[0]-1,M_GATE[1]] : null; go(key, at); }
  function enterHome(){ const a=!roomBlocked(1,RN-1)?[1,RN-1]:[0,RN-1]; go("room", a, null, {from:()=>[0.05,RN-0.5], door:roomDoor}); }
  function tap(e){ const c=cellAt(e); if(!c) return; walkTo(c[0], c[1]); }
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
  return {ON, back, ready, G, PLC, N, OX, OZ, S, build, enter, tick, show, labels, tap, blocked, nameOk, gate, SPOT, slots, myHouse:()=>myHouse, W, J, doorCell, enterHome};
})();
window.ISLE=ISLE; PL.isle=ISLE.PLC; LBL_DEF.isle=ISLE.labels; LBL_NEAR.isle=1;
