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
        if v < 40:   return "#00e87a"
        elif v < 70: return "#f59e0b"
        elif v < 85: return "#ff9966"
        else:        return "#f05050"

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
    <meta name="viewport" content="width=1280">
    <title>CI/CD Automation Project</title>
    <link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        :root {
            --bg:     #090b0e;
            --bg2:    #10141a;
            --bg3:    #171c24;
            --green:  #00e87a;
            --blue:   #1a9fff;
            --purple: #a855f7;
            --red:    #f05050;
            --amber:  #f59e0b;
            --cyan:   #06b6d4;
            --text:   #dde3ed;
            --text2:  #7a8799;
            --text3:  #3d4a5c;
            --border: rgba(255,255,255,0.06);
            --border2:rgba(255,255,255,0.10);
        }
        html, body {
            background: var(--bg);
            color: var(--text);
            font-family: 'Syne', sans-serif;
            width: 1280px;
            height: 720px;
            overflow: hidden;
            font-size: 11px;
        }
        .page {
            width: 1280px;
            height: 720px;
            display: grid;
            grid-template-rows: 44px 94px 1fr 44px;
            overflow: hidden;
            background:
                radial-gradient(ellipse at 8% 0%,   rgba(0,232,122,0.05)  0%, transparent 40%),
                radial-gradient(ellipse at 92% 100%, rgba(26,159,255,0.05) 0%, transparent 40%),
                var(--bg);
        }

        /* TOPBAR */
        .topbar {
            display: flex; justify-content: space-between; align-items: center;
            padding: 0 20px; border-bottom: 1px solid var(--border);
            background: rgba(9,11,14,0.98);
        }
        .topbar-brand { display: flex; align-items: center; gap: 9px; }
        .logo-box {
            width: 26px; height: 26px;
            background: linear-gradient(135deg, var(--green), var(--blue));
            border-radius: 7px; display: flex; align-items: center; justify-content: center;
            font-weight: 700; font-size: 10px; color: #090b0e;
        }
        .brand-name { font-size: 12px; font-weight: 700; }
        .brand-sub  { font-size: 9px; color: var(--text3); font-family: 'JetBrains Mono', monospace; letter-spacing: 2px; margin-left: 6px; }
        .topbar-right { display: flex; align-items: center; gap: 14px; }
        .status-pill {
            display: flex; align-items: center; gap: 5px;
            background: rgba(0,232,122,0.07); border: 1px solid rgba(0,232,122,0.18);
            border-radius: 100px; padding: 3px 10px;
            font-size: 9px; font-family: 'JetBrains Mono', monospace; color: var(--green);
        }
        .pulse { width: 6px; height: 6px; border-radius: 50%; background: var(--green); animation: pulse 2s ease infinite; flex-shrink: 0; }
        @keyframes pulse { 0%,100%{opacity:1;transform:scale(1)}50%{opacity:.4;transform:scale(1.4)} }
        .clock { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--text2); }

        /* PIPELINE */
        .pipeline-section { padding: 8px 20px 0; display: flex; flex-direction: column; gap: 5px; }
        .section-label { font-family: 'JetBrains Mono', monospace; font-size: 9px; letter-spacing: 2px; color: var(--text3); text-transform: uppercase; }
        .pipeline-track {
            background: var(--bg2); border: 1px solid var(--border);
            border-radius: 10px; padding: 9px 16px;
            display: flex; flex-direction: column; gap: 8px;
        }
        .pipeline-header { display: flex; justify-content: space-between; align-items: center; }
        .pipeline-title  { font-size: 11px; font-weight: 600; }
        .commit-info     { font-family: 'JetBrains Mono', monospace; font-size: 9px; color: var(--text2); }
        .commit-sha      { color: var(--blue); }
        .stages { display: grid; grid-template-columns: repeat(5,1fr); position: relative; }
        .stage  { display: flex; flex-direction: column; align-items: center; gap: 3px; position: relative; }
        .stage:not(:last-child)::after {
            content:''; position: absolute; right: -50%; top: 13px;
            width: 100%; height: 1.5px; background: var(--border); z-index: 0;
        }
        .stage:not(:last-child).done::after    { background: var(--green); }
        .stage:not(:last-child).running::after { background: linear-gradient(90deg, var(--green), var(--border)); }
        .stage-dot {
            width: 27px; height: 27px; border-radius: 8px;
            display: flex; align-items: center; justify-content: center;
            font-size: 11px; position: relative; z-index: 1;
        }
        .stage-dot.done    { background: rgba(0,232,122,.1);  border: 1.5px solid var(--green); }
        .stage-dot.running { background: rgba(26,159,255,.1); border: 1.5px solid var(--blue); animation: sp 1.5s ease infinite; }
        .stage-dot.pending { background: var(--bg3);          border: 1.5px solid var(--border); color: var(--text3); }
        @keyframes sp { 0%,100%{box-shadow:0 0 8px rgba(26,159,255,.2)}50%{box-shadow:0 0 16px rgba(26,159,255,.5)} }
        .stage-name { font-size: 8.5px; font-family: 'JetBrains Mono', monospace; color: var(--text2); text-align: center; }
        .stage-time { font-size: 8px; font-family: 'JetBrains Mono', monospace; color: var(--text3); }

        /* MAIN */
        .main-content {
            display: grid; grid-template-columns: 192px 1fr 168px;
            gap: 10px; padding: 10px 20px; overflow: hidden;
        }

        /* LEFT KPI */
        .left-col { display: flex; flex-direction: column; gap: 7px; }
        .kpi-card {
            background: var(--bg2); border: 1px solid var(--border);
            border-radius: 10px; padding: 9px 11px; flex: 1;
        }
        .kpi-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; }
        .kpi-icon   { font-size: 13px; }
        .kpi-badge  { font-family: 'JetBrains Mono', monospace; font-size: 8px; padding: 2px 7px; border-radius: 100px; border: 1px solid; }
        .bg-green  { color: var(--green);  border-color: rgba(0,232,122,.3);  background: rgba(0,232,122,.07); }
        .bg-blue   { color: var(--blue);   border-color: rgba(26,159,255,.3); background: rgba(26,159,255,.07); }
        .bg-purple { color: var(--purple); border-color: rgba(168,85,247,.3); background: rgba(168,85,247,.07); }
        .kpi-label { font-size: 8.5px; font-family: 'JetBrains Mono', monospace; color: var(--text3); letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 2px; }
        .kpi-value { font-size: 20px; font-weight: 700; line-height: 1.1; }
        .kpi-sub   { font-size: 9px; color: var(--text2); margin-top: 2px; }
        .milestone-sm {
            font-family: 'JetBrains Mono', monospace; font-size: 7.5px;
            color: var(--green); background: rgba(0,232,122,.07);
            border: 1px solid rgba(0,232,122,.18); border-radius: 100px;
            padding: 2px 7px; display: inline-block; margin-top: 3px;
        }

        /* CENTER */
        .center-col { display: flex; flex-direction: column; gap: 7px; }
        .health-grid { display: grid; grid-template-columns: repeat(5,1fr); gap: 7px; }
        .hcard {
            background: var(--bg2); border: 1px solid var(--border);
            border-radius: 9px; padding: 9px 7px; text-align: center;
            cursor: pointer; transition: all .2s;
            display: flex; flex-direction: column; align-items: center; gap: 3px;
        }
        .hcard:hover { border-color: rgba(0,232,122,.2); transform: translateY(-2px); }
        .hcard-icon  { font-size: 13px; }
        .hcard-name  { font-family: 'JetBrains Mono', monospace; font-size: 7.5px; letter-spacing: 1px; color: var(--text3); text-transform: uppercase; }
        .hcard-val   { font-size: 16px; font-weight: 700; }
        .hcard-badge { font-family: 'JetBrains Mono', monospace; font-size: 7px; padding: 2px 6px; border-radius: 100px; border: 1px solid; }
        .hbar        { width: 100%; background: rgba(255,255,255,.04); border-radius: 2px; height: 3px; overflow: hidden; }
        .hbar-fill   { height: 100%; border-radius: 2px; transition: width .8s cubic-bezier(.4,0,.2,1); }
        .docker-card {
            background: var(--bg2); border: 1px solid var(--border);
            border-radius: 10px; padding: 9px 12px;
        }
        .docker-row { display: flex; align-items: center; justify-content: space-between; }
        .docker-col { }
        .docker-tag { font-family: 'JetBrains Mono', monospace; font-size: 13px; font-weight: 700; color: var(--purple); }

        /* RIGHT */
        .right-col { display: flex; flex-direction: column; gap: 7px; }
        .stack-card {
            background: var(--bg2); border: 1px solid var(--border);
            border-radius: 10px; padding: 9px 10px; flex: 1;
        }
        .stack-pills { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 6px; }
        .pill {
            font-family: 'JetBrains Mono', monospace; font-size: 8px;
            padding: 3px 8px; border-radius: 100px;
            border: 1px solid var(--border); color: var(--text2); transition: all .2s;
        }
        .pill:hover   { border-color: rgba(0,232,122,.25); color: var(--green); }
        .pill.hi-blue { border-color: rgba(26,159,255,.28); color: var(--blue); background: rgba(26,159,255,.06); }
        .actions-card {
            background: var(--bg2); border: 1px solid var(--border);
            border-radius: 10px; padding: 9px 10px;
            display: flex; flex-direction: column; gap: 5px;
        }
        .action-btn {
            display: flex; align-items: center; gap: 7px;
            padding: 5px 8px; background: var(--bg3);
            border: 1px solid var(--border); border-radius: 7px;
            cursor: pointer; transition: all .2s;
            font-family: 'JetBrains Mono', monospace; font-size: 8.5px; color: var(--text);
        }
        .action-btn:hover { border-color: rgba(0,232,122,.22); color: var(--green); }
        .adot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
        .dg { background: var(--green); } .db { background: var(--blue); } .da { background: var(--amber); }

        /* MODAL */
        .modal-overlay {
            position: fixed; inset: 0; z-index: 1000;
            background: rgba(0,0,0,.85); backdrop-filter: blur(16px);
            display: flex; align-items: center; justify-content: center;
            opacity: 0; pointer-events: none; transition: opacity .25s;
        }
        .modal-overlay.active { opacity: 1; pointer-events: all; }
        .modal {
            background: var(--bg2); border: 1px solid var(--border2);
            border-radius: 14px; padding: 18px; max-width: 340px; width: 90%;
            transform: scale(.93) translateY(10px);
            transition: transform .3s cubic-bezier(.4,0,.2,1); position: relative;
        }
        .modal-overlay.active .modal { transform: scale(1) translateY(0); }
        .modal-close {
            position: absolute; top: 12px; right: 12px;
            font-family: 'JetBrains Mono', monospace; font-size: 8px;
            color: var(--text3); cursor: pointer; padding: 3px 7px;
            border: 1px solid var(--border); border-radius: 5px; transition: all .2s;
        }
        .modal-close:hover { border-color: var(--green); color: var(--green); }
        .modal-header { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
        .modal-icon-box { width: 38px; height: 38px; background: var(--bg3); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 17px; }
        .modal-title h3 { font-size: 13px; font-weight: 600; margin-bottom: 2px; }
        .modal-title p  { font-family: 'JetBrains Mono', monospace; font-size: 8.5px; color: var(--text3); }
        .modal-value    { font-size: 40px; font-weight: 700; text-align: center; margin: 8px 0; }
        .modal-bar-label{ display: flex; justify-content: space-between; font-family: 'JetBrains Mono', monospace; font-size: 8.5px; color: var(--text3); margin-bottom: 4px; }
        .modal-bar-track{ height: 4px; background: rgba(255,255,255,.04); border-radius: 3px; overflow: hidden; }
        .modal-bar-fill { height: 100%; border-radius: 3px; transition: width .8s ease; }
        .modal-details  { display: grid; grid-template-columns: repeat(2,1fr); gap: 7px; margin-top: 12px; }
        .modal-detail   { background: var(--bg3); border: 1px solid var(--border); border-radius: 8px; padding: 9px; }
        .modal-dl       { font-family: 'JetBrains Mono', monospace; font-size: 7.5px; color: var(--text3); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 3px; }
        .modal-dv       { font-size: 12px; font-weight: 600; }

        /* FOOTER */
        .footer {
            display: flex; justify-content: space-between; align-items: center;
            padding: 0 20px; border-top: 1px solid var(--border);
            font-family: 'JetBrains Mono', monospace; font-size: 9px; color: var(--text3);
            background: rgba(9,11,14,0.98);
        }
        .footer-status { display: flex; align-items: center; gap: 6px; }
        .footer-dot { width: 5px; height: 5px; border-radius: 50%; background: var(--green); animation: pulse 2s ease infinite; }

        @keyframes fadeUp { from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)} }
        .pipeline-section { animation: fadeUp .35s ease .05s both; }
        .main-content     { animation: fadeUp .35s ease .12s both; }
    </style>
