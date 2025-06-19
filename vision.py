"""
vision.py
----------
Deteksi objek dengan YOLOv8 + keputusan gerak L/R/F/S
• Untuk simulasi      : pastikan ada robot_sim.py
• Untuk robot fisik   : buat robot_serial.py lalu ganti import di baris 18
"""

from ultralytics import YOLO
import cv2, time

# ⬇️  Ganti modul ini:
import robot_serial as robot            # → if ready:  import robot_serial as robot

# ────────────────────────────────
# 1. Inisialisasi model & kamera
# ────────────────────────────────
model = YOLO("yolov8n.pt")           # otomatis di‑download pertama kali
cap   = cv2.VideoCapture(0)          # 0 = webcam laptop

if not cap.isOpened():
    raise RuntimeError("Webcam tidak terdeteksi.")

FRAME_W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 640)
CENTER  = FRAME_W // 2               # titik tengah layar
DEAD    = 60                         # zona tenang ±60 px

# ────────────────────────────────
# 2. Loop utama
# ────────────────────────────────
try:
    while True:
        ok, frame = cap.read()
        if not ok:
            print("🔴  Gagal ambil frame webcam.")
            break

        # predict() ⇒ list[Results]  (bukan generator)
        results = model.predict(frame, verbose=False)    # default imgsz 640
        r       = results[0]                             # hanya 1 frame

        # ─── Ambil kotak dengan kepercayaan tertinggi ──
        decision = "S"                                   # default STOP
        if len(r.boxes):                                 # ada deteksi
            best_idx = r.boxes.conf.argmax()
            box      = r.boxes[best_idx]

            x1, y1, x2, y2 = box.xyxy.cpu().numpy()[0]
            cx = int((x1 + x2) / 2)                      # titik tengah bbox

            if   cx < CENTER - DEAD: decision = "L"
            elif cx > CENTER + DEAD: decision = "R"
            else:                    decision = "F"

        robot.act(decision)                              # kirim ke robot

        # ─── Tampilkan frame dengan bbox ───────────────
        cv2.imshow("YOLO‑Robot", r.plot())
        if cv2.waitKey(1) & 0xFF == 27:                  # ESC untuk keluar
            break

finally:
    cap.release()
    cv2.destroyAllWindows()