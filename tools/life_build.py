# v626 💬 생활영어 — 수준별 상황 대화 (유치원 8 · G1-2 12 · G3-4 12 · G5-6 12) → data/life.json
# 상황: id · t(한글 제목) · emo · sc(장면) · a(친구 캐릭터) · L(대화 [누가 a=친구/b=나, 영어, 한글, (유치원) 그림])
#       say(상황 보고 말 고르기 [그림, 상황, 정답 영어]) · fb(빈칸 [문장 ___, 정답, 오답, 오답] — 한글 뜻이 같이 나오므로 정답 하나)
import json, os, re
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "life.json")

def S(id, t, emo, sc, a, L, say, fb=None):
    d = {"id": id, "t": t, "emo": emo, "sc": sc, "a": a, "L": L, "say": say}
    if fb: d["fb"] = fb
    return d

K = [
 S("k-1", "안녕!", "👋", "유치원에서 친구를 만났어요", "cat",
   [["a","Hello!","안녕!","👋"],["b","Hi!","안녕!","🙋"],["a","How are you?","잘 지내?","❓"],["b","I'm good!","좋아!","😊"]],
   [["🏫🙋","친구를 만났어요","Hello!"],["🙂❓","친구가 How are you? 하고 물어요","I'm good!"]]),
 S("k-2", "고마워!", "🎁", "친구가 선물을 줬어요", "explorer",
   [["a","This is for you.","이거 너 줄게.","🎁"],["b","Thank you!","고마워!","🙏"],["a","You're welcome.","천만에.","😌"],["b","I love it!","정말 좋아!","😍"]],
   [["🎁","친구가 선물을 줬어요","Thank you!"],["🙏","친구가 Thank you! 해요","You're welcome."]]),
 S("k-3", "미안해", "🙇", "놀다가 친구랑 부딪혔어요", "hero",
   [["a","Ouch!","아야!","🤕"],["b","I'm sorry!","미안해!","🙇"],["a","That's okay.","괜찮아.","👌"],["b","Let's play!","같이 놀자!","🤸"]],
   [["💥🤕","친구랑 부딪혔어요","I'm sorry!"],["🙇","친구가 I'm sorry! 해요","That's okay."]]),
 S("k-4", "잘 자!", "🌙", "잘 시간이에요", "mage",
   [["a","It's bedtime.","잘 시간이야.","🛏️"],["b","Good night, Mom!","잘 자요, 엄마!","🌙"],["a","Sweet dreams!","좋은 꿈 꿔!","💭"],["b","I love you!","사랑해요!","❤️"]],
   [["🌙🛏️","자기 전에 엄마께","Good night!"],["☀️","아침에 일어났어요","Good morning!"]]),
 S("k-5", "배고파", "🍎", "간식 시간이에요", "scholar",
   [["a","Are you hungry?","배고프니?","🍽️"],["b","Yes, I'm hungry.","네, 배고파요.","🤤"],["a","Here's an apple.","사과 여기 있어.","🍎"],["b","Yummy!","맛있어요!","😋"]],
   [["🤤","배가 고파요","I'm hungry."],["😋","간식이 맛있어요","Yummy!"]]),
 S("k-6", "같이 놀자", "⚽", "운동장에서 놀아요", "archer",
   [["a","Let's play!","같이 놀자!","🤸"],["b","Okay!","좋아!","🙆"],["a","Kick the ball!","공 차!","⚽"],["b","Yay!","야호!","🎉"]],
   [["🤸","친구랑 놀고 싶어요","Let's play!"],["🎉","신나요!","Yay!"]]),
 S("k-7", "화장실", "🚽", "수업 중에 화장실에 가고 싶어요", "scholar",
   [["a","What's wrong?","왜 그러니?","😟"],["b","Bathroom, please.","화장실 갈래요.","🚽"],["a","Okay. Go ahead.","그래. 다녀오렴.","👉"],["b","Thank you!","고맙습니다!","🙏"]],
   [["🚽","화장실에 가고 싶어요","Bathroom, please."],["🙏","선생님이 다녀오라고 허락해 주셨어요","Thank you!"]]),
 S("k-8", "또 봐요!", "🏠", "집에 갈 시간이에요", "knight",
   [["a","Time to go home!","집에 갈 시간이야!","🏠"],["b","Bye, teacher!","안녕히 계세요, 선생님!","👩‍🏫"],["a","See you tomorrow!","내일 보자!","📅"],["b","See you!","또 봐요!","🚌"]],
   [["🏠👋","집에 갈 때 선생님께","Bye, teacher!"],["📅","내일 또 만나요","See you tomorrow!"]]),
]

