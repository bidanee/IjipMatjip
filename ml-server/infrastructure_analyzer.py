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

# import os
# import psycopg2
# import pandas as pd
# from dotenv import load_dotenv
# from math import radians, sin, cos, sqrt, atan2

# class InfrastructureAnalyzer:
#     def __init__(self):
#         print("인프라 분석기 초기화 (DB 연결)...")
#         load_dotenv()
#         self.db_config = {
#             "host": os.getenv("DB_HOST"), "port": os.getenv("DB_PORT"),
#             "dbname": os.getenv("DB_NAME"), "user": os.getenv("DB_USER"),
#             "password": os.getenv("DB_PASSWORD")
#         }
#         self.school_df = self._load_data_from_db('schools')
#         self.subway_df = self._load_data_from_db('subways')
#         print("✅ 인프라 데이터 로딩 완료")

#     def _load_data_from_db(self, table_name):
#         """DB에서 전체 데이터를 불러와 pandas DataFrame으로 저장"""
#         conn = None
#         try:
#             conn = psycopg2.connect(**self.db_config)
#             query = f"SELECT name, latitude, longitude FROM {table_name};"
#             df = pd.read_sql_query(query, conn)
#             return df
#         except Exception as e:
#             print(f"{table_name} 데이터 로딩 중 오류 발생: {e}")
#             return pd.DataFrame() # 오류 발생 시 빈 데이터프레임 반환
#         finally:
#             if conn: conn.close()
    
#     def haversine_distance(self, lat1, lon1, lat2, lon2):
#         """두 지점의 위도, 경도를 받아 거리를 km 단위로 계산"""
#         R = 6371.0
#         lat1_rad, lon1_rad = radians(lat1), radians(lon1)
#         lat2_rad, lon2_rad = radians(lat2), radians(lon2)
#         dlon = lon2_rad - lon1_rad
#         dlat = lat2_rad - lat1_rad
#         a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
#         c = 2 * atan2(sqrt(a), sqrt(1 - a))
#         return R * c

#     def find_nearby(self, lat, lon, radius_km, infra_type):
#         """
#         Pandas를 사용해 지정된 반경 내의 인프라를 검색합니다.
#         """
#         if lat is None or lon is None: return []
        
#         df = None
#         if infra_type == 'school': df = self.school_df
#         elif infra_type == 'subway': df = self.subway_df
#         else: return []

#         if df.empty: return []

#         nearby_infra = []
#         for index, row in df.iterrows():
#             distance = self.haversine_distance(lat, lon, row['latitude'], row['longitude'])
#             if distance <= radius_km:
#                 nearby_infra.append({
#                     'name': row['name'],
#                     'latitude': row['latitude'],
#                     'longitude': row['longitude'],
#                     'distance_km': round(distance, 3)
#                 })
        
#         # 거리순으로 정렬
#         nearby_infra.sort(key=lambda x: x['distance_km'])
#         return nearby_infra