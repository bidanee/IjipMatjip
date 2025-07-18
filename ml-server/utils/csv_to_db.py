import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv

def migrate_csv_to_db():
  """
    csv 파일을 읽어 PostgreSQL DB에 테이블을 만들고 데이터 삽입
  """
  # .env 파일에서 DB 접속 정보 로드
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
    
    # 2. 테이블 생성 SQL
    create_tables_sql = """
    DROP TABLE IF EXISTS schools, subways, neighborhood_score;
    
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
      school_count INTEGER,
      subway_count INTEGER,
      avg_price BIGINT,
      school_score FLOAT,
      subway_score FLOAT,
      price_score FLOAT
    );
    """
    cur.execute(create_tables_sql)
    print("테이블 생성 완료")
    
    # 3. CSV 데이터 DB에 삽입
    school_df = pd.read_csv('../datas/encoding_schools.csv', encoding='utf-8-sig')
    for index, row in school_df.iterrows():
      cur.execute(
        "INSERT INTO schools (name, latitude, longitude, geom) VALUES (%s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))",(row['학교명'],row['위도'], row['경도'], row['경도'], row['위도'])
      )
    
    subway_df = pd.read_csv('../datas/subway_combined.csv', encoding='utf-8-sig')
    for index, row in subway_df.iterrows():
      cur.execute(
        "INSERT INTO subways (name, latitude, longitude, geom) VALUES (%s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))",(row['역명'],row['위도'], row['경도'], row['경도'], row['위도'])
      )    
    
    scores_df = pd.read_csv('../datas/neighborhood_final_scores_v2.csv')
    for index, row in scores_df.iterrows():
        cur.execute(
            "INSERT INTO neighborhood_scores (dong, school_count, subway_count, avg_price, school_score, subway_score, price_score) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (row['dong'], row['school_count'], row['subway_count'], row['avg_price'], row['school_score'], row['subway_score'], row['price_score'])
        )
    print("CSV데이터 삽입 완료")    
    
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
    print(f"데이터베이스 연결 중 오류 발생: {e}")
  finally:
    if conn:
      conn.close()
      print("데이터베이스 연결 해제 ")
      
if __name__ == '__main__':
  migrate_csv_to_db()