"""(v476) 사용자: "영어 선생님인데 타운에 박유범으로 들어가져 · 보스도 내가 안 잡았는데 박유범 설정돼서 박유범 보상을 받음 · 플레이어에서 이름 바꾸면 자동으로 그 이름 뜨게 · 연계되는 것도"
  ① 내 기기에 남은 「박유범」 연결 → 설정에 ⚠️ 「기록이 쌓이는 이름: 박유범」 + 「내 이름으로 하기」 → 풀림
  ② 플레이어 이름을 바꾸면 이름이 다른 명단 연결은 풀림 · 새 이름과 같은 명단 아이가 있으면 그 아이로 · 이름에서 저절로 붙은 연결은 이름이 바뀌면 버림
  ③ 관리 비밀번호를 넣은 기기 = 🧑‍🏫 선생님 기기: 남은 아이 연결 풀기 · 그 아이 이름으로 이 기기가 올린 ☁️ 백업 지움 · 받은 수업 보석 합계 안내
  ④ 선생님 기기: Kid.me = 선생님(내 이름) · ☁️ 백업 안 함 · 「오늘 한 아이」에 안 들어감 · 아이 이름을 고르면 이번에만(sessionStorage · 20분)
  ⑤ 이름 고르기 창에 「🧑‍🏫 선생님이에요」 (공용 패드엔 없음) · 틀린 비밀번호 → 「비밀번호가 달라요」
  ⑥ My Town(proto/house.html)도 같은 규칙: 선생님 기기 → 내 이름 · 낡은 자동 연결 → 내 이름"""
