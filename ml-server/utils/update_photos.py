import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv
from tqdm import tqdm

def update_photo_url():
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

        df = pd.read_csv('../datas/real_estate_lists_cleaned.csv')
        df.dropna(subset=['상세주소', '방사진'], inplace=True)

        update_count = 0
        for index, row in tqdm(df.iterrows(), total=len(df), desc="사진 URL 업데이트 중"):
            # 쉼표로 구분된 URL 문자열을 URL 리스트(배열)로 변환
            photo_url = [url.strip() for url in str(row['방사진']).split(',')]
            address = row['상세주소']

            # 주소(address)를 기준으로 photo_url 컬럼을 업데이트
            cur.execute(
                "UPDATE estates SET photo_url = %s WHERE address = %s",
                (photo_url, address)
            )
            update_count += cur.rowcount

        conn.commit()
        print(f"🎉 총 {update_count}개의 매물에 사진 URL을 성공적으로 업데이트했습니다.")

    except Exception as e:
        if conn: conn.rollback()
        print(f"오류 발생: {e}")
    finally:
        if conn: conn.close()
        print("데이터베이스 연결 해제")

if __name__ == '__main__':
    update_photo_url()