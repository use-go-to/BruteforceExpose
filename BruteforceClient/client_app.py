"""
POSTE CLIENT - Application web de login (édition immersive v2)
----------------------------------------------------------------
Lancement :
    pip install flask
    python3 client_app.py

Améliorations immersives :
  * Moteur sonore Web Audio (aucun fichier audio requis)
  * Canvas de particules réseau (style blockchain)
  * Dashboard crypto réaliste (sidebar, solde animé, sparkline, transactions)
  * Séquence d'unlock cinématique au login
  * Ticker marché défilant, toasts, scanlines, glow néon

Faille pédagogique inchangée : /backup/users.txt expose le hash MD5.
"""

from flask import Flask, request, redirect, session, render_template_string
import hashlib
import os

app = Flask(__name__)
app.secret_key = os.urandom(16)

USERS_FILE = "users.txt"
ADMIN_LOGIN = "admin"

# ═══════════════════════════════════════════════════════════════════════
#  STYLE GLOBAL (CSS)
# ═══════════════════════════════════════════════════════════════════════
BASE_STYLE = """
<style>
  :root{
    --bg-0:#04060c; --bg-1:#070b14; --bg-2:#0b1120;
    --panel:rgba(12,18,32,0.72);
    --panel-2:rgba(18,26,44,0.55);
    --border:rgba(120,180,255,0.10);
    --border-strong:rgba(120,180,255,0.22);
    --text:#e8eefc; --muted:#7c88a8; --muted-2:#4d5group;
    --accent:#00e5ff; --accent-2:#7c5cff; --accent-3:#00ffa3;
    --success:#00ff88; --danger:#ff4d6d; --warn:#ffb020;
    --glow-cyan:0 0 24px rgba(0,229,255,0.35);
    --glow-purple:0 0 24px rgba(124,92,255,0.35);
    --mono:'JetBrains Mono','SF Mono',Consolas,monospace;
    --sans:'Inter','Segoe UI',system-ui,-apple-system,sans-serif;
  }
  *{box-sizing:border-box;margin:0;padding:0;}
  html,body{height:100%;}
  body{
    font-family:var(--sans); color:var(--text); overflow-x:hidden;
    background:
      radial-gradient(ellipse 800px 500px at 15% -10%, rgba(0,229,255,0.10), transparent 60%),
      radial-gradient(ellipse 900px 600px at 85% 110%, rgba(124,92,255,0.12), transparent 60%),
      linear-gradient(160deg, var(--bg-0) 0%, var(--bg-1) 50%, var(--bg-2) 100%);
    min-height:100vh;
  }
  /* Scanlines subtiles */
  body::after{
    content:''; position:fixed; inset:0; pointer-events:none; z-index:9998;
    background:repeating-linear-gradient(0deg,
      rgba(255,255,255,0.012) 0px, rgba(255,255,255,0.012) 1px,
      transparent 1px, transparent 3px);
    mix-blend-mode:overlay;
  }
  /* Vignette */
  body::before{
    content:''; position:fixed; inset:0; pointer-events:none; z-index:9997;
    background:radial-gradient(ellipse at center, transparent 55%, rgba(0,0,0,0.55) 100%);
  }
  #bg-canvas{position:fixed; inset:0; z-index:0; pointer-events:none;}

  /* ─────────── Layout ─────────── */
  .shell{position:relative; z-index:1; min-height:100vh; display:flex; flex-direction:column;}
  .topbar{
    display:flex; align-items:center; justify-content:space-between;
    padding:14px 24px; border-bottom:1px solid var(--border);
    background:linear-gradient(180deg, rgba(8,12,22,0.9), rgba(8,12,22,0.4));
    backdrop-filter:blur(20px); -webkit-backdrop-filter:blur(20px);
    position:sticky; top:0; z-index:100;
  }
  .brand{display:flex; align-items:center; gap:12px;}
  .logo{
    width:42px; height:42px; border-radius:12px; position:relative;
    background:conic-gradient(from 140deg, var(--accent), var(--accent-2), var(--accent-3), var(--accent));
    display:flex; align-items:center; justify-content:center;
    font-size:22px; color:#04060c; font-weight:800;
    box-shadow:var(--glow-cyan), inset 0 0 12px rgba(255,255,255,0.4);
    animation:logoPulse 3.5s ease-in-out infinite;
  }
  @keyframes logoPulse{
    0%,100%{box-shadow:0 0 18px rgba(0,229,255,0.30), inset 0 0 12px rgba(255,255,255,0.35);}
    50%    {box-shadow:0 0 32px rgba(0,229,255,0.55), 0 0 60px rgba(124,92,255,0.25), inset 0 0 14px rgba(255,255,255,0.5);}
  }
  .brand h1{font-size:17px; letter-spacing:0.6px; font-weight:700;}
  .brand h1 span{
    background:linear-gradient(90deg, var(--accent), var(--accent-2));
    -webkit-background-clip:text; background-clip:text; color:transparent;
  }
  .brand .tag{font-size:10px; color:var(--muted); letter-spacing:1.4px; text-transform:uppercase; margin-top:2px;}

  .status-badge{
    display:flex; align-items:center; gap:8px;
    font-size:11px; letter-spacing:0.6px; color:var(--accent-3);
    padding:6px 12px; border-radius:20px;
    border:1px solid rgba(0,255,163,0.25); background:rgba(0,255,163,0.06);
    font-family:var(--mono);
  }
  .status-badge .dot{
    width:7px; height:7px; border-radius:50%; background:var(--accent-3);
    box-shadow:0 0 10px var(--accent-3); animation:blink 1.6s ease-in-out infinite;
  }
  @keyframes blink{0%,100%{opacity:1;}50%{opacity:.35;}}

  .main-grid{display:grid; grid-template-columns:220px 1fr; flex:1; min-height:0;}
  .sidebar{
    border-right:1px solid var(--border); padding:22px 14px;
    background:linear-gradient(180deg, rgba(8,12,22,0.5), rgba(8,12,22,0.2));
    display:flex; flex-direction:column; gap:6px;
  }
  .nav-item{
    display:flex; align-items:center; gap:12px;
    padding:11px 14px; border-radius:10px;
    color:var(--muted); font-size:13.5px; font-weight:500;
    cursor:pointer; transition:all .2s ease; position:relative;
    border:1px solid transparent;
  }
  .nav-item:hover{color:var(--text); background:rgba(120,180,255,0.05);}
  .nav-item.active{
    color:var(--accent); background:rgba(0,229,255,0.08);
    border-color:rgba(0,229,255,0.25);
    box-shadow:inset 0 0 20px rgba(0,229,255,0.08);
  }
  .nav-item.active::before{
    content:''; position:absolute; left:-14px; top:50%; transform:translateY(-50%);
    width:3px; height:20px; border-radius:0 3px 3px 0;
    background:linear-gradient(180deg, var(--accent), var(--accent-2));
    box-shadow:0 0 12px var(--accent);
  }
  .nav-item .ico{font-size:16px; width:20px; text-align:center;}
  .nav-sep{height:1px; background:var(--border); margin:14px 4px;}

  .content{padding:26px 30px; overflow-y:auto; position:relative;}

  /* ─────────── Cards ─────────── */
  .card{
    background:var(--panel); backdrop-filter:blur(22px); -webkit-backdrop-filter:blur(22px);
    border:1px solid var(--border); border-radius:18px;
    padding:24px; position:relative; overflow:hidden;
    box-shadow:0 20px 60px rgba(0,0,0,0.55), inset 0 1px 0 rgba(255,255,255,0.04);
    animation:rise .55s cubic-bezier(.2,.9,.3,1) both;
  }
  .card::before{
    content:''; position:absolute; top:0; left:0; right:0; height:1px;
    background:linear-gradient(90deg, transparent, rgba(0,229,255,0.5), transparent);
    opacity:.6;
  }
  @keyframes rise{from{opacity:0; transform:translateY(16px);} to{opacity:1; transform:translateY(0);}}

  /* ─────────── Auth (setup/login) ─────────── */
  .auth-wrap{
    min-height:100vh; display:flex; align-items:center; justify-content:center;
    padding:30px; position:relative; z-index:1;
  }
  .auth-card{
    width:420px; padding:42px 38px;
    background:var(--panel); backdrop-filter:blur(24px);
    border:1px solid var(--border); border-radius:22px;
    box-shadow:0 30px 80px rgba(0,0,0,0.65), inset 0 1px 0 rgba(255,255,255,0.05);
    position:relative; overflow:hidden;
    animation:rise .7s cubic-bezier(.2,.9,.3,1) both;
  }
  .auth-card::before{
    content:''; position:absolute; top:-2px; left:0; right:0; height:2px;
    background:linear-gradient(90deg, transparent, var(--accent), var(--accent-2), transparent);
    animation:scanline 3s linear infinite;
  }
  @keyframes scanline{0%{transform:translateX(-100%);}100%{transform:translateX(100%);}}

  .lock-icon{
    font-size:34px; text-align:center; margin-bottom:16px;
    filter:drop-shadow(0 0 18px rgba(0,229,255,0.5));
    animation:floatY 3s ease-in-out infinite;
  }
  @keyframes floatY{0%,100%{transform:translateY(0);}50%{transform:translateY(-6px);}}

  .subtitle{color:var(--muted); font-size:13px; margin:6px 0 26px; letter-spacing:0.2px;}

  .field{margin-bottom:18px;}
  .field label{
    display:block; font-size:11px; color:var(--muted);
    margin-bottom:8px; letter-spacing:1px; text-transform:uppercase; font-weight:600;
  }
  .input-wrap{position:relative;}
  input[type=password], input[type=text]{
    width:100%; padding:14px 44px 14px 14px; border-radius:12px;
    border:1px solid var(--border-strong);
    background:rgba(4,8,16,0.6); color:var(--text);
    font-size:14.5px; font-family:var(--mono); letter-spacing:0.5px;
    outline:none; transition:all .22s ease;
  }
  input::placeholder{color:#3a4460;}
  input:focus{
    border-color:var(--accent);
    box-shadow:0 0 0 3px rgba(0,229,255,0.12), 0 0 24px rgba(0,229,255,0.15);
    background:rgba(4,8,16,0.85);
  }
  .input-wrap .eye{
    position:absolute; right:12px; top:50%; transform:translateY(-50%);
    cursor:pointer; color:var(--muted); font-size:15px; user-select:none;
    transition:color .2s;
  }
  .input-wrap .eye:hover{color:var(--accent);}

  .btn{
    width:100%; padding:15px; border:none; border-radius:12px;
    background:linear-gradient(135deg, var(--accent), var(--accent-2));
    color:#04060c; font-size:14px; font-weight:700; letter-spacing:0.4px;
    cursor:pointer; position:relative; overflow:hidden;
    box-shadow:0 12px 30px rgba(0,229,255,0.28), 0 0 0 1px rgba(255,255,255,0.06) inset;
    transition:transform .15s ease, box-shadow .2s ease;
    font-family:var(--sans);
  }
  .btn:hover{transform:translateY(-2px); box-shadow:0 18px 40px rgba(0,229,255,0.42), 0 0 0 1px rgba(255,255,255,0.1) inset;}
  .btn:active{transform:translateY(0);}
  .btn::after{
    content:''; position:absolute; inset:0;
    background:linear-gradient(110deg, transparent 30%, rgba(255,255,255,0.35) 50%, transparent 70%);
    transform:translateX(-100%);
  }
  .btn:hover::after{animation:shine .8s ease;}
  @keyframes shine{to{transform:translateX(100%);}}

  .error{
    background:rgba(255,77,109,0.10); border:1px solid rgba(255,77,109,0.35);
    color:var(--danger); font-size:13px; padding:11px 14px; border-radius:11px; margin-bottom:16px;
    display:flex; align-items:center; gap:8px;
    animation:shake .4s ease;
  }
  @keyframes shake{
    0%,100%{transform:translateX(0);}
    20%{transform:translateX(-6px);} 40%{transform:translateX(6px);}
    60%{transform:translateX(-4px);} 80%{transform:translateX(4px);}
  }
  .foot{text-align:center; margin-top:22px; font-size:11px; color:var(--muted); letter-spacing:0.4px;}
  .foot a{color:var(--accent); text-decoration:none; transition:opacity .2s;}
  .foot a:hover{opacity:.75;}

  /* ─────────── Dashboard ─────────── */
  .page-head{display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:22px;}
  .page-head h2{font-size:22px; font-weight:700; letter-spacing:0.3px;}
  .page-head .sub{font-size:12px; color:var(--muted); margin-top:4px; font-family:var(--mono);}

  .balance-hero{
    display:grid; grid-template-columns:1.3fr 1fr; gap:22px; margin-bottom:22px;
  }
  .balance-card{
    background:linear-gradient(135deg, rgba(0,229,255,0.06), rgba(124,92,255,0.06));
    border:1px solid rgba(0,229,255,0.18); border-radius:18px; padding:26px;
    position:relative; overflow:hidden;
  }
  .balance-card::after{
    content:''; position:absolute; right:-40%; top:-40%; width:80%; height:180%;
    background:radial-gradient(circle, rgba(0,229,255,0.10), transparent 70%);
    pointer-events:none;
  }
  .balance-label{font-size:11px; color:var(--muted); letter-spacing:1.4px; text-transform:uppercase; font-weight:600;}
  .balance-amount{
    font-family:var(--mono); font-size:38px; font-weight:700; margin:12px 0 6px;
    letter-spacing:-0.5px;
    background:linear-gradient(90deg, #fff, var(--accent));
    -webkit-background-clip:text; background-clip:text; color:transparent;
    text-shadow:0 0 40px rgba(0,229,255,0.15);
  }
  .balance-amount small{font-size:18px; opacity:.6; font-weight:500;}
  .balance-eur{font-family:var(--mono); font-size:15px; color:var(--muted);}
  .balance-eur .up{color:var(--success); font-weight:600;}

  .actions{display:flex; gap:10px; margin-top:20px; flex-wrap:wrap;}
  .action-btn{
    flex:1; min-width:100px; padding:11px 14px; border-radius:11px;
    background:rgba(255,255,255,0.04); border:1px solid var(--border-strong);
    color:var(--text); font-size:12.5px; font-weight:600; cursor:pointer;
    transition:all .2s ease; display:flex; align-items:center; justify-content:center; gap:7px;
    font-family:var(--sans);
  }
  .action-btn:hover{
    background:rgba(0,229,255,0.10); border-color:rgba(0,229,255,0.4);
    transform:translateY(-1px);
  }
  .action-btn .ico{font-size:14px;}

  .chart-card{
    background:var(--panel-2); border:1px solid var(--border);
    border-radius:18px; padding:20px; display:flex; flex-direction:column;
  }
  .chart-head{display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;}
  .chart-head .pair{font-size:14px; font-weight:700; letter-spacing:0.3px;}
  .chart-head .pair small{color:var(--muted); font-weight:500; font-size:11px; margin-left:6px;}
  .chart-head .price{font-family:var(--mono); font-size:16px; color:var(--accent-3);}
  .chart-head .price.up::before{content:'▲ '; font-size:11px;}
  .chart-head .price.down::before{content:'▼ '; font-size:11px; color:var(--danger);}
  .sparkline{width:100%; height:80px; display:block;}

  .asset-row{
    display:grid; grid-template-columns:44px 1fr auto auto; gap:14px;
    align-items:center; padding:14px 16px; border-radius:12px;
    border:1px solid transparent; transition:all .2s ease;
  }
  .asset-row:hover{background:rgba(120,180,255,0.04); border-color:var(--border);}
  .asset-icon{
    width:38px; height:38px; border-radius:11px; display:flex;
    align-items:center; justify-content:center; font-weight:800; font-size:14px;
    font-family:var(--mono); color:#04060c;
  }
  .asset-name{font-size:13.5px; font-weight:600;}
  .asset-name small{color:var(--muted); font-weight:400; font-family:var(--mono); font-size:11px; margin-left:6px;}
  .asset-amount{font-family:var(--mono); font-size:13px; color:var(--muted); text-align:right;}
  .asset-value{font-family:var(--mono); font-size:13.5px; font-weight:600; text-align:right; min-width:100px;}
  .asset-value.up{color:var(--success);}
  .asset-value.down{color:var(--danger);}

  .tx-row{
    display:grid; grid-template-columns:44px 1fr auto; gap:14px;
    align-items:center; padding:13px 16px; border-radius:12px;
    transition:background .2s;
  }
  .tx-row:hover{background:rgba(120,180,255,0.04);}
  .tx-icon{
    width:36px; height:36px; border-radius:50%; display:flex;
    align-items:center; justify-content:center; font-size:15px;
  }
  .tx-icon.in{background:rgba(0,255,136,0.12); color:var(--success); border:1px solid rgba(0,255,136,0.25);}
  .tx-icon.out{background:rgba(255,77,109,0.12); color:var(--danger); border:1px solid rgba(255,77,109,0.25);}
  .tx-main{font-size:13.5px; font-weight:600;}
  .tx-sub{font-size:11px; color:var(--muted); margin-top:3px; font-family:var(--mono);}
  .tx-amount{font-family:var(--mono); font-size:13.5px; font-weight:600; text-align:right;}
  .tx-amount.in{color:var(--success);}
  .tx-amount.out{color:var(--danger);}

  .ticker{
    height:34px; border-top:1px solid var(--border); border-bottom:1px solid var(--border);
    background:rgba(4,8,16,0.7); overflow:hidden; display:flex; align-items:center;
    font-family:var(--mono); font-size:11.5px; color:var(--muted);
    margin:-26px -30px 22px; padding:0 0;
  }
  .ticker-track{display:flex; gap:44px; white-space:nowrap; animation:tick 40s linear infinite; padding-left:100%;}
  @keyframes tick{to{transform:translateX(-100%);}}
  .ticker-item{display:flex; gap:8px; align-items:center;}
  .ticker-item .up{color:var(--success);}
  .ticker-item .down{color:var(--danger);}

  .divider{height:1px; background:var(--border); margin:20px 0;}
  .section-title{font-size:12px; letter-spacing:1.2px; text-transform:uppercase; color:var(--muted); font-weight:600; margin-bottom:10px;}

  /* ─────────── Unlock overlay ─────────── */
  .unlock-overlay{
    position:fixed; inset:0; z-index:10000; display:none;
    background:radial-gradient(ellipse at center, rgba(4,8,16,0.92), rgba(2,4,10,0.98));
    backdrop-filter:blur(20px);
    align-items:center; justify-content:center; flex-direction:column;
  }
  .unlock-overlay.show{display:flex; animation:fadeIn .35s ease;}
  @keyframes fadeIn{from{opacity:0;}to{opacity:1;}}
  .vault-ring{
    width:140px; height:140px; border-radius:50%; position:relative;
    border:2px solid rgba(0,229,255,0.15);
    display:flex; align-items:center; justify-content:center;
  }
  .vault-ring::before, .vault-ring::after{
    content:''; position:absolute; inset:-2px; border-radius:50%;
    border:2px solid transparent;
    border-top-color:var(--accent);
    animation:spin 1.1s linear infinite;
  }
  .vault-ring::after{
    inset:-12px; border-top-color:var(--accent-2);
    animation-duration:1.7s; animation-direction:reverse;
  }
  @keyframes spin{to{transform:rotate(360deg);}}
  .vault-lock{font-size:44px; filter:drop-shadow(0 0 22px var(--accent));}
  .unlock-status{
    margin-top:28px; font-family:var(--mono); font-size:13px; color:var(--accent);
    letter-spacing:1.2px; text-align:center;
  }
  .unlock-bar{
    width:340px; height:4px; border-radius:3px; margin-top:14px;
    background:rgba(255,255,255,0.06); overflow:hidden;
  }
  .unlock-bar-fill{
    height:100%; width:0%; border-radius:3px;
    background:linear-gradient(90deg, var(--accent), var(--accent-2), var(--accent-3));
    box-shadow:0 0 12px var(--accent);
    transition:width .3s ease;
  }

  /* ─────────── Toasts ─────────── */
  #toasts{position:fixed; bottom:24px; right:24px; z-index:9999; display:flex; flex-direction:column; gap:10px;}
  .toast{
    min-width:280px; padding:13px 16px; border-radius:12px;
    background:rgba(12,18,32,0.92); backdrop-filter:blur(16px);
    border:1px solid var(--border-strong);
    font-size:13px; color:var(--text);
    display:flex; align-items:center; gap:10px;
    box-shadow:0 20px 50px rgba(0,0,0,0.6);
    animation:toastIn .35s cubic-bezier(.2,.9,.3,1);
    border-left:3px solid var(--accent);
  }
  .toast.success{border-left-color:var(--success);}
  .toast.error{border-left-color:var(--danger);}
  .toast.warn{border-left-color:var(--warn);}
  @keyframes toastIn{from{opacity:0; transform:translateX(40px);}to{opacity:1; transform:translateX(0);}}
  .toast.out{animation:toastOut .3s ease forwards;}
  @keyframes toastOut{to{opacity:0; transform:translateX(40px);}}

  /* scrollbar */
  ::-webkit-scrollbar{width:9px; height:9px;}
  ::-webkit-scrollbar-track{background:transparent;}
  ::-webkit-scrollbar-thumb{background:rgba(120,180,255,0.15); border-radius:10px;}
  ::-webkit-scrollbar-thumb:hover{background:rgba(0,229,255,0.35);}

  @media (max-width:820px){
    .main-grid{grid-template-columns:1fr;}
    .sidebar{display:none;}
    .balance-hero{grid-template-columns:1fr;}
    .content{padding:20px;}
  }
</style>
"""

