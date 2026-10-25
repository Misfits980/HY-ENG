"""(v400) 유치부는 섞지 않는다 — 팀 대항전에서 유치부(반 이름에 유치·씨앗 …)는 유치부끼리, 나머지는 나머지끼리
  ① 유치부 6명 + 사자반 8명 → 유치부 팀들엔 유치부만, 다른 팀들엔 유치부가 한 명도 없음
  ② 유치부 아이 화면: 「유치부」 표시 + 유치부 팀만 보임 / 다른 아이 화면: 유치부 팀 안 보임
  ③ 유치부 3명뿐이면 유치부는 「4명 이상」 안내 (나머지와 섞이지 않음), 나머지는 정상
  ④ 지난주 우승 💎은 자기 그룹 안에서만 계산"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright
Y={f'y{i}':f'유{i}' for i in range(1,7)}; O={f'o{i}':f'일{i}' for i in range(1,9)}
async def main():
    bad=[]; errs=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(); ctx=await br.new_context(viewport={"width":390,"height":844}, service_workers="block"); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        A=await ctx.new_page(); A.on("pageerror", lambda e: errs.append(str(e))); await boot(A)
        def roster(ys):
            k={i:{'n':n,'t':'y'} for i,n in list(Y.items())[:ys]}; k.update({i:{'n':n,'t':'a'} for i,n in O.items()}); return k
        async def setr(k):
            await A.evaluate("""(k)=>{ HyBoss.live(); return FB.set('/hy/roster', {t:{y:{n:'유치부',e:'🧸'}, a:{n:'사자반',e:'🦁'}}, k}); }""", k)
            await A.wait_for_timeout(600); await A.evaluate("()=>HyBoss.refresh(true)")
        await setr(roster(6)); mon=await A.evaluate("()=>HyBoss.monday()")
        tm=await A.evaluate("(m)=>Cup.teams(m).map(x=>[x.t,x.g,x.ids])", mon); print(tm)
        ty=[t for t in tm if t[1]=='y']; to=[t for t in tm if t[1]=='o']
        ok(len(ty)==2 and sorted(i for t in ty for i in t[2])==sorted(Y), f"유치부 6명 → 유치부끼리 2팀 {[len(t[2]) for t in ty]}")
        ok(len(to)==2 and sorted(i for t in to for i in t[2])==sorted(O), "나머지 8명 → 나머지끼리 2팀, 유치부 없음")
        ok(len({t[0] for t in tm})==len(tm), "팀 id 안 겹침")
        # ② 화면
        await A.evaluate("([i,n])=>{ Kid.set({id:i,n:n,t:'y'}); showRank('cup'); }", ['y1', Y['y1']]); await A.wait_for_timeout(1500)
        t=await A.evaluate("()=>document.getElementById('rankList').innerText"); n=await A.evaluate("()=>document.querySelectorAll('#rankList .cpT').length")
        ok("유치부" in t and n==2, f"유치부 아이: 「유치부」 표시 · 팀 막대 2개 ({n})")
        ok("일1" not in t, "유치부 화면에 다른 반 이름 없음")
        await A.evaluate("()=>showRank('easy')")
        await A.evaluate("([i,n])=>{ Kid.set({id:i,n:n,t:'a'}); showRank('cup'); }", ['o1', O['o1']]); await A.wait_for_timeout(1500)
        t=await A.evaluate("()=>document.getElementById('rankList').innerText"); n=await A.evaluate("()=>document.querySelectorAll('#rankList .cpT').length")
        ok("유치부" not in t and n==2, f"다른 아이: 유치부 표시 없음 · 팀 2개 ({n})")
        # ③ 유치부 3명
        await setr(roster(3)); await A.evaluate("()=>showRank('easy')")
        tm=await A.evaluate("(m)=>Cup.teams(m).map(x=>[x.t,x.g,x.ids])", mon)
        ok(not [t for t in tm if t[1]=='y'] and len([t for t in tm if t[1]=='o'])==2, "유치부 3명 → 유치부 팀 없음, 나머지는 그대로")
        await A.evaluate("([i,n])=>{ Kid.set({id:i,n:n,t:'y'}); showRank('cup'); }", ['y1', Y['y1']]); await A.wait_for_timeout(1500)
        t=await A.evaluate("()=>document.getElementById('rankList').innerText")
        ok("4명 이상" in t and "유치부" in t, "유치부 3명뿐 → 「유치부 … 4명 이상」 안내 (다른 반과 안 섞임)")
        # ④ 우승 💎 은 자기 그룹 안에서만
        await setr(roster(6)); await A.evaluate("()=>showRank('easy')")
        last=await A.evaluate("()=>HyBoss.monday(Date.now()-7*864e5)"); ld=await A.evaluate("(m)=>Cup.addDay(m,2)", last)
        tl=await A.evaluate("(m)=>Cup.teams(m).map(x=>[x.t,x.g,x.ids])", last)
        ly=[t for t in tl if t[1]=='y']; lo=[t for t in tl if t[1]=='o']
        pts={ly[0][2][0]:[20,10], ly[1][2][0]:[1,0], lo[0][2][0]:[500,0], lo[1][2][0]:[1,0]}   # 나머지 그룹 점수가 훨씬 커도 유치부 우승은 따로
        await A.evaluate("""([d,P])=>{ const o={}; Object.keys(P).forEach(i=>{ o[i]={n:'x',so:P[i][0],rr:P[i][1]}; }); return FB.set('/hy/day/'+d, o); }""", [ld, pts])
        winY=ly[0][2][0]; loseY=ly[1][2][0]
        await A.evaluate("(m)=>{ localStorage.removeItem('hyeng_cup_'+m); Cup._c={}; }", last)   # 앞에서 빈 지난주 기록이 기기에 남았음
        for who,exp in ((winY,10),(loseY,0)):
            await A.evaluate("([i,n])=>{ Kid.set({id:i,n:n,t:'y'}); }", [who, Y.get(who,'x')])
            g0=await A.evaluate("()=>Wallet.gems()"); await A.evaluate("()=>showRank('cup')"); await A.wait_for_timeout(1500); g1=await A.evaluate("()=>Wallet.gems()")
            await A.evaluate("()=>showRank('easy')")
            ok(g1-g0==exp, f"유치부 {who} 지난주 💎 {exp} 기대 → {g1-g0}")
        real=[e for e in errs if 'ResizeObserver' not in e]
        ok(not real, f"페이지 오류 없음 {real[:2]}")
        await br.close()
    print("DONE bad=%d"%len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
