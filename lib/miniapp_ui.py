# -*- coding: utf-8 -*-
"""Вёрстка Telegram Mini App. Лежит в .py, чтобы Vercel гарантированно включил
её в бандл serverless-функции (не зависит от раздачи статики)."""

HTML = r"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#12161e">
<title>Lead Radar — поиск клиентов</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>
:root{
  color-scheme:dark;
  --bg:#12161e; --bg2:#161c26; --card:#1b2230; --soft:#222b3a;
  --text:#e8edf6; --hint:#a4b0c4; --accent:#6aa1ff; --accent2:#8a76f0;
  --accent-text:#fff; --line:rgba(180,200,235,.11);
  --green:#4fd0a8; --red:#ff8a8a; --yellow:#e7c477;
  --shadow:0 10px 30px rgba(0,0,0,.28); --glow:rgba(106,161,255,.25);
}
:root[data-theme="light"]{
  color-scheme:light;
  --bg:#f6f7fa; --bg2:#eef1f6; --card:#ffffff; --soft:#eef1f6;
  --text:#1e2733; --hint:#5f6b7d; --accent:#3f78dd; --accent2:#6d5ad6;
  --accent-text:#fff; --line:rgba(30,45,75,.10);
  --green:#199b73; --red:#d9534f; --yellow:#a97813;
  --shadow:0 10px 28px rgba(31,45,75,.10); --glow:rgba(63,120,221,.20);
}
:root[data-motion="calm"] *{animation-duration:.001ms!important;animation-iteration-count:1!important;transition-duration:.001ms!important}
:root[data-font="large"] body{font-size:17px}
:root[data-font="large"] .hero-sub,
:root[data-font="large"] .meta,
:root[data-font="large"] .issues,
:root[data-font="large"] .pitch{font-size:14px}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html{scroll-behavior:smooth}
[hidden]{display:none!important}
body{margin:0;background:var(--bg);color:var(--text);
  font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  padding:0 14px calc(34px + env(safe-area-inset-bottom));
  transition:background-color .35s ease,color .35s ease;-webkit-font-smoothing:antialiased}
body,button,input,.card,.chip,.summary,.sheet-inner,.tab,.mini,.icon-btn,
.hero-stats span,.bar,.bar i,.log,.log div,#toast,.seg,.seg button{
  transition:background-color .3s ease,color .3s ease,border-color .3s ease,
             box-shadow .3s ease,transform .3s cubic-bezier(.2,.8,.2,1),opacity .3s ease}
button,input{font:inherit}
section:not([hidden]){animation:screenIn .38s ease both}
@keyframes screenIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
@media (hover:hover){
  .chip:hover,.mini:hover,.tab:hover,.icon-btn:hover,.seg button:not(.on):hover,
  #more:hover,.close-x:hover{transform:translateY(-2px);box-shadow:var(--shadow)}
}
#app{max-width:620px;margin:0 auto}
.hero{padding:24px 4px 18px;position:relative;overflow:hidden}
.hero:before{content:"";position:absolute;width:240px;height:240px;border-radius:50%;
  background:radial-gradient(circle,var(--glow),transparent 70%);top:-130px;right:-80px;pointer-events:none;
  animation:floatGlow 9s ease-in-out infinite alternate}
@keyframes floatGlow{to{transform:translate(-18px,14px) scale(1.12)}}
.brand{display:flex;align-items:center;gap:10px;font-weight:800;letter-spacing:.5px;font-size:19px;padding-right:46px}
.brand .dot{width:11px;height:11px;border-radius:50%;background:var(--green);box-shadow:0 0 0 5px var(--glow);
  animation:softPulse 2.6s ease-in-out infinite}
@keyframes softPulse{50%{box-shadow:0 0 0 9px transparent}}
.icon-btn{position:absolute;right:4px;top:19px;width:38px;height:38px;border-radius:12px;border:1px solid var(--line);
  background:var(--card);color:var(--text);font-size:17px;cursor:pointer;display:grid;place-items:center;box-shadow:var(--shadow)}
.icon-btn:active{transform:scale(.94)}
.hero-sub{color:var(--hint);margin-top:6px;font-size:13px}
.hero-stats{display:flex;gap:8px;margin-top:16px;flex-wrap:wrap}
.hero-stats span{background:var(--card);border:1px solid var(--line);border-radius:999px;
  padding:6px 11px;font-size:11px;color:var(--hint);box-shadow:0 2px 10px rgba(0,0,0,.04)}
