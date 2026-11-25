// (v723 · 서버 v27) 🔐 아이 계정 — Code.gs 를 가짜 시트·가짜 Firebase 로 노드에서 돌려 봄 (node tools/tests/gs_acct723.js)
// 만들기(아이디·이름·생일 검사) · 비밀번호(HMAC 만 저장) · 틀림 5번 5분 / 10번 선생님 · 새 기기 승인 · 태그 기기 = 바로 · 승인 없이 기간 · 출입증(FB_SECRET HS256) · 새로 받기 · 기기 빼기 · 이름 바꾸기(같은 반 막기) · 졸업
const fs = require("fs"), vm = require("vm"), path = require("path"), crypto = require("crypto");
const src = fs.readFileSync(path.join(__dirname, "..", "..", "server", "Code.gs"), "utf8");
function Sheet(name){ const S = {name, d:[]};
  const cell = (r, c)=>{ while (S.d.length < r) S.d.push([]); const row = S.d[r - 1]; while (row.length < c) row.push(""); return row; };
  function Range(r, c, nr, nc){ return {
    getValue(){ const row = S.d[r - 1]; return row && row[c - 1] !== undefined ? row[c - 1] : ""; },
    getValues(){ const o = []; for (let i = 0; i < nr; i++){ const row = S.d[r - 1 + i] || []; const a = []; for (let j = 0; j < nc; j++) a.push(row[c - 1 + j] !== undefined ? row[c - 1 + j] : ""); o.push(a); } return o; },
    setValue(v){ cell(r, c)[c - 1] = v; return this; },
    setValues(V){ V.forEach((a, i)=>a.forEach((v, j)=>{ cell(r + i, c + j)[c - 1 + j] = v; })); return this; },
    setNumberFormat(){ return this; }, setFontWeight(){ return this; }, setDataValidation(){ return this; } }; }
  return Object.assign(S, {
    getRange(a, b, c, d){ if (typeof a === "string") return Range(1, 1, 1, 1); return Range(a, b, c || 1, d || 1); },
    getLastRow(){ let n = S.d.length; while (n > 0 && !(S.d[n - 1] || []).some(v=>v !== "" && v !== undefined)) n--; return n; },
    appendRow(a){ const n = this.getLastRow() + 1; a.forEach((v, j)=>{ cell(n, j + 1)[j] = v; }); },
    setFrozenRows(){}, setTabColor(){}, setColumnWidth(){} }); }
