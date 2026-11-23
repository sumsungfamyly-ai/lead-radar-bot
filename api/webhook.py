import os, re, ssl, json, time, html, hashlib, datetime, io, csv, base64, math, threading
import urllib.request, urllib.parse, urllib.error
import xml.etree.ElementTree as ET
import concurrent.futures as cf

from lib import ledger

TOKEN = os.environ.get("BOT_TOKEN", "")
SECRET = os.environ.get("WEBHOOK_SECRET", "")
API = f"https://api.telegram.org/bot{TOKEN}/"
UA = {"User-Agent": "leads-finder-bot/3.0 (telegram bot)"}
BROWSER = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                         "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
           "Accept-Language": "en,ru;q=0.8,fi;q=0.6"}
# Запасные серверы карт: если один лёг или перегружен, идём к следующему
OVERPASS = ["https://overpass-api.de/api/interpreter",
            "https://overpass.kumi.systems/api/interpreter",
            "https://overpass.private.coffee/api/interpreter",
            "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
            "https://overpass.osm.jp/api/interpreter",
            "https://z.overpass-api.de/api/interpreter"]

# ---------- ТВОИ ДАННЫЕ (задаются в Vercel -> Environment Variables) ----------
ME = os.environ.get("MY_NAME") or "[ваше имя]"
CONTACT = os.environ.get("MY_CONTACT") or "[ваш Telegram / телефон]"
PORTFOLIO = os.environ.get("MY_PORTFOLIO") or "[ссылка на портфолио]"
PRICE = os.environ.get("MY_PRICE") or ""          # например: от 300 €
DEFAULT_LANG = (os.environ.get("DEFAULT_LANG") or "ru").lower()
MY_CHAT_ID = os.environ.get("MY_CHAT_ID") or ""   # куда слать напоминания (cron)
PSI_KEY = os.environ.get("PAGESPEED_API_KEY") or ""  # необязательно, повышает лимиты

# ---------- Мини-приложение (тот же бот, но наглядно) ----------
APP_URL = (os.environ.get("APP_URL") or "").rstrip("/")
if not APP_URL and os.environ.get("VERCEL_URL"):
    APP_URL = "https://" + os.environ["VERCEL_URL"].rstrip("/")
MINIAPP_URL = APP_URL + "/api/miniapp" if APP_URL else ""

# ---------- CRM (необязательно): бесплатный Upstash Redis ----------
# Если не задано — бот работает как раньше, просто без базы клиентов.
UPSTASH_URL = (os.environ.get("UPSTASH_REDIS_REST_URL") or "").rstrip("/")
UPSTASH_TOKEN = os.environ.get("UPSTASH_REDIS_REST_TOKEN") or ""
CRM_ON = bool(UPSTASH_URL and UPSTASH_TOKEN)

