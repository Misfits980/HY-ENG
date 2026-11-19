"""(v710) G5-6 리딩 1·2·3 짧은 글(data/rdst.json) 검사 — 게임에서 과 단어를 뽑아 맞춰 봄
   7~8문장 · 80~100단어 · 문장 15단어 이하 · 그 과 단어 5~6개가 글에 있음 · 과거 문장 6+ · 순서 말 4 · OX ⭕❌ 하나씩 · 해요체 · (v710) 책 시험 빈칸 bl · (v711) 세부 내용 wh · 순서 sq
   (v712) G1-2 basic (L1: 3문장 · 문장당 3~6단어 · 쓴 단어 2) · G3-4 elem (L2: 4문장 · 25~40단어 · 쓴 단어 3) — 지금 일 · 글과 문제의 모든 낱말이
   그 학년 책 + 아래 책(유치원 7권 · G1-2)에 있음(모양 바뀐 것 포함) · 빈칸 답이 다른 문제(OX·제목·세부·생각)에 안 보임 · OX·세부 근거가 빈칸 문장이 아님 · 생각 틀(fr)·고르기(ch)·예시 답이 맞물림
   python3 tools/rdst_check.py"""
import re
import asyncio, sys, os, json
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT+"/tools/tests")
from harness import *
from playwright.async_api import async_playwright
JS=r"""(set)=>{ Study.ctx(set); const L=Study.lessons(set); const U={}, seen={};
  L.forEach(l=>{ const u=String(Study.stageNo(set,l.n)).split('-')[0]; (l.ws||[]).forEach(w=>{ if(!w || !w.en || seen[w.en]) return; seen[w.en]=1; let D=null; try{ D=DexData.of(w.en); }catch(e){} (U[u]=U[u]||[]).push([w.en, w.ko, D && D[1] ? String(D[1]) : '']); }); });
  return U; }"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); ctx=await br.new_context(); pg=await ctx.new_page()
        await boot(pg); E=pg.evaluate
        await E("()=>{ try{ DexData.load(1); DexData.load(2); DexData.load(3); loadEasy(); }catch(e){} }"); await pg.wait_for_timeout(3000)
        out={}
        for s in ("rd1","rd2","rd3","g56","basic","elem"):
            out[s]=await E(JS, s)
        out["_lex"]=await E("""()=>{ const o={}; ["kinder","abc","short","long","digr","vowel2","sight","basic","elem"].forEach(s=>{ Study.ctx(s); const W={}; Study.lessons(s).forEach(l=>(l.ws||[]).forEach(w=>{ if(w&&w.en) W[w.en.toLowerCase()]=1; })); o[s]=Object.keys(W); }); return o; }""")
        return out
        await br.close()
U=asyncio.run(main())

D=json.load(open(ROOT+'/data/rdst.json',encoding='utf-8'))
NAMES={"Siwoo","Leo","Hana","Sora","Doyun","Emma","Ben","Yejin","Noah","Haeun","Lily","Sam","Mr","Kim"}
OKCAP={"Grandma","Dad","Mom","Earth","Day","Delicious","Just","Wear","They","It","Last","First","Then","Finally","After","One","On","Every","Her","His","Photography","Local","April","Sunday","Saturday","Friday","I"}
IRR={"catch":["caught"],"fly":["flew"],"break":["broke"],"lose":["lost"],"sleep":["slept"],"swim":["swam"],"think":["thought"],"leave":["left"],"spend":["spent"],"choose":["chose"],"melt":["melted"],"board":["boarded"],"meet":["met"],"bring":["brought"],"take":["took"],"buy":["bought"],"tell":["told"],"give":["gave"],"draw":["drew","drawn","drawing"],"choose":["chose"],"hang":["hung"],"win":["won"],"eat":["ate"],"go":["went"],"cut":["cut"],"put":["put"],"say":["said"],"sell":["sold"],"show":["showed"],"feel":["felt"],"find":["found"],"write":["wrote"],"have":["had"],"run":["ran"]}
PAST=re.compile(r"\b(\w+ed|was|were|had|went|took|gave|told|felt|said|brought|bought|found|wrote|ate|ran|met|sold|chose|cut|put|hung|won|drew|hurt|spent|left|made|saw|did)\b", re.I)
def forms(w):
    if " " in w: return [w, w+"s", w+"es"]
    f=[w, w+"s", w+"es", w+"ed", w+"d", w+"ing", w[:-1]+"ies" if w.endswith("y") else w, w[:-1]+"ing" if w.endswith("e") else w]
    if re.search(r"[^aeiou][aeiou][bdgmnprt]$", w): f+= [w+w[-1]+"ed", w+w[-1]+"ing"]
    return f+IRR.get(w,[])
bad=0
ALLC=set()
# ── (v712) G1-2 · G3-4 ──
LX=U["_lex"]; A1=set()
for k in ("kinder","abc","short","long","digr","vowel2","sight","basic"): A1.update(LX[k])
A2=A1|set(LX["elem"])
for A in (A1,A2): A.update([t for x in list(A) if " " in x for t in x.split()])
LNAMES={"Amy","Ben","Tom","Mina","Jiho","Yuna","Minho","Sora","Jun","Hana","Mia","Leo","Grandma","Mom"}
FW=set("a an the and but or so is are am it its his her their our my your they we you he she i me him them us to of in on at for with by from about then very too not do does can there this that what who where when how".split())
LIRR={"teeth":"tooth","feet":"foot","children":"child","men":"man","women":"woman"}
def cands(t):
    t=t.lower().replace("’","'")
    if t.endswith("'s"): t=t[:-2]
    c={t}
    if t in LIRR: c.add(LIRR[t])
    for suf,rep in (("ies","y"),("es",""),("s",""),("ed",""),("ed","e"),("d",""),("ing",""),("ing","e")):
        if t.endswith(suf): c.add(t[:-len(suf)]+rep)
    if re.search(r"(bb|dd|gg|mm|nn|pp|rr|tt)(ed|ing)$", t): c.add(re.sub(r"(.)\1(ed|ing)$", r"\1", t))
    return c
def known(t, A):
    if re.sub(r"['’]s$","",t) in LNAMES: return True
    return any(x in A or x in FW for x in cands(t))
LPAST=re.compile(r"\b(\w+ed|was|were|had|went|took|gave|told|felt|said|brought|bought|found|wrote|ate|ran|met|sold|chose|made|saw|did|came|got|drew|flew|won)\b", re.I)
OKED={"tired","excited","bored","scared","red","bed","need","feed","seed","sled"}
TOK=lambda t: re.findall(r"[A-Za-z'’-]+", t)
for book, lv in (("basic",1),("elem",2)):
    for u, L in (D.get(book) or {}).items():
        for st in L:
            prob=[]; txt=" ".join(s[0] for s in st["s"]); words=TOK(txt); n=len(words); A=A1 if lv==1 else A2
            uw={e.lower() for e,ko,p in U[book][u]}
            if len(st["s"])!=(3 if lv==1 else 4): prob.append(f"문장 {len(st['s'])}")
            if lv==1: prob+=[f"문장 길이 {len(TOK(s[0]))}" for s in st["s"] if not 3<=len(TOK(s[0]))<=6]
            elif not 25<=n<=40: prob.append(f"단어 {n}")
            if len(st["ws"])!=(2 if lv==1 else 3): prob.append("쓴 단어 수")
            for w in st["ws"]:
                if w.lower() not in uw: prob.append(f"{w} 그 Stage 단어 아님")
                if not any(w.lower() in cands(x) for x in words): prob.append(f"{w} 글에 없음")
            extra=[o[0] for o in st["ox"]]+st.get("tc",[])+([st["wh"][0]]+st["wh"][2:6] if st.get("wh") else [])+[st["q"][0], st["ex"][0], st["fr"]]+st.get("ch",[])
            unk=[x for x in words+TOK(" ".join(extra)) if not known(x, A)]
            if unk: prob.append("이 학년 책에 없는 낱말 "+str(sorted(set(unk))))
            past=[s[0] for s in st["s"] if any(m.lower() not in OKED for m in LPAST.findall(s[0]))]
            if past: prob.append("지난 일? "+str(past))
            ox=st["ox"]
            if len(ox)!=2 or sorted(o[2] for o in ox)!=[False,True] or any(not 1<=o[3]<=len(st["s"]) for o in ox): prob.append("OX")
            bl=st.get("bl")
            if not bl or len(bl)!=4 or len(set(bl))!=4: prob.append("빈칸 bl")
            else:
                rx=r"\b"+re.escape(bl[0])+r"\b"
                if len(re.findall(rx, txt, re.I))!=1 or any(re.match(rx, s[0]) for s in st["s"]): prob.append("빈칸 자리 "+bl[0])
                else:
                    bsi=next(i for i,s in enumerate(st["s"]) if re.search(rx, s[0]))
                    if any(o[3]==bsi+1 for o in ox): prob.append(f"OX 근거가 빈칸 문장 ({bsi+1})")
                    if st.get("wh") and st["wh"][6]==bsi+1: prob.append("세부 내용 근거가 빈칸 문장")
                if any(re.search(r"\b"+re.escape(d)+r"\b", txt, re.I) for d in bl[1:]): prob.append("틀린 보기가 글에 있음")
                if not any(c in A for c in cands(bl[0])): prob.append("빈칸 답이 책 단어 아님")
                prob+=["보기 수준 "+d for d in bl[1:] if not known(d, A)]
                stem=bl[0].lower() if len(bl[0])<=4 else re.sub(r"(ed|s|d)$","",bl[0].lower()).rstrip("e")
                if re.search(r"\b"+re.escape(stem)+r"[a-z]{0,3}\b", " | ".join(extra).lower()): prob.append("빈칸 답이 다른 문제에 보임 "+bl[0])
            if lv==2:
                if len(st.get("tc") or [])!=3 or len(set(st["tc"]))!=3 or st["tc"][0]!=st["t"][0]: prob.append("제목 tc (정답 = 제목 t)")
                wh=st.get("wh")
                if not wh or len(wh)!=7 or len(set(wh[2:6]))!=4 or not 1<=wh[6]<=4: prob.append("세부 내용 wh")
                else:
                    miss=[t for t in re.findall(r"[a-z]{3,}", wh[2].lower()) if t not in txt.lower() and t not in ("the","his","her")]
                    if miss: prob.append("세부 정답 낱말이 글에 없음 "+str(miss))
            elif st.get("tc") or st.get("sm") or st.get("wh"): prob.append("G1-2 는 제목·요약·세부 없음")
            fr=st.get("fr") or ""
            if fr.count("___")!=1: prob.append("생각 틀 fr")
            elif lv==1:
                ch=st.get("ch") or []
                if len(ch)!=2: prob.append("고르기 ch")
                elif st["ex"][0] not in [fr.replace("___", c).replace(" .", ".") for c in ch]: prob.append("예시 답 ≠ 틀+고르기 "+st["ex"][0])
            else:
                m=re.fullmatch(re.escape(fr.replace(" .",".")).replace("___", r"(.+?)"), st["ex"][0])
                if not m: prob.append("예시 답 ≠ 틀 "+st["ex"][0])
                elif len(m.group(1).split())!=1: prob.append("한 단어 아님 "+m.group(1))
            prob+=["해요체 "+s[1][-6:] for s in st["s"] if not s[1].endswith(("요.","요!","요?"))]
            print(f"{book:5s} {u:>2} {st['t'][0][:30]:30s} 단어 {n:2d} {'OK' if not prob else prob}")
            bad+=bool(prob)
for book, units in D.items():
    if book in ("_","basic","elem"): continue
    for u, L in units.items():
        for k, st in enumerate(L):
            txt=" ".join(s[0] for s in st["s"]); words=re.findall(r"[A-Za-z']+", txt); n=len(words)
            uw={e.lower() for e,ko,p in U[book][u]}
            prob=[]
            if not 7<=len(st["s"])<=8: prob.append(f"문장 {len(st['s'])}")
            if not 80<=n<=100: prob.append(f"단어 {n}")
            if not 5<=len(st["ws"])<=6: prob.append(f"쓴 단어 {len(st['ws'])}")
            for w in st["ws"]:
                if w.lower() not in uw: prob.append(f"{w} 과 단어 아님")
                if not any(re.search(r"\b"+re.escape(f)+r"\b", txt, re.I) for f in forms(w.lower())): prob.append(f"{w} 글에 없음")
            caps=set()
            for s in st["s"]:
                ws_=re.findall(r"[A-Za-z']+", s[0])
                for i,x in enumerate(ws_):
                    if x[0].isupper() and x not in NAMES and x not in OKCAP and not x.endswith("'s") : caps.add(x)
                    if x.endswith("'s") and x[:-2] not in NAMES and x[:-2] not in OKCAP: caps.add(x)
            ALLC.update(caps)
            seq=sum(1 for s in st["s"] if re.match(r"(First|Then|After that|Finally)\b", s[0]))
            if seq<4: prob.append(f"순서 말 {seq}")
            past=sum(1 for s in st["s"] if PAST.search(s[0]))
            if past<6: prob.append(f"과거 문장 {past}")
            ox=st["ox"]
            if len(ox)!=2 or sorted([o[2] for o in ox])!=[False,True] or any(not 1<=o[3]<=len(st["s"]) for o in ox): prob.append("OX")
            if len(st["tc"])!=3 or len(st["sm"])!=3 or st["tc"][0]!=st["t"][0]: prob.append("고르기")
            if not st.get("q") or not st.get("ex") or not st["ex"][0].startswith("I would"): prob.append("생각")
            bl=st.get("bl")   # (v710) 책 시험 빈칸 — 글 속 낱말이 한 번 · 문장 첫 낱말 X · ⭕❌·제목·요약에 안 나옴 · 틀린 보기 3개는 글에 없음
            if not bl or len(bl)!=4 or len(set(bl))!=4: prob.append("빈칸 bl")
            else:
                rx=r"\b"+re.escape(bl[0])+r"\b"; shown=" | ".join([o[0] for o in st["ox"]]+st["tc"]+st["sm"])
                if len(re.findall(rx, txt))!=1 or any(re.match(rx, s[0]) for s in st["s"]): prob.append("빈칸 자리 "+bl[0])
                stem=bl[0] if len(bl[0])<=4 else re.sub(r"(ed|s|d)$","",bl[0]).rstrip("e")   # 짧은 낱말(fee)은 그대로 — f… 로 줄이면 for·fun 이 다 걸림
                if re.search(r"\b"+re.escape(stem)+r"[a-z]{0,3}\b", shown, re.I): prob.append("빈칸 답이 문제에 보임 "+bl[0])
                if any(re.search(r"\b"+re.escape(d)+r"\b", txt, re.I) for d in bl[1:]): prob.append("틀린 보기가 글에 있음")
            wh, sq = st.get("wh"), st.get("sq")   # (v711) 세부 내용 · 순서 — 정답 낱말이 글에 있음 · 근거 문장 · 순서 문장 번호가 차례로 · 빈칸 답을 알려 주지 않음
            low=txt.lower(); bstem=(bl[0] if len(bl[0])<=4 else re.sub(r"(ed|s|d)$","",bl[0]).rstrip("e")).lower() if bl else "~"
            if not wh or len(wh)!=7 or len(set(wh[2:6]))!=4 or not 1<=wh[6]<=len(st["s"]): prob.append("세부 내용 wh")
            else:
                miss=[t for t in re.findall(r"[a-z]{4,}", wh[2].lower()) if t not in low]
                if miss: prob.append("세부 내용 정답 낱말이 글에 없음 "+str(miss))
                if re.search(r"\b"+re.escape(bstem), (wh[0]+" "+" ".join(wh[2:6])).lower()): prob.append("세부 내용에 빈칸 답")
            if not sq or len(sq)!=3 or not (sq[0][1]<sq[1][1]<sq[2][1]) or len({x[0] for x in sq})!=3: prob.append("순서 sq")
            elif any(re.search(r"\b"+re.escape(bstem), x[0].lower()) for x in sq): prob.append("순서에 빈칸 답")
            for s in st["s"]:
                if len(re.findall(r"[A-Za-z']+", s[0]))>15: prob.append("긴 문장 "+s[0][:20])
                if not s[1].endswith(("요.", "요!", "요?")): prob.append("해요체 "+s[1][-6:])
            print(f"{book} {u:>2} {st['t'][0][:30]:30s} 단어 {n:2d} 과거 {past} 순서 {seq} {'OK' if not prob else prob}")
            bad+=bool(prob)
print("대문자 낱말(이름·고유명사 확인용)", sorted(ALLC))
print("문제", bad)
sys.exit(1 if bad else 0)
