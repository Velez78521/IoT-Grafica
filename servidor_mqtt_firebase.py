import paho.mqtt.client as mqtt
import firebase_admin
from firebase_admin import credentials, firestore

# Configuración de los parámetros MQTT
MQTT_BROKER = "2001:db8:cb::1"  # Dirección IPv6 del broker MQTT
MQTT_PORT = 1886  # Puerto MQTT
MQTT_KEEP_ALIVE_INTERVAL = 60  # Intervalo de mantenimiento de la conexión
TOPIC = "sensor/data"  # Nombre del topic al que te vas a suscribir
QOS = 0  # Nivel de QoS (0, 1, 2)

# Inicializar Firebase
cred = credentials.Certificate('/home/velez/RIOT/examples/emcute_mqttsn/base-sensores-firebase-adminsdk-vdffh-eb998bdd5f.json')  # Asegúrate de tener el archivo de clave JSON de Firebase
firebase_admin.initialize_app(cred)

# Referencia a la base de datos Firestore
db = firestore.client()
messages_ref = db.collection('messages')  # Nombre de la colección en Firestore

# Función para guardar un mensaje en Firestore
def save_message(topic, message):
    # Añadir el mensaje a la colección "messages" en Firestore
    messages_ref.add({
        'topic': topic,
        'message': message
    })
    print(f"Mensaje guardado en Firebase: {message}")

# Callback para cuando el cliente se conecta al broker
def on_connect(client, userdata, flags, rc):
    print(f"Conectado con el código de resultado: {rc}")
    # Nos suscribimos al topic 'sensor/data' cuando nos conectamos al broker
    client.subscribe(TOPIC, qos=QOS)

# Callback para cuando se recibe un mensaje
def on_message(client, userdata, msg):
    message = msg.payload.decode()
    print(f"Mensaje recibido en el topic '{msg.topic}': {message}")
    # Si el mensaje proviene del topic 'sensor/data', lo guardamos en Firebase
    if msg.topic == "sensor/data":
        save_message(msg.topic, message)

# Crear una instancia del cliente MQTT
client = mqtt.Client()

# Asignar las funciones callback
client.on_connect = on_connect
client.on_message = on_message

# Conectar al broker MQTT
client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEP_ALIVE_INTERVAL)

# Bloquear el cliente para esperar mensajes
client.loop_forever()

