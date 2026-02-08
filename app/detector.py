from collections import defaultdict
from datetime import datetime, timedelta

# 메모리 내 사용자 행동 기록
user_history = defaultdict(list)

def analyze(event: dict) -> tuple[bool, str]:
    """비정상 패턴 분석, True면 차단 대상"""
    ip = event.get("ipAddress")
    now = datetime.now()
    
    # 기록 추가
    user_history[ip].append({
        "timestamp": now,
        "endpoint": event.get("endpoint"),
        "sessionId": event.get("sessionId")
    })
    
    # 10초 이내 기록만 유지
    user_history[ip] = [
        h for h in user_history[ip] 
        if now - h["timestamp"] < timedelta(seconds=10)
    ]
    
    recent = user_history[ip]
    
    # 패턴 1: Burst (10초 내 20회)
    if len(recent) >= 20:
        return True, "burst_request"
    
    # 패턴 2: Session Hopping
    null_sessions = sum(1 for h in recent if not h["sessionId"])
    if null_sessions >= 5:
        return True, "session_hopping"
    
    # 패턴 3: Endpoint Scan
    unique_endpoints = len(set(h["endpoint"] for h in recent))
    if unique_endpoints >= 5 and len(recent) >= 5:
        return True, "endpoint_scan"
    
    return False, ""
