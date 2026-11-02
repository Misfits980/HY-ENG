/* ═════════ (v528) 🏝 우리 마을 — 아이들끼리 하는 놀이 6가지
   사용자: "애들끼리 할 만한 좋은 컨텐츠는?" → "6번까지 다 해보고 서버 저장까지 다 해서 완성도 있게 · qa 까지"
   ① 🎣 같이 낚시 — 호수(house.html pondCtx) · 잡으면 모두에게 소식 · 🏆 낚시 대회 (15:30~20:40, 매시 30분부터 10분) 순위 · 상
   ② ⭕❌ OX 단어 마당 — 12초마다 「🐱 = cat ?」 · 맞는 판(O/X)에 서 있기 · 연속 기록 · 오늘 순위
   ③ 🧊 얼음땡 (놀이터) — 1분 판 · 술래(같은 규칙으로 모두가 같은 아이) · 잡히면 얼음 · 친구가 와서 단어를 맞히면 풀림
   ④ 🗼 하늘 타워 — 입구 이름표에 「지금 N명」 (같이 오르기는 타워 실시간 그대로)
   ⑤ 🎁 보물찾기 — 오늘의 단어 카드 10장이 섬 곳곳에 · 주우면 단어 소리 · 학원 전체 합이 목표에 닿으면 광장 상자가 열림 (한 번씩 상)
   ⑥ 🏠 친구 집 놀러 가기 · 좋아요 · 스티커 — 동네 집을 누르면 (isle.js visitLot → 기존 방문·방명록)
   서버: /hy/isle/ft/<시각>/<아이> · /hy/isle/ox/<날>/<아이> · /hy/isle/tr/<날>/<아이> · 얼음 = 섬 실시간 /hy/day/il<날>/<코드>/z */
