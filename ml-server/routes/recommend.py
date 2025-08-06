import os
import psycopg2
import psycopg2.extras
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Union

router = APIRouter()

def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"), port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"), user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    return conn

# --- Pydantic 모델 정의 ---
class SizePyeong(BaseModel):
    min: int | None = None
    max: int | None = None

class JeonseBudget(BaseModel):
    min: int | None = None
    max: int | None = None

class WolseBudget(BaseModel):
    deposit_max: int | None = None
    rent_min: int | None = None
    rent_max: int | None = None

class RecommendationRequest(BaseModel):
    preferences: List[str]
    region: str | None = None
    deal_type: str
    budget: Union[JeonseBudget, WolseBudget]
    size_pyeong: SizePyeong | None = None
    room_type: str | None = None

@router.post("/neighborhood")
def recommend_neighborhood_and_estates(request: RecommendationRequest):
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            # 1. 라이프 스타일 조건에 따라 동적으로 점수 계산
            lifestyle_to_score_map = {
                '학군 중요': 'school_score',
                '교통 편리': 'subway_score',
                '생활편의시설': '(mart_score + hospital_score)',
                '조용한 곳': '(park_score - subway_score)',
                '번화가': '(subway_score + mart_score)'
            }
            
            score_clauses = [lifestyle_to_score_map[pref] for pref in request.preferences if pref in lifestyle_to_score_map]

            if not score_clauses:
                # 사용자가 선호도를 선택하지 않았을 경우, 모든 점수를 균등하게 고려
                total_score_sql = "(school_score + subway_score + mart_score + hospital_score + park_score) / 5"
            else:
                total_score_sql = " + ".join(score_clauses)

            # 2. 최적의 동네 추천
            where_clauses_dong = ["latitude IS NOT NULL"]
            params_dong = []

            if request.region:
                where_clauses_dong.append("sigungu_name = %s")
                params_dong.append(request.region)
            
            where_sql_dong = "WHERE " + " AND ".join(where_clauses_dong)
            
            # 동네 추천 쿼리
            dong_query = f"SELECT *, ({total_score_sql}) AS total_score FROM neighborhood_scores {where_sql_dong} ORDER BY total_score DESC LIMIT 5;"
            
            cur.execute(dong_query, tuple(params_dong))
            recommended_dongs = [dict(row) for row in cur.fetchall()]

            # 3. 추천된 동네 내에서 매물 검색
            estates = []
            recommended_dong_names = [d['dong'] for d in recommended_dongs]

            if recommended_dong_names:
                dong_conditions = " OR ".join([f"address LIKE %s" for _ in recommended_dong_names])
                dong_params = [f"%{name}%" for name in recommended_dong_names]

                where_clauses_prop = [f"({dong_conditions})"]
                params_prop = dong_params

                if request.deal_type:
                    where_clauses_prop.append("deal_type = %s")
                    params_prop.append(request.deal_type)

                if request.room_type:
                    where_clauses_prop.append("room_type LIKE %s")
                    params_prop.append(f"%{request.room_type}%")

                if request.deal_type == '전세' and isinstance(request.budget, JeonseBudget):
                    if request.budget.min is not None:
                        where_clauses_prop.append("price_deposit >= %s")
                        params_prop.append(request.budget.min)
                    if request.budget.max is not None:
                        where_clauses_prop.append("price_deposit <= %s")
                        params_prop.append(request.budget.max)
                elif request.deal_type == '월세' and isinstance(request.budget, WolseBudget):
                    if request.budget.deposit_max is not None:
                        where_clauses_prop.append("price_deposit <= %s")
                        params_prop.append(request.budget.deposit_max)
                    if request.budget.rent_min is not None:
                        where_clauses_prop.append("price_rent >= %s")
                        params_prop.append(request.budget.rent_min)
                    if request.budget.rent_max is not None:
                        where_clauses_prop.append("price_rent <= %s")
                        params_prop.append(request.budget.rent_max)

                if request.size_pyeong and request.size_pyeong.min is not None:
                    where_clauses_prop.append("area_m2 >= %s")
                    params_prop.append(request.size_pyeong.min * 3.305785)
                if request.size_pyeong and request.size_pyeong.max is not None:
                    where_clauses_prop.append("area_m2 <= %s")
                    params_prop.append(request.size_pyeong.max * 3.305785)

                where_sql_prop = "WHERE " + " AND ".join(where_clauses_prop)
                prop_query = f"SELECT * FROM estates {where_sql_prop} LIMIT 20;"

                cur.execute(prop_query, tuple(params_prop))
                estates = [dict(row) for row in cur.fetchall()]

            return {"neighborhoods": recommended_dongs, "estates": estates}

    except Exception as e:
        print(f"추천 API 처리 중 오류 발생 : {e}")
        raise HTTPException(status_code=500, detail="추천 정보를 가져오는 데 실패했습니다.")
    finally:
        if conn:
            conn.close()