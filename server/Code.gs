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
   - (v404 · 서버 v4) 🏷 태그 — 아이마다 4자리 번호(이름을 바꿔도 그대로). '태그' 탭 = 태그 · 기기 · 처음 이름 · 지금 이름 …
     #0000 = 선생님(나, 관리 화면에서 「이 기기 = #0000」) · #0001~#0005 = 공용 패드 전용 · 아이들은 #0006 부터 차례로 (이름을 처음 정할 때)
     POST type:"tag" (기기·이름 → 태그) · 선생님 type:"tagMe"/"tagSet"(태그를 새 기기로 옮기기)/"tags"(목록)
     scores·구매·이름 탭 맨 끝에 '태그' 칸 · 랭킹은 태그로 묶음(같은 이름이 둘이어도 안 섞임, 이름을 바꿔도 한 줄)
   - (v563 · 서버 v8) 🏝 My Town — scores 탭 맨 끝에 코인·미끼·은행 코인·은행 보석·강화 칸 · 플레이(초)는 한 줄 3600(1시간)까지
     '마을 현황' 탭 = 아이 한 줄(태그, 없으면 👤 뗀 이름) — 판 기록이 올 때마다 보석·모은 보석·마을 돈을 고쳐 씀 · 관리 화면 「📋 우리 반」에도 (report.town)
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
  ["short","짧은 판"],                                              // (v267) 이 줄 전에 초원에서 끝나 기록하지 않은 판 수
  ["tag","태그"],                                                   // (v404) 아이 태그 4자리 (이름을 바꿔도 그대로)
  ["own","주인 패드"],                                              // (v417) 🧸 공용 패드에서 주인(유치부 아이)이 한 판 = 1 → 그 패드 단어 수를 주인 것으로 셈
  ["coin","코인"], ["bait","미끼"], ["bank","은행 코인"], ["gbank","은행 보석"], ["tup","강화"],   // (v563 · 서버 v8) 🏝 My Town (옛 게임은 빈 칸)
  ["cn","단어 카드"], ["cf","끝까지 본 카드"], ["cs","카드 평균(초)"],   // (v600 · 서버 v9) 오늘의 30 — 단어·뜻·문장 카드를 몇 장 봤고, 소리(단어 두 번 + 문장)가 끝날 때까지 본 카드가 몇 장인지
  ["rep","다시 푼 판"],                                             // (v600 · 서버 v9) 같은 날 이미 끝까지 푼 같은 Stage 를 또 풀면 1 (서버가 셈)
  ["rid","기록 번호"],                                               // (v611 · 서버 v13) 판마다 게임이 붙이는 번호 — 같은 번호가 또 오면(인터넷이 끊겨 다시 보낸 것) 안 적음
];
COLS.push(["rvo","며칠 뒤 맞힘"], ["rvn","며칠 뒤 푼 수"], ["rvw","며칠 뒤 틀린 단어"], ["sp","말한 단어"]);   // (v650 · 서버 v19) 오늘의 30 — 복습 날이 된 단어를 그날 처음 푼 결과 · 🎤 따라 말한 단어 수
const NUM = {rvo:1, rvn:1, sp:1, score:1, stage:1, acc:1, combo:1, right:1, wrong:1, clear:1, secs:1, dex:1, gems:1, earned:1, short:1, coin:1, bait:1, bank:1, gbank:1, cn:1, cf:1, rep:1};
const NEW9 = {cn:1, cf:1, cs:1, rep:1, rvo:1, rvn:1, sp:1};                                // (v600) 옛 게임 줄은 빈 칸
const NUM_MAX = {score:10000000, secs:3600};                         // (v563) 플레이(초) 한 줄 1시간까지 — 탭을 뒤로 보내 둔 시간이 846분으로 쌓이던 것
/* (v563) 🏝 마을 현황 탭 — 아이 한 줄 (태그 → 없으면 👤 뗀 이름) · 판 기록이 올 때마다 고쳐 씀 */
const TOWN_SHEET = "마을 현황";
const TOWN_COLS = [["nick","아이"], ["tag","태그"], ["at","마지막"], ["gems","보석"], ["earned","모은 보석"], ["coin","코인"], ["bait","미끼"], ["bank","은행 코인"], ["gbank","은행 보석"], ["tup","강화"], ["ver","버전"]];
const TOWN_KEEP = {coin:1, bait:1, bank:1, gbank:1, tup:1};          // 옛 게임 줄(이 칸이 없음)은 전에 적힌 값을 그대로 둠
/* 구매 탭 열 순서 */
const BUY_SHEET = "구매";
const BUY_COLS = [["date","날짜"], ["nick","닉네임"], ["kind","종류"], ["name","물건"], ["item","코드"],
                  ["price","가격"], ["gems","남은 보석"], ["dev","기기"], ["ver","버전"], ["tag","태그"]];
const C = {}; COLS.forEach((c,i)=>C[c[0]]=i);                     // 이름 → 열 번호(0부터)

/* (v222) 원격 조치 탭 — 선생님이 한 줄 적으면, 그 아이 게임이 켜질 때 처리하고 "처리" 칸에 기기·시각을 남긴다
   대상 = 닉네임(게임에 적은 이름) 또는 기기(관리자 화면·기록의 '기기' 칸)  ·  모두 = 모든 아이
   조치 = 보석 (값: +50 / -30) · 선물 (값: 물건 코드) · 회수 (값: 물건 코드) · 환불회수 (값: 물건 코드, 낸 보석을 돌려줌) · 캐릭터 (값: hero 등 캐릭터 코드)
   한 기기에서는 한 줄을 한 번만 처리한다 (같은 조치를 또 하려면 새 줄) */
const ACT_SHEET = "조치";
const ACT_COLS = [["date","날짜 (비우면 자동)"], ["who","대상 (닉네임·#태그·기기·모두)"], ["kind","조치"], ["value","값"], ["memo","아이에게 보일 말"], ["done","처리 (자동)"]];
const ACT_KINDS = ["보석","선물","회수","환불회수","캐릭터","이름","이름권"];   // (v225) 이름 = 값으로 바로 바꿈 · 이름권 = 무료 변경권 (값 = 장 수)
/* (v225) 이름 탭 — 이름을 처음 정하거나 바꿀 때마다 한 줄 (같은 기기 = 같은 아이) */
const NAME_SHEET = "이름";
const NAME_COLS = [["date","날짜"], ["dev","기기"], ["old","전 이름"], ["nick","새 이름"], ["how","방법"], ["ver","버전"], ["tag","태그"]];
/* (v404) 🏷 태그 탭 — 한 줄 = 태그 하나. 태그 칸은 글자(@)라 0006 의 0 이 안 없어짐. 0000~0005 는 처음에 미리 만들어 둠 */
const TAG_SHEET = "태그";
const TAG_COLS = [["tag","태그"], ["dev","기기"], ["first","처음 이름"], ["nick","지금 이름"], ["since","받은 날"], ["at","마지막으로 본 날"], ["memo","메모"], ["rlv","랭킹 단계"]];   // (v631) 랭킹 단계 = 선생님이 정함 (관리 화면 · 이 칸)
const TAG_ME = "0000", TAG_PADS = ["0001","0002","0003","0004","0005"], TAG_FIRST_KID = 6;
/* (v264) 공지 탭 — 선생님이 직접 적어도 되고, 게임 관리 화면에서 올려도 된다 */
const NOTICE_SHEET = "공지";
const NOTICE_COLS = [["date","날짜 (비우면 자동)"], ["text","내용"], ["show","보이기 (끄기 = 숨김)"], ["until","끝나는 날 (비우면 계속)"], ["by","쓴 기기"], ["id","번호 (자동)"]];
const SERVER_V = 20;  // (v653) 20 = 📒 문법별 정답률 (report.learn.gram · 아이별 약한 문법) · (v650) 19 = 🧠 며칠 뒤에도 기억하나 (scores 끝에 며칠 뒤 맞힘·푼 수·틀린 단어·말한 단어 칸 · 선생님 report.learn) · (v638) 18 = 🏅 나의 리그 「기준」(같은 단계 가운데값 60%) — 낮은 점수로 칭호 못 땀 · (v636) 17 = ⚔️ 스테이지 도전장(「도전장」 탭) · (v635) 16 = 🏅 나의 리그(지난주 나 넘기: me.lg) · (v631) 15 = 🏆 아이마다 랭킹 단계 — 「태그」 탭 「랭킹 단계」 칸(자동·유치원·G1-2·G3-4·G5-6·중등·빼기) · 관리 화면에서도 · 정한 단계보다 쉬운 책은 랭킹에 안 셈(높은 건 셈) · 빼기 = 랭킹에 안 나옴 · (v618) 14 = 🏛 명예의 전당(「명예의 전당」 탭: 날마다 1위 · 주마다 1~3위) · 🔥 연속 1위 · 📅 개근 · 메달 · 📚 오늘의 30 「전체」 · 내 기록 · (v613) 13 = + 같은 Stage 는 한 주에 가장 잘한 판 하나만 · (v611) 13 = 같은 판 두 번 안 적기(기록 번호 rid) · 글자로 들어간 날짜도 읽기 · 「연습」 판은 공부 점수에 안 셈
//  // (v603) 12 = 📚 공부 점수 = 스테이지 점수 + 푼 문제 · (v602) 11 = 랭킹은 「내 단계」보다 쉬운 판 빼기 · board 에 나(me: 순위·어제보다·바로 위 친구) · (v601) 10 = 🔥 실시간 랭킹(board=1: 이번 주 공부 점수 · 이번 주 모은 단어 · 달리기 · 어제보다 ▲▼) · 📚 공부 랭킹(diff=study) · 단어 수집 「이번 주」 = 이번 주에 모은 수 · (v600) 9 = 오늘의 30 카드 칸(단어 카드·끝까지 본 카드·카드 평균 초) · 다시 푼 판 · 「마이타운 시간」 탭 (type "mt")
const MT_SHEET = "마이타운 시간";
const MT_COLS = [["day","날짜"], ["kid","아이"], ["tag","태그"], ["dev","기기"], ["min","마이타운(분)"], ["segs","들어온 번"], ["at","마지막"], ["ver","버전"], ["nick","게임 이름"]];
/* 이전 서버 버전: (v563) 8 = 🏝 My Town 칸(코인·미끼·은행·강화) · 「마을 현황」 탭 · 플레이(초) 1시간까지 · (v306) 3 = 관리 화면 「📋 우리 반」 (report) · (v404) 4 = 🏷 태그 · (v416) 5 = 랭킹 한 사람 한 줄(👤 묶기·공용 패드 단어 수 안 셈·선생님 빼기) · (v417) 6 = 「주인 패드」 칸 · (v419) 7 = 🔐 선생님 기기 등록(fbTeacher) */

