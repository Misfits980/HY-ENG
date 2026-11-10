# v636 ⚔️ 스테이지 도전장 — 💜2 판 · 같은 씨앗 = 같은 문제 · 보내기(친구 고르기) · 받은 도전장 · 승패 · 보석 · 옛 서버 숨김 · 휴대폰/패드/가로
import asyncio, sys, os, subprocess, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *

OUT = os.environ.get("HY_OUT", "/tmp/duel636_")
bad = []
def ok(c, m):
    print(("OK  " if c else "BAD ") + m)
    if not c: bad.append(m)

# 서버 흉내 (한 페이지 안 · 서버 v17)
MOCK = """(v)=>{ window._srv=window._srv||{rows:[], posts:[]}; const S=window._srv; Online.on=()=>true;
  try{ Tag.get=()=> '0006'; Tag.pad=()=>false; }catch(e){}
  Online.submit=o=>{ S.posts.push(JSON.parse(JSON.stringify(o))); if(v<17 && /^duel/.test(o.type||'')) return Promise.resolve({ok:false, err:'type'});
    if(o.type==='duelFriends') return Promise.resolve({ok:true, v, list:[{id:'#0006',nick:'나',tag:'0006'},{id:'#0007',nick:'나래',tag:'0007'},{id:'#0008',nick:'다솜',tag:'0008'},{id:'민수',nick:'민수',tag:''}]});
    if(o.type==='duelSend'){ const id=String(S.rows.length+100); S.rows.push(Object.assign({id, at:Date.now(), from:o.me, st:'wait', tsc:0, ttot:0, tms:0}, o)); return Promise.resolve({ok:true, v, id}); }
    if(o.type==='duelBox'){ const me=o.me; return Promise.resolve({ok:true, v, inbox:S.rows.filter(r=>r.to===me && r.st==='wait'), sent:S.rows.filter(r=>r.from===me), got:S.rows.filter(r=>r.to===me && r.st!=='wait')}); }
    if(o.type==='duelDone'){ const r=S.rows.find(x=>x.id===o.id); Object.assign(r, {tsc:o.sc, ttot:o.tot, tms:o.ms, st:'done', dat:Date.now()}); return Promise.resolve({ok:true, v, d:r}); }
    return Promise.resolve({ok:true}); };
  Duel.sv=0; Duel._bT=0; Duel.fr=null; }"""
SIG = "()=>StudyUI.qs.map(q=>q.t+':'+(q.w&&q.w.en)+':'+((q.opts||[]).map(o=>o&&o.en||o).join('|'))+':'+(q.x&&q.x.full||q.s||'')).join('~')"
PLAY = """async (n)=>{ let k=0, wrong=0; while(k++<200){ const q=StudyUI.qs[StudyUI.i]; if(!q) break; const w = wrong<n && q.t!=='intro'; if(w) wrong++; await window.__solve(w); await new Promise(z=>setTimeout(z,30)); } return [StudyUI.first, StudyUI.total]; }"""

