# HY ENG 문법 곁가지 데이터 → data/gram.json
# 카드: R(제목, 한 줄 설명, 예시[[그림, 앞, 뒤, 뜻]], x=주의 카드) · T(같이 해 보기 문제들)
# 문제: P 고르기 · OX 맞아요/틀려요 · OR 순서 맞추기 · FX 틀린 단어 찾기 ({}는 강조)
import json, sys, re

def R(h, p, ex, x=0):
    d = {"k": "rule", "h": h, "p": p, "ex": ex}
    if x: d["x"] = 1
    return d
def T(*qs): return {"k": "try", "q": list(qs)}
def P(s, o, a, ko, w=None, h=None):
    d = {"k": "pick", "s": s, "o": o, "a": a, "ko": ko}
    if w: d["w"] = w
    if h: d["h"] = h
    return d
def OX(s, ok, ko, fix=None, w=None):
    d = {"k": "ox", "s": s, "ok": bool(ok), "ko": ko}
    if fix: d["fix"] = fix
    if w: d["w"] = w
    return d
def OR(words, ko): return {"k": "order", "w": words, "ko": ko}
def FX(s, bad, a, ko, w=None):
    d = {"k": "fix", "s": s, "bad": bad, "a": a, "ko": ko}
    if w: d["w"] = w
    return d
def G(id, at, t, emo, sub, cards, qs): return {"id": id, "at": at, "t": t, "emo": emo, "sub": sub, "cards": cards, "qs": qs}

