import os
import joblib
import pandas as pd
import psycopg2
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from dotenv import load_dotenv

from model_utils import train_and_save_model
from infrastructure_analyzer import InfrastructureAnalyzer

app = FastAPI()
load_dotenv()

# 전역 변수 선언
loaded_models = {}
infra_analyzer = None

# --- DB 정보를 반환하는 함수 ---
def get_db_connection():
  conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
  )
  return conn

# --- 서버 시작 시 인프라 분석기만 초기화 ---
@app.on_event("startup")
def startup_event():
  global infra_analyzer
  infra_analyzer = InfrastructureAnalyzer()
  
# --- Pydantic 모델 정의 ---
class HouseInfo(BaseModel):
  region_code: str
  area: float
  floor: int
  build_year: int

class InfraQuery(BaseModel):
  latitude: float
  longitude: float
  radius_km: float

class Budget(BaseModel):
  min: int | None = None
  max: int | None = None
  
class RecommendationRequest(BaseModel):
    preferences: List[str]
    budget: Budget | None = None

# --- API 엔드포인트 정의 ---
@app.post("/predict")
def predict_price(info:HouseInfo):
  model_filename = f"real_estate_model_{info.region_code}.pkl"
  if model_filename in loaded_models:
    model = loaded_models[model_filename]
  else:
    if not os.path.exists(model_filename):
      success = train_and_save_model(info.region_code)
    if not success:
      raise HTTPException(status_code=404, detail=f"{info.region_code} 지역의 데이터를 찾을 수 없거나 모델을 생성할 수 없습니다.")
    model = joblib.load(model_filename)
    loaded_models[model_filename] = model
    print(f"'{model_filename}' 모델을 로드했습니다.")
  
  current_year = time.localtime().tm_year
  age = current_year - info.build_year
  input_data = pd.DataFrame([[info.area, info.floor, age]], columns=['area','floor','age'])
  prediction = model.predict(input_data)
  return {"predicted_price": prediction[0]}

@app.post("infrastructure")
def get_nearby_infrastructure(query: InfraQuery) -> Dict[str, List]:
  if not infra_analyzer:
    raise HTTPException(status_code=503, detail="인프라 분석기가 아직 준비되지 않았습니다.")
  
  # 주변 학교 검색
  nearby_schools = infra_analyzer.find_nearby(
    lat=query.latitude,
    lng=query.longitude,
    radius_km=query.radius_km,
    infra_type='school'
  )
  # 주변 지하철 검색
  nearby_subways = infra_analyzer.find_nearby(
    lat=query.latitude,
    lng=query.longitude,
    radius_km=query.radius_km,
    infra_type='subway'
  )
  
  return{
    "schools": nearby_schools,
    "subways": nearby_subways
  }
  
@app.post("/recommend/neighborhood")
def recommend_neighborhood(request: RecommendationRequest):
  conn = get_db_connection()
  recommendations = []
  try:
    with conn.cursor() as cur:
      # 1. 사용자의 선호도에 따라 동적으로 SQL 쿼리 생성
      score_clauses = []
      for pref in request.preferences:
        score_col = f'{pref}_score'
        # 컬럼있는지 확인
        if score_col in ['school_score', 'subway_score', 'price_score']:
          score_clauses.append(score_col)
      total_score_sql = " + ".join(score_clauses) if score_clauses else "school_score"

      # 2. 예산 필터링 쿼리 추가
      where_clauses = []
      params = []
      if request.budget:
        if request.budget.min is not None:
          where_clauses.append("avg_price >= %s")
          params.append(request.budget.min)
        if request.budget.max is not None:
          where_clauses.append("avg_price <= %s")
          params.append(request.budget.max)
          
      
      where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
      
      # 3. 최종 SQL 쿼리 조합 및 실행
      query = f"""
      SELECT *, ({total_score_sql}) AS total_score
      FROM neighborhood_scores
      {where_sql}
      ORDER BY total_score DESC
      LIMIT 5;
      """
      cur.execute(query, tuple(params))
      
      # 4. 결과를 JSON 형태로 변환
      columns = [desc[0] for desc in cur.description] 
      for row in cur.fetchall():
        recommendations.append(dict(zip(columns, row)))
        
      return recommendations
    
  except Exception as e:
    print(f"추천 API 처리 중 오류 발생: {e}")  
    raise HTTPException(status_code=500, detail="추천 정보를 받아오는 데 실패했습니다.")
  finally:
    if conn:
      conn.close()
  