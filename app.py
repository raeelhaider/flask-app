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
        if v < 40: return "#4aff9e"  # Neon green
        elif v < 70: return "#ffd966"  # Gold
        elif v < 85: return "#ff9966"  # Orange
        else: return "#ff6b6b"  # Red
        
    def label(v): 
        return "OPTIMAL" if v < 40 else "NOMINAL" if v < 70 else "ELEVATED" if v < 85 else "CRITICAL"

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

    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CI/CD Automation Project | Dark Edition</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Space+Grotesk:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        *, *::before, *::after { box-sizing:border-box; margin:0; padding:0; }
        
        :root {
            --bg-primary: #0a0c0f;
            --bg-secondary: #14181c;
            --bg-tertiary: #1e2429;
            --bg-card: rgba(20, 24, 28, 0.95);
            --bg-card-hover: rgba(30, 36, 41, 0.98);
            --accent-primary: #4aff9e;
            --accent-secondary: #00b8ff;
            --accent-tertiary: #bd6bff;
            --accent-glow: rgba(74, 255, 158, 0.4);
            --accent-gradient: linear-gradient(135deg, #4aff9e 0%, #00b8ff 50%, #bd6bff 100%);
            --text-primary: #ffffff;
            --text-secondary: #b0b8c5;
            --text-tertiary: #6e7a8a;
            --border-color: rgba(255, 255, 255, 0.08);
            --border-glow: rgba(74, 255, 158, 0.15);
            --success: #4aff9e;
            --warning: #ffd966;
            --danger: #ff6b6b;
            --info: #00b8ff;
            --shadow-sm: 0 4px 6px rgba(0, 0, 0, 0.3);
            --shadow-md: 0 8px 24px rgba(0, 0, 0, 0.4);
            --shadow-lg: 0 16px 32px rgba(0, 0, 0, 0.5);
            --shadow-glow: 0 0 30px var(--accent-glow);
        }
        
        html, body {
            height: 100%;
            overflow: hidden;
            background: var(--bg-primary);
        }
        
        body {
            font-family: 'Inter', sans-serif;
            color: var(--text-primary);
            cursor: default;
            position: relative;
        }
        
        /* Animated Background */
        .noise-bg {
            position: fixed;
            inset: 0;
            z-index: 0;
            opacity: 0.02;
            background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100"><filter id="noise"><feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="3" stitchTiles="stitch"/></filter><rect width="100" height="100" filter="url(%23noise)" opacity="0.8"/></svg>');
            pointer-events: none;
        }
        
        .gradient-bg {
            position: fixed;
            inset: 0;
            z-index: 0;
            background: 
                radial-gradient(circle at 20% 20%, rgba(74, 255, 158, 0.08) 0%, transparent 40%),
                radial-gradient(circle at 80% 30%, rgba(0, 184, 255, 0.08) 0%, transparent 40%),
                radial-gradient(circle at 40% 80%, rgba(189, 107, 255, 0.08) 0%, transparent 40%);
            pointer-events: none;
            animation: gradientShift 20s ease-in-out infinite;
        }
        
        @keyframes gradientShift {
            0%, 100% { opacity: 0.5; }
            50% { opacity: 1; }
        }
        
        .grid-overlay {
            position: fixed;
            inset: 0;
            z-index: 0;
            background-image: 
                linear-gradient(rgba(74, 255, 158, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(74, 255, 158, 0.03) 1px, transparent 1px);
            background-size: 60px 60px;
            pointer-events: none;
        }
        
        /* Floating Orbs */
        .orb-container {
            position: fixed;
            inset: 0;
            z-index: 0;
            overflow: hidden;
            pointer-events: none;
        }
        
        .orb {
            position: absolute;
            border-radius: 50%;
            filter: blur(60px);
            opacity: 0.15;
            animation: floatOrb 15s ease-in-out infinite;
        }
        
        .orb-1 {
            width: 400px;
            height: 400px;
            background: #4aff9e;
            top: -100px;
            left: -100px;
            animation-delay: 0s;
        }
        
        .orb-2 {
            width: 500px;
            height: 500px;
            background: #00b8ff;
            bottom: -150px;
            right: -150px;
            animation-delay: -5s;
        }
        
        .orb-3 {
            width: 300px;
            height: 300px;
            background: #bd6bff;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            animation-delay: -10s;
        }
        
        @keyframes floatOrb {
            0%, 100% { transform: translate(0, 0) scale(1); }
            33% { transform: translate(30px, -30px) scale(1.1); }
            66% { transform: translate(-30px, 30px) scale(0.9); }
        }
        
        /* Glowing Lines */
        .glow-line {
            position: fixed;
            z-index: 0;
            background: linear-gradient(90deg, transparent, var(--accent-primary), transparent);
            height: 1px;
            width: 100%;
            opacity: 0.1;
            pointer-events: none;
        }
        
        .glow-line-1 { top: 20%; animation: slideGlow 8s linear infinite; }
        .glow-line-2 { top: 50%; animation: slideGlow 12s linear infinite reverse; }
        .glow-line-3 { top: 80%; animation: slideGlow 10s linear infinite; }
        
        @keyframes slideGlow {
            from { transform: translateX(-100%); }
            to { transform: translateX(100%); }
        }
        
        /* Corner Accents */
        .corner {
            position: fixed;
            width: 100px;
            height: 100px;
            z-index: 2;
            pointer-events: none;
        }
        
        .corner-tl {
            top: 20px;
            left: 20px;
            border-top: 2px solid var(--accent-primary);
            border-left: 2px solid var(--accent-primary);
            box-shadow: -2px -2px 15px var(--accent-glow);
        }
        
        .corner-tr {
            top: 20px;
            right: 20px;
            border-top: 2px solid var(--accent-secondary);
            border-right: 2px solid var(--accent-secondary);
            box-shadow: 2px -2px 15px rgba(0, 184, 255, 0.4);
        }
        
        .corner-bl {
            bottom: 20px;
            left: 20px;
            border-bottom: 2px solid var(--accent-tertiary);
            border-left: 2px solid var(--accent-tertiary);
            box-shadow: -2px 2px 15px rgba(189, 107, 255, 0.4);
        }
        
        .corner-br {
            bottom: 20px;
            right: 20px;
            border-bottom: 2px solid var(--accent-primary);
            border-right: 2px solid var(--accent-primary);
            box-shadow: 2px 2px 15px var(--accent-glow);
        }
        
        /* Main Container */
        .dashboard {
            position: relative;
            z-index: 10;
            height: 100vh;
            display: flex;
            flex-direction: column;
            padding: 24px 32px;
            gap: 20px;
            backdrop-filter: blur(10px);
        }
        
        /* Top Bar */
        .topbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 20px;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            backdrop-filter: blur(20px);
            box-shadow: var(--shadow-sm);
            animation: slideDown 0.5s ease;
        }
        
        .topbar-left {
            display: flex;
            align-items: center;
            gap: 16px;
        }
        
        .logo {
            width: 40px;
            height: 40px;
            background: var(--accent-gradient);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 20px;
            color: var(--bg-primary);
            box-shadow: var(--shadow-glow);
        }
        
        .top-titles {
            display: flex;
            flex-direction: column;
        }
        
        .eyebrow {
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 3px;
            color: var(--text-tertiary);
        }
        
        .title {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 18px;
            font-weight: 600;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .topbar-right {
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
            color: var(--text-secondary);
            text-align: right;
        }
        
        #clock {
            color: var(--accent-primary);
            font-size: 16px;
            font-weight: 500;
            text-shadow: 0 0 20px var(--accent-glow);
        }
        
        /* Hero Section */
        .hero {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 40px 20px;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 32px;
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(20px);
            box-shadow: var(--shadow-md);
            animation: fadeIn 0.7s ease 0.2s both;
        }
        
        .hero-glow {
            position: absolute;
            inset: 0;
            background: radial-gradient(circle at 50% 50%, var(--accent-glow) 0%, transparent 70%);
            opacity: 0.1;
            pointer-events: none;
        }
        
        .hero-eyebrow {
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            letter-spacing: 4px;
            color: var(--accent-primary);
            margin-bottom: 16px;
            text-transform: uppercase;
            animation: slideUp 0.5s ease 0.4s both;
        }
        
        .hero-greeting {
            font-size: 14px;
            font-weight: 300;
            letter-spacing: 8px;
            color: var(--text-tertiary);
            text-transform: uppercase;
            margin-bottom: 8px;
            animation: slideUp 0.5s ease 0.5s both;
        }
        
        .hero-title {
            font-family: 'Space Grotesk', sans-serif;
            font-size: clamp(2.5rem, 6vw, 4.5rem);
            font-weight: 700;
            line-height: 1.1;
            margin-bottom: 20px;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            filter: drop-shadow(0 0 30px var(--accent-glow));
            animation: slideUp 0.6s ease 0.6s both;
        }
        
        .hero-typewriter {
            display: inline-block;
            border-right: 3px solid var(--accent-primary);
            white-space: nowrap;
            overflow: hidden;
            animation: typing 2.5s steps(30, end) 0.8s forwards, blink 0.8s step-end infinite;
            max-width: 0;
        }
        
        @keyframes typing {
            to { max-width: 100%; }
        }
        
        @keyframes blink {
            50% { border-color: transparent; }
        }
        
        .hero-desc {
            max-width: 600px;
            color: var(--text-secondary);
            line-height: 1.8;
            font-size: 15px;
            margin-bottom: 30px;
            animation: slideUp 0.5s ease 0.9s both;
        }
        
        /* KPI Row */
        .kpi-row {
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
            animation: slideUp 0.5s ease 1s both;
        }
        
        .kpi-card {
            background: var(--bg-tertiary);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 16px 24px;
            min-width: 140px;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .kpi-card:hover {
            transform: translateY(-4px);
            border-color: var(--accent-primary);
            box-shadow: var(--shadow-glow);
        }
        
        .kpi-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: var(--accent-gradient);
            transform: translateX(-100%);
            transition: transform 0.5s ease;
        }
        
        .kpi-card:hover::before {
            transform: translateX(100%);
        }
        
        .kpi-label {
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: var(--text-tertiary);
            margin-bottom: 8px;
        }
        
        .kpi-value {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 32px;
            font-weight: 600;
            color: var(--text-primary);
        }
        
        .kpi-value.online {
            font-size: 18px;
            color: var(--success);
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .pulse-dot {
            width: 10px;
            height: 10px;
            background: var(--success);
            border-radius: 50%;
            box-shadow: 0 0 20px var(--success);
            animation: pulse 2s ease infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(1.2); }
        }
        
        /* Milestone */
        .milestone {
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
            color: var(--accent-primary);
            background: rgba(74, 255, 158, 0.1);
            border: 1px solid rgba(74, 255, 158, 0.2);
            border-radius: 100px;
            padding: 8px 24px;
            display: inline-block;
            animation: glowPulse 2s ease infinite;
        }
        
        @keyframes glowPulse {
            0%, 100% { box-shadow: 0 0 20px rgba(74, 255, 158, 0.2); }
            50% { box-shadow: 0 0 40px rgba(74, 255, 158, 0.4); }
        }
        
        /* Health Section */
        .health-section {
            flex: 1;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 24px;
            padding: 24px;
            backdrop-filter: blur(20px);
            box-shadow: var(--shadow-md);
            animation: slideUp 0.5s ease 1.2s both;
        }
        
        .health-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .section-label {
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 3px;
            color: var(--text-tertiary);
        }
        
        .refresh-badge {
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            color: var(--text-secondary);
            display: flex;
            align-items: center;
            gap: 8px;
            background: var(--bg-tertiary);
            padding: 6px 12px;
            border-radius: 100px;
            border: 1px solid var(--border-color);
        }
        
        .refresh-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--accent-primary);
            animation: blink 1s ease infinite;
        }
        
        .health-grid {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 16px;
        }
        
        .health-card {
            background: var(--bg-tertiary);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 20px 16px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        
        .health-card:hover {
            transform: translateY(-6px) scale(1.02);
            border-color: var(--accent-primary);
            box-shadow: var(--shadow-glow);
        }
        
        .health-card::after {
            content: '';
            position: absolute;
            inset: 0;
            background: radial-gradient(circle at 50% 0%, var(--accent-glow), transparent 70%);
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        
        .health-card:hover::after {
            opacity: 0.2;
        }
        
        .card-icon {
            font-size: 28px;
            margin-bottom: 12px;
            filter: drop-shadow(0 0 10px currentColor);
        }
        
        .card-name {
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: var(--text-tertiary);
            margin-bottom: 8px;
        }
        
        .card-value {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 28px;
            font-weight: 600;
            margin-bottom: 8px;
            transition: color 0.3s ease;
        }
        
        .card-badge {
            font-family: 'JetBrains Mono', monospace;
            font-size: 10px;
            padding: 4px 12px;
            border-radius: 100px;
            display: inline-block;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            border: 1px solid;
        }
        
        .progress-bar {
            width: 100%;
            height: 6px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 3px;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            border-radius: 3px;
            transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        /* Stack Section */
        .stack-section {
            padding: 16px;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            backdrop-filter: blur(20px);
            animation: slideUp 0.5s ease 1.4s both;
        }
        
        .stack-grid {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 12px;
        }
        
        .stack-item {
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            padding: 8px 16px;
            background: var(--bg-tertiary);
            border: 1px solid var(--border-color);
            border-radius: 100px;
            color: var(--text-secondary);
            transition: all 0.3s ease;
            cursor: default;
        }
        
        .stack-item:hover {
            border-color: var(--accent-primary);
            color: var(--accent-primary);
            transform: translateY(-2px);
            box-shadow: var(--shadow-glow);
        }
        
        /* Footer */
        .footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 20px;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            color: var(--text-tertiary);
            animation: slideUp 0.5s ease 1.6s both;
        }
        
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            background: var(--success);
            border-radius: 50%;
            box-shadow: 0 0 20px var(--success);
            animation: pulse 2s ease infinite;
        }
        
        /* Modal */
        .modal-overlay {
            position: fixed;
            inset: 0;
            z-index: 1000;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(20px);
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s ease;
        }
        
        .modal-overlay.active {
            opacity: 1;
            pointer-events: all;
        }
        
        .modal {
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 32px;
            padding: 32px;
            max-width: 480px;
            width: 90%;
            transform: scale(0.9) translateY(20px);
            transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: var(--shadow-lg);
        }
        
        .modal-overlay.active .modal {
            transform: scale(1) translateY(0);
        }
        
        .modal-header {
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 24px;
        }
        
        .modal-icon {
            width: 60px;
            height: 60px;
            background: var(--accent-gradient);
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
        }
        
        .modal-title h3 {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 4px;
        }
        
        .modal-title p {
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            color: var(--text-tertiary);
        }
        
        .modal-close {
            position: absolute;
            top: 24px;
            right: 24px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            color: var(--text-tertiary);
            cursor: pointer;
            padding: 8px 12px;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        
        .modal-close:hover {
            border-color: var(--accent-primary);
            color: var(--accent-primary);
        }
        
        .modal-value {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 64px;
            font-weight: 700;
            text-align: center;
            margin: 24px 0;
        }
        
        .modal-bar {
            margin: 24px 0;
        }
        
        .modal-bar-label {
            display: flex;
            justify-content: space-between;
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            color: var(--text-tertiary);
            margin-bottom: 8px;
        }
        
        .modal-bar-track {
            height: 8px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 4px;
            overflow: hidden;
        }
        
        .modal-bar-fill {
            height: 100%;
            border-radius: 4px;
            transition: width 0.8s ease;
        }
        
        .modal-details {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
        }
        
        .modal-detail-item {
            background: var(--bg-tertiary);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 16px;
        }
        
        .modal-detail-label {
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            color: var(--text-tertiary);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }
        
        .modal-detail-value {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 18px;
            font-weight: 600;
        }
        
        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes slideDown {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes slideLeft {
            from { opacity: 0; transform: translateX(20px); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        @keyframes slideRight {
            from { opacity: 0; transform: translateX(-20px); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        /* Ripple Effect */
        .ripple {
            position: fixed;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(74, 255, 158, 0.3) 0%, transparent 70%);
            pointer-events: none;
            z-index: 9999;
            animation: rippleAnimation 1s ease-out forwards;
        }
        
        @keyframes rippleAnimation {
            from { width: 0; height: 0; opacity: 0.5; }
            to { width: 1000px; height: 1000px; opacity: 0; }
        }
    </style>
</head>
<body>
    <div class="noise-bg"></div>
    <div class="gradient-bg"></div>
    <div class="grid-overlay"></div>
    
    <div class="orb-container">
        <div class="orb orb-1"></div>
        <div class="orb orb-2"></div>
        <div class="orb orb-3"></div>
    </div>
    
    <div class="glow-line glow-line-1"></div>
    <div class="glow-line glow-line-2"></div>
    <div class="glow-line glow-line-3"></div>
    
    <div class="corner corner-tl"></div>
    <div class="corner corner-tr"></div>
    <div class="corner corner-bl"></div>
    <div class="corner corner-br"></div>

    <!-- Modal -->
    <div class="modal-overlay" id="modalOverlay">
        <div class="modal">
            <div class="modal-close" onclick="closeModal()">[ CLOSE ]</div>
            <div class="modal-header">
                <div class="modal-icon" id="modalIcon">⚙️</div>
                <div class="modal-title">
                    <h3 id="modalTitle">System Component</h3>
                    <p id="modalStatus">Status</p>
                </div>
            </div>
            <div class="modal-value" id="modalValue">0%</div>
            <div class="modal-bar">
                <div class="modal-bar-label">
                    <span>UTILIZATION</span>
                    <span id="modalPercent">0%</span>
                </div>
                <div class="modal-bar-track">
                    <div class="modal-bar-fill" id="modalBarFill"></div>
                </div>
            </div>
            <div class="modal-details" id="modalDetails"></div>
        </div>
    </div>

    <div class="dashboard">""" + f"""
        <!-- Top Bar -->
        <div class="topbar">
            <div class="topbar-left">
                <div class="logo">CI</div>
                <div class="top-titles">
                    <div class="eyebrow">// PRODUCTION DASHBOARD</div>
                    <div class="title">CI/CD AUTOMATION PROJECT</div>
                </div>
            </div>
            <div class="topbar-right">
                <div id="date"></div>
                <div id="clock">00:00:00</div>
            </div>
        </div>

        <!-- Hero -->
        <div class="hero">
            <div class="hero-glow"></div>
            <div class="hero-eyebrow">SYSTEM ONLINE · PRODUCTION ENVIRONMENT</div>
            <div class="hero-greeting">WELCOME BACK, OPERATOR</div>
            <div class="hero-title">
                <span class="hero-typewriter">CI/CD Automation Project</span>
            </div>
            <div class="hero-desc">
                A fully automated CI/CD pipeline
            </div>
            <div class="kpi-row">
                <div class="kpi-card">
                    <div class="kpi-label">Total Visits</div>
                    <div class="kpi-value" id="visitCount">{count}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">App Status</div>
                    <div class="kpi-value online">
                        <span class="pulse-dot"></span>
                        ONLINE
                    </div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Uptime</div>
                    <div class="kpi-value" style="font-size: 20px;" id="heroUptime">{h['uptime']}</div>
                </div>
            </div>
            {f'<div class="milestone">{milestone}</div>' if milestone else ''}
        </div>

        <!-- Health Section -->
        <div class="health-section">
            <div class="health-header">
                <div class="section-label">// SYSTEM HEALTH MONITOR</div>
                <div class="refresh-badge">
                    <span class="refresh-dot"></span>
                    <span id="refreshLabel">LIVE · 5s</span>
                </div>
            </div>
            <div class="health-grid">
                <div class="health-card" onclick="openModal('cpu')">
                    <div class="card-icon">⚙️</div>
                    <div class="card-name">CPU</div>
                    <div class="card-value" id="cpu-val" style="color: {h['cpu_color']};">{h['cpu']}%</div>
                    <div class="card-badge" id="cpu-badge" style="color: {h['cpu_color']}; border-color: {h['cpu_color']};">{h['cpu_label']}</div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="cpu-bar" style="width: {h['cpu']}%; background: {h['cpu_color']};"></div>
                    </div>
                </div>
                <div class="health-card" onclick="openModal('mem')">
                    <div class="card-icon">🧠</div>
                    <div class="card-name">MEMORY</div>
                    <div class="card-value" id="mem-val" style="color: {h['mem_color']};">{h['mem']}%</div>
                    <div class="card-badge" id="mem-badge" style="color: {h['mem_color']}; border-color: {h['mem_color']};">{h['mem_label']}</div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="mem-bar" style="width: {h['mem']}%; background: {h['mem_color']};"></div>
                    </div>
                </div>
                <div class="health-card" onclick="openModal('disk')">
                    <div class="card-icon">💾</div>
                    <div class="card-name">DISK</div>
                    <div class="card-value" id="disk-val" style="color: {h['disk_color']};">{h['disk']}%</div>
                    <div class="card-badge" id="disk-badge" style="color: {h['disk_color']}; border-color: {h['disk_color']};">{h['disk_label']}</div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="disk-bar" style="width: {h['disk']}%; background: {h['disk_color']};"></div>
                    </div>
                </div>
                <div class="health-card" onclick="openModal('uptime')">
                    <div class="card-icon">⏱️</div>
                    <div class="card-name">UPTIME</div>
                    <div class="card-value" style="font-size: 22px; color: #4aff9e;" id="uptime-val">{h['uptime']}</div>
                    <div class="card-badge" style="color: #4aff9e; border-color: #4aff9e;">STABLE</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 100%; background: #4aff9e;"></div>
                    </div>
                </div>
                <div class="health-card" onclick="openModal('flask')">
                    <div class="card-icon">🌶️</div>
                    <div class="card-name">FLASK</div>
                    <div class="card-value" style="font-size: 18px; color: #4aff9e;" id="flask-val">SERVING</div>
                    <div class="card-badge" style="color: #4aff9e; border-color: #4aff9e;">ONLINE</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 100%; background: #4aff9e;"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Stack Section -->
        <div class="stack-section">
            <div class="stack-grid">
                <span class="stack-item">🐍 Python 3.11</span>
                <span class="stack-item">🌶️ Flask</span>
                <span class="stack-item">🗄️ Redis</span>
                <span class="stack-item">🐳 Docker</span>
                <span class="stack-item">📦 Docker Compose</span>
                <span class="stack-item">🔧 Jenkins</span>
                <span class="stack-item">🐙 GitHub</span>
                <span class="stack-item">🏔️ Docker Hub</span>
                <span class="stack-item">☁️ AWS EC2</span>
                <span class="stack-item">📊 Psutil</span>
                <span class="stack-item">⚡ DevOps</span>
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            <div class="status-indicator">
                <span class="status-dot"></span>
                ALL SYSTEMS NOMINAL
            </div>
            <div>CLOUD & DEVOPS · PRODUCTION</div>
            <div>[ CLICK BACKGROUND TO SHIFT THEME ]</div>
        </div>
    </div>

    <script>
        function updateClock() {{
            const now = new Date();
            document.getElementById('clock').textContent = now.toTimeString().split(' ')[0];
            document.getElementById('date').textContent = now.toLocaleDateString('en-US', {{ 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
            }});
        }}
        updateClock();
        setInterval(updateClock, 1000);

        // System health data
        let healthData = {{
            cpu: {h['cpu']}, cpu_color: "{h['cpu_color']}", cpu_label: "{h['cpu_label']}",
            cpu_count: {h['cpu_count']}, cpu_freq: {h['cpu_freq']},
            mem: {h['mem']}, mem_color: "{h['mem_color']}", mem_label: "{h['mem_label']}",
            mem_total: {h['mem_total']}, mem_used_gb: {h['mem_used_gb']}, mem_available: {h['mem_available']},
            disk: {h['disk']}, disk_color: "{h['disk_color']}", disk_label: "{h['disk_label']}",
            disk_total: {h['disk_total']}, disk_used_gb: {h['disk_used_gb']}, disk_free: {h['disk_free']},
            net_sent: {h['net_sent']}, net_recv: {h['net_recv']},
            uptime: "{h['uptime']}", uptime_secs: {h['uptime_secs']}
        }};

        // Modal definitions
        const modalDefs = {{
            cpu: d => ({{
                icon: '⚙️',
                title: 'CPU PROCESSOR',
                status: `${{d.cpu_count}} Cores · ${{d.cpu_freq}} MHz`,
                value: `${{d.cpu}}%`,
                color: d.cpu_color,
                percent: d.cpu,
                details: [
                    ['Load', `${{d.cpu}}%`],
                    ['Cores', d.cpu_count],
                    ['Frequency', `${{d.cpu_freq}} MHz`],
                    ['Status', d.cpu_label]
                ]
            }}),
            mem: d => ({{
                icon: '🧠',
                title: 'MEMORY (RAM)',
                status: `${{d.mem_total}} GB Total`,
                value: `${{d.mem}}%`,
                color: d.mem_color,
                percent: d.mem,
                details: [
                    ['Used', `${{d.mem_used_gb}} GB`],
                    ['Total', `${{d.mem_total}} GB`],
                    ['Available', `${{d.mem_available}} MB`],
                    ['Status', d.mem_label]
                ]
            }}),
            disk: d => ({{
                icon: '💾',
                title: 'DISK STORAGE',
                status: `${{d.disk_total}} GB Total`,
                value: `${{d.disk}}%`,
                color: d.disk_color,
                percent: d.disk,
                details: [
                    ['Used', `${{d.disk_used_gb}} GB`],
                    ['Total', `${{d.disk_total}} GB`],
                    ['Free', `${{d.disk_free}} GB`],
                    ['Status', d.disk_label]
                ]
            }}),
            uptime: d => ({{
                icon: '⏱️',
                title: 'SYSTEM UPTIME',
                status: 'Server Running Time',
                value: d.uptime,
                color: '#4aff9e',
                percent: 100,
                details: [
                    ['Uptime', d.uptime],
                    ['Seconds', d.uptime_secs],
                    ['Net Sent', `${{d.net_sent}} MB`],
                    ['Net Recv', `${{d.net_recv}} MB`]
                ]
            }}),
            flask: d => ({{
                icon: '🌶️',
                title: 'FLASK APPLICATION',
                status: 'Web Server · Active',
                value: 'SERVING',
                color: '#4aff9e',
                percent: 100,
                details: [
                    ['Status', 'ONLINE'],
                    ['Framework', 'Flask'],
                    ['Python', '3.11'],
                    ['Port', '5000']
                ]
            }})
        }};

        let activeModal = null;

        function openModal(type) {{
            activeModal = type;
            const data = modalDefs[type](healthData);
            
            document.getElementById('modalIcon').textContent = data.icon;
            document.getElementById('modalTitle').textContent = data.title;
            document.getElementById('modalStatus').textContent = data.status;
            document.getElementById('modalValue').textContent = data.value;
            document.getElementById('modalValue').style.color = data.color;
            document.getElementById('modalPercent').textContent = typeof data.percent === 'number' ? data.percent + '%' : data.percent;
            
            const barFill = document.getElementById('modalBarFill');
            barFill.style.background = data.color;
            barFill.style.width = '0%';
            setTimeout(() => barFill.style.width = data.percent + '%', 100);
            
            const detailsHtml = data.details.map(([label, value]) => 
                `<div class="modal-detail-item">
                    <div class="modal-detail-label">${{label}}</div>
                    <div class="modal-detail-value">${{value}}</div>
                </div>`
            ).join('');
            document.getElementById('modalDetails').innerHTML = detailsHtml;
            
            document.getElementById('modalOverlay').classList.add('active');
        }}

        function closeModal() {{
            document.getElementById('modalOverlay').classList.remove('active');
            activeModal = null;
        }}

        // Auto-refresh health data
        let countdown = 5;
        function refreshHealth() {{
            const dot = document.querySelector('.refresh-dot');
            const label = document.getElementById('refreshLabel');
            
            dot.style.animation = 'none';
            dot.offsetHeight;
            dot.style.animation = 'blink 1s ease infinite';
            
            label.textContent = 'REFRESHING...';
            
            fetch('/health')
                .then(r => r.json())
                .then(data => {{
                    healthData = data;
                    
                    // Update UI
                    const updates = [
                        {{id: 'cpu', val: data.cpu + '%', color: data.cpu_color, badge: data.cpu_label, pct: data.cpu}},
                        {{id: 'mem', val: data.mem + '%', color: data.mem_color, badge: data.mem_label, pct: data.mem}},
                        {{id: 'disk', val: data.disk + '%', color: data.disk_color, badge: data.disk_label, pct: data.disk}},
                        {{id: 'uptime', val: data.uptime, color: '#4aff9e', badge: 'STABLE', pct: 100}},
                        {{id: 'flask', val: 'SERVING', color: '#4aff9e', badge: 'ONLINE', pct: 100}}
                    ];
                    
                    updates.forEach(u => {{
                        const valEl = document.getElementById(u.id + '-val');
                        const badgeEl = document.getElementById(u.id + '-badge');
                        const barEl = document.getElementById(u.id + '-bar');
                        
                        if (valEl) {{
                            valEl.textContent = u.val;
                            valEl.style.color = u.color;
                        }}
                        if (badgeEl) {{
                            badgeEl.textContent = u.badge;
                            badgeEl.style.color = u.color;
                            badgeEl.style.borderColor = u.color;
                        }}
                        if (barEl) {{
                            barEl.style.background = u.color;
                            barEl.style.width = u.pct + '%';
                        }}
                    }});
                    
                    document.getElementById('heroUptime').textContent = data.uptime;
                    
                    if (activeModal) openModal(activeModal);
                    
                    countdown = 5;
                    label.textContent = 'LIVE · 5s';
                }})
                .catch(() => {{
                    label.textContent = 'RETRY...';
                }});
        }}

        setInterval(() => {{
            countdown--;
            if (countdown > 0) {{
                document.getElementById('refreshLabel').textContent = `LIVE · ${{countdown}}s`;
            }} else {{
                refreshHealth();
            }}
        }}, 1000);

        // Theme shift on background click
        const themes = [
            {{ bg: '#0a0c0f', accent: '#4aff9e' }},
            {{ bg: '#0f0a14', accent: '#bd6bff' }},
            {{ bg: '#0a1414', accent: '#00b8ff' }},
            {{ bg: '#140a0a', accent: '#ff6b6b' }}
        ];
        let themeIndex = 0;
        
        document.querySelector('.dashboard').addEventListener('click', (e) => {{
            if (e.target.closest('.health-card') || 
                e.target.closest('.modal-overlay') || 
                e.target.closest('.kpi-card') || 
                e.target.closest('.stack-item') ||
                e.target.closest('.modal-close')) {{
                return;
            }}
            
            themeIndex = (themeIndex + 1) % themes.length;
            const theme = themes[themeIndex];
            
            document.documentElement.style.setProperty('--bg-primary', theme.bg);
            document.documentElement.style.setProperty('--accent-primary', theme.accent);
            document.documentElement.style.setProperty('--accent-glow', `${{theme.accent}}40`);
            
            // Create ripple effect
            const ripple = document.createElement('div');
            ripple.className = 'ripple';
            ripple.style.left = e.clientX + 'px';
            ripple.style.top = e.clientY + 'px';
            document.body.appendChild(ripple);
            setTimeout(() => ripple.remove(), 1000);
        }});

        // Click outside modal to close
        document.getElementById('modalOverlay').addEventListener('click', (e) => {{
            if (e.target === document.getElementById('modalOverlay')) {{
                closeModal();
            }}
        }});
    </script>
</body>
</html>"""

    return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