.hero-stats b{color:var(--text)}
.sec{margin:20px 0 9px;font-size:12px;font-weight:700;letter-spacing:.7px;text-transform:uppercase;color:var(--hint)}
.chips{display:flex;flex-wrap:wrap;gap:8px}
.chip{border:1px solid var(--line);background:var(--card);color:var(--text);border-radius:13px;
  padding:10px 12px;font-size:13px;cursor:pointer;user-select:none;box-shadow:0 2px 8px rgba(0,0,0,.04)}
.chip:active{transform:scale(.96)}
.chip.on{background:var(--accent);color:var(--accent-text);border-color:transparent;
  box-shadow:0 8px 20px var(--glow);transform:translateY(-1px)}
.chip.sm{padding:9px 11px;font-size:12px}
.city-row{display:flex;gap:8px}
#city{flex:1;min-width:0;background:var(--card);border:1px solid var(--line);color:var(--text);
  border-radius:13px;padding:14px;outline:none}
#city:focus{border-color:var(--accent);box-shadow:0 0 0 3px var(--glow)}
#geo{width:50px;border-radius:13px;border:1px solid var(--line);background:var(--card);color:var(--text);cursor:pointer}
#geo:active{transform:scale(.95)}
.primary{width:100%;margin-top:18px;border:0;border-radius:15px;padding:16px;cursor:pointer;
  background:linear-gradient(135deg,var(--accent),var(--accent2));background-size:160% 100%;
  color:#fff;font-weight:750;font-size:16px;box-shadow:0 10px 26px var(--glow);
  transition:transform .25s cubic-bezier(.2,.8,.2,1),box-shadow .3s ease,background-position .5s ease,opacity .3s ease}
.primary:hover{background-position:100% 0;box-shadow:0 14px 30px var(--glow);transform:translateY(-2px)}
.primary:active{transform:scale(.985)}
.primary:disabled{opacity:.6;box-shadow:none;transform:none}
.hint{color:var(--hint);font-size:12px;text-align:center;margin-top:10px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.card{background:var(--card);border:1px solid var(--line);border-radius:17px;padding:15px;margin-bottom:11px;
  position:relative;overflow:hidden;box-shadow:var(--shadow);animation:rise .42s cubic-bezier(.2,.8,.2,1) both}
.card:hover{transform:translateY(-3px);box-shadow:0 16px 34px rgba(0,0,0,.16)}
.card:before{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--green)}
.card.weak:before{background:var(--yellow)}
@keyframes rise{from{opacity:0;transform:translateY(16px) scale(.985)}to{opacity:1;transform:none}}
.card h3{margin:0 0 5px;font-size:16px;padding-right:64px}
.badge{position:absolute;right:13px;top:14px;font-size:10px;font-weight:700;border-radius:999px;
  padding:4px 8px;background:rgba(79,208,168,.14);background:color-mix(in srgb,var(--green) 14%,transparent);color:var(--green)}
.card.weak .badge{background:rgba(231,196,119,.14);background:color-mix(in srgb,var(--yellow) 15%,transparent);color:var(--yellow)}
.meta{color:var(--hint);font-size:12px;margin:3px 0}
.issues{font-size:12px;color:var(--yellow);margin-top:6px}
.pitch{font-size:12px;color:var(--hint);margin-top:7px;font-style:italic}
.card-actions{display:flex;gap:7px;flex-wrap:wrap;margin-top:12px}
.mini{border:1px solid var(--line);background:transparent;color:var(--text);border-radius:10px;
  padding:8px 11px;font-size:12px;cursor:pointer;text-decoration:none;display:inline-flex;align-items:center;gap:4px}
.mini.main{background:var(--accent);border-color:transparent;color:#fff;font-weight:650;box-shadow:0 6px 16px var(--glow)}
.summary{background:linear-gradient(135deg,var(--glow),transparent);
  border:1px solid var(--line);border-radius:17px;padding:16px;margin-top:14px;box-shadow:var(--shadow);
  animation:rise .45s .08s ease both}
.summary .big{font-size:24px;font-weight:800}
.summary .pot{color:var(--green);font-weight:700;margin-top:6px}
.toolbar{display:flex;gap:7px;flex-wrap:wrap;margin:13px 0}
.toolbar button{flex:1;min-width:90px}
#more{width:100%;margin:8px 0 18px;background:var(--card);color:var(--text);
  border:1px solid var(--line);border-radius:13px;padding:13px;cursor:pointer}