g34 = [
G("g34-1", 1, "a / an", "🍎", "하나일 때 붙이는 말", [
  R("하나일 때는 a", "물건이나 동물이 하나면 앞에 a 를 붙여요.", [["🐶","","{a} dog","개 한 마리"],["🚗","","{a} car","자동차 한 대"],["📕","","{a} book","책 한 권"]]),
  R("첫소리가 아·에·이·오·어 소리면 an", "a apple 은 말하기 어려워서 an apple 이라고 해요.", [["🍎","","{an} apple","사과 한 개"],["🥚","","{an} egg","달걀 한 개"],["🐘","","{an} elephant","코끼리 한 마리"],["☂️","","{an} umbrella","우산 하나"]], 1),
  T(P("I have ___ cat.", ["a","an"], "a", "나는 고양이가 한 마리 있어요.", "cat 은 '크' 소리로 시작 → a"),
    P("She eats ___ apple.", ["a","an"], "an", "그녀는 사과를 하나 먹어요.", "apple 은 '애' 소리로 시작 → an"))
], [
  P("He has ___ bike.", ["a","an"], "a", "그는 자전거가 한 대 있어요.", "bike 는 '바' 소리 → a"),
  P("It is ___ egg.", ["a","an"], "an", "그것은 달걀이에요.", "egg 는 '에' 소리 → an"),
  P("I see ___ elephant.", ["a","an"], "an", "나는 코끼리 한 마리를 봐요.", "elephant 는 '엘' 소리 → an"),
  P("This is ___ orange.", ["a","an"], "an", "이것은 오렌지예요.", "orange 는 '오' 소리 → an"),
  P("It is ___ big box.", ["a","an"], "a", "그것은 큰 상자예요.", "바로 뒤 big 이 '비' 소리 → a"),
  P("I want ___ ice cream.", ["a","an"], "an", "나는 아이스크림을 하나 원해요.", "ice 는 '아' 소리 → an"),
  P("My mom is ___ teacher.", ["a","an"], "a", "우리 엄마는 선생님이에요.", "teacher 는 '티' 소리 → a"),
  OX("I have a apple.", 0, "나는 사과가 하나 있어요.", "I have an apple."),
  OX("It is an egg.", 1, "그것은 달걀이에요."),
  OX("He is a doctor.", 1, "그는 의사예요."),
  OX("She has an bag.", 0, "그녀는 가방이 하나 있어요.", "She has a bag."),
  OR(["I","have","an","umbrella."], "나는 우산이 하나 있어요."),
  OR(["It","is","a","red","car."], "그것은 빨간 자동차예요."),
  OR(["She","eats","an","egg."], "그녀는 달걀을 하나 먹어요."),
]),
G("g34-2", 2, "여러 개 -s", "🐱", "둘 이상이면 끝에 s", [
  R("여러 개면 끝에 s", "둘 이상이면 단어 끝에 s 를 붙여요.", [["🐱","one cat","two cat{s}","고양이 두 마리"],["🍎","one apple","three apple{s}","사과 세 개"],["📕","a book","five book{s}","책 다섯 권"]]),
  R("s · x · ch · sh 로 끝나면 es", "끝소리가 '스 · 크스 · 치 · 시' 처럼 나면 es 를 붙여요.", [["🚌","a bus","two bus{es}","버스 두 대"],["📦","a box","three box{es}","상자 세 개"],["🍑","a peach","two peach{es}","복숭아 두 개"],["🍽️","a dish","four dish{es}","접시 네 개"]], 1),
  R("모양이 확 바뀌는 단어", "이 단어들은 s 를 붙이지 않고 모양이 바뀌어요.", [["👶","a child","two {children}","아이 둘"],["👨","a man","three {men}","남자 셋"],["🦶","a foot","two {feet}","발 두 개"],["🦷","a tooth","many {teeth}","이 여러 개"]], 1),
  T(P("I have two ___.", ["dog","dogs"], "dogs", "나는 개가 두 마리 있어요.", "둘이니까 s", "dog"),
    P("She has three ___.", ["boxs","boxes"], "boxes", "그녀는 상자가 세 개 있어요.", "x 로 끝나면 es", "box"))
], [
  P("I have two ___.", ["pen","pens"], "pens", "나는 펜이 두 개 있어요.", "둘이니까 s", "pen"),
  P("I see five ___.", ["bird","birds"], "birds", "나는 새 다섯 마리를 봐요.", "다섯이니까 s", "bird"),
  P("I eat two ___.", ["peachs","peaches"], "peaches", "나는 복숭아 두 개를 먹어요.", "ch 로 끝나면 es", "peach"),
  P("The ___ are happy.", ["childs","children"], "children", "아이들이 행복해요.", "child 는 children 으로 바뀌어요", "child"),
  P("I wash my ___.", ["foots","feet"], "feet", "나는 발을 씻어요.", "foot 은 feet 으로 바뀌어요", "foot"),
  P("We need three ___.", ["buss","buses"], "buses", "우리는 버스 세 대가 필요해요.", "s 로 끝나면 es", "bus"),
  P("I have ten ___.", ["finger","fingers"], "fingers", "나는 손가락이 열 개 있어요.", "열이니까 s", "finger"),
  OX("I have two dogs.", 1, "나는 개가 두 마리 있어요."),
  OX("She has three boxs.", 0, "그녀는 상자가 세 개 있어요.", "She has three boxes."),
  OX("The mans are tall.", 0, "그 남자들은 키가 커요.", "The men are tall."),
  OX("I see two buses.", 1, "나는 버스 두 대를 봐요."),
  OR(["I","have","two","brothers."], "나는 남동생이 두 명 있어요."),
  OR(["We","eat","five","apples."], "우리는 사과 다섯 개를 먹어요."),
  OR(["Three","children","are","here."], "아이 세 명이 여기 있어요."),
]),
G("g34-3", 3, "am · are · is", "🙋", "'~이에요' 는 누구냐에 따라", [
  R("나는 am, 너는 are", "'~이에요 · ~해요' 는 누구냐에 따라 am · are · is 로 바뀌어요.", [["🙋","","I {am} happy.","나는 행복해요."],["👉","","You {are} tall.","너는 키가 커요."]]),
  R("한 명 · 한 개면 is", "he · she · it, 그리고 하나인 것은 is 를 써요.", [["👦","","He {is} my friend.","그는 내 친구예요."],["👧","","She {is} kind.","그녀는 친절해요."],["🐶","","It {is} a dog.","그것은 개예요."]]),
  R("여럿이면 are", "we · they, 그리고 여럿인 것은 are 를 써요.", [["👨‍👩‍👧","","We {are} a family.","우리는 가족이에요."],["👫","","They {are} students.","그들은 학생이에요."],["🐱","","The cats {are} cute.","고양이들이 귀여워요."]]),
  T(P("I ___ ten.", ["am","is","are"], "am", "나는 열 살이에요.", "I 다음엔 am"),
    P("They ___ my friends.", ["am","is","are"], "are", "그들은 내 친구들이에요.", "they 는 여럿 → are"))
], [
  P("She ___ a teacher.", ["am","is","are"], "is", "그녀는 선생님이에요.", "she 는 한 명 → is"),
  P("We ___ in the park.", ["am","is","are"], "are", "우리는 공원에 있어요.", "we 는 여럿 → are"),
  P("I ___ hungry.", ["am","is","are"], "am", "나는 배고파요.", "I 다음엔 am"),
  P("You ___ my best friend.", ["am","is","are"], "are", "너는 나의 가장 친한 친구야.", "you 다음엔 are"),
  P("The dog ___ big.", ["am","is","are"], "is", "그 개는 커요.", "개 한 마리 → is"),
  P("Tom and I ___ happy.", ["am","is","are"], "are", "톰과 나는 행복해요.", "Tom and I = 우리 → are"),
  P("It ___ a book.", ["am","is","are"], "is", "그것은 책이에요.", "it 은 하나 → is"),
  OX("I is a student.", 0, "나는 학생이에요.", "I am a student."),
  OX("They are sleepy.", 1, "그들은 졸려요."),
  OX("He are my dad.", 0, "그는 우리 아빠예요.", "He is my dad."),
  OX("The apples are red.", 1, "사과들이 빨개요."),
  OR(["She","is","my","sister."], "그녀는 내 여동생이에요."),
  OR(["We","are","in","the","classroom."], "우리는 교실에 있어요."),
  OR(["I","am","nine","years","old."], "나는 아홉 살이에요."),
]),
G("g34-4", 5, "this · that", "👇", "가까이 · 멀리", [
  R("가까이는 this, 멀리는 that", "손에 닿을 만큼 가까우면 this, 멀리 있으면 that 이에요.", [["👇📕","","{This} is my book.","이것은 내 책이야."],["👉🏠","","{That} is my house.","저것은 우리 집이야."]]),
  R("여러 개면 these · those", "여러 개면 this → these, that → those. 뒤에는 are 가 와요.", [["👇🍎","","{These} are apples.","이것들은 사과야."],["👉⭐","","{Those} are stars.","저것들은 별이야."]], 1),
  T(P("___ is my bag.", ["This","These"], "This", "이것은 내 가방이야.", "가까이 하나 → This", "👇 가까이"),
    P("___ are birds.", ["These","Those"], "Those", "저것들은 새야.", "멀리 여러 개 → Those", "👉 멀리, 여러 개"))
], [
  P("___ is my pencil.", ["This","That"], "This", "이것은 내 연필이야.", "가까이 → This", "👇 가까이"),
  P("___ is a tree.", ["This","That"], "That", "저것은 나무야.", "멀리 → That", "👉 멀리"),
  P("___ are my shoes.", ["These","Those"], "These", "이것들은 내 신발이야.", "가까이 여러 개 → These", "👇 가까이, 여러 개"),
  P("___ are clouds.", ["These","Those"], "Those", "저것들은 구름이야.", "멀리 여러 개 → Those", "👉 멀리, 여러 개"),
  P("These ___ my books.", ["is","are"], "are", "이것들은 내 책이야.", "these 뒤에는 are"),
  P("That ___ a big dog.", ["is","are"], "is", "저것은 큰 개야.", "that 뒤에는 is"),
  OX("This are my cat.", 0, "이것은 내 고양이야.", "This is my cat."),
  OX("Those are birds.", 1, "저것들은 새야."),
  OX("These is red.", 0, "이것들은 빨개.", "These are red."),
  OX("That is my school.", 1, "저것은 우리 학교야."),
  OR(["This","is","my","friend."], "이 아이는 내 친구야."),
  OR(["Those","are","big","trees."], "저것들은 큰 나무야."),
  OR(["These","are","my","shoes."], "이것들은 내 신발이야."),
]),
G("g34-5", 7, "my · your · his · her", "🎒", "누구의 것인지", [
  R("누구의 것인지 말해요", "가방 앞에 누구의 것인지 붙여요.", [["🙋","","{my} bag","나의 가방"],["👉","","{your} bag","너의 가방"],["👦","","{his} bag","그의 가방"],["👧","","{her} bag","그녀의 가방"]]),
  R("여럿의 것 · 동물의 것", "우리 것은 our, 그들 것은 their, 동물이나 물건은 its.", [["👨‍👩‍👧","","{our} house","우리의 집"],["👫","","{their} dog","그들의 개"],["🐶","","{its} tail","그것의 꼬리"]], 1),
  T(P("Mina has a cat. ___ cat is white.", ["His","Her"], "Her", "미나는 고양이가 있어요. 그녀의 고양이는 하얘요.", "미나는 여자 → Her"),
    P("Jack has a bike. ___ bike is blue.", ["His","Her"], "His", "잭은 자전거가 있어요. 그의 자전거는 파래요.", "잭은 남자 → His"))
], [
  P("We have a dog. ___ dog is big.", ["Our","Their"], "Our", "우리는 개가 있어요. 우리 개는 커요.", "we → our"),
  P("I have a bag. ___ bag is red.", ["My","Your"], "My", "나는 가방이 있어요. 내 가방은 빨개요.", "I → my"),
  P("They have a car. ___ car is new.", ["Our","Their"], "Their", "그들은 차가 있어요. 그들의 차는 새것이에요.", "they → their"),
  P("Is this ___ hat? — Yes, it's mine.", ["your","his"], "your", "이거 네 모자니? — 응, 내 거야.", "너에게 묻는 말 → your"),
  P("Tom loves ___ mom.", ["his","her"], "his", "톰은 그의 엄마를 사랑해요.", "Tom 은 남자 → his"),
  P("The bird is in ___ nest.", ["its","their"], "its", "새가 자기 둥지에 있어요.", "새 한 마리 → its"),
  OX("Mina likes his doll.", 0, "미나는 자기 인형을 좋아해요.", "Mina likes her doll."),
  OX("I love my family.", 1, "나는 우리 가족을 사랑해요."),
  OX("Tom rides her bike.", 0, "톰은 자기 자전거를 타요.", "Tom rides his bike."),
  OX("We clean our room.", 1, "우리는 우리 방을 청소해요."),
  OR(["This","is","my","dog."], "이 아이는 내 개야."),
  OR(["Her","name","is","Mina."], "그녀의 이름은 미나예요."),
  OR(["They","love","their","teacher."], "그들은 그들의 선생님을 좋아해요."),
]),
G("g34-6", 9, "he plays (-s)", "⚽", "한 명이면 동사에 s", [
  R("I · you · we · they 는 그대로", "나 · 너 · 우리 · 그들이 하는 일은 동사를 그대로 써요.", [["🙋","","I {play} soccer.","나는 축구를 해요."],["👫","","They {like} pizza.","그들은 피자를 좋아해요."]]),
  R("한 명(he · she · it)이면 동사에 s", "다른 한 사람이나 하나가 하는 일이면 동사 끝에 s 를 붙여요.", [["👦","","He play{s} soccer.","그는 축구를 해요."],["👧","","She like{s} pizza.","그녀는 피자를 좋아해요."],["🐶","","It run{s} fast.","그것은 빨리 달려요."]]),
  R("es 를 붙이는 동사 · has", "go · do · watch · wash 는 es, have 는 has 가 돼요.", [["🏫","go","She {goes} to school.","그녀는 학교에 가요."],["📺","watch","He watch{es} TV.","그는 TV 를 봐요."],["🐱","have","She {has} a cat.","그녀는 고양이가 있어요."]], 1),
  T(P("He ___ milk.", ["drink","drinks"], "drinks", "그는 우유를 마셔요.", "he → 동사에 s"),
    P("We ___ English.", ["learn","learns"], "learn", "우리는 영어를 배워요.", "we → 그대로"))
], [
  P("She ___ the piano.", ["play","plays"], "plays", "그녀는 피아노를 쳐요.", "she → 동사에 s"),
  P("My dad ___ to work.", ["go","goes"], "goes", "우리 아빠는 일하러 가요.", "아빠 한 명 → goes"),
  P("I ___ my teeth.", ["brush","brushes"], "brush", "나는 이를 닦아요.", "I → 그대로"),
  P("Tom ___ a dog.", ["have","has"], "has", "톰은 개가 있어요.", "Tom 한 명 → has"),
  P("They ___ books.", ["read","reads"], "read", "그들은 책을 읽어요.", "they → 그대로"),
  P("The cat ___ fish.", ["eat","eats"], "eats", "그 고양이는 생선을 먹어요.", "고양이 한 마리 → eats"),
  P("Mina ___ TV at night.", ["watch","watches"], "watches", "미나는 밤에 TV 를 봐요.", "watch → watches"),
  OX("He like apples.", 0, "그는 사과를 좋아해요.", "He likes apples."),
  OX("She goes to school.", 1, "그녀는 학교에 가요."),
  OX("I plays games.", 0, "나는 게임을 해요.", "I play games."),
  OX("My mom has a car.", 1, "우리 엄마는 차가 있어요."),
  OR(["She","reads","a","book."], "그녀는 책을 읽어요."),
  OR(["He","goes","to","school."], "그는 학교에 가요."),
  OR(["My","brother","likes","pizza."], "내 남동생은 피자를 좋아해요."),
]),
G("g34-7", 11, "묻는 문장 ?", "❓", "Are you…? Do you…?", [
  R("am · are · is 는 앞으로", "묻고 싶으면 am · are · is 를 맨 앞으로 보내요.", [["😋","You are hungry.","{Are} you hungry?","너 배고프니?"],["🦒","He is tall.","{Is} he tall?","그는 키가 크니?"]]),
  R("동사 문장은 Do · Does 로 시작", "한 명(he · she · it)이면 Does. Does 뒤 동사는 s 없이 써요.", [["🐱","You like cats.","{Do} you like cats?","너는 고양이를 좋아하니?"],["🐱","She likes cats.","{Does} she like cats?","그녀는 고양이를 좋아하니?"]]),
  R("대답하기", "물어본 말로 짧게 대답해요.", [["🙆","Are you hungry?","Yes, I {am}. / No, I'm not.","응. / 아니."],["🙆","Do you like cats?","Yes, I {do}. / No, I {don't}.","응. / 아니."]], 1),
  T(P("___ you happy?", ["Are","Do"], "Are", "너 행복하니?", "happy 앞엔 be → Are"),
    P("___ he play soccer?", ["Do","Does"], "Does", "그는 축구를 하니?", "he → Does"))
], [
  P("___ she your sister?", ["Is","Does"], "Is", "그녀가 네 여동생이니?", "'~이니?' → Is"),
  P("___ they like milk?", ["Do","Does"], "Do", "그들은 우유를 좋아하니?", "they → Do"),
  P("___ it a cat?", ["Is","Do"], "Is", "그것은 고양이니?", "'~이니?' → Is"),
  P("___ Tom have a bike?", ["Do","Does"], "Does", "톰은 자전거가 있니?", "Tom 한 명 → Does"),
  P("Does she ___ to school?", ["go","goes"], "go", "그녀는 학교에 가니?", "Does 뒤 동사는 s 없이"),
  P("Are you a student? — Yes, I ___.", ["am","do"], "am", "너는 학생이니? — 응, 맞아.", "Are 로 물으면 am 으로 대답"),
  P("Do you like pizza? — No, I ___.", ["don't","am not"], "don't", "피자 좋아하니? — 아니.", "Do 로 물으면 don't 로 대답"),
  OX("Does he likes music?", 0, "그는 음악을 좋아하니?", "Does he like music?"),
  OX("Are they your friends?", 1, "그들이 네 친구들이니?"),
  OX("Do she swim?", 0, "그녀는 수영을 하니?", "Does she swim?"),
  OX("Is it your pencil?", 1, "그거 네 연필이니?"),
  OR(["Are","you","hungry?"], "너 배고프니?"),
  OR(["Do","you","like","dogs?"], "너는 개를 좋아하니?"),
  OR(["Does","she","play","the","piano?"], "그녀는 피아노를 치니?"),
]),
G("g34-8", 13, "아니에요 not", "🙅", "isn't · don't · doesn't", [
  R("am · are · is 뒤에 not", "'~이 아니에요' 는 am · are · is 뒤에 not 을 붙여요. 줄이면 isn't · aren't.", [["🦒","He is tall.","He is {not} tall.","그는 키가 크지 않아요."],["😋","They are hungry.","They {aren't} hungry.","그들은 배고프지 않아요."]]),
  R("동사 문장은 don't · doesn't", "한 명(he · she · it)이면 doesn't. doesn't 뒤 동사는 s 없이 써요.", [["🥕","I like carrots.","I {don't} like carrots.","나는 당근을 안 좋아해요."],["🥕","She likes carrots.","She {doesn't} like carrots.","그녀는 당근을 안 좋아해요."]]),
  T(P("I ___ like spiders.", ["don't","doesn't"], "don't", "나는 거미를 안 좋아해요.", "I → don't"),
    P("It ___ a cat.", ["isn't","don't"], "isn't", "그것은 고양이가 아니에요.", "'~이 아니에요' → isn't"))
], [
  P("He ___ eat fish.", ["don't","doesn't"], "doesn't", "그는 생선을 안 먹어요.", "he → doesn't"),
  P("We ___ tired.", ["aren't","don't"], "aren't", "우리는 피곤하지 않아요.", "tired 앞엔 be → aren't"),
  P("She ___ a doctor.", ["isn't","doesn't"], "isn't", "그녀는 의사가 아니에요.", "'~이 아니에요' → isn't"),
  P("They ___ play games at night.", ["don't","doesn't"], "don't", "그들은 밤에 게임을 안 해요.", "they → don't"),
  P("My cat doesn't ___ milk.", ["drink","drinks"], "drink", "우리 고양이는 우유를 안 마셔요.", "doesn't 뒤 동사는 s 없이"),
  P("I ___ not hungry.", ["am","do"], "am", "나는 배고프지 않아요.", "hungry 앞엔 be → am"),
  P("Tom ___ have a phone.", ["don't","doesn't"], "doesn't", "톰은 휴대폰이 없어요.", "Tom 한 명 → doesn't"),
  OX("She don't like rain.", 0, "그녀는 비를 안 좋아해요.", "She doesn't like rain."),
  OX("I am not sleepy.", 1, "나는 졸리지 않아요."),
  OX("He doesn't plays soccer.", 0, "그는 축구를 안 해요.", "He doesn't play soccer."),
  OX("They aren't at home.", 1, "그들은 집에 없어요."),
  OR(["I","don't","like","onions."], "나는 양파를 안 좋아해요."),
  OR(["She","is","not","my","sister."], "그녀는 내 여동생이 아니에요."),
  OR(["He","doesn't","eat","meat."], "그는 고기를 안 먹어요."),
]),
]

