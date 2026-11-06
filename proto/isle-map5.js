/* (v607~) 🏝 새 섬 설계도 5판 — 「⚓ 항구 섬마을」 (시안 2판 = A 항구 도시 + C 섬마을 군도 + 텃밭 섬)
   사용자(11-06): 「도시가 길도 없고 도시도 없어서 · 도심 속에 마트가 있어야 해」 → 「꼭 땅을 저 원형으로 만들 필요 없어 · 시안 3개」 → 「A+C 를 합쳐서 조율」
     → 「농장 섬 밭으로 하자 · 대신 애들이 가깝게 갈 수 있게」 → 「시작하자」
   · 아이들이 쓰는 마을은 그대로 두고 시험판으로만 켬: ?v5=1 (기기에 기억) · ?v5=0 끔
   · 좌표 = 광장(시계탑 분수) 기준 · 북 = -z · ISLE_MAP(4판)과 같은 모양의 값을 돌려줌 → isle.js 가 그대로 짓고, 섬(isles)·다리(links)·큰길(asph)만 더 읽음
   · 가운데 = 초승달 항구 섬: 만 북쪽 해안에 도심(북쪽 가게 거리) · 서쪽 팔 주택가 1~3동 · 동쪽 팔 4~6동 · 뒤 언덕 배움 언덕
   · 둘레 섬 = 🌾 텃밭(서, 주택가 바로 옆 다리 2) · 🍄🌸 버섯·꽃(남서) · 🏔 광산(북) · 🎣 호수(북동) · 🎡 놀이(동) · 🏖 등대 모래섬(만 한가운데, 바다 다리) · 🌫 안개(잠김) · 🏝 비밀 */
