from flask import Flask
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
    secs = int(time.time() - psutil.boot_time())
    uptime = f"{secs//3600}h {(secs%3600)//60}m"
 
    try:
        r.ping()
        redis_status, redis_color = "ONLINE", "#c9a84c"
    except:
        redis_status, redis_color = "OFFLINE", "#e05c5c"
 
    def color(v):
        return "#c9a84c" if v < 60 else "#e8c56a" if v < 85 else "#e05c5c"
    def label(v):
        return "NOMINAL" if v < 60 else "MODERATE" if v < 85 else "CRITICAL"
 
    return dict(
        cpu=round(cpu,1),       cpu_color=color(cpu),       cpu_label=label(cpu),
        mem=round(mem.percent,1), mem_color=color(mem.percent), mem_label=label(mem.percent),
        mem_total=round(mem.total/(1024**3),1),
        disk=round(disk.percent,1), disk_color=color(disk.percent), disk_label=label(disk.percent),
        disk_free=round(disk.free/(1024**3),1),
        uptime=uptime,
        redis_status=redis_status, redis_color=redis_color,
    )
 
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
            background: var(--navy);
            font-family: 'Rajdhani', sans-serif;
            color: var(--text);
            cursor: default;
            transition: background 0.7s ease;
        }}
        .bg-layer {{
            position:fixed; inset:0; z-index:0;
            background:
                radial-gradient(ellipse 80% 50% at 50% 0%, rgba(201,168,76,0.07) 0%, transparent 70%),
                radial-gradient(ellipse 60% 40% at 100% 100%, rgba(7,40,80,0.6) 0%, transparent 60%),
                repeating-linear-gradient(0deg,   transparent, transparent 39px, rgba(201,168,76,0.03) 39px, rgba(201,168,76,0.03) 40px),
                repeating-linear-gradient(90deg,  transparent, transparent 39px, rgba(201,168,76,0.03) 39px, rgba(201,168,76,0.03) 40px);
            pointer-events:none;
        }}
        .corner {{ position:fixed; width:44px; height:44px; pointer-events:none; z-index:2; opacity:0.7; }}
        .corner-tl {{ top:18px; left:18px; border-top:1px solid var(--gold); border-left:1px solid var(--gold); }}
        .corner-tr {{ top:18px; right:18px; border-top:1px solid var(--gold); border-right:1px solid var(--gold); }}
        .corner-bl {{ bottom:18px; left:18px; border-bottom:1px solid var(--gold); border-left:1px solid var(--gold); }}
        .corner-br {{ bottom:18px; right:18px; border-bottom:1px solid var(--gold); border-right:1px solid var(--gold); }}
 
        .dashboard {{
            position:relative; z-index:10;
            height:100vh;
            display:grid;
            grid-template-rows: auto auto auto 1fr auto auto;
            padding:22px 32px 18px;
            gap:12px;
        }}
 
        /* HEADER */
        .header {{
            display:flex; justify-content:space-between; align-items:flex-start;
            border-bottom:1px solid var(--gold-border); padding-bottom:12px;
            animation:fadeDown 0.7s ease forwards;
        }}
        .project-eyebrow {{
            font-family:'Share Tech Mono',monospace;
            font-size:0.6rem; letter-spacing:5px; color:var(--gold); opacity:0.8;
            text-transform:uppercase;
        }}
        .project-title {{
            font-family:'Cinzel',serif;
            font-size:clamp(1.1rem,2.5vw,1.6rem); font-weight:700; letter-spacing:2px;
            background:linear-gradient(135deg,var(--gold-light) 0%,var(--gold) 60%,#a07830 100%);
            -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
            filter:drop-shadow(0 0 12px rgba(201,168,76,0.35));
            margin:3px 0;
        }}
        .project-desc {{
            font-size:0.72rem; font-weight:300; letter-spacing:1px; color:var(--dim);
        }}
        .header-right {{
            text-align:right; font-family:'Share Tech Mono',monospace;
            font-size:0.7rem; color:var(--dim); line-height:1.7;
        }}
        #clock {{ font-size:1rem; color:var(--gold); text-shadow:0 0 10px rgba(201,168,76,0.5); }}
 
        /* DIVIDER */
        .gold-rule {{
            display:flex; align-items:center; gap:10px;
            opacity:0; animation:fadeUp 0.5s 0.3s ease forwards;
        }}
        .gold-rule::before, .gold-rule::after {{
            content:''; flex:1; height:1px;
            background:linear-gradient(90deg,transparent,var(--gold-border),transparent);
        }}
        .gold-diamond {{ width:5px; height:5px; background:var(--gold); transform:rotate(45deg); box-shadow:0 0 6px var(--gold); }}
 
        /* GREETING */
        .greeting-row {{
            display:flex; align-items:center; justify-content:space-between; gap:20px;
            opacity:0; animation:fadeUp 0.6s 0.4s ease forwards;
        }}
        .greeting-sub {{
            font-family:'Share Tech Mono',monospace;
            font-size:0.6rem; letter-spacing:5px; color:var(--gold); opacity:0.7; margin-bottom:4px;
        }}
        .greeting-main {{
            font-family:'Cinzel',serif;
            font-size:clamp(1.3rem,3vw,2rem); font-weight:600; letter-spacing:1px;
            color:#fff; text-shadow:0 0 30px rgba(201,168,76,0.2);
        }}
        .typewriter {{
            display:inline-block; overflow:hidden; white-space:nowrap;
            border-right:2px solid var(--gold);
            animation:typing 2s steps(22,end) 0.8s forwards, blink 0.8s step-end infinite;
            max-width:0;
        }}
        @keyframes typing {{ from {{ max-width:0; }} to {{ max-width:100%; }} }}
        @keyframes blink   {{ 50% {{ border-color:transparent; }} }}
 
        .kpi-row {{ display:flex; gap:10px; flex-shrink:0; }}
        .kpi-pill {{
            background:var(--gold-dim); border:1px solid var(--gold-border);
            border-radius:8px; padding:8px 16px; text-align:center; min-width:90px;
            position:relative; overflow:hidden;
        }}
        .kpi-pill::before {{
            content:''; position:absolute; top:0; left:0; right:0; height:1px;
            background:linear-gradient(90deg,transparent,var(--gold),transparent);
        }}
        .kpi-label {{ font-family:'Share Tech Mono',monospace; font-size:0.5rem; letter-spacing:3px; color:var(--dim); text-transform:uppercase; margin-bottom:3px; }}
        .kpi-value {{
            font-family:'Cinzel',serif; font-size:1.4rem; font-weight:700;
            color:var(--gold); text-shadow:0 0 12px rgba(201,168,76,0.5);
            animation:popIn 0.5s cubic-bezier(0.34,1.56,0.64,1);
        }}
        .kpi-value.status {{
            font-size:0.75rem; color:#5dcc7a; text-shadow:0 0 8px rgba(93,204,122,0.5);
            padding-top:4px; font-family:'Share Tech Mono',monospace;
        }}
        @keyframes popIn {{ from {{ transform:scale(0.6); opacity:0; }} to {{ transform:scale(1); opacity:1; }} }}
 
        /* MILESTONE */
        .milestone {{
            font-family:'Share Tech Mono',monospace; font-size:0.72rem; letter-spacing:2px;
            color:var(--gold); background:var(--gold-dim); border:1px solid var(--gold-border);
            border-radius:6px; padding:6px 18px; text-align:center;
            opacity:0; animation:fadeUp 0.5s 1.2s ease forwards, goldPulse 2.5s 1.7s ease-in-out infinite;
        }}
        @keyframes goldPulse {{ 0%,100% {{ box-shadow:0 0 6px rgba(201,168,76,0.15); }} 50% {{ box-shadow:0 0 18px rgba(201,168,76,0.4); }} }}
 
        /* HEALTH */
        .health-section {{ display:flex; flex-direction:column; gap:7px; opacity:0; animation:fadeUp 0.6s 0.6s ease forwards; }}
        .section-label {{ font-family:'Share Tech Mono',monospace; font-size:0.55rem; letter-spacing:4px; color:var(--dim); text-transform:uppercase; text-align:center; }}
        .health-grid {{ display:grid; grid-template-columns:repeat(6,1fr); gap:8px; }}
        .hcard {{
            background:var(--navy-card); border:1px solid var(--gold-border);
            border-radius:8px; padding:9px 7px; text-align:center;
            position:relative; overflow:hidden;
            transition:border-color 0.3s, box-shadow 0.3s;
        }}
        .hcard:hover {{ border-color:var(--gold); box-shadow:0 0 14px rgba(201,168,76,0.12); }}
        .hcard::before {{
            content:''; position:absolute; top:0; left:0; right:0; height:1px;
            background:linear-gradient(90deg,transparent,var(--gold),transparent); opacity:0.5;
        }}
        .hcard-icon  {{ font-size:0.9rem; margin-bottom:3px; }}
        .hcard-name  {{ font-family:'Share Tech Mono',monospace; font-size:0.48rem; letter-spacing:2px; color:var(--dim); text-transform:uppercase; margin-bottom:4px; }}
        .hcard-val   {{ font-family:'Cinzel',serif; font-size:0.9rem; font-weight:600; line-height:1; margin-bottom:4px; }}
        .hcard-badge {{ font-family:'Share Tech Mono',monospace; font-size:0.42rem; letter-spacing:1.5px; padding:2px 5px; border-radius:999px; border:1px solid; display:inline-block; margin-bottom:5px; text-transform:uppercase; }}
        .progress-track {{ width:100%; height:2px; background:rgba(255,255,255,0.06); border-radius:999px; overflow:hidden; }}
        .progress-fill  {{ height:100%; border-radius:999px; animation:barGrow 1.2s cubic-bezier(0.16,1,0.3,1) forwards; }}
        @keyframes barGrow {{ from {{ width:0 !important; }} }}
 
        /* STACK */
        .stack-section {{ border-top:1px solid var(--gold-border); padding-top:10px; opacity:0; animation:fadeUp 0.6s 0.9s ease forwards; }}
        .stack-inner {{ display:flex; flex-wrap:wrap; justify-content:center; gap:6px; }}
        .stack-badge {{
            display:inline-flex; align-items:center; gap:5px;
            padding:3px 11px; border:1px solid var(--gold-border);
            border-radius:999px; background:var(--gold-dim);
            font-family:'Share Tech Mono',monospace; font-size:0.58rem; letter-spacing:1.5px;
            color:var(--gold-light); text-transform:uppercase; transition:all 0.25s;
        }}
        .stack-badge:hover {{ border-color:var(--gold); color:var(--gold); box-shadow:0 0 10px rgba(201,168,76,0.2); }}
 
        /* FOOTER */
        .footer {{
            display:flex; justify-content:space-between; align-items:center;
            border-top:1px solid var(--gold-border); padding-top:10px;
            font-family:'Share Tech Mono',monospace; font-size:0.58rem; color:var(--dim); letter-spacing:2px;
            opacity:0; animation:fadeUp 0.6s 1s ease forwards;
        }}
        .status-dot {{ display:inline-block; width:5px; height:5px; border-radius:50%; background:#5dcc7a; box-shadow:0 0 6px #5dcc7a; margin-right:6px; animation:pulse 2s ease-in-out infinite; }}
        @keyframes pulse {{ 0%,100% {{ opacity:1; }} 50% {{ opacity:0.3; }} }}
 
        .ripple {{ position:fixed; border-radius:50%; border:1px solid var(--gold); pointer-events:none; z-index:5; animation:rippleOut 0.9s ease-out forwards; transform:translate(-50%,-50%); }}
        @keyframes rippleOut {{ from {{ width:0; height:0; opacity:0.5; }} to {{ width:500px; height:500px; opacity:0; }} }}
 
        @keyframes fadeUp   {{ from {{ opacity:0; transform:translateY(14px); }} to {{ opacity:1; transform:translateY(0); }} }}
        @keyframes fadeDown {{ from {{ opacity:0; transform:translateY(-14px); }} to {{ opacity:1; transform:translateY(0); }} }}
    </style>
</head>
<body>
    <div class="bg-layer"></div>
    <div class="corner corner-tl"></div>
    <div class="corner corner-tr"></div>
    <div class="corner corner-bl"></div>
    <div class="corner corner-br"></div>
 
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
                    <div class="kpi-value">{count}</div>
                </div>
                <div class="kpi-pill">
                    <div class="kpi-label">Status</div>
                    <div class="kpi-value status">● ONLINE</div>
                </div>
            </div>
        </div>
 
        {"<div class='milestone'>" + milestone + "</div>" if milestone else "<div></div>"}
 
        <!-- HEALTH -->
        <div class="health-section">
            <div class="section-label">// System Health Monitor</div>
            <div class="health-grid">
                <div class="hcard">
                    <div class="hcard-icon">⚙️</div>
                    <div class="hcard-name">CPU</div>
                    <div class="hcard-val" style="color:{h['cpu_color']};text-shadow:0 0 8px {h['cpu_color']};">{h['cpu']}%</div>
                    <div class="hcard-badge" style="color:{h['cpu_color']};border-color:{h['cpu_color']};">{h['cpu_label']}</div>
                    <div class="progress-track"><div class="progress-fill" style="width:{h['cpu']}%;background:{h['cpu_color']};"></div></div>
                </div>
                <div class="hcard">
                    <div class="hcard-icon">🧠</div>
                    <div class="hcard-name">Memory</div>
                    <div class="hcard-val" style="color:{h['mem_color']};text-shadow:0 0 8px {h['mem_color']};">{h['mem']}%</div>
                    <div class="hcard-badge" style="color:{h['mem_color']};border-color:{h['mem_color']};">{h['mem_label']}</div>
                    <div class="progress-track"><div class="progress-fill" style="width:{h['mem']}%;background:{h['mem_color']};"></div></div>
                </div>
                <div class="hcard">
                    <div class="hcard-icon">💾</div>
                    <div class="hcard-name">Disk</div>
                    <div class="hcard-val" style="color:{h['disk_color']};text-shadow:0 0 8px {h['disk_color']};">{h['disk']}%</div>
                    <div class="hcard-badge" style="color:{h['disk_color']};border-color:{h['disk_color']};">{h['disk_label']}</div>
                    <div class="progress-track"><div class="progress-fill" style="width:{h['disk']}%;background:{h['disk_color']};"></div></div>
                </div>
                <div class="hcard">
                    <div class="hcard-icon">🗄️</div>
                    <div class="hcard-name">Redis</div>
                    <div class="hcard-val" style="color:{h['redis_color']};text-shadow:0 0 8px {h['redis_color']};font-size:0.65rem;padding-top:3px;">{h['redis_status']}</div>
                    <div class="hcard-badge" style="color:{h['redis_color']};border-color:{h['redis_color']};">{h['redis_status']}</div>
                    <div class="progress-track"><div class="progress-fill" style="width:{'100' if h['redis_status']=='ONLINE' else '0'}%;background:{h['redis_color']};"></div></div>
                </div>
                <div class="hcard">
                    <div class="hcard-icon">⏱️</div>
                    <div class="hcard-name">Uptime</div>
                    <div class="hcard-val" style="color:#c9a84c;text-shadow:0 0 8px #c9a84c;font-size:0.7rem;padding-top:3px;">{h['uptime']}</div>
                    <div class="hcard-badge" style="color:#c9a84c;border-color:#c9a84c;">STABLE</div>
                    <div class="progress-track"><div class="progress-fill" style="width:100%;background:#c9a84c;"></div></div>
                </div>
                <div class="hcard">
                    <div class="hcard-icon">🌶️</div>
                    <div class="hcard-name">Flask</div>
                    <div class="hcard-val" style="color:#5dcc7a;text-shadow:0 0 8px #5dcc7a;font-size:0.65rem;padding-top:3px;">SERVING</div>
                    <div class="hcard-badge" style="color:#5dcc7a;border-color:#5dcc7a;">ONLINE</div>
                    <div class="progress-track"><div class="progress-fill" style="width:100%;background:#5dcc7a;"></div></div>
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
            <div>[ CLICK TO SHIFT THEME ]</div>
        </div>
 
    </div>
 
    <script>
        function updateClock() {{
            const now = new Date();
            document.getElementById('clock').textContent = now.toTimeString().split(' ')[0];
            document.getElementById('date').textContent  = now.toLocaleDateString('en-US', {{
                weekday:'long', year:'numeric', month:'long', day:'numeric'
            }});
        }}
        updateClock();
        setInterval(updateClock, 1000);
 
        const palettes = [
            {{ bg:'#050d1a', dim:'rgba(201,168,76,0.18)', border:'rgba(201,168,76,0.28)' }},
            {{ bg:'#070d1f', dim:'rgba(120,160,255,0.07)', border:'rgba(120,160,255,0.28)' }},
            {{ bg:'#0a0d14', dim:'rgba(93,204,122,0.06)', border:'rgba(93,204,122,0.25)' }},
            {{ bg:'#150d0a', dim:'rgba(220,120,80,0.07)', border:'rgba(220,120,80,0.28)' }},
            {{ bg:'#0d0a18', dim:'rgba(180,120,220,0.07)', border:'rgba(180,120,220,0.25)' }},
        ];
 
        let current = 0;
        const root  = document.documentElement;
 
        document.body.addEventListener('click', function(e) {{
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
