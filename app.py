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
    if count == 1:        return "🌌 First contact established."
    elif count == 5:      return "⚡ 5 visits — System warming up."
    elif count == 10:     return "🔥 10 visits — You're on a streak!"
    elif count == 25:     return "💀 25 visits — Impressive persistence."
    elif count == 50:     return "🌙 50 visits — You live here now."
    elif count == 100:    return "👁️ 100 visits — LEGENDARY STATUS."
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

    def color(v):
        if v < 40:   return "#3dffa0"
        elif v < 70: return "#ffb347"
        elif v < 85: return "#ff9966"
        else:        return "#ff5f5f"

    def label(v):
        return "OPTIMAL" if v < 40 else "NOMINAL" if v < 70 else "ELEVATED" if v < 85 else "CRITICAL"

    return dict(
        cpu=round(cpu, 1),           cpu_color=color(cpu),           cpu_label=label(cpu),
        cpu_count=cpu_count,         cpu_freq=round(cpu_freq.current, 0) if cpu_freq else 0,
        mem=round(mem.percent, 1),   mem_color=color(mem.percent),   mem_label=label(mem.percent),
        mem_total=round(mem.total/(1024**3), 1),
        mem_used_gb=round(mem.used/(1024**3), 1),
        mem_available=round(mem.available/(1024**2)),
        disk=round(disk.percent, 1), disk_color=color(disk.percent), disk_label=label(disk.percent),
        disk_total=round(disk.total/(1024**3), 1),
        disk_used_gb=round(disk.used/(1024**3), 1),
        disk_free=round(disk.free/(1024**3), 1),
        net_sent=round(net.bytes_sent/(1024**2), 1),
        net_recv=round(net.bytes_recv/(1024**2), 1),
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

    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CI/CD Automation Project</title>
    <link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

        :root {
            --bg:     #0b0d10;
            --bg2:    #13161b;
            --bg3:    #1a1e25;
            --bg4:    #222830;
            --green:  #3dffa0;
            --blue:   #38b6ff;
            --purple: #b06bff;
            --red:    #ff5f5f;
            --amber:  #ffb347;
            --text:   #e8edf5;
            --text2:  #8a95a8;
            --text3:  #4a5568;
            --border: rgba(255,255,255,0.07);
        }

        html, body {
            background: var(--bg);
            color: var(--text);
            font-family: 'Syne', sans-serif;
            min-height: 100vh;
            overflow-x: hidden;
        }

        .mono { font-family: 'JetBrains Mono', monospace; }

        /* ── TOPBAR ── */
        .topbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 14px 28px;
            border-bottom: 1px solid var(--border);
            background: rgba(11,13,16,0.95);
            backdrop-filter: blur(20px);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        .topbar-brand { display: flex; align-items: center; gap: 12px; }
        .logo-box {
            width: 36px; height: 36px;
            background: linear-gradient(135deg, var(--green), var(--blue));
            border-radius: 10px;
            display: flex; align-items: center; justify-content: center;
            font-weight: 800; font-size: 14px; color: #0b0d10;
        }
        .brand-name  { font-size: 15px; font-weight: 700; letter-spacing: 0.5px; }
        .brand-sub   { font-size: 11px; color: var(--text2); font-family: 'JetBrains Mono', monospace; letter-spacing: 2px; }
        .topbar-right { display: flex; align-items: center; gap: 20px; }
        .status-pill {
            display: flex; align-items: center; gap: 7px;
            background: rgba(61,255,160,0.08);
            border: 1px solid rgba(61,255,160,0.2);
            border-radius: 100px; padding: 6px 14px;
            font-size: 12px; font-family: 'JetBrains Mono', monospace; color: var(--green);
        }
        .pulse {
            width: 8px; height: 8px; border-radius: 50%;
            background: var(--green); box-shadow: 0 0 12px var(--green);
            animation: pulse 2s ease infinite;
        }
        @keyframes pulse { 0%,100% { opacity:1; transform:scale(1); } 50% { opacity:.5; transform:scale(1.3); } }
        .clock { font-family: 'JetBrains Mono', monospace; font-size: 13px; color: var(--text2); }

        /* ── PIPELINE ── */
        .pipeline-section { padding: 24px 28px 0; }
        .section-label {
            font-family: 'JetBrains Mono', monospace; font-size: 11px;
            letter-spacing: 3px; color: var(--text3);
            text-transform: uppercase; margin-bottom: 12px;
        }
        .pipeline-track {
            background: var(--bg2); border: 1px solid var(--border);
            border-radius: 16px; padding: 20px 24px;
            display: flex; flex-direction: column; gap: 14px;
        }
        .pipeline-header { display: flex; justify-content: space-between; align-items: center; }
        .pipeline-title  { font-size: 14px; font-weight: 600; }
        .commit-info     { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--text2); }
        .commit-sha      { color: var(--blue); }

        .stages {
            display: grid; grid-template-columns: repeat(5, 1fr);
            gap: 0; position: relative;
        }
        .stage { display: flex; flex-direction: column; align-items: center; gap: 8px; position: relative; }
        .stage:not(:last-child)::after {
            content: ''; position: absolute; right: -50%; top: 20px;
            width: 100%; height: 2px; background: var(--border); z-index: 0;
        }
        .stage:not(:last-child).done::after    { background: var(--green); box-shadow: 0 0 8px rgba(61,255,160,.3); }
        .stage:not(:last-child).running::after { background: linear-gradient(90deg, var(--green), var(--border)); }

        .stage-dot {
            width: 40px; height: 40px; border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            font-size: 16px; position: relative; z-index: 1; transition: all .3s;
        }
        .stage-dot.done    { background: rgba(61,255,160,.12);  border: 1.5px solid var(--green);  box-shadow: 0 0 20px rgba(61,255,160,.15); }
        .stage-dot.running { background: rgba(56,182,255,.12);  border: 1.5px solid var(--blue);   box-shadow: 0 0 20px rgba(56,182,255,.2); animation: stagePulse 1.5s ease infinite; }
        .stage-dot.pending { background: var(--bg3);            border: 1.5px solid var(--border); }
        .stage-dot.failed  { background: rgba(255,95,95,.12);   border: 1.5px solid var(--red);    box-shadow: 0 0 20px rgba(255,95,95,.15); }
        @keyframes stagePulse { 0%,100% { box-shadow: 0 0 20px rgba(56,182,255,.2); } 50% { box-shadow: 0 0 30px rgba(56,182,255,.4); } }

        .stage-name { font-size: 11px; font-family: 'JetBrains Mono', monospace; color: var(--text2); text-align: center; }
        .stage-time { font-size: 10px; font-family: 'JetBrains Mono', monospace; color: var(--text3); }

        /* ── MIDDLE GRID ── */
        .middle-grid {
            display: grid; grid-template-columns: 1fr 1fr 1fr;
            gap: 16px; padding: 16px 28px;
        }
        .card {
            background: var(--bg2); border: 1px solid var(--border);
            border-radius: 16px; padding: 20px; transition: all .2s;
        }
        .card:hover { border-color: rgba(255,255,255,.12); transform: translateY(-2px); }
        .card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; }
        .card-icon   { width: 38px; height: 38px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 16px; }
        .card-icon.green  { background: rgba(61,255,160,.1); }
        .card-icon.blue   { background: rgba(56,182,255,.1); }
        .card-icon.purple { background: rgba(176,107,255,.1); }
        .card-badge { font-family: 'JetBrains Mono', monospace; font-size: 10px; padding: 4px 10px; border-radius: 100px; border: 1px solid; }
        .badge-green  { color: var(--green);  border-color: rgba(61,255,160,.3);  background: rgba(61,255,160,.07); }
        .badge-blue   { color: var(--blue);   border-color: rgba(56,182,255,.3);  background: rgba(56,182,255,.07); }
        .badge-amber  { color: var(--amber);  border-color: rgba(255,179,71,.3);  background: rgba(255,179,71,.07); }
        .card-label { font-size: 12px; font-family: 'JetBrains Mono', monospace; color: var(--text3); text-transform: uppercase; letter-spacing: 2px; margin-bottom: 6px; }
        .card-value { font-size: 32px; font-weight: 700; line-height: 1; }
        .card-sub   { font-size: 12px; color: var(--text2); margin-top: 6px; }

        /* ── HEALTH CARDS ── */
        .health-grid {
            grid-column: 1 / -1;
            display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px;
        }
        .hcard {
            background: var(--bg2); border: 1px solid var(--border);
            border-radius: 14px; padding: 16px; text-align: center;
            transition: all .2s; cursor: pointer;
        }
        .hcard:hover { border-color: rgba(61,255,160,.25); transform: translateY(-3px); box-shadow: 0 8px 24px rgba(0,0,0,.3); }
        .hcard-icon  { font-size: 20px; margin-bottom: 8px; }
        .hcard-name  { font-family: 'JetBrains Mono', monospace; font-size: 10px; letter-spacing: 2px; color: var(--text3); margin-bottom: 6px; }
        .hcard-val   { font-size: 22px; font-weight: 700; margin-bottom: 6px; }
        .hcard-badge { font-family: 'JetBrains Mono', monospace; font-size: 9px; padding: 3px 10px; border-radius: 100px; border: 1px solid; display: inline-block; margin-bottom: 10px; }
        .hbar        { background: rgba(255,255,255,.05); border-radius: 3px; height: 4px; overflow: hidden; }
        .hbar-fill   { height: 100%; border-radius: 3px; transition: width .8s cubic-bezier(.4,0,.2,1); }

        /* ── BOTTOM ROW ── */
        .bottom-row { display: grid; grid-template-columns: 2fr 1fr; gap: 16px; padding: 0 28px 16px; }
        .stack-card    { background: var(--bg2); border: 1px solid var(--border); border-radius: 16px; padding: 20px; }
        .actions-card  { background: var(--bg2); border: 1px solid var(--border); border-radius: 16px; padding: 20px; display: flex; flex-direction: column; gap: 10px; }
        .stack-pills   { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
        .pill {
            font-family: 'JetBrains Mono', monospace; font-size: 11px;
            padding: 6px 14px; border-radius: 100px;
            border: 1px solid var(--border); color: var(--text2); transition: all .2s;
        }
        .pill:hover          { border-color: rgba(61,255,160,.3); color: var(--green); }
        .pill.highlight      { border-color: rgba(56,182,255,.35); color: var(--blue); background: rgba(56,182,255,.06); }
        .action-btn {
            display: flex; align-items: center; gap: 10px;
            padding: 10px 14px; background: var(--bg3);
            border: 1px solid var(--border); border-radius: 10px;
            cursor: pointer; transition: all .2s;
            font-family: 'JetBrains Mono', monospace; font-size: 12px; color: var(--text);
        }
        .action-btn:hover { border-color: rgba(61,255,160,.3); color: var(--green); }
        .action-dot       { width: 8px; height: 8px; border-radius: 50%; }
        .dot-green  { background: var(--green); }
        .dot-blue   { background: var(--blue); }
        .dot-amber  { background: var(--amber); }

        /* ── MODAL ── */
        .modal-overlay {
            position: fixed; inset: 0; z-index: 1000;
            background: rgba(0,0,0,.8); backdrop-filter: blur(20px);
            display: flex; align-items: center; justify-content: center;
            opacity: 0; pointer-events: none; transition: opacity .3s;
        }
        .modal-overlay.active { opacity: 1; pointer-events: all; }
        .modal {
            background: var(--bg2); border: 1px solid var(--border);
            border-radius: 24px; padding: 28px; max-width: 420px; width: 90%;
            transform: scale(.9) translateY(20px);
            transition: transform .4s cubic-bezier(.4,0,.2,1);
            position: relative;
        }
        .modal-overlay.active .modal { transform: scale(1) translateY(0); }
        .modal-close {
            position: absolute; top: 20px; right: 20px;
            font-family: 'JetBrains Mono', monospace; font-size: 11px;
            color: var(--text3); cursor: pointer;
            padding: 6px 10px; border: 1px solid var(--border); border-radius: 6px;
            transition: all .2s;
        }
        .modal-close:hover { border-color: var(--green); color: var(--green); }
        .modal-header   { display: flex; align-items: center; gap: 14px; margin-bottom: 20px; }
        .modal-icon-box { width: 52px; height: 52px; background: var(--bg3); border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 24px; }
        .modal-title h3 { font-size: 18px; font-weight: 600; margin-bottom: 3px; }
        .modal-title p  { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--text3); }
        .modal-value    { font-size: 56px; font-weight: 700; text-align: center; margin: 16px 0; }
        .modal-bar-label { display: flex; justify-content: space-between; font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--text3); margin-bottom: 6px; }
        .modal-bar-track { height: 6px; background: rgba(255,255,255,.05); border-radius: 3px; overflow: hidden; }
        .modal-bar-fill  { height: 100%; border-radius: 3px; transition: width .8s ease; }
        .modal-details   { display: grid; grid-template-columns: repeat(2,1fr); gap: 10px; margin-top: 20px; }
        .modal-detail    { background: var(--bg3); border: 1px solid var(--border); border-radius: 12px; padding: 14px; }
        .modal-dl        { font-family: 'JetBrains Mono', monospace; font-size: 10px; color: var(--text3); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; }
        .modal-dv        { font-size: 16px; font-weight: 600; }

        /* ── FOOTER ── */
        .footer {
            display: flex; justify-content: space-between; align-items: center;
            padding: 12px 28px; border-top: 1px solid var(--border);
            font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--text3);
        }

        /* ── MILESTONE ── */
        .milestone {
            font-family: 'JetBrains Mono', monospace; font-size: 12px;
            color: var(--green); background: rgba(61,255,160,.08);
            border: 1px solid rgba(61,255,160,.2); border-radius: 100px;
            padding: 7px 20px; display: inline-block; margin-top: 12px;
            animation: glowPulse 2s ease infinite;
        }
        @keyframes glowPulse {
            0%,100% { box-shadow: 0 0 16px rgba(61,255,160,.15); }
            50%      { box-shadow: 0 0 30px rgba(61,255,160,.35); }
        }

        /* ── ANIMATIONS ── */
        @keyframes fadeUp { from { opacity:0; transform:translateY(16px); } to { opacity:1; transform:translateY(0); } }
        .pipeline-section { animation: fadeUp .5s ease .1s both; }
        .middle-grid      { animation: fadeUp .5s ease .2s both; }
        .bottom-row       { animation: fadeUp .5s ease .3s both; }
    </style>
