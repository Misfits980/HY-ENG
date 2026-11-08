# v626 💬 생활영어 — 책 고르기 탭 → 수준 4개 · ★1 듣고 배우기 → ★2 대답 고르기(유치원 그림) → ★3 상황 시험 · 💎 · 헷갈린 말 · 화면 안 넘침
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from harness import *

OUT = os.environ.get("HY_OUT", "/tmp/life626_")
bad = []
def ok(c, m):
    print(("OK  " if c else "BAD ") + m)
    if not c: bad.append(m)

# 문제를 끝까지 (wrongFirst: 첫 문제는 일부러 두 번 틀림 → 다시 나옴 · 헷갈린 말)
PLAY = """async (wf)=>{ const U=LifeUI; let k=0, kinds={}, w=wf?1:0;
  while(k++<200 && U.mode==='quiz'){ const q=U.cur(); kinds[q.k]=1;
    if(!q.res){ if(q.k==='ord'){ if(w){ q.pk=[1,0,2,3]; w=0; } else q.pk=[0,1,2,3]; U.ochk(); }
      else if(w){ const bad=q.o.map((o,i)=>i).filter(i=>q.o[i]!==q.a); U.pick(bad[0]); U.pick(bad[1]); w=0; }
      else U.pick(q.o.indexOf(q.a)); }
    U.qnext(); await new Promise(r=>setTimeout(r,10)); }
  return {mode:U.mode, first:U.first, n:U.n, kinds:Object.keys(kinds).sort().join(','), res:U.res}; }"""

