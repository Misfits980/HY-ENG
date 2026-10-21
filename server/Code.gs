/* =====================================================================
   HY ENG 학원 랭킹 — 구글 Apps Script (Code.gs)
   - 게임(index.html)의 Online.URL 이 이 스크립트의 "웹 앱" 주소
   - POST : 판 기록 1줄을 scores 탭에 추가 · type:"buy" 면 상점 구매 1줄을 "구매" 탭에 추가
   - GET  : 난이도별 랭킹 (이번 주 / 전체) — 닉네임마다 최고 점수 1줄 · diff=dex 면 단어 수집 랭킹 (v221) · act=1 이면 그 아이에게 온 원격 조치 (v222)
   - POST type:"ack" : 원격 조치를 처리했다는 표시를 '조치' 탭 '처리' 칸에 (v222)
   - POST type:"name" : 이름을 정하거나 바꾼 기록을 '이름' 탭에 (v225)
   - (v225) scores 탭 맨 끝에 '틀린 단어' 칸 — 그 판(달리기·공부)에서 틀린 단어
   - (v264 · 서버 v2) GET notice=1 : '공지' 탭에서 지금 보이는 공지 (아이 게임이 켜질 때 받아서 창으로 보여 줌)
     POST type:"check"/"notice"/"noticeOff"/"actAdd" : 게임 관리 화면에서 공지 올리기·내리기·원격 조치 보내기
       → 선생님 열쇠(tk)가 스크립트 속성 ADMIN_KEY 와 같아야 한다 (열쇠는 관리 화면 📢 공지 → 설정 방법에서 복사)
       ⚙ 프로젝트 설정 → 스크립트 속성 → 속성 추가: ADMIN_KEY = (열쇠). 코드에는 열쇠를 적지 않는다 (저장소가 공개라서)
   붙여 넣은 뒤 반드시: 배포 → 배포 관리 → ✏️수정 → 버전 "새 버전" → 배포
   (새 배포를 만들면 주소가 바뀌어 게임이 못 찾는다)
===================================================================== */
const KEY        = "HYENG";                                        // 게임의 Online.KEY 와 같아야 함
const SHEET_ID   = "1lsio09VZ7pkFgimSa7Jv4s3TlOtVRuSxTTqOlCD5bzA";
const SHEET_NAME = "scores";
const TZ         = "Asia/Seoul";

/* 시트 열 순서 (A~Z) — 헤더 1행과 같아야 한다. 새 칸은 맨 뒤에만 추가할 것 */
const COLS = [
  ["date","날짜"], ["nick","닉네임"], ["score","점수"], ["diff","난이도"], ["rule","방식"],
  ["stage","단계"], ["acc","정답률"], ["char","캐릭터"], ["dev","기기"],
  ["title","칭호"], ["combo","최대콤보"], ["right","정답수"], ["wrong","오답수"],
  ["boss","문지기처치"], ["clear","완주"], ["end","끝난이유"], ["cause","넘어진이유"],
  ["zone","지대"], ["set","단어장"], ["secs","플레이(초)"], ["dex","도감"], ["gems","보석"],
  ["outfit","옷"], ["fx","달리기효과"], ["hit","정답효과"], ["ver","버전"],
  ["owned","가진 물건"], ["earned","모은 보석"], ["miss","틀린 단어"],
  ["short","짧은 판"]                                               // (v267) 이 줄 전에 초원에서 끝나 기록하지 않은 판 수
];
const NUM = {score:1, stage:1, acc:1, combo:1, right:1, wrong:1, clear:1, secs:1, dex:1, gems:1, earned:1, short:1};
/* 구매 탭 열 순서 */
const BUY_SHEET = "구매";
const BUY_COLS = [["date","날짜"], ["nick","닉네임"], ["kind","종류"], ["name","물건"], ["item","코드"],
                  ["price","가격"], ["gems","남은 보석"], ["dev","기기"], ["ver","버전"]];
const C = {}; COLS.forEach((c,i)=>C[c[0]]=i);                     // 이름 → 열 번호(0부터)

/* (v222) 원격 조치 탭 — 선생님이 한 줄 적으면, 그 아이 게임이 켜질 때 처리하고 "처리" 칸에 기기·시각을 남긴다
   대상 = 닉네임(게임에 적은 이름) 또는 기기(관리자 화면·기록의 '기기' 칸)  ·  모두 = 모든 아이
   조치 = 보석 (값: +50 / -30) · 선물 (값: 물건 코드) · 회수 (값: 물건 코드) · 환불회수 (값: 물건 코드, 낸 보석을 돌려줌) · 캐릭터 (값: hero 등 캐릭터 코드)
   한 기기에서는 한 줄을 한 번만 처리한다 (같은 조치를 또 하려면 새 줄) */
