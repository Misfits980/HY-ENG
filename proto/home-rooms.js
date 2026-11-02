/* (v536) 🏠 집 안 넓히기 — (v553) 다시: 한 공간 + 칸막이 · 넓힐 방향·방 위치는 아이가 정함
   사용자: "사서 넓히고 애들이 하게 해 줘야지 · 어디로 넓힐지는 그 아이들의 선택" → "문을 다 구역으로 만들면 배치를 자유롭게 할 수 있을까?" → (한 공간 + 칸막이) "넓어지는 것도 방 위치도 아이들이 설정할 수 있게"
   · 1층 = 한 방 (6→8→10→12) · 넓힐 때 어느 쪽으로 늘릴지 고름 (↖↗↙↘ — 놓은 가구는 그대로 따라 움직임)
   · 미리 정한 문·잠긴 문 없음 → 🧱 칸막이 벽 · 🚪 아치 문을 가구처럼 놓아 방을 직접 나눔
   · 부엌·침실·욕실 = 방이 아니라 가구 세트 (🍳 스토브 · 🛏 침대 · 🛁 욕조가 어디 있든 그 일을 함)
   · 2~4층 = 🪜 계단을 원하는 곳에 놓고 눌러서 올라감 (층마다 따로 꾸밈 · 여는 조건 = 🔥 연속 공부 + 💎)
   저장: hyeng_proto_home = {c:지금 층, o:{산 것}, r:{층: roomData}, mig} · 서버 /hy/life/h/<코드>.home */
