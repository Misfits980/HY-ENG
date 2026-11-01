"""Daily 30 전체 QA 크롤러 — python3 qa_d30.py <set> <state> <phone|pad> <outdir>
state: path | t1 | t4 | t2 | t3 | fin | v0 | v1 | v2
- 화면마다 audit(): 깨진 그림 · 404 · 가로로 삐져나옴 · (문제·끝 화면) 세로 스크롤 · 확인 띠에 가려진 버튼 · 글자 잘림 · 창이 화면 밖 · 버튼 겹침
- 처음 보는 문제 유형마다 캡처, 처음 2번은 일부러 틀려서 틀림 화면도 캡처, 힌트 단추도 눌러 봄, 끝 화면 · 보물상자 · 길 화면 단추들
결과: outdir/<set>_<state>_<vp>.json + 캡처 png"""
import asyncio, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

AUDIT = r"""(tag)=>{ const W=innerWidth, H=innerHeight, S=document.getElementById('scStudy'), iss=[];
  const desc=e=>(e.id?'#'+e.id:'')+'.'+[...e.classList].slice(0,3).join('.')+'「'+(e.textContent||'').trim().replace(/\s+/g,' ').slice(0,18)+'」';
  const vis=e=>{ const r=e.getBoundingClientRect(); if(!(r.width>1&&r.height>1)) return false; let n=e; while(n && n!==document.body){ const c=getComputedStyle(n); if(c.display==='none'||c.visibility==='hidden'||+c.opacity<0.05) return false; n=n.parentElement; } return true; };
  document.querySelectorAll('#scStudy img, #stPop img').forEach(im=>{ if(vis(im) && im.complete && im.naturalWidth===0) iss.push('그림깨짐 '+im.getAttribute('src')); });
  const scope=[S, document.getElementById('stPop')].filter(Boolean);
  scope.forEach(R=>R.querySelectorAll('button,.stOpt,.stPrompt,.stCard,img,.stTile,.stMsg,.zBan,.mdRow,.stWorld,.stWT,.stCheck,p,h2,h3').forEach(e=>{ if(!vis(e) || e.closest('.stTabs,.stSubs,.stAmb,.stCut')) return; const r=e.getBoundingClientRect(); if(r.right>W+2 || r.left<-2) iss.push('가로삐짐 '+desc(e)+' '+Math.round(r.left)+'~'+Math.round(r.right)); }));
  if(document.documentElement.scrollWidth>W+1) iss.push('페이지가로스크롤 '+document.documentElement.scrollWidth);
  const view=S.classList.contains('vLesson')?'lesson':S.classList.contains('vDone')?'done':S.classList.contains('vGram')?'gram':'path';
  if(view==='lesson'||view==='done'){ const o=S.scrollHeight-S.clientHeight; if(o>2) iss.push('세로스크롤 '+o+'px'); }
  const F=document.getElementById('stFoot');
  if(view==='lesson' && F && vis(F)){ const fr=F.getBoundingClientRect(); document.querySelectorAll('#stQ .stOpt, #stQ .stTile, #stQ button, #stQ .stPrompt, #stQ .stTalk').forEach(e=>{ if(!vis(e)) return; const r=e.getBoundingClientRect(); if(r.bottom>fr.top+3 && r.top<fr.bottom) iss.push('확인띠에가림 '+desc(e)); }); }
  scope.forEach(R=>R.querySelectorAll('button,.stOpt,b,span,small,.stWT').forEach(e=>{ if(!vis(e) || !e.textContent.trim()) return; const cs=getComputedStyle(e); if((cs.overflow==='hidden'||cs.overflowX==='hidden'||cs.textOverflow==='ellipsis') && e.scrollWidth>e.clientWidth+3) iss.push('글자잘림 '+desc(e)); }));
  const P=document.getElementById('stPop'); if(P && P.classList.contains('on') && P.firstChild){ const r=P.firstChild.getBoundingClientRect(); if(r.top<-1||r.bottom>H+1) iss.push('창이화면밖 '+Math.round(r.top)+'~'+Math.round(r.bottom)); }
  if(view!=='path'){ const bs=[...document.querySelectorAll('#scStudy button, #stPop button')].filter(vis).map(e=>[e,e.getBoundingClientRect()]);
    for(let i=0;i<bs.length;i++) for(let j=i+1;j<bs.length;j++){ const [a,ra]=bs[i],[b,rb]=bs[j]; if(a.contains(b)||b.contains(a)) continue; const ix=Math.max(0,Math.min(ra.right,rb.right)-Math.max(ra.left,rb.left)), iy=Math.max(0,Math.min(ra.bottom,rb.bottom)-Math.max(ra.top,rb.top)); const ar=Math.min(ra.width*ra.height, rb.width*rb.height); if(ix*iy>0.25*ar) iss.push('버튼겹침 '+desc(a)+' × '+desc(b)); } }
  return {view, iss}; }"""

