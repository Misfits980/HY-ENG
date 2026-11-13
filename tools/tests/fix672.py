"""(v672) 사용자 크롬(Windows PC)으로 직접 점검하고 「일단 다 고치고 또 열어 보자」
   ① 「나는 누구?」 닫기가 안 됨 → 닫히고 공용 패드면 첫 화면
   ② 공용 패드에서 이름을 새로 고르면 Daily 30 지도가 앞 아이(패드) 진도 그대로 → 그 아이 것으로 다시 그림
   ③ 공용 패드 달리기 결과 기기 랭킹 = 패드 이름 → 고른 아이 이름
   ④ 공용 패드 설정 「태그 받는 중…」이 영원히 → 공용 패드 안내
   ⑤ 「이어서 하기」 = 아이별 · 게임 시작 고르는 화면도 마지막 난이도
   ⑥ 실시간 줄 = 점수만 · 좁으면 이름표 그림만 (잘림 없음)
   ⑦ 실시간 연결(EventSource) 4개까지 · 넘으면 읽기(poll) · 방 듣기가 오면 hy/… 를 읽기로 내림 · 닫으면 다시 올림
   ⑧ 랭킹·2인용 대결 왼쪽 위 ◀ 뒤로 · 0점 메달 없음 · 꺼진 보드 시작 단추 회색 · Adventure 카드 기록 칸이 설명을 안 덮음"""
import asyncio, sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

