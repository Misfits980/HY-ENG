"""(v710) G5-6 리딩 1·2·3 짧은 글(data/rdst.json) 검사 — 게임에서 과 단어를 뽑아 맞춰 봄
   7~8문장 · 80~100단어 · 문장 15단어 이하 · 그 과 단어 5~6개가 글에 있음 · 과거 문장 6+ · 순서 말 4 · OX ⭕❌ 하나씩 · 해요체 · (v710) 책 시험 빈칸 bl · (v711) 세부 내용 wh · 순서 sq
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
        for s in ("rd1","rd2","rd3","g56"):
            out[s]=await E(JS, s)
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
for book, units in D.items():
    if book=="_": continue
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
