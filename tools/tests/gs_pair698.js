// (v690) Code.gs 서버 v24 — 🏡 My Town 잠금 「오늘의 30 Stage 3개」를 학원 패드·집 기기 합쳐 셈 (scores 끝 「마을 칸」 tw · board 답 me.tw · me.twd) (node tools/tests/gs_town689.js)
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

// 시간 고정: 2026-11-18(수) 15:00 한국 시간 → 이번 주 = 11/16(월)~ · 짝은 11/2~11/15 에 공부한 아이
const NOW=Date.UTC(2026,10,18,6,0,0), H=3600e3, KST=d=>Date.UTC(2026,d[0]-1,d[1],d[2]-9,d[3]||0,0);
vm.runInContext("Date.now=()=>"+NOW, ctx);
vm.runInContext("CacheService={getScriptCache:()=>({get(){return null}, put(){}, remove(){}})}", ctx);
ok(post({type:"check", tk:"K"}).v>=25, "SERVER_V ≥ 25");
const COLS=vm.runInContext("COLS.map(c=>c[0])", ctx), S=book.scores;
S.d=[vm.runInContext("COLS.map(c=>c[1])", ctx)];
const add=(t,o)=>{ S.d.push(COLS.map(k=>k==="date"?new Date(t):(o[k]!==undefined?o[k]:""))); };
const st=(who,t,tw)=>add(t, Object.assign({}, who, {diff:"study", rule:"study", set:"G3-4 Stage", right:10, score:100, clear:1, tw:tw||""}));
const K=[["ACE","#0006"],["BEE","#0007"],["CAT","#0008"],["DOG","#0009"],["EGG","#0010"]].map(([n,t])=>({nick:n, tag:t, dev:"d"+n}));
const T0={nick:"👤루아", tag:"", dev:"pad1"}, TCH={nick:"선생님", tag:"#0000", dev:"dT"}, PAD={nick:"한양패드1", tag:"", dev:"pad2"};
// 지난 2주 (짝 정하는 기간)
K.forEach((k,i)=>st(k, KST([11,5+i,16]), "x"));
st(T0, KST([11,10,16]), "x"); st(TCH, KST([11,10,16]), "x"); st(PAD, KST([11,10,16]), "x");
// 이번 주 Stage
st(K[0], KST([11,16,16]), "s1"); st(K[0], KST([11,16,16,30]), "s1"); st(K[0], KST([11,17,16]), "s1"); st(K[0], KST([11,17,16,30]), "s2");   // ACE: 같은 날 같은 칸 1 → 3
st(K[1], KST([11,16,17]), "s1"); st(K[1], KST([11,16,17,10]), "");   // BEE 1 (못 끝낸 판 빼고)
const NEW={nick:"NEW", tag:"#0011", dev:"dN"}; st(NEW, KST([11,17,10]), "s1");   // 이번 주에 처음 = 다음 주부터 짝
const b=(p)=>get(Object.assign({board:1}, p)).me||{};
const me=b({tag:"0006", nick:"ACE"}).pq, Q=vm.runInContext("pairs_", ctx);
ok(me && me.mem && me.mem.length>=2, "ACE 에게 짝이 있음 "+JSON.stringify(me));
const all=["0006","0007","0008","0009","0010"].map(t=>b({tag:t, nick:"x"}).pq).filter(Boolean);
const lu=b({tag:"", nick:"루아"}).pq;
ok(all.length===5 && !!lu, "지난 2주 공부한 아이 6명(태그 5 + 공용 패드 루아) 모두 짝 · 선생님·패드 이름 빼고");
const sizes=[...all, lu].map(x=>x.mem.length); ok(sizes.every(n=>n===2||n===3) && sizes.filter(n=>n===3).length===0, "6명 = 둘씩 셋 "+JSON.stringify(sizes));
ok(!b({tag:"0000", nick:"선생님"}).pq && !b({tag:"0011", nick:"NEW"}).pq, "선생님·이번 주 처음 온 아이 = 짝 없음");
const aceM=me.mem.find(x=>x.me), other=me.mem.find(x=>!x.me);
ok(aceM && aceM.c===3 && aceM.n==="ACE", "ACE 이번 주 Stage 3 (같은 날 같은 칸 1) "+JSON.stringify(aceM));
ok(me.sum===me.mem.reduce((a,x)=>a+x.c,0) && me.goal===15, "합 · 목표 15 "+me.sum);
const again=b({tag:"0006", nick:"ACE"}).pq; ok(JSON.stringify(again.mem.map(x=>x.n))===JSON.stringify(me.mem.map(x=>x.n)), "같은 주엔 짝이 안 바뀜");
// 응원
const r1=post({type:"cheer", tag:"0006", nick:"ACE", m:1}); ok(r1.ok, "응원 보내기 ok");
const P2=book["짝 응원"]; ok(P2 && P2.d.length===2 && P2.d[1][5]===1, "「짝 응원」 탭에 한 줄");
const otherTag=all.find(x=>x.mem.some(m=>m.n==="ACE") && !x.mem.find(m=>m.me && m.n==="ACE"));
const theirs=[["0007","BEE"],["0008","CAT"],["0009","DOG"],["0010","EGG"]].map(([t,n])=>[n, b({tag:t, nick:n}).pq]).find(([n,q])=>q.mem.some(m=>m.n==="ACE"));
ok(theirs && theirs[1].ch.length===1 && theirs[1].ch[0][0]==="ACE" && theirs[1].ch[0][1]===1, "짝이 받은 응원 "+JSON.stringify(theirs && theirs[1].ch));
post({type:"cheer", tag:"0006", nick:"ACE", m:0}); post({type:"cheer", tag:"0006", nick:"ACE", m:2});
const r4=post({type:"cheer", tag:"0006", nick:"ACE", m:0}); ok(!r4.ok && r4.err==="max", "하루 3번까지");
ok(post({type:"cheer", tag:"0011", nick:"NEW", m:0}).err==="nopair", "짝 없는 아이 응원 = nopair");
// 다음 주 = 새로 섞음 (같은 아이들)
vm.runInContext("Date.now=()=>"+(NOW+7*24*H), ctx);
const nx=b({tag:"0006", nick:"ACE"}).pq; ok(nx && nx.ws!==me.ws && nx.sum<=nx.goal, "다음 주 = 새 주 · 새 합 "+JSON.stringify([nx && nx.ws, nx && nx.sum]));
console.log("DONE bad="+bad); process.exit(bad?1:0);