T = os.path.dirname(os.path.abspath(__file__)) + "/"
DATA = re.search(r'DATA = r"""(.*?)"""', open(T + "rank618.py", encoding="utf-8").read(), re.S).group(1)

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch()
        pg = await br.new_page(viewport={"width": 894, "height": 551}); pg.on("pageerror", lambda e: errs.append(str(e)))
        await boot(pg); E = pg.evaluate
        # 공용 패드 + 명단
        await E("""()=>{ localStorage.setItem('hyeng_nick','한양패드1'); HyBoss.R={k:{ka:{n:'민준',t:''}, kb:{n:'서연',t:''}}, t:{}}; HyBoss.kids=()=>HyBoss.R.k; HyBoss.teams=()=>({}); HyBoss.refresh=()=>Promise.resolve(); sessionStorage.removeItem('hyeng_kid'); return Kid.shared(); }""")
        # ① 닫기
        await E("()=>{ StudyUI.open(); KidPick.open(()=>{}); }"); await pg.wait_for_timeout(300)
        r = await E("()=>{ document.querySelector('#kidPick [data-kp=\"\"]').click(); return [!!document.getElementById('kidPick'), document.querySelector('[id^=sc].on').id]; }")
        ok(r == [False, "scStart"], f"① 「나는 누구?」 닫기 → 창 닫힘 · 첫 화면 {r}")
        # ② 패드 진도(G5-6) → 민준(새 아이) 고르면 지도가 민준 것
        await E("""()=>{ const s=Study.load(); s.book='g56'; Study.save(); StudyUI.open(); }"""); await pg.wait_for_timeout(300)
        b0 = await E("()=>(document.getElementById('stHead').innerText||'')+'|'+(document.querySelector('#stPath').innerText||'').slice(0,80)")
        await E("()=>{ KidPick.open(()=>{}); }"); await pg.wait_for_timeout(200)
        await E("()=>document.querySelector('#kidPick [data-kp=ka]').click()"); await pg.wait_for_timeout(500)
        r = await E("()=>[Kid.k('hyeng_study_v1'), Study.load().book, (document.getElementById('stHead').innerText||'')+'|'+(document.querySelector('#stPath').innerText||'').slice(0,80)]")
        ok(r[0].endswith("@ka") and r[1] != "g56" and "G5-6" in b0 and "G5-6" not in r[2], f"② 이름을 고르면 지도가 그 아이 것으로 (패드: {b0[:40]!r} → {r[2][:40]!r}) {r[:2]}")
        # ③ 달리기 기기 랭킹 이름
        r = await E("""()=>{ const sv=Ranking.save; let got=null; Ranking.save=o=>{ got=o.nick; return 1; }; try{ G.score=120; G.stage=2; G.right=3; G.wrong=1; G.diff='normal'; G.set='elem'; G.rule='normal'; G.testRun=false; G.practice=false; Online.submit=()=>Promise.resolve(null); Online.top=()=>Promise.resolve(null); gameOver(); }catch(e){ got='ERR '+e.message; } Ranking.save=sv; return got; }""")
        ok(r == "민준", f"③ 공용 패드 달리기 기기 랭킹 이름 = 고른 아이 {r}")
        await E("()=>show('scStart')")
        # ④ 태그 안내
        r = await E("()=>{ NameCard.draw && NameCard.draw(); const t=[...document.querySelectorAll('.nmTag')].map(e=>e.textContent).join('|'); return t; }")
        ok("받는 중" not in r, f"④ 공용 패드에 「태그 받는 중」 없음 {r[:60]}")
        # ⑤ 이어서 하기 = 아이별 · 고르는 화면 = 마지막 난이도
        r = await E("""()=>{ LastSetup.save({rule:'normal', diff:'hard', mode:'mix', set:'elem', char:'hero'}); const a=localStorage.getItem('hyeng_setup_v1@ka'); sessionStorage.setItem('hyeng_kid', JSON.stringify({id:'kb', n:'서연', at:Date.now()})); const b=LastSetup.get(); sessionStorage.setItem('hyeng_kid', JSON.stringify({id:'ka', n:'민준', at:Date.now()})); G.diff='normal'; return [!!a, b, LastSetup.get().diff]; }""")
        ok(r[0] and r[1] is None and r[2] == "hard", f"⑤ 이어서 하기 = 아이별 칸 {r}")
        await E("()=>{ Kid.confirm=(cb)=>cb(); document.getElementById('btnGo').click(); }"); await pg.wait_for_timeout(500)
        r = await E("()=>{ goStep(1); return [G.diff, document.querySelector('#selDiff [data-v].sel').dataset.v]; }")
        ok(r == ["hard", "hard"], f"⑤ 게임 시작 → 난이도 = 마지막 설정 {r}")
        await E("()=>show('scStart')")
        # ⑥ 실시간 줄
        await E(DATA); await pg.wait_for_timeout(1200)
        r = await E("""()=>{ clearTimeout(LiveRank._t); LiveRank.draw(); clearTimeout(LiveRank._t); const bar=document.getElementById('lrBar'), R=document.getElementById('lrRoll'), cut=[]; LiveRank.it.filter(x=>x[1]>=0).forEach(x=>{ R.innerHTML=LiveRank.rowH(x); const it=R.firstChild; ['.n','.v'].forEach(s=>{ const e=it.querySelector(s); if(e && e.scrollWidth>e.clientWidth+1 && !(s==='.n' && e.textContent.length>5)) cut.push(x[0]+':'+e.textContent); }); if(/판|문제/.test(it.querySelector('.v').textContent)) cut.push('long '+it.textContent); }); LiveRank.draw(); return [Math.round(bar.getBoundingClientRect().width), bar.classList.contains('nar'), cut]; }""")
        ok(not r[2] and (r[0] >= 400 or r[1]), f"⑥ 실시간 줄 = 점수만 · 잘림 없음 (폭 {r[0]} · 좁음 {r[1]}) {r[2][:4]}")
        # ⑦ 실시간 연결 4개까지 — 가짜 Firebase + 가짜 EventSource (열린 수만 셈)
        from fakefb import fake
        q = await br.new_page(viewport={"width": 894, "height": 551}); q.on("pageerror", lambda e: errs.append(str(e)))
        await q.add_init_script("window.EventSource=class{ constructor(u){ this.u=u; this.readyState=1; } addEventListener(){} close(){ this.readyState=2; } };")
        await q.route("**/*", fake); await q.goto(ORIGIN + "index.html"); await q.wait_for_timeout(1500)
        r = await q.evaluate("""async()=>{ const m=await FB.ready(); if(m!=="fb") return ['mode', m]; const base=FB.stat().n;
            const H=['/hy/x1','/hy/x2','/hy/x3','/hy/x4','/hy/x5'].map(p=>FB.listen(p, ()=>{})); await new Promise(r=>setTimeout(r,150)); const s1=FB.stat();
            const R=FB.listen('/battle/1234', ()=>{}); await new Promise(r=>setTimeout(r,150)); const s2=FB.stat();
            R.close(); H.slice(0,3).forEach(h=>h.close()); await new Promise(r=>setTimeout(r,300)); const s4=FB.stat(); H.forEach(h=>h.close());
            return [s1.es, s1.poll>=1, s2.es, s2.paths.indexOf('/battle/1234')>=0, s2.paths.some(p=>p==='~/battle/1234'), s4.es<=4, s4.poll, base]; }""")
        ok(r[0] == 4 and r[1] and r[2] == 4 and r[3] and not r[4] and r[5] and r[6] == 0, f"⑦ 실시간 연결 4개까지 · 넘으면 읽기 · 방 듣기는 실시간(hy 를 읽기로 내림) · 닫으면 다시 올림 {r}")
        await q.close()
        await pg.close()
        # ⑧ 화면
        pg = await br.new_page(viewport={"width": 894, "height": 551}); pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg); E = pg.evaluate
        r = await E("""()=>{ const an=document.getElementById('rkAnn'); if(an) an.remove(); show('scRank'); const b=document.querySelector('#scRank .topBack'), r=b.getBoundingClientRect(), top=document.elementFromPoint(r.left+r.width/2, r.top+r.height/2); b.click(); return [r.top>=0 && r.top<140 && (top===b || b.contains(top)), document.querySelector('[id^=sc].on').id]; }""")
        ok(r == [True, "scStart"], f"⑧ 랭킹 왼쪽 위 ◀ 뒤로 {r}")
        r = await E("""()=>{ show('scVs'); const b=document.querySelector('#scVs .topBack'), r=b.getBoundingClientRect(); return [r.top<80, b.dataset.tb]; }""")
        ok(r == [True, "vsBack"], f"⑧ 2인용 대결 왼쪽 위 ◀ 뒤로 {r}")
        await E("()=>show('scStart')")
        await E("()=>{ document.getElementById('btnGo').click(); }"); await pg.wait_for_timeout(500)
        r = await E("""()=>{ const c=document.querySelector('#selRule [data-v=normal]'), a=c.querySelector('small').getBoundingClientRect(), s=c.querySelector('.mStat').getBoundingClientRect(), cr=c.getBoundingClientRect(); return [Math.round(s.top-a.bottom), s.bottom<=cr.bottom+1, Math.round(cr.height)]; }""")
        ok(r[0] >= 0 and r[1] and r[2] >= 250, f"⑧ Adventure 카드: 기록 칸이 설명 아래 · 카드 안 · 가로 화면 카드 높이 {r}")
        r = await E("""()=>{ const b=document.createElement('button'); b.className='bdGo'; b.disabled=true; document.body.appendChild(b); const f=getComputedStyle(b).filter; b.remove(); return f; }""")
        ok("grayscale" in r, f"⑧ 꺼진 보드 시작 단추 = 회색 {r}")
        ok(not real_errs(errs), f"JS 오류 없음 {real_errs(errs)[:2]}")
        await br.close()
    print("DONE bad=%d" % len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
