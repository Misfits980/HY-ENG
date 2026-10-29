"""(v452) 사용자 그림 — 새 미니게임 9개 엠블럼 · 배경 6 · 부품(과일·점프·탑·신호등·로켓·10초·숫자 타일·물고기) · 메달 · 황금 주사위 (유아 k / 초등 e)
   그림이 하나도 안 깨지고(naturalWidth>0) · 게임마다 제 그림을 쓰는지"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright
NAMES = ("em_tug em_light em_paint em_fish em_stop em_num em_fruit em_stack em_jump fr_basket fr_apple fr_banana fr_grape fr_berry fr_orange fr_melon fr_peach fr_gold fr_bomb fr_splat fr_spark "
         "jp_run jp_jump jp_cactus jp_rock jp_box jp_ground st_base st_block st_gold st_chip fx_dust fx_spark lt_off lt_r lt_y lt_g tg_rocket tg_rope tg_flagr tg_flagb sp_watch nu_tile nu_ok nu_no "
         "fi_o fi_b fi_g fi_hook pt_roller pt_bucket pt_splat pt_brush pod md_1 md_2 md_3 dice_gold rb_red rb_gold confetti bg_tug bg_light bg_paint bg_fish bg_fruit bg_jump").split()
async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m, flush=True)
        if not c: bad.append(m)
    miss = [sk + "/" + n for sk in "ke" for n in NAMES if not os.path.isfile(os.path.join(SITE, "assets", "mg", sk, n + ".webp"))]
    ok(not miss, f"그림 파일 {len(NAMES)}×2 모두 있음 {miss[:5]}")
    async with async_playwright() as p:
        br = await p.chromium.launch()
        pg = await br.new_page(viewport={"width": 1024, "height": 768}); pg.on("pageerror", lambda e: errs.append(str(e)))
        await boot(pg); E = pg.evaluate
        await E("()=>{ window.HY_NOHOW=true; }")
        r = await E("()=>[MiniG.ACT.concat(MiniG.ENG).map(k=>MiniG.em(k)), MiniG.bg('stack'), MiniG.bg('fruit'), MiniG.bg('stop')]")
        ok(r[0][2:] == ["tug","light","paint","stop","num","fruit","stack","jump","ox","memory","fish"] and r[1:] == ["jump","fruit","party"], f"엠블럼 = 게임마다 전용 · 배경 🧱→점프 · ⏱→party {r}")
        OPEN = """([k,sk])=>{ const c={set:'elem',from:0,to:3,words:[],qt:['mean']}, x=Object.create(Battle); x._ws=null; x.cfg=()=>c;
            const P=[{n:'루아',ch:0},{n:'주호',ch:3}].map((p,i)=>Object.assign(p,{i,col:Board.COL[i]}));
            MG.open({title:MiniG.L[k][0], sub:MiniG.L[k][1], P, ctx:x, kind:k, sec:20, sk}, sc=>0); }"""
        WANT = {"tug": ".mgTugR img[src$='tg_rocket.webp']", "light": ".mgLtL.img img[src$='lt_g.webp']", "fruit": ".mgBk img[src$='fr_basket.webp']",
                "jump": ".mgJpC img[src$='jp_jump.webp']", "stop": ".mgSwT.img", "fish": ".mgSea", "num": ".mgNu button", "stack": ".mgStB.base", "paint": ".mgPt i"}
        for sk in "ke":
            for k, sel in WANT.items():
                await E(OPEN, [k, sk])
                for _ in range(40):
                    if await E("()=>!document.querySelector('.mgIntro') && MG.o && MG.o.inst"): break
                    await pg.wait_for_timeout(150)
                await pg.wait_for_timeout(1300)
                for _ in range(3): await E("()=>{ try{ MG.o.inst[0].auto(); }catch(e){} }")
                await pg.wait_for_timeout(500)
                r = await E("""(sel)=>{ const d=document.getElementById('bdMG'); const im=[...d.querySelectorAll('img')]; const br=im.filter(i=>i.complete && !i.naturalWidth).map(i=>i.src.split('/').slice(-2).join('/'));
                    const g=d.querySelector('.mgG'), v=getComputedStyle(g).getPropertyValue('--mgI-nu_tile'); return [!!d.querySelector(sel), br, /assets\\/mg\\/"""+sk+"""\\/nu_tile/.test(v), d.querySelector('.mgIntro')?1:0, getComputedStyle(d).getPropertyValue('--mgParty')]; }""", sel)
                ok(r[0] and not r[1] and r[2], f"{sk} {k}: 제 그림 · 깨진 그림 없음 · 자리에 그림 주소 {r[:3]}")
                if k == "fruit":
                    r2 = await E("()=>[...document.querySelectorAll('#bdMG .mgFt img')].map(i=>i.src.split('/').pop())")
                    ok(len(r2) > 0 and all(x.startswith("fr_") for x in r2), f"{sk} 과일 = 그림 {r2[:4]}")
                if k == "jump":
                    r2 = await E("()=>[...document.querySelectorAll('#bdMG .mgJpO img')].map(i=>i.src.split('/').pop())")
                    ok(all(x in ("jp_cactus.webp","jp_rock.webp","jp_box.webp") for x in r2), f"{sk} 장애물 = 그림 {r2[:4]}")
                if k == "fish":
                    r2 = await E("()=>[...document.querySelectorAll('#bdMG .mgFi')].map(f=>[f.classList.contains('img'), f.style.getPropertyValue('--fb')])")
                    ok(len(r2) > 0 and all(a and b.startswith("var(--mgI-fi_") for a, b in r2), f"{sk} 물고기 = 그림 {r2[:2]}")
                await E("()=>MG.close()")
        # 메달 · 황금 주사위
        r = await E("""()=>{ const h=Board.podHtml('t',[{i:0,n:'a',ch:0,col:'#f00',sc:3,c:10,r:1},{i:1,n:'b',ch:1,col:'#00f',sc:2,c:5,r:2}]); return [(h.match(/md_[123]\\.webp/g)||[]).length, Board.ic('gold').indexOf('dice_gold.webp')>0]; }""")
        ok(r[0] >= 2 and r[1], f"🥇🥈 → 메달 그림 · 🎯 황금 주사위 그림 {r}")
        await br.close()
    r = real_errs(errs)
    print("errs", r)
    if bad or r: print("FAILED", bad); sys.exit(1)
    print("ALL OK")
asyncio.run(main())
