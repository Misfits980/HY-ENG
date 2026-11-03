"""(v570) 사용자: 「곧 겨울이니까 벽난로 같은 것 · 미니멀 라이프(그냥 방에 스토브 같은 것)도 고려해서 가구 · 낚시 생물도 더」
   ① 새 가구 15개 = 가게에 있고 그려짐(오류 없음) · 겨울 방 사진  ② 🏠 원룸 주방 = 요리(부엌 열기 뒤) · 작은 냉장고 = 냉장고 · 소파 침대·바닥 침대 = 잠
   ③ 새 생물 13 · 계절(mon): 겨울엔 🧤🧣·🦢 · 여름 생물은 안 나옴 · 「오늘의 물고기」 도 철인 것만"""
import asyncio, sys, os
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from fakefb import fake
from playwright.async_api import async_playwright

NEW=["woodstove","heater","firewood","armchair","wreath","stockings","snowrug","sled","cocoa","kitchenette","minifridge","sofabed","futon","lowtable","cushion"]

async def main():
    bad=[]; errs=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        ctx=await br.new_context(viewport={"width":820,"height":1180}, has_touch=True)
        pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html"); await pg.wait_for_timeout(400)
        await pg.evaluate("""()=>{ localStorage.setItem('hyeng_proto_code', JSON.stringify('WINTR')); localStorage.setItem('hyeng_nick','루아'); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99}));
            localStorage.setItem('hyeng_study_v1', JSON.stringify({days:{n:8,tot:9,hs:8,hb:8,last:Math.floor((Date.now()-new Date().getTimezoneOffset()*60000)/864e5)}})); }""")
        await pg.reload(); await pg.wait_for_timeout(3000)
        r=await pg.evaluate("(L)=>L.map(id=>[id, !!HOUSE.PRICE[id], (()=>{ try{ return !!ITEMS[id].build(0); }catch(e){ return String(e); } })(), JSON.stringify(furnCO(id))])", NEW)
        okAll=all(x[1] and x[2] is True for x in r)
        ok(okAll and len(r)==15, f"① 새 가구 15개 = 가게에 있고 그려짐 {[x[0]+':'+x[3] for x in r]}")
        r=await pg.evaluate("()=>[JSON.stringify(furnCO('kitchenette')), JSON.stringify(furnCO('minifridge'))]")
        ok(r==['{"g":0,"c":380}','{"g":0,"c":220}'], f"② 원룸 주방 🪙380 · 작은 냉장고 🪙220 (🪙만) {r}")
        # 겨울 방 꾸미기 사진
        await pg.evaluate("""()=>{ growRoom(8); placed.slice().forEach(p=>{ try{ removePlaced ? removePlaced(p) : 0; }catch(e){} });
            const put=(id,x,z,r)=>{ try{ if(fits(id,x,z,r||0)) addPlaced(id,x,z,r||0,0); }catch(e){ console.warn(e); } };
            put('fireplace',3,0); put('woodstove',0,0); put('firewood',1,0); put('armchair',2,2); put('snowrug',3,2); put('cocoa',5,2); put('sled',7,1); put('heater',7,4);
            put('kitchenette',0,5); put('minifridge',0,6); put('lowtable',3,5); put('cushion',2,5); put('cushion',4,5); put('futon',6,5); put('sofabed',5,4);
            ['wreath','stockings'].forEach((id,i)=>{ try{ addWall(id, 0, 2+i*3, 0); }catch(e){ console.warn(e); } }); saveRoom(); placeCamera(); }""")
        await pg.wait_for_timeout(1200)
        await pg.screenshot(path=OUT+"winter570_room.png")
        # ② 쓰기
        await pg.evaluate("()=>{ HOMEX.H().o.kitchen=1; }")
        await pg.evaluate("()=>{ const p=placed.find(p=>p.id==='kitchenette'); if(p) useItem(p); }"); await pg.wait_for_timeout(300)
        ok(await pg.evaluate("()=>document.getElementById('craftP').classList.contains('on')"), "② 🏠 원룸 주방을 누르면 🍳 요리 (부엌 연 뒤)")
        await pg.evaluate("()=>{ document.getElementById('craftP').classList.remove('on'); const p=placed.find(p=>p.id==='minifridge'); if(p) useItem(p); }"); await pg.wait_for_timeout(300)
        ok(await pg.evaluate("()=>document.getElementById('stoP').classList.contains('on')"), "② 🧊 작은 냉장고 = 냉장고 보관")
        await pg.evaluate("()=>{ document.getElementById('stoP').classList.remove('on'); const p=placed.find(p=>p.id==='heater'); if(p) useItem(p); }"); await pg.wait_for_timeout(200)
        ok(await pg.evaluate("()=>{ const p=placed.find(p=>p.id==='heater'); return !!(p && p.on); }"), "♨️ 히터 켜기")
        ok(await pg.evaluate("()=>ITEMS.sofabed.sit==='sleep' && ITEMS.futon.sit==='sleep'"), "② 소파 침대 · 바닥 침대 = 잘 수 있음")
        # ③ 생물
        r=await pg.evaluate("""()=>{ const N=['clownfish','pufferfish','oyster','swan','hippo','snake','dragon','ring','crown','key','mitten','scarf','leaf']; const has=N.filter(n=>FISH_BY[n] && SPEC[n]);
            const mon=m=>{ const real=now; const base=Date.UTC(2026,m-1,15,3)-9*3600e3; tShift=base-Date.now(); const a=FISH.filter(f=>canAppear(f)).map(f=>f.en); const t=todaySp().en; tShift=0; return [a, t]; };
            const [w,tw]=mon(1), [s,ts]=mon(7);
            const mOK=(n,m)=>!SPEC[n].mon || SPEC[n].mon.includes(m);
            return [has.length, w.includes('mitten')&&w.includes('scarf')&&mOK('swan',1)&&mOK('dragon',1), !w.includes('hippo')&&!w.includes('clownfish'), s.includes('clownfish')&&mOK('hippo',7)&&!s.includes('mitten')&&!mOK('swan',7),
              (SPEC[tw].mon||[1]).includes(1), (SPEC[ts].mon||[7]).includes(7), FISH.length]; }""")
        ok(r[0]==13 and r[1] and r[2] and r[3] and r[4] and r[5], f"③ 새 생물 13 · 1월 = 🧤🧣🦢 (🦛🐠 없음) · 7월 = 🦛🐠 (🧤 없음) · 오늘의 물고기도 철 {r}")
        await pg.evaluate("()=>{ openFurn('furn'); furnCat='season'; drawFurn(); }"); await pg.wait_for_timeout(400)
        await pg.screenshot(path=OUT+"winter570_shop.png")
        await br.close()
    ok(not errs, f"오류 없음 {errs[:2]}")
    print("\nFAIL" if bad else "\nPASS", len(bad)); sys.exit(1 if bad else 0)

asyncio.run(main())
