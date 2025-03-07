import json
import random

import aiomqtt
from sqlalchemy.exc import IntegrityError

from app.core.logger import get_logger
from app.model.tracking_event import TrackingEvent
from app.monitoring.metrics import MSG_RECEIVED_TOTAL
from app.schema.mqtt_data import MQTTDataPayload

log = get_logger()

CLIENT_ID = f"tracking-{random.randint(0, 1000)}"

FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60

FLAG_EXIT = False


class MQTTService:
    def __init__(self, host, port, username, password, topic, session_factory):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.topic = topic
        self.session_factory = session_factory

    async def subscribe(self):
        try:
            mqtt_client = aiomqtt.Client(
                    hostname=self.host,
                    port=self.port,
                    identifier=CLIENT_ID,
                    username=self.username,
                    password=self.password,
                    tls_params=aiomqtt.TLSParameters(ca_certs="app/client/emqxsl-ca.cer"),
                )
            log.info(f"Connecting to MQTT Broker: {self.host}:{self.port}")
            async with mqtt_client  as client:
                log.info(f"Subscribing to topic: {self.topic}")
                await client.subscribe(self.topic)
                async for message in client.messages:
                    try:
                        log.info(
                            f"Received `{message.payload.decode()}` from `{message.topic}` topic"
                        )
                        event_received = json.loads(message.payload.decode())
                        event = MQTTDataPayload(**event_received)
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
                    except Exception as e:
                        log.error(f"Could not process MQTT message: {e}")
                        MSG_RECEIVED_TOTAL.labels(
                            device_type="unknown", success=False
                        ).inc()
        except Exception as e:
            log.error(f"Error subscribing to MQTT topic: {e}")
