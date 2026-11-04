# KayKit 모델 묶음 (CC0 · Kay Lousberg, www.kaylousberg.com)
- 원본: github.com/KayKit-Game-Assets — kaykit-medieval-hexagon-pack-1.0 · kaykit-furniture-bits-1.0 (CC0, 출처 표기 의무 없음 — 고마워서 적어 둠)
- 만들기: `python3 tools/kk/pack.py <묶음> <텍스처.png> <gltf...>` → assets/town/kk/<묶음>.json·.bin·.webp
- nature: 만든 뒤 텍스처의 연두(풀 윗면, H 56~82°)를 My Town 잔디 초록(H 104°, 채도 ≤0.56)으로 바꿔 다시 저장 (v434 대화 기록)
- 읽기: tools/kk/kk.js 와 같은 코드가 proto/house.html 안에 있음 (KK.load)
- 미리 보기: tools/kk/preview.html#nature (테스트 서버로 열기)
- (v521) isle: KayKit Medieval Hexagon Pack 1.0 (github.com/KayKit-Game-Assets/KayKit-Medieval-Hexagon-Pack-1.0, CC0) — 🏝 우리 마을 섬 (육각 땅·집·시장·교회=학교·탑·광산·풍차·나무). 만든 뒤 nature 와 같은 방법으로 연두 → 초록 (H 56~82° → 104°, 채도 ≤0.56)
- (v591 뒤 · 2026-11-04) 사용자가 받아 준 Kenney 모음(CC0) — 아직 게임 코드에선 안 씀:
  - 묶어 둠(colormap 텍스처): suburb(City Kit Suburban 2.0 · 주택 40) · commerce(City Kit Commercial 2.1 · 41) · food(Food Kit · 198, 냄비·프라이팬 뚜껑 2개는 UV 범위 밖이라 뺌) · holiday(Holiday Kit · 99) · blaster(Blaster Kit 2.1 · 7, 물총 아레나에서 씀)
  - 원본만 둠(tools/kk/src/): furniture-kit(140) · nature-kit(329) — 텍스처 없이 재료 색이라 pack.py 에 「재료 색 → 작은 팔레트 텍스처」 굽기를 더해야 묶을 수 있음
