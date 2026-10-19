"""(v348) 수업 도구 다듬기 — 사용자: 교실 배틀·수업 레이드·숙제 열기·시험 열기 개선이 거의 없어
  ① 📌 숙제를 반마다 따로 (사자반·돌고래반 다른 숙제) · 예전 모양(숙제 하나) 읽기 · 선생님 표에 안 한 아이도 · 하나만 끝내기 · 안 한 아이 복사
  ② Stage 범위를 눌러서 고르기 (처음 → 끝 · 거꾸로 · 같은 칸 두 번 = 하나) — 배틀 · 시험 · 숙제
  ③ 배틀·레이드 반 고르기 → 기다리는 화면에 「아직 안 들어온 아이」 · 방 번호 크게 · 🔁 같은 설정으로 한 판 더 (아이 점수 0 · 다시 보석)
  ④ 시험(반) 선생님 표에 아직 안 들어온 아이"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

ROSTER = "{t:{a:{n:'사자반',e:'🦁'},b:{n:'돌고래반',e:'🐬'}},k:{k1:{n:'민준',t:'a'},k2:{n:'서연',t:'a'},k4:{n:'지우',t:'a'},k3:{n:'하준',t:'b'}}}"

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch()
        ctx = await br.new_context(viewport={"width": 820, "height": 1180}, is_mobile=True, has_touch=True)
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        T = await ctx.new_page(); T.on("pageerror", lambda e: errs.append("T " + str(e))); await boot(T)
        await T.evaluate("()=>{ sessionStorage.setItem('hyeng_admin_ok', String(Date.now())); sessionStorage.setItem('hyeng_admin_tk','testkey'); }")
        await T.reload(); await T.wait_for_timeout(1500)
        await T.evaluate("""()=>{ document.querySelectorAll('.sheet.on').forEach(s=>s.classList.remove('on')); Online.on=()=>true; Online.submit=o=>Promise.resolve(o.type==='report'?{ok:true,rep:{nicks:[]}}:{ok:true});
            Notice.fetch=()=>Promise.resolve({v:3,notices:[]}); window.confirm=()=>true; window._clip=''; try{ navigator.clipboard.writeText=t=>{ window._clip=t; return Promise.resolve(); }; }catch(e){} }""")
        await T.evaluate("()=>FB.set('/hy/roster'," + ROSTER + ")"); await T.wait_for_timeout(300)
        E = T.evaluate

        # ── ① 예전 모양 숙제(하나) 읽기 ──
        await E("()=>FB.set('/hy/hw/cur', {id:'hold', on:1, set:'elem', from:0, to:1, goal:1, due:Date.now()+864e5, title:'옛 숙제', at:1})")
        await E("()=>HyHW.check(true)")
        ok(await E("()=>HyHW.L.length===1 && HyHW.L[0].id==='hold'"), "예전 모양 숙제도 읽음")

        await E("()=>{ Admin.open(); Admin._tab('exam'); }"); await T.wait_for_timeout(1200)
        ok(await E("()=>!!document.getElementById('adHwTeam')"), "숙제 반 고르기 칸")
        # ② 숙제 Stage 눌러 고르기 — 사자반 Grade 3-4 Stage 3~6
        await T.select_option("#adHwTeam", "a")
        await E("()=>{ const s=document.getElementById('adHwSet'); s.value='elem'; s.dispatchEvent(new Event('change')); }"); await T.wait_for_timeout(300)
        rows = await E("()=>[...document.querySelectorAll('#adHwFrom, #adHwTo')].map(e=>getComputedStyle(e.closest('.adPinRow')).display)")
        ok(rows == ["none", "none"], f"부터·까지 드롭다운 숨김 {rows}")
        await T.click("#adHwFromPick .stgC[data-i='6']"); await T.wait_for_timeout(150)
        hint = await E("()=>document.querySelector('#adHwFromPick .stgHd').innerText")
        ok("끝 Stage" in hint and await E("()=>[adHwFrom.value, adHwTo.value]") == ["6", "6"], f"첫 번째 누름 = 처음 (그 하나) {hint!r}")
        await T.click("#adHwFromPick .stgC[data-i='3']"); await T.wait_for_timeout(150)   # 거꾸로
        ok(await E("()=>[adHwFrom.value, adHwTo.value]") == ["3", "6"], "두 번째 누름 = 끝 (거꾸로 눌러도)")
        ins = await E("()=>[...document.querySelectorAll('#adHwFromPick .stgC.in')].map(b=>+b.dataset.i)")
        ok(ins == [3, 4, 5, 6], f"범위 칸 칠함 {ins}")
        await T.click("#adHwFromPick .stgC[data-i='2']"); await T.click("#adHwFromPick .stgC[data-i='2']"); await T.wait_for_timeout(150)
        ok(await E("()=>[adHwFrom.value, adHwTo.value]") == ["2", "2"], "같은 칸 두 번 = 그 하나")
        await T.click("#adHwFromPick .stgC[data-i='0']"); await T.click("#adHwFromPick .stgC[data-i='3']"); await T.wait_for_timeout(150)
        await T.click('[data-ad="hwOpen"]'); await T.wait_for_timeout(600)
        cur = await E("()=>FB.get('/hy/hw/cur')")
        ok(isinstance(cur, dict) and "set" not in cur and len(cur) == 2 and all(isinstance(v, dict) and v.get("set") for v in cur.values()), f"새 모양(반마다)으로 다시 씀 (옛 전체 숙제 + 사자반) {list((cur or {}).keys())}")
        # 돌고래반 숙제 — 다른 책
        await T.select_option("#adHwTeam", "b")
        await E("()=>{ const s=document.getElementById('adHwSet'); s.value='g56'; s.dispatchEvent(new Event('change')); }"); await T.wait_for_timeout(200)
        await T.click("#adHwFromPick .stgC[data-i='0']"); await T.click("#adHwFromPick .stgC[data-i='1']"); await T.wait_for_timeout(100)
        await T.click('[data-ad="hwOpen"]'); await T.wait_for_timeout(600)
        L = await E("()=>HyHW.L.map(c=>[c.team||'all', c.set, c.from, c.to])")
        ok(sorted(L) == sorted([["all", "elem", 0, 1], ["a", "elem", 0, 3], ["b", "g56", 0, 1]]), f"숙제 3개 (전체 · 사자반 · 돌고래반) {L}")
        # 아이 쪽 — 반마다 자기 숙제
        mine = await E("""()=>{ const r={}; [['k1','민준','a'],['k3','하준','b']].forEach(([id,n,t])=>{ Kid.set({id,n,t}); r[n]=HyHW.mine() && [HyHW.mine().team, HyHW.mine().set]; }); Kid.clear(); r['none']=HyHW.mine() && (HyHW.mine().team||'all'); return r; }""")
        ok(mine == {"민준": ["a", "elem"], "하준": ["b", "g56"], "none": "all"}, f"아이마다 자기 반 숙제 · 이름 없으면 전체 숙제 {mine}")
        # 서연(사자반) 2/4 · 민준 4/4 → 선생님 표: 지우 아직
        await E("()=>{ const id=HyHW.L.find(c=>c.team==='a').id; FB.set('/hy/hw/res/'+id+'/k1',{n:'민준',t:'a',done:4,tot:4,at:1}); FB.set('/hy/hw/res/'+id+'/k2',{n:'서연',t:'a',done:2,tot:4,at:1}); }")
        await E("()=>{ Admin._tab('home'); Admin._tab('exam'); }"); await T.wait_for_timeout(1200)
        tb = await E("()=>{ const id=HyHW.L.find(c=>c.team==='a').id; return document.getElementById('adHwRes_'+id).innerText; }")
        ok("지우" in tb and "아직 1" in tb and "하는 중 1" in tb and "다 함 1" in tb and "하준" not in tb, f"사자반 숙제 표 — 안 한 아이(지우)도 · 다른 반 아이 없음 {tb[:80]!r}")
        first = await E("()=>{ const id=HyHW.L.find(c=>c.team==='a').id; const k=document.querySelector('#adHwRes_'+id+' .hwK'); return k ? [k.className, k.innerText] : null; }")
        ok(first and "no" in first[0] and "지우" in first[1], f"안 한 아이가 맨 앞 · 빨강 {first}")
        await E("()=>{ const id=HyHW.L.find(c=>c.team==='a').id; document.querySelector('[data-ad=\"hwCopy\"][data-id=\"'+id+'\"]').click(); }"); await T.wait_for_timeout(300)
        clip = await E("()=>window._clip")
        ok("지우" in clip and "서연 (2/4)" in clip and "민준" not in clip, f"안 한 아이 이름 복사 {clip!r}")
        # 하나만 끝내기
        await E("()=>{ const id=HyHW.L.find(c=>c.team==='b').id; document.querySelector('[data-ad=\"hwEnd\"][data-id=\"'+id+'\"]').click(); }"); await T.wait_for_timeout(500)
        cur = await E("()=>FB.get('/hy/hw/cur')")
        ok(isinstance(cur, dict) and sorted((v.get("team") or "all") for v in cur.values()) == ["a", "all"], f"돌고래반 숙제만 끝 {cur and [v.get('team') for v in cur.values()]}")
        await T.screenshot(path=OUT + "cls_hw.png")

        # ── ② 배틀 · 시험도 Stage 눌러 고르기 ──
        await E("()=>Admin._tab('play')"); await T.wait_for_timeout(800)
        ok(await E("()=>!!document.querySelector('#adBtFromPick .stgC') && !!document.getElementById('adBtCls') && !!document.getElementById('adRdCls')"), "배틀: Stage 칸 · 반 고르기 · 레이드 반 고르기")
        await E("()=>Admin._tab('exam')"); await T.wait_for_timeout(800)
        ok(await E("()=>!!document.querySelector('#adExFromPick .stgC')"), "시험: Stage 칸")

        # ── ④ 시험(사자반) — 아직 안 들어온 아이 ──
        await T.select_option("#adExTeam", "a")
        await E("()=>{ const s=document.getElementById('adExSet'); s.value='elem'; s.dispatchEvent(new Event('change')); }"); await T.wait_for_timeout(200)
        await T.click("#adExFromPick .stgC[data-i='0']"); await T.click("#adExFromPick .stgC[data-i='2']")
        await T.click('[data-ad="exOpen"]'); await T.wait_for_timeout(900)
        await E("()=>{ const c=HyExam.L[0]; FB.set('/hy/exam/res/'+c.id+'/k1', {n:'민준', p:0, tot:20}); }"); await T.wait_for_timeout(800)
        ex = await E("()=>{ const c=HyExam.L[0]; const e=document.getElementById('adExRes_'+c.id); return e ? e.innerText : ''; }")
        ok("아직 2명" in ex and "서연" in ex and "지우" in ex and "하준" not in ex, f"시험 표: 사자반 중 아직 안 들어온 아이 {ex[:70]!r}")
        await E("()=>{ HyExam.tv(HyExam.L[0].id); }"); await T.wait_for_timeout(400)
        tv = await E("()=>document.getElementById('exTv').innerText")
        ok("아직 2명" in tv, "시험 크게 보기에도 아직 안 들어온 아이")
        await E("()=>{ const d=document.getElementById('exTv'); if(d) d.remove(); HyExam._tv=null; }")

        # ── ③ 배틀 (사자반) ──
        await E("()=>Admin._tab('play')"); await T.wait_for_timeout(700)
        await T.select_option("#adBtCls", "a")
        await E("()=>{ const s=document.getElementById('adBtSet'); s.value='g56'; s.dispatchEvent(new Event('change')); document.getElementById('adBtDur').value='180'; }"); await T.wait_for_timeout(200)
        await T.click("#adBtFromPick .stgC[data-i='0']"); await T.click("#adBtFromPick .stgC[data-i='2']")
        await T.click('[data-ad="btGo"]'); await T.wait_for_timeout(1500)
        room = await E("()=>Battle.room"); cfg = await E("()=>Battle.cfg()")
        ok(cfg.get("cls") == "a" and cfg.get("from") == 0 and cfg.get("to") == 2, f"배틀 방: 반·범위 {cfg.get('cls')} {cfg.get('from')}~{cfg.get('to')}")
        w = await E("()=>document.getElementById('rdIn').innerText")
        ok(room in w and "아직 3명" in w and "하준" not in w, f"기다리는 화면: 방 번호 크게 · 사자반 아직 3명 {w[:90]!r}")
        ok(await E("()=>{ const b=document.querySelector('[data-bth=\"start\"]'); return b && b.classList.contains('big') && b.getBoundingClientRect().height>=60; }"), "시작 버튼 크게")
        kids = []
        for nm, kid in (("민준", "k1"), ("서연", "k2")):
            k = await ctx.new_page(); k.on("pageerror", lambda e, n=nm: errs.append(n + " " + str(e))); await k.set_viewport_size({"width": 390, "height": 844}); await boot(k)
            await k.evaluate(f"()=>{{ Kid.set({{id:'{kid}', n:'{nm}', t:'a'}}); Battle.join('{room}', {{id:'{kid}', n:'{nm}', t:'a'}}); }}")
            await k.wait_for_timeout(700); await k.evaluate("()=>{ Battle.FAST=0; }"); kids.append(k)
        await T.wait_for_timeout(600)
        w = await E("()=>document.getElementById('rdIn').innerText")
        ok("아직 1명" in w and "지우" in w, f"들어오면 줄어듦 (지우만) {w[:120]!r}")
        await T.screenshot(path=OUT + "cls_bt_wait.png")

        async def play_round():
            await E("()=>Battle.hostAct('start')"); await T.wait_for_timeout(4200)
            for step in range(40):
                for k in kids:
                    await k.evaluate("()=>{ const q=Battle.q; if(!q||q.done) return; const i=q.ans!=null?q.ans:q.opts.findIndex(o=>o.en===q.w.en); Battle.answer(i); }")
                await T.wait_for_timeout(120)
            await E("()=>Battle.hostAct('end')"); await T.wait_for_timeout(3500)
            return [await k.evaluate("()=>[Battle.ended, Battle.sc, Battle._gems]") for k in kids]
        r1 = await play_round()
        ok(all(x[0] and x[1] > 0 and x[2] > 0 for x in r1), f"1판 끝 · 보석 {r1}")
        ctl = await E("()=>document.querySelector('.rdCtl').innerText")
        ok("한 판 더" in ctl, f"끝 화면에 🔁 한 판 더 {ctl[:60]!r}")
        await T.screenshot(path=OUT + "cls_bt_end.png")
        await E("()=>document.querySelector('[data-bth=\"again\"]').click()"); await T.wait_for_timeout(1500)
        st = await E("()=>Battle.st()"); P = await E("()=>Object.values(Battle.T().p||{}).map(p=>p.sc|0)")
        ok(st.get("s") == "wait" and st.get("rnd") == 1 and P == [0, 0], f"같은 방 다시 기다림 · 점수 0 {st} {P}")
        kk = [await k.evaluate("()=>[Battle.room, Battle.ended, Battle.sc]") for k in kids]
        ok(all(x[0] == room and not x[1] and x[2] == 0 for x in kk), f"아이들은 그대로 같은 방 · 점수 0 {kk}")
        r2 = await play_round()
        ok(all(x[0] and x[1] > 0 and x[2] > 0 for x in r2), f"2판도 끝 · 보석 다시 {r2}")
        for k in kids: await k.close()
        await E("()=>{ Battle.leave && Battle.leave(); }"); await T.wait_for_timeout(300)

        # ── ③ 레이드 (돌고래반) 기다리는 화면 ──
        await E("()=>{ Admin.open(); Admin._tab('play'); }"); await T.wait_for_timeout(700)
        await T.select_option("#adRdCls", "b")
        await T.click('[data-ad="raidGo"]'); await T.wait_for_timeout(1500)
        w = await E("()=>document.getElementById('rdIn').innerText")
        ok(await E("()=>(RaidNet.get().cfg||{}).cls") == "b" and "아직 1명" in w and "하준" in w and "민준" not in w, f"레이드 기다리는 화면: 돌고래반 아직 1명 {w[-120:]!r}")
        ok(await E("()=>{ const b=document.querySelector('[data-rdh=\"start\"]'); return b && b.classList.contains('big'); }"), "레이드 시작 버튼 크게")
        await T.screenshot(path=OUT + "cls_rd_wait.png")
        e = real_errs(errs); ok(not e, "오류 없음 " + str(e[:3]))
        await br.close()
    print("결과:", "통과" if not bad else "실패 " + str(bad))
asyncio.run(main())
