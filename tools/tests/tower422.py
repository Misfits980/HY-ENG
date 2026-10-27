"""(v422) 🗼 하늘 타워 (로블록스 오비) · 😀 감정 표현 · 🏆 오늘 친구 기록 — 사용자: "마이타운에 로블록스 타워 같은 것도 · 마이타운을 더 다듬어 줘 · 애들이 재미없어지면 안 되니까"
  ① 마을 🗼 건물·이름표 → 쉬움/어려움 고르기 → 타워 안 (조이스틱·점프 단추·층·시간)
  ② 몸: 앞으로 걷기 · 점프 · 착지 · 용암/떨어지면 🚩 체크포인트 · 🔤 단어 다리(맞는 유리만) · 점프대 · 사라지는 발판
  ③ 날마다 같은 타워(모든 기기) · 다른 날은 다르게 · 🤖 자동 선수가 쉬움·어려움 모든 날 끝까지 (못 깨는 타워 없음)
  ④ 꼭대기: 오늘 처음 💎 (쉬움 5 · 어려움 12) · 기록 · 다시 하면 💎 없음 · 친구 기록 · 마을로
  ⑤ 😀 감정 표현 (👋 마을 사람이 대답 · 💃 춤)"""
import asyncio, sys, os, json
os.environ["HY_REAL3D"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright
BOT = r"""(opt)=>{ const H=HOUSE, T=H.TW, X=H.THX; T.bot=true; T.seed=opt.seed; H.twBuild(opt.mode); T.on=true; T.fin=false; T.cp=0; T.dead=0; T.t0=performance.now(); H.twRespawn(true); T.yaw=0;
  const walk=s=>s.on && ["solid","cp","top","bounce","conv","fade","glass"].includes(s.kind) && !(s.kind==="glass" && !s.ok);
  const wps=i=>T.S.slice(T.secR[i][0], T.secR[i][1]).filter(walk).concat([T.cps[i+1]]);
  const gap=(s,p)=>{ const dx=Math.max(s.min.x-(p.x+X), (p.x-X)-s.max.x, 0), dz=Math.max(s.min.z-(p.z+X), (p.z-X)-s.max.z, 0); return Math.hypot(dx,dz); };
  const inXZ=(s,x,z)=>x>s.min.x && x<s.max.x && z>s.min.z && z<s.max.z;
  let k=0, sec=-1, dead=T.dead, t=0, log=[], stuck=0, lastCp=0, secT=0; const dt=1/90;
  while(t<opt.max && !T.fin){ t+=dt; secT+=dt;
    if(T.cp!==sec || T.dead!==dead){ if(T.cp!==sec){ log.push([sec, +secT.toFixed(1), T.dead]); secT=0; } sec=T.cp; dead=T.dead; k=0; }
    if(sec>=T.cps.length-1) break;
    const W=wps(sec), p=T.p; for(let j=W.length-1;j>=0;j--){ if(T.onG && T.gnd===W[j]){ k=Math.max(k,j+1); break; } }
    if(W[k] && W[k].kind==="bounce" && T.v.y>8 && inXZ(W[k],p.x,p.z)) k++;
    if(k>=W.length) k=W.length-1; let tg=W[k]; while(!tg.on && k<W.length-1){ k++; tg=W[k]; }
    const m=Math.min(0.45,(tg.max.x-tg.min.x)/2-0.02), n=Math.min(0.45,(tg.max.z-tg.min.z)/2-0.02);
    const cx=Math.max(tg.min.x+m,Math.min(tg.max.x-m,p.x)), cz=Math.max(tg.min.z+n,Math.min(tg.max.z-n,p.z));
    let dx=cx-p.x, dz=cz-p.z; const L=Math.hypot(dx,dz); if(L>0.05){ dx/=L; dz/=L; } else { dx=dz=0; }
    if(T.onG && T.gnd && T.gnd.push && (dx||dz)){ dx=dx*4.4-T.gnd.push[0]; dz=dz*4.4-T.gnd.push[1]; const q=Math.hypot(dx,dz); dx/=q; dz/=q; }
    const g=T.gnd, gp=gap(tg,p), rise=tg.max.y-(g?g.max.y:p.y);
    if(T.onG && g && g!==tg){
      const nx=p.x+dx*0.35, nz=p.z+dz*0.35, leaving=!inXZ(g,nx,nz);
      const R=tg.move?1.1:2.0; if(leaving && (gp>R || rise>1.45)){ dx=dz=0; }   // 기다림 (움직이는 발판)
      else if((leaving || rise>0.06) && gp<R && rise<1.5 && (leaving || gp<1.1)) T.buf=0.16;
    }
    for(const s of T.S){ if(s.kind==="spin" && T.onG){ const a=-s.mesh.rotation.y, ex=Math.cos(a), ez=Math.sin(a), qx=p.x-s.c[0], qz=p.z-s.c[1], u=Math.max(-s.len,Math.min(s.len,qx*ex+qz*ez)), d=Math.hypot(qx-ex*u, qz-ez*u); if(d<0.75) T.buf=0.16; } }
    T.inp.x=dx; T.inp.y=-dz; H.twStep(dt);
  }
  log.push([sec, +secT.toFixed(1), T.dead]);
  const r={fin:T.fin, t:+t.toFixed(1), dead:T.dead, cp:T.cp, n:T.cps.length-1, secs:T.secs, log}; T.bot=false; T.inp.x=T.inp.y=0; return r; }
"""

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "FAIL ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        ctx = await br.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*", route); await pg.goto(ORIGIN + "proto/house.html"); await pg.wait_for_timeout(800)
        await pg.evaluate("()=>{ Object.keys(localStorage).filter(k=>k.startsWith('hyeng_proto_')).forEach(k=>localStorage.removeItem(k)); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); localStorage.setItem('hyeng_proto_baitok','1'); }")
        await pg.reload(); await pg.wait_for_timeout(2500)
        E = pg.evaluate
        async def until(js, n=60):
            for _ in range(n):
                try:
                    if await E(js): return True
                except Exception: pass
                await pg.wait_for_timeout(200)
            return False
        await E("()=>{ HOUSE.setWx(false); HOUSE.go('village'); }"); await until("()=>HOUSE.place()==='village'")
        # ① 마을
        r = await E("()=>[HOUSE.LBL().some(L=>L.d.k==='tower'), !!HOUSE.towerObj(), HOUSE.TW_AT]")
        ok(r[0] and r[1] and r[2] == [9, 3, 2, 2], f"마을에 🗼 타워 건물 · 이름표 {r}")
        r = await E("()=>{ const L=HOUSE.LBL().find(L=>L.d.k==='tower'); L.d.act(); return 1; }")
        ok(await until("()=>document.getElementById('info').classList.contains('on') && !!document.getElementById('twE')", 80), "이름표 → 걸어가서 「오늘의 하늘 타워」 쉬움/어려움")
        r = await E("()=>document.getElementById('infoT').innerText")
        ok("쉬움" in r and "어려움" in r and "친구 기록" in r or "첫 번째" in r, f"고르기 창 + 🏆 오늘 친구 기록 {r[:80]!r}")
        await pg.screenshot(path=OUT + "tower422_ask.png")
        await E("()=>{ HOUSE.TW.seed='2026-10-07'; document.getElementById('twE').click(); }")
        ok(await until("()=>HOUSE.place()==='tower' && HOUSE.TW.on"), "🟢 쉬움 → 타워 안")
        r = await E("()=>[HOUSE.TW.cps.length-1, HOUSE.TW.secs.includes('word'), document.getElementById('twUI').classList.contains('on'), getComputedStyle(document.querySelector('.bar.bot')).display, document.getElementById('twFloor').textContent, HOUSE.TW.cp]")
        ok(r[0] == 6 and r[1] and r[2] and r[3] == "none" and r[4].startswith("0 /") and r[5] == 0, f"6층 · 🔤 단어 다리 꼭 · 조이스틱·점프 화면 (아래 독 숨김) {r}")
        await pg.wait_for_timeout(800); await pg.screenshot(path=OUT + "tower422_in.png")
        # ② 몸 — 시간이 멈춘 채로 직접 계산 (TW.bot)
        r = await E("""()=>{ const T=HOUSE.TW; T.bot=true; HOUSE.twRespawn(true); const y0=T.p.y, a=[T.onG, T.p.x, T.p.z]; T.yaw=0; T.inp.x=0; T.inp.y=0;
            for(let i=0;i<30;i++) HOUSE.twStep(1/90); const still=[T.p.x, T.p.y];
            T.buf=0.16; let top=0; for(let i=0;i<120;i++){ HOUSE.twStep(1/90); top=Math.max(top, T.p.y-y0); }
            return [a[0], Math.abs(still[1]-y0)<0.01, +top.toFixed(2), T.onG, Math.abs(T.p.y-y0)<0.02]; }""")
        ok(r[0] and r[1] and 1.3 < r[2] < 2.0 and r[3] and r[4], f"서 있기 · 점프 높이 ≈1.6 · 다시 착지 {r}")
        r = await E("""()=>{ const T=HOUSE.TW, x0=T.p.x; T.key.r=1; for(let i=0;i<20;i++) HOUSE.twStep(1/90); T.key.r=0; const dx=T.p.x-x0; for(let i=0;i<30;i++) HOUSE.twStep(1/90); return [+dx.toFixed(2), Math.round(HOUSE.TW.p.y*100)/100]; }""")
        ok(r[0] > 0.3, f"⌨️ 오른쪽 화살표 → 움직임 {r}")
        r = await E("""()=>{ const T=HOUSE.TW; for(let d=1; d<60; d++){ T.seed='2026-12-'+d; HOUSE.twBuild('easy'); if(T.secs.includes('lava')) break; } T.cp=0; HOUSE.twRespawn(true); const d0=T.dead; const lava=T.S.find(s=>s.kind==='kill'); if(!lava) return 'nolava';
            T.cp=1; HOUSE.twRespawn(true); const c=T.p.clone(); T.p.set((lava.min.x+lava.max.x)/2, lava.max.y+0.05, (lava.min.z+lava.max.z)/2); T.v.set(0,-1,0); for(let i=0;i<10;i++) HOUSE.twStep(1/90);
            const back=T.p.distanceTo(c)<0.05; const d1=T.dead; T.p.y-=20; HOUSE.twStep(1/90); return [T.dead-d0, back, T.dead-d1, T.p.distanceTo(c)<0.05]; }""")
        ok(r != "nolava" and r[0] >= 1 and r[1] and r[2] == 1 and r[3], f"🔥 용암 → 🚩 체크포인트로 · 떨어져도 체크포인트로 {r}")
        r = await E("""()=>{ const T=HOUSE.TW, G=T.S.filter(s=>s.kind==='glass'), good=G.find(s=>s.ok), bad=G.find(s=>!s.ok);
            const put=s=>{ T.p.set((s.min.x+s.max.x)/2, s.max.y+0.02, (s.min.z+s.max.z)/2); T.v.set(0,0,0); for(let i=0;i<4;i++) HOUSE.twStep(1/90); };
            put(good); const a=[good.on, T.onG, good.said]; put(bad); return a.concat([bad.on, bad.mesh.visible, G.filter(s=>s.ok).length, T.words.length]); }""")
        ok(r[0] and r[1] and r[2] == 1 and r[3] is False and r[4] is False and r[5] == 2 and r[6] == 2, f"🔤 맞는 단어 유리 = 튼튼 · 틀린 유리 = 깨짐 (2줄) {r}")
        # ③ 날마다
        r = await E("""()=>{ const T=HOUSE.TW, sig=()=>T.secs.join()+'|'+T.S.length+'|'+T.hy.toFixed(2); T.seed='2026-10-07'; HOUSE.twBuild('hard'); const a=sig(); HOUSE.twBuild('hard'); const b=sig(); T.seed='2026-10-08'; HOUSE.twBuild('hard'); const c=sig(); return [a===b, a!==c, T.cps.length-1]; }""")
        ok(r[0] and r[1] and r[2] == 10, f"같은 날 = 같은 타워 · 다른 날 = 다른 타워 · 🔴 10층 {r}")
        r = await E("""()=>{ const T=HOUSE.TW, bad=[]; const solid=s=>s.min && s.kind!=='spin' && s.kind!=='floor';
            for(const mode of ['easy','hard']) for(let d=1; d<=12; d++){ T.seed='2026-09-'+d; HOUSE.twBuild(mode); const own=new Map(); T.secR.forEach(([a,b],i)=>{ for(let j=a;j<b;j++) own.set(T.S[j], i); });
              const L=T.S.filter(solid).filter(s=>own.has(s)); for(let i=0;i<L.length;i++) for(let j=i+1;j<L.length;j++){ const A=L[i], B=L[j]; if(own.get(A)===own.get(B)) continue;
                const o=k=>Math.min(A.max[k],B.max[k])-Math.max(A.min[k],B.min[k]); if(o('x')>0.02 && o('y')>0.02 && o('z')>0.02) bad.push([mode,d,own.get(A),own.get(B),A.kind,B.kind]); } }
            return bad; }""")
        ok(not r, f"층과 층의 발판이 겹치지 않음 (24개 타워) {r[:3]}")
        res = []
        for mode in ["easy", "hard"]:
            for seed in ["2026-11-%02d" % d for d in range(1, 9)]:
                r = await E(BOT, {"mode": mode, "seed": seed, "max": 300})
                res.append((mode, seed, r["fin"], r["t"], r["dead"]))
        fails = [x for x in res if not x[2]]
        ok(not fails, f"🤖 자동 선수가 쉬움 8일·어려움 8일 모두 꼭대기 (못 깨는 타워 없음) {fails[:3]} 평균 {sum(x[3] for x in res)/len(res):.0f}초")
        # ④ 꼭대기 (🤖 가 남긴 기록은 지움)
        await E("()=>{ HOUSE.TW.rec={}; Object.keys(localStorage).filter(k=>k.indexOf('hyeng_proto_tower')>=0).forEach(k=>localStorage.removeItem(k)); }")
        await E("()=>{ const T=HOUSE.TW; T.bot=false; T.seed=null; HOUSE.twBuild('easy'); T.on=true; T.fin=false; T.mode='easy'; T.t0=performance.now()-65000; T.cp=0; HOUSE.twRespawn(true); HOUSE.setGems(10); }")
        r = await E("""()=>{ const T=HOUSE.TW, top=T.top; T.bot=true; T.p.set((top.min.x+top.max.x)/2, top.max.y+0.3, (top.min.z+top.max.z)/2); T.v.set(0,0,0); for(let i=0;i<40;i++) HOUSE.twStep(1/90); T.bot=false; return [T.fin, HOUSE.gems()]; }""")
        await pg.wait_for_timeout(1200)
        t = await E("()=>document.getElementById('infoT').innerText")
        ok(r[0] and r[1] == 15 and "꼭대기" in t and "💎 +5" in t and "1:0" in t, f"🏆 꼭대기 → 💎 +5 (오늘 처음) · 시간 {r} {t[:60]!r}")
        await pg.screenshot(path=OUT + "tower422_win.png")
        r = await E("""()=>{ const rec=JSON.parse(localStorage.getItem(Object.keys(localStorage).find(k=>k.indexOf('hyeng_proto_tower')>=0))); const d=Object.keys(rec)[0]; return [rec[d].easy.best>60, rec[d].easy.n]; }""")
        ok(r[0] and r[1] == 1, f"기록 저장 {r}")
        await E("()=>{ document.getElementById('info').classList.remove('on'); const T=HOUSE.TW; T.on=true; T.fin=false; T.t0=performance.now()-40000; T.cp=0; HOUSE.twRespawn(true); }")
        r = await E("""()=>{ const T=HOUSE.TW, top=T.top; T.bot=true; T.p.set((top.min.x+top.max.x)/2, top.max.y+0.3, (top.min.z+top.max.z)/2); T.v.set(0,0,0); for(let i=0;i<40;i++) HOUSE.twStep(1/90); T.bot=false; return [T.fin, HOUSE.gems()]; }""")
        await pg.wait_for_timeout(1200)
        t = await E("()=>document.getElementById('infoT').innerText")
        ok(r[1] == 15 and "새 기록" in t, f"두 번째 = 💎 없음 · 🎉 새 기록 {r} {t[:50]!r}")
        r = await E("()=>{ HOUSE.TW.rec; return document.querySelector('#infoT') && 1; }")
        await E("()=>document.getElementById('infoOk').click()")
        ok(await until("()=>HOUSE.place()==='village' && !HOUSE.TW.on"), "🏘 마을로 → 타워 끝")
        r = await E("()=>[document.getElementById('twUI').classList.contains('on'), document.body.classList.contains('twOn'), HOUSE.camera.fov, getComputedStyle(document.querySelector('.bar.bot')).display]")
        ok(r == [False, False, 30, "flex"], f"화면·카메라 원래대로 {r}")
        # 친구 기록 (publish 에 tw)
        r = await E("""()=>{ const d=HOUSE.dayKey(); const s=HOUSE.SOC(); s.cls={AAAAA:{n:'루아', tw:{d, e:41.2}}, BBBBB:{n:'주호', tw:{d:'2000-01-01', e:10}}}; s.who={CCCCC:{n:'라언', tw:{d, e:80, h:120.5}}};
            HOUSE.towerAsk(); return document.getElementById('twBd').innerText; }""")
        ok("루아" in r and "라언" in r and "주호" not in r and "🥇" in r and "0:41.2" in r, f"🏆 오늘 친구 기록 (오늘 것만 · 빠른 순) {r!r}")
        await pg.screenshot(path=OUT + "tower422_board.png")
        await E("()=>document.getElementById('infoOk').click()")
        # ⑤ 감정 표현
        await pg.wait_for_timeout(600)
        ok(await E("()=>document.getElementById('bEmo').classList.contains('on')"), "😀 감정 표현 단추 (마을)")
        await E("()=>{ const h=HOUSE.hero(), n=HOUSE.npcs[0]; n.path=[]; n.moving=false; n.talking=false; n.cx=h.cx+1; n.cz=h.cz; n.g.position.set(n.cx+0.5,0,n.cz+0.5); document.getElementById('bEmo').click(); }")
        ok(await E("()=>document.getElementById('emoBar').classList.contains('on') && document.querySelectorAll('#emoBar button').length===4"), "👋 💃 🎉 ❤️")
        await pg.screenshot(path=OUT + "tower422_emo.png")
        await E("()=>document.querySelector('#emoBar [data-emo=\"1\"]').click()"); await pg.wait_for_timeout(900)
        r = await E("()=>[HOUSE.hero().act, HOUSE.npcs[0].act, document.getElementById('toast').innerText]")
        ok(r[0] == "dance" and r[1] == "yay" and "dance" in r[2], f"💃 춤 → 옆 마을 사람도 같이 {r}")
        await pg.screenshot(path=OUT + "tower422_dance.png")
        ok(not real_errs(errs), "오류 없음 " + str(real_errs(errs)[:3]))
        await br.close()
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)

asyncio.run(main())
