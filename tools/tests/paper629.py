# v629 🖨 시험지: 💬 생활영어 · 📒 문법 모드 + 유치원 단어 시험지 — 쪽 넘침 없음 · 답안지 · A/B · 🔄 바꾸기 · 읽기 쪽 · 휴대폰 화면
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from harness import *

OUT = os.environ.get("HY_OUT", "/tmp/paper629_")
bad = []
def ok(c, m):
    print(("OK  " if c else "BAD ") + m)
    if not c: bad.append(m)

STATE = """()=>{ const W=document.getElementById('ppWrap'); const z=W.style.zoom; W.style.zoom=''; const cols=[...W.querySelectorAll('.ppCol,.ppKC')];
  const over=cols.filter(c=>c.scrollHeight>c.clientHeight+1).length; W.style.zoom=z;
  return {pages:W.querySelectorAll('.pp').length, rd:W.querySelectorAll('.pp.rd').length, key:W.querySelectorAll('.pp.key').length, q:W.querySelectorAll('.pp:not(.rd):not(.key) .ppQ').length,
    over, info:document.getElementById('ppInfo').textContent, title:(W.querySelector('.ppHdT b')||{}).textContent||'', B:Paper.B ? Paper.B.total : -1,
    keyN:W.querySelectorAll('.pp.key .ppKS > span').length, secs:[...W.querySelectorAll('.pp:not(.rd):not(.key) .ppSec')].map(x=>x.textContent).slice(0,8)}; }"""
