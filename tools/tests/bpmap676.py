"""(v676) 사용자: 친구 패드엔 「방장 화면을 봐요」+순위만 → 시안대로 방장 판 그림 위에 말 자리 · ⭐ 칸 · 「나」 · 지금 차례 표시
   ① 방장(BoardTV.st)이 말 자리(pos)·별 칸(sp)을 보냄  ② 차례 화면: 판이 보이고 말·별이 그 칸 자리 · 내 말 「나」 · 차례인 말 cur · ⭐까지 N칸
   ③ 말이 움직이면 같은 말이 자리만 바뀜(스르륵)  ④ 내 문제·미니게임·기다림 화면에선 숨김  ⑤ 휴대폰·가로 낮은 화면에서 판이 화면 안"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright
MK = """(st)=>{ let d=document.getElementById('board'); if(d) d.remove(); d=document.createElement('div'); d.id='board'; d.className='bdModePad sk-e';
  d.innerHTML='<div class="bpTop"><button class="bdX" data-bp="x">✕</button><div class="bpMe" id="bpMe"></div><b class="bdRnd" id="bpRnd"></b></div><div class="bpMap" id="bpMap" hidden></div><div class="bpBody" id="bpBody"></div><div class="bpMG" id="bpMG" hidden></div>';
  document.body.appendChild(d); BoardPad.me='kb'; BoardPad.nm='서연'; BoardPad.room='1234'; FB.update=()=>Promise.resolve(); BoardPad.st=st; BoardPad.draw(); return 1; }"""
ST = {"s": "play", "kh": 1, "cur": 0, "rnd": 3, "R": 10, "sk": "e", "sp": 15, "P": [
    {"n": "민준", "col": "#ff4d6d", "ch": 0, "mem": ["ka"], "star": 2, "coin": 14, "it": [], "pos": 7},
    {"n": "서연", "col": "#3fa9ff", "ch": 3, "mem": ["kb"], "star": 1, "coin": 21, "it": [], "pos": 12},
    {"n": "도윤", "col": "#2fd27a", "ch": 5, "mem": ["kc"], "star": 1, "coin": 9, "it": [], "pos": 3}]}
CHK = """()=>{ const M=document.getElementById('bpMap'), r=M.getBoundingClientRect(), SK=Board.SK.e, s=BoardPad.st;
  const tk=[...M.querySelectorAll('.bpTk')].map(t=>{ const q=SK.P[s.P[+t.dataset.i].pos]; const L=parseFloat(t.style.left), T=parseFloat(t.style.top); return [+t.dataset.i, Math.abs(L-q[0]*100)<0.1 && Math.abs(T-q[1]*100)<0.1, t.classList.contains('cur'), t.classList.contains('me')]; });
  const S=M.querySelector('.bpMpS'), q=SK.P[s.sp];
  return {vis:!M.hidden && r.height>50, inView:r.top>=0 && r.bottom<=innerHeight+1 && r.left>=0 && r.right<=innerWidth+1, h:Math.round(r.height), tk, star:Math.abs(parseFloat(S.style.left)-q[0]*100)<0.1 && !!S.querySelector('img,.bdIc'), lab:M.querySelector('.bpMpT').textContent,
    body:document.getElementById('bpBody').innerText.replace(/\\s+/g,' ').slice(0,40)}; }"""

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await br.new_page(viewport={"width": 820, "height": 1180})
        pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg); E = pg.evaluate
        await E("()=>{ window._hits=[]; window.hyCssHit=t=>window._hits.push(t); }"); await E(CSS_SCAN)
        # ① 방장 상태
        r = await E("""()=>{ Board.begin({sk:'e', set:'elem', from:0, to:3, qt:['mean'], sec:0, rounds:3, star:12, tv:1, P:[{n:'루아',id:'',ch:0,mem:[{id:'a',n:'루아'}]},{n:'주호',id:'',ch:3,mem:[{id:'b',n:'주호'}]}]}); Board.o.P[1].pos=5; const st=BoardTV.st(); Board.close&&Board.close(); const d=document.getElementById('board'); if(d) d.remove(); return [st.sp, st.P.map(x=>x.pos)]; }""")
        ok(r == [12, [0, 5]], f"① 방장이 말 자리·별 칸을 보냄 {r}")
        # ② 차례 화면
        await E(MK, ST); await pg.wait_for_timeout(300)
        r = await E(CHK)
        ok(r["vis"] and r["inView"] and all(t[1] for t in r["tk"]) and [t[2] for t in r["tk"]] == [True, False, False] and [t[3] for t in r["tk"]] == [False, True, False] and r["star"] and r["lab"] == "⭐까지 3칸" and "민준 차례" in r["body"], f"② 판 · 말 자리 · 차례 · 나 · 별 {r}")
        # ③ 움직임 = 같은 말
        r = await E("""(st)=>{ const t0=document.querySelector('#bpMap .bpTk[data-i="0"]'); st=JSON.parse(JSON.stringify(st)); st.P[0].pos=10; st.cur=1; BoardPad.st=st; BoardPad.draw(); const t1=document.querySelector('#bpMap .bpTk[data-i="0"]'); return [t0===t1, getComputedStyle(t1).transitionProperty, document.querySelector('#bpMap .bpTk[data-i="1"]').classList.contains('cur')]; }""", ST)
        ok(r[0] and "left" in r[1] and r[2], f"③ 말이 움직이면 같은 말이 자리만 (스르륵) {r}")
        # ④ 숨김
        r = await E("""(st)=>{ const o=[]; const S=x=>{ BoardPad.st=x; BoardPad.draw(); o.push(document.getElementById('bpMap').hidden); };
          S(Object.assign({}, st, {req:{id:7, who:['kb'], h:'<div class="bdQ"><button class="bdO" data-bd="opt" data-k="0">a</button></div>', q:1}}));
          BoardPad.ans=0; S(Object.assign({}, st, {s:'wait'})); S(Object.assign({}, st, {s:'end', end:[{n:'민준',col:'#f00',star:2,coin:3,mem:['ka']}]})); BoardPad.ans=7; S(Object.assign({}, st, {req:{id:7, who:['kb'], h:'x', q:1}}));
          return o; }""", ST)
        ok(r == [True, True, True, False], f"④ 내 문제·기다림·끝 = 숨김 · 「보냈어요」 = 보임 {r}")
        # ⑤ 크기
        for vp in ({"width": 390, "height": 844}, {"width": 1280, "height": 593}, {"width": 844, "height": 390}):
            await pg.set_viewport_size(vp); await E(MK, ST); await pg.wait_for_timeout(300); r = await E(CHK)
            rk = await E("()=>{ const b=document.getElementById('bpBody'); return b.scrollHeight<=b.clientHeight+2 || b.clientHeight>120; }")
            ok(r["vis"] and r["inView"] and rk, f"⑤ {vp['width']}×{vp['height']}: 판 화면 안 (높이 {r['h']}) · 아래 칸 남음 {rk}")
        await pg.set_viewport_size({"width": 820, "height": 1180}); await E(MK, ST); await pg.wait_for_timeout(700)
        await pg.screenshot(path=OUT + "bpmap676.png")
        hits = await E("()=>window._hits"); ok(not hits, f"이름 겹친 CSS 없음 {hits[:3]}")
        ok(not real_errs(errs), f"JS 오류 없음 {real_errs(errs)[:2]}")
        await br.close()
    print("DONE bad=%d" % len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
