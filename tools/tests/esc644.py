# v644 🔐 영어 방탈출 3.0 — 테마 · 방마다 퍼즐 3개 동시 · 아이템(게이트) · 📜 쪽지 합치기 · 🔌🎛🎹 기계 · 🚀 마지막 장치 · 퍼즐별 잠김 · 귀띔 · ⭐ 별 · 시간 넘김 · 5화면
import asyncio, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *

OUT = os.environ.get("HY_OUT", "/tmp/esc644_")
bad = []
def ok(c, m):
    print(("OK  " if c else "BAD ") + m)
    if not c: bad.append(m)

GEN = """async ([set, lv])=>{ await Duel.ready(); const L=Study.lessons(set); const p=Esc.make({set, from:0, to:Math.min(5, L.length-1), lv, th:'pir'}); const A=p.A, ids=Esc.ids(), bad=[];
  ids.forEach(id=>{ const z=Esc.pz({R:p.R, m:p.m}, id); if(!z) bad.push(id+':없음'); else if(z.id!==id) bad.push(id+':번호'); if(!A[id]) bad.push(id+':답'); });
  p.R.forEach((R,r)=>{ const got=['a','b','c'].map(x=>p.G[r+x].join('')).join(''); if(got.split('').sort().join('')!==A[r+'d'].split('').sort().join('')) bad.push(r+':문 글자');
    if(!R.P[0].give || !R.P[1].gate || R.P[0].give!==R.P[1].gate.it) bad.push(r+':아이템'); if(R.ob.length!==6) bad.push(r+':물건');
    R.P.forEach(z=>{ const a=A[z.id];
      if(z.k==='wire'){ const ok=a.length===z.n && a.split('').every((x,i)=>z.ko[+x]===Esc.ko1(Study.lessons(set).flatMap(l=>l.ws||[]).find(w=>w.en===z.en[i])||{ko:''}) || true) && new Set(a).size===z.n; if(!ok) bad.push(z.id+':전선'); }
      if(z.k==='dial' && !a.split('').every((c,i)=>z.wh[i].indexOf(c)>=0)) bad.push(z.id+':다이얼');
      if(z.k==='simon' && (a!==z.seq.join(' ') || !z.seq.every(w=>z.tiles.indexOf(w)>=0))) bad.push(z.id+':소리');
      if(z.k==='ord' && !a.split(' ').every(w=>z.tiles.indexOf(w)>=0)) bad.push(z.id+':문장');
      if(z.k==='code' && !new RegExp('^\\\\d{'+z.n+'}$').test(a)) bad.push(z.id+':번호'); }); });
  if(A.m!==[0,1,2].map(r=>A[r+'d'].length).join('')) bad.push('m:마지막');
  const nz=p.R[1].P.find(z=>z.note); if(!nz || !nz.note.full || nz.note.a+nz.note.b!==nz.note.full) bad.push('쪽지');
  const st=M=>M.map(me=>Esc.stash(p.R[0], M, me, me+'|0|1'));
  const S3=st(['a','b','c']), gob=p.R[0].P[1].gate.ob, allT=[].concat(...S3).filter(x=>x.t).map(x=>x.pid+x.t);
  p.R[0].P.filter(z=>!z.gate).forEach(z=>z.pc.forEach(t=>{ if(allT.indexOf(z.id+t)<0) bad.push(z.id+':숨긴 단서 빠짐'); }));
  if([].concat(...S3).some(x=>x.ob===gob)) bad.push('아이템 물건에 숨김');
  const N=['a','b'].map(me=>Esc.stash(p.R[1], ['a','b'], me, me+'|1|1').filter(x=>x.it).map(x=>x.it).join(','));
  return {ks:ids.map(id=>Esc.pz({R:p.R, m:p.m}, id).k).join(','), bad, N, A}; }"""

SOLVE = """async ([id, v])=>{ const P=EscPad; P.view=id; P.inp=''; P.iw=[]; P.iwI=[]; P.wm=null; P.dl=null; P.wl=null; P.draw(); const z=P.z();
  if(z.k==='ord'||z.k==='simon'){ const K=[...document.querySelectorAll('#escPad .epKeys.wd button')]; v.split(' ').forEach(w=>{ const b=K.find(b=>b.dataset.v===w && !b.disabled && P.iwI.indexOf(+b.dataset.i)<0); if(b) b.click(); }); }
  else if(z.k==='wire'){ v.split('').forEach((r,i)=>{ document.querySelector('#escPad [data-ep=wl][data-i="'+i+'"]').click(); document.querySelector('#escPad [data-ep=wr][data-i="'+r+'"]').click(); }); }
  else if(z.k==='dial'){ P.dl=z.wh.map((L,i)=>L.indexOf(v[i])); P.draw(); }
  else P.inp=v;
  P.drawIn(); const s=document.getElementById('epSend'); const dis=s.disabled; P.send(); return {k:z.k, dis, v:P.val()}; }"""
