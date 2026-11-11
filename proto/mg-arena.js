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
  /* (v599) 사용자: 「설정도 없고 들어가는 방식도 없어서 그냥 인게임으로 가야 하네」 → 아레나 메뉴 화면 · 설정(기기마다 저장) · 시작 연출 */
  const SETK="hyeng_proto_arenaset", SET=Object.assign({sens:3, aim:2, auto:0, fov:1, btn:1, vol:2, diff:"normal", map:"pool"}, (()=>{ try{ return JSON.parse(localStorage.getItem(SETK)||"{}")||{}; }catch(e){ return {}; } })());
  const saveSet=()=>{ try{ localStorage.setItem(SETK, JSON.stringify(SET)); }catch(e){} };
  if(api.opt.diff) SET.diff=api.opt.diff; if(api.opt.map) SET.map=api.opt.map; if(api.opt.auto!=null) SET.auto=+api.opt.auto;
  let D=DIFF[SET.diff]||DIFF.normal, CO=false, phase="menu";   /* menu · room(같이 하기 방) · intro(시작 연출) · play */
  const scene=new THREE.Scene(); scene.background=new THREE.Color(0x9fdcff); scene.fog=new THREE.Fog(0x9fdcff, 45, 95);
  const cam=new THREE.PerspectiveCamera(76, 1, 0.05, 280); cam.rotation.order="YXZ";
  const hemi=new THREE.HemisphereLight(0xfff4e0, 0x5a7ab0, 0.5); scene.add(hemi); scene.add(new THREE.AmbientLight(0xffffff, .08));
  const sunL=new THREE.DirectionalLight(0xfff0d8, .95); sunL.position.set(18,34,12); scene.add(sunL); scene.add(sunL.target);
  if(!api.low){ sunL.castShadow=true; sunL.shadow.mapSize.set(1024,1024); const sc=sunL.shadow.camera; sc.left=sc.bottom=-32; sc.right=sc.top=32; sc.near=1; sc.far=90; sunL.shadow.bias=-0.0012; }
  const toon=m=>{ try{ TOON.mat(m); }catch(e){} return m; };
  const VCM=toon(new THREE.MeshStandardMaterial({vertexColors:true, roughness:.85}));
  const disp=[];   /* 나갈 때 지울 것 */

  /* ════ 경기장 (50×50 · 180° 돌려도 같은 모양 = 공평) — (v599) 사용자: 「맵도 하나잖아」 → 맵 3개 (메뉴에서 고르면 뒤 배경이 바로 바뀜) ════ */
  const BOX=[], PADS=[], SPAWN=[], R=25; let MAPK="pool", MAPG=null;
  const bx=(x0,z0,x1,z1,y1,col,y0)=>{ const b={x0:Math.min(x0,x1), z0:Math.min(z0,z1), x1:Math.max(x0,x1), z1:Math.max(z0,z1), y0:y0||0, y1, col}; BOX.push(b); return b; };
  const sym=(x0,z0,x1,z1,y1,col,y0)=>{ bx(x0,z0,x1,z1,y1,col,y0); bx(-x0,-z0,-x1,-z1,y1,col,y0); };
  const mtx=(x,y,z,rx,ry,rz,sx,sy,sz)=>new THREE.Matrix4().compose(new V3(x,y,z), new THREE.Quaternion().setFromEuler(new THREE.Euler(rx||0,ry||0,rz||0)), new V3(sx||1,sy||1,sz||1));
  function merge(L, mat){ const parts=L.map(e=>{ let g=e.g.index?e.g.toNonIndexed():e.g; if(e.m) g.applyMatrix4(e.m); if(!g.attributes.normal) g.computeVertexNormals(); return [g, new THREE.Color(e.col).convertSRGBToLinear()]; });
    let n=0; parts.forEach(([g])=>n+=g.attributes.position.count); const P=new Float32Array(n*3), N=new Float32Array(n*3), C=new Float32Array(n*3); let o=0;
    parts.forEach(([g,c])=>{ const k=g.attributes.position.count; P.set(g.attributes.position.array.subarray(0,k*3),o*3); N.set(g.attributes.normal.array.subarray(0,k*3),o*3); for(let i=0;i<k;i++){ C[(o+i)*3]=c.r; C[(o+i)*3+1]=c.g; C[(o+i)*3+2]=c.b; } o+=k; g.dispose(); });
    const G=new THREE.BufferGeometry(); G.setAttribute("position",new THREE.BufferAttribute(P,3)); G.setAttribute("normal",new THREE.BufferAttribute(N,3)); G.setAttribute("color",new THREE.BufferAttribute(C,3)); G.computeBoundingSphere();
    const m=new THREE.Mesh(G, mat||VCM); m.castShadow=true; m.receiveShadow=true; return m; }
  const B3=(w,h,d)=>new THREE.BoxGeometry(w,h,d), CY=(r,h,n,r2)=>new THREE.CylinderGeometry(r,r2==null?r:r2,h,n||14), SP=(r,a,b)=>new THREE.SphereGeometry(r,a||14,b||10);
  /* 상자마다 그림 + 큰 벽 위 흰 줄 · 바닥 바둑판 · 둘레 띠 · 분수 발판 */
  function boxMesh(VL, line){ BOX.forEach(b=>{ const w=b.x1-b.x0, h=b.y1-b.y0, d=b.z1-b.z0; VL.push({g:B3(w,h,d), col:b.col, m:mtx((b.x0+b.x1)/2,(b.y0+b.y1)/2,(b.z0+b.z1)/2)});
    if(line!=null && h>2 && w>.5 && d>.5 && b.y0===0 && !b.nl) VL.push({g:B3(w+.04,.14,d+.04), col:line, m:mtx((b.x0+b.x1)/2,b.y1-.3,(b.z0+b.z1)/2)}); }); }
  function floor(VL, c1, c2, N){ const s=50/N; for(let i=0;i<N;i++) for(let j=0;j<N;j++) VL.push({g:new THREE.PlaneGeometry(s,s), col:(i+j)%2?c1:c2, m:mtx(-R+s*(i+.5),0,-R+s*(j+.5),-Math.PI/2)}); }
  function rim(VL, c1, c2){ for(let i=0;i<4;i++){ const a=i*Math.PI/2; VL.push({g:B3(52,.35,.2), col:c1, m:mtx(Math.sin(a)*(R-.08),3.9,Math.cos(a)*(R-.08),0,a,0)}); VL.push({g:B3(52,.25,.2), col:c2, m:mtx(Math.sin(a)*(R-.08),2.2,Math.cos(a)*(R-.08),0,a,0)}); } }
  function pads(VL, GLOW, ring, glow, edge){ PADS.forEach(([x,z])=>{ VL.push({g:CY(1.0,.12,22,1.1), col:ring, m:mtx(x,.06,z)}); GLOW.push({g:CY(.82,.04,22), col:glow, m:mtx(x,.13,z)}); GLOW.push({g:new THREE.TorusGeometry(.95,.05,6,24), col:edge, m:mtx(x,.14,z,Math.PI/2)}); }); }
  const outer=(h,c1,c2)=>{ bx(-R-1,-R-1,R+1,-R,h,c1); bx(-R-1,R,R+1,R+1,h,c1); bx(-R-1,-R,-R,R,h,c2); bx(R,-R,R+1,R,h,c2); BOX.slice(-4).forEach(b=>b.nl=1); };
  const MAPS={
    /* 🏖 워터파크 (처음 맵) */
    pool:{ic:"🏖", nm:"워터파크", sky:0x9fdcff, sea:0x6fc9f0, fog:[45,95], pad:"💧 분수 발판", show:[2,1.6,2.4],
      build(VL, GLOW){ outer(4.6,0x4f9be8,0x5aa7ff);
        bx(-4,-4,4,4,1.6,0xffc23d); for(let k=1;k<=3;k++) sym(-1.7,-4-.7*k,1.7,-4-.7*(k-1),1.6-.4*k,0xffd76a);
        sym(-4,-1.6,-3.55,1.6,2.75,0xd7e3ff,1.6); bx(-.55,-.55,.55,.55,5.4,0xffffff,1.6);
        const wk=(x0,x1,sg)=>{ bx(x0,-9,x1,9,2.4,0x4f9be8).nl=1; for(let k=1;k<=5;k++){ bx(x0,-9-.7*k,x1,-9-.7*(k-1),2.4-.4*k,0x7ab8f5); bx(x0,9+.7*(k-1),x1,9+.7*k,2.4-.4*k,0x7ab8f5); } bx(sg>0?x0:x1-.35, -5, sg>0?x0+.35:x1, 5, 3.35, 0xd7e3ff, 2.4); };
        wk(-21,-17,-1); wk(17,21,1);
        sym(-17,-17,-11,-16.4,2.7,0xff6f91); sym(-17,-16.4,-16.4,-11,2.7,0xff6f91); sym(11,-17,17,-16.4,2.7,0xff6f91); sym(16.4,-16.4,17,-11,2.7,0xff6f91);
        const cr=(x,z,h,c)=>sym(x-.6,z-.6,x+.6,z+.6,h||1.15,{0xff9a3d:0xff8a3d,0x5ee36b:0x45c46a,0xb28dff:0x9b7be8,0xff7aa8:0xff6f91}[c||0xff9a3d]||c);
        cr(-8.5,-11); cr(-7.3,-11,1.15,0x5ee36b); cr(-8.5,-11,2.3,0xff9a3d); cr(-11.5,-4.5,1.15,0xb28dff); cr(-11.5,-3.3,2.3,0xb28dff); cr(-7,7.5,1.15,0x5ee36b); cr(-13,9.5,1.15,0xff9a3d);
        cr(8.5,-11.5,1.15,0x5ee36b); cr(12,-6,2.3,0xff9a3d); cr(12,-4.8,1.15,0xff9a3d); cr(7,12.5,1.15,0xb28dff); cr(-3.5,-20,1.15,0xff9a3d); cr(-2.3,-20,2.3,0xff7aa8); cr(-21.5,-21,1.15,0x5ee36b); cr(-20.3,-21.6,1.15,0xb28dff);
        sym(-2.2,-15.6,2.2,-15,1.0,0xd7e3ff); sym(-14.2,-1,-13.6,3,1.0,0xd7e3ff); sym(5.6,-8,6.2,-5,1.0,0xd7e3ff); sym(-24.9,-17,-23.6,-15.8,1.15,0xff9a3d);
        /* (v597) 파라솔 밑 탁자(부딪힘) · 파라솔 높이 */
        [[-23,-12],[23,12],[-12,23],[12,-23]].forEach(([x,z])=>bx(x-.75,z-.75,x+.75,z+.75,.85,0xfff6e6));
        PADS.push([-13.8,-9.2],[13.8,9.2],[-8.2,15.8],[8.2,-15.8]);
        SPAWN.push([-23,0],[23,0],[0,-23],[0,23],[-22.5,-22.5],[22.5,22.5],[-22.5,22.5],[22.5,-22.5],[-9.5,-8],[9.5,8],[-9,9],[9,-9],[-19,-4],[19,4]);
        boxMesh(VL, 0xffffff); rim(VL, 0xffffff, 0xffd23f); floor(VL, 0x8fd0dc, 0x7cc3d1, 20);
        [[-9,-17.5],[9,17.5]].forEach(([x,z])=>{ VL.push({g:CY(2.3,.2,26), col:0xffffff, m:mtx(x,.1,z)}); VL.push({g:CY(2.05,.06,26), col:0x46b3ff, m:mtx(x,.2,z)});
          VL.push({g:new THREE.TorusGeometry(.55,.22,10,18), col:0xffd23f, m:mtx(x+.6,.3,z-.4,Math.PI/2)}); VL.push({g:SP(.3), col:0xffd23f, m:mtx(x+.6,.62,z-.95)}); VL.push({g:new THREE.ConeGeometry(.1,.2,8), col:0xff9a3d, m:mtx(x+.6,.62,z-1.27,Math.PI/2)}); });
        [[-23,-12],[23,12],[-12,23],[12,-23]].forEach(([x,z],i)=>{ VL.push({g:CY(.06,3.6,8), col:0xffffff, m:mtx(x,1.8,z)}); VL.push({g:new THREE.ConeGeometry(1.7,.7,10), col:[0xff7aa8,0xffd23f,0x5ee36b,0xb28dff][i], m:mtx(x,3.7,z)}); });
        VL.push({g:SP(1.5,20,14), col:0x7fd3ff, m:mtx(0,6.6,0)}); VL.push({g:CY(1.52,.25,20), col:0xffffff, m:mtx(0,6.6,0)}); VL.push({g:new THREE.ConeGeometry(.5,.8,14), col:0x46b3ff, m:mtx(0,8.3,0)});
        pads(VL, GLOW, 0xffffff, 0x7fe0ff, 0x46b3ff); } },
    /* 🏰 모래성 해변 — 가운데 큰 모래성(높이 2.4 · 탑 위 = 점프로) · 동서 계단 · 구조대 망루 2 · 난파선 · 야자수 */
    sand:{ic:"🏰", nm:"모래성 해변", sky:0xaee6ff, sea:0x37c3c9, fog:[48,100], pad:"🐚 물 뿜는 조개", show:[0,0,10.5],
      build(VL, GLOW){ outer(4.2,0xd9b77a,0xe2c084);
        const S1=0xf0d49a, S2=0xe7c27f, S3=0xdcb06c;
        bx(-5,-5,5,5,2.4,S1);
        sym(-5,-5,-3,-3,3.8,S3); sym(3,-5,5,-3,3.8,S3);   /* 모서리 탑 4 (단 위에서 점프하면 올라감) */
        for(let k=1;k<=5;k++) sym(5+.7*(k-1),-1.7,5+.7*k,1.7,2.4-.4*k,S2);   /* 동·서 계단 */
        sym(-3,-5,3,-4.55,3.05,S3,2.4);   /* 북·남 성벽 (단 위 엄폐) */
        /* 구조대 망루 (높이 2.4 · 계단) */
        sym(-21,-21,-16.5,-16.5,2.4,0xff6f61); for(let k=1;k<=5;k++) sym(-16.5+.7*(k-1),-20.2,-16.5+.7*k,-17.3,2.4-.4*k,0xffffff); sym(-21,-21,-20.6,-18,3.2,0xffffff,2.4);
        /* 모래 둑 (낮은 엄폐) · 모래성 작은 것 · 바위 */
        sym(-14,-9.5,-6,-8.9,1.1,S2); sym(-20,2.5,-13.5,3.1,1.1,S2); sym(-9,13,-3,13.6,1.1,S2); sym(11,-1,11.6,6,1.1,S2);
        const cs=(x,z,h)=>sym(x-.8,z-.8,x+.8,z+.8,h||1.3,S3); cs(-10,-3); cs(-15,9,2.2); cs(4,-12); cs(-6,-17,2.2); cs(18,-10); cs(-23,8);
        sym(-24.9,-6,-23.4,-4.5,1.6,0x9aa3ad); sym(-3,-24.9,-1.4,-23.4,1.2,0x9aa3ad);
        /* 난파선 (갑판 1.6 · 뱃머리 높음) */
        sym(8,-22.5,16,-19,1.6,0x9b6b43); sym(16,-22.2,18,-19.3,2.4,0x8a5d38); sym(8,-22.5,16,-22.1,2.3,0x8a5d38,1.6); for(let k=1;k<=3;k++) sym(7.3-.7*(k-1),-21.5,8-.7*(k-1),-20,1.6-.4*k,0xb07d50);
        /* 야자수 줄기 (부딪힘) */
        const PALM=[[-12,-21],[21,-14],[-17,15],[14,23.2],[3,18],[-3,-18]]; PALM.forEach(([x,z])=>bx(x-.25,z-.25,x+.25,z+.25,3.4,0xa0703f));
        PADS.push([-12.5,-14],[12.5,14],[-14,13.5],[14,-13.5]);
        boxMesh(VL, 0xfff3d6); rim(VL, 0xfff3d6, 0x37c3c9); floor(VL, 0xf2d8a0, 0xecce8e, 20);
        /* 성 꼭대기 장식 · 깃발 · 조개 · 야자 잎 · 파라솔 · 비치볼 */
        [[-4,-4],[4,4],[4,-4],[-4,4]].forEach(([x,z],i)=>{ VL.push({g:new THREE.ConeGeometry(1.25,1.2,4), col:S2, m:mtx(x,4.4,z,0,Math.PI/4)}); VL.push({g:CY(.04,1.4,6), col:0xffffff, m:mtx(x,5.5,z)}); VL.push({g:B3(.7,.4,.04), col:[0xff6f61,0x46b3ff,0xffd23f,0x5ee36b][i], m:mtx(x+.36,5.95,z)}); });
        for(let i=-2;i<=2;i++){ VL.push({g:B3(.7,.5,.7), col:S1, m:mtx(i*1.9,3.3,-4.75)}); VL.push({g:B3(.7,.5,.7), col:S1, m:mtx(i*1.9,3.3,4.75)}); }
        PALM.forEach(([x,z],i)=>{ for(let k=0;k<5;k++){ const a=k/5*Math.PI*2+i; VL.push({g:B3(2.6,.08,.7), col:k%2?0x3fae5a:0x56c46d, m:mtx(x+Math.cos(a)*1.1,3.45,z+Math.sin(a)*1.1,0,-a,-.32)}); } VL.push({g:SP(.42), col:0x7a5a2c, m:mtx(x,3.35,z)}); });
        [[-23,-12],[23,12]].forEach(([x,z],i)=>{ VL.push({g:CY(.06,3.2,8), col:0xffffff, m:mtx(x,1.6,z)}); VL.push({g:new THREE.ConeGeometry(1.7,.7,10), col:i?0xff6f61:0x46b3ff, m:mtx(x,3.3,z)}); });
        [[-7,9,0xff6f61],[8,-6,0x46b3ff],[19,8,0xffd23f]].forEach(([x,z,c])=>VL.push({g:SP(.45,12,9), col:c, m:mtx(x,.45,z)}));
        VL.push({g:CY(.09,4.5,8), col:0x8a5d38, m:mtx(12,3.85,-20.7)}); VL.push({g:B3(.05,2.2,2.6), col:0xffffff, m:mtx(12,4.4,-20.7)});
        pads(VL, GLOW, 0xffc2c8, 0x7fe0ff, 0xff8fa3); } },
    /* 🧸 거인 장난감 방 — 내가 장난감만큼 작아짐 · 탁자 아래로 지나가기 · 책 계단으로 탁자 위 · 블록 더미 */
    toy:{ic:"🧸", nm:"거인 장난감 방", sky:0xfde3c0, sea:0xc98d5a, fog:[40,90], pad:"🟢 스프링 단추", show:[0,0,10],
      build(VL, GLOW){ outer(9,0xfff1d6,0xffeacb);
        const WD=0xe0a15e, LG=0xc98a4b;
        bx(-4.3,-4.3,4.3,4.3,2.5,0xf4a259,2.2);   /* 탁자 판 (아래로 지나갈 수 있음) */
        sym(-4.1,-4.1,-3.5,-3.5,2.2,LG); sym(3.5,-4.1,4.1,-3.5,2.2,LG);
        const BK=[0xff6f61,0x46b3ff,0xffd23f,0x5ee36b,0xb28dff];
        for(let k=1;k<=5;k++) sym(-1.6,-4.3-.75*k,1.6,-4.3-.75*(k-1),2.5-.45*k,BK[k-1]);   /* 책 계단 남·북 */
        /* 블록 더미 (큰 2.4 · 작은 1.2 = 점프로 오르기) */
        const blk=(x,z,s,h,c)=>sym(x-s/2,z-s/2,x+s/2,z+s/2,h,c);
        blk(-14,-8,2.4,2.4,0xff6f61); blk(-12.2,-8.6,1.2,1.2,0xffd23f); blk(-14,-5.8,2,1.2,0x46b3ff);
        blk(-9,10,2.4,2.4,0x5ee36b); blk(-10.8,10.6,1.2,1.2,0xff7aa8); blk(-6.6,14,2.4,1.2,0xffd23f);
        blk(-20,-15,2.4,3.6,0xb28dff); blk(-18.2,-15.6,1.2,1.2,0x46b3ff); blk(-20,-12.8,2,2.4,0xff6f61); blk(-20,-11,1.4,1.2,0x5ee36b);
        blk(15,1,2.4,1.2,0xff7aa8); blk(-3,-19,2.4,2.4,0x46b3ff); blk(-1,-19.6,1.2,1.2,0xffd23f);
        /* 크레파스 (낮은 엄폐 · 점프로 넘기) */
        sym(-21,6,-13,6.7,.7,0xff6f61); sym(6,-13.5,6.7,-6,.7,0x46b3ff); sym(-8,-22,-2,-21.3,.7,0x5ee36b);
        /* 곰 인형 (구석 · 앉은 몸 = 엄폐) */
        sym(-23.8,-23.8,-20.6,-20.6,3,0xc08552);
        PADS.push([-11.5,-14.5],[11.5,14.5],[-16,1.5],[16,-1.5]);
        boxMesh(VL, null); floor(VL, 0xe8b27a, 0xdea56c, 10);
        for(let i=0;i<4;i++){ const a=i*Math.PI/2; VL.push({g:B3(52,.7,.25), col:0xffffff, m:mtx(Math.sin(a)*(R-.1),.35,Math.cos(a)*(R-.1),0,a,0)}); }   /* 걸레받이 */
        VL.push({g:CY(8,.04,40), col:0x8fd0ff, m:mtx(0,.02,0)}); VL.push({g:CY(6.4,.05,40), col:0xffffff, m:mtx(0,.03,0)}); VL.push({g:CY(4.8,.06,40), col:0xff9ab0, m:mtx(0,.04,0)});   /* 둥근 깔개 */
        /* 블록 글자 면 · 탁자 위 크레파스 · 곰 머리·귀 · 공 · 연필 */
        [[-14,-8,2.4,"A"],[14,8,2.4,"B"],[-9,10,2.4,"C"],[9,-10,2.4,"D"]].forEach(([x,z,s])=>{ VL.push({g:B3(s*.6,s*.6,.03), col:0xffffff, m:mtx(x,s/2,z+s/2+.02)}); VL.push({g:B3(s*.6,s*.6,.03), col:0xffffff, m:mtx(x,s/2,z-s/2-.02)}); });
        [[-22.2,-22.2],[22.2,22.2]].forEach(([x,z])=>{ const sg=Math.sign(x); VL.push({g:SP(1.5,16,12), col:0xc08552, m:mtx(x,3.9,z)}); VL.push({g:SP(.5), col:0xc08552, m:mtx(x+sg*.9,5.1,z+sg*.2)}); VL.push({g:SP(.5), col:0xc08552, m:mtx(x+sg*.2,5.1,z+sg*.9)}); VL.push({g:SP(.55), col:0xf2d1a8, m:mtx(x-sg*.9,3.7,z-sg*.9)}); VL.push({g:SP(.14), col:0x2a2a2a, m:mtx(x-sg*1.1,4.3,z-sg*.6)}); VL.push({g:SP(.14), col:0x2a2a2a, m:mtx(x-sg*.6,4.3,z-sg*1.1)}); });
        [[10,-18,0xff6f61],[-17,19,0x46b3ff],[20,-3,0xffd23f]].forEach(([x,z,c])=>{ VL.push({g:SP(1.1,16,12), col:c, m:mtx(x,1.1,z)}); });
        [[10,-18],[-17,19],[20,-3]].forEach(([x,z])=>bx(x-.8,z-.8,x+.8,z+.8,1.9,0xffffff));   /* 공 (부딪힘만) */
        pads(VL, GLOW, 0xffffff, 0x7dff8a, 0x2fbf4a); } }};
  const MAPL=["pool","sand","toy"];
  /* ════ (v658) 둘레 풍경 — 벽 너머·머리 위에만 (부딪힘 없음 = 발 닿는 곳에는 안 둠) · 하늘 반구(위는 진하게) · 해 · 구름 ════ */
  function scenery(k, VL, GLOW, SKY){
    const cone=(r,h,n)=>new THREE.ConeGeometry(r,h,n||12);
    const palm=(x,z,h,ry)=>{ VL.push({g:CY(.3,h,8,.48), col:0xa0703f, m:mtx(x,h/2,z,0,0,.05)}); for(let i=0;i<7;i++){ const a=i/7*Math.PI*2+(ry||0); VL.push({g:B3(4.2,.1,1.1), col:i%2?0x3fae5a:0x56c46d, m:mtx(x+Math.cos(a)*1.8,h-.2,z+Math.sin(a)*1.8,0,-a,-.42)}); } VL.push({g:SP(.42,8,6), col:0x7a5a2c, m:mtx(x+.3,h-.35,z+.2)}); VL.push({g:SP(.38,8,6), col:0x7a5a2c, m:mtx(x-.3,h-.4,z-.2)}); };
    const cloud=(x,y,z,sc)=>{ [[0,0,0,1],[1.6,.2,.3,.8],[-1.5,.1,-.2,.75],[.5,.5,-.4,.7],[-.4,.35,.5,.6]].forEach(([a,b,c,r])=>SKY.push({g:SP(2.2*r,10,8), col:0xffffff, m:mtx(x+a*sc,y+b*sc,z+c*sc,0,0,0,sc*1.35,sc*.6,sc)})); };
    const balloon=(x,y,z,c1,c2)=>{ SKY.push({g:SP(3.2,14,12), col:c1, m:mtx(x,y,z,0,0,0,1,1.15,1)}); SKY.push({g:CY(3.22,1.2,14), col:c2, m:mtx(x,y+.4,z)}); SKY.push({g:cone(2.2,2.6,12), col:c1, m:mtx(x,y-3.6,z,Math.PI)}); SKY.push({g:B3(1.1,.9,1.1), col:0x9b6b43, m:mtx(x,y-5.6,z)}); };
    const bunting=(x0,y0,z0,x1,y1,z1,n,sag)=>{ const C=[0xff6f61,0xffd23f,0x5ee36b,0x46b3ff,0xb28dff,0xff7aa8], ry=Math.atan2(x1-x0,z1-z0)+Math.PI/2; for(let i=1;i<n;i++){ const t=i/n, y=y0+(y1-y0)*t-Math.sin(t*Math.PI)*(sag||1.2); const g=cone(.42,.75,3); g.scale(1,1,.12); VL.push({g, col:C[i%C.length], m:mtx(x0+(x1-x0)*t, y-.36, z0+(z1-z0)*t, Math.PI, ry, 0)}); }
      const L=Math.hypot(x1-x0,z1-z0,y1-y0); VL.push({g:B3(.05,.05,L), col:0xffffff, m:mtx((x0+x1)/2,(y0+y1)/2-(sag||1.2)*.62,(z0+z1)/2,-Math.atan2(y1-y0,Math.hypot(x1-x0,z1-z0)),Math.atan2(x1-x0,z1-z0),0)}); };
    const pole=(x,z,h,c)=>{ VL.push({g:CY(.13,h,8), col:0xffffff, m:mtx(x,h/2,z)}); VL.push({g:SP(.32,10,8), col:c||0xffd23f, m:mtx(x,h+.2,z)}); };
    if(k==="pool"){
      /* 물 미끄럼틀 탑 2 (빙글빙글 통) */
      [[-37,-13,0xffd23f,0x46b3ff,1],[37,13,0xff7aa8,0x5ee36b,-1]].forEach(([x,z,c1,c2,sg])=>{ for(let i=0;i<7;i++) VL.push({g:CY(2,2.6,14), col:i%2?0xffffff:0x5aa7ff, m:mtx(x,1.3+i*2.6,z)});
        VL.push({g:CY(3.6,.5,16), col:0xffffff, m:mtx(x,18.4,z)}); VL.push({g:cone(4.2,3,8), col:0xff6f61, m:mtx(x,21.6,z)}); VL.push({g:CY(.1,2,6), col:0xffffff, m:mtx(x,24,z)}); VL.push({g:B3(1.3,.8,.06), col:0xffd23f, m:mtx(x+.7,24.5,z)});
        [[c1,0],[c2,Math.PI]].forEach(([c,ph])=>{ const P=[]; for(let i=0;i<=40;i++){ const t=i/40, a=ph+sg*t*Math.PI*5; P.push(new V3(x+Math.cos(a)*(4.4+t*2.4), 17.5-t*15.5, z+Math.sin(a)*(4.4+t*2.4))); } VL.push({g:new THREE.TubeGeometry(new THREE.CatmullRomCurve3(P), 70, 1.05, 8, false), col:c}); }); });
      /* 큰 관람차 */
      { const cx=0, cy=14.5, cz=-47, Rw=11; VL.push({g:new THREE.TorusGeometry(Rw,.3,8,40), col:0xffffff, m:mtx(cx,cy,cz)}); VL.push({g:new THREE.TorusGeometry(Rw*.55,.2,8,30), col:0xffd23f, m:mtx(cx,cy,cz)}); VL.push({g:CY(1.1,1.4,14), col:0xff6f61, m:mtx(cx,cy,cz,Math.PI/2)});
        for(let i=0;i<10;i++){ const a=i/10*Math.PI*2; VL.push({g:B3(.16,Rw,.16), col:0xd7e3ff, m:mtx(cx+Math.sin(a)*Rw/2,cy+Math.cos(a)*Rw/2,cz,0,0,-a)}); VL.push({g:B3(1.9,1.6,1.6), col:[0xff6f61,0xffd23f,0x5ee36b,0x46b3ff,0xb28dff][i%5], m:mtx(cx+Math.sin(a)*Rw,cy+Math.cos(a)*Rw-1,cz)}); VL.push({g:cone(1.4,.8,4), col:0xffffff, m:mtx(cx+Math.sin(a)*Rw,cy+Math.cos(a)*Rw+.2,cz,0,Math.PI/4)}); }
        [-1,1].forEach(sx=>VL.push({g:B3(.5,cy+1,.5), col:0x7ab8f5, m:mtx(cx+sx*4.4,cy/2-.2,cz,0,0,sx*.3)})); }
      /* 큰 고무 오리 · 튜브 */
      { const x=40, z=-14; VL.push({g:SP(5,18,14), col:0xffd23f, m:mtx(x,4,z,0,0,0,1.15,.85,1)}); VL.push({g:SP(3,16,12), col:0xffd23f, m:mtx(x-2.6,9.4,z)}); VL.push({g:cone(1,1.8,10), col:0xff9a3d, m:mtx(x-5.6,9,z,0,0,Math.PI/2,1,1,1.5)}); VL.push({g:SP(.42,8,6), col:0x2a2a2a, m:mtx(x-4.6,10.4,z+1.5)}); VL.push({g:SP(.42,8,6), col:0x2a2a2a, m:mtx(x-4.6,10.4,z-1.5)}); VL.push({g:cone(2.2,3.4,8), col:0xffc23d, m:mtx(x+5.2,5.2,z,0,0,-1.1,1,1,.5)}); }
      [[-41,22,0xff7aa8],[30,40,0x5ee36b],[-28,-41,0xb28dff]].forEach(([x,z,c])=>{ VL.push({g:new THREE.TorusGeometry(3.2,1.3,10,22), col:c, m:mtx(x,.2,z,Math.PI/2)}); VL.push({g:new THREE.TorusGeometry(3.2,1.32,6,6,.5), col:0xffffff, m:mtx(x,.22,z,Math.PI/2)}); });
      for(let i=0;i<14;i++){ const a=i/14*Math.PI*2+.22, r=31+(i%3)*2.5; if(Math.abs(Math.cos(a)*r)>30 || Math.abs(Math.sin(a)*r)>30) palm(Math.cos(a)*r, Math.sin(a)*r, 9+(i%4)*1.2, i); }
      [[-1,-1],[1,-1],[-1,1],[1,1]].forEach(([a,b])=>{ pole(a*25.5,b*25.5,9.2,0xff6f61); bunting(a*25.5,9,b*25.5, 0,9.3,0, 22, 1.6); });
      VL.push({g:CY(.1,1.6,6), col:0xffffff, m:mtx(0,9.2,0)});
      balloon(-58,30,-30,0xff6f61,0xffffff); balloon(52,36,-52,0x46b3ff,0xffd23f); balloon(20,42,64,0xb28dff,0xffffff); }
    else if(k==="sand"){
      /* 등대 · 돛단배 · 섬 */
      { const x=-40, z=18; for(let i=0;i<8;i++) VL.push({g:CY(2.6-i*.12,2.8,14,2.72-i*.12), col:i%2?0xffffff:0xff6f61, m:mtx(x,1.4+i*2.8,z)}); VL.push({g:CY(3.1,.4,14), col:0x4a5568, m:mtx(x,22.6,z)}); GLOW.push({g:CY(1.7,2.2,12), col:0xfff2a8, m:mtx(x,23.9,z)}); VL.push({g:cone(2.5,2.2,12), col:0xff6f61, m:mtx(x,26.1,z)}); VL.push({g:SP(5.5,12,8), col:0x9aa3ad, m:mtx(x,-1.2,z,0,0,0,1.4,.5,1.2)}); }
      [[44,-20,0xff6f61,.4],[-30,-46,0x46b3ff,2.2],[18,48,0xffd23f,-1],[52,30,0xffffff,1.2]].forEach(([x,z,c,ry])=>{ VL.push({g:B3(7,1.6,2.6), col:0x9b6b43, m:mtx(x,.3,z,0,ry,0)}); VL.push({g:CY(.14,9,6), col:0x8a5d38, m:mtx(x,5,z)}); const g=cone(3.4,7.5,3); g.scale(1,1,.08); VL.push({g, col:c, m:mtx(x+Math.cos(ry)*1.4,5.6,z-Math.sin(ry)*1.4,0,ry,0)}); const g2=cone(2.2,5,3); g2.scale(1,1,.08); VL.push({g:g2, col:0xffffff, m:mtx(x-Math.cos(ry)*1.8,4.6,z+Math.sin(ry)*1.8,0,ry,0)}); });
      [[-46,-18],[36,-40]].forEach(([x,z],i)=>{ VL.push({g:SP(7,12,8), col:0xf0d49a, m:mtx(x,-1.5,z,0,0,0,1.5,.45,1.2)}); palm(x-1,z,8,i); palm(x+2.5,z+1.5,6.5,i+2); });
      for(let i=0;i<12;i++){ const a=i/12*Math.PI*2+.4, r=31+(i%3)*2; if(Math.abs(Math.cos(a)*r)>29.5 || Math.abs(Math.sin(a)*r)>29.5) palm(Math.cos(a)*r, Math.sin(a)*r, 8.5+(i%4)*1.3, i); }
      [[-1,-1],[1,-1],[-1,1],[1,1]].forEach(([a,b])=>{ pole(a*25.5,b*25.5,8.6,0x37c3c9); }); bunting(-25.5,8.4,-25.5, 25.5,8.4,-25.5, 34, 2.2); bunting(-25.5,8.4,25.5, 25.5,8.4,25.5, 34, 2.2); bunting(-25.5,8.4,-25.5, -25.5,8.4,25.5, 34, 2.2); bunting(25.5,8.4,-25.5, 25.5,8.4,25.5, 34, 2.2);
      for(let i=0;i<7;i++){ const a=i*1.7, r=38+i*5, y=20+(i%3)*5; SKY.push({g:B3(1.5,.1,.34), col:0xffffff, m:mtx(Math.cos(a)*r-.62,y,Math.sin(a)*r,0,a,.38)}); SKY.push({g:B3(1.5,.1,.34), col:0xffffff, m:mtx(Math.cos(a)*r+.62,y,Math.sin(a)*r,0,a,-.38)}); }
      balloon(60,34,10,0xffd23f,0xff6f61); }
    else if(k==="toy"){
      /* 방: 벽 위쪽(벽지 · 띠) · 창문 · 선반 위 장난감 · 액자 · 매단 등 */
      const WP1=0xffe2bf, WP2=0xffd3a8;
      for(let i=0;i<4;i++){ const a=i*Math.PI/2, sx=Math.sin(a), cz=Math.cos(a); VL.push({g:B3(54,13,.4), col:WP1, m:mtx(sx*26.4,15.5,cz*26.4,0,a,0)}); VL.push({g:B3(54,.5,.5), col:0xffffff, m:mtx(sx*26.2,9.3,cz*26.2,0,a,0)}); for(let j=-6;j<=6;j++) VL.push({g:B3(1.1,12.2,.05), col:WP2, m:mtx(sx*26.15+cz*j*4,15.6,cz*26.15-sx*j*4,0,a,0)}); }
      { const z=-26.1; VL.push({g:B3(15,8,.3), col:0xffffff, m:mtx(0,15,z)}); GLOW.push({g:B3(13.8,6.8,.1), col:0xaee6ff, m:mtx(0,15,z+.2)}); VL.push({g:B3(.35,6.8,.2), col:0xffffff, m:mtx(0,15,z+.28)}); VL.push({g:B3(13.8,.35,.2), col:0xffffff, m:mtx(0,15,z+.28)});
        GLOW.push({g:SP(1.3,12,8), col:0xffffff, m:mtx(-3.6,16.6,z+.24,0,0,0,1.5,.6,.1)}); GLOW.push({g:SP(1,12,8), col:0xffffff, m:mtx(3.2,14.2,z+.24,0,0,0,1.6,.6,.1)}); GLOW.push({g:CY(1,.06,20), col:0xfff2a8, m:mtx(4.6,17.2,z+.24,Math.PI/2)});
        [-1,1].forEach(sx=>VL.push({g:B3(2.6,9,.3), col:0xff8fa3, m:mtx(sx*8.7,15,z+.3)})); VL.push({g:B3(21,.7,.5), col:0xff6f61, m:mtx(0,19.7,z+.35)}); }
      { const x=26; VL.push({g:B3(.9,.4,22), col:0xe0a15e, m:mtx(x-.9,12.6,0)}); [-9,9].forEach(z=>VL.push({g:B3(.7,1.6,.4), col:0xc98a4b, m:mtx(x-.7,11.8,z)}));
        VL.push({g:CY(1.1,4.6,12), col:0xffffff, m:mtx(x-1.4,15.3,-7)}); VL.push({g:cone(1.1,2,12), col:0xff6f61, m:mtx(x-1.4,18.6,-7)}); VL.push({g:SP(.42,8,6), col:0x46b3ff, m:mtx(x-2.4,16.2,-7)}); [0,2.1,4.2].forEach(a=>VL.push({g:B3(.12,1.6,1.2), col:0xff6f61, m:mtx(x-1.4+Math.cos(a)*1.3,13.6,-7+Math.sin(a)*1.3,0,-a,0)}));
        [[2.2,0xff6f61],[1.85,0xffd23f],[1.5,0x5ee36b],[1.15,0x46b3ff],[.8,0xb28dff]].forEach(([r,c],i)=>VL.push({g:new THREE.TorusGeometry(r,.5,8,20), col:c, m:mtx(x-2.4,13.3+i*.95,0,Math.PI/2)}));
        VL.push({g:B3(2.2,2.6,2), col:0x9aa3ad, m:mtx(x-1.5,14.1,7)}); VL.push({g:B3(1.6,1.4,1.5), col:0xd7e3ff, m:mtx(x-1.5,16.1,7)}); GLOW.push({g:SP(.22,8,6), col:0xffd23f, m:mtx(x-2.3,16.3,6.6)}); GLOW.push({g:SP(.22,8,6), col:0xffd23f, m:mtx(x-2.3,16.3,7.4)}); VL.push({g:CY(.06,.8,6), col:0x4a5568, m:mtx(x-1.5,17.2,7)}); GLOW.push({g:SP(.2,8,6), col:0xff6f61, m:mtx(x-1.5,17.7,7)}); [-1,1].forEach(sz=>VL.push({g:B3(.6,1.8,.6), col:0x9aa3ad, m:mtx(x-1.5,14.2,7+sz*1.45)})); }
      [[-26.1,-9,0x7fd3ff],[-26.1,8,0xffd23f]].forEach(([x,z,c],i)=>{ VL.push({g:B3(.3,5.4,6.6), col:0xc98a4b, m:mtx(x,14.5,z)}); GLOW.push({g:B3(.1,4.4,5.6), col:c, m:mtx(x+.2,14.5,z)}); GLOW.push({g:i?SP(1.2,12,8):cone(1.6,2.4,3), col:i?0xff6f61:0x5ee36b, m:mtx(x+.26,14.2,z,0,0,0,.1,1,1)}); });
      { const z=26.1; "ABC".split("").forEach((_,i)=>{ VL.push({g:B3(4,4,.4), col:[0xff6f61,0x46b3ff,0x5ee36b][i], m:mtx(-7+i*7,14+((i%2)?.8:0),z,0,0,(i-1)*.08)}); VL.push({g:B3(2.6,2.6,.1), col:0xffffff, m:mtx(-7+i*7,14+((i%2)?.8:0),z-.24,0,0,(i-1)*.08)}); }); }
      VL.push({g:CY(.06,9,6), col:0x4a5568, m:mtx(0,19.5,0)}); VL.push({g:cone(2.6,2,16), col:0xff8fa3, m:mtx(0,14.6,0)}); GLOW.push({g:SP(.9,12,8), col:0xfff2a8, m:mtx(0,13.5,0)});
      bunting(-25.6,11,-25.6, 25.6,11,25.6, 44, 2.6); bunting(25.6,11,-25.6, -25.6,11,25.6, 44, 2.6); }
    if(k!=="toy"){ const sa=k==="pool"?.9:2.3, sx=Math.cos(sa)*100, sz=Math.sin(sa)*100; SKY.push({g:SP(7,16,12), col:0xfff6c8, m:mtx(sx,62,sz)}); SKY.push({g:SP(10.5,16,12), col:k==="pool"?0xdff3ff:0xe6f8ff, m:mtx(sx*1.02,62.5,sz*1.02)});
      for(let i=0;i<11;i++){ const a=i/11*Math.PI*2+i*.37, r=62+(i%4)*14; cloud(Math.cos(a)*r, 24+(i%5)*6, Math.sin(a)*r, 1.4+(i%3)*.7); } } }
  const SKYM=new THREE.MeshBasicMaterial({vertexColors:true, fog:false}); disp.push(SKYM);
  function skyDome(M, k){ const g=new THREE.SphereGeometry(150, 24, 14), P=g.attributes.position, C=new Float32Array(P.count*3), top=new THREE.Color(M.sky), hor=new THREE.Color(M.sky), c=new THREE.Color();
    if(k==="toy"){ top.setHex(0xfff0dc); hor.setHex(0xfde3c0); } else { top.offsetHSL(-.02,.12,-.2); hor.lerp(new THREE.Color(0xffffff), .5); }
    top.convertSRGBToLinear(); hor.convertSRGBToLinear();
    for(let i=0;i<P.count;i++){ const t=Math.max(0, Math.min(1, P.getY(i)/150*1.5+.08)); c.copy(hor).lerp(top, Math.pow(t,.7)); C[i*3]=c.r; C[i*3+1]=c.g; C[i*3+2]=c.b; }
    g.setAttribute("color", new THREE.BufferAttribute(C,3)); const m=new THREE.Mesh(g, new THREE.MeshBasicMaterial({vertexColors:true, side:THREE.BackSide, fog:false, depthWrite:false})); m.renderOrder=-10; m.frustumCulled=false; return m; }
  function buildMap(k){ if(!MAPS[k]) k="pool"; MAPK=k; const M=MAPS[k]; BOX.length=0; PADS.length=0; SPAWN.length=0;
    if(MAPG){ scene.remove(MAPG); MAPG.traverse(o=>{ if(o.geometry) o.geometry.dispose(); }); }
    MAPG=new THREE.Group(); scene.add(MAPG); const VL=[], GLOW=[], SKY=[], DEC=[]; M.build(VL, GLOW);
    try{ scenery(k, DEC, GLOW, SKY); }catch(e){ console.warn("scenery", e); }
    MAPG.add(merge(VL)); if(DEC.length){ const dm=merge(DEC); dm.castShadow=false; dm.receiveShadow=false; MAPG.add(dm); } if(GLOW.length){ const gm=merge(GLOW, GMB); gm.castShadow=false; MAPG.add(gm); }
    if(SKY.length){ const sm=merge(SKY, SKYM); sm.castShadow=false; sm.receiveShadow=false; sm.frustumCulled=false; MAPG.add(sm); MAPG.userData.sky=sm; }
    { const dome=skyDome(M, k); MAPG.add(dome); disp.push(dome.material); }
    const sea=new THREE.Mesh(new THREE.PlaneGeometry(400,400), new THREE.MeshBasicMaterial({color:M.sea})); sea.rotation.x=-Math.PI/2; sea.position.y=-.6; MAPG.add(sea); disp.push(sea.material);
    scene.background=new THREE.Color(M.sky); scene.fog=new THREE.Fog(M.sky, M.fog[0], M.fog[1]); }
  const GMB=new THREE.MeshBasicMaterial({vertexColors:true}); disp.push(GMB);
  buildMap(SET.map);

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
    if(c){ c.t=0; c.blinkT=2; c.act='idle'; c.g.scale.setScalar(AVK); G.add(c.g); a.c=c; c.g.traverse(m=>{ if(m.isMesh){ m.castShadow=!api.low; } }); }
    else { const m=new THREE.Mesh(new THREE.CapsuleGeometry ? new THREE.CylinderGeometry(.35,.35,1.7,10) : new THREE.CylinderGeometry(.35,.35,1.7,10), toon(new THREE.MeshStandardMaterial({color:0xff9a3d}))); m.position.y=.85; G.add(m); }
    a.gun=new THREE.Group(); if(c && c.armR){ c.armR.add(a.gun); a.gun.position.set(0,-.2,0); a.gun.scale.setScalar(.7); }
    a.tag=nameTag(b.nm); a.tag.position.y=2.15; G.add(a.tag);
    const bub=new THREE.Mesh(new THREE.SphereGeometry(1.15,16,12), new THREE.MeshBasicMaterial({color:0x9fe8ff, transparent:true, opacity:.25, depthWrite:false})); bub.position.y=.95; G.add(bub); a.bub=bub;
    a.brain={tg:null, see:false, seeT:0, react:0, path:[], pathT:0, goal:null, str:1, strT:0, stuckT:0, lastP:new V3(), aimY:0, aimP:0, ex:0, ey:0, eT:0, think:Math.random()*.2, roam:null};
    gunModel(a.gun, 0, true); });
  const BOTL=ACT.filter(a=>a.bot); BOTL.forEach(a=>{ a.G.visible=false; }); ACT.length=0; ACT.push(me);   /* 메뉴에선 나만 · 혼자 = 봇 5 · 같이 = 빈자리만큼 */
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
    armR.add(a.gun); a.gun.position.set(-.2,-1.02,-.24); a.gun.scale.setScalar(1.75);   /* (v593) 사용자: 「총이 손에 파묻혀」 → 손 아래·앞으로 · 더 크게 */ a.hb=HB_BK; }
  let gone=false;
  try{ fetch("../assets/mg/blocky/blocky.json").then(r=>r.json()).then(J=>{ if(gone) return; BOTL.forEach(a=>{ const k=BKS[a.i%BKS.length]; blockify(a, J[k], k); }); }).catch(e=>console.warn("blocky", e)); }catch(e){}
  try{ KK.load("blaster").then(()=>{ if(gone) return; vmSet(me.wi); ACT.forEach(a=>{ if(a.bot || a.net) gunModel(a.gun, a.wi, true); }); }); }catch(e){}
  vmSet(0); VM.position.set(.24,-.22,-.5); const vmA={kick:0, sw:1, bob:0, swing:0, side:1};

  /* ════ 물줄기 · 물보라 (작은 공 여러 개를 한 번에) ════ */
  const DROP=new THREE.InstancedMesh(new THREE.SphereGeometry(.06,6,4), new THREE.MeshBasicMaterial({color:0x8fe3ff, transparent:true, opacity:.9}), 900); DROP.frustumCulled=false; DROP.count=0; scene.add(DROP); disp.push(DROP.geometry);
  const SPL=new THREE.InstancedMesh(new THREE.SphereGeometry(.07,6,4), new THREE.MeshBasicMaterial({color:0xc8f3ff, transparent:true, opacity:.85}), 500); SPL.frustumCulled=false; SPL.count=0; scene.add(SPL); disp.push(SPL.geometry);
  const STR=[], PAR=[], BAL=[]; const _m=new THREE.Matrix4(), _q=new THREE.Quaternion(), _s=new V3(), _v=new V3(), _w=new V3();
  function stream(a, b, w, big, mine){ const L=a.distanceTo(b); STR.push({a:a.clone(), b:b.clone(), L, t:0, sp:big?52:78, w:w||1, big, mine}); }
  function burst(p, n, k){ for(let i=0;i<n && PAR.length<480;i++){ const th=Math.random()*Math.PI*2, ph=Math.random()*1.2; PAR.push({p:p.clone(), v:new V3(Math.cos(th)*Math.sin(ph)*(2+Math.random()*3)*(k||1), (1.5+Math.random()*3.5)*(k||1), Math.sin(th)*Math.sin(ph)*(2+Math.random()*3)*(k||1)), t:0, L:.35+Math.random()*.35, s:.6+Math.random()*.9}); } }
  const BALG=new THREE.SphereGeometry(.2,14,10); disp.push(BALG);
  function fxTick(dt){ let n=0;
    for(let i=STR.length-1;i>=0;i--){ const s=STR[i]; s.t+=dt; const hd=Math.min(s.L, s.t*s.sp), tl=Math.max(0, hd-(s.big?3.2:2.2));
      if(tl>=s.L-1e-3){ STR.splice(i,1); continue; } const k=s.big?9:6;
      for(let j=0;j<k && n<900;j++){ const f=tl+(hd-tl)*(j/(k-1)); _v.copy(s.a).lerp(s.b, s.L>0?f/s.L:1); const sc=(s.big?2.2:1.15)*s.w*(.55+.45*j/(k-1)); if(!s.mine && _v.distanceToSquared(cam.position)<2.6) continue; _s.set(sc,sc,sc); _m.compose(_v,_q,_s); DROP.setMatrixAt(n++, _m); } }   /* (v597) 버그: 남이 나를 맞힌 물줄기가 카메라 앞에서 커다란 덩어리 → 가까운 것은 안 그림 */
    DROP.count=n; DROP.instanceMatrix.needsUpdate=true; n=0;
    for(let i=PAR.length-1;i>=0;i--){ const p=PAR[i]; p.t+=dt; if(p.t>p.L){ PAR.splice(i,1); continue; } p.v.y-=14*dt; p.p.addScaledVector(p.v, dt); if(p.p.y<.02){ p.p.y=.02; p.v.y*=-.2; p.v.x*=.6; p.v.z*=.6; } const sc=p.s*(1-p.t/p.L*.6); if(p.p.distanceToSquared(cam.position)<1.7) continue; _s.set(sc,sc,sc); _m.compose(p.p,_q,_s); if(n<500) SPL.setMatrixAt(n++, _m); }
    SPL.count=n; SPL.instanceMatrix.needsUpdate=true;
    for(let i=BAL.length-1;i>=0;i--){ const b=BAL[i]; b.t+=dt; b.v.y-=13*dt; const o=b.m.position.clone(); b.m.position.addScaledVector(b.v, dt); b.m.rotation.x+=dt*6; const d=b.m.position.clone().sub(o), L=d.length(); let hit=null;
      if(L>0){ d.divideScalar(L); const r=rayBox(o, d, L); if(r.t<L) hit=o.addScaledVector(d, r.t); }
      if(!hit) for(const a of ACT){ if(a===b.by || !a.alive) continue; if(b.m.position.distanceTo(_w.set(a.p.x, a.p.y+.85*(a.h/HH), a.p.z))<.75){ hit=b.m.position.clone(); break; } }
      if(!hit && b.t>4) hit=b.m.position.clone();
      if(hit){ scene.remove(b.m); BAL.splice(i,1); pop(hit, b.by); } } }
  function pop(p, by){ burst(p, 30, 1.5); try{ api.sfx.splash(); }catch(e){}
    for(const a of ACT){ if(!a.alive) continue; const c=_w.set(a.p.x, a.p.y+.85*(a.h/HH), a.p.z), d=c.distanceTo(p); if(d<2.9){ const dm=WP[5].dmg*(1-Math.min(1,d/2.9)*.65); if(a!==by) hurt(a, dm, by, 5, false, p); } } }

  /* ════ 쏘기 ════ */
  const time={t:0, left:MATCH, cd:1e9, over:false};
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
  function fire(a, o, d, hint){ const W=WP[a.wi]; a.cd=W.rate*(a.bot?D.fire:1); a.prot=0; a.fc=(a.fc|0)+1;
    const mz=muzzle(a); let snd=a.me || o.distanceTo(me.p)<22;
    if(W.t==="melee"){ let best=null, bd=W.rng; for(const t of ACT){ if(t===a || !t.alive) continue; const c=new V3(t.p.x, t.p.y+.8, t.p.z), v=c.clone().sub(o), L=v.length(); if(L>bd+.5) continue; v.y*=.4; if(v.normalize().dot(d)<Math.cos(42*D2R)) continue; if(!sees(o,c)) continue; bd=L; best=t; }
      if(a.me){ vmA.swing=1; me.v.addScaledVector(new V3(d.x,0,d.z).normalize(), 3.2); } if(snd) api.sfx.shot("hammer", !a.me);
      if(best){ burst(new V3(best.p.x,best.p.y+1.1,best.p.z), 16); hurt(best, W.dmg, a, a.wi, false, o); } return; }
    if(W.t==="proj"){ const m=new THREE.Mesh(BALG, gmat(Math.random()<.5?0xff7aa8:0x46b3ff)); m.position.copy(a.me?mz:o.clone().addScaledVector(d,.7)); scene.add(m); BAL.push({m, v:d.clone().multiplyScalar(21).add(new V3(0,3.2,0)), by:a, t:0}); if(snd) api.sfx.shot("balloon", !a.me); if(a.me) vmA.kick=1; return; }
    const n=W.n||1, sp=a.me?(W.t==="snipe" && (Math.hypot(me.v.x,me.v.z)>2 || !me.onG) ? 2.2 : W.spr):W.spr; let hitAny=false, hd=false;
    for(let i=0;i<n;i++){ let dd=spread(d, sp); let r=trace(a, o, dd, W.rng);
      if(!r.who && hint && i===0){ const as=hint(o, dd, W.rng); if(as){ dd=as.c.clone().sub(o).normalize(); r={t:as.L, who:as.a, head:false}; } }
      const end=o.clone().addScaledVector(dd, Math.min(r.t, W.rng)); stream(mz, end, W.t==="beam"?1.6:W.t==="snipe"?.8:1, W.t==="beam", !!a.me);
      if(r.who){ let dm=W.dmg; if(W.k==="shot"){ const L=r.t; dm*=L<9?1:Math.max(.35,1-(L-9)/15); } if(r.head && W.t!=="beam") dm*=1.5; hurt(r.who, dm, a, a.wi, r.head, o); hitAny=true; hd=hd||r.head;
        if(W.t==="beam"){ const pu=new V3(dd.x,0,dd.z).normalize().multiplyScalar(5.5*Math.max(.3,1-r.t/16)); r.who.v.x+=pu.x*.35; r.who.v.z+=pu.z*.35; } burst(end, W.t==="beam"?2:4, .6); }
      else if(r.t<W.rng){ if(Math.random()<(W.t==="beam"?.3:1)) burst(end, W.n?2:5, .7); } }
    if(snd) api.sfx.shot(W.k, !a.me); if(a.me){ vmA.kick=W.t==="snipe"?1.6:W.t==="beam"?.25:W.k==="shot"?1.3:.7; vmA.side=-vmA.side; } }

  /* ════ 맞음 · 흠뻑 · 단계 오르기 ════ */
  const FEED=[]; let hitT=0, hitHead=false, hurtT=0, hurtA=0, streak=0, killT=0;
  function dmgFx(t, dm, head){ try{ if(hud.querySelectorAll(".aDmg").length>7) return; const v=new V3(t.p.x+(Math.random()-.5)*.5, t.p.y+1.8, t.p.z+(Math.random()-.5)*.5).project(cam); if(v.z>1 || Math.abs(v.x)>1.1) return; const el=document.createElement("div"); el.className="aDmg"+(head?" hd":""); el.textContent=Math.max(1,Math.round(dm));
      el.style.left=((v.x+1)/2*root.clientWidth)+"px"; el.style.top=((1-v.y)/2*root.clientHeight)+"px"; hud.appendChild(el); setTimeout(()=>el.remove(), 660); }catch(e){} }
  const STK=["","","연속 2명! 🔥","연속 3명! 🔥🔥","멈출 수 없어! 🔥🔥🔥"];
  function killFx(nm){ streak++; killT=1.7; eKill.innerHTML="💦 흠뻑! "+esc(nm||"")+(streak>=2?'<small>'+STK[Math.min(4,streak)]+'</small>':''); eKill.classList.remove("pop","y"); void eKill.offsetWidth; eKill.classList.add("on","pop"); if(streak>=2) eKill.classList.add("y"); try{ api.sfx.win && streak>=3 && api.sfx.clear(); }catch(e){} }
  function hurt(t, dm, by, wi, head, from, raw){ if(!t.alive || (t.prot>0 && !t.net && !t.rb) || time.over) return;   /* 친구·방장 봇은 그쪽 화면이 보호시간을 셈 */ if(by && by.bot && !raw) dm*=t.bot?D.bvb:D.dm;
    /* 같이 하기: 맞은 사람(친구 = 그 기기 · 봇 = 방장)이 젖음을 셈 → 사건으로 보냄 */
    if(CO && NETR && (t.net || (t.bot && t.rb))){ if(by && by.me){ hitT=.18; hitHead=head; api.sfx.hit(head); dmgFx(t, dm, head); }
      if(by && (by.me || (by.bot && !by.rb))){ const o={k:t.net?"hit":"hitb", i:t.i, dm:+dm.toFixed(1), wi, hd:head?1:0, by:idOf(by), fx:from?+from.x.toFixed(1):0, fz:from?+from.z.toFixed(1):0}; NETR.ev(t.net?t.code:hostCode(), o); }
      return; }
    t.soak+=dm; t.lastHit=time.t; t.by=by; t.dmgBy.set(by, (t.dmgBy.get(by)||0)+dm);
    if(by && by.me){ hitT=.18; hitHead=head; api.sfx.hit(head); dmgFx(t, dm, head); }
    if(t.me){ hurtT=.7; if(from){ const v=new V3().subVectors(from, me.p); hurtA=Math.atan2(v.x, v.z); } api.sfx.hurt(); }
    if(t.bot && by && !t.brain.tg){ t.brain.tg=by; t.brain.react=D.react*.6; }
    if(t.soak>=100) soaked(t, by, wi); }
  function feedAdd(a, b, ic, mine){ FEED.unshift({a, b, ic, me:mine, t:5}); if(FEED.length>4) FEED.length=4; drawFeed(); }
  function soaked(t, by, wi){ t.alive=false; t.deaths=(t.deaths|0)+1; t.soak=100; t.resp=RESP; t.dead=0; t.sl=false; t.h=HH; burst(new V3(t.p.x,t.p.y+1,t.p.z), 34, 1.4); api.sfx.soak();
    feedAdd(by?by.nm:"", t.nm, by?WP[wi].ic:"💧", (by&&by.me)||t.me); if(CO && NETR) NETR.feed({a:by?by.nm:"", b:t.nm, ic:by?WP[wi].ic:"💧"});
    if(CO && by && by!==t && (by.net || by.rb)){ NETR.ev(by.net?by.code:hostCode(), by.net?{k:"kill", wi, vic:t.nm}:{k:"bkill", i:by.i, wi, vic:t.nm}); t.dmgBy.clear();
      if(t.me){ streak=0; eSplat.classList.remove("on"); void eSplat.offsetWidth; eSplat.classList.add("on"); api.msg('💦 흠뻑!<small>'+esc(by.nm)+' 의 '+WP[wi].ic+' '+WP[wi].nm+'</small>', 1900); } return; }   /* 잡은 사람(다른 기기)이 다음 무기로 */
    if(by && by.me && by!==t) killFx(t.nm); if(t.me){ streak=0; eSplat.classList.remove("on"); void eSplat.offsetWidth; eSplat.classList.add("on"); }
    if(by && by!==t){ by.kills++; if(wi>=LAST && by.wi>=LAST){ declareWin(by); return; } up(by);
      t.dmgBy.forEach((v,k)=>{ if(k && k!==by && k!==t && v>=40 && k.alive){ k.asst++; if(k.asst>=2 && k.wi<LAST-1){ k.asst=0; up(k, true); } } }); }
    t.dmgBy.clear();
    if(t.me){ api.msg('💦 흠뻑!<small>'+(by&&by!==t?esc(by.nm)+' 의 '+WP[wi].ic+' '+WP[wi].nm:'')+'</small>', 1900); } }
  function up(a, asst){ if(a.wi>=LAST) return; a.wi++; if(a.bot){ gunModel(a.gun, a.wi, true); return; }
    api.sfx.up(); vmA.sw=0; setTimeout(()=>{ vmSet(me.wi); }, 160); fireIc();
    api.msg('<b class="aUp">'+(asst?'🤝 ':'')+WP[a.wi].ic+' '+WP[a.wi].nm+'!</b><small>'+(asst?'도움 2번 · ':'')+(a.wi===LAST?'마지막! 🔨 뿅망치로 맞히면 우승!':(a.wi+1)+' / '+WP.length+' 단계')+'</small>', 1700); drawLadder(); }
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
  function navBuild(){ for(let i=0;i<NC;i++) for(let j=0;j<NC;j++){ const x=-R+CS*(i+.5), z=-R+CS*(j+.5); let top=0; for(const b of BOX) if(b.y0===0 && x>b.x0 && x<b.x1 && z>b.z0 && z<b.z1) top=Math.max(top,b.y1); HT[j*NC+i]=top;
    let bl=0; for(const b of BOX){ if(x+.36>b.x0 && x-.36<b.x1 && z+.36>b.z0 && z-.36<b.z1){ if(b.y1>top+.45 && b.y0<top+1.7) { bl=1; break; } } } BL[j*NC+i]=bl || top>3; }
    /* 나오는 자리가 없는 맵 = 땅 칸 중에서 서로 멀리 14곳 */
    if(!SPAWN.length){ const C=[]; for(let i=3;i<NC-3;i+=3) for(let j=3;j<NC-3;j+=3){ const c=j*NC+i, x=-R+CS*(i+.5), z=-R+CS*(j+.5); if(BL[c] || HT[c]>0 || Math.hypot(x,z)<7 || !free({x, y:0, z}, HH)) continue; let ok=true; for(let di=-2;di<=2 && ok;di++) for(let dj=-2;dj<=2;dj++){ const q=(j+dj)*NC+i+di; if(BL[q]){ ok=false; break; } } if(ok) C.push([x,z]); }
      const pick=[C.reduce((b,p)=>Math.hypot(p[0],p[1])>Math.hypot(b[0],b[1])?p:b, C[0])]; while(pick.length<14 && pick.length<C.length){ let best=null, bd=-1; C.forEach(p=>{ let d=1e9; for(const q of pick) d=Math.min(d, Math.hypot(p[0]-q[0],p[1]-q[1])); if(d>bd){ bd=d; best=p; } }); pick.push(best); } SPAWN.push(...pick); } }
  navBuild();
  function setMap(k){ if(k===MAPK || !MAPS[k]) return; buildMap(k); navBuild(); placeShow(); }
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

  /* ════ 👫 같이 하기 (최대 6명 · 모자라면 봇) ════ */
  let NETR=null; const PEER={};
  const idOf=a=>a.me?(NETR?NETR.code:"me"):a.net?a.code:"b"+a.i;
  const actorOf=id=>{ if(!id) return null; if(NETR && id===NETR.code) return me; if(id.charAt(0)==="b" && /^b\d$/.test(id)) return ACT.find(a=>a.bot && a.i===+id.slice(1))||null; return PEER[id]||null; };
  const hostCode=()=>{ const h=(NETR&&NETR.d&&NETR.d.h)||{}, L=NETR?NETR.live(true).map(p=>p.k):[]; return L.indexOf(h.c)>=0?h.c:L[0]; };
  function mkPeer(k, p){ const a=mkAct({net:true, code:k, nm:(p.n||"친구").slice(0,8), prot:0}); a.tp=new V3(p.x||0,p.y||0,p.z||0); a.p.copy(a.tp); a.lf=p.f|0;
    let c=null; try{ c=buildAvatar(p.av||{}); c.t=0; c.blinkT=2; c.act="idle"; }catch(e){ c=null; } const G=new THREE.Group(); scene.add(G); a.G=G;
    if(c){ c.g.scale.setScalar(AVK); G.add(c.g); a.c=c; c.g.traverse(m=>{ if(m.isMesh) m.castShadow=!api.low; }); }
    a.gun=new THREE.Group(); if(c && c.armR){ c.armR.add(a.gun); a.gun.position.set(0,-.2,0); a.gun.scale.setScalar(.7); } gunModel(a.gun, p.wi|0, true); a.gw=p.wi|0;
    a.tag=nameTag("👫 "+a.nm); a.tag.position.y=2.15; G.add(a.tag); const bub=new THREE.Mesh(new THREE.SphereGeometry(1.15,16,12), new THREE.MeshBasicMaterial({color:0x9fe8ff, transparent:true, opacity:.25, depthWrite:false})); bub.position.y=.95; G.add(bub); a.bub=bub; bub.visible=false;
    PEER[k]=a; return a; }
  function netStart(h, peers){ if(h.map && h.map!==MAPK) setMap(h.map); D=DIFF[h.df]||DIFF.normal; const ks=peers.map(p=>p.k).filter(k=>k!==NETR.code).slice(0,5);
    ks.forEach(k=>{ const p=(NETR.d.p||{})[k]||{}; mkPeer(k, p); });
    const nb=Math.max(0, 6-1-ks.length); BOTL.slice(0,nb).forEach(a=>{ ACT.push(a); a.G.visible=true; a.rb=!NETR.authority(); spawn(a); a.prot=0; });
    spawn(me); me.prot=0; time.st=h.st+INTRO*1000+3000; drawBoard(); intro(h.st); }
  function netNode(){ return {av:api.av||{}, x:+me.p.x.toFixed(2), y:+me.p.y.toFixed(2), z:+me.p.z.toFixed(2), yw:+me.yaw.toFixed(2), pt:+me.pitch.toFixed(2), wi:me.wi, al:me.alive?1:0, sl:me.sl?1:0, f:me.fc|0, kl:me.kills, sk:Math.round(me.soak)}; }
  function onEv(e){ if(time.over) return; const by=actorOf(e.by), from=new V3(e.fx||0,1.4,e.fz||0);
    if(e.k==="hit"){ hurt(me, e.dm, by||{nm:"친구", net:true}, e.wi|0, !!e.hd, from, true); }
    else if(e.k==="hitb"){ const b=ACT.find(a=>a.bot && a.i===e.i); if(b) hurt(b, e.dm, by, e.wi|0, !!e.hd, from, true); }
    else if(e.k==="kill"){ me.kills++; killFx(e.vic); if((e.wi|0)>=LAST && me.wi>=LAST){ declareWin(me); return; } up(me); }
    else if(e.k==="bkill"){ const b=ACT.find(a=>a.bot && a.i===e.i); if(!b) return; b.kills++; if((e.wi|0)>=LAST && b.wi>=LAST){ declareWin(b); return; } up(b); } }
  function netApply(dt){ if(!NETR || !NETR.d || (phase!=="play" && phase!=="intro")) return; const d=NETR.d, host=NETR.authority();
    Object.keys(PEER).forEach(k=>{ const a=PEER[k], p=(d.p||{})[k]; if(!p || NETR.now()-(p.t||0)>10000){ if(a.G.visible){ a.G.visible=false; a.alive=false; } return; }
      a.tp.set(p.x||0,p.y||0,p.z||0); a.ty=p.yw||0; a.pitch=p.pt||0; a.kills=p.kl|0; a.soak=p.sk|0; a.sl=!!p.sl; a.h=a.sl?HS:HH; if((p.wi|0)!==a.gw){ a.wi=p.wi|0; a.gw=a.wi; gunModel(a.gun, a.wi, true); }
      const al=!!p.al; if(al && !a.alive){ a.alive=true; a.dead=0; a.p.copy(a.tp); a.G.visible=true; } else if(!al && a.alive){ a.alive=false; a.dead=0; } 
      if((p.f|0)>a.lf){ a.lf=p.f|0; if(a.alive){ const e=eyeOf(a), dd=dirOf(a.yaw, a.pitch), r=trace(a, e, dd, WP[a.wi].rng); stream(muzzle(a), e.clone().addScaledVector(dd, Math.min(r.t, WP[a.wi].rng)), 1, WP[a.wi].t==="beam"); if(e.distanceTo(me.p)<22) api.sfx.shot(WP[a.wi].k, true); } } });
    /* 봇: 방장이 움직이고 나머지는 받아서 그림 */
    if(host){ ACT.forEach(a=>{ if(a.bot) a.rb=false; }); NETR.bT=(NETR.bT||0)-dt; if(NETR.bT<=0){ NETR.bT=.12; NETR.put("b", ACT.filter(a=>a.bot).map(a=>[a.i, +a.p.x.toFixed(2), +a.p.y.toFixed(2), +a.p.z.toFixed(2), +a.yaw.toFixed(2), +a.pitch.toFixed(2), a.wi, a.alive?1:0, a.sl?1:0, a.fc|0, a.kills, Math.round(a.soak)])); } }
    else { (d.b||[]).forEach(r=>{ const a=ACT.find(x=>x.bot && x.i===r[0]); if(!a) return; a.rb=true; a.tp=a.tp||new V3(); a.tp.set(r[1],r[2],r[3]); a.ty=r[4]; a.pitch=r[5]; if(r[6]!==a.wi){ a.wi=r[6]; gunModel(a.gun, a.wi, true); } a.kills=r[10]; a.soak=r[11]; a.sl=!!r[8]; a.h=a.sl?HS:HH;
        const al=!!r[7]; if(al && !a.alive){ a.alive=true; a.dead=0; a.p.copy(a.tp); a.G.visible=true; } else if(!al && a.alive){ a.alive=false; a.dead=0; }
        if((r[9]|0)>(a.lf|0)){ a.lf=r[9]|0; if(a.alive){ const e=eyeOf(a), dd=dirOf(a.yaw, a.pitch), q=trace(a, e, dd, WP[a.wi].rng); stream(muzzle(a), e.clone().addScaledVector(dd, Math.min(q.t, WP[a.wi].rng)), 1, WP[a.wi].t==="beam"); if(e.distanceTo(me.p)<22) api.sfx.shot(WP[a.wi].k, true); } } }); }
    if(d.h && d.h.win && !time.over){ const w=actorOf(d.h.win.c)||{nm:d.h.win.n}; win(w); } }
  /* 받아서 그리는 사람·봇 (부드럽게 따라감 · 넘어짐) */
  function netVis(a, dt){ if(!a.tp) return; if(a.alive){ a.v.subVectors(a.tp, a.p).multiplyScalar(1/Math.max(dt,1e-3)*.18); a.p.lerp(a.tp, Math.min(1, dt*12)); let dy=angN(a.ty-a.yaw); a.yaw+=dy*Math.min(1,dt*14); a.onG=a.p.y<.05 || Math.abs(a.tp.y-a.p.y)<.05; }
    else a.dead+=dt;
    const G=a.G; G.position.set(a.p.x,a.p.y,a.p.z); a.bub.visible=false; drawTag(a.tag, a.soak, a.wi);
    if(!a.alive){ const k=Math.min(1.5, a.dead*6); if(a.bk){ a.bk.g.rotation.x=-k; } else if(a.c){ a.c.g.rotation.x=-Math.min(1.4,k); } if(a.dead>1.1) G.visible=false; return; }
    G.visible=true; if(a.c){ const c=a.c; c.face=a.yaw+Math.PI; c.moving=Math.hypot(a.tp.x-a.p.x, a.tp.z-a.p.z)>.03 && a.onG && !a.sl; try{ animChar(c, dt); }catch(e){} c.g.rotation.y=a.yaw+Math.PI; c.g.rotation.x=a.sl?-.55:0; c.g.position.y=a.sl?.15:0;
      if(c.armR){ c.armR.rotation.x=-Math.PI/2-a.pitch*.8; c.armR.rotation.z=0; } if(c.armL){ c.armL.rotation.x=-1.25-a.pitch*.6; c.armL.rotation.z=-.35; } }
    if(a.bk){ const B=a.bk, mv=Math.hypot(a.tp.x-a.p.x, a.tp.z-a.p.z)>.03; B.t+=dt*(mv?11:0); const sw=mv?Math.sin(B.t)*.8:0; B.legL.rotation.x=sw; B.legR.rotation.x=-sw; B.g.rotation.set(a.sl?-.6:0, a.yaw+Math.PI, 0); B.g.position.y=a.sl?.25:0; B.armR.rotation.set(-Math.PI/2-a.pitch*.8,0,0); B.armL.rotation.set(-Math.PI/2+.2-a.pitch*.6,-.5,0); } }
  const mapTag=h=>{ const M=MAPS[h && h.map]||MAPS.pool; return M.ic+' '+M.nm; };
  function goCo(){ CO=true; phase="room"; menuUI("room");
    NETR=MG.room(api, {pre:"mga", title:"물총 같이 하기", ic:"💦", max:6, fill:1, h:()=>({df:SET.diff, map:MAPK}), tag:mapTag, back:()=>{ const R0=NETR; NETR=null; try{ R0.dispose(); }catch(e){} CO=false; phase="menu"; setMap(SET.map); menuUI("main"); }});
    NETR.node=netNode; NETR.onEv=onEv; NETR.onFeed=f=>feedAdd(f.a, f.b, f.ic, false); NETR.onStart=(h, peers)=>netStart(h, peers); }
  function beginSolo(){ CO=false; D=DIFF[SET.diff]||DIFF.normal; BOTL.forEach(a=>{ if(!ACT.includes(a)) ACT.push(a); a.rb=false; a.G.visible=true; spawn(a); a.prot=0; }); spawn(me); me.prot=0; time.left=MATCH; drawBoard(); intro(0); }

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
#mgUI .mgX{display:none}
#mgUI.aMenuOn .mgHud>*:not(style),#mgUI.aMenuOn .mgB,#mgUI.aMenuOn .mgJoy,#mgUI.aMenuOn .mgJoyH,#mgUI.aMenuOn .mgTop,#mgUI.aMenuOn .aPzB{display:none!important}
#mgUI.aBs0 .mgB{scale:.82} #mgUI.aBs2 .mgB{scale:1.2}
#mgUI .aPzB{position:absolute;left:max(10px,env(safe-area-inset-left));top:calc(8px + env(safe-area-inset-top));pointer-events:auto;border:0;background:rgba(20,30,60,.55);color:#fff;font:inherit;font-size:15px;border-radius:14px;padding:8px 12px;min-height:40px}
#mgUI .aM{position:absolute;inset:0;pointer-events:none;display:none;color:#fff}
#mgUI.aMenuOn .aM{display:block}
#mgUI .aSide{position:absolute;left:0;top:0;bottom:0;width:min(400px,50vw);box-sizing:border-box;padding:calc(12px + env(safe-area-inset-top)) 22px calc(12px + env(safe-area-inset-bottom)) max(18px,calc(env(safe-area-inset-left) + 10px));background:linear-gradient(90deg,rgba(8,24,66,.9) 0%,rgba(8,24,66,.74) 72%,rgba(8,24,66,0) 100%);display:flex;flex-direction:column;justify-content:center;gap:9px;pointer-events:auto}
#mgUI .aLogo b{display:block;font-family:var(--en);font-weight:900;font-size:38px;line-height:.95;letter-spacing:.01em;color:#fff;text-shadow:0 3px 0 #2f7fff,0 6px 0 rgba(0,0,0,.25)}
#mgUI .aLogo span{display:block;font-size:14.5px;opacity:.9;margin-top:6px}
#mgUI .aBig{display:flex;flex-direction:column;align-items:flex-start;border:0;border-radius:18px;padding:9px 16px;font:inherit;color:#fff;text-align:left;min-height:58px;box-shadow:0 5px 0 rgba(0,0,0,.28);cursor:pointer}
#mgUI .aBig span{font-size:21px;line-height:1.2} #mgUI .aBig small{font-size:13px;opacity:.95}
#mgUI .aBig.solo{background:linear-gradient(135deg,#ffa06b,#ff6a4d)} #mgUI .aBig.co{background:linear-gradient(135deg,#55b6ff,#2f6fff)}
#mgUI .aBig:active,#mgUI .aRow button:active,#mgUI .aMaps button:active{transform:translateY(3px)}
#mgUI .aMaps{display:flex;gap:6px}
#mgUI .aMaps button{flex:1;min-width:0;border:2px solid rgba(255,255,255,.22);background:rgba(255,255,255,.1);color:#fff;border-radius:14px;font:inherit;font-size:12.5px;padding:4px 2px;min-height:50px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:1px;line-height:1.15;word-break:keep-all}
#mgUI .aMaps button i{font-style:normal;font-size:20px} #mgUI .aMaps button.on{border-color:#ffd23f;background:rgba(255,210,63,.24);box-shadow:0 0 0 2px rgba(255,210,63,.35)}
#mgUI .aRow{display:flex;gap:6px}
#mgUI .aRow button{flex:1;border:0;border-radius:14px;background:rgba(255,255,255,.16);color:#fff;font:inherit;font-size:21px;min-height:52px;display:flex;flex-direction:column;align-items:center;justify-content:center;line-height:1.1}
#mgUI .aRow button small{font-size:12px;margin-top:2px}
#mgUI .aMe{position:absolute;right:max(14px,env(safe-area-inset-right));bottom:calc(12px + env(safe-area-inset-bottom));background:rgba(8,24,66,.62);border-radius:14px;padding:6px 12px;text-align:right;pointer-events:none}
#mgUI .aMe b{display:block;font-weight:400;font-size:17px} #mgUI .aMe small{font-size:12.5px;opacity:.9}
#mgUI.aIntro .aSide,#mgUI.aIntro .aMe,#mgUI.aRoom .aSide{display:none}
#mgUI.aRoom .mgRoomP{left:max(16px,calc(env(safe-area-inset-left) + 8px));top:50%;transform:translateY(-50%);width:min(400px,calc(50vw - 16px));max-height:calc(100% - 24px);overflow:auto;box-sizing:border-box}
@media (orientation:portrait){ #mgUI.aRoom .mgRoomP{left:50%;top:auto;bottom:calc(16px + env(safe-area-inset-bottom));transform:translateX(-50%);width:min(440px,calc(100vw - 24px))} }
#mgUI .aVs{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);display:none;text-align:center;pointer-events:none;width:min(560px,calc(100vw - 24px))}
#mgUI.aIntro .aVs{display:block}
#mgUI .aVs h2{font-weight:900;font-size:44px;margin:0;text-shadow:0 4px 0 #2f6fff,0 7px 0 rgba(0,0,0,.25);animation:aPop .45s cubic-bezier(.2,1.6,.4,1) both}
#mgUI .aVs .mp{display:inline-block;font-size:17px;margin:6px 0 10px;background:rgba(8,24,66,.7);border-radius:12px;padding:3px 12px}
#mgUI .aVs .ps{display:flex;flex-wrap:wrap;gap:6px;justify-content:center}
#mgUI .aVs .ps span{background:rgba(8,24,66,.8);border:2px solid rgba(255,255,255,.45);border-radius:14px;padding:5px 11px;font-size:15.5px;animation:aPop .35s cubic-bezier(.2,1.6,.4,1) both}
#mgUI .aVs .ps span.me{background:#ff8466;border-color:#fff} #mgUI .aVs .ps span.fr{background:#2f8cff}
#mgUI .aVs .rl{margin-top:12px;font-size:15px;background:rgba(8,24,66,.66);display:inline-block;border-radius:12px;padding:5px 12px;animation:aPop .4s .8s both}
@keyframes aPop{from{transform:scale(.4);opacity:0}to{transform:scale(1);opacity:1}}
#mgUI .aCardW{position:absolute;inset:0;display:none;align-items:center;justify-content:center;background:rgba(5,12,35,.5);pointer-events:auto;z-index:6}
#mgUI .aCardW.on{display:flex}
#mgUI .aCard{width:min(470px,calc(100vw - 28px));max-height:calc(100% - 20px);overflow:auto;box-sizing:border-box;background:#fff8ea;color:#4b3527;border-radius:24px;border:3px solid #cfae7e;padding:12px 16px 14px;position:relative;box-shadow:0 10px 0 rgba(0,0,0,.15)}
#mgUI .aCard h3{margin:2px 0 4px;font-size:22px;font-weight:400;text-align:center}
#mgUI .aCard .sub2{color:#9a7e63;font-size:13.5px;text-align:center;margin:2px 0 8px}
#mgUI .aCard .x{position:absolute;right:8px;top:8px;width:42px;height:42px;border:0;border-radius:50%;background:#f0e4cc;color:#4b3527;font-size:18px}
#mgUI .aSet{display:flex;align-items:center;gap:8px;padding:6px 0;border-bottom:1px dashed #e6d3b0}
#mgUI .aSet>span{flex:0 0 128px;font-size:15px}
#mgUI .aSeg{display:flex;flex:1;gap:4px}
#mgUI .aSeg button{flex:1;min-width:0;min-height:44px;border:0;border-radius:12px;background:#f0e4cc;color:#4b3527;font:inherit;font-size:14.5px;padding:0 4px}
#mgUI .aSeg button.on{background:#5aa7ff;color:#fff;box-shadow:0 3px 0 #2f7fb3}
#mgUI .aGo{display:block;width:100%;margin-top:12px;border:0;border-radius:16px;min-height:52px;background:#ff8466;color:#fff;font:inherit;font-size:19px;box-shadow:0 4px 0 #d9604a}
#mgUI .aRow2{display:flex;gap:6px;margin-top:8px} #mgUI .aRow2 button{flex:1;border:0;border-radius:14px;min-height:48px;background:#f0e4cc;color:#4b3527;font:inherit;font-size:15px}
#mgUI .aWpL{display:grid;grid-template-columns:1fr 1fr;gap:6px}
#mgUI .aWpL div{background:#f5e8d0;border-radius:14px;padding:6px 8px;display:flex;gap:8px;align-items:center;font-size:13px;line-height:1.3;text-align:left}
#mgUI .aWpL i{font-style:normal;font-size:26px} #mgUI .aWpL b{font-weight:400;font-size:15px;display:block}
#mgUI .aRec{display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px}
#mgUI .aRec div{background:#f5e8d0;border-radius:14px;padding:8px 4px;text-align:center;font-size:13px} #mgUI .aRec b{display:block;font-size:22px;font-weight:400;color:#ff6a4d}
@media (max-height:440px) and (orientation:landscape){ #mgUI .aSide{gap:6px} #mgUI .aLogo b{font-size:28px} #mgUI .aLogo span{margin-top:3px;font-size:13px} #mgUI .aBig{min-height:50px;padding:6px 14px} #mgUI .aBig span{font-size:18px} #mgUI .aMaps button{min-height:44px} #mgUI .aRow button{min-height:46px;font-size:18px} #mgUI .aSet{padding:4px 0} #mgUI .aSeg button{min-height:40px} }
@media (min-height:700px) and (orientation:landscape){ #mgUI .aSide{width:min(460px,46vw);gap:12px} #mgUI .aLogo b{font-size:52px} #mgUI .aLogo span{font-size:16px} #mgUI .aBig{min-height:70px} #mgUI .aBig span{font-size:25px} #mgUI .aBig small{font-size:14.5px} #mgUI .aMaps button{min-height:62px;font-size:14px} #mgUI .aMaps button i{font-size:26px} #mgUI .aRow button{min-height:62px;font-size:24px} #mgUI .aRow button small{font-size:13.5px} }
@media (orientation:portrait){ #mgUI .aSide{top:auto;width:100%;padding:44px max(16px,env(safe-area-inset-right)) calc(14px + env(safe-area-inset-bottom)) max(16px,env(safe-area-inset-left));background:linear-gradient(0deg,rgba(8,24,66,.92) 0%,rgba(8,24,66,.8) 75%,rgba(8,24,66,0) 100%)} #mgUI .aSide>*{max-width:560px;width:100%;margin:0 auto} #mgUI .aMe{top:calc(12px + env(safe-area-inset-top));bottom:auto} }
@media (max-width:520px){ #mgUI .aSet{flex-wrap:wrap} #mgUI .aSet>span{flex-basis:100%} #mgUI .aWpL{grid-template-columns:1fr} #mgUI .aRec{grid-template-columns:1fr 1fr} }
/* (v658) 사용자: 「물총 아레나 … 게임 자체 퀄리티도 올려 줬으면」 — 게임 중 = 섬 스티커(A) · 메뉴 = 게임쇼(B) */
#mgUI .aClock{background:#FFF6E3;color:#4A2E1F;border:3px solid #4A2E1F;border-radius:999px;box-shadow:0 0 0 2px #fff,0 4px 0 2px rgba(74,46,31,.35);padding:0 14px;font-size:20px;display:flex;align-items:center;gap:5px}
#mgUI .aClock.low{background:#FF5A4E;color:#fff;animation:aLow .5s infinite alternate} @keyframes aLow{to{transform:scale(1.1)}}
#mgUI .aTop{gap:7px}
#mgUI .aLad{gap:2px;background:#FFF6E3;border:3px solid #4A2E1F;border-radius:14px;padding:3px 6px;box-shadow:0 0 0 2px #fff,0 4px 0 2px rgba(74,46,31,.35)}
#mgUI .aLad b{background:#efe0c2;width:25px;height:25px;opacity:.8;border-radius:8px}
#mgUI .aLad b.d{opacity:.38} #mgUI .aLad b.c{background:#FF5A4E;box-shadow:0 0 0 2.5px #4A2E1F;transform:scale(1.28);opacity:1;position:relative;z-index:1;animation:aCur .9s infinite alternate} @keyframes aCur{to{transform:scale(1.4)}}
#mgUI .aBd{background:#FFF6E3;color:#4A2E1F;border:3px solid #4A2E1F;border-radius:14px;box-shadow:0 0 0 2px #fff,0 4px 0 2px rgba(74,46,31,.35);padding:4px 10px;font-size:14px;min-width:112px}
#mgUI .aBd .me{color:#e0452f} #mgUI .aBd div+div{border-top:1.5px dashed rgba(74,46,31,.25)}
#mgUI .aFd div{background:#FFF6E3;color:#4A2E1F;border:2px solid #4A2E1F;border-radius:999px;padding:0 10px;box-shadow:0 2px 0 rgba(74,46,31,.35);animation:aFdIn .25s} @keyframes aFdIn{from{transform:translateX(-30px);opacity:0}}
#mgUI .aFd .me{background:#FF8FC4;color:#4A2E1F}
#mgUI .aWpn{background:#FFF6E3;color:#4A2E1F;border:3px solid #4A2E1F;border-radius:999px;box-shadow:0 0 0 2px #fff,0 4px 0 2px rgba(74,46,31,.35);font-size:16px;padding:2px 15px}
#mgUI .aSoak{width:176px;height:16px;border:3px solid #4A2E1F;border-radius:10px;background:#FFF6E3;box-shadow:0 0 0 2px #fff,0 3px 0 2px rgba(74,46,31,.3);bottom:calc(56px + env(safe-area-inset-bottom));overflow:visible}
#mgUI .aSoak i{border-radius:6px;transition:width .12s} #mgUI .aSoak::before{content:"💧";position:absolute;left:-26px;top:-6px;font-size:18px}
#mgUI .aCnt{color:#ffd860;-webkit-text-stroke:12px #0D0F33;paint-order:stroke fill;font-size:118px;transform:translate(-50%,-50%) rotate(-4deg);text-shadow:none}
#mgUI .aHint{background:#FFF6E3;color:#4A2E1F;border:2px solid #4A2E1F;bottom:calc(92px + env(safe-area-inset-bottom))}
#mgUI .aPzB{background:#fff;color:#4A2E1F;border:3px solid #4A2E1F;border-radius:14px;box-shadow:inset 0 -4px 0 rgba(0,0,0,.08),0 4px 0 #4A2E1F;font-family:var(--kr)}
#mgUI .mgB[data-b=fire],#mgUI .mgB[data-b=fire2]{background:#FF5A4E;border:4px solid #4A2E1F;box-shadow:0 0 0 4px #fff,inset 0 -9px 0 rgba(0,0,0,.16),0 6px 0 4px rgba(74,46,31,.4);opacity:.9}
#mgUI .mgB[data-b=jump],#mgUI .mgB[data-b=slide]{background:#FFF6E3;color:#4A2E1F;border:4px solid #4A2E1F;box-shadow:0 0 0 3px #fff,inset 0 -6px 0 rgba(74,46,31,.14),0 5px 0 3px rgba(74,46,31,.4);opacity:.88;font-family:var(--kr);font-weight:400;letter-spacing:0}
#mgUI .mgB[data-b=jump]{font-size:19px} #mgUI .mgB[data-b=slide]{font-size:13px}
#mgUI .mgB.dn{transform:translateY(4px) scale(.95);filter:brightness(1.08)}
#mgUI .aDmg{position:absolute;transform:translate(-50%,-50%);font-family:var(--en);font-weight:900;font-size:24px;color:#fff;-webkit-text-stroke:5px #1d3f8a;paint-order:stroke fill;pointer-events:none;animation:aDmg .65s ease-out forwards;z-index:2}
#mgUI .aDmg.hd{color:#ffe14d;font-size:32px;-webkit-text-stroke:6px #7a3b00}
@keyframes aDmg{0%{transform:translate(-50%,-50%) scale(.4)}25%{transform:translate(-50%,-110%) scale(1.25)}100%{transform:translate(-50%,-260%) scale(.9);opacity:0}}
#mgUI .aKill{top:60%;font-size:28px;display:none;padding:4px 24px} #mgUI .aKill.on{display:block} #mgUI .aKill small{display:block;font-size:14px;opacity:.95;margin-top:-2px}
#mgUI .aSplat{position:absolute;inset:0;pointer-events:none;opacity:0;background:radial-gradient(circle at 12% 18%,rgba(120,200,255,.85) 0 34px,transparent 36px),radial-gradient(circle at 86% 26%,rgba(120,200,255,.8) 0 46px,transparent 48px),radial-gradient(circle at 22% 78%,rgba(120,200,255,.8) 0 40px,transparent 42px),radial-gradient(circle at 80% 82%,rgba(120,200,255,.85) 0 30px,transparent 32px),radial-gradient(circle at 55% 10%,rgba(120,200,255,.7) 0 22px,transparent 24px)}
#mgUI .aSplat.on{animation:aSplat .9s ease-out} @keyframes aSplat{0%{opacity:1;transform:scale(.7)}30%{opacity:.95;transform:scale(1)}100%{opacity:0;transform:scale(1.06) translateY(30px)}}
#mgUI .mgMsg .aUp{display:inline-block;font-weight:400;font-size:42px;color:#ffd860;-webkit-text-stroke:8px #0D0F33;paint-order:stroke fill;transform:rotate(-3deg);text-shadow:none;white-space:nowrap}
#mgUI .aSide{background:linear-gradient(90deg,rgba(13,15,51,.95) 0%,rgba(30,33,96,.86) 70%,rgba(30,33,96,0) 100%)}
#mgUI .aLogo b{font-family:var(--kr);font-weight:400;font-size:46px;line-height:1.15;letter-spacing:0;color:#ffd860;-webkit-text-stroke:9px #0D0F33;paint-order:stroke fill;text-shadow:none;filter:drop-shadow(0 5px 0 #0D0F33) drop-shadow(0 0 14px rgba(255,201,74,.5));transform:rotate(-3deg);display:inline-block}
#mgUI .aLogo span{display:inline-block;background:rgba(255,255,255,.14);border-radius:999px;padding:3px 12px;margin-top:4px}
#mgUI .aBig{border:3px solid #0D0F33;box-shadow:inset 0 -7px 0 rgba(0,0,0,.2),inset 0 4px 0 rgba(255,255,255,.3),0 5px 0 #0D0F33;text-shadow:0 2px 0 rgba(0,0,0,.25)}
#mgUI .aBig.solo{background:#FF4FA8} #mgUI .aBig.co{background:#2FB5FF}
#mgUI .aMaps button{border:2px solid #FFC94A;background:#262a78;box-shadow:0 4px 0 #0D0F33;border-radius:16px}
#mgUI .aMaps button.on{background:#FFC94A;color:#0D0F33;border-color:#FFC94A;box-shadow:0 0 0 3px #3FD8FF,0 4px 0 #0D0F33}
#mgUI .aRow button{background:#262a78;border:2px solid rgba(255,201,74,.6);box-shadow:0 4px 0 #0D0F33}
#mgUI .aMe{background:#1E2160;border:2px solid #FFC94A;border-radius:16px;box-shadow:0 3px 0 #0D0F33}
#mgUI .aCard{background:#FFF6E3;border:3px solid #4A2E1F;box-shadow:0 0 0 4px #fff,0 8px 0 4px rgba(74,46,31,.35);color:#4A2E1F}
#mgUI .aGo{background:#FF4FA8;border:3px solid #4A2E1F;box-shadow:inset 0 -6px 0 rgba(0,0,0,.14),0 5px 0 #4A2E1F}
#mgUI .aSeg button.on{background:#FFC53D;color:#4A2E1F;box-shadow:0 0 0 2.5px #4A2E1F}
#mgUI .aVs h2{font-family:var(--kr);font-weight:400;font-size:54px;color:#ffd860;-webkit-text-stroke:10px #0D0F33;paint-order:stroke fill;text-shadow:none;filter:drop-shadow(0 5px 0 #0D0F33)}
#mgUI .aVs .mp,#mgUI .aVs .rl{background:#1E2160;border:2px solid #FFC94A}
@media (max-height:440px) and (orientation:landscape){ #mgUI .aLogo b{font-size:32px;-webkit-text-stroke-width:7px} #mgUI .aLogo span{font-size:12.5px;margin-top:1px} #mgUI .aVs h2{font-size:40px} #mgUI .aKill{font-size:22px;top:62%} }
@media (min-height:700px) and (orientation:landscape){ #mgUI .aLogo b{font-size:58px} }
@media (min-width:700px) and (min-height:900px), (min-width:1000px) and (min-height:700px){ #mgUI .aTop,#mgUI .aBd,#mgUI .aFd,#mgUI .aWpn,#mgUI .aPzB,#mgUI .aSoak{zoom:1.3} #mgUI .aKill{zoom:1.3} #mgUI .aDmg{font-size:32px} #mgUI .aHint{bottom:calc(128px + env(safe-area-inset-bottom))} #mgUI.aBs0 .mgB{scale:1.05} #mgUI.aBs1 .mgB{scale:1.3} #mgUI.aBs2 .mgB{scale:1.55} #mgUI .mgB[data-b=fire]{right:max(40px,calc(env(safe-area-inset-right) + 32px));bottom:calc(196px + env(safe-area-inset-bottom))} #mgUI .mgB[data-b=jump]{right:max(36px,calc(env(safe-area-inset-right) + 28px));bottom:calc(58px + env(safe-area-inset-bottom))} #mgUI .mgB[data-b=slide]{right:max(168px,calc(env(safe-area-inset-right) + 160px));bottom:calc(52px + env(safe-area-inset-bottom))} #mgUI .mgB[data-b=fire2]{left:max(36px,calc(env(safe-area-inset-left) + 28px));bottom:calc(270px + env(safe-area-inset-bottom))} }
@media (orientation:portrait){ #mgUI .aBd,#mgUI .aFd{top:calc(100px + env(safe-area-inset-top))} #mgUI .mgB[data-b=fire]{bottom:calc(200px + env(safe-area-inset-bottom))} #mgUI .mgB[data-b=jump]{bottom:calc(106px + env(safe-area-inset-bottom))} #mgUI .mgB[data-b=slide]{bottom:calc(100px + env(safe-area-inset-bottom))} #mgUI .aHint{bottom:calc(310px + env(safe-area-inset-bottom));white-space:normal;text-align:center;width:max-content;max-width:calc(100vw - 30px)} #mgUI .aKill{top:54%} }
#mgUI.aEnd .mgHud>*:not(style):not(.puR),#mgUI.aEnd .mgB,#mgUI.aEnd .mgJoy,#mgUI.aEnd .mgJoyH,#mgUI.aEnd .aPzB{display:none!important}
</style>
<div class="aWet"></div><div class="aDead"></div><div class="aDir"><i></i></div>
<div class="aCx"><i class="h" style="left:-18px"></i><i class="h" style="left:8px"></i><i class="v" style="top:-18px"></i><i class="v" style="top:8px"></i><i class="d"></i></div><div class="aHm"></div>
<div class="aTop"><div class="aClock">5:00</div><div class="aLad"></div></div><div class="aBd"></div><div class="aFd"></div>
<div class="aSoak"><i></i></div><div class="aWpn"></div><div class="aCnt"></div><div class="aHint"></div><div class="aSplat"></div><div class="paBan aKill"></div>`;
  const Q=s=>hud.querySelector(s), eCx=Q(".aCx"), eHm=Q(".aHm"), eWet=Q(".aWet"), eDir=Q(".aDir"), eClk=Q(".aClock"), eLad=Q(".aLad"), eBd=Q(".aBd"), eFd=Q(".aFd"), eWpn=Q(".aWpn"), eSoak=Q(".aSoak i"), eCnt=Q(".aCnt"), eDead=Q(".aDead"), eHint=Q(".aHint"), eSplat=Q(".aSplat"), eKill=Q(".aKill"); try{ PUI.css(); }catch(e){}
  const root=api.ui, fireB=root.querySelector('[data-b=fire]'), fire2=root.querySelector('[data-b=fire2]');
  function fireIc(){ const W=WP[me.wi]; if(fireB) fireB.firstChild.nodeValue=W.ic; if(fire2) fire2.firstChild.nodeValue=W.ic; eWpn.innerHTML=W.ic+' '+W.nm+' <small>'+(me.wi+1)+'/'+WP.length+(W.t==="snipe"?' · 꾹 눌러 조준 → 떼면 쏘기':W.t==="melee"?' · 가까이 가서!':'')+'</small>'; }
  function drawLadder(){ eLad.innerHTML=WP.map((w,i)=>'<b class="'+(i<me.wi?"d":i===me.wi?"c":"")+'">'+w.ic+'</b>').join(""); }
  function drawFeed(){ eFd.innerHTML=FEED.map(f=>'<div class="'+(f.me?"me":"")+'">'+(f.a?esc(f.a)+' '+f.ic+' ':'💧 ')+esc(f.b)+'</div>').join(""); }
  let bdT=0; function drawBoard(){ const L=ACT.slice().sort((x,y)=>y.wi-x.wi || y.kills-x.kills); const S3=L.slice(0,3); if(S3.indexOf(me)<0) S3.push(me); eBd.innerHTML=S3.map(a=>[a,L.indexOf(a)]).map(([a,i])=>'<div class="'+(a.me?"me":"")+'"><span>'+(i+1)+'. '+esc(a.nm)+'</span><span>'+WP[a.wi].ic+' '+(a.wi+1)+'</span></div>').join(""); }
  const touch=matchMedia("(pointer:coarse)").matches || "ontouchstart" in window;
  eHint.style.display="none";
  function showHint(){ eHint.style.display=""; if(!touch){ eHint.textContent="화면을 누르면 마우스 잠금 · 클릭 = 쏘기 · WASD 이동 · 스페이스 = 점프 · Shift = 슬라이드 · Esc = 풀기"; setTimeout(()=>{ eHint.style.display="none"; }, 9000); }
    else { eHint.innerHTML="왼쪽 = 움직이기 · 오른쪽 끌기 = 둘러보기 · 💦 누른 채 끌면 조준"; setTimeout(()=>{ eHint.style.display="none"; }, 7000); } }
  fireIc(); drawLadder(); drawBoard();

  /* ════ (v599) 아레나 메뉴 화면 — 뒤에서 맵이 돌고 가운데 내 캐릭터 · 혼자 / 같이 / 맵 / 설정 / 무기 / 기록 ════ */
  const SENS=[.45,.7,1,1.35,1.8], FOVA=[-8,0,10], INTRO=2.4, DFN={easy:"🐣 쉬움", normal:"🙂 보통", hard:"🔥 어려움"};
  const WPD=["처음 무기 · 한 방 = 물 ⅓","두 손으로 빠르게 쏴요","가까이서 쫙! 멀면 약해요","누르고 있으면 계속 나가요","꾹 눌러 조준 → 떼면 한 방","던지면 펑! 둘레가 다 젖어요","가까이 있는 친구를 밀어내요","마지막! 가까이서 한 방 = 우승"];
  let introT=0, introSt=0, orbA=.5, padFx=0, cardK="";
  const cFromP=new V3(), cFromQ=new THREE.Quaternion(), _cP=new V3(), _cQ=new THREE.Quaternion();
  const SHOW=new THREE.Group(); scene.add(SHOW); let showC=null;
  try{ showC=buildAvatar(api.av||{}); showC.t=0; showC.blinkT=2; showC.act="idle"; showC.g.scale.setScalar(AVK); SHOW.add(showC.g); showC.g.traverse(m=>{ if(m.isMesh) m.castShadow=!api.low; });
    if(showC.armR){ const gg=new THREE.Group(); showC.armR.add(gg); gg.position.set(0,-.2,0); gg.scale.setScalar(.7); gunModel(gg, 0, true); SHOW.userData.gun=gg; } }catch(e){ showC=null; }
  function placeShow(){ const s=MAPS[MAPK].show; SHOW.position.set(s[0],s[1],s[2]); }
  /* 가로 = 캐릭터가 오른쪽 (왼쪽은 메뉴) · 세로 = 캐릭터가 위 (아래는 메뉴) */
  /* 캐릭터는 맵 가운데 쪽을 등지고 섬 · 카메라는 바깥에서 살짝 좌우로 흔들리며 → 뒤로 맵이 보임 */
  const camA=()=>Math.sin(orbA*.9)*.5;
  function menuCam(){ const s=SHOW.position, asp=cam.aspect||1.5, f=50, d=asp>=1.05?5.6:7.4, A=camA(), hy=1.15;
    if(Math.abs(cam.fov-f)>.01){ cam.fov=f; cam.updateProjectionMatrix(); }
    cam.position.set(s.x+Math.sin(A)*d, s.y+hy+.85, s.z+Math.cos(A)*d);
    const hh=Math.tan(f/2*D2R)*d, hw=hh*asp, rx=Math.cos(A), rz=-Math.sin(A), ox=asp>=1.05?-.42*hw:0, oy=asp>=1.05?0:-.4*hh;
    cam.lookAt(s.x+rx*ox, s.y+hy+oy, s.z+rz*ox); cam.updateMatrixWorld(); }
  function menuTick(dt){ orbA+=dt*.16; api.I.lx=api.I.ly=0; menuCam(); VM.visible=false;
    if(showC){ const th=camA()-.35; showC.face=th; showC.moving=false; try{ animChar(showC, dt); }catch(e){} showC.g.rotation.y=th; if(showC.armR) showC.armR.rotation.x=-1.1; }
    padFx-=dt; if(padFx<=0 && PADS.length){ padFx=1.4; const p=PADS[(Math.random()*PADS.length)|0]; burst(new V3(p[0],.2,p[1]), 22, 1.3); } }

  const MU=document.createElement("div"); MU.className="aM"; api.ui.appendChild(MU); MU.addEventListener("pointerdown", e=>e.stopPropagation());
  MU.innerHTML='<div class="aSide"></div><div class="aMe"></div><div class="aVs"></div>';
  const CW=document.createElement("div"); CW.className="aCardW"; CW.innerHTML='<div class="aCard"></div>'; api.ui.appendChild(CW); CW.addEventListener("pointerdown", e=>e.stopPropagation()); const CD=CW.firstChild;
  const PZ=document.createElement("button"); PZ.className="aPzB"; PZ.textContent="☰ 메뉴"; api.ui.appendChild(PZ); PZ.addEventListener("pointerdown", e=>e.stopPropagation());
  PZ.onclick=()=>{ try{ if(document.pointerLockElement) document.exitPointerLock(); }catch(e){} card("pz"); };
  function menuUI(m){ const U=api.ui; U.classList.toggle("aMenuOn", m!=="play"); U.classList.toggle("aIntro", m==="intro"); U.classList.toggle("aRoom", m==="room"); api.menu=m!=="play";
    SHOW.visible=m==="main" || m==="room"; if(m==="main") drawSide(); if(m!=="main" && cardK!=="pz") closeCard(); }
  function drawSide(){ const left=MG.payLeft("arena");
    MU.querySelector(".aSide").innerHTML='<div class="aLogo"><b>물총 아레나</b><br><span>💦 한 명 적실 때마다 다음 물총 · 8단계</span></div>'+
      '<button class="aBig solo" data-c="solo"><span>▶ 혼자 하기</span><small>봇 5명이랑 · '+DFN[SET.diff]+'</small></button>'+
      '<button class="aBig co" data-c="co"><span>👫 친구랑 같이</span><small>최대 6명 · 빈자리는 봇이 채워요</small></button>'+
      '<div class="aMaps">'+MAPL.map(k=>'<button data-m="'+k+'" class="'+(k===MAPK?"on":"")+'"><i>'+MAPS[k].ic+'</i>'+MAPS[k].nm+'</button>').join("")+'</div>'+
      '<div class="aRow"><button data-c="set">⚙<small>설정</small></button><button data-c="wp">🔫<small>무기</small></button><button data-c="rec">🏆<small>기록</small></button><button data-c="out">🏝<small>섬으로</small></button></div>';
    MU.querySelector(".aMe").innerHTML='<b>⭐ '+esc(me.nm)+'</b><small>'+(left>0?'오늘 🪙 상 '+left+'판 남음':'오늘 🪙 상 다 받았어요')+'</small>'; }
  MU.addEventListener("click", e=>{ const b=e.target.closest("button"); if(!b || phase!=="menu") return; try{ api.sfx.tick(); }catch(_){}
    if(b.dataset.m){ SET.map=b.dataset.m; saveSet(); setMap(SET.map); drawSide(); return; }
    const c=b.dataset.c; if(c==="solo") card("solo"); else if(c==="co") goCo(); else if(c==="set") card("set"); else if(c==="wp") card("wp"); else if(c==="rec") card("rec"); else if(c==="out") MG.exit(); });
  function closeCard(){ CW.classList.remove("on"); cardK=""; if(phase==="play" && !CO) paused=false; }
  CW.addEventListener("click", e=>{ if(e.target===CW) closeCard(); });
  const seg=(k, vals)=>'<div class="aSeg">'+vals.map(([v,t])=>'<button data-s="'+k+'" data-v="'+v+'" class="'+(String(SET[k])===String(v)?"on":"")+'">'+t+'</button>').join("")+'</div>';
  const row=(t, h)=>'<div class="aSet"><span>'+t+'</span>'+h+'</div>';
  function card(k){ cardK=k; let h='<button class="x" data-x="1" aria-label="닫기">✕</button>';
    if(k==="solo") h+='<h3>▶ 혼자 하기</h3><div class="sub2">봇 5명과 대결 · '+MAPS[MAPK].ic+' '+MAPS[MAPK].nm+'</div>'+row('🤖 봇 실력', seg("diff",[["easy","🐣 쉬움"],["normal","🙂 보통"],["hard","🔥 어려움"]]))+'<button class="aGo" data-go="solo">▶ 시작!</button>';
    else if(k==="set") h+='<h3>⚙ 설정</h3>'+row('👀 둘러보기', seg("sens",[[1,"1"],[2,"2"],[3,"3"],[4,"4"],[5,"5"]]))+row('🎯 조준 도움', seg("aim",[[0,"끄기"],[1,"조금"],[2,"많이"]]))+
      row('🔫 자동 쏘기', seg("auto",[[0,"끄기"],[1,"켜기"]]))+row('🔭 시야', seg("fov",[[0,"좁게"],[1,"보통"],[2,"넓게"]]))+row('🔘 버튼 크기', seg("btn",[[0,"작게"],[1,"보통"],[2,"크게"]]))+row('🔊 소리', seg("vol",[[0,"끄기"],[1,"작게"],[2,"크게"]]))+
      '<div class="sub2">이 기기에 저장돼요 · 자동 쏘기 = 터치에서 조준만 맞추면 쏴요</div>'+(phase==="play"?'<button class="aGo" data-go="pz">← 돌아가기</button>':'');
    else if(k==="wp") h+='<h3>🔫 무기 8단계</h3><div class="sub2">한 명을 흠뻑 적시면 다음 무기 · 마지막 🔨 로 맞히면 우승</div><div class="aWpL">'+WP.map((w,i)=>'<div><i>'+w.ic+'</i><span><b>'+(i+1)+'. '+w.nm+'</b>'+WPD[i]+'</span></div>').join("")+'</div>';
    else if(k==="rec"){ const r=MG.rec(), b=r.b.arena||{}, t=r.t.arena||{};
      h+='<h3>🏆 내 기록</h3><div class="aRec">'+[["🏆 우승",(t.win|0)+"번"],["💦 모두 적신 수",(t.kills|0)+"명"],["🎯 한 판 최고",(b.kill|0)+"명"],["🪜 최고 단계",(b.wi|0)+" / 8"],["⚡ 가장 빠른 우승",b.fast?b.fast+"초":"—"],["🪙 오늘 상",MG.payLeft("arena")+"판 남음"]].map(x=>'<div>'+x[0]+'<b>'+x[1]+'</b></div>').join("")+'</div>'; }
    else if(k==="pz") h+='<h3>⏸ 메뉴</h3>'+(CO?'<div class="sub2">같이 하는 중에는 게임이 멈추지 않아요</div>':'<div class="sub2">게임이 잠깐 멈췄어요</div>')+'<button class="aGo" data-go="resume">▶ 계속하기</button><div class="aRow2"><button data-go="set">⚙ 설정</button><button data-go="menu">💦 아레나 메뉴</button><button data-go="out">🏝 섬으로</button></div>';
    CD.innerHTML=h; CW.classList.add("on"); if(phase==="play" && !CO) paused=true; }
  CD.addEventListener("click", e=>{ const b=e.target.closest("button"); if(!b) return; try{ api.sfx.tick(); }catch(_){}
    if(b.dataset.x){ closeCard(); return; }
    if(b.dataset.s){ const k=b.dataset.s, v=b.dataset.v; SET[k]=k==="diff"?v:+v; saveSet(); applySet(); card(cardK); if(k==="vol") try{ api.sfx.up(); }catch(_){} return; }
    const g=b.dataset.go; if(g==="solo"){ closeCard(); beginSolo(); } else if(g==="resume") closeCard(); else if(g==="set") card("set"); else if(g==="pz") card("pz");
    else if(g==="menu"){ closeCard(); api.restart({}); } else if(g==="out"){ closeCard(); MG.exit(); } });
  function applySet(){ const U=api.ui; U.classList.remove("aBs0","aBs1","aBs2"); U.classList.add("aBs"+(SET.btn|0)); try{ api.sfx.vol=[0,.45,1][SET.vol|0]; }catch(e){} }
  /* 시작 연출: 누구랑 붙는지 · 맵 이름 → 하늘에서 내 눈으로 → 3·2·1 */
  function intro(st){ phase="intro"; introT=0; introSt=st; time.cd=1e9; cFromP.copy(cam.position); cFromQ.copy(cam.quaternion); fov=cam.fov; menuUI("intro");
    const L=ACT.slice(); MU.querySelector(".aVs").innerHTML='<h2>💦 '+L.length+'명 대결!</h2><div class="mp">'+MAPS[MAPK].ic+' '+MAPS[MAPK].nm+'</div><div class="ps">'+L.map((a,i)=>'<span class="'+(a.me?"me":a.net?"fr":"")+'" style="animation-delay:'+(.2+i*.1).toFixed(2)+'s">'+(a.me?"⭐ ":a.net?"👫 ":"🤖 ")+esc(a.nm)+'</span>').join("")+'</div><div class="rl">🔨 뿅망치로 먼저 맞히면 우승!</div>';
    try{ api.sfx.up(); }catch(e){} }

  /* ════ 나 ════ */
  let camY=0, fov=76, zoom=0, paused=false, roll=0, deadCam=0;
  ACT.forEach(spawn); me.prot=0; ACT.forEach(a=>{ if(a.bot) a.prot=0; });
  function myTick(dt){ const I=api.I;
    /* 둘러보기 — 터치는 적 위에서 살짝 느려짐 */
    let sens=(I.lock||I.mouse&&!I.touch ? .0023 : .0058)*SENS[Math.max(0,Math.min(4,(SET.sens|0)-1))]; if(zoom>.5) sens*=.4;
    if(I.touch && me.alive && SET.aim){ const e=eyeOf(me), d=dirOf(me.yaw, me.pitch); if(assist(me, e, d, 60, 5)) sens*=SET.aim>1?.55:.78; }
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
    if(SET.auto && I.touch && !want && W.t!=="snipe" && W.t!=="melee"){ const as=assist(me, e, d, W.rng, 2.4); if(as) want=1; }
    if(W.t==="snipe"){ if(I.fire){ me.hold+=dt; zoom=Math.min(1, zoom+dt*5); } else { if(me.hold>.12 && me.cd<=0 && time.cd<=0){ fire(me, e, d, I.touch && SET.aim?(o,dd,rg)=>assist(me,o,dd,rg,SET.aim>1?1.8:1):null); } me.hold=0; zoom=Math.max(0, zoom-dt*6); } }
    else if(W.t==="melee"){ if(want && me.cd<=0 && time.cd<=0) fire(me, e, d); }
    else if(want && me.cd<=0 && time.cd<=0){ fire(me, e, d, !SET.aim?null:I.touch?(o,dd,rg)=>assist(me,o,dd,rg,SET.aim>1?3.4:1.8):I.mouse?(o,dd,rg)=>assist(me,o,dd,rg,.9):null); }
    /* 마르기 */
    if(time.t-me.lastHit>3.2) me.soak=Math.max(0, me.soak-34*dt); }
  function botsTick(dt){ for(const a of ACT){ if(a.net || (a.bot && a.rb)){ netVis(a, dt); continue; } if(!a.bot) continue; if(!a.alive){ a.resp-=dt; a.dead+=dt; if(a.c){ a.c.g.rotation.x=-Math.min(1.4, a.dead*5); a.c.g.position.y=Math.max(-.3, -a.dead*.4); } if(a.bk){ const B=a.bk; B.g.rotation.x=-Math.min(1.5, a.dead*6); B.g.position.y=0; B.armL.rotation.set(-2.6,0,.3); B.armR.rotation.set(-2.6,0,-.3); B.legL.rotation.x=.3; B.legR.rotation.x=-.3; } if(a.dead>1.0) a.G.visible=false; if(a.resp<=0) spawn(a); continue; }
      a.prot=Math.max(0,a.prot-dt); if(time.cd>0){ a.G.position.set(a.p.x,a.p.y,a.p.z); continue; } botTick(a, dt); if(time.t-a.lastHit>3.2) a.soak=Math.max(0, a.soak-30*dt); } }

  /* ════ 판 끝 ════ */
  function win(w){ if(time.over) return; time.over=true; finishMatch(w); }
  function declareWin(w){ if(CO && NETR){ NETR.put("h/win", {n:w.nm, c:idOf(w)}); } win(w); }
  function finishMatch(w){ if(w && !ACT.includes(w)) w=ACT.find(a=>a.nm===w.nm)||null; const L=ACT.slice().sort((x,y)=>(y===w)-(x===w) || y.wi-x.wi || y.kills-x.kills), rank=L.indexOf(me)+1, won=L[0]===me;
    api.msg(won?'🏆 우승!':w?'🏁 '+esc(w.nm)+' 우승!':'⏰ 시간 끝!', 1800);
    setTimeout(()=>{ try{ if(document.pointerLockElement) document.exitPointerLock(); }catch(e){}
      if(gone) return; const coins=won?15:rank<=3?8:5, b0=(()=>{ try{ return Object.assign({}, MG.rec().b.arena||{}); }catch(e){ return {}; } })();
      const got=PUI.award(api, {title:won?'🏆 '+esc(me.nm)+' 우승!':rank<=3?'🎉 '+rank+'등!':'💦 '+rank+'등', sub:'흠뻑 적신 수 '+me.kills+' · 단계 '+(me.wi+1)+'/'+WP.length, rows:null, coins, again:{mode:CO?"co":"solo", quick:1},
        upd:(b,t)=>{ t.kills=(t.kills|0)+me.kills; if(won){ t.win=(t.win|0)+1; if(!b.fast || time.t<b.fast) b.fast=Math.round(time.t); } if(me.kills>(b.kill|0)) b.kill=me.kills; if(me.wi+1>(b.wi|0)) b.wi=me.wi+1; }});
      let left=3; try{ left=MG.payLeft("arena"); }catch(e){}
      root.classList.add("aEnd"); eKill.classList.remove("on");
      PUI.result(hud, {res:rank<=3?"win":"lose", stars:won?3:rank===2?2:rank===3?1:0, title:won?"우승!":rank+"등!", av:api.av,
        sub:MAPS[MAPK].ic+" "+MAPS[MAPK].nm+(won?" · "+Math.round(time.t)+"초 만에":w?" · "+esc(w.nm)+" 우승":" · 시간 끝"),
        rewards:[["🪙", got>0?"+"+got:"0", got>0?"코인":"오늘 상 끝"], ["💦", me.kills, "흠뻑 적신 수", me.kills>(b0.kill|0) && me.kills>0], [WP[me.wi].ic, (me.wi+1)+" / "+WP.length, "무기 단계", me.wi+1>(b0.wi|0)]],
        extra:'<div class="puRank">'+L.slice(0,6).map((a,i)=>'<div class="'+(a.me?"me":"")+'"><span>'+(i<3?["🥇","🥈","🥉"][i]:(i+1)+".")+' '+esc((a.net?"👫 ":"")+a.nm)+'</span><b>'+WP[a.wi].ic+' '+(a.wi+1)+' · 💦'+a.kills+'</b></div>').join("")+'</div>',
        prog:{t:"오늘 🪙 상 "+(3-left)+" / 3판", v:(3-left)/3},
        onAgain:()=>api.restart({mode:CO?"co":"solo", quick:1}), onMenu:()=>api.restart({})}); }, 1700); }

  /* ════ 한 장면 ════ */
  function tick(dt){ if(paused && !CO) return; time.t+=dt; if(MAPG && MAPG.userData.sky) MAPG.userData.sky.rotation.y+=dt*.008;
    if(NETR){ NETR.tick(dt); netApply(dt); if(time.st) time.left=Math.max(0, Math.min(MATCH, MATCH-(NETR.now()-time.st)/1000));
      if(phase==="room" && NETR && NETR.d && NETR.d.h && NETR.d.h.map && NETR.d.h.map!==MAPK) setMap(NETR.d.h.map); }   /* 친구 방에 들어가면 그 방 맵이 뒤에 보임 */
    if(phase==="menu" || phase==="room"){ menuTick(dt); fxTick(dt); return; }
    if(phase==="intro"){ introT+=dt; api.I.lx=api.I.ly=0; const now=NETR?NETR.now():0, done=introSt?now>=introSt+INTRO*1000:introT>=INTRO;
      if(done){ phase="play"; api.menu=false; menuUI("play"); time.cd=introSt?Math.max(.1,(introSt+INTRO*1000+3000-now)/1000):3.2; showHint(); } }
    else if(time.cd>0){ const c0=Math.ceil(time.cd); time.cd-=dt; const c1=Math.ceil(time.cd); eCnt.textContent=time.cd>0?c1:"GO!"; if(c1!==c0) api.sfx.tick(); if(time.cd<=0){ api.sfx.up(); setTimeout(()=>{ eCnt.textContent=""; }, 600); } }
    else if(!time.over){ if(!CO) time.left-=dt; if(time.left<=0){ time.left=0; time.over=true; finishMatch(null); } }
    if(phase==="play") myTick(dt); botsTick(dt);
    fxTick(dt);
    for(const f of FEED) f.t-=dt; if(FEED.length && FEED[FEED.length-1].t<=0){ FEED.pop(); drawFeed(); }
    /* 카메라 */
    const eyeH=me.alive?(me.sl?EYES:EYE):.35, ty=me.p.y+eyeH; if(Math.abs(ty-camY)<.7 && me.onG) camY+=(ty-camY)*Math.min(1,dt*16); else camY=ty;
    cam.position.set(me.p.x, camY, me.p.z); const hs=Math.hypot(me.v.x,me.v.z);
    const asp=cam.aspect||1.5, base=(asp>=1?76:Math.min(100, 76+(1-asp)*55))+FOVA[SET.fov|0];   /* 세로 화면(아이패드 세로)은 위아래 시야를 넓혀 옆이 너무 좁지 않게 */
    const tf=(base+Math.max(0,Math.min(12,(hs-MAXS)*1.4)))*(1-zoom*.55); fov+=(tf-fov)*Math.min(1,dt*8); if(Math.abs(cam.fov-fov)>.05){ cam.fov=fov; cam.updateProjectionMatrix(); }
    roll+=((me.sl?-.06:0)-roll)*Math.min(1,dt*8); cam.rotation.set(me.pitch-deadCam*.5, me.yaw, roll+deadCam*.35);
    cam.updateMatrixWorld();
    let introK=1; if(phase==="intro"){ const k=Math.min(1, introT/(INTRO*.85)); introK=k*k*(3-2*k); _cP.copy(cam.position); _cQ.copy(cam.quaternion); cam.position.lerpVectors(cFromP, _cP, introK); cam.quaternion.copy(cFromQ).slerp(_cQ, introK); cam.updateMatrixWorld(); }
    /* 내 화면 총 흔들림 · 반동 */
    vmA.bob+=dt*(me.onG && hs>1 ? hs*1.05 : 0); vmA.kick=Math.max(0, vmA.kick-dt*7); vmA.sw=Math.min(1, vmA.sw+dt*4); vmA.swing=Math.max(0, vmA.swing-dt*3.2);
    const bx2=Math.sin(vmA.bob)*.012*Math.min(1,hs/6), by2=Math.abs(Math.cos(vmA.bob))*.014*Math.min(1,hs/6);
    VM.position.set(.24+bx2-zoom*.24, -.22-by2-(1-vmA.sw)*.35+(me.onG?0:.015)-(zoom*.05), -.5+vmA.kick*.05); VM.rotation.set(.04+vmA.kick*.12+vmA.swing*1.1-(1-vmA.sw)*.6, .2-vmA.swing*.5, -.06+vmA.swing*.4);
    if(VMG.userData.twin) VMG.userData.twin.position.z=(vmA.side<0?vmA.kick*.06:0); VMG.position.z=vmA.side>0?0:-vmA.kick*.0;
    VM.visible=me.alive && zoom<.9 && introK>.95;
    /* 글자 */
    hitT=Math.max(0,hitT-dt); eHm.style.opacity=hitT>0?1:0; eHm.classList.toggle("hd", hitHead);
    hurtT=Math.max(0,hurtT-dt); eDir.style.opacity=hurtT>0?Math.min(1,hurtT*2):0; if(hurtT>0) eDir.style.transform="rotate("+(-(hurtA-me.yaw)+Math.PI)+"rad)";
    eWet.style.opacity=Math.min(1, me.soak/85); eSoak.style.width=Math.min(100,me.soak)+"%"; eDead.style.opacity=me.alive?0:1;
    const W=WP[me.wi], spr=(W.spr||0)+(me.onG?0:1.5)+Math.min(2,hs/6); const g=8+spr*3; eCx.querySelectorAll(".h")[0].style.left=(-10-g)+"px"; eCx.querySelectorAll(".h")[1].style.left=g+"px"; eCx.querySelectorAll(".v")[0].style.top=(-10-g)+"px"; eCx.querySelectorAll(".v")[1].style.top=g+"px"; eCx.style.opacity=zoom>.5?0:1;
    const s=Math.max(0,Math.ceil(time.left)); if(s!==eClk._s){ eClk._s=s; eClk.textContent=Math.floor(s/60)+":"+String(s%60).padStart(2,"0"); eClk.classList.toggle("low", s<=30 && !time.over); }
    if(killT>0){ killT-=dt; if(killT<=0) eKill.classList.remove("on"); }
    bdT-=dt; if(bdT<=0){ bdT=.5; drawBoard(); } }
  /* 처음 화면 = 메뉴 (결과의 「한 판 더」 = 바로 시작) */
  applySet(); placeShow(); menuUI("main"); menuCam();
  if(api.opt.quick){ if(api.opt.mode==="co") goCo(); else beginSolo(); }
  function render(rn){ MG.draw(scene, cam); const va=cam.aspect||1.5, vf=va>=1.3?58:Math.min(92, 58+(1.3-va)*52); if(vmC.aspect!==va || vmC.fov!==vf){ vmC.aspect=va; vmC.fov=vf; vmC.updateProjectionMatrix(); } rn.autoClear=false; rn.clearDepth(); rn.render(vmS, vmC); rn.autoClear=true; }
  function dispose(){ gone=true; try{ api.sfx.vol=1; }catch(e){} if(NETR){ try{ NETR.dispose(); }catch(e){} } if(MAPG) MAPG.traverse(o=>{ if(o.geometry) o.geometry.dispose(); }); disp.forEach(x=>{ try{ x.dispose(); }catch(e){} }); Object.values(GM).forEach(m=>{ try{ m.dispose(); }catch(e){} }); BAL.forEach(b=>scene.remove(b.m)); }
  return {scene, cam, tick, render, dispose, pause:(v)=>{ paused=!!v; }, vmSet, VM, me, ACT, PEER, get NETR(){ return NETR; }, WP, time, BOX, fire, hurt, spawn, PADS, SPAWN, moveAct, up, win, path, sees, get D(){ return D; }, vmA, get zoom(){ return zoom; },
    get phase(){ return phase; }, beginSolo, goCo, setMap, get MAPK(){ return MAPK; }, MAPS, MAPL, SET, applySet, menuUI, card, HT, BL, NC}; }

MG.reg("arena", {ic:"💦", nm:"물총 아레나", tag:"1인칭 · 아레나 무브 · 무기 8단계", bg:"linear-gradient(135deg,#7fd3ff,#2f7fff)", big:"🔫💦",
  how:[["🎯","한 명을 흠뻑 적실 때마다 <b>다음 무기</b>로 (8단계)"],["🔨","마지막 <b>뿅망치</b>로 맞히면 우승! · 5분이 지나면 가장 멀리 간 사람"],["🛝","달리다 <b>슬라이드</b> → 빨라짐 · 슬라이드 중 점프 = 속도 그대로"],["🐇","땅에 닿는 순간 점프(점프 꾹) = 속도 유지 · 💧 분수 발판 = 높이 점프"],["👐","왼손 = 움직이기 · 오른손 = 끌어서 둘러보기 · 💦 누른 채 끌면 조준"]],
  menu:true,   /* (v599) 탑 → 바로 아레나 메뉴 화면 (혼자 · 같이 · 맵 · 설정 · 무기 · 기록) */
  payTxt:"우승 🪙15 · 3등 안 🪙8 · 참가 🪙5",
  bestTxt:(b,t)=>'🏆 우승 '+(t.win|0)+'번 · 💦 모두 '+(t.kills|0)+'명'+(b.fast?' · 가장 빠른 우승 '+b.fast+'초':'')+(b.wi?' · 최고 '+b.wi+'단계':''),
  ui:{look:true, btns:[{b:"fire", ic:"🔫"}, {b:"jump", ic:"점프"}, {b:"slide", ic:"슬라이드"}]},
  start});
})();
