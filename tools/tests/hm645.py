# v645 🏚 저택 탈출 (아오오니처럼) — 반 전체 한 저택 · 걸어 다니기 · 가구 뒤지기 → 모두의 📒 노트 · 층마다 퍼즐 3 + 🪜 계단 · 아이템 · 쪽지 · 🔵 아오(숨기·잡힘) · 늦게 온 아이 · ⭐ · 5화면
import asyncio, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *

OUT = os.environ.get("HY_OUT", "/tmp/hm645_")
bad = []
def ok(c, m):
    print(("OK  " if c else "BAD ") + m)
    if not c: bad.append(m)

GEN = """async (set)=>{ await Duel.ready(); const L=Study.lessons(set); const p=Esc.make({set, from:0, to:Math.min(5, L.length-1), lv:1, th:'house'}); const H=p.H, bad=[];
  if(!H || H.length!==3) return {bad:['H 없음']};
  H.forEach((Hz,z)=>{ const R=p.R[z], F=[].concat(...Hz.R.map((r,ri)=>r.F.map((f,s)=>Object.assign({ri, s}, f))));
    const st=F.filter(f=>f.st); if(st.length!==3 || new Set(st.map(f=>f.ri)).size!==3) bad.push(z+':퍼즐 3개 방마다 하나');
    R.P.forEach(q=>{ const f=F.find(f=>f.st===q.id); if(!f || q.at!==Esc.fk(z,f.ri,f.s)) bad.push(q.id+':자리'); });
    const g=F.filter(f=>f.gate); if(g.length!==1 || g[0].gate!==R.P[1].id || g[0].st || R.P[1].gate.f!==Esc.fk(z,g[0].ri,g[0].s)) bad.push(z+':잠긴 가구');
    const C=[].concat(...F.map(f=>(f.c||[]).map(c=>Object.assign({f}, c)))); if(C.some(c=>c.f.st || c.f.gate)) bad.push(z+':퍼즐 가구에 단서');
    R.P.forEach(q=>{ if(q.gate) return; (q.pc||[]).forEach(t=>{ if(C.filter(c=>c.pid===q.id && c.t===t).length!==1) bad.push(q.id+':단서 '+t.slice(0,10)); }); });
    if(z===1 && C.filter(c=>c.it).length!==2) bad.push('쪽지 두 장'); if(C.filter(c=>c.x).length!==1) bad.push(z+':낡은 쪽지');
    if(F.length!==15) bad.push(z+':가구 15'); });
  const w=[[0,3],[8,3]].every(d=>!Esc.wall(d[0],d[1])) && Esc.SLOT.every(s=>Esc.wall(s[0],s[1])) && Esc.wall(4,5);
  const pa=Esc.path([1,3],[7,3]), nr=Esc.near([1,3], Esc.SLOT[1]);
  return {bad, w, pa:pa && pa.length, nr}; }"""

SOLVE = """async ([id, v])=>{ const P=EscPad; P.view=id; P.inp=''; P.iw=[]; P.iwI=[]; P.wm=null; P.dl=null; P.wl=null; P._dk=''; P.draw(); const z=P.z();
  if(z.k==='ord'||z.k==='simon'){ const K=[...document.querySelectorAll('#escPad .epKeys.wd button')]; v.split(' ').forEach(w=>{ const b=K.find(b=>b.dataset.v===w && !b.disabled && P.iwI.indexOf(+b.dataset.i)<0); if(b) b.click(); }); }
  else if(z.k==='wire'){ v.split('').forEach((r,i)=>{ document.querySelector('#escPad [data-ep=wl][data-i="'+i+'"]').click(); document.querySelector('#escPad [data-ep=wr][data-i="'+r+'"]').click(); }); }
  else if(z.k==='dial'){ P.dl=z.wh.map((L,i)=>L.indexOf(v[i])); P._dk=''; P.draw(); }
  else P.inp=v;
  P.drawIn(); const s=document.getElementById('epSend'); const dis=s && s.disabled; P.send(); return {k:z.k, dis}; }"""
