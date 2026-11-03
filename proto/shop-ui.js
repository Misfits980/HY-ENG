/* ═════════ (v584) 🧺 가게 계산대 — 사용자: 「우리 파는 거 사는 게 약간 아쉬워 · 그 UI 가 진짜로」
   예전: 글자 줄 목록 · 한 줄마다 「sell」 하나씩 · 씨앗이 모두 🌰 같은 그림 · 창이 가게 안을 다 가림
   새것: 주인이 말하는 머리 + 큰 그림 칸(카드) + 아래 계산대(바구니 · 합계 · 사기/팔기 한 번)
   · 칸을 누르면 바구니에 +1 (− 로 빼기) · 같은 물고기는 한 칸에 ×개수 · 씨앗 = 작물 그림이 그려진 씨앗 봉투
   · 창은 화면 아래 2/3 만 (휴대폰) — 위로 가게 안·주인이 보임 · 패드는 가운데 카드
   쓰는 법: SHOPUI.open({kind, title, sub, keeper:{e, nm, en, ko}, tabs:[{k, t, mode:"buy"|"sell", items:()=>[{id, e, seed?, en, sub, price, have, max, tag, cls}], quote?(basket)=>🪙, act(basket)=>{n, c, msg}}], tools?:html, onTools?(e)})
   basket = [[id, qty], …] · act 가 실제로 사고팔고 결과를 돌려줌 (경제·저장은 원래 코드 그대로) */
