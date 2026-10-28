"""(v440) 🎲 보드게임 — 관리자 화면에서만 시범 + 끝까지 돌려 보기 (사용자: "관리자 모드에만 구현시켜 놔 줘 · 오류 없는지 점검")
  ① 아이 첫 화면: 보드게임 카드 = 「🔧 점검 중」 (사용자: "애들한테 보이게 하는데 서비스 점검 중") · 눌러도 안 열림 · 관리자 🎮 지금 수업에 「🎲 영어 파티 보드 시범」 → 누르면 관리자 닫히고 설정 화면
  ② 🪑 한 패드: 2·4·8명 · 두 판 모양(e·k) · 문제 시간 있음/없음 — 봇이 끝까지 (멈춤 없음 · 오류 없음 · 순위·💎)
  ③ 📺 TV + 각자 패드 4대: 로비 → 시작 → 패드에서 차례·문제·미니게임 → 끝 · 패드에 순위
  ④ 점검(다른 눈 검토)으로 고친 것: 함정을 못 놓는 자리 → 카드 다시(멈춤 X) · 모두 한 팀이면 시작 못 함 · TV 새로고침 = 패드에 끝 알림 · 미니게임 팀 점수 = 낸 사람만 · 안 들어온 아이 차례 4초"""
import asyncio, sys, os, time
TVONLY = os.environ.get("HY_TVONLY") == "1"   # 📺 TV + 패드 4대는 가짜 3D 로 (진짜 3D TV 가 CPU 를 다 써서 패드가 안 열림)
if not TVONLY: os.environ["HY_REAL3D"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

BOT = r"""()=>{ clearInterval(window.__bot); window.__be=[]; window.__sig=''; window.__sigT=Date.now();
  window.__bot=setInterval(()=>{ try{ const o=Board.o; if(!o) return; if(o.fin){ window.__done=1; return; }
    const sig=[o.cur, o.rnd, o.P.map(p=>p.pos+':'+p.coin+':'+p.star).join(','), ($('bdAct')||{}).innerHTML||'', MG.o ? 'mg'+JSON.stringify(MG.o.sc)+MG.o.qi+':'+MG.o.won : ''].join('|');
    if(sig!==window.__sig){ window.__sig=sig; window.__sigT=Date.now(); }
    if(MG.o){ const m=MG.o; if(m.inst && m.inst.length){ m.inst.forEach(g=>{ if(Math.random()<0.45) try{ g.auto(); }catch(e){ window.__be.push('auto '+e); } }); }
      else { const bs=[...document.querySelectorAll('#bdMG [data-mg]')].filter(b=>!b.disabled); if(bs.length && Math.random()<0.5) bs[Math.floor(Math.random()*bs.length)].dispatchEvent(new PointerEvent('pointerdown',{bubbles:true, cancelable:true})); } return; }
    const q=o.q, os=[...document.querySelectorAll('#bdAct .bdO')];
    if(q && !q.done && os.length){ const i=q.opts.findIndex((x,k)=>Board.right(q,k)); (Math.random()<0.7 && i>=0 ? os[i] : os[Math.floor(Math.random()*os.length)]).click(); return; }
    const bs=[...document.querySelectorAll('#board [data-bd]')].filter(b=>b.offsetParent && !b.disabled && !/^(x|quit|setup|again|del|add|ch|rng|mgtry|go|say)$/.test(b.dataset.bd));
    if(bs.length){ const r=bs.find(b=>b.dataset.bd==='roll'); (r && Math.random()<0.8 ? r : bs[Math.floor(Math.random()*bs.length)]).click(); }
  }catch(e){ window.__be.push(String(e && e.stack || e).slice(0,200)); } }, 280); }"""

PADBOT = r"""()=>{ clearInterval(window.__pb); window.__be=[];
  window.__pb=setInterval(()=>{ try{ const B=document.getElementById('bpBody'); if(!B) return;
    if(BoardPad.g){ if(Math.random()<0.5) BoardPad.g.auto(); return; }
    const bs=[...B.querySelectorAll('[data-bd]')].filter(b=>b.offsetParent && !b.disabled && !/^(x|quit|say)$/.test(b.dataset.bd));
    const ans=bs.filter(b=>b.classList.contains('bdO')); const s=BoardPad.st||{}, rq=s.req, q=rq && rq.q;
    if(ans.length){ let k=-1; try{ if(q) k=q.opts.findIndex((x,i)=>MG.right(q,i)); }catch(e){} const pick=(k>=0 && Math.random()<0.7) ? ans.find(b=>+b.dataset.i===k || +b.dataset.k===k) : null; (pick||ans[Math.floor(Math.random()*ans.length)]).click(); return; }
    if(bs.length){ const r=bs.find(b=>b.dataset.bd==='roll'); (r||bs[Math.floor(Math.random()*bs.length)]).click(); }
  }catch(e){ window.__be.push(String(e).slice(0,200)); } }, 350); }"""

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m, flush=True)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        NM = "루아 주호 라언 수아 단우 경훈 서원 지후".split()
        if not TVONLY:
          # ① 관리자에만
          c0 = await br.new_context(viewport={"width": 1180, "height": 820}); await c0.add_init_script("window.HY_FB_LOCAL=true;")
          pg = await c0.new_page(); pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)
          r = await pg.evaluate("""async ()=>{ document.getElementById('btnGo').click(); await new Promise(z=>setTimeout(z,500)); const c=document.querySelector('#selRule [data-v=join]'); const vis=!!c && getComputedStyle(c).display!=='none' && c.offsetHeight>60;
              c.click(); await new Promise(z=>setTimeout(z,600)); const rj=document.querySelector('.rdJoin'); const out=[vis, c.innerText.replace(/\\n/g,' '), !!rj && rj.offsetHeight>0, !!document.getElementById('board'), !!document.querySelector('#selRule [data-v=board]')]; try{ RaidJoin.close(); }catch(e){} return out; }""")
          ok(r[0] and "수업 게임" in r[1] and r[2] and not r[3] and not r[4], f"① (v441) 첫 화면 🎮 수업 게임 카드 → 바로 이름·방 번호 창 {r}")
          r = await pg.evaluate("()=>{ StudyUI.open(); return !!document.querySelector('[data-raidjoin]'); }")
          ok(r is False, "① (v441) Daily 30 에서 ⚔️ 배틀·레이드 단추 빠짐")
          await pg.evaluate("()=>{ sessionStorage.setItem('hyeng_admin_ok', String(Date.now())); sessionStorage.setItem('hyeng_admin_tk', 'testkey'); }")
          await pg.reload(); await pg.wait_for_timeout(1500)
          await pg.evaluate("()=>{ document.querySelectorAll('.sheet.on').forEach(s=>s.classList.remove('on')); window.confirm=()=>true; Admin.open(); }"); await pg.wait_for_timeout(1200)
          await pg.evaluate("()=>Admin._tab('now')"); await pg.wait_for_timeout(1200)
          r = await pg.evaluate("()=>{ const b=document.querySelector('[data-ad=bdTry]'); return b ? [b.innerText.replace(/\\n/g,' '), b.getBoundingClientRect().height] : null; }")
          ok(r and "영어 파티 보드" in r[0] and r[1] >= 44, f"① 관리자 🎮 지금 수업: 🎲 영어 파티 보드 시범 {r}")
          await pg.screenshot(path=OUT + "board440_admin.png")
          await pg.click('[data-ad="bdTry"]'); await pg.wait_for_timeout(900)
          r = await pg.evaluate("()=>[document.getElementById('shAdmin').classList.contains('on'), !!document.getElementById('bdSetup'), !!document.querySelector('[data-bd=go]')]")
          ok(r == [False, True, True], f"① 누르면 관리자 닫히고 보드 설정 화면 {r}")
          await pg.screenshot(path=OUT + "board440_setup.png")
          await pg.close()
          # ② 한 패드 끝까지
          FULL = os.environ.get("HY_FULL") == "1"   # 빠른 검사 = 2명 한 판 · 끝까지 검사(board440full) = 2·4·8명 + 📺 TV + 패드 4대
          for (n, sk, sec, vw) in ([(2, "e", 0, (430, 932)), (4, "k", 15, (1180, 820)), (8, "e", 0, (820, 1180))] if FULL else [(2, "e", 0, (430, 932))]):
              pg = await br.new_page(viewport={"width": vw[0], "height": vw[1]}); pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)
              P = [{"n": NM[i], "id": "", "ch": i} for i in range(n)]
              await pg.evaluate("(a)=>Board.begin({sk:a[1], set:'elem', from:0, to:3, qt:['mean','pic','spell'], sec:a[2], rounds:3, star:12, P:a[0]})", [P, sk, sec])
              await pg.evaluate(BOT); t0 = time.time(); stuck = None
              while time.time() - t0 < 900:
                  await pg.wait_for_timeout(2000)
                  s = await pg.evaluate("()=>[!!window.__done, Date.now()-window.__sigT, (window.__be||[]).slice(0,2), Board.o && Board.o.rnd]")
                  if s[0]: break
                  if s[1] > 45000: stuck = await pg.evaluate("()=>[Board.o && Board.o.cur, Board.o && Board.o.rnd, ($('bdAct')||{}).innerText, !!MG.o, document.getElementById('board') && document.getElementById('board').innerText.slice(0,200)]"); break
              el = round(time.time() - t0)
              r = await pg.evaluate("()=>[!!window.__done, (window.__be||[]).slice(0,3), Board.o && Board.o.P.map(p=>p.star+'⭐'+p.coin), (document.getElementById('board')||{}).innerText ? document.getElementById('board').innerText.indexOf('1')>=0 : false]")
              ok(r[0] and not r[1] and not stuck, f"② 한 패드 {n}명 · 판 {sk} · 문제 시간 {sec or '없음'}: 3라운드 끝까지 {el}초 · 봇 오류 {r[1]} · 멈춤 {stuck} · {r[2]}")
              await pg.screenshot(path=OUT + f"board440_end{n}.png")
              await pg.evaluate("()=>{ clearInterval(window.__bot); Board.close(); }"); await pg.close()
        # ③ TV + 패드 4대
        if TVONLY:
          ctx = await br.new_context(viewport={"width": 1280, "height": 720}, service_workers="block"); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
          T = await ctx.new_page(); T.on("pageerror", lambda e: errs.append("TV " + str(e))); await boot(T)
          await T.evaluate("()=>Board.setup()"); await T.wait_for_timeout(500)
          await T.evaluate("()=>{ const b=document.querySelector('[data-mode=tv]'); if(b) b.click(); const l=document.querySelector('[data-len=\"3\"]'); if(l) l.click(); }"); await T.wait_for_timeout(300)
          await T.evaluate("()=>document.querySelector('[data-bd=go]').click()"); await T.wait_for_timeout(1500)
          room = await T.evaluate("()=>BoardTV.room")
          ok(bool(room), f"③ 📺 방 {room}")
          K = []
          for i in range(4):
              k = await ctx.new_page(); k.set_default_navigation_timeout(120000); k.set_default_timeout(120000); k.on("pageerror", lambda e, i=i: errs.append(f"pad{i} " + str(e))); await boot(k)
              await k.evaluate("(a)=>BoardPad.join(a[0], {id:'k'+a[1], n:a[2], c:'hero'})", [room, i, NM[i]]); K.append(k)
          await T.wait_for_timeout(2500)
          r = await T.evaluate("()=>BoardTV.kids().length")
          ok(r == 4, f"③ 로비에 4명 {r}")
          await T.evaluate("()=>{ const b=document.getElementById('lbGo'); if(b) b.click(); else BoardTV.go(); }"); await T.wait_for_timeout(2500)
          ok(await T.evaluate("()=>!!(Board.o && Board.o.tv)"), "③ TV 판 시작")
          for k in K: await k.evaluate(PADBOT)
          await T.evaluate(BOT.replace("const q=o.q, os=", "if(o.tv) return; const q=o.q, os="))
          t0 = time.time(); stuck = None
          while time.time() - t0 < 1200:
              await T.wait_for_timeout(3000)
              s = await T.evaluate("()=>[!!(Board.o && Board.o.fin), Date.now()-window.__sigT]")
              if s[0]: break
              if s[1] > 70000: stuck = await T.evaluate("()=>[Board.o.cur, Board.o.rnd, ($('bdAct')||{}).innerText.slice(0,120), !!BoardTV.mgO, !!BoardTV.rq]"); break
          el = round(time.time() - t0)
          ok(not stuck and await T.evaluate("()=>!!(Board.o && Board.o.fin)"), f"③ 📺 TV + 패드 4대: 3라운드 끝까지 {el}초 · 멈춤 {stuck}")
          await T.screenshot(path=OUT + "board440_tv.png")
          await K[0].wait_for_timeout(3000)
          pe = []
          for k in K: pe += await k.evaluate("()=>window.__be||[]")
          txt = await K[0].evaluate("()=>(document.getElementById('bpBody')||{}).innerText||''")
          ok(not pe and ("1" in txt), f"③ 패드: 봇 오류 {pe[:2]} · 끝 화면 {txt[:60]!r}")
          await K[0].screenshot(path=OUT + "board440_pad.png")
        if not TVONLY:
          # ④ 고친 것 확인
          pg = await br.new_page(viewport={"width": 1180, "height": 820}); pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)
          await pg.evaluate("()=>Board.begin({sk:'e', set:'elem', from:0, to:3, qt:['mean'], sec:0, rounds:3, star:12, P:[{n:'루아',id:'',ch:0},{n:'주호',id:'',ch:3}]})")
          for _ in range(40):
              if await pg.evaluate("()=>!!document.querySelector('[data-bd=roll]')"): break
              await pg.wait_for_timeout(250)
          r = await pg.evaluate("""()=>{ const o=Board.o, p=Board.me(); p.it=['trap']; p.pos=0; Board.use('trap'); return [!!document.querySelector('#bdAct [data-bd=roll]'), p.it.length]; }""")
          ok(r == [True, 1], f"④ 출발 칸에서 🔒 함정 → 못 놓음 · 굴리기 카드가 다시 나옴 (멈춤 없음) {r}")
          await pg.evaluate("()=>Board.close()"); await pg.close()
          ctx = await br.new_context(viewport={"width": 1280, "height": 720}, service_workers="block"); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
          T = await ctx.new_page(); T.on("pageerror", lambda e: errs.append("TV2 " + str(e))); await boot(T)
          await T.evaluate("()=>BoardTV.host({sk:'e', set:'elem', from:0, to:3, qt:['mean'], sec:20, rounds:3})"); await T.wait_for_timeout(1500)
          room = await T.evaluate("()=>BoardTV.room")
          await T.evaluate("(r)=>{ ['a','b','c'].forEach((k,i)=>FB.update('/battle/'+r+'/p/'+k, {n:'아이'+i, c:'hero', at:Date.now()})); }", room); await T.wait_for_timeout(1500)
          r = await T.evaluate("()=>{ BoardTV.mode='team'; BoardTV.nT=2; BoardTV.tm={a:0,b:0,c:0}; BoardTV.lobby(); return [document.getElementById('lbGo').disabled, document.getElementById('lbMsg').textContent]; }")
          ok(r[0] and "두 팀" in r[1], f"④ 👥 모두 한 팀이면 시작 단추 꺼짐 {r}")
          r = await T.evaluate("()=>{ BoardTV.tm={a:0,b:1,c:0}; BoardTV.lobby(); return document.getElementById('lbGo').disabled; }")
          ok(r is False, "④ 두 팀으로 나누면 시작 가능")
          r = await T.evaluate("""async (r)=>{ TvRoom.save('board', r); const ok=await TvRoom.open(); await new Promise(z=>setTimeout(z,600)); const st=await FB.get('/battle/'+r+'/st'); return [ok, st && st.s, st && st.bye]; }""", room)
          ok(r[0] is False and r[1] == "end" and r[2] == 1, f"④ 📺 TV 새로고침 → 패드에 「끝났어요」 · 새로 만들게 {r}")
          await ctx.close()
        await br.close()
    real = real_errs(errs)
    ok(not real, f"오류 없음 {real[:4]}")
    print("DONE bad=%d" % len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
