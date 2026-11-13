"""(v671) 사용자: 「탑 쌓기 — 내려오는 것도 아니고 그냥 누르면 쌓이는 것처럼 보여」 · 「땅따먹기도 칸을 누르라고 했더니 전체가 눌리는 게 있네 · 보드게임들 다 확인해 봐야겠는데? 오류가 심각하게 많아」
   한 패드 4자리(위 두 자리는 거꾸로) 실제 화면에서 「진짜 손가락 터치」로 눌러 봄
   ① 🎨 땅따먹기: 누른 칸 하나만 내 색 · 칸 크기 그대로 (예전: 칸에 붙인 이름 pp 가 종이 인쇄용 .pp{210mm×297mm} 에 걸려 한 칸이 판 전체를 덮음)
   ② 🏃 장애물 점프: 제때 뛰면 넘어서 점수가 오름 (예전: 꼭대기 12.6 < 넘는 높이 14 → 누구나 0점)
   ③ 🍎 과일 받기: 거꾸로 앉은 자리도 바구니가 손가락 쪽으로 (예전: 반대쪽)
   ④ 🎈 풍선: 겹쳐 있어도 손가락 밑 내 색 풍선이 터짐
   ⑤ 🧱 탑 쌓기: 진짜 터치 → 블록이 떨어진 뒤 쌓임
   ⑥ 🚩 깃발 달리기 🔥 게이지가 흰 종이(A4)가 되지 않음 · 달리기 점수 글자 .pop 이 다른 화면으로 새지 않음
   ⑦ 이름이 겹친 CSS 없음 (harness.CSS_SCAN)"""
import asyncio, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
OPEN = """([n,kind])=>{ window.HY_NOHOW=1; try{ MG.close(true); }catch(e){} const P=[]; for(let i=0;i<n;i++) P.push({i, n:['루아','민준','서연','도윤'][i], col:Board.COL[i], ch:''});
  const ctx={words:()=>Study.lessons('elem')[0].ws, cfg:()=>({}), mkQ:()=>null}; MiniG.snd=()=>{}; MG.open({P, kind, title:MiniG.L[kind][0], sub:MiniG.L[kind][1], sk:'e', ctx, sec:90}, ()=>{}); return 1; }"""
