// (v723) 시험용 가짜 서버 — 진짜 Code.gs 를 가짜 시트로 돌리고(POST /gs) · 가짜 Firebase REST(/fb/…​.json) 를 규칙(/kacct · /kdev)처럼 지킴
// node tools/tests/fake_acct_srv.js <port>  → 첫 줄에 READY 를 찍음. GET /db = 지금 Firebase 통째로 (시험이 확인)
const fs = require("fs"), vm = require("vm"), path = require("path"), crypto = require("crypto"), http = require("http");
const src = fs.readFileSync(path.join(__dirname, "..", "..", "server", "Code.gs"), "utf8");
const SECRET = "TESTSECRET", PORT = +process.argv[2] || 8799;
function Sheet(name){ const S = {name, d:[]};
  const cell = (r, c)=>{ while (S.d.length < r) S.d.push([]); const row = S.d[r - 1]; while (row.length < c) row.push(""); return row; };
  function Range(r, c, nr, nc){ return {
    getValue(){ const row = S.d[r - 1]; return row && row[c - 1] !== undefined ? row[c - 1] : ""; },
    getValues(){ const o = []; for (let i = 0; i < nr; i++){ const row = S.d[r - 1 + i] || []; const a = []; for (let j = 0; j < nc; j++) a.push(row[c - 1 + j] !== undefined ? row[c - 1 + j] : ""); o.push(a); } return o; },
    getDisplayValues(){ return this.getValues().map(a=>a.map(String)); },
    setValue(v){ cell(r, c)[c - 1] = v; return this; }, setValues(V){ V.forEach((a, i)=>a.forEach((v, j)=>{ cell(r + i, c + j)[c - 1 + j] = v; })); return this; },
    setNumberFormat(){ return this; }, setFontWeight(){ return this; }, setDataValidation(){ return this; } }; }
  return Object.assign(S, { getRange(a, b, c, d){ if (typeof a === "string") return Range(1, 1, 1, 1); return Range(a, b, c || 1, d || 1); },
    getLastRow(){ let n = S.d.length; while (n > 0 && !(S.d[n - 1] || []).some(v=>v !== "" && v !== undefined)) n--; return n; },
    appendRow(a){ const n = this.getLastRow() + 1; a.forEach((v, j)=>{ cell(n, j + 1)[j] = v; }); }, setFrozenRows(){}, setTabColor(){}, setColumnWidth(){}, deleteRows(){}, getMaxColumns(){ return 99; }, insertColumnsAfter(){} }); }
const book = {}, props = {ADMIN_KEY:"TK", FB_SECRET:SECRET, FB_DB:"http://fake"}, cache = {}, DB = {};
const sbytes = buf=>Array.from(buf).map(b=>(b > 127 ? b - 256 : b));
const parts = p=>String(p || "").split("/").filter(Boolean);
const getAt = p=>{ let o = DB; for (const k of parts(p)){ if (!o || typeof o !== "object") return null; o = o[k]; } return o === undefined ? null : o; };
const setAt = (p, v)=>{ const P = parts(p); if (!P.length) return; let o = DB; for (let i = 0; i < P.length - 1; i++){ if (!o[P[i]] || typeof o[P[i]] !== "object") o[P[i]] = {}; o = o[P[i]]; } if (v === null) delete o[P[P.length - 1]]; else o[P[P.length - 1]] = JSON.parse(JSON.stringify(v)); };
const b64d = s=>Buffer.from(String(s).replace(/-/g, "+").replace(/_/g, "/"), "base64").toString();
function who(auth){ if (!auth) return null; if (auth === SECRET) return {admin:true};
  const [h, p, s] = String(auth).split("."); if (!s) return {bad:1};
  const want = crypto.createHmac("sha256", SECRET).update(h + "." + p).digest("base64").replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
  if (want !== s) return {bad:1}; let o = null; try { o = JSON.parse(b64d(p)); } catch(e){ return {bad:1}; } if (!o || o.v !== 0 || !o.d || (o.exp && o.exp * 1000 < Date.now())) return {bad:1}; return o.d; }
/* 규칙 (firebase-rules.json 과 같은 뜻): /kacct/$uid = 내 uid + /kdev/$uid/<내 기기> == true · /kdev/$uid 읽기 = 내 uid · 쓰기는 서버(비밀)만 */
function allow(p, method, a){ if (a && a.admin) return true; const P = parts(p);
  if (P[0] === "kacct"){ return !!(a && !a.bad && a.uid === P[1] && getAt("kdev/" + P[1] + "/" + a.dk) === true); }
  if (P[0] === "kdev"){ return method === "GET" && !!(a && !a.bad && a.uid === P[1]); }
  return true; }
