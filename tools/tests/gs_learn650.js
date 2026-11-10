// (v650) Code.gs 서버 v19 — 🧠 며칠 뒤에도 기억하나 (node tools/tests/gs_learn650.js)
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
ok(post({type:"check", tk:"K"}).v>=19, "SERVER_V ≥ 19");
const now=Date.now(), base={diff:"study", rule:"study-review", score:10, acc:90, right:9, wrong:1, set:"복습", secs:60, ver:"v650"};
ok(post(Object.assign({}, base, {nick:"민준", tag:"0006", at:now-1000, rid:"a1", rvo:3, rvn:10, rvw:"quite, through", sp:2})).ok, "기록 1");
post(Object.assign({}, base, {nick:"민준", tag:"0006", at:now-900, rid:"a2", rvo:6, rvn:10, rvw:"quite"}));
post(Object.assign({}, base, {nick:"서연", tag:"0007", at:now-800, rid:"a3", rvo:9, rvn:10, rvw:"quite", sp:5}));
post(Object.assign({}, base, {nick:"지호", tag:"0008", at:now-700, rid:"a4"}));   // 옛 게임 — 칸 없음
const H=book.scores.d[0], ci=n=>H.indexOf(n), r1=book.scores.d[1], r4=book.scores.d[4];
ok(ci("며칠 뒤 맞힘")>0 && ci("며칠 뒤 푼 수")===ci("며칠 뒤 맞힘")+1 && ci("말한 단어")===H.length-1, "새 칸 4개가 맨 끝에 "+H.slice(-4).join(" · "));
ok(r1[ci("며칠 뒤 맞힘")]===3 && r1[ci("며칠 뒤 푼 수")]===10 && r1[ci("며칠 뒤 틀린 단어")]==="quite, through" && r1[ci("말한 단어")]===2, "값이 숫자·글자 그대로");
ok(r4[ci("며칠 뒤 맞힘")]==="" && r4[ci("말한 단어")]==="", "옛 게임 줄은 빈 칸");
const L=post({type:"report", tk:"K"}).rep.learn;
ok(L && L.kids.length===2 && L.kids[0].n==="민준" && L.kids[0].ok===9 && L.kids[0].tot===20 && L.kids[0].sp===2 && L.kids[1].n==="서연" && L.kids[1].ok===9, "아이마다 합 · 낮은 아이 먼저 "+JSON.stringify(L.kids.map(k=>[k.n,k.ok,k.tot,k.sp])));
ok(JSON.stringify(L.kids[0].w)===JSON.stringify([["quite",2],["through",1]]) && JSON.stringify(L.words[0])===JSON.stringify(["quite",2,3]), "안 붙는 단어: 아이별 · 반(아이 수 많은 순) "+JSON.stringify(L.words));
book.scores.d[1][0]=new Date(now-20*864e5);
ok(post({type:"report", tk:"K"}).rep.learn.kids[0].tot===10, "14일보다 오래된 줄은 뺌");
console.log(bad ? "FAIL "+bad : "PASS"); process.exit(bad?1:0);