SEARCH = "async ()=>{ const P=EscPad; P.view=null; P.sel=null; P.draw(); for(let i=0;i<6;i++){ P.look(i); await new Promise(z=>setTimeout(z,760)); } P.draw(); return P.lm; }"
USE = """(wrong)=>{ const P=EscPad; P.view=null; P.draw(); const T=P.myT(), R=P.Z().R[T.rm], gz=R.P.find(x=>x.gate); const it=gz.gate.it; document.querySelector('#escPad [data-ep=it][data-v="'+it+'"]').click();
  const ob=wrong ? (gz.gate.ob+1)%6 : gz.gate.ob; document.querySelector('#escPad [data-ep=ob][data-i="'+ob+'"]').click(); return [it, ob, P.lm]; }"""
TS = "(t)=>{ const T=EscTV.st.T[t]; return {rm:T.rm, sv:Object.keys(T.sv||{}).sort().join(','), inv:(T.inv||[]).join(','), rev:Object.keys(T.rev||{}).join(','), msg:(T.msg||{}).m||'', out:T.out, star:T.star, pen:T.pen, hn:T.hn, fz:T.fz||{}, w:T.w}; }"

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        # ① 문제 만들기 — 학년 · 어려움마다
        pg = await b.new_page(); await boot(pg)
        for st, lv in (("basic", 0), ("elem", 1), ("g56", 2), ("mv1", 1)):
            try: r = await pg.evaluate(GEN, [st, lv])
            except Exception as e: ok(False, f"{st} 만들기 오류 {str(e)[:160]}"); continue
            want = "word,code,wire,fin,first,say,dial,fin," + ("kb" if st == "basic" else "ord") + ",code,simon,fin,code"
            ok(not r["bad"] and (r["ks"] == want or r["ks"] == want.replace("ord", "kb")) , f"{st}/{lv}: 13개 · {r['ks']} · 문제 없음 {r['bad']}")
            ok(r["N"] == ["n1", "n2"], f"{st}: 쪽지 반쪽은 서로 다른 친구에게 {r['N']}")
        r = await pg.evaluate("()=>[Esc.stars(5*60e3, 20*60e3, 0), Esc.stars(15*60e3, 20*60e3, 0), Esc.stars(19*60e3, 20*60e3, 3), Esc.stars(30*60e3, 20*60e3, 0), Esc.stars(60*60e3, 20*60e3, 9)]")
        ok(r == [5, 4, 2, 1, 1], f"⭐ 별 = 시간 + 힌트 {r}")
        await pg.close()
        # ② 수업판 — TV + 패드 4대 (2팀)
        ctx = await b.new_context(viewport={"width": 1920, "height": 1080})
        await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        tv = await ctx.new_page(); errs = []; tv.on("pageerror", lambda e: errs.append("tv " + str(e))); await boot(tv)
        await tv.evaluate("()=>{ EscTV.setup(); }"); await tv.wait_for_timeout(400)
        await tv.screenshot(path=OUT + "setup.png")
        await tv.evaluate("()=>{ document.getElementById('escBk').value='elem'; document.getElementById('escBk').onchange(); document.querySelector('[data-th=\"spc\"]').click(); document.querySelector('[data-lv=\"1\"]').click(); document.querySelector('[data-dur=\"20\"]').click(); document.querySelector('[data-es=go]').click(); }")
        await tv.wait_for_function("()=>EscTV.room && /^\\d{4}$/.test(EscTV.room)", timeout=8000); room = await tv.evaluate("()=>EscTV.room")
        ok(await tv.evaluate("()=>EscTV.cfg.dur===20 && EscTV.cfg.th==='spc' && EscTV.cfg.lv===1"), f"방 만들기 (🚀 우주 · 보통 · 20분) {room}")
        kids = []
        for i, (nm, vp) in enumerate((("가온", (820, 1180)), ("나래", (390, 844)), ("다솜", (915, 412)), ("라온", (1180, 820)))):
            k = await ctx.new_page(); k.on("pageerror", lambda e, nm=nm: errs.append(nm + " " + str(e))); await k.set_viewport_size({"width": vp[0], "height": vp[1]}); await boot(k)
            await k.evaluate("(a)=>{ EscPad.join(a[0], {id:'k'+a[1], n:a[2]}); window.confirm=()=>true; }", [room, i, nm]); kids.append(k); await k.wait_for_timeout(300)
        await tv.wait_for_timeout(800)
        await tv.evaluate("()=>{ document.querySelector('[data-et=nt][data-n=\"2\"]').click(); }"); await tv.wait_for_timeout(200)
        await tv.evaluate("()=>document.querySelector('[data-et=go]').click()"); await tv.wait_for_function("()=>EscTV.st && EscTV.st.s==='run'", timeout=10000); await tv.wait_for_timeout(1500)
        r = await tv.evaluate("()=>!document.getElementById('escStory').hidden"); ok(r, "시작 전 TV 이야기 화면")
        await tv.screenshot(path=OUT + "tv_story.png")
        S = await tv.evaluate("()=>({M:EscTV.st.M, ans:EscTV.ans})")
        kid = {f"k{i}": kids[i] for i in range(4)}
        A, B = [kid[x] for x in S["M"]["0"]]; t1m = [kid[x] for x in S["M"]["1"]]; a0 = S["ans"]["0"]
        ok(await A.evaluate("()=>!!document.querySelector('#escPad .epStory')"), "패드도 이야기 화면")
        await A.screenshot(path=OUT + "pad_story.png")
        await tv.wait_for_function("()=>EscTV.now()>=EscTV.st.t0", timeout=12000); await tv.wait_for_timeout(1300)
        # 방 화면: 퍼즐 카드 4개(문은 잠김) · 물건 6 · 가방 비었음
        r = await A.evaluate("()=>({c:document.querySelectorAll('#escPad .epPzC').length, wait:document.querySelectorAll('#escPad .epPzC.wait').length, ob:document.querySelectorAll('#escPad .epObj button').length, inv:document.querySelector('#escPad .epInv').textContent})")
        ok(r["c"] == 4 and r["wait"] == 1 and r["ob"] == 6 and "비었어요" in r["inv"], f"방 화면 = 퍼즐 3 + 문(잠김) · 물건 6 · 가방 {r}")
        await A.screenshot(path=OUT + "room_pad.png")
        # 게이트 퍼즐에 힌트 → 귀띔(아이템 필요)
        await A.evaluate("()=>{ EscPad.view='0b'; EscPad.draw(); document.querySelector('[data-ep=hint]').click(); }"); await tv.wait_for_timeout(800)
        t = await tv.evaluate(TS, 0); h = await tv.evaluate("()=>EscTV.st.T[0].hs['0b'][0]")
        ok("필요" in h and t["pen"] == 45000 and t["hn"] == 1, f"아이템 전 힌트 = 귀띔 · 벌점 45초 {h} {t['pen']}")
        # 뒤지기 → 단서 찾음
        lm = await A.evaluate(SEARCH); lmB = await B.evaluate(SEARCH)
        c = [await m.evaluate("()=>['0a','0c'].map(id=>EscPad.clues(Esc.pz(EscPad.Z(), id)).length)") for m in (A, B)]
        ok(sum(c[0]) + sum(c[1]) >= 3 and sum(c[0]) < 3, f"뒤져서 단서 · 나눠 받음 {c} {lm[:40]}")
        await A.screenshot(path=OUT + "room_found_pad.png")
        # 틀리면 그 퍼즐만 20초 잠김 · 다른 퍼즐은 됨
        await A.evaluate(SOLVE, ["0a", "zzzz"]); await tv.wait_for_timeout(800)
        t = await tv.evaluate(TS, 0)
        ok(t["w"] == 1 and "0a" in t["fz"] and t["pen"] == 55000, f"틀림 → 0a 만 잠김 · +10초 {t['fz']} {t['pen']}")
        r = await B.evaluate(SOLVE, ["0c", a0["0c"]]); await tv.wait_for_timeout(800)
        t = await tv.evaluate(TS, 0); ok("0c" in t["sv"], f"잠긴 동안 다른 퍼즐(🔌 전선) 열림 {t['sv']} {r}")
        r = await B.evaluate(SOLVE, ["0a", a0["0a"]]); await tv.wait_for_timeout(800)
        ok("0a" not in (await tv.evaluate(TS, 0))["sv"], "잠긴 퍼즐은 정답도 안 받음")
        await tv.evaluate("()=>{ EscTV.st.T[0].fz={}; EscTV.push(); }"); await tv.wait_for_timeout(500)
        await A.evaluate(SOLVE, ["0a", a0["0a"]]); await tv.wait_for_timeout(900)
        t = await tv.evaluate(TS, 0); it = t["inv"]
        ok("0a" in t["sv"] and it in ("lamp", "lens", "key", "mag") and "얻었어요" in t["msg"], f"🔤 풀면 아이템 {it} · 안내 {t['msg']}")
        await B.evaluate("()=>{ EscPad.view=null; EscPad.draw(); }"); await B.wait_for_timeout(300)
        ok(await B.evaluate("(it)=>!!document.querySelector('#escPad [data-ep=it][data-v=\"'+it+'\"]')", it), "팀원 가방에도 아이템")
        await B.screenshot(path=OUT + "room_item_ph.png")
        # 잘못 쓰기 = 아무 일도 없음 · 맞게 쓰기 = 단서 나타남
        r = await B.evaluate(USE, True); ok("아무 일도" in r[2], f"엉뚱한 물건에 쓰면 아무 일도 없음 {r}")
        r = await B.evaluate(USE, False); await tv.wait_for_timeout(900)
        t = await tv.evaluate(TS, 0); ok("0b" in t["rev"] and "단서가 나왔어요" in t["msg"], f"맞는 물건에 쓰면 0b 단서 {t['rev']} {t['msg'][:40]}")
        n = await A.evaluate("()=>EscPad.clues(Esc.pz(EscPad.Z(),'0b')).length"); ok(n == 3, f"단서가 팀 모두에게 {n}")
        await A.evaluate("()=>{ EscPad.view='0b'; EscPad.draw(); }"); await A.screenshot(path=OUT + "pz_code_pad.png")
        await A.evaluate(SOLVE, ["0b", a0["0b"]]); await tv.wait_for_timeout(900)
        t = await tv.evaluate(TS, 0); ok(t["sv"] == "0a,0b,0c", f"방 1 퍼즐 3개 {t['sv']}")
        await tv.screenshot(path=OUT + "tv_run.png")
        await B.evaluate(SOLVE, ["0d", a0["0d"]]); await tv.wait_for_timeout(900)
        t = await tv.evaluate(TS, 0); ok(t["rm"] == 1 and "문이 열렸어요" in t["msg"], f"🚪 문 → 방 2 {t['rm']} {t['msg'][:30]}")
        await tv.screenshot(path=OUT + "tv_big.png")
        # 방 2: 쪽지 두 장 → 합치기 · 아이템 · 다이얼
        await A.evaluate(SEARCH); await B.evaluate(SEARCH); await tv.wait_for_timeout(900)
        t = await tv.evaluate(TS, 0); ok("n1" in t["inv"] and "n2" in t["inv"], f"📜 쪽지 반쪽 두 장 {t['inv']}")
        await A.evaluate("()=>{ EscPad.view=null; EscPad.draw(); }"); await A.wait_for_timeout(200)
        await A.screenshot(path=OUT + "room2_notes_pad.png")
        await A.evaluate("()=>document.querySelector('#escPad [data-ep=mix]').click()"); await tv.wait_for_timeout(900)
        t = await tv.evaluate(TS, 0); ok("1c" in t["rev"] and "n1" not in t["inv"], f"쪽지 합치기 → 다이얼 뜻 {t['rev']} {t['msg'][:50]}")
        n = await B.evaluate("()=>EscPad.clues(Esc.pz(EscPad.Z(),'1c'))"); ok(any("뜻" in x for x in n), f"합친 뜻이 단서에 {n}")
        await B.evaluate("()=>{ EscPad.view='1c'; EscPad.draw(); }"); await B.screenshot(path=OUT + "pz_dial_ph.png")
        for pid, m in (("1a", A), ("1c", B)):
            r = await m.evaluate(SOLVE, [pid, a0[pid]]); await tv.wait_for_timeout(800)
        await B.evaluate(USE, False); await tv.wait_for_timeout(800)
        await A.evaluate(SOLVE, ["1b", a0["1b"]]); await tv.wait_for_timeout(800)
        await A.evaluate(SOLVE, ["1d", a0["1d"]]); await tv.wait_for_timeout(900)
        t = await tv.evaluate(TS, 0); ok(t["rm"] == 2, f"방 2 끝 {t['sv']}")
        # 방 3: 아이템 귀띔(오래 안 쓰면) · 소리 순서 · 문 · 마지막 장치
        await A.evaluate(SOLVE, ["2a", a0["2a"]]); await tv.wait_for_timeout(900)
        await tv.evaluate("()=>{ const T=EscTV.st.T[0]; Object.keys(T.got).forEach(k=>T.got[k]-=90000); }"); await tv.wait_for_timeout(1200)
        t = await tv.evaluate(TS, 0); ok("💭" in t["msg"], f"아이템 오래 안 쓰면 귀띔 {t['msg']}")
        await B.evaluate("()=>{ EscPad.view='2c'; EscPad.draw(); }"); await B.screenshot(path=OUT + "pz_simon_ph.png")
        await A.evaluate("()=>{ EscPad.view='2a'; EscPad.draw(); }")
        await B.evaluate(SOLVE, ["2c", a0["2c"]]); await tv.wait_for_timeout(800)
        await A.evaluate(USE, False); await tv.wait_for_timeout(800)
        await A.evaluate(SOLVE, ["2b", a0["2b"]]); await tv.wait_for_timeout(800)
        await B.evaluate(SOLVE, ["2d", a0["2d"]]); await tv.wait_for_timeout(1000)
        t = await tv.evaluate(TS, 0); ok(t["rm"] == 3, f"방 3 끝 → 🚀 {t['sv']}")
        ok(await A.evaluate("()=>EscPad.view==='m' && !!document.querySelector('#escPad .epPz')"), "마지막 장치 화면이 바로")
        await A.screenshot(path=OUT + "pz_meta_pad.png")
        # 시간 넘김 → 안 끝남 · 별 줄어듦
        await tv.evaluate("()=>{ EscTV.st.t0-=24*60e3; EscTV.push(); }"); await tv.wait_for_timeout(1200)
        r = await tv.evaluate("()=>[EscTV.st.s, document.getElementById('escClock').textContent]")
        ok(r[0] == "run" and r[1].startswith("+"), f"목표 시간이 지나도 계속 (+시간) {r}")
        await A.evaluate(SOLVE, ["m", a0["m"]]); await tv.wait_for_timeout(1200)
        t = await tv.evaluate(TS, 0); ok(t["out"] and 1 <= t["star"] <= 2, f"탈출 · 시간 넘겨서 별 {t['star']}")
        r = await A.evaluate("()=>[document.querySelector('#escPad .epEnd h3').textContent, (document.querySelector('#escPad .epStars')||{}).textContent||'', (document.querySelector('#escPad .stGem')||{}).textContent||'']")
        ok("탈출 성공" in r[0] and "⭐" in r[1] and "+" in r[2], f"패드 끝 화면 · 별 · 보석 {r}")
        await A.screenshot(path=OUT + "end_pad.png")
        # 팀 1 = 방 1 만 → 끝내기
        a1 = S["ans"]["1"]; X, Y = t1m
        await X.evaluate(SEARCH)
        for pid, m in (("0a", X), ("0c", Y)): await m.evaluate(SOLVE, [pid, a1[pid]]); await tv.wait_for_timeout(700)
        await Y.evaluate(USE, False); await tv.wait_for_timeout(700)
        await X.evaluate(SOLVE, ["0b", a1["0b"]]); await tv.wait_for_timeout(700)
        await X.evaluate(SOLVE, ["0d", a1["0d"]]); await tv.wait_for_timeout(800)
        await tv.evaluate("()=>{ window.confirm=()=>true; document.querySelector('[data-et=end]').click(); }"); await tv.wait_for_timeout(1000)
        r = await tv.evaluate("()=>[EscTV.st.s, EscTV.st.ord, EscTV.st.T[1].rm, document.querySelector('.escRank').textContent]")
        ok(r[0] == "end" and r[1] == ["0", "1"] and r[2] == 1 and "⭐" in r[3], f"끝 · 순위 · 별 {r}")
        await tv.screenshot(path=OUT + "tv_end.png")
        r = await X.evaluate("()=>[document.querySelector('#escPad .epEnd h3').textContent, (document.querySelector('#escPad .stGem')||{}).textContent||'']")
        ok("여기까지" in r[0] and "+3" in r[1], f"못 나간 팀 = 방 1개 💎2 + 1 {r}")
        e = [x for x in errs if "favicon" not in x]; ok(not e, f"오류 없음 {e[:3]}")
        await ctx.close()
        # ③ 화면 — 휴대폰 · 패드 · 가로 휴대폰 · 가로 패드 : 방 화면 + 퍼즐 종류마다 스크롤 없이 · 열기 단추 화면 안
        for setn in ("elem", "mv1"):
            ctx = await b.new_context(viewport={"width": 1280, "height": 800}); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
            tv = await ctx.new_page(); await boot(tv)
            await tv.evaluate("(s)=>EscTV.host({set:s, from:0, to:5, dur:20, th:'wiz', lv:2})", setn); await tv.wait_for_function("()=>EscTV.room", timeout=8000); room = await tv.evaluate("()=>EscTV.room")
            pads = []
            for nm, vp in (("phL", (915, 412)), ("ph", (390, 844)), ("pad", (820, 1180)), ("padL", (1180, 820)), ("se", (375, 667))):
                k = await ctx.new_page(); await k.set_viewport_size({"width": vp[0], "height": vp[1]}); await boot(k)
                await k.evaluate("(a)=>{ EscPad.join(a[0], {id:a[1], n:a[1]}); window.confirm=()=>true; }", [room, nm]); pads.append((nm, k))
            await tv.wait_for_timeout(700); await tv.evaluate("async ()=>{ EscTV.nT=1; await EscTV.go(); EscTV.st.t0=EscTV.now()+300; EscTV.push(); }"); await tv.wait_for_timeout(1500)
            ids = await tv.evaluate("()=>Esc.ids()")
            # 모든 퍼즐 단서가 보이게: 아이템 다 · 단서 다 열림 · 글자 다
            await tv.evaluate("()=>{ const T=EscTV.st.T[0]; T.inv=['lamp','lens','key','mag','n1','n2']; T.rev={'0b':1,'1b':1,'2b':1,'1c':1}; T.msg={t:EscTV.now(), m:'🎁 🔦 손전등을 얻었어요! — 어두운 곳을 비춰요 · 어디에 쓸까요?'}; EscTV.push(); }"); await tv.wait_for_timeout(600)
            for nm, k in pads:
                await k.evaluate(SEARCH)
            for i, pid in enumerate([None] + ids):
                if pid and pid[1:] == "d": await tv.evaluate("(r)=>{ const T=EscTV.st.T[0]; T.fl=EscTV.ans[0][r+'d'].slice(0,-1); EscTV.push(); }", pid[0]); await tv.wait_for_timeout(400)
                if pid == "m": await tv.evaluate("()=>{ EscTV.st.T[0].rm=3; EscTV.push(); }"); await tv.wait_for_timeout(500)
                elif pid: await tv.evaluate("(r)=>{ EscTV.st.T[0].rm=r; EscTV.push(); }", int(pid[0])); await tv.wait_for_timeout(400)
                for nm, k in pads:
                    await k.evaluate("(id)=>{ EscPad.view=id; EscPad.inp=''; EscPad.iw=[]; EscPad.iwI=[]; EscPad.draw(); }", pid)
                    if pid: await k.evaluate(SOLVE.replace("P.send();", ""), [pid, await tv.evaluate("(i)=>EscTV.ans[0][i]", pid)])
                    r = await k.evaluate("""()=>{ const P=document.getElementById('escPad'), s=document.getElementById('epSend'), all=[...P.querySelectorAll('button')].filter(b=>b.offsetParent).map(b=>b.getBoundingClientRect());
                        return [P.scrollHeight-P.clientHeight, Math.round(Math.max(...all.map(x=>x.bottom))), innerHeight, Math.round(Math.max(...all.map(x=>x.right))), innerWidth, s ? Math.round(s.getBoundingClientRect().bottom) : 0]; }""")
                    ok(r[0] <= 0 and r[1] <= r[2] and r[3] <= r[4] and r[5] <= r[2], f"{setn} {nm} {pid or '방'}: 스크롤 없이 화면 안 {r}")
                    if setn == "elem" and (pid in (None, "0c", "1c", "2c", "2a") or nm in ("phL", "ph") and pid in ("0d", "m")): await k.screenshot(path=f"{OUT}fit_{pid or 'room'}_{nm}.png")
            await ctx.close()
        await b.close()
    print("PASS" if not bad else "FAIL", len(bad))
    if bad: sys.exit(1)

asyncio.run(main())
