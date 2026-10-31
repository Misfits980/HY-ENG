"""(v474) 사용자: "문제 2(철자) 모를 때 「모르겠어요」 하고 답 보여 주고 다시 푸는 형태 · 대신 모른다 하면 맨 마지막으로 문제를 보내서 풀게" · "애들이 데일리는 몇 시에 · 달리기는 몇 시에 · 마이타운은 몇 시에 했는지" · "관리자 창 정리"
  ① 철자 문제에 🤔 모르겠어요 → 칸에 답이 채워짐 · 「맨 마지막에 다시」 · 같은 문제가 판 맨 끝에 (글자 다시 섞음)
  ② 계속 → 다음 문제로 (모르겠어요는 하트·'틀림' 숫자에 안 셈 · 복습 칸에는 틀림) · 맨 끝에서 맞히면 끝
  ③ 시험(test)·확인 문제에는 모르겠어요 없음 · 같은 문제 두 번째 모르겠어요까지만
  ④ ⏰ HyDay.add 가 시간 칸(tl)도 씀 · 같은 이름 두 줄 합칠 때 tl 도 합침 · 시간표 카드: 아이마다 막대 + 「📚 16:05~16:20」
  ⑤ 관리자 탭 5개: 🏫 수업 · 👥 아이들 · ⏰ 언제 했나 · 📝 숙제·시험 · 📢 보내기 · 수업 탭엔 💬·📅·바로가기 줄 없음 · 아이들 탭에 📅·💬"""
