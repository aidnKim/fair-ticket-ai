import json
import os
from kafka import KafkaProducer

KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC = "blocked-users"

# 1. 처음엔 무조건 연결하지 않고 비워둠 (None)
producer = None

# 2. 프로듀서를 가져오는 함수를 새로 만듬
def get_producer():
    global producer
    # 만약 프로듀서가 비어있다면, 그때서야 처음으로 생성(연결)
    if producer is None:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )
    return producer

# 3. 메시지 보내는 함수
def send_blocked_user(user_id: str, reason: str):
    message = {
        "userId": user_id,
        "reason": reason
    }
    # 이제 그냥 producer 대신에 get_producer()를 호출해서 사용
    get_producer().send(TOPIC, message)
    get_producer().flush()
    print(f"📤 Blocked user sent: {user_id}")