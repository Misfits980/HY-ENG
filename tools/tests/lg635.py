# v635 🏅 나의 리그 「지난주 나 넘기」 — 실시간 랭킹 창 · 🏆 랭킹 화면 · 넘으면 한 번 축하 · 칭호 · 휴대폰/패드/가로
import asyncio, sys, os, subprocess, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *

OUT = os.environ.get("HY_OUT", "/tmp/lg635_")
bad = []
def ok(c, m):
    print(("OK  " if c else "BAD ") + m)
    if not c: bad.append(m)

def board(lg, ws=1762700000000):
    return {"study": [{"nick": "가온", "tag": "0006", "score": 1200, "n": 4}, {"nick": "나", "tag": "0009", "score": lg["now"] if lg else 0, "n": 2}],
            "words": [], "run": [], "ws": ws, "hof": None,
            "me": {"study": {"nick": "나", "tag": "0009", "score": lg["now"] if lg else 0, "n": 2, "rank": 2, "of": 2, "lv": "G3-4", "fix": 0}, **({"lg": lg} if lg else {})}}

LG = {
  "win":  {"now": 440, "last": 330, "keep": 300, "goal": 331, "st": 3, "hist": [330, 330, 330, 0, 0, 0], "win": 2},
  "keep": {"now": 310, "last": 330, "keep": 300, "goal": 331, "st": 5, "hist": [330] * 6, "win": 1},
  "low":  {"now": 120, "last": 400, "keep": 360, "goal": 401, "bar": 450, "st": 0, "hist": [400, 0, 0, 0, 0, 0], "win": 0},
  "first": {"now": 110, "last": 0, "keep": 300, "goal": 300, "st": 0, "hist": [0] * 6, "win": 0},
}
BOX = "()=>{ const b=document.querySelector('#lrPanel .lgBox'); if(!b) return null; const r=b.getBoundingClientRect(), p=document.querySelector('#lrPanel .lrP').getBoundingClientRect(); return {t:b.textContent, win:b.classList.contains('win'), w:Math.round(b.querySelector('.lgBar i').getBoundingClientRect().width), in:r.left>=p.left-1 && r.right<=p.right+1}; }"

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True); errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await boot(pg)
        await pg.evaluate("()=>{ LiveRank.fetch=()=>{}; localStorage.removeItem('hyeng_lg_win'); }")
        want = {"win": ("지난주 나를 넘었어요", "🌳 나무 · 3주째", True), "keep": ("지켰어요 · 넘기까지 21점", "🏅 꾸준왕 · 5주째", False),
                "low": ("기준보다 낮아서 목표가 기준 450점", None, False), "first": ("첫 주예요", None, False)}
        for k, (txt, title, win) in want.items():
            await pg.evaluate("(B)=>{ LiveRank.set(B, true); LiveRank.open('study'); }", board(LG[k])); await pg.wait_for_timeout(300)
            r = await pg.evaluate(BOX)
            ok(r and txt in r["t"] and (title is None and "주째" not in r["t"] or title and title in r["t"]) and r["win"] == win and r["in"], f"{k}: {r and r['t']}")
            if k == "keep": await pg.screenshot(path=OUT + "panel_ph.png")
            await pg.evaluate("()=>{ const d=document.getElementById('lrPanel'); if(d) d.remove(); }")
        # 다른 탭 · 옛 서버(lg 없음) = 상자 없음
        await pg.evaluate("(B)=>{ LiveRank.set(B, true); LiveRank.open('run'); }", board(LG["win"])); await pg.wait_for_timeout(200)
        ok(await pg.evaluate(BOX) is None, "달리기 탭 = 리그 상자 없음")
        await pg.evaluate("()=>document.getElementById('lrPanel').remove()")
        await pg.evaluate("(B)=>{ LiveRank.set(B, true); LiveRank.open('study'); }", board(None)); await pg.wait_for_timeout(200)
        ok(await pg.evaluate(BOX) is None, "옛 서버 (lg 없음) = 상자 없음 · 오류 없음")
        await pg.evaluate("()=>document.getElementById('lrPanel').remove()")
        # 넘으면 한 번 축하 (같은 주에 다시 안 함 · 다음 주엔 또)
        n = await pg.evaluate("""async (B)=>{ const c=()=>document.querySelectorAll('.lgToast').length; LiveRank.set(B, false); await new Promise(z=>setTimeout(z,900)); const a=c();
            LiveRank.set(B, false); await new Promise(z=>setTimeout(z,900)); const b2=document.querySelectorAll('.lgToast').length; return [a, b2, (document.querySelector('.lgToast')||{}).textContent||'']; }""", board(LG["win"]))
        ok(n[0] == 1 and n[1] == 1 and "넘었어요" in n[2], f"넘은 순간 축하 한 번 {n}")
        await pg.screenshot(path=OUT + "toast_ph.png")
        n = await pg.evaluate("""async (B)=>{ await new Promise(z=>setTimeout(z,4400)); LiveRank.set(B, false); await new Promise(z=>setTimeout(z,900)); return document.querySelectorAll('.lgToast').length; }""", board(LG["win"], ws=1763300000000))
        ok(n == 1, f"다음 주에 또 넘으면 다시 축하 {n}")
        n = await pg.evaluate("""async (B)=>{ await new Promise(z=>setTimeout(z,4400)); LiveRank.set(B, false); await new Promise(z=>setTimeout(z,900)); return document.querySelectorAll('.lgToast').length; }""", board(LG["keep"], ws=1763900000000))
        ok(n == 0, f"지키기만 하면 축하 없음 {n}")
        # 🏆 랭킹 화면 오늘의 30 탭에도
        await pg.evaluate("(B)=>{ LiveRank.set(B, true); showRank('study'); }", board(LG["keep"])); await pg.wait_for_timeout(500)
        r = await pg.evaluate("()=>{ const b=document.querySelector('#scRank .lgBox'); return b ? b.textContent : null; }")
        ok(r and "지켰어요" in r, f"🏆 랭킹 화면에도 리그 상자 {r}")
        await pg.screenshot(path=OUT + "rank_ph.png")
        e = real_errs(errs); ok(not e, f"오류 없음 {e[:3]}")
        await pg.close()
        for nm, vp in (("pad", (820, 1180)), ("phL", (915, 412)), ("padL", (1180, 820))):
            pg = await b.new_page(viewport={"width": vp[0], "height": vp[1]}, is_mobile=True, has_touch=True); await boot(pg)
            await pg.evaluate("(B)=>{ LiveRank.fetch=()=>{}; LiveRank.set(B, true); LiveRank.open('study'); }", board(LG["low"])); await pg.wait_for_timeout(400)
            r = await pg.evaluate(BOX)
            w = await pg.evaluate("()=>document.documentElement.scrollWidth-innerWidth")
            ok(r and r["in"] and w <= 0, f"{nm} 리그 상자 칸 안 · 넘침 없음 {r and r['in']} {w}")
            await pg.screenshot(path=f"{OUT}panel_{nm}.png")
            await pg.close()
        await b.close()
    for js in ("gs_lg635.js", "gs_lg638.js"):
        r = subprocess.run(["node", os.path.join(os.path.dirname(os.path.abspath(__file__)), js)], capture_output=True, text=True)
        print((r.stdout.strip().splitlines() or [r.stderr[:200]])[-1])
        ok(r.returncode == 0, "서버 나의 리그 (" + js + ")")
    print("PASS" if not bad else "FAIL", len(bad))
    if bad: sys.exit(1)

asyncio.run(main())
