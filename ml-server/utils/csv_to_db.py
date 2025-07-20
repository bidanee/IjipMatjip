import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv

def migrate_csv_to_db():
  """
    csv 파일을 읽어 PostgreSQL DB에 테이블을 만들고 데이터 삽입
  """
  load_dotenv()
  
  conn = None
  try:
    # 1. 데이터베이스에 연결
    conn = psycopg2.connect(
      host=os.getenv("DB_HOST"),
      port=os.getenv("DB_PORT"),
      dbname=os.getenv("DB_NAME"),
      user=os.getenv("DB_USER"),
      password=os.getenv("DB_PASSWORD")
    )
    cur = conn.cursor()
    print("데이터 베이스 연결 성공")
    
    # 2. 테이블 생성 SQL (transactions 테이블 추가)
    create_tables_sql = """
    DROP TABLE IF EXISTS schools, subways, neighborhood_scores, transactions;
    
    CREATE TABLE schools (
      id SERIAL PRIMARY KEY,
      name VARCHAR(255),
      latitude DOUBLE PRECISION,
      longitude DOUBLE PRECISION,
      geom GEOMETRY(Point, 4326)
    );
    
    CREATE TABLE subways (
      id SERIAL PRIMARY KEY,
      name VARCHAR(255),
      latitude DOUBLE PRECISION,
      longitude DOUBLE PRECISION,
      geom GEOMETRY(Point, 4326)
    );
    
    CREATE TABLE neighborhood_scores(
      id SERIAL PRIMARY KEY,
      dong VARCHAR(255),
      sigungu_name VARCHAR(255),
      school_count INTEGER,
      subway_count INTEGER,
      avg_price BIGINT,
      school_score FLOAT,
      subway_score FLOAT,
      price_score FLOAT,
      latitude DOUBLE PRECISION,
      longitude DOUBLE PRECISION
    );
    
    CREATE TABLE transactions(
      id SERIAL PRIMARY KEY,
      sigungu VARCHAR(255),
      dong_name VARCHAR(255),
      complex_name VARCHAR(255),
      area FLOAT,
      price INTEGER,
      floor INTEGER,
      build_year INTEGER
    );
    """
    cur.execute(create_tables_sql)
    print("테이블 생성 완료")
    
    # 3. CSV 데이터 DB에 삽입
    print("CSV 파일을 DB에 삽입 중...")
    
    # 학교 데이터
    school_df = pd.read_csv('../datas/encoding_schools.csv', encoding='utf-8-sig')
    for index, row in school_df.iterrows():
      cur.execute(
        "INSERT INTO schools (name, latitude, longitude, geom) VALUES (%s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))",(row['학교명'],row['위도'], row['경도'], row['경도'], row['위도'])
      )
    print("학교 데이터 삽입 완료")
    
    # 지하철역 데이터
    subway_df = pd.read_csv('../datas/subway_combined.csv', encoding='utf-8-sig')
    for index, row in subway_df.iterrows():
      cur.execute(
        "INSERT INTO subways (name, latitude, longitude, geom) VALUES (%s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))",(row['역명'],row['위도'], row['경도'], row['경도'], row['위도'])
      )    
    print("지하철역 데이터 삽입 완료")
    
    # 동네 점수 데이터
    scores_df = pd.read_csv('../datas/neighborhood_final_scores.csv')
    for index, row in scores_df.iterrows():
      cur.execute(
        """
        INSERT INTO neighborhood_scores (dong, sigungu_name, school_count, subway_count, avg_price, school_score, subway_score, price_score, latitude, longitude) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (row['dong'], row['sigungu'], row['school_count'], row['subway_count'], row['avg_price'], row['school_score'], row['subway_score'], row['price_score'], row.get('latitude'), row.get('longitude'))
      )
    print("동네 점수 데이터 삽입 완료")
    
    # --- 거래 데이터 삽입 로직 ---
    trade_df = pd.read_csv('../datas/seoul_transactions_202306.csv', encoding='utf-8-sig')
    trade_df['dong_name'] = trade_df['시군구'].str.split().str[2]
    trade_df['전용면적(㎡)'] = pd.to_numeric(trade_df['전용면적(㎡)'], errors='coerce')
    trade_df['거래금액(만원)'] = pd.to_numeric(trade_df['거래금액(만원)'].str.replace(',', ''), errors='coerce')
    trade_df.dropna(subset=['전용면적(㎡)', '거래금액(만원)','건축년도','층','단지명'], inplace=True)
    
    for index, row in trade_df.iterrows():
      cur.execute(
        """
        INSERT INTO transactions (sigungu, dong_name, complex_name, area, price, floor, build_year) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (row['시군구'], row['dong_name'], row['단지명'], row['전용면적(㎡)'], row['거래금액(만원)'], row['층'], row['건축년도'])
      )
    print("거래 데이터 삽입 완료")
    
    # 4. 공간 인덱스 생성 (위치 기반 검색 속도 향상)
    create_index_sql = """
    CREATE INDEX schools_geom_idx ON schools USING GIST (geom);
    CREATE INDEX subways_geom_idx ON subways USING GIST (geom);
    """
    cur.execute(create_index_sql)
    print("공간 인덱스 생성 완료")
    
    # 변경사항 저장
    conn.commit()
  except Exception as e:
    # 에러 발생 시 롤백
    if conn:
      conn.rollback()
    print(f"데이터베이스 연결 중 오류 발생: {e}")
  finally:
    if conn:
      conn.close()
      print("데이터베이스 연결 해제 ")
      
if __name__ == '__main__':
  migrate_csv_to_db()