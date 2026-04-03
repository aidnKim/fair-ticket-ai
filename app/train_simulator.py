"""
초기 모델 학습을 위한 시뮬레이터.
정상 사용자와 봇의 가짜 데이터를 생성하여 모델을 사전 학습시킵니다.
사용법: python train_simulator.py
"""
import random
import numpy as np
from ml_model import BotDetectorModel

def generate_normal_features(n=200):
    """정상 사용자 피처 생성"""
    data = []
    for _ in range(n):
        data.append([
            random.randint(1, 10),         # request_count: 적음
            random.uniform(1.0, 10.0),     # avg_interval: 느린 간격
            random.uniform(0.5, 5.0),      # std_interval: 불규칙 (사람)
            random.randint(1, 3),          # unique_endpoints: 적음
            1,                              # unique_sessions: 1개
            0.0,                            # null_session_ratio: 0
            random.uniform(100, 500),      # avg_response_time: 보통
            random.uniform(0.5, 2.0),      # entropy: 다양한 액션
        ])
    return np.array(data)

def generate_bot_features(n=30):
    """봇 피처 생성"""
    data = []
    for _ in range(n):
        data.append([
            random.randint(15, 50),        # request_count: 매우 많음
            random.uniform(0.01, 0.5),     # avg_interval: 매우 빠름
            random.uniform(0.0, 0.1),      # std_interval: 매우 일정 (기계적)
            random.randint(3, 10),         # unique_endpoints: 스캔
            random.randint(1, 5),          # unique_sessions: 호핑 가능
            random.uniform(0.3, 1.0),      # null_session_ratio: 높음
            random.uniform(10, 50),        # avg_response_time: 매우 빠름
            random.uniform(0.0, 0.5),      # entropy: 단일 액션 반복
        ])
    return np.array(data)

if __name__ == "__main__":
    model = BotDetectorModel(contamination=0.1)
    
    normal = generate_normal_features(200)
    bots = generate_bot_features(30)
    all_data = np.vstack([normal, bots])
    np.random.shuffle(all_data)
    
    for row in all_data:
        model.training_data.append(row)
    
    model.min_samples_for_fit = 50
    model.fit()
    
    # 검증
    print("\n=== 검증 ===")
    for i in range(5):
        feat = generate_normal_features(1)
        is_bot, score = model.predict(feat)
        print(f"정상 사용자 {i+1}: is_bot={is_bot}, score={score:.4f}")
    
    for i in range(5):
        feat = generate_bot_features(1)
        is_bot, score = model.predict(feat)
        print(f"봇 사용자 {i+1}: is_bot={is_bot}, score={score:.4f}")
    
    print("\n✅ 모델 사전 학습 완료! model/ 디렉토리에 저장됨")
