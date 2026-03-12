from flask import Flask
import redis
import os
 
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
 
@app.route("/")
def hello():
    count = r.incr("visits")
    milestone = get_milestone_message(count)
 
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
                --grid: rgba(0, 255, 231, 0.04);
                --panel: rgba(0, 255, 231, 0.03);
                --border: rgba(0, 255, 231, 0.15);
                --text: #c8f0ff;
                --dim: rgba(200, 240, 255, 0.35);
            }}
 
            body {{
                min-height: 100vh;
                background-color: var(--bg);
                font-family: 'Exo 2', sans-serif;
                color: var(--text);
                cursor: crosshair;
                overflow: hidden;
                transition: background-color 0.8s ease;
            }}
 
            .grid-bg {{
                position: fixed;
                inset: 0;
                background-image:
                    linear-gradient(var(--grid) 1px, transparent 1px),
                    linear-gradient(90deg, var(--grid) 1px, transparent 1px);
                background-size: 40px 40px;
                pointer-events: none;
                z-index: 0;
            }}
 
            .scanlines {{
                position: fixed;
                inset: 0;
                background: repeating-linear-gradient(
                    0deg,
                    transparent,
                    transparent 2px,
                    rgba(0,0,0,0.08) 2px,
                    rgba(0,0,0,0.08) 4px
                );
                pointer-events: none;
                z-index: 1;
                animation: scanMove 8s linear infinite;
            }}
            @keyframes scanMove {{
                from {{ background-position: 0 0; }}
                to   {{ background-position: 0 100vh; }}
            }}
 
            .corner {{
                position: fixed;
                width: 60px; height: 60px;
                pointer-events: none;
                z-index: 2;
                opacity: 0.6;
            }}
            .corner-tl {{ top: 20px; left: 20px; border-top: 2px solid var(--glow); border-left: 2px solid var(--glow); }}
            .corner-tr {{ top: 20px; right: 20px; border-top: 2px solid var(--glow); border-right: 2px solid var(--glow); }}
            .corner-bl {{ bottom: 20px; left: 20px; border-bottom: 2px solid var(--glow); border-left: 2px solid var(--glow); }}
            .corner-br {{ bottom: 20px; right: 20px; border-bottom: 2px solid var(--glow); border-right: 2px solid var(--glow); }}
 
            .hud {{
                position: relative;
                z-index: 10;
                min-height: 100vh;
                display: grid;
                grid-template-rows: auto 1fr auto;
                padding: 40px;
                gap: 20px;
            }}
 
            .topbar {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 1px solid var(--border);
                padding-bottom: 16px;
                animation: fadeDown 0.6s ease forwards;
            }}
 
            .sys-label {{
                font-family: 'Orbitron', monospace;
                font-size: 0.65rem;
                letter-spacing: 4px;
                color: var(--glow);
                text-transform: uppercase;
                text-shadow: 0 0 10px var(--glow);
            }}
 
            .datetime {{
                font-family: 'Share Tech Mono', monospace;
                font-size: 0.85rem;
                color: var(--dim);
                text-align: right;
                line-height: 1.6;
            }}
 
            #clock {{
                font-size: 1.1rem;
                color: var(--glow);
                text-shadow: 0 0 8px var(--glow);
            }}
 
            .center {{
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                gap: 32px;
                text-align: center;
            }}
 
            .greeting-sub {{
                font-family: 'Share Tech Mono', monospace;
                font-size: 0.75rem;
                letter-spacing: 6px;
                color: var(--glow);
                text-shadow: 0 0 12px var(--glow);
                margin-bottom: 12px;
                opacity: 0;
                animation: fadeUp 0.6s 0.2s ease forwards;
            }}
 
            .greeting-main {{
                font-family: 'Orbitron', monospace;
                font-size: clamp(2rem, 5vw, 3.5rem);
                font-weight: 900;
                line-height: 1.1;
                letter-spacing: -1px;
                background: linear-gradient(135deg, #ffffff 0%, var(--glow) 50%, var(--glow2) 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                filter: drop-shadow(0 0 20px rgba(0,255,231,0.3));
                opacity: 0;
                animation: fadeUp 0.7s 0.4s cubic-bezier(0.16,1,0.3,1) forwards;
            }}
 
            .typewriter {{
                display: inline-block;
                overflow: hidden;
                white-space: nowrap;
                border-right: 3px solid var(--glow);
                animation: typing 2s steps(22, end) 1s forwards, blink 0.75s step-end infinite;
                max-width: 0;
            }}
            @keyframes typing {{
                from {{ max-width: 0; }}
                to   {{ max-width: 100%; }}
            }}
            @keyframes blink {{
                50% {{ border-color: transparent; }}
            }}
 
            .stats-panel {{
                display: grid;
                grid-template-columns: 1fr 1fr 1fr;
                gap: 16px;
                width: 100%;
                max-width: 700px;
                opacity: 0;
                animation: fadeUp 0.7s 0.8s ease forwards;
            }}
 
            .stat-box {{
                background: var(--panel);
                border: 1px solid var(--border);
                border-radius: 12px;
                padding: 20px 16px;
                position: relative;
                overflow: hidden;
                transition: border-color 0.3s, box-shadow 0.3s;
            }}
            .stat-box:hover {{
                border-color: var(--glow);
                box-shadow: 0 0 20px rgba(0,255,231,0.1), inset 0 0 20px rgba(0,255,231,0.03);
            }}
            .stat-box::before {{
                content: '';
                position: absolute;
                top: 0; left: 0; right: 0;
                height: 2px;
                background: linear-gradient(90deg, transparent, var(--glow), transparent);
                opacity: 0.6;
            }}
 
            .stat-label {{
                font-family: 'Share Tech Mono', monospace;
                font-size: 0.6rem;
                letter-spacing: 3px;
                color: var(--dim);
                text-transform: uppercase;
                margin-bottom: 8px;
            }}
 
            .stat-value {{
                font-family: 'Orbitron', monospace;
                font-size: 2.2rem;
                font-weight: 700;
                color: #fff;
                text-shadow: 0 0 15px var(--glow);
                line-height: 1;
            }}
 
            .stat-value.visits {{
                font-size: 3rem;
                background: linear-gradient(135deg, var(--glow), var(--glow2));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                animation: popIn 0.5s cubic-bezier(0.34,1.56,0.64,1);
            }}
 
            @keyframes popIn {{
                from {{ transform: scale(0.5); opacity: 0; }}
                to   {{ transform: scale(1); opacity: 1; }}
            }}
 
            .stat-unit {{
                font-family: 'Share Tech Mono', monospace;
                font-size: 0.65rem;
                color: var(--dim);
                margin-top: 4px;
                letter-spacing: 2px;
            }}
 
            .milestone {{
                font-family: 'Share Tech Mono', monospace;
                font-size: 0.9rem;
                color: #ffd43b;
                text-shadow: 0 0 12px rgba(255,212,59,0.6);
                background: rgba(255,212,59,0.05);
                border: 1px solid rgba(255,212,59,0.2);
                border-radius: 8px;
                padding: 10px 24px;
                letter-spacing: 1px;
                opacity: 0;
                animation: fadeUp 0.5s 1.2s ease forwards, glowPulse 2s 1.7s ease-in-out infinite;
            }}
            @keyframes glowPulse {{
                0%, 100% {{ box-shadow: 0 0 8px rgba(255,212,59,0.2); }}
                50%        {{ box-shadow: 0 0 20px rgba(255,212,59,0.5); }}
            }}
 
            .bottombar {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-top: 1px solid var(--border);
                padding-top: 16px;
                font-family: 'Share Tech Mono', monospace;
                font-size: 0.7rem;
                color: var(--dim);
                letter-spacing: 2px;
                opacity: 0;
                animation: fadeUp 0.6s 1s ease forwards;
            }}
 
            .status-dot {{
                display: inline-block;
                width: 6px; height: 6px;
                border-radius: 50%;
                background: #40c057;
                box-shadow: 0 0 8px #40c057;
                margin-right: 8px;
                animation: pulse 2s ease-in-out infinite;
            }}
            @keyframes pulse {{
                0%, 100% {{ opacity: 1; }}
                50%        {{ opacity: 0.3; }}
            }}
 
            .ripple {{
                position: fixed;
                border-radius: 50%;
                border: 1px solid var(--glow);
                pointer-events: none;
                z-index: 5;
                animation: rippleOut 0.8s ease-out forwards;
                transform: translate(-50%, -50%);
            }}
            @keyframes rippleOut {{
                from {{ width: 0; height: 0; opacity: 0.6; }}
                to   {{ width: 400px; height: 400px; opacity: 0; }}
            }}
 
            @keyframes fadeUp {{
                from {{ opacity: 0; transform: translateY(20px); }}
                to   {{ opacity: 1; transform: translateY(0); }}
            }}
            @keyframes fadeDown {{
                from {{ opacity: 0; transform: translateY(-20px); }}
                to   {{ opacity: 1; transform: translateY(0); }}
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
            <div class="topbar">
                <div>
                    <div class="sys-label">// DevOps Terminal v2.0</div>
                    <div class="sys-label" style="margin-top:4px; opacity:0.5;">Flask · Redis · Docker · Jenkins</div>
                </div>
                <div class="datetime">
                    <div id="date"></div>
                    <div id="clock">00:00:00</div>
                </div>
            </div>
 
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
                        <div class="stat-label">// Redis Host</div>
                        <div class="stat-value" style="font-size:1.1rem; padding-top:6px;">{redis_host}</div>
                        <div class="stat-unit">PORT {redis_port}</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">// App Status</div>
                        <div class="stat-value" style="font-size:1rem; padding-top:6px; color:#40c057; -webkit-text-fill-color:#40c057; text-shadow: 0 0 12px #40c057;">ONLINE</div>
                        <div class="stat-unit">FLASK · 5000</div>
                    </div>
                </div>
 
                {"<div class='milestone'>" + milestone + "</div>" if milestone else ""}
            </div>
 
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
                    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
                }});
            }}
            updateClock();
            setInterval(updateClock, 1000);
 
            const palettes = [
                {{ bg: '#020b14', glow: '#00ffe7', glow2: '#0077ff', grid: 'rgba(0,255,231,0.04)', border: 'rgba(0,255,231,0.15)' }},
                {{ bg: '#0d0014', glow: '#bf5fff', glow2: '#ff2d78', grid: 'rgba(191,95,255,0.04)', border: 'rgba(191,95,255,0.15)' }},
                {{ bg: '#001408', glow: '#00ff88', glow2: '#00ccff', grid: 'rgba(0,255,136,0.04)', border: 'rgba(0,255,136,0.15)' }},
                {{ bg: '#14060a', glow: '#ff2d78', glow2: '#ff8c00', grid: 'rgba(255,45,120,0.04)', border: 'rgba(255,45,120,0.15)' }},
                {{ bg: '#110e00', glow: '#ffd700', glow2: '#ff6600', grid: 'rgba(255,215,0,0.04)', border: 'rgba(255,215,0,0.15)' }},
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
