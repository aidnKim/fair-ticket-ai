import logging
from feature_extractor import FeatureExtractor
from ml_model import BotDetectorModel

logger = logging.getLogger(__name__)

# 전역 인스턴스
feature_extractor = FeatureExtractor(window_seconds=30)
model = BotDetectorModel(contamination=0.1)

# 모델 학습 전 fallback 룰 (기존 로직)
def _rule_based_check(ip: str) -> tuple[bool, str]:
    """모델 학습 전 사용할 기본 룰"""
    history = feature_extractor.user_history.get(ip, [])
    
    # 패턴 1: Burst (10초 내 20회)
    if len(history) >= 20:
        return True, "burst_request"
    
    # 패턴 2: Session Hopping
    null_sessions = sum(1 for h in history if not h["sessionId"] and not h.get("userEmail"))
    if null_sessions >= 10:
        return True, "session_hopping"
    
    # 패턴 3: Endpoint Scan
    unique_endpoints = len(set(h["endpoint"] for h in history if h["endpoint"]))
    if unique_endpoints >= 5 and len(history) >= 5:
        return True, "endpoint_scan"
    
    return False, ""


def analyze(event: dict) -> tuple[bool, str]:
    """
    AI 기반 비정상 패턴 분석.
    모델이 학습되지 않은 초기에는 룰 기반 fallback 사용.
    """
    ip = event.get("ipAddress")
    
    # 1. 이벤트 추가 & 피처 추출
    feature_extractor.add_event(event)
    features = feature_extractor.extract_features(ip)
    
    # 2. 학습 데이터로 축적
    model.add_training_data(features)
    
    # 3. 모델이 학습되었으면 ML 판단, 아니면 룰 기반
    if model.is_fitted:
        is_bot, score = model.predict(features)
        if is_bot:
            logger.info(f"🤖 ML 탐지: IP={ip}, score={score:.4f}")
            return True, f"ml_anomaly (score: {score:.4f})"
        return False, ""
    else:
        logger.debug("모델 미학습 상태, 룰 기반 fallback 사용")
        return _rule_based_check(ip)