import asyncio, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "FAIL ") + m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch()
        pg = await br.new_page(viewport={"width": 820, "height": 1180}); pg.on("pageerror", lambda e: errs.append(str(e)))
        await boot(pg)
        E = pg.evaluate
        await E("()=>{ const s=Study.load(); s.book='g34'; s.set='elem'; Study.save(); StudyUI.open(); }"); await pg.wait_for_timeout(700)
        await E("()=>{ StudyUI.start(0,false); }"); await pg.wait_for_timeout(400)
        # 지금 문제 자리에 철자 문제를 넣음
        r = await E("""()=>{ const U=StudyUI; let k=U.i; while(U.qs[k] && U.qs[k].t==='intro') k++; U.i=k; const q0=U.qs[k], w=q0.w;
            const q={t:'spell', w, tiles:shuffle(w.en.split('')), got:'', used:[], step:2}; U.qs.splice(k, 0, q); U.locked=false; U.show(); return [w.en, U.qs.length, k]; }""")
        en, n0, k0 = r
        await pg.wait_for_timeout(300)
        r = await E("()=>[!!document.getElementById('stIdk'), document.getElementById('stIdk') && document.getElementById('stIdk').innerText]")
        ok(r[0] and "힌트" in r[1], f"① (v481) 철자 문제에 💡 힌트 → 🤔 모르겠어요 단추 {r}")
        await E("()=>{ for(let k=0;k<4;k++){ const b=document.getElementById('stIdk'); if(!b) return; const last=/모르겠어요/.test(b.innerText); b.click(); if(last) return; } }"); await pg.wait_for_timeout(300)
        r = await E("""(en)=>{ const U=StudyUI, last=U.qs[U.qs.length-1]; return [document.getElementById('stSlots').innerText.replace(/\\s+/g,''), document.getElementById('stFoot').innerText, U.qs.length, last.t, last.w.en, last.idk, last.again, last.got, U.locked, U.wrong, U.missed[en]===1]; }""", en)
        ok(r[0] == en.replace(" ", "") and "맨 마지막" in r[1] and r[2] == n0 + 1 and r[3] == "spell" and r[4] == en and r[5] == 1 and r[6] and r[7] == "" and r[8] and r[9] == 0 and r[10],
           f"① 답이 칸에 · 「맨 마지막에 다시」 · 판 맨 끝에 같은 문제(idk 1) · 틀림 숫자 0 · 복습엔 틀림 {r}")
        await E("()=>document.getElementById('stCheck').click()"); await pg.wait_for_timeout(300)
        r = await E("()=>[StudyUI.i, StudyUI.locked]")
        ok(r[0] == k0 + 1 and r[1] is False, f"② 「알겠어요」 → 다음 문제 {r}")
        # 맨 끝까지 정답으로
        for _ in range(160):
            st = await E("()=>{ const U=StudyUI; return [U.i, U.qs.length, document.getElementById('stLesson').style.display]; }")
            if st[0] >= st[1] - 1: break
            await E(SOLVE, False); await pg.wait_for_timeout(120)
        r = await E("()=>{ const U=StudyUI, q=U.qs[U.i]; return [U.i, U.qs.length, q && q.t, q && q.w.en, q && q.idk, !!document.getElementById('stIdk')]; }")
        ok(r[0] == r[1] - 1 and r[2] == "spell" and r[3] == en and r[4] == 1 and r[5], f"② 맨 끝 문제 = 모르겠어요 한 철자 문제 (한 번 더 모르겠어요 가능) {r}")
        await E("()=>{ for(let k=0;k<4;k++){ const b=document.getElementById('stIdk'); if(!b) return; const last=/모르겠어요/.test(b.innerText); b.click(); if(last) return; } }"); await pg.wait_for_timeout(250)
        r = await E("()=>{ const U=StudyUI, last=U.qs[U.qs.length-1]; return [last.idk, U.qs.length]; }")
        await E("()=>document.getElementById('stCheck').click()"); await pg.wait_for_timeout(250)
        r2 = await E("()=>{ const U=StudyUI, q=U.qs[U.i]; return [q && q.idk, !!document.getElementById('stIdk')]; }")
        ok(r[0] == 2 and r2 == [2, False], f"③ 두 번째 모르겠어요 → 또 맨 끝 · 세 번째엔 단추 없음 (끝없이 미루기 막기) {r} {r2}")
        r = await E("""()=>{ const U=StudyUI, q=U.qs[U.i]; const o={test:U.test, oly:U.oly}; U.test=true; const a=U.idkOK(q); U.test=o.test; const c=U.idkOK(Object.assign({}, q, {idk:0, chk:1})), d=U.idkOK(Object.assign({}, q, {idk:0})), e=U.idkOK(Object.assign({}, q, {idk:0, t:'e2k'})); return [a, c, d, e]; }""")
        ok(r == [False, False, True, False], f"③ 시험·확인 문제·고르기 문제엔 없음 · 철자엔 있음 {r}")
        # ④ 시간 기록
        r = await E("""async ()=>{ const day=HyDay.key(); const a0=Date.now()-15*60000; HyDay.add({s:1, so:5, sw:1}, null, {id:'k1', n:'김지후', t:'all'}, a0); HyDay.add({r:1, rr:3, rw:0, rs:120}, {b:100, bs:2}, {id:'d123', n:'김지후', t:'all'}, Date.now()-3*60000);
            await new Promise(r=>setTimeout(r,300)); await HyDay.load(day); const D=HyDay.D[day]; const L=HyDay.merge(D); const g=L.find(x=>x.n==='김지후'); const sp=HyDay.spans(g);
            HyDay.day=day; const h=HyDay.timeCard(); return [L.length, Object.keys(g.tl||{}).length, sp.map(s=>s.k), Math.round((sp[0].b-sp[0].a)/60000), (h.match(/class="whS"/g)||[]).length, h.indexOf('📚 ')>=0 && h.indexOf('🏃 ')>=0, /whRow/.test(h)]; }""")
        ok(r[0] == 1 and r[1] == 2 and r[2] == ["s", "r"] and 14 <= r[3] <= 16 and r[4] == 2 and r[5] and r[6], f"④ ⏰ 시간 칸 · 두 줄 합침 · 막대 2개 (📚 15분 · 🏃) {r}")
        r = await E("""()=>{ const D={a:{n:'루아', la:Date.now(), lk:'m', tl:{['m'+Math.round(Date.now()/1000-1800).toString(36)]:[Math.round(Date.now()/1000-1800), Math.round(Date.now()/1000)]}}}; HyDay.D['2026-01-01']=D; HyDay.day='2026-01-01'; const h=HyDay.timeCard(); HyDay.day=HyDay.key(); return [h.indexOf('🏘')>=0, h.indexOf('30분')>=0]; }""")
        ok(r == [True, True], f"④ 🏘 My Town 기록(마이타운에서 씀)도 막대 + 「30분」 {r}")
        # ⑤ 관리자
        await E("()=>{ sessionStorage.setItem('hyeng_admin_ok', String(Date.now())); }")
        await pg.goto(ORIGIN + "index.html?admin", wait_until="domcontentloaded"); await pg.wait_for_timeout(2500)
        r = await E("()=>[...document.querySelectorAll('#adTabs [data-t]')].map(b=>b.dataset.t+':'+b.innerText.replace(/\\s+/g,''))")
        ok([x.split(":")[0] for x in r] == ["now", "class", "time", "work", "send"], f"⑤ 탭 5개 {r}")
        r = await E("()=>{ const b=document.getElementById('adBody'); return [!!b.querySelector('#adVc'), !!b.querySelector('.adQRow'), /한 아이/.test(b.innerText), !!b.querySelector('.adTiles')]; }")
        ok(r == [False, False, False, True], f"⑤ 🏫 수업 탭 = 수업 타일만 (💬·바로가기 줄·📅 없음) {r}")
        await E("()=>document.querySelector('#adTabs [data-t=\"class\"]').click()"); await pg.wait_for_timeout(1200)
        r = await E("()=>{ const b=document.getElementById('adBody'); return [!!b.querySelector('#adVc'), /한 아이/.test(b.innerText)]; }")
        ok(r == [True, True], f"⑤ 👥 아이들 탭 = 📅 오늘 한 아이 + 💬 마을 대화 {r}")
        await E("()=>document.querySelector('#adTabs [data-t=\"time\"]').click()"); await pg.wait_for_timeout(1500)
        r = await E("()=>{ const b=document.getElementById('adBody'); return [/언제 했나/.test(b.innerText), b.querySelectorAll('.whRow').length]; }")
        ok(r[0], f"⑤ ⏰ 언제 했나 탭 {r}")
        await pg.screenshot(path=OUT + "study474_time.png", full_page=False)
        ok(not real_errs(errs), "오류 없음 " + str(real_errs(errs)[:3]))
        await br.close()
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)
asyncio.run(main())
