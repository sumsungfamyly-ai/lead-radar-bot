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
  --bg:#0a101a; --bg2:#101827; --card:rgba(20,30,46,.74); --soft:rgba(42,56,78,.52);
  --text:#f1f6ff; --hint:#a8bad3; --accent:#7ab0ff; --accent2:#a58bff;
  --accent-text:#fff; --line:rgba(170,200,255,.13);
  --green:#61d8b0; --red:#ff9494; --yellow:#f2c766;
  --shadow:0 20px 56px rgba(0,0,0,.34), inset 0 1px 0 rgba(255,255,255,.05);
  --glow:rgba(122,176,255,.30); --glass:blur(20px) saturate(145%);
}
:root[data-theme="light"]{
  color-scheme:light;
  --bg:#eef3fb; --bg2:#e6edf8; --card:rgba(255,255,255,.78); --soft:rgba(255,255,255,.65);
  --text:#182235; --hint:#5f7088; --accent:#3f7ae0; --accent2:#7a5af8;
  --accent-text:#fff; --line:rgba(40,60,100,.10);
  --green:#17956e; --red:#de5f5f; --yellow:#b88308;
  --shadow:0 18px 40px rgba(40,60,100,.12), inset 0 1px 0 rgba(255,255,255,.8);
  --glow:rgba(63,122,224,.18); --glass:blur(16px) saturate(130%);
}
:root[data-motion="calm"] *{animation-duration:.001ms!important;animation-iteration-count:1!important;transition-duration:.001ms!important}
:root[data-font="large"] body{font-size:17px}
:root[data-font="large"] .hero-sub,
:root[data-font="large"] .meta,
:root[data-font="large"] .issues,
:root[data-font="large"] .pitch{font-size:15px}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html{scroll-behavior:smooth}
[hidden]{display:none!important}
body{margin:0;color:var(--text);
  font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  padding:0 14px calc(34px + env(safe-area-inset-bottom));
  background:radial-gradient(1200px 700px at 10% -10%,rgba(110,168,255,.18),transparent 50%),
             radial-gradient(900px 600px at 100% 0%,rgba(155,123,255,.14),transparent 45%),
             linear-gradient(180deg,var(--bg2),var(--bg));
  transition:background-color .35s ease,color .35s ease;-webkit-font-smoothing:antialiased;overflow-x:hidden}
body:before,body:after{content:"";position:fixed;border-radius:50%;pointer-events:none;z-index:-1;filter:blur(2px)}
body:before{width:320px;height:320px;top:-120px;right:-80px;background:radial-gradient(circle,rgba(110,168,255,.22),transparent 68%);animation:orbA 14s ease-in-out infinite alternate}
body:after{width:260px;height:260px;bottom:10%;left:-100px;background:radial-gradient(circle,rgba(155,123,255,.16),transparent 70%);animation:orbB 16s ease-in-out infinite alternate}
@keyframes orbA{to{transform:translate(-30px,40px) scale(1.08)}}
@keyframes orbB{to{transform:translate(40px,-30px) scale(1.12)}}
body,button,input,select,.card,.chip,.summary,.sheet-inner,.tab,.mini,.icon-btn,
.hero-stats span,.bar,.bar i,.log,.log div,#toast,.seg,.seg button,#map,.pin,.f-count,.f-lead,.hist-item{
  transition:background-color .3s ease,color .3s ease,border-color .3s ease,
             box-shadow .3s ease,transform .3s cubic-bezier(.2,.8,.2,1),opacity .3s ease}
button,input{font:inherit}
section:not([hidden]){animation:screenIn .38s ease both}
@keyframes screenIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
@media (hover:hover){
  .chip:hover,.mini:hover,.tab:hover,.icon-btn:hover,.seg button:not(.on):hover,
  #more:hover,.close-x:hover,.hist-item:hover{transform:translateY(-2px);box-shadow:var(--shadow)}
}
#app{max-width:620px;margin:0 auto;perspective:1200px}
.hero{padding:26px 4px 18px;position:relative;overflow:visible}
.hero-sky{position:absolute;inset:-40px -20px auto -20px;height:280px;pointer-events:none;z-index:-1;
  background:radial-gradient(ellipse 80% 60% at 50% 0%,rgba(120,170,255,.22),transparent 65%),
             radial-gradient(ellipse 45% 40% at 20% 10%,rgba(160,120,255,.18),transparent 60%),
             radial-gradient(ellipse 35% 35% at 80% 15%,rgba(90,200,255,.12),transparent 60%)}
.hero-sky:after{content:"";position:absolute;left:10%;top:18px;width:140px;height:44px;border-radius:50px;
  background:rgba(255,255,255,.05);filter:blur(2px);box-shadow:180px 30px 0 20px rgba(255,255,255,.04),80px 58px 0 10px rgba(255,255,255,.03);animation:cloudDrift 18s ease-in-out infinite alternate}
@keyframes cloudDrift{to{transform:translateX(20px)}}
.brand{display:flex;align-items:center;gap:10px;font-weight:900;letter-spacing:1px;font-size:34px;line-height:1;padding-right:92px;
  background:linear-gradient(120deg,rgba(255,255,255,.95),rgba(122,176,255,.95),rgba(165,139,255,.95),rgba(255,255,255,.9));
  background-size:220% 220%;-webkit-background-clip:text;background-clip:text;color:transparent;
  filter:drop-shadow(0 8px 28px rgba(122,176,255,.25));animation:brandShift 8s ease infinite;opacity:.96}
