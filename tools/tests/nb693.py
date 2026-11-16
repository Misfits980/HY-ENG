"""(v693) 🐻 이웃과 영어로 — 사용자: 「그래 너가 한번 해 봐라」 (claude/hy-eng-plan-town-study.md 1번)
   ① 오늘 「❗」 이웃 둘: 단어 하나 · 부탁 하나 (아이마다 같은 날 같은 둘)
   ② 이웃을 누르면 게임 대화창(#dlg) — 이름표에 하트 5칸 · 시간에 맞는 영어 인사
   ③ 단어 ❗: 오늘 오늘의 30 에서 처음 본 단어(rabbit) → 그림 3개 + 🔊 → 맞히면 🪙 +10 · 우정 +2 · ❗ 사라짐
   ④ 틀리면 「다시 해 봐」 → 두 번 틀리면 답을 알려 줌 (벌 없음)
   ⑤ 부탁 ❗: 그 이웃의 의뢰를 영어로 부탁 → 「Sure!」 = 의뢰 받기
   ⑥ 🎁 선물: 좋아하는 것(Tom 🥕) = 우정 +3 · 좋아하는 것 알게 됨 · 하루 한 번
   ⑦ 하트가 오르면 선물 (♥2 = 🪙 · ♥3 = 마당 가구)
   ⑧ 마을 시간 기록 = 아이 태그 (반 번호가 아님)"""
import asyncio, sys, os, json
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from fakefb import fake
from playwright.async_api import async_playwright

