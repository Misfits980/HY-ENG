"""(v264) 선생님 관리 화면(탭 5개) + 📢 공지 — 가짜 Apps Script 로 확인
   - 아이 화면: 공지가 첫 화면에 창으로 한 번 · 확인하면 다시 안 뜸 · 소식지 맨 위에 계속
   - 관리 화면: 탭마다 그려지는지 · 공지 올리기/내리기 · 원격 조치 보내기 · 예전 서버(공지 없음)면 보내기 막힘"""
import asyncio, os, sys, json
from urllib.parse import urlparse, parse_qs
from playwright.async_api import async_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *

NOTICES = [{"id": "n1", "text": "금요일은 단어 시험!\n오늘의 30 꼭 하고 오세요", "date": "10월 14일", "until": "2099-01-01"}]

def make_route(state):
    async def r(route):
        url = route.request.url
        if "script.google.com" in url:
            if route.request.method == "POST":
                d = json.loads(route.request.post_data or "{}"); state["posts"].append(d)
                if d.get("type") in ("check", "notice", "noticeOff", "actAdd"):
                    if not state["v2"]: body = {"ok": True}          # 예전 서버는 scores 에 써 버린다 → 보내면 안 됨
                    elif d.get("tk") != "testkey": body = {"ok": False, "err": "badkey"}
                    else:
                        body = {"ok": True, "v": 2}
                        if d["type"] == "notice": state["notices"].insert(0, {"id": "n%d" % len(state["posts"]), "text": d["text"], "date": "10월 14일", "until": ""})
                        if d["type"] == "noticeOff": state["notices"] = [n for n in state["notices"] if n["id"] != d["id"]]
                else: body = {"ok": True}
                return await route.fulfill(status=200, content_type="application/json", body=json.dumps(body))
            q = parse_qs(urlparse(url).query)
            if "notice" in q and state["v2"]: body = {"ok": True, "v": 2, "notices": state["notices"]}
            elif "act" in q: body = {"ok": True, "list": []}
            else: body = {"ok": True, "list": []}                   # 예전 서버: notice 를 몰라서 랭킹을 준다
            return await route.fulfill(status=200, content_type="application/json", body=json.dumps(body))
        return await route_fn(route)
    return r
route_fn = route