function sheet_(){
  const sh = SpreadsheetApp.openById(SHEET_ID).getSheetByName(SHEET_NAME);
  if (sh.getMaxColumns() < COLS.length) sh.insertColumnsAfter(sh.getMaxColumns(), COLS.length - sh.getMaxColumns());   // (v600) 새 칸이 시트 폭보다 많으면 늘림
  if (sh.getRange(1, COLS.length).getValue() === "")                // 헤더가 비었으면 채운다 (새 칸이 생겨도)
    sh.getRange(1, 1, 1, COLS.length).setValues([COLS.map(c=>c[1])]);
  return sh;
}
function buySheet_(){
  const ss = SpreadsheetApp.openById(SHEET_ID);
  let sh = ss.getSheetByName(BUY_SHEET);
  if (!sh){ sh = ss.insertSheet(BUY_SHEET); sh.setFrozenRows(1); }
  if (sh.getRange(1, BUY_COLS.length).getValue() === "") sh.getRange(1, 1, 1, BUY_COLS.length).setValues([BUY_COLS.map(c=>c[1])]);   // (v404) 새 칸(태그)이 생겨도 머리 줄 채움
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
  if (d.type === "tag") return tagFor_(d);                           // (v404) 🏷 이 기기의 태그 (없으면 새로)
  if (d.type === "mt") return mtLog_(d);                             // (v600) 🏝 마이타운 시간 (아이·날마다 한 줄)
  if (["duelFriends","duelSend","duelBox","duelDone"].indexOf(d.type) >= 0) return duel_(d);   // (v636) ⚔️ 스테이지 도전장
  if (["check","notice","noticeOff","actAdd","report","tagMe","tagSet","tags","tagLv"].indexOf(d.type) >= 0) return teacher_(d);   // (v264) 선생님 관리 화면
  if (d.type && d.type !== "buy") return json_({ok:false, err:"type"});   // 모르는 종류는 scores 에 쓰지 않는다
  const isBuy = d.type === "buy";
  /* (v367) 기기에 쌓였다가 늦게 온 기록은 실제로 판이 끝난 때(d.at)로 적는다 — 7일 안 · 미래는 안 됨. 그 밖에는 받은 때 */
  const now = new Date(), at = Number(d.at), when = (at > now.getTime() - 7*864e5 && at <= now.getTime() + 60000) ? new Date(at) : now;

  const row = isBuy ? BUY_COLS.map(([k])=>{
    if (k === "date") return when;
    if (k === "nick") return txt_(d.nick, 20) || "PLAYER";
    if (k === "tag") return tag_(d.tag) ? "#" + tag_(d.tag) : "";   // "#0006" — 글자로 남아 0 이 안 없어짐
    if (k === "price" || k === "gems") return num_(d[k], 1000000);
    return txt_(d[k], 40);
  }) : COLS.map(([k])=>{
    if (k === "date") return when;
    if (k === "nick") return txt_(d.nick, 20) || "PLAYER";
    if (k === "rep")  return "";                                     // (v600) 아래에서 서버가 셈
    if (k === "rid")  return txt_(d.rid, 24);
    if (k === "cs")   return has_(d, "cs") ? Math.max(0, Math.min(600, Math.round(Number(d.cs) * 10) / 10 || 0)) : "";
    if (NUM[k])       return ((k in TOWN_KEEP || k in NEW9) && !has_(d, k)) ? "" : num_(d[k], NUM_MAX[k] || 1000000);   // (v563) 옛 게임 = 마을 칸 비움
    if (k === "boss") return txt_(d.boss, 40).replace(/,/g, " · ");   // "50,80" 이 숫자 5080 으로 바뀌지 않게
    if (k === "tag")  return tag_(d.tag) ? "#" + tag_(d.tag) : "";
    return txt_(d[k], k === "owned" ? 400 : (k === "miss" || k === "rvw" ? 400 : (k === "cause" ? 60 : 40)));
  });

  const lock = LockService.getScriptLock();
  try {
    lock.waitLock(10000);                                           // 여러 명이 동시에 보내도 줄이 안 겹치게
    const sh = isBuy ? buySheet_() : sheet_();
    if (!isBuy && d.rid) {                                         // (v611) 같은 판이 두 번 — 게임이 보냈는데 답을 받기 전에 앱이 뒤로 가면 실패로 알고 다시 보냄 → 최근 600줄에 같은 번호가 있으면 안 적음
      const rid = txt_(d.rid, 24), last = sh.getLastRow();
      if (rid && last >= 2){ const n0 = Math.min(600, last - 1), ids = sh.getRange(last - n0 + 1, C.rid + 1, n0, 1).getValues();
        for (let i = 0; i < ids.length; i++) if (String(ids[i][0]) === rid) return json_({ok:true, dup:true}); }
    }
    if (!isBuy) { try { row[C.rep] = repOf_(sh, row, when); } catch(e3){} }   // (v600) 다시 푼 판
    sh.appendRow(row);
    sh.getRange(sh.getLastRow(), 1).setNumberFormat("yyyy-mm-dd hh:mm");   // 날짜를 다른 줄과 같은 모양으로
    if (!isBuy) { try { townUpsert_(d, when); } catch(e2){} }      // (v563) 🏝 마을 현황 — 안 되어도 판 기록은 남김
  } catch(err){
    return json_({ok:false, err:"busy"});
  } finally {
    try { lock.releaseLock(); } catch(_){}
  }
  return json_({ok:true});
}

/* ── (v600) 다시 푼 판 — 오늘의 30(방식 study…) 줄이면 최근 400줄에서 같은 날 · 같은 아이(태그 → 기기+이름) · 같은 Stage 를 끝까지 푼 줄이 있는지 ── */
function repOf_(sh, row, when){
  if (!/^study/.test(String(row[C.rule] || ""))) return "";
  const set = String(row[C.set] || ""); if (!set || set === "복습") return "";
  const last = sh.getLastRow(); if (last < 2) return 0;
  const from = Math.max(2, last - 399), rows = sh.getRange(from, 1, last - from + 1, C.tag + 1).getValues();
  const day = Utilities.formatDate(when, TZ, "yyyy-MM-dd"), tg = String(row[C.tag] || ""), dev = String(row[C.dev] || ""), nk = plain_(row[C.nick]).toUpperCase();
  const same = r => tg ? String(r[C.tag] || "") === tg : (String(r[C.dev] || "") === dev && plain_(r[C.nick]).toUpperCase() === nk);
  return rows.some(r => Number(r[C.clear]) === 1 && String(r[C.set] || "") === set && same(r) && time_(r[C.date]) && Utilities.formatDate(new Date(time_(r[C.date])), TZ, "yyyy-MM-dd") === day) ? 1 : 0;
}

/* ── (v600) 🏝 마이타운 시간 — 아이·날마다 한 줄 (그날 모두 몇 분). 게임이 그날 합계를 보내므로 여러 번 와도 같은 값으로 덮음 ──
   「아이」 = 명단의 기기로 찾은 이름(기록 정리 탭과 같은 모양: 실제 이름 (게임 이름)) · 공용 패드면 고른 아이 이름 */
function mtSheet_(){
  const ss = SpreadsheetApp.openById(SHEET_ID);
  let sh = ss.getSheetByName(MT_SHEET);
  if (!sh){ sh = ss.insertSheet(MT_SHEET); sh.setFrozenRows(1); }
  if (sh.getRange(1, 1).getValue() === ""){
    sh.getRange(1, 1, 1, MT_COLS.length).setValues([MT_COLS.map(c=>c[1])]).setFontWeight("bold");
    sh.getRange("A:A").setNumberFormat("@"); sh.getRange("C:C").setNumberFormat("@");
  }
  return sh;
}
function rosterName_(dev, nick){
  try {
    const sh = SpreadsheetApp.openById(SHEET_ID).getSheetByName("명단"); if (!sh || !dev) return "";
    const rows = sh.getRange(5, 1, 196, 5).getValues();
    for (const r of rows){
      if ([r[2], r[3], r[4]].some(x => String(x).trim() === dev)){
        const rc = String(r[0]).trim(), rn = String(r[1]).trim();
        if (!rc && rn && nick) return "";                            // 공용 패드 줄(게임 이름 없음) → 고른 아이 이름으로
        return rn ? rn + (rc ? " (" + rc + ")" : "") : rc;
      }
    }
  } catch(e){}
  return "";
}
function mtLog_(d){
  const day = String(d.day || ""); if (!/^\d{4}-\d{2}-\d{2}$/.test(day)) return json_({ok:false, err:"day"});
  const dev = txt_(d.dev, 40), nick = plain_(txt_(d.nick, 20)), tg = tag_(d.tag) ? "#" + tag_(d.tag) : "";
  if (!dev && !tg) return json_({ok:false, err:"who"});
  const kid = (Number(d.pad) ? "" : rosterName_(dev, nick)) || nick || "친구";
  const min = Math.max(0, Math.min(1440, Math.round(Number(d.min) * 10) / 10 || 0)), segs = num_(d.segs, 500);
  const lock = LockService.getScriptLock();
  try {
    lock.waitLock(10000);
    const sh = mtSheet_(), last = sh.getLastRow(), N = MT_COLS.length;
    const rows = last >= 2 ? sh.getRange(2, 1, last - 1, N).getValues() : [];
    const key = r => String(r[0]) + "|" + (Number(d.pad) ? String(r[1]) : (String(r[2]) || String(r[3])));
    const want = day + "|" + (Number(d.pad) ? kid : (tg || dev));
    let hit = -1; for (let i = rows.length - 1; i >= 0 && i >= rows.length - 400; i--){ if (key(rows[i]) === want){ hit = i; break; } }
    const old = hit >= 0 ? rows[hit] : null;
    const out = [day, kid, tg || (old ? old[2] : ""), dev, Math.max(min, old ? Number(old[4]) || 0 : 0), Math.max(segs, old ? Number(old[5]) || 0 : 0), new Date(), txt_(d.ver, 20), nick];
    const at = hit >= 0 ? hit + 2 : last + 1;
    sh.getRange(at, 1).setNumberFormat("@"); sh.getRange(at, 3).setNumberFormat("@");
    sh.getRange(at, 1, 1, N).setValues([out]);
    sh.getRange(at, 7).setNumberFormat("yyyy-mm-dd hh:mm");
  } catch(err){ return json_({ok:false, err:"busy"}); }
  finally { try { lock.releaseLock(); } catch(_){} }
  return json_({ok:true});
}

/* ── (v563) 🏝 마을 현황 ── */
function has_(d, k){ return d && d[k] !== undefined && d[k] !== null && d[k] !== ""; }
function townSheet_(){
  const ss = SpreadsheetApp.openById(SHEET_ID);
  let sh = ss.getSheetByName(TOWN_SHEET);
  if (!sh){ sh = ss.insertSheet(TOWN_SHEET); sh.setFrozenRows(1); }
  if (sh.getRange(1, TOWN_COLS.length).getValue() === ""){
    sh.getRange(1, 1, 1, TOWN_COLS.length).setValues([TOWN_COLS.map(c=>c[1])]).setFontWeight("bold");
    sh.getRange("B:B").setNumberFormat("@");                         // #0006 의 0 이 안 없어지게
  }
  return sh;
}
/* 판 기록 한 줄 → 그 아이 줄을 고침 (없으면 새 줄). doPost 의 잠금 안에서 부름
   찾기: 태그가 있으면 같은 태그 줄 → 없으면 같은 이름이면서 태그가 빈 줄(그 줄에 태그를 붙임) · 태그가 없으면 같은 이름이면서 태그가 빈 줄 */
