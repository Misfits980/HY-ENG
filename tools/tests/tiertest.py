"""(v301) 별 5개 — ★1 배우기 → (다음 날) ★2 확인 80% · 💎1 → ★3 써 보기 80% (90% 면 심화 열림) → ★4 심화 80% · 💎10 · ★5 = 🚩.
   (v273 원본) 별 단계 — ★1(알아보기) → ★2(쓰임 카드 + 철자) → 95% 면 💜 심화 열림 → 심화 80% 면 💜 + 💎10.
   학년마다(G1-2 · G3-4 · G5-6 · 중등) 한 Stage 씩 끝까지 풀어 본다. 예전 ★3 → ★2 + 심화 열림 옮기기도 확인.
   3단계 1~15과(Stage 1~15)가 G5-6 앞에 들어왔는지, 교재 뜻(order = 주문하다)도 본다."""
import asyncio, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

async def play(pg, shots=None, tag="", wrong_n=0):
    types=[]; seen=set(); wn=0
    for step in range(260):
        t=await pg.evaluate("()=>{ const q=StudyUI.qs[StudyUI.i]; return q ? (q.t+(q.use?'-use':'')+(q.hd?'-'+q.hd:'')+(q.again?'*':'')+(StudyUI.locked||StudyUI._brk?'#':'')) : null }")
        if not t: break
        lk=t.endswith("#"); t=t.rstrip("#"); ag=t.endswith("*") or lk; t=t.rstrip("*")   # (v301) 답한 뒤 '계속' 누르는 걸음은 틀릴 차례로 안 셈
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
        if not info["order"] or not info["order"]["ko"].startswith("주문하다"): bad.append("order 교재 뜻")
        if info["st16"]!="16-1": bad.append("16과 Stage 번호 %s" % info["st16"])
        if info["bex"]<400: bad.append("bex.json")
        for set_, label in (("basic","g12"),("elem","g34"),("g56","g56"),("mid","mid")):
            await pg.evaluate(f"()=>{{ Study._day(0); StudyUI.book=Study.bookOf('{set_}'); StudyUI.set='{set_}'; StudyUI.path(); }}")
            n=await pg.evaluate(f"()=>Study.lessons('{set_}')[0].n")
            g0=await pg.evaluate("()=>Wallet.gems()")
            S=lambda: pg.evaluate(f"()=>({{lv:Study.lv('{set_}',{n}), ck:Study.ckOk('{set_}',{n}), dp:Study.dpOpen('{set_}',{n}), s:Study.starN('{set_}',Study.lessons('{set_}')[0]), gems:Wallet.gems(), txt:document.getElementById('stDoneIn').innerText.slice(0,200)}})")
            again="()=>{ const b=document.getElementById('stBack'); if(b && document.getElementById('stDone').style.display!=='none') b.click(); StudyUI.start(0,false); return StudyUI.tier; }"
            # ★1 배우기
            t1=await pg.evaluate(again); ty1=await play(pg)
            lv1=await pg.evaluate(f"()=>Study.lv('{set_}',{n})")
            if lv1==0: await pg.evaluate(again); ty1+=await play(pg); lv1=await pg.evaluate(f"()=>Study.lv('{set_}',{n})")   # 25단어 = 두 판
            if t1!=1 or lv1!=1: bad.append(f"{label} ★1 tier {t1} lv {lv1}")
            if any(x in ty1 for x in ("dict","sentp","past")): bad.append(f"{label} ★1 판에 받아쓰기·과거형: {sorted(set(ty1))}")
            if not all(x in ty1 for x in ("intro-guess","intro-once","spell")): bad.append(f"{label} ★1 6단계(짐작·만져 보기·한 번 더) 없음: {sorted(set(ty1))}")   # (v302)
            if label!="g12" and "intro-know" not in ty1: bad.append(f"{label} 아는 단어 빼기 카드 없음")
            if label=="mid" and "intro-sort" not in ty1: bad.append("중등 세 칸 나누기 없음")
            # 오늘은 확인 못 함 → 연습 (별 그대로)
            t5=await pg.evaluate(again); await play(pg); st5=await S()
            if t5!=5 or st5["lv"]!=1 or st5["ck"]: bad.append(f"{label} 같은 날 확인 {t5} {st5}")
            # 내일 — ★2 확인 (두세 개 틀림 → 80% 안 됨)
            await pg.evaluate("()=>Study._day(1)")
            t4=await pg.evaluate(again); nq=await pg.evaluate("()=>StudyUI.qs.filter(q=>q.t!=='intro').length")
            ty4=await play(pg, wrong_n=nq//4+1); st4=await S(); a4=await pg.evaluate("()=>StudyUI.acc1()")
            if t4!=4 or "intro-chk" not in ty4 or any(t.endswith("*") for t in ty4): bad.append(f"{label} 확인 판 {t4} {sorted(set(ty4))}")
            if st4["ck"]!=(a4>=80): bad.append(f"{label} 확인 {nq}문제 {a4}% → {st4}")
            if a4>=80: print(label, "확인 틀리기가 덜 됨", a4)
            # 다시 — 다 맞힘 → ★2 · 💎1
            if not st4["ck"]:
                g4=await pg.evaluate("()=>Wallet.gems()")
                await pg.evaluate(again); await play(pg); st4b=await S()
                if not st4b["ck"] or st4b["s"]!=2 or "확인 통과" not in st4b["txt"]: bad.append(f"{label} 확인 통과 {st4b}")
                if st4b["gems"]-g4<1: bad.append(f"{label} 확인 💎1 없음")
            # ★3 써 보기 — 몇 개 틀림 → 규칙대로인지 (80% ★3 · 90% 심화 열림)
            t2=await pg.evaluate(again); nq2=await pg.evaluate("()=>StudyUI.qs.filter(q=>q.t!=='intro').length")
            ty2=await play(pg, [], label+"2", wrong_n=max(2, -(-nq2*13//100))); st2=await S(); a2=await pg.evaluate("()=>StudyUI.acc1()")
            if t2!=2: bad.append(f"{label} ★3 tier {t2}")
            if "intro-use" not in ty2: bad.append(f"{label} ★3 쓰임 카드 없음")
            if (st2["lv"]==2)!=(a2>=80) or st2["dp"]!=(a2>=90) or st2["s"]!=(3 if a2>=80 else 2): bad.append(f"{label} ★3 {a2}% → {st2}")
            if not st2["dp"]:
                await pg.evaluate(again); await play(pg); st2b=await S()
                if st2b["lv"]!=2 or not st2b["dp"]: bad.append(f"{label} ★3 100% → {st2b}")
                if "심화가 열렸어요" not in st2b["txt"]: bad.append(f"{label} 심화 열림 안내 없음")
            print(label, "★3 첫 판", a2, "%")
            await pg.evaluate("()=>{ document.getElementById('stBack').click(); }"); await pg.wait_for_timeout(200)
            await pg.evaluate("()=>StudyUI.pop(0)"); await pg.wait_for_timeout(100)
            popb=await pg.evaluate("()=>{ const b=document.querySelector('#stPop .stGo'); return b ? b.className+'|'+b.textContent : '' }")
            if "deep" not in popb: bad.append(f"{label} 심화 버튼 {popb}")
            await pg.screenshot(path=OUT+f"tier_{label}_pop.png")
            # ★4 심화
            await pg.evaluate("()=>{ StudyUI.pop(null); StudyUI.start(0,false); }"); await pg.wait_for_timeout(200)
            t3=await pg.evaluate("()=>StudyUI.tier"); ty3=await play(pg, [], label+"3"); st3=await S()
            await pg.screenshot(path=OUT+f"tier_{label}_done3.png")
            if t3!=3 or st3["lv"]!=3 or st3["s"]!=4: bad.append(f"{label} 심화 tier {t3} {st3}")
            deep=[t for t in ty3 if t not in ("intro","intro-deep","intro-rule","k2e","listen","e2k")]
            print(label, "★1", sorted(set(ty1)), "| 확인", sorted(set(ty4)), "| ★3", sorted(set(ty2)), "| 심화", sorted(set(ty3)), "| 💎", st3["gems"]-g0)
            if len(set(deep))<3: bad.append(f"{label} 심화 문제 종류가 적음 {sorted(set(deep))}")
            if "💎 +10" not in st3["txt"]: bad.append(f"{label} 심화 💎10 없음: {st3['txt'][:120]}")
            await pg.evaluate("()=>{ document.getElementById('stBack').click(); }")
            cls=await pg.evaluate("()=>{ const d=document.querySelector('#stMap .stDot[data-i=\"0\"]'); return d ? d.className+'|'+d.textContent : '' }")
            if "deep" not in cls: bad.append(f"{label} 길 노드 {cls}")
            await pg.evaluate("()=>Study._day(0)")
        # (v301) 저장 버그 — 카드만 보고 나가면 '본 단어'가 안 됨 · 이어 하기는 그대로
        sv=await pg.evaluate("""()=>{ StudyUI.book='g34'; StudyUI.set='elem'; StudyUI.path(); const L=Study.lessons('elem'), k=L.findIndex(x=>!x.fin && x.ws.every(w=>!Study.load().seen[w.en]));
            StudyUI.start(k,false); for(let j=0;j<6;j++){ const q=StudyUI.qs[StudyUI.i]; if(q.t==='intro'){ StudyUI.check(); continue; } StudyUI.i++; StudyUI.show(); }
            const pend=Object.keys(StudyUI._sp||{}); StudyUI.saveCur(); const c=JSON.parse(localStorage.getItem('hyeng_study_cur_v1'));
            document.getElementById('stQuit').click(); const S=Study.load().seen; return {pend:pend.length, saved:Object.keys(c.sp||{}).length, leaked:pend.filter(e=>S[e]).length}; }""")
        print("seen", sv)
        if not sv["pend"] or sv["leaked"] or sv["saved"]!=sv["pend"]: bad.append(f"본 단어 저장 {sv}")
        # (v301) 엄격한 보기 — 🚩 시험 보기 중 같은 Stage 가 아닌 단어 (철자 비슷)
        st=await pg.evaluate("""()=>{ const L=Study.lessons('elem'), f=L.find(x=>x.fin), q=Study.buildOly('elem', f).filter(q=>q.opts && q.opts[0] && q.opts[0].en), own={}; f.ws.forEach(w=>own[w.en]=1);
            const out=q.map(x=>x.opts.filter(o=>!own[o.en]).length); return {n:q.length, outside:out.filter(k=>k>=2).length, ex:q.slice(0,3).map(x=>x.w.en+': '+x.opts.map(o=>o.en).join('/'))} }""")
        print("strict", st)
        if st["outside"] < st["n"]*0.6: bad.append(f"🚩 보기가 같은 Stage 위주 {st}")
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
