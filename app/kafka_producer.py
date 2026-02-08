import json
from kafka import KafkaProducer

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
TOPIC = "blocked-users"

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def send_blocked_user(user_id: str, reason: str):
    message = {
        "userId": user_id,
        "reason": reason
    }
    producer.send(TOPIC, message)
    producer.flush()
    print(f"📤 Blocked user sent: {user_id}")