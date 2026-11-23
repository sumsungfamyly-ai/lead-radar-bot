import os, re, ssl, json, time, html, datetime
import urllib.request, urllib.parse, urllib.error
import concurrent.futures as cf
from http.server import BaseHTTPRequestHandler

TOKEN = os.environ.get("BOT_TOKEN", "")
SECRET = os.environ.get("WEBHOOK_SECRET", "")
API = f"https://api.telegram.org/bot{TOKEN}/"
UA = {"User-Agent": "leads-finder-bot/3.0 (telegram bot)"}
BROWSER = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                         "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
           "Accept-Language": "en,ru;q=0.8,fi;q=0.6"}
OVERPASS = ["https://overpass-api.de/api/interpreter",
            "https://overpass.kumi.systems/api/interpreter"]

# ---------- ТВОИ ДАННЫЕ (задаются в Vercel -> Environment Variables) ----------
ME = os.environ.get("MY_NAME") or "[ваше имя]"
CONTACT = os.environ.get("MY_CONTACT") or "[ваш Telegram / телефон]"
PORTFOLIO = os.environ.get("MY_PORTFOLIO") or "[ссылка на портфолио]"
PRICE = os.environ.get("MY_PRICE") or ""          # например: от 300 €
DEFAULT_LANG = (os.environ.get("DEFAULT_LANG") or "ru").lower()

PAGE = 5            # карточек за раз
WEAK_MIN = 30       # с какого балла сайт считается слабым
MAX_ANALYZE = 40    # сколько сайтов проверять за один поиск

NICHES = {
    "dentist": ("🦷 Стоматологии", ["amenity=dentist"]),
    "clinic": ("🩺 Клиники и врачи", ["amenity=clinic", "amenity=doctors"]),
    "beauty": ("💇 Салоны красоты", ["shop=hairdresser", "shop=beauty"]),
    "food": ("🍽 Кафе и рестораны", ["amenity=restaurant", "amenity=cafe"]),
    "car": ("🚗 Автосервисы", ["shop=car_repair"]),
    "fitness": ("💪 Фитнес и спорт", ["leisure=fitness_centre"]),
    "shop": ("🛍 Магазины одежды", ["shop=clothes"]),
    "hotel": ("🏨 Отели и гостевые дома", ["tourism=hotel", "tourism=guest_house"]),
    "lawyer": ("⚖️ Юристы", ["office=lawyer"]),
    "estate": ("🏠 Недвижимость", ["office=estate_agent"]),
    "vet": ("🐶 Ветклиники", ["amenity=veterinary"]),
    "school": ("🎓 Школы и курсы", ["amenity=language_school", "amenity=driving_school"]),
}
MODES = {"n": "🚫 Без сайта", "w": "🐌 Слабый сайт", "a": "🔥 Всё вместе"}
STYLES = ["primary", "success", "danger"]  # синий, зелёный, красный
SOCIAL = ("facebook.com", "instagram.com", "vk.com", "t.me", "linktr.ee",
          "ok.ru", "wa.me", "tiktok.com", "fb.com")

PITCH = {
    "nosite": "сайт-визитка + карточка в Google",
    "social": "полноценный сайт вместо соцсети",
    "dead": "новый сайт (старый не работает)",
    "stub": "запуск настоящего сайта (сейчас заглушка)",
    "ssl": "исправление SSL / HTTPS",
    "https": "переход на HTTPS",
    "mobile": "адаптивная вёрстка под телефоны",
    "slow": "ускорение сайта",
    "old": "современный редизайн",
    "seo": "базовое SEO",
}

