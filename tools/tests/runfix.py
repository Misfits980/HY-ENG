"""(v322) 달리기 결과·기록 점검 고침 — 책 달리기 뒤 틀린 단어만 · 공용 패드 내 순위 · 못 보낸 기록 모아 보내기 · 시험 주소 최고 기록 ·
   넘어지는 연출 중 멈춤 · 유치원/연습 줄 · 연습 문구 · Daily 30 다시 하기 · 쉬는 시간 · 책 최고 기록 · 아이별 짧은 판 · 저주 길 검사 · 단어판 캐시 · 자동 품질"""
import asyncio, os, sys, json
from playwright.async_api import async_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *

# 가짜 시트 서버 — window._net: 'ok' | 'down' | 'busy' | 'key'
NET = """()=>{ window._posts=[]; window._net='ok';
  const real=window.fetch.bind(window);
  window.fetch=(u,o)=>{ if(String(u).indexOf(Online.URL)!==0) return real(u,o);
    if(o && o.method==='POST'){ if(window._net==='down') return Promise.reject(new Error('offline'));
      const b=JSON.parse(o.body); if(window._net==='ok') window._posts.push(b);
      const j = window._net==='ok' ? {ok:true} : {ok:false, err:window._net};
      return Promise.resolve({json:()=>Promise.resolve(j)}); }
    return Promise.resolve({json:()=>Promise.resolve({ok:true, list:window._top||[]})}); };
  Online.top=()=>Promise.resolve(window._top||null); }"""
# 한 판 끝내기 (o = G 에 덮을 값)
END = """(o)=>{ startGame(); Object.assign(G, {right:6, wrong:2, score:1200, stage:20, zone:2, bestCombo:3, wrongWords:[{en:'apple',ko:'사과'}], quit:true}, o||{});
  G.running=false; G.skipOutro=true; G.overFade=false; G._overDone=false; gameOver(); G.skipOutro=false; return true; }"""

