import paho.mqtt.client as mqtt
import requests
import json
import re

# CONFIGURAZIONE
MQTT_BROKER = "192.168.1.35"
MQTT_TOPIC_DATA = "caldaia/dati"
MQTT_TOPIC_COMANDO = "caldaia/set"

# CREDENZIALI
MQTT_USER = "Gruppo4" 
MQTT_PASSWORD = "techloop26"

def interroga_ollama(messaggio_caldaia):
    url = "http://localhost:11434/api/generate"
    
    # Prompt molto più autoritario per evitare chiacchiere
    prompt = (
        f"Dati caldaia: {messaggio_caldaia}. "
        "REGOLE RIGIDE: Se 'temperatura_mandata' > 65, rispondi ESCLUSIVAMENTE con il JSON: "
        "{\"temperatura\": 55.0}. Se è <= 65, rispondi ESCLUSIVAMENTE con la parola 'OK'. "
        "Non aggiungere spiegazioni, non scrivere altro."
    )
    
    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0  # Forza l'IA a essere precisa e non creativa
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        risposta = response.json()['response'].strip()
        return risposta
    except Exception as e:
        return f"Errore connessione Ollama: {e}"

def on_message(client, userdata, msg):
    dati_raw = msg.payload.decode()
    print(f"\n[DATI RICEVUTI]: {dati_raw}")
    
    # L'IA analizza i dati
    risposta_ia = interroga_ollama(dati_raw)
    
    # Pulizia della risposta (estriamo solo il JSON se l'IA ha aggiunto testo per errore)
    comando_pulito = None
    if '{"temperatura":' in risposta_ia:
        match = re.search(r'\{.*\}', risposta_ia) # Cerca il pattern JSON { }
        if match:
            comando_pulito = match.group(0)

    if comando_pulito:
        print(f"[RAGIONAMENTO IA]: Soglia superata! Invio correzione.")
        client.publish(MQTT_TOPIC_COMANDO, comando_pulito)
        print(f"--- COMANDO INVIATO ALLA CALDAIA: {comando_pulito} ---")
    else:
        print(f"[RAGIONAMENTO IA]: {risposta_ia}")

# Configurazione Client
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
client.on_message = on_message

try:
    client.connect(MQTT_BROKER, 1883, 60)
    client.subscribe(MQTT_TOPIC_DATA)
    print("IA locale ottimizzata avviata. In ascolto su MQTT...")
    client.loop_forever()
except Exception as e:
    print(f"Errore di connessione dell'IA: {e}")