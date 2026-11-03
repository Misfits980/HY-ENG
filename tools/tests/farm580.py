"""(v580) 사용자:
   ① 「기차가 있는데 지도로 텔포하면 기차 의미가 있을까 · 집 가는 거랑 광산은 하게 해 줘」 → 지도 🚀 = ⭐ 내 집(무료)·⛏ 광산(🪙)만 · 먼 곳 = 🚶/🚉 기차역으로
   ② 「마당에 자유롭게 땅을 가꾸게」 → 꾸미기 🌱 밭 일구기: 빈 풀밭 = 밭 · 빈 밭 = 풀밭 · 칸 수(plotN)까지 · 🪙 로 늘리면 새 칸 자동 · 저장 · 친구 마당엔 친구 밭 자리
   ③ 「개인 연못에는 작은 물고기만」 → 마당 연못 = 40cm 이하·잡동사니만 (고래·상어·보물 없음) · 섬 호수는 그대로"""
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
        await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html?isle=1"); await pg.wait_for_timeout(400)
        await pg.evaluate("()=>{ localStorage.setItem('hyeng_proto_code', JSON.stringify('FARM8')); localStorage.setItem('hyeng_nick','루아'); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); }")
        await pg.reload(); await pg.wait_for_timeout(2800)
        # ③ 연못
        r=await pg.evaluate("""()=>{ const out={}; go('yard', [DOOR[0],DOOR[1]+1]); return 1; }""")
        await pg.wait_for_timeout(2200)
        r=await pg.evaluate("""()=>{ const W=n=>fishW(FISH_BY[n]); return [place===PL.yard, W('whale'), W('shark'), W('treasure'), W('crown'), W('fish')>0, W('frog')>0, W('crab')>0, W('can')>0]; }""")
        ok(r[0] and r[1:5]==[0,0,0,0] and all(r[5:]), f"③ 마당 연못: 고래·상어·보물·왕관 0 · 물고기·개구리·게·캔은 나옴 {r}")
        # ② 밭 일구기
        r=await pg.evaluate("()=>[PLOTS.length, plotN, plots.length]")
        ok(r==[6,6,6], f"② 처음 = 예전 밭 6칸 그대로 {r}")
        await pg.evaluate("()=>{ setEdit(true); yTool='farm'; yDrawInv(); yFarmMarks(); }"); await pg.wait_for_timeout(500)
        t=await pg.evaluate("()=>document.getElementById('inv').innerText.replace(/\\s+/g,' ')")
        ok("밭 일구기" in t and "6 / 6" in t and "2칸 더" in t, f"② 꾸미기 = 🌱 밭 일구기 칸 · 6/6 · ➕ 2칸 더 {t[:120]!r}")
        await pg.screenshot(path=OUT+"farm580_edit.png")
        r=await pg.evaluate("""()=>{ const i=0, c=PLOTS[0].slice(); yFarmAt(c); const after=[PLOTS.length, at(PLOTS,c[0],c[1])];
            // 빈 풀밭 찾기
            let cell=null; for(let x=0;x<YN && !cell;x++) for(let z=0;z<YN && !cell;z++) if(!yTillWhy(x,z) && x>3 && z>3) cell=[x,z];
            yFarmAt(cell); return [after, PLOTS.length, at(PLOTS,cell[0],cell[1])>=0, cell]; }""")
        ok(r[0]==[5,-1] and r[1]==6 and r[2], f"② 빈 밭 → 풀밭 · 빈 풀밭 → 밭 (옮기기) {r}")
        r=await pg.evaluate("""()=>{ let cell=null; for(let x=0;x<YN && !cell;x++) for(let z=0;z<YN && !cell;z++) if(!yTillWhy(x,z)) cell=[x,z]; const n=PLOTS.length; yFarmAt(cell); return [n, PLOTS.length, document.getElementById('ask').classList.contains('on')]; }""")
        ok(r[0]==6 and r[1]==6 and r[2], f"② 다 찼으면 안 늘고 「2칸 더」 물어봄 {r}")
        await pg.evaluate("()=>document.getElementById('ask').classList.remove('on')")
        r=await pg.evaluate("""()=>{ const i=1; plots[i]={s:'carrot', g:0, wt:0}; const n=PLOTS.length; yFarmAt(PLOTS[i].slice()); const a=PLOTS.length;
            const k=Object.keys(yd.g)[0]; let pathBad=null; yd.g['5,5']='dirt'; pathBad=yTillWhy(5,5); delete yd.g['5,5'];
            return [n, a, pathBad, yTillWhy(DOOR[0],DOOR[1]+1), yTillWhy(POND.x0,POND.z0)]; }""")
        ok(r[0]==r[1] and r[2]=="path" and r[3]=="door" and r[4]=="busy", f"② 작물 있는 밭은 안 없어짐 · 길·문 앞·연못엔 못 일굼 {r}")
        # 🪙 로 늘리기 → 새 칸 자동
        r=await pg.evaluate("""()=>{ TECO.addCoin ? TECO.addCoin(500) : 0; const c0=TECO.coins(); const ok=buyLand(); return [ok, plotN, PLOTS.length, plots.length, c0-TECO.coins(), new Set(PLOTS.map(c=>c+'')).size===PLOTS.length]; }""")
        ok(r[0] is True and r[1]==8 and r[2]==8 and r[3]==8 and r[4]>0 and r[5], f"② 🪙 로 2칸 더 → 새 밭 2칸 바로 일궈짐 (겹침 없음) {r}")
        lay=await pg.evaluate("()=>JSON.stringify(PLOTS)")
        await pg.evaluate("()=>{ setEdit(false); }")
        await pg.reload(); await pg.wait_for_timeout(2800)
        r=await pg.evaluate("()=>[JSON.stringify(PLOTS)===%r, plotN, plots.length, plots.some(p=>p.s==='carrot'), scene.userData.plotG.length]" % lay)
        ok(r[0] and r[1]==8 and r[2]==8 and r[3] and r[4]==8, f"② 다시 열어도 밭 자리·작물 그대로 {r}")
        # 친구 마당
        r=await pg.evaluate("""()=>{ const mine=JSON.stringify(PLOTS); const v={code:'ZZZZZ', n:'민지', data:{y:{v:1, fp:[[8,2],[9,2]], p:[], g:{}, pc:[0,0,0], db:{}, hx:{}}, av:{}}};
            yEnterVisit(v); return mine; }""")
        await pg.wait_for_timeout(2500)
        r2=await pg.evaluate("()=>[place.key, JSON.stringify(PLOTS), !!scene.userData.yvPlots && scene.userData.yvPlots.children.length, scene.userData.plotG.every(P=>!P.visible)]")
        ok(r2[0]=="yvisit" and r2[1]=="[[8,2],[9,2]]" and r2[2]==2 and r2[3], f"② 친구 마당 = 친구 밭 자리(2칸) · 내 밭은 숨김 {r2}")
        await pg.screenshot(path=OUT+"farm580_visit.png")
        await pg.evaluate("()=>{ go('yard', [DOOR[0],DOOR[1]+1]); }"); await pg.wait_for_timeout(2500)
        r3=await pg.evaluate("()=>[place.key, JSON.stringify(PLOTS), !scene.userData.yvPlots, JSON.parse(localStorage.getItem('hyeng_proto_plotxy')).length]")
        ok(r3[0]=="yard" and r3[1]==r and r3[2] and r3[3]==8, f"② 돌아오면 내 밭 자리 그대로 · 저장 안 바뀜 {r3}")
        await pg.screenshot(path=OUT+"farm580_yard.png")
        # ① 섬 지도
        await pg.evaluate("()=>ISLE.enter()")
        for _ in range(160):
            if await pg.evaluate("()=>HOUSE.place()==='isle' && !HOUSE.trip().busy"): break
            await pg.wait_for_timeout(250)
        await pg.wait_for_timeout(1200)
        r=await pg.evaluate("""()=>{ const W=ISLE_MAP.spots; const p=hero.g.position; const far=ISLE_MAP.zones.find(z=>z.k==='park');
            document.getElementById('ihMenu').click(); document.querySelector('#ihM [data-m=map]') ? document.querySelector('#ihM [data-m=map]').click() : 0;
            const svg=document.querySelector('#ihMap svg'); return [!!svg, !!document.querySelector('#ihMap [data-z=mine]'), !!document.querySelector('#ihMap [data-z=myhome]')]; }""")
        ok(r[0] and r[1], f"① 지도에 ⛏ 광산 표시 {r}")
        r=await pg.evaluate("""()=>{ document.querySelector('#ihMap [data-z=park] polygon').dispatchEvent(new MouseEvent('click',{bubbles:true})); const t=document.getElementById('ask').innerText; return [document.getElementById('ask').classList.contains('on'), t.replace(/\\s+/g,' ')]; }""")
        ok(r[0] and "기차역" in r[1] and "바로" not in r[1], f"① 먼 곳(놀이 공원) = 🚶 걸어가기 · 🚉 기차역으로 (🚀 없음) {r}")
        await pg.screenshot(path=OUT+"farm580_far.png")
        await pg.evaluate("()=>document.querySelector('#ask [data-gz=\"1\"]').click()"); await pg.wait_for_timeout(400)
        await pg.evaluate("()=>{ document.getElementById('ihMenu').click(); document.querySelector('#ihM [data-m=map]').click(); }"); await pg.wait_for_timeout(300)
        r=await pg.evaluate("""()=>{ document.querySelector('#ihMap [data-z=mine] circle').dispatchEvent(new MouseEvent('click',{bubbles:true})); const t=document.getElementById('ask').innerText.replace(/\\s+/g,' '); return [t]; }""")
        ok("바로 광산으로" in r[0], f"① ⛏ 광산 = 🚀 바로 가기 있음 {r}")
        await pg.evaluate("()=>{ TECO.addCoin ? TECO.addCoin(50) : 0; document.querySelector('#ask [data-gz=\"1\"]').click(); }")
        for _ in range(80):
            if await pg.evaluate("()=>HOUSE.place()==='mine' && !HOUSE.trip().busy"): break
            await pg.wait_for_timeout(250)
        ok(await pg.evaluate("()=>HOUSE.place()==='mine'"), "① 🚀 바로 광산 → 광산 안")
        await pg.evaluate("()=>mineToVillage()")
        for _ in range(160):
            if await pg.evaluate("()=>HOUSE.place()==='isle' && !HOUSE.trip().busy"): break
            await pg.wait_for_timeout(250)
        await pg.wait_for_timeout(800)
        await pg.evaluate("()=>document.getElementById('bIHome').click()")
        for _ in range(80):
            if await pg.evaluate("()=>HOUSE.place()==='room' && !HOUSE.trip().busy"): break
            await pg.wait_for_timeout(250)
        ok(await pg.evaluate("()=>HOUSE.place()==='room'"), "① 광산 앞에서 ⭐ 내 집 → 바로 집 안 (멀면 텔포)")
        await br.close()
    ok(not errs, f"오류 없음 {errs[:2]}")
    print("\nFAIL" if bad else "\nPASS", len(bad)); sys.exit(1 if bad else 0)

asyncio.run(main())
