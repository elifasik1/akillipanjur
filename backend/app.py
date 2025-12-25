from flask import Flask, request, jsonify
from flask_cors import CORS
from db import init_db, insert_sensor_data, get_latest_sensor_data, get_state, set_state

app = Flask(__name__)
CORS(app)
init_db()

def decide_shutter(isik: int, sicaklik: float) -> str:
    # Kontrol algoritması mantığı 
    if sicaklik >= 30.0: return "CLOSED"
    if isik > 700 and sicaklik > 26.0: return "CLOSED"
    if isik < 300: return "OPEN"
    return "OPEN"

@app.get("/sensor-data")
def get_sensor_data():
    from db import get_history_data # Fonksiyonu buradan çağırıyoruz
    return jsonify({
        "latest": get_latest_sensor_data(), 
        "state": get_state(),
        "history": get_history_data(15) # Son 15 veriyi de gönderiyoruz
    })

@app.post("/sensor-data")
def post_sensor_data():
    data = request.get_json(silent=True) or {} 
    try:
        isik, sicaklik, nem = int(data["isik"]), float(data["sicaklik"]), float(data["nem"])
    except: return jsonify({"error": "Geçersiz veri"}), 400
    
    state = get_state()
    # Otomatik mod kontrolü [cite: 19, 108]
    shutter = decide_shutter(isik, sicaklik) if state["mode"] == "AUTO" else state["shutter"]
    if state["mode"] == "AUTO": set_state(shutter=shutter)
    
    insert_sensor_data(isik, sicaklik, nem, state["mode"], shutter) 
    return jsonify({"message": "ok", "mode": state["mode"], "shutter": shutter})

@app.post("/control")
def control():
    data = request.get_json(silent=True) or {} 
    mode, shutter = data.get("mode"), data.get("shutter")
    if shutter: mode = "MANUEL" # Manuel komut gelince mod değişir 
    set_state(mode=mode, shutter=shutter)
    return jsonify({"message": "ok", "state": get_state()})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)