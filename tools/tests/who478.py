"""(v478) 사용자: "자기 패드나 휴대폰일 때 이름 고르기가 필요해? 공용 패드만 따로" → "그렇게 하자 · 확실하게 Daily 30 · 주간 레이드에서도 선택 안 하게"
  ① 내 기기: 설정 이름 = 명단 이름 → 저절로 묶임(hyeng_me) · 이름 고르기 창이 아예 안 뜸(KidPick.open = 바로 콜백)
  ② 성 빼고 이름만(「지후」 ↔ 「김지후」) 하나뿐이면 그 아이 · 명단에 없으면 새로 넣음(🆕 · 반 없음)
  ③ 이름을 바꿔도 같은 아이(id 그대로) · 보이는 이름은 새 이름
  ④ 예전에 다른 아이를 골라 둔 연결(박유범) = 이름이 다르면 버리고 내 이름으로
  ⑤ 반이 없으면 Daily 30 기회 = 미뤄 둠 → 선생님이 반을 정하면 쌓임
  ⑥ 주간 보스 화면: 이름 고르기·↺ 바꾸기 없음 · Daily 30 열어도 이름 고르기 안 뜸
  ⑦ 설정: 「📱 내 기기」 · 새로 넣은 줄이면 「명단에 내 이름이 따로 있어요」 → 고르면(확인) 그 줄로 묶음
  ⑧ 공용 패드는 예전처럼 이름 고르기 · My Town 도 같은 아이(hyeng_me)"""
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
        R = """(nick)=>{ localStorage.setItem('hyeng_nick', nick); ['hyeng_kid','hyeng_me','hyeng_teacher_dev','hyeng_boss_pend','hyeng_kp_ask'].forEach(k=>localStorage.removeItem(k)); sessionStorage.removeItem('hyeng_kid');
            HyBoss.ok=true; HyBoss.R=Object.assign(HyBoss.R||{}, {t:{a:{n:'초원', e:'🌱'}}, k:{k1:{n:'박유범', t:'a'}, k2:{n:'김지후', t:'a'}, k3:{n:'이서연', t:'a'}}}); HyBoss.refresh=()=>Promise.resolve(); }"""
        # ①
        await E(R, "이서연")
        r = await E("()=>{ const m=Kid.me(); let cb=null; KidPick.open(v=>{ cb=v && v.id; }); return [m.id, m.n, m.t, JSON.parse(localStorage.getItem('hyeng_me')).id, cb, !!document.getElementById('kidPick')]; }")
        ok(r == ["k3", "이서연", "a", "k3", "k3", False], f"① 같은 이름 → 저절로 묶임 · 이름 고르기 창 없이 바로 {r}")
        # ②
        await E(R, "지후"); r = await E("()=>{ const m=Kid.me(); return [m.id, m.n]; }")
        ok(r == ["k2", "지후"], f"② 「지후」 → 김지후(하나뿐) · 보이는 이름 지후 {r}")
        await E(R, "도윤"); r = await E("()=>{ const m=Kid.me(); const k=HyBoss.kids()[m.id]; return [m.id.length>5, k && k.n, k && k.t, !!(k && k.nw), m.nw]; }")
        ok(r == [True, "도윤", "", True, True], f"② 명단에 없음 → 새로 넣음(🆕 · 반 없음) {r}")
        # ③
        await E(R, "김지후"); id0 = await E("()=>Kid.me().id")
        await E("()=>NameCard.write('지후짱','test')"); r = await E("()=>{ const m=Kid.me(); return [m.id, m.n]; }")
        ok(r == [id0, "지후짱"], f"③ 이름을 바꿔도 같은 아이 · 이름만 바뀜 {r}")
        # ④
        await E(R, "김지후"); await E("()=>localStorage.setItem('hyeng_kid', JSON.stringify({id:'k1', n:'박유범', t:'a', pk:Date.now()}))")
        r = await E("()=>[Kid.me().id, localStorage.getItem('hyeng_kid')]")
        ok(r == ["k2", None], f"④ 예전에 고른 박유범 연결 → 버리고 김지후 {r}")
        await E(R, "지후"); await E("()=>localStorage.setItem('hyeng_kid', JSON.stringify({id:'k2', n:'김지후', t:'a', pk:Date.now()}))")
        r = await E("()=>Kid.me().id"); ok(r == "k2", f"④ 예전 연결이 비슷한 이름이면 그대로 {r}")
        # ⑤
        await E(R, "도윤")
        r = await E("""async ()=>{ const H=HyBoss; const on0=H.on, earn0=H.earn, B0=H.B, team0=H.team; H.B={id:'wb1', n:'보스', team:1, max:{a:100}}; H.on=()=>true; let got=[]; H.earn=(me,k,n)=>{ got.push([me.id,k,n]); return n; };
            const me=Kid.me(); H.pendAdd('s', 20, 10); const a=H.pendApply(me), n0=H.pendN(); H.R.k[me.id].t='a'; const b=H.pendApply(Kid.me()); const n1=H.pendN();
            H.on=on0; H.earn=earn0; H.B=B0; return [a, n0, b, n1, got]; }""")
        ok(r[0] == 0 and r[1] == 20 and r[2] == 2 and r[3] == 0 and r[4][0][1] == "study", f"⑤ 반 없음 = 미뤄 둠 → 반이 생기면 ⚔️ 2 {r}")
        # ⑥
        await E(R, "김지후")
        await E("()=>{ const s=Study.load(); s.book='g34'; s.set='elem'; Study.save(); StudyUI.open(); }"); await pg.wait_for_timeout(1200)
        ok(await E("()=>!document.getElementById('kidPick')"), "⑥ Daily 30 열어도 이름 고르기 안 뜸")
        await E("()=>StudyUI.path()")
        r = await E("""()=>{ HyBoss.B=HyBoss.B||{id:'wbx', n:'보스', max:{all:100}, hp:{all:100}}; const on0=HyBoss.on; HyBoss.on=()=>true; let h=''; try{ WeekBoss.open(); const d=document.getElementById('wbView'); h=d?d.innerHTML:''; WeekBoss.close(); }catch(e){ h='ERR '+e.message; } HyBoss.on=on0; return [/내 이름 고르기/.test(h), /data-kidpick="1" title="바꾸기" hidden/.test(h) || !/title="바꾸기"/.test(h)]; }""")
        ok(r == [False, True], f"⑥ 주간 보스 화면: 이름 고르기·↺ 없음 {r}")
        # ⑦
        await E(R, "도윤")
        await E("()=>{ Kid.me(); openSettings(); }"); await pg.wait_for_timeout(200)
        r = await E("()=>document.getElementById('kwRow').innerText")
        ok("내 기기" in r and "도윤" in r and "명단에 내 이름이 따로" in r, f"⑦ 설정: 📱 내 기기 + 「명단에 내 이름이 따로 있어요」 {r!r}")
        await E("()=>document.querySelector('#kwRow [data-kw=\"find\"]').click()"); await pg.wait_for_timeout(200)
        ok(await E("()=>!!document.querySelector('#kidPick .kpL')"), "⑦ 그때만 명단이 열림")
        await E("()=>document.querySelector('#kidPick .kpL [data-kp=\"k1\"]').click()"); await pg.wait_for_timeout(150)
        ok(await E("()=>/정말 나예요/.test(document.getElementById('kidPick').innerText)"), "⑦ 다른 이름이면 한 번 더 확인")
        await E("()=>document.querySelector('#kidPick [data-sure]').click()"); await pg.wait_for_timeout(200)
        r = await E("()=>[Kid.me().id, Kid.me().n]"); ok(r == ["k1", "도윤"], f"⑦ 확인하면 그 줄로 묶음 (보이는 이름은 설정 이름) {r}")
        await E("()=>closeSettings()")
        # ⑨ 같은 이름이 여럿 → 새로 만들지 않고 한 번 고르기
        await E(R, "김지후"); await E("()=>{ HyBoss.R.k.k4={n:'김지후', t:'a'}; }")
        r = await E("()=>{ const m=Kid.me(); return [!!m.tmp, m.amb, localStorage.getItem('hyeng_me'), Object.keys(HyBoss.R.k).length]; }")
        ok(r == [True, 1, None, 4], f"⑨ 명단에 같은 이름 둘 → 새 줄 안 만듦 · 한 번 고르기 {r}")
        await E("()=>{ openSettings(); }"); await pg.wait_for_timeout(150)
        await E("()=>document.querySelector('#kwRow [data-kw=\"find\"]').click()"); await pg.wait_for_timeout(200)
        await E("()=>document.querySelector('#kidPick .kpL [data-kp=\"k4\"]').click()"); await pg.wait_for_timeout(200)
        r = await E("()=>{ closeSettings(); return Kid.me().id; }"); ok(r == "k4", f"⑨ 고르면 그 줄로 {r}")
        # ⑩ 선생님 기기로 바꾸면 이 기기가 저절로 만든 🆕 줄은 명단에서 지움
        await E(R, "영어선생님"); nid = await E("()=>Kid.me().id")
        r = await E("()=>{ Kid.setTeacher(true); const r=[!!HyBoss.R.k[arguments[0]], localStorage.getItem('hyeng_me')]; Kid.setTeacher(false); return r; }".replace("arguments[0]", repr(nid)))
        ok(r == [False, None], f"⑩ 선생님 기기 → 저절로 만든 「영어선생님」 줄 지움 {r}")
        # ⑧
        await E(R, "한양패드1"); r = await E("()=>{ const a=Kid.me(); KidPick.open(()=>{}); const b=!!document.getElementById('kidPick'); KidPick.close(); return [a, b, localStorage.getItem('hyeng_me')]; }")
        ok(r == [None, True, None], f"⑧ 공용 패드는 예전처럼 이름 고르기 {r}")
        await E(R, "김지후"); await E("()=>Kid.me()")
        H = await ctx.new_page(); H.on("pageerror", lambda e: errs.append("H " + str(e))); await H.route("**/*", route)
        await H.goto(ORIGIN + "proto/house.html"); await H.wait_for_timeout(2500)
        r = await H.evaluate("()=>{ const K=kidInfo(); return [K.n, K.rid]; }")
        ok(r == ["김지후", "k2"], f"⑧ My Town = 같은 아이(k2) {r}")
        ok(not real_errs(errs), "오류 없음 " + str(real_errs(errs)[:3]))
        await br.close()
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)
asyncio.run(main())
