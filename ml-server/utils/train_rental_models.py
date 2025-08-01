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
    df_cleaned['sigungu'] = df['시군구'].apply(lambda x: str(x).split()[1] if isinstance(x, str) and len(x.split()) > 1 else None)
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
    
    df_apt = clean_data(pd.read_csv('../datas/rental_apartments.csv', encoding='utf-8-sig', low_memory=False), '아파트')
    df_dagagu = clean_data(pd.read_csv('../datas/rental_dagagu.csv', encoding='utf-8-sig', low_memory=False), '다가구')
    df_dasedae = clean_data(pd.read_csv('../datas/rental_dasedae.csv', encoding='utf-8-sig', low_memory=False), '다세대')
    df_officetel = clean_data(pd.read_csv('../datas/rental_officetel.csv', encoding='utf-8-sig', low_memory=False), '오피스텔')
    
    df_all = pd.concat([df_apt, df_dagagu, df_dasedae, df_officetel], ignore_index=True)
    df_all['floor'] = df_all['floor'].fillna(1)
    
    if len(df_all) > 150000:
        df_all = df_all.sample(n=150000, random_state=42)
    print(f"총 {len(df_all)}개의 샘플 데이터로 모델 학습을 시작합니다.")
    
    preprocessor = make_column_transformer(
        (OneHotEncoder(handle_unknown='ignore'), ['sigungu']),
        remainder='passthrough'
    )
    
    # 전세 모델 학습
    jeonse_df = df_all[df_all['rent'] == 0].copy()
    if not jeonse_df.empty:
        print("전세 모델 학습 시작...")
        X = jeonse_df[['area', 'build_year', 'floor', 'sigungu']]
        y = jeonse_df['deposit']
        
        jeonse_model = make_pipeline(
            preprocessor,
            RandomForestRegressor(n_estimators=30, max_depth=10, random_state=42, n_jobs=-1)
        )
        
        jeonse_model.fit(X, y)
        joblib.dump(jeonse_model, '../models/jeonse_model.pkl')
        print("전세 모델(jeonse_model.pkl) 저장 완료!")
    
    # 월세 모델 학습
    wolse_df = df_all[df_all['rent'] > 0].copy()
    if not wolse_df.empty:
        print("월세 모델 학습 시작...")
        X = wolse_df[['area', 'build_year', 'floor', 'deposit', 'sigungu']]
        y = wolse_df['rent']
        
        wolse_model = make_pipeline(
            preprocessor,
            RandomForestRegressor(n_estimators=30, max_depth=10, random_state=42, n_jobs=-1)
        )
        
        wolse_model.fit(X, y)
        joblib.dump(wolse_model, '../models/wolse_model.pkl')
        print("월세 모델(wolse_model.pkl) 저장 완료!")

if __name__ == '__main__':
    train_and_save_models()
