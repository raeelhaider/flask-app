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
 
    try:
        r.ping()
        redis_info   = r.info()
        redis_status = "ONLINE"
        redis_color  = "#c9a84c"
        redis_mem    = round(redis_info.get('used_memory', 0) / (1024*1024), 2)
        redis_keys   = redis_info.get('db0', {}).get('keys', 0) if 'db0' in redis_info else 0
        redis_clients= redis_info.get('connected_clients', 1)
    except:
        redis_status = "OFFLINE"
        redis_color  = "#e05c5c"
        redis_mem    = 0
        redis_keys   = 0
        redis_clients= 0
 
    def color(v):
        return "#c9a84c" if v < 60 else "#e8c56a" if v < 85 else "#e05c5c"
    def label(v):
        return "NOMINAL" if v < 60 else "MODERATE" if v < 85 else "CRITICAL"
 
    return dict(
        cpu=round(cpu,1),            cpu_color=color(cpu),         cpu_label=label(cpu),
        cpu_count=cpu_count,
        cpu_freq=round(cpu_freq.current,0) if cpu_freq else "N/A",
        mem=round(mem.percent,1),    mem_color=color(mem.percent), mem_label=label(mem.percent),
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
        redis_status=redis_status,   redis_color=redis_color,
        redis_mem=redis_mem,         redis_keys=redis_keys,
        redis_clients=redis_clients,
    )
 
