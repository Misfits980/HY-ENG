"""(v738) 📺 수업 게임 대기 화면 v4 — 사용자: 「애들한테 화면 띄울 때 관리자 창이 보이면 이상」 → 「시안처럼 해 봐」
   ① 교실 배틀(개인 · 두 팀 · 반 깃발) · 달리기 레이스 · 레이드 · 파티 보드 대기 화면 = 게임 그림 · 📚 오늘 단어 · 이름 · 규칙 한 줄 · 방 번호 · 얼굴 · ▶ 시작
   ② 선생님 TV 에 ✕ 없음 · 구석 🔒 — 톡 = 「1초 꾹」 안내만 · 꾹 = 선생님 메뉴 (그 상태 단추만) · 메뉴로 끝내기/멈춤이 됨
   ③ 달리는 중 화면에 「🏁 지금 끝내기」 · 레이드 「⏸ ⚡ ➕ 🏁」 단추 안 보임 (🔒 메뉴로)
   ④ 1280×720 · 1920×1080 · 세로 패드(820×1180) 에서 넘침·겹침 없음 (시작 단추가 화면 안 · 판 안쪽이 안 잘림)"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright
KN = ["토토", "별사탕", "콩콩", "젤리", "마루", "쿠키", "포포"]; CH = ["hero", "explorer", "archer", "mage", "knight", "scholar", "cat"]
RNG = "()=>{ const L=Study.lessons('g56'); return [L.findIndex(x=>Study.stageNo('g56',x.n)==='6-1'), L.findIndex(x=>Study.stageNo('g56',x.n)==='6-4')]; }"
HOST = {
    "bt": "([f,t])=>Battle.host({set:'g56', from:f, to:t, words:[], dur:300, team:false, mode:'score', qt:['mean'], lvl:'exam', lbl:'G5-6', cls:'all'})",
    "auto": "([f,t])=>Battle.host({set:'g56', from:f, to:t, words:[], dur:300, team:true, mode:'auto', goal:0, qt:['mean'], lvl:'exam', lbl:'G5-6', cls:'all', fun:true})",
    "run": "([f,t])=>Battle.host({kind:'run', rng:'stg', rset:'g56', diff:'normal', dur:180, mode:'score', set:'g56', from:f, to:t, words:[], lbl:'달리기', cls:'all'})",
    "rd": "()=>{ Raid.MIN=1000; return Raid.host('g56', [], 0, null, 900, 'all'); }",
    "bd": "async ([f,t])=>{ BoardTV.host({sk:'e', set:'g56', from:f, to:t, qt:['mean'], sec:20, rounds:10}); for(let k=0;k<40 && !BoardTV.room;k++) await new Promise(z=>setTimeout(z,100)); return BoardTV.room; }",
}
FIT = """()=>{ const H=innerHeight - (document.body.classList.contains('tcOn') ? 64 : 0), go=[...document.querySelectorAll('.lb4Btn')].map(b=>Math.round(b.getBoundingClientRect().bottom));
  const B=document.querySelector('#scRaid.on #rdB') || document.querySelector('#board .bdLob'), clip = B && getComputedStyle(B).overflowY!=='visible' ? B.scrollHeight - B.clientHeight : 0;
  const code=document.querySelector('.lb4Code b'), cr=code && code.getBoundingClientRect(); return {H, go, clip, ox:document.documentElement.scrollWidth-innerWidth, code: cr ? [Math.round(cr.left), Math.round(cr.right)] : null}; }"""
async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch()
        for vw, vh in ((1280, 720), (1920, 1080), (820, 1180)):
            for k in ("bt", "auto", "run", "rd", "bd"):
                if (vw, vh) != (1280, 720) and k not in ("auto", "rd", "bd"): continue
                ctx = await br.new_context(viewport={"width": vw, "height": vh}, service_workers="block"); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
                T = await ctx.new_page(); T.on("pageerror", lambda e: errs.append(str(e))); E = T.evaluate
                await boot(T); await E("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); document.querySelectorAll('.sheet.on').forEach(s=>s.classList.remove('on')); try{ Voice.speak=()=>{}; }catch(e){} }")
                f, t = await E(RNG); room = await E(HOST[k], [f, t]); await T.wait_for_timeout(900)
                path = ("/raids/" if k == "rd" else "/battle/") + str(room)
                await E("""([path,K,C,raid])=>K.forEach((n,i)=>{ const o={n, c:C[i], at: raid ? Raid.now() : Date.now(), dv:'pad'}; if(raid) Object.assign(o,{e:'🙂',d:0,b:0,sh:0,h:0,m:0,t:'all'}); FB.update(path+'/p/k'+i, o); })""", [path, KN, CH, k == "rd"])
                await T.wait_for_timeout(2200)
                tag = f"{k}@{vw}x{vh}"
                r = await E("""()=>{ const S=document.querySelector('#scRaid.on') || document.getElementById('board'); const tx=S ? S.innerText : '';
                    return {lb4:!!document.querySelector('.lb4'), lock:!!document.querySelector('.lb4Lock'), x:[...document.querySelectorAll('#scRaid.on .rdX, #board .bdX')].filter(e=>e.offsetParent).length,
                      h1:(document.querySelector('.lb4H h1')||{}).textContent||'', code:(document.querySelector('.lb4Code b')||{}).textContent||'', faces:document.querySelectorAll('.lb4K, #board .lbKid, .rsHero').length,
                      teams:document.querySelectorAll('.lb4T, #board .lbTeam').length, word:tx.indexOf('오늘 단어')>=0, go:document.querySelectorAll('.lb4Btn').length}; }""")
                ok(r["lb4"] and r["lock"] and r["x"] == 0 and r["word"] and r["go"] == 1 and r["code"] in (str(room), ""), f"① {tag} 대기 화면 v4 · 🔒 · ✕ 없음 · 오늘 단어 · 시작 단추 {r}")
                ok(r["code"] == str(room) or k == "bd", f"① {tag} 방 번호 크게 {r['code']} = {room}")
                if k == "bd": ok(await E("()=>document.getElementById('lbRoom').textContent") == str(room), f"① {tag} 보드 방 번호 {room}")
                if k in ("bt", "run"): ok(r["faces"] == 7, f"① {tag} 들어온 친구 얼굴 7 {r['faces']}")
                if k in ("auto", "bd"): ok(r["teams"] == 2, f"① {tag} 두 팀 판 {r['teams']}")
                if k == "rd": ok("를 쓰러뜨려라" in r["h1"] and "초원 수호자" in r["h1"], f"① {tag} 보스 이름 · 받침 맞는 조사 {r['h1']}")
                fit = await E(FIT)
                ok(all(g <= fit["H"] for g in fit["go"]) and fit["clip"] <= 2 and fit["ox"] <= 0, f"④ {tag} 시작 단추 화면 안 · 판 안 잘림 · 옆 넘침 없음 {fit}")
                if (vw, vh) == (1280, 720):
                    # ② 🔒 톡 = 안내만 · 꾹 = 메뉴
                    r = await E("""async ()=>{ const L=document.querySelector('.lb4Lock'); L.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true})); L.dispatchEvent(new PointerEvent('pointerup',{bubbles:true})); L.click(); await new Promise(z=>setTimeout(z,150));
                        const tap=[!!document.querySelector('.lb4Hint'), !!document.getElementById('lb4Menu')];
                        L.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true})); await new Promise(z=>setTimeout(z,1000)); L.dispatchEvent(new PointerEvent('pointerup',{bubbles:true})); L.click();
                        return [tap, [...document.querySelectorAll('#lb4Menu .lb4MB')].map(b=>b.textContent)]; }""")
                    ok(r[0] == [True, False] and any("시작" in x for x in r[1]) and any("관리로" in x for x in r[1]), f"② {tag} 🔒 톡 = 안내 · 꾹 = 메뉴(시작 · 관리로) {r}")
                    if k in ("auto", "rd"):
                        # ▶ 메뉴의 시작 → 달리는 중 → ③ 화면에 끝내기 단추 없음 · 메뉴로 끝내기
                        await E("()=>document.querySelector('#lb4Menu .lb4MB.gold').click()"); await T.wait_for_timeout(5200)
                        r = await E("""()=>({s:(typeof Battle!=='undefined' && Battle.role==='host' ? Battle.st().s : Raid.st().s), lb4:!!document.querySelector('#scRaid.lb4'), lock:!!document.querySelector('#scRaid.on .lb4Lock'),
                            btns:[...document.querySelectorAll('#scRaid.on #rdC button')].filter(b=>b.offsetParent).map(b=>b.textContent), x:[...document.querySelectorAll('#scRaid.on .rdX')].filter(e=>e.offsetParent).length})""")
                        ok(r["s"] in ("run", "count") and not r["lb4"] and r["lock"] and r["x"] == 0 and not any(("끝내기" in b or "멈춤" in b or "분노" in b) for b in r["btns"]), f"③ {tag} 달리는 중: 🔒 만 · 끝내기·멈춤 단추 안 보임 {r}")
                        if k == "rd":
                            await E("()=>{ const L=document.querySelector('#scRaid.on .lb4Lock'); L.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true})); }"); await T.wait_for_timeout(1000)
                            m = await E("()=>{ document.querySelector('#scRaid.on .lb4Lock').dispatchEvent(new PointerEvent('pointerup',{bubbles:true})); return [...document.querySelectorAll('#lb4Menu .lb4MB')].map(b=>b.textContent); }")
                            ok(any("멈춤" in x for x in m) and any("분노" in x for x in m) and any("3분" in x for x in m) and any("끝내기" in x for x in m), f"③ {tag} 레이드 🔒 메뉴 = 멈춤 · 분노 · 3분 · 끝내기 · 관리로 {m}")
                            await E("()=>[...document.querySelectorAll('#lb4Menu .lb4MB')].find(b=>b.textContent.indexOf('멈춤')>=0).click()"); await T.wait_for_timeout(700)
                            ok(await E("()=>Raid.st().s") == "pause" and not await E("()=>!!document.getElementById('lb4Menu')"), "③ 메뉴 「⏸ 잠깐 멈춤」 → 멈춤 · 메뉴 닫힘")
                        else:
                            await E("()=>{ const L=document.querySelector('#scRaid.on .lb4Lock'); L.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true})); }"); await T.wait_for_timeout(1000)
                            await E("()=>{ document.querySelector('#scRaid.on .lb4Lock').dispatchEvent(new PointerEvent('pointerup',{bubbles:true})); const b=[...document.querySelectorAll('#lb4Menu .lb4MB')].find(x=>x.textContent.indexOf('끝내기')>=0); b.click(); }"); await T.wait_for_timeout(1500)
                            ok(await E("()=>Battle.st().s") == "end", "③ 메뉴 「🏁 지금 끝내기」 → 끝")
                await ctx.close()
        await br.close()
    e = real_errs(errs); ok(not e, f"오류 없음 {e[:3]}")
    print("BAD: %d" % len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
