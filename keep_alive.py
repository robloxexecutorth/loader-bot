from flask import Flask
from threading import Thread
import logging

# [1] สร้าง Instance ของ Flask
app = Flask('')

# [2] ปิด Log ของ Flask ที่ไม่จำเป็นเพื่อประหยัดทรัพยากร
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/')
def home():
    # ข้อความที่จะแสดงเมื่อเรากดเข้า URL ของบอท
    return "🛡️ RETH OFFICIAL: Loader Bot is Heartbeating!"

def run():
    # พอร์ต 8080 เป็นพอร์ตมาตรฐานที่ Render มักจะมองหา
    try:
        app.run(host='0.0.0.0', port=8080)
    except Exception as e:
        print(f"Keep Alive Error: {e}")

def keep_alive():
    """ฟังก์ชันหลักที่จะถูกเรียกใช้ใน main.py เพื่อเริ่มรัน Server ขนาดเล็ก"""
    t = Thread(target=run)
    # ตั้งเป็น Daemon เพื่อให้ Thread ปิดตัวลงอัตโนมัติเมื่อโปรแกรมหลัก (บอท) ปิด
    t.daemon = True 
    t.start()
    print("✅ Keep Alive System: Active on Port 8080")
