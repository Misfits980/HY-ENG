"""(v397) 💬 학부모 문자 — 시트 문장에 교실 수업 참여 · 보스 · 시험 · 칭찬 한 줄 · 못 온 주는 부드럽게 · 틀린 단어는 집에서 할 일로"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright
async def main():
    bad=[]; errs=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(); ctx=await br.new_context(viewport={"width":390,"height":844}, service_workers="block"); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)
        D={"weekly":[["주간 리포트"],["주 시작 (월요일)","2026-10-19 (월)","~ 10/25 (일)"],[],[],[],
            ["김지후","7","98","89","213.4","88","25","17,106","11","129","versus, congress","+31","김지후 학생은 이번 주 7일 들어왔어요."],
            ["주호","3","31","30","58.5","93","0","0","0","0","chin, dancer","-33","주호 학생은 이번 주 3일 들어왔어요."],
            ["루아","0","0","0","0","","0","0","0","0","","","루아 학생은 이번 주 들어오지 않았어요."],
            ["단우","2","8","8","20","80","0","0","0","0","","","단우 학생은 이번 주 2일 들어왔어요."]],
          "lesson":[["날짜","수업","아이","종류","점수","순위"],["10/23 15:52","레이드 5026","김지후","⚔️ 레이드","996","","93","51","4"],["10/22 15:47","교실 배틀","김지후","🏫 배틀","976","1등"],["10/12 15:47","교실 배틀(지난 주 아님)","김지후","🏫 배틀","449","5등"],["10/23 15:47","교실 배틀","주호","🏫 배틀","757","2등"]]}
        M=lambda r: pg.evaluate("([r,D])=>Admin._pMsg(r,D)", [r, D])
        W=D["weekly"]
        a=await M(W[5]); print(a)
        ok("7일" in a and "98번(213분)" in a and "88%" in a, "기본 숫자")
        ok("달리기 25판(새로 만난 단어 129개)" in a and "교실 배틀·레이드 2번" in a, "달리기 · 이번 주 수업 2번(지난 주 건 안 셈)")
        ok("지난주보다 31분" in a or "정확하게 푸는 힘" in a, "칭찬 한 줄")
        ok("versus, congress" in a and "집에서" in a, "틀린 단어는 집에서 할 일")
        b=await M(W[6]); print(b)
        ok("교실 배틀·레이드 1번" in b and "정확하게 푸는 힘" in b, "수업 1번 · 정답률 93% 칭찬")
        c=await M(W[7]); print(c)
        ok("들어오지 못했어요" in c and "다음 주" in c and "정답률" not in c, "못 온 주는 부드럽게")
        d=await M(W[8]); print(d)
        ok("3~4번" in d, "2일 이하는 권유 한 줄")
        e=await pg.evaluate("()=>Admin._pMsg(['x'],{})"); ok(e=="", "시트 문장이 없으면 빈 글")
        er=real_errs(errs); ok(not er, "오류 없음 "+str(er[:2]))
        await br.close()
    print("결과:", "통과" if not bad else "실패 "+str(bad))
asyncio.run(main())
