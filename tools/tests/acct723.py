"""(v723) 🔐 아이 계정 1단계 — 진짜 Code.gs(가짜 시트) + 가짜 Firebase(규칙 흉내) 로 끝까지:
   선생님 계정 만들기(같은 이름·생일 알림) → 계정 켜기 → 아이 A: 첫 화면 → 아이디(ABC) → 비밀번호(로고 포털) → 처음 기기 승인 기다림 → 선생님 승인 → 「이 기기 기록 맞아요?」 → 서버에 올림
   → 아이 B(빈 기기): 로그인 → 승인 → A 기록 받아 옴 → B 저장 → A 가 받아 옴 → 둘 다 바꾸면 A 것은 맡겨 둠(park) → 이름 바꾸기(같은 반 막기 · 💎 안 빠짐)
   → 틀린 비밀번호 남은 기회 → 기기 내보내기 = 바로 못 씀 → 로그아웃(저장 확인 · 기기 비움 · 누가 할까요)
   node tools/tests/fake_acct_srv.js 를 띄워서 씀"""
import asyncio, sys, os, subprocess, json, urllib.request, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

PORT = 8790 + (os.getpid() % 200)
FBH = "https://hy-eng-raid-default-rtdb.asia-southeast1.firebasedatabase.app"
def http(method, path, body=None):
    req = urllib.request.Request("http://127.0.0.1:%d%s" % (PORT, path), data=(body.encode() if isinstance(body, str) else body), method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as r: return r.status, r.read().decode()
    except urllib.error.HTTPError as e: return e.code, e.read().decode()
def db(): return json.loads(http("GET", "/db")[1])

ROSTER = {"k": {"r1": {"n": "토토", "t": "t1"}, "r2": {"n": "별사탕", "t": "t1"}, "r3": {"n": "콩콩", "t": "t1"}}, "t": {"t1": {"n": "돌고래반", "e": "🐬"}}}

async def wire(pg):
    async def gs(r):
        st, body = http("POST", "/gs", r.request.post_data or "{}"); await r.fulfill(status=200, body=body, content_type="application/json")
    async def fbr(r):
        u = r.request.url; p = u[len(FBH):]
        if not (p.startswith("/kacct") or p.startswith("/kdev")): return await r.fallback()
        path, _, q = p.partition("?"); st, body = http(r.request.method, "/fb" + path + ("?" + q if q else ""), r.request.post_data)
        await r.fulfill(status=st, body=body, content_type="application/json")
    await pg.route("https://script.google.com/**", gs)
    await pg.route(FBH + "/**", fbr)

async def kid(br, errs, tag, seed=None):
    ctx = await br.new_context(viewport={"width": 390, "height": 844}); pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(tag + " " + str(e)))
    await pg.add_init_script("window.HY_FB_LOCAL=1"); await boot(pg); await wire(pg)
    await pg.evaluate("""(R)=>FB.ready().then(()=>Promise.all([FB.set('/hy/roster', R), FB.set('/hy/acon', {on:1})]))""", ROSTER)
    if seed: await pg.evaluate(seed)
    await pg.reload(); await pg.wait_for_timeout(2200)
    return ctx, pg

async def ui(pg): return await pg.evaluate("()=>{ const u=document.getElementById('acctUI'); if(!u || !u.classList.contains('on')) return ''; const s=u.querySelector('.acS.on'); return s ? s.dataset.s : '?'; }")
async def typeId(pg, s):
    for c in s: await pg.click('#acKb button[data-l="%s"]' % c); await pg.wait_for_timeout(40)