# ═══════════════════════════════════════════════════════════════════════
#  MOTEUR SONORE + PARTICULES (JS partagé)
# ═══════════════════════════════════════════════════════════════════════
COMMON_JS = """
<script>
/* ═════════════════ Sound Engine (Web Audio API) ═════════════════ */
const Sound = (() => {
  let ctx = null, enabled = true, master = null;
  const init = () => {
    if (ctx) return;
    try {
      ctx = new (window.AudioContext || window.webkitAudioContext)();
      master = ctx.createGain();
      master.gain.value = 0.55;
      master.connect(ctx.destination);
    } catch(e){ enabled = false; }
  };
  const tone = (freq, dur, type='sine', vol=0.06, slideTo=null, delay=0) => {
    if (!enabled) return;
    init(); if (!ctx) return;
    const t0 = ctx.currentTime + delay;
    const o = ctx.createOscillator();
    const g = ctx.createGain();
    o.type = type;
    o.frequency.setValueAtTime(freq, t0);
    if (slideTo) o.frequency.exponentialRampToValueAtTime(slideTo, t0 + dur);
    g.gain.setValueAtTime(0.0001, t0);
    g.gain.exponentialRampToValueAtTime(vol, t0 + 0.008);
    g.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);
    o.connect(g); g.connect(master);
    o.start(t0); o.stop(t0 + dur + 0.02);
  };
  return {
    unlock: () => { tone(220,0.08,'square',0.05); tone(440,0.08,'square',0.05,null,0.08); tone(660,0.10,'square',0.05,null,0.16); tone(880,0.35,'sine',0.07,1320,0.24); },
    click:  () => tone(880, 0.05, 'square', 0.035),
    hover:  () => tone(1400, 0.025, 'sine', 0.015),
    type:   () => tone(2200, 0.015, 'square', 0.010),
    success:() => { tone(523,0.09,'sine',0.06); tone(659,0.09,'sine',0.06,null,0.07); tone(784,0.28,'sine',0.07,null,0.14); },
    error:  () => { tone(180,0.14,'sawtooth',0.05); tone(140,0.22,'sawtooth',0.05,null,0.11); },
    coin:   () => { tone(1200,0.05,'sine',0.05); tone(1600,0.12,'sine',0.05,null,0.045); },
    ambient:() => { tone(110, 2.5, 'sine', 0.012); }
  };
})();

/* Autoplay unlock on first interaction (browser policy) */
['click','keydown','touchstart','pointerdown'].forEach(ev =>
  window.addEventListener(ev, () => { Sound.click && (window.__audioUnlocked = true); }, {once:true})
);

/* ═════════════════ Particle Network (canvas) ═════════════════ */
(function particles(){
  const canvas = document.getElementById('bg-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let W, H, nodes = [], mouse = {x:-999, y:-999};
  const NODE_COUNT = Math.min(70, Math.floor(window.innerWidth / 22));
  const LINK_DIST = 150, MOUSE_DIST = 180;

  function resize(){
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }
  function makeNodes(){
    nodes = [];
    for (let i=0;i<NODE_COUNT;i++){
      nodes.push({
        x: Math.random()*W, y: Math.random()*H,
        vx: (Math.random()-0.5)*0.35, vy: (Math.random()-0.5)*0.35,
        r: Math.random()*1.6 + 0.6,
        hue: Math.random() < 0.5 ? 190 : 265
      });
    }
  }
  function step(){
    ctx.clearRect(0,0,W,H);
    // links
    for (let i=0;i<nodes.length;i++){
      const a = nodes[i];
      for (let j=i+1;j<nodes.length;j++){
        const b = nodes[j];
        const dx = a.x-b.x, dy = a.y-b.y;
        const d = Math.hypot(dx,dy);
        if (d < LINK_DIST){
          const alpha = (1 - d/LINK_DIST) * 0.22;
          ctx.strokeStyle = `hsla(${a.hue}, 90%, 65%, ${alpha})`;
          ctx.lineWidth = 0.6;
          ctx.beginPath(); ctx.moveTo(a.x,a.y); ctx.lineTo(b.x,b.y); ctx.stroke();
        }
      }
      // mouse link
      const dm = Math.hypot(a.x-mouse.x, a.y-mouse.y);
      if (dm < MOUSE_DIST){
        const alpha = (1 - dm/MOUSE_DIST) * 0.4;
        ctx.strokeStyle = `hsla(190, 100%, 70%, ${alpha})`;
        ctx.lineWidth = 0.8;
        ctx.beginPath(); ctx.moveTo(a.x,a.y); ctx.lineTo(mouse.x,mouse.y); ctx.stroke();
      }
    }
    // nodes
    for (const n of nodes){
      n.x += n.vx; n.y += n.vy;
      if (n.x < 0 || n.x > W) n.vx *= -1;
      if (n.y < 0 || n.y > H) n.vy *= -1;
      const glow = ctx.createRadialGradient(n.x, n.y, 0, n.x, n.y, n.r*6);
      glow.addColorStop(0, `hsla(${n.hue}, 100%, 70%, 0.9)`);
      glow.addColorStop(1, `hsla(${n.hue}, 100%, 60%, 0)`);
      ctx.fillStyle = glow;
      ctx.beginPath(); ctx.arc(n.x, n.y, n.r*6, 0, Math.PI*2); ctx.fill();
      ctx.fillStyle = `hsla(${n.hue}, 100%, 80%, 1)`;
      ctx.beginPath(); ctx.arc(n.x, n.y, n.r, 0, Math.PI*2); ctx.fill();
    }
    requestAnimationFrame(step);
  }
  window.addEventListener('resize', () => { resize(); makeNodes(); });
  window.addEventListener('mousemove', e => { mouse.x = e.clientX; mouse.y = e.clientY; });
  window.addEventListener('mouseleave', () => { mouse.x = mouse.y = -999; });

  resize(); makeNodes(); step();
})();

/* ═════════════════ Toast helper ═════════════════ */
function toast(msg, type='info', ms=3200){
  const wrap = document.getElementById('toasts');
  if (!wrap) return;
  const el = document.createElement('div');
  el.className = 'toast ' + type;
  const icon = type === 'success' ? '✔' : type === 'error' ? '⚠' : type === 'warn' ? '⚡' : 'ℹ';
  el.innerHTML = `<span style="font-size:16px">${icon}</span><span>${msg}</span>`;
  wrap.appendChild(el);
  if (type === 'success') Sound.success();
  else if (type === 'error') Sound.error();
  else Sound.click();
  setTimeout(() => { el.classList.add('out'); setTimeout(()=>el.remove(), 320); }, ms);
}

/* Global hover sound (delegated) */
document.addEventListener('mouseover', e => {
  if (e.target.closest('.nav-item, .action-btn, .btn, .asset-row, .tx-row, a, input')) {
    Sound.hover();
  }
});
document.addEventListener('click', e => {
  if (e.target.closest('.nav-item, .action-btn, .btn, button')) Sound.click();
});
</script>
<div id="toasts"></div>
"""

