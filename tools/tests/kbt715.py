# v715 🏫 교실 배틀 「시험처럼」 유치부 — 사용자 사진 2장: ① 「유치부 애들이 문장 풀 수 있어? 뜻 없이?」 (C 대화 빈칸) ② 「그림이 없는데?」 (A 그림에 맞는 영어 — 그림 칸이 비었음)
# ① 유치부 책(bookOf k) = 그림 보고 단어 · 🔊 듣고 단어 · 뜻 보고 단어 (문장·대화 없음) — 초등은 그대로
# ② 그림 문제는 칸이 모자라도 그림을 숨기지 않음 (패드 = 위 띠를 낮추고 · 그래도 모자라면 그림을 작게)
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
bad = []
def ok(c, m):
    print(("OK  " if c else "BAD ") + m, flush=True)
    if not c: bad.append(m)
KIDQ = """(sets)=>{ const out={n:0, t:{}, ab:{}, bad:[], code:[], err:[], noPic:[]};
  Battle.role='kid'; Battle.room='9999'; Battle.me='k1'; Battle.pick={id:'k1', n:'K1'}; Battle.h=null; Battle.screen();
  sets.forEach(set=>{ let L=[]; try{ L=Study.lessons(set); }catch(e){ return; }
    for(let a=0;a<L.length;a+=4){ Battle._ws=null; Battle._eq=null; Battle.q=null; Battle._last={cfg:{set, from:a, to:Math.min(L.length-1,a+5), qt:['mean'], lvl:'exam', dur:300}, st:{s:'run', t0:Date.now()-1000}, p:{}};
      for(let r=0;r<10;r++){ let q; try{ q=Battle.mkQ(); }catch(e){ out.err.push([set,String(e)]); break; } if(!q.exq) continue; out.n++; out.t[q.t]=(out.t[q.t]||0)+1; if(q.ab) out.ab[q.ab]=(out.ab[q.ab]||0)+1;
        if(!q.opts.some(o=>o.en===q.w.en)) out.bad.push([set,q.t,q.w.en]);
        if(q.t==='opic' && !q.w.emoji) out.noPic.push([set,q.w.en]);
        if(r<3){ Battle.q=q; Battle.qAt=Date.now(); Battle.draw(); const tx=document.getElementById('rdIn').innerText; if(/<img|undefined|null/.test(tx)) out.code.push([set,q.t,q.w.en]); } } } });
  Battle.q=null; return out; }"""
SETQ = """(t)=>{ const q0=Battle.q; if(!q0) return 'noq'; const W=e=>WORD_BANK.find(x=>x.en===e), w=W(t==='k2e'?'bed':'red');
  Battle.q=Object.assign({}, q0, {t, w, ab:t==='opic'?'A':t==='listen'?'B':'C', opts:[w, W('igloo'), W('snow'), W('bread')], exq:1, sec:9, done:0, pick:null, ok:null, ans:null, lab:null, zap:false, tk:null, st:null, sts:null, opic:0, _said:0});
  Battle.qAt=Battle.now(); Battle.lockTo=0; document.getElementById('rdB')._pf=null; Battle.draw(); return 'ok'; }"""
MEAS = """()=>{ const S=document.getElementById('scRaid'), Q=S.querySelector('.rdQ'), P=S.querySelector('.rdPr'), O=[...S.querySelectorAll('.rdOpts .stOpt')].map(b=>b.getBoundingClientRect()), pic=S.querySelector('.rdPr .btPic'), st=document.getElementById('btStrip');
  const r=pic ? pic.getBoundingClientRect() : null, q=Q.getBoundingClientRect(), pb=parseFloat(getComputedStyle(Q).paddingBottom)||0, oTop=Math.min(...O.map(x=>x.top)), land=innerWidth>innerHeight;
  return {pad:S.classList.contains('btPad'), tight:S.classList.contains('btTight'), pic:!!pic, vis:!!pic && getComputedStyle(pic).display!=='none' && r.height>0, h:r ? Math.round(r.height) : 0, lap:!!r && !land && r.bottom>oTop+1, cut:Math.max(...O.map(x=>x.bottom))>q.bottom-pb+2, optH:Math.round(Math.min(...O.map(x=>x.height))), over:S.scrollHeight-S.clientHeight, strip:st ? Math.round(st.getBoundingClientRect().height) : 0, kq:(S.querySelector('.rdQK')||{}).innerText||'', lsn:!!S.querySelector('.rdPr .btLsn')}; }"""
