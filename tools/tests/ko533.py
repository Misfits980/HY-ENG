"""(v533) 쓰러진 그림 — Daily 30 배틀 띠 마지막 한 방(25마리) · 주간 보스 쓰러짐(길 카드 · 첫 화면 고리 · 보스 화면 · 달리기 끝 칸)
python3 ko533.py <outdir>"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright
OUTD = sys.argv[1] if len(sys.argv) > 1 else OUT
SETUP = r"""([set])=>{ localStorage.setItem('hyeng_nick','한양패드1'); const s=Study.load(); s.book=Object.keys(Study.BOOKS).find(b=>Study.BOOKS[b].sets.indexOf(set)>=0); s.set=set; s.lv={}; Study.save(); StudyUI._sel=null; StudyUI.open(); try{ KidPick.close(); }catch(e){} }"""
KO = r"""(k)=>{ const U=StudyUI, B=document.getElementById('stBt'), m=Object.assign(U.mon(k), {ar:'forest'}); U._bm=m;
  B.className='stBt ar-forest'+(m.flip?' flipM':'')+(k==='knight'?' bigM':'')+(m.atk?' hasAtk':'')+' mk-'+k; B.style.setProperty('--mon','url('+m.img+')'); B.style.setProperty('--atk', m.atk?'url('+m.atk+')':'none');
  U.done=U.total; U.bt(true); return [U.done, U.total]; }"""
BOSS = r"""(img)=>{ const now=Date.now(); HyBoss.on=()=>true; HyBoss.refresh=()=>Promise.resolve(); HyBoss.ok=true;
  HyBoss.B={id:'wbk'+img, n:'테스트 보스', img, max:{all:1000}, hp:{all:0}, dead:{all:{by:'민준', t:now}}, start:now-86400000, end:now+3*86400000};
  HyBoss.D={}; return HyBoss.state('all'); }"""
async def main():
    os.makedirs(OUTD, exist_ok=True); errs = []; miss = []
    async with async_playwright() as p:
        br = await p.chromium.launch()
        for vpn, vp in {"phone": (390, 844), "pad": (820, 1180)}.items():
            pg = await br.new_page(viewport={"width": vp[0], "height": vp[1]})
            pg.on("pageerror", lambda e: errs.append(str(e)[:200]))
            pg.on("response", lambda r: (r.status >= 400 and r.url.startswith(ORIGIN) and not r.url.endswith(".js")) and miss.append(r.url[len(ORIGIN):]))
            await boot(pg); E = pg.evaluate
            await E(SETUP, ["elem"]); await pg.wait_for_timeout(900); await E("()=>{ try{ KidPick.close(); }catch(e){} }")
            await E("()=>StudyUI.start(0,false)"); await pg.wait_for_timeout(900)
            ks = await E("()=>Object.keys(StudyUI.HAVE)")
            for k in (ks if vpn == "phone" else ks[:3]):
                await E(KO, k); await pg.wait_for_timeout(1300)
                st = await E("()=>{ const B=document.getElementById('stBt'), M=B.querySelector('.bM'), r=M.getBoundingClientRect(), R=B.getBoundingClientRect(); return [B.classList.contains('ko'), getComputedStyle(M).backgroundImage.slice(-30), Math.round(r.left), Math.round(r.right), Math.round(r.top), Math.round(r.bottom), Math.round(R.right), Math.round(R.top)]; }")
                if not st[0] or 'ko_' not in st[1] or st[3] > st[6] + 1 or st[4] < st[7] - 1: errs.append(f"KO {vpn} {k} {st}")
                el = await pg.query_selector("#stBt"); await el.screenshot(path=os.path.join(OUTD, f"bt_{vpn}_{k}.png"))
            # fit1 (작은 화면)
            await E("()=>{ document.getElementById('scStudy').classList.add('fit1'); }"); await E(KO, "overlord"); await pg.wait_for_timeout(1200)
            el = await pg.query_selector("#stBt"); await el.screenshot(path=os.path.join(OUTD, f"bt_{vpn}_fit1.png"))
            await E("()=>{ document.getElementById('scStudy').classList.remove('fit1'); }")
            # 다음 판 시작하면 원래대로
            await E("()=>StudyUI.btIdle()"); r = await E("()=>document.getElementById('stBt').classList.contains('ko')")
            if r: errs.append("btIdle 뒤에도 ko 남음")
            await E("()=>{ try{ StudyUI.close(); }catch(e){} }")
            for img in (["hb3", "hb1", "hb4"] if vpn == "phone" else ["hb5"]):
                st = await E(BOSS, img)
                # 길 카드
                await E(SETUP, ["elem"]); await pg.wait_for_timeout(700); await E("()=>{ try{ KidPick.close(); }catch(e){} StudyUI.bossCard(); }"); await pg.wait_for_timeout(300)
                await E("()=>{ const c=document.querySelector('#stBossCard'); if(c) c.scrollIntoView({block:'center'}); }"); await pg.wait_for_timeout(300)
                bc = await pg.query_selector("#stBossCard")
                src = await E("()=>{ const i=document.querySelector('#stBossCard img'); return i? i.getAttribute('src'):'' }")
                if 'ko_' not in src: errs.append(f"길 카드 {img} {src}")
                if bc and await bc.is_visible(): await bc.screenshot(path=os.path.join(OUTD, f"card_{vpn}_{img}.png"))
                # 보스 화면
                await E("()=>{ try{ StudyUI.close(); }catch(e){} try{ WeekBoss.open(); }catch(e){ console.error(e); } }"); await pg.wait_for_timeout(1600)
                src = await E("()=>{ const i=document.querySelector('#wbStage .rsBossIn img'); return i? i.getAttribute('src')+' '+document.getElementById('wbStage').className:'(없음)' }")
                if 'ko_' not in src: errs.append(f"보스 화면 {img} {src}")
                await pg.screenshot(path=os.path.join(OUTD, f"wb_{vpn}_{img}.png"))
                await E("()=>{ try{ WeekBoss.close(); }catch(e){} }"); await pg.wait_for_timeout(300)
                # 첫 화면 고리
                await E("()=>{ try{ show('scStart'); }catch(e){} try{ WeekBoss.banner(); }catch(e){ console.error(e); } }"); await pg.wait_for_timeout(500)
                src = await E("()=>{ const i=document.querySelector('#hbBan .hbRing img'); return i? i.getAttribute('src'):'(없음)' }")
                if 'ko_' not in src: errs.append(f"첫 화면 고리 {img} {src}")
                hb = await pg.query_selector("#hbBan")
                if hb and await hb.is_visible(): await hb.screenshot(path=os.path.join(OUTD, f"ring_{vpn}_{img}.png"))
        await br.close()
    print("ERRS", len(errs)); [print(" ", e) for e in errs]
    print("404", sorted(set(miss)))
asyncio.run(main())
