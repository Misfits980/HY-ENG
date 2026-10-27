// (v404) Code.gs 🏷 태그 — 구글 Apps Script 를 가짜 시트로 노드에서 돌려 봄 (node tools/tests/gs_tag.js)
const fs=require("fs"), vm=require("vm"), path=require("path");
const src=fs.readFileSync(path.join(__dirname,"..","..","server","Code.gs"),"utf8");
function Sheet(name){ const S={name, d:[], fmt:{}};
  const cell=(r,c)=>{ while(S.d.length<r) S.d.push([]); const row=S.d[r-1]; while(row.length<c) row.push(""); return row; };
  function Range(r,c,nr,nc){ return {
    getValue(){ const row=S.d[r-1]; return row && row[c-1]!==undefined ? row[c-1] : ""; },
    getValues(){ const o=[]; for(let i=0;i<nr;i++){ const row=S.d[r-1+i]||[]; const a=[]; for(let j=0;j<nc;j++) a.push(row[c-1+j]!==undefined?row[c-1+j]:""); o.push(a); } return o; },
    getDisplayValues(){ return this.getValues().map(a=>a.map(String)); },
    setValue(v){ const row=cell(r,c); row[c-1]=(S.fmt[c]==="@" && v!=="" && typeof v!=="object")?String(v):v; return this; },
    setValues(V){ V.forEach((a,i)=>a.forEach((v,j)=>{ const row=cell(r+i,c+j); row[c-1+j]=(S.fmt[c+j]==="@")?String(v):v; })); return this; },
    setNumberFormat(f){ if(f==="@") for(let j=0;j<nc;j++) S.fmt[c+j]="@"; return this; }, setFontWeight(){ return this; } }; }
  return Object.assign(S, {
    getRange(a,b,c,d){ if(typeof a==="string"){ if(a==="A:A") return Range(1,1,1,1); return Range(1,1,1,1); } return Range(a,b,c||1,d||1); },
    getLastRow(){ let n=S.d.length; while(n>0 && !(S.d[n-1]||[]).some(v=>v!=="" && v!==undefined)) n--; return n; },
    appendRow(a){ const n=this.getLastRow()+1; a.forEach((v,j)=>{ cell(n,j+1)[j]=v; }); },
    setFrozenRows(){}, setColumnWidth(){}, deleteRows(){} }); }
const book={}; book.scores=Sheet("scores");
const ctx={ SpreadsheetApp:{ openById:()=>({ getSheetByName:n=>book[n]||null, insertSheet:n=>(book[n]=Sheet(n)) }) },
  LockService:{ getScriptLock:()=>({waitLock(){}, releaseLock(){}}) },
  ContentService:{ createTextOutput:t=>({ setMimeType(){ return this; }, getContent:()=>t }), MimeType:{JSON:1} },
  PropertiesService:{ getScriptProperties:()=>({ getProperty:()=>"K" }) },
  Utilities:{ formatDate:(d)=>new Date(d).toISOString().slice(0,16) }, Logger:{log(){}}, console };
