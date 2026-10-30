"""(v473) 사용자: "밤 10시 되면 (타워) 문 닫고 · 들어가려면 관리자 비밀번호 · 오전 6시 열림 · 1분 전 알림 · 주말도" · "마을에서 애들이 떠들고 이야기할 수 있는 수단 (정해진 말 + 자유 입력)"
  ① 🌙 22:00~06:00 (한국 시간) = 닫힘 · 06:00 열림 · 주말도 같음 · 다음 아침 6시 계산
  ② 닫힌 시간에 🗼 → 🌙 창 + 선생님 비밀번호 칸 · 틀리면 「비밀번호가 달라요」 · 열린 패드(아침 6시까지)는 그냥 고르기 창
  ③ 타워 안: 21:59 = 「1분 뒤」 알림 · 22:00 = 마을로 · 선생님이 연 패드는 안 쫓겨남
  ④ 💬 나쁜 말·전화번호·주소 = *** (원래 글은 선생님만) · 보통 말은 그대로
  ⑤ 두 아이가 마을에: 서로 보임(이름표) · 말하기 → 상대 화면 머리 위 말풍선 + 왼쪽 위 대화 띠 · 💬 창 목록
  ⑥ 천천히(1.5초) · 같은 말 세 번 = 10초 쉬기 · 마을 밖으로 나가면 내 자리 지움
  ⑦ 선생님 화면 💬 마을 대화: 나쁜 말 빨갛게 + 원래 글 · 🗑 두 번 = 지움"""