# =====================================================================
#                     ШАБЛОНЫ ТЕКСТОВ (RU / EN / FI)
#  Переменные: {biz} {me} {domain} {problem} {pricep} {portfolio} {contact}
#  Можно спокойно редактировать тексты под себя.
# =====================================================================
T = {
 "ru": {
  "and": " и ",
  "prob": {
   "mobile": "сайт плохо открывается на телефоне",
   "https": "у сайта нет защищённого HTTPS-соединения",
   "ssl": "у сайта проблема с сертификатом безопасности",
   "stub": "сайт выглядит недоделанным",
   "old": "сайт выглядит устаревшим",
   "slow": "сайт долго загружается",
   "dead": "сайт не открывается",
   "social": "вместо сайта у вас только страница в соцсети",
   "seo": "у сайта нет описания для поисковиков",
   "generic": "сайт можно заметно улучшить",
  },
  "dm_nosite": [
   "Здравствуйте! Меня зовут {me}. Нашёл «{biz}» на карте, но собственного сайта не увидел. Сейчас большинство клиентов сначала ищут услуги в Google с телефона. Я делаю сайты для местного бизнеса{pricep}. Могу бесплатно показать макет сайта для «{biz}», без обязательств. Примеры работ: {portfolio}. Прислать?",
   "Здравствуйте! У «{biz}» нет сайта, а я делаю сайты для местного бизнеса. Могу бесплатно показать макет. Интересно?",
  ],
  "dm_weak": [
   "Здравствуйте! Меня зовут {me}. Смотрел сайт «{biz}» ({domain}) и заметил: {problem}. Из-за этого часть клиентов может уходить к конкурентам. Могу бесплатно подготовить мини-разбор на 1 страницу и показать, что стоит поправить. Примеры работ: {portfolio}. Отправить?",
   "Здравствуйте! Зашёл на {domain} и заметил: {problem}. Могу бесплатно прислать короткий разбор, как это исправить. Интересно?",
  ],
  "call": {
   "open": "Добрый день! Меня зовут {me}. Займу буквально минуту. Это «{biz}»?",
   "hook_nosite": "Я нашёл вас на карте и не увидел вашего сайта. Подскажите, клиенты сейчас находят вас через интернет?",
   "hook_weak": "Я заходил на ваш сайт {domain} и заметил: {problem}. Вы не замечали, что из-за этого теряете обращения?",
   "offer": "Я делаю сайты для местного бизнеса{pricep}. Могу бесплатно подготовить короткий разбор или макет, без обязательств.",
   "close": "Куда удобнее отправить: в WhatsApp или на почту? Или созвонимся завтра на 10 минут?",
   "secretary": "Мне нужно переговорить с тем, кто отвечает за сайт или маркетинг. Когда его можно застать?",
   "mail": "Конечно, отправлю. Продиктуйте, пожалуйста, адрес и как к вам обращаться.",
  },
  "em_subj_nosite": "Макет сайта для «{biz}» — бесплатно",
  "em_subj_weak": "Идеи по улучшению сайта {domain}",
  "em_nosite": "Здравствуйте!\n\nМеня зовут {me}. Я нашёл «{biz}» на карте и заметил, что у вас нет собственного сайта. Большинство клиентов сейчас сначала ищут услуги в Google с телефона, и сайт помогает их не терять.\n\nЯ делаю сайты для местного бизнеса{pricep}. Могу бесплатно подготовить макет для «{biz}», без обязательств.\n\nПримеры работ: {portfolio}\n\nЕсли интересно, просто ответьте на это письмо.\n\nС уважением,\n{me}\n{contact}",
  "em_weak": "Здравствуйте!\n\nМеня зовут {me}. Я посмотрел сайт «{biz}» ({domain}) и заметил: {problem}. Это может снижать число обращений от клиентов.\n\nЯ делаю сайты для местного бизнеса{pricep} и могу бесплатно подготовить короткий разбор (1 страница) с конкретными шагами по улучшению.\n\nПримеры работ: {portfolio}\n\nЕсли интересно, ответьте на это письмо.\n\nС уважением,\n{me}\n{contact}",
  "fu": [
   "Здравствуйте! Напоминаю о моём сообщении про сайт для «{biz}». Если сейчас не до этого, просто скажите, не буду беспокоить. Если интересно, пришлю макет за 1–2 дня.",
   "Это моё последнее сообщение. Подготовил для «{biz}» короткий план по сайту, отправить? Если нет, желаю успехов в бизнесе!",
  ],
  "obj": {
   "price": "Понимаю. Давайте я сначала бесплатно покажу макет, а вы решите, стоит ли он своих денег. Часто один-два новых клиента окупают сайт.",
   "noneed": "Понимаю. Многие так думают, пока не видят, сколько клиентов ищут услуги в Google. Могу бесплатно показать за 2 минуты, как вы выглядите в поиске на фоне конкурентов.",
   "think": "Конечно. Чтобы вам было проще решить, пришлю макет и краткое описание, что войдёт в работу. Когда лучше вернуться к разговору: во вторник или в четверг?",
   "have": "Отлично, что вы уже этим занимаетесь. Если захотите, пришлю бесплатный разбор текущего сайта как второе мнение, без обязательств.",
   "social": "Соцсети хороши, чтобы привлечь внимание, но сайты клиенты ищут в Google. Сайт дополняет соцсети, а не заменяет их. Могу показать на примерах.",
   "fine": "Рад, что он вас устраивает. Давайте я бесплатно покажу, как он выглядит на телефоне и как быстро открывается. Если всё хорошо, так и скажу.",
  },
 },
 "en": {
  "and": " and ",
  "prob": {
   "mobile": "the site doesn't work well on mobile phones",
   "https": "the site has no secure HTTPS connection",
   "ssl": "there is a problem with the site's security certificate",
   "stub": "the site looks unfinished",
   "old": "the site looks outdated",
   "slow": "the site loads slowly",
   "dead": "the site doesn't open",
   "social": "you only have a social media page instead of a website",
   "seo": "the site has no search description",
   "generic": "the site could be noticeably improved",
  },
  "dm_nosite": [
   "Hi! I'm {me}. I found «{biz}» on the map but couldn't find a website. Most customers now search Google on their phone first. I build websites for local businesses{pricep}. I can show you a free mockup for «{biz}», no strings attached. Examples: {portfolio}. Shall I send it?",
   "Hi! «{biz}» doesn't seem to have a website. I build them for local businesses and can show a free mockup. Interested?",
  ],
  "dm_weak": [
   "Hi! I'm {me}. I looked at the website of «{biz}» ({domain}) and noticed that {problem}. This may send some customers to competitors. I can prepare a free one-page review showing what to fix. Examples: {portfolio}. Shall I send it?",
   "Hi! I visited {domain} and noticed that {problem}. I can send a short free review on how to fix it. Interested?",
  ],
  "call": {
   "open": "Hello! My name is {me}. I'll only take a minute. Is this «{biz}»?",
   "hook_nosite": "I found you on the map but couldn't find a website. Do customers find you online these days?",
   "hook_weak": "I visited your website {domain} and noticed that {problem}. Have you noticed you may be losing enquiries because of it?",
   "offer": "I build websites for local businesses{pricep}. I can prepare a short free review or mockup, no strings attached.",
   "close": "Would you prefer I send it on WhatsApp or by email? Or we could have a quick 10-minute call tomorrow.",
   "secretary": "I'd like to speak with whoever handles your website or marketing. When would be a good time to reach them?",
   "mail": "Of course, I'll send it over. Could I get the address and the name to address it to?",
  },
  "em_subj_nosite": "Free website mockup for «{biz}»",
  "em_subj_weak": "Ideas to improve {domain}",
  "em_nosite": "Hello,\n\nMy name is {me}. I found «{biz}» on the map and noticed you don't have your own website. Most customers now search Google on their phone first, and a website helps you keep them.\n\nI build websites for local businesses{pricep}. I can prepare a free mockup for «{biz}», no obligation.\n\nExamples of my work: {portfolio}\n\nIf you're interested, just reply to this email.\n\nBest regards,\n{me}\n{contact}",
  "em_weak": "Hello,\n\nMy name is {me}. I looked at the website of «{biz}» ({domain}) and noticed that {problem}. This may reduce the number of enquiries you get.\n\nI build websites for local businesses{pricep} and can prepare a free short review (1 page) with concrete steps to improve it.\n\nExamples of my work: {portfolio}\n\nIf you're interested, just reply to this email.\n\nBest regards,\n{me}\n{contact}",
  "fu": [
   "Hi! Just following up on my message about a website for «{biz}». If now isn't a good time, just let me know and I won't bother you. If you're interested, I can send a mockup in 1–2 days.",
   "This is my last message. I've prepared a short website plan for «{biz}». Shall I send it? If not, I wish you all the best with the business!",
  ],
  "obj": {
   "price": "I understand. Let me first show you a free mockup, and you can decide if it's worth it. Often one or two new customers pay for the site.",
   "noneed": "Fair enough. Many people feel that way until they see how many customers search on Google. I can show you in two minutes how you appear compared to competitors, for free.",
   "think": "Of course. To make it easier, I'll send the mockup and a short summary of what's included. Would Tuesday or Thursday be better to follow up?",
   "have": "Great that you're already working on it. If you like, I can send a free review of your current site as a second opinion, no obligation.",
   "social": "Social media is great for attention, but people search Google for websites. A site complements your social pages rather than replacing them. I can show you examples.",
   "fine": "Glad you're happy with it. Let me show you for free how it looks on a phone and how fast it loads. If everything is fine, I'll tell you so.",
  },
 },
 "fi": {
  "and": " ja ",
  "prob": {
   "mobile": "sivusto ei toimi hyvin matkapuhelimella",
   "https": "sivustolla ei ole suojattua HTTPS-yhteyttä",
   "ssl": "sivuston suojausvarmenteessa on ongelma",
   "stub": "sivusto vaikuttaa keskeneräiseltä",
   "old": "sivusto näyttää vanhentuneelta",
   "slow": "sivusto latautuu hitaasti",
   "dead": "sivusto ei avaudu",
   "social": "yrityksellä on vain some-sivu eikä omaa verkkosivustoa",
   "seo": "sivustolta puuttuu hakukonekuvaus",
   "generic": "sivustoa voisi parantaa selvästi",
  },
  "dm_nosite": [
   "Hei! Olen {me}. Löysin yrityksenne «{biz}» kartalta, mutta en löytänyt verkkosivuja. Asiakkaat etsivät palveluita yhä useammin ensin Googlesta puhelimella. Teen verkkosivuja paikallisille yrityksille{pricep}. Voin tehdä yritykselle «{biz}» maksuttoman luonnoksen, ei sitoumuksia. Esimerkkejä: {portfolio}. Lähetänkö sen?",
   "Hei! Yrityksellä «{biz}» ei näytä olevan verkkosivuja. Teen niitä paikallisille yrityksille ja voin näyttää maksuttoman luonnoksen. Kiinnostaako?",
  ],
  "dm_weak": [
   "Hei! Olen {me}. Kävin yrityksenne «{biz}» sivuilla ({domain}) ja huomasin, että {problem}. Se voi ohjata asiakkaita kilpailijoille. Teen maksuttoman lyhyen arvion (1 sivu), josta näkyy mitä kannattaisi korjata. Esimerkkejä töistäni: {portfolio}. Lähetänkö sen?",
   "Hei! Kävin sivustolla {domain} ja huomasin, että {problem}. Voin lähettää maksuttoman lyhyen arvion korjauksista. Kiinnostaako?",
  ],
  "call": {
   "open": "Hyvää päivää! Nimeni on {me}. Vien vain minuutin. Onko kyseessä «{biz}»?",
   "hook_nosite": "Löysin teidät kartalta, mutta en löytänyt verkkosivuja. Löytävätkö asiakkaat teidät nykyään netistä?",
   "hook_weak": "Kävin sivustollanne {domain} ja huomasin, että {problem}. Oletteko huomanneet, että se voi vähentää yhteydenottoja?",
   "offer": "Teen verkkosivuja paikallisille yrityksille{pricep}. Voin tehdä maksuttoman lyhyen arvion tai luonnoksen ilman sitoumuksia.",
   "close": "Sopisiko lähettää se WhatsAppilla vai sähköpostilla? Tai soitetaanko huomenna kymmenen minuuttia?",
   "secretary": "Haluaisin puhua sille, joka vastaa verkkosivuista tai markkinoinnista. Milloin hänet tavoittaa?",
   "mail": "Totta kai, lähetän. Voisinko saada osoitteen ja kenelle viesti osoitetaan?",
  },
  "em_subj_nosite": "Maksuton luonnos verkkosivuista: «{biz}»",
  "em_subj_weak": "Ideoita sivuston {domain} parantamiseen",
  "em_nosite": "Hei,\n\nOlen {me}. Löysin yrityksenne «{biz}» kartalta, mutta en löytänyt omia verkkosivuja. Useimmat asiakkaat etsivät nykyään palveluita ensin Googlesta puhelimella, ja sivusto auttaa pitämään heidät.\n\nTeen verkkosivuja paikallisille yrityksille{pricep}. Voin tehdä yritykselle «{biz}» maksuttoman luonnoksen ilman sitoumuksia.\n\nEsimerkkejä töistäni: {portfolio}\n\nJos asia kiinnostaa, vastaa vain tähän viestiin.\n\nYstävällisin terveisin,\n{me}\n{contact}",
  "em_weak": "Hei,\n\nOlen {me}. Kävin yrityksenne «{biz}» sivustolla ({domain}) ja huomasin, että {problem}. Se voi vähentää yhteydenottoja.\n\nTeen verkkosivuja paikallisille yrityksille{pricep} ja voin tehdä maksuttoman lyhyen arvion (1 sivu) konkreettisine parannusehdotuksineen.\n\nEsimerkkejä töistäni: {portfolio}\n\nJos asia kiinnostaa, vastaa vain tähän viestiin.\n\nYstävällisin terveisin,\n{me}\n{contact}",
  "fu": [
   "Hei! Muistutan viestistäni koskien verkkosivuja yritykselle «{biz}». Jos ajankohta ei sovi, kertokaa vain, niin en vaivaa enempää. Jos asia kiinnostaa, lähetän luonnoksen 1–2 päivässä.",
   "Tämä on viimeinen viestini. Olen valmistellut yritykselle «{biz}» lyhyen suunnitelman sivuista. Lähetänkö sen? Jos ei, menestystä yritykselle!",
  ],
  "obj": {
   "price": "Ymmärrän. Näytän ensin maksuttoman luonnoksen, ja te päätätte, onko se sen arvoinen. Usein yksi tai kaksi uutta asiakasta maksaa sivuston takaisin.",
   "noneed": "Ymmärrän. Moni ajattelee niin, kunnes näkee kuinka moni asiakas hakee palveluita Googlesta. Voin näyttää kahdessa minuutissa maksutta, miltä näytätte hauissa kilpailijoihin verrattuna.",
   "think": "Totta kai. Jotta päätös olisi helpompi, lähetän luonnoksen ja lyhyen kuvauksen sisällöstä. Sopisiko tiistai vai torstai jatkoon?",
   "have": "Hienoa, että asiaa jo hoidetaan. Jos haluatte, voin lähettää maksuttoman arvion nykyisistä sivuistanne toisena mielipiteenä, ei sitoumuksia.",
   "social": "Some on hyvä huomion herättämiseen, mutta Googlesta asiakkaat hakevat verkkosivuja. Sivusto täydentää some-sivuja eikä korvaa niitä. Voin näyttää esimerkkejä.",
   "fine": "Hyvä, että olette tyytyväisiä. Näytän maksutta, miltä sivut näyttävät puhelimella ja kuinka nopeasti ne latautuvat. Jos kaikki on kunnossa, kerron sen suoraan.",
  },
 },
}
LANGS = [("ru", "🇷🇺 RU"), ("en", "🇬🇧 EN"), ("fi", "🇫🇮 FI")]
if DEFAULT_LANG not in T:
    DEFAULT_LANG = "ru"

