// (v667) Code.gs 서버 v23 — 🔥 오늘의 대결(board.today · 오늘의 상 · me.today) + 선생님 📊 랭킹 통계(report.rk) (node tools/tests/gs_today667.js)
const fs=require("fs"), vm=require("vm"), path=require("path");
const src=fs.readFileSync(path.join(__dirname,"..","..","server","Code.gs"),"utf8");
const colN=s=>s.split("").reduce((n,ch)=>n*26+ch.charCodeAt(0)-64,0);
function Sheet(name){ const S={name, d:[], fmt:{}};
  const cell=(r,c)=>{ while(S.d.length<r) S.d.push([]); const row=S.d[r-1]; while(row.length<c) row.push(""); return row; };
  function Range(r,c,nr,nc){ return {
    getValue(){ const row=S.d[r-1]; return row && row[c-1]!==undefined ? row[c-1] : ""; },
    getValues(){ const o=[]; for(let i=0;i<nr;i++){ const row=S.d[r-1+i]||[]; const a=[]; for(let j=0;j<nc;j++) a.push(row[c-1+j]!==undefined?row[c-1+j]:""); o.push(a); } return o; },
    getDisplayValues(){ return this.getValues().map(a=>a.map(v=>v instanceof Date ? v.toISOString().slice(0,16) : String(v))); },
    setValue(v){ const row=cell(r,c); row[c-1]=(S.fmt[c]==="@" && v!=="" && typeof v!=="object")?String(v):v; return this; },
    setValues(V){ V.forEach((a,i)=>a.forEach((v,j)=>{ const row=cell(r+i,c+j); row[c-1+j]=(S.fmt[c+j]==="@")?String(v):v; })); return this; },
    setNumberFormat(f){ if(f==="@") for(let j=0;j<nc;j++) S.fmt[c+j]="@"; return this; }, setFontWeight(){ return this; } }; }
  return Object.assign(S, {
    getRange(a,b,c,d){ if(typeof a==="string"){ const m=a.match(/^([A-Z]+)(\d+):([A-Z]+)(\d+)$/); if(m) return Range(+m[2], colN(m[1]), +m[4]-+m[2]+1, colN(m[3])-colN(m[1])+1);
        const k=a.match(/^([A-Z]+):\1$/); if(k) return Range(1, colN(k[1]), 1, 1); return Range(1,1,1,1); } return Range(a,b,c||1,d||1); },
    getLastRow(){ let n=S.d.length; while(n>0 && !(S.d[n-1]||[]).some(v=>v!=="" && v!==undefined)) n--; return n; },
    appendRow(a){ const n=this.getLastRow()+1; a.forEach((v,j)=>{ cell(n,j+1)[j]=v; }); },
    setFrozenRows(){}, setColumnWidth(){}, deleteRows(){}, getMaxColumns(){ return 99; }, insertColumnsAfter(){} }); }
const book={}; book.scores=Sheet("scores"); book["명단"]=Sheet("명단");
const ctx={ SpreadsheetApp:{ openById:()=>({ getSheetByName:n=>book[n]||null, insertSheet:n=>(book[n]=Sheet(n)) }) },
  LockService:{ getScriptLock:()=>({waitLock(){}, releaseLock(){}}) },
  ContentService:{ createTextOutput:t=>({ setMimeType(){ return this; }, getContent:()=>t }), MimeType:{JSON:1} },
  PropertiesService:{ getScriptProperties:()=>({ getProperty:()=>"K" }) },
  Utilities:{ formatDate:(d,tz,f)=>{ const k=new Date(new Date(d).getTime()+9*3600e3).toISOString(); return f==="yyyy-MM-dd"?k.slice(0,10):k.slice(0,16); } }, Logger:{log(){}}, console };
vm.createContext(ctx); vm.runInContext(src, ctx);
const post=(o)=>JSON.parse(ctx.doPost({postData:{contents:JSON.stringify(Object.assign({key:"HYENG"},o))}}).getContent());
let bad=0; const ok=(c,m)=>{ console.log((c?"OK  ":"BAD ")+m); if(!c) bad++; };
const get=(p)=>JSON.parse(ctx.doGet({parameter:Object.assign({key:"HYENG"},p)}).getContent());

