import paho.mqtt.client as mqtt
import requests
import json
import re

# CONFIGURAZIONE
MQTT_BROKER = "192.168.5.19"
MQTT_TOPIC_DATA = "caldaia/dati"
MQTT_TOPIC_COMANDO = "caldaia/set"
MQTT_TOPIC_LOG = "caldaia/ia_log" # Nuovo topic per i log

# CREDENZIALI
MQTT_USER = "Gruppo4" 
MQTT_PASSWORD = "techloop26"

def interroga_ollama(messaggio_caldaia):
    url = "http://localhost:11434/api/generate"
    
    prompt = (
        "Sei un sistema di controllo industriale. Rispondi SEMPRE e SOLO con una parola o un JSON.\n"
        "ESEMPIO 1: Se temperatura_mandata è 72.0, rispondi: {\"temperatura\": 55.0}\n"
        "ESEMPIO 2: Se temperatura_mandata è 52.1, rispondi: OK\n"
        f"Dati attuali da analizzare: {messaggio_caldaia}\n"
        "Risposta:"
    )
    
    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0,
            "stop": ["\n", "Nota:", "Dati:", "Spiegazione:"]
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()['response'].strip()
    except Exception as e:
        return f"Errore Ollama: {e}"

def on_message(client, userdata, msg):
    try:
        payload_str = msg.payload.decode()
        dati = json.loads(payload_str)
        temp_reale = dati.get("temperatura_mandata", 0)
        
        print(f"\n[DATI RICEVUTI]: Temp: {temp_reale}°C | Pressione: {dati.get('pressione_acqua')} bar")
        
        risposta_ia = interroga_ollama(payload_str)
        
        # LOGICA DI CONTROLLO CON INVIO LOG
        if '{"temperatura":' in risposta_ia and temp_reale > 65:
            match = re.search(r'\{.*\}', risposta_ia)
            if match:
                comando_pulito = match.group(0)
                print(f"[RAGIONAMENTO IA]: !!! EMERGENZA !!! Temperatura {temp_reale} > 65.")
                
                # Invia comando alla caldaia
                client.publish(MQTT_TOPIC_COMANDO, comando_pulito)
                
                # Invia log testuale a Home Assistant
                log_alert = f"⚠️ EMERGENZA: Temp {temp_reale}°C. Reset target a 55°C richiesto dall'IA."
                client.publish(MQTT_TOPIC_LOG, log_alert)
                
                print(f"--- COMANDO INVIATO ALLA CALDAIA: {comando_pulito} ---")
        else:
            print(f"[RAGIONAMENTO IA]: Stato Normale. Risposta IA: {risposta_ia}")
            # Log di stato normale (facoltativo, mantiene aggiornata l'interfaccia)
            client.publish(MQTT_TOPIC_LOG, "✅ Sistema in sicurezza - Monitoraggio attivo")

    except Exception as e:
        print(f"Errore nel processare il messaggio: {e}")

# Configurazione Client
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
client.on_message = on_message

try:
    client.connect(MQTT_BROKER, 1883, 60)
    client.subscribe(MQTT_TOPIC_DATA)
    print("IA locale con LOGGING attivo. In ascolto...")
    client.loop_forever()
except Exception as e:
    print(f"Errore di connessione: {e}")