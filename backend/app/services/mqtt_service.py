import json
import logging
from typing import Dict, Any, Optional
import paho.mqtt.client as mqtt
from app.config import settings

logger = logging.getLogger("mqtt_service")

class MQTTManager:
    """
    Mosquitto MQTT client manager for IIoT telemetry streaming.
    """

    def __init__(self, broker_host: str = "localhost", broker_port: int = 1883):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client = mqtt.Client(client_id="tyreiq_backend_subscriber", callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self.is_connected = False
        self._setup_callbacks()

    def _setup_callbacks(self):
        def on_connect(client, userdata, flags, rc, properties=None):
            if rc == 0:
                self.is_connected = True
                logger.info(f"Connected to Mosquitto MQTT Broker at {self.broker_host}:{self.broker_port}")
                # Subscribe to all mine topics
                client.subscribe("mine/+/truck/+/tyre/+/telemetry")
                client.subscribe("mine/+/truck/+/imu")
                client.subscribe("mine/+/truck/+/gps")
                client.subscribe("mine/+/tyre/+/inspection")
                client.subscribe("mine/+/alerts")
            else:
                logger.warning(f"Failed to connect to MQTT broker, rc={rc}")

        def on_message(client, userdata, msg):
            try:
                payload = json.loads(msg.payload.decode("utf-8"))
                logger.info(f"MQTT Message received on topic {msg.topic}: {payload.get('scenario_id', 'unknown')}")
            except Exception as e:
                logger.error(f"Error parsing MQTT payload on topic {msg.topic}: {e}")

        self.client.on_connect = on_connect
        self.client.on_message = on_message

    def connect(self):
        try:
            self.client.connect_async(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
        except Exception as e:
            logger.warning(f"MQTT broker connection unavailable ({e}). Operating in HTTP/simulation fallback mode.")

    def publish_telemetry(self, mine_id: str, truck_id: str, tyre_id: str, payload: Dict[str, Any]):
        topic = f"mine/{mine_id}/truck/{truck_id}/tyre/{tyre_id}/telemetry"
        self._publish(topic, payload)

    def publish_imu(self, mine_id: str, truck_id: str, payload: Dict[str, Any]):
        topic = f"mine/{mine_id}/truck/{truck_id}/imu"
        self._publish(topic, payload)

    def publish_gps(self, mine_id: str, truck_id: str, payload: Dict[str, Any]):
        topic = f"mine/{mine_id}/truck/{truck_id}/gps"
        self._publish(topic, payload)

    def publish_alert(self, mine_id: str, payload: Dict[str, Any]):
        topic = f"mine/{mine_id}/alerts"
        self._publish(topic, payload)

    def _publish(self, topic: str, payload: Dict[str, Any]):
        try:
            msg_str = json.dumps(payload)
            if self.is_connected:
                self.client.publish(topic, msg_str)
        except Exception as e:
            logger.debug(f"MQTT publish to {topic} skipped: {e}")

# Global MQTT manager instance
mqtt_manager = MQTTManager()
