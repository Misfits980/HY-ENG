"""(v713) 🎲 파티 보드 버그 묶음 — 사용자: 「버그 먼저 바로」 · 「땅따먹기는 버그 때문에 아직도 안 되던데?」
  ① 서버 규칙: /battle/<방>/ 아래 쓰는 칸이 server/firebase-rules*.json 이 허용하는 것(cfg·st·fx·p)뿐인지 — 코드 글자 검사 + 실제로 쓰는 길 기록
     (땅따먹기 /pt/ = 규칙에 없어서 서버가 모두 거절 → 패드마다 자기 칸만 · TV 점수 0 · 가짜 서버 테스트는 규칙이 없어 못 잡았음)
  ② 🎨 땅따먹기 TV + 패드 3대: 모든 패드·TV 판이 같은 칸 수 · 점수 = 칸 수 · 칸 길 = /fx/pt<게임>
  ③ TV 긴 카드(🏪 상점 · 🎒 가방 3개 · 🔄 누구에게 5명): 카드 위가 화면 밖으로 안 잘림 (1920×1080 · 1366×768 · 1280×720)
  ④ 📺 수업판 아이 패드: 판에 들어가면 뒤 첫 화면 3D 를 안 그림 (예전 3초에 수십 번)
  ⑤ 같은 칸 말 2~6명: 가로 간격 0.7 넘게 · 이름표 층 0.62
  ⑥ 초등 던전 판 🍄 = 「버섯 물약」(그림) · 유아 판 = 「버섯」 · ⑦ 별 칸 위에 서면 「⭐ 바로 여기」(예전 「까지 30칸」)"""
import asyncio, sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
REC = """()=>{ if(window.__fbw) return; window.__fbw=[]; ['set','update','push','inc','once'].forEach(k=>{ const f=FB[k]; FB[k]=function(p){ try{ window.__fbw.push(String(p)); }catch(e){} return f.apply(this, arguments); }; }); }"""

def allowed(rules, top):
    """규칙 파일에서 /<top>/$room/ 아래 쓸 수 있는 칸 이름 (정해진 칸 + $other 정규식)"""
    R = rules["rules"][top]["$room"]
    names = {k for k in R if not k.startswith("$") and not k.startswith(".")}
    rx = None
    o = R.get("$other", {}).get(".validate", "")
    m = re.search(r"matches\(/(.+?)/\)", o)
    if m: rx = re.compile(m.group(1))
    return names, rx

