"""(v399) 🎲 집에서 하는 팀 대항전 (랜덤 팀 · 이름 있는 아이만) + 💌 응원
  ① 랭킹 → 「팀 대항」 · 명단에 이름 있는 아이를 월요일 날짜로 섞어 팀으로 (인원 거의 같게, 모든 기기가 같은 팀) · 팀 1인 평균 · 내 팀 표시 · 영웅 3명
  ② 지난주 우승 팀 💎10 (아이마다 한 번 · 지난주 1문제도 안 한 아이는 못 받음)
  ③ 응원: 이모티콘만 · 같은 팀 친구에게 · 하루 5번 · 같은 친구 하루 한 번 · 🏆 랭킹 단추에 새 응원 점
  ④ 이름 있는 아이가 4명보다 적으면 안 열림 · 이름 글자는 HTML 로 안 읽힘 · 반 없는 중복 이름은 뺌"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright
KIDS={'k1':'민준','k2':'서연<b>x</b>','k3':'하준','k4':'수아','k5':'도윤','k6':'지우','k7':'예준','k8':'서윤'}
async def main():
    bad=[]; errs=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(); ctx=await br.new_context(viewport={"width":390,"height":844}, service_workers="block"); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        A=await ctx.new_page(); A.on("pageerror", lambda e: errs.append("A "+str(e))); await boot(A)
        k={i:{'n':n,'t':('a' if int(i[1:])%2 else 'b')} for i,n in KIDS.items()}; k['kd']={'n':'👤민준'}   # 반 없는 중복 이름
        await A.evaluate("""(k)=>{ HyBoss.live(); return FB.set('/hy/roster', {t:{a:{n:'사자반',e:'🦁'}, b:{n:'돌고래반',e:'🐬'}}, k}); }""", k)
        await A.wait_for_timeout(600); await A.evaluate("()=>HyBoss.refresh(true)")
        today=await A.evaluate("()=>HyBoss.dayOf(Date.now())"); mon=await A.evaluate("()=>HyBoss.monday()"); last=await A.evaluate("()=>HyBoss.monday(Date.now()-7*864e5)")
        lastDay=await A.evaluate("(m)=>Cup.addDay(m,2)", last)
        # ① 팀 나누기
        tm=await A.evaluate("(m)=>Cup.teams(m).map(x=>[x.t,x.n,x.ids])", mon); print(tm)
        allids=sorted(i for t in tm for i in t[2])
        ok(len(tm)==2 and sorted(len(t[2]) for t in tm)==[4,4], f"8명 → 2팀 4명씩 {[len(t[2]) for t in tm]}")
        ok(allids==sorted(KIDS), "이름 있는 아이 8명만 (반 없는 👤민준은 빠짐), 한 명도 두 팀에 안 들어감")
        B=await ctx.new_page(); B.on("pageerror", lambda e: errs.append("B "+str(e))); await boot(B)
        await B.evaluate("()=>{ HyBoss.live(); return HyBoss.refresh(true); }"); await B.wait_for_timeout(500)
        tm2=await B.evaluate("(m)=>Cup.teams(m).map(x=>[x.t,x.n,x.ids])", mon)
        ok(tm==tm2, "다른 기기도 같은 팀")
        oth=await A.evaluate("()=>Cup.teams('2026-01-05').map(x=>x.ids.join())"); print("다른 주 팀 예:", oth)
        T0,T1=tm[0],tm[1]   # 점수 큰 쪽 = T0
        w=T0[2]; l=T1[2]
        pts_now={w[0]:[30,20], w[1]:[40,10], w[2]:[0,0], w[3]:[0,0], l[0]:[5,5], l[1]:[0,0], l[2]:[0,0], l[3]:[0,0]}   # T0 합 100 → 평균 25 / T1 합 10 → 2.5
        # 지난주: 반대로 T1(지금 기준) 이 아니라 지난주 팀 기준으로 우승 팀을 정함
        tl=await A.evaluate("(m)=>Cup.teams(m).map(x=>[x.t,x.n,x.ids])", last)
        lw=tl[0][2]; ll=tl[1][2]
        lastpts={lw[0]:[50,40], lw[1]:[5,0], ll[0]:[10,5]}
        await A.evaluate("""([d,l,P,Q])=>{ const mk=(O)=>{ const o={}; Object.keys(O).forEach(i=>{ o[i]={n:'x',so:O[i][0],rr:O[i][1]}; }); return o; };
          return Promise.all([FB.set('/hy/day/'+d, mk(P)), FB.set('/hy/day/'+l, mk(Q))]); }""", [today, lastDay, pts_now, lastpts])
        me=w[0]
        await A.evaluate("([i,n])=>{ Kid.set({id:i,n:n,t:'a'}); showRank('cup'); }", [me, KIDS[me]]); await A.wait_for_timeout(1500)
        r=await A.evaluate("()=>[...document.querySelectorAll('#rankList .cpT')].map(e=>[e.innerText.replace(/\\s+/g,' ').trim(), e.classList.contains('me')])")
        print(r)
        ok(len(r)==2 and r[0][1] and not r[1][1], "막대 2개 · 평균이 큰 내 팀이 먼저 · 내 팀 표시")
        ok("평균 25" in r[0][0] and "4명" in r[0][0] and ("평균 3" in r[1][0] or "평균 2" in r[1][0]), "1인 평균 = 총점 ÷ 팀 사람 수 (안 한 아이도 인원에 듦)")
        t=await A.evaluate("()=>document.getElementById('rankList').innerText")
        ok("내가 맞힌 문제 50" in t and "2팀 중 1등" in t, "내 기여 50 · 1등")
        ok("영웅" in t, "팀 영웅")
        ok(await A.evaluate("()=>!document.getElementById('rankList').innerHTML.includes('<b>x</b>')"), "이름 글자는 HTML 로 안 읽힘")
        ok("랜덤" not in t and "반 1인" not in t, "글에 '반 1인' 없음")
        await A.screenshot(path=OUT+"cup_a.png")
        # ② 지난주 우승 팀
        g0=await A.evaluate("()=>Wallet.gems()")
        await A.evaluate("([i,n])=>{ Kid.set({id:i,n:n}); }", [lw[0], KIDS[lw[0]]]); await A.evaluate("()=>showRank('easy')"); await A.evaluate("()=>showRank('cup')"); await A.wait_for_timeout(1500)
        g1=await A.evaluate("()=>Wallet.gems()"); tx=await A.evaluate("()=>document.getElementById('rankList').innerText")
        ok(g1-g0==10 and "지난주 우승" in tx, f"지난주 우승 팀 아이는 💎+10 {g0}→{g1}")
        await A.evaluate("()=>showRank('easy')"); await A.evaluate("()=>showRank('cup')"); await A.wait_for_timeout(1200)
        ok(await A.evaluate("()=>Wallet.gems()")==g1, "한 번만")
        await A.evaluate("([i,n])=>{ Kid.set({id:i,n:n}); }", [lw[2], KIDS[lw[2]]]); await A.evaluate("()=>showRank('easy')"); await A.evaluate("()=>showRank('cup')"); await A.wait_for_timeout(1200)
        ok(await A.evaluate("()=>Wallet.gems()")==g1, "지난주 1문제도 안 한 우승 팀 아이는 못 받음")
        await A.evaluate("([i,n])=>{ Kid.set({id:i,n:n}); }", [ll[0], KIDS[ll[0]]]); await A.evaluate("()=>showRank('easy')"); await A.evaluate("()=>showRank('cup')"); await A.wait_for_timeout(1200)
        ok(await A.evaluate("()=>Wallet.gems()")==g1, "진 팀은 못 받음")
        # ③ 응원 — 같은 팀만
        mates=[x for x in w if x!=me]
        await A.evaluate("([i,n])=>{ Kid.set({id:i,n:n}); localStorage.removeItem(Cup.dk(Kid.me())); }", [me, KIDS[me]]); await A.evaluate("()=>showRank('easy')"); await A.evaluate("()=>showRank('cup')"); await A.wait_for_timeout(1500)
        who=await A.evaluate("()=>[...document.querySelectorAll('.cpCh [data-cup=who]')].map(b=>b.dataset.k)")
        ok(sorted(who)==sorted(mates), f"같은 팀 친구만 {who}")
        to=mates[0]
        await A.evaluate("(t)=>document.querySelector('.cpCh [data-cup=who][data-k='+t+']').click()", to); await A.wait_for_timeout(200)
        em=await A.evaluate("()=>[...document.querySelectorAll('.cpCh [data-cup=emo]')].map(b=>b.textContent)")
        ok(em==["👏","👍","🔥","💪","🎉","⭐"], f"이모티콘 6개만 {em}")
        await A.evaluate("()=>document.querySelector('.cpCh [data-cup=emo]').click()"); await A.wait_for_timeout(700)
        d=await A.evaluate("(t)=>FB.get('/hy/cheer/'+t+'/'+HyBoss.dayOf(Date.now()))", to)
        v=list((d or {}).values())
        ok(len(v)==1 and v[0]["e"]=="👏" and v[0]["fid"]==me, f"서버에 응원 {v}")
        ok(await A.evaluate("(t)=>document.querySelector('.cpCh [data-cup=who][data-k='+t+']').disabled", to), "같은 친구에게 하루 한 번 (단추 잠김)")
        r2=await A.evaluate("(t)=>Cup.send(Kid.me(),t,'👍')", to); ok(r2=="limit", f"같은 친구 두 번째는 막힘 {r2}")
        r3=await A.evaluate("(t)=>Cup.send(Kid.me(),t,'💬')", mates[1]); ok(r3=="limit", f"정해진 이모티콘이 아니면 막힘 {r3}")
        await A.evaluate("()=>{ const c=Cup.today(Kid.me()); c.n=5; localStorage.setItem(Cup.dk(Kid.me()), JSON.stringify(c)); }")
        r4=await A.evaluate("(t)=>Cup.send(Kid.me(),t,'👍')", mates[1]); ok(r4=="limit", f"하루 5번 넘으면 막힘 {r4}")
        # 받는 아이
        await B.evaluate("([i,n])=>{ Kid.set({id:i,n:n}); }", [to, KIDS[to]]); await B.wait_for_timeout(300)
        await B.evaluate("()=>{ show('scStart'); Cup.badge(true); }"); await B.wait_for_timeout(900)
        ok(await B.evaluate("()=>document.getElementById('btnRankHome').classList.contains('cheerNew')"), "🏆 랭킹 단추에 새 응원 점")
        await B.evaluate("()=>showRank('cup')"); await B.wait_for_timeout(1500)
        tx=await B.evaluate("()=>document.querySelector('.cpCh').innerText")
        ok("👏" in tx and KIDS[me].split('<')[0] in tx, f"받은 응원에 보임 {tx[-40:]!r}")
        await B.wait_for_timeout(500)
        ok(await B.evaluate("()=>!document.getElementById('btnRankHome').classList.contains('cheerNew')"), "본 뒤엔 점이 사라짐")
        await B.screenshot(path=OUT+"cup_b.png")
        # ④ 이름 있는 아이가 4명 미만이면 안 열림
        await A.evaluate("()=>FB.set('/hy/roster/k', {k1:{n:'민준',t:'a'}, k2:{n:'서연',t:'a'}, k3:{n:'하준',t:'b'}})"); await A.evaluate("()=>HyBoss.refresh(true)"); await A.evaluate("()=>showRank('easy')"); await A.evaluate("()=>showRank('cup')"); await A.wait_for_timeout(1200)
        ok("4명 이상" in await A.evaluate("()=>document.getElementById('rankList').innerText"), "이름 있는 아이가 4명보다 적으면 열리지 않음")
        e=real_errs(errs); ok(not e, "오류 없음 "+str(e[:3]))
        await br.close()
    print("결과:", "통과" if not bad else "실패 "+str(bad))
asyncio.run(main())