function townUpsert_(d, when){
  const nick = plain_(txt_(d.nick, 20)), tg = tag_(d.tag) ? "#" + tag_(d.tag) : "";
  if (!nick && !tg) return;
  if (!tg && (!nick || /^PLAYER$/i.test(nick))) return;              // 이름도 태그도 없는 줄은 누구 것인지 몰라 안 적음
  const sh = townSheet_(), last = sh.getLastRow(), N = TOWN_COLS.length;
  const rows = last >= 2 ? sh.getRange(2, 1, last - 1, N).getValues() : [];
  const up = nick.toUpperCase(); let hit = -1;
  if (tg) hit = rows.findIndex(r=>String(r[1]).trim() === tg);
  if (hit < 0) hit = rows.findIndex(r=>!String(r[1]).trim() && plain_(r[0]).toUpperCase() === up);
  const old = hit >= 0 ? rows[hit] : TOWN_COLS.map(()=>"");
  const out = TOWN_COLS.map(([k], i)=>{
    if (k === "nick") return nick || old[i];
    if (k === "tag")  return tg || old[i];
    if (k === "at")   return when;
    if (k === "ver")  return txt_(d.ver, 20) || old[i];
    if (k === "tup")  return has_(d, k) ? txt_(d.tup, 60) : old[i];
    if (TOWN_KEEP[k] && !has_(d, k)) return old[i];                  // 옛 게임 — 마을 칸은 전에 적힌 그대로
    if (k === "gems" || k === "earned"){ if (!has_(d, k)) return old[i]; }
    return num_(d[k], 10000000);
  });
  const at = hit >= 0 ? hit + 2 : last + 1;
  sh.getRange(at, 2).setNumberFormat("@");
  sh.getRange(at, 1, 1, N).setValues([out]);
  sh.getRange(at, 3).setNumberFormat("yyyy-mm-dd hh:mm");
}

/* ------------------------------ 랭킹 ------------------------------ */
function weekStart_(){                                              // 이번 주 월요일 0시 (한국 시간)
  const H9 = 9*3600*1000, now = Date.now(), k = new Date(now + H9);
  const back = (k.getUTCDay() + 6) % 7;
  return Date.UTC(k.getUTCFullYear(), k.getUTCMonth(), k.getUTCDate() - back) - H9;
}
function time_(v){
  if (v instanceof Date) return v.getTime();
  const s = String(v === undefined || v === null ? "" : v).trim();
  /* (v611) 날짜 칸에 글자로 들어간 줄 — 「2026-11-05 22:53」 · 「2026. 11. 5 오후 10:53:39」 (한국 시간) → 예전엔 못 읽어서 그 판이 랭킹에서 빠졌음 */
  const m = s.match(/^(\d{4})[.\-\/]\s*(\d{1,2})[.\-\/]\s*(\d{1,2})\.?\s*(?:(오전|오후|AM|PM)\s*)?(\d{1,2})?(?::(\d{2}))?(?::(\d{2}))?/i);
  if (m){ let h = Number(m[5] || 0); const ap = m[4] || ""; if (/오후|PM/i.test(ap) && h < 12) h += 12; if (/오전|AM/i.test(ap) && h === 12) h = 0;
    return Date.UTC(+m[1], +m[2] - 1, +m[3], h, Number(m[6] || 0), Number(m[7] || 0)) - 9 * 3600 * 1000; }
  const t = new Date(s).getTime(); return isFinite(t) ? t : 0;
}

function doGet(e){
  const p = (e && e.parameter) || {};
  if (p.key !== KEY) return json_({ok:false, err:"key"});
  if (p.act) return json_({ok:true, list:actsFor_(String(p.nick||""), String(p.dev||""), tag_(p.tag))});   // (v222) 원격 조치 · (v404) 대상에 #태그도
  if (p.notice) return json_({ok:true, v:SERVER_V, notices:notices_()});                          // (v264) 공지
  if (p.board) return json_(board_(p));                                                            // (v601) 🔥 실시간 랭킹
  const diff  = String(p.diff || "easy");
  const range = String(p.range || "week");
  const n     = Math.max(1, Math.min(100, Number(p.n) || 20));
  const dev   = String(p.dev || "");
  const since = range === "all" ? 0 : weekStart_();

  const sh = sheet_(), last = sh.getLastRow();
  if (last < 2) return json_({ok:true, list:[]});
  if (diff === "dex" && since) return json_({ok:true, list:weekList_(sh, last, "words", n, dev)});   // (v601) 이번 주 = 이번 주에 모은 단어 수 (예전: 그때까지 모은 전체 수)
  if (diff === "study") return json_({ok:true, list:weekList_(sh, last, "study", n, dev, range === "all" ? 0 : null)});   // (v618) 전체 = 지금까지 (같은 Stage 는 가장 잘한 판 하나)   // (v601) 📚 이번 주 공부 점수
  if (diff === "dex") return json_({ok:true, list:dexRank_(sh, last, since, n, dev)});   // (v221) 단어 수집 랭킹 (전체)
  const rows = sh.getRange(2, 1, last - 1, COLS.length).getValues();   // (v404) 태그 칸(맨 끝)까지

  const best = {}, P = people_(rows);                               // 태그(없으면 닉네임) → 최고 기록 — (v404) 같은 이름이 둘이어도 안 섞이고, 이름을 바꿔도 한 줄 · (v416) 👤 뗀 이름으로 묶음
  rows.forEach(r=>{
    if (String(r[C.diff]) !== diff) return;
    if (r[C.rule] && String(r[C.rule]) !== "normal") return;
    const t = time_(r[C.date]); if (t < since) return;
    if (P.hide(r)) return;
    const nick = plain_(r[C.nick]) || "PLAYER", score = Number(r[C.score]) || 0, tg = P.tag(r), id = P.id(r);
    let b = best[id];
    if (!b){ b = best[id] = {nick, tag:tg, score:0, stage:0, title:"", tt:0, nt:0, me:false}; }
    if (t >= b.nt){ b.nick = nick; b.nt = t; }                      // 가장 최근 이름
    if (score > b.score){ b.score = score; b.stage = Number(r[C.stage]) || 0; }
    if (r[C.char] && t >= (b.ct || 0)){ b.ch = String(r[C.char]); b.ct = t; }   // (v618) 랭킹 얼굴
    if (r[C.title] && t >= b.tt){ b.title = String(r[C.title]); b.tt = t; }  // 가장 최근 칭호
    if (dev && String(r[C.dev]) === dev) b.me = true;
  });

  const list = Object.keys(best).map(k=>best[k])
    .sort((a,b)=>b.score - a.score).slice(0, n)
    .map(b=>({nick:b.nick, tag:b.tag, ch:b.ch || "", score:b.score, stage:b.stage, title:b.title, me:b.me}));
  return json_({ok:true, list});
}

/* ── (v601) 🔥 이번 주 랭킹 셋 — 사용자: 「이번 주 단어 모은 수여야 하는데 전체로 나와」 「달리기 점수 1등 이런 게 나와야」 · 공부 점수로 랭킹
   study = 이번 주 오늘의 30(끝까지 푼 판)의 스테이지 점수 + 푼 문제 수 (v603, 예전 = 맞힌 수 합) — 같은 날 같은 Stage 를 또 끝내면 안 셈(반복으로 올리기 X) · 배틀·레이드는 뺌
   words = 이번 주에 모은 단어 수 = 이번 주 가장 큰 도감 수 − 이번 주 전 가장 큰 도감 수 (이번 주에 처음 온 아이 = 이번 주 가장 큰 수) · 공용 패드 줄은 안 셈(주인 패드는 셈)
   run   = 이번 주 달리기(방식 normal) 가장 높은 점수 (난이도 상관없이)
   cut = 이 때까지의 줄만 (어제 순위 = 지금 − 24시간)
   (v602) 사용자: 「이번 주 1등 하려고 초5 가 초1-2 보카로 달릴까」 → 아이마다 「내 단계」 = 최근 4주 오늘의 30 에서 가장 많이 푼 학년(유치원·G1-2·G3-4·G5-6·중등)
          → 내 단계보다 쉬운 단어장으로 한 공부·달리기는 랭킹 점수에 안 넣음 (보석·기록은 그대로) · 단계를 모르는 판(복습·틀린 단어·모든 학년)은 셈 */
