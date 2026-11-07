# v626 문법 늘리기 ① — 빠진 문법 8개 (초3-4: There is·can·in/on/under·Let's/명령 · 초5-6: 의문사·목적격·빈도부사·want to/would like)
# 실행: python3 tools/gram_add625.py  (data/gram.json 에 같은 id 가 있으면 바꿔 씀)
import json, os, re
P = os.path.join(os.path.dirname(__file__), "..", "data", "gram.json")

def pk(s, o, a, ko, w): return {"k": "pick", "s": s, "o": o, "a": a, "ko": ko, "w": w}
def ox(s, ok, ko, fix=None):
    d = {"k": "ox", "s": s, "ok": ok, "ko": ko}
    if fix: d["fix"] = fix
    return d
def fx(s, bad, a, ko, w): return {"k": "fix", "s": s, "bad": bad, "a": a, "ko": ko, "w": w}
def od(ws, ko): return {"k": "order", "w": ws.split(" "), "ko": ko}
def rule(h, p, ex, q, x=0):
    d = {"k": "rule", "h": h, "p": p, "ex": [[e[0], "", e[1], e[2]] for e in ex], "q": q}
    if x: d["x"] = 1
    return d

NEW = {"g34": [
 {"id": "g34-9", "at": 4, "t": "There is · There are", "emo": "📦", "sub": "~이 있어요", "cards": [
   rule("하나면 There is", "하나(물·우유처럼 셀 수 없는 것도)는 There is.",
        [["🐱", "{There is} a cat on the sofa.", "소파 위에 고양이가 있어요."], ["🍎", "{There is} an apple in the box.", "상자 안에 사과가 있어요."], ["💧", "{There is} water in the cup.", "컵에 물이 있어요."]],
        pk("There ___ a dog in the park.", ["is", "are"], "is", "공원에 개가 한 마리 있어요.", "a dog = 하나 → is")),
   rule("여럿이면 There are", "두 개가 넘으면 There are.",
        [["🐦", "{There are} three birds in the tree.", "나무에 새가 세 마리 있어요."], ["📚", "{There are} many books on the desk.", "책상 위에 책이 많아요."], ["👧", "{There are} two girls in the room.", "방에 여자아이가 두 명 있어요."]],
        pk("There ___ five pencils in my bag.", ["is", "are"], "are", "내 가방에 연필이 다섯 자루 있어요.", "five pencils = 여럿 → are")),
   rule("묻고 답하기", "Is there ~? · Are there ~? → Yes, there is. / No, there aren't.",
        [["❓", "{Is there} a pool in your school?", "너희 학교에 수영장이 있니?"], ["🙆", "Yes, {there is}.", "응, 있어."], ["🍪", "{Are there} any cookies?", "쿠키 있어?"]],
        pk("___ there a bank near here?", ["Is", "Are"], "Is", "이 근처에 은행이 있나요?", "a bank = 하나 → Is"), 1)],
  "qs": [
   pk("There ___ a ball under the bed.", ["is", "are"], "is", "침대 밑에 공이 하나 있어요.", "a ball = 하나 → is"),
   pk("There ___ two cats on the roof.", ["is", "are"], "are", "지붕 위에 고양이가 두 마리 있어요.", "two cats = 여럿 → are"),
   pk("There ___ milk in the fridge.", ["is", "are"], "is", "냉장고에 우유가 있어요.", "milk 는 셀 수 없어요 → is"),
   pk("There ___ many stars in the sky.", ["is", "are"], "are", "하늘에 별이 많아요.", "many stars = 여럿 → are"),
   pk("There ___ an egg on the plate.", ["is", "are"], "is", "접시에 달걀이 하나 있어요.", "an egg = 하나 → is"),
   pk("There ___ four seasons in Korea.", ["is", "are"], "are", "한국에는 계절이 넷 있어요.", "four seasons = 여럿 → are"),
   pk("___ there a park near your house?", ["Is", "Are"], "Is", "너희 집 근처에 공원이 있니?", "a park = 하나 → Is"),
   pk("___ there any apples in the box?", ["Is", "Are"], "Are", "상자에 사과가 있니?", "apples = 여럿 → Are"),
   pk("There is a ___ on the desk.", ["book", "books"], "book", "책상 위에 책이 한 권 있어요.", "There is = 하나 → book"),
   pk("There are three ___ in the pond.", ["duck", "ducks"], "ducks", "연못에 오리가 세 마리 있어요.", "three = 여럿 → ducks"),
   pk("Is there a TV in your room? — Yes, there ___.", ["is", "are"], "is", "네 방에 TV 있어? — 응, 있어.", "Is there? → there is"),
   pk("Are there any chairs? — No, there ___.", ["isn't", "aren't"], "aren't", "의자 있어? — 아니, 없어.", "Are there? → there aren't"),
   pk("There ___ a lot of people at the zoo.", ["is", "are"], "are", "동물원에 사람이 많아요.", "people = 여러 사람 → are"),
   ox("There are a cat in the box.", False, "상자 안에 고양이가 있어요.", "There is a cat in the box."),
   ox("There is a clock on the wall.", True, "벽에 시계가 있어요."),
   ox("There is six chairs in the room.", False, "방에 의자가 여섯 개 있어요.", "There are six chairs in the room."),
   ox("Are there any eggs?", True, "달걀 있어요?"),
   fx("There is two dogs in the yard.", "is", "are", "마당에 개가 두 마리 있어요.", "two dogs = 여럿 → are"),
   fx("There are a bird in the tree.", "are", "is", "나무에 새가 한 마리 있어요.", "a bird = 하나 → is"),
   fx("Is there many toys in the box?", "Is", "Are", "상자에 장난감이 많이 있어요?", "many toys = 여럿 → Are"),
   od("There is a dog in the park.", "공원에 개가 한 마리 있어요."),
   od("There are three books on the desk.", "책상 위에 책이 세 권 있어요."),
   od("Is there a bus stop near here?", "이 근처에 버스 정류장이 있나요?")]},
 {"id": "g34-10", "at": 6, "t": "can · can't", "emo": "💪", "sub": "할 수 있어요 · 못 해요", "cards": [
   rule("할 수 있어요 = can", "can 뒤에는 원래 모양 그대로.",
        [["🏊", "I {can} swim.", "나는 수영할 수 있어요."], ["🚲", "She {can} ride a bike.", "그녀는 자전거를 탈 수 있어요."], ["🐒", "Monkeys {can} climb trees.", "원숭이는 나무를 탈 수 있어요."]],
        pk("He can ___ fast.", ["run", "runs"], "run", "그는 빨리 달릴 수 있어요.", "can 뒤 → 원래 모양")),
   rule("못 해요 = can't", "can't = can not. 뒤는 똑같이 원래 모양.",
        [["🐧", "Penguins {can't} fly.", "펭귄은 날 수 없어요."], ["🎹", "I {can't} play the piano.", "나는 피아노를 못 쳐요."], ["🐟", "Fish {can't} walk.", "물고기는 걸을 수 없어요."]],
        pk("A turtle ___ run fast.", ["can", "can't"], "can't", "거북은 빨리 달릴 수 없어요.", "거북은 느려요 → can't")),
   rule("묻고 답하기", "Can 을 맨 앞에! → Yes, I can. / No, I can't.",
        [["❓", "{Can} you swim?", "너 수영할 수 있어?"], ["🙆", "Yes, I {can}.", "응, 할 수 있어."], ["🙅", "No, I {can't}.", "아니, 못 해."]],
        pk("Can you skate? — Yes, I ___.", ["can", "can't"], "can", "스케이트 탈 수 있어? — 응, 탈 수 있어.", "Yes → can"), 1)],
  "qs": [
   pk("I can ___ English.", ["speak", "speaks"], "speak", "나는 영어를 할 수 있어요.", "can 뒤 → 원래 모양"),
   pk("Birds ___ fly.", ["can", "can't"], "can", "새는 날 수 있어요.", "새는 날아요 → can"),
   pk("Babies ___ drive a car.", ["can", "can't"], "can't", "아기는 운전을 못 해요.", "아기는 못 해요 → can't"),
   pk("She can ___ well.", ["sing", "sings"], "sing", "그녀는 노래를 잘해요.", "can 뒤 → sing"),
   pk("___ you play soccer?", ["Can", "Are"], "Can", "너 축구 할 수 있어?", "할 수 있니? → Can"),
   pk("Can he jump high? — No, he ___.", ["can", "can't"], "can't", "그는 높이 뛸 수 있어? — 아니, 못 해.", "No → can't"),
   pk("Can they swim? — Yes, they ___.", ["can", "can't"], "can", "그들은 수영할 수 있어? — 응, 할 수 있어.", "Yes → can"),
   pk("My dog can ___ the ball.", ["catch", "catches"], "catch", "우리 개는 공을 잡을 수 있어요.", "can 뒤 → catch"),
   pk("I ___ see the board. It's too far.", ["can", "can't"], "can't", "칠판이 안 보여요. 너무 멀어요.", "너무 멀어요 → can't"),
   pk("Elephants can ___ heavy things.", ["carry", "carries"], "carry", "코끼리는 무거운 것을 나를 수 있어요.", "can 뒤 → carry"),
   ox("He can swims.", False, "그는 수영할 수 있어요.", "He can swim."),
   ox("I can read this book.", True, "나는 이 책을 읽을 수 있어요."),
   ox("Can you help me?", True, "나 좀 도와줄 수 있어?"),
   ox("She cans dance.", False, "그녀는 춤을 출 수 있어요.", "She can dance."),
   fx("Tom can plays the guitar.", "plays", "play", "톰은 기타를 칠 수 있어요.", "can 뒤 → play"),
   fx("She can makes cookies.", "makes", "make", "그녀는 쿠키를 만들 수 있어요.", "can 뒤 → make"),
   fx("We can goes to the park.", "goes", "go", "우리는 공원에 갈 수 있어요.", "can 뒤 → go"),
   od("I can swim very well.", "나는 수영을 아주 잘할 수 있어요."),
   od("Can you ride a bike?", "너 자전거 탈 수 있어?"),
   od("Penguins can't fly.", "펭귄은 날 수 없어요.")]},
 {"id": "g34-11", "at": 8, "t": "in · on · under", "emo": "📍", "sub": "어디에 있어요?", "cards": [
   rule("안에 = in", "상자·방·가방 안에 있으면 in.",
        [["📦", "The cat is {in} the box.", "고양이가 상자 안에 있어요."], ["🎒", "My book is {in} my bag.", "내 책은 가방 안에 있어요."], ["🐟", "The fish is {in} the water.", "물고기가 물속에 있어요."]],
        pk("The pencil is ___ the pencil case.", ["in", "under"], "in", "연필은 필통 안에 있어요.", "필통 안 → in")),
   rule("위에 = on", "위에 닿아 있거나 벽에 붙어 있으면 on.",
        [["📚", "The book is {on} the desk.", "책이 책상 위에 있어요."], ["🖼️", "The picture is {on} the wall.", "그림이 벽에 걸려 있어요."], ["🧢", "The cap is {on} his head.", "모자가 그의 머리 위에 있어요."]],
        pk("The cup is ___ the table.", ["on", "in"], "on", "컵이 탁자 위에 있어요.", "탁자 위 → on")),
   rule("아래에 = under", "밑에 있으면 under.",
        [["⚽", "The ball is {under} the bed.", "공이 침대 밑에 있어요."], ["🐶", "The dog is {under} the table.", "개가 탁자 밑에 있어요."], ["☂️", "We are {under} the umbrella.", "우리는 우산 밑에 있어요."]],
        pk("My shoes are ___ the chair.", ["under", "in"], "under", "내 신발은 의자 밑에 있어요.", "의자 밑 → under")),
   rule("어디 있어? = Where is ~?", "Where is my bag? → It's on the chair.",
        [["❓", "{Where} is my bag?", "내 가방 어디 있어?"], ["🪑", "It's {on} the chair.", "의자 위에 있어."]],
        pk("Where ___ my shoes? — They're under the bed.", ["is", "are"], "are", "내 신발 어디 있어? — 침대 밑에 있어.", "shoes = 여럿 → are"), 1)],
  "qs": [
   pk("The milk is ___ the fridge.", ["in", "on", "under"], "in", "우유는 냉장고 안에 있어요.", "냉장고 안 → in"),
   pk("The cat is sleeping ___ the sofa.", ["on", "in", "under"], "on", "고양이가 소파 위에서 자요.", "소파 위 → on"),
   pk("The bird is ___ the cage.", ["in", "on", "under"], "in", "새가 새장 안에 있어요.", "새장 안 → in"),
   pk("There is a mouse ___ the table.", ["under", "in", "on"], "under", "탁자 밑에 쥐가 있어요.", "탁자 밑 → under"),
   pk("The clock is ___ the wall.", ["on", "in", "under"], "on", "시계가 벽에 걸려 있어요.", "벽에 붙어 있어요 → on"),
   pk("My socks are ___ the drawer.", ["in", "on", "under"], "in", "내 양말은 서랍 안에 있어요.", "서랍 안 → in"),
   pk("The kids are swimming ___ the pool.", ["in", "on", "under"], "in", "아이들이 수영장에서 수영해요.", "물속 → in"),
   pk("The cat is hiding ___ the blanket.", ["under", "on", "in"], "under", "고양이가 담요 밑에 숨어 있어요.", "담요 밑 → under"),
   pk("Put your plate ___ the table, please.", ["on", "in", "under"], "on", "접시를 탁자 위에 놓아 주세요.", "탁자 위 → on"),
   pk("Where is my pen? — It's ___ your hand!", ["in", "on", "under"], "in", "내 펜 어디 있어? — 네 손안에 있잖아!", "손안 → in"),
   ox("The book is on the desk.", True, "책이 책상 위에 있어요."),
   ox("The fish is on the water.", False, "물고기가 물속에 있어요.", "The fish is in the water."),
   ox("The ball is under the chair.", True, "공이 의자 밑에 있어요."),
   fx("The apples are on the basket.", "on", "in", "사과들이 바구니 안에 있어요.", "바구니 안 → in"),
   fx("My cap is in my head.", "in", "on", "내 모자는 머리 위에 있어요.", "머리 위 → on"),
   od("The cat is under the table.", "고양이가 탁자 밑에 있어요."),
   od("My book is in my bag.", "내 책은 가방 안에 있어요."),
   od("Where is my pencil?", "내 연필 어디 있어?")]},
 {"id": "g34-12", "at": 10, "t": "Let's · 하세요 · Don't", "emo": "📣", "sub": "~하자 · ~해요 · ~하지 마요", "cards": [
   rule("~하자 = Let's + 원래 모양", "같이 하자고 할 때 Let's. 뒤에는 원래 모양.",
        [["⚽", "{Let's} play soccer.", "축구 하자."], ["🍕", "{Let's} eat pizza.", "피자 먹자."], ["🏠", "{Let's} go home.", "집에 가자."]],
        pk("Let's ___ together.", ["sing", "sings"], "sing", "같이 노래하자.", "Let's 뒤 → 원래 모양")),
   rule("~해요 = 원래 모양으로 시작", "시킬 때는 주어 없이 동사부터. please 를 붙이면 더 공손해요.",
        [["🪑", "{Sit} down, please.", "앉아 주세요."], ["👂", "{Listen} to me.", "내 말을 들어 봐."], ["🚪", "{Open} the door.", "문을 열어요."]],
        pk("___ your hands, please.", ["Wash", "Washes"], "Wash", "손을 씻으세요.", "시키는 말 → 원래 모양으로 시작")),
   rule("~하지 마요 = Don't", "하지 말라고 할 때 Don't + 원래 모양.",
        [["🏃", "{Don't} run in the hall.", "복도에서 뛰지 마요."], ["🔊", "{Don't} be loud.", "시끄럽게 하지 마요."], ["🍬", "{Don't} eat too much candy.", "사탕을 너무 많이 먹지 마요."]],
        pk("___ touch the stove! It's hot.", ["Don't", "Let's"], "Don't", "난로 만지지 마! 뜨거워.", "하지 말라 → Don't"), 1)],
  "qs": [
   pk("Let's ___ to the park.", ["go", "goes"], "go", "공원에 가자.", "Let's 뒤 → 원래 모양"),
   pk("It's raining. ___ take an umbrella.", ["Let's", "Don't"], "Let's", "비가 와. 우산 가져가자.", "같이 하자 → Let's"),
   pk("___ quiet in the library.", ["Be", "Is"], "Be", "도서관에서는 조용히 하세요.", "시키는 말 → Be"),
   pk("Don't ___ late for school.", ["be", "is"], "be", "학교에 늦지 마요.", "Don't 뒤 → be"),
   pk("___ your name here.", ["Write", "Writes"], "Write", "여기에 이름을 쓰세요.", "시키는 말 → 원래 모양"),
   pk("The floor is wet. ___ run!", ["Don't", "Let's"], "Don't", "바닥이 젖었어. 뛰지 마!", "위험해요 → Don't"),
   pk("I'm hungry. — ___ have lunch.", ["Let's", "Don't"], "Let's", "배고파. — 점심 먹자.", "같이 하자 → Let's"),
   pk("Please ___ the window.", ["close", "closes"], "close", "창문 좀 닫아 주세요.", "시키는 말 → 원래 모양"),
   pk("Don't ___ in class.", ["talk", "talks"], "talk", "수업 시간에 떠들지 마요.", "Don't 뒤 → 원래 모양"),
   pk("Let's ___ a picture.", ["take", "takes"], "take", "사진 찍자.", "Let's 뒤 → 원래 모양"),
   ox("Let's plays a game.", False, "게임 하자.", "Let's play a game."),
   ox("Don't touch the cake.", True, "케이크 만지지 마요."),
   ox("Opens your book.", False, "책을 펴요.", "Open your book."),
   ox("Let's go to the beach.", True, "바닷가에 가자."),
   fx("Let's watches a movie.", "watches", "watch", "영화 보자.", "Let's 뒤 → watch"),
   fx("Don't runs on the stairs.", "runs", "run", "계단에서 뛰지 마요.", "Don't 뒤 → run"),
   fx("Sits down, please.", "Sits", "Sit", "앉아 주세요.", "시키는 말 → Sit"),
   od("Let's play outside.", "밖에서 놀자."),
   od("Don't run in the hall.", "복도에서 뛰지 마요."),
   od("Please close the door.", "문을 닫아 주세요.")]}],
"g56": [
 {"id": "g56-9", "at": 3, "t": "What · Where · When · Who", "emo": "❓", "sub": "무엇·어디·언제·누구·왜·어떻게", "cards": [
   rule("무엇 = What · 누구 = Who", "물건·하는 일은 What, 사람은 Who.",
        [["🍎", "{What} is this?", "이것은 뭐예요?"], ["🎨", "{What} do you like?", "너는 뭘 좋아해?"], ["👩", "{Who} is she?", "그녀는 누구예요?"]],
        pk("___ is your teacher? — Ms. Kim.", ["Who", "What"], "Who", "너희 선생님은 누구야? — 김 선생님이야.", "사람 → Who")),
   rule("어디 = Where · 언제 = When", "장소는 Where, 때는 When.",
        [["🏠", "{Where} do you live?", "너는 어디 살아?"], ["🎂", "{When} is your birthday?", "네 생일은 언제야?"], ["🏫", "{When} does school start?", "학교는 언제 시작해?"]],
        pk("___ is the library? — It's next to the gym.", ["Where", "When"], "Where", "도서관은 어디예요? — 체육관 옆이에요.", "장소 → Where")),
   rule("왜 = Why · 어떻게 = How", "이유는 Why (대답은 Because ~), 방법·상태는 How.",
        [["😢", "{Why} are you sad?", "왜 슬퍼?"], ["🚌", "{How} do you go to school?", "학교에 어떻게 가?"], ["🙂", "{How} are you?", "어떻게 지내?"]],
        pk("___ do you go to school? — By bus.", ["How", "Why"], "How", "학교에 어떻게 가? — 버스로.", "방법 → How")),
   rule("대답을 보고 골라요", "대답이 장소면 Where, 시간이면 When, 사람이면 Who.",
        [["⏰", "{When} do you get up? — At seven.", "언제 일어나? — 7시에."], ["📍", "{Where} is my phone? — On the sofa.", "내 폰 어디 있어? — 소파 위에."]],
        pk("___ do you eat lunch? — At 12:30.", ["When", "Where"], "When", "점심은 언제 먹어? — 12시 30분에.", "시간 → When"), 1)],
  "qs": [
   pk("___ is your favorite color? — Blue.", ["What", "Who"], "What", "가장 좋아하는 색이 뭐야? — 파란색.", "색 → What"),
   pk("___ is that boy? — He's my brother.", ["Who", "Where"], "Who", "저 남자아이는 누구야? — 내 남동생이야.", "사람 → Who"),
   pk("___ are you going? — To the park.", ["Where", "When"], "Where", "어디 가? — 공원에.", "장소 → Where"),
   pk("___ is the concert? — On Saturday.", ["When", "Where"], "When", "콘서트는 언제야? — 토요일이야.", "때 → When"),
   pk("___ are you late? — Because I missed the bus.", ["Why", "How"], "Why", "왜 늦었어? — 버스를 놓쳤거든.", "Because → Why"),
   pk("___ old are you? — I'm twelve.", ["How", "What"], "How", "몇 살이야? — 열두 살이야.", "How old = 몇 살"),
   pk("___ do you do after school? — I play soccer.", ["What", "Where"], "What", "방과 후에 뭐 해? — 축구 해.", "하는 일 → What"),
   pk("___ is your birthday? — It's May 5th.", ["When", "Who"], "When", "네 생일은 언제야? — 5월 5일이야.", "날짜 → When"),
   pk("___ many apples do you have?", ["How", "What"], "How", "사과가 몇 개 있어?", "How many = 몇 개"),
   pk("___ is my bag? — It's under the desk.", ["Where", "Why"], "Where", "내 가방 어디 있어? — 책상 밑에.", "장소 → Where"),
   pk("___ made this cake? — My mom did.", ["Who", "What"], "Who", "이 케이크 누가 만들었어? — 우리 엄마가.", "누가 → Who"),
   pk("___ is the weather today? — It's sunny.", ["How", "Who"], "How", "오늘 날씨 어때? — 맑아.", "상태 → How"),
   ox("Where do you live?", True, "너는 어디 살아?"),
   ox("Who is your name?", False, "네 이름이 뭐야?", "What is your name?"),
   ox("When is your birthday?", True, "네 생일은 언제야?"),
   ox("How are you sad?", False, "왜 슬퍼?", "Why are you sad?"),
   fx("Where is your birthday? — It's in May.", "Where", "When", "네 생일은 언제야? — 5월이야.", "때 → When"),
   fx("What is that girl? — She's my sister.", "What", "Who", "저 여자아이는 누구야? — 내 여동생이야.", "사람 → Who"),
   fx("When do you live? — In Seoul.", "When", "Where", "어디 살아? — 서울에.", "장소 → Where"),
   od("Where do you live?", "너는 어디 살아?"),
   od("What do you want for lunch?", "점심으로 뭐 먹고 싶어?"),
   od("When does the movie start?", "영화는 언제 시작해?")]},
 {"id": "g56-10", "at": 7, "t": "me · him · her · them", "emo": "👉", "sub": "~을 · ~에게", "cards": [
   rule("~을 · ~에게 = me · you · him · her", "동사 뒤에 오는 사람은 모양이 바뀌어요. I → me, he → him, she → her.",
        [["🤗", "My mom loves {me}.", "엄마는 나를 사랑해요."], ["📞", "I called {him} yesterday.", "나는 어제 그에게 전화했어요."], ["🎁", "We gave {her} a gift.", "우리는 그녀에게 선물을 줬어요."]],
        pk("Can you help ___?", ["me", "I"], "me", "나 좀 도와줄래?", "help 뒤 → me")),
   rule("여럿 = us · them · 물건 하나 = it", "we → us, they → them, 물건 하나는 it.",
        [["👨‍🏫", "Our teacher helps {us}.", "선생님은 우리를 도와주세요."], ["🐶", "I like dogs. I play with {them}.", "나는 개를 좋아해. 개들이랑 놀아."], ["🍪", "This cookie is good. Try {it}!", "이 쿠키 맛있어. 먹어 봐!"]],
        pk("I have two cats. I love ___.", ["them", "they"], "them", "고양이가 두 마리 있어. 걔들을 사랑해.", "love 뒤 → them")),
   rule("with · for · to 뒤에도", "with · for · to 뒤에도 me · him · her · them.",
        [["⚽", "Play with {us}!", "우리랑 놀자!"], ["🎂", "This cake is for {you}.", "이 케이크는 너를 위한 거야."], ["✉️", "I wrote a letter to {her}.", "나는 그녀에게 편지를 썼어요."]],
        pk("Come with ___!", ["we", "us"], "us", "우리랑 같이 가자!", "with 뒤 → us"), 1)],
  "qs": [
   pk("Tom is my friend. I like ___.", ["him", "he"], "him", "톰은 내 친구야. 나는 그를 좋아해.", "like 뒤 → him"),
   pk("Mina is kind. Everyone loves ___.", ["her", "she"], "her", "미나는 친절해. 모두 그녀를 좋아해.", "loves 뒤 → her"),
   pk("Where are my glasses? I can't find ___.", ["them", "it"], "them", "내 안경 어디 있지? 못 찾겠어.", "glasses = 여럿 → them"),
   pk("This book is fun. Read ___!", ["it", "them"], "it", "이 책 재밌어. 읽어 봐!", "책 한 권 → it"),
   pk("Please tell ___ the answer.", ["me", "I"], "me", "나에게 답을 알려 줘.", "tell 뒤 → me"),
   pk("We are lost. Can you help ___?", ["us", "we"], "us", "우리 길을 잃었어요. 도와줄 수 있나요?", "help 뒤 → us"),
   pk("My grandparents live in Busan. I visit ___ every summer.", ["them", "they"], "them", "할아버지 할머니는 부산에 사셔. 나는 여름마다 찾아뵈어.", "visit 뒤 → them"),
   pk("___ like pizza.", ["I", "Me"], "I", "나는 피자를 좋아해.", "문장 맨 앞(누가) → I"),
   pk("Jiho is my brother. ___ is ten.", ["He", "Him"], "He", "지호는 내 남동생이야. 그는 열 살이야.", "문장 맨 앞(누가) → He"),
   pk("I made this for ___, Mom!", ["you", "your"], "you", "엄마, 이거 엄마 주려고 만들었어요!", "for 뒤 → you"),
   ox("She helps I with my homework.", False, "그녀는 내 숙제를 도와줘요.", "She helps me with my homework."),
   ox("I miss them a lot.", True, "나는 그들이 많이 보고 싶어요."),
   ox("Look at he!", False, "그를 봐!", "Look at him!"),
   ox("Our teacher likes us.", True, "선생님은 우리를 좋아하세요."),
   fx("Can you call she tonight?", "she", "her", "오늘 밤 그녀에게 전화할 수 있어?", "call 뒤 → her"),
   fx("I see they every day.", "they", "them", "나는 그들을 매일 봐요.", "see 뒤 → them"),
   fx("Dad took we to the zoo.", "we", "us", "아빠가 우리를 동물원에 데려가셨어요.", "took 뒤 → us"),
   od("My mom loves me.", "엄마는 나를 사랑해요."),
   od("I play with them after school.", "나는 방과 후에 그들과 놀아요."),
   od("Can you help us?", "우리를 도와줄 수 있어요?")]},
 {"id": "g56-11", "at": 12, "t": "always · usually · never", "emo": "🔁", "sub": "얼마나 자주", "cards": [
   rule("얼마나 자주?", "always 늘 → usually 보통 → often 자주 → sometimes 가끔 → never 절대 안.",
        [["🦷", "I {always} brush my teeth.", "나는 항상 이를 닦아요."], ["🚌", "She {usually} takes the bus.", "그녀는 보통 버스를 타요."], ["🍔", "We {sometimes} eat burgers.", "우리는 가끔 햄버거를 먹어요."], ["🥦", "He {never} eats broccoli.", "그는 브로콜리를 절대 안 먹어요."]],
        pk("I eat breakfast every day. I ___ eat breakfast.", ["always", "never"], "always", "나는 매일 아침을 먹어요. 항상 먹어요.", "매일 → always")),
   rule("자리 = 하는 말(동사) 앞", "일반 동사 앞에 와요: I often play ~.",
        [["⚽", "I {often} play soccer.", "나는 자주 축구를 해요."], ["📚", "Mina {usually} reads at night.", "미나는 보통 밤에 책을 읽어요."]],
        pk("We ___ go to the beach in summer.", ["often", "every"], "often", "우리는 여름에 자주 바닷가에 가요.", "자주 → often (go 앞)")),
   rule("am · is · are 는 뒤에", "be동사(am · is · are) 뒤에 와요: I am always happy.",
        [["😊", "I am {always} happy.", "나는 항상 행복해요."], ["⏰", "He is {never} late.", "그는 절대 늦지 않아요."]],
        pk("He is ___ busy on Mondays.", ["always", "every"], "always", "그는 월요일에 항상 바빠요.", "is 뒤 → always"), 1)],
  "qs": [
   pk("I brush my teeth every night. I ___ brush my teeth.", ["always", "never"], "always", "나는 매일 밤 이를 닦아요.", "매일 → always"),
   pk("He doesn't like fish. He ___ eats fish.", ["never", "always"], "never", "그는 생선을 싫어해. 생선을 절대 안 먹어.", "싫어해요 → never"),
   pk("We go swimming once a month. We ___ go swimming.", ["sometimes", "always"], "sometimes", "우리는 한 달에 한 번 수영하러 가요.", "한 달에 한 번 → sometimes"),
   pk("Jiho plays games almost every day. He ___ plays games.", ["usually", "never"], "usually", "지호는 거의 매일 게임을 해요.", "거의 매일 → usually"),
   pk("She is ___ happy. She smiles all the time.", ["always", "never"], "always", "그녀는 항상 행복해. 늘 웃어.", "늘 → always"),
   pk("I ___ walk to school, but today I took the bus.", ["usually", "never"], "usually", "나는 보통 걸어서 학교에 가는데, 오늘은 버스를 탔어.", "보통 → usually"),
   pk("My dad ___ cooks on Sundays. It's his day!", ["always", "never"], "always", "아빠는 일요일엔 항상 요리하셔. 아빠의 날이야!", "항상 → always"),
   pk("I don't like scary movies. I ___ watch them.", ["never", "often"], "never", "나는 무서운 영화가 싫어. 절대 안 봐.", "싫어요 → never"),
   pk("Amy ___ goes to the library. She loves books.", ["often", "never"], "often", "에이미는 자주 도서관에 가. 책을 아주 좋아하거든.", "좋아해요 → often"),
   pk("How often do you exercise? — I ___ exercise. Maybe twice a week.", ["sometimes", "never"], "sometimes", "얼마나 자주 운동해? — 가끔. 일주일에 두 번쯤.", "두 번쯤 → sometimes"),
   ox("I always eat breakfast.", True, "나는 항상 아침을 먹어요."),
   ox("She goes often to the park.", False, "그녀는 자주 공원에 가요.", "She often goes to the park."),
   ox("He is usually busy.", True, "그는 보통 바빠요."),
   ox("We never are late.", False, "우리는 절대 늦지 않아요.", "We are never late."),
   fx("I love ice cream. I never eat it in summer.", "never", "often", "나는 아이스크림이 좋아. 여름엔 자주 먹어.", "좋아해요 → often"),
   fx("Mina hates carrots. She always eats them.", "always", "never", "미나는 당근을 싫어해. 절대 안 먹어.", "싫어해요 → never"),
   od("I always get up at seven.", "나는 항상 7시에 일어나요."),
   od("She is never late for school.", "그녀는 절대 학교에 늦지 않아요."),
   od("We sometimes play badminton.", "우리는 가끔 배드민턴을 쳐요.")]},
 {"id": "g56-12", "at": 15, "t": "want to · would like", "emo": "🙏", "sub": "하고 싶어요 · 주세요", "cards": [
   rule("~하고 싶어 = want to + 원래 모양", "want to 뒤에는 원래 모양.",
        [["🎢", "I {want to} ride the roller coaster.", "롤러코스터 타고 싶어."], ["🏖️", "She {wants to} go to the beach.", "그녀는 바닷가에 가고 싶어 해요."], ["🍜", "Do you {want to} eat ramen?", "라면 먹고 싶어?"]],
        pk("I want to ___ a doctor.", ["be", "am"], "be", "나는 의사가 되고 싶어요.", "want to 뒤 → 원래 모양")),
   rule("공손하게 = would like", "I'd like ~ = ~ 주세요. I'd like to ~ = ~하고 싶어요. Would you like ~? = ~ 드릴까요?",
        [["🍕", "{I'd like} a cheese pizza, please.", "치즈 피자 주세요."], ["🧃", "{Would you like} some juice?", "주스 좀 드릴까요?"], ["🎨", "{I'd like to} join the art club.", "미술 동아리에 들고 싶어요."]],
        pk("___ you like some water? — Yes, please.", ["Would", "Do"], "Would", "물 좀 드릴까요? — 네, 주세요.", "공손하게 → Would")),
   rule("he · she 는 wants", "he · she · 이름 하나 → wants to.",
        [["⚽", "He {wants to} play soccer.", "그는 축구를 하고 싶어 해요."], ["🐱", "Mina {wants} a cat.", "미나는 고양이를 갖고 싶어 해요."]],
        pk("She ___ to learn Chinese.", ["wants", "want"], "wants", "그녀는 중국어를 배우고 싶어 해요.", "she → wants"), 1)],
  "qs": [
   pk("I want to ___ a new bike.", ["buy", "buys"], "buy", "나는 새 자전거를 사고 싶어요.", "want to 뒤 → 원래 모양"),
   pk("He ___ to be a scientist.", ["wants", "want"], "wants", "그는 과학자가 되고 싶어 해요.", "he → wants"),
   pk("Do you want ___ play with me?", ["to", "for"], "to", "나랑 놀고 싶어?", "want to + 원래 모양"),
   pk("I'd like ___ order, please.", ["to", "for"], "to", "주문하고 싶어요.", "I'd like to + 원래 모양"),
   pk("May I take your order? — I'd ___ a hamburger, please.", ["like", "want to"], "like", "주문하시겠어요? — 햄버거 주세요.", "I'd like + 물건"),
   pk("What do you want to ___ for your birthday?", ["get", "gets"], "get", "생일에 뭐 받고 싶어?", "want to 뒤 → 원래 모양"),
   pk("They want to ___ the museum.", ["visit", "visits"], "visit", "그들은 박물관에 가 보고 싶어 해요.", "want to 뒤 → 원래 모양"),
   pk("___ you like to come to my party? — Sure!", ["Would", "Are"], "Would", "내 파티에 올래? — 좋아!", "초대할 때 → Would you like to"),
   pk("My sister ___ a puppy for Christmas.", ["wants", "want"], "wants", "언니는 크리스마스에 강아지를 갖고 싶어 해요.", "sister 한 명 → wants"),
   pk("I'd like ___ hot chocolate, please.", ["a", "an"], "a", "핫초코 한 잔 주세요.", "hot 은 '하' 소리 → a"),
   ox("I want to go home.", True, "나는 집에 가고 싶어요."),
   ox("She want to swim.", False, "그녀는 수영하고 싶어 해요.", "She wants to swim."),
   ox("Would you like some tea?", True, "차 좀 드릴까요?"),
   ox("I want to plays outside.", False, "나는 밖에서 놀고 싶어요.", "I want to play outside."),
   fx("He want to be a pilot.", "want", "wants", "그는 비행기 조종사가 되고 싶어 해요.", "he → wants"),
   fx("I'd like to eats pasta.", "eats", "eat", "파스타 먹고 싶어요.", "to 뒤 → eat"),
   fx("Do you want to goes shopping?", "goes", "go", "쇼핑 가고 싶어?", "to 뒤 → go"),
   od("I want to be a teacher.", "나는 선생님이 되고 싶어요."),
   od("I'd like a glass of milk.", "우유 한 잔 주세요."),
   od("Would you like to come?", "올래요?")]}]}

