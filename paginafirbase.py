from flask import Flask, jsonify, render_template
from threading import Thread
import paho.mqtt.client as mqtt

app = Flask(__name__)

# Configuración MQTT
MQTT_BROKER = "2001:db8:cb::1"
MQTT_PORT = 1886
MQTT_KEEP_ALIVE_INTERVAL = 60
TOPIC = "sensor/data"

# Almacén de datos recibidos
data_store = []

# Callback para cuando el cliente MQTT se conecta al broker
def on_connect(client, userdata, flags, rc):
    print(f"Conectado con el código de resultado: {rc}")
    client.subscribe(TOPIC)

# Callback para cuando se recibe un mensaje
def on_message(client, userdata, msg):
    global data_store
    try:
        import json
        message = json.loads(msg.payload.decode())
        print(f"Mensaje recibido: {message}")
        
        # Guardar los datos en el almacén
        data_store.append({
            "time": len(data_store) + 1,  # Simulación de tiempo
            "temperature": message["temperature"],
            "humidity": message["humidity"]
        })
    except Exception as e:
        print(f"Error al procesar el mensaje: {e}")

# Iniciar el cliente MQTT en un hilo separado
def start_mqtt_client():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEP_ALIVE_INTERVAL)
    client.loop_forever()

# Endpoint para obtener los datos
@app.route('/api/data')
def get_data():
    return jsonify(data_store)

# Ruta para la página principal
@app.route('/')
def index():
    return render_template('index.html')

# Iniciar Flask en un hilo separado
if __name__ == '__main__':
    # Iniciar el cliente MQTT en un hilo separado
    mqtt_thread = Thread(target=start_mqtt_client)
    mqtt_thread.daemon = True
    mqtt_thread.start()

    # Iniciar la aplicación Flask
    app.run(debug=True, host="0.0.0.0", port=5000)

