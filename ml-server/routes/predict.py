from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import joblib
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, '..', 'models')
jeonse_path = os.path.join(MODEL_DIR, 'jeonse_model.pkl')
wolse_path = os.path.join(MODEL_DIR, 'wolse_model.pkl')
router = APIRouter()

# --- 모델 로드 ---
try:
  jeonse_model = joblib.load(jeonse_path)
  wolse_model = joblib.load(wolse_path)
  print(" 전월세 모델 로딩 완료")
except FileNotFoundError as e:
  jeonse_model = None
  wolse_model = None
  print(f" 전월세 예측 모델 파일을 찾을 수 없습니다 {e}")
  
# --- Pydantic 모델 정의 ---
class RentalInfo(BaseModel):
  area: float
  build_year: int
  floor: int
  sigungu: str
  deposit: int = 0
  
# --- API 엔드포인트 ---
@router.post("/rental")
def predict_rental_price(info: RentalInfo):
  if not jeonse_model or not wolse_model:
    raise HTTPException(status_code=503, detail="모델이 준비되지 않았습니다.")
  
  input_df = pd.DataFrame([info.model_dump()])
  
  # 전세가 예측
  predicted_jeonse = jeonse_model.predict(input_df[['area', 'build_year', 'floor', 'sigungu']])[0]
  
  # 월세 예측
  predicted_wolse = wolse_model.predict(input_df[['area', 'build_year', 'floor', 'deposit','sigungu']])[0]
  
  return {
    "predicted_jeonse_deposit": round(predicted_jeonse, -2), # 100 단위로 반올림
    "predicted_wolse_rent": round(predicted_wolse)
  }