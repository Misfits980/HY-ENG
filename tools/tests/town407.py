"""(v407) 🏡 My Town 편하게 — 사용자: "조잡함이 심하네 · 누르는 방법, 나가는 문도 없고 갑자기 텔레포트 · 낚시는 어떻게? 미끼는 왜 뭐지? — 불편함 덩어리"
  ① 🚪 진짜 문(방 왼쪽 벽 맨 앞 · 마당 집) — 걸어가서 문 열고 나감 → 다음 곳에선 문·길 쪽에서 걸어 들어옴 · 길(표지판)도 끝까지 걸어감
  ② 누를 곳 이름표 (눌러도 그 일을 함) · ③ 🧑‍🌾 Mia 처음 안내 (해 보면 다음 · 건너뛰어도 따라감 · 그만 보기)
  ④ 🎣 낚시 코치 (던지기 → 기다리기 → 톡!) · 처음 4번은 쉽게 · 입질 전 톡은 끝내지 않음 · ⑤ 🪱 미끼 카드 · ⑥ 📋 할 일 (💎 받기)"""
import asyncio, sys, os
os.environ["HY_REAL3D"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        ctx = await br.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*", route); await pg.goto(ORIGIN + "proto/house.html"); await pg.wait_for_timeout(1200)
        await pg.evaluate("()=>{ Object.keys(localStorage).filter(k=>k.startsWith('hyeng_proto_')).forEach(k=>localStorage.removeItem(k)); }")
        await pg.reload(); await pg.wait_for_timeout(3000)
        E = pg.evaluate
        async def until(js, n=160):
            for _ in range(n):
                if await E(js): return True
                await pg.wait_for_timeout(150)
            return False
        async def stand(x, z):
            await E("(a)=>{ const h=HOUSE.hero(); h.path=[]; h.moving=false; h.cx=a[0]; h.cz=a[1]; h.g.position.set(a[0]+.5,0,a[1]+.5); }", [x, z])

        # ── 처음 화면: 안내 · 이름표 · 독 · 디버그 글씨 없음
        ok(await E("()=>document.getElementById('coach').classList.contains('on') && /바닥을/.test(document.getElementById('coachT').innerText)"), "처음 들어오면 Mia 안내 (바닥을 톡)")
        ok(await E("()=>getComputedStyle(document.getElementById('fps')).display==='none'"), "fps 글씨 안 보임")
        ok(await E("()=>HOUSE.LBL().map(l=>l.d.k).join()==='door' && HOUSE.LBL()[0].el.style.display!=='none'"), "방: 🚪 나가기 이름표")
        ok(await E("()=>document.getElementById('bOut').innerText.includes('나가기') && !!document.getElementById('bVill') && !!document.getElementById('bMine')"), "독: 🚪 나가기 · 마당 🏘 마을 · 마을 ⛏ 광산")
        # ── 🚪 방 문
        d = await E("()=>{ const D=HOUSE.roomDoor(), R=HOUSE.RN(); return [!!D && D.parent===HOUSE.walls[3], HOUSE.wallFits(3,R-1), HOUSE.wallFits(3,R-2) || HOUSE.wplaced.some(p=>p.side===3&&p.s===R-2), HOUSE.fits('plant',0,R-1,0), HOUSE.fits('rug',0,R-2,0)]; }")
        ok(d[0] and not d[1] and d[2] and not d[3], f"방 문 = 왼쪽 벽 맨 앞 · 그 벽 칸엔 못 걺 · 문 앞 칸엔 가구 못 놓음 {d}")
        # 걷기 → 안내 다음
        await E("()=>HOUSE.walkTo(3,3)"); await pg.wait_for_timeout(300)
        ok(await E("()=>HOUSE.tut().s")==1, "바닥 톡(걷기) → 안내 2 (가구도 눌러 봐요)")
        await until("()=>!HOUSE.hero().moving")
        # 나가기: 문까지 걸어가 → 문 열림 → 마당 집 문 앞에서 걸어 나옴
        await stand(0, await E("()=>HOUSE.RN()-1"))
        await E("()=>HOUSE.exitRoom()"); await pg.wait_for_timeout(120)
        o = await E("()=>[HOUSE.roomDoor().userData.open, HOUSE.trip().busy, HOUSE.place()]")
        ok(o == [1, True, "room"], f"🚪 누름 → 문이 열리고 걸어 나가는 중 {o}")
        ok(await until("()=>HOUSE.place()==='yard'"), "→ 마당")
        a = await E("()=>{ const h=HOUSE.hero(); return [h.cx, h.cz, !!h.slide, HOUSE.houseDoor().userData.open]; }")
        ok(a[0] == 1 and a[1] == 3 and a[3] == 1, f"마당: 집 문이 열리고 문 앞(1,3)으로 걸어 나옴 {a}")
        ok(await until("()=>!HOUSE.hero().slide && !HOUSE.trip().busy"), "걸어 나오기 끝")
        ok(await E("()=>HOUSE.tut().s")==3, "마당에 오면 안내가 낚시로 건너뜀 (가구 안내 건너뛰어도 따라감)")
        L = await E("()=>HOUSE.LBL().map(l=>l.d.k)")
        ok(L == ["house", "pond", "shop", "bench", "pot", "farm", "gate", "parc0", "parc1", "parc2"], f"마당 이름표 7 + (v415) 🌱 새 땅 3 {L}")
        await pg.wait_for_timeout(500)
        ok(await E("()=>{ const e=document.querySelector('#tls .tl[data-k=pond]'); return e.classList.contains('hot') && !e.classList.contains('far') && getComputedStyle(e).opacity==='1'; }"), "안내 중인 곳(🎣 낚시) 이름표가 반짝 · (v437) 멀어도 보임")
        # ── 🪱 미끼 카드 → 🎣 낚시 코치
        await E("()=>document.querySelector('#tls .tl[data-k=pond]').click()"); await pg.wait_for_timeout(300)
        ok(await E("()=>document.getElementById('info').classList.contains('on') && /공부하면 생겨요/.test(document.getElementById('infoT').innerText)"), "처음 연못 → 🪱 미끼 카드 (밥 · 1번에 1개 · 공부하면 생겨요)")
        ok(await E("()=>document.getElementById('tls').classList.contains('off') && !document.getElementById('coach').classList.contains('on')"), "카드가 떠 있으면 이름표·안내 숨김")
        await E("()=>document.getElementById('infoOk').click()")
        ok(await until("()=>HOUSE.F.st==='wait'", 300), "🎣 낚시하러 가기 → 연못까지 걸어가 던짐")
        f = await E("()=>[document.getElementById('fc').classList.contains('on'), document.querySelector('#fc li.on').innerText, document.getElementById('bobL').classList.contains('on'), HOUSE.F.nib.length, HOUSE.F.win]")
        ok(f[0] and f[1] == "기다리기" and f[2] and f[3] == 0 and f[4] >= 1.9, f"코치 ② 기다리기 · 찌 이름표 · 처음엔 콕콕 없음 · 2초 {f}")
        await E("()=>{ HOUSE.F.T=99; HOUSE.tapWhileFishing(); }"); await pg.wait_for_timeout(200)
        ok(await E("()=>HOUSE.F.st==='wait' && /아직/.test(document.getElementById('fc').innerText)"), "입질 전 톡 → 끝내지 않고 '아직이에요'")
        await E("()=>HOUSE.bite()"); await pg.wait_for_timeout(150)
        ok(await E("()=>document.getElementById('fc').classList.contains('go') && /지금/.test(document.getElementById('fc').innerText)"), "입질 → ③ 지금 톡!")
        await E("()=>HOUSE.tapWhileFishing()")
        ok(await until("()=>{ if(HOUSE.F.st==='fight') HOUSE.winFight(); return HOUSE.F.st==='quiz'; }"), "톡 → (줄다리기) → 잡음")
        ok(await E("()=>!document.getElementById('fc').classList.contains('on') && HOUSE.tut().s===4"), "잡으면 코치 닫힘 · 안내 다음 (가게에서 팔기)")
        await E("()=>document.getElementById('qOk').click()"); await pg.wait_for_timeout(300)
        # ── 📋 할 일
        ok(await E("()=>!document.getElementById('hQn').hidden && document.getElementById('hQn').innerText==='1'"), "할 일 1개 끝 → 📋 에 빨간 1")
        await E("()=>HOUSE.openQ()"); await pg.wait_for_timeout(200)
        q = await E("()=>[document.querySelectorAll('#qBody .qRow').length, document.querySelectorAll('#qBody [data-q]').length]")
        ok(q == [11, 1], f"할 일 = 처음 8 + 오늘 3 · 받기 1 {q}")
        g0 = await E("()=>HOUSE.gems()")
        await E("()=>document.querySelector('#qBody [data-q]').click()"); await pg.wait_for_timeout(200)
        ok(await E("()=>HOUSE.gems()") == g0 + 2 and await E("()=>document.getElementById('hQn').hidden"), "💎2 받기")
        ok(await E("()=>HOUSE.qClaim('s:catch')") == 0, "두 번은 못 받음")
        await E("()=>document.getElementById('qDone').click()")
        dd = await E("()=>{ const a=HOUSE.qList().filter(q=>q.sec==='d').map(q=>q.k); return [a.length, new Set(a).size]; }")
        ok(dd == [3, 3], f"오늘 할 일 3개 (겹치지 않음) {dd}")
        # 🪱 HUD 누르면 미끼 카드
        await E("()=>document.getElementById('hBait').click()"); await pg.wait_for_timeout(150)
        ok(await E("()=>document.getElementById('info').classList.contains('on')"), "🪱 숫자를 누르면 미끼 설명")
        await E("()=>document.getElementById('infoOk').click()")
        # ── 길로 마을 → 걸어 들어옴
        await stand(9, 8); await E("()=>HOUSE.yardToVillage()")
        ok(await until("()=>HOUSE.place()==='village'"), "🏘 표지판 길 → 마을")
        v = await E("()=>{ const h=HOUSE.hero(); return [h.cx, h.cz, h.g.position.x<1.5]; }")
        ok(v[0] == 1 and v[1] == 6 and v[2], f"마을 왼쪽 길 끝에서 걸어 들어옴 {v}")
        await until("()=>!HOUSE.trip().busy && !HOUSE.hero().slide")
        ok(await E("()=>HOUSE.LBL().map(l=>l.d.k).join()") == "gate,east,tower,board", "마을 이름표: 마당 · 광산 · (v422) 🗼 타워 · 부탁")
        ok(await E("()=>HOUSE.tut().s") == 7 and await E("()=>/영어로/.test(document.getElementById('coachT').innerText)"), "마을 안내 (마을 사람 = 영어로)")
        await E("()=>document.getElementById('coachSkip').click()")
        ok(await E("()=>HOUSE.tut().s>=HOUSE.TUT.length && !document.getElementById('coach').classList.contains('on')"), "안내 그만 보기")
        # 광산 ↔ 마을
        await stand(11, 6); await E("()=>HOUSE.villageToMine()")
        ok(await until("()=>HOUSE.place()==='mine'"), "⛏ 광산으로")
        await until("()=>!HOUSE.trip().busy && !HOUSE.hero().slide")
        await stand(9, 5); await E("()=>HOUSE.mineToVillage()")
        ok(await until("()=>HOUSE.place()==='village'"), "🏘 마을로")
        await until("()=>!HOUSE.trip().busy && !HOUSE.hero().slide")
        # 놀러 가기 = 문으로 들어옴 · 나갈 때도 문
        await E("()=>HOUSE.visitNpc('rosa')"); ok(await until("()=>HOUSE.place()==='visit' && !HOUSE.trip().busy"), "Rosa 집")
        r = await E("()=>{ const h=HOUSE.hero(), R=HOUSE.RN(); return [h.cx, h.cz, R, HOUSE.placed.some(p=>p.x===0&&p.z===R-1&&!HOUSE.ITEMS[p.id].rug)]; }")
        ok(r[1] == r[2] - 1 and r[0] <= 1 and not r[3], f"남의 집도 문으로 들어옴 · 문 앞 비어 있음 {r}")
        await stand(0, r[2] - 1); await E("()=>HOUSE.exitRoom()")
        ok(await until("()=>!HOUSE.visiting() && HOUSE.place()==='village'"), "🚪 나가기 → 마을로 돌아옴")
        # 할 일: 놀러 가기 체크
        ok(await E("()=>HOUSE.qList().find(q=>q.id==='s:visit').c>=1"), "할 일 '이웃 집 놀러 가기' 체크")
        # 다시 보기
        await E("()=>{ HOUSE.openQ(); }"); await pg.wait_for_timeout(150); await E("()=>document.getElementById('qTut').click()"); await pg.wait_for_timeout(500)
        ok(await E("()=>HOUSE.tut().s===7 && document.getElementById('coach').classList.contains('on')"), "📋 → Mia 안내 다시 보기 (지금 있는 곳부터)")
        ok(not errs, "오류 없음 " + str(errs[:3]))
        await br.close()
    print("결과:", "통과" if not bad else f"실패 {len(bad)}")
    sys.exit(1 if bad else 0)

asyncio.run(main())