G12 = [
 S("g12-1", "안녕, 잘 지내?", "👋", "아침에 교실에서 친구를 만났어요", "explorer",
   [["a","Good morning, Minsu!","좋은 아침이야, 민수야!"],["b","Good morning, Amy!","좋은 아침, 에이미!"],["a","How are you today?","오늘 기분 어때?"],["b","I'm great, thanks!","아주 좋아, 고마워!"],["a","Let's go to class.","교실에 가자."],["b","Okay!","좋아!"]],
   [["🏫☀️","아침에 선생님을 만났어요","Good morning!"],["🙂❓","친구가 How are you? 하고 물어요","I'm fine, thanks."]],
   ["How ___ you today?","are","is","am"]),
 S("g12-2", "들어가도 돼요?", "🚪", "늦게 와서 교실 문 앞에 섰어요", "scholar",
   [["a","Who's there?","누구니?"],["b","It's me, Jiho. May I come in?","저 지호예요. 들어가도 돼요?"],["a","Sure. Come in.","그래. 들어오렴."],["b","Sorry, I'm late.","늦어서 죄송해요."],["a","That's okay. Sit down, please.","괜찮아. 앉으렴."],["b","Thank you.","감사합니다."]],
   [["🚪⏰","교실 문 앞에서 선생님께","May I come in?"],["⏰🙇","수업에 늦었어요","Sorry, I'm late."]],
   ["May I ___ in?","come","comes","coming"]),
 S("g12-3", "이게 뭐야?", "✏️", "친구가 처음 보는 필통을 갖고 왔어요", "cat",
   [["a","What's this?","이게 뭐야?"],["b","It's my new pencil case.","내 새 필통이야."],["a","Wow, it's cute!","와, 귀엽다!"],["b","Thanks! It's a gift from my mom.","고마워! 엄마가 주신 선물이야."],["a","Can I see it?","봐도 돼?"],["b","Sure. Here you are.","그럼. 여기 있어."]],
   [["✏️❓","친구 물건이 뭔지 궁금해요","What's this?"],["🤲","친구에게 물건을 건네줘요","Here you are."]],
   ["What's ___?","this","these","those"]),
 S("g12-4", "날씨 어때?", "☀️", "쉬는 시간에 창밖을 봐요", "hero",
   [["a","How's the weather today?","오늘 날씨 어때?"],["b","It's sunny and warm.","맑고 따뜻해."],["a","Let's play outside!","밖에서 놀자!"],["b","Good idea!","좋은 생각이야!"],["a","Oh, it's raining now.","어, 이제 비가 와."],["b","Let's play inside, then.","그럼 안에서 놀자."]],
   [["🌧️","밖에 비가 와요","It's raining."],["💡","친구 생각이 좋아요","Good idea!"]],
   ["It's ___ and warm.","sunny","sun","suns"]),
 S("g12-5", "몇 살이야?", "🎂", "새 친구와 이야기해요", "archer",
   [["a","How old are you?","몇 살이야?"],["b","I'm eight years old.","여덟 살이야."],["a","When is your birthday?","생일이 언제야?"],["b","It's in May.","5월이야."],["a","My birthday is in May, too!","내 생일도 5월이야!"],["b","Wow, really?","와, 정말?"]],
   [["🎂❓","친구 나이가 궁금해요","How old are you?"],["🎂🎉","오늘 친구 생일이에요","Happy birthday!"]],
   ["I'm eight ___ old.","years","year","yes"]),
 S("g12-6", "뭐 좋아해?", "🍕", "점심시간에 좋아하는 음식 이야기를 해요", "mage",
   [["a","What food do you like?","무슨 음식 좋아해?"],["b","I like pizza.","나는 피자 좋아해."],["a","Do you like carrots?","당근 좋아해?"],["b","No, I don't.","아니, 안 좋아해."],["a","I love carrots!","나는 당근 정말 좋아해!"],["b","Really? Like a rabbit!","정말? 토끼 같다!"]],
   [["🍕❤️","피자를 좋아해요","I like pizza."],["🥕🙅","당근 좋아하냐고 물었는데 싫어해요","No, I don't."]],
   ["Do you ___ carrots?","like","likes","liking"]),
 S("g12-7", "빌려줄래?", "📏", "지우개를 집에 두고 왔어요", "knight",
   [["a","What's wrong?","왜 그래?"],["b","I don't have an eraser.","나 지우개가 없어."],["a","You can use mine.","내 거 써."],["b","Thank you so much!","정말 고마워!"],["a","No problem.","별거 아니야."],["b","I'll give it back soon.","금방 돌려줄게."]],
   [["✏️🙏","친구 지우개를 빌리고 싶어요","Can I borrow your eraser?"],["🙂","친구가 고맙다고 해요","No problem."]],
   ["You can use ___.","mine","my","me"]),
 S("g12-8", "어디 있어?", "🧢", "모자를 찾고 있어요", "scholar",
   [["a","Where is my cap?","내 모자 어디 있지?"],["b","It's on the bed.","침대 위에 있어."],["a","No, it's not there.","아니, 거기 없어."],["b","Look! It's under the desk.","봐! 책상 아래에 있어."],["a","Oh, thanks!","아, 고마워!"],["b","You're welcome.","천만에."]],
   [["🧢❓","모자를 찾고 있어요","Where is my cap?"],["🛏️","물건이 침대 위에 있어요","It's on the bed."]],
   ["It's ___ the desk.","under","on","in"]),
 S("g12-9", "얼마예요?", "🛒", "문구점에서 공을 사요", "explorer",
   [["a","Can I help you?","도와줄까?"],["b","I want this ball.","이 공 사고 싶어요."],["a","Here you are.","여기 있단다."],["b","How much is it?","얼마예요?"],["a","It's two thousand won.","2천 원이야."],["b","Here you are. Thank you!","여기요. 감사합니다!"]],
   [["💰❓","물건값이 궁금해요","How much is it?"],["⚽","공을 사고 싶어요","I want this ball."]],
   ["How ___ is it?","much","many","long"]),
 S("g12-10", "어디 아파?", "🤕", "보건 선생님을 만났어요", "scholar",
   [["a","Are you okay?","괜찮니?"],["b","I have a headache.","머리가 아파요."],["a","Oh, that's too bad.","저런, 안됐구나."],["b","Can I lie down here?","여기 누워도 돼요?"],["a","Yes, you can.","그래, 누우렴."],["b","Thank you.","감사합니다."]],
   [["🤕","머리가 아파요","I have a headache."],["😟","친구가 아파 보여요","Are you okay?"]],
   ["I have a ___.","headache","head","heads"]),
 S("g12-11", "잘했어!", "🖍️", "미술 시간이에요", "cat",
   [["a","Look at my drawing!","내 그림 봐!"],["b","Wow, good job!","와, 잘 그렸다!"],["a","Thanks! It's my dog.","고마워! 우리 강아지야."],["b","He is so cute.","정말 귀엽다."],["a","Do you want to draw with me?","나랑 같이 그릴래?"],["b","Sure!","그럼!"]],
   [["🖼️👍","친구가 그림을 잘 그렸어요","Good job!"],["🐶","강아지가 귀여워요","He is so cute."]],
   ["Look ___ my drawing!","at","to","on"]),
 S("g12-12", "내일 봐!", "🏠", "학교가 끝났어요", "hero",
   [["a","It's time to go home.","집에 갈 시간이야."],["b","Bye, Amy! See you tomorrow.","안녕, 에이미! 내일 봐."],["a","Have a nice day!","좋은 하루 보내!"],["b","You too!","너도!"],["a","Don't forget your bag!","가방 잊지 마!"],["b","Oops! Thanks.","앗! 고마워."]],
   [["🏠👋","친구와 헤어져요","See you tomorrow."],["😊","친구가 Have a nice day! 해요","You too!"]],
   ["Have a ___ day!","nice","nicely","nine"]),
]

