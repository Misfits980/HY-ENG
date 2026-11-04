"""(v590) 사용자: 「놀이터가 너무 재미가 없다는 피드백」 → 「타워처럼 하나씩 게임 입장」 → 「1번 아스날(1인칭 · 아레나 무브) · 2번 발판 게임(초록 안전 · 파랑 밟아 지우기 · 빨강 점프/피하기)」
   ① 🎡 놀이 공원 입구 양옆 게임 타워 2채 · 이름표 · 부딪힘 · 누르면 안내 창(규칙 · 실력 고르기 · 오늘 🪙)
   ② 💦 물총 아레나: 들어가면 섬은 멈춤 · 3초 뒤 시작 · 3번 맞히면 흠뻑 → 다음 무기 · 슬라이드 = 빨라짐 · 분수 발판 · 계단
      봇 5명이 길 찾아 다니며 서로 싸움 · 🔨 뿅망치로 맞히면 우승 → 결과 창 · 🪙15 · 기록 · 하루 3판 · 나가면 섬 그대로
   ③ 🟦 발판 게임: 파랑 밟으면 지워짐 · 빨강 밟으면 ❤️ -1 · 다 지우면 다음 판 · ❤️ 0 → 결과 · 자동 선수가 2판 이상 깸
   (시험 화면은 느려서 MG.step 으로 시간을 직접 넘김)"""
import asyncio, sys, os
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from fakefb import fake
from playwright.async_api import async_playwright

async def boot_isle(pg, code):
    await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html?isle=1"); await pg.wait_for_timeout(400)
    await pg.evaluate("(c)=>{ localStorage.setItem('hyeng_proto_code', JSON.stringify(c)); localStorage.setItem('hyeng_nick','루아'); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); }", code)
    await pg.reload(); await pg.wait_for_timeout(2600)
    await pg.evaluate("()=>HOUSE.exitRoom()")
    for _ in range(160):
        if await pg.evaluate("()=>HOUSE.place()==='isle' && !HOUSE.trip().busy"): break
        await pg.wait_for_timeout(250)
    await pg.wait_for_timeout(800)

GRID_BOT = """(secs)=>{ const R=MG.run, I=MG.I, N=R.N; let t=0, lost0=R.st.lives; const log=[];
  while(t<secs && !R.st.over){ const P=R.P.p, id=R.idxAt(P.x,P.z), i0=id%N, j0=Math.floor(id/N), bad=q=>R.red[q]||R.warn[q];
    /* 목표: 빨강·경고 아닌 가장 가까운 파랑 */
    let best=-1, bd=1e9; for(let q=0;q<N*N;q++){ if(R.cell[q]!==1 || bad(q)) continue; const d=Math.hypot(R.cx(q%N)-P.x, R.cx(Math.floor(q/N))-P.z); if(d<bd){ bd=d; best=q; } }
    let tx=P.x, tz=P.z; if(bad(id)){ let sb=-1, sd=1e9; for(let q=0;q<N*N;q++){ if(bad(q)) continue; const d=Math.hypot(R.cx(q%N)-P.x, R.cx(Math.floor(q/N))-P.z); if(d<sd){ sd=d; sb=q; } } if(sb>=0){ tx=R.cx(sb%N); tz=R.cx(Math.floor(sb/N)); } }
    else if(best>=0){ tx=R.cx(best%N); tz=R.cx(Math.floor(best/N)); }
    const dx=tx-P.x, dz=tz-P.z, L=Math.hypot(dx,dz); I.mx=L>.15?dx/L:0; I.my=L>.15?-dz/L:0;
    /* 빨강이 바로 옆이면 점프 */
    let near=false; for(let a=-1;a<=1;a++) for(let b=-1;b<=1;b++){ const i=i0+a, j=j0+b; if(i<0||j<0||i>=N||j>=N) continue; if(R.red[j*N+i] && Math.abs(a)+Math.abs(b)<=1) near=true; }
    I.jump=near?1:0;
    MG.step(1/30,false); t+=1/30; }
  I.mx=I.my=0; I.jump=0; return {stage:R.st.stage+1, lives:R.st.lives, score:R.st.score, over:R.st.over, t:+t.toFixed(1)}; }"""