OBJECTIONS = {
    "price": ("💸 «Дорого»", "Не называй цену первым и не снижай её сразу. Вернись к ценности: сколько стоит один новый клиент? Предложи пакет попроще или оплату частями."),
    "noneed": ("🙅 «Нам не нужно»", "Не спорь. Задай вопрос: «Откуда у вас сейчас приходят клиенты?» И покажи конкретику: поиск в Google по их нише и городу."),
    "think": ("🤔 «Подумаем»", "Это мягкое «нет» или нехватка информации. Уточни, что именно нужно обдумать, и назначь конкретную дату следующего контакта."),
    "have": ("👷 «Уже есть кто делает»", "Не критикуй чужую работу. Предложи независимый разбор как второе мнение и оставь свой контакт."),
    "social": ("📱 «Хватает соцсетей»", "Согласись, что соцсети важны, и покажи разницу: поиск в Google, доверие, заявки, карта. Сайт и соцсети работают вместе."),
    "fine": ("👍 «Сайт нормальный»", "Не нападай на сайт. Покажи факты: скриншот на телефоне, скорость загрузки. Если сайт правда хороший, предложи другое: SEO, Google-карточку, рекламу."),
}

PLAN_NOSITE = (
    "📋 <b>План: как взять клиента без сайта</b>\n\n"
    "<b>1. Подготовка (5 минут)</b>\nОткрой карточку на карте, посмотри фото и отзывы, найди имя владельца (Google, Facebook, Instagram). Решай, какую ОДНУ выгоду покажешь.\n\n"
    "<b>2. Первое касание</b>\nНапиши в директ или WhatsApp (кнопка «Директ»). Одно сообщение, один вопрос в конце.\n\n"
    "<b>3. Бесплатный «крючок»</b>\nСделай быстрый макет главной страницы на шаблоне (20–30 минут) и пришли скриншот. Это сильнее любых слов.\n\n"
    "<b>4. Follow-up</b>\nЕсли тишина, напиши через 2–3 дня, потом через 7 (кнопка «Follow-up»). После этого остановись.\n\n"
    "<b>5. Звонок</b>\nЛучшее время: будни 10–12 или 14–16, не в обед. Позвони после сообщения: «Я писал вам, хотел уточнить, видели ли».\n\n"
    "<b>6. Разговор на 10–15 минут</b>\nЗадай три вопроса: откуда сейчас приходят клиенты, сколько их в месяц, что хотели бы улучшить. Слушай больше, чем говори.\n\n"
    "<b>7. Оффер</b>\nДай 3 пакета (мини, стандарт, про). Средний делай основным. Назови срок и что именно входит.\n\n"
    "<b>8. Закрытие</b>\nПредоплата 30–50%, договор на 1 страницу, дата сдачи. Спроси прямо: «Начинаем в понедельник?»\n\n"
    "<b>9. Допродажа</b>\nПоддержка, Google-карточка, SEO, реклама.\n\n"
    "<i>Ориентир, не гарантия: на 30–50 сообщений обычно приходит 5–10 ответов и 1–3 сделки.</i>"
)
PLAN_WEAK = (
    "📋 <b>План: как взять клиента со слабым сайтом</b>\n\n"
    "<b>1. Подготовка (10 минут)</b>\nОткрой сайт с телефона и сделай 2–3 скриншота проблем. Прогони его через Google PageSpeed Insights и запиши скорость. Найди имя владельца.\n\n"
    "<b>2. Первое касание</b>\nНапиши в директ или WhatsApp (кнопка «Директ»). Назови ОДНУ конкретную проблему, не список из десяти.\n\n"
    "<b>3. Мини-аудит как «крючок»</b>\nСделай разбор на 1 страницу: проблема, чем она мешает бизнесу, как исправить. Без критики и обвинений.\n\n"
    "<b>4. Покажи «до и после»</b>\nСделай набросок главной страницы по-новому. Люди покупают то, что видят.\n\n"
    "<b>5. Follow-up</b>\nЧерез 2–3 дня, потом через 7 (кнопка «Follow-up»). После этого остановись.\n\n"
    "<b>6. Звонок</b>\nБудни 10–12 или 14–16. Начни с аудита: «Я прислал разбор вашего сайта, хотел обсудить».\n\n"
    "<b>7. Работа с возражениями</b>\nЧаще всего: «дорого», «нам и так нормально», «уже есть веб-мастер». Ответы в кнопке «Возражения».\n\n"
    "<b>8. Оффер</b>\nДва варианта: «исправить текущий» (дешевле) и «новый сайт» (дороже). Клиенту проще выбирать из двух.\n\n"
    "<b>9. Закрытие</b>\nПредоплата 30–50%, договор на 1 страницу, срок. Спроси прямо: «С чего начнём, с исправлений или с нового сайта?»\n\n"
    "<i>Ориентир, не гарантия: на 30–50 сообщений обычно приходит 5–10 ответов и 1–3 сделки.</i>"
)
GENERAL_TIPS = (
    "🎯 <b>Общие советы по продажам</b>\n\n"
    "• Пиши на языке клиента. В Финляндии финский или английский сработают лучше русского, если владелец не русскоязычный.\n"
    "• Одно сообщение, одна мысль, один вопрос в конце.\n"
    "• Предлагай бесплатный мини-результат (макет или аудит), а не «давайте сотрудничать».\n"
    "• Называй проблему клиента, а не свои услуги.\n"
    "• Не пиши и не звони до 10:00 и после 18:00. Лучшие дни: вторник–четверг.\n"
    "• Следи за регуляциями: холодные письма физлицам и рассылки подпадают под GDPR, пиши вручную и по делу. Не спамь.\n"
    "• Веди таблицу: кому писал, когда, что ответили, дата следующего шага.\n"
    "• После 2 follow-up останавливайся. Вернуться можно через 1–2 месяца.\n\n"
    "Нажми «✍️ Скрипты и подсказки» под любой карточкой, чтобы получить готовые тексты именно для этого клиента."
)


