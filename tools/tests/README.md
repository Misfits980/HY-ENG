# HY ENG 자동 테스트

배포 전에 꼭 한 번:

```
python3 tools/tests/run_all.py          # 빠른 검사 25개 + 기본 검사 (약 3~5분)
python3 tools/tests/run_all.py --slow   # + 전 세트 전 스테이지 자동 풀이(sweep1) · 달리기 289조합(runsweep) — 30분 넘게
python3 tools/tests/run_all.py olytest  # 하나만
```

- 필요: Python 3 + Playwright(Chromium), node.
- 저장소 파일을 그대로 `https://misfits980.github.io/HY-ENG/` 주소처럼 연다. 사이트를 따로 복사할 필요가 없다.
- 바깥 주소(CDN·구글 시트)는 막는다. `three.min.js` 는 `fake_three.js`(그림 없이 로직만 도는 가짜 3D 엔진)로 바꿔 준다.
- 통과 기준
  - 종료 코드 0, Traceback 없음
  - 'errs [...]'·BAD·Error: 줄 없음. 바깥 주소를 막아서 생긴 'Failed to load'는 정상으로 본다.
- 기본 검사
  - index.html 스크립트 문법
  - GAME_VER 와 sw.js VERSION 일치
  - data/*.json 읽기
  - 대화 단문 (tools/talk/check.py)
- 출력·스크린샷은 `tools/tests/out/` (git 에 안 올림).
- 공용 코드는 `harness.py`: route, boot(page), SOLVE(Daily 30 문제 자동 풀이), real_errs.

| 테스트 | 보는 것 |
|---|---|
| study3 · study4 | Daily 30 한 판·복습·적응 |
| v243test · v246test · v249test | 파닉스 월드 · 유치원 7탭 · 초등 나눈 Stage·과거형·이어 하기 |
| uitest · screens · fixedscan · poptest · foottest | 메뉴·화면 9개 모바일/PC · position:fixed |
| scrolltest2 · bottomtap · shx | 길 화면 시작 창·돌아오기 · 창 ✕ |
| newstest · swreload | 소식지 · 업데이트 새로고침 미루기 |
| homotest | 소리가 같은 단어·같은 그림 |
| dexgr · bingotest · bingo2 · albumtest2 | 도감 학년 탭·빙고·앨범 보상 |
| v256test · mv1run | 교재 단계 옮기기·중등 voca 1·기록 옮기기 |
| olytest · olyfail · talkshot | 🚩 마지막 시험·시간 초과·대화 빈칸·도감 대화 탭 |
| sweep1 · runsweep (--slow) | 전 세트 전 스테이지 · 달리기 세트×난이도×룰 |