const LV_S_ = s => /^유치원/.test(s) ? 0 : /^G1-2/.test(s) ? 1 : /^G3-4/.test(s) ? 2 : /^G5-6/.test(s) ? 3 : /^중등/.test(s) ? 4 : -1;
const LV_R_ = s => { const k = String(s || "").split("/")[0]; const m = {kinder:0, abc:0, short:0, long:0, digr:0, vowel2:0, sight:0, basic:1, elem:2, g56:3, rd1:3, rd2:3, rd3:3, mid:4, mv0:4, mv1:4, jl:4}; return k in m ? m[k] : -1; };
const LV_NM = ["유치원", "G1-2", "G3-4", "G5-6", "중등"];
function weekCore_(rows, P, ws, cut, det){   // (v618) det = 아이마다 날마다 점수·센 판 목록도 (📊 내 기록)
  const M = {study:{}, words:{}, run:{}}, idx = [];
  rows.forEach((r, i)=>{ const t = time_(r[C.date]); if (!t || t >= cut || P.hide(r)) return; const nk = plain_(r[C.nick]), id = P.id(r);
    if (!nk || id === "PLAYER" || /^한양|패드$/.test(nk)) return; idx.push([t, i, id]); });
  idx.sort((a, b)=>a[0] - b[0]);
  const RL = rankLv_(), FIX = {};   // (v631) 선생님이 정한 단계 · 빼기
  for (let j = idx.length - 1; j >= 0; j--) if (RL[idx[j][2]] === "x") idx.splice(j, 1);
  const LC = {}, LV = {};   // 내 단계 = 최근 4주(cut 전) 공부 줄에서 가장 많은 학년 (같으면 높은 쪽)
  idx.forEach(([t, i, id])=>{ if (t < cut - 28 * 864e5) return; const r = rows[i]; if (String(r[C.diff] || "") !== "study") return; const lv = LV_S_(String(r[C.set] || "")); if (lv < 0) return; (LC[id] = LC[id] || [0,0,0,0,0])[lv]++; });
  Object.keys(LC).forEach(id=>{ let b = -1, n = 0; LC[id].forEach((c, l)=>{ if (c > 0 && c >= n){ n = c; b = l; } }); LV[id] = b; });
  Object.keys(RL).forEach(id=>{ if (typeof RL[id] === "number"){ LV[id] = RL[id]; FIX[id] = 1; } });   // (v631) 정한 단계가 자동보다 먼저
  const easy = (id, lv)=>lv >= 0 && id in LV && lv < LV[id];
  const ent = (k, id, r, t)=>{ let b = M[k][id]; if (!b) b = M[k][id] = {id, nick:"", tag:"", score:0, n:0, nt:0}; if (t >= b.nt){ b.nick = plain_(r[C.nick]); b.nt = t; const ch = String(r[C.char] || ""); if (ch) b.ch = ch; } const tg = P.tag(r); if (tg) b.tag = tg; return b; };   // (v618) ch = 캐릭터 (랭킹 얼굴)
  const done = {}, dxB = {}, dxW = {}, dxM = {}, first = {};
  idx.forEach(([t, i, id])=>{ const r = rows[i], rule = String(r[C.rule] || ""), diff = String(r[C.diff] || "");
    if (!(id in first)) first[id] = t;
    const dx = (P.sharedDev(r) && !String(r[C.own] || "")) ? 0 : (Number(r[C.dex]) || 0);
    if (dx > 0){ if (t < ws) dxB[id] = Math.max(dxB[id] || 0, dx); else { dxW[id] = Math.max(dxW[id] || 0, dx); dxM[id] = Math.min(dxM[id] || 1e9, dx); } }
    if (t < ws) return;
    if (diff === "study" && /^study/.test(rule) && !/^study-(battle|raid)/.test(rule)){
      if (Number(r[C.clear]) !== 1) return;
      const DT = det ? (ok, v)=>{ const e = ent("study", id, r, t); const x = [String(r[C.set] || "").slice(0, 34), v, ok, t]; (e.ent = e.ent || []).push(x); if (e.ent.length > 16) e.ent.shift(); return x; } : ()=>null;
      if (/연습\s*$/.test(String(r[C.set] || ""))){ DT("p", 0); return; }            // (v611) 「Stage 3-3 연습」 = 다 푼 Stage 를 다시 연습한 판 → 공부 점수 X (예전엔 다른 Stage 로 보고 또 셈)
      if (easy(id, LV_S_(String(r[C.set] || "")))){ DT("e", 0); return; }            // (v602) 내 단계보다 쉬운 판
      /* (v613) 사용자: 「몇 개를 하든 하루에 몰아서 하든 제한 X · 계속 똑같은 걸 반복하는 애들은 막자」
         → Stage 판(「… Stage 3-2 ★3」처럼 Stage 가 적힌 것)은 한 주에 같은 Stage·같은 단계는 한 번만 — 여러 번 풀면 가장 잘한 판 하나 (예전: 날마다 또 셈)
         → Stage 가 없는 판(복습 · 틀린 단어 · 주간 시험)은 예전처럼 하루에 한 번 */
      const set0 = String(r[C.set] || ""), key = id + "|" + (/Stage\s*\d/.test(set0) ? "W" : Utilities.formatDate(new Date(t), TZ, "yyyy-MM-dd")) + "|" + set0;
      /* (v603) 사용자: 「데일리 30 랭킹은 푼 문제랑 스테이지 점수 총합으로」 → 공부 점수 = 스테이지 점수(처음에 맞힌 문제 ×10, 시트 「점수」) + 푼 문제 수(맞힘+틀림) */
      const b = ent("study", id, r, t), q = (Number(r[C.right]) || 0) + (Number(r[C.wrong]) || 0), ss = Number(r[C.score]) || 0, was = done[key];
      if (was && was.v >= ss + q){ DT("w", ss + q); return; }           // 같은 Stage 를 또 — 전보다 못하면 안 셈
      const di = Math.floor((t - ws) / 864e5);
      if (was){ b.score -= was.v; b.q -= was.q; b.ss -= was.ss; if (det && b.day) b.day[was.di] -= was.v; if (was.e) was.e[2] = "r"; } else b.n++;   // 더 잘했으면 그 판으로 바꿈 (판 수는 그대로)
      if (det){ if (!b.day) b.day = [0,0,0,0,0,0,0]; if (di >= 0 && di < 7) b.day[di] += ss + q; }
      done[key] = {v:ss + q, q, ss, di, e:DT("o", ss + q)};
      b.score += ss + q; b.q = (b.q || 0) + q; b.ss = (b.ss || 0) + ss;
    } else if (diff !== "study" && (!rule || rule === "normal")){
      if (easy(id, LV_R_(r[C.set]))) return;                          // (v602) 내 단계보다 쉬운 단어장으로 달린 판
      const b = ent("run", id, r, t), sc = Number(r[C.score]) || 0; if (sc > b.score){ b.score = sc; b.n = Number(r[C.stage]) || 0; }
    }
    if (dx > 0) ent("words", id, r, t);
  });
  Object.keys(M.words).forEach(id=>{ const w = dxW[id] || 0, b = id in dxB ? dxB[id] : (first[id] >= ws ? 0 : (dxM[id] || w));   // 전 기록이 공용 패드뿐 = 이번 주 처음 수부터
    M.words[id].score = Math.max(0, w - b); });
  const out = {}; Object.keys(M).forEach(k=>{ out[k] = Object.keys(M[k]).map(id=>Object.assign(M[k][id], {lv: id in LV ? LV[id] : -1, fix: FIX[id] ? 1 : 0})).filter(b=>b.score > 0).sort((a, b)=>b.score - a.score || a.nt - b.nt); });
  return out;
}
function weekList_(sh, last, k, n, dev, ws0){
  const rows = sh.getRange(2, 1, last - 1, COLS.length).getValues(), P = people_(rows), L = weekCore_(rows, P, ws0 == null ? weekStart_() : ws0, Date.now() + 1)[k];
  const mine = {}; if (dev) rows.forEach(r=>{ if (String(r[C.dev]) === dev) mine[P.id(r)] = 1; });
  return L.slice(0, n).map(b=>({nick:b.nick, tag:b.tag, ch:b.ch || "", score:b.score, stage:b.n, title:"", me:!!mine[b.id]}));
}
/* (v601) 🔥 실시간 랭킹 — 게임 첫 화면 「실시간 검색어」. 셋 다 10등까지 + 어제(24시간 전)보다 몇 칸 올랐나(mv) · 1분 동안 같은 답(시트 부담 줄이기) */
function board_(p){
  p = p || {};
  let cache = null, full = null; try { cache = CacheService.getScriptCache(); const hit = cache.get("board_v4"); if (hit) full = JSON.parse(hit); } catch(e){}
  if (!full){
    const sh = sheet_(), last = sh.getLastRow(), now = Date.now(), ws = weekStart_();
    full = {at:now, ws, L:{study:[], words:[], run:[]}};
    if (last >= 2){
      const rows = sh.getRange(2, 1, last - 1, COLS.length).getValues(), P = people_(rows);
      const A = weekCore_(rows, P, ws, now + 1, true), B = now - 864e5 > ws ? weekCore_(rows, P, ws, now - 864e5) : {study:[], words:[], run:[]};
      Object.keys(A).forEach(k=>{ const old = {}; B[k].forEach((b, i)=>{ old[b.id] = i + 1; });
        full.L[k] = A[k].slice(0, 80).map((b, i)=>({id:b.id, nick:b.nick, tag:b.tag, ch:b.ch || "", score:b.score, n:b.n, q:b.q || 0, ss:b.ss || 0, lv:b.lv, fix:b.fix || 0, mv: old[b.id] ? old[b.id] - (i + 1) : "new", day:k === "study" ? b.day : undefined, ent:k === "study" ? b.ent : undefined})); });
      try { full.hof = hof_(rows, P, A, now, ws); } catch(eh){ full.hof = {err:String(eh).slice(0, 80)}; }   // (v618) 🏛 명예의 전당
      try { full.lg = lgHist_(rows, P, ws); } catch(el){ full.lg = {}; }   // (v635) 🏅 지난주 나 넘기
    }
    try { if (cache) cache.put("board_v4", JSON.stringify(full), 60); } catch(e){ try { const f2 = JSON.parse(JSON.stringify(full)); Object.keys(f2.L).forEach(k=>f2.L[k].forEach(b=>{ delete b.ent; })); cache.put("board_v4", JSON.stringify(f2), 60); } catch(e2){} }
  }
  /* (v602) 나: 순위 · 어제보다 · 바로 위 친구(따라잡을 점수) — 태그 → 없으면 👤 뗀 이름 */
  const tg = tag_(p.tag), me = tg ? "#" + tg : plain_(txt_(p.nick, 20)).toUpperCase();
  const H = full.hof || {}, stk = H.streak || {};
  const pub = (b, k, i)=>{ const o = {nick:b.nick, tag:b.tag, ch:b.ch, score:b.score, n:b.n, q:b.q, ss:b.ss, mv:b.mv}; if (i === 0 && stk[k] && stk[k].id === b.id) o.st = stk[k].n; return o; };   // (v618) 1위 = 🔥 며칠째
  const res = {ok:true, v:SERVER_V, at:full.at, ws:full.ws, boards:{}, me:{}};
  Object.keys(full.L).forEach(k=>{ const L = full.L[k]; res.boards[k] = L.slice(0, 10).map((b, i)=>pub(b, k, i));
    const i = me ? L.findIndex(b=>b.id === me || (!tg && String(b.nick).toUpperCase() === me)) : -1;   // 태그가 없는 기기 = 이름으로
    if (i >= 0) res.me[k] = Object.assign(pub(L[i], k, i), {rank:i + 1, of:L.length, lv:L[i].lv >= 0 ? LV_NM[L[i].lv] : "", fix:L[i].fix || 0, above: i > 0 ? {nick:L[i - 1].nick, score:L[i - 1].score} : null}, k === "study" ? {day:L[i].day || null, ent:L[i].ent || null} : {}); });
  /* (v635) 🏅 나의 리그 — 지난주 나 넘기 (이번 주 점수 · 지난 6주 · 지킨 주 연속) */
  if (me && full.lg){ const st = full.L.study.find(b=>b.id === me || (!tg && String(b.nick).toUpperCase() === me)), id = st ? st.id : me;
    if (st || full.lg[id]) res.me.lg = lgOf_(st ? st.score : 0, full.lg[id], full.lg._b, st ? st.lv : -1); }
  /* (v618) 🏛 명예의 전당 — 모두에게 같은 것 + 나(지난주 순위 · 메달 · 연속 공부 날) */
  if (H.cal){ const strip = x=>x ? {nick:x.nick, tag:x.tag, score:x.score, n:x.n} : null;
    res.hof = {cal:H.cal, streak:{}, weeks:H.weeks, longest:H.longest, medals:{}, att:(H.att || []).slice(0, 10).map(strip), lastKey:H.lastKey, ch:{}};
    Object.keys(full.L).forEach(k=>full.L[k].forEach(b=>{ if (b.ch){ res.hof.ch[b.tag ? "#" + b.tag : String(b.nick).toUpperCase()] = b.ch; } }));   // 이름표 → 캐릭터 (명예의 전당 얼굴)
    Object.keys(stk).forEach(k=>{ res.hof.streak[k] = {nick:stk[k].nick, tag:stk[k].tag, n:stk[k].n}; });
    Object.keys(H.medals || {}).forEach(k=>{ res.hof.medals[k] = H.medals[k].slice(0, 5).map(x=>({nick:x.nick, tag:x.tag, g:x.g, s:x.s, b:x.b})); });
    const meId = (()=>{ if (!me) return ""; for (const k of Object.keys(full.L)){ const b = full.L[k].find(b=>b.id === me || (!tg && String(b.nick).toUpperCase() === me)); if (b) return b.id; } return tg ? "#" + tg : me; })();
    if (meId){ res.me.hof = {last:(H.lastRank || {})[meId] || null, medal:((H.medalOf || {}).study || {})[meId] || null, att:(H.attOf || {})[meId] || 0, best:(H.bestOf || {})[meId] || null}; }
  }
  return res;
}

