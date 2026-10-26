"""(v415) 🌳 내 땅 꾸미기 — 사용자: "집 콘텐츠는? 자기 땅을 어떻게 꾸밀지"
  ① 마당 14×14 · 🌾 새 땅 3구역(잠김 = 못 걸어감) → 💎 로 열기 → 잡초·돌·그루터기 → 치우면 재료 · 다 치우면 땅
  ② ✏️ 마당 꾸미기: 물건 놓기·옮기기·돌리기·색·넣기 · 길을 막으면 못 놓음 · 울타리 이어짐 · 🛠 제작대·나무 옮기기
  ③ 🛤 길 칠하기 · 🏠 집 색 · 가로등 밤에 켜짐 · 🛒 가게 🌳 마당 · 🛠 만들기 · 🏅 도장 · 저장 → 다시 열어도 그대로 · 친구에게 올리는 데이터"""
import asyncio, sys, os, json
os.environ["HY_REAL3D"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "FAIL ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        ctx = await br.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*", route); await pg.goto(ORIGIN + "proto/house.html"); await pg.wait_for_timeout(800)
        await pg.evaluate("()=>{ Object.keys(localStorage).filter(k=>k.startsWith('hyeng_proto_')).forEach(k=>localStorage.removeItem(k)); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); localStorage.setItem('hyeng_proto_baitok','1'); }")
        await pg.reload(); await pg.wait_for_timeout(2500)
        E = pg.evaluate
        async def until(js, n=80):
            for _ in range(n):
                try:
                    if await E(js): return True
                except Exception: pass
                await pg.wait_for_timeout(250)
            return False
        await E("()=>{ HOUSE.setWx(false); HOUSE.go('yard'); }"); await until("()=>HOUSE.place()==='yard'")
        r = await E("()=>[HOUSE.yd().pc, document.getElementById('bDeco')!==null, !document.getElementById('bBait'), HOUSE.ystock()]")
        ok(r[0] == [0, 0, 0] and r[1] and r[2], f"마당 14×14 · 새 땅 3구역 잠김 · 아래 독 ✏️ 꾸미기 {r}")
        # ① 잠긴 땅은 못 들어감 · 열기
        r = await E("()=>{ HOUSE.setGems(200); return [0, HOUSE.yParcOpen(0), HOUSE.yd().pc[0], Object.keys(HOUSE.yd().db).length, HOUSE.gems()]; }")
        ok(r[1] and r[2] == 1 and r[3] > 10 and r[4] == 180, f"동쪽 숲 열기 💎20 → 잡초·돌·그루터기 {r[3]}칸 {r}")
        k = await E("()=>Object.keys(HOUSE.yd().db).find(k=>HOUSE.yd().db[k]==='stone')")
        r = await E("(k)=>{ const m0=HOUSE.mats().stone|0; HOUSE.yClear(k); return [!HOUSE.yd().db[k], (HOUSE.mats().stone|0)-m0]; }", k)
        ok(r[0] and r[1] == 1, f"🪨 돌 치우기 → stone +1 {r}")
        await E("()=>Object.keys(HOUSE.yd().db).forEach(k=>HOUSE.yClear(k))"); await pg.wait_for_timeout(500)
        ok(await E("()=>Object.keys(HOUSE.yd().db).length===0"), "다 치움")
        st = await E("()=>HOUSE.yStamps().filter(s=>s[2]).map(s=>s[0])")
        ok("y_land" in st, f"🏅 개척자 도장 {st}")
        await pg.screenshot(path=OUT + "land415_open.png")
        # ② 꾸미기
        await E("()=>document.getElementById('bDeco').click()"); await pg.wait_for_timeout(800)
        r = await E("()=>[document.getElementById('drawer').classList.contains('yard'), document.querySelectorAll('#inv [data-yid]').length, document.querySelector('#drawer .hd b span').textContent]")
        ok(r[0] and r[1] >= 3 and "마당" in r[2], f"✏️ 마당 꾸미기 서랍 (처음 선물 물건) {r}")
        r = await E("""()=>{ const H=HOUSE; const a=H.yFits('fence',11,2,0), b=H.yFits('fence',7,6,0), c=H.yFits('fence',13,8,0);
             H.yAdd('fence',11,2,0,0); H.yAdd('fence',12,2,0,0); H.yAdd('fence',13,2,0,0); return [a,b,c, H.yplaced.length]; }""")
        ok(r[0] == 1 and r[1] == 0 and r[2] == 0 and r[3] == 3, f"빈 칸 = 놓기 · 연못·마을 길 = 못 놓음 {r}")
        # 길 막기: 가게 앞 두 칸을 둘러싸면 2
        r = await E("""()=>{ const H=HOUSE; return H.yFits('hedge',5,3,0); }""")
        ok(r in (1, 2), f"보통 칸 검사 {r}")
        r = await E("""()=>{ const H=HOUSE; const L=[[8,1],[8,2],[8,3],[7,3],[6,3],[5,3],[5,2]]; const add=[]; let last=1;
            for(const [x,z] of L){ last=H.yFits('hedge',x,z,0); if(last!==1) break; add.push(H.yAdd('hedge',x,z,0,0)); } const res=last; add.forEach(p=>{ H.yplaced.splice(H.yplaced.indexOf(p),1); p.obj.parent.remove(p.obj); }); return res; }""")
        ok(r == 2, f"🚧 가게 가는 길을 막으면 못 놓음 (2) {r}")
        # 놓기 UI 흐름 (ghost)
        await E("()=>{ HOUSE.yTool('items'); HOUSE.yStartGhost('lamp', null); }"); await pg.wait_for_timeout(300)
        r = await E("()=>[document.getElementById('place').classList.contains('on'), !document.getElementById('pOk').disabled]")
        ok(r == [True, True], f"물건 고르면 초록 칸 · ✅ {r}")
        await E("()=>document.getElementById('pOk').click()"); await pg.wait_for_timeout(300)
        r = await E("()=>[HOUSE.yplaced.some(p=>p.id==='lamp'), HOUSE.ystock().lamp|0]")
        ok(r == [True, 0], f"💡 가로등 놓음 · 창고에서 빠짐 {r}")
        # 울타리 이어짐
        ok(await E("()=>HOUSE.yplaced.filter(p=>p.id==='fence').map(p=>p.obj.userData.cn|0).join(',')") == "2,10,8", "🪵 울타리 이웃끼리 이어짐 (오른쪽·양쪽·왼쪽)")
        # 선택 → 색 → 넣기
        await E("()=>{ const p=HOUSE.yplaced.find(p=>p.id==='fence'); HOUSE.ySel(p); }"); await pg.wait_for_timeout(200)
        await E("()=>document.getElementById('mCol').click()")
        ok(await E("()=>HOUSE.yplaced.find(p=>p.id==='fence').c")==1, "🎨 색 바꾸기")
        await E("()=>{ const p=HOUSE.yplaced.find(p=>p.id==='fence' && p.x===13); HOUSE.ySel(p); document.getElementById('mBox').click(); }")
        r = await E("()=>[HOUSE.yplaced.filter(p=>p.id==='fence').length, HOUSE.ystock().fence]")
        ok(r == [2, 7], f"📦 넣기 → 창고로 (6 + 1) {r}")
        # 원래 물건 옮기기: 제작대
        r = await E("""()=>{ const H=HOUSE; H.ySel({fixed:{f:'bench'}, obj:H.benchObj(), y:1}); document.getElementById('mMove').click(); const g=H.ghost(); g.x=12; g.z=5; H.yUpd(); document.getElementById('pOk').click(); return [H.BENCH(), H.benchObj().position.x]; }""")
        ok(r[0] == [12, 5] and abs(r[1] - 12.5) < 0.01, f"🛠 제작대 옮기기 {r}")
        # ③ 길 칠하기
        r = await E("()=>{ const H=HOUSE; H.yTool('path'); H.yPaintK('dirt'); for(let x=4;x<=6;x++) H.yPaintAt([x,4]); H.yPaintAt([7,6]); return [Object.keys(H.yd().g).length, H.yd().g['7,6']]; }")
        ok(r[0] == 3 and r[1] is None, f"🛤 흙길 3칸 · 연못엔 안 칠함 {r}")
        r = await E("()=>{ const H=HOUSE; H.setGems(100); document.querySelector('#inv [data-yt=path]').click(); document.querySelector('#inv [data-gp=brick]').click(); return !!document.getElementById('ask').classList.contains('on'); }")
        ok(r, "🧱 벽돌 길은 처음에 사기 (묻기)")
        await E("()=>document.getElementById('askOk').click()"); await pg.wait_for_timeout(200)
        r = await E("()=>[HOUSE.ownGP().includes('brick'), HOUSE.yPaintK(), HOUSE.gems()]")
        ok(r[0] and r[1] == "brick" and r[2] == 94, f"샀으면 계속 칠함 {r}")
        # 집 색
        await E("()=>{ document.querySelector('#inv [data-yt=house]').click(); document.querySelector('#inv [data-hx=r2]').click(); document.querySelector('#inv [data-hx=d1]').click(); }")
        r = await E("()=>[HOUSE.yd().hx, '#'+HOUSE.houseRoof().material.color.getHexString()]")
        ok(r[0]["r"] == 2 and r[0]["d"] == 1 and r[1] == "#5cbf5a", f"🏠 지붕·문 색 {r}")
        await pg.screenshot(path=OUT + "land415_edit.png")
        # 밤 가로등
        r = await E("()=>{ HOUSE.yNight(true); const l=HOUSE.yplaced.find(p=>p.id==='lamp').obj.userData; const a=[l.bulb.material.emissiveIntensity, l.glow.material.opacity]; return a; }")
        ok(r[0] > 1 and r[1] > 0.2, f"💡 밤에 켜짐 {r}")
        await E("()=>HOUSE.yNight(false)")
        await E("()=>document.getElementById('bDone').click()"); await pg.wait_for_timeout(600)
        ok(await E("()=>!document.getElementById('drawer').classList.contains('on') && getComputedStyle(document.querySelector('.bar.bot')).visibility==='visible'"), "✅ 다 했어요 → 꾸미기 끝")
        # 가게 · 만들기
        r = await E("""()=>{ const H=HOUSE; H.setGems(50); H.openFurn('yard'); const b=document.querySelector('#furnBody [data-by=swing]'); b.click(); const t=[...document.querySelectorAll('#furnTabs [data-ft]')].map(x=>x.dataset.ft); document.getElementById('furnDone').click(); return [H.ystock().swing, H.gems(), t]; }""")
        ok(r[0] == 1 and r[1] == 35 and "yard" in r[2], f"🛒 가게 🌳 마당 탭 · 그네 사기 {r}")
        r = await E("()=>{ const H=HOUSE; H.addMat('branch',4); H.addMat('stone',1); const ok=H.make('craft','y_obench'); return [ok, H.ystock().obench]; }")
        ok(r[0] and r[1] == 1, f"🛠 정원 벤치 만들기 {r}")
        # 저장 → 다시 열기
        before = await E("()=>JSON.stringify(HOUSE.yData())")
        await pg.reload(); await pg.wait_for_timeout(2500)
        after = await E("()=>JSON.stringify(HOUSE.yData())")
        ok(json.loads(before) == json.loads(after), "다시 열어도 그대로 (물건·길·집 색·땅·옮긴 제작대)")
        ok(await E("()=>HOUSE.yplaced.length")==3 and await E("()=>HOUSE.BENCH()")==[12,5], "놓은 것 3개 · 제작대 자리")
        r = await E("()=>{ const d=HOUSE.yData(); return JSON.stringify(d).length; }")
        ok(r < 20000, f"친구에게 올리는 데이터 크기 {r}")
        # 👫 친구 마당부터
        mine = await E("()=>JSON.stringify(HOUSE.yData())")
        await E("()=>HOUSE.yEnterVisit({code:'ABCDE', n:'민준', data:{n:'민준', rn:6, f:1, w:1, p:[['bed',0,0,0,0]], wl:[], av:{hat:'cap'}, y:{p:[['swing',10,1,0,0],['fountain',5,10,0,0]], g:{'4,4':'brick','5,4':'brick'}, pc:[1,0,1], db:{}, hx:{r:3,w:1,d:2}}}})")
        ok(await until("()=>HOUSE.place()==='yvisit' && HOUSE.yplaced.length===2", 60), "친구 마당으로 (마을 길에서 걸어 들어옴)")
        r = await E("()=>[HOUSE.yplaced.map(p=>p.id).join(','), HOUSE.yd().hx.r, !!HOUSE.yHost(), document.getElementById('gVisit').classList.contains('on'), HOUSE.BENCH()]")
        ok(r[0] == "swing,fountain" and r[1] == 3 and r[2] and r[3] and r[4] == [3, 1], f"친구가 꾸민 물건·집 색·주인 인형 · 아래 나가기·좋아요 {r}")
        await pg.screenshot(path=OUT + "land415_visit.png")
        await E("()=>HOUSE.yVisitHouse()")
        ok(await until("()=>HOUSE.place()==='visit'", 80), "집 문 → 친구 방")
        await E("()=>document.getElementById('bVLeave').click()")
        ok(await until("()=>HOUSE.place()==='yvisit'", 80), "친구 방에서 나오면 친구 마당")
        await E("()=>document.getElementById('bVLeave').click()")
        ok(await until("()=>!HOUSE.visiting() && ['room','yard'].includes(HOUSE.place())", 80), "나가기 → 원래 있던 곳")
        after = await E("()=>JSON.stringify(HOUSE.yData())")
        ok(json.loads(after) == json.loads(mine) and await E("()=>HOUSE.yplaced.length")==3, "내 마당 그대로 돌아옴 (물건·길·제작대 자리)")
        ok(await E("()=>HOUSE.placed.length>0 && !HOUSE.placed.some(p=>p.host)"), "내 방도 그대로")
        ok(not errs, "오류 없음 " + str(errs[:3]))
        await br.close()
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)

asyncio.run(main())