const ACT_SHEET = "조치";
const ACT_COLS = [["date","날짜 (비우면 자동)"], ["who","대상 (닉네임·기기·모두)"], ["kind","조치"], ["value","값"], ["memo","아이에게 보일 말"], ["done","처리 (자동)"]];
const ACT_KINDS = ["보석","선물","회수","환불회수","캐릭터","이름","이름권"];   // (v225) 이름 = 값으로 바로 바꿈 · 이름권 = 무료 변경권 (값 = 장 수)
/* (v225) 이름 탭 — 이름을 처음 정하거나 바꿀 때마다 한 줄 (같은 기기 = 같은 아이) */
const NAME_SHEET = "이름";
const NAME_COLS = [["date","날짜"], ["dev","기기"], ["old","전 이름"], ["nick","새 이름"], ["how","방법"], ["ver","버전"]];
/* (v264) 공지 탭 — 선생님이 직접 적어도 되고, 게임 관리 화면에서 올려도 된다 */
const NOTICE_SHEET = "공지";
const NOTICE_COLS = [["date","날짜 (비우면 자동)"], ["text","내용"], ["show","보이기 (끄기 = 숨김)"], ["until","끝나는 날 (비우면 계속)"], ["by","쓴 기기"], ["id","번호 (자동)"]];
const SERVER_V = 3;   // (v306) 3 = 관리 화면 「📋 우리 반」 (report)

function sheet_(){
  const sh = SpreadsheetApp.openById(SHEET_ID).getSheetByName(SHEET_NAME);
  if (sh.getRange(1, COLS.length).getValue() === "")                // 헤더가 비었으면 채운다 (새 칸이 생겨도)
    sh.getRange(1, 1, 1, COLS.length).setValues([COLS.map(c=>c[1])]);
  return sh;
}
function buySheet_(){
  const ss = SpreadsheetApp.openById(SHEET_ID);
  let sh = ss.getSheetByName(BUY_SHEET);
  if (!sh){ sh = ss.insertSheet(BUY_SHEET); sh.setFrozenRows(1); }
  if (sh.getRange(1, 1).getValue() === "") sh.getRange(1, 1, 1, BUY_COLS.length).setValues([BUY_COLS.map(c=>c[1])]);
  return sh;
}
function json_(o){
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}
/* 글자는 길이 제한 + 수식(=,+,-,@)으로 시작하지 않게 */
function txt_(v, n){
  let s = (v === undefined || v === null) ? "" : String(v).replace(/[\r\n\t]/g," ").trim().slice(0, n||40);
  if (/^[=+\-@]/.test(s)) s = "'" + s;
  return s;
}
function num_(v, max){
  const x = Math.round(Number(v));
  return isFinite(x) ? Math.max(0, Math.min(max||1e9, x)) : 0;
}

/* ---------------------------- 기록 저장 ---------------------------- */
function doPost(e){
  let d;
  try { d = JSON.parse(e.postData.contents); } catch(err){ return json_({ok:false, err:"bad json"}); }
  if (!d || d.key !== KEY) return json_({ok:false, err:"key"});
  if (d.type === "ack") return ackAct_(d);                          // (v222) 원격 조치 처리 확인
  if (d.type === "name") return nameLog_(d);                         // (v225) 이름 바꾼 기록
  if (["check","notice","noticeOff","actAdd","report"].indexOf(d.type) >= 0) return teacher_(d);   // (v264) 선생님 관리 화면
  if (d.type && d.type !== "buy") return json_({ok:false, err:"type"});   // 모르는 종류는 scores 에 쓰지 않는다
  const isBuy = d.type === "buy";
  /* (v367) 기기에 쌓였다가 늦게 온 기록은 실제로 판이 끝난 때(d.at)로 적는다 — 7일 안 · 미래는 안 됨. 그 밖에는 받은 때 */
  const now = new Date(), at = Number(d.at), when = (at > now.getTime() - 7*864e5 && at <= now.getTime() + 60000) ? new Date(at) : now;

  const row = isBuy ? BUY_COLS.map(([k])=>{
    if (k === "date") return when;
    if (k === "nick") return txt_(d.nick, 20) || "PLAYER";
    if (k === "price" || k === "gems") return num_(d[k], 1000000);
    return txt_(d[k], 40);
  }) : COLS.map(([k])=>{
    if (k === "date") return when;
    if (k === "nick") return txt_(d.nick, 20) || "PLAYER";
    if (NUM[k])       return num_(d[k], k === "score" ? 10000000 : 1000000);
    if (k === "boss") return txt_(d.boss, 40).replace(/,/g, " · ");   // "50,80" 이 숫자 5080 으로 바뀌지 않게
    return txt_(d[k], k === "owned" ? 400 : (k === "miss" ? 400 : (k === "cause" ? 60 : 40)));
  });

  const lock = LockService.getScriptLock();
  try {
    lock.waitLock(10000);                                           // 여러 명이 동시에 보내도 줄이 안 겹치게
    const sh = isBuy ? buySheet_() : sheet_();
    sh.appendRow(row);
    sh.getRange(sh.getLastRow(), 1).setNumberFormat("yyyy-mm-dd hh:mm");   // 날짜를 다른 줄과 같은 모양으로
  } catch(err){
    return json_({ok:false, err:"busy"});
  } finally {
    try { lock.releaseLock(); } catch(_){}
  }
  return json_({ok:true});
}

