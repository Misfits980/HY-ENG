"""(v687) 사용자: 「다 고쳐 주고 QA」 — v678 전체 QA 에서 찾은 것 (이름 창·4줄 팡·시험 판정은 다른 세션 v684 와 겹쳐 그쪽 것을 씀 → town684)
   ① 이름 없는 아이(v684 이름 창): 정하면 1.3초 뒤 My Town (이름 기록·태그가 끊기지 않게) · My Town 안 「네」 → #townname → 같은 창
   ② 선생님 화면: 서버가 오류(report)를 주면 30초 동안 저절로 다시 안 부름 (전엔 1초에 몇 번씩 끝없이)
   ③ 첫소리 문제: chinese → Chinese (밑줄 Ch)
   ④ 랭킹 이번 주: 서버 실패 → 「못 불러왔어요」 + 🔄 다시 불러오기 (전엔 「불러오는 중…」 영원히)
   ⑤ 첫 인사 「📚 첫 공부 시작」 → 첫 Stage 카드까지
   ⑥ My Town 코치 = 처음 본 단계가 1 (전엔 3 / 10)
   ⑦ 소식지 맨 위 = My Town · 잠금 창에 「이 기기에서」 · 폰 카드 설명 짧게
   ⑧ 친구랑 보드게임 방: 서버 연결이 안 되면 로비에 알림
   ⑨ Grade 1-2 문법 노트 머리글 = 「Grade 1-2 에서 만나는 문법」 (전엔 초3-4)
   ⑩ 패드 세로 미션 창 = 배율 (전엔 휴대폰 크기)
   ⑪ 달리기: 다음 문 단어 발음 파일을 미리 받음"""