# ═══════════════════════════════════════════════════════════════════════
#  PAGE : SETUP (premier lancement)
# ═══════════════════════════════════════════════════════════════════════
SETUP_PAGE = """
<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>NovaVault — Initialisation du coffre</title>
""" + BASE_STYLE + """
</head>
<body>
<canvas id="bg-canvas"></canvas>
<div class="auth-wrap">
  <div class="auth-card">
    <div class="brand" style="justify-content:center; margin-bottom:14px;">
      <div class="logo">◆</div>
      <div>
        <h1>Nova<span>Vault</span></h1>
        <div class="tag">Cold Wallet · v4.2.1</div>
      </div>
    </div>
    <p class="subtitle" style="text-align:center;">Première configuration — définissez votre mot de passe maître.</p>
    <div class="lock-icon">🔐</div>
    <form method="post" id="setup-form">
      <div class="field">
        <label>Mot de passe maître</label>
        <div class="input-wrap">
          <input type="password" name="password" id="pwd" placeholder="••••••••••••••••" required autofocus minlength="4">
          <span class="eye" id="eye">👁</span>
        </div>
      </div>
      <div class="field">
        <label>Confirmer le mot de passe</label>
        <div class="input-wrap">
          <input type="password" name="confirm" id="pwd2" placeholder="••••••••••••••••" required minlength="4">
        </div>
      </div>
      <div id="err" class="error" style="display:none;">⚠ Les deux mots de passe ne correspondent pas.</div>
      <button type="submit" class="btn">Initialiser mon coffre</button>
    </form>
    <p class="foot">Vos clés sont chiffrées localement · AES-256-GCM</p>
  </div>
</div>
""" + COMMON_JS + """
<script>
  const pwd = document.getElementById('pwd');
  const pwd2 = document.getElementById('pwd2');
  const err = document.getElementById('err');
  const eye = document.getElementById('eye');
  eye.addEventListener('click', () => {
    const show = pwd.type === 'password';
    pwd.type = pwd2.type = show ? 'text' : 'password';
    eye.textContent = show ? '🙈' : '👁';
    Sound.click();
  });
  pwd.addEventListener('input', () => Sound.type());
  pwd2.addEventListener('input', () => Sound.type());
  document.getElementById('setup-form').addEventListener('submit', e => {
    if (pwd.value !== pwd2.value){
      e.preventDefault(); err.style.display = 'flex'; Sound.error();
      pwd2.focus();
      setTimeout(()=>{ err.style.display='none'; }, 4000);
    } else {
      Sound.unlock();
    }
  });
  window.addEventListener('load', () => {
    setTimeout(()=> toast('Aucun coffre détecté — initialisation requise.', 'warn'), 600);
  });
</script>
</body>
</html>
"""