FIT = """()=>{ const F=document.querySelector('#stLife .lfFoot'), Q=document.querySelector('#stLife .lfQ'), O=[...document.querySelectorAll('#stLife .lfO, #stLife .lfOrdS')];
  const fb=F ? F.getBoundingClientRect().top : innerHeight, last=O.length ? Math.max(...O.map(o=>o.getBoundingClientRect().bottom)) : 0;
  const S=document.getElementById('scStudy'); return {fit: last <= fb+1, last:Math.round(last), foot:Math.round(fb), sc:S.scrollHeight-S.clientHeight, w:document.documentElement.scrollWidth-innerWidth}; }"""

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for nm, (w, h) in (("ph", (390, 844)), ("pad", (820, 1180)), ("tv", (1920, 1080))):
            pg = await b.new_page(viewport={"width": w, "height": h}, is_mobile=nm != "tv", has_touch=nm != "tv"); errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            await boot(pg)
            await pg.evaluate("()=>{ Online.on=()=>false; localStorage.removeItem(Life.sk()); const s=Study.load(); s.book='g12'; Study.save(); StudyUI.open(); }"); await pg.wait_for_timeout(900)
            # 책 고르기 탭 맨 끝에 💬 생활영어
            r = await pg.evaluate("()=>{ const t=[...document.querySelectorAll('#stTabs .stCat')]; return [t.length, t[t.length-1].dataset.life, t[t.length-1].textContent]; }")
            ok(r[1] == "1" and "생활영어" in r[2], f"{nm} 책 고르기 끝에 생활영어 {r}")
            await pg.evaluate("()=>document.querySelector('#stTabs [data-life]').click()"); await pg.wait_for_timeout(900)
            r = await pg.evaluate("()=>({v:StudyUI._v, lv:LifeUI.lv, n:document.querySelectorAll('#stLife .lfSit').length, now:(document.querySelector('#stLife .lfSt.now')||{}).dataset, lvs:document.querySelectorAll('#stLife .lfLv').length})")
            ok(r["v"] == "stLife" and r["lv"] == "g12" and r["n"] == 12 and r["lvs"] == 4 and r["now"] and r["now"]["lfs"] == "g12-1", f"{nm} 생활영어 길 (G1-2 = 공부 책 따라) {r}")
            await pg.screenshot(path=f"{OUT}{nm}_home_g12.png")
            for lv in ("k", "g12", "g34", "g56"):
                await pg.evaluate("(lv)=>LifeUI.setLv(lv)", lv); await pg.wait_for_timeout(200)
                sid = lv + "-1"
                g0 = await pg.evaluate("()=>Wallet.gems()")
                # ★1 듣고 배우기
                await pg.evaluate("(id)=>LifeUI.go(id,1)", sid); await pg.wait_for_timeout(300)
                n = await pg.evaluate("()=>LifeUI.s.L.length")
                for i in range(n - 1):
                    await pg.evaluate("()=>document.querySelector('#stLife [data-lf=lnext]').click()")
                if nm != "tv" or lv == "g56":
                    await pg.screenshot(path=f"{OUT}{nm}_{lv}_learn.png")
                r = await pg.evaluate("()=>({b:document.querySelectorAll('#stLife .lfChat .lfB').length, btn:(document.querySelector('#stLife [data-lf=learned]')||{}).textContent})")
                ok(r["b"] == n and r["btn"] and "다 들었어요" in r["btn"], f"{nm} {lv} ★1 대화 {n}줄 다 보임 {r}")
                await pg.evaluate("()=>document.querySelector('#stLife [data-lf=learned]').click()"); await pg.wait_for_timeout(200)
                r = await pg.evaluate("(id)=>[LifeUI.mode, Life.stars(id), (document.querySelector('#stLife .lfEndB [data-t]')||{}).dataset]", sid)
                ok(r[0] == "end" and r[1] == 1 and r[2] and r[2]["t"] == "2", f"{nm} {lv} ★1 끝 → ★2 버튼 {r}")
                # ★2
                await pg.evaluate("()=>document.querySelector('#stLife .lfEndB [data-t]').click()"); await pg.wait_for_timeout(500)
                q = await pg.evaluate("()=>({k:LifeUI.cur().k, n:LifeUI.qs.length, o:LifeUI.cur().o.length})")
                ok(q["k"] == ("pic" if lv == "k" else "reply") and q["o"] == 3, f"{nm} {lv} ★2 = {'그림' if lv=='k' else '대답'} 고르기 {q}")
                fit = await pg.evaluate(FIT); ok(fit["fit"] and fit["w"] <= 0, f"{nm} {lv} ★2 보기가 아래 칸에 안 가림 {fit}")
                if nm != "tv" or lv == "g56": await pg.screenshot(path=f"{OUT}{nm}_{lv}_q2.png")
                # 처음 틀림 = 한 번 더 (정답 안 보임)
                r = await pg.evaluate("()=>{ const U=LifeUI, q=U.cur(); const i=q.o.findIndex(o=>o!==q.a); U.pick(i); return [q.res, q.tried.length, !!document.querySelector('#stLife .lfO.tried'), !document.querySelector('#stLife .lfO.ok'), document.querySelector('#stLife .lfFoot').textContent]; }")
                ok(r[0] is None and r[1] == 1 and r[2] and r[3] and "한 번 더" in r[4], f"{nm} {lv} 처음 틀리면 한 번 더 {r}")
                if nm == "ph" and lv == "g12": await pg.screenshot(path=f"{OUT}{nm}_{lv}_try.png")
                await pg.evaluate("()=>{ const q=LifeUI.cur(); LifeUI.pick(q.o.indexOf(q.a)); }")
                if nm == "ph" and lv == "g12": await pg.screenshot(path=f"{OUT}{nm}_{lv}_ok.png")
                await pg.evaluate("()=>LifeUI.qnext()")
                res = await pg.evaluate(PLAY, False)
                st = await pg.evaluate("(id)=>Life.stars(id)", sid)
                ok(res["mode"] == "end" and res["res"]["pass"] and st == 2, f"{nm} {lv} ★2 통과 {res} ★{st}")
                # ★3 상황 시험 (첫 문제 두 번 틀림)
                await pg.evaluate("(id)=>LifeUI.go(id,3)", sid); await pg.wait_for_timeout(400)
                ks = await pg.evaluate("()=>LifeUI.qs.map(q=>q.k).join(',')")
                want = {"k": {"say", "pic"}, "g12": {"say", "reply", "fb"}, "g34": {"say", "reply", "fb", "ord"}, "g56": {"say", "reply", "fb", "ord"}}[lv]
                ok(set(ks.split(",")) == want, f"{nm} {lv} ★3 문제 종류 {ks}")
                fit = await pg.evaluate(FIT); ok(fit["fit"], f"{nm} {lv} ★3 첫 화면 안 가림 {fit}")
                if nm != "tv" or lv == "g56": await pg.screenshot(path=f"{OUT}{nm}_{lv}_q3.png")
                # 순서 맞추기 화면 (G3-4 · G5-6)
                if lv in ("g34", "g56"):
                    await pg.evaluate("()=>{ const U=LifeUI; const i=U.qs.findIndex(q=>q.k==='ord'); const q=U.qs[i]; U.qs.splice(i,1); U.qs.splice(U.qi+1,0,q); }")
                n0 = await pg.evaluate("()=>LifeUI.qs.length")
                res = await pg.evaluate(PLAY, True)
                # 다시 나온 문제 · 끝
                ok(res["mode"] == "end" and res["n"] == n0 and res["first"] == n0 - 1, f"{nm} {lv} ★3 끝 (틀린 1개 다시 나옴) {res}")
                st = await pg.evaluate("(id)=>[Life.stars(id), Life.st().rv.length]", sid)
                g1 = await pg.evaluate("()=>Wallet.gems()")
                ok(st[0] == 3 and st[1] >= 1 and g1 - g0 == 10, f"{nm} {lv} ★3 · 헷갈린 말 저장 · 💎 2+3+5 {st} 💎{g1-g0}")
                if nm == "ph" and lv == "g34": await pg.screenshot(path=f"{OUT}{nm}_{lv}_end.png")
                # 같은 단계 다시 = 💎 없음
                await pg.evaluate("(id)=>LifeUI.go(id,2)", sid); await pg.wait_for_timeout(200); await pg.evaluate(PLAY, False)
                g2 = await pg.evaluate("()=>Wallet.gems()"); ok(g2 == g1, f"{nm} {lv} 다시 하면 💎 안 줌 {g2-g1}")
            # 순서 맞추기 중간 화면
            if nm in ("ph", "pad"):
                await pg.evaluate("()=>{ LifeUI.setLv('g56'); LifeUI.go('g56-1',3); const U=LifeUI; const i=U.qs.findIndex(q=>q.k==='ord'); U.qi=i; U.cur().pk=[0,1]; U.draw(); }"); await pg.wait_for_timeout(200)
                fit = await pg.evaluate(FIT); ok(fit["fit"], f"{nm} 순서 맞추기 안 가림 {fit}")
                await pg.screenshot(path=f"{OUT}{nm}_ord.png")
            # 🔁 헷갈린 말
            await pg.evaluate("()=>{ LifeUI.setLv('g34'); }"); await pg.wait_for_timeout(200)
            r = await pg.evaluate("()=>{ const b=document.querySelector('#stLife [data-lf=rv]'); return b ? b.textContent : null; }")
            ok(r and "헷갈린 말" in r, f"{nm} 길에 🔁 헷갈린 말 {r}")
            await pg.evaluate("()=>document.querySelector('#stLife [data-lf=rv]').click()"); await pg.wait_for_timeout(300)
            res = await pg.evaluate(PLAY, False)
            r = await pg.evaluate("()=>[LifeUI.rv, Life.st().rv.filter(x=>Life.lvOf(x.id)==='g34').length, document.querySelector('#stLife .lfEnd h2').textContent]")
            ok(res["mode"] == "end" and r[0] and r[1] == 0 and "다 잡았어요" in r[2], f"{nm} 헷갈린 말 다 맞히면 빠짐 {res} {r}")
            # 다음 상황 열림 · 잠긴 상황
            await pg.evaluate("()=>LifeUI.home()"); await pg.wait_for_timeout(200)
            r = await pg.evaluate("()=>({o2:Life.open('g34-2'), o3:Life.open('g34-3'), lock:document.querySelectorAll('#stLife .lfSit.lock').length, now:document.querySelector('#stLife .lfSt.now').dataset.lfs})")
            ok(r["o2"] and not r["o3"] and r["lock"] == 10 and r["now"] == "g34-2", f"{nm} 다음 상황만 열림 {r}")
            if nm == "ph": await pg.screenshot(path=f"{OUT}{nm}_home_g34.png")
            # ◀ = 원래 길 · 탭에 진행 수
            await pg.evaluate("()=>document.querySelector('#stLife [data-lf=close]').click()"); await pg.wait_for_timeout(600)
            r = await pg.evaluate("()=>[StudyUI._v, document.querySelector('#stTabs [data-life] small').textContent]")
            ok(r[0] == "stPath" and r[1].startswith("4 /"), f"{nm} ◀ 원래 길 · 탭 4 / 44 {r}")
            e = real_errs(errs); ok(not e, f"{nm} 오류 없음 {e[:3]}")
            await pg.close()
        await b.close()
    print("PASS" if not bad else "FAIL", len(bad))
    if bad: sys.exit(1)

asyncio.run(main())