PAGE = 5            # карточек за раз
WEAK_MIN = 30       # с какого балла сайт считается слабым
MAX_ANALYZE = 60    # сколько сайтов проверять за один поиск

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
    "bakery": ("🥐 Пекарни и кондитерские", ["shop=bakery", "shop=confectionery"]),
    "florist": ("💐 Цветочные магазины", ["shop=florist"]),
    "carwash": ("🧽 Автомойки", ["amenity=car_wash"]),
    "massage": ("💆 Массаж и SPA", ["shop=massage", "leisure=spa"]),
    "repair": ("🔧 Ремонт техники", ["shop=electronics_repair", "craft=electronics_repair"]),
    "accountant": ("🧾 Бухгалтеры", ["office=accountant"]),
    "photo": ("📸 Фотостудии", ["shop=photo", "craft=photographer"]),
    "barber": ("💈 Барбершопы", ["shop=hairdresser"]),
}
MODES = {"n": "🚫 Без сайта", "w": "🐌 Слабый сайт", "a": "🔥 Всё вместе"}
# Слова для запасного POI-поиска (Photon) по каждой нише (включая местные языки)
NICHE_QUERY = {
    "dentist": ["dentist", "hammaslääkäri"], "clinic": ["clinic", "lääkäriasema"],
    "beauty": ["hairdresser", "kampaamo", "beauty salon"],
    "food": ["cafe", "restaurant", "ravintola", "kahvila"],
    "car": ["car repair", "autokorjaamo"], "fitness": ["gym", "kuntosali"],
    "shop": ["clothes shop", "vaateliike"], "hotel": ["hotel", "hotelli"],
    "lawyer": ["lawyer", "asianajotoimisto"], "estate": ["estate agent", "kiinteistönvälitys"],
    "vet": ["veterinary", "eläinlääkäri"], "school": ["language school", "kielikoulu"],
    "bakery": ["bakery", "leipomo"], "florist": ["florist", "kukkakauppa"],
    "carwash": ["car wash", "autopesula"], "massage": ["massage", "hieronta"],
    "repair": ["electronics repair", "huolto"], "accountant": ["accountant", "tilitoimisto"],
    "photo": ["photo studio", "valokuvaamo"],
    "barber": ["barbershop", "parturi", "barber"],
}
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
 "et": {
  "and": " ja ",
  "prob": {
   "mobile": "sait ei tööta hästi mobiiltelefonis",
   "https": "saidil puudub turvaline HTTPS-ühendus",
   "ssl": "saidi turvasertifikaadiga on probleem",
   "stub": "sait tundub lõpetamata",
   "old": "sait näeb välja aegunud",
   "slow": "sait laadib aeglaselt",
   "dead": "sait ei avane",
   "social": "kodulehe asemel on ainult sotsiaalmeedia leht",
   "seo": "saidil puudub otsingumootorite kirjeldus",
   "generic": "saiti saaks märgatavalt parandada",
  },
  "dm_nosite": [
   "Tere! Olen {me}. Leidsin «{biz}» kaardilt, aga oma kodulehte ei leidnud. Enamik kliente otsib teenuseid kõigepealt Google'ist telefoniga. Teen kodulehti kohalikele ettevõtetele{pricep}. Saan tasuta näidata «{biz}» kodulehe kavandit, ilma kohustusteta. Näited: {portfolio}. Kas saadan?",
   "Tere! «{biz}» ei paista olevat kodulehte. Teen neid kohalikele ettevõtetele ja saan näidata tasuta kavandit. Kas huvitab?",
  ],
  "dm_weak": [
   "Tere! Olen {me}. Vaatasin «{biz}» kodulehte ({domain}) ja märkasin: {problem}. See võib saata osa kliente konkurentide juurde. Saan tasuta teha üheleheküljelise ülevaate, mida parandada. Näited: {portfolio}. Kas saadan?",
   "Tere! Külastasin {domain} ja märkasin: {problem}. Saan saata lühikese tasuta ülevaate parandustest. Kas huvitab?",
  ],
  "call": {
   "open": "Tere päevast! Minu nimi on {me}. Võtan ainult minuti. Kas see on «{biz}»?",
   "hook_nosite": "Leidsin teid kaardilt, aga kodulehte ei leidnud. Kas kliendid leiavad teid praegu internetist?",
   "hook_weak": "Külastasin teie kodulehte {domain} ja märkasin: {problem}. Kas olete märganud, et see võib vähendada päringuid?",
   "offer": "Teen kodulehti kohalikele ettevõtetele{pricep}. Saan tasuta teha lühikese ülevaate või kavandi, ilma kohustusteta.",
   "close": "Kas saata WhatsAppi või e-postiga? Või helistame homme 10 minutiks?",
   "secretary": "Soovin rääkida sellega, kes vastutab kodulehe või turunduse eest. Millal teda tabab?",
   "mail": "Muidugi saadan. Öelge palun aadress ja kellele kirjutan.",
  },
  "em_subj_nosite": "Tasuta kodulehe kavand: «{biz}»",
  "em_subj_weak": "Ideid saidi {domain} parandamiseks",
  "em_nosite": "Tere!\n\nOlen {me}. Leidsin «{biz}» kaardilt ja märkasin, et teil pole oma kodulehte. Enamik kliente otsib teenuseid kõigepealt Google'ist telefoniga — koduleht aitab neid mitte kaotada.\n\nTeen kodulehti kohalikele ettevõtetele{pricep}. Saan tasuta teha «{biz}» kavandi, ilma kohustusteta.\n\nNäited töödest: {portfolio}\n\nKui huvitab, vastake lihtsalt sellele kirjale.\n\nLugupidamisega,\n{me}\n{contact}",
  "em_weak": "Tere!\n\nOlen {me}. Vaatasin «{biz}» kodulehte ({domain}) ja märkasin: {problem}. See võib vähendada päringute arvu.\n\nTeen kodulehti kohalikele ettevõtetele{pricep} ja saan tasuta teha lühikese ülevaate (1 lehekülg) konkreetsete parandustega.\n\nNäited töödest: {portfolio}\n\nKui huvitab, vastake lihtsalt sellele kirjale.\n\nLugupidamisega,\n{me}\n{contact}",
  "fu": [
   "Tere! Tuletan meelde oma kirja «{biz}» kodulehe kohta. Kui praegu pole aega, öelge lihtsalt ja ma ei tülita. Kui huvitab, saadan kavandi 1–2 päevaga.",
   "See on minu viimane kiri. Valmistasin «{biz}» jaoks lühikese kodulehe plaani. Kas saadan? Kui ei, soovin edu ettevõtluses!",
  ],
  "obj": {
   "price": "Mõistan. Näitan kõigepealt tasuta kavandit ja te otsustate, kas see on oma hinda väärt. Sageli tasub üks-kaks uut klienti kodulehe kinni.",
   "noneed": "Mõistan. Paljud arvavad nii, kuni näevad, kui palju kliente otsib teenuseid Google'ist. Saan kahe minutiga tasuta näidata, kuidas paistate konkurentide kõrval.",
   "think": "Muidugi. Et otsustamine oleks lihtsam, saadan kavandi ja lühikese kirjelduse. Kas teisipäev või neljapäev sobib jätkuks?",
   "have": "Tore, et sellega juba tegeletakse. Soovi korral saadan tasuta ülevaate praegusest saidist teise arvamusena, ilma kohustusteta.",
   "social": "Sotsiaalmeedia on tähelepanu jaoks hea, aga kliendid otsivad Google'ist kodulehti. Sait täiendab sotsiaalmeediat, ei asenda seda. Saan näidata näiteid.",
   "fine": "Hea, et olete rahul. Näitan tasuta, kuidas sait telefonis välja näeb ja kui kiiresti avaneb. Kui kõik on korras, ütlen seda otse.",
  },
 },
 "sv": {
  "and": " och ",
  "prob": {
   "mobile": "sajten fungerar dåligt i mobilen",
   "https": "sajten saknar säker HTTPS-anslutning",
   "ssl": "det finns problem med sajtens säkerhetscertifikat",
   "stub": "sajten ser ofärdig ut",
   "old": "sajten ser föråldrad ut",
   "slow": "sajten laddar långsamt",
   "dead": "sajten öppnar inte",
   "social": "ni har bara en sociala medier-sida i stället för en webbplats",
   "seo": "sajten saknar beskrivning för sökmotorer",
   "generic": "sajten kan förbättras tydligt",
  },
  "dm_nosite": [
   "Hej! Jag heter {me}. Jag hittade «{biz}» på kartan men ingen egen webbplats. De flesta kunder söker tjänster i Google med mobilen först. Jag bygger webbplatser för lokala företag{pricep}. Jag kan visa en gratis skiss för «{biz}», utan förpliktelser. Exempel: {portfolio}. Ska jag skicka?",
   "Hej! «{biz}» verkar sakna webbplats. Jag bygger sådana för lokala företag och kan visa en gratis skiss. Intresserad?",
  ],
  "dm_weak": [
   "Hej! Jag heter {me}. Jag tittade på webbplatsen för «{biz}» ({domain}) och märkte: {problem}. Det kan göra att kunder går till konkurrenter. Jag kan gratis ta fram en genomgång på en sida. Exempel: {portfolio}. Ska jag skicka?",
   "Hej! Jag besökte {domain} och märkte: {problem}. Jag kan skicka en kort gratis genomgång. Intresserad?",
  ],
  "call": {
   "open": "God dag! Jag heter {me}. Jag tar bara en minut. Är det «{biz}»?",
   "hook_nosite": "Jag hittade er på kartan men ingen webbplats. Hittar kunderna er online i dag?",
   "hook_weak": "Jag besökte er webbplats {domain} och märkte: {problem}. Har ni märkt att det kan kosta er förfrågningar?",
   "offer": "Jag bygger webbplatser för lokala företag{pricep}. Jag kan gratis ta fram en kort genomgång eller skiss, utan förpliktelser.",
   "close": "Vill ni ha det via WhatsApp eller e-post? Eller ringer vi 10 minuter i morgon?",
   "secretary": "Jag vill tala med den som ansvarar för webbplatsen eller marknadsföringen. När når jag dem?",
   "mail": "Självklart skickar jag. Kan jag få adressen och vem jag ska ställa det till?",
  },
  "em_subj_nosite": "Gratis webbplatsskiss för «{biz}»",
  "em_subj_weak": "Idéer för att förbättra {domain}",
  "em_nosite": "Hej!\n\nJag heter {me}. Jag hittade «{biz}» på kartan och såg att ni saknar egen webbplats. De flesta kunder söker tjänster i Google med mobilen först, och en webbplats hjälper er att behålla dem.\n\nJag bygger webbplatser för lokala företag{pricep}. Jag kan gratis ta fram en skiss för «{biz}», utan förpliktelser.\n\nExempel på arbeten: {portfolio}\n\nOm det är intressant, svara bara på detta mejl.\n\nVänliga hälsningar,\n{me}\n{contact}",
  "em_weak": "Hej!\n\nJag heter {me}. Jag tittade på webbplatsen för «{biz}» ({domain}) och märkte: {problem}. Det kan minska antalet förfrågningar.\n\nJag bygger webbplatser för lokala företag{pricep} och kan gratis ta fram en kort genomgång (1 sida) med konkreta förbättringar.\n\nExempel på arbeten: {portfolio}\n\nOm det är intressant, svara bara på detta mejl.\n\nVänliga hälsningar,\n{me}\n{contact}",
  "fu": [
   "Hej! Jag påminner om mitt meddelande om en webbplats för «{biz}». Om det inte passar just nu, säg bara till så stör jag inte. Om det är intressant skickar jag en skiss inom 1–2 dagar.",
   "Detta är mitt sista meddelande. Jag har tagit fram en kort webbplatsplan för «{biz}». Ska jag skicka den? Annars önskar jag er lycka till med företaget!",
  ],
  "obj": {
   "price": "Jag förstår. Låt mig först visa en gratis skiss, så kan ni avgöra om den är värd priset. Ofta betalar en eller två nya kunder tillbaka webbplatsen.",
   "noneed": "Jag förstår. Många tycker så tills de ser hur många kunder som söker i Google. Jag kan gratis visa på två minuter hur ni syns jämfört med konkurrenterna.",
   "think": "Självklart. För att göra det enkelt skickar jag skissen och en kort beskrivning. Passar tisdag eller torsdag för uppföljning?",
   "have": "Vad bra att ni redan jobbar med det. Om ni vill skickar jag en gratis genomgång av nuvarande sajt som en andra åsikt, utan förpliktelser.",
   "social": "Sociala medier är bra för uppmärksamhet, men kunder söker webbplatser i Google. Sajten kompletterar sociala medier i stället för att ersätta dem. Jag kan visa exempel.",
   "fine": "Kul att ni är nöjda. Jag visar gratis hur sajten ser ut i mobilen och hur snabbt den laddar. Är allt bra säger jag det.",
  },
 },
 "de": {
  "and": " und ",
  "prob": {
   "mobile": "die Seite funktioniert auf dem Handy nicht gut",
   "https": "die Seite hat keine sichere HTTPS-Verbindung",
   "ssl": "es gibt ein Problem mit dem Sicherheitszertifikat der Seite",
   "stub": "die Seite wirkt unfertig",
   "old": "die Seite wirkt veraltet",
   "slow": "die Seite lädt langsam",
   "dead": "die Seite öffnet nicht",
   "social": "statt einer Website gibt es nur eine Social-Media-Seite",
   "seo": "der Seite fehlt die Beschreibung für Suchmaschinen",
   "generic": "die Seite lässt sich deutlich verbessern",
  },
  "dm_nosite": [
   "Hallo! Ich bin {me}. Ich habe «{biz}» auf der Karte gefunden, aber keine eigene Website. Die meisten Kunden suchen Leistungen heute zuerst bei Google am Handy. Ich baue Websites für lokale Unternehmen{pricep}. Ich kann Ihnen kostenlos einen Entwurf für «{biz}» zeigen, unverbindlich. Beispiele: {portfolio}. Soll ich ihn schicken?",
   "Hallo! «{biz}» scheint keine Website zu haben. Ich baue welche für lokale Unternehmen und kann kostenlos einen Entwurf zeigen. Interesse?",
  ],
  "dm_weak": [
   "Hallo! Ich bin {me}. Ich habe mir die Website von «{biz}» ({domain}) angesehen und bemerkt: {problem}. Dadurch können Kunden zur Konkurrenz gehen. Ich kann kostenlos eine einseitige Analyse mit Verbesserungen erstellen. Beispiele: {portfolio}. Soll ich sie schicken?",
   "Hallo! Ich war auf {domain} und habe bemerkt: {problem}. Ich kann eine kurze kostenlose Analyse schicken. Interesse?",
  ],
  "call": {
   "open": "Guten Tag! Mein Name ist {me}. Ich brauche nur eine Minute. Ist das «{biz}»?",
   "hook_nosite": "Ich habe Sie auf der Karte gefunden, aber keine Website. Finden Kunden Sie heute online?",
   "hook_weak": "Ich war auf Ihrer Website {domain} und habe bemerkt: {problem}. Ist Ihnen aufgefallen, dass dadurch Anfragen verloren gehen?",
   "offer": "Ich baue Websites für lokale Unternehmen{pricep}. Ich kann kostenlos eine kurze Analyse oder einen Entwurf erstellen, unverbindlich.",
   "close": "Soll ich es per WhatsApp oder E-Mail schicken? Oder telefonieren wir morgen 10 Minuten?",
   "secretary": "Ich möchte mit der Person sprechen, die für Website oder Marketing zuständig ist. Wann ist sie erreichbar?",
   "mail": "Natürlich schicke ich es. Nennen Sie mir bitte die Adresse und den Ansprechpartner.",
  },
  "em_subj_nosite": "Kostenloser Website-Entwurf für «{biz}»",
  "em_subj_weak": "Ideen zur Verbesserung von {domain}",
  "em_nosite": "Hallo!\n\nich bin {me}. Ich habe «{biz}» auf der Karte gefunden und gesehen, dass Sie keine eigene Website haben. Die meisten Kunden suchen Leistungen heute zuerst bei Google am Handy — eine Website hilft, sie nicht zu verlieren.\n\nIch baue Websites für lokale Unternehmen{pricep}. Ich kann kostenlos einen Entwurf für «{biz}» erstellen, unverbindlich.\n\nBeispiele meiner Arbeit: {portfolio}\n\nWenn es Sie interessiert, antworten Sie einfach auf diese E-Mail.\n\nFreundliche Grüße\n{me}\n{contact}",
  "em_weak": "Hallo!\n\nich bin {me}. Ich habe mir die Website von «{biz}» ({domain}) angesehen und bemerkt: {problem}. Das kann die Zahl der Anfragen verringern.\n\nIch baue Websites für lokale Unternehmen{pricep} und kann kostenlos eine kurze Analyse (1 Seite) mit konkreten Verbesserungen erstellen.\n\nBeispiele meiner Arbeit: {portfolio}\n\nWenn es Sie interessiert, antworten Sie einfach auf diese E-Mail.\n\nFreundliche Grüße\n{me}\n{contact}",
  "fu": [
   "Hallo! Ich erinnere an meine Nachricht wegen einer Website für «{biz}». Wenn es gerade nicht passt, sagen Sie einfach Bescheid, dann störe ich nicht weiter. Bei Interesse schicke ich den Entwurf in 1–2 Tagen.",
   "Dies ist meine letzte Nachricht. Ich habe einen kurzen Website-Plan für «{biz}» erstellt. Soll ich ihn schicken? Falls nicht, wünsche ich Ihnen viel Erfolg!",
  ],
  "obj": {
   "price": "Ich verstehe. Ich zeige Ihnen zuerst kostenlos einen Entwurf, und Sie entscheiden, ob er den Preis wert ist. Oft bezahlen ein bis zwei neue Kunden die Website.",
   "noneed": "Ich verstehe. Viele denken so, bis sie sehen, wie viele Kunden bei Google suchen. Ich kann Ihnen in zwei Minuten kostenlos zeigen, wie Sie im Vergleich zur Konkurrenz aussehen.",
   "think": "Natürlich. Damit die Entscheidung leichter fällt, schicke ich den Entwurf und eine kurze Beschreibung. Passt Dienstag oder Donnerstag für ein Follow-up?",
   "have": "Schön, dass Sie schon daran arbeiten. Wenn Sie möchten, schicke ich eine kostenlose Analyse der aktuellen Seite als zweite Meinung, unverbindlich.",
   "social": "Social Media ist gut für Aufmerksamkeit, aber Kunden suchen Websites bei Google. Die Website ergänzt Social Media, statt sie zu ersetzen. Ich kann Beispiele zeigen.",
   "fine": "Freut mich, dass Sie zufrieden sind. Ich zeige Ihnen kostenlos, wie die Seite am Handy aussieht und wie schnell sie lädt. Wenn alles gut ist, sage ich das auch.",
  },
 },
}
LANGS = [("ru", "🇷🇺 RU"), ("en", "🇬🇧 EN"), ("fi", "🇫🇮 FI"),
         ("et", "🇪🇪 ET"), ("sv", "🇸🇪 SV"), ("de", "🇩🇪 DE")]
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