g56 = [
G("g56-1", 2, "지금 하는 중 -ing", "🏃", "be + 동사ing", [
  R("지금 하고 있어요 = am · are · is + ing", "지금 하는 중인 일은 be 동사 뒤에 동사ing 를 써요.", [["🏃","","I {am running}.","나는 달리고 있어요."],["📖","","She {is reading} a book.","그녀는 책을 읽고 있어요."],["⚽","","They {are playing} soccer.","그들은 축구를 하고 있어요."]]),
  R("ing 붙이는 방법", "e 로 끝나면 e 를 빼고, 짧은 단어는 끝 글자를 한 번 더 써요.", [["🎂","make","mak{ing}","만들고 있는"],["🏊","swim","swim{ming}","수영하고 있는"],["🏃","run","run{ning}","달리고 있는"],["🪑","sit","sit{ting}","앉아 있는"]], 1),
  T(P("He is ___ a song.", ["sing","singing"], "singing", "그는 노래를 부르고 있어요.", "is 뒤엔 ing"),
    P("We ___ eating lunch.", ["is","are"], "are", "우리는 점심을 먹고 있어요.", "we → are"))
], [
  P("Look! The baby is ___.", ["sleep","sleeping"], "sleeping", "봐! 아기가 자고 있어.", "is 뒤엔 ing"),
  P("I am ___ a cake.", ["makeing","making"], "making", "나는 케이크를 만들고 있어요.", "e 로 끝나면 e 빼고 ing"),
  P("They are ___ in the pool.", ["swiming","swimming"], "swimming", "그들은 수영장에서 수영하고 있어요.", "swim → swimming (m 한 번 더)"),
  P("She ___ watching TV now.", ["is","are"], "is", "그녀는 지금 TV 를 보고 있어요.", "she → is"),
  P("My dad ___ cooking dinner.", ["is","are"], "is", "아빠는 저녁을 요리하고 있어요.", "아빠 한 명 → is"),
  P("We are ___ to music.", ["listen","listening"], "listening", "우리는 음악을 듣고 있어요.", "are 뒤엔 ing"),
  P("What are you doing? — I am ___ a letter.", ["writing","writeing"], "writing", "뭐 하고 있니? — 편지를 쓰고 있어.", "e 로 끝나면 e 빼고 ing"),
  OX("He is runing fast.", 0, "그는 빨리 달리고 있어요.", "He is running fast."),
  OX("They are dancing now.", 1, "그들은 지금 춤추고 있어요."),
  OX("I am eat lunch.", 0, "나는 점심을 먹고 있어요.", "I am eating lunch."),
  OX("She is sitting on the bench.", 1, "그녀는 벤치에 앉아 있어요."),
  OR(["She","is","drawing","a","picture."], "그녀는 그림을 그리고 있어요."),
  OR(["We","are","waiting","for","the","bus."], "우리는 버스를 기다리고 있어요."),
  OR(["What","are","you","doing?"], "너 뭐 하고 있니?"),
  FX("He are playing the guitar.", "are", "is", "그는 기타를 치고 있어요.", "he → is"),
  FX("I am drink milk now.", "drink", "drinking", "나는 지금 우유를 마시고 있어요.", "am 뒤엔 ing"),
]),
G("g56-2", 5, "했어요 -ed", "📅", "과거: 동사 + ed", [
  R("이미 한 일 = 동사 + ed", "어제 · 지난주처럼 지나간 일은 동사 끝에 ed 를 붙여요.", [["⚽","I play soccer.","I play{ed} soccer yesterday.","나는 어제 축구를 했어요."],["🚶","She walks to school.","She walk{ed} to school.","그녀는 학교에 걸어갔어요."],["🎬","","We watch{ed} a movie last night.","우리는 어젯밤 영화를 봤어요."]]),
  R("ed 붙이는 방법", "e 로 끝나면 d 만, 자음 + y 는 y 를 i 로, 짧은 단어는 끝 글자 한 번 더.", [["❤️","like","lik{ed}","좋아했다"],["📚","study","stud{ied}","공부했다"],["✋","stop","stop{ped}","멈췄다"],["😢","cry","cr{ied}","울었다"]], 1),
  R("지나간 때를 알려 주는 말", "이런 말이 보이면 과거로 써요.", [["📅","","{yesterday}","어제"],["🗓️","","{last} week · {last} night","지난주 · 어젯밤"],["⏳","","two days {ago}","이틀 전"]], 1),
  T(P("I ___ my room yesterday.", ["clean","cleaned"], "cleaned", "나는 어제 내 방을 청소했어요.", "yesterday → ed"),
    P("She ___ English last year.", ["studyed","studied"], "studied", "그녀는 작년에 영어를 공부했어요.", "study → studied"))
], [
  P("We ___ to music last night.", ["listen","listened"], "listened", "우리는 어젯밤 음악을 들었어요.", "last night → ed"),
  P("He ___ the door an hour ago.", ["opens","opened"], "opened", "그는 한 시간 전에 문을 열었어요.", "ago → 과거"),
  P("They ___ basketball yesterday.", ["play","played"], "played", "그들은 어제 농구를 했어요.", "yesterday → ed"),
  P("I ___ my grandma last Sunday.", ["visit","visited"], "visited", "나는 지난 일요일에 할머니를 찾아뵀어요.", "last Sunday → ed"),
  P("The bus ___ suddenly.", ["stoped","stopped"], "stopped", "버스가 갑자기 멈췄어요.", "stop → stopped (p 한 번 더)"),
  P("She ___ the cake.", ["liked","likeed"], "liked", "그녀는 그 케이크를 좋아했어요.", "e 로 끝나면 d 만"),
  P("My brother ___ hard for the test.", ["studied","studyed"], "studied", "형은 시험 공부를 열심히 했어요.", "study → studied"),
  OX("I watched TV yesterday.", 1, "나는 어제 TV 를 봤어요."),
  OX("We play tennis yesterday.", 0, "우리는 어제 테니스를 쳤어요.", "We played tennis yesterday."),
  OX("They studyed math.", 0, "그들은 수학을 공부했어요.", "They studied math."),
  OX("She cleaned her room last week.", 1, "그녀는 지난주에 방을 청소했어요."),
  OR(["I","helped","my","mom","yesterday."], "나는 어제 엄마를 도와드렸어요."),
  OR(["We","walked","to","the","park."], "우리는 공원까지 걸어갔어요."),
  OR(["She","visited","her","uncle","last","week."], "그녀는 지난주에 삼촌을 찾아갔어요."),
  FX("He wash his car yesterday.", "wash", "washed", "그는 어제 세차를 했어요.", "yesterday → ed"),
  FX("I cryed last night.", "cryed", "cried", "나는 어젯밤에 울었어요.", "cry → cried"),
]),
G("g56-3", 8, "went · ate · saw", "🔁", "모양이 바뀌는 과거", [
  R("모양이 바뀌는 과거", "자주 쓰는 동사는 ed 대신 모양이 바뀌어요. 짝으로 외워요.", [["🚶","go","{went}","갔다"],["🍽️","eat","{ate}","먹었다"],["👀","see","{saw}","봤다"],["🎒","have","{had}","가졌다"],["🔨","make","{made}","만들었다"],["🏠","come","{came}","왔다"]]),
  R("더 알아 두기", "이것도 자주 나와요.", [["🛍️","buy","{bought}","샀다"],["✍️","write","{wrote}","썼다"],["🏊","swim","{swam}","수영했다"],["📷","take","{took}","찍었다 · 가져갔다"],["🎁","get","{got}","받았다"]], 1),
  R("am · is → was, are → were", "be 동사도 과거가 있어요.", [["😴","I am tired.","I {was} tired.","나는 피곤했어요."],["🏠","They are at home.","They {were} at home.","그들은 집에 있었어요."]], 1),
  T(P("I ___ to the zoo yesterday.", ["goed","went"], "went", "나는 어제 동물원에 갔어요.", "go → went"),
    P("We ___ pizza last night.", ["ate","eated"], "ate", "우리는 어젯밤 피자를 먹었어요.", "eat → ate"))
], [
  P("She ___ a bird in the tree.", ["saw","seed"], "saw", "그녀는 나무에 있는 새를 봤어요.", "see → saw"),
  P("He ___ a new bike.", ["buyed","bought"], "bought", "그는 새 자전거를 샀어요.", "buy → bought"),
  P("I ___ a letter to Tom.", ["wrote","writed"], "wrote", "나는 톰에게 편지를 썼어요.", "write → wrote"),
  P("They ___ happy yesterday.", ["was","were"], "were", "그들은 어제 행복했어요.", "they → were"),
  P("It ___ cold last night.", ["was","were"], "was", "어젯밤은 추웠어요.", "it → was"),
  P("We ___ a lot of fun.", ["had","haved"], "had", "우리는 아주 재미있었어요.", "have → had"),
  P("Mom ___ cookies for us.", ["made","maked"], "made", "엄마가 우리에게 쿠키를 만들어 주셨어요.", "make → made"),
  OX("I goed to school.", 0, "나는 학교에 갔어요.", "I went to school."),
  OX("She ate an apple.", 1, "그녀는 사과를 먹었어요."),
  OX("We was late.", 0, "우리는 늦었어요.", "We were late."),
  OX("He took a picture.", 1, "그는 사진을 찍었어요."),
  OR(["We","went","to","the","beach."], "우리는 바닷가에 갔어요."),
  OR(["I","saw","a","rainbow."], "나는 무지개를 봤어요."),
  OR(["She","was","very","tired."], "그녀는 아주 피곤했어요."),
  FX("I swimmed in the lake.", "swimmed", "swam", "나는 호수에서 수영했어요.", "swim → swam"),
  FX("They was at the library.", "was", "were", "그들은 도서관에 있었어요.", "they → were"),
]),
G("g56-4", 11, "Did …? didn't", "🤔", "과거로 묻기 · 아니라고 하기", [
  R("과거 질문은 Did", "Did 를 맨 앞에 두고, 뒤 동사는 원래 모양으로 돌려요.", [["⚽","You played soccer.","{Did} you play soccer?","너 축구했니?"],["🏠","She went home.","{Did} she go home?","그녀는 집에 갔니?"]]),
  R("'안 했어요' 는 didn't", "didn't 뒤 동사도 원래 모양이에요.", [["🍳","I ate breakfast.","I {didn't} eat breakfast.","나는 아침을 안 먹었어요."],["🏫","He went to school.","He {didn't} go to school.","그는 학교에 안 갔어요."]]),
  R("대답하기", "Did 로 물으면 did · didn't 로 대답해요.", [["🙆","Did you have fun?","Yes, I {did}. / No, I {didn't}.","응. / 아니."]], 1),
  T(P("___ you see the movie yesterday?", ["Did","Do"], "Did", "너 어제 그 영화 봤니?", "yesterday → Did"),
    P("She didn't ___ her homework.", ["do","did"], "do", "그녀는 숙제를 안 했어요.", "didn't 뒤엔 원래 모양"))
], [
  P("___ they come to the party last night?", ["Did","Do"], "Did", "그들은 어젯밤 파티에 왔니?", "last night → Did"),
  P("Did he ___ the window?", ["break","broke"], "break", "그가 창문을 깼니?", "Did 뒤엔 원래 모양"),
  P("I didn't ___ TV yesterday.", ["watch","watched"], "watch", "나는 어제 TV 를 안 봤어요.", "didn't 뒤엔 원래 모양"),
  P("We ___ go out last weekend.", ["didn't","don't"], "didn't", "우리는 지난 주말에 밖에 안 나갔어요.", "last weekend → didn't"),
  P("Did you have fun? — Yes, I ___.", ["did","do"], "did", "재미있었니? — 응.", "Did 로 물으면 did"),
  P("Did she call you? — No, she ___.", ["didn't","doesn't"], "didn't", "그녀가 전화했니? — 아니.", "Did 로 물으면 didn't"),
  P("___ Mina buy a new bag last week?", ["Did","Does"], "Did", "미나는 지난주에 새 가방을 샀니?", "last week → Did"),
  OX("Did you went to the park?", 0, "너 공원에 갔니?", "Did you go to the park?"),
  OX("I didn't sleep well.", 1, "나는 잠을 잘 못 잤어요."),
  OX("She didn't liked the soup.", 0, "그녀는 그 수프를 안 좋아했어요.", "She didn't like the soup."),
  OX("Did they win the game?", 1, "그들이 경기에서 이겼니?"),
  OR(["Did","you","finish","your","homework?"], "너 숙제 다 했니?"),
  OR(["I","didn't","bring","my","umbrella."], "나는 우산을 안 가져왔어요."),
  OR(["Did","she","call","you","yesterday?"], "그녀가 어제 너에게 전화했니?"),
  FX("He didn't came to school.", "came", "come", "그는 학교에 안 왔어요.", "didn't 뒤엔 원래 모양"),
  FX("Did you saw the rainbow?", "saw", "see", "너 무지개 봤니?", "Did 뒤엔 원래 모양"),
]),
G("g56-5", 14, "will · be going to", "🔮", "앞으로 할 일", [
  R("앞으로 할 일 = will + 동사", "누가 하든 will 은 그대로, 뒤 동사는 원래 모양이에요.", [["🤝","","I {will} help you.","내가 도와줄게."],["🌧️","","It {will} rain tomorrow.","내일 비가 올 거예요."],["⏰","","I {won't} be late.","늦지 않을게요. (won't = will not)"]]),
  R("미리 정한 계획 = be going to + 동사", "am · are · is 는 누구냐에 따라 바뀌어요.", [["👵","","I {am going to} visit my grandma.","나는 할머니 댁에 갈 거예요."],["🏊","","She {is going to} learn swimming.","그녀는 수영을 배울 거예요."],["⚾","","They {are going to} play baseball.","그들은 야구를 할 거예요."]]),
  T(P("I will ___ you tomorrow.", ["call","calls"], "call", "내일 전화할게.", "will 뒤엔 원래 모양"),
    P("She ___ going to buy a bike.", ["is","are"], "is", "그녀는 자전거를 살 거예요.", "she → is"))
], [
  P("It will ___ sunny tomorrow.", ["be","is"], "be", "내일은 맑을 거예요.", "will 뒤엔 be"),
  P("We are going to ___ a movie.", ["watch","watching"], "watch", "우리는 영화를 볼 거예요.", "going to 뒤엔 원래 모양"),
  P("He ___ come back soon.", ["will","wills"], "will", "그는 곧 돌아올 거예요.", "will 은 늘 그대로"),
  P("They ___ going to have a party.", ["is","are"], "are", "그들은 파티를 열 거예요.", "they → are"),
  P("I ___ be late again. I promise!", ["won't","will"], "won't", "다시는 안 늦을게. 약속해!", "약속 = 안 늦을게 → won't"),
  P("Tom will ___ his homework after dinner.", ["do","does"], "do", "톰은 저녁 먹고 숙제를 할 거예요.", "will 뒤엔 원래 모양"),
  P("I ___ going to visit Busan next week.", ["am","will"], "am", "나는 다음 주에 부산에 갈 거예요.", "I + going to → am"),
  OX("She will goes to the market.", 0, "그녀는 시장에 갈 거예요.", "She will go to the market."),
  OX("I am going to read this book.", 1, "나는 이 책을 읽을 거예요."),
  OX("We will be there at 5.", 1, "우리는 5시에 거기 갈게요."),
  OX("He are going to sing.", 0, "그는 노래할 거예요.", "He is going to sing."),
  OR(["I","will","help","you."], "내가 도와줄게."),
  OR(["We","are","going","to","play","soccer."], "우리는 축구를 할 거예요."),
  OR(["It","will","snow","tomorrow."], "내일 눈이 올 거예요."),
  FX("She will makes a cake.", "makes", "make", "그녀는 케이크를 만들 거예요.", "will 뒤엔 원래 모양"),
  FX("They is going to travel.", "is", "are", "그들은 여행을 갈 거예요.", "they → are"),
]),
G("g56-6", 17, "더 · 가장 (-er · -est)", "🏆", "비교하기", [
  R("더 ~해요 = er + than", "둘을 비교할 때 끝에 er 을 붙이고 than(~보다)을 써요.", [["🐘","","An elephant is big{ger} than a mouse.","코끼리는 쥐보다 커요."],["🦒","tall","tall{er} than","~보다 키가 큰"],["🚀","fast","fast{er} than","~보다 빠른"]]),
  R("가장 ~해요 = the + est", "셋 이상에서 제일일 때 the ~est 를 써요.", [["🏆","","He is the tall{est} in my class.","그는 우리 반에서 가장 키가 커요."],["📦","","This is the small{est} box.","이것이 가장 작은 상자예요."]]),
  R("긴 단어는 more · most, 모양이 바뀌는 단어", "긴 단어는 앞에 more · most. good 과 bad 는 모양이 바뀌어요.", [["🌸","beautiful","{more} beautiful · the {most} beautiful","더 아름다운 · 가장 아름다운"],["👍","good","{better} · the {best}","더 좋은 · 가장 좋은"],["👎","bad","{worse} · the {worst}","더 나쁜 · 가장 나쁜"],["🐘","big","big{ger} · happ{ier}","g 한 번 더 · y 는 i"]], 1),
  T(P("A car is ___ than a bike.", ["faster","fastest"], "faster", "자동차는 자전거보다 빨라요.", "than → er"),
    P("She is the ___ girl in the team.", ["taller","tallest"], "tallest", "그녀는 팀에서 가장 키가 커요.", "the → est"))
], [
  P("My bag is ___ than yours.", ["heavier","heavyer"], "heavier", "내 가방이 네 것보다 무거워.", "heavy → heavier"),
  P("This is the ___ day of my life!", ["best","goodest"], "best", "오늘은 내 인생 최고의 날이야!", "good → best"),
  P("Math is ___ than art for me.", ["more difficult","difficulter"], "more difficult", "나에게는 수학이 미술보다 어려워요.", "긴 단어 → more"),
  P("The cheetah is the ___ animal.", ["faster","fastest"], "fastest", "치타는 가장 빠른 동물이에요.", "the → est"),
  P("Today is ___ than yesterday.", ["hotter","hoter"], "hotter", "오늘은 어제보다 더워요.", "hot → hotter (t 한 번 더)"),
  P("Seoul is ___ than my town.", ["bigger","biggest"], "bigger", "서울은 우리 동네보다 커요.", "than → er"),
  P("This movie is ___ interesting of all.", ["the most","more"], "the most", "이 영화가 모든 것 중에 가장 재미있어요.", "of all(모든 것 중) → the most"),
  OX("A whale is bigger than a dog.", 1, "고래는 개보다 커요."),
  OX("He is the most tall boy.", 0, "그는 가장 키가 큰 소년이에요.", "He is the tallest boy."),
  OX("My sister is younger than me.", 1, "내 여동생은 나보다 어려요."),
  OX("This is gooder than that.", 0, "이게 저것보다 좋아요.", "This is better than that."),
  OR(["My","dad","is","taller","than","my","mom."], "아빠는 엄마보다 키가 커요."),
  OR(["This","is","the","biggest","pizza."], "이것이 가장 큰 피자예요."),
  OR(["Winter","is","colder","than","fall."], "겨울은 가을보다 추워요."),
  FX("He is the fastest than me.", "fastest", "faster", "그는 나보다 빨라요.", "than → er"),
  FX("It is the bigest cake.", "bigest", "biggest", "그것은 가장 큰 케이크예요.", "big → biggest (g 한 번 더)"),
]),
G("g56-7", 20, "can · must · should", "💪", "할 수 있다 · 해야 한다", [
  R("할 수 있어요 = can", "can 뒤 동사는 원래 모양. 못 하면 can't.", [["🏊","","I {can} swim.","나는 수영할 수 있어요."],["🗣️","","She {can} speak English.","그녀는 영어를 할 수 있어요."],["🐴","","I {can't} ride a horse.","나는 말을 못 타요."]]),
  R("꼭 해야 해요 must · 하는 게 좋아요 should", "must 는 규칙처럼 강하게, should 는 조언처럼 부드럽게.", [["🚗","","You {must} wear a seat belt.","안전벨트를 꼭 매야 해요."],["💧","","You {should} drink water.","물을 마시는 게 좋아요."],["🍬","","You {shouldn't} eat too much candy.","사탕을 너무 많이 먹지 않는 게 좋아요."]]),
  R("묻는 말", "can · should 를 맨 앞으로 보내면 묻는 말이 돼요.", [["✏️","","{Can} I use your pen?","펜 좀 써도 돼?"],["🍱","","{Should} I bring my lunch?","점심을 가져와야 해?"]], 1),
  T(P("Birds ___ fly.", ["can","can't"], "can", "새는 날 수 있어요.", "새는 날 수 있으니까 can"),
    P("You ___ stop at a red light.", ["must","can't"], "must", "빨간불에는 꼭 멈춰야 해요.", "규칙 → must"))
], [
  P("Penguins ___ fly.", ["can","can't"], "can't", "펭귄은 날 수 없어요.", "펭귄은 못 날아요 → can't"),
  P("She can ___ the piano.", ["play","plays"], "play", "그녀는 피아노를 칠 수 있어요.", "can 뒤엔 원래 모양"),
  P("You ___ wash your hands before dinner.", ["should","shouldn't"], "should", "저녁 먹기 전에 손을 씻는 게 좋아요.", "좋은 습관 → should"),
  P("You ___ run in the hallway.", ["should","shouldn't"], "shouldn't", "복도에서 뛰지 않는 게 좋아요.", "위험해요 → shouldn't"),
  P("We ___ be quiet in the library.", ["must","can't"], "must", "도서관에서는 꼭 조용히 해야 해요.", "규칙 → must"),
  P("___ I open the window?", ["Can","Do"], "Can", "창문 열어도 돼요?", "허락 구하기 → Can"),
  P("He should ___ to bed early.", ["go","goes"], "go", "그는 일찍 자는 게 좋아요.", "should 뒤엔 원래 모양"),
  OX("She can sings well.", 0, "그녀는 노래를 잘해요.", "She can sing well."),
  OX("You must wear a helmet.", 1, "헬멧을 꼭 써야 해요."),
  OX("I can't find my key.", 1, "열쇠를 못 찾겠어요."),
  OX("He shoulds study.", 0, "그는 공부하는 게 좋아요.", "He should study."),
  OR(["Can","you","help","me?"], "나 좀 도와줄 수 있어?"),
  OR(["You","should","eat","breakfast."], "아침을 먹는 게 좋아요."),
  OR(["We","must","not","be","late."], "우리는 절대 늦으면 안 돼요."),
  FX("He can speaks Chinese.", "speaks", "speak", "그는 중국어를 할 수 있어요.", "can 뒤엔 원래 모양"),
  FX("You must to wear a mask.", "to", "", "마스크를 꼭 써야 해요.", "must 뒤엔 to 없이 바로 동사"),
]),
G("g56-8", 23, "at · on · in (때)", "⏰", "시각 · 요일 · 달", [
  R("시각은 at", "몇 시, 정오, 밤처럼 딱 한 때는 at.", [["⏰","","{at} 7 o'clock","7시에"],["🕛","","{at} noon","정오에"],["🌙","","{at} night","밤에"]]),
  R("요일 · 날짜는 on", "달력의 한 칸(하루)은 on.", [["📅","","{on} Monday","월요일에"],["🎈","","{on} May 5th","5월 5일에"],["🎂","","{on} my birthday","내 생일에"]]),
  R("달 · 계절 · 해 · 아침저녁은 in", "긴 시간 안에 있을 때는 in.", [["🌸","","{in} March","3월에"],["☀️","","{in} summer","여름에"],["📆","","{in} 2026","2026년에"],["🌅","","{in} the morning","아침에"]]),
  T(P("I get up ___ 7.", ["at","on"], "at", "나는 7시에 일어나요.", "시각 → at"),
    P("We go camping ___ summer.", ["in","on"], "in", "우리는 여름에 캠핑을 가요.", "계절 → in"))
], [
  P("School starts ___ 9 o'clock.", ["at","in"], "at", "학교는 9시에 시작해요.", "시각 → at"),
  P("My birthday is ___ June.", ["in","on"], "in", "내 생일은 6월이에요.", "달 → in"),
  P("I have piano class ___ Tuesday.", ["on","in"], "on", "나는 화요일에 피아노 수업이 있어요.", "요일 → on"),
  P("We see stars ___ night.", ["at","in"], "at", "우리는 밤에 별을 봐요.", "at night"),
  P("It snows ___ winter.", ["in","at"], "in", "겨울에는 눈이 와요.", "계절 → in"),
  P("Children's Day is ___ May 5th.", ["on","in"], "on", "어린이날은 5월 5일이에요.", "날짜 → on"),
  P("I read books ___ the evening.", ["in","on"], "in", "나는 저녁에 책을 읽어요.", "in the evening"),
  OX("I was born in 2015.", 1, "나는 2015년에 태어났어요."),
  OX("See you on Friday!", 1, "금요일에 만나!"),
  OX("The movie starts in 3 o'clock.", 0, "영화는 3시에 시작해요.", "The movie starts at 3 o'clock."),
  OX("We have a test at Monday.", 0, "우리는 월요일에 시험이 있어요.", "We have a test on Monday."),
  OR(["I","go","swimming","on","Saturday."], "나는 토요일에 수영하러 가요."),
  OR(["The","party","is","at","six."], "파티는 6시예요."),
  OR(["Flowers","bloom","in","spring."], "꽃은 봄에 피어요."),
  FX("I go to bed in 10 o'clock.", "in", "at", "나는 10시에 자요.", "시각 → at"),
  FX("My birthday is in July 7th.", "in", "on", "내 생일은 7월 7일이에요.", "날짜 → on"),
]),
]


