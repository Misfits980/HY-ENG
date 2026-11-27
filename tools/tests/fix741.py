"""(v741) 사용자 「또다른 버그는?」 · 「오락실 다른 버그들도 찾아서 고치고 올리자」
   ① 🏝 섬 📱 → 😊 표정: 줄이 바로 닫히던 것 → 열려 있음 · 다른 곳 누르면 닫힘 · 표정 고르면 닫힘
   ② 📱 앱: 열린 창 위에 새 앱 → 열려 있던 창 먼저 닫힘 (도감 → 가방 · 나 꾸미기 → 이웃)
   ③ 🎨 그려 보기: 낮은 가로 휴대폰(667×375 · 844×390)에서 굵기 줄 · 「✔ 다 그렸어요」 화면 안
   ④ 🃏 컬러팡 쌓기: 한도 8장 — 6 에서 +4 는 못 냄 (예전엔 10장까지 쌓임)
   ⑤ 🎡 낮은 가로 휴대폰(667×375) 메뉴: 그림 맞히기 · 볼링 「🏝 섬으로」가 화면 밖(반쯤) → 넘치면 줄임
   ⑥ 🃏 컬러팡 낮은 가로 휴대폰: 세 자리 이름표가 서로 · 위 차례 줄과 겹치지 않음
   ⑦ 🎡 결과 창(6명 순위 · 물총 아레나 꼴) 375×667 · 360×640: 「☰ 메뉴 · 🏝 섬으로」 화면 안
   ⑧ 🃏 컬러팡 360×640: 「✕ 나가기」 한 줄 · 위 줄(차례 · 🪙) 화면 안"""