# ═══════════════════════════════════════════════════════════════════════
#  PAGE : LOGIN
# ═══════════════════════════════════════════════════════════════════════
LOGIN_PAGE = """
<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>NovaVault — Connexion sécurisée</title>
""" + BASE_STYLE + """
</head>
<body>
<canvas id="bg-canvas"></canvas>
<div class="auth-wrap">
  <div class="auth-card">
    <div class="brand" style="justify-content:center; margin-bottom:14px;">
      <div class="logo">◆</div>
      <div>
        <h1>Nova<span>Vault</span></h1>
        <div class="tag">Cold Wallet · v4.2.1</div>
      </div>
    </div>
    <p class="subtitle" style="text-align:center;">Déverrouillez votre portefeuille pour accéder à vos actifs.</p>
    <div class="lock-icon">🔒</div>
    {% if error %}
    <div class="error">⚠ {{ error }}</div>
    {% endif %}
    <form method="post" id="login-form" autocomplete="off">
      <input type="hidden" name="login" value="admin" readonly>
      <div class="field">
        <label>Mot de passe maître</label>
        <div class="input-wrap">
          <input type="password" name="password" id="pwd" placeholder="••••••••••••••••" required autofocus>
          <span class="eye" id="eye">👁</span>
        </div>
      </div>
      <button type="submit" class="btn" id="btn-submit">🔓 Déverrouiller le coffre</button>
    </form>
    <p class="foot">Protégé par chiffrement AES-256 · <a href="#" onclick="toast('Récupération impossible sans phrase de récupération.','warn'); return false;">Mot de passe oublié ?</a></p>
  </div>
</div>

<!-- Overlay d'unlock cinématique -->
<div class="unlock-overlay" id="unlock">
  <div class="vault-ring">
    <div class="vault-lock">🔐</div>
  </div>
  <div class="unlock-status" id="unlock-status">Initialisation du déchiffrement…</div>
  <div class="unlock-bar"><div class="unlock-bar-fill" id="unlock-bar"></div></div>
</div>

""" + COMMON_JS + """
<script>
  const pwd = document.getElementById('pwd');
  const eye = document.getElementById('eye');
  eye.addEventListener('click', () => {
    const show = pwd.type === 'password';
    pwd.type = show ? 'text' : 'password';
    eye.textContent = show ? '🙈' : '👁';
    Sound.click();
  });
  pwd.addEventListener('input', () => Sound.type());

  const unlockEl = document.getElementById('unlock');
  const unlockStatus = document.getElementById('unlock-status');
  const unlockBar = document.getElementById('unlock-bar');

  const steps = [
    ['Initialisation du déchiffrement…', 18],
    ['Vérification de la clé maître…', 42],
    ['Déchiffrement AES-256 du coffre…', 68],
    ['Chargement de la blockchain locale…', 88],
    ['Ouverture du portefeuille…', 100],
  ];

  document.getElementById('login-form').addEventListener('submit', e => {
    e.preventDefault();
    Sound.unlock();
    unlockEl.classList.add('show');
    let i = 0;
    const run = () => {
      if (i >= steps.length){
        setTimeout(() => { e.target.submit(); }, 260);
        return;
      }
      unlockStatus.textContent = steps[i][0];
      unlockBar.style.width = steps[i][1] + '%';
      i++;
      setTimeout(run, 260 + Math.random()*140);
    };
    run();
  });

  window.addEventListener('load', () => {
    setTimeout(()=> Sound.ambient && Sound.ambient(), 800);
  });
</script>
</body>
</html>
"""

