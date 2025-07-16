import os
import joblib
import pandas as pd
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict

from model_utils import train_and_save_model
from infrastructure_analyzer import InfrastructureAnalyzer

app = FastAPI()

# 전역 변수 선언
loaded_models = {}
infra_analyzer = None
neighborhood_score_df = None # 동네 점수 데이터를 저장할 변수

# 서버 시작 시 인프라 데이터 미리 로드
@app.on_event("startup")
def startup_event():
  global infra_analyzer, neighborhood_score_df
  infra_analyzer = InfrastructureAnalyzer()
  
  # 미리 계산된 동네 점수 파일 로드
  try:
    neighborhood_score_df = pd.read_csv('./datas/neighborhood_final_scores_v2.csv')
    print("동네 점수 데이터 로딩 완료.")
  except FileNotFoundError:
    print("경고 : 'neighborhood_final_scores_v2.csv' 파일을 찾을 수 없습니다.")

# Pydantic 모델 정의
class HouseInfo(BaseModel):
  region_code: str
  area: float
  floor: int
  build_year: int
  
class InfraQuery(BaseModel):
  latitude: float
  longitude: float
  radius_km: float
  
class RecommendationRequest(BaseModel):
  preferences: List[str] # "school", "subway","price" 등 선호 조건 리스트 
  
# API 엔드 포인트
@app.post("/predict")
def predict_price(info:HouseInfo):
  model_filename = f"real_estate_model_{info.region_code}.pkl"
  if model_filename in loaded_models:
    model = loaded_models[model_filename]
  else:
    if not os.path.exists(model_filename):
      success = train_and_save_model(info.region_code)
      if not success:
        raise HTTPException(status_code=404, detail=f"{info.region_code} 지역의 데이터를 찾을 수 없거나 모델을 생성 할 수 없습니다.")
    model = joblib.load(model_filename)
    loaded_models[model_filename] = model
    print(f"'{model_filename}' 모델을 로드했습니다.")
  
  current_year = time.localtime().tm_year
  age = current_year -info.build_year
  input_data = pd.DataFrame([[info.area, info.floor, age]], columns=['area','floor','age'] )
  prediction = model.predict(input_data)
  return {"predicted_price": prediction[0]}

@app.post("/infrastructure")
def get_nearby_infrastructure(query: InfraQuery) -> Dict[str, List]:
  if not infra_analyzer:
    raise HTTPException(status_code=503, detail="인프라 분석기가 아직 준비되지 않았습니다.")
  
  # 주변 학교 검색
  nearby_schools = infra_analyzer.find_nearby(
    lat=query.latitude,
    lon=query.longitude,
    radius_km=query.radius_km,
    infra_type='school'
  )
  
  # 주변 지하철역 검색
  nearby_subways = infra_analyzer.find_nearby(
    lat=query.latitude,
    lon=query.longitude,
    radius_km=query.radius_km,
    infra_type='subway'
  )
  
  return {
    "schools": nearby_schools,
    "subways": nearby_subways
  }
  
@app.post("/recommend/neighborhood")
def recommend_neighborhood(request: RecommendationRequest):
  if neighborhood_score_df is None:
    raise HTTPException(status_code=503, detail="추천 데이터가 준비되지 않았습니다.")
  
  df = neighborhood_score_df.copy()
  
  # 총점 계산
  df['total_score'] = 0
  for pre in request.preferences:
    score_col = f'{pre}_score' 
    if score_col in df.columns:
      df['total_score'] += df[score_col]
      
  # 총점이 높은 순으로 정렬
  recommended_dongs = df.sort_values(by='total_score', ascending=False)
  
  # 상위 5개 결과 반환
  return recommended_dongs.head(5).to_dict('records')
  
  
  
  