// (v635) Code.gs 서버 v16 — 🏅 나의 리그 (지난주 나 넘기) (node tools/tests/gs_lg635.js)
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
ok(post({type:"check", tk:"K"}).v>=15, "SERVER_V ≥ 15");
const now=Date.now(), H=3600e3;
const COLS=vm.runInContext("COLS.map(c=>c[0])", ctx), S=book.scores;
S.d=[vm.runInContext("COLS.map(c=>c[1])", ctx)];
const add=(t,o)=>{ const r=COLS.map(k=>k==="date"?new Date(t):(o[k]!==undefined?o[k]:"")); S.d.push(r); };
const st=(who,t,set,right,o)=>add(t, Object.assign({}, who, {diff:"study", rule:"study", set, right, wrong:0, score:right*10, clear:1}, o||{}));
const run=(who,t,set,score)=>add(t, Object.assign({}, who, {diff:"hard", rule:"normal", set, score, stage:5}));
// 태그 탭 (아이가 이름을 정하면 생김)
["devA","devB","devC"].forEach((d,i)=>post({type:"tag", dev:d, nick:["가온","나래","다솜"][i]}));
const A={nick:"가온", tag:"0006", dev:"devA"}, B={nick:"나래", tag:"0007", dev:"devB"}, Cc={nick:"다솜", tag:"0008", dev:"devC"};
ok(post({type:"check", tk:"K"}).v>=16, "SERVER_V ≥ 16");
const ws=vm.runInContext("weekStart_()", ctx), W=7*864e5, mid=x=>ws - x*W + 2*864e5 + 3600e3;   // x 주 전 수요일
// 가온: 3주 전 330 · 2주 전 440 · 지난주 330(=440의 75% → 못 지킴) ... 그래서 연속 = 지난주만 보면 0
// 나래: 3주 전 330 · 2주 전 330 · 지난주 330 → 3주 연속 지킴 · 이번 주 아직 220
// 다솜: 지난주 0 · 이번 주 330 → 지난주 없음 → 목표 300
const t0=Date.now()-3600e3;
st(A,mid(3),"G3-4 Stage 1-1",30); st(A,mid(2),"G3-4 Stage 1-2",40); st(A,mid(1),"G3-4 Stage 1-3",30); st(A,t0,"G3-4 Stage 2-1",30); st(A,t0+1e3,"G3-4 Stage 2-2",10);
st(B,mid(3),"G3-4 Stage 1-1",30); st(B,mid(2),"G3-4 Stage 1-2",30); st(B,mid(1),"G3-4 Stage 1-3",30); st(B,t0,"G3-4 Stage 2-1",20);
st(Cc,t0,"G3-4 Stage 1-1",30);
const lg=(tag)=>get({board:1, tag}).me.lg;
let a=lg("0006"), b=lg("0007"), c=lg("0008");
ok(a && a.last===330 && a.hist[1]===440 && a.hist[2]===330 && a.st===0, "가온 지난 주들 · 지난주 못 지킴 → 연속 0 "+JSON.stringify(a));
ok(a.now===440 && a.goal===331 && a.win===2, "가온 이번 주 440 > 지난주 330 → 넘기 "+JSON.stringify([a.now,a.goal,a.win]));
ok(b && b.st===3 && b.last===330 && b.now===220 && b.win===0 && b.keep===300, "나래 3주 연속 지킴 · 이번 주 아직 "+JSON.stringify(b));
ok(c && c.last===0 && c.goal===300 && c.now===330 && c.win===2 && c.st===0, "다솜 지난주 없음 → 목표 300 · 넘음 "+JSON.stringify(c));
ok(get({board:1, tag:"0099"}).me.lg===undefined, "기록 없는 아이 = lg 없음");
// 랭킹 단계: 다솜을 G5-6 으로 정하면 G3-4 판은 안 셈 → 이번 주 0
post({type:"tagLv", tk:"K", tags:["0008"], lv:"G5-6"});
c=get({board:1, tag:"0008"}).me.lg; ok(!c || c.now===0, "랭킹 단계 규칙도 그대로 (쉬운 책은 안 셈) "+JSON.stringify(c));
console.log("DONE bad="+bad); process.exit(bad?1:0);
