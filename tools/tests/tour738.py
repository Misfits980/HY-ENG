"""(v738) 🧭 화면 투어 — 사용자: 「점검 도구들도 예전 것들 오류 없는지 체크하고 새로 만들거나 해야 해」
   휴대폰 · 패드 세로 · 패드 가로 · TV 에서 첫 화면의 보이는 단추를 하나씩 눌러 열리는 창·화면마다 본다:
   ① 콘솔 오류 · 페이지 오류  ② 옆으로 넘침(가로 스크롤)  ③ 열린 창 안 단추가 화면 옆으로 잘림  ④ 위아래로 화면 밖인데 굴릴 수도 없는 단추
   + 선생님 관리 창 탭 전부 · Daily 30 문제 화면 · 미션 창 · 이달의 나
   결과: 문제 목록(없으면 통과) · 사진 out/tour/<기기>_<번호>.png · 「python3 tour738.py [phone pad lpad tv]」"""
import asyncio, sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

VPS = {"phone": (390, 844, True), "pad": (820, 1180, True), "lpad": (1180, 820, True), "tv": (1920, 1080, False)}
SHOT = os.path.join(OUT, "tour"); os.makedirs(SHOT, exist_ok=True)
# 누르면 다른 페이지로 가거나 판이 시작되는 단추 — 투어에서 뺌 (따로 시험이 있음)
SKIP = re.compile(r"마을|My Town|타운|달리기 시작|출발|▶ 시작|게임 시작|btnGo|btnTown|전체 화면|⛶")
RESET = """()=>{ try{ document.querySelectorAll('.sheet.on').forEach(s=>s.classList.remove('on')); }catch(e){}
  try{ ['dmView','monCard','monMt','wgView','lb4Menu','lrPanel'].forEach(id=>{ const e=document.getElementById(id); if(e) e.remove(); }); document.querySelectorAll('.rdJoin').forEach(e=>e.remove()); }catch(e){}
  try{ if(typeof StudyUI!=='undefined' && document.getElementById('scStudy').classList.contains('on')) StudyUI.close(); }catch(e){}
  try{ show('scStart'); }catch(e){} try{ window.scrollTo(0,0); }catch(e){} }"""
BTNS = """()=>{ const vis=e=>{ const r=e.getBoundingClientRect(), s=getComputedStyle(e); return r.width>4 && r.height>4 && s.visibility!=='hidden' && s.display!=='none' && r.bottom>0 && r.top<innerHeight && r.right>0 && r.left<innerWidth; };
  return [...document.querySelectorAll('#scStart button, #scStart [data-go], #scStart .mItem')].filter(vis).map((e,i)=>{ e.dataset.tourI=i; return [i, (e.id||'')+' '+(e.textContent||'').replace(/\\s+/g,' ').trim().slice(0,24)]; }); }"""
CHECK = """()=>{ const W=innerWidth, H=innerHeight, out={ox:document.documentElement.scrollWidth-W, layer:'', side:[], below:[]};
  /* 맨 위 층 = 화면 가운데를 누르면 닿는 것 (pointer-events:none 인 장식 층은 건너뜀) → body 바로 밑 조상 */
  let hit=document.elementFromPoint(W/2, H*0.45); while(hit && hit.parentElement && hit.parentElement!==document.body) hit=hit.parentElement;
  const sh=[...document.querySelectorAll('.sheet.on')].pop(), sc=document.querySelector('.screen.on'), ov=hit;
  const L=ov || sh || sc; out.layer=L ? (L.id||L.className.split(' ')[0]) : '';
  if(!L) return out;
  const scrollable=e=>{ for(let p=e.parentElement; p && p!==document.body; p=p.parentElement){ const s=getComputedStyle(p); if(/(auto|scroll)/.test(s.overflowY) && p.scrollHeight>p.clientHeight+2) return true; } return document.documentElement.scrollHeight>H+2; };
  for(const b of L.querySelectorAll('button')){ const r=b.getBoundingClientRect(), s=getComputedStyle(b); if(r.width<=2 || r.height<=2 || s.visibility==='hidden' || s.display==='none') continue;
    let hid=false, hs=false; for(let p=b.parentElement; p && p!==L; p=p.parentElement){ const q=getComputedStyle(p); if(q.display==='none' || q.visibility==='hidden' || (q.overflowX==='hidden' && (r.right<p.getBoundingClientRect().left || r.left>p.getBoundingClientRect().right))){ hid=true; break; }
      if(/(auto|scroll)/.test(q.overflowX) && p.scrollWidth>p.clientWidth+2) hs=true; } if(hid) continue;   /* 옆으로 미는 줄(탭 줄 등) 안이면 잘린 게 아님 */
    const t=(b.textContent||b.getAttribute('aria-label')||b.className||'').replace(/\\s+/g,' ').trim().slice(0,20);
    if(!hs && (r.right>W+1 || r.left<-1)) out.side.push(t+' '+Math.round(r.left)+'~'+Math.round(r.right));
    else if((r.top>=H || r.bottom<=0) && !scrollable(b)) out.below.push(t+' '+Math.round(r.top)); }
  out.side=out.side.slice(0,4); out.below=out.below.slice(0,4); return out; }"""

