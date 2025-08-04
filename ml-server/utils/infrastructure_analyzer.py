import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

class InfrastructureAnalyzer:
    def __init__(self):
        print("인프라 분석기 초기화 (DB 연결)...")
        load_dotenv()
        self.db_config = {
            "host": os.getenv("DB_HOST"), "port": os.getenv("DB_PORT"),
            "dbname": os.getenv("DB_NAME"), "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD")
        }

    def find_nearby(self, lat, lon, radius_km, infra_type):
        if lat is None or lon is None: return []
        
        table_map = {
            'school': 'schools',
            'subway': 'subways',
            'hospital': 'hospitals',
            'mart': 'marts',
            'park': 'parks'
        }
        table_name = table_map.get(infra_type)
        if not table_name: return []
        
        query = f"""
        SELECT name, latitude, longitude
        FROM {table_name}
        WHERE ST_DWithin(
            geom,
            ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
            %s
        );
        """
        
        results = []
        conn = None
        try:
            conn = psycopg2.connect(**self.db_config)
            """DictCursor를 사용하면 fetchall() 결과가 [{'name': ..., 'latitude': ..., 'longitude': ...}, ...]처럼 딕셔너리 형태로 나와서 코드가 더 가독성 있고 명확함 """
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(query, (lon, lat, radius_km * 1000))
                rows = cur.fetchall()
                for row in rows:
                    results.append(dict(row))
        except Exception as e:
            print(f"DB 쿼리 중 오류 발생 ({table_name}): {e}")
        finally:
            if conn: conn.close()
            
        return results