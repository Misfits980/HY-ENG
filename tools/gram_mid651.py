# (v651) 중등 문법 코스 → data/gram.json 의 "mid"   (python3 tools/gram_mid651.py  →  python3 tools/check_gram.py)
# 중1 4단원부터: be동사 · 일반동사 현재 · 과거시제 · 조동사.  문제: P 고르기 · OX · OR 순서 · FX 틀린 단어 · W 직접 쓰기(새 유형)
# 쓰는 법: 단원을 더할 때 이 파일의 MID 에 G(...) 를 이어 붙이고 다시 돌림 (같은 id 는 덮어씀)
import json, os
P_ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "gram.json")

def R(h, p, ex, q, x=0):
    d = {"k": "rule", "h": h, "p": p, "ex": ex, "q": q}
    if x: d["x"] = 1
    return d
def P(s, o, a, ko, w, hd=0):
    d = {"k": "pick", "s": s, "o": o, "a": a, "ko": ko, "w": w}
    if hd: d["hd"] = 1
    return d
def OX(s, ok, ko, fix=None, w=None):
    d = {"k": "ox", "s": s, "ok": bool(ok), "ko": ko}
    if fix: d["fix"] = fix
    if w: d["w"] = w
    return d
def OR(words, ko): return {"k": "order", "w": words.split(" "), "ko": ko}
def FX(s, bad, a, ko, w): return {"k": "fix", "s": s, "bad": bad, "a": a, "ko": ko, "w": w}
def W(s, a, ko, w, alt=None):
    d = {"k": "write", "s": s, "a": a, "ko": ko, "w": w}
    if alt: d["alt"] = alt
    return d
def G(id, t, emo, sub, cards, qs): return {"id": id, "at": 0, "t": t, "emo": emo, "sub": sub, "cards": cards, "qs": qs}