const SHOPUI=(()=>{
  const $=id=>document.getElementById(id);
  const css=`
#suP{left:50%;right:auto;width:min(760px,100vw);transform:translate(-50%,105%);padding:0;display:flex;flex-direction:column;max-height:min(68vh,640px);overflow:hidden;background:#fffaf0}
#suP.on{transform:translate(-50%,0)}
#suP::before{display:none}
#suP .suAw{flex:none;height:14px;background:repeating-linear-gradient(90deg,var(--suA,#ff8a8a) 0 26px,#fffaf0 26px 52px);border-radius:24px 24px 0 0;border-bottom:2px solid rgba(90,60,30,.18)}
#suP .suHd{flex:none;display:flex;align-items:center;gap:10px;padding:10px 12px 8px}
#suP .suK{flex:none;width:52px;height:52px;border-radius:50%;background:#fff1d6;border:3px solid var(--line2);display:grid;place-items:center;font-size:30px;box-shadow:0 3px 0 rgba(90,60,30,.15)}
#suP .suSay{flex:1;min-width:0;position:relative;background:#fff;border:2.5px solid var(--line2);border-radius:16px;padding:6px 10px}
#suP .suSay::before{content:"";position:absolute;left:-9px;top:16px;border:7px solid transparent;border-right-color:var(--line2)}
#suP .suSay b{display:block;font:800 15px/1.25 var(--en);color:var(--ink)} #suP .suSay small{display:block;font-size:12px;color:var(--sub);margin-top:1px}
#suP .suSay.pop{animation:suPop .35s cubic-bezier(.2,.9,.3,1.4)}
#suP .suR{flex:none;display:flex;flex-direction:column;align-items:flex-end;gap:5px}
#suP .suCoin{display:inline-flex;align-items:center;gap:4px;height:32px;padding:0 12px;border-radius:999px;background:#fff1c9;color:#8a5a00;font:800 15px var(--en);box-shadow:inset 0 -2px 0 rgba(90,60,30,.12)}
#suP .suX{width:36px;height:36px;border-radius:50%;border:2.5px solid var(--line2);background:#fff;font-size:16px;color:var(--ink)}
#suP .suTabs{flex:none;display:flex;gap:6px;padding:0 12px 8px;overflow-x:auto;scrollbar-width:none}
#suP .suTabs button{flex:none;height:38px;padding:0 14px;border-radius:999px;border:2.5px solid var(--line2);background:#fff;font:800 14px var(--kr);color:var(--ink)}
#suP .suTabs button.on{background:var(--suA,#ff8a8a);border-color:var(--suA,#ff8a8a);color:#fff;box-shadow:0 3px 0 rgba(0,0,0,.12)}
#suP .suTools{flex:none;display:flex;flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none;gap:6px;align-items:center;padding:0 12px 6px;font-size:12px;color:var(--sub);white-space:nowrap} #suP .suTools>*{flex:none}
#suP .suTools .mk{display:inline-flex;gap:3px;align-items:center;padding:2px 8px;border-radius:999px;background:#f2ead8;font:700 12px var(--en);color:#6b5a4e} #suP .suTools .mk.up{background:#e2f6da;color:#2f8a3a} #suP .suTools .mk.dn{background:#ffe3df;color:#c0392b}
#suP .suTools .btn{height:30px;font-size:12px;padding:0 10px}
#suP .suBody{flex:1;min-height:0;overflow-y:auto;padding:4px 12px 12px;overscroll-behavior:contain}
#suP .suG{display:grid;grid-template-columns:repeat(auto-fill,minmax(104px,1fr));gap:9px}
#suP .suC{position:relative;display:flex;flex-direction:column;align-items:center;gap:2px;padding:10px 6px 8px;border-radius:18px;border:2.5px solid var(--line);background:#fff;box-shadow:0 3px 0 rgba(90,60,30,.12);font-family:inherit;color:var(--ink);min-width:0;transition:transform .12s}
#suP .suC:active{transform:translateY(2px) scale(.97)}
#suP .suC.in{border-color:var(--suA,#ff8a8a);background:#fff6f0;box-shadow:0 3px 0 var(--suA,#ff8a8a)}
#suP .suC.off{opacity:.45}
#suP .suC.rot{background:#f3efe6}
#suP .suC .ic{font-size:40px;line-height:48px;height:48px}
#suP .suC .pk{position:relative;width:44px;height:50px;border-radius:6px 6px 10px 10px;background:linear-gradient(#f7e2b5,#e9c88a);border:2px solid #b9884f;display:grid;place-items:center;font-size:26px;margin-bottom:-2px}
#suP .suC .pk::before{content:"";position:absolute;top:-2px;left:6px;right:6px;height:8px;background:repeating-linear-gradient(90deg,#b9884f 0 3px,transparent 3px 6px);border-radius:2px}
#suP .suC .pk::after{content:"🌱";position:absolute;right:-8px;bottom:-6px;font-size:16px}
#suP .suC .nm{font:800 14px/1.2 var(--en);max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
#suP .suC .sb{font-size:11px;color:var(--sub);max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
#suP .suC .pr{margin-top:3px;display:inline-flex;align-items:center;gap:3px;height:24px;padding:0 9px;border-radius:999px;background:#fff1c9;color:#8a5a00;font:800 13px var(--en)}
#suP .suC .hv{position:absolute;left:6px;top:6px;padding:0 6px;height:20px;border-radius:10px;background:#f2ead8;color:#6b5a4e;font:800 11px/20px var(--en)}
#suP .suC .tg{position:absolute;right:6px;top:6px;font:800 11px var(--en)} #suP .suC .tg.up{color:#2f8a3a} #suP .suC .tg.dn{color:#c0392b}
#suP .suC .q{position:absolute;right:-6px;top:-8px;min-width:28px;height:28px;padding:0 6px;border-radius:14px;background:var(--suA,#ff8a8a);color:#fff;border:2.5px solid #fff;font:900 15px/22px var(--en);box-shadow:0 2px 0 rgba(0,0,0,.15)}
#suP .suC .q small{font-size:11px;opacity:.9} #suP .suC .mn{position:absolute;left:-6px;top:-8px;width:30px;height:30px;border-radius:50%;background:#fff;border:2.5px solid var(--line2);font:900 18px/22px var(--en);color:var(--ink);padding:0}
#suP .suC .fb{width:70%;height:5px;border-radius:3px;background:#eadfca;overflow:hidden;margin-top:2px} #suP .suC .fb s{display:block;height:100%;background:linear-gradient(90deg,#ff8a65,#ffd23f,#7ed957)}
#suP .suC.bump{animation:suBump .3s}
#suP .suE{padding:26px 10px;text-align:center;color:var(--sub);font-size:14px}
#suP .suFt{flex:none;display:flex;align-items:center;gap:10px;padding:10px 12px calc(10px + max(0px,env(safe-area-inset-bottom)) + var(--gapB,0px));background:#f6ecd9;border-top:2.5px solid var(--line)}
#suP .suBk{flex:1;min-width:0;display:flex;flex-direction:column;gap:1px}
#suP .suBk .li{font-size:20px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
#suP .suBk small{font-size:12px;color:var(--sub)}
#suP .suAll{flex:none;height:44px;padding:0 12px;border-radius:14px;border:2.5px solid var(--line2);background:#fff;font:800 13px var(--kr);color:var(--ink)}
#suP .suGo{flex:none;min-width:132px;height:52px;padding:0 16px;border-radius:16px;border:0;background:var(--suA,#ff8a8a);color:#fff;font:900 17px var(--kr);box-shadow:0 4px 0 rgba(0,0,0,.18);display:flex;flex-direction:column;align-items:center;justify-content:center;line-height:1.15}
#suP .suGo small{font:800 12px var(--en);opacity:.92}
#suP .suGo:disabled{background:#cfc6b6;box-shadow:none}
#suP .suGo.poor{background:#e0796b}
#suP .suFly{position:fixed;z-index:40;font-size:26px;pointer-events:none;animation:suFly .7s ease-in forwards}
@keyframes suPop{0%{transform:scale(.9)}100%{transform:scale(1)}}
@keyframes suBump{0%{transform:scale(1)}40%{transform:scale(1.08)}100%{transform:scale(1)}}
@keyframes suFly{0%{transform:translate(0,0) scale(1);opacity:1}100%{transform:translate(var(--dx),var(--dy)) scale(.5);opacity:.2}}
@media (min-width:700px){ #suP{bottom:18px;border-radius:26px;border:3px solid var(--line2);max-height:min(72vh,720px)} #suP .suAw{border-radius:22px 22px 0 0} #suP .suG{grid-template-columns:repeat(auto-fill,minmax(122px,1fr))} #suP .suFt{border-radius:0 0 22px 22px;padding-bottom:12px} }
`;
  let el=null, cfg=null, tab=0, bk=new Map(), busy=false;
  function mk(){ if(el) return el; const st=document.createElement("style"); st.textContent=css; document.head.appendChild(st);
    el=document.createElement("div"); el.id="suP"; el.className="sheet"; el.setAttribute("role","dialog"); document.body.appendChild(el);
    try{ if(typeof SHEETS!=="undefined" && SHEETS.indexOf("suP")<0) SHEETS.push("suP"); }catch(e){}
    el.addEventListener("click", onClick);
    return el; }
  const T=()=>cfg.tabs[tab];
  const items=()=>{ try{ return T().items()||[]; }catch(e){ console.warn(e); return []; } };
  const coins=()=>{ try{ return TECO.coins(); }catch(e){ return 0; } };
  const esc=s=>String(s==null?"":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  function quote(){ const L=[...bk.entries()].filter(([,q])=>q>0); if(!L.length) return 0; const t=T(); if(t.quote) try{ return t.quote(L); }catch(e){}
    const I=items(); return L.reduce((s,[id,q])=>{ const it=I.find(x=>x.id===id); return s+(it?it.price*q:0); },0); }
  function draw(){ if(!el || !cfg) return; const t=T(), I=items(), c=coins();
    el.style.setProperty("--suA", cfg.color||"#ff8a8a");
    /* 바구니에 남은 것 중 없어진 것 정리 */
    for(const [id,q] of [...bk.entries()]){ const it=I.find(x=>x.id===id); if(!it) bk.delete(id); else if(it.max!=null && q>it.max) bk.set(id, it.max); }
    const K=cfg.keeper||{};
    let h='<div class="suAw"></div><div class="suHd"><div class="suK">'+(K.e||"🧑")+'</div><div class="suSay" id="suSay"><b>'+esc(K.en||"Hello!")+'</b><small>'+esc((K.nm?K.nm+" · ":"")+(K.ko||""))+'</small></div>'
      +'<div class="suR"><button class="suX" data-x aria-label="닫기">✕</button><span class="suCoin">🪙 <b id="suCoinN">'+c.toLocaleString("ko-KR")+'</b></span></div></div>';
    if(cfg.tabs.length>1) h+='<div class="suTabs">'+cfg.tabs.map((x,i)=>'<button class="'+(i===tab?'on':'')+'" data-tab="'+i+'">'+x.t+'</button>').join("")+'</div>';
    const tools=typeof cfg.tools==="function" ? cfg.tools(t) : cfg.tools; if(tools) h+='<div class="suTools">'+tools+'</div>';
    h+='<div class="suBody">'+(I.length ? '<div class="suG">'+I.map(it=>{ const q=bk.get(it.id)|0, off=(t.mode==="buy" && it.price>c && !q) || it.dis;
        return '<button class="suC'+(q?' in':'')+(off?' off':'')+(it.cls?' '+it.cls:'')+'" data-id="'+esc(it.id)+'">'
          +(it.seed ? '<span class="pk">'+it.e+'</span>' : '<span class="ic">'+it.e+'</span>')
          +'<span class="nm">'+esc(it.en)+'</span>'+(it.sub?'<span class="sb">'+it.sub+'</span>':'')+(it.fr!=null?'<span class="fb"><s style="width:'+Math.round(it.fr*100)+'%"></s></span>':'')
          +'<span class="pr">🪙 '+it.price+'</span>'+(it.have!=null && !(q && t.mode==="sell")?'<span class="hv">'+(t.mode==="sell"?'×':'🎒')+it.have+'</span>':'')+(it.tag?'<span class="tg '+(it.tagc||'')+'">'+it.tag+'</span>':'')
          +(q?'<span class="q">'+q+(t.mode==="sell" && it.have>1?'<small>/'+it.have+'</small>':'')+'</span><span class="mn" data-minus="'+esc(it.id)+'" role="button" aria-label="하나 빼기">−</span>':'')+'</button>'; }).join("")+'</div>'
        : '<p class="suE">'+(t.empty||"아직 없어요")+'</p>')+'</div>';
    const L=[...bk.entries()].filter(([,q])=>q>0), n=L.reduce((s,[,q])=>s+q,0), sum=quote(), poor=t.mode==="buy" && sum>c;
    const li=L.map(([id,q])=>{ const it=I.find(x=>x.id===id); return it ? it.e+(q>1?'<small>×'+q+'</small>':'') : ''; }).join(" ");
    h+='<div class="suFt"><div class="suBk">'+(n ? '<span class="li">'+li+'</span><small>🧺 '+n+'개 담았어요 · − 로 빼요</small>' : '<small>👆 '+(t.mode==="sell"?'팔 것을 누르면 바구니에 담겨요':'살 것을 누르면 바구니에 담겨요')+'</small>')+'</div>'
      +(t.mode==="sell" && I.length ? '<button class="suAll" data-all>'+(t.allT||"전부 담기")+'</button>' : '')
      +'<button class="suGo'+(poor?' poor':'')+'" data-go'+(n?'':' disabled')+'>'+(t.mode==="sell" ? '💰 팔기<small>+🪙 '+sum+'</small>' : poor ? '🪙 '+(sum-c)+' 모자라요<small>바구니 🪙 '+sum+'</small>' : '🛒 사기<small>🪙 '+sum+'</small>')+'</button></div>';
    const sc=el.querySelector(".suBody"), top=sc?sc.scrollTop:0; el.innerHTML=h; const sc2=el.querySelector(".suBody"); if(sc2) sc2.scrollTop=top; }
  function say(en, ko, speak){ const s=$("suSay"); if(!s) return; s.innerHTML='<b>'+esc(en)+'</b><small>'+esc(ko||"")+'</small>'; s.classList.remove("pop"); void s.offsetWidth; s.classList.add("pop"); if(speak) try{ window.say && window.say(en); }catch(e){} }
  function fly(fromEl, emo){ try{ const a=fromEl.getBoundingClientRect(), b=($("suCoinN")||fromEl).getBoundingClientRect(); const f=document.createElement("div"); f.className="suFly"; f.textContent=emo; f.style.left=(a.left+a.width/2-13)+"px"; f.style.top=(a.top+a.height/2-13)+"px"; f.style.setProperty("--dx",(b.left-a.left-a.width/2+20)+"px"); f.style.setProperty("--dy",(b.top-a.top-a.height/2)+"px"); el.appendChild(f); setTimeout(()=>f.remove(), 750); }catch(e){} }
  function onClick(e){ if(busy) return;
    if(e.target.closest("[data-x]")){ close(); return; }
    const tb=e.target.closest("[data-tab]"); if(tb){ tab=+tb.dataset.tab; bk.clear(); draw(); return; }
    const mn=e.target.closest("[data-minus]"); if(mn){ e.stopPropagation(); const id=mn.dataset.minus, q=(bk.get(id)|0)-1; if(q>0) bk.set(id,q); else bk.delete(id); try{ SND.click(); }catch(_){} draw(); return; }
    if(e.target.closest("[data-all]")){ items().forEach(it=>{ if(!it.dis) bk.set(it.id, it.max!=null?it.max:(it.have||1)); }); try{ SND.pop(); }catch(_){} draw(); return; }
    if(e.target.closest("[data-go]")){ go(e.target.closest("[data-go]")); return; }
    const c=e.target.closest(".suC"); if(c){ const id=c.dataset.id, it=items().find(x=>x.id===id); if(!it || it.dis) return; const q=bk.get(id)|0;
      if(it.max!=null && q>=it.max){ say(cfg.keeper && cfg.keeper.allEn || "That's all of them!", "그게 다예요", false); return; }
      bk.set(id, q+1); try{ SND.click(); }catch(_){} try{ if(T().mode==="buy" && !q) window.say && window.say(String(it.en).replace(/ seeds$/,"")); }catch(_){}
      draw(); const c2=el.querySelector('.suC[data-id="'+CSS.escape(id)+'"]'); if(c2) c2.classList.add("bump"); try{ if(cfg.onPick) cfg.onPick(it); }catch(_){} }
    else if(cfg.onTools) cfg.onTools(e); }
  function go(btn){ const L=[...bk.entries()].filter(([,q])=>q>0); if(!L.length) return; const t=T();
    if(t.mode==="buy" && quote()>coins()){ say("Oh no, not enough coins!", "🪙 가 모자라요 — 바구니에서 − 로 빼 봐요", false); try{ SND.snap && SND.snap(); }catch(_){} return; }
    busy=true; let r=null; try{ r=t.act(L); }catch(err){ console.warn(err); } busy=false;
    if(!r || !r.n){ if(r && r.msg) say(r.msg[0], r.msg[1], false); draw(); return; }
    bk.clear(); fly(btn, t.mode==="sell" ? "🪙" : "🛍"); try{ (t.mode==="sell"?SND.big:SND.pop)(); }catch(_){} try{ navigator.vibrate && navigator.vibrate(25); }catch(_){}
    draw(); const K=cfg.keeper||{}; say(K.thx||"Thank you!", t.mode==="sell" ? "🪙 +"+r.c+" 받았어요 · 고마워요!" : r.n+"개 샀어요 → 🎒 가방에 · 고마워요!", true);
    try{ if(cfg.after) cfg.after(t, r); }catch(_){} }
  function open(c){ mk(); cfg=c; tab=Math.max(0, Math.min((c.tab|0), c.tabs.length-1)); bk.clear(); draw(); el.classList.add("on"); const K=c.keeper||{}; try{ if(K.en && window.say) window.say(K.en); }catch(e){} return el; }
  function close(){ if(!el) return; el.classList.remove("on"); const c=cfg; cfg=null; bk.clear(); try{ if(c && c.onClose) c.onClose(); }catch(e){} }
  function isOn(){ return !!(el && el.classList.contains("on")); }
  function refresh(){ if(isOn()) draw(); }
  return {open, close, isOn, refresh, kind:()=>cfg && cfg.kind, tab:()=>tab, basket:()=>[...bk.entries()], pick:(id,q)=>{ if(!cfg) return; bk.set(id,(bk.get(id)|0)+(q||1)); draw(); }, go:()=>{ const b=el && el.querySelector("[data-go]"); if(b) go(b); }, el:()=>el, setTab:i=>{ tab=i; bk.clear(); draw(); }};
})();
window.SHOPUI=SHOPUI;