# ── API endpoint for live refresh ──
@app.route("/health")
def health_api():
    h = get_system_health()
    return jsonify(h)
 
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
    <title>Cloud & DevOps Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Rajdhani:wght@300;400;500;600&family=Share+Tech+Mono&display=swap" rel="stylesheet">
    <style>
        *, *::before, *::after {{ box-sizing:border-box; margin:0; padding:0; }}
        :root {{
            --gold:        #c9a84c;
            --gold-light:  #e8d5a3;
            --gold-dim:    rgba(201,168,76,0.18);
            --gold-border: rgba(201,168,76,0.28);
            --navy:        #050d1a;
            --navy-card:   rgba(7,20,40,0.85);
            --text:        #dce8f5;
            --dim:         rgba(220,232,245,0.38);
        }}
        html, body {{ height:100%; overflow:hidden; }}
        body {{
            background:var(--navy); font-family:'Rajdhani',sans-serif;
            color:var(--text); cursor:default; transition:background 0.7s ease;
        }}
        .bg-layer {{
            position:fixed; inset:0; z-index:0;
            background:
                radial-gradient(ellipse 80% 50% at 50% 0%, rgba(201,168,76,0.07) 0%, transparent 70%),
                radial-gradient(ellipse 60% 40% at 100% 100%, rgba(7,40,80,0.6) 0%, transparent 60%),
                repeating-linear-gradient(0deg,  transparent,transparent 39px,rgba(201,168,76,0.03) 39px,rgba(201,168,76,0.03) 40px),
                repeating-linear-gradient(90deg, transparent,transparent 39px,rgba(201,168,76,0.03) 39px,rgba(201,168,76,0.03) 40px);
            pointer-events:none;
        }}
        .corner {{ position:fixed; width:44px; height:44px; pointer-events:none; z-index:2; opacity:0.7; }}
        .corner-tl {{ top:18px; left:18px; border-top:1px solid var(--gold); border-left:1px solid var(--gold); }}
        .corner-tr {{ top:18px; right:18px; border-top:1px solid var(--gold); border-right:1px solid var(--gold); }}
        .corner-bl {{ bottom:18px; left:18px; border-bottom:1px solid var(--gold); border-left:1px solid var(--gold); }}
        .corner-br {{ bottom:18px; right:18px; border-bottom:1px solid var(--gold); border-right:1px solid var(--gold); }}
 
        .dashboard {{
            position:relative; z-index:10; height:100vh;
            display:grid; grid-template-rows:auto auto auto 1fr auto auto;
            padding:22px 32px 18px; gap:12px;
        }}
 
        /* HEADER */
        .header {{
            display:flex; justify-content:space-between; align-items:flex-start;
            border-bottom:1px solid var(--gold-border); padding-bottom:12px;
            animation:fadeDown 0.7s ease forwards;
        }}
        .project-eyebrow {{ font-family:'Share Tech Mono',monospace; font-size:0.6rem; letter-spacing:5px; color:var(--gold); opacity:0.8; text-transform:uppercase; }}
        .project-title {{
            font-family:'Cinzel',serif; font-size:clamp(1.1rem,2.5vw,1.6rem); font-weight:700; letter-spacing:2px;
            background:linear-gradient(135deg,var(--gold-light) 0%,var(--gold) 60%,#a07830 100%);
            -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
            filter:drop-shadow(0 0 12px rgba(201,168,76,0.35)); margin:3px 0;
        }}
        .project-desc {{ font-size:0.72rem; font-weight:300; letter-spacing:1px; color:var(--dim); }}
        .header-right {{ text-align:right; font-family:'Share Tech Mono',monospace; font-size:0.7rem; color:var(--dim); line-height:1.7; }}
        #clock {{ font-size:1rem; color:var(--gold); text-shadow:0 0 10px rgba(201,168,76,0.5); }}
 
        /* DIVIDER */
        .gold-rule {{ display:flex; align-items:center; gap:10px; opacity:0; animation:fadeUp 0.5s 0.3s ease forwards; }}
        .gold-rule::before, .gold-rule::after {{ content:''; flex:1; height:1px; background:linear-gradient(90deg,transparent,var(--gold-border),transparent); }}
        .gold-diamond {{ width:5px; height:5px; background:var(--gold); transform:rotate(45deg); box-shadow:0 0 6px var(--gold); }}
 
        /* GREETING */
        .greeting-row {{ display:flex; align-items:center; justify-content:space-between; gap:20px; opacity:0; animation:fadeUp 0.6s 0.4s ease forwards; }}
        .greeting-sub {{ font-family:'Share Tech Mono',monospace; font-size:0.6rem; letter-spacing:5px; color:var(--gold); opacity:0.7; margin-bottom:4px; }}
        .greeting-main {{ font-family:'Cinzel',serif; font-size:clamp(1.3rem,3vw,2rem); font-weight:600; color:#fff; text-shadow:0 0 30px rgba(201,168,76,0.2); }}
        .typewriter {{ display:inline-block; overflow:hidden; white-space:nowrap; border-right:2px solid var(--gold); animation:typing 2s steps(22,end) 0.8s forwards,blink 0.8s step-end infinite; max-width:0; }}
        @keyframes typing {{ from {{ max-width:0; }} to {{ max-width:100%; }} }}
        @keyframes blink   {{ 50% {{ border-color:transparent; }} }}
 
        .kpi-row {{ display:flex; gap:10px; flex-shrink:0; }}
        .kpi-pill {{ background:var(--gold-dim); border:1px solid var(--gold-border); border-radius:8px; padding:8px 16px; text-align:center; min-width:90px; position:relative; overflow:hidden; }}
        .kpi-pill::before {{ content:''; position:absolute; top:0; left:0; right:0; height:1px; background:linear-gradient(90deg,transparent,var(--gold),transparent); }}
        .kpi-label {{ font-family:'Share Tech Mono',monospace; font-size:0.5rem; letter-spacing:3px; color:var(--dim); text-transform:uppercase; margin-bottom:3px; }}
        .kpi-value {{ font-family:'Cinzel',serif; font-size:1.4rem; font-weight:700; color:var(--gold); text-shadow:0 0 12px rgba(201,168,76,0.5); }}
        .kpi-value.status {{ font-size:0.75rem; color:#5dcc7a; text-shadow:0 0 8px rgba(93,204,122,0.5); padding-top:4px; font-family:'Share Tech Mono',monospace; }}
 
        /* MILESTONE */
        .milestone {{ font-family:'Share Tech Mono',monospace; font-size:0.72rem; letter-spacing:2px; color:var(--gold); background:var(--gold-dim); border:1px solid var(--gold-border); border-radius:6px; padding:6px 18px; text-align:center; opacity:0; animation:fadeUp 0.5s 1.2s ease forwards,goldPulse 2.5s 1.7s ease-in-out infinite; }}
        @keyframes goldPulse {{ 0%,100% {{ box-shadow:0 0 6px rgba(201,168,76,0.15); }} 50% {{ box-shadow:0 0 18px rgba(201,168,76,0.4); }} }}
 
        /* HEALTH */
        .health-section {{ display:flex; flex-direction:column; gap:7px; opacity:0; animation:fadeUp 0.6s 0.6s ease forwards; }}
        .health-header {{ display:flex; justify-content:space-between; align-items:center; }}
        .section-label {{ font-family:'Share Tech Mono',monospace; font-size:0.55rem; letter-spacing:4px; color:var(--dim); text-transform:uppercase; }}
        .refresh-indicator {{ font-family:'Share Tech Mono',monospace; font-size:0.52rem; color:var(--dim); letter-spacing:2px; display:flex; align-items:center; gap:6px; }}
        .refresh-dot {{ width:5px; height:5px; border-radius:50%; background:var(--gold); animation:pulse 1s ease-in-out infinite; }}
        .refresh-dot.spinning {{ animation:spin 1s linear infinite; }}
        @keyframes spin {{ from {{ transform:rotate(0deg); }} to {{ transform:rotate(360deg); }} }}
 
        .health-grid {{ display:grid; grid-template-columns:repeat(6,1fr); gap:8px; }}
 
        /* HEALTH CARD */
        .hcard {{
            background:var(--navy-card); border:1px solid var(--gold-border);
            border-radius:8px; padding:9px 7px; text-align:center;
            position:relative; overflow:hidden;
            cursor:pointer;
            transition:border-color 0.3s, box-shadow 0.3s, transform 0.2s;
        }}
        .hcard:hover {{ border-color:var(--gold); box-shadow:0 0 18px rgba(201,168,76,0.18); transform:translateY(-2px); }}
        .hcard.active {{ border-color:var(--gold); box-shadow:0 0 22px rgba(201,168,76,0.25); }}
        .hcard::before {{ content:''; position:absolute; top:0; left:0; right:0; height:1px; background:linear-gradient(90deg,transparent,var(--gold),transparent); opacity:0.5; }}
        .hcard-icon  {{ font-size:0.9rem; margin-bottom:3px; pointer-events:none; }}
        .hcard-name  {{ font-family:'Share Tech Mono',monospace; font-size:0.48rem; letter-spacing:2px; color:var(--dim); text-transform:uppercase; margin-bottom:4px; pointer-events:none; }}
        .hcard-val   {{ font-family:'Cinzel',serif; font-size:0.9rem; font-weight:600; line-height:1; margin-bottom:4px; transition:all 0.4s ease; pointer-events:none; }}
        .hcard-badge {{ font-family:'Share Tech Mono',monospace; font-size:0.42rem; letter-spacing:1.5px; padding:2px 5px; border-radius:999px; border:1px solid; display:inline-block; margin-bottom:5px; text-transform:uppercase; pointer-events:none; }}
        .progress-track {{ width:100%; height:2px; background:rgba(255,255,255,0.06); border-radius:999px; overflow:hidden; }}
        .progress-fill {{ height:100%; border-radius:999px; transition:width 0.6s ease; }}
 
        /* EXPANDED DETAIL MODAL */
        .modal-overlay {{
            position:fixed; inset:0; z-index:100;
            background:rgba(5,13,26,0.85);
            backdrop-filter:blur(6px);
            display:flex; align-items:center; justify-content:center;
            opacity:0; pointer-events:none;
            transition:opacity 0.3s ease;
        }}
        .modal-overlay.show {{ opacity:1; pointer-events:all; }}
        .modal {{
            background:linear-gradient(135deg,#071428,#050d1a);
            border:1px solid var(--gold-border);
            border-radius:16px; padding:28px 32px;
            min-width:320px; max-width:420px; width:90%;
            position:relative;
            transform:scale(0.9) translateY(20px);
            transition:transform 0.3s cubic-bezier(0.16,1,0.3,1);
            box-shadow:0 0 40px rgba(201,168,76,0.15);
        }}
        .modal-overlay.show .modal {{ transform:scale(1) translateY(0); }}
        .modal::before {{ content:''; position:absolute; top:0; left:0; right:0; height:2px; background:linear-gradient(90deg,transparent,var(--gold),transparent); border-radius:16px 16px 0 0; }}
        .modal-close {{
            position:absolute; top:12px; right:16px;
            font-family:'Share Tech Mono',monospace; font-size:0.7rem;
            color:var(--dim); cursor:pointer; letter-spacing:2px;
            transition:color 0.2s;
        }}
        .modal-close:hover {{ color:var(--gold); }}
        .modal-icon  {{ font-size:2rem; margin-bottom:8px; }}
        .modal-title {{ font-family:'Cinzel',serif; font-size:1.1rem; font-weight:700; color:var(--gold); margin-bottom:4px; letter-spacing:2px; }}
        .modal-status {{ font-family:'Share Tech Mono',monospace; font-size:0.6rem; letter-spacing:3px; color:var(--dim); margin-bottom:20px; }}
        .modal-big-val {{ font-family:'Cinzel',serif; font-size:3rem; font-weight:700; line-height:1; margin-bottom:16px; }}
        .modal-bar-wrap {{ margin-bottom:20px; }}
        .modal-bar-label {{ font-family:'Share Tech Mono',monospace; font-size:0.55rem; letter-spacing:3px; color:var(--dim); margin-bottom:6px; display:flex; justify-content:space-between; }}
        .modal-bar-track {{ width:100%; height:6px; background:rgba(255,255,255,0.06); border-radius:999px; overflow:hidden; }}
        .modal-bar-fill  {{ height:100%; border-radius:999px; transition:width 0.8s ease; }}
        .modal-details {{ display:grid; grid-template-columns:1fr 1fr; gap:10px; }}
        .modal-detail-box {{ background:rgba(201,168,76,0.05); border:1px solid var(--gold-border); border-radius:8px; padding:10px 12px; }}
        .modal-detail-label {{ font-family:'Share Tech Mono',monospace; font-size:0.5rem; letter-spacing:2px; color:var(--dim); text-transform:uppercase; margin-bottom:4px; }}
        .modal-detail-val   {{ font-family:'Cinzel',serif; font-size:0.95rem; font-weight:600; color:var(--gold-light); }}
 
        /* STACK */
        .stack-section {{ border-top:1px solid var(--gold-border); padding-top:10px; opacity:0; animation:fadeUp 0.6s 0.9s ease forwards; }}
        .stack-inner {{ display:flex; flex-wrap:wrap; justify-content:center; gap:6px; }}
        .stack-badge {{ display:inline-flex; align-items:center; gap:5px; padding:3px 11px; border:1px solid var(--gold-border); border-radius:999px; background:var(--gold-dim); font-family:'Share Tech Mono',monospace; font-size:0.58rem; letter-spacing:1.5px; color:var(--gold-light); text-transform:uppercase; transition:all 0.25s; }}
        .stack-badge:hover {{ border-color:var(--gold); color:var(--gold); box-shadow:0 0 10px rgba(201,168,76,0.2); }}
 
        /* FOOTER */
        .footer {{ display:flex; justify-content:space-between; align-items:center; border-top:1px solid var(--gold-border); padding-top:10px; font-family:'Share Tech Mono',monospace; font-size:0.58rem; color:var(--dim); letter-spacing:2px; opacity:0; animation:fadeUp 0.6s 1s ease forwards; }}
        .status-dot {{ display:inline-block; width:5px; height:5px; border-radius:50%; background:#5dcc7a; box-shadow:0 0 6px #5dcc7a; margin-right:6px; animation:pulse 2s ease-in-out infinite; }}
        @keyframes pulse {{ 0%,100% {{ opacity:1; }} 50% {{ opacity:0.3; }} }}
 
        .ripple {{ position:fixed; border-radius:50%; border:1px solid var(--gold); pointer-events:none; z-index:5; animation:rippleOut 0.9s ease-out forwards; transform:translate(-50%,-50%); }}
        @keyframes rippleOut {{ from {{ width:0; height:0; opacity:0.5; }} to {{ width:500px; height:500px; opacity:0; }} }}
 
        @keyframes fadeUp   {{ from {{ opacity:0; transform:translateY(14px); }} to {{ opacity:1; transform:translateY(0); }} }}
        @keyframes fadeDown {{ from {{ opacity:0; transform:translateY(-14px); }} to {{ opacity:1; transform:translateY(0); }} }}
        @keyframes countUp  {{ from {{ opacity:0; transform:translateY(8px); }} to {{ opacity:1; transform:translateY(0); }} }}
        .count-anim {{ animation:countUp 0.4s ease forwards; }}
    </style>
</head>
<body>
    <div class="bg-layer"></div>
    <div class="corner corner-tl"></div>
    <div class="corner corner-tr"></div>
    <div class="corner corner-bl"></div>
    <div class="corner corner-br"></div>
 
    <!-- DETAIL MODAL -->
    <div class="modal-overlay" id="modalOverlay" onclick="closeModal(event)">
        <div class="modal" id="modal">
            <div class="modal-close" onclick="closeModal(null, true)">[ CLOSE ]</div>
            <div class="modal-icon"  id="modalIcon"></div>
            <div class="modal-title" id="modalTitle"></div>
            <div class="modal-status" id="modalStatus"></div>
            <div class="modal-big-val" id="modalBigVal"></div>
            <div class="modal-bar-wrap">
                <div class="modal-bar-label">
                    <span>UTILISATION</span>
                    <span id="modalBarPct"></span>
                </div>
                <div class="modal-bar-track">
                    <div class="modal-bar-fill" id="modalBarFill"></div>
                </div>
            </div>
            <div class="modal-details" id="modalDetails"></div>
        </div>
    </div>
 
    <div class="dashboard">
 
        <!-- HEADER -->
        <div class="header">
            <div>
                <div class="project-eyebrow">// Live Production Dashboard</div>
                <div class="project-title">Cloud &amp; DevOps Pipeline</div>
                <div class="project-desc">A fully automated CI/CD application deployed on AWS EC2 &mdash; built with Flask, Redis, Docker &amp; Jenkins</div>
            </div>
            <div class="header-right">
                <div id="date"></div>
                <div id="clock">00:00:00</div>
            </div>
        </div>
 
        <!-- DIVIDER -->
        <div class="gold-rule"><div class="gold-diamond"></div></div>
 
        <!-- GREETING + KPIs -->
        <div class="greeting-row">
            <div>
                <div class="greeting-sub">// Operator Session Active</div>
                <div class="greeting-main"><span class="typewriter">Hello, DevOps Explorer</span></div>
            </div>
            <div class="kpi-row">
                <div class="kpi-pill">
                    <div class="kpi-label">Visits</div>
                    <div class="kpi-value" id="visitCount">0</div>
                </div>
                <div class="kpi-pill">
                    <div class="kpi-label">Status</div>
                    <div class="kpi-value status">● ONLINE</div>
                </div>
            </div>
        </div>
 
        {"<div class='milestone'>" + milestone + "</div>" if milestone else "<div></div>"}
 
        <!-- HEALTH GRID -->
        <div class="health-section">
            <div class="health-header">
                <div class="section-label">// System Health Monitor</div>
                <div class="refresh-indicator">
                    <div class="refresh-dot" id="refreshDot"></div>
                    <span id="refreshLabel">LIVE · REFRESHES IN 5s</span>
                </div>
            </div>
            <div class="health-grid" id="healthGrid">
 
                <div class="hcard" onclick="openModal('cpu')" title="Click for details">
                    <div class="hcard-icon">⚙️</div>
                    <div class="hcard-name">CPU</div>
                    <div class="hcard-val" id="cpu-val" style="color:{h['cpu_color']};text-shadow:0 0 8px {h['cpu_color']};">{h['cpu']}%</div>
                    <div class="hcard-badge" id="cpu-badge" style="color:{h['cpu_color']};border-color:{h['cpu_color']};">{h['cpu_label']}</div>
                    <div class="progress-track"><div class="progress-fill" id="cpu-bar" style="width:{h['cpu']}%;background:{h['cpu_color']};"></div></div>
                </div>
 
                <div class="hcard" onclick="openModal('mem')" title="Click for details">
                    <div class="hcard-icon">🧠</div>
                    <div class="hcard-name">Memory</div>
                    <div class="hcard-val" id="mem-val" style="color:{h['mem_color']};text-shadow:0 0 8px {h['mem_color']};">{h['mem']}%</div>
                    <div class="hcard-badge" id="mem-badge" style="color:{h['mem_color']};border-color:{h['mem_color']};">{h['mem_label']}</div>
                    <div class="progress-track"><div class="progress-fill" id="mem-bar" style="width:{h['mem']}%;background:{h['mem_color']};"></div></div>
                </div>
 
                <div class="hcard" onclick="openModal('disk')" title="Click for details">
                    <div class="hcard-icon">💾</div>
                    <div class="hcard-name">Disk</div>
                    <div class="hcard-val" id="disk-val" style="color:{h['disk_color']};text-shadow:0 0 8px {h['disk_color']};">{h['disk']}%</div>
                    <div class="hcard-badge" id="disk-badge" style="color:{h['disk_color']};border-color:{h['disk_color']};">{h['disk_label']}</div>
                    <div class="progress-track"><div class="progress-fill" id="disk-bar" style="width:{h['disk']}%;background:{h['disk_color']};"></div></div>
                </div>
 
                <div class="hcard" onclick="openModal('redis')" title="Click for details">
                    <div class="hcard-icon">🗄️</div>
                    <div class="hcard-name">Redis</div>
                    <div class="hcard-val" id="redis-val" style="color:{h['redis_color']};text-shadow:0 0 8px {h['redis_color']};font-size:0.65rem;padding-top:3px;">{h['redis_status']}</div>
                    <div class="hcard-badge" id="redis-badge" style="color:{h['redis_color']};border-color:{h['redis_color']};">{h['redis_status']}</div>
                    <div class="progress-track"><div class="progress-fill" id="redis-bar" style="width:{'100' if h['redis_status']=='ONLINE' else '0'}%;background:{h['redis_color']};"></div></div>
                </div>
 
                <div class="hcard" onclick="openModal('uptime')" title="Click for details">
                    <div class="hcard-icon">⏱️</div>
                    <div class="hcard-name">Uptime</div>
                    <div class="hcard-val" id="uptime-val" style="color:#c9a84c;text-shadow:0 0 8px #c9a84c;font-size:0.7rem;padding-top:3px;">{h['uptime']}</div>
                    <div class="hcard-badge" id="uptime-badge" style="color:#c9a84c;border-color:#c9a84c;">STABLE</div>
                    <div class="progress-track"><div class="progress-fill" id="uptime-bar" style="width:100%;background:#c9a84c;"></div></div>
                </div>
 
                <div class="hcard" onclick="openModal('flask')" title="Click for details">
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
        // ── CLOCK ──
        function updateClock() {{
            const now = new Date();
            document.getElementById('clock').textContent = now.toTimeString().split(' ')[0];
            document.getElementById('date').textContent  = now.toLocaleDateString('en-US', {{
                weekday:'long', year:'numeric', month:'long', day:'numeric'
            }});
        }}
        updateClock(); setInterval(updateClock, 1000);
 
        // ── ANIMATED VISIT COUNTER ──
        function animateCount(target, duration=1200) {{
            const el = document.getElementById('visitCount');
            const start = 0, startTime = performance.now();
            function step(now) {{
                const progress = Math.min((now - startTime) / duration, 1);
                const ease = 1 - Math.pow(1 - progress, 3);
                el.textContent = Math.floor(ease * target);
                el.classList.add('count-anim');
                if (progress < 1) requestAnimationFrame(step);
                else el.textContent = target;
            }}
            requestAnimationFrame(step);
        }}
        animateCount({count});
 
        // ── STORED HEALTH DATA for modal ──
        let healthData = {{
            cpu:         {h['cpu']},
            cpu_color:   "{h['cpu_color']}",
            cpu_label:   "{h['cpu_label']}",
            cpu_count:   {h['cpu_count']},
            cpu_freq:    {h['cpu_freq']},
            mem:         {h['mem']},
            mem_color:   "{h['mem_color']}",
            mem_label:   "{h['mem_label']}",
            mem_total:   {h['mem_total']},
            mem_used_gb: {h['mem_used_gb']},
            mem_available: {h['mem_available']},
            disk:        {h['disk']},
            disk_color:  "{h['disk_color']}",
            disk_label:  "{h['disk_label']}",
            disk_total:  {h['disk_total']},
            disk_used_gb:{h['disk_used_gb']},
            disk_free:   {h['disk_free']},
            net_sent:    {h['net_sent']},
            net_recv:    {h['net_recv']},
            uptime:      "{h['uptime']}",
            uptime_secs: {h['uptime_secs']},
            redis_status:"{h['redis_status']}",
            redis_color: "{h['redis_color']}",
            redis_mem:   {h['redis_mem']},
            redis_keys:  {h['redis_keys']},
            redis_clients:{h['redis_clients']},
        }};
 
        // ── MODAL ──
        let activeCard = null;
        const modalDefs = {{
            cpu: (d) => ({{
                icon:'⚙️', title:'CPU PROCESSOR', status:`${{d.cpu_count}} Cores · ${{d.cpu_freq}} MHz`,
                bigVal:`${{d.cpu}}%`, color:d.cpu_color, pct:d.cpu, barPct:`${{d.cpu}}%`,
                details:[
                    {{ label:'Load', val:`${{d.cpu}}%` }},
                    {{ label:'Cores', val:d.cpu_count }},
                    {{ label:'Frequency', val:`${{d.cpu_freq}} MHz` }},
                    {{ label:'Status', val:d.cpu_label }},
                ]
            }}),
            mem: (d) => ({{
                icon:'🧠', title:'MEMORY (RAM)', status:`${{d.mem_total}} GB Total`,
                bigVal:`${{d.mem}}%`, color:d.mem_color, pct:d.mem, barPct:`${{d.mem}}%`,
                details:[
                    {{ label:'Used', val:`${{d.mem_used_gb}} GB` }},
                    {{ label:'Total', val:`${{d.mem_total}} GB` }},
                    {{ label:'Available', val:`${{d.mem_available}} MB` }},
                    {{ label:'Status', val:d.mem_label }},
                ]
            }}),
            disk: (d) => ({{
                icon:'💾', title:'DISK STORAGE', status:`${{d.disk_total}} GB Total`,
                bigVal:`${{d.disk}}%`, color:d.disk_color, pct:d.disk, barPct:`${{d.disk}}%`,
                details:[
                    {{ label:'Used', val:`${{d.disk_used_gb}} GB` }},
                    {{ label:'Total', val:`${{d.disk_total}} GB` }},
                    {{ label:'Free', val:`${{d.disk_free}} GB` }},
                    {{ label:'Status', val:d.disk_label }},
                ]
            }}),
            redis: (d) => ({{
                icon:'🗄️', title:'REDIS CACHE', status:`Cache Layer · ${{d.redis_status}}`,
                bigVal:d.redis_status, color:d.redis_color, pct:d.redis_status==='ONLINE'?100:0, barPct:d.redis_status,
                details:[
                    {{ label:'Status', val:d.redis_status }},
                    {{ label:'Memory', val:`${{d.redis_mem}} MB` }},
                    {{ label:'Keys', val:d.redis_keys }},
                    {{ label:'Clients', val:d.redis_clients }},
                ]
            }}),
            uptime: (d) => ({{
                icon:'⏱️', title:'SYSTEM UPTIME', status:'Server Running Time',
                bigVal:d.uptime, color:'#c9a84c', pct:100, barPct:'STABLE',
                details:[
                    {{ label:'Uptime', val:d.uptime }},
                    {{ label:'Seconds', val:d.uptime_secs }},
                    {{ label:'Net Sent', val:`${{d.net_sent}} MB` }},
                    {{ label:'Net Recv', val:`${{d.net_recv}} MB` }},
                ]
            }}),
            flask: (d) => ({{
                icon:'🌶️', title:'FLASK APP', status:'Web Application · Active',
                bigVal:'SERVING', color:'#5dcc7a', pct:100, barPct:'100%',
                details:[
                    {{ label:'Status', val:'ONLINE' }},
                    {{ label:'Framework', val:'Flask' }},
                    {{ label:'Language', val:'Python 3.11' }},
                    {{ label:'Port', val:'Internal' }},
                ]
            }}),
        }};
 
        function openModal(type) {{
            activeCard = type;
            const def  = modalDefs[type](healthData);
            document.getElementById('modalIcon').textContent   = def.icon;
            document.getElementById('modalTitle').textContent  = def.title;
            document.getElementById('modalStatus').textContent = def.status;
            document.getElementById('modalBigVal').textContent = def.bigVal;
            document.getElementById('modalBigVal').style.color = def.color;
            document.getElementById('modalBigVal').style.textShadow = `0 0 20px ${{def.color}}`;
            document.getElementById('modalBarPct').textContent  = def.barPct;
            const fill = document.getElementById('modalBarFill');
            fill.style.background = def.color;
            fill.style.width = '0%';
            setTimeout(() => fill.style.width = def.pct + '%', 50);
            document.getElementById('modalDetails').innerHTML = def.details.map(d =>
                `<div class="modal-detail-box">
                    <div class="modal-detail-label">${{d.label}}</div>
                    <div class="modal-detail-val">${{d.val}}</div>
                </div>`
            ).join('');
            document.getElementById('modalOverlay').classList.add('show');
        }}
 
        function closeModal(e, force=false) {{
            if (force || (e && e.target === document.getElementById('modalOverlay'))) {{
                document.getElementById('modalOverlay').classList.remove('show');
                activeCard = null;
            }}
        }}
 
        // ── 5s HEALTH REFRESH ──
        let countdown = 5;
        function updateHealthUI(d) {{
            healthData = d;
            const cards = [
                {{ id:'cpu',   val:`${{d.cpu}}%`,     color:d.cpu_color,   badge:d.cpu_label,    pct:d.cpu,   fontSize:null }},
                {{ id:'mem',   val:`${{d.mem}}%`,     color:d.mem_color,   badge:d.mem_label,    pct:d.mem,   fontSize:null }},
                {{ id:'disk',  val:`${{d.disk}}%`,    color:d.disk_color,  badge:d.disk_label,   pct:d.disk,  fontSize:null }},
                {{ id:'redis', val:d.redis_status,    color:d.redis_color, badge:d.redis_status, pct:d.redis_status==='ONLINE'?100:0, fontSize:'0.65rem' }},
                {{ id:'uptime',val:d.uptime,           color:'#c9a84c',    badge:'STABLE',       pct:100,     fontSize:'0.7rem' }},
                {{ id:'flask', val:'SERVING',          color:'#5dcc7a',    badge:'ONLINE',       pct:100,     fontSize:'0.65rem' }},
            ];
            cards.forEach(c => {{
                const valEl   = document.getElementById(c.id + '-val');
                const badgeEl = document.getElementById(c.id + '-badge');
                const barEl   = document.getElementById(c.id + '-bar');
                valEl.textContent   = c.val;
                valEl.style.color   = c.color;
                valEl.style.textShadow = `0 0 8px ${{c.color}}`;
                if (c.fontSize) valEl.style.fontSize = c.fontSize;
                badgeEl.textContent    = c.badge;
                badgeEl.style.color    = c.color;
                badgeEl.style.borderColor = c.color;
                barEl.style.background = c.color;
                barEl.style.width      = c.pct + '%';
            }});
            if (activeCard) openModal(activeCard);
        }}
 
        function refreshHealth() {{
            const dot   = document.getElementById('refreshDot');
            const label = document.getElementById('refreshLabel');
            dot.classList.add('spinning');
            label.textContent = 'REFRESHING...';
            fetch('/health')
                .then(r => r.json())
                .then(d => {{
                    updateHealthUI(d);
                    dot.classList.remove('spinning');
                    countdown = 5;
                    label.textContent = `LIVE · REFRESHES IN ${{countdown}}s`;
                }})
                .catch(() => {{
                    dot.classList.remove('spinning');
                    label.textContent = 'REFRESH FAILED';
                }});
        }}
 
        setInterval(() => {{
            countdown--;
            const label = document.getElementById('refreshLabel');
            if (countdown > 0) {{
                label.textContent = `LIVE · REFRESHES IN ${{countdown}}s`;
            }} else {{
                refreshHealth();
            }}
        }}, 1000);
 
        // ── THEME PALETTES (body click only, not cards) ──
        const palettes = [
            {{ bg:'#050d1a', dim:'rgba(201,168,76,0.18)', border:'rgba(201,168,76,0.28)' }},
            {{ bg:'#070d1f', dim:'rgba(120,160,255,0.07)', border:'rgba(120,160,255,0.28)' }},
            {{ bg:'#0a0d14', dim:'rgba(93,204,122,0.06)', border:'rgba(93,204,122,0.25)' }},
            {{ bg:'#150d0a', dim:'rgba(220,120,80,0.07)', border:'rgba(220,120,80,0.28)' }},
            {{ bg:'#0d0a18', dim:'rgba(180,120,220,0.07)', border:'rgba(180,120,220,0.25)' }},
        ];
        let current = 0;
        const root  = document.documentElement;
 
        document.querySelector('.dashboard').addEventListener('click', function(e) {{
            if (e.target.closest('.hcard') || e.target.closest('.modal-overlay')) return;
            current = (current + 1) % palettes.length;
            const p = palettes[current];
            document.body.style.backgroundColor = p.bg;
            root.style.setProperty('--navy', p.bg);
            root.style.setProperty('--gold-dim', p.dim);
            root.style.setProperty('--gold-border', p.border);
            const ripple = document.createElement('div');
            ripple.className = 'ripple';
            ripple.style.left = e.clientX + 'px';
            ripple.style.top  = e.clientY + 'px';
            document.body.appendChild(ripple);
            setTimeout(() => ripple.remove(), 900);
        }});
    </script>
</body>
</html>"""
    return html
 
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