.hidden-note{text-align:center;padding:45px 10px;color:var(--hint)}
.hidden-note b{display:block;color:var(--text);font-size:17px;margin-bottom:6px}
/* --- загрузка --- */
#loading{padding:26px 6px;text-align:center}
.radar{width:190px;height:190px;margin:12px auto 22px;border-radius:50%;position:relative;
  border:1px solid var(--line);background:radial-gradient(circle,var(--glow),transparent 65%)}
.radar:before{content:"";position:absolute;inset:0;border-radius:50%;
  background:conic-gradient(from 0deg,var(--accent),transparent 28%);opacity:.6;
  animation:sweep 1.5s linear infinite}
@keyframes sweep{to{transform:rotate(360deg)}}
.radar .ring{position:absolute;border:1px solid var(--line);border-radius:50%;inset:26px;animation:pulse 2.2s ease-in-out infinite}
.radar .ring:nth-child(2){inset:56px;animation-delay:.4s}
@keyframes pulse{50%{transform:scale(1.09);opacity:.45}}
.radar .core{position:absolute;left:50%;top:50%;width:16px;height:16px;border-radius:50%;
  background:var(--green);transform:translate(-50%,-50%);box-shadow:0 0 0 8px var(--glow),0 0 22px var(--green)}
.radar .blip{position:absolute;width:7px;height:7px;border-radius:50%;background:var(--yellow);
  box-shadow:0 0 12px var(--yellow);animation:blip 2.1s ease-out infinite}
.radar .blip.b1{left:67%;top:34%}.radar .blip.b2{left:32%;top:64%;animation-delay:.7s}
.radar .blip.b3{left:60%;top:70%;animation-delay:1.2s}
@keyframes blip{0%{transform:scale(0);opacity:0}30%{opacity:1}100%{transform:scale(1.6);opacity:0}}
.stage{font-size:17px;font-weight:700;margin-bottom:4px}
.ticker{color:var(--accent);font-size:12px;height:20px;overflow:hidden}
.ticker span{display:block;animation:tick 2.8s ease-in-out infinite}
@keyframes tick{0%{opacity:.35;transform:translateY(6px)}50%{opacity:1;transform:none}100%{opacity:.35;transform:translateY(-6px)}}
.bar{height:7px;background:var(--card);border-radius:99px;overflow:hidden;margin:20px 0 15px;box-shadow:inset 0 1px 3px rgba(0,0,0,.12)}
.bar i{display:block;height:100%;width:0;border-radius:99px;
  background:linear-gradient(90deg,var(--accent),var(--green),var(--accent2));background-size:200% 100%;
  animation:barShine 1.8s linear infinite;
  transition:width .55s cubic-bezier(.2,.8,.2,1),box-shadow .3s ease,background-color .3s ease;
  box-shadow:0 0 14px var(--glow)}
