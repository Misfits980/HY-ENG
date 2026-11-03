"""(v568) 사용자: 「다른 팝업도 이참에 찍어서 보여 줄래?」 — My Town 창(시트·팝업)을 폰 390×844 로 하나씩 찍어 out/pop568/ 에 저장
   검사가 아니라 사진첩 (창이 안 열리면 NO 로 표시)"""
import asyncio, sys, os
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from fakefb import fake
from playwright.async_api import async_playwright

W, H = int(os.environ.get("PW", "390")), int(os.environ.get("PH", "844"))
D = OUT + "pop568" + ("" if W == 390 else "_%d" % W) + os.sep
os.makedirs(D, exist_ok=True)

ROOM = [  # 방에서
    ("01_furn", "()=>{ openFurn('furn'); }"),
    ("02_furn_yard", "()=>{ openFurn('yard'); }"),
    ("03_furn_wall", "()=>{ openFurn('wall'); }"),
    ("04_furn_up", "()=>{ openFurn('up'); }"),
    ("05_homex_up", "()=>{ HOMEX.openUp(); }"),
    ("06_bag", "()=>{ openBag(); }"),
    ("07_sto", "()=>{ openSto('ch'); }"),
    ("08_av", "()=>{ openAv(); }"),
    ("09_craft", "()=>{ openCraft('bench'); }"),
    ("10_friends", "()=>{ openFr(); }"),
    ("11_score", "()=>{ openScore(); }"),
    ("12_quests", "()=>{ openQ(); }"),
    ("13_books", "()=>{ HLIFE.openBooks(); }"),
    ("14_mart", "()=>{ HLIFE.openMart(); }"),
]
ISLE = [  # 섬에서
    ("20_bank_ex", "()=>{ TECO.openBank('ex'); }"),
    ("21_bank_sv", "()=>{ TECO.openBank('sv'); }"),
    ("22_upgrade", "()=>{ TECO.openUpg(); }"),
    ("23_build", "()=>{ TECO.openBuild('free2'); }"),
    ("24_fishshop", "()=>{ openShop(); }"),
    ("25_snack", "()=>{ TFAC.openSnack(); }"),
    ("26_pet", "()=>{ TFAC.openPet(); }"),
    ("27_post", "()=>{ TFAC.openPost(); }"),
    ("28_museum", "()=>{ TFAC.openMuseum(); }"),
    ("29_library", "()=>{ TFAC.openLib(); }"),
    ("30_station", "()=>{ TFAC.openStation(); }"),
    ("31_goal", "()=>{ TFAC.openGoal(); }"),
    ("32_photo", "()=>{ TFAC.openPhoto(); }"),
    ("33_me", "()=>{ TFAC.openMe(); }"),
    ("34_map", "()=>{ IHUD.openMap(); }"),
    ("35_dex", "()=>{ document.getElementById('dexP') && (typeof openDex==='function' ? openDex() : document.getElementById('dexP').classList.add('on')); }"),
]
CLOSE = """()=>{ document.querySelectorAll('.sheet.on,.hlP.on,#ask.on,#info.on,.tfP.on,#ihMap.on').forEach(e=>e.classList.remove('on')); document.querySelectorAll('[id].on').forEach(e=>{ if(/P$|^tf|^te|^hl|^ask$|^info$/.test(e.id)) e.classList.remove('on'); }); }"""
OPENED = """()=>{ const L=[...document.querySelectorAll('.sheet.on,.hlP.on,#ask.on,#info.on,[id^=tf].on,[id^=te].on')].filter(e=>e.getBoundingClientRect().height>40); return L.map(e=>e.id).join(','); }"""

async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        ctx = await br.new_context(viewport={"width": W, "height": H}, is_mobile=W < 500, has_touch=True, device_scale_factor=2)
        pg = await ctx.new_page(); errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*", fake); await pg.goto(ORIGIN + "proto/house.html"); await pg.wait_for_timeout(500)
        await pg.evaluate("()=>{ localStorage.setItem('hyeng_proto_code', JSON.stringify('AAAAA')); localStorage.setItem('hyeng_nick','루아'); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99}));"
                          " localStorage.setItem('hyeng_study_v1', JSON.stringify({days:{n:8,tot:9,hs:8,hb:8,last:Math.floor((Date.now()-new Date().getTimezoneOffset()*60000)/864e5)}})); }")
        await pg.reload(); await pg.wait_for_timeout(2600)
        await pg.evaluate("()=>{ gems=1240; saveBag(); TECO.setCoin(860); try{ addMat('carrot',4); addMat('apple',3); addMat('branch',6); addMat('stone',4); for(let i=0;i<3;i++) bag.push({en:HOUSE.FISH[i].en, at:Date.now(), cm:30}); saveBag(); }catch(e){} }")
        res = []
        async def shot(name, js):
            await pg.evaluate(CLOSE); await pg.wait_for_timeout(150)
            try:
                await pg.evaluate(js)
            except Exception as e:
                res.append((name, "ERR " + str(e)[:80])); return
            await pg.wait_for_timeout(700)
            o = await pg.evaluate(OPENED)
            await pg.screenshot(path=D + name + ".png")
            res.append((name, o or "NO"))
        for n, js in ROOM: await shot(n, js)
        await pg.evaluate(CLOSE)
        await pg.evaluate("()=>HOUSE.exitRoom()")
        for _ in range(160):
            if await pg.evaluate("()=>HOUSE.place()==='isle' && !HOUSE.trip().busy"): break
            await pg.wait_for_timeout(250)
        await pg.wait_for_timeout(1200)
        await pg.evaluate(CLOSE); await pg.screenshot(path=D + "19_isle_hud.png"); res.append(("19_isle_hud", "-"))
        for n, js in ISLE: await shot(n, js)
        await br.close()
    for n, o in res: print(n, o)
    print("errors", errs[:3])

asyncio.run(main())
