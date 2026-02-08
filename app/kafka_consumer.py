import json
import threading
from kafka import KafkaConsumer
from detector import analyze
from kafka_producer import send_blocked_user

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
TOPIC = "user-actions"
GROUP_ID = "ai-fraud-detector"

def start_consumer():
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=GROUP_ID,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="latest"
    )
    
    print(f"✅ Kafka Consumer started on topic: {TOPIC}")
    
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