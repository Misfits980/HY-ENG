/* ═════════ (v590) 💦 물총 아레나 — 1인칭 · 아스날(Arsenal) 규칙 · 아레나 무브
   사용자: 「아레나 무브도 만들 수 있어? 1인칭이라 잘 만들어야 할 텐데」 · 참고 = Arsenal (로블록스) → 물총 버전 (아이들 게임이라 「흠뻑」 젖으면 다시 나옴)
   규칙: 한 명을 흠뻑 적실 때마다 다음 무기 (8단계) → 마지막 🔨 뿅망치로 맞히면 우승 · 5분 끝나면 가장 멀리 간 사람 · 도움 2번 = 한 단계
   아레나 무브: 빠른 달리기 · 🛝 슬라이드(속도 붙음) · 슬라이드 점프(속도 그대로) · 착지 순간 점프 = 속도 유지(버니합) · 공중에서 방향 틀기 · 💧 분수 발판(높이 튀어 오름)
   조작: 왼손 = 아무 데나 끌어 움직이기 · 오른손 = 화면 끌어 둘러보기 · 💦 버튼 = 쏘기(누른 채 끌면 조준도) · 점프 · 슬라이드 / 키보드 WASD · 마우스(클릭하면 잠금) · 스페이스 · Shift
   손 도움(터치): 적 위에서 조준이 살짝 느려짐 · 거의 맞을 때 살짝 끌어당김 · (고르면) 자동 쏘기 */
