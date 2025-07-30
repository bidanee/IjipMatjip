import pandas as pd
from sklearn.compose import make_column_transformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder
import joblib

def clean_data(df, type_name):
  """데이터프레임을 표준 형식으로 정리하는 함수"""
  df_cleaned = pd.DataFrame()
  
  # 시군구 정보에서 '구' 이름만 추출
  df_cleaned['sigungu'] = df['시군구'].str.split().str[1]
  # 공통 컬럼 매핑
  df_cleaned['type'] = type_name
  area_col_name = '전용면적(㎡)' if '전용면적(㎡)' in df.columns else '계약면적(㎡)'
  df_cleaned['area'] = pd.to_numeric(df[area_col_name], errors='coerce')
  df_cleaned['deposit'] = pd.to_numeric(df['보증금(만원)'].astype(str).str.replace(',',''), errors='coerce')
  df_cleaned['rent'] = pd.to_numeric(df['월세금(만원)'].astype(str).str.replace(',',''), errors='coerce')
  df_cleaned['build_year'] = pd.to_numeric(df['건축년도'], errors='coerce')
  df_cleaned['floor'] = pd.to_numeric(df.get('층'), errors='coerce')
  
  # 결측치(NaN) 제거
  df_cleaned.dropna(subset=['sigungu','area', 'deposit', 'rent', 'build_year'], inplace=True)
  return df_cleaned

def train_and_save_models():
  print("4종류의 전월세 데이터 로딩 및 통합...")
  
  # 각 CSV 파일 로드 및 정리
  df_apt = clean_data(pd.read_csv('../datas/rental_apartments.csv', encoding='utf-8-sig', low_memory=False), '아파트')
  df_dagagu = clean_data(pd.read_csv('../datas/rental_dagagu.csv', encoding='utf-8-sig', low_memory=False), '다가구')
  df_dasedae = clean_data(pd.read_csv('../datas/rental_dasedae.csv', encoding='utf-8-sig', low_memory=False), '다세대')
  df_officetel = clean_data(pd.read_csv('../datas/rental_officetel.csv', encoding='utf-8-sig', low_memory=False), '오피스텔')
  
  # 모든 데이터 하나로 합치기
  df_all = pd.concat([df_apt, df_dagagu, df_dasedae, df_officetel], ignore_index=True)
  df_all['floor'] = df_all['floor'].fillna(1) # 층 정보가 없는 경우 1층으로 간주
  
  # 메모리 부족 문제를 해결하기 위해, 전체 데이터 중 20만개만 무작위로 샘플링하여 사용
  if len(df_all) > 200000:
      df_all = df_all.sample(n=200000, random_state=42)
  print(f"총 {len(df_all)}개의 샘플 데이터로 모델 학습을 시작합니다.")
  
  # 전처리 파이프라인 설정 : 'sigungu' 컬럼은 OneHot-Encoding, 나머지는 그대로 통과
  preprocessor = make_column_transformer(
    (OneHotEncoder(handle_unknown='ignore'),['sigungu']),
    remainder='passthrough'
  )
  
  # 1. 전세 모델 학습 (월세가 0인 경우)
  jeonse_df = df_all[df_all['rent'] == 0].copy()
  if not jeonse_df.empty:
    print("전세 모델 학습 시작...")
    X = jeonse_df[['area', 'build_year', 'floor','sigungu']]
    y = jeonse_df['deposit']
    
    jeonse_model = make_pipeline(
      preprocessor,
      RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    )
    
    jeonse_model.fit(X,y)
    joblib.dump(jeonse_model, '../models/jeonse_model.pkl')
    print("위치 정보 포함 전세 모델(jeonse_model.pkl) 저장 완료!")
    
  # 2. 월세 모델 학습 (월세가 0보다 큰 경우)
  wolse_df = df_all[df_all['rent'] > 0].copy()
  if not wolse_df.empty:
    print("월세 모델 학습 시작...")
    X = wolse_df[['area','build_year','floor', 'deposit','sigungu']]
    y = wolse_df['rent']
    
    wolse_model = make_pipeline(
      preprocessor,
      RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    )
    wolse_model.fit(X,y)
    joblib.dump(wolse_model, '../models/wolse_model.pkl')
    print("월세 모델(wolse_model.pkl) 저장 완료!")
    
if __name__ == '__main__':
  train_and_save_models()
  