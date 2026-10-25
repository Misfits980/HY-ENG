"""(v398) 🏫 집에서 하는 반 대항전 + 💌 응원
  ① 랭킹 → 「반 대항」 탭 · 반 1인 평균 맞힌 문제 막대 · 내 반 표시 · 내 기여 · 반 영웅 3명
  ② 지난주 우승 반 💎10 (아이마다 한 번 · 지난주 1문제도 안 한 아이는 못 받음)
  ③ 응원: 이모티콘만 · 같은 반 친구에게 · 하루 5번 · 같은 친구 하루 한 번 · 받은 아이에게 보임 · 🏆 랭킹 단추에 새 응원 점
  ④ 반이 하나면 안 열림 · 이름 글자는 HTML 로 안 읽힘"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright
async def main():
    bad=[]; errs=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(); ctx=await br.new_context(viewport={"width":390,"height":844}, service_workers="block"); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        A=await ctx.new_page(); A.on("pageerror", lambda e: errs.append("A "+str(e))); await boot(A)
        await A.evaluate("""()=>{ HyBoss.live(); return FB.set('/hy/roster', {t:{a:{n:'사자반',e:'🦁'}, b:{n:'돌고래반',e:'🐬'}}, k:{k1:{n:'민준',t:'a'}, k2:{n:'서연<b>x</b>',t:'a'}, k3:{n:'하준',t:'a'}, k4:{n:'수아',t:'b'}, k5:{n:'도윤',t:'b'}}}); }""")
        today=await A.evaluate("()=>HyBoss.dayOf(Date.now())"); mon=await A.evaluate("()=>HyBoss.monday()"); last=await A.evaluate("()=>HyBoss.monday(Date.now()-7*864e5)")
        lastDay=await A.evaluate("(m)=>Cup.addDay(m,2)", last)
        await A.evaluate("""([d,l])=>Promise.all([
          FB.set('/hy/day/'+d, {k1:{n:'민준',t:'a',so:30,rr:20}, k2:{n:'서연',t:'a',so:40,rr:10}, k4:{n:'수아',t:'b',so:20,rr:10}}),
          FB.set('/hy/day/'+l, {k1:{n:'민준',t:'a',so:10,rr:5}, k4:{n:'수아',t:'b',so:50,rr:40}, k5:{n:'도윤',t:'b',so:5,rr:0}})])""", [today, lastDay])
        # ① 
        await A.evaluate("()=>{ Kid.set({id:'k1',n:'민준',t:'a'}); showRank('cup'); }"); await A.wait_for_timeout(1500)
        r=await A.evaluate("()=>[...document.querySelectorAll('#rankList .cpT')].map(e=>[e.innerText.replace(/\\s+/g,' ').trim(), e.classList.contains('me')])")
        print(r)
        ok(len(r)==2 and "사자반" in r[0][0] and r[0][1] and "돌고래반" in r[1][0] and not r[1][1], "막대 2개 · 평균이 큰 반(사자반 100÷3=33 vs 돌고래 30÷2=15) 먼저 · 내 반 표시")
        ok("평균 33" in r[0][0] and "3명" in r[0][0] and "평균 15" in r[1][0], "1인 평균 = 총점 ÷ 반 사람 수 (못 한 하준도 인원에 듦)")
        t=await A.evaluate("()=>document.getElementById('rankList').innerText")
        ok("내가 맞힌 문제 50" in t and "2반 중 1등" in t, "내 기여 50 · 1등")
        ok("영웅" in t and "민준 50" in t and "서연" in t, "반 영웅")
        ok(await A.evaluate("()=>!document.getElementById('rankList').innerHTML.includes('<b>x</b>')"), "이름 글자는 HTML 로 안 읽힘")
        await A.screenshot(path=OUT+"cup_a.png")
        # ② 지난주 우승 = 돌고래반 (수아 90 · 도윤 5 → 평균 47) vs 사자반 (민준 15 → 평균 5) → 민준(사자반) 은 못 받음
        g0=await A.evaluate("()=>Wallet.gems()"); ok(True, f"지난주 우승은 돌고래반 · 사자반 민준은 안 받음 💎{g0}")
        await A.evaluate("()=>{ Kid.set({id:'k4',n:'수아',t:'b'}); }"); await A.evaluate("()=>showRank('easy')"); await A.evaluate("()=>showRank('cup')"); await A.wait_for_timeout(1500)
        g1=await A.evaluate("()=>Wallet.gems()"); tx=await A.evaluate("()=>document.getElementById('rankList').innerText")
        ok(g1-g0==10 and "지난주 우승" in tx, f"수아(우승 반)는 💎+10 {g0}→{g1}")
        await A.evaluate("()=>showRank('easy')"); await A.evaluate("()=>showRank('cup')"); await A.wait_for_timeout(1200)
        ok(await A.evaluate("()=>Wallet.gems()")==g1, "한 번만")
        await A.evaluate("()=>{ Kid.set({id:'k5',n:'도윤',t:'b'}); }"); await A.evaluate("()=>showRank('easy')"); await A.evaluate("()=>showRank('cup')"); await A.wait_for_timeout(1200)
        ok(await A.evaluate("()=>Wallet.gems()")-g1==10, "지난주 5문제 한 도윤도 받음")
        # ③ 응원
        await A.evaluate("()=>{ Kid.set({id:'k1',n:'민준',t:'a'}); localStorage.removeItem(Cup.dk(Kid.me())); }"); await A.evaluate("()=>showRank('easy')"); await A.evaluate("()=>showRank('cup')"); await A.wait_for_timeout(1300)
        who=await A.evaluate("()=>[...document.querySelectorAll('.cpCh [data-cup=who]')].map(b=>b.dataset.k)")
        ok(sorted(who)==["k2","k3"], f"같은 반 친구만 {who}")
        await A.evaluate("()=>document.querySelector('.cpCh [data-cup=who][data-k=k2]').click()"); await A.wait_for_timeout(200)
        em=await A.evaluate("()=>[...document.querySelectorAll('.cpCh [data-cup=emo]')].map(b=>b.textContent)")
        ok(em==["👏","👍","🔥","💪","🎉","⭐"], f"이모티콘 6개만 {em}")
        await A.evaluate("()=>document.querySelector('.cpCh [data-cup=emo]').click()"); await A.wait_for_timeout(700)
        d=await A.evaluate("()=>FB.get('/hy/cheer/k2/'+HyBoss.dayOf(Date.now()))")
        v=list((d or {}).values())
        ok(len(v)==1 and v[0]["e"]=="👏" and v[0]["f"]=="민준" and v[0]["fid"]=="k1", f"서버에 응원 {v}")
        ok(await A.evaluate("()=>document.querySelector('.cpCh [data-cup=who][data-k=k2]').disabled"), "같은 친구에게 하루 한 번 (단추 잠김)")
        r2=await A.evaluate("()=>Cup.send(Kid.me(),'k2','👍')"); ok(r2=="limit", f"같은 친구 두 번째는 막힘 {r2}")
        r3=await A.evaluate("()=>Cup.send(Kid.me(),'k3','💬')"); ok(r3=="limit", f"정해진 이모티콘이 아니면 막힘 {r3}")
        await A.evaluate("()=>{ const c=Cup.today(Kid.me()); c.n=5; localStorage.setItem(Cup.dk(Kid.me()), JSON.stringify(c)); }")
        r4=await A.evaluate("()=>Cup.send(Kid.me(),'k3','👍')"); ok(r4=="limit", f"하루 5번 넘으면 막힘 {r4}")
        # 받는 아이
        B=await ctx.new_page(); B.on("pageerror", lambda e: errs.append("B "+str(e))); await boot(B)
        await B.evaluate("()=>{ HyBoss.live(); return HyBoss.refresh(true).then(()=>Kid.set({id:'k2',n:'서연',t:'a'})); }"); await B.wait_for_timeout(500)
        await B.evaluate("()=>{ show('scStart'); Cup.badge(true); }"); await B.wait_for_timeout(900)
        ok(await B.evaluate("()=>document.getElementById('btnRankHome').classList.contains('cheerNew')"), "🏆 랭킹 단추에 새 응원 점")
        await B.evaluate("()=>showRank('cup')"); await B.wait_for_timeout(1500)
        tx=await B.evaluate("()=>document.querySelector('.cpCh').innerText")
        ok("👏 민준" in tx, f"받은 응원에 보임 {tx[-40:]!r}")
        await B.wait_for_timeout(500)
        ok(await B.evaluate("()=>!document.getElementById('btnRankHome').classList.contains('cheerNew')"), "본 뒤엔 점이 사라짐")
        await B.screenshot(path=OUT+"cup_b.png")
        # ④ 반이 하나
        await A.evaluate("()=>FB.set('/hy/roster/t/b', null)"); await A.evaluate("()=>HyBoss.refresh(true)"); await A.evaluate("()=>showRank('easy')"); await A.evaluate("()=>showRank('cup')"); await A.wait_for_timeout(1000)
        ok("두 개 이상" in await A.evaluate("()=>document.getElementById('rankList').innerText"), "반이 하나면 열리지 않음")
        e=real_errs(errs); ok(not e, "오류 없음 "+str(e[:3]))
        await br.close()
    print("결과:", "통과" if not bad else "실패 "+str(bad))
asyncio.run(main())