# ───── (v386b) 사용자: 별 6개 · 별마다 💎5 · 별이 오를수록 어렵게 · 설명을 정말 잘 (누가 = 주어 바꾸기, 언제 쓰는지) ─────
def H(s, o, a, ko, w=None, h=None):
    d = P(s, o, a, ko, w, h); d["hd"] = 1; return d
WHO = lambda tail: R("누가 하는지 먼저 찾아요", "이름이나 여러 사람은 I · you · he · she · it · we · they 중 하나로 바꿔 생각해요. "+tail, [["🙋👧","Mina and I","→ {we}","미나와 나 = 우리"],["👫","Mina and Tom","→ {they}","미나와 톰 = 그들"],["👦","my brother","→ {he}","내 남동생 = 그"],["👩","my mom","→ {she}","우리 엄마 = 그녀"],["🐶","my dog","→ {it}","우리 개 = 그것"]])
CARDS = {   # id: [(넣을 자리, 카드)] — 자리는 설명 카드 순서(0부터), try 앞
 "g34-1": [(2, R("언제 a · an 을 안 붙일까요?", "이름, 물처럼 셀 수 없는 것, 여러 개일 때는 a · an 을 붙이지 않아요.", [["👧","","Mina is my friend.","이름 → 안 붙여요"],["💧","","I drink water.","셀 수 없는 것 → 안 붙여요"],["🍎","","I like apples.","여러 개 → 안 붙여요"]], 1))],
 "g34-2": [(1, R("언제 s 를 붙일까요?", "two · three · many · some 처럼 '여럿'을 알려 주는 말 뒤에 와요. 하나면 그대로!", [["☝️","","one cat · a cat","하나 → 그대로"],["✌️","","two cat{s}","둘 → s"],["📚","","many book{s}","많은 → s"]]))],
 "g34-3": [(3, WHO("그다음 we · they 면 are, he · she · it 이면 is.")), (4, R("언제 써요?", "'~이에요', '~해요(기분 · 모양)', '~에 있어요' 를 말할 때 써요.", [["🧑‍🎓","","I {am} a student.","~이에요"],["😊","","I {am} happy.","~해요 (기분)"],["🏠","","I {am} at home.","~에 있어요"]], 1))],
 "g34-6": [(2, WHO("he · she · it 이 되면 동사에 s!")), (3, R("언제 써요?", "매일 · 늘 하는 일을 말할 때 써요. every day, always, usually 가 자주 같이 나와요.", [["🌅","","He get{s} up at 7 every day.","그는 매일 7시에 일어나요."],["🦷","","Mina always brush{es} her teeth.","미나는 늘 이를 닦아요."]], 1))],
 "g34-7": [(2, WHO("he · she · it 이면 Does, 나머지는 Do."))],
 "g34-8": [(2, WHO("he · she · it 이면 doesn't, 나머지는 don't."))],
 "g56-1": [(1, R("언제 써요? 지금 vs 매일", "지금 이 순간 하는 일은 -ing, 매일 하는 일은 그냥 동사예요. now, Look!, Listen! 이 보이면 -ing.", [["📅","매일","I play soccer every day.","나는 매일 축구를 해요."],["👀","지금","I {am playing} soccer now.","나는 지금 축구를 하고 있어요."],["👂","","Listen! She {is singing}.","들어 봐! 그녀가 노래하고 있어."]])),
            (2, WHO("I 는 am, he · she · it 은 is, we · you · they 는 are."))],
 "g56-2": [(3, R("매일 vs 어제", "매일 하는 일은 지금 모양, 어제 한 일은 ed.", [["📅","매일","I clean my room every day.","나는 매일 방을 청소해요."],["⏪","어제","I clean{ed} my room yesterday.","나는 어제 방을 청소했어요."]], 1))],
 "g56-4": [(2, R("Do vs Did", "보통 하는 일을 물으면 Do · Does, 지난 일을 물으면 Did 예요.", [["📅","보통","{Do} you like soup?","너 수프 좋아하니?"],["⏪","지난번","{Did} you like the soup?","너 그 수프 맛있었니?"]], 1))],
 "g56-5": [(2, R("언제 써요?", "tomorrow · next week · soon · later 처럼 앞으로의 때를 알려 주는 말과 같이 와요.", [["📅","","I will call you {tomorrow}.","내일 전화할게."],["🗓️","","We are going to travel {next week}.","우리는 다음 주에 여행 갈 거예요."]], 1))],
 "g56-6": [(2, R("언제 er, 언제 est?", "둘을 비교하면 er + than, 셋 이상 중에 제일이면 the est (of all · in my class).", [["⚖️","둘","Tom is tall{er} than Mina.","톰은 미나보다 커요."],["🏆","셋 이상","Tom is the tall{est} in my class.","톰은 우리 반에서 가장 커요."]], 1))],
}
MORE = {   # id: 더 넣을 문제 (어려운 문제 hd · G3-4 틀린 단어 찾기)
 "g34-1": [H("I drink ___ water.", ["a","an","-"], "-", "나는 물을 마셔요.", "물은 셀 수 없어서 안 붙여요"),
           H("This is ___ old book.", ["a","an","-"], "an", "이것은 오래된 책이에요.", "old 가 '오' 소리 → an"),
           H("I like ___ apples.", ["a","an","-"], "-", "나는 사과를 좋아해요.", "여러 개(apples)면 안 붙여요"),
           FX("I have a orange.", "a", "an", "나는 오렌지가 하나 있어요.", "orange 는 '오' 소리 → an"),
           FX("She has an cat.", "an", "a", "그녀는 고양이가 한 마리 있어요.", "cat 은 '크' 소리 → a")],
 "g34-2": [H("I have one ___.", ["cat","cats"], "cat", "나는 고양이가 한 마리 있어요.", "하나면 s 없이", "cat"),
           H("Many ___ are in the park.", ["childs","children"], "children", "공원에 아이들이 많아요.", "child → children", "child"),
           H("I need some ___.", ["dishs","dishes"], "dishes", "나는 접시가 좀 필요해요.", "sh 로 끝나면 es", "dish"),
           FX("I have three cat.", "cat", "cats", "나는 고양이가 세 마리 있어요.", "셋이니까 s"),
           FX("Two childs are here.", "childs", "children", "아이 두 명이 여기 있어요.", "child → children")],
 "g34-3": [H("Mina and I ___ classmates.", ["am","is","are"], "are", "미나와 나는 반 친구예요.", "Mina and I = we → are"),
           H("My mom ___ in the kitchen.", ["am","is","are"], "is", "엄마는 부엌에 계세요.", "my mom = she → is"),
           H("My friends ___ at the zoo.", ["am","is","are"], "are", "내 친구들은 동물원에 있어요.", "my friends = they → are"),
           FX("We is friends.", "is", "are", "우리는 친구예요.", "we → are"),
           FX("My dad are a cook.", "are", "is", "우리 아빠는 요리사예요.", "my dad = he → is")],
 "g34-4": [H("___ shoes are new.", ["This","These"], "These", "이 신발은 새것이에요.", "shoes 는 여러 개 → These", "👇 가까이"),
           H("Look at ___ birds over there!", ["these","those"], "those", "저기 저 새들 좀 봐!", "over there(저기) 여러 개 → those"),
           H("Is ___ your dog?", ["that","those"], "that", "저거 네 개니?", "멀리 하나 → that", "👉 멀리"),
           FX("Look at that birds!", "that", "those", "저 새들 좀 봐!", "birds 여러 개 → those"),
           FX("This shoes are new.", "This", "These", "이 신발은 새것이에요.", "shoes 여러 개 → These")],
 "g34-5": [H("Mina and Tom love ___ dog.", ["our","their"], "their", "미나와 톰은 그들의 개를 사랑해요.", "Mina and Tom = they → their"),
           H("Mina and I clean ___ room.", ["our","their"], "our", "미나와 나는 우리 방을 청소해요.", "Mina and I = we → our"),
           H("The cat licks ___ paw.", ["its","his"], "its", "고양이가 자기 발을 핥아요.", "고양이(그것) → its"),
           FX("Mina loves his mom.", "his", "her", "미나는 (자기) 엄마를 사랑해요.", "Mina 는 여자 → her"),
           FX("Tom washes her face.", "her", "his", "톰은 (자기) 얼굴을 씻어요.", "Tom 은 남자 → his")],
 "g34-6": [H("Mina and I ___ soccer.", ["play","plays"], "play", "미나와 나는 축구를 해요.", "Mina and I = we → 그대로"),
           H("My dog ___ in the yard.", ["run","runs"], "runs", "우리 개는 마당에서 뛰어요.", "my dog = it → s"),
           H("Tom and Mina ___ to school.", ["go","goes"], "go", "톰과 미나는 학교에 가요.", "Tom and Mina = they → 그대로"),
           FX("She play the violin.", "play", "plays", "그녀는 바이올린을 켜요.", "she → plays"),
           FX("My mom have a car.", "have", "has", "엄마는 차가 있어요.", "my mom = she → has")],
 "g34-7": [H("___ your brother like games?", ["Do","Does"], "Does", "네 동생은 게임을 좋아하니?", "your brother = he → Does"),
           H("___ Mina and Tom in the same class?", ["Is","Are"], "Are", "미나와 톰은 같은 반이니?", "Mina and Tom = they → Are"),
           H("Does your dog ___ a lot?", ["bark","barks"], "bark", "너희 개는 많이 짖니?", "Does 뒤엔 s 없이"),
           FX("Does she likes milk?", "likes", "like", "그녀는 우유를 좋아하니?", "Does 뒤엔 s 없이"),
           FX("Do he play tennis?", "Do", "Does", "그는 테니스를 치니?", "he → Does")],
 "g34-8": [H("Mina and I ___ like math.", ["don't","doesn't"], "don't", "미나와 나는 수학을 안 좋아해요.", "Mina and I = we → don't"),
           H("My dad ___ drink coffee.", ["don't","doesn't"], "doesn't", "아빠는 커피를 안 드세요.", "my dad = he → doesn't"),
           H("The shoes ___ new.", ["isn't","aren't"], "aren't", "그 신발은 새것이 아니에요.", "shoes 여러 개 → aren't"),
           FX("He don't eat carrots.", "don't", "doesn't", "그는 당근을 안 먹어요.", "he → doesn't"),
           FX("I doesn't like snakes.", "doesn't", "don't", "나는 뱀을 안 좋아해요.", "I → don't")],
 "g56-1": [H("I ___ soccer every Saturday.", ["play","am playing"], "play", "나는 토요일마다 축구를 해요.", "every Saturday(매주) → 그냥 동사"),
           H("Be quiet! The baby ___.", ["sleeps","is sleeping"], "is sleeping", "조용히! 아기가 자고 있어.", "지금 자는 중 → is sleeping"),
           H("Mina and I ___ making a cake.", ["is","are"], "are", "미나와 나는 케이크를 만들고 있어요.", "Mina and I = we → are")],
 "g56-2": [H("I ___ my room every day.", ["clean","cleaned"], "clean", "나는 매일 방을 청소해요.", "every day(매일) → 지금 모양"),
           H("We ___ the museum two days ago.", ["visit","visited"], "visited", "우리는 이틀 전에 박물관에 갔어요.", "ago → ed"),
           H("She ___ her friend yesterday.", ["huged","hugged"], "hugged", "그녀는 어제 친구를 안아 줬어요.", "hug → hugged (g 한 번 더)")],
 "g56-3": [H("I ___ a cold last week.", ["have","had"], "had", "나는 지난주에 감기에 걸렸어요.", "last week → had"),
           H("He ___ a book every night.", ["reads","readed"], "reads", "그는 매일 밤 책을 읽어요.", "every night(매일 밤) → 지금 모양"),
           H("They ___ here an hour ago.", ["come","came"], "came", "그들은 한 시간 전에 여기 왔어요.", "ago → came")],
 "g56-4": [H("Did Mina ___ her homework?", ["finish","finished"], "finish", "미나는 숙제를 끝냈니?", "Did 뒤엔 원래 모양"),
           H("___ you like the soup last night?", ["Do","Did"], "Did", "어젯밤 그 수프 맛있었니?", "last night → Did"),
           H("He ___ come yesterday.", ["doesn't","didn't"], "didn't", "그는 어제 안 왔어요.", "yesterday → didn't")],
 "g56-5": [H("Look at the clouds! It ___ rain.", ["is going to","will to"], "is going to", "구름 좀 봐! 비가 오겠어.", "보이는 걸 보고 곧 일어날 일 → is going to"),
           H("Mina and I ___ going to visit the zoo.", ["is","are"], "are", "미나와 나는 동물원에 갈 거예요.", "Mina and I = we → are"),
           H("I ___ help you later.", ["will","am"], "will", "나중에 도와줄게.", "앞으로 할 일 → will")],
 "g56-6": [H("This is ___ book in the library.", ["the most interesting","the interestingest"], "the most interesting", "이것이 도서관에서 가장 재미있는 책이에요.", "긴 단어 → the most"),
           H("My cat is ___ than my dog.", ["smaller","more small"], "smaller", "우리 고양이는 우리 개보다 작아요.", "짧은 단어 → er"),
           H("She sings ___ than me.", ["better","gooder"], "better", "그녀는 나보다 노래를 잘해요.", "good · well → better")],
 "g56-7": [H("You ___ touch that. It's hot!", ["must not","can"], "must not", "그거 만지면 안 돼. 뜨거워!", "위험해요 → must not"),
           H("She ___ go to the dentist. Her tooth hurts.", ["should","shouldn't"], "should", "그녀는 치과에 가는 게 좋겠어요. 이가 아파요.", "아프니까 → should"),
           H("___ you swim? — Yes, I can.", ["Can","Must"], "Can", "너 수영할 수 있니? — 응, 할 수 있어.", "Yes, I can 으로 대답 → Can")],
 "g56-8": [H("We have lunch ___ noon.", ["at","in"], "at", "우리는 정오에 점심을 먹어요.", "at noon"),
           H("The shop opens ___ Sunday morning.", ["on","in"], "on", "그 가게는 일요일 아침에 열어요.", "요일이 붙으면 on"),
           H("I go to bed ___ 9:30.", ["at","on"], "at", "나는 9시 30분에 자요.", "시각 → at")],
}
for g in g34 + g56:
    for at, c in sorted(CARDS.get(g["id"], []), key=lambda x: -x[0]):
        pass
    # 자리 순서대로 넣기 (앞에서부터, 넣을 때마다 밀림 고려)
    add = sorted(CARDS.get(g["id"], []), key=lambda x: x[0])
    rules = [c for c in g["cards"] if c["k"] == "rule"]; tr = [c for c in g["cards"] if c["k"] == "try"]
    for at, c in add: rules.insert(min(at, len(rules)), c)
    g["cards"] = rules + tr
    g["qs"] += MORE.get(g["id"], [])


