import os
import psycopg2
from dotenv import load_dotenv
from math import radians, sin, cos, sqrt, atan2

class InfrastructureAnalyzer:
  def __init__(self):
    print('인프라 초기화 (DB 연결)...')
    load_dotenv()
    try:
      self.conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
      )
      print('데이터 베이스 연결 성공')
    except Exception as e:
      print(f"데이터 베이스 연결 실패:{e}")
      self.conn = None
      
  def find_nearby(self, lat, lng, radius_km, infra_type):
    """
    PostGIS를 사용해 지정된 반경 내의 인프라를 검색하고 거리순으로 정렬합니다.
    """
    if not self.conn or lat is None or lng is None: return []
    
    table_name= ''
    if infra_type == 'school': table_name = 'schools'
    elif infra_type == 'subway': table_name = 'subways'
    else: return []
    
    # ST_DWithin으로 반경 내 데이터 필터링, ST_DistanceSphere로 정확한 거리 계산
    query = f"""
    SELECT name, latitude, longitude
    FROM {table_name}
    WHERE ST_DWithin(
      geom,
      ST_SetSRID(ST_MakePoint(%s, %s), 4326),
      %s
    );
    """
    
    nearby_infra = []
    try:
      with self.conn.cursor() as cur:
        cur.execute(query, (lng, lat, radius_km * 1000))
        rows = cur.fetchall()
        for row in rows:
          nearby_infra.append({
            'name': row[0],
            'latitude': row[1],
            'longitude': row[2],
          })
    except Exception as e:
      print(f"DB 쿼리 중 오류 발생: {e}")
    return nearby_infra
  
  def __del__(self):
    if self.conn:
      self.conn.close()
      print('데이터 베이스 연결 종료')
