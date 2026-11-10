// (v636) Code.gs 서버 v17 — ⚔️ 스테이지 도전장 (node tools/tests/gs_duel636.js)
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
const A={nick:"가온", tag:"0006", dev:"devA"}, B={nick:"나래", tag:"0007", dev:"devB"};
ok(post({type:"check", tk:"K"}).v>=17, "SERVER_V ≥ 17");
const t0=Date.now()-3600e3;
st(A,t0,"G3-4 Stage 1-1",30); st(B,t0,"G3-4 Stage 1-1",20); st({nick:"👤 다솜", tag:"0002", dev:"pad2"},t0,"G1-2 Stage 1-1",20); st({nick:"영어선생님", tag:"0000", dev:"t"},t0,"G1-2 Stage 1-1",20);
let r=post({type:"duelFriends"}); const ids=r.list.map(x=>x.id);
ok(r.ok && ids.indexOf("#0006")>=0 && ids.indexOf("#0007")>=0 && ids.indexOf("#0000")<0, "친구 목록 (선생님 빼고) "+JSON.stringify(r.list));
r=post({type:"duelSend", me:"#0006", fnick:"가온", to:"#0007", tnick:"나래", set:"elem", n:3, label:"G3-4 Stage 1-3", seed:123456, fsc:25, ftot:30, fms:95000});
ok(r.ok && r.id && book["도전장"] && book["도전장"].d.length===2, "도전장 보냄 → 「도전장」 탭 "+JSON.stringify(r));
const id=r.id;
ok(!post({type:"duelSend", me:"#0006", to:"#0006", set:"elem", n:3, seed:1}).ok, "나한테는 못 보냄");
let bx=post({type:"duelBox", me:"#0007"}); ok(bx.inbox.length===1 && bx.inbox[0].fnick==="가온" && bx.inbox[0].seed===123456 && bx.inbox[0].label==="G3-4 Stage 1-3", "나래 받은 도전장 "+JSON.stringify(bx.inbox[0]));
bx=post({type:"duelBox", me:"#0006"}); ok(bx.inbox.length===0 && bx.sent.length===1 && bx.sent[0].st==="wait", "가온 보낸 도전장 = 기다림");
ok(!post({type:"duelDone", me:"#0006", id, sc:30, tot:30, ms:1}).ok, "보낸 아이는 대신 못 끝냄");
r=post({type:"duelDone", me:"#0007", id, sc:27, tot:30, ms:120000}); ok(r.ok && r.d.st==="done" && r.d.tsc===27 && r.d.fsc===25, "나래 끝냄 → 결과 "+JSON.stringify(r.d));
r=post({type:"duelDone", me:"#0007", id, sc:30, tot:30, ms:1}); ok(r.ok && r.again && r.d.tsc===27, "두 번은 안 바뀜");
bx=post({type:"duelBox", me:"#0006"}); ok(bx.sent[0].st==="done" && bx.sent[0].tsc===27, "가온: 보낸 도전장 결과 보임");
bx=post({type:"duelBox", me:"#0007"}); ok(bx.inbox.length===0 && bx.got.length===1, "나래: 끝난 것으로 옮겨짐");
for(let i=0;i<10;i++) post({type:"duelSend", me:"#0006", to:"#0007", set:"elem", n:1, seed:i});
ok(post({type:"duelSend", me:"#0006", to:"#0007", set:"elem", n:1, seed:99}).err==="max", "하루 10장까지");
// 7일 지난 것 = 시간 끝
const D=book["도전장"].d; D[2][1]=new Date(Date.now()-8*864e5);
bx=post({type:"duelBox", me:"#0007"}); ok(bx.inbox.every(x=>x.id!==String(D[2][0])), "7일 지난 도전장은 받은 칸에서 빠짐");
ok(post({type:"duelDone", me:"#0007", id:String(D[2][0]), sc:1, tot:1, ms:1}).err==="old", "7일 지난 건 못 끝냄");
// 이름 아이(공용 패드)
r=post({type:"duelSend", me:"👤 다솜", fnick:"다솜", to:"#0006", set:"basic", n:1, seed:5, fsc:10, ftot:20, fms:1}); ok(r.ok, "이름으로 노는 아이도 보냄");
bx=post({type:"duelBox", me:"다솜"}); ok(bx.sent.length===1, "이름(👤 뗀) 으로 다시 찾음 "+JSON.stringify(bx.sent.map(x=>x.from)));
console.log("DONE bad="+bad); process.exit(bad?1:0);
