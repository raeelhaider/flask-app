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
        if v < 40:   return "#1e6fff"
        elif v < 70: return "#0ea5e9"
        elif v < 85: return "#f59e0b"
        else:        return "#ef4444"

    def label(v):
        return "OPTIMAL" if v < 40 else "NOMINAL" if v < 70 else "ELEVATED" if v < 85 else "CRITICAL"

    def badge_style(v):
        if v < 40:   return "color:#1565c0;border-color:#90caf9;background:#e3f2fd"
        elif v < 70: return "color:#0277bd;border-color:#81d4fa;background:#e1f5fe"
        elif v < 85: return "color:#b45309;border-color:#fcd34d;background:#fef3c7"
        else:        return "color:#b91c1c;border-color:#fca5a5;background:#fee2e2"

    return dict(
        cpu=round(cpu, 1),           cpu_color=color(cpu),           cpu_label=label(cpu),         cpu_badge=badge_style(cpu),
        cpu_count=cpu_count,         cpu_freq=round(cpu_freq.current, 0) if cpu_freq else 0,
        mem=round(mem.percent, 1),   mem_color=color(mem.percent),   mem_label=label(mem.percent), mem_badge=badge_style(mem.percent),
        mem_total=round(mem.total/(1024**3), 1),
        mem_used_gb=round(mem.used/(1024**3), 1),
        mem_available=round(mem.available/(1024**2)),
        disk=round(disk.percent, 1), disk_color=color(disk.percent), disk_label=label(disk.percent), disk_badge=badge_style(disk.percent),
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

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=1280">
    <title>CI/CD Automation Project</title>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
        html, body {{ background: #f0f4f8; color: #1a2332; font-family: 'Space Grotesk', sans-serif; font-size: 12px; width: 1280px; height: 720px; overflow: hidden; }}

        .wrap {{ background: #f0f4f8; padding: 9px; display: flex; flex-direction: column; gap: 6px; width: 1280px; height: 720px; overflow: hidden; }}

        /* TOPBAR */
        .topbar {{ display: flex; justify-content: space-between; align-items: center; background: #ffffff; border: 1px solid #d0dce8; border-radius: 8px; padding: 7px 13px; box-shadow: 0 1px 3px rgba(30,80,140,.06); }}
        .brand  {{ display: flex; align-items: center; gap: 9px; }}
        .logo   {{ width: 28px; height: 28px; background: linear-gradient(135deg,#1e6fff,#0ea5e9); border-radius: 7px; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; color: #fff; flex-shrink: 0; }}
        .bname  {{ font-size: 13px; font-weight: 700; color: #1a2332; }}
        .bsub   {{ font-family: 'JetBrains Mono', monospace; font-size: 8px; color: #94a3b8; letter-spacing: 2px; margin-left: 5px; }}
        .spill  {{ display: flex; align-items: center; gap: 5px; background: #e8f5e9; border: 1px solid #a5d6a7; border-radius: 100px; padding: 3px 10px; font-family: 'JetBrains Mono', monospace; font-size: 8px; color: #2e7d32; }}
        .dot    {{ width: 5px; height: 5px; border-radius: 50%; background: #43a047; flex-shrink: 0; animation: pu 2s infinite; }}
        @keyframes pu {{ 0%,100%{{opacity:1}} 50%{{opacity:.35}} }}
        .clk    {{ font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #64748b; }}

        /* PIPELINE */
        .pipe   {{ background: #ffffff; border: 1px solid #d0dce8; border-radius: 8px; padding: 8px 13px; box-shadow: 0 1px 3px rgba(30,80,140,.06); }}
        .slbl   {{ font-family: 'JetBrains Mono', monospace; font-size: 8px; letter-spacing: 2px; color: #94a3b8; text-transform: uppercase; margin-bottom: 5px; }}
        .phdr   {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 7px; }}
        .ptitle {{ font-size: 12px; font-weight: 600; color: #1a2332; }}
        .cinfo  {{ font-family: 'JetBrains Mono', monospace; font-size: 8px; color: #94a3b8; }}
        .csha   {{ color: #1e6fff; }}
        .stages {{ display: grid; grid-template-columns: repeat(5,1fr); }}
        .stg    {{ display: flex; flex-direction: column; align-items: center; gap: 3px; position: relative; }}
        .stg:not(:last-child)::after {{ content:''; position: absolute; right: -50%; top: 12px; width: 100%; height: 1.5px; background: #e2e8f0; z-index: 0; }}
        .stg.done:not(:last-child)::after {{ background: #1e6fff; }}
        .stg.running:not(:last-child)::after {{ background: linear-gradient(90deg,#1e6fff,#e2e8f0); }}
        .sd     {{ width: 24px; height: 24px; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 10px; position: relative; z-index: 1; }}
        .sd.done    {{ background: #e8f0fe; border: 1.5px solid #1e6fff; color: #1e6fff; }}
        .sd.running {{ background: #e0f2fe; border: 1.5px solid #0ea5e9; color: #0ea5e9; animation: sp 1.5s infinite; }}
        .sd.pending {{ background: #f8fafc; border: 1.5px solid #e2e8f0; color: #cbd5e1; }}
        @keyframes sp {{ 0%,100%{{box-shadow:0 0 6px rgba(14,165,233,.2)}} 50%{{box-shadow:0 0 14px rgba(14,165,233,.45)}} }}
        .sn     {{ font-family: 'JetBrains Mono', monospace; font-size: 8px; color: #64748b; text-align: center; }}
        .st     {{ font-family: 'JetBrains Mono', monospace; font-size: 7px; color: #94a3b8; }}

        /* GRID */
        .grid3  {{ display: grid; grid-template-columns: 148px 1fr 148px; gap: 6px; width: 100%; align-items: stretch; }}
        .lcol, .rcol, .ccol {{ display: flex; flex-direction: column; gap: 6px; }}

        /* KPI CARDS */
        .kcard  {{ background: #ffffff; border: 1px solid #d0dce8; border-radius: 8px; padding: 10px 12px; flex: 1; box-shadow: 0 1px 3px rgba(30,80,140,.05); }}
        .khdr   {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; }}
        .kico   {{ font-size: 16px; }}
        .kbdg   {{ font-family: 'JetBrains Mono', monospace; font-size: 7.5px; padding: 2px 7px; border-radius: 100px; border: 1px solid; }}
        .kg     {{ color: #2e7d32; border-color: #a5d6a7; background: #e8f5e9; }}
        .kb     {{ color: #1565c0; border-color: #90caf9; background: #e3f2fd; }}
        .kw     {{ color: #6a1b9a; border-color: #ce93d8; background: #f3e5f5; }}
        .klbl   {{ font-family: 'JetBrains Mono', monospace; font-size: 8px; color: #94a3b8; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 3px; }}
        .kval   {{ font-size: 24px; font-weight: 700; line-height: 1.1; }}
        .ksub   {{ font-size: 10px; color: #64748b; margin-top: 3px; }}
        .milestone-sm {{ font-family: 'JetBrains Mono', monospace; font-size: 8px; color: #2e7d32; background: #e8f5e9; border: 1px solid #a5d6a7; border-radius: 100px; padding: 2px 8px; display: inline-block; margin-top: 4px; }}

        /* HEALTH CARDS */
        .hgrid  {{ display: grid; grid-template-columns: repeat(5,1fr); gap: 6px; }}
        .hcard  {{ background: #ffffff; border: 1px solid #d0dce8; border-radius: 8px; padding: 12px 6px; text-align: center; cursor: pointer; transition: border-color .2s, transform .15s, box-shadow .15s; display: flex; flex-direction: column; align-items: center; gap: 4px; box-shadow: 0 1px 3px rgba(30,80,140,.05); }}
        .hcard:hover {{ border-color: #1e6fff; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(30,111,255,.12); }}
        .hico   {{ font-size: 18px; }}
        .hn     {{ font-family: 'JetBrains Mono', monospace; font-size: 7.5px; letter-spacing: 1px; color: #94a3b8; text-transform: uppercase; }}
        .hv     {{ font-size: 20px; font-weight: 700; }}
        .hbdg   {{ font-family: 'JetBrains Mono', monospace; font-size: 7px; padding: 2px 7px; border-radius: 100px; border: 1px solid; }}
        .hbar   {{ width: 100%; background: #e2e8f0; border-radius: 2px; height: 3px; overflow: hidden; margin-top: 2px; }}
        .hbf    {{ height: 100%; border-radius: 2px; transition: width .8s cubic-bezier(.4,0,.2,1); }}

        /* BIG CARD */
        .bigcard {{ background: #ffffff; border: 1px solid #d0dce8; border-radius: 8px; padding: 11px 12px; flex: 1; box-shadow: 0 1px 3px rgba(30,80,140,.05); }}
        .depgrid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px; }}
        .depval  {{ font-size: 13px; font-weight: 600; margin-top: 3px; }}
        .logrow  {{ display: flex; gap: 8px; padding: 5px 0; border-bottom: 1px solid #f1f5f9; align-items: flex-start; }}
        .logrow:last-child {{ border-bottom: none; }}
        .logtime {{ font-family: 'JetBrains Mono', monospace; font-size: 8px; color: #94a3b8; min-width: 52px; padding-top: 1px; flex-shrink: 0; }}
        .logicon {{ font-size: 10px; min-width: 11px; flex-shrink: 0; }}
        .logmsg  {{ font-size: 10px; color: #64748b; line-height: 1.4; }}

        /* STACK + ACTIONS + WORKFLOW */
        .scard  {{ background: #ffffff; border: 1px solid #d0dce8; border-radius: 8px; padding: 10px 12px; flex: 1; box-shadow: 0 1px 3px rgba(30,80,140,.05); }}
        .spills {{ display: flex; flex-wrap: wrap; gap: 4px; margin-top: 6px; }}
        .pill   {{ font-family: 'JetBrains Mono', monospace; font-size: 8px; padding: 3px 9px; border-radius: 100px; border: 1px solid #d0dce8; color: #64748b; background: #f8fafc; transition: all .2s; cursor: default; }}
        .pill:hover {{ border-color: #1e6fff; color: #1e6fff; background: #e8f0fe; }}
        .pill.hi {{ border-color: #90caf9; color: #1565c0; background: #e3f2fd; }}
        .acard  {{ background: #ffffff; border: 1px solid #d0dce8; border-radius: 8px; padding: 10px 12px; display: flex; flex-direction: column; gap: 5px; box-shadow: 0 1px 3px rgba(30,80,140,.05); }}
        .abtn   {{ display: flex; align-items: center; gap: 7px; padding: 6px 9px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 10px; color: #1a2332; cursor: pointer; transition: all .2s; }}
        .abtn:hover {{ border-color: #1e6fff; color: #1e6fff; background: #e8f0fe; }}
        .adot   {{ width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }}
        .wcard  {{ background: #ffffff; border: 1px solid #d0dce8; border-radius: 8px; padding: 10px 12px; flex: 1; box-shadow: 0 1px 3px rgba(30,80,140,.05); }}
        .wline  {{ display: flex; gap: 6px; padding: 3px 0; }}
        .wkey   {{ font-family: 'JetBrains Mono', monospace; font-size: 9px; color: #1e6fff; min-width: 50px; flex-shrink: 0; }}
        .wval   {{ font-family: 'JetBrains Mono', monospace; font-size: 9px; color: #64748b; }}
        .wsec   {{ color: #0ea5e9; font-weight: 500; }}

        /* MODAL */
        .modal-overlay {{ position: fixed; inset: 0; z-index: 1000; background: rgba(15,23,42,.5); backdrop-filter: blur(8px); display: flex; align-items: center; justify-content: center; opacity: 0; pointer-events: none; transition: opacity .25s; }}
        .modal-overlay.active {{ opacity: 1; pointer-events: all; }}
        .modal  {{ background: #ffffff; border: 1px solid #d0dce8; border-radius: 14px; padding: 20px; max-width: 340px; width: 90%; transform: scale(.93) translateY(10px); transition: transform .3s cubic-bezier(.4,0,.2,1); position: relative; box-shadow: 0 20px 40px rgba(30,80,140,.15); }}
        .modal-overlay.active .modal {{ transform: scale(1) translateY(0); }}
        .modal-close {{ position: absolute; top: 12px; right: 12px; font-family: 'JetBrains Mono', monospace; font-size: 8px; color: #94a3b8; cursor: pointer; padding: 3px 7px; border: 1px solid #e2e8f0; border-radius: 5px; transition: all .2s; }}
        .modal-close:hover {{ border-color: #1e6fff; color: #1e6fff; }}
        .modal-header {{ display: flex; align-items: center; gap: 10px; margin-bottom: 14px; }}
        .modal-icon-box {{ width: 40px; height: 40px; background: #f0f4f8; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 18px; border: 1px solid #d0dce8; }}
        .modal-title h3 {{ font-size: 14px; font-weight: 600; margin-bottom: 2px; color: #1a2332; }}
        .modal-title p  {{ font-family: 'JetBrains Mono', monospace; font-size: 9px; color: #94a3b8; }}
        .modal-value    {{ font-size: 44px; font-weight: 700; text-align: center; margin: 10px 0; }}
        .modal-bar-label {{ display: flex; justify-content: space-between; font-family: 'JetBrains Mono', monospace; font-size: 9px; color: #94a3b8; margin-bottom: 5px; }}
        .modal-bar-track {{ height: 5px; background: #e2e8f0; border-radius: 3px; overflow: hidden; }}
        .modal-bar-fill  {{ height: 100%; border-radius: 3px; transition: width .8s ease; }}
        .modal-details  {{ display: grid; grid-template-columns: repeat(2,1fr); gap: 8px; margin-top: 14px; }}
        .modal-detail   {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 9px; padding: 10px; }}
        .modal-dl       {{ font-family: 'JetBrains Mono', monospace; font-size: 8px; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px; }}
        .modal-dv       {{ font-size: 13px; font-weight: 600; color: #1a2332; }}

        /* FOOTER */
        .footer {{ display: flex; justify-content: space-between; align-items: center; background: #ffffff; border: 1px solid #d0dce8; border-radius: 8px; padding: 6px 13px; font-family: 'JetBrains Mono', monospace; font-size: 8px; color: #94a3b8; box-shadow: 0 1px 3px rgba(30,80,140,.05); }}
        .fst    {{ display: flex; align-items: center; gap: 5px; }}
        .fdot   {{ width: 5px; height: 5px; border-radius: 50%; background: #43a047; animation: pu 2s infinite; }}

        @keyframes fadeUp {{ from{{opacity:0;transform:translateY(8px)}} to{{opacity:1;transform:translateY(0)}} }}
        .pipe  {{ animation: fadeUp .35s ease .05s both; }}
        .grid3 {{ animation: fadeUp .35s ease .12s both; }}
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

<div class="wrap">

    <div class="topbar">
        <div class="brand">
            <div class="logo">CI</div>
            <span class="bname">CI/CD Automation Project</span>
            <span class="bsub">// PRODUCTION DASHBOARD</span>
        </div>
        <div style="display:flex;align-items:center;gap:10px">
            <div class="spill"><span class="dot"></span>ALL SYSTEMS NOMINAL</div>
            <div class="clk" id="clock">--:--:--</div>
        </div>
    </div>

    <div class="pipe">
        <div class="slbl">GitHub Actions · Flask CI/CD Pipeline · main branch</div>
        <div class="phdr">
            <div class="ptitle">Last run: <span style="color:#2e7d32;font-weight:600">✓ Success</span> &nbsp;·&nbsp; <span style="color:#64748b;font-weight:400">push → main</span></div>
            <div class="cinfo">commit <span class="csha">a3f92bc</span> · "Update docker-compose config" · 2m ago · raeel/flask-app:latest</div>
        </div>
        <div class="stages">
            <div class="stg done"><div class="sd done">✓</div><div class="sn">Checkout</div><div class="st">3s</div></div>
            <div class="stg done"><div class="sd done">✓</div><div class="sn">DockerHub Login</div><div class="st">5s</div></div>
            <div class="stg done"><div class="sd done">✓</div><div class="sn">Build &amp; Push</div><div class="st">1m 12s</div></div>
            <div class="stg running" id="stage-deploy">
                <div class="sd running" id="stage-deploy-dot">⟳</div>
                <div class="sn">SSH Deploy</div>
                <div class="st" id="deploy-timer">0s</div>
            </div>
            <div class="stg pending" id="stage-health">
                <div class="sd pending" id="stage-health-dot">·</div>
                <div class="sn">Health Check</div>
                <div class="st" id="health-timer">—</div>
            </div>
        </div>
    </div>

    <div class="grid3">

        <div class="lcol">
            <div class="kcard">
                <div class="khdr"><span class="kico">🚀</span><span class="kbdg kg">LIVE</span></div>
                <div class="klbl">Total Visits</div>
                <div class="kval" style="color:#1e6fff">{count}</div>
                <div class="ksub">Tracked via Redis</div>
                {f'<div class="milestone-sm">{milestone}</div>' if milestone else ''}
            </div>
            <div class="kcard">
                <div class="khdr"><span class="kico">⏱</span><span class="kbdg kb">STABLE</span></div>
                <div class="klbl">Uptime</div>
                <div class="kval" id="heroUptime" style="color:#0ea5e9;font-size:20px">{h['uptime']}</div>
                <div class="ksub">EC2 instance running</div>
            </div>
            <div class="kcard">
                <div class="khdr"><span class="kico">🐳</span><span class="kbdg kw">Hub</span></div>
                <div class="klbl">Docker Image</div>
                <div class="kval" style="color:#6a1b9a;font-size:13px">raeel/flask-app</div>
                <div class="ksub" style="color:#0ea5e9">:latest pushed ✓</div>
            </div>
        </div>

        <div class="ccol">
            <div class="slbl">// System Health Monitor</div>
            <div class="hgrid">
                <div class="hcard" onclick="openModal('cpu')">
                    <div class="hico">⚙️</div><div class="hn">CPU</div>
                    <div class="hv" id="cpu-val" style="color:{h['cpu_color']}">{h['cpu']}%</div>
                    <div class="hbdg" id="cpu-badge" style="{h['cpu_badge']}">{h['cpu_label']}</div>
                    <div class="hbar"><div class="hbf" id="cpu-bar" style="background:{h['cpu_color']};width:{h['cpu']}%"></div></div>
                </div>
                <div class="hcard" onclick="openModal('mem')">
                    <div class="hico">🧠</div><div class="hn">MEM</div>
                    <div class="hv" id="mem-val" style="color:{h['mem_color']}">{h['mem']}%</div>
                    <div class="hbdg" id="mem-badge" style="{h['mem_badge']}">{h['mem_label']}</div>
                    <div class="hbar"><div class="hbf" id="mem-bar" style="background:{h['mem_color']};width:{h['mem']}%"></div></div>
                </div>
                <div class="hcard" onclick="openModal('disk')">
                    <div class="hico">💾</div><div class="hn">DISK</div>
                    <div class="hv" id="disk-val" style="color:{h['disk_color']}">{h['disk']}%</div>
                    <div class="hbdg" id="disk-badge" style="{h['disk_badge']}">{h['disk_label']}</div>
                    <div class="hbar"><div class="hbf" id="disk-bar" style="background:{h['disk_color']};width:{h['disk']}%"></div></div>
                </div>
                <div class="hcard" onclick="openModal('net')">
                    <div class="hico">🌐</div><div class="hn">NET</div>
                    <div class="hv" id="net-val" style="color:#1e6fff;font-size:14px">{h['net_sent']}MB</div>
                    <div class="hbdg" style="color:#1565c0;border-color:#90caf9;background:#e3f2fd">TX/RX</div>
                    <div class="hbar"><div class="hbf" style="background:#1e6fff;width:55%"></div></div>
                </div>
                <div class="hcard" onclick="openModal('flask')">
                    <div class="hico">🌶️</div><div class="hn">FLASK</div>
                    <div class="hv" style="color:#2e7d32;font-size:12px">SERVING</div>
                    <div class="hbdg" style="color:#2e7d32;border-color:#a5d6a7;background:#e8f5e9">ONLINE</div>
                    <div class="hbar"><div class="hbf" style="background:#43a047;width:100%"></div></div>
                </div>
            </div>

            <div class="bigcard">
                <div class="depgrid">
                    <div><div class="slbl">Docker Image</div><div class="depval" style="color:#6a1b9a">raeel/flask-app<span style="color:#0ea5e9">:latest</span></div></div>
                    <div><div class="slbl">Deployed via</div><div class="depval" style="color:#1e6fff;font-size:11px">appleboy/ssh-action<span style="color:#94a3b8">@v1.0.3</span></div></div>
                    <div><div class="slbl">Platform</div><div class="depval" style="color:#1a2332">AWS EC2 ☁️</div></div>
                    <div><div class="slbl">Container</div><div class="depval" style="color:#2e7d32">Running ✓</div></div>
                </div>
                <div class="slbl" style="margin-bottom:5px">Recent Deploy Log</div>
                <div class="logrow"><span class="logtime" id="lt1">--:--:--</span><span class="logicon" style="color:#2e7d32">✓</span><span class="logmsg">docker-compose up -d — 2 containers started</span></div>
                <div class="logrow"><span class="logtime" id="lt2">--:--:--</span><span class="logicon" style="color:#2e7d32">✓</span><span class="logmsg">docker pull raeel/flask-app:latest</span></div>
                <div class="logrow"><span class="logtime" id="lt3">--:--:--</span><span class="logicon" style="color:#2e7d32">✓</span><span class="logmsg">git pull origin main — Already up to date</span></div>
                <div class="logrow"><span class="logtime" id="lt4">--:--:--</span><span class="logicon" style="color:#1e6fff">→</span><span class="logmsg">SSH connected to EC2 via appleboy/ssh-action</span></div>
                <div class="logrow"><span class="logtime" id="lt5">--:--:--</span><span class="logicon" style="color:#2e7d32">✓</span><span class="logmsg">Image pushed to Docker Hub successfully</span></div>
                <div class="logrow"><span class="logtime" id="lt6">--:--:--</span><span class="logicon" style="color:#2e7d32">✓</span><span class="logmsg">Docker build — raeel/flask-app:latest</span></div>
            </div>
        </div>

        <div class="rcol">
            <div class="scard">
                <div class="slbl">Tech Stack</div>
                <div class="spills">
                    <span class="pill">🐍 Python 3.11</span>
                    <span class="pill">🌶️ Flask</span>
                    <span class="pill">🗄️ Redis</span>
                    <span class="pill">🐳 Docker</span>
                    <span class="pill">📦 Compose</span>
                    <span class="pill hi">⚡ GitHub Actions</span>
                    <span class="pill hi">🐙 GitHub</span>
                    <span class="pill">🏔️ Docker Hub</span>
                    <span class="pill">☁️ AWS EC2</span>
                    <span class="pill">📊 Psutil</span>
                    <span class="pill">🔑 ssh-action</span>
                </div>
            </div>
            <div class="acard">
                <div class="slbl">Quick Actions</div>
                <div class="abtn"><span class="adot" style="background:#43a047"></span>Trigger Deploy</div>
                <div class="abtn"><span class="adot" style="background:#1e6fff"></span>View GH Actions Log</div>
                <div class="abtn"><span class="adot" style="background:#0ea5e9"></span>Rollback to Previous</div>
            </div>
            <div class="wcard">
                <div class="slbl" style="margin-bottom:6px">Workflow · .github/workflows</div>
                <div class="wline"><span class="wkey">on:</span><span class="wval">push → main</span></div>
                <div class="wline"><span class="wkey">job 1:</span><span class="wsec">build-and-push</span></div>
                <div class="wline" style="padding-left:10px"><span class="wkey">›</span><span class="wval">docker/login-action</span></div>
                <div class="wline" style="padding-left:10px"><span class="wkey">›</span><span class="wval">build-push-action</span></div>
                <div class="wline"><span class="wkey">job 2:</span><span class="wsec">deploy</span></div>
                <div class="wline" style="padding-left:10px"><span class="wkey">›</span><span class="wval">needs: build-and-push</span></div>
                <div class="wline" style="padding-left:10px"><span class="wkey">›</span><span class="wval">appleboy/ssh-action</span></div>
                <div class="wline" style="padding-left:10px"><span class="wkey">›</span><span class="wval">host: <span class="wsec">EC2_HOST</span></span></div>
                <div class="wline" style="padding-left:10px"><span class="wkey">›</span><span class="wval">key: <span class="wsec">EC2_SSH_KEY</span></span></div>
            </div>
        </div>

    </div>

    <div class="footer">
        <div class="fst"><span class="fdot"></span>All systems operational · Auto-refresh every 5s</div>
        <div>Flask · Redis · Docker · GitHub Actions · AWS EC2</div>
        <div id="footer-date">—</div>
    </div>

</div>

<script>
    function updateClock() {{
        const n = new Date();
        document.getElementById('clock').textContent = n.toTimeString().split(' ')[0];
        document.getElementById('footer-date').textContent = n.toLocaleDateString('en-US', {{weekday:'short',month:'short',day:'numeric',year:'numeric'}});
        const t = n.toTimeString().split(' ')[0];
        ['lt1','lt2','lt3','lt4','lt5','lt6'].forEach((id, i) => {{
            const d = new Date(n - i * 20000);
            document.getElementById(id).textContent = d.toTimeString().split(' ')[0];
        }});
    }}
    updateClock(); setInterval(updateClock, 1000);

    let deploySecs = 0;
    setInterval(() => {{
        deploySecs++;
        const t = document.getElementById('deploy-timer');
        if (t) t.textContent = deploySecs < 60 ? deploySecs+'s' : Math.floor(deploySecs/60)+'m '+(deploySecs%60)+'s';
        if (deploySecs === 12) {{
            document.getElementById('stage-deploy').className = 'stg done';
            document.getElementById('stage-deploy-dot').className = 'sd done';
            document.getElementById('stage-deploy-dot').textContent = '✓';
            document.getElementById('stage-health').className = 'stg running';
            document.getElementById('stage-health-dot').className = 'sd running';
            document.getElementById('stage-health-dot').textContent = '⟳';
        }}
        if (deploySecs === 18) {{
            document.getElementById('stage-health').className = 'stg done';
            document.getElementById('stage-health-dot').className = 'sd done';
            document.getElementById('stage-health-dot').textContent = '✓';
            document.getElementById('health-timer').textContent = '6s';
        }}
    }}, 1000);

    let hData = {{
        cpu:{h['cpu']}, cpu_color:'{h['cpu_color']}', cpu_label:'{h['cpu_label']}', cpu_badge:'{h['cpu_badge']}',
        cpu_count:{h['cpu_count']}, cpu_freq:{h['cpu_freq']},
        mem:{h['mem']}, mem_color:'{h['mem_color']}', mem_label:'{h['mem_label']}', mem_badge:'{h['mem_badge']}',
        mem_total:{h['mem_total']}, mem_used_gb:{h['mem_used_gb']}, mem_available:{h['mem_available']},
        disk:{h['disk']}, disk_color:'{h['disk_color']}', disk_label:'{h['disk_label']}', disk_badge:'{h['disk_badge']}',
        disk_total:{h['disk_total']}, disk_used_gb:{h['disk_used_gb']}, disk_free:{h['disk_free']},
        net_sent:{h['net_sent']}, net_recv:{h['net_recv']},
        uptime:'{h['uptime']}', uptime_secs:{h['uptime_secs']}
    }};

    const modalDefs = {{
        cpu:   d => ({{ icon:'⚙️', title:'CPU PROCESSOR',    sub:`${{d.cpu_count}} Cores · ${{d.cpu_freq}} MHz`, val:`${{d.cpu}}%`,       color:d.cpu_color,  pct:d.cpu,  details:[['Load',`${{d.cpu}}%`],['Cores',d.cpu_count],['Freq',`${{d.cpu_freq}} MHz`],['Status',d.cpu_label]] }}),
        mem:   d => ({{ icon:'🧠', title:'MEMORY (RAM)',      sub:`${{d.mem_total}} GB Total`,                   val:`${{d.mem}}%`,       color:d.mem_color,  pct:d.mem,  details:[['Used',`${{d.mem_used_gb}} GB`],['Total',`${{d.mem_total}} GB`],['Free',`${{d.mem_available}} MB`],['Status',d.mem_label]] }}),
        disk:  d => ({{ icon:'💾', title:'DISK STORAGE',      sub:`${{d.disk_total}} GB Total`,                  val:`${{d.disk}}%`,      color:d.disk_color, pct:d.disk, details:[['Used',`${{d.disk_used_gb}} GB`],['Total',`${{d.disk_total}} GB`],['Free',`${{d.disk_free}} GB`],['Status',d.disk_label]] }}),
        net:   d => ({{ icon:'🌐', title:'NETWORK I/O',       sub:'Bytes Transferred',                           val:`${{d.net_sent}}MB`, color:'#1e6fff',    pct:55,     details:[['Sent',`${{d.net_sent}} MB`],['Recv',`${{d.net_recv}} MB`],['Uptime',d.uptime],['Secs',d.uptime_secs]] }}),
        flask: d => ({{ icon:'🌶️', title:'FLASK APPLICATION', sub:'Web Server · Port 5000',                      val:'SERVING',           color:'#2e7d32',    pct:100,    details:[['Status','ONLINE'],['Framework','Flask'],['Python','3.11'],['Port','5000']] }}),
    }};

    let activeModal = null;

    function openModal(type) {{
        activeModal = type;
        const d = modalDefs[type](hData);
        document.getElementById('mIcon').textContent = d.icon;
        document.getElementById('mTitle').textContent = d.title;
        document.getElementById('mSub').textContent = d.sub;
        document.getElementById('mVal').textContent = d.val;
        document.getElementById('mVal').style.color = d.color;
        document.getElementById('mPct').textContent = typeof d.pct === 'number' ? d.pct+'%' : d.pct;
        const bar = document.getElementById('mBarFill');
        bar.style.background = d.color; bar.style.width = '0%';
        setTimeout(() => bar.style.width = d.pct+'%', 80);
        document.getElementById('mDetails').innerHTML = d.details.map(([l,v]) =>
            `<div class="modal-detail"><div class="modal-dl">${{l}}</div><div class="modal-dv">${{v}}</div></div>`
        ).join('');
        document.getElementById('modalOverlay').classList.add('active');
    }}

    function closeModal() {{
        document.getElementById('modalOverlay').classList.remove('active');
        activeModal = null;
    }}

    document.getElementById('modalOverlay').addEventListener('click', e => {{
        if (e.target === document.getElementById('modalOverlay')) closeModal();
    }});

    let countdown = 5;
    function refreshHealth() {{
        fetch('/health').then(r => r.json()).then(d => {{
            hData = d;
            [['cpu',d.cpu,d.cpu_color,d.cpu_label,d.cpu_badge],
             ['mem',d.mem,d.mem_color,d.mem_label,d.mem_badge],
             ['disk',d.disk,d.disk_color,d.disk_label,d.disk_badge]].forEach(([id,val,color,lbl,bdg]) => {{
                const v = document.getElementById(id+'-val');
                const b = document.getElementById(id+'-badge');
                const r = document.getElementById(id+'-bar');
                if (v) {{ v.textContent = val+'%'; v.style.color = color; }}
                if (b) {{ b.textContent = lbl; b.style.cssText = bdg; }}
                if (r) {{ r.style.background = color; r.style.width = val+'%'; }}
            }});
            const nu = document.getElementById('net-val'); if (nu) nu.textContent = d.net_sent+'MB';
            const hu = document.getElementById('heroUptime'); if (hu) hu.textContent = d.uptime;
            if (activeModal) openModal(activeModal);
            countdown = 5;
        }}).catch(() => {{}});
    }}
    setInterval(() => {{ if (--countdown <= 0) refreshHealth(); }}, 1000);
</script>
</body>
</html>"""

    return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
