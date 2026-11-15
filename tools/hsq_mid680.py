# v680 사용자: 「고등꺼는 중학교꺼로 살짝 수준 맞춰서」 — data/hsq.json 「어법 심화」 12가지의 어려운 문제(lv2 120 · lv3 48)를 중학교 내신 수준으로 다시 씀
#  · lv2: 8~12단어 · 함정은 하나(짧은 꾸밈말 · 감각동사 · 사역/지각 · 실제 조건 vs 가정법 같은 중학교 단골) · 과거완료·분사구문·긴 관계절 없음
#  · lv3: (A)(B) 둘 다 같은 주제 (중학교 「(A),(B)에 들어갈 말로 알맞게 짝지어진 것은?」) · 다른 주제를 섞지 않음
#  · 같은 자리(번호)에 바꿔 넣음 → hyeng_hsq_seen(본 문제 번호) 그대로
import json, os, re, sys
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "hsq.json")

def a(s, o, ko, why, r1, r2): return ("2", s, o, ko, why, {o[1]: r1, o[2]: r2})
def b(s, A, B, ko, why, wA, wB): return ("3", s, A, B, ko, why, wA, wB)

NEW = {
"part": [
 a("The last scene of the movie was really ___.", ["surprising", "surprised", "surprise"], "그 영화의 마지막 장면은 정말 놀라웠어요.", "마지막 장면이 놀라움을 '주는' 것 → -ing", "surprised 는 사람이 놀랄 때 써요", "was really 뒤엔 형용사 · surprise 는 동사·명사"),
 a("Jiho was ___ at the news about the test.", ["shocked", "shocking", "shock"], "지호는 시험 소식에 깜짝 놀랐어요.", "지호가 충격을 '느끼는' 것 → -ed", "shocking 은 충격을 '주는' 것에 써요", "was 뒤에 동사원형 shock 는 못 와요"),
 a("The long speech made the students very ___.", ["bored", "boring", "bore"], "긴 연설 때문에 학생들은 아주 지루해졌어요.", "학생들이 지루함을 '느끼는' 것 → -ed (make + 사람 + 형용사)", "boring 은 지루함을 '주는' 쪽 · 학생들은 -ed", "very 뒤엔 형용사 · bore 는 동사"),
 a("I found the book about dinosaurs very ___.", ["interesting", "interested", "interest"], "저는 공룡에 관한 그 책이 아주 재미있었어요.", "책이 재미를 '주는' 것 → -ing (find + 물건 + 형용사)", "interested 는 사람이 관심을 느낄 때 써요", "very 뒤엔 형용사 · interest 는 명사·동사"),
 a("Mina looked very ___ with her new bike.", ["pleased", "pleasing", "please"], "미나는 새 자전거가 아주 마음에 드는 것 같았어요.", "미나가 기쁨을 '느끼는' 것 + with → -ed", "pleasing 은 기쁨을 '주는' 것에 써요", "looked very 뒤엔 형용사가 와요"),
 a("Cleaning the whole classroom after school was very ___.", ["tiring", "tired", "tire"], "방과 후에 교실 전체를 청소하는 건 아주 힘들었어요.", "청소가 피곤함을 '주는' 것 → -ing", "tired 는 사람이 피곤할 때 써요", "was very 뒤엔 형용사 · tire 는 동사"),
 a("We were ___ to hear the good news.", ["excited", "exciting", "excite"], "우리는 좋은 소식을 듣고 신이 났어요.", "우리가 신남을 '느끼는' 것 → -ed", "exciting 은 신나게 '하는' 쪽 · 사람은 -ed", "were 뒤에 동사원형 excite 는 못 와요"),
 a("The rules of the new game were ___ to Tom.", ["confusing", "confused", "confuse"], "새 게임의 규칙은 톰에게 헷갈렸어요.", "주어는 rules · 규칙이 헷갈림을 '주는' 것 → -ing", "confused 는 사람이 헷갈릴 때 · 주어는 rules", "were 뒤에 동사원형 confuse 는 못 와요"),
 a("Amy felt ___ because she lost her favorite pen.", ["disappointed", "disappointing", "disappoint"], "에이미는 가장 좋아하는 펜을 잃어버려서 실망했어요.", "에이미가 실망을 '느끼는' 것 → -ed", "disappointing 은 실망을 '주는' 것에 써요", "felt 뒤엔 형용사 · disappoint 는 동사"),
 a("Watching the stars at night is always ___.", ["amazing", "amazed", "amaze"], "밤에 별을 보는 건 언제나 놀라워요.", "별 보기가 놀라움을 '주는' 것 → -ing", "amazed 는 사람이 놀랄 때 써요", "is always 뒤엔 형용사 · amaze 는 동사"),
 b("The magic show was (A)___, and all the children were (B)___.", ["amazing", "amazed"], ["excited", "exciting"], "마술 쇼는 놀라웠고 아이들은 모두 신이 났어요.", "(A) 쇼가 놀라움을 줌 → -ing · (B) 아이들이 느낌 → -ed", "amazed 는 사람이 느낄 때 · 쇼엔 -ing", "exciting 은 신나게 '하는' 쪽 · 아이들은 -ed"),
 b("Jiho was (A)___ because the math class was really (B)___.", ["bored", "boring"], ["boring", "bored"], "수학 수업이 정말 지루해서 지호는 따분했어요.", "(A) 지호가 느낌 → -ed · (B) 수업이 지루함을 줌 → -ing", "boring 은 지루함을 '주는' 쪽 · 지호는 -ed", "bored 는 사람이 느낄 때 · 수업엔 -ing"),
 b("The test was (A)___, so many students looked (B)___.", ["confusing", "confused"], ["confused", "confusing"], "시험이 헷갈려서 많은 학생이 당황한 얼굴이었어요.", "(A) 시험이 헷갈림을 줌 → -ing · (B) 학생들이 느낌 → -ed", "confused 는 사람이 헷갈릴 때 · 시험엔 -ing", "confusing 은 헷갈리게 '하는' 쪽 · 학생들은 -ed"),
 b("Amy was (A)___ with the gift, and the letter inside was (B)___.", ["pleased", "pleasing"], ["touching", "touched"], "에이미는 선물이 마음에 들었고, 안에 든 편지는 감동적이었어요.", "(A) 에이미가 기쁨을 느낌 → -ed · (B) 편지가 감동을 줌 → -ing", "pleasing 은 기쁨을 '주는' 쪽 · 에이미는 -ed", "touched 는 사람이 감동받을 때 · 편지엔 -ing"),
],
"voice": [
 a("The windows in our classroom ___ by Tom yesterday.", ["were cleaned", "cleaned", "are cleaned"], "우리 교실 창문은 어제 톰이 닦았어요.", "창문은 '닦이는' 것 + yesterday → were cleaned", "창문이 스스로 닦을 수 없어요 · 수동태로!", "yesterday 는 과거 → were cleaned"),
 a("This song ___ by many teenagers around the world.", ["is loved", "loves", "loved"], "이 노래는 전 세계 많은 십 대에게 사랑받아요.", "노래는 '사랑받는' 것 → is loved", "노래가 누군가를 사랑하는 게 아니에요 · 수동태", "be동사가 빠졌어요 · is loved"),
 a("The school festival will ___ in the gym next Friday.", ["be held", "hold", "held"], "학교 축제는 다음 주 금요일에 체육관에서 열려요.", "조동사 수동태: will be + 과거분사", "축제가 무언가를 여는 게 아니에요 · be held", "will 뒤엔 원형 · will be held"),
 a("Stars can ___ clearly from the top of this hill.", ["be seen", "see", "seen"], "이 언덕 꼭대기에서는 별이 또렷하게 보여요.", "별은 '보이는' 것 → can be seen", "별이 보는 게 아니라 보여요 · be seen", "can 뒤엔 원형 · can be seen"),
 a("Jiho ___ the window by mistake this morning.", ["broke", "was broken", "is broken"], "지호가 오늘 아침 실수로 창문을 깼어요.", "지호가 직접 '깬' 것 + 목적어 the window → 능동 broke", "지호가 깨진 게 아니라 깼어요 · 뒤에 목적어가 있어요", "this morning 은 과거 + 지호가 직접 깼어요"),
 a("This cake ___ by my dad for my birthday.", ["was made", "made", "makes"], "이 케이크는 아빠가 제 생일에 만들어 주셨어요.", "케이크는 '만들어지는' 것 + by → was made", "케이크가 만든 게 아니에요 · was made", "케이크가 만드는 게 아니에요 · 수동태로!"),
 a("Many people ___ this restaurant on weekends.", ["visit", "are visited", "visits"], "주말에는 많은 사람이 이 식당을 찾아요.", "사람들이 직접 '찾아가는' 것 + 목적어 → 능동 visit", "사람들이 방문'받는' 게 아니에요 · 능동", "주어 Many people 은 복수 → visit"),
 a("The first telephone ___ more than 100 years ago.", ["was invented", "invented", "invents"], "최초의 전화기는 100년도 더 전에 발명되었어요.", "전화기는 '발명되는' 것 + ago → was invented", "전화기가 발명한 게 아니에요 · was invented", "ago 는 과거 + 수동태로!"),
 a("My bike ___ in front of the library last night.", ["was stolen", "stole", "is stolen"], "어젯밤 도서관 앞에서 제 자전거를 도둑맞았어요.", "자전거는 '도둑맞는' 것 + last night → was stolen", "자전거가 훔친 게 아니에요 · 수동태", "last night 은 과거 → was stolen"),
 a("Mina ___ a letter to her grandma last week.", ["wrote", "was written", "is written"], "미나는 지난주에 할머니께 편지를 썼어요.", "미나가 직접 '쓴' 것 + 목적어 a letter → 능동 wrote", "미나가 쓰인 게 아니라 썼어요 · 목적어 a letter", "last week 은 과거 + 미나가 직접 써요"),
 b("The bridge (A)___ in 1990, and many cars (B)___ it every day.", ["was built", "built"], ["cross", "are crossed"], "그 다리는 1990년에 지어졌고, 매일 많은 차가 그 다리를 건너요.", "(A) 다리는 지어지는 것 → 수동 · (B) 차가 직접 건넘 + 목적어 it → 능동", "다리가 지은 게 아니에요 · was built", "차가 건너'지는' 게 아니에요 · 목적어 it 이 있어요"),
 b("Mina (A)___ some cookies, and they (B)___ quickly by her friends.", ["baked", "was baked"], ["were eaten", "ate"], "미나가 쿠키를 구웠고, 친구들이 금방 다 먹었어요.", "(A) 미나가 직접 구움 → 능동 · (B) 쿠키는 먹히는 것 → 수동", "미나가 구워진 게 아니에요 · 목적어 cookies", "쿠키가 먹은 게 아니에요 · were eaten"),
 b("Hangeul (A)___ by King Sejong, and it (B)___ by many people today.", ["was made", "made"], ["is used", "uses"], "한글은 세종대왕이 만들었고, 오늘날 많은 사람이 써요.", "(A)(B) 한글은 만들어지고 쓰이는 것 → 수동태 · 때에 맞게 was / is", "한글이 만든 게 아니에요 · was made", "한글이 쓰는 게 아니에요 · is used"),
 b("The soccer game (A)___ because of the rain, so we (B)___ a movie instead.", ["was canceled", "canceled"], ["watched", "were watched"], "축구 경기가 비 때문에 취소되어서 우리는 대신 영화를 봤어요.", "(A) 경기는 취소되는 것 → 수동 · (B) 우리가 직접 봄 → 능동", "경기가 취소한 게 아니에요 · was canceled", "우리가 보여진 게 아니에요 · 목적어 a movie"),
],
"agree": [
 a("The books on the desk near the window ___ mine.", ["are", "is", "be"], "창가 책상 위의 책들은 제 거예요.", "진짜 주어는 The books(복수) → are", "desk · window 가 아니라 books 가 주어 → are", "주어 뒤에 원형 be 는 못 와요"),
 a("Each of the students in my class ___ a name tag.", ["has", "have", "having"], "우리 반 학생은 저마다 이름표가 있어요.", "Each of + 복수명사 → 단수 동사 has", "Each 는 하나씩 → 단수 has", "-ing 만으로는 동사가 못 돼요"),
 a("One of my cousins ___ in Busan with his parents.", ["lives", "live", "living"], "제 사촌 중 한 명은 부모님과 부산에 살아요.", "주어는 One(하나) → lives", "cousins 가 아니라 One 이 주어 → lives", "-ing 만으로는 동사가 못 돼요"),
 a("Everyone in my class ___ the new teacher.", ["likes", "like", "liking"], "우리 반 모두가 새 선생님을 좋아해요.", "Everyone 은 단수 → likes", "Everyone 은 단수 → likes", "-ing 만으로는 동사가 못 돼요"),
 a("Riding bikes in the park ___ good exercise.", ["is", "are", "be"], "공원에서 자전거를 타는 건 좋은 운동이에요.", "동명사 주어(Riding ~)는 단수 → is", "bikes 에 속지 마요 · 주어는 Riding(단수)", "주어 뒤에 원형 be 는 못 와요"),
 a("The man with many bags ___ my uncle.", ["is", "are", "be"], "가방을 많이 든 남자는 우리 삼촌이에요.", "주어는 The man(단수) · with many bags 는 꾸밈말 → is", "bags 가 아니라 The man 이 주어 → is", "주어 뒤에 원형 be 는 못 와요"),
 a("Both Tom and his sister ___ in the school band.", ["are", "is", "be"], "톰과 여동생은 둘 다 학교 밴드에서 활동해요.", "Both A and B 는 두 명 → 복수 are", "두 명(Both A and B)은 복수 → are", "주어 뒤에 원형 be 는 못 와요"),
 a("The children in the music room ___ singing together.", ["are", "is", "be"], "음악실에 있는 아이들이 함께 노래하고 있어요.", "주어는 The children(복수) → are", "room 이 아니라 children 이 주어 → are", "주어 뒤에 원형 be 는 못 와요"),
 a("The color of these leaves ___ in the fall.", ["changes", "change", "changing"], "이 나뭇잎들의 색은 가을에 바뀌어요.", "주어는 The color(단수) → changes", "leaves 가 아니라 color 가 주어 → changes", "-ing 만으로는 동사가 못 돼요"),
 a("My sister and her friends ___ to the same school.", ["go", "goes", "going"], "우리 언니와 언니 친구들은 같은 학교에 다녀요.", "A and B 주어는 복수 → go", "주어가 여럿(A and B) → go", "-ing 만으로는 동사가 못 돼요"),
 b("The cookies in the box (A)___ sweet, and each of them (B)___ a heart shape.", ["are", "is"], ["has", "have"], "상자 속 쿠키들은 달콤하고, 하나하나 하트 모양이에요.", "(A) 주어 cookies(복수) → are · (B) each of ~ → 단수 has", "box 가 아니라 cookies 가 주어 → are", "each 는 하나씩 → 단수 has"),
 b("Learning new words (A)___ hard, but my friends and I (B)___ every day.", ["is", "are"], ["practice", "practices"], "새 단어를 익히는 건 어렵지만, 친구들과 저는 매일 연습해요.", "(A) 동명사 주어 → 단수 is · (B) my friends and I → 복수 practice", "words 에 속지 마요 · 주어는 Learning(단수)", "my friends and I 는 여럿 → practice"),
 b("One of my friends (A)___ a cat, and the cat's eyes (B)___ blue.", ["has", "have"], ["are", "is"], "제 친구 중 한 명이 고양이를 키우는데, 그 고양이 눈은 파래요.", "(A) One(하나) → has · (B) eyes(복수) → are", "friends 가 아니라 One 이 주어 → has", "cat 이 아니라 eyes 가 주어 → are"),
 b("Everyone in the room (A)___ quiet because the baby and her mom (B)___ sleeping.", ["is", "are"], ["are", "is"], "아기와 엄마가 자고 있어서 방 안의 모두가 조용히 있어요.", "(A) Everyone → 단수 is · (B) A and B → 복수 are", "Everyone 은 단수 → is", "the baby and her mom 은 두 명 → are"),
],
"what": [
 a("___ I want for Christmas is a puppy.", ["What", "That", "Which"], "크리스마스에 제가 갖고 싶은 건 강아지예요.", "앞에 선행사 없음 + '~한 것' → What", "앞에 선행사가 없어요 · '~한 것'은 What", "Which 로는 '~한 것'을 못 만들어요"),
 a("Write down ___ you learned today.", ["what", "that", "where"], "오늘 배운 것을 적어 보세요.", "선행사 없음 + learned 의 목적어 빠짐 → what", "앞에 선행사가 없어요 → what", "장소가 아니라 '배운 것' → what"),
 a("This is the dress ___ Mom bought for me.", ["that", "what", "where"], "이게 엄마가 저에게 사 주신 원피스예요.", "선행사 the dress 있음 → that", "what 은 선행사(the dress)와 같이 못 써요", "bought 의 목적어가 빠졌어요 · 장소 X"),
 a("I think ___ Jiho is right about the plan.", ["that", "what", "which"], "저는 그 계획에 대해 지호 말이 맞다고 생각해요.", "뒤가 완전한 문장 + '~라고' → 접속사 that", "Jiho is right 는 완전한 문장 → what X", "which 는 앞에 꾸밀 명사가 있어야 해요"),
 a("Is this ___ you are looking for?", ["what", "that", "which"], "이게 네가 찾고 있는 거니?", "선행사 없음 + for 의 목적어 빠짐 → what", "앞에 선행사가 없어요 → what", "which 로는 '~한 것'을 못 만들어요"),
 a("The movie ___ we saw last night was funny.", ["that", "what", "where"], "어젯밤에 우리가 본 영화는 재미있었어요.", "선행사 The movie 있음 → that", "what 은 선행사(The movie)와 같이 못 써요", "saw 의 목적어가 빠졌어요 · 장소 X"),
 a("Tell me ___ happened at school today.", ["what", "that", "who"], "오늘 학교에서 있었던 일을 말해 줘.", "선행사 없음 + happened 의 주어 빠짐 → what", "앞에 선행사가 없어요 → what", "who 는 사람 · 일어난 '일'은 what"),
 a("___ Amy cooked for us was delicious.", ["What", "That", "Who"], "에이미가 우리에게 해 준 요리는 맛있었어요.", "'~한 것' + cooked 의 목적어 빠짐 → What", "That 은 앞에 선행사가 있어야 해요", "Who 는 사람 · 요리한 '것'은 What"),
 a("I know ___ Tom likes soccer very much.", ["that", "what", "which"], "저는 톰이 축구를 아주 좋아한다는 걸 알아요.", "뒤가 완전한 문장(Tom likes soccer) → 접속사 that", "뒤 문장에 빠진 것이 없어요 → that", "which 는 앞에 꾸밀 명사가 있어야 해요"),
 a("Minsu didn't understand ___ the teacher said.", ["what", "that", "where"], "민수는 선생님 말씀을 이해하지 못했어요.", "선행사 없음 + said 의 목적어 빠짐 → what", "said 의 목적어가 빠졌어요 → what", "장소가 아니라 '말한 것' → what"),
 b("(A)___ I like most is pizza. I think (B)___ you will like it too.", ["What", "That"], ["that", "what"], "제가 제일 좋아하는 건 피자예요. 너도 좋아할 거라고 생각해.", "(A) '~한 것' + like 의 목적어 빠짐 → What · (B) 뒤 문장 완전 → 접속사 that", "That 은 앞에 선행사가 필요해요 → What", "you will like it 은 완전한 문장 → what X"),
 b("This is the bag (A)___ Mina bought, but I don't know (B)___ is inside.", ["that", "what"], ["what", "that"], "이게 미나가 산 가방인데, 안에 뭐가 들었는지는 몰라요.", "(A) 선행사 the bag → that · (B) 선행사 없음 + is 의 주어 빠짐 → what", "what 은 선행사(the bag)와 같이 못 써요", "is 의 주어가 빠졌고 선행사도 없어요 → what"),
 b("Jiho told me (A)___ he was sick, so I brought him (B)___ he needed.", ["that", "what"], ["what", "that"], "지호가 아프다고 해서 저는 지호에게 필요한 걸 가져다줬어요.", "(A) 뒤 문장 완전 → 접속사 that · (B) needed 의 목적어 빠짐 + 선행사 없음 → what", "he was sick 는 완전한 문장 → what X", "needed 의 목적어가 빠졌어요 → what"),
 b("The pictures (A)___ Amy took were great. (B)___ I liked best was the sea.", ["that", "what"], ["What", "That"], "에이미가 찍은 사진들은 멋졌어요. 제가 제일 마음에 든 건 바다였어요.", "(A) 선행사 The pictures → that · (B) 선행사 없음 + '~한 것' → What", "what 은 선행사(The pictures)와 같이 못 써요", "That 은 앞에 선행사가 있어야 해요 → What"),
],
"reladv": [
 a("This is the school ___ my mom was a student.", ["where", "which", "when"], "여기가 우리 엄마가 학생이었던 학교예요.", "장소(the school) + 뒤 문장 완전 → where", "my mom was a student 는 완전한 문장 → which X", "when 은 시간 · 학교는 장소"),
 a("Do you know the time ___ the movie starts?", ["when", "where", "which"], "영화가 시작하는 시간을 아세요?", "시간(the time) + 뒤 문장 완전 → when", "where 는 장소 · 시간은 when", "the movie starts 는 완전한 문장 → which X"),
 a("That is the reason ___ I was late for school.", ["why", "which", "where"], "그게 제가 학교에 늦은 이유예요.", "이유(the reason) + 뒤 문장 완전 → why", "I was late 는 완전한 문장 → which X", "where 는 장소 · 이유는 why"),
 a("This is ___ I solved the math problem.", ["how", "what", "which"], "이게 제가 그 수학 문제를 푼 방법이에요.", "'~하는 방법' → how (the way 와 같이 쓰지 않아요)", "I solved the problem 은 완전한 문장 → what X", "which 는 앞에 꾸밀 명사가 있어야 해요"),
 a("Summer is the season ___ I like most.", ["which", "when", "where"], "여름은 제가 가장 좋아하는 계절이에요.", "like 의 목적어가 빠짐(불완전) → 관계대명사 which", "시간이라도 like 의 목적어가 빠졌으면 which", "where 는 장소 · 뒤 문장도 불완전해요"),
 a("Sunday is the day ___ my family goes hiking.", ["when", "where", "which"], "일요일은 우리 가족이 등산 가는 날이에요.", "시간(the day) + 뒤 문장 완전 → when", "where 는 장소 · 날은 when", "my family goes hiking 은 완전 → which X"),
 a("The park ___ we play soccer is near my house.", ["where", "which", "when"], "우리가 축구하는 공원은 우리 집 근처에 있어요.", "장소(The park) + 뒤 문장 완전 → where", "we play soccer 는 완전한 문장 → which X", "when 은 시간 · 공원은 장소"),
 a("The museum ___ we visited last week was very big.", ["which", "where", "when"], "지난주에 우리가 간 박물관은 아주 컸어요.", "visited 의 목적어가 빠짐 → 관계대명사 which", "장소라도 visited 의 목적어가 빠졌으면 which", "when 은 시간 · 뒤 문장도 불완전해요"),
 a("Nobody knows the reason ___ Minsu left early.", ["why", "which", "where"], "민수가 일찍 간 이유를 아무도 몰라요.", "이유(the reason) + 뒤 문장 완전 → why", "Minsu left early 는 완전한 문장 → which X", "where 는 장소 · 이유는 why"),
 a("This is the restaurant ___ we ate pizza last Sunday.", ["where", "which", "how"], "여기가 지난 일요일에 우리가 피자를 먹은 식당이에요.", "장소 + 뒤 문장 완전(we ate pizza) → where", "we ate pizza 는 완전한 문장 → which X", "how 는 방법 · 식당은 장소"),
 b("This is the library (A)___ I study, and Monday is the day (B)___ it closes.", ["where", "which"], ["when", "where"], "여기가 제가 공부하는 도서관이고, 월요일은 도서관이 쉬는 날이에요.", "(A) 장소 + 완전 → where · (B) 시간(the day) + 완전 → when", "I study 는 완전한 문장 → which X", "where 는 장소 · 날은 when"),
 b("Jeju is the island (A)___ I visited, and it is the place (B)___ my uncle lives.", ["which", "where"], ["where", "which"], "제주는 제가 가 본 섬이고, 삼촌이 사시는 곳이에요.", "(A) visited 의 목적어 빠짐 → which · (B) 장소 + 완전 → where", "visited 의 목적어가 빠졌어요 → which", "my uncle lives 는 완전한 문장 → which X"),
 b("Tell me (A)___ you made this cake and the reason (B)___ you made it.", ["how", "which"], ["why", "when"], "이 케이크를 어떻게 만들었는지, 그리고 왜 만들었는지 말해 줘.", "(A) '~한 방법' → how · (B) 이유(the reason) + 완전 → why", "which 는 앞에 꾸밀 명사가 있어야 해요", "when 은 시간 · 이유는 why"),
 b("Winter is the season (A)___ I like best because it is the time (B)___ it snows.", ["which", "when"], ["when", "which"], "겨울은 제가 가장 좋아하는 계절이에요. 눈이 오는 때거든요.", "(A) like 의 목적어 빠짐 → which · (B) 시간 + 완전 → when", "시간이라도 like 의 목적어가 빠졌으면 which", "it snows 는 완전한 문장 → which X"),
],
"ifp": [
 a("If I ___ rich, I would buy a big house.", ["were", "am", "be"], "내가 부자라면 큰 집을 살 텐데.", "가정법 과거: If + 주어 + were, would + 원형", "would 와 짝이면 현재형 am 은 X", "if 절에 원형 be 는 못 와요"),
 a("If I had a time machine, I ___ visit the dinosaurs.", ["could", "can", "will"], "나에게 타임머신이 있다면 공룡을 보러 갈 수 있을 텐데.", "If + 과거(had) → 주절은 could + 원형", "If + 과거형 짝은 can 이 아니라 could", "If + 과거형 짝은 will 이 아니라 would · could"),
 a("I wish I ___ a little sister like Yuna.", ["had", "have", "has"], "나도 유나 같은 여동생이 있으면 좋을 텐데.", "I wish + 과거형 → 지금 이루기 힘든 바람", "I wish 뒤엔 과거형 · had", "I 에는 has 를 안 써요 · 과거형 had"),
 a("If Grandma ___ here, she would make us cookies.", ["were", "is", "be"], "할머니가 여기 계신다면 우리에게 쿠키를 만들어 주실 텐데.", "가정법 과거: be동사는 were", "would 와 짝이면 현재형 is 는 X", "if 절에 원형 be 는 못 와요"),
 a("If I knew Amy's phone number, I ___ her now.", ["would call", "will call", "called"], "에이미 전화번호를 안다면 지금 전화할 텐데.", "If + 과거(knew) → would + 원형", "If + 과거형 짝은 will 이 아니라 would", "주절엔 would + 원형 · called X"),
 a("If we ___ a car, we could go camping.", ["had", "have", "has"], "우리에게 차가 있다면 캠핑을 갈 수 있을 텐데.", "주절이 could → if 절은 과거형 had", "주절이 could → if 절도 과거형", "we 에는 has X · 과거형 had"),
 a("I wish I ___ swim like a fish.", ["could", "can", "will"], "물고기처럼 수영할 수 있으면 좋을 텐데.", "I wish + could + 원형", "I wish 뒤엔 과거형 · could", "I wish 뒤엔 will 이 아니라 could"),
 a("If it rains tomorrow, I ___ stay at home.", ["will", "would", "am"], "내일 비가 오면 저는 집에 있을 거예요.", "정말 일어날 수 있는 일(조건) → If + 현재, will + 원형", "rains 는 현재형 · 실제 조건이면 will", "am 뒤엔 stay(원형)를 못 써요"),
 a("If Mina ___ the answer, she would tell us.", ["knew", "knows", "know"], "미나가 답을 안다면 우리에게 말해 줄 텐데.", "주절이 would → if 절은 과거형 knew", "would 와 짝이면 현재형 X", "Mina 는 3인칭 + 과거형이 필요해요"),
 a("If I were a bird, I ___ fly over the sea.", ["would", "will", "am"], "내가 새라면 바다 위를 날아갈 텐데.", "If I were ~ → would + 원형", "If I were 짝은 will 이 아니라 would", "am 뒤엔 fly(원형)를 못 써요"),
 b("If I (A)___ a robot, it (B)___ do my homework for me.", ["had", "have"], ["would", "will"], "나에게 로봇이 있다면 내 숙제를 대신 해 줄 텐데.", "가정법 과거: If + 과거형, would + 원형", "would 짝 → if 절은 과거형 had", "If + 과거형 짝은 will 이 아니라 would"),
 b("I wish I (A)___ taller. If I were tall, I (B)___ play basketball better.", ["were", "am"], ["could", "can"], "키가 더 크면 좋을 텐데. 키가 크다면 농구를 더 잘할 수 있을 텐데.", "(A) I wish + were · (B) If I were ~ → could + 원형", "I wish 뒤엔 과거형 · be동사는 were", "If I were 짝은 can 이 아니라 could"),
 b("If it (A)___ tomorrow, we will stay home. If it were sunny, we (B)___ swim.", ["rains", "rained"], ["could", "can"], "내일 비가 오면 우리는 집에 있을 거예요. 날씨가 맑다면 수영할 수 있을 텐데요.", "(A) 주절 will → 실제 조건, 현재형 rains · (B) If it were ~ → could + 원형", "주절이 will → 실제 조건이라 현재형 rains", "If it were 짝은 can 이 아니라 could"),
 b("If Jiho (A)___ in Seoul, he (B)___ visit us every weekend.", ["lived", "lives"], ["would", "will"], "지호가 서울에 산다면 주말마다 우리를 보러 올 텐데.", "가정법 과거: If + 과거형, would + 원형", "would 짝 → if 절은 과거형 lived", "If + 과거형 짝은 will 이 아니라 would"),
],
"verb2": [
 a("Jiho finished ___ the book in one day.", ["reading", "to read", "read"], "지호는 하루 만에 그 책을 다 읽었어요.", "finish 는 -ing 만 목적어로 써요", "finish 뒤에는 to 를 못 써요 · -ing", "finished 뒤에 원형은 못 와요"),
 a("Mina decided ___ a new hobby this year.", ["to start", "starting", "start"], "미나는 올해 새 취미를 시작하기로 했어요.", "decide 는 to + 원형을 목적어로 써요", "decide 뒤엔 -ing X · to 부정사", "decided 뒤에 원형은 못 와요"),
 a("Please stop ___ in the library. It's too loud.", ["talking", "to talk", "talk"], "도서관에서 그만 떠들어 주세요. 너무 시끄러워요.", "stop -ing: 하던 것을 멈추다", "stop to 는 '~하려고 멈추다' · 떠들기를 멈추는 건 -ing", "stop 뒤에 원형은 못 와요"),
 a("On the way home, Jiho stopped ___ some bread.", ["to buy", "buying", "buy"], "집에 가는 길에 지호는 빵을 사려고 멈췄어요.", "stop to: ~하려고 (가던 길을) 멈추다", "stop -ing 는 '하던 걸 멈춤' · 사려고 멈춘 건 to", "stopped 뒤에 원형은 못 와요"),
 a("I will never forget ___ the ocean for the first time.", ["seeing", "to see", "see"], "처음 바다를 본 일을 절대 잊지 못할 거예요.", "forget -ing: (전에) ~한 것을 잊다", "forget to 는 '할 일'을 잊음 · 이미 본 건 -ing", "forget 뒤에 원형은 못 와요"),
 a("Remember ___ your umbrella. It will rain today.", ["to take", "taking", "take"], "우산 챙기는 거 잊지 마. 오늘 비 온대.", "remember to: (앞으로) ~할 것을 기억하다", "remember -ing 는 '한 일' · 할 일은 to", "Remember 뒤에 원형은 못 와요"),
 a("Would you mind ___ me with this box?", ["helping", "to help", "help"], "이 상자 옮기는 것 좀 도와주실래요?", "mind 는 -ing 만 목적어로 써요", "mind 뒤에는 to 를 못 써요 · -ing", "mind 뒤에 원형은 못 와요"),
 a("Yuna hopes ___ a doctor in the future.", ["to become", "becoming", "become"], "유나는 나중에 의사가 되고 싶어 해요.", "hope 는 to + 원형을 목적어로 써요", "hope 뒤엔 -ing X · to 부정사", "hopes 뒤에 원형은 못 와요"),
 a("My dad gave up ___ coffee last month.", ["drinking", "to drink", "drink"], "우리 아빠는 지난달에 커피를 끊으셨어요.", "give up 은 -ing 만 목적어로 써요", "give up 뒤엔 to 를 못 써요 · -ing", "gave up 뒤에 원형은 못 와요"),
 a("Minsu forgot ___ his lunch, so he was hungry.", ["to bring", "bringing", "bring"], "민수는 점심을 챙겨 오는 걸 잊어서 배가 고팠어요.", "forget to: (해야 할 일을) 잊다", "forget -ing 는 '한 일'을 잊음 · 할 일을 잊은 건 to", "forgot 뒤에 원형은 못 와요"),
 b("I enjoy (A)___ pictures, and I want (B)___ a photographer someday.", ["taking", "to take"], ["to be", "being"], "저는 사진 찍는 걸 좋아하고, 언젠가 사진작가가 되고 싶어요.", "(A) enjoy + -ing · (B) want + to 부정사", "enjoy 뒤엔 to 를 못 써요 · -ing", "want 뒤엔 -ing X · to 부정사"),
 b("Jiho stopped (A)___ games and decided (B)___ for the test.", ["playing", "to play"], ["to study", "studying"], "지호는 게임을 그만하고 시험공부를 하기로 했어요.", "(A) stop -ing: 하던 걸 멈춤 · (B) decide + to 부정사", "stop to 는 '~하려고 멈춤' · 게임을 그만둔 건 -ing", "decide 뒤엔 -ing X · to 부정사"),
 b("I remember (A)___ Amy at the camp, so I won't forget (B)___ her a card.", ["meeting", "to meet"], ["to send", "sending"], "캠프에서 에이미를 만난 게 기억나서, 카드 보내는 걸 잊지 않을 거예요.", "(A) remember -ing: 지난 일 · (B) forget to: 앞으로 할 일", "만난 건 지난 일 → remember -ing", "보낼 건 앞으로 할 일 → forget to"),
 b("Tom gave up (A)___ the piano, but now he wants (B)___ again.", ["playing", "to play"], ["to start", "starting"], "톰은 피아노를 그만뒀지만, 이제 다시 시작하고 싶어 해요.", "(A) give up + -ing · (B) want + to 부정사", "give up 뒤엔 to 를 못 써요 · -ing", "want 뒤엔 -ing X · to 부정사"),
],
"caus": [
 a("Our coach made us ___ around the field twice.", ["run", "to run", "running"], "코치님은 우리에게 운동장을 두 바퀴 뛰게 하셨어요.", "make + 목적어 + 동사원형", "make + 사람 뒤엔 to 없이 원형", "make + 사람 뒤엔 -ing 아닌 원형"),
 a("Mom told me ___ my room before dinner.", ["to clean", "clean", "cleaning"], "엄마가 저녁 전에 방을 치우라고 하셨어요.", "tell + 목적어 + to 부정사 (tell 은 사역동사가 아니에요)", "tell 은 사역동사가 아니라 to 가 필요해요", "tell + 사람 뒤엔 to + 원형"),
 a("My parents finally let me ___ a puppy at home.", ["have", "to have", "having"], "부모님이 드디어 집에서 강아지를 키우게 해 주셨어요.", "let + 목적어 + 동사원형", "let + 사람 뒤엔 to 없이 원형", "let + 사람 뒤엔 -ing 아닌 원형"),
 a("Grandma had me ___ the flowers in her garden.", ["water", "to water", "watered"], "할머니는 저에게 정원의 꽃에 물을 주게 하셨어요.", "have + 사람 + 동사원형", "have + 사람 뒤엔 to 없이 원형", "제가 직접 물을 줘요 · 원형 water"),
 a("I saw Tom ___ across the street to the bus.", ["run", "to run", "ran"], "저는 톰이 길 건너 버스로 달려가는 걸 봤어요.", "see(지각동사) + 목적어 + 원형 · -ing", "see + 사람 뒤엔 to 를 못 써요", "see + 사람 뒤엔 과거형 말고 원형"),
 a("I felt something ___ on my arm.", ["move", "to move", "moved"], "팔 위에서 뭔가 움직이는 게 느껴졌어요.", "feel(지각동사) + 목적어 + 원형 · -ing", "feel + 목적어 뒤엔 to 를 못 써요", "직접 움직이는 것 → 과거형 말고 원형"),
 a("Amy helped her mom ___ the dishes.", ["wash", "washing", "washed"], "에이미는 엄마가 설거지하시는 걸 도왔어요.", "help + 목적어 + 원형 (to + 원형도 돼요)", "help + 사람 뒤엔 -ing X · 원형", "help + 사람 뒤엔 과거형 X · 원형"),
 a("The coach wanted us ___ more water.", ["to drink", "drink", "drinking"], "코치님은 우리가 물을 더 마시기를 바라셨어요.", "want + 목적어 + to 부정사", "want 는 사역동사가 아니라 to 가 필요해요", "want + 사람 뒤엔 to + 원형"),
 a("Minsu watched his brother ___ a sand castle on the beach.", ["build", "to build", "built"], "민수는 남동생이 해변에서 모래성을 쌓는 걸 지켜봤어요.", "watch(지각동사) + 목적어 + 원형 · -ing", "watch + 사람 뒤엔 to 를 못 써요", "남동생이 직접 쌓아요 · 원형"),
 a("Please let me ___ you with your bag.", ["help", "to help", "helping"], "가방 드는 거 제가 도와드릴게요.", "let + 목적어 + 동사원형", "let + 사람 뒤엔 to 없이 원형", "let + 사람 뒤엔 -ing 아닌 원형"),
 b("Our teacher made us (A)___ in pairs and asked us (B)___ a poster.", ["work", "to work"], ["to make", "make"], "선생님은 우리를 짝지어 활동하게 하시고, 포스터를 만들라고 하셨어요.", "(A) make + 목적어 + 원형 · (B) ask + 목적어 + to 부정사", "make + 사람 뒤엔 to 없이 원형", "ask 는 사역동사가 아니라 to 가 필요해요"),
 b("I saw Jiho (A)___ the street, and I heard him (B)___ my name.", ["cross", "to cross"], ["call", "to call"], "지호가 길을 건너는 걸 봤고, 지호가 제 이름을 부르는 걸 들었어요.", "지각동사 see · hear + 목적어 + 원형", "see + 사람 뒤엔 to 를 못 써요", "hear + 사람 뒤엔 to 를 못 써요"),
 b("Mom let me (A)___ TV, but she told me (B)___ to bed by ten.", ["watch", "to watch"], ["to go", "go"], "엄마는 TV 를 보게 해 주셨지만, 10시까지는 자라고 하셨어요.", "(A) let + 원형 · (B) tell + to 부정사", "let + 사람 뒤엔 to 없이 원형", "tell 은 사역동사가 아니라 to 가 필요해요"),
 b("The coach had us (A)___ every day, and he watched us (B)___ the game.", ["practice", "to practice"], ["play", "to play"], "코치님은 우리에게 매일 연습을 시키셨고, 우리가 경기하는 걸 지켜보셨어요.", "(A) have + 원형 · (B) watch(지각동사) + 원형", "have + 사람 뒤엔 to 없이 원형", "watch + 사람 뒤엔 to 를 못 써요"),
],
"adj": [
 a("Tom runs very ___. He always wins the race.", ["fast", "fastly", "faster"], "톰은 아주 빨리 달려요. 늘 경주에서 이겨요.", "fast 는 형용사·부사 모양이 같아요 (fastly 는 없는 말)", "fastly 라는 말은 없어요 · fast 가 부사", "very 뒤엔 비교급을 못 써요 · very fast"),
 a("Jiho studied ___ for the test, so he got an A.", ["hard", "hardly", "hardness"], "지호는 시험공부를 열심히 해서 A를 받았어요.", "hard = 열심히 (부사) · hardly 는 '거의 ~않다'", "hardly 는 '거의 안' · 열심히는 hard", "hardness 는 명사 · 동사를 꾸밀 땐 부사"),
 a("This soup smells ___. Can I try some?", ["good", "well", "nicely"], "이 수프 냄새 좋네요. 좀 먹어 봐도 돼요?", "smell(감각동사) 뒤 → 형용사 good", "smell 뒤엔 형용사 · well 은 여기선 부사", "nicely 는 부사 · 감각동사 뒤엔 형용사"),
 a("Mina is a ___ girl, so everyone likes her.", ["friendly", "friendship", "friend"], "미나는 상냥한 아이라서 모두 미나를 좋아해요.", "girl 을 꾸미는 형용사 friendly (-ly 지만 형용사예요)", "friendship 은 명사(우정) · 형용사 자리", "friend 는 명사 · a ___ girl 엔 형용사"),
 a("Please speak ___ to your friends in the library.", ["quietly", "quiet", "quietness"], "도서관에서는 친구에게 조용히 말해 주세요.", "동사 speak 를 꾸밈 → 부사 quietly", "quiet 는 형용사 · 동사를 꾸밀 땐 부사", "quietness 는 명사 · 부사 자리"),
 a("The news made all of us very ___.", ["happy", "happily", "happiness"], "그 소식은 우리 모두를 아주 행복하게 했어요.", "make + 목적어 + 형용사 → happy", "make + 목적어 뒤엔 부사 X · 형용사", "happiness 는 명사 · '행복하게'는 형용사 자리"),
 a("The baby is sleeping ___ in her bed.", ["peacefully", "peaceful", "peace"], "아기가 침대에서 평화롭게 자고 있어요.", "동사 sleeping 을 꾸밈 → 부사 peacefully", "peaceful 은 형용사 · 동사를 꾸밀 땐 부사", "peace 는 명사 · 부사 자리"),
 a("Your idea sounds ___. Let's try it.", ["great", "greatly", "greatness"], "네 생각 정말 좋은 것 같아. 해 보자.", "sound(감각동사) 뒤 → 형용사 great", "sound(~하게 들리다) 뒤엔 부사 X · 형용사", "greatness 는 명사 · 형용사 자리"),
 a("Please keep your hands ___ before lunch.", ["clean", "cleanly", "cleaning"], "점심 먹기 전에는 손을 깨끗하게 해 두세요.", "keep + 목적어 + 형용사 → clean", "keep + 목적어 뒤엔 부사 X · 형용사", "손이 청소하는 게 아니에요 · 형용사 clean"),
 a("Amy came home ___ last night, so she was tired.", ["late", "lately", "lateness"], "에이미는 어젯밤 늦게 집에 와서 피곤했어요.", "late = 늦게 (부사) · lately 는 '최근에'", "lately 는 '최근에' · 늦게는 late", "lateness 는 명사 · 부사 자리"),
 b("The cake looks (A)___, and Mom cut it (B)___ for us.", ["delicious", "deliciously"], ["carefully", "careful"], "케이크가 맛있어 보이고, 엄마가 우리에게 조심스럽게 잘라 주셨어요.", "(A) look(감각동사) + 형용사 · (B) 동사 cut 을 꾸밈 → 부사", "look 뒤엔 부사 X · 형용사", "careful 은 형용사 · 동사를 꾸밀 땐 부사"),
 b("Jiho answered the question (A)___, and his answer sounded (B)___.", ["quickly", "quick"], ["correct", "correctly"], "지호는 질문에 재빨리 대답했고, 대답은 맞는 것 같았어요.", "(A) 동사 answered 를 꾸밈 → 부사 · (B) sound + 형용사", "quick 은 형용사 · 동사를 꾸밀 땐 부사", "sound 뒤엔 부사 X · 형용사"),
 b("Please keep the room (A)___ and walk (B)___ when the baby sleeps.", ["quiet", "quietly"], ["quietly", "quiet"], "아기가 잘 때는 방을 조용하게 하고 조용히 걸어 주세요.", "(A) keep + 목적어 + 형용사 · (B) 동사 walk 를 꾸밈 → 부사", "keep + 목적어 뒤엔 부사 X · 형용사", "quiet 는 형용사 · 동사를 꾸밀 땐 부사"),
 b("Yuna worked (A)___ all day, so she felt (B)___ at night.", ["hard", "hardly"], ["tired", "tiredly"], "유나는 하루 종일 열심히 일해서 밤에 피곤했어요.", "(A) hard = 열심히 · (B) feel + 형용사", "hardly 는 '거의 안' · 열심히는 hard", "feel 뒤엔 부사 X · 형용사"),
],
"indq": [
 a("I wonder where ___ at night.", ["the birds sleep", "do the birds sleep", "the birds sleeps"], "새들이 밤에 어디서 자는지 궁금해요.", "간접의문문: 의문사 + 주어 + 동사", "문장 속 의문문엔 do 를 안 써요 · the birds sleep", "the birds 는 복수 → sleep"),
 a("I want to know how much ___.", ["this bag is", "is this bag", "does this bag"], "이 가방이 얼마인지 알고 싶어요.", "how much + 주어 + 동사", "문장 속 의문문은 주어 먼저 · this bag is", "does 를 쓸 필요가 없어요 · 주어 + 동사"),
 a("I don't know why ___ angry this morning.", ["Tom was", "was Tom", "did Tom"], "톰이 오늘 아침에 왜 화가 났는지 모르겠어요.", "why + 주어 + 동사", "문장 속 의문문은 주어 먼저 · Tom was", "did 를 쓸 필요가 없어요 · 주어 + 동사"),
 a("Please ask Amy ___ she can come to the party.", ["if", "what", "which"], "에이미에게 파티에 올 수 있는지 물어봐 줘.", "의문사 없는 간접의문문 → if(~인지)", "뒤 문장이 완전해요 → what X", "which 는 '어느 것' · '~인지'는 if"),
 a("Nobody knows who ___ this cake for the party.", ["made", "did he make", "he made"], "파티 케이크를 누가 만들었는지 아무도 몰라요.", "의문사(who)가 주어 → who + 동사", "문장 속 의문문엔 did 를 안 써요 · who 가 주어", "who 가 주어라 he 가 또 올 수 없어요"),
 a("Tell me what ___ for lunch.", ["you want", "do you want", "want you"], "점심으로 뭘 먹고 싶은지 말해 줘.", "what + 주어 + 동사", "문장 속 의문문엔 do 를 안 써요", "주어가 먼저 · you want"),
 a("I'm not sure when ___.", ["the movie starts", "does the movie start", "the movie start"], "영화가 언제 시작하는지 잘 모르겠어요.", "when + 주어 + 동사 (3인칭 단수 -s)", "문장 속 의문문엔 does 를 안 써요", "the movie 는 3인칭 단수 → starts"),
 a("Do you know how many students ___ in your class?", ["there are", "are there", "there is"], "너희 반에 학생이 몇 명 있는지 아니?", "how many + 주어(there) + 동사 → there are", "문장 속 의문문은 주어 먼저 · there are", "students 는 복수 → there are"),
 a("Minsu asked me where ___ my new shoes.", ["I bought", "did I buy", "bought I"], "민수가 저에게 새 신발을 어디서 샀는지 물었어요.", "where + 주어 + 동사", "문장 속 의문문엔 did 를 안 써요 · I bought", "주어가 먼저 · I bought"),
 a("Could you tell me ___ this bus goes to the zoo?", ["if", "what", "who"], "이 버스가 동물원에 가는지 알려 주실래요?", "의문사 없는 의문문(Does this bus go ~?) → if", "뒤 문장이 완전해요 → what X", "who 는 '누구' · '~인지'는 if"),
 b("Do you know where (A)___? I also wonder (B)___ it is open today.", ["the library is", "is the library"], ["if", "what"], "도서관이 어디 있는지 아세요? 오늘 문을 여는지도 궁금해요.", "(A) where + 주어 + 동사 · (B) 의문사 없는 의문문 → if", "문장 속 의문문은 주어 먼저 · the library is", "뒤 문장이 완전해요 → what X"),
 b("Mom asked me what (A)___ and when (B)___ home.", ["I ate", "did I eat"], ["I came", "did I come"], "엄마는 제가 뭘 먹었는지, 언제 집에 왔는지 물으셨어요.", "(A)(B) 문장 속 의문문 → 의문사 + 주어 + 동사", "문장 속 의문문엔 did 를 안 써요 · I ate", "문장 속 의문문엔 did 를 안 써요 · I came"),
 b("Can you tell me how (A)___ there? I don't know (B)___ it is far.", ["I can get", "can I get"], ["if", "what"], "거기 어떻게 가는지 알려 줄래요? 먼지 잘 모르겠어요.", "(A) how + 주어 + 동사 · (B) 의문사 없는 의문문 → if", "문장 속 의문문은 주어 먼저 · I can get", "뒤 문장이 완전해요 → what X"),
 b("Yuna wonders why (A)___ sad, so she asks him (B)___ he is okay.", ["Jiho is", "is Jiho"], ["whether", "what"], "유나는 지호가 왜 슬픈지 궁금해서 괜찮은지 물어봐요.", "(A) why + 주어 + 동사 · (B) 의문사 없는 의문문 → whether(~인지)", "문장 속 의문문은 주어 먼저 · Jiho is", "뒤 문장이 완전해요 → what X · '~인지'는 whether"),
],
"it": [
 a("It is helpful ___ a list before shopping.", ["to make", "make", "makes"], "장 보기 전에 목록을 만들어 두면 도움이 돼요.", "가주어 It ~ 진주어 to + 원형", "진주어는 to + 원형 · to 가 빠졌어요", "makes 는 문장의 동사 모양 · 진주어는 to + 원형"),
 a("It was wise ___ Jiho to save his money.", ["of", "for", "to"], "용돈을 모으다니 지호는 현명했어요.", "wise(사람을 칭찬하는 말) → 의미상 주어 of", "wise 처럼 사람을 칭찬하는 말 뒤엔 of", "to Jiho 는 X · 성격 형용사 뒤엔 of"),
 a("It is difficult ___ my grandpa to use a smartphone.", ["for", "of", "to"], "할아버지는 스마트폰을 쓰기가 어려우세요.", "difficult(쉽다 · 어렵다) → 의미상 주어 for", "difficult 는 사람 성격이 아니에요 → for", "to my grandpa to ~ 는 X · for"),
 a("To learn a new language ___ fun but hard.", ["is", "are", "be"], "새 언어를 배우는 건 재미있지만 어려워요.", "to 부정사 주어는 단수 → is", "to 부정사 주어는 단수 → is", "주어 뒤에 원형 be 는 못 와요"),
 a("It is not safe ___ alone at night.", ["to walk", "walk", "walked"], "밤에 혼자 걷는 건 안전하지 않아요.", "It ~ 진주어 to + 원형", "진주어는 to + 원형 · to 가 빠졌어요", "walked 는 과거형 · 진주어는 to + 원형"),
 a("___ is fun to play soccer with friends.", ["It", "That", "This"], "친구들과 축구하는 건 재미있어요.", "뒤의 to 부정사를 대신하는 가주어 → It", "가주어는 It 만 써요", "가주어는 It 만 써요"),
 a("Taking care of a pet ___ a lot of time.", ["takes", "take", "taking"], "반려동물을 돌보는 데는 시간이 많이 들어요.", "동명사 주어(Taking ~)는 단수 → takes", "주어는 Taking(단수) → takes", "-ing 만으로는 동사가 못 돼요"),
 a("It was hard ___ Minsu to wake up early.", ["for", "of", "to"], "민수는 일찍 일어나기가 힘들었어요.", "hard(어렵다) → 의미상 주어 for", "hard 는 성격 칭찬이 아니에요 → for", "to Minsu 는 X · for Minsu"),
 a("It is a good idea ___ a map before the trip.", ["to check", "check", "checked"], "여행 전에 지도를 확인하는 건 좋은 생각이에요.", "It ~ 진주어 to + 원형", "진주어는 to + 원형 · to 가 빠졌어요", "checked 는 과거형 · 진주어는 to + 원형"),
 a("It was polite ___ Tom to say thank you.", ["of", "for", "with"], "고맙다고 말하다니 톰은 예의가 발랐어요.", "polite(성격 칭찬) → 의미상 주어 of", "polite 처럼 성격을 말할 땐 of", "with 는 X · 성격 형용사 뒤엔 of"),
 b("It is fun (A)___ games, but it is hard (B)___ me to win.", ["to play", "play"], ["for", "of"], "게임을 하는 건 재미있지만, 제가 이기기는 어려워요.", "(A) 진주어 to + 원형 · (B) hard → 의미상 주어 for", "진주어는 to + 원형 · to 가 빠졌어요", "hard 는 성격 칭찬이 아니에요 → for"),
 b("It was brave (A)___ you to sing on stage. Singing there (B)___ not easy.", ["of", "for"], ["is", "are"], "무대에서 노래하다니 너 용감했어. 거기서 노래하는 건 쉽지 않거든.", "(A) brave(성격) → of · (B) 동명사 주어 → 단수 is", "brave 처럼 성격을 말할 땐 of", "동명사 주어는 단수 → is"),
 b("It is important (A)___ enough sleep, and (B)___ is good to eat vegetables.", ["to get", "getting"], ["it", "that"], "잠을 충분히 자는 건 중요하고, 채소를 먹는 것도 좋아요.", "(A) 진주어 to + 원형 · (B) 가주어 it", "가주어 It 의 진주어는 to + 원형", "가주어는 it 만 써요"),
 b("Riding a bike (A)___ fun, but it is not easy (B)___ up a hill.", ["is", "are"], ["to go", "go"], "자전거 타기는 재미있지만, 언덕을 오르기는 쉽지 않아요.", "(A) 동명사 주어 → 단수 is · (B) 진주어 to + 원형", "동명사 주어는 단수 → is", "진주어는 to + 원형 · to 가 빠졌어요"),
],
"paral": [
 a("I like to sing and ___ with my friends.", ["dance", "dancing", "danced"], "저는 친구들과 노래하고 춤추는 걸 좋아해요.", "to sing 과 짝 → (to) dance", "to sing 과 짝 · to 뒤엔 원형 dance", "danced 는 과거형 · to 와 짝 → 원형"),
 a("The park is big, clean, and ___.", ["beautiful", "beautifully", "beauty"], "그 공원은 넓고, 깨끗하고, 아름다워요.", "big, clean 과 같은 형용사", "beautifully 는 부사 · big, clean 은 형용사", "beauty 는 명사 · 형용사끼리 짝"),
 a("Tom washed the dishes and ___ the floor.", ["cleaned", "cleans", "cleaning"], "톰은 설거지를 하고 바닥을 청소했어요.", "washed 와 같은 과거형", "washed(과거)와 짝 → cleaned", "-ing 만으로는 동사가 못 돼요"),
 a("You can either walk or ___ the bus.", ["take", "taking", "took"], "걸어가거나 버스를 탈 수 있어요.", "either A or B · can 뒤 walk 와 같은 원형", "can walk 와 짝 → 원형 take", "can 뒤엔 과거형 X · 원형"),
 a("Yuna not only sings well but also ___ well.", ["dances", "dance", "dancing"], "유나는 노래를 잘할 뿐 아니라 춤도 잘 춰요.", "not only A but also B · sings 와 같은 모양", "sings(-s)와 짝 → dances", "-ing 만으로는 동사가 못 돼요"),
 a("Reading books and ___ to music are my hobbies.", ["listening", "listen", "listened"], "책 읽기와 음악 듣기가 제 취미예요.", "Reading 과 짝 → -ing", "Reading 과 짝 → listening", "listened 는 과거형 · Reading 과 짝 → -ing"),
 a("Please open your book and ___ to page 10.", ["turn", "turning", "turned"], "책을 펴고 10쪽을 펴세요.", "명령문 open 과 같은 원형", "open(원형)과 짝 → turn", "명령문은 원형 · open 과 짝"),
 a("Our teacher speaks slowly and ___.", ["clearly", "clear", "clearness"], "우리 선생님은 천천히 또박또박 말씀하세요.", "slowly 와 같은 부사", "slowly(부사)와 짝 → clearly", "clearness 는 명사 · 부사끼리 짝"),
 a("We went to the beach, swam, and ___ sand castles.", ["built", "build", "building"], "우리는 해변에 가서 수영하고 모래성을 쌓았어요.", "went, swam 과 같은 과거형", "went, swam(과거)과 짝 → built", "-ing 만으로는 동사가 못 돼요"),
 a("The teacher told us to listen and ___ notes.", ["take", "taking", "took"], "선생님은 우리에게 잘 듣고 필기하라고 하셨어요.", "to listen 과 짝 → (to) take", "to listen 과 짝 → 원형 take", "to 뒤엔 과거형 X · 원형"),
 b("Amy likes reading and (A)___, and she is kind and (B)___.", ["drawing", "to draw"], ["honest", "honestly"], "에이미는 책 읽기와 그림 그리기를 좋아하고, 친절하고 정직해요.", "(A) reading 과 짝 → -ing · (B) kind 와 짝 → 형용사", "reading 과 짝 → drawing", "kind(형용사)와 짝 → honest"),
 b("Jiho cleaned his room and (A)___ his homework, so he felt happy and (B)___.", ["did", "does"], ["proud", "proudly"], "지호는 방을 치우고 숙제를 해서 기분이 좋고 뿌듯했어요.", "(A) cleaned 와 짝 → 과거형 did · (B) happy 와 짝 → 형용사", "cleaned(과거)와 짝 → did", "happy(형용사)와 짝 → proud"),
 b("Minsu not only (A)___ fast but also jumps high, so he is strong and (B)___.", ["runs", "run"], ["healthy", "healthily"], "민수는 빨리 달릴 뿐 아니라 높이 뛰어요. 그래서 튼튼하고 건강해요.", "(A) jumps 와 짝 → runs · (B) strong 과 짝 → 형용사", "jumps(-s)와 짝 → runs", "strong(형용사)와 짝 → healthy"),
 b("I like to read or (A)___ movies, and my sister enjoys cooking and (B)___.", ["watch", "watching"], ["baking", "to bake"], "저는 책 읽기나 영화 보기를 좋아하고, 언니는 요리하고 빵 굽는 걸 즐겨요.", "(A) to read 와 짝 → (to) watch · (B) cooking 과 짝 → -ing", "to read 와 짝 → 원형 watch", "enjoy + -ing · cooking 과 짝 → baking"),
],
}

