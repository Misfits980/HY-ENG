# G5-6 Basic Step 1~15 (노션 DAY 01~15) 옮긴 자료
dayNN.txt 한 줄씩:
- W|영어|대표 뜻|다른 뜻|대표 품사|추가 품사|예문1|해석1|예문2(과거 중심)|해석2
- T|영어|A|B|해석(A / B)
build.py → COURSE(게임 코드는 손으로) · data/bex.json(교재 예문) · tools/talk/g56.txt 대화 추가
화면에는 교재 이름을 쓰지 않는다 (Stage 번호만).
- T 줄의 A 가 '@1'/'@2' 면 그 단어 예문1/예문2 와 같은 문장 (노션에서 대화 A = 예문인 DAY)

## (v278) 노션 v6 (챗지피티 최종 프롬프트, claude/hy-eng-voca-prompt-final.md) 가져오기
1. 노션 DAY 페이지를 글로 옮겨 `tools/basic/v6/DAYnn.md` 로 저장 (Claude 가 노션에서 읽어 저장)
2. `python3 tools/basic/v6.py check tools/basic/v6/DAY*.md --level L3` — ❌ 꼭 고칠 것 · ⚠️ 확인할 것 · 과거/전치사 비율
3. ❌ 가 0 이면 `python3 tools/basic/v6.py apply …` → data/bex.json(P 품사별 뜻 · x 예문+뜻 번호 · f · c · g 어려운 말), data/dex<권>.json(D[10] 품사별 뜻 …), tools/talk/v6.txt(상황) → talk.json
4. 시험용 예시: tools/basic/v6sample/DAY99.md (permit · coil) — 실제 자료에 apply 하지 말 것

## (v442) 중등 [표 3] · 📖 짧은 글 (노션 Junior DAY 36~70, claude/hy-eng-voca-prompt-addon.md v2.1)
1. 노션 DAY 페이지의 [표 3] · [짧은 글 1] · [짧은 글 2] 를 글 그대로 `tools/basic/v6/junior/x/DAYnn.md` 로 저장 (변하는 모양은 `tools/basic/v6/junior/DAYnn.md` [표 1] 에서 읽음)
2. `python3 tools/basic/xtra.py check` — 경고 확인 → `python3 tools/basic/xtra.py apply` → `data/xtra.json`
   - w[en] = {d 영어 풀이 · hint 영어 힌트 · fam 짝 단어 · idm 숙어(pre/post) · fs/form/fpre/fpost/fopt 모양 바꿔 쓰기}
   - st[DAY] = [{t 제목 · ws 단어 · s 문장 6 [영,한] · ox [[영,한,참거짓]]×2 · tc 제목 고르기 · sm 요약(첫째가 답) · q 생각 질문 · ex 예시 답}]
3. 게임: mv1 Stage 의 `pn` = DAY 번호 → `Study.storyFor` 가 그 DAY 짧은 글 중 안 읽은 것
- 노션 Junior DAY 01~35 (QA 가 새로 만든 페이지) 는 아직 게임에 없음
