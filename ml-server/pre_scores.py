import pandas as pd
from infrastructure_analyzer import InfrastructureAnalyzer
from tqdm import tqdm

def pre__scores():
  print("전체 동네 인프라 점수 계산을 시작합니다.")
  
  # 1. 인프라 분석기 및 동네 좌표 데이터 로드
  infra_analyzer = InfrastructureAnalyzer()
  dong_df = pd.read_csv('./datas/encoding_dong_code.csv', encoding='utf-8-sig')
  
  results = []
  
  for index, row in tqdm(dong_df.iterrows(), total=len(dong_df), desc="동네별 인프라 개수 계산 중.."):
    dong_name = row['읍면동명']
    latitude = row['Y']
    longitude = row['X']
    
    nearby_school = infra_analyzer.find_nearby(latitude, longitude, 1.0, 'school')
    nearby_subways = infra_analyzer.find_nearby(latitude,longitude, 1.0, 'subway')
    
    results.append({
      'dong':dong_name,
      'school_count': len(nearby_school),
      'subway_count': len(nearby_subways)
    })
    
  result_df = pd.DataFrame(results)
  
  # --- 정규화 로직 추가 ---
  print("\n 인프라 점수 정규화를 시작합니다.")
  
  # 2. 각 항목의 최소값, 최대값 계산
  min_schools = result_df['school_count'].min()
  max_schools = result_df['school_count'].max()
  min_subways = result_df['subway_count'].min()
  max_subways = result_df['subway_count'].max()
  
  # 3. 정규화 점수 계산 (0~100점)
  # 최대값과 최소값이 같을 경우 (모든 동네의 개수가 같을 경우) 0으로 나누는 것을 방지
  if (max_schools - min_schools) > 0:
    result_df['school_score'] = round(((result_df['school_count'] - min_schools) / (max_schools - min_schools)) * 100, 2)
  else:
    result_df['school_score'] = 50.0 # 모든 값이 같은 경우 중간값인 50점 부여
  
  if (max_subways - min_subways) > 0:
    result_df['subway_score'] = round(((result_df['subway_count'] - min_subways) / (max_subways - min_subways)) * 100, 2)
  else:
    result_df['subway_score'] = 50.0
    
  print("\n --- 최종 점수 계산 완료 (상위 5개) ---")
  print(result_df.head())
  
  # 4. 최종 결과 파일로 저장
  result_df.to_csv('./datas/neighborhood_final_scores.csv', index=False)
  print("\n최종점수 결과를 파일로 저장했습니다.")
  
if __name__ == '__main__':
  pre__scores()
    