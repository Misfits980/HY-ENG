"""(v699) 게임 전체 QA (크롬 + 자동) 에서 찾은 것 — claude/hy-eng-qa-v699.md
   ① 오늘의 30 지도 칩 줄: 폰(390)에서 넘치면 맨 뒤 「🧭 이야기 NEW」·「🤝 짝」이 화면 밖 → 할 것(hot)·짝·빨간 표 칩이 앞 · 넘치면 오른쪽 끝 흐림(.more)
   ② ☁️ 예전 기록: 서버 기록도 비어 있으면(💎0 · Stage 0 · 📖0) 「가져올까요?」 안 물음 · 뭔가 있으면 그대로 물음
   ③ 달리기 속 복습(DueMix): 🏃 수업 달리기 레이스(G.race)·「이 Stage 단어로 달리기」(G.words)엔 안 섞음 · 그냥 혼자 달리기엔 섞음
   ④ 주간 보스 옆모습 무대: 0번 친구(내 바로 뒤)의 이름표 = 머리 위 (발밑이면 내 캐릭터에 가렸음) · 1번 = 발밑
   ⑤ 윈도우 10·옛 아이패드가 둘로 갈라 그리는 이모지 → 되는 것으로: 🧭 이야기 Captain Jay 👨‍✈️ · Mia 👩‍🌾 · Tom 👨‍🌾 · Rosa·Sunny 👩‍🍳
   ⑥ 🕰 하루 리듬: 자동 시험(webdriver)은 HY_HOUR 가 없으면 늘 낮 12시 (밤에 돌려도 이웃·가게 시험이 안 깨짐)"""
import asyncio, sys, os, json, time
os.environ["HY_REAL3D"]="1"   # 마을(진짜 3D) 칸이 있어서
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from fakefb import fake
from playwright.async_api import async_playwright