import asyncio, sys, os, json, re
os.environ["HY_REAL3D"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright
DB = {}
def db_get(path):
    o = DB
    for k in [x for x in path.split("/") if x]:
        if not isinstance(o, dict) or k not in o: return None
        o = o[k]
    return o
def db_put(path, v):
    ks = [x for x in path.split("/") if x]; o = DB
    for k in ks[:-1]: o = o.setdefault(k, {})
    if v is None: o.pop(ks[-1], None)
    else: o[ks[-1]] = v
async def fake(r):
    url = r.request.url
    if "firebasedatabase.app" in url or "firebaseio.com" in url:
        if "text/event-stream" in (r.request.headers.get("accept") or ""): return await r.fulfill(status=503, body="no")
        path = re.sub(r"^https://[^/]+", "", url).split("?")[0]; path = path[:-5] if path.endswith(".json") else path
        m = r.request.method
        if path == "/hy/ok": return await r.fulfill(status=200, body="true", content_type="application/json")
        if m == "GET": return await r.fulfill(status=200, body=json.dumps(db_get(path)), content_type="application/json")
        if m == "PUT": v = json.loads(r.request.post_data or "null"); db_put(path, v); return await r.fulfill(status=200, body=json.dumps(v), content_type="application/json")
        if m == "DELETE": db_put(path, None); return await r.fulfill(status=200, body="null", content_type="application/json")
        return await r.fulfill(status=400, body="x")
    return await route(r)

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "FAIL ") + m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        async def open_kid(code, name):
            ctx = await br.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
            pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
            await pg.route("**/*", fake); await pg.goto(ORIGIN + "proto/house.html"); await pg.wait_for_timeout(600)
            await pg.evaluate("""([c,n])=>{ Object.keys(localStorage).filter(k=>k.startsWith('hyeng_proto_')).forEach(k=>localStorage.removeItem(k)); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); localStorage.setItem('hyeng_proto_baitok','1');
                localStorage.setItem('hyeng_proto_code', JSON.stringify(c)); localStorage.setItem('hyeng_nick', n); }""", [code, name])
            await pg.reload(); await pg.wait_for_timeout(2000); return pg
        async def until(pg, js, n=60):
            for _ in range(n):
                try:
                    if await pg.evaluate(js): return True
                except Exception: pass
                await pg.wait_for_timeout(200)
            return False
        A = await open_kid("AAAAA", "루아"); E = A.evaluate
        # 시각 맞추기: KST h:m:s 가 되게 TWN8.test
        SET = """([h,m,s,dow])=>{ const H=HOUSE, N=H.TWN8; N.force=true; N.test=0; const t=H.srvNow(), d=new Date(t+9*3600e3); let tgt=Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate(), h, m, s)-9*3600e3;
            if(dow!=null){ while(new Date(tgt+9*3600e3).getUTCDay()!==dow) tgt+=86400e3; } N.test=tgt-Date.now()-N.off; return new Date(H.srvNow()+9*3600e3).toISOString().slice(0,19); }"""
        # ①
        r = await E("""()=>{ const H=HOUSE, k=(h,m)=>{ const t=Date.UTC(2026,9,30,h,m)-9*3600e3; return H.twNightAt(t); }, sat=Date.UTC(2026,9,31,23,0)-9*3600e3;
            const o=H.twOpenAt(Date.UTC(2026,9,30,22,30)-9*3600e3), o2=H.twOpenAt(Date.UTC(2026,9,31,3,0)-9*3600e3);
            return [k(21,59), k(22,0), k(23,30), k(2,0), k(5,59), k(6,0), k(12,0), H.twNightAt(sat), new Date(o+9*3600e3).toISOString().slice(0,16), new Date(o2+9*3600e3).toISOString().slice(0,16)]; }""")
        ok(r == [False, True, True, True, True, False, False, True, "2026-10-31T06:00", "2026-10-31T06:00"], f"① 22:00~05:59 닫힘 · 06:00 열림 · 토요일도 · 다음 아침 6시 {r}")
        # ②
        await E("()=>{ HOUSE.setWx(false); HOUSE.go('village'); }"); await until(A, "()=>HOUSE.place()==='village'")
        print(await E(SET, [23, 10, 0, None]))
        await E("()=>HOUSE.towerAskX()"); await A.wait_for_timeout(300)
        r = await E("()=>[document.getElementById('infoT').innerText, !!document.getElementById('twPin'), !!document.getElementById('twS')]")
        ok("문을 닫았어요" in r[0] and "아침 6시" in r[0] and r[1] and not r[2], f"② 23:10 🗼 → 🌙 닫힘 창 + 비밀번호 칸 (고르기 단추 없음) {r[0][:60]!r}")
        await E("()=>{ document.getElementById('twPin').value='0000'; document.getElementById('twPinB').click(); }"); await A.wait_for_timeout(400)
        r = await E("()=>[document.getElementById('twPinM').textContent, HOUSE.twNightOn()]")
        ok(r[0] == "비밀번호가 달라요" and r[1], f"② 틀린 비밀번호 → 「비밀번호가 달라요」 · 그대로 닫힘 {r}")
        await E("()=>{ document.getElementById('info').classList.remove('on'); localStorage.setItem('hyeng_proto_twnight', JSON.stringify(HOUSE.twOpenAt(HOUSE.srvNow()))); }")
        await E("()=>HOUSE.towerAskX()"); await A.wait_for_timeout(300)
        r = await E("()=>[HOUSE.twNightOn(), !!document.getElementById('twS')]")
        ok(r == [False, True], f"② 선생님이 연 패드(아침 6시까지) → 고르기 창 {r}")
        await E("()=>{ document.getElementById('info').classList.remove('on'); localStorage.removeItem('hyeng_proto_twnight'); }")
        print(await E(SET, [6, 0, 30, None]))
        r = await E("()=>HOUSE.twNightOn()"); ok(r is False, "② 아침 6시 = 다시 열림")
        # ③
        print(await E(SET, [21, 59, 20, None]))
        await E("()=>{ HOUSE.TW.seed='2026-11-01'; HOUSE.twEnterGo('sky'); }"); await until(A, "()=>HOUSE.place()==='tower' && HOUSE.TW.on")
        await A.wait_for_timeout(1300)
        r = await E("()=>document.getElementById('toast').innerText")
        ok("1분 뒤" in r, f"③ 21:59 = 「1분 뒤 타워 문이 닫혀요」 {r!r}")
        await E("()=>{ HOUSE.TWN8.test+=45000; }")
        ok(await until(A, "()=>HOUSE.place()==='village' && !HOUSE.TW.on", 40), "③ 22:00 → 마을로")
        r = await E("()=>document.getElementById('toast').innerText"); ok("문 닫는 시간" in r, f"③ 「타워 문 닫는 시간」 {r!r}")
        await A.wait_for_timeout(600)
        await E("()=>{ localStorage.setItem('hyeng_proto_twnight', JSON.stringify(HOUSE.twOpenAt(HOUSE.srvNow()))); HOUSE.twEnterGo('sky'); }"); await until(A, "()=>HOUSE.place()==='tower' && HOUSE.TW.on")
        await A.wait_for_timeout(2200)
        ok(await E("()=>HOUSE.place()==='tower' && HOUSE.TW.on"), "③ 선생님이 연 패드는 밤에도 타워 그대로")
        await E("()=>{ localStorage.removeItem('hyeng_proto_twnight'); HOUSE.TWN8.force=false; HOUSE.TWN8.test=0; HOUSE.twLeave(); }"); await until(A, "()=>HOUSE.place()==='village'")
        # ④
        r = await E("""()=>['Hello, friends!','씨발 진짜','시 1 발','너 바보 멍청이','내 번호 010-1234-5678','www.abc.com 와','fuck you','ㅋㅋㅋㅋ 재밌다'].map(s=>{ const o=HOUSE.vcClean(s); return [o.m, o.bad]; })""")
        ok(r[0] == ["Hello, friends!", False] and r[1][1] and "씨발" not in r[1][0] and r[2][1] and "발" not in r[2][0] and r[3][1] and "멍청" not in r[3][0] and "바보" in r[3][0]
           and r[4][1] and "1234" not in r[4][0] and r[5][1] and "abc" not in r[5][0] and r[6][1] and "fuck" not in r[6][0] and r[7] == ["ㅋㅋㅋㅋ 재밌다", False], f"④ 나쁜 말·번호·주소 = *** {r}")
        # ⑤
        B = await open_kid("BBBBB", "주호")
        await B.evaluate("()=>{ HOUSE.setWx(false); HOUSE.go('village'); }"); await until(B, "()=>HOUSE.place()==='village'")
        ok(await until(A, "()=>HOUSE.vlCount()===1", 60) and await until(B, "()=>HOUSE.vlCount()===1", 60), "⑤ 둘 다 마을 → 서로 보임")
        r = await B.evaluate("()=>{ const c=Object.values(HOUSE.VLN.peers)[0]; return [c.nm, !!c.tag, c.g.visible]; }")
        ok(r == ["루아", True, True], f"⑤ B 화면의 A = 이름표 「루아」 {r}")
        await E("()=>{ document.getElementById('bChat').click(); }")
        r = await E("()=>[document.getElementById('vcPane').classList.contains('on'), document.querySelectorAll('#vcQuick button').length, document.querySelectorAll('#vcEmo button').length, document.getElementById('vcWho').textContent]")
        ok(r[0] and r[1] >= 15 and r[2] == 8 and "1명" in r[3], f"⑤ 💬 말하기 창: 정해진 말 {r[1]} · 이모지 {r[2]} · {r[3]}")
        await E("()=>document.querySelector('#vcQuick [data-q=\"1\"]').click()")
        r = await E("()=>[!!HOUSE.hero().say, document.getElementById('vcFeed').innerText, document.getElementById('vcList').innerText]")
        ok(r[0] and "Hello, friends!" in r[1] and "Hello, friends!" in r[2], f"⑤ 내 머리 위 말풍선 · 대화 띠 · 목록 {r[1:]}")
        ok(await until(B, "()=>document.getElementById('vcFeed').innerText.indexOf('Hello, friends!')>=0", 40), "⑤ B 화면 대화 띠에 「루아 Hello, friends!」")
        r = await B.evaluate("()=>{ const c=Object.values(HOUSE.VLN.peers)[0]; return [!!c.say, document.getElementById('vcFeed').innerText]; }")
        ok(r[0] and "루아" in r[1], f"⑤ B 화면 A 머리 위 말풍선 {r}")
        await A.screenshot(path=OUT + "town473_a.png"); await B.screenshot(path=OUT + "town473_b.png")
        await A.wait_for_timeout(1600)
        await E("()=>{ const i=document.getElementById('vcTxt'); i.value='야 씨발 내 번호 01012345678'; document.getElementById('vcSend').click(); }")
        ok(await until(B, "()=>document.getElementById('vcFeed').innerText.indexOf('***')>=0", 40), "④ 나쁜 말 → B 에게는 *** 로")
        r = await B.evaluate("()=>document.getElementById('vcFeed').innerText"); ok("씨발" not in r and "0101" not in r, f"④ B 화면에 원래 말 없음 {r!r}")
        # ⑥
        r = await E("""async ()=>{ const H=HOUSE, w=ms=>new Promise(r=>setTimeout(r,ms)); H.vcSay('Hi! 👋'); const a=H.vcSay('Yes!'); const t1=document.getElementById('toast').innerText; await w(1600); const b=H.vcSay('Yes!'); await w(1600); const c=H.vcSay('Yes!'); await w(1600); const d=H.vcSay('Yes!'); const t2=document.getElementById('toast').innerText; return [a, t1, b, c, d, t2]; }""")
        ok(r[0] is False and "천천히" in r[1] and r[2] and r[3] and r[4] is False and "10초" in r[5], f"⑥ 1.5초 안 = 천천히 · 같은 말 3번째 = 10초 쉬기 {r}")
        await E("()=>HOUSE.go('yard')"); await until(A, "()=>HOUSE.place()==='yard'")
        ok(await until(B, "()=>HOUSE.vlCount()===0", 60), "⑥ A 가 마당으로 → B 화면에서 사라짐")
        day = await E("()=>HOUSE.VLN.mp")
        r = db_get(day) or {}
        bads = [v for v in r.values() if v.get("b")]
        ok(len(r) >= 4 and len(bads) == 1 and "씨발" in bads[0].get("r", "") and "***" in bads[0]["m"], f"⑦ 서버: 말 {len(r)}개 · 나쁜 말 1개(원래 글은 r) {bads}")
        # ⑦ 선생님 화면 (관리자 카드 그리기)
        T = await (await br.new_context(viewport={"width": 430, "height": 900})).new_page(); T.on("pageerror", lambda e: errs.append(str(e)))
        await T.route("**/*", fake); await T.goto(ORIGIN + "index.html", wait_until="domcontentloaded"); await T.wait_for_timeout(2500)
        r = await T.evaluate("""async (path)=>{ const k=path.slice(-8); if(HyVc.ymd(0)!==k) return ['day', HyVc.ymd(0), k]; await HyVc.load(); const h=HyVc.html(); const id=HyVc.list.find(x=>x.b).id;
            return [HyVc.list.length, (h.match(/adVcRow bad/g)||[]).length, h.indexOf('원래: ')>=0, id]; }""", day)
        ok(r[0] >= 4 and r[1] == 1 and r[2], f"⑦ 💬 마을 대화 카드: 말 {r[0]} · 빨간 줄 {r[1]} · 원래 글 {r[2]}")
        n0 = len(db_get(day) or {})
        await T.evaluate("""(id)=>{ const d=document.createElement('div'); d.id='adVc'; document.body.appendChild(d); HyVc.paint(); const b=()=>document.querySelector('#adVc [data-id="'+id+'"]'); HyVc.act('vcDel', b()); HyVc.act('vcDel', b()); }""", r[3])
        await T.wait_for_timeout(800)
        r2 = db_get(day) or {}
        ok(r[3] not in r2 and len(r2) == n0 - 1, f"⑦ 🗑 두 번 → 서버에서 지움 ({len(r2)}개 남음)")
        ok(not real_errs(errs), "오류 없음 " + str(real_errs(errs)[:3]))
        await br.close()
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)
asyncio.run(main())
