"""(v439) 사용자 사진 3장 (교실 2대2 레이스 · 유치부)
  ① 📺 TV: 2대2 인데 한 줄에 3명 — 깃발 든 큰 캐릭터(반 1등)와 무리에 1등이 또 그려짐 → 무리 = 1등 뺀 나머지 · 한 줄 = 그 반 아이 수
  ② 패드: 내 반만 무리를 그려서 2대2 가 3대1 처럼 보임 → 모든 반 무리 (3명까지)
  ③ 유치원 단모음 '잘 듣고 빈칸 소리' 타일이 한 점으로 겹침 — 보드게임 .bdT(동그란 칸) CSS 가 덮어씀 → #stQ 안으로
  ④ 사용자: "G1-2 에서 문장이 뜻도 없이 나옴 · 최소한 뜻이 나오고 밑줄로" → G1-2·G3-4 배우는 판 대화·문장 빈칸: 해석 + 빈칸 뜻 밑줄(없으면 💡 빈칸 = 뜻) · G5-6·중등·시험은 그대로"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch()
        for tv in (True, False):
            pg = await br.new_page(viewport={"width": 1180, "height": 820}); pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)
            await pg.evaluate(f"()=>FlagRun.demo(false, {{teams:2, kids:2, tv:{'true' if tv else 'false'}}})"); await pg.wait_for_timeout(900)
            r = await pg.evaluate("""()=>FlagRun.o.L.map(T=>{ const R=document.getElementById('frR'+T.k); return [T.kids.length, R.querySelectorAll('.frSpr').length + R.querySelectorAll('.frKid').length, R.querySelector('.frSpr').style.backgroundImage.indexOf(T.kids.slice().sort((a,b)=>b.sc-a.sc)[0].ch)>=0]; })""")
            ok(all(a == b and c for a, b, c in r), f"{'📺 TV' if tv else '패드'}: 한 줄 캐릭터 수 = 그 반 아이 수 · 큰 캐릭터 = 1등 아이 {r}")
            await pg.screenshot(path=OUT + f"fr439_{'tv' if tv else 'pad'}.png")
            if tv:
                await pg.evaluate("()=>{ FlagRun.close(); FlagRun.demo(false, {teams:2, kids:9, tv:true}); }"); await pg.wait_for_timeout(700)
                r = await pg.evaluate("()=>FlagRun.o.L.map(T=>{ const R=document.getElementById('frR'+T.k); return [R.querySelectorAll('.frKid').length, (R.querySelector('.frMore')||{}).textContent]; })")
                ok(all(a == 6 and m == "+2" for a, m in r), f"📺 9명 반: 큰 캐릭터 1 + 무리 6 + '+2' {r}")
            await pg.close()
        pg = await br.new_page(viewport={"width": 820, "height": 1180}); pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)
        await pg.evaluate("()=>{ Voice.canListen=()=>true; StudyUI.open(); }"); await pg.wait_for_timeout(600)
        r = await pg.evaluate("""()=>{ const s=Study.load(); s.lv={}; const L=Study.lessons('short'); const i=L.findIndex(x=>!x.fin); const K=Study.key('short',L[i].n); s.seen={}; L[i].ws.forEach(w=>s.seen[w.en]=1); s.lv[K]=1; Study.save();
            StudyUI.book=Study.bookOf('short'); StudyUI.set='short'; StudyUI.start(i,false); const j=StudyUI.qs.findIndex(q=>q.t==='blend' && q.aud); StudyUI.i=j; StudyUI.show();
            const T=[...document.querySelectorAll('#bdRow .bdT')].map(e=>e.getBoundingClientRect()); return [T.length, T.every(b=>b.width>=40 && b.height>=50), T.every((b,k)=>!k || b.left>=T[k-1].right-1), getComputedStyle(document.querySelector('#bdRow .bdT')).position]; }""")
        ok(r[0] >= 2 and r[1] and r[2] and r[3] == "static", f"③ 단모음 빈칸 타일: 크기 그대로 · 나란히 (겹침 없음) {r}")
        await pg.screenshot(path=OUT + "fr439_vhear.png")
        for st, want in (("basic", True), ("elem", True), ("g56", False)):
            r = await pg.evaluate("""(st)=>{ const s=Study.load(); s.lv={}; s.seen={}; Study.save(); const L=Study.lessons(st), i=L.findIndex(x=>!x.fin); StudyUI.book=Study.bookOf(st); StudyUI.set=st; StudyUI.start(i,false); const out=[];
                StudyUI.qs.forEach((q,j)=>{ if(!((q.t==='talk') || (q.t==='sent' && !q.col && q.st && q.st.ko))) return; StudyUI.i=j; StudyUI.show(); const d=document.getElementById('stQ');
                  out.push([q.t, !!d.querySelector('.stTalkKo, .stSentKo'), !!(d.querySelector('u.koU') || d.querySelector('.stKoHint'))]); }); return out; }""", st)
            good = [x for x in r if x[2] == want and (x[1] or not want or x[0] == 'sent')]
            ok(len(r) >= 3 and len(good) == len(r), f"④ {st}: 대화·문장 빈칸 {len(r)}개 — {'해석 + 뜻 밑줄/💡' if want else '그대로 (도움 없음)'} {r[:4]}")
        await pg.screenshot(path=OUT + "fr439_g12.png")
        await br.close()
    real = real_errs(errs)
    ok(not real, f"오류 없음 {real[:3]}")
    print("DONE bad=%d" % len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