const IPLAY=(()=>{
  if(!window.ISLE) return null;
  const W_=typeof ISLE_WORDS!=="undefined" ? ISLE_WORDS : [["cat","고양이","🐱",1],["dog","개","🐶",1],["fish","물고기","🐟",1]];
  const q=new URLSearchParams(location.search), TEST=q.get("iplay")==="test";
  const T=()=>{ try{ return srvNow(); }catch(e){ return Date.now(); } };
  const KST=t=>new Date(t+9*3600e3);
  const day=()=>KST(T()).toISOString().slice(0,10).replace(/-/g,"");
  const H=s=>{ let h=2166136261; for(const ch of String(s)){ h^=ch.charCodeAt(0); h=Math.imul(h,16777619)>>>0; } return h; };
  const me=()=>ISLE.myKey(), nm=()=>{ try{ return String(kidInfo().n||"친구").slice(0,10); }catch(e){ return "친구"; } };
  const inIsle=()=>place===PL.isle;
  const S={ban:"", banT:0, ft:{best:0, board:null, bAt:0, done:{}}, ox:{i:-1, st:0, best:0, judged:-1, word:null, ok:null, board:null, bAt:0}, tag:{round:-1, frozenMe:false, asked:false, msgT:0}, tr:{found:{}, total:0, tAt:0, objs:[], goal:40, claimed:false}, tw:{n:0, at:0}};
  /* ── 위 알림 띠 ── */
  function ui(){ if($("ipBan")) return; const st=document.createElement("style"); st.textContent=`
#ipBan{position:fixed;left:50%;top:calc(66px + env(safe-area-inset-top));transform:translateX(-50%);z-index:4;max-width:min(92vw,460px);display:none;align-items:center;gap:8px;padding:6px 14px 6px 8px;border-radius:999px;background:#fffdf7;border:3px solid #3b2433;box-shadow:0 4px 0 #3b2433;font:15px var(--kr);color:#3b2433;pointer-events:none;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
body.isleOn #ipBan.on{display:flex} #ipBan i{font-style:normal;font-size:20px} #ipBan b{font-weight:400;color:#c8364a} #ipBan small{font-size:12.5px;color:#9a7e63}
#ipBan.hot{background:#fff3bf} #ipBan.ok{background:#dff3d6} #ipBan.bad{background:#ffe3e3}
#ipQ{position:fixed;inset:0;z-index:21;display:none;align-items:center;justify-content:center;background:rgba(30,18,40,.45)}
#ipQ.on{display:flex} #ipQ .b{width:min(340px,90vw);background:#fff8ea;border:3px solid #3b2433;border-radius:24px;box-shadow:0 6px 0 #3b2433;padding:16px;text-align:center;font-family:var(--kr);color:#3b2433}
#ipQ .e{font-size:58px;line-height:1.1} #ipQ p{margin:6px 0 12px;font-size:16px} #ipQ .o{display:grid;gap:8px}
#ipQ button{height:52px;border-radius:16px;border:3px solid #3b2433;background:#fffdf7;box-shadow:0 3px 0 #3b2433;font:800 20px var(--en);color:#3b2433}
#ipQ button.r{background:#86dc7c;color:#fff} #ipQ button.w{background:#ffb3b3}
.ipBoard{margin:8px 0 2px;text-align:left;font-size:14px} .ipBoard div{display:flex;gap:8px;padding:4px 8px;border-radius:10px} .ipBoard div:nth-child(odd){background:rgba(0,0,0,.04)} .ipBoard div.me{background:#fff3bf} .ipBoard b{margin-left:auto;font-weight:400}`;
    document.head.appendChild(st); const b=document.createElement("div"); b.id="ipBan"; document.body.appendChild(b); const qd=document.createElement("div"); qd.id="ipQ"; qd.innerHTML='<div class="b"></div>'; document.body.appendChild(qd);
    ["pointerdown","pointerup"].forEach(ev=>qd.addEventListener(ev, e=>e.stopPropagation())); }
  function ban(html, cls){ ui(); const b=$("ipBan"); if(S.ban!==html+cls){ S.ban=html+cls; b.innerHTML=html; b.className=(html?"on ":"")+(cls||""); } }
  /* 단어 문제 창 (보기 3) — cb(맞음 true/false) */
  function askWord(title, cb){ ui(); const w=W_[Math.floor(Math.random()*W_.length)], opts=[w]; while(opts.length<3){ const o=W_[Math.floor(Math.random()*W_.length)]; if(!opts.some(x=>x[0]===o[0])) opts.push(o); } opts.sort(()=>Math.random()-.5);
    const box=$("ipQ").querySelector(".b"); box.innerHTML='<div class="e">'+w[2]+'</div><p>'+title+'<br><small>'+esc(w[1])+' — 영어로?</small></p><div class="o">'+opts.map(o=>'<button data-w="'+o[0]+'">'+o[0]+'</button>').join("")+'</div>';
    $("ipQ").classList.add("on"); box.onclick=e=>{ const bt=e.target.closest("[data-w]"); if(!bt) return; const ok=bt.dataset.w===w[0]; bt.classList.add(ok?"r":"w"); box.querySelectorAll("[data-w]").forEach(x=>{ if(x.dataset.w===w[0]) x.classList.add("r"); x.disabled=true; }); try{ say(w[0]); }catch(_){}
      setTimeout(()=>{ $("ipQ").classList.remove("on"); cb(ok); }, ok?700:1300); }; }
  const fmtT=ms=>{ const s=Math.max(0,Math.ceil(ms/1000)); return Math.floor(s/60)+":"+String(s%60).padStart(2,"0"); };
  function board(o, unit){ const L=Object.entries(o||{}).map(([k,v])=>({k, n:v&&v.n||"친구", s:+(v&&v.s)||0})).filter(x=>x.s>0).sort((a,b)=>b.s-a.s); return L; }
  function boardHTML(L, unit, n){ return '<div class="ipBoard">'+L.slice(0,n||5).map((x,i)=>'<div class="'+(x.k===me()?"me":"")+'"><span>'+["🥇","🥈","🥉","4","5","6","7","8"][i]+'</span>'+esc(x.n)+'<b>'+x.s+unit+'</b></div>').join("")+'</div>'; }
  /* ════ ① 🎣 낚시 대회 ════ */
  function ftSlot(t){ t=t==null?T():t; if(TEST && q.get("ft")==="on"){ const st=Math.floor(t/600000)*600000; return {id:"t"+st, st, en:st+600000}; }
    const d=KST(t), h=d.getUTCHours(), m=d.getUTCMinutes(); if(h<15 || h>20) return null; if(m<30 || m>=40) return null;
    const st=t-((m-30)*60+d.getUTCSeconds())*1000-d.getUTCMilliseconds(); return {id:d.toISOString().slice(0,13).replace(/\D/g,""), st, en:st+600000}; }
  function ftNext(t){ t=t==null?T():t; for(let k=0;k<26;k++){ const x=Math.ceil((t+1)/1800000)*1800000+k*1800000; const s=ftSlot(x+1000); if(s) return s; } return null; }
  async function ftLoad(id){ try{ const v=await NET.get("/hy/isle/ft/"+id); S.ft.board=board(v); S.ft.bAt=Date.now(); }catch(e){} }
  function onCatch(f, cm, sh, rec){ if(!inIsle()) return; const K=nm();
    if(cm>0 || f.en==="treasure"){ const m="🎣 "+f.e+" "+f.en+(cm?" "+cm+"cm":"")+(sh?" ✨":"")+"!"; const id=Date.now().toString(36)+myCode, v={c:myCode, n:K, m, at:Date.now(), sys:1};
      try{ VLN.msgs[id]=v; vcFeed(K, m, true); NET.put(VLN.mp+"/"+id, v).catch(()=>{}); }catch(e){} }
    const s=ftSlot(); if(s && cm>0 && cm>S.ft.best){ S.ft.best=cm; NET.put("/hy/isle/ft/"+s.id+"/"+me(), {n:K, s:cm, e:f.e, en:f.en, at:Date.now()}).catch(()=>{}); setTimeout(()=>ftLoad(s.id), 600); toast("🏆 대회 기록 <b>"+cm+"cm</b>!", 1800); } }
  function ftTick(){ const now=T(), s=ftSlot(now);
    if(s){ if(S.ft.id!==s.id){ S.ft.id=s.id; S.ft.best=0; S.ft.board=null; ftLoad(s.id); toast("🏆 <b>낚시 대회</b> 시작! 10분 동안 가장 큰 물고기를 잡아요<br><small>🎣 호수 부두로!</small>", 3400); }
      if(Date.now()-S.ft.bAt>8000){ S.ft.bAt=Date.now(); ftLoad(s.id); }
      const L=S.ft.board||[], top=L[0], mi=L.findIndex(x=>x.k===me());
      return ['<i>🏆</i>낚시 대회 <b>'+fmtT(s.en-now)+'</b> <small>'+(top?'1등 '+esc(top.n)+' '+top.s+'cm':'아직 기록 없음')+(mi>=0?' · 나 '+(mi+1)+'등':'')+'</small>', "hot"]; }
    if(S.ft.id && !S.ft.done[S.ft.id]){ const id=S.ft.id; S.ft.done[id]=1; ftEnd(id); }
    const n=ftNext(now); if(n && n.st-now<20*60000) return ['<i>🎣</i>낚시 대회 <small>'+fmtT(n.st-now)+' 뒤 시작</small>', ""];
    return null; }
  async function ftEnd(id){ await ftLoad(id); const L=S.ft.board||[]; if(!L.length) return; const mi=L.findIndex(x=>x.k===me()); let got=0, key="hyeng_isle_ftp_"+id;
    let paid=false; try{ paid=!!localStorage.getItem(key); }catch(e){} if(mi>=0 && !paid){ got=[30,20,10][mi]||3; try{ gems+=got; saveBag(); localStorage.setItem(key,"1"); }catch(e){} }
    info('<div class="iBig">🏆</div><b>낚시 대회 끝!</b>'+boardHTML(L,"cm",5)+(mi>=0?'<small>나는 <b>'+(mi+1)+'등</b>'+(got?' · 💎 +'+got:'')+'</small>':'<small>다음 대회에 같이 해요!</small>'), "좋아요", null); }
  /* ════ ② ⭕❌ OX 단어 마당 ════ */
  const OXP=12000, OXJ=10000;   // 12초에 한 문제 · 10초에 판정
  function oxQ(i){ const r=H("ox|"+i), w=W_[r%W_.length]; let shown=w; const yes=(r>>>8)%2===0; if(!yes){ let k=1; do{ shown=W_[(r+k*7919)%W_.length]; k++; }while(shown[0]===w[0]); } return {w, shown, yes}; }
  function oxIn(){ const c=ISLE.SPOT.oxC; if(!c) return null; const p=hero.g.position, dx=p.x-c[0], dz=p.z-c[1]; if(Math.hypot(dx,dz)>3.9) return null; if(Math.abs(dz)>1.55) return "mid"; return dx<-.45 ? "O" : dx>.45 ? "X" : "mid"; }
  function oxNear(){ const c=ISLE.SPOT.oxC; if(!c) return false; const p=hero.g.position; return Math.hypot(p.x-c[0],p.z-c[1])<6.5; }
  async function oxLoad(){ try{ const v=await NET.get("/hy/isle/ox/"+day()); S.ox.board=board(v); S.ox.bAt=Date.now(); }catch(e){} }
  function oxJudge(j, at){ S.ox.judged=j; if(!at) return; const Q=oxQ(j), right=at!=="mid" && (at==="O")===Q.yes;
    const o=ISLE.G.userData["ox"+(Q.yes?"O":"X")]; if(o){ o.material.emissive=new THREE.Color(0x66ff66); o.material.emissiveIntensity=.35; setTimeout(()=>{ o.material.emissiveIntensity=0; dirty=true; }, 1600); }
    if(right){ S.ox.st++; S.ox.ok=true; try{ SND.win(); }catch(e){} hero.act="yay"; hero.actT=0; if(S.ox.st>S.ox.best){ S.ox.best=S.ox.st; NET.put("/hy/isle/ox/"+day()+"/"+me(), {n:nm(), s:S.ox.best, at:Date.now()}).catch(()=>{}); } if(S.ox.st%5===0){ try{ gems+=2; saveBag(); }catch(e){} toast("⭕ "+S.ox.st+"연속! 💎 +2", 1600); } }
    else { S.ox.ok=false; S.ox.st=0; try{ SND.snap(); }catch(e){} const c=ISLE.SPOT.oxC, p=hero.g.position; p.set(c[0], 0, c[1]+4.6); hero.cx=Math.floor(p.x); hero.cz=Math.floor(p.z); hero.path=[]; toast("❌ 아쉬워요! 정답은 "+(Q.yes?"⭕":"❌")+" — <b>"+Q.w[2]+" = "+Q.w[0]+"</b>", 2200); }
    try{ say(Q.w[0]); }catch(e){} }
  function oxTick(){ if(!oxNear()){ S.ox.i=-1; return null; } const now=T(), i=Math.floor(now/OXP), ph=now-i*OXP, Q=oxQ(i), at=oxIn();
    /* 화면이 느려 판정 2초를 놓쳤으면 (지난 문제 · 바로 앞 두 문제까지만) 지금 서 있는 자리로 판정 */
    if(S.ox.i>=0 && S.ox.i===i-1 && ph<2500 && S.ox.judged!==S.ox.i && S.ox.lastAt) oxJudge(S.ox.i, at);   /* 막 넘어간 직후만 (시간이 크게 건너뛰면 판정 안 함) */
    if(S.ox.i!==i){ S.ox.i=i; S.ox.ok=null; }
    S.ox.lastAt=at;
    if(ph>=OXJ && S.ox.judged!==i) oxJudge(i, at);
    if(Date.now()-S.ox.bAt>15000) oxLoad();
    const left=OXJ-ph, judge=ph>=OXJ, top=(S.ox.board||[])[0];
    if(!at) return ['<i>⭕</i>OX 단어 마당 <small>안으로 들어가요 · '+Q.w[2]+' = '+Q.shown[0]+' ?'+(top?' · 오늘 1등 '+esc(top.n)+' '+top.s+'연속':'')+'</small>', ""];
    if(judge) return ['<i>'+(S.ox.ok?"🎉":"⭕")+'</i>'+(Q.yes?"⭕ 맞아요":"❌ 아니에요")+' <small>'+Q.w[2]+' = '+Q.w[0]+' · 연속 '+S.ox.st+'</small>', S.ox.ok?"ok":S.ox.ok===false?"bad":""];
    return ['<i>'+Q.w[2]+'</i>= <b>'+Q.shown[0]+'</b> ? <small>⭕ 왼쪽 · ❌ 오른쪽 · '+Math.ceil(left/1000)+'초 · 연속 '+S.ox.st+'</small>', at==="mid"?"":"hot"]; }
  /* ════ ③ 🧊 얼음땡 (놀이터) ════ */
  const TAGP=60000;
  function inPG(x,z){ const c=ISLE.SPOT.pgC; return c && Math.hypot(x-c[0],z-c[1])<3.5; }
  function tagPlayers(){ const L=[]; const p=hero.g.position; if(inPG(p.x,p.z)) L.push({k:myCode, x:p.x, z:p.z, me:true, z_:(VLN.tree[myCode]||{}).z, t_:(VLN.tree[myCode]||{}).t});
    try{ Object.keys(VLN.tree).forEach(k=>{ if(k===myCode) return; const d=VLN.tree[k]; if(!d || !d.p) return; const c=VLN.peers[k]; if(c && c.g.visible===false) return; if(Math.abs(Date.now()-(+d.p[4]||0))>60000) return; if(inPG(+d.p[0],+d.p[1])) L.push({k, x:+d.p[0], z:+d.p[1], z_:d.z, t_:d.t, c}); }); }catch(e){} return L; }
  /* 술래 = 이번 판에 먼저 「내가 술래」라고 적은 아이 (늦게 보인 친구 때문에 술래가 둘이 되지 않게) · 없으면 해시로 */
  function tagger(L, r){ const C=L.filter(x=>+x.t_===r), P=C.length?C:L; let b=null, bh=1e18; P.forEach(x=>{ const h=H(r+"|"+x.k); if(h<bh){ bh=h; b=x; } }); return b; }
  function frozen(){ if(!inIsle()) return false; const r=Math.floor(T()/TAGP), d=(VLN.tree||{})[myCode]; return !!(d && +d.z===r && inPG(hero.g.position.x, hero.g.position.z)); }
  function iceOn(c, on){ if(!c || !c.g) return; if(on && !c.ice){ const m=new THREE.Mesh(new THREE.CylinderGeometry(.42,.42,1.25,10), new THREE.MeshStandardMaterial({color:0xbfeaff, transparent:true, opacity:.45, roughness:.1})); m.position.y=.62; c.g.add(m); c.ice=m; dirty=true; }
    if(!on && c.ice){ c.g.remove(c.ice); c.ice=null; dirty=true; } }
  function capOn(c, on){ if(!c || !c.g) return; if(on && !c.tcap){ const m=new THREE.Mesh(new THREE.ConeGeometry(.2,.4,10), new THREE.MeshBasicMaterial({color:0xff4d5e})); m.position.y=1.95; c.g.add(m); c.tcap=m; dirty=true; } if(!on && c.tcap){ c.g.remove(c.tcap); c.tcap=null; dirty=true; } }
  function tagTick(dt){ const r=Math.floor(T()/TAGP), L=tagPlayers(), meIn=L.some(x=>x.me);
    const peers=Object.entries(VLN.peers||{}); peers.forEach(([k,c])=>{ const d=VLN.tree[k]||{}, on=inPG(c.g.position.x,c.g.position.z); iceOn(c, on && +d.z===r); });
    const tg=L.length>=2 ? tagger(L, r) : null;
    if(tg && tg.me && +tg.t_!==r){ const m=VLN.tree[myCode]=VLN.tree[myCode]||{}; m.t=r; NET.put(VLN.path+"/"+myCode+"/t", r).catch(()=>{}); } peers.forEach(([k,c])=>capOn(c, !!(tg && tg.k===k))); capOn(hero, !!(tg && tg.me));
    const fz=frozen(); iceOn(hero, fz);
    if(!meIn){ S.tag.asked=false; return null; }
    if(L.length<2) return ['<i>🧊</i>얼음땡 놀이터 <small>친구가 오면 시작해요 (2명부터)</small>', ""];
    const left=TAGP-(T()-r*TAGP), alive=L.filter(x=>+x.z_!==r && x!==tg);
    if(tg.me){ L.forEach(x=>{ if(x.me || +x.z_===r) return; if(Math.hypot(x.x-hero.g.position.x, x.z-hero.g.position.z)<.95){ NET.put(VLN.path+"/"+x.k+"/z", r).catch(()=>{}); x.z_=r; try{ VLN.tree[x.k].z=r; SND.snap(); }catch(e){} toast("🧊 잡았다!", 900); } });
      return ['<i>🔴</i>내가 <b>술래</b>! 친구를 잡아요 <small>'+fmtT(left)+' · 남은 친구 '+alive.length+'</small>', "hot"]; }
    if(fz) return ['<i>🧊</i><b>얼음!</b> <small>친구가 와서 풀어 줄 때까지 기다려요 · '+fmtT(left)+'</small>', "bad"];
    const near=L.find(x=>!x.me && +x.z_===r && Math.hypot(x.x-hero.g.position.x, x.z-hero.g.position.z)<1.1);
    if(near && !S.tag.asked && !$("ipQ").classList.contains("on")){ S.tag.asked=true; askWord("🧊 친구를 녹여 줘요!", ok=>{ if(ok){ NET.put(VLN.path+"/"+near.k+"/z", null).catch(()=>{}); try{ delete VLN.tree[near.k].z; }catch(e){} toast("💧 땡! 친구가 풀렸어요", 1400); } else toast("다시 가까이 가서 해 봐요", 1200); setTimeout(()=>{ S.tag.asked=false; }, 1500); }); }
    if(!near) S.tag.asked=false;
    return ['<i>🏃</i>얼음땡 · 술래를 피해요 <small>'+fmtT(left)+' · 얼음 친구에게 가면 풀어 줄 수 있어요</small>', ""]; }
  /* ════ ⑤ 🎁 보물찾기 ════ */
  const TRN=10;
  function trSpots(){ const d=day(), L=[], N=ISLE.N; let k=0;
    while(L.length<TRN && k<4000){ k++; const h=H("tr|"+d+"|"+k), x=h%N, z=(h>>>8)%N; if(ISLE.blocked(x,z) || ISLE.waterCell(x,z)) continue; const px=x+.5, pz=z+.5;
      if(ISLE.onPave(px,pz) || L.some(o=>Math.hypot(o.x-px,o.z-pz)<6)) continue; const w=W_[(h>>>4)%W_.length]; L.push({i:L.length, x:px, z:pz, w}); } return L; }
  function trLoadFound(){ try{ const o=JSON.parse(localStorage.getItem("hyeng_isle_tr")||"{}"); S.tr.found=o.d===day() ? (o.f||{}) : {}; S.tr.claimed=o.d===day() && !!o.c; }catch(e){ S.tr.found={}; } }
  function trSave(){ try{ localStorage.setItem("hyeng_isle_tr", JSON.stringify({d:day(), f:S.tr.found, c:S.tr.claimed?1:0})); }catch(e){} }
  async function trTotal(){ try{ const v=await NET.get("/hy/isle/tr/"+day()); let s=0; Object.values(v||{}).forEach(n=>{ s+=Math.min(TRN, +n||0); }); S.tr.total=s; S.tr.tAt=Date.now(); }catch(e){} return S.tr.total; }
  function trCard(w){ const c=document.createElement("canvas"); c.width=128; c.height=160; const g=c.getContext("2d"); g.fillStyle="#fffdf7"; g.strokeStyle="#3b2433"; g.lineWidth=8; g.beginPath(); g.roundRect ? g.roundRect(6,6,116,148,18) : g.rect(6,6,116,148); g.fill(); g.stroke();
    g.font="64px sans-serif"; g.textAlign="center"; g.textBaseline="middle"; g.fillText("❓",64,72); g.fillStyle="#ffd23f"; g.fillRect(24,122,80,14); const t=new THREE.CanvasTexture(c); t.encoding=THREE.sRGBEncoding;
    const s=new THREE.Sprite(new THREE.SpriteMaterial({map:t, depthWrite:false})); s.scale.set(.62,.78,1); return s; }
  function trBuild(){ S.tr.objs.forEach(o=>{ if(o.s.parent) o.s.parent.remove(o.s); }); S.tr.objs=[]; trLoadFound(); S.tr.day=day();
    trSpots().forEach(o=>{ if(S.tr.found[o.i]) return; const s=trCard(o.w); s.position.set(o.x,.9,o.z); ISLE.G.add(s); S.tr.objs.push(Object.assign(o,{s})); }); }
  function trTick(dt){ if(S.tr.day!==day()) trBuild(); const p=hero.g.position, t=performance.now()*.003; let anim=false;
    S.tr.objs.forEach(o=>{ if(!o.s.parent) return; o.s.position.y=.9+Math.sin(t+o.i)*.12; anim=true;
      if(Math.hypot(o.x-p.x,o.z-p.z)<1.1 && !$("ipQ").classList.contains("on") && F.st==="idle"){ o.s.parent.remove(o.s); S.tr.found[o.i]=1; trSave(); const n=Object.keys(S.tr.found).length;
        NET.put("/hy/isle/tr/"+day()+"/"+me(), n).catch(()=>{}); S.tr.total++; try{ SND.sparkle(); say(o.w[0]); }catch(e){}
        info('<div class="iBig">'+o.w[2]+'</div><span class="enBig">'+o.w[0]+'</span><br><small>'+esc(o.w[1])+'</small><br><small>🎁 보물 카드 '+n+'/'+TRN+' · 우리 마을 '+S.tr.total+'/'+S.tr.goal+'</small>', "주웠어요!", null); } });
    if(Date.now()-S.tr.tAt>20000){ S.tr.tAt=Date.now(); trTotal(); }
    const lid=ISLE.G.userData.chestLid, open=S.tr.total>=S.tr.goal; if(lid){ const want=open?-1.1:0; if(Math.abs(lid.rotation.x-want)>.01){ lid.rotation.x+=(want-lid.rotation.x)*Math.min(1,dt*3); anim=true; } }
    return anim; }
  function chestTap(){ if(S.tr.busy) return; S.tr.busy=true; trTotal().finally(()=>{ S.tr.busy=false; }).then(()=>{ const open=S.tr.total>=S.tr.goal, n=Object.keys(S.tr.found).length;
    if(open && !S.tr.claimed){ S.tr.claimed=true; trSave(); try{ gems+=10; setBait(bait+5); saveBag(); SND.big(); }catch(e){} info('<div class="iBig">🎁</div><b>보물 상자가 열렸어요!</b><br>우리 마을 친구들이 카드 <b>'+S.tr.total+'장</b>을 모았어요<br><small>💎 +10 · 🪱 +5</small>', "고마워요!", null); return; }
    info('<div class="iBig">🎁</div><b>오늘의 보물 상자</b><br>섬 곳곳의 <b>❓ 단어 카드</b>를 주워요<br><small>우리 마을 '+S.tr.total+' / '+S.tr.goal+'장 · 내가 '+n+'/'+TRN+'장'+(open?' · 오늘 상은 받았어요':'')+'</small>', "찾으러 가요", null); }); }
  /* ════ ④ 🗼 타워 인원 ════ */
  async function twCount(){ if(Date.now()-S.tw.at<15000) return S.tw.n; S.tw.at=Date.now(); let n=0;
    for(const m of ["k","e","h","s"]){ try{ const v=await NET.query("/hy/day/tw"+dayKey().replace(/\D/g,"")+m, "shallow=true"); n+=Object.keys(v||{}).length; }catch(e){} }
    S.tw.n=n; const L=(typeof LBL!=="undefined"?LBL:[]).find(L=>L.d.k==="tower"); if(L) L.el.innerHTML='<i>🗼</i>하늘 타워'+(n?' · 지금 '+n+'명':''); return n; }
  /* ── 이름표 더하기 ── */
  const baseLbl=LBL_DEF.isle;
  LBL_DEF.isle=()=>{ const L=baseLbl(), Sp=ISLE.SPOT;
    if(Sp.ox) L.push({k:"ox", ic:"⭕", t:"OX 단어 마당", p:Sp.ox, r:5, act:()=>{ const c=Sp.oxC; walkTo(Math.floor(c[0]), Math.floor(c[1]-2.6)); }});
    if(Sp.pg) L.push({k:"pg", ic:"🧊", t:"얼음땡 놀이터", p:Sp.pg, r:5, act:()=>{ const c=Sp.pgC; walkTo(Math.floor(c[0]), Math.floor(c[1])); toast("🧊 <b>얼음땡</b> — 놀이터 안에 2명 이상 있으면 시작! 술래(🔴 모자)를 피해요<br><small>얼음이 된 친구에게 가면 단어를 맞혀 풀어 줄 수 있어요</small>", 3600); }});
    if(Sp.chest) L.push({k:"chest", ic:"🎁", t:"보물 상자", p:Sp.chest, r:3.6, act:chestTap});
    return L; };
  ISLE.onBuild(()=>{ trBuild(); });
  /* ── 매 프레임 ── */
  let slow=0;
  function tick(dt){ if(!inIsle()){ if(S.ban) ban(""," "); return false; } let anim=false; const tn=performance.now(), slowGo=tn-slow>250;
    if(trTick(dt)) anim=true; const tg=tagTick(dt);
    if(slowGo){ slow=tn; const ox=oxTick(), ft=ftTick(); const B=tg||ox||ft; if(B) ban(B[0], B[1]); else ban("", ""); twCount(); }
    return anim; }
  function onMsg(v){}
  return {S, tick, onCatch, onMsg, frozen, ftSlot, ftNext, oxQ, oxIn, tagger, tagPlayers, trSpots, trTotal, chestTap, askWord, day, ftEnd, ftLoad, oxLoad, trBuild, T};
})();
window.IPLAY=IPLAY;