from lib.sales import (SCRIPTS as _SCRIPTS, PLAN_NOSITE as _PLAN_NOSITE,
                       PLAN_WEAK as _PLAN_WEAK, GENERAL_TIPS as _GENERAL_TIPS,
                       OBJECTIONS as _OBJECTIONS)
T.update(_SCRIPTS)  # продающие тексты FULLY заменяют старые шаблоны выше
PLAN_NOSITE, PLAN_WEAK = _PLAN_NOSITE, _PLAN_WEAK
GENERAL_TIPS, OBJECTIONS = _GENERAL_TIPS, _OBJECTIONS


# ---------- Telegram ----------
def _strip_styles(m):
    if isinstance(m, dict):
        m.pop("style", None)
        for v in m.values():
            _strip_styles(v)
    elif isinstance(m, list):
        for v in m:
            _strip_styles(v)


def _has_style(m):
    if isinstance(m, dict):
        if "style" in m:
            return True
        return any(_has_style(v) for v in m.values())
    if isinstance(m, list):
        return any(_has_style(v) for v in m)
    return False


def tg(method, **params):
    def _call(p):
        req = urllib.request.Request(API + method, data=json.dumps(p).encode(),
                                     headers={"Content-Type": "application/json"})
        resp = urllib.request.urlopen(req, timeout=10).read()
        return json.loads(resp)

    try:
        resp = _call(params)
        if resp.get("ok"):
            return resp.get("result")
        # Если Telegram не принял style кнопок — повторяем без style
        desc = str(resp.get("description") or "")
        if "reply_markup" in params and _has_style(params["reply_markup"]) and "style" in desc.lower():
            p2 = json.loads(json.dumps(params))
            _strip_styles(p2.get("reply_markup"))
            resp = _call(p2)
            return resp.get("result")
        print("tg error", method, desc)
        return None
    except Exception as e:
        # fallback: старый API мог упасть на неизвестном поле style
        if "reply_markup" in params and _has_style(params["reply_markup"]):
            try:
                p2 = json.loads(json.dumps(params))
                _strip_styles(p2.get("reply_markup"))
                resp = _call(p2)
                return resp.get("result")
            except Exception:
                pass
        print("tg error", method, e)
        return None


def delete_msg(chat_id, message_id):
    """Тихо удаляет сообщение (ошибки не страшны: сообщение могло уже быть удалено)."""
    if message_id:
        tg("deleteMessage", chat_id=chat_id, message_id=message_id)


# Память о служебных сообщениях чата: новое сообщение того же типа заменяет старое,
# чтобы чат не засорялся. Живёт, пока прогрет инстанс Vercel; при холодной старте
# бот просто шлёт новое сообщение — ничего не ломается.
_CHAT = {}


def remember(chat_id, kind, message_id):
    st = _CHAT.setdefault(chat_id, {})
    old = st.get(kind)
    st[kind] = message_id
    if old and old != message_id:
        delete_msg(chat_id, old)


def edit_msg(chat_id, message_id, text, markup):
    """Редактирует сообщение на месте (без нового сообщения в чате)."""
    return bool(tg("editMessageText", chat_id=chat_id, message_id=message_id, text=text,
                   parse_mode="HTML", reply_markup=markup, disable_web_page_preview=True))


# Кэш результатов поиска: листание страниц больше не запускает поиск заново.
_CACHE = {}
CACHE_TTL = 30 * 60  # результаты живут полчаса


def cache_store(key, mode, city, res, flags=""):
    token = hashlib.md5(f"{key}|{mode}|{city.lower()}|{flags}".encode()).hexdigest()[:10]
    now = time.time()
    for t in [t for t, v in _CACHE.items() if now - v["ts"] > CACHE_TTL]:
        _CACHE.pop(t, None)
    entry = {"key": key, "mode": mode, "city": city, "res": res,
             "flags": flags, "ts": now}
    _CACHE[token] = entry
    if CRM_ON:  # постоянный кэш на 7 дней: повторный поиск не трогает карты вообще
        kv_cmd("SET", "cache:" + token, json.dumps(entry, ensure_ascii=False), "EX", 7 * 86400)
    return token


def cache_load(token):
    v = _CACHE.get(token)
    if v and time.time() - v["ts"] <= CACHE_TTL:
        return v
    if CRM_ON:
        raw = kv_cmd("GET", "cache:" + token)
        if raw:
            try:
                v = json.loads(raw)
                _CACHE[token] = v
                return v
            except Exception:
                pass
    return None


# ---------- CRM: база клиентов в бесплатном Upstash Redis ----------
def kv_cmd(*args):
    req = urllib.request.Request(UPSTASH_URL, data=json.dumps(list(args)).encode(),
                                 headers={"Authorization": "Bearer " + UPSTASH_TOKEN,
                                          "Content-Type": "application/json"})
    try:
        return json.loads(urllib.request.urlopen(req, timeout=8).read()).get("result")
    except Exception as e:
        print("kv error", e)
        return None


def lead_id(it):
    """Один id для CRM, истории, Mini App и cron."""
    return ledger.lead_id(it.get("name", ""), it.get("addr", ""),
                          it.get("site", ""), it.get("city", ""),
                          it.get("lat"), it.get("lon"))


def lead_socials(tags):
    """Достаём соцсети из OSM-тегов и приводим к ссылкам."""
    out = []
    rules = [
        ("contact:instagram", "Instagram", "https://instagram.com/"),
        ("instagram", "Instagram", "https://instagram.com/"),
        ("contact:facebook", "Facebook", "https://facebook.com/"),
        ("facebook", "Facebook", "https://facebook.com/"),
        ("contact:telegram", "Telegram", "https://t.me/"),
        ("telegram", "Telegram", "https://t.me/"),
        ("contact:vk", "ВКонтакте", "https://vk.com/"),
        ("vk", "ВКонтакте", "https://vk.com/"),
    ]
    for tag, label, prefix in rules:
        value = (tags.get(tag) or "").strip()
        if not value:
            continue
        url = value if value.startswith("http") else prefix + value.lstrip("@/")
        out.append({"label": label, "url": url})
    return out[:4]


def lead_audit(it, issues=None):
    """Дешёвый аудит из уже собранных данных — без дополнительных запросов."""
    keys = {k for k, _ in (issues or it.get("issues") or [])}
    if not it.get("site"):
        return {"site_ok": False, "https": False, "phone_on_site": False,
                "issues": ["нет сайта"]}
    return {
        "site_ok": not ({"dead", "social"} & keys),
        "https": "https" not in keys,
        "phone_on_site": None,
        "mobile": "mobile" not in keys,
        "load_s": None,
        "issues": [txt for k, txt in (issues or it.get("issues") or [])][:4],
    }


def crm_all():
    if not CRM_ON:
        return {}
    raw = kv_cmd("GET", "crm")
    try:
        return json.loads(raw) if raw else {}
    except Exception:
        return {}


def crm_save(db):
    kv_cmd("SET", "crm", json.dumps(db, ensure_ascii=False))


CRM_LABEL = {"contacted": "✍️ написали", "deal": "🤝 сделка", "refused": "❌ отказ"}


def crm_set(it, status):
    db = crm_all()
    lid = lead_id(it)
    rec = db.get(lid, {})
    rec.update(name=it["name"], status=status, ts=int(time.time()),
               site=it.get("site", ""), phone=it.get("phone", ""))
    if status == "contacted":
        rec["next"] = int(time.time()) + 3 * 86400  # напомнить через 3 дня
        rec["fu"] = 1
    else:
        rec.pop("next", None)
    db[lid] = rec
    crm_save(db)
    try:
        ledger.set_status(lid, "lost" if status == "refused" else status,
                          it.get("name", ""), it.get("site", ""))
    except Exception as e:
        print("ledger sync error", e)
    return rec


def crm_toggle_fav(it):
    db = crm_all()
    rec = db.get(lead_id(it), {})
    rec.update(name=it["name"], site=it.get("site", ""), phone=it.get("phone", ""))
    rec["fav"] = not rec.get("fav", False)
    if not rec.get("status"):
        rec["status"] = "new"
    db[lead_id(it)] = rec
    crm_save(db)
    return rec


