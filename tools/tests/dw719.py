"""(v719) 🎨 그림 맞히기 난이도 = 학년 + 동사 — 사용자 「어려움에 코끼리 이런 게 나오고 다 명사라 · 행동하는 동사 단어도 · 어려움 = 초5-6 · 보통 = 초1-2·초3-4 · 쉬움 = 유아·초1-2」
   ① 단어 묶음: 쉬움 = 학년 1 · 보통 = 학년 2 + 학년 1 긴 것 · 어려움 = 학년 3 (코끼리 없음) · 혼자 퍼즐 그림이 겹치지 않음
   ② 메뉴 단계 단추에 학년 글
   ③ 혼자 8문제 = 동사 3 + 이름씨 5 · 동사 문제 「동사」 표시 · 글자 칸 = 원래 모양
   ④ 그려 보기 3개 = 동사 하나 + 이름씨 둘
   ⑤ 같이 2명: 방 단계(어려움) → 방 목록 글 · 고르는 3개도 어려움 · 동사를 그리면 친구 화면 「동사」 · 맞힘"""
import asyncio, sys, os
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from draw635 import boot
async def enter(pg, k):
    for _ in range(30):
        if not await pg.evaluate("()=>MG.on"): break
        await pg.wait_for_timeout(200)
    for t in range(3):
        await pg.evaluate("(k)=>{ if(!MG.on) MG.enter(k,{}); }", k)
        for _ in range(80):
            if await pg.evaluate("()=>!!(MG.on && MG.run && MG.run.ready)"): break
            await pg.wait_for_timeout(200)
        if await pg.evaluate("()=>!!(MG.on && MG.run && MG.run.ready)"): break
    await pg.wait_for_timeout(400)