</head>
<body>

<!-- Modal -->
<div class="modal-overlay" id="modalOverlay">
    <div class="modal">
        <div class="modal-close" onclick="closeModal()">[ CLOSE ]</div>
        <div class="modal-header">
            <div class="modal-icon-box" id="mIcon">⚙️</div>
            <div class="modal-title">
                <h3 id="mTitle">Component</h3>
                <p id="mSub">Details</p>
            </div>
        </div>
        <div class="modal-value" id="mVal">—</div>
        <div>
            <div class="modal-bar-label"><span>UTILIZATION</span><span id="mPct">—</span></div>
            <div class="modal-bar-track"><div class="modal-bar-fill" id="mBarFill"></div></div>
        </div>
        <div class="modal-details" id="mDetails"></div>
    </div>
</div>

<!-- Topbar -->
<div class="topbar">
    <div class="topbar-brand">
        <div class="logo-box">CI</div>
        <div>
            <div class="brand-name">CI/CD Automation Project</div>
            <div class="brand-sub mono">// PRODUCTION DASHBOARD</div>
        </div>
    </div>
    <div class="topbar-right">
        <div class="status-pill"><span class="pulse"></span>ALL SYSTEMS NOMINAL</div>
        <div class="clock mono" id="clock">--:--:--</div>
    </div>