vm.createContext(ctx); vm.runInContext(src, ctx);
const post=(o)=>JSON.parse(ctx.doPost({postData:{contents:JSON.stringify(Object.assign({key:"HYENG"},o))}}).getContent());
const get=(p)=>JSON.parse(ctx.doGet({parameter:Object.assign({key:"HYENG"},p)}).getContent());
let bad=0; const ok=(c,m)=>{ console.log((c?"OK  ":"BAD ")+m); if(!c) bad++; };
let r=post({type:"tag", dev:"devA", nick:""}); ok(!r.ok && r.err==="noname", "이름이 없으면 태그 없음");
r=post({type:"tag", dev:"devA", nick:"스트로베리"}); ok(r.ok && r.tag==="0006", "첫 아이 = #0006 "+JSON.stringify(r));
const T=book["태그"].d; ok(T[1][0]==="0000" && T[2][0]==="0001" && T[6][0]==="0005" && /공용 패드 1/.test(T[2][6]), "태그 탭: 0000 나 · 0001~0005 공용 패드 미리");
r=post({type:"tag", dev:"devB", nick:"민준"}); ok(r.tag==="0007", "다음 아이 #0007");
r=post({type:"tag", dev:"devA", nick:"딸기"}); ok(r.tag==="0006" && T[7][3]==="딸기" && T[7][2]==="스트로베리", "이름을 바꿔도 같은 #0006 · 지금 이름만 바뀜 (처음 이름 남음)");
r=post({type:"tag", dev:"pad1", nick:"한양패드1", pad:1}); ok(r.tag==="0001", "공용 패드 = #0001");
for(let i=2;i<=5;i++) post({type:"tag", dev:"pad"+i, nick:"패드"+i, pad:1});
r=post({type:"tag", dev:"pad6", nick:"한양패드6", pad:1}); ok(!r.ok && r.err==="nopad", "공용 패드 자리는 5개뿐");
r=post({type:"tagMe", dev:"teach", tk:"X"}); ok(!r.ok && r.err==="badkey", "#0000 은 선생님 열쇠가 있어야");
r=post({type:"tagMe", dev:"teach", tk:"K"}); ok(r.ok && r.tag==="0000" && post({type:"tag", dev:"teach", nick:"선생님"}).tag==="0000", "선생님 기기 = #0000");
r=post({type:"tagSet", tk:"K", tag:"0007", dev:"devB2", nick:"민준"}); ok(r.ok && post({type:"tag", dev:"devB2", nick:"민준"}).tag==="0007" && post({type:"tag", dev:"devB", nick:"민준"}).tag==="0007", "태그에 기기 더하기: 민준 새 기기도 #0007 (옛 기기도 그대로)");
r=post({type:"tagMe", dev:"teach2", tk:"K"}); ok(post({type:"tag", dev:"teach", nick:"선생님"}).tag==="0000" && post({type:"tag", dev:"teach2", nick:"선생님"}).tag==="0000", "선생님 기기 2대 모두 #0000");
const k0=post({type:"tag", dev:"kidX", nick:"딸기"}).tag; post({type:"tagSet", tk:"K", tag:"0006", dev:"kidX"}); ok(k0==="0008" && post({type:"tag", dev:"kidX", nick:"딸기"}).tag==="0006" && book["태그"].d.some(row=>row[0]===k0 && row[1]===""), "잘못 받은 태그 → 맞는 태그에 더하면 잘못 받은 줄은 기기가 빠짐");
book["태그"].d[4][1]="padPre"; ok(post({type:"tag", dev:"padPre", nick:"루아"}).tag==="0003", "태그 탭에 패드 기기를 미리 적어 두면 그 번호 (패드 이름이 '루아' 여도)");
book["태그"].d[1][1]="tA, tB"; ok(post({type:"tag", dev:"tB", nick:"선생님"}).tag==="0000", "기기 칸에 쉼표로 여러 기기");
r=post({type:"tags", tk:"K"}); ok(r.ok && r.list.some(x=>x.tag==="0006" && x.nick==="딸기"), "태그 목록");
// 기록·랭킹
post({nick:"스트로베리", score:500, diff:"easy", rule:"normal", tag:"0006"}); post({nick:"딸기", score:800, diff:"easy", rule:"normal", tag:"6"});
post({nick:"민준", score:300, diff:"easy", rule:"normal", tag:"0007"}); post({nick:"민준", score:700, diff:"easy", rule:"normal", tag:"0008"});
const sc=book.scores.d, ti=sc[0].indexOf("태그"); ok(ti>=0 && sc[2][ti]==="#0006" && sc[0][sc[0].length-1]==="주인 패드", "scores '태그' 칸 (6 → #0006, 글자라 0 이 안 없어짐) · (v417) 맨 끝은 「주인 패드」");
const L=get({diff:"easy", range:"all"}).list; console.log(JSON.stringify(L));
ok(L.length===3 && L[0].nick==="딸기" && L[0].tag==="0006" && L[0].score===800, "랭킹: 이름을 바꾼 아이는 한 줄 (가장 최근 이름 · 최고 점수)");
ok(L.filter(x=>x.nick==="민준").length===2, "같은 이름 민준 둘 = 태그가 달라 두 줄");
post({type:"name", dev:"devA", old:"스트로베리", nick:"딸기", how:"무료권", tag:"0006"}); ok(book["이름"].d[1][6]==="#0006", "이름 탭에 태그");
book["조치"]=Sheet("조치"); post({type:"actAdd", tk:"K", who:"#0006", kind:"보석", value:"+10"});
ok(get({act:1, nick:"딸기", dev:"devA", tag:"0006"}).list.length===1 && get({act:1, nick:"딸기", dev:"devX", tag:"0007"}).list.length===0, "조치 대상에 #태그");
console.log("DONE bad="+bad); process.exit(bad?1:0);
