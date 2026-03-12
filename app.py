from flask import Flask, jsonify
import redis
import os
import psutil
import time

app = Flask(__name__)

redis_host = os.environ.get("REDIS_HOST", "localhost")
redis_port = int(os.environ.get("REDIS_PORT", 6379))
r = redis.Redis(host=redis_host, port=redis_port)

def get_milestone_message(count):
    if count == 1:        return "🚀 First contact established."
    elif count == 5:      return "⚡ 5 visits — System warming up."
    elif count == 10:     return "🔥 10 visits — You're on a streak!"
    elif count == 25:     return "💥 25 visits — Impressive persistence."
    elif count == 50:     return "🌌 50 visits — You live here now."
    elif count == 100:    return "👾 100 visits — LEGENDARY STATUS."
    elif count % 10 == 0: return f"🛸 {count} visits — The matrix notices you."
    else:                 return ""

def get_system_health():
    cpu  = psutil.cpu_percent(interval=0.1)
    mem  = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    net  = psutil.net_io_counters()
    secs = int(time.time() - psutil.boot_time())
    uptime = f"{secs//3600}h {(secs%3600)//60}m"
    cpu_count = psutil.cpu_count()
    cpu_freq  = psutil.cpu_freq()

    def color(v): return "#c9a84c" if v < 60 else "#e8c56a" if v < 85 else "#e05c5c"
    def label(v): return "NOMINAL" if v < 60 else "MODERATE" if v < 85 else "CRITICAL"

    return dict(
        cpu=round(cpu,1),            cpu_color=color(cpu),          cpu_label=label(cpu),
        cpu_count=cpu_count,         cpu_freq=round(cpu_freq.current,0) if cpu_freq else 0,
        mem=round(mem.percent,1),    mem_color=color(mem.percent),  mem_label=label(mem.percent),
        mem_total=round(mem.total/(1024**3),1),
        mem_used_gb=round(mem.used/(1024**3),1),
        mem_available=round(mem.available/(1024**2)),
        disk=round(disk.percent,1),  disk_color=color(disk.percent), disk_label=label(disk.percent),
        disk_total=round(disk.total/(1024**3),1),
        disk_used_gb=round(disk.used/(1024**3),1),
        disk_free=round(disk.free/(1024**3),1),
        net_sent=round(net.bytes_sent/(1024**2),1),
        net_recv=round(net.bytes_recv/(1024**2),1),
        uptime=uptime, uptime_secs=secs,
    )

@app.route("/health")
def health_api():
    return jsonify(get_system_health())

