"""(v601) 사용자: 「랭킹 시스템 업데이트 · 딱 게임 들어갈 때 실시간 검색어처럼」 「이번 주 단어 모은 수 · 달리기 점수 1등 이런 게」 · 「마이타운 잠시 점검 중으로 닫아 두자」
   ① 첫 화면 🔥 실시간 줄: 📚 1위 → 📖 1위 → 🏃 1위 → 📚 2위 … 굴러감 · ▲▼ NEW
   ② 누르면 1~10위 (탭 셋 · 규칙 한 줄 · 내 줄 표시) · 🏆 전체 랭킹 → 📚 공부 점수 탭
   ③ 서버가 옛 버전(boards 없음)이면 줄을 숨김
   ④ 🛠 My Town (v601 점검 중 → v663 다시 엶): 점검 표시·안내 카드 없음 · house.html 바로 열어도 마을"""
import asyncio, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

BOARD={"ok":True,"v":10,"boards":{
  "study":[{"nick":"지후","tag":"0006","score":230,"n":12,"mv":1},{"nick":"민수","tag":"0007","score":200,"n":10,"mv":-1},{"nick":"새싹","tag":"0008","score":40,"n":2,"mv":"new"},{"nick":"라언","tag":"0009","score":30,"n":3,"mv":0}],
  "words":[{"nick":"선아","tag":"0010","score":42,"n":0,"mv":2},{"nick":"지후","tag":"0006","score":30,"n":0,"mv":"new"}],
  "run":[{"nick":"지환","tag":"0011","score":48952,"n":15,"mv":0}]},
  "me":{"study":{"nick":"루아","tag":"0006","score":32,"n":3,"mv":-2,"rank":12,"of":15,"lv":"G1-2","above":{"nick":"서원","score":40}},"run":{"nick":"루아","tag":"0006","score":50000,"n":20,"mv":1,"rank":1,"of":5,"lv":"G1-2","above":None}}}