async def setup(b, vp, v=17, me="0006", **kw):
    pg = await b.new_page(viewport=vp, **kw); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    await boot(pg)
    await pg.evaluate("(s)=>{ window.__solve=new Function('return ('+s+')')(); }", SOLVE)
    await pg.evaluate(MOCK, v)
    await pg.evaluate("(t)=>{ Tag.get=()=>t; $('nick').value=t==='0006'?'가온':'나래'; }", me)
    return pg, errs

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg, errs = await setup(b, {"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        # 같은 씨앗 = 같은 문제 (두 번 만들어도) · 다른 씨앗 = 다름
        r = await pg.evaluate("""()=>{ const sg=q=>q.map(x=>x.t+':'+(x.w&&x.w.en)+':'+((x.opts||[]).map(o=>o&&o.en||o).join('|'))).join('~'); const a=sg(Duel.build('elem',101,777)), b2=sg(Duel.build('elem',101,777)), c=sg(Duel.build('elem',101,778)); const q=Duel.build('elem',101,777); return [a===b2, a!==c, q.length, q.filter(x=>x.tg==='💜2').length, q.some(x=>x.tm)]; }""")
        ok(r[0] and r[1] and r[3] >= 10, f"같은 씨앗 = 같은 문제 · 다른 씨앗 = 다른 순서 · 💜2 문제 {r}")
        # Stage 창: 깬 Stage 에 「⚔️ 친구에게 도전장」 (서버 v17)
        await pg.evaluate("()=>Duel.poll(true)"); await pg.wait_for_timeout(300)
        await pg.evaluate("()=>{ const s=Study.load(); s.book='g34'; Study.save(); StudyUI.open(); }"); await pg.wait_for_timeout(700)
        r = await pg.evaluate("""()=>{ const set=StudyUI.set, L=Study.lessons(set); Study.setLv(set, L[0].n, 3); StudyUI.path(); StudyUI.pop(0); return [!!document.querySelector('#stPop .stDuelB'), Study.lv(set, L[0].n), set]; }""")
        ok(r[0], f"깬 Stage 창에 ⚔️ 친구에게 도전장 {r}")
        r2 = await pg.evaluate("()=>{ StudyUI.pop(5); return !!document.querySelector('#stPop .stDuelB'); }")
        ok(not r2, "안 깬 Stage = 도전장 버튼 없음")
        await pg.evaluate("()=>StudyUI.pop(0)"); await pg.wait_for_timeout(200)
        await pg.screenshot(path=OUT + "pop_ph.png")
        # 보내기: 내가 먼저 풂 (2개 틀림)
        await pg.evaluate("()=>document.querySelector('#stPop .stDuelB').click()"); await pg.wait_for_function("()=>!!StudyUI.duel", timeout=12000); await pg.wait_for_timeout(400)
        sigA = await pg.evaluate(SIG)
        r = await pg.evaluate("()=>[!!StudyUI.duel, StudyUI.tier, StudyUI.dl, StudyUI.retryMode, (StudyUI.qs[1]||{}).tg]")
        ok(r[0] and r[1] == 3 and r[2] == 2 and r[3] and r[4] == "💜2", f"도전 판 = 💜2 · 다시 안 냄 {r}")
        await pg.screenshot(path=OUT + "q_ph.png")
        sc = await pg.evaluate(PLAY, 2); await pg.wait_for_timeout(1200)
        t = await pg.evaluate("()=>document.getElementById('stDoneIn').textContent")
        fr = await pg.evaluate("()=>[...document.querySelectorAll('#duFr button')].map(b=>b.dataset.to)")
        ok("도전장 준비 끝" in t and str(sc[0]) in t and "#0006" not in fr and "#0007" in fr and "민수" in fr, f"끝 = 내 점수 {sc} · 친구 목록(나 빼고) {fr}")
        await pg.fill("#duQ", "나래"); await pg.wait_for_timeout(200)
        fr = await pg.evaluate("()=>[...document.querySelectorAll('#duFr button')].map(b=>b.dataset.to)")
        ok(fr == ["#0007"], f"친구 찾기 {fr}")
        await pg.screenshot(path=OUT + "send_ph.png")
        gem0 = await pg.evaluate("()=>Wallet.gems ? Wallet.gems() : (JSON.parse(localStorage.getItem('hyeng_wallet')||'{}').gems||0)")
        await pg.evaluate("()=>document.querySelector('#duFr button').click()"); await pg.wait_for_timeout(500)
        r = await pg.evaluate("()=>[document.getElementById('stDoneIn').textContent, window._srv.rows[0]]")
        row = r[1]
        ok("나래에게 보냈어요" in r[0] and row["to"] == "#0007" and row["me"] == "#0006" and row["fsc"] == sc[0] and row["ftot"] == sc[1] and row["set"] == "elem" and row["seed"] > 0 and "Stage" in row["label"],
           f"보냄 → 서버 줄 {json.dumps({k: row[k] for k in ('to','me','set','n','seed','fsc','ftot','label')}, ensure_ascii=False)}")
        ok(await pg.evaluate("()=>StudyUI.duel===null"), "보내기 판 끝 = 별·기록 없음 (도전 상태 비움)")
        e = real_errs(errs); ok(not e, f"보내는 쪽 오류 없음 {e[:3]}")
        srv = await pg.evaluate("()=>{ window._srv.rows[0].fsc=Math.max(0, window._srv.rows[0].ftot-4); return window._srv; }")   # 보낸 아이 점수를 낮춰 받는 쪽이 이기게
        await pg.close()
        # 받는 쪽 (나래) — 첫 화면 ⚔️ 도전장 1 · 도전! → 같은 문제 → 이김(다 맞힘) → 💎3
        pg, errs = await setup(b, {"width": 390, "height": 844}, me="0007", is_mobile=True, has_touch=True)
        await pg.evaluate("(S)=>{ window._srv=S; }", srv); await pg.evaluate(MOCK, 17); await pg.evaluate("()=>{ Tag.get=()=>'0007'; $('nick').value='나래'; }")
        await pg.evaluate("()=>Duel.poll(true)"); await pg.wait_for_timeout(400)
        r = await pg.evaluate("()=>[!document.getElementById('btnDuel').hidden, document.getElementById('duelN').textContent, !document.getElementById('duelN').hidden]")
        ok(r == [True, "1", True], f"첫 화면 ⚔️ 도전장이 왔어요 알약 · 받은 수 {r}")
        await pg.screenshot(path=OUT + "start_ph.png")
        await pg.evaluate("()=>document.getElementById('btnDuel').click()"); await pg.wait_for_timeout(500)
        t = await pg.evaluate("()=>document.getElementById('duelMt').textContent")
        ok("가온" in t and "도전!" in t and "Stage" in t, f"받은 도전장 창 {t[:80]}")
        await pg.screenshot(path=OUT + "box_ph.png")
        g0 = await pg.evaluate("()=>Wallet.gems()")
        await pg.evaluate("()=>document.querySelector('#duelMt [data-go]').click()"); await pg.wait_for_function("()=>!!StudyUI.duel", timeout=12000); await pg.wait_for_timeout(400)
        sigB = await pg.evaluate(SIG)
        ok(sigA == sigB and len(sigA) > 50, f"받은 쪽 = 보낸 쪽과 같은 문제 ({len(sigA)}자)")
        sc2 = await pg.evaluate(PLAY, 0); await pg.wait_for_timeout(1300)
        t = await pg.evaluate("()=>document.getElementById('stDoneIn').textContent")
        row = await pg.evaluate("()=>window._srv.rows[0]")
        g1 = await pg.evaluate("()=>Wallet.gems()")
        ok("이겼어요" in t and row["st"] == "done" and row["tsc"] == sc2[0] and sc2[0] > row["fsc"], f"이김 · 결과 보냄 {sc2} vs {sc} · {t[:40]}")
        ok(g1 - g0 == 3, f"이기면 💎3 (끝까지 1 + 이김 2) {g0}→{g1}")
        await pg.screenshot(path=OUT + "win_ph.png")
        # 결과 탭
        await pg.evaluate("()=>{ Duel.poll(true); }"); await pg.wait_for_timeout(300)
        await pg.evaluate("()=>{ Duel.tab='res'; Duel.open(); }"); await pg.wait_for_timeout(500)
        t = await pg.evaluate("()=>document.getElementById('duelMt').textContent")
        ok("🏆 이김" in t and "가온" in t, f"결과 탭 {t[:90]}")
        await pg.evaluate("()=>document.getElementById('duelMt').remove()")
        # 하루 보석 3판까지
        n = await pg.evaluate("()=>{ const a=[]; for(let i=0;i<4;i++) a.push(Duel.gem(1)); return a; }")
        ok(n == [3, 3, 0, 0], f"보석은 하루 3판까지 {n}")
        e = real_errs(errs); ok(not e, f"받는 쪽 오류 없음 {e[:3]}")
        await pg.close()
        # 옛 서버 = 버튼 숨김
        pg, errs = await setup(b, {"width": 390, "height": 844}, v=15, is_mobile=True, has_touch=True)
        await pg.evaluate("()=>Duel.poll(true)"); await pg.wait_for_timeout(300)
        r = await pg.evaluate("()=>[document.getElementById('btnDuel').hidden, Duel.on()]")
        ok(r == [True, False], f"옛 서버 = ⚔️ 버튼 없음 {r}")
        await pg.close()
        # 패드 · 가로: 보내기 끝 화면 · 결과 화면 넘침 없음 · 버튼 화면 안
        for nm, vp in (("pad", (820, 1180)), ("phL", (915, 412)), ("padL", (1180, 820))):
            pg, errs = await setup(b, {"width": vp[0], "height": vp[1]}, is_mobile=True, has_touch=True)
            await pg.evaluate("()=>Duel.poll(true)"); await pg.wait_for_timeout(200)
            await pg.evaluate("()=>{ const s=Study.load(); s.book='g34'; Study.save(); StudyUI.open(); Duel.make('elem', 101); }"); await pg.wait_for_function("()=>!!StudyUI.duel", timeout=12000); await pg.wait_for_timeout(400)
            await pg.evaluate(PLAY, 1); await pg.wait_for_timeout(1500)
            r = await pg.evaluate("""()=>{ const S=document.getElementById('scStudy'); const bs=[...document.querySelectorAll('#stDoneIn button')].filter(b=>b.offsetParent).map(b=>Math.round(b.getBoundingClientRect().bottom)); return [S.scrollHeight-S.clientHeight, document.documentElement.scrollWidth-innerWidth, bs.length, Math.max(...bs)]; }""")
            ok(r[1] <= 0 and r[2] >= 3 and (r[0] <= 2 or nm == "phL"), f"{nm} 보내기 끝 화면 {r}")
            await pg.screenshot(path=f"{OUT}send_{nm}.png")
            e = real_errs(errs); ok(not e, f"{nm} 오류 없음 {e[:3]}")
            await pg.close()
        await b.close()
    r = subprocess.run(["node", os.path.join(os.path.dirname(os.path.abspath(__file__)), "gs_duel636.js")], capture_output=True, text=True)
    print((r.stdout.strip().splitlines() or [r.stderr[:200]])[-1])
    ok(r.returncode == 0, "서버 도전장 (gs_duel636.js)")
    print("PASS" if not bad else "FAIL", len(bad))
    if bad: sys.exit(1)

asyncio.run(main())