async def main():
    bad = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={"width": 820, "height": 1180}, has_touch=True); pg = await ctx.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)
        await pg.evaluate("()=>{ window._hits=[]; window.hyCssHit=t=>window._hits.push(t); }"); await pg.evaluate(CSS_SCAN)
        async def start(kind):
            await pg.evaluate(OPEN, [4, kind])
            for _ in range(60):
                if await pg.evaluate("()=>!!(MG.o && MG.o.inst)"): break
                await pg.wait_for_timeout(150)
            await pg.wait_for_timeout(300)
        # ① 땅따먹기
        await start("paint")
        for z in (0, 2):
            pt = await pg.evaluate("(z)=>{ const g=MG.o.inst[z], r=g.cells[9+z].getBoundingClientRect(); window._b4=g.sh.get().slice(); return [r.left+r.width/2, r.top+r.height/2, Math.round(r.width), Math.round(r.height)]; }", z)
            await pg.touchscreen.tap(pt[0], pt[1]); await pg.wait_for_timeout(500)
            r = await pg.evaluate("(z)=>{ const g=MG.o.inst[z], A=g.sh.get(), d=[]; A.forEach((v,i)=>{ if(v!==window._b4[i]) d.push(i+':'+v); }); const q=g.cells[9+z].getBoundingClientRect(), G=g.host.getBoundingClientRect(); return [d, Math.round(q.width), Math.round(q.height), q.width<G.width/4 && q.height<G.height/4, g.cells.every(c=>c.getBoundingClientRect().width>10)]; }", z)
            ok(r[0] == [f"{9+z}:{z}"] and r[1] == pt[2] and r[2] == pt[3] and r[3] and r[4], f"① 땅따먹기 자리{z}{'(거꾸로)' if z < 2 else ''}: 누른 칸 하나만 · 칸 크기 그대로 {r} (누르기 전 {pt[2:]})")
        # ② 장애물 점프 — 장애물이 가까이 오면 진짜 터치
        await start("jump"); s0 = None
        for z in (1, 3):
            s0 = await pg.evaluate("()=>MG.o.inst.map(g=>g.sc)"); n = 0
            for _ in range(260):
                t = await pg.evaluate("(z)=>{ const g=MG.o.inst[z]; if(g.lock>0 || g.y>0.5) return null; const o=g.os.find(x=>!x.pass && !x.hit && x.x<36 && x.x>27); if(!o) return null; const r=g.host.getBoundingClientRect(); return [r.left+r.width/2, r.top+r.height/2]; }", z)
                if t: await pg.touchscreen.tap(t[0], t[1]); n += 1; await pg.wait_for_timeout(300)
                else: await pg.wait_for_timeout(40)
                if n >= 4: break
            await pg.wait_for_timeout(900); s1 = await pg.evaluate("()=>MG.o.inst.map(g=>g.sc)"); g = await pg.evaluate("(z)=>{ const g=MG.o.inst[z]; return [+g.thr.toFixed(1), +g.pk.toFixed(1)]; }", z)
            ok(n >= 3 and s1[z] - s0[z] >= 2 and g[1] > g[0] * 1.8, f"② 장애물 점프 자리{z}: {n}번 뛰어 +{s1[z]-s0[z]}점 (넘는 높이 {g[0]} · 꼭대기 {g[1]})")
        # ③ 과일 받기
        await start("fruit")
        for z in range(4):
            r = await pg.evaluate("(z)=>{ const r=MG.o.inst[z].F.getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; }", z); res = []
            for fx in (0.22, 0.78):
                x = r[0] + r[2] * fx; await pg.touchscreen.tap(x, r[1] + r[3] * 0.5); await pg.wait_for_timeout(500)
                res.append(round(abs(await pg.evaluate("(z)=>{ const k=MG.o.inst[z].K.getBoundingClientRect(); return k.left+k.width/2; }", z) - x)))
            ok(max(res) < r[2] * 0.1, f"③ 과일 받기 자리{z}{'(거꾸로)' if z < 2 else ''}: 바구니가 손가락 쪽으로 (차이 {res}px)")
        # ④ 풍선 — 내 색 풍선 위에 다른 색을 겹쳐 놓고 누름
        await start("balloon")
        r0 = await pg.evaluate("""()=>{ const g=MG.o.inst[2]; g.bs.forEach(o=>o.el.remove()); g.bs=[]; g.sp=99; const a=g.spawn(g.me.k%4), b=g.spawn((g.me.k+1)%4); [a,b].forEach(o=>{ o.x=50; o.y=40; o.v=0; o.el.style.left='50%'; o.el.style.bottom='40%'; }); const r=a.el.getBoundingClientRect(); return [r.left+r.width/2, r.top+r.height/2, g.sc, document.elementFromPoint(r.left+r.width/2, r.top+r.height/2).closest('.mgB')===b.el]; }""")
        await pg.touchscreen.tap(r0[0], r0[1]); await pg.wait_for_timeout(200)
        r = await pg.evaluate("()=>{ const g=MG.o.inst[2]; return [g.sc, g.bs.map(o=>o.pop?1:0)]; }")
        ok(r0[3] and r[0] == r0[2] + 1 and r[1][0] == 1 and r[1][1] == 0, f"④ 풍선: 다른 색이 위에 겹쳐도 내 색이 터짐 +1 {r}")
        # ⑤ 탑 쌓기 — 진짜 터치
        await start("stack")
        r = await pg.evaluate("()=>{ const g=MG.o.inst[3], top=g.L[0]; g.mv.x=top.x; g.mv.d=0; const r=g.host.getBoundingClientRect(); return [r.left+r.width/2, r.top+r.height/2, parseFloat(g.M.style.bottom), g.top()]; }")
        await pg.touchscreen.tap(r[0], r[1]); a = await pg.evaluate("()=>{ const g=MG.o.inst[3]; return [!!g.fl, g.T.querySelectorAll('.mgStB').length, g.sc]; }")
        await pg.wait_for_timeout(600); c = await pg.evaluate("()=>{ const g=MG.o.inst[3]; return [!!g.fl, g.T.querySelectorAll('.mgStB').length, g.sc, g.N.textContent, getComputedStyle(g.N).position, Math.round(g.host.getBoundingClientRect().right-g.N.getBoundingClientRect().right)]; }")
        ok(r[2] - r[3] >= 20 and a == [True, 1, 2] and c[:4] == [False, 2, 2, "1층 ✨"] and c[5] < 40, f"⑤ 탑 쌓기: 높은 곳({r[2]}%)에서 떨어진 뒤 쌓임 · 층수 글자는 제자리 {a} → {c}")
        hits = [json.loads(x)["s"] for x in await pg.evaluate("()=>{ window._cssScan(); return window._hits; }")]
        await pg.evaluate("()=>{ try{ MG.close(true); }catch(e){} }")
        # ⑥ 깃발 달리기 게이지 · .pop
        r = await pg.evaluate("""()=>{ const d=document.createElement('div'); d.id='tg'; d.style.cssText='position:fixed;left:0;top:0;width:500px;z-index:999'; d.innerHTML='<div class="frGauge" id="frGauge"></div><button class="frItem" id="frItem"></button><div class="frQ pop" id="tq"><div class="sent">a b c</div></div><button class="dmCh pop" id="tc"></button>'; document.body.appendChild(d);
          FlagRun.st=2; FlagRun.item=null; FlagRun.gauge(); const G=document.getElementById('frGauge').firstChild.getBoundingClientRect(), q=getComputedStyle(document.getElementById('tq')), c=getComputedStyle(document.getElementById('tc')); const o=[Math.round(G.width), Math.round(G.height), q.whiteSpace, q.webkitTextStrokeWidth, c.position]; d.remove(); return o; }""")
        ok(r[0] < 200 and r[1] < 60 and r[2] == "normal" and r[3] == "0px" and r[4] != "absolute", f"⑥ 깃발 달리기 🔥 게이지 {r[0]}×{r[1]}px (예전 794×1123 흰 종이) · 문제 카드 줄바꿈 {r[2]} · 테두리 {r[3]} · 상자 {r[4]}")
        r = await pg.evaluate("()=>{ show('scGame'); popScore('GREAT!', 'x2', '#fff', 46); const e=document.querySelector('#popLayer .pop'), c=e && getComputedStyle(e); return e ? [c.position, c.whiteSpace, e.className] : null; }")
        ok(r == ["absolute", "nowrap", "pop big"], f"⑥ 달리기 점수 글자는 그대로 {r}")
        ok(not hits, f"⑦ 이름이 겹친 CSS 없음 {hits}")
        ok(not real_errs(errs), f"JS 오류 없음 {real_errs(errs)[:2]}")
        await b.close()
    print("DONE bad=%d" % len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