# ───── (v386c) 사용자: 설명이 어렵지 않을까 · 문제도 있어야 → 쉬운 말 · 카드당 두 줄 · 카드마다 확인 문제 1개 (설명 → 문제 → 설명 → 문제) ─────
# G3-4: 문법 용어 없음 ("동사" → "하는 말") · G5-6: "하는 말(동사)" 로 처음 알려 주고 씀 · "원래 모양" → "기본 모양(go · eat)"
C = lambda s, o, a, ko, w: P(s, o, a, ko, w)
RW = {
 "g34-1": [("하나면 a", "하나 있는 것 앞에 a 를 붙여요.", C("I have ___ dog.", ["a","an"], "a", "나는 개가 한 마리 있어요.", "dog 하나 → a")),
           ("아 · 에 · 이 · 오 · 어 소리면 an", "a apple 은 말하기 어려워요. 그래서 an apple!", C("It is ___ egg.", ["a","an"], "an", "그것은 달걀이에요.", "egg 는 '에' 소리 → an")),
           ("이럴 땐 안 붙여요", "이름 · 물 · 여러 개 앞에는 a · an 이 없어요.", C("I like ___ apples.", ["a","an","-"], "-", "나는 사과를 좋아해요.", "apples 는 여러 개 → 안 붙여요"))],
 "g34-2": [("여러 개면 끝에 s", "두 개부터는 끝에 s 를 붙여요.", C("I have two ___.", ["cat","cats"], "cats", "나는 고양이가 두 마리 있어요.", "두 마리 → s")),
           ("하나면 그대로", "one · a 뒤에는 s 를 안 붙여요. two · many 뒤에 붙여요.", C("I have one ___.", ["dog","dogs"], "dog", "나는 개가 한 마리 있어요.", "one → 그대로")),
           ("스 · 치 · 시 소리로 끝나면 es", "bus · box · peach · dish 는 s 대신 es!", C("I see two ___.", ["buss","buses"], "buses", "나는 버스 두 대를 봐요.", "bus → buses")),
           ("모양이 바뀌는 단어", "이 단어들은 s 없이 모양이 바뀌어요. 외워 둬요!", C("Two ___ are here.", ["childs","children"], "children", "아이 두 명이 여기 있어요.", "child → children"))],
 "g34-3": [("나는 am, 너는 are", "'나는 ~이에요' 는 I am, '너는' 은 You are.", C("I ___ happy.", ["am","is","are"], "am", "나는 행복해요.", "I 다음엔 am")),
           ("한 명 · 한 개면 is", "그(he) · 그녀(she) · 그것(it) 은 is.", C("She ___ kind.", ["am","is","are"], "is", "그녀는 친절해요.", "she → is")),
           ("여럿이면 are", "우리(we) · 그들(they) · 여러 개는 are.", C("They ___ students.", ["am","is","are"], "are", "그들은 학생이에요.", "they → are")),
           ("이름은 바꿔 생각해요", "Mina and I = 우리(we) → are. 이름도 이렇게 바꿔요.", C("Mina and I ___ friends.", ["is","are"], "are", "미나와 나는 친구예요.", "Mina and I = we → are")),
           ("이럴 때 써요", "'~이에요 · ~해요(기분) · ~에 있어요' 를 말할 때!", C("I ___ at home.", ["am","is","are"], "am", "나는 집에 있어요.", "~에 있어요 → I am"))],
 "g34-4": [("가까이는 this, 멀리는 that", "손에 닿으면 this, 저기 있으면 that.", C("___ is my house. (저기)", ["This","That"], "That", "저것은 우리 집이야.", "저기 → That")),
           ("여러 개면 these · those", "this → these, that → those. 뒤에는 are!", C("___ are apples. (가까이 여러 개)", ["This","These"], "These", "이것들은 사과야.", "가까이 여러 개 → These"))],
 "g34-5": [("누구 거예요?", "내 것 my · 너의 것 your · 그의 것 his · 그녀의 것 her.", C("Mina has a bag. It is ___ bag.", ["his","her"], "her", "미나는 가방이 있어요. 그건 그녀의 가방이에요.", "미나 = 그녀 → her")),
           ("우리 것 · 그들 것 · 그것의 것", "우리 것 our · 그들 것 their · 동물이나 물건은 its.", C("We love ___ school.", ["our","their"], "our", "우리는 우리 학교를 좋아해요.", "we → our"))],
 "g34-6": [("나 · 너 · 우리 · 그들은 그대로", "I · you · we · they 가 하면 하는 말(play · like)을 그대로 써요.", C("We ___ soccer.", ["play","plays"], "play", "우리는 축구를 해요.", "we → 그대로")),
           ("한 명이면 끝에 s", "he · she · it 이 하면 하는 말 끝에 s!", C("He ___ pizza.", ["like","likes"], "likes", "그는 피자를 좋아해요.", "he → likes")),
           ("이름은 바꿔 생각해요", "my mom = 그녀(she) → plays, Mina and I = 우리 → play.", C("My mom ___ tea.", ["drink","drinks"], "drinks", "엄마는 차를 드세요.", "my mom = she → s")),
           ("이럴 때 써요", "매일 · 늘 하는 일을 말할 때! every day, always 와 같이 나와요.", C("She ___ up at 7 every day.", ["get","gets"], "gets", "그녀는 매일 7시에 일어나요.", "she + 매일 → gets")),
           ("es 를 붙이는 말 · has", "go → goes, watch → watches, have → has.", C("Tom ___ a cat.", ["have","has"], "has", "톰은 고양이가 있어요.", "Tom = he → has"))],
 "g34-7": [("묻고 싶으면 앞으로!", "am · are · is 를 맨 앞으로 보내면 묻는 말이 돼요.", C("___ you hungry?", ["Are","Do"], "Are", "너 배고프니?", "hungry 앞에는 are → Are 를 앞으로")),
           ("하는 말이 있으면 Do · Does", "you like 처럼 하는 말이 있으면 Do 로 시작해요. 한 명이면 Does!", C("___ she like cats?", ["Do","Does"], "Does", "그녀는 고양이를 좋아하니?", "she → Does")),
           ("이름은 바꿔 생각해요", "Tom 은 he → Does, Mina and Tom 은 they → Do.", C("___ Tom play soccer?", ["Do","Does"], "Does", "톰은 축구를 하니?", "Tom = he → Does")),
           ("대답하기", "Are 로 물으면 am, Do 로 물으면 do 로 대답해요.", C("Do you like milk? — Yes, I ___.", ["am","do"], "do", "우유 좋아하니? — 응.", "Do 로 물었으니 do"))],
 "g34-8": [("'아니에요' 는 not", "am · are · is 뒤에 not! is not 은 isn't 로 줄여요.", C("He is ___ tall.", ["not","don't"], "not", "그는 키가 크지 않아요.", "is 뒤에 not")),
           ("하는 말이 있으면 don't · doesn't", "I don't like ~ (안 좋아해요). 한 명이면 doesn't!", C("I ___ like carrots.", ["don't","doesn't"], "don't", "나는 당근을 안 좋아해요.", "I → don't")),
           ("이름은 바꿔 생각해요", "my dad 는 he → doesn't, Mina and I 는 we → don't.", C("My dad ___ eat fish.", ["don't","doesn't"], "doesn't", "아빠는 생선을 안 드세요.", "my dad = he → doesn't"))],
 "g56-1": [("지금 하는 중 = am · are · is + ing", "하는 말(동사) 끝에 ing 를 붙이고 앞에 am · are · is!", C("I am ___ now.", ["run","running"], "running", "나는 지금 달리고 있어요.", "am 뒤 → ing")),
           ("지금 vs 매일", "지금 하는 중이면 -ing, 매일 하는 일이면 그냥! now · Look! 이 보이면 -ing.", C("Look! The dog ___ .", ["runs","is running"], "is running", "봐! 개가 달리고 있어.", "Look! = 지금 → is running")),
           ("누가 하는지 보고 am · are · is", "I 는 am, 한 명은 is, 여럿(우리 · 그들)은 are.", C("Mina and Tom ___ dancing.", ["is","are"], "are", "미나와 톰은 춤추고 있어요.", "Mina and Tom = they → are")),
           ("ing 붙이는 요령", "e 로 끝나면 e 빼고(making), run · swim 은 끝 글자 한 번 더(running).", C("We are ___ in the pool.", ["swiming","swimming"], "swimming", "우리는 수영장에서 수영하고 있어요.", "swim → swimming"))],
 "g56-2": [("이미 한 일 = ed", "어제처럼 지나간 일은 하는 말(동사) 끝에 ed!", C("I ___ soccer yesterday.", ["play","played"], "played", "나는 어제 축구를 했어요.", "yesterday → ed")),
           ("ed 붙이는 요령", "끝 모양에 따라 조금 달라요. 아래 예를 봐요!", C("She ___ hard.", ["studyed","studied"], "studied", "그녀는 열심히 공부했어요.", "study → studied")),
           ("지나간 때를 알려 주는 말", "yesterday · last week · ago 가 보이면 ed!", C("We ___ a movie last night.", ["watch","watched"], "watched", "우리는 어젯밤 영화를 봤어요.", "last night → ed")),
           ("매일 vs 어제", "매일 하는 일은 그대로, 어제 한 일은 ed.", C("I ___ my room every day.", ["clean","cleaned"], "clean", "나는 매일 방을 청소해요.", "every day → 그대로"))],
 "g56-3": [("ed 대신 모양이 바뀌는 말", "자주 쓰는 말은 모양이 바뀌어요. go → went, eat → ate!", C("I ___ to the park yesterday.", ["goed","went"], "went", "나는 어제 공원에 갔어요.", "go → went")),
           ("이것도 외워 둬요", "buy → bought, write → wrote, take → took.", C("He ___ a new bike.", ["buyed","bought"], "bought", "그는 새 자전거를 샀어요.", "buy → bought")),
           ("am · is → was, are → were", "'~였어요' 는 was · were 로 말해요.", C("They ___ at home.", ["was","were"], "were", "그들은 집에 있었어요.", "they → were"))],
 "g56-4": [("'~했니?' 는 Did 로 시작", "Did 뒤에는 기본 모양(go · eat · play)을 써요.", C("Did you ___ soccer?", ["play","played"], "play", "너 축구했니?", "Did 뒤 → 기본 모양")),
           ("'안 했어요' 는 didn't", "didn't 뒤에도 기본 모양!", C("I didn't ___ breakfast.", ["eat","ate"], "eat", "나는 아침을 안 먹었어요.", "didn't 뒤 → 기본 모양")),
           ("Do vs Did", "평소 일은 Do, 지난 일은 Did 로 물어요.", C("___ you go to school yesterday?", ["Do","Did"], "Did", "너 어제 학교 갔니?", "yesterday → Did")),
           ("대답하기", "Did 로 물으면 Yes, I did. / No, I didn't.", C("Did you have fun? — Yes, I ___.", ["did","do"], "did", "재미있었니? — 응.", "Did 로 물었으니 did"))],
 "g56-5": [("앞으로 할 일 = will", "will 뒤에는 기본 모양! 누가 하든 will 은 그대로.", C("I will ___ you.", ["help","helps"], "help", "내가 도와줄게.", "will 뒤 → 기본 모양")),
           ("정해 둔 계획 = be going to", "I am going to ~, She is going to ~ 처럼 써요.", C("She ___ going to visit Busan.", ["is","are"], "is", "그녀는 부산에 갈 거예요.", "she → is")),
           ("앞으로를 알려 주는 말", "tomorrow · next week · soon 이 보이면 미래예요.", C("It ___ rain tomorrow.", ["will","is"], "will", "내일 비가 올 거예요.", "tomorrow → will"))],
 "g56-6": [("둘 중에 '더' = er + than", "tall → taller than (~보다 더 큰).", C("Tom is ___ than Mina.", ["taller","tallest"], "taller", "톰은 미나보다 키가 커요.", "than → er")),
           ("여럿 중에 '가장' = the + est", "the tallest (가장 큰).", C("He is the ___ in my class.", ["taller","tallest"], "tallest", "그는 우리 반에서 가장 키가 커요.", "the → est")),
           ("둘이면 er, 여럿이면 est", "than 이 보이면 er, the · of all · in my class 가 보이면 est.", C("It is the ___ dog of all.", ["smaller","smallest"], "smallest", "그것은 모든 개 중에 가장 작아요.", "of all → est")),
           ("긴 말 · 모양이 바뀌는 말", "긴 말은 more · most. good → better → best!", C("This cake is ___ than that one.", ["gooder","better"], "better", "이 케이크가 저것보다 맛있어요.", "good → better"))],
 "g56-7": [("할 수 있어요 = can", "can 뒤에는 기본 모양. 못 하면 can't.", C("Birds can ___.", ["fly","flies"], "fly", "새는 날 수 있어요.", "can 뒤 → 기본 모양")),
           ("꼭 해야 해요 must · 하는 게 좋아요 should", "규칙은 must, 좋은 습관은 should.", C("You ___ wear a seat belt.", ["must","can't"], "must", "안전벨트를 꼭 매야 해요.", "꼭 지킬 규칙 → must")),
           ("묻는 말", "Can · Should 를 맨 앞으로! Can I ~? = ~해도 돼요?", C("___ I use your pen?", ["Can","Am"], "Can", "펜 좀 써도 돼?", "~해도 돼? → Can"))],
 "g56-8": [("몇 시에는 at", "at 7 o'clock, at noon, at night.", C("I get up ___ 7.", ["at","in"], "at", "나는 7시에 일어나요.", "몇 시 → at")),
           ("요일 · 날짜에는 on", "달력의 하루 한 칸은 on. on Monday, on May 5th.", C("See you ___ Friday!", ["on","in"], "on", "금요일에 만나!", "요일 → on")),
           ("달 · 계절 · 해에는 in", "긴 시간은 in. in March, in summer, in the morning.", C("It snows ___ winter.", ["in","on"], "in", "겨울에는 눈이 와요.", "계절 → in"))],
}
for g in g34 + g56:
    rules = [c for c in g["cards"] if c["k"] == "rule"]
    W = RW[g["id"]]
    assert len(W) == len(rules), (g["id"], len(W), len(rules))
    for c, (h, pp, q) in zip(rules, W):
        c["h"] = h; c["p"] = pp; c["q"] = q
    g["cards"] = rules          # 끝의 '같이 해 보기' 카드는 카드마다 확인 문제로 바꿈

