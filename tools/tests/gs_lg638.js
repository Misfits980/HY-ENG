// (v638) Code.gs 서버 v18 — 🏅 나의 리그 「기준」: 낮은 점수만으로는 칭호 · 넘기 못 함 (node tools/tests/gs_lg638.js)
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
ok(post({type:"check", tk:"K"}).v>=16, "SERVER_V ≥ 16");
const ws=vm.runInContext("weekStart_()", ctx), W=7*864e5, mid=x=>ws - x*W + 2*864e5 + 3600e3;   // x 주 전 수요일
// 같은 단계(G3-4) 6명: 4명은 주마다 1000 · 「낮은」 아이는 주마다 330 · 「오른」 아이는 330 → 700 → 800
const K=["가","나","다","라","낮","오"].map((n,i)=>({nick:n+"이", tag:String(20+i).padStart(4,"0"), dev:"d"+i}));
K.forEach(k=>post({type:"tag", dev:k.dev, nick:k.nick}));
const t0=Date.now()-3600e3;
for(let w=1; w<=3; w++){ K.slice(0,4).forEach((k,i)=>st(k, mid(w)+i*1e3, "G3-4 Stage 1-"+w, 100));
  st(K[4], mid(w)+9e3, "G3-4 Stage 1-"+w, 33);
  st(K[5], mid(w)+9e3, "G3-4 Stage 1-"+w, w===1 ? 80 : w===2 ? 70 : 33); }
st(K[4], t0, "G3-4 Stage 2-1", 40);     // 이번 주 400 > 지난주 330 — 그래도 기준(600) 아래
st(K[5], t0, "G3-4 Stage 2-1", 70);     // 이번 주 700 < 지난주 800 · 기준 이상 → 지킴
const lg=(tag)=>get({board:1, tag}).me.lg;
const top=lg("0020"), low=lg("0024"), up=lg("0025");
const B=Math.round(top.last*0.6);
ok(low && low.bar===B && low.last<B && low.st===0, "낮은 아이: 기준 = 같은 단계 가운데값 60% · 330 만 하던 주는 칭호에 안 셈 "+JSON.stringify(low));
ok(low.goal===B && low.keep===B && low.now>low.last && low.now<B && low.win===0, "낮은 아이: 지난주보다 늘어도 기준 아래면 넘기 아님 "+JSON.stringify([low.goal,low.keep,low.now,low.win]));
ok(up && up.st===2 && up.keep===Math.round(up.last*0.9) && up.now<up.keep && up.win===0, "오른 아이: 기준 넘은 2주만 연속 · 이번 주 아직 못 지킴 "+JSON.stringify(up));
ok(top && top.st===3 && top.bar===B && top.goal===top.last+1, "꾸준한 아이: 3주 연속 · 목표 1001 "+JSON.stringify(top));
console.log("DONE bad="+bad); process.exit(bad?1:0);
