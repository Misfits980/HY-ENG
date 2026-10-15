"""(v273) 별 단계 — ★1(알아보기) → ★2(쓰임 카드 + 철자) → 95% 면 💜 심화 열림 → 심화 80% 면 💜 + 💎10.
   학년마다(G1-2 · G3-4 · G5-6 · 중등) 한 Stage 씩 끝까지 풀어 본다. 예전 ★3 → ★2 + 심화 열림 옮기기도 확인.
   3단계 1~15과(Stage 1~15)가 G5-6 앞에 들어왔는지, 교재 뜻(order = 주문하다)도 본다."""
import asyncio, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

async def play(pg, shots=None, tag="", wrong_n=0):
    types=[]; seen=set(); wn=0
    for step in range(260):
        t=await pg.evaluate("()=>{ const q=StudyUI.qs[StudyUI.i]; return q ? (q.t+(q.use?'-use':'')+(q.hd?'-'+q.hd:'')+(q.again?'*':'')) : null }")
        if not t: break
        ag=t.endswith("*"); t=t.rstrip("*")
        if shots is not None and t not in seen and t not in ("intro","e2k","k2e","listen"):
            seen.add(t); await pg.wait_for_timeout(60); await pg.screenshot(path=OUT+f"tier_{tag}_{t}.png")
        wr = wn<wrong_n and not ag and not t.startswith("intro") and t not in ("drag","match","ox")
        if wr: wn+=1
        r=await pg.evaluate(SOLVE, wr); types.append(t)
        await pg.wait_for_timeout(450 if r=='drag' else 25)
        if await pg.evaluate("()=>document.getElementById('stDone').style.display!=='none'"): break
    return types