G34 = [
 S("g34-1", "길 묻기", "🗺️", "도서관 가는 길을 몰라요", "explorer",
   [["a","Hi! Do you need help?","안녕! 도와줄까?"],["b","Yes. Where is the library?","네. 도서관이 어디예요?"],["a","Go straight and turn left.","쭉 가서 왼쪽으로 돌아."],["b","Is it far from here?","여기서 멀어요?"],["a","No. It's next to the bank.","아니. 은행 옆에 있어."],["b","Thank you very much!","정말 고마워요!"]],
   [["🗺️❓","도서관 가는 길을 몰라요","Where is the library?"],["⬆️⬅️","쭉 가서 왼쪽으로 가라고 알려 줘요","Go straight and turn left."]],
   ["Go straight and ___ left.","turn","turns","turning"]),
 S("g34-2", "전화하기", "📞", "친구 집에 전화를 걸었어요", "archer",
   [["a","Hello?","여보세요?"],["b","Hello. This is Jiho. Can I speak to Mina?","여보세요. 저 지호인데요. 미나랑 통화할 수 있어요?"],["a","Sorry, she's not home.","미안, 미나는 집에 없어."],["b","Okay. I'll call back later.","알겠어요. 나중에 다시 걸게요."],["a","Okay. Bye!","그래. 잘 있어!"],["b","Goodbye!","안녕히 계세요!"]],
   [["📞","전화를 걸어 내 이름을 말해요","This is Jiho."],["📞⏰","친구가 없어서 나중에 다시 걸 거예요","I'll call back later."]],
   ["Can I ___ to Mina?","speak","speaks","spoke"]),
 S("g34-3", "초대하기", "🎉", "친구를 생일 파티에 초대해요", "mage",
   [["a","Can you come to my birthday party?","내 생일 파티에 올 수 있어?"],["b","Sure! When is it?","그럼! 언제야?"],["a","It's this Saturday at two.","이번 토요일 2시야."],["b","Where is the party?","파티는 어디서 해?"],["a","At my house.","우리 집에서."],["b","Great! See you on Saturday.","좋아! 토요일에 봐."]],
   [["🎉✉️","친구를 생일 파티에 초대해요","Can you come to my party?"],["🙅","초대받았는데 그날 못 가요","Sorry, I can't."]],
   ["See you ___ Saturday.","on","in","at"]),
 S("g34-4", "도서관에서", "📚", "공룡 책을 빌리러 왔어요", "scholar",
   [["a","May I help you?","도와줄까?"],["b","I'm looking for a book about dinosaurs.","공룡에 관한 책을 찾고 있어요."],["a","They're over there.","저쪽에 있단다."],["b","Can I borrow this book?","이 책 빌려도 돼요?"],["a","Yes. You can keep it for a week.","그래. 일주일 동안 빌릴 수 있어."],["b","Thank you!","감사합니다!"]],
   [["🦕📚","공룡 책을 찾고 있어요","I'm looking for a book about dinosaurs."],["📖","이 책을 빌리고 싶어요","Can I borrow this book?"]],
   ["I'm looking ___ a book about dinosaurs.","for","at","to"]),
 S("g34-5", "뭐 할까?", "🚲", "방과 후에 친구랑 놀 계획을 세워요", "hero",
   [["a","What do you want to do?","뭐 하고 싶어?"],["b","Let's ride our bikes.","자전거 타자."],["a","Sounds good! Where?","좋아! 어디서?"],["b","How about the park?","공원 어때?"],["a","Okay. Let's meet at three.","좋아. 3시에 만나자."],["b","See you there!","거기서 봐!"]],
   [["🚲","친구에게 자전거를 타자고 해요","Let's ride our bikes."],["🌳❓","공원에서 노는 게 어떤지 물어봐요","How about the park?"]],
   ["How ___ the park?","about","much","many"]),
 S("g34-6", "무슨 일이야?", "😢", "친구가 슬퍼 보여요", "cat",
   [["a","You look sad. What's wrong?","슬퍼 보여. 무슨 일이야?"],["b","I lost my favorite cap.","제일 좋아하는 모자를 잃어버렸어."],["a","Oh, I'm sorry to hear that.","저런, 안됐다."],["b","I looked everywhere.","다 찾아봤어."],["a","Let's look for it together.","같이 찾아보자."],["b","Thanks. You're a good friend.","고마워. 넌 좋은 친구야."]],
   [["😢","친구가 슬퍼 보여요","What's wrong?"],["😔","친구에게 안 좋은 일이 생겼어요","I'm sorry to hear that."]],
   ["You ___ sad.","look","see","watch"]),
 S("g34-7", "몇 시야?", "⏰", "아침에 학교 갈 준비를 해요", "knight",
   [["a","What time is it?","몇 시야?"],["b","It's seven thirty.","7시 30분이야."],["a","Oh no! I'm late for school.","이런! 학교에 늦겠다."],["b","Hurry up!","서둘러!"],["a","What time does the bus come?","버스는 몇 시에 와?"],["b","At seven forty.","7시 40분에."]],
   [["⏰❓","지금 몇 시인지 궁금해요","What time is it?"],["🏃","친구가 늦을 것 같아요","Hurry up!"]],
   ["It's seven ___.","thirty","thirteen","three"]),
 S("g34-8", "할 수 있어?", "🏊", "수영장에 가기로 했어요", "archer",
   [["a","Can you swim?","수영할 수 있어?"],["b","Yes, I can. I swim every Sunday.","응, 할 수 있어. 일요일마다 수영해."],["a","Wow! I can't swim.","와! 나는 수영 못 해."],["b","I can teach you.","내가 가르쳐 줄게."],["a","Really? Thank you!","정말? 고마워!"],["b","It's easy. Don't worry.","쉬워. 걱정 마."]],
   [["🏊❓","친구가 수영할 수 있는지 궁금해요","Can you swim?"],["😟","친구가 걱정하고 있어요","Don't worry."]],
   ["I ___ teach you.","can","cans","am"]),
 S("g34-9", "옷 사기", "👕", "옷 가게에 왔어요", "explorer",
   [["a","May I help you?","도와드릴까요?"],["b","Yes, please. I'm looking for a T-shirt.","네. 티셔츠를 찾고 있어요."],["a","What color do you want?","무슨 색을 원해요?"],["b","Blue, please.","파란색이요."],["a","How about this one?","이건 어때요?"],["b","I like it. How much is it?","마음에 들어요. 얼마예요?"],["a","It's ten thousand won.","만 원이에요."],["b","I'll take it.","이걸로 살게요."]],
   [["👕💙","파란색을 원해요","Blue, please."],["🛍️","마음에 들어서 사기로 했어요","I'll take it."]],
   ["What ___ do you want?","color","colors","colorful"]),
 S("g34-10", "취미", "🎨", "시간 날 때 하는 일을 이야기해요", "mage",
   [["a","What do you do in your free time?","시간 날 때 뭐 해?"],["b","I usually draw pictures.","보통 그림 그려."],["a","Cool! What do you draw?","멋지다! 뭘 그려?"],["b","I draw animals. How about you?","동물을 그려. 너는?"],["a","I play the piano.","나는 피아노 쳐."],["b","That sounds fun!","재미있겠다!"]],
   [["🎨","시간 날 때 그림을 그려요","I usually draw pictures."],["🎹","친구 취미가 재미있을 것 같아요","That sounds fun!"]],
   ["I ___ the piano.","play","plays","playing"]),
 S("g34-11", "병원에서", "🤒", "목이 아파서 병원에 왔어요", "scholar",
   [["a","What's the matter?","어디가 아프니?"],["b","I have a sore throat.","목이 아파요."],["a","Do you have a fever?","열도 있니?"],["b","Yes, a little.","네, 조금요."],["a","Take this medicine and get some rest.","이 약 먹고 좀 쉬렴."],["b","Thank you, doctor.","감사합니다, 선생님."]],
   [["🤒","목이 아파요","I have a sore throat."],["💊🛌","아픈 친구에게 푹 쉬라고 해요","Get some rest."]],
   ["Do you have a ___?","fever","feet","fun"]),
 S("g34-12", "TV 봐도 돼요?", "📺", "숙제를 다 했어요", "knight",
   [["a","Are you done with your homework?","숙제 다 했니?"],["b","Yes. Can I watch TV now?","네. 이제 TV 봐도 돼요?"],["a","Sure, but only for one hour.","그래, 하지만 한 시간만."],["b","Okay. Can you turn it on, please?","알겠어요. 켜 주실래요?"],["a","Here's the remote.","리모컨 여기 있어."],["b","Thanks, Mom!","고마워요, 엄마!"]],
   [["📺❓","TV를 봐도 되는지 물어봐요","Can I watch TV now?"],["🙏","엄마께 TV를 켜 달라고 부탁해요","Can you turn it on, please?"]],
   ["Can I ___ TV now?","watch","watches","watching"]),
]

