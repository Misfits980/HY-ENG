"""(v732) 🧑‍🏫 선생님 패드 · 새 기기 잔가지
사용자: 「내 패드가 마치 공용 패드가 되어 있는 것 같은데? 영어선생님패드라고 적혀 있어 근데 0000이네 이런 오류들이 나오는 거 체크해 봐」
① 「영어선생님패드」 #0000 = 선생님 기기 (공용 패드 아님) · 게임·My Town(house.html)이 같은 판단 · 관리 🧸 카드 없음 · 이름 카드 「#0000 = 선생님 번호」
② 진짜 공용 패드(…패드 · 한양…)는 그대로 공용 · 「선생님」 이름 기기는 명단에 아이 줄을 안 만들고 로그인도 안 띄움 · 「📱 아이 기기로」 = #0000 이어도 끔
③ 계정 켜짐 · 게스트 잠금 중에 선생님 기기가 되면 잠금이 바로 풀림 (My Town 이 첫 화면으로 안 튕김)
④ 새 패드에서 선생님: My Town 은 Stage 없이 · 이름은 한 번 (「선생님」 됨)  (아이 계정 새 기기 = acct723)"""
import asyncio, sys, os, json
os.environ["HY_REAL3D"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import acct723 as A
from harness import *
from playwright.async_api import async_playwright

ST = """()=>{ let K={}; try{ K=HyBoss.kids()||{}; }catch(e){} const me=Kid.me()||{};
  return {sh:Kid.shared(), te:Kid.teacher(), ac:Acct.usable(), free:TownGate.free(), me:me.id||'', n:me.n||'', newRow:Object.values(K).filter(r=>r.nw).map(r=>r.n)}; }"""
async def dev(br, errs, tag, seed, acon=False, fake=False):
    ctx = await br.new_context(viewport={"width": 820, "height": 1180}); pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(tag + " " + str(e)))
    await pg.add_init_script("window.HY_FB_LOCAL=1;window.HY_TOWN_GATE=1;window.HY_TOWN_NAME=1;(function(S){ if(sessionStorage.getItem('_sd')) return; sessionStorage.setItem('_sd','1'); for(const k in S){ if(S[k]) localStorage.setItem(k,S[k]); else localStorage.removeItem(k); } })(" + json.dumps(seed) + ")")
    await boot(pg)
    if fake: await A.wire(pg)
    await pg.evaluate("""(o)=>FB.ready().then(()=>Promise.all([FB.set('/hy/roster', o.R), FB.set('/hy/acon', o.on ? {on:1} : null)]))""", {"R": A.ROSTER, "on": acon})
    await pg.reload(); await pg.wait_for_timeout(3000)
    await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); }")
    return ctx, pg
