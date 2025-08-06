import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Union
import requests
import json

router = APIRouter()

# --- Pydantic 모델 정의 ---
class PropertyData(BaseModel):
    address: str
    deal_type: str
    price_deposit: int
    price_rent: int
    room_type: str
    area_m2: float
    floor: str
    build_date: str | None = None

class UserPreferences(BaseModel):
    preferences: List[str]
    region: str | None = None

class ReportRequest(BaseModel):
    property_data: PropertyData
    user_preferences: UserPreferences

def generate_llm_prompt(prop: PropertyData, prefs: UserPreferences) -> str:
    """Gemini AI에게 보낼 상세한 프롬프트를 생성하는 함수"""
    
    prompt = f"""
너는 한국 부동산 시장에 매우 능통한 전문 AI 컨설턴트야.
사용자가 선택한 매물과 사용자의 선호도를 바탕으로, 이 매물에 대한 객관적이고 유용한 'AI 분석 리포트'를 생성해줘.

**[사용자 선호도]**
- 중요하게 생각하는 가치: {', '.join(prefs.preferences) if prefs.preferences else '특별히 없음'}
- 희망 지역: {prefs.region if prefs.region else '전체'}

**[매물 정보]**
- 주소: {prop.address}
- 거래 유형: {prop.deal_type}
- 가격: {f"보증금 {prop.price_deposit}만원 / 월세 {prop.price_rent}만원" if prop.deal_type == '월세' else f"전세 {prop.price_deposit}만원"}
- 방 종류: {prop.room_type}
- 면적: {prop.area_m2:.2f} ㎡
- 건축년도: {prop.build_date}

**[생성할 리포트 내용]**
1.  **score**: 이 매물이 사용자의 선호도와 얼마나 일치하는지 0점에서 100점 사이의 점수로 평가해줘.
2.  **summary**: 전체적인 평가를 1~2문장의 자연스러운 한국어 문장으로 요약해줘.
3.  **pros**: 이 매물의 명확한 장점(추천하는 이유)을 2~3가지 항목으로箇条書き(箇条書き)로 작성해줘.
4.  **cons**: 사용자가 계약 전에 반드시 고려해야 할 단점이나 확인해야 할 사항을 2~3가지 항목으로 箇条書き(箇条書き)로 작성해줘.

**[출력 형식]**
반드시 아래와 같은 JSON 형식으로만 응답해줘. 다른 설명은 절대 추가하지 마.
{{
  "score": <점수 (int)>,
  "summary": "<요약 (string)>",
  "pros": ["<장점 1 (string)>", "<장점 2 (string)>"],
  "cons": ["<단점 1 (string)>", "<단점 2 (string)>"]
}}
"""
    return prompt

@router.post("/generate")
async def generate_report(request: ReportRequest):
    prompt = generate_llm_prompt(request.property_data, request.user_preferences)
    
    # Gemini API 호출
    api_key = os.getenv("GEMINI_KEY") # .env 파일에서 GEMINI_KEY를 읽어옵니다.
    if not api_key:
        raise HTTPException(status_code=500, detail="Gemini API 키가 설정되지 않았습니다.")
        
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={api_key}"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
        }
    }
    
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status() # HTTP 에러가 발생하면 예외를 일으킴
        
        # Gemini 응답에서 순수 JSON 텍스트만 추출
        result_text = response.json()['candidates'][0]['content']['parts'][0]['text']
        report_data = json.loads(result_text)
        
        return report_data
        
    except requests.exceptions.RequestException as e:
        print(f"Gemini API 통신 오류: {e}")
        raise HTTPException(status_code=503, detail="AI 서버와 통신하는 데 실패했습니다.")
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"Gemini API 응답 파싱 오류: {e}")
        raise HTTPException(status_code=500, detail="AI 리포트를 생성하는 데 실패했습니다.")