# ---------- загрузка файлов в Telegram (CSV, скриншоты) ----------
def tg_upload(method, fields, filename, content, field="document"):
    boundary = "----leadradar" + hashlib.md5(str(time.time()).encode()).hexdigest()
    body = b""
    for k, v in fields.items():
        body += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n"
                 f"{v}\r\n").encode()
    body += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{field}\"; "
             f"filename=\"{filename}\"\r\nContent-Type: application/octet-stream\r\n\r\n").encode()
    body += content + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(API + method, data=body,
                                 headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    try:
        return json.loads(urllib.request.urlopen(req, timeout=40).read()).get("result")
    except Exception as e:
        print("tg upload error", method, e)
        return None


def export_csv(chat_id, token):
    hit = cache_load(token)
    if not hit:
        tg("sendMessage", chat_id=chat_id, text="Поиск устарел — запусти новый, и кнопка CSV появится снова.")
        return
    items = hit["res"][0]
    buf = io.StringIO()
    wr = csv.writer(buf)
    wr.writerow(["Название", "Тип", "Балл", "Сайт", "Телефон", "Email", "Адрес", "Проблемы", "Карта"])
    for it in items:
        wr.writerow([it["name"], "нет сайта" if it["kind"] == "nosite" else "слабый сайт",
                     it["score"], it["site"], it["phone"], it["email"], it["addr"],
                     "; ".join(t for _, t in it["issues"]),
                     f"https://www.google.com/maps/search/?api=1&query={it['lat']},{it['lon']}"])
    fname = f"leads-{hit['key']}-{datetime.date.today().isoformat()}.csv"
    ok = tg_upload("sendDocument", {"chat_id": str(chat_id),
                                    "caption": f"📥 {len(items)} клиентов. Открывается в Excel / Google Sheets."},
                   fname, buf.getvalue().encode("utf-8-sig"))
    if not ok:
        tg("sendMessage", chat_id=chat_id, text="⚠️ Не смог отправить файл, попробуй ещё раз.")


# ---------- PageSpeed: точная скорость сайта от Google ----------
def pagespeed(url):
    api = ("https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url="
           + urllib.parse.quote(url, safe="") + "&strategy=mobile&category=performance")
    if PSI_KEY:
        api += "&key=" + PSI_KEY
    return get_json(api, timeout=50)


def send_pagespeed(chat_id, it):
    status = tg("sendMessage", chat_id=chat_id,
                text=f"⏳ Замеряю скорость {it['site']} (Google PageSpeed, до 40 секунд)...")
    try:
        data = pagespeed(it["site"])
    except Exception as e:
        print("psi error", e)
        data = None
    if status:
        delete_msg(chat_id, status["message_id"])
    if not data or "lighthouseResult" not in data:
        tg("sendMessage", chat_id=chat_id,
           text="⚠️ Google не смог замерить этот сайт (закрыт от ботов или недоступен).")
        return
    lh = data["lighthouseResult"]
    score = round((lh.get("categories", {}).get("performance", {}).get("score") or 0) * 100)
    a = lh.get("audits", {})

    def metric(key, fmt="{:.1f} с"):
        v = a.get(key, {}).get("numericValue")
        return fmt.format(v / 1000) if v is not None and "с" in fmt else (fmt.format(v) if v is not None else "—")

    emoji = "🟢" if score >= 90 else "🟡" if score >= 50 else "🔴"
    text = (f"🚀 <b>PageSpeed: {esc(it['name'])}</b>\n"
            f"📱 Мобильная версия: <b>{emoji} {score}/100</b>\n\n"
            f"• Первая отрисовка: {metric('first-contentful-paint')}\n"
            f"• Основной контент: {metric('largest-contentful-paint')}\n"
            f"• Блокировка скриптами: {metric('total-blocking-time', '{:.0f} мс')}\n"
            f"• Сдвиги макета (CLS): {metric('cumulative-layout-shift', '{:.2f}')}\n\n")
    if score < 50:
        text += "💡 <i>Отличный аргумент для письма: «Ваш сайт набирает X/100 в Google PageSpeed, клиенты с телефона ждут Y секунд».</i>"
    elif score < 90:
        text += "💡 <i>Есть что улучшить — можно предложить точечную оптимизацию.</i>"
    else:
        text += "💡 <i>Скорость в порядке. Ищи другие проблемы: дизайн, SEO, мобильную версию.</i>"
    shot = a.get("final-screenshot", {}).get("details", {}).get("data", "")
    if shot.startswith("data:image"):
        try:
            img = base64.b64decode(shot.split(",", 1)[1])
            tg_upload("sendPhoto", {"chat_id": str(chat_id), "caption": text[:1000],
                                    "parse_mode": "HTML"}, "pagespeed.jpg", img, field="photo")
            return
        except Exception as e:
            print("psi shot error", e)
    tg("sendMessage", chat_id=chat_id, text=text, parse_mode="HTML")


def get_json(url, data=None, timeout=25):
    req = urllib.request.Request(url, data=data, headers=UA)
    return json.loads(urllib.request.urlopen(req, timeout=timeout).read())


def get_bytes(url, timeout=15):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read()


def osm_api_data(bbox, niche_tags):
    """Запасной путь: основной API OpenStreetMap (другая инфраструктура, не Overpass).
    Если район слишком плотный (>50000 узлов) — автоматически уменьшаем область."""
    want = set(tuple(t.split("=")) for t in niche_tags)
    s, w, n, e = bbox
    root = None
    for _ in range(4):
        url = f"https://api.openstreetmap.org/api/0.6/map?bbox={w},{s},{e},{n}"
        try:
            root = ET.fromstring(get_bytes(url, timeout=12))
            break
        except urllib.error.HTTPError as err:
            body = err.read()
            if err.code == 400 and b"too many nodes" in body:
                clat, clon = (s + n) / 2, (w + e) / 2
                hs, hw = (n - s) / 4, (e - w) / 4
                s, w, n, e = clat - hs, clon - hw, clat + hs, clon + hw
                continue
            raise
    if root is None:
        raise RuntimeError("osm area too dense")
    nodes, elements = {}, []
    for nd in root.iter("node"):
        la, lo = float(nd.get("lat")), float(nd.get("lon"))
        nodes[nd.get("id")] = (la, lo)
        tags = {t.get("k"): t.get("v") for t in nd.findall("tag")}
        if tags.get("name") and any(tags.get(k) == v for k, v in want):
            elements.append({"tags": tags, "lat": la, "lon": lo})
    for wy in root.iter("way"):
        tags = {t.get("k"): t.get("v") for t in wy.findall("tag")}
        if not tags.get("name") or not any(tags.get(k) == v for k, v in want):
            continue
        pts = [nodes[r.get("ref")] for r in wy.findall("nd") if r.get("ref") in nodes]
        if pts:
            elements.append({"tags": tags,
                             "center": {"lat": sum(p[0] for p in pts) / len(pts),
                                        "lon": sum(p[1] for p in pts) / len(pts)}})
    return {"elements": elements}


def photon_leads(niche_key, city, lat, lon):
    """Ещё один независимый источник: Photon (инфраструктура Komoot).
    Находит объекты по названию, полные теги (сайт/телефон) добираем из API OSM."""
    words = NICHE_QUERY.get(niche_key, [niche_key])
    want = set(tuple(t.split("=")) for t in NICHES[niche_key][1])
    feats = {}
    for word in words[:4]:
        try:
            d = get_json(f"https://photon.komoot.io/api/?limit=100&lat={lat}&lon={lon}&q="
                         + urllib.parse.quote(f"{word} {city}"), timeout=5)
            for f in d.get("features", []):
                p = f.get("properties", {})
                if (p.get("osm_key"), p.get("osm_value")) in want and p.get("osm_id"):
                    feats[(p.get("osm_type"), p["osm_id"])] = f
        except Exception as err:
            print("photon poi fail", err)
    if not feats:
        raise RuntimeError("photon empty")
    kind_map = {"N": "node", "W": "way", "R": "relation"}

    def fetch(item):
        (ot, oid), f = item
        p = f.get("properties", {})
        try:
            d = get_json(f"https://api.openstreetmap.org/api/0.6/"
                         f"{kind_map.get(ot, 'node')}/{oid}.json", timeout=5)
            tags = d.get("elements", [{}])[0].get("tags", {})
        except Exception:
            tags = {}
        c = f.get("geometry", {}).get("coordinates") or [lon, lat]
        if not tags.get("name") and p.get("name"):
            tags["name"] = p["name"]
        return {"tags": tags, "lat": c[1], "lon": c[0]}

    with cf.ThreadPoolExecutor(max_workers=16) as ex:
        els = list(ex.map(fetch, list(feats.items())[:60]))
    return {"elements": [e for e in els if e["tags"].get("name")]}


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
                                   timeout=4, context=ctx)
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
    if elapsed > 3:
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
def parse_city(text):
    """«Helsinki» или «Helsinki, 10 км» -> (город, радиус_км или 0)."""
    m = re.search(r"[,\s]+(\d{1,2})\s*(?:км|km)\s*$", text.strip(), re.I)
    if m:
        return text[:m.start()].strip(" ,"), min(int(m.group(1)), 50)
    return text.strip(), 0


def geocode(city):
    """Координаты города. Nominatim, а если он недоступен — запасной Photon.
    Возвращает (lat, lon, bbox), строку 'notfound' или None (сервисы легли)."""
    answered = False
    try:
        geo = get_json("https://nominatim.openstreetmap.org/search?format=json&limit=1&q="
                       + urllib.parse.quote(city), timeout=8)
        answered = True
        if geo:
            s, n, w, e = map(float, geo[0]["boundingbox"])
            return float(geo[0]["lat"]), float(geo[0]["lon"]), (s, w, n, e)
    except Exception as e:
        print("nominatim fail", e)
    try:
        geo = get_json("https://photon.komoot.io/api/?limit=1&q="
                       + urllib.parse.quote(city), timeout=8)
        answered = True
        f = (geo.get("features") or [None])[0]
        if f:
            lon, lat = f["geometry"]["coordinates"]
            ext = f.get("properties", {}).get("extent")
            bbox = (ext[1], ext[0], ext[3], ext[2]) if ext else None
            return lat, lon, bbox
    except Exception as e:
        print("photon fail", e)
    return "notfound" if answered else None