# ---------- Telegram ----------
def tg(method, **params):
    req = urllib.request.Request(API + method, data=json.dumps(params).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=10).read()
    except Exception as e:
        print("tg error", method, e)


def get_json(url, data=None, timeout=25):
    req = urllib.request.Request(url, data=data, headers=UA)
    return json.loads(urllib.request.urlopen(req, timeout=timeout).read())


def esc(s):
    return html.escape(str(s))


# ---------- анализ сайта ----------
def analyze(url):
    """Возвращает (балл 0-100, [(ключ, текст)]). Чем выше балл, тем хуже сайт."""
    host = urllib.parse.urlparse(url).netloc.lower().replace("www.", "")
    if any(host == s or host.endswith("." + s) for s in SOCIAL):
        return 55, [("social", "вместо сайта — соцсеть или мессенджер")]

    def fetch(ctx=None):
        r = urllib.request.urlopen(urllib.request.Request(url, headers=BROWSER),
                                   timeout=6, context=ctx)
        return r.geturl(), r.read(250000).decode("utf-8", "ignore")

    issues, score = [], 0
    t0 = time.time()
    try:
        final, body = fetch()
    except urllib.error.HTTPError as e:
        if e.code in (401, 403, 429, 999):
            return 0, []  # сайт закрыт от ботов, оценить нельзя
        return 65, [("dead", f"сайт отдаёт ошибку {e.code}")]
    except Exception as e:
        reason = getattr(e, "reason", e)
        if isinstance(reason, ssl.SSLError):
            try:
                final, body = fetch(ssl._create_unverified_context())
                issues.append(("ssl", "проблема с SSL-сертификатом"))
                score += 30
            except Exception:
                return 65, [("dead", "сайт не открывается")]
        else:
            return 65, [("dead", "сайт не открывается или не отвечает")]
    elapsed = time.time() - t0
    low = body.lower()

    if re.search(r"under construction|сайт в разработке|coming soon|domain is for sale|"
                 r"welcome to nginx|apache2 ubuntu default|на реконструкции|сайт временно", low):
        score += 40
        issues.append(("stub", "заглушка / сайт не готов"))
    if final.startswith("http://"):
        score += 20
        issues.append(("https", "нет HTTPS"))
    if not re.search(r"<meta[^>]+viewport", low):
        score += 25
        issues.append(("mobile", "не адаптирован под телефон"))
    if elapsed > 4:
        score += 10
        issues.append(("slow", f"медленно грузится ({elapsed:.0f} с)"))
    years = re.findall(r"(?:©|&copy;|copyright)[^<]{0,40}?((?:19|20)\d{2})", low)
    if years and max(map(int, years)) <= datetime.datetime.now().year - 3:
        score += 15
        issues.append(("old", f"устарел, © {max(map(int, years))}"))
    if re.search(r"<marquee|<font[ >]|<center>|<frameset|swfobject|\.swf", low):
        score += 20
        issues.append(("old", "древняя вёрстка (font/center/flash)"))
    if re.search(r"jquery[-.]1\.\d", low):
        score += 10
        issues.append(("old", "старый jQuery 1.x"))
    if not re.search(r"<meta[^>]+name=[\"']description", low):
        score += 5
        issues.append(("seo", "нет SEO-описания"))
    if len(body) < 1500:
        score += 15
        issues.append(("stub", "почти пустая страница"))
    return min(score, 100), issues


