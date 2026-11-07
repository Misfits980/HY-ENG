# v626 문법 늘리기 ③ — 중등 문법 중 문제 은행이 없던 7가지(동명사·현재완료·수동태·관계대명사·이어 주는 말·기간·to부정사)에 15문제씩
# lv 0 (쉬운 것) 만 → 🔀 섞어 풀기에만 쓰임 (심화 도전·Stage 문법은 그대로) · 끝에 덧붙여 기존 번호(본 문제 기록) 유지
import json, os
P = os.path.join(os.path.dirname(__file__), "..", "data", "hsq.json")
def q(k, s, o, ko, why, w=None):
    d = {"k": k, "lv": 0, "s": s, "o": o, "ko": ko, "why": why}
    if w: d["w"] = w
    return d

NEW = [
# 동명사 ger
q("ger", "I enjoy ___ comic books.", ["reading", "to read", "read"], "나는 만화책 읽는 걸 좋아해요.", "enjoy 뒤 → -ing", {"to read": "enjoy 뒤에는 to 가 못 와요"}),
q("ger", "Please stop ___ so loudly.", ["talking", "talk", "talked"], "그렇게 시끄럽게 떠들지 좀 마.", "stop(그만두다) 뒤 → -ing"),
q("ger", "He finished ___ his room.", ["cleaning", "to clean", "clean"], "그는 방 청소를 끝냈어요.", "finish 뒤 → -ing", {"to clean": "finish 뒤에는 to 가 못 와요"}),
q("ger", "Mina is good at ___.", ["drawing", "draw", "to draw"], "미나는 그림을 잘 그려요.", "전치사 at 뒤 → -ing", {"draw": "at 같은 전치사 뒤에는 동사원형이 못 와요"}),
q("ger", "___ vegetables is good for you.", ["Eating", "Eat", "Ate"], "채소를 먹는 것은 몸에 좋아요.", "문장 맨 앞 '~하는 것' → -ing", {"Eat": "Eat 으로 시작하면 '먹어라'가 돼요"}),
q("ger", "Thank you for ___ me.", ["helping", "help", "helped"], "도와줘서 고마워.", "for 뒤 → -ing"),
q("ger", "My hobby is ___ stamps.", ["collecting", "collect", "collected"], "내 취미는 우표 모으기예요.", "is 뒤 '~하는 것' → -ing"),
q("ger", "Do you mind ___ the window?", ["opening", "to open", "open"], "창문 좀 열어도 될까요?", "mind 뒤 → -ing", {"to open": "mind 뒤에는 to 가 못 와요"}),
q("ger", "Keep ___. You can do it!", ["trying", "try", "tried"], "계속 해 봐. 할 수 있어!", "keep(계속하다) 뒤 → -ing"),
q("ger", "I'm sorry for ___ late.", ["being", "be", "am"], "늦어서 미안해.", "for 뒤 → be 도 being"),
q("ger", "She practices ___ the piano every day.", ["playing", "to play", "plays"], "그녀는 매일 피아노 치는 연습을 해요.", "practice 뒤 → -ing"),
q("ger", "We talked about ___ a trip.", ["taking", "take", "took"], "우리는 여행 가는 것에 대해 이야기했어요.", "about 뒤 → -ing"),
q("ger", "Swimming in the sea ___ fun.", ["is", "are", "am"], "바다에서 수영하는 것은 재미있어요.", "-ing 로 시작하는 주어 = 하나 → is", {"are": "Swimming ~ 은 한 가지 일이라 are 가 아니에요"}),
q("ger", "How about ___ a movie tonight?", ["watching", "watch", "to watch"], "오늘 밤 영화 보는 거 어때?", "How about 뒤 → -ing"),
q("ger", "He gave up ___ sweets.", ["eating", "to eat", "eat"], "그는 단것 먹기를 그만뒀어요.", "give up 뒤 → -ing"),
# 현재완료 perf
q("perf", "I have ___ my homework.", ["finished", "finish", "finishing"], "나는 숙제를 끝냈어요.", "have + 과거분사"),
q("perf", "She ___ lived in Seoul for five years.", ["has", "have", "is"], "그녀는 5년 동안 서울에 살아 왔어요.", "she → has + 과거분사", {"have": "she 는 has 를 써요"}),
q("perf", "Have you ever ___ a panda?", ["seen", "saw", "see"], "판다 본 적 있어?", "Have + 과거분사 seen", {"saw": "saw 는 과거형 — have 뒤는 seen"}),
q("perf", "We have known each other ___ 2020.", ["since", "for", "ago"], "우리는 2020년부터 서로 알고 지냈어요.", "시작한 때 → since", {"for": "for 뒤에는 '얼마 동안'(기간)이 와요"}),
q("perf", "He has been sick ___ three days.", ["for", "since", "ago"], "그는 사흘째 아파요.", "기간 → for", {"since": "since 뒤에는 시작한 때가 와요"}),
q("perf", "I have never ___ sushi.", ["eaten", "ate", "eat"], "나는 초밥을 먹어 본 적이 없어요.", "have + 과거분사 eaten"),
q("perf", "They have just ___ home.", ["arrived", "arrive", "arriving"], "그들은 막 집에 도착했어요.", "have just + 과거분사"),
q("perf", "Has he ___ his phone?", ["found", "find", "finded"], "그가 휴대폰을 찾았어?", "find → found"),
q("perf", "I ___ to Jeju three times.", ["have been", "have be", "am been"], "나는 제주에 세 번 가 봤어요.", "가 본 적 = have been"),
q("perf", "She has ___ a letter to her friend.", ["written", "wrote", "write"], "그녀는 친구에게 편지를 썼어요.", "write → written"),
q("perf", "We ___ seen that movie yet.", ["haven't", "didn't", "aren't"], "우리는 아직 그 영화를 못 봤어요.", "yet + 현재완료 부정 → haven't"),
q("perf", "My dad has ___ his car.", ["washed", "wash", "washing"], "아빠는 세차를 하셨어요.", "has + 과거분사"),
q("perf", "Have you finished lunch? — Yes, I ___.", ["have", "do", "am"], "점심 다 먹었어? — 응.", "Have ~? → I have"),
q("perf", "It has rained ___ morning.", ["since", "for", "during"], "아침부터 비가 왔어요.", "시작한 때(아침) → since"),
q("perf", "I have ___ my key. I can't open the door.", ["lost", "lose", "losing"], "열쇠를 잃어버렸어. 문을 못 열어.", "lose → lost"),
# 수동태 pass
q("pass", "This cake was ___ by my mom.", ["made", "make", "making"], "이 케이크는 엄마가 만드셨어요.", "was + 과거분사"),
q("pass", "English is ___ in many countries.", ["spoken", "spoke", "speak"], "영어는 많은 나라에서 쓰여요.", "is + 과거분사 spoken", {"spoke": "spoke 는 과거형 — is 뒤는 spoken"}),
q("pass", "The window was broken ___ the ball.", ["by", "of", "to"], "창문이 공에 깨졌어요.", "누가·무엇이 했는지 → by"),
q("pass", "The letters ___ sent yesterday.", ["were", "was", "are"], "편지들은 어제 보내졌어요.", "letters(여럿) + 어제 → were"),
q("pass", "This song is loved ___ many people.", ["by", "with", "for"], "이 노래는 많은 사람들에게 사랑받아요.", "~에 의해 → by"),
q("pass", "The room is ___ every day.", ["cleaned", "clean", "cleaning"], "그 방은 매일 청소돼요.", "is + 과거분사"),
q("pass", "The bridge was ___ in 1990.", ["built", "build", "builded"], "그 다리는 1990년에 지어졌어요.", "build → built"),
q("pass", "The thief was ___ by the police.", ["caught", "catched", "catch"], "도둑은 경찰에게 잡혔어요.", "catch → caught"),
q("pass", "Many stars can ___ seen at night.", ["be", "is", "are"], "밤에는 별이 많이 보여요.", "can 뒤 → be + 과거분사"),
q("pass", "The door ___ opened by Tom.", ["was", "were", "did"], "문은 톰이 열었어요.", "door 하나 + 지난 일 → was"),
q("pass", "This book was ___ by a famous writer.", ["written", "wrote", "writing"], "이 책은 유명한 작가가 썼어요.", "write → written"),
q("pass", "Rice is ___ in Korea.", ["grown", "grew", "grow"], "한국에서는 쌀이 재배돼요.", "grow → grown"),
q("pass", "The toys ___ made in China.", ["are", "is", "do"], "그 장난감들은 중국에서 만들어져요.", "toys(여럿) → are"),
q("pass", "Was the dog ___ by the kids?", ["found", "find", "founded"], "그 개는 아이들이 찾았어?", "find → found", {"founded": "founded 는 '세우다(found)'의 과거분사예요"}),
q("pass", "The game will ___ played tomorrow.", ["be", "is", "been"], "그 경기는 내일 열려요.", "will 뒤 → be + 과거분사"),
# 관계대명사 rel
q("rel", "I have a friend ___ lives in Busan.", ["who", "which", "where"], "나는 부산에 사는 친구가 있어요.", "사람 → who", {"which": "which 는 사물·동물에 써요"}),
q("rel", "This is the book ___ I bought yesterday.", ["which", "who", "where"], "이건 내가 어제 산 책이에요.", "사물 → which", {"who": "who 는 사람에 써요"}),
q("rel", "The girl ___ is singing is my sister.", ["who", "which", "what"], "노래하고 있는 소녀는 내 동생이에요.", "사람 → who"),
q("rel", "I like the dog ___ has long ears.", ["which", "who", "when"], "나는 귀가 긴 그 개가 좋아요.", "동물 → which"),
q("rel", "He is the teacher ___ helped me.", ["who", "which", "whose"], "그분이 나를 도와주신 선생님이에요.", "사람 → who"),
q("rel", "The cake ___ Mom made was delicious.", ["that", "who", "where"], "엄마가 만드신 케이크는 맛있었어요.", "사물 → that(=which)도 돼요"),
q("rel", "I know a boy ___ father is a pilot.", ["whose", "who", "which"], "나는 아빠가 조종사인 남자아이를 알아요.", "~의 아빠 → whose", {"who": "뒤에 father 가 바로 오면 '누구의' = whose"}),
q("rel", "Do you see the bus ___ goes to the zoo?", ["that", "who", "what"], "동물원 가는 버스 보여?", "사물 → that"),
q("rel", "She has a cat ___ eyes are blue.", ["whose", "which", "who"], "그녀는 눈이 파란 고양이가 있어요.", "그 고양이의 눈 → whose"),
q("rel", "The man ___ I met was kind.", ["who", "which", "where"], "내가 만난 그 남자는 친절했어요.", "사람 → who"),
q("rel", "This is the phone ___ my dad gave me.", ["that", "who", "whose"], "이건 아빠가 주신 휴대폰이에요.", "사물 → that"),
q("rel", "I want a robot ___ can clean my room.", ["which", "who", "where"], "내 방을 청소해 주는 로봇을 갖고 싶어요.", "사물 → which"),
q("rel", "Students ___ study hard get good grades.", ["who", "which", "what"], "열심히 공부하는 학생들은 좋은 성적을 받아요.", "사람 → who"),
q("rel", "The movie ___ we watched was scary.", ["which", "who", "whose"], "우리가 본 영화는 무서웠어요.", "사물 → which"),
q("rel", "I have an uncle ___ is a cook.", ["who", "which", "what"], "나는 요리사인 삼촌이 있어요.", "사람 → who"),
# 이어 주는 말 conj
q("conj", "I stayed home ___ I was sick.", ["because", "but", "so"], "나는 아파서 집에 있었어요.", "이유(아파서) → because"),
q("conj", "It was cold, ___ I wore a coat.", ["so", "because", "until"], "추워서 코트를 입었어요.", "그래서 → so"),
q("conj", "Wash your hands ___ you eat.", ["before", "after", "because"], "먹기 전에 손을 씻어요.", "~하기 전에 → before"),
q("conj", "___ it rained, we played soccer.", ["Although", "Because", "If"], "비가 왔지만 우리는 축구를 했어요.", "~인데도 → Although", {"Because": "비가 와서 축구를 했다는 건 이상해요"}),
q("conj", "Call me ___ you get home.", ["when", "until", "although"], "집에 도착하면 전화해.", "~할 때 → when"),
q("conj", "___ you hurry, you will miss the bus.", ["Unless", "If", "Because"], "서두르지 않으면 버스를 놓칠 거야.", "~하지 않으면 → Unless", {"If": "If 면 '서두르면 놓친다'가 돼요"}),
q("conj", "I listened to music ___ I was cooking.", ["while", "until", "unless"], "나는 요리하는 동안 음악을 들었어요.", "~하는 동안 → while"),
q("conj", "Let's wait here ___ the rain stops.", ["until", "while", "because"], "비가 그칠 때까지 여기서 기다리자.", "~할 때까지 → until"),
q("conj", "___ you are tired, take a rest.", ["If", "Although", "Until"], "피곤하면 좀 쉬어.", "만약 ~하면 → If"),
q("conj", "We went for a walk ___ dinner.", ["after", "before", "because"], "우리는 저녁을 먹고 산책했어요.", "~후에 → after"),
q("conj", "He is small, ___ he is very strong.", ["but", "so", "because"], "그는 작지만 아주 힘이 세요.", "반대 내용 → but"),
q("conj", "She smiled ___ she saw her dog.", ["when", "unless", "until"], "그녀는 자기 개를 보고 웃었어요.", "~할 때 → when"),
q("conj", "I couldn't sleep ___ it was too hot.", ["because", "although", "so"], "너무 더워서 잠을 못 잤어요.", "이유 → because"),
q("conj", "Do you want tea ___ juice?", ["or", "but", "so"], "차 마실래, 주스 마실래?", "둘 중 하나 → or"),
q("conj", "Study hard, ___ you will pass the test.", ["and", "or", "but"], "열심히 공부해. 그러면 시험에 붙을 거야.", "명령 + and → 그러면", {"or": "or 면 '그렇지 않으면'이 돼요"}),
# 기간·때 dur
q("dur", "I slept ___ ten hours.", ["for", "since", "during"], "나는 10시간 동안 잤어요.", "숫자 기간 → for"),
q("dur", "She has lived here ___ 2019.", ["since", "for", "during"], "그녀는 2019년부터 여기 살았어요.", "시작한 때 → since"),
q("dur", "Don't talk ___ the movie.", ["during", "for", "since"], "영화 보는 동안 떠들지 마.", "일·행사 동안 → during", {"for": "for 뒤에는 숫자 기간이 와요"}),
q("dur", "The shop is open ___ 9 p.m.", ["until", "since", "during"], "가게는 저녁 9시까지 열어요.", "~까지 → until"),
q("dur", "We stayed in Jeju ___ a week.", ["for", "during", "since"], "우리는 일주일 동안 제주에 있었어요.", "a week(기간) → for"),
q("dur", "I met Jiho ___ the summer vacation.", ["during", "for", "since"], "나는 여름방학 동안 지호를 만났어요.", "방학(일·때) → during"),
q("dur", "He has been here ___ this morning.", ["since", "for", "until"], "그는 오늘 아침부터 여기 있었어요.", "시작한 때 → since"),
q("dur", "Please wait ___ five minutes.", ["for", "since", "during"], "5분만 기다려 주세요.", "숫자 기간 → for"),
q("dur", "It snowed ___ the night.", ["during", "since", "for"], "밤사이에 눈이 왔어요.", "the night(때) → during"),
q("dur", "I'll be at school ___ 3 o'clock.", ["until", "since", "during"], "나는 3시까지 학교에 있을 거예요.", "~까지 → until"),
q("dur", "They have been friends ___ a long time.", ["for", "since", "during"], "그들은 오랫동안 친구로 지냈어요.", "a long time(기간) → for"),
q("dur", "My grandpa has worked here ___ he was young.", ["since", "for", "during"], "할아버지는 젊으셨을 때부터 여기서 일하셨어요.", "그때부터 → since"),
q("dur", "We visited many places ___ our trip.", ["during", "for", "until"], "우리는 여행 동안 많은 곳에 갔어요.", "여행(일) → during"),
q("dur", "I studied English ___ two hours.", ["for", "during", "since"], "나는 두 시간 동안 영어 공부를 했어요.", "숫자 기간 → for"),
q("dur", "Keep running ___ you reach the line.", ["until", "during", "since"], "선에 닿을 때까지 계속 달려.", "~할 때까지 → until"),
# to부정사 inf
q("inf", "I want ___ a pilot.", ["to be", "be", "being"], "나는 조종사가 되고 싶어요.", "want + to + 동사원형"),
q("inf", "She decided ___ the piano.", ["to learn", "learning", "learn"], "그녀는 피아노를 배우기로 했어요.", "decide + to", {"learning": "decide 뒤에는 -ing 가 못 와요"}),
q("inf", "We plan ___ Busan this summer.", ["to visit", "visiting", "visit"], "우리는 이번 여름에 부산에 갈 계획이에요.", "plan + to"),
q("inf", "I went to the store ___ milk.", ["to buy", "buying", "buy"], "나는 우유를 사러 가게에 갔어요.", "~하려고 → to + 동사원형"),
q("inf", "He hopes ___ his grandma soon.", ["to see", "seeing", "see"], "그는 할머니를 곧 뵙기를 바라요.", "hope + to"),
q("inf", "It's time ___ to bed.", ["to go", "going", "go"], "잘 시간이야.", "time + to + 동사원형"),
q("inf", "I need something ___.", ["to drink", "drink", "drinking"], "나는 마실 것이 필요해요.", "~할 것 → something + to"),
q("inf", "She was happy ___ the news.", ["to hear", "hear", "heard"], "그녀는 그 소식을 듣고 기뻤어요.", "기쁜 이유 → to + 동사원형"),
q("inf", "Do you want ___ with me?", ["to play", "play", "playing"], "나랑 같이 놀래?", "want + to"),
q("inf", "I forgot ___ my homework.", ["to bring", "bring", "brought"], "숙제 가져오는 걸 깜빡했어요.", "forget + to (할 일을 잊다)"),
q("inf", "He has a lot of books ___.", ["to read", "reading", "read"], "그는 읽을 책이 많아요.", "~할 책 → books + to"),
q("inf", "We would like ___ some pizza.", ["to order", "ordering", "order"], "피자를 주문하고 싶어요.", "would like + to"),
q("inf", "My dream is ___ around the world.", ["to travel", "travel", "traveled"], "내 꿈은 세계 여행을 하는 거예요.", "~하는 것 → to + 동사원형"),
q("inf", "She promised ___ late again.", ["not to be", "to not being", "not be"], "그녀는 다시는 늦지 않겠다고 약속했어요.", "~하지 않기로 → not to"),
q("inf", "I got up early ___ the sunrise.", ["to see", "seeing", "saw"], "나는 해돋이를 보려고 일찍 일어났어요.", "~하려고 → to + 동사원형")]

H = json.load(open(P)); raw = open(P).read()
have = {(x["k"], x.get("s")) for x in H}; add = 0
for x in NEW:
    assert x["s"].count("___") == 1 and len(set(x["o"])) == len(x["o"]) == 3, x
    for wk in (x.get("w") or {}): assert wk in x["o"][1:], x
    if (x["k"], x["s"]) not in have: H.append(x); have.add((x["k"], x["s"])); add += 1
compact = "\n" not in raw.strip()[:3000]
open(P, "w").write(json.dumps(H, ensure_ascii=False, separators=(",", ":")) if compact else json.dumps(H, ensure_ascii=False, indent=1))
import collections; print("added", add, collections.Counter(x["k"] for x in H if x["lv"] == 0))