STEP = """async (n)=>{ for(let i=0;i<n;i++){ MG.step(.05,false); await null; await null; } }"""
from playwright.async_api import async_playwright
OUTD=OUT+"dw719/"; os.makedirs(OUTD, exist_ok=True)
bad=[]
def ok(c,m):
    print(("OK  " if c else "BAD ")+m, flush=True)
    if not c: bad.append(m)
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        ctx,pg,errs=await boot(br,"루아","DW719A", vp={"width":768,"height":954}, isle=False)
        await enter(pg, "draw")
        # ① 묶음
        r=await pg.evaluate("""()=>{ const R=MG.run, W=R.W, out={};
            [1,2,3].forEach(lv=>{ const P=R.POOL(lv); out[lv]={n:P.length, v:P.filter(i=>W[i][4].includes('v')).length, solo:P.filter(i=>!W[i][4].includes('x')).length,
                g:[...new Set(P.map(i=>W[i][3]))].sort().join(','), eleph:P.some(i=>W[i][0]==='elephant'), cat:P.some(i=>W[i][0]==='cat'), astro:P.some(i=>W[i][0]==='astronaut')}; });
            const em={}; W.forEach((w,i)=>{ if(!w[4].includes('x')) (em[w[2]]=em[w[2]]||[]).push(w[0]); }); out.dupE=Object.values(em).filter(a=>a.length>1);
            out.five=W.every(w=>w.length===5 && typeof w[3]==='number' && typeof w[4]==='string'); out.first=W.slice(0,3).map(w=>w[0]).join(',');
            return out; }""")
        ok(r["1"]["g"]=="1" and r["1"]["n"]>=120 and r["1"]["v"]>=30 and r["1"]["cat"] and not r["1"]["astro"], f"① 쉬움 = 유아·초1-2 {r["1"]}")
        ok(r["2"]["g"]=="1,2" and r["2"]["n"]>=100 and r["2"]["v"]>=15 and r["2"]["eleph"] and not r["2"]["cat"], f"① 보통 = 초1-2(긴 말)·초3-4 {r["2"]}")
        ok(r["3"]["g"]=="3" and r["3"]["n"]>=100 and r["3"]["v"]>=15 and not r["3"]["eleph"] and r["3"]["astro"], f"① 어려움 = 초5-6 · 코끼리 없음 {r["3"]}")
        ok(not r["dupE"], f"① 혼자 퍼즐 그림 겹침 없음 {r['dupE'][:4]}")
        ok(r["five"] and r["first"]=="cat,dog,bird", f"① 단어 칸 다섯 · 앞 순서 그대로(같이 하기 번호) {r['first']}")
        # ② 메뉴
        t=await pg.evaluate("()=>[...document.querySelectorAll('#mgUI .puSeg button')].map(b=>b.innerText.replace(/\\s+/g,' ').trim())")
        ok(len(t)==3 and "유아" in t[0] and "초3-4" in t[1] and "초5-6" in t[2], f"② 단계 단추 학년 {t}")
        over=await pg.evaluate("()=>{ const b=[...document.querySelectorAll('#mgUI .puSeg button')]; return b.some(x=>x.scrollWidth>x.clientWidth+1 || x.getBoundingClientRect().right>innerWidth); }")
        ok(not over, "② 단추 글 안 넘침")
        await pg.screenshot(path=OUTD+"menu.png")
        # ③ 혼자 — 단계마다
        for lv in (1,2,3):
            await pg.evaluate("(lv)=>{ MG.run.setLv(lv); MG.run.menuGo('solo'); }", lv); await pg.wait_for_timeout(200)
            r=await pg.evaluate("(lv)=>{ const R=MG.run, W=R.W, q=[R.S.cur].concat(R.S.q); return {n:q.length, v:q.filter(i=>W[i][4].includes('v')).length, x:q.filter(i=>W[i][4].includes('x')).length, g:q.every(i=>R.POOL(lv).includes(i)), w:q.map(i=>W[i][0]).join(',')}; }", lv)
            ok(r["n"]==8 and r["v"]==3 and r["x"]==0 and r["g"], f"③ 혼자 {lv}단계: 8문제 · 동사 3 · 그 단계 단어 {r}")
            # 동사 문제까지 넘기기
            for k in range(9):
                cur=await pg.evaluate("()=>{ const R=MG.run; return [R.W[R.S.cur][0], R.W[R.S.cur][4].includes('v'), document.querySelector('#mgUI .dwVb').classList.contains('on'), R.fb]; }")
                if cur[1]: break
                ok(not cur[2], f"③ 이름씨 문제엔 「동사」 표시 없음 {cur[0]}") if k==0 else None
                await pg.evaluate("()=>{ const R=MG.run; R.typeWord(R.ans()); R.submit(); }"); await pg.evaluate(STEP, 40); await pg.wait_for_timeout(100)
            ok(cur[1] and cur[2] and "동사" in cur[3], f"③ {lv}단계 동사 문제: 「동사」 표시 · 안내 {cur}")
            if lv==1: await pg.evaluate(STEP, 30); await pg.screenshot(path=OUTD+"solo_verb.png")
            r=await pg.evaluate("()=>{ const R=MG.run, w=R.ans(), n=document.querySelectorAll('#mgUI .dwBx i').length, ok0=R.S.ok; R.typeWord(w); R.submit(); return [w, n, R.S.ok-ok0, R.fb]; }")
            ok(r[1]==len(r[0]) and r[2]==1 and "정답" in r[3], f"③ {lv}단계 동사도 글자 칸 = 원래 모양 길이 · 맞힘 {r}")
            await ctx.close(); ctx,pg,e2=await boot(br,"루아","DW719A", vp={"width":768,"height":954}, isle=False); errs+=e2; await enter(pg, "draw")
        # ④ 그려 보기
        r=await pg.evaluate("()=>{ const R=MG.run; R.setLv(3); R.menuGo('sketch'); const ch=R.SK.ch, W=R.W; return {n:ch.length, v:ch.filter(i=>W[i][4].includes('v')).length, g:ch.every(i=>W[i][3]===3), tag:document.querySelectorAll('#mgUI .dwOv.on .dwVt').length, w:ch.map(i=>W[i][0]).join(',')}; }")
        ok(r["n"]==3 and r["v"]==1 and r["g"] and r["tag"]==1, f"④ 그려 보기 어려움: 동사 하나 + 이름씨 둘 · 「동사」 표 {r}")
        await pg.screenshot(path=OUTD+"sketch_pick.png")
        await ctx.close()
        # ⑤ 같이 2명 (방장 = 어려움)
        cA,A_,eA=await boot(br,"루아","DW719A", isle=False); cB,B_,eB=await boot(br,"민수","DW719B", isle=False)
        P2=[A_,B_]
        async def steps(n=1):
            for _ in range(n):
                for x in P2: await x.evaluate("async ()=>{ MG.step(.1,false); await null; await null; }")
                await A_.wait_for_timeout(40)
        for x in P2: await enter(x, "draw")
        await A_.evaluate("()=>{ MG.run.setLv(3); MG.run.menuGo('co'); }"); await steps(3)
        await A_.evaluate("()=>MG.run.RM.make()"); await steps(4)
        await B_.evaluate("()=>{ MG.run.setLv(1); MG.run.menuGo('co'); }")
        tag=""
        for _ in range(15):
            await B_.evaluate("()=>MG.run.RM.list()"); await steps(2)
            tag=await B_.evaluate("()=>{ const b=document.querySelector('#mgUI [data-j]'); return b ? b.innerText : ''; }")
            if tag: break
        ok("어려움" in tag and "초5-6" in tag, f"⑤ 방 목록에 방 단계 「{tag.strip()[:40]}」")
        await B_.evaluate("()=>document.querySelector('#mgUI [data-j]').click()"); await steps(4)
        for x in P2: await x.evaluate("()=>{ MG.run.fast=true; }")
        await A_.evaluate("()=>document.querySelector('#mgUI [data-st]').click()"); await steps(4)
        for x in P2: await x.evaluate("()=>{ TWN8.test=(TWN8.test||0)+7000; }")
        for _ in range(30):
            await steps(3)
            r=[await x.evaluate("()=>[MG.run.mode, MG.run.G.ph, MG.run.G.dr]") for x in P2]
            if all(q[0]=="co-play" and q[1]=="pick" for q in r): break
        st=await A_.evaluate("()=>{ const R=MG.run, W=R.W; return [R.G.lv, R.G.ch.map(i=>W[i][3]).join(','), R.G.ch.filter(i=>W[i][4].includes('v')).length, R.G.dr]; }")
        ok(st[0]==3 and set(st[1].split(","))=={"3"} and st[2]==1, f"⑤ 방장 단계 3 · 고르는 3개 = 초5-6 · 동사 1 {st}")
        codes={"DW719A":A_,"DW719B":B_}; D=codes[st[3]]; O=B_ if D is A_ else A_
        await D.evaluate("()=>{ const R=MG.run, W=R.W, k=R.G.ch.findIndex(i=>W[i][4].includes('v')); document.querySelectorAll('#mgUI .dwOv.on [data-p]')[k].click(); }"); await steps(5)
        for _ in range(20):
            if all([await x.evaluate("()=>MG.run.G.ph==='draw'") for x in P2]): break
            await steps(2)
        await D.evaluate("()=>MG.run.demo(3)"); await steps(6)
        w=await D.evaluate("()=>MG.run.ans()")
        r=await O.evaluate("()=>[document.querySelector('#mgUI .dwVb').classList.contains('on'), MG.run.G.vb]")
        rd=await D.evaluate("()=>document.querySelector('#mgUI .dwVb').classList.contains('on')")
        ok(r[0] and r[1]==1 and not rd, f"⑤ 동사를 그리면 맞히는 친구 화면에 「동사」 (그리는 사람은 안 보임) {r} {rd}")
        await O.screenshot(path=OUTD+"co_verb_guess.png")
        await O.evaluate("(s)=>{ MG.run.typeWord(s); MG.run.submit(); }", w); await steps(4)
        r=await A_.evaluate("()=>Object.keys(MG.run.G.ok||{}).length")
        ok(r==1, f"⑤ 친구가 「{w}」 맞힘 → 방장이 정답으로 셈 {r}")
        ok(not (errs+eA+eB), f"오류 없음 {(errs+eA+eB)[:3]}")
        for c in (cA,cB): await c.close()
        await br.close()
    print("\n== 결과:", "모두 통과" if not bad else f"{len(bad)}개 실패")
    sys.exit(1 if bad else 0)
asyncio.run(main())
