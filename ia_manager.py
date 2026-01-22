import paho.mqtt.client as mqtt
import requests
import json

# CONFIGURAZIONE
MQTT_BROKER = "192.168.1.35" # L'IP della tua VirtualBox
MQTT_TOPIC_DATA = "caldaia/dati"
MQTT_TOPIC_COMANDO = "caldaia/set"

def interroga_ollama(messaggio_caldaia):
    url = "http://localhost:11434/api/generate"
    prompt = f"Sei un assistente tecnico. Dati caldaia: {messaggio_caldaia}. Se la temperatura è sopra 65 gradi, suggerisci di abbassarla inviando un JSON con la nuova temperatura. Rispondi solo con il JSON."
    
    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload)
        return response.json()['response']
    except Exception as e:
        return f"Errore Ollama: {e}"

def on_message(client, userdata, msg):
    dati = msg.payload.decode()
    print(f"IA analizza dati: {dati}")
    
    # L'IA analizza i dati
    risposta_ia = interroga_ollama(dati)
    print(f"Suggerimento IA: {risposta_ia}")
    
    # Se l'IA decide di cambiare qualcosa, lo pubblica su MQTT
    # (Logica semplificata: qui potresti estrarre i dati dal JSON di Ollama)

client = mqtt.Client()
client.connect(MQTT_BROKER, 1883, 60)
client.subscribe(MQTT_TOPIC_DATA)
client.on_message = on_message

print("IA locale avviata e in ascolto...")
client.loop_forever()