// 시간 고정: 2026-11-12(목) 15:00 한국 시간 → 이번 주 = 11/9(월)~ · 지난주 = 11/2~8 · 지난달 = 10월
const NOW=Date.UTC(2026,10,12,6,0,0), H=3600e3, D=24*H, KST=d=>Date.UTC(2026,d[0]-1,d[1],d[2]-9,0,0);
vm.runInContext("Date.now=()=>"+NOW, ctx);
ok(post({type:"check", tk:"K"}).v>=23, "SERVER_V ≥ 23");
const COLS=vm.runInContext("COLS.map(c=>c[0])", ctx), S=book.scores;
S.d=[vm.runInContext("COLS.map(c=>c[1])", ctx)];
book["명단"].d=[[],[],[],[],["ACE","김에이","dA","",""]];
const add=(t,o)=>{ S.d.push(COLS.map(k=>k==="date"?new Date(t):(o[k]!==undefined?o[k]:""))); };
const st=(who,t,set,right,wrong,o)=>add(t, Object.assign({}, who, {diff:"study", rule:"study", set:"G3-4 "+set, right, wrong:wrong||0, score:right*10, clear:1}, o||{}));
const A={nick:"ACE", tag:"0006", dev:"dA"}, B={nick:"비비", tag:"0007", dev:"dB"}, Cc={nick:"👤씨씨", dev:"pad1"};
// 지난달
st(A, KST([10,20,16]), "Stage 9-1", 10);
st(B, KST([10,28,16]), "Stage 9-1", 10);
// 지난주
st(B, KST([11,3,16]), "Stage 5-1", 10);
// 이번 주
st(A, KST([11,9,16]),  "Stage 1-1", 10, 0, {dex:40});   // 월: A 110
st(B, KST([11,9,17]),  "Stage 1-1", 20);                // 월: B 220 → 월 1등 B
st(A, KST([11,10,16]), "Stage 1-2", 30, 0, {dex:50});   // 화: A 330 → 화 1등 A
st(A, KST([11,11,16]), "Stage 1-1", 15);                // 수: A 같은 Stage 더 잘함 165 → +55
st(B, KST([11,11,16]), "Stage 1-2", 5, 5);              // 수: B 60 → 수 1등 B (60 > 55 > 44)
st(Cc,KST([11,11,17]), "Stage 2-1", 4);                 // 수: 씨씨 44
st(A, KST([11,12,10]), "Stage 1-3", 10, 0, {dex:58});   // 오늘: A 110
st(Cc,KST([11,12,11]), "Stage 2-2", 20);                // 오늘: 씨씨 220 → 오늘 1등
st(B, KST([11,12,12]), "Stage 1-1 연습", 30);           // 오늘: B 연습 판 (점수 X · 푼 문제 O)
add(KST([11,12,13]), Object.assign({}, B, {diff:"study", rule:"study-battle", set:"x", right:50, wrong:0, score:500, clear:1}));   // 배틀 = 통계에서 뺌
const b=get({board:1, tag:"0006", nick:"ACE"});
const T=b.today||{}, L=T.list||[];
ok(T.key==="2026-11-12" && T.of===2 && L.length===2, "오늘 순위 2명 "+JSON.stringify(L.map(x=>[x.nick,x.score,x.n])));
ok(L[0] && L[0].nick==="씨씨" && L[0].score===220 && L[1].nick==="ACE" && L[1].score===110 && L[1].n===1, "오늘 1등 씨씨 220 · 2등 ACE 110 (연습만 한 비비는 없음)");
const wk=(b.boards.study||[]).map(x=>[x.nick,x.score]);
ok(JSON.stringify(wk)===JSON.stringify([["ACE",605],["비비",280],["씨씨",264]]), "이번 주 점수는 그대로 "+JSON.stringify(wk));
const mt=b.me.today||{};
ok(mt.rank===2 && mt.of===2 && mt.score===110 && mt.above && mt.above.nick==="씨씨" && mt.above.score===220 && mt.below===null, "나(ACE) 오늘 2등 · 위 씨씨 220 "+JSON.stringify(mt));
ok(b.me.study && b.me.study.rank===1 && JSON.stringify(b.me.study.day)===JSON.stringify([0,330,165,110,0,0,0]), "📊 내 기록 날마다 점수(day)는 예전 그대로 "+JSON.stringify(b.me.study&&b.me.study.day));
const aw=T.aw||{};
ok(aw.up && aw.up.nick==="씨씨" && aw.up.v===1, "📈 역전왕 씨씨 (이번 주 2번째 → 오늘 1등) "+JSON.stringify(aw.up));
ok(aw.acc && aw.acc.nick==="씨씨" && aw.acc.v===100, "🎯 정확왕 씨씨 100% (ACE 는 10문제라 빠짐) "+JSON.stringify(aw.acc));
ok(aw.word && aw.word.nick==="ACE" && aw.word.v===8, "📖 단어왕 ACE +8 "+JSON.stringify(aw.word));
ok(aw.att && aw.att.nick==="ACE" && aw.att.v===4, "🔥 개근왕 ACE 4일 "+JSON.stringify(aw.att));
const none=get({board:1, tag:"0007", nick:"비비"});
ok(none.today && none.today.of===2 && !none.me.today, "오늘 안 한 아이: 순위는 보이고 me.today 없음");
// 선생님 통계
const rep=post({type:"report", tk:"K"}).rep, rk=rep.rk||{}, per={}; (rk.per||[]).forEach(p=>{ per[p.k]=p; });
const row=(k,n)=>((per[k]||{}).rows||[]).find(r=>r.n===n)||{};
ok(rk.per && rk.per.length===4 && per.w0.from==="2026-11-09" && per.w0.to==="2026-11-15" && per.w1.from==="2026-11-02" && per.m0.from==="2026-11-01" && per.m0.to==="2026-11-30" && per.m1.from==="2026-10-01" && per.m1.to==="2026-10-31", "기간 넷 "+JSON.stringify((rk.per||[]).map(p=>[p.name,p.from,p.to])));
const a0=row("w0","김에이"), b0=row("w0","비비"), c0=row("w0","씨씨");
ok(a0.g==="ACE" && a0.tag==="0006", "이름 = 명단 이름(김에이) · 게임 이름 ACE "+JSON.stringify([a0.n,a0.g,a0.tag]));
ok(a0.d1===1 && b0.d1===2 && !c0.d1 && per.w0.dn===3, "이번 주 하루 1등: 비비 2(월·수) · 김에이 1(화) · 오늘은 아직 안 셈 "+JSON.stringify([a0.d1,b0.d1,c0.d1,per.w0.dn]));
ok(a0.rk===1 && b0.rk===2 && c0.rk===3, "이번 주 순위 1·2·3");
ok(a0.days===4 && b0.days===3 && c0.days===2, "한 날: 김에이 4 · 비비 3(연습한 날도) · 씨씨 2 "+JSON.stringify([a0.days,b0.days,c0.days]));
ok(a0.q===65 && b0.q===60 && c0.q===24, "푼 문제: 65 · 60(배틀 50문제는 뺌) · 24 "+JSON.stringify([a0.q,b0.q,c0.q]));
ok(a0.ok===100 && b0.ok===92 && a0.sc===605 && b0.sc===280 && c0.sc===264 && a0.r===4 && b0.r===3, "정답률·점수·끝낸 판 "+JSON.stringify([a0.ok,b0.ok,a0.sc,b0.sc,c0.sc,a0.r,b0.r]));
const b1=row("w1","비비");
ok(per.w1.rows.length===1 && b1.d1===1 && b1.rk===1 && b1.days===1 && b1.q===10, "지난주: 비비만 · 하루 1등 1 · 1위");
const am=row("m1","김에이"), bm=row("m1","비비");
ok(am.d1===1 && am.w1===1 && am.days===1 && am.q===10 && bm.d1===1 && bm.w1===0, "지난달(10월): 김에이 하루 1등 1·주 1등 1 · 비비 하루 1등 1·주 1등 0(그 주는 11/1 에 끝남) "+JSON.stringify([am.d1,am.w1,bm.d1,bm.w1]));
const an=row("m0","김에이"), bn=row("m0","비비"), cn=row("m0","씨씨");
ok(bn.d1===3 && bn.w1===2 && an.d1===1 && an.w1===0, "이번 달(11월): 비비 하루 1등 3(11/3·9·11)·주 1등 2 · 김에이 1·0 "+JSON.stringify([bn.d1,bn.w1,an.d1,an.w1]));
ok(bn.q===70 && an.q===65 && cn.q===24 && per.m0.rows[0].n==="비비", "이번 달 푼 문제 70·65·24 · 많이 푼 순 "+JSON.stringify(per.m0.rows.map(r=>[r.n,r.q])));
ok(bn.days===4 && an.days===4, "이번 달 한 날 4·4");
console.log("DONE bad="+bad); process.exit(bad?1:0);