import asyncio, sys, os, json
os.environ["HY_REAL3D"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from fakefb import fake
from draw635 import boot as dboot, menu as dmenu
from playwright.async_api import async_playwright
OUTD = OUT + "fix741/"; os.makedirs(OUTD, exist_ok=True)
bad = []
def ok(c, m):
    print(("OK  " if c else "BAD ") + m, flush=True)
    if not c: bad.append(m)
APP = """async (t)=>{ const M=document.getElementById('ihM'); if(!M || !M.offsetParent){ document.getElementById('ihMenu').click(); await new Promise(z=>setTimeout(z,350)); }
  const b=[...document.querySelectorAll('#ihM button')].find(b=>(b.textContent||'').includes(t)); if(b) b.click(); return !!b; }"""
ON = "(ids)=>ids.map(i=>{ const e=document.getElementById(i); return !!(e && e.classList.contains('on')); })"
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        # ①② 섬 (패드 세로)
        ctx, pg, errs = await dboot(br, "루아", "FX741A", vp={"width": 820, "height": 1180})
        await pg.evaluate("()=>{ const b=document.getElementById('coachSkip'); if(b && b.offsetParent) b.click(); }"); await pg.wait_for_timeout(800)
        await pg.evaluate(APP, "표정"); r = []
        for t in (400, 1200, 1500):
            await pg.wait_for_timeout(t); r.append(await pg.evaluate("()=>document.getElementById('emoBar').classList.contains('on')"))
        ok(r == [True, True, True], f"① 섬 📱 → 😊 표정: 줄이 3초 넘게 열려 있음 {r}")
        await pg.screenshot(path=OUTD + "emo.png")
        await pg.mouse.click(200, 600); await pg.wait_for_timeout(400)
        ok(not await pg.evaluate("()=>document.getElementById('emoBar').classList.contains('on')"), "① 다른 곳을 누르면 표정 줄 닫힘")
        await pg.evaluate(APP, "표정"); await pg.wait_for_timeout(600)
        await pg.evaluate("()=>document.querySelector('#emoBar [data-emo]').click()"); await pg.wait_for_timeout(500)
        ok(not await pg.evaluate("()=>document.getElementById('emoBar').classList.contains('on')"), "① 표정을 고르면 줄 닫힘")
        await pg.evaluate(APP, "도감"); await pg.wait_for_timeout(1200); await pg.evaluate(APP, "가방"); await pg.wait_for_timeout(1200)
        r = await pg.evaluate(ON, ["dexP", "bagP"])
        ok(r == [False, True], f"② 도감 위에서 가방 → 도감 닫히고 가방 [도감, 가방] {r}")
        await pg.evaluate(APP, "나 꾸미기"); await pg.wait_for_timeout(1500)
        a0 = await pg.evaluate("()=>avOpen")
        await pg.evaluate(APP, "이웃"); await pg.wait_for_timeout(1200)
        r = await pg.evaluate(ON, ["avP", "nbP", "bagP"]) + [await pg.evaluate("()=>avOpen")]
        ok(a0 and r == [False, True, False, False], f"② 나 꾸미기 위에서 이웃 → 꾸미기(카메라까지) 닫힘 [꾸미기, 이웃, 가방, avOpen] {r}")
        await pg.screenshot(path=OUTD + "apps.png")
        ok(not real_errs(errs), f"①② 오류 없음 {real_errs(errs)[:3]}")
        await ctx.close()
        # ③ 그려 보기 · 낮은 가로 휴대폰
        ctx, pg, errs = await dboot(br, "루아", "FX741B", vp={"width": 667, "height": 375}, isle=False)
        await dmenu(pg)
        await pg.evaluate("()=>MG.run.menuGo('sketch')"); await pg.wait_for_timeout(600)
        await pg.evaluate("()=>MG.run.pick(0)"); await pg.wait_for_timeout(600)
        for w, h in ((667, 375), (844, 390), (390, 844)):
            await pg.set_viewport_size({"width": w, "height": h}); await pg.wait_for_timeout(900)
            r = await pg.evaluate("""()=>{ const vis=e=>e && e.offsetParent!==null && getComputedStyle(e).display!=='none';
                const L=[...document.querySelectorAll('#mgUI .dwTl button, #mgUI .dwR button')].filter(vis), out=L.filter(e=>{ const r=e.getBoundingClientRect(); return r.bottom>innerHeight+1 || r.right>innerWidth+1 || r.left<-1; }).map(e=>(e.textContent||e.className).trim().slice(0,10));
                const done=L.find(e=>/다 그렸어요/.test(e.textContent||'')); return {n:L.length, out, done:!!done}; }""")
            ok(r["n"] >= 6 and r["done"] and not r["out"], f"③ 그려 보기 {w}×{h}: 도구·「✔ 다 그렸어요」 화면 안 {r}")
            await pg.screenshot(path=OUTD + "sketch_%dx%d.png" % (w, h))
        ok(not errs, f"③ 오류 없음 {errs[:3]}")
        await ctx.close()
        # ④ 컬러팡 쌓기 한도
        ctx, pg, errs = await dboot(br, "루아", "FX741C", isle=False)
        for _ in range(3):
            await pg.evaluate("()=>{ if(!MG.on) MG.enter('card',{}); }")
            for _ in range(80):
                if await pg.evaluate("()=>!!(MG.on && MG.run && MG.run.ready)"): break
                await pg.wait_for_timeout(200)
            if await pg.evaluate("()=>MG.on"): break
        await pg.evaluate("()=>MG.run.menuGo('solo')"); await pg.wait_for_timeout(500)
        r = await pg.evaluate("""()=>{ const R=MG.run, G=R.G, C=R.CARD; const f=(v,c)=>{ for(let id=0; id<200; id++){ let k=null; try{ k=C(id); }catch(e){} if(k && k.v===v && (c==null || k.c===c)) return k; } return null; };
            const d2=f('d2'), w4=f('wild4'); if(!d2 || !w4) return 'no card';
            const save={top:G.top, pend:G.pend}; const out=[];
            G.top=d2; for(const p of [2,4,6,8]){ G.pend=p; out.push([p, R.okC(d2), R.okC(w4)]); }
            G.top=save.top; G.pend=save.pend; return out; }""")
        ok(r == [[2, True, True], [4, True, True], [6, True, False], [8, False, False]], f"④ 컬러팡 쌓기 한도 8장: [쌓인 수, +2, +4] {r}")
        ok(not errs, f"④ 오류 없음 {errs[:3]}")
        await ctx.close()
        # ⑤⑥ 낮은 가로 휴대폰
        ctx, pg, errs = await dboot(br, "루아", "FX741D", vp={"width": 667, "height": 375}, isle=False)
        async def go(k):
            for _ in range(30):
                if not await pg.evaluate("()=>MG.on"): break
                await pg.wait_for_timeout(200)
            for _ in range(3):
                await pg.evaluate("(k)=>{ if(!MG.on) MG.enter(k,{}); }", k)
                for _ in range(80):
                    if await pg.evaluate("()=>!!(MG.on && MG.run && MG.run.ready!==false)"): break
                    await pg.wait_for_timeout(200)
                if await pg.evaluate("()=>MG.on"): break
            await pg.wait_for_timeout(900)
        for k in ("draw", "bowl", "c4", "fruit", "grid"):
            await go(k)
            r = await pg.evaluate("""()=>{ const m=[...document.querySelectorAll('#mgUI .puM')].find(e=>e.style.display!=='none'), b=m && m.querySelector('.out'); if(!b) return null; const R=b.getBoundingClientRect(), t=m.querySelector('.puTile');
                return {bot:Math.round(R.bottom), H:innerHeight, top:Math.round(R.top), tight:m.classList.contains('puTight'), tile:t?Math.round(t.getBoundingClientRect().height):0}; }""")
            ok(r and r["bot"] <= r["H"] and r["top"] >= 0, f"⑤ {k} 메뉴 667×375: 「🏝 섬으로」 화면 안 {r}")
            await pg.screenshot(path=OUTD + "menu_%s_667.png" % k)
            await pg.evaluate("()=>MG.exit()")
        await go("card"); await pg.evaluate("()=>MG.run.menuGo('solo')")
        await pg.evaluate("async ()=>{ for(let i=0;i<60;i++){ MG.step(.05,false); await null; } }"); await pg.wait_for_timeout(1500)
        r = await pg.evaluate("""()=>{ const o=document.querySelector('#mgUI .cpOrd').getBoundingClientRect(), L=[...document.querySelectorAll('#mgUI .cpPlate')].filter(e=>e.style.display!=='none').map(e=>e.querySelector('.nm').getBoundingClientRect());
            const hit=(a,b)=>a.left<b.right-2 && b.left<a.right-2 && a.top<b.bottom-2 && b.top<a.bottom-2; let pp=0, po=0; L.forEach((a,i)=>{ if(hit(a,o)) po++; L.forEach((b,j)=>{ if(j>i && hit(a,b)) pp++; }); });
            return {n:L.length, pp, po, L:L.map(a=>[Math.round(a.left),Math.round(a.top),Math.round(a.right)])}; }""")
        ok(r["n"] == 3 and r["pp"] == 0 and r["po"] == 0, f"⑥ 컬러팡 667×375: 이름표 3개 서로·차례 줄과 안 겹침 {r}")
        await pg.screenshot(path=OUTD + "card_667.png")
        ok(not errs, f"⑤⑥ 오류 없음 {errs[:3]}")
        await ctx.close()
        # ⑦ 결과 창 · 작은 세로 휴대폰
        ctx, pg, errs = await dboot(br, "루아", "FX741E", vp={"width": 375, "height": 667}, isle=False)
        await go("c4")
        for w, h in ((375, 667), (360, 640), (390, 844)):
            await pg.set_viewport_size({"width": w, "height": h}); await pg.wait_for_timeout(400)
            r = await pg.evaluate("""async ()=>{ const rk='<div class="puRank">'+['루아','Tom','Lily','4. Sam','5. Joe','6. Zoe'].map((n,i)=>'<div class="'+(i?'':'me')+'"><span>'+n+'</span><b>1 · 0</b></div>').join('')+'</div>';
                const el=PUI.result(document.getElementById('mgUI'), {res:'win', stars:3, title:'우승!', sub:'워터파크 · 83초 만에', av:{}, rewards:[['🪙','+15','코인'],['💦','0','흠뻑 적신 수'],['🔫','1/8','무기 단계']], extra:rk, prog:{t:'오늘 🪙 상 1 / 3판', v:.33}});
                await new Promise(z=>setTimeout(z, 900)); const b=[...el.querySelectorAll('.bt button')].map(e=>{ const q=e.getBoundingClientRect(); return [Math.round(q.top), Math.round(q.bottom)]; }); const c=el.className; el.remove(); return {b, H:innerHeight, c}; }""")
            ok(all(0 <= t and bt <= r["H"] for t, bt in r["b"]) and len(r["b"]) == 3, f"⑦ 결과 창 {w}×{h}: 단추 3개 화면 안 {r}")
        await pg.set_viewport_size({"width": 360, "height": 640}); await pg.evaluate("()=>MG.exit()"); await go("card"); await pg.evaluate("()=>MG.run.menuGo('solo')")
        await pg.evaluate("async ()=>{ for(let i=0;i<40;i++){ MG.step(.05,false); await null; } }"); await pg.wait_for_timeout(1200)
        r = await pg.evaluate("""()=>{ const q=s=>{ const e=document.querySelector(s); if(!e) return null; const r=e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)]; }; return {x:q('#mgUI .mgX'), ord:q('#mgUI .cpOrd'), coin:q('#mgUI .cpCoin'), W:innerWidth}; }""")
        ok(r["x"] and r["x"][3] - r["x"][1] <= 48 and r["ord"] and r["ord"][2] <= r["W"] and (not r["coin"] or r["coin"][2] <= r["W"]), f"⑧ 컬러팡 360×640: 나가기 한 줄 · 위 줄 화면 안 {r}")
        await pg.screenshot(path=OUTD + "card_360.png")
        ok(not errs, f"⑦⑧ 오류 없음 {errs[:3]}")
        await ctx.close(); await br.close()
    print("== 문제 %d" % len(bad))
    sys.exit(1 if bad else 0)
asyncio.run(main())