# ═══════════════════════════════════════════════════════════════════════
#  PAGE : DASHBOARD
# ═══════════════════════════════════════════════════════════════════════
DASHBOARD_PAGE = """
<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>NovaVault — Portefeuille</title>
""" + BASE_STYLE + """
</head>
<body>
<canvas id="bg-canvas"></canvas>
<div class="shell">

  <!-- ══════════ TOPBAR ══════════ -->
  <header class="topbar">
    <div class="brand">
      <div class="logo">◆</div>
      <div>
        <h1>Nova<span>Vault</span></h1>
        <div class="tag">Cold Wallet · v4.2.1</div>
      </div>
    </div>
    <div style="display:flex; align-items:center; gap:14px;">
      <div class="status-badge" title="Session active">
        <span class="dot"></span>
        <span>Accès administrateur confirmé</span>
      </div>
      <div style="width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,var(--accent),var(--accent-2));display:flex;align-items:center;justify-content:center;font-weight:700;color:#04060c;font-size:14px;">A</div>
    </div>
  </header>

  <!-- ══════════ LAYOUT ══════════ -->
  <div class="main-grid">
    <aside class="sidebar">
      <div class="nav-item active" data-page="wallet"><span class="ico">💼</span> Portefeuille</div>
      <div class="nav-item" data-page="tx"><span class="ico">📜</span> Transactions</div>
      <div class="nav-item" data-page="market"><span class="ico">📈</span> Marché</div>
      <div class="nav-item" data-page="stacking"><span class="ico">🥩</span> Staking</div>
      <div class="nav-sep"></div>
      <div class="nav-item" data-page="security"><span class="ico">🛡</span> Sécurité</div>
      <div class="nav-item" data-page="settings"><span class="ico">⚙</span> Paramètres</div>
      <div style="flex:1"></div>
      <a class="nav-item" href="/logout" style="color:var(--danger);">
        <span class="ico">🔒</span> Verrouiller
      </a>
    </aside>

    <main class="content">
      <!-- Ticker -->
      <div class="ticker">
        <div class="ticker-track" id="ticker-track"></div>
      </div>

      <div class="page-head">
        <div>
          <h2>Portefeuille principal</h2>
          <div class="sub" id="last-sync">Dernière synchronisation : —</div>
        </div>
      </div>

      <!-- ══════════ HERO ══════════ -->
      <div class="balance-hero">
        <div class="balance-card card">
          <div class="balance-label">Solde total du coffre</div>
          <div class="balance-amount" id="btc-total">12.4821 <small>BTC</small></div>
          <div class="balance-eur">≈ <span id="eur-total">742 300</span> € <span class="up" id="pct-24h">▲ +2.84% (24h)</span></div>
          <div class="actions">
            <button class="action-btn" data-action="receive"><span class="ico">↘</span> Recevoir</button>
            <button class="action-btn" data-action="send"><span class="ico">↗</span> Envoyer</button>
            <button class="action-btn" data-action="swap"><span class="ico">⇄</span> Échanger</button>
            <button class="action-btn" data-action="buy"><span class="ico">＋</span> Acheter</button>
          </div>
        </div>

        <div class="chart-card card" style="animation-delay:.1s;">
          <div class="chart-head">
            <div class="pair">BTC / EUR <small>· 24h</small></div>
            <div class="price up" id="btc-price">59 477 €</div>
          </div>
          <svg class="sparkline" id="sparkline" viewBox="0 0 300 80" preserveAspectRatio="none">
            <defs>
              <linearGradient id="spark-grad" x1="0" x2="0" y1="0" y2="1">
                <stop offset="0%" stop-color="rgba(0,229,255,0.35)"/>
                <stop offset="100%" stop-color="rgba(0,229,255,0)"/>
              </linearGradient>
            </defs>
            <path id="spark-fill" fill="url(#spark-grad)" d=""/>
            <path id="spark-line" fill="none" stroke="var(--accent)" stroke-width="1.6" d=""/>
          </svg>
        </div>
      </div>

      <!-- ══════════ ACTIFS ══════════ -->
      <div class="card" style="animation-delay:.15s; margin-bottom:22px;">
        <div class="section-title">Vos actifs</div>
        <div id="asset-list"></div>
      </div>

      <!-- ══════════ TRANSACTIONS ══════════ -->
      <div class="card" style="animation-delay:.2s;">
        <div class="section-title">Activité récente</div>
        <div id="tx-list"></div>
      </div>

    </main>
  </div>
</div>

""" + COMMON_JS + """
<script>
/* ═══════════════ Fake market data ═══════════════ */
const MARKETS = [
  {sym:'BTC', name:'Bitcoin',  price:59477,  change:+2.84, icon:'₿', color:'#f7931a'},
  {sym:'ETH', name:'Ethereum', price:2841,   change:+1.62, icon:'Ξ', color:'#627eea'},
  {sym:'SOL', name:'Solana',   price:142.30, change:-0.71, icon:'◎', color:'#14f195'},
  {sym:'XRP', name:'Ripple',   price:0.5217, change:+3.15, icon:'✕', color:'#25a768'},
  {sym:'ADA', name:'Cardano',  price:0.412,  change:-1.23, icon:'₳', color:'#0033ad'},
  {sym:'DOT', name:'Polkadot', price:6.42,   change:+0.48, icon:'●', color:'#e6007a'},
  {sym:'LINK',name:'Chainlink',price:14.20,  change:+4.02, icon:'⬡', color:'#2a5ada'},
  {sym:'AVAX',name:'Avalanche',price:31.85,  change:-0.94, icon:'▲', color:'#e84142'},
];

const HOLDINGS = [
  {sym:'BTC', qty:12.4821},
  {sym:'ETH', qty:4.812},
  {sym:'SOL', qty:182.40},
  {sym:'LINK',qty:340.0},
  {sym:'AVAX',qty:120.5},
];

/* ═══════════════ Ticker ═══════════════ */
function buildTicker(){
  const track = document.getElementById('ticker-track');
  const items = [];
  for (let rep=0; rep<2; rep++){
    for (const m of MARKETS){
      const dir = m.change >= 0 ? 'up' : 'down';
      const arrow = m.change >= 0 ? '▲' : '▼';
      items.push(`<span class="ticker-item">
        <strong style="color:${m.color}">${m.sym}</strong>
        <span>${m.price.toLocaleString('fr-FR')} €</span>
        <span class="${dir}">${arrow} ${m.change>0?'+':''}${m.change.toFixed(2)}%</span>
      </span>`);
    }
  }
  track.innerHTML = items.join('');
}
buildTicker();

/* ═══════════════ Sparkline ═══════════════ */
function buildSparkline(){
  const N = 60;
  const pts = [];
  let v = 100;
  for (let i=0; i<N; i++){
    v += (Math.random()-0.45)*4;
    v = Math.max(60, Math.min(160, v));
    pts.push(v);
  }
  const min = Math.min(...pts), max = Math.max(...pts);
  const norm = pts.map(p => 80 - ((p-min)/(max-min || 1))*70 - 5);
  const dLine = norm.map((y,i) => `${i===0?'M':'L'} ${(i/(N-1))*300} ${y}`).join(' ');
  const dFill = dLine + ` L 300 80 L 0 80 Z`;
  document.getElementById('spark-line').setAttribute('d', dLine);
  document.getElementById('spark-fill').setAttribute('d', dFill);
  // animated draw
  const line = document.getElementById('spark-line');
  const len = line.getTotalLength ? line.getTotalLength() : 400;
  line.style.strokeDasharray = len;
  line.style.strokeDashoffset = len;
  line.animate(
    [{strokeDashoffset: len}, {strokeDashoffset: 0}],
    {duration: 1400, easing: 'cubic-bezier(.2,.9,.3,1)', fill:'forwards'}
  );
}
buildSparkline();

/* ═══════════════ Asset list ═══════════════ */
function renderAssets(){
  const wrap = document.getElementById('asset-list');
  wrap.innerHTML = HOLDINGS.map(h => {
    const m = MARKETS.find(x => x.sym === h.sym);
    const val = h.qty * m.price;
    const cls = m.change >= 0 ? 'up' : 'down';
    const arrow = m.change >= 0 ? '▲' : '▼';
    return `<div class="asset-row">
      <div class="asset-icon" style="background:linear-gradient(135deg, ${m.color}, ${m.color}cc);">${m.icon}</div>
      <div>
        <div class="asset-name">${m.name}<small>${m.sym}</small></div>
        <div style="font-size:11.5px;color:var(--muted);font-family:var(--mono);margin-top:2px;">
          ${h.qty.toLocaleString('fr-FR')} ${m.sym}
        </div>
      </div>
      <div class="asset-amount">${m.price.toLocaleString('fr-FR')} €</div>
      <div class="asset-value ${cls}">${arrow} ${(val/1000).toFixed(1)} k€</div>
    </div>`;
  }).join('');
}
renderAssets();

/* ═══════════════ Transactions ═══════════════ */
const TXS = [
  {type:'in',  title:'Réception BTC',       sub:'bc1q…8f4k · 0x4a9b…2e71', amount:'+0.2841 BTC', time:'il y a 12 min'},
  {type:'out', title:'Envoi ETH',           sub:'0x71c3…b4a9 · gas 21 gwei', amount:'-1.250 ETH',  time:'il y a 1 h'},
  {type:'in',  title:'Staking reward SOL',  sub:'Validateur Everstake',      amount:'+2.14 SOL',   time:'il y a 3 h'},
  {type:'out', title:'Paiement marchand',   sub:'Épicerie fine · Paris',     amount:'-0.012 BTC',  time:'hier'},
  {type:'in',  title:'Swap BTC → LINK',     sub:'DEX Uniswap v4',            amount:'+340 LINK',   time:'hier'},
  {type:'in',  title:'Dépôt fiat',          sub:'Virement SEPA · Revolut',   amount:'+2 500 €',    time:'il y a 2 j'},
];
function renderTxs(){
  document.getElementById('tx-list').innerHTML = TXS.map(t => `
    <div class="tx-row">
      <div class="tx-icon ${t.type}">${t.type==='in'?'↓':'↑'}</div>
      <div>
        <div class="tx-main">${t.title}</div>
        <div class="tx-sub">${t.sub} · ${t.time}</div>
      </div>
      <div class="tx-amount ${t.type}">${t.amount}</div>
    </div>
  `).join('');
}
renderTxs();

/* ═══════════════ Live balance animation ═══════════════ */
function animateNumber(el, from, to, decimals=2, duration=1200){
  const start = performance.now();
  const step = now => {
    const t = Math.min(1, (now-start)/duration);
    const eased = 1 - Math.pow(1-t, 3);
    const v = from + (to-from)*eased;
    el.textContent = v.toFixed(decimals);
    if (t < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}
window.addEventListener('load', () => {
  const btcEl = document.getElementById('btc-total');
  const eurEl = document.getElementById('eur-total');
  animateNumber(btcEl, 0, 12.4821, 4, 1600);
  animateNumber(eurEl, 0, 742300, 0, 1600);
  btcEl.innerHTML = btcEl.textContent + ' <small>BTC</small>';
  eurEl.textContent = Number(eurEl.textContent).toLocaleString('fr-FR');

  // Clock sync
  const sync = () => {
    const d = new Date();
    document.getElementById('last-sync').textContent =
      'Dernière synchronisation : ' + d.toLocaleTimeString('fr-FR');
  };
  sync(); setInterval(sync, 1000);

  // Welcome toast
  setTimeout(() => toast('Coffre déverrouillé avec succès.', 'success'), 500);
  setTimeout(() => toast('12 actifs synchronisés · réseau Bitcoin opérationnel.', 'info', 4200), 1400);
});

/* ═══════════════ Live market ticks ═══════════════ */
setInterval(() => {
  const m = MARKETS[Math.floor(Math.random()*MARKETS.length)];
  const delta = (Math.random()-0.5)*0.4;
  m.change = +(m.change + delta).toFixed(2);
  m.price  = +(m.price * (1 + delta/200)).toFixed(m.price < 5 ? 4 : 2);
  const priceEl = document.getElementById('btc-price');
  const btc = MARKETS[0];
  priceEl.textContent = btc.price.toLocaleString('fr-FR') + ' €';
  priceEl.className = 'price ' + (btc.change >= 0 ? 'up' : 'down');
  document.getElementById('pct-24h').textContent =
    (btc.change>=0?'▲ +':'▼ ') + btc.change.toFixed(2) + '% (24h)';
  document.getElementById('pct-24h').style.color =
    btc.change>=0 ? 'var(--success)' : 'var(--danger)';
}, 2600);

/* ═══════════════ Nav interactions ═══════════════ */
document.querySelectorAll('.nav-item[data-page]').forEach(el => {
  el.addEventListener('click', () => {
    document.querySelectorAll('.nav-item').forEach(x => x.classList.remove('active'));
    el.classList.add('active');
    const page = el.dataset.page;
    const labels = {
      wallet:'Portefeuille principal',
      tx:'Historique complet des transactions',
      market:'Marché & cotations en direct',
      stacking:'Staking & rendements',
      security:'Sécurité du coffre',
      settings:'Paramètres'
    };
    document.querySelector('.page-head h2').textContent = labels[page] || 'Portefeuille';
    if (page !== 'wallet') toast('Section « ' + (labels[page]||page) + ' » — démonstration.', 'info');
  });
});

/* ═══════════════ Actions ═══════════════ */
document.querySelectorAll('.action-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const a = btn.dataset.action;
    const msgs = {
      receive:'Adresse de réception copiée : bc1q7f4k…8e2a',
      send:'Fenêtre d\'envoi — démonstration',
      swap:'Échange BTC ⇄ ETH — démonstration',
      buy:'Achat fiat → crypto — démonstration'
    };
    toast(msgs[a] || 'Action', 'success');
  });
});

/* ═══════════════ Random ambient pings ═══════════════ */
setInterval(() => {
  if (Math.random() < 0.25) Sound.coin();
}, 6000);
</script>
</body>
</html>
"""