# ---------- поиск на карте ----------
def find_leads(niche_key, mode, city):
    geo = get_json("https://nominatim.openstreetmap.org/search?format=json&limit=1&q="
                   + urllib.parse.quote(city))
    if not geo:
        return None
    s, n, w, e = geo[0]["boundingbox"]
    bbox = f"{s},{w},{n},{e}"
    parts = ""
    for tag in NICHES[niche_key][1]:
        k, v = tag.split("=")
        parts += f'nwr["{k}"="{v}"]["name"]({bbox});'
    query = f"[out:json][timeout:20];({parts});out tags center 200;"
    data = None
    for ep in OVERPASS:
        try:
            data = get_json(ep, data=urllib.parse.urlencode({"data": query}).encode())
            break
        except Exception as e:
            print("overpass fail", ep, e)
    if data is None:
        raise RuntimeError("overpass down")

    nosite, with_site = [], []
    for el in data.get("elements", []):
        t = el.get("tags", {})
        lat = el.get("lat") or el.get("center", {}).get("lat")
        lon = el.get("lon") or el.get("center", {}).get("lon")
        if lat is None:
            continue
        site = t.get("website") or t.get("contact:website") or t.get("url") or ""
        site = site.split(";")[0].strip()
        if site and not site.startswith("http"):
            site = "http://" + site
        it = {
            "name": t["name"], "site": site, "lat": lat, "lon": lon,
            "phone": t.get("phone") or t.get("contact:phone") or "",
            "email": t.get("email") or t.get("contact:email") or "",
            "addr": (t.get("addr:street", "") + " " + t.get("addr:housenumber", "")).strip(),
            "score": 0, "issues": [],
        }
        (with_site if site else nosite).append(it)

    nosite.sort(key=lambda x: (not x["phone"], not x["email"]))
    for it in nosite:
        it["kind"] = "nosite"

    weak = []
    if mode in ("w", "a") and with_site:
        cands = with_site[:MAX_ANALYZE]
        with cf.ThreadPoolExecutor(max_workers=16) as ex:
            futs = {ex.submit(analyze, it["site"]): it for it in cands}
            done, _ = cf.wait(futs, timeout=22)
            for f in done:
                try:
                    it = futs[f]
                    it["score"], it["issues"] = f.result()
                    if it["score"] >= WEAK_MIN:
                        it["kind"] = "weak"
                        weak.append(it)
                except Exception:
                    pass
        weak.sort(key=lambda x: -x["score"])

    items = nosite if mode == "n" else weak if mode == "w" else nosite + weak
    return items, len(nosite), len(weak), len(with_site)


