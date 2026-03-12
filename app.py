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
    if count == 1:
        return "🚀 First contact established."
    elif count == 5:
        return "⚡ 5 visits — System warming up."
    elif count == 10:
        return "🔥 10 visits — You're on a streak!"
    elif count == 25:
        return "💥 25 visits — Impressive persistence."
    elif count == 50:
        return "🌌 50 visits — You live here now."
    elif count == 100:
        return "👾 100 visits — LEGENDARY STATUS."
    elif count % 10 == 0:
        return f"🛸 {count} visits — The matrix notices you."
    else:
        return ""
 
def get_system_health():
    cpu = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    uptime_seconds = int(time.time() - psutil.boot_time())
    hours = uptime_seconds // 3600
    minutes = (uptime_seconds % 3600) // 60
 
    try:
        r.ping()
        redis_status = "ONLINE"
        redis_color = "#40c057"
    except:
        redis_status = "OFFLINE"
        redis_color = "#ff4444"
 
    def health_color(val):
        if val < 60:   return "#40c057"
        elif val < 85: return "#ffd43b"
        else:          return "#ff4444"
 
    def health_label(val):
        if val < 60:   return "OK"
        elif val < 85: return "WARN"
        else:          return "CRIT"
 
    return {
        "cpu":        round(cpu, 1),
        "cpu_color":  health_color(cpu),
        "cpu_label":  health_label(cpu),
        "mem_used":   round(mem.percent, 1),
        "mem_color":  health_color(mem.percent),
        "mem_label":  health_label(mem.percent),
        "mem_total":  round(mem.total / (1024**3), 1),
        "disk_used":  round(disk.percent, 1),
        "disk_color": health_color(disk.percent),
        "disk_label": health_label(disk.percent),
        "disk_free":  round(disk.free / (1024**3), 1),
        "uptime":     f"{hours}h {minutes}m",
        "redis_status": redis_status,
        "redis_color":  redis_color,
    }
 
