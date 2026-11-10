// (v654) Code.gs 서버 v21 — 🎮 「모드 사용」 탭 (node tools/tests/gs_use654.js)
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
    setNumberFormat(f){ if(f==="@") for(let j=0;j<nc;j++) S.fmt[c+j]="@"; return this; }, setFontWeight(){ return this; }, setBackground(){ return this; }, setWrap(){ return this; } }; }
  return Object.assign(S, {
    getRange(a,b,c,d){ if(typeof a==="string"){ const m=a.match(/^([A-Z]+)(\d+):([A-Z]+)(\d+)$/); if(m) return Range(+m[2], colN(m[1]), +m[4]-+m[2]+1, colN(m[3])-colN(m[1])+1);
        const k=a.match(/^([A-Z]+):\1$/); if(k) return Range(1, colN(k[1]), 1, 1); return Range(1,1,1,1); } return Range(a,b,c||1,d||1); },
    getLastRow(){ let n=S.d.length; while(n>0 && !(S.d[n-1]||[]).some(v=>v!=="" && v!==undefined)) n--; return n; },
    appendRow(a){ const n=this.getLastRow()+1; a.forEach((v,j)=>{ cell(n,j+1)[j]=v; }); },
    setFrozenRows(){}, setFrozenColumns(){}, setColumnWidths(){}, setColumnWidth(){}, deleteRows(){}, getMaxColumns(){ return 99; }, insertColumnsAfter(){} }); }
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
ok(post({type:"check", tk:"K"}).v>=21, "SERVER_V ≥ 21");
const today=new Date(Date.now()+9*3600e3).toISOString().slice(0,10), old=new Date(Date.now()+9*3600e3-20*864e5).toISOString().slice(0,10);
ok(post({type:"use", dev:"devSA", nick:"스트로베리", tag:"0003", day:today, m:{study:12.5, run:3, menu:1.2}, ver:"v654"}).ok, "개인 기기 기록");
const U=book["모드 사용"], H=U.d[0], c=n=>H.indexOf(n);
ok(H.slice(0,5).join()==="날짜,아이,태그,기기,합계(분)" && c("보드게임(분)")>0 && c("마이타운(분)")>0 && c("저택 탈출(분)")>0, "탭 머리글 "+H.join(" · "));
ok(U.d[1][0]===today && U.d[1][1]==="최선아 (스트로베리)" && U.d[1][2]==="#0003" && U.d[1][c("오늘의 30(분)")]===12.5 && U.d[1][c("달리기(분)")]===3 && U.d[1][4]===16.7 && U.d[1][c("보드게임(분)")]==="", "명단 이름 · 모드 칸 · 합계 · 안 한 모드는 빈칸 "+JSON.stringify(U.d[1].slice(0,8)));
post({type:"use", dev:"devSA", nick:"스트로베리", tag:"0003", day:today, m:{study:20, run:2, board:9.5}, ver:"v654"});
ok(U.d.length===2 && U.d[1][c("오늘의 30(분)")]===20 && U.d[1][c("달리기(분)")]===3 && U.d[1][c("보드게임(분)")]===9.5 && U.d[1][4]===33.7, "같은 날 다시 오면 같은 줄 · 큰 값으로 (줄어들지 않음) "+U.d[1][4]);
post({type:"mt", dev:"devSA", nick:"스트로베리", tag:"0003", day:today, min:7, segs:2, ver:"town"});
ok(U.d.length===2 && U.d[1][c("마이타운(분)")]===7 && U.d[1][4]===40.7 && book["마이타운 시간"].d[1][4]===7, "🏝 마이타운 기록이 같은 줄의 마이타운 칸에 (예전 탭도 그대로)");
post({type:"use", dev:"padK1", nick:"라언", pad:1, day:today, m:{esc:15, battle:6}, ver:"v654"});
post({type:"use", dev:"padK1", nick:"단우", pad:1, day:today, m:{esc:14}, ver:"v654"});
ok(U.d.length===4 && U.d[2][1]==="라언" && U.d[3][1]==="단우" && U.d[2][c("저택 탈출(분)")]===15, "공용 패드 = 고른 아이마다 한 줄");
post({type:"use", dev:"devJH", nick:"김지환", day:old, m:{run:50}, ver:"v654"});
ok(!post({type:"use", dev:"", nick:"x", day:today, m:{run:1}}).ok && !post({type:"use", dev:"d", day:"11/10", m:{run:1}}).ok, "누구인지·날짜가 없으면 안 받음");
const R=post({type:"report", tk:"K"}).rep.use, M={}; R.modes.forEach(r=>{ M[r[0]]=r; });
ok(R.kids===3 && M.study[2]===20 && M.study[3]===1 && M.esc[2]===29 && M.esc[3]===2 && M.town[2]===7 && M.board[2]===9.5 && M.run[2]===3 && M.raid[2]===0 && R.modes.length===10, "선생님 화면: 최근 14일 모드마다 분·아이 수 (20일 전 것은 빠짐 · 안 쓴 모드 0) "+JSON.stringify(R.modes.map(r=>[r[1],r[2],r[3]])));
console.log(bad ? "FAIL "+bad : "PASS"); process.exit(bad?1:0);
