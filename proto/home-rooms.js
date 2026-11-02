/* (v536) 🏠 집 안 넓히기 — 방이 하나씩 늘어남 (문 자리는 처음부터 정해 둠)
   사용자: "집안도 늘릴 수 있는 기능이 있어야 해" · "몇 일 연속 들어와서 공부해야 보상받는 느낌" · "2층 다락 추천 · 3층 4층 가능성도"
   방 = 거실(처음) · 🍳 부엌 · 🛏 침실 · 🛁 욕실(침실 안쪽) · 🪜 2층 · 3층 · 🌿 4층 옥상 — 여는 조건 = 🔥 연속 공부(가장 긴 연속, 토·일은 쉬어도 이어짐) + 💎
   방마다 가구·벽지·바닥·크기(6→8→10) 따로 · 문으로 걸어서 이동(짧은 페이드) · 친구가 놀러 오면 열린 방을 다 구경
   문 자리: 모든 방의 왼쪽 벽 맨 앞(side 3, RN-1) = 앞 방(거실은 밖) · 뒷벽(side 0) 1칸 = 위층 계단 · 뒷벽 RN-2 칸 = 옆방 · 왼쪽 벽(side 3) 1칸 = 거실→침실
   저장: hyeng_proto_home = {c:지금 방, o:{열린 방}, r:{방: roomData}} (지금 방의 가구는 hyeng_proto_room 이 정본) · 서버 /hy/life/h/<코드>.home */