async def main():
    want = [a for a in sys.argv[1:] if a in VPS] or list(VPS)
    probs = []; n = 0; tot = 0
    async with async_playwright() as p:
        br = await p.chromium.launch()
        for vp in want:
            w, h, touch = VPS[vp]
            ctx = await br.new_context(viewport={"width": w, "height": h}, service_workers="block", is_mobile=touch, has_touch=touch)
            await ctx.add_init_script("window.HY_FB_LOCAL=true; window.confirm=()=>false; window.alert=()=>{};")
            pg = await ctx.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append("page: " + str(e)[:160]))
            pg.on("console", lambda m: errs.append("console: " + m.text[:160]) if m.type == "error" else None)
            await boot(pg); E = pg.evaluate
            await E("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); try{ Voice.speak=()=>{}; }catch(e){} }"); await E(RESET); await pg.wait_for_timeout(600)
            base = await pg.evaluate("()=>location.href"); n = 0   # 사진 번호는 기기마다 1부터
            async def look(name):
                nonlocal n, tot
                await pg.wait_for_timeout(800); n += 1; tot += 1
                try: c = await E(CHECK)
                except Exception as e: c = {"err": str(e)[:100]}
                e = real_errs(errs); errs.clear()
                bad = []
                if e: bad.append("오류 " + " | ".join(e[:2]))
                if c.get("ox", 0) > 1: bad.append("옆으로 넘침 %dpx" % c["ox"])
                if c.get("side"): bad.append("단추 옆으로 잘림 %s" % c["side"])
                if c.get("below"): bad.append("화면 밖 단추(굴릴 수 없음) %s" % c["below"])
                tag = "%s_%02d" % (vp, n)
                try: await pg.screenshot(path=os.path.join(SHOT, tag + ".png"))
                except Exception: pass
                print(("BAD " if bad else "OK  ") + "%s %-28s [%s] %s" % (tag, name[:28], c.get("layer", "?"), " · ".join(bad)), flush=True)
                if bad: probs.append("%s %s: %s" % (vp, name, " · ".join(bad)))
            # ① 첫 화면 단추 하나씩
            await look("첫 화면")
            L = await E(BTNS)
            for i, label in L:
                if SKIP.search(label): continue
                await E(RESET); await pg.wait_for_timeout(250); await E(BTNS)
                try:
                    await E("(i)=>{ const b=document.querySelector('[data-tour-i=\"'+i+'\"]'); if(b) b.click(); }", i)
                except Exception: pass
                await pg.wait_for_timeout(300)
                if (await pg.evaluate("()=>location.href")) != base:   # 다른 페이지로 갔으면 돌아오기
                    print("    → 다른 페이지로 감 · 돌아옴", flush=True); await boot(pg); await E("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); }"); continue
                await look("단추 " + label)
            # ② 정해 둔 화면들
            await E(RESET)
            for name, js in [("Daily 30 길", "()=>StudyUI.open()"), ("Daily 30 문제", "()=>{ StudyUI.open(); StudyUI.start(0,false); }"),
                             ("미션 창", "()=>DM.view()"), ("이달의 나", "()=>MonthCard.open()")]:
                await E(RESET); await pg.wait_for_timeout(250)
                try: await E(js)
                except Exception as e: probs.append("%s %s: 열기 실패 %s" % (vp, name, str(e)[:80])); continue
                await look(name)
            # ③ 선생님 관리 창 탭 전부
            await E(RESET)
            await E("()=>{ sessionStorage.setItem('hyeng_admin_ok', String(Date.now())); sessionStorage.setItem('hyeng_admin_tk','testkey'); }")
            await pg.reload(); await settle(pg, 900)   # 관리 잠금은 켤 때 봄
            await E("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); document.querySelectorAll('.sheet.on').forEach(s=>s.classList.remove('on')); Admin.open(); }"); await pg.wait_for_timeout(1200)
            tabs = await E("()=>[...document.querySelectorAll('#adTabs [data-t]')].map(b=>b.dataset.t)")
            for t in tabs:
                await E("(t)=>document.querySelector('#adTabs [data-t=\"'+t+'\"]').click()", t)
                await look("관리 탭 " + t)
            await ctx.close()
        await br.close()
    print("== 화면 %d개 · 문제 %d개" % (tot, len(probs)))
    for x in probs: print("  - " + x)
    print("BAD: %d" % len(probs)); sys.exit(1 if probs else 0)

asyncio.run(main())
