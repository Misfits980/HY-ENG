// (v631) Code.gs 서버 v15 — 🏆 아이마다 랭킹 단계 (시트 「태그」 H칸 · 관리자 tagLv) (node tools/tests/gs_rank631.js)
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
const t=now-2*H;
// 가온 = 쉬운 G1-2 를 많이 → 자동 단계 G1-2 (다 셈) · G3-4 한 판
st(A,t,"G1-2 Stage 1-1",10); st(A,t+1e3,"G1-2 Stage 1-2",10); st(A,t+2e3,"G1-2 Stage 1-3",10); st(A,t+3e3,"G3-4 Stage 1-1",5);
run(A,t,"basic",800); run(A,t+1e3,"elem",300);
// 나래 = G5-6 · 다솜 = G3-4
st(B,t,"G5-6 Stage 1-1",8); st(Cc,t,"G3-4 Stage 1-1",7); run(Cc,t,"elem",400);
const H8=vm.runInContext("TAG_COLS.map(c=>c[1])", ctx);
ok(H8.length===8 && H8[7]==="랭킹 단계" && book["태그"].d[0][7]==="랭킹 단계", "태그 탭 H칸 = 랭킹 단계 "+JSON.stringify(book["태그"].d[0]));
const sc=(b,k,n)=>{ const x=(b.boards[k]||[]).find(y=>y.nick===n); return x ? x.score : null; };
let b=get({board:1});
ok(sc(b,"study","가온")===385 && sc(b,"run","가온")===800, "자동 = G1-2 → 가온 G1-2 판도 셈 (공부 "+sc(b,"study","가온")+" · 달리기 "+sc(b,"run","가온")+")");
let L=post({type:"tags", tk:"K"}).list; const la=L.find(x=>x.tag==="0006");
ok(la && la.rlv==="" && la.auto==="G1-2", "tags 목록: rlv 빈칸 · auto=G1-2 "+JSON.stringify(la));
// 관리자 창에서 가온 → G3-4
ok(!post({type:"tagLv", tk:"X", tags:["0006"], lv:"G3-4"}).ok, "열쇠 없으면 못 바꿈");
ok(!post({type:"tagLv", tk:"K", tags:["0006"], lv:"G9"}).ok, "없는 단계 = 안 됨");
let r=post({type:"tagLv", tk:"K", tags:["0006"], lv:"G3-4"});
ok(r.ok && book["태그"].d.find(x=>x[0]==="0006")[7]==="G3-4", "tagLv → 시트 H칸 G3-4 "+JSON.stringify(r));
b=get({board:1});
ok(sc(b,"study","가온")===55 && sc(b,"run","가온")===300, "가온 G3-4 → G1-2 판·basic 달리기 안 셈, G3-4 만 (공부 "+sc(b,"study","가온")+" · 달리기 "+sc(b,"run","가온")+")");
let me=get({board:1, tag:"0006"}).me;
ok(me.study && me.study.lv==="G3-4" && me.study.fix===1, "나 = 내 단계 G3-4 · 🔒 fix "+JSON.stringify(me.study));
ok(get({board:1, tag:"0008"}).me.study.fix===0, "다솜 = 자동 (fix 0)");
// 높은 단계는 셈: 나래(G5-6) 를 G3-4 로 → 그대로
post({type:"tagLv", tk:"K", tags:["0007"], lv:"G3-4"}); b=get({board:1});
ok(sc(b,"study","나래")===88, "정한 단계보다 높은 판은 셈 (나래 G5-6 = "+sc(b,"study","나래")+")");
// 여러 명 한꺼번에 빼기
post({type:"tagLv", tk:"K", tags:["0007","0008"], lv:"빼기"}); b=get({board:1});
ok(sc(b,"study","나래")===null && sc(b,"study","다솜")===null && sc(b,"run","다솜")===null && sc(b,"study","가온")===55, "빼기 = 랭킹에 안 나옴 (가온은 그대로)");
// 시트에서 바로 고치기 (자동으로 되돌리기 · 글자 그대로 「중등」)
const row=book["태그"].d.find(x=>x[0]==="0007"); row[7]="";
book["태그"].d.find(x=>x[0]==="0006")[7]="중등"; vm.runInContext("RLV_=null; RLV_", ctx);
b=get({board:1});
ok(sc(b,"study","나래")===88 && sc(b,"study","다솜")===null && sc(b,"study","가온")===null && sc(b,"run","가온")===null, "시트에서: 나래 빈칸 = 자동 (다시 나옴) · 가온 중등 = G3-4 판도 안 셈");
post({type:"tagLv", tk:"K", tags:["0006","0008"], lv:"자동"}); b=get({board:1});
ok(book["태그"].d.find(x=>x[0]==="0006")[7]==="" && sc(b,"study","가온")===385 && sc(b,"study","다솜")===77, "자동 = 빈칸 · 다 돌아옴");
ok(!post({type:"tagLv", tk:"K", tags:["0000"], lv:"빼기"}).ok, "#0000 (선생님) 은 못 바꿈");
console.log("DONE bad="+bad); process.exit(bad?1:0);