async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); errs=[]; bad=[]
        pg=await br.new_page(viewport={"width":390,"height":844}, device_scale_factor=1, is_mobile=True, has_touch=True)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None)
        await boot(pg)
        await pg.evaluate("()=>{ StudyUI.open(); }"); await pg.wait_for_timeout(1500)   # 도감·교재 예문 받기
        # 3단계 1~15과
        info=await pg.evaluate("""()=>{ const L=Study.lessons('g56'); return {n0:L[0].n, w0:L[0].ws.slice(0,4).map(w=>w.en+'='+w.ko), sn:Study.stageNo('g56',L[0].n),
            st16:Study.stageNo('g56', 11601), order:(L.find(x=>x.ws.some(w=>w.en==='order'))||{ws:[]}).ws.find(w=>w.en==='order'), bex:Object.keys(BEX).length, easter:!!Study.word('easter')} }""")
        print("g56", json.dumps(info, ensure_ascii=False))
        if info["n0"]!=10101: bad.append("G5-6 첫 Stage 가 3단계 1과가 아님")
        if not info["order"] or info["order"]["ko"]!="주문하다": bad.append("order 교재 뜻")
        if info["st16"]!="16-1": bad.append("16과 Stage 번호 %s" % info["st16"])
        if info["bex"]<400: bad.append("bex.json")
        for set_, label in (("basic","g12"),("elem","g34"),("g56","g56"),("mid","mid")):
            await pg.evaluate(f"()=>{{ StudyUI.book=Study.bookOf('{set_}'); StudyUI.set='{set_}'; StudyUI.path(); }}")
            n=await pg.evaluate(f"()=>Study.lessons('{set_}')[0].n")
            g0=await pg.evaluate("()=>Wallet.gems()")
            # ★1
            await pg.evaluate("()=>StudyUI.start(0,false)"); await pg.wait_for_timeout(200)
            t1=await pg.evaluate("()=>StudyUI.tier"); ty1=await play(pg)
            lv1=await pg.evaluate(f"()=>Study.lv('{set_}',{n})")
            # 한 판으로 다 못 만나면(25단어) 한 번 더
            if lv1==0: await pg.evaluate("()=>{ document.getElementById('stBack').click(); StudyUI.start(0,false); }"); ty1+=await play(pg); lv1=await pg.evaluate(f"()=>Study.lv('{set_}',{n})")
            if t1!=1 or lv1!=1: bad.append(f"{label} ★1 tier {t1} lv {lv1}")
            if any(x in ty1 for x in ("spell","dict","sent","sentp","past")): bad.append(f"{label} ★1 판에 철자/빈칸: {sorted(set(ty1))}")
            # ★2 (한 번 틀려서 95% 안 됨 → 심화 안 열림)
            await pg.evaluate("()=>{ document.getElementById('stBack').click(); StudyUI.start(0,false); }"); await pg.wait_for_timeout(200)
            t2=await pg.evaluate("()=>StudyUI.tier"); ty2=await play(pg, [], label+"2", wrong_n=(5 if set_=="mid" else 3))
            st2=await pg.evaluate(f"()=>({{lv:Study.lv('{set_}',{n}), dp:Study.dpOpen('{set_}',{n}), txt:document.getElementById('stDoneIn').innerText.slice(0,160)}})")
            if t2!=2: bad.append(f"{label} ★2 tier {t2}")
            if "intro-use" not in ty2: bad.append(f"{label} ★2 쓰임 카드 없음")
            if st2["lv"]!=2 or st2["dp"]: bad.append(f"{label} ★2 (두 개 틀림) → {st2}")
            # ★2 다시 — 다 맞힘 → 심화 열림
            await pg.evaluate("()=>{ document.getElementById('stBack').click(); StudyUI.start(0,false); }"); await pg.wait_for_timeout(200)
            await play(pg)
            st2b=await pg.evaluate(f"()=>({{lv:Study.lv('{set_}',{n}), dp:Study.dpOpen('{set_}',{n}), txt:document.getElementById('stDoneIn').innerText.slice(0,200)}})")
            if st2b["lv"]!=2 or not st2b["dp"]: bad.append(f"{label} ★2 100% → {st2b}")
            if "심화가 열렸어요" not in st2b["txt"]: bad.append(f"{label} 심화 열림 안내 없음")
            # 길 · 팝업 보라 버튼
            await pg.evaluate("()=>{ document.getElementById('stBack').click(); }"); await pg.wait_for_timeout(200)
            await pg.evaluate("()=>StudyUI.pop(0)"); await pg.wait_for_timeout(100)
            popb=await pg.evaluate("()=>{ const b=document.querySelector('#stPop .stGo'); return b ? b.className+'|'+b.textContent : '' }")
            if "deep" not in popb: bad.append(f"{label} 심화 버튼 {popb}")
            await pg.screenshot(path=OUT+f"tier_{label}_pop.png")
            # 💜 심화
            await pg.evaluate("()=>{ StudyUI.pop(null); StudyUI.start(0,false); }"); await pg.wait_for_timeout(200)
            t3=await pg.evaluate("()=>StudyUI.tier"); ty3=await play(pg, [], label+"3")
            st3=await pg.evaluate(f"()=>({{lv:Study.lv('{set_}',{n}), gems:Wallet.gems(), txt:document.getElementById('stDoneIn').innerText.slice(0,220)}})")
            await pg.screenshot(path=OUT+f"tier_{label}_done3.png")
            if t3!=3 or st3["lv"]!=3: bad.append(f"{label} 심화 tier {t3} lv {st3['lv']}")
            deep=[t for t in ty3 if t not in ("intro","intro-deep","intro-rule","k2e","listen","e2k")]
            print(label, "★1", sorted(set(ty1)), "| ★2", sorted(set(ty2)), st2["lv"], st2["dp"], "| 심화", sorted(set(ty3)), "| 💎", st3["gems"]-g0)
            if len(set(deep))<3: bad.append(f"{label} 심화 문제 종류가 적음 {sorted(set(deep))}")
            if "💎 +10" not in st3["txt"]: bad.append(f"{label} 심화 💎10 없음: {st3['txt'][:120]}")
            await pg.evaluate("()=>{ document.getElementById('stBack').click(); }")
            # 💜 노드
            cls=await pg.evaluate("()=>{ const d=document.querySelector('#stMap .stDot[data-i=\"0\"]'); return d ? d.className+'|'+d.textContent : '' }")
            if "deep" not in cls: bad.append(f"{label} 길 노드 {cls}")
        # 하루 5번 — 다섯 번 받았으니 다음 심화는 보석 대신 안내
        print("dg left", await pg.evaluate("()=>Study.dgLeft()"))
        # 이어 하기 — 심화 판 중간에 저장 · 다시 열기
        await pg.evaluate("()=>{ StudyUI.book='g34'; StudyUI.set='elem'; StudyUI.path(); StudyUI.start(0,false); }")
        for k in range(8): await pg.evaluate(SOLVE, False); await pg.wait_for_timeout(30)
        cur=await pg.evaluate("()=>{ const q=StudyUI.qs[StudyUI.i]; StudyUI.saveCur(); return [StudyUI.i, q && q.t, StudyUI.tier] }")
        ok=await pg.evaluate("()=>{ StudyUI.close(); return StudyUI.resume(); }")
        cur2=await pg.evaluate("()=>{ const q=StudyUI.qs[StudyUI.i]; return [StudyUI.i, q && q.t, StudyUI.tier] }")
        print("resume", cur, cur2, ok)
        if not ok or cur[:2]!=cur2[:2] or cur2[2]!=3: bad.append(f"이어 하기 {cur} {cur2}")
        await play(pg)
        # (v275) 결과 화면 '다음 스테이지로 가기' · 빈칸은 밑줄 하나
        nx=await pg.evaluate("""()=>{ const b=document.querySelector('#stDoneIn [data-next]'), r=!!document.querySelector('#stDoneIn [data-retry]'); if(!b) return {b:null, r};
            const t=b.textContent; b.click(); return {b:t, r, n:StudyUI.les.n, want:Study.lessons('elem')[1].n, blank:document.getElementById('stQ').innerHTML.indexOf('＿')} }""")
        print("next", nx)
        if not nx["b"] or nx["r"] or nx.get("n")!=nx.get("want") or nx.get("blank",-1)>=0: bad.append(f"다음 스테이지 {nx}")
        await pg.evaluate("()=>document.getElementById('stQuit').click()")
        # (v276) 시제·시간 전치사 빈칸 — 설명 한 줄이 붙는 것만
        gq=await pg.evaluate("""()=>{ const a=Study._gram('tense','charge'), b=Study._gram('prep','tulip'), c=Study._gram('tense','arrest');
            return {a:a&&[a.ans,a.x.why], b:b&&[b.ans,b.x.why], c:c&&c.ans} }""")
        print("gram", gq)
        if not gq["a"] or gq["a"][0]!="charged" or not gq["b"] or gq["b"][0]!="in" or gq["c"]: bad.append(f"문법 빈칸 {gq}")
        # (v277) 이어 하기 → 바로 나감을 두 번 해도 시트 줄은 한 번 · 모은 보석(earned)도 보냄
        lg=await pg.evaluate("""()=>{ const sent=[]; const on=Online.on, sub=Online.submit; Online.on=()=>true; Online.submit=r=>{ sent.push(r); return Promise.resolve({}); };
            try{ localStorage.removeItem('hyeng_study_lastquit'); }catch(e){}
            StudyUI.book='g34'; StudyUI.set='elem'; StudyUI.path(); StudyUI.start(0,false);
            for(let k=0;k<4;k++){ const q=StudyUI.qs[StudyUI.i]; if(q.t==='intro'){ StudyUI.i++; continue; } StudyUI.done++; StudyUI.i++; }
            StudyUI.saveCur(); document.getElementById('stQuit').click();
            StudyUI.resume(); document.getElementById('stQuit').click();
            Online.on=on; Online.submit=sub; return sent.map(r=>[r.end, r.earned]); }""")
        print("quit log", lg)
        if len(lg)!=1 or lg[0][1] is None: bad.append(f"나감 기록 {lg}")
        # 예전 ★3 옮기기
        await pg.evaluate("""()=>{ const s=Study.load(); const L=Study.lessons('elem').filter(x=>!x.fin); s.lv['elem-'+L[3].n]=3; delete s.tv; s.dp={}; Study.save(); }""")
        await pg.reload(); await pg.wait_for_timeout(1500)
        mg=await pg.evaluate("()=>{ const L=Study.lessons('elem').filter(x=>!x.fin); return [Study.lv('elem',L[3].n), Study.dpOpen('elem',L[3].n), Study.load().tv] }")
        print("migrate", mg)
        if mg[:2]!=[2,True]: bad.append(f"옮기기 {mg}")
        real=real_errs(errs)
        if real: bad.append("오류: "+" / ".join(real[:5]))
        print("결과:", "통과 ✅" if not bad else "실패 ❌"); [print(" -", b) for b in bad]
        await br.close()
        if bad: sys.exit(1)
asyncio.run(main())
