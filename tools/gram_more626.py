# v626 문법 늘리기 ② — 원래 있던 문법 16개에 문제 10개씩 더 (19 → 29 안팎) · 같은 문장은 안 넣음
import json, os
P = os.path.join(os.path.dirname(__file__), "..", "data", "gram.json")
def pk(s, o, a, ko, w): return {"k": "pick", "s": s, "o": o, "a": a, "ko": ko, "w": w}
def ox(s, ok, ko, fix=None):
    d = {"k": "ox", "s": s, "ok": ok, "ko": ko}
    if fix: d["fix"] = fix
    return d
def fx(s, bad, a, ko, w): return {"k": "fix", "s": s, "bad": bad, "a": a, "ko": ko, "w": w}
def od(ws, ko): return {"k": "order", "w": ws.split(" "), "ko": ko}

MORE = {
"g34-1": [
 pk("It is ___ owl.", ["a", "an"], "an", "그것은 부엉이예요.", "owl 은 '아' 소리 → an"),
 pk("I ate ___ banana.", ["a", "an"], "a", "나는 바나나 하나를 먹었어요.", "banana 는 '바' 소리 → a"),
 pk("That is ___ old house.", ["a", "an"], "an", "저것은 오래된 집이에요.", "바로 뒤 old 가 '오' 소리 → an"),
 pk("She has ___ uncle in Busan.", ["a", "an"], "an", "그녀는 부산에 삼촌이 있어요.", "uncle 은 '어' 소리 → an"),
 pk("I need ___ new eraser.", ["a", "an"], "a", "나는 새 지우개가 필요해요.", "바로 뒤 new 가 '뉴' 소리 → a"),
 pk("We saw ___ octopus at the aquarium.", ["a", "an"], "an", "우리는 수족관에서 문어를 봤어요.", "octopus 는 '아' 소리 → an"),
 ox("It is an ant.", True, "그것은 개미예요."),
 ox("I want a orange.", False, "나는 오렌지를 원해요.", "I want an orange."),
 fx("This is a easy question.", "a", "an", "이건 쉬운 문제예요.", "easy 는 '이' 소리 → an"),
 od("She has an orange cat.", "그녀는 주황색 고양이가 있어요.")],
"g34-2": [
 pk("I have two ___.", ["cats", "cat"], "cats", "나는 고양이가 두 마리 있어요.", "two → cats"),
 pk("There are many ___ in the box.", ["toys", "toy"], "toys", "상자 안에 장난감이 많아요.", "many → toys"),
 pk("I brush my ___ every day.", ["teeth", "tooths"], "teeth", "나는 매일 이를 닦아요.", "tooth 여럿 → teeth"),
 pk("The ___ are on the table.", ["dishes", "dishs"], "dishes", "접시들이 탁자 위에 있어요.", "sh 로 끝나면 → es"),
 pk("We saw three ___ on the farm.", ["sheep", "sheeps"], "sheep", "우리는 농장에서 양 세 마리를 봤어요.", "sheep 은 여럿이어도 sheep"),
 pk("I have one ___.", ["sister", "sisters"], "sister", "나는 언니가 한 명 있어요.", "one → 그대로"),
 ox("I see two foxes.", True, "나는 여우 두 마리를 봐요."),
 ox("She has four babys.", False, "그녀는 아기가 넷 있어요.", "She has four babies."),
 fx("My feets are cold.", "feets", "feet", "내 발이 차가워요.", "foot 여럿 → feet"),
 od("I have two big dogs.", "나는 큰 개가 두 마리 있어요.")],
"g34-3": [
 pk("The cats ___ cute.", ["are", "is"], "are", "고양이들이 귀여워요.", "cats = 여럿 → are"),
 pk("My name ___ Jiho.", ["is", "am"], "is", "내 이름은 지호예요.", "name 하나 → is"),
 pk("You and Mina ___ late.", ["are", "is"], "are", "너와 미나는 늦었어.", "두 사람 → are"),
 pk("I ___ in the third grade.", ["am", "is"], "am", "나는 3학년이에요.", "I → am"),
 pk("The weather ___ nice today.", ["is", "are"], "is", "오늘 날씨가 좋아요.", "weather 하나 → is"),
 pk("These cookies ___ delicious.", ["are", "is"], "are", "이 쿠키들은 맛있어요.", "cookies = 여럿 → are"),
 ox("My brothers is tall.", False, "우리 형들은 키가 커요.", "My brothers are tall."),
 ox("It is cold outside.", True, "밖이 추워요."),
 fx("I are ten years old.", "are", "am", "나는 열 살이에요.", "I → am"),
 od("We are in the same class.", "우리는 같은 반이에요.")],
"g34-4": [
 pk("___ is my house. Come in!", ["This", "These"], "This", "여기가 우리 집이야. 들어와!", "가까이 하나 → This"),
 pk("Look at ___ mountain over there.", ["that", "this"], "that", "저기 저 산 좀 봐.", "멀리 하나 → that"),
 pk("___ apples in my hand are red.", ["These", "Those"], "These", "내 손에 있는 이 사과들은 빨개요.", "가까이 여럿 → These"),
 pk("Who are ___ people over there?", ["those", "these"], "those", "저기 저 사람들은 누구야?", "멀리 여럿 → those"),
 pk("Is ___ your bag on the desk next to me?", ["this", "those"], "this", "내 옆 책상에 있는 이거 네 가방이야?", "가까이 하나 → this"),
 pk("___ stars are so bright tonight.", ["Those", "That"], "Those", "오늘 밤 저 별들은 정말 밝아.", "멀리 여럿 → Those"),
 ox("That is my school over there.", True, "저기 저게 우리 학교야."),
 ox("These is my pencils.", False, "이것들은 내 연필이야.", "These are my pencils."),
 fx("Those bird is singing.", "bird", "birds", "저 새들이 노래하고 있어요.", "Those 뒤 → 여럿 birds"),
 od("This is my new bike.", "이건 내 새 자전거야.")],
"g34-5": [
 pk("I love ___ dog.", ["my", "me"], "my", "나는 우리 개를 사랑해요.", "나의 → my"),
 pk("Is this ___ pencil, Tom?", ["your", "you"], "your", "톰, 이거 네 연필이야?", "너의 → your"),
 pk("Jiho is washing ___ hands.", ["his", "her"], "his", "지호는 손을 씻고 있어요.", "Jiho(남자) → his"),
 pk("My sister is reading ___ book.", ["her", "his"], "her", "언니는 자기 책을 읽고 있어요.", "sister(여자) → her"),
 pk("We love ___ school.", ["our", "us"], "our", "우리는 우리 학교를 좋아해요.", "우리의 → our"),
 pk("The kids are playing with ___ toys.", ["their", "they"], "their", "아이들이 자기들 장난감으로 놀고 있어요.", "kids 의 → their"),
 ox("This is her bag.", True, "이건 그녀의 가방이야."),
 ox("They clean they room.", False, "그들은 자기 방을 청소해요.", "They clean their room."),
 fx("My dad loves he car.", "he", "his", "아빠는 자기 차를 좋아하세요.", "dad 의 → his"),
 od("What is your name?", "네 이름은 뭐야?")],
"g34-6": [
 pk("My sister ___ milk every morning.", ["drinks", "drink"], "drinks", "언니는 매일 아침 우유를 마셔요.", "sister 한 명 → drinks"),
 pk("We ___ to school by bus.", ["go", "goes"], "go", "우리는 버스로 학교에 가요.", "we → 그대로 go"),
 pk("He ___ his homework after dinner.", ["does", "do"], "does", "그는 저녁 먹고 숙제를 해요.", "he + do → does"),
 pk("The baby ___ a lot.", ["cries", "crys"], "cries", "아기가 많이 울어요.", "y 로 끝나면 → ies"),
 pk("Mina ___ two cats.", ["has", "haves"], "has", "미나는 고양이가 두 마리 있어요.", "Mina + have → has"),
 pk("My parents ___ in Seoul.", ["live", "lives"], "live", "부모님은 서울에 사세요.", "parents = 여럿 → live"),
 ox("He watches TV every day.", True, "그는 매일 TV를 봐요."),
 ox("She go to bed at nine.", False, "그녀는 9시에 자요.", "She goes to bed at nine."),
 fx("Tom like bananas.", "like", "likes", "톰은 바나나를 좋아해요.", "Tom 한 명 → likes"),
 od("My mom makes good cookies.", "엄마는 맛있는 쿠키를 만드세요.")],
"g34-7": [
 pk("___ you hungry?", ["Are", "Do"], "Are", "너 배고파?", "hungry(상태) → Are"),
 pk("___ he play baseball?", ["Does", "Is"], "Does", "그는 야구를 하니?", "play(하는 말) + he → Does"),
 pk("___ this your phone?", ["Is", "Does"], "Is", "이거 네 휴대폰이야?", "this + 상태 → Is"),
 pk("___ your friends live near here?", ["Do", "Does"], "Do", "네 친구들은 이 근처에 살아?", "friends = 여럿 → Do"),
 pk("Is she your teacher? — Yes, she ___.", ["is", "does"], "is", "그분이 너희 선생님이야? — 응, 맞아.", "Is ~? → she is"),
 pk("Does he like cats? — No, he ___.", ["doesn't", "isn't"], "doesn't", "그는 고양이를 좋아해? — 아니, 안 좋아해.", "Does ~? → doesn't"),
 ox("Do you have a pet?", True, "너 반려동물 있어?"),
 ox("Is he play soccer?", False, "그는 축구를 하니?", "Does he play soccer?"),
 fx("Does they go to school?", "Does", "Do", "그들은 학교에 다녀?", "they → Do"),
 od("Do you like ice cream?", "너 아이스크림 좋아해?")],
"g34-8": [
 pk("I ___ like spiders.", ["don't", "doesn't"], "don't", "나는 거미를 안 좋아해요.", "I → don't"),
 pk("She ___ at home now.", ["isn't", "doesn't"], "isn't", "그녀는 지금 집에 없어요.", "at home(상태) → isn't"),
 pk("My dog ___ like baths.", ["doesn't", "don't"], "doesn't", "우리 개는 목욕을 싫어해요.", "dog 한 마리 → doesn't"),
 pk("We ___ go to school on Sunday.", ["don't", "aren't"], "don't", "우리는 일요일에 학교에 안 가요.", "go(하는 말) → don't"),
 pk("They ___ hungry now.", ["aren't", "don't"], "aren't", "그들은 지금 배고프지 않아요.", "hungry(상태) → aren't"),
 pk("He doesn't ___ a bike.", ["have", "has"], "have", "그는 자전거가 없어요.", "doesn't 뒤 → 원래 모양"),
 ox("It isn't my umbrella.", True, "그건 내 우산이 아니에요."),
 ox("Mina don't eat fish.", False, "미나는 생선을 안 먹어요.", "Mina doesn't eat fish."),
 fx("He doesn't likes milk.", "likes", "like", "그는 우유를 안 좋아해요.", "doesn't 뒤 → like"),
 od("I don't have a pet.", "나는 반려동물이 없어요.")],
"g56-1": [
 pk("Listen! Someone ___ singing.", ["is", "are"], "is", "들어 봐! 누가 노래하고 있어.", "someone 한 명 → is"),
 pk("The kids are ___ in the snow.", ["playing", "play"], "playing", "아이들이 눈 속에서 놀고 있어요.", "are + ing"),
 pk("I'm ___ my homework now.", ["doing", "do"], "doing", "나는 지금 숙제를 하고 있어요.", "am + ing"),
 pk("She is ___ a bike.", ["riding", "rideing"], "riding", "그녀는 자전거를 타고 있어요.", "e 로 끝나면 e 빼고 ing"),
 pk("The dog is ___ after the ball.", ["running", "runing"], "running", "개가 공을 쫓아 달리고 있어요.", "run → running (n 하나 더)"),
 pk("Are you ___ a movie? — Yes, I am.", ["watching", "watch"], "watching", "영화 보고 있어? — 응.", "Are + ing"),
 ox("We are swimming in the sea.", True, "우리는 바다에서 수영하고 있어요."),
 ox("He is write a letter.", False, "그는 편지를 쓰고 있어요.", "He is writing a letter."),
 fx("They is eating lunch now.", "is", "are", "그들은 지금 점심을 먹고 있어요.", "they → are"),
 od("My brother is sleeping now.", "남동생은 지금 자고 있어요.")],
"g56-2": [
 pk("I ___ the dishes last night.", ["washed", "wash"], "washed", "나는 어젯밤에 설거지를 했어요.", "last night → washed"),
 pk("She ___ a song at the concert yesterday.", ["played", "plays"], "played", "그녀는 어제 음악회에서 노래를 연주했어요.", "yesterday → played"),
 pk("We ___ at the joke.", ["laughed", "laughd"], "laughed", "우리는 그 농담에 웃었어요.", "ed 붙이기 → laughed"),
 pk("He ___ the box to the car.", ["carried", "carryed"], "carried", "그는 상자를 차로 옮겼어요.", "y → ied"),
 pk("The train ___ at the station.", ["stopped", "stoped"], "stopped", "기차가 역에 멈췄어요.", "stop → stopped (p 하나 더)"),
 pk("I ___ in Busan two years ago.", ["lived", "liveed"], "lived", "나는 2년 전에 부산에 살았어요.", "e 로 끝나면 d 만"),
 ox("She closed the window an hour ago.", True, "그녀는 한 시간 전에 창문을 닫았어요."),
 ox("We plaied soccer yesterday.", False, "우리는 어제 축구를 했어요.", "We played soccer yesterday."),
 fx("He cook dinner last night.", "cook", "cooked", "그는 어젯밤 저녁을 만들었어요.", "last night → cooked"),
 od("I visited my uncle last weekend.", "나는 지난 주말에 삼촌 댁에 갔어요.")],
"g56-3": [
 pk("I ___ a strange dream last night.", ["had", "haved"], "had", "나는 어젯밤 이상한 꿈을 꿨어요.", "have → had"),
 pk("We ___ pizza for dinner yesterday.", ["ate", "eated"], "ate", "우리는 어제 저녁으로 피자를 먹었어요.", "eat → ate"),
 pk("She ___ to the library after school.", ["went", "goed"], "went", "그녀는 방과 후에 도서관에 갔어요.", "go → went"),
 pk("He ___ me a nice card.", ["gave", "gived"], "gave", "그는 나에게 멋진 카드를 줬어요.", "give → gave"),
 pk("I ___ my homework at nine.", ["did", "doed"], "did", "나는 9시에 숙제를 했어요.", "do → did"),
 pk("The kids ___ in the park all day.", ["were", "was"], "were", "아이들은 하루 종일 공원에 있었어요.", "kids = 여럿 → were"),
 ox("I met my friend at the mall.", True, "나는 쇼핑몰에서 친구를 만났어요."),
 ox("She runned to the bus stop.", False, "그녀는 버스 정류장으로 뛰어갔어요.", "She ran to the bus stop."),
 fx("We buyed some flowers for Mom.", "buyed", "bought", "우리는 엄마께 드릴 꽃을 샀어요.", "buy → bought"),
 od("I saw a big rainbow yesterday.", "나는 어제 큰 무지개를 봤어요.")],
"g56-4": [
 pk("___ you eat breakfast this morning?", ["Did", "Do"], "Did", "오늘 아침 먹었어?", "this morning(지난 일) → Did"),
 pk("Did she ___ the bus?", ["miss", "missed"], "miss", "그녀가 버스를 놓쳤어?", "Did 뒤 → 원래 모양"),
 pk("I didn't ___ the answer.", ["know", "knew"], "know", "나는 답을 몰랐어요.", "didn't 뒤 → 원래 모양"),
 pk("Did they enjoy the trip? — Yes, they ___.", ["did", "do"], "did", "그들은 여행이 즐거웠대? — 응.", "Did ~? → did"),
 pk("We ___ see the movie. It was sold out.", ["didn't", "don't"], "didn't", "우리는 그 영화를 못 봤어. 매진이었거든.", "지난 일 → didn't"),
 pk("Did you ___ your grandma last week?", ["visit", "visited"], "visit", "지난주에 할머니 댁에 갔었어?", "Did 뒤 → visit"),
 ox("Did he call you last night?", True, "어젯밤에 그가 너한테 전화했어?"),
 ox("She didn't went home.", False, "그녀는 집에 안 갔어요.", "She didn't go home."),
 fx("Does you sleep well last night?", "Does", "Did", "어젯밤에 잘 잤어?", "last night → Did"),
 od("Did you clean your room?", "네 방 청소했어?")],
"g56-5": [
 pk("I ___ call you tonight.", ["will", "am"], "will", "오늘 밤에 전화할게.", "앞으로 할 일 → will"),
 pk("We are going to ___ camping next week.", ["go", "going"], "go", "우리는 다음 주에 캠핑을 갈 거예요.", "going to 뒤 → 원래 모양"),
 pk("She ___ going to bake a cake.", ["is", "will"], "is", "그녀는 케이크를 구울 거예요.", "she → is going to"),
 pk("Will you ___ me tomorrow?", ["help", "helps"], "help", "내일 나 도와줄래?", "will 뒤 → 원래 모양"),
 pk("It ___ be cold this weekend.", ["will", "is"], "will", "이번 주말엔 추울 거예요.", "앞으로의 날씨 → will be"),
 pk("They ___ going to move next month.", ["are", "is"], "are", "그들은 다음 달에 이사할 거예요.", "they → are going to"),
 ox("I will be ten next year.", True, "나는 내년에 열 살이 돼요."),
 ox("We going to visit Jeju.", False, "우리는 제주에 갈 거예요.", "We are going to visit Jeju."),
 fx("He will visits his aunt.", "visits", "visit", "그는 이모 댁에 갈 거예요.", "will 뒤 → visit"),
 od("I am going to learn swimming.", "나는 수영을 배울 거예요.")],
"g56-6": [
 pk("An elephant is ___ than a horse.", ["bigger", "biggest"], "bigger", "코끼리는 말보다 커요.", "둘 비교 + than → bigger"),
 pk("Who is the ___ in your class?", ["tallest", "taller"], "tallest", "너희 반에서 누가 제일 키가 커?", "여럿 중 가장 → tallest"),
 pk("This box is ___ than that one.", ["heavier", "heavyer"], "heavier", "이 상자가 저것보다 무거워요.", "y → ier"),
 pk("Summer is ___ than spring.", ["hotter", "hoter"], "hotter", "여름은 봄보다 더워요.", "hot → hotter (t 하나 더)"),
 pk("This is the ___ beautiful flower in the garden.", ["most", "more"], "most", "이건 정원에서 가장 예쁜 꽃이에요.", "긴 말 + 가장 → most"),
 pk("My score is ___ than yours.", ["better", "gooder"], "better", "내 점수가 네 것보다 좋아.", "good → better"),
 ox("A mouse is smaller than a cat.", True, "쥐는 고양이보다 작아요."),
 ox("This is the more expensive bag in the shop.", False, "이것은 가게에서 가장 비싼 가방이에요.", "This is the most expensive bag in the shop."),
 fx("Tom is old than me.", "old", "older", "톰은 나보다 나이가 많아요.", "than → older"),
 od("Mount Everest is the highest mountain.", "에베레스트산은 가장 높은 산이에요.")],
"g56-7": [
 pk("You ___ cross the street at a red light.", ["must not", "must"], "must not", "빨간불에 길을 건너면 절대 안 돼요.", "위험해요 → must not"),
 pk("I ___ ride a bike, but I can't swim.", ["can", "can't"], "can", "나는 자전거는 탈 수 있지만 수영은 못 해요.", "but 앞은 할 수 있어요 → can"),
 pk("You look tired. You ___ get some rest.", ["should", "shouldn't"], "should", "피곤해 보여. 좀 쉬는 게 좋겠어.", "좋은 생각 → should"),
 pk("We must ___ our homework by Friday.", ["finish", "finishes"], "finish", "우리는 금요일까지 숙제를 꼭 끝내야 해요.", "must 뒤 → 원래 모양"),
 pk("___ I borrow your eraser?", ["Can", "Must"], "Can", "지우개 좀 빌려도 돼?", "허락 → Can"),
 pk("You ___ eat so much candy. It's bad for your teeth.", ["shouldn't", "should"], "shouldn't", "사탕을 그렇게 많이 먹지 않는 게 좋아. 이에 나빠.", "나빠요 → shouldn't"),
 ox("Students must wear a uniform.", True, "학생들은 교복을 꼭 입어야 해요."),
 ox("You should to sleep early.", False, "일찍 자는 게 좋아요.", "You should sleep early."),
 fx("She can runs very fast.", "runs", "run", "그녀는 아주 빨리 달릴 수 있어요.", "can 뒤 → run"),
 od("You should drink more water.", "물을 더 마시는 게 좋아요.")],
"g56-8": [
 pk("I wake up ___ seven o'clock.", ["at", "on"], "at", "나는 7시에 일어나요.", "몇 시 → at"),
 pk("We go to the beach ___ summer.", ["in", "on"], "in", "우리는 여름에 바닷가에 가요.", "계절 → in"),
 pk("The test is ___ Wednesday.", ["on", "in"], "on", "시험은 수요일이에요.", "요일 → on"),
 pk("Christmas is ___ December 25th.", ["on", "in"], "on", "크리스마스는 12월 25일이에요.", "날짜 → on"),
 pk("My cousin was born ___ 2018.", ["in", "at"], "in", "사촌은 2018년에 태어났어요.", "해(연도) → in"),
 pk("Let's meet ___ 3:30.", ["at", "in"], "at", "3시 30분에 만나자.", "몇 시 → at"),
 ox("I play soccer on Sundays.", True, "나는 일요일마다 축구를 해요."),
 ox("We have a vacation on August.", False, "우리는 8월에 방학이 있어요.", "We have a vacation in August."),
 fx("The store closes in 8 p.m.", "in", "at", "가게는 저녁 8시에 닫아요.", "몇 시 → at"),
 od("My birthday is in October.", "내 생일은 10월이에요.")]}

def key(q): return q.get("s") or " ".join(q.get("w", []))
G = json.load(open(P)); raw = open(P).read(); add = 0
for bk in ("g34", "g56"):
    for g in G[bk]:
        if g["id"] not in MORE: continue
        have = {key(q) for q in g["qs"]}
        for q in MORE[g["id"]]:
            if q["k"] == "pick": assert q["a"] in q["o"] and q["s"].count("___") == 1, q
            if q["k"] == "fix": assert [t.strip(".,!?") for t in q["s"].split(" ")].count(q["bad"]) == 1, q
            if q["k"] == "ox" and not q["ok"]: assert q.get("fix"), q
            if key(q) not in have: g["qs"].append(q); have.add(key(q)); add += 1
compact = "\n" not in raw.strip()[:2000]
open(P, "w").write(json.dumps(G, ensure_ascii=False, separators=(",", ":")) if compact else json.dumps(G, ensure_ascii=False, indent=1))
print("added", add); print({g["id"]: len(g["qs"]) for bk in ("g34", "g56") for g in G[bk]})
