/* (v536) 🏝 새 우리 마을 설계도 — 하나로 이어진 큰 섬 · 굽은 길 · 이름 있는 동네 길
   사용자: "처음부터 다시 꾸미는 거라 다 날리니까 마을은 이쁘게 다시 만들어 줘야 해" → "한꺼번에 내보내자 근데 조금 더 가다듬어 줘"
   좌표 = 섬 가운데(광장) 기준, 북 = -z · isle.js 가 이 설계도대로 짓고, 시안 지도(tools)도 같은 파일로 그림 (설계도 = 실제) */
const ISLE_MAP=(()=>{
  /* (v550) 사용자: "맵이 더 커져야 하고 조금 더 정돈 · 시설이 애매하게 붙어 있어서 구역 같은 느낌이 아니야" → "3.5배 정도 널널하게 · 밭도 그렇고 다른 걸 넣을 걸 대비해서"
     → 섬 3.5배 (88×77) · 구역 7곳 (바닥 색·입구 문·이름판) · 주택가 = 남쪽 큰길 양옆 반듯한 골목 6개 · 🚧 빈 자리 3곳 (나중에) */
  const island={cx:0, cz:4, ax:88, az:77, s:1.3};
  const plaza={x:0, z:0, r:7.5};
  /* 길: 굵기 w · 점 = 부드러운 곡선(Catmull-Rom) — market = 상점가 큰길 · school = 배움 언덕 길 */
  const roads={
    market:{w:3.0, p:[[5.4,-5.4],[12,-12],[19,-19],[26,-26],[33,-33],[40,-40]]},
    school:{w:2.4, p:[[-5.4,-5.4],[-12,-12],[-19,-19],[-27,-26]]},
    east:  {w:2.4, p:[[7.5,0],[18,.6],[30,0],[42,.6],[54,0],[66,.8],[78,2]]},
    west:  {w:2.4, p:[[-7.5,0],[-18,.6],[-30,0],[-42,.6],[-54,0]]},
    south: {w:2.8, p:[[0,7.5],[0,16],[0,26],[0,36],[0,46],[0,56],[0,62]]},
    mine:  {w:2.0, p:[[40,-40],[33,-48],[24,-53],[15,-56]]},
  };
  /* 주택가 골목 — 1~3동 처음부터 · 4~6동은 아이가 늘면 (공사 중 울타리) */
  const hood=(id,nm,ic,tree,z,side)=>({id,nm,ic,tree,p:[[side*1.6,z],[side*9,z+.4],[side*17,z],[side*25,z+.4],[side*29,z]],s0:4.8,from:"south"});
  const hoods=[hood("1동","벚꽃길","🌸","blossom",19,-1), hood("2동","해바라기길","🌻","sun",19,1), hood("3동","클로버길","🍀","clover",35,-1), hood("4동","단풍길","🍁","maple",35,1), hood("5동","바닷가길","🌊","palm",51,-1), hood("6동","별빛길","⭐","star",51,1)];
  const LOT=2.2, GAP=2.75, OFF=2.15, PER=8;
  const spots={
    fountain:[0,0], board:[-2.9,-7.1], goal:[5.9,4.8], stage:[-7,-16], camp:[-11,-21.5], station:[2.5,-14], post:[9.5,8.5], bank:[-9.5,8.5],
    market:[22,-22], campus:[-31,-29], school:[-37,-35], library:[-25,-36.5], museum:[-39,-22],
    lake:{x:52, z:-16, rx:11, rz:7.5}, dock:[41.5,-15], tower:[82,3],
    mine:[10,-58], mountain:[17,-66],
    farm:[-60,-17], windmill:[-68,-28],
    park:{x:56, z:26, r:12}, ox:[51,22], pg:[61,31], chest:[56,16],
  };
  /* 상점가 가게 8채 — 큰길 s 자리 양옆에서 마주 봄 */
  const shops=[["fish","🐟","생선 가게",0x5aa7ff],["clothes","👕","옷 가게",0xff6b6b],["mart","🛒","마트",0x5cc46a],["hair","💇","미용실",0xff9ac8],["snack","🍦","간식 가게",0xffb6d1],["furn","🛋","가구점",0xffc93d],["pet","🐶","펫 가게",0x7fd36a],["photo","📸","사진관",0x9b72f0]];
  const shopS=[9,16.5,24,31.5], SHOP_OFF=4.4;
  /* 구역 — 바닥 색 · 입구 문(gate) · 이름 · free = 🚧 빈 자리(나중에 새 구역) */
  const zones=[
    {k:"center", nm:"⛲ 중앙 광장", c:0xf2d9a0, poly:[[-15,-25],[13,-25],[15,9],[-15,9]]},
    {k:"shop", nm:"🏪 상점가", c:0xff9ec0, gate:[10,-10], poly:[[9,-6],[24,-5],[47,-31],[44,-45],[31,-46],[7,-22]]},
    {k:"campus", nm:"🎓 배움 언덕", c:0x9ec4ff, gate:[-10,-10], poly:[[-9,-9],[-16,-29],[-30,-46],[-49,-42],[-50,-14],[-22,-9]]},
    {k:"home", nm:"🏘 주택가", c:0xffe08a, gate:[0,12.5], poly:[[-34,12],[34,12],[34,57],[-34,57]]},
    {k:"farm", nm:"🌾 농장·캠핑", c:0xd8e86a, gate:[-48,0], poly:[[-50,-6],[-80,-6],[-80,-38],[-54,-38]]},
    {k:"lake", nm:"🎣 호수·숲", c:0x7fe0c8, gate:[36,0], poly:[[35,-3],[35,-28],[68,-28],[70,-3]]},
    {k:"park", nm:"🎡 놀이 공원", c:0xa0f07a, gate:[52,4], poly:[[41,6],[71,6],[71,41],[41,41]]},
    {k:"adv", nm:"🏔 모험", c:0xc9b49a, gate:[38,-38], poly:[[0,-47],[30,-47],[30,-72],[0,-72]]},
    {k:"free1", nm:"🚧 빈 자리", free:1, poly:[[-38,14],[-70,14],[-66,44],[-40,48]]},
    {k:"free2", nm:"🚧 빈 자리", free:1, poly:[[38,46],[64,46],[56,68],[36,66]]},
    {k:"free3", nm:"🚧 빈 자리", free:1, poly:[[-20,-50],[-46,-50],[-40,-68],[-18,-68]]},
  ];
  /* ── 곡선 ── */
  function cr(P, n){ const out=[]; for(let i=0;i<P.length-1;i++){ const p0=P[Math.max(0,i-1)], p1=P[i], p2=P[i+1], p3=P[Math.min(P.length-1,i+2)];
      for(let k=0;k<n;k++){ const t=k/n, t2=t*t, t3=t2*t; out.push([0,1].map(j=>.5*((2*p1[j])+(-p0[j]+p2[j])*t+(2*p0[j]-5*p1[j]+4*p2[j]-p3[j])*t2+(-p0[j]+3*p1[j]-3*p2[j]+p3[j])*t3))); } }
    out.push(P[P.length-1].slice()); return out; }
  function arc(Q){ const L=[0]; for(let i=1;i<Q.length;i++) L.push(L[i-1]+Math.hypot(Q[i][0]-Q[i-1][0],Q[i][1]-Q[i-1][1])); return L; }
  function at(Q, L, s){ let i=1; while(i<L.length-1 && L[i]<s) i++; const a=Q[i-1], b=Q[i], f=Math.max(0,Math.min(1,(s-L[i-1])/((L[i]-L[i-1])||1)));
    const x=a[0]+(b[0]-a[0])*f, z=a[1]+(b[1]-a[1])*f, d=Math.hypot(b[0]-a[0],b[1]-a[1])||1; return {x, z, tx:(b[0]-a[0])/d, tz:(b[1]-a[1])/d}; }
  const curve=P=>{ const Q=cr(P,10); return {Q, L:arc(Q)}; };
  /* 동네 땅 — 길 따라 양쪽 8칸씩 (마지막 줄 = ⭐ 좋은 자리) · 집은 길을 봄 */
  function hoodLots(h, hi){ const C=curve(h.p), out=[]; let n=0;
    for(let k=0;k<PER;k++){ const s=h.s0+k*GAP, A=at(C.Q,C.L,s), nx=-A.tz, nz=A.tx;
      [-1,1].forEach(side=>{ n++; const x=A.x+nx*OFF*side, z=A.z+nz*OFF*side, fx=-nx*side, fz=-nz*side;
        out.push({id:(hi+1)+"-"+n, hood:h.id, n, x, z, face:Math.atan2(fx,fz), prem:k===PER-1, lane:hi}); }); }
    return out; }
  const allLots=()=>hoods.reduce((a,h,i)=>a.concat(hoodLots(h,i)),[]);
  /* 섬 가장자리 */
  function edge(a){ const I=island, c=Math.cos(a), s=Math.sin(a); const r=1/Math.sqrt((c/I.ax)**2+(s/I.az)**2); return r*(1+.04*Math.sin(3*a+I.s)+.025*Math.sin(5*a+I.s*2)+.015*Math.sin(9*a+I.s*.7)); }
  function inside(x,z,m){ const dx=x-island.cx, dz=z-island.cz, a=Math.atan2(dz,dx); return Math.hypot(dx,dz) < edge(a)-(m||0); }
  function shopLots(){ const C=curve(roads.market.p), out=[]; shopS.forEach((s,k)=>{ const A=at(C.Q,C.L,s); [-1,1].forEach((sd,j)=>{ const nx=-A.tz*sd, nz=A.tx*sd; out.push({sh:shops[k*2+j], x:A.x+nx*SHOP_OFF, z:A.z+nz*SHOP_OFF, nx, nz, rx:A.x, rz:A.z}); }); }); return out; }
  function inPoly(x,z,P){ let c=false; for(let i=0,j=P.length-1;i<P.length;j=i++){ const a=P[i], b=P[j]; if(((a[1]>z)!==(b[1]>z)) && (x<(b[0]-a[0])*(z-a[1])/(b[1]-a[1])+a[0])) c=!c; } return c; }
  const zoneAt=(x,z)=>zones.find(Z=>inPoly(x,z,Z.poly))||null;
  return {island, plaza, roads, hoods, spots, zones, shops, shopS, SHOP_OFF, shopLots, inPoly, zoneAt, LOT, GAP, OFF, PER, cr, arc, at, curve, hoodLots, allLots, edge, inside};
})();
if(typeof window!=="undefined") window.ISLE_MAP=ISLE_MAP;
if(typeof module!=="undefined") module.exports=ISLE_MAP;