def ok_child(c, names, rx):
    return c in names or (rx is not None and rx.match(c) is not None)

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m, flush=True)
        if not c: bad.append(m)
    src = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    # ① 코드 글자 검사 — 두 규칙 파일 모두
    for rf in ["firebase-rules.json", "firebase-rules-auth.json"]:
        rules = json.load(open(os.path.join(ROOT, "server", rf), encoding="utf-8"))
        for top in ["battle", "raids"]:
            names, rx = allowed(rules, top)
            used = set(re.findall(r'"/' + top + r'/"\+[A-Za-z_.()]+\+"/([a-z]+)', src))
            if top == "raids": used |= set(re.findall(r'RaidNet\.(?:write|inc|push)\("/([a-z]+)', src))
            badc = sorted(c for c in used if not ok_child(c, names, rx))
            ok(used and not badc, f"① {rf} · /{top}/<방>/ 에 쓰는 칸 {sorted(used)} — 규칙에 없는 칸 {badc}")
    rules = json.load(open(os.path.join(ROOT, "server", "firebase-rules.json"), encoding="utf-8"))
    BN, BRX = allowed(rules, "battle")
    async with async_playwright() as p:
        br = await p.chromium.launch()
        # ② 땅따먹기 TV + 패드 3대
        ctx = await br.new_context(viewport={"width": 1920, "height": 1080}, service_workers="block")
        await ctx.add_init_script("window.HY_FB_LOCAL=true; window.HY_NOHOW=true;")
        T = await ctx.new_page(); T.on("pageerror", lambda e: errs.append("TV " + str(e))); await boot(T); await T.evaluate(REC)
        async def until(pg, js, n=80):
            for _ in range(n):
                if await pg.evaluate(js): return True
                await pg.wait_for_timeout(250)
            return False
        await T.evaluate("()=>FB.set('/hy/roster',{t:{a1:{n:'1반',e:'🍎'}}, k:{k1:{n:'민준',t:'a1'}, k2:{n:'서연',t:'a1'}, k3:{n:'도윤',t:'a1'}}}).then(()=>HyBoss.refresh(true))")
        await T.evaluate("()=>Board.setup()"); await T.wait_for_timeout(300)
        await T.evaluate("()=>{ document.querySelector('[data-mode=tv]').click(); document.getElementById('bdGo').click(); }")
        await until(T, "()=>/^\\d{4}$/.test((document.getElementById('lbRoom')||{}).textContent||'')"); room = await T.evaluate("()=>BoardTV.room")
        K = []
        for i, (k, n) in enumerate([("k1", "민준"), ("k2", "서연"), ("k3", "도윤")]):
            pg = await ctx.new_page(); await pg.set_viewport_size({"width": 820, "height": 1180})
            pg.on("pageerror", lambda e, i=i: errs.append(f"P{i} " + str(e))); await boot(pg); await pg.evaluate(REC)
            if i == 0:   # ④ 판에 들어가기 전/뒤 뒤 3D 그리기 횟수
                cnt = "()=>{ if(!window.__rc){ window.__rc=0; const r=renderer.render.bind(renderer); renderer.render=(...a)=>{ window.__rc++; return r(...a); }; if(typeof composer!=='undefined' && composer){ const c=composer.render.bind(composer); composer.render=(...a)=>{ window.__rc++; return c(...a); }; } } const v=window.__rc; window.__rc=0; return v; }"
                await pg.evaluate(cnt); await pg.wait_for_timeout(1500); before = await pg.evaluate(cnt)
            await pg.evaluate("()=>HyBoss.refresh(true)"); await pg.evaluate(f"()=>BoardPad.join('{room}', {{id:'{k}', n:'{n}', t:'a1'}})"); K.append(pg)
            if i == 0:
                await pg.wait_for_timeout(600); await pg.evaluate(cnt); await pg.wait_for_timeout(1500); after = await pg.evaluate(cnt)
                ok(before > 5 and after == 0, f"④ 아이 패드: 첫 화면 3D {before}번/1.5초 → 판에 들어가면 {after}번")
        await until(T, "()=>document.querySelectorAll('#lbKids .lbKid').length===3")
        await T.evaluate("()=>document.querySelector('[data-lb=solo]').click()"); await T.evaluate("()=>document.getElementById('lbGo').click()")
        await until(T, "()=>Board.o && Board.o.tv", 80); await T.wait_for_timeout(1200)
        await T.evaluate("()=>{ clearTimeout(Board._to); const o=Board.o; o.mgOnly='paint'; o.cur=o.P.length-1; Board.act(''); Board.endTurn(); }")
        ok(await until(T, "()=>!!BoardTV.mgS && BoardTV.mgS.kind==='paint'", 60), "② TV 🎨 땅따먹기 시작")
        ok(all([await until(pg, "()=>!!BoardPad.g", 90) for pg in K]), "② 패드 3대 모두 땅따먹기")
        for r in range(10):
            for pg in K:
                await pg.evaluate("()=>{ const g=BoardPad.g; if(!g) return; const A=g.sh.get(); const L=A.map((v,i)=>v!==g.me.i?i:-1).filter(i=>i>=0); const el=g.cells[L[Math.floor(Math.random()*L.length)]]; if(el) el.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true})); }")
            await T.wait_for_timeout(330)
        await T.wait_for_timeout(900)
        pads = [await pg.evaluate("()=>{ const g=BoardPad.g; if(!g) return null; const c={}; g.sh.get().forEach(v=>{ if(v>=0) c[v]=(c[v]|0)+1; }); return {me:g.me.i, sc:g.sc, c}; }") for pg in K]
        tv = await T.evaluate("()=>{ const m=BoardTV.mgO; return m ? {c:MiniG.ptCount(m.pt), sc:BoardTV.mgSc()} : null; }")
        same = tv and all(x and x["c"] == tv["c"] for x in pads)
        ok(same and len(tv["c"]) == 3 and all(x["sc"] == tv["c"].get(str(x["me"]), 0) for x in pads), f"② 모든 판이 같음 · 점수 = 칸 수 · 세 색 {tv} {pads}")
        await K[0].screenshot(path=OUT + "bd713_paint_pad.png"); await T.screenshot(path=OUT + "bd713_paint_tv.png")
        paths = set()
        for pg in [T] + K:
            paths |= set(await pg.evaluate("()=>window.__fbw||[]"))
        ch = sorted({re.match(r"/?battle/\d+/([^/]+)", x).group(1) for x in paths if re.match(r"/?battle/\d+/[^/]+", x)})
        badc = [c for c in ch if not ok_child(c, BN, BRX)]
        ok(ch and not badc and any("/fx/pt" in x for x in paths), f"① 실제로 쓴 칸 {ch} · 규칙에 없는 칸 {badc} · 땅따먹기 = /fx/pt…")
        await ctx.close()
        # ③ TV 긴 카드 · ⑤ 같은 칸 · ⑥ 이름 · ⑦ 0칸
        for (w, h) in [(1920, 1080), (1366, 768), (1280, 720)]:
            pg = await br.new_page(viewport={"width": w, "height": h}); pg.on("pageerror", lambda e: errs.append(f"{w} " + str(e))); await boot(pg)
            await pg.evaluate("()=>Board.begin({sk:'e', set:'elem', from:0, to:3, qt:['mean','pic'], sec:0, rounds:10, P:[0,1,2,3,4,5].map(i=>({n:['민준','서연','도윤','하은','시우','아린'][i],id:'',ch:i}))})")
            await pg.wait_for_timeout(1200)
            await pg.evaluate("()=>{ const hw=document.getElementById('bdHow'); if(hw) hw.remove(); document.getElementById('board').classList.add('tv'); document.getElementById('bdAct').dataset.who='민준'; }")
            M = "()=>{ const a=document.getElementById('bdAct'), c=a.firstElementChild, r=a.getBoundingClientRect(), cr=c.getBoundingClientRect(); return {cut:Math.round(r.top-cr.top), out:Math.round(cr.bottom-innerHeight), tall:a.classList.contains('bdTall'), scroll:a.scrollHeight>a.clientHeight+4, t:(c.innerText||'').replace(/\\s+/g,' ').slice(0,24)} }"
            for name, js in [("shop", "()=>{ clearTimeout(Board._to); Board.o.P[0].coin=40; Board.shop(); }"),
                             ("bag3", "()=>{ clearTimeout(Board._to); Board.o.P[0].it=['mush','gold','swap']; Board.bag(); }"),
                             ("swap5", "()=>{ clearTimeout(Board._to); Board.o.P[0].it=['swap']; Board.use('swap'); }"),
                             ("roll", "()=>{ clearTimeout(Board._to); Board.turnMenu(); }")]:
                await pg.evaluate(js); await pg.wait_for_timeout(700)
                r = await pg.evaluate(M)
                ok(r["cut"] <= 2 and r["out"] <= 2 and not r["scroll"], f"③ TV {w}×{h} {name}: 위 안 잘림·아래 안 넘침 {r}")
                if w == 1920 and name in ("shop", "bag3"): await pg.screenshot(path=OUT + f"bd713_tv_{name}.png")
            if w == 1920:
                r = await pg.evaluate("()=>{ const o=Board.o, out=[]; for(let n=2;n<=6;n++){ o.P.forEach((p,i)=>{ p.pos = i<n ? 5 : 12+i; p.vis=null; }); B3.place(true); const xs=o.P.slice(0,n).map((p,i)=>B3.slot(i)); let mn=99; for(let a=0;a<n;a++) for(let b=a+1;b<n;b++){ const d=Math.hypot(xs[a].x-xs[b].x, (xs[a].z-xs[b].z)); if(d<mn) mn=d; } const ny=B3.pc ? B3.pc.slice(0,n).map(c=>Math.round(c.nm.position.y*100)/100) : []; out.push([n, Math.round(mn*100)/100, ny]); } return out; }")
                ok(all(x[1] >= 0.7 for x in r) and all(len(set(x[2])) == x[0] and min(b - a for a, b in zip(sorted(x[2]), sorted(x[2])[1:])) >= 0.6 for x in r if x[2]), f"⑤ 같은 칸 2~6명: 가장 가까운 말 간격 · 이름표 높이 {r}")
                r = await pg.evaluate("()=>{ clearTimeout(Board._to); Board.o.P[0].coin=40; Board.shop(); const t=document.getElementById('bdAct').innerText; return [/버섯 물약/.test(t), Board.itN('mush')]; }")
                ok(r == [True, "버섯 물약"], f"⑥ 초등 던전: 🍄 = 버섯 물약 {r}")
                r = await pg.evaluate("()=>{ clearTimeout(Board._to); const o=Board.o; o.cur=0; o.P[0].pos=o.star; o.P[0].vis=null; Board.turnMenu(); return document.querySelector('#bdAct .bdHudS').innerText; }")
                ok("바로 여기" in r and "30" not in r, f"⑦ 별 칸 위 = 「바로 여기」 {r!r}")
            await pg.close()
        pg = await br.new_page(viewport={"width": 1180, "height": 820}); pg.on("pageerror", lambda e: errs.append("k " + str(e))); await boot(pg)
        await pg.evaluate("()=>Board.begin({sk:'k', set:'kinder', from:0, to:2, qt:['pic'], sec:0, rounds:10, P:[{n:'민준',id:'',ch:0},{n:'서연',id:'',ch:3}]})"); await pg.wait_for_timeout(800)
        ok(await pg.evaluate("()=>Board.itN('mush')") == "버섯", "⑥ 유아 판 = 버섯 (그림이 버섯)")
        await br.close()
    real = [e for e in real_errs(errs) if "reading 'set'" not in e]
    ok(not real, f"오류 없음 {real[:3]}")
    print("DONE bad=%d" % len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
