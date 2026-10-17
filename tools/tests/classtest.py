"""(v306) 관리 화면 📋 우리 반 — 서버(Code.gs v3 report)를 흉내 내서: 출석표·오늘·확인 필요·약한 단어·학부모 문자 · 약한 단어 → 배틀 칸 · 옛 서버(v2)면 바꾸는 안내 · 탭 한 줄"""
import asyncio, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright
REP={"head":"2026-10-16 (금)  ·  오늘 공부한 아이 11명  ·  달리기 한 아이 3명",
 "check":[["종류","아이","내용","할 일"],["😴 안 들어옴","박유범","마지막 10/12 (4일 전)","연락해 보기"],["📱 옛 버전 15대","스트로베리, 김지환","v224 ~ v302 (최신 v304)","앱을 완전히 껐다 켜기"]],
 "weekOf":"2026-10-12 (월)",
 "week":[["아이","월 10/12","화 10/13","수 10/14","목 10/15","금 10/16","토 10/17","일 10/18","평일 들어옴","빠진 평일","끝낸 공부 판","공부(분)","정답률(%)","★2 확인 통과","주간 시험","자주 틀린 단어","상태","구분"],
   ["김지후","🔸 5","❌","✅ 6","✅ 6","✅ 23","","","4 / 5","1","35","87","95","1","","into","⚠️ 평일 1일 빠짐","개인"],
   ["박유범","🔸 1","❌","❌","❌","❌","","","1 / 5","4","0","0","-","0","","","⚠️ 평일 4일 빠짐","개인"],
   ["스트로베리","🔸 10","✅ 5","🔸 5","✅ 6","🔸 2","⭐ 1","","5 / 5","0","11","36","97","0","","president","🔸 목표 못 채운 날 있음","개인"]],
 "today":[["아이","한 횟수","끝까지 한 횟수","푼 문제","정답률(%)","공부(분)","마지막","한 Stage"],["김지후","23","23","562","94","43.0","22:09","18개"],["김지환","9","4","207","94","10.4","21:32","5개"]],
 "weekly":[["아이","들어온 날","오늘의 30","끝까지","공부(분)","정답률(%)","달리기 판","달리기 최고","짧은 판","새 도감","자주 틀린 단어","지난주보다 (공부)","학부모 문자"],
   ["김지후","4","37","35","87.2","95","8","6,616","0","6","into","+37","김지후 학생은 이번 주 4일 들어왔어요. 오늘의 30을 37번 했어요."]],
 "miss":[["단어","틀린 횟수","틀린 아이"],["home","5","3"],["gate","5","3"],["smile","5","3"],["fan","4","3"],["trouble","4","3"]],
 "lesson":[["아직 수업 기록이 없어요"]],
 "prog":[["아이","🧸 유치원","🍎 G1-2","🎒 G3-4","🧭 G5-6","🧭 G5-6 리딩","🏫 중등","마지막 공부"],["김지후","","","","Stage 3-1 ★3 · 13개 · 10/16","","","10/16 22:09"]]}
