━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SmartSign — by Harsh Manglam
  CRPF Public School, Rohini | Class 12D
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 FILES IN THIS FOLDER:
─────────────────────────
  start.bat        ← Double-click this EVERY morning
  brain.py         ← The AI background watcher (auto-started)
  periodsync.html  ← Your app (auto-opens in browser)
  config.json      ← Edit teacher names & API keys here
  README.txt       ← This file


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  FIRST TIME SETUP (do this ONCE only)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STEP 1 — Add your Gemini API keys to config.json
  1. Open config.json in Notepad
  2. Replace "PASTE_YOUR_GEMINI_KEY_1_HERE" with your key
  3. Get a free key at: https://aistudio.google.com/app/apikey
  4. Add multiple keys for backup (if key 1 fails, key 2 is used)
  5. Save the file

STEP 2 — Double click start.bat
  - First time will install Python + Tesseract automatically
  - This takes 5-10 minutes (internet needed)
  - After this, every future start takes only 10 seconds

STEP 3 — Wait for SmartSign to open in Edge
  - You will see a green window saying "Brain is running!"
  - SmartSign will open automatically in your browser
  - DO NOT close the black window — minimize it!


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  EVERY DAY USAGE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Double-click start.bat before class starts
2. SmartSign opens in browser automatically
3. Teacher opens smart board (PPT / YouTube / Word / Blackboard)
4. Every 10 seconds, AI reads the screen
5. Teacher name + Topic fills automatically in the correct period
6. You just need to get the teacher's SIGNATURE
7. Click "Lock Row" after signing to protect it


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  HOW TO CHANGE TEACHER NAMES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Open config.json in Notepad
2. Find the "teachers" section
3. Change any name — e.g. "Balesh Vashisth" to "New Teacher"
4. Save the file
5. Changes take effect on next screenshot (within 10 seconds)
   No need to restart anything!


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  HOW TO ADD/CHANGE API KEYS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Open config.json in Notepad
2. Find "api_keys" section
3. Add or replace keys in the list
4. Keys are tried in order — key 1 first, then key 2, etc.
5. Save the file — takes effect immediately


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  TROUBLESHOOTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Problem: "Brain not running" shows in the app
Fix: Double-click start.bat and keep the window open

Problem: Topics not auto-filling
Fix: Check your Gemini API key in config.json
     Make sure start.bat window is still open

Problem: First time setup fails
Fix: Make sure you have internet connection
     Run start.bat as Administrator (right-click → Run as Admin)

Problem: Wrong teacher name being filled
Fix: Open config.json and correct the teacher name

Check periodsync_log.txt for detailed error messages


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Made by Harsh Manglam | CRPF Public School Rohini
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
