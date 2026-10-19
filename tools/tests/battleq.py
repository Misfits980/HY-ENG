"""(v350) 교실 배틀(개인 레이스)·수업 레이드 문제 점검 — 사용자: 개인 레이스에서 갑자기 4줄 글이 나오고 답이 없음
  ① 학원 PC·옛 패드에서 이모지가 그림(<img class="emj">)으로 바뀐 단어 — 배틀 「그림 보고」·레이드 그림 보기에 코드 글이 아니라 그림으로
  ② 레이드 그림 문제 보기는 모두 그림 있는 단어 (빈 칸 없음) · 같은 그림 겹침 없음
  ③ 모든 책 · 모든 문제 종류: 정답이 보기에 있음 · 빈 보기 없음"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright

async def main():
    bad = []; errs = []
    def ok(c, m):
        print(("OK  " if c else "BAD ") + m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br = await p.chromium.launch(); pg = await br.new_page(viewport={"width": 390, "height": 844})
        pg.on("pageerror", lambda e: errs.append(str(e))); await boot(pg)
        E = pg.evaluate
        # ① 그림으로 바뀐 이모지 (EmojiFix 가 한 것처럼)
        await E("""()=>{ window._w=WORD_BANK.find(w=>w.en==='ant'); window._e0=_w.emoji; _w.emoji='<img class="emj" src="assets/emoji/1f41c.svg" alt="" draggable="false">'; }""")
        r = await E("""()=>{ const w=_w, o=WORD_BANK.filter(x=>x.emoji && x.en!=='ant').slice(0,3);
            Battle.role='kid'; Battle.room='9999'; Battle.me='k1'; Battle.pick={id:'k1', n:'민준'}; Battle.h=null; Battle._last={cfg:{set:'short', from:0, to:2, dur:300, qt:['pic']}, st:{s:'run', t0:Date.now()-1000}, p:{}};
            Battle.screen(); Battle.q={t:'pic', w, opts:[w].concat(o), lab:[w.en].concat(o.map(x=>x.en)), ans:0}; Battle.qAt=Date.now(); Battle.draw();
            const d=document.querySelector('.btPic'); return [!!(d && d.querySelector('img.emj')), document.getElementById('rdIn').innerText.indexOf('<img')>=0]; }""")
        ok(r == [True, False], f"배틀 그림 보고: 그림으로 보임 · 코드 글 없음 {r}")
        await E("()=>{ Battle.role=null; Battle.q=null; clearInterval(Battle.t); }")
        r = await E("""()=>{ const w=_w, o=WORD_BANK.filter(x=>x.emoji && x.en!=='ant' && x.emoji.indexOf('<')<0).slice(0,2);
            Raid.role='kid'; Raid.screen(); Raid._st0=Raid.st; Raid.st=()=>({s:'run'}); Raid.q={t:'pic', w, opts:[w].concat(o)}; Raid.atk=null; Raid.ended=false; Raid.restTo=0;
            try{ Raid.drawKid(); }catch(e){ return ['ERR', String(e)]; }
            const b=[...document.querySelectorAll('#rdOpts .stOpt')]; return [b.length, b.some(x=>x.querySelector('img.emj')), document.getElementById('rdIn').innerText.indexOf('<img')>=0]; }""")
        print("raid draw", r)
        ok(r[0] == 3 and r[1] and not r[2], f"레이드 그림 보기: 그림으로 보임 · 코드 글 없음 {r}")
        await E("()=>{ _w.emoji=_e0; Raid.st=Raid._st0; Raid.role=null; Raid.q=null; }")
        # ② 레이드 그림 문제 보기 (유치원·파닉스 책 모든 단어)
        r = await E("""()=>{ const out={n:0, pic:0, empty:[], dupe:[], miss:[]}; const sets=Study.BOOKS.k.sets;
            sets.forEach(set=>{ const ws=[]; Study.lessons(set).forEach(x=>x.ws.forEach(w=>{ if(!ws.some(y=>y.en===w.en)) ws.push(w); }));
              Raid._pool=ws; Raid._set=set; Raid.again=[];
              ws.forEach(w=>{ for(const easy of [false,true]){ const q=Raid.mkQ(easy, w); out.n++; if(q.t!=='pic') continue; out.pic++;
                const labs=q.opts.map(o=>o.emoji); if(labs.some(x=>!x)) out.empty.push([set,w.en]); if(new Set(labs).size<labs.length) out.dupe.push([set,w.en]);
                if(!q.opts.some(o=>o.en===w.en)) out.miss.push([set,w.en]); } }); });
            Raid._pool=null; return out; }""")
        ok(r["pic"] > 100 and not r["empty"] and not r["dupe"] and not r["miss"], f"레이드 그림 문제 {r['pic']}개: 빈 보기 {len(r['empty'])} · 같은 그림 {len(r['dupe'])} · 정답 없음 {len(r['miss'])} {r['empty'][:3]}")
        # ③ 배틀 — 모든 책 · 모든 문제 종류
        r = await E("""()=>{ const out={n:0, bad:[], empty:[]}; const sets=[].concat(...Object.keys(Study.BOOKS).filter(k=>k!=="ph").map(k=>Study.BOOKS[k].sets));
            const QT=Object.keys(Battle.QT).filter(k=>k!=="lsn");
            sets.forEach(set=>{ let L=[]; try{ L=Study.lessons(set); }catch(e){ return; }
              for(let a=0;a<L.length;a+=4){ Battle._ws=null; Battle.h=null; Battle.q=null; Battle._last={cfg:{set, from:a, to:Math.min(L.length-1,a+2), qt:QT}, st:{}};
                for(let r=0;r<12;r++){ const q=Battle.mkQ(); out.n++; Battle.q=q; const labs=q.opts.map((o,k)=>q.lab ? q.lab[k] : q.t==="e2k" ? o.ko : o.en);
                  if(!(q.ans!=null ? (q.ans>=0 && q.ans<q.opts.length) : q.opts.some(o=>o.en===q.w.en))) out.bad.push([set,q.t,q.w.en]);
                  if(labs.some(x=>x==null || x==="")) out.empty.push([set,q.t,q.w.en]); } } });
            Battle._last=null; Battle.q=null; return out; }""")
        ok(r["n"] > 2000 and not r["bad"] and not r["empty"], f"배틀 문제 {r['n']}개: 정답 없음 {len(r['bad'])} · 빈 보기 {len(r['empty'])} {r['bad'][:3]}")
        e = real_errs(errs); ok(not e, "오류 없음 " + str(e[:3]))
        await br.close()
    print("결과:", "통과" if not bad else "실패 " + str(bad))
asyncio.run(main())