/* ------------------------------ 랭킹 ------------------------------ */
function weekStart_(){                                              // 이번 주 월요일 0시 (한국 시간)
  const H9 = 9*3600*1000, now = Date.now(), k = new Date(now + H9);
  const back = (k.getUTCDay() + 6) % 7;
  return Date.UTC(k.getUTCFullYear(), k.getUTCMonth(), k.getUTCDate() - back) - H9;
}
function time_(v){
  if (v instanceof Date) return v.getTime();
  const t = new Date(v).getTime(); return isFinite(t) ? t : 0;
}

function doGet(e){
  const p = (e && e.parameter) || {};
  if (p.key !== KEY) return json_({ok:false, err:"key"});
  if (p.act) return json_({ok:true, list:actsFor_(String(p.nick||""), String(p.dev||""))});   // (v222) 원격 조치
  if (p.notice) return json_({ok:true, v:SERVER_V, notices:notices_()});                          // (v264) 공지
  const diff  = String(p.diff || "easy");
  const range = String(p.range || "week");
  const n     = Math.max(1, Math.min(100, Number(p.n) || 20));
  const dev   = String(p.dev || "");
  const since = range === "all" ? 0 : weekStart_();

  const sh = sheet_(), last = sh.getLastRow();
  if (last < 2) return json_({ok:true, list:[]});
  if (diff === "dex") return json_({ok:true, list:dexRank_(sh, last, since, n, dev)});   // (v221) 단어 수집 랭킹
  const rows = sh.getRange(2, 1, last - 1, C.title + 1).getValues();   // 날짜 ~ 칭호까지만 읽는다

  const best = {};                                                  // 닉네임 → 최고 기록
  rows.forEach(r=>{
    if (String(r[C.diff]) !== diff) return;
    if (r[C.rule] && String(r[C.rule]) !== "normal") return;
    const t = time_(r[C.date]); if (t < since) return;
    const nick = String(r[C.nick] || "PLAYER"), score = Number(r[C.score]) || 0;
    let b = best[nick];
    if (!b){ b = best[nick] = {nick, score:0, stage:0, title:"", tt:0, me:false}; }
    if (score > b.score){ b.score = score; b.stage = Number(r[C.stage]) || 0; }
    if (r[C.title] && t >= b.tt){ b.title = String(r[C.title]); b.tt = t; }  // 가장 최근 칭호
    if (dev && String(r[C.dev]) === dev) b.me = true;
  });

  const list = Object.keys(best).map(k=>best[k])
    .sort((a,b)=>b.score - a.score).slice(0, n)
    .map(b=>({nick:b.nick, score:b.score, stage:b.stage, title:b.title, me:b.me}));
  return json_({ok:true, list});
}

/* (v221) 단어 수집 랭킹 — 닉네임마다 '도감' 칸의 가장 큰 값 (모든 방식·난이도·공부 기록 포함)
   이번 주 = 이번 주에 기록이 있는 사람만 (값은 그때까지 모은 전체 단어 수) */
