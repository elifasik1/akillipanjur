from flask import Flask, jsonify, request
from flask_cors import CORS
import serial
import threading
import re
import time

from db import (
    init_db,
    insert_sensor_data,
    get_history_data,
    get_latest_sensor_data,
    get_state,
    set_state
)

app = Flask(__name__)
CORS(app)

# ---------------- DB ----------------
init_db()

# ---------------- SHUTTER LOGIC ----------------
def decide_shutter(isik: int, sicaklik: float) -> str:
    if sicaklik >= 30:
        return "CLOSED"
    if isik > 700 and sicaklik > 26:
        return "CLOSED"
    if isik < 300:
        return "OPEN"
    return "OPEN"

# ---------------- SERIAL ----------------
try:
    ser = serial.Serial("COM3", 9600, timeout=1)
    time.sleep(2)  # Arduino reset bekle
    print("Arduino baglandi (COM3)")
except Exception as e:
    ser = None
    print("Arduino baglanamadi:", e)

# ---------------- LISTENER ----------------
def listen_to_arduino():
    while True:
        try:
            if not ser or not ser.is_open:
                continue

            line = ser.readline().decode("utf-8", errors="ignore").strip()
            if not line:
                continue

            print("SERIAL:", line)

            match = re.search(
                r"Durum:\s*(\w+)\s*\|\s*LDR:\s*(\d+)\s*\|\s*Sicaklik:\s*([\d.]+)C\s*\|\s*Nem:\s*([\d.]+)%",
                line
            )

            if not match:
                continue

            durum = match.group(1)
            isik = int(match.group(2))
            sicaklik = float(match.group(3))
            nem = float(match.group(4))

            shutter = "CLOSED" if durum.upper() == "KAPALI" else "OPEN"
            state = get_state()

            insert_sensor_data(
                isik=isik,
                sicaklik=sicaklik,
                nem=nem,
                mode=state["mode"],
                shutter=shutter
            )

        except Exception as e:
            print("OKUMA HATASI:", e)

# Thread baslat
threading.Thread(target=listen_to_arduino, daemon=True).start()

# ---------------- API ----------------
@app.route("/sensor-data", methods=["GET"])
def sensor_data():
    return jsonify({
        "latest": get_latest_sensor_data(),
        "state": get_state(),
        "history": get_history_data(15)
    })

@app.route("/control", methods=["POST"])
def control():
    data = request.get_json(silent=True) or {}

    mode = data.get("mode")
    shutter = data.get("shutter")

    if shutter:
        mode = "MANUEL"

    set_state(mode=mode, shutter=shutter)

    return jsonify({"status": "ok", "state": get_state()})

# ---------------- MAIN ----------------
if __name__ == "__main__":
    # ⚠️ DEBUG KAPALI - SERIAL ICIN ZORUNLU
    app.run(host="127.0.0.1", port=5000, debug=False)