async def main():
    bad=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(); errs=[]
        for (vw,vh,nm) in [(390,844,"phone"),(1180,820,"pad")]:
            pg=await br.new_page(viewport={"width":vw,"height":vh}); pg.on("pageerror", lambda e: errs.append(str(e)))
            calls=[]
            async def sheet(r):
                u=r.request.url; calls.append(u)
                if "board=1" in u: return await r.fulfill(status=200, body=json.dumps(BOARD), content_type="application/json")
                if "diff=study" in u: return await r.fulfill(status=200, body=json.dumps({"ok":True,"list":[{"nick":"지후","tag":"0006","score":230,"stage":12,"title":"","me":True}]}), content_type="application/json")
                return await r.fulfill(status=200, body='{"ok":true,"list":[]}', content_type="application/json")
            await pg.route("**/*", route); await pg.route("https://script.google.com/**", sheet)
            await pg.goto(ORIGIN+"index.html"); await pg.wait_for_timeout(300)
            await pg.evaluate("()=>{ localStorage.setItem('hyeng_tag','0006'); localStorage.removeItem('hyeng_board'); }")
            await pg.add_init_script("window.HY_TOWN_SHUT=true")   # 점검 중 그대로 시험
            await pg.reload(); await pg.wait_for_timeout(1200)
            await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); }")
            await pg.wait_for_timeout(1500)
            r=await pg.evaluate("()=>{ const b=document.getElementById('lrBar'); return [!!b && !b.hidden && b.offsetHeight>0, document.querySelector('#lrRoll .lrIt').innerText.replace(/\\s+/g,' '), LiveRank.it.map(x=>x[0][0]+(x[1]+1)).join(',')]; }")
            ok(r[0] and ("공부" in r[1] or "오늘의 30" in r[1]) and "지후" in r[1] and "▲1" in r[1] and r[2].startswith("s1,w1,r1,s0,r0,s2,w2,s3,s4,s0,r0"), f"① [{nm}] 🔥 실시간 줄: 📚 1위 지후 ▲1 · 순서 {r[2]} · '{r[1]}'")
            if nm=="phone":
                await pg.evaluate("()=>{ LiveRank.i=0; LiveRank.draw(); }"); await pg.wait_for_timeout(3300)
                r=await pg.evaluate("()=>document.querySelector('#lrRoll .lrIt').innerText.replace(/\\s+/g,' ')")
                ok("단어" in r and "선아" in r and "▲2" in r, f"① 다음 줄로 굴러감 → 📖 1위 선아 ▲2 '{r}'")
                await pg.screenshot(path=OUT+"rank601_start_phone.png")
                await pg.evaluate("()=>{ LiveRank.i=0; LiveRank.draw(); document.getElementById('lrBar').click(); }"); await pg.wait_for_timeout(300)
                r=await pg.evaluate("()=>{ const P=document.getElementById('lrPanel'); return [!!P, P.querySelectorAll('.lrRow').length, P.querySelector('.lrTabs .on').innerText, [...P.querySelectorAll('.lrMv')].map(x=>x.innerText).join(','), !!P.querySelector('.lrRow.me .meTag'), P.querySelector('.lrRule').innerText]; }")
                ok(r[0] and r[1]==5 and ("공부" in r[2] or "오늘의 30" in r[2]) and r[3]=="▲1,▼1,NEW,–,▼2" and r[4] and ("스테이지 점수" in r[5] or "점수" in r[5]), f"② 누르면 1~10위 · ▲▼NEW– · 내 줄(나) · 규칙 {r}")
                r=await pg.evaluate("()=>{ const P=document.getElementById('lrPanel'); const m=P.querySelector('.lrRow.me:last-of-type'); return [!!P.querySelector('.lrDots'), [...P.querySelectorAll('.lrRow.me')].map(x=>x.innerText.replace(/\\s+/g,' ')).join('|'), (P.querySelector('.lrLv')||{}).innerText||'']; }")
                ok(r[0] and "12" in r[1] and "서원까지 8점" in r[1] and "▼2" in r[1] and "G1-2" in r[2], f"(v602) 10위 밖이어도 ⋯ 아래 내 줄 (12위 · 서원까지 8점 · ▼2) · 내 단계 {r}")
                r=await pg.evaluate("()=>{ const i=LiveRank.it.findIndex(x=>x[1]<0); return LiveRank.rowH(LiveRank.it[i]).replace(/<[^>]+>/g,' ').replace(/\\s+/g,' '); }")
                ok("나" in r and "12위" in r and "밀렸어요" in r and "서원까지 8점" in r, f"(v602) 실시간 줄의 ⭐ 나: '{r}'")
                await pg.screenshot(path=OUT+"rank601_panel_phone.png")
                await pg.evaluate("()=>document.querySelector('#lrPanel [data-t=words]').click()"); await pg.wait_for_timeout(150)
                r=await pg.evaluate("()=>[...document.querySelectorAll('#lrPanel .lrRow')].map(x=>x.innerText.replace(/\\s+/g,' ')).join(' | ')")
                ok("선아" in r and "42단어" in r and "NEW" in r, f"② 📖 단어 탭 = 이번 주 모은 단어 '{r}'")
                await pg.evaluate("()=>document.querySelector('#lrPanel [data-t=run]').click()"); await pg.wait_for_timeout(150)
                r=await pg.evaluate("()=>document.querySelector('#lrPanel .lrRow').innerText.replace(/\\s+/g,' ')")
                ok("지환" in r and "48,952" in r, f"② 🏃 달리기 1등 '{r}'")
                await pg.evaluate("()=>{ document.querySelector('#lrPanel [data-t=study]').click(); document.querySelector('#lrPanel [data-all]').click(); }"); await pg.wait_for_timeout(800)
                r=await pg.evaluate("()=>[document.getElementById('scRank').classList.contains('on'), document.querySelector('#selRankDiff .sel').dataset.v, document.getElementById('rankList').innerText.replace(/\\s+/g,' ')]")
                ok(r[0] and r[1]=="study" and "지후" in r[2] and "230" in r[2] and "점" in r[2], f"② 🏆 전체 랭킹 → 📚 공부 점수 탭 {r}")
                await pg.screenshot(path=OUT+"rank601_rank_phone.png")
                # (v605) 「전체 랭킹도 수정해야」 — 탭 넷(공부·단어·달리기·팀 대항) · 이번 주 = 실시간 기록(▲▼·내 줄) · 달리기 전체 = 난이도 칩
                r=await pg.evaluate("()=>[[...document.querySelectorAll('#selRankDiff [data-v]')].map(x=>x.dataset.v).join(','), getComputedStyle(document.getElementById('btnNews')).display, document.getElementById('scStart').classList.contains('on'), document.getElementById('rankList').innerText.replace(/\\s+/g,' ')]")
                ok(r[0]=="study,dex,run,cup" and r[1]=="none" and not r[2] and "지후" in r[3] and "230" in r[3] and "서원까지 8점" in r[3], f"(v605 → v618 시상대: 1~3위는 ▲·판 수 대신 메달) 탭 넷 · 📰 안 겹침 · 공부 = ▲▼·판·내 줄(12위) {r}")
                await pg.evaluate("()=>document.querySelector('#selRankDiff [data-v=dex]').click()"); await pg.wait_for_timeout(300)
                r=await pg.evaluate("()=>document.getElementById('rankList').innerText.replace(/\\s+/g,' ')")
                ok("선아" in r and "42단어" in r.replace(" ","") and "새로 모은" in r, f"(v605) 📖 단어 이번 주 = 이번 주 모은 단어 · ▲▼ '{r[:120]}'")
                await pg.screenshot(path=OUT+"rank605_words_phone.png")
                await pg.evaluate("()=>document.querySelector('#selRankDiff [data-v=run]').click()"); await pg.wait_for_timeout(300)
                r=await pg.evaluate("()=>[document.getElementById('rankList').innerText.replace(/\\s+/g,' '), document.getElementById('selRankRun').style.display]")
                ok("지환" in r[0] and "48,952" in r[0] and r[1]=="none", f"(v605) 🏃 달리기 이번 주 = 난이도 상관없이 1등 · 난이도 칩 숨김 {r}")
                await pg.evaluate("()=>document.querySelector('#selRankRange [data-v=all]').click()"); await pg.wait_for_timeout(500)
                r=await pg.evaluate("()=>[document.getElementById('selRankRun').style.display, document.querySelector('#selRankRun .sel').dataset.v, RANK_VIEW.diff]")
                ok(r==["","normal","run"], f"(v605) 🏃 전체 = 난이도 칩(Normal) {r}")
                await pg.screenshot(path=OUT+"rank605_runall_phone.png")
                await pg.evaluate("()=>{ document.querySelector('#selRankRange [data-v=week]').click(); document.querySelector('#selRankDiff [data-v=study]').click(); }"); await pg.wait_for_timeout(200)
                await pg.evaluate("()=>document.getElementById('btnRankBack').click()")
                # ④ (v663) My Town 다시 엶 — 「이제 열자」
                await pg.evaluate("()=>document.getElementById('btnGo').click()"); await pg.wait_for_timeout(500)
                r=await pg.evaluate("()=>{ const t=document.querySelector('#selRule .c-town'); return [t.classList.contains('closed'), t.innerText.replace(/\\s+/g,' '), TOWN_OPEN, townOpen()]; }")
                ok(not r[0] and "점검" not in r[1] and "My Town" in r[1] and r[2] and r[3], f"④ My Town 칸 = 열림 (점검 표시 없음) {r}")
                await pg.screenshot(path=OUT+"rank601_town_phone.png")
                ne=len(errs); await pg.evaluate("()=>document.querySelector('#selRule .c-town').click()"); await pg.wait_for_timeout(1500)
                r=await pg.evaluate("()=>[!document.getElementById('townMt'), location.pathname]")
                ok(r[0] and r[1].endswith("/proto/house.html"), f"④ 누르면 점검 안내 없이 마을로 감 {r}")
                del errs[ne:]   # 마을 화면은 가짜 3D 엔진(fake_three)이라 그림 오류가 남 — 진짜 마을은 isle·town 시험이 봄
                await pg.goto(ORIGIN+"index.html"); await pg.wait_for_timeout(1500)
                # ③ 옛 서버
                await pg.evaluate("()=>{ LiveRank.it=[]; LiveRank.draw(); }")
                ok(await pg.evaluate("()=>document.getElementById('lrBar').hidden"), "③ 기록 없으면(옛 서버) 줄을 숨김")
            else:
                await pg.screenshot(path=OUT+"rank601_start_pad.png")
            await pg.close()
        # (v604) 「랭킹이 안 나왔는데」 — 서버가 늦으면 「불러오는 중」 줄 · 실패하면 다시 부름
        pg=await br.new_page(viewport={"width":390,"height":844}); pg.on("pageerror", lambda e: errs.append(str(e))); bc=[]
        async def slow(r):
            if "board=1" in r.request.url: bc.append(1); return await r.abort()
            return await r.fulfill(status=200, body='{"ok":true,"list":[]}', content_type="application/json")
        await pg.route("**/*", route); await pg.route("https://script.google.com/**", slow)
        await pg.goto(ORIGIN+"index.html"); await pg.wait_for_timeout(300)
        await pg.evaluate("()=>{ localStorage.removeItem('hyeng_board'); }"); await pg.reload(); await pg.wait_for_timeout(1500)
        await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); }")
        r=await pg.evaluate("()=>{ const b=document.getElementById('lrBar'); return [!b.hidden && b.offsetHeight>0, b.innerText.replace(/\\s+/g,' ')]; }")
        ok(r[0] and "불러오는 중" in r[1], f"(v604) 기록이 오기 전 = 「순위를 불러오는 중…」 줄 {r}")
        await pg.wait_for_timeout(9000)
        ok(len(bc)>=2, f"(v604) 못 받으면 8초 뒤 다시 부름 · {len(bc)}번")
        r=await pg.evaluate("()=>{ const b=document.getElementById('btnNews'); const q=b.getBoundingClientRect(); return [Math.round(q.width), Math.round(q.height)]; }")
        ok(r[0]<=40, f"(v604) 📰 소식지 단추 작게 {r}")
        await pg.close()
        # ④ house.html 바로 열기 (자동 시험 표시를 끔 → 실제 아이처럼) — (v663) 열렸으니 그대로 마을
        ctx=await br.new_context(viewport={"width":390,"height":844}); await ctx.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>false})")
        pg=await ctx.new_page(); await pg.route("**/*", route)
        await pg.goto(ORIGIN+"proto/house.html"); await pg.wait_for_timeout(2500)
        r=await pg.evaluate("()=>[location.pathname, !!document.getElementById('townMt')]")
        ok(r[0].endswith("/proto/house.html") and not r[1], f"④ house.html 을 바로 열면 → 마을 그대로 {r}")
        await br.close()
    ok(not real_errs(errs), f"오류 없음 {real_errs(errs)[:2]}")
    print("\nFAIL" if bad else "\nPASS", len(bad)); sys.exit(1 if bad else 0)

if __name__=="__main__": asyncio.run(main())
