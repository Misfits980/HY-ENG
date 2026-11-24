"""(v721) 🌐 연결 재기 — 사용자: 「게임이 끊기기도 하고 렉이 너무 심해 · 다른 게임들을 만들 때 아이들이 힘들 것 같아서」 (서버를 옮기기 전에 숫자로)
   ① guard.js: 게임 중(HY_NETTAG)에만 20초마다 서버까지 시간·화면 fps · 페이지마다 한 번 서울/싱가포르 참고 → 게임이 바뀌면 한 줄(k:"net")
   ② 게임 화면 이름: 교실 배틀·레이드·보드 × 패드/TV · 게임 밖 = 안 잼
   ③ 마을: 섬 · 오락실 게임 이름
   ④ err.html 「🌐 연결」 칸: 보통/느릴 때 · 서울이면 · 화면 속도 · 오류 목록에는 안 섞임
   ⑤ 자동 시험(HY_NETMON 없음)은 안 잼"""
import asyncio, sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from draw635 import boot as hboot
from playwright.async_api import async_playwright
from fakefb import fake
bad=[]
def ok(c,m):
    print(("OK  " if c else "BAD ")+m, flush=True)
    if not c: bad.append(m)
DELAY={"firebasedatabase.app":.12, "ap-northeast-2":.02, "ap-southeast-1":.08}
async def pings(pg, slow=None):
    async def h(route):
        u=route.request.url; d=next((v for k,v in DELAY.items() if k in u), .05)
        await asyncio.sleep(d); await route.fulfill(status=401 if "firebase" in u else 200, body="x", headers={"access-control-allow-origin":"*"})
    await pg.route("**/.json?shallow=true*", h); await pg.route("**/ping?*", h)
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(); errs=[]   # 게임·err.html = 보통 브라우저 (swiftshader 면 화면 갱신이 1fps 로 떨어져 잰 값이 엉터리)
        # ⑤ 자동 시험 = 안 잼
        ctx=await br.new_context(viewport={"width":820,"height":1180}); await ctx.add_init_script("window.HY_NETMS=800;")
        pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)[:200])); await boot(pg); await pings(pg)
        await pg.evaluate("()=>{ window.HY_NETTAG=()=>'교실 배틀 · 패드'; }"); await pg.wait_for_timeout(2500)
        r=await pg.evaluate("()=>[!!GUARD.net.S, GUARD.sent.filter(x=>x.k==='net').length]")
        ok(r==[False,0], f"⑤ 자동 시험(HY_NETMON 없음)은 안 잼 {r}")
        await ctx.close()
        # ①② 게임
        ctx=await br.new_context(viewport={"width":820,"height":1180}); await ctx.add_init_script("window.HY_NETMON=1; window.HY_NETMS=900;")
        pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)[:200])); await boot(pg); await pings(pg); E=pg.evaluate
        r=await E("()=>HY_NETTAG()")
        ok(r=="", f"② 게임 밖(첫 화면) = 안 잼 「{r}」")
        await E("()=>{ window._nt0=window.HY_NETTAG; window._tg='교실 배틀 · 패드'; window.HY_NETTAG=()=>window._tg; window.HY_NETD=3; }")
        for _ in range(40):
            s=await E("()=>GUARD.net.S && GUARD.net.S.r.length")
            if s and s>=3: break
            await pg.wait_for_timeout(500)
        await E("()=>{ window.HY_NETD=5; window._tg=''; }")
        for _ in range(20):
            n=await E("()=>GUARD.sent.filter(x=>x.k==='net')")
            if n: break
            await pg.wait_for_timeout(400)
        rec=n[0] if n else {}
        ok(bool(n) and rec.get("m")=="교실 배틀 · 패드" and 110<=rec.get("rtt",0)<=260 and 0<=rec.get("sel",-1)<=80 and 60<=rec.get("sg",-1)<=160 and rec.get("fb3",0)>=110 and rec.get("drop")==2 and rec.get("fps") is not None and rec.get("n",0)>=2,   # fps 값은 머리 없는 브라우저에서 들쭉날쭉 (실제 숫자는 nmdbg 로 30fps 확인)
           f"① 한 판 한 줄: 서버 {rec.get('rtt')}ms(느릴 때 {rec.get('p90')}) · 서울 {rec.get('sel')} · 싱가포르 {rec.get('sg')} · 지금 서버 가장 빠른 {rec.get('fb3')} · fps {rec.get('fps')}/{rec.get('fpsMin')} · 끊김 {rec.get('drop')} · {rec.get('n')}번")
        r=await E("()=>{ const s0=GUARD.sent.length; return new Promise(res=>setTimeout(()=>res([!!GUARD.net.S, GUARD.sent.length-s0]), 2500)); }")
        ok(r==[False,0], f"① 게임이 끝나면 더 안 잼 {r}")
        await E("()=>{ window.HY_NETTAG=window._nt0; }")
        tags=await E("""()=>{ const out=[]; const B0=Battle.role, R0=Raid.role;
            Battle.role='host'; out.push(HY_NETTAG()); Battle.role='kid'; out.push(HY_NETTAG()); Battle.role=B0;
            Raid.role='host'; out.push(HY_NETTAG()); Raid.role='kid'; out.push(HY_NETTAG()); Raid.role=R0;
            BoardPad.room='1234'; out.push(HY_NETTAG()); BoardPad.room=null; return out; }""")
        ok(tags==["교실 배틀 · TV","교실 배틀 · 패드","레이드 · TV","레이드 · 패드","파티 보드 · 패드"], f"② 이름 {tags}")
        await ctx.close()
        # ③ 마을 (진짜 3D)
        os.environ["HY_REAL3D"]="1"
        br3=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        ctx2,hp,he=await hboot(br3,"루아","NM721A"); errs+=he
        await hp.evaluate("()=>{ window.HY_NETMON=1; }")
        r1=await hp.evaluate("()=>HY_NETTAG()")
        await hp.evaluate("()=>MG.enter('card',{})")
        for _ in range(40):
            if await hp.evaluate("()=>!!(MG.on && MG.run)"): break
            await hp.wait_for_timeout(200)
        r2=await hp.evaluate("()=>HY_NETTAG()")
        await hp.evaluate("()=>{ try{ HOUSE.enterRoom && HOUSE.enterRoom(); }catch(e){} }")
        ok(r1=="마이타운 섬" and r2=="오락실 · 컬러팡", f"③ 마을: 「{r1}」 · 「{r2}」")
        await ctx2.close(); await br3.close(); os.environ.pop("HY_REAL3D", None)
        # ④ err.html
        ctx=await br.new_context(viewport={"width":1280,"height":900}); pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)[:200]))
        now=int(time.time()*1000)
        recs={"a":{"k":"net","m":"교실 배틀 · 패드","p":"game","v":"v721","d":"iPad 15 · 사파리 15 · 768×1024 · 코어 4","w":"K1","t":now-60000,"sec":300,"n":15,"rtt":95,"p90":180,"mx":420,"fail":0,"fb3":88,"sel":12,"sg":75,"fps":24,"fpsMin":11,"jank":9,"drop":1},
              "b":{"k":"net","m":"교실 배틀 · TV","p":"game","v":"v721","d":"Windows · 크롬 131 · 1920×1080 · 코어 8","w":"","t":now-50000,"sec":300,"n":15,"rtt":70,"p90":110,"mx":200,"fail":0,"fb3":66,"sel":9,"sg":61,"fps":60,"fpsMin":58,"jank":0,"drop":0},
              "c":{"k":"err","m":"TypeError: x is undefined","p":"game","v":"v721","d":"iPad","w":"K2","t":now-40000}}
        async def fb(route):
            u=route.request.url
            if "/hy/day/er" in u: await route.fulfill(status=200, body=json.dumps(recs if u.split("/hy/day/er")[1][:8]==time.strftime("%Y%m%d", time.gmtime(time.time()+9*3600)) else None), headers={"content-type":"application/json","access-control-allow-origin":"*"})
            else: await route.fulfill(status=200, body="null", headers={"content-type":"application/json","access-control-allow-origin":"*"})
        await pg.route("**/*", fake); await pg.route("**/*firebasedatabase.app/**", fb); await pg.route("**/*firebaseio.com/**", fb)
        await pg.goto(ORIGIN+"err.html"); await pg.wait_for_timeout(2500)
        r=await E2(pg)
        ok(r[0]==2 and "보통 " in r[1] and "서울 서버였다면" in r[1] and "약 76ms 빨라짐" in r[1] and "30fps 아래 1번" in r[1] and r[2]==1 and "연결" not in r[3] and r[4]==2, f"④ err.html 「🌐 연결」 줄 {r[0]} · 오류 목록 {r[2]}묶음 · {r[1][:160]}")
        await pg.screenshot(path=OUT+"nm721_err.png", full_page=True)
        await ctx.close()
        ok(not real_errs(errs), f"JS 오류 없음 {real_errs(errs)[:3]}")
        await br.close()
    print("DONE bad=%d" % len(bad)); sys.exit(1 if bad else 0)
async def E2(pg):
    return await pg.evaluate("()=>[document.querySelectorAll('#net tr').length-1, (document.getElementById('net').innerText||'').replace(/\\s+/g,' '), document.querySelectorAll('#list .it').length, document.getElementById('list').innerText, +(([...document.querySelectorAll('#sum div')].pop()||{}).querySelector ? [...document.querySelectorAll('#sum div')].pop().querySelector('b').textContent : 0)]")
asyncio.run(main())
