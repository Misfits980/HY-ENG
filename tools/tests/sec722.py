"""(v722) 보안 업데이트 1 — 📱 선생님 기기 연결(관리 ⚙️ 설정 → 🔑) · 백업 가져오기는 기기 전용 칸 빼기 · 선물 받는 양 줄이기 ·
   「선생님 · 관리자」 이름 막기 · #board 길 없앰 · 서버 주소 하나 — HY_FB_LOCAL + 가짜 시트 서버(v26 흉내)"""
import asyncio, sys, os, subprocess, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

# 두 기기(탭)가 같은 가짜 서버를 씀 — 서버 상태는 테스트(파이썬) 쪽에 두고 expose_function 으로
SRV = {"legacy": "LEGACY", "off": False, "devs": [], "codes": {}, "bad": 0}
import secrets
def srv(o):
    t = o.get("type"); tk = o.get("tk") or ""
    if t == "pairUse":
        c = str(o.get("code") or "")
        if c not in SRV["codes"]: return {"ok": False, "err": "badcode"}
        del SRV["codes"][c]; k = secrets.token_hex(32); SRV["devs"].append({"k": k, "n": o.get("n") or "기기"}); return {"ok": True, "v": 26, "tk": k}
    who = None
    if tk == SRV["legacy"] and not SRV["off"]: who = "legacy"
    for i, d in enumerate(SRV["devs"]):
        if d["k"] == tk: who = i
    if who is None: return {"ok": False, "err": "badkey"}
    if t == "check": return {"ok": True, "v": 26, "legacy": who == "legacy", "off": SRV["off"], "devs": len(SRV["devs"])}
    if t == "pairSelf":
        if who != "legacy": return {"ok": False, "err": "notlegacy"}
        if SRV["devs"]: return {"ok": False, "err": "has"}
        k = secrets.token_hex(32); SRV["devs"].append({"k": k, "n": o.get("n") or "기기"}); return {"ok": True, "v": 26, "tk": k}
    if t == "pairMake":
        if who == "legacy": return {"ok": False, "err": "notme"}
        c = "%06d" % secrets.randbelow(10**6); SRV["codes"][c] = 1; return {"ok": True, "v": 26, "code": c, "ttl": 600}
    if t == "devList": return {"ok": True, "v": 26, "list": [{"i": i, "n": d["n"], "at": 1764000000000, "u": 0, "me": who == i} for i, d in enumerate(SRV["devs"])], "legacy": who == "legacy", "off": SRV["off"]}
    if t == "legacyOff":
        if who == "legacy": return {"ok": False, "err": "notme"}
        SRV["off"] = bool(o.get("on")); return {"ok": True, "v": 26, "off": SRV["off"]}
    if t == "devDel":
        i = int(o.get("i")); SRV["devs"].pop(i); return {"ok": True, "v": 26}
    return {"ok": True, "v": 26}

async def admin(ctx, errs, tag, key):
    pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(tag + " " + str(e)))
    await pg.set_viewport_size({"width": 390, "height": 844}); await pg.expose_function("_srv", srv); await boot(pg)
    await pg.evaluate("(k)=>{ sessionStorage.setItem('hyeng_admin_ok', String(Date.now())); sessionStorage.setItem('hyeng_admin_tk', k); }", key)
    await pg.reload(); await pg.wait_for_timeout(1500)
    await pg.evaluate("""(k)=>{ Online.on=()=>true; window._posts=[]; Online.submit=o=>{ window._posts.push(o); return window._srv(o); };
      Notice.fetch=()=>Promise.resolve({v:26, notices:[]}); sessionStorage.setItem('hyeng_admin_ok', String(Date.now())); sessionStorage.setItem('hyeng_admin_tk', k);
      window.confirm=()=>true; document.querySelectorAll('.sheet.on').forEach(s=>s.classList.remove('on')); }""", key)
    return pg

async def gotoKey(pg):
    await pg.evaluate("()=>{ Admin.open(); }"); await pg.wait_for_timeout(700)
    await pg.evaluate("()=>{ const b=document.querySelector('#shAdmin [data-ad=tab][data-t=set]') || document.querySelector('#shAdmin [data-ad=gear]'); if(b) b.click(); }"); await pg.wait_for_timeout(500)
    await pg.evaluate("()=>{ const b=document.querySelector('#shAdmin [data-ad=sub][data-s=key]'); if(b) b.click(); }"); await pg.wait_for_timeout(900)