def check(g):
    bad = []
    allq = g["qs"] + [c["q"] for c in g["cards"]]
    for q in allq:
        if q["k"] == "pick":
            if q["a"] not in q["o"]: bad.append(("a not in o", q["s"]))
            if q["s"].count("___") != 1: bad.append(("blank", q["s"]))
        if q["k"] == "fix":
            toks = [t.strip(".,!?") for t in q["s"].split(" ")]
            if toks.count(q["bad"]) != 1: bad.append(("fix tok", q["s"]))
        if q["k"] == "ox" and not q["ok"] and not q.get("fix"): bad.append(("ox fix", q["s"]))
    for c in g["cards"]:
        for e in c["ex"]:
            if not re.search(r"\{[^}]+\}", e[2]): bad.append(("no hl", e[2]))
    return bad

G = json.load(open(P))
raw = open(P).read()
for bk, L in NEW.items():
    for g in L:
        b = check(g)
        assert not b, (g["id"], b)
        G[bk] = [x for x in G[bk] if x["id"] != g["id"]] + [g]
    G[bk].sort(key=lambda x: (x["at"], x["id"]))
compact = "\n" not in raw.strip()[:2000]
open(P, "w").write(json.dumps(G, ensure_ascii=False, separators=(",", ":")) if compact else json.dumps(G, ensure_ascii=False, indent=1))
for bk in NEW: print(bk, [(g["id"], g["at"], len(g["qs"])) for g in G[bk]])