OK_CAP = set("A Grandma I Mina Jiho Minsu Yuna Tom Amy Mom Dad Busan Seoul Jeju Hangeul King Sejong Christmas Sunday Monday Friday English TV".split())
PPF = re.compile(r"\bhad (been|\w+ed|done|gone|seen|eaten|taken|written|given|known|made|put|left|lost|found|bought|got)\b", re.I)
def words(s): return len(re.findall(r"[A-Za-z'.]+", s))

def build():
    out = {}
    for k, L in NEW.items():
        assert len(L) == 14, (k, len(L))
        l2 = [x for x in L if x[0] == "2"]; l3 = [x for x in L if x[0] == "3"]; assert len(l2) == 10 and len(l3) == 4, k
        D2 = []
        for _, s, o, ko, why, w in l2: D2.append({"k": k, "lv": 2, "s": s, "o": o, "ko": ko, "why": why, "w": w})
        D3 = []
        for _, s, A, B, ko, why, wA, wB in l3: D3.append({"k": k, "lv": 3, "s": s, "A": A, "B": B, "ko": ko, "why": why, "wA": wA, "wB": wB})
        out[k] = (D2, D3)
    return out

def check(d, H):
    bad = []
    s = d["s"]
    if d["lv"] == 2:
        if s.count("___") != 1: bad.append("빈칸 수")
        if len(set(d["o"])) != 3: bad.append("보기 겹침")
        if set(d["w"]) != set(d["o"][1:]): bad.append("오답 이유 짝")
        full = s.replace("___", d["o"][0]); n = words(full)
        if not 6 <= n <= 12: bad.append("길이 %d" % n)
        if s.startswith("___") and not d["o"][0][0].isupper(): bad.append("첫 글자")
    else:
        if s.count("(A)___") != 1 or s.count("(B)___") != 1 or s.count("___") != 2: bad.append("(A)(B) 자리")
        if len(set(d["A"])) != 2 or len(set(d["B"])) != 2: bad.append("보기 겹침")
        if " – ".join([d["A"][0], d["B"][0]]) == " – ".join([d["A"][1], d["B"][1]]): bad.append("조합")
        full = s.replace("(A)___", d["A"][0]).replace("(B)___", d["B"][0]); n = words(full)
        if not 9 <= n <= 16: bad.append("길이 %d" % n)
    if PPF.search(full): bad.append("과거완료")
    for i, t in enumerate(re.findall(r"[A-Za-z']+", full)):
        if t[0].isupper() and re.sub(r"'s$", "", t) not in OK_CAP:
            pre = full[:full.find(t)].rstrip()
            if pre and pre[-1] not in ".?!": bad.append("이름/대문자 " + t)
    tw = lambda t: set(re.findall(r"[a-z']+", t.lower())) - {"the", "a", "an", "to", "is", "was", "and", "in", "of", "my", "i"}
    me = tw(s)
    for x in H:
        if x.get("s") == s: bad.append("같은 문장 있음")
        elif me and len(me & tw(x["s"])) / len(me | tw(x["s"])) >= 0.55: bad.append("비슷한 문장: " + x["s"])
    return bad

