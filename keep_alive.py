from flask import Flask
from threading import Thread
import logging

# [1] สร้าง Instance ของ Flask สำหรับทำ Web Server ขนาดเล็ก
app = Flask('')

# [2] ปิดการแสดง Log ของ Flask (Werkzeug) เพื่อลดความรกของหน้าจอ Console
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/')
def home():
    # ข้อความที่จะแสดงเมื่อมีการเรียกไปที่ URL ของบอท
    return "🛡️ RETH OFFICIAL: Loader Bot is Online and Heartbeating!"

def run():
    # ใช้พอร์ต 8080 ซึ่งเป็นพอร์ตมาตรฐานที่ Hosting มักจะตรวจสอบ
    try:
        app.run(host='0.0.0.0', port=8080)
    except Exception as e:
        print(f"Keep Alive Server Error: {e}")

def keep_alive():
    """ฟังก์ชันที่จะถูกเรียกใน main.py เพื่อเริ่มรัน Web Server ใน Background"""
    t = Thread(target=run)
    # ตั้งเป็น Daemon เพื่อให้ Thread ปิดตัวเองเมื่อโปรแกรมหลักหยุดทำงาน
    t.daemon = True 
    t.start()
    print("✅ Keep Alive System: Active on Port 8080")
