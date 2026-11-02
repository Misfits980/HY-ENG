"""(v563) 새 경제 — 게임 쪽
   · 🪱 Daily 30 한 판을 끝까지 → My Town 미끼 +5 (Kid.k("hyeng_town_inbox") = {bait})  · 결과 화면에 「🪱 +5 My Town 미끼」
   · 🏃 달리기 15단계 넘게 → +3 · 짧은 판 0 · 시험·연습 판 없음 · 결과 화면 줄
   · ⏸ 화면을 가린(뒤로 보낸) 시간은 플레이 시간에서 뺌 — Daily 30 · 달리기 · 시트 플레이(초) 1시간까지 · ⏰ 시간 막대
   · 시트 줄에 🏝 마을 칸(coin·bait·bank·gbank·tup) — Kid.k("hyeng_town_sum")
   · 관리 화면 📊 이 기기 「🏝 My Town」 · 📋 우리 반 🪙·🪱·🏦 칸 · 🏝 반 전체 표
   · server/Code.gs v8 (node gs_town563.js)"""
import asyncio, os, sys, json, subprocess
from playwright.async_api import async_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *

CLOCK = """()=>{ if(window._dn) return; window._dn=Date.now.bind(Date); window._off=0; Date.now=()=>window._dn()+window._off;
  window._hid=false; Object.defineProperty(document,'hidden',{configurable:true, get:()=>window._hid}); Object.defineProperty(document,'visibilityState',{configurable:true, get:()=>window._hid?'hidden':'visible'});
  window.hideFor=(ms)=>{ window._hid=true; document.dispatchEvent(new Event('visibilitychange')); window._off+=ms; window._hid=false; document.dispatchEvent(new Event('visibilitychange')); };
  window._rows=[]; Online.on=()=>true; Online.post=b=>{ window._rows.push(JSON.parse(JSON.stringify(b))); return Promise.resolve({ok:true}); }; Online.top=()=>Promise.resolve(null);
  window._day=[]; HyDay.add=(inc,best,who,a0)=>{ window._day.push({inc, a0, now:Date.now()}); }; }"""
INBOX = "()=>{ try{ return JSON.parse(localStorage.getItem(Town.k('hyeng_town_inbox'))||'null'); }catch(e){ return 'bad'; } }"
SUM = {"coin": 340, "bait": 7, "bank": 1200, "gbank": 55, "tup": "낚싯대2 가방1 밭0", "at": 1762000000000}

async def solve_all(pg, hide_at=None):
    for step in range(260):
        if await pg.evaluate("()=>document.getElementById('stDone').style.display!=='none'"): return True
        if hide_at is not None and step == hide_at: await pg.evaluate("()=>hideFor(40*60000)")   # 공부하다 40분 동안 탭을 뒤로
        r = await pg.evaluate(SOLVE, False)
        await pg.wait_for_timeout(450 if r == 'drag' else 15)
    return await pg.evaluate("()=>document.getElementById('stDone').style.display!=='none'")

