"""(v584) 사용자: 「우리 파는 거 사는 게 약간 아쉬워 · 그 UI 가 진짜로」 → 🧺 가게 계산대 (shop-ui.js)
   ① 생선 가게: 같은 물고기 한 칸 ×개수 · 누르면 바구니 +1 · − 로 빼기 · 합계 = 실제 받는 🪙 · 다 담기 · 팔면 가방에서 빠짐 · 주인이 고마워요
   ② 작물·재료 팔기 · 🌱 씨앗 사기(봉투 그림 · 작물 그림이 다 다름) · 🪙 모자라면 「모자라요」 · 안 삼
   ③ 마트(씨앗·요리 재료) · 간식(담고 → 영어 맞히기 → 산다) · 휴대폰에서 창이 화면을 다 가리지 않음"""
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
        ctx=await br.new_context(viewport={"width":390,"height":844}, is_mobile=True, has_touch=True)
        pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html"); await pg.wait_for_timeout(400)
        await pg.evaluate("()=>{ localStorage.setItem('hyeng_proto_code', JSON.stringify('SHPUI')); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); }")
        await pg.reload(); await pg.wait_for_timeout(2600)
        await pg.evaluate("""()=>{ TECO.setCoin(100); bag.length=0; const t=Date.now(); [['whale',600],['fish',30],['fish',12],['fish',20],['crab',20]].forEach(([en,cm])=>bag.push({en,at:t,cm})); mats={}; addMat('carrot',3); saveBag(); openShop(); }""")
        await pg.wait_for_timeout(500)
        r=await pg.evaluate("()=>[SHOPUI.isOn(), SHOPUI.kind(), [...document.querySelectorAll('#suP .suC')].map(c=>c.dataset.id+':'+(c.querySelector('.hv')||{}).textContent)]")
        ok(r[0] and r[1]=="fish" and "fish:×3" in r[2] and len(r[2])==3, f"① 같은 물고기 한 칸 ×3 {r}")
        h=await pg.evaluate("()=>{ const s=document.getElementById('suP').getBoundingClientRect(); return [Math.round(s.top), innerHeight]; }")
        ok(h[0]>innerH_min(h[1]), f"③ 휴대폰: 창 위로 가게가 보임 (창 위 {h[0]}px) {h}")
        await pg.screenshot(path=OUT+"shopui584_fish.png")
        # 눌러 담기 · 빼기
        await pg.evaluate("()=>{ document.querySelector('#suP .suC[data-id=fish]').click(); document.querySelector('#suP .suC[data-id=fish]').click(); document.querySelector('#suP .suC[data-id=whale]').click(); }")
        r=await pg.evaluate("()=>SHOPUI.basket()")
        ok(sorted(map(tuple,r))==[("fish",2),("whale",1)], f"① 누르면 바구니 +1 {r}")
        await pg.evaluate("()=>document.querySelector('#suP .suC[data-id=fish] [data-minus]').click()")
        r=await pg.evaluate("()=>SHOPUI.basket()")
        ok(sorted(map(tuple,r))==[("fish",1),("whale",1)], f"① − 로 하나 빼기 {r}")
        await pg.evaluate("()=>{ for(let i=0;i<6;i++) document.querySelector('#suP .suC[data-id=crab]').click(); }")
        r=await pg.evaluate("()=>SHOPUI.basket().find(x=>x[0]==='crab')")
        ok(r==["crab",1], f"① 가진 것보다 많이 못 담음 {r}")
        await pg.screenshot(path=OUT+"shopui584_basket.png")
        r=await pg.evaluate("""()=>{ const btn=document.querySelector('#suP [data-go]'); const q=+btn.innerText.replace(/[^0-9]/g,''); const c0=TECO.coins(), b0=bag.length; SHOPUI.go(); return [q, TECO.coins()-c0, b0-bag.length, document.getElementById('suSay').innerText.replace(/\\s+/g,' ')]; }""")
        ok(r[0]>0 and r[0]==r[1] and r[2]==3 and "Thank" in r[3], f"① 팔기 = 합계만큼 🪙 · 가방에서 3마리 빠짐 · 주인 인사 {r}")
        r=await pg.evaluate("()=>{ document.querySelector('#suP [data-all]').click(); const n=SHOPUI.basket().reduce((s,x)=>s+x[1],0); SHOPUI.go(); return [n, bag.length]; }")
        ok(r==[2,0], f"① 🐟 다 담기 → 팔기 → 가방 비움 {r}")
        # ② 재료 · 씨앗
        await pg.evaluate("()=>SHOPUI.setTab(1)")
        r=await pg.evaluate("()=>{ const c0=TECO.coins(); SHOPUI.pick('carrot',2); SHOPUI.go(); return [mats.carrot|0, TECO.coins()>c0]; }")
        ok(r==[1,True], f"② 🥕 작물 2개 팔기 {r}")
        await pg.evaluate("()=>SHOPUI.setTab(2)")
        r=await pg.evaluate("()=>{ const C=[...document.querySelectorAll('#suP .suC .pk')].map(e=>e.textContent); return [C.length, new Set(C).size]; }")
        ok(r[0]==8 and r[1]==8, f"② 씨앗 8가지 = 봉투 그림 · 그림이 다 다름 {r}")
        await pg.screenshot(path=OUT+"shopui584_seeds.png")
        r=await pg.evaluate("()=>{ const c0=TECO.coins(), s0=mats['wheat seeds']|0; SHOPUI.pick('wheat',3); SHOPUI.go(); return [(mats['wheat seeds']|0)-s0, c0-TECO.coins()]; }")
        ok(r==[3,3], f"② wheat seeds ×3 사기 = 🪙3 {r}")
        r=await pg.evaluate("()=>{ TECO.setCoin(2); SHOPUI.pick('watermelon',1); const t=document.querySelector('#suP [data-go]').innerText; const s0=mats['watermelon seeds']|0; SHOPUI.go(); return [/모자라요/.test(t), (mats['watermelon seeds']|0)-s0, TECO.coins()]; }")
        ok(r==[True,0,2], f"② 🪙 모자라면 「모자라요」 · 안 삼 {r}")
        await pg.evaluate("()=>SHOPUI.close()")
        # ③ 마트
        await pg.evaluate("()=>{ TECO.setCoin(100); HLIFE.openMart(); }"); await pg.wait_for_timeout(300)
        r=await pg.evaluate("()=>{ SHOPUI.setTab(1); const t0=mats.tomato|0; SHOPUI.pick('tomato',2); SHOPUI.go(); return [SHOPUI.kind(), (mats.tomato|0)-t0]; }")
        ok(r==["mart",2], f"③ 🛒 마트 tomato ×2 {r}")
        await pg.evaluate("()=>SHOPUI.close()")
        await br.close()
    ok(not errs, f"오류 없음 {errs[:2]}")
    print("\nFAIL" if bad else "\nPASS", len(bad)); sys.exit(1 if bad else 0)

def innerH_min(H): return H*0.25

asyncio.run(main())
