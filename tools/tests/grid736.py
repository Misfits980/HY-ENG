"""(v736) 🟦 발판 게임 — 사용자 「박자 형식 격자는 살 틈이 없어 · 두 번째 벽에 블럭이 다가오는데 애들이 안 밀려 · 이름 때문에 파란 블럭이 안 보여」
   + 「벽이 아이를 밀어내는 건 좋아 · 초록색에선 피해지는 것도 좋고」
   ① ♟ 박자 스텝: 박자마다 빨강은 앞 반만 · 뒤 반은 다 꺼짐(다음 빨강 주황) → 점프 없이 콩콩 옮기는 봇이 한 번도 안 맞음 · 다른 빨강이 안 겹침
   ② 🟪 높은 벽 = 밀기: 서 있으면 벽 앞에 붙어 같이 밀림(❤️ 그대로) · 가장자리에 끼면 ❤️ 하나 · 초록 칸 = 비켜 감 · 틈 = 지나감
   ③ 이름 알약 작게 (패드 가로에서도)"""
import asyncio, sys, os
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from fakefb import fake
from playwright.async_api import async_playwright
OUTD=OUT+"grid736/"; os.makedirs(OUTD, exist_ok=True)

async def main():
    bad=[]; errs=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        ctx=await br.new_context(viewport={"width":1180,"height":820}, has_touch=True)
        pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html?isle=1"); await pg.wait_for_timeout(300)
        await pg.evaluate("()=>{ localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); }")
        await pg.reload(); await pg.wait_for_timeout(2400)
        await pg.evaluate("()=>MG.enter('grid',{mode:'solo'})"); await pg.wait_for_timeout(1500)
        # ① 박자 스텝 — 상태 없는 계산으로 확인
        r=await pg.evaluate("""()=>{ const R=MG.run, N=R.N, out={};
            for(const df of ['easy','normal','hard']){ let worst=9, gapMin=9, over=0;
              for(let seed=1;seed<=20;seed++) for(const s of [2,6]){ const P=R.plan(seed, s, df); const hs=P.H.filter(h=>h.k==='checker'); for(const h of hs){
                const red=new Float32Array(N*N), warn=new Float32Array(N*N), cell=new Uint8Array(N*N);
                /* 박자 사이에 「모든 칸이 안 빨강」인 시간이 얼마나 되나 + 그 시간에 다른 무늬가 겹쳤나 */
                for(let b=0;b<h.n-1;b++){ let free=0; for(let k=0;k<40;k++){ const tt=h.t0+h.w+b*h.per+k*h.per/40; R.hzAt([h], tt, cell, red, warn); const any=red.some(v=>v>0); if(!any) free+=h.per/40;
                    R.hzAt(P.H.filter(x=>x!==h), tt, cell, red, warn); if(red.some(v=>v>0)) over++; }
                  gapMin=Math.min(gapMin, free); } } }
              out[df]={gapMin:+gapMin.toFixed(2), over}; }
            return out; }""")
        ok(all(r[k]["gapMin"]>=0.5 for k in r), f"① 박자 사이 다 꺼지는 시간 ≥ 0.5초 {r}")
        ok(all(r[k]["over"]==0 for k in r), f"① 박자 스텝 동안 다른 빨강 안 겹침 {r}")
        # 봇: 점프 없이 박자마다 「방금 꺼진 색」으로 한 칸 옮김
        r=await pg.evaluate("""async ()=>{ const R=MG.run, st=R.st, P=R.P, N=R.N; st.lives=3; P.inv=0; R.newStage(2); st.pl.H=[{t0:1, k:'checker', w:1.85, per:1.5, n:8, p0:0, sig:'checker'}]; st.pl.GD=[]; st.pl.GO=null;
            for(let q=0;q<N*N;q++){ if(R.cell[q]===2) R.cell[q]=0; }   /* 초록 없이 */
            P.p.set(R.cx(6),0,R.cx(6)); const I=MG.I; let hits=0, l0=st.lives, hops=0, tgt=null;
            for(let f=0;f<260;f++){ const el=st.el, h=st.pl.H[0], u=el-h.t0-h.w; I.mx=0; I.my=0; I.jump=0; I.jumpP=0;
              const id=R.idxAt(P.p.x,P.p.z), i=id%N, j=Math.floor(id/N), par=(i+j)%2;
              let bad;   /* 다음에 빨강이 될 색 */
              if(u<0) bad=h.p0; else { const b=Math.floor(u/h.per), ph=u-b*h.per; bad = ph<h.per*.5 ? (b+h.p0)%2 : (b+1+h.p0)%2; }
              if(par===bad && (u<0 || (u-Math.floor(u/h.per)*h.per)>=h.per*.5 || u<0)){ if(!tgt){ tgt=[R.cx(i+(i<N-2?1:-1)), R.cx(j)]; hops++; } }
              if(tgt){ const dx=tgt[0]-P.p.x; if(Math.abs(dx)<.15){ tgt=null; } else { I.mx=Math.sign(dx); } }
              MG.step(1/20, false); await null; }
            I.mx=0; return {lost:l0-st.lives, hops}; }""")
        ok(r["lost"]==0 and r["hops"]>=6, f"① 점프 없이 콩콩 옮기면 안 맞음 {r}")
        # ② 벽 밀기
        WALL = """async ([x, z, green, gap])=>{ const R=MG.run, st=R.st, P=R.P, N=R.N; R.newStage(5); st.lives=3; P.inv=0; st.pl.GD=[]; st.pl.GO=null;
            for(let q=0;q<N*N;q++){ if(R.cell[q]===2) R.cell[q]=0; }
            const i=Math.floor((x+R.HALF)/R.TS), j=Math.floor((z+R.HALF)/R.TS); if(green) R.cell[j*N+i]=2;
            st.pl.H=[{t0:.2, k:'row', dir:1, sp:2.2, w:.6, th:1, hi:1, gap: gap?[i-1,i+1]:[0,0]}]; if(!gap) st.pl.H[0].gap=[N+5,N+6];
            P.p.set(x,0,z); const I=MG.I; I.mx=0; I.my=0; let pushed=0, zmax=z; for(let f=0;f<200;f++){ MG.step(1/20,false); if(P.p.z>z+.3) pushed=1; zmax=Math.max(zmax,P.p.z); await null; }
            return {lost:3-st.lives, pushed, z0:+z.toFixed(2), zmax:+zmax.toFixed(2)}; }"""
        mid=await pg.evaluate("()=>MG.run.cx(6)")
        r=await pg.evaluate(WALL, [mid, mid, False, False])
        ok(r["pushed"]==1 and r["lost"]==1, f"② 서 있으면 벽이 밀고 감 → 끝까지 밀려 끼면 ❤️ 하나 {r}")
        r=await pg.evaluate(WALL, [mid, mid, True, False])
        ok(r["pushed"]==0 and r["lost"]==0, f"② 초록 칸에 서 있으면 벽이 비켜 감 {r}")
        r=await pg.evaluate(WALL, [mid, mid, False, True])
        ok(r["pushed"]==0 and r["lost"]==0, f"② 틈 자리면 그냥 지나감 {r}")
        # 밀리는 중 = 벽 앞에 붙어 있음 (뚫고 지나가지 않음) · 화면 사진
        r=await pg.evaluate("""async ()=>{ const R=MG.run, st=R.st, P=R.P, N=R.N; R.newStage(5); st.lives=3; P.inv=0; st.pl.GD=[]; st.pl.GO=null; for(let q=0;q<N*N;q++){ if(R.cell[q]===2) R.cell[q]=0; }
            st.pl.H=[{t0:.2, k:'row', dir:1, sp:1.6, w:.6, th:1, hi:1, gap:[2,4]}]; P.p.set(R.cx(7),0,R.cx(4)); const I=MG.I; I.mx=0; I.my=0; let inside=0;
            for(let f=0;f<90;f++){ MG.step(1/20, f>80); const h=st.pl.H[0], u=st.el-h.t0-h.w; if(u>0){ const pos=-.5+u*h.sp, F=-R.HALF+R.TS*(pos+1), Bk=-R.HALF+R.TS*pos; if(P.p.z>Bk+.1 && P.p.z<F-.1) inside++; } await null; }
            return {inside, z:+P.p.z.toFixed(2), lost:3-st.lives}; }""")
        await pg.wait_for_timeout(200); await pg.screenshot(path=OUTD+"wall_push.png")
        ok(r["inside"]==0 and r["lost"]==0, f"② 밀리는 동안 벽 속에 안 들어감 {r}")
        # ③ 이름 알약
        r=await pg.evaluate("()=>{ const R=MG.run; MG.step(.05,true); return 1; }")
        await br.close()
    print("오류", errs[:4])
    if errs: bad.append("errors")
    print("BAD: %d" % len(bad))
    if bad: sys.exit(1)
asyncio.run(main())
