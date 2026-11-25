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

// 시간 고정: 2026-11-12(목) 15:00 한국 시간
const NOW=Date.UTC(2026,10,12,6,0,0), H=3600e3, KST=d=>Date.UTC(2026,d[0]-1,d[1],d[2]-9,d[3]||0,0);
vm.runInContext("Date.now=()=>"+NOW, ctx);
/* 서버가 줄 날짜를 new Date() 로 적음 → 진짜 시계(오늘)가 아니라 시험 시계로 (예전엔 시험을 만든 날 11/12 에만 통과했음) */
vm.runInContext("(function(){ const D0=Date; globalThis.Date=class extends D0{ constructor(...a){ if(!a.length) super(globalThis.Date.now()); else super(...a); } static now(){ return D0.now(); } }; })()", ctx);
ok(post({type:"check", tk:"K"}).v>=24, "SERVER_V ≥ 24");
const COLS=vm.runInContext("COLS.map(c=>c[0])", ctx), S=book.scores;
ok(COLS[COLS.length-1]==="tw", "「마을 칸」(tw) 은 scores 맨 끝 칸 (옛 칸 자리 그대로)");
S.d=[vm.runInContext("COLS.map(c=>c[1])", ctx)];
const add=(t,o)=>{ S.d.push(COLS.map(k=>k==="date"?new Date(t):(o[k]!==undefined?o[k]:""))); };
const st=(who,t,tw,o)=>add(t, Object.assign({}, who, {diff:"study", rule:"study", set:"G3-4 Stage", right:10, wrong:0, score:100, clear:1, tw}, o||{}));
const A={nick:"ACE", tag:"#0006", dev:"dA"}, Apad={nick:"👤ACE", tag:"", dev:"pad1"};
const B={nick:"비비", tag:"#0007", dev:"dB"}, Cpad={nick:"👤씨씨", tag:"", dev:"pad1"}, Dpad={nick:"👤디디", tag:"", dev:"pad2"};
// 어제 (안 셈)
st(Apad, KST([11,11,16]), "g34_9-0"); st(A, KST([11,11,20]), "g34_8-0");
// 오늘 · 학원 패드 (ACE 이름으로)
st(Apad, KST([11,12,9]),  "g34_1-0");
st(Apad, KST([11,12,9,30]), "g34_2-0");
// 오늘 · 집 기기 (같은 Stage 하나 + 새 Stage 하나)
st(A, KST([11,12,13]), "g34_2-0");
st(A, KST([11,12,14]), "g34_3-0");
st(A, KST([11,12,14,10]), "");                                         // 끝까지 못 푼 판(게임이 tw 를 안 붙임) = 안 셈
add(KST([11,12,14,20]), Object.assign({}, A, {diff:"normal", rule:"run", score:900, tw:"g34_7-0"}));   // 공부 줄이 아니면 안 셈
// 다른 아이들
st(B, KST([11,12,10]), "g34_1-0");
st(Cpad, KST([11,12,11]), "g34_1-0"); st(Cpad, KST([11,12,11,20]), "rv"); st(Cpad, KST([11,12,11,40]), "rv");   // 복습 두 판 = 1개
// 0시 지나 (한국 날짜 오늘 0:10 = UTC 어제) → 셈 · 오늘 23:59 처럼 끝 쪽도 확인할 필요 없음(지금 15시)
st(Dpad, KST([11,12,0,10]), "g34_5-0");
st(Dpad, KST([11,11,23,50]), "g34_6-0");                              // 어제 23:50 = 안 셈

const me=(p)=>{ const b=get(Object.assign({board:1}, p)); return b.me||{}; };
const a1=me({tag:"0006", nick:"ACE"});
ok(a1.tw===3, "집 기기(태그 #0006): 학원 패드 2 + 집 2 → 서로 다른 Stage 3개 (같은 것 1개) · 받은 값 "+a1.tw);
ok(a1.twd==="2026-11-12", "센 날 twd = 오늘(한국) "+a1.twd);
ok(JSON.stringify((a1.twk||[]).slice().sort())==='["g34_1-0","g34_2-0","g34_3-0"]', "이름들 twk = 게임이 그 기기 것과 합칠 수 있게 "+JSON.stringify(a1.twk));
const a2=me({tag:"", nick:"ACE"});
ok(a2.tw===3, "학원 공용 패드(태그 없음 · 이름 ACE): 집 기기 것도 합쳐 3 · 받은 값 "+a2.tw);
const b1=me({tag:"0007", nick:"비비"});
ok(b1.tw===1, "비비 1개 (다른 아이 것과 안 섞임) · 받은 값 "+b1.tw);
const c1=me({tag:"", nick:"씨씨"});
ok(c1.tw===2, "씨씨: Stage 1개 + 복습(두 판이어도 1개) = 2 · 받은 값 "+c1.tw);
ok(JSON.stringify((c1.twk||[]).slice().sort())==='["g34_1-0","rv"]', "씨씨 twk "+JSON.stringify(c1.twk));
const d1=me({tag:"", nick:"디디"});
ok(d1.tw===1, "디디: 오늘 0:10 판은 셈 · 어제 23:50 판은 안 셈 → 1 · 받은 값 "+d1.tw);
const e1=me({tag:"0099", nick:"새친구"});
ok(e1.tw===undefined && e1.twd===undefined, "오늘 한 판도 없는 아이 = me.tw 없음");

// 게임이 보낸 판 → 「마을 칸」 에 적힘 → 다음 board 에 바로
const r=post({nick:"비비", tag:"0007", dev:"dB", diff:"study", rule:"study", set:"G3-4 Stage 1-2", score:100, right:10, clear:1, at:NOW-60e3, tw:"g34_1-2-0"});
ok(r.ok, "판 보내기 ok");
const last=S.d[S.d.length-1];
ok(last[COLS.indexOf("tw")]==="g34_1-2-0", "새 줄의 마을 칸 = 보낸 값");
const r2=post({nick:"비비", tag:"0007", dev:"dB", diff:"study", rule:"study", set:"G3-4 Stage 1-3", score:100, right:10, clear:0, at:NOW-30e3});
ok(r2.ok && S.d[S.d.length-1][COLS.indexOf("tw")]==="", "tw 없이 온 판(옛 게임 · 못 끝낸 판) = 빈 칸");
const b2=me({tag:"0007", nick:"비비"});
ok(b2.tw===2, "비비: 보낸 판까지 2 · 받은 값 "+b2.tw);

// 다음 날이 되면 0 부터 (me.tw 없음)
vm.runInContext("Date.now=()=>"+(NOW+24*H), ctx);
const a3=me({tag:"0006", nick:"ACE"});
ok(a3.tw===undefined, "다음 날 = 어제 것 안 셈 (me.tw 없음) "+JSON.stringify([a3.tw, a3.twd]));
console.log("DONE bad="+bad); process.exit(bad?1:0);