def find_leads(niche_key, mode, city, flags="", budget_s=45):
    """flags: p — только с телефоном, e — только с email, c — без сетей."""
    deadline = time.time() + max(12, min(55, float(budget_s or 45)))
    city, radius = parse_city(city)
    geo = geocode(city)
    if geo == "notfound":
        return None
    if geo is None:
        try:
            tok = hashlib.md5(f"{niche_key}|{mode}|{city.lower()}|{flags}".encode()).hexdigest()[:10]
            stale = cache_load(tok)
            if stale and stale.get("res"):
                return stale["res"]
        except Exception:
            pass
        raise RuntimeError("geocode down")
    lat, lon, bbox = geo
    if radius:
        dlat = radius / 111.0
        dlon = radius / (111.0 * max(0.2, math.cos(math.radians(lat))))
        s, w, n, e = lat - dlat, lon - dlon, lat + dlat, lon + dlon
        area = f"(around:{radius * 1000},{lat},{lon})"
    else:
        if bbox:
            s, w, n, e = bbox
            # у больших городов огромные границы — сужаем вокруг центра,
            # чтобы карты отвечали быстро и не падали по таймауту
            if n - s > 0.6:
                s, n = lat - 0.3, lat + 0.3
            if e - w > 0.6:
                w, e = lon - 0.3, lon + 0.3
        else:
            s, w, n, e = lat - 0.15, lon - 0.15, lat + 0.15, lon + 0.15
        area = f"({s},{w},{n},{e})"
    parts = ""
    for tag in NICHES[niche_key][1]:
        k, v = tag.split("=")
        parts += f'nwr["{k}"="{v}"]["name"]{area};'
    query = f"[out:json][timeout:10];({parts});out tags center 600;"
    payload = urllib.parse.urlencode({"data": query}).encode()

    stop = threading.Event()

    def try_overpass():
        for ep in OVERPASS:
            if stop.is_set():  # Photon уже ответил — не опрашиваем остальные серверы
                break
            left = deadline - time.time()
            if left < 12:
                break
            try:
                return get_json(ep, data=payload, timeout=max(3, min(6, left - 10)))
            except Exception as err:
                print("overpass fail", ep, err)
        return None

    ov_data, ph_data = None, None
    with cf.ThreadPoolExecutor(max_workers=2) as ex:
        f_ov = ex.submit(try_overpass)
        f_ph = ex.submit(photon_leads, niche_key, city, lat, lon)
        # Раньше ждали Overpass 12 с, и только потом запускали Photon — поиск занимал 30–40 с.
        # Теперь оба источника стартуют одновременно: Photon обычно готов за 2–5 с.
        try:
            ph_data = f_ph.result(timeout=min(14, max(6, deadline - time.time() - 12)))
        except Exception as err:
            print("photon fail", err)
        stop.set()
        try:
            ov_data = f_ov.result(timeout=7)  # текущий запрос успеет завершиться
        except Exception as err:
            print("overpass race fail", err)
    if ov_data and ph_data:
        data = {"elements": ov_data.get("elements", []) + ph_data.get("elements", [])}
        print("used overpass + photon (merged)")
    else:
        data = ov_data or ph_data
        if data:
            print("used", "overpass" if ov_data else "photon")
    if data is None:
        # последний рубеж — основной API OpenStreetMap
        try:
            data = osm_api_data((s, w, n, e), NICHES[niche_key][1])
            print("used osm api fallback")
        except Exception as err:
            print("osm api fail", err)
            try:
                tok = hashlib.md5(f"{niche_key}|{mode}|{city.lower()}|{flags}".encode()).hexdigest()[:10]
                stale = cache_load(tok)
                if stale and stale.get("res"):
                    print("used stale cache after maps down")
                    return stale["res"]
            except Exception:
                pass
            raise RuntimeError("maps down")

    elements = data.get("elements", [])
    name_counts = {}
    if "c" in flags:  # сеть = одно и то же название встречается 3+ раз
        for el in elements:
            nm = el.get("tags", {}).get("name", "").strip().lower()
            name_counts[nm] = name_counts.get(nm, 0) + 1

    nosite, with_site, seen = [], [], set()
    for el in elements:
        t = el.get("tags", {})
        if niche_key == "barber":  # барбершоп ≠ салон красоты: мужской зал или barber в названии
            if t.get("male") != "yes" and not re.search(r"barber|parturi", t.get("name", ""), re.I):
                continue
        lat = el.get("lat") or el.get("center", {}).get("lat")
        lon = el.get("lon") or el.get("center", {}).get("lon")
        if lat is None:
            continue
        dup = (t["name"].strip().lower(), round(lat, 4), round(lon, 4))
        if dup in seen:  # OSM часто отдаёт один объект дважды (node + way)
            continue
        seen.add(dup)
        if "c" in flags and name_counts.get(t["name"].strip().lower(), 0) >= 3:
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
            "score": 0, "issues": [], "city": city,
            "socials": lead_socials(t),
            "hours": t.get("opening_hours") or "",
        }
        it["id"] = lead_id(it)
        it["audit"] = lead_audit(it)
        if "p" in flags and not it["phone"]:
            continue
        if "e" in flags and not it["email"]:
            continue
        (with_site if site else nosite).append(it)

    nosite.sort(key=lambda x: (not x["phone"], not x["email"]))
    for it in nosite:
        it["kind"] = "nosite"

    weak = []
    if mode in ("w", "a") and with_site:
        cands = with_site[:MAX_ANALYZE]
        with cf.ThreadPoolExecutor(max_workers=20) as ex:
            futs = {ex.submit(analyze, it["site"]): it for it in cands}
            done, _ = cf.wait(futs, timeout=max(6, min(20, deadline - time.time())))
            for f in done:
                try:
                    it = futs[f]
                    it["score"], it["issues"] = f.result()
                    it["audit"] = lead_audit(it, it["issues"])
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
    rows = []
    if MINIAPP_URL:
        rows.append([{"text": "🚀 Открыть мини-приложение", "web_app": {"url": MINIAPP_URL}, "style": "primary"}])
    rows.append([{"text": "⚙️ Настройки", "callback_data": "settings", "style": "primary"},
                 {"text": "ℹ️ О приложении", "callback_data": "about", "style": "success"}])
    rows.append([{"text": "🎯 Советы по продажам", "callback_data": "tips", "style": "success"},
                 {"text": "📊 Воронка", "callback_data": "funnel_info", "style": "primary"}])
    return {"inline_keyboard": rows}


MENU_TEXT = ("🚀 <b>Lead Radar Mini App</b>\n\n"
             "Основная работа теперь в мини-приложении: поиск лидов, карта, скрипты, история и воронка.\n\n"
             "В боте — быстрые настройки, подсказки и информация о приложении.")


def potential_text(n):
    """Показывает масштаб возможности, если в настройках указана цена услуги."""
    m = re.search(r"(\d[\d\s]*)", PRICE or "")
    if not m or not n:
        return ""
    cur = re.sub(r"^.*?\d[\d\s]*", "", PRICE).strip(" .–-") or "€"
    total = int(m.group(1).replace(" ", "")) * n
    return f"\n💰 Потенциал: {n} клиентов × {m.group(1).strip()} {cur} = <b>{total:,} {cur}</b>"


def send_menu(chat_id):
    m = tg("sendMessage", chat_id=chat_id, reply_markup=menu_markup(), parse_mode="HTML", text=MENU_TEXT)
    if m:
        remember(chat_id, "menu", m["message_id"])  # старое меню удалится само


def modes_markup(key, flags=""):
    btns = [{"text": MODES[m], "callback_data": f"m|{key}|{m}|{flags}"} for m in ("n", "w", "a")]

    def toggle(ch):
        return flags.replace(ch, "") if ch in flags else flags + ch

    def tog_btn(ch, label):
        return {"text": label + (" ✅" if ch in flags else ""),
                "callback_data": f"f|{key}|{toggle(ch)}"}

    return {"inline_keyboard": [
        [btns[0], btns[1]], [btns[2]],
        [tog_btn("p", "📞 Только с телефоном"), tog_btn("e", "✉️ Только с email")],
        [tog_btn("c", "🏪 Без сетей и франшиз")],
        [{"text": "⬅️ Назад", "callback_data": "back_menu", "style": "primary"}],
    ]}


def modes_text(key, flags=""):
    fl = [lbl for ch, lbl in (("p", "только с телефоном"), ("e", "только с email"),
                              ("c", "без сетей")) if ch in flags]
    return (f"Ниша: {NICHES[key][0]}\nЧто ищем?" +
            ("\n🧰 Фильтры: " + ", ".join(fl) if fl else ""))


def prompt_text(key, mode, flags=""):
    fl = [lbl for ch, lbl in (("p", "только с телефоном"), ("e", "только с email"),
                              ("c", "без сетей")) if ch in flags]
    return (f"🔎 Ниша: {NICHES[key][0]}\n🎯 Режим: {MODES[mode]}" +
            ("\n🧰 Фильтры: " + ", ".join(fl) if fl else "") +
            "\n\nПросто напиши город (или ответь на это сообщение).\n"
            "Можно с радиусом: «Helsinki, 10 км»")


def send_prompt(chat_id, key, mode, flags=""):
    # force_reply нельзя поставить через редактирование, поэтому шлём новое сообщение,
    # а старое (выбор режима) удаляем — в чате ничего не копится
    m = tg("sendMessage", chat_id=chat_id, text=prompt_text(key, mode, flags),
           reply_markup={"force_reply": True,
                         "input_field_placeholder": "Например: Helsinki или Turku, 10 км"})
    if m:
        remember(chat_id, "flow", m["message_id"])
    _CHAT.setdefault(chat_id, {})["pending"] = (key, mode, flags)  # город можно писать без reply


def send_tips(chat_id):
    m = tg("sendMessage", chat_id=chat_id, text=GENERAL_TIPS, parse_mode="HTML",
           reply_markup={"inline_keyboard": [[{"text": "🔄 Меню", "callback_data": "menu", "style": "primary"},
                                              {"text": "❌ Закрыть", "callback_data": "del", "style": "danger"}]]})
    if m:
        remember(chat_id, "tips", m["message_id"])


def send_about(chat_id):
    text = ("ℹ️ <b>О Lead Radar</b>\n\n"
            "Lead Radar помогает находить бизнесы без сайта или со слабым сайтом и готовит скрипты продаж.\n\n"
            "• Основной режим — мини-приложение\n"
            "• Поиск по нишам, карта, история, воронка\n"
            "• Скрипты на 6 языках: RU, EN, FI, ET, SV, DE\n"
            "• Экспорт CSV, статусы лидов, CRM-память")
    if MINIAPP_URL:
        text += "\n\n🚀 Открой мини-приложение кнопкой в меню."
    m = tg("sendMessage", chat_id=chat_id, text=text, parse_mode="HTML",
           reply_markup={"inline_keyboard": [[{"text": "🚀 Мини-приложение", "web_app": {"url": MINIAPP_URL}, "style": "primary"}] if MINIAPP_URL else [],
                                              [{"text": "🔄 Меню", "callback_data": "menu", "style": "primary"},
                                               {"text": "❌ Закрыть", "callback_data": "del", "style": "danger"}]]})
    if m:
        remember(chat_id, "about", m["message_id"])


