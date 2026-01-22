import paho.mqtt.client as mqtt
import requests
import json

# CONFIGURAZIONE
MQTT_BROKER = "192.168.1.35"
MQTT_TOPIC_DATA = "caldaia/dati"
MQTT_TOPIC_COMANDO = "caldaia/set"

# CREDENZIALI (Aggiunte per sbloccare l'ascolto)
MQTT_USER = "Gruppo4" 
MQTT_PASSWORD = "techloop26"

def interroga_ollama(messaggio_caldaia):
    url = "http://localhost:11434/api/generate"
    # Prompt ottimizzato per ricevere solo il JSON
    prompt = f"Dati caldaia: {messaggio_caldaia}. Se temperatura_mandata > 65, rispondi SOLO con questo JSON: {{\"temperatura\": 55.0}}. Altrimenti rispondi 'OK'."
    
    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()['response']
    except Exception as e:
        return f"Errore connessione Ollama: {e}"

def on_message(client, userdata, msg):
    dati = msg.payload.decode()
    print(f"\n[DATI RICEVUTI]: {dati}")
    
    # Interroga Ollama
    risposta_ia = interroga_ollama(dati)
    print(f"[RAGIONAMENTO IA]: {risposta_ia}")
    
    # Se l'IA suggerisce una nuova temperatura, la inviamo alla caldaia
    if '{"temperatura":' in risposta_ia:
        client.publish(MQTT_TOPIC_COMANDO, risposta_ia)
        print(f"--- COMANDO INVIATO ALLA CALDAIA: {risposta_ia} ---")

# Configurazione Client con versione 2 e credenziali
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
client.on_message = on_message

try:
    client.connect(MQTT_BROKER, 1883, 60)
    client.subscribe(MQTT_TOPIC_DATA)
    print("IA locale avviata e correttamente autenticata. In ascolto...")
    client.loop_forever()
except Exception as e:
    print(f"Errore di connessione dell'IA: {e}")