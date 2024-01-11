import random
import time

from paho.mqtt import client as mqtt_client

from app.core.logger import get_logger

log = get_logger()

CLIENT_ID = f"tracking-{random.randint(0, 1000)}"

FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60

FLAG_EXIT = False


class MQTTService:
    def __init__(self, host, port, username, password, topic):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.topic = topic

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0 and client.is_connected():
            log.info("Connected to MQTT Broker!")
        else:
            log.info(f"Failed to connect, return code {rc}")

    def on_disconnect(self, client, userdata, rc):
        log.info("Disconnected with result code: %s", rc)
        reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
        while reconnect_count < MAX_RECONNECT_COUNT:
            log.info("Reconnecting in %d seconds...", reconnect_delay)
            time.sleep(reconnect_delay)

            try:
                client.reconnect()
                log.info("Reconnected successfully!")
                return
            except Exception as err:
                log.error("%s. Reconnect failed. Retrying...", err)

            reconnect_delay *= RECONNECT_RATE
            reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
            reconnect_count += 1
        log.info("Reconnect failed after %s attempts. Exiting...", reconnect_count)
        global FLAG_EXIT
        FLAG_EXIT = True

    def connect_mqtt(self):
        try:
            client = mqtt_client.Client(CLIENT_ID)
            # Set CA certificate
            client.tls_set(ca_certs="app/client/emqxsl-ca.cer")
            client.username_pw_set(self.username, self.password)
            client.on_connect = self.on_connect
            client.connect(self.host, self.port, keepalive=120)
            client.on_disconnect = self.on_disconnect

            client.loop_start()
            time.sleep(1)

            if not client.is_connected():
                log.error("MQTT client is not connected!")
                client.loop_stop()
                return None
            log.info(
                f"MQTT client is connected: {CLIENT_ID} to {self.host}:{self.port}"
            )
            return client
        except Exception as e:
            log.error(f"Could not connect to MQTT broker: {e}")
            return None

    def subscribe(self, mqtt_client):
        def on_message(mqtt_client, userdata, msg):
            log.info(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

        try:
            log.info(f"Subscribing to topic: {self.topic}")
            mqtt_client.subscribe(self.topic)
            mqtt_client.on_message = on_message
        except Exception as e:
            log.error(f"Could not subscribe to MQTT topic: {e}")