function dexRank_(sh, last, since, n, dev){
  const rows = sh.getRange(2, 1, last - 1, C.dex + 1).getValues();
  const best = {};
  rows.forEach(r=>{
    const t = time_(r[C.date]); if (t < since) return;
    const nick = String(r[C.nick] || "PLAYER"), dex = Number(r[C.dex]) || 0;
    let b = best[nick]; if (!b){ b = best[nick] = {nick, score:0, title:"", tt:0, me:false}; }
    if (dex > b.score) b.score = dex;
    if (r[C.title] && t >= b.tt){ b.title = String(r[C.title]); b.tt = t; }
    if (dev && String(r[C.dev]) === dev) b.me = true;
  });
  return Object.keys(best).map(k=>best[k]).filter(b=>b.score>0)
    .sort((a,b)=>b.score - a.score).slice(0, n)
    .map(b=>({nick:b.nick, score:b.score, stage:0, title:b.title, me:b.me}));
}

/* ── (v222) 원격 조치 ── */
function actSheet_(){
  const ss = SpreadsheetApp.openById(SHEET_ID);
  let sh = ss.getSheetByName(ACT_SHEET);
  if (!sh){ sh = ss.insertSheet(ACT_SHEET); sh.setFrozenRows(1); }
  if (sh.getRange(1, 1).getValue() === "") sh.getRange(1, 1, 1, ACT_COLS.length).setValues([ACT_COLS.map(c=>c[1])]);
  return sh;
}
function actId_(r){ return [time_(r[0]), String(r[1]).trim(), String(r[2]).trim(), String(r[3]).trim()].join("|"); }
function actsFor_(nick, dev){
  const sh = actSheet_(), last = sh.getLastRow(); if (last < 2) return [];
  const rows = sh.getRange(2, 1, last - 1, ACT_COLS.length).getValues(), out = [];
  const N = nick.trim().toUpperCase();
  rows.forEach((r, i)=>{
    const who = String(r[1] || "").trim(), kind = String(r[2] || "").trim();
    if (!who || ACT_KINDS.indexOf(kind) < 0) return;
    const W = who.toUpperCase();
    if (!(W === "모두" || (N && W === N) || (dev && who === dev))) return;
    if (dev && String(r[5] || "").indexOf(dev) >= 0) return;        // 이 기기는 이미 처리함
    if (!r[0]){ r[0] = new Date(); sh.getRange(i + 2, 1).setValue(r[0]).setNumberFormat("yyyy-mm-dd hh:mm"); }   // 날짜가 비면 지금으로 (같은 줄을 구별하는 열쇠)
    out.push({id:actId_(r), kind, value:String(r[3] || "").trim(), memo:String(r[4] || "").trim()});
  });
  return out;
}
function ackAct_(d){
  const sh = actSheet_(), last = sh.getLastRow(); if (last < 2) return json_({ok:true});
  const rows = sh.getRange(2, 1, last - 1, ACT_COLS.length).getValues();
  const lock = LockService.getScriptLock();
  try {
    lock.waitLock(10000);
    rows.forEach((r, i)=>{ if (actId_(r) !== String(d.id)) return;
      const cell = sh.getRange(i + 2, ACT_COLS.length), prev = String(cell.getValue() || "");
      const tag = txt_(d.nick, 20) + "(" + txt_(d.dev, 20) + ") " + Utilities.formatDate(new Date(), TZ, "MM-dd HH:mm") + (d.res ? " " + txt_(d.res, 40) : "");
      if (prev.indexOf(String(d.dev)) < 0) cell.setValue(prev ? prev + "\n" + tag : tag); });
  } catch(err){ return json_({ok:false, err:"busy"}); }
  finally { try { lock.releaseLock(); } catch(_){} }
  return json_({ok:true});
}

/* ── (v225) 이름 기록 ── */
function nameLog_(d){
  const ss = SpreadsheetApp.openById(SHEET_ID);
  let sh = ss.getSheetByName(NAME_SHEET);
  const lock = LockService.getScriptLock();
  try {
    lock.waitLock(10000);
    if (!sh){ sh = ss.insertSheet(NAME_SHEET); sh.setFrozenRows(1); }
    if (sh.getRange(1, 1).getValue() === "") sh.getRange(1, 1, 1, NAME_COLS.length).setValues([NAME_COLS.map(c=>c[1])]);
    sh.appendRow(NAME_COLS.map(([k])=> k === "date" ? new Date() : txt_(d[k], 30)));
    sh.getRange(sh.getLastRow(), 1).setNumberFormat("yyyy-mm-dd hh:mm");
  } catch(err){ return json_({ok:false, err:"busy"}); }
  finally { try { lock.releaseLock(); } catch(_){} }
  return json_({ok:true});
}

