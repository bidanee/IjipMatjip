import os
import joblib
import pandas as pd
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from model_utils import train_and_save_model

app = FastAPI()
loaded_models = {}

class HouseInfo(BaseModel):
  region_code: str # 지역 코드 추가
  area: float
  floor: int
  build_year: int

@app.post("/predict")
def predict_price(info: HouseInfo):
  model_filename = f"real_estate_model_{info.region_code}.pkl"
  
  # 1. 메모리에 모델이 있는지 확인
  if model_filename in loaded_models:
    model = loaded_models[model_filename]
  else:
    # 2. 파일로 저장된 모델이 있는지 확인
    if not os.path.exists(model_filename):
      # 3. 모델이 없으면 새로 학습 후 저장
      success = train_and_save_model(info.region_code)
      if not success:
        raise HTTPException(status_code=404, detail=f"{info.region_code} 지역의 데이터를 찾을 수 없거나 모델을 생성할 수 없습니다.")
      # 4. 파일에서 모델을 불러와 메모리에 저장
      model = joblib.load(model_filename)
      loaded_models[model_filename] = model
      print(f"'{model_filename}' 모델을 로드했습니다.")
      
  # 예측 수행
  current_year = time.localtime().tm_year
  age = current_year - info.build_year
  input_data = pd.DataFrame([[info.area, info.floor, age]], columns=['area','floor','age'])
  
  prediction = model.predict(input_data)
  
  return {"predicted_price" : prediction[0]}