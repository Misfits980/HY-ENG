// (v722) 시트 서버 v26 — 🔐 선생님 기기 연결 시험 (Apps Script 흉내 · node tools/tests/srv722.js)
// 옛 열쇠 → 첫 기기 바로 연결 → 6자리 코드로 둘째 기기 → 옛 열쇠 끄기 → 옛 열쇠 막힘 · 틀린 열쇠 12번 → 잠깐 막힘(맞는 열쇠는 그대로)
const fs = require("fs"), path = require("path"), crypto = require("crypto");
const src = fs.readFileSync(path.join(__dirname, "../../server/Code.gs"), "utf8");
const props = {ADMIN_KEY: "LEGACYKEY123"}, cache = {};
let now = 1764000000000;
const S = {
  PropertiesService: {getScriptProperties: () => ({getProperty: k => (k in props ? props[k] : null), setProperty: (k, v) => { props[k] = String(v); }, deleteProperty: k => { delete props[k]; }})},
  CacheService: {getScriptCache: () => ({get: k => (cache[k] && cache[k].until > now ? cache[k].v : null), put: (k, v, s) => { cache[k] = {v: String(v), until: now + s * 1000}; }, remove: k => { delete cache[k]; }})},
  LockService: {getScriptLock: () => ({waitLock() {}, releaseLock() {}})},
  Utilities: {getUuid: () => crypto.randomUUID(), computeDigest: (a, s) => Array.from(crypto.createHash("sha256").update(String(s), "utf8").digest()).map(b => (b > 127 ? b - 256 : b)),
    DigestAlgorithm: {SHA_256: 1}, Charset: {UTF_8: 1}},
  ContentService: {createTextOutput: t => ({t, setMimeType() { return JSON.parse(this.t); }}), MimeType: {JSON: 1}},
  SpreadsheetApp: {}, UrlFetchApp: {}, Session: {}, Logger: {log() {}},
};
const fn = new Function(...Object.keys(S), src + "\nreturn {doPost, KEY};");
const G = fn(...Object.values(S));
const post = o => G.doPost({postData: {contents: JSON.stringify(Object.assign({key: G.KEY}, o))}});
let bad = 0; const ok = (c, m) => { console.log((c ? "OK  " : "BAD ") + m); if (!c) bad++; };
// (v722 사고) 새 함수 devs_ 가 태그 칸 devs_(v) 를 덮어써서 실제 서버의 태그가 깨졌었음 → 같은 이름 함수가 둘이면 실패
{ const C = {}; (src.match(/^function\s+([A-Za-z0-9_$]+)\s*\(/mg) || []).forEach(x => { const n = x.replace(/^function\s+|\s*\($/g, ""); C[n] = (C[n] || 0) + 1; });
  const D = Object.keys(C).filter(k => C[k] > 1); ok(!D.length, "같은 이름 함수 없음 " + D.join(",")); }

let r = post({type: "check", tk: "LEGACYKEY123"});
ok(r.ok && r.v >= 26 && r.legacy === true && r.devs === 0, "옛 열쇠 = 됨 (legacy · 기기 0) " + JSON.stringify(r));
ok(post({type: "pairMake", tk: "LEGACYKEY123"}).err === "notme", "옛 열쇠로는 6자리 코드 못 만듦");
r = post({type: "pairSelf", tk: "LEGACYKEY123", n: "윈도우 PC · 크롬"});
ok(r.ok && /^[0-9a-f]{64}$/.test(r.tk), "첫 기기 바로 연결 → 64자 무작위 열쇠");
const A = r.tk;
ok(!JSON.stringify(props).includes(A), "서버에는 열쇠가 아니라 SHA-256 값만");
ok(post({type: "pairSelf", tk: "LEGACYKEY123"}).err === "has", "둘째부터는 옛 열쇠로 바로 연결 안 됨");
r = post({type: "check", tk: A}); ok(r.ok && r.legacy === false && r.devs === 1, "연결된 기기 열쇠 = 됨");
r = post({type: "pairMake", tk: A}); ok(r.ok && /^\d{6}$/.test(r.code) && r.ttl === 600, "연결된 기기 → 6자리 코드 " + r.code);
const code = r.code;
ok(post({type: "pairUse", code: "000000" === code ? "111111" : "000000"}).err === "badcode", "틀린 코드 = 안 됨");
r = post({type: "pairUse", code, n: "아이폰 · 사파리"}); ok(r.ok && /^[0-9a-f]{64}$/.test(r.tk) && r.tk !== A, "코드로 둘째 기기 연결");
const B = r.tk;
ok(post({type: "pairUse", code}).err === "badcode", "같은 코드 두 번은 안 됨");
r = post({type: "pairMake", tk: A}); now += 601000; ok(post({type: "pairUse", code: r.code}).err === "badcode", "10분 지난 코드 = 안 됨");
r = post({type: "devList", tk: B}); ok(r.ok && r.list.length === 2 && r.list[1].me && !r.list[0].me && r.list[1].n === "아이폰 · 사파리", "기기 목록 · 이 기기 표시");
ok(post({type: "legacyOff", tk: "LEGACYKEY123", on: 1}).err === "notme", "옛 열쇠 끄기는 연결된 기기에서만");
r = post({type: "legacyOff", tk: A, on: 1}); ok(r.ok && props.ADMIN_LEGACY_OFF === "1", "옛 열쇠 끄기");
ok(post({type: "check", tk: "LEGACYKEY123"}).err === "badkey", "끈 뒤 옛 열쇠 = 막힘");
ok(post({type: "pairSelf", tk: "LEGACYKEY123"}).err === "badkey", "끈 뒤 옛 열쇠로 기기 더하기 = 막힘");
ok(post({type: "check", tk: B}).ok === true, "끈 뒤에도 연결된 기기는 그대로");
r = post({type: "devDel", tk: A, i: 1}); ok(r.ok, "기기 빼기");
ok(post({type: "check", tk: B}).err === "badkey", "뺀 기기 = 막힘");
ok(post({type: "devDel", tk: A, i: 0}).err === "last", "옛 열쇠를 껐으면 마지막 기기는 못 뺌");
// 틀린 열쇠 여러 번
for (let k = 0; k < 12; k++) post({type: "check", tk: "x" + k});
ok(post({type: "check", tk: "nope"}).err === "wait", "틀린 열쇠 12번 → 잠깐 막힘");
ok(post({type: "check", tk: A}).ok === true, "맞는 열쇠는 막히지 않음");
ok(post({type: "pairUse", code: "123456"}).err === "wait", "막힌 동안 코드 넣기도 막힘");
now += 601000;
ok(post({type: "check", tk: "nope"}).err === "badkey", "10분 뒤 다시 (틀리면 badkey)");
r = post({type: "legacyOff", tk: A, on: 0}); ok(r.ok && !("ADMIN_LEGACY_OFF" in props), "옛 열쇠 다시 켜기");
ok(post({type: "check", tk: "LEGACYKEY123"}).ok === true, "다시 켜면 옛 열쇠 됨");
console.log(bad ? "FAIL " + bad : "ALL OK");
process.exit(bad ? 1 : 0);