/* ── (v264) 공지 ── */
function noticeSheet_(){
  const ss = SpreadsheetApp.openById(SHEET_ID);
  let sh = ss.getSheetByName(NOTICE_SHEET);
  if (!sh){ sh = ss.insertSheet(NOTICE_SHEET); sh.setFrozenRows(1); sh.setColumnWidth(2, 420); }
  if (sh.getRange(1, 1).getValue() === "") sh.getRange(1, 1, 1, NOTICE_COLS.length).setValues([NOTICE_COLS.map(c=>c[1])]).setFontWeight("bold");
  return sh;
}
function ymd_(v){ const t = time_(v); return t ? Utilities.formatDate(new Date(t), TZ, "yyyy-MM-dd") : String(v||"").trim(); }
function noticeId_(r){ return String(r[5] || "").trim() || ("n" + time_(r[0])); }
/* 지금 보이는 공지 — 보이기가 '끄기'가 아니고, 끝나는 날이 오늘이거나 그 뒤 (최신 10개) */
function notices_(){
  const sh = noticeSheet_(), last = sh.getLastRow(); if (last < 2) return [];
  const rows = sh.getRange(2, 1, last - 1, NOTICE_COLS.length).getValues(), today = Utilities.formatDate(new Date(), TZ, "yyyy-MM-dd"), out = [];
  rows.forEach((r, i)=>{
    const text = String(r[1] || "").trim(); if (!text) return;
    if (String(r[2] || "").trim() === "끄기") return;
    const until = r[3] ? ymd_(r[3]) : ""; if (until && until < today) return;
    if (!r[0]){ r[0] = new Date(); sh.getRange(i + 2, 1).setValue(r[0]).setNumberFormat("yyyy-mm-dd hh:mm"); }   // 직접 적은 줄 — 날짜가 번호가 된다
    out.push({id:noticeId_(r), text:text.slice(0, 300), date:Utilities.formatDate(new Date(time_(r[0])), TZ, "M월 d일"), until, t:time_(r[0])});
  });
  return out.sort((a,b)=>b.t - a.t).slice(0, 10).map(n=>({id:n.id, text:n.text, date:n.date, until:n.until}));
}
/* 여러 줄 글 (공지) — 줄바꿈은 남기고 수식으로 시작하지 않게 */
function txtMulti_(v, n){
  let s = (v === undefined || v === null) ? "" : String(v).replace(/\r/g,"").replace(/\t/g," ").trim().slice(0, n||300);
  if (/^[=+\-@]/.test(s)) s = "'" + s;
  return s;
}
/* 선생님 관리 화면 — 스크립트 속성 ADMIN_KEY 와 같은 열쇠만 */
function teacher_(d){
  const want = PropertiesService.getScriptProperties().getProperty("ADMIN_KEY");
  if (!want) return json_({ok:false, err:"nokey"});
  if (String(d.tk || "") !== want) return json_({ok:false, err:"badkey"});
  if (d.type === "check") return json_({ok:true, v:SERVER_V});
  if (d.type === "report") return json_({ok:true, v:SERVER_V, at:Date.now(), rep:report_()});   // (v306) 우리 반 — 시트 요약 탭을 보이는 그대로
  const lock = LockService.getScriptLock();
  try {
    lock.waitLock(10000);
    if (d.type === "notice"){
      const text = txtMulti_(d.text, 300); if (!text) return json_({ok:false, err:"empty"});
      const days = Math.max(0, Math.min(60, Math.round(Number(d.days) || 0)));
      const until = days ? Utilities.formatDate(new Date(Date.now() + (days - 1) * 864e5), TZ, "yyyy-MM-dd") : "";
      const sh = noticeSheet_(), now = new Date();
      sh.appendRow([now, text, "켜기", until ? "'" + until : "", txt_(d.dev, 20), "n" + now.getTime()]);
      sh.getRange(sh.getLastRow(), 1).setNumberFormat("yyyy-mm-dd hh:mm");
      return json_({ok:true});
    }
    if (d.type === "noticeOff"){
      const sh = noticeSheet_(), last = sh.getLastRow(); if (last < 2) return json_({ok:false, err:"none"});
      const rows = sh.getRange(2, 1, last - 1, NOTICE_COLS.length).getValues(); let hit = 0;
      rows.forEach((r, i)=>{ if (noticeId_(r) === String(d.id)){ sh.getRange(i + 2, 3).setValue("끄기"); hit++; } });
      return json_({ok:hit > 0, err:hit ? "" : "none"});
    }
    if (d.type === "actAdd"){
      const kind = String(d.kind || "").trim(); if (ACT_KINDS.indexOf(kind) < 0) return json_({ok:false, err:"kind"});
      const who = txt_(d.who, 40); if (!who) return json_({ok:false, err:"who"});
      const sh = actSheet_(), now = new Date();
      sh.appendRow([now, who, kind, txt_(d.value, 40), txt_(d.memo, 60), ""]);
      sh.getRange(sh.getLastRow(), 1).setNumberFormat("yyyy-mm-dd hh:mm");
      return json_({ok:true});
    }
  } catch(err){ return json_({ok:false, err:"busy"}); }
  finally { try { lock.releaseLock(); } catch(_){} }
  return json_({ok:false, err:"type"});
}