async def txt(pg):
    return await pg.evaluate("()=>document.querySelector('#shAdmin').innerText")

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    # ── 시트 서버 v26 (node 로 Code.gs 를 Apps Script 흉내로) ──
    r = subprocess.run(["node", os.path.join(os.path.dirname(os.path.abspath(__file__)), "srv722.js")], capture_output=True, text=True)
    ok(r.returncode == 0 and "ALL OK" in r.stdout, "시트 서버 v26 기기 연결 흉내 시험 " + (r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-200:]))
    async with async_playwright() as p:
        br = await p.chromium.launch(); ctx = await br.new_context(has_touch=True); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        A = await admin(ctx, errs, "A", "LEGACY")
        # 관리 화면 머리 ⚙️ 단추 이름 확인
        await gotoKey(A)
        t = await txt(A)
        ok("📱 선생님 기기 연결" in t and "첫 선생님 기기로 연결" in t, "옛 열쇠 기기: 📱 「첫 선생님 기기로 연결」 보임")
        ok("ADMIN_KEY" not in t, "v26: 「ADMIN_KEY 바꾸기」 안내는 안 보임")
        await A.click('[data-ad="pairSelf"]'); await A.wait_for_timeout(1200)
        k = await A.evaluate("()=>localStorage.getItem('hyeng_admin_key')")
        ok(bool(k) and re.fullmatch(r"[0-9a-f]{64}", k or "") is not None and k == SRV["devs"][0]["k"], "첫 기기 연결 → 이 기기에 무작위 열쇠 저장")
        ok(await A.evaluate("()=>sessionStorage.getItem('hyeng_admin_tk')") == k, "지금 열쇠도 새 열쇠로")
        t = await txt(A)
        ok("6자리 코드 만들기" in t and "(이 기기)" in t, "연결 뒤: 코드 만들기 · 기기 목록(이 기기)")
        ok("옛 열쇠 끄기" in t, "🔒 옛 열쇠 끄기 단추")
        await A.click('[data-ad="pairMake"]'); await A.wait_for_timeout(900)
        code = list(SRV["codes"].keys())[0] if SRV["codes"] else ""
        t = await txt(A)
        ok(code and (code[:3] + " " + code[3:]) in t, "6자리 코드가 크게 보임 " + code)
        # ── 둘째 기기: 옛 열쇠를 끈 뒤 ──
        await A.click('[data-ad="legacyOff"]'); await A.wait_for_timeout(900)
        ok(SRV["off"] and "옛 열쇠(비밀번호로 만든 것)는 꺼져 있어요" in await txt(A), "🔒 옛 열쇠 끄기 → 꺼짐 표시")
        ctx2 = await br.new_context(has_touch=True); await ctx2.add_init_script("window.HY_FB_LOCAL=true;")   # 다른 기기 = 저장 칸 따로
        B = await admin(ctx2, errs, "B", "LEGACY")
        await gotoKey(B)
        t = await txt(B)
        ok("아직 선생님 기기로 연결되지 않았어요" in t and "6자리 코드" in t, "끈 뒤 옛 열쇠 기기: 「6자리 코드로 연결」 안내")
        await B.fill("#adPairIn", "000000" if code != "000000" else "111111"); await B.click('[data-ad="pairUse"]'); await B.wait_for_timeout(800)
        ok("코드가 맞지 않거나" in await txt(B), "틀린 코드 → 안내")
        await B.fill("#adPairIn", code); await B.click('[data-ad="pairUse"]'); await B.wait_for_timeout(1400)
        kb = await B.evaluate("()=>localStorage.getItem('hyeng_admin_key')")
        ok(kb and kb != k and kb == SRV["devs"][1]["k"], "코드로 둘째 기기 연결")
        t = await txt(B)
        ok("연결된 선생님 기기 2대" in t and "아직 선생님 기기로 연결되지" not in t, "둘째 기기: 연결됨 · 2대")
        devname = SRV["devs"][1]["n"]
        ok(bool(devname) and "·" in devname, "기기 이름 저절로 (예: 아이폰 · 사파리 · 날짜) " + devname)
        # ── 기기 빼기 ──
        await A.evaluate("()=>{ Admin.open(); }"); await A.wait_for_timeout(300); await gotoKey(A)
        await A.wait_for_timeout(800)
        ok(await A.evaluate("()=>document.querySelectorAll('#shAdmin [data-ad=devDel]').length") == 2, "첫 기기에서도 목록 2대")
        await A.click('#shAdmin [data-ad="devDel"][data-i="1"]'); await A.wait_for_timeout(900)
        ok(len(SRV["devs"]) == 1, "「빼기」 → 서버 목록에서 빠짐")
        A.on("dialog", lambda d: asyncio.ensure_future(d.dismiss()))

        # ── 백업 가져오기: 기기 전용 · 선생님 칸 빼기 ──
        K = await ctx.new_page(); K.on("pageerror", lambda e: errs.append("K " + str(e))); await boot(K, iso="K")
        out = await K.evaluate("""()=>Move.unpack('k1', {hyeng_teacher_dev:'1', hyeng_admin_key:'a'.repeat(64), hyeng_admin_tk:'x', hyeng_fb_key:'AIza', hyeng_unhook:'{}', hyeng_dev:'zz', hyeng_wallet_v1:'{"gems":5}', wgr_best:'10'})""")
        ok(sorted(out.keys()) == ["hyeng_wallet_v1", "wgr_best"], "백업 가져오기: 선생님 기기 · 관리 열쇠 · 서버 키 칸은 안 넣음 " + str(sorted(out.keys())))
        # ── 선물 받는 양 ──
        g = await K.evaluate("""async()=>{ Kid.me=()=>({id:'k1', n:'토토'}); FB.ready=()=>Promise.resolve('fb'); const g0=Wallet.gems();
            FB.get=()=>Promise.resolve({a:{at:1,g:99999,from:'x'}, b:{at:2,g:99999}, c:{at:3,p:9999999}}); FB.set=()=>Promise.resolve();
            try{ Kid.guest=()=>null; await Gift.recv(); }catch(e){ return "err "+e; } return Wallet.gems()-g0; }""")
        ok(isinstance(g, int) and 0 < g <= 2000, f"선물 한 번에 💎2000 까지 (받은 것 {g})")
        # ── 이름 막기 ──
        r1 = await K.evaluate("()=>NameCard.change('선생님')"); r2 = await K.evaluate("()=>NameCard.change('관 리 자')"); r3 = await K.evaluate("()=>NameCard.change('Admin')")
        ok(all("쓸 수 없어요" in (x or "") for x in [r1, r2, r3]), "「선생님 · 관 리 자 · Admin」 이름 막기")
        r4 = await K.evaluate("()=>NameCard.change('별사탕')")
        ok(r4 == "", "보통 이름은 그대로 됨")
        r5 = await K.evaluate("()=>{ localStorage.setItem('hyeng_teacher_dev','1'); const r=NameCard.change('선생님'); localStorage.removeItem('hyeng_teacher_dev'); return r; }")
        ok(r5 == "" or "보석" in (r5 or ""), "선생님 기기는 「선생님」 이름 됨 " + str(r5))
        # ── #board 길 ──
        await K.goto(ORIGIN + "index.html#board"); await K.wait_for_timeout(1500)
        ok(await K.evaluate("()=>localStorage.getItem('hyeng_board_try')") is None, "#board 주소로 점검 중 보드게임 열기 없앰")
        ok(await K.evaluate("()=>FB_URLS.length===1 && /asia-southeast1/.test(FB_URLS[0])"), "서버 주소 = 아시아 하나")
        await br.close()
    # ── 마을 대화 이름 (house.html 의 VC_STAFF 그대로) ──
    src = open(os.path.join(SITE, "proto/house.html"), encoding="utf-8").read()
    line = [l for l in src.splitlines() if l.startswith("const VC_STAFF=")][0]
    r = subprocess.run(["node", "-e", line + "\nconsole.log(JSON.stringify(['선생님','관리 자','토토','teacher','쌤이야','원장','콩콩'].map(vcNm)))"], capture_output=True, text=True)
    ok(r.stdout.strip() == '["친구","친구","토토","친구","친구","원장","콩콩"]', "마을 대화: 선생님 같은 이름 → 「친구」 " + r.stdout.strip())
    E = real_errs(errs); ok(not E, "페이지 오류 없음 " + str(E[:3]))
    print("FAIL", len(bad), bad) if bad else print("ALL OK")
    sys.exit(1 if bad else 0)

if __name__ == "__main__": asyncio.run(main())