.brand .dot{width:12px;height:12px;border-radius:50%;background:var(--green);box-shadow:0 0 0 6px var(--glow);animation:softPulse 2.6s ease-in-out infinite}
@keyframes brandShift{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
@keyframes softPulse{50%{box-shadow:0 0 0 10px transparent}}
.icon-btn{position:absolute;right:4px;top:24px;width:44px;height:44px;border-radius:14px;border:1px solid var(--line);
  background:var(--card);color:var(--text);font-size:18px;cursor:pointer;display:grid;place-items:center;box-shadow:var(--shadow);backdrop-filter:var(--glass)}
.icon-btn.alt{right:54px;font-size:16px}
.icon-btn:active{transform:scale(.94)}
.hero-sub{color:var(--hint);margin-top:10px;font-size:14px;max-width:520px;font-family:ui-rounded,"Segoe UI",system-ui,sans-serif}
.lang-clouds{display:flex;flex-wrap:wrap;gap:10px;margin-top:16px;position:relative;min-height:52px}
.lang-cloud{padding:10px 14px;border-radius:16px;border:1px solid var(--line);background:rgba(255,255,255,.06);
  backdrop-filter:blur(10px);color:var(--text);font-size:12px;font-weight:650;box-shadow:0 10px 24px rgba(0,0,0,.12);
  animation:cloudFloat 6s ease-in-out infinite}
.lang-cloud:nth-child(2){animation-delay:.6s}.lang-cloud:nth-child(3){animation-delay:1.2s}
.lang-cloud:nth-child(4){animation-delay:1.8s}.lang-cloud:nth-child(5){animation-delay:2.4s}.lang-cloud:nth-child(6){animation-delay:3s}
@keyframes cloudFloat{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}
.hero-stats{display:flex;gap:8px;margin-top:16px;flex-wrap:wrap}
.hero-stats span{background:var(--card);border:1px solid var(--line);border-radius:999px;
  padding:7px 12px;font-size:11px;color:var(--hint);box-shadow:0 2px 10px rgba(0,0,0,.04);animation:statFloat 7s ease-in-out infinite}
.hero-stats span:nth-child(2){animation-delay:.8s}.hero-stats span:nth-child(3){animation-delay:1.6s}
@keyframes statFloat{0%,100%{transform:translateY(0)}50%{transform:translateY(-3px)}}
.hero-stats b{color:var(--text)}
.sec{margin:20px 0 9px;font-size:12px;font-weight:700;letter-spacing:.7px;text-transform:uppercase;color:var(--hint)}
.chips{display:flex;flex-wrap:wrap;gap:8px}
.chip{border:1px solid var(--line);background:var(--card);backdrop-filter:var(--glass);-webkit-backdrop-filter:var(--glass);
  color:var(--text);border-radius:16px;padding:12px 14px;font-size:14px;cursor:pointer;user-select:none;
  box-shadow:0 6px 18px rgba(0,0,0,.08),inset 0 1px 0 rgba(255,255,255,.05);transition:transform .2s ease,box-shadow .25s ease}
.chip:active{transform:scale(.96)}
.chip.on{background:linear-gradient(135deg,var(--accent),var(--accent2));color:var(--accent-text);border-color:transparent;
  box-shadow:0 12px 28px var(--glow),inset 0 1px 0 rgba(255,255,255,.25);transform:translateY(-2px)}
.chip.sm{padding:9px 11px;font-size:12px}
.city-row{display:flex;gap:8px}
#city{flex:1;min-width:0;background:var(--card);border:1px solid var(--line);color:var(--text);
  border-radius:13px;padding:14px;outline:none}
#city:focus{border-color:var(--accent);box-shadow:0 0 0 3px var(--glow)}
#geo{width:50px;border-radius:13px;border:1px solid var(--line);background:var(--card);color:var(--text);cursor:pointer}
#geo:active{transform:scale(.95)}
.primary{width:100%;margin-top:18px;border:0;border-radius:18px;padding:18px;cursor:pointer;position:relative;overflow:hidden;
  background:linear-gradient(135deg,var(--accent),var(--accent2));background-size:180% 100%;
  color:#fff;font-weight:780;font-size:17px;letter-spacing:.2px;
  box-shadow:0 16px 34px var(--glow),inset 0 1px 0 rgba(255,255,255,.28);
  transition:transform .25s cubic-bezier(.2,.8,.2,1),box-shadow .3s ease,background-position .6s ease,opacity .3s ease}
.primary:before{content:"";position:absolute;inset:0;background:linear-gradient(110deg,transparent 30%,rgba(255,255,255,.22) 50%,transparent 70%);transform:translateX(-120%);transition:transform .7s ease}
.primary:hover{background-position:100% 0;box-shadow:0 20px 40px var(--glow);transform:translateY(-3px) scale(1.01)}
.primary:hover:before{transform:translateX(120%)}
.primary:active{transform:translateY(1px) scale(.995)}
.primary:disabled{opacity:.6;box-shadow:none;transform:none}
.hint{color:var(--hint);font-size:12px;text-align:center;margin-top:10px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.card{background:var(--card);backdrop-filter:var(--glass);-webkit-backdrop-filter:var(--glass);
  border:1px solid var(--line);border-radius:20px;padding:16px;margin-bottom:12px;
  position:relative;overflow:hidden;box-shadow:var(--shadow);
  transform-style:preserve-3d;animation:rise .45s cubic-bezier(.2,.8,.2,1) both}
.card:after{content:"";position:absolute;inset:0;background:linear-gradient(135deg,rgba(255,255,255,.08),transparent 40%,transparent 60%,rgba(255,255,255,.03));pointer-events:none}
.card:hover{transform:translateY(-5px) rotateX(1.5deg);box-shadow:0 24px 50px rgba(0,0,0,.22),0 0 0 1px var(--glow)}
.card:before{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--green)}
.card.weak:before{background:var(--yellow)}
@keyframes rise{from{opacity:0;transform:translateY(16px) scale(.985)}to{opacity:1;transform:none}}
.card h3{margin:0 0 8px;font-size:19px;line-height:1.3;padding-right:8px}
.badge{position:absolute;right:13px;top:14px;font-size:10px;font-weight:700;border-radius:999px;
  padding:4px 8px;background:rgba(79,208,168,.14);background:color-mix(in srgb,var(--green) 14%,transparent);color:var(--green)}
.card.weak .badge{background:rgba(231,196,119,.14);background:color-mix(in srgb,var(--yellow) 15%,transparent);color:var(--yellow)}
.meta{color:var(--hint);font-size:14px;margin:4px 0;line-height:1.5}
.issues{font-size:13px;color:var(--yellow);margin-top:8px;line-height:1.45}
.pitch{font-size:13px;color:var(--hint);margin-top:8px;font-style:italic;line-height:1.45}
.card-actions{display:flex;gap:7px;flex-wrap:wrap;margin-top:12px}
.mini{border:1px solid var(--line);background:rgba(255,255,255,.03);color:var(--text);border-radius:12px;
  padding:10px 13px;font-size:13px;cursor:pointer;text-decoration:none;display:inline-flex;align-items:center;gap:5px;
  transition:transform .2s ease,box-shadow .25s ease,background .25s ease}
