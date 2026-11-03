# 문장 성분 · 문장 형식 표시 (한국 중학교 영문법 기준)

입력 파일의 줄마다 `{"i": 번호, "s": "영어 문장"}` 이 있다. 줄마다 아래 형식의 JSON 한 줄을 출력 파일에 쓴다 (입력 순서 그대로, 빠짐없이).

```
{"i": 번호, "f": 형식, "t": "시제", "r": [["S","주어 부분"],["V","동사 부분"],["O","목적어 부분"]]}
```

- `r` = 문장 성분 조각들. 각 조각의 글자는 **문장에 있는 그대로 (대소문자·구두점 포함) 잘라 낸 연속된 부분**이어야 하고, 문장에 나오는 **순서대로** 적는다. 수식어(부사, 전치사구, 부사절, 시간·장소 표현)는 넣지 않는다.
- 역할: `S` 주어 · `V` 동사(서술어) · `O` 목적어 · `IO` 간접목적어(~에게) · `DO` 직접목적어(~을) · `C` 주격 보어 · `OC` 목적격 보어
- `f` = 1~5 (주절 기준). 확실하지 않거나 아래 「빼기」에 해당하면 `"f": 0, "r": []` 로 쓴다.
- `t` = 주절 동사의 시제: `현재` · `과거` · `미래` · `현재진행` · `과거진행` · `현재완료` · `조동사` (can·could·must·should·may·might·would 가 붙으면 `조동사`). f 가 0 이어도 t 는 쓴다 (모르면 "").

## 조각 자르는 법
- S: 주어 명사구 전체 (관사·형용사·소유격·뒤에 붙은 전치사구 수식까지): "My little brother", "The boy in the red hat"
- V: 조동사·be·have·not·부정 축약까지 포함한 동사 덩어리, 구동사의 부사 짝도 포함: "will give", "doesn't like", "has finished", "was running", "turned off", "looked after". 동사가 떨어져 있으면 (조동사 … 동사 사이에 부사) 부사까지 포함해 한 조각으로: "can always find"
- O/DO/C/OC: 그 성분의 구 전체 (뒤 수식어 포함): "a special talk", "to play soccer", "that the earth is round", "reading books"
- 전치사구·부사·시간 표현은 빼고 그 앞에서 끊는다: "A baby lamb stood next to its mother in the field." → S "A baby lamb", V "stood" → 1형식

## 형식 판단
- 1형식 S+V (+수식어): "Birds fly.", "He lives in Seoul.", "There is a cat on the sofa." (There 구문 = 1형식, S = "a cat", V = "is"), be + 장소 = 1형식 ("The book is on the desk.")
- 2형식 S+V+C: be·become·get·turn·look·feel·sound·smell·taste·seem·stay·keep·remain + 명사/형용사 ("She is a doctor.", "The soup tastes salty.", "It got dark.")
- 3형식 S+V+O: 목적어 하나 (명사·to부정사·동명사·that절·의문사절): "I want to go home.", "She enjoys reading.", "I think that he is right."
- 4형식 S+V+IO+DO: give·send·show·tell·teach·buy·make·bring·lend·ask + 사람 + 사물 ("He gave me a book." → IO "me", DO "a book"). "give a book to me" 처럼 to/for 가 붙으면 3형식 (to me 는 수식어)
- 5형식 S+V+O+OC: make·keep·find·call·name·leave + O + 명사/형용사 ("The news made us happy."), want·ask·tell·allow·expect·encourage + O + to V ("Mom told me to clean my room."), let·make·have·help + O + 동사원형, see·hear·watch·feel + O + 동사원형/-ing
- 명령문 (주어 없음): S 없이 V·O… 만 적고 형식은 동사 모양대로 ("Close the door." → V "Close", O "the door", f 3)
- 부사절(when/because/if/before/after/while…)·분사구문은 수식어 → 주절만 분석. 부사절이 앞에 와도 주절만.

## 빼기 (f 0)
- 수동태 (be + p.p. 로 「~되다·당하다」): "The window was broken by Tom."
- 의문문, 감탄문 (What a …!), 동사가 없는 조각 ("Dear Sir or Madam")
- and/but/or/so 로 이어진 주절이 두 개 이상인 문장 ("I like dogs, but she likes cats.")
- 「It ~ to/that」 가주어 구문, 강조 구문, 도치
- 확실하지 않은 것

## 예
{"i":1,"f":3,"t":"미래","r":[["S","A Nobel laureate"],["V","will give"],["O","a special talk"]]}
{"i":2,"f":1,"t":"현재","r":[["S","A baby kangaroo"],["V","stays"]]}
{"i":3,"f":4,"t":"과거","r":[["S","Grandma"],["V","bought"],["IO","me"],["DO","a red scarf"]]}
{"i":4,"f":5,"t":"과거","r":[["S","The movie"],["V","made"],["O","everyone"],["OC","sad"]]}
{"i":5,"f":2,"t":"현재","r":[["S","This soup"],["V","tastes"],["C","too salty"]]}
{"i":6,"f":0,"t":"과거","r":[]}
