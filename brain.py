"""
PeriodSync Brain — by Harsh Manglam
====================================
Runs silently in background.
Takes screenshots → OCR → Gemini AI → sends topic to browser app.
Multiple API key fallback built in.
"""

import os, sys, json, time, base64, threading, datetime, logging
from pathlib import Path
from io import BytesIO

# ── Setup logging ─────────────────────────────────────────────────────────────
logging.basicConfig(
    filename="periodsync_log.txt",
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s"
)
log = logging.getLogger("PeriodSync")

# ── Load config ───────────────────────────────────────────────────────────────
CONFIG_PATH = Path(__file__).parent / "config.json"

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# ── Shared state (thread-safe) ────────────────────────────────────────────────
state = {
    "current_period": None,   # e.g. "Period 3"
    "last_topic":     "",
    "last_subject":   "",
    "last_teacher":   "",
    "status":         "starting",   # starting / watching / tiffin / idle / error
    "last_update":    "",
    "api_status":     "ok",
    "screenshot_b64": ""
}
state_lock = threading.Lock()

# ── Figure out which period it is right now ───────────────────────────────────
def get_current_period(periods):
    now = datetime.datetime.now().time()
    for p in periods:
        start = datetime.datetime.strptime(p["start"], "%H:%M").time()
        end   = datetime.datetime.strptime(p["end"],   "%H:%M").time()
        if start <= now <= end:
            return p["name"]
    return None

# ── Take a screenshot ─────────────────────────────────────────────────────────
def take_screenshot():
    try:
        import mss, mss.tools
        with mss.mss() as sct:
            monitor = sct.monitors[0]   # full screen (all monitors combined)
            sct_img  = sct.grab(monitor)
            from PIL import Image
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            # Resize to reduce API payload
            img.thumbnail((1280, 720), Image.LANCZOS)
            buf = BytesIO()
            img.save(buf, format="JPEG", quality=75)
            return buf.getvalue()
    except Exception as e:
        log.error(f"Screenshot failed: {e}")
        return None

# ── OCR on the screenshot ─────────────────────────────────────────────────────
def ocr_image(img_bytes):
    try:
        import pytesseract
        from PIL import Image
        img = Image.open(BytesIO(img_bytes))
        text = pytesseract.image_to_string(img, lang="eng")
        return text.strip()
    except Exception as e:
        log.error(f"OCR failed: {e}")
        return ""

# ── Gemini API call with multi-key fallback ───────────────────────────────────
def ask_gemini(img_bytes, ocr_text, subjects, ignore_kw, api_keys):
    """
    Sends screenshot + OCR text to Gemini.
    Tries each API key in order. Returns dict with subject + topic.
    """
    import google.generativeai as genai

    prompt = f"""
You are an AI assistant for a school class record system in India.
You are looking at a screenshot of a classroom smart board / OPS screen.

The OCR text read from the screen is:
\"\"\"
{ocr_text[:3000]}
\"\"\"

Valid subjects for this class: {subjects}
Ignore these if detected: {ignore_kw}

Your job:
1. Identify which SUBJECT is being taught RIGHT NOW from the screen content.
2. Write a SHORT topic description (max 12 words) of what is being taught.
3. If the screen shows YouTube, read the video title as the topic.
4. If the screen shows PowerPoint, read the slide heading as the topic.
5. If the screen shows a Word document, summarize the heading.
6. If it shows a virtual blackboard, summarize what is written.
7. If you cannot determine the subject (e.g. desktop, lock screen, irrelevant), return subject as "Unknown".

Respond ONLY in this exact JSON format, nothing else:
{{
  "subject": "Physics",
  "topic": "Newton's Second Law of Motion - Force and Acceleration"
}}
"""

    last_error = None
    for key_index, api_key in enumerate(api_keys):
        if not api_key or api_key.startswith("PASTE_"):
            continue
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")

            # Send both image and OCR text
            from PIL import Image as PILImage
            img = PILImage.open(BytesIO(img_bytes))

            response = model.generate_content([prompt, img])
            raw = response.text.strip()

            # Clean JSON from response
            if "```" in raw:
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            raw = raw.strip()

            result = json.loads(raw)
            log.info(f"Gemini key {key_index+1} succeeded: {result}")
            return result

        except Exception as e:
            last_error = e
            log.warning(f"Gemini key {key_index+1} failed: {e}")
            continue

    log.error(f"All Gemini keys failed. Last error: {last_error}")
    return {"subject": "Unknown", "topic": ""}