import asyncio, sys, os
os.environ["HY_REAL3D"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

DAY = "Math.floor((Date.now()-new Date().getTimezoneOffset()*60000)/864e5)"

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        # ── ① 이름 없는 아이 (진짜 아이 기기처럼: webdriver 끔 · 잠금 켬)
        ctx = await br.new_context(viewport={"width": 820, "height": 1180}, has_touch=True)
        await ctx.add_init_script("Object.defineProperty(Navigator.prototype,'webdriver',{get:()=>false,configurable:true}); window.HY_TOWN_GATE=1; window.HY_TOWN_NAME=1; window.HY_FB_LOCAL=true;")
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); E = pg.evaluate
        await boot(pg, news=False); await pg.wait_for_timeout(600)
        await E("()=>{ ['helloMt','rkAnn'].forEach(i=>{ const d=document.getElementById(i); if(d) d.remove(); }); document.querySelectorAll('.sheet.on').forEach(s=>s.classList.remove('on')); localStorage.removeItem('hyeng_nick'); NameCard.draw(); Kid.confirm=(cb)=>cb(); document.getElementById('btnGo').click(); }")
        await pg.wait_for_timeout(600)
        r = await E("()=>document.querySelector('#selRule .c-town small').textContent")
        ok("3개" in r and len(r) <= 16, f"⑦ 잠긴 My Town 카드 설명이 짧음 (폰에서 안 잘리게) {r!r}")
        await E("()=>{ ['a','b','c'].forEach(k=>Study.townTick('t-'+k)); TownGate.card(); }")
        await E("()=>document.querySelector('#selRule .c-town').click()"); await pg.wait_for_timeout(600)
        r = await E("()=>{ const d=document.getElementById('townMt'); return d ? [d.innerText.replace(/\\s+/g,' ').slice(0,90), !!document.getElementById('twNm'), location.pathname] : null; }")
        ok(r and "이름" in r[0] and r[1] and r[2].endswith("index.html"), f"① 이름 없으면 카드 → 이름 정하기 창 (My Town 으로 안 감) {r}")
        await pg.screenshot(path=OUT + "fix687_name.png")
        await E("()=>{ document.getElementById('twNm').value='@@@'; document.querySelector('#townMt [data-ok]').click(); }"); await pg.wait_for_timeout(300)
        r = await E("()=>[document.getElementById('twNmMsg').textContent, !!document.getElementById('townMt'), localStorage.getItem('hyeng_nick')]")
        ok(r[0] and r[1] and not r[2], f"① 이상한 이름 → 안내 · 창 그대로 {r}")
        await E("()=>{ document.getElementById('twNm').value='루아'; document.querySelector('#townMt [data-ok]').click(); }")
        await pg.wait_for_timeout(500)
        r = await E("()=>location.pathname")
        ok(r.endswith("index.html"), f"① 정하자마자 바로 떠나지 않음 (이름 기록이 나갈 시간) {r}")
        try: await pg.wait_for_url("**/proto/house.html*", timeout=8000)
        except Exception: pass
        r = await E("()=>[location.pathname, localStorage.getItem('hyeng_nick'), localStorage.getItem('hyeng_town_ok')==String(" + DAY + ")]")
        ok(r[0].endswith("proto/house.html") and r[1] == "루아" and r[2], f"① 이름 정하기 → 바로 My Town (이름 저장 · 오늘 열림) {r}")
        # My Town 안 이름 창 단추 → index.html#townname
        for _ in range(60):
            if await E("()=>!!(window.HOUSE && HOUSE.place)"): break
            await pg.wait_for_timeout(500)
        r = None
        for _ in range(20):
            await pg.wait_for_timeout(500)
            r = await E("()=>{ const c=document.getElementById('coachN'); return c && c.offsetParent ? c.textContent : null; }")
            if r: break
        ok(r and r.startswith("1 / "), f"⑥ My Town 코치 = 처음 본 단계가 1 {r!r}")
        await E("()=>{ localStorage.removeItem('hyeng_nick'); try{ ISLE.enter && ISLE.enter(); }catch(e){} }"); await pg.wait_for_timeout(800)
        r = await E("()=>[document.getElementById('ask').classList.contains('on'), document.getElementById('askT').innerText.replace(/\\s+/g,' ').slice(0,60)]")
        ok(r[0] and "이름" in r[1], f"① My Town 안 이름 창 = 「지금 정할까요?」 {r}")
        await pg.screenshot(path=OUT + "fix687_house_gate.png")
        await E("()=>document.getElementById('askOk').click()")
        try: await pg.wait_for_url("**/index.html*", timeout=8000)
        except Exception: pass
        await pg.wait_for_timeout(2500)
        r = await E("()=>[location.pathname, location.hash, !!document.getElementById('twNm')]")
        ok(r[0].endswith("index.html") and r[1] == "" and r[2], f"① → 첫 화면 이름 정하기 창이 바로 뜸 {r}")
        await ctx.close()

        # ── ②~⑪ 보통 시험 기기
        ctx = await br.new_context(viewport={"width": 820, "height": 1180}, has_touch=True)
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); E = pg.evaluate
        await boot(pg, news=False); await pg.wait_for_timeout(600)
        # ⑦ 소식지 · 잠금 창
        r = await E("()=>[NEWS[0].id, NEWS[0].title, NEWS.find(n=>n.id==='2026-10-20a').title]")
        ok(r[0] == "2026-11-15a" and "My Town" in r[1] and "끝났" in r[2], f"⑦ 소식지 맨 위 = My Town · 빼빼로는 끝났다고 {r}")
        r = await E("()=>{ const f=TownGate.free; TownGate.free=()=>false; TownGate.show(); TownGate.free=f; const d=document.getElementById('townMt'); const t=d.innerText, b=d.querySelector('.tmB'); const z=[getComputedStyle(b).zoom, Math.round(b.getBoundingClientRect().width)]; d.remove(); return [t, z]; }")
        ok("학원 패드" in r[0], "⑦ 잠금 창에 어디서 한 것을 세는지 (v690: 같은 이름이면 학원 패드·집 기기 합쳐)")
        ok(float(r[1][0]) > 1.2 and r[1][1] > 520, f"(v688) 패드 세로 잠금 창 = 배율 (전엔 휴대폰 크기) {r[1]}")
        # ③ 첫소리 문제 고유명사
        await E("()=>{ const S=Study.load(); S.book='g12'; Study.save(); StudyUI.open(); StudyUI.start(0,false); }"); await pg.wait_for_timeout(800)
        r = await E("""()=>{ const q={t:"sfs", w:{en:"chinese", ko:"중국어"}, x:{on:"ch", em:{}}, opts:["chinese","cheese","sun","dog"], a:0, ans:0};
            StudyUI.qs.splice(StudyUI.i, 0, q); StudyUI.show(); const w=document.querySelector('#stLesson .wdW');
            return w ? [w.textContent, (w.querySelector('u')||{}).textContent||'', [...document.querySelectorAll('#stLesson .stOpt.sfs')].map(b=>b.textContent)] : null; }""")
        ok(r and r[0] == "Chinese" and r[1] == "Ch" and "Chinese" in r[2], f"③ 첫소리 문제: chinese → Chinese (밑줄 Ch) {r}")
        # ⑨ Grade 1-2 문법 노트
        await E("()=>{ StudyUI.close(); GramUI.note('g12'); }"); await pg.wait_for_timeout(1500)
        r = await E("()=>[...document.querySelectorAll('#stGram .glNH')].map(x=>x.textContent)")
        ok(r and r[0] == "Grade 1-2 에서 만나는 문법" and not any("초3-4" in x for x in r), f"⑨ Grade 1-2 문법 노트 머리글 {r}")
        r = await E("()=>{ StudyUI.close(); GramUI.note('g34'); return new Promise(ok=>setTimeout(()=>ok([...document.querySelectorAll('#stGram .glNH')].map(x=>x.textContent)), 1200)); }")
        ok(r and r[0] == "초3-4", f"⑨ Grade 3-4 는 그대로 「초3-4」 {r}")
        await E("()=>{ try{ StudyUI.close(); }catch(e){} show('scStart'); }"); await pg.wait_for_timeout(300)
        # ⑤ 첫 인사
        await E("()=>{ News.hello(); document.querySelector('#helloMt [data-d]').click(); }"); await pg.wait_for_timeout(1500)
        r = await E("()=>[document.getElementById('scStudy').classList.contains('on'), document.getElementById('stPop').classList.contains('on'), (document.getElementById('stPop').innerText||'').replace(/\\s+/g,' ').slice(0,160)]")
        ok(r[0] and r[1] and "배우기" in r[2], f"⑤ 「📚 첫 공부 시작」 → 첫 Stage 카드까지 {r}")
        await E("()=>{ StudyUI.pop(null); StudyUI.close(); }"); await pg.wait_for_timeout(300)
        # ⑩ 패드 세로 미션 창
        await E("()=>DM.view()"); await pg.wait_for_timeout(600)
        r = await E("()=>{ const el=document.querySelector('#dmView .dmIn'); return el ? [getComputedStyle(el).zoom, Math.round(el.getBoundingClientRect().width)] : null; }")
        ok(r and float(r[0]) > 1.2 and r[1] > 480, f"⑩ 패드 세로 미션 창 = 배율 {r}")
        await pg.screenshot(path=OUT + "fix687_mission.png")
        await E("()=>{ const d=document.getElementById('dmView'); if(d) d.remove(); }")
        # ④ 랭킹 이번 주 — 서버 실패
        await E("""()=>{ Online.on=()=>true; const of=window.fetch; window.fetch=function(u,o){ if(String(u).indexOf('board=1')>=0) return Promise.reject(new Error('net')); return of.apply(this, arguments); };
            LiveRank.B=null; LiveRank.it=[]; LiveRank._fail=2; LiveRank._busy=0; LiveRank.st='load'; RANK_VIEW.diff='study'; RANK_VIEW.range='week'; showRank('study'); }""")
        await pg.wait_for_timeout(1500)
        r = await E("()=>{ const b=document.getElementById('rankList'); return [b.innerText.replace(/\\s+/g,' ').slice(0,80), !!b.querySelector('[data-lr=retry]')]; }")
        ok("못 불러왔어요" in r[0] and r[1], f"④ 랭킹 이번 주: 서버 실패 → 안내 + 다시 불러오기 {r}")
        await pg.screenshot(path=OUT + "fix687_rank.png")
        await E("()=>{ try{ document.getElementById('btnRankBack').click(); }catch(e){} show('scStart'); }")
        # ⑧ 친구랑 보드게임 방 — 서버 연결 안 됨
        r = await E("""()=>{ const ofb=FB.mode; FB.mode=()=>'local'; window.HY_FB_LOCAL=false; window._fbm=ofb;
            BoardTV.host({kid:{id:'k1', n:'루아', c:'hero'}, set:Study.SETS[0], from:0, to:2, sk:'e', qt:'mix', rounds:10}); return !!document.getElementById('board'); }""")
        for _ in range(16):
            await pg.wait_for_timeout(500)
            if await E("()=>/\\d{4}/.test((document.getElementById('lbRoom')||{}).textContent||'')"): break
        await pg.wait_for_timeout(900)
        r = await E("()=>{ const n=document.getElementById('lbNet'); return n ? [!n.hidden, n.innerText.replace(/\\s+/g,' ')] : null; }")
        ok(r and r[0] and "못 들어와요" in r[1], f"⑧ 서버 연결 안 됨 → 로비에 알림 {r}")
        await pg.screenshot(path=OUT + "fix687_board.png")
        r = await E("()=>{ FB.mode=()=>'fb'; window.HY_FB_LOCAL=true; return new Promise(ok=>setTimeout(()=>ok(document.getElementById('lbNet').hidden), 900)); }")
        ok(r, "⑧ 연결되면 알림이 사라짐")
        await E("()=>{ FB.mode=window._fbm; try{ BoardTV.stop(); }catch(e){} const b=document.getElementById('board'); if(b) b.remove(); document.body.classList.remove('arOn'); }")
        # ⑪ 달리기: 다음 문 단어 발음 미리 받기
        await E("()=>{ window._pf=[]; const o=Voice.prefetch.bind(Voice); Voice.prefetch=function(l){ window._pf.push(...(l||[])); return o(l); }; Voice.on=true; RunVoice.on=()=>true; G.set='elem'; G.diff='normal'; G.rule='normal'; G.mode='e2k'; G.lesson=null; G.tag=null; G.dir='e2k'; startGame(); }")
        await pg.wait_for_timeout(6000)
        r = await E("()=>[window._pf.slice(0,4), G.nextQ && G.nextQ.word && G.nextQ.word.en]")
        ok(len(r[0]) >= 1, f"⑪ 달리기: 다음 문 단어 발음 미리 받기 {r}")
        await E("()=>{ G.quit=true; G.skipOutro=true; gameOver(); }"); await pg.wait_for_timeout(500)
        await ctx.close()

        # ── ② 선생님 화면: report 오류 → 30초 쉼
        ctx = await br.new_context(viewport={"width": 820, "height": 1180}, has_touch=True)
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); E = pg.evaluate
        await boot(pg, news=False)
        await E("()=>{ sessionStorage.setItem('hyeng_admin_ok', String(Date.now())); sessionStorage.setItem('hyeng_admin_tk', 'testkey'); }")
        await pg.reload(); await pg.wait_for_timeout(1500)
        await E("""()=>{ document.querySelectorAll('.sheet.on').forEach(s=>s.classList.remove('on')); localStorage.removeItem('hyeng_admin_rep'); Online.on=()=>true; window._sub=[];
            Online.submit=o=>{ window._sub.push(o.type); return new Promise(res=>setTimeout(()=>res(o.type==='check' ? {ok:true} : o.type==='tags' ? {ok:false, err:'busy'} : o.type==='report' ? {ok:false, err:'busy'} : {ok:true}), 150)); };
            Notice.fetch=()=>Promise.resolve({v:3, notices:[]}); Admin.open(); }""")
        await pg.wait_for_timeout(1200)
        await E("()=>{ const b=[...document.querySelectorAll('#shAdmin .adTabs button')].find(b=>/아이들/.test(b.textContent)); b.click(); }")
        await pg.wait_for_timeout(5000)
        r = await E("()=>[window._sub.filter(t=>t==='report').length, window._sub.filter(t=>t==='tags').length, window._sub.length]")
        ok(r[0] <= 2 and r[1] <= 2, f"② 서버 오류 → 저절로 끝없이 다시 안 부름 (5초에 report {r[0]}번 · tags {r[1]}번) {r}")
        await E("()=>[...document.querySelectorAll('#shAdmin .adTabs button')].find(b=>/기록/.test(b.textContent)).click()"); await pg.wait_for_timeout(800)
        await E("()=>{ window._sub=window._sub.filter(x=>x!=='report'); }")
        r = [await E("()=>window._sub.filter(t=>t==='report').length")]
        await E("()=>{ const b=document.querySelector('[data-ad=repLoad]'); if(b) b.click(); }"); await pg.wait_for_timeout(600)
        r2 = await E("()=>window._sub.filter(t=>t==='report').length")
        ok(r2 == r[0] + 1, f"② 🔄 단추는 바로 다시 부름 {r[0]} → {r2}")
        await ctx.close(); await br.close()
    real = real_errs(errs)
    ok(not real, f"스크립트 오류 없음 {real[:4]}")
    print("FAIL" if bad else "PASS", len(bad)); sys.exit(1 if bad else 0)

asyncio.run(main())