# ═══════════════════════════════════════════════════════════════════════
#  LOGIQUE BACKEND (inchangée)
# ═══════════════════════════════════════════════════════════════════════
def users_file_exists():
    return os.path.exists(USERS_FILE)


def write_user_hash(login, password):
    h = hashlib.md5(password.encode()).hexdigest()
    with open(USERS_FILE, "w") as f:
        f.write(f"{login}:{h}\n")


def check_password(login, password):
    if not users_file_exists():
        return False
    with open(USERS_FILE) as f:
        for line in f:
            u, h = line.strip().split(":")
            if u == login and hashlib.md5(password.encode()).hexdigest() == h:
                return True
    return False


@app.route("/", methods=["GET", "POST"])
def index():
    if not users_file_exists():
        if request.method == "POST":
            pwd = request.form["password"]
            write_user_hash(ADMIN_LOGIN, pwd)
            return redirect("/")
        return render_template_string(SETUP_PAGE)

    if session.get("logged_in"):
        return render_template_string(DASHBOARD_PAGE, login=ADMIN_LOGIN)

    error = None
    if request.method == "POST":
        login = request.form["login"]
        pwd = request.form["password"]
        if check_password(login, pwd):
            session["logged_in"] = True
            return redirect("/")
        error = "Identifiants invalides."
    return render_template_string(LOGIN_PAGE, error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# --- Faille simulée : backup de la base de comptes oublié en accès libre ---
@app.route("/backup/users.txt")
def backup_leak():
    if not users_file_exists():
        return "Aucun compte configuré.", 404
    with open(USERS_FILE) as f:
        return f.read(), 200, {"Content-Type": "text/plain"}


if __name__ == "__main__":
    if users_file_exists():
        os.remove(USERS_FILE)
        print(f"{USERS_FILE} supprimé (reset avant lancement).")
    print("Client démarré sur http://0.0.0.0:5000")
    print("Faille de démo exposée sur /backup/users.txt (format John: login:hash)")
    app.run(host="0.0.0.0", port=5000, debug=False)