SET = """async (a)=>{ const el=document.getElementById(a[0]); el.value=a[1]; el.dispatchEvent(new Event('change',{bubbles:true})); await new Promise(r=>setTimeout(r,a[2]||700)); }"""

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1100, "height": 1300}); errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await boot(pg)
        await pg.evaluate("()=>{ localStorage.removeItem('hyeng_paper'); Paper.open({}); }"); await pg.wait_for_timeout(800)
        r = await pg.evaluate("()=>[...document.querySelectorAll('#ppMd button')].map(x=>x.dataset.v).join(',')")
        ok(r == "test,kw,ks,lf,gm", f"모드 5개 {r}")
        await pg.evaluate("()=>document.querySelector('#ppMd [data-v=lf]').click()"); await pg.wait_for_timeout(1500)
        vis = await pg.evaluate("()=>[getComputedStyle(document.getElementById('ppSet').parentNode).display, getComputedStyle(document.getElementById('ppLv').parentNode).display, getComputedStyle(document.getElementById('ppGb').parentNode).display]")
        ok(vis[0] == "none" and vis[1] != "none" and vis[2] == "none", f"생활영어 모드 = 책·Stage 숨김 · 수준 보임 {vis}")
        for lv, want in (("k", {"듣고", "그림과"}), ("g12", {"대답", "그림과", "빈칸"}), ("g34", {"대답", "그림과", "빈칸", "순서"}), ("g56", {"대답", "그림과", "빈칸", "순서", "뜻을"})):
            await pg.evaluate(SET, ["ppLv", lv, 900])
            await pg.evaluate(SET, ["ppLT", "5", 1200])
            st = await pg.evaluate(STATE)
            secs = " ".join(st["secs"])
            ok(st["rd"] >= 1 and st["key"] >= 1 and st["over"] == 0 and st["B"] >= 18 and st["q"] == st["B"] * 2 and all(w in secs for w in want) and "생활영어" in st["title"],
               f"생활영어 {lv}: 대화문 {st['rd']}쪽 · 문제 {st['B']}×A·B · 넘침 {st['over']} · {st['title']} · {secs[:80]}")
            if lv in ("k", "g34"):
                els = await pg.query_selector_all("#ppWrap .pp")
                for i, el in enumerate(els[:3]): await el.screenshot(path=f"{OUT}lf_{lv}_{i}.png")
        # 대화문 해석 쓰기 칸
        await pg.evaluate("()=>{ document.querySelector('#ppTy input[value=lfdk]').click(); }"); await pg.wait_for_timeout(1200)
        r = await pg.evaluate("()=>[document.querySelectorAll('#ppWrap .pp.rd .ppDl .ppLine').length, document.querySelectorAll('#ppWrap .pp.rd .ppDl small').length]")
        ok(r[0] > 10 and r[1] == 0, f"대화문 해석 쓰기 칸 {r}")
        # 🔄 바꾸기
        r = await pg.evaluate("async ()=>{ const q=document.querySelector('#ppWrap .ppQ[data-src]'); const t0=q.textContent; q.click(); await new Promise(z=>setTimeout(z,100)); document.querySelector('#ppWrap .ppSwap').click(); await new Promise(z=>setTimeout(z,600)); const q2=document.querySelector('#ppWrap .ppQ[data-src=\"'+q.dataset.src+'\"]'); return [t0.slice(0,40), q2 ? q2.textContent.slice(0,40) : null]; }")
        ok(r[1] and r[0] != r[1], f"생활영어 🔄 이 문제 바꾸기 {r}")
        # 📒 문법
        await pg.evaluate("()=>document.querySelector('#ppMd [data-v=gm]').click()"); await pg.wait_for_timeout(1500)
        for bk, want in (("g34", {"고르세요", "O, 틀리면", "고쳐", "늘어놓아"}), ("g56", {"고르세요", "O, 틀리면", "고쳐", "늘어놓아"}), ("mid", {"고르세요"})):
            await pg.evaluate(SET, ["ppGb", bk, 900]); await pg.evaluate(SET, ["ppGT", "3", 1200])
            st = await pg.evaluate(STATE); secs = " ".join(st["secs"])
            ok(st["rd"] >= 1 and st["key"] >= 1 and st["over"] == 0 and st["B"] >= 20 and all(w in secs for w in want) and "문법" in st["title"], f"문법 {bk}: 규칙 {st['rd']}쪽 · 문제 {st['B']} · 넘침 {st['over']} · {secs[:90]}")
            if bk == "g56":
                els = await pg.query_selector_all("#ppWrap .pp")
                for i, el in enumerate(els[:3]): await el.screenshot(path=f"{OUT}gm_{bk}_{i}.png")
        r = await pg.evaluate("()=>{ const t=[...document.querySelectorAll('#ppWrap .pp:not(.rd):not(.key) .ppQ')].map(x=>x.textContent); return [t.some(x=>/\\(아무것도 안 씀\\)/.test(x)) || true, t.filter(x=>/ - /.test(x)).length]; }")
        # 순서 쓰기 첫 낱말 소문자
        await pg.evaluate(SET, ["ppGb", "g34", 900]); await pg.evaluate(SET, ["ppGT", "11", 1500])
        r = await pg.evaluate("()=>{ const W=[...document.querySelectorAll('#ppWrap .ppWd')].map(x=>[...x.querySelectorAll('i')].map(i=>i.textContent)); return W.map(w=>w.filter(x=>/^[A-Z]/.test(x) && !/^(I|I'm|Mina|Minsu|Jiho|Tom|Amy|Korea|Seoul|Busan|Jeju)$/.test(x))).filter(a=>a.length).slice(0,5); }")
        ok(len(r) == 0, f"순서대로 쓰기: 대문자 첫 낱말로 답이 안 보임 {r}")
        # 읽기만 (문제 형식 다 끄기)
        await pg.evaluate("()=>{ document.querySelectorAll('#ppTy input:checked').forEach(x=>{ if(x.value!=='gmr') x.click(); }); }"); await pg.wait_for_timeout(1200)
        st = await pg.evaluate(STATE)
        ok(st["rd"] >= 1 and st["B"] == 0 and st["key"] == 0, f"규칙 정리만 {st['rd']}쪽 {st['info']}")
        await pg.evaluate("()=>{ document.querySelectorAll('#ppTy input:not(:checked)').forEach(x=>x.click()); }"); await pg.wait_for_timeout(800)
        # 다시 열면 문법 모드 그대로 · 단어 시험지 설정은 안 날아감
        await pg.evaluate("()=>{ Paper.close(); Paper.open({}); }"); await pg.wait_for_timeout(1800)
        r = await pg.evaluate("()=>[Paper.mode, document.querySelector('#ppMd .on').dataset.v, document.getElementById('paper').classList.contains('ppGmM')]")
        ok(r == ["gm", "gm", True], f"다시 열면 문법 모드 {r}")
        # 유치원 단어 시험지 (그림 보고 고르기 · 그림 선 잇기 · 빠진 글자)
        await pg.evaluate("()=>document.querySelector('#ppMd [data-v=test]').click()"); await pg.wait_for_timeout(900)
        r = await pg.evaluate("()=>[...document.getElementById('ppSet').options].map(o=>o.value).filter(v=>['kinder','abc','short'].indexOf(v)>=0)")
        ok("kinder" in r and "abc" in r, f"책 목록에 유치원 {r}")
        await pg.evaluate(SET, ["ppSet", "kinder", 1500])
        st = await pg.evaluate(STATE); secs = " ".join(st["secs"])
        r = await pg.evaluate("()=>[document.querySelectorAll('#ppWrap .ppM .r .ppPic').length, [...document.querySelectorAll('#ppTy input:checked')].map(x=>x.value).join(',')]")
        ok(st["over"] == 0 and "그림에 알맞은" in secs and "선으로" in secs and r[0] >= 3 and r[1] == "pic,match,gap", f"유치원 단어 시험지 {secs[:80]} · 그림 잇기 {r}")
        els = await pg.query_selector_all("#ppWrap .pp")
        for i, el in enumerate(els[:2]): await el.screenshot(path=f"{OUT}kin_{i}.png")
        # 인쇄 눌러도 오류 없음 (print 막아 둠)
        r = await pg.evaluate("async ()=>{ window.print=()=>{}; Paper.forcePdf=false; document.querySelector('#ppMd [data-v=lf]').click(); await new Promise(z=>setTimeout(z,1500)); Paper.print(); await new Promise(z=>setTimeout(z,300)); return document.querySelectorAll('#ppWrap .pp').length; }")
        ok(r > 0, f"생활영어 인쇄 {r}쪽")
        e = real_errs(errs); ok(not e, f"오류 없음 {e[:3]}")
        # 휴대폰에서 설정 칸
        ph = await b.new_page(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True); errs2 = []
        ph.on("pageerror", lambda e: errs2.append(str(e)))
        await boot(ph)
        await ph.evaluate("()=>{ Paper.open({}); }"); await ph.wait_for_timeout(800)
        await ph.evaluate("()=>document.querySelector('#ppMd [data-v=lf]').click()"); await ph.wait_for_timeout(1800)
        w = await ph.evaluate("()=>document.documentElement.scrollWidth - innerWidth")
        await ph.screenshot(path=f"{OUT}ph_lf.png")
        ok(w <= 0, f"휴대폰 가로 넘침 없음 {w}")
        r = await ph.evaluate("()=>[+document.getElementById('ppLF').value, +document.getElementById('ppLT').value]")
        ok(r == [0, 2], f"처음 범위 = 상황 1~3 {r}")
        e = real_errs(errs2); ok(not e, f"휴대폰 오류 없음 {e[:3]}")
        await b.close()
    print("PASS" if not bad else "FAIL", len(bad))
    if bad: sys.exit(1)

asyncio.run(main())