async def main():
    bad = []
    def chk(ok, name):
        if not ok: bad.append(name)
    async with async_playwright() as p:
        br = await p.chromium.launch(); errs = []
        ctx = await br.new_context(viewport={"width": 390, "height": 844})
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        await boot(pg); await pg.wait_for_timeout(300)
        await pg.evaluate(NET)

        # 1 🔴 책 달리기 뒤 '틀린 단어만 다시 풀기'
        await pg.evaluate("()=>{ ['apple','banana','school','friend','water','happy','teacher','window'].forEach(w=>WrongBook.add(w)); G.set='g56'; G.book='rd1'; G.tag=null; G.diff='normal'; G.rule='normal'; }")
        await pg.evaluate(END, {})
        await pg.wait_for_timeout(200)
        await pg.evaluate("()=>document.getElementById('btnReview').click()"); await pg.wait_for_timeout(200)
        a = await pg.evaluate("()=>{ const p=pool().map(w=>w.en), wl=WrongBook.list(); return {set:G.set, book:G.book, n:p.length, out:p.filter(e=>wl.indexOf(e)<0).length, ls:(LastSetup.get()||{}).book}; }")
        print("1 틀린 단어만", a); chk(a["set"] == "wrong" and a["book"] is None and a["n"] >= 6 and a["out"] == 0 and a["ls"] is None, "1 틀린 단어 다시")

        # 10 Daily 30 카드 판 → ▶ 다시 하기도 같은 단어
        await pg.evaluate("()=>{ G.set='elem'; G.book=null; G.lesson=0; G._nextWords=['apple','banana','school','friend','water','happy']; G._nextPractice=false; }")
        await pg.evaluate(END, {}); await pg.wait_for_timeout(100)
        await pg.evaluate("()=>document.getElementById('btnRetry').click()"); await pg.wait_for_timeout(200)
        r = await pg.evaluate("()=>({w:G.words, pr:G.practice, n:pool().length})")
        print("10 다시 하기", r); chk(r["w"] and len(r["w"]) == 6 and r["pr"] is True and r["n"] == 6, "10 다시 하기 같은 단어")

        # 9 · 8 연습 판 문구 + 시트 rule:practice / 유치원 rule:kinder
        await pg.evaluate("()=>{ G.set='elem'; G._nextWords=['apple','banana','school','friend','water','happy']; G._nextPractice=true; window._posts=[]; }")
        await pg.evaluate(END, {}); await pg.wait_for_timeout(300)
        r = await pg.evaluate("()=>({note:document.getElementById('oRank').innerText, rows:window._posts.map(b=>b.rule)})")
        print("9/8 연습", r); chk("연습 달리기는 랭킹에 안 올라가요" in r["note"], "9 연습 문구"); chk(r["rows"] == ["practice"], "8 연습 줄")
        await pg.evaluate("()=>{ G.set='kinder'; G.book=null; window._posts=[]; }")
        await pg.evaluate(END, {}); await pg.wait_for_timeout(300)
        r = await pg.evaluate("()=>({note:document.getElementById('oRank').innerText, rows:window._posts.map(b=>b.rule)})")
        print("8 유치원", r); chk("유치원" in r["note"] and r["rows"] == ["kinder"], "8 유치원 줄")

        # 12 책 최고 기록 — 난이도 최고가 높아도 그 책 기록과 비교
        await pg.evaluate("()=>{ Best.save('normal',{score:99999,stage:90,acc:100}); localStorage.setItem('hyeng_bookbest_v1', JSON.stringify({rd2:1000})); G.set='g56'; G.book='rd2'; }")
        await pg.evaluate(END, {"score": 1500}); await pg.wait_for_timeout(100)
        h1 = await pg.evaluate("()=>document.getElementById('oHighlight').innerText")
        await pg.evaluate("()=>{ G.book='rd2'; }")
        await pg.evaluate(END, {"score": 1200}); await pg.wait_for_timeout(100)
        h2 = await pg.evaluate("()=>document.getElementById('oHighlight').innerText")
        print("12 책 최고", h1, "|", h2); chk("리딩 2 최고 기록" in h1 and "최고 기록" not in h2, "12 책 최고 기록")

        # 3 인터넷이 끊기면 기기에 모았다가 다시 보냄 (short 는 줄에 담겼으니 다시 세지 않음)
        await pg.evaluate("()=>{ localStorage.removeItem('hyeng_sheetq'); window._net='key'; return Online.submit({nick:'X', score:1, diff:'normal', rule:'normal'}); }"); await pg.wait_for_timeout(200)
        q3 = await pg.evaluate("()=>JSON.parse(localStorage.getItem('hyeng_sheetq')||'[]').length")   # key·type 오류는 다시 보내도 안 되니 모으지 않음
        await pg.evaluate("()=>{ G.set='elem'; G.book=null; window._net='down'; window._posts=[]; localStorage.removeItem('hyeng_sheetq'); localStorage.setItem('hyeng_short_v1','2'); }")
        await pg.evaluate(END, {"score": 3100}); await pg.wait_for_timeout(400)
        q1 = await pg.evaluate("()=>({q:JSON.parse(localStorage.getItem('hyeng_sheetq')||'[]').map(x=>[x.b.score,x.b.short,!!x.b.key]), short:localStorage.getItem('hyeng_short_v1')})")
        await pg.evaluate("()=>{ window._net='busy'; }")
        await pg.evaluate(END, {"score": 3200}); await pg.wait_for_timeout(400)
        q2 = await pg.evaluate("()=>JSON.parse(localStorage.getItem('hyeng_sheetq')||'[]').map(x=>x.b.score)")
        await pg.evaluate("()=>{ window._net='ok'; window.dispatchEvent(new Event('online')); }"); await pg.wait_for_timeout(600)
        q4 = await pg.evaluate("()=>({q:localStorage.getItem('hyeng_sheetq'), sent:window._posts.map(b=>b.score)})")
        print("3 모아 보내기", q1, q2, q3, q4)
        chk(q1["q"] == [[3100, 2, True]] and q1["short"] == "0", "3 끊김 → 모음")
        chk(q2 == [3100, 3200] and q3 == 0, "3 busy 모음 / key 오류는 안 모음")
        chk(q4["q"] is None and q4["sent"] == [3100, 3200], "3 online 때 보냄")

        # 2 · 13 공용 패드 — 내 순위는 보낸 이름으로 · 짧은 판은 아이마다
        await pg.evaluate("""()=>{ localStorage.setItem('hyeng_nick','한양패드'); Kid.set({id:'k1',n:'민준'}); window._posts=[];
          window._top=[{nick:'👤서연',score:9000,me:true},{nick:'AAA',score:8000,me:false},{nick:'👤민준',score:7000,me:true},{nick:'👤지우',score:500,me:true}];
          localStorage.removeItem('hyeng_short_v1'); localStorage.removeItem('hyeng_short_v1_k1'); G.set='elem'; }""")
        await pg.evaluate(END, {"score": 7000}); await pg.wait_for_timeout(400)
        r = await pg.evaluate("()=>({my:(document.querySelector('#oRank .resMy')||{}).innerText, me:[...document.querySelectorAll('#oRank .rrow.me')].map(e=>e.innerText.replace(/\\n/g,' ')), nick:(window._posts[0]||{}).nick})")
        print("2 내 순위", r); chk(r["my"] == "내 순위 3위" and len(r["me"]) == 1 and "민준" in r["me"][0] and r["nick"] == "👤민준", "2 공용 패드 내 순위")
        await pg.evaluate(END, {"zone": 0}); await pg.wait_for_timeout(200)
        r = await pg.evaluate("()=>({k:localStorage.getItem('hyeng_short_v1_k1'), all:localStorage.getItem('hyeng_short_v1')})")
        print("13 짧은 판", r); chk(r["k"] == "1" and r["all"] is None, "13 아이별 짧은 판")
        await pg.evaluate("()=>{ localStorage.removeItem('hyeng_nick'); }")

        # 11 쉬는 시간은 '플레이(초)'에서 뺀다
        r = await pg.evaluate("""()=>{ G.set='elem'; startGame(); G.runStart=Date.now()-15000; togglePause(); G.pauseAt-=10000; togglePause(); return {secs:runReport().secs, pm:G.pauseMs}; }""")
        print("11 쉬는 시간", r); chk(4 <= r["secs"] <= 6, "11 쉬는 시간 빼기")

        # 5 넘어지는 연출(0.62초) 중 ⏸·Esc 는 안 멈춤 · 결과 화면에 '잠깐 쉬는 중' 없음
        await pg.evaluate("()=>{ G.set='elem'; startGame(); }"); await pg.wait_for_timeout(800)
        await pg.evaluate("()=>{ G.score=300; G.right=2; gameOver(); document.getElementById('pauseBtn').click(); }")
        await pg.keyboard.press("Escape"); await pg.wait_for_timeout(1000)
        r = await pg.evaluate("()=>({over:$('scOver').classList.contains('on'), pause:$('scPause').classList.contains('on'), paused:G.paused})")
        print("5 연출 중 멈춤", r); chk(r["over"] and not r["pause"] and not r["paused"], "5 연출 중 멈춤")

        # 7 저주 걸린 문제는 느린 걸음으로 길 검사 — 보통 걸음으로 통과한 함정 묶음에서 더 빼야 하는 문제가 생긴다 (가로 화면 7줄 · 어려움 75단계)
        await pg.set_viewport_size({"width": 844, "height": 390}); await pg.wait_for_timeout(200)
        r = await pg.evaluate("""()=>{ G.set='elem'; G.diff='hard'; startGame(); G.stage=75; applyZone(zoneIndex(75), false);
          let more=0, r1s=0, tries=0; const z=P.z-G.spawnDist, spd=G.spawnDist/approachTime(75);
          for(let i=0;i<120;i++){ Hazards.clear(); const hb=new Set(Hazards.list); const ans=i%G.lanes; Hazards.spawnFor(z, ans, spd);
            const nh=Hazards.list.filter(h=>!hb.has(h)); if(!nh.length) continue; tries++;
            if(Hazards.ensurePath(nh, z, ans, spd, 1)>0) r1s++; const left=Hazards.list.filter(h=>!hb.has(h)); if(Hazards.ensurePath(left, z, ans, spd, CURSE_SLOW.hard)>0) more++; }
          Hazards.clear(); return {lanes:G.lanes, tries, r1s, more}; }""")
        print("7 저주 길 검사", r); chk(r["tries"] > 0 and r["more"] > 0, "7 저주 길 검사")
        await pg.set_viewport_size({"width": 390, "height": 844}); await pg.wait_for_timeout(200)

        # 6 단어판 캔버스 다시 쓰기 · fitFont 가 예전과 같은 크기 · 자동 품질 낮춤
        r = await pg.evaluate("""()=>{ const t1=signTexture('BANANA'), t2=signTexture('BANANA'), t3=signTexture('APPLE');
          const old=(x,text,maxW,start,weight)=>{ let s=start; while(s>16){ x.font=weight+" "+s+"px 'Pretendard','Apple SD Gothic Neo','Malgun Gothic',system-ui,sans-serif"; if(x.measureText(text).width<=maxW) break; s-=4; } return s; };
          const x=document.createElement('canvas').getContext('2d'); let diff=[];
          ['A','CAT','BANANA','INTERNATIONAL','IN FRONT OF','잡고 있었다 (hold)','supercalifragilistic','✕','WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW'].forEach(w=>[348,200,57,18].forEach(st=>{
            const a=old(x,w,800,st,'800'), fa=x.font, b=fitFont(x,w,800,st,'800'), fb=x.font; if(a!==b || fa!==fb) diff.push([w,st,a,b]); }));
          return {same:t1.image===t2.image, other:t1.image!==t3.image, diff}; }""")
        print("6 단어판", r); chk(r["same"] and r["other"] and not r["diff"], "6 단어판 캐시 / fitFont")
        r = await pg.evaluate("""()=>{ Quality.save('mid'); FrameWatch.force=true; FrameWatch.reset(); let t=1000; for(let i=0;i<120;i++){ t+=40; FrameWatch.tick(t); }
          const keep=Quality.resolved(); Quality.level='auto'; Quality.autoLow=false; localStorage.removeItem(Quality.AKEY); FrameWatch.reset(); t=1000; for(let i=0;i<60;i++){ t+=16; FrameWatch.tick(t); }
          const fast=Quality.resolved(); for(let i=0;i<120;i++){ t+=40; FrameWatch.tick(t); }
          const r={keep, fast, slow:Quality.resolved(), saved:localStorage.getItem(Quality.AKEY), tip:(document.getElementById('trapTip')||{}).textContent||''};
          Quality.save('auto'); FrameWatch.force=false; return r; }""")
        print("6 자동 품질", r); chk(r["keep"] == "mid" and r["fast"] != "low" and r["slow"] == "low" and r["saved"] == "low" and "가볍게" in r["tip"], "6 자동 품질")
        e = real_errs(errs); print("errs", e)
        if e: bad.append("errors")
        await ctx.close()

        # 4 시험 주소(?stage=60) 판은 최고 기록·Expert 열기·판 수에 안 들어감 · 시트에도 안 보냄
        ctx = await br.new_context(viewport={"width": 390, "height": 844}); errs2 = []
        pg = await ctx.new_page(); pg.on("pageerror", lambda e: errs2.append(str(e)))
        await pg.route("**/*", route); await pg.goto(ORIGIN + "index.html?stage=60"); await pg.wait_for_timeout(1200)
        await pg.evaluate("()=>{ const b=document.getElementById('btnNewsOk'); if(b) b.click(); }")
        await pg.evaluate(NET)
        await pg.evaluate("()=>{ G.set='elem'; G.diff='hard'; G.rule='normal'; }")
        await pg.evaluate(END, {"score": 9000, "stage": 60}); await pg.wait_for_timeout(300)
        r = await pg.evaluate("()=>({ex:extremeOpen(), best:Best.get('hard'), games:Stats.all().games, hl:document.getElementById('oHighlight').innerText, posts:window._posts.length})")
        print("4 시험 주소", r); chk(not r["ex"] and not r["best"] and r["games"] == 0 and "최고 기록" not in r["hl"] and r["posts"] == 0, "4 시험 주소 기록")
        e = real_errs(errs2); print("errs", e)
        if e: bad.append("errors")
        if bad: print("BAD", bad)
        await br.close()
asyncio.run(main())
