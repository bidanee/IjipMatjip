import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv
from infrastructure_analyzer import InfrastructureAnalyzer
from tqdm import tqdm
import numpy as np

def get_db_connection():
  """DB 연결을 생성하는 함수"""
  conn = psycopg2.connect(
    host=os.getenv("DB_HOST"), port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"), user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
  )
  return conn

def precompute_scores_from_db():
    print("DB 데이터를 기반으로 전체 동네 인프라 및 가격 점수 계산을 시작합니다...")

    infra_analyzer = InfrastructureAnalyzer()
    dong_df = pd.read_csv('../datas/encoding_dong_code.csv', encoding='utf-8-sig')

    # --- 👇 DB에서 최신 매물 데이터를 직접 불러옵니다 ---
    conn = get_db_connection()
    try:
      # '전세'이면서 '원룸' 또는 '투룸'인 데이터만 가져옵니다.
      query = "SELECT address, price_deposit FROM estates WHERE deal_type = '전세' AND (room_type LIKE '%원룸%' OR room_type LIKE '%투룸%')"
      estates_df = pd.read_sql_query(query, conn)
      # 주소에서 '동' 이름만 추출
      estates_df['dong_name'] = estates_df['address'].str.split().str[2]
      print(f"✅ DB에서 {len(estates_df)}개의 전세 매물 데이터를 불러왔습니다.")
    finally:
        if conn:
            conn.close()
    # --- 여기까지 ---

    results = []

    for index, row in tqdm(dong_df.iterrows(), total=len(dong_df), desc="동네별 점수 계산 중"):
      dong_name = row['읍면동명']
      sigungu_name = row['시군구명']
      latitude = row['Y']
      longitude = row['X']

      nearby_schools = infra_analyzer.find_nearby(latitude, longitude, 1.0, 'school')
      nearby_subways = infra_analyzer.find_nearby(latitude, longitude, 1.0, 'subway')
      nearby_hospitals = infra_analyzer.find_nearby(latitude, longitude, 1.0, 'hospital')
      nearby_marts = infra_analyzer.find_nearby(latitude, longitude, 1.0, 'mart')
      nearby_parks = infra_analyzer.find_nearby(latitude, longitude, 1.0, 'park')

      # --- 👇 새로운 매물 데이터 기준으로 평균 전세가 계산 ---
      current_dong_estates = estates_df[estates_df['dong_name'] == dong_name]
      avg_price = current_dong_estates['price_deposit'].mean()
      if pd.isna(avg_price):
          avg_price = 0
      # --- 여기까지 ---

      results.append({
        'dong': dong_name,
        'sigungu_name': sigungu_name,
        'latitude': latitude,
        'longitude': longitude,
        'school_count': len(nearby_schools),
        'subway_count': len(nearby_subways),
        'hospital_count': len(nearby_hospitals), # hospital_count 추가
        'mart_count': len(nearby_marts),       # mart_count 추가
        'park_count': len(nearby_parks),      # park_count 추가
        'avg_price': int(avg_price) # 이제 이 가격은 '평균 전세 보증금'이 됩니다.
      })

    result_df = pd.DataFrame(results)
    
    # 정규화 로직 (이전과 동일)
    def normalize(series):
      min_val, max_val = series.min(), series.max()
      if pd.notna(min_val) and pd.notna(max_val) and (max_val - min_val) > 0:
          return round(((series - min_val) / (max_val - min_val)) * 100, 2)
      return 50.0
    
    for col in ['school_count', 'subway_count', 'hospital_count', 'mart_count', 'park_count']:
      result_df[col.replace('_count', '_score')] = normalize(result_df[col])
    
    price_filtered_df = result_df[result_df['avg_price'] > 0].copy()
    if not price_filtered_df.empty:
      price_filtered_df['price_score'] = 100 - normalize(price_filtered_df['avg_price'])
      result_df = result_df.merge(price_filtered_df[['dong', 'price_score']], on='dong', how='left')
      result_df['price_score'].fillna(0, inplace=True)
    else:
      result_df['price_score'] = 0

    print("\n--- 최종 점수 계산 완료 (상위 5개) ---")
    print(result_df.head())

    result_df.to_csv('../datas/neighborhood_final_scores.csv', index=False, encoding='utf-8-sig')
    print("\n최종 점수 결과를 '../datas/neighborhood_final_scores.csv' 파일로 저장했습니다.")

if __name__ == '__main__':
    precompute_scores_from_db()