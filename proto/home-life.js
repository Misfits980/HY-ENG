/* (v539) 🏠 집 안 생활 — 방·층마다 할 일 + 🛒 마트 + 🍳 요리 듣기 놀이 + 새 시작(마을 광장 → 땅 → 집 → 입주 선물)
   사용자: "2층 3층 4층 기능은 뭐로 할 거야? 이런 것도 있어야 하는 거 아니야?" → "그냥 해 줘 · 애들이 켜면 무엇을 따라가서 집이 생기고 침대·책상이 생기는 거야? · 마트나 이런 시설 — 옷이랑 그런 걸 사는 거지"
   📚 2층 공부방 = Daily 30 에서 익힌 단어(srs) 10개 = 책 1권 · 책 펴서 단어·소리 · 📝 오늘의 복습 5문제 (맞힌 만큼 💎, 하루 한 번)
   🏆 3층 자랑방 = 도감·가장 큰 물고기·타워 완주·연속 공부·공부한 날·책·왕관 이 저절로 · 친구가 놀러 오면 그 아이 기록
   🌿 4층 옥상 = 🔭 망원경(마을 친구 집 목록 → 바로 놀러 가기) · 🪴 화분(공부한 날마다 꽃 한 송이)
   🛏 침실 = 침대에서 자면 💤 꿈 카드 3문제 (하루 한 번) · 🛁 욕실 = 씻으면 ✨ 낚시 행운 10분 (1시간에 한 번) · 🍳 부엌 = 요리할 때 "Put in the tomato!" 듣고 재료 고르기 */