let NOW = 1764000000000, FBC = 200;
class FDate extends Date { constructor(...a){ if (!a.length) super(NOW); else super(...a); } static now(){ return NOW; } }
const book = {}, props = {ADMIN_KEY:"TK", FB_SECRET:"SECRET123"}, cache = {}, fbCalls = [];
const sbytes = buf=>Array.from(buf).map(b=>(b > 127 ? b - 256 : b));
const ctx = {
  Date:FDate, console, JSON, Math,
  SpreadsheetApp:{openById:()=>({getSheetByName:n=>book[n] || null, insertSheet:n=>(book[n] = Sheet(n))}), newDataValidation:()=>({requireValueInList(){ return this; }, setAllowInvalid(){ return this; }, setHelpText(){ return this; }, build(){ return {}; }})},
  LockService:{getScriptLock:()=>({waitLock(){}, releaseLock(){}})},
  ContentService:{createTextOutput:t=>({setMimeType(){ return this; }, getContent:()=>t}), MimeType:{JSON:1}},
  PropertiesService:{getScriptProperties:()=>({getProperty:k=>(k in props ? props[k] : null), setProperty:(k, v)=>{ props[k] = String(v); }, deleteProperty:k=>{ delete props[k]; }})},
  CacheService:{getScriptCache:()=>({get:k=>(cache[k] && cache[k].until > NOW ? cache[k].v : null), put:(k, v, s)=>{ cache[k] = {v:String(v), until:NOW + s * 1000}; }, remove:k=>{ delete cache[k]; }})},
  UrlFetchApp:{fetch:(u, o)=>{ fbCalls.push({u, m:o.method, p:o.payload}); return {getResponseCode:()=>FBC, getContentText:()=>'{"on":1}'}; }},
  Utilities:{getUuid:()=>crypto.randomUUID(), formatDate:d=>new Date(d).toISOString().slice(0, 10),
    computeDigest:(a, s)=>sbytes(crypto.createHash("sha256").update(String(s), "utf8").digest()), DigestAlgorithm:{SHA_256:1}, Charset:{UTF_8:1},
    computeHmacSha256Signature:(v, k)=>sbytes(crypto.createHmac("sha256", String(k)).update(String(v), "utf8").digest()),
    base64EncodeWebSafe:x=>Buffer.from(typeof x === "string" ? Buffer.from(x, "utf8") : Uint8Array.from(x.map(b=>(b < 0 ? b + 256 : b)))).toString("base64").replace(/\+/g, "-").replace(/\//g, "_")},
  Session:{}, Logger:{log(){}}
};
vm.createContext(ctx); vm.runInContext(src, ctx);
const post = o=>JSON.parse(ctx.doPost({postData:{contents:JSON.stringify(Object.assign({key:"HYENG"}, o))}}).getContent());
let bad = 0; const ok = (c, m)=>{ console.log((c ? "OK  " : "BAD ") + m); if (!c) bad++; };
{ const C = {}; (src.match(/^function\s+([A-Za-z0-9_$]+)\s*\(/mg) || []).forEach(x=>{ const n = x.replace(/^function\s+|\s*\($/g, ""); C[n] = (C[n] || 0) + 1; });
  const D = Object.keys(C).filter(k=>C[k] > 1); ok(!D.length, "같은 이름 함수 없음 " + D.join(",")); }
const T = (type, o)=>post(Object.assign({type, tk:"TK"}, o || {}));
ok(post({type:"acctList"}).err === "badkey", "선생님 열쇠 없으면 계정 목록 안 됨");
let r = T("acctMake", {list:[
  {rid:"r1", n:"토토", t:"돌고래반", id:"toto", bd:"150309"},
  {rid:"r2", n:"별사탕", t:"돌고래반", id:"byul", bd:"150309"},
  {rid:"r3", n:"토토", t:"돌고래반", id:"totob", bd:"141201"},
  {rid:"r4", n:"토토", t:"사자반", id:"totoc", bd:"141201"},
  {rid:"r5", n:"콩콩", t:"사자반", id:"toto", bd:"141201"},
  {rid:"r6", n:"뭉치", t:"사자반", id:"Mu1", bd:"141201"},
  {rid:"r7", n:"젤리", t:"사자반", id:"jelly", bd:"149999"},
  {rid:"r8", n:"선생님", t:"사자반", id:"teach", bd:"141201"},
  {rid:"r9", n:"관리", t:"사자반", id:"admin", bd:"141201"}]});
const RS = {}; (r.res || []).forEach(x=>{ RS[x.id + "|" + x.n] = x; });
ok(r.ok && r.made === 3, "만들기 3개 " + JSON.stringify(r.res));
ok(RS["toto|토토"].ok && RS["byul|별사탕"].ok && RS["totoc|토토"].ok, "토토(돌고래) · 별사탕 · 토토(사자반 — 다른 반은 같은 이름 됨)");
ok(RS["byul|별사탕"].sameBirth.length === 1 && RS["byul|별사탕"].sameBirth[0] === "토토", "같은 반 같은 생일 → 알려 줌 (토토)");
ok(RS["totob|토토"].err === "dupname", "같은 반 같은 이름 = 안 됨");
ok(RS["toto|콩콩"].err === "dupid" && RS["mu1|뭉치"].err === "badid" && RS["jelly|젤리"].err === "badbd", "같은 아이디 · 아이디 모양(영어 소문자 3~8) · 생일 모양");
ok(RS["teach|선생님"].err === "badname" && RS["admin|관리"].err === "badid", "선생님 같은 이름 · 쓰면 안 되는 아이디");
const raw = JSON.stringify(book["계정"].d); ok(raw.indexOf("150309") < 0 && raw.indexOf("141201") < 0, "시트에 생일(비밀번호)이 그대로 안 적힘");
ok(props.ACCT_PEPPER && props.ACCT_PEPPER.length === 64, "서버 비밀 PEPPER 저절로 만들어짐");
const L = T("acctList").list; const toto = L.find(x=>x.id === "toto"); ok(L.length === 3 && toto.pk === "생일" && !("salt" in toto) && !("ph" in toto), "목록엔 비밀 값이 안 나감");
// 로그인
ok(post({type:"acctLogin", id:"nobody", pw:"150309", dev:"devAAA1"}).err === "noid", "없는 아이디");
r = post({type:"acctLogin", id:"toto", pw:"000000", dev:"devAAA1"}); ok(r.err === "pw" && r.left === 4, "틀린 비밀번호 → 4번 남음");
for (let k = 0; k < 3; k++) post({type:"acctLogin", id:"toto", pw:"000000", dev:"devAAA1"});
r = post({type:"acctLogin", id:"toto", pw:"000000", dev:"devAAA1"}); ok(r.err === "lock" && r.until === NOW + 300000, "5번 틀림 → 5분 잠김");
ok(post({type:"acctLogin", id:"toto", pw:"150309", dev:"devAAA1"}).err === "lock", "잠긴 동안은 맞아도 안 됨");
NOW += 301000;
for (let k = 0; k < 4; k++) post({type:"acctLogin", id:"toto", pw:"000000", dev:"devAAA1"});
r = post({type:"acctLogin", id:"toto", pw:"000000", dev:"devAAA1"}); ok(r.err === "tlock", "10번 틀림 → 선생님이 풀어야");
ok(post({type:"acctLogin", id:"toto", pw:"150309", dev:"devAAA1"}).err === "tlock", "선생님 잠김은 맞아도 안 됨");
ok(T("acctList").list.find(x=>x.id === "toto").tl === true, "선생님 목록에 잠김 표시");
ok(T("acctUnlock", {uid:toto.uid}).ok, "선생님 잠금 풀기");
r = post({type:"acctLogin", id:"toto", pw:"150309", dev:"devAAA1", n:"갤럭시 탭"}); ok(r.ok && r.wait && /^[0-9a-f]{20}$/.test(r.pid), "처음 보는 기기 → 승인 기다림");
const pid = r.pid; ok(post({type:"acctWait", id:"toto", pid}).wait === true, "아직 승인 전");
let P = T("acctList").list.find(x=>x.id === "toto").pend; ok(P.length === 1 && P[0].n === "갤럭시 탭" && P[0].pid === pid, "선생님 목록에 승인 기다림");
ok(T("acctApprove", {uid:toto.uid, pid, yes:1}).ok, "선생님 승인");
fbCalls.length = 0; r = post({type:"acctWait", id:"toto", pid}); ok(r.ok && r.tok && r.uid === toto.uid && r.dk === "devAAA1" && /^[0-9a-f]{32}$/.test(r.ds), "승인 뒤 → 출입증 + 기기 비밀값");
ok(fbCalls.some(c=>/\/kdev\/k_[0-9a-f]{12}\/devAAA1\.json\?auth=SECRET123$/.test(c.u) && c.m === "put" && c.p === "true"), "서버가 /kdev/<계정>/<기기> = true");
const [h64, p64, s64] = r.tok.split("."), pay = JSON.parse(Buffer.from(p64.replace(/-/g, "+").replace(/_/g, "/"), "base64").toString());
const want = crypto.createHmac("sha256", "SECRET123").update(h64 + "." + p64).digest("base64").replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
ok(s64 === want && JSON.parse(Buffer.from(h64, "base64").toString()).alg === "HS256", "출입증 서명 = FB_SECRET HS256 (옛 방식 Firebase 토큰)");
ok(pay.v === 0 && pay.d.uid === toto.uid && pay.d.dk === "devAAA1" && pay.exp * 1000 === Math.floor(NOW / 1000) * 1000 + 7 * 864e5 && r.exp === pay.exp * 1000, "출입증 안 = uid · 기기 · 7일");
ok(!JSON.stringify(book["계정"].d).includes(r.ds), "기기 비밀값은 서버에 그대로 안 적힘 (SHA-256)");
ok(post({type:"acctWait", id:"toto", pid}).err === "pid", "같은 승인으로 두 번 못 받음");
const ds1 = r.ds;
r = post({type:"acctRenew", uid:toto.uid, dev:"devAAA1", ds:ds1}); ok(r.ok && r.tok && r.acct.id === "toto", "출입증 새로 받기");
ok(post({type:"acctRenew", uid:toto.uid, dev:"devAAA1", ds:"x" + ds1.slice(1)}).err === "gone", "기기 비밀값이 다르면 안 됨");
r = post({type:"acctLogin", id:"toto", pw:"150309", dev:"devAAA1"}); ok(r.ok && r.tok && !r.wait, "승인된 기기 = 다음부터 바로");
ok(post({type:"acctRenew", uid:toto.uid, dev:"devAAA1", ds:ds1}).err === "gone", "다시 로그인하면 옛 기기 비밀값은 끝 (새 값)");
const ds2 = r.ds;
// 거절
r = post({type:"acctLogin", id:"toto", pw:"150309", dev:"devBBB2"}); T("acctApprove", {uid:toto.uid, pid:r.pid, yes:0}); ok(post({type:"acctWait", id:"toto", pid:r.pid}).err === "no", "선생님 「아니에요」 → 거절");
// 하루 지나면 저절로 거절
r = post({type:"acctLogin", id:"toto", pw:"150309", dev:"devCCC3"}); NOW += 864e5 + 1000; ok(post({type:"acctWait", id:"toto", pid:r.pid}).err === "no", "하루 지나면 저절로 거절");
// 태그에 있던 기기 = 바로
ctx.tagSheet_(); book["태그"].d.push(["0012", "oldDev99, kidPhone7", "토토", "토토", "", "", "", ""]);
r = post({type:"acctLogin", id:"toto", pw:"150309", dev:"kidPhone7"}); ok(r.ok && r.tok && !r.wait, "예전부터 그 아이 기기(태그 칸) = 승인 없이 바로");
{ const tg = r.acct && r.acct.tag, TR = book["태그"].d.find(x=>String(x[0]) === tg) || [];
  ok(/^\d{4}$/.test(tg || "") && String(TR[1]).indexOf("kidPhone7") >= 0 && String((book["태그"].d.find(x=>String(x[0]) === "0012") || [])[1]).indexOf("kidPhone7") < 0, "(v28) 로그인한 기기는 계정 태그 줄로 (#" + tg + ") · 다른 줄에서 빠짐"); }
r = post({type:"acctLogin", id:"byul", pw:"150309", dev:"kidPhone7"}); ok(r.ok && r.wait, "남의 태그 기기 = 승인 기다림");
// 승인 없이 기간
fbCalls.length = 0; ok(T("acctOpen", {days:3}).ok && !fbCalls.some(c=>/\/hy\/acon\.json/.test(c.u)), "(v28b) 「승인 없이 3일」 = 계정 켜기와 따로 (계정은 안 켜짐)");
r = post({type:"acctLogin", id:"byul", pw:"150309", dev:"newPad11"}); ok(r.ok && r.tok, "승인 없이 기간 = 바로");
T("acctOpen", {days:0}); ok(post({type:"acctLogin", id:"byul", pw:"150309", dev:"newPad12"}).wait, "기간 끝 = 다시 승인");
// 기기 빼기
fbCalls.length = 0; ok(T("acctDev", {uid:toto.uid, dk:"devAAA1"}).ok && fbCalls.some(c=>/\/kdev\/k_\w+\/devAAA1\.json/.test(c.u) && c.m === "delete"), "선생님 기기 내보내기 → /kdev 지움");
ok(post({type:"acctRenew", uid:toto.uid, dev:"devAAA1", ds:ds2}).err === "gone", "내보낸 기기 = 출입증 못 받음");
// 비밀번호
ok(T("acctPw", {uid:toto.uid, pw:"111111"}).err === "badpw" && T("acctPw", {uid:toto.uid, pw:"123456"}).err === "badpw", "쉬운 비밀번호 막기");
ok(T("acctPw", {uid:toto.uid, pw:"482913"}).ok, "새 비밀번호");
ok(post({type:"acctLogin", id:"toto", pw:"150309", dev:"kidPhone7"}).err === "pw" && post({type:"acctLogin", id:"toto", pw:"482913", dev:"kidPhone7"}).tok, "새 비밀번호로만 들어감");
ok(T("acctList").list.find(x=>x.id === "toto").pk === "바꿈", "목록 = 바꿈 (값은 안 보임)");
ok(T("acctPw", {uid:toto.uid, birth:1}).ok && post({type:"acctLogin", id:"toto", pw:"150309", dev:"kidPhone7"}).tok, "생일로 되돌리기 (선생님이 생일을 다시 안 넣어도)");
// 아이디·이름
ok(T("acctEdit", {uid:toto.uid, id:"byul"}).err === "dupid", "같은 아이디로 못 바꿈");
ok(T("acctEdit", {uid:toto.uid, id:"totoa"}).ok && post({type:"acctLogin", id:"totoa", pw:"150309", dev:"kidPhone7"}).tok, "아이디 바꾸기 → 새 아이디로 로그인");
r = post({type:"acctLogin", id:"totoa", pw:"150309", dev:"kidPhone7"}); const ds7 = r.ds;
ok(post({type:"acctName", uid:toto.uid, dev:"kidPhone7", ds:ds7, name:"별사탕"}).err === "dup", "아이 이름 바꾸기: 같은 반에 있는 이름 = 막힘");
ok(post({type:"acctName", uid:toto.uid, dev:"kidPhone7", ds:ds7, name:"선생님"}).err === "bad", "선생님 같은 이름 막힘");
r = post({type:"acctName", uid:toto.uid, dev:"kidPhone7", ds:ds7, name:"토토로"}); ok(r.ok && r.n === "토토로" && T("acctList").list.find(x=>x.uid === toto.uid).n === "토토로", "다른 이름 = 됨 (계정에 적힘)");
ok(post({type:"acctName", uid:toto.uid, dev:"kidPhone7", ds:"bad", name:"토토"}).err === "gone", "기기 비밀값 없으면 이름 못 바꿈");
ok(T("acctEdit", {uid:toto.uid, n:"별사탕"}).err === "dupname" && T("acctEdit", {uid:toto.uid, t:"사자반"}).ok && T("acctEdit", {uid:toto.uid, n:"토토"}).err === "dupname", "선생님 이름·반 바꾸기도 같은 반 같은 이름 막기");
// 졸업
fbCalls.length = 0; ok(T("acctClose", {uid:toto.uid}).ok && fbCalls.filter(c=>c.m === "delete").length >= 1, "졸업 → 기기 모두 빼기");
ok(post({type:"acctLogin", id:"totoa", pw:"150309", dev:"kidPhone7"}).err === "closed", "졸업한 계정 = 못 들어감");
ok(T("acctMake", {list:[{rid:"r10", n:"토토로", t:"사자반", id:"totoz", bd:"150101"}]}).res[0].ok, "졸업한 아이 이름(토토로)은 같은 반에서 다시 쓸 수 있음");
// 모르는 아이디 여러 번
for (let k = 0; k < 60; k++) post({type:"acctLogin", id:"zzz" + "abcdefghij"[k % 10], pw:"123456", dev:"evil0001"});
ok(post({type:"acctLogin", id:"byul", pw:"150309", dev:"newPad11"}).err === "wait", "모르는 아이디 10분에 60번 → 잠깐 막기");
NOW += 601000; ok(post({type:"acctLogin", id:"byul", pw:"150309", dev:"newPad11"}).tok, "10분 뒤 다시");
ok(post({type:"check", tk:"TK"}).v >= 27, "서버 v27 이상");
// (v27b) Firebase 쓰기가 안 되면 「됐어요」라고 하지 않음
r = T("acctList"); ok(r.fb && r.fb.sec === true && r.fb.code === 200 && r.fb.on === true && !("FB_SECRET" in r.fb) && JSON.stringify(r).indexOf("SECRET123") < 0, "선생님 목록 = Firebase 열쇠 있음·켜짐 (열쇠 값은 안 보냄)");
FBC = 401; r = T("acctOn", {on:1}); ok(r.ok === false && r.err === "fb" && r.why === "401", "FB_SECRET 이 안 맞으면 계정 켜기 = 실패로 알림 (401)");
r = T("acctList"); ok(r.fb.code === 401 && r.fb.on === false, "목록에도 401 · 안 켜짐");
ok(T("acctOpen", {days:3}).ok, "승인 없이 3일은 Firebase 를 안 씀 → 열쇠가 틀려도 됨");
r = post({type:"acctLogin", id:"byul", pw:"150309", dev:"newPad11"}); ok(r.ok === false && r.err === "fb" && !r.tok, "기기를 Firebase 에 못 넣으면 출입증을 안 줌");
FBC = 200; delete props.FB_SECRET; r = T("acctOn", {on:1}); ok(r.err === "fb" && r.why === "nosec", "FB_SECRET 이 없으면 계정 켜기 = 실패 (nosec)");
r = T("acctList"); ok(r.fb.sec === false && r.fb.code === "nosec", "목록 = 열쇠 없음");
props.FB_SECRET = "SECRET123"; ok(T("acctOn", {on:1}).ok, "열쇠를 넣으면 다시 켜짐");
// (v28) 🏷 계정 태그 — 기기가 바뀌어도 같은 태그 · 형제가 한 기기를 써도 안 섞임
{ const TR = ()=>book["태그"].d.slice(1).filter(x=>x[0]), row = t=>TR().find(x=>String(x[0]) === t) || [], devsOf = t=>String(row(t)[1] || "").split(/[\s,]+/).filter(Boolean);
  book["태그"].d.push(["0040", "momPhone1", "몽글", "몽글", new Date(2026, 0, 1), new Date(2026, 10, 20), "", ""]);
  book["태그"].d.push(["0041", "oldPad3", "몽글", "몽글", new Date(2026, 10, 25), new Date(2026, 10, 25), "", ""]);   // 같은 이름 줄이 하나 더 (나중에 생김)
  r = T("acctMake", {list:[{rid:"r20", n:"몽글", t:"돌고래반", id:"monggl", bd:"151010"}, {rid:"r21", n:"포포", t:"돌고래반", id:"popo", bd:"151111"}]}); ok(r.ok && r.made === 2, "몽글 · 포포 계정");
  ok(T("acctOpen", {days:3}).ok, "승인 없이 3일 (시험)");
  const n0 = TR().length;
  r = post({type:"acctLogin", id:"popo", pw:"151111", dev:"momPhone1"}); const tp = r.acct && r.acct.tag;
  ok(r.ok && tp && tp !== "0040" && TR().length === n0 + 1 && row(tp)[3] === "포포" && devsOf(tp).indexOf("momPhone1") >= 0, "형제 기기: 포포가 몽글 기기로 로그인 → 포포 새 태그 #" + tp + " (몽글 태그 아님)");
  ok(devsOf("0040").indexOf("momPhone1") < 0 && row("0040")[3] === "몽글", "그 기기는 몽글 줄에서 빠지고 몽글 줄 이름은 그대로");
  r = post({type:"acctLogin", id:"monggl", pw:"151010", dev:"momPhone1"});
  ok(r.ok && r.acct.tag === "0040" && devsOf("0040").indexOf("momPhone1") >= 0 && devsOf(tp).indexOf("momPhone1") < 0, "몽글이 다시 로그인 → 몽글 태그 #0040 (같은 이름 줄 둘 중 이 아이 기기가 든 줄) · 기기는 몽글 줄로");
  const n1 = TR().length; r = post({type:"acctLogin", id:"monggl", pw:"151010", dev:"newTab9"}); const ds9 = r.ds;
  ok(r.ok && r.acct.tag === "0040" && devsOf("0040").indexOf("newTab9") >= 0 && TR().length === n1, "몽글 새 기기 → 같은 태그 #0040 · 새 줄 안 생김 (랭킹 한 줄)");
  r = post({type:"acctName", uid:r.uid, dev:"newTab9", ds:ds9, name:"몽글이"}); ok(r.ok && row("0040")[3] === "몽글이", "이름 바꾸면 태그 줄 「지금 이름」도");
  const ac = book["계정"].d, H = ac[0], AIt = H.indexOf("태그"), mi = ac.findIndex(x=>x[H.indexOf("아이디")] === "monggl"); const uidM = ac[mi][H.indexOf("계정 번호")]; ac[mi][AIt] = "";
  r = post({type:"acctRenew", uid:uidM, dev:"newTab9", ds:ds9}); ok(r.ok && r.acct.tag === "0040" && String(ac[mi][AIt]) === "0040", "v27 때 로그인한 기기(계정에 태그 없음) = 새로 받을 때 태그 #0040 채움");
  ok(AIt === 18, "계정 탭 머리글 맨 끝에 「태그」 칸 (" + AIt + ")"); }
console.log(bad ? "FAIL " + bad : "ALL OK"); process.exit(bad ? 1 : 0);