async def main():
    bad = []
    async with async_playwright() as p:
        br = await p.chromium.launch(); errs = []
        st = {"posts": [], "notices": list(NOTICES), "v2": True}
        ctx = await br.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2)
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.route("**/*", make_route(st)); await pg.goto(ORIGIN + "index.html"); await pg.wait_for_timeout(1200)
        await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); }")
        await pg.wait_for_timeout(3500)
        on = await pg.evaluate("()=>document.getElementById('shNotice').classList.contains('on')")
        print("kid popup", on, await pg.evaluate("()=>document.getElementById('ntList').innerText"))
        await pg.screenshot(path=OUT + "ad_kid_notice.png")
        if not on: bad.append("공지 창이 안 뜸")
        print("dot", await pg.evaluate("()=>getComputedStyle(document.getElementById('newsDot')).display"))
        await pg.click("#btnNoticeOk"); await pg.wait_for_timeout(200)
        await pg.evaluate("()=>{ Notice.last=0; Notice.poll(true); }"); await pg.wait_for_timeout(600)
        again = await pg.evaluate("()=>document.getElementById('shNotice').classList.contains('on')")
        print("again after seen", again)
        if again: bad.append("본 공지가 다시 뜸")
        await pg.evaluate("()=>News.open()"); await pg.wait_for_timeout(200)
        blk = await pg.evaluate("()=>document.getElementById('newsNotice').innerText")
        print("news block", blk.replace("\n", " / "))
        await pg.screenshot(path=OUT + "ad_kid_news.png")
        if "단어 시험" not in blk: bad.append("소식지에 공지 없음")
        await pg.evaluate("()=>News.close()"); await pg.wait_for_timeout(500)

        # 관리 화면 — 비밀번호 화면
        await pg.evaluate("()=>Admin.open()"); await pg.wait_for_timeout(300)
        await pg.screenshot(path=OUT + "ad_0_pin.png")
        # 비밀번호를 맞힌 것처럼 (열쇠 = testkey)
        await pg.evaluate("()=>{ sessionStorage.setItem('hyeng_admin_ok','1'); sessionStorage.setItem('hyeng_admin_tk','testkey'); Admin.close(); }")
        await pg.reload(); await pg.wait_for_timeout(1500)
        await pg.evaluate("()=>{ document.querySelectorAll('.sheet.on').forEach(s=>s.classList.remove('on')); Admin.open(); }"); await pg.wait_for_timeout(500)
        for t in ["home", "notice", "send", "fix", "move"]:
            await pg.click('#adTabs [data-t="%s"]' % t); await pg.wait_for_timeout(700)
            await pg.screenshot(path=OUT + "ad_%s.png" % t)
            txt = await pg.evaluate("()=>document.getElementById('adBody').innerText.slice(0,120)")
            print(t, "|", txt.replace("\n", " / ")[:110])
        # 긴 화면을 내려도 탭 줄이 위에 붙어 있는지
        await pg.click('#adTabs [data-t="home"]'); await pg.wait_for_timeout(300)
        top = await pg.evaluate("()=>{ const s=document.querySelector('#shAdmin .sheetIn'); s.scrollTop=900; const a=document.querySelector('.adTop').getBoundingClientRect(), b=s.getBoundingClientRect(); return [Math.round(a.top-b.top), s.scrollTop] }")
        print("sticky top", top); await pg.screenshot(path=OUT + "ad_home_scrolled.png")
        if top[1] > 0 and abs(top[0]) > 2: bad.append("탭 줄이 안 붙음")
        # 공지 올리기
        await pg.click('#adTabs [data-t="notice"]'); await pg.wait_for_timeout(600)
        print("srv", await pg.evaluate("()=>document.querySelector('.adSrv').innerText"))
        pg.on("dialog", lambda d: asyncio.ensure_future(d.accept()))
        await pg.fill("#adNtText", "내일은 쉬는 날이에요"); await pg.click('[data-ad="ntDays"][data-d="1"]')
        await pg.click('[data-ad="ntPost"]'); await pg.wait_for_timeout(1500)
        nt = [x for x in st["posts"] if x.get("type") == "notice"]
        print("notice post", nt[-1] if nt else None)
        if not nt or nt[-1]["days"] != 1 or nt[-1]["tk"] != "testkey": bad.append("공지 보내기")
        lst = await pg.evaluate("()=>[...document.querySelectorAll('.adNt p')].map(p=>p.innerText)")
        print("list", lst)
        await pg.screenshot(path=OUT + "ad_notice_after.png")
        await pg.click('.adNt [data-ad="ntOff"]'); await pg.wait_for_timeout(1500)
        print("after off", await pg.evaluate("()=>[...document.querySelectorAll('.adNt p')].map(p=>p.innerText)"))
        # 원격 조치
        await pg.click('#adTabs [data-t="send"]'); await pg.wait_for_timeout(600)
        await pg.fill("#adWho", "SEOWON"); await pg.select_option("#adKind", "보석"); await pg.fill("#adVal", "+50"); await pg.fill("#adMemo", "시험 1등!")
        await pg.click('[data-ad="sendGo"]'); await pg.wait_for_timeout(1200)
        ac = [x for x in st["posts"] if x.get("type") == "actAdd"]
        print("act post", ac[-1] if ac else None, "|", await pg.evaluate("()=>document.getElementById('adMsg').innerText"))
        if not ac or ac[-1]["who"] != "SEOWON" or ac[-1]["value"] != "+50": bad.append("조치 보내기")
        await pg.select_option("#adKind", "선물"); await pg.wait_for_timeout(100)
        print("gift list", await pg.evaluate("()=>document.querySelectorAll('#adValList option').length"))
        await pg.screenshot(path=OUT + "ad_send_filled.png")
        # 고치기: 보석 +10
        await pg.click('#adTabs [data-t="fix"]'); await pg.wait_for_timeout(300)
        g0 = await pg.evaluate("()=>Wallet.gems()"); await pg.click('[data-ad="g"][data-n="10"]'); await pg.wait_for_timeout(200)
        g1 = await pg.evaluate("()=>Wallet.gems()"); print("gems", g0, g1)
        if g1 != g0 + 10: bad.append("보석 고치기")

        # 예전 서버(공지 모름): 보내기 단추가 막혀 있고 아무것도 안 보낸다
        st["v2"] = False; n0 = len(st["posts"])
        await pg.click('#adTabs [data-t="notice"]'); await pg.evaluate("()=>{ document.querySelector('[data-ad=recheck]').click(); }"); await pg.wait_for_timeout(1200)
        dis = await pg.evaluate("()=>document.querySelector('[data-ad=ntPost]').disabled")
        print("old server:", await pg.evaluate("()=>document.querySelector('.adSrv').innerText"), "| post disabled", dis, "| posts", len(st["posts"]) - n0)
        await pg.screenshot(path=OUT + "ad_notice_oldserver.png")
        if not dis or len(st["posts"]) != n0: bad.append("예전 서버에 보냄")
        # (v268) 열쇠가 없는 예전 세션: 설정 카드가 위에 펼쳐져 있고, 비밀번호 칸으로 열쇠를 만든다
        st["v2"] = True
        await pg.evaluate("()=>{ sessionStorage.removeItem('hyeng_admin_tk'); }")
        await pg.reload(); await pg.wait_for_timeout(1500)
        await pg.evaluate("()=>{ document.querySelectorAll('.sheet.on').forEach(s=>s.classList.remove('on')); Admin.open(); }"); await pg.wait_for_timeout(300)
        await pg.click('#adTabs [data-t="notice"]'); await pg.wait_for_timeout(900)
        card = await pg.evaluate("()=>{ const c=document.querySelector('.adSetupCard'); return c ? {vis: c.getBoundingClientRect().height>0, pin: !!document.getElementById('adPin2'), top: Math.round(c.getBoundingClientRect().top)} : null }")
        print("setup card (no key)", card)
        await pg.screenshot(path=OUT + "ad_setup_nokey.png")
        if not card or not card["vis"] or not card["pin"]: bad.append("설정 카드")
        e = real_errs(errs); print("errs", e)
        if e: bad.append("errors")
        if bad: print("BAD", bad)
        await br.close()
asyncio.run(main())
