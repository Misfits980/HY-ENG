"""(v472) 🗼 도전 — 사용자: "층마다 길이 늘어났나? 진짜 발판 찾기는 점프만 하면 끝나 · 발판 간격이 점프 한 번이면 넘어가 ·
          층마다 함정 2개 + 길도 늘어나야 · 얼음은 그냥 멈춰지니까 더 미끄럽게 · 1인칭/3인칭 전환 · 떨어지면 화면이 안 돌아가는 프리징"
  ① 11층부터 한 층 = 한 바퀴(네 면): 함정 A 두 면 → 함정 B 두 면 · 모서리 흰 발판(체크포인트 아님)
  ② 다음 층 사다리 기둥 밑 = 이 층 시작 발판 머리 위 2.95 이상 · 기둥 오르는 길에 걸리는 것 없음
  ③ 🦶 진짜 발판(도전) = 줄 2개 · 줄마다 3칸 중 1칸 · 한 줄 건너뛰기 불가 (점프 시험)
  ④ 🟥 킬브릭(도전) = 머리 위 빨간 막대 4개 · 점프하면 닿아서 죽음 · 걸으면 괜찮음
  ⑤ 🧊 얼음 = 손 떼도 더 멀리 미끄러짐 (도전 > 쉬움)
  ⑥ 👁 1인칭/3인칭 단추 · 1인칭이면 내 캐릭터 숨김 · 기억
  ⑦ 다시 시작(카메라 저절로 도는 중)에 화면 끌면 바로 내 손대로 · 손 뗀 게 안 잡혀도 1.5초 뒤 새로 끌기"""