# ---------- меню и карточки ----------
def menu_markup():
    rows, row = [], []
    for i, (key, (label, _)) in enumerate(NICHES.items()):
        row.append({"text": label, "callback_data": f"n|{key}", "style": STYLES[i % 3]})
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([{"text": "🎯 Советы по продажам", "callback_data": "tips", "style": "success"}])
    return {"inline_keyboard": rows}


def send_menu(chat_id):
    tg("sendMessage", chat_id=chat_id, reply_markup=menu_markup(), parse_mode="HTML",
       text="Выбери нишу бизнеса 👇\nЯ найду тех, у кого <b>нет сайта</b> или он <b>слабый</b>, "
            "а под каждой карточкой дам готовые тексты и подсказки, как взять клиента.")


def send_modes(chat_id, key):
    btns = [{"text": MODES[m], "callback_data": f"m|{key}|{m}", "style": st}
            for m, st in (("n", "success"), ("w", "danger"), ("a", "primary"))]
    tg("sendMessage", chat_id=chat_id, text=f"Ниша: {NICHES[key][0]}\nЧто ищем?",
       reply_markup={"inline_keyboard": [[btns[0], btns[1]], [btns[2]]]})


def send_card(chat_id, it, city):
    text = f"<b>{esc(it['name'])}</b>"
    if it["kind"] == "nosite":
        text += "  🚫 нет сайта\n"
        pitch_keys = ["nosite"]
    else:
        emoji = "🔴" if it["score"] >= 60 else "🟡"
        dom = urllib.parse.urlparse(it["site"]).netloc.replace("www.", "")
        text += f"  {emoji} сайт {it['score']}/100\n🌐 {esc(dom)}\n"
        text += "⚠️ " + esc("; ".join(t for _, t in it["issues"])) + "\n"
        pitch_keys = list(dict.fromkeys(k for k, _ in it["issues"]))
    if it["addr"]:
        text += f"📍 {esc(it['addr'])}\n"
    text += f"📞 {esc(it['phone'])}\n" if it["phone"] else "📞 телефона нет\n"
    if it["email"]:
        text += f"✉️ {esc(it['email'])}\n"
    text += "💡 <i>Предложи: " + esc(", ".join(PITCH[k] for k in pitch_keys[:3])) + "</i>"

    row1 = [{"text": "📍 На карте", "style": "primary",
             "url": f"https://www.google.com/maps/search/?api=1&query={it['lat']},{it['lon']}"}]
    if it["kind"] == "weak":
        row1.append({"text": "🌐 Открыть сайт", "style": "danger", "url": it["site"]})
    else:
        row1.append({"text": "🔎 Проверить в Google", "style": "danger",
                     "url": "https://www.google.com/search?q=" + urllib.parse.quote(f"{it['name']} {city}")})
    rows = [row1]
    digits = "".join(c for c in it["phone"] if c.isdigit())
    if it["phone"].startswith("+") and len(digits) >= 8:
        rows.append([{"text": "💬 Написать в WhatsApp", "style": "success",
                      "url": f"https://wa.me/{digits}"}])
    rows.append([{"text": "✍️ Скрипты и подсказки", "style": "success", "callback_data": "t|o"}])
    tg("sendMessage", chat_id=chat_id, text=text, parse_mode="HTML",
       disable_web_page_preview=True, reply_markup={"inline_keyboard": rows})


def run_search(chat_id, key, mode, city, offset):
    if offset == 0:
        tg("sendMessage", chat_id=chat_id, text="⏳ Ищу и проверяю сайты, это может занять до 30 секунд...")
    try:
        res = find_leads(key, mode, city)
    except Exception as e:
        print("search error", e)
        tg("sendMessage", chat_id=chat_id, text="⚠️ Карты не ответили, попробуй ещё раз через минуту.")
        return
    if res is None:
        tg("sendMessage", chat_id=chat_id, text="Не нашёл такой город 🤷")
        return send_menu(chat_id)
    items, n_no, n_weak, n_with = res
    if offset == 0:
        tg("sendMessage", chat_id=chat_id, parse_mode="HTML",
           text=(f"📊 <b>{esc(city)}</b>, {NICHES[key][0]}\n"
                 f"🚫 без сайта: <b>{n_no}</b>\n"
                 f"🐌 слабых сайтов: <b>{n_weak}</b> (проверено до {MAX_ANALYZE} из {n_with})"))
    if not items:
        tg("sendMessage", chat_id=chat_id, text="Подходящих не нашёл. Попробуй другую нишу или режим.")
        return send_menu(chat_id)
    for it in items[offset:offset + PAGE]:
        send_card(chat_id, it, city)
    end = min(offset + PAGE, len(items))
    buttons = []
    if end < len(items):
        prefix = f"p|{key}|{mode}|{end}|"
        c = city.encode()[:64 - len(prefix.encode())].decode(errors="ignore")
        buttons.append({"text": "➡️ Ещё", "callback_data": prefix + c, "style": "success"})
    buttons.append({"text": "🔄 Меню", "callback_data": "menu", "style": "primary"})
    tg("sendMessage", chat_id=chat_id, text=f"Показано {offset + 1}–{end} из {len(items)}",
       reply_markup={"inline_keyboard": [buttons]})


# =====================================================================
#            СКРИПТЫ И ПОДСКАЗКИ (контекст берётся из текста сообщения)
# =====================================================================
KEY_PATTERNS = [("адаптирован", "mobile"), ("HTTPS", "https"), ("SSL", "ssl"),
                ("заглушк", "stub"), ("пустая", "stub"), ("устарел", "old"),
                ("древняя", "old"), ("jQuery", "old"), ("медленно", "slow"),
                ("не открывается", "dead"), ("ошибку", "dead"), ("соцсеть", "social"),
                ("SEO", "seo")]


def keys_from(text):
    keys = []
    for pat, k in KEY_PATTERNS:
        if pat in text and k not in keys:
            keys.append(k)
    return keys


def parse_card(text):
    lines = text.split("\n")
    first = lines[0]
    name = re.split(r"\s+(?:🚫|🔴|🟡)", first)[0].strip()
    kind = "weak" if "/100" in first else "nosite"
    domain, issues = "", ""
    for ln in lines[1:]:
        if ln.startswith("🌐 "):
            domain = ln.split(" ", 1)[1].strip()
        elif ln.startswith("⚠️") and " " in ln:
            issues = ln.split(" ", 1)[1].strip()
    return {"name": name, "kind": kind, "domain": domain, "issues": issues,
            "keys": keys_from(issues), "lang": DEFAULT_LANG}