# 한 층 가구를 다 뒤짐 (퍼즐·잠긴 가구 빼고) — act 를 0.3초 간격으로
LOOK = """async (z)=>{ const P=EscPad, Z=P.Z(), T=P.myT(); let n=0; for(let r=0;r<3;r++) for(let s=0;s<5;s++){ const F=Z.H[z].R[r].F[s], fk=Esc.fk(z,r,s); if(F.st || (F.gate && !(T.rev||{})[F.gate]) || (P.myT().lk||{})[fk]) continue; P.act({a:'look', f:fk}); n++; await new Promise(q=>setTimeout(q,320)); } return n; }"""
GO = "(l)=>{ EscPad.loc=Object.assign({h:0}, l); EscPad.put(); EscPad._dk=''; EscPad.draw(); }"
TS = "()=>{ const T=EscTV.st.T[0]; return {rm:T.rm, sv:Object.keys(T.sv||{}).sort().join(','), inv:(T.inv||[]).join(','), rev:Object.keys(T.rev||{}).join(','), nt:(T.nt||[]).length, msg:(T.msg||{}).m||'', out:T.out, star:T.star, M:EscTV.st.M[0].length}; }"

async def walk_touch(k, kind, s=None):
    await k.evaluate("(a)=>EscPad.touch(a[0], a[1])", [kind, s])
    await k.wait_for_function("()=>!EscPad.way.length && !EscPad._srch", timeout=8000); await k.wait_for_timeout(400)

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(); await boot(pg)
        for st in ("basic", "elem", "mv1"):
            r = await pg.evaluate(GEN, st)
            ok(not r["bad"] and r["w"] and r["pa"] == 6 and r["nr"], f"{st}: 층마다 퍼즐 3·잠긴 가구 1·단서 다 배치 · 걷기 {r}")
        await pg.close()
        ctx = await b.new_context(viewport={"width": 1920, "height": 1080}); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        tv = await ctx.new_page(); errs = []; tv.on("pageerror", lambda e: errs.append("tv " + str(e))); await boot(tv)
        await tv.evaluate("()=>EscTV.setup()"); await tv.wait_for_timeout(300); await tv.screenshot(path=OUT + "setup.png")
        await tv.evaluate("()=>{ document.getElementById('escBk').value='elem'; document.getElementById('escBk').onchange(); document.querySelector('[data-mo=\"1\"]').click(); document.querySelector('[data-es=go]').click(); }")
        await tv.wait_for_function("()=>EscTV.room", timeout=8000); room = await tv.evaluate("()=>EscTV.room")
        ok(await tv.evaluate("()=>EscTV.cfg.mo===1 && EscTV.cfg.th==='house'"), f"저택 열기 (아오 보통) {room}")
        ks = []
        for nm, vp in (("가온", (820, 1180)), ("나래", (390, 844)), ("다솜", (915, 412))):
            k = await ctx.new_page(); k.on("pageerror", lambda e, nm=nm: errs.append(nm + " " + str(e))); await k.set_viewport_size({"width": vp[0], "height": vp[1]}); await boot(k)
            await k.evaluate("(a)=>{ EscPad.join(a[0], {id:a[1], n:a[1]}); window.confirm=()=>true; }", [room, nm]); ks.append(k); await k.wait_for_timeout(250)
        A, B, C = ks
        await tv.wait_for_timeout(700); await tv.screenshot(path=OUT + "lobby_tv.png")
        await tv.evaluate("()=>document.querySelector('[data-et=go]').click()"); await tv.wait_for_function("()=>EscTV.st && EscTV.st.s==='run'", timeout=10000)
        await tv.evaluate("()=>{ EscTV.st.t0=EscTV.now()+1500; EscTV.st.mo.nx=EscTV.now()+9e5; EscTV.push(); }"); await tv.wait_for_timeout(2600)
        ans = await tv.evaluate("()=>EscTV.ans[0]")
        r = await A.evaluate("()=>({map:!!document.querySelector('#escPad .hmGrid.big'), f:document.querySelectorAll('#escPad .hmF').length, me:!!document.querySelector('#escPad .hmK.me'), loc:EscPad.loc})")
        ok(r["map"] and r["f"] >= 7 and r["me"] and r["loc"]["z"] == 0 and r["loc"]["r"] == 0, f"패드 = 저택 지도 · 내 캐릭터 · 현관 {r}")
        await A.screenshot(path=OUT + "map_pad.png"); await B.screenshot(path=OUT + "map_ph.png"); await C.screenshot(path=OUT + "map_phL.png")
        # 다른 친구도 내 화면에 보임
        await tv.wait_for_timeout(600); n = await B.evaluate("()=>document.querySelectorAll('#escPad .hmK').length"); ok(n == 3, f"같은 방 친구 3명 보임 {n}")
        # 걷기: 바닥 누르기
        await B.evaluate("()=>{ const g=document.querySelector('#escPad .hmGrid.big'), r=g.getBoundingClientRect(), c=r.width/9; g.dispatchEvent(new MouseEvent('click', {bubbles:true, clientX:r.left+c*5.5, clientY:r.top+c*2.5})); }")
        await B.wait_for_timeout(1500); l = await B.evaluate("()=>EscPad.loc"); ok(l["x"] == 5 and l["y"] == 2, f"바닥 누르면 걸어감 {l}")
        await tv.wait_for_timeout(500); l2 = await tv.evaluate("(id)=>(EscTV.P[id]||{}).loc", "나래"); ok(l2 and l2["x"] == 5, f"TV 도 내 자리 {l2}")
        # 가구 뒤지기 (진짜로 걸어가서) → 모두의 노트
        Z = await tv.evaluate("()=>EscTV.st.Z[0].H")
        s0 = next(s for s, F in enumerate(Z[0]["R"][0]["F"]) if not F.get("st") and not F.get("gate"))
        await walk_touch(B, "f", s0); await tv.wait_for_timeout(1300)
        t = await tv.evaluate(TS); fk = f"0-0-{s0}"
        ok(await tv.evaluate("(f)=>!!EscTV.st.T[0].lk[f]", fk), f"걸어가서 뒤짐 → TV 에 표시 {fk} · 노트 {t['nt']}")
        await B.screenshot(path=OUT + "search_ph.png")
        # 1층 가구 다 뒤지기 → 노트 공유
        await A.evaluate(LOOK, 0); await tv.wait_for_timeout(900)
        t = await tv.evaluate(TS); ok(t["nt"] >= 3, f"1층 단서 노트 {t['nt']}개")
        nB = await B.evaluate("()=>{ EscPad.view='note'; EscPad._dk=''; EscPad.draw(); return document.querySelectorAll('#escPad .epNG p:not(.e)').length; }")
        ok(nB == t["nt"], f"다른 친구 노트에도 같은 단서 {nB}/{t['nt']}")
        await B.screenshot(path=OUT + "note_ph.png"); await B.evaluate("()=>{ EscPad.view=null; EscPad._dk=''; EscPad.draw(); }")
        # 퍼즐 가구까지 걸어가면 퍼즐 화면
        st0 = next(s for s, F in enumerate(Z[0]["R"][0]["F"]) if F.get("st")); pid0 = Z[0]["R"][0]["F"][st0]["st"]
        await walk_touch(A, "f", st0); r = await A.evaluate("()=>EscPad.view"); ok(r == pid0, f"퍼즐 가구 → 퍼즐 화면 {r}")
        await A.screenshot(path=OUT + "pz_pad.png")
        # 1층: a → 아이템 · b(아이템 쓰기) · c · 계단
        await A.evaluate(SOLVE, ["0a", ans["0a"]]); await tv.wait_for_timeout(900)
        t = await tv.evaluate(TS); it = t["inv"]; ok("0a" in t["sv"] and it, f"🔤 → 아이템 {it}")
        gk = await tv.evaluate("()=>EscTV.st.Z[0].R[0].P[1].gate.f"); gz, gr, gs = map(int, gk.split("-"))
        await A.evaluate(GO, {"z": 0, "r": gr, "x": 4, "y": 2})
        await A.evaluate("(it)=>{ EscPad.sel=it; }", it); await walk_touch(A, "f", gs); await tv.wait_for_timeout(900)
        t = await tv.evaluate(TS); ok("0b" in t["rev"] and "단서가 나왔어요" in t["msg"], f"아이템 들고 잠긴 가구 → 단서 {t['msg'][:50]}")
        for pid in ("0b", "0c"): await A.evaluate(SOLVE, [pid, ans[pid]]); await tv.wait_for_timeout(800)
        await A.evaluate(GO, {"z": 0, "r": 2, "x": 4, "y": 3}); await walk_touch(A, "up"); ok(await A.evaluate("()=>EscPad.view") == "0d", "퍼즐 3개 뒤 계단 → 계단 문 퍼즐")
        await A.evaluate(SOLVE, ["0d", ans["0d"]]); await tv.wait_for_timeout(900)
        t = await tv.evaluate(TS); ok(t["rm"] == 1 and "계단이 열렸어요" in t["msg"], f"계단 열림 {t['msg'][:30]}")
        await tv.screenshot(path=OUT + "tv_run.png")
        await A.evaluate("()=>{ EscPad.view=null; EscPad._dk=''; EscPad.draw(); }"); await walk_touch(A, "up")
        l = await A.evaluate("()=>EscPad.loc"); ok(l["z"] == 1 and l["r"] == 0, f"계단 → 2층 {l}")
        # 늦게 온 아이도 같이
        D = await ctx.new_page(); await D.set_viewport_size({"width": 1180, "height": 820}); await boot(D)
        await D.evaluate("(a)=>{ EscPad.join(a, {id:'라온', n:'라온'}); window.confirm=()=>true; }", room); await tv.wait_for_timeout(1500)
        t = await tv.evaluate(TS); r = await D.evaluate("()=>!!document.querySelector('#escPad .hmGrid.big')")
        ok(t["M"] == 4 and r, f"늦게 온 아이도 저택에 {t['M']}")
        # 2층: 쪽지 두 장 → 합치기
        for k in (A, B, C, D): await k.evaluate(GO, {"z": 1, "r": 0, "x": 4, "y": 2})
        await B.evaluate(LOOK, 1); await tv.wait_for_timeout(900)
        t = await tv.evaluate(TS); ok("n1" in t["inv"] and "n2" in t["inv"], f"📜 쪽지 두 장 {t['inv']}")
        await C.evaluate("()=>{ EscPad._dk=''; EscPad.draw(); document.querySelector('#escPad [data-ep=mix]').click(); }"); await tv.wait_for_timeout(900)
        t = await tv.evaluate(TS); ok("1c" in t["rev"], f"쪽지 합침 {t['msg'][:40]}")
        # 🔵 아오: 숨은 아이는 안 잡힘 · 안 숨은 아이는 잡혀 처음 방으로
        await tv.evaluate("()=>{ EscTV.cfg.mo=2; EscTV.st.mo.nx=EscTV.now(); }")
        await B.evaluate(GO, {"z": 1, "r": 1, "x": 4, "y": 4}); await walk_touch(B, "hide")
        await C.evaluate(GO, {"z": 1, "r": 1, "x": 6, "y": 2}); await A.evaluate(GO, {"z": 1, "r": 2, "x": 4, "y": 2}); await D.evaluate(GO, {"z": 1, "r": 2, "x": 5, "y": 2})
        await tv.evaluate("()=>{ EscTV.st.mo.nx=EscTV.now(); }"); await tv.wait_for_timeout(600)
        mo = await tv.evaluate("()=>EscTV.st.mo"); ok(mo["on"] == 1 and mo["z"] == 1, f"아오 등장 {mo}")
        await tv.evaluate("()=>{ const m=EscTV.st.mo; m.r=1; m.x=6; m.y=3; m.wait=0; EscTV.push(); }"); await tv.wait_for_timeout(2500)
        await C.screenshot(path=OUT + "monster_phL.png")
        cg = await tv.evaluate("()=>Object.keys(EscTV.st.cg||{})")
        ok("다솜" in cg and "나래" not in cg, f"안 숨은 아이만 잡힘 · 옷장에 숨은 아이는 안전 {cg}")
        hp = await tv.evaluate("()=>[EscTV.st.T[0].hp, EscTV.st.T[0].hpM]"); ok(hp[1] == 4 and hp[0] == 3, f"❤️ 팀 목숨(3명 시작 = 4) 하나 줄어듦 {hp}")
        r = await C.evaluate("()=>[document.querySelectorAll('#escPad .hmHp i').length, document.querySelectorAll('#escPad .hmHp i.off').length]"); ok(r == [4, 1], f"패드에 ❤️ {r}")
        await C.wait_for_timeout(500); l = await C.evaluate("()=>[EscPad.loc, !document.getElementById('epCaught').hidden]")
        ok(l[0]["r"] == 0 and l[0]["z"] == 1, f"잡히면 그 층 처음 방 {l}")
        await C.screenshot(path=OUT + "caught_phL.png")
        # 옷장: 꽉 차면(2명) 못 숨음 · 아오가 보는 앞에서 숨으면 들킴
        await tv.evaluate("()=>{ EscTV.st.mo.on=0; EscTV.st.mo.nx=EscTV.now()+9e5; EscTV.push(); }"); await tv.wait_for_timeout(300)
        for k in (A, D): await k.evaluate(GO, {"z": 1, "r": 1, "x": 3, "y": 5}); await k.evaluate("()=>{ EscPad.loc.h=1; EscPad.put(); }")
        await tv.wait_for_timeout(700); await C.evaluate(GO, {"z": 1, "r": 1, "x": 5, "y": 4}); await C.evaluate("()=>EscPad.touch('hide')"); await C.wait_for_timeout(300)
        r = await C.evaluate("()=>[EscPad.loc.h, EscPad.lm]"); ok(not r[0] and "꽉 찼어요" in r[1], f"옷장 2명까지 {r}")
        for k in (A, D): await k.evaluate("()=>{ EscPad.loc.h=0; EscPad.put(); }")
        await B.evaluate("()=>{ EscPad.loc.h=0; EscPad.put(); }"); await tv.wait_for_timeout(500)
        await tv.evaluate("()=>{ const m=EscTV.st.mo; Object.assign(m, {on:1, z:1, r:1, x:3, y:3, until:EscTV.now()+60000, wait:EscTV.now()+1500, mv:0}); EscTV.st.cg={}; EscTV._hd={}; EscTV.push(); }")
        await C.evaluate(GO, {"z": 1, "r": 1, "x": 3, "y": 4}); await C.evaluate("()=>{ EscPad.loc.h=1; EscPad.put(); }"); await A.evaluate(GO, {"z": 1, "r": 0, "x": 2, "y": 2})
        await B.evaluate(GO, {"z": 1, "r": 0, "x": 3, "y": 2}); await D.evaluate(GO, {"z": 1, "r": 0, "x": 4, "y": 2})
        await tv.wait_for_timeout(3500); cg = await tv.evaluate("()=>Object.keys(EscTV.st.cg||{})")
        ok("다솜" in cg, f"아오가 보는 앞에서 숨으면 들킴 {cg}")
        await tv.evaluate("()=>{ EscTV.st.mo.on=0; EscTV.st.mo.nx=EscTV.now()+9e5; EscTV.push(); }")
        await C.evaluate("()=>{ EscPad.loc.h=0; EscPad.put(); }")
        # 2층 · 지하 · 마지막
        await B.evaluate("()=>{ EscPad.loc.h=0; EscPad.put(); }")
        for pid in ("1a", "1c"): await A.evaluate(SOLVE, [pid, ans[pid]]); await tv.wait_for_timeout(800)
        gk = await tv.evaluate("()=>EscTV.st.Z[0].R[1].P[1].gate.f"); _, gr, gs = map(int, gk.split("-")); it = await tv.evaluate("()=>EscTV.st.Z[0].R[1].P[1].gate.it")
        await A.evaluate(GO, {"z": 1, "r": gr, "x": 4, "y": 2}); await A.evaluate("(it)=>{ EscPad.sel=it; }", it); await walk_touch(A, "f", gs); await tv.wait_for_timeout(800)
        for pid in ("1b", "1d"): await A.evaluate(SOLVE, [pid, ans[pid]]); await tv.wait_for_timeout(800)
        t = await tv.evaluate(TS); ok(t["rm"] == 2, f"2층 끝 {t['sv']}")
        await A.evaluate(GO, {"z": 2, "r": 0, "x": 4, "y": 2}); await A.evaluate(LOOK, 2); await tv.wait_for_timeout(800)
        for pid in ("2a", "2c"): await A.evaluate(SOLVE, [pid, ans[pid]]); await tv.wait_for_timeout(800)
        gk = await tv.evaluate("()=>EscTV.st.Z[0].R[2].P[1].gate.f"); _, gr, gs = map(int, gk.split("-")); it = await tv.evaluate("()=>EscTV.st.Z[0].R[2].P[1].gate.it")
        await A.evaluate(GO, {"z": 2, "r": gr, "x": 4, "y": 2}); await A.evaluate("(it)=>{ EscPad.sel=it; }", it); await walk_touch(A, "f", gs); await tv.wait_for_timeout(800)
        for pid in ("2b", "2d"): await A.evaluate(SOLVE, [pid, ans[pid]]); await tv.wait_for_timeout(800)
        t = await tv.evaluate(TS); ok(t["rm"] == 3, f"지하 끝 → 큰 문 {t['sv']}")
        await A.evaluate(GO, {"z": 2, "r": 2, "x": 4, "y": 3}); await walk_touch(A, "up"); ok(await A.evaluate("()=>EscPad.view") == "m", "큰 문 → 마지막 장치")
        await A.screenshot(path=OUT + "meta_pad.png")
        await A.evaluate(SOLVE, ["m", ans["m"]]); await tv.wait_for_timeout(1300)
        t = await tv.evaluate(TS); ok(t["out"] and t["star"] >= 3, f"다 같이 탈출 ⭐{t['star']}")
        r = await B.evaluate("()=>[document.querySelector('#escPad .epEnd h3').textContent, (document.querySelector('#escPad .stGem')||{}).textContent||'']")
        ok("탈출 성공" in r[0] and "+" in r[1], f"모든 패드 탈출 화면 · 보석 {r}")
        await tv.screenshot(path=OUT + "tv_end.png"); await B.screenshot(path=OUT + "end_ph.png")
        e = [x for x in errs if "favicon" not in x]; ok(not e, f"오류 없음 {e[:3]}")
        await ctx.close()
        # 💀 게임 오버: ❤️ 를 다 잃으면 끝
        ctx = await b.new_context(viewport={"width": 1920, "height": 1080}); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        tv = await ctx.new_page(); await boot(tv)
        await tv.evaluate("()=>EscTV.host({set:'elem', from:0, to:5, dur:20, lv:1, mo:2})"); await tv.wait_for_function("()=>EscTV.room", timeout=8000); room = await tv.evaluate("()=>EscTV.room")
        k = await ctx.new_page(); await k.set_viewport_size({"width": 390, "height": 844}); await boot(k)
        await k.evaluate("(a)=>{ EscPad.join(a, {id:'가온', n:'가온'}); window.confirm=()=>true; }", room); await tv.wait_for_timeout(800)
        await tv.evaluate("async ()=>{ await EscTV.go(); EscTV.st.t0=EscTV.now()+300; EscTV.st.mo.nx=EscTV.now()+9e5; EscTV.push(); }"); await tv.wait_for_timeout(1500)
        r = await tv.evaluate("()=>EscTV.st.T[0].hpM"); ok(r == 3, f"1명이면 ❤️ 3 {r}")
        await tv.evaluate("()=>{ EscTV.st.T[0].hp=1; const l=EscTV.P['가온'].loc; Object.assign(EscTV.st.mo, {on:1, z:0, r:0, x:l.x+1, y:l.y, until:EscTV.now()+60000, wait:0, mv:0}); EscTV.push(); }")
        await tv.wait_for_timeout(2500)
        r = await tv.evaluate("()=>[EscTV.st.s, EscTV.st.T[0].dead, EscTV.st.T[0].hp]"); ok(r[0] == "end" and r[1] == 1 and r[2] == 0, f"❤️ 0 = 게임 오버 {r}")
        await k.wait_for_timeout(1500)
        r = await k.evaluate("()=>[document.querySelector('#escPad .epEnd h3').textContent, !!document.querySelector('#escPad .epEnd .scFace')]"); ok("게임 오버" in r[0] and r[1], f"패드 게임 오버 화면 {r}")
        await k.screenshot(path=OUT + "over_ph.png"); await tv.screenshot(path=OUT + "over_tv.png")
        await ctx.close()
        # 화면: 지도·노트·퍼즐 × 5 크기 · TV 1280×720
        ctx = await b.new_context(viewport={"width": 1280, "height": 720}); await ctx.add_init_script("window.HY_FB_LOCAL=true;")
        tv = await ctx.new_page(); await boot(tv)
        await tv.evaluate("()=>EscTV.host({set:'mv1', from:0, to:5, dur:20, lv:2, mo:1})"); await tv.wait_for_function("()=>EscTV.room", timeout=8000); room = await tv.evaluate("()=>EscTV.room")
        pads = []
        for nm, vp in (("phL", (915, 412)), ("ph", (390, 844)), ("pad", (820, 1180)), ("padL", (1180, 820)), ("se", (375, 667))):
            k = await ctx.new_page(); await k.set_viewport_size({"width": vp[0], "height": vp[1]}); await boot(k)
            await k.evaluate("(a)=>{ EscPad.join(a[0], {id:a[1], n:a[1]}); window.confirm=()=>true; }", [room, nm]); pads.append((nm, k))
        await tv.wait_for_timeout(700); await tv.evaluate("async ()=>{ await EscTV.go(); EscTV.st.t0=EscTV.now()+300; EscTV.st.mo.nx=EscTV.now()+9e5; const T=EscTV.st.T[0]; T.inv=['lamp','lens','n1','n2']; T.msg={t:EscTV.now(), m:'🔍 가온이 🧊 냉장고에서 단서 · 📜 쪽지 왼쪽 발견! → 📒 노트 · 쪽지 두 장을 합쳐 봐요'}; EscTV.push(); }"); await tv.wait_for_timeout(1500)
        for nm, k in pads: await k.evaluate(LOOK, 0)
        await tv.wait_for_timeout(1000)
        ids = await tv.evaluate("()=>Esc.ids()")
        FIT = """()=>{ const P=document.getElementById('escPad'), all=[...P.querySelectorAll('button')].filter(b=>b.offsetParent).map(b=>b.getBoundingClientRect());
            return [P.scrollHeight-P.clientHeight, Math.round(Math.max(...all.map(x=>x.bottom))), innerHeight, Math.round(Math.max(...all.map(x=>x.right))), innerWidth]; }"""
        for view in [None, "note"] + ids:
            if view and view != "note":
                if view == "m": await tv.evaluate("()=>{ EscTV.st.T[0].rm=3; EscTV.push(); }")
                else: await tv.evaluate("(r)=>{ const T=EscTV.st.T[0]; T.rm=r; T.fl=EscTV.ans[0][r+'d'].slice(0,-1); EscTV.push(); }", int(view[0]))
                await tv.wait_for_timeout(400)
            for nm, k in pads:
                await k.evaluate("(v)=>{ EscPad.view=v; EscPad._dk=''; EscPad.draw(); }", view)
                if view and view != "note": await k.evaluate(SOLVE.replace("P.send();", ""), [view, await tv.evaluate("(i)=>EscTV.ans[0][i]", view)])
                r = await k.evaluate(FIT)
                ok((r[0] <= 0 or view == "note") and r[1] <= r[2] and r[3] <= r[4], f"{nm} {view or '지도'}: 화면 안 {r}")
                if view in (None, "note", "1c", "0c") : await k.screenshot(path=f"{OUT}fit_{view or 'map'}_{nm}.png")
        r = await tv.evaluate("()=>{ EscTV.draw(true); const d=document.getElementById('escTV'); return [d.scrollHeight-d.clientHeight, d.scrollWidth-d.clientWidth]; }")
        ok(r[0] <= 2 and r[1] <= 0, f"TV 1280×720 넘침 없음 {r}"); await tv.screenshot(path=OUT + "tv_720.png")
        await ctx.close(); await b.close()
    print("PASS" if not bad else "FAIL", len(bad))
    if bad: sys.exit(1)

asyncio.run(main())