async def house(pg):
    """게임 안에서 My Town 으로 가는 것처럼 — house.html 을 열고 튕기는지"""
    await pg.goto(ORIGIN + "proto/house.html"); await pg.wait_for_timeout(2500)
    return pg.url.split("/")[-1]

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m, flush=True)
        if not c: bad.append(m)
    node = A.subprocess.Popen(["node", os.path.join(os.path.dirname(os.path.abspath(__file__)), "fake_acct_srv.js"), str(A.PORT)], stdout=A.subprocess.PIPE, text=True)
    assert "READY" in node.stdout.readline()
    try:
        async with async_playwright() as p:
            br = await p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
            # ① 사용자 패드 — 「영어선생님패드」 · #0000 · 공용 패드였을 때 남은 주인·고른 아이
            ctx, pg = await dev(br, errs, "T", {"hyeng_nick": "영어선생님패드", "hyeng_tag": "0000", "hyeng_pad_owner": json.dumps({"k": "r2", "n": "별사탕", "t": "t1", "at": 1})}, acon=True)
            s = await pg.evaluate(ST); print("   ", s)
            ok(not s["sh"] and s["te"] and not s["ac"] and s["free"], "① 영어선생님패드 #0000 = 공용 패드 아님 · 선생님 기기 · 아이 로그인 없음 · My Town 그냥")
            ok(s["me"].startswith("t") and s["n"] == "영어선생님패드" and not s["newRow"], "① 기록 이름 = 선생님(내 이름) · 패드 주인(별사탕)으로 안 쌓임 · 명단에 새 줄 없음")
            await pg.wait_for_timeout(600)
            ok(await pg.evaluate("()=>localStorage.getItem('hyeng_teacher_dev')") == "1", "① 처음 한 번 「선생님 기기로」 표시가 남음 (hyeng_teacher_dev=1)")
            ok(not await pg.evaluate("()=>!!(document.getElementById('acctUI')||{classList:{contains:()=>false}}).classList.contains('on') || !!document.getElementById('acChip')"), "① 계정이 켜져 있어도 로그인 창·칩 없음")
            t = await pg.evaluate("()=>{ try{ NameCard.draw(); }catch(e){} const e=document.querySelector('.nmTag'); return e ? e.innerText : ''; }")
            ok("#0000" in t and "선생님 번호" in t, "① 이름 카드 = 「#0000 = 선생님 번호」 " + t.replace("\n", " ")[:60])
            ok(await pg.evaluate("()=>NameCard.change('영어쌤') !== '공용 패드 이름은 선생님이 관리 화면에서 바꿔요'"), "① 설정에서 이름을 바꿀 수 있음 (공용 패드라 막히던 것)")
            await pg.evaluate("()=>{ try{ localStorage.setItem('hyeng_nick','영어선생님패드'); }catch(e){} }")
            await pg.evaluate("()=>{ sessionStorage.setItem('hyeng_admin_ok', String(Date.now())); sessionStorage.setItem('hyeng_admin_tk', 'TK'); }"); await pg.reload(); await pg.wait_for_timeout(2000)
            await pg.evaluate("()=>{ sessionStorage.setItem('hyeng_admin_ok', String(Date.now())); try{ Admin.open(); }catch(e){} }"); await pg.wait_for_timeout(700)
            await pg.evaluate("()=>{ const b=document.querySelector('#shAdmin [data-ad=tab][data-t=set]'); if(b) b.click(); }"); await pg.wait_for_timeout(500)
            await pg.evaluate("()=>{ const b=document.querySelector('#shAdmin [data-ad=sub][data-s=dev]'); if(b) b.click(); }"); await pg.wait_for_timeout(700)
            pc = await pg.evaluate("()=>(document.getElementById('shAdmin')||{}).innerText||''")
            if "선생님(나)" not in pc: print("   (관리)", pc[:300].replace("\n", " "))
            ok("이 패드 주인" not in pc and "선생님(나)" in pc, "① 관리 「📊 이 기기」 = 🧸 패드 주인 카드 없음 · 👑 선생님(나)")
            u = await house(pg); dk = await pg.evaluate("()=>HY_DEVK()")
            ok(u == "house.html" and dk["teacher"] and not dk["shared"], "① My Town(house.html)도 선생님 기기로 봄 · 첫 화면으로 안 튕김 " + u)
            await ctx.close()
            # ② 진짜 공용 패드 · 한양… · 「선생님」 이름 · 끈 #0000
            for nm, tg, want in (("배려패드", "0002", "sh"), ("한양키즈하우스", "", "sh"), ("선생님", "", "kid"), ("토토", "0000", "te")):
                ctx, pg = await dev(br, errs, "S", {"hyeng_nick": nm, "hyeng_tag": tg}, acon=True)
                s = await pg.evaluate(ST)
                if want == "sh": ok(s["sh"] and not s["te"] and not s["ac"], "② 「%s」 = 그대로 공용 패드" % nm)
                elif want == "kid": ok(not s["sh"] and not s["te"] and not s["ac"] and not s["newRow"], "② 「선생님」 이름(표시 없음) = 명단에 🆕 「선생님」 줄 없음 · 아이 로그인 안 띄움 %s" % s["newRow"])
                else:
                    ok(s["te"], "② #0000 = 선생님 기기")
                    await pg.evaluate("()=>Kid.setTeacher(false)"); s = await pg.evaluate(ST)
                    ok(not s["te"] and await pg.evaluate("()=>localStorage.getItem('hyeng_teacher_dev')") == "0", "② 「📱 아이 기기로」 = #0000 이어도 끔 (표시 \"0\")")
                if want == "sh":
                    await pg.evaluate("()=>TownGate.pass()"); u = await house(pg)   # 오늘 Stage 3개 한 것처럼
                    ok(u == "house.html" and await pg.evaluate("()=>window.HY_DEVK ? HY_DEVK().shared : false"), "② My Town 도 공용 패드로 봄 (" + nm + ") " + u)
                await ctx.close()
            # ③ 계정 켜짐 · 아이 개인 기기 · 「로그인 없이」 → 게스트 잠금 → 이때 선생님 기기가 됨
            ctx, pg = await dev(br, errs, "G", {"hyeng_acct_skip": ""}, acon=True, fake=True)
            await pg.evaluate("()=>{ sessionStorage.setItem('hyeng_acct_skip','1'); }"); await pg.reload(); await pg.wait_for_timeout(2800)
            g0 = await pg.evaluate("()=>({lk:Acct.locked(), gl:localStorage.getItem('hyeng_acct_glock'), chip:!!document.getElementById('acChip'), town:TownGate.ok()})"); print("   ", g0)
            ok(g0["lk"] and g0["gl"] == "1" and g0["chip"], "③ 게스트 = 🔒 잠금 · 칩")
            await pg.evaluate("()=>{ Kid.setTeacher(true); }"); await pg.wait_for_timeout(400)
            g1 = await pg.evaluate("()=>({lk:Acct.locked(), gl:localStorage.getItem('hyeng_acct_glock'), chip:!!document.getElementById('acChip'), town:TownGate.ok(), card:(document.querySelector('#selRule [data-v=town]')||{}).className||''})"); print("   ", g1)
            ok(not g1["lk"] and g1["gl"] is None and not g1["chip"] and g1["town"] and "twLock" not in g1["card"], "③ 선생님 기기가 되자마자 잠금 · 칩 · 🔒 카드가 풀림 (새로 켜기 전에도)")
            u = await house(pg); ok(u == "house.html", "③ 바로 My Town 을 열어도 첫 화면으로 안 튕김 " + u)
            await ctx.close()
            # ④ 새 패드 · 선생님 — My Town 이름은 한 번 (「선생님」 됨)
            ctx, pg = await dev(br, errs, "N", {})
            await pg.evaluate("()=>{ Kid.setTeacher(true); }"); await pg.wait_for_timeout(300)
            ok(await pg.evaluate("()=>TownGate.ok() && !TownGate.named()"), "④ 선생님 = Stage 없이 열림 · 이름은 아직")
            await pg.evaluate("()=>{ const t=document.querySelector('#selRule [data-v=town]'); if(t) t.click(); }"); await pg.wait_for_timeout(700)
            ok(await pg.evaluate("()=>!!document.getElementById('townMt')"), "④ My Town 을 누르면 이름 정하기 창")
            await pg.fill("#townMt input", "선생님"); await pg.evaluate("()=>{ const b=[...document.querySelectorAll('#townMt button')].pop(); b.click(); }"); 
            try: await pg.wait_for_url("**/house.html", timeout=12000); await pg.wait_for_timeout(800)
            except Exception: pass
            nm = await pg.evaluate("()=>localStorage.getItem('hyeng_nick')")
            ok(nm == "선생님" and "house.html" in pg.url, "④ 「선생님」 이름으로 들어감 " + str(nm) + " " + pg.url.split('/')[-1])
            await ctx.close()
            await br.close()
    finally:
        node.kill()
    re_ = real_errs(errs); ok(not re_, "페이지 오류 없음 " + str(re_[:3]))
    print("who732", "PASS" if not bad else "FAIL", len(bad))
    sys.exit(1 if bad else 0)
asyncio.run(main())