function fb(method, p, auth, body){ const a = who(auth); if (a && a.bad) return {code:401, v:{error:"Could not parse auth token."}};
  if (!allow(p, method, a)) return {code:401, v:{error:"Permission denied"}};
  if (method === "GET") return {code:200, v:getAt(p)}; if (method === "DELETE"){ setAt(p, null); return {code:200, v:null}; }
  const v = JSON.parse(body || "null"); setAt(p, v); return {code:200, v}; }
const ctx = { console, JSON, Math,
  SpreadsheetApp:{openById:()=>({getSheetByName:n=>book[n] || null, insertSheet:n=>(book[n] = Sheet(n))}), newDataValidation:()=>({requireValueInList(){ return this; }, setAllowInvalid(){ return this; }, setHelpText(){ return this; }, build(){ return {}; }})},
  LockService:{getScriptLock:()=>({waitLock(){}, releaseLock(){}})},
  ContentService:{createTextOutput:t=>({setMimeType(){ return this; }, getContent:()=>t}), MimeType:{JSON:1}},
  PropertiesService:{getScriptProperties:()=>({getProperty:k=>(k in props ? props[k] : null), setProperty:(k, v)=>{ props[k] = String(v); }, deleteProperty:k=>{ delete props[k]; }})},
  CacheService:{getScriptCache:()=>({get:k=>(cache[k] && cache[k].until > Date.now() ? cache[k].v : null), put:(k, v, s)=>{ cache[k] = {v:String(v), until:Date.now() + s * 1000}; }, remove:k=>{ delete cache[k]; }})},
  UrlFetchApp:{fetch:(u, o)=>{ const m = /^http:\/\/fake(\/[^?]*)\.json\?auth=(.*)$/.exec(u); const r = m ? fb((o.method || "get").toUpperCase(), m[1], decodeURIComponent(m[2]), o.payload) : {code:404}; return {getResponseCode:()=>r.code, getContentText:()=>JSON.stringify(r.v)}; }},
  Utilities:{getUuid:()=>crypto.randomUUID(), formatDate:d=>new Date(d).toISOString().slice(0, 10),
    computeDigest:(a, s)=>sbytes(crypto.createHash("sha256").update(String(s), "utf8").digest()), DigestAlgorithm:{SHA_256:1}, Charset:{UTF_8:1},
    computeHmacSha256Signature:(v, k)=>sbytes(crypto.createHmac("sha256", String(k)).update(String(v), "utf8").digest()),
    base64EncodeWebSafe:x=>Buffer.from(typeof x === "string" ? Buffer.from(x, "utf8") : Uint8Array.from(x.map(b=>(b < 0 ? b + 256 : b)))).toString("base64").replace(/\+/g, "-").replace(/\//g, "_")},
  Session:{}, Logger:{log(){}} };
vm.createContext(ctx); vm.runInContext(src, ctx);
const srv = http.createServer((req, res)=>{ let body = ""; req.on("data", c=>{ body += c; }); req.on("end", ()=>{
  const u = new URL(req.url, "http://x"); res.setHeader("Content-Type", "application/json");
  try {
    if (u.pathname === "/gs"){ const out = ctx.doPost({postData:{contents:body}}).getContent(); res.end(out); return; }
    if (u.pathname === "/db"){ res.end(JSON.stringify({db:DB, sheet:book["계정"] ? book["계정"].d : [], tags:book["태그"] ? book["태그"].d : []})); return; }
    if (u.pathname === "/tag"){ const o = JSON.parse(body); ctx.tagSheet_(); book["태그"].d.push(o.row); res.end("{}"); return; }
    if (u.pathname.startsWith("/fb/")){ const p = u.pathname.slice(3).replace(/\.json$/, ""), r = fb(req.method, p, u.searchParams.get("auth"), body); res.statusCode = r.code; res.end(JSON.stringify(r.v)); return; }
    res.statusCode = 404; res.end("{}");
  } catch(e){ res.statusCode = 500; res.end(JSON.stringify({ok:false, err:String(e)})); } }); });
srv.listen(PORT, "127.0.0.1", ()=>console.log("READY " + PORT));