def send_settings(chat_id):
    text = ("⚙️ <b>Настройки</b>\n\n"
            f"Имя: {esc(ME)}\nКонтакт: {esc(CONTACT)}\nПортфолио: {esc(PORTFOLIO)}\n"
            f"Цена: {esc(PRICE or '— не указана')}\nЯзык по умолчанию: {DEFAULT_LANG.upper()}\n\n"
            "Меняются в Vercel: Settings → Environment Variables (MY_NAME, MY_CONTACT, MY_PORTFOLIO, MY_PRICE, DEFAULT_LANG), потом Redeploy.\n\n"
            "Тема, шрифт и анимации настраиваются внутри мини-приложения (⚙️).")
    m = tg("sendMessage", chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=CLOSE_KB)
    if m:
        remember(chat_id, "settings", m["message_id"])


def send_card(chat_id, it, city, token=None, idx=0, db=None):
    text = f"<b>{esc(it['name'])}</b>"
    if it["kind"] == "nosite":
        text += "  🚫 нет сайта\n"
        pitch_keys = ["nosite"]
    else:
        emoji = "🔴" if it["score"] >= 60 else "🟡"
        dom = urllib.parse.urlparse(it["site"]).netloc.replace("www.", "")
        site_url = esc(it.get("site") or "")
        dead = any(k == "dead" for k, _ in it.get("issues", []))
        text += f"  {emoji} сайт {it['score']}/100\n"
        text += f"🌐 <a href=\"{site_url}\">{esc(dom)}</a>\n"
        if dead:
            text += "⚠️ Сайт есть, но сейчас может не открываться — ссылку всё равно даю выше.\n"
        issues_txt = "; ".join(t for _, t in it.get("issues", []))
        if issues_txt:
            text += "⚠️ " + esc(issues_txt) + "\n"
        pitch_keys = list(dict.fromkeys(k for k, _ in it.get("issues", [])))
    if it["addr"]:
        text += f"📍 {esc(it['addr'])}\n"
    text += f"📞 {esc(it['phone'])}\n" if it["phone"] else "📞 телефона нет\n"
    if it["email"]:
        text += f"✉️ {esc(it['email'])}\n"
    text += "💡 <i>Предложи: " + esc(", ".join(PITCH[k] for k in pitch_keys[:3])) + "</i>"
    rec = (db or {}).get(lead_id(it))
    if rec:
        mark = CRM_LABEL.get(rec.get("status"), "")
        if rec.get("fav"):
            mark = ("⭐ " + mark).strip()
        if mark:
            text += f"\n📌 {mark}"

    row1 = [{"text": "📍 На карте",
             "url": f"https://www.google.com/maps/search/?api=1&query={it['lat']},{it['lon']}"}]
    if it["kind"] == "weak":
        row1.append({"text": "🌐 Открыть сайт", "url": it["site"]})
    else:
        row1.append({"text": "🔎 Проверить в Google",
                     "url": "https://www.google.com/search?q=" + urllib.parse.quote(f"{it['name']} {city}")})
    rows = [row1]
    digits = "".join(c for c in it["phone"] if c.isdigit())
    if it["phone"].startswith("+") and len(digits) >= 8:
        rows.append([{"text": "💬 Написать в WhatsApp",
                      "url": f"https://wa.me/{digits}"}])
    if token is not None:
        if it["kind"] == "weak":
            rows.append([{"text": "🖼 Скриншот сайта", "callback_data": f"v|{token}|{idx}|shot"},
                         {"text": "🚀 Скорость (Google)", "callback_data": f"v|{token}|{idx}|ps"}])
        if CRM_ON:
            rows.append([{"text": "✅ Написал", "callback_data": f"c|{token}|{idx}|contacted"},
                         {"text": "🤝 Сделка", "callback_data": f"c|{token}|{idx}|deal"}])
            rows.append([{"text": "❌ Отказ", "callback_data": f"c|{token}|{idx}|refused"},
                         {"text": "⭐ В избранное", "callback_data": f"c|{token}|{idx}|fav"}])
    rows.append([{"text": "✍️ Скрипты и подсказки", "callback_data": "t|o"}])
    return tg("sendMessage", chat_id=chat_id, text=text, parse_mode="HTML",
              disable_web_page_preview=True, reply_markup={"inline_keyboard": rows})


def clear_cards(chat_id):
    """Удаляет карточки и сводку прошлого поиска — чат не засоряется."""
    st = _CHAT.setdefault(chat_id, {})
    for mid in st.get("cards", []):
        delete_msg(chat_id, mid)
    st["cards"] = []
    st = _CHAT.setdefault(chat_id, {})
    for kind in ("summary", "pager", "panel"):
        if st.get(kind):
            delete_msg(chat_id, st.pop(kind))


def run_search(chat_id, key, mode, city, offset, token=None, cleanup=(), flags=""):
    city = " ".join(city.split())[:80]
    res, fresh = None, False
    if token:
        hit = cache_load(token)  # листаем/показываем снова — поиск уже сделан, берём из кэша
        if hit and hit["key"] == key and hit["mode"] == mode:
            res, city, flags = hit["res"], hit["city"], hit.get("flags", "")
    if res is None:
        fresh = True
        clear_cards(chat_id)  # новый поиск — убираем карточки прошлого
        status = tg("sendMessage", chat_id=chat_id,
                    text="⏳ Ищу клиентов и проверяю сайты — обычно 5–15 секунд...")
        try:
            res = find_leads(key, mode, city, flags)
        except Exception as e:
            print("search error", e)
            res = "error"
        if status:  # статус больше не нужен — сразу убираем
            delete_msg(chat_id, status["message_id"])
    for mid in cleanup:  # сообщение пользователя с городом и подсказка "напиши город"
        delete_msg(chat_id, mid)
    if res == "error":
        tg("sendMessage", chat_id=chat_id,
           text="⚠️ Все серверы карт сейчас перегружены — я пробовал 4 запасных и основной API OSM. "
                "Это временно: подожди 1–2 минуты и повтори поиск.",
           reply_markup={"inline_keyboard": [[{"text": "🔄 Меню", "callback_data": "menu", "style": "primary"},
                                              {"text": "❌ Закрыть", "callback_data": "del", "style": "danger"}]]})
        return
    if res is None:
        tg("sendMessage", chat_id=chat_id, text="Не нашёл такой город 🤷 Проверь название или напиши по-английски.")
        return send_menu(chat_id)
    items, n_no, n_weak, n_with = res
    new_ids = []
    if fresh:
        try:
            q = ledger.query_id(key, mode, city, flags)
            new_ids = ledger.record_search(q, city, NICHES[key][0], mode, flags,
                                           res[0], key)
        except Exception as e:
            print("history error", e)
    db = crm_all()
    if CRM_ON:  # уже обработанных клиентов в поиске больше не показываем
        items = [it for it in items
                 if db.get(lead_id(it), {}).get("status") not in ("contacted", "deal", "refused")]
    if fresh:
        token = cache_store(key, mode, city, res, flags)
        sm = tg("sendMessage", chat_id=chat_id, parse_mode="HTML",
                text=(f"📊 <b>{esc(city)}</b>, {NICHES[key][0]}\n"
                      f"🚫 без сайта: <b>{n_no}</b>\n"
                      f"🐌 слабых сайтов: <b>{n_weak}</b> (проверено до {MAX_ANALYZE} из {n_with})"
                      + (f"\n🆕 новых: <b>{len(new_ids)}</b>" if new_ids else "")
                      + potential_text(n_no)))
        if sm:
            remember(chat_id, "summary", sm["message_id"])
    if not items:
        tg("sendMessage", chat_id=chat_id,
           text="Подходящих не нашёл (или все уже в твоей базе ✅). Попробуй другую нишу, режим или фильтры.")
        return send_menu(chat_id)
    st = _CHAT.setdefault(chat_id, {})
    if not fresh:  # листаем дальше — карточки прошлой страницы убираем
        for mid in st.get("cards", []):
            delete_msg(chat_id, mid)
        st["cards"] = []
    for i, it in enumerate(items[offset:offset + PAGE], start=offset):
        m = send_card(chat_id, it, city, token=token, idx=i, db=db)
        if m:
            st.setdefault("cards", []).append(m["message_id"])
    end = min(offset + PAGE, len(items))
    buttons = []
    if end < len(items):
        buttons.append({"text": "➡️ Ещё", "callback_data": f"p|{key}|{mode}|{token}|{end}|{flags}"})
    buttons.append({"text": "🙈 Скрыть", "callback_data": f"hide|{token}"})
    buttons.append({"text": "📥 CSV", "callback_data": f"e|{token}"})
    buttons.append({"text": "🔄 Меню", "callback_data": "menu", "style": "primary"})
    pager = tg("sendMessage", chat_id=chat_id, text=f"Показано {offset + 1}–{end} из {len(items)}",
               reply_markup={"inline_keyboard": [buttons]})
    if pager:
        remember(chat_id, "pager", pager["message_id"])  # старый счётчик страниц удалится


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
    lang_btns = [{"text": ("✅ " if code == ctx["lang"] else "") + label, "callback_data": f"t|L|{code}", "style": "primary"}
                 for code, label in LANGS]
    return {"inline_keyboard": [
        [{"text": "📱 Директ / WhatsApp", "callback_data": "t|c|dm", "style": "primary"},
         {"text": "📞 Звонок", "callback_data": "t|c|call", "style": "primary"}],
        [{"text": "✉️ Email", "callback_data": "t|c|em", "style": "primary"},
         {"text": "🔁 Follow-up", "callback_data": "t|c|fu", "style": "primary"}],
        [{"text": "🛡 Возражения", "callback_data": "t|x", "style": "success"},
         {"text": "📋 План сделки", "callback_data": "t|p", "style": "success"}],
        [{"text": "🤝 Закрыть сделку", "callback_data": "t|z", "style": "success"}],
        lang_btns[:3],
        lang_btns[3:],
        [{"text": "❌ Закрыть", "callback_data": "del", "style": "danger"}],
    ]}


def panel_text(ctx):
    return (header(ctx) + "Выбери, что нужно. Язык текстов меняется внизу — "
            "пиши клиенту на том языке, на котором он говорит." + settings_warning())


