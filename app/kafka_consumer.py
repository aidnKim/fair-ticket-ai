import json
import threading
import time
from kafka import KafkaConsumer
from detector import analyze
from kafka_producer import send_blocked_user

import os
KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC = "user-actions"
GROUP_ID = "ai-fraud-detector"
def start_consumer():
    consumer = None
    while consumer is None:
        try:
            consumer = KafkaConsumer(
                TOPIC,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                group_id=GROUP_ID,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                auto_offset_reset="latest"
            )
            print(f"✅ Kafka Consumer started on topic: {TOPIC}")
        except Exception as e:
            print(f"⏳ Kafka not ready, retrying in 5s... ({e})")
            time.sleep(5)
    
    for msg in consumer:
        event = msg.value
        print(f"📩 Received: {event.get('userEmail')} - {event.get('endpoint')}")
        
        is_suspicious, reason = analyze(event)
        
        if is_suspicious:
            user_id = event.get("userEmail") or event.get("sessionId")
            print(f"🚨 Suspicious detected: {user_id} - {reason}")
            send_blocked_user(user_id, reason)
def run_in_background():
    thread = threading.Thread(target=start_consumer, daemon=True)
    thread.start()