async def main():
    bad=[]; errs=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        ctx=await br.new_context(viewport={"width":820,"height":1180}, has_touch=True); pg=await ctx.new_page(); pg.set_default_timeout(150000)
        pg.on("pageerror", lambda e: errs.append(str(e)[:200]))
        await pg.route("**/*", fake); await pg.goto(ORIGIN+"proto/house.html?isle=1"); await pg.wait_for_timeout(400)
        await pg.evaluate("""()=>{ Object.keys(localStorage).filter(k=>k.startsWith('hyeng_')).forEach(k=>localStorage.removeItem(k)); const dn=Math.floor((Date.now()-new Date().getTimezoneOffset()*60000)/864e5);
            localStorage.setItem('hyeng_proto_code', JSON.stringify('QN693')); localStorage.setItem('hyeng_nick','루아'); localStorage.setItem('hyeng_dev','dQN693'); localStorage.setItem('hyeng_tag','#0042'); localStorage.setItem('hyeng_me', JSON.stringify({id:'kQN693', t:'A568'})); localStorage.setItem('hyeng_proto_tut', JSON.stringify({s:99})); localStorage.setItem('hyeng_isle_cam','1');
            localStorage.setItem('hyeng_study_v1', JSON.stringify({days:{n:4,tot:6,hs:4,hb:4,last:dn}, sd:{rabbit:dn, apple:dn-3}, srs:{rabbit:[1,dn+1]}})); }""")
        await pg.reload(); await pg.wait_for_timeout(2000)
        await pg.evaluate("()=>ISLE.enter()")
        for _ in range(200):
            if await pg.evaluate("()=>HOUSE.place()==='isle' && !HOUSE.trip().busy"): break
            await pg.wait_for_timeout(250)
        E=pg.evaluate
        # ① 오늘 ❗
        B=await E("()=>VIL.bangs()"); W=await E("()=>VIL.wordToday()")
        ok(B["wc"]!=B["fv"] and W and W["en"]=="rabbit" and len(W["opts"])==3 and any(o[0]=="rabbit" for o in W["opts"]), f"① ❗ 둘 = 단어 {B['wc']} · 부탁 {B['fv']} · 오늘 단어 {W and W['en']} 그림 {W and [o[2] for o in W['opts']]}")
        # 버섯 마을로
        await E("()=>{ const w=VIL.W()[0]; const p=w.c.g.position; TFAC.warp(p.x+1.5, p.z+1.5); }"); await pg.wait_for_timeout(1500)
        L=await E("()=>[...document.querySelectorAll('#tls .tl')].map(e=>e.textContent.trim()).filter(t=>/❗/.test(t))")
        ok(len(L)>=1, f"① 이름표에 ❗ {L}")
        # ② ③ 단어 이웃과 대화
        async def talk(id):
            await E("(id)=>VIL.talkNb(id)", id)
            for _ in range(60):
                if await E("()=>document.getElementById('dlg').classList.contains('on')"): break
                await pg.wait_for_timeout(200)
        async def until_choices(n=80):
            for _ in range(n):
                on=await E("()=>document.getElementById('dlgCh').classList.contains('on')")
                if on: return True
                await E("()=>{ const b=document.getElementById('dlgBox'); if(b) b.click(); }"); await pg.wait_for_timeout(250)
            return False
        c0=await E("()=>TECO.coins()")
        await talk(B["wc"])
        r=await E("()=>[document.getElementById('dlg').classList.contains('on'), document.getElementById('dlgName').textContent]")
        ok(r[0] and "♥" in r[1] or "♡" in r[1], f"② 대화창 · 이름표 하트 {r}")
        ok(await until_choices(), "③ 그림 고르기가 나옴")
        ch=await E("()=>[...document.querySelectorAll('#dlgCh .dch')].map(b=>[b.dataset.ch, b.textContent.trim(), b.className])")
        ok(len([c for c in ch if c[0].startswith('w:')])==3 and any(c[0]=="say" for c in ch) and all('pic' in c[2] for c in ch), f"③ 그림 3개 + 🔊 {ch}")
        f0=await E("(id)=>VIL.st().f[id]|0", B["wc"])
        # ④ 틀린 것 먼저
        wrong=[c[0] for c in ch if c[0].startswith('w:') and c[0]!="w:rabbit"][0]
        await E("(k)=>document.querySelector('#dlgCh [data-ch=\"'+k+'\"]').click()", wrong); await pg.wait_for_timeout(300)
        ok(await until_choices(), "④ 틀리면 다시 고르기")
        t=await E("()=>document.getElementById('dlgEn').textContent+' / '+document.getElementById('dlgKo').textContent")
        await E("()=>document.querySelector('#dlgCh [data-ch=\"w:rabbit\"]').click()"); await pg.wait_for_timeout(300)
        await until_choices()
        r=await E("(id)=>[TECO.coins(), VIL.st().f[id]|0, VIL.st().nb.wc[id], VIL.bangOf(id)]", B["wc"])
        ok(r[0]==c0+10 and r[1]>=f0+2 and r[2]==1 and r[3]=="", f"③ 맞힘 → 🪙 {c0}→{r[0]} · 우정 {f0}→{r[1]} · ❗ 사라짐 {r[2:]} (틀린 뒤 말: {t[:60]})")
        await E("()=>{ try{ closeTalk(); }catch(e){} }"); await pg.wait_for_timeout(300)
        # ⑤ 부탁
        await talk(B["fv"]); ok(await until_choices(), "⑤ 부탁 이웃 대화")
        ch=await E("()=>[...document.querySelectorAll('#dlgCh .dch')].map(b=>b.dataset.ch)")
        ok("fvY" in ch and "fvN" in ch, f"⑤ 「Sure! / Sorry」 {ch}")
        await E("()=>document.querySelector('#dlgCh [data-ch=\"fvY\"]').click()"); await pg.wait_for_timeout(500)
        r=await E("(id)=>{ const q=VIL.today().find(q=>q.who===id); return [!!(q && VIL.st().acc[q.id]), VIL.bangOf(id)]; }", B["fv"])
        ok(r[0] and r[1]=="", f"⑤ 의뢰를 받음 · ❗ 사라짐 {r}")
        await until_choices(); await E("()=>{ try{ closeTalk(); }catch(e){} }"); await pg.wait_for_timeout(300)
        # ⑥ 선물 (Tom 🥕)
        await E("()=>{ HOUSE.addMat('carrot', 2); }")
        await talk("tom"); ok(await until_choices(), "⑥ Tom 대화")
        ch=await E("()=>[...document.querySelectorAll('#dlgCh .dch')].map(b=>b.dataset.ch)")
        if "gift" not in ch:
            # Tom 이 ❗ 이웃이면 먼저 끝냄
            ok(False, f"⑥ 선물 고르기 없음 {ch}")
        else:
            fT=await E("()=>VIL.st().f.tom|0")
            await E("()=>document.querySelector('#dlgCh [data-ch=\"gift\"]').click()"); await pg.wait_for_timeout(300)
            for _ in range(60):
                if await E("()=>!!document.querySelector('#dlgSeeds.on [data-gift=\"m:carrot\"]')"): break
                await E("()=>{ const b=document.getElementById('dlgBox'); if(b) b.click(); }"); await pg.wait_for_timeout(250)
            await E("()=>document.querySelector('#dlgSeeds [data-gift=\"m:carrot\"]').click()"); await pg.wait_for_timeout(400)
            r=await E("()=>[VIL.st().f.tom|0, VIL.st().nb.gift.tom, (VIL.st().lk.tom||{}).carrot, VIL.nbList().find(x=>x.id==='tom').likes]")
            ok(r[0]>=fT+3 and r[1]==1 and r[2]==1, f"⑥ 🥕 좋아하는 선물 → 우정 {fT}→{r[0]} · 좋아하는 것 알게 됨 {r[3]}")
            await until_choices()
            ch=await E("()=>[...document.querySelectorAll('#dlgCh .dch')].map(b=>b.dataset.ch)")
            ok("gift" not in ch, f"⑥ 선물은 하루 한 번 {ch}")
        await E("()=>{ try{ closeTalk(); }catch(e){} }")
        # ⑦ 하트 선물
        r=await E("""()=>{ const s=VIL.st(); s.f.joe=7; s.lv.joe=1; const c=TECO.coins(); VIL.addF('joe', 1); const a=[VIL.lv('joe'), TECO.coins()-c]; const y0=(typeof ystock!=='undefined' && ystock.lantern)|0; VIL.addF('joe', 7); return a.concat([VIL.lv('joe'), ((typeof ystock!=='undefined' && ystock.lantern)|0)-y0]); }""")
        ok(r[0]==2 and r[1]==20 and r[2]==3 and r[3]==1, f"⑦ ♥2 = 🪙 20 · ♥3 = 🏮 마당 가구 {r}")
        # ⑧ 마을 시간 기록 태그
        r=await E("""()=>{ const sent=[]; const of=window.fetch; window.fetch=(u,o)=>{ try{ const b=JSON.parse(o&&o.body||'{}'); if(b.type==='mt') sent.push(b.tag); }catch(e){} return Promise.resolve(new Response('{}')); }; MTL.force=1; MTS.at=0; MTS.sent=''; try{ mtSheet({d:'2026-11-16', s:600, g:1}, true); }catch(e){ sent.push('err '+e); } window.fetch=of; return sent; }""")
        ok(r==["0042"], f"⑧ 마을 시간 태그 = 아이 태그 0042 (반 A568 아님) {r}")
        ok(not real_errs(errs), f"JS 오류 없음 {real_errs(errs)[:3]}")
        await br.close()
    print("DONE bad=%d"%len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