async def main():
    bad=[]; errs=[]
    async with async_playwright() as p:
        br=await p.chromium.launch()
        for W,H,name in [(390,844,"phone"),(1366,900,"tv")]:
            ctx=await br.new_context(viewport={"width":W,"height":H}); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
            pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)
            await pg.evaluate("()=>{ sessionStorage.setItem('hyeng_admin_ok',String(Date.now())); sessionStorage.setItem('hyeng_admin_tk','testkey'); }")
            await pg.reload(); await pg.wait_for_timeout(1200)
            await pg.evaluate("(R)=>{ window._srvV=3; Online.on=()=>true; Notice.fetch=()=>Promise.resolve({v:window._srvV, notices:[]}); Online.submit=o=>Promise.resolve(o.type==='report' ? (window._srvV>=3?{ok:true, rep:R}:{ok:false, err:'type'}) : {ok:true}); document.querySelectorAll('.sheet.on').forEach(s=>s.classList.remove('on')); Admin.open(); }", REP)
            await pg.wait_for_timeout(800)
            txt=await pg.evaluate("()=>document.getElementById('adBody').innerText")
            for want in ["이번 주 출석","오늘 공부한 아이 2명","확인 필요 2건","home","학부모 문자"]:
                if want not in txt: bad.append(f"{name} 우리 반에 '{want}' 없음")
            tabs=await pg.evaluate("()=>{ const t=document.getElementById('adTabs'), b=[...t.querySelectorAll('button')]; return [b.length, new Set(b.map(x=>Math.round(x.getBoundingClientRect().top))).size, document.documentElement.scrollWidth<=innerWidth]; }")
            print(name, "tabs", tabs)
            if tabs[0]!=8 or tabs[1]!=1: bad.append(f"{name} 탭이 한 줄이 아님 {tabs}")
            await pg.screenshot(path=OUT+f"class_{name}.png", full_page=False)
            if name=="phone":
                await pg.click("[data-ad=weakBt]"); await pg.wait_for_timeout(400)
                v=await pg.evaluate("()=>[(document.getElementById('adBtWords')||{}).value, document.querySelector('#adTabs .on').dataset.t]"); print("weakBt", v)
                if v[1]!="raid" or "home" not in (v[0] or ""): bad.append(f"약한 단어 → 배틀 칸 {v}")
                await pg.screenshot(path=OUT+"class_raidtab.png")
                await pg.click("[data-ad=btGo]"); await pg.wait_for_timeout(900)   # (v308) 배틀 방 만들기 버튼이 정말 방을 여는지
                bt=await pg.evaluate("()=>[Battle.role, Battle.room, (Battle.cfg().words||[]).length]"); print("btGo", bt)
                if bt[0]!="host" or not bt[1] or bt[2]<3: bad.append(f"배틀 방 만들기 버튼 {bt}")
                # (v322) 📺 TV 새로고침 → 관리 ⚔️ 탭 「방 다시 열기」 → 같은 방 (새로 쓰지 않음)
                await pg.reload(); await pg.wait_for_timeout(1000)
                await pg.evaluate("(R)=>{ Online.on=()=>true; Notice.fetch=()=>Promise.resolve({v:3, notices:[]}); Online.submit=o=>Promise.resolve(o.type==='report' ? {ok:true, rep:R} : {ok:true}); document.querySelectorAll('.sheet.on').forEach(s=>s.classList.remove('on')); Admin.open(); }", REP)
                await pg.wait_for_timeout(500); await pg.click('#adTabs [data-t="raid"]'); await pg.wait_for_timeout(400)
                has=await pg.evaluate("()=>!!document.querySelector('[data-ad=tvBack]')")
                if not has: bad.append("📺 방 다시 열기 버튼 없음")
                else:
                    await pg.click("[data-ad=tvBack]"); await pg.wait_for_timeout(700)
                    bt2=await pg.evaluate("()=>[Battle.role, Battle.room, (Battle.cfg().words||[]).length]"); print("tvBack", bt2)
                    if bt2!=bt: bad.append(f"📺 다시 열기 {bt2} != {bt}")
                await pg.evaluate("()=>Battle.leave()"); await pg.wait_for_timeout(300)
                if await pg.evaluate("()=>!!TvRoom.get()"): bad.append("TV 를 닫았는데 다시 열기가 남음")
                # (v322) 방패 단어 — 쉼표로만 나눔 ('put on' 그대로) · 없는 단어는 알려 줌
                await pg.evaluate("()=>{ document.querySelectorAll('.sheet.on').forEach(s=>s.classList.remove('on')); Admin.open(); }"); await pg.wait_for_timeout(400)
                await pg.click('#adTabs [data-t="raid"]'); await pg.wait_for_timeout(300)
                await pg.evaluate("()=>{ document.getElementById('adRdWords').value='put on, zzqx, home'; }")
                await pg.click("[data-ad=raidGo]"); await pg.wait_for_timeout(900)
                rd=await pg.evaluate("()=>[Raid.role, ((RaidNet.get().sh||{}).w)||[], (document.getElementById('hyToast')||{}).textContent||'', !!Study.word('put on')]"); print("raidGo", rd)
                want=(["put on"] if rd[3] else [])+["home"]
                if rd[0]!="host" or rd[1]!=want or "zzqx" not in rd[2]: bad.append(f"방패 단어 칸 {rd}")
                await pg.evaluate("()=>Raid.leave()"); await pg.wait_for_timeout(300)
                # 옛 서버 (v2) — 처음부터
                await pg.reload(); await pg.wait_for_timeout(1000)
                await pg.evaluate("(R)=>{ window._srvV=2; Online.on=()=>true; Notice.fetch=()=>Promise.resolve({v:2, notices:[]}); Online.submit=o=>Promise.resolve(o.type==='report' ? {ok:false, err:'type'} : {ok:true}); localStorage.removeItem('hyeng_admin_rep'); document.querySelectorAll('.sheet.on').forEach(s=>s.classList.remove('on')); Admin.open(); }", REP)
                await pg.wait_for_timeout(500); await pg.click('#adTabs [data-t="class"]'); await pg.wait_for_timeout(700)
                t2=await pg.evaluate("()=>document.getElementById('adBody').innerText"); print("old", t2[:80].replace("\n"," / "))
                if "Code.gs" not in t2: bad.append("옛 서버 안내 없음")
                await pg.screenshot(path=OUT+"class_old.png")
            await ctx.close()
        print("errs", errs[:5]); await br.close()
    e=real_errs(errs)
    print("결과:", "통과 ✅" if not bad and not e else "실패 ❌"); [print(" BAD", b) for b in bad]
    if bad or e: sys.exit(1)
asyncio.run(main())
