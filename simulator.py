import paho.mqtt.client as mqtt
import time
import json
import random

# CONFIGURAZIONE
MQTT_BROKER = "192.168.1.35" 
MQTT_TOPIC_DATA = "caldaia/dati"
MQTT_TOPIC_COMMAND = "caldaia/set"

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
            print(f"\n[IA] COMANDO RICEVUTO: Nuova temperatura target: {temperatura_target}°C")
    except Exception as e:
        print(f"Errore nel processare il comando: {e}")

# --- CONFIGURAZIONE CLIENT (VERSIONE 2 PER EVITARE WARNING) ---
# Usiamo CallbackAPIVersion.VERSION2 per compatibilità con le ultime librerie
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
client.on_message = on_message 

try:
    print(f"Tentativo di connessione a {MQTT_BROKER}...")
    # Il timeout è impostato a 60 secondi
    client.connect(MQTT_BROKER, 1883, 60)
    print(f"Connesso con successo al broker MQTT!")
    
    # Sottoscrizione al topic dei comandi
    client.subscribe(MQTT_TOPIC_COMMAND)
    client.loop_start() 
    
except TimeoutError:
    print("\nERRORE: Timeout della connessione. Controlla che:")
    print(f"1. La VirtualBox con IP {MQTT_BROKER} sia accesa.")
    print("2. La rete di VirtualBox sia impostata su 'Scheda con bridge'.")
    print("3. Il firewall della macchina virtuale permetta il traffico sulla porta 1883.")
    exit()
except Exception as e:
    print(f"Errore di connessione imprevisto: {e}")
    exit()

print("Inizio invio dati simulati... (Premi CTRL+C per fermare)")

try:
    while True:
        # Simulazione dati dinamici basati sul target dell'IA
        dati_caldaia = {
            "temperatura_mandata": round(random.uniform(temperatura_target - 1.5, temperatura_target + 1.5), 1),
            "pressione_acqua": round(random.uniform(1.4, 1.6), 2),
            "fiamma_accesa": True if temperatura_target > 20 else False,
            "stato": "OK",
            "target_impostato": temperatura_target
        }
        
        # Pubblicazione dati
        client.publish(MQTT_TOPIC_DATA, json.dumps(dati_caldaia))
        print(f"Inviato: {dati_caldaia}", end='\r') # Sovrascrive la riga per pulizia
        
        time.sleep(5)
except KeyboardInterrupt:
    print("\nSimulatore arrestato dall'utente.")
    client.disconnect()