(function(){
  /* (v610) 사용자: 「배포를 해서 보여 줘야 · 예전 섬은 이미 없는 거잖아」 → 새 섬이 기본 · ?v5=0 (기기에 기억) 이면 옛 섬 · ?v5=1 다시 새 섬 */
  const V5=(()=>{ try{ const q=location.search; if(/[?&]v5=0/.test(q)){ localStorage.setItem("hyeng_isle_v5","0"); return false; }
    if(/[?&]v5=1/.test(q)){ localStorage.setItem("hyeng_isle_v5","1"); return true; } return localStorage.getItem("hyeng_isle_v5")!=="0"; }catch(e){ return true; } })();
  if(typeof window!=="undefined") window.ISLE_V5=V5;
  if(!V5) return;
  /* ── 곡선 (4판과 같음) ── */
  function cr(P, n){ const out=[]; for(let i=0;i<P.length-1;i++){ const p0=P[Math.max(0,i-1)], p1=P[i], p2=P[i+1], p3=P[Math.min(P.length-1,i+2)];
      for(let k=0;k<n;k++){ const t=k/n, t2=t*t, t3=t2*t; out.push([0,1].map(j=>.5*((2*p1[j])+(-p0[j]+p2[j])*t+(2*p0[j]-5*p1[j]+4*p2[j]-p3[j])*t2+(-p0[j]+3*p1[j]-3*p2[j]+p3[j])*t3))); } }
    out.push(P[P.length-1].slice()); return out; }
  function crc(P, n){ const L=P.length, out=[]; for(let i=0;i<L;i++){ const p0=P[(i-1+L)%L], p1=P[i], p2=P[(i+1)%L], p3=P[(i+2)%L];
      for(let k=0;k<n;k++){ const t=k/n, t2=t*t, t3=t2*t; out.push([0,1].map(j=>.5*((2*p1[j])+(-p0[j]+p2[j])*t+(2*p0[j]-5*p1[j]+4*p2[j]-p3[j])*t2+(-p0[j]+3*p1[j]-3*p2[j]+p3[j])*t3))); } } return out; }
  function arc(Q){ const L=[0]; for(let i=1;i<Q.length;i++) L.push(L[i-1]+Math.hypot(Q[i][0]-Q[i-1][0],Q[i][1]-Q[i-1][1])); return L; }
  function at(Q, L, s){ let i=1; while(i<L.length-1 && L[i]<s) i++; const a=Q[i-1], b=Q[i], f=Math.max(0,Math.min(1,(s-L[i-1])/((L[i]-L[i-1])||1)));
    const x=a[0]+(b[0]-a[0])*f, z=a[1]+(b[1]-a[1])*f, d=Math.hypot(b[0]-a[0],b[1]-a[1])||1; return {x, z, tx:(b[0]-a[0])/d, tz:(b[1]-a[1])/d}; }
  const curve=P=>{ const Q=cr(P,10); return {Q, L:arc(Q)}; };
  function inPoly(x,z,P){ let c=false; for(let i=0,j=P.length-1;i<P.length;j=i++){ const a=P[i], b=P[j]; if(((a[1]>z)!==(b[1]>z)) && (x<(b[0]-a[0])*(z-a[1])/(b[1]-a[1])+a[0])) c=!c; } return c; }

  /* ── 가운데 초승달 섬 (만 = 남쪽) ── */
  const island={cx:0, cz:-12, ax:64, az:60, s:1.3};
  const MAINP=[[-74,-6],[-68,-36],[-50,-56],[-20,-66],[16,-66],[46,-56],[64,-34],[71,-6],[69,22],[63,44],[51,60],[39,58],[31,44],[25,29],[13,19],[-2,17],[-17,19],[-29,29],[-35,44],[-43,58],[-55,60],[-67,44],[-73,22]];
  const SM=crc(MAINP,8);
  /* 가장자리 = 섬 가운데에서 그 방향으로 처음 만나는 물가 (각도 1440칸 표) */
  const EDGE=(()=>{ const n=1440, R=new Float32Array(n); for(let i=0;i<n;i++){ const a=i/n*Math.PI*2, dx=Math.cos(a), dz=Math.sin(a); let best=1e9;
      for(let j=0;j<SM.length;j++){ const p=SM[j], q=SM[(j+1)%SM.length], ex=q[0]-p[0], ez=q[1]-p[1], wx=p[0]-island.cx, wz=p[1]-island.cz, den=dx*ez-dz*ex; if(Math.abs(den)<1e-9) continue;
        const t=(wx*ez-wz*ex)/den, u=(wx*dz-wz*dx)/den; if(t>0 && u>=0 && u<=1 && t<best) best=t; }
      R[i]=best<1e9?best:40; } return R; })();
  function edge(a){ const n=EDGE.length; let f=((a/(Math.PI*2))%1+1)%1*n; const i=Math.floor(f)%n, j=(i+1)%n; f-=Math.floor(f); return EDGE[i]*(1-f)+EDGE[j]*f; }
  function inside(x,z,m){ const dx=x-island.cx, dz=z-island.cz, a=Math.atan2(dz,dx); return Math.hypot(dx,dz) < edge(a)-(m||0); }

  /* ── 둘레 섬 (매끈한 둥근 땅 · R = 반지름) ── */
  const isles=[
    {k:"farm",  nm:"🌾 텃밭 섬",     cx:-108, cz:8,   R:24, s:2.1},
    {k:"vil",   nm:"🍄🌸 버섯·꽃 섬", cx:-82,  cz:66,  R:20, s:3.4},
    {k:"adv",   nm:"🏔 광산 섬",     cx:0,    cz:-96, R:23, s:.7},
    {k:"lake",  nm:"🎣 호수 섬",     cx:86,   cz:-74, R:22, s:5.2, lake:1},
    {k:"park",  nm:"🎡 놀이 섬",     cx:108,  cz:6,   R:27, s:4.4},
    {k:"beach", nm:"🏖 등대 모래섬",  cx:0,    cz:74,  R:10, s:1.9},
    {k:"fog",   nm:"🌫 안개 섬",     cx:-78,  cz:-92, R:12, s:6.1, lock:1},
    {k:"secret",nm:"🏝 비밀 섬",     cx:100,  cz:82,  R:8,  s:2.7, lock:1},
  ];
  /* 다리 [x1,z1,x2,z2,폭] — 양 끝이 땅 안쪽 1.5칸 */
  const links=[
    [-70,4,-87,4,3.0], [-68,18,-89,18,2.6],       /* 주택가 → 🌾 텃밭 섬 (넓은 다리 2) */
    [-58,48.4,-68,56,2.4],                       /* 서쪽 팔 끝 → 🍄 버섯·꽃 섬 · (v608) 다리는 물 위만 (땅 위로 난간이 보이던 것) */
    [0,-63,0,-75,2.8],                           /* 북쪽 → 🏔 광산 섬 */
    [48,-52,69.5,-64.4,2.4],                     /* 북동 → 🎣 호수 섬 (끝을 섬 안으로) */
    [68,4,84,4,3.0],                             /* 동쪽 → 🎡 놀이 섬 */
    [0,15,0,66,2.2],                             /* 부두 → 🏖 등대 모래섬 (바다 다리) */
  ];
  const broken=[[-22,-96,-58,-93]];               /* 🌫 안개 섬 — 부서진 다리 (못 감) */

  const plaza={x:0, z:0, r:7.5};
  /* 길 — asph = 아스팔트 큰길(회색 · 가운데 노란 점선) · 없으면 흙길 */
  const roads={
    market:{w:3.0, asph:1, p:[[0,-7.5],[0,-16],[0,-24],[0,-32],[0,-40],[0,-47]]},     /* 🏙 도심 가게 거리 (북쪽) */
    east:  {w:2.8, asph:1, p:[[7.5,0],[18,0],[31,0],[46,1],[60,2],[70,4]]},
    west:  {w:2.8, asph:1, p:[[-7.5,0],[-18,0],[-31,0],[-46,1],[-60,2],[-71,4]]},
    bay:   {w:2.4, asph:1, p:[[-31,10],[-17,11.5],[0,10.5],[17,11.5],[31,10]]},    /* 만 따라 해안길 · 부두 */
    pier:  {w:2.2, asph:1, p:[[0,7.5],[0,10.5],[0,15]]},
    warm:  {w:2.4, asph:1, p:[[-31,0],[-31.5,10],[-32,22],[-33,36],[-46,42],[-57,48]]},       /* 서쪽 팔 큰길 → 버섯 섬 다리 */
    earm:  {w:2.4, asph:1, p:[[31,0],[31.5,10],[32,22],[33,34]]},                    /* 동쪽 팔 큰길 (4~6동) */
    north: {w:2.6, asph:1, p:[[0,-47],[0,-56],[0,-64]]},                             /* → 광산 섬 다리 */
    ne:    {w:2.4, asph:1, p:[[0,-47],[16,-49],[32,-50],[48,-52]]},                  /* → 호수 섬 다리 */
    ave2:  {w:2.6, asph:1, p:[[24,0],[24,-12],[24,-25.3],[24,-38],[24,-49.6]]},      /* (3단계) 🏙 시내 2번가 (남북) */
    cross: {w:2.6, asph:1, p:[[0,-25.3],[12,-25.3],[24,-25.3],[40,-25.3],[55,-25.3]]}, /* (3단계) 🏙 시내 가로길 (동서) · 끝 = 바다 전망 */
    farm2: {w:1.5, lane:1, p:[[-59.5,19.5],[-64,18.6],[-69,18]]},                  /* 2번 다리 앞 = 2동 해바라기길 끝이 그대로 다리로 (v613: 아스팔트 토막이 골목과 안 맞던 것) */
    school:{w:2.2, p:[[0,-26],[-10,-28],[-20,-32]]},                                 /* 배움 언덕 (흙길) */
    mine:  {w:2.0, p:[[0,-75],[-1,-80],[-2,-83]]},
    farmIn:{w:2.2, p:[[-87,4],[-100,4],[-122,4]]}, farmIn2:{w:2.0, p:[[-89,18],[-122,18]]}, farmIn3:{w:2.0, p:[[-92,-10],[-122,-10]]}, farmV:{w:2.0, p:[[-92,-12],[-92,22]]},
    lakeIn:{w:2.0, p:[[69,-64],[76,-68]]},
    vil:   {w:2.2, p:[[-68,56],[-76,62]]},
    parkIn:{w:2.4, asph:1, p:[[84,4],[89,4],[93.4,4]]},   /* (v608) 놀이 섬 둥근 마당(반지름 15) 안으로는 안 들어감 — 마당 바닥과 길이 겹쳐 계단처럼 깨져 보이던 것 */
    beach: {w:1.8, p:[[0,66],[0,72]]},
  };
  /* 주택가 — 서쪽 팔 1~3동 · 동쪽 팔 4~6동 (예전 땅 번호 그대로 → 내 땅이 저절로 이사) */
  const LOT=2.2, GAP=2.75, OFF=2.15, PER=8;
  const hood=(id,nm,ic,tree,z,side)=>{ const x0=side*32.5; return {id,nm,ic,tree,p:[[x0,z],[x0+side*7,z+.3],[x0+side*14,z],[x0+side*21,z+.3],[x0+side*27,z]],s0:4.8,from:side<0?"warm":"earm"}; };
  const hoods=[hood("1동","벚꽃길","🌸","blossom",8,-1), hood("2동","해바라기길","🌻","sun",19.5,-1), hood("3동","클로버길","🍀","clover",31,-1),
               hood("4동","단풍길","🍁","maple",8,1), hood("5동","바닷가길","🌊","palm",19.5,1), hood("6동","별빛길","⭐","star",30,1)];
  const spots={
    fountain:[0,0], board:[-5.2,-4.6], goal:[5.8,4.4], stage:[-16,-9], camp:[-126.5,11.5], station:[16,-9], post:[10,7], bank:[-10,7],
    market:[0,-28], campus:[-28,-36], school:[-36,-46], library:[-17,-44], museum:[-44,-30],
    lake:{x:90, z:-76, rx:8.5, rz:6}, dock:[79,-70], tower:[126,-10],
    mine:[-2,-86], mountain:[9,-100],
    farm:[-96,11], windmill:[-121.6,-6.2], vil:[-82,68],
    park:{x:108, z:8, r:15}, ox:[100,-4], pg:[116,-4], chest:[104,20],
    mgArena:[98,16], mgGrid:[118,16],
  };
  /* (3단계) 🏙 시내 건물 블록 — 길 쪽(f: N/S/E/W)으로 건물 앞이 봄 · h = 높이 단계(0 낮음 · 1 보통 · 2 높음) · 블록 안쪽은 뒷마당(나무) */
  const city={pack:"commerce", s:2.5, blocks:[
    {k:"A", x0:7.6,  x1:22.4, z0:-23.6, z1:-14.6, f:["N","E"], h:0},
    {k:"B", x0:25.6, x1:58,   z0:-23.6, z1:-2.8,  f:["S","N","W"], h:1},
    {k:"C", x0:7.6,  x1:22.4, z0:-46.2, z1:-27.0, f:["S","E"], h:1},
    {k:"D", x0:25.6, x1:47,   z0:-46.4, z1:-27.0, f:["S","W","N"], h:2},
    {k:"W1",x0:-12.4,x1:-7.2, z0:-24.6, z1:-12.0, f:["W"], h:0},
    {k:"W2",x0:-12.4,x1:-7.2, z0:-46,   z1:-31.6, f:["W"], h:1},
  ], cross:[[0,-25.3],[24,-25.3],[24,0],[24,-49.6],[0,-47]], view:[57.6,-25.3]};
  /* (4단계) 🌾 텃밭 섬 「내 밭」 — 아이마다 한 자리(5×4 = 20칸, 지금 마당 밭 규칙 그대로) · 흙길 3줄 양옆에 줄지어 (친구 밭이 서로 보임)
     자리 = 길 쪽이 앞 · 처음엔 빈 밭(팻말) → 눌러서 내 밭으로 · 섬 가장자리에 안 걸리는 자리만 */
  const fields=(()=>{ const I=isles[0], C=5, R=4, cell=1.0, out=[]; const lanes=[[-10,1],[4,-1],[4,1],[18,-1],[18,1]];
    lanes.forEach(([lz,sd],li)=>{ for(let j=0;j<5;j++){ const x=-97.6-j*5.8, z=lz+sd*3.7, hw=C*cell/2+.35, hd=R*cell/2+.35;
      const ok=[[x-hw,z-hd],[x+hw,z-hd],[x-hw,z+hd],[x+hw,z+hd]].every(([a,b])=>Math.hypot(a-I.cx,b-I.cz)<I.R*.9);
      if(ok) out.push({id:out.length, x, z, face:sd>0?Math.PI:0, lane:lz}); } });
    return {cols:C, rows:R, cell, slots:out}; })();
  const shops=[["mart","🛒","마트",0x5cc46a],["snack","🍦","간식 가게",0xffb6d1],["clothes","👕","옷 가게",0xff6b6b],["hair","💇","미용실",0xff9ac8],["photo","📸","사진관",0x9b72f0],["pet","🐶","펫 가게",0x7fd36a],["furn","🛋","가구점",0xffc93d],["fish","🐟","생선 가게",0x5aa7ff]];
  const shopS=[6.5,14,21.5,29], SHOP_OFF=4.4;
  /* 가게 자리 — 북쪽 가게 거리 양옆 7곳(마주 봄) + 🐟 생선 가게 = 부두 옆 (낚시 → 바로 팔기) */
  function shopLots(){ const out=[]; for(let k=0;k<7;k++){ const s=shopS[k>>1], z=-7.5-s, sd=k%2?1:-1; out.push({sh:shops[k], x:sd*SHOP_OFF, z, nx:sd, nz:0, rx:0, rz:z}); }
    out.push({sh:shops[7], x:14, z:15.2, nx:0, nz:1, rx:14, rz:11.2}); return out; }
  const zones=[
    {k:"center", nm:"🏙 도심", c:0xd9d4cc, gate:[0,-9.6], poly:[[-12,-48],[12,-48],[24,12],[-24,12]]},
    {k:"campus", nm:"🎓 배움 언덕", c:0x9ec4ff, gate:[-11,-27], poly:[[-13,-50],[-46,-54],[-56,-24],[-15,-20]]},
    {k:"home", nm:"🏘 주택가", c:0xffe08a, gate:[-31,4], poly:[[-72,2],[-29,2],[-30,32],[-38,52],[-56,56],[-68,42],[-72,22]]},
    {k:"home2", nm:"🏘 4~6동", c:0xfff0b8, gate:[31,4], poly:[[29,2],[70,2],[68,22],[62,42],[50,56],[36,52],[29,30]]},
    {k:"farm", nm:"🌾 텃밭 섬", c:0xd8e86a, gate:[-88,4], poly:[[-90,-14],[-100,-26],[-120,-26],[-130,-8],[-128,20],[-114,30],[-94,28],[-88,16]]},
    {k:"lake", nm:"🎣 호수 섬", c:0x7fe0c8, gate:[71.6,-65.6], poly:[[68,-62],[76,-90],[100,-88],[106,-66],[94,-56],[74,-56]]},
    {k:"park", nm:"🎡 놀이 섬", c:0xa0f07a, gate:[85,4], poly:[[86,-14],[104,-20],[126,-16],[130,10],[120,28],[96,28],[86,16]]},
    {k:"adv", nm:"🏔 광산 섬", c:0xc9b49a, gate:[0,-76], poly:[[-18,-78],[18,-78],[18,-112],[-18,-112]]},
    {k:"vil", nm:"🍄 버섯 마을", c:0xf2c6d8, gate:[-69,57], poly:[[-98,54],[-84,48],[-68,56],[-66,70],[-96,72]]},
    {k:"beach", nm:"🏖 등대 모래섬", c:0xfff0b8, poly:[[-8,68],[8,68],[8,81],[-8,81]]},
    {k:"free1", nm:"🚧 빈 자리", free:1, poly:[[-96,74],[-74,74],[-74,82],[-96,82]]},
    {k:"free2", nm:"🚧 빈 자리", free:1, poly:[[96,24],[110,24],[110,32],[96,32]]},
    {k:"free3", nm:"🚧 빈 자리", free:1, poly:[[-18,-104],[-8,-104],[-8,-96],[-18,-96]]},
  ];
  function hoodLots(h, hi){ const C=curve(h.p), out=[]; let n=0;
    for(let k=0;k<PER;k++){ const s=h.s0+k*GAP, A=at(C.Q,C.L,s), nx=-A.tz, nz=A.tx;
      [-1,1].forEach(side=>{ n++; const x=A.x+nx*OFF*side, z=A.z+nz*OFF*side, fx=-nx*side, fz=-nz*side;
        out.push({id:(hi+1)+"-"+n, hood:h.id, n, x, z, face:Math.atan2(fx,fz), prem:k===PER-1, lane:hi}); }); }
    return out; }
  const allLots=()=>hoods.reduce((a,h,i)=>a.concat(hoodLots(h,i)),[]);
  const zoneAt=(x,z)=>zones.find(Z=>inPoly(x,z,Z.poly))||null;
  window.ISLE_MAP5={v5:1, grid:{N:280, OX:140, OZ:140}, farR:178, island, MAINP, isles, links, broken, plaza, roads, city, fields, hoods, spots, zones, shops, shopS, SHOP_OFF, shopLots, inPoly, zoneAt, LOT, GAP, OFF, PER, cr, arc, at, curve, hoodLots, allLots, edge, inside};
})();
