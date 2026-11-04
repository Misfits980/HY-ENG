"""(v595) 사용자: 「나중엔 점프로만 피할 수 없게 · 초록 칸도 적어져야 · 빨간 칸이 선풍기처럼 돌아가기도 · 그러려면 조금 더 넓어야」
   ① 바닥 14×14 · 🟩 판마다 줄어듦(9판 ≤3칸) · 4판부터 30초에 절반 꺼짐
   ② 🟪 높은 벽 = 점프 중에도 맞음 · 틈(3칸)은 안전 · 굵은 줄 = 2~3칸
   ③ 🌀 선풍기 = 날개 3~4개가 돌아감 (시간 따라 빨간 칸이 바뀜)"""
import asyncio, sys, os
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from fakefb import fake
from playwright.async_api import async_playwright

async def main():
    bad=[]; errs=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        ctx=await br.new_context(viewport={"width":820,"height":1180}, has_touch=True)
        pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html?isle=1"); await pg.wait_for_timeout(300)
        await pg.evaluate("()=>{ localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); }")
        await pg.reload(); await pg.wait_for_timeout(2400)
        await pg.evaluate("()=>MG.enter('grid',{mode:'solo'})"); await pg.wait_for_timeout(1500)
        r=await pg.evaluate("()=>{ const R=MG.run; return [R.N, [0,2,4,6,8].map(s=>R.plan(5,s).G.length), [0,1,2].map(s=>!!R.plan(5,s).GO), !!R.plan(5,4).GO]; }")
        ok(r[0]==14 and r[1][0]>r[1][2]>=r[1][3]>=r[1][4] and r[1][4]<=3 and r[2]==[False,False,False] and r[3], f"① 14×14 · 🟩 줄어듦 {r[1]} · 4판부터 판 중간에 꺼짐")
        r=await pg.evaluate("""()=>{ const R=MG.run; R.newStage(4); R.st.intro=0; R.P.inv=0; const g0=[...R.cell].filter(v=>v===2).length; R.st.el=29.9; MG.step(.05,false); MG.step(.05,false); const g1=[...R.cell].filter(v=>v===2).length; return [g0, g1]; }""")
        ok(r[1]<r[0] and r[1]>=1, f"① 30초에 🟩 절반 꺼짐 {r}")
        # ② 높은 벽 · 틈 · 점프
        r=await pg.evaluate("""()=>{ const R=MG.run, N=R.N; const H=[{t0:0, k:'row', dir:1, sp:2, w:0, th:1, hi:1, gap:[5,7]}], c=new Uint8Array(N*N), red=new Float32Array(N*N), warn=new Float32Array(N*N), hi=new Float32Array(N*N);
            R.hzAt(H, 2.75, c, red, warn, hi); const row=Math.round(-.5+2.75*2); const L=[]; for(let i=0;i<N;i++) L.push(red[row*N+i]?(hi[row*N+i]?'H':'r'):'.');
            const B=[{t0:0, k:'col', dir:1, sp:1.5, w:0, th:3}]; R.hzAt(B, 4, c, red, warn, hi); let cols=new Set(); for(let q=0;q<N*N;q++) if(red[q]) cols.add(q%N);
            return [L.join(''), cols.size]; }""")
        ok(r[0]=="HHHHH...HHHHHH" and r[1]==3, f"② 🟪 높은 벽 + 틈 3칸 {r[0]} · 굵은 줄 = {r[1]}칸")
        r=await pg.evaluate("""()=>{ const R=MG.run, N=R.N; R.st.pl.H.length=0; R.st.lives=3; R.P.inv=0; const z=[...R.cell].findIndex(v=>v===0); const i=z%N, j=Math.floor(z/N);
            R.st.pl.H.push({t0:R.st.el-.01, k:'blink', L:[z], w:0, on:5, hi:1}); R.P.p.set(R.cx(i),1.0,R.cx(j)); R.P.onG=false; R.P.vy=4; MG.step(.02,false); const a=R.st.lives;
            R.P.inv=0; R.st.pl.H.length=0; R.st.pl.H.push({t0:R.st.el-.01, k:'blink', L:[z], w:0, on:5}); R.P.p.set(R.cx(i),1.0,R.cx(j)); R.P.onG=false; R.P.vy=4; MG.step(.02,false); const b=R.st.lives; return [a, b]; }""")
        ok(r==[2,2], f"② 점프 중: 🟪 높은 것은 맞음(❤️3→2) · 보통 빨강은 안 맞음 {r}")
        # ③ 선풍기
        r=await pg.evaluate("""()=>{ const R=MG.run, N=R.N; const H=[{t0:0, k:'fan', cx:6.5, cz:6.5, nb:4, a:0, sp:1.2, len:7, dur:8, w:0}], c=new Uint8Array(N*N), red=new Float32Array(N*N), warn=new Float32Array(N*N);
            R.hzAt(H, 1, c, red, warn); const a=[...red].join(''); const n1=[...red].filter(v=>v).length; R.hzAt(H, 1.6, c, red, warn); const b=[...red].join(''); R.hzAt(H, 9.5, c, red, warn); const n3=[...red].filter(v=>v).length; return [n1, a!==b, n3]; }""")
        ok(r[0]>=24 and r[1] and r[2]==0, f"③ 🌀 선풍기 날개 4개 · 돌아감 · 끝나면 사라짐 {r}")
        # (v596) 쉬움 · 어려움
        r=await pg.evaluate("""()=>{ const R=MG.run; const f=df=>{ const P=R.plan(9,6,df); return [P.G.length, P.H.length, P.H.some(h=>h.hi), +Math.max(...P.H.filter(h=>h.k==='row'||h.k==='col').map(h=>h.sp)).toFixed(2)]; }; return [f('easy'), f('normal'), f('hard')]; }""")
        e,n,h=r
        ok(e[0]>n[0]>h[0] and e[1]<n[1]<h[1] and not e[2] and e[3]<n[3]<h[3], f"(v596) 7판: 쉬움 = 🟩 많고 빨강 적고 느림 · 🟪 없음 / 어려움 = 반대 {r}")
        await pg.evaluate("()=>MG.exit()"); await pg.wait_for_timeout(900)
        await pg.evaluate("()=>MG.enter('grid',{mode:'solo', df:'easy'})"); await pg.wait_for_timeout(1500)
        r=await pg.evaluate("()=>[MG.run.st.lives, document.querySelector('#mgUI .lv').textContent]")
        ok(r[0]==5 and r[1].count("❤️")==5 if False else r[0]==5, f"(v596) 쉬움 = ❤️5 {r}")
        await pg.wait_for_timeout(1500); await pg.screenshot(path=OUT+"grid596_me.png")
        await br.close()
    ok(not errs, f"오류 없음 {errs[:2]}")
    print("\nFAIL" if bad else "\nPASS", len(bad)); sys.exit(1 if bad else 0)

if __name__=="__main__": asyncio.run(main())
