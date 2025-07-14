import pandas as pd
from infrastructure_analyzer import InfrastructureAnalyzer
from tqdm import tqdm

def pre_scores():
  print("전체 동네 인프라 점수 계산을 시작합니다.")
  
  # 1. 인프라 분석기 및 동네 좌표 데이터 로드
  infra_analyzer = InfrastructureAnalyzer()
  dong_df = pd.read_csv('./datas/encoding_dong_code.csv', encoding='utf-8-sig')
  
  results = []
  
  # tqdm을 사용해 진행 상황을 시각적으로 표시
  for index, row in tqdm(dong_df.iterrows(), total=len(dong_df), desc="동네별 인프라 계산 중..."):
    dong_name = row['읍면동명']
    latitude = row['Y']
    longitude = row['X']
    
    # 2. 각 동네의 중심점에서 반경 1km 내 인프라 개수 계산
    nearby_schools =infra_analyzer.find_nearby(latitude, longitude, 1.0,'school')
    nearby_subways =infra_analyzer.find_nearby(latitude, longitude, 1.0,'subway')
    
    results.append({
      'dong': dong_name,
      'latitude': latitude,
      'longitude':longitude,
      'school_count':len(nearby_schools),
      'subway_count':len(nearby_subways)
    })
  
  # 3. 결과 확인
  result_df = pd.DataFrame(results)
  print("\n --- 인프라 개수 계산 완료(상위 5개) ---")
  print(result_df.head())

  # 4. 파일로 저장
  result_df.to_csv('./datas/neighborhood_raw_scores.csv', index=False)
  print("\n 계산 결과를 파일로 저장했습니다.")
  
if __name__ == '__main__':
  pre_scores()