@app.route("/")
def hello():
    count     = r.incr("visits")
    milestone = get_milestone_message(count)
    h         = get_system_health()

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CI/CD Automation Project</title>
    <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Oswald:wght@300;400;500;600;700&family=Share+Tech+Mono&display=swap" rel="stylesheet">
    <style>
        *, *::before, *::after {{ box-sizing:border-box; margin:0; padding:0; }}
        :root {{
            --gold:        #c9a84c;
            --gold-light:  #f0dea0;
            --gold-dim:    rgba(201,168,76,0.12);
            --gold-border: rgba(201,168,76,0.25);
            --navy:        #040c18;
            --navy-card:   rgba(6,18,36,0.9);
            --text:        #dce8f5;
            --dim:         rgba(220,232,245,0.35);
        }}
        html, body {{ height:100%; overflow:hidden; }}
        body {{ background:var(--navy); font-family:'Oswald',sans-serif; color:var(--text); cursor:default; transition:background 0.8s ease; }}
        .bg-radial {{ position:fixed; inset:0; z-index:0; pointer-events:none;
            background:
                radial-gradient(ellipse 90% 60% at 50% -10%, rgba(201,168,76,0.10) 0%, transparent 65%),
                radial-gradient(ellipse 50% 50% at 10% 90%, rgba(10,40,90,0.7) 0%, transparent 55%),
                radial-gradient(ellipse 50% 50% at 90% 90%, rgba(10,40,90,0.7) 0%, transparent 55%); }}
        .bg-grid {{ position:fixed; inset:0; z-index:0; pointer-events:none;
            background-image: linear-gradient(rgba(201,168,76,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(201,168,76,0.04) 1px, transparent 1px);
            background-size:48px 48px; }}
        .ring {{ position:fixed; border-radius:50%; pointer-events:none; z-index:0; border:1px solid rgba(201,168,76,0.07); }}
        .ring-1 {{ width:600px; height:600px; top:50%; left:50%; transform:translate(-50%,-50%); animation:spinR 40s linear infinite; }}
        .ring-2 {{ width:850px; height:850px; top:50%; left:50%; transform:translate(-50%,-50%); border-style:dashed; animation:spinR 60s linear infinite reverse; }}
        .ring-3 {{ width:1100px; height:1100px; top:50%; left:50%; transform:translate(-50%,-50%); animation:spinR 80s linear infinite; }}
        @keyframes spinR {{ from {{ transform:translate(-50%,-50%) rotate(0deg); }} to {{ transform:translate(-50%,-50%) rotate(360deg); }} }}
        .corner {{ position:fixed; width:48px; height:48px; pointer-events:none; z-index:3; opacity:0.6; }}
        .corner-tl {{ top:20px; left:20px; border-top:1px solid var(--gold); border-left:1px solid var(--gold); }}
        .corner-tr {{ top:20px; right:20px; border-top:1px solid var(--gold); border-right:1px solid var(--gold); }}
        .corner-bl {{ bottom:20px; left:20px; border-bottom:1px solid var(--gold); border-left:1px solid var(--gold); }}
        .corner-br {{ bottom:20px; right:20px; border-bottom:1px solid var(--gold); border-right:1px solid var(--gold); }}

        .dashboard {{ position:relative; z-index:10; height:100vh; display:grid; grid-template-rows:auto 1fr auto auto; padding:20px 28px 16px; gap:10px; }}

        /* TOP BAR */
        .topbar {{ display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--gold-border); padding-bottom:10px; animation:fadeDown 0.7s ease forwards; }}
        .topbar-left {{ display:flex; align-items:center; gap:12px; }}
        .logo-hex {{ width:36px; height:36px; flex-shrink:0; }}
        .logo-hex svg {{ width:100%; height:100%; }}
        .top-titles {{ display:flex; flex-direction:column; gap:1px; }}
        .eyebrow {{ font-family:'Share Tech Mono',monospace; font-size:0.55rem; letter-spacing:4px; color:var(--gold); opacity:0.7; text-transform:uppercase; }}
        .top-title {{ font-family:'Bebas Neue',cursive; font-size:1rem; letter-spacing:3px; color:var(--gold-light); }}
        .topbar-right {{ text-align:right; font-family:'Share Tech Mono',monospace; font-size:0.68rem; color:var(--dim); line-height:1.7; }}
        #clock {{ color:var(--gold); font-size:0.95rem; text-shadow:0 0 10px rgba(201,168,76,0.4); }}

        /* HERO */
        .hero {{ display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; gap:10px; position:relative; }}
        .orb {{ position:absolute; width:280px; height:280px; border-radius:50%; background:radial-gradient(ellipse at center, rgba(201,168,76,0.08) 0%, transparent 70%); border:1px solid rgba(201,168,76,0.12); top:50%; left:50%; transform:translate(-50%,-50%); pointer-events:none; animation:orbPulse 4s ease-in-out infinite; }}
        .orb-inner {{ position:absolute; width:160px; height:160px; border-radius:50%; background:radial-gradient(ellipse at center, rgba(201,168,76,0.12) 0%, transparent 70%); top:50%; left:50%; transform:translate(-50%,-50%); pointer-events:none; animation:orbPulse 3s ease-in-out infinite reverse; }}
        @keyframes orbPulse {{ 0%,100% {{ opacity:0.6; transform:translate(-50%,-50%) scale(1); }} 50% {{ opacity:1; transform:translate(-50%,-50%) scale(1.05); }} }}
        .hero-eyebrow {{ font-family:'Share Tech Mono',monospace; font-size:0.6rem; letter-spacing:7px; color:var(--gold); opacity:0; animation:fadeUp 0.5s 0.3s ease forwards; }}
        .hero-greeting {{ font-family:'Oswald',sans-serif; font-size:clamp(0.9rem,2vw,1.1rem); font-weight:300; letter-spacing:6px; color:var(--dim); text-transform:uppercase; opacity:0; animation:fadeUp 0.5s 0.5s ease forwards; }}
        .hero-title {{ font-family:'Bebas Neue',cursive; font-size:clamp(2.2rem,5vw,3.8rem); line-height:1.05; letter-spacing:4px;
            background:linear-gradient(160deg, #fff 0%, var(--gold-light) 30%, var(--gold) 65%, #8a6520 100%);
            -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
            filter:drop-shadow(0 0 30px rgba(201,168,76,0.4));
            opacity:0; animation:fadeUp 0.7s 0.7s cubic-bezier(0.16,1,0.3,1) forwards; }}
        .hero-typewriter {{ display:inline-block; overflow:hidden; white-space:nowrap; border-right:3px solid var(--gold); animation:typing 2.5s steps(24,end) 1s forwards, blink 0.8s step-end infinite; max-width:0; }}
        @keyframes typing {{ from {{ max-width:0; }} to {{ max-width:100%; }} }}
        @keyframes blink   {{ 50% {{ border-color:transparent; }} }}
        .hero-desc {{ font-family:'Oswald',sans-serif; font-size:0.78rem; font-weight:300; letter-spacing:1.5px; color:var(--dim); max-width:520px; line-height:1.6; opacity:0; animation:fadeUp 0.5s 0.9s ease forwards; }}

        /* KPI */
        .kpi-row {{ display:flex; gap:12px; justify-content:center; opacity:0; animation:fadeUp 0.6s 1.1s ease forwards; }}
        .kpi-pill {{ background:var(--gold-dim); border:1px solid var(--gold-border); border-radius:10px; padding:8px 20px; text-align:center; position:relative; overflow:hidden; min-width:100px; transition:box-shadow 0.3s; }}
        .kpi-pill:hover {{ box-shadow:0 0 20px rgba(201,168,76,0.2); }}
        .kpi-pill::before {{ content:''; position:absolute; top:0; left:0; right:0; height:1px; background:linear-gradient(90deg,transparent,var(--gold),transparent); }}
        .kpi-label {{ font-family:'Share Tech Mono',monospace; font-size:0.48rem; letter-spacing:3px; color:var(--dim); text-transform:uppercase; margin-bottom:3px; }}
        .kpi-value {{ font-family:'Bebas Neue',cursive; font-size:1.5rem; color:var(--gold); text-shadow:0 0 14px rgba(201,168,76,0.5); }}
        .kpi-value.online {{ font-size:0.78rem; color:#5dcc7a; text-shadow:0 0 8px rgba(93,204,122,0.5); padding-top:6px; font-family:'Share Tech Mono',monospace; }}

        /* DIVIDER */
        .gold-rule {{ display:flex; align-items:center; gap:10px; opacity:0; animation:fadeUp 0.5s 1.2s ease forwards; }}
        .gold-rule::before, .gold-rule::after {{ content:''; flex:1; height:1px; background:linear-gradient(90deg,transparent,var(--gold-border),transparent); }}
        .gold-diamond {{ width:5px; height:5px; background:var(--gold); transform:rotate(45deg); box-shadow:0 0 6px var(--gold); }}

        /* MILESTONE */
        .milestone {{ font-family:'Share Tech Mono',monospace; font-size:0.68rem; letter-spacing:2px; color:var(--gold); background:var(--gold-dim); border:1px solid var(--gold-border); border-radius:6px; padding:5px 16px; text-align:center; opacity:0; animation:fadeUp 0.5s 1.3s ease forwards, goldPulse 2.5s 1.8s ease-in-out infinite; }}
        @keyframes goldPulse {{ 0%,100% {{ box-shadow:0 0 6px rgba(201,168,76,0.1); }} 50% {{ box-shadow:0 0 16px rgba(201,168,76,0.35); }} }}

        /* HEALTH */
        .health-section {{ opacity:0; animation:fadeUp 0.6s 1.4s ease forwards; }}
        .health-header {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:7px; }}
        .section-label {{ font-family:'Share Tech Mono',monospace; font-size:0.52rem; letter-spacing:4px; color:var(--dim); text-transform:uppercase; }}
        .refresh-badge {{ font-family:'Share Tech Mono',monospace; font-size:0.5rem; color:var(--dim); letter-spacing:2px; display:flex; align-items:center; gap:5px; }}
        .refresh-dot {{ width:5px; height:5px; border-radius:50%; background:var(--gold); animation:pulse 1s ease-in-out infinite; }}
        .refresh-dot.spin {{ animation:rSpin 0.8s linear infinite; }}
        @keyframes rSpin {{ to {{ transform:rotate(360deg); }} }}
        .health-grid {{ display:grid; grid-template-columns:repeat(5,1fr); gap:8px; }}
        .hcard {{ background:var(--navy-card); border:1px solid var(--gold-border); border-radius:10px; padding:10px 8px; text-align:center; position:relative; overflow:hidden; cursor:pointer; transition:border-color 0.3s, box-shadow 0.3s, transform 0.2s; }}
        .hcard:hover {{ border-color:var(--gold); box-shadow:0 0 20px rgba(201,168,76,0.15); transform:translateY(-3px); }}
        .hcard::before {{ content:''; position:absolute; top:0; left:0; right:0; height:1px; background:linear-gradient(90deg,transparent,var(--gold),transparent); opacity:0.6; }}
        .hcard::after {{ content:''; position:absolute; inset:0; border-radius:10px; background:radial-gradient(ellipse at 50% 0%, rgba(201,168,76,0.06), transparent 70%); opacity:0; transition:opacity 0.3s; pointer-events:none; }}
        .hcard:hover::after {{ opacity:1; }}
        .hcard-icon  {{ font-size:1rem; margin-bottom:3px; pointer-events:none; }}
        .hcard-name  {{ font-family:'Share Tech Mono',monospace; font-size:0.46rem; letter-spacing:2px; color:var(--dim); text-transform:uppercase; margin-bottom:4px; pointer-events:none; }}
        .hcard-val   {{ font-family:'Bebas Neue',cursive; font-size:0.9rem; line-height:1; margin-bottom:4px; transition:color 0.4s; pointer-events:none; }}
        .hcard-badge {{ font-family:'Share Tech Mono',monospace; font-size:0.4rem; letter-spacing:1.5px; padding:2px 6px; border-radius:999px; border:1px solid; display:inline-block; margin-bottom:5px; text-transform:uppercase; pointer-events:none; }}
        .progress-track {{ width:100%; height:3px; background:rgba(255,255,255,0.05); border-radius:999px; overflow:hidden; }}
        .progress-fill  {{ height:100%; border-radius:999px; transition:width 0.7s ease; }}

        /* STACK */
        .stack-section {{ border-top:1px solid var(--gold-border); padding-top:9px; opacity:0; animation:fadeUp 0.6s 1.5s ease forwards; }}
        .stack-inner {{ display:flex; flex-wrap:wrap; justify-content:center; gap:6px; }}
        .stack-badge {{ display:inline-flex; align-items:center; gap:5px; padding:3px 12px; border:1px solid var(--gold-border); border-radius:999px; background:var(--gold-dim); font-family:'Share Tech Mono',monospace; font-size:0.56rem; letter-spacing:1.5px; color:var(--gold-light); text-transform:uppercase; transition:all 0.25s; }}
        .stack-badge:hover {{ border-color:var(--gold); color:var(--gold); box-shadow:0 0 10px rgba(201,168,76,0.2); transform:translateY(-1px); }}

        /* MODAL */
        .modal-overlay {{ position:fixed; inset:0; z-index:100; background:rgba(4,12,24,0.88); backdrop-filter:blur(8px); display:flex; align-items:center; justify-content:center; opacity:0; pointer-events:none; transition:opacity 0.3s ease; }}
        .modal-overlay.show {{ opacity:1; pointer-events:all; }}
        .modal {{ background:linear-gradient(145deg,#071428 0%,#040c18 100%); border:1px solid var(--gold-border); border-radius:18px; padding:30px 34px; min-width:340px; max-width:440px; width:92%; position:relative; box-shadow:0 0 60px rgba(201,168,76,0.12); transform:scale(0.88) translateY(24px); transition:transform 0.35s cubic-bezier(0.16,1,0.3,1); }}
        .modal-overlay.show .modal {{ transform:scale(1) translateY(0); }}
        .modal::before {{ content:''; position:absolute; top:0; left:10%; right:10%; height:1px; background:linear-gradient(90deg,transparent,var(--gold),transparent); }}
        .modal-close {{ position:absolute; top:14px; right:18px; font-family:'Share Tech Mono',monospace; font-size:0.65rem; color:var(--dim); cursor:pointer; letter-spacing:2px; transition:color 0.2s; }}
        .modal-close:hover {{ color:var(--gold); }}
        .modal-top {{ display:flex; align-items:center; gap:14px; margin-bottom:20px; }}
        .modal-icon-wrap {{ width:52px; height:52px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:1.4rem; border:1px solid var(--gold-border); background:var(--gold-dim); flex-shrink:0; }}
        .modal-title  {{ font-family:'Bebas Neue',cursive; font-size:1.2rem; color:var(--gold); letter-spacing:3px; }}
        .modal-status {{ font-family:'Share Tech Mono',monospace; font-size:0.55rem; letter-spacing:3px; color:var(--dim); margin-top:3px; }}
        .modal-big {{ font-family:'Bebas Neue',cursive; font-size:3.2rem; line-height:1; text-align:center; margin:16px 0; }}
        .modal-bar-wrap {{ margin-bottom:20px; }}
        .modal-bar-label {{ font-family:'Share Tech Mono',monospace; font-size:0.52rem; letter-spacing:2px; color:var(--dim); margin-bottom:6px; display:flex; justify-content:space-between; }}
        .modal-bar-track {{ width:100%; height:6px; background:rgba(255,255,255,0.05); border-radius:999px; overflow:hidden; }}
        .modal-bar-fill  {{ height:100%; border-radius:999px; transition:width 0.8s ease; }}
        .modal-details {{ display:grid; grid-template-columns:1fr 1fr; gap:8px; }}
        .mdet {{ background:rgba(201,168,76,0.05); border:1px solid var(--gold-border); border-radius:8px; padding:10px 13px; }}
        .mdet-label {{ font-family:'Share Tech Mono',monospace; font-size:0.48rem; letter-spacing:2px; color:var(--dim); text-transform:uppercase; margin-bottom:4px; }}
        .mdet-val   {{ font-family:'Bebas Neue',cursive; font-size:1rem; color:var(--gold-light); }}

        /* FOOTER */
        .footer {{ display:flex; justify-content:space-between; align-items:center; border-top:1px solid var(--gold-border); padding-top:9px; font-family:'Share Tech Mono',monospace; font-size:0.55rem; color:var(--dim); letter-spacing:2px; opacity:0; animation:fadeUp 0.6s 1.6s ease forwards; }}
        .status-dot {{ display:inline-block; width:5px; height:5px; border-radius:50%; background:#5dcc7a; box-shadow:0 0 6px #5dcc7a; margin-right:6px; animation:pulse 2s ease-in-out infinite; }}
        @keyframes pulse {{ 0%,100% {{ opacity:1; }} 50% {{ opacity:0.3; }} }}
        .ripple {{ position:fixed; border-radius:50%; border:1px solid rgba(201,168,76,0.5); pointer-events:none; z-index:5; animation:rippleOut 1s ease-out forwards; transform:translate(-50%,-50%); }}
        @keyframes rippleOut {{ from {{ width:0; height:0; opacity:0.7; }} to {{ width:600px; height:600px; opacity:0; }} }}
        @keyframes fadeUp   {{ from {{ opacity:0; transform:translateY(16px); }} to {{ opacity:1; transform:translateY(0); }} }}
        @keyframes fadeDown {{ from {{ opacity:0; transform:translateY(-16px); }} to {{ opacity:1; transform:translateY(0); }} }}
    </style>
</head>
<body>
    <div class="bg-radial"></div>
    <div class="bg-grid"></div>
    <div class="ring ring-1"></div>
    <div class="ring ring-2"></div>
    <div class="ring ring-3"></div>
    <div class="corner corner-tl"></div>
    <div class="corner corner-tr"></div>
    <div class="corner corner-bl"></div>
    <div class="corner corner-br"></div>

    <!-- MODAL -->
    <div class="modal-overlay" id="modalOverlay" onclick="closeModal(event)">
        <div class="modal">
            <div class="modal-close" onclick="closeModal(null,true)">[ CLOSE ]</div>
            <div class="modal-top">
                <div class="modal-icon-wrap" id="mIcon"></div>
                <div>
                    <div class="modal-title"  id="mTitle"></div>
                    <div class="modal-status" id="mStatus"></div>
                </div>
            </div>
            <div class="modal-big" id="mBig"></div>
            <div class="modal-bar-wrap">
                <div class="modal-bar-label"><span>UTILISATION</span><span id="mBarPct"></span></div>
                <div class="modal-bar-track"><div class="modal-bar-fill" id="mBarFill"></div></div>
            </div>
            <div class="modal-details" id="mDetails"></div>
        </div>
    </div>

    <div class="dashboard">

        <!-- TOP BAR -->
        <div class="topbar">
            <div class="topbar-left">
                <div class="logo-hex">
                    <svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <polygon points="20,2 36,11 36,29 20,38 4,29 4,11" stroke="#c9a84c" stroke-width="1.2" fill="rgba(201,168,76,0.08)"/>
                        <polygon points="20,8 30,14 30,26 20,32 10,26 10,14" stroke="#c9a84c" stroke-width="0.6" fill="rgba(201,168,76,0.05)" opacity="0.6"/>
                        <circle cx="20" cy="20" r="4" fill="#c9a84c" opacity="0.8"/>
                    </svg>
                </div>
                <div class="top-titles">
                    <div class="eyebrow">// Live Production Dashboard</div>
                    <div class="top-title">CI/CD Automation Project</div>
                </div>
            </div>
            <div class="topbar-right">
                <div id="date"></div>
                <div id="clock">00:00:00</div>
            </div>
        </div>

        <!-- HERO -->
        <div class="hero">
            <div class="orb"></div>
            <div class="orb-inner"></div>
            <div class="hero-eyebrow">// SYSTEM ONLINE · OPERATOR SESSION ACTIVE</div>
            <div class="hero-greeting">Welcome Back</div>
            <div class="hero-title">
                <span class="hero-typewriter">CI/CD Automation Project</span>
            </div>
            <div class="hero-desc">
                A fully automated CI/CD application deployed on AWS EC2 —
                built with Flask, Redis, Docker &amp; Jenkins
            </div>
            <div class="kpi-row">
                <div class="kpi-pill">
                    <div class="kpi-label">Total Visits</div>
                    <div class="kpi-value" id="visitCount">0</div>
                </div>
                <div class="kpi-pill">
                    <div class="kpi-label">App Status</div>
                    <div class="kpi-value online">● ONLINE</div>
                </div>
                <div class="kpi-pill">
                    <div class="kpi-label">Uptime</div>
                    <div class="kpi-value" style="font-size:1rem;padding-top:4px;" id="heroUptime">{h['uptime']}</div>
                </div>
            </div>
            {"<div class='milestone'>" + milestone + "</div>" if milestone else ""}
        </div>

        <!-- DIVIDER -->
        <div class="gold-rule"><div class="gold-diamond"></div></div>

        <!-- HEALTH -->
        <div class="health-section">
            <div class="health-header">
                <div class="section-label">// System Health Monitor — Click any card for details</div>
                <div class="refresh-badge">
                    <div class="refresh-dot" id="refreshDot"></div>
                    <span id="refreshLabel">LIVE · 5s</span>
                </div>
            </div>
            <div class="health-grid">
                <div class="hcard" onclick="openModal('cpu')">
                    <div class="hcard-icon">⚙️</div>
                    <div class="hcard-name">CPU</div>
                    <div class="hcard-val" id="cpu-val" style="color:{h['cpu_color']};text-shadow:0 0 8px {h['cpu_color']};">{h['cpu']}%</div>
                    <div class="hcard-badge" id="cpu-badge" style="color:{h['cpu_color']};border-color:{h['cpu_color']};">{h['cpu_label']}</div>
                    <div class="progress-track"><div class="progress-fill" id="cpu-bar" style="width:{h['cpu']}%;background:{h['cpu_color']};"></div></div>
                </div>
                <div class="hcard" onclick="openModal('mem')">
                    <div class="hcard-icon">🧠</div>
                    <div class="hcard-name">Memory</div>
                    <div class="hcard-val" id="mem-val" style="color:{h['mem_color']};text-shadow:0 0 8px {h['mem_color']};">{h['mem']}%</div>
                    <div class="hcard-badge" id="mem-badge" style="color:{h['mem_color']};border-color:{h['mem_color']};">{h['mem_label']}</div>
                    <div class="progress-track"><div class="progress-fill" id="mem-bar" style="width:{h['mem']}%;background:{h['mem_color']};"></div></div>
                </div>
                <div class="hcard" onclick="openModal('disk')">
                    <div class="hcard-icon">💾</div>
                    <div class="hcard-name">Disk</div>
                    <div class="hcard-val" id="disk-val" style="color:{h['disk_color']};text-shadow:0 0 8px {h['disk_color']};">{h['disk']}%</div>
                    <div class="hcard-badge" id="disk-badge" style="color:{h['disk_color']};border-color:{h['disk_color']};">{h['disk_label']}</div>
                    <div class="progress-track"><div class="progress-fill" id="disk-bar" style="width:{h['disk']}%;background:{h['disk_color']};"></div></div>
                </div>
                <div class="hcard" onclick="openModal('uptime')">
                    <div class="hcard-icon">⏱️</div>
                    <div class="hcard-name">Uptime</div>
                    <div class="hcard-val" id="uptime-val" style="color:#c9a84c;text-shadow:0 0 8px #c9a84c;font-size:0.7rem;padding-top:3px;">{h['uptime']}</div>
                    <div class="hcard-badge" id="uptime-badge" style="color:#c9a84c;border-color:#c9a84c;">STABLE</div>
                    <div class="progress-track"><div class="progress-fill" id="uptime-bar" style="width:100%;background:#c9a84c;"></div></div>
                </div>
                <div class="hcard" onclick="openModal('flask')">
                    <div class="hcard-icon">🌶️</div>
                    <div class="hcard-name">Flask</div>
                    <div class="hcard-val" id="flask-val" style="color:#5dcc7a;text-shadow:0 0 8px #5dcc7a;font-size:0.65rem;padding-top:3px;">SERVING</div>
                    <div class="hcard-badge" id="flask-badge" style="color:#5dcc7a;border-color:#5dcc7a;">ONLINE</div>
                    <div class="progress-track"><div class="progress-fill" id="flask-bar" style="width:100%;background:#5dcc7a;"></div></div>
                </div>
            </div>
        </div>

        <!-- STACK -->
        <div class="stack-section">
            <div class="stack-inner">
                <span class="stack-badge">🐍 Python 3.11</span>
                <span class="stack-badge">🌶️ Flask</span>
                <span class="stack-badge">🗄️ Redis</span>
                <span class="stack-badge">🐳 Docker</span>
                <span class="stack-badge">📦 Docker Compose</span>
                <span class="stack-badge">🔧 Jenkins CI/CD</span>
                <span class="stack-badge">🐙 GitHub</span>
                <span class="stack-badge">🏔️ Docker Hub</span>
                <span class="stack-badge">☁️ AWS EC2</span>
                <span class="stack-badge">📊 Psutil</span>
                <span class="stack-badge">⚡ DevOps Pipeline</span>
            </div>
        </div>

        <!-- FOOTER -->
        <div class="footer">
            <div><span class="status-dot"></span>ALL SYSTEMS NOMINAL</div>
            <div>CLOUD &amp; DEVOPS · PRODUCTION ENVIRONMENT</div>
            <div>[ CLICK BACKGROUND TO SHIFT THEME ]</div>
        </div>
    </div>

    <script>
        function updateClock() {{
            const now = new Date();
            document.getElementById('clock').textContent = now.toTimeString().split(' ')[0];
            document.getElementById('date').textContent  = now.toLocaleDateString('en-US',{{ weekday:'long',year:'numeric',month:'long',day:'numeric' }});
        }}
        updateClock(); setInterval(updateClock, 1000);

        function animateCount(target, duration=1400) {{
            const el = document.getElementById('visitCount');
            const t0 = performance.now();
            function step(now) {{
                const p = Math.min((now-t0)/duration,1);
                const e = 1-Math.pow(1-p,4);
                el.textContent = Math.floor(e*target);
                if (p<1) requestAnimationFrame(step); else el.textContent=target;
            }}
            requestAnimationFrame(step);
        }}
        animateCount({count});

        let hd = {{
            cpu:{h['cpu']}, cpu_color:"{h['cpu_color']}", cpu_label:"{h['cpu_label']}",
            cpu_count:{h['cpu_count']}, cpu_freq:{h['cpu_freq']},
            mem:{h['mem']}, mem_color:"{h['mem_color']}", mem_label:"{h['mem_label']}",
            mem_total:{h['mem_total']}, mem_used_gb:{h['mem_used_gb']}, mem_available:{h['mem_available']},
            disk:{h['disk']}, disk_color:"{h['disk_color']}", disk_label:"{h['disk_label']}",
            disk_total:{h['disk_total']}, disk_used_gb:{h['disk_used_gb']}, disk_free:{h['disk_free']},
            net_sent:{h['net_sent']}, net_recv:{h['net_recv']},
            uptime:"{h['uptime']}", uptime_secs:{h['uptime_secs']},
        }};

        const defs = {{
            cpu:    d=>({{ icon:'⚙️', title:'CPU PROCESSOR',  status:`${{d.cpu_count}} Cores · ${{d.cpu_freq}} MHz`, big:`${{d.cpu}}%`,  color:d.cpu_color,  pct:d.cpu,  details:[['Load',`${{d.cpu}}%`],['Cores',d.cpu_count],['Frequency',`${{d.cpu_freq}} MHz`],['Status',d.cpu_label]] }}),
            mem:    d=>({{ icon:'🧠', title:'MEMORY (RAM)',   status:`${{d.mem_total}} GB Total`,                     big:`${{d.mem}}%`,  color:d.mem_color,  pct:d.mem,  details:[['Used',`${{d.mem_used_gb}} GB`],['Total',`${{d.mem_total}} GB`],['Available',`${{d.mem_available}} MB`],['Status',d.mem_label]] }}),
            disk:   d=>({{ icon:'💾', title:'DISK STORAGE',  status:`${{d.disk_total}} GB Total`,                    big:`${{d.disk}}%`, color:d.disk_color, pct:d.disk, details:[['Used',`${{d.disk_used_gb}} GB`],['Total',`${{d.disk_total}} GB`],['Free',`${{d.disk_free}} GB`],['Status',d.disk_label]] }}),
            uptime: d=>({{ icon:'⏱️', title:'SYSTEM UPTIME', status:'Server Running Time',                           big:d.uptime,       color:'#c9a84c',    pct:100,    details:[['Uptime',d.uptime],['Seconds',d.uptime_secs],['Net Sent',`${{d.net_sent}} MB`],['Net Recv',`${{d.net_recv}} MB`]] }}),
            flask:  d=>({{ icon:'🌶️', title:'FLASK APP',    status:'Web Application · Active',                      big:'SERVING',      color:'#5dcc7a',    pct:100,    details:[['Status','ONLINE'],['Framework','Flask'],['Language','Python 3.11'],['Port','Internal']] }}),
        }};

        let activeCard = null;
        function openModal(type) {{
            activeCard = type;
            const m = defs[type](hd);
            document.getElementById('mIcon').textContent   = m.icon;
            document.getElementById('mTitle').textContent  = m.title;
            document.getElementById('mStatus').textContent = m.status;
            document.getElementById('mBig').textContent    = m.big;
            document.getElementById('mBig').style.color    = m.color;
            document.getElementById('mBig').style.textShadow = `0 0 24px ${{m.color}}`;
            document.getElementById('mBarPct').textContent = typeof m.pct==='number' ? m.pct+'%' : m.pct;
            const fill = document.getElementById('mBarFill');
            fill.style.background = m.color; fill.style.width='0%';
            setTimeout(()=>fill.style.width=m.pct+'%',60);
            document.getElementById('mDetails').innerHTML = m.details.map(([l,v])=>
                `<div class="mdet"><div class="mdet-label">${{l}}</div><div class="mdet-val">${{v}}</div></div>`
            ).join('');
            document.getElementById('modalOverlay').classList.add('show');
        }}
        function closeModal(e, force=false) {{
            if (force||(e&&e.target===document.getElementById('modalOverlay'))) {{
                document.getElementById('modalOverlay').classList.remove('show');
                activeCard=null;
            }}
        }}

        let countdown=5;
        function refreshHealth() {{
            const dot=document.getElementById('refreshDot'), lbl=document.getElementById('refreshLabel');
            dot.classList.add('spin'); lbl.textContent='REFRESHING...';
            fetch('/health').then(r=>r.json()).then(d=>{{
                hd=d;
                const cards=[
                    {{id:'cpu',   val:`${{d.cpu}}%`,  color:d.cpu_color,  badge:d.cpu_label,  pct:d.cpu,  fs:null}},
                    {{id:'mem',   val:`${{d.mem}}%`,  color:d.mem_color,  badge:d.mem_label,  pct:d.mem,  fs:null}},
                    {{id:'disk',  val:`${{d.disk}}%`, color:d.disk_color, badge:d.disk_label, pct:d.disk, fs:null}},
                    {{id:'uptime',val:d.uptime,        color:'#c9a84c',   badge:'STABLE',     pct:100,    fs:'0.7rem'}},
                    {{id:'flask', val:'SERVING',       color:'#5dcc7a',   badge:'ONLINE',     pct:100,    fs:'0.65rem'}},
                ];
                cards.forEach(c=>{{
                    const v=document.getElementById(c.id+'-val'),
                          b=document.getElementById(c.id+'-badge'),
                          p=document.getElementById(c.id+'-bar');
                    v.textContent=c.val; v.style.color=c.color; v.style.textShadow=`0 0 8px ${{c.color}}`;
                    if(c.fs) v.style.fontSize=c.fs;
                    b.textContent=c.badge; b.style.color=c.color; b.style.borderColor=c.color;
                    p.style.background=c.color; p.style.width=c.pct+'%';
                }});
                document.getElementById('heroUptime').textContent=d.uptime;
                if(activeCard) openModal(activeCard);
                dot.classList.remove('spin'); countdown=5; lbl.textContent='LIVE · 5s';
            }}).catch(()=>{{ dot.classList.remove('spin'); lbl.textContent='RETRY...'; }});
        }}
        setInterval(()=>{{ countdown--; if(countdown>0) document.getElementById('refreshLabel').textContent=`LIVE · ${{countdown}}s`; else refreshHealth(); }},1000);

        const palettes=[
            {{bg:'#040c18',gdim:'rgba(201,168,76,0.12)',gborder:'rgba(201,168,76,0.25)'}},
            {{bg:'#060d1e',gdim:'rgba(100,150,255,0.08)',gborder:'rgba(100,150,255,0.22)'}},
            {{bg:'#080d12',gdim:'rgba(80,200,120,0.07)',gborder:'rgba(80,200,120,0.22)'}},
            {{bg:'#120808',gdim:'rgba(220,100,80,0.08)',gborder:'rgba(220,100,80,0.22)'}},
            {{bg:'#0c0814',gdim:'rgba(180,100,220,0.08)',gborder:'rgba(180,100,220,0.22)'}},
        ];
        let curr=0; const root=document.documentElement;
        document.querySelector('.dashboard').addEventListener('click',function(e){{
            if(e.target.closest('.hcard')||e.target.closest('.modal-overlay')||e.target.closest('.kpi-pill')||e.target.closest('.stack-badge')) return;
            curr=(curr+1)%palettes.length;
            const p=palettes[curr];
            document.body.style.backgroundColor=p.bg;
            root.style.setProperty('--navy',p.bg);
            root.style.setProperty('--gold-dim',p.gdim);
            root.style.setProperty('--gold-border',p.gborder);
            const rip=document.createElement('div'); rip.className='ripple';
            rip.style.left=e.clientX+'px'; rip.style.top=e.clientY+'px';
            document.body.appendChild(rip); setTimeout(()=>rip.remove(),1000);
        }});
    </script>
</body>
</html>"""
    return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
