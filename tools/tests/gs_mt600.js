// (v600) Code.gs 서버 v9 — 오늘의 30 카드 칸 · 다시 푼 판 · 「마이타운 시간」 탭 (node tools/tests/gs_mt600.js)
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
ok(post({type:"check", tk:"K"}).v===9, "SERVER_V = 9");
const T0=Math.floor((Date.now()-3*864e5)/864e5)*864e5+2*3600e3;   // 사흘 전 한국 11:00 (서버는 7일 안 · 미래 아닌 때만 판 시각으로 적음)
const study=(o)=>post(Object.assign({nick:"👤주호", diff:"study", rule:"study", set:"유치원 장모음 Stage 3-1", clear:1, right:6, wrong:0, secs:60, tag:"0011", dev:"devJU", ver:"v600", at:T0}, o));
study({cn:6, cf:4, cs:3.46});
const H=book.scores.d[0], row=i=>book.scores.d[i], col=(i,n)=>row(i)[H.indexOf(n)];
ok(H.slice(-4).join(",")==="단어 카드,끝까지 본 카드,카드 평균(초),다시 푼 판", "scores 맨 끝 4칸 "+H.slice(-4).join(","));
ok(col(1,"단어 카드")===6 && col(1,"끝까지 본 카드")===4 && col(1,"카드 평균(초)")===3.5 && col(1,"다시 푼 판")===0, "카드 6 · 끝까지 4 · 평균 3.5초 · 처음 = 0");
study({cn:6, cf:1, cs:1.2, at:T0+600000});
ok(col(2,"다시 푼 판")===1, "같은 날 같은 Stage 다시 = 1");
study({set:"유치원 장모음 Stage 3-2", at:T0+700000});
ok(col(3,"다시 푼 판")===0, "다른 Stage = 0");
study({at:T0+86400000});
ok(col(4,"다시 푼 판")===0, "다음 날 같은 Stage = 0");
study({tag:"0012", dev:"devX", nick:"라언", at:T0+800000});
ok(col(5,"다시 푼 판")===0, "다른 아이 = 0");
study({set:"유치원 장모음 Stage 3-2", clear:0, end:"quit", at:T0+900000});
study({set:"유치원 장모음 Stage 3-2", at:T0+950000});
ok(col(7,"다시 푼 판")===1, "끝까지 푼 판 다음이면 1 (중간에 나간 판은 안 셈)");
post({nick:"민준", score:50, diff:"easy", rule:"normal", secs:120, tag:"0007", ver:"v555"});
ok(col(8,"단어 카드")==="" && col(8,"다시 푼 판")==="", "달리기·옛 게임 줄 = 빈 칸");
// 마이타운 시간
let r=post({type:"mt", day:"2026-11-05", dev:"devSA", nick:"스트로베리", tag:"0006", min:12.34, segs:2, ver:"v600"});
ok(r.ok, "mt OK");
const M=book["마이타운 시간"]; ok(!!M && M.d[0].join(",")==="날짜,아이,태그,기기,마이타운(분),들어온 번,마지막,버전,게임 이름", "「마이타운 시간」 탭 머리 줄 "+(M&&M.d[0].join(",")));
ok(M.d[1][0]==="2026-11-05" && M.d[1][1]==="최선아 (스트로베리)" && M.d[1][2]==="#0006" && M.d[1][4]===12.3, "명단 기기로 이름 = 최선아 (스트로베리) · 12.3분 "+JSON.stringify(M.d[1]));
post({type:"mt", day:"2026-11-05", dev:"devSA", nick:"스트로베리", tag:"0006", min:30, segs:3, ver:"v600"});
ok(M.d.length===2 && M.d[1][4]===30 && M.d[1][5]===3, "같은 날 = 같은 줄 덮어씀 (30분 · 3번)");
post({type:"mt", day:"2026-11-05", dev:"devSA", nick:"스트로베리", tag:"0006", min:20, segs:1});
ok(M.d[1][4]===30, "늦게 온 작은 값으로 줄지 않음");
post({type:"mt", day:"2026-11-06", dev:"devSA", nick:"스트로베리", tag:"0006", min:5, segs:1});
ok(M.d.length===3 && M.d[2][0]==="2026-11-06", "다음 날 = 새 줄");
post({type:"mt", day:"2026-11-05", dev:"padK1", nick:"라언", pad:1, min:8});
post({type:"mt", day:"2026-11-05", dev:"padK1", nick:"단우", pad:1, min:9});
ok(M.d.length===5 && M.d[3][1]==="라언" && M.d[4][1]==="단우", "공용 패드 = 고른 아이마다 한 줄");
post({type:"mt", day:"2026-11-05", dev:"devNEW", nick:"빈", min:4});
ok(M.d[5][1]==="빈", "명단에 없는 기기 = 게임 이름");
ok(!post({type:"mt", day:"11/05", dev:"x", min:3}).ok && !post({type:"mt", day:"2026-11-05", min:3}).ok, "날짜·누구 없으면 안 적음");
ok(book.scores.d.length===9, "mt 는 scores 에 안 적음");
console.log("DONE bad="+bad); process.exit(bad?1:0);
