# import os
# import pandas as pd
# import psycopg2
# from dotenv import load_dotenv
# import requests
# import time

# def get_coords(address, api_key):
#   """
#   카카오 API를 호출하여 주소를 좌표로 변환하는 함수
#   """
#   url = "https://dapi.kakao.com/v2/local/search/address.json"
#   headers = {"Authorization": f"KakaoAK {api_key}"}
#   params = {"query": address}
#   try:
#     response = requests.get(url, headers=headers, params=params).json()
#     if response['documents']:
#       location = response['documents'][0]
#       return float(location['y']), float(location['x'])
#   except Exception as e:
#     print(f"주소 변환 실패: {address}, 오류: {e}")
#   return None, None

# def migrate_csv_to_db():
#   """
#     csv 파일을 읽어 PostgreSQL DB에 테이블을 만들고 데이터 삽입
#   """
#   load_dotenv()
#   conn = None
#   try:
#     # 1. 데이터베이스에 연결
#     conn = psycopg2.connect(
#       host=os.getenv("DB_HOST"),
#       port=os.getenv("DB_PORT"),
#       dbname=os.getenv("DB_NAME"),
#       user=os.getenv("DB_USER"),
#       password=os.getenv("DB_PASSWORD")
#     )
#     cur = conn.cursor()
#     print("데이터 베이스 연결 성공")
    
#     # 2. 테이블 생성 SQL (transactions 테이블 추가)
#     create_tables_sql = """
#     DROP TABLE IF EXISTS schools, subways, neighborhood_scores, transactions;
    
#     CREATE TABLE schools (
#       id SERIAL PRIMARY KEY,
#       name VARCHAR(255),
#       latitude DOUBLE PRECISION,
#       longitude DOUBLE PRECISION,
#       geom GEOMETRY(Point, 4326)
#     );
    
#     CREATE TABLE subways (
#       id SERIAL PRIMARY KEY,
#       name VARCHAR(255),
#       latitude DOUBLE PRECISION,
#       longitude DOUBLE PRECISION,
#       geom GEOMETRY(Point, 4326)
#     );
    
#     CREATE TABLE neighborhood_scores(
#       id SERIAL PRIMARY KEY,
#       dong VARCHAR(255),
#       sigungu_name VARCHAR(255),
#       school_count INTEGER,
#       subway_count INTEGER,
#       avg_price BIGINT,
#       school_score FLOAT,
#       subway_score FLOAT,
#       price_score FLOAT,
#       latitude DOUBLE PRECISION,
#       longitude DOUBLE PRECISION
#     );
    
#     CREATE TABLE transactions(
#       id SERIAL PRIMARY KEY,
#       sigungu VARCHAR(255),
#       dong_name VARCHAR(255),
#       complex_name VARCHAR(255),
#       area FLOAT,
#       price INTEGER,
#       floor INTEGER,
#       build_year INTEGER,
#       latitude DOUBLE PRECISION,
#       longitude DOUBLE PRECISION
#     );
#     """
#     cur.execute(create_tables_sql)
#     print("테이블 생성 완료")
    
#     # 3. CSV 데이터 DB에 삽입
#     print("CSV 파일을 DB에 삽입 중...")
    
#     # 학교 데이터
#     school_df = pd.read_csv('../datas/encoding_schools.csv', encoding='utf-8-sig')
#     for index, row in school_df.iterrows():
#       cur.execute(
#         "INSERT INTO schools (name, latitude, longitude, geom) VALUES (%s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))",(row['학교명'],row['위도'], row['경도'], row['경도'], row['위도'])
#       )
#     print("학교 데이터 삽입 완료")
    
#     # 지하철역 데이터
#     subway_df = pd.read_csv('../datas/subway_combined.csv', encoding='utf-8-sig')
#     for index, row in subway_df.iterrows():
#       cur.execute(
#         "INSERT INTO subways (name, latitude, longitude, geom) VALUES (%s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))",(row['역명'],row['위도'], row['경도'], row['경도'], row['위도'])
#       )    
#     print("지하철역 데이터 삽입 완료")
    
#     # 동네 점수 데이터
#     scores_df = pd.read_csv('../datas/neighborhood_final_scores.csv')
#     for index, row in scores_df.iterrows():
#       cur.execute(
#         """
#         INSERT INTO neighborhood_scores (dong, sigungu_name, school_count, subway_count, avg_price, school_score, subway_score, price_score, latitude, longitude) 
#         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#         """,
#         (row['dong'], row['sigungu_name'], row['school_count'], row['subway_count'], row['avg_price'], row['school_score'], row['subway_score'], row['price_score'], row.get('latitude'), row.get('longitude'))
#       )
#     print("동네 점수 데이터 삽입 완료")
    
#     # --- 거래 데이터 삽입 로직 ---
#     trade_df = pd.read_csv('../datas/seoul_transactions_202306.csv', encoding='utf-8-sig')
    
