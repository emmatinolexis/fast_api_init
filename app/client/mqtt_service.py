from concurrent.futures import ThreadPoolExecutor
import json
import random
import threading
import time
from typing import Any, Coroutine, TypeVar

from paho.mqtt import client as mqtt_client
from sqlalchemy.exc import IntegrityError

from app.core.logger import get_logger
from app.model.tracking_event import TrackingEvent
from app.monitoring.metrics import MSG_RECEIVED_TOTAL
from app.schema.mqtt_data import MQTTDataPayload
import asyncio

log = get_logger()

CLIENT_ID = f"tracking-{random.randint(0, 1000)}"

FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60

FLAG_EXIT = False

T = TypeVar("T")


class MQTTService:
    def __init__(self, host, port, username, password, topic, session_factory):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.topic = topic
        self.session_factory = session_factory

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
            event_received = json.loads(msg.payload.decode())
            event = MQTTDataPayload(**event_received)
            async def save_event():
                async with self.session_factory() as session:
                    query = TrackingEvent(**event.model_dump())
                    try:
                        session.add(query)
                        await session.commit()
                        await session.refresh(query)

                        log.info(f"Event saved to database: {event_received}")
                        MSG_RECEIVED_TOTAL.labels(
                            device_type=event.device_type, success=True
                        ).inc()
                    except IntegrityError as e:
                        log.error(f"Integrity Error: {e}")
                        MSG_RECEIVED_TOTAL.labels(
                            device_type=event.device_type, success=False
                        ).inc()
                    except Exception as e:
                        log.error(f"Exception: {e}")
                        MSG_RECEIVED_TOTAL.labels(
                            device_type=event.device_type, success=False
                        ).inc()

            self._run_coroutine_sync(save_event())

        try:
            log.info(f"Subscribing to topic: {self.topic}")
            if not mqtt_client.is_connected():
                log.error("MQTT client is not connected!")
                mqtt_client = self.connect_mqtt()
            mqtt_client.subscribe(self.topic)
            mqtt_client.on_message = on_message
        except Exception as e:
            log.error(f"Could not subscribe to MQTT topic: {e}")

    def _run_coroutine_sync(self, coroutine: Coroutine[Any, Any, T], timeout: float = 30) -> T:
        def run_in_new_loop():
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                return new_loop.run_until_complete(coroutine)
            finally:
                new_loop.close()

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(coroutine)

        if threading.current_thread() is threading.main_thread():
            if not loop.is_running():
                return loop.run_until_complete(coroutine)
            else:
                with ThreadPoolExecutor() as pool:
                    future = pool.submit(run_in_new_loop)
                    return future.result(timeout=timeout)
        else:
            return asyncio.run_coroutine_threadsafe(coroutine, loop).result()