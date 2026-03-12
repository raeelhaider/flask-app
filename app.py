from flask import Flask
import redis
import os
 
app = Flask(__name__)
 
redis_host = os.environ.get("REDIS_HOST", "localhost")
redis_port = int(os.environ.get("REDIS_PORT", 6379))
r = redis.Redis(host=redis_host, port=redis_port)
 
@app.route("/")
def hello():
    count = r.incr("visits")
 
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Flask App</title>
        <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
 
            :root {{
                --bg: #0f0c1a;
                --accent: #ff6b6b;
            }}
 
            body {{
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                background-color: var(--bg);
                font-family: 'DM Sans', sans-serif;
                transition: background-color 0.6s ease;
                cursor: pointer;
                overflow: hidden;
            }}
 
            /* Animated background blobs */
            .blob {{
                position: fixed;
                border-radius: 50%;
                filter: blur(80px);
                opacity: 0.35;
                animation: float 8s ease-in-out infinite;
                pointer-events: none;
                transition: background 0.6s ease;
            }}
            .blob-1 {{
                width: 500px; height: 500px;
                top: -100px; left: -100px;
                background: var(--blob1, #ff6b6b);
                animation-delay: 0s;
            }}
            .blob-2 {{
                width: 400px; height: 400px;
                bottom: -80px; right: -80px;
                background: var(--blob2, #845ef7);
                animation-delay: 3s;
            }}
            .blob-3 {{
                width: 300px; height: 300px;
                top: 50%; left: 50%;
                transform: translate(-50%, -50%);
                background: var(--blob3, #339af0);
                animation-delay: 1.5s;
            }}
 
            @keyframes float {{
                0%, 100% {{ transform: translateY(0px) scale(1); }}
                50% {{ transform: translateY(-30px) scale(1.05); }}
            }}
 
            .card {{
                position: relative;
                z-index: 10;
                text-align: center;
                padding: 60px 80px;
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 32px;
                max-width: 620px;
                width: 90%;
                box-shadow: 0 30px 80px rgba(0,0,0,0.4);
                animation: slideUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
            }}
 
            @keyframes slideUp {{
                from {{ opacity: 0; transform: translateY(40px); }}
                to   {{ opacity: 1; transform: translateY(0); }}
            }}
 
            .greeting {{
                font-family: 'Syne', sans-serif;
                font-size: 2.8rem;
                font-weight: 800;
                color: #ffffff;
                line-height: 1.1;
                margin-bottom: 12px;
                letter-spacing: -1px;
            }}
 
            .greeting span {{
                background: linear-gradient(135deg, var(--accent, #ff6b6b), #ffd43b);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                transition: background 0.6s ease;
            }}
 
            .subtitle {{
                font-size: 1rem;
                color: rgba(255,255,255,0.5);
                margin-bottom: 48px;
                font-weight: 300;
                letter-spacing: 0.5px;
            }}
 
            .counter-wrapper {{
                display: inline-flex;
                flex-direction: column;
                align-items: center;
                gap: 6px;
                background: rgba(255,255,255,0.07);
                border: 1px solid rgba(255,255,255,0.12);
                border-radius: 20px;
                padding: 24px 48px;
                margin-bottom: 40px;
            }}
 
            .counter-label {{
                font-size: 0.75rem;
                text-transform: uppercase;
                letter-spacing: 3px;
                color: rgba(255,255,255,0.4);
                font-weight: 500;
            }}
 
            .counter-number {{
                font-family: 'Syne', sans-serif;
                font-size: 4.5rem;
                font-weight: 800;
                color: #ffffff;
                line-height: 1;
                animation: popIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
            }}
 
            @keyframes popIn {{
                from {{ transform: scale(0.6); opacity: 0; }}
                to   {{ transform: scale(1);   opacity: 1; }}
            }}
 
            .hint {{
                font-size: 0.85rem;
                color: rgba(255,255,255,0.3);
                letter-spacing: 0.5px;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
            }}
 
            .hint::before, .hint::after {{
                content: '';
                display: block;
                width: 30px;
                height: 1px;
                background: rgba(255,255,255,0.15);
            }}
 
            .click-ripple {{
                position: fixed;
                border-radius: 50%;
                pointer-events: none;
                animation: ripple 0.6s ease-out forwards;
                z-index: 5;
            }}
 
            @keyframes ripple {{
                from {{ width: 0; height: 0; opacity: 0.4; transform: translate(-50%, -50%); }}
                to   {{ width: 300px; height: 300px; opacity: 0; transform: translate(-50%, -50%); }}
            }}
        </style>
    </head>
    <body>
        <div class="blob blob-1"></div>
        <div class="blob blob-2"></div>
        <div class="blob blob-3"></div>
 
        <div class="card">
            <div class="greeting">
                Welcome back, <br><span>DevOps Explorer!</span>
            </div>
            <p class="subtitle">Cloud &amp; DevOps Flask App — Running Live</p>
 
            <div class="counter-wrapper">
                <div class="counter-label">Total Visits</div>
                <div class="counter-number">{count}</div>
            </div>
 
            <p class="hint">Click anywhere to change the vibe</p>
        </div>
 
        <script>
            const palettes = [
                {{ bg: '#0f0c1a', blob1: '#ff6b6b', blob2: '#845ef7', blob3: '#339af0', accent: '#ff6b6b' }},
                {{ bg: '#0a1628', blob1: '#339af0', blob2: '#20c997', blob3: '#74c0fc', accent: '#339af0' }},
                {{ bg: '#1a0a0a', blob1: '#ff922b', blob2: '#f03e3e', blob3: '#ffd43b', accent: '#ff922b' }},
                {{ bg: '#0a1a0f', blob1: '#40c057', blob2: '#20c997', blob3: '#94d82d', accent: '#40c057' }},
                {{ bg: '#12091a', blob1: '#cc5de8', blob2: '#f06595', blob3: '#845ef7', accent: '#cc5de8' }},
                {{ bg: '#1a1508', blob1: '#ffd43b', blob2: '#ff922b', blob3: '#f06595', accent: '#ffd43b' }},
            ];
 
            let current = 0;
            const root = document.documentElement;
 
            function applyPalette(p) {{
                root.style.setProperty('--bg', p.bg);
                root.style.setProperty('--blob1', p.blob1);
                root.style.setProperty('--blob2', p.blob2);
                root.style.setProperty('--blob3', p.blob3);
                root.style.setProperty('--accent', p.accent);
                document.body.style.backgroundColor = p.bg;
            }}
 
            // Apply initial palette
            applyPalette(palettes[0]);
 
            document.body.addEventListener('click', function(e) {{
                current = (current + 1) % palettes.length;
                applyPalette(palettes[current]);
 
                // Ripple effect
                const ripple = document.createElement('div');
                ripple.className = 'click-ripple';
                ripple.style.left = e.clientX + 'px';
                ripple.style.top = e.clientY + 'px';
                ripple.style.background = palettes[current].accent;
                document.body.appendChild(ripple);
                setTimeout(() => ripple.remove(), 600);
            }});
        </script>
    </body>
    </html>
    """
    return html
 
 
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