import asyncio, sys, os, json
os.environ["HY_REAL3D"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "FAIL ") + m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        ctx = await br.new_context(viewport={"width": 430, "height": 900})
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await boot(pg); E = pg.evaluate
        SETUP = """()=>{ localStorage.setItem('hyeng_nick','영어선생님'); localStorage.setItem('hyeng_dev','abcdef123456'); localStorage.removeItem('hyeng_teacher_dev'); sessionStorage.removeItem('hyeng_kid');
            HyBoss.R=Object.assign(HyBoss.R||{}, {t:{a:{n:'초원', e:'🌱'}}, k:{k1:{n:'박유범', t:'a'}, k2:{n:'김지후', t:'a'}}});
            localStorage.setItem('hyeng_kid', JSON.stringify({id:'k1', n:'박유범', t:'a', pk:Date.now()})); }"""
        # ① ② (v478 부터 개인 기기는 「내 기기」 — 남은 아이 연결은 쓰지 않음 · 자세한 건 who478)
        await E(SETUP)
        r = await E("()=>{ HyBoss.ok=true; const m=Kid.me(); return [m.n, m.id==='k1', localStorage.getItem('hyeng_kid')]; }")
        ok(r[0] == "영어선생님" and r[1] is False and r[2] is None, f"①② 개인 기기: 남은 「박유범」 연결을 안 씀 · 내 이름 {r}")
        await E("()=>localStorage.removeItem('hyeng_me')")
        # ③ ④
        await E("()=>localStorage.setItem('hyeng_nick','영어선생님')")
        await E(SETUP)
        await E("""()=>{ const W=Wallet.raw(); W.log=(W.log||[]).concat([[Date.now(), 30, '🎁 수업 보석 (공용 패드)', 30],[Date.now(), 20, '🎁 수업 보석 (레이드)', 50]]); }""")
        await E("()=>FB.set('/hy/acct/k1', {dev:Online.dev(), n:'박유범', at:1, d:'{}'})")
        r = await E("async ()=>{ const k=Kid.setTeacher(true); await new Promise(r=>setTimeout(r,500)); const a=await FB.get('/hy/acct/k1'); return [k && k.n, localStorage.getItem('hyeng_kid'), a, document.getElementById('hyToast') ? document.getElementById('hyToast').innerText : (document.querySelector('.hyToast')||{}).innerText, JSON.parse(localStorage.getItem('hyeng_unhook')||'{}').g]; }")
        ok(r[0] == "박유범" and r[1] is None and r[2] is None, f"③ 선생님 기기로 → 박유범 연결 풀림 · 이 기기가 올린 박유범 ☁️ 백업 지움 {r[:3]}")
        ok(r[4] == 50 or (r[4] or 0) >= 50, f"③ 그 이름으로 받은 수업 보석 합계 안내 💎 {r[4]} · 「{r[3]}」")
        r = await E("()=>{ const m=Kid.me(); return [m.n, m.teacher, m.id.slice(0,1), Cloud.who()]; }")
        ok(r == ["영어선생님", 1, "t", None], f"④ 선생님 기기: 내 이름 · ☁️ 백업 안 함 {r}")
        r = await E("async ()=>{ const day=HyDay.key(); HyDay.add({s:1, so:1, sw:0}); await new Promise(r=>setTimeout(r,300)); const D=await FB.get('/hy/day/'+day); return Object.keys(D||{}).filter(k=>k[0]==='t'); }")
        ok(r == [], f"④ 선생님 판은 「오늘 한 아이」에 안 들어감 {r}")
        # 이번에만 아이 이름
        await E("()=>{ KidPick.open(()=>{}); }"); await pg.wait_for_timeout(200)
        r = await E("()=>[document.querySelector('#kidPick').innerText.indexOf('선생님 기기')>=0, !!document.querySelector('#kidPick [data-kptch]')]")
        ok(r == [True, False], f"④ 선생님 기기의 이름 고르기 창 = 「고른 이름은 이번에만」 안내 {r}")
        await E("()=>document.querySelector('#kidPick [data-kp=\"k2\"]').click()"); await pg.wait_for_timeout(200)
        r = await E("()=>[Kid.me().n, localStorage.getItem('hyeng_kid'), !!sessionStorage.getItem('hyeng_kid')]")
        ok(r == ["김지후", None, True], f"④ 아이 이름을 고르면 이번에만 (sessionStorage) {r}")
        await E("()=>{ const v=JSON.parse(sessionStorage.getItem('hyeng_kid')); v.at=Date.now()-21*60000; sessionStorage.setItem('hyeng_kid', JSON.stringify(v)); }")
        r = await E("()=>Kid.me().n"); ok(r == "영어선생님", f"④ 20분 지나면 다시 선생님 {r}")
        # ⑤
        await E("()=>{ Kid.setTeacher(false); localStorage.setItem('hyeng_nick','영어선생님'); openSettings(); }"); await pg.wait_for_timeout(200)
        ok(await E("()=>!!document.querySelector('#kwRow [data-kw=\"tch\"]')"), "⑤ (v478) 개인 기기 = 설정에 「🧑‍🏫 선생님이에요」")
        await E("()=>{ document.querySelector('#kwRow [data-kw=\"tch\"]').click(); closeSettings(); }"); await pg.wait_for_timeout(200)
        await E("()=>{ document.getElementById('kpPin').value='1111'; document.querySelector('#kidPick [data-kptok]').click(); }"); await pg.wait_for_timeout(400)
        r = await E("()=>[document.getElementById('kpMsg').textContent, Kid.teacher()]")
        ok(r == ["비밀번호가 달라요", False], f"⑤ 틀린 비밀번호 {r}")
        await E("()=>{ KidPick.close(); localStorage.setItem('hyeng_nick','한양패드1'); KidPick.open(()=>{}); }"); await pg.wait_for_timeout(200)
        ok(await E("()=>!document.querySelector('#kidPick [data-kptch]')"), "⑤ 공용 패드엔 「선생님이에요」 없음")
        await E("()=>{ KidPick.close(); localStorage.setItem('hyeng_nick','영어선생님'); }")
        # ⑥ My Town
        H = await ctx.new_page(); H.on("pageerror", lambda e: errs.append("H " + str(e)))
        await H.route("**/*", route)
        await H.goto(ORIGIN + "proto/house.html"); await H.wait_for_timeout(2500)
        r = await H.evaluate("""()=>{ const out=[]; localStorage.setItem('hyeng_nick','영어선생님'); localStorage.setItem('hyeng_kid', JSON.stringify({id:'k1', n:'박유범', t:'a', pk:Date.now()}));
            localStorage.setItem('hyeng_teacher_dev','1'); return out; }""")
        r = await H.evaluate("()=>{ const K=window.kidInfo ? kidInfo() : null; return K && [K.n, K.rid]; }")
        ok(r == ["영어선생님", ""], f"⑥ My Town 선생님 기기 = 내 이름 (남은 박유범 무시) {r}")
        r = await H.evaluate("()=>{ localStorage.removeItem('hyeng_teacher_dev'); localStorage.setItem('hyeng_kid', JSON.stringify({id:'k2', n:'김지후', t:'a', auto:1})); const K=kidInfo(); return [K.n, K.rid]; }")
        me = await H.evaluate("()=>(JSON.parse(localStorage.getItem('hyeng_me')||'null')||{}).id||''")
        ok(r == ["영어선생님", me], f"⑥ My Town 낡은 자동 연결 무시 → 내 기기 이름(hyeng_me) {r}")
        r = await H.evaluate("()=>{ localStorage.setItem('hyeng_kid', JSON.stringify({id:'k2', n:'김지후', t:'a', pk:Date.now()})); const K=kidInfo(); return [K.n, K.rid]; }")
        ok(r == ["영어선생님", me], f"⑥ (v478) 개인 기기는 남은 아이 연결(hyeng_kid)도 무시 → 내 기기 {r}")
        ok(not real_errs(errs), "오류 없음 " + str(real_errs(errs)[:3]))
        await br.close()
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)
asyncio.run(main())