/* ── (v267) 오래된 기록 보관 — scores 가 너무 길어져 시트가 느려지면 ──
   KEEP_DAYS 보다 오래된 줄을 '보관' 탭으로 옮긴다 (지우지 않음). 시트 요약 탭들은 scores 만 보므로 옮긴 줄은 요약에서 빠진다.
   쓰는 법: 편집기 위 함수 고르기에서 archiveOld → ▶실행 (한 번)  ·  자동으로: ⏰ 트리거 → 트리거 추가 → archiveOld · 시간 기반 · 주 단위 */
const ARCHIVE_SHEET = "보관", KEEP_DAYS = 90;
function archiveOld(){
  const ss = SpreadsheetApp.openById(SHEET_ID), sh = sheet_();
  const lock = LockService.getScriptLock(); lock.waitLock(30000);
  try {
    const last = sh.getLastRow(); if (last < 2) return;
    const vals = sh.getRange(2, 1, last - 1, COLS.length).getValues(), cut = Date.now() - KEEP_DAYS * 864e5;
    let n = 0; while (n < vals.length && time_(vals[n][0]) && time_(vals[n][0]) < cut) n++;   // 줄은 시간 순서로 쌓여 있다 → 위에서부터
    if (!n) return;
    let ar = ss.getSheetByName(ARCHIVE_SHEET);
    if (!ar){ ar = ss.insertSheet(ARCHIVE_SHEET); ar.getRange(1, 1, 1, COLS.length).setValues([COLS.map(c=>c[1])]); ar.setFrozenRows(1); }
    const at = ar.getLastRow() + 1;
    ar.getRange(at, 1, n, COLS.length).setValues(vals.slice(0, n));
    ar.getRange(at, 1, n, 1).setNumberFormat("yyyy-mm-dd hh:mm");
    sh.deleteRows(2, n);
    Logger.log(n + "줄을 보관 탭으로 옮겼어요");
  } finally { try { lock.releaseLock(); } catch(_){} }
}

/* 편집기에서 ▶실행 으로 확인용 — 시트에 쓰지 않고 랭킹만 로그로 */
function test(){
  const out = doGet({parameter:{key:KEY, diff:"hard", range:"all", n:"5"}}).getContent();
  Logger.log(out);
}

/* ── (v306) 관리 화면 「📋 우리 반」 — 시트 요약 탭(수식이 계산한 것)을 보이는 글자 그대로 보낸다 (선생님 열쇠가 있어야) ── */
function report_(){
  const ss = SpreadsheetApp.openById(SHEET_ID);
  const g = (name, a1)=>{ try { const sh = ss.getSheetByName(name); if (!sh) return [];
    return sh.getRange(a1).getDisplayValues().filter(r=>r.some(c=>String(c).trim() !== "")); } catch(err){ return []; } };   // (v308) 탭 칸이 바뀌어도 나머지는 보냄
  return {
    head:  (g("🏠 한눈에", "A2:A2")[0] || [""])[0],
    check: g("확인 필요", "A4:D40"),
    week:  g("주간 체크", "A5:R80"),
    weekOf: (g("주간 체크", "B2:B2")[0] || [""])[0],
    today: g("오늘의 30 요약", "A5:H80"),
    weekly: g("주간 리포트", "A5:M80"),
    miss:  g("틀린 단어", "A5:C40"),
    lesson: g("수업 기록", "A3:I40"),
    prog:  g("진도표", "A3:H80"),
    nicks: g("기기별 이름", "B5:B300").map(r=>String(r[0]).trim()).filter(n=>n && !/^PLAYER$/i.test(n))   // (v308) 보내기 받는 아이 = 게임 이름(닉네임)
  };
}