RUN_END = """(o)=>{ G.set='basic'; G.lesson=0; G.book=null; G.words=null; G.rule='normal'; G.diff='normal'; G.testRun=!!o.test; G.practice=!!o.prac; G.cleared=false; G.quit=true; G._gemDone=false;
  G.score=1500; G.stage=o.stage; G.zone=o.stage>=15?2:1; G.right=12; G.wrong=2; G.running=false; G.skipOutro=true; G.overFade=false; G._overDone=false; gameOver(); G.skipOutro=false;
  return {gems:(document.getElementById('oGems')||{}).innerText||''}; }"""

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    # 서버 (Code.gs v8) — 노드로 가짜 시트
    g = subprocess.run(["node", os.path.join(HERE, "gs_town563.js")], capture_output=True, text=True)
    print(g.stdout.strip().splitlines()[-1] if g.stdout.strip() else g.stderr[:300])
    ok(g.returncode == 0 and "bad=0" in g.stdout, "server/Code.gs v8 (gs_town563.js)")
    g2 = subprocess.run(["node", os.path.join(HERE, "gs_tag.js")], capture_output=True, text=True)
    ok(g2.returncode == 0 and "bad=0" in g2.stdout, "server/Code.gs 예전 검사 (gs_tag.js) 그대로")
    async with async_playwright() as p:
        br = await p.chromium.launch()
        pg = await br.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await boot(pg); await pg.evaluate(CLOCK)
        ok(await pg.evaluate("()=>Town.k('hyeng_town_inbox')") == "hyeng_town_inbox", "내 기기 = 받은 편지함 hyeng_town_inbox")
        ok(await pg.evaluate("()=>JSON.stringify(Town.fields())") == "{}", "마을 요약이 없으면 칸 없음 (안 터짐)")
        await pg.evaluate("()=>localStorage.setItem('hyeng_town_sum','{bad json')")
        ok(await pg.evaluate("()=>JSON.stringify(Town.fields())") == "{}", "마을 요약이 깨져 있어도 안 터짐")

        # ── 📚 Daily 30 한 판 (중간에 40분 뒤로 보냄) ──
        await pg.evaluate("()=>{ StudyUI.open(); }"); await pg.wait_for_timeout(900)
        await pg.evaluate("()=>{ StudyUI.book='mid'; StudyUI.path(); StudyUI.set='mid'; StudyUI.start(0,false); }"); await pg.wait_for_timeout(300)
        done = await solve_all(pg, hide_at=6)
        ok(done, "Daily 30 한 판 끝")
        await pg.wait_for_timeout(300)
        ib = await pg.evaluate(INBOX)
        ok(ib == {"bait": 5}, f"Daily 30 끝 → 편지함 미끼 +5 {ib}")
        txt = await pg.evaluate("()=>document.getElementById('stDoneIn').innerText")
        ok("🪱 +5" in txt and "My Town 미끼" in txt, "결과 화면에 🪱 +5 My Town 미끼")
        await pg.screenshot(path=OUT + "econ563_study_done.png")
        rows = await pg.evaluate("()=>window._rows.filter(r=>r.diff==='study')")
        ok(len(rows) == 1 and rows[0]["secs"] < 600, f"공부 플레이(초)에 뒤로 보낸 40분이 안 들어감 secs={rows[0]['secs'] if rows else None}")
        dy = await pg.evaluate("()=>window._day.filter(d=>d.inc.s)")
        ok(len(dy) == 1 and dy[0]["now"] - dy[0]["a0"] < 10 * 60000, f"⏰ 공부 시간 막대 = 실제로 푼 시간 ({round((dy[0]['now']-dy[0]['a0'])/60000,1) if dy else '-'}분)")
        # 같은 판 결과를 다시 그려도 두 번 안 줌
        await pg.evaluate("()=>{ try{ StudyUI.finish(true); }catch(e){} }"); await pg.wait_for_timeout(200)
        ok(await pg.evaluate(INBOX) == {"bait": 5}, "같은 판은 한 번만 (+5 그대로)")
        # 두 번째 판 → +5 더 · 가득(20)이면 「가득」
        await pg.evaluate("()=>{ document.getElementById('stBack').click(); StudyUI.set='mid'; StudyUI.start(1,false); }"); await pg.wait_for_timeout(300)
        await solve_all(pg); await pg.wait_for_timeout(200)
        ok(await pg.evaluate(INBOX) == {"bait": 10}, "두 번째 판 → 10")
        await pg.evaluate("()=>localStorage.setItem('hyeng_town_inbox', JSON.stringify({bait:20, x:1}))")
        await pg.evaluate("()=>{ document.getElementById('stBack').click(); StudyUI.set='mid'; StudyUI.start(2,false); }"); await pg.wait_for_timeout(300)
        await solve_all(pg); await pg.wait_for_timeout(200)
        ib = await pg.evaluate(INBOX); txt = await pg.evaluate("()=>document.getElementById('stDoneIn').innerText")
        ok(ib == {"bait": 20, "x": 1} and "미끼 가득" in txt, f"편지함 20 이면 그대로 · 「미끼 가득」 · 다른 칸은 안 지움 {ib}")
        # 건너뛰기 시험은 미끼 없음
        await pg.evaluate("()=>localStorage.removeItem('hyeng_town_inbox')")
        await pg.evaluate("()=>{ document.getElementById('stBack').click(); StudyUI.set='mid'; StudyUI.test=true; StudyUI.finish(true); }"); await pg.wait_for_timeout(200)
        ok(await pg.evaluate(INBOX) is None, "건너뛰기 시험 = 미끼 없음")
        await pg.evaluate("()=>{ StudyUI.test=false; try{ document.getElementById('stBack').click(); }catch(e){} StudyUI.close && StudyUI.close(); show('scStart'); }")

        # ── 🏃 달리기 ──
        await pg.evaluate("()=>localStorage.removeItem('hyeng_town_inbox')")
        # 40분 뒤로 보냄 (넘어지는 연출 중이라 멈출 수 없는 때) + 10분 멈춤 → 플레이(초)에서 둘 다 뺌
        await pg.evaluate("""()=>{ window._rows.length=0; G.runStart=Date.now()-120000; G.pauseMs=0; G.pauseAt=0; G.hidAt=0; G.running=true; G.paused=false; G.overFade=true;
          hideFor(40*60000); G.overFade=false; togglePause(); window._off+=10*60000; togglePause(); }""")
        a = await pg.evaluate("()=>Math.round(runActMs()/1000)")
        ok(110 <= a <= 140, f"달리기: 뒤로 보낸 40분·멈춘 10분 뺌 → {a}초")
        r = await pg.evaluate(RUN_END, {"stage": 16})
        ib = await pg.evaluate(INBOX)
        ok(ib == {"bait": 3}, f"16단계 판 → 미끼 +3 {ib}")
        ok("🪱 +3" in r["gems"], "결과 화면에 🪱 +3 " + r["gems"].replace("\n", " ")[:120])
        await pg.screenshot(path=OUT + "econ563_run_over.png")
        rr = await pg.evaluate("()=>window._rows.filter(r=>r.diff==='normal')")
        ok(len(rr) == 1 and rr[0]["secs"] <= 150, f"달리기 줄 플레이(초) {rr[0]['secs'] if rr else None}")
        rd = await pg.evaluate("()=>window._day.filter(d=>d.inc.r).slice(-1)[0]")
        ok(rd and rd["inc"]["rs"] <= 150 and rd["now"] - rd["a0"] <= 150000, f"📅·⏰ 달리기 시간 = 실제로 달린 시간 rs={rd and rd['inc']['rs']}")
        await pg.evaluate("()=>{ G.runStart=Date.now()-60000; G.pauseMs=0; G.pauseAt=0; G.hidAt=0; }")
        r = await pg.evaluate(RUN_END, {"stage": 9})
        ok(await pg.evaluate(INBOX) == {"bait": 3}, "9단계 판 → 미끼 0 (그대로 3)")
        ok("15단계까지 달리면" in r["gems"], "짧은 판 결과에 「15단계까지 달리면 미끼 +3」")
        await pg.evaluate("()=>{ G.runStart=Date.now()-60000; }")
        await pg.evaluate(RUN_END, {"stage": 30, "prac": True}); await pg.evaluate(RUN_END, {"stage": 30, "test": True})
        ok(await pg.evaluate(INBOX) == {"bait": 3}, "연습·시험 달리기 → 미끼 없음")
        # 탭이 오래 뒤에 있던 판도 한 줄 1시간까지 (클라이언트)
        await pg.evaluate("()=>{ window._rows.length=0; Online.submit({nick:'X', score:1, diff:'easy', rule:'normal', secs:50760}); }"); await pg.wait_for_timeout(100)
        ok(await pg.evaluate("()=>window._rows[0].secs") == 3600, "시트 줄 플레이(초) 3600 까지")

        # ── 시트 줄에 🏝 마을 칸 ──
        await pg.evaluate("(s)=>{ localStorage.setItem('hyeng_town_sum', JSON.stringify(s)); window._rows.length=0; Online.submit({nick:'X', score:1, diff:'easy', rule:'normal', secs:10}); Online.submit({type:'buy', nick:'X', item:'a', price:1, gems:1}); }", SUM)
        await pg.wait_for_timeout(100)
        R = await pg.evaluate("()=>window._rows")
        row = R[0]; buy = [x for x in R if x.get("type") == "buy"]
        ok(all(row.get(k) == SUM[k] for k in ["coin", "bait", "bank", "gbank", "tup"]), "판 줄에 coin·bait·bank·gbank·tup " + json.dumps({k: row.get(k) for k in ['coin','bait','bank','gbank','tup']}, ensure_ascii=False))
        ok(buy and "coin" not in buy[0], "구매 줄에는 안 붙임")
        # 공용 패드에서 이름 고른 아이 = …@아이 칸
        gk = await pg.evaluate("""()=>{ const s=localStorage.getItem('hyeng_nick'); localStorage.setItem('hyeng_nick','한양패드1'); Kid.st().setItem('hyeng_kid', JSON.stringify({id:'kidA', n:'라언', at:Date.now()}));
          const k=[Town.k('hyeng_town_inbox'), Town.k('hyeng_town_sum')]; Town.bait(5); const v=localStorage.getItem('hyeng_town_inbox@kidA'); Kid.st().removeItem('hyeng_kid'); if(s==null) localStorage.removeItem('hyeng_nick'); else localStorage.setItem('hyeng_nick', s); return k.concat([v]); }""")
        ok(gk[0] == "hyeng_town_inbox@kidA" and gk[1] == "hyeng_town_sum@kidA" and gk[2] == '{"bait":5}', f"공용 패드 이름 고른 아이 = 따로 칸 {gk}")

        # ── 관리 화면 ──
        await pg.evaluate("""()=>{ const W=Wallet.raw(); W.log=(W.log||[]).concat([[Date.now()-5000, -30, '🏝 마을 가구 소파', 100], [Date.now()-3000, 12, '🏝 마을 낚시 대회', 112], [Date.now()-1000, 5, '공부 mid-1', 117]]); localStorage.setItem('hyeng_wallet_v1', JSON.stringify(W));
          localStorage.setItem('hyeng_town_inbox', JSON.stringify({bait:4})); sessionStorage.setItem('hyeng_admin_ok', String(Date.now())); sessionStorage.setItem('hyeng_admin_tk', 'testkey'); }""")
        await pg.reload(); await pg.wait_for_timeout(1500)
        await pg.evaluate("""()=>{ document.querySelectorAll('.sheet.on').forEach(s=>s.classList.remove('on')); Online.on=()=>true;
          window._rep={nicks:[], weekly:[['아이','들어온 날','오늘의 30','끝까지','공부(분)','정답률(%)','달리기 판','달리기 최고','짧은 판','새 도감','자주 틀린 단어','지난주보다 (공부)','학부모 문자'],['유이홍','4','8','7','60','88','5','1200','1','3','apple','+10분','잘했어요'],['서연','2','3','2','20','75','1','500','0','1','pear','-','잘했어요']],
            town:[['아이','태그','마지막','보석','모은 보석','코인','미끼','은행 코인','은행 보석','강화','버전'],['유이홍','#0009','2026-11-02 15:01','140','920','400','2','1,300','60','낚싯대3 가방1 밭0','v563'],['라언','','2026-11-02 14:00','7','7','9','1','','','','v563']]};
          Online.submit=o=>Promise.resolve(o.type==='report' ? {ok:true, rep:window._rep} : o.type==='tags' ? {ok:true, list:[]} : {ok:true});
          Notice.fetch=()=>Promise.resolve({v:8, notices:[]}); window.confirm=()=>true; }""")
        await pg.evaluate("()=>{ Admin.open(); Admin._tab('dev'); }"); await pg.wait_for_timeout(900)
        t = await pg.evaluate("()=>[...document.querySelectorAll('.adCard')].map(c=>c.innerText).find(x=>/My Town/.test(x))||''")
        print("dev card:", t.replace("\n", " | ")[:300])
        ok("🪙 340" in t and "🪱 7" in t and "1,200" in t and "💎55" in t and "낚싯대2" in t, "📊 이 기기 🏝 My Town: 코인·미끼·은행·강화")
        ok("받을 것 +4" in t, "편지함 미끼(받을 것)도 보임")
        ok("마을 낚시 대회" in t and "마을 가구 소파" in t and "공부 mid-1" not in t, "🏝 보석 기록 줄만")
        await pg.evaluate("()=>{ const c=[...document.querySelectorAll('.adCard')].find(x=>/My Town/.test(x.innerText)); if(c) c.scrollIntoView(); }")
        await pg.screenshot(path=OUT + "econ563_admin_dev.png")
        await pg.evaluate("()=>Admin._tab('class')"); await pg.wait_for_timeout(1500)
        info = await pg.evaluate("""()=>{ const T=[...document.querySelectorAll('table.kidSum')]; const wk=T.find(t=>/들어온 날/.test(t.innerText)), tw=T.find(t=>/모은 💎/.test(t.innerText));
          const row=n=>wk ? [...wk.querySelectorAll('tr')].map(r=>[...r.children].map(c=>c.innerText.trim())).find(r=>r[0]===n) : null;
          return {head: wk ? [...wk.querySelectorAll('th')].map(x=>x.innerText) : null, yi: row('유이홍'), sy: row('서연'), town: tw ? tw.innerText : null}; }""")
        print("class:", json.dumps(info, ensure_ascii=False)[:500])
        hd = info["head"] or []
        ok("🪙" in hd and "🪱" in hd and "🏦" in hd, "👤 아이별 이번 주 표에 🪙 · 🪱 · 🏦 칸")
        if info["yi"] and "🪙" in hd:
            i = hd.index("🪙"); ok(info["yi"][i:i+3] == ["400", "2", "1,300 · 💎60"], f"유이홍 🪙·🪱·🏦 = {info['yi'][i:i+3]}")
            ok(info["sy"][i:i+3] == ["—", "—", "—"], "기록 없는 아이는 —")
        ok(info["town"] and "유이홍" in info["town"] and "라언" in info["town"] and "140" in info["town"], "🏝 보석 · My Town (반 전체) 표")
        await pg.evaluate("()=>{ const T=[...document.querySelectorAll('table.kidSum')].find(t=>/모은 💎/.test(t.innerText)); if(T) T.scrollIntoView(); }")
        await pg.screenshot(path=OUT + "econ563_admin_class.png")
        # 옛 서버(v7) — 마을 표 대신 바꾸는 법
        await pg.evaluate("()=>{ localStorage.removeItem('hyeng_admin_rep'); }"); await pg.reload(); await pg.wait_for_timeout(1500)
        await pg.evaluate("""()=>{ document.querySelectorAll('.sheet.on').forEach(s=>s.classList.remove('on')); Online.on=()=>true;
          const rep={nicks:[], weekly:[['아이','들어온 날','오늘의 30','끝까지','공부(분)','정답률(%)','달리기 판'],['서연','2','3','2','20','75','1']]};
          Online.submit=o=>Promise.resolve(o.type==='report' ? {ok:true, rep} : o.type==='tags' ? {ok:true, list:[]} : {ok:true}); Notice.fetch=()=>Promise.resolve({v:7, notices:[]}); }""")
        await pg.evaluate("()=>{ Admin.open(); Admin._tab('class'); }"); await pg.wait_for_timeout(1500)
        t2 = await pg.evaluate("()=>[...document.querySelectorAll('.adCard')].map(c=>c.innerText).find(x=>/반 전체/.test(x))||''")
        ok("v8" in t2 and "새 Code.gs 복사" in t2, "옛 서버(v7) → 「v8 로 바꾸면」 안내 + 복사 단추 · " + t2.replace("\n", " ")[:100])
        sy = await pg.evaluate("()=>{ const t=[...document.querySelectorAll('table.kidSum')].find(t=>/들어온 날/.test(t.innerText)); return t ? [...t.querySelectorAll('tr')].map(r=>[...r.children].map(c=>c.innerText.trim())).find(r=>r[0]==='서연') : null; }")
        ok(sy and sy[5:8] == ["—", "—", "—"], f"옛 서버: 표의 🪙·🪱·🏦 = — {sy}")
        e = real_errs(errs); print("errs", e)
        if e: bad.append("errors")
        await br.close()
    if bad: print("BAD", bad)
asyncio.run(main())