@keyframes barShine{to{background-position:200% 0}}
.log{height:190px;overflow-y:auto;text-align:left;position:relative;scroll-behavior:smooth;scrollbar-width:none;
  mask-image:linear-gradient(to bottom,transparent,#000 22%,#000 82%,transparent);
  -webkit-mask-image:linear-gradient(to bottom,transparent,#000 22%,#000 82%,transparent)}
.log::-webkit-scrollbar{display:none}
.log div{font-size:12px;color:var(--hint);padding:5px 9px;border-left:2px solid var(--line);margin-bottom:5px;
  border-radius:0 8px 8px 0;animation:logIn .35s ease both}
.log div b{color:var(--green);font-weight:600}
.log div.now{border-left-color:var(--accent);color:var(--text)}
@keyframes logIn{from{opacity:0;transform:translateX(-10px)}to{opacity:1;transform:none}}
/* --- шторка скриптов --- */
.sheet{position:fixed;inset:0;background:rgba(6,10,18,.55);z-index:20;display:flex;align-items:flex-end;justify-content:center;
  animation:fadeIn .24s ease both;backdrop-filter:blur(3px)}
.sheet[hidden]{display:none}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
.sheet-inner{background:var(--bg);width:100%;max-width:620px;max-height:88vh;border-radius:22px 22px 0 0;
  border:1px solid var(--line);box-shadow:0 -16px 40px rgba(0,0,0,.2);
  display:flex;flex-direction:column;overflow:hidden;animation:up .34s cubic-bezier(.2,.8,.2,1) both}
@keyframes up{from{transform:translateY(100%);opacity:.5}to{transform:none;opacity:1}}
.sheet-head{display:flex;align-items:center;justify-content:space-between;padding:16px 16px 10px}
.sheet-head b{font-size:16px}
.close-x{border:0;background:var(--card);color:var(--text);border-radius:50%;width:32px;height:32px;cursor:pointer}
.tabs{display:flex;gap:7px;overflow-x:auto;padding:4px 14px 10px;scrollbar-width:none}
.tabs::-webkit-scrollbar{display:none}
.tab{white-space:nowrap;border:1px solid var(--line);background:transparent;color:var(--hint);
  border-radius:999px;padding:7px 11px;font-size:12px;cursor:pointer}
.tab.on{background:var(--accent);color:#fff;border-color:transparent}
.sheet-body{padding:4px 16px 18px;overflow-y:auto;font-size:14px}
.sheet-body h4{margin:18px 0 6px;font-size:13px;color:var(--hint);text-transform:uppercase;letter-spacing:.5px}
.sheet-body pre{white-space:pre-wrap;word-wrap:break-word;background:var(--card);border:1px solid var(--line);
  border-radius:13px;padding:13px;font:12px/1.55 ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--text);margin:6px 0 14px}
.sheet-body p{margin:8px 0}
.sheet-body>*{animation:fadeUp .3s ease both}
@keyframes fadeUp{from{opacity:0;transform:translateY(7px)}to{opacity:1;transform:none}}
.langs{display:flex;gap:6px;flex-wrap:wrap;margin:10px 0}
.langs button{border:1px solid var(--line);background:transparent;color:var(--hint);border-radius:9px;padding:6px 9px;font-size:11px;cursor:pointer}
.langs button.on{border-color:var(--accent);color:var(--accent)}
.sheet-foot{padding:12px 16px calc(14px + env(safe-area-inset-bottom));border-top:1px solid var(--line);display:flex;gap:8px}
.sheet-foot button{flex:1}
/* --- настройки --- */
.setting{padding:13px 0;border-bottom:1px solid var(--line)}
.setting:last-of-type{border-bottom:0}
.setting label{display:block;font-size:11px;color:var(--hint);margin-bottom:9px;text-transform:uppercase;letter-spacing:.6px}
.seg{display:flex;gap:4px;background:var(--soft);border:1px solid var(--line);border-radius:13px;padding:4px}
.seg button{flex:1;border:0;background:transparent;color:var(--hint);border-radius:10px;padding:10px 6px;font-size:13px;cursor:pointer}
.seg button.on{background:var(--accent);color:#fff;box-shadow:0 6px 16px var(--glow)}
.setting-note{color:var(--hint);font-size:12px;padding:14px 0 4px}
.settings-foot{padding:12px 16px calc(14px + env(safe-area-inset-bottom));border-top:1px solid var(--line)}
.settings-foot button{width:100%}
#toast{position:fixed;left:50%;bottom:30px;transform:translateX(-50%) translateY(20px);
  background:var(--card);color:var(--text);border:1px solid var(--line);
  padding:12px 18px;border-radius:12px;font-size:13px;opacity:0;transition:.28s ease;
  pointer-events:none;z-index:50;box-shadow:var(--shadow);max-width:90vw;text-align:center}
#toast.show{opacity:1;transform:translateX(-50%)}
</style>
</head>
<body>
<div id="app">
  <div class="hero">
    <div class="brand"><span class="dot"></span> LEAD RADAR</div>
    <button class="icon-btn" id="settingsBtn" title="Настройки">⚙️</button>
    <div class="hero-sub">Нахожу бизнесы без сайта и со слабым сайтом — и даю готовые тексты, чтобы продать им сайт.</div>
    <div class="hero-stats">
      <span>🌍 <b>6</b> языков скриптов</span><span>🗺 <b>6</b> источников карт</span><span>⚡ поиск от <b>6 сек</b></span>
    </div>
  </div>

  <section id="setup">
    <div class="sec">1. Ниша бизнеса</div>
    <div class="chips" id="niches"></div>
    <div class="sec">2. Что ищем</div>
    <div class="chips" id="modes"></div>
    <div class="sec">3. Фильтры</div>
    <div class="chips" id="flags"></div>
    <div class="sec">4. Город</div>
    <div class="city-row">
      <input id="city" placeholder="Например: Helsinki или Turku, 10 км" autocomplete="off">
      <button id="geo" title="Моё местоположение">📍</button>
    </div>
    <button class="primary" id="find">🔎 Найти клиентов</button>
    <div class="hint">Можно писать город на местном языке — поиск учитывает синонимы</div>
  </section>

  <section id="loading" hidden>
    <div class="radar"><div class="ring"></div><div class="ring"></div><div class="core"></div>
      <div class="blip b1"></div><div class="blip b2"></div><div class="blip b3"></div></div>
    <div class="stage" id="stage">Подключаюсь к картам…</div>
    <div class="ticker"><span id="tickerText">Ищем там, где конкуренты ещё не успели…</span></div>
    <div class="bar"><i id="bar"></i></div>
    <div class="log" id="log"></div>
  </section>

  <section id="results" hidden>
    <div class="summary" id="summary"></div>
    <div class="toolbar">
      <button class="mini" id="toggleView">🙈 Скрыть</button>
      <button class="mini" id="csv">📥 CSV</button>
      <button class="mini" id="again">🔄 Новый поиск</button>
    </div>
    <div id="cards"></div>
    <div class="hidden-note" id="hiddenNote" hidden><b>Результаты скрыты</b>Они никуда не делись — нажми, чтобы вернуть.</div>
    <button id="more" hidden>Показать ещё ↓</button>
  </section>
</div>

<div id="sheet" class="sheet" hidden>
  <div class="sheet-inner">
    <div class="sheet-head"><b id="sheetTitle">Скрипты</b><button class="close-x" id="sheetClose">✕</button></div>
    <div class="tabs" id="tabs"></div>
    <div class="sheet-body" id="sheetBody"></div>
    <div class="sheet-foot">
      <button class="mini main" id="sendChat">📨 Отправить в чат</button>
      <button class="mini" id="copyText">📋 Копировать</button>
    </div>
  </div>
</div>

<div id="settings" class="sheet" hidden>
  <div class="sheet-inner">
    <div class="sheet-head"><b>Настройки</b><button class="close-x" id="settingsClose">✕</button></div>
    <div class="sheet-body">
      <div class="setting">
        <label>Тема оформления</label>
        <div class="seg" id="segTheme"><button data-v="dark">🌙 Чёрная</button><button data-v="light">☀️ Белая</button></div>
      </div>
      <div class="setting">
        <label>Анимации</label>
        <div class="seg" id="segMotion"><button data-v="smooth">✨ Плавные</button><button data-v="calm">🌿 Спокойные</button></div>
      </div>
      <div class="setting">
        <label>Размер текста</label>
        <div class="seg" id="segFont"><button data-v="normal">Обычный</button><button data-v="large">Крупнее</button></div>
      </div>
      <p class="setting-note">Выбор сохраняется на этом устройстве и применяется сразу. Спокойный режим убирает лишнее движение.</p>
    </div>
    <div class="settings-foot"><button class="mini main" id="settingsDone">Готово</button></div>
  </div>
</div>
<div id="toast"></div>

<script>
const $=s=>document.querySelector(s);
const TG=window.Telegram&&window.Telegram.WebApp;
const state={cfg:null,key:'food',mode:'n',flags:'',city:'',data:null,page:0,lang:'ru',lead:null,tab:'dm',hidden:false};
const FLAGS=[['p','📞 С телефоном'],['e','✉️ С email'],['c','🏪 Без сетей']];
const PREFS={theme:'lr_theme',motion:'lr_motion',font:'lr_font'};
const calm=()=>document.documentElement.dataset.motion==='calm';
const scrollBehavior=()=>calm()?'auto':'smooth';

function applyPrefs(){
  const t=localStorage.getItem(PREFS.theme)||'dark';
  const m=localStorage.getItem(PREFS.motion)||'smooth';
  const f=localStorage.getItem(PREFS.font)||'normal';
  const root=document.documentElement;
  root.dataset.theme=t;root.dataset.motion=m;root.dataset.font=f;
  const shell=t==='light'?'#f6f7fa':'#12161e';
  const meta=document.querySelector('meta[name="theme-color"]');
  if(meta)meta.setAttribute('content',shell);
  if(TG){try{TG.setHeaderColor(shell);TG.setBackgroundColor(shell)}catch(e){}}
  [['segTheme',t],['segMotion',m],['segFont',f]].forEach(([id,v])=>{
    const box=document.getElementById(id);if(!box)return;
    [...box.children].forEach(b=>b.classList.toggle('on',b.dataset.v===v));
  });
}
function bindSeg(id,key){
  const box=document.getElementById(id);if(!box)return;
  [...box.children].forEach(b=>b.onclick=()=>{
    haptic();localStorage.setItem(PREFS[key],b.dataset.v);applyPrefs();
  });
}
function haptic(t){try{TG&&TG.HapticFeedback.impactOccurred(t||'light')}catch(e){}}
function toast(t){const el=$('#toast');el.textContent=t;el.classList.add('show');setTimeout(()=>el.classList.remove('show'),2200)}
function show(id){
  ['setup','loading','results'].forEach(s=>$('#'+s).hidden=(s!==id));
  try{window.scrollTo({top:0,behavior:scrollBehavior()})}catch(e){window.scrollTo(0,0)}
}
function countUp(el,to){
  if(calm()){el.textContent=to;return}
  const t0=performance.now(),dur=650;
  (function step(t){
    const k=Math.min(1,(t-t0)/dur);
    el.textContent=Math.round(to*(1-Math.pow(1-k,3)));
    if(k<1)requestAnimationFrame(step);
  })(t0);
}
function animateNums(root){root.querySelectorAll('[data-count]').forEach(el=>countUp(el,+el.dataset.count||0))}
function chip(txt,on,fn,small){const b=document.createElement('button');b.className='chip'+(on?' on':'')+(small?' sm':'');b.textContent=txt;b.onclick=()=>{haptic();fn()};return b}

async function api(path,body){
  const r=await fetch('/api/miniapp/'+path,{method:body?'POST':'GET',headers:{'Content-Type':'application/json'},body:body?JSON.stringify(body):undefined});
  return r.json();
}
async function init(){
  if(TG){TG.ready();TG.expand()}
  applyPrefs();
  bindSeg('segTheme','theme');bindSeg('segMotion','motion');bindSeg('segFont','font');
  try{
    state.cfg=await api('config');
    if(state.cfg.default_lang)state.lang=state.cfg.default_lang;
    state.key=state.cfg.default_niche||'food';
    renderConfig();
  }catch(e){toast('Не удалось загрузить настройки')}
  $('#geo').onclick=geo;
  $('#find').onclick=startSearch;
  $('#city').onkeydown=e=>{if(e.key==='Enter')startSearch()};
  $('#again').onclick=()=>{state.hidden=false;show('setup')};
  $('#toggleView').onclick=()=>{state.hidden=!state.hidden;$('#cards').hidden=state.hidden;$('#more').hidden=state.hidden||state.page*5>=state.data.items.length;$('#hiddenNote').hidden=!state.hidden;$('#toggleView').textContent=state.hidden?'📂 Показать':'🙈 Скрыть'};
  $('#csv').onclick=exportCsv;
  $('#more').onclick=()=>{state.page++;renderCards()};
  $('#sheetClose').onclick=()=>{$('#sheet').hidden=true};
  $('#sheet').onclick=e=>{if(e.target.id==='sheet')$('#sheet').hidden=true};
  $('#settingsBtn').onclick=()=>{haptic('medium');$('#settings').hidden=false};
  $('#settingsClose').onclick=()=>{$('#settings').hidden=true};
  $('#settingsDone').onclick=()=>{$('#settings').hidden=true};
  $('#settings').onclick=e=>{if(e.target.id==='settings')$('#settings').hidden=true};
  document.addEventListener('keydown',e=>{if(e.key==='Escape'){$('#sheet').hidden=true;$('#settings').hidden=true}});
  $('#copyText').onclick=()=>{const t=$('#sheetBody').innerText;navigator.clipboard&&navigator.clipboard.writeText(t).then(()=>toast('Скопировано')).catch(()=>toast('Не получилось скопировать'))};
  $('#sendChat').onclick=sendToChat;
}
function renderConfig(){
  const c=state.cfg;
  $('#niches').innerHTML='';
  c.niches.forEach(n=>$('#niches').appendChild(chip(n.label,n.key===state.key,()=>{state.key=n.key;renderConfig()})));
  $('#modes').innerHTML='';
  c.modes.forEach(m=>$('#modes').appendChild(chip(m.label,m.key===state.mode,()=>{state.mode=m.key;renderConfig()})));
  $('#flags').innerHTML='';
  FLAGS.forEach(([k,l])=>$('#flags').appendChild(chip(l+(state.flags.includes(k)?' ✅':''),state.flags.includes(k),()=>{
    state.flags=state.flags.includes(k)?state.flags.replace(k,''):state.flags+k;renderConfig()
  },true)));
}
function geo(){
  if(!navigator.geolocation)return toast('Геолокация недоступна');
  $('#geo').textContent='…';
  navigator.geolocation.getCurrentPosition(p=>{
    state.city=p.coords.latitude.toFixed(4)+','+p.coords.longitude.toFixed(4);
    $('#city').value=state.city;$('#geo').textContent='📍';toast('Координаты подставлены');
  },()=>{$('#geo').textContent='📍';toast('Разрешите геолокацию в браузере')},{timeout:7000});
}
const STEPS=[
  ['1','Геокодируем город и строим область поиска'],
  ['2','Опрашиваем 4 сервера Overpass (могут быть перегружены)'],
  ['3','Параллельно ищем в Photon / Komoot — независимый источник'],
  ['4','Собираем телефоны, адреса и сайты из OpenStreetMap'],
  ['5','Проверяем сайты: HTTPS, телефон, скорость, SEO'],
  ['6','Готовим продающие скрипты для каждой карточки']];
const FACTS=['Ищем там, где конкуренты ещё не успели…','Сайт — не картинка, а заявки и телефон…','Клиент ищет «рядом со мной» — найдём вас первыми…','Пока другие ждут карты, мы уже считаем потенциал…'];
let anim=null;
function startAnim(){
  let i=0,p=4;
  $('#bar').style.width='4%';$('#log').innerHTML='';
  const fact=setInterval(()=>$('#tickerText').textContent=FACTS[Math.floor(Math.random()*FACTS.length)],2600);
  const timer=setInterval(()=>{
    if(i<STEPS.length){
      const [n,txt]=STEPS[i++];
      const d=document.createElement('div');d.className='now';
      d.innerHTML='<b>'+n+'.</b> '+txt;$('#log').appendChild(d);
      [...$('#log').children].forEach(x=>x.classList.remove('now'));
      d.classList.add('now');
      const lg=$('#log');
      if(lg.scrollTo)lg.scrollTo({top:lg.scrollHeight,behavior:scrollBehavior()});else lg.scrollTop=lg.scrollHeight;
      $('#stage').textContent=txt.replace(' (могут быть перегружены)','');
      p=Math.min(88,p+9+Math.random()*7);$('#bar').style.width=p+'%';
    }
  },520);
  anim=()=>{clearInterval(timer);clearInterval(fact);$('#bar').style.width='100%'};
}
async function startSearch(){
  const city=$('#city').value.trim();
  if(!city)return toast('Напишите город');
  state.city=city;state.page=0;state.hidden=false;
  $('#find').disabled=true;show('loading');startAnim();
  try{
    const r=await api('search',{key:state.key,mode:state.mode,city:city,flags:state.flags});
    if(!r.ok)throw new Error(r.error||'Ошибка поиска');
    state.data=r;renderResults();show('results');
    haptic('success');
  }catch(e){toast(e.message||'Сервер карт перегружен — попробуйте ещё раз');show('setup')}
  finally{if(anim){anim();anim=null}$('#find').disabled=false}
}
function esc(s){return String(s||'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))}
function renderResults(){
  const d=state.data;
  $('#summary').innerHTML='<div class="big">'+esc(d.city)+' · '+esc(d.niche_label)+'</div>'+
    '<div>🚫 без сайта: <b data-count="'+d.nosite+'">0</b> &nbsp; 🐌 слабых сайтов: <b data-count="'+d.weak+'">0</b></div>'+
    (d.potential?'<div class="pot">'+esc(d.potential)+'</div>':'')+
    '<div style="color:var(--hint);font-size:12px;margin-top:6px">Найдено: <b data-count="'+d.total+'">0</b>. Нажмите «Скрипты», чтобы получить готовый текст для продажи.</div>';
  animateNums($('#summary'));
  $('#cards').innerHTML='';renderCards();
}
function renderCards(){
  const d=state.data,items=d.items,from=state.page*5,part=items.slice(from,from+5);
  part.forEach((it,idx)=>{
    const i=from+idx,el=document.createElement('div');
    el.className='card'+(it.kind==='weak'?' weak':'');
    el.style.animationDelay=(idx*75)+'ms';
    const badge=it.kind==='weak'?'🔴 '+it.score+'/100':'🚫 НЕТ САЙТА';
    const issues=(it.issues||[]).map(x=>esc(x[1])).join('; ');
    const pitch=(it.pitch||[]).join(', ');
    el.innerHTML='<span class="badge">'+badge+'</span><h3>'+esc(it.name)+'</h3>'+
      (it.site?'<div class="meta">🌐 '+esc(it.site.replace(/^https?:\/\//,'').replace(/\/$/,''))+'</div>':'')+
      (it.addr?'<div class="meta">📍 '+esc(it.addr)+'</div>':'')+
      '<div class="meta">📞 '+(it.phone?esc(it.phone):'<span style="opacity:.6">телефона нет</span>')+'</div>'+
      (issues?'<div class="issues">⚠ '+issues+'</div>':'')+
      (pitch?'<div class="pitch">💡 Предложи: '+esc(pitch)+'</div>':'')+
      '<div class="card-actions">'+
      '<button class="mini main" data-act="scripts" data-i="'+i+'">✍️ Скрипты</button>'+
      '<a class="mini" href="https://www.google.com/maps/search/?api=1&query='+encodeURIComponent(it.lat+','+it.lon)+'" target="_blank">📍 Карта</a>'+
      (it.phone&&it.phone.startsWith('+')?'<a class="mini" href="https://wa.me/'+it.phone.replace(/\D/g,'')+'" target="_blank">💬 WhatsApp</a>':'')+
      '</div>';
    el.querySelector('[data-act=scripts]').onclick=()=>openScripts(i);
    $('#cards').appendChild(el);
  });
  $('#more').hidden=from+5>=items.length||state.hidden;
  $('#more').textContent='Показать ещё ↓ (осталось '+(items.length-from-5)+')';
}
function exportCsv(){
  const it=state.data.items;
  if(!it.length)return toast('Нечего выгружать');
  const q=v=>'"'+String(v||'').replace(/"/g,'""')+'"';
  const rows=[['Название','Сайт','Телефон','Email','Адрес','Тип','Штраф','Проблемы','Широта','Долгота']];
  it.forEach(x=>rows.push([x.name,x.site,x.phone,x.email,x.addr,x.kind,x.score,(x.issues||[]).map(y=>y[1]).join('; '),x.lat,x.lon]));
  const csv='\ufeff'+rows.map(r=>r.map(q).join(';')).join('\n');
  const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));
  a.download='leads_'+state.city.replace(/[^\w\u0400-\u04ff]+/g,'_')+'.csv';a.click();
  URL.revokeObjectURL(a.href);toast('CSV сохранён');
}
const TABS=[['dm','📱 Директ'],['call','📞 Звонок'],['em','✉️ Email'],['fu','🔁 Follow-up'],
            ['obj','🛡 Возражения'],['plan','📋 План'],['close','🤝 Закрыть сделку']];
async function openScripts(idx){
  state.lead=state.data.items[idx];state.tab='dm';
  $('#sheetTitle').textContent=state.lead.name;
  $('#tabs').innerHTML='';
  TABS.forEach(([k,l])=>{const b=document.createElement('button');b.className='tab'+(k===state.tab?' on':'');b.textContent=l;
    b.onclick=()=>{state.tab=k;[...$('#tabs').children].forEach(x=>x.classList.remove('on'));b.classList.add('on');loadScripts()};$('#tabs').appendChild(b)});
  $('#sheet').hidden=false;haptic('medium');await loadScripts();
}
async function loadScripts(){
  const l=state.lead;if(!l)return;
  $('#sheetBody').innerHTML='<div style="color:var(--hint);font-size:12px">Готовлю текст…</div>';
  try{
    const r=await api('scripts',{kind:l.kind,issues:l.issues||[],lang:state.lang,name:l.name,domain:(l.site||'').replace(/^https?:\/\//,''),site:l.site,phone:l.phone,price:state.cfg.price||''});
    let html='<div class="langs">'+r.langs.map(x=>'<button data-l="'+x.k+'" class="'+(x.k===state.lang?'on':'')+'">'+x.label+'</button>').join('')+'</div>';
    html+=r.body[state.tab]||'';
    $('#sheetBody').innerHTML=html;
    $('#sheetBody').querySelectorAll('[data-l]').forEach(b=>b.onclick=()=>{state.lang=b.dataset.l;loadScripts()});
  }catch(e){$('#sheetBody').innerHTML='<p>Не удалось загрузить скрипты.</p>'}
}
function sendToChat(){
  if(!state.lead)return;
  if(TG){TG.sendData(JSON.stringify({name:state.lead.name,kind:state.lead.kind,issues:state.lead.issues,site:state.lead.site,lang:state.lang}));TG.close()}
  else toast('Откройте мини-приложение из бота, чтобы отправить в чат');
}
init();
</script>
</body>
</html>
"""
