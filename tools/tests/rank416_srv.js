// (v416) 서버 Code.gs 랭킹 「분신술」 — 같은 아이 한 줄 · 공용 패드 단어 수 안 셈 · 선생님 빼기 (node 로 실행)
const fs = require("fs"), vm = require("vm"), path = require("path");
const src = fs.readFileSync(path.join(__dirname, "../../server/Code.gs"), "utf8");
let SH = null;
const ctx = { console, Date, Math, JSON, String, Number, Object, Array, isFinite,
  ContentService: { createTextOutput: s => ({ s, setMimeType(){ return this; } }), MimeType: { JSON: 1 } },
  SpreadsheetApp: { openById: () => ({ getSheetByName: () => SH }) },
  PropertiesService: { getScriptProperties: () => ({ getProperty: () => "" }) } };
vm.createContext(ctx); vm.runInContext(src + "\n;this.__T={dexRank_, people_, plain_, C, COLS, doGet};", ctx);
const { dexRank_, C, COLS } = ctx.__T;
const NOW = Date.now(), DAY = 864e5;
function row(o){ const r = COLS.map(() => ""); Object.keys(o).forEach(k => { r[C[k]] = o[k]; }); return r; }
const rows = [
  // 김지후 — 자기 기기 A: 달리기 「김지후」 · 공부 「👤김지후」
  row({date:new Date(NOW-1*DAY), nick:"김지후", diff:"hard", rule:"normal", dev:"A", dex:211, score:5000}),
  row({date:new Date(NOW-1*DAY), nick:"👤김지후", diff:"study", rule:"study", dev:"A", dex:210, score:100}),
  // 스트로베리 — 자기 기기 B
  row({date:new Date(NOW-1*DAY), nick:"스트로베리", diff:"normal", rule:"normal", dev:"B", dex:856, score:9000}),
  row({date:new Date(NOW-1*DAY), nick:"👤스트로베리", diff:"study", rule:"study", dev:"B", dex:856}),
  // SEOWON — 자기 기기 S (태그 0010, 지난주) + 공용 패드 P 에서 이번 주 한 판
  row({date:new Date(NOW-20*DAY), nick:"SEOWON", diff:"normal", rule:"normal", dev:"S", dex:782, tag:"0010", score:4000}),
  row({date:new Date(NOW-1*DAY), nick:"👤SEOWON", diff:"normal", rule:"normal", dev:"P", dex:1, score:3195}),
  // 박유범 — 자기 기기 Y(지난주 413) · 이번 주는 공용 패드 P 만
  row({date:new Date(NOW-20*DAY), nick:"박유범", diff:"normal", rule:"normal", dev:"Y", dex:413, score:7000}),
  row({date:new Date(NOW-1*DAY), nick:"👤박유범", diff:"normal", rule:"normal", dev:"P", dex:6, score:4784}),
  // 공용 패드 Q (공부만 한 패드) — 두 아이
  row({date:new Date(NOW-1*DAY), nick:"👤민준", diff:"study", rule:"study", dev:"Q", dex:900}),
  row({date:new Date(NOW-1*DAY), nick:"👤서연", diff:"study", rule:"study", dev:"Q", dex:900}),
  row({date:new Date(NOW-30*DAY), nick:"민준", diff:"easy", rule:"normal", dev:"M", dex:120}),
  // 선생님
  row({date:new Date(NOW-1*DAY), nick:"영어선생님", diff:"study", rule:"study-review", dev:"T", dex:3508}),
  // 다른 아이 같은 이름(태그 다름)은 안 섞임
  row({date:new Date(NOW-1*DAY), nick:"하준", diff:"easy", rule:"normal", dev:"H1", dex:50, tag:"0020"}),
  row({date:new Date(NOW-1*DAY), nick:"하준", diff:"easy", rule:"normal", dev:"H2", dex:70, tag:"0021"}),
];
const sh = { getRange: () => ({ getValues: () => rows, getValue: () => "x" }), getLastRow: () => rows.length + 1 }; SH = sh;
const since = NOW - 3*DAY;
const L = dexRank_(sh, rows.length + 1, since, 20, "A");
let bad = 0; const ok = (c, m) => { console.log((c ? "OK  " : "FAIL ") + m); if(!c) bad++; };
const by = n => L.filter(x => x.nick === n);
console.log(JSON.stringify(L));
ok(by("김지후").length === 1 && by("김지후")[0].score === 211 && by("김지후")[0].me, "김지후 한 줄 (달리기·👤공부 묶음) · 나");
ok(by("스트로베리").length === 1 && by("스트로베리")[0].score === 856, "스트로베리 한 줄");
ok(by("SEOWON").length === 1 && by("SEOWON")[0].score === 782 && by("SEOWON")[0].tag === "0010", "SEOWON = 자기 기기 782 · #0010 (공용 패드 1 안 셈)");
ok(by("박유범").length === 1 && by("박유범")[0].score === 413, "박유범 = 이번 주엔 공용 패드만 했어도 자기 기기 413");
ok(by("민준").length === 1 && by("민준")[0].score === 120 && by("서연").length === 0, "공부만 한 공용 패드(두 아이)의 900 은 안 셈 · 자기 기기 기록이 없으면 안 나옴");
ok(by("영어선생님").length === 0, "선생님 빼기");
ok(by("하준").length === 2, "태그가 다른 같은 이름은 두 줄");
ok(!L.some(x => /👤/.test(x.nick)), "👤 없이 이름만");
// 달리기 랭킹도 묶임
const g = ctx.__T.doGet({ parameter: { key: "HYENG", diff: "normal", range: "all", dev: "B" } });
const N = JSON.parse(g.s).list; console.log(JSON.stringify(N));
ok(N.filter(x => x.nick === "스트로베리").length === 1 && N.find(x => x.nick === "스트로베리").me, "달리기 랭킹도 한 줄");
ok(!N.some(x => /👤/.test(x.nick)), "달리기 랭킹 👤 없음");
process.exit(bad ? 1 : 0);