/* ── (v636) ⚔️ 스테이지 도전장 ──
   사용자: 「친구 도전장은 10문제보다 스테이지 대결 — 보라색(💜 심화) 같은」
   · 보내는 아이가 먼저 한 Stage 의 💜 도전 판(같은 씨앗 seed = 같은 문제)을 풀고 → 친구에게 보냄 → 친구가 같은 문제로 → 맞힌 수, 같으면 시간
   · 아이 = 랭킹과 같은 이름표(#태그 또는 이름) · 7일 지나면 「시간 끝」 · 한 아이가 하루에 보낼 수 있는 도전장 10장
   · 「도전장」 탭: 번호 · 보낸 때 · 보낸 아이 · 이름 · 받는 아이 · 이름 · 책 · Stage · 이름표 · 씨앗 · 보낸 점수 · 문제 수 · 시간 · 받은 점수 · 문제 수 · 시간 · 상태 · 끝난 때 */
const DUEL_SHEET = "도전장";
const DUEL_COLS = [["id","번호"],["at","보낸 때"],["from","보낸 아이"],["fnick","보낸 이름"],["to","받는 아이"],["tnick","받는 이름"],["set","책"],["n","Stage"],["label","이름표"],["seed","씨앗"],
  ["fsc","보낸 점수"],["ftot","문제 수"],["fms","시간(ms)"],["tsc","받은 점수"],["ttot","받은 문제 수"],["tms","받은 시간(ms)"],["st","상태"],["dat","끝난 때"]];
const DUEL_DAYS = 7, DUEL_DAY_MAX = 10;
const DI = {}; DUEL_COLS.forEach((c, i)=>{ DI[c[0]] = i; });
function duelSheet_(){ const ss = SpreadsheetApp.openById(SHEET_ID); let sh = ss.getSheetByName(DUEL_SHEET);
  if (!sh){ sh = ss.insertSheet(DUEL_SHEET); sh.getRange(1, 1, 1, DUEL_COLS.length).setValues([DUEL_COLS.map(c=>c[1])]); sh.setFrozenRows(1); try { sh.getRange("A:A").setNumberFormat("@"); sh.getRange("C:C").setNumberFormat("@"); sh.getRange("E:E").setNumberFormat("@"); } catch(e){} }
  return sh; }