(()=>{ if(typeof MG==="undefined" || typeof THREE==="undefined") return;
const V3=THREE.Vector3, D2R=Math.PI/180;
const WP=[
  {k:"pistol",  ic:"🔫", nm:"물권총",    t:"hs",    dmg:34, rate:.30, spr:.7,  rng:60, col:0xff9a3d, tk:0x46b3ff, pref:10},
  {k:"duo",     ic:"✌️", nm:"쌍권총",    t:"hs",    dmg:20, rate:.12, spr:1.5, rng:50, col:0xff6b9a, tk:0x7fe0ff, pref:9},
  {k:"shot",    ic:"🌊", nm:"물대포",    t:"hs",    dmg:15, rate:.78, spr:5.5, rng:24, col:0x3ccf6a, tk:0x46b3ff, pref:5, n:7},
  {k:"smg",     ic:"💦", nm:"연발 물총", t:"hs",    dmg:11, rate:.075,spr:2.3, rng:45, col:0xffc93d, tk:0xb28dff, pref:9},
  {k:"snipe",   ic:"🎯", nm:"저격 물총", t:"snipe", dmg:100,rate:.95, spr:0,   rng:90, col:0x4f7fff, tk:0xffffff, pref:18},
  {k:"balloon", ic:"🎈", nm:"물풍선",    t:"proj",  dmg:90, rate:.85, spr:0,   rng:40, col:0xff7aa8, tk:0xffd23f, pref:11},
  {k:"wave",    ic:"🌀", nm:"파도 대포", t:"beam",  dmg:8,  rate:.09, spr:1.2, rng:16, col:0x2ec4c4, tk:0x7fe0ff, pref:7},
  {k:"hammer",  ic:"🔨", nm:"뿅망치",    t:"melee", dmg:100,rate:.5,  spr:0,   rng:2.8, col:0xff4d6d, tk:0xffd23f, pref:0}];
const LAST=WP.length-1;
const BOTS=[
  {nm:"Tom",  av:{skin:1, hair:"short", hc:1, style:"overalls", top:3, pc:2, hat:"straw", acc:"none"}},
  {nm:"Lily", av:{skin:0, hair:"bun", hc:6, style:"dress", top:6, pc:5, hat:"none", acc:"ribbon"}},
  {nm:"Sam",  av:{skin:2, hair:"short", hc:0, style:"hoodie", top:1, pc:1, hat:"beanie", acc:"none"}},
  {nm:"Joe",  av:{skin:1, hair:"spiky", hc:4, style:"tee", top:7, pc:2, hat:"cap", acc:"glasses"}},
  {nm:"Zoe",  av:{skin:3, hair:"pigtails", hc:3, style:"tee", top:4, pc:4, hat:"none", acc:"flower"}}];
/* bvb = 봇끼리 맞힐 때 물 양 (봇끼리 너무 빨리 끝나지 않게 — 아이가 따라잡을 시간) */
const DIFF={easy:{err:6.5, react:.9, turn:4, fire:1.7, spd:.78, gang:1, bvb:.35, dm:.6}, normal:{err:3.8, react:.55, turn:6.5, fire:1.3, spd:.88, gang:2, bvb:.38, dm:.85}, hard:{err:2.1, react:.32, turn:10, fire:1.05, spd:.96, gang:3, bvb:.5, dm:1}};
/* 움직임 (m · 초) */
const GRAV=22, JV=8.1, MAXS=7.6, ACC=11, FRIC=6.2, STOP=2.6, AIRACC=14, AIRCAP=1.05, SLFRIC=0.5, SLBOOST=4.4, SLMAX=15.5, SLCD=0.85, HCAP=17, STEP=0.55, HW=0.34, HH=1.75, HS=1.05, EYE=1.48, EYES=0.92, PADV=13.2;
const MATCH=300, RESP=2.6, PROT=1.6;

function start(api){
  const D=DIFF[api.opt.diff]||DIFF.normal, AUTO=!!api.opt.auto;
  const scene=new THREE.Scene(); scene.background=new THREE.Color(0x9fdcff); scene.fog=new THREE.Fog(0x9fdcff, 45, 95);
  const cam=new THREE.PerspectiveCamera(76, 1, 0.05, 160); cam.rotation.order="YXZ";
  const hemi=new THREE.HemisphereLight(0xfff4e0, 0x5a7ab0, 0.5); scene.add(hemi); scene.add(new THREE.AmbientLight(0xffffff, .08));
  const sunL=new THREE.DirectionalLight(0xfff0d8, .95); sunL.position.set(18,34,12); scene.add(sunL); scene.add(sunL.target);
  if(!api.low){ sunL.castShadow=true; sunL.shadow.mapSize.set(1024,1024); const sc=sunL.shadow.camera; sc.left=sc.bottom=-32; sc.right=sc.top=32; sc.near=1; sc.far=90; sunL.shadow.bias=-0.0012; }
  const toon=m=>{ try{ TOON.mat(m); }catch(e){} return m; };
  const VCM=toon(new THREE.MeshStandardMaterial({vertexColors:true, roughness:.85}));
  const disp=[];   /* 나갈 때 지울 것 */

  /* ════ 경기장 (50×50 · 180° 돌려도 같은 모양 = 공평) ════ */
  const BOX=[], DECO=[], GLOW=[];
  const bx=(x0,z0,x1,z1,y1,col,y0)=>{ const b={x0:Math.min(x0,x1), z0:Math.min(z0,z1), x1:Math.max(x0,x1), z1:Math.max(z0,z1), y0:y0||0, y1, col}; BOX.push(b); return b; };
  const sym=(x0,z0,x1,z1,y1,col,y0)=>{ bx(x0,z0,x1,z1,y1,col,y0); bx(-x0,-z0,-x1,-z1,y1,col,y0); };
  const R=25;
  bx(-R-1,-R-1,R+1,-R,4.6,0x4f9be8); bx(-R-1,R,R+1,R+1,4.6,0x4f9be8); bx(-R-1,-R,-R,R,4.6,0x5aa7ff); bx(R,-R,R+1,R,4.6,0x5aa7ff);
  /* 가운데 노란 단(1.6) · 계단 남북 · 양옆 낮은 벽 · 가운데 물탑 기둥 */
  bx(-4,-4,4,4,1.6,0xffc23d);
  for(let k=1;k<=3;k++) sym(-1.7,-4-.7*k,1.7,-4-.7*(k-1),1.6-.4*k,0xffd76a);
  sym(-4,-1.6,-3.55,1.6,2.75,0xd7e3ff,1.6);
  bx(-.55,-.55,.55,.55,5.4,0xffffff,1.6);
  /* 양옆 높은 길(2.4) · 끝마다 계단 · 안쪽 난간 */
  const wk=(x0,x1,sg)=>{ bx(x0,-9,x1,9,2.4,0x4f9be8); for(let k=1;k<=5;k++){ bx(x0,-9-.7*k,x1,-9-.7*(k-1),2.4-.4*k,0x7ab8f5); bx(x0,9+.7*(k-1),x1,9+.7*k,2.4-.4*k,0x7ab8f5); } bx(sg>0?x0:x1-.35, -5, sg>0?x0+.35:x1, 5, 3.35, 0xd7e3ff, 2.4); };
  wk(-21,-17,-1); wk(17,21,1);
  /* 모서리 ㄱ자 벽 (분홍) */
  sym(-17,-17,-11,-16.4,2.7,0xff6f91); sym(-17,-16.4,-16.4,-11,2.7,0xff6f91); sym(11,-17,17,-16.4,2.7,0xff6f91); sym(16.4,-16.4,17,-11,2.7,0xff6f91);
  /* 상자 (튜브 장난감 색) · 쌓은 상자 · 낮은 벽 */
  const cr=(x,z,h,c)=>sym(x-.6,z-.6,x+.6,z+.6,h||1.15,{0xff9a3d:0xff8a3d,0x5ee36b:0x45c46a,0xb28dff:0x9b7be8,0xff7aa8:0xff6f91}[c||0xff9a3d]||c);
  cr(-8.5,-11); cr(-7.3,-11,1.15,0x5ee36b); cr(-8.5,-11,2.3,0xff9a3d); cr(-11.5,-4.5,1.15,0xb28dff); cr(-11.5,-3.3,2.3,0xb28dff); cr(-7,7.5,1.15,0x5ee36b); cr(-13,9.5,1.15,0xff9a3d);
  cr(8.5,-11.5,1.15,0x5ee36b); cr(12,-6,2.3,0xff9a3d); cr(12,-4.8,1.15,0xff9a3d); cr(7,12.5,1.15,0xb28dff); cr(-3.5,-20,1.15,0xff9a3d); cr(-2.3,-20,2.3,0xff7aa8); cr(-21.5,-21,1.15,0x5ee36b); cr(-20.3,-21.6,1.15,0xb28dff);
  sym(-2.2,-15.6,2.2,-15,1.0,0xd7e3ff); sym(-14.2,-1,-13.6,3,1.0,0xd7e3ff); sym(5.6,-8,6.2,-5,1.0,0xd7e3ff); sym(-24.9,-17,-23.6,-15.8,1.15,0xff9a3d);
  /* 💧 분수 발판 (밟으면 높이 튀어 오름) */
  const PADS=[[-13.8,-9.2],[13.8,9.2],[-8.2,15.8],[8.2,-15.8]];
  /* 나오는 자리 */
  const SPAWN=[[-23,0],[23,0],[0,-23],[0,23],[-22.5,-22.5],[22.5,22.5],[-22.5,22.5],[22.5,-22.5],[-9.5,-8],[9.5,8],[-9,9],[9,-9],[-19,-4],[19,4]];

  /* 땅 — 수영장 데크 바둑판 · 꾸밈(작은 풀장 · 파라솔 · 오리 튜브 · 물탑) */
  const VL=[];   /* 합칠 것 {g, col, m} */
  const mtx=(x,y,z,rx,ry,rz,sx,sy,sz)=>new THREE.Matrix4().compose(new V3(x,y,z), new THREE.Quaternion().setFromEuler(new THREE.Euler(rx||0,ry||0,rz||0)), new V3(sx||1,sy||1,sz||1));
  BOX.forEach(b=>{ const w=b.x1-b.x0, h=b.y1-b.y0, d=b.z1-b.z0; VL.push({g:new THREE.BoxGeometry(w,h,d), col:b.col, m:mtx((b.x0+b.x1)/2,(b.y0+b.y1)/2,(b.z0+b.z1)/2)});
    if(h>2 && w>.5 && d>.5 && b.y0===0 && b.col!==0x4f9be8 && b.col!==0x7fd3ff) VL.push({g:new THREE.BoxGeometry(w+.04,.14,d+.04), col:0xffffff, m:mtx((b.x0+b.x1)/2,b.y1-.3,(b.z0+b.z1)/2)}); });
  for(let i=0;i<4;i++){ const a=i*Math.PI/2; VL.push({g:new THREE.BoxGeometry(52,.35,.2), col:0xffffff, m:mtx(Math.sin(a)*(R-.08),3.9,Math.cos(a)*(R-.08),0,a,0)}); VL.push({g:new THREE.BoxGeometry(52,.25,.2), col:0xffd23f, m:mtx(Math.sin(a)*(R-.08),2.2,Math.cos(a)*(R-.08),0,a,0)}); }
  { const N=20, s=50/N; for(let i=0;i<N;i++) for(let j=0;j<N;j++) VL.push({g:new THREE.PlaneGeometry(s,s), col:(i+j)%2?0x8fd0dc:0x7cc3d1, m:mtx(-R+s*(i+.5),0,-R+s*(j+.5),-Math.PI/2)}); }
  [[-9,-17.5],[9,17.5]].forEach(([x,z])=>{ VL.push({g:new THREE.CylinderGeometry(2.3,2.3,.2,26), col:0xffffff, m:mtx(x,.1,z)}); VL.push({g:new THREE.CylinderGeometry(2.05,2.05,.06,26), col:0x46b3ff, m:mtx(x,.2,z)});
    VL.push({g:new THREE.TorusGeometry(.55,.22,10,18), col:0xffd23f, m:mtx(x+.6,.3,z-.4,Math.PI/2)}); VL.push({g:new THREE.SphereGeometry(.3,10,8), col:0xffd23f, m:mtx(x+.6,.62,z-.95)}); VL.push({g:new THREE.ConeGeometry(.1,.2,8), col:0xff9a3d, m:mtx(x+.6,.62,z-1.27,Math.PI/2)}); });
  [[-23,-12],[23,12],[-12,23],[12,-23]].forEach(([x,z],i)=>{ VL.push({g:new THREE.CylinderGeometry(.06,.06,2.8,8), col:0xffffff, m:mtx(x,1.4,z)}); VL.push({g:new THREE.ConeGeometry(1.7,.7,10), col:[0xff7aa8,0xffd23f,0x5ee36b,0xb28dff][i], m:mtx(x,2.9,z)}); });
  VL.push({g:new THREE.SphereGeometry(1.5,20,14), col:0x7fd3ff, m:mtx(0,6.6,0)}); VL.push({g:new THREE.CylinderGeometry(1.52,1.52,.25,20), col:0xffffff, m:mtx(0,6.6,0)}); VL.push({g:new THREE.ConeGeometry(.5,.8,14), col:0x46b3ff, m:mtx(0,8.3,0)});
  PADS.forEach(([x,z])=>{ VL.push({g:new THREE.CylinderGeometry(1.0,1.1,.12,22), col:0xffffff, m:mtx(x,.06,z)}); GLOW.push({g:new THREE.CylinderGeometry(.82,.82,.04,22), col:0x7fe0ff, m:mtx(x,.13,z)}); GLOW.push({g:new THREE.TorusGeometry(.95,.05,6,24), col:0x46b3ff, m:mtx(x,.14,z,Math.PI/2)}); });
  function merge(L, mat){ const parts=L.map(e=>{ let g=e.g.index?e.g.toNonIndexed():e.g; if(e.m) g.applyMatrix4(e.m); if(!g.attributes.normal) g.computeVertexNormals(); return [g, new THREE.Color(e.col).convertSRGBToLinear()]; });
    let n=0; parts.forEach(([g])=>n+=g.attributes.position.count); const P=new Float32Array(n*3), N=new Float32Array(n*3), C=new Float32Array(n*3); let o=0;
    parts.forEach(([g,c])=>{ const k=g.attributes.position.count; P.set(g.attributes.position.array.subarray(0,k*3),o*3); N.set(g.attributes.normal.array.subarray(0,k*3),o*3); for(let i=0;i<k;i++){ C[(o+i)*3]=c.r; C[(o+i)*3+1]=c.g; C[(o+i)*3+2]=c.b; } o+=k; g.dispose(); });
    const G=new THREE.BufferGeometry(); G.setAttribute("position",new THREE.BufferAttribute(P,3)); G.setAttribute("normal",new THREE.BufferAttribute(N,3)); G.setAttribute("color",new THREE.BufferAttribute(C,3)); G.computeBoundingSphere();
    const m=new THREE.Mesh(G, mat||VCM); m.castShadow=true; m.receiveShadow=true; disp.push(G); return m; }
  scene.add(merge(VL)); { const gm=merge(GLOW, new THREE.MeshBasicMaterial({vertexColors:true})); gm.castShadow=false; scene.add(gm); }
  /* 멀리 보이는 바다 · 하늘 둘레 */
  { const sea=new THREE.Mesh(new THREE.PlaneGeometry(400,400), new THREE.MeshBasicMaterial({color:0x6fc9f0})); sea.rotation.x=-Math.PI/2; sea.position.y=-.6; scene.add(sea); disp.push(sea.geometry); }

  /* ════ 충돌 · 광선 ════ */
  const ov=(a,b)=>a.x0<b.x1 && a.x1>b.x0 && a.y0<b.y1 && a.y1>b.y0 && a.z0<b.z1 && a.z1>b.z0;
  const aabb=(p,h)=>({x0:p.x-HW, x1:p.x+HW, y0:p.y, y1:p.y+h, z0:p.z-HW, z1:p.z+HW});
  function free(p,h){ const A=aabb(p,h); for(const b of BOX) if(ov(A,b)) return false; return true; }
  /* 광선 ↔ 상자 (가장 가까운 t · 면 방향) */
  function rayBox(o, d, maxT){ let best=maxT, nrm=null;
    for(const b of BOX){ let t0=0, t1=best, ax=-1, sgn=0; const lo=[b.x0,b.y0,b.z0], hi=[b.x1,b.y1,b.z1], oo=[o.x,o.y,o.z], dd=[d.x,d.y,d.z]; let ok=true;
      for(let i=0;i<3;i++){ if(Math.abs(dd[i])<1e-9){ if(oo[i]<lo[i]||oo[i]>hi[i]){ ok=false; break; } continue; } let ta=(lo[i]-oo[i])/dd[i], tb=(hi[i]-oo[i])/dd[i], s=-1; if(ta>tb){ const q=ta; ta=tb; tb=q; s=1; } if(ta>t0){ t0=ta; ax=i; sgn=s; } if(tb<t1) t1=tb; if(t0>t1){ ok=false; break; } }
      if(ok && t0<best && t0>0){ best=t0; nrm=[0,0,0]; if(ax>=0) nrm[ax]=sgn; } }
    if(d.y<-1e-6){ const tg=-o.y/d.y; if(tg>0 && tg<best){ best=tg; nrm=[0,1,0]; } }
    return {t:best, n:nrm}; }
  function sees(a, b){ const o=new V3(a.x, a.y, a.z), d=new V3(b.x-a.x, b.y-a.y, b.z-a.z), L=d.length(); if(L<1e-3) return true; d.divideScalar(L); return rayBox(o, d, L).t>=L-1e-3; }
  function raySph(o, d, c, r){ const ox=o.x-c.x, oy=o.y-c.y, oz=o.z-c.z, b=ox*d.x+oy*d.y+oz*d.z, cc=ox*ox+oy*oy+oz*oz-r*r, h=b*b-cc; if(h<0) return -1; const t=-b-Math.sqrt(h); return t>0?t:-1; }

  /* ════ 물총 모양 (손에 든 것 · 내 화면 것 같은 모양) ════ */
  const KIT={pistol:["blaster-k",.38,.034], duo:["blaster-a",.33,.03], shot:["blaster-b",.44,.04], smg:["blaster-d",.52,.034], snipe:["blaster-e",.72,.03], balloon:["blaster-h",.5,.04], wave:["blaster-l",.5,.048]};
  const TANK=new THREE.MeshStandardMaterial({color:0x6fd0ff, transparent:true, opacity:.72, roughness:.15, metalness:0}); disp.push(TANK);
  let KMAT=null; const kitMat=R=>{ if(!KMAT){ KMAT=R.mat; toon(KMAT); } return KMAT; };
  const GM={}; const gmat=c=>GM[c]||(GM[c]=toon(new THREE.MeshStandardMaterial({color:c, roughness:.55})));
  function gunModel(G, wi, small){ while(G.children.length) G.remove(G.children[0]); const W=WP[wi], add=(geo,c,x,y,z,rx,ry,rz)=>{ const m=new THREE.Mesh(geo, gmat(c)); m.position.set(x,y,z); m.rotation.set(rx||0,ry||0,rz||0); if(!small) m.castShadow=false; G.add(m); return m; };
    /* 앞 = -z (내 화면) — 봇 손에서는 팔 방향(-y)으로 돌림 */
    const H=new THREE.Group(); G.add(H); if(small) H.rotation.x=-Math.PI/2; const A=(geo,c,x,y,z,rx,ry,rz)=>{ const m=add(geo,c,x,y,z,rx,ry,rz); G.remove(m); H.add(m); return m; };
    const B=(w,h,d)=>new THREE.BoxGeometry(w,h,d), C=(r,h,n,r2)=>new THREE.CylinderGeometry(r,r2==null?r:r2,h,n||14), S=r=>new THREE.SphereGeometry(r,14,10), Z=Math.PI/2;
    const dk=c=>{ const k=new THREE.Color(c); k.multiplyScalar(.72); return k.getHex(); };
    if(W.k==="hammer"){ A(C(.032,.5,8),0xc98b5a,0,.02,-.08,Z*.78); A(C(.12,.32,18),W.col,0,.2,-.3,0,0,Z); [-.13,.13].forEach(x=>A(C(.125,.05,18),W.tk,x,.2,-.3,0,0,Z)); A(S(.05),0xffffff,0,.3,-.2); return; }
    /* (v591) 사용자: 「무기가 너무 아쉬워」 → Kenney Blaster Kit(CC0) 장난감 블래스터 + 위에 투명 물통 = 장난감 물총 (모델이 아직 안 왔으면 아래 상자 물총) */
    const KM=KIT[W.k], R=(typeof KK!=="undefined") && KK.R.blaster;
    if(KM && R && R.G[KM[0]]){ const g=R.G[KM[0]], bb=g.boundingBox, s=KM[1]/(bb.max.z-bb.min.z), m=new THREE.Mesh(g, kitMat(R)); m.scale.setScalar(s); m.castShadow=!!small;   /* 모델 앞 = -z 그대로 */
      m.position.set(-(bb.min.x+bb.max.x)/2*s, .07-bb.max.y*s, .1-bb.max.z*s); H.add(m); const L=KM[1], tr=KM[2]||.045;
      const tk=new THREE.Mesh(C(tr,L*.28,16), TANK); tk.rotation.x=Z; tk.position.set(0,.07+tr*.85,.1-L*.42); H.add(tk); [1,-1].forEach(e=>{ const c=new THREE.Mesh(S(tr), TANK); c.scale.z=.5; c.position.set(0,.07+tr*.85,.1-L*.42+e*L*.14); H.add(c); });
      const cp=new THREE.Mesh(C(tr*.45,.05,10), gmat(0xffffff)); cp.position.set(0,.07+tr*1.75,.1-L*.34); H.add(cp);
      if(W.k==="duo" && !small){ const G2=new THREE.Group(); G.add(G2); G2.position.set(-.42,0,0); H.children.forEach(q=>G2.add(q.clone())); G.userData.twin=G2; } else G.userData.twin=null;
      return; }
    if(W.k==="balloon"){ A(C(.085,.5,16),W.col,0,0,-.2,Z); A(C(.095,.06,16),0xffffff,0,0,-.45,Z); A(S(.12),0x46b3ff,0,.0,-.55); A(B(.08,.2,.1),dk(W.col),0,-.15,.0,.3); A(C(.05,.14,12),W.tk,0,.11,-.08,Z); return; }
    /* 물총 = 몸통 · 위 물통 · 앞 꼭지 · 아래 펌프 · 손잡이 */
    const P={pistol:[.08,.1,.34,.055,.16], duo:[.07,.09,.3,.05,.13], shot:[.13,.12,.46,.075,.24], smg:[.09,.11,.5,.06,.26], snipe:[.075,.09,.7,.05,.26], wave:[.15,.14,.5,.095,.28]}[W.k]||[.09,.11,.36,.06,.2];
    const [w,h,L,tr,tl]=P;
    A(B(w,h,L),W.col,0,0,-L/2+.06); A(B(w*.8,h*.5,L*.6),dk(W.col),0,-h*.35,-L*.45);
    A(C(tr,tl,16),W.tk,0,h/2+tr*.7,-L*.45,Z); [1,-1].forEach(e=>{ const m=A(S(tr),W.tk,0,h/2+tr*.7,-L*.45+e*tl/2); m.scale.z=.55; }); A(C(tr*.5,.05,10),0xffffff,0,h/2+tr*1.62,-L*.45+tl*.3);
    A(B(w*.85,.2,.1),dk(W.col),0,-h/2-.08,.0,.32); A(C(.045,.14,12),W.tk,0,-h/2-.02,-L*.72,Z);
    if(W.k==="shot"){ [-.045,0,.045].forEach(x=>A(C(.024,.1,10),0xffffff,x,.01,-L+.0,Z)); }
    else if(W.k==="wave"){ A(C(.07,.16,18,.12),0xffffff,0,0,-L-.02,-Z); A(C(.125,.03,18),W.tk,0,0,-L-.1,Z); }
    else { A(C(.028,.1,10),0xffffff,0,0,-L+.02,Z); A(C(.036,.025,12),W.tk,0,0,-L+.06,Z); }
    if(W.k==="snipe"){ A(C(.035,.26,12),0x2a3550,0,h/2+.11,-L*.25,Z); A(C(.04,.02,12),0x7fe0ff,0,h/2+.11,-L*.25-.14,Z); }
    if(W.k==="duo" && !small){ const G2=new THREE.Group(); G.add(G2); G2.position.set(-.42,0,0); H.children.forEach(m=>G2.add(m.clone())); G.userData.twin=G2; } }

  /* ════ 선수(나 + 봇 5) ════ */
  const ACT=[];
  function mkAct(o){ const a=Object.assign({p:new V3(), v:new V3(), yaw:0, pitch:0, onG:true, sl:false, slT:0, slCD:0, soak:0, alive:true, resp:0, prot:PROT, wi:0, kills:0, asst:0, lastHit:-9, by:null, dmgBy:new Map(), cd:0, hold:0, h:HH, jbuf:0, coy:0, padT:0, dead:0}, o); ACT.push(a); return a; }
  const me=mkAct({me:true, nm:api.nick});
  const AVH=1.25, AVK=1.42;   /* 아바타 키 1.25 → ×1.42 ≈ 1.78 */
  const HB_AV={h:1.28,hr:.42,b:.68,br:.46,l:.25,lr:.34}, HB_BK={h:1.53,hr:.34,b:.98,br:.42,l:.36,lr:.3};   /* 맞는 자리(머리·몸·다리) — 블록 사람은 머리가 작고 높음 */
  BOTS.forEach((b,i)=>{ const a=mkAct({bot:true, nm:b.nm, i});
    let c=null; try{ c=buildAvatar(b.av); }catch(e){ c=null; }
    const G=new THREE.Group(); scene.add(G); a.G=G;
    if(c){ c.g.scale.setScalar(AVK); G.add(c.g); a.c=c; c.g.traverse(m=>{ if(m.isMesh){ m.castShadow=!api.low; } }); }
    else { const m=new THREE.Mesh(new THREE.CapsuleGeometry ? new THREE.CylinderGeometry(.35,.35,1.7,10) : new THREE.CylinderGeometry(.35,.35,1.7,10), toon(new THREE.MeshStandardMaterial({color:0xff9a3d}))); m.position.y=.85; G.add(m); }
    a.gun=new THREE.Group(); if(c && c.armR){ c.armR.add(a.gun); a.gun.position.set(0,-.2,0); a.gun.scale.setScalar(.7); }
    a.tag=nameTag(b.nm); a.tag.position.y=2.15; G.add(a.tag);
    const bub=new THREE.Mesh(new THREE.SphereGeometry(1.15,16,12), new THREE.MeshBasicMaterial({color:0x9fe8ff, transparent:true, opacity:.25, depthWrite:false})); bub.position.y=.95; G.add(bub); a.bub=bub;
    a.brain={tg:null, see:false, seeT:0, react:0, path:[], pathT:0, goal:null, str:1, strT:0, stuckT:0, lastP:new V3(), aimY:0, aimP:0, ex:0, ey:0, eT:0, think:Math.random()*.2, roam:null};
    gunModel(a.gun, 0, true); });
  /* 머리 위 이름 · 젖음 막대 */
  function nameTag(nm){ const cv=document.createElement("canvas"); cv.width=256; cv.height=72; const tx=new THREE.CanvasTexture(cv); tx.encoding=THREE.sRGBEncoding; disp.push(tx);
    const sp=new THREE.Sprite(new THREE.SpriteMaterial({map:tx, depthWrite:false, transparent:true})); sp.scale.set(1.5,.42,1); sp.userData={cv, tx, nm, k:-1, w:-1}; drawTag(sp, 0, 0); return sp; }
  function drawTag(sp, soak, wi){ const u=sp.userData, k=Math.round(soak/5); if(u.k===k && u.w===wi) return; u.k=k; u.w=wi; const g=u.cv.getContext("2d"); g.clearRect(0,0,256,72);
    g.font="800 30px Nunito, Jua, sans-serif"; g.textAlign="center"; g.lineWidth=7; g.strokeStyle="rgba(20,30,60,.8)"; const t=WP[wi].ic+" "+u.nm; g.strokeText(t,128,32); g.fillStyle="#fff"; g.fillText(t,128,32);
    g.fillStyle="rgba(20,30,60,.7)"; g.fillRect(48,46,160,14); g.fillStyle=soak>66?"#2f7fff":"#7fd3ff"; g.fillRect(50,48,156*Math.min(1,soak/100),10); u.tx.needsUpdate=true; }

  /* ════ 내 화면 총 (따로 그려서 벽에 안 묻힘) ════ */
  const vmS=new THREE.Scene(), vmC=new THREE.PerspectiveCamera(58, 1, .01, 10); vmS.add(new THREE.HemisphereLight(0xffffff, 0x8899bb, .5)); { const l=new THREE.DirectionalLight(0xffffff,.95); l.position.set(.6,2,1.2); vmS.add(l); }
  const VM=new THREE.Group(); vmS.add(VM); const VMG=new THREE.Group(); VM.add(VMG);
  const hand=new THREE.Mesh(new THREE.SphereGeometry(.07,12,10), toon(new THREE.MeshStandardMaterial({color:(()=>{ try{ return AV_OPT.skin[api.av.skin|0]; }catch(e){ return "#ffe0c2"; } })(), roughness:.8})));
  function vmSet(wi){ gunModel(VMG, wi, false); VMG.add(hand); hand.position.set(0,-.2,.03); hand.scale.set(1,1.15,1.25); VM.userData.wi=wi; }
  /* (v592) 사용자: 「캐릭터 모델은 없을까」 → 「이건 아레나 지금 해 줘」 — Kenney Blocky Characters 2.0(CC0) 로블록스 같은 블록 사람 6종 · 부위(다리·몸·팔·머리)를 직접 움직임 */
  const BKS=["b","d","e","n","o","g"];
  function blockify(a, P, k){ if(!P) return; const tx=new THREE.TextureLoader().load("../assets/mg/blocky/skin-"+k+".webp"); tx.encoding=THREE.sRGBEncoding; tx.flipY=false; tx.wrapS=tx.wrapT=THREE.RepeatWrapping; tx.magFilter=tx.minFilter=THREE.NearestFilter; tx.generateMipmaps=false; disp.push(tx);
    const mat=toon(new THREE.MeshStandardMaterial({map:tx, roughness:.9})); disp.push(mat);
    const part=n=>{ const q=P[n], g=new THREE.BufferGeometry(); g.setAttribute("position",new THREE.Float32BufferAttribute(q.p,3)); g.setAttribute("normal",new THREE.Float32BufferAttribute(q.n,3)); g.setAttribute("uv",new THREE.Float32BufferAttribute(q.u,2)); g.setIndex(q.i); g.computeBoundingSphere(); disp.push(g);
      const m=new THREE.Mesh(g, mat); m.castShadow=!api.low; const o=new THREE.Group(); o.position.fromArray(q.t); const w=new THREE.Group(); w.scale.fromArray(q.s); w.add(m); o.add(w); return o; };
    const root=new THREE.Group(), legL=part("leg-left"), legR=part("leg-right"), torso=part("torso"), armL=part("arm-left"), armR=part("arm-right"), head=part("head");
    root.add(legL, legR, torso); torso.add(armL, armR, head); root.scale.setScalar(.667);
    if(a.c){ a.G.remove(a.c.g); a.c=null; } a.G.add(root); a.bk={g:root, legL, legR, torso, armL, armR, head, t:Math.random()*6};
    armR.add(a.gun); a.gun.position.set(-.2,-.95,.02); a.gun.scale.setScalar(1.35); a.hb=HB_BK; }
  let gone=false;
  try{ fetch("../assets/mg/blocky/blocky.json").then(r=>r.json()).then(J=>{ if(gone) return; ACT.forEach(a=>{ if(a.bot){ const k=BKS[a.i%BKS.length]; blockify(a, J[k], k); } }); }).catch(e=>console.warn("blocky", e)); }catch(e){}
  try{ KK.load("blaster").then(()=>{ if(gone) return; vmSet(me.wi); ACT.forEach(a=>{ if(a.bot) gunModel(a.gun, a.wi, true); }); }); }catch(e){}
  vmSet(0); VM.position.set(.24,-.22,-.5); const vmA={kick:0, sw:1, bob:0, swing:0, side:1};

  /* ════ 물줄기 · 물보라 (작은 공 여러 개를 한 번에) ════ */
  const DROP=new THREE.InstancedMesh(new THREE.SphereGeometry(.06,6,4), new THREE.MeshBasicMaterial({color:0x8fe3ff, transparent:true, opacity:.9}), 900); DROP.frustumCulled=false; DROP.count=0; scene.add(DROP); disp.push(DROP.geometry);
  const SPL=new THREE.InstancedMesh(new THREE.SphereGeometry(.07,6,4), new THREE.MeshBasicMaterial({color:0xc8f3ff, transparent:true, opacity:.85}), 500); SPL.frustumCulled=false; SPL.count=0; scene.add(SPL); disp.push(SPL.geometry);
  const STR=[], PAR=[], BAL=[]; const _m=new THREE.Matrix4(), _q=new THREE.Quaternion(), _s=new V3(), _v=new V3(), _w=new V3();
  function stream(a, b, w, big){ const L=a.distanceTo(b); STR.push({a:a.clone(), b:b.clone(), L, t:0, sp:big?52:78, w:w||1, big}); }
  function burst(p, n, k){ for(let i=0;i<n && PAR.length<480;i++){ const th=Math.random()*Math.PI*2, ph=Math.random()*1.2; PAR.push({p:p.clone(), v:new V3(Math.cos(th)*Math.sin(ph)*(2+Math.random()*3)*(k||1), (1.5+Math.random()*3.5)*(k||1), Math.sin(th)*Math.sin(ph)*(2+Math.random()*3)*(k||1)), t:0, L:.35+Math.random()*.35, s:.6+Math.random()*.9}); } }
  const BALG=new THREE.SphereGeometry(.2,14,10); disp.push(BALG);
  function fxTick(dt){ let n=0;
    for(let i=STR.length-1;i>=0;i--){ const s=STR[i]; s.t+=dt; const hd=Math.min(s.L, s.t*s.sp), tl=Math.max(0, hd-(s.big?3.2:2.2));
      if(tl>=s.L-1e-3){ STR.splice(i,1); continue; } const k=s.big?9:6;
      for(let j=0;j<k && n<900;j++){ const f=tl+(hd-tl)*(j/(k-1)); _v.copy(s.a).lerp(s.b, s.L>0?f/s.L:1); const sc=(s.big?2.2:1.15)*s.w*(.55+.45*j/(k-1)); _s.set(sc,sc,sc); _m.compose(_v,_q,_s); DROP.setMatrixAt(n++, _m); } }
    DROP.count=n; DROP.instanceMatrix.needsUpdate=true; n=0;
    for(let i=PAR.length-1;i>=0;i--){ const p=PAR[i]; p.t+=dt; if(p.t>p.L){ PAR.splice(i,1); continue; } p.v.y-=14*dt; p.p.addScaledVector(p.v, dt); if(p.p.y<.02){ p.p.y=.02; p.v.y*=-.2; p.v.x*=.6; p.v.z*=.6; } const sc=p.s*(1-p.t/p.L*.6); _s.set(sc,sc,sc); _m.compose(p.p,_q,_s); if(n<500) SPL.setMatrixAt(n++, _m); }
    SPL.count=n; SPL.instanceMatrix.needsUpdate=true;
    for(let i=BAL.length-1;i>=0;i--){ const b=BAL[i]; b.t+=dt; b.v.y-=13*dt; const o=b.m.position.clone(); b.m.position.addScaledVector(b.v, dt); b.m.rotation.x+=dt*6; const d=b.m.position.clone().sub(o), L=d.length(); let hit=null;
      if(L>0){ d.divideScalar(L); const r=rayBox(o, d, L); if(r.t<L) hit=o.addScaledVector(d, r.t); }
      if(!hit) for(const a of ACT){ if(a===b.by || !a.alive) continue; if(b.m.position.distanceTo(_w.set(a.p.x, a.p.y+.85*(a.h/HH), a.p.z))<.75){ hit=b.m.position.clone(); break; } }
      if(!hit && b.t>4) hit=b.m.position.clone();
      if(hit){ scene.remove(b.m); BAL.splice(i,1); pop(hit, b.by); } } }
  function pop(p, by){ burst(p, 30, 1.5); try{ api.sfx.splash(); }catch(e){}
    for(const a of ACT){ if(!a.alive) continue; const c=_w.set(a.p.x, a.p.y+.85*(a.h/HH), a.p.z), d=c.distanceTo(p); if(d<2.9){ const dm=WP[5].dmg*(1-Math.min(1,d/2.9)*.65); if(a!==by) hurt(a, dm, by, 5, false, p); } } }

  /* ════ 쏘기 ════ */
  const time={t:0, left:MATCH, cd:3.2, over:false};
  function eyeOf(a){ return new V3(a.p.x, a.p.y+(a.sl?EYES:EYE), a.p.z); }
  function dirOf(yaw, pitch){ const cp=Math.cos(pitch); return new V3(-Math.sin(yaw)*cp, Math.sin(pitch), -Math.cos(yaw)*cp); }
  function muzzle(a){ if(a.me){ const v=new V3(.26,-.22,-.75); return v.applyMatrix4(cam.matrixWorld); } const e=eyeOf(a), f=dirOf(a.yaw, a.pitch), r=new V3(Math.cos(a.yaw),0,-Math.sin(a.yaw)); return e.addScaledVector(f,.55).addScaledVector(r,.32).add(new V3(0,-.35,0)); }
  function spread(d, deg){ if(!deg) return d; const a=Math.random()*Math.PI*2, r=Math.tan(deg*D2R)*Math.sqrt(Math.random()); const up=Math.abs(d.y)>.95?new V3(1,0,0):new V3(0,1,0), u=new V3().crossVectors(d,up).normalize(), w=new V3().crossVectors(u,d).normalize(); return d.clone().addScaledVector(u,Math.cos(a)*r).addScaledVector(w,Math.sin(a)*r).normalize(); }
  /* 한 줄기: 가장 먼저 맞는 것 (머리 · 몸 · 다리) */
  function trace(sh, o, d, rng){ const wall=rayBox(o, d, rng); let best=wall.t, who=null, head=false;
    for(const a of ACT){ if(a===sh || !a.alive) continue; const k=a.h/HH, P=a.p;
      const hb=a.hb||HB_AV;
      const th=raySph(o,d,_w.set(P.x,P.y+hb.h*k,P.z),hb.hr); if(th>0 && th<best){ best=th; who=a; head=true; }
      const tb=raySph(o,d,_w.set(P.x,P.y+hb.b*k,P.z),hb.br); if(tb>0 && tb<best){ best=tb; who=a; head=false; }
      const tl=raySph(o,d,_w.set(P.x,P.y+hb.l,P.z),hb.lr); if(tl>0 && tl<best){ best=tl; who=a; head=false; } }
    return {t:best, who, head, n:who?null:wall.n}; }
  /* 손 도움(터치): 거의 맞을 때 가장 가까운 적 몸으로 */
  function assist(sh, o, d, rng, deg){ let best=null, bd=deg*D2R;
    for(const a of ACT){ if(a===sh || !a.alive || a.prot>0) continue; const c=new V3(a.p.x, a.p.y+.75*(a.h/HH), a.p.z), v=c.clone().sub(o), L=v.length(); if(L>rng) continue; const ang=v.normalize().angleTo(d); if(ang<bd && sees(o,c)){ bd=ang; best={a, c, L}; } }
    return best; }
  function fire(a, o, d, hint){ const W=WP[a.wi]; a.cd=W.rate*(a.bot?D.fire:1); a.prot=0;
    const mz=muzzle(a); let snd=a.me || o.distanceTo(me.p)<22;
    if(W.t==="melee"){ let best=null, bd=W.rng; for(const t of ACT){ if(t===a || !t.alive) continue; const c=new V3(t.p.x, t.p.y+.8, t.p.z), v=c.clone().sub(o), L=v.length(); if(L>bd+.5) continue; v.y*=.4; if(v.normalize().dot(d)<Math.cos(42*D2R)) continue; if(!sees(o,c)) continue; bd=L; best=t; }
      if(a.me){ vmA.swing=1; me.v.addScaledVector(new V3(d.x,0,d.z).normalize(), 3.2); } if(snd) api.sfx.shot("hammer", !a.me);
      if(best){ burst(new V3(best.p.x,best.p.y+1.1,best.p.z), 16); hurt(best, W.dmg, a, a.wi, false, o); } return; }
    if(W.t==="proj"){ const m=new THREE.Mesh(BALG, gmat(Math.random()<.5?0xff7aa8:0x46b3ff)); m.position.copy(a.me?mz:o.clone().addScaledVector(d,.7)); scene.add(m); BAL.push({m, v:d.clone().multiplyScalar(21).add(new V3(0,3.2,0)), by:a, t:0}); if(snd) api.sfx.shot("balloon", !a.me); if(a.me) vmA.kick=1; return; }
    const n=W.n||1, sp=a.me?(W.t==="snipe" && (Math.hypot(me.v.x,me.v.z)>2 || !me.onG) ? 2.2 : W.spr):W.spr; let hitAny=false, hd=false;
    for(let i=0;i<n;i++){ let dd=spread(d, sp); let r=trace(a, o, dd, W.rng);
      if(!r.who && hint && i===0){ const as=hint(o, dd, W.rng); if(as){ dd=as.c.clone().sub(o).normalize(); r={t:as.L, who:as.a, head:false}; } }
      const end=o.clone().addScaledVector(dd, Math.min(r.t, W.rng)); stream(i===0||n<4?mz:mz, end, W.t==="beam"?1.6:W.t==="snipe"?.8:1, W.t==="beam");
      if(r.who){ let dm=W.dmg; if(W.k==="shot"){ const L=r.t; dm*=L<9?1:Math.max(.35,1-(L-9)/15); } if(r.head && W.t!=="beam") dm*=1.5; hurt(r.who, dm, a, a.wi, r.head, o); hitAny=true; hd=hd||r.head;
        if(W.t==="beam"){ const pu=new V3(dd.x,0,dd.z).normalize().multiplyScalar(5.5*Math.max(.3,1-r.t/16)); r.who.v.x+=pu.x*.35; r.who.v.z+=pu.z*.35; } burst(end, W.t==="beam"?2:4, .6); }
      else if(r.t<W.rng){ if(Math.random()<(W.t==="beam"?.3:1)) burst(end, W.n?2:5, .7); } }
    if(snd) api.sfx.shot(W.k, !a.me); if(a.me){ vmA.kick=W.t==="snipe"?1.6:W.t==="beam"?.25:W.k==="shot"?1.3:.7; vmA.side=-vmA.side; } }

  /* ════ 맞음 · 흠뻑 · 단계 오르기 ════ */
  const FEED=[]; let hitT=0, hitHead=false, hurtT=0, hurtA=0;
  function hurt(t, dm, by, wi, head, from){ if(!t.alive || t.prot>0 || time.over) return; if(by && by.bot) dm*=t.bot?D.bvb:D.dm; t.soak+=dm; t.lastHit=time.t; t.by=by; t.dmgBy.set(by, (t.dmgBy.get(by)||0)+dm);
    if(by && by.me){ hitT=.18; hitHead=head; api.sfx.hit(head); }
    if(t.me){ hurtT=.7; if(from){ const v=new V3().subVectors(from, me.p); hurtA=Math.atan2(v.x, v.z); } api.sfx.hurt(); }
    if(t.bot && by && !t.brain.tg){ t.brain.tg=by; t.brain.react=D.react*.6; }
    if(t.soak>=100) soaked(t, by, wi); }
  function soaked(t, by, wi){ t.alive=false; t.deaths=(t.deaths|0)+1; t.soak=100; t.resp=RESP; t.dead=0; t.sl=false; t.h=HH; burst(new V3(t.p.x,t.p.y+1,t.p.z), 34, 1.4); api.sfx.soak();
    FEED.unshift({a:by?by.nm:"", b:t.nm, ic:by?WP[wi].ic:"💧", me:(by&&by.me)||t.me, t:5}); if(FEED.length>4) FEED.length=4; drawFeed();
    if(by && by!==t){ by.kills++; if(wi>=LAST && by.wi>=LAST){ win(by); return; } up(by);
      t.dmgBy.forEach((v,k)=>{ if(k && k!==by && k!==t && v>=40 && k.alive){ k.asst++; if(k.asst>=2 && k.wi<LAST-1){ k.asst=0; up(k, true); } } }); }
    t.dmgBy.clear();
    if(t.me){ api.msg('💦 흠뻑!<small>'+(by&&by!==t?esc(by.nm)+' 의 '+WP[wi].ic+' '+WP[wi].nm:'')+'</small>', 1900); } }
  function up(a, asst){ if(a.wi>=LAST) return; a.wi++; if(a.bot){ gunModel(a.gun, a.wi, true); return; }
    api.sfx.up(); vmA.sw=0; setTimeout(()=>{ vmSet(me.wi); }, 160); fireIc();
    api.msg((asst?'🤝 도움 2번! ':'🎉 ')+WP[a.wi].ic+' '+WP[a.wi].nm+'<small>'+(a.wi===LAST?'마지막! 🔨 뿅망치로 맞히면 우승!':(a.wi+1)+' / '+WP.length+' 단계')+'</small>', 1700); drawLadder(); }
  const esc=s=>String(s).replace(/[<>&]/g,c=>({"<":"&lt;",">":"&gt;","&":"&amp;"}[c]));

  /* ════ 움직임 (내 것 · 봇 같은 규칙) ════ */
  function accel(a, dx, dz, ws, ac, dt){ const cur=a.v.x*dx+a.v.z*dz, add=ws-cur; if(add<=0) return; const s=Math.min(ac*dt*Math.max(ws,1), add); a.v.x+=dx*s; a.v.z+=dz*s; }
  function moveAct(a, wx, wz, wl, jump, slideP, slideH, dt){
    const hs=Math.hypot(a.v.x, a.v.z), wasG=a.onG; a.slCD=Math.max(0,a.slCD-dt); a.padT=Math.max(0,a.padT-dt);
    if(a.onG){
      /* 🛝 슬라이드 시작 — 달리는 중 · 쉬는 시간이 끝났으면 속도 붙음 */
      if((slideP || (slideH && a.landT>0)) && !a.sl && hs>3.6){ a.sl=true; a.slT=0; const k=a.slCD<=0?Math.min(SLBOOST, Math.max(0, SLMAX-hs)):0; a.v.x+=a.v.x/hs*k; a.v.z+=a.v.z/hs*k; a.slCD=SLCD; if(a.me) api.sfx.slide(); }
      if(jump){ a.v.y=JV; a.onG=false; a.coy=0; if(a.sl){ a.sl=false; } if(a.me) api.sfx.jump(); }
      else { const fr=a.sl?SLFRIC:FRIC, sp=Math.hypot(a.v.x,a.v.z); if(sp>0){ const drop=Math.max(sp,STOP)*fr*dt, ns=Math.max(0,sp-drop)/sp; a.v.x*=ns; a.v.z*=ns; }
        if(a.sl){ accel(a, wx, wz, 2.2*wl, 3, dt); a.slT+=dt; const s2=Math.hypot(a.v.x,a.v.z); if(s2<3.2 || a.slT>1.25 || (!slideH && a.slT>.55)){ if(free(a.p,HH)) a.sl=false; } }
        else accel(a, wx, wz, MAXS*wl*(a.bot?D.spd:1), ACC, dt); } }
    else { accel(a, wx, wz, Math.min(MAXS*wl, AIRCAP), AIRACC, dt); a.v.y-=GRAV*dt; if(a.sl && a.v.y<0 && free(a.p,HH)) a.sl=false; }
    const sp=Math.hypot(a.v.x,a.v.z); if(sp>HCAP){ a.v.x*=HCAP/sp; a.v.z*=HCAP/sp; }
    a.h=a.sl?HS:HH; a.landT=Math.max(0,(a.landT||0)-dt);
    /* 축마다 움직이고 밀어내기 · 낮은 턱(0.55)은 올라섬 */
    const P=a.p; a.onG=false;
    for(const ax of ["x","z"]){ P[ax]+=a.v[ax]*dt; const A=aabb(P,a.h);
      for(const b of BOX){ if(!ov(A,b)) continue; const up=b.y1-P.y;
        if(up>0 && up<=STEP && (wasG||a.coy>0)){ const t={x:P.x, y:b.y1+1e-3, z:P.z}; if(free(t,a.h)){ P.y=b.y1+1e-3; Object.assign(A, aabb(P,a.h)); continue; } }
        if(a.v[ax]>0) P[ax]=(ax==="x"?b.x0:b.z0)-HW-1e-3; else P[ax]=(ax==="x"?b.x1:b.z1)+HW+1e-3; a.v[ax]=0; Object.assign(A, aabb(P,a.h)); } }
    if(wasG && a.v.y<=0) a.v.y=-.5;
    P.y+=a.v.y*dt; { const A=aabb(P,a.h); for(const b of BOX){ if(!ov(A,b)) continue; if(a.v.y<=0){ P.y=b.y1; a.v.y=0; a.onG=true; } else { P.y=b.y0-a.h-1e-3; a.v.y=0; } Object.assign(A, aabb(P,a.h)); } }
    if(P.y<=0){ P.y=0; if(a.v.y<0) a.v.y=0; a.onG=true; }
    /* 계단 내려갈 때 붙어 있기 */
    if(!a.onG && wasG && a.v.y<=0){ let top=0; const A=aabb(P,a.h); A.y0=P.y-.6; A.y1=P.y; for(const b of BOX) if(ov(A,b) && b.y1<=P.y+1e-3) top=Math.max(top,b.y1); if(P.y-top<.6){ P.y=top; a.v.y=0; a.onG=true; } }
    if(a.onG && !wasG){ a.landT=.12; if(a.me && a.fallV<-6) api.sfx.land(); }
    a.fallV=a.v.y; a.coy=a.onG?.1:Math.max(0,(a.coy||0)-dt);
    /* 💧 분수 발판 */
    if(a.onG && a.padT<=0) for(const [x,z] of PADS){ if(Math.hypot(P.x-x,P.z-z)<1.0){ a.v.y=PADV; a.onG=false; a.padT=.6; a.sl=false; burst(new V3(x,.2,z), 22, 1.3); if(a.me || P.distanceTo(me.p)<16) api.sfx.pad(); break; } } }

  /* ════ 나오는 자리 — 다른 사람에게서 가장 먼 곳 ════ */
  function spawn(a){ let best=SPAWN[0], bd=-1; SPAWN.forEach(s=>{ let m=1e9; for(const o of ACT){ if(o===a || !o.alive) continue; m=Math.min(m, Math.hypot(o.p.x-s[0], o.p.z-s[1])); } m+=Math.random()*4; if(m>bd){ bd=m; best=s; } });
    a.p.set(best[0], 0, best[1]); a.v.set(0,0,0); a.soak=0; a.alive=true; a.prot=PROT; a.sl=false; a.h=HH; a.onG=true; a.dmgBy.clear(); a.yaw=Math.atan2(best[0], best[1]); a.pitch=0; a.cd=.3;
    if(a.bot){ a.brain.tg=null; a.brain.path=[]; a.brain.aimY=a.yaw; a.G.visible=true; a.G.rotation.set(0,0,0); } }

  /* ════ 봇 길 찾기 (0.5m 칸 높이 지도) ════ */
  const NC=100, CS=.5, HT=new Float32Array(NC*NC), BL=new Uint8Array(NC*NC);
  for(let i=0;i<NC;i++) for(let j=0;j<NC;j++){ const x=-R+CS*(i+.5), z=-R+CS*(j+.5); let top=0; for(const b of BOX) if(b.y0===0 && x>b.x0 && x<b.x1 && z>b.z0 && z<b.z1) top=Math.max(top,b.y1); HT[j*NC+i]=top;
    let bl=0; for(const b of BOX){ if(x+.36>b.x0 && x-.36<b.x1 && z+.36>b.z0 && z-.36<b.z1){ if(b.y1>top+.45 && b.y0<top+1.7) { bl=1; break; } } } BL[j*NC+i]=bl || top>3; }
  const cell=(x,z)=>[Math.max(0,Math.min(NC-1,Math.floor((x+R)/CS))), Math.max(0,Math.min(NC-1,Math.floor((z+R)/CS)))];
  function path(a, gx, gz){ const [sx,sz]=cell(a.p.x,a.p.z); let [tx,tz]=cell(gx,gz); if(BL[tz*NC+tx]){ let f=null; for(let r=1;r<8 && !f;r++) for(let dx=-r;dx<=r && !f;dx++) for(let dz=-r;dz<=r;dz++){ const x=tx+dx, z=tz+dz; if(x<0||z<0||x>=NC||z>=NC) continue; if(!BL[z*NC+x]){ f=[x,z]; break; } } if(!f) return []; [tx,tz]=f; }
    const pv=new Int32Array(NC*NC).fill(-2), q=new Int32Array(NC*NC); let h=0, t=0; const st=sz*NC+sx, goal=tz*NC+tx; pv[st]=-1; q[t++]=st;
    while(h<t){ const c=q[h++]; if(c===goal) break; const x=c%NC, z=(c-x)/NC, hc=HT[c]; for(const [dx,dz] of [[1,0],[-1,0],[0,1],[0,-1],[1,1],[1,-1],[-1,1],[-1,-1]]){ const nx=x+dx, nz=z+dz; if(nx<0||nz<0||nx>=NC||nz>=NC) continue; const ni=nz*NC+nx; if(pv[ni]!==-2 || BL[ni] || Math.abs(HT[ni]-hc)>.45) continue; if(dx&&dz && (BL[z*NC+nx]||BL[nz*NC+x])) continue; pv[ni]=c; q[t++]=ni; } }
    if(pv[goal]===-2) return []; const out=[]; for(let c=goal;c!==-1 && c!==st;c=pv[c]){ const x=c%NC, z=(c-x)/NC; out.push([-R+CS*(x+.5), -R+CS*(z+.5)]); } out.reverse();
    const sm=[]; let i=0; while(i<out.length){ let j=Math.min(out.length-1,i+10); while(j>i+1 && !lineOK(out[i],out[j])) j--; sm.push(out[j]); i=j+1; } return sm; }
  function lineOK(a, b){ const L=Math.hypot(b[0]-a[0],b[1]-a[1]), n=Math.ceil(L/.25); let h0=null; for(let k=0;k<=n;k++){ const x=a[0]+(b[0]-a[0])*k/n, z=a[1]+(b[1]-a[1])*k/n, [i,j]=cell(x,z), c=j*NC+i; if(BL[c]) return false; if(h0!=null && Math.abs(HT[c]-h0)>.45) return false; h0=HT[c]; } return true; }

  /* ════ 봇 머리 ════ */
  const angN=a=>{ while(a>Math.PI) a-=Math.PI*2; while(a<-Math.PI) a+=Math.PI*2; return a; };
  function botThink(a){ const B=a.brain, e=eyeOf(a); let best=null, bs=1e9, onMe=ACT.filter(o=>o.bot && o!==a && o.alive && o.brain.tg===me).length;
    for(const o of ACT){ if(o===a || !o.alive) continue; const c=new V3(o.p.x,o.p.y+.9*(o.h/HH),o.p.z), L=c.distanceTo(e); if(L>48) continue; const vis=sees(e,c); let s=L+(vis?0:22)+(o.prot>0?12:0); if(o===me && onMe>=D.gang && B.tg!==me) s+=30; if(o===B.tg) s-=6; if(s<bs){ bs=s; best={o, vis, c}; } }
    const old=B.tg; B.tg=best?best.o:null; B.see=!!(best && best.vis); if(B.tg!==old) B.react=D.react*(.8+Math.random()*.5);
    if(B.see) B.last=best.c.clone();
    const W=WP[a.wi]; let goal=null;
    if(B.tg && !B.see) goal=[B.tg.p.x, B.tg.p.z];
    else if(B.tg && B.see){ const L=Math.hypot(B.tg.p.x-a.p.x, B.tg.p.z-a.p.z); if(L>W.pref+4 || W.t==="melee") goal=[B.tg.p.x, B.tg.p.z]; }
    else { if(!B.roam || Math.hypot(B.roam[0]-a.p.x,B.roam[1]-a.p.z)<2) B.roam=SPAWN[Math.floor(Math.random()*SPAWN.length)]; goal=B.roam; }
    if(goal && (time.t>B.pathT || !B.path.length || !B.goal || Math.hypot(goal[0]-B.goal[0],goal[1]-B.goal[1])>3)){ B.path=path(a, goal[0], goal[1]); B.goal=goal; B.pathT=time.t+.8+Math.random()*.4; }
    if(!goal) B.path=[]; }
  function botTick(a, dt){ const B=a.brain; B.think-=dt; if(B.think<=0){ B.think=.16+Math.random()*.08; botThink(a); }
    let wx=0, wz=0, wl=0, jump=false, slide=false;
    const W=WP[a.wi], tg=B.tg && B.tg.alive ? B.tg : null;
    if(B.path.length){ const w=B.path[0], dx=w[0]-a.p.x, dz=w[1]-a.p.z, L=Math.hypot(dx,dz); if(L<.5){ B.path.shift(); } else { wx=dx/L; wz=dz/L; wl=1; } }
    if(tg && B.see){ const dx=tg.p.x-a.p.x, dz=tg.p.z-a.p.z, L=Math.hypot(dx,dz)||1; B.strT-=dt; if(B.strT<=0){ B.str=Math.random()<.5?-1:1; B.strT=.6+Math.random()*1.1; }
      const sx=-dz/L*B.str, sz=dx/L*B.str; let fx=0, fz=0; if(W.t==="melee"){ fx=dx/L; fz=dz/L; } else if(L<W.pref-3){ fx=-dx/L; fz=-dz/L; } else if(L>W.pref+3 && !B.path.length){ fx=dx/L; fz=dz/L; }
      if(!B.path.length || W.t!=="melee"){ wx=sx*.85+fx+(B.path.length?wx*.6:0); wz=sz*.85+fz+(B.path.length?wz*.6:0); const m=Math.hypot(wx,wz)||1; wx/=m; wz/=m; wl=1; }
      if(a.onG && Math.random()<dt*(W.t==="melee"?.9:.35)) jump=true;
      if(a.onG && W.t==="melee" && L>5 && L<11 && Math.random()<dt*1.2) slide=true; }
    /* 막힘 → 점프 + 다시 길 찾기 */
    B.stuckT+=dt; if(B.stuckT>.9){ if(wl>0 && a.p.distanceTo(B.lastP)<.45){ jump=true; B.pathT=0; B.str=-B.str; B.roam=null; } B.stuckT=0; B.lastP.copy(a.p); }
    moveAct(a, wx, wz, wl, jump && a.onG, slide, slide, dt);
    /* 조준: 몸으로 천천히 · 흔들림(쉬움일수록 큼) */
    let ty=wl>0?Math.atan2(-wx,-wz):a.yaw, tp=0;
    if(tg && (B.see || B.last)){ const c=B.see?new V3(tg.p.x, tg.p.y+.85*(tg.h/HH), tg.p.z):B.last, e=eyeOf(a); if(W.t==="proj"){ c.y-=.6; } const v=c.clone().sub(e), L=v.length();
      B.eT-=dt; if(B.eT<=0){ const tv=Math.hypot(tg.v.x,tg.v.z), k=D.err*(1+Math.min(1.2,tv/8))*D2R; B.ex=(Math.random()*2-1)*k; B.ey=(Math.random()*2-1)*k*.6; B.eT=.25+Math.random()*.35; }
      ty=Math.atan2(-v.x,-v.z)+B.ex; tp=Math.asin(Math.max(-1,Math.min(1,v.y/L)))+B.ey+(W.t==="proj"?Math.min(.35,L*.012):0); }
    const dy=angN(ty-a.yaw); a.yaw+=Math.sign(dy)*Math.min(Math.abs(dy), D.turn*dt); a.pitch+=(tp-a.pitch)*Math.min(1,dt*D.turn*.8);
    /* 쏘기 */
    a.cd-=dt; if(tg && B.see){ B.react-=dt; if(B.react<=0 && a.cd<=0 && a.prot<=0){ const e=eyeOf(a), c=new V3(tg.p.x,tg.p.y+.8*(tg.h/HH),tg.p.z), L=c.distanceTo(e), ok=W.t==="melee"?L<W.rng+.3:L<W.rng*(W.t==="hs"&&W.k==="shot"?.9:1);
        if(ok && Math.abs(angN(Math.atan2(-(c.x-e.x),-(c.z-e.z))-a.yaw))<.22) fire(a, e, dirOf(a.yaw, a.pitch)); } }
    /* 모습 */
    const G=a.G; G.position.set(a.p.x, a.p.y, a.p.z); if(a.c){ const c=a.c; c.face=a.yaw+Math.PI; c.moving=Math.hypot(a.v.x,a.v.z)>1.2 && a.onG && !a.sl; try{ animChar(c, dt); }catch(e){}
      c.g.rotation.y=a.yaw+Math.PI; c.g.rotation.x=a.sl?-.55:0; c.g.position.y=a.sl?.15:0;
      if(c.armR){ c.armR.rotation.x=-Math.PI/2-a.pitch*.8; c.armR.rotation.z=0; } if(c.armL){ c.armL.rotation.x=-1.25-a.pitch*.6; c.armL.rotation.z=-.35; } }
    if(a.bk){ const B=a.bk, hs=Math.hypot(a.v.x,a.v.z), mv=hs>1.2 && a.onG && !a.sl; B.t+=dt*(mv?Math.min(14,5+hs*1.1):0); const sw=mv?Math.sin(B.t)*.8:0;
      B.legL.rotation.x=a.onG?sw:-.55; B.legR.rotation.x=a.onG?-sw:.35;
      B.g.rotation.set(a.sl?-.6:0, a.yaw+Math.PI, 0); B.g.position.y=a.sl?.25:(mv?Math.abs(Math.cos(B.t))*.05:0);
      B.armR.rotation.set(-Math.PI/2-a.pitch*.8,0,0); B.armL.rotation.set(-Math.PI/2+.2-a.pitch*.6,-.5,0); B.head.rotation.set(-a.pitch*.5,0,0); }
    a.bub.visible=a.prot>0; drawTag(a.tag, a.soak, a.wi); }

  /* ════ 화면 글자(HUD) ════ */
  const hud=api.hud;
  hud.innerHTML=`<style>
#mgUI .aCx{position:absolute;left:50%;top:50%;width:0;height:0;pointer-events:none}
#mgUI .aCx i{position:absolute;background:#fff;border-radius:2px;box-shadow:0 0 0 1.5px rgba(20,30,60,.55)}
#mgUI .aCx .h{width:10px;height:3px;top:-1.5px} #mgUI .aCx .v{width:3px;height:10px;left:-1.5px}
#mgUI .aCx .d{width:4px;height:4px;left:-2px;top:-2px;border-radius:50%}
#mgUI .aHm{position:absolute;left:50%;top:50%;width:34px;height:34px;margin:-17px 0 0 -17px;pointer-events:none;opacity:0}
#mgUI .aHm:before,#mgUI .aHm:after{content:"";position:absolute;left:15px;top:0;width:4px;height:34px;background:#fff;border-radius:2px;transform:rotate(45deg);box-shadow:0 0 0 1.5px rgba(20,30,60,.5)}
#mgUI .aHm:after{transform:rotate(-45deg)} #mgUI .aHm.hd:before,#mgUI .aHm.hd:after{background:#ffd23f}
#mgUI .aWet{position:absolute;inset:0;pointer-events:none;opacity:0;background:radial-gradient(ellipse at center, rgba(70,170,255,0) 45%, rgba(40,140,255,.55) 100%)}
#mgUI .aDir{position:absolute;left:50%;top:50%;width:150px;height:150px;margin:-75px 0 0 -75px;pointer-events:none;opacity:0}
#mgUI .aDir i{position:absolute;left:50%;top:-6px;width:46px;height:16px;margin-left:-23px;border-radius:50% 50% 0 0;background:rgba(40,150,255,.85);box-shadow:0 0 10px rgba(40,150,255,.8)}
#mgUI .aTop{position:absolute;left:50%;top:calc(8px + env(safe-area-inset-top));transform:translateX(-50%);display:flex;flex-direction:column;align-items:center;gap:4px;pointer-events:none}
#mgUI .aClock{background:rgba(20,30,60,.55);border-radius:12px;padding:3px 12px;font-size:18px;font-family:var(--en);font-weight:900}
#mgUI .aLad{display:flex;gap:3px} #mgUI .aLad b{width:24px;height:24px;border-radius:8px;background:rgba(20,30,60,.4);display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:400;opacity:.55}
#mgUI .aLad b.d{opacity:.35;filter:grayscale(1)} #mgUI .aLad b.c{opacity:1;background:#ff8466;transform:scale(1.2);box-shadow:0 2px 0 #d9604a}
#mgUI .aBd{position:absolute;right:max(8px,env(safe-area-inset-right));top:calc(56px + env(safe-area-inset-top));background:rgba(20,30,60,.45);border-radius:12px;padding:5px 8px;font-size:13px;line-height:1.5;pointer-events:none;min-width:104px}
#mgUI .aBd div{display:flex;gap:6px;justify-content:space-between} #mgUI .aBd .me{color:#ffd23f}
#mgUI .aFd{position:absolute;left:max(8px,env(safe-area-inset-left));top:calc(56px + env(safe-area-inset-top));font-size:13px;line-height:1.6;pointer-events:none}
#mgUI .aFd div{background:rgba(20,30,60,.45);border-radius:10px;padding:1px 8px;margin-bottom:3px;width:max-content}
#mgUI .aFd .me{background:rgba(255,132,102,.75)}
#mgUI .aWpn{position:absolute;left:50%;bottom:calc(14px + env(safe-area-inset-bottom));transform:translateX(-50%);background:rgba(20,30,60,.5);border-radius:14px;padding:4px 12px;font-size:15px;pointer-events:none;white-space:nowrap}
#mgUI .aWpn small{opacity:.8}
#mgUI .aSoak{position:absolute;left:50%;bottom:calc(46px + env(safe-area-inset-bottom));transform:translateX(-50%);width:150px;height:10px;border-radius:6px;background:rgba(20,30,60,.5);overflow:hidden;pointer-events:none}
#mgUI .aSoak i{display:block;height:100%;width:0;background:linear-gradient(90deg,#7fd3ff,#2f7fff)}
#mgUI .aCnt{position:absolute;left:50%;top:42%;transform:translate(-50%,-50%);font-size:84px;font-family:var(--en);font-weight:900;text-shadow:0 5px 0 rgba(0,0,0,.25);pointer-events:none}
#mgUI .aDead{position:absolute;inset:0;background:rgba(60,150,255,.35);pointer-events:none;opacity:0;transition:opacity .25s}
#mgUI .aHint{position:absolute;left:50%;bottom:calc(74px + env(safe-area-inset-bottom));transform:translateX(-50%);font-size:13px;background:rgba(20,30,60,.45);border-radius:10px;padding:4px 10px;pointer-events:none;white-space:nowrap}
#mgUI .mgB[data-b=fire]{right:max(22px,calc(env(safe-area-inset-right) + 14px));bottom:calc(130px + env(safe-area-inset-bottom));width:98px;height:98px;font-size:40px;background:rgba(255,132,102,.5)}
#mgUI .mgB[data-b=jump]{right:max(18px,calc(env(safe-area-inset-right) + 10px));bottom:calc(36px + env(safe-area-inset-bottom));width:80px;height:80px;font-size:16px}
#mgUI .mgB[data-b=slide]{right:max(112px,calc(env(safe-area-inset-right) + 104px));bottom:calc(30px + env(safe-area-inset-bottom));width:68px;height:68px;font-size:13px}
#mgUI .mgB[data-b=fire2]{left:max(20px,calc(env(safe-area-inset-left) + 12px));bottom:calc(200px + env(safe-area-inset-bottom));width:64px;height:64px;font-size:26px;background:rgba(255,132,102,.4)}
</style>
<div class="aWet"></div><div class="aDead"></div><div class="aDir"><i></i></div>
<div class="aCx"><i class="h" style="left:-18px"></i><i class="h" style="left:8px"></i><i class="v" style="top:-18px"></i><i class="v" style="top:8px"></i><i class="d"></i></div><div class="aHm"></div>
<div class="aTop"><div class="aClock">5:00</div><div class="aLad"></div></div><div class="aBd"></div><div class="aFd"></div>
<div class="aSoak"><i></i></div><div class="aWpn"></div><div class="aCnt"></div><div class="aHint"></div>`;
  const Q=s=>hud.querySelector(s), eCx=Q(".aCx"), eHm=Q(".aHm"), eWet=Q(".aWet"), eDir=Q(".aDir"), eClk=Q(".aClock"), eLad=Q(".aLad"), eBd=Q(".aBd"), eFd=Q(".aFd"), eWpn=Q(".aWpn"), eSoak=Q(".aSoak i"), eCnt=Q(".aCnt"), eDead=Q(".aDead"), eHint=Q(".aHint");
  const root=api.ui, fireB=root.querySelector('[data-b=fire]'), fire2=root.querySelector('[data-b=fire2]');
  function fireIc(){ const W=WP[me.wi]; if(fireB) fireB.firstChild.nodeValue=W.ic; if(fire2) fire2.firstChild.nodeValue=W.ic; eWpn.innerHTML=W.ic+' '+W.nm+' <small>'+(me.wi+1)+'/'+WP.length+(W.t==="snipe"?' · 꾹 눌러 조준 → 떼면 쏘기':W.t==="melee"?' · 가까이 가서!':'')+'</small>'; }
  function drawLadder(){ eLad.innerHTML=WP.map((w,i)=>'<b class="'+(i<me.wi?"d":i===me.wi?"c":"")+'">'+w.ic+'</b>').join(""); }
  function drawFeed(){ eFd.innerHTML=FEED.map(f=>'<div class="'+(f.me?"me":"")+'">'+(f.a?esc(f.a)+' '+f.ic+' ':'💧 ')+esc(f.b)+'</div>').join(""); }
  let bdT=0; function drawBoard(){ const L=ACT.slice().sort((x,y)=>y.wi-x.wi || y.kills-x.kills); const S3=L.slice(0,3); if(S3.indexOf(me)<0) S3.push(me); eBd.innerHTML=S3.map(a=>[a,L.indexOf(a)]).map(([a,i])=>'<div class="'+(a.me?"me":"")+'"><span>'+(i+1)+'. '+esc(a.nm)+'</span><span>'+WP[a.wi].ic+' '+(a.wi+1)+'</span></div>').join(""); }
  const touch=matchMedia("(pointer:coarse)").matches || "ontouchstart" in window;
  if(!touch){ eHint.textContent="화면을 누르면 마우스 잠금 · 클릭 = 쏘기 · WASD 이동 · 스페이스 = 점프 · Shift = 슬라이드 · Esc = 풀기"; setTimeout(()=>{ eHint.style.display="none"; }, 9000); }
  else { eHint.innerHTML="왼쪽 = 움직이기 · 오른쪽 끌기 = 둘러보기 · 💦 누른 채 끌면 조준"; setTimeout(()=>{ eHint.style.display="none"; }, 7000); }
  fireIc(); drawLadder(); drawBoard();

  /* ════ 나 ════ */
  let camY=0, fov=76, zoom=0, paused=false, roll=0, deadCam=0;
  ACT.forEach(spawn); me.prot=0; ACT.forEach(a=>{ if(a.bot) a.prot=0; });
  function myTick(dt){ const I=api.I;
    /* 둘러보기 — 터치는 적 위에서 살짝 느려짐 */
    let sens=I.lock||I.mouse&&!I.touch ? .0023 : .0058; if(zoom>.5) sens*=.4;
    if(I.touch && me.alive){ const e=eyeOf(me), d=dirOf(me.yaw, me.pitch); if(assist(me, e, d, 60, 5)) sens*=.55; }
    me.yaw-=I.lx*sens; me.pitch-=I.ly*sens; me.pitch=Math.max(-1.45, Math.min(1.45, me.pitch)); I.lx=I.ly=0;
    if(!me.alive){ me.resp-=dt; deadCam=Math.min(1, deadCam+dt*2.5); if(me.resp<=0){ spawn(me); deadCam=0; } return; }
    me.prot=Math.max(0, me.prot-dt);
    const f=I.my, r=I.mx, sy=Math.sin(me.yaw), cy=Math.cos(me.yaw); let wx=-sy*f+cy*r, wz=-cy*f-sy*r; const wl=Math.min(1, Math.hypot(wx,wz)); if(wl>0){ wx/=Math.hypot(wx,wz); wz/=Math.hypot(wx,wz); }
    if(I.jumpP) me.jbuf=.14; me.jbuf=Math.max(0, me.jbuf-dt);
    const jump=me.onG && (me.jbuf>0 || I.jump);   /* 점프 꾹 = 땅에 닿자마자 또 (버니합) */
    if(jump) me.jbuf=0;
    if(time.cd>0){ me.v.x=me.v.z=0; } else moveAct(me, wx, wz, wl, jump, !!I.slideP, !!I.slide, dt);
    /* 쏘기 */
    me.cd-=dt; const W=WP[me.wi], e=eyeOf(me), d=dirOf(me.yaw, me.pitch);
    let want=I.fire;
    if(AUTO && I.touch && !want && W.t!=="snipe" && W.t!=="melee"){ const as=assist(me, e, d, W.rng, 2.4); if(as) want=1; }
    if(W.t==="snipe"){ if(I.fire){ me.hold+=dt; zoom=Math.min(1, zoom+dt*5); } else { if(me.hold>.12 && me.cd<=0 && time.cd<=0){ fire(me, e, d, I.touch?(o,dd,rg)=>assist(me,o,dd,rg,1.8):null); } me.hold=0; zoom=Math.max(0, zoom-dt*6); } }
    else if(W.t==="melee"){ if(want && me.cd<=0 && time.cd<=0) fire(me, e, d); }
    else if(want && me.cd<=0 && time.cd<=0){ fire(me, e, d, I.touch?(o,dd,rg)=>assist(me,o,dd,rg,3.4):I.mouse?(o,dd,rg)=>assist(me,o,dd,rg,.9):null); }
    /* 마르기 */
    if(time.t-me.lastHit>3.2) me.soak=Math.max(0, me.soak-34*dt); }
  function botsTick(dt){ for(const a of ACT){ if(!a.bot) continue; if(!a.alive){ a.resp-=dt; a.dead+=dt; if(a.c){ a.c.g.rotation.x=-Math.min(1.4, a.dead*5); a.c.g.position.y=Math.max(-.3, -a.dead*.4); } if(a.bk){ const B=a.bk; B.g.rotation.x=-Math.min(1.5, a.dead*6); B.g.position.y=0; B.armL.rotation.set(-2.6,0,.3); B.armR.rotation.set(-2.6,0,-.3); B.legL.rotation.x=.3; B.legR.rotation.x=-.3; } if(a.dead>1.0) a.G.visible=false; if(a.resp<=0) spawn(a); continue; }
      a.prot=Math.max(0,a.prot-dt); if(time.cd>0){ a.G.position.set(a.p.x,a.p.y,a.p.z); continue; } botTick(a, dt); if(time.t-a.lastHit>3.2) a.soak=Math.max(0, a.soak-30*dt); } }

  /* ════ 판 끝 ════ */
  function win(w){ if(time.over) return; time.over=true; finishMatch(w); }
  function finishMatch(w){ const L=ACT.slice().sort((x,y)=>(y===w)-(x===w) || y.wi-x.wi || y.kills-x.kills), rank=L.indexOf(me)+1, won=L[0]===me;
    api.msg(won?'🏆 우승!':w?'🏁 '+esc(w.nm)+' 우승!':'⏰ 시간 끝!', 1800);
    setTimeout(()=>{ try{ if(document.pointerLockElement) document.exitPointerLock(); }catch(e){}
      api.end({title:won?'🏆 '+esc(me.nm)+' 우승!':rank<=3?'🎉 '+rank+'등!':'💦 '+rank+'등', sub:'흠뻑 적신 수 '+me.kills+' · 단계 '+(me.wi+1)+'/'+WP.length+(won?' · '+Math.round(time.t)+'초':''),
        rows:L.map(a=>[a.nm, WP[a.wi].ic+' '+(a.wi+1)+'단계 · 💦'+a.kills, a.me]), coins:won?15:rank<=3?8:5,
        upd:(b,t)=>{ t.kills=(t.kills|0)+me.kills; if(won){ t.win=(t.win|0)+1; if(!b.fast || time.t<b.fast) b.fast=Math.round(time.t); } if(me.kills>(b.kill|0)) b.kill=me.kills; if(me.wi+1>(b.wi|0)) b.wi=me.wi+1; }}); }, 1700); }

  /* ════ 한 장면 ════ */
  function tick(dt){ if(paused) return; time.t+=dt;
    if(time.cd>0){ const c0=Math.ceil(time.cd); time.cd-=dt; const c1=Math.ceil(time.cd); eCnt.textContent=time.cd>0?c1:"GO!"; if(c1!==c0) api.sfx.tick(); if(time.cd<=0){ api.sfx.up(); setTimeout(()=>{ eCnt.textContent=""; }, 600); } }
    else if(!time.over){ time.left-=dt; if(time.left<=0){ time.left=0; time.over=true; finishMatch(null); } }
    if(!time.over || true){ myTick(dt); botsTick(dt); }
    fxTick(dt);
    for(const f of FEED) f.t-=dt; if(FEED.length && FEED[FEED.length-1].t<=0){ FEED.pop(); drawFeed(); }
    /* 카메라 */
    const eyeH=me.alive?(me.sl?EYES:EYE):.35, ty=me.p.y+eyeH; if(Math.abs(ty-camY)<.7 && me.onG) camY+=(ty-camY)*Math.min(1,dt*16); else camY=ty;
    cam.position.set(me.p.x, camY, me.p.z); const hs=Math.hypot(me.v.x,me.v.z);
    const asp=cam.aspect||1.5, base=asp>=1?76:Math.min(100, 76+(1-asp)*55);   /* 세로 화면(아이패드 세로)은 위아래 시야를 넓혀 옆이 너무 좁지 않게 */
    const tf=(base+Math.max(0,Math.min(12,(hs-MAXS)*1.4)))*(1-zoom*.55); fov+=(tf-fov)*Math.min(1,dt*8); if(Math.abs(cam.fov-fov)>.05){ cam.fov=fov; cam.updateProjectionMatrix(); }
    roll+=((me.sl?-.06:0)-roll)*Math.min(1,dt*8); cam.rotation.set(me.pitch-deadCam*.5, me.yaw, roll+deadCam*.35);
    cam.updateMatrixWorld();
    /* 내 화면 총 흔들림 · 반동 */
    vmA.bob+=dt*(me.onG && hs>1 ? hs*1.05 : 0); vmA.kick=Math.max(0, vmA.kick-dt*7); vmA.sw=Math.min(1, vmA.sw+dt*4); vmA.swing=Math.max(0, vmA.swing-dt*3.2);
    const bx2=Math.sin(vmA.bob)*.012*Math.min(1,hs/6), by2=Math.abs(Math.cos(vmA.bob))*.014*Math.min(1,hs/6);
    VM.position.set(.24+bx2-zoom*.24, -.22-by2-(1-vmA.sw)*.35+(me.onG?0:.015)-(zoom*.05), -.5+vmA.kick*.05); VM.rotation.set(.04+vmA.kick*.12+vmA.swing*1.1-(1-vmA.sw)*.6, .2-vmA.swing*.5, -.06+vmA.swing*.4);
    if(VMG.userData.twin) VMG.userData.twin.position.z=(vmA.side<0?vmA.kick*.06:0); VMG.position.z=vmA.side>0?0:-vmA.kick*.0;
    VM.visible=me.alive && zoom<.9;
    /* 글자 */
    hitT=Math.max(0,hitT-dt); eHm.style.opacity=hitT>0?1:0; eHm.classList.toggle("hd", hitHead);
    hurtT=Math.max(0,hurtT-dt); eDir.style.opacity=hurtT>0?Math.min(1,hurtT*2):0; if(hurtT>0) eDir.style.transform="rotate("+(-(hurtA-me.yaw)+Math.PI)+"rad)";
    eWet.style.opacity=Math.min(1, me.soak/85); eSoak.style.width=Math.min(100,me.soak)+"%"; eDead.style.opacity=me.alive?0:1;
    const W=WP[me.wi], spr=(W.spr||0)+(me.onG?0:1.5)+Math.min(2,hs/6); const g=8+spr*3; eCx.querySelectorAll(".h")[0].style.left=(-10-g)+"px"; eCx.querySelectorAll(".h")[1].style.left=g+"px"; eCx.querySelectorAll(".v")[0].style.top=(-10-g)+"px"; eCx.querySelectorAll(".v")[1].style.top=g+"px"; eCx.style.opacity=zoom>.5?0:1;
    const s=Math.max(0,Math.ceil(time.left)); eClk.textContent=Math.floor(s/60)+":"+String(s%60).padStart(2,"0");
    bdT-=dt; if(bdT<=0){ bdT=.5; drawBoard(); } }
  function render(rn){ MG.draw(scene, cam); const va=cam.aspect||1.5, vf=va>=1.3?58:Math.min(92, 58+(1.3-va)*52); if(vmC.aspect!==va || vmC.fov!==vf){ vmC.aspect=va; vmC.fov=vf; vmC.updateProjectionMatrix(); } rn.autoClear=false; rn.clearDepth(); rn.render(vmS, vmC); rn.autoClear=true; }
  function dispose(){ gone=true; disp.forEach(x=>{ try{ x.dispose(); }catch(e){} }); Object.values(GM).forEach(m=>{ try{ m.dispose(); }catch(e){} }); BAL.forEach(b=>scene.remove(b.m)); }
  return {scene, cam, tick, render, dispose, pause:(v)=>{ paused=!!v; }, vmSet, VM, me, ACT, WP, time, BOX, fire, hurt, spawn, PADS, moveAct, up, win, path, sees, D, vmA, get zoom(){ return zoom; }}; }

MG.reg("arena", {ic:"💦", nm:"물총 아레나", tag:"1인칭 · 아레나 무브 · 무기 8단계", bg:"linear-gradient(135deg,#7fd3ff,#2f7fff)", big:"🔫💦",
  how:[["🎯","한 명을 흠뻑 적실 때마다 <b>다음 무기</b>로 (8단계)"],["🔨","마지막 <b>뿅망치</b>로 맞히면 우승! · 5분이 지나면 가장 멀리 간 사람"],["🛝","달리다 <b>슬라이드</b> → 빨라짐 · 슬라이드 중 점프 = 속도 그대로"],["🐇","땅에 닿는 순간 점프(점프 꾹) = 속도 유지 · 💧 분수 발판 = 높이 점프"],["👐","왼손 = 움직이기 · 오른손 = 끌어서 둘러보기 · 💦 누른 채 끌면 조준"]],
  opts:[{k:"diff", t:"상대(마을 친구 5명) 실력", d:"normal", v:[["easy","🐣 쉬움"],["normal","🙂 보통"],["hard","🔥 어려움"]]},{k:"auto", t:"터치 자동 쏘기 (조준만 하면 쏨)", d:0, v:[[0,"끄기"],[1,"켜기"]]}],
  payTxt:"우승 🪙15 · 3등 안 🪙8 · 참가 🪙5",
  bestTxt:(b,t)=>'🏆 우승 '+(t.win|0)+'번 · 💦 모두 '+(t.kills|0)+'명'+(b.fast?' · 가장 빠른 우승 '+b.fast+'초':'')+(b.wi?' · 최고 '+b.wi+'단계':''),
  ui:{look:true, btns:[{b:"fire", ic:"🔫"}, {b:"jump", ic:"JUMP", cls:"tx"}, {b:"slide", ic:"SLIDE", cls:"tx"}]},
  start});
})();