</head>
<body>

<div class="modal-overlay" id="modalOverlay">
    <div class="modal">
        <div class="modal-close" onclick="closeModal()">[ ESC ]</div>
        <div class="modal-header">
            <div class="modal-icon-box" id="mIcon">⚙️</div>
            <div class="modal-title"><h3 id="mTitle">—</h3><p id="mSub">—</p></div>
        </div>
        <div class="modal-value" id="mVal">—</div>
        <div>
            <div class="modal-bar-label"><span>UTILIZATION</span><span id="mPct">—</span></div>
            <div class="modal-bar-track"><div class="modal-bar-fill" id="mBarFill"></div></div>
        </div>
        <div class="modal-details" id="mDetails"></div>
    </div>
</div>

<div class="page">

    <div class="topbar">
        <div class="topbar-brand">
            <div class="logo-box">CI</div>
            <div class="brand-name">CI/CD Automation Project</div>
            <span class="brand-sub">// PRODUCTION DASHBOARD</span>
        </div>
        <div class="topbar-right">
            <div class="status-pill"><span class="pulse"></span>ALL SYSTEMS NOMINAL</div>
            <div class="clock" id="clock">--:--:--</div>
        </div>
    </div>

    <div class="pipeline-section">
        <div class="section-label">GitHub Actions · Flask CI/CD Pipeline · main branch</div>
        <div class="pipeline-track">
            <div class="pipeline-header">
                <div class="pipeline-title">
                    Last run: <span style="color:var(--green)">✓ Success</span>
                    &nbsp;·&nbsp;<span style="color:var(--text2);font-weight:400">push → main</span>
                </div>
                <div class="commit-info">
                    commit <span class="commit-sha">a3f92bc</span>
                    · "Update docker-compose config" · 2m ago · raeel/flask-app:latest
                </div>
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

    <div class="main-content">

        <div class="left-col">
            <div class="kpi-card">
                <div class="kpi-header">
                    <div class="kpi-icon">🚀</div>
                    <div class="kpi-badge bg-green">LIVE</div>
                </div>
                <div class="kpi-label">Total Visits</div>
                <div class="kpi-value" style="color:var(--green)">""" + str(count) + """</div>
                <div class="kpi-sub">Tracked via Redis</div>
                """ + (f'<div class="milestone-sm">{milestone}</div>' if milestone else '') + """
            </div>
            <div class="kpi-card">
                <div class="kpi-header">
                    <div class="kpi-icon">⏱</div>
                    <div class="kpi-badge bg-blue">STABLE</div>
                </div>
                <div class="kpi-label">Uptime</div>
                <div class="kpi-value" id="heroUptime" style="color:var(--blue);font-size:15px">""" + h['uptime'] + """</div>
                <div class="kpi-sub">EC2 instance</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-header">
                    <div class="kpi-icon">🐳</div>
                    <div class="kpi-badge bg-purple">Hub</div>
                </div>
                <div class="kpi-label">Image</div>
                <div class="kpi-value" style="color:var(--purple);font-size:12px">raeel/flask-app</div>
                <div class="kpi-sub" style="color:var(--amber)">:latest pushed ✓</div>
            </div>
        </div>

        <div class="center-col">
            <div class="section-label">// System Health Monitor</div>
            <div class="health-grid">
                <div class="hcard" onclick="openModal('cpu')">
                    <div class="hcard-icon">⚙️</div>
                    <div class="hcard-name">CPU</div>
                    <div class="hcard-val" id="cpu-val" style="color:""" + h['cpu_color'] + """">""" + str(h['cpu']) + """%</div>
                    <div class="hcard-badge" id="cpu-badge" style="color:""" + h['cpu_color'] + """;border-color:""" + h['cpu_color'] + """44">""" + h['cpu_label'] + """</div>
                    <div class="hbar"><div class="hbar-fill" id="cpu-bar" style="background:""" + h['cpu_color'] + """;width:""" + str(h['cpu']) + """%"></div></div>
                </div>
                <div class="hcard" onclick="openModal('mem')">
                    <div class="hcard-icon">🧠</div>
                    <div class="hcard-name">MEM</div>
                    <div class="hcard-val" id="mem-val" style="color:""" + h['mem_color'] + """">""" + str(h['mem']) + """%</div>
                    <div class="hcard-badge" id="mem-badge" style="color:""" + h['mem_color'] + """;border-color:""" + h['mem_color'] + """44">""" + h['mem_label'] + """</div>
                    <div class="hbar"><div class="hbar-fill" id="mem-bar" style="background:""" + h['mem_color'] + """;width:""" + str(h['mem']) + """%"></div></div>
                </div>
                <div class="hcard" onclick="openModal('disk')">
                    <div class="hcard-icon">💾</div>
                    <div class="hcard-name">DISK</div>
                    <div class="hcard-val" id="disk-val" style="color:""" + h['disk_color'] + """">""" + str(h['disk']) + """%</div>
                    <div class="hcard-badge" id="disk-badge" style="color:""" + h['disk_color'] + """;border-color:""" + h['disk_color'] + """44">""" + h['disk_label'] + """</div>
                    <div class="hbar"><div class="hbar-fill" id="disk-bar" style="background:""" + h['disk_color'] + """;width:""" + str(h['disk']) + """%"></div></div>
                </div>
                <div class="hcard" onclick="openModal('net')">
                    <div class="hcard-icon">🌐</div>
                    <div class="hcard-name">NET</div>
                    <div class="hcard-val" id="net-val" style="color:var(--cyan);font-size:11px">""" + str(h['net_sent']) + """MB</div>
                    <div class="hcard-badge" style="color:var(--cyan);border-color:rgba(6,182,212,.3)">TX/RX</div>
                    <div class="hbar"><div class="hbar-fill" id="net-bar" style="background:var(--cyan);width:55%"></div></div>
                </div>
                <div class="hcard" onclick="openModal('flask')">
                    <div class="hcard-icon">🌶️</div>
                    <div class="hcard-name">FLASK</div>
                    <div class="hcard-val" style="color:var(--green);font-size:10px">SERVING</div>
                    <div class="hcard-badge" style="color:var(--green);border-color:rgba(0,232,122,.3)">ONLINE</div>
                    <div class="hbar"><div class="hbar-fill" style="background:var(--green);width:100%"></div></div>
                </div>
            </div>
            <div class="docker-card">
                <div class="docker-row">
                    <div class="docker-col">
                        <div class="section-label" style="margin-bottom:3px">Docker · AWS EC2 Deployment</div>
                        <div class="docker-tag">raeel/flask-app<span style="color:var(--amber)">:latest</span></div>
                    </div>
                    <div class="docker-col" style="text-align:right">
                        <div class="section-label" style="margin-bottom:3px">Deployed via</div>
                        <div style="font-size:10px;font-weight:600;color:var(--blue)">appleboy/ssh-action<span style="color:var(--text3)">@v1.0.3</span></div>
                    </div>
                    <div class="docker-col" style="text-align:right">
                        <div class="section-label" style="margin-bottom:3px">Platform</div>
                        <div style="font-size:10px;font-weight:600;color:var(--text)">AWS EC2 ☁️</div>
                    </div>
                    <div class="docker-col" style="text-align:right">
                        <div class="section-label" style="margin-bottom:3px">Container</div>
                        <div style="font-size:10px;font-weight:600;color:var(--green)">Running ✓</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="right-col">
            <div class="stack-card">
                <div class="section-label">Tech Stack</div>
                <div class="stack-pills">
                    <span class="pill">🐍 Python 3.11</span>
                    <span class="pill">🌶️ Flask</span>
                    <span class="pill">🗄️ Redis</span>
                    <span class="pill">🐳 Docker</span>
                    <span class="pill">📦 Compose</span>
                    <span class="pill hi-blue">⚡ GitHub Actions</span>
                    <span class="pill hi-blue">🐙 GitHub</span>
                    <span class="pill">🏔️ Docker Hub</span>
                    <span class="pill">☁️ AWS EC2</span>
                    <span class="pill">📊 Psutil</span>
                    <span class="pill">🔑 ssh-action</span>
                </div>
            </div>
            <div class="actions-card">
                <div class="section-label">Quick Actions</div>
                <div class="action-btn"><span class="adot dg"></span>Trigger Deploy</div>
                <div class="action-btn"><span class="adot db"></span>View GH Actions Log</div>
                <div class="action-btn"><span class="adot da"></span>Rollback to Previous</div>
            </div>
        </div>

    </div>

    <div class="footer">
        <div class="footer-status"><span class="footer-dot"></span>All systems operational</div>
        <div>Flask · Redis · Docker · GitHub Actions · AWS EC2</div>
        <div id="footer-date">—</div>
    </div>

</div>

<script>
    function updateClock() {
        const n = new Date();
        document.getElementById('clock').textContent = n.toTimeString().split(' ')[0];
        document.getElementById('footer-date').textContent = n.toLocaleDateString('en-US',{weekday:'short',month:'short',day:'numeric',year:'numeric'});
    }
    updateClock(); setInterval(updateClock, 1000);

    let deploySecs = 0;
    setInterval(() => {
        deploySecs++;
        const t = document.getElementById('deploy-timer');
        if (t) t.textContent = deploySecs < 60 ? deploySecs+'s' : Math.floor(deploySecs/60)+'m '+(deploySecs%60)+'s';
        if (deploySecs === 12) {
            document.getElementById('stage-deploy').className='stage done';
            document.getElementById('stage-deploy-dot').className='stage-dot done';
            document.getElementById('stage-deploy-dot').textContent='✓';
            document.getElementById('stage-health').className='stage running';
            document.getElementById('stage-health-dot').className='stage-dot running';
            document.getElementById('stage-health-dot').textContent='⟳';
        }
        if (deploySecs === 18) {
            document.getElementById('stage-health').className='stage done';
            document.getElementById('stage-health-dot').className='stage-dot done';
            document.getElementById('stage-health-dot').textContent='✓';
            document.getElementById('health-timer').textContent='6s';
        }
    }, 1000);

    let hData = {
        cpu:""" + str(h['cpu']) + """, cpu_color:'""" + h['cpu_color'] + """', cpu_label:'""" + h['cpu_label'] + """',
        cpu_count:""" + str(h['cpu_count']) + """, cpu_freq:""" + str(h['cpu_freq']) + """,
        mem:""" + str(h['mem']) + """, mem_color:'""" + h['mem_color'] + """', mem_label:'""" + h['mem_label'] + """',
        mem_total:""" + str(h['mem_total']) + """, mem_used_gb:""" + str(h['mem_used_gb']) + """, mem_available:""" + str(h['mem_available']) + """,
        disk:""" + str(h['disk']) + """, disk_color:'""" + h['disk_color'] + """', disk_label:'""" + h['disk_label'] + """',
        disk_total:""" + str(h['disk_total']) + """, disk_used_gb:""" + str(h['disk_used_gb']) + """, disk_free:""" + str(h['disk_free']) + """,
        net_sent:""" + str(h['net_sent']) + """, net_recv:""" + str(h['net_recv']) + """,
        uptime:'""" + h['uptime'] + """', uptime_secs:""" + str(h['uptime_secs']) + """
    };

    const modalDefs = {
        cpu:   d=>({icon:'⚙️',title:'CPU PROCESSOR',   sub:`${d.cpu_count} Cores · ${d.cpu_freq} MHz`,val:`${d.cpu}%`,      color:d.cpu_color, pct:d.cpu, details:[['Load',`${d.cpu}%`],['Cores',d.cpu_count],['Freq',`${d.cpu_freq} MHz`],['Status',d.cpu_label]]}),
        mem:   d=>({icon:'🧠',title:'MEMORY (RAM)',     sub:`${d.mem_total} GB Total`,                 val:`${d.mem}%`,      color:d.mem_color, pct:d.mem, details:[['Used',`${d.mem_used_gb} GB`],['Total',`${d.mem_total} GB`],['Free',`${d.mem_available} MB`],['Status',d.mem_label]]}),
        disk:  d=>({icon:'💾',title:'DISK STORAGE',     sub:`${d.disk_total} GB Total`,                val:`${d.disk}%`,     color:d.disk_color,pct:d.disk,details:[['Used',`${d.disk_used_gb} GB`],['Total',`${d.disk_total} GB`],['Free',`${d.disk_free} GB`],['Status',d.disk_label]]}),
        net:   d=>({icon:'🌐',title:'NETWORK I/O',      sub:'Bytes Transferred',                       val:`${d.net_sent}MB`,color:'#06b6d4',   pct:55,    details:[['Sent',`${d.net_sent} MB`],['Recv',`${d.net_recv} MB`],['Uptime',d.uptime],['Secs',d.uptime_secs]]}),
        flask: d=>({icon:'🌶️',title:'FLASK APP',        sub:'Web Server · Port 5000',                  val:'ONLINE',         color:'#00e87a',   pct:100,   details:[['Status','ONLINE'],['Framework','Flask'],['Python','3.11'],['Port','5000']]}),
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
        document.getElementById('mPct').textContent = typeof d.pct==='number' ? d.pct+'%' : d.pct;
        const bar = document.getElementById('mBarFill');
        bar.style.background = d.color; bar.style.width = '0%';
        setTimeout(()=> bar.style.width = d.pct+'%', 80);
        document.getElementById('mDetails').innerHTML = d.details.map(([l,v])=>
            `<div class="modal-detail"><div class="modal-dl">${l}</div><div class="modal-dv">${v}</div></div>`
        ).join('');
        document.getElementById('modalOverlay').classList.add('active');
    }

    function closeModal() {
        document.getElementById('modalOverlay').classList.remove('active');
        activeModal = null;
    }

    document.getElementById('modalOverlay').addEventListener('click', e=>{
        if (e.target===document.getElementById('modalOverlay')) closeModal();
    });

    let countdown = 5;
    function refreshHealth() {
        fetch('/health').then(r=>r.json()).then(d=>{
            hData = d;
            [['cpu',d.cpu,d.cpu_color,d.cpu_label],
             ['mem',d.mem,d.mem_color,d.mem_label],
             ['disk',d.disk,d.disk_color,d.disk_label]].forEach(([id,val,color,lbl])=>{
                const v=document.getElementById(id+'-val');
                const b=document.getElementById(id+'-badge');
                const r=document.getElementById(id+'-bar');
                if(v){v.textContent=val+'%';v.style.color=color;}
                if(b){b.textContent=lbl;b.style.color=color;b.style.borderColor=color+'44';}
                if(r){r.style.background=color;r.style.width=val+'%';}
            });
            const nu=document.getElementById('net-val'); if(nu) nu.textContent=d.net_sent+'MB';
            const hu=document.getElementById('heroUptime'); if(hu) hu.textContent=d.uptime;
            if(activeModal) openModal(activeModal);
            countdown=5;
        }).catch(()=>{});
    }
    setInterval(()=>{ if(--countdown<=0) refreshHealth(); },1000);
</script>
</body>
</html>"""

    return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