G56 = [
 S("g56-1", "식당에서", "🍕", "피자 가게에서 주문해요", "explorer",
   [["a","May I take your order?","주문하시겠어요?"],["b","I'd like a cheese pizza, please.","치즈 피자 주세요."],["a","Anything to drink?","마실 것도 드릴까요?"],["b","Orange juice, please.","오렌지 주스 주세요."],["a","For here or to go?","여기서 드세요, 가져가세요?"],["b","For here, please.","여기서 먹을게요."],["a","Okay. It'll be ready in ten minutes.","네. 10분 뒤에 나와요."],["b","Thank you.","감사합니다."]],
   [["🍕","치즈 피자를 주문해요","I'd like a cheese pizza, please."],["🥡","음식을 집에 가져가고 싶어요","To go, please."]],
   ["I'd ___ a cheese pizza, please.","like","likes","liking"]),
 S("g56-2", "주말 이야기", "🏕️", "월요일 아침, 친구가 주말 이야기를 물어요", "hero",
   [["a","How was your weekend?","주말 어땠어?"],["b","It was great. I went camping with my family.","좋았어. 가족이랑 캠핑 갔어."],["a","Sounds fun! What did you do there?","재미있었겠다! 거기서 뭐 했어?"],["b","We fished in the river and made a campfire.","강에서 낚시하고 모닥불을 피웠어."],["a","Did you catch any fish?","물고기 잡았어?"],["b","Yes, I caught two!","응, 두 마리 잡았어!"],["a","Wow, I'm jealous.","와, 부럽다."],["b","Let's go together next time.","다음엔 같이 가자."]],
   [["🏕️❓","친구 주말이 궁금해요","How was your weekend?"],["🎣","물고기를 두 마리 잡았어요","I caught two fish."]],
   ["I ___ camping with my family.","went","go","goes"]),
 S("g56-3", "버스 타고 가기", "🚌", "박물관에 가는 길을 물어요", "scholar",
   [["a","You look lost. Can I help you?","길을 잃은 것 같네. 도와줄까?"],["b","Yes, please. How can I get to the museum?","네. 박물관에 어떻게 가요?"],["a","Take bus number 7.","7번 버스를 타렴."],["b","Where is the bus stop?","버스 정류장은 어디예요?"],["a","It's across the street.","길 건너편에 있어."],["b","How long does it take?","얼마나 걸려요?"],["a","About fifteen minutes.","15분쯤."],["b","Thank you for your help.","도와주셔서 감사합니다."]],
   [["🏛️❓","박물관 가는 법을 몰라요","How can I get to the museum?"],["⏱️❓","얼마나 걸리는지 궁금해요","How long does it take?"]],
   ["___ bus number 7.","Take","Takes","Taking"]),
 S("g56-4", "약속 정하기", "📅", "주말에 친구와 만날 약속을 해요", "archer",
   [["a","Are you free this Saturday?","이번 토요일에 시간 있어?"],["b","I have a piano lesson in the morning. Why?","오전에 피아노 레슨이 있어. 왜?"],["a","Let's go to the new science museum.","새로 생긴 과학관에 가자."],["b","Sounds great! What time should we meet?","좋아! 몇 시에 만날까?"],["a","How about two o'clock?","2시 어때?"],["b","Okay. Where should we meet?","좋아. 어디서 만날까?"],["a","Let's meet in front of the school.","학교 앞에서 만나자."],["b","See you then!","그때 봐!"]],
   [["📅❓","친구에게 토요일에 시간 있는지 물어요","Are you free this Saturday?"],["⏰❓","만날 시간을 정해요","What time should we meet?"]],
   ["Let's meet in ___ of the school.","front","back","side"]),
 S("g56-5", "늦은 이유", "🙇", "학교에 또 늦었어요", "knight",
   [["a","You're late again, Jiho.","지호, 또 늦었구나."],["b","I'm sorry. I missed the bus.","죄송해요. 버스를 놓쳤어요."],["a","Why did you miss it?","왜 놓쳤니?"],["b","I got up late. I'll get up earlier tomorrow.","늦게 일어났어요. 내일은 더 일찍 일어날게요."],["a","Okay. Don't be late again.","그래. 다시는 늦지 마라."],["b","I won't. I promise.","안 늦을게요. 약속해요."]],
   [["🚌💨","버스를 놓쳐서 늦었어요","I missed the bus."],["🤞","다시는 안 그러겠다고 약속해요","I promise."]],
   ["Why ___ you miss it?","did","do","were"]),
 S("g56-6", "응원하기", "🍀", "친구가 말하기 대회 때문에 떨려 해요", "cat",
   [["a","I'm so nervous about the speech contest.","말하기 대회 때문에 너무 떨려."],["b","You should practice in front of your family.","가족 앞에서 연습해 봐."],["a","That's a good idea.","좋은 생각이다."],["b","And don't forget to smile!","그리고 웃는 거 잊지 마!"],["a","What if I forget my lines?","할 말을 잊어버리면 어떡하지?"],["b","Just take a deep breath. You'll do great.","숨을 크게 쉬어. 넌 잘할 거야."],["a","Thanks. I feel better now.","고마워. 이제 좀 나아졌어."],["b","Good luck!","행운을 빌어!"]],
   [["😰","친구가 대회 때문에 떨려 해요","You'll do great."],["🍀","시험 보러 가는 친구에게","Good luck!"]],
   ["You ___ practice in front of your family.","should","shoulds","must to"]),
 S("g56-7", "장래 희망", "🔬", "커서 되고 싶은 것을 이야기해요", "mage",
   [["a","What do you want to be in the future?","커서 뭐가 되고 싶어?"],["b","I want to be a scientist.","과학자가 되고 싶어."],["a","Why do you want to be a scientist?","왜 과학자가 되고 싶어?"],["b","Because I like doing experiments.","실험하는 걸 좋아하거든."],["a","Cool! I want to be a chef.","멋지다! 나는 요리사가 되고 싶어."],["b","Then you should cook for me someday!","그럼 언젠가 나한테 요리해 줘!"],["a","Sure, I will!","그럼, 그럴게!"]],
   [["🔬","과학자가 되고 싶어요","I want to be a scientist."],["🤔❓","친구의 꿈이 궁금해요","What do you want to be?"]],
   ["I want ___ be a scientist.","to","for","at"]),
 S("g56-8", "신발 바꾸기", "👟", "어제 산 신발이 작아요", "explorer",
   [["a","Hello. How can I help you?","안녕하세요. 무엇을 도와드릴까요?"],["b","I bought these shoes yesterday, but they're too small.","어제 이 신발을 샀는데 너무 작아요."],["a","Do you want a bigger size?","더 큰 사이즈로 드릴까요?"],["b","Yes. Can I exchange them?","네. 바꿀 수 있어요?"],["a","Sure. Do you have the receipt?","그럼요. 영수증 있어요?"],["b","Yes, here it is.","네, 여기 있어요."],["a","Here's a size 230. Try them on.","230 사이즈예요. 신어 보세요."],["b","They fit perfectly. Thank you!","딱 맞아요. 감사합니다!"]],
   [["👟🔄","신발이 작아서 바꾸고 싶어요","Can I exchange them?"],["👟👌","새 신발이 딱 맞아요","They fit perfectly."]],
   ["They're too ___.","small","smaller","smallest"]),
 S("g56-9", "잃어버린 가방", "🎒", "분실물 센터에 왔어요", "scholar",
   [["a","What did you lose?","무엇을 잃어버렸니?"],["b","I lost my backpack.","가방을 잃어버렸어요."],["a","What does it look like?","어떻게 생겼니?"],["b","It's black and has a yellow star on it.","검은색이고 노란 별이 붙어 있어요."],["a","Where did you lose it?","어디서 잃어버렸니?"],["b","I think I left it in the gym.","체육관에 두고 온 것 같아요."],["a","Is this yours?","이거 네 거니?"],["b","Yes, it's mine! Thank you so much.","네, 제 거예요! 정말 감사합니다."]],
   [["🎒❓","가방을 잃어버렸어요","I lost my backpack."],["🙋","찾아 준 물건이 내 거예요","It's mine!"]],
   ["What does it look ___?","like","as","for"]),
 S("g56-10", "뭐가 더 좋아?", "🐶", "고양이와 개 중에 뭐가 더 좋은지 이야기해요", "hero",
   [["a","Which do you like better, cats or dogs?","고양이랑 개 중에 뭐가 더 좋아?"],["b","I like dogs better.","개가 더 좋아."],["a","Why?","왜?"],["b","Dogs are friendlier than cats.","개가 고양이보다 더 다정하거든."],["a","But cats are cleaner!","하지만 고양이가 더 깨끗해!"],["b","That's true. They're both cute.","맞아. 둘 다 귀여워."]],
   [["🐶❤️","개가 더 좋아요","I like dogs better."],["🤝","친구 말이 맞아요","That's true."]],
   ["Dogs are ___ than cats.","friendlier","friendly","friendliest"]),
 S("g56-11", "메시지 남기기", "📱", "친구 집에 전화했는데 친구가 없어요", "archer",
   [["a","Hello?","여보세요?"],["b","Hello. May I speak to Tom, please?","여보세요. 톰과 통화할 수 있을까요?"],["a","Sorry, he's out right now. Who's calling?","미안, 지금 밖에 나갔어. 누구니?"],["b","This is Jiho, his classmate.","같은 반 친구 지호예요."],["a","Can I take a message?","메시지 전해 줄까?"],["b","Yes. Please tell him to call me back.","네. 저한테 다시 전화해 달라고 전해 주세요."],["a","Okay, I'll tell him.","그래, 전해 줄게."],["b","Thank you. Goodbye.","감사합니다. 안녕히 계세요."]],
   [["📱✉️","톰에게 다시 전화해 달라고 전해요","Please tell him to call me back."],["📞❓","전화한 사람이 누구인지 물어요","Who's calling?"]],
   ["Can I take a ___?","message","massage","messages"]),
 S("g56-12", "새 친구", "🤝", "다른 나라에서 온 친구가 전학 왔어요", "knight",
   [["a","Hi, I'm new here. My name is Leo.","안녕, 나 여기 새로 왔어. 내 이름은 레오야."],["b","Nice to meet you, Leo. I'm Jiho.","만나서 반가워, 레오. 나는 지호야."],["a","Nice to meet you, too.","나도 반가워."],["b","Where are you from?","어디서 왔어?"],["a","I'm from Canada.","캐나다에서 왔어."],["b","Cool! Do you want to have lunch with us?","멋지다! 우리랑 점심 같이 먹을래?"],["a","I'd love to. Thanks!","좋아. 고마워!"],["b","Let me show you around the school.","학교 구경시켜 줄게."]],
   [["🤝","새 친구를 처음 만났어요","Nice to meet you."],["🌍❓","친구가 어느 나라에서 왔는지 궁금해요","Where are you from?"]],
   ["Where are you ___?","from","to","at"]),
]