.mini.main{background:linear-gradient(135deg,var(--accent),var(--accent2));border-color:transparent;color:#fff;font-weight:700;box-shadow:0 8px 20px var(--glow)}
.summary{background:linear-gradient(135deg,var(--glow),rgba(155,123,255,.08),transparent);
  backdrop-filter:var(--glass);-webkit-backdrop-filter:var(--glass);
  border:1px solid var(--line);border-radius:20px;padding:18px;margin-top:14px;box-shadow:var(--shadow);
  position:relative;overflow:hidden;animation:rise .45s .08s ease both}
.summary:before{content:"";position:absolute;width:180px;height:180px;right:-60px;top:-80px;border-radius:50%;
  background:radial-gradient(circle,var(--glow),transparent 70%);pointer-events:none}
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
.sheet-inner{background:linear-gradient(180deg,var(--bg2),var(--bg));backdrop-filter:var(--glass);-webkit-backdrop-filter:var(--glass);
  width:100%;max-width:620px;max-height:88vh;border-radius:24px 24px 0 0;
  border:1px solid var(--line);box-shadow:0 -20px 60px rgba(0,0,0,.25),inset 0 1px 0 rgba(255,255,255,.06);
  display:flex;flex-direction:column;overflow:hidden;animation:up .34s cubic-bezier(.2,.8,.2,1) both}
@keyframes up{from{transform:translateY(100%);opacity:.5}to{transform:none;opacity:1}}
.sheet-head{display:flex;align-items:center;justify-content:space-between;padding:16px 16px 10px}
.sheet-head b{font-size:16px}
.close-x{border:0;background:var(--card);color:var(--text);border-radius:50%;width:32px;height:32px;cursor:pointer}
.tabs{display:flex;gap:8px;overflow-x:auto;padding:4px 14px 10px;scrollbar-width:none;align-items:center;flex:0 0 auto;width:100%;box-sizing:border-box;-webkit-overflow-scrolling:touch}
.tabs::-webkit-scrollbar{display:none}
.tab{flex:0 0 auto;display:inline-flex;align-items:center;justify-content:center;gap:4px;
  white-space:nowrap;border:1px solid var(--line);background:rgba(255,255,255,.02);color:var(--hint);
  border-radius:999px;padding:8px 12px;font-size:12px;line-height:1.2;min-height:36px;cursor:pointer;box-sizing:border-box;
  transition:transform .2s ease,box-shadow .25s ease,background .25s ease,color .25s ease,border-color .25s ease}
.tab:hover{transform:translateY(-1px);color:var(--text)}
.tab.on{background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff;border-color:transparent;box-shadow:0 8px 20px var(--glow)}
.sheet-body{padding:4px 16px 18px;overflow-y:auto;font-size:14px;flex:1;min-height:0}
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
.setting{padding:13px 0;border-bottom:1px solid var(--line);animation:softBob 8s ease-in-out infinite}
.setting:last-of-type{border-bottom:0}
@keyframes softBob{0%,100%{transform:translateY(0)}50%{transform:translateY(-2px)}}
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
/* --- фильтры результатов --- */
.filter-row{display:flex;align-items:center;gap:7px;flex-wrap:wrap;margin:12px 0 14px;padding:9px 10px;
  background:var(--bg2);border:1px solid var(--line);border-radius:15px}
.filter-lab{font-size:10px;letter-spacing:.7px;text-transform:uppercase;color:var(--hint);margin-right:2px}
.filter-row .chip{padding:7px 10px;font-size:11px;border-radius:10px;background:var(--card)}
/* --- карта --- */
#map{position:relative;height:340px;border:1px solid var(--line);border-radius:17px;overflow:hidden;margin-bottom:12px;
  background-color:var(--bg2);
  background-image:linear-gradient(var(--line) 1px,transparent 1px),
                   linear-gradient(90deg,var(--line) 1px,transparent 1px),
                   radial-gradient(circle at 50% 45%,var(--glow),transparent 72%);
  background-size:34px 34px,34px 34px,100% 100%;box-shadow:var(--shadow);animation:rise .4s ease both}
.map-label{position:absolute;left:12px;top:10px;z-index:2;font-size:11px;letter-spacing:.7px;
  text-transform:uppercase;color:var(--hint)}
.map-legend{position:absolute;left:10px;bottom:10px;z-index:2;display:flex;gap:11px;flex-wrap:wrap;
  background:var(--card);border:1px solid var(--line);border-radius:11px;padding:6px 9px;font-size:10px;color:var(--hint)}
.map-legend i{display:inline-block;width:7px;height:7px;border-radius:50%;margin-right:4px;background:var(--green)}
.map-legend .weak i{background:var(--yellow)}
.map-legend .ok i{background:var(--accent)}
.pin{position:absolute;z-index:1;width:18px;height:18px;padding:0;border-radius:50%;border:2px solid var(--card);
  background:var(--green);cursor:pointer;box-shadow:0 3px 10px rgba(0,0,0,.28);
  transform:translate(-50%,-50%);animation:pinPulse 2.6s ease-in-out infinite}
.pin.weak{background:var(--yellow);animation-delay:.5s}
.pin.ok{background:var(--accent);animation-delay:1s}
.pin:before{content:"";position:absolute;inset:-7px;border-radius:50%;border:1px solid var(--green);
  opacity:.6;animation:pinWave 2.6s ease-out infinite}
.pin.weak:before{border-color:var(--yellow)}
.pin.ok:before{border-color:var(--accent)}
.pin:after{content:attr(data-name);position:absolute;left:50%;bottom:calc(100% + 9px);
  transform:translateX(-50%) translateY(4px);max-width:190px;overflow:hidden;text-overflow:ellipsis;
  white-space:nowrap;background:var(--card);color:var(--text);border:1px solid var(--line);
  border-radius:9px;padding:5px 8px;font-size:11px;box-shadow:var(--shadow);
  opacity:0;pointer-events:none;transition:opacity .2s ease,transform .2s ease}
.pin:hover:after,.pin:focus:after{opacity:1;transform:translateX(-50%)}
@keyframes pinPulse{0%,100%{transform:translate(-50%,-50%) scale(1)}50%{transform:translate(-50%,-50%) scale(1.14)}}
@keyframes pinWave{0%{transform:scale(.55);opacity:.7}100%{transform:scale(1.6);opacity:0}}
.map-empty{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:80%;
  text-align:center;color:var(--hint);font-size:13px}
/* --- статус и бейдж «новый» в карточке --- */
.card-toprow{display:flex;align-items:center;gap:8px;margin:8px 0 2px}
.badge.new-badge{position:static;display:inline-flex;align-items:center;flex:0 0 auto;
  background:rgba(106,161,255,.14);background:color-mix(in srgb,var(--accent) 15%,transparent);
  color:var(--accent);animation:newIn .45s cubic-bezier(.2,.8,.2,1) both}
