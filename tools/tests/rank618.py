# v618 🏆 랭킹 · 🏛 명예의 전당 · 점수 규칙 · 내 기록 · 켤 때 발표 (가짜 board 데이터)
import asyncio, sys
sys.path.insert(0, "/home/claude/hy-eng/tools/tests")
from harness import *
from playwright.async_api import async_playwright
DATA = r"""()=>{ const mk=a=>a.map(([n,t,s,mv,ch,x])=>Object.assign({nick:n, tag:t, score:s, mv, ch}, x||{}));
  const study=mk([["빈","0012",2140,0,"hero",{n:11,st:3}],["라언","0009",1890,1,"archer",{n:12}],["김지후","0007",1720,-1,"mage",{n:9}],["주호","0011",1510,0,"explorer",{n:8}],["스트로베리","0008",1320,2,"wolf",{n:14}],["SEOWON","0017",860,1,"scholar",{n:4}],["루아","0014",820,-2,"ghost",{n:7}],["단우","0015",640,"new","cat",{n:5}],["유이홍","0016",500,0,"",{n:3}],["패트","0019",320,0,"knight",{n:2}]]);
  const words=mk([["이무이무시완","0013",88,0,"knight",{st:6}],["빈","0012",64,0,"hero"],["김지환","0018",51,1,"cat"],["스트로베리","0008",40,-1,"wolf"]]);
  const run=mk([["이무이무시완","0013",48952,0,"knight",{n:72,st:9}],["김지환","0018",22021,0,"cat",{n:56}],["스트로베리","0008",13730,0,"wolf",{n:50}],["김지후","0007",12297,1,"mage",{n:34}]]);
  const now=Date.now(), H9=9*3600e3, k=new Date(now+H9), back=(k.getUTCDay()+6)%7, ws=Date.UTC(k.getUTCFullYear(),k.getUTCMonth(),k.getUTCDate()-back)-H9;
  const cal=[0,1,2,3,4,5,6].map(i=>i>back?null:(i<2?{nick:"라언",tag:"0009"}:{nick:"빈",tag:"0012",now:i===back?1:0}));
  const hof={cal:{study:cal, words:cal.map(x=>x&&{nick:"이무이무시완",tag:"0013"}), run:cal.map(x=>x&&{nick:"이무이무시완",tag:"0013"})}, streak:{study:{nick:"빈",tag:"0012",n:3},words:{nick:"이무이무시완",tag:"0013",n:6},run:{nick:"이무이무시완",tag:"0013",n:9}},
    weeks:{study:[{key:"2026-10-26",top:[{nick:"빈",tag:"0012",score:2310},{nick:"라언",tag:"0009",score:2050},{nick:"주호",tag:"0011",score:1980}]},{key:"2026-10-19",top:[{nick:"김지후",tag:"0007",score:1980}]},{key:"2026-10-12",top:[{nick:"빈",tag:"0012",score:2050}]}],words:[],run:[]},
    longest:{study:[{nick:"빈",tag:"0012",n:5,end:"2026-10-24",now:0},{nick:"김지후",tag:"0007",n:4,end:"2026-10-31"},{nick:"빈",tag:"0012",n:3,end:"2026-11-06",now:1}],words:[],run:[]},
    medals:{study:[{nick:"빈",tag:"0012",g:2,s:1,b:0},{nick:"김지후",tag:"0007",g:1,s:2,b:0},{nick:"라언",tag:"0009",g:0,s:1,b:2}]},
    att:[{nick:"빈",tag:"0012",n:12},{nick:"스트로베리",tag:"0008",n:9},{nick:"라언",tag:"0009",n:8},{nick:"주호",tag:"0011",n:5}], lastKey:"2026-10-26", ch:{"#0011":"explorer","#0012":"hero","#0009":"archer","#0007":"mage","#0008":"wolf","#0013":"knight"}};
  const me={study:Object.assign({}, study[3], {rank:4, of:10, lv:"G3-4", above:{nick:"김지후",score:1720}, day:[300,420,0,370,420,0,0], ent:[["G3-4 Stage 5-1 ★3",300,"o",1],["G3-4 Stage 5-2",220,"o",2],["G3-4 Stage 5-1 ★3",280,"w",3],["G3-4 Stage 5-3 연습",0,"p",4]]}), hof:{last:{rank:3, of:14, score:1980}, medal:{g:0,s:1,b:2}, att:5}};
  document.getElementById('nick').value='주호'; try{ localStorage.setItem('hyeng_tag','0011'); }catch(e){}
  LiveRank.fetch=()=>{}; LiveRank.set({study, words, run, me, hof, ws});
  Online.top=(d,r)=>Promise.resolve(d==="study"?study.map(x=>({nick:x.nick,tag:x.tag,score:x.score*3,stage:x.n})):d==="dex"?words.map(x=>({nick:x.nick,tag:x.tag,score:x.score*15})):run.map(x=>({nick:x.nick,tag:x.tag,score:x.score,stage:x.n})));
}"""
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); errs=[]
        for nm,vw in (("ph",(390,844)),("pad",(820,1180))):
            pg=await br.new_page(viewport={"width":vw[0],"height":vw[1]}, device_scale_factor=2); pg.on("pageerror", lambda e: errs.append(str(e)[:300])); await boot(pg); E=pg.evaluate
            await E(DATA); await pg.wait_for_timeout(1700)
            await pg.screenshot(path=f"/tmp/claude-0/rank618_{nm}_ann.png")
            await E("()=>{ const d=document.getElementById('rkAnn'); if(d) d.remove(); }")
            for d,r in (("study","week"),("study","hof"),("study","all"),("dex","week"),("dex","all"),("run","week"),("run","all"),("run","hof")):
                await E("(a)=>{ RANK_VIEW.range=a[1]; showRank(a[0]); }", [d,r]); await pg.wait_for_timeout(500)
                await pg.screenshot(path=f"/tmp/claude-0/rank618_{nm}_{d}_{r}.png")
                if d=="study" and r=="hof":
                    await E("()=>{ const s=document.getElementById('scRank'); s.scrollTop=s.scrollHeight; }"); await pg.wait_for_timeout(200); await pg.screenshot(path=f"/tmp/claude-0/rank618_{nm}_hof2.png")
            await E("(a)=>{ RANK_VIEW.range='week'; showRank('study'); }"); await pg.wait_for_timeout(300)
            await E("()=>document.querySelector('[data-rkrule]').click()"); await pg.wait_for_timeout(300); await pg.screenshot(path=f"/tmp/claude-0/rank618_{nm}_rule.png")
            await E("()=>document.getElementById('rkSheet').remove()")
            await E("()=>document.querySelector('#scRank [data-rkmy]').click()"); await pg.wait_for_timeout(300); await pg.screenshot(path=f"/tmp/claude-0/rank618_{nm}_my.png")
            await pg.close()
        print("ERR", errs); await br.close()
asyncio.run(main())
