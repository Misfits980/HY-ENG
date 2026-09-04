# HY ENG — 단어 게이트 러너

3D 영어 단어 학습 게임. 브라우저만 있으면 설치 없이 실행됩니다.

## 깃허브에 올려서 링크로 배포하기

1. **저장소 만들기** — 깃허브에서 `New repository` → 이름 `hy-eng` → **Public** → Create
2. **파일 올리기** — 저장소 화면에서 `Add file` → `Upload files` → 이 폴더의 파일을 전부 드래그 → `Commit changes`
3. **Pages 켜기** — `Settings` → 왼쪽 `Pages` → Source를 `Deploy from a branch`, 브랜치 `main`, 폴더 `/ (root)` → `Save`
4. **1~2분 뒤 주소 확인** — `https://아이디.github.io/hy-eng/`

이 주소를 QR코드로 만들어 나눠주면 학생들이 바로 접속합니다.

## 수정하는 법

`index.html` 안의 `WORD_BANK` 배열을 고치면 단어가 바뀝니다.
깃허브에서 파일을 열고 연필 아이콘 → 수정 → `Commit changes` 하면 1분 안에 반영됩니다.

**중요**: 게임을 고쳤으면 `sw.js` 첫 줄의 `hyeng-v1`을 `hyeng-v2`처럼 올려주세요.
안 그러면 예전에 접속했던 기기에 옛 버전이 계속 보입니다.

## 오프라인으로도 돌리려면

`https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js` 를 브라우저에서 열고
`Ctrl+S`(맥은 `Cmd+S`)로 저장한 뒤, 파일 이름을 `three.min.js` 로 해서 이 폴더에 같이 올리세요.
게임이 자동으로 이 파일을 먼저 찾고, 없을 때만 인터넷에서 받아옵니다.

## 홈 화면에 앱처럼 설치하기

- **안드로이드 크롬**: 주소창 오른쪽 `⋮` → `앱 설치` 또는 `홈 화면에 추가`
- **아이폰 사파리**: 아래 공유 버튼 → `홈 화면에 추가`

설치하면 주소창 없이 전체화면으로 실행되고, 한 번 접속한 뒤에는 인터넷이 없어도 열립니다.

## 파일 설명

| 파일 | 역할 |
|---|---|
| `index.html` | 게임 본체 (단어 데이터 포함) |
| `manifest.webmanifest` | 앱 이름·아이콘·전체화면 설정 |
| `sw.js` | 오프라인 캐시 |
| `icon-*.png` | 홈 화면 아이콘 |