def back_markup(extra=None):
    row = []
    if extra:
        row.append(extra)
    row.append({"text": "⬅️ Назад", "callback_data": "t|b", "style": "primary"})
    row.append({"text": "❌ Закрыть", "callback_data": "del", "style": "danger"})
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
        panel = tg("sendMessage", chat_id=chat_id, text=panel_text(ctx), parse_mode="HTML",
                   reply_markup=panel_markup(ctx), reply_to_message_id=cb["message"]["message_id"])
        if panel:
            remember(chat_id, "panel", panel["message_id"])  # прошлая панель удалится
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
        rows.append([{"text": "⬅️ Назад", "callback_data": "t|b", "style": "primary"},
                     {"text": "❌ Закрыть", "callback_data": "del", "style": "danger"}])
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
    elif act == "z":  # продающий блок: как довести клиента до оплаты
        edit(cb, header(ctx) + T[ctx["lang"]]["close_deal"].format(**vars_for(ctx)), back_markup())


HELP_TEXT = ("👋 <b>Бот для поиска клиентов</b>\n\n"
             "Ищет на карте бизнесы без сайта и со слабым сайтом, оценивает сайты и даёт готовые тексты "
             "для директа, звонка и email на 6 языках (RU, EN, FI, ET, SV, DE). Ещё подсказывает, как отвечать на "
             "возражения и вести клиента до сделки.\n\n"
             "/start — меню\n/tips — советы по продажам\n/me — твои данные для текстов\n"
             "/stats — база клиентов и напоминания\n/history — последние поиски\n/funnel — воронка по статусам\n/fav — избранное\n\n"
             "Под карточкой: 🖼 скриншот сайта, 🚀 скорость от Google, 📥 CSV-выгрузка.\n🙈 Скрыть / 📂 Показать снова — управлять результатами.\nВ скриптах: 🤝 Закрыть сделку — как довести клиента до оплаты.\n\nПоехали 👇")

if MINIAPP_URL:
    HELP_TEXT += "\n\n🚀 Мини-приложение (кнопка в меню) — тот же поиск, но наглядно."

CRM_HINT = ("📒 <b>База клиентов не подключена</b>\n\n"
            "Чтобы отмечать «✅ Написал / 🤝 Сделка / ❌ Отказ», вести избранное и получать "
            "напоминания о follow-up:\n"
            "1. Зарегистрируйся на upstash.com (бесплатно) и создай Redis-базу.\n"
            "2. В Vercel → Environment Variables добавь:\n"
            "UPSTASH_REDIS_REST_URL, UPSTASH_REDIS_REST_TOKEN (из панели Upstash)\n"
            "MY_CHAT_ID — твой chat id (узнать: @userinfobot)\n"
            "3. Redeploy. Кнопки появятся под карточками сами.")


CLOSE_KB = {"inline_keyboard": [[{"text": "🔄 Меню", "callback_data": "menu", "style": "primary"},
                                 {"text": "❌ Закрыть", "callback_data": "del", "style": "danger"}]]}


def send_stats(chat_id):
    if not CRM_ON:
        m = tg("sendMessage", chat_id=chat_id, text=CRM_HINT, parse_mode="HTML", reply_markup=CLOSE_KB)
    else:
        db = crm_all()
        now = int(time.time())
        cnt = {"contacted": 0, "deal": 0, "refused": 0}
        due, fav = [], 0
        for r in db.values():
            if r.get("status") in cnt:
                cnt[r["status"]] += 1
            if r.get("fav"):
                fav += 1
            if r.get("next") and r["next"] <= now + 86400:
                due.append(r["name"])
        text = (f"📒 <b>Твоя база клиентов</b>\n\n"
                f"✍️ Написали: <b>{cnt['contacted']}</b>\n"
                f"🤝 Сделки: <b>{cnt['deal']}</b>\n"
                f"❌ Отказы: <b>{cnt['refused']}</b>\n"
                f"⭐ Избранное: <b>{fav}</b>\n\n")
        if due:
            text += "🔁 <b>Пора напомнить о себе:</b>\n" + "\n".join("• " + esc(n) for n in due[:15])
        else:
            text += "🔁 Напоминаний на ближайшие сутки нет."
        m = tg("sendMessage", chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=CLOSE_KB)
    if m:
        remember(chat_id, "stats", m["message_id"])


def send_fav(chat_id):
    if not CRM_ON:
        m = tg("sendMessage", chat_id=chat_id, text=CRM_HINT, parse_mode="HTML", reply_markup=CLOSE_KB)
    else:
        favs = [r for r in crm_all().values() if r.get("fav")]
        if not favs:
            text = "⭐ Избранное пусто. Нажимай «⭐ В избранное» под карточкой клиента."
        else:
            text = "⭐ <b>Избранные клиенты</b>\n\n"
            for r in favs[:30]:
                line = f"• <b>{esc(r['name'])}</b>"
                if r.get("site"):
                    line += f" — {esc(r['site'])}"
                if r.get("phone"):
                    line += f" 📞 {esc(r['phone'])}"
                mark = CRM_LABEL.get(r.get("status"))
                if mark:
                    line += f" ({mark})"
                text += line + "\n"
        m = tg("sendMessage", chat_id=chat_id, text=text, parse_mode="HTML",
               disable_web_page_preview=True, reply_markup=CLOSE_KB)
    if m:
        remember(chat_id, "fav", m["message_id"])


def _ago(ts):
    diff = max(0, int(time.time()) - int(ts or 0))
    if diff < 3600:
        return "только что" if diff < 120 else f"{diff // 60} мин назад"
    if diff < 86400:
        return f"{diff // 3600} ч назад"
    return f"{diff // 86400} дн назад"


def send_history(chat_id):
    rows = ledger.history_list(10)["items"]
    if not rows:
        text = "🕘 Истории поиска пока нет. Найди клиентов — и я запомню запрос."
    else:
        text = "🕘 <b>Последние поиски</b>\n\n"
        for r in rows:
            text += (f"• {esc(r['city'])} · {esc(r['label'])} — {r['count']} лидов, "
                     f"новых: {r['new_count']} ({_ago(r['ts'])})\n")
    buttons = []
    for r in rows[:5]:
        buttons.append([{"text": f"🔎 {r['city'][:18]}",
                         "callback_data": f"h|{r['q']}"}])
    buttons.append([{"text": "❌ Закрыть", "callback_data": "del", "style": "danger"}])
    m = tg("sendMessage", chat_id=chat_id, text=text, parse_mode="HTML",
           reply_markup={"inline_keyboard": buttons})
    if m:
        remember(chat_id, "stats", m["message_id"])


def send_funnel(chat_id):
    d = ledger.funnel(limit=20)
    c = d["counts"]
    lines = [f"{lab.split(' ', 1)[-1]}: <b>{c[key]}</b>" for key, lab in ledger.STATUSES]
    text = "📊 <b>Воронка клиентов</b>\n\n" + "\n".join(lines)
    if d["items"]:
        text += "\n\n<b>Последние:</b>\n"
        for r in d["items"][:15]:
            lab = dict(ledger.STATUSES).get(r["status"], "🆕 Новый")
            text += f"• {lab} — {esc(r['name'] or 'без названия')}\n"
    else:
        text += "\n\nПока нет лидов в базе. Отмечай статусы в мини-приложении или под карточкой."
    m = tg("sendMessage", chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=CLOSE_KB)
    if m:
        remember(chat_id, "stats", m["message_id"])


# Защита от повторов: Telegram переотправляет апдейт, если бот отвечал слишком долго.
# Запоминаем обработанные update_id, чтобы не отвечать дважды/трижды.
_SEEN_UPDATES = {}


def handle_webapp_data(chat_id, raw, message_id=None):
    """Кнопка «Отправить в чат» из мини-приложения: открываем панель скриптов."""
    try:
        d = json.loads(raw)
    except Exception:
        return
    if not isinstance(d, dict):
        return
    keys, texts = [], []
    for x in (d.get("issues") or []):
        if isinstance(x, (list, tuple)):
            if x:
                keys.append(str(x[0]))
            if len(x) > 1:
                texts.append(str(x[1]))
        elif isinstance(x, str):
            keys.append(x)
    ctx = {
        "name": str(d.get("name") or "Клиент")[:80],
        "kind": "weak" if d.get("kind") == "weak" else "nosite",
        "domain": re.sub(r"^https?://", "", str(d.get("site") or "")).rstrip("/"),
        "issues": ", ".join(texts),
        "keys": keys,
        "lang": d.get("lang") if d.get("lang") in T else DEFAULT_LANG,
    }
    if message_id:
        delete_msg(chat_id, message_id)  # системное сообщение мини-приложения не нужно
    m = tg("sendMessage", chat_id=chat_id, text=panel_text(ctx), parse_mode="HTML",
           reply_markup=panel_markup(ctx), disable_web_page_preview=True)
    if m:
        remember(chat_id, "panel", m["message_id"])


def handle(update):
    uid = update.get("update_id")
    if uid is not None:
        if uid in _SEEN_UPDATES:
            return
        _SEEN_UPDATES[uid] = 1
        if len(_SEEN_UPDATES) > 500:
            for k in list(_SEEN_UPDATES)[:250]:
                _SEEN_UPDATES.pop(k, None)
    cb = update.get("callback_query")
    if cb:
        tg("answerCallbackQuery", callback_query_id=cb["id"])
        chat_id = cb["message"]["chat"]["id"]
        data = cb.get("data", "")
        parts = data.split("|")
        mid = cb["message"]["message_id"]
        if data.startswith("t|"):
            handle_tools(cb)
        elif parts[0] == "del":  # «❌ Закрыть» — убираем сообщение и память о нём
            delete_msg(chat_id, mid)
            st = _CHAT.setdefault(chat_id, {})
            for k, v in list(st.items()):
                if v == mid:
                    st.pop(k)
        elif parts[0] == "back_menu":  # «⬅️ Назад» с экрана режимов — в меню, на месте
            _CHAT.setdefault(chat_id, {}).pop("pending", None)
            if not edit_msg(chat_id, mid, MENU_TEXT, menu_markup()):
                send_menu(chat_id)
            else:
                remember(chat_id, "menu", mid)
        elif parts[0] == "hide" and len(parts) == 2:  # «🙈 Скрыть» — убираем карточки
            hit = cache_load(parts[1])
            clear_cards(chat_id)
            n = len(hit["res"][0]) if hit else 0
            m = tg("sendMessage", chat_id=chat_id,
                   text=f"🙈 Результаты скрыты ({n} найдено). Их можно вернуть в любой момент.",
                   reply_markup={"inline_keyboard": [
                       [{"text": "📂 Показать снова", "callback_data": f"show|{parts[1]}|0"}],
                       [{"text": "🔄 Меню", "callback_data": "menu", "style": "primary"},
                        {"text": "❌ Закрыть", "callback_data": "del", "style": "danger"}]]})
            if m:
                remember(chat_id, "hidden", m["message_id"])
        elif parts[0] == "show" and len(parts) == 3:  # «📂 Показать снова» — из кэша, без поиска
            hit = cache_load(parts[1])
            if not hit:
                tg("sendMessage", chat_id=chat_id, text="Поиск устарел — запусти новый через меню.")
                return
            st = _CHAT.setdefault(chat_id, {})
            if st.get("hidden"):
                delete_msg(chat_id, st.pop("hidden"))
            try:
                offset = int(parts[2])
            except ValueError:
                offset = 0
            items, n_no, n_weak, n_with = hit["res"]
            sm = tg("sendMessage", chat_id=chat_id, parse_mode="HTML",
                    text=(f"📊 <b>{esc(hit['city'])}</b>, {NICHES[hit['key']][0]}\n"
                          f"🚫 без сайта: <b>{n_no}</b>\n🐌 слабых сайтов: <b>{n_weak}</b>"
                          + potential_text(n_no)))
            if sm:
                remember(chat_id, "summary", sm["message_id"])
            run_search(chat_id, hit["key"], hit["mode"], hit["city"], offset, token=parts[1])
        elif parts[0] == "h" and len(parts) > 1:
            q = parts[1]
            row = next((r for r in ledger.history() if r.get("q") == q), None)
            if not row:
                tg("sendMessage", chat_id=chat_id, text="Поиск не найден. Запусти его заново из меню.")
                return
            key = row.get("niche_key") or "barber"
            if key not in NICHES:
                key = "barber"
            delete_msg(chat_id, mid)
            run_search(chat_id, key, row.get("mode") or "n", row.get("city") or "",
                       0, flags=row.get("flags") or "")
        elif parts[0] == "menu":
            # превращаем сообщение со счётчиком страниц в меню — без нового сообщения
            st = _CHAT.setdefault(chat_id, {})
            st.pop("pending", None)
            if st.get("pager") == mid:
                st.pop("pager")
            if st.get("hidden") == mid:
                st.pop("hidden")
            if edit_msg(chat_id, mid, MENU_TEXT, menu_markup()):
                remember(chat_id, "menu", mid)
            else:
                send_menu(chat_id)
        elif parts[0] == "tips":
            send_tips(chat_id)
        elif parts[0] == "about":
            send_about(chat_id)
        elif parts[0] == "settings":
            send_settings(chat_id)
        elif parts[0] == "funnel_info":
            if 'send_funnel' in globals():
                send_funnel(chat_id)
            else:
                tg("sendMessage", chat_id=chat_id, text="Откройте воронку в мини-приложении: 📊", reply_markup=CLOSE_KB)
        elif parts[0] == "n" and parts[1] in NICHES:
            # выбор режима редактирует меню на месте
            _CHAT.setdefault(chat_id, {}).pop("pending", None)
            if not edit_msg(chat_id, mid, modes_text(parts[1]), modes_markup(parts[1])):
                tg("sendMessage", chat_id=chat_id, text=modes_text(parts[1]),
                   reply_markup=modes_markup(parts[1]))
        elif parts[0] == "f" and parts[1] in NICHES:
            # переключили фильтр — перерисовываем то же сообщение
            flags = parts[2] if len(parts) > 2 else ""
            edit_msg(chat_id, mid, modes_text(parts[1], flags), modes_markup(parts[1], flags))
        elif parts[0] == "m" and parts[1] in NICHES and parts[2] in MODES:
            delete_msg(chat_id, mid)  # выбор режима больше не нужен
            send_prompt(chat_id, parts[1], parts[2], parts[3] if len(parts) > 3 else "")
        elif parts[0] == "p" and len(parts) == 6 and parts[1] in NICHES and parts[2] in MODES:
            try:
                offset = int(parts[4])
            except ValueError:
                return
            hit = cache_load(parts[3])
            if hit:
                run_search(chat_id, parts[1], parts[2], hit["city"], offset, token=parts[3])
            else:
                # кэш остыл (прошло >30 минут или перезапуск) — просто спросим город заново
                delete_msg(chat_id, mid)
                send_prompt(chat_id, parts[1], parts[2], parts[5])
        elif parts[0] == "e" and len(parts) == 2:
            export_csv(chat_id, parts[1])
        elif parts[0] == "v" and len(parts) == 4:
            hit = cache_load(parts[1])
            try:
                it = hit["res"][0][int(parts[2])] if hit else None
            except (ValueError, IndexError):
                it = None
            if not it:
                tg("sendMessage", chat_id=chat_id, text="Поиск устарел — запусти новый.")
                return
            if parts[3] == "shot":
                ok = tg("sendPhoto", chat_id=chat_id,
                        photo="https://image.thum.io/get/width/800/noanimate/" + it["site"],
                        caption=f"🖼 {it['name']} — {it['site']}")
                if not ok:
                    tg("sendMessage", chat_id=chat_id,
                       text="⚠️ Скриншот не получился (сайт закрыт от ботов). Открой его кнопкой «Открыть сайт».")
            elif parts[3] == "ps":
                send_pagespeed(chat_id, it)
        elif parts[0] == "c" and len(parts) == 4 and CRM_ON:
            hit = cache_load(parts[1])
            try:
                it = hit["res"][0][int(parts[2])] if hit else None
            except (ValueError, IndexError):
                it = None
            if not it:
                tg("sendMessage", chat_id=chat_id, text="Поиск устарел — запусти новый.")
                return
            if parts[3] == "fav":
                rec = crm_toggle_fav(it)
                mark = "⭐ добавлено в избранное" if rec.get("fav") else "☆ убрано из избранного"
            elif parts[3] in CRM_LABEL:
                crm_set(it, parts[3])
                mark = CRM_LABEL[parts[3]]
                if parts[3] == "contacted":
                    mark += " · напомню через 3 дня"
            else:
                return
            text = re.sub(r"\n📌[^\n]*", "", cb["message"].get("text", "")) + "\n📌 " + mark
            tg("editMessageText", chat_id=chat_id, message_id=mid, text=text, parse_mode="HTML",
               reply_markup=cb["message"].get("reply_markup"), disable_web_page_preview=True)
        return

    msg = update.get("message")
    if not msg:
        return
    if msg.get("web_app_data"):  # данные из мини-приложения
        return handle_webapp_data(msg["chat"]["id"],
                                  msg["web_app_data"].get("data", ""),
                                  msg.get("message_id"))
    if "text" not in msg:
        return
    chat_id, text = msg["chat"]["id"], msg["text"].strip()

    if text.startswith("/"):
        delete_msg(chat_id, msg["message_id"])  # команды пользователя не засоряют чат

    if text.startswith("/tips"):
        return send_tips(chat_id)
    if text.startswith("/stats"):
        return send_stats(chat_id)
    if text.startswith("/fav"):
        return send_fav(chat_id)
    if text.startswith("/history"):
        return send_history(chat_id)
    if text.startswith("/funnel"):
        return send_funnel(chat_id)
    if text.startswith("/me"):
        m = tg("sendMessage", chat_id=chat_id, parse_mode="HTML",
               text=("⚙️ <b>Твои данные в текстах</b>\n"
                     f"Имя: {esc(ME)}\nКонтакт: {esc(CONTACT)}\nПортфолио: {esc(PORTFOLIO)}\n"
                     f"Цена: {esc(PRICE or '— не указана')}\nЯзык по умолчанию: {DEFAULT_LANG.upper()}\n\n"
                     "Меняются в Vercel: Settings → Environment Variables (MY_NAME, MY_CONTACT, "
                     "MY_PORTFOLIO, MY_PRICE, DEFAULT_LANG), потом Redeploy."),
               reply_markup=CLOSE_KB)
        if m:
            remember(chat_id, "me", m["message_id"])
        return
    if text.startswith("/help"):
        m = tg("sendMessage", chat_id=chat_id, text=HELP_TEXT, parse_mode="HTML", reply_markup=CLOSE_KB)
        if m:
            remember(chat_id, "help", m["message_id"])
        return
    if text.startswith("/start"):
        m = tg("sendMessage", chat_id=chat_id, text=HELP_TEXT, parse_mode="HTML", reply_markup=CLOSE_KB)
        if m:
            remember(chat_id, "help", m["message_id"])
        return send_menu(chat_id)

    reply = msg.get("reply_to_message") or {}
    reply_text = reply.get("text", "")
    st = _CHAT.setdefault(chat_id, {})
    if reply_text.startswith("🔎 Ниша:") and not text.startswith("/"):
        key = next((k for k, (lbl, _) in NICHES.items() if lbl in reply_text), None)
        mode = next((m for m, lbl in MODES.items() if lbl in reply_text), None)
        flags = "".join(ch for ch, lbl in (("p", "только с телефоном"), ("e", "только с email"),
                                           ("c", "без сетей")) if lbl in reply_text)
        if key and mode:
            # после поиска удаляем сообщение с городом и подсказку "напиши город"
            st.pop("pending", None)
            return run_search(chat_id, key, mode, text, 0, flags=flags,
                              cleanup=(msg["message_id"], reply.get("message_id")))
    elif st.get("pending") and not text.startswith("/"):
        # город написали просто текстом, без reply — тоже работает
        key, mode, flags = st.pop("pending")
        return run_search(chat_id, key, mode, text, 0, flags=flags,
                          cleanup=(msg["message_id"], st.get("flow")))
    send_menu(chat_id)


def _respond(start_response, status, body):
    start_response(status, [("Content-Type", "text/plain; charset=utf-8")])
    return [body]


def app(environ, start_response):
    """WSGI-приложение: Vercel вызывает его на каждый запрос от Telegram."""
    if environ.get("REQUEST_METHOD") == "POST":
        if SECRET and environ.get("HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN") != SECRET:
            return _respond(start_response, "403 Forbidden", b"forbidden")
        try:
            length = int(environ.get("CONTENT_LENGTH") or 0)
            handle(json.loads(environ["wsgi.input"].read(length)))
        except Exception as e:
            print("error", e)
        return _respond(start_response, "200 OK", b"ok")
    return _respond(start_response, "200 OK", b"bot is running")