</div>

<!-- Pipeline -->
<div class="pipeline-section">
    <div class="section-label">GitHub Actions Pipeline</div>
    <div class="pipeline-track">
        <div class="pipeline-header">
            <div class="pipeline-title">Flask CI/CD Pipeline <span style="color:var(--text2);font-weight:400;font-size:13px">· main branch</span></div>
            <div class="commit-info mono">push → <span class="commit-sha">main</span> · "Automated deploy via GitHub Actions"</div>
        </div>
        <div class="stages">
            <div class="stage done">
                <div class="stage-dot done">✓</div>
                <div class="stage-name">Checkout</div>
                <div class="stage-time">3s</div>
            </div>
            <div class="stage done">
                <div class="stage-dot done">✓</div>
                <div class="stage-name">DockerHub Login</div>
                <div class="stage-time">5s</div>
            </div>
            <div class="stage done">
                <div class="stage-dot done">✓</div>
                <div class="stage-name">Build & Push</div>
                <div class="stage-time">1m 12s</div>
            </div>
            <div class="stage running" id="stage-deploy">
                <div class="stage-dot running" id="stage-deploy-dot">⟳</div>
                <div class="stage-name">SSH Deploy</div>
                <div class="stage-time" id="deploy-timer">0s</div>
            </div>
            <div class="stage pending" id="stage-health">
                <div class="stage-dot pending" id="stage-health-dot">·</div>
                <div class="stage-name">Health Check</div>
                <div class="stage-time" id="health-timer">—</div>
            </div>
        </div>
    </div>
