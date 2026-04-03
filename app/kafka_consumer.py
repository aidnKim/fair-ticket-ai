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

# 이미 차단한 유저를 기억하는 set
blocked_users = set()

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
        user_id = event.get("userEmail") or event.get("sessionId")
        
        # 이미 차단된 유저면 스킵
        if user_id in blocked_users:
            continue
        
        is_suspicious, reason = analyze(event)
        
        if is_suspicious:
            blocked_users.add(user_id)
            print(f"🚨 Suspicious detected: {user_id} - {reason}")
            send_blocked_user(user_id, reason)
        else:
            # 디버깅용: 정상으로 판단된 경우도 출력
            print(f"✅ Normal: {user_id}")

    # 루프 밖에는 안 되고, 위 else 아래에 아래 줄도 추가
    # (전체 차단 현황 확인)
    print(f"📊 현재 차단 목록 ({len(blocked_users)}명): {blocked_users}")


def run_in_background():
    thread = threading.Thread(target=start_consumer, daemon=True)
    thread.start()
