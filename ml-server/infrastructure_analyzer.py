import pandas as pd
from math import radians, sin, cos, sqrt, atan2

class InfrastructureAnalyzer:
    def __init__(self):
        print("인프라 데이터 로딩을 시작합니다...")
        try:
            # --- 학교 데이터 로드 ---
            school_df = pd.read_csv('./datas/encoding_schools.csv', encoding='utf-8-sig')
            # 정확한 컬럼 이름으로 데이터 선택
            self.school_df = school_df[['학교명', '위도', '경도']].copy()
            # 표준 컬럼 이름으로 변경
            self.school_df.columns = ['name', 'latitude', 'longitude']
            
            # --- 지하철역 데이터 로드 ---
            subway_df = pd.read_csv('./datas/subway_combined.csv', encoding='utf-8-sig')
            # 정확한 컬럼 이름으로 데이터 선택
            self.subway_df = subway_df[['역명', '위도', '경도']].copy()
            # 표준 컬럼 이름으로 변경
            self.subway_df.columns = ['name', 'latitude', 'longitude']

            print("학교, 지하철 데이터 로딩 및 처리 완료!")
            
        except FileNotFoundError as e:
            print(f"오류: 데이터 파일을 찾을 수 없습니다. {e}")
        except KeyError as e:
            print(f"오류: CSV 파일에서 필요한 컬럼을 찾을 수 없습니다. 컬럼명을 확인해주세요: {e}")
        except Exception as e:
            print(f"데이터 로딩 중 오류 발생: {e}")

    def haversine_distance(self, lat1, lon1, lat2, lon2):
        """ 두 지점의 위도, 경도를 받아 거리를 km 단위로 계산합니다. """
        R = 6371.0  # 지구 반지름 (km)

        lat1_rad, lon1_rad = radians(lat1), radians(lon1)
        lat2_rad, lon2_rad = radians(lat2), radians(lon2)

        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad

        a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return R * c

    def find_nearby(self, lat, lon, radius_km, infra_type):
        """ 지정된 반경 내의 인프라를 검색합니다. """
        if infra_type == 'school':
            # self.school_df가 존재하는지 확인
            if not hasattr(self, 'school_df'): return []
            df = self.school_df
        elif infra_type == 'subway':
            # self.subway_df가 존재하는지 확인
            if not hasattr(self, 'subway_df'): return []
            df = self.subway_df
        else:
            return []

        nearby_infra = []
        for index, row in df.iterrows():
            # 데이터에 결측치가 있을 경우를 대비한 예외 처리
            try:
                distance = self.haversine_distance(lat, lon, float(row['latitude']), float(row['longitude']))
                if distance <= radius_km:
                    nearby_infra.append({
                        'name': row['name'],
                        'distance_km': round(distance, 3),
                        'latitude': row['latitude'],
                        'longitude':row['longitude']
                    })
            except (ValueError, TypeError):
                # 위도/경도 값이 숫자가 아니거나 비어있는 경우 건너뜀
                continue
        
        return nearby_infra