#     # 시군구에서 'dong_name'추출
#     trade_df['dong_name'] = trade_df['시군구'].str.split().str[2]
    
#     # '거래금액(만원)' 컬럼에서 쉼표 제거 후 숫자로 변환
#     trade_df['거래금액(만원)'] = pd.to_numeric(trade_df['거래금액(만원)'].str.replace(',',''), errors='coerce')
    
#     trade_df.dropna(subset=['거래금액(만원)','도로명'], inplace=True)
    
#     api_key = os.getenv("KAKAO_REST_API_KEY")
#     for index, row in trade_df.iterrows():
#       full_address = f"{row['시군구']} {row.get('도로명','')}"
#       lat, lng = get_coords(full_address, api_key)
#       if lat and lng:
#         cur.execute(
#           """
#           INSERT INTO transactions (sigungu, dong_name, complex_name, area, price, floor, build_year, latitude, longitude)
#           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
#           """,
#           (row['시군구'],row['dong_name'], row['단지명'], row['전용면적(㎡)'], row['거래금액(만원)'], row['층'], row['건축년도'], lat, lng)
#         )
#       time.sleep(0.05)
#     print("-> 거래 데이터 삽입 완료")
    
#     # 4. 공간 인덱스 생성 (위치 기반 검색 속도 향상)
#     create_index_sql = """
#     CREATE INDEX schools_geom_idx ON schools USING GIST (geom);
#     CREATE INDEX subways_geom_idx ON subways USING GIST (geom);
#     """
#     cur.execute(create_index_sql)
#     print("공간 인덱스 생성 완료")
    
#     # 변경사항 저장
#     conn.commit()
#     print("모든 데이터가 성공적으로 DB에 저장되었습니다.")
#   except Exception as e:
#     if conn:
#       conn.rollback()
#     print(f"데이터베이스 연결 중 오류 발생: {e}")
#   finally:
#     if conn:
#       conn.close()
#       print("데이터베이스 연결 해제 ")
      
# if __name__ == '__main__':
#   migrate_csv_to_db()


import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv

def migrate_csv_to_db():
    load_dotenv()
    conn = None
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"), port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"), user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        cur = conn.cursor()
        print("✅ DB 연결 성공")

        # 테이블 생성 SQL
        create_tables_sql = """
        DROP TABLE IF EXISTS schools, subways;
        CREATE TABLE schools (
            id SERIAL PRIMARY KEY, name VARCHAR(255),
            latitude DOUBLE PRECISION, longitude DOUBLE PRECISION,
            geom GEOGRAPHY(Point, 4326)
        );
        CREATE TABLE subways (
            id SERIAL PRIMARY KEY, name VARCHAR(255),
            latitude DOUBLE PRECISION, longitude DOUBLE PRECISION,
            geom GEOGRAPHY(Point, 4326)
        );
        """
        cur.execute(create_tables_sql)
        print("✅ schools, subways 테이블 생성 완료")

        print("CSV 데이터 삽입을 시작합니다...")
        
        # 학교 데이터 (INSERT 문 수정)
        school_df = pd.read_csv('../datas/encoding_schools.csv', encoding='utf-8-sig')
        # 위도, 경도 값이 없는 데이터 제거
        school_df.dropna(subset=['위도', '경도'], inplace=True)
        for index, row in school_df.iterrows():
            # 👇 ST_SetSRID(ST_MakePoint(경도, 위도), 4326) 를 사용해 geom 컬럼 채우기
            cur.execute(
                "INSERT INTO schools (name, latitude, longitude, geom) VALUES (%s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))",
                (row['학교명'], row['위도'], row['경도'], row['경도'], row['위도'])
            )
        print("-> 학교 데이터 삽입 완료")
        
        # 지하철 데이터 (INSERT 문 수정)
        subway_df = pd.read_csv('../datas/subway_combined.csv', encoding='utf-8-sig')
        subway_df.dropna(subset=['위도', '경도'], inplace=True)
        for index, row in subway_df.iterrows():
            cur.execute(
                "INSERT INTO subways (name, latitude, longitude, geom) VALUES (%s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))",
                (row['역명'], row['위도'], row['경도'], row['경도'], row['위도'])
            )
        print("-> 지하철 데이터 삽입 완료")
        
        # 공간 인덱스 생성
        create_index_sql = """
        CREATE INDEX schools_geom_idx ON schools USING GIST (geom);
        CREATE INDEX subways_geom_idx ON subways USING GIST (geom);
        """
        cur.execute(create_index_sql)
        print("✅ 공간 인덱스 생성 완료")

        conn.commit()
        print("🎉 인프라 데이터가 성공적으로 DB에 저장되었습니다.")

    except Exception as e:
        if conn: conn.rollback()
        print(f"오류 발생: {e}")
    finally:
        if conn: conn.close()
        print("데이터베이스 연결 해제")

if __name__ == '__main__':
    # 참고: 이 스크립트는 이제 인프라 데이터만 처리합니다.
    migrate_csv_to_db()