D = {"lv": {"k": {"nm": "유치원", "emo": "🧸", "sub": "인사 · 기분 · 듣고 그림"},
            "g12": {"nm": "G1-2", "emo": "🍎", "sub": "안부 · 허락 · 날씨"},
            "g34": {"nm": "G3-4", "emo": "🎒", "sub": "길 · 전화 · 초대 · 아플 때"},
            "g56": {"nm": "G5-6", "emo": "🧭", "sub": "주문 · 약속 · 조언 · 교환"}},
     "k": K, "g12": G12, "g34": G34, "g56": G56}

# ── 검사 ──
CH = {"hero", "explorer", "archer", "mage", "knight", "scholar", "ghost", "cat", "wolf"}
ids = set()
for lv in ("k", "g12", "g34", "g56"):
    for s in D[lv]:
        assert s["id"] not in ids, s["id"]; ids.add(s["id"])
        assert s["a"] in CH, s
        assert len(s["L"]) >= 4 and s["L"][0][0] == "a", s["id"]
        for i, l in enumerate(s["L"]):
            assert l[0] in "ab" and l[1] and l[2], (s["id"], l)
            assert re.match(r"^[A-Z]", l[1]) and re.search(r"[.!?]$", l[1]), (s["id"], l[1])
            if lv == "k": assert len(l) == 4 and l[3], (s["id"], l)
        assert sum(1 for i in range(1, len(s["L"])) if s["L"][i][0] == "b" and s["L"][i-1][0] == "a") >= 2, s["id"]
        assert len(s["say"]) == 2, s["id"]
        if lv != "k":
            f = s["fb"]; assert f[0].count("___") == 1 and len(set(f[1:])) == 3, (s["id"], f)
            full = f[0].replace("___", f[1]); assert any(full.lower().rstrip(".!?") in l[1].lower() for l in s["L"]), (s["id"], full)
    if lv == "k":   # 그림 고르기: 같은 단계 안에서 그림이 겹치는 다른 말이 없어야 보기가 헷갈리지 않음
        seen = {}
        for s in D[lv]:
            for l in s["L"]:
                if l[3] in seen and seen[l[3]] != l[1]: raise SystemExit(f"그림 겹침 {l[3]} {seen[l[3]]} / {l[1]}")
                seen[l[3]] = l[1]
json.dump(D, open(OUT, "w"), ensure_ascii=False, separators=(",", ":"))
print("ok", {lv: len(D[lv]) for lv in ("k", "g12", "g34", "g56")}, sum(len(s["L"]) for lv in ("k","g12","g34","g56") for s in D[lv]), "lines")
