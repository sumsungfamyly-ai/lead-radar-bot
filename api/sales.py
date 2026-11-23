# -*- coding: utf-8 -*-
"""Продающие скрипты (6 языков).

Логика каждого текста: конкретная боль клиента → цена бездействия →
результат в цифрах/сроке → ОДИН чёткий шаг. Никаких «если интересно, напишите».

Доступные переменные: {biz} {me} {domain} {problem} {pricep} {portfolio} {contact}
"""

SCRIPTS = {
 "ru": {
  "and": " и ",
  "prob": {
   "mobile": "сайт неудобен на телефоне — клиент уходит, не дождавшись",
   "https": "нет HTTPS — браузер предупреждает клиента о риске",
   "ssl": "ошибка сертификата — клиент видит предупреждение «небезопасно»",
   "stub": "сайт выглядит недоделанным — нет доверия к бизнесу",
   "old": "сайт выглядит устаревшим — клиент думает, что вы не работаете",
   "slow": "сайт медленно открывается — часть клиентов уходит до загрузки",
   "dead": "сайт не открывается — заявки просто теряются",
   "social": "вместо сайта только соцсеть — вас не найти в Google",
   "seo": "нет описания для поисковиков — вы не попадаете в выдачу",
   "generic": "сайт упускает клиентов, которых можно было бы получить",
  },
  "dm_nosite": [
   "Здравствуйте! Меня зовут {me}. Нашёл «{biz}» на карте — хорошее место, но без сайта вас почти не видно: клиент ищет услугу рядом на телефоне и выбирает из первых трёх ссылок. Сайт с телефоном, картой и кнопкой заявки закрывает эту задачу за 5–7 дней{pricep}. Примеры: {portfolio}. Удобно завтра 15 минут обсудить, что поставить на первую страницу?",
   "Здравствуйте! «{biz}» есть на карте, но нет сайта — поэтому часть клиентов выбирает конкурентов. Делаю сайты под местный бизнес{pricep}. Покажу 2 примера и срок: сегодня или завтра удобно глянуть?",
  ],
  "dm_weak": [
   "Здравствуйте! Меня зовут {me}. Зашёл на {domain}: {problem}. Из-за этого клиент часто уходит к конкуренту ещё до звонка. Исправляется за 2–3 дня, без смены домена. Пришлю разбор «до/после» на одной странице{pricep}. Примеры: {portfolio}. Когда удобно 10 минут посмотреть?",
   "Здравствуйте! Проверил сайт {domain}: {problem}. Это стоит вам части заявок. Покажу, как исправить за пару дней, на конкретном примере{pricep}. Сегодня или завтра удобно?",
  ],
  "call": {
   "open": "Здравствуйте! Меня зовут {me}. Понимаю, время дорого — задам один вопрос: откуда сейчас приходят клиенты?",
   "hook_nosite": "Нашёл вас на карте, но не нашёл сайта. Когда человек ищет вашу услугу рядом, он видит конкурентов, а не вас. Сколько заявок в месяц приходит с интернета?",
   "hook_weak": "На вашем сайте {domain}: {problem}. Из-за этого вы теряете часть звонков. Сколько заявок приходит сейчас — и сколько хотите?",
   "offer": "За 5–7 дней сделаю сайт под вашу нишу{pricep}: телефон, карта, форма заявки, быстрая загрузка. Не «красивая картинка», а инструмент, который приносит заявки.",
   "close": "Без долгих разговоров: пришлю 2 примера и точный срок. Куда — WhatsApp или почта? Если не подойдёт, честно скажу сразу.",
   "secretary": "Мне нужно 2 минуты с тем, кто решает по сайту. Скажите, когда удобнее позвонить — до обеда или после?",
   "mail": "Отправил. Подскажите, когда заглянуть — завтра днём?",
  },
  "em_subj_nosite": "«{biz}»: заявки из Google вместо пустого экрана",
  "em_subj_weak": "{domain}: что мешает вам получать заявки",
  "em_nosite": "Здравствуйте!\n\nМеня зовут {me}. Нашёл «{biz}» на карте. Услугу ищут на телефоне «рядом с нами» — и выбирают тех, у кого есть сайт с телефоном и формой заявки. Без сайта вы отдаёте этих клиентов конкурентам.\n\nЧто сделаю за 5–7 дней{pricep}:\n• страница с вашими услугами, ценами и телефоном;\n• карта и кнопка звонка с телефона;\n• форма заявки, которая приходит вам в Telegram или на почту.\n\nПримеры работ: {portfolio}\n\nОтветьте одним словом «да» — пришлю 2 примера и точный срок.\n\n{me}\n{contact}",
  "em_weak": "Здравствуйте!\n\nМеня зовут {me}. Проверил сайт «{biz}» ({domain}). Главная проблема: {problem}. Каждый день это стоит вам части заявок.\n\nЧто исправлю за 2–3 дня{pricep}:\n• уберу преграды на телефоне и ускорю загрузку;\n• добавлю понятные кнопки «позвонить» и «заказать»;\n• подключу форму заявки и базовое SEO.\n\nПримеры работ: {portfolio}\n\nОтветьте «да» — пришлю разбор «до/после» на одной странице.\n\n{me}\n{contact}",
  "fu": [
   "Здравствуйте! Отправил вам примеры и срок по сайту для «{biz}». Если решение затянулось — не страшно: скажите, что именно нужно уточнить, и я отвечу одним сообщением.",
   "Последнее письмо. Если сейчас неактуально — удалю вас из списка и не буду беспокоить. Если хотите заявки из Google вместо потерь — ответьте «да», пришлю план на 1 страницу.",
  ],
  "obj": {
   "price": "Понимаю вопрос денег. Давайте посчитаем: сколько стоит один новый клиент для «{biz}»? Если сайт приводит хотя бы одного в месяц, он окупается. Могу начать с мини-версии, а затем расширить — без полной оплаты сразу.",
   "noneed": "Хороший вопрос. Откуда у вас сейчас клиенты? Если в основном сарафан и соцсети — вы отдаёте инициативу конкурентам. Покажу за 2 минуты, что по вашей нише ищут в Google прямо сейчас. Решение останется за вами.",
   "think": "Конечно. Что именно нужно обдумать — цена, срок или объём? Назовите, и я пришлю один ответ. Чтобы не терять время, вернёмся в среду в 11:00 — удобно?",
   "have": "Отлично, значит тема живая. Не буду критиковать чужую работу: пришлю независимый взгляд на текущий сайт — 3 конкретных пункта. Если совпадёт, обсудим; если нет, просто останемся на связи.",
   "social": "Соцсети дают внимание, но когда клиент готов купить, он ищет в Google и заходит на сайт — это другой этап. Сайт не заменяет соцсети, а ловит тех, кто уже готов купить. Покажу на 2 примерах вашей ниши.",
   "fine": "Рад за вас. Тогда давайте проверим факты: откроем сайт на телефоне и замерим скорость. Если всё отлично — скажу честно и предложу то, что действительно пригодится: Google-карточка или SEO.",
  },
  "close_deal": "🤝 <b>Как довести до оплаты</b>\n\n<b>1. Три пакета, средний — основной.</b> Мини: быстрая страница с телефоном и формой. Стандарт: сайт под нишу + заявки + базовое SEO. Про: сайт + контент + запуск рекламы. Озвучьте цену среднего первым — остальные вокруг него.\n\n<b>2. Пробный вопрос.</b> «Если сделаем за 5 дней и первые заявки пойдут — начинаем в понедельник?» Это не давление, а шаг к решению.\n\n<b>3. Снимите страх.</b> Предоплата 30–50%, оставшееся после сдачи. Договор на 1 страницу, срок и объём прописаны. Покажите 2 примера и отзыв.\n\n<b>4. Заберите следующий шаг сразу.</b> «Прислать счёт или сначала уточнить текст на главной?» Любой ответ — это движение.\n\n<b>5. Если молчат.</b> Одно напоминание через 2–3 дня с конкретикой: срок, цена, что входит. Потом остановитесь.\n\n<i>Считайте заявки, а не «красоту»: цель сайта — телефон и форма, а не красивый скриншот.</i>",
 },
 "en": {
  "and": " and ",
  "prob": {
   "mobile": "the site is hard to use on a phone — customers leave before it loads",
   "https": "no HTTPS — the browser warns customers about risk",
   "ssl": "certificate error — customers see a «not secure» warning",
   "stub": "the site looks unfinished — it destroys trust",
   "old": "the site looks outdated — customers think the business is closed",
   "slow": "the site loads slowly — people leave before seeing your offer",
   "dead": "the site doesn't open — enquiries are simply lost",
   "social": "only a social page — you can't be found on Google",
   "seo": "no search description — you don't appear in results",
   "generic": "the site is losing enquiries you could be getting",
  },
  "dm_nosite": [
   "Hi, this is {me}. I found «{biz}» on the map — great location, but almost invisible online: people search for your service nearby on their phone and pick one of the first three results. A site with your phone number, map and enquiry button solves this in 5–7 days{pricep}. Examples: {portfolio}. Can we spend 15 minutes tomorrow deciding what goes on the first screen?",
   "Hi! «{biz}» is on the map but has no website, so part of your customers choose competitors. I build sites for local businesses{pricep}. I'll show you 2 examples and a deadline — today or tomorrow?",
  ],
  "dm_weak": [
   "Hi, this is {me}. I checked {domain}: {problem}. Because of that, customers often call a competitor instead. It takes 2–3 days to fix, no domain change. I'll send a one-page before/after breakdown{pricep}. Examples: {portfolio}. When can you take 10 minutes to look?",
   "Hi! I checked {domain}: {problem}. It's costing you enquiries. I'll show how to fix it in a couple of days on a real example{pricep}. Today or tomorrow?",
  ],
  "call": {
   "open": "Hello, this is {me}. I know your time is valuable — one question: where do your customers come from right now?",
   "hook_nosite": "I found you on the map but no website. When someone searches for your service nearby, they see competitors instead of you. How many enquiries do you get from the internet per month?",
   "hook_weak": "Your site {domain}: {problem}. That's costing you calls. How many enquiries do you get now — and how many would you like?",
   "offer": "In 5–7 days I'll build a site for your niche{pricep}: phone, map, enquiry form, fast loading. Not a pretty picture — a tool that brings enquiries.",
   "close": "Let's keep it short: I'll send 2 examples and an exact deadline. WhatsApp or email? If it's not a fit, I'll tell you honestly.",
   "secretary": "I need 2 minutes with whoever decides on the website. When is a good time to call — before or after lunch?",
   "mail": "Sent. When should I check back — tomorrow afternoon?",
  },
  "em_subj_nosite": "«{biz}»: get enquiries from Google instead of nothing",
  "em_subj_weak": "{domain}: what's costing you enquiries",
  "em_nosite": "Hello!\n\nThis is {me}. I found «{biz}» on the map. People look for services on their phone — «near me» — and choose companies with a site, phone number and enquiry form. Without one, you hand those customers to competitors.\n\nWhat I'll deliver in 5–7 days{pricep}:\n• a page with your services, prices and phone;\n• map and tap-to-call button for mobiles;\n• an enquiry form delivered to your Telegram or email.\n\nExamples: {portfolio}\n\nReply with just «yes» and I'll send 2 examples and an exact deadline.\n\n{me}\n{contact}",
  "em_weak": "Hello!\n\nThis is {me}. I checked the site of «{biz}» ({domain}). Main issue: {problem}. Every day it costs you part of your enquiries.\n\nWhat I'll fix in 2–3 days{pricep}:\n• remove mobile blockers and speed it up;\n• add clear «call» and «order» buttons;\n• connect an enquiry form and basic SEO.\n\nExamples: {portfolio}\n\nReply «yes» and I'll send a one-page before/after breakdown.\n\n{me}\n{contact}",
  "fu": [
   "Hi! I sent you examples and a timeline for the site for «{biz}». If the decision is stuck, tell me exactly what needs clarifying — one message is enough.",
   "Last email. If the timing is wrong, I'll remove you from my list and won't bother you. If you want enquiries from Google instead of lost customers, reply «yes» and I'll send a one-page plan.",
  ],
  "obj": {
   "price": "Fair question. Let's calculate: what is one new customer worth to «{biz}»? If the site brings just one per month, it pays for itself. We can start with a lean version and expand later — no full payment upfront.",
   "noneed": "Good question. Where do your customers come from now? If it's mostly word of mouth and social, you're leaving Google to competitors. Let me show you in 2 minutes what people are searching for in your niche. The decision is yours.",
   "think": "Sure. What exactly needs thinking over — price, timing or scope? Tell me and I'll answer in one message. Let's reconnect on Wednesday at 11 — works?",
   "have": "Great, so the topic is live. I won't criticise anyone's work: I'll send an independent look at your current site — 3 concrete points. If it matches, we talk; if not, we stay in touch.",
   "social": "Social media creates attention, but when someone is ready to buy they search Google and open a website — a different stage. A site doesn't replace social, it catches people who are already warm. I'll show you 2 examples in your niche.",
   "fine": "Glad to hear it. Then let's check the facts: open it on a phone and measure loading. If it's genuinely great, I'll say so and suggest what actually helps — Google Business Profile or SEO.",
  },
  "close_deal": "🤝 <b>How to close the deal</b>\n\n<b>1. Three packages, middle one is the anchor.</b> Basic: fast page with phone and form. Standard: niche site + enquiries + basic SEO. Pro: site + content + ads. Quote the middle price first — the others are judged around it.\n\n<b>2. Trial close.</b> «If we deliver in 5 days and enquiries start coming — shall we start on Monday?» Not pressure, just the next step.\n\n<b>3. Remove the risk.</b> 30–50% upfront, rest on delivery. One-page contract with scope and deadline. Show 2 examples and a review.\n\n<b>4. Take the next step immediately.</b> «Shall I send the invoice or confirm the homepage copy first?» Any answer is progress.\n\n<b>5. If they go quiet.</b> One reminder in 2–3 days with specifics: deadline, price, what's included. Then stop.\n\n<i>Measure enquiries, not beauty: the goal is phone calls and forms, not a pretty screenshot.</i>",
 },
 "fi": {
  "and": " ja ",
  "prob": {
   "mobile": "sivusto ei toimi puhelimella — asiakas poistuu ennen kuin se latautuu",
   "https": "HTTPS puuttuu — selain varoittaa asiakasta riskistä",
   "ssl": "varmentovirhe — asiakas näkee «ei turvallinen» -varoituksen",
   "stub": "sivusto näyttää keskeneräiseltä — luottamus katoaa",
   "old": "sivusto näyttää vanhentuneelta — asiakas luulee yrityksen lopettaneen",
   "slow": "sivusto latautuu hitaasti — osa asiakkaista lähtee ennen tarjousta",
   "dead": "sivusto ei avaudu — yhteydenotot menetetään",
   "social": "vain some-sivu — teitä ei löydy Googleista",
   "seo": "ei hakukonekuvausta — ette näy hakuissa",
   "generic": "sivusto menettää asiakkaita, jotka voisitte saada",
  },
  "dm_nosite": [
   "Hei! Olen {me}. Löysin yrityksenne «{biz}» kartalta — hyvä sijainti, mutta verkossa teitä ei lähes näy: asiakas hakee palvelua puhelimella läheltään ja valitsee yhden kolmesta ensimmäisestä tuloksesta. Sivusto, jossa on puhelinnumero, kartta ja yhteydenottolomake, ratkaisee tämän 5–7 päivässä{pricep}. Esimerkkejä: {portfolio}. Sopiisko huomenna 15 minuuttia käydä läpi, mitä etusivulle laitetaan?",
   "Hei! «{biz}» on kartalla, mutta ei verkkosivuja — osa asiakkaista valitsee kilpailijan. Teen sivustoja paikallisille yrityksille{pricep}. Näytän 2 esimerkkiä ja aikataulun — tänään vai huomenna?",
  ],
  "dm_weak": [
   "Hei! Olen {me}. Kävin sivustollanne {domain}: {problem}. Sen takia asiakas soittaa usein kilpailijalle. Korjaus kestää 2–3 päivää, domainia ei vaihdeta. Lähetän yhden sivun ennen/jälkeen -vertailun{pricep}. Esimerkkejä: {portfolio}. Milloin voitte käyttää 10 minuuttia?",
   "Hei! Tarkastin sivuston {domain}: {problem}. Se maksaa teille yhteydenottoja. Näytän, miten korjataan parissa päivässä, oikealla esimerkillä{pricep}. Tänään vai huomenna?",
  ],
  "call": {
   "open": "Hei! Olen {me}. Ymmärrän, että aika on kortilla — yksi kysymys: mistä asiakkaat tulevat nyt?",
   "hook_nosite": "Löysin teidät kartalta, mutta en verkkosivuja. Kun asiakas hakee palveluanne läheltään, hän näkee kilpailijat. Kuinka monta yhteydenottoa kuukaudessa tulee netistä?",
   "hook_weak": "Sivustollanne {domain}: {problem}. Se maksaa teille puheluita. Montako yhteydenottoa saatte nyt — ja montako haluaisitte?",
   "offer": "Teen 5–7 päivässä sivuston alaanne{pricep}: puhelin, kartta, yhteydenottolomake, nopea lataus. En kaunista kuvaa vaan työkalun, joka tuo yhteydenottoja.",
   "close": "Pidetään tämä lyhyenä: lähetän 2 esimerkkiä ja tarkan aikataulun. WhatsAppiin vai sähköpostiin? Jos tämä ei sovi, sanon sen suoraan.",
   "secretary": "Tarvitsen 2 minuuttia siltä, joka päättää verkkosivuista. Milloin voin soittaa — ennen lounasta vai sen jälkeen?",
   "mail": "Lähetin. Milloin voin tarkistaa vastauksen — huomenna iltapäivällä?",
  },
  "em_subj_nosite": "«{biz}»: yhteydenottoja Googleista tyhjän sijaan",
  "em_subj_weak": "{domain}: mikä estää yhteydenottoja",
  "em_nosite": "Hei!\n\nOlen {me}. Löysin yrityksenne «{biz}» kartalta. Asiakkaat hakevat palveluita puhelimella «lähelläni» ja valitsevat yritykset, joilla on sivusto, puhelin ja lomake. Ilman niitä annatte asiakkaat kilpailijoille.\n\nTeen 5–7 päivässä{pricep}:\n• sivu palveluineen, hintoineen ja puhelinnumeroineen;\n• kartta ja soita-nappi puhelimessa;\n• yhteydenottolomake Telegramiin tai sähköpostiin.\n\nEsimerkkejä: {portfolio}\n\nVastaa yhdellä sanalla «kyllä» — lähetän 2 esimerkkiä ja tarkan aikataulun.\n\n{me}\n{contact}",
  "em_weak": "Hei!\n\nOlen {me}. Tarkastin yrityksenne «{biz}» sivuston ({domain}). Pääongelma: {problem}. Joka päivä se maksaa teille osan yhteydenotoista.\n\nKorjaan 2–3 päivässä{pricep}:\n• poistan puhelimen esteet ja nopeutan latausta;\n• lisään selkeät «soita» ja «tilaa» -napit;\n• yhdistän lomakkeen ja perus-SEO:n.\n\nEsimerkkejä: {portfolio}\n\nVastaa «kyllä» — lähetän yhden sivun ennen/jälkeen -vertailun.\n\n{me}\n{contact}",
  "fu": [
   "Hei! Lähetin teille esimerkit ja aikataulun «{biz}» sivustosta. Jos päätös jumittuu, kertokaa tarkasti, mitä täytyy selventää — yksi viesti riittää.",
   "Viimeinen viesti. Jos ajankohta ei sovi, poistan teidät listalta enkä häiritse enää. Jos haluatte yhteydenottoja Googleista menetysten sijaan, vastatkaa «kyllä» — lähetän yhden sivun suunnitelman.",
  ],
  "obj": {
   "price": "Ymmärrän hinnan. Lasketaan: mitä yksi uusi asiakas on arvoinen yrityksellesi «{biz}»? Jos sivusto tuo yhden kuukaudessa, se maksaa itsensä takaisin. Voitte aloittaa pienemmällä versiolla ja laajentaa myöhemmin — ei koko summaa heti.",
   "noneed": "Hyvä kysymys. Mistä asiakkaat tulevat nyt? Jos lähinnä suusta suuhun ja somesta, Google jää kilpailijoille. Näytän 2 minuutissa, mitä alallanne haetaan nyt. Päätös on teidän.",
   "think": "Totta kai. Mikä täytyy harkita — hinta, aikataulu vai laajuus? Kertokaa, vastaan yhdellä viestillä. Palataan keskiviikkona klo 11 — sopiiko?",
   "have": "Hienoa, aihe on siis ajankohtainen. En arvostele kenenkään työtä: lähetän riippumattoman katseen nykyiseen sivustoon — 3 konkreettista kohtaa. Jos osuu, puhutaan; jos ei, pysytään yhteydessä.",
   "social": "Some tuo huomiota, mutta kun asiakas on valmis ostamaan, hän hakee Googleista ja avaa sivuston — eri vaihe. Sivusto ei korvaa somea, se ottaa kiinni jo lämpimät asiakkaat. Näytän 2 esimerkkiä alaltanne.",
   "fine": "Iloista kuulla. Tarkistetaan faktat: avataan sivu puhelimella ja mitataan nopeus. Jos se on oikeasti hyvä, sanon sen suoraan ja ehdotan jotain muuta — Google-korttia tai SEO:ta.",
  },
  "close_deal": "🤝 <b>Näin viet kauppaan loppuun</b>\n\n<b>1. Kolme pakettia, keskimmäinen päävalintana.</b> Mini: nopea sivu puhelimella ja lomakkeella. Standard: alakohtainen sivusto + yhteydenotot + perus-SEO. Pro: sivusto + sisältö + mainonnan käynnistys. Mainitse keskimmäinen hinta ensin — muut arvioidaan sen ympärillä.\n\n<b>2. Kokeilukysymys.</b> «Jos toimitamme 5 päivässä ja yhteydenotot alkavat — aloitetaanko maanantaina?» Ei painostusta, vain seuraava askel.\n\n<b>3. Poista pelko.</b> 30–50 % ennakkoon, loppi toimituksen jälkeen. Yhden sivun sopimus, aikataulu ja sisältö kirjattuna. Näytä 2 esimerkkiä ja palaute.\n\n<b>4. Ota seuraava askel heti.</b> «Lähetänkö laskun vai vahvistammeko etusivun tekstit ensin?» Mikä tahansa vastaus on edistystä.\n\n<b>5. Jos hiljaisuus jatkuu.</b> Yksi muistutus 2–3 päivän kuluttua konkreettisesti: aikataulu, hinta, sisältö. Sitten pysähdy.\n\n<i>Mittaa yhteydenottoja, ei kauneutta: sivuston tavoite on puhelut ja lomakkeet, ei hieno kuva.</i>",
 },
 "et": {
  "and": " ja ",
  "prob": {
   "mobile": "sait ei tööta telefonis — klient lahkub enne laadimist",
   "https": "HTTPS puudub — brauser hoiatab klienti ohust",
   "ssl": "sertifikaadiviga — klient näeb hoiatuse «pole turvaline»",
   "stub": "sait tundub lõpetamata — usaldus kaob",
   "old": "sait näeb aegunud välja — klient arvab, et ettevõte on sulgunud",
   "slow": "sait laadib aeglaselt — osa kliente lahkub enne pakkumist",
   "dead": "sait ei avane — päringud lähevad kaotsi",
   "social": "ainult sotsiaalmeedia leht — teid ei leita Google'ist",
   "seo": "otsingumootori kirjeldus puudub — te ei ilmu tulemustes",
   "generic": "sait kaotab kliente, keda võiksite saada",
  },
  "dm_nosite": [
   "Tere! Olen {me}. Leidsin «{biz}» kaardilt — hea asukoht, aga veebis teid peaaegu ei nähta: klient otsib teenust telefoniga lähedalt ja valib ühe esimese kolme tulemuse seast. Sait, kus on telefon, kaart ja päringuvorm, lahendab selle 5–7 päevaga{pricep}. Näited: {portfolio}. Kas homme saab 15 minutit esilehe sisu üle rääkida?",
   "Tere! «{biz}» on kaardil, aga kodulehte pole — osa kliente valib konkurendi. Teen kodulehti kohalikele ettevõtetele{pricep}. Näitan 2 näidet ja tähtaega — kas sobib täna või homne?",
  ],
  "dm_weak": [
   "Tere! Olen {me}. Vaatasin {domain}: {problem}. Selle tõttu helistab klient sageli konkurendile. Parandus võtab 2–3 päeva, domeeni ei vahetata. Saadan ühe lehe enne/järel-võrdluse{pricep}. Näited: {portfolio}. Millal saate 10 minutit vaadata?",
   "Tere! Kontrollisin {domain}: {problem}. See maksab teile päringuid. Näitan, kuidas paari päevaga parandada, päris näite peal{pricep}. Täna või homme?",
  ],
  "call": {
   "open": "Tere! Olen {me}. Tean, et aeg on kallis — üks küsimus: kust kliendid praegu tulevad?",
   "hook_nosite": "Leidsin teid kaardilt, aga kodulehte ei leidnud. Kui klient otsib teie teenust lähedalt, näeb ta konkurente. Kui palju päringuid internetist kuus tuleb?",
   "hook_weak": "Teie saidil {domain}: {problem}. See maksab teile kõnesid. Kui palju päringuid saate nüüd — ja kui palju sooviksite?",
   "offer": "Teen 5–7 päevaga teie alale kodulehe{pricep}: telefon, kaart, päringuvorm, kiire laadimine. Mitte ilus pilt, vaid tööriist, mis toob päringuid.",
   "close": "Hoiame lühikeseks: saadan 2 näidet ja täpse tähtaja. WhatsAppi või e-postile? Kui ei sobi, ütlen ausalt.",
   "secretary": "Vajan 2 minutit selle inimesega, kes otsustab kodulehe üle. Millal saan helistada — enne või pärast lõunat?",
   "mail": "Saatsin. Millal võin vastuse üle vaadata — hommikul pärast lõunat?",
  },
  "em_subj_nosite": "«{biz}»: päringud Google'ist tühja asemel",
  "em_subj_weak": "{domain}: mis takistab päringuid",
  "em_nosite": "Tere!\n\nOlen {me}. Leidsin «{biz}» kaardilt. Kliendid otsivad teenuseid telefoniga «minu lähedal» ja valivad ettevõtted, kellel on sait, telefon ja vorm. Ilma selleta annate kliendid konkurentidele.\n\nMisan 5–7 päevaga{pricep}:\n• leht teenuste, hindade ja telefoniga;\n• kaart ja helista-nupp telefonis;\n• päringuvorm Telegrami või e-postile.\n\nNäited: {portfolio}\n\nVastage ühe sõnaga «jah» — saadan 2 näidet ja täpse tähtaja.\n\n{me}\n{contact}",
  "em_weak": "Tere!\n\nOlen {me}. Vaatasin «{biz}» saiti ({domain}). Põhiprobleem: {problem}. Iga päev maksab see teile osa päringutest.\n\nParandan 2–3 päevaga{pricep}:\n• eemaldan telefoni takistused ja kiirendan laadimist;\n• lisan selged «helista» ja «tellige» nupud;\n• ühendan päringuvormi ja põhi-SEO.\n\nNäited: {portfolio}\n\nVastake «jah» — saadan ühe lehe enne/järel-võrdluse.\n\n{me}\n{contact}",
  "fu": [
   "Tere! Saatsin teile näited ja tähtaja «{biz}» kodulehe kohta. Kui otsus seisab, öelge täpselt, mis vajab selgitust — ühest vastusest piisab.",
   "Viimane kiri. Kui aeg ei sobi, kustutan teid nimekirjast ega häiri enam. Kui soovite päringuid Google'ist kadude asemel, vastake «jah» — saadan ühelehelise plaani.",
  ],
  "obj": {
   "price": "Mõistan hinda. Arvutame: kui palju on üks uus klient väärt ettevõttele «{biz}»? Kui sait toob ühe kuus, tasub ta end ära. Võite alustada lihtsamast versioonist ja laiendada hiljem — mitte kogu summat korraga.",
   "noneed": "Hea küsimus. Kust kliendid praegu tulevad? Kui peamiselt suust suhu ja sotsiaalmeediast, jääb Google konkurentidele. Näitan 2 minutil, mida teie alal praegu otsitakse. Otsus on teie.",
   "think": "Muidugi. Mis täpselt vajab kaalumist — hind, tähtaeg või maht? Öelge, vastan ühe sõnumiga. Kohtume kolmapäeval kell 11 — sobib?",
   "have": "Suurepärane, teema on aktuaalne. Ei kritiseeri kellegi tööd: saadan sõltumatu vaate praegusele saidile — 3 konkreetset punkti. Kui-tab, räägime; kui ei, jääme ühendusse.",
   "social": "Sotsiaalmeedia toob tähelepanu, aga kui klient on ostmiseks valmis, ta otsib Google'ist ja avab kodulehe — teine etapp. Sait ei asenda sotsiaalmeediat, ta püüab juba soojad kliendid kinni. Näitan 2 näidet teie alalt.",
   "fine": "Rõõm kuulda. Kontrollime faktid: avame saadi telefonis ja mõõdame kiiruse. Kui see on tõesti hea, ütlen ausalt ja pakkun midagi muud — Google'i kaarti või SEO-d.",
  },
  "close_deal": "🤝 <b>Kuidas tehing lõpule viia</b>\n\n<b>1. Kolm paketti, keskmine on põhivalik.</b> Mini: kiire leht telefoni ja vormiga. Standard: koduleht + päringud + põhi-SEO. Pro: sait + sisu + reklaami käivitamine. Öelge keskmine hind esimesena — teised hinnatakse selle ümber.\n\n<b>2. Katseküsimus.</b> «Kui valmistame 5 päevaga ja päringud hakkavad tulema — alustame esmaspäeval?» See ei ole surve, vaid järgmine samm.\n\n<b>3. Eemalge hirm.</b> 30–50% ettemaks, ülejäänud pärast üleandmist. Üheleheline leping, tähtaeg ja maht kirjas. Näitage 2 näidet ja tagasisidet.\n\n<b>4. Võtke järgmine samm kohe.</b> «Kas saata arve või kinnitada esilehe tekstid enne?» Iga vastus on edasiminek.\n\n<b>5. Kui vaikib.</b> Üks meeldetuletus 2–3 päeva pärast konkreetselt: tähtaeg, hind, sisu. Seejärel peatuge.\n\n<i>Mõõdake päringuid, mitte ilu: saidi eesmärk on kõned ja vormid, mitte ilus pilt.</i>",
 },
 "sv": {
  "and": " och ",
  "prob": {
   "mobile": "sajten fungerar dåligt i mobilen — kunden lämnar innan den laddar",
   "https": "ingen HTTPS — webbläsaren varnar kunden för risk",
   "ssl": "certifikatfel — kunden ser varningen «inte säker»",
   "stub": "sajten ser ofärdig ut — förtroendet försvinner",
   "old": "sajten ser föråldrad ut — kunden tror att företaget är nedlagt",
   "slow": "sajten laddar långsamt — kunder lämnar innan erbjudandet visas",
   "dead": "sajten öppnar inte — förfrågningar går förlorade",
   "social": "bara en social medier-sida — ni hittas inte på Google",
   "seo": "ingen beskrivning för sökmotorer — ni syns inte i resultaten",
   "generic": "sajten tappar kunder som ni skulle kunna få",
  },
  "dm_nosite": [
   "Hej! Jag heter {me}. Jag hittade «{biz}» på kartan — bra läge, men ni syns nästan inte online: kunder söker tjänster nära sig på mobilen och väljer bland de tre första träffarna. En sajt med telefonnummer, karta och förfrågningsknapp löser det på 5–7 dagar{pricep}. Exempel: {portfolio}. Passar det att vi tar 15 minuter i morgon och bestämmer vad som ska stå på startsidan?",
   "Hej! «{biz}» finns på kartan men har ingen webbplats, så en del kunder väljer konkurrenter. Jag bygger sajter för lokala företag{pricep}. Jag visar 2 exempel och en deadline — idag eller imorgon?",
  ],
  "dm_weak": [
   "Hej! Jag heter {me}. Jag tittade på {domain}: {problem}. Därför ringer kunder ofta till en konkurrent. Det går att fixa på 2–3 dagar, utan att byta domän. Jag skickar en sida med före/efter{pricep}. Exempel: {portfolio}. När har ni 10 minuter att titta?",
   "Hej! Jag kontrollerade {domain}: {problem}. Det kostar er förfrågningar. Jag visar hur det förbättras på ett par dagar, med ett riktigt exempel{pricep}. Idag eller imorgon?",
  ],
  "call": {
   "open": "Hej! Jag heter {me}. Jag vet att er tid är värdefull — en fråga: var kommer kunderna ifrån just nu?",
   "hook_nosite": "Jag hittade er på kartan men ingen webbplats. När någon söker er tjänst nära sig ser de konkurrenterna. Hur många förfrågningar får ni från nätet per månad?",
   "hook_weak": "Er sajt {domain}: {problem}. Det kostar er samtal. Hur många förfrågningar får ni nu — och hur många vill ni ha?",
   "offer": "På 5–7 dagar bygger jag en sajt för er bransch{pricep}: telefon, karta, förfrågningsformulär, snabb laddning. Inte en fin bild — ett verktyg som ger förfrågningar.",
   "close": "Vi håller det kort: jag skickar 2 exempel och ett exakt datum. WhatsApp eller e-post? Passar det inte säger jag det ärligt.",
   "secretary": "Jag behöver 2 minuter med den som bestämmer om webbplatsen. När passar det att ringa — före eller efter lunch?",
   "mail": "Skickat. När ska jag höra av mig igen — i morgon eftermiddag?",
  },
  "em_subj_nosite": "«{biz}»: förfrågningar från Google i stället för ingenting",
  "em_subj_weak": "{domain}: det som stoppar era förfrågningar",
  "em_nosite": "Hej!\n\nJag heter {me}. Jag hittade «{biz}» på kartan. Kunder söker tjänster på mobilen «nära mig» och väljer företag med en sajt, telefonnummer och formulär. Utan det ger ni kunderna till konkurrenterna.\n\nVad jag levererar på 5–7 dagar{pricep}:\n• en sida med era tjänster, priser och telefonnummer;\n• karta och ringsknapp för mobilen;\n• ett förfrågningsformulär till er Telegram eller e-post.\n\nExempel: {portfolio}\n\nSvara med ett enda ord «ja» — jag skickar 2 exempel och ett exakt datum.\n\n{me}\n{contact}",
  "em_weak": "Hej!\n\nJag heter {me}. Jag granskade sajten för «{biz}» ({domain}). Huvudproblemet: {problem}. Varje dag kostar det er en del av förfrågningarna.\n\nVad jag fixar på 2–3 dagar{pricep}:\n• tar bort hinder på mobilen och snabbar upp laddningen;\n• lägger till tydliga «ring» och «beställ»-knappar;\n• kopplar ett formulär och grundläggande SEO.\n\nExempel: {portfolio}\n\nSvara «ja» — jag skickar en sida med före/efter.\n\n{me}\n{contact}",
  "fu": [
   "Hej! Jag skickade exempel och tidsplan för sajten till «{biz}». Om beslutet har fastnat: säg exakt vad som behöver förtydligas — ett meddelande räcker.",
   "Sista meddelandet. Om det inte passar nu tar jag bort er från listan och stör er inte mer. Om ni vill ha förfrågningar från Google i stället för förluster — svara «ja», jag skickar en en-sidig plan.",
  ],
  "obj": {
   "price": "Jag förstår frågan om pengar. Låt oss räkna: vad är en ny kund värd för «{biz}»? Om sajten ger en i månaden betalar den sig själv. Vi kan börja med en enklare version och bygga vidare — inte hela beloppet direkt.",
   "noneed": "Bra fråga. Var kommer kunderna ifrån nu? Om det mest är mun till mun och sociala medier får Google stå åt konkurrenterna. Jag visar på 2 minuter vad som söks inom er bransch just nu. Beslutet är ert.",
   "think": "Självklart. Vad behöver ni fundera på — pris, tid eller omfattning? Säg det, jag svarar med ett meddelande. Vi återkommer onsdag kl. 11 — passar det?",
   "have": "Bra, då är ämnet aktuellt. Jag ska inte kritisera någon annans arbete: jag skickar en oberoende syn på er nuvarande sajt — 3 konkreta punkter. Om det stämmer pratar vi, annars håller vi kontakten.",
   "social": "Sociala medier ger uppmärksamhet, men när kunden är redo att köpa söker hon på Google och öppnar en webbplats — ett annat steg. Sajten ersätter inte sociala medier, den fångar dem som redan är varma. Jag visar 2 exempel i er bransch.",
   "fine": "Roligt att höra. Då kollar vi fakta: öppna sajten i mobilen och mät laddningen. Om den verkligen är bra säger jag det och föreslår i stället något som faktiskt hjälper — Google-profilen eller SEO.",
  },
  "close_deal": "🤝 <b>Så här stänger du affären</b>\n\n<b>1. Tre paket, den mittersta är huvudvalet.</b> Mini: snabb sida med telefon och formulär. Standard: branschanpassad sajt + förfrågningar + basic SEO. Pro: sajt + innehåll + annonsstart. Nämnd det mittersta priset först — de andra bedöms utifrån det.\n\n<b>2. Testfråga.</b> «Om vi levererar på 5 dagar och förfrågningarna börjar komma — drar vi igång på måndagen?» Inte press, bara nästa steg.\n\n<b>3. Ta bort risken.</b> 30–50 % i förskott, resten vid leverans. Ett en-sidigt avtal med tid och omfattning. Visa 2 exempel och ett omdöme.\n\n<b>4. Ta nästa steg direkt.</b> «Ska jag skicka fakturan eller bekräftar vi startsidetexten först?» Alla svar är framsteg.\n\n<b>5. Om det blir tyst.</b> En påminnelse efter 2–3 dagar med fakta: deadline, pris, innehåll. Sedan stannar du.\n\n<i>Mät förfrågningar, inte skönhet: sajtens mål är samtal och formulär, inte en fin bild.</i>",
 },
 "de": {
  "and": " und ",
  "prob": {
   "mobile": "die Seite ist am Handy schwer bedienbar — Kunden springen ab",
   "https": "kein HTTPS — der Browser warnt Kunden vor Risiko",
   "ssl": "Zertifikatsfehler — Kunden sehen «nicht sicher»",
   "stub": "die Seite wirkt unfertig — das Vertrauen fehlt",
   "old": "die Seite wirkt veraltet — Kunden denken, das Geschäft sei geschlossen",
   "slow": "die Seite lädt langsam — Kunden gehen vor dem Angebot weg",
   "dead": "die Seite öffnet nicht — Anfragen gehen verloren",
   "social": "nur eine Social-Media-Seite — bei Google sind Sie nicht zu finden",
   "seo": "keine Beschreibung für Suchmaschinen — Sie tauchen nicht auf",
   "generic": "die Seite verliert Anfragen, die Sie bekommen könnten",
  },
  "dm_nosite": [
   "Guten Tag! Ich bin {me}. Ich habe «{biz}» auf der Karte gefunden — gute Lage, aber online sind Sie kaum sichtbar: Kunden suchen Leistungen in der Nähe am Handy und wählen aus den ersten drei Treffern. Eine Seite mit Telefonnummer, Karte und Anfrageformular löst das in 5–7 Tagen{pricep}. Beispiele: {portfolio}. Haben Sie morgen 15 Minuten, um den Inhalt der Startseite festzulegen?",
   "Hallo! «{biz}» steht auf der Karte, hat aber keine Website — so entscheiden sich Kunden für die Konkurrenz. Ich baue Websites für lokale Unternehmen{pricep}. Ich zeige 2 Beispiele und einen Termin — heute oder morgen?",
  ],
  "dm_weak": [
   "Guten Tag! Ich bin {me}. Ich habe mir {domain} angesehen: {problem}. Deshalb ruft der Kunde oft die Konkurrenz an. Die Behebung dauert 2–3 Tage, ohne Domainwechsel. Ich schicke eine einseitige Vorher/Nachher-Analyse{pricep}. Beispiele: {portfolio}. Wann haben Sie 10 Minuten Zeit?",
   "Hallo! Ich habe {domain} geprüft: {problem}. Das kostet Sie Anfragen. Ich zeige an einem echten Beispiel, wie es in zwei Tagen besser wird{pricep}. Heute oder morgen?",
  ],
  "call": {
   "open": "Guten Tag! Ich bin {me}. Ich weiß, Ihre Zeit ist kostbar — eine Frage: woher kommen Ihre Kunden gerade?",
   "hook_nosite": "Ich habe Sie auf der Karte gefunden, aber keine Website. Wer Ihre Leistung in der Nähe sucht, sieht die Konkurrenz. Wie viele Anfragen kommen monatlich aus dem Internet?",
   "hook_weak": "Ihre Seite {domain}: {problem}. Das kostet Sie Anrufe. Wie viele Anfragen bekommen Sie derzeit — und wie viele möchten Sie?",
   "offer": "In 5–7 Tagen baue ich eine Website für Ihre Branche{pricep}: Telefon, Karte, Anfrageformular, schnelle Ladezeit. Kein hübsches Bild, sondern ein Werkzeug, das Anfragen bringt.",
   "close": "Kurz und knapp: ich schicke 2 Beispiele und einen festen Termin. WhatsApp oder E-Mail? Wenn es nicht passt, sage ich ehrlich Bescheid.",
   "secretary": "Ich brauche 2 Minuten mit der Person, die über die Website entscheidet. Wann kann ich anrufen — vor oder nach der Mittagspause?",
   "mail": "Versandt. Wann darf ich nachfragen — morgen Nachmittag?",
  },
  "em_subj_nosite": "«{biz}»: Anfragen aus Google statt nichts",
  "em_subj_weak": "{domain}: was Ihre Anfragen verhindert",
  "em_nosite": "Guten Tag!\n\nIch bin {me}. Ich habe «{biz}» auf der Karte gefunden. Kunden suchen Leistungen am Handy mit «in der Nähe» und entscheiden sich für Firmen mit Website, Telefonnummer und Formular. Ohne die bekommen die Konkurrenten diese Kunden.\n\nWas ich in 5–7 Tagen liefere{pricep}:\n• eine Seite mit Leistungen, Preisen und Telefonnummer;\n• Karte und Klick-zu-Anrufen fürs Handy;\n• ein Anfrageformular in Telegram oder per E-Mail.\n\nBeispiele: {portfolio}\n\nAntworten Sie einfach mit «ja» — ich schicke 2 Beispiele und einen festen Termin.\n\n{me}\n{contact}",
  "em_weak": "Guten Tag!\n\nIch bin {me}. Ich habe die Seite von «{biz}» ({domain}) geprüft. Das Hauptproblem: {problem}. Jeden Tag kostet Sie das einen Teil der Anfragen.\n\nWas ich in 2–3 Tagen behebe{pricep}:\n• Hürden auf dem Handy entferne und die Ladezeit verbessere;\n• klare «Anrufen»- und «Bestellen»-Buttons ergänze;\n• ein Formular und grundlegendes SEO anbinde.\n\nBeispiele: {portfolio}\n\nAntworten Sie mit «ja» — ich schicke die einseitige Vorher/Nachher-Analyse.\n\n{me}\n{contact}",
  "fu": [
   "Guten Tag! Ich habe Ihnen Beispiele und den Zeitplan für die Website von «{biz}» geschickt. Falls die Entscheidung stockt: sagen Sie mir genau, was geklärt werden muss — eine Nachricht genügt.",
   "Letzte Nachricht. Falls es gerade nicht passt, entferne ich Sie von meiner Liste und störe Sie nicht weiter. Wenn Sie Anfragen aus Google statt Verluste möchten, antworten Sie mit «ja» — ich schicke einen einseitigen Plan.",
  ],
  "obj": {
   "price": "Ich verstehe die Frage nach dem Preis. Rechnen wir: Was ist ein neuer Kunde für «{biz}» wert? Wenn die Website nur einen pro Monat bringt, hat sie sich amortisiert. Wir können mit einer kleinen Version starten und später erweitern — nicht den vollen Betrag sofort.",
   "noneed": "Gute Frage. Woher kommen Ihre Kunden derzeit? Wenn hauptsächlich durch Weiterempfehlung und soziale Medien, überlassen Sie Google der Konkurrenz. Ich zeige Ihnen in 2 Minuten, wonach in Ihrer Branche gerade gesucht wird. Die Entscheidung bleibt bei Ihnen.",
   "think": "Natürlich. Was genau muss überlegt werden — Preis, Zeitraum oder Umfang? Sagen Sie es, ich antworte mit einer Nachricht. Mittwoch um 11 Uhr — passt das?",
   "have": "Super, dann ist das Thema aktuell. Ich werde die Arbeit anderer nicht kritisieren: ich schicke einen unabhängigen Blick auf Ihre aktuelle Seite — 3 konkrete Punkte. Wenn es passt, sprechen wir; wenn nicht, bleiben wir in Kontakt.",
   "social": "Soziale Medien bringen Aufmerksamkeit, aber wenn der Kunde kaufbereit ist, sucht er bei Google und öffnet eine Website — eine andere Phase. Die Website ersetzt Social Media nicht, sie fängt bereits warme Kunden ab. Ich zeige 2 Beispiele aus Ihrer Branche.",
   "fine": "Freut mich. Dann prüfen wir die Fakten: öffnen wir die Seite am Handy und messen die Ladezeit. Wenn sie wirklich gut ist, sage ich das ehrlich und schlage etwas vor, das tatsächlich hilft — Google-Profil oder SEO.",
  },
  "close_deal": "🤝 <b>So führen Sie das Gespräch zum Abschluss</b>\n\n<b>1. Drei Pakete, das mittlere ist die Hauptwahl.</b> Mini: schnelle Seite mit Telefon und Formular. Standard: Branchen-Website + Anfragen + Basis-SEO. Pro: Website + Inhalte + Anzeigenstart. Nennen Sie den mittleren Preis zuerst — die anderen werden daran gemessen.\n\n<b>2. Testfrage.</b> «Wenn wir in 5 Tagen liefern und die Anfragen kommen — starten wir am Montag?» Kein Druck, nur der nächste Schritt.\n\n<b>3. Risiko nehmen.</b> 30–50 % Anzahlung, Rest bei Übergabe. Ein einseitiger Vertrag mit Termin und Umfang. Zeigen Sie 2 Beispiele und ein Feedback.\n\n<b>4. Nächsten Schritt sofort holen.</b> «Soll ich die Rechnung schicken oder zuerst den Text der Startseite festlegen?» Jede Antwort ist Fortschritt.\n\n<b>5. Bei Stille.</b> Eine Erinnerung nach 2–3 Tagen mit Fakten: Termin, Preis, Inhalt. Dann stoppen Sie.\n\n<i>Messen Sie Anfragen, nicht Schönheit: Ziel der Website sind Anrufe und Formulare, kein hübscher Screenshot.</i>",
 },
}

# ---------- Памятки для оператора (RU): продажа, а не «предложение сотрудничества» ----------
PLAN_NOSITE = (
    "📋 <b>План: взять клиента без сайта (продажа)</b>\n\n"
    "<b>1. За 5 минут собери факты</b>\nОткрой карточку, посмотри фото и отзывы, найди имя владельца. Выбери ОДНУ выгоду: «клиенты ищут вас рядом и не находят».\n\n"
    "<b>2. Первый контакт = боль + цифра</b>\nОдно сообщение из кнопки «Директ», один вопрос в конце. Не пиши «давайте сотрудничать».\n\n"
    "<b>3. Крючок</b>\nСделай быстрый скрин главной под их нишу за 20 минут. Покажи картинку, а не обещания.\n\n"
    "<b>4. Дожим</b>\nТишина → через 2–3 дня конкретный вопрос, через 7 дней последнее письмо. Дальше стоп.\n\n"
    "<b>5. Звонок</b>\nБудни 10–12 или 14–16. Начни с вопроса «откуда сейчас клиенты?», слушай больше, чем говори.\n\n"
    "<b>6. Оффер</b>\nТри пакета, средний — основной. Назови срок и что именно входит. Затем «пробный вопрос»: «начинаем в понедельник?»\n\n"
    "<b>7. Оплата</b>\nПредоплата 30–50%, договор на 1 страницу, дата сдачи. Сразу возьми следующий шаг: счёт или текст для главной.\n\n"
    "<b>8. Допродажа</b>\nGoogle-карточка, поддержка, SEO, реклама.\n\n"
    "<i>Ориентир: из 30–50 касаний — 5–10 ответов и 1–3 сделки. Считай ответы и оплаты, а не «красоту».</i>"
)
PLAN_WEAK = (
    "📋 <b>План: взять клиента со слабым сайтом (продажа)</b>\n\n"
    "<b>1. Собери доказательства за 10 минут</b>\nСкриншот с телефона + скорость из Google PageSpeed + одна самая заметная проблема. Без критики — только факты.\n\n"
    "<b>2. Первый контакт</b>\nНазови ОДНУ проблему и цену бездействия: «из-за этого клиент уходит к конкуренту». Один вопрос в конце.\n\n"
    "<b>3. Крючок</b>\nРазбор «до/после» на одной странице. Покажи, как обновится страница и пойдёт заявка, а не просто «сделаем лучше».\n\n"
    "<b>4. Дожим</b>\nЧерез 2–3 дня уточняющий вопрос, через 7 дней последнее письмо. Дальше стоп.\n\n"
    "<b>5. Оффер</b>\nДва пути: «починить текущий» (дешевле) и «новый под задачи» (дороже). Клиенту проще выбрать из двух.\n\n"
    "<b>6. Работа с возражениями</b>\n«Дорого» → считаем цену одного клиента. «Нам нормально» → факты со скриншота. Кнопка «Возражения».\n\n"
    "<b>7. Закрытие</b>\nПредоплата 30–50%, срок, один вопрос: «с чего начнём — с исправлений или с нового?»\n\n"
    "<i>Продавай не сайт, а результат: телефон, заявку и клиента, который уже выбрал вас.</i>"
)
GENERAL_TIPS = (
    "🎯 <b>Продающие привычки</b>\n\n"
    "• Говори на языке клиента: в Финляндии — финский или английский, если владелец не русскоязычный.\n"
    "• Одно сообщение = одна мысль = один вопрос в конце.\n"
    "• Сначала боль и цена бездействия, потом срок и результат. Не «давайте сотрудничать».\n"
    "• Показывай картинку/скрин «до и после» — она продаёт лучше слов.\n"
    "• Не пиши до 10:00 и после 18:00. Лучшие дни: вторник–четверг.\n"
    "• Холодные письма и рассылки попадают под GDPR: пиши вручную, по делу, не спамь.\n"
    "• Веди учёт: кому писал, что ответили, дата следующего шага.\n"
    "• После двух напоминаний остановись. Вернуться можно через 1–2 месяца.\n\n"
    "Нажми «✍️ Скрипты и подсказки» под карточкой — там готовые тексты и план закрытия именно для этого клиента."
)
OBJECTIONS = {
    "price": ("💸 «Дорого»", "Не снижай цену сразу. Спроси: «Сколько стоит для вас один новый клиент?» Покажи, что один клиент в месяц окупает сайт. Предложи мини-пакет или оплату частями."),
    "noneed": ("🙅 «Нам не нужно»", "Не спорь. Спроси «Откуда клиенты сейчас?» и покажи, что по их нише ищут в Google. Оставь решение за клиентом."),
    "think": ("🤔 «Подумаем»", "Уточни, что именно: цена, срок или объём. Ответь одним сообщением и назначь конкретную дату, а не «на связи»."),
    "have": ("👷 «Уже есть кто делает»", "Не критикуй. Предложи независимый взгляд: 3 конкретных пункта по текущему сайту. Оставь контакт без давления."),
    "social": ("📱 «Хватает соцсетей»", "Согласись и раздели этапы: соцсети — внимание, Google — намерение купить. Сайт ловит горячих, соцсети — нет."),
    "fine": ("👍 «Сайт нормальный»", "Не нападай. Покажи скрин с телефона и скорость. Если правда хорошо — скажи честно и предложи Google-карточку или SEO."),
}
