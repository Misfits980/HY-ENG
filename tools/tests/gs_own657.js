// (v657) Code.gs 서버 v22 — 🧸 주인 패드(유치부) 아이: 자동 랭킹 단계 = 유치원 → 유치원 책도 랭킹에 셈 (node tools/tests/gs_own657.js)
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
ok(post({type:"check", tk:"K"}).v>=22, "SERVER_V ≥ 22");
const now=Date.now(), H=3600e3;
const COLS=vm.runInContext("COLS.map(c=>c[0])", ctx), S=book.scores;
S.d=[vm.runInContext("COLS.map(c=>c[1])", ctx)];
const add=(t,o)=>{ const r=COLS.map(k=>k==="date"?new Date(t):(o[k]!==undefined?o[k]:"")); S.d.push(r); };
const st=(who,t,set,right,o)=>add(t, Object.assign({}, who, {diff:"study", rule:"study", set, right, wrong:0, score:right*10, clear:1}, o||{}));
const run=(who,t,set,score)=>add(t, Object.assign({}, who, {diff:"normal", rule:"normal", set, score, stage:5}));
const t=now-2*H;
// 루아 = 주인 패드(own 1) · G1-2 3판 + 유치원 2판 → 예전엔 자동 단계 G1-2 라 유치원 판이 빠졌음
const RU={nick:"👤루아", dev:"padA", own:1};
st(RU,t,"G1-2 Stage 1-1",10); st(RU,t+1e3,"G1-2 Stage 1-2",10); st(RU,t+2e3,"G1-2 Stage 1-3",10);
st(RU,t+3e3,"유치원 이중자음 Stage 2-2",6); st(RU,t+4e3,"유치원 이중자음 Stage 2-3",6); run(RU,t+5e3,"digr",900);
// 다른 아이(자기 기기 · 주인 패드 아님) 같은 모양 → 그대로 빠짐 (쉬운 책 막기는 그대로)
const NA={nick:"나래", tag:"0007", dev:"devB"};
st(NA,t,"G1-2 Stage 1-1",10); st(NA,t+1e3,"G1-2 Stage 1-2",10); st(NA,t+2e3,"G1-2 Stage 1-3",10);
st(NA,t+3e3,"유치원 이중자음 Stage 2-2",6); run(NA,t+5e3,"digr",900);
const sc=(b,k,n)=>{ const x=(b.boards[k]||[]).find(y=>y.nick===n); return x ? x.score : null; };
const b=get({board:1});
ok(sc(b,"study","루아")===3*110+2*66, "루아(주인 패드) 유치원 판도 공부 점수에 셈 = "+sc(b,"study","루아"));
ok(sc(b,"run","루아")===900, "루아 유치원 단어장(digr) 달리기도 셈 = "+sc(b,"run","루아"));
ok(sc(b,"study","나래")===3*110 && sc(b,"run","나래")===null, "자기 기기 아이는 그대로 (내 단계보다 쉬운 판 안 셈) 공부 "+sc(b,"study","나래")+" · 달리기 "+sc(b,"run","나래"));
const me=get({board:1, nick:"루아"}).me;
ok(me.study && me.study.lv==="유치원", "루아 내 단계 = 유치원 "+JSON.stringify(me.study&&me.study.lv));
console.log("DONE bad="+bad); process.exit(bad?1:0);