def header(ctx):
    tag = "Нет сайта" if ctx["kind"] == "nosite" else f"Сайт {ctx['domain']} — {ctx['issues']}"
    return f"✍️ <b>{esc(ctx['name'])}</b>\n🏷 {esc(tag)}\n🌐 Язык: {ctx['lang'].upper()}\n\n"


def parse_header(text):
    lines = text.split("\n")
    if len(lines) < 3 or not lines[0].startswith("✍️") or " " not in lines[0] or " " not in lines[1]:
        return None
    name = lines[0].split(" ", 1)[1].strip()
    tag = lines[1].split(" ", 1)[1].strip()
    m = re.search(r"Язык:\s*([A-Za-z]{2})", lines[2])
    lang = m.group(1).lower() if m else DEFAULT_LANG
    if lang not in T:
        lang = DEFAULT_LANG
    if tag.startswith("Нет сайта"):
        return {"name": name, "kind": "nosite", "domain": "", "issues": "", "keys": [], "lang": lang}
    m = re.match(r"Сайт (\S+)(?: — (.*))?", tag)
    domain = m.group(1) if m else ""
    issues = (m.group(2) or "") if m else ""
    return {"name": name, "kind": "weak", "domain": domain, "issues": issues,
            "keys": keys_from(issues), "lang": lang}


def vars_for(ctx):
    L = T[ctx["lang"]]
    probs = [L["prob"][k] for k in ctx["keys"] if k in L["prob"]][:2]
    problem = L["and"].join(probs) if probs else L["prob"]["generic"]
    return dict(biz=ctx["name"], me=ME, domain=ctx["domain"], problem=problem,
                pricep=f" ({PRICE})" if PRICE else "", portfolio=PORTFOLIO, contact=CONTACT)


def pre(s):
    return "<pre>" + esc(s) + "</pre>"


def settings_warning():
    miss = [n for n, v in (("MY_NAME", os.environ.get("MY_NAME")),
                           ("MY_CONTACT", os.environ.get("MY_CONTACT")),
                           ("MY_PORTFOLIO", os.environ.get("MY_PORTFOLIO"))) if not v]
    if not miss:
        return ""
    return ("\n⚠️ <i>Не заданы " + ", ".join(miss) + " в Vercel (Environment Variables): "
            "в текстах будут заглушки в [квадратных скобках].</i>")


def body_dm(ctx):
    L, v = T[ctx["lang"]], vars_for(ctx)
    main, short = L["dm_" + ctx["kind"]]
    return ("📱 <b>Директ / WhatsApp</b>\n\n<b>Основной:</b>\n" + pre(main.format(**v)) +
            "\n<b>Короткий:</b>\n" + pre(short.format(**v)) +
            "\n<i>Нажми на текст, чтобы скопировать. Подставь своё имя и ссылку, если их нет.</i>")


def body_call(ctx):
    c, v = T[ctx["lang"]]["call"], vars_for(ctx)
    hook = c["hook_" + ctx["kind"]]
    steps = [("1️⃣ Приветствие", c["open"]), ("2️⃣ Зацепка", hook), ("3️⃣ Предложение", c["offer"]),
             ("4️⃣ Закрытие", c["close"]), ("🛡 Если ответил секретарь", c["secretary"]),
             ("📧 Если просят «пришлите на почту»", c["mail"])]
    out = "📞 <b>Скрипт звонка</b>\n\n"
    for title, txt in steps:
        out += f"<b>{title}</b>\n" + pre(txt.format(**v)) + "\n"
    out += ("<i>Советы: улыбайся (это слышно), говори медленно, после вопроса молчи и жди ответа. "
            "Не читай как робот, перескажи своими словами.</i>")
    return out


def body_email(ctx):
    L, v = T[ctx["lang"]], vars_for(ctx)
    return ("✉️ <b>Email</b>\n\n<b>Тема:</b>\n" + pre(L["em_subj_" + ctx["kind"]].format(**v)) +
            "\n<b>Текст:</b>\n" + pre(L["em_" + ctx["kind"]].format(**v)))


def body_fu(ctx):
    L, v = T[ctx["lang"]], vars_for(ctx)
    return ("🔁 <b>Follow-up</b>\n\n<b>Через 2–3 дня, если нет ответа:</b>\n" + pre(L["fu"][0].format(**v)) +
            "\n<b>Через 7 дней (последнее):</b>\n" + pre(L["fu"][1].format(**v)) +
            "\n<i>После двух напоминаний остановись. Можно вернуться через 1–2 месяца.</i>")


def panel_markup(ctx):
    lang_row = [{"text": ("✅ " if code == ctx["lang"] else "") + label, "callback_data": f"t|L|{code}"}
                for code, label in LANGS]
    return {"inline_keyboard": [
        [{"text": "📱 Директ / WhatsApp", "callback_data": "t|c|dm", "style": "primary"},
         {"text": "📞 Звонок", "callback_data": "t|c|call", "style": "success"}],
        [{"text": "✉️ Email", "callback_data": "t|c|em", "style": "primary"},
         {"text": "🔁 Follow-up", "callback_data": "t|c|fu", "style": "success"}],
        [{"text": "🛡 Возражения", "callback_data": "t|x", "style": "danger"},
         {"text": "📋 План сделки", "callback_data": "t|p", "style": "primary"}],
        lang_row,
    ]}


def panel_text(ctx):
    return (header(ctx) + "Выбери, что нужно. Язык текстов меняется внизу — "
            "пиши клиенту на том языке, на котором он говорит." + settings_warning())


def back_markup(extra=None):
    row = []
    if extra:
        row.append(extra)
    row.append({"text": "⬅️ Назад", "callback_data": "t|b", "style": "primary"})
    return {"inline_keyboard": [row]}


def edit(cb, text, markup):
    tg("editMessageText", chat_id=cb["message"]["chat"]["id"], message_id=cb["message"]["message_id"],
       text=text, parse_mode="HTML", reply_markup=markup, disable_web_page_preview=True)