SETUP = r"""([set, state])=>{ localStorage.setItem('hyeng_nick','한양패드1'); const s=Study.load(); const bk=Study.bookOf ? Study.bookOf(set) : null;
  s.book=Object.keys(Study.BOOKS).find(b=>Study.BOOKS[b].sets.indexOf(set)>=0)||'g34'; s.set=set; s.lv={}; s.ck={}; s.d1={}; s.last={};
  const L=Study.lessons(set), x=L[0], k=Study.key(set,x.n);
  if(state==='t4'){ s.lv[k]=1; } if(state==='t2'){ s.lv[k]=1; s.ck[k]=1; } if(state==='t3'){ s.lv[k]=3; s.ck[k]=1; }
  if(state==='v1') s.lv[k]=1; if(state==='v2') s.lv[k]=2;
  if(state==='path'){ L.slice(0,2).forEach(y=>s.lv[Study.key(set,y.n)]=1); s.last[set]=L[1] ? L[1].n : x.n; }
  Study.save(); StudyUI._sel=null; StudyUI.open(); try{ KidPick.close(); }catch(e){}
  const fi=L.findIndex(y=>y.fin); return {n:L.length, fi, tier:!!Study.tierLes(set,x), book:s.book}; }"""

async def main(set_, state, vpn, out):
    os.makedirs(out, exist_ok=True)
    vp = {"phone": (390, 844), "pad": (820, 1180)}[vpn]
    tag0 = f"{set_}_{state}_{vpn}"
    rep = {"set": set_, "state": state, "vp": vpn, "shots": [], "errs": [], "404": []}
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await br.new_page(viewport={"width": vp[0], "height": vp[1]})
        pg.on("pageerror", lambda e: rep["errs"].append(str(e)[:200]))
        pg.on("response", lambda r: (r.status >= 400 and r.url.startswith(ORIGIN) and not r.url.endswith(".js")) and rep["404"].append(r.url[len(ORIGIN):]))
        await boot(pg); E = pg.evaluate
        info = await E(SETUP, [set_, state]); rep["info"] = info; await pg.wait_for_timeout(1100)
        await E("()=>{ try{ KidPick.close(); }catch(e){} }")
        n = [0]
        async def shot(name, full=False):
            n[0] += 1; fn = f"{tag0}_{n[0]:02d}_{name}.png"
            a = await E(AUDIT, name)
            await pg.screenshot(path=os.path.join(out, fn), full_page=False)
            rep["shots"].append({"f": fn, "name": name, "view": a["view"], "iss": a["iss"]})
        if state.startswith("gram"):
            # 📒 쉬어 가기: 길에서 첫 문법 돌 누르기 → 설명·확인 문제·문제를 끝까지 (처음 한 번은 틀림)
            import importlib.util
            spec = importlib.util.spec_from_file_location("g386", os.path.join(os.path.dirname(os.path.abspath(__file__)), "gram386.py")); g = importlib.util.module_from_spec(spec)
            src = open(spec.origin, encoding="utf-8").read(); ANS = src.split('ANS = """', 1)[1].split('"""', 1)[0]
            if state == "gram2": await E("()=>{ const g=Gram.list(StudyUI.book)[0]; Gram.save && 0; }")
            ok = await E("()=>{ const b=document.querySelector('#scStudy [data-gram]'); if(!b) return false; b.click(); return true; }")
            if not ok: rep["skip"] = "no gram"
            await pg.wait_for_timeout(700); await shot("문법_시작")
            sig = set(); wrong = 0
            for k in range(120):
                st = await E("()=>{ const U=GramUI, q=U.cur&&U.cur(); return [U.mode, U.tier, q&&q.k, !!U.ck, q&&q.res, StudyUI._v, !!document.querySelector('#stGram [data-gr=chk]'), !!document.querySelector('#stGram [data-gr=cnext]'), !!document.querySelector('#stGram [data-gr=qnext]'), !!document.querySelector('#stGram [data-gr=go]')]; }")
                if st[5] != "stGram": break
                key = (st[0], st[2], st[3])
                if key not in sig: sig.add(key); await shot("문법_" + "_".join(str(x) for x in key))
                if st[0] == "quiz" or st[3]:
                    w = wrong < 1 and st[4] is None
                    await E(ANS, w); await pg.wait_for_timeout(300)
                    if w: wrong += 1; await shot("문법_틀림")
                    if st[3]:
                        if await E("()=>!!document.querySelector('#stGram [data-gr=uncheck]')"): await E("()=>document.querySelector('#stGram [data-gr=uncheck]').click()"); await E(ANS, False); await pg.wait_for_timeout(200)
                    for b in ("qnext", "cnext"):
                        if await E(f"()=>{{ const b=document.querySelector('#stGram [data-gr={b}]'); if(b){{ b.click(); return true; }} return false; }}"): break
                elif st[6]: await E("()=>document.querySelector('#stGram [data-gr=chk]').click()")
                elif st[7]: await E("()=>document.querySelector('#stGram [data-gr=cnext]').click()")
                elif st[9]: await E("()=>document.querySelector('#stGram [data-gr=go]').click()")
                else:
                    await shot("문법_끝"); break
                await pg.wait_for_timeout(250)
        elif state == "path":
            await E("()=>{ document.getElementById('scStudy').scrollTop=0; }"); await pg.wait_for_timeout(300); await shot("길_위")
            await E("()=>{ const n=document.querySelector('#scStudy .stDot.now'); if(n) n.scrollIntoView({block:'center'}); }"); await pg.wait_for_timeout(300); await shot("길_지금")
            await E("()=>{ const S=document.getElementById('scStudy'); S.scrollTop=S.scrollHeight; }"); await pg.wait_for_timeout(400); await shot("길_끝")
            # 단추들 하나씩 (누른 뒤 캡처 → 다시 길 화면)
            BTN = [("Stage누름", "#scStudy .stDot[data-i='1']"), ("마지막시험누름", "#scStudy .stWN.fin .stDot, #scStudy .mdRow.mdFin"), ("쉬어가기", "#scStudy [data-gram]"),
                   ("미션", "#dmStrip"), ("복습상자", "#scStudy [data-rv], #scStudy .cpRv button"), ("주간시험", "#scStudy .stWeek"), ("확인할단어", "#scStudy .stChkB"),
                   ("문법노트", "#scStudy [data-gnote]"), ("이어하기", "#scStudy [data-resume]"), ("다른책", "#scStudy .stSubB:not(.on)")]
            for nm, sel in BTN:
                ok = await E("(sel)=>{ const b=document.querySelector(sel); if(!b) return false; b.scrollIntoView({block:'center'}); b.click(); return true; }", sel)
                if not ok: continue
                await pg.wait_for_timeout(800); await shot(nm)
                # 열린 창 안의 단추도 한 번
                if nm in ("미션",):
                    await E("()=>{ const b=[...document.querySelectorAll('.dmIn button, #dmView button')].find(x=>x.offsetParent); if(b) b.click(); }"); await pg.wait_for_timeout(500); await shot(nm + "_안")
                await E("()=>{ document.querySelectorAll('.modal.on, .dmView.on').forEach(m=>m.classList.remove('on')); try{ DM.close&&DM.close(); }catch(e){} try{ StudyUI.pop(null); }catch(e){} try{ StudyUI.path(); }catch(e){} }"); await pg.wait_for_timeout(500)
        else:
            idx = info["fi"] if state == "fin" else 0
            if idx < 0: rep["skip"] = "no fin"; await br.close(); return rep
            await E(f"()=>{{ StudyUI.start({idx},false); }}"); await pg.wait_for_timeout(900)
            await shot("시작")
            seen = {}; wrong = 0; hint = 0
            for k in range(220):
                st = await E("()=>{ const U=StudyUI, q=U.qs[U.i]; return [q&&q.t, U.i, U.qs.length, StudyUI._v, U.locked, !!document.getElementById('stIdk'), U._brk?1:0]; }")
                if st[3] != "stLesson": break
                t = st[0]
                if not st[4] and t not in seen:
                    seen[t] = 1; await shot("문제_" + str(t))
                    if st[5] and hint < 2:
                        await E("()=>document.getElementById('stIdk').click()"); await pg.wait_for_timeout(400); await shot("힌트_" + str(t)); hint += 1
                        # 힌트로 바뀐 판 다시 읽음
                if not st[4] and t not in ("intro",) and wrong < 3 and seen.get(t) == 1:
                    seen[t] = 2
                    r = await E(SOLVE, True); await pg.wait_for_timeout(500)
                    lk = await E("()=>StudyUI.locked")
                    if lk: await shot("틀림_" + str(t)); wrong += 1
                    continue
                r = await E(SOLVE, False); await pg.wait_for_timeout(180)
                if r == "brk": await pg.wait_for_timeout(300)
                if k == 6: await pg.wait_for_timeout(200);
                if await E("()=>StudyUI._brk?1:0"): await shot("쉬는시간")
            await pg.wait_for_timeout(1800)
            v = await E("()=>StudyUI._v")
            if v == "stDone":
                await shot("끝화면")
                ok = False
                for _w in range(10):
                    ok = await E("()=>{ const b=document.querySelector('#stDone [data-chest]'); if(!b) return false; b.click(); return true; }")
                    if ok: break
                    await pg.wait_for_timeout(500)
                if not ok: rep["noChest"] = await E("()=>document.getElementById('stDoneIn').innerHTML.length")
                if ok: await pg.wait_for_timeout(1600); await shot("상자연뒤")
                await E("()=>{ const S=document.getElementById('scStudy'); S.scrollTop=S.scrollHeight; }"); await pg.wait_for_timeout(300)
                await shot("끝화면_아래")
            else:
                rep["noDone"] = v
        await br.close()
    with open(os.path.join(out, tag0 + ".json"), "w") as f: json.dump(rep, f, ensure_ascii=False, indent=1)
    return rep

if __name__ == "__main__":
    r = asyncio.run(main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]))
    bad = sum(len(s["iss"]) for s in r["shots"])
    print(f'{sys.argv[1]} {sys.argv[2]} {sys.argv[3]}: 캡처 {len(r["shots"])} · 문제 {bad} · 오류 {len(r["errs"])} · 404 {len(set(r["404"]))}' + (f' · 끝 안남({r.get("noDone")})' if r.get("noDone") else ''))