async def pin(pg, s):
    for c in s: await pg.click('#acKeys button[data-k="%s"]' % c); await pg.wait_for_timeout(60)

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    node = subprocess.Popen(["node", os.path.join(os.path.dirname(os.path.abspath(__file__)), "fake_acct_srv.js"), str(PORT)], stdout=subprocess.PIPE, text=True)
    assert "READY" in node.stdout.readline()
    try:
        async with async_playwright() as p:
            br = await p.chromium.launch()
            # ── 선생님: 계정 만들기 ──
            tctx = await br.new_context(viewport={"width": 1100, "height": 900}); tp = await tctx.new_page(); tp.on("pageerror", lambda e: errs.append("T " + str(e)))
            await tp.add_init_script("window.HY_FB_LOCAL=1"); await boot(tp); await wire(tp)
            await tp.evaluate("""(R)=>FB.ready().then(()=>FB.set('/hy/roster', R)).then(()=>{ sessionStorage.setItem('hyeng_admin_ok', String(Date.now())); sessionStorage.setItem('hyeng_admin_tk', 'TK'); localStorage.setItem('hyeng_teacher_dev','1'); })""", ROSTER)
            await tp.reload(); await tp.wait_for_timeout(2000)
            await tp.evaluate("()=>{ sessionStorage.setItem('hyeng_admin_ok', String(Date.now())); Admin.open(); }"); await tp.wait_for_timeout(800)
            await tp.evaluate("()=>{ const b=document.querySelector('#shAdmin [data-ad=tab][data-t=class]'); if(b) b.click(); }"); await tp.wait_for_timeout(1500)
            t = await tp.evaluate("()=>(document.getElementById('acAdm')||{}).innerText||''")
            ok("아이 계정" in t and "0명" in t, "관리 👥 아이들에 🔐 아이 계정 카드 (아직 0명) " + t[:80].replace("\n", " "))
            ok(not await tp.evaluate("()=>!!document.getElementById('acctUI') && document.getElementById('acctUI').classList.contains('on')"), "선생님 기기엔 아이 로그인 화면이 안 뜸")
            # (v725) 6자리 코드로 연결한 선생님 휴대폰(열쇠만 있고 「이 기기 = 선생님」은 안 누름)도 로그인 안 뜸
            pctx, pp = await kid(br, errs, "P", "()=>{ localStorage.setItem('hyeng_admin_key', 'ab'.repeat(24)); }")
            ok(await ui(pp) == "" and not await pp.evaluate("()=>!!document.getElementById('acChip')"), "연결된 선생님 휴대폰 = 로그인 화면 · 칩 없음")
            await pctx.close()
            await tp.click("#acAdm [data-acx=mk]"); await tp.wait_for_timeout(300)
            sug = await tp.evaluate("()=>[...document.querySelectorAll('#acAdm [data-mki]')].map(i=>i.dataset.mki+'='+i.value)")
            ok(len(sug) == 3 and "r1=toto" in sug and "r2=satang" in sug, "명단 아이 3명 · 아이디 자동 제안(이름 → 영어) " + str(sug))
            await tp.evaluate("""()=>{ const s=(k,id,bd)=>{ document.querySelector('#acAdm [data-mki="'+k+'"]').value=id; document.querySelector('#acAdm [data-mkb="'+k+'"]').value=bd; };
              s('r1','toto','150309'); s('r2','byul','150309'); s('r3','x1','141201'); }""")
            await tp.click("#acAdm [data-acx=mkgo]"); await tp.wait_for_timeout(1500)
            t = await tp.evaluate("()=>document.getElementById('acAdm').innerText")
            ok("만든 계정 2개" in t and "생일이 같은 친구" in t and "아이디 모양" in t, "2개 만듦 · 같은 반 같은 생일 알림 · 틀린 아이디 모양 알림")
            ok("2명" in t and "toto" in t and "아직 로그인 안 함" in t, "목록에 토토 · 아직 로그인 안 함")
            sh = json.dumps(db()["sheet"], ensure_ascii=False); ok("150309" not in sh and "141201" not in sh, "시트 「계정」에 생일 글자가 없음")
            await tp.click("#acAdm [data-acx=on]"); await tp.wait_for_timeout(900)
            ok(db()["db"].get("hy", {}).get("acon", {}).get("on") == 1, "선생님 「계정 켜기」 → 서버가 /hy/acon 켬")
            # ── 아이 A: 이 기기에 💎 기록이 있음 ──
            actx, ap = await kid(br, errs, "A", "()=>{ localStorage.setItem('hyeng_nick','토토'); Wallet.adjust(777, '시험'); return Tag.sync(); }")   # 예전부터 쓰던 기기 = 태그가 이미 있음
            ok(await ui(ap) == "home", "아이 A: 켜면 로그인 첫 화면")
            await ap.screenshot(path=OUT + "acct723_home.png")
            await ap.click('#acctUI [data-s=home] .acGold'); await ap.wait_for_timeout(400); ok(await ui(ap) == "id", "🔑 로그인 → 아이디")
            ok(await ap.evaluate("()=>document.getElementById('acIdNext').disabled"), "3글자 전엔 「다음」 못 누름")
            await typeId(ap, "toto"); await ap.screenshot(path=OUT + "acct723_id.png")
            await ap.click("#acIdNext"); await ap.wait_for_timeout(400); ok(await ui(ap) == "pw", "다음 → 비밀번호 (로고 포털)")
            await pin(ap, "150"); g = await ap.evaluate("()=>document.querySelectorAll('#acGems .acDm.on').length"); ok(g == 3, "숫자 3개 = 보석 3개 켜짐")
            await ap.screenshot(path=OUT + "acct723_pw.png")
            await pin(ap, "309")
            tg = json.dumps(db()["tags"], ensure_ascii=False); ok("토토" in tg, "(이 기기는 예전부터 토토 기기 — 태그 칸에 있음)")
            for _ in range(20):
                if await ui(ap) == "mine": break
                await ap.wait_for_timeout(400)
            ok(await ui(ap) == "mine", "예전부터 쓰던 기기(태그) = 승인 없이 → 포털 → 「이 기기에 있던 기록 · 토토 기록 맞아요?」")
            t = await ap.evaluate("()=>document.getElementById('acCmp').innerText"); ok("777" in t and "아직 비어" in t, "이 기기 💎777 · 계정은 비어 있음"); await ap.screenshot(path=OUT + "acct723_mine.png")
            await ap.click("#acctUI [data-mine=mine]")
            for _ in range(20):
                if await ui(ap) == "wel": break
                await ap.wait_for_timeout(400)
            ok(await ui(ap) == "wel", "「어서 와, 토토!」"); await ap.wait_for_timeout(1200); await ap.screenshot(path=OUT + "acct723_wel.png")
            D = db()["db"]; uid = list(D.get("kacct", {}).keys())[0] if D.get("kacct") else ""
            m = D.get("kacct", {}).get(uid, {}).get("main", {}); ok(m.get("rev") == 1 and m.get("sm", {}).get("g") == 777, "서버 /kacct/<토토>/main 에 올라감 (rev 1 · 💎777)")
            ok("hyeng_acct" not in (m.get("d") or ""), "올린 기록에 출입증·기기 비밀값이 없음")
            await ap.click('#acctUI [data-go=done]'); await ap.wait_for_timeout(300)
            st = await ap.evaluate("()=>({me:localStorage.getItem('hyeng_me'), nick:localStorage.getItem('hyeng_nick'), chip:(document.getElementById('acChip')||{}).innerText||'', cloud:Cloud.who()})")
            ok('"id":"r1"' in (st["me"] or "") and st["nick"] == "토토" and "토토" in st["chip"] and st["cloud"] is None, "로그인 = 명단 토토로 묶임(이름 고르기 안 물음) · 첫 화면 칩 · 예전 공개 ☁️ 백업 안 씀")
            await ap.screenshot(path=OUT + "acct723_start.png"); await ap.click("#acChip"); await ap.wait_for_timeout(500); ok(await ui(ap) == "me", "칩 → 내 계정"); await ap.screenshot(path=OUT + "acct723_me.png"); await ap.click('#acctUI [data-s=me] [data-go=done]'); await ap.wait_for_timeout(300)
            # 규칙: 출입증 없이 /kacct 못 읽음
            s, _ = http("GET", "/fb/kacct/%s/main.json" % uid); ok(s == 401, "출입증 없이 /kacct 못 읽음 (규칙)")
            # ── 아이 B: 빈 기기 ──
            bctx, bp = await kid(br, errs, "B")
            await bp.click('#acctUI [data-s=home] .acGold'); await typeId(bp, "toto"); await bp.click("#acIdNext"); await pin(bp, "150309"); await bp.wait_for_timeout(1500)
            ok(await ui(bp) == "wait", "아이 B(처음 쓰는 기기): 「선생님이 확인하고 있어요」")
            await bp.screenshot(path=OUT + "acct723_wait.png")
            await bp.click('#acctUI [data-go=guest]'); await bp.wait_for_timeout(300); ok(await ui(bp) == "", "「그동안 게스트로 놀기」 → 게임으로")
            await tp.click("#acAdm [data-acx=re]"); await tp.wait_for_timeout(1500)
            t = await tp.evaluate("()=>document.getElementById('acAdm').innerText"); ok("새 기기 승인 1" in t and "토토" in t, "선생님 화면에 🔔 새 기기 승인 1 (토토 · 지금 게스트로 하는 중)")
            await tp.screenshot(path=OUT + "acct723_admin.png")
            await tp.click("#acAdm [data-acx=ap]"); await tp.wait_for_timeout(500)
            for _ in range(30):
                try: g = await bp.evaluate("()=>{ try{ return Wallet.gems(); }catch(e){ return -1; } }")
                except Exception: g = -2   # 서버 기록을 받으면 새로 켜짐(reload)
                if g == 777: break
                await bp.wait_for_timeout(500)
            ok(g == 777, "승인되면 B 가 토토 기록(💎777)을 받아 옴 (빈 기기라 묻지 않음)")
            await bp.wait_for_load_state("load"); await bp.wait_for_timeout(1200)
            # B 에서 바꾸고 저장 → A 가 받아 옴
            await bp.evaluate("()=>{ Wallet.adjust(23, '시험'); }"); r = await bp.evaluate("()=>Acct.save()"); ok(r is True, "B 저장 (rev 2)")
            ok(db()["db"]["kacct"][uid]["main"]["rev"] == 2, "서버 rev 2")
            await ap.evaluate("()=>Acct.check()"); await ap.wait_for_timeout(1800)
            ok(await ap.evaluate("()=>Wallet.gems()") == 800, "A: 여기서 바뀐 게 없으면 B 기록(💎800)을 받아 옴")
            # 둘 다 바꿈 → 먼저 저장한 쪽이 남고 다른 쪽은 맡겨 둠
            await bp.evaluate("()=>{ Wallet.adjust(5, '시험'); }"); await ap.evaluate("()=>{ Wallet.adjust(100, '시험'); }")
            await bp.evaluate("()=>Acct.save()"); await ap.evaluate("()=>Acct.save()"); await ap.wait_for_timeout(1800)
            D = db()["db"]["kacct"][uid]; ok(D["main"]["sm"]["g"] == 805 and any(v.get("why") == "conflict" and v.get("sm", {}).get("g") == 900 for v in D.get("park", {}).values()), "둘 다 바꾸면 늦은 A 것(💎900)은 선생님께 맡겨 두고(park) 서버 것(💎805)을 받음")
            ok(await ap.evaluate("()=>Wallet.gems()") == 805, "A 는 서버 기록으로")
            # 이름 바꾸기 (같은 반 막기)
            g0 = await ap.evaluate("()=>Wallet.gems()")
            r = await ap.evaluate("()=>Acct.rename('별사탕')"); ok("같은 반" in r, "같은 반에 있는 이름(별사탕) = 막힘")
            ok(await ap.evaluate("()=>Wallet.gems()") == g0, "막히면 💎 안 빠짐")
            r = await ap.evaluate("()=>Acct.rename('토토로')"); ok(r == "", "다른 이름 = 됨")
            # 틀린 비밀번호 · 내보내기
            cctx, cp = await kid(br, errs, "C")
            await cp.click('#acctUI [data-s=home] .acGold'); await typeId(cp, "byul"); await cp.click("#acIdNext"); await pin(cp, "000000"); await cp.wait_for_timeout(1500)
            t = await cp.evaluate("()=>document.getElementById('acMsg').innerText"); ok("4번 남았어요" in t, "틀린 비밀번호 → 「4번 남았어요」 " + t)
            await cp.screenshot(path=OUT + "acct723_bad.png")
            await tp.click("#acAdm [data-acx=re]"); await tp.wait_for_timeout(1200)
            await tp.click('#acAdm [data-acx=op]'); await tp.wait_for_timeout(300)
            n0 = await tp.evaluate("()=>document.querySelectorAll('#acAdm [data-acx=dd]').length"); ok(n0 == 2, "토토 기기 2대 보임")
            await tp.click('#acAdm [data-acx=dd] >> nth=1'); await tp.wait_for_timeout(1000)
            r = await bp.evaluate("()=>Acct.fb('/kacct/'+Acct.get().uid+'/main/rev','GET')"); ra = await ap.evaluate("()=>Acct.fb('/kacct/'+Acct.get().uid+'/main/rev','GET')")
            ok((r.get("err") == "deny") != (ra.get("err") == "deny"), "내보낸 기기만 바로 못 씀 (출입증이 남아 있어도 규칙이 막음)")
            # 로그아웃 (A)
            r = await ap.evaluate("()=>Acct.logout()"); await ap.wait_for_timeout(2500)
            st = await ap.evaluate("()=>({on:Acct.on(), g:Wallet.gems(), ui:(document.querySelector('#acctUI .acS.on')||{}).dataset||{}, list:Acct.list().map(x=>x.id)})")
            if st["ui"].get("s") != "who": print("   (디버그)", st, await ap.evaluate("()=>({skip:sessionStorage.getItem('hyeng_acct_skip'), acon:Acct.acon, usable:Acct.usable(), uiOn:!!(document.getElementById('acctUI')&&document.getElementById('acctUI').classList.contains('on'))})"), errs[-3:])
            ok(r.get("ok") and not st["on"] and st["g"] == 0 and st["ui"].get("s") == "who" and "toto" in st["list"], "로그아웃 = 저장 확인 뒤 이 기기 비움 → 「누가 할까요?」에 토토")
            await ap.screenshot(path=OUT + "acct723_who.png")
            await ap.click('#acPpl [data-who=toto]'); await ap.wait_for_timeout(300); ok(await ui(ap) == "pw", "얼굴을 누르면 비밀번호만")
            await pin(ap, "150309"); await ap.wait_for_timeout(6000)
            for _ in range(10):
                try:
                    got = await ap.evaluate("()=>Acct.on() && Wallet.gems()")
                    if got == 805: break
                except Exception: pass
                await ap.wait_for_timeout(800)
            ok(got == 805, "다시 로그인 = 승인 없이(아는 기기) · 서버 기록 그대로 받아 옴 (💎805)")
            await br.close()
    finally:
        node.kill()
    re_ = real_errs(errs); ok(not re_, "페이지 오류 없음 " + str(re_[:3]))
    print("FAIL " + str(len(bad)) if bad else "ALL OK"); sys.exit(1 if bad else 0)

if __name__ == "__main__": asyncio.run(main())
