import os
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import logging

logger = logging.getLogger(__name__)

MODEL_PATH = os.environ.get("MODEL_PATH", "model/isolation_forest.pkl")
SCALER_PATH = os.environ.get("SCALER_PATH", "model/scaler.pkl")

class BotDetectorModel:
    """Isolation Forest 기반 봇 탐지 모델"""
    
    def __init__(self, contamination=0.1):
        """
        contamination: 전체 데이터에서 이상치(봇)의 예상 비율.
                        0.1이면 약 10%가 봇이라고 가정.
        """
        self.model = IsolationForest(
            n_estimators=100,         # 트리 개수
            contamination=contamination,
            max_samples='auto',
            random_state=42,
            n_jobs=-1                 # 모든 CPU 코어 사용
        )
        self.scaler = StandardScaler()
        self.is_fitted = False
        self.training_data = []       # 온라인 학습용 데이터 버퍼
        self.min_samples_for_fit = 500 # 최소 50개 샘플 후 학습 시작
        
        # 저장된 모델이 있으면 로드
        self._load_model()
    
    def _load_model(self):
        """저장된 모델 파일이 있으면 로드"""
        if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
                self.scaler = joblib.load(SCALER_PATH)
                self.is_fitted = True
                logger.info("✅ 저장된 모델 로드 완료")
            except Exception as e:
                logger.warning(f"모델 로드 실패, 새로 학습합니다: {e}")
    
    def _save_model(self):
        """모델을 파일로 저장"""
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        joblib.dump(self.model, MODEL_PATH)
        joblib.dump(self.scaler, SCALER_PATH)
        logger.info("💾 모델 저장 완료")
    
    def add_training_data(self, features: np.ndarray):
        """학습 데이터 버퍼에 추가 (온라인 학습)"""
        self.training_data.append(features.flatten())
        
        # 일정 샘플이 모이면 자동 재학습
        if len(self.training_data) >= self.min_samples_for_fit and not self.is_fitted:
            self.fit()
        elif len(self.training_data) >= self.min_samples_for_fit * 2 and self.is_fitted:
            # 이미 학습된 모델은 두 배 데이터가 모여야 재학습
            self.fit()

    
    def fit(self):
        """모델 학습 (혹은 재학습)"""
        if len(self.training_data) < self.min_samples_for_fit:
            logger.info(f"학습 데이터 부족: {len(self.training_data)}/{self.min_samples_for_fit}")
            return
        
        X = np.array(self.training_data)
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)
        self.is_fitted = True
        self._save_model()
        
        logger.info(f"🎓 모델 학습 완료 (샘플 수: {len(self.training_data)})")
        
        # 버퍼 비우기 (최근 일부만 유지)
        self.training_data = self.training_data[-100:]
    
    def predict(self, features: np.ndarray) -> tuple[bool, float]:
        """
        예측: 봇인지 판단
        Returns: (is_bot: bool, anomaly_score: float)
                 anomaly_score가 낮을수록 이상치 (봇)
        """
        if not self.is_fitted:
            return False, 0.0
        
        X_scaled = self.scaler.transform(features)
        
        # -1: 이상치(봇), 1: 정상
        prediction = self.model.predict(X_scaled)[0]
        
        # anomaly_score: 낮을수록 이상 (-1에 가까움)
        score = self.model.decision_function(X_scaled)[0]
        
        is_bot = prediction == -1
        return is_bot, float(score)