# ── Main watcher loop ─────────────────────────────────────────────────────────
def watcher_loop():
    log.info("PeriodSync Brain started.")
    while True:
        try:
            cfg = load_config()   # reload config each loop so edits take effect immediately
            interval  = cfg.get("screenshot_interval_seconds", 10)
            periods   = cfg.get("periods", [])
            teachers  = cfg.get("teachers", {})
            subjects  = cfg.get("subjects", [])
            ignore_kw = cfg.get("ignore_keywords", [])
            api_keys  = cfg.get("api_keys", [])

            # Which period is it?
            period_name = get_current_period(periods)

            if period_name is None:
                with state_lock:
                    state["status"]         = "idle"
                    state["current_period"] = None
                log.info("No active period right now. Waiting...")
                time.sleep(30)
                continue

            # Take screenshot
            img_bytes = take_screenshot()
            if img_bytes is None:
                time.sleep(interval)
                continue

            # OCR
            ocr_text = ocr_image(img_bytes)

            # Ask Gemini
            result  = ask_gemini(img_bytes, ocr_text, subjects, ignore_kw, api_keys)
            subject = result.get("subject", "Unknown")
            topic   = result.get("topic", "")

            # Get teacher name for this subject
            teacher = teachers.get(subject, "")

            # Save screenshot as base64 for display in app
            b64 = base64.b64encode(img_bytes).decode("utf-8")

            with state_lock:
                state["current_period"] = period_name
                state["last_subject"]   = subject
                state["last_topic"]     = topic
                state["last_teacher"]   = teacher
                state["status"]         = "watching"
                state["last_update"]    = datetime.datetime.now().strftime("%H:%M:%S")
                state["screenshot_b64"] = b64
                state["api_status"]     = "ok" if subject != "Unknown" else "uncertain"

            log.info(f"Period={period_name} | Subject={subject} | Topic={topic} | Teacher={teacher}")

        except Exception as e:
            log.error(f"Watcher loop error: {e}")
            with state_lock:
                state["status"] = "error"

        time.sleep(interval)

# ── Flask server ──────────────────────────────────────────────────────────────
def run_server():
    from flask import Flask, jsonify, send_file, request
    from flask_cors import CORS

    app = Flask(__name__)
    CORS(app)   # allow browser to call this local server

    @app.route("/status")
    def status():
        with state_lock:
            return jsonify(dict(state))

    @app.route("/latest")
    def latest():
        """Returns the latest detected subject, topic, teacher, period."""
        with state_lock:
            return jsonify({
                "period":  state["current_period"],
                "subject": state["last_subject"],
                "topic":   state["last_topic"],
                "teacher": state["last_teacher"],
                "status":  state["status"],
                "time":    state["last_update"]
            })

    @app.route("/config")
    def get_config():
        """Returns config (without API keys) for the frontend to read."""
        cfg = load_config()
        safe = {k: v for k, v in cfg.items() if k != "api_keys"}
        return jsonify(safe)

    @app.route("/screenshot")
    def screenshot():
        """Returns the latest screenshot as base64 JPEG."""
        with state_lock:
            b64 = state.get("screenshot_b64", "")
        return jsonify({"image": b64})

    @app.route("/ping")
    def ping():
        return jsonify({"ok": True, "message": "PeriodSync Brain is running!"})

    @app.route("/")
    def index():
        html_path = Path(__file__).parent / "periodsync.html"
        return send_file(str(html_path))

    log.info("Flask server starting on http://localhost:5050")
    app.run(host="127.0.0.1", port=5050, debug=False, use_reloader=False)

# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Start watcher in background thread
    watcher = threading.Thread(target=watcher_loop, daemon=True)
    watcher.start()

    # Run Flask server (blocking — keeps process alive)
    run_server()
