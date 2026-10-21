"""(v362) 사용자: 닉네임 글자 제한 필요 — 한글·영어·숫자·띄어쓰기만 · 8글자까지 · 명단 아이 시트 이름(👤)이 10글자에서 잘리지 않게"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await br.new_page(viewport={"width": 390, "height": 844})
        pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)
        await pg.evaluate("()=>{ localStorage.removeItem('hyeng_nick'); localStorage.removeItem('hyeng_name_v1'); }")
        ok(await pg.evaluate("()=>document.getElementById('nick').maxLength") == 8, "이름 칸 8글자")
        r = await pg.evaluate("()=>NameCard.change('패트와 매트(패트)')")
        ok("기호" in r, f"기호 섞이면 안내 {r}")
        r = await pg.evaluate("()=>NameCard.change('아주아주긴이름입니다')")
        ok("8글자" in r, f"8글자 넘으면 안내 {r}")
        r = await pg.evaluate("()=>[NameCard.change('패트와 매트'), NameCard.cur()]")
        ok(r == ["", "패트와 매트"], f"한글·띄어쓰기 8글자 안 = 정해짐 {r}")
        r = await pg.evaluate("()=>[NameCard.clean('Kim☆민준😀!!'), NameCard.clean('abcdefghijk')]")
        ok(r == ["Kim민준", "abcdefgh"], f"clean: 기호·이모지 빼고 8글자 {r}")
        # 선생님 조치(force)는 그대로 고쳐 줌
        r = await pg.evaluate("()=>[NameCard.change('서연(2반)', '조치'), NameCard.cur()]")
        ok(r == ["", "서연2반"], f"선생님 조치는 기호만 빼고 정함 {r}")
        # 명단 아이 시트 이름 — 10글자 그대로
        r = await pg.evaluate("()=>{ Kid.set({id:'k1', n:'패트와 매트(패트)', t:'all'}); return Online.nickOf({rule:'study', nick:'X'}); }")
        ok(r == "👤패트와 매트(패트)", f"명단 이름 10글자 안 잘림 {r}")
        r = await pg.evaluate("()=>{ Kid.set({id:'k2', n:'👤라언', t:'all'}); return Online.nickOf({rule:'study', nick:'X'}); }")
        ok(r == "👤라언", f"(v366) 👤 두 번 안 붙음 {r}")
        e = real_errs(errs); ok(not e, "오류 없음 " + str(e[:3]))
        await br.close()
    print("결과:", "통과" if not bad else "실패 " + str(bad))
asyncio.run(main())