def handle_tools(cb):
    parts = cb["data"].split("|")
    chat_id = cb["message"]["chat"]["id"]
    text = cb["message"].get("text", "")
    act = parts[1] if len(parts) > 1 else ""

    if act == "o":  # нажали на карточке
        ctx = parse_card(text)
        tg("sendMessage", chat_id=chat_id, text=panel_text(ctx), parse_mode="HTML",
           reply_markup=panel_markup(ctx), reply_to_message_id=cb["message"]["message_id"])
        return
    ctx = parse_header(text)
    if not ctx:
        tg("sendMessage", chat_id=chat_id,
           text="Не смог прочитать карточку. Нажми «✍️ Скрипты и подсказки» под карточкой клиента ещё раз.")
        return

    if act == "L" and len(parts) > 2 and parts[2] in T:
        ctx["lang"] = parts[2]
        edit(cb, panel_text(ctx), panel_markup(ctx))
    elif act == "b":
        edit(cb, panel_text(ctx), panel_markup(ctx))
    elif act == "c" and len(parts) > 2:
        builders = {"dm": body_dm, "call": body_call, "em": body_email, "fu": body_fu}
        if parts[2] in builders:
            edit(cb, header(ctx) + builders[parts[2]](ctx), back_markup())
    elif act == "x" and len(parts) == 2:
        rows, row = [], []
        for i, (k, (label, _)) in enumerate(OBJECTIONS.items()):
            row.append({"text": label, "callback_data": f"t|x|{k}", "style": STYLES[i % 3]})
            if len(row) == 2:
                rows.append(row)
                row = []
        if row:
            rows.append(row)
        rows.append([{"text": "⬅️ Назад", "callback_data": "t|b", "style": "primary"}])
        edit(cb, header(ctx) + "🛡 <b>Что ответил клиент?</b>", {"inline_keyboard": rows})
    elif act == "x" and len(parts) > 2 and parts[2] in OBJECTIONS:
        label, advice = OBJECTIONS[parts[2]]
        reply = T[ctx["lang"]]["obj"][parts[2]]
        body = (f"🛡 <b>{esc(label)}</b>\n\n💡 <b>Совет:</b> {esc(advice)}\n\n<b>Что ответить:</b>\n" + pre(reply))
        edit(cb, header(ctx) + body,
             back_markup({"text": "🛡 К возражениям", "callback_data": "t|x", "style": "danger"}))
    elif act == "p":
        plan = PLAN_NOSITE if ctx["kind"] == "nosite" else PLAN_WEAK
        edit(cb, header(ctx) + plan, back_markup())


HELP_TEXT = ("👋 <b>Бот для поиска клиентов</b>\n\n"
             "Ищет на карте бизнесы без сайта и со слабым сайтом, оценивает сайты и даёт готовые тексты "
             "для директа, звонка и email на русском, английском и финском. Ещё подсказывает, как отвечать на "
             "возражения и вести клиента до сделки.\n\n"
             "/start — меню\n/tips — советы по продажам\n/me — твои данные для текстов\n\nПоехали 👇")


def handle(update):
    cb = update.get("callback_query")
    if cb:
        tg("answerCallbackQuery", callback_query_id=cb["id"])
        chat_id = cb["message"]["chat"]["id"]
        data = cb.get("data", "")
        parts = data.split("|", 4)
        if data.startswith("t|"):
            handle_tools(cb)
        elif parts[0] == "menu":
            send_menu(chat_id)
        elif parts[0] == "tips":
            tg("sendMessage", chat_id=chat_id, text=GENERAL_TIPS, parse_mode="HTML")
        elif parts[0] == "n" and parts[1] in NICHES:
            send_modes(chat_id, parts[1])
        elif parts[0] == "m" and parts[1] in NICHES and parts[2] in MODES:
            tg("sendMessage", chat_id=chat_id,
               text=f"🔎 Ниша: {NICHES[parts[1]][0]}\n🎯 Режим: {MODES[parts[2]]}\n\n"
                    "Напиши город ответом на это сообщение",
               reply_markup={"force_reply": True, "input_field_placeholder": "Например: Helsinki"})
        elif parts[0] == "p" and len(parts) == 5 and parts[1] in NICHES and parts[2] in MODES:
            run_search(chat_id, parts[1], parts[2], parts[4], int(parts[3]))
        return

    msg = update.get("message")
    if not msg or "text" not in msg:
        return
    chat_id, text = msg["chat"]["id"], msg["text"].strip()

    if text.startswith("/tips"):
        return tg("sendMessage", chat_id=chat_id, text=GENERAL_TIPS, parse_mode="HTML")
    if text.startswith("/me"):
        return tg("sendMessage", chat_id=chat_id, parse_mode="HTML",
                  text=("⚙️ <b>Твои данные в текстах</b>\n"
                        f"Имя: {esc(ME)}\nКонтакт: {esc(CONTACT)}\nПортфолио: {esc(PORTFOLIO)}\n"
                        f"Цена: {esc(PRICE or '— не указана')}\nЯзык по умолчанию: {DEFAULT_LANG.upper()}\n\n"
                        "Меняются в Vercel: Settings → Environment Variables (MY_NAME, MY_CONTACT, "
                        "MY_PORTFOLIO, MY_PRICE, DEFAULT_LANG), потом Redeploy."))
    if text.startswith("/help"):
        return tg("sendMessage", chat_id=chat_id, text=HELP_TEXT, parse_mode="HTML")
    if text.startswith("/start"):
        tg("sendMessage", chat_id=chat_id, text=HELP_TEXT, parse_mode="HTML")
        return send_menu(chat_id)

    reply_text = (msg.get("reply_to_message") or {}).get("text", "")
    if reply_text.startswith("🔎 Ниша:") and not text.startswith("/"):
        key = next((k for k, (lbl, _) in NICHES.items() if lbl in reply_text), None)
        mode = next((m for m, lbl in MODES.items() if lbl in reply_text), None)
        if key and mode:
            return run_search(chat_id, key, mode, text, 0)
    send_menu(chat_id)


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if SECRET and self.headers.get("X-Telegram-Bot-Api-Secret-Token") != SECRET:
            self.send_response(403); self.end_headers(); return
        try:
            body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
            handle(json.loads(body))
        except Exception as e:
            print("error", e)
        self.send_response(200); self.end_headers(); self.wfile.write(b"ok")

    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"bot is running")