function duelId_(v){ const s = String(v || "").trim(); if (/^#\d{4}$/.test(s)) return s; const t = tag_(s); if (t && /^\d+$/.test(s.replace(/^#/, ""))) return "#" + t; return plain_(txt_(s, 20)).toUpperCase(); }
function duelPub_(r){ const o = {}; DUEL_COLS.forEach(([k], i)=>{ o[k] = r[i] instanceof Date ? r[i].getTime() : r[i]; }); ["n","seed","fsc","ftot","fms","tsc","ttot","tms"].forEach(k=>{ o[k] = Number(o[k]) || 0; }); o.id = String(o.id); return o; }
function duel_(d){
  const now = Date.now();
  if (d.type === "duelFriends"){   // 최근 4주에 공부·달리기를 한 아이들 (선생님·숨김·공용 패드 이름 빼고)
    const sh = sheet_(), last = sh.getLastRow(); if (last < 2) return json_({ok:true, v:SERVER_V, list:[]});
    const rows = sh.getRange(2, 1, last - 1, COLS.length).getValues(), P = people_(rows), M = {};
    rows.forEach(r=>{ const t = time_(r[C.date]); if (!t || t < now - 28 * 864e5 || P.hide(r)) return; const nk = plain_(r[C.nick]); if (!nk || nk === "PLAYER" || /^한양|패드$/.test(nk)) return;
      const id = P.id(r), b = M[id]; if (!b || t >= b.t) M[id] = {id, nick:nk, tag:P.tag(r) || "", t}; });
    const list = Object.keys(M).map(k=>M[k]).sort((a, b)=>b.t - a.t).slice(0, 120).map(x=>({id:x.id, nick:x.nick, tag:x.tag}));
    return json_({ok:true, v:SERVER_V, list});
  }
  const sh = duelSheet_(), last = sh.getLastRow(), R = last >= 2 ? sh.getRange(2, 1, last - 1, DUEL_COLS.length).getValues() : [];
  const me = duelId_(d.me);
  if (d.type === "duelSend"){
    const from = me, to = duelId_(d.to); if (!from || !to || from === to) return json_({ok:false, err:"who"});
    const today = R.filter(r=>String(r[DI.from]) === from && time_(r[DI.at]) > now - 864e5).length; if (today >= DUEL_DAY_MAX) return json_({ok:false, err:"max"});
    const id = String(now).slice(-9) + Math.floor(Math.random() * 90 + 10);
    const row = DUEL_COLS.map(([k])=>{
      if (k === "id") return id; if (k === "at") return new Date(now); if (k === "from") return from; if (k === "to") return to;
      if (k === "fnick" || k === "tnick") return txt_(d[k], 20); if (k === "set") return txt_(d.set, 20); if (k === "label") return txt_(d.label, 40);
      if (k === "st") return "wait"; if (k === "dat" || k === "tsc" || k === "ttot" || k === "tms") return "";
      return num_(d[k], k === "fms" ? 36e5 : k === "seed" ? 2e9 : 1000); });
    sh.appendRow(row); return json_({ok:true, v:SERVER_V, id});
  }
  if (d.type === "duelDone"){
    const i = R.findIndex(r=>String(r[DI.id]) === String(d.id)); if (i < 0) return json_({ok:false, err:"none"});
    const r = R[i]; if (String(r[DI.to]) !== me) return json_({ok:false, err:"who"}); if (String(r[DI.st]) !== "wait") return json_({ok:true, v:SERVER_V, d:duelPub_(r), again:1});
    if (time_(r[DI.at]) < now - DUEL_DAYS * 864e5) return json_({ok:false, err:"old"});
    r[DI.tsc] = num_(d.sc, 1000); r[DI.ttot] = num_(d.tot, 1000); r[DI.tms] = num_(d.ms, 36e5); r[DI.st] = "done"; r[DI.dat] = new Date(now);
    sh.getRange(i + 2, 1, 1, DUEL_COLS.length).setValues([r]); return json_({ok:true, v:SERVER_V, d:duelPub_(r)});
  }
  /* duelBox: 나한테 온 것(기다림) · 내가 보낸 것 · 끝난 것 — 14일 안 */
  const box = {inbox:[], sent:[], got:[]};
  R.forEach(r=>{ const t = time_(r[DI.at]); if (!t || t < now - 14 * 864e5) return; const o = duelPub_(r); if (o.st === "wait" && t < now - DUEL_DAYS * 864e5) o.st = "old";
    if (String(r[DI.to]) === me){ if (o.st === "wait") box.inbox.push(o); else box.got.push(o); } else if (String(r[DI.from]) === me) box.sent.push(o); });
  const by = (a, b)=>b.at - a.at; box.inbox.sort(by); box.sent.sort(by); box.got.sort(by);
  return json_({ok:true, v:SERVER_V, inbox:box.inbox.slice(0, 20), sent:box.sent.slice(0, 20), got:box.got.slice(0, 20)});
}

/* ── (v635) 🏅 나의 리그 — 「지난주 나 넘기」 ──
   사용자: 랭킹은 잘하는 아이만 위 → 모든 아이가 이길 수 있는 경쟁. 점수 = 랭킹과 같은 📚 오늘의 30 주간 점수(랭킹 단계 규칙 그대로).
   · 넘기 = 이번 주 > 지난주 · 지키기 = 지난주의 90% 이상 (그리고 한 판 이상 = LG_MIN 점) · 지킨 주가 이어지면 칭호
   · 지난 6주는 바뀌지 않으니 주마다 한 번 계산해 6시간 캐시 (lg2_<월요일>)
   · (v638) 사용자: 「원래 점수가 낮았던 애들은 칭호를 따기가 쉬워진다」 → 주마다 「기준」 = 그 주 같은 랭킹 단계 아이들 점수 가운데값의 60% (3명 안 되면 전체 · 최소 LG_MIN)
     칭호 연속 주 = 기준 이상 + 지난주 90% 이상인 주만 · 이번 주 목표·지키기도 기준보다 낮을 수 없음 (기준 = 지난주 것) */
const LG_MIN = 300, LG_KEEP = 0.9, LG_WEEKS = 6, LG_BAR = 0.6;
function lgMed_(a){ a = a.slice().sort((x, y)=>x - y); const n = a.length; return n ? (n % 2 ? a[(n - 1) / 2] : (a[n / 2 - 1] + a[n / 2]) / 2) : 0; }
function lgBars_(list){   // 한 주 study 목록 → {a: 전체 기준, 0~4: 단계 기준}
  const all = list.map(x=>x.score), o = {a: all.length >= 3 ? Math.max(LG_MIN, Math.round(lgMed_(all) * LG_BAR)) : LG_MIN};
  for (let lv = 0; lv <= 4; lv++){ const L = list.filter(x=>x.lv === lv).map(x=>x.score); o[lv] = L.length >= 3 ? Math.max(LG_MIN, Math.round(lgMed_(L) * LG_BAR)) : o.a; }
  return o;
}
function lgHist_(rows, P, ws){
  const key = "lg2_" + ws; let c = null; try { c = CacheService.getScriptCache(); const h = c.get(key); if (h) return JSON.parse(h); } catch(e){}
  const H = {_b: []};
  for (let i = 1; i <= LG_WEEKS; i++){ const a = ws - 7 * i * 864e5, b = ws - 7 * (i - 1) * 864e5; const W = weekCore_(rows, P, a, b);
    H._b[i - 1] = lgBars_(W.study);
    W.study.forEach(x=>{ (H[x.id] = H[x.id] || new Array(LG_WEEKS).fill(0))[i - 1] = x.score; }); }
  try { if (c) c.put(key, JSON.stringify(H), 21600); } catch(e){}
  return H;
}
function lgOf_(cur, W, BB, lv){   // BB = H._b (주마다 기준) · lv = 랭킹 단계(0~4, 모르면 -1)
  W = (W || []).slice(0, LG_WEEKS); while (W.length < LG_WEEKS) W.push(0);
  const bar = j=>{ const o = (BB || [])[j]; return o ? (lv >= 0 && o[lv] ? o[lv] : o.a) || LG_MIN : LG_MIN; };
  let st = 0; for (let j = 0; j < W.length; j++){ const a = W[j], b = W[j + 1] || 0; if (a >= bar(j) && a >= LG_KEEP * b) st++; else break; }
  const last = W[0], B0 = bar(0), keep = Math.max(B0, Math.round(last * LG_KEEP)), goal = Math.max(B0, last + 1);
  return {now:cur, last, keep, goal, bar:B0, st, hist:W, win:cur >= goal ? 2 : cur >= keep ? 1 : 0};
}

/* ── (v618) 🏛 명예의 전당 · 🔥 연속 1위 ──
   사용자: 「명예의 전당 · 며칠 연속 1위 · 데일리 30 이 메인」
   · 「명예의 전당」 탭 = 날마다 밤 12시의 1위(종류 day) · 주마다 1~3위(종류 week) — 한 번 적으면 그대로 (scores 가 보관 탭으로 옮겨져도 남음)
   · 연속 1위 = 지금 1위인 아이가 어제·그제… 밤 12시에도 1위였던 날 수 + 오늘 (월요일에 주가 바뀌어도 이어짐)
   · 개근 = 오늘의 30 을 끝까지 푼 날이 며칠 이어졌나 (오늘 아직 안 했으면 어제까지) */
const HOF_SHEET = "명예의 전당";
const HOF_COLS = [["kind","종류"], ["key","날짜"], ["cat","분야"], ["rank","순위"], ["id","아이"], ["nick","이름"], ["tag","태그"], ["score","점수"], ["at","적은 때"]];
const HOF_CATS = ["study", "words", "run"];
function hofSheet_(){
  const ss = SpreadsheetApp.openById(SHEET_ID); let sh = ss.getSheetByName(HOF_SHEET);
  if (!sh){ sh = ss.insertSheet(HOF_SHEET); sh.getRange(1, 1, 1, HOF_COLS.length).setValues([HOF_COLS.map(c=>c[1])]); sh.setFrozenRows(1); sh.getRange("B:B").setNumberFormat("@"); sh.getRange("E:G").setNumberFormat("@"); }
  return sh;
}
const ymdK_ = t=>Utilities.formatDate(new Date(t), TZ, "yyyy-MM-dd");
function wsOf_(t){ const H9 = 9*3600*1000, k = new Date(t + H9), back = (k.getUTCDay() + 6) % 7; return Date.UTC(k.getUTCFullYear(), k.getUTCMonth(), k.getUTCDate() - back) - H9; }
function dayStart_(t){ const H9 = 9*3600*1000, k = new Date(t + H9); return Date.UTC(k.getUTCFullYear(), k.getUTCMonth(), k.getUTCDate()) - H9; }
function hof_(rows, P, A, now, ws){
  const sh = hofSheet_(), last = sh.getLastRow();
  let H = last >= 2 ? sh.getRange(2, 1, last - 1, HOF_COLS.length).getValues().map(r=>({kind:String(r[0]), key:ymd_(r[1]), cat:String(r[2]), rank:Number(r[3]) || 0, id:String(r[4] || ""), nick:String(r[5] || ""), tag:String(r[6] || ""), score:Number(r[7]) || 0})) : [];
  const have = {}; H.forEach(h=>{ have[h.kind + "|" + h.key] = 1; });
  let t0 = 0; rows.forEach(r=>{ const t = time_(r[C.date]); if (t && (!t0 || t < t0)) t0 = t; });
  let add = []; const stamp = new Date(), today0 = dayStart_(now);
  if (t0){
    let budget = 45;                                                       // 한 번에 너무 오래 걸리지 않게 (남은 날은 다음 번에)
    for (let d = dayStart_(t0); d < today0 && budget > 0; d += 864e5){ const key = ymdK_(d); if (have["day|" + key]) continue; budget--;
      const L = weekCore_(rows, P, wsOf_(d), d + 864e5);
      HOF_CATS.forEach(c=>{ const b = L[c][0]; add.push(["day", key, c, b ? 1 : 0, b ? b.id : "", b ? b.nick : "", b ? b.tag : "", b ? b.score : 0, stamp]); }); }
    for (let w = wsOf_(t0); w + 7 * 864e5 <= now && budget > 0; w += 7 * 864e5){ const key = ymdK_(w); if (have["week|" + key]) continue; budget--;
      const L = weekCore_(rows, P, w, w + 7 * 864e5);
      HOF_CATS.forEach(c=>{ const top = L[c].slice(0, 3); if (!top.length) add.push(["week", key, c, 0, "", "", "", 0, stamp]);
        top.forEach((b, i)=>add.push(["week", key, c, i + 1, b.id, b.nick, b.tag, b.score, stamp])); }); }
  }
  if (add.length){ const lock = LockService.getScriptLock();
    try { lock.waitLock(5000); const l2 = sh.getLastRow();
      if (l2 > last){ const got = {}; sh.getRange(last + 1, 1, l2 - last, 2).getValues().forEach(r=>{ got[String(r[0]) + "|" + ymd_(r[1])] = 1; }); add = add.filter(r=>!got[r[0] + "|" + r[1]]); }   // (v621) 두 사람이 동시에 열면 같은 날을 두 번 적던 것
      if (add.length) sh.getRange(l2 + 1, 1, add.length, HOF_COLS.length).setValues(add);
      H = H.concat(add.map(r=>({kind:r[0], key:r[1], cat:r[2], rank:r[3], id:r[4], nick:r[5], tag:r[6], score:r[7]}))); } catch(e){} finally { try { lock.releaseLock(); } catch(_){} } }
  const pick = b=>b ? {id:b.id, nick:b.nick, tag:b.tag, score:b.score} : null;
  const out = {cal:{}, streak:{}, weeks:{}, longest:{}, medals:{}, medalOf:{}, lastRank:{}, bestOf:{}};
  HOF_CATS.forEach(c=>{
    const days = H.filter(h=>h.kind === "day" && h.cat === c).sort((a, b)=>a.key < b.key ? -1 : 1), cur = A[c][0] || null, dayOf = {};
    days.forEach(h=>{ dayOf[h.key] = h; });
    /* 이번 주 월~일: 지난 날 = 그날 밤 12시 1위 · 오늘 = 지금 1위 */
    out.cal[c] = [0,1,2,3,4,5,6].map(i=>{ const d = ws + i * 864e5, key = ymdK_(d); if (d > now) return null; if (d === today0 || key === ymdK_(now)) return cur ? {nick:cur.nick, tag:cur.tag, now:1} : null; const h = dayOf[key]; return h && h.rank ? {nick:h.nick, tag:h.tag} : null; });
    /* 지금 1위의 연속 (오늘 포함) */
    if (cur){ let n = 1; for (let d = today0 - 864e5; ; d -= 864e5){ const h = dayOf[ymdK_(d)]; if (!h || h.id !== cur.id) break; n++; } out.streak[c] = {id:cur.id, nick:cur.nick, tag:cur.tag, n}; }
    /* 가장 오래 1위 (지금 이어지는 것도) */
    const runs = []; let rn = null;
    days.forEach(h=>{ if (h.rank && rn && rn.id === h.id) { rn.n++; rn.end = h.key; } else { if (rn) runs.push(rn); rn = h.rank ? {id:h.id, nick:h.nick, tag:h.tag, n:1, end:h.key} : null; } });
    if (rn) runs.push(rn);
    if (out.streak[c]){ const s = out.streak[c], lastR = runs[runs.length - 1]; if (lastR && lastR.id === s.id && lastR.end === ymdK_(today0 - 864e5)){ lastR.n = s.n; lastR.end = ymdK_(now); lastR.now = 1; } else runs.push({id:s.id, nick:s.nick, tag:s.tag, n:1, end:ymdK_(now), now:1}); }
    out.longest[c] = runs.sort((a, b)=>b.n - a.n || (a.end < b.end ? 1 : -1)).slice(0, 5).map(r=>({nick:r.nick, tag:r.tag, n:r.n, end:r.end, now:r.now || 0}));
    /* 주마다 1~3위 (최근 8주) · 메달 */
    const wk = {}; H.filter(h=>h.kind === "week" && h.cat === c && h.rank).forEach(h=>{ (wk[h.key] = wk[h.key] || [])[h.rank - 1] = h; });
    const keys = Object.keys(wk).sort().reverse();
    out.weeks[c] = keys.slice(0, 8).map(k=>({key:k, top:wk[k].filter(Boolean).map(h=>({nick:h.nick, tag:h.tag, score:h.score}))}));
    const M = {}; keys.forEach(k=>wk[k].forEach((h, i)=>{ if (!h) return; const m = M[h.id] = M[h.id] || {nick:h.nick, tag:h.tag, g:0, s:0, b:0}; m[["g","s","b"][i]]++; }));
    out.medalOf[c] = M; out.medals[c] = Object.keys(M).map(id=>M[id]).sort((a, b)=>(b.g - a.g) || (b.s - a.s) || (b.b - a.b)).slice(0, 5);
    if (c === "study") keys.forEach(k=>wk[k].forEach((h, i)=>{ if (h && (!out.bestOf[h.id] || i + 1 < out.bestOf[h.id].rank)) out.bestOf[h.id] = {rank:i + 1, key:k}; }));
  });
  /* 지난주 오늘의 30 — 모든 아이의 순위 (월요일 발표) */
  out.lastKey = ymdK_(ws - 7 * 864e5);
  if (now - ws < 7 * 864e5){ const LW = weekCore_(rows, P, ws - 7 * 864e5, ws).study; LW.forEach((b, i)=>{ out.lastRank[b.id] = {rank:i + 1, of:LW.length, score:b.score}; }); }
  /* 📅 개근 — 오늘의 30 끝까지 푼 날이 이어진 수 */
  const dd = {}, nm = {};
  rows.forEach(r=>{ if (String(r[C.diff]) !== "study" || P.hide(r)) return; const rule = String(r[C.rule] || ""); if (!/^study/.test(rule) || /^study-(battle|raid)/.test(rule) || Number(r[C.clear]) !== 1) return;
    const t = time_(r[C.date]); if (!t || t < now - 60 * 864e5) return; const id = P.id(r), nk = plain_(r[C.nick]); if (!nk || id === "PLAYER" || /^한양|패드$/.test(nk)) return;
    (dd[id] = dd[id] || {})[ymdK_(t)] = 1; if (!nm[id] || t >= nm[id].t) nm[id] = {t, nick:nk, tag:P.tag(r)}; });
  out.attOf = {}; const att = [];
  Object.keys(dd).forEach(id=>{ let d = dd[id][ymdK_(now)] ? today0 : today0 - 864e5, n = 0; while (dd[id][ymdK_(d)]){ n++; d -= 864e5; } out.attOf[id] = n; if (n >= 2) att.push({nick:nm[id].nick, tag:nm[id].tag, n, today:dd[id][ymdK_(now)] ? 1 : 0}); });
  out.att = att.sort((a, b)=>b.n - a.n).slice(0, 12);
  return out;
}

/* (v221) 단어 수집 랭킹 — 닉네임마다 '도감' 칸의 가장 큰 값 (모든 방식·난이도·공부 기록 포함)
   이번 주 = 이번 주에 기록이 있는 사람만 (값은 그때까지 모은 전체 단어 수) */
/* (v416) 사용자 QA 「분신술」 — 같은 아이가 「김지후」(달리기)·「👤김지후」(공부)로 두 줄 · 공용 패드에서 한 판 하면 그 패드 단어 수(1·6·17)로 또 한 줄
   → 사람마다 한 줄(태그 → 👤 뗀 이름) · 이번 주 = 이번 주에 기록이 있는 아이, 값 = 지금까지 자기 기기에서 모은 가장 큰 단어 수 (공용 패드의 단어 수는 그 아이 것이 아니라 안 셈) */
function dexRank_(sh, last, since, n, dev){
  const rows = sh.getRange(2, 1, last - 1, COLS.length).getValues();
  const best = {}, P = people_(rows), on = {};
  rows.forEach(r=>{ if (!P.hide(r) && time_(r[C.date]) >= since) on[P.id(r)] = 1; });
  rows.forEach(r=>{
    if (P.hide(r)) return;
    const t = time_(r[C.date]), id = P.id(r); if (!on[id]) return;
    const nick = plain_(r[C.nick]) || "PLAYER", dex = (P.sharedDev(r) && !String(r[C.own] || "")) ? 0 : (Number(r[C.dex]) || 0), tg = P.tag(r);   // (v417) 주인 패드 줄은 셈
    let b = best[id]; if (!b){ b = best[id] = {nick, tag:tg, score:0, title:"", tt:0, nt:0, me:false}; }
    if (t >= b.nt){ b.nick = nick; b.nt = t; }
    if (tg && !b.tag) b.tag = tg;
    if (dex > b.score) b.score = dex;
    if (r[C.char] && t >= (b.ct || 0)){ b.ch = String(r[C.char]); b.ct = t; }   // (v618) 랭킹 얼굴
    if (r[C.title] && t >= b.tt){ b.title = String(r[C.title]); b.tt = t; }
    if (dev && String(r[C.dev]) === dev) b.me = true;
  });
  return Object.keys(best).map(k=>best[k]).filter(b=>b.score>0)
    .sort((a,b)=>b.score - a.score).slice(0, n)
    .map(b=>({nick:b.nick, tag:b.tag, ch:b.ch || "", score:b.score, stage:0, title:b.title, me:b.me}));
}

/* (v416) 랭킹에서 「한 사람」 찾기
   · plain_ = 이름 앞 👤 떼기 (명단에서 고른 이름은 👤 를 붙여 적음)
   · id = 태그(#1234) → 없으면 그 이름에 붙은 태그(이름 하나에 태그가 하나일 때만) → 없으면 👤 뗀 이름(대문자)
   · sharedDev = 그 기기가 공용 패드인가: 달리기 기록에 👤 이름이 있음(공용 패드에서만 그렇게 적힘) 또는 👤 이름이 두 아이 이상
   · hide = 선생님(#0000 · HIDE_NICKS) — 아이 랭킹에서 뺌 */
const HIDE_NICKS = ["영어선생님"];
function plain_(n){ return String(n === undefined || n === null ? "" : n).replace(/^(👤\s*)+/, "").trim(); }
function people_(rows){
  const nameTag = {}, devP = {}, devPad = {};
  rows.forEach(r=>{ const p = plain_(r[C.nick]).toUpperCase(), tg = tag_(r[C.tag]); if (!p || !tg || tg === "0000") return;
    if (!nameTag[p]) nameTag[p] = tg; else if (nameTag[p] !== tg) nameTag[p] = "x"; });   // 같은 이름에 태그가 둘 = 다른 아이 → 이름으로 안 묶음
  const tagOf = r=>{ const tg = tag_(r[C.tag]); if (tg) return tg; const t = nameTag[plain_(r[C.nick]).toUpperCase()]; return t && t !== "x" ? t : ""; };
  const idOf = r=>{ const tg = tagOf(r); return tg ? "#" + tg : (plain_(r[C.nick]).toUpperCase() || "PLAYER"); };
  rows.forEach(r=>{ const d = String(r[C.dev] || ""), nk = String(r[C.nick] || ""); if (!d || nk.indexOf("👤") !== 0) return;
    if (String(r[C.diff]) !== "study") devPad[d] = 1;                 // 달리기 줄에 👤 = 공용 패드 (내 기기 달리기는 기기 이름 그대로)
    (devP[d] = devP[d] || {})[idOf(r)] = 1; });
  return {
    id: idOf, tag: tagOf,
    hide(r){ return tag_(r[C.tag]) === "0000" || HIDE_NICKS.indexOf(plain_(r[C.nick])) >= 0; },
    sharedDev(r){ const d = String(r[C.dev] || ""); return !!d && (!!devPad[d] || Object.keys(devP[d] || {}).length > 1); }
  };
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
function actsFor_(nick, dev, tg){
  const sh = actSheet_(), last = sh.getLastRow(); if (last < 2) return [];
  const rows = sh.getRange(2, 1, last - 1, ACT_COLS.length).getValues(), out = [];
  const N = nick.trim().toUpperCase();
  rows.forEach((r, i)=>{
    const who = String(r[1] || "").trim(), kind = String(r[2] || "").trim();
    if (!who || ACT_KINDS.indexOf(kind) < 0) return;
    const W = who.toUpperCase();
    if (!(W === "모두" || (N && W === N) || (dev && who === dev) || (tg && tag_(who) === tg && /^#/.test(who)))) return;
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
    if (sh.getRange(1, NAME_COLS.length).getValue() === "") sh.getRange(1, 1, 1, NAME_COLS.length).setValues([NAME_COLS.map(c=>c[1])]);   // (v404) 태그 칸 머리
    sh.appendRow(NAME_COLS.map(([k])=> k === "date" ? new Date() : k === "tag" ? (tag_(d.tag) ? "#" + tag_(d.tag) : "") : txt_(d[k], 30)));
    sh.getRange(sh.getLastRow(), 1).setNumberFormat("yyyy-mm-dd hh:mm");
  } catch(err){ return json_({ok:false, err:"busy"}); }
  finally { try { lock.releaseLock(); } catch(_){} }
  return json_({ok:true});
}

/* ── (v404) 🏷 태그 ── */
function tag_(v){ const s = String(v === undefined || v === null ? "" : v).replace(/^#/, "").trim(); return /^\d{1,4}$/.test(s) ? ("0000" + s).slice(-4) : ""; }
function tagSheet_(){
  const ss = SpreadsheetApp.openById(SHEET_ID);
  let sh = ss.getSheetByName(TAG_SHEET);
  if (!sh){ sh = ss.insertSheet(TAG_SHEET); sh.setFrozenRows(1); }
  if (sh.getRange(1, 1).getValue() === ""){
    sh.getRange(1, 1, 1, TAG_COLS.length).setValues([TAG_COLS.map(c=>c[1])]).setFontWeight("bold");
    sh.getRange("A:A").setNumberFormat("@");
    const seed = [[TAG_ME, "", "", "", "", "", "나 (선생님) — 관리 화면 「이 기기 = #0000」"]].concat(TAG_PADS.map((t, i)=>[t, "", "", "", "", "", "공용 패드 " + (i + 1)]));
    sh.getRange(2, 1, seed.length, TAG_COLS.length - 1).setValues(seed);
    rlvRule_(sh);
  }
  if (sh.getRange(1, 8).getValue() === ""){   // (v631) 예전 시트 = 「랭킹 단계」 칸을 뒤에 붙임 + 고르기 목록
    sh.getRange(1, 8).setValue("랭킹 단계").setFontWeight("bold");
    rlvRule_(sh);
  }
  return sh;
}
function rlvRule_(sh){ try { sh.getRange("H2:H").setDataValidation(SpreadsheetApp.newDataValidation().requireValueInList(RLV_LIST, true).setAllowInvalid(true).setHelpText("정한 단계보다 쉬운 책으로 한 공부·달리기는 랭킹에 안 들어가요 (높은 단계는 들어감) · 빈칸·자동 = 최근 4주에 가장 많이 푼 학년 · 빼기 = 랭킹에 안 나옴").build()); } catch(e){} }
/* (v631) 🏆 랭킹 단계 — 사용자: 「애들이 위로 등급이 올라가는 건 좋아도 아래 걸 하는 걸 방지」
   「태그」 탭 H칸 = 자동(빈칸) · 유치원 · G1-2 · G3-4 · G5-6 · 중등 · 빼기 → { "#0012": 2, "#0013": "x" } */
const RLV_LIST = ["자동", "유치원", "G1-2", "G3-4", "G5-6", "중등", "빼기"];
function rlvOf_(v){ const s = String(v || "").trim(); if (!s || s === "자동") return null; if (/^빼|^제외|^x$/i.test(s)) return "x"; const i = LV_NM.indexOf(s); if (i >= 0) return i; const j = LV_S_(s); return j >= 0 ? j : null; }
let RLV_ = null;
function rankLv_(){ if (RLV_) return RLV_; RLV_ = {}; try { tagRows_(tagSheet_()).forEach(r=>{ const tg = tag_(r[0]), v = rlvOf_(r[7]); if (tg && v !== null) RLV_["#" + tg] = v; }); } catch(e){} return RLV_; }
function tagLv_(d){
  const lv = String(d.lv || "").trim(); if (RLV_LIST.indexOf(lv) < 0) return json_({ok:false, err:"lv"});
  const want = (Array.isArray(d.tags) ? d.tags : [d.tag]).map(tag_).filter(t=>t && t !== "0000"); if (!want.length) return json_({ok:false, err:"tag"});
  const lock = LockService.getScriptLock();
  try {
    lock.waitLock(10000);
    const sh = tagSheet_(), rows = tagRows_(sh); let n = 0;
    rows.forEach((r, i)=>{ if (want.indexOf(tag_(r[0])) >= 0){ sh.getRange(i + 2, 8).setValue(lv === "자동" ? "" : lv); n++; } });
    try { CacheService.getScriptCache().removeAll(["board_v4", "lg2_" + weekStart_()]); } catch(e){}   // 랭킹에 바로 · (v635) 나의 리그 지난 주들도 다시
    RLV_ = null;
    return json_({ok:n > 0, n, err:n ? "" : "none"});
  } catch(err){ return json_({ok:false, err:"busy"}); }
  finally { try { lock.releaseLock(); } catch(_){} }
}
/* 아이마다 지금 자동 단계(최근 4주 오늘의 30 에서 가장 많이 푼 학년) — 관리 화면에 「자동(G3-4)」로 */
function autoLv_(){ const out = {}; try { const sh = sheet_(), last = sh.getLastRow(); if (last < 2) return out; const rows = sh.getRange(2, 1, last - 1, COLS.length).getValues(), P = people_(rows), cut = Date.now() - 28 * 864e5, LC = {};
    rows.forEach(r=>{ const t = time_(r[C.date]); if (!t || t < cut || String(r[C.diff] || "") !== "study") return; const lv = LV_S_(String(r[C.set] || "")); if (lv < 0) return; const id = P.id(r); (LC[id] = LC[id] || [0,0,0,0,0])[lv]++; });
    Object.keys(LC).forEach(id=>{ let b = -1, n = 0; LC[id].forEach((c, l)=>{ if (c > 0 && c >= n){ n = c; b = l; } }); if (b >= 0) out[id] = LV_NM[b]; }); } catch(e){} return out; }
/* (v404b) 기기 칸에 여러 기기 (쉼표·띄어쓰기로) — 한 아이가 기기 여러 대 · 선생님 기기 2대도 #0000 하나 */
function devs_(v){ return String(v || "").split(/[\s,]+/).map(x=>x.trim()).filter(x=>x); }
function tagRows_(sh){ const last = sh.getLastRow(); return last < 2 ? [] : sh.getRange(2, 1, last - 1, TAG_COLS.length).getValues(); }
/* 이 기기 태그 — 있으면 그대로(지금 이름·마지막 날만 고침) · 없으면: 공용 패드 = 0001~0005 중 빈 것 · 아이 = 지금 가장 큰 번호 + 1 (0006 부터) · 이름이 없으면 안 줌 */
function tagFor_(d){
  const dev = txt_(d.dev, 30), nick = txt_(d.nick, 20);
  if (!dev) return json_({ok:false, err:"dev"});
  const lock = LockService.getScriptLock();
  try {
    lock.waitLock(10000);
    const sh = tagSheet_(), rows = tagRows_(sh), now = new Date();
    for (let i = 0; i < rows.length; i++){
      if (devs_(rows[i][1]).indexOf(dev) < 0) continue;
      const tg = tag_(rows[i][0]);
      if (nick && String(rows[i][3]) !== nick) sh.getRange(i + 2, 4).setValue(nick);
      sh.getRange(i + 2, 6).setValue(now).setNumberFormat("yyyy-mm-dd hh:mm");
      return json_({ok:true, tag:tg, v:SERVER_V});
    }
    if (!nick || /^PLAYER$/i.test(nick)) return json_({ok:false, err:"noname"});   // 이름을 정해야 태그가 생김
    let row = -1, tg = "";
    if (d.pad){ for (let i = 0; i < rows.length; i++){ const t = tag_(rows[i][0]); if (TAG_PADS.indexOf(t) >= 0 && !devs_(rows[i][1]).length){ row = i + 2; tg = t; break; } }
      if (row < 0) return json_({ok:false, err:"nopad"}); }
    else { let mx = TAG_FIRST_KID - 1; rows.forEach(r=>{ const t = Number(tag_(r[0])); if (t > mx) mx = t; }); if (mx >= 9999) return json_({ok:false, err:"full"});
      tg = ("0000" + (mx + 1)).slice(-4); row = sh.getLastRow() + 1; sh.getRange(row, 1).setNumberFormat("@").setValue(tg); }
    sh.getRange(row, 2, 1, 5).setValues([[dev, nick, nick, now, now]]); sh.getRange(row, 5, 1, 2).setNumberFormat("yyyy-mm-dd hh:mm");
    return json_({ok:true, tag:tg, v:SERVER_V, made:true});
  } catch(err){ return json_({ok:false, err:"busy"}); }
  finally { try { lock.releaseLock(); } catch(_){} }
}
/* 선생님: 이 기기를 그 태그에 더함 (#0000 = 나 · 아이가 새 기기를 쓰면 그 아이 태그에) — 그 기기는 다른 태그 줄에서 빠짐 · 원래 기기들은 그대로 */
function tagSet_(tg, dev, d){
  if (!tg) return json_({ok:false, err:"tag"}); if (!dev) return json_({ok:false, err:"dev"});
  const lock = LockService.getScriptLock();
  try {
    lock.waitLock(10000);
    const sh = tagSheet_(), rows = tagRows_(sh); let hit = -1;
    rows.forEach((r, i)=>{ const t = tag_(r[0]), L = devs_(r[1]); if (t === tg) hit = i; else if (L.indexOf(dev) >= 0) sh.getRange(i + 2, 2).setValue(L.filter(x=>x !== dev).join(", ")); });
    if (hit < 0) return json_({ok:false, err:"none"});
    const L = devs_(rows[hit][1]); if (L.indexOf(dev) < 0) L.push(dev); hit += 2;
    sh.getRange(hit, 2).setValue(L.join(", ")); if (d && d.nick) sh.getRange(hit, 4).setValue(txt_(d.nick, 20));
    sh.getRange(hit, 6).setValue(new Date()).setNumberFormat("yyyy-mm-dd hh:mm");
    return json_({ok:true, tag:tg});
  } catch(err){ return json_({ok:false, err:"busy"}); }
  finally { try { lock.releaseLock(); } catch(_){} }
}
function tagList_(auto){ const A = auto ? autoLv_() : {}; return tagRows_(tagSheet_()).map(r=>({tag:tag_(r[0]), dev:devs_(r[1]).join(", "), first:String(r[2] || ""), nick:String(r[3] || ""), at:time_(r[5]), memo:String(r[6] || ""), rlv:String(r[7] || ""), auto:A["#" + tag_(r[0])] || ""})).filter(x=>x.tag); }

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
/* (v419) 🔐 선생님 기기 등록 — 열쇠(ADMIN_KEY)가 맞으면 Firebase /hy/teachers/<uid> 에 적음
   스크립트 속성 FB_SECRET = Firebase 콘솔 → 프로젝트 설정 → 서비스 계정 → 데이터베이스 비밀번호(Database secrets) · FB_DB = 데이터베이스 주소(없으면 아시아) */
function fbTeacher_(d){
  const P = PropertiesService.getScriptProperties(), sec = P.getProperty("FB_SECRET"), db = P.getProperty("FB_DB") || "https://hy-eng-raid-default-rtdb.asia-southeast1.firebasedatabase.app";
  const uid = String(d.uid || ""); if (!/^[A-Za-z0-9]{10,40}$/.test(uid)) return json_({ok:false, err:"uid"});
  if (!sec) return json_({ok:false, err:"FB_SECRET 없음"});
  const r = UrlFetchApp.fetch(db + "/hy/teachers/" + uid + ".json?auth=" + encodeURIComponent(sec), {method:"put", contentType:"application/json", payload:JSON.stringify({at:Date.now(), n:txt_(d.nick, 20)}), muteHttpExceptions:true});
  return json_({ok:r.getResponseCode() === 200, err:r.getResponseCode() === 200 ? "" : "firebase " + r.getResponseCode()});
}
/* 선생님 관리 화면 — 스크립트 속성 ADMIN_KEY 와 같은 열쇠만 */
function teacher_(d){
  const want = PropertiesService.getScriptProperties().getProperty("ADMIN_KEY");
  if (!want) return json_({ok:false, err:"nokey"});
  if (String(d.tk || "") !== want) return json_({ok:false, err:"badkey"});
  if (d.type === "check") return json_({ok:true, v:SERVER_V});
  if (d.type === "report") return json_({ok:true, v:SERVER_V, at:Date.now(), rep:report_()});   // (v306) 우리 반 — 시트 요약 탭을 보이는 그대로
  if (d.type === "tags") return json_({ok:true, v:SERVER_V, list:tagList_(true)});
  if (d.type === "tagLv") return tagLv_(d);                                                         // (v631) 🏆 랭킹 단계 바꾸기                                 // (v404) 🏷 태그 목록
  if (d.type === "tagMe" || d.type === "tagSet") return tagSet_(d.type === "tagMe" ? TAG_ME : tag_(d.tag), String(d.dev || ""), d);
  if (d.type === "fbTeacher") return fbTeacher_(d);                                                // (v419) 🔐 Firebase 선생님 기기
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
/* (v650 · 서버 v19) 🧠 며칠 뒤에도 기억하나 — 최근 14일 · 아이마다(태그 → 이름) 며칠 뒤 첫 번 맞힘/푼 수 · 그때 틀린 단어 · 🎤 말한 단어
   words = 반이 안 붙는 단어 [단어, 아이 수, 횟수] (아이 수 많은 순) */
function learn_(){
  const sh = sheet_(), last = sh.getLastRow(); if (last < 2) return {days:14, kids:[], words:[]};
  const n = Math.min(last - 1, 6000), rows = sh.getRange(last - n + 1, 1, n, COLS.length).getValues(), cut = Date.now() - 14 * 864e5, K = {}, W = {}, GU = {};
  rows.forEach(r=>{ const t = time_(r[C.date]); if (!t || t < cut) return;
    const tot = Number(r[C.rvn]) || 0, ok = Number(r[C.rvo]) || 0, sp = Number(r[C.sp]) || 0, ws = String(r[C.rvw] || "").split(",").map(x=>x.trim().toLowerCase()).filter(x=>x);
    /* (v653) 📒 문법 판(방식 study-grammar): 단어장 칸 「중등 문법 · 현재완료 ★4」 → 단원마다 맞힘/푼 수 */
    const gm = String(r[C.rule]) === "study-grammar" ? String(r[C.set] || "").replace(/\s*★\d+\s*$/, "").trim() : "", gr = gm ? (Number(r[C.right]) || 0) : 0, gt = gm ? gr + (Number(r[C.wrong]) || 0) : 0;
    if (!tot && !sp && !ws.length && !gt) return;
    const tg = String(r[C.tag] || "").trim(), nm = plain_(r[C.nick]), id = tg || nm; if (!id) return;
    const k = K[id] || (K[id] = {n:nm, ok:0, tot:0, sp:0, w:{}, g:{}}); k.n = nm;
    if (gt){ const a = k.g[gm] || (k.g[gm] = [0, 0]); a[0] += gr; a[1] += gt; const u = GU[gm] || (GU[gm] = {k:{}, n:0, r:0, t:0}); u.k[id] = 1; u.n++; u.r += gr; u.t += gt; } k.ok += Math.min(ok, tot); k.tot += tot; k.sp += sp;
    ws.forEach(w=>{ k.w[w] = (k.w[w] || 0) + 1; const x = W[w] || (W[w] = {k:{}, n:0}); x.k[id] = 1; x.n++; }); });
  const kids = Object.keys(K).map(id=>{ const k = K[id]; const gw = Object.keys(k.g).filter(u=>k.g[u][1] >= 5).sort((a, b)=>k.g[a][0] / k.g[a][1] - k.g[b][0] / k.g[b][1])[0];
      return {n:k.n, ok:k.ok, tot:k.tot, sp:k.sp, w:Object.keys(k.w).sort((a, b)=>k.w[b] - k.w[a]).slice(0, 5).map(w=>[w, k.w[w]]), g:gw ? [gw, Math.round(k.g[gw][0] / k.g[gw][1] * 100)] : null}; })
    .sort((a, b)=>(a.tot ? a.ok / a.tot : 2) - (b.tot ? b.ok / b.tot : 2));
  const words = Object.keys(W).map(w=>[w, Object.keys(W[w].k).length, W[w].n]).sort((a, b)=>b[1] - a[1] || b[2] - a[2]).slice(0, 12);
  const gram = Object.keys(GU).map(u=>[u, Object.keys(GU[u].k).length, GU[u].n, GU[u].t ? Math.round(GU[u].r / GU[u].t * 100) : 0]).sort((a, b)=>a[3] - b[3]).slice(0, 30);   // [단원, 아이 수, 판 수, 정답률%] 낮은 것부터
  return {days:14, kids:kids, words:words, gram:gram};
}
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
    nicks: g("기기별 이름", "B5:B300").map(r=>String(r[0]).trim()).filter(n=>n && !/^PLAYER$/i.test(n)),   // (v308) 보내기 받는 아이 = 게임 이름(닉네임)
    tags:  tagList_().filter(x=>x.dev).map(x=>[x.tag, x.nick, x.first]),   // (v404) 🏷 태그 · 지금 이름 · 처음 이름
    learn: (function(){ try { return learn_(); } catch(err){ return null; } })(),   // (v650) 🧠 며칠 뒤에도 기억하나
    town:  g(TOWN_SHEET, "A1:K300")   // (v563) 🏝 마을 현황 — 머리 줄(아이·태그·마지막·보석·모은 보석·코인·미끼·은행 코인·은행 보석·강화·버전) + 아이마다 한 줄
  };
}
