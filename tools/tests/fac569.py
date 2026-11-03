"""(v569) 사용자: 「부엌 시설 오픈에 다이아를 쓰게 하고 기구는 따로 더 받아야 하는 거 아니야?」
   ① 💎 = 🍳 부엌 · 🛏️ 침실 · 🛁 욕실 「열기」 (기구 안 줌)  ② 기구는 가구 가게에서 🪙 (🛁 욕조도 팖 · 안 열었으면 🔒 표시)
   ③ 안 열고 스토브·냉장고·욕조를 누르면 「먼저 열어야 해요」 + 넓히기 창  ④ 예전에 기구가 있던 아이는 그 시설이 열린 것으로 (한 번)"""
import asyncio, sys, os
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from fakefb import fake
from playwright.async_api import async_playwright

async def main():
    bad=[]; errs=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        async def kid(code, pre):
            ctx=await br.new_context(viewport={"width":390,"height":844}, is_mobile=True, has_touch=True)
            pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
            await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html"); await pg.wait_for_timeout(400)
            await pg.evaluate("""([c,pre])=>{ localStorage.setItem('hyeng_proto_code', JSON.stringify(c)); localStorage.setItem('hyeng_nick','루아'); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99}));
                localStorage.setItem('hyeng_study_v1', JSON.stringify({days:{n:8,tot:9,hs:8,hb:8,last:Math.floor((Date.now()-new Date().getTimezoneOffset()*60000)/864e5)}}));
                if(pre) localStorage.setItem('hyeng_proto_room', JSON.stringify({p:[], wl:[], f:0, w:0, rn:6, s:{bed:1, desk:1, stove:1, bathtub:1}})); }""", [code, pre])
            await pg.reload(); await pg.wait_for_timeout(3000); return pg
        # ④ 예전 아이: 스토브·욕조가 창고에 있었음
        O=await kid("OLDKD", True)
        r=await O.evaluate("()=>[HOMEX.facOK('kitchen'), HOMEX.facOK('bath'), HOMEX.facOK('bedroom'), HOMEX.H().fm]")
        ok(r==[True,True,False,569], f"④ 예전에 스토브·욕조가 있던 아이 = 부엌·욕실 열림 (침실은 아님) {r}")
        # 새 아이
        A=await kid("NEWKD", False)
        r=await A.evaluate("()=>[HOMEX.facOK('kitchen'), HOMEX.facOK('bath'), HOMEX.facOK('bedroom')]")
        ok(r==[False,False,False], f"새 아이 = 시설 안 열림 {r}")
        # ② 가구 가게: 욕조 팖 · 🔒 표시
        await A.evaluate("()=>{ TECO.setCoin(2000); openFurn('furn'); furnCat='all'; drawFurn(); }"); await A.wait_for_timeout(300)
        r=await A.evaluate("()=>{ const row=id=>{ const b=document.querySelector('#furnBody [data-bf='+id+']'); return b ? b.closest('.sRow').innerText : ''; }; return [row('stove'), row('bathtub'), !!HOUSE.PRICE.bathtub]; }")
        ok("🔒" in r[0] and "부엌" in r[0] and "🪙300" in r[0].replace(" ","") and "💎" not in r[0].split("써요")[1] and "🔒" in r[1] and "🪙450" in r[1].replace(" ","") and r[2], f"② 가구 가게에 🍳 stove · 🛁 bathtub (🪙) · 안 열었으면 「🔒 … 열기 하면 써요」 {[x[:60] for x in r[:2]]}")
        # ③ 안 열고 스토브 누르기
        await A.evaluate("()=>{ document.getElementById('furnP').classList.remove('on'); addStock('stove'); for(let x=0;x<RN;x++) for(let z=0;z<RN-1;z++){ if(stock.stove>0 && fits('stove',x,z,0)){ addPlaced('stove',x,z,0,0); stock.stove--; } } useItem(placed.find(p=>p.id==='stove')); window._t=document.getElementById('toast').innerText; }")
        await A.wait_for_timeout(1300)
        r=await A.evaluate("()=>[window._t, document.getElementById('craftP').classList.contains('on'), !!(document.getElementById('upP')||{classList:{contains:()=>false}}).classList.contains('on')]")
        ok("부엌" in r[0] and not r[1] and r[2], f"③ 안 열고 스토브 → 「🍳 부엌을 먼저 열어야 해요」 · 요리 창 안 열림 · 넓히기 창 {r}")
        # ① 열기 = 💎 · 기구 안 줌 · 그 뒤 요리 됨
        r=await A.evaluate("()=>{ document.getElementById('upP').classList.remove('on'); gems=1000; saveBag(); const s0=stock.fridge|0; HOMEX.unlock('kitchen'); return [HOMEX.facOK('kitchen'), HOUSE.gems(), (stock.fridge|0)-s0]; }")
        ok(r==[True,600,0], f"① 🍳 부엌 열기 💎400 · 기구는 안 들어옴 {r}")
        await A.evaluate("()=>useItem(placed.find(p=>p.id==='stove'))"); await A.wait_for_timeout(400)
        ok(await A.evaluate("()=>document.getElementById('craftP').classList.contains('on')"), "① 연 뒤 스토브 → 🍳 요리 창")
        await A.evaluate("()=>{ HOMEX.openUp(); }"); await A.wait_for_timeout(300)
        t=await A.evaluate("()=>document.querySelector('[data-row=kitchen]').innerText + ' | ' + document.querySelector('[data-row=bath]').innerText")
        ok("열림" in t and "열기" in t and "가구 가게" in t, f"넓히기 창 = 「🔓 시설 열기」 · ✅ 열림 · 기구는 가구 가게 안내 {t[:120]!r}")
        await A.screenshot(path=OUT+"fac569_up.png")
        await br.close()
    ok(not errs, f"오류 없음 {errs[:2]}")
    print("\nFAIL" if bad else "\nPASS", len(bad)); sys.exit(1 if bad else 0)

asyncio.run(main())
