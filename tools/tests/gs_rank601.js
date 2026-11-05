// (v601) Code.gs 서버 v10 — 🔥 실시간 랭킹 board · 📚 공부 랭킹 · 이번 주 단어 수 (node tools/tests/gs_rank601.js)
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
book["명단"].d=[[],[],[],[],["스트로베리","최선아","devSA","devSA2","",""],["","라언","padK1","","",""],["김지환","","devJH","","",""]];
const ctx={ SpreadsheetApp:{ openById:()=>({ getSheetByName:n=>book[n]||null, insertSheet:n=>(book[n]=Sheet(n)) }) },
  LockService:{ getScriptLock:()=>({waitLock(){}, releaseLock(){}}) },
  ContentService:{ createTextOutput:t=>({ setMimeType(){ return this; }, getContent:()=>t }), MimeType:{JSON:1} },
  PropertiesService:{ getScriptProperties:()=>({ getProperty:()=>"K" }) },
  Utilities:{ formatDate:(d,tz,f)=>{ const k=new Date(new Date(d).getTime()+9*3600e3).toISOString(); return f==="yyyy-MM-dd"?k.slice(0,10):k.slice(0,16); } }, Logger:{log(){}}, console };
vm.createContext(ctx); vm.runInContext(src, ctx);
const post=(o)=>JSON.parse(ctx.doPost({postData:{contents:JSON.stringify(Object.assign({key:"HYENG"},o))}}).getContent());
let bad=0; const ok=(c,m)=>{ console.log((c?"OK  ":"BAD ")+m); if(!c) bad++; };
const get=(p)=>JSON.parse(ctx.doGet({parameter:Object.assign({key:"HYENG"},p)}).getContent());
ok(post({type:"check", tk:"K"}).v===10, "SERVER_V = 10");
const ws=vm.runInContext("weekStart_()", ctx), now=Date.now(), H=3600e3;
const COLS=vm.runInContext("COLS.map(c=>c[0])", ctx), S=book.scores;
S.d=[vm.runInContext("COLS.map(c=>c[1])", ctx)];
const add=(t,o)=>{ const r=COLS.map(k=>k==="date"?new Date(t):(o[k]!==undefined?o[k]:"")); S.d.push(r); };
const A={nick:"👤지후", tag:"#0006", dev:"dA"}, B={nick:"민수", tag:"#0007", dev:"dB"}, Cc={nick:"새싹", tag:"#0008", dev:"dC"}, T={nick:"영어선생님", tag:"#0000", dev:"dT"};
const st=(who,t,set,right,o)=>add(t, Object.assign({}, who, {diff:"study", rule:"study", set, right, clear:1}, o||{}));
const old=now-ws>30*H;   // 이번 주가 하루 넘게 지났으면 ▲▼ 시험
// 지난주 도감
add(ws-2*864e5, Object.assign({}, A, {nick:"지후", diff:"easy", rule:"normal", score:100, dex:100}));   // 내 기기 달리기 줄은 👤 없음
add(ws-2*864e5, Object.assign({}, B, {diff:"easy", rule:"normal", score:100, dex:50}));
// 이번 주 — B 가 먼저 많이 (어제보다 전)
const e1=old ? ws+H : now-3*H, e2=now-H;
st(B, e1, "S1", 10); st(B, e1+60000, "S2", 10, {dex:50});
st(A, e1+120000, "S1", 6, {dex:110});
// 최근 24시간 — A 가 따라잡음
st(A, e2, "S2", 8, {dex:120}); st(A, e2+60000, "S2", 8);               // 같은 날 같은 Stage 다시 = 안 셈
st(A, e2+120000, "S3", 9, {dex:130}); st(A, e2+180000, "S4", 9, {clear:0}); // 중간에 나감 = 안 셈
st(A, e2+200000, "S5", 30, {rule:"study-battle"});                     // 배틀 = 안 셈
st(Cc, e2, "S1", 4, {dex:12});
st(T, e2, "S1", 99, {dex:999});
add(e2, Object.assign({}, A, {nick:"지후", diff:"hard", rule:"normal", score:900, stage:12})); add(e2, Object.assign({}, A, {nick:"지후", diff:"easy", rule:"normal", score:500}));
add(e2, Object.assign({}, B, {diff:"normal", rule:"normal", score:700, stage:9}));
add(e2, Object.assign({}, Cc, {diff:"easy", rule:"study-raid", score:5000}));
const b=get({board:1});
ok(b.ok && b.v===10 && b.boards, "board=1 → 셋 "+JSON.stringify(Object.keys(b.boards||{})));
const s=b.boards.study, w=b.boards.words, r=b.boards.run;
ok(s.map(x=>x.nick+":"+x.score+":"+x.n).join(",")==="지후:23:3,민수:20:2,새싹:4:1", "📚 공부 = 끝까지 푼 판 맞힌 수 (같은 날 다시 · 나감 · 배틀 · 선생님 빼기) "+JSON.stringify(s));
ok(w.map(x=>x.nick+":"+x.score).join(",")==="지후:30,새싹:12", "📖 이번 주 단어 = 이번 주에 모은 수 (지후 100→130 = 30 · 새싹 처음 12 · 민수 0 = 없음) "+JSON.stringify(w));
ok(r.map(x=>x.nick+":"+x.score).join(",")==="지후:900,민수:700", "🏃 달리기 = 이번 주 가장 높은 점수 (난이도 상관없이 · 레이드 X) "+JSON.stringify(r));
ok(s[0].tag==="0006" && s[0].nick==="지후", "이름 👤 떼고 태그");
if(old){ ok(s[0].mv===1 && s[1].mv===-1 && s[2].mv==="new", "▲▼: 지후 ▲1 · 민수 ▼1 · 새싹 NEW "+JSON.stringify(s.map(x=>x.mv))); }
else console.log("(이번 주가 하루도 안 지나 ▲▼ 시험은 건너뜀)");
const ls=get({diff:"study", range:"week", n:"5", dev:"dA"}).list;
ok(ls[0].nick==="지후" && ls[0].score===23 && ls[0].me===true && ls[1].me===false, "diff=study 목록 · 내 기기 = me "+JSON.stringify(ls));
const lw=get({diff:"dex", range:"week"}).list, la=get({diff:"dex", range:"all"}).list;
ok(lw[0].score===30 && la[0].score===130, "단어 수집: 이번 주 = 30 (모은 수) · 전체 = 130 (지금까지)");
console.log("DONE bad="+bad); process.exit(bad?1:0);