</div>

<!-- Middle Grid -->
<div class="middle-grid">
    <div class="card">
        <div class="card-header">
            <div class="card-icon green">🚀</div>
            <div class="card-badge badge-green">LIVE</div>
        </div>
        <div class="card-label">Total Visits</div>
        <div class="card-value" style="color:var(--green)">""" + str(count) + """</div>
        <div class="card-sub">Tracked via Redis</div>
        """ + (f'<div class="milestone">{milestone}</div>' if milestone else '') + """
    </div>

    <div class="card">
        <div class="card-header">
            <div class="card-icon blue">⏱</div>
            <div class="card-badge badge-blue">STABLE</div>
        </div>
        <div class="card-label">Uptime</div>
        <div class="card-value" id="heroUptime" style="color:var(--blue);font-size:22px">""" + h['uptime'] + """</div>
        <div class="card-sub">EC2 instance running</div>
    </div>

    <div class="card">
        <div class="card-header">
            <div class="card-icon purple">🐳</div>
            <div class="card-badge badge-amber">raeel/flask-app</div>
        </div>
        <div class="card-label">Docker Image</div>
        <div class="card-value" style="color:var(--purple);font-size:20px">:latest</div>
        <div class="card-sub">Pushed to Docker Hub</div>
    </div>

    <!-- Health Cards -->
    <div class="health-grid">
        <div class="hcard" onclick="openModal('cpu')">
            <div class="hcard-icon">⚙️</div>
            <div class="hcard-name">CPU</div>
            <div class="hcard-val" id="cpu-val" style="color:""" + h['cpu_color'] + """">""" + str(h['cpu']) + """%</div>
            <div class="hcard-badge" id="cpu-badge" style="color:""" + h['cpu_color'] + """;border-color:""" + h['cpu_color'] + """55">""" + h['cpu_label'] + """</div>
            <div class="hbar"><div class="hbar-fill" id="cpu-bar" style="background:""" + h['cpu_color'] + """;width:""" + str(h['cpu']) + """%"></div></div>
        </div>
        <div class="hcard" onclick="openModal('mem')">
            <div class="hcard-icon">🧠</div>
            <div class="hcard-name">MEMORY</div>
            <div class="hcard-val" id="mem-val" style="color:""" + h['mem_color'] + """">""" + str(h['mem']) + """%</div>
            <div class="hcard-badge" id="mem-badge" style="color:""" + h['mem_color'] + """;border-color:""" + h['mem_color'] + """55">""" + h['mem_label'] + """</div>
            <div class="hbar"><div class="hbar-fill" id="mem-bar" style="background:""" + h['mem_color'] + """;width:""" + str(h['mem']) + """%"></div></div>
        </div>
        <div class="hcard" onclick="openModal('disk')">
            <div class="hcard-icon">💾</div>
            <div class="hcard-name">DISK</div>
            <div class="hcard-val" id="disk-val" style="color:""" + h['disk_color'] + """">""" + str(h['disk']) + """%</div>
            <div class="hcard-badge" id="disk-badge" style="color:""" + h['disk_color'] + """;border-color:""" + h['disk_color'] + """55">""" + h['disk_label'] + """</div>
            <div class="hbar"><div class="hbar-fill" id="disk-bar" style="background:""" + h['disk_color'] + """;width:""" + str(h['disk']) + """%"></div></div>
        </div>
        <div class="hcard" onclick="openModal('net')">
            <div class="hcard-icon">🌐</div>
            <div class="hcard-name">NETWORK</div>
            <div class="hcard-val" id="net-val" style="color:var(--blue);font-size:14px">""" + str(h['net_sent']) + """↑</div>
            <div class="hcard-badge" style="color:var(--blue);border-color:rgba(56,182,255,.3)">TX/RX</div>
            <div class="hbar"><div class="hbar-fill" id="net-bar" style="background:var(--blue);width:60%"></div></div>
        </div>
        <div class="hcard" onclick="openModal('flask')">
            <div class="hcard-icon">🌶️</div>
            <div class="hcard-name">FLASK</div>
            <div class="hcard-val" style="color:var(--green);font-size:14px">SERVING</div>
            <div class="hcard-badge" style="color:var(--green);border-color:rgba(61,255,160,.3)">ONLINE</div>
            <div class="hbar"><div class="hbar-fill" style="background:var(--green);width:100%"></div></div>
        </div>
    </div>
</div>

<!-- Bottom Row -->
<div class="bottom-row">
    <div class="stack-card">
        <div class="section-label">Tech Stack</div>
        <div class="stack-pills">
            <span class="pill">🐍 Python 3.11</span>
            <span class="pill">🌶️ Flask</span>
            <span class="pill">🗄️ Redis</span>
            <span class="pill">🐳 Docker</span>
            <span class="pill">📦 Docker Compose</span>
            <span class="pill highlight">⚡ GitHub Actions</span>
            <span class="pill highlight">🐙 GitHub</span>
            <span class="pill">🏔️ Docker Hub</span>
            <span class="pill">☁️ AWS EC2</span>
            <span class="pill">📊 Psutil</span>
            <span class="pill">🔑 appleboy/ssh-action</span>
        </div>
    </div>
    <div class="actions-card">
        <div class="section-label">Quick Actions</div>
        <div class="action-btn"><span class="action-dot dot-green"></span>Trigger Deploy</div>
        <div class="action-btn"><span class="action-dot dot-blue"></span>View GH Actions Log</div>
        <div class="action-btn"><span class="action-dot dot-amber"></span>Rollback to Previous</div>
    </div>
</div>

<!-- Footer -->
<div class="footer">
    <div>Flask CI/CD · AWS EC2 · Production</div>
    <div>GitHub Actions · appleboy/ssh-action@v1.0.3</div>
    <div id="footer-date"></div>
</div>

<script>
    // Clock
    function updateClock() {
        const n = new Date();
        document.getElementById('clock').textContent = n.toTimeString().split(' ')[0];
        document.getElementById('footer-date').textContent = n.toLocaleDateString('en-US', {
            weekday: 'short', month: 'short', day: 'numeric', year: 'numeric'
        });
    }
    updateClock();
    setInterval(updateClock, 1000);

    // Pipeline stage animation
    let deploySecs = 0;
    setInterval(() => {
        deploySecs++;
        const t = document.getElementById('deploy-timer');
        if (t) t.textContent = deploySecs < 60 ? deploySecs + 's' : Math.floor(deploySecs/60) + 'm ' + (deploySecs%60) + 's';
        if (deploySecs === 12) {
            document.getElementById('stage-deploy').className = 'stage done';
            document.getElementById('stage-deploy-dot').className = 'stage-dot done';
            document.getElementById('stage-deploy-dot').textContent = '✓';
            document.getElementById('stage-health').className = 'stage running';
            document.getElementById('stage-health-dot').className = 'stage-dot running';
            document.getElementById('stage-health-dot').textContent = '⟳';
        }
        if (deploySecs === 18) {
            document.getElementById('stage-health').className = 'stage done';
            document.getElementById('stage-health-dot').className = 'stage-dot done';
            document.getElementById('stage-health-dot').textContent = '✓';
            document.getElementById('health-timer').textContent = '6s';
        }
    }, 1000);

    // Health data
    let hData = {
        cpu: """ + str(h['cpu']) + """, cpu_color: '""" + h['cpu_color'] + """', cpu_label: '""" + h['cpu_label'] + """',
        cpu_count: """ + str(h['cpu_count']) + """, cpu_freq: """ + str(h['cpu_freq']) + """,
        mem: """ + str(h['mem']) + """, mem_color: '""" + h['mem_color'] + """', mem_label: '""" + h['mem_label'] + """',
        mem_total: """ + str(h['mem_total']) + """, mem_used_gb: """ + str(h['mem_used_gb']) + """, mem_available: """ + str(h['mem_available']) + """,
        disk: """ + str(h['disk']) + """, disk_color: '""" + h['disk_color'] + """', disk_label: '""" + h['disk_label'] + """',
        disk_total: """ + str(h['disk_total']) + """, disk_used_gb: """ + str(h['disk_used_gb']) + """, disk_free: """ + str(h['disk_free']) + """,
        net_sent: """ + str(h['net_sent']) + """, net_recv: """ + str(h['net_recv']) + """,
        uptime: '""" + h['uptime'] + """', uptime_secs: """ + str(h['uptime_secs']) + """
    };

    // Modal definitions
    const modalDefs = {
        cpu:   d => ({ icon:'⚙️', title:'CPU PROCESSOR',     sub:`${d.cpu_count} Cores · ${d.cpu_freq} MHz`, val:`${d.cpu}%`,       color:d.cpu_color,  pct:d.cpu,  details:[['Load',`${d.cpu}%`],['Cores',d.cpu_count],['Freq',`${d.cpu_freq} MHz`],['Status',d.cpu_label]] }),
        mem:   d => ({ icon:'🧠', title:'MEMORY (RAM)',       sub:`${d.mem_total} GB Total`,                  val:`${d.mem}%`,       color:d.mem_color,  pct:d.mem,  details:[['Used',`${d.mem_used_gb} GB`],['Total',`${d.mem_total} GB`],['Free',`${d.mem_available} MB`],['Status',d.mem_label]] }),
        disk:  d => ({ icon:'💾', title:'DISK STORAGE',       sub:`${d.disk_total} GB Total`,                 val:`${d.disk}%`,      color:d.disk_color, pct:d.disk, details:[['Used',`${d.disk_used_gb} GB`],['Total',`${d.disk_total} GB`],['Free',`${d.disk_free} GB`],['Status',d.disk_label]] }),
        net:   d => ({ icon:'🌐', title:'NETWORK I/O',        sub:'Bytes Transferred',                        val:`${d.net_sent}MB`, color:'#38b6ff',    pct:60,     details:[['Sent',`${d.net_sent} MB`],['Received',`${d.net_recv} MB`],['Uptime',d.uptime],['Secs',d.uptime_secs]] }),
        flask: d => ({ icon:'🌶️', title:'FLASK APPLICATION',  sub:'Web Server · Port 5000',                   val:'SERVING',         color:'#3dffa0',    pct:100,    details:[['Status','ONLINE'],['Framework','Flask'],['Python','3.11'],['Port','5000']] }),
    };

    let activeModal = null;

    function openModal(type) {
        activeModal = type;
        const d = modalDefs[type](hData);
        document.getElementById('mIcon').textContent = d.icon;
        document.getElementById('mTitle').textContent = d.title;
        document.getElementById('mSub').textContent = d.sub;
        document.getElementById('mVal').textContent = d.val;
        document.getElementById('mVal').style.color = d.color;
        document.getElementById('mPct').textContent = typeof d.pct === 'number' ? d.pct + '%' : d.pct;
        const bar = document.getElementById('mBarFill');
        bar.style.background = d.color;
        bar.style.width = '0%';
        setTimeout(() => bar.style.width = d.pct + '%', 100);
        document.getElementById('mDetails').innerHTML = d.details.map(([l,v]) =>
            `<div class="modal-detail"><div class="modal-dl">${l}</div><div class="modal-dv">${v}</div></div>`
        ).join('');
        document.getElementById('modalOverlay').classList.add('active');
    }

    function closeModal() {
        document.getElementById('modalOverlay').classList.remove('active');
        activeModal = null;
    }

    document.getElementById('modalOverlay').addEventListener('click', e => {
        if (e.target === document.getElementById('modalOverlay')) closeModal();
    });

    // Auto-refresh health
    let countdown = 5;
    function refreshHealth() {
        fetch('/health')
            .then(r => r.json())
            .then(d => {
                hData = d;
                [['cpu', d.cpu, d.cpu_color, d.cpu_label],
                 ['mem', d.mem, d.mem_color, d.mem_label],
                 ['disk', d.disk, d.disk_color, d.disk_label]].forEach(([id, val, color, label]) => {
                    const v = document.getElementById(id+'-val');
                    const b = document.getElementById(id+'-badge');
                    const r = document.getElementById(id+'-bar');
                    if (v) { v.textContent = val + '%'; v.style.color = color; }
                    if (b) { b.textContent = label; b.style.color = color; b.style.borderColor = color + '55'; }
                    if (r) { r.style.background = color; r.style.width = val + '%'; }
                });
                const nu = document.getElementById('net-val');
                if (nu) nu.textContent = d.net_sent + '↑ MB';
                const hu = document.getElementById('heroUptime');
                if (hu) hu.textContent = d.uptime;
                if (activeModal) openModal(activeModal);
                countdown = 5;
            })
            .catch(() => {});
    }

    setInterval(() => {
        countdown--;
        if (countdown <= 0) refreshHealth();
    }, 1000);
</script>
</body>
</html>"""

    return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