import asyncio, sys, os
os.environ["HY_REAL3D"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

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
        # ① ②
        r = await E("""()=>{ const H=HOUSE, T=H.TW, laps=[], gap=[], hit=[]; for(let d=1; d<=8; d++){ T.seed='2026-12-'+d; H.twBuild('sky');
            for(let i=10;i<40;i++){ if(!T.secsB[i]) continue; laps.push(T.frEnd[i]-T.fr[i]+1); gap.push(+(T.cps[i+1].min.y-T.cps[i].max.y).toFixed(2)); }
            const B=T.S.filter(s=>s.min && s.max && s.kind!=='floor');
            for(let i=0;i<T.cps.length-1;i++){ const P=T.cps[i+1]; if(!P.climb) continue; const Fp=H.twFrame(T.frEnd[i]), a=Fp.P(7.45,-1.0), b=Fp.P(8.0,1.0), x0=Math.min(a[0],b[0]), x1=Math.max(a[0],b[0]), z0=Math.min(a[1],b[1]), z1=Math.max(a[1],b[1]);
              for(const s of B){ if(s===P || (s.noWalk && s.net==null)) continue; if(s.max.x<=x0+0.01||s.min.x>=x1-0.01||s.max.z<=z0+0.01||s.min.z>=z1-0.01) continue; if(s.max.y<=P.min.y+0.75 || s.min.y>=P.max.y+1.15 || Math.abs(s.max.y-P.max.y)<0.06 && s.min.y>=P.max.y-0.5) continue; hit.push([d,i,s.kind]); } } }
          const conn=T.S.filter(s=>s.conn), cp=T.cps.filter(c=>c.conn); return [new Set(laps).size, laps[0], Math.min(...gap), hit.length, hit.slice(0,3), conn.length, cp.length]; }""")
        ok(r[0] == 1 and r[1] == 4 and r[5] == 84 and r[6] == 0, f"① 11~40층(땅·벽 빼고) 한 층 = 4면 · 모서리 흰 발판 84개(체크포인트 아님) {r}")
        ok(r[2] >= 2.94 and r[3] == 0, f"② 사다리 기둥 밑 ≥ 시작 발판 +2.95 ({r[2]}) · 오르는 길에 걸리는 것 {r[3]} {r[4]}")
        # ③ 진짜 발판 — 점프 시험 (공중에서 목표로 조종 · 코요테 점프 포함)
        r = await E("""()=>{ const H=HOUSE, T=H.TW; T.bot=true; for(let d=1; d<300; d++){ T.seed='2027-12-'+d; H.twBuild('sky'); if(T.S.some(s=>s.seg && s.seg.kind==='tiptoe' && s.seg.i>=10 && s.seg.part==null)) break; }
            T.on=true; const F=T.S.find(s=>s.seg && s.seg.kind==='tiptoe' && s.seg.i>=10 && s.seg.part==null).seg, S=T.S.filter(s=>s.seg===F), real=S.filter(s=>s.kind==='solid' && !s.noWalk && !s.fake && s.net==null), rows=S.filter(s=>s.kind==='solid' && s.min.y>real[0].max.y-0.1 && (s.fake||!s.noWalk) && s!==real[0] && s!==real[real.length-1]);
            const ctr=s=>[(s.min.x+s.max.x)/2,(s.min.z+s.max.z)/2];
            const tryJ=(from,to,dl)=>{ const c=ctr(from), d=F.d, tc=ctr(to), lat=(tc[0]-c[0])*F.n[0]+(tc[1]-c[1])*F.n[1]; T.p.set(c[0]+d[0]*0.1+F.n[0]*lat, from.max.y+0.001, c[1]+d[1]*0.1+F.n[1]*lat); T.v.set(0,0,0); T.onG=true; T.gnd=from; T.coy=0; T.buf=0; T.yaw=Math.atan2(-d[0],-d[1]);
                let t=0, left=null, j=false, air=false; while(t<3){ t+=1/90; T.inp.x=0; const al=(tc[0]-T.p.x)*d[0]+(tc[1]-T.p.z)*d[1]; T.inp.y=!j?1:Math.max(-1,Math.min(1,al*3)); if(!j){ if(T.onG) left=null; else if(left==null) left=t; if(left!=null && t-left>=dl){ T.buf=0.16; j=true; } }
                  H.twStep(1/90); if(!T.onG) air=true; if(j && T.onG && T.gnd===to) return 1; if(j && air && T.onG && T.gnd!==from) return 0; if(T.p.y<from.max.y-3) return 0; } return 0; };
            const can=(a,b)=>[0,0.04,0.08,0.12].some(dl=>tryJ(a,b,dl));
            const res=[can(real[0],real[1]), can(real[1],real[2]), can(real[0],real[2]), can(real[1],real[3])]; T.bot=false; T.on=false; return [real.length, rows.length, res]; }""")
        ok(r[0] == 4 and r[1] == 6 and r[2] == [True, True, False, False], f"③ 🦶 줄 2개 × 3칸(진짜 1) · 한 줄씩은 건넘 · 한 줄 건너뛰기 불가 {r}")
        # ④ 킬브릭 막대
        r = await E("""()=>{ const H=HOUSE, T=H.TW; T.bot=true; for(let d=1; d<300; d++){ T.seed='2027-12-'+d; H.twBuild('sky'); if(T.S.some(s=>s.noJump && s.seg.kind==='brick')) break; }
            T.on=true; const bars=T.S.filter(s=>s.noJump && s.seg.kind==='brick'), F=bars[0].seg, S0=T.S.filter(s=>s.seg===F && s.kind==='solid' && !s.conn && !s.noWalk), st=S0[1], c=[(st.min.x+st.max.x)/2,(st.min.z+st.max.z)/2], under=bars.filter(b=>b.seg===F).some(b=>b.max.x>c[0]-0.24 && b.min.x<c[0]+0.24 && b.max.z>c[1]-0.24 && b.min.z<c[1]+0.24);
            const run=(jump)=>{ T.p.set(c[0], st.max.y+0.001, c[1]); T.v.set(0,0,0); T.onG=true; T.gnd=st; T.dead=0; T.cp=F.i; T.inp.x=T.inp.y=0; if(jump) T.buf=0.16; for(let q=0;q<60;q++) H.twStep(1/90); return T.dead; };
            const a=run(false), b=run(true); T.bot=false; T.on=false; return [bars.filter(s=>s.seg===F).length, +(bars[0].min.y-st.max.y).toFixed(2), a, b, under]; }""")
        ok(r[0] == 4 and 1.2 < r[1] < 1.35 and r[2] == 0 and r[3] == 1 and r[4], f"④ 🟥 머리 위 막대 4개(서 있으면 안 닿음 · 점프하면 죽음) {r}")
        # ⑤ 얼음
        r = await E("""()=>{ const H=HOUSE, T=H.TW, out={}; T.bot=true; for(const m of ['sky','kid']){ for(let d=1; d<300; d++){ T.seed='2027-12-'+d; H.twBuild(m); if(T.S.some(s=>s.kind==='ice' && s.seg.i>=10)) break; }
              T.on=true; const s=T.S.find(s=>s.kind==='ice' && s.seg.i>=10), F=s.seg; T.cp=F.i; T.lastGY=null; T.p.set((s.min.x+s.max.x)/2,s.max.y+0.001,(s.min.z+s.max.z)/2); T.onG=true; T.gnd=s; T.v.set(F.d[0]*2,0,F.d[1]*2); T.inp.x=T.inp.y=0; let t=0; while(t<0.3){ t+=1/90; H.twStep(1/90); }
              out[m]=[s.slip, +(Math.hypot(T.v.x,T.v.z)).toFixed(2)]; } T.bot=false; T.on=false; return out; }""")
        ok(r["sky"][0] <= 1.3 and r["kid"][0] < 2.2 and r["sky"][1] > 1.25 and r["sky"][1] > r["kid"][1] > 1.1, f"⑤ 🧊 손 떼고 0.3초 뒤에도 미끄러지는 중 (도전 > 쉬움 · 예전 2.2) {r}")
        # ⑥ ⑦
        await E("()=>{ HOUSE.setWx(false); HOUSE.go('village'); }"); await pg.wait_for_timeout(1500)
        await E("()=>{ HOUSE.TW.seed='2026-11-01'; HOUSE.twEnterGo('sky'); }")
        for _ in range(40):
            if await E("()=>HOUSE.place()==='tower' && HOUSE.TW.on"): break
            await pg.wait_for_timeout(200)
        await pg.wait_for_timeout(1500)
        r = await E("""async ()=>{ const b=document.getElementById('twView'), H=HOUSE, a0=[H.TW.fp, b.innerText.replace(/\\s+/g,'')]; b.click(); await new Promise(r=>setTimeout(r,300)); const a1=[H.TW.fp, b.innerText.replace(/\\s+/g,''), H.camera.fov, H.hero().g.visible, +(H.camera.position.y-H.TW.p.y).toFixed(2), JSON.parse(localStorage.getItem('hyeng_proto_twfp'))];
            b.click(); await new Promise(r=>setTimeout(r,300)); return [a0, a1, [H.TW.fp, H.hero().g.visible, H.camera.fov]]; }""")
        ok(r[0] == [False, "🎥3인칭"] and r[1][0] and r[1][1] == "🎥1인칭" and r[1][2] == 70 and r[1][3] is False and 0.8 < r[1][4] < 1.1 and r[1][5] == 1 and r[2] == [False, True, 50], f"⑥ 👁 1인칭(눈 높이 · 내 캐릭터 숨김 · 기억) ↔ 3인칭 {r}")
        r = await E("""async ()=>{ const T=HOUSE.TW, el=document.getElementById('twTouch'), ev=(t,id,x,y)=>el.dispatchEvent(new PointerEvent(t,{pointerId:id, clientX:x, clientY:y, bubbles:true})), w=ms=>new Promise(r=>setTimeout(r,ms));
            ev('pointerdown',7,300,300); ev('pointermove',7,310,300); const cam0=!!T.cam; T.yaw+=2.0; HOUSE.twDie(''); const s0=T.snap; await w(80); ev('pointermove',7,350,300); const y1=T.yaw; ev('pointermove',7,390,300); const y2=T.yaw; await w(250); const y3=T.yaw; ev('pointerup',7,390,300);
            ev('pointerdown',8,300,300); await w(1700); ev('pointerdown',9,300,320); const y4=T.yaw; ev('pointermove',9,350,320); const y5=T.yaw; ev('pointerup',9,350,320);
            return [s0, T.snap, +(y1-y2).toFixed(2), cam0, +(y2-y3).toFixed(3), +(y4-y5).toFixed(2)]; }""")
        ok(r[0] == 1 and r[1] == 0 and abs(r[2] - 0.36) < 0.05 and abs(r[4]) < 0.01 and abs(r[5] - 0.45) < 0.05, f"⑦ 다시 시작 중에 끌면 바로 내 손대로(저절로 안 돌아감) · 손 뗀 게 안 잡혀도 새로 끌기 {r}")
        ok(not real_errs(errs), "오류 없음 " + str(real_errs(errs)[:3]))
        await br.close()
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)
asyncio.run(main())