const HLIFE=(()=>{
  const day=()=>{ try{ return dayKey(); }catch(e){ return new Date().toISOString().slice(0,10); } };
  const W_=()=>typeof ISLE_WORDS!=="undefined" ? ISLE_WORDS : [["cat","고양이","🐱",1],["dog","개","🐶",1],["fish","물고기","🐟",1],["apple","사과","🍎",1]];
  const study=()=>{ try{ return JSON.parse(localStorage.getItem("hyeng_study_v1")||"{}"); }catch(e){ return {}; } };
  function myWords(){ const S=study().srs||{}, M={}; W_().forEach(w=>{ M[w[0]]=w; }); const L=[]; Object.keys(S).forEach(en=>{ const w=M[en]||M[en.toLowerCase()]; if(w) L.push({w, box:(S[en]||[0])[0]|0}); }); return L; }
  /* ── 창 (공통) ── */
  const st=document.createElement("style"); st.textContent=`
.hlP{position:fixed;inset:0;z-index:21;display:none;background:rgba(30,18,40,.45);align-items:flex-end;justify-content:center} .hlP.on{display:flex}
.hlP .lb{width:min(560px,100%);max-height:90vh;overflow:auto;background:#fff8ea;border:3px solid #3b2433;border-bottom:0;border-radius:26px 26px 0 0;padding:12px 14px calc(16px + env(safe-area-inset-bottom));font-family:var(--kr);color:#3b2433}
.hlP h3{margin:2px 4px 8px;font-weight:400;font-size:21px;display:flex;align-items:center;gap:8px}.hlP h3 small{font-size:12px;color:#9a7e63;flex:1}
.hlP .x{width:38px;height:38px;border-radius:50%;border:3px solid #3b2433;background:#fffdf7;box-shadow:0 3px 0 #3b2433;font-size:16px;color:#3b2433}
.hlBooks{display:grid;grid-template-columns:repeat(auto-fill,minmax(64px,1fr));gap:8px;margin:6px 0}
.hlBooks button{height:86px;border-radius:10px 14px 14px 10px;border:3px solid #3b2433;box-shadow:inset 6px 0 0 rgba(0,0,0,.15),0 3px 0 #3b2433;color:#fff;font:15px var(--kr);text-shadow:0 1px 1px rgba(0,0,0,.4);display:flex;flex-direction:column;align-items:center;justify-content:center}
.hlW{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:6px}
.hlW button{display:flex;align-items:center;gap:8px;padding:6px 8px;border-radius:14px;border:2.5px solid #3b2433;background:#fffdf7;text-align:left;font:13px var(--kr);color:#3b2433}
.hlW i{font-style:normal;font-size:24px}.hlW b{font:800 16px var(--en);display:block}
.hlBig{display:flex;align-items:center;justify-content:center;gap:8px;width:100%;height:54px;margin:8px 0 4px;border-radius:16px;border:3px solid #3b2433;box-shadow:0 3px 0 #3b2433;font:18px var(--kr);color:#fff;background:linear-gradient(180deg,#86dc7c,#4caf50)}
.hlBig[disabled]{background:#e8dfd0;color:#8a7a6a}
.hlTiles{display:grid;grid-template-columns:repeat(2,1fr);gap:8px}
.hlTiles div{border:3px solid #3b2433;border-radius:18px;padding:8px 10px;background:#fffdf7;box-shadow:0 3px 0 #3b2433;display:flex;align-items:center;gap:8px}
.hlTiles i{font-style:normal;font-size:30px}.hlTiles b{display:block;font:800 18px var(--en)}.hlTiles small{font-size:12px;color:#8a6a4a}
.hlList button{display:flex;align-items:center;gap:10px;width:100%;margin-bottom:6px;padding:8px 10px;border-radius:16px;border:3px solid #3b2433;background:#fffdf7;box-shadow:0 3px 0 #3b2433;font:15px var(--kr);color:#3b2433;text-align:left}
.hlList em{margin-left:auto;font-style:normal;font-size:13px;color:#4caf50}
#hqP{position:fixed;inset:0;z-index:22;display:none;align-items:center;justify-content:center;background:rgba(30,18,40,.5)} #hqP.on{display:flex}
#hqP .b{width:min(340px,90vw);background:#fff8ea;border:3px solid #3b2433;border-radius:24px;box-shadow:0 6px 0 #3b2433;padding:14px;text-align:center;font-family:var(--kr);color:#3b2433}
#hqP .t{font-size:14px;color:#8a6a4a}#hqP .e{font-size:66px;line-height:1.1}#hqP .k{font-size:18px;margin:2px 0 10px}
#hqP .o{display:grid;grid-template-columns:1fr 1fr;gap:8px}#hqP .o button{height:52px;border-radius:16px;border:3px solid #3b2433;background:#fffdf7;box-shadow:0 3px 0 #3b2433;font:800 19px var(--en);color:#3b2433}
#hqP .o button.r{background:#bff0a8}#hqP .o button.w{background:#ffc4c4}
#hqP .o.em button{font-size:34px;height:64px}
#hqP .sb{margin-top:8px;height:40px;padding:0 16px;border-radius:14px;border:3px solid #3b2433;background:#fffdf7;font:15px var(--kr)}`; document.head.appendChild(st);
  function sheet(id){ let d=$(id); if(d) return d; d=document.createElement("div"); d.id=id; d.className="hlP"; d.innerHTML='<div class="lb"></div>'; document.body.appendChild(d);
    d.addEventListener("click", e=>{ if(e.target===d || e.target.closest(".x")) d.classList.remove("on"); }); ["pointerdown","pointerup"].forEach(ev=>d.addEventListener(ev, e=>e.stopPropagation())); try{ SHEETS.push(id); }catch(e){} return d; }
  function show(id, html){ const d=sheet(id); d.querySelector(".lb").innerHTML=html; d.classList.add("on"); return d; }
  /* ── 단어 문제 (그림+뜻 → 영어 4개) ── */
  function quiz(title, list, done){ let q=$("hqP"); if(!q){ q=document.createElement("div"); q.id="hqP"; q.innerHTML='<div class="b"></div>'; document.body.appendChild(q); ["pointerdown","pointerup","click"].forEach(ev=>q.addEventListener(ev, e=>e.stopPropagation())); }
    const box=q.querySelector(".b"); let i=0, ok=0; const all=W_();
    const next=()=>{ if(i>=list.length){ q.classList.remove("on"); done(ok); return; } const w=list[i]; const opts=[w]; let g=0; while(opts.length<4 && g++<60){ const x=all[Math.floor(Math.random()*all.length)]; if(!opts.some(o=>o[0]===x[0])) opts.push(x); } opts.sort(()=>Math.random()-.5);
      box.innerHTML='<div class="t">'+title+' · '+(i+1)+' / '+list.length+'</div><div class="e">'+w[2]+'</div><div class="k">'+esc(w[1])+' — 영어로?</div><div class="o">'+opts.map(o=>'<button data-w="'+o[0]+'">'+o[0]+'</button>').join("")+'</div>';
      box.onclick=e=>{ const b=e.target.closest("[data-w]"); if(!b || box.dataset.lock) return; box.dataset.lock=1; const r=b.dataset.w===w[0]; if(r) ok++; b.classList.add(r?"r":"w"); box.querySelectorAll("[data-w]").forEach(x=>{ if(x.dataset.w===w[0]) x.classList.add("r"); });
        try{ say(w[0]); (r?SND.win:SND.snap)(); }catch(_){} setTimeout(()=>{ delete box.dataset.lock; i++; next(); }, 1100); }; };
    q.classList.add("on"); next(); }
  function pickWords(n){ const L=myWords().sort((a,b)=>a.box-b.box), out=[]; L.slice(0,Math.max(n*3,n)).sort(()=>Math.random()-.5).forEach(x=>{ if(out.length<n) out.push(x.w); });
    if(out.length<n){ const B=W_().filter(w=>w[3]<=1); while(out.length<n && B.length){ const w=B.splice(Math.floor(Math.random()*B.length),1)[0]; if(!out.some(o=>o[0]===w[0])) out.push(w); } } return out; }
  /* ── 📚 2층 공부방 ── */
  function openBooks(){ if(visiting){ const b=((visiting.data||{}).brag||{}).books|0; toast("📚 "+esc(visiting.n||"친구")+" 의 단어 책 <b>"+b+"권</b>", 2000); return; }
    const L=myWords(), books=Math.floor(L.length/10), C=["#ff6b6b","#5aa7ff","#e0a41a","#4caf50","#9b72f0","#f07ab0"], done=store("hyeng_proto_rev")===day();
    let h='<h3>📚 내 단어 책장<small>Daily 30 에서 익힌 단어 10개 = 책 1권</small><button class="x" aria-label="닫기">✕</button></h3>';
    h+='<p style="margin:0 4px 6px;font-size:14px">단어 <b>'+L.length+'</b>개 · 책 <b>'+books+'</b>권'+(L.length%10?' · 다음 책까지 '+(10-L.length%10)+'개':'')+'</p>';
    h+='<button class="hlBig" data-rev'+(done?' disabled':'')+'>'+(done?'✅ 오늘 복습은 했어요 — 내일 또!':'📝 오늘의 복습 5문제 · 맞힌 만큼 💎')+'</button>';
    h+=books ? '<div class="hlBooks">'+Array.from({length:books},(_, i)=>'<button data-book="'+i+'" style="background:'+C[i%6]+'">📖<br>'+(i+1)+'권</button>').join("")+'</div>' : '<p style="text-align:center;color:#8a6a4a;margin:14px 0">아직 책이 없어요 — 🏫 학교(Daily 30)에서 단어를 익히면 책이 꽂혀요</p>';
    h+='<div id="hlBookW"></div>';
    const d=show("hlBk", h);
    d.querySelector(".lb").onclick=e=>{ const b=e.target.closest("[data-book]"); if(b){ const i=+b.dataset.book, W=L.slice(i*10,i*10+10).map(x=>x.w); $("hlBookW").innerHTML='<h4 style="margin:10px 4px 6px">📖 '+(i+1)+'권</h4><div class="hlW">'+W.map(w=>'<button data-say="'+w[0]+'"><i>'+w[2]+'</i><span><b>'+w[0]+'</b>'+esc(w[1])+'</span></button>').join("")+'</div>'; $("hlBookW").scrollIntoView({block:"nearest"}); return; }
      const s2=e.target.closest("[data-say]"); if(s2){ try{ say(s2.dataset.say); }catch(_){} return; }
      if(e.target.closest("[data-rev]") && !done){ d.classList.remove("on"); quiz("📝 오늘의 복습", pickWords(5), ok=>{ store("hyeng_proto_rev", day()); if(ok){ gems+=ok; saveBag(); } try{ tEv("review"); SND.big(); }catch(_){} emote(hero, ok>=4?"🌟":"👍"); toast("📝 복습 끝! "+ok+" / 5 · 💎 +"+ok, 2400); }); } }; }
  /* ── 🏆 3층 자랑방 ── */
  function brag(){ let fishN=0, big=null; try{ fishN=FISH.filter(f=>dex[f.en] && !f.noRot).length; Object.keys(FR).forEach(en=>{ const r=FR[en]; if(r && r.b && (!big || r.b>big[2])){ const f=FISH_BY[en]; if(f) big=[f.e, en, r.b]; } }); }catch(e){}
    let tw=0, twBest=0; try{ Object.values(TW.rec||{}).forEach(r=>{ if(r && r.sky && r.sky.best){ tw++; twBest=twBest? Math.min(twBest, r.sky.best) : r.sky.best; } }); }catch(e){}
    const d=study().days||{}; return {fish:fishN, fishT:(()=>{ try{ return FISH.filter(f=>!f.noRot).length; }catch(e){ return 0; } })(), big, tw, twBest:twBest?Math.round(twBest):0, hb:Math.max(d.hb||0,d.n||0), tot:d.tot||0, books:Math.floor(myWords().length/10), crown:(()=>{ try{ return !!crown; }catch(e){ return false; } })()}; }
  function openBrag(){ const B=visiting ? ((visiting.data||{}).brag||null) : brag(), who=visiting ? esc(visiting.n||"친구")+" 의" : "내";
    if(!B){ toast("🏆 아직 기록이 없어요", 1500); return; }
    const T=[["🐟", B.fish+(B.fishT?" / "+B.fishT:""), "물고기 도감"], ["🏆", B.big ? B.big[0]+" "+B.big[2]+"cm" : "—", B.big ? "가장 큰 "+B.big[1] : "가장 큰 물고기"], ["🗼", B.tw+"번", "하늘 타워 40층 완주"+(B.twBest?" · 최고 "+B.twBest+"초":"")], ["🔥", B.hb+"일", "가장 긴 연속 공부"], ["📅", B.tot+"일", "공부한 날"], ["📚", B.books+"권", "단어 책"]].concat(B.crown?[["👑","왕관","광산에서 만들었어요"]]:[]);
    show("hlBr", '<h3>🏆 '+who+' 자랑 진열장<small>'+(visiting?'친구 기록을 구경해요':'놀고 공부한 만큼 저절로 늘어나요 · 친구가 놀러 오면 보여요')+'</small><button class="x" aria-label="닫기">✕</button></h3><div class="hlTiles">'+T.map(t=>'<div><i>'+t[0]+'</i><span><b>'+t[1]+'</b><small>'+t[2]+'</small></span></div>').join("")+'</div>'); }
  /* ── 🔭 4층 옥상 망원경 ── */
  async function openScope(){ if(visiting){ toast("🔭 와! 마을이 한눈에 보여요", 1600); return; } const d=show("hlSc", '<h3>🔭 망원경<small>마을 친구 집 — 누르면 바로 놀러 가요</small><button class="x" aria-label="닫기">✕</button></h3><div class="hlList" id="hlScL"><p>찾는 중…</p></div>');
    let S={}; try{ await ISLE.loadLots(); S=ISLE.SRV()||{}; }catch(e){} const me=(()=>{ try{ return ISLE.myKey(); }catch(e){ return ""; } })();
    const L=Object.entries(S).filter(([id,v])=>v && v.c && v.k!==me).sort((a,b)=>a[0].localeCompare(b[0],undefined,{numeric:true}));
    const hn=id=>{ const h=(window.ISLE_MAP && ISLE_MAP.hoods[(+id.split("-")[0])-1]); return h ? h.ic+" "+h.nm : id; };
    $("hlScL").innerHTML=L.length ? L.slice(0,60).map(([id,v])=>'<button data-c="'+esc(v.c)+'"><span style="font-size:24px">🏠</span><span><b style="font-weight:400">'+esc(String(v.n||"친구"))+'</b><br><small style="color:#8a6a4a">'+hn(id)+' '+id.split("-")[1]+'번 땅'+((+v.f||1)>1?' · '+v.f+'층':'')+'</small></span><em>놀러 가기 →</em></button>').join("") : '<p style="text-align:center;color:#8a6a4a">아직 마을에 친구 집이 없어요</p>';
    $("hlScL").onclick=e=>{ const b=e.target.closest("[data-c]"); if(!b) return; d.classList.remove("on"); try{ visitCode(b.dataset.c); }catch(_){} }; }
  /* ── 🛁 · 🪴 · 💤 ── */
  function bath(){ const last=+(store("hyeng_proto_bath")||0); if(Date.now()-last<3600e3){ toast("🫧 방금 씻었어요 — "+Math.ceil((3600e3-(Date.now()-last))/60e3)+"분 뒤에 또", 1800); return; }
    store("hyeng_proto_bath", Date.now()); try{ buffUntil=Math.max(buffUntil, now())+10*60e3; saveFarm(); SND.sparkle(); }catch(e){} emote(hero,"✨"); try{ say("bath"); }catch(e){} toast("🛁 뽀득뽀득! <b>✨ 반짝 10분</b><br><small>드문 물고기가 더 잘 잡혀요 (🍀 lucky)</small>", 2600); }
  function planter(){ const n=Math.min(9,(study().days||{}).tot||0); toast("🪴 공부한 날마다 꽃이 한 송이씩 피어요 <b>"+n+" / 9</b>", 2200); }
  function slept(p){ if(visiting) return; if(store("hyeng_proto_dream")===day()) return;
    setTimeout(()=>{ if(!hero.seat) return; quiz("💤 꿈속 단어 카드", pickWords(3), ok=>{ store("hyeng_proto_dream", day()); if(ok){ gems+=ok; saveBag(); } try{ tEv("dream"); }catch(_){} toast("💤 잘 잤어요! 꿈 카드 "+ok+" / 3 · 💎 +"+ok+"<br><small>내일 또 자면 새 꿈 카드</small>", 2600); }); }, 1500); }
  function use(u){ if(u==="books"){ openBooks(); return true; } if(u==="brag"){ openBrag(); return true; } if(u==="scope"){ openScope(); return true; } if(u==="planter"){ planter(); return true; } if(u==="bath"){ if(visiting) return true; bath(); return true; } return false; }
  /* ── 🛒 마트 — 씨앗 · 요리 재료 ── */
  const MART=["wheat","tomato","potato","corn","strawberry","apple","pumpkin","watermelon"];
  function openMart(){ const seeds=Object.keys(SEEDS||{}), rows=seeds.map(n=>[n+" seeds", MAT[n+" seeds"]?MAT[n+" seeds"].e:"🌰", SEEDS[n].p, "씨앗 — 내 마당 밭에 심어요"]).concat(MART.filter(n=>MAT[n]).map(n=>[n, MAT[n].e, Math.max(2, MAT[n].p*2), "요리 재료"]));
    const d=show("hlMt", '<h3>🛒 마트<small>씨앗 · 요리 재료 · 💎 <b id="hlMtG">'+gems+'</b></small><button class="x" aria-label="닫기">✕</button></h3><div class="hlList">'+rows.map(([n,e,p,t])=>'<button data-buy="'+esc(n)+'" data-p="'+p+'"><span style="font-size:26px">'+e+'</span><span><b style="font:800 16px var(--en)">'+esc(n)+'</b><br><small style="color:#8a6a4a">'+t+' · 가방에 '+(mats[n]|0)+'</small></span><em>💎 '+p+'</em></button>').join("")+'</div>');
    d.querySelector(".lb").onclick=e=>{ const b=e.target.closest("[data-buy]"); if(!b) return; const n=b.dataset.buy, p=+b.dataset.p; if(!spend(p)) return; addMat(n,1); saveBag(); try{ say(n.replace(" seeds","")); SND.pop(); tEv("mart"); }catch(_){} toast(MAT[n].e+" "+n+" 샀어요! → 🎒", 1300); openMart(); }; }
  /* ── 🍳 요리 듣기 놀이 — "Put in the tomato!" ── */
  let cookOK=false;
  function cookGame(r, then){ const ING=Object.keys(r.need).map(n=>n==="🐟"?"fish":n), pool=Object.keys(MAT).filter(n=>MAT[n].e && !/seeds|stone|branch|coal|iron|gold|diamond|wood/.test(n)); let i=0;
    let q=$("hqP"); if(!q){ quiz("", [], ()=>{}); q=$("hqP"); } const box=q.querySelector(".b");
    const ask=()=>{ if(i>=ING.length){ q.classList.remove("on"); then(); return; } const n=ING[i], e=n==="fish"?"🐟":MAT[n].e; const opts=[[n,e]]; let g=0; while(opts.length<4 && g++<50){ const x=pool[Math.floor(Math.random()*pool.length)]; if(x!==n && !opts.some(o=>o[0]===x)) opts.push([x, MAT[x].e]); } opts.sort(()=>Math.random()-.5);
      box.innerHTML='<div class="t">🍳 '+r.id+' 만들기 · 재료 '+(i+1)+' / '+ING.length+'</div><div class="e">🍲</div><div class="k"><b style="font:800 20px var(--en)">"Put in the '+n+'!"</b><br><small>잘 듣고 맞는 재료를 눌러요</small></div><div class="o em">'+opts.map(o=>'<button data-w="'+o[0]+'">'+o[1]+'</button>').join("")+'</div><button class="sb" data-again>🔊 다시 듣기</button>';
      try{ say("Put in the "+n); }catch(_){}
      box.onclick=e=>{ if(e.target.closest("[data-again]")){ try{ say("Put in the "+n); }catch(_){} return; } const b=e.target.closest("[data-w]"); if(!b || box.dataset.lock) return;
        if(b.dataset.w===n){ box.dataset.lock=1; b.classList.add("r"); try{ SND.pop(); }catch(_){} setTimeout(()=>{ delete box.dataset.lock; i++; ask(); }, 600); } else { b.classList.add("w"); try{ SND.snap(); say(n); }catch(_){} setTimeout(()=>b.classList.remove("w"), 600); } }; };
    q.classList.add("on"); ask(); }
  $("craftBody").addEventListener("click", e=>{ if(cookOK) return; try{ if(craftKind!=="cook") return; }catch(_){ return; } const b=e.target.closest("[data-make]"); if(!b || b.disabled) return; const r=COOK.find(x=>x.id===b.dataset.make); if(!r) return;
    e.stopImmediatePropagation(); e.preventDefault(); $("craftP").classList.remove("on");
    cookGame(r, ()=>{ cookOK=true; try{ make("cook", r.id); }finally{ cookOK=false; } try{ say(r.id); emote(hero,"😋"); }catch(_){} toast("🍳 <b>"+r.id+"</b> 완성! → 🎒", 1800); }); }, true);
  /* ── 새 시작 — 마을 광장에서 (섬 꺼짐·이름 없음 = 방 단계부터) · 방에 처음 오면 🎁 입주 선물 ── */
  function init(){ try{ if(tut.s<2){ const can=window.ISLE && ISLE.ON && ISLE.nameOk(); if(!can) tutAdv(2); else if(tut.s===0 && place===PL.room) setTimeout(()=>{ if(tut.s===0 && place===PL.room && !trip.busy) ISLE.enter(); }, 700); } }catch(e){ console.warn(e); }
    setInterval(()=>{ try{ if(tut.s>=2 && tut.s<=3 && place===PL.room && !visiting && store("hyeng_proto_gift")==="due" && !$("info").classList.contains("on") && !trip.busy){ store("hyeng_proto_gift", 1);
        info('<div class="iBig">🎁</div><b>Mia 의 입주 선물!</b><br>🛏 침대 · 📚 책상<br><small>🛋️ 가구 단추를 눌러 방에 놓아요</small>', "고마워요!", null); try{ SND.big(); }catch(_){} } }catch(e){} }, 600); }
  init();
  return {use, slept, openBooks, openBrag, openScope, openMart, brag, quiz, pickWords, myWords, bath, cookGame};
})();
window.HLIFE=HLIFE;