async def join(ctx, room, nm, vp, i):
    k = await ctx.new_page(); await k.set_viewport_size({"width": vp[0], "height": vp[1]}); await boot(k)
    await k.evaluate(f"()=>{{ const k0=Kid.k.bind(Kid); Kid.k=b=>k0(b)+'@t{i}'; RaidJoin.open(); }}"); await k.wait_for_timeout(100)
    await k.evaluate(f"()=>{{ document.getElementById('rdRoomIn').value='{room}'; document.getElementById('rdNameIn').value='{nm}'; document.querySelector('[data-rj=go]').click(); }}"); await k.wait_for_timeout(450); return k
async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(); errs = []
        ctx = await br.new_context(viewport={"width": 1280, "height": 900}, service_workers="block"); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        K = await ctx.new_page(); K.on("pageerror", lambda e: errs.append("K " + str(e)[:200])); await boot(K)
        await K.evaluate("()=>HyExam.ready()")
        # ① 유치부 책 — 문장·대화 없음
        ks = await K.evaluate("()=>Study.BOOKS.k ? Study.BOOKS.k.sets.slice() : Object.keys(WORD_SETS).filter(s=>Study.bookOf(s)==='k')")
        r = await K.evaluate(KIDQ, ks)
        print("유치부", ks, r["n"], r["t"], r["ab"], r["bad"][:3], r["code"][:3], r["err"][:2], r["noPic"][:3])
        ok(r["n"] > 60 and not r["err"] and not r["bad"] and not r["code"] and not r["noPic"], f"① 유치부 시험처럼 {r['n']}문제: 정답 없음 {len(r['bad'])} · 코드 글 {len(r['code'])} · 그림 없는 그림 문제 {len(r['noPic'])} · 오류 {len(r['err'])}")
        ok(not any(r["t"].get(t) for t in ("talk", "sent", "sent2", "def")), f"① 유치부: 대화·문장 빈칸 문제 0개 {r['t']}")
        ok(all(r["t"].get(t, 0) > 0 for t in ("opic", "listen", "k2e")) and set(r["ab"]) == {"A", "B", "C"}, f"① 유치부: 🖼️ 그림 · 🔊 듣기 · 🔤 뜻 다 나옴 {r['t']} {r['ab']}")
        r2 = await K.evaluate(KIDQ, ["elem", "g56"])
        ok(r2["t"].get("talk", 0) + r2["t"].get("sent", 0) + r2["t"].get("sent2", 0) > 0 and not r2["t"].get("listen"), f"① 초등(G3-4·G5-6)은 그대로 문장 문제 있음 · 듣기 없음 {r2['t']}")
        # 소리가 안 나는 기기 — 듣기 문제 없음 (그림·뜻만)
        r3 = await K.evaluate("(sets)=>{ const c0=Voice.canListen; Voice.canListen=()=>false; try{ return (%s)(sets); } finally { Voice.canListen=c0; } }" % KIDQ, ["short"])
        ok(r3["n"] > 10 and not r3["t"].get("listen") and not any(r3["t"].get(t) for t in ("talk", "sent", "sent2")), f"① 소리 안 나는 기기: 듣기 문제 없이 그림·뜻만 {r3['t']}")
        # 선생님 📝 시험(같은 문제 틀)도 유치부는 문장 없음
        e = await K.evaluate("""()=>{ const qs=Study.buildExam({set:'short', from:0, to:14}); const t={}; qs.slice(1).forEach(q=>{ t[q.t]=(t[q.t]||0)+1; });
            return {P:qs[0].P, t, prof:Study.olyProf('short'), g12:Study.olyProf(Study.BOOKS.g12 ? Study.BOOKS.g12.sets[0] : 'elem'), nm:HyExam.P_NM.k, tt:HyExam.timeTbl("k")}; }""")
        ok(e["P"] == "k" and e["prof"] == "k" and not any(e["t"].get(t) for t in ("talk", "sent", "sent2")) and e["t"].get("opic", 0) > 0 and "유치부" in (e["nm"] or "") and "듣기" in e["tt"], f"① 📝 선생님 시험(유치원 단모음): 단계 유치부 · 문장 없음 {e}")
        # ② 패드 화면 — 그림 칸
        await ctx.close()
        ctx = await br.new_context(viewport={"width": 1920, "height": 1080}, service_workers="block"); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        H = await ctx.new_page(); H.on("pageerror", lambda e: errs.append("H " + str(e)[:200])); await boot(H)
        room = await H.evaluate("()=>Battle.host({set:'short', from:0, to:14, dur:300, mode:'score', qt:['mean'], lvl:'exam', team:false, lbl:'유치원 단모음 Stage 1-1~3-4'})")
        VP = [("세로 옛 아이패드(주소창)", (768, 900)), ("세로 아이패드", (768, 1004)), ("세로 아이패드 미니", (744, 1050)), ("가로 아이패드", (1024, 704)), ("세로 큰 패드", (820, 1180))]
        P = [await join(ctx, room, "패드%d" % i, vp, i) for i, (nm, vp) in enumerate(VP)]
        F = [await join(ctx, room, "친구%d" % i, (390, 844), 10 + i) for i in range(3)]
        for k in P + F: k.on("pageerror", lambda e: errs.append("K " + str(e)[:200]))
        await H.evaluate("()=>Battle.hostAct('start')"); await H.wait_for_function("()=>Battle.st().s==='run' && Battle.left()>0", timeout=12000); await H.wait_for_timeout(1200)
        for k in F:   # 친구 점수 → 순위 두 칸 (사진처럼 순위 칸이 큼)
            for _ in range(3):
                await k.evaluate("()=>{ const q=Battle.q; if(!q||q.done) return; const i=q.ans!=null?q.ans:q.opts.findIndex(o=>o.en===q.w.en); Battle.lockTo=0; Battle.qAt=0; Battle.answer(i); }"); await k.wait_for_timeout(450)
        await asyncio.sleep(1.2)
        for (nm, vp), k in zip(VP, P):
            await k.evaluate("()=>{ window.__said=[]; DexDet.say=e=>{ window.__said.push(e); }; }")
            s0 = (await k.evaluate(MEAS))["strip"]
            await k.evaluate(SETQ, "opic"); await k.wait_for_timeout(350); m = await k.evaluate(MEAS)
            small = vp[1] < 860
            ok(m["pad"] and m["vis"] and m["h"] >= (50 if small else 90) and not m["lap"] and not m["cut"] and m["over"] <= 1 and m["optH"] >= 52, f"② {nm} A 그림 문제: 그림 보임 {m['h']}px · 보기와 안 겹침 · 스크롤 없음 {m}")
            if nm.startswith("세로 옛"): await k.screenshot(path=OUT + "kbt715_pic.png")
            await k.evaluate(SETQ, "k2e"); await k.wait_for_timeout(300); m2 = await k.evaluate(MEAS)
            ok(m2["tight"] == m["tight"] and m2["over"] <= 1 and not m2["cut"], f"② {nm}: 다음 문제에서 위 띠가 오르내리지 않음 ({s0}→{m['strip']}→{m2['strip']}px) {m2['tight']}")
            await k.evaluate(SETQ, "listen"); await k.wait_for_timeout(300); m3 = await k.evaluate(MEAS); said = await k.evaluate("()=>window.__said.slice()")
            ok(m3["lsn"] and "듣고" in m3["kq"] and said == ["red"] and not m3["cut"] and m3["over"] <= 1, f"② {nm} B 듣기 문제: 🔊 단추 · 바로 소리 {said} · {m3['kq']}")
            if nm.startswith("세로 옛"): await k.screenshot(path=OUT + "kbt715_listen.png")
        # 휴대폰도 그림은 안 숨김
        await F[0].evaluate(SETQ, "opic"); await F[0].wait_for_timeout(300); m = await F[0].evaluate(MEAS)
        ok(m["vis"] and m["h"] >= 40 and m["over"] <= 1, f"② 휴대폰 A 그림 문제: 그림 보임 {m['h']}px {m}")
        ok(not errs, f"오류 없음 {errs[:3]}")
        await br.close()
    print("\n== 결과:", "모두 통과" if not bad else f"{len(bad)}개 실패")
    sys.exit(1 if bad else 0)
asyncio.run(main())