if __name__ == "__main__":
    H = json.load(open(P, encoding="utf-8"))
    N = build(); errs = []
    for k, (D2, D3) in N.items():
        i2 = [i for i, x in enumerate(H) if x["k"] == k and x["lv"] == 2]; i3 = [i for i, x in enumerate(H) if x["k"] == k and x["lv"] == 3]
        assert len(i2) == 10 and len(i3) == 4, (k, len(i2), len(i3))
        keep = [x for x in H if not (x["k"] == k and x["lv"] >= 2)]
        for d in D2 + D3:
            b_ = check(d, keep)
            if b_: errs.append((k, d["s"], b_))
        for i, d in zip(i2, D2): H[i] = d
        for i, d in zip(i3, D3): H[i] = d
    for e in errs: print("BAD", e)
    if errs: sys.exit(1)
    S = [x["s"] for x in H]; mine = set(d["s"] for D2, D3 in N.values() for d in D2 + D3); dup = set(s for s in S if S.count(s) > 1 and s in mine)
    if dup: print("DUP", dup); sys.exit(1)
    if "--dry" in sys.argv: print("ok (dry)"); sys.exit(0)
    json.dump(H, open(P, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    L2 = [words(x["s"].replace("___", x["o"][0])) for x in H if x["lv"] == 2]; L3 = [words(x["s"]) for x in H if x["lv"] == 3]
    print("ok · 바꾼 것 %d · lv2 평균 %.1f단어 · lv3 평균 %.1f단어 · 전체 %d" % (sum(len(a_) + len(b_) for a_, b_ in N.values()), sum(L2) / len(L2), sum(L3) / len(L3), len(H)))
