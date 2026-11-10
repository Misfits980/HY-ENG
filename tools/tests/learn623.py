# v623 단어·문법 외우기 연구 반영 — ① 틀리면 한 번 더 ② 기억 칸에 맞춘 복습 ③ G3-4 문법 찾기 카드 ④ 🔀 문법 섞어 풀기
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from harness import *

OUT = os.environ.get("HY_OUT", "/tmp/learn623_")
bad = []
def ok(c, m):
    print(("OK  " if c else "BAD ") + m)
    if not c: bad.append(m)

SETUP = """(st)=>{ Online.on=()=>false; const s=Study.load(); s.book=Object.keys(Study.BOOKS).find(b=>Study.BOOKS[b].sets.indexOf(st)>=0); s.set=st; Study.save(); StudyUI.open(); StudyUI.start(0,false); }"""
# 다음 고르는 문제(보기 3개+)까지 풀어 나감
TO_CHOICE = """async ()=>{ const U=StudyUI; for(let i=0;i<80;i++){ const q=U.qs[U.i]; if(U._v!=='stLesson') return null;
    if(q && !U.locked && q.t!=='intro'){ const S=U.sel; U.sel=0; const e=U.try2Ok(q); U.sel=S; if(e) return {t:q.t, n:q.opts.length}; }
    await window.__solve(); await new Promise(r=>setTimeout(r,60)); } return null; }"""

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for nm, (w, h) in (("ph", (390, 844)), ("pad", (820, 1180)), ("tv", (1920, 1080))):
            pg = await b.new_page(viewport={"width": w, "height": h}, is_mobile=nm != "tv", has_touch=nm != "tv"); errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            await boot(pg)
            await pg.evaluate("(src)=>{ window.__solve=()=>Promise.resolve((new Function('return ('+src+')'))()(false)); }", SOLVE)

            # ① 틀리면 한 번 더 — 세트 셋 (테마 셋)
            for st in (["basic", "g56", "mid"] if nm != "tv" else ["elem"]):
                await pg.evaluate(SETUP, st); await pg.wait_for_timeout(700)
                c = await pg.evaluate(TO_CHOICE)
                if not c: ok(False, f"{nm} {st} 고르는 문제를 못 찾음"); continue
                r = await pg.evaluate("""()=>{ const U=StudyUI, q=U.qs[U.i], b=[...document.querySelectorAll('#stQ .stOpt')];
                    const right=k=>{ const o=q.opts[k]; return q.so ? o===q.ans : q.t==='blend' ? o===q.mid : q.t==='past' ? o===q.w.en : q.t==='sentp' ? o===q.form : (o && o.en===q.w.en); };
                    const wk=q.opts.findIndex((o,k)=>!right(k)), rk=q.opts.findIndex((o,k)=>right(k)); const f0=U.first, n0=U.qs.length, lv0=JSON.stringify((Study.load().srs||{})[q.w.en]||null);
                    b[wk].click(); const s1={locked:U.locked, tried:b[wk].classList.contains('tried'), foot:document.getElementById('stFoot').className, msg:document.getElementById('stFoot').innerText.slice(0,40), n:U.qs.length===n0};
                    b[wk].click(); const s2={locked:U.locked};
                    b[rk].click(); const s3={locked:U.locked, first:U.first===f0, foot:document.getElementById('stFoot').className, lv:JSON.stringify((Study.load().srs||{})[q.w.en]||null), lv0};
                    return {t:q.t, s1, s2, s3}; }""")
                s1, s2, s3 = r["s1"], r["s2"], r["s3"]
                ok(not s1["locked"] and s1["tried"] and "try" in s1["foot"] and "한 번 더" in s1["msg"] and s1["n"], f"{nm} {st} ① 처음 틀리면 정답 안 보여 주고 한 번 더 ({r['t']}) {s1}")
                ok(not s2["locked"], f"{nm} {st} ① 흐려진 보기는 다시 눌러도 안 됨")
                ok(s3["locked"] and s3["first"] and "good" in s3["foot"], f"{nm} {st} ① 두 번째에 맞히면 맞힘 · 한 번에 맞힘은 안 셈 {s3['foot']}")
                if st in ("basic", "mid") or nm == "tv":
                    await pg.evaluate("()=>{ const U=StudyUI, q=U.qs[U.i]; }")
                # 화면: 한 번 더 상태
                await pg.evaluate(SETUP, st); await pg.wait_for_timeout(700); await pg.evaluate(TO_CHOICE)
                await pg.evaluate("""()=>{ const U=StudyUI, q=U.qs[U.i], b=[...document.querySelectorAll('#stQ .stOpt')]; const right=k=>{ const o=q.opts[k]; return q.so ? o===q.ans : q.t==='blend' ? o===q.mid : q.t==='past' ? o===q.w.en : q.t==='sentp' ? o===q.form : (o && o.en===q.w.en); }; b[q.opts.findIndex((o,k)=>!right(k))].click(); }""")
                await pg.wait_for_timeout(300); await pg.screenshot(path=f"{OUT}{nm}_try_{st}.png")
                sc = await pg.evaluate("()=>{ const s=document.getElementById('scStudy'); const f=document.getElementById('stFoot').getBoundingClientRect(); return {sh:s.scrollHeight>s.clientHeight+4, fb:f.bottom<=innerHeight+1, ft:Math.round(f.top)}; }")
                ok(sc["fb"], f"{nm} {st} ① 아래 칸이 화면 안 {sc}")
                # 끝까지 — 두 번 틀려도 오류 없이 끝남
                await pg.evaluate("""async ()=>{ for(let i=0;i<200 && StudyUI._v==='stLesson';i++){ await window.__solve(); await new Promise(r=>setTimeout(r,40)); } }""")
                await pg.wait_for_timeout(1500)
                ok(await pg.evaluate("()=>StudyUI._v") == "stDone", f"{nm} {st} ① 판 끝까지 감")

            # ② 기억 칸에 맞춘 복습
            if nm == "ph":
                r = await pg.evaluate("""()=>{ const st='elem', L=Study.lessons(st), ws=[].concat(...L.slice(0,3).map(x=>x.ws)).slice(0,10); const s=Study.load(); s.srs=s.srs||{};
                    const T={}; const run=lv=>{ ws.forEach(w=>{ s.srs[w.en]=[lv, 0]; }); Study.save(); const o={}; for(let k=0;k<6;k++){ const qs=Study.buildReview(st)||[]; qs.slice(0, ws.length).forEach(q=>{ o[q.t]=(o[q.t]|0)+1; }); } return o; };
                    T.lo=run(1); T.mid=run(3); T.hi=run(6); return T; }""")
                prod = lambda o: sum(v for k, v in o.items() if k in ("spell", "dict", "sent", "kdict"))
                tot = lambda o: max(1, sum(o.values()))
                print("  복습 종류", r)
                ok(prod(r["hi"]) / tot(r["hi"]) > 0.8, f"② 5칸 넘은 단어는 꺼내 쓰기(철자·받아쓰기·빈칸) 위주 {r['hi']}")
                ok(prod(r["hi"]) / tot(r["hi"]) > prod(r["lo"]) / tot(r["lo"]), f"② 칸이 높을수록 쓰기가 많음 lo={r['lo']}")
                # 하루 한 칸 (v622) 그대로
                r = await pg.evaluate("()=>{ const en=WORD_BANK[3].en; const s=Study.load(); delete (s.srs||{})[en]; Study.save(); Study.mark(en,true); Study.mark(en,true); return Study.load().srs[en][0]; }")
                ok(r == 1, f"② 같은 날 여러 번 맞혀도 한 칸 ({r})")

            # ③ G3-4 문법 찾기 카드
            r = await pg.evaluate("""()=>GNote.load().then(()=>Gram.load()).then(()=>{ const o={}; ['be','pl','s3','past'].forEach(k=>{ const D=GNote.disc(k); o[k]=D ? [D.ex.length, D.rs.length] : null; });
                  const v=GNote.st(); delete v.seen.be; GNote.put(v); return o; })""")
            ok(r["be"] == [3, 3] and r["pl"] and r["s3"] and r["past"] is None, f"{nm} ③ 초3-4 문법만 찾기 카드 (예문·규칙 수) {r}")
            await pg.evaluate("""()=>{ const s=Study.load(); s.book='g34'; s.set='elem'; Study.save(); StudyUI.open(); StudyUI.start(0,false);
                const U=StudyUI, q={t:'gram', w:WORD_BANK[0], so:1, ans:'is', opts:['am','is','are'], st:{pre:'She ', post:' kind.', ko:'', cap:false}, x:{kind:'be', why:'she → is'}};
                U.qs.splice(U.i, 0, q); U.show(); }""")
            await pg.wait_for_timeout(500)
            r = await pg.evaluate("()=>{ const q=StudyUI.qs[StudyUI.i]; const c=document.querySelector('#stQ .grCard'); return {hd:q.hd, dc:!!q.dc, disc:!!(c && c.classList.contains('disc')), ex:c?c.querySelectorAll('.grExR').length:0, rv:!!(c && c.querySelector('details.grRv')), open:!!(c && c.querySelector('details.grRv[open]'))}; }")
            ok(r["hd"] == "gl" and r["disc"] and r["ex"] == 3 and r["rv"] and not r["open"], f"{nm} ③ 공부 중 처음 만난 be = 예문 3개 + 💡 규칙은 눌러야 {r}")
            await pg.screenshot(path=f"{OUT}{nm}_disc_lesson.png")
            await pg.evaluate("()=>{ const d=document.querySelector('#stQ details.grRv'); if(d) d.open=true; }"); await pg.wait_for_timeout(200)
            await pg.screenshot(path=f"{OUT}{nm}_disc_lesson_open.png")
            sc = await pg.evaluate("()=>{ const d=document.querySelector('#stQ details.grRv').getBoundingClientRect(), f=document.getElementById('stFoot').getBoundingClientRect(), s=document.getElementById('scStudy'); return {b:Math.round(d.bottom), ft:Math.round(f.top), top:s.scrollTop}; }")
            ok(sc["b"] <= sc["ft"] + 2, f"{nm} ③ 💡 규칙을 펴도 아래 단추에 안 가려짐 {sc}")
            # GramUI g34 레슨 카드
            await pg.evaluate("()=>{ localStorage.removeItem('hyeng_gram_v1'); Gram.put('g34-2', {s:1}); GramUI.start('g34-3'); }"); await pg.wait_for_timeout(700)
            r = await pg.evaluate("()=>{ const c=document.querySelector('#stGram .grCard'); return {disc:!!(c && c.classList.contains('disc')), lab:(document.querySelector('#stGram .grHead small')||{}).textContent||''}; }")
            ok(r["disc"] and "찾아보기" in r["lab"], f"{nm} ③ 문법 돌(am·are·is) 처음 = 찾기 카드 {r}")
            await pg.screenshot(path=f"{OUT}{nm}_disc_gram.png")
            await pg.evaluate("()=>GramUI.start('g34-3', true)"); await pg.wait_for_timeout(600)
            r = await pg.evaluate("()=>{ const c=document.querySelector('#stGram .grCard'); return !!(c && !c.classList.contains('disc')); }")
            ok(r, f"{nm} ③ 📒 자세히로 다시 보면 설명 카드")
            r = await pg.evaluate("()=>{ Gram.put('g34-1',{s:1}); GramUI.res={pass:true, up:false, pct:1, gem:0, need:3, tier:2}; GramUI.mode='end'; GramUI.draw(); return !!document.querySelector('#stGram .grEnd [data-gr=mix]'); }")
            ok(r, f"{nm} ④ 문법 돌 끝 화면에도 🔀 섞어 풀기 (배운 문법 둘 넘으면)")
            r = await pg.evaluate("()=>{ GramUI.start('g56-1'); return new Promise(z=>setTimeout(()=>{ const c=document.querySelector('#stGram .grCard'); z(!!(c && !c.classList.contains('disc'))); }, 500)); }")
            ok(r, f"{nm} ③ G5-6 문법은 지금처럼 설명 먼저")
            r = await pg.evaluate("()=>Gram.load().then(()=>{ const n=g=>[].concat(...Gram.get(g).cards.filter(c=>c.k==='rule').map(c=>c.ex)).length; return [n('g34-4'), n('g34-5')]; })")
            ok(r[0] >= 10 and r[1] >= 13, f"{nm} ③ this·that / my·your 예문 보탬 {r}")

            # ④ 🔀 섞어 풀기
            await pg.evaluate("()=>{ ['g34-1','g34-2','g34-3','g34-6','g34-7'].forEach((id,i)=>Gram.put(id, {s:1, at:Date.now()-i*1e6})); const v=GNote.st(); delete v.s.be; delete v.s.pl; GNote.put(v); }")
            await pg.evaluate("()=>GramUI.note('g34')"); await pg.wait_for_timeout(700)
            r = await pg.evaluate("()=>{ const b=document.querySelector('#stGram .grMixB'); return b ? b.innerText.replace(/\\s+/g,' ') : null; }")
            ok(bool(r) and "섞어 풀기" in r, f"{nm} ④ 문법 노트에 🔀 섞어 풀기 단추 {r}")
            await pg.screenshot(path=f"{OUT}{nm}_mix_note.png")
            g0 = await pg.evaluate("()=>Wallet.gems()")
            await pg.click("#stGram .grMixB"); await pg.wait_for_timeout(700)
            r = await pg.evaluate("()=>{ const Q=GramUI.qs; let same=0; for(let i=1;i<Q.length;i++) if(Q[i].from===Q[i-1].from) same++; return {mode:GramUI.mode, n:Q.length, topics:[...new Set(Q.map(q=>q.from))].length, same, lab:(document.querySelector('#stGram .grFrom')||{}).textContent||''}; }")
            ok(r["mode"] == "quiz" and r["n"] == 10 and r["topics"] >= 3 and r["same"] == 0 and "📒" in r["lab"], f"{nm} ④ 10문제 · 문법 3~4개 · 같은 문법 연달아 없음 {r}")
            await pg.screenshot(path=f"{OUT}{nm}_mix_q.png")
            await pg.evaluate("()=>{ GramUI.peek=true; GramUI.draw(); }"); await pg.wait_for_timeout(200)
            r = await pg.evaluate("()=>document.querySelectorAll('#stGram .grPeek .grCard').length")
            ok(r >= 1, f"{nm} ④ 📒 규칙 = 지금 문제의 문법 카드 ({r})")
            await pg.evaluate("()=>{ GramUI.peek=false; GramUI.draw(); }")
            # 다 풀기 (첫 문제만 틀림)
            await pg.evaluate("""async ()=>{ const G=GramUI; let k=0; while(G.mode==='quiz' && k++<40){ const q=G.qs[G.qi];
                  if(!q.res){ const wrong = k===1; if(q.k==='pick'){ const i=q.opts.findIndex(o=> wrong ? o!==q.a : o===q.a); G.pick(i); } else if(q.k==='ox'){ G.ox(((q.ok)!==wrong) ? 'o' : 'x'); } else if(q.k==='fix'){ const ts=q.s.split(' '); const i=ts.findIndex(t=> wrong ? t.replace(/[.,!?]/g,'')!==q.bad : t.replace(/[.,!?]/g,'')===q.bad); G.fixTap(i); } else if(q.k==='order'){ q.pickd=q.w.map((w,i)=>i); G.ochk(); } }
                  G.qnext(); await new Promise(r=>setTimeout(r,20)); } }""")
            await pg.wait_for_timeout(500)
            r = await pg.evaluate("()=>({mode:GramUI.mode, rows:document.querySelectorAll('#stGram .grMixR').length, weak:document.querySelectorAll('#stGram .grMixR.weak').length, t:(document.querySelector('#stGram .grEnd')||{}).innerText||''})")
            g1 = await pg.evaluate("()=>Wallet.gems()")
            ok(r["mode"] == "end" and r["rows"] >= 3 and r["weak"] == 1 and "9 / 10" in r["t"].replace("\n", " "), f"{nm} ④ 끝 = 문법별 결과 · 헷갈린 문법 하나 {r['rows']} {r['weak']}")
            ok(g1 - g0 == 2, f"{nm} ④ 하루 첫 번 💎2 ({g1-g0})")
            r = await pg.evaluate("()=>({T:GramUI.mixT.map(t=>t.id), st:GNote.st().s, mx:Gram.list('g34').filter(g=>(Gram.st(g.id)||{}).mx).map(g=>g.id)})")
            ok(len(r["T"]) == 4 and sorted(r["mx"]) == sorted(r["T"]), f"{nm} ④ 섞은 문법 = 방금 함 표시 {r['T']} {r['mx']}")
            ok(any(k in r["st"] for k in ("be", "pl", "s3")), f"{nm} ④ 📒 문법 노트 맞힌 비율에 들어감 {r['st']}")
            left = [x for x in ["g34-1","g34-2","g34-3","g34-6","g34-7"] if x not in r["T"]]
            await pg.screenshot(path=f"{OUT}{nm}_mix_end.png")
            await pg.click("#stGram [data-gr=mix]"); await pg.wait_for_timeout(600)
            ok(await pg.evaluate("()=>GramUI.mode==='quiz' && GramUI.qs.length===10"), f"{nm} ④ 한 번 더 섞기")
            r = await pg.evaluate("()=>GramUI.mixT.map(t=>t.id)")
            ok(all(x in r for x in left), f"{nm} ④ 다음 섞기엔 빠졌던 문법이 먼저 {left} → {r}")
            await pg.evaluate("""async ()=>{ const G=GramUI; let k=0; while(G.mode==='quiz' && k++<40){ const q=G.qs[G.qi]; if(!q.res){ if(q.k==='pick') G.pick(q.opts.indexOf(q.a)); else if(q.k==='ox') G.ox(q.ok?'o':'x'); else if(q.k==='fix'){ const ts=q.s.split(' '); G.fixTap(ts.findIndex(t=>t.replace(/[.,!?]/g,'')===q.bad)); } else { q.pickd=q.w.map((w,i)=>i); G.ochk(); } } G.qnext(); await new Promise(r=>setTimeout(r,20)); } }""")
            ok(await pg.evaluate("()=>Wallet.gems()") == g1, f"{nm} ④ 두 번째는 💎 없음")
            await pg.click("#stGram [data-gnote]"); await pg.wait_for_timeout(600)
            ok(await pg.evaluate("()=>GramUI.mode==='note' && !!document.querySelector('#stGram .grMixB')"), f"{nm} ④ 끝 → 📒 문법 노트")
            # 중등 — 문제에서 만난 문법으로
            await pg.evaluate("()=>{ const v=GNote.st(); ['part','voice','agree'].forEach(k=>v.seen[k]=Date.now()); GNote.put(v); }")
            await pg.evaluate("()=>GramUI.mixStart('mid')"); await pg.wait_for_timeout(1200)
            r = await pg.evaluate("()=>({mode:GramUI.mode, n:GramUI.qs.length, k:[...new Set(GramUI.qs.map(q=>q.gk))].length, s:(GramUI.qs[0]||{}).s})")
            ok(r["mode"] == "quiz" and r["n"] == 10 and r["k"] == 3, f"{nm} ④ 중등 섞어 풀기 (hsq) {r}")
            await pg.screenshot(path=f"{OUT}{nm}_mix_mid.png")
            await pg.evaluate("()=>GramUI.home()"); await pg.wait_for_timeout(400)
            ok(await pg.evaluate("()=>StudyUI._v") == "stPath", f"{nm} ④ 길로 돌아가기")
            e = real_errs(errs); ok(not e, f"{nm} 오류 없음 {e[:3]}")
            await pg.close()
        await b.close()
    print("PASS" if not bad else "FAIL", len(bad))
    if bad: sys.exit(1)

asyncio.run(main())