MID = [
# ───────────────────────── 중1 ① be동사 ─────────────────────────
G("mid-1", "be동사", "🟦", "중1 · am · are · is · was · were", [
  R("주어에 따라 am · are · is", "I 는 am, you · we · they(여럿)는 are, he · she · it(하나)은 is 를 써요.",
    [["🙋", "", "I {am} a middle school student.", "나는 중학생이에요."], ["👫", "", "My friends {are} in the gym.", "내 친구들은 체육관에 있어요."], ["👩‍🏫", "", "Ms. Kim {is} our English teacher.", "김 선생님은 우리 영어 선생님이에요."]],
    P("Tom and I ___ in the same class.", ["am", "are", "is"], "are", "톰과 나는 같은 반이에요.", "Tom and I = we(여럿) → are")),
  R("지난 일은 was · were", "am · is 의 과거는 was, are 의 과거는 were 예요.",
    [["🌧️", "It is rainy.", "It {was} rainy yesterday.", "어제는 비가 왔어요."], ["🏫", "We are late.", "We {were} late this morning.", "우리는 오늘 아침에 늦었어요."]],
    P("My parents ___ in Busan last weekend.", ["was", "were"], "were", "부모님은 지난 주말에 부산에 계셨어요.", "parents = 여럿 + last weekend → were")),
  R("아니에요 = be + not · 물어볼 때는 be 를 앞으로", "not 은 be동사 바로 뒤에, 물어볼 때는 be동사를 문장 맨 앞으로 보내요. (is not = isn't · are not = aren't)",
    [["🙅", "She is tired.", "She {is not} tired.", "그녀는 피곤하지 않아요."], ["❓", "You are busy.", "{Are} you busy?", "너 바쁘니?"], ["❓", "He was at home.", "{Was} he at home?", "그는 집에 있었니?"]],
    P("___ your sister a high school student?", ["Is", "Are", "Does"], "Is", "너희 누나는 고등학생이니?", "your sister = 하나 → Is · be동사 문장에는 Does 를 안 써요"), x=1),
], [
  P("My brother ___ good at soccer.", ["am", "are", "is"], "is", "우리 형은 축구를 잘해요.", "my brother = he → is"),
  P("The students ___ in the library now.", ["is", "are"], "are", "학생들은 지금 도서관에 있어요.", "students = 여럿 → are"),
  P("I ___ not hungry right now.", ["am", "is", "are"], "am", "나는 지금 배고프지 않아요.", "I → am"),
  P("It ___ very cold last night.", ["is", "was", "were"], "was", "어젯밤은 아주 추웠어요.", "it + last night → was"),
  P("We ___ at the concert yesterday.", ["are", "was", "were"], "were", "우리는 어제 콘서트에 있었어요.", "we + yesterday → were"),
  P("___ you tired after the game yesterday?", ["Are", "Was", "Were"], "Were", "어제 경기 끝나고 피곤했니?", "you + yesterday → Were"),
  P("This book ___ not interesting.", ["is", "are", "am"], "is", "이 책은 재미있지 않아요.", "this book = 하나 → is"),
  P("Mina and her sister ___ twins.", ["is", "are"], "are", "미나와 여동생은 쌍둥이예요.", "A and B = 여럿 → are"),
  P("A: Is he your teacher?  B: No, he ___.", ["isn't", "aren't", "doesn't"], "isn't", "A: 그분이 너희 선생님이니? B: 아니, 아니야.", "Is he …? 로 물으면 he isn't 로 답해요"),
  P("The shoes on the floor ___ mine.", ["is", "are"], "are", "바닥에 있는 신발은 내 것이에요.", "주어는 the shoes(여럿) — the floor 가 아니에요", 1),
  P("One of my friends ___ from Canada.", ["is", "are"], "is", "내 친구들 중 한 명은 캐나다에서 왔어요.", "주어는 One(한 명) → is", 1),
  P("There ___ two cats under the table an hour ago.", ["is", "was", "were"], "were", "한 시간 전에 탁자 밑에 고양이 두 마리가 있었어요.", "two cats(여럿) + an hour ago → were", 1),
  OX("My friends is very kind.", False, "내 친구들은 아주 친절해요.", "My friends are very kind.", "friends = 여럿 → are"),
  OX("She was sick last week.", True, "그녀는 지난주에 아팠어요."),
  OX("Are your father a doctor?", False, "너희 아버지는 의사시니?", "Is your father a doctor?", "your father = 하나 → Is"),
  OX("They were not at school yesterday.", True, "그들은 어제 학교에 없었어요."),
  OX("I amn't ready yet.", False, "나는 아직 준비가 안 됐어요.", "I am not ready yet.", "am not 은 줄여 쓰지 않아요 (I'm not)"),
  OR("My sister is not a student.", "우리 언니는 학생이 아니에요."),
  OR("Were you at home last night?", "너 어젯밤에 집에 있었니?"),
  OR("The children are in the playground.", "아이들은 놀이터에 있어요."),
  OR("Is your mother a nurse?", "너희 어머니는 간호사시니?"),
  FX("My parents is very busy today.", "is", "are", "부모님은 오늘 아주 바쁘세요.", "parents = 여럿 → are"),
  FX("He were late for school yesterday.", "were", "was", "그는 어제 학교에 늦었어요.", "he → was"),
  FX("Does she your new classmate?", "Does", "Is", "그 애가 새로 온 반 친구니?", "be동사 문장(명사가 바로 옴) → Is"),
  W("I ___ thirteen years old now. (be)", "am", "나는 지금 열세 살이에요.", "I → am"),
  W("My cousins ___ in Seoul last year. (be)", "were", "내 사촌들은 작년에 서울에 있었어요.", "cousins(여럿) + last year → were"),
  W("The movie ___ very boring yesterday. (be)", "was", "그 영화는 어제 아주 지루했어요.", "the movie(하나) + yesterday → was"),
  W("___ you ready now? (be)", "are", "지금 준비됐니?", "you + now → Are"),
  W("She ___ my sister. She is my cousin. (be, not)", "isn't", "그녀는 내 여동생이 아니에요. 사촌이에요.", "is + not = isn't", ["is not"]),
  W("We ___ late for class this morning. We were on time. (be, not)", "weren't", "우리는 오늘 아침 수업에 늦지 않았어요. 제시간에 왔어요.", "were + not = weren't", ["were not"]),
]),
# ───────────────────────── 중1 ② 일반동사 현재 ─────────────────────────
G("mid-2", "일반동사 현재", "🏃", "중1 · -s · don't · doesn't · Do · Does", [
  R("he · she · it 이면 동사에 -s", "주어가 하나(he · she · it)이고 지금 늘 하는 일이면 동사 끝에 -s 나 -es 를 붙여요. (study → studies · have → has)",
    [["⚽", "I play soccer.", "He {plays} soccer.", "그는 축구를 해요."], ["📺", "We watch TV.", "She {watches} TV.", "그녀는 TV를 봐요."], ["📚", "They study hard.", "Jinsu {studies} hard.", "진수는 열심히 공부해요."]],
    P("My sister ___ a dog.", ["have", "has"], "has", "우리 언니는 개를 길러요.", "my sister = she → has")),
  R("아니에요 = don't · doesn't + 동사 그대로", "he · she · it 이면 doesn't, 나머지는 don't. 뒤에 오는 동사는 -s 를 떼고 원래 모양으로 써요.",
    [["🙅", "I like onions.", "I {don't like} onions.", "나는 양파를 좋아하지 않아요."], ["🙅‍♂️", "He likes onions.", "He {doesn't like} onions.", "그는 양파를 좋아하지 않아요."]],
    P("She doesn't ___ breakfast.", ["eat", "eats"], "eat", "그녀는 아침을 먹지 않아요.", "doesn't 뒤에는 동사 그대로 (eat)")),
  R("물어볼 때는 Do · Does 를 앞에", "Do · Does 를 문장 맨 앞에 두고, 동사는 원래 모양으로 써요. 답은 Yes, I do. / No, she doesn't.",
    [["❓", "You like music.", "{Do} you {like} music?", "너 음악 좋아하니?"], ["❓", "He lives here.", "{Does} he {live} here?", "그는 여기 사니?"]],
    P("___ your brother play the guitar?", ["Do", "Does", "Is"], "Does", "너희 형은 기타를 치니?", "your brother = he → Does · 일반동사(play)가 있으니 Is 는 안 돼요"), x=1),
], [
  P("Mina ___ to school by bus.", ["go", "goes"], "goes", "미나는 버스로 학교에 가요.", "Mina = she → goes"),
  P("My friends ___ basketball after school.", ["play", "plays"], "play", "내 친구들은 방과 후에 농구를 해요.", "friends = 여럿 → play"),
  P("He ___ English very well.", ["speak", "speaks"], "speaks", "그는 영어를 아주 잘해요.", "he → speaks"),
  P("We ___ like spicy food.", ["don't", "doesn't"], "don't", "우리는 매운 음식을 좋아하지 않아요.", "we → don't"),
  P("My father ___ drink coffee.", ["don't", "doesn't"], "doesn't", "우리 아버지는 커피를 안 드세요.", "my father = he → doesn't"),
  P("Does she ___ in Seoul?", ["live", "lives"], "live", "그녀는 서울에 사니?", "Does 뒤에는 동사 그대로 (live)"),
  P("___ they walk to school?", ["Do", "Does"], "Do", "그들은 학교에 걸어가니?", "they → Do"),
  P("The baby ___ a lot at night.", ["cry", "cries"], "cries", "그 아기는 밤에 많이 울어요.", "the baby = it → cry 의 y 를 i 로 바꾸고 -es"),
  P("A: Do you know him?  B: Yes, I ___.", ["do", "does", "am"], "do", "A: 너 그를 아니? B: 응, 알아.", "Do you …? 로 물으면 I do 로 답해요"),
  P("My dog ___ like baths.", ["don't", "doesn't", "isn't"], "doesn't", "우리 개는 목욕을 좋아하지 않아요.", "my dog = it + 일반동사 like → doesn't", 1),
  P("Jisu and her brother ___ up early every day.", ["get", "gets"], "get", "지수와 남동생은 매일 일찍 일어나요.", "A and B = 여럿 → get", 1),
  P("Everyone in my class ___ the new teacher.", ["like", "likes"], "likes", "우리 반 모두가 새 선생님을 좋아해요.", "everyone 은 하나로 봐요 → likes", 1),
  OX("She don't like math.", False, "그녀는 수학을 좋아하지 않아요.", "She doesn't like math.", "she → doesn't"),
  OX("My uncle teaches science.", True, "우리 삼촌은 과학을 가르치세요."),
  OX("Does he plays the piano?", False, "그는 피아노를 치니?", "Does he play the piano?", "Does 뒤에는 동사 그대로"),
  OX("They don't watch TV on weekdays.", True, "그들은 평일에 TV를 보지 않아요."),
  OX("Do your mother work on Saturdays?", False, "너희 어머니는 토요일에 일하시니?", "Does your mother work on Saturdays?", "your mother = she → Does"),
  OR("My brother does not eat meat.", "우리 형은 고기를 먹지 않아요."),
  OR("Do you have a pencil?", "너 연필 있니?"),
  OR("She studies English every evening.", "그녀는 매일 저녁 영어를 공부해요."),
  OR("Does your father cook dinner?", "너희 아버지는 저녁을 요리하시니?"),
  FX("He don't have a phone.", "don't", "doesn't", "그는 휴대폰이 없어요.", "he → doesn't"),
  FX("My mom watch the news every morning.", "watch", "watches", "우리 엄마는 매일 아침 뉴스를 보세요.", "my mom = she → watches"),
  FX("Does she likes cats?", "likes", "like", "그녀는 고양이를 좋아하니?", "Does 뒤에는 동사 그대로"),
  W("My sister ___ to bed at ten every night. (go)", "goes", "우리 언니는 매일 밤 10시에 자요.", "my sister = she → goes"),
  W("He ___ his homework after dinner every day. (do)", "does", "그는 매일 저녁을 먹고 숙제를 해요.", "he → does"),
  W("Tom ___ two brothers. (have)", "has", "톰은 형제가 둘 있어요.", "Tom = he → has"),
  W("I ___ milk. I drink juice. (not, drink)", "don't drink", "나는 우유를 안 마셔요. 주스를 마셔요.", "I → don't + 동사 그대로", ["do not drink"]),
  W("She ___ meat. She is a vegetarian. (not, eat)", "doesn't eat", "그녀는 고기를 안 먹어요. 채식주의자예요.", "she → doesn't + 동사 그대로", ["does not eat"]),
  W("___ your teacher live near the school? (do)", "does", "너희 선생님은 학교 근처에 사시니?", "your teacher = 하나 → Does"),
]),
# ───────────────────────── 중1 ③ 과거시제 ─────────────────────────
G("mid-3", "과거시제", "⏪", "중1 · -ed · 불규칙 · didn't · Did", [
  R("지난 일은 동사 + -ed", "yesterday · last week · two days ago 처럼 지난 때를 말하면 동사에 -ed 를 붙여요. (stop → stopped · study → studied)",
    [["🧹", "I clean my room.", "I {cleaned} my room yesterday.", "나는 어제 방을 청소했어요."], ["📖", "She studies math.", "She {studied} math last night.", "그녀는 어젯밤 수학을 공부했어요."], ["🚌", "The bus stops here.", "The bus {stopped} here.", "버스가 여기 멈췄어요."]],
    P("We ___ soccer after school yesterday.", ["play", "played"], "played", "우리는 어제 방과 후에 축구를 했어요.", "yesterday → played")),
  R("모양이 바뀌는 동사는 외워요", "자주 쓰는 동사는 -ed 를 안 붙이고 모양이 바뀌어요.",
    [["🚶", "go", "{went}", "갔다"], ["🍽️", "eat", "{ate}", "먹었다"], ["👀", "see", "{saw}", "봤다"], ["🛍️", "buy", "{bought}", "샀다"], ["✍️", "write", "{wrote}", "썼다"], ["🎁", "give", "{gave}", "줬다"]],
    P("I ___ a great movie last weekend.", ["see", "saw", "seed"], "saw", "나는 지난 주말에 멋진 영화를 봤어요.", "see → saw")),
  R("didn't · Did 뒤에는 동사 그대로", "안 했어요 = didn't + 동사 원래 모양. 했니? = Did + 주어 + 동사 원래 모양. 과거 표시는 did 가 가져가요.",
    [["🙅", "I went there.", "I {didn't go} there.", "나는 거기 가지 않았어요."], ["❓", "She called you.", "{Did} she {call} you?", "그녀가 너한테 전화했니?"]],
    P("He didn't ___ his homework.", ["finish", "finished"], "finish", "그는 숙제를 끝내지 않았어요.", "didn't 뒤에는 동사 그대로 (finish)"), x=1),
], [
  P("I ___ my grandparents last Sunday.", ["visit", "visited"], "visited", "나는 지난 일요일에 조부모님을 찾아뵀어요.", "last Sunday → visited"),
  P("She ___ a letter to her friend yesterday.", ["writes", "wrote", "writed"], "wrote", "그녀는 어제 친구에게 편지를 썼어요.", "write → wrote"),
  P("We ___ pizza for lunch an hour ago.", ["eat", "ate"], "ate", "우리는 한 시간 전에 점심으로 피자를 먹었어요.", "an hour ago → ate"),
  P("They didn't ___ to the party last night.", ["come", "came"], "come", "그들은 어젯밤 파티에 오지 않았어요.", "didn't 뒤에는 동사 그대로"),
  P("Did you ___ the news this morning?", ["hear", "heard"], "hear", "오늘 아침에 그 소식 들었니?", "Did 뒤에는 동사 그대로"),
  P("My dad ___ a new car last month.", ["buys", "bought", "buyed"], "bought", "우리 아빠는 지난달에 새 차를 사셨어요.", "buy → bought"),
  P("The train ___ at the station ten minutes ago.", ["stops", "stopped"], "stopped", "기차는 10분 전에 역에 멈췄어요.", "ten minutes ago → stopped"),
  P("___ she call you last night?", ["Does", "Did", "Was"], "Did", "그녀가 어젯밤에 너한테 전화했니?", "last night + 일반동사 call → Did"),
  P("A: Did you enjoy the trip?  B: Yes, I ___.", ["do", "did", "was"], "did", "A: 여행 즐거웠니? B: 응, 즐거웠어.", "Did you …? 로 물으면 I did 로 답해요"),
  P("He ___ his leg two days ago, so he can't play today.", ["breaks", "broke"], "broke", "그는 이틀 전에 다리를 다쳐서 오늘은 경기를 못 해요.", "two days ago → broke", 1),
  P("I ___ up late this morning and missed the bus.", ["get", "got"], "got", "나는 오늘 아침 늦게 일어나서 버스를 놓쳤어요.", "뒤의 missed 처럼 지난 일 → got", 1),
  P("She usually walks to school, but yesterday she ___ the bus.", ["takes", "took"], "took", "그녀는 보통 걸어서 학교에 가지만 어제는 버스를 탔어요.", "yesterday → took (usually 쪽은 지금 모양)", 1),
  OX("I goed to the park yesterday.", False, "나는 어제 공원에 갔어요.", "I went to the park yesterday.", "go → went"),
  OX("She didn't watch TV last night.", True, "그녀는 어젯밤 TV를 보지 않았어요."),
  OX("Did he went to school yesterday?", False, "그는 어제 학교에 갔니?", "Did he go to school yesterday?", "Did 뒤에는 동사 그대로"),
  OX("We met our teacher at the mall last Saturday.", True, "우리는 지난 토요일에 쇼핑몰에서 선생님을 만났어요."),
  OX("He didn't knew the answer.", False, "그는 답을 몰랐어요.", "He didn't know the answer.", "didn't 뒤에는 동사 그대로"),
  OR("I did not see him yesterday.", "나는 어제 그를 보지 못했어요."),
  OR("Did you finish your homework?", "너 숙제 끝냈니?"),
  OR("She bought a new bag last week.", "그녀는 지난주에 새 가방을 샀어요."),
  OR("We went to the beach last summer.", "우리는 지난여름에 바닷가에 갔어요."),
  FX("I buyed a new notebook yesterday.", "buyed", "bought", "나는 어제 새 공책을 샀어요.", "buy → bought"),
  FX("She didn't came to school yesterday.", "came", "come", "그녀는 어제 학교에 오지 않았어요.", "didn't 뒤에는 동사 그대로"),
  FX("Did you saw the rainbow this morning?", "saw", "see", "오늘 아침에 무지개 봤니?", "Did 뒤에는 동사 그대로"),
  W("We ___ to Jeju last summer. (go)", "went", "우리는 지난여름에 제주에 갔어요.", "go → went"),
  W("She ___ English for two hours yesterday. (study)", "studied", "그녀는 어제 두 시간 동안 영어를 공부했어요.", "study → y 를 i 로 바꾸고 -ed"),
  W("I ___ my friend at the library yesterday. (meet)", "met", "나는 어제 도서관에서 친구를 만났어요.", "meet → met"),
  W("He ___ breakfast this morning. He was too busy. (not, eat)", "didn't eat", "그는 오늘 아침을 안 먹었어요. 너무 바빴어요.", "didn't + 동사 그대로", ["did not eat"]),
  W("My mom ___ a cake for my birthday last week. (make)", "made", "엄마가 지난주 내 생일에 케이크를 만들어 주셨어요.", "make → made"),
  W("___ you sleep well last night? (do)", "did", "어젯밤에 잘 잤니?", "last night → Did"),
]),
# ───────────────────────── 중1 ④ 조동사 ─────────────────────────
G("mid-4", "조동사", "🔑", "중1 · can · must · have to · should", [
  R("조동사 뒤에는 동사 그대로", "can · must · should · will 뒤의 동사에는 -s · -ed · to 를 붙이지 않아요. 주어가 he · she 여도 조동사 모양은 그대로예요.",
    [["🏊", "She swims fast.", "She {can swim} fast.", "그녀는 빨리 수영할 수 있어요."], ["📝", "He studies hard.", "He {must study} hard.", "그는 열심히 공부해야 해요."], ["😴", "You go to bed early.", "You {should go} to bed early.", "너는 일찍 자는 게 좋아."]],
    P("My brother can ___ a bike.", ["ride", "rides", "to ride"], "ride", "내 남동생은 자전거를 탈 수 있어요.", "can 뒤에는 동사 그대로")),
  R("뜻으로 골라요", "can = 할 수 있다 · must · have to = 꼭 해야 한다 · should = 하는 게 좋다(충고)",
    [["💪", "", "I {can} lift this box.", "나는 이 상자를 들 수 있어요. (능력)"], ["🚦", "", "You {must} stop at a red light.", "빨간불에는 꼭 멈춰야 해요. (의무)"], ["🤒", "", "You {should} see a doctor.", "병원에 가 보는 게 좋겠어. (충고)"]],
    P("You look tired. You ___ get some rest.", ["should", "can't"], "should", "피곤해 보여. 좀 쉬는 게 좋겠어.", "충고 → should")),
  R("must not 과 don't have to 는 달라요", "must not = 하면 안 된다(금지) · don't have to = 안 해도 된다(필요 없음). he · she 는 has to · doesn't have to.",
    [["🚫", "", "You {must not} run in the hallway.", "복도에서 뛰면 안 돼요."], ["🆗", "", "You {don't have to} hurry.", "서두르지 않아도 돼요."], ["👧", "", "She {has to} wear a uniform.", "그녀는 교복을 입어야 해요."]],
    P("Tomorrow is Sunday. We ___ go to school.", ["must not", "don't have to"], "don't have to", "내일은 일요일이에요. 학교에 안 가도 돼요.", "가면 안 되는 게 아니라 안 가도 되는 것 → don't have to"), x=1),
], [
  P("She can ___ three languages.", ["speak", "speaks", "speaking"], "speak", "그녀는 세 가지 언어를 할 수 있어요.", "can 뒤에는 동사 그대로"),
  P("He ___ play the violin very well.", ["can", "cans"], "can", "그는 바이올린을 아주 잘 켤 수 있어요.", "조동사에는 -s 를 안 붙여요"),
  P("You must ___ your hands before meals.", ["wash", "to wash", "washing"], "wash", "식사 전에는 꼭 손을 씻어야 해요.", "must 뒤에는 동사 그대로"),
  P("My sister ___ to get up early tomorrow.", ["have", "has"], "has", "우리 언니는 내일 일찍 일어나야 해요.", "my sister = she → has to"),
  P("___ I use your pen?", ["Can", "Do", "Am"], "Can", "네 펜 좀 써도 될까?", "해도 되는지 물을 때 → Can I …?"),
  P("You ___ swim here. It is too dangerous.", ["must not", "don't have to"], "must not", "여기서 수영하면 안 돼요. 너무 위험해요.", "위험 → 금지 → must not"),
  P("It is very cold outside. You ___ wear a coat.", ["should", "should not"], "should", "밖이 아주 추워. 코트를 입는 게 좋겠어.", "충고 → should"),
  P("I ___ find my phone. Did you see it?", ["can", "can't"], "can't", "내 휴대폰을 못 찾겠어. 너 봤니?", "봤는지 묻는 걸 보면 못 찾는 중 → can't"),
  P("We have a lot of time. We ___ hurry.", ["must not", "don't have to"], "don't have to", "우리는 시간이 많아요. 서두르지 않아도 돼요.", "시간이 많다 → 필요 없음 → don't have to"),
  P("He ___ have to wear a uniform at his school.", ["don't", "doesn't"], "doesn't", "그는 학교에서 교복을 안 입어도 돼요.", "he → doesn't have to", 1),
  P("Students ___ use their phones during the test.", ["must not", "don't have to"], "must not", "학생들은 시험 중에 휴대폰을 쓰면 안 돼요.", "시험 중 규칙(금지) → must not", 1),
  P("Does she ___ to finish the report today?", ["have", "has"], "have", "그녀는 오늘 보고서를 끝내야 하니?", "Does 뒤에는 동사 그대로 → have to", 1),
  OX("She cans play the piano.", False, "그녀는 피아노를 칠 수 있어요.", "She can play the piano.", "조동사에는 -s 를 안 붙여요"),
  OX("You should eat more vegetables.", True, "채소를 더 먹는 게 좋아요."),
  OX("He must to finish his homework.", False, "그는 숙제를 끝내야 해요.", "He must finish his homework.", "must 뒤에 to 를 안 써요"),
  OX("My brother has to clean his room.", True, "내 남동생은 방을 청소해야 해요."),
  OX("Can you helps me?", False, "나 좀 도와줄 수 있니?", "Can you help me?", "can 뒤에는 동사 그대로"),
  OR("You must not be late.", "늦으면 안 돼요."),
  OR("Can you open the window?", "창문 좀 열어 줄 수 있니?"),
  OR("She has to study for the test.", "그녀는 시험 공부를 해야 해요."),
  OR("You should not eat too much candy.", "사탕을 너무 많이 먹지 않는 게 좋아요."),
  FX("He can swims very fast.", "swims", "swim", "그는 아주 빨리 수영할 수 있어요.", "can 뒤에는 동사 그대로"),
  FX("She have to go home now.", "have", "has", "그녀는 지금 집에 가야 해요.", "she → has to"),
  FX("You should to drink more water.", "to", "", "물을 더 마시는 게 좋아요.", "should 뒤에 to 를 안 써요"),
  W("My little sister can ___ very well. (sing)", "sing", "내 여동생은 노래를 아주 잘할 수 있어요.", "can 뒤에는 동사 그대로"),
  W("He ___ to wear glasses in class. (have)", "has", "그는 수업 시간에 안경을 써야 해요.", "he → has to"),
  W("You ___ be quiet in the library. (꼭 해야 한다 · m으로 시작)", "must", "도서관에서는 조용히 해야 해요.", "의무 → must"),
  W("You look sick. You ___ see a doctor. (하는 게 좋다 · s로 시작)", "should", "아파 보여. 병원에 가 보는 게 좋겠어.", "충고 → should"),
  W("It is free. You ___ have to pay. (not)", "don't", "그건 무료예요. 돈을 안 내도 돼요.", "you → don't have to", ["do not"]),
  W("She ___ have to cook today. Her dad is cooking. (not)", "doesn't", "그녀는 오늘 요리를 안 해도 돼요. 아빠가 요리하고 계세요.", "she → doesn't have to", ["does not"]),
]),
]

if __name__ == "__main__":
    raw = open(P_, encoding="utf-8").read(); D = json.loads(raw)
    old = {g["id"]: g for g in D.get("mid", [])}
    for g in MID: old[g["id"]] = g
    D["mid"] = sorted(old.values(), key=lambda g: int(g["id"].split("-")[1]))
    compact = "\n" not in raw.strip()[:2000]
    open(P_, "w", encoding="utf-8").write(json.dumps(D, ensure_ascii=False, separators=(",", ":")) if compact else json.dumps(D, ensure_ascii=False, indent=1))
    print({g["id"]: len(g["qs"]) for g in D["mid"]})
