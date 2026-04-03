from collections import defaultdict
from datetime import datetime, timedelta
import numpy as np

class FeatureExtractor:
    """사용자 행동 이벤트에서 ML 피처를 추출"""
    
    def __init__(self, window_seconds=30):
        self.window_seconds = window_seconds
        # IP별 이벤트 히스토리
        self.user_history = defaultdict(list)
    
    def add_event(self, event: dict):
        """이벤트를 히스토리에 추가하고 윈도우 밖 이벤트 정리"""
        ip = event.get("ipAddress")
        now = datetime.now()
        
        self.user_history[ip].append({
            "timestamp": now,
            "endpoint": event.get("endpoint"),
            "sessionId": event.get("sessionId"),
            "userEmail": event.get("userEmail"),
            "userAgent": event.get("userAgent"),
            "responseTimeMs": event.get("responseTimeMs", 0),
            "actionType": event.get("actionType"),
        })
        
        # 윈도우 밖 이벤트 정리
        cutoff = now - timedelta(seconds=self.window_seconds)
        self.user_history[ip] = [
            h for h in self.user_history[ip] if h["timestamp"] > cutoff
        ]
    
    def extract_features(self, ip: str) -> np.ndarray:
        """IP의 현재 윈도우 기준 피처 벡터 추출"""
        history = self.user_history.get(ip, [])
        
        if len(history) < 2:
            # 데이터 부족시 정상으로 간주할 수 있는 기본값
            return np.array([0, 0, 0, 0, 0, 0, 0, 0]).reshape(1, -1)
        
        timestamps = [h["timestamp"] for h in history]
        
        # === 피처들 ===
        
        # 1. 윈도우 내 총 요청 수
        request_count = len(history)
        
        # 2. 요청 간 평균 간격 (초) - 봇은 매우 일정한 간격
        intervals = [(timestamps[i+1] - timestamps[i]).total_seconds() 
                      for i in range(len(timestamps)-1)]
        avg_interval = np.mean(intervals) if intervals else 0
        
        # 3. 요청 간격의 표준편차 - 봇은 매우 낮음 (일정한 간격)
        std_interval = np.std(intervals) if len(intervals) > 1 else 0
        
        # 4. 고유 엔드포인트 수
        unique_endpoints = len(set(h["endpoint"] for h in history if h["endpoint"]))
        
        # 5. 고유 세션 수 (세션 호핑 감지)
        sessions = set(h["sessionId"] for h in history if h["sessionId"])
        unique_sessions = len(sessions)
        
        # 6. null 세션 비율
        null_session_ratio = sum(1 for h in history if not h["sessionId"]) / request_count
        
        # 7. 평균 응답 시간
        response_times = [h["responseTimeMs"] for h in history if h["responseTimeMs"]]
        avg_response_time = np.mean(response_times) if response_times else 0
        
        # 8. 특정 액션 타입 집중도 (엔트로피 기반)
        action_types = [h["actionType"] for h in history if h["actionType"]]
        if action_types:
            from collections import Counter
            counts = Counter(action_types)
            probs = np.array(list(counts.values())) / len(action_types)
            entropy = -np.sum(probs * np.log2(probs + 1e-10))
        else:
            entropy = 0
        
        features = np.array([
            request_count,
            avg_interval,
            std_interval,
            unique_endpoints,
            unique_sessions,
            null_session_ratio,
            avg_response_time,
            entropy,
        ]).reshape(1, -1)
        
        return features