data = {"v": 1, "g34": g34, "g56": g56}
# 검사
bad = []
strip = lambda t: re.sub(r"[.,!?]", "", t)
for bk in ("g34", "g56"):
    ids = set()
    for g in data[bk]:
        assert g["id"] not in ids; ids.add(g["id"])
        assert all(c["k"] == "rule" and c.get("q") and c["q"]["a"] in c["q"]["o"] for c in g["cards"]), g["id"]
        for c in g["cards"]: assert len(c["p"]) <= 62, (g["id"], c["p"], len(c["p"]))
        for c in g["cards"]:
            if c["k"] == "rule":
                for e in c["ex"]:
                    assert len(e) == 4, (g["id"], e)
                    assert e[2].count("{") == e[2].count("}"), (g["id"], e)
            else:
                for q in c["q"]: assert q["a"] in q["o"], (g["id"], q)
        ks = {}
        for q in g["qs"]:
            ks[q["k"]] = ks.get(q["k"], 0) + 1
            if q["k"] == "pick":
                assert q["a"] in q["o"] and q["s"].count("___") == 1, (g["id"], q)
            if q["k"] == "ox" and not q["ok"]: assert q.get("fix"), (g["id"], q)
            if q["k"] == "fix":
                toks = [strip(t) for t in q["s"].split()]
                assert toks.count(q["bad"]) == 1, (g["id"], q)
            if q["k"] == "order": assert len(q["w"]) >= 3
        need = {"pick": 6, "ox": 4, "order": 3, "fix": 2}
        if sum(1 for q in g["qs"] if q.get("hd")) < 3: bad.append((g["id"], "hard"))
        for k, n in need.items():
            if ks.get(k, 0) < n: bad.append((g["id"], k, ks.get(k, 0)))
print("문법", len(g34), len(g56), "· 문제", sum(len(g["qs"]) for g in g34 + g56), "· 부족", bad)
out = sys.argv[1] if len(sys.argv) > 1 else "gram.json"
json.dump(data, open(out, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