async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m, flush=True)
        if not c: bad.append(m)
    ME = {}
    async def sheet(r):
        u = r.request.url
        if r.request.method == "POST":
            return await r.fulfill(status=200, content_type="application/json", body='{"ok":true}')
        if "board=1" in u:
            return await r.fulfill(status=200, content_type="application/json", body=json.dumps({"ok": True, "v": 25, "boards": {"study": [], "words": [], "run": []}, "me": ME}))
        return await r.fulfill(status=200, content_type="application/json", body='{"ok":true,"list":[]}')
    async with async_playwright() as p:
        br = await p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        ctx = await br.new_context(viewport={"width": 390, "height": 844}, has_touch=True)
        await ctx.add_init_script("window.HY_STY=1; localStorage.setItem('hyeng_nick','민준'); localStorage.setItem('hyeng_tag','0006');")
        pg = await ctx.new_page(); pg.set_default_timeout(120000); pg.on("pageerror", lambda e: errs.append(str(e)[:200]))
        await pg.route("**/*", route); await pg.route("https://script.google.com/**", sheet)
        await pg.goto(ORIGIN + "index.html"); await pg.wait_for_timeout(1300)
        await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); try{ StudyUI.FAST=0; }catch(e){} ['helloMt','rkAnn','moveAsk'].forEach(i=>{ const d=document.getElementById(i); if(d) d.remove(); }); }")
        E = pg.evaluate

        # ── ① 칩 줄
        now = int(time.time() * 1000)
        ME.clear(); ME.update({"pq": {"ws": now - 2 * 864e5, "goal": 15, "sum": 9, "mem": [{"n": "민준", "c": 4, "me": 1}, {"n": "서연", "c": 5}], "ch": []}})
        await E("""()=>{ const set=Study.BOOKS.g34.sets[0]; const S=Study.load(); S.book='g34'; S.lv=S.lv||{}; S.sty={}; Study.lessons(set).filter(x=>!x.fin).slice(0,3).forEach(x=>{ S.lv[Study.key(set,x.n)]=1; }); Study.save();
            StudyUI.set=set; StudyUI.book='g34'; StudyUI.open(); LiveRank._f=0; LiveRank._busy=0; LiveRank._fresh=0; LiveRank.fetch(); }""")
        for _ in range(30):
            n = await E("()=>document.querySelectorAll('#sbChips .sbChip').length")
            has = await E("()=>[...document.querySelectorAll('#sbChips .sbChip')].some(c=>/🤝/.test(c.textContent))")
            if n >= 4 and has: break
            await pg.wait_for_timeout(300)
        r = await E("""()=>{ const C=document.getElementById('sbChips'); const L=[...C.querySelectorAll('.sbChip')]; return {k:L.map(c=>c.dataset.sbk), sw:C.scrollWidth, cw:C.clientWidth, more:C.classList.contains('more'),
            vis:L.slice(0,2).map(c=>{ const b=c.getBoundingClientRect(), cb=C.getBoundingClientRect(); return b.right<=cb.right+1; })}; }""")
        ok(r["k"][:2] == ["sty", "pq"] and all(r["vis"]), f"① 🧭 이야기·🤝 짝 칩이 맨 앞 · 화면 안 {r['k']} {r['vis']}")
        ok((r["sw"] > r["cw"] + 4) == r["more"], f"① 넘치면 오른쪽 끝 흐림 (.more) {r['sw']}>{r['cw']} → {r['more']}")
        await pg.screenshot(path=OUT + "fix699_chips.png")
        await E("()=>{ const C=document.getElementById('sbChips'); C.scrollLeft=C.scrollWidth; C.dispatchEvent(new Event('scroll')); }"); await pg.wait_for_timeout(200)
        ok(not await E("()=>document.getElementById('sbChips').classList.contains('more')"), "① 끝까지 밀면 흐림 없음")

        # ── ② ☁️ 빈 서버 기록 = 안 물음
        r = await E("""async ()=>{ const me={id:'k1', n:'민준'}; const o={who:Cloud.who, empty:Cloud.empty, get:Cloud.get};
            Cloud.who=()=>me; Cloud.empty=()=>true; Cloud.get=async()=>({d:'{"data":{}}', dev:'other', at:12345, n:'민준', sm:{g:0,e:0,st:0,dx:0}});
            try{ localStorage.removeItem(Cloud.SEEN); }catch(e){} const k0=Kid.shared; Kid.shared=()=>false;
            await Cloud.check(); const a=!!document.getElementById('moveAsk');
            Cloud.get=async()=>({d:'{"data":{}}', dev:'other', at:12346, n:'민준', sm:{g:12,e:30,st:2,dx:5}}); await Cloud.check(); const b=!!document.getElementById('moveAsk');
            const m=document.getElementById('moveAsk'); if(m) m.remove(); Object.assign(Cloud, o); Kid.shared=k0; return [a, b]; }""")
        ok(r == [False, True], f"② 서버 기록이 비면 안 물음 · 있으면 물음 {r}")

        # ── ③ DueMix
        r = await E("""()=>{ const o={race:G.race, words:G.words, set:G.set, rule:G.rule, lesson:G.lesson, tag:G.tag, versus:G.versus};
            Object.assign(G,{set:'elem', rule:'normal', lesson:0, tag:null, versus:false, race:null, words:null}); const a=DueMix.ok();
            G.race={room:'1234', rnd:1, base:0}; const b=DueMix.ok(); G.race=null; G.words=['cat','dog']; const c=DueMix.ok(); Object.assign(G,o); return [a,b,c]; }""")
        ok(r == [True, False, False], f"③ 혼자 달리기만 섞음 · 수업 레이스·Stage 달리기는 안 섞음 {r}")

        # ── ④ 주간 보스 옆모습 이름표
        r = await E("""()=>{ try{ WeekBoss.open(); }catch(e){}
            let box=document.getElementById('wbStage'); if(!box || !box.clientWidth){ box=document.createElement('div'); box.id='qaStage'; box.style.cssText='position:fixed;left:10px;top:120px;width:345px;height:250px;z-index:99999'; document.body.appendChild(box); }
            RaidStage.ensure('wk', {box, boss:Raid.rb(), me:'민준'}); RaidStage.allies({a:{n:'스트로베리',c:'hero'}, b:{n:'이무이무시완',c:'hero'}, c:{n:'seowon',c:'hero'}}, 'me');
            const A=Object.values(RaidStage.al).sort((x,y)=>x.slot-y.slot); return {side:!!RaidStage.side, up:A.map(a=>[a.slot, a.el.classList.contains('rsUp')])}; }""")
        ok(isinstance(r, dict) and (not r["side"] or (r["up"][0] == [0, True] and r["up"][1] == [1, False])), f"④ 옆모습 무대 0번 = 머리 위 · 1번 = 발밑 {r}")
        await pg.screenshot(path=OUT + "fix699_wb.png")

        # ── ⑤ 이모지
        r = await E("()=>[StoryQ.TH.g56.npc, StoryQ.TH.mid.npc]")
        ok(r == ["👨‍✈️", "👨‍✈️"], f"⑤ 이야기 Captain Jay = 👨‍✈️ {r}")

        # ── ⑤⑥ 마을
        await pg.route("**/*", fake)
        await pg.goto(ORIGIN + "proto/house.html?isle=1"); await pg.wait_for_timeout(500)
        await E("()=>{ localStorage.setItem('hyeng_proto_code', JSON.stringify('QF699')); localStorage.setItem('hyeng_dev','dQF699'); localStorage.setItem('hyeng_me', JSON.stringify({id:'kQF699', t:'A568'})); }")
        await pg.reload(); await pg.wait_for_timeout(2500)
        await E("()=>ISLE.enter()")
        for _ in range(200):
            if await E("()=>HOUSE.place()==='isle' && !HOUSE.trip().busy"): break
            await pg.wait_for_timeout(250)
        r = await E("()=>[DAYR.hour(), DAYR.night(), (document.querySelector('#coach .cMas')||{}).textContent, (VIL.nbList().find(x=>x.id==='tom')||{}).ic]")
        ok(r[0] == 12 and r[1] is False, f"⑥ 자동 시험 = 늘 낮 12시 {r[:2]}")
        ok(r[2] == "👩‍🌾" and r[3] == "👨‍🌾", f"⑤ Mia 👩‍🌾 · Tom 👨‍🌾 {r[2:]}")
        r = await E("()=>{ window.HY_HOUR=23; const a=[DAYR.hour(), DAYR.night()]; window.HY_HOUR=null; return a; }")
        ok(r == [23, True], f"⑥ HY_HOUR 를 주면 그 시각 {r}")
        ok(not real_errs(errs), f"JS 오류 없음 {real_errs(errs)[:3]}")
        await br.close()
    print("DONE bad=%d" % len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
