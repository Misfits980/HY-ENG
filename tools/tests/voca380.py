"""(v380) 사용자: Daily 30 단모음·단자음 문제가 그 느낌이 안 난다 + 문제 중에 오류가 몇 개 있는 것 같다 (중등·올림피아 문제도)
  ① 단모음: 👂 듣고 모음 고르기(그림·뜻 없이, 보기는 같은 틀의 진짜 단어 모음 먼저) · 모음 소리가 같은 단어 · ★2·3 도 소리 문제가 절반 넘게
  ② 단자음: x 판은 첫 글자 말고 x 자리 · ★2·3 도 첫소리 문제
  ③ 유치원 그림 보기는 쉬운 그림 단어만
  ④ 예문에 쓰인 뜻이 빠진 단어 뜻 더하기(교재 뜻에도) · 그림이 다른 단어 그림 빼기 · 사이트 워드 Stage 이름 · 예문 고침"""
import asyncio, sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

DUMP = r"""([st,LV])=>{ Voice.broken=false; const R=[]; const L=Study.lessons(st);
  L.forEach((x,i)=>{ if(x.fin) return; const s=Study.load(), K=Study.key(st,x.n); s.seen={}; x.ws.forEach(w=>s.seen[w.en]=1); s.lv={}; s.lv[K]=LV; Study.save();
    StudyUI.book=Study.bookOf(st); StudyUI.set=st; StudyUI.start(i,false);
    StudyUI.qs.forEach(q=>{ if(q.t==='intro') return; R.push({stage:Study.stageNo(st,x.n), hl:x.hl, t:q.t, en:q.w&&q.w.en, aud:!!q.aud, pre:q.pre, mid:q.mid, post:q.post, ans:q.ans,
      opts:(q.opts||[]).map(o=>typeof o==='string'?o:[o.en,o.level,o.emoji||'']), x:q.x||null}); }); });
  return R; }"""

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await br.new_page(viewport={"width": 390, "height": 844})
        pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)
        await pg.evaluate("()=>{ Voice.canListen=()=>true; StudyUI.open(); }"); await pg.wait_for_timeout(600)
        # ① 단모음
        S = {lv: await pg.evaluate(DUMP, ["short", lv]) for lv in (1, 2, 3)}
        allq = [q for lv in S for q in S[lv]]
        vh = [q for q in allq if q["t"] == "blend" and q["aud"]]
        sv = [q for q in allq if q["t"] == "svs"]
        ok(len(vh) >= 60 and len(sv) >= 60, f"단모음: 듣고 모음 고르기 {len(vh)} · 모음 소리 같은 단어 {len(sv)}")
        badv = [q for q in vh if q["pre"] + q["mid"] + q["post"] != q["en"] or q["mid"] not in q["opts"] or len(set(q["opts"])) != 3 or any(o not in "aeiou" for o in q["opts"])]
        ok(not badv, f"듣고 모음 고르기: 단어 = 앞+모음+뒤 · 보기 모음 3개 {badv[:2]}")
        mp = await pg.evaluate("""(qs)=>qs.filter(q=>q.opts.filter(v=>v!==q.mid && WORD_BANK.some(w=>w.en===q.pre+v+q.post)).length>=1).length""", vh)
        ok(mp >= len(vh) * 0.4, f"보기 모음이 같은 틀의 진짜 단어(pan·pen·pin)인 문제 {mp}/{len(vh)}")
        V = re.compile(r"^[^aeiou]*([aeiou])[^aeiouy]*$")
        def vow(en, v1): return en[0] if v1 else (V.match(en).group(1) if V.match(en) else None)
        bads = []
        for q in sv:
            v1 = q["x"]["v1"]; wv = vow(q["en"], v1)
            if vow(q["ans"], v1) != wv or q["ans"] not in q["opts"] or q["ans"] == q["en"]: bads.append(q)
            ds = [o for o in q["opts"] if o != q["ans"]]
            if any(vow(d, v1) == wv for d in ds) or len({vow(d, v1) for d in ds}) != 2: bads.append(q)
        ok(not bads, f"모음 소리 같은 단어: 정답만 같은 모음 · 다른 보기 둘은 서로 다른 모음 {[(q['en'],q['opts']) for q in bads[:3]]}")
        for lv in (2, 3):
            qs = S[lv]; sp = sum(1 for q in qs if q["t"] == "spell"); snd = sum(1 for q in qs if q["t"] in ("svs",) or (q["t"] == "blend"))
            ok(sp < len(qs) * 0.45 and snd > len(qs) * 0.5, f"단모음 ★{lv}: 소리 문제 {snd} · 철자 {sp} / {len(qs)}")
        # 그림 문제 보기 = 쉬운 말
        pics = [q for q in allq if q["t"] in ("rpic", "hpic")]
        SW = {q["en"] for q in allq}
        hard = [o for q in pics for o in q["opts"] if isinstance(o, list) and o[0] not in SW and ((o[1] or 0) > 1 or not re.match(r"^[a-z]{2,8}$", o[0]))]
        ok(not hard, f"단모음 그림 보기에 어려운 말 없음 {hard[:4]}")
        # 화면: 듣고 모음 고르기 — 그림·뜻 숨김
        r = await pg.evaluate("""()=>{ const i=StudyUI.qs.findIndex(q=>q.t==='blend' && q.aud); if(i<0) return null; StudyUI.i=i; StudyUI.show(); const d=document.getElementById('stQ');
            return {kind:d.querySelector('.stKind').innerText, pic:!!d.querySelector('.stPic'), ko:!!d.querySelector('.stKo'), big:!!d.querySelector('.stBig'), slot:!!d.querySelector('.bdT.slot'), n:d.querySelectorAll('.stOpt').length}; }""")
        print("vhear view", r)
        ok(r and "듣고" in r["kind"] and not r["pic"] and not r["ko"] and r["big"] and r["slot"] and r["n"] == 3, f"👂 듣고 모음 고르기 화면: 소리만 · 빈칸 · 보기 3 {r}")
        r = await pg.evaluate("""()=>{ const i=StudyUI.qs.findIndex(q=>q.t==='blend' && q.aud); StudyUI.i=i; StudyUI.show(); const q=StudyUI.qs[i]; StudyUI.sel=q.opts.indexOf(q.mid); StudyUI.check();
            return [...document.querySelectorAll('#stQ .stOpt')].map(x=>x.className); }""")
        ok(any("ok" in c.split() for c in r), f"정답을 누르면 맞음 {r}")
        r = await pg.evaluate("""()=>{ const s=Study.load(); s.lv={}; Study.save(); const L=Study.lessons('short'); const i=L.findIndex(x=>!x.fin && x.hl==='a'); const K=Study.key('short',L[i].n); s.seen={}; L[i].ws.forEach(w=>s.seen[w.en]=1); s.lv[K]=2; Study.save();
            StudyUI.set='short'; StudyUI.start(i,false); const j=StudyUI.qs.findIndex(q=>q.t==='svs'); if(j<0) return null; StudyUI.i=j; StudyUI.show(); const d=document.getElementById('stQ'), q=StudyUI.qs[j];
            return {kind:d.querySelector('.stKind').innerText, u:(d.querySelector('.stEn u')||{}).innerText, n:d.querySelectorAll('.stOpt').length, v:q.x.v}; }""")
        print("svs view", r)
        ok(r and "가운데 소리" in r["kind"] and r["u"] == r["v"] and r["n"] == 3, f"모음 소리 같은 단어 화면 (모음에 밑줄) {r}")
        # 이어 하기로 저장했다 다시 열어도 그대로
        r = await pg.evaluate("""()=>{ const j=StudyUI.qs.findIndex(q=>q.t==='blend' && q.aud); if(j<0) return 'none'; StudyUI.i=j; StudyUI.saveCur(); const a=StudyUI.qs[j]; StudyUI.qs=[]; StudyUI.resume(); const b=StudyUI.qs[j]; return [b.t, !!b.aud, b.mid===a.mid, b.pre===a.pre]; }""")
        ok(r == ["blend", True, True, True], f"이어 하기: 듣고 모음 고르기 그대로 {r}")
        # ② 단자음
        A = {lv: await pg.evaluate(DUMP, ["abc", lv]) for lv in (1, 2, 3)}
        x = [q for lv in A for q in A[lv] if q["hl"] == "c1x" and "x" in q["en"][1:]]
        xf = [q for q in x if q["t"] == "first"]
        xb = [q for q in x if q["t"] == "blend"]
        ok(not xf and xb and all(q["mid"] == "x" and set(q["opts"]) <= {"x", "s", "k", "z"} for q in xb), f"x 판: 첫 글자 문제 없음 · x 자리 문제 {len(xb)} {[(q['en'],q['t']) for q in xf[:3]]}")
        for lv in (2, 3):
            qs = A[lv]; sp = sum(1 for q in qs if q["t"] == "spell")
            ok(sp < len(qs) * 0.5, f"단자음 ★{lv}: 철자 쓰기 {sp}/{len(qs)} (첫소리 문제가 더 많음)")
        # ③ 유치원 그림 보기
        K = await pg.evaluate(DUMP, ["kinder", 2])
        hk = [q for q in K if q["t"] in ("rpic", "hpic")]
        hard = [o[0] for q in hk for o in q["opts"] if isinstance(o, list) and o[0] != q["en"] and not re.match(r"^[a-z]{2,8}$", o[0])]
        ok(hk and not hard, f"유치원 그림 보기 {len(hk)}문제: 띄어쓰기·긴 단어 없음 {hard[:4]}")
        # ④ 뜻 · 그림 · 이름 · 예문
        r = await pg.evaluate("""()=>{ const b=en=>(WORD_BANK.find(w=>w.en===en)||{}); return {goal:b('goal').ko, inst:b('instrument').ko, rel:b('relative').ko, aunt:b('aunt').ko, held:b('held').ko,
            eraser:b('eraser').emoji||null, towel:b('towel').emoji||null, short:b('short').emoji||null, lot:b('lot').emoji||null, sweater:b('sweater').emoji||null, cat:b('cat').emoji};
          }""")
        print(r)
        ok(r["goal"] == "골, 목표" and "악기" in r["inst"] and "상대적인" in r["rel"] and r["aunt"] == "이모, 고모" and r["held"].count("잡고") == 1, f"빠진 뜻 더하기 (같은 뜻 두 번 안 붙임) {r}")
        ok(not any(r[k] for k in ("eraser", "towel", "short", "lot", "sweater")) and r["cat"], "그림이 다른 단어 그림 빼기")
        r = await pg.evaluate("""()=>{ const out=[]; Study.SETS.forEach(st=>{ let L=[]; try{ L=Study.lessons(st); }catch(e){} L.forEach(x=>x.ws.forEach(w=>{ if(w.en==='order' || w.en==='goal') out.push(w.ko); })); }); return [...new Set(out)]; }""")
        ok(r and all("순서" in k or "목표" in k for k in r), f"교재 뜻(과마다 다른 뜻)에도 빠진 뜻 더하기 {r}")
        r = await pg.evaluate("()=>JSON.stringify(PH_WORLDS.sight)")
        ok("했어요 · 해요" in r and '"말하기"' not in r and '"어디?"' not in r, "사이트 워드 Stage 이름이 단어와 맞음")
        for f, has, no in [("data/dex2.json", "한국을 대표하는 운동", "한국의 국기라서"), ("data/bex.json", "Please save the file", "walk in single file"),
                           ("data/dex3.json", "A cactus can tolerate", "\"Cactus can tolerate"), ("data/mid.json", "My phone broke, so I got a replacement", "replacement teacher taught")]:
            t = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", f), encoding="utf-8").read()
            ok(has in t and no not in t, f"예문 고침 {f}")
        e = real_errs(errs); ok(not e, "오류 없음 " + str(e[:3]))
        await br.close()
    print("결과:", "통과" if not bad else "실패 " + str(bad))
asyncio.run(main())