const HOMEX=(()=>{
  const R={
    living: {nm:"거실", ic:"🛋️", f:0, w:0},
    kitchen:{nm:"부엌", ic:"🍳", par:"living", sl:[0,"R"], st:2, gem:20, f:1, w:3, tip:"🍳 영어 듣고 요리 · 🧊 냉장고"},
    bedroom:{nm:"침실", ic:"🛏️", par:"living", sl:[3,1], st:3, gem:40, f:2, w:1, tip:"💤 침대에서 자면 꿈 카드 (하루 한 번 💎) · 👗 옷장"},
    bath:   {nm:"욕실", ic:"🛁", par:"bedroom", sl:[0,"R"], st:5, gem:60, f:8, w:5, tip:"🫧 씻으면 ✨ 낚시 행운 10분"},
    f2:     {nm:"2층 공부방", ic:"📚", par:"living", sl:[0,1], st:7, gem:80, f:6, w:4, up:2, tip:"📚 내 단어 책장 · 오늘의 복습 → 💎"},
    f3:     {nm:"3층 자랑방", ic:"🏆", par:"f2", sl:[0,1], st:10, gem:120, f:7, w:2, up:3, tip:"🏆 트로피·물고기·타워 기록이 저절로 진열"},
    f4:     {nm:"4층 옥상", ic:"🌿", par:"f3", sl:[0,1], st:14, gem:160, f:5, w:5, up:4, tip:"🔭 망원경으로 친구 집 · 🪴 공부한 날마다 꽃"}
  };
  const ORDER=["kitchen","bedroom","bath","f2","f3","f4"];
  let H=store("hyeng_proto_home"); if(!H || typeof H!=="object" || !H.o) H={c:"living", o:{living:1}, r:{}};
  if(!R[H.c]) H.c="living";
  let vcur="living";   // 친구 집에서 지금 방
  const save=()=>store("hyeng_proto_home", H);
  const inVisit=()=>!!visiting;   /* 친구/마을 사람 집 (자리 잡는 중에도 — 아직 place 가 바뀌기 전) */
  const cur=()=>inVisit() ? vcur : H.c;
  const opened=id=>{ if(inVisit()){ const h=(visiting.data||{}).home; return id==="living" || !!(h && h.o && h.o[id]); } return !!H.o[id]; };
  /* 이 방의 문 자리 [{side, s, to}] — 앞 문(side3·RN-1) + 자식 방 문 */
  function slots(id, rn){ id=id||cur(); rn=rn||RN; const L=[{side:3, s:rn-1, to:id==="living"?"out":R[id].par, back:1}];
    if(inVisit() && (visiting.npc || !(visiting.data||{}).home)) return L;   /* 마을 사람 집 · 예전 집 = 방 문 없음 */
    Object.keys(R).forEach(k=>{ const r=R[k]; if(r.par!==id) return; L.push({side:r.sl[0], s:r.sl[1]==="R"?rn-2:r.sl[1], to:k}); }); return L; }
  const fcell=sl=>[[sl.s,0],[RN-1,sl.s],[sl.s,RN-1],[0,sl.s]][sl.side];
  const outPt=sl=>[[sl.s+.5,-.12],[RN+.12,sl.s+.5],[sl.s+.5,RN+.12],[-.12,sl.s+.5]][sl.side];
  function cells(){ return slots().map(fcell); }
  function isSlot(side,s){ return slots().some(sl=>sl.side===side && sl.s===s); }
  /* 문 그림 — 잠긴 문 = 판자 X + 🔒 · 계단 문 = 밝은 나무 */
  const DC={}; let built=[];
  function doorFor(to){ if(DC[to]) return DC[to]; const up=to && R[to] && R[to].up, D=makeDoor(.84,1.95, up?0xd9a46c:0x9a6a40, true); D.userData.hto=to; D.traverse(m=>{ m.userData.hto=to; });
    const pl=new THREE.Group(); [[.6,1],[-.6,1]].forEach(([a])=>{ const b=new THREE.Mesh(rbox(1.0,.16,.06,.02), M(0xc48a58)); b.rotation.z=a; b.position.set(0,1.0,.1); pl.add(b); }); D.add(pl); D.userData.planks=pl; return DC[to]=D; }
  function doors(){ built.forEach(D=>{ if(D.parent) D.parent.remove(D); }); built=[];
    if(!walls.length) return; slots().forEach(sl=>{ if(sl.back) return; const D=doorFor(sl.to); walls[sl.side].add(D); D.position.set(wallLX(sl.side,sl.s),0,WT/2+.01); D.userData.planks.visible=!opened(sl.to); built.push(D); }); dirty=true; }
  /* 이름표 */
  function labels(base){ const L=base.filter(d=>d.k!=="door"); const c=cur();
    slots().forEach(sl=>{ const p=sl.side===0 ? [sl.s+.5,1.3,.12] : sl.side===3 ? [.12,1.3,sl.s+.5] : sl.side===1 ? [RN-.12,1.3,sl.s+.5] : [sl.s+.5,1.3,RN-.12];
      if(sl.back){ const t=sl.to==="out" ? ["🚪","나가기"] : [R[sl.to].up||R[c].up ? "🪜" : R[sl.to].ic, (R[sl.to].nm)+(R[c].up?" (아래층)":"로")]; L.push({k:"door", ic:t[0], t:t[1], p, act:exitRoom, show:()=>walls[3].visible}); return; }
      const r=R[sl.to], op=opened(sl.to); if(!op && inVisit()) return;
      L.push({k:"hd_"+sl.to, ic:op?r.ic:"🔒", t:op?r.nm:r.nm+" 🔥"+r.st+"일", p, act:()=>go2(sl.to), show:()=>walls[sl.side].visible}); });
    return L; }
  /* 방 옮기기 */
  function data(id){ if(inVisit()){ const d=visiting.data||{}, h=d.home||{}; const rr=(h.r||{})[id]; if(rr) return rr; if(id===(h.c||"living")) return d; return dflt(id); }
    return id===H.c ? roomData() : (H.r[id] || dflt(id)); }
  /* (v539) 방마다 처음 들어 있는 가구 — 그 방에서만 하는 일 (문 자리는 비움) */
  const FIX={kitchen:[["stove",2,0,0],["fridge",3,0,0],["table",3,3,0],["stool",2,3,1]], bedroom:[["closet",2,0,0],["kk_night",5,0,0],["bed",5,2,0],["rug",2,2,0]], bath:[["bathtub",2,0,0],["plant",5,0,0]],
    f2:[["bookcase",2,0,0],["desk",3,3,0],["chair",3,4,2],["kk_books",5,0,0]], f3:[["trophy",2,0,0],["kk_rug",2,2,0],["kk_armchair",4,3,3]], f4:[["telescope",4,1,0],["planter",2,0,0],["planter",3,0,0],["planter",5,3,0],["stool",2,3,0]]};
  const FIXW={bath:[["mirror",0,4,0],["window",3,3,1]], f4:[["window",3,3,1]]};
  function dflt(id){ const r=R[id]||R.living; return {p:(FIX[id]||[]).map(x=>x.concat([0])), wl:FIXW[id]||[["window",0,r.up?3:2,0],["window",3,3,1]], f:Math.min(FLOORS.length-1,r.f|0), w:Math.min(WALLS.length-1,r.w|0), rn:6}; }
  function load(D, host){ placed.splice(0).concat(wplaced.splice(0)).forEach(p=>p.obj.parent && p.obj.parent.remove(p.obj));
    if(host){ if(hostDoll){ roomG.remove(hostDoll.g); hostDoll=null; } buildShell(Math.max(6,Math.min(10,D.rn|0||6))); floorIx=Math.min(FLOORS.length-1,D.f|0); wallIx=Math.min(WALLS.length-1,D.w|0); setFloor(floorIx); setWall(wallIx);
      (D.p||[]).slice(0,90).forEach(([id,x,z,r,c])=>{ if(ITEMS[id] && !ITEMS[id].wall && fits(id,x,z,r,null,true)){ const p=addPlaced(id,x,z,r,c); p.host=1; } });
      (D.wl||[]).slice(0,40).forEach(([id,sd,s,c])=>{ if(ITEMS[id] && ITEMS[id].wall && wallFits(sd,s)) addWall(id,sd,s,c); }); }
    else loadRoomData(Object.assign({}, D, {s:null})); }
  function swapTo(id){ const from=cur(); if(inVisit()){ vcur=id; load(data(id), true); }
    else { H.r[from]=roomData(); H.c=id; const D=H.r[id] || dflt(id); delete H.r[id]; load(D, false); save(); saveRoom(); }
    doors(); const back=slots().find(sl=>id==="living" ? sl.to===from : sl.back); return back; }
  function go2(to){ if(F.st!=="idle" || trip.busy) return; if(!opened(to)){ if(!inVisit()) openUp(to); return; }
    const sl=slots().find(s=>s.to===to); if(!sl) return; const D=built.find(d=>d.userData.hto===to);
    leaveBy(fcell(sl), outPt(sl), ()=>moveTo(to), D); }
  function moveTo(to){ const key=place.key; let back=null;
    go(key, null, ()=>{ back=swapTo(to); PL[key].start=back ? fcell(back) : [1,RN-1]; PL[key].name=(inVisit() ? "🏠 "+(visiting.n||"")+" 의 집 · " : "🏠 ")+R[to].nm; },
      {from:()=>back ? outPt(back) : [0.05,RN-0.5], door:null}); try{ tEv("room_"+to); }catch(e){} }
  function back(){ const c=cur(); if(c==="living") return; const sl=slots()[0]; leaveBy(fcell(sl), outPt(sl), ()=>moveTo(R[c].par), roomDoor); }
  /* 밖에서 들어올 때 = 늘 거실 */
  function toLiving(){ if(H.c!=="living"){ H.r[H.c]=roomData(); H.c="living"; const D=H.r.living || dflt("living"); delete H.r.living; load(D,false); save(); saveRoom(); doors(); } PL.room.name="🏠 내 집"; }
  function visitStart(d){ vcur="living"; const h=d && d.home; if(h && h.c && h.c!=="living" && h.r && h.r.living) return Object.assign({}, d, h.r.living); return d; }
  function pub(){ const r=Object.assign({}, H.r); r[H.c]=roomData(); return {c:H.c, o:H.o, r}; }
  /* 🔥 연속 공부 */
  function streak(){ try{ const s=JSON.parse(localStorage.getItem("hyeng_study_v1")||"{}"), d=s.days||{}; const today=Math.floor((Date.now()-new Date().getTimezoneOffset()*60000)/864e5);
      const live=d.last && today-d.last<=3 ? (d.hs||d.n||0) : 0; return {best:Math.max(d.hb||0, d.hs||0, d.n||0), now:live, tot:d.tot||d.n||0}; }catch(e){ return {best:0, now:0, tot:0}; } }
  const floors=()=>1+["f2","f3","f4"].filter(k=>H.o[k]).length;
  function state(id){ const r=R[id], S=streak(); if(H.o[id]) return "have"; if(R[r.par] && !H.o[r.par]) return "par"; if(S.best<r.st) return "streak"; if(gems<r.gem) return "gem"; return "ok"; }
  function unlock(id){ const r=R[id]; if(state(id)!=="ok") return false; if(!spend(r.gem)) return false; H.o[id]=1; save(); doors(); drawLabels(); try{ saveRoom(); }catch(e){} try{ tEv("roomup"); }catch(e){}
    try{ SND.big(); act("yay"); emote(hero,"🎉"); }catch(e){} toast("🎉 <b>"+r.ic+" "+r.nm+"</b> 이 생겼어요!<br><small>문을 눌러 들어가 봐요"+(r.up?" · 바깥 집도 "+floors()+"층이 됐어요":"")+"</small>", 3200);
    try{ if(window.ISLE) ISLE.syncMine(); }catch(e){} drawUp(); return true; }
  /* 🏗 넓히기 창 */
  function css(){ if($("upP")) return; const st=document.createElement("style"); st.textContent=`
#upP{position:fixed;inset:0;z-index:20;display:none;background:rgba(30,18,40,.42);align-items:flex-end;justify-content:center} #upP.on{display:flex}
#upP .lb{width:min(560px,100%);max-height:92vh;overflow:auto;background:#fff8ea;border:3px solid #3b2433;border-bottom:0;border-radius:26px 26px 0 0;padding:12px 14px calc(16px + env(safe-area-inset-bottom));font-family:var(--kr);color:#3b2433}
#upP h3{margin:2px 4px 6px;font-weight:400;font-size:21px;display:flex;align-items:center;gap:8px}#upP h3 small{font-size:12px;color:#9a7e63;flex:1}
#upP .x{width:38px;height:38px;border-radius:50%;border:3px solid #3b2433;background:#fffdf7;box-shadow:0 3px 0 #3b2433;font-size:16px;color:#3b2433}
.upS{display:flex;align-items:center;gap:10px;margin:2px 2px 10px;padding:8px 12px;border-radius:16px;background:#fff1d0;border:2.5px solid #3b2433;font-size:14px}
.upS b{font-size:22px;font-weight:400}.upS i{font-style:normal;font-size:26px}
#upMap{display:block;margin:0 auto 6px}
.upR{display:flex;align-items:center;gap:10px;background:#fffdf7;border:3px solid #3b2433;border-radius:18px;padding:7px 10px;box-shadow:0 3px 0 #3b2433;margin-bottom:8px}
.upR.hot{outline:4px solid #ffd23f}
.upR .ic{width:46px;height:46px;border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:27px;border:2.5px solid #3b2433;background:#fff1d0;flex:none}
.upR b{display:block;font-weight:400;font-size:16px}.upR small{display:block;font-size:12px;color:#8a6a4a;line-height:1.35}
.upR .go{margin-left:auto;height:44px;padding:0 12px;border-radius:14px;border:3px solid #3b2433;box-shadow:0 3px 0 #3b2433;font:15px var(--kr);white-space:nowrap;color:#fff;background:linear-gradient(180deg,#86dc7c,#4caf50);flex:none}
.upR .go[disabled]{background:#e8dfd0;color:#8a7a6a}
.upR.have{opacity:.6}.upR.have .go{background:#fff;color:#4caf50}
.upBar{height:8px;width:110px;border-radius:5px;border:2px solid #3b2433;background:#eadfcb;overflow:hidden;margin-top:3px}.upBar i{display:block;height:100%;background:#ff9a3d}`; document.head.appendChild(st);
    const d=document.createElement("div"); d.id="upP"; d.innerHTML='<div class="lb"><h3>🏗 집 넓히기<small>공부를 <b>이어서</b> 하면 방이 늘어나요 · 토·일은 쉬어도 이어져요</small><button class="x" id="upX" aria-label="닫기">✕</button></h3><div id="upB"></div></div>'; document.body.appendChild(d);
    d.addEventListener("click", e=>{ if(e.target===d || e.target.id==="upX"){ d.classList.remove("on"); return; } const b=e.target.closest("[data-up]"); if(!b) return; const k=b.dataset.up;
      if(k==="size"){ const u=ROOM_UP.find(x=>x[0]>RN); if(u && spend(u[1])){ growRoom(u[0]); doors(); drawLabels(); toast("🏠 "+R[cur()].nm+"이 "+u[0]+"×"+u[0]+" 이 됐어요!"); try{ tEv("roomup"); }catch(_){} drawUp(); } return; }
      const r=R[k]; ask(r.ic+" <b>"+r.nm+"</b>을 열까요?<br><small>💎 "+r.gem+"</small>", ()=>unlock(k)); });
    ["pointerdown","pointerup"].forEach(ev=>d.addEventListener(ev, e=>e.stopPropagation())); try{ SHEETS.push("upP"); }catch(e){} }
  let hot=null;
  function planSVG(){ const cell=(x,y,w,h,id)=>{ const r=R[id], o=H.o[id], c=cur()===id; return '<g><rect x="'+x+'" y="'+y+'" width="'+w+'" height="'+h+'" rx="6" fill="'+(o?(c?"#ffd86b":"#ffe9c2"):"#fffdf7")+'" stroke="#3b2433" stroke-width="2.5"'+(o?'':' stroke-dasharray="5 4"')+'/><text x="'+(x+w/2)+'" y="'+(y+h/2-2)+'" text-anchor="middle" font-size="18">'+(o?r.ic:"🔒")+'</text><text x="'+(x+w/2)+'" y="'+(y+h/2+15)+'" text-anchor="middle" font-size="11" fill="#3b2433">'+r.nm+(c?" · 지금":"")+'</text></g>'; };
    let s='<svg id="upMap" viewBox="0 0 330 150" width="330" height="150">';
    s+=cell(10,72,90,70,"bedroom")+cell(10,4,90,64,"bath")+cell(104,72,100,70,"living")+cell(208,72,90,70,"kitchen");
    s+=cell(126,40,56,28,"f2")+cell(130,10,48,26,"f3")+cell(250,8,70,52,"f4");
    s+='<text x="214" y="34" font-size="11" fill="#9a7e63">위층 →</text></svg>'; return s; }
  function drawUp(){ if(!$("upB")) return; const S=streak(), u=ROOM_UP.find(x=>x[0]>RN), c=cur();
    let h='<div class="upS"><i>🔥</i><div><b>연속 '+S.now+'일</b> <small>· 가장 긴 연속 '+S.best+'일 · 공부한 날 '+S.tot+'일</small><br><small>Daily 30 을 하면 하루가 쌓여요</small></div></div>'+planSVG();
    h+='<div class="upR"><div class="ic">'+R[c].ic+'</div><div><b>'+R[c].nm+' 크기</b><small>지금 '+RN+'×'+RN+(u?' → '+u[0]+'×'+u[0]:' · 가장 커요')+'</small></div><button class="go" data-up="size"'+(u?'':' disabled')+'>'+(u?'💎 '+u[1]:'✅ 최대')+'</button></div>';
    ORDER.forEach(k=>{ const r=R[k], st=state(k), need=Math.max(0,r.st-S.best);
      const btn=st==="have" ? '<button class="go" disabled>✅ 있음</button>' : st==="ok" ? '<button class="go" data-up="'+k+'">💎 '+r.gem+' 열기</button>'
        : st==="par" ? '<button class="go" disabled>🔒 '+R[r.par].nm+' 먼저</button>' : st==="streak" ? '<button class="go" disabled>🔥 '+need+'일 더</button>' : '<button class="go" disabled>💎 '+(r.gem-gems)+' 더</button>';
      h+='<div class="upR'+(st==="have"?" have":"")+(hot===k?" hot":"")+'" data-row="'+k+'"><div class="ic">'+r.ic+'</div><div><b>'+r.nm+'</b><small>'+r.tip+'<br>🔥 연속 '+r.st+'일 + 💎 '+r.gem+'</small>'+(st==="streak"?'<div class="upBar"><i style="width:'+Math.round(Math.min(1,S.best/r.st)*100)+'%"></i></div>':'')+'</div>'+btn+'</div>'; });
    $("upB").innerHTML=h; }
  function openUp(k){ if(inVisit()) return; css(); hot=k||null; drawUp(); try{ SHEETS.forEach(id=>{ const e=$(id); if(e && id!=="upP") e.classList.remove("on"); }); }catch(e){} $("upP").classList.add("on");
    if(k) setTimeout(()=>{ const r=document.querySelector('[data-row="'+k+'"]'); if(r) r.scrollIntoView({block:"center"}); }, 60); }
  /* 눌렀을 때 — 문 */
  function tap(e){ if(!(place===PL.room || place===PL.visit)) return false; const D=built.filter(d=>d.parent && d.parent.visible); if(!D.length) return false;
    ndc.set(e.clientX/innerWidth*2-1, -(e.clientY/innerHeight)*2+1); ray.setFromCamera(ndc, camera); const h=ray.intersectObjects(D, true)[0]; if(!h) return false;
    let o=h.object; while(o && !o.userData.hto) o=o.parent; if(!o) return false; go2(o.userData.hto); return true; }
  function init(){ doors(); try{ PL.room.name="🏠 "+(H.c==="living"?"내 집":R[H.c].nm); }catch(e){} try{ drawLabels(); }catch(e){} }
  return {R, ORDER, H:()=>H, cur, slots, cells, isSlot, doors, labels, go2, moveTo, back, toLiving, visitStart, pub, streak, floors, state, unlock, openUp, drawUp, tap, init, opened, save};
})();
window.HOMEX=HOMEX;