@app.route("/")
def hello():
    count = r.incr("visits")
    milestone = get_milestone_message(count)
    h = get_system_health()
 
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DevOps Terminal</title>
        <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&family=Exo+2:wght@300;400;600&display=swap" rel="stylesheet">
        <style>
            *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
 
            :root {{
                --glow: #00ffe7;
                --glow2: #0077ff;
                --bg: #020b14;
                --grid: rgba(0,255,231,0.04);
                --panel: rgba(0,255,231,0.03);
                --border: rgba(0,255,231,0.15);
                --text: #c8f0ff;
                --dim: rgba(200,240,255,0.35);
            }}
 
            body {{
                min-height: 100vh;
                background-color: var(--bg);
                font-family: 'Exo 2', sans-serif;
                color: var(--text);
                cursor: crosshair;
                overflow-y: auto;
                overflow-x: hidden;
                transition: background-color 0.8s ease;
            }}
 
            .grid-bg {{
                position: fixed; inset: 0;
                background-image:
                    linear-gradient(var(--grid) 1px, transparent 1px),
                    linear-gradient(90deg, var(--grid) 1px, transparent 1px);
                background-size: 40px 40px;
                pointer-events: none; z-index: 0;
            }}
            .scanlines {{
                position: fixed; inset: 0;
                background: repeating-linear-gradient(
                    0deg, transparent, transparent 2px,
                    rgba(0,0,0,0.08) 2px, rgba(0,0,0,0.08) 4px
                );
                pointer-events: none; z-index: 1;
                animation: scanMove 8s linear infinite;
            }}
            @keyframes scanMove {{
                from {{ background-position: 0 0; }}
                to   {{ background-position: 0 100vh; }}
            }}
 
            .corner {{
                position: fixed; width: 50px; height: 50px;
                pointer-events: none; z-index: 2; opacity: 0.6;
            }}
            .corner-tl {{ top:16px; left:16px; border-top:2px solid var(--glow); border-left:2px solid var(--glow); }}
            .corner-tr {{ top:16px; right:16px; border-top:2px solid var(--glow); border-right:2px solid var(--glow); }}
            .corner-bl {{ bottom:16px; left:16px; border-bottom:2px solid var(--glow); border-left:2px solid var(--glow); }}
            .corner-br {{ bottom:16px; right:16px; border-bottom:2px solid var(--glow); border-right:2px solid var(--glow); }}
 
            .hud {{
                position: relative; z-index: 10;
                min-height: 100vh;
                display: grid;
                grid-template-rows: auto auto auto auto auto auto;
                padding: 24px 28px;
                gap: 16px;
            }}
 
            /* Top Bar */
            .topbar {{
                display: flex; justify-content: space-between; align-items: center;
                border-bottom: 1px solid var(--border); padding-bottom: 12px;
                animation: fadeDown 0.6s ease forwards;
            }}
            .sys-label {{
                font-family: 'Orbitron', monospace;
                font-size: 0.6rem; letter-spacing: 3px;
                color: var(--glow); text-transform: uppercase;
                text-shadow: 0 0 10px var(--glow);
            }}
            .datetime {{
                font-family: 'Share Tech Mono', monospace;
                font-size: 0.75rem; color: var(--dim);
                text-align: right; line-height: 1.5;
            }}
            #clock {{
                font-size: 0.95rem; color: var(--glow);
                text-shadow: 0 0 8px var(--glow);
            }}
 
            /* Greeting */
            .center {{
                display: flex; flex-direction: column;
                align-items: center; gap: 16px; text-align: center;
            }}
            .greeting-sub {{
                font-family: 'Share Tech Mono', monospace;
                font-size: 0.65rem; letter-spacing: 5px;
                color: var(--glow); text-shadow: 0 0 10px var(--glow);
                margin-bottom: 6px;
                opacity: 0; animation: fadeUp 0.6s 0.2s ease forwards;
            }}
            .greeting-main {{
                font-family: 'Orbitron', monospace;
                font-size: clamp(1.6rem, 4vw, 2.8rem);
                font-weight: 900; line-height: 1.1; letter-spacing: -1px;
                background: linear-gradient(135deg, #ffffff 0%, var(--glow) 50%, var(--glow2) 100%);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                background-clip: text;
                filter: drop-shadow(0 0 16px rgba(0,255,231,0.3));
                opacity: 0; animation: fadeUp 0.7s 0.4s cubic-bezier(0.16,1,0.3,1) forwards;
            }}
            .typewriter {{
                display: inline-block; overflow: hidden; white-space: nowrap;
                border-right: 2px solid var(--glow);
                animation: typing 2s steps(22,end) 1s forwards, blink 0.75s step-end infinite;
                max-width: 0;
            }}
            @keyframes typing {{ from {{ max-width:0; }} to {{ max-width:100%; }} }}
            @keyframes blink  {{ 50% {{ border-color:transparent; }} }}
 
            /* Visit + Status */
            .stats-panel {{
                display: grid; grid-template-columns: 1fr 1fr;
                gap: 10px; width: 100%; max-width: 460px;
                opacity: 0; animation: fadeUp 0.7s 0.8s ease forwards;
            }}
            .stat-box {{
                background: var(--panel); border: 1px solid var(--border);
                border-radius: 10px; padding: 14px 14px;
                position: relative; overflow: hidden;
                transition: border-color 0.3s, box-shadow 0.3s;
            }}
            .stat-box:hover {{
                border-color: var(--glow);
                box-shadow: 0 0 16px rgba(0,255,231,0.1);
            }}
            .stat-box::before {{
                content: ''; position: absolute;
                top:0; left:0; right:0; height:2px;
                background: linear-gradient(90deg,transparent,var(--glow),transparent);
                opacity: 0.6;
            }}
            .stat-label {{
                font-family: 'Share Tech Mono', monospace;
                font-size: 0.55rem; letter-spacing: 3px;
                color: var(--dim); text-transform: uppercase; margin-bottom: 6px;
            }}
            .stat-value {{
                font-family: 'Orbitron', monospace;
                font-size: 1.9rem; font-weight: 700;
                color: #fff; text-shadow: 0 0 12px var(--glow); line-height: 1;
            }}
            .stat-value.visits {{
                font-size: 2.4rem;
                background: linear-gradient(135deg, var(--glow), var(--glow2));
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                background-clip: text;
                animation: popIn 0.5s cubic-bezier(0.34,1.56,0.64,1);
            }}
            @keyframes popIn {{
                from {{ transform:scale(0.5); opacity:0; }}
                to   {{ transform:scale(1); opacity:1; }}
            }}
            .stat-unit {{
                font-family: 'Share Tech Mono', monospace;
                font-size: 0.55rem; color: var(--dim); margin-top: 3px; letter-spacing: 2px;
            }}
 
            /* Milestone */
            .milestone {{
                font-family: 'Share Tech Mono', monospace; font-size: 0.8rem;
                color: #ffd43b; text-shadow: 0 0 10px rgba(255,212,59,0.6);
                background: rgba(255,212,59,0.05); border: 1px solid rgba(255,212,59,0.2);
                border-radius: 8px; padding: 8px 20px; letter-spacing: 1px;
                opacity: 0;
                animation: fadeUp 0.5s 1.2s ease forwards, glowPulse 2s 1.7s ease-in-out infinite;
            }}
            @keyframes glowPulse {{
                0%,100% {{ box-shadow:0 0 6px rgba(255,212,59,0.2); }}
                50%      {{ box-shadow:0 0 16px rgba(255,212,59,0.5); }}
            }}
 
            /* ── COMPACT HEALTH GRID ── */
            .health-section {{
                width: 100%;
                opacity: 0;
                animation: fadeUp 0.7s 1.1s ease forwards;
            }}
            .health-title {{
                font-family: 'Share Tech Mono', monospace;
                font-size: 0.55rem; letter-spacing: 4px;
                color: var(--dim); text-transform: uppercase;
                margin-bottom: 10px; text-align: center;
            }}
            .health-grid {{
                display: grid;
                grid-template-columns: repeat(6, 1fr);
                gap: 8px;
            }}
            .health-card {{
                background: var(--panel);
                border: 1px solid var(--border);
                border-radius: 8px;
                padding: 10px 8px;
                position: relative;
                overflow: hidden;
                transition: border-color 0.3s, box-shadow 0.3s;
                text-align: center;
            }}
            .health-card:hover {{
                border-color: var(--glow);
                box-shadow: 0 0 12px rgba(0,255,231,0.08);
            }}
            .health-card::before {{
                content: ''; position: absolute;
                top:0; left:0; right:0; height:2px;
                background: linear-gradient(90deg,transparent,var(--glow),transparent);
                opacity: 0.5;
            }}
            .health-icon {{
                font-size: 0.95rem;
                margin-bottom: 4px;
            }}
            .health-card-name {{
                font-family: 'Share Tech Mono', monospace;
                font-size: 0.5rem; letter-spacing: 2px;
                color: var(--dim); text-transform: uppercase;
                margin-bottom: 5px;
            }}
            .health-value-sm {{
                font-family: 'Orbitron', monospace;
                font-size: 0.95rem; font-weight: 700;
                line-height: 1; margin-bottom: 5px;
            }}
            .health-badge-sm {{
                font-family: 'Share Tech Mono', monospace;
                font-size: 0.45rem; letter-spacing: 1.5px;
                padding: 2px 5px; border-radius: 999px;
                border: 1px solid; text-transform: uppercase;
                display: inline-block; margin-bottom: 6px;
            }}
            .progress-track {{
                width: 100%; height: 3px;
                background: rgba(255,255,255,0.06);
                border-radius: 999px; overflow: hidden;
            }}
            .progress-fill {{
                height: 100%; border-radius: 999px;
                animation: barGrow 1.2s cubic-bezier(0.16,1,0.3,1) forwards;
            }}
            @keyframes barGrow {{ from {{ width:0 !important; }} }}
 
            /* Stack */
            .stack-section {{
                width: 100%;
                border-top: 1px solid var(--border);
                border-bottom: 1px solid var(--border);
                padding: 12px 0;
                opacity: 0;
                animation: fadeUp 0.6s 1.4s ease forwards;
            }}
            .stack-label {{
                font-family: 'Share Tech Mono', monospace;
                font-size: 0.55rem; letter-spacing: 4px;
                color: var(--dim); text-align: center;
                margin-bottom: 10px; text-transform: uppercase;
            }}
            .stack-grid {{
                display: flex; flex-wrap: wrap;
                justify-content: center; gap: 7px;
                max-width: 860px; margin: 0 auto;
            }}
            .stack-badge {{
                display: inline-flex; align-items: center; gap: 6px;
                padding: 4px 12px; border: 1px solid var(--border);
                border-radius: 999px; background: var(--panel);
                font-family: 'Share Tech Mono', monospace;
                font-size: 0.62rem; letter-spacing: 1.5px;
                color: var(--text); text-transform: uppercase;
                transition: border-color 0.3s, box-shadow 0.3s, color 0.3s;
            }}
            .stack-badge:hover {{
                border-color: var(--glow); color: var(--glow);
                box-shadow: 0 0 10px rgba(0,255,231,0.12);
                text-shadow: 0 0 6px var(--glow);
            }}
 
            /* Bottom */
            .bottombar {{
                display: flex; justify-content: space-between; align-items: center;
                border-top: 1px solid var(--border); padding-top: 12px;
                font-family: 'Share Tech Mono', monospace;
                font-size: 0.6rem; color: var(--dim); letter-spacing: 2px;
                opacity: 0; animation: fadeUp 0.6s 1s ease forwards;
            }}
            .status-dot {{
                display: inline-block; width: 5px; height: 5px;
                border-radius: 50%; background: #40c057;
                box-shadow: 0 0 6px #40c057; margin-right: 6px;
                animation: pulse 2s ease-in-out infinite;
            }}
            @keyframes pulse {{ 0%,100% {{ opacity:1; }} 50% {{ opacity:0.3; }} }}
 
            .ripple {{
                position: fixed; border-radius: 50%;
                border: 1px solid var(--glow);
                pointer-events: none; z-index: 5;
                animation: rippleOut 0.8s ease-out forwards;
                transform: translate(-50%,-50%);
            }}
            @keyframes rippleOut {{
                from {{ width:0; height:0; opacity:0.6; }}
                to   {{ width:400px; height:400px; opacity:0; }}
            }}
 
            @keyframes fadeUp {{
                from {{ opacity:0; transform:translateY(16px); }}
                to   {{ opacity:1; transform:translateY(0); }}
            }}
            @keyframes fadeDown {{
                from {{ opacity:0; transform:translateY(-16px); }}
                to   {{ opacity:1; transform:translateY(0); }}
            }}
        </style>
    </head>
    <body>
        <div class="grid-bg"></div>
        <div class="scanlines"></div>
        <div class="corner corner-tl"></div>
        <div class="corner corner-tr"></div>
        <div class="corner corner-bl"></div>
        <div class="corner corner-br"></div>
 
        <div class="hud">
 
            <!-- Top Bar -->
            <div class="topbar">
                <div>
                    <div class="sys-label">// DevOps Terminal v2.0</div>
                    <div class="sys-label" style="margin-top:3px;opacity:0.5;">Powered by Cloud &amp; DevOps Stack</div>
                </div>
                <div class="datetime">
                    <div id="date"></div>
                    <div id="clock">00:00:00</div>
                </div>
            </div>
 
            <!-- Greeting -->
            <div class="center">
                <div>
                    <div class="greeting-sub">// SYSTEM ONLINE — IDENTITY CONFIRMED</div>
                    <div class="greeting-main">
                        <span class="typewriter">Hello, DevOps Explorer</span>
                    </div>
                </div>
                <div class="stats-panel">
                    <div class="stat-box">
                        <div class="stat-label">// Total Visits</div>
                        <div class="stat-value visits">{count}</div>
                        <div class="stat-unit">CONNECTIONS</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">// App Status</div>
                        <div class="stat-value" style="font-size:1rem;padding-top:4px;color:#40c057;-webkit-text-fill-color:#40c057;text-shadow:0 0 10px #40c057;">ONLINE</div>
                        <div class="stat-unit">RUNNING</div>
                    </div>
                </div>
                {"<div class='milestone'>" + milestone + "</div>" if milestone else ""}
            </div>
 
            <!-- Compact Health Grid -->
            <div class="health-section">
                <div class="health-title">// System Health</div>
                <div class="health-grid">
 
                    <div class="health-card">
                        <div class="health-icon">⚙️</div>
                        <div class="health-card-name">CPU</div>
                        <div class="health-value-sm" style="color:{h['cpu_color']};text-shadow:0 0 8px {h['cpu_color']};">{h['cpu']}%</div>
                        <div class="health-badge-sm" style="color:{h['cpu_color']};border-color:{h['cpu_color']};">{h['cpu_label']}</div>
                        <div class="progress-track"><div class="progress-fill" style="width:{h['cpu']}%;background:{h['cpu_color']};"></div></div>
                    </div>
 
                    <div class="health-card">
                        <div class="health-icon">🧠</div>
                        <div class="health-card-name">Memory</div>
                        <div class="health-value-sm" style="color:{h['mem_color']};text-shadow:0 0 8px {h['mem_color']};">{h['mem_used']}%</div>
                        <div class="health-badge-sm" style="color:{h['mem_color']};border-color:{h['mem_color']};">{h['mem_label']}</div>
                        <div class="progress-track"><div class="progress-fill" style="width:{h['mem_used']}%;background:{h['mem_color']};"></div></div>
                    </div>
 
                    <div class="health-card">
                        <div class="health-icon">💾</div>
                        <div class="health-card-name">Disk</div>
                        <div class="health-value-sm" style="color:{h['disk_color']};text-shadow:0 0 8px {h['disk_color']};">{h['disk_used']}%</div>
                        <div class="health-badge-sm" style="color:{h['disk_color']};border-color:{h['disk_color']};">{h['disk_label']}</div>
                        <div class="progress-track"><div class="progress-fill" style="width:{h['disk_used']}%;background:{h['disk_color']};"></div></div>
                    </div>
 
                    <div class="health-card">
                        <div class="health-icon">🗄️</div>
                        <div class="health-card-name">Redis</div>
                        <div class="health-value-sm" style="color:{h['redis_color']};text-shadow:0 0 8px {h['redis_color']};font-size:0.7rem;padding-top:2px;">{h['redis_status']}</div>
                        <div class="health-badge-sm" style="color:{h['redis_color']};border-color:{h['redis_color']};">{h['redis_status']}</div>
                        <div class="progress-track"><div class="progress-fill" style="width:{'100' if h['redis_status']=='ONLINE' else '0'}%;background:{h['redis_color']};"></div></div>
                    </div>
 
                    <div class="health-card">
                        <div class="health-icon">⏱️</div>
                        <div class="health-card-name">Uptime</div>
                        <div class="health-value-sm" style="color:#40c057;text-shadow:0 0 8px #40c057;font-size:0.75rem;padding-top:2px;">{h['uptime']}</div>
                        <div class="health-badge-sm" style="color:#40c057;border-color:#40c057;">STABLE</div>
                        <div class="progress-track"><div class="progress-fill" style="width:100%;background:#40c057;"></div></div>
                    </div>
 
                    <div class="health-card">
                        <div class="health-icon">🌶️</div>
                        <div class="health-card-name">Flask</div>
                        <div class="health-value-sm" style="color:#40c057;text-shadow:0 0 8px #40c057;font-size:0.7rem;padding-top:2px;">SERVING</div>
                        <div class="health-badge-sm" style="color:#40c057;border-color:#40c057;">ONLINE</div>
                        <div class="progress-track"><div class="progress-fill" style="width:100%;background:#40c057;"></div></div>
                    </div>
 
                </div>
            </div>
 
            <!-- Stack -->
            <div class="stack-section">
                <div class="stack-label">// Built With</div>
                <div class="stack-grid">
                    <span class="stack-badge">🐍 Python 3.11</span>
                    <span class="stack-badge">🌶️ Flask</span>
                    <span class="stack-badge">🗄️ Redis</span>
                    <span class="stack-badge">🐳 Docker</span>
                    <span class="stack-badge">📦 Docker Compose</span>
                    <span class="stack-badge">🔧 Jenkins CI/CD</span>
                    <span class="stack-badge">🐙 GitHub</span>
                    <span class="stack-badge">🏔️ Docker Hub</span>
                    <span class="stack-badge">☁️ Cloud Deployed</span>
                    <span class="stack-badge">⚡ DevOps Pipeline</span>
                </div>
            </div>
 
            <!-- Bottom -->
            <div class="bottombar">
                <div><span class="status-dot"></span>ALL SYSTEMS NOMINAL</div>
                <div>[ CLICK ANYWHERE TO SHIFT REALITY ]</div>
                <div>UPLINK · SECURED</div>
            </div>
 
        </div>
 
        <script>
            function updateClock() {{
                const now = new Date();
                document.getElementById('clock').textContent = now.toTimeString().split(' ')[0];
                document.getElementById('date').textContent = now.toLocaleDateString('en-US', {{
                    weekday:'long', year:'numeric', month:'long', day:'numeric'
                }});
            }}
            updateClock();
            setInterval(updateClock, 1000);
 
            const palettes = [
                {{ bg:'#020b14', glow:'#00ffe7', glow2:'#0077ff', grid:'rgba(0,255,231,0.04)', border:'rgba(0,255,231,0.15)' }},
                {{ bg:'#0d0014', glow:'#bf5fff', glow2:'#ff2d78', grid:'rgba(191,95,255,0.04)', border:'rgba(191,95,255,0.15)' }},
                {{ bg:'#001408', glow:'#00ff88', glow2:'#00ccff', grid:'rgba(0,255,136,0.04)', border:'rgba(0,255,136,0.15)' }},
                {{ bg:'#14060a', glow:'#ff2d78', glow2:'#ff8c00', grid:'rgba(255,45,120,0.04)', border:'rgba(255,45,120,0.15)' }},
                {{ bg:'#110e00', glow:'#ffd700', glow2:'#ff6600', grid:'rgba(255,215,0,0.04)', border:'rgba(255,215,0,0.15)' }},
            ];
 
            let current = 0;
            const root = document.documentElement;
 
            document.body.addEventListener('click', function(e) {{
                current = (current + 1) % palettes.length;
                const p = palettes[current];
                root.style.setProperty('--bg', p.bg);
                root.style.setProperty('--glow', p.glow);
                root.style.setProperty('--glow2', p.glow2);
                root.style.setProperty('--grid', p.grid);
                root.style.setProperty('--border', p.border);
                document.body.style.backgroundColor = p.bg;
 
                const ripple = document.createElement('div');
                ripple.className = 'ripple';
                ripple.style.left = e.clientX + 'px';
                ripple.style.top = e.clientY + 'px';
                ripple.style.borderColor = p.glow;
                document.body.appendChild(ripple);
                setTimeout(() => ripple.remove(), 800);
            }});
        </script>
    </body>
    </html>
    """
    return html
 
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
 
