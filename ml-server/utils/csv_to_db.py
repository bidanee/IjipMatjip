import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv
import requests
import re
import time
from tqdm import tqdm

def parse_price(price_str):
  """ 월세와 전세 같은 문자열 파싱 함수 """
  if not isinstance(price_str,str): return 'None', 0, 0
  price_str = price_str.replace(',','').replace('만원','')
  deal_type, deposit, rent = None, 0, 0
  
  if '월세' in price_str:
    deal_type = '월세'
    parts = price_str.replace('월세','').strip().split('/')
    deposit_part = parts[0]
    rent_part = parts[1] if len(parts) > 1 else '0'
    
    deposit = 0
    if '억' in deposit_part:
      억_match = re.search(r'(\d+)억', deposit_part)
      if 억_match: deposit += int(억_match.group(1)) * 10000
    만_match = re.findall(r'(\d+)', deposit_part)
    if 만_match: deposit += int(만_match[-1])
    
    rent = int(rent_part) if rent_part.isdigit() else 0
    
  elif '전세' in price_str:
    deal_type = '전세'
    deposit_part = price_str.replace('전세','').strip()
    deposit = 0
    if '억' in deposit_part:
      억_match = re.search(r'(\d+)억', deposit_part)
      if 억_match: deposit += int(억_match.group(1)) * 10000
    만_match = re.findall(r'(\d+)', deposit_part)
    if 만_match: deposit += int(만_match[-1])
        
  return deal_type,deposit, rent

def parse_maintenance_fee(fee_str):
  """관리비 문자열 파싱 함수"""
  if not isinstance(fee_str, str) or '없음' in fee_str: return 0
  numbers = re.findall(r'\d+\.?\d*', fee_str)
  if not numbers: return 0
  fee = float(numbers[0])
  if '만' in fee_str: fee *= 10000
  return int(fee)

def get_coords(address, api_key):
  """ 카카오 API를 호출하여 주소를 좌표로 변환하는 함수"""
  url = "https://dapi.kakao.com/v2/local/search/address.json"
  headers = {"Authorization": f"KakaoAK {api_key}"}
  params = {"query": address}
  try:
    response = requests.get(url, headers=headers, params=params).json()
    if response.get('documents'):
      location = response['documents'][0]
      return float(location['y']), float(location['x'])
  except Exception as e:
    print(f"주소 변환 실패: {address}, 오류: {e}")
  return None, None

def migrate_csv_to_db():
  load_dotenv()
  conn = None
  try:
    conn = psycopg2.connect(
      host=os.getenv("DB_HOST"),
      port=os.getenv("DB_PORT"),
      dbname=os.getenv("DB_NAME"),
      user=os.getenv("DB_USER"),
      password=os.getenv("DB_PASSWORD"),
    )
    cur = conn.cursor()
    print("✅ DB 연결 성공")
    
    cur.execute("DROP TABLE IF EXISTS estates;")
    # 👇 room_bathrooms 오타 수정 및 build_date 타입 VARCHAR로 변경
    cur.execute("""
      CREATE TABLE estates (
        id SERIAL PRIMARY KEY, deal_type VARCHAR(50),
        price_deposit BIGINT, price_rent INT, maintenance_fee INT, 
        room_type VARCHAR(100), area_m2 FLOAT, floor VARCHAR(50), 
        address VARCHAR(255), build_date VARCHAR(50), rooms_bathrooms VARCHAR(100), 
        photo_url TEXT, latitude DOUBLE PRECISION, longitude DOUBLE PRECISION, 
        geom GEOGRAPHY(Point, 4326)
      );
    """)
    print("✅ 새로운 estates 테이블 생성 완료")
    
    df = pd.read_csv('../datas/real_estate_data.csv')
    df = df.where(pd.notnull(df), None)
    
    api_key = os.getenv("KAKAO_REST_API_KEY")
    
    for index, row in tqdm(df.iterrows(), total=len(df), desc="매물 데이터 처리중"):
      deal_type, deposit, rent = parse_price(row['거래유형/가격'])
      if not deal_type: continue
      
      maintenance_fee = parse_maintenance_fee(row['관리비'])
      area_m2_match = re.search(r'(\d+\.?\d*)㎡', str(row['면적']))
      area_m2 = float(area_m2_match.group(1)) if area_m2_match else None
      photo_url = str(row['방사진']).split(',')[0].strip() if row['방사진'] else None
      lat, lng = get_coords(row['상세주소'], api_key)
      
      if lat and lng:
        # 👇 INSERT 구문의 컬럼과 VALUES 개수를 14개로 일치시킴
        cur.execute(
          """
            INSERT INTO estates
            (deal_type, price_deposit, price_rent, maintenance_fee, room_type, area_m2, floor, address, build_date, rooms_bathrooms, photo_url, latitude, longitude, geom)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s),4326))
          """,
          (deal_type, deposit, rent, maintenance_fee, row['방 종류'], area_m2, row['층수'], row['상세주소'], row['준공년월'], row['방/욕실 수'], photo_url, lat, lng, lng, lat)
        )
      # 👇 API 호출 간격을 줄여 속도 향상
      time.sleep(0.05)
    
    conn.commit()
    print("🎉 새로운 데이터가 성공적으로 DB에 저장되었습니다.")
  except Exception as e:
    if conn: conn.rollback()
    print(f"오류 발생: {e}")
  finally:
    if conn: conn.close()
    print("데이터베이스 연결 해제")

if __name__ == '__main__':
  migrate_csv_to_db()