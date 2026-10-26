"""(L0-10) 🏡 생활 맛보기 — 집 꾸미기 더(가전 9 · 벽에 거는 것 6 · 색 바꾸기 · 앉기/눕기 · 집 넓히기 · 🏅 꾸미기 도장 · 이름#번호 태그) + 👫 친구 · 🏠 놀러 가기
  사용자: "집도 꾸미는 재미를 더 · 가전제품 · 남의 집도 갈 수 있게 · 친구 추가하면 그 집에 갈 수 있게"
  서버는 가짜(Firebase REST 흉내, 이 파일 안 사전) — 두 아이(민준·서연 = 브라우저 둘)가 같은 서버를 씀"""
import asyncio, sys, os, json, re
from urllib.parse import urlparse, parse_qs, unquote
os.environ["HY_REAL3D"]="1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
from playwright.async_api import async_playwright
DB={}; LOG=[]
def getp(path):
    o=DB
    for k in [x for x in path.split("/") if x]:
        if not isinstance(o,dict) or k not in o: return None
        o=o[k]
    return o
def setp(path, v):
    P=[x for x in path.split("/") if x]; o=DB
    for k in P[:-1]: o=o.setdefault(k,{})
    if v is None: o.pop(P[-1],None)
    else: o[P[-1]]=v
async def fb(r):
    u=urlparse(r.request.url)
    if "firebasedatabase" not in u.netloc: return await route(r)
    path=unquote(u.path)[:-5] if u.path.endswith(".json") else unquote(u.path); m=r.request.method; LOG.append((m,path))
    if m=="GET":
        v=getp(path); q=parse_qs(u.query)
        if "orderBy" in q and isinstance(v,dict):
            key=json.loads(q["orderBy"][0]); items=list(v.items())
            if "equalTo" in q: eq=json.loads(q["equalTo"][0]); items=[(k,x) for k,x in items if isinstance(x,dict) and x.get(key)==eq]
            items.sort(key=lambda kv: (kv[1].get(key) if isinstance(kv[1],dict) else 0) or 0)
            if "limitToLast" in q: items=items[-int(q["limitToLast"][0]):]
            v=dict(items)
        return await r.fulfill(status=200, content_type="application/json", body=json.dumps(v))
    body=r.request.post_data; val=json.loads(body) if body else None
    if m=="PUT": setp(path,val)
    if m=="DELETE": setp(path,None); val=None
    return await r.fulfill(status=200, content_type="application/json", body=json.dumps(val))
async def main():
    bad=[]; errs=[]
    def ok(c,m):
        print(("OK  " if c else "BAD ")+m)
        if not c: bad.append(m)
    async with async_playwright() as p:
        br=await p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader"])
        async def kid(name, t, tag=""):
            ctx=await br.new_context(viewport={"width":390,"height":844}, is_mobile=True, has_touch=True)
            pg=await ctx.new_page(); pg.on("pageerror", lambda e: errs.append(name+": "+str(e)))
            await pg.route("**/*", fb); await pg.goto(ORIGIN+"proto/house.html"); await pg.wait_for_timeout(1500)
            await pg.evaluate("(a)=>{ Object.keys(localStorage).filter(k=>k.startsWith('hyeng_proto_')).forEach(k=>localStorage.removeItem(k)); localStorage.setItem('hyeng_kid', JSON.stringify({id:a[0], n:a[0], t:a[1]})); localStorage.setItem('hyeng_nick', a[0]); if(a[2]) localStorage.setItem('hyeng_tag', a[2]); }", [name, t, tag])
            await pg.reload(); await pg.wait_for_timeout(3500); return pg
        A=await kid("민준","A1","0006")
        async def until(pg, js, n=60):
            for _ in range(n):
                if await pg.evaluate(js): return True
                await pg.wait_for_timeout(250)
            return False
        # ① 가전 · 벽 · 색 · 앉기 · 넓히기 · 점수
        n=await A.evaluate("()=>Object.keys(HOUSE.PRICE).length"); ok(n==35, f"가게 물건 35가지 (가구 20 + 가전 9 + 벽 6) {n}")
        ok(await A.evaluate("()=>HOUSE.wplaced.length")==3, "처음 방: 창문 2 · 그림 1 (벽에 걸림)")
        await A.evaluate("()=>{ HOUSE.setGems(999); ['tank','fan','radio','washer','robot','poster','mirror'].forEach(id=>HOUSE.addStock(id)); }")
        await A.click("#bEdit"); await A.wait_for_timeout(200)
        for id in ["tank","fan","radio","washer","robot","poster","mirror"]:
            await A.click(f'.card[data-id="{id}"]'); await A.wait_for_timeout(150)
            if not await A.evaluate("()=>!document.getElementById('pOk').disabled"): await A.click("#pRot"); await A.wait_for_timeout(100)
            await A.click("#pOk"); await A.wait_for_timeout(150)
        ok(await A.evaluate("()=>['tank','fan','radio','washer','robot'].every(id=>HOUSE.placed.some(p=>p.id===id)) && HOUSE.wplaced.length===5"), "가전 5 놓기 · 벽에 포스터·거울 걸기")
        wp=await A.evaluate("()=>HOUSE.wplaced.map(p=>p.obj.parent===HOUSE.walls[p.side])")
        ok(all(wp), "벽 물건은 그 벽에 붙음 (벽이 안 보이면 같이 숨음)")
        await A.click("#bDone")
        r=await A.evaluate("""()=>{ const P=id=>HOUSE.placed.find(p=>p.id===id); HOUSE.useItem(P('fan')); HOUSE.useItem(P('radio')); HOUSE.useItem(P('washer')); HOUSE.robotGo(P('robot'));
            return {fan:P('fan').on, radio:P('radio').on, wash:P('washer').run>0, robot:(P('robot').route||[]).length>0}; }""")
        ok(all(r.values()), f"선풍기·라디오 켜기 · 세탁기 돌리기 · 로봇 청소 {r}")
        b0=await A.evaluate("()=>HOUSE.placed.find(p=>p.id==='fan').obj.userData.blades.rotation.z"); await A.wait_for_timeout(600)
        ok(await A.evaluate("()=>HOUSE.placed.find(p=>p.id==='fan').obj.userData.blades.rotation.z")!=b0, "선풍기 날개가 돎")
        await A.evaluate("()=>{ HOUSE.dex()['crab']=1; HOUSE.dex()['octopus']=1; HOUSE.dex()['fish']=1; const p=HOUSE.placed.find(p=>p.id==='tank'); HOUSE.rebuildP(p); }")
        ok(await A.evaluate("()=>HOUSE.placed.find(p=>p.id==='tank').obj.userData.fishG.children.length")==3, "🐠 어항 = 내가 잡은 물고기가 헤엄침")
        c0=await A.evaluate("()=>HOUSE.placed.find(p=>p.id==='bed').c|0")
        await A.click("#bEdit"); await A.wait_for_timeout(150)
        await A.evaluate("()=>HOUSE.selectP(HOUSE.placed.find(p=>p.id==='bed'))"); await A.wait_for_timeout(150)
        ok(await A.evaluate("()=>getComputedStyle(document.getElementById('mCol')).display!=='none'"), "놓인 가구 누르면 🎨 색 바꾸기 단추")
        await A.click("#mCol"); await A.wait_for_timeout(150); await A.click("#bDone")
        ok(await A.evaluate("()=>JSON.parse(localStorage.getItem('hyeng_proto_room')).p.find(x=>x[0]==='bed')[4]")==c0+1, "🎨 침대 색 바꾸기 → 저장")
        await A.evaluate("()=>HOUSE.sitOn(HOUSE.placed.find(p=>p.id==='bed'))")
        ok(await A.evaluate("()=>HOUSE.hero().act==='sleep' && HOUSE.hero().g.position.y>0.5"), "🛏 침대 누르면 누워 잠 💤")
        await A.evaluate("()=>HOUSE.walkTo(5,5)"); await until(A,"()=>!HOUSE.hero().moving")
        ok(await A.evaluate("()=>HOUSE.hero().act!=='sleep' && HOUSE.hero().g.position.y===0"), "걸으면 일어남")
        s0=await A.evaluate("()=>HOUSE.stamps().filter(x=>x[2]).length")
        await A.evaluate("()=>HOUSE.openFurn('up')"); await A.wait_for_timeout(200); await A.click('#furnBody [data-up="room"]'); await A.wait_for_timeout(400)
        ok(await A.evaluate("()=>HOUSE.RN()")==8 and await A.evaluate("()=>JSON.parse(localStorage.getItem('hyeng_proto_room')).rn")==8, "🏠 집 넓히기 6 → 8 (💎60) · 저장")
        s1=await A.evaluate("()=>HOUSE.stamps().filter(x=>x[2]).length"); ok(s1>s0 and await A.evaluate("()=>HOUSE.stamps().find(x=>x[0]==='big')[2]"), f"🏅 도장 늘어남 (넓은 집) {s0}→{s1}")
        await A.click("#furnDone")
        await A.evaluate("()=>HOUSE.openScore()"); await A.wait_for_timeout(200)
        st=await A.evaluate("()=>document.getElementById('scBody').innerText")
        ok("🏅" in st and "점" not in st and "★" not in st and await A.evaluate("()=>HOUSE.stamps().length")==14, "🏅 꾸미기 도장 14개 · 점수·별·감점 없음")
        await A.evaluate("()=>document.getElementById('scDone').click()")
        await A.reload(); await A.wait_for_timeout(3000)
        ok(await A.evaluate("()=>HOUSE.RN()===8 && HOUSE.wplaced.length===5 && HOUSE.placed.some(p=>p.id==='tank')"), "새로 열어도 넓은 집·벽 물건 그대로")
        # ② 🏘 마을 사람 집 (서버 없이도)
        await A.evaluate("()=>HOUSE.visitNpc('leo')"); await A.wait_for_timeout(1200)
        ok(await A.evaluate("()=>HOUSE.place()==='visit' && !!HOUSE.hostDoll() && HOUSE.placed.some(p=>p.id==='tank') && HOUSE.RN()===6"), "🏠 Leo 집에 놀러 감 (주인 인형 · 어항)")
        await A.evaluate("()=>HOUSE.useItem(HOUSE.placed.find(p=>p.id==='tank'))")
        ok(await A.evaluate("()=>HOUSE.placed.find(p=>p.id==='tank').fishE.length")==6, "Leo 어항엔 Leo 물고기")
        await A.evaluate("()=>{ const p=HOUSE.placed.find(p=>p.id==='bed'); HOUSE.useItem({id:'fridge', obj:p.obj}); }")
        ok("구경만" in await A.evaluate("()=>document.getElementById('toast').innerText"), "남의 집 냉장고는 못 열어요 (구경만)")
        ok(await A.evaluate("()=>{ document.getElementById('bEdit').click(); return !document.getElementById('drawer').classList.contains('on'); }"), "남의 집에선 가구 꾸미기 안 됨")
        await A.click("#bVLike"); await A.wait_for_timeout(200)
        ok("좋아요" in await A.evaluate("()=>document.getElementById('toast').innerText"), "❤️ 좋아요")
        await A.click("#bVLeave"); await A.wait_for_timeout(1000)
        ok(await A.evaluate("()=>HOUSE.place()==='room' && !HOUSE.visiting() && HOUSE.RN()===8 && HOUSE.placed.some(p=>p.id==='robot') && HOUSE.wplaced.length===5"), "🚪 나가기 → 내 집 그대로 돌아옴")
        # ③ 👫 친구 — 서연 집 코드로 요청 → 수락 → 놀러 가기 · 좋아요 · 스티커 · 우리 반
        B=await kid("서연","A1","0007")
        await B.evaluate("()=>{ HOUSE.setGems(200); HOUSE.addStock('piano'); }")
        await B.wait_for_timeout(500)
        codeA=await A.evaluate("()=>HOUSE.myCode()"); codeB=await B.evaluate("()=>HOUSE.myCode()")
        tagA=await A.evaluate("()=>HOUSE.ensureTag()"); tagB=await B.evaluate("()=>HOUSE.ensureTag()")
        ok(re.match(r"^\d{4}$", tagA) and re.match(r"^\d{4}$", tagB) and tagA=="0006" and tagB=="0007" and DB["hy"]["life"]["tag"][tagA]==codeA, f"게임 태그 그대로 (시트 서버가 준 번호) 민준#{tagA} · 서연#{tagB} (서버에 하나씩)")
        ok(DB["hy"]["life"]["kid"]["민준"]=={"c":codeA,"g":tagA}, "반 명단 아이 = 태그 하나 (kid/<id>)")
        await A.evaluate("()=>HOUSE.publish()"); await B.evaluate("()=>HOUSE.publish()")
        h=DB.get("hy",{}).get("life",{}).get("h",{})
        ok(codeA in h and h[codeA]["n"]=="민준" and h[codeA]["rn"]==8 and len(h[codeA]["wl"])==5, "내 집이 서버에 올라감 (이름 = 반 명단 이름)")
        await A.evaluate("()=>HOUSE.openFr()"); await until(A,"()=>/우리 반/.test(document.getElementById('frBody').innerText)")
        ok(("#"+tagA) in await A.evaluate("()=>document.getElementById('frBody').innerText"), "👫 시트에 내 이름#번호")
        ok("서연" in await A.evaluate("()=>document.getElementById('frBody').innerText"), "🏫 우리 반 집에 서연")
        ok("★" not in await A.evaluate("()=>document.getElementById('frBody').innerText"), "친구 목록에 별·점수 없음")
        await A.fill("#frCode", "#"+tagB+"9"); await A.wait_for_timeout(100)
        ok(await A.evaluate("()=>document.getElementById('frCode').value")==tagB, "번호 칸 = 숫자 4자리만")
        await A.click("#frSend"); await until(A,"()=>document.getElementById('ask').classList.contains('on')")
        ok(("서연#"+tagB) in await A.evaluate("()=>document.getElementById('askT').innerText"), "찾으면 '서연#번호 맞아요?' 확인")
        await A.click("#askOk"); await A.wait_for_timeout(500)
        ok(DB["hy"]["life"].get("req",{}).get(codeB,{}).get(codeA,{}).get("n")=="민준", "📮 친구 요청 → 서버")
        await B.evaluate("()=>HOUSE.openFr()"); await until(B,"()=>!!document.querySelector('#frBody [data-acc]')")
        await B.click('#frBody [data-acc]'); await B.wait_for_timeout(600)
        fr=DB["hy"]["life"].get("fr",{})
        ok(codeB in fr.get(codeA,{}) and codeA in fr.get(codeB,{}) and not DB["hy"]["life"].get("req",{}).get(codeB), "✅ 수락 → 둘 다 친구 · 요청 지움")
        await A.evaluate("()=>HOUSE.loadSocial().then(()=>HOUSE.drawFr())"); await A.wait_for_timeout(400)
        await A.click(f'#frBody [data-vis="{codeB}"]'); await until(A,"()=>HOUSE.place()==='visit'")
        await A.wait_for_timeout(800)
        ok(await A.evaluate("()=>HOUSE.visiting() && HOUSE.visiting().n==='서연' && HOUSE.RN()===6 && HOUSE.placed.some(p=>p.id==='chest')"), "🏠 서연 집에 놀러 감 (서연 방 모습)")
        mv=await A.evaluate("()=>{ const p=HOUSE.placed.find(p=>p.id==='chair'); return [p.x,p.z]; }")
        await A.click("#bVLike"); await A.wait_for_timeout(300)
        lk=DB["hy"]["life"].get("lk",{}).get(codeB,{})
        ok(lk.get(codeA)==await A.evaluate("()=>HOUSE.dayKey()"), "❤️ 좋아요 → 서버 (하루 한 번)")
        await A.click("#bVLike"); await A.wait_for_timeout(200)
        ok("벌써" in await A.evaluate("()=>document.getElementById('toast').innerText"), "같은 날 또 좋아요는 안 됨")
        await A.click("#bVStk"); await A.wait_for_timeout(200); await A.click('[data-stk="💖"]'); await A.wait_for_timeout(300)
        gb=list(DB["hy"]["life"].get("gb",{}).get(codeB,{}).values())
        ok(len(gb)==1 and gb[0]["e"]=="💖" and gb[0]["n"]=="민준", "🌟 스티커 방명록 💖")
        ok(await A.evaluate("()=>HOUSE.saveRoom() || JSON.parse(localStorage.getItem('hyeng_proto_room')).rn")==8, "놀러 간 동안 내 방 저장은 안 바뀜")
        await A.screenshot(path=OUT+"life_visit.png")
        await A.click("#bVLeave"); await A.wait_for_timeout(1000)
        ok(await A.evaluate("()=>HOUSE.place()==='room' && HOUSE.RN()===8"), "나가면 내 집")
        # 서연: 방명록 · 좋아요 보임
        await B.evaluate("()=>HOUSE.openFr()"); await until(B,"()=>/방명록/.test(document.getElementById('frBody').innerText)")
        t=await B.evaluate("()=>document.getElementById('frBody').innerText")
        ok("💖" in t and "민준" in t and "❤️" in t, "서연: 방명록 💖 민준 · ❤️ 좋아요 수")
        await B.screenshot(path=OUT+"life_friends.png")
        # ③-2 이름을 바꿔도 번호로 알아봄 · 새 기기에서 같은 아이 = 같은 번호·같은 집
        await B.evaluate("()=>{ localStorage.setItem('hyeng_kid', JSON.stringify({id:'서연', n:'딸기', t:'A1'})); return HOUSE.publish(); }")
        await A.evaluate("()=>HOUSE.loadSocial().then(()=>HOUSE.drawFr())"); await A.wait_for_timeout(400)
        t=await A.evaluate("()=>document.getElementById('frBody').innerText")
        ok(("딸기#"+tagB) in t, "서연 → 딸기로 이름을 바꿔도 같은 #번호로 보임")
        C=await kid("민준","A1","0006")
        ok(await C.evaluate("()=>HOUSE.myTag()")==tagA and await C.evaluate("()=>HOUSE.myCode()")==codeA and await C.evaluate("()=>HOUSE.RN()")==8 and await C.evaluate("()=>HOUSE.placed.some(p=>p.id==='tank')"), "새 기기에서 민준을 고르면 같은 #번호 · 내 집을 불러옴")
        # ④ 공용 패드 = 집을 올리지 않음
        await B.evaluate("()=>{ localStorage.setItem('hyeng_nick','한양패드'); }")
        ok(await B.evaluate("()=>HOUSE.kidInfo().shared") and not await B.evaluate("()=>HOUSE.publish()"), "👥 공용 패드는 내 집을 안 올림")
        # ⑤ 서버가 없으면 → 마을 사람 집만
        e=real_errs(errs); ok(not e, "오류 없음 "+str(e[:2]))
        await br.close()
    print("DONE bad=%d"%len(bad)); sys.exit(1 if bad else 0)
asyncio.run(main())
