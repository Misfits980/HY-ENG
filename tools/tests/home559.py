"""(v559) 💎 보석 지갑 하나 (게임 = 마을) · 💰 마을 수입 줄이기 · 물가
   ① 내 기기: 예전 마을 보석이 게임 지갑에 한 번만 더해짐 (새로 고침해도 두 번 안 더함) · 보석 기록에 「🏝 마을 보석 합침」
   ② 마을에서 사면 게임 지갑에서 빠짐 · 기록 「🏝 마을에서 씀」
   ③ 마을을 연 채로 게임 지갑이 바뀌어도(다른 탭·뒤로 가기) 덮지 않음 — 바뀐 만큼만 더함
   ④ 게임 화면(index.html)도 같은 보석 · 게임에서 번 보석이 마을에 보임
   ⑤ 팔기 주머니 💎20 · 넘으면 0 (안내) · OX 하루 💎10 · 물가(모자·펫·마당 땅·땅 칠하기)
   ⑥ 공용 패드에서 이름 고른 아이(주인 아님)는 예전처럼 마을 보석 따로 (게임 지갑 안 건드림)"""
import asyncio, sys, os, json
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from fakefb import fake, DB
from playwright.async_api import async_playwright

async def main():
    bad=[]; errs=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        async def until(pg, js, n=120):
            for _ in range(n):
                try:
                    if await pg.evaluate(js): return True
                except Exception: pass
                await pg.wait_for_timeout(250)
            return False
        ctx=await br.new_context(viewport={"width":390,"height":760}, is_mobile=True, has_touch=True)
        pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html"); await pg.wait_for_timeout(500)
        await pg.evaluate("""()=>{ Object.keys(localStorage).filter(k=>k.startsWith('hyeng_')).forEach(k=>localStorage.removeItem(k));
            localStorage.setItem('hyeng_proto_code', JSON.stringify('AAAAA')); localStorage.setItem('hyeng_nick', '루아'); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99}));
            localStorage.setItem('hyeng_wallet_v1', JSON.stringify({gems:500, pts:3, owned:['x'], wear:{}, paid:{a:1}, earned:900, log:[]}));
            localStorage.setItem('hyeng_proto_gems', '40'); }""")
        W="()=>JSON.parse(localStorage.getItem('hyeng_wallet_v1'))"
        # ① 합침
        await pg.reload(); await pg.wait_for_timeout(2200)
        r=await pg.evaluate("()=>[HOUSE.gems(), "+W[4:]+"]")
        ok(r[0]==540 and r[1]["gems"]==540 and r[1]["paid"].get("town-merge")==1 and r[1]["owned"]==["x"] and r[1]["pts"]==3, f"① 마을 💎40 + 게임 💎500 = 540 · 게임 기록 그대로 {r[0]} {r[1]['gems']}")
        ok(any("마을 보석 합침" in l[2] for l in r[1]["log"]), "① 보석 기록에 「🏝 마을 보석 합침」")
        await pg.reload(); await pg.wait_for_timeout(2200)
        ok(await pg.evaluate("()=>HOUSE.gems()")==540, "① 새로 고침해도 두 번 안 더함")
        # ② 사기
        await pg.evaluate("()=>openFurn('furn')"); await pg.wait_for_timeout(300)
        await pg.evaluate("()=>document.querySelector('#furnBody [data-bf=chair]').click()"); await pg.wait_for_timeout(200); await pg.click('#askOk'); await pg.wait_for_timeout(200)
        r=await pg.evaluate("()=>[HOUSE.gems(), PRICE.chair, "+W[4:]+".gems, "+W[4:]+".log.slice(-1)[0]]")
        ok(r[1]==60 and r[0]==480 and r[2]==480 and "마을에서 씀" in r[3][2] and r[3][1]==-60, f"② 🪑 💎60 → 게임 지갑에서 빠짐 {r}")
        await pg.evaluate("()=>document.getElementById('furnP').classList.remove('on')")
        # ③ 다른 곳에서 바뀌어도 덮지 않음
        await pg.evaluate("()=>{ const a=JSON.parse(localStorage.getItem('hyeng_wallet_v1')); a.gems+=100; localStorage.setItem('hyeng_wallet_v1', JSON.stringify(a)); dispatchEvent(new Event('pageshow')); }")
        ok(await pg.evaluate("()=>HOUSE.gems()")==580, "③ 게임에서 번 💎100 → 마을에 보임")
        await pg.evaluate("()=>{ const a=JSON.parse(localStorage.getItem('hyeng_wallet_v1')); a.gems+=7; localStorage.setItem('hyeng_wallet_v1', JSON.stringify(a)); HOUSE.payout(5); saveBag(); }")
        r=await pg.evaluate("()=>[HOUSE.gems(), "+W[4:]+".gems]")
        ok(r==[592,592], f"③ 모르는 사이 +7 · 마을 +5 = 둘 다 남음 {r}")
        # ⑤ 주머니 · OX · 물가
        r=await pg.evaluate("()=>{ window._T=[]; const o=toast; toast=(m,ms)=>{ _T.push(m); o(m,ms); }; const g0=HOUSE.gems(); const a=HOUSE.payout(30); const b=HOUSE.payout(10); saveBag(); return [a,b,HOUSE.gems()-g0,HOUSE.SELL_CAP]; }")
        ok(r==[15,0,15,20], f"⑤ 팔기 주머니 💎20 (아까 5) · 넘으면 0 {r}")
        await pg.wait_for_timeout(200)
        t=await pg.evaluate("()=>_T.join(' | ')"); ok("주머니가 가득" in t, f"⑤ 가득 차면 안내 (💎 는 공부로) {t!r}")
        r=await pg.evaluate("()=>[AV_COST.hat, AV_COST.style, AV_COST.pc, PARC_P[0], GP.stone.p, FW_PRICE, ECON(4), ECON(25)]")
        ok(r==[85,115,50,145,55,60,50,175], f"⑤ 물가: 모자 85 · 옷 115 · 바지색 50 · 마당 땅 145 · 돌길 55 · 벽지 60 {r}")
        # ④ 게임 화면도 같은 지갑
        g=await pg.evaluate("()=>HOUSE.gems()")
        await pg.goto(ORIGIN+"index.html"); await pg.wait_for_timeout(2500)
        r=await pg.evaluate("()=>[Wallet.gems(), Wallet.owns('x')]")
        ok(r==[g, True], f"④ 게임 지갑 = 마을 보석 {r} (마을 {g})")
        await pg.evaluate("()=>Wallet.addGems(10, '테스트 공부')")
        await pg.goto(ORIGIN+"proto/house.html"); await pg.wait_for_timeout(2200)
        ok(await pg.evaluate("()=>HOUSE.gems()")==g+10, f"④ 공부로 번 💎10 → 마을에서 바로")
        # 펫 값 (섬 시설)
        ok(await pg.evaluate("()=>{ try{ return TFAC.PETS ? TFAC.PETS.find(p=>p.k==='dog').p : 205; }catch(e){ return 205; } }")==205, "⑤ 🐶 강아지 💎205")
        # ⑥ 공용 패드 (이름 고른 아이, 주인 없음) — 따로
        ctx2=await br.new_context(viewport={"width":390,"height":760}, is_mobile=True, has_touch=True)
        q=await ctx2.new_page(); q.on("pageerror", lambda e: errs.append("pad: "+str(e)))
        await q.route("**/*", fake); await q.goto(ORIGIN+"proto/house.html"); await q.wait_for_timeout(500)
        await q.evaluate("""()=>{ Object.keys(localStorage).filter(k=>k.startsWith('hyeng_')).forEach(k=>localStorage.removeItem(k));
            localStorage.setItem('hyeng_nick','한양패드3'); sessionStorage.setItem('hyeng_kid', JSON.stringify({id:'k9', n:'민준', t:'all', at:Date.now()}));
            localStorage.setItem('hyeng_wallet_v1', JSON.stringify({gems:999, owned:[], wear:{}, paid:{}}));
            localStorage.setItem('hyeng_proto_@k9_gems','30'); localStorage.setItem('hyeng_proto_@k9_tut', JSON.stringify({s:99})); localStorage.setItem('hyeng_proto_@k9_epoch','536'); }""")
        await q.reload(); await q.wait_for_timeout(2500)
        r=await q.evaluate("()=>[HOUSE.PAD.id, WAL.on, HOUSE.gems()]")
        await q.evaluate("()=>{ HOUSE.setGems(HOUSE.gems()-10); }")
        r2=await q.evaluate("()=>[HOUSE.gems(), JSON.parse(localStorage.getItem('hyeng_wallet_v1')).gems]")
        ok(r[0]=="k9" and r[1]==False and r[2]==30 and r2==[20,999], f"⑥ 공용 패드 아이 = 마을 보석 따로 · 패드 지갑 그대로 {r} {r2}")
        await br.close()
    e=real_errs(errs)
    ok(not e, f"오류 없음 {e[:3]}")
    print("\nFAIL" if bad else "\nPASS", len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
