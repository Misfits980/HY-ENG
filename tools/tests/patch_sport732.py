"""v732 — 볼링·다트·아레나 (#34 #54 #55 #49 #50)
   main 판(v729)과 다른 세션의 arena730 판 둘 다에 맞게 (같은 줄을 찾아 바꿈)
   python3 sport.py <mg-sport.js> <mg-arena.js>"""
import sys
def patch(p, fn):
    s=open(p,encoding='utf-8').read(); s2=fn(s); open(p,'w',encoding='utf-8').write(s2); print("ok", p)
def rep(s, a, b, c=1):
    assert s.count(a)==c, (s.count(a), a[:90]); return s.replace(a, b)

def sport(s):
    # #55 처음 누른 손가락만 (두 번째 손가락이 투구·다트를 덮어쓰던 것)
    s=rep(s, """pd={x:e.clientX, y:e.clientY, t:performance.now()}; trail=[pd]; if(mode==="dart") dartDown(e); });""",
          """if(pd && pd.id!==e.pointerId && performance.now()-pd.t<4000) return; pd={x:e.clientX, y:e.clientY, t:performance.now(), id:e.pointerId}; trail=[pd]; if(mode==="dart") dartDown(e); });   /* (v732 #55) 처음 누른 손가락만 */
  ["pointercancel","lostpointercapture"].forEach(t=>HIT.addEventListener(t, e=>{ if(pd && pd.id===e.pointerId){ pd=null; DT.hold=false; try{ guide.visible=false; }catch(_){} } }));""")
    s=rep(s, """HIT.addEventListener("pointermove", e=>{ if(!pd) return;""", """HIT.addEventListener("pointermove", e=>{ if(!pd || pd.id!==e.pointerId) return;""")
    s=rep(s, """HIT.addEventListener("pointerup", e=>{ if(!pd) return;""", """HIT.addEventListener("pointerup", e=>{ if(!pd || pd.id!==e.pointerId) return;""")
    # #54 셋째 다트 뒤 라운드 바꾸는 동안은 던지기를 쉬고, 그때 있던 다트만 치움 (예전: 빨리 던지면 새 화살도 지우고 「2.33라운드」)
    s=rep(s, """if(DT.n%3===0) later(fast?.05:1.4, ()=>{ DT.darts.forEach(d=>DART.remove(d.m)); DT.darts=[]; say((DT.n/3+1)+"라운드!"); }); }""",
          """if(DT.n%3===0){ const old=DT.darts.slice(), rn=DT.n/3+1; DT.clr=1; later(fast?.05:1.4, ()=>{ old.forEach(d=>DART.remove(d.m)); DT.darts=DT.darts.filter(d=>old.indexOf(d)<0); DT.clr=0; say(rn+"라운드!"); }); } }   /* (v732 #54) */""")
    s=rep(s, """function dartDown(e){ if(DT.fly || DT.n>=DN) return;""", """function dartDown(e){ if(DT.fly || DT.clr || DT.n>=DN) return;""")
    s=rep(s, """function dart(x, y){ if(mode!=="dart" || DT.fly || DT.n>=DN) return null;""", """function dart(x, y){ if(mode!=="dart" || DT.fly || DT.clr || DT.n>=DN) return null;""")
    if "DT.darts.forEach(d=>DART.remove(d.m)); Object.assign(DT,{n:0," in s:
        s=rep(s, "DT.darts.forEach(d=>DART.remove(d.m)); Object.assign(DT,{n:0,", "DT.darts.forEach(d=>DART.remove(d.m)); Object.assign(DT,{clr:0, n:0,")
    # #34 볼링 STRIKE = 새로 세운 핀(10개)을 한 번에 — 0개 뒤 10개는 스페어 (예전: STRIKE! 글자 · 스트라이크 기록 +1)
    if "const strike=got===10 && before===10," in s:   # arena730 판
        s=rep(s, "const before=L.pins.filter(p=>p.up).length;", "const fr0=rollsInFrame(L.rolls), before=L.pins.filter(p=>p.up).length;")
        s=rep(s, "const strike=got===10 && before===10,", "const strike=got===10 && before===10 && fr0.reset,   /* (v732 #34) */")
    else:   # main(v729) 판
        s=rep(s, """const r=REC(); if(got===10 && before===10){ big("STRIKE!",""", """const r=REC(); if(got===10 && before===10 && f.reset){ big("STRIKE!",""")   # f = rollsInFrame(굴리기 전)
    if "sk=BW.rolls.filter(x=>x===10).length" in s:
        s=rep(s, "sk=BW.rolls.filter(x=>x===10).length", "sk=bowlScore(BW.rolls).marks.reduce((n,m)=>n+m.filter(x=>x===\"X\").length,0)")
    return s

def arena(s):
    # #50 시간 끝 · 1등이 같은 단계·같은 수면 「공동 1등」 (예전: 참가자 줄 순서로 나 = 우승 · 🪙15)
    s=rep(s, """const L=ACT.slice().sort((x,y)=>(y===w)-(x===w) || y.wi-x.wi || y.kills-x.kills), rank=L.indexOf(me)+1, won=L[0]===me;""",
          """const L=ACT.slice().sort((x,y)=>(y===w)-(x===w) || y.wi-x.wi || y.kills-x.kills || (y===me)-(x===me)), tie=!w && L.length>1 && L[1].wi===L[0].wi && L[1].kills===L[0].kills, rank=L.indexOf(me)+1, won=L[0]===me && !tie;   /* (v732 #50) */""")
    s=rep(s, """api.msg(won?'🏆 우승!':w?'🏁 '+esc(w.nm)+' 우승!':'⏰ 시간 끝!', 1800);""",
          """api.msg(won?'🏆 우승!':w?'🏁 '+esc(w.nm)+' 우승!':tie && L.slice(0,2).includes(me)?'🤝 공동 1등! (시간 끝)':'⏰ 시간 끝!', 1800);""")
    # #49 가장 빠른 우승 = 이번 판 시간 (메뉴에서 기다린 시간 빼고) — arena730 판은 이미 beginSolo 에서 time.t=0
    if "time.t=0" not in s:
        s=rep(s, "  function beginSolo(){ CO=false;", "  function beginSolo(){ time.t=0;   /* (v732 #49) */ CO=false;")
    return s

if __name__=="__main__":
    patch(sys.argv[1], sport); patch(sys.argv[2], arena)