async def main():
    bad=[]; errs=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        for nm,vp in [("pad",{"width":820,"height":1180}),("phone",{"width":844,"height":390})]:
            ctx=await br.new_context(viewport=vp, is_mobile=nm=="phone", has_touch=True)
            pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.on("console", lambda m: m.type=="warning" and ("MG" in m.text) and errs.append(m.text[:200]))
            await boot_isle(pg, "MG590")
            if nm=="pad":
                # ① 게임 타워
                r=await pg.evaluate("""()=>{ const A=MG.SPOT.arena, G=MG.SPOT.grid, L=LBL.filter(l=>/^mg_/.test(l.d.k)).map(l=>l.d.k);
                    return [!!A, !!G, L.sort().join(","), ISLE.blocked(Math.floor(A[0]),Math.floor(A[2])), ISLE.blocked(Math.floor(G[0]),Math.floor(G[2])), !!ISLE.G.getObjectByName("mgGates")]; }""")
                ok(r[0] and r[1] and r[2]=="mg_arena,mg_grid" and r[3] and r[4] and r[5], f"① 놀이 공원 게임 타워 2채 · 이름표 · 부딪힘 {r}")
                await pg.evaluate("()=>{ const g=MG.SPOT.arena; HOUSE.setWx(false); TFAC.warp(g[0]+1, g[2]+8); ISLE.CAM.zoom=2.6; ISLE.CAM.pitch=.85; yaw=yawTo=Math.PI*1.08; ISLE.CAM.dragAt=performance.now()+1e6; }")
                await pg.wait_for_timeout(2200); await pg.screenshot(path=OUT+"mg590_gates.png")
                await pg.evaluate("()=>{ const g=MG.SPOT.arena; TFAC.warp(g[0]+.5, g[2]+3.6); }"); await pg.wait_for_timeout(600)   # 시험 화면은 걸음이 느림 → 문 앞으로
                await pg.evaluate("()=>{ const L=LBL.find(l=>l.d.k==='mg_arena'); L.d.act(); }")
                for _ in range(60):
                    if await pg.evaluate("()=>{ const el=document.getElementById('mgLob'); return !!el && el.classList.contains('on'); }"): break
                    await pg.wait_for_timeout(250)
                await pg.wait_for_timeout(400)
                r=await pg.evaluate("()=>{ const el=document.getElementById('mgLob'); return [el && el.classList.contains('on'), el && el.innerText.includes('물총 아레나'), el && el.querySelectorAll('[data-o=diff]').length, el && /3판/.test(el.innerText)]; }")
                ok(r==[True,True,3,True], f"① 누르면 안내 창 (규칙 · 실력 3가지 · 오늘 🪙 3판) {r}")
                await pg.screenshot(path=OUT+"mg590_lobby.png")
                await pg.evaluate("()=>document.querySelector('#mgLob [data-o=diff][data-v=easy]').click()")
                r=await pg.evaluate("()=>(store('hyeng_proto_mgopt')||{})['arena.diff']")
                ok(r=="easy", f"① 고른 실력은 기억 {r}")
                await pg.evaluate("()=>document.querySelector('#mgLob [data-o=diff][data-v=normal]').click()")
                # ② 아레나
                h0=await pg.evaluate("()=>[hero.g.position.x, hero.g.position.z, renderer.getPixelRatio()]")
                await pg.evaluate("()=>document.querySelector('#mgLob .go').click()"); await pg.wait_for_timeout(1500)
                r=await pg.evaluate("()=>[MG.on, MG.k, document.body.classList.contains('mgOn'), getComputedStyle(document.querySelector('.bar.top')).visibility, MG.run.ACT.length, MG.run.D===undefined?0:1]")
                ok(r[0] and r[1]=="arena" and r[2] and r[3]=="hidden" and r[4]==6, f"② 들어가면 아레나 · 섬 화면은 숨김 · 나+봇 5 {r}")
                r=await pg.evaluate("()=>{ const R=MG.run, me=R.me; R.ACT.forEach(a=>{ if(a.bot) a.prot=0; }); me.cd=0; MG.I.fire=1; MG.step(.05,false); const shot0=me.cd>0; MG.I.fire=0; return [R.time.cd>2, shot0]; }")
                ok(r==[True,False], f"② 3초 세기 동안은 못 쏨 {r}")
                await pg.evaluate("()=>{ for(let i=0;i<70;i++) MG.step(.05,false); }")
                r=await pg.evaluate("""()=>{ const R=MG.run, me=R.me, b=R.ACT[1]; R.ACT.forEach(a=>{ if(a.bot && a!==b){ a.alive=false; a.resp=999; } });
                    me.p.set(0,0,22); me.v.set(0,0,0); b.p.set(0,0,16); b.v.set(0,0,0); b.prot=0; b.soak=0; b.brain.think=99; const out=[];
                    for(let k=0;k<3;k++){ me.cd=0; const e=new THREE.Vector3(me.p.x, me.p.y+1.48, me.p.z), c=new THREE.Vector3(b.p.x, b.p.y+.7, b.p.z); b.p.set(0,0,16); const d=c.clone().sub(e).normalize(); R.fire(me, e, d); out.push(Math.round(b.soak)); }
                    return [out, b.alive, me.wi, me.kills, document.querySelector('#mgUI .aLad b.c').textContent, document.querySelector('#mgUI .aFd').innerText.includes('Tom')]; }""")
                ok(r[1]==False and r[2]==1 and r[3]==1 and r[4]=="✌️" and r[5], f"② 3번 맞히면 흠뻑 → 다음 무기 ✌️ 쌍권총 · 알림 {r}")
                r=await pg.evaluate("""()=>{ const R=MG.run, I=MG.I, me=R.me, st=n=>{ for(let i=0;i<n;i++) MG.step(1/60,false); }, hs=()=>Math.hypot(me.v.x,me.v.z);
                    R.ACT.forEach(a=>{ if(a.bot){ a.alive=false; a.resp=999; } });
                    me.p.set(-14,0,22.5); me.yaw=-Math.PI/2; me.v.set(0,0,0); I.my=1; st(60); const run=hs(); I.slideP=1; st(1); const sl=hs(); st(10); I.jumpP=1; st(1); const sj=hs(), air=!me.onG; I.my=0; st(90);
                    me.p.set(R.PADS[0][0],0,R.PADS[0][1]); me.v.set(0,0,0); let top=0; for(let i=0;i<80;i++){ MG.step(1/60,false); top=Math.max(top,me.p.y); }
                    me.p.set(0,0,-9); me.v.set(0,0,0); me.yaw=Math.PI; I.my=1; st(130); const plat=me.p.y; I.my=0;
                    return [+run.toFixed(1), +sl.toFixed(1), +sj.toFixed(1), air, +top.toFixed(1), +plat.toFixed(2)]; }""")
                ok(r[0]>=7 and r[1]>r[0]+3 and r[2]>r[0]+2 and r[3] and r[4]>3 and abs(r[5]-1.6)<.05, f"② 아레나 무브: 달리기 {r[0]} → 슬라이드 {r[1]} → 슬라이드 점프 {r[2]} · 분수 발판 높이 {r[4]}m · 계단으로 단 위 {r[5]}")
                # 봇이 길 찾아 다니며 싸움
                r=await pg.evaluate("""()=>{ const R=MG.run; R.ACT.forEach(a=>{ if(a.bot){ R.spawn(a); a.prot=0; a.brain.think=0; } }); R.me.alive=false; R.me.resp=999; const p0=R.ACT.map(a=>a.p.clone()); const k0=R.ACT.reduce((s,a)=>s+a.kills,0);
                    let mv=new Set(); for(let i=0;i<500;i++){ MG.step(.05,false); R.ACT.forEach((a,j)=>{ if(a.bot && a.p.distanceTo(p0[j])>3) mv.add(j); }); }
                    const k=R.ACT.reduce((s,a)=>s+a.kills,0)-k0; R.me.resp=0; MG.step(.05,false); return [mv.size, k, R.ACT.filter(a=>a.bot && a.wi>0).length]; }""")
                ok(r[0]==5 and r[1]>=2, f"② 봇 5명 모두 길 찾아 다니며 서로 싸움 (25초: 움직인 봇 {r[0]} · 흠뻑 {r[1]}) {r}")
                await pg.evaluate("()=>{ const R=MG.run, me=R.me; R.ACT.forEach(a=>{ if(a.bot){ a.alive=true; a.prot=0; a.p.set(-6+a.i*3,0,10); a.brain.think=99; a.yaw=0; } }); me.alive=true; me.soak=0; me.p.set(0,0,18); me.yaw=0; me.pitch=-.05; me.wi=2; R.vmSet(2); }")
                await pg.wait_for_timeout(1500); await pg.screenshot(path=OUT+"mg590_arena_pad.png")
                # 🔨 뿅망치로 우승
                c0=await pg.evaluate("()=>TECO.coins()")
                r=await pg.evaluate("""()=>{ const R=MG.run, me=R.me, b=R.ACT[2]; me.wi=7; R.vmSet(7); b.alive=true; b.prot=0; b.soak=0; b.p.set(0,0,16.6); me.p.set(0,0,18); me.cd=0;
                    const e=new THREE.Vector3(0,1.48,18), d=new THREE.Vector3(0,-.3,-1).normalize(); R.fire(me, e, d); return [R.time.over, b.alive]; }""")
                ok(r==[True,False], f"② 🔨 뿅망치로 맞히면 우승 {r}")
                await pg.wait_for_timeout(2600)
                r=await pg.evaluate("()=>{ const el=document.getElementById('mgRes'); return [el.classList.contains('on'), /우승/.test(el.innerText), /🪙 \\+15/.test(el.innerText), (store('hyeng_proto_mg')||{}).t.arena.win, (store('hyeng_proto_mg')||{}).b.arena.fast>0]; }")
                c1=await pg.evaluate("()=>TECO.coins()")
                ok(r[0] and r[1] and r[2] and r[3]==1 and r[4] and c1-c0==15, f"② 결과 창 · 🪙 +15 · 우승 기록 {r} {c1-c0}")
                await pg.screenshot(path=OUT+"mg590_result.png")
                # 하루 3판 — 4번째부터 🪙 없음
                r=await pg.evaluate("()=>{ const c0=TECO.coins(); for(let i=0;i<3;i++) MG.result('arena', {title:'t', coins:5}); return [TECO.coins()-c0, MG.payLeft('arena')]; }")
                ok(r==[10,0], f"② 오늘 🪙 는 3판까지 (2판 더 → +10 · 4판째 0) {r}")
                await pg.evaluate("()=>{ document.querySelector('#mgRes .out').click(); }"); await pg.wait_for_timeout(1500)
                r=await pg.evaluate("(h)=>[MG.on, document.body.classList.contains('mgOn'), !!document.getElementById('mgUI'), HOUSE.place(), Math.hypot(hero.g.position.x-h[0], hero.g.position.z-h[1])<1.5, renderer.getPixelRatio()===h[2]]", h0)
                ok(r==[False,False,False,"isle",True,True], f"② 나가면 섬 그 자리 그대로 · 화면 원래대로 {r}")
                # ③ 발판 게임
                await pg.evaluate("()=>MG.lobby('grid')"); await pg.wait_for_timeout(300)
                await pg.evaluate("()=>document.querySelector('#mgLob .go').click()"); await pg.wait_for_timeout(1500)
                r=await pg.evaluate("()=>{ const R=MG.run; let b=0, g=0; for(let q=0;q<100;q++){ if(R.cell[q]===1) b++; if(R.cell[q]===2) g++; } return [MG.k, b, g, R.st.lives, R.cell[R.idxAt(R.P.p.x,R.P.p.z)]]; }")
                ok(r[0]=="grid" and r[1]>=10 and r[2]>=4 and r[3]==3 and r[4]==2, f"③ 발판 게임: 파랑 {r[1]} · 초록 {r[2]} · ❤️3 · 초록에서 시작 {r}")
                r=await pg.evaluate("()=>{ const R=MG.run; MG.I.mx=.7; MG.I.my=.5; for(let i=0;i<20;i++) MG.step(.03,false); MG.I.mx=MG.I.my=0; const g=R.scene.children.find(c=>c.type==='Group' && c.scale.x>1.2); let ok=true; g.updateMatrixWorld(true); g.traverse(o=>{ if(o.isMesh && !isFinite(o.matrixWorld.elements[13])) ok=false; }); return [ok, g.visible]; }")
                ok(r==[True,True], f"③ (v593) 걸어도 내 캐릭터가 보임 (예전: 걸으면 NaN 으로 사라짐) {r}")
                r=await pg.evaluate("""()=>{ const R=MG.run, N=R.N; const q=[...R.cell].findIndex(v=>v===1); R.P.p.set(R.cx(q%N),0,R.cx(Math.floor(q/N))); const b0=R.st.blue; MG.step(.03,false); const a=[R.cell[q], b0-R.st.blue, R.st.score];
                    const z=[...R.cell].findIndex(v=>v===0); R.st.intro=0; R.P.p.set(R.cx(z%N),0,R.cx(Math.floor(z/N))); R.st.hz=[{k:'blink', L:[z], w:0, on:3, t:0}]; MG.step(.03,false); const l1=R.st.lives;
                    R.P.inv=0; R.P.p.y=.8; R.P.onG=false; R.P.vy=3; MG.step(.03,false); const l2=R.st.lives; return a.concat([l1, l2]); }""")
                ok(r[0]==3 and r[1]==1 and r[2]>=10 and r[3]==2 and r[4]==2, f"③ 파랑 밟으면 지워짐 ⭐ · 빨강 밟으면 ❤️ -1 · 점프 중엔 안 맞음 {r}")
                r=await pg.evaluate("""()=>{ const R=MG.run, N=R.N; R.P.inv=0; R.st.hz=[]; R.P.p.y=0; R.P.onG=true; R.P.vy=0; for(let q=0;q<N*N;q++){ if(R.cell[q]===1){ R.P.p.set(R.cx(q%N),0,R.cx(Math.floor(q/N))); MG.step(.02,false); } }
                    const c=R.st.clearT>0; for(let i=0;i<60;i++) MG.step(.05,false); return [c, R.st.stage+1, R.st.lives]; }""")
                ok(r[0] and r[1]==2, f"③ 파랑을 다 지우면 다음 판 {r}")
                await pg.evaluate("()=>{ const R=MG.run; R.spawnHz(); R.spawnHz(); for(let i=0;i<40;i++) MG.step(.05,false); }")
                await pg.wait_for_timeout(1200); await pg.screenshot(path=OUT+"mg590_grid_pad.png")
                await pg.evaluate("()=>{ document.querySelector('#mgUI .mgX').click(); document.querySelector('#mgUI .mgConf .go').click(); }"); await pg.wait_for_timeout(1500)
                # 자동 선수 (게임이 깰 수 있는지)
                await pg.evaluate("()=>MG.enter('grid',{})"); await pg.wait_for_timeout(1500)
                r=await pg.evaluate(GRID_BOT, 150)
                ok(r["stage"]>=3, f"③ 자동 선수(파랑 찾아가기 · 빨강 옆이면 점프 · 경고 칸 피하기) {r['t']}초에 {r['stage']}판 · ❤️ {r['lives']} · ⭐ {r['score']}")
                r=await pg.evaluate("()=>{ const R=MG.run; R.P.inv=0; R.st.lives=1; R.st.hz=[]; const z=[...R.cell].findIndex(v=>v===0||v===3); R.P.p.set(R.cx(z%10),0,R.cx(Math.floor(z/10))); R.P.p.y=0; R.P.onG=true; R.red[z]=1; R.st.hz=[{k:'blink', L:[z], w:0, on:3, t:0}]; MG.step(.03,false); return R.st.over; }")
                await pg.wait_for_timeout(1800)
                r2=await pg.evaluate("()=>{ const el=document.getElementById('mgRes'); return [el.classList.contains('on'), /판까지/.test(el.innerText), (store('hyeng_proto_mg')||{}).b.grid.st>=1]; }")
                ok(r and r2==[True,True,True], f"③ ❤️ 다 쓰면 결과 창 · 기록 {r} {r2}")
                await pg.evaluate("()=>document.querySelector('#mgRes .out').click()"); await pg.wait_for_timeout(1400)
            else:
                # 휴대폰 가로: 아레나 화면
                await pg.evaluate("()=>MG.enter('arena',{diff:'normal'})"); await pg.wait_for_timeout(1500)
                await pg.evaluate("()=>{ for(let i=0;i<70;i++) MG.step(.05,false); const R=MG.run, me=R.me; R.ACT.forEach(a=>{ if(a.bot){ a.alive=true; a.prot=0; a.p.set(-6+a.i*3,0,8); a.brain.think=99; } }); me.p.set(0,0,18); me.yaw=0; me.pitch=-.03; }")
                await pg.wait_for_timeout(1500); await pg.screenshot(path=OUT+"mg590_arena_phone.png")
                r=await pg.evaluate("()=>{ const q=s=>document.querySelector(s).getBoundingClientRect(); const f=q('#mgUI [data-b=fire]'), j=q('#mgUI [data-b=jump]'), s=q('#mgUI [data-b=slide]'), b=q('#mgUI .aBd'); const ov=(a,c)=>!(a.right<c.left||c.right<a.left||a.bottom<c.top||c.bottom<a.top); return [f.width>=90, ov(f,j), ov(f,s), ov(f,b), f.bottom<=innerHeight, j.bottom<=innerHeight]; }")
                ok(r==[True,False,False,False,True,True], f"휴대폰 가로: 💦 쏘기 · 점프 · 슬라이드 버튼이 겹치지 않음 · 순위표와도 안 겹침 {r}")
                await pg.evaluate("()=>MG.exit()"); await pg.wait_for_timeout(800)
                await pg.evaluate("()=>MG.enter('grid',{})"); await pg.wait_for_timeout(1500)
                await pg.evaluate("()=>{ const R=MG.run; for(let i=0;i<60;i++) MG.step(.05,false); R.spawnHz(); for(let i=0;i<30;i++) MG.step(.05,false); }")
                await pg.wait_for_timeout(1200); await pg.screenshot(path=OUT+"mg590_grid_phone.png")
                await pg.evaluate("()=>MG.exit()"); await pg.wait_for_timeout(800)
            await ctx.close()
        await br.close()
    ok(not errs, f"오류 없음 {errs[:3]}")
    print("\nFAIL" if bad else "\nPASS", len(bad)); sys.exit(1 if bad else 0)

if __name__=="__main__": asyncio.run(main())
