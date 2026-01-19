import paho.mqtt.client as mqtt
import time
import json
import random

# CONFIGURAZIONE
MQTT_BROKER = "192.168.1.35" 
MQTT_TOPIC = "caldaia/dati"
# Inserisci qui le credenziali che hai configurato in Home Assistant
MQTT_USER = "gruppo4" 
MQTT_PASSWORD = "techloop26"

client = mqtt.Client()

# --- RIGA AGGIUNTA PER L'AUTENTICAZIONE ---
client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
# ------------------------------------------

try:
    client.connect(MQTT_BROKER, 1883, 60)
    print(f"Connesso al broker MQTT su {MQTT_BROKER}")
except Exception as e:
    print(f"Errore di connessione: {e}")

while True:
    # Simuliamo dati che arrivano via OpenTherm
    dati_caldaia = {
        "temperatura_mandata": round(random.uniform(40.0, 70.0), 1),
        "pressione_acqua": round(random.uniform(1.2, 1.8), 2),
        "fiamma_accesa": random.choice([True, False]),
        "stato": "OK"
    }
    
    # Invio i dati a Home Assistant
    client.publish(MQTT_TOPIC, json.dumps(dati_caldaia))
    print(f"Inviato: {dati_caldaia}")
    
    time.sleep(5) # Aspetta 5 secondi