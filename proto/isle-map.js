/* (v536) 🏝 새 우리 마을 설계도 — 하나로 이어진 큰 섬 · 굽은 길 · 이름 있는 동네 길
   사용자: "처음부터 다시 꾸미는 거라 다 날리니까 마을은 이쁘게 다시 만들어 줘야 해" → "한꺼번에 내보내자 근데 조금 더 가다듬어 줘"
   좌표 = 섬 가운데(광장) 기준, 북 = -z · isle.js 가 이 설계도대로 짓고, 시안 지도(tools)도 같은 파일로 그림 (설계도 = 실제) */
const ISLE_MAP=(()=>{
  const island={cx:0, cz:1, ax:47, az:41, s:1.3};
  const plaza={x:0, z:0, r:4.8};
  /* 길: 굵기 w · 점 = 부드러운 곡선(Catmull-Rom) */
  const roads={
    school:{w:2.0, p:[[0,-4.6],[-2,-11],[-7,-17],[-12,-22]]},
    market:{w:2.4, p:[[3.4,-3.4],[8,-8],[13,-12.8],[17.6,-17.6],[21.4,-22]]},
    east:  {w:2.0, p:[[4.7,.4],[11,1.6],[18,4.2],[26,6.2],[34,7.4],[39.5,7.8]]},
    farm:  {w:1.8, p:[[-6.4,-15.6],[-14,-14.6],[-21,-14],[-27,-13.6]]},
    park:  {w:1.6, p:[[-3.5,3.5],[-6.6,6.6],[-9.8,9.6],[-12.2,12]]},
  };
  /* 동네 길 — 1~3동 처음부터 · 4~6동은 아이가 늘면 (공사 중 울타리) */
  const hoods=[
    {id:"1동", nm:"벚꽃길", ic:"🌸", tree:"blossom", p:[[0,4.7],[-.6,10],[-2.2,16],[-3.6,22],[-4.4,28],[-4.8,34]], s0:5.2},
    {id:"2동", nm:"해바라기길", ic:"🌻", tree:"sun", p:[[-4.7,.3],[-10,1.2],[-16,1.8],[-22,3.6],[-28,6.6],[-34,10.4],[-38.5,13.4]], s0:4.2},
    {id:"3동", nm:"바닷가길", ic:"🌊", tree:"palm", p:[[3.4,3.4],[8,8.4],[12.6,13.6],[17.6,18.4],[23,22.4],[28.6,25.6],[33.4,27.6]], s0:4.6},
    {id:"4동", nm:"클로버길", ic:"🍀", tree:"clover", p:[[-2.2,-11.6],[-1,-17],[.6,-22.6],[1.8,-28.4],[2.2,-34.6],[2,-38]], s0:4.8, from:"school"},
    {id:"5동", nm:"단풍길", ic:"🍁", tree:"maple", p:[[-31.2,8.6],[-31.8,15],[-31.2,21.4],[-29.6,27.6],[-27.2,33]], s0:4.4, from:"2동"},
    {id:"6동", nm:"별빛길", ic:"⭐", tree:"star", p:[[36,7.4],[37.4,1],[37.8,-6],[36.8,-13],[34,-19.4]], s0:3.6, from:"east"},
  ];
  const LOT=2.2, GAP=2.75, OFF=2.15, PER=8;
  const spots={
    fountain:[0,0], board:[-4.4,-4.4], market:[13.5,-13],
    lake:{x:22.4, z:-7.2, rx:6.8, rz:5}, dock:[15.8,-6.6],
    tower:[41.4,8.6], mine:[24.6,-26.2], school:[-13.4,-24.6],
    farm:[-32,-15], park:{x:-15.5, z:15.5, r:7.4}, ox:[-19,12], pg:[-12.6,20], chest:[-12.6,13.6],
    stage:[-10,-7], camp:[-7.2,-9.6],
  };
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
  function edge(a){ const I=island, c=Math.cos(a), s=Math.sin(a); const r=1/Math.sqrt((c/I.ax)**2+(s/I.az)**2); return r*(1+.045*Math.sin(3*a+I.s)+.03*Math.sin(5*a+I.s*2)+.02*Math.sin(9*a+I.s*.7)); }
  function inside(x,z,m){ const dx=x-island.cx, dz=z-island.cz, a=Math.atan2(dz,dx); return Math.hypot(dx,dz) < edge(a)-(m||0); }
  return {island, plaza, roads, hoods, spots, LOT, GAP, OFF, PER, cr, arc, at, curve, hoodLots, allLots, edge, inside};
})();
if(typeof window!=="undefined") window.ISLE_MAP=ISLE_MAP;
if(typeof module!=="undefined") module.exports=ISLE_MAP;
