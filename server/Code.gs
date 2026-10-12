/* =====================================================================
   HY ENG 학원 랭킹 — 구글 Apps Script (Code.gs)
   - 게임(index.html)의 Online.URL 이 이 스크립트의 "웹 앱" 주소
   - POST : 판 기록 1줄을 scores 탭에 추가 · type:"buy" 면 상점 구매 1줄을 "구매" 탭에 추가
   - GET  : 난이도별 랭킹 (이번 주 / 전체) — 닉네임마다 최고 점수 1줄
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
  ["owned","가진 물건"], ["earned","모은 보석"]
];
const NUM = {score:1, stage:1, acc:1, combo:1, right:1, wrong:1, clear:1, secs:1, dex:1, gems:1, earned:1};
/* 구매 탭 열 순서 */
const BUY_SHEET = "구매";
const BUY_COLS = [["date","날짜"], ["nick","닉네임"], ["kind","종류"], ["name","물건"], ["item","코드"],
                  ["price","가격"], ["gems","남은 보석"], ["dev","기기"], ["ver","버전"]];
const C = {}; COLS.forEach((c,i)=>C[c[0]]=i);                     // 이름 → 열 번호(0부터)

function sheet_(){
  const sh = SpreadsheetApp.openById(SHEET_ID).getSheetByName(SHEET_NAME);
  if (sh.getRange(1, COLS.length).getValue() === "")                // 헤더가 비었으면 채운다
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
  const isBuy = d.type === "buy";

  const row = isBuy ? BUY_COLS.map(([k])=>{
    if (k === "date") return new Date();
    if (k === "nick") return txt_(d.nick, 20) || "PLAYER";
    if (k === "price" || k === "gems") return num_(d[k], 1000000);
    return txt_(d[k], 40);
  }) : COLS.map(([k])=>{
    if (k === "date") return new Date();
    if (k === "nick") return txt_(d.nick, 20) || "PLAYER";
    if (NUM[k])       return num_(d[k], k === "score" ? 10000000 : 1000000);
    if (k === "boss") return txt_(d.boss, 40).replace(/,/g, " · ");   // "50,80" 이 숫자 5080 으로 바뀌지 않게
    return txt_(d[k], k === "owned" ? 400 : (k === "cause" ? 60 : 40));
  });

  const lock = LockService.getScriptLock();
  try {
    lock.waitLock(10000);                                           // 여러 명이 동시에 보내도 줄이 안 겹치게
    (isBuy ? buySheet_() : sheet_()).appendRow(row);
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
  const diff  = String(p.diff || "easy");
  const range = String(p.range || "week");
  const n     = Math.max(1, Math.min(100, Number(p.n) || 20));
  const dev   = String(p.dev || "");
  const since = range === "all" ? 0 : weekStart_();

  const sh = sheet_(), last = sh.getLastRow();
  if (last < 2) return json_({ok:true, list:[]});
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

/* 편집기에서 ▶실행 으로 확인용 — 시트에 쓰지 않고 랭킹만 로그로 */
function test(){
  const out = doGet({parameter:{key:KEY, diff:"hard", range:"all", n:"5"}}).getContent();
  Logger.log(out);
}
