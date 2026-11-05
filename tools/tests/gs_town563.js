// (v563) Code.gs 서버 v8 — 🏝 My Town 칸 · 「마을 현황」 탭 · 플레이(초) 1시간까지 · report.town (node tools/tests/gs_town563.js)
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
const book={}; book.scores=Sheet("scores");
const ctx={ SpreadsheetApp:{ openById:()=>({ getSheetByName:n=>book[n]||null, insertSheet:n=>(book[n]=Sheet(n)) }) },
  LockService:{ getScriptLock:()=>({waitLock(){}, releaseLock(){}}) },
  ContentService:{ createTextOutput:t=>({ setMimeType(){ return this; }, getContent:()=>t }), MimeType:{JSON:1} },
  PropertiesService:{ getScriptProperties:()=>({ getProperty:()=>"K" }) },
  Utilities:{ formatDate:(d)=>new Date(d).toISOString().slice(0,16) }, Logger:{log(){}}, console };
vm.createContext(ctx); vm.runInContext(src, ctx);
const post=(o)=>JSON.parse(ctx.doPost({postData:{contents:JSON.stringify(Object.assign({key:"HYENG"},o))}}).getContent());
let bad=0; const ok=(c,m)=>{ console.log((c?"OK  ":"BAD ")+m); if(!c) bad++; };

ok(post({type:"check", tk:"K"}).v>=8, "SERVER_V ≥ 8");
// 새 게임 줄 — 마을 칸 + 플레이(초) 1시간까지
let r=post({nick:"유이홍", score:100, diff:"study", rule:"study", secs:50760, gems:120, earned:900, tag:"0009", ver:"v563", coin:340, bait:7, bank:1200, gbank:55, tup:"낚싯대2 가방1 밭0"});
ok(r.ok, "판 기록 OK");
const H=book.scores.d[0], row=book.scores.d[1], col=n=>row[H.indexOf(n)];
ok(H.slice(H.indexOf("코인"), H.indexOf("코인")+5).join(",")==="코인,미끼,은행 코인,은행 보석,강화", "scores 마을 5칸 = 코인·미끼·은행 코인·은행 보석·강화 "+H.slice(-6).join(","));
ok(col("플레이(초)")===3600, "플레이(초) 50760 → 3600 (1시간까지)");
ok(col("코인")===340 && col("미끼")===7 && col("은행 코인")===1200 && col("은행 보석")===55 && col("강화")==="낚싯대2 가방1 밭0", "마을 칸 값");
ok(col("점수")===100 && col("보석")===120, "다른 칸은 그대로");
// 옛 게임 줄 — 마을 칸 없음
post({nick:"민준", score:50, diff:"easy", rule:"normal", secs:120, gems:30, earned:40, tag:"0007", ver:"v555"});
const row2=book.scores.d[2], c2=n=>row2[H.indexOf(n)];
ok(c2("코인")==="" && c2("미끼")==="" && c2("강화")==="" && c2("플레이(초)")===120, "옛 게임 줄: 마을 칸은 빈 칸 · 플레이(초) 그대로");
// 마을 현황
const T=book["마을 현황"]; ok(!!T, "「마을 현황」 탭이 생김");
const TH=T.d[0]; ok(TH.join(",")==="아이,태그,마지막,보석,모은 보석,코인,미끼,은행 코인,은행 보석,강화,버전", "마을 현황 머리 줄 "+TH.join(","));
const find=(f)=>T.d.slice(1).find(f), byTag=t=>find(x=>x[1]==="#"+t);
let y=byTag("0009"); ok(y && y[0]==="유이홍" && y[3]===120 && y[4]===900 && y[5]===340 && y[6]===7 && y[7]===1200 && y[8]===55 && y[9]==="낚싯대2 가방1 밭0" && y[10]==="v563", "유이홍 #0009 한 줄 "+JSON.stringify(y));
let m=byTag("0007"); ok(m && m[3]===30 && m[5]==="" && m[9]==="", "옛 게임 아이도 보석은 적힘 (마을 칸은 빈 칸)");
// 같은 아이 다음 판 → 같은 줄을 고침
post({nick:"유이홍", score:10, diff:"easy", rule:"normal", secs:30, gems:130, earned:910, tag:"0009", ver:"v563", coin:400, bait:2, bank:1300, gbank:60, tup:"낚싯대3 가방1 밭0"});
ok(T.d.slice(1).filter(x=>x[1]==="#0009").length===1, "같은 태그 = 한 줄");
y=byTag("0009"); ok(y[3]===130 && y[5]===400 && y[6]===2 && y[9]==="낚싯대3 가방1 밭0", "새 값으로 고침");
// 옛 게임 기기에서 한 판 (마을 칸 없음) → 마을 값은 그대로 두고 보석만
post({nick:"유이홍", score:10, diff:"easy", rule:"normal", gems:140, earned:920, tag:"0009", ver:"v560"});
y=byTag("0009"); ok(y[3]===140 && y[5]===400 && y[9]==="낚싯대3 가방1 밭0" && y[10]==="v560", "옛 게임 줄: 마을 값은 전 것 그대로 · 보석·버전만 새로");
// 태그 없는 아이 (공용 패드 👤) → 이름으로 · 나중에 태그가 생기면 그 줄을 이어 씀
post({nick:"👤라언", score:10, diff:"study", rule:"study", gems:5, earned:5, coin:3, bait:1, tag:""});
post({nick:"라언", score:10, diff:"study", rule:"study", gems:6, earned:6, coin:4, bait:1});
ok(T.d.slice(1).filter(x=>x[0]==="라언").length===1 && find(x=>x[0]==="라언")[3]===6, "태그 없으면 👤 뗀 이름으로 한 줄");
post({nick:"라언", score:10, diff:"study", rule:"study", gems:7, earned:7, coin:9, bait:1, tag:"0012"});
ok(T.d.slice(1).filter(x=>x[0]==="라언").length===1 && byTag("0012") && byTag("0012")[5]===9, "태그가 생기면 이름 줄에 태그를 붙여 이어 씀");
post({nick:"PLAYER", score:10, diff:"easy", rule:"normal", gems:1});
ok(!find(x=>x[0]==="PLAYER"), "이름·태그 없는 PLAYER 는 안 적음");
// 구매 줄은 마을 현황을 안 건드림
const n0=T.getLastRow(); post({type:"buy", nick:"새친구", item:"x", name:"x", kind:"옷", price:10, gems:5, tag:"0020"}); ok(T.getLastRow()===n0, "구매 줄은 마을 현황에 안 적음");
// report.town
r=post({type:"report", tk:"K"}); const tw=r.rep && r.rep.town;
ok(Array.isArray(tw) && tw[0][0]==="아이" && tw.some(x=>x[1]==="#0009" && x[5]==="400"), "report.town = 머리 줄 + 아이 줄 (보이는 글자 그대로)");
console.log("DONE bad="+bad); process.exit(bad?1:0);
