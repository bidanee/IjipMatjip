import pandas as pd
from infrastructure_analyzer import InfrastructureAnalyzer
from tqdm import tqdm
import numpy as np

def precompute_scores():
    print("전체 동네 인프라 및 가격 점수 계산을 시작합니다...")

    # 1. 필요한 모든 데이터 로드
    infra_analyzer = InfrastructureAnalyzer()
    dong_df = pd.read_csv('./datas/encoding_dong_code.csv', encoding='utf-8-sig')
    trade_df = pd.read_csv('./datas/seoul_transactions_202306.csv', encoding='utf-8-sig')

    # --- 👇 실제 CSV 파일의 컬럼명으로 수정 ---
    # 1. '시군구' 컬럼에서 동 이름만 추출하여 새 컬럼 'dong_name' 생성
    trade_df['dong_name'] = trade_df['시군구'].str.split().str[2]
    
    # 2. 숫자여야 하는 컬럼들을 숫자 형태로 변환
    trade_df['전용면적(㎡)'] = pd.to_numeric(trade_df['전용면적(㎡)'], errors='coerce')
    trade_df['거래금액(만원)'] = pd.to_numeric(trade_df['거래금액(만원)'].str.replace(',', ''), errors='coerce')
    trade_df.dropna(subset=['전용면적(㎡)', '거래금액(만원)'], inplace=True)
    # --- 여기까지 수정 ---

    results = []

    for index, row in tqdm(dong_df.iterrows(), total=len(dong_df), desc="동네별 점수 계산 중"):
        dong_name = row['읍면동명']
        latitude = row['Y']
        longitude = row['X']

        nearby_schools = infra_analyzer.find_nearby(latitude, longitude, 1.0, 'school')
        nearby_subways = infra_analyzer.find_nearby(latitude, longitude, 1.0, 'subway')

        # --- 👇 새로 만든 'dong_name' 컬럼을 사용하도록 수정 ---
        current_dong_trades = trade_df[trade_df['dong_name'] == dong_name]
        target_size_trades = current_dong_trades[
            (current_dong_trades['전용면적(㎡)'] >= 59) & (current_dong_trades['전용면적(㎡)'] < 60)
        ]
        avg_price = target_size_trades['거래금액(만원)'].mean()
        # --- 여기까지 수정 ---
        
        if pd.isna(avg_price):
            avg_price = 0

        results.append({
            'dong': dong_name,
            'school_count': len(nearby_schools),
            'subway_count': len(nearby_subways),
            'avg_price': int(avg_price)
        })

    result_df = pd.DataFrame(results)
    
    # 정규화 로직 (이하 동일)
    min_schools = result_df['school_count'].min()
    max_schools = result_df['school_count'].max()
    min_subways = result_df['subway_count'].min()
    max_subways = result_df['subway_count'].max()
    price_filtered_df = result_df[result_df['avg_price'] > 0]
    min_price = price_filtered_df['avg_price'].min()
    max_price = price_filtered_df['avg_price'].max()

    def normalize(value, min_val, max_val):
        if (max_val - min_val) > 0:
            return round(((value - min_val) / (max_val - min_val)) * 100, 2)
        return 50.0

    result_df['school_score'] = result_df['school_count'].apply(lambda x: normalize(x, min_schools, max_schools))
    result_df['subway_score'] = result_df['subway_count'].apply(lambda x: normalize(x, min_subways, max_subways))
    result_df['price_score'] = result_df['avg_price'].apply(
        lambda x: 100 - normalize(x, min_price, max_price) if x > 0 else 0
    )

    print("\n--- 최종 점수 계산 완료 (상위 5개) ---")
    print(result_df.head())

    result_df.to_csv('./datas/neighborhood_final_scores_v2.csv', index=False)
    print("\n최종 점수 결과를 './datas/neighborhood_final_scores_v2.csv' 파일로 저장했습니다.")


if __name__ == '__main__':
    precompute_scores()