# HY Trace (따라쓰기 흐린 글씨 글꼴)

- 원본: Edu SA Beginner — AU School Handwriting Fonts Project (https://github.com/MezMerrit/AU-School-Handwriting-Fonts), SIL Open Font License 1.1 (`OFL-hy-trace.txt`).
- 바꾼 것 (v709): 굵기 600 으로 고정 · 5.5° 기운 글자를 똑바로 세움 · 라틴 기본 글자만 남김 · 이름 「HY Trace」.
- 쓰는 곳: 시험지·따라쓰기 종이의 흐린 글씨(`.kjT`)만. 4선(윗줄·점선·빨간 줄·아랫줄)에 맞는 비율 — 머리:몸통:꼬리 ≈ 0.85 : 1 : 0.85.
- 다시 만들기: `build.py <EduSABeginner[wght].ttf> hy-trace.ttf 5.5 600` (fontTools instancer → TransformPen 기울기 풀기 → subset).