@keyframes newIn{from{opacity:0;transform:scale(.8) translateY(-4px)}to{opacity:1;transform:none}}
.statusSel{margin-left:auto;max-width:142px;border:1px solid var(--line);background:var(--soft);
  color:var(--text);border-radius:9px;padding:5px 8px;font-size:11px;cursor:pointer;outline:none}
.statusSel:focus{border-color:var(--accent)}
.quick-row{display:flex;gap:6px;flex-wrap:wrap;margin-top:10px}
.qbtn{border:1px solid var(--line);background:rgba(255,255,255,.03);color:var(--text);border-radius:999px;padding:10px 14px;font-size:13px;cursor:pointer;transition:.2s ease;min-height:42px}
.qbtn:hover{transform:translateY(-1px)}
.qbtn.on{background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff;border-color:transparent;box-shadow:0 6px 16px var(--glow)}
.qbtn.danger.on{background:linear-gradient(135deg,#ff7a7a,#d94f4f)}
.card.flash{outline:2px solid var(--accent);outline-offset:3px;box-shadow:0 0 0 7px var(--glow)}
.meta a{color:var(--accent);text-decoration:none;margin-right:9px;border-bottom:1px dotted var(--accent)}
.audit-line{color:var(--hint)}
/* --- история и воронка --- */
.list-empty{text-align:center;color:var(--hint);padding:36px 12px;font-size:13px}
.list-empty b{display:block;color:var(--text);font-size:15px;margin-bottom:6px}
.hist-item{display:block;width:100%;text-align:left;border:1px solid var(--line);background:var(--card);
  color:var(--text);border-radius:13px;padding:12px 14px;margin:9px 0;cursor:pointer;animation:softBob 9s ease-in-out infinite}
.hist-item b{display:block;font-size:14px;padding-right:70px}
.hist-item span{display:block;font-size:12px;color:var(--hint);margin-top:3px}
.hist-item em{float:right;font-style:normal;font-size:11px;color:var(--accent);margin-top:2px}
.funnel-counts{display:flex;flex-wrap:wrap;gap:7px;margin:6px 0 12px}
.f-count{display:inline-flex;align-items:center;gap:5px;border:1px solid var(--line);background:var(--soft);
  border-radius:999px;padding:6px 10px;font-size:11px;color:var(--hint)}
.f-count b{color:var(--sc,var(--accent));font-size:13px}
.f-count[data-s="new"]{--sc:var(--accent)}
.f-count[data-s="contacted"]{--sc:var(--accent2)}
.f-count[data-s="replied"]{--sc:var(--yellow)}
.f-count[data-s="meeting"]{--sc:var(--green)}
.f-count[data-s="deal"]{--sc:var(--green)}
.f-count[data-s="lost"]{--sc:var(--red)}
.f-lead{display:flex;align-items:center;gap:9px;background:var(--card);border:1px solid var(--line);
  border-radius:11px;padding:9px 11px;margin:6px 0;animation:softBob 10s ease-in-out infinite}
.f-lead .f-name{flex:1;min-width:0;font-size:12px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.f-lead .f-name small{display:block;color:var(--hint);font-size:10px}
.f-lead .statusSel{margin-left:0;flex:0 0 auto}
/* splash */
#splash{position:fixed;inset:0;z-index:100;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:14px;
  background:radial-gradient(ellipse 80% 50% at 50% 0%,rgba(122,176,255,.25),transparent 60%),linear-gradient(180deg,#101a2b,#0a101a);
  transition:opacity .55s ease,visibility .55s ease}
#splash.hide{opacity:0;visibility:hidden}
.splash-logo{font-size:44px;font-weight:900;letter-spacing:1.5px;
  background:linear-gradient(120deg,#fff,#7ab0ff,#a58bff,#fff);background-size:220% 220%;
  -webkit-background-clip:text;background-clip:text;color:transparent;animation:brandShift 5s ease infinite}
.splash-sub{color:#a8bad3;font-size:14px;font-family:ui-rounded,"Segoe UI",system-ui,sans-serif}
.splash-bar{width:160px;height:4px;border-radius:99px;background:rgba(255,255,255,.1);overflow:hidden}
.splash-bar i{display:block;height:100%;width:40%;background:linear-gradient(90deg,var(--accent),var(--accent2));border-radius:99px;animation:splashLoad 1.2s ease infinite}
@keyframes splashLoad{0%{transform:translateX(-100%)}100%{transform:translateX(260%)}}
</style>
</head>
<body>
<div id="splash"><div class="splash-logo">LEAD RADAR</div><div class="splash-sub">Запускаем мини-приложение…</div><div class="splash-bar"><i></i></div></div>
<div id="app">
  <div class="hero">
    <div class="hero-sky"></div>
    <div class="brand"><span class="dot"></span>LEAD RADAR</div>
    <button class="icon-btn alt" id="funnelBtn" title="Воронка продаж">📊</button>
    <button class="icon-btn" id="settingsBtn" title="Настройки">⚙️</button>
    <div class="hero-sub">Нахожу клиентов, которые уже нужны вашему бизнесу — и даю готовые скрипты продаж на 6 языках.</div>
    <div class="lang-clouds" aria-label="Языки скриптов">
      <span class="lang-cloud">🇷🇺 RU</span><span class="lang-cloud">🇬🇧 EN</span><span class="lang-cloud">🇫🇮 FI</span>
      <span class="lang-cloud">🇪🇪 ET</span><span class="lang-cloud">🇸🇪 SV</span><span class="lang-cloud">🇩🇪 DE</span>
    </div>

  </div>

  <section id="setup">
    <div class="sec">1. Ниши бизнеса <span style="opacity:.7;font-weight:500">(можно выбрать до 4)</span></div>
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
      <button class="mini" id="mapBtn">🗺 Карта</button>
      <button class="mini" id="historyBtn">🕘 История</button>
      <button class="mini" id="csv">📥 Скачать CSV</button>
      <button class="mini" id="again">🔄 Новый поиск</button>
    </div>
    <div class="filter-row" id="filters"></div>
    <div id="map" hidden></div>
    <div id="cards"></div>

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

<div id="historySheet" class="sheet" hidden>
  <div class="sheet-inner">
    <div class="sheet-head"><b>🕘 История поисков</b><button class="close-x" id="historyClose">✕</button></div>
    <div class="sheet-body" id="historyBody"></div>
  </div>
</div>

<div id="funnelSheet" class="sheet" hidden>
  <div class="sheet-inner">
    <div class="sheet-head"><b>📊 Воронка продаж</b><button class="close-x" id="funnelClose">✕</button></div>
    <div class="sheet-body" id="funnelBody"></div>
  </div>
</div>
<div id="toast"></div>

<script>
const $=s=>document.querySelector(s);
const TG=window.Telegram&&window.Telegram.WebApp;
const state={cfg:null,keys:['barber'],key:'barber',mode:'n',flags:'',city:'',data:null,page:0,lang:'ru',lead:null,tab:'dm',hidden:false,
  view:'list',filters:{new:false,phone:false,nosite:false,hot:false},new_ids:[],statuses:null,visible:[],counts:{},funnelLeads:{}};
const FLAGS=[['p','📞 С телефоном'],['e','✉️ С email'],['c','🏪 Без сетей']];
const DEFAULT_STATUSES=[['new','Новый'],['contacted','Связались'],['replied','Ответили'],['meeting','Встреча'],['deal','Сделка'],['lost','Потерян']];
const FILTERS=[['new','✨ Только новые'],['phone','📞 С телефоном'],['nosite','🚫 Без сайта'],['hot','🔥 Сначала горячие']];
const warned=new Set();
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
function warnOnce(key,msg){if(warned.has(key))return;warned.add(key);toast(msg)}
function normalizeStatuses(arr){
  if(!Array.isArray(arr))return [];
  return arr.map(x=>Array.isArray(x)?x:[x&&x.key,x&&x.label])
    .filter(x=>x&&x[0]).map(x=>[String(x[0]),String(x[1]||x[0])]);
}
function statuses(){return (state.statuses&&state.statuses.length)?state.statuses:DEFAULT_STATUSES}
function statusKeys(){return statuses().map(x=>x[0])}
function statusOptions(cur){return statuses().map(([k,l])=>'<option value="'+esc(k)+'"'+(k===cur?' selected':'')+'>'+esc(l)+'</option>').join('')}
function statusLabel(k){const f=statuses().find(x=>x[0]===k);return f?f[1]:k}
function itemKey(it){return (it&&it.id)||((it&&it.name||'')+'|'+(it&&it.site||''))}
function isNewItem(it){
  if(!it)return false;
  if(it.is_new)return true;
  const ids=state.new_ids||[];
  return ids.indexOf(it.id)>=0||ids.indexOf(itemKey(it))>=0;
}
function issueText(x){return Array.isArray(x)?String(x[1]||''):String(x||'')}
function hotRank(x){return !x.site?0:(x.phone?1:2)}
function visibleItems(){
  if(!state.data||!Array.isArray(state.data.items))return [];
  let a=state.data.items.slice(),f=state.filters||{};
  if(f.new)a=a.filter(isNewItem);
  if(f.phone)a=a.filter(x=>!!x.phone);
  if(f.nosite)a=a.filter(x=>!x.site);
  if(f.hot)a.sort((x,y)=>hotRank(x)-hotRank(y)||(+y.score||0)-(+x.score||0));
  return a;
}
function buildFilters(){
  const box=$('#filters');if(!box)return;box.innerHTML='';
  const lab=document.createElement('span');lab.className='filter-lab';lab.textContent='Фильтр';box.appendChild(lab);
  FILTERS.forEach(([k,l])=>{
    const b=chip(l,!!state.filters[k],()=>{
      state.filters[k]=!state.filters[k];
      b.classList.toggle('on',state.filters[k]);
      state.page=0;renderCards();renderMap();applyView();
    },true);
    b.dataset.f=k;box.appendChild(b);
  });
}
function renderFilters(){
  const box=$('#filters');if(!box)return;
  [...box.querySelectorAll('[data-f]')].forEach(b=>b.classList.toggle('on',!!state.filters[b.dataset.f]));
}
function applyView(){
  const mapOn=state.view==='map',total=visibleItems().length;
  const f=$('#filters');if(f)f.hidden=!!state.hidden;
  $('#map').hidden=state.hidden||!mapOn;
  $('#cards').hidden=state.hidden||mapOn;
  const hn=$('#hiddenNote'); if(hn) hn.hidden=!state.hidden;
  $('#more').hidden=state.hidden||mapOn||state.page*5>=total;
  const mb=$('#mapBtn');if(mb)mb.textContent=mapOn?'📋 Список':'🗺 Карта';
  if(mapOn&&!state.hidden)renderMap();
}
function renderMap(){
  const box=$('#map');if(!box)return;
  const items=visibleItems();
  let html='<div class="map-label">Карта · '+items.length+' точек</div>';
  if(!items.length){box.innerHTML=html+'<div class="map-empty">Нет точек — измените фильтры или выполните поиск</div>';return}
  const pts=items.map((it,i)=>({it:it,i:i,lat:Number(it.lat),lon:Number(it.lon)}))
    .filter(p=>isFinite(p.lat)&&isFinite(p.lon));
  if(!pts.length){box.innerHTML=html+'<div class="map-empty">У результатов нет координат</div>';return}
  html='<div class="map-label">Карта · '+pts.length+' точек</div>';
  const lats=pts.map(p=>p.lat),lons=pts.map(p=>p.lon);
  const minLa=Math.min.apply(null,lats),maxLa=Math.max.apply(null,lats);
  const minLo=Math.min.apply(null,lons),maxLo=Math.max.apply(null,lons);
  const n=pts.length;
  const px=p=>8+((maxLo>minLo)?((p.lon-minLo)/(maxLo-minLo)):((p.i+0.5)/n))*84;
  const py=p=>8+((maxLa>minLa)?((maxLa-p.lat)/(maxLa-minLa)):((p.i+0.5)/n))*84;
  pts.forEach(p=>{
    const cls=p.it.kind==='weak'?'weak':(p.it.site?'ok':'');
    html+='<button class="pin '+cls+'" style="left:'+px(p).toFixed(2)+'%;top:'+py(p).toFixed(2)+'%"'+
      ' data-i="'+p.i+'" data-name="'+esc(p.it.name||'Без названия')+'" title="'+esc(p.it.name||'')+'"></button>';
  });
  html+='<div class="map-legend"><span><i></i> без сайта</span><span class="weak"><i></i> слабый сайт</span><span class="ok"><i></i> сайт ок</span></div>';
  box.innerHTML=html;
  box.querySelectorAll('.pin').forEach(b=>b.onclick=()=>focusCard(+b.dataset.i));
}
function focusCard(i){
  state.view='list';state.hidden=false;state.page=Math.floor(i/5);
  renderCards();applyView();
  requestAnimationFrame(()=>{
    const el=$('#cards').children[i-state.page*5];
    if(!el)return;
    el.classList.add('flash');
    try{el.scrollIntoView({behavior:scrollBehavior(),block:'center'})}catch(e){el.scrollIntoView()}
    setTimeout(()=>el.classList.remove('flash'),1700);
  });
}
function auditLine(a){
  if(!a||typeof a!=='object')return '';
  const p=[];
  if(a.site_ok===true)p.push('доступен');else if(a.site_ok===false)p.push('недоступен');
  if(a.https===true)p.push('HTTPS');else if(a.https===false)p.push('без HTTPS');
  if(a.phone_on_site===true)p.push('телефон на сайте');
  if(a.mobile===true)p.push('мобильная версия');
  if(a.load_s!==undefined&&a.load_s!==null&&a.load_s!=='')p.push('загрузка '+a.load_s+' c');
  const iss=(Array.isArray(a.issues)?a.issues:[]).map(issueText).filter(Boolean).join('; ');
  const txt=[p.join(' · '),iss].filter(Boolean).join(' — ');
  return txt?'<div class="issues audit-line">🌐 проверка сайта: '+esc(txt)+'</div>':'';
}
function relDate(ts){
  if(!ts&&ts!==0)return '';
  let t=ts;
  if(typeof t==='string')t=Date.parse(t);
  else if(t<1e12)t=t*1000;
  if(!isFinite(t))return '';
  const m=Math.floor(Math.max(0,Date.now()-t)/60000);
  if(m<1)return 'только что';
  if(m<60)return m+' мин назад';
  const h=Math.floor(m/60);if(h<24)return h+' ч назад';
  const d=Math.floor(h/24);if(d<30)return d+' дн назад';
  try{return new Date(t).toLocaleDateString('ru-RU')}catch(e){return ''}
}
async function changeStatus(id,name,site,value,sel,after){
  const it=(state.data&&state.data.items||[]).find(x=>itemKey(x)===id);
  const old=sel?(sel.dataset.prev||sel.value):(it&&it.status||'new');
  if(sel)sel.disabled=true;
  try{
    const r=await api('status',{id:id,name:name||'',site:site||'',status:value});
    if(!r||!r.ok)throw new Error('bad');
    const final=r.status||value;
    if(it)it.status=final;
    if(r.counts&&Object.keys(r.counts).length)state.counts=r.counts;
    if(sel){sel.dataset.prev=final;sel.value=final}
    document.querySelectorAll('[data-qid="'+CSS.escape(String(id))+'"]').forEach(b=>b.classList.toggle('on',b.dataset.qs===final));
    haptic('success');toast('Статус: '+statusLabel(final));
    if(after)after();
  }catch(e){
    if(sel)sel.value=old;
    warnOnce('status','Не удалось обновить статус');
  }finally{if(sel)sel.disabled=false}
}
async function openHistory(){
  $('#historySheet').hidden=false;haptic('medium');
  $('#historyBody').innerHTML='<div class="list-empty">Загружаю историю…</div>';
  try{
    const r=await api('history');
    if(!r||!r.ok)throw new Error('bad');
    const items=Array.isArray(r.items)?r.items:[];
    if(!items.length){$('#historyBody').innerHTML='<div class="list-empty"><b>Пока нет истории</b>После первого поиска здесь появятся запросы.</div>';return}
    $('#historyBody').innerHTML='';
    items.forEach(h=>{
      const b=document.createElement('button');b.className='hist-item';
      const when=relDate(h.ts);
      b.innerHTML=(when?'<em>'+esc(when)+'</em>':'')+
        '<b>'+esc(h.label||h.q||h.niche||'Поиск')+'</b>'+
        '<span>'+esc(h.city||'—')+' · '+(h.count||0)+' найдено'+(h.new_count?' · '+h.new_count+' новых':'')+'</span>';
      b.onclick=()=>restoreHistory(h);
      $('#historyBody').appendChild(b);
    });
  }catch(e){
    warnOnce('history','История пока недоступна');
    $('#historyBody').innerHTML='<div class="list-empty"><b>История пока недоступна</b>Попробуйте обновить мини-приложение позже.</div>';
  }
}
function restoreHistory(h){
  $('#historySheet').hidden=true;
  if(!h)return;
  const nk=(h.niche_key||h.niche||'').split('+').filter(k=>state.cfg&&state.cfg.niches.some(n=>n.key===k));
  if(nk.length)state.keys=nk.slice(0,4); else if(h.niche && state.cfg){
    const found=state.cfg.niches.find(n=>n.label===h.niche||n.key===h.niche);
    if(found)state.keys=[found.key];
  }
  state.key=(state.keys&&state.keys[0])||state.key;
  state.mode=h.mode||state.mode;state.flags=h.flags||'';
  state.city=h.city||h.q||'';$('#city').value=state.city;
  if(state.cfg)renderConfig();
  startSearch();
}
function openFunnel(){$('#funnelSheet').hidden=false;haptic('medium');loadFunnel()}
async function loadFunnel(quiet){
  if(!quiet)$('#funnelBody').innerHTML='<div class="list-empty">Загружаю воронку…</div>';
  try{
    const r=await api('funnel');
    if(!r||!r.ok)throw new Error('bad');
    state.counts=r.counts||state.counts||{};
    renderFunnel(r);
  }catch(e){
    warnOnce('funnel','Воронка пока недоступна');
    $('#funnelBody').innerHTML='<div class="list-empty"><b>Воронка пока недоступна</b>Попробуйте обновить мини-приложение позже.</div>';
  }
}
function renderFunnel(r){
  const defs=statuses(),counts=r.counts||{},items=Array.isArray(r.items)?r.items:[];
  let html='<div class="funnel-counts">';
  defs.forEach(([k,l])=>{html+='<span class="f-count" data-s="'+esc(k)+'"><b>'+(+counts[k]||0)+'</b>'+esc(l)+'</span>'});
  html+='</div>';
  if(!items.length){$('#funnelBody').innerHTML=html+'<div class="list-empty"><b>Пока нет лидов</b>Статусы появятся здесь после поиска.</div>';return}
  const groups={},known=statusKeys(),leads={};
  items.forEach(x=>{
    const k=known.indexOf(x.status)>=0?x.status:'new';
    (groups[k]=groups[k]||[]).push(x);
    leads[itemKey(x)]=x;
  });
  state.funnelLeads=leads;
  defs.forEach(([k,l])=>{
    const g=groups[k];if(!g||!g.length)return;
    html+='<h4>'+esc(l)+' · '+g.length+'</h4>';
    g.forEach(x=>{
      const id=itemKey(x),site=(x.site||'').replace(/^https?:\/\//,'').replace(/\/$/,'');
      html+='<div class="f-lead"><div class="f-name">'+esc(x.name||'Без названия')+
        (site?'<small>'+esc(site)+'</small>':'')+'</div>'+
        '<select class="statusSel" data-fid="'+esc(id)+'" data-prev="'+esc(k)+'">'+statusOptions(k)+'</select></div>';
    });
  });
  $('#funnelBody').innerHTML=html;
  $('#funnelBody').querySelectorAll('.statusSel').forEach(sel=>{
    sel.onchange=()=>{
      const x=state.funnelLeads[sel.dataset.fid]||{};
      changeStatus(sel.dataset.fid,x.name||'',x.site||'',sel.value,sel,()=>loadFunnel(true));
    };
  });
}

async function api(path,body){
  const r=await fetch('/api/miniapp/'+path,{method:body?'POST':'GET',headers:{'Content-Type':'application/json'},body:body?JSON.stringify(body):undefined});
  return r.json();
}
async function init(){
  if(TG){TG.ready();TG.expand()}
  applyPrefs();
  bindSeg('segTheme','theme');bindSeg('segMotion','motion');bindSeg('segFont','font');
  setTimeout(()=>{const s=$('#splash'); if(s) s.classList.add('hide')}, 650);
  try{
    state.cfg=await api('config');
    if(state.cfg.default_lang)state.lang=state.cfg.default_lang;
    const dn=state.cfg.default_niche||'barber';
    state.key=dn; state.keys=[dn];
    const ss=normalizeStatuses(state.cfg.statuses);
    if(ss.length)state.statuses=ss;
    renderConfig();
  }catch(e){toast('Не удалось загрузить настройки')}
  buildFilters();
  $('#geo').onclick=geo;
  $('#find').onclick=startSearch;
  $('#city').onkeydown=e=>{if(e.key==='Enter')startSearch()};
  $('#again').onclick=()=>{state.hidden=false;show('setup')};
  $('#mapBtn').onclick=()=>{haptic();state.view=state.view==='map'?'list':'map';state.hidden=false;applyView()};
  $('#historyBtn').onclick=openHistory;
  $('#funnelBtn').onclick=openFunnel;
  $('#csv').onclick=exportCsv;
  $('#more').onclick=()=>{state.page++;renderCards();applyView()};
  $('#sheetClose').onclick=()=>{$('#sheet').hidden=true};
  $('#sheet').onclick=e=>{if(e.target.id==='sheet')$('#sheet').hidden=true};
  $('#settingsBtn').onclick=()=>{haptic('medium');$('#settings').hidden=false};
  $('#settingsClose').onclick=()=>{$('#settings').hidden=true};
  $('#settingsDone').onclick=()=>{$('#settings').hidden=true};
  $('#settings').onclick=e=>{if(e.target.id==='settings')$('#settings').hidden=true};
  $('#historyClose').onclick=()=>{$('#historySheet').hidden=true};
  $('#historySheet').onclick=e=>{if(e.target.id==='historySheet')$('#historySheet').hidden=true};
  $('#funnelClose').onclick=()=>{$('#funnelSheet').hidden=true};
  $('#funnelSheet').onclick=e=>{if(e.target.id==='funnelSheet')$('#funnelSheet').hidden=true};
  document.addEventListener('keydown',e=>{if(e.key==='Escape'){
    ['sheet','settings','historySheet','funnelSheet'].forEach(id=>$('#'+id).hidden=true)
  }});
  $('#copyText').onclick=()=>{const t=$('#sheetBody').innerText;navigator.clipboard&&navigator.clipboard.writeText(t).then(()=>toast('Скопировано')).catch(()=>toast('Не получилось скопировать'))};
  $('#sendChat').onclick=sendToChat;
}
function renderConfig(){
  const c=state.cfg;
  if(!Array.isArray(state.keys)||!state.keys.length)state.keys=[state.key||'barber'];
  state.key=state.keys[0];
  $('#niches').innerHTML='';
  c.niches.forEach(n=>{
    const on=state.keys.indexOf(n.key)>=0;
    $('#niches').appendChild(chip(n.label+(on&&state.keys.length>1?' ✓':''),on,()=>{
      const i=state.keys.indexOf(n.key);
      if(i>=0){ if(state.keys.length===1)return toast('Выберите хотя бы одну нишу'); state.keys.splice(i,1); }
      else { if(state.keys.length>=4)return toast('Можно выбрать до 4 ниш за раз'); state.keys.push(n.key); }
      state.key=state.keys[0];renderConfig();
    }));
  });
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
    const keys=(Array.isArray(state.keys)&&state.keys.length)?state.keys:[state.key];
    const r=await api('search',{key:keys[0],keys:keys,mode:state.mode,city:city,flags:state.flags});
    if(!r.ok)throw new Error(r.error||'Ошибка поиска');
    state.data=r;renderResults();show('results');
    if(r.message)toast(r.message);
    else if(r.partial||r.stale)toast(r.stale?'Показаны последние сохранённые результаты':'Часть источников не ответила, показано что нашли');
    haptic('success');
  }catch(e){toast(e.message||'Сервер карт перегружен — попробуйте ещё раз');show('setup')}
  finally{if(anim){anim();anim=null}$('#find').disabled=false}
}
function esc(s){return String(s||'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))}
function renderResults(){
  const d=state.data;
  state.new_ids=Array.isArray(d.new_ids)?d.new_ids:[];
  const fromResp=normalizeStatuses(d.statuses);
  if(fromResp.length)state.statuses=fromResp;
  if(!state.statuses||!state.statuses.length)state.statuses=DEFAULT_STATUSES.slice();
  state.filters={new:false,phone:false,nosite:false,hot:false};
  state.view='list';state.hidden=false;state.page=0;
  renderFilters();
  $('#summary').innerHTML='<div class="big">'+esc(d.city)+' · '+esc(d.niche_label)+'</div>'+
    '<div>🚫 без сайта: <b data-count="'+d.nosite+'">0</b> &nbsp; 🐌 слабых сайтов: <b data-count="'+d.weak+'">0</b></div>'+
    (d.potential?'<div class="pot">'+esc(d.potential)+'</div>':'')+
    '<div style="color:var(--hint);font-size:12px;margin-top:6px">Найдено: <b data-count="'+d.total+'">0</b>. Нажмите «Скрипты», чтобы получить готовый текст для продажи.</div>';
  animateNums($('#summary'));
  $('#cards').innerHTML='';
  renderCards();renderMap();applyView();
}
function renderCards(){
  const items=visibleItems(),from=state.page*5,part=items.slice(from,from+5);
  state.visible=items;
  if(!items.length){
    const msg=(state.data&&state.data.message)||'Попробуйте изменить фильтры или нишу.';
    $('#cards').innerHTML='<div class="list-empty"><b>Ничего не найдено</b>'+esc(msg)+'</div>';
    $('#more').hidden=true;return;
  }
  $('#cards').innerHTML='';
  part.forEach((it,idx)=>{
    const i=from+idx,el=document.createElement('div');
    el.className='card'+(it.kind==='weak'?' weak':'');
    el.style.animationDelay=(idx*75)+'ms';
    const badge=it.kind==='weak'?'🔴 '+(it.score||0)+'/100':'🚫 НЕТ САЙТА';
    const issues=(Array.isArray(it.issues)?it.issues:[]).map(issueText).filter(Boolean).map(esc).join('; ');
    const pitch=(Array.isArray(it.pitch)?it.pitch:[]).join(', ');
    const socials=(Array.isArray(it.socials)?it.socials:[]).filter(s=>s&&s.url)
      .map(s=>'<a href="'+esc(s.url)+'" target="_blank" rel="noopener">'+esc(s.label||'ссылка')+'</a>').join('');
    const cur=statusKeys().indexOf(it.status)>=0?it.status:'new';
    el.innerHTML='<span class="badge">'+badge+'</span><h3>'+esc(it.name)+'</h3>'+
      (isNewItem(it)?'<div style="margin-bottom:8px"><span class="badge new-badge">✨ Новый</span></div>':'')+
      (it.site?'<div class="meta">🌐 <a href="'+esc(it.site)+'" target="_blank" rel="noopener" style="color:var(--accent);text-decoration:none">'+esc(it.site.replace(/^https?:\/\//,'').replace(/\/$/,''))+'</a></div>':'')+
      ((it.site && (Array.isArray(it.issues)?it.issues:[]).some(x=>String(x).indexOf('dead')>=0||String(x).indexOf('не открывается')>=0))?'<div class="meta" style="color:var(--yellow)">⚠️ Сайт есть, но сейчас может быть недоступен</div>':'')+
      (it.addr?'<div class="meta">📍 '+esc(it.addr)+'</div>':'')+
      '<div class="meta">📞 '+(it.phone?esc(it.phone):'<span style="opacity:.6">телефона нет</span>')+'</div>'+
      (it.hours?'<div class="meta">🕒 '+esc(it.hours)+'</div>':'')+
      (socials?'<div class="meta">🔗 '+socials+'</div>':'')+
      auditLine(it.audit)+
      (issues?'<div class="issues">⚠ '+issues+'</div>':'')+
      (pitch?'<div class="pitch">💡 Предложи: '+esc(pitch)+'</div>':'')+
      '<div class="quick-row">'+
        [['contacted','✉️ Написал'],['replied','💬 Ответил'],['deal','🤝 Сделка'],['lost','❌ Отказ']].map(([s,l])=>
          '<button class="qbtn'+(cur===s?' on':'')+(s==='lost'?' danger':'')+'" data-qid="'+esc(itemKey(it))+'" data-qs="'+s+'" data-qi="'+i+'">'+l+'</button>'
        ).join('')+
      '</div>'+
      '<div class="card-actions">'+
      '<button class="mini main" data-act="scripts" data-i="'+i+'">✍️ Скрипты</button>'+
      '<a class="mini" href="https://www.google.com/maps/search/?api=1&query='+encodeURIComponent(it.lat+','+it.lon)+'" target="_blank">📍 Карта</a>'+
      (it.phone&&it.phone.startsWith('+')?'<a class="mini" href="https://wa.me/'+it.phone.replace(/\D/g,'')+'" target="_blank">💬 WhatsApp</a>':'')+
      '</div>';
    el.querySelector('[data-act=scripts]').onclick=()=>openScripts(i);
    el.querySelectorAll('.qbtn').forEach(b=>b.onclick=()=>changeStatus(itemKey(it),it.name,it.site||'',b.dataset.qs,null));
    $('#cards').appendChild(el);
  });
  $('#more').hidden=from+5>=items.length||state.hidden;
  $('#more').textContent='Показать ещё ↓ (осталось '+Math.max(0,items.length-from-5)+')';
}
function exportCsv(){
  const it=state.data.items;
  if(!it.length)return toast('Нечего выгружать');
  const q=v=>'"'+String(v||'').replace(/"/g,'""')+'"';
  const rows=[['Название','Сайт','Телефон','Email','Адрес','Тип','Штраф','Проблемы','Широта','Долгота']];
  it.forEach(x=>rows.push([x.name,x.site,x.phone,x.email,x.addr,x.kind,x.score,
    (Array.isArray(x.issues)?x.issues:[]).map(issueText).join('; '),x.lat,x.lon]));
  const csv='\ufeff'+rows.map(r=>r.map(q).join(';')).join('\n');
  const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));
  a.download='leads_'+state.city.replace(/[^\w\u0400-\u04ff]+/g,'_')+'.csv';a.click();
  URL.revokeObjectURL(a.href);toast('CSV сохранён');
}
const TABS=[['dm','📱 Директ'],['call','📞 Звонок'],['em','✉️ Email'],['fu','🔁 Follow-up'],
            ['obj','🛡 Возражения'],['plan','📋 План'],['close','🤝 Закрыть сделку']];
async function openScripts(idx){
  state.lead=(state.visible||[])[idx]||(state.data&&state.data.items[idx]);state.tab='dm';
  if(!state.lead)return;
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
    const langs=(r.langs||[]).map(x=>({k:x.k||x.key,label:x.label}));
    let html='<div class="langs">'+langs.map(x=>'<button data-l="'+x.k+'" class="'+(x.k===state.lang?'on':'')+'">'+x.label+'</button>').join('')+'</div>';
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
