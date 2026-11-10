# v650 Daily 30 — ① 며칠 뒤 첫 번 정답률 · ② 초3 이상 꺼내기(첫 글자만 주고 쓰기) · ③ 내가 고른 것 뜻 + 🔀 헷갈리는 짝 · ④ 🎤 따라 말하기 · ⑤ 선생님 화면
import asyncio, sys, os, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *

OUT = os.environ.get("HY_OUT", "/tmp/d650_")
bad = []
def ok(c, m):
    print(("OK  " if c else "BAD ") + m)
    if not c: bad.append(m)

MIC = """window.__heard='apple'; window.webkitSpeechRecognition=window.SpeechRecognition=class { start(){ window.__micN=(window.__micN|0)+1; setTimeout(()=>{ if(window.__heard==='__deny') this.onerror({error:'not-allowed'}); else if(window.__heard==='') this.onerror({error:'no-speech'}); else this.onresult({results:[[{transcript:window.__heard},{transcript:'zzz'}]]}); }, 60); } abort(){} };"""

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True); await ctx.add_init_script(MIC)
        pg = await ctx.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        await boot(pg)
        await pg.evaluate("()=>{ Online.on=()=>true; window.__sub=[]; Online.submit=r=>{ window.__sub.push(r); return Promise.resolve({ok:true}); }; }")
        G34 = await pg.evaluate("()=>Study.BOOKS.g34.sets[0]"); G12 = await pg.evaluate("()=>Study.BOOKS.g12.sets[0]")
        # ① 며칠 뒤 첫 번
        r = await pg.evaluate("""(set)=>{ const S=Study.load(), t=Study.today(), ws=Study.lessons(set)[0].ws.filter(w=>/^[a-z]{3,9}$/.test(w.en)).slice(0,6).map(w=>w.en); S.srs={}; S.rt={}; S.rw={}; S.rtd={};
            S.srs[ws[0]]=[1,t]; S.srs[ws[1]]=[4,t-1]; S.srs[ws[2]]=[6,t]; S.srs[ws[3]]=[2,t+3]; Study.save();
            const a=Study.ret(ws[0],true), a2=Study.ret(ws[0],false), b=Study.ret(ws[1],false), c=Study.ret(ws[2],true), d=Study.ret(ws[3],true), e=Study.ret(ws[4],true);
            return {a, a2, b, c, d, e, sum:Study.retSum(14), st:Study.sticky(), ws}; }""", G34)
        ok(r["a"] and r["a"]["b"] == "1" and r["a2"] is None and r["b"]["b"] == "4" and r["c"]["b"] == "15" and r["d"] is None and r["e"] is None, f"복습 날이 된 단어의 그날 첫 번만 적음 · 칸 1/4/15 {r['a']} {r['b']} {r['c']}")
        ok(r["sum"]["all"] == [2, 3] and r["sum"]["4"] == [0, 1], f"모음 {r['sum']}")
        ws = r["ws"]
        r = await pg.evaluate("""(w)=>{ const S=Study.load(); Study._day(1); S.srs[w]=[1,Study.today()]; Study.save(); Study.ret(w,false); const st=Study.sticky().slice(); Study._day(2); S.srs[w]=[1,Study.today()]; Study.save(); Study.ret(w,true); const st2=Study.sticky().slice(); Study._day(0); return [st, st2]; }""", ws[1])
        ok(r[0] == [ws[1]] and r[1] == [], f"며칠 뒤 두 번 틀리면 안 붙는 단어 · 맞히면 빠짐 {r}")
        # ② 꺼내기 사다리 (초3 이상만)
        r = await pg.evaluate("""([hi, lo])=>{ const out={}; [hi, lo].forEach(set=>{ const S=Study.load(), t=Study.today(); S.srs={}; S.set=set; Study.save(); Study.ctx(set);
              const W=Study.lessons(set).slice(0,3).reduce((a,x)=>a.concat(x.ws),[]).filter(w=>/^[a-z]{3,9}$/.test(w.en)).slice(0,10); const o={};
              [1,3,5].forEach(L=>{ W.forEach(w=>{ S.srs[w.en]=[L,t]; }); Study.save(); const T={}; for(let k=0;k<12;k++){ const qs=Study.buildReview(set)||[]; qs.slice(0,10).forEach(q=>{ const key=q.t==='kdict' ? (q.kk&&q.fl?'kk':'kdict') : q.t; T[key]=(T[key]|0)+1; }); } o[L]=T; }); out[set]=o; }); return out; }""", [G34, G12])
        H, L = r[G34], r[G12]
        ok(not H["1"].get("e2k") and not H["1"].get("pic") and H["1"].get("k2e", 0) > 0, f"G3-4 1칸: 뜻 고르기(알아보기) 없이 한글→영어·듣기·빈칸 {H['1']}")
        ok(not H["3"].get("e2k") and (H["3"].get("spell", 0) + H["3"].get("dict", 0)) > 40, f"G3-4 3칸: 철자·받아쓰기 위주 {H['3']}")
        ok(H["5"].get("kk", 0) > 40 and not H["5"].get("e2k") and not H["5"].get("k2e"), f"G3-4 5칸: 보기 없이 뜻 보고 쓰기 {H['5']}")
        ok(not L["5"].get("kk") and not L["3"].get("kk") and not L["1"].get("kk"), f"G1-2 는 그대로 (직접 쓰기 없음) {L['5']}")
        # ② 화면: 첫 글자만 주고 쓰기 → 풀기 · ① 기록이 서버로
        await pg.evaluate("""(set)=>{ const S=Study.load(), t=Study.today(); S.srs={}; S.rt={}; S.rw={}; S.rtd={}; S.set=set; Study.lessons(set).slice(0,2).reduce((a,x)=>a.concat(x.ws),[]).filter(w=>/^[a-z]{3,8}$/.test(w.en)).slice(0,6).forEach(w=>{ S.srs[w.en]=[5,t]; }); Study.save(); StudyUI.set=set; StudyUI.book='g34'; StudyUI.open(); StudyUI.review(); }""", G34)
        await pg.wait_for_timeout(500)
        seenkk = False; n = 0; wrong_one = None
        for _ in range(120):
            st = await pg.evaluate("()=>{ const U=StudyUI, q=U.qs[U.i]; return q ? {t:q.t, kk:q.kk, fl:q.fl, got:q.got, en:q.w.en, locked:U.locked, view:document.getElementById('stDone').style.display} : null; }")
            if not st or st["view"] not in ("none", ""): break
            if st["t"] == "kdict" and st["fl"] and not st["locked"] and not seenkk:
                seenkk = True; r = await pg.evaluate("()=>[StudyUI.qs[StudyUI.i].got, document.getElementById('stSlots').textContent, document.querySelector('#stQ .stKind').textContent, document.querySelectorAll('#stQ .stOpt').length]")
                ok(r[0] == st["en"][0] and r[1].strip() == st["en"][0] and "첫 글자" in r[2] and r[3] == 0, f"보기 없이 · 첫 글자만 {r}")
                await pg.screenshot(path=OUT + "kk_ph.png")
                fit = await pg.evaluate("()=>{ const S=document.getElementById('scStudy'); return [S.scrollHeight-S.clientHeight, Math.round(document.getElementById('stCheck').getBoundingClientRect().bottom), innerHeight]; }")
                ok(fit[0] <= 1 and fit[1] <= fit[2], f"쓰기 화면 스크롤 없음 {fit}")
                if wrong_one is None:   # 한 번은 틀리게
                    wrong_one = st["en"]; await pg.evaluate("()=>{ document.querySelector('.kdK[data-kk=\"z\"]').click(); document.getElementById('stCheck').click(); }"); await pg.wait_for_timeout(120); continue
            await pg.evaluate(SOLVE, False); await pg.wait_for_timeout(60); n += 1
        ok(seenkk, "복습에 첫 글자 쓰기 문제가 나옴")
        await pg.wait_for_timeout(600)
        sub = await pg.evaluate("()=>window.__sub.filter(r=>r.rule==='study-review').slice(-1)[0]||null")
        ok(sub and sub.get("rvn") == 6 and sub.get("rvo") == 5 and sub.get("rvw") == wrong_one, f"기록: 며칠 뒤 푼 수 6 · 맞힘 5 · 틀린 단어 {sub and [sub.get('rvo'), sub.get('rvn'), sub.get('rvw')]} ({wrong_one})")
        r = await pg.evaluate("()=>Study.retSum(14)"); ok(r["15"] == [5, 6], f"기기에도 쌓임 {r}")
        # ③ 내가 고른 것 뜻 + 🔀 헷갈리는 짝 · ④ 🎤
        await pg.evaluate("""(set)=>{ const S=Study.load(); S.srs={}; S.seen={}; S.lv={}; S.cp={}; S.wuSkip=Study.today(); Study.save(); StudyUI.set=set; StudyUI.book='g34'; StudyUI.open(); StudyUI.start(0,false); }""", G34)
        await pg.wait_for_timeout(600)
        mic = None; pk = None
        for _ in range(200):
            st = await pg.evaluate("()=>{ const U=StudyUI, q=U.qs[U.i]; return q ? {t:q.t, hd:q.hd||'', card:q.card, locked:U.locked, again:!!q.again, objs:!!q.mine, en:q.w.en} : null; }")
            if not st: break
            if st["t"] == "intro" and st["card"] and mic is None:
                mic = await pg.evaluate("()=>!!document.querySelector('#stQ .stMic')"); ok(mic, "새 단어 카드에 🎤 따라 말하기")
                await pg.evaluate("(en)=>{ window.__heard=en; }", st["en"]); await pg.click("#stQ .stMic"); await pg.wait_for_timeout(250)
                r = await pg.evaluate("()=>[document.querySelector('#stQ .stMicR').textContent, Object.keys(StudyUI.spW||{}), StudyUI.i]"); ok("잘 말했어요" in r[0] and r[1] == [st["en"]], f"맞게 말하면 👍 {r}")
                await pg.screenshot(path=OUT + "mic_ph.png")
                await pg.evaluate("()=>{ window.__heard='banana split'; }"); await pg.click("#stQ .stMic"); await pg.wait_for_timeout(250)
                r = await pg.evaluate("()=>document.querySelector('#stQ .stMicR').textContent"); ok("처럼 들렸어요" in r, f"다르게 들리면 다시 (점수 없음) {r}")
                await pg.evaluate("()=>{ window.__heard=''; }"); await pg.click("#stQ .stMic"); await pg.wait_for_timeout(250)
                r = await pg.evaluate("()=>document.querySelector('#stQ .stMicR').textContent"); ok("안 들렸어요" in r, f"조용하면 안내 {r}")
                fit = await pg.evaluate("()=>{ const S=document.getElementById('scStudy'); return [S.scrollHeight-S.clientHeight]; }"); ok(fit[0] <= 1, f"카드 스크롤 없음 {fit}")
                await pg.evaluate("()=>{ const U=StudyUI, W=U.les.ws.slice(0,4); U.qs.splice(U.i+1, 0, {t:'e2k', w:W[0], opts:[W[1],W[0],W[2],W[3]], step:1, mine:1}); }")
            if st["t"] in ("e2k", "k2e") and st["objs"] and not st["locked"] and not st["again"] and pk is None:
                pk = await pg.evaluate("""()=>{ const U=StudyUI, q=U.qs[U.i]; q.opts.forEach(o=>{ if(o.en!==q.w.en) Study.cfPair(q.w.en, o.en); }); let o=null;
                    for(let k=0;k<q.opts.length && !U.locked;k++){ if(q.opts[k].en===q.w.en) continue; const b=document.querySelector('#stQ .stOpt[data-k="'+k+'"]'); if(b.disabled || b.classList.contains('bad')) continue; o=q.opts[k]; b.click(); }
                    return {a:q.w.en, b:o.en, ko:o.ko, locked:U.locked}; }""")
                await pg.wait_for_timeout(150)
                r = await pg.evaluate("()=>[(document.querySelector('#stFoot .stPk')||{}).textContent||'', (StudyUI.qs[StudyUI.i+1]||{}).hd, !!(StudyUI.qs[StudyUI.i+2]||{}).retry, !!(StudyUI.qs[StudyUI.i+3]||{}).cmp, StudyUI.first, StudyUI.done]")
                ok(pk["b"] in r[0] and pk["ko"] in r[0], f"틀리면 내가 고른 단어의 뜻 한 줄 「{r[0]}」")
                ok(r[1] == "cmp" and r[2] and r[3], f"같은 짝을 두 번 바꿔 고름 → 🔀 카드 · 한 번 더 · 둘 중 고르기 {r}")
                await pg.screenshot(path=OUT + "why_ph.png"); f0 = r[4:]
                await pg.click("#stCheck"); await pg.wait_for_timeout(250)
                r = await pg.evaluate("()=>[document.querySelector('#stQ .stKind').textContent, document.querySelectorAll('#stQ .stCards.cmp .stMini').length, document.getElementById('scStudy').scrollHeight-document.getElementById('scStudy').clientHeight]")
                ok("헷갈리는 짝" in r[0] and r[1] == 2 and r[2] <= 1, f"🔀 카드 두 단어 나란히 {r}"); await pg.screenshot(path=OUT + "cmp_ph.png")
                await pg.click("#stCheck"); await pg.wait_for_timeout(200); await pg.evaluate(SOLVE, False); await pg.wait_for_timeout(200); await pg.evaluate(SOLVE, False); await pg.wait_for_timeout(250)
                r = await pg.evaluate("()=>{ const q=StudyUI.qs[StudyUI.i]; return [q.cmp, q.w.en, q.opts.length, document.querySelector('#stQ .stStep').textContent]; }")
                ok(r[0] == 1 and r[1] == pk["b"] and r[2] == 2 and "헷갈리는" in r[3], f"둘 중 고르기 (고른 쪽 단어) {r}")
                await pg.evaluate(SOLVE, False); await pg.wait_for_timeout(200)
                r = await pg.evaluate("()=>[StudyUI.first, StudyUI.done, !!(StudyUI._sp||{})['"+pk["b"]+"']]"); ok(r[:2] == f0 and not r[2], f"짝 문제는 점수·진도·본 단어에 안 들어감 {r} {f0}")
                break
            await pg.evaluate(SOLVE, False); await pg.wait_for_timeout(60)
        ok(mic is not None and pk is not None, f"카드·고르기 문제를 만남 {mic} {bool(pk)}")
        # ④ 마이크 거절 · 끄기 · 없는 기기
        await pg.evaluate("()=>{ window.__heard='__deny'; StudyUI.qs.splice(StudyUI.i+1, 0, {t:'intro', w:StudyUI.qs[StudyUI.i].w, ws:[StudyUI.qs[StudyUI.i].w], card:1}); StudyUI.locked=false; StudyUI.next(); }"); await pg.wait_for_timeout(300)
        if await pg.evaluate("()=>!!document.querySelector('#stQ .stMic')"):
            await pg.click("#stQ .stMic"); await pg.wait_for_timeout(250)
        r = await pg.evaluate("()=>[!!document.querySelector('#stQ .stMic'), Speak.ok()]"); ok(r == [False, False], f"마이크 거절 → 단추 사라짐 · 공부는 그대로 {r}")
        r = await pg.evaluate("()=>{ Speak.dead=false; localStorage.setItem('hyeng_mic_off','1'); const a=Speak.ok(); localStorage.removeItem('hyeng_mic_off'); const R=Speak.R; Speak.R=null; const b=Speak.ok(); Speak.R=R; return [a,b, Speak.match('through',['threw']), Speak.match('cat',['the cat']), Speak.match('cat',['cut']), Speak.match('beautiful',['beautifull'])]; }")
        ok(r == [False, False, False, True, False, True], f"끄기 · 인식 없는 기기 = 안 보임 · 비슷함 판정 {r}")
        e = real_errs(errs); ok(not e, f"오류 없음 {e[:3]}")
        await ctx.close()
        # ⑤ 선생님 화면 (세로·가로 패드)
        REP = {"at": 0, "d": {"nicks": [], "learn": {"days": 14, "kids": [{"n": "민준", "ok": 9, "tot": 20, "sp": 3, "w": [["quite", 3], ["through", 2]]}, {"n": "서연", "ok": 18, "tot": 20, "sp": 12, "w": []}],
                                           "words": [["quite", 2, 4], ["through", 1, 2]]}}}
        for nm, vp in (("pad", (820, 1180)), ("padL", (1180, 820))):
            ctx = await b.new_context(viewport={"width": vp[0], "height": vp[1]}, is_mobile=True, has_touch=True); T = await ctx.new_page(); await boot(T)
            await T.evaluate("(r)=>{ r.at=Date.now(); localStorage.setItem('hyeng_admin_rep', JSON.stringify(r)); sessionStorage.setItem('hyeng_admin_ok',String(Date.now())); sessionStorage.setItem('hyeng_admin_tk','testkey'); }", REP)
            await T.reload(); await T.wait_for_timeout(1500)
            await T.evaluate("(R)=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); Online.on=()=>true; Notice.fetch=()=>Promise.resolve({v:3, notices:[]}); Online.submit=o=>Promise.resolve(o.type==='report' ? {ok:true, rep:R.d} : {ok:true}); document.querySelectorAll('.sheet.on').forEach(s=>s.classList.remove('on')); Admin.open(); }", REP)
            await T.wait_for_timeout(500); await T.click('#adTabs [data-t="rec"]'); await T.wait_for_timeout(800)
            await T.evaluate("()=>{ document.querySelectorAll('#adBody details').forEach(d=>{ if(/며칠 뒤/.test(d.textContent)) d.open=true; }); const el=[...document.querySelectorAll('#adBody *')].find(x=>/며칠 뒤에도 기억하나/.test(x.textContent) && x.children.length<4); if(el) el.scrollIntoView({block:'start'}); }")
            t = await T.evaluate("()=>document.getElementById('adBody').innerText")
            ok("며칠 뒤에도 기억하나" in t and "68%" in t and "45%" in t and "quite" in t and "민준" in t, f"{nm}: 🧠 카드 — 반 68% · 민준 45% · 안 붙는 단어")
            r = await T.evaluate("()=>{ const b=document.getElementById('adBody'); return b.scrollWidth-b.clientWidth; }"); ok(r <= 1, f"{nm}: 가로 넘침 없음 {r}")
            await T.screenshot(path=f"{OUT}admin_{nm}.png"); await ctx.close()
        await b.close()
    g = subprocess.run(["node", os.path.join(os.path.dirname(os.path.abspath(__file__)), "gs_learn650.js")], capture_output=True, text=True)
    print(g.stdout.strip()); ok(g.returncode == 0, "Code.gs v19 (gs_learn650.js)")
    print("PASS" if not bad else "FAIL", len(bad))
    if bad: sys.exit(1)

asyncio.run(main())
