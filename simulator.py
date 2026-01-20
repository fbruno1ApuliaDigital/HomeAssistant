import paho.mqtt.client as mqtt
import time
import json
import random

# CONFIGURAZIONE
MQTT_BROKER = "192.168.1.35" 
MQTT_TOPIC_DATA = "caldaia/dati"
MQTT_TOPIC_COMMAND = "caldaia/set" # Topic dove l'IA invierà i comandi

MQTT_USER = "Gruppo4" 
MQTT_PASSWORD = "techloop26"

# Variabile per memorizzare la temperatura impostata dall'IA
temperatura_target = 50.0

# --- FUNZIONE CHE RICEVE I COMANDI DALL'IA ---
def on_message(client, userdata, msg):
    global temperatura_target
    try:
        payload = json.loads(msg.payload.decode())
        if "temperatura" in payload:
            temperatura_target = float(payload["temperatura"])
            print(f"--- COMANDO IA RICEVUTO: Nuova temperatura target: {temperatura_target}°C ---")
    except Exception as e:
        print(f"Errore nel processare il comando: {e}")

client = mqtt.Client()
client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
client.on_message = on_message # Collega la funzione di ascolto

try:
    client.connect(MQTT_BROKER, 1883, 60)
    print(f"Connesso al broker MQTT su {MQTT_BROKER}")
    
    # Inizia ad ascoltare i comandi
    client.subscribe(MQTT_TOPIC_COMMAND)
    client.loop_start() # Avvia il loop di ascolto in un thread separato
    
except Exception as e:
    print(f"Errore di connessione: {e}")

while True:
    # Simuliamo dati che oscillano intorno alla temperatura target impostata dall'IA
    dati_caldaia = {
        "temperatura_mandata": round(random.uniform(temperatura_target - 2, temperatura_target + 2), 1),
        "pressione_acqua": round(random.uniform(1.2, 1.8), 2),
        "fiamma_accesa": random.choice([True, False]),
        "stato": "OK",
        "target_impostato": temperatura_target
    }
    
    # Invio i dati a Home Assistant
    client.publish(MQTT_TOPIC_DATA, json.dumps(dati_caldaia))
    print(f"Inviato: {dati_caldaia}")
    
    time.sleep(5)
    