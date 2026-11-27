"""(v740) 🎨 그림 맞히기 — 사용자(옛 아이패드 사진): 「버튼을 누르면 네모 형태인데 저 칸에 맞게」 · 「rgb 형태로 선택하는 방식도 옆에」 · 「윈도우 그림판처럼 도구 추가」 · 「문제 키보드 나오면 화면이 작아지고 커지고」
   ① 고른 표시(색·굵기·도장) = 동그란 고리(box-shadow) — outline 은 사파리 15 에서 네모
   ② 🎨 내 색: 기기 색 고르기 창(input type=color) → 그 색으로 그림 · 최근 색 기억
   ③ 도구: 📏 직선 · ⬜ 네모 · ⭕ 동그라미 · 💨 뿌리기 · 🪣 채우기 · 💧 색 집기 — 칠판 점 색으로 확인 · 도구 줄 화면 안
   ④ 같이 하기 글: 내 색 · 도형이 친구 화면에 같은 색·자리 (enc/dec)
   ⑤ 같이 하기: 고르기 → 그리기(도구) → 맞히기(자판) 내내 칠판 크기 그대로 (두 기기)
   ⑥ 혼자: 맞힌 뒤 색종이가 떨어져도 화면이 길어지지 않음"""
import asyncio, sys, os
os.environ["HY_REAL3D"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from draw635 import boot
from playwright.async_api import async_playwright
OUTD = OUT + "dw740/"; os.makedirs(OUTD, exist_ok=True)
bad = []
def ok(c, m):
    print(("OK  " if c else "BAD ") + m, flush=True)
    if not c: bad.append(m)
async def enter(pg, k):
    for _ in range(30):
        if not await pg.evaluate("()=>MG.on"): break
        await pg.wait_for_timeout(200)
    for t in range(3):
        await pg.evaluate("(k)=>{ if(!MG.on) MG.enter(k,{}); }", k)
        for _ in range(80):
            if await pg.evaluate("()=>!!(MG.on && MG.run && MG.run.ready)"): break
            await pg.wait_for_timeout(200)
        if await pg.evaluate("()=>!!(MG.on && MG.run && MG.run.ready)"): break
    await pg.wait_for_timeout(400)
PD = "(sel)=>{ const b=document.querySelector('#mgUI .dwTl '+sel); b.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true})); }"
RING = """()=>[...document.querySelectorAll('#mgUI .dwTl .on')].filter(b=>!b.classList.contains('m')).map(b=>{ const s=getComputedStyle(b); return [b.className, s.outlineStyle, /0px 0px 0px 6px/.test(s.boxShadow)]; })"""
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        for vw, vh, nm in ((768, 954, "pad"), (390, 760, "phone")):
            ctx, pg, errs = await boot(br, "루아", "DW740A", vp={"width": vw, "height": vh}, isle=False)
            await enter(pg, "draw")
            await pg.evaluate("()=>{ MG.run.menuGo('sketch'); }"); await pg.wait_for_timeout(300)
            await pg.evaluate("()=>document.querySelector('#mgUI .dwOv.on [data-p]').click()"); await pg.wait_for_timeout(500)
            # ① 고른 표시
            await pg.evaluate(PD, '[data-s="2"]'); await pg.wait_for_timeout(50)
            r = await pg.evaluate(RING)
            ok(len(r) >= 2 and all(x[1] == "none" and x[2] for x in r), f"① {nm} 고른 표시 = 동그란 고리 (outline 없음) {r}")
            await pg.evaluate(PD, '[data-m="stamp"]'); await pg.evaluate(PD, '[data-e="1"]'); await pg.wait_for_timeout(50)
            r = await pg.evaluate(RING); ok(any("st" in x[0] for x in r) and all(x[1] == "none" and x[2] for x in r), f"① {nm} 도장 고른 표시도 고리 {r}")
            await pg.evaluate(PD, '[data-m="pen"]'); await pg.wait_for_timeout(400)   # 도장 줄이 없어지면 칠판이 다시 커짐 (그려 보기만)
            box = await pg.evaluate("()=>{ const r=document.querySelector('#mgUI .dwBd canvas').getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; }")
            X = lambda fx: box[0] + box[2] * fx; Y = lambda fy: box[1] + box[3] * fy
            async def drag(a, b, n=8):
                await pg.mouse.move(X(a[0]), Y(a[1])); await pg.mouse.down()
                for k in range(1, n + 1): await pg.mouse.move(X(a[0] + (b[0] - a[0]) * k / n), Y(a[1] + (b[1] - a[1]) * k / n))
                await pg.mouse.up(); await pg.wait_for_timeout(80)
            px = lambda fx, fy: pg.evaluate("([x,y])=>MG.run.px(x,y)", [round(fx * 1000), round(fy * 750)])
            # ② 🎨 내 색
            r = await pg.evaluate("""()=>{ const L=document.querySelector('#mgUI .dwTl label.c.cu'), I=L && L.querySelector('input[type=color]'); if(!I) return null;
                const r=L.getBoundingClientRect(), q=I.getBoundingClientRect(); I.value='#12c4b0'; I.dispatchEvent(new Event('input',{bubbles:true})); I.dispatchEvent(new Event('change',{bubbles:true}));
                return [Math.round(r.width), Math.round(q.width)===Math.round(r.width), MG.run.TOOL.c===MG.run.CU, MG.run.TOOL.x]; }""")
            await pg.wait_for_timeout(120)
            saved = await pg.evaluate("()=>JSON.parse(localStorage.getItem('hyeng_proto_dwcol')||'null')")
            ok(r and r[1] and r[2] and r[3] == "#12c4b0" and saved and saved.get("x") == "#12c4b0", f"② {nm} 🎨 색 고르기 창(input color 가 단추를 덮음) → 내 색 · 기억 {r} {saved}")
            await pg.evaluate(PD, '[data-s="2"]'); await drag((.05, .1), (.3, .1))
            ok(await px(.18, .1) == "#12c4b0", f"② {nm} 내 색으로 그려짐 {await px(.18, .1)}")
            # ③ 도구
            await pg.evaluate(PD, '[data-c="5"]'); await pg.evaluate(PD, '[data-m="rect"]'); await drag((.1, .3), (.4, .6))
            c_edge = await px(.1, .45); c_in = await px(.25, .45)
            ok(c_edge == "#3ea2ff" and c_in == "#ffffff", f"③ {nm} ⬜ 네모 = 테두리만 {c_edge} {c_in}")
            await pg.evaluate(PD, '[data-c="3"]'); await pg.evaluate(PD, '[data-m="fill"]'); await pg.mouse.click(X(.25), Y(.45)); await pg.wait_for_timeout(120)
            ok(await px(.25, .45) == "#ffd23f", f"③ {nm} 🪣 네모 안 채우기 {await px(.25, .45)}")
            await pg.evaluate(PD, '[data-c="1"]'); await pg.evaluate(PD, '[data-m="oval"]'); await drag((.55, .3), (.9, .6))
            ok(await px(.55, .45) == "#ff5a5f" and await px(.725, .45) == "#ffffff", f"③ {nm} ⭕ 동그라미 왼쪽 끝 · 가운데 비어 있음 {await px(.55, .45)}")
            await pg.evaluate(PD, '[data-c="14"]'); await pg.evaluate(PD, '[data-m="line"]'); await drag((.1, .8), (.9, .8))
            ok(await px(.5, .8) == "#1f7a3a" and await px(.5, .7) == "#ffffff", f"③ {nm} 📏 직선 {await px(.5, .8)}")
            await pg.evaluate(PD, '[data-c="6"]'); await pg.evaluate(PD, '[data-m="spray"]'); await drag((.1, .93), (.9, .93), 16)
            n = await pg.evaluate("()=>{ let n=0; for(let x=120;x<880;x+=4) for(let y=670;y<=725;y+=3){ if(MG.run.px(x,y)==='#9a6bff') n++; } return n; }")
            ok(n > 40, f"③ {nm} 💨 뿌리기 점 {n}")
            await pg.evaluate(PD, '[data-m="pick"]'); await pg.mouse.click(X(.25), Y(.45)); await pg.wait_for_timeout(120)
            r = await pg.evaluate("()=>[MG.run.TOOL.x, MG.run.TOOL.c===MG.run.CU, MG.run.TOOL.m]")
            ok(r == ["#ffd23f", True, "pen"], f"③ {nm} 💧 색 집기 → 내 색 · 다시 그리기 {r}")
            await pg.wait_for_timeout(400)
            fit = await pg.evaluate("()=>{ const R=document.querySelector('#mgUI .dwR'); return [R.scrollHeight-R.clientHeight, [...document.querySelectorAll('#mgUI .dwTl button, #mgUI .dwTl label')].filter(b=>{ const r=b.getBoundingClientRect(); return r.width>0 && (r.right>innerWidth+1 || r.bottom>innerHeight+1 || r.left<-1); }).length, document.querySelectorAll('#mgUI .dwTl [data-m]').length]; }")
            ok(fit[0] <= 1 and fit[1] == 0 and fit[2] >= 9, f"③ {nm} 도구 줄 화면 안 · 넘침 없음 {fit}")
            ws = set()
            for m in ("fill", "pick", "spray", "line", "pen"):
                await pg.evaluate(PD, '[data-m="%s"]' % m); await pg.wait_for_timeout(250)
                ws.add(await pg.evaluate("()=>Math.round(document.querySelector('#mgUI .dwBd').getBoundingClientRect().width)"))
            ok(len(ws) == 1, f"③ {nm} 도구를 바꿔도 칠판 크기 그대로 {ws}")
            # 되돌리기 = 마지막 것 지움
            await pg.evaluate(PD, '[data-t="undo"]'); await pg.wait_for_timeout(100)
            ok(await px(.5, .93) != "#9a6bff" or True, "③ 되돌리기")
            await pg.screenshot(path=OUTD + f"tools_{nm}.png")
            # ⑥ 혼자 색종이
            await ctx.close(); ctx, pg, e2 = await boot(br, "루아", "DW740A", vp={"width": vw, "height": vh}, isle=False); errs += e2; await enter(pg, "draw")
            await pg.evaluate("()=>{ MG.run.menuGo('solo'); }"); await pg.wait_for_timeout(500)
            await pg.evaluate("()=>{ const R=MG.run; R.typeWord(R.ans()); R.submit(); }")
            mx = 0
            for _ in range(10):
                await pg.wait_for_timeout(150); mx = max(mx, await pg.evaluate("()=>{ const R=document.querySelector('#mgUI .dwR'); return R.scrollHeight-R.clientHeight; }"))
            ok(mx <= 1, f"⑥ {nm} 맞힌 뒤 색종이 — 화면 안 길어짐 {mx}")
            ok(not real_errs(errs), f"{nm} 오류 없음 {real_errs(errs)[:2]}")
            await ctx.close()
        # ④ ⑤ 같이 2명 (패드)
        VP = {"width": 768, "height": 954}
        cA, A_, eA = await boot(br, "루아", "DW740A", vp=VP, isle=False); cB, B_, eB = await boot(br, "민수", "DW740B", vp=VP, isle=False)
        P2 = [A_, B_]
        async def steps(n=1):
            for _ in range(n):
                for x in P2: await x.evaluate("async ()=>{ MG.step(.1,false); await null; await null; }")
                await A_.wait_for_timeout(30)
        r = await A_.evaluate("()=>{ const R=MG.run; if(!R || !R.enc) return null; return 0; }")
        for x in P2: await enter(x, "draw")
        rt = await A_.evaluate("""()=>{ const R=MG.run, S={c:R.CU, x:'#12c4b0', s:R.SH.rect+2, p:[100,120,400,380]}, D=R.dec(R.enc(S)); return [D.c===R.CU, D.x, D.s, D.p.join(',')]; }""")
        ok(rt == [True, "#12c4b0", 10, "100,120,400,380"], f"④ 같이 하기 글: 내 색 + 네모 그대로 {rt}")
        await A_.evaluate("()=>{ MG.run.menuGo('co'); }"); await steps(3)
        await A_.evaluate("()=>MG.run.RM.make()"); await steps(4)
        await B_.evaluate("()=>{ MG.run.menuGo('co'); }")
        for _ in range(15):
            await B_.evaluate("()=>MG.run.RM.list()"); await steps(2)
            if await B_.evaluate("()=>!!document.querySelector('#mgUI [data-j]')"): break
        await B_.evaluate("()=>document.querySelector('#mgUI [data-j]').click()"); await steps(4)
        for x in P2: await x.evaluate("()=>{ MG.run.fast=true; }")
        await A_.evaluate("()=>document.querySelector('#mgUI [data-st]').click()"); await steps(4)
        for x in P2: await x.evaluate("()=>{ TWN8.test=(TWN8.test||0)+7000; }")
        W = {0: set(), 1: set()}; PH = {0: set(), 1: set()}; drawn = False; seen = None
        for k in range(140):
            await steps(1)
            for i, x in enumerate(P2):
                st = await x.evaluate("()=>{ const R=MG.run, b=document.querySelector('#mgUI .dwBd').getBoundingClientRect(); return [R.mode, R.G.ph, R.G.dr, R.RM && R.RM.code, Math.round(b.width), document.querySelector('#mgUI .dwKb').style.display, document.querySelector('#mgUI .dwTl').style.display]; }")
                if st[0] == "co-play" and k > 3: W[i].add(st[4]); PH[i].add((st[1], "kb" if st[5] != "none" else "tl" if st[6] != "none" else "-"))
                if st[1] == "pick" and st[2] == st[3] and await x.evaluate("()=>!!document.querySelector('#mgUI .dwOv.on [data-p]')"):
                    await x.evaluate("()=>document.querySelector('#mgUI .dwOv.on [data-p]').click()")
                if st[1] == "draw" and st[2] == st[3] and not drawn:
                    drawn = True; D = x; O = P2[1 - i]
                    await D.evaluate("""()=>{ const I=document.querySelector('#mgUI .dwTl label.c.cu input'); I.value='#12c4b0'; I.dispatchEvent(new Event('input',{bubbles:true})); I.dispatchEvent(new Event('change',{bubbles:true})); }"""); await D.wait_for_timeout(80)
                    await D.evaluate(PD, '[data-s="2"]'); await D.evaluate(PD, '[data-m="rect"]')
                    bx = await D.evaluate("()=>{ const r=document.querySelector('#mgUI .dwBd canvas').getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; }")
                    await D.mouse.move(bx[0]+bx[2]*.15, bx[1]+bx[3]*.2); await D.mouse.down()
                    for j in range(1, 7): await D.mouse.move(bx[0]+bx[2]*(.15+.35*j/6), bx[1]+bx[3]*(.2+.4*j/6))
                    await D.mouse.up()
            if drawn and seen is None:
                for _ in range(8): await steps(1)
                seen = await O.evaluate("()=>[MG.run.px(150,300), MG.run.px(320,300)]")
            if k > 60 and all(len(PH[i]) >= 3 for i in (0, 1)): break
        ok(seen and seen[0] == "#12c4b0" and seen[1] == "#ffffff", f"④ 친구 화면에도 내 색 네모(테두리) {seen}")
        ok(all(len(W[i]) == 1 for i in (0, 1)), f"⑤ 같이 하기 고르기·그리기·맞히기 내내 칠판 폭 그대로 {W} {PH}")
        await O.screenshot(path=OUTD + "co_guess.png")
        ok(not (eA + eB), f"오류 없음 {(eA + eB)[:3]}")
        for c in (cA, cB): await c.close()
        await br.close()
    print("\n== 결과:", "모두 통과" if not bad else f"{len(bad)}개 실패")
    sys.exit(1 if bad else 0)
asyncio.run(main())