const HOMEX=(()=>{
  const R={
    living: {nm:"1층", ic:"🏠", f:0, w:0},
    f2:     {nm:"2층 공부방", ic:"📚", par:"living", st:7, gem:300, f:6, w:4, up:2, tip:"📚 내 단어 책장 · 오늘의 복습 → 💎 · 🪜 계단으로 올라가요"},
    f3:     {nm:"3층 자랑방", ic:"🏆", par:"f2", st:10, gem:450, f:7, w:2, up:3, tip:"🏆 트로피·물고기·타워 기록이 저절로 진열"},
    f4:     {nm:"4층 옥상", ic:"🌿", par:"f3", st:14, gem:600, f:5, w:5, up:4, tip:"🔭 망원경으로 친구 집 · 🪴 공부한 날마다 꽃"}
  };
  /* 가구 세트 — 사면 창고로 · 아무 데나 놓음 */
  const SETS={
    walls:  {nm:"방 나누기 세트", ic:"🧱", st:1, gem:120, items:[["partition",6],["archway",2]], tip:"🧱 칸막이 벽 6 · 🚪 아치 문 2 — 내 방을 직접 나눠요"},
    kitchen:{nm:"부엌 세트", ic:"🍳", st:2, gem:250, items:[["stove",1],["fridge",1],["table",1],["stool",2]], tip:"🍳 영어 듣고 요리 · 🧊 냉장고"},
    bedroom:{nm:"침실 세트", ic:"🛏️", st:3, gem:200, items:[["closet",1],["kk_night",1],["rug",1]], tip:"💤 침대에서 자면 꿈 카드 · 👗 옷장"},
    bath:   {nm:"욕실 세트", ic:"🛁", st:5, gem:250, items:[["bathtub",1],["mirror",1],["plant",1]], tip:"🫧 욕조에서 씻으면 ✨ 낚시 행운 10분"},
  };
  SETS.door={nm:"🚪 옆방 문", ic:"🚪", st:4, gem:250, rep:1, tip:"원하는 벽에 달면 문 너머에 <b>새 방</b> (따로 꾸밈·넓히기) · 6개까지"};
  const ORDER=["walls","door","kitchen","bedroom","bath","f2","f3","f4"];
  const NEXT={living:"f2", f2:"f3", f3:"f4"};
  let H=store("hyeng_proto_home"); if(!H || typeof H!=="object" || !H.o) H={c:"living", o:{living:1}, r:{}, mig:553};
  let vcur="living";
  const save=()=>store("hyeng_proto_home", H);
  const inVisit=()=>!!visiting;
  const isAx=id=>/^a\d+$/.test(id||"");
  const axMap=()=>(inVisit() ? ((visiting.data||{}).home||{}).ax : H.ax)||{};
  /* (v557) 🚪 옆방 = 벽에 단 문(sidedoor, c = 옆방 번호) 너머의 방 */
  const rinfo=id=>R[id] || (isAx(id) ? {nm:"옆방 "+id.slice(1), ic:"🚪", par:(axMap()[id.slice(1)]||{}).par||"living", f:3, w:1} : R.living);
  const cur=()=>inVisit() ? vcur : (R[H.c] || isAx(H.c) ? H.c : "living");
  const floorOf=id=>{ let k=id, n=0; while(isAx(k) && n++<10) k=rinfo(k).par; return k; };
  const opened=id=>{ if(inVisit()){ const h=(visiting.data||{}).home; return id==="living" || !!(h && h.o && h.o[id]); } return !!H.o[id]; };
  /* 문 = 나가는 문 하나 (1층 = 밖 · 위층 = 아래층) */
  function slots(id, rn){ id=id||cur(); rn=rn||RN; return [{side:3, s:rn-1, to:id==="living"?"out":rinfo(id).par||"living", back:1}]; }
  const sdoors=()=>wplaced.filter(w=>w.id==="sidedoor");
  const fcell=sl=>[[sl.s,0],[RN-1,sl.s],[sl.s,RN-1],[0,sl.s]][sl.side];
  const outPt=sl=>[[sl.s+.5,-.12],[RN+.12,sl.s+.5],[sl.s+.5,RN+.12],[-.12,sl.s+.5]][sl.side];
  function cells(){ return slots().map(fcell).concat(sdoors().map(w=>fcell({side:w.side, s:w.s}))); }
  function isSlot(side,s){ return slots().some(sl=>sl.side===side && sl.s===s); }
  function doors(){ dirty=true; }
  function labels(base){ const L=base.filter(d=>d.k!=="door"); const c=cur();
    slots().forEach(sl=>{ const p=[.12,1.3,sl.s+.5]; const t=sl.to==="out" ? ["🚪","나가기"] : isAx(c) ? ["🚪", ro(sl.to==="living" ? "거실" : rinfo(sl.to).nm)+" 돌아가기"] : ["🪜", rinfo(sl.to).nm+" (아래층)"]; L.push({k:"door", ic:t[0], t:t[1], p, act:exitRoom, show:()=>walls[3].visible}); });
    sdoors().forEach(w=>{ const sd=w.side, s=w.s, p=sd===0 ? [s+.5,1.3,.12] : sd===3 ? [.12,1.3,s+.5] : sd===1 ? [RN-.12,1.3,s+.5] : [s+.5,1.3,RN-.12]; L.push({k:"sd_"+w.c, ic:"🚪", t:"옆방 "+w.c, p, act:()=>annex(w), show:()=>walls[sd].visible}); });
    return L; }
  /* 층 데이터 */
  function data(id){ if(inVisit()){ const d=visiting.data||{}, h=d.home||{}; const rr=(h.r||{})[id]; if(rr) return rr; if(id===(h.c||"living")) return d; return dflt(id); }
    return id===H.c ? roomData() : (H.r[id] || dflt(id)); }
  const FIX={f2:[["bookcase",2,0,0],["desk",3,3,0],["chair",3,4,2],["kk_books",5,0,0],["stairs",5,3,0]], f3:[["trophy",2,0,0],["kk_rug",2,2,0],["kk_armchair",4,3,3],["stairs",5,3,0]], f4:[["telescope",4,1,0],["planter",2,0,0],["planter",3,0,0],["planter",5,3,0],["stool",2,3,0]]};
  const FIXW={f4:[["window",3,3,1]]};
  function dflt(id){ if(isAx(id)) return {p:[], wl:[["window",0,2,0]], f:3, w:1, rn:6}; const r=R[id]||R.living; return {p:(FIX[id]||[]).map(x=>x.concat([0])), wl:FIXW[id]||[["window",0,r.up?3:2,0],["window",3,3,1]], f:Math.min(FLOORS.length-1,r.f|0), w:Math.min(WALLS.length-1,r.w|0), rn:6}; }
  function load(D, host){ placed.splice(0).concat(wplaced.splice(0)).forEach(p=>p.obj.parent && p.obj.parent.remove(p.obj));
    if(host){ if(hostDoll){ roomG.remove(hostDoll.g); hostDoll=null; } buildShell(Math.max(6,Math.min(12,D.rn|0||6))); floorIx=Math.min(FLOORS.length-1,D.f|0); wallIx=Math.min(WALLS.length-1,D.w|0); setFloor(floorIx); setWall(wallIx);
      (D.p||[]).slice(0,120).forEach(([id,x,z,r,c])=>{ if(ITEMS[id] && !ITEMS[id].wall && fits(id,x,z,r,null,true)){ const p=addPlaced(id,x,z,r,c); p.host=1; } });
      (D.wl||[]).slice(0,40).forEach(([id,sd,s,c])=>{ if(ITEMS[id] && ITEMS[id].wall && wallFits(sd,s)) addWall(id,sd,s,c); }); }
    else loadRoomData(Object.assign({}, D, {s:null})); }
  function swapTo(id){ const from=cur(); if(inVisit()){ vcur=id; load(data(id), true); }
    else { H.r[from]=roomData(); H.c=id; const D=H.r[id] || dflt(id); delete H.r[id]; load(D, false); save(); saveRoom(); }
    doors(); return id==="living" ? null : slots()[0]; }
  /* 🪜 계단 옆 칸 (1층으로 내려왔을 때 · 위층에 올라갈 때 섬) */
  function nearStairs(){ const st=placed.find(p=>p.id==="stairs"); if(!st) return null; for(const [dx,dz] of [[0,1],[1,0],[-1,0],[0,-1],[1,1],[-1,1]]){ const x=st.x+dx, z=st.z+dz; if(x>=0&&z>=0&&x<RN&&z<RN && !roomBlocked(x,z)) return [x,z]; } return null; }
  function moveTo(to){ const key=place.key, from=cur(); let back=null, st=null;
    go(key, null, ()=>{ back=swapTo(to); if(isAx(from) && rinfo(from).par===to){ const d=sdoors().find(w=>"a"+w.c===from); if(d) back={side:d.side, s:d.s}; }
      st=back ? fcell(back) : (nearStairs()||[1,RN-1]); PL[key].start=st; PL[key].name=(inVisit() ? "🏠 "+(visiting.n||"")+" 의 집 · " : "🏠 ")+(to==="living"?"내 집":rinfo(to).nm); },
      {from:()=>back ? outPt(back) : [st[0]+.5, st[1]+.5], door:null}); try{ tEv("room_"+to); }catch(e){} }
  function go2(to){ if(F.st!=="idle" || trip.busy) return; if(!opened(to)){ if(!inVisit()) openUp(to); return; } moveTo(to); }
  /* (v561) QA: 위층에서 계단을 누르면 올라가기만 돼서 헷갈림 → 위층에서는 「⬆ 위층 · ⬇ 아래층」 고르기 */
  const ro=w=>{ const c=String(w).replace(/[^가-힣]/g,"").slice(-1), j=c ? (c.charCodeAt(0)-0xac00)%28 : 0; return w+(j && j!==8 ? "으로" : "로"); };   /* 받침 있으면 으로 (ㄹ 받침은 로) */
  function stairs(pick){ const c=floorOf(cur()), nx=NEXT[c], dn=c!=="living" ? (R[c].par||"living") : null;
    if(dn && pick!==1){ const A=$("ask"), ok=$("askOk");
      ask('🪜 <b>계단</b> — 어디로 갈까요?<div class="hxPick">'+(nx?'<button class="btn on" data-sp="u">⬆ '+R[nx].nm+'</button>':'')+'<button class="btn on" data-sp="d">⬇ '+R[dn].nm+'</button></div>', null); ok.hidden=true;
      const h=e=>{ const b=e.target.closest("[data-sp]"); if(!b && !e.target.closest("#askNo") && e.target!==A) return; A.removeEventListener("click", h, true); ok.hidden=false; if(b){ A.classList.remove("on"); if(b.dataset.sp==="d"){ try{ SND.pop(); }catch(_){} moveTo(dn); } else stairs(1); } };
      A.addEventListener("click", h, true); return; }
    if(!nx){ toast("🌿 여기가 꼭대기 층이에요", 1500); return; }
    if(!opened(nx)){ if(inVisit()){ toast("🪜 친구는 아직 "+R[nx].nm+"이 없어요", 1600); return; } toast("🪜 <b>🏗 넓히기</b>에서 "+R[nx].nm+"을 열면 올라가요", 2200); openUp(nx); return; }
    try{ SND.pop(); }catch(e){} moveTo(nx); }
  function back(){ const c=cur(); if(c==="living") return; const sl=slots()[0]; leaveBy(fcell(sl), outPt(sl), ()=>moveTo(rinfo(c).par), roomDoor); }
  /* 🚪 옆방 — 문을 처음 달면 새 번호 (치웠다가 다시 달면 예전 옆방을 다시 씀) */
  function newAnnex(){ H.ax=H.ax||{}; const used={}; const scan=wl=>(wl||[]).forEach(w=>{ if(w[0]==="sidedoor" && w[3]>0) used[w[3]]=1; }); Object.values(H.r||{}).forEach(r=>scan(r && r.wl)); wplaced.forEach(w=>{ if(w.id==="sidedoor" && w.c>0) used[w.c]=1; });
    let n=Object.keys(H.ax).map(Number).sort((a,b)=>a-b).find(k=>!used[k]); if(!n){ n=1; while(H.ax[n] || used[n]) n++; } H.ax[n]=Object.assign(H.ax[n]||{}, {par:cur()}); save(); return n; }
  function annex(w){ if(F.st!=="idle" || trip.busy || !w || !(w.c>0)) return; const id="a"+w.c;
    if(inVisit()){ const h=(visiting.data||{}).home||{}; if(!(h.ax||{})[w.c]){ toast("🚪 아직 빈 방이에요", 1400); return; } }
    else { H.ax=H.ax||{}; H.ax[w.c]=Object.assign(H.ax[w.c]||{}, {par:cur()}); save(); }
    const sl={side:w.side, s:w.s}; leaveBy(fcell(sl), outPt(sl), ()=>moveTo(id), (w.obj && w.obj.userData.door)||null); }
  function toLiving(){ if(H.c!=="living"){ H.r[H.c]=roomData(); H.c="living"; const D=H.r.living || dflt("living"); delete H.r.living; load(D,false); save(); saveRoom(); } PL.room.name="🏠 내 집"; }
  function visitStart(d){ vcur="living"; const h=d && d.home; if(h && h.c && h.c!=="living" && h.r && h.r.living) return Object.assign({}, d, h.r.living); return d; }
  function pub(){ const r=Object.assign({}, H.r); r[H.c]=roomData(); return {c:H.c, o:H.o, ax:H.ax||{}, r}; }
  /* 🔥 연속 공부 */
  function streak(){ try{ const s=JSON.parse(localStorage.getItem("hyeng_study_v1")||"{}"), d=s.days||{}; const today=Math.floor((Date.now()-new Date().getTimezoneOffset()*60000)/864e5);
      const live=d.last && today-d.last<=3 ? (d.hs||d.n||0) : 0; return {best:Math.max(d.hb||0, d.hs||0, d.n||0), now:live, tot:d.tot||d.n||0}; }catch(e){ return {best:0, now:0, tot:0}; } }
  const floors=()=>1+["f2","f3","f4"].filter(k=>H.o[k]).length;
  const info=id=>SETS[id]||R[id];
  const axCount=()=>Object.keys(H.ax||{}).length+(stock.sidedoor|0);
  function state(id){ const r=info(id), S=streak(); if(id==="door"){ if(axCount()>=6) return "have"; } else if(H.o[id]) return "have"; if(r.par && R[r.par] && !H.o[r.par]) return "par"; if(S.best<r.st) return "streak"; if(gems<r.gem) return "gem"; return "ok"; }
  function unlock(id){ const r=info(id); if(state(id)!=="ok") return false; if(!spend(r.gem)) return false; if(id==="door"){ addStock("sidedoor"); saveRoom(); try{ SND.big(); tEv("roomup"); }catch(e){} toast("🚪 <b>옆방 문</b> → 🏠 창고<br><small>🛋️ 가구에서 골라 <b>원하는 벽</b>에 달아요 · 문을 누르면 새 방!</small>", 3400); drawUp(); return true; }
    H.o[id]=1; save();
    if(SETS[id]) r.items.forEach(([it,n])=>{ if(ITEMS[it]) for(let i=0;i<n;i++) addStock(it); });
    if(id==="f2") addStock("stairs");
    try{ saveRoom(); }catch(e){} try{ tEv("roomup"); }catch(e){} try{ SND.big(); act("yay"); emote(hero,"🎉"); }catch(e){}
    toast(SETS[id] ? "🎉 <b>"+r.ic+" "+r.nm+"</b> → 🏠 창고<br><small>🛋️ 가구 단추로 <b>원하는 곳</b>에 놓아요</small>"
      : "🎉 <b>"+r.ic+" "+r.nm+"</b> 이 생겼어요!<br><small>"+(id==="f2"?"🪜 계단이 창고에 들어갔어요 — 원하는 곳에 놓고 눌러요":"🪜 아래층 계단을 눌러 올라가요")+" · 바깥 집도 "+floors()+"층</small>", 3400);
    try{ if(window.ISLE) ISLE.syncMine(); }catch(e){} drawUp(); return true; }
  /* 📐 넓히기 — 어느 쪽으로 늘릴지 (dx = 왼쪽 벽 쪽 · dz = 오른쪽 벽 쪽 · 놓은 가구·벽 물건은 그대로 따라감) */
  const DIRS=[["lr","↑","뒤쪽",1,1],["l","↖","왼쪽",1,0],["r","↗","오른쪽",0,1],["f","↓","앞쪽",0,0]];
  function grow(dir){ if(inVisit()) return false; const u=ROOM_UP.find(x=>x[0]>RN); if(!u) return false; if(!spend(u[1])) return false;
    const D0=DIRS.find(d=>d[0]===dir)||DIRS[0], d=u[0]-RN, dx=D0[3]?d:0, dz=D0[4]?d:0, D=roomData();
    D.p=D.p.map(([id,x,z,r,c])=>[id,x+dx,z+dz,r,c]); D.wl=D.wl.map(([id,sd,s,c])=>[id,sd,s+((sd===0||sd===2)?dx:dz),c]); D.rn=u[0];
    loadRoomData(Object.assign({}, D, {s:null})); try{ hero.cx=Math.min(RN-1,hero.cx+dx); hero.cz=Math.min(RN-1,hero.cz+dz); hero.g.position.set(hero.cx+.5,0,hero.cz+.5); hero.path=[]; }catch(e){}
    saveRoom(); PL.room.N=RN; try{ setShadow(); placeCamera(); drawInv(); drawLabels(); }catch(e){} try{ tEv("roomup"); SND.big(); }catch(e){}
    toast("🏠 "+(cur()==="living"?"집":rinfo(cur()).nm)+"이 <b>"+RN+"×"+RN+"</b> 이 됐어요!<br><small>"+D0[1]+" "+D0[2]+" 으로 넓어졌어요</small>", 2400); drawUp(); return true; }
  function dirSVG(dx,dz,o,n){ const k=34/n, P=(x,z)=>[(x-z)*k+40, (x+z)*k/2+4], poly=pts=>pts.map(p=>P(p[0],p[1]).map(v=>v.toFixed(1)).join(",")).join(" ");
    return '<svg viewBox="0 0 80 44" style="width:100%;max-width:80px;height:auto;display:block"><polygon points="'+poly([[0,0],[n,0],[n,n],[0,n]])+'" fill="#c9efbd" stroke="#4caf50" stroke-width="1.5"/><polygon points="'+poly([[dx,dz],[dx+o,dz],[dx+o,dz+o],[dx,dz+o]])+'" fill="#ffe9c2" stroke="#3b2433" stroke-width="1.5"/></svg>'; }
  /* 기존 아이 — 방(부엌·침실·욕실)에 있던 가구는 모두 창고로 · 위층이 있으면 🪜 계단 */
  function migrate(){ if(inVisit() || H.mig>=553) return; let n=0; const give=id=>{ if(ITEMS[id] && id!=="stairs"){ addStock(id); n++; } };
    ["kitchen","bedroom","bath"].forEach(k=>{ if(H.c===k){ const D=roomData(); D.p.forEach(p=>give(p[0])); D.wl.forEach(w=>give(w[0])); H.c="living"; const L=H.r.living||dflt("living"); delete H.r.living; load(L,false); }
      else if(H.r[k]){ (H.r[k].p||[]).forEach(p=>give(p[0])); (H.r[k].wl||[]).forEach(w=>give(w[0])); } delete H.r[k]; });
    ["f2","f3","f4"].forEach(k=>{ if(H.o[k]) addStock("stairs"); });
    H.mig=553; save(); try{ saveRoom(); }catch(e){} if(n) setTimeout(()=>{ try{ toast("🏠 집이 <b>한 공간</b>으로 바뀌었어요!<br><small>부엌·침실 가구 "+n+"개는 🛋️ 창고에 — 원하는 곳에 놓아요</small>", 3600); }catch(e){} }, 1500); }
  /* 🏗 넓히기 창 */
  function css(){ if($("upP")) return; const st=document.createElement("style"); st.textContent=`
.hxPick{display:flex;gap:8px;justify-content:center;margin-top:10px;flex-wrap:wrap}.hxPick .btn{min-width:120px}
#upP{position:fixed;inset:0;z-index:20;display:none;background:rgba(30,18,40,.42);align-items:flex-end;justify-content:center} #upP.on{display:flex}
#upP .lb{width:min(560px,100%);max-height:92vh;overflow:auto;background:#fff8ea;border:3px solid #3b2433;border-bottom:0;border-radius:26px 26px 0 0;padding:12px 14px calc(16px + env(safe-area-inset-bottom));font-family:var(--kr);color:#3b2433}
#upP h3{margin:2px 4px 6px;font-weight:400;font-size:21px;display:flex;align-items:center;gap:8px}#upP h3 small{font-size:12px;color:#9a7e63;flex:1}
#upP h4{margin:10px 4px 6px;font-weight:400;font-size:15px}
#upP .x{width:38px;height:38px;border-radius:50%;border:3px solid #3b2433;background:#fffdf7;box-shadow:0 3px 0 #3b2433;font-size:16px;color:#3b2433}
.upS{display:flex;align-items:center;gap:10px;margin:2px 2px 10px;padding:8px 12px;border-radius:16px;background:#fff1d0;border:2.5px solid #3b2433;font-size:14px}
.upS b{font-size:22px;font-weight:400}.upS i{font-style:normal;font-size:26px}
.upDir{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:6px;margin-bottom:8px}
.upDir button{border:3px solid #3b2433;border-radius:14px;background:#fffdf7;box-shadow:0 3px 0 #3b2433;padding:4px 2px;font:12px var(--kr);color:#3b2433;display:flex;flex-direction:column;align-items:center}
.upDir button[disabled]{opacity:.45}
.upR{display:flex;align-items:center;gap:10px;background:#fffdf7;border:3px solid #3b2433;border-radius:18px;padding:7px 10px;box-shadow:0 3px 0 #3b2433;margin-bottom:8px}
.upR.hot{outline:4px solid #ffd23f}
.upR .ic{width:46px;height:46px;border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:27px;border:2.5px solid #3b2433;background:#fff1d0;flex:none}
.upR b{display:block;font-weight:400;font-size:16px}.upR small{display:block;font-size:12px;color:#8a6a4a;line-height:1.35}
.upR .go{margin-left:auto;height:44px;padding:0 12px;border-radius:14px;border:3px solid #3b2433;box-shadow:0 3px 0 #3b2433;font:15px var(--kr);white-space:nowrap;color:#fff;background:linear-gradient(180deg,#86dc7c,#4caf50);flex:none}
.upR .go[disabled]{background:#e8dfd0;color:#8a7a6a}
.upR.have{opacity:.6}.upR.have .go{background:#fff;color:#4caf50}
.upBar{height:8px;width:110px;border-radius:5px;border:2px solid #3b2433;background:#eadfcb;overflow:hidden;margin-top:3px}.upBar i{display:block;height:100%;background:#ff9a3d}`; document.head.appendChild(st);
    const d=document.createElement("div"); d.id="upP"; d.innerHTML='<div class="lb"><h3>🏗 집 넓히기<small>공부를 <b>이어서</b> 하면 열려요 · 토·일은 쉬어도 이어져요</small><button class="x" id="upX" aria-label="닫기">✕</button></h3><div id="upB"></div></div>'; document.body.appendChild(d);
    d.addEventListener("click", e=>{ if(e.target===d || e.target.id==="upX"){ d.classList.remove("on"); return; } const g=e.target.closest("[data-grow]"); if(g && !g.disabled){ const D0=DIRS.find(x=>x[0]===g.dataset.grow); ask(D0[1]+" <b>"+D0[2]+"</b>으로 넓힐까요?<br><small>💎 "+(ROOM_UP.find(x=>x[0]>RN)||[0,0])[1]+" · 놓은 가구는 그대로예요</small>", ()=>grow(g.dataset.grow)); return; }
      const b=e.target.closest("[data-up]"); if(!b) return; const k=b.dataset.up, r=info(k); const nm=String(r.nm).replace(/^\S+\s/, m=>m.trim()===r.ic?"":m), last=nm.replace(/[^가-힣]/g,"").slice(-1), jo=last && (last.charCodeAt(0)-0xac00)%28 ? "을" : "를";   /* (v561) QA: 「세트을」 → 받침 보고 을/를 · 「🚪 🚪 옆방 문」 그림 두 번 */
      ask(r.ic+" <b>"+nm+"</b>"+jo+" 살까요?<br><small>💎 "+r.gem+(SETS[k]?" · 창고에 들어가요":"")+" · 가진 💎 "+gems+"</small>", ()=>unlock(k)); });
    ["pointerdown","pointerup"].forEach(ev=>d.addEventListener(ev, e=>e.stopPropagation())); try{ SHEETS.push("upP"); }catch(e){} }
  let hot=null;
  function drawUp(){ if(!$("upB")) return; const S=streak(), u=ROOM_UP.find(x=>x[0]>RN), c=cur();
    let h='<div class="upS"><i>🔥</i><div><b>연속 '+S.now+'일</b> <small>· 가장 긴 연속 '+S.best+'일 · 공부한 날 '+S.tot+'일</small><br><small>Daily 30 을 하면 하루가 쌓여요</small></div></div>';
    h+='<h4>📐 '+(c==="living"?"집":rinfo(c).nm)+' 넓히기 · 지금 '+RN+'×'+RN+(u?' → '+u[0]+'×'+u[0]+' · 💎 '+u[1]:' · 가장 커요')+'</h4>';
    if(u){ const d=u[0]-RN; h+='<div class="upDir">'+DIRS.map(D=>'<button data-grow="'+D[0]+'"'+(gems<u[1]?' disabled':'')+'>'+dirSVG(D[3]?d:0, D[4]?d:0, RN, u[0])+'<span>'+D[1]+' '+D[2]+'</span></button>').join("")+'</div>'+(gems<u[1]?'<p style="margin:0 4px 6px;font-size:12px;color:#8a6a4a">💎 '+(u[1]-gems)+'개 더 모으면 넓힐 수 있어요</p>':''); }
    h+='<h4>🛋 가구 세트 · 🪜 위층</h4>';
    ORDER.forEach(k=>{ const r=info(k), st=state(k), need=Math.max(0,r.st-S.best);
      const btn=st==="have" ? '<button class="go" disabled>'+(k==="door"?'✅ 6개':'✅ 있음')+'</button>' : st==="ok" ? '<button class="go" data-up="'+k+'">💎 '+r.gem+' 사기</button>'
        : st==="par" ? '<button class="go" disabled>🔒 '+R[r.par].nm+' 먼저</button>' : st==="streak" ? '<button class="go" disabled>🔥 '+need+'일 더</button>' : '<button class="go" disabled>💎 '+(r.gem-gems)+' 더</button>';
      h+='<div class="upR'+(st==="have"?" have":"")+(hot===k?" hot":"")+'" data-row="'+k+'"><div class="ic">'+r.ic+'</div><div><b>'+r.nm+'</b><small>'+r.tip+'<br>🔥 연속 '+r.st+'일 + 💎 '+r.gem+'</small>'+(st==="streak"?'<div class="upBar"><i style="width:'+Math.round(Math.min(1,S.best/r.st)*100)+'%"></i></div>':'')+'</div>'+btn+'</div>'; });
    $("upB").innerHTML=h; }
  function openUp(k){ if(inVisit()) return; css(); hot=k||null; drawUp(); try{ SHEETS.forEach(id=>{ const e=$(id); if(e && id!=="upP") e.classList.remove("on"); }); }catch(e){} $("upP").classList.add("on"); $("upP").querySelectorAll("*").forEach(e=>{ if(e.scrollTop) e.scrollTop=0; });   /* (v561) QA: 다시 열면 맨 아래부터 보이던 것 */
    if(k) setTimeout(()=>{ const r=document.querySelector('[data-row="'+k+'"]'); if(r) r.scrollIntoView({block:"center"}); }, 60); }
  function tap(){ return false; }
  function init(){ migrate(); doors(); try{ PL.room.name="🏠 "+(cur()==="living"?"내 집":rinfo(cur()).nm); }catch(e){} try{ drawLabels(); }catch(e){} }
  return {R, SETS, ORDER, DIRS, newAnnex, annex, rinfo, isAx, H:()=>H, cur, slots, cells, isSlot, doors, labels, go2, moveTo, back, toLiving, visitStart, pub, streak, floors, state, unlock, grow, stairs, openUp, drawUp, tap, init, opened, save, migrate};
})();
window.HOMEX=